---

# 379. Pandas Operations
# हिंदी में: Pandas Operations (Filter, Sort, Group, Merge, Pivot)

---

## 🔵 Simple Definition (English)
Pandas operations are the everyday tools to reshape data: filter rows, sort, group and aggregate, merge tables, add computed columns and pivot. Each returns a new object, so you can chain them into a readable pipeline.

## 🔵 सरल परिभाषा (Hindi)
Pandas operations वे रोज़ के tools हैं जिनसे data का आकार बदला जाता है: rows filter करना, sort करना, group और aggregate करना, tables merge करना, computed columns जोड़ना और pivot करना। हर operation नया object लौटाता है, इसलिए इन्हें chain करके पढ़ने लायक pipeline बना सकते हैं।

---

## 🔴 Problem it Solves
Real data is never in the shape you need. Reports need totals per city, joins need users matched with orders, and dashboards need a pivot table. Writing this with loops and dicts is long and slow. Pandas operations express each step in one line and run in optimised C, and chaining them keeps the transformation readable and testable.

## 🔴 यह क्यों बना? (Hindi)
Real data कभी उस shape में नहीं मिलता जो चाहिए। Reports को city-wise totals चाहिए, joins में users को orders से मिलाना होता है, dashboards को pivot table चाहिए। यह सब loops और dicts से लिखना लंबा और धीमा है। Pandas operations हर step एक line में लिखते हैं और optimised C में चलते हैं, और chaining से transformation पढ़ने और test करने लायक रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Filter:     df[(cond1) & (cond2)]        boolean mask, brackets + & |
Step 2 → Sort:       df.sort_values(["a","b"], ascending=[True, False])
Step 3 → Group:      df.groupby("city").agg(total=("amount","sum"))
Step 4 → Merge:      left.merge(right, on="key", how="left", validate="many_to_one")
Step 5 → New column: df.assign(x=lambda d: d.a * 2)   or np.where / np.select
Step 6 → Reshape:    pivot_table(index=, columns=, values=, aggfunc=)
Step 7 → Chain them; none of these change the original frame
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Filter:     df[(cond1) & (cond2)]        boolean mask, brackets + & |
Step 2 → Sort:       df.sort_values(["a","b"], ascending=[True, False])
Step 3 → Group:      df.groupby("city").agg(total=("amount","sum"))
Step 4 → Merge:      left.merge(right, on="key", how="left", validate="many_to_one")
Step 5 → नया column: df.assign(x=lambda d: d.a * 2)   या np.where / np.select
Step 6 → Reshape:    pivot_table(index=, columns=, values=, aggfunc=)
Step 7 → इन्हें chain करो; इनमें से कोई भी original frame नहीं बदलता
```

---

## 🟡 Real World Example
A Swiggy finance report: join orders with restaurants (`merge`), keep delivered orders (`filter`), group by restaurant and week (`groupby`), sort by revenue, and pivot weeks into columns. A Razorpay reconciliation merges payments with bank files using `how='outer'` and flags the rows where one side is missing. An ML pipeline uses `np.select` to turn a numeric score into 'gold/silver/bronze' tiers.

## 🟡 Real Example Hindi mein
Swiggy की finance report: orders को restaurants से join करो (`merge`), delivered orders रखो (`filter`), restaurant और week से group करो (`groupby`), revenue से sort करो, और weeks को columns में pivot करो। Razorpay की reconciliation payments को bank files से `how='outer'` से merge करती है और जहां एक तरफ नहीं है वे rows flag करती है। ML pipeline `np.select` से numeric score को 'gold/silver/bronze' tiers में बदलती है।

---

## 💻 Code Example — Basic
```python
# Basic pandas operations: filter, sort, groupby, merge, apply, pivot
import pandas as pd                               # import pandas

orders: pd.DataFrame = pd.DataFrame({
    "order_id": [1, 2, 3, 4],                     # order ids
    "user_id": [10, 11, 10, 12],                  # who ordered
    "amount": [250.0, 120.0, 80.0, 300.0],        # order value
    "city": ["Delhi", "Pune", "Delhi", "Pune"],   # delivery city
})                                                # orders table
users: pd.DataFrame = pd.DataFrame({
    "user_id": [10, 11, 13],                      # user 12 missing on purpose
    "name": ["Asha", "Ravi", "Meera"],            # names
})                                                # users table

print(orders[(orders["amount"] > 100) & (orders["city"] == "Pune")]["order_id"].tolist())   # & not 'and'
print(orders.sort_values("amount", ascending=False)["order_id"].tolist())   # sort by amount
print(orders.groupby("city")["amount"].agg(["sum", "mean"]).round(1).to_dict("index"))   # per-city stats
merged: pd.DataFrame = orders.merge(users, on="user_id", how="left")   # keep every order
print(merged[["order_id", "name"]].fillna("unknown").values.tolist())   # missing user -> unknown
orders["band"] = orders["amount"].apply(lambda x: "big" if x >= 200 else "small")   # row-wise function
print(orders["band"].tolist())                    # bands
pv = orders.pivot_table(index="city", columns="band", values="amount", aggfunc="sum", fill_value=0)   # cross-tab
print(pv.to_dict("index"))                        # pivot as dict
print(orders["amount"].cumsum().tolist())         # running total

# Output:
# [2, 4]
# [4, 1, 2, 3]
# {'Delhi': {'sum': 330.0, 'mean': 165.0}, 'Pune': {'sum': 420.0, 'mean': 210.0}}
# [[1, 'Asha'], [2, 'Ravi'], [3, 'Asha'], [4, 'unknown']]
# ['big', 'small', 'small', 'big']
# {'Delhi': {'big': 250.0, 'small': 80.0}, 'Pune': {'big': 300.0, 'small': 120.0}}
# [250.0, 370.0, 450.0, 750.0]
```

## 💻 Code Example — Advanced
```python
# Production style: chainable pipeline, no mutation, vectorised logic, merge validation
import pandas as pd                               # pandas
import numpy as np                                # for np.where / np.select


def enrich(orders: pd.DataFrame, users: pd.DataFrame) -> pd.DataFrame:
    """Join users, add tier and city share. Returns a NEW frame."""
    return (
        orders
        .merge(users, on="user_id", how="left", validate="many_to_one")   # fails if users has duplicate ids
        .assign(
            name=lambda d: d["name"].fillna("unknown"),               # fill missing names
            tier=lambda d: np.select(                                   # vectorised if/elif/else
                [d["amount"] >= 250, d["amount"] >= 100], ["gold", "silver"], default="bronze"
            ),
            city_share=lambda d: (d["amount"] / d.groupby("city")["amount"].transform("sum")).round(3),   # share of city total
        )
        .sort_values(["city", "amount"], ascending=[True, False])      # stable report order
        .reset_index(drop=True)                                         # clean index
    )


orders = pd.DataFrame({"order_id": [1, 2, 3, 4], "user_id": [10, 11, 10, 12],
                       "amount": [250.0, 120.0, 80.0, 300.0], "city": ["Delhi", "Pune", "Delhi", "Pune"]})
users = pd.DataFrame({"user_id": [10, 11], "name": ["Asha", "Ravi"]})
out = enrich(orders, users)                       # run the pipeline
print(out.to_string(index=False))                 # show result
print(orders.columns.tolist())                    # original untouched
dup = pd.DataFrame({"user_id": [10, 10], "name": ["A", "B"]})   # bad lookup table
try:                                              # error handling
    enrich(orders, dup)                           # duplicate keys
except pd.errors.MergeError as e:                 # pandas MergeError
    print("Error:", str(e).splitlines()[0])      # first line of message

# Output (shortened error message):
#  order_id  user_id  amount  city    name   tier  city_share
#         1       10   250.0 Delhi    Asha   gold       0.758
#         3       10    80.0 Delhi    Asha bronze       0.242
#         4       12   300.0  Pune unknown   gold       0.714
#         2       11   120.0  Pune    Ravi silver       0.286
# ['order_id', 'user_id', 'amount', 'city']
# Error: Merge keys are not unique in right dataset; not a many-to-one merge
```



---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (pandas) | JavaScript |
|---------|-----------------|-----------|
| Filter | `df[df.amt > 100]` | `rows.filter(r => r.amt > 100)` |
| Sort | `sort_values("amt")` | `rows.sort((a,b) => a.amt - b.amt)` (mutates!) |
| Group + sum | `groupby("c")["amt"].sum()` | `reduce` into object |
| Join | `a.merge(b, on="id")` | manual lookup `Map` |
| New column | `df["x"] = df.a * 2` | `rows.map(r => ({...r, x: r.a * 2}))` |

```python
# Python way — filter, sort, take 2 in a chain (original untouched)
import pandas as pd                               # pandas
df: pd.DataFrame = pd.DataFrame({"id": [1, 2, 3], "amt": [50, 300, 120]})
print(df[df.amt > 100].sort_values("amt", ascending=False)["id"].tolist())   # [2, 3]
```
```javascript
// JavaScript way — note sort() mutates the array it is called on
const rows = [{id: 1, amt: 50}, {id: 2, amt: 300}, {id: 3, amt: 120}];
console.log(rows.filter(r => r.amt > 100).sort((a, b) => b.amt - a.amt).map(r => r.id));   // [2, 3]
```

Key difference: JS needs a hand-written reduce for group-by and a lookup Map for joins. In pandas these are single calls with validation options (`validate=`), and pandas `sort_values` returns a new frame while JS `sort` changes the original array.

---

## 🟠 FastAPI Connection
A report endpoint filters, groups and returns a small summary, so DataFrames never leave the server. Because pandas is CPU bound, run the work with `run_in_threadpool` (or a plain `def` endpoint). For big or frequent reports, precompute and cache in Redis instead of recomputing per request.

```python
# FastAPI: report endpoint with groupby, run in a thread so the event loop is not blocked
import pandas as pd                               # pandas
from fastapi import FastAPI                       # app
from fastapi.concurrency import run_in_threadpool   # run blocking code off the event loop
from fastapi.testclient import TestClient         # demo client

app: FastAPI = FastAPI()
ORDERS: pd.DataFrame = pd.DataFrame({"city": ["Delhi", "Pune", "Delhi", "Pune"], "amount": [250.0, 120.0, 80.0, 300.0]})


def build_report(min_amount: float) -> list[dict[str, object]]:
    df = ORDERS[ORDERS["amount"] >= min_amount]   # filter
    out = df.groupby("city", as_index=False).agg(total=("amount", "sum"), orders=("amount", "size"))   # aggregate
    return out.sort_values("total", ascending=False).to_dict("records")   # JSON-ready


@app.get("/report")
async def report(min_amount: float = 0) -> list[dict[str, object]]:
    return await run_in_threadpool(build_report, min_amount)   # CPU/pandas work in a worker thread


client = TestClient(app)
print(client.get("/report").json())
print(client.get("/report", params={"min_amount": 100}).json())

# Output:
# [{'city': 'Pune', 'total': 420.0, 'orders': 2}, {'city': 'Delhi', 'total': 330.0, 'orders': 2}]
# [{'city': 'Pune', 'total': 420.0, 'orders': 2}, {'city': 'Delhi', 'total': 250.0, 'orders': 1}]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Chained boolean filters with `and`, or without brackets around conditions
✅ Correct: `&` / `|` with each condition in parentheses (`&` binds tighter than `>`)

```python
import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3]})
# Wrong — df.a>1 & df.a<3 is parsed as df.a > (1 & df.a) < 3 -> ValueError (truth value of a Series is ambiguous)
# Right
print(df[(df.a > 1) & (df.a < 3)]["a"].tolist())   # [2]
```

❌ Mistake 2: Expecting `sort_values` / `drop` to change the frame in place
✅ Correct: assign the result

```python
import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3]})
# Wrong — result thrown away
df.sort_values("a", ascending=False)
print(df["a"].tolist())               # [1, 2, 3]
# Right
df = df.sort_values("a", ascending=False)
print(df["a"].tolist())               # [3, 2, 1]
```

❌ Mistake 3: Merging on a key with duplicates and silently multiplying rows
✅ Correct: pass `validate=` so pandas stops you

```python
import pandas as pd
a = pd.DataFrame({"k": [1, 2]})
b = pd.DataFrame({"k": [2, 2], "v": [10, 20]})   # duplicate key 2
# Wrong — row for k=2 appears twice, totals double
print(len(a.merge(b, on="k")))        # 2
# Right — raises MergeError for the bad lookup table
try:
    a.merge(b, on="k", validate="one_to_one")
except pd.errors.MergeError:
    print("duplicate keys caught")
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import pandas as pd
df = pd.DataFrame({"g": ["a", "a", "b"], "v": [1, 2, 3]})
print(df.groupby("g").sum().columns.tolist())
print(df.groupby("g", as_index=False)["v"].sum().to_dict("list"))
a = pd.DataFrame({"k": [1, 2]}); b = pd.DataFrame({"k": [2, 3]})
print(len(a.merge(b)), len(a.merge(b, how="outer")))
```
Answer: `['v']`, then `{'g': ['a', 'b'], 'v': [3, 3]}`, then `1 3`. `groupby('g')` moves `g` into the index, so it is not a column any more (use `as_index=False` or `reset_index()` to keep it). `merge` defaults to `how='inner'`, so only key 2 survives (1 row); `outer` keeps keys 1, 2, 3 (3 rows). Verified on pandas 3.1.1.

---

## ⚫ Interview Questions + Answers

Q1: `merge` vs `join` vs `concat`?
A1: `merge` joins on column values (SQL-style). `join` is a shortcut that joins on the index. `concat` stacks frames vertically (`axis=0`) or side by side (`axis=1`) with no key matching.

Q2: `apply` vs `map` vs vectorised?
A2: Vectorised column maths is fastest, `map` (dict or function) works per value of one column, `apply(axis=1)` runs a Python function per row and is the slowest. Reach for `np.where`, `np.select` and `.str` first.

Q3: `transform` vs `agg` in groupby?
A3: `agg` reduces each group to one row. `transform` returns a result with the same length as the input (like a window function): for example `amount / groupby('city').amount.transform('sum')` gives each row's share of its city.

Q4: What does `pivot_table` do and how is it different from `groupby`?
A4: It groups by two axes and spreads one of them into columns (cross-tab), with `aggfunc` and `fill_value`. `groupby` gives a long format; pivot gives wide format. `melt` goes back from wide to long.

Q5: Why does a chained assignment on a filtered frame behave oddly?
A5: In pandas < 3 filtering may return a view or a copy, so `df[mask]["x"] = 1` could silently do nothing and raised `SettingWithCopyWarning`. In pandas 3 Copy-on-Write makes it always a copy. Use `df.loc[mask, "x"] = 1` to change the original on purpose.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Reports, aggregations, joins and reshaping of tabular data
- Data preparation before ML or export
- Prototyping logic you may later move to SQL

❌ Avoid when:
- The data already lives in a database - do the filter/group in SQL, pull the result only
- Data is bigger than memory - use chunks, Polars or DuckDB
- You write `apply(axis=1)` over millions of rows - find a vectorised version

---

## 📊 Visual Diagram
```
orders --filter--> paid --groupby city--> totals --sort--> top cities
                     \
users  --merge(on user_id, how=left)--> orders + name (NaN where no user)

pivot_table: rows=city, columns=band, values=sum(amount)
            big   small
   Delhi    250     80
   Pune     300    120
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Boolean mask | True/False per row used to filter | Filter के लिए True/False list |
| groupby | Split rows into groups, then aggregate | Rows को groups में बांटकर aggregate |
| merge | SQL-style join | SQL जैसा join |
| pivot | Turn row values into columns | Row values को columns बनाना |
| transform | Group result broadcast back to rows | Group का result rows पर वापस |
| Method chaining | `df.a().b().c()` pipeline | Methods की श्रृंखला |

---

## ⚡ 3-Line Summary
English: Filter with `&`/`|`, sort, `groupby` + `agg`, `merge` with `validate=`, `assign` for new columns, and `pivot_table` for wide reports. Each returns a new frame, so assign the result. Prefer vectorised logic over `apply`, and let the database do heavy filtering when possible.
Hindi: Filter के लिए `&`/`|`, फिर sort, `groupby` + `agg`, `validate=` के साथ `merge`, नए columns के लिए `assign`, और wide reports के लिए `pivot_table`। हर operation नया frame लौटाता है, इसलिए result को assign करें। `apply` की जगह vectorised logic चुनें, और भारी filtering database से करवाएं।

---

## ➡️ Next Topic
**382. Data Cleaning with Pandas** — dropna, fillna, duplicates, type fixes and validation of messy real-world data.
