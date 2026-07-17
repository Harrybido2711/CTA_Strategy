# Python Functions

## `pandas.merge_asof`

Official documentation: [pandas.merge_asof](https://pandas.pydata.org/docs/reference/api/pandas.merge_asof.html)

`pd.merge_asof()` performs an approximate ordered merge. Unlike a normal `merge`, it does not require the values in the merge key to be exactly equal. For every row in the left DataFrame, it searches the right DataFrame for the closest eligible row.

The DataFrames must be sorted in ascending order by the merge key before calling it:

```python
data = data.sort_values('ts_event')
dollar = dollar.sort_values('ts_event')

df = pd.merge_asof(
    left=data,
    right=dollar,
    on='ts_event',
    direction='backward'
)
```

In this example:

- `left=data`: determines which timestamps and rows appear in the result.
- `right=dollar`: supplies values to matching left-side rows.
- `on='ts_event'`: uses `ts_event` as the ordered matching key in both tables.
- `direction='backward'`: selects the closest right-side timestamp that is less than or equal to the left-side timestamp.

For example:

```text
left: data                 right: dollar
ts_event  close            ts_event  dollar
1.2       100              1.3       10000
1.3       102              1.4       15000
1.5       104
```

The result is:

```text
ts_event  close  dollar
1.2       100    NaN
1.3       102    10000
1.5       104    15000
```

Explanation:

- At `1.2`, the right table has no timestamp less than or equal to `1.2`, so the match is `NaN`.
- At `1.3`, there is an exact match with right-side `1.3`.
- At `1.5`, there is no right-side `1.5`, so the closest earlier timestamp, `1.4`, is selected.
- Right-side `1.4` does not create a separate result row because the left table has no `1.4` row. Its value can still be matched to a later left-side row.

In short: **the left table determines the result rows; the right table provides the matched values.**

### `direction`

- `backward`: closest right key where `right_key <= left_key`. This is commonly used in backtesting because it only uses information available at or before the current time.
- `forward`: closest right key where `right_key >= left_key`.
- `nearest`: closest right key in either direction. This can select a future record and may cause look-ahead bias in a backtest.

### Other useful parameters

- `left_on` / `right_on`: use these when the matching columns have different names.
- `by`: first require another column, such as `symbol`, to match, and then perform the time match within that group.
- `tolerance`: specify the maximum permitted distance between the left and right keys.
- `allow_exact_matches=True`: allow equal timestamps to match. If set to `False`, `backward` uses strictly earlier records and `forward` uses strictly later records.
- `suffixes`: distinguish overlapping non-key column names from the left and right tables.

### Signal-delay example

```python
dollar['ts_event'] = dollar['ts_event'] + timedelta(days=1)
```

This changes only the timestamps in `dollar`; it does not change or delete rows in `data`. For example:

```text
Before delay              After one-day delay
ts_event  dollar          ts_event  dollar
1.2       10000           1.3       10000
1.3       15000           1.4       15000
```

After the delay, the signal originally created on `1.2` becomes eligible for matching from `1.3`. Earlier rows from the left-side market data can still appear in the merged result, but their signal value will be `NaN` if there is no eligible earlier right-side record.

Note that `timedelta(days=1)` adds one calendar day, not one trading day.
