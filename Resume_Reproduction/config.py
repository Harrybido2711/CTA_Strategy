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
