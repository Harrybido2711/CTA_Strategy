# 07 · Toolbox: pandas

> - **Answers:** how the non-obvious pandas functions in this project actually behave.
> - **Prerequisites:** none — reference material.
> - **Related:** [02](02-building-signals.md), [04](04-understanding-backtesting.md).

---

## `pandas.merge_asof`

[Docs](https://pandas.pydata.org/docs/reference/api/pandas.merge_asof.html) · An approximate ordered
merge: keys need not be equal, so for each left row it finds the closest eligible right row. **Both
frames must be sorted by the key first.**

```python
data   = data.sort_values('ts_event')
dollar = dollar.sort_values('ts_event')

df = pd.merge_asof(left=data, right=dollar, on='ts_event', direction='backward')
```

- `left` determines which rows appear in the result; `right` supplies matched values.
- `direction='backward'` takes the closest right key ≤ left key.

```text
left: data          right: dollar        result
ts_event  close     ts_event  dollar     ts_event  close  dollar
1.2       100       1.3       10000      1.2       100    NaN     no right key ≤ 1.2
1.3       102       1.4       15000      1.3       102    10000   exact match
1.5       104                            1.5       104    15000   closest earlier is 1.4
```

Right-side `1.4` creates no row of its own — the left table has no `1.4`. In short: **left decides
the rows, right provides the values.**

### `direction`

| Value        | Match                            | Note                                                    |
| ------------ | -------------------------------- | ------------------------------------------------------- |
| `backward` | closest`right_key <= left_key` | standard for backtesting — uses only past information  |
| `forward`  | closest`right_key >= left_key` |                                                         |
| `nearest`  | closest in either direction      | **can select a future record → look-ahead bias** |

### Other parameters

- `left_on` / `right_on` — differing column names.
- `by` — require another column (e.g. `symbol`) to match first, then time-match within that group.
- `tolerance` — maximum permitted key distance.
- `allow_exact_matches=False` — makes `backward` strictly earlier, `forward` strictly later.
- `suffixes` — disambiguate overlapping non-key columns.

### Signal-delay example

```python
dollar['ts_event'] = dollar['ts_event'] + timedelta(days=1)
```

Only `dollar`'s timestamps move; `data`'s rows are untouched. A signal created on `1.2` becomes
matchable from `1.3` onward; earlier left rows still appear, with `NaN` where no eligible right
record exists. Note `timedelta(days=1)` is one **calendar** day, not one trading day.

---

## `SettingWithCopyWarning`

Raised on **chained indexing** — filter, then assign into the filtered result:

```python
df[df.symbol == "SPY"]["signal"] = 0        # ⚠️ warns, and may silently do nothing
df.loc[df.symbol == "SPY", "signal"] = 0    # ✅ unambiguous
```

pandas cannot tell whether `df[...]` is a view or a copy, so it cannot tell whether you meant to
modify `df` or a temporary — and the write may never reach `df`.

**Why bother.** Rarely matters for throwaway analysis, but once code is reused, a flood of
meaningless warnings buries the one that mattered.

---

## `DataFrame.ewm`

Exponentially weighted moving average — weights recent observations more heavily, unlike
`rolling(N).mean()` which weights the window equally.

```python
signal = returns.ewm(halflife=H).mean()
```

`halflife` is the periods after which an observation's weight halves — the parameter worth
grid-searching ([02 § 7](02-building-signals.md)).

`span`, `com`, and `alpha` parameterize the same decay differently. Pick one and state which: a
"20" means three different things depending on the argument.

---

Reference chapter — no next step. Used by [02 · Signals](02-building-signals.md) and
[04 · Backtesting](04-understanding-backtesting.md).

[Index](00-index.md)
