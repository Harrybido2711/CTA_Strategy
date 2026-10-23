"""Mean-variance optimizer with vector inputs (homework D, chapter 05 2.3).

    max_w  mu' w - gamma w' Sigma w - tau' |w - w_prev|
    s.t.   sum |w| <= gross,  |w_i| <= cap_i,  sum w = net

mu, cap and tau are vectors, Sigma a matrix, w_prev the previous target: nothing the optimizer
takes is a single number except gamma, gross and net. Sigma is the sample covariance of the
model's residuals (homework D); a Ledoit-Wolf shrinkage of the same residuals is the variant.
The problem is compiled once with cvxpy parameters and re-solved per date.
"""
import cvxpy as cp
import numpy as np
import pandas as pd


class MeanVariance:
    def __init__(self, n, gross=2.0, net=0.0):
        self.n = n
        self.w = cp.Variable(n)
        a, t = cp.Variable(n), cp.Variable(n)
        self.mu = cp.Parameter(n)
        self.L = cp.Parameter((n, n))            # sqrt(gamma) x chol(Sigma)', so w' gamma Sigma w = ||L w||^2
        self.w_prev = cp.Parameter(n)
        self.cap = cp.Parameter(n, nonneg=True)
        self.tau = cp.Parameter(n, nonneg=True)
        obj = cp.Maximize(self.mu @ self.w - cp.sum_squares(self.L @ self.w) - self.tau @ t)
        cons = [self.w <= a, -self.w <= a, cp.sum(a) <= gross,
                self.w <= self.cap, -self.w <= self.cap,
                self.w - self.w_prev <= t, self.w_prev - self.w <= t,
                cp.sum(self.w) == net]
        self.prob = cp.Problem(obj, cons)

    def solve(self, mu, sigma_chol_t, w_prev, gamma, cap_vec, tau_vec):
        self.mu.value = np.asarray(mu, float)
        self.L.value = np.sqrt(gamma) * np.asarray(sigma_chol_t, float)
        self.w_prev.value = np.asarray(w_prev, float)
        self.cap.value = np.asarray(cap_vec, float)
        self.tau.value = np.asarray(tau_vec, float)
        self.prob.solve(solver=cp.CLARABEL)
        if self.w.value is None:
            raise RuntimeError(f"optimizer failed: {self.prob.status}")
        return np.asarray(self.w.value).ravel()


def chol_t(sigma, jitter=1e-10):
    """Upper factor U with Sigma = U' U, after clipping negative eigenvalues to make Sigma PSD."""
    s = np.asarray(sigma, float)
    s = (s + s.T) / 2
    vals, vecs = np.linalg.eigh(s)
    s = (vecs * np.clip(vals, 0, None)) @ vecs.T + jitter * np.eye(len(s))
    return np.linalg.cholesky(s).T


def residual_covariance(resid, assets, method="sample"):
    """Covariance across assets of the residuals (date x asset), on a fixed asset order."""
    R = resid.unstack("asset").reindex(columns=assets)
    if method == "sample":
        return R.cov().fillna(0.0).to_numpy()
    if method == "ledoit_wolf":
        from sklearn.covariance import LedoitWolf
        X = R.fillna(0.0).to_numpy()
        return LedoitWolf().fit(X).covariance_
    raise ValueError(method)


def model_inputs(wd, panel, model):
    """mu (date x asset) from the model's test-quarter predictions, and chol(Sigma) per rung and method."""
    import rr_models as MD
    assets = list(wd.close.columns)
    mu = pd.DataFrame(np.nan, index=wd.cal, columns=assets)
    chol = {}
    for r in wd.rungs:
        _, p, resid = MD.fit_rung(model, panel, wd.cal, r)
        mu.update(p.unstack("asset").reindex(columns=assets))
        for method in ("sample", "ledoit_wolf"):
            chol[(r["test_q"], method)] = chol_t(residual_covariance(resid, assets, method))
    return mu, chol


def optimized_weights(wd, mu, chol, gamma, cap, tau_per_dollar, net, method, dates, gross=2.0):
    """Solve the optimizer date by date over `dates`, carrying the previous target as w_prev."""
    assets = list(wd.close.columns)
    quarter = pd.Series([str(q) for q in wd.cal.to_period("Q")], index=wd.cal)
    opt = MeanVariance(len(assets), gross=gross, net=net)
    out = pd.DataFrame(0.0, index=wd.cal, columns=assets)
    w_prev = np.zeros(len(assets))
    for d in dates:
        m = mu.loc[d].to_numpy()
        ok = np.isfinite(m)
        w = opt.solve(np.where(ok, m, 0.0), chol[(quarter[d], method)], w_prev, gamma,
                      np.where(ok, cap, 0.0), np.full(len(assets), tau_per_dollar))
        w = np.where(np.abs(w) < 1e-9, 0.0, w)
        out.loc[d] = w
        w_prev = w
    return out
