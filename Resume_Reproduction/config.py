"""Every fixed setting of the reproduction, in one place.

Each constant here was decided before the data it governs was read (OUTLINE.md section 4,
DATA.md). Nothing in this file may be changed after a result has been looked at without the
change being logged in results/run_ledger.csv.
"""
import os

# ----------------------------------------------------------------------------- paths
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CTA_DATA = os.path.join(ROOT, "CTA_data")
INDICES = os.path.join(CTA_DATA, "_indices")
DATA_ADJ = os.path.join(HERE, "data", "adjusted")
DATA_EXT = os.path.join(HERE, "data", "external")
RESULTS = os.path.join(HERE, "results")
FIGURES = os.path.join(HERE, "figures")

# ----------------------------------------------------------------------------- data (DATA.md 1-4)
SAMPLE_START = "2020-01-02"
SAMPLE_END = "2026-06-29"
SPLIT_DATE = "2025-12-05"                       # 2-for-1 forward split, unadjusted in CTA_data
SPLIT_TICKERS = ("XLB", "XLE", "XLK", "XLU", "XLY")
SPLIT_RATIO = 2.0
# Cboe's official closes on the three days the class VIX file disagrees with them
VIX_CORRECTIONS = {"2021-08-11": 16.06, "2021-10-01": 21.15, "2026-02-06": 17.76}
INDEX_FFILL_LIMIT = 1                           # VIX/MOVE forward-filled at most one day
EXTERNAL_STAMP = "2026-10-23"                   # download date of every file in data/external
VENDOR_GAP = ("2022-11-21", "2022-12-09")       # IEF, TLT, SHY, QQQ miss days inside this window

UNIVERSE_CATEGORY = {
    "SPY": "equity", "QQQ": "equity", "IWM": "equity", "DIA": "equity", "MDY": "equity",
    "XLK": "equity", "XLF": "equity", "XLE": "equity", "XLV": "equity", "XLI": "equity",
    "XLY": "equity", "XLP": "equity", "XLU": "equity", "XLB": "equity", "XLRE": "equity",
    "XLC": "equity", "EFA": "equity", "EEM": "equity", "VGK": "equity", "EWJ": "equity",
    "FXI": "equity",
    "TLT": "bonds", "IEF": "bonds", "SHY": "bonds", "AGG": "bonds", "LQD": "bonds",
    "HYG": "bonds", "TIP": "bonds",
    "GLD": "commodities", "SLV": "commodities", "DBC": "commodities", "USO": "commodities",
    "UNG": "commodities", "DBA": "commodities",
    "VNQ": "alternatives", "GDX": "alternatives", "UUP": "alternatives",
}
SAMPLE_STATEMENT = ("37 liquid US-listed ETFs as futures proxies; daily UTC-dated bars; "
                    "2020-01-02 to 2026-06-29; split-adjusted copy (DATA.md 4); "
                    "dividends unadjusted unless the file says total return")

# ----------------------------------------------------------------------------- walk-forward (OUTLINE 4.5)
WARMUP_END = "2020-12-31"
WF_FIRST_TEST_Q = "2022Q1"
WF_LAST_TEST_Q = "2026Q2"
OV_QUARTERS = ("2024Q3", "2024Q4", "2025Q1", "2025Q2")
TEST_QUARTERS = ("2025Q3", "2025Q4", "2026Q1", "2026Q2")
PRE_TEST_END = "2025-06-30"           # nothing after this date is looked at before W10
H = 5                                 # forward-return horizon, trading days
SKIP = 1                              # scored return close_{t+1} -> close_{t+6}
PURGE = H + 1                         # rows dropped at the end of every fitting window
NW_LAG = H - 1

# ----------------------------------------------------------------------------- execution (OUTLINE 4.2, Q2)
LAG = 1
EXEC_PRICE = "close"
COST_BP = 5.0                         # per side, approved by Harry 2026-10-23
SLIP_BP = 2.0
HOLD = 5                              # overlapping tranches: held weight = 5-day mean of targets
GROSS = 2.0

# ----------------------------------------------------------------------------- B0, frozen before any rung runs
BASELINE = {
    "mom_lookback": 21,               # trailing mean of daily returns (chapter 02)
    "vol_window": 21,                 # sigma through t-1 (chapter 02 4)
    "pct_window": 252, "pct_min_periods": 126,
    "macd_ladder": (1, 5, 10, 21, 63),          # chapter 03's geometric ladder
    "macd_reference_cell": (12, 26),
    "macd_signal_span": 9,
    "macd_rules": ("zero", "crossover", "proportional"),
    "macd_rule_in_book": "proportional",
    "band_t_min": 1.0,                # a cell is warm if its G5-G1 spread is at least one NW SE above 0
    "band_needs_neighbour": True,     # and at least one adjacent cell on the ladder is warm too
    "smoothers": (1, 2, 3, 5, 9),     # EMA span; 1 = none; applied to a cell only when q < n_f
    "smoother_criterion": "spread per unit score turnover, on the rung's training window",
    "val_check": "band score's G5-G1 spread on the validation quarter > 0, else MOM only that quarter",
    "score": "0.5 * centred MOM + 0.5 * centred MACD band score",
    "weights": "score demeaned across assets, scaled to gross 2, net 0; then 5-day overlap",
}

# ----------------------------------------------------------------------------- B1, frozen before any rung runs
REBUILD = {
    "switches": ("vol_scaling_with_cap", "regime_multiplier", "deadband"),
    "cap": 0.20,                      # |w| <= 0.20 of capital, cap then renormalise, repeated once
    "kappa": 0.5,                     # regime multiplier on the scope below
    "kappa_scope": "LV/HV corner",    # low-volume, high-volatility cell, rolling cut D
    "deadband_multiple": 1.0,         # x median daily |dw_held| of B0 in the rung's training window
    "ov_sensitivity": {"deadband_multiple": (0.25, 0.5, 1, 2), "kappa": (1, 0.75, 0.5, 0.25),
                       "kappa_scope": ("LV/HV corner", "high-sigma row")},
}

# ----------------------------------------------------------------------------- optimizer (W9, homework D and E)
OPTIMIZER = {
    "target_vol": 0.10,                       # the risk preference: 10% annualised book volatility
    "gamma_grid": (0.3, 0.5, 1, 2, 5),
    "cap_grid": (0.20, 0.25, 0.30),
    "tau_multiple_grid": (0.0, 1.0, 2.0),     # tau_i = multiple x (cost + slippage) per dollar traded
    "covariance": "sample covariance of the chosen model's refit-window residuals",
    "rule": "per (cap, tau) the gamma whose OV vol is closest to target_vol; then the one-SE rule on OV "
            "mean daily net return, simplest = lowest cap, then highest tau",
}

# ----------------------------------------------------------------------------- ROUND 2: time-series momentum (ROUND2.md)
# Frozen 2026-10-23 before any Round 2 number was computed. Parameters are the paper's unless noted.
ROUND2 = {
    "source": "Moskowitz, Ooi and Pedersen (2012), Time Series Momentum, SSRN 2089463",
    "month_days": 21,
    "lookback_months": 12,                    # paper: k = 12 (TSMOM)
    "holding_months": 1,                      # paper: h = 1
    "lookback_grid_months": (1, 3, 6, 9, 12), # paper's Table 2 grid, truncated: 24+ months does not fit 2020-2026
    "holding_grid_months": (1, 3),
    "signal": "sign of the past k-month excess return, total-return prices minus DTB3",
    "ewma_com_days": 60,                      # paper eq. 1: centre of mass 60 days
    "annualise": 261,                         # paper eq. 1
    "asset_vol_target": 0.40,                 # paper: 40% / sigma per instrument, averaged over 1/S
    "asset_weight_cap": 0.50,                 # ours: no ETF above 0.5 of capital (SHY would be ~0.5 uncapped)
    "gross_cap": 3.0,                         # ours: a margin account, not futures
    "book_vol_target": 0.10,                  # ours: T1 scales the whole book to 10% ex-ante volatility
    "book_cov_com_days": 60,
    "regime_index": "VIX", "regime_cut": "D rolling 252-day tercile",
    "regime_multiplier_grid": (1.0, 0.75, 0.5, 0.25),   # applied to T1's leverage in the high-VIX tercile
    "regime_rule": "choose on 2021-02..2024-06 by excess-return Sharpe, one-SE rule toward 1.0; OV confirms",
    "deadband": 0.005,                        # ours: T2 skips rebalance trades under 0.5% of capital
    "prices": "total return (distributions reinvested); price return as a robustness row",
    "rebalance": "signal at the last close of each month; trade at the next close (lag 1)",
    "first_signal": "2021-01-29",             # first month-end with a full 12-month lookback
}
