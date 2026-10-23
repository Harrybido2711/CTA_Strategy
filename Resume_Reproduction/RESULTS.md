# Resume Reproduction — Results

Measured on 2026-10-23. **Sample:** 37 liquid US-listed ETFs as futures proxies, daily bars,
2020-01-02 → 2026-06-29, split-adjusted copy, price returns. **Out of sample:** 18 walk-forward
quarters, 2022Q1 → 2026Q2. Each quarter is traded by choices made from the quarters before it
(`OUTLINE.md` § 4.5). **Test:** 2025Q3 → 2026Q2, read once at 14:49 against commit `36e86c4`.
**Execution:** next-close fill, 5 bp per side plus 2 bp slippage, $1 of constant notional, net 0,
gross 2.

This file is the authoritative home of every measured number. `OUTLINE.md` § 2 carries each
claim's one-line status, and `results/` carries the tables behind it.

## Bottom line

None of the four resume bullets reproduces on this data. The reasons are measurable:

- **There is no edge to keep.** At a five-day horizon the momentum signal has no edge over
  2022–2026: G5 − G1 is −0.19% per five days (t −0.93). Every MACD cell is mildly negative. Before
  costs B0 returns −1.2% a year, with a 90% CI of −11% to +9%.
- **Friction is the whole story.** B0 turns its gross book over 39 times a year. At 7 bp per side
  that costs about 500 bp a year, and turns a zero edge into −6.3% a year.
- **The rebuild changes turnover, not performance.** B1 cuts turnover 4.5% (CI −7.9% to −0.9%).
  Its Sharpe change is −0.04, with a CI of −0.52 to +0.43.
- **Turnover control is the lever that works.** The only book that survives costs is the
  turnover-penalised optimizer: +2.2% a year over 18 quarters (Sharpe 0.20) and +5.6% on Test, on
  15 turns a year.

## Claimed versus measured

| Resume claim | Measured | Where |
| --- | --- | --- |
| Momentum and MACD signals | MOM's G5 − G1 is −0.19% per 5 days (t −0.93), not monotone. One of 18 rungs found a MACD band, and none passed validation, so B0 traded MOM only | `01_bucket_mom`, `09_selected_signals_all_rungs` |
| Engine reports Sharpe, drawdown, turnover, IC, win rate | All computed. B0: Sharpe −0.41 (CI −1.07 to +0.23), drawdown −0.50 of capital, 38.9 turns a year, IC −0.014, win rate 0.502 against a base rate of 0.522 | `06_scorecard`, `01_signal_quality` |
| Over 25% of the naive return lost to execution | **Undefined as a ratio**, because the naive return is not positive (−1.2% a year). Friction costs 509 bp a year. On the train-ladder quarters alone, where the naive return was +3.3% a year, costs took 149% of it | `03_haircut_waterfall_test`, `11_waterfall_wf` |
| Trend signals work best in high-volume, low-volatility regimes | **Not supported.** HV/LV minus LV/HV is −3.8 bp per 5 days (t −0.32). The difference is positive in 2 of 5 periods, and its CI runs from −26 to +17 bp. The frozen cut gives the opposite sign | `04_regime_by_period_with_test`, `04_regime_bootstrap` |
| +8% out-of-sample Sharpe | **Not supported.** ΔSR is −0.04 over 18 quarters (CI −0.52 to +0.43) and −0.18 on Test. B0's Sharpe CI includes zero, so a percentage change is undefined | `06_scorecard`, `08_robustness_rebuild_bootstrap` |
| −14% annual turnover | **Partly.** Turnover falls −4.5% over 18 quarters (CI −7.9% to −0.9%), but rises 1.5% on Test | same |

## The numbers behind it

18 walk-forward quarters, realistic execution unless the row says otherwise:

| Book | Annual return | Volatility | Sharpe | Max drawdown | Turnover per unit gross |
| --- | --- | --- | --- | --- | --- |
| B0, before costs | −1.2% | 15.4% | −0.08 | −0.31 | 38.9 |
| B0 | −6.3% | 15.4% | −0.41 | −0.50 | 38.9 |
| B1 | −4.7% | 10.4% | −0.45 | −0.41 | 37.2 |
| MACD 12/26 prop-signal | −0.4% | 16.5% | −0.02 | −0.30 | 26.0 |
| Optimizer, net 0 | +2.2% | 10.9% | +0.20 | −0.17 | 15.1 |
| P1 150/50 (prototype) | −2.4% | 17.1% | −0.14 (−0.38 after DTB3) | −0.51 | 40.4 |

On Test alone, B0 returns −7.0% (Sharpe −0.45) and B1 −5.2% (Sharpe −0.63). The optimizer returns
+5.6% (Sharpe 0.70), and P1 +5.7%, with a Sharpe of 0.31 that falls to 0.10 after DTB3.

**Execution haircut, B0, all 18 quarters.** Each line adds one assumption, in this order:

| Step | Annual return |
| --- | --- |
| Same close, no cost | −191 bp |
| + one-day delay | +74 bp (the delay helps: five-day returns reverse) |
| + 5 bp cost | −363 bp |
| + 2 bp slippage | −145 bp |
| Realistic | −625 bp |

**Models (homework C).** The OV quarters chose Equal Weights by MSE under the one-SE rule. Ridge
(λ 0.1) had the lowest OV MSE, but Equal Weights, OLS, every Ridge and two Lassos were within one SE
of it. On Test, Equal Weights beats a zero forecast by 0.13% of MSE, with an IC of 0.031. Ridge
(λ 10) would have done slightly better on Test. The boosted trees overfit.

**Optimizer (homework D, E).** The risk preference was set as a 10% annual volatility. Every cap
and turnover-penalty pair reached for γ = 5, the top of the grid, and still ran at 13.5–14.9% on
OV, because the gross limit sets the volatility. The chosen configuration is γ 5, cap 0.20, and a
turnover penalty of twice the cost. Without the penalty the same optimizer trades 89–100 times a
year and loses 6–7% a year.

**VIX and MOVE (homework B).** B0 earns +7 bp a day when VIX is in its lowest fifth of the past
year (t 1.54), and loses in the middle three fifths. The homework's ceil(ln VIX²) cut leaves cells
of 0–15 days; Test holds no stressed VIX day. Lecture 5's residual test does not pass: G5 − G1 is
+0.09% (t 0.84), not monotone, with an IC of −0.040.

## Figures

| Figure | Shows |
| --- | --- |
| `figures/rr-equity-curves-{light,dark}.png` | B0 before and after costs, B1, the optimizer, with OV and Test shaded |
| `figures/rr-execution-haircut-{light,dark}.png` | The haircut table above as a waterfall |
| `figures/rr-regime-map-{light,dark}.png` | 3×3 volume × volatility grid with every cell's count |
| `figures/rr-rebuild-scorecard-{light,dark}.png` | B1 − B0 Sharpe and turnover with bootstrap CIs |
| `figures/rr-macd-heatmap-{light,dark}.png` | t of G5 − G1 across the MACD grid |

All five pass a panel-alignment gate, a 5 pt glyph floor and a rendered collision audit. They are
PNG pairs, which is the repository's figure contract; vector export is not part of it.

## Where the plan changed after it was written

Each change is in the run ledger or the outline, and none was made to move a number toward the
resume:

| Change | Why |
| --- | --- |
| The regime cell statistic became the signal-weighted return | The pre-registered per-date G5 − G1 inside a cell was not computable: about four assets per cell per date |
| The win-rate base rate is pooled over the sample | A per-date majority is an oracle that knows each day's market |
| Lasso's λ is a fraction of λ_max | The lecture's absolute values zero every coefficient on daily returns |
| A display flag marks VIX/MOVE states under 60 days | Cells of 0–15 days were being shown without one |
| γ stayed at the top of the pre-set grid | The 10% target was not reachable; the grid was not widened |

## Open threads for the next round

The evidence points at three levers, none of them tried yet:

- **Trade less.** Every book that survives costs is a book that trades less: the optimizer with a
  turnover penalty, and to a lesser degree MACD 12/26 at 26 turns a year. B0's score is a daily
  re-ranked percentile, and that is what drives its 39 turns.
- **Match the horizon to the signal.** At a five-day horizon these series reverse, which is why the
  one-day delay helps. A trend signal is usually scored, and held, over weeks to months.
- **Treat the regime result as cut-dependent.** The rolling, frozen and full-sample cuts disagree on
  sign. No single cut should carry a claim.

## Regenerate

```bash
.venv/bin/pip install -r Resume_Reproduction/requirements.txt
.venv/bin/python Resume_Reproduction/run_00_data.py          # W1 data fix and checks
.venv/bin/python -m pytest -q Resume_Reproduction/tests      # 30 tests, incl. parity with backtest.py
.venv/bin/python Resume_Reproduction/run_01_signals.py       # W3
.venv/bin/python Resume_Reproduction/run_02_portfolios.py    # W4
.venv/bin/python Resume_Reproduction/run_03_haircut.py       # W4
.venv/bin/python Resume_Reproduction/run_04_regimes.py       # W5
.venv/bin/python Resume_Reproduction/run_05_vix_move.py      # W6
.venv/bin/python Resume_Reproduction/run_06_rebuild.py       # W7
.venv/bin/python Resume_Reproduction/run_07_models.py        # W8
.venv/bin/python Resume_Reproduction/run_08_optimizer.py     # W9
.venv/bin/python Resume_Reproduction/run_09_test.py          # W10, the Test read
.venv/bin/python Resume_Reproduction/run_10_robustness.py    # W10
.venv/bin/python Resume_Reproduction/run_11_reconcile.py     # W11, plot data and ledger status
.venv/bin/python Resume_Reproduction/make_rr_figures.py      # W11, figures
```

Every script is deterministic, and every result file carries its sample statement and a JSON
sidecar with the commit it ran at.
