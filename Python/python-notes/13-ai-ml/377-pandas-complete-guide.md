---

# 377. Pandas — Complete Guide
# हिंदी में: Pandas — पूरी गाइड (Tabular Data Analysis)

---

## 🔵 Simple Definition (English)
Pandas is the main Python library for working with table-like data (rows and columns), like Excel or a SQL table inside Python. It reads CSV/JSON/SQL, cleans, filters, groups and merges data in a few lines. Built on NumPy.

## 🔵 सरल परिभाषा (Hindi)
Pandas Python की मुख्य library है जो table जैसे data (rows और columns) के साथ काम करती है, जैसे Python के अंदर Excel या SQL table। यह CSV/JSON/SQL पढ़ती है और कुछ ही lines में data को clean, filter, group और merge करती है। यह NumPy पर बनी है।

---

## 🔴 Problem it Solves
Plain Python lists of dicts make analysis painful: you write loops for filtering, a dict of counters for group-by, manual code for missing values and dates, and it is slow for millions of rows. Pandas gives columns with types, built-in handling of missing data (NaN), SQL-like group/join, time-series tools and fast vectorised operations in C.

## 🔴 यह क्यों बना? (Hindi)
Plain Python की list of dicts पर analysis मुश्किल है: filtering के लिए loops, group-by के लिए counters का dict, missing values और dates के लिए manual code, और लाखों rows पर यह धीमा है। Pandas typed columns, missing data (NaN) की built-in handling, SQL जैसा group/join, time-series tools और C में तेज़ vectorised operations देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Load data:        df = pd.read_csv(...)   (also read_json, read_sql, read_parquet)
Step 2 → Inspect:          df.shape, df.dtypes, df.head(), df.isna().sum()
Step 3 → Clean:            dropna / fillna, fix dtypes, strip text, parse dates
Step 4 → Transform:        filter rows, add columns (vectorised, no loops)
Step 5 → Aggregate:        groupby(...).agg(...), pivot_table, merge with other tables
Step 6 → Output:           to_dict("records") for APIs, to_csv / to_parquet / to_sql
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Data load करो:     df = pd.read_csv(...)   (read_json, read_sql, read_parquet भी)
Step 2 → Inspect करो:      df.shape, df.dtypes, df.head(), df.isna().sum()
Step 3 → Clean करो:        dropna / fillna, dtype ठीक करो, text strip करो, dates parse करो
Step 4 → Transform करो:    rows filter करो, columns जोड़ो (vectorised, बिना loops)
Step 5 → Aggregate करो:    groupby(...).agg(...), pivot_table, दूसरी tables से merge
Step 6 → Output:           APIs के लिए to_dict("records"), to_csv / to_parquet / to_sql
```

---

## 🟡 Real World Example
A Zomato analytics job loads yesterday's orders CSV (2 million rows), drops cancelled orders, groups by city and hour, and finds peak demand. A Razorpay ops team reconciles bank settlement files against their payments table with a pandas merge. An AI team uses pandas to clean a training dataset (remove duplicates, fix nulls) before feeding it to a model.

## 🟡 Real Example Hindi mein
Zomato का analytics job कल की orders CSV (20 लाख rows) load करता है, cancelled orders हटाता है, city और hour से group करके peak demand निकालता है। Razorpay की ops team bank settlement files को अपनी payments table से pandas merge करके reconcile करती है। AI team model को देने से पहले training dataset pandas से clean करती है (duplicates हटाना, nulls ठीक करना)।

---

## 💻 Code Example — Basic
```python
# Basic pandas workflow: load, inspect, filter, group
import io                                         # fake file in memory
import pandas as pd                               # import pandas

csv_text: str = """order_id,city,amount,status
1,Delhi,250.5,paid
2,Mumbai,120.0,paid
3,Delhi,80.0,failed
4,Pune,300.0,paid
5,Mumbai,,paid
"""                                               # small CSV as a string
df: pd.DataFrame = pd.read_csv(io.StringIO(csv_text))   # read like a file
print(df.shape)                                   # (rows, columns)
print({c: str(t) for c, t in df.dtypes.items()})   # type of each column (as text)
print(df["amount"].isna().sum())                  # count missing amounts
paid: pd.DataFrame = df[df["status"] == "paid"]   # boolean filter
print(paid["amount"].sum())                       # NaN skipped by default
print(df.groupby("city")["amount"].sum().to_dict())   # total per city
print(df.sort_values("amount", ascending=False).head(2)["order_id"].tolist())   # top 2 orders

# Output:
# (5, 4)
# {'order_id': 'int64', 'city': 'str', 'amount': 'float64', 'status': 'str'}
# 1
# 670.5
# {'Delhi': 330.5, 'Mumbai': 120.0, 'Pune': 300.0}
# [4, 1]
```

## 💻 Code Example — Advanced
```python
# Production style: typed ETL function with validation, cleaning, aggregation
import io                                         # in-memory file
import pandas as pd                               # pandas

REQUIRED: set[str] = {"order_id", "city", "amount", "status", "created_at"}   # must-have columns


def load_orders(source: io.StringIO) -> pd.DataFrame:
    """Read, validate and clean the orders file."""
    df: pd.DataFrame = pd.read_csv(source)        # read raw text first
    missing: set[str] = REQUIRED - set(df.columns)     # which columns are absent
    if missing:                                   # fail early with a clear message
        raise ValueError(f"missing columns: {sorted(missing)}")
    df = df.dropna(subset=["amount"])             # drop rows without an amount
    df = df.assign(created_at=pd.to_datetime(df["created_at"]))   # parse dates after validation
    df = df.assign(city=df["city"].str.strip().str.title())   # normalise city text
    return df                                     # cleaned frame


def daily_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue and order count per day for paid orders."""
    paid: pd.DataFrame = df.loc[df["status"] == "paid"]    # only paid
    out: pd.DataFrame = (
        paid.groupby(paid["created_at"].dt.date)  # group by calendar day
        .agg(revenue=("amount", "sum"), orders=("order_id", "count"))   # named aggregation
        .reset_index()                            # day back to a column
    )
    return out                                    # summary table


raw: str = """order_id,city,amount,status,created_at
1, delhi ,250.5,paid,2026-01-01 10:00
2,MUMBAI,120.0,paid,2026-01-01 12:30
3,delhi,80.0,failed,2026-01-02 09:00
4,pune,300.0,paid,2026-01-02 18:45
5,mumbai,,paid,2026-01-02 19:00
"""                                               # sample data
orders = load_orders(io.StringIO(raw))            # load
print(orders["city"].tolist())                    # cleaned cities
print(daily_revenue(orders).to_string(index=False))   # revenue per day
try:                                              # error handling
    load_orders(io.StringIO("order_id,city\n1,Delhi\n"))   # bad file
except ValueError as e:                           # catch
    print("Error:", e)                            # message

# Output (the last line is the validation error):
# ['Delhi', 'Mumbai', 'Delhi', 'Pune']
# created_at  revenue  orders
# 2026-01-01    370.5       2
# 2026-01-02    300.0       1
# Error: missing columns: ['amount', 'created_at', 'status']
```



---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (pandas) | JavaScript |
|---------|-----------------|-----------|
| Table type | `DataFrame` | array of objects (or Danfo.js / Arquero) |
| Filter rows | `df[df.age > 18]` | `rows.filter(r => r.age > 18)` |
| Group by | `df.groupby("city")["amt"].sum()` | `reduce` into an object |
| Missing values | `NaN`, `isna()`, `fillna()` | `null`/`undefined` checks by hand |
| Read CSV | `pd.read_csv(path)` | `papaparse` / `csv-parse` package |

```python
# Python way — total amount per city
import pandas as pd                               # pandas
df: pd.DataFrame = pd.DataFrame({"city": ["Delhi", "Pune", "Delhi"], "amt": [10, 20, 30]})
print(df.groupby("city")["amt"].sum().to_dict())  # {'Delhi': 40, 'Pune': 20}
```
```javascript
// JavaScript way — manual reduce
const rows = [{city: "Delhi", amt: 10}, {city: "Pune", amt: 20}, {city: "Delhi", amt: 30}];
const total = rows.reduce((acc, r) => { acc[r.city] = (acc[r.city] ?? 0) + r.amt; return acc; }, {});
console.log(total);   // { Delhi: 40, Pune: 20 }
```

Key difference: JS has no built-in table type, so you hand-write reduce/filter code. Pandas columns are typed and vectorised, and it knows about missing data and dates. Pandas needs the whole dataset in memory, unlike streaming JS code.

---

## 🟠 FastAPI Connection
FastAPI often sits in front of pandas for reporting endpoints, CSV upload and ML preprocessing. Important rules: (1) pandas is blocking CPU work, so use a plain `def` endpoint or `run_in_threadpool`; (2) NaN and numpy types are not valid JSON, so convert with `to_dict('records')` after replacing NaN with None; (3) validate columns of uploaded files and return 4xx, not 500.

```python
# FastAPI: upload a CSV, summarise it with pandas
import io                                         # in-memory bytes
import pandas as pd                               # pandas
from fastapi import FastAPI, File, HTTPException, UploadFile   # web pieces
from fastapi.testclient import TestClient         # demo client

app: FastAPI = FastAPI()                          # app


@app.post("/summary")
async def summary(file: UploadFile = File(...)) -> dict[str, object]:
    raw: bytes = await file.read()                # read upload (async)
    try:
        df: pd.DataFrame = pd.read_csv(io.BytesIO(raw))   # parse CSV
    except Exception as e:                        # bad file
        raise HTTPException(400, f"cannot parse CSV: {type(e).__name__}")
    if "amount" not in df.columns:                # validate schema
        raise HTTPException(422, "column 'amount' required")
    return {"rows": len(df), "total": float(df["amount"].sum()), "missing": int(df["amount"].isna().sum())}


client = TestClient(app)
files = {"file": ("o.csv", b"amount\n10\n20.5\n\n", "text/csv")}
print(client.post("/summary", files=files).json())
print(client.post("/summary", files={"file": ("o.csv", b"x\n1\n", "text/csv")}).status_code)

# Output:
# {'rows': 2, 'total': 30.5, 'missing': 0}
# 422
# (needs: pip install python-multipart for UploadFile)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Looping over rows with `iterrows()` or `apply` when a vectorised form exists
✅ Correct: use column operations

```python
import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3]})
# Wrong — slow Python loop (100x slower on big data)
df["b"] = [row["a"] * 2 for _, row in df.iterrows()]
# Right — vectorised
df["b"] = df["a"] * 2
print(df["b"].tolist())               # [2, 4, 6]
```

❌ Mistake 2: Using `and` / `or` instead of `&` / `|` in filters
✅ Correct: use `&`, `|` and wrap each condition in brackets

```python
import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3], "b": [3, 2, 1]})
# Wrong — ValueError: The truth value of a Series is ambiguous
# df[df.a > 1 and df.b > 1]
# Right
print(df[(df.a > 1) & (df.b > 1)]["a"].tolist())   # [2]
```

❌ Mistake 3: Believing NaN equals NaN, or forgetting missing values exist
✅ Correct: use `isna()`, `dropna()` or `fillna()`

```python
import pandas as pd
s = pd.Series([1.0, None, 3.0])
# Wrong — NaN == NaN is False, so this never finds the missing one
print((s == float("nan")).sum())      # 0
# Right
print(s.isna().sum())                 # 1
```

---

## 🧠 Tricky Interview Question

```python
# What will this output? (pandas 3.x)
import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
sub = df[df["a"] > 1]
sub["b"] = 0
print(df["b"].tolist(), sub["b"].tolist())
df2 = pd.DataFrame({"a": [1, 2, None]})
print((df2["a"] == df2["a"]).tolist(), df2.dropna().shape)
```
Answer: `[4, 5, 6] [0, 0]` then `[True, True, False] (2, 1)`. In pandas 3 (Copy-on-Write is always on) changing `sub` NEVER changes `df`, and there is no `SettingWithCopyWarning` any more. In pandas 1.x/2.x this was a confusing warning and sometimes modified the original. Second part: the NaN row compares unequal even to itself (`False`), and `dropna()` leaves 2 rows. Verified on pandas 3.1.1. Version note: pandas 3 also makes text columns the new `str` dtype instead of `object`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `loc` and `iloc`?
A1: `loc` is label-based (index labels, inclusive end in slices); `iloc` is position-based (0..n-1, exclusive end). After filtering, labels and positions differ, which is the usual source of bugs.

Q2: How do you handle missing data?
A2: Detect with `isna()`, remove with `dropna(subset=[...])`, or fill with `fillna(value)`/forward-fill. Decide per column: drop a row if the key is missing, fill a numeric measure with median, keep NaN if the model handles it.

Q3: How do merges work and what are the join types?
A3: `df.merge(other, on="key", how=...)`: `inner` (only matching), `left` (all left rows), `right`, `outer` (everything). Use `validate="many_to_one"` to catch accidental duplicate keys that would multiply rows.

Q4: How do you work with a file bigger than RAM?
A4: Read in chunks (`read_csv(chunksize=...)`), choose smaller dtypes (`category`, `int32`), read only needed columns (`usecols`), or switch to Parquet, Polars or DuckDB.

Q5: Why is `apply(axis=1)` slow?
A5: It calls a Python function per row, so there is no vectorisation. Prefer column maths, `np.where`/`np.select`, string accessors `.str`, or `map` with a dict.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Analysing, cleaning and reporting on tabular data up to a few GB
- CSV/Excel/SQL import and export, quick ETL
- Feature preparation before ML

❌ Avoid when:
- Simple row-by-row API logic with a handful of rows (plain Python is clearer)
- Data far larger than RAM - use Spark, Polars, DuckDB
- Real-time per-request hot paths where DataFrame overhead (ms) matters

---

## 📊 Visual Diagram
```
CSV / SQL / JSON
      |
      v
 +-----------+   filter   +-----------+  groupby/agg  +----------+
 | DataFrame | ---------> | DataFrame | ------------> | Summary  |
 | (columns  |  assign    | cleaned   |   merge       | to API / |
 |  + index) |  dropna    |           |               | CSV / DB |
 +-----------+            +-----------+               +----------+
 Each column = a typed Series (NumPy array under the hood)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| DataFrame | 2-D table with labelled columns | Labelled columns वाली 2-D table |
| Series | One column | एक column |
| Index | Row labels | Rows के labels |
| NaN | Missing value marker | Missing value का निशान |
| groupby | Split-apply-combine | बांटो, लागू करो, जोड़ो |
| Vectorised | Whole-column operation | पूरे column पर एक साथ operation |

---

## ⚡ 3-Line Summary
English: Pandas gives you typed tables (DataFrames) with fast vectorised filtering, cleaning, grouping and merging. Validate columns, handle NaN, avoid row loops, and convert to plain dicts before returning JSON. Use plain `def` or a thread pool in FastAPI because pandas blocks.
Hindi: Pandas आपको typed tables (DataFrames) देता है जिनमें तेज़ vectorised filtering, cleaning, grouping और merging होती है। Columns validate करें, NaN संभालें, row loops से बचें, और JSON लौटाने से पहले plain dicts में बदलें। FastAPI में plain `def` या thread pool इस्तेमाल करें क्योंकि pandas blocking है।

---

## ➡️ Next Topic
**378. DataFrame + Series** — the two core objects: construction, indexing with loc/iloc, alignment and dtypes.
