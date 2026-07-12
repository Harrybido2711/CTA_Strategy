"""Validate and explore all daily OHLCV ETF files in CTA_data.

Run with Python 3.9+:
    python analyze_cta_data.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


DATA_DIR = Path(__file__).resolve().parent / "CTA_data"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
REQUIRED = {
    "ts_event", "rtype", "publisher_id", "instrument_id",
    "open", "high", "low", "close", "volume", "symbol",
}
NUMERIC = ["rtype", "publisher_id", "instrument_id", "open", "high", "low", "close", "volume"]


def load_one(path: Path) -> pd.DataFrame:
    """Load one CSV with explicit date parsing and basic schema validation."""
    df = pd.read_csv(path, parse_dates=["ts_event"])
    missing = REQUIRED.difference(df.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="raise")
    return df


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    manifest = pd.read_csv(DATA_DIR / "_manifest.csv").set_index("symbol")
    results = []
    loaded = {}

    for path in sorted(DATA_DIR.glob("*_ohlcv_1d.csv")):
        symbol = path.name.split("_")[0]
        errors = []
        try:
            df = load_one(path)
            loaded[symbol] = df
            if df["symbol"].nunique() != 1 or df["symbol"].iloc[0] != symbol:
                errors.append("symbol/file mismatch")
            if df["ts_event"].isna().any() or df[NUMERIC].isna().any().any():
                errors.append("missing value")
            if df["ts_event"].duplicated().any():
                errors.append("duplicate timestamp")
            if not df["ts_event"].is_monotonic_increasing:
                errors.append("timestamps not sorted")
            bad_ohlc = (
                (df["high"] < df[["open", "close", "low"]].max(axis=1))
                | (df["low"] > df[["open", "close", "high"]].min(axis=1))
                | (df["volume"] < 0)
            )
            if bad_ohlc.any():
                errors.append(f"{int(bad_ohlc.sum())} invalid OHLC/volume rows")
            if symbol not in manifest.index or len(df) != int(manifest.loc[symbol, "rows"]):
                errors.append("manifest row-count mismatch")

            overnight = (df["open"] - df["close"].shift(1)).abs()
            intraday = (df["close"] - df["open"]).abs()
            overnight_pct = (df["open"] / df["close"].shift(1) - 1).abs() * 100
            intraday_pct = (df["close"] / df["open"] - 1).abs() * 100
            results.append({
                "symbol": symbol,
                "rows": len(df),
                "start": df["ts_event"].min().date(),
                "end": df["ts_event"].max().date(),
                "avg_abs_overnight_usd": overnight.mean(),
                "avg_abs_intraday_usd": intraday.mean(),
                "overnight_gt_intraday_usd": overnight.mean() > intraday.mean(),
                "avg_abs_overnight_pct": overnight_pct.mean(),
                "avg_abs_intraday_pct": intraday_pct.mean(),
                "overnight_gt_intraday_pct": overnight_pct.mean() > intraday_pct.mean(),
                "status": "PASS" if not errors else "FAIL: " + "; ".join(errors),
            })
        except Exception as exc:
            results.append({"symbol": symbol, "status": f"LOAD FAIL: {exc}"})

    summary = pd.DataFrame(results).sort_values("symbol")
    summary.to_csv(OUTPUT_DIR / "validation_and_gap_summary.csv", index=False)

    chosen = [s for s in ["SPY", "TLT", "GLD", "EEM", "DBC"] if s in loaded]
    fig, axes = plt.subplots(len(chosen), 1, figsize=(12, 2.5 * len(chosen)), sharex=True)
    if len(chosen) == 1:
        axes = [axes]
    for ax, symbol in zip(axes, chosen):
        df = loaded[symbol]
        ax.plot(df["ts_event"], df["close"], linewidth=1, label=f"{symbol} close")
        ax.set_ylabel("USD")
        ax.legend(loc="upper left")
        ax.grid(alpha=0.25)
    axes[-1].set_xlabel("Date (UTC)")
    fig.suptitle("Selected ETF daily close prices (unadjusted)")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "selected_price_trends.png", dpi=160)
    plt.close(fig)

    passed = summary["status"].eq("PASS").sum()
    print(f"Loaded and checked {len(summary)} files: {passed} PASS, {len(summary) - passed} FAIL")
    print(
        "Overnight mean absolute move > intraday: "
        f"{int(summary['overnight_gt_intraday_usd'].sum())}/{len(summary)} by dollars; "
        f"{int(summary['overnight_gt_intraday_pct'].sum())}/{len(summary)} by percent"
    )
    print(f"Outputs written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
