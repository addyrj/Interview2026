---

# 381. Pandas Merge + Join
# हिंदी में: Pandas Merge + Join (दो tables को key से जोड़ना)

---

## 🔵 Simple Definition (English)
`merge` combines two DataFrames by matching values in key columns, exactly like SQL `JOIN`. `join` is a shortcut that matches on the index. `concat` is different: it just stacks tables on top of each other or side by side.

## 🔵 सरल परिभाषा (Hindi)
`merge` दो DataFrames को key columns के matching values से जोड़ता है, बिल्कुल SQL `JOIN` की तरह। `join` उसका shortcut है जो index पर match करता है। `concat` अलग चीज है: वह tables को ऊपर-नीचे या बगल-बगल रख देता है।

---

## 🔴 Problem it Solves
Real data lives in many tables: orders in one, users in another, cities in a third. To answer "which city's users spend the most" you must combine them. Doing this with nested loops is slow and bug-prone. `merge` does a hash join in optimized code and handles missing matches (inner, left, right, outer).

## 🔴 यह क्यों बना? (Hindi)
Real data कई tables में होता है: orders एक में, users दूसरे में, cities तीसरे में। "किस शहर के users सबसे ज्यादा खर्च करते हैं" जानने के लिए इन्हें जोड़ना पड़ता है। Nested loops से यह धीमा और bug वाला होता है। `merge` optimized code में hash join करता है और match न मिलने की स्थिति (inner, left, right, outer) भी संभालता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose the key column(s) present in both tables (on="user_id")
Step 2 → pandas builds a hash table of the keys of one side
Step 3 → For each row of the other side it looks up matching rows
Step 4 → how= decides what happens to rows without a match:
         inner = drop them, left = keep left rows, right = keep right rows, outer = keep all
Step 5 → If a key appears many times on both sides, rows MULTIPLY (cartesian per key)
Step 6 → Same non-key column names get suffixes _x and _y (or your suffixes=)

orders(user_id: 10,11,99) + users(user_id: 10,11,12)
 inner -> 10, 11 | left -> 10, 11, 99 | outer -> 10, 11, 12, 99
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → दोनों tables में मौजूद key column(s) चुनें (on="user_id")
Step 2 → pandas एक तरफ की keys की hash table बनाता है
Step 3 → दूसरी तरफ की हर row के लिए matching rows ढूंढता है
Step 4 → how= तय करता है कि match न मिलने वाली rows का क्या होगा:
         inner = हटा दो, left = left की rows रखो, right = right की रखो, outer = सब रखो
Step 5 → अगर key दोनों तरफ कई बार आती है, तो rows MULTIPLY हो जाती हैं
Step 6 → एक जैसे non-key column names पर suffix _x और _y लगता है (या आपका suffixes=)
```

---

## 🟡 Real World Example
Swiggy has an `orders` table with `restaurant_id` and a `restaurants` table with name and city. A nightly job left-joins orders with restaurants, then with a `cities` table, to produce a report. Razorpay joins `payments` with `merchants` on `merchant_id`. A FastAPI endpoint joins in-memory frames to return a user's orders with the user name.

## 🟡 Real Example Hindi mein
Swiggy के पास `orders` table है जिसमें `restaurant_id` है, और `restaurants` table है जिसमें नाम और शहर है। रात की job orders को restaurants से left-join करती है, फिर `cities` से, और report बनाती है। Razorpay `payments` को `merchants` से `merchant_id` पर join करता है। FastAPI endpoint memory के frames join करके user का नाम और उसके orders लौटाता है।

---

## 💻 Code Example — Basic
```python
# Basic merge / join / concat (pandas 3.x)
import pandas as pd                                   # import pandas

orders: pd.DataFrame = pd.DataFrame({                 # orders table
    "order_id": [1, 2, 3, 4],                         # unique order ids
    "user_id": [10, 11, 10, 99],                      # 99 has no user row
    "amount": [250, 400, 120, 90],                    # money
})
users: pd.DataFrame = pd.DataFrame({                  # users table
    "user_id": [10, 11, 12],                          # 12 has no orders
    "name": ["Asha", "Ravi", "Meena"],                # names
})
print(orders.merge(users, on="user_id", how="inner"))             # only matching rows
print(orders.merge(users, on="user_id", how="left"))              # keep all orders
print(orders.merge(users, on="user_id", how="outer", indicator=True))   # all rows + source flag
a: pd.DataFrame = orders.set_index("order_id")        # index = order_id
b: pd.DataFrame = pd.DataFrame({"status": ["paid", "paid", "failed"]}, index=[1, 2, 3])   # same index
print(a.join(b))                                      # join on index, left join by default
print(pd.concat([users, users.iloc[:1]], ignore_index=True))      # stack rows vertically

# Output:
#    order_id  user_id  amount  name
# 0         1       10     250  Asha
# 1         2       11     400  Ravi
# 2         3       10     120  Asha
#    order_id  user_id  amount  name
# 0         1       10     250  Asha
# 1         2       11     400  Ravi
# 2         3       10     120  Asha
# 3         4       99      90   NaN
#    order_id  user_id  amount   name      _merge
# 0       1.0       10   250.0   Asha        both
# 1       3.0       10   120.0   Asha        both
# 2       2.0       11   400.0   Ravi        both
# 3       NaN       12     NaN  Meena  right_only
# 4       4.0       99    90.0    NaN   left_only
#           user_id  amount  status
# order_id
# 1              10     250    paid
# 2              11     400    paid
# 3              10     120  failed
# 4              99      90     NaN
#    user_id   name
# 0       10   Asha
# 1       11   Ravi
# 2       12  Meena
# 3       10   Asha
```

## 💻 Code Example — Advanced
```python
# Production style: safe enrichment with validate=, duplicate checks and row-count guard
from __future__ import annotations                    # modern type hints
import pandas as pd                                   # pandas


def enrich_orders(orders: pd.DataFrame, users: pd.DataFrame, cities: pd.DataFrame) -> pd.DataFrame:
    """Left-join orders with users and cities without changing the row count."""
    for name, frame, key in (("users", users, "user_id"), ("cities", cities, "city_id")):   # lookup tables
        if frame[key].duplicated().any():             # duplicate keys would multiply rows
            raise ValueError(f"{name}.{key} has duplicates: join would multiply rows")
    out: pd.DataFrame = (
        orders.merge(users, on="user_id", how="left", validate="many_to_one")   # pandas also checks
        .merge(cities, left_on="home_city", right_on="city_id", how="left",
               validate="many_to_one", suffixes=("", "_city"))   # different key names on each side
        .drop(columns=["city_id"])                    # drop the duplicate key column
    )
    if len(out) != len(orders):                       # safety net: a left join must keep rows
        raise RuntimeError("row count changed after merge")
    return out                                        # enriched table


orders = pd.DataFrame({"order_id": [1, 2, 3], "user_id": [10, 11, 77], "amount": [250.0, 400.0, 90.0]})
users = pd.DataFrame({"user_id": [10, 11], "name": ["Asha", "Ravi"], "home_city": [1, 2]})
cities = pd.DataFrame({"city_id": [1, 2], "city_name": ["Delhi", "Pune"]})
res: pd.DataFrame = enrich_orders(orders, users, cities)      # run the join
print(res.to_string(index=False))                     # show the result
print("unmatched users:", res[res["name"].isna()]["order_id"].tolist())   # orders with no user
dup: pd.DataFrame = pd.concat([users, users.iloc[[0]]], ignore_index=True)   # user 10 twice
try:                                                  # our own guard
    enrich_orders(orders, dup, cities)                # should refuse
except ValueError as e:                               # catch it
    print("Error:", e)                                # clear message
try:                                                  # pandas built-in guard
    orders.merge(dup, on="user_id", validate="many_to_one")   # validate raises on duplicate right keys
except pd.errors.MergeError as e:                     # catch MergeError
    print("MergeError:", str(e)[:60])                 # first 60 chars of the message

# Output:
#  order_id  user_id  amount name  home_city city_name
#         1       10   250.0 Asha        1.0     Delhi
#         2       11   400.0 Ravi        2.0      Pune
#         3       77    90.0  NaN        NaN       NaN
# unmatched users: [3]
# Error: users.user_id has duplicates: join would multiply rows
# MergeError: Merge keys are not unique in right dataset; not a many-to-on
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (pandas) | JavaScript |
|---------|-----------------|-----------|
| Inner join | `a.merge(b, on="k")` | `a.filter(...).map(x => ({...x, ...find}))` |
| Left join | `how="left"` | `a.map(x => ({...x, ...lookup.get(x.k)}))` |
| Many-to-one check | `validate="many_to_one"` | write your own |
| Stack tables | `pd.concat` | `[...a, ...b]` |

```python
# Python way
import pandas as pd                                        # pandas
o = pd.DataFrame({"uid": [1, 2], "amt": [5, 6]})           # orders
u = pd.DataFrame({"uid": [1, 2], "name": ["A", "B"]})      # users
print(o.merge(u, on="uid").to_dict("records"))             # joined records
```
```javascript
// JavaScript way
const o = [{uid: 1, amt: 5}, {uid: 2, amt: 6}];            // orders
const u = new Map([[1, {name: "A"}], [2, {name: "B"}]]);   // lookup map by key
const joined = o.map(x => ({...x, ...u.get(x.uid)}));      // manual left join
console.log(joined);                                       // [{uid:1,amt:5,name:"A"}, ...]
```

Key difference: in JavaScript you build a `Map` and spread objects by hand, and you must decide yourself what to do on missing keys. pandas gives all four join types and can validate key uniqueness.

---

## 🟠 FastAPI Connection
Enrichment endpoints often join an orders frame with a users frame and return records. Use `to_dict(orient="records")` to get JSON-friendly output. Keep lookup tables (`users`) cached in memory, not reloaded per request. In big systems, prefer a SQL JOIN in the database.

```python
# FastAPI example — user's orders with name (verified with TestClient)
import pandas as pd                                        # pandas
from fastapi import FastAPI                                # FastAPI

app: FastAPI = FastAPI()                                   # create app
U: pd.DataFrame = pd.DataFrame({"user_id": [1, 2], "name": ["Asha", "Ravi"]})   # users
O: pd.DataFrame = pd.DataFrame({"user_id": [1, 1, 2], "amount": [10.0, 20.0, 5.0]})   # orders


@app.get("/users/{uid}/orders")                            # GET /users/1/orders
def user_orders(uid: int) -> list[dict[str, object]]:      # sync def: CPU work
    m: pd.DataFrame = O.merge(U, on="user_id", how="left")     # attach the name
    return m[m["user_id"] == uid].to_dict(orient="records")    # JSON-friendly list

# GET /users/1/orders ->
# [{'user_id': 1, 'amount': 10.0, 'name': 'Asha'}, {'user_id': 1, 'amount': 20.0, 'name': 'Asha'}]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Duplicate keys silently multiply rows
✅ Correct: use `validate="many_to_one"` or de-duplicate first

```python
import pandas as pd
l = pd.DataFrame({"k": [1, 1, 2], "a": ["x", "y", "z"]})
r = pd.DataFrame({"k": [1, 1, 3], "b": ["p", "q", "r"]})
# Wrong — key 1 has 2 rows on each side -> 2 x 2 = 4 rows
print(len(l.merge(r, on="k")))                        # 4
# Right — a validate= argument would raise MergeError here
```

❌ Mistake 2: Merging on keys with different dtypes (int vs str)
✅ Correct: cast to the same type first

```python
import pandas as pd
l3 = pd.DataFrame({"k": [1, 2]}); r3 = pd.DataFrame({"k": ["1", "2"]})
# Wrong — raises ValueError: You are trying to merge on int64 and str columns for key 'k'...
# l3.merge(r3, on="k")
# Right
r3["k"] = r3["k"].astype(int)                         # same dtype
print(len(l3.merge(r3, on="k")))                      # 2
```

❌ Mistake 3: Unexpected `_x` / `_y` columns
✅ Correct: pass `suffixes=` or rename columns before merging

```python
import pandas as pd
l2 = pd.DataFrame({"id": [1, 2], "v": [1, 2]}); r2 = pd.DataFrame({"id": [1, 2], "v": [10, 20]})
print(l2.merge(r2, on="id").columns.tolist())                         # ['id', 'v_x', 'v_y']
print(l2.merge(r2, on="id", suffixes=("_old", "_new")).columns.tolist())   # ['id', 'v_old', 'v_new']
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import pandas as pd
l = pd.DataFrame({"k": [1, 1, 2], "a": ["x", "y", "z"]})
r = pd.DataFrame({"k": [1, 1, 3], "b": ["p", "q", "r"]})
print(len(l.merge(r, on="k")))
print(len(l.merge(r, on="k", how="left")))
print(len(l.merge(r, on="k", how="outer")))
```
Answer: `4`, `5`, `6`. Inner: key 1 appears twice on each side, so 2 x 2 = 4 rows; keys 2 and 3 have no match. Left: those 4 plus the unmatched left row with k=2, so 5. Outer: 4 plus unmatched k=2 (left) and k=3 (right), so 6. Joins on non-unique keys produce a cartesian product per key.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `merge`, `join` and `concat`?
A1: `merge` joins on column values (like SQL), `join` is a shortcut for joining on the index (left join by default), and `concat` stacks frames along an axis without matching keys.

Q2: How do you find rows that failed to match?
A2: Use `indicator=True` and filter `_merge == "left_only"`, or do a left join and check for NaN in the right-side columns.

Q3: What does `validate` do?
A3: It checks the key relationship (`one_to_one`, `one_to_many`, `many_to_one`, `many_to_many`) and raises `MergeError` if violated. It protects against silent row explosion.

Q4: Why does my row count grow after a left join?
A4: The right table has duplicate keys. Each left row is repeated for every matching right row. De-duplicate the right side or validate.

Q5: How to merge when the key columns have different names?
A5: `left_on="home_city", right_on="city_id"`, then drop the extra key column.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Enriching fact tables with lookup (dimension) tables
- Combining data from CSV, API and DB sources in memory
- Finding unmatched records (anti-joins)

❌ Avoid when:
- Both tables are in a database: do the JOIN in SQL
- Data is too big for memory: use Dask, Polars, or the DB
- You only need to stack rows: use `concat`

---

## 📊 Visual Diagram
```
 orders.user_id: 10  11  99          users.user_id: 10  11  12

 inner : 10 11               (in both)
 left  : 10 11 99            (all orders)
 right : 10 11 12            (all users)
 outer : 10 11 12 99         (everything)

 Venn:   [ orders  ( 10 11 ) users ]
            99         12
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| merge | SQL-style join on columns | Columns पर SQL जैसा join |
| join | Join on index | Index पर join |
| how | Join type: inner/left/right/outer | Join का प्रकार |
| validate | Check key relationship | Key के संबंध की जांच |
| suffixes | Names added to clashing columns | टकराने वाले columns के suffix |
| indicator | Column showing row source | Row कहां से आई बताने वाला column |

---

## ⚡ 3-Line Summary
English: `merge` joins tables on keys with inner, left, right or outer logic. Duplicate keys multiply rows, so use `validate=` and check row counts. Use `join` for index joins and `concat` for stacking.
Hindi: `merge` tables को keys पर inner, left, right या outer logic से जोड़ता है। Duplicate keys से rows बढ़ जाती हैं, इसलिए `validate=` और row count जांचें। Index join के लिए `join` और stacking के लिए `concat` इस्तेमाल करें।

---

## ➡️ Next Topic
**383. Matplotlib Basics** — draw line, bar and scatter charts with figures and axes, and save them as images.
