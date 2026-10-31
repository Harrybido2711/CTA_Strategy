"""Round 3 (ROUND3.md): regime measures under the dynamic cut D, and the learning-path pipeline.

Part A pieces live here: the D percentile and tercile, the per-asset and market measures of A1,
the exact holding-month return of a month-end position, and A8's turnover decomposition.
Everything a label at date t uses is known at the close of t (indices, correlation) or of t - 1
(per-asset volume and volatility, as rr_regimes defines them).
"""
import numpy as np
import pandas as pd

import config as C
import rr_data as D
import rr_regimes as R
import rr_tsmom as T

P3 = C.ROUND3
P2 = C.ROUND2
LABELS = R.LABELS
BONDS = [t for t, c in C.UNIVERSE_CATEGORY.items() if c == "bonds"]


# ----------------------------------------------------------------------------- the cut
def d_pct(x, n=P3["rank_window"], minp=P3["rank_min_periods"]):
    """D: percentile of today's value among the trailing n days, today included."""
    return x.rolling(n, min_periods=minp).rank(pct=True)


def d_tercile(pct):
    """0 / 1 / 2 = low / mid / high at the 1/3 and 2/3 percentiles; NaN where pct is NaN."""
    lab = np.where(pct <= 1 / 3, 0, np.where(pct <= 2 / 3, 1, 2))
    if isinstance(pct, pd.DataFrame):
        return pd.DataFrame(lab, index=pct.index, columns=pct.columns).where(pct.notna())
    return pd.Series(lab, index=pct.index).where(pct.notna())


# ----------------------------------------------------------------------------- A1 measures
def avg_pairwise_corr(xr, n=P3["corr_window"]):
    """Mean off-diagonal correlation of daily excess returns over the trailing n days, through t."""
    a = xr.to_numpy()
    out = np.full(len(a), np.nan)
    for i in range(n - 1, len(a)):
        blk = a[i - n + 1:i + 1]
        keep = np.isfinite(blk).sum(axis=0) >= n - 5
        if keep.sum() < 10:
            continue
        c = pd.DataFrame(blk[:, keep]).corr().to_numpy()
        k = c.shape[0]
        out[i] = (np.nansum(c) - k) / (k * (k - 1))
    return pd.Series(out, index=xr.index, name="avg_corr")


def ewma_sigma(xr, com):
    """Annualised EWMA volatility through t - 1 (the paper's estimator at another centre of mass)."""
    return T.ewma_vol(xr, com=com)


def measures(wd, xr):
    """A1, as daily frames: per-asset percentiles and terciles, and the market-wide series."""
    vol = D.panel(wd.etfs, "volume", wd.cal)
    v_pct = d_pct(R.volume_measure(vol, P3["measure_window"]))
    s_pct = d_pct(R.sigma_measure(wd.close, P3["measure_window"]))
    vix, _ = D.load_index("VIX", wd.cal)
    move, _ = D.load_index("MOVE", wd.cal)
    vix_pct, move_pct = d_pct(vix), d_pct(move)
    idx_pct = pd.DataFrame({t: (move_pct if t in BONDS else vix_pct) for t in wd.close.columns})
    mkt_vol_pct = d_pct(v_pct.mean(axis=1))
    corr = avg_pairwise_corr(xr)
    corr_pct = d_pct(corr)
    fast, slow = ewma_sigma(xr, P3["sigma_fast_com"]), ewma_sigma(xr, P3["sigma_slow_com"])
    return {
        "V_pct": v_pct, "sigma_pct": s_pct, "index_pct": idx_pct,
        "V_lab": d_tercile(v_pct), "sigma_lab": d_tercile(s_pct), "index_lab": d_tercile(idx_pct),
        "VIX": vix, "MOVE": move, "VIX_pct": vix_pct, "MOVE_pct": move_pct,
        "VIX_lab": d_tercile(vix_pct), "MOVE_lab": d_tercile(move_pct),
        "mkt_volume_pct": mkt_vol_pct, "mkt_volume_lab": d_tercile(mkt_vol_pct),
        "corr": corr, "corr_pct": corr_pct, "corr_lab": d_tercile(corr_pct),
        "sigma_fast": fast, "sigma_slow": slow,
    }


def trend_z(xr, sig_vol, k_months, md=P2["month_days"]):
    """k-month cumulative excess log return over sigma x sqrt(k / 12), through t (sigma through t - 1)."""
    n = k_months * md
    cum = np.log1p(xr).rolling(n, min_periods=n).sum()
    return cum / (sig_vol * np.sqrt(k_months / 12.0))


# ----------------------------------------------------------------------------- holding months
def holding_rows(cal, me, lag=C.LAG):
    """For each month-end F, the calendar rows whose daily return the position formed at F earns.

    The fill is at close F + lag; the position is held until the fill after the next month-end.
    Daily return at row j is close_j / close_{j-1} - 1, so the rows are pos(F)+lag+1 .. pos(F')+lag.
    The last month-end has no F' and gets no rows.
    """
    pos = cal.get_indexer(me)
    out = {}
    for i, f in enumerate(me[:-1]):
        a, b = pos[i] + lag + 1, pos[i + 1] + lag
        if b < len(cal):
            out[f] = np.arange(a, b + 1)
    return out


def holding_return(xr, cal, me, lag=C.LAG):
    """Compounded daily excess return of every asset over each month-end's holding month."""
    rows = holding_rows(cal, me, lag)
    a = xr.to_numpy()
    out = pd.DataFrame(np.nan, index=me, columns=xr.columns)
    for f, r in rows.items():
        blk = a[r]
        g = np.prod(1.0 + np.nan_to_num(blk), axis=0) - 1.0
        g[np.isnan(blk).all(axis=0)] = np.nan
        out.loc[f] = g
    return out


def book_holding_return(x_daily, cal, me, lag=C.LAG):
    """Sum of a book's daily excess PnL over each month-end's holding month ($1 of capital, additive)."""
    rows = holding_rows(cal, me, lag)
    v = x_daily.reindex(cal).to_numpy()
    return pd.Series({f: float(np.nansum(v[r])) for f, r in rows.items()})


# ----------------------------------------------------------------------------- A8 turnover sources
def turnover_sources_t0(sign, a, w0):
    """Split T0's month-end weight changes into flips, entries/exits, sizing, 1/S and the caps.

    w0 = caps(sign x a / S). The path from one month-end to the next changes, in order, the sign,
    the size a = 40%/sigma, the count S, then the caps; the parts sum exactly to w0_t - w0_{t-1}.
    Returns one row per month-end with the L1 norm of each part and of the actual change.
    """
    valid = sign.notna() & a.notna()                           # T0's S counts exactly these
    s = sign.where(valid).fillna(0.0)
    aa = a.where(valid).fillna(0.0)
    n = valid.sum(axis=1).astype(float).replace(0, np.nan).ffill().bfill()
    rows = []
    for i in range(1, len(w0)):
        s0, s1 = s.iloc[i - 1], s.iloc[i]
        a0, a1 = aa.iloc[i - 1], aa.iloc[i]
        n0, n1 = n.iloc[i - 1], n.iloc[i]
        flip = (s0 != 0) & (s1 != 0) & (s0 != s1)
        entry = (s0 == 0) != (s1 == 0)
        a_ref = a0.where(s0 != 0, a1)                           # an entry is sized at its new size
        d_sign = (s1 - s0) * a_ref / n0
        d_size = s1 * (a1 - a_ref) / n0
        d_count = s1 * a1 / n1 - s1 * a1 / n0
        uc0, uc1 = s0 * a0 / n0, s1 * a1 / n1
        d_cap = (w0.iloc[i] - uc1) - (w0.iloc[i - 1] - uc0)
        actual = w0.iloc[i] - w0.iloc[i - 1]
        rows.append({"date": w0.index[i],
                     "sign_flip": float(d_sign[flip].abs().sum()), "entry_exit": float(d_sign[entry].abs().sum()),
                     "sizing": float(d_size.abs().sum()), "count_1_over_S": float(d_count.abs().sum()),
                     "caps": float(d_cap.abs().sum()), "actual": float(actual.abs().sum()),
                     "check": float((d_sign + d_size + d_count + d_cap - actual).abs().max())})
    return pd.DataFrame(rows).set_index("date")


def turnover_sources_t1(w0, lev, w1):
    """T1 = caps(L x T0). Split its change into T0's own change at the old leverage, the leverage
    change, and T1's caps; the parts sum exactly to w1_t - w1_{t-1}."""
    rows = []
    for i in range(1, len(w1)):
        l0, l1 = lev.iloc[i - 1], lev.iloc[i]
        d_book = l0 * (w0.iloc[i] - w0.iloc[i - 1])
        d_lev = (l1 - l0) * w0.iloc[i]
        d_cap = (w1.iloc[i] - l1 * w0.iloc[i]) - (w1.iloc[i - 1] - l0 * w0.iloc[i - 1])
        actual = w1.iloc[i] - w1.iloc[i - 1]
        rows.append({"date": w1.index[i], "T0_change_at_old_leverage": float(d_book.abs().sum()),
                     "leverage": float(d_lev.abs().sum()), "caps": float(d_cap.abs().sum()),
                     "actual": float(actual.abs().sum()),
                     "check": float((d_book + d_lev + d_cap - actual).abs().max())})
    return pd.DataFrame(rows).set_index("date")


# ----------------------------------------------------------------------------- inference
def month_mean_se(panel_y, mask=None, nw_lag=1):
    """Equal-weight each month: cross-sectional mean per month, then mean and NW SE across months."""
    import rr_metrics as M
    y = panel_y if mask is None else panel_y.where(mask)
    d = y.mean(axis=1).dropna()
    se = M.newey_west_se(d, nw_lag) if len(d) > 2 else np.nan
    return d, (float(d.mean()) if len(d) else np.nan), se


def block_bootstrap_ci(d, blocks=(1, 3, 6), n_draws=4000, level=0.90):
    """Stationary-bootstrap CI of a monthly series' mean at several mean block lengths; the widest."""
    import rr_metrics as M
    x = np.asarray(d, dtype=float)
    out = {}
    for bl in blocks:
        idx = M.stationary_bootstrap_indices(len(x), bl, n_draws, seed=bl)
        m = x[idx].mean(axis=1)
        out[bl] = (float(np.quantile(m, (1 - level) / 2)), float(np.quantile(m, 1 - (1 - level) / 2)))
    lo = min(v[0] for v in out.values()); hi = max(v[1] for v in out.values())
    return lo, hi, out


# ============================================================================= Part B: the learning path
FEATURES_OFF = [f"z{k}" for k in P3["mom_months"]] + ["macd"]
REGIME = ["sigma_rank", "V_rank", "index_rank", "corr_rank"]
FEATURES_ON = FEATURES_OFF + REGIME + [f"z12_x_{r}" for r in REGIME]


def feature_frames(close, xr, sig_vol, ms, me):
    """B1 at month-ends F: name -> (F x asset) frame, every value known by the close of F."""
    import rr_signals as S
    f = {f"z{k}": trend_z(xr, sig_vol, k).loc[me] for k in P3["mom_months"]}
    nf, ns = P3["macd_pair"]
    f["macd"] = S.macd_line(close, nf, ns).loc[me] / sig_vol.loc[me]
    f["sigma_rank"] = ms["sigma_pct"].loc[me] - 0.5
    f["V_rank"] = ms["V_pct"].loc[me] - 0.5
    f["index_rank"] = ms["index_pct"].loc[me] - 0.5
    cr = ms["corr_pct"].loc[me] - 0.5
    f["corr_rank"] = pd.DataFrame({t: cr for t in close.columns})
    for r in REGIME:
        f[f"z12_x_{r}"] = f["z12"] * f[r]
    return f


def label_return(xr, cal, me, d):
    """Amendment 1: excess return from the fill F + d to the next month-end close F' (known at F')."""
    pos = cal.get_indexer(me)
    a = xr.to_numpy()
    out = pd.DataFrame(np.nan, index=me, columns=xr.columns)
    for i in range(len(me) - 1):
        lo, hi = pos[i] + d + 1, pos[i + 1]
        if hi < lo:
            continue
        blk = a[lo:hi + 1]
        g = np.prod(1.0 + np.nan_to_num(blk), axis=0) - 1.0
        g[np.isnan(blk).all(axis=0)] = np.nan
        out.iloc[i] = g
    return out


def long_panel(feats, label, sig_vol_me):
    """One row per (F, asset): features, the target y = label / monthly sigma, the monthly sigma,
    and the quarter of the holding month (the month after F), which is the row's segment."""
    sm = sig_vol_me / np.sqrt(12.0)
    df = pd.DataFrame({k: v.stack(dropna=False) for k, v in feats.items()})
    df["y"] = (label / sm).stack(dropna=False)
    df["sig_m"] = sm.stack(dropna=False)
    F = df.index.get_level_values(0)
    df["seg"] = (F.to_period("M") + 1).asfreq("Q")
    return df


def monthly_rungs(first=P3["first_apply_q"], last=P3["last_apply_q"]):
    """Chapter 07's ladder on holding-month quarters: train q-4..q-2, validate q-1, apply q."""
    return [{"q": q, "train": [q - 4, q - 3, q - 2], "val": [q - 1]} for q in pd.period_range(first, last, freq="Q")]


class Standardizer:
    """Chapter 07: z-score with the fitting rows' mean and sd, then clip at +-clip_sd."""

    def __init__(self, X):
        self.m, self.s = X.mean(), X.std(ddof=0).replace(0, 1.0)

    def __call__(self, X):
        return ((X - self.m) / self.s).clip(-P3["clip_sd"], P3["clip_sd"])


def model_grid(name):
    """(label, factory) for each inner-grid point of one model class (B2)."""
    from catboost import CatBoostRegressor
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.linear_model import Lasso, Ridge
    if name == "EW":
        return [("EW", None)]
    if name == "Ridge":
        return [(f"Ridge a={a}", lambda a=a: Ridge(alpha=a)) for a in P3["ridge_alpha"]]
    if name == "Lasso":
        return [(f"Lasso f={f}", ("lasso", f)) for f in P3["lasso_alpha_frac"]]
    if name == "CatBoost":
        c = P3["catboost"]
        return [(f"CatBoost depth={dp}", lambda dp=dp: CatBoostRegressor(depth=dp, iterations=c["iterations"],
                 learning_rate=c["learning_rate"], verbose=0, random_seed=0, allow_writing_files=False, thread_count=1))
                for dp in c["depth"]]
    if name == "HGB":
        h = P3["hgb"]
        return [(f"HGB depth={dp}", lambda dp=dp: HistGradientBoostingRegressor(max_depth=dp, max_iter=h["max_iter"],
                 learning_rate=h["learning_rate"], min_samples_leaf=h["min_samples_leaf"], random_state=0))
                for dp in h["max_depth"]]
    raise ValueError(name)


class Fit:
    """One fitted grid point: standardizer + model; predict returns y-hat for any rows."""

    def __init__(self, label, factory, rows, cols):
        from sklearn.linear_model import Lasso
        self.label, self.cols = label, cols
        X = rows[cols]
        self.std = Standardizer(X)
        Z, y = self.std(X).to_numpy(), rows["y"].to_numpy()
        if factory is None:                                    # EW: the mean of the trend features, one slope
            s = Z[:, [cols.index(c) for c in FEATURES_OFF]].mean(axis=1)
            b = np.polyfit(s, y, 1)
            self.model = ("EW", b)
        elif isinstance(factory, tuple):                       # Lasso: alpha as a fraction of alpha_max
            amax = np.abs(Z.T @ (y - y.mean())).max() / len(y)
            self.model = Lasso(alpha=factory[1] * amax, max_iter=20000).fit(Z, y)
        else:
            self.model = factory().fit(Z, y)

    def predict(self, rows):
        Z = self.std(rows[self.cols]).to_numpy()
        if isinstance(self.model, tuple):
            b = self.model[1]
            return np.polyval(b, Z[:, [self.cols.index(c) for c in FEATURES_OFF]].mean(axis=1))
        return self.model.predict(Z)


def fit_and_choose(model, cols, train, val):
    """Inner layer, step 1-2: fit each grid point on train, keep the one with the lowest validation MSE."""
    best = None
    for label, fac in model_grid(model):
        f = Fit(label, fac, train, cols)
        mse = float(np.mean((f.predict(val) - val["y"].to_numpy()) ** 2))
        if best is None or mse < best[1]:
            best = (label, mse, fac)
    return best


# ----------------------------------------------------------------------------- B3: the optimizer
class CostAwareBook:
    """max mu'w - k'|w - w_held|  s.t. ||L w|| <= budget, |w| <= cap, sum|w| <= gross, sum w <= net_max.

    k = phi x kappa + gamma per asset (Amendment 1); L' L = Sigma-hat (monthly); budget = sigma_0 / sqrt(12).
    Compiled once with cvxpy parameters, re-solved per month-end.
    """

    def __init__(self, n):
        import cvxpy as cp
        self.cp = cp
        self.w = cp.Variable(n)
        t = cp.Variable(n)
        self.mu, self.L = cp.Parameter(n), cp.Parameter((n, n))
        self.wh, self.k = cp.Parameter(n), cp.Parameter(n, nonneg=True)
        self.cap, self.budget = cp.Parameter(n, nonneg=True), cp.Parameter(nonneg=True)
        cons = [t >= self.w - self.wh, t >= self.wh - self.w, cp.norm(self.L @ self.w, 2) <= self.budget,
                self.w <= self.cap, -self.w <= self.cap, cp.norm1(self.w) <= P3["gross_cap"],
                cp.sum(self.w) <= P3["net_max"]]
        self.prob = cp.Problem(cp.Maximize(self.mu @ self.w - self.k @ t), cons)

    def solve(self, mu, L, w_held, k, cap, budget):
        self.mu.value, self.L.value, self.wh.value = mu, L, w_held
        self.k.value, self.cap.value, self.budget.value = k, cap, budget
        for solver in ("CLARABEL", "ECOS", "SCS"):
            try:
                self.prob.solve(solver=solver)
                if self.w.value is not None and self.prob.status in ("optimal", "optimal_inaccurate"):
                    return np.clip(self.w.value, -cap, cap)
            except Exception:                                   # noqa: BLE001 - try the next solver
                continue
        return np.clip(w_held, -cap, cap)                       # no solution: hold, within the caps


def ewma_cov(xr, com=P3["cov_com_days"]):
    return xr.ewm(com=com, adjust=False).cov(bias=True)


def risk_inputs(cov, xr, F, assets, horizon=P3["cov_horizon_days"]):
    """Monthly Sigma-hat known by the close before F, its upper Cholesky factor, and assets with a usable variance."""
    rows = xr.index
    i = rows.get_loc(F)
    S = cov.loc[rows[i - 1]].reindex(index=assets, columns=assets).to_numpy() * horizon
    ok = np.isfinite(np.diag(S)) & (np.diag(S) > 0)
    S = np.where(np.isfinite(S), S, 0.0)
    S[~ok, :] = 0.0; S[:, ~ok] = 0.0
    S[np.diag_indices_from(S)] = np.where(ok, np.diag(S), 1.0)
    w, V = np.linalg.eigh((S + S.T) / 2)
    L = (V * np.sqrt(np.clip(w, 1e-12, None))).T                 # L'L = S
    return L, ok


def drifted(w_target, close, pos_fill, pos_now):
    """Weights of a book filled at row pos_fill (constant shares) marked at row pos_now."""
    c = close.ffill().to_numpy()
    with np.errstate(invalid="ignore", divide="ignore"):
        r = c[pos_now] / c[pos_fill]
    return np.nan_to_num(w_target * np.where(np.isfinite(r), r, 1.0))


# ----------------------------------------------------------------------------- B4: the walk-forward
def choose(series, labels=None):
    """Chapter 09's rule: drop candidates whose max drawdown is deeper than the median; take the highest
    cumulative excess; if the runner-up's mean daily return is within one SE of the leader's, the higher
    Sharpe. series: dict label -> daily excess return Series. Returns (label, table)."""
    import rr_metrics as M
    rows = []
    for k, x in series.items():
        x = x.dropna()
        rows.append({"cand": k, "cum": float(x.sum()), "max_dd": M.max_drawdown(x)[0], "mean": float(x.mean()),
                     "se": float(x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 1 else np.nan,
                     "sharpe": float(x.mean() / x.std(ddof=1) * np.sqrt(252)) if x.std(ddof=1) > 0 else np.nan})
    tab = pd.DataFrame(rows).set_index("cand")
    keep = tab[tab["max_dd"] >= tab["max_dd"].median()].sort_values("cum", ascending=False)
    pick = keep.index[0]
    if len(keep) > 1:
        a, b = keep.iloc[0], keep.iloc[1]
        if a["mean"] - b["mean"] < a["se"] and np.nan_to_num(b["sharpe"], nan=-9) > np.nan_to_num(a["sharpe"], nan=-9):
            pick = keep.index[1]
    tab["kept"] = tab.index.isin(keep.index)
    tab["chosen"] = tab.index == pick
    return pick, tab


class Context:
    """Everything the procedures share: prices, returns, risk, the long panel at one delay d."""

    def __init__(self, wd, xr, sig_vol, ms, me, d=P3["delay_days"]):
        self.wd, self.cal, self.close, self.open, self.rf = wd, wd.cal, wd.close, wd.open, wd.rf
        self.xr, self.me, self.d, self.assets = xr, me, d, list(wd.close.columns)
        self.cov = ewma_cov(xr)
        feats = feature_frames(wd.close, xr, sig_vol, ms, me)
        self.panel = long_panel(feats, label_return(xr, self.cal, me, d), sig_vol.loc[me])
        self.pos = pd.Series(self.cal.get_indexer(me), index=me)
        self.risk = {F: risk_inputs(self.cov, xr, F, self.assets) for F in me}

    def run_engine(self, w_me, lo=None, hi=None, cost_bp=C.COST_BP, slip_bp=C.SLIP_BP, lag=None):
        """The book through the unchanged engine, on rows lo..hi of the calendar."""
        from rr_engine import simulate
        lag = self.d if lag is None else lag
        lo = 0 if lo is None else lo
        hi = len(self.cal) - 1 if hi is None else hi
        cal = self.cal[lo:hi + 1]
        w_me = w_me.loc[(w_me.index >= cal[0]) & (w_me.index <= cal[-1])]
        res = simulate(self.open.iloc[lo:hi + 1], self.close.iloc[lo:hi + 1], T.daily_weights(w_me, cal), lag=lag,
                       exec_price="close", deadband=T.rebalance_deadband(w_me, cal, lag=lag), cost_bp=cost_bp, slip_bp=slip_bp)
        import rr_metrics as M
        res["excess"] = M.excess_returns(res["pnl_net"], self.rf.reindex(cal), res["net"])
        return res


class Procedure:
    """One candidate procedure (model class x regime features), run unchanged through every rung."""

    def __init__(self, ctx, model, regime_on, phi=P3["cost_phi"], gamma_fixed=None, kappa_bp=P3["kappa_bp"]):
        self.ctx, self.model, self.regime_on, self.phi, self.gamma_fixed = ctx, model, regime_on, phi, gamma_fixed
        self.cols = FEATURES_ON if regime_on else FEATURES_OFF
        self.name = f"{model} | regime {'on' if regime_on else 'off'}"
        self.book = CostAwareBook(len(ctx.assets))
        self.live = {}                                         # F -> target vector
        self.log = []
        self.kappa = np.full(len(ctx.assets), kappa_bp / 1e4)   # the cost grid re-prices the optimizer

    def _rows(self, segs, need_y=True):
        p = self.ctx.panel
        r = p[p["seg"].isin(segs)].dropna(subset=self.cols + ["sig_m"])
        return r.dropna(subset=["y"]) if need_y else r

    def _targets(self, fit, F_list, start_target, start_F, sigma0, gamma):
        """Sequential month-end targets from a start state; each trade priced from the drifted book."""
        ctx, out = self.ctx, {}
        prev_w, prev_F = start_target, start_F
        rows = self._rows([(F.to_period("M") + 1).asfreq("Q") for F in F_list], need_y=False)
        for F in F_list:
            r = rows.xs(F, level=0) if F in rows.index.get_level_values(0) else None
            mu = np.zeros(len(ctx.assets)); cap = np.zeros(len(ctx.assets))
            L, ok = ctx.risk[F]
            if r is not None and len(r):
                yhat = fit.predict(r)
                ix = [ctx.assets.index(a) for a in r.index]
                mu[ix] = yhat * r["sig_m"].to_numpy()
                cap[ix] = P3["asset_cap"]
            cap = np.where(ok, cap, 0.0)
            w_held = (np.zeros(len(ctx.assets)) if prev_w is None
                      else drifted(prev_w, ctx.close, ctx.pos[prev_F] + ctx.d, ctx.pos[F]))
            k = self.phi * self.kappa + gamma
            w = self.book.solve(mu, L, w_held, k, cap, sigma0 / np.sqrt(12.0))
            out[F] = w
            prev_w, prev_F = w, F
        return out

    def _last_live_before(self, F):
        ks = [k for k in self.live if k < F]
        return (self.live[max(ks)], max(ks)) if ks else (None, None)

    def rung(self, rg):
        ctx = self.ctx
        train, val = self._rows(rg["train"]), self._rows(rg["val"])
        label, mse, fac = fit_and_choose(self.model, self.cols, train, val)
        fit_tr = Fit(label, fac, train, self.cols)
        val_F = sorted(set(ctx.me[[(F.to_period("M") + 1).asfreq("Q") == rg["val"][0] for F in ctx.me]]))
        app_F = sorted(set(ctx.me[[(F.to_period("M") + 1).asfreq("Q") == rg["q"] for F in ctx.me]]))
        if not val_F or not app_F:
            return
        start_w, start_F = self._last_live_before(val_F[0])
        lo = ctx.pos[start_F] if start_F is not None else ctx.pos[val_F[0]]
        hi = ctx.pos[app_F[0]]                                  # the last close of the validation quarter
        vq = rg["val"][0]
        gammas = (self.gamma_fixed,) if self.gamma_fixed is not None else P3["gamma_grid"]
        series = {}
        for s0 in P3["risk_budget_grid"]:
            for g in gammas:
                tg = self._targets(fit_tr, val_F, start_w, start_F, s0, g)
                w_me = pd.DataFrame(tg, index=ctx.assets).T
                if start_F is not None:
                    w_me = pd.concat([pd.DataFrame({start_F: start_w}, index=ctx.assets).T, w_me])
                res = ctx.run_engine(w_me, lo, hi)
                x = res["excess"]
                series[(s0, g)] = x[x.index.to_period("Q") == vq]
        pair, tab = choose(series)
        refit = Fit(label, fac, pd.concat([train, val]), self.cols)
        prev_w, prev_F = self._last_live_before(app_F[0])
        self.live.update(self._targets(refit, app_F, prev_w, prev_F, pair[0], pair[1]))
        coefs = {}
        m = refit.model
        if hasattr(m, "coef_"):
            coefs = dict(zip(self.cols, np.round(m.coef_, 4)))
        elif hasattr(m, "feature_importances_"):
            coefs = dict(zip(self.cols, np.round(m.feature_importances_, 4)))
        elif hasattr(m, "get_feature_importance"):
            coefs = dict(zip(self.cols, np.round(m.get_feature_importance(), 2)))
        self.log.append({"procedure": self.name, "apply_q": str(rg["q"]), "model_point": label, "val_mse": mse,
                         "sigma0": pair[0], "gamma": pair[1], "train_rows": len(train), "val_rows": len(val),
                         "coefs": coefs})

    def run(self, rungs):
        for rg in rungs:
            self.rung(rg)
        return pd.DataFrame(self.live, index=self.ctx.assets).T.sort_index()


PROCEDURES = [("EW", False)] + [(m, on) for m in ("Ridge", "Lasso", "CatBoost", "HGB") for on in (False, True)]
