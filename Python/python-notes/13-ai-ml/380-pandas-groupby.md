---

# 380. Pandas GroupBy
# हिंदी में: Pandas GroupBy (डेटा को group करके summary निकालना)

---

## 🔵 Simple Definition (English)
`groupby` splits a DataFrame into groups by one or more columns, applies a function (sum, mean, count, custom) to each group, and combines the results. This is the "split - apply - combine" pattern, the pandas version of SQL `GROUP BY`.

## 🔵 सरल परिभाषा (Hindi)
`groupby` DataFrame को एक या ज्यादा columns के आधार पर groups में बांटता है, हर group पर function (sum, mean, count या custom) चलाता है, और results को जोड़ देता है। यह "split - apply - combine" pattern है, यानी SQL के `GROUP BY` का pandas version।

---

## 🔴 Problem it Solves
Raw data has thousands of rows, but business questions are about groups: revenue per city, average order value per category, top order per user. Without `groupby` you would write Python loops with dictionaries, which are slow and long. `groupby` runs in optimized C/Cython code and gives the answer in one line.

## 🔴 यह क्यों बना? (Hindi)
Raw data में हजारों rows होती हैं, लेकिन business के सवाल groups के बारे में होते हैं: हर शहर की revenue, हर category का average order value, हर user का सबसे बड़ा order। `groupby` के बिना आपको loops और dictionaries लिखनी पड़ती, जो धीमी और लंबी होती हैं। `groupby` optimized C/Cython code में चलता है और जवाब एक line में देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → df.groupby("city") does NOT compute anything yet (lazy). It makes a GroupBy object
Step 2 → SPLIT: rows are bucketed by the unique values in the key column(s)
Step 3 → APPLY: an aggregation (sum, mean...), transform or filter runs per bucket
Step 4 → COMBINE: results are stitched back into a Series or DataFrame
Step 5 → agg()       -> one row per group (smaller result)
         transform() -> same length as the original (per-row result)
         filter()    -> keeps or drops whole groups
Step 6 → The group keys become the index, unless as_index=False or reset_index()

df -> groupby("city") -> [Delhi rows][Mumbai rows][Pune rows] -> sum -> one number each
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → df.groupby("city") अभी कुछ compute नहीं करता (lazy)। यह GroupBy object बनाता है
Step 2 → SPLIT: key column के unique values के हिसाब से rows buckets में बंटती हैं
Step 3 → APPLY: हर bucket पर aggregation (sum, mean...), transform या filter चलता है
Step 4 → COMBINE: results को वापस Series या DataFrame में जोड़ा जाता है
Step 5 → agg()       -> हर group की एक row (छोटा result)
         transform() -> original जितनी ही length (हर row का result)
         filter()    -> पूरे group को रखता या हटाता है
Step 6 → Group keys index बन जाती हैं, जब तक as_index=False या reset_index() न हो
```

---

## 🟡 Real World Example
Zomato's analytics team has a table of orders. Every morning a job computes revenue, order count and average tip per city and per category, then ranks cities. Razorpay computes daily settlement totals per merchant. A FastAPI dashboard endpoint returns "revenue by city" for a chart. All of these are one `groupby` call.

## 🟡 Real Example Hindi mein
Zomato की analytics team के पास orders की table है। हर सुबह एक job हर शहर और हर category के हिसाब से revenue, order count और average tip निकालती है, फिर शहरों को rank करती है। Razorpay हर merchant का daily settlement total निकालता है। FastAPI dashboard का endpoint chart के लिए "शहर के हिसाब से revenue" लौटाता है। ये सब एक `groupby` call हैं।

---

## 💻 Code Example — Basic
```python
# Basic groupby examples (pandas 3.x)
import pandas as pd                                   # import pandas

df: pd.DataFrame = pd.DataFrame({                     # small order table
    "city": ["Delhi", "Delhi", "Mumbai", "Mumbai", "Pune"],   # group key
    "amount": [100, 200, 150, 50, 300],               # numbers to summarize
})
print(df.groupby("city")["amount"].sum())             # total per city
print(df.groupby("city")["amount"].agg(["count", "mean"]))   # several stats at once
print(df.groupby("city", as_index=False)["amount"].max())    # keep city as a normal column
df["city_avg"] = df.groupby("city")["amount"].transform("mean")   # per-row group average
print(df)                                             # same length as original
print(df.groupby("city").filter(lambda g: len(g) > 1))   # keep only cities with 2+ orders

# Output:
# city
# Delhi     300
# Mumbai    200
# Pune      300
# Name: amount, dtype: int64
#         count   mean
# city
# Delhi       2  150.0
# Mumbai      2  100.0
# Pune        1  300.0
#      city  amount
# 0   Delhi     200
# 1  Mumbai     150
# 2    Pune     300
#      city  amount  city_avg
# 0   Delhi     100     150.0
# 1   Delhi     200     150.0
# 2  Mumbai     150     100.0
# 3  Mumbai      50     100.0
# 4    Pune     300     300.0
#      city  amount  city_avg
# 0   Delhi     100     150.0
# 1   Delhi     200     150.0
# 2  Mumbai     150     100.0
# 3  Mumbai      50     100.0
```

## 💻 Code Example — Advanced
```python
# Production style: validated report with named aggregation, share-of-total, top-1 per group
from __future__ import annotations                    # allow modern type hints everywhere
import pandas as pd                                   # pandas


def build_orders() -> pd.DataFrame:
    """Return sample order data."""
    return pd.DataFrame({                             # one row per order
        "order_id": [1, 2, 3, 4, 5, 6],               # unique id
        "city": ["Delhi", "Delhi", "Mumbai", "Mumbai", "Pune", "Delhi"],   # city
        "category": ["food", "grocery", "food", "food", "grocery", "food"],   # type
        "amount": [250.0, 900.0, 300.0, 120.0, 640.0, 410.0],   # order value
        "tip": [10.0, 0.0, 20.0, 5.0, 0.0, 15.0],     # tip given
    })


def city_report(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue report per (city, category), sorted by revenue."""
    required: set[str] = {"city", "category", "amount", "tip"}   # columns we need
    missing: set[str] = required - set(df.columns)    # which ones are absent
    if missing:                                       # fail early with a clear message
        raise KeyError(f"missing columns: {sorted(missing)}")
    return (
        df.groupby(["city", "category"])              # two keys -> MultiIndex
        .agg(                                         # named aggregation: new_name=(col, func)
            orders=("order_id", "count"),             # number of orders
            revenue=("amount", "sum"),                # total money
            avg_tip=("tip", "mean"),                  # average tip
            max_order=("amount", "max"),              # biggest order
        )
        .reset_index()                                # keys back to normal columns
        .sort_values("revenue", ascending=False)      # biggest revenue first
    )


orders: pd.DataFrame = build_orders()                 # build data
print(city_report(orders).to_string(index=False))     # print the report
orders["share_pct"] = (                               # each order's share inside its city
    orders["amount"] / orders.groupby("city")["amount"].transform("sum") * 100
).round(1)                                            # one decimal place
print(orders[["city", "amount", "share_pct"]])        # show result
top: pd.DataFrame = orders.sort_values("amount", ascending=False).groupby("city").head(1)   # top order per city
print(top[["city", "order_id", "amount"]].sort_values("city"))   # tidy output
print(orders.groupby("city")["amount"].rank(ascending=False).tolist())   # rank inside each city
try:                                                  # error handling demo
    city_report(orders.drop(columns=["tip"]))         # tip column removed
except KeyError as e:                                 # catch the missing-column error
    print("Error:", e)                                # clear message

# Output:
#   city category  orders  revenue  avg_tip  max_order
#  Delhi  grocery       1    900.0      0.0      900.0
#  Delhi     food       2    660.0     12.5      410.0
#   Pune  grocery       1    640.0      0.0      640.0
# Mumbai     food       2    420.0     12.5      300.0
#      city  amount  share_pct
# 0   Delhi   250.0       16.0
# 1   Delhi   900.0       57.7
# 2  Mumbai   300.0       71.4
# 3  Mumbai   120.0       28.6
# 4    Pune   640.0      100.0
# 5   Delhi   410.0       26.3
#      city  order_id  amount
# 1   Delhi         2   900.0
# 2  Mumbai         3   300.0
# 4    Pune         5   640.0
# [3.0, 1.0, 1.0, 2.0, 1.0, 2.0]
# Error: "missing columns: ['tip']"
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (pandas) | JavaScript |
|---------|-----------------|-----------|
| Group and sum | `df.groupby("city")["amount"].sum()` | `reduce` into an object / `Map` |
| Many stats | `.agg(["count", "mean"])` | write each by hand |
| Per-row group value | `.transform("mean")` | two passes over the array |
| Library | pandas (vectorized, C speed) | lodash `_.groupBy` (returns arrays only) |

```python
# Python way
import pandas as pd                                        # pandas
df = pd.DataFrame({"city": ["a", "a", "b"], "x": [1, 2, 3]})   # data
print(df.groupby("city")["x"].sum().to_dict())             # {'a': 3, 'b': 3}
```
```javascript
// JavaScript way
const rows = [{city: "a", x: 1}, {city: "a", x: 2}, {city: "b", x: 3}];   // data
const sums = rows.reduce((acc, r) => {                     // manual accumulation
  acc[r.city] = (acc[r.city] ?? 0) + r.x;                  // add into the bucket
  return acc;                                              // pass the object on
}, {});                                                    // start with {}
console.log(sums);                                         // { a: 3, b: 3 }
```

Key difference: in JavaScript you write the accumulation yourself (or use lodash and then sum each group). In pandas the aggregation is built in, runs vectorized, and returns a table you can sort or merge.

---

## 🟠 FastAPI Connection
Dashboard endpoints often load data with pandas, group it, and return JSON. Convert numpy numbers to plain Python types (`float(v)`), because FastAPI cannot always serialize numpy types. For heavy data, do the grouping in SQL or cache the result; pandas work is CPU-bound, so use a normal `def` endpoint (it runs in a thread pool) instead of `async def`.

```python
# FastAPI example — revenue by city (verified with TestClient)
import pandas as pd                                        # pandas
from fastapi import FastAPI                                # FastAPI

app: FastAPI = FastAPI()                                   # create app
ORDERS: pd.DataFrame = pd.DataFrame(                       # demo data (normally loaded from DB)
    {"city": ["Delhi", "Delhi", "Pune"], "amount": [100.0, 200.0, 300.0]}
)


@app.get("/revenue")                                       # GET /revenue
def revenue() -> dict[str, float]:                         # plain def: CPU-bound work
    s: pd.Series = ORDERS.groupby("city")["amount"].sum()  # group and sum
    return {str(k): float(v) for k, v in s.items()}        # numpy -> plain python

# GET /revenue -> {"Delhi": 300.0, "Pune": 300.0}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting that rows with a NaN key are dropped
✅ Correct: pass `dropna=False` if those rows matter

```python
import pandas as pd
df = pd.DataFrame({"k": ["a", "a", None, "b"], "v": [1, 2, 3, 4]})
# Wrong — the row with key None silently disappears
print(df.groupby("k").v.sum().tolist())               # [3, 4]  (the 3 is lost)
# Right
print(df.groupby("k", dropna=False).v.sum().tolist()) # [3, 4, 3]
```

❌ Mistake 2: Using `apply` with a Python lambda when a built-in aggregation exists
✅ Correct: use `sum`, `mean`, `agg`, `transform` (they are vectorized and much faster)

```python
# Wrong — slow Python function called once per group
# df.groupby("city").apply(lambda g: g["amount"].sum())
# Right — built-in
# df.groupby("city")["amount"].sum()
```

❌ Mistake 3: Expecting `groupby` to return a DataFrame immediately
✅ Correct: it returns a lazy GroupBy object; call an aggregation on it

```python
import pandas as pd
df = pd.DataFrame({"city": ["a", "a", "b"], "x": [1, 2, 3]})
g = df.groupby("city")                                # Wrong to print this: just an object
print(g.x.sum().tolist())                             # Right: [3, 3]
```

❌ Mistake 4: Categorical keys and the `observed` flag
✅ Correct: with categorical columns, set `observed` explicitly (`False` shows empty categories with 0, `True` hides them)

```python
import pandas as pd
df2 = pd.DataFrame({"c": pd.Categorical(["x", "x"], categories=["x", "y"]), "v": [1, 2]})
print(df2.groupby("c", observed=False).v.sum().to_dict())   # {'x': 3, 'y': 0}
print(df2.groupby("c", observed=True).v.sum().to_dict())    # {'x': 3}
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import pandas as pd
df = pd.DataFrame({"k": ["a", "a", "b"], "v": [1.0, None, 4.0]})
print(df.groupby("k").size().tolist())
print(df.groupby("k")["v"].count().tolist())
print(df.groupby("k")["v"].mean().tolist())
```
Answer: `[2, 1]`, `[1, 1]`, `[1.0, 4.0]`. `size()` counts ALL rows in the group, including NaN, so group "a" has 2. `count()` counts only non-null values, so "a" has 1. `mean()` skips NaN, so the mean of `[1.0, NaN]` is 1.0, not 0.5. This difference is a classic bug source in reports.

---

## ⚫ Interview Questions + Answers

Q1: What is the split-apply-combine pattern?
A1: `groupby` splits data by key, applies a function to each group, and combines the outputs. `agg` shrinks each group to one row, `transform` returns the same shape as the input, `filter` keeps or removes whole groups, and `apply` is the flexible (but slower) catch-all.

Q2: What is the difference between `agg` and `transform`?
A2: `agg` returns one value per group (result has one row per group). `transform` returns one value per original row (result has the same index as the input), so you can add it as a new column, for example the group mean next to each row.

Q3: How do you get several named statistics in one call?
A3: Named aggregation: `df.groupby("city").agg(orders=("order_id", "count"), revenue=("amount", "sum"))`. It gives clean column names with no MultiIndex columns.

Q4: How do you get the top N rows per group?
A4: Sort first, then `groupby(...).head(n)`; or use `groupby(...).nlargest`; or `rank()` inside each group and filter on the rank.

Q5: `size()` vs `count()`?
A5: `size()` counts rows including NaN and returns a Series; `count()` counts non-null values per column and returns a DataFrame (or Series for one column).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need per-category totals, averages, counts
- You need to add group-level features to every row (`transform`)
- Data fits in memory (up to a few million rows)

❌ Avoid when:
- Data is huge and already in a database: do `GROUP BY` in SQL
- You only need a simple count of one column: `value_counts()` is shorter
- You use `apply` with a lambda on big data: look for a built-in

---

## 📊 Visual Diagram
```
 city    amount
 Delhi     100  ─┐
 Delhi     200  ─┴─> group "Delhi"  ─> sum = 300  ─┐
 Mumbai    150  ─┐                                  │
 Mumbai     50  ─┴─> group "Mumbai" ─> sum = 200  ─┼─> combined result
 Pune      300  ───> group "Pune"   ─> sum = 300  ─┘

   SPLIT            APPLY                COMBINE
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| groupby | Split rows into groups by key | Key से rows को groups में बांटना |
| agg | Reduce each group to one row | हर group को एक row में बदलना |
| transform | Per-row result using group stats | Group के stats से हर row का result |
| filter | Keep or drop whole groups | पूरे group को रखना या हटाना |
| Named aggregation | `new=(col, func)` syntax | नाम वाला aggregation |
| as_index | Keep keys as index or columns | Keys को index या column रखना |

---

## ⚡ 3-Line Summary
English: `groupby` splits, applies, and combines, like SQL `GROUP BY`. Use `agg` for one row per group, `transform` for per-row group values, and `filter` for whole groups. Watch out for NaN keys, `size` vs `count`, and categorical `observed`.
Hindi: `groupby` data को split, apply और combine करता है, SQL के `GROUP BY` की तरह। हर group की एक row के लिए `agg`, हर row पर group का value देने के लिए `transform`, और पूरे group रखने/हटाने के लिए `filter` इस्तेमाल करें। NaN keys, `size` बनाम `count`, और categorical `observed` से सावधान रहें।

---

## ➡️ Next Topic
**381. Pandas Merge + Join** — combine two tables on a key, like SQL JOIN: inner, left, right, outer, and the traps of duplicate keys.
