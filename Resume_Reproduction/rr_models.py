"""Models on the walk-forward ladder (homework C, OUTLINE W8, chapter 05).

One row per (date, asset). Features are bounded scores (centred percentiles, or tercile labels
minus one), so winsorising them is a no-op; the target is winsorised at 1% / 99% inside each
fitting window only, and every model is scored on the raw forward return. Linear models see
features and target z-scored with fitting-window statistics (WF 6).

Each rung: fit on train, select features on validation (Lasso only), refit on train + validation,
predict the test quarter once. The model class and its hyperparameters are the outer layer,
chosen on the OV quarters by MSE with a one-SE rule.
"""
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge

import config as C
import rr_data as D
import rr_regimes as R
import rr_signals as S

FEATURES = ["mom", "macd", "macd_hist", "macd_smooth", "sigma_rank", "volume_rank",
            "volume_tercile", "sigma_tercile", "vix_state", "move_state"]

# simplest first: the one-SE rule picks the first model in this order that is within one SE
MODEL_ORDER = (["EW"] + [f"Lasso f={f}" for f in (0.7, 0.5, 0.1, 0.05)]
               + [f"Ridge l={l}" for l in (10, 1, 0.1, 0.01)] + ["OLS", "HGB", "CatBoost"])


def build_panel(wd):
    """Long frame (date, asset) -> features and target, every column known by the close of the date."""
    close = wd.close
    m = S.macd_line(close, 12, 26)
    hist = m - S.ema(m, C.BASELINE["macd_signal_span"])
    vol = D.panel(wd.etfs, "volume", wd.cal)
    V, SIG = R.volume_measure(vol), R.sigma_measure(close)
    vlab, slab = R.cut_rolling(V), R.cut_rolling(SIG)
    vix, _ = D.load_index("VIX", wd.cal)
    move, _ = D.load_index("MOVE", wd.cal)
    lv = R.index_labels(vix, wd.cal, wd.rungs, C.PRE_TEST_END)["D rolling"]
    lm = R.index_labels(move, wd.cal, wd.rungs, C.PRE_TEST_END)["D rolling"]
    bc = lambda s: pd.DataFrame(np.repeat(s.to_numpy()[:, None], close.shape[1], axis=1),  # noqa: E731
                                index=close.index, columns=close.columns)
    parts = {
        "mom": wd.mom, "macd": wd.cells[(12, 26)], "macd_hist": S.centred(hist),
        "macd_smooth": S.macd_score(close, 12, 26, "proportional", 5),
        "sigma_rank": S.centred(SIG), "volume_rank": S.centred(V),
        "volume_tercile": vlab - 1, "sigma_tercile": slab - 1,       # rolling cut D only
        "vix_state": bc(lv) - 1, "move_state": bc(lm) - 1,           # rolling cut D only
        "y": wd.fwd,
    }
    long = pd.concat({k: v.stack(dropna=False) for k, v in parts.items()}, axis=1)
    long.index.names = ["date", "asset"]
    return long


def _z(X, mu, sd):
    return (X - mu) / sd.replace(0, 1.0)


class Fitted:
    """A model fitted on one window; predicts in return units."""

    def __init__(self, name, fit_rows, sel_rows=None):
        self.name = name
        X, y = fit_rows[FEATURES], fit_rows["y"]
        lo, hi = y.quantile(0.01), y.quantile(0.99)
        yw = y.clip(lo, hi)
        self.mu, self.sd = X.mean(), X.std()
        self.my, self.sy = yw.mean(), yw.std()
        Z, zy = _z(X, self.mu, self.sd), (yw - self.my) / self.sy
        self.features = list(FEATURES)
        self.coef = None
        if name == "EW":
            self.sign = np.sign([np.corrcoef(Z[f], zy)[0, 1] for f in FEATURES])
            c = (Z.to_numpy() * self.sign).mean(axis=1)
            self.m = LinearRegression().fit(c[:, None], zy)
            self.coef = pd.Series(self.sign * self.m.coef_[0] / len(FEATURES), index=FEATURES)
        elif name == "OLS":
            self.m = LinearRegression().fit(Z, zy); self.coef = pd.Series(self.m.coef_, index=FEATURES)
        elif name.startswith("Ridge"):
            lam = float(name.split("=")[1])
            self.m = Ridge(alpha=lam * len(Z)).fit(Z, zy); self.coef = pd.Series(self.m.coef_, index=FEATURES)
        elif name.startswith("Lasso"):
            raise RuntimeError("use fit_lasso")
        elif name == "HGB":
            self.m = HistGradientBoostingRegressor(max_depth=3, max_iter=200, learning_rate=0.05, random_state=0).fit(X, yw)
        elif name == "CatBoost":
            from catboost import CatBoostRegressor
            self.m = CatBoostRegressor(depth=4, iterations=300, learning_rate=0.05, loss_function="RMSE",
                                       random_seed=0, verbose=0, thread_count=4).fit(X, yw)
        else:
            raise ValueError(name)

    def predict(self, rows):
        X = rows[FEATURES]
        if self.name in ("HGB", "CatBoost"):
            return pd.Series(self.m.predict(X), index=rows.index)
        Z = _z(X, self.mu, self.sd)
        if self.name == "EW":
            c = (Z.to_numpy() * self.sign).mean(axis=1)
            z = self.m.predict(c[:, None])
        else:
            z = self.m.predict(Z[self.features])
        return pd.Series(self.my + self.sy * z, index=rows.index)


class FittedLasso(Fitted):
    """Lasso as a feature selector: fit on train, prune on validation, refit OLS on train + validation."""

    def __init__(self, name, train, val, refit):
        f = float(name.split("=")[1])
        self.name = name
        X, y = train[FEATURES], train["y"]
        yw = y.clip(y.quantile(0.01), y.quantile(0.99))
        mu, sd = X.mean(), X.std()
        Z, zy = _z(X, mu, sd), (yw - yw.mean()) / yw.std()
        lam_max = float(np.max(np.abs(Z.to_numpy().T @ zy.to_numpy())) / len(Z))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            las = Lasso(alpha=f * lam_max, max_iter=10000).fit(Z, zy)
        surv = [c for c, b in zip(FEATURES, las.coef_) if b != 0]
        order = sorted(surv, key=lambda c: abs(las.coef_[FEATURES.index(c)]))

        def val_mse(feats):
            if not feats:
                return float(((val["y"] - yw.mean()) ** 2).mean())
            m = LinearRegression().fit(Z[feats], zy)
            p = yw.mean() + yw.std() * m.predict(_z(val[FEATURES], mu, sd)[feats])
            return float(((val["y"] - p) ** 2).mean())
        keep = list(surv)
        for c in order:                               # one backward pass on the validation quarter
            trial = [k for k in keep if k != c]
            if val_mse(trial) < val_mse(keep):
                keep = trial
        self.selected_after_lasso, self.kept = surv, keep
        X2, y2 = refit[FEATURES], refit["y"]
        y2w = y2.clip(y2.quantile(0.01), y2.quantile(0.99))
        self.mu, self.sd = X2.mean(), X2.std()
        self.my, self.sy = y2w.mean(), y2w.std()
        self.features = keep
        Z2, zy2 = _z(X2, self.mu, self.sd), (y2w - self.my) / self.sy
        if keep:
            self.m = LinearRegression().fit(Z2[keep], zy2)
            self.coef = pd.Series(0.0, index=FEATURES); self.coef[keep] = self.m.coef_
        else:
            self.m = None
            self.coef = pd.Series(0.0, index=FEATURES)

    def predict(self, rows):
        if self.m is None:
            return pd.Series(self.my, index=rows.index)
        z = self.m.predict(_z(rows[FEATURES], self.mu, self.sd)[self.features])
        return pd.Series(self.my + self.sy * z, index=rows.index)


def rung_rows(panel, cal, rung):
    def take(pos):
        d = cal[pos]
        return panel.loc[panel.index.get_level_values("date").isin(d)].dropna(subset=FEATURES + ["y"])
    test = panel.loc[panel.index.get_level_values("date").isin(cal[rung["test"]])].dropna(subset=FEATURES)
    return take(rung["train"]), take(rung["val"]), take(rung["refit"]), test


def fit_rung(name, panel, cal, rung):
    train, val, refit, test = rung_rows(panel, cal, rung)
    model = FittedLasso(name, train, val, refit) if name.startswith("Lasso") else Fitted(name, refit)
    resid = refit["y"] - model.predict(refit)
    return model, model.predict(test), resid
