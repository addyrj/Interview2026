---

# 378. DataFrame + Series
# हिंदी में: DataFrame + Series (Pandas के दो मुख्य objects)

---

## 🔵 Simple Definition (English)
A Series is one labelled column of data. A DataFrame is a table of many Series that share the same row labels (index). Almost everything in pandas is one of these two objects.

## 🔵 सरल परिभाषा (Hindi)
Series data का एक labelled column है। DataFrame कई Series की table है जिनके row labels (index) एक ही होते हैं। Pandas में लगभग सब कुछ इन्हीं दो objects में से एक होता है।

---

## 🔴 Problem it Solves
A list or a dict of lists has no labels, no types, no alignment. If you add two lists of prices for different products you must match positions by hand and errors are silent. Series and DataFrame attach a label to each value, so operations line up by label, columns keep their own dtype, and you can select data by name or position.

## 🔴 यह क्यों बना? (Hindi)
List या dict of lists में labels, types या alignment नहीं होते। अलग-अलग products की दो price lists जोड़ने पर positions हाथ से मिलाने पड़ते हैं और गलतियां चुपचाप हो जाती हैं। Series और DataFrame हर value पर label लगाते हैं, इसलिए operations label के हिसाब से align होते हैं, हर column का अपना dtype रहता है, और data को नाम या position से चुन सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Series = values (NumPy array) + index (labels) + name + dtype
Step 2 → DataFrame = dict of Series sharing ONE index; df["col"] gives a Series
Step 3 → Select by label:    df.loc[row_label, "col"]       (end of slice included)
Step 4 → Select by position: df.iloc[row_pos, col_pos]      (end of slice excluded)
Step 5 → Maths between objects ALIGNS on index labels first; no match -> NaN
Step 6 → df[["a"]] (list inside) -> DataFrame, df["a"] -> Series
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Series = values (NumPy array) + index (labels) + name + dtype
Step 2 → DataFrame = Series का dict जो एक ही index share करती हैं; df["col"] एक Series देता है
Step 3 → Label से चुनो:    df.loc[row_label, "col"]       (slice का अंत शामिल)
Step 4 → Position से चुनो: df.iloc[row_pos, col_pos]      (slice का अंत शामिल नहीं)
Step 5 → Objects के बीच maths पहले index labels पर ALIGN होता है; मेल नहीं -> NaN
Step 6 → df[["a"]] (अंदर list) -> DataFrame, df["a"] -> Series
```

---

## 🟡 Real World Example
An e-commerce backend keeps one Series of stock per SKU and one Series of price per SKU. `stock * price` aligns by SKU automatically, even if the SKUs are in a different order or one is missing. A user table becomes a DataFrame indexed by `user_id`, so `df.loc[42]` is an instant lookup. An AI feature store is a DataFrame where each column is a feature.

## 🟡 Real Example Hindi mein
E-commerce backend हर SKU का stock एक Series में और price दूसरी Series में रखता है। `stock * price` SKU के हिसाब से अपने आप align हो जाता है, चाहे SKUs का order अलग हो या कोई missing हो। User table, `user_id` index वाला DataFrame बन जाती है, इसलिए `df.loc[42]` तुरंत lookup है। AI feature store ऐसा DataFrame है जिसका हर column एक feature है।

---

## 💻 Code Example — Basic
```python
# Basic Series and DataFrame
import pandas as pd                               # import pandas

s: pd.Series = pd.Series([10, 20, 30], index=["a", "b", "c"], name="price")   # labelled 1-D data
print(s["b"], s.iloc[0])                          # by label and by position
print((s * 2).to_dict())                          # vectorised maths on every item
other: pd.Series = pd.Series([1, 2], index=["a", "z"])   # different labels
print((s + other).to_dict())                      # aligned by label, missing -> NaN

df: pd.DataFrame = pd.DataFrame(
    {"name": ["Asha", "Ravi", "Meera"], "age": [25, 31, 28], "city": ["Delhi", "Pune", "Delhi"]}
)                                                 # build from dict of columns
print(df.shape, list(df.columns))                 # (3, 3) and the column names
print(type(df["age"]).__name__)                   # one column is a Series
print(df.loc[1, "name"], df.iloc[2, 1])           # label-based and position-based access
df["age_next"] = df["age"] + 1                    # add a computed column
print(df.query("age > 26")["name"].tolist())      # filter with a query string
print(df.set_index("name").loc["Ravi", "city"])   # use a column as the index

# Output:
# 20 10
# {'a': 20, 'b': 40, 'c': 60}
# {'a': 11.0, 'b': nan, 'c': nan, 'z': nan}
# (3, 3) ['name', 'age', 'city']
# Series
# Ravi 28
# ['Ravi', 'Meera']
# Pune
```

## 💻 Code Example — Advanced
```python
# Production style: typed constructors, safe selection, dtype control, records for APIs
import pandas as pd                               # pandas
from pydantic import BaseModel                    # validation of API rows


class User(BaseModel):
    """One user row."""
    user_id: int                                  # id
    name: str                                     # name
    plan: str                                     # plan name


def to_frame(rows: list[User]) -> pd.DataFrame:
    """Convert validated models into a typed DataFrame."""
    df: pd.DataFrame = pd.DataFrame([r.model_dump() for r in rows])   # list of dicts -> table
    df["plan"] = df["plan"].astype("category")    # few repeated values -> category saves memory
    return df.set_index("user_id")                # unique id as the index


def get_user(df: pd.DataFrame, user_id: int) -> dict[str, object]:
    """Return one row as a plain dict or raise KeyError."""
    if user_id not in df.index:                   # check before .loc raises a vague error
        raise KeyError(f"user {user_id} not found")   # explicit message
    return df.loc[user_id].to_dict()              # Series -> dict


users = [User(user_id=1, name="Asha", plan="pro"), User(user_id=2, name="Ravi", plan="free"),
         User(user_id=3, name="Meera", plan="pro")]   # validated input
frame = to_frame(users)                           # build frame
print(frame.dtypes.astype(str).to_dict())         # plan is category
print(get_user(frame, 2))                         # one row as dict
print(frame.reset_index().to_dict(orient="records"))   # JSON-ready list of dicts
try:                                              # error handling
    get_user(frame, 99)                           # missing id
except KeyError as e:                             # catch
    print("Error:", e)                            # message

# Output:
# {'name': 'str', 'plan': 'category'}
# {'name': 'Ravi', 'plan': 'free'}
# [{'user_id': 1, 'name': 'Asha', 'plan': 'pro'}, {'user_id': 2, 'name': 'Ravi', 'plan': 'free'}, {'user_id': 3, 'name': 'Meera', 'plan': 'pro'}]
# Error: 'user 99 not found'
```



---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (pandas) | JavaScript |
|---------|-----------------|-----------|
| 1-D labelled data | `Series` | `Map` or object |
| Table | `DataFrame` | array of objects |
| Get a column | `df["age"]` | `rows.map(r => r.age)` |
| Row by label | `df.loc[1]` | `rows.find(r => r.id === 1)` |
| Row by position | `df.iloc[0]` | `rows[0]` |
| Auto-align on labels | yes | no |

```python
# Python way — label alignment is automatic
import pandas as pd                               # pandas
a: pd.Series = pd.Series([1, 2], index=["x", "y"])    # labels x, y
b: pd.Series = pd.Series([10, 20], index=["y", "x"])  # same labels, other order
print((a + b).to_dict())                           # {'x': 21, 'y': 12}
```
```javascript
// JavaScript way — you align by key yourself
const a = {x: 1, y: 2}, b = {y: 10, x: 20};
const sum = Object.fromEntries(Object.keys(a).map(k => [k, a[k] + b[k]]));
console.log(sum);   // { x: 21, y: 12 }
```

Key difference: pandas adds values by label, not by position. JavaScript arrays only know positions, so you must join by key yourself. Also `df.loc` (label) vs `df.iloc` (position) has no JS equivalent.

---

## 🟠 FastAPI Connection
In FastAPI you rarely return a DataFrame directly. Convert it with `to_dict(orient='records')` into a list of dicts that Pydantic/FastAPI can serialise. NaN is not valid JSON (it becomes an error or `null` depending on the encoder), so replace NaN with `None` first and convert numpy numbers with `float()`/`int()`.

```python
# FastAPI: return a DataFrame as JSON the safe way
import pandas as pd                               # pandas
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # demo client

app: FastAPI = FastAPI()
DF: pd.DataFrame = pd.DataFrame({"id": [1, 2, 3], "price": [9.5, float("nan"), 12.0]})   # in-memory table


@app.get("/items")
def items() -> list[dict[str, object]]:
    clean: pd.DataFrame = DF.astype(object).where(DF.notna(), None)   # NaN -> None (NaN is invalid JSON)
    return clean.to_dict(orient="records")        # list of plain dicts, FastAPI serialises it


@app.get("/items/{item_id}")
def item(item_id: int) -> dict[str, object]:
    row: pd.DataFrame = DF[DF["id"] == item_id]   # filter -> frame with 0 or 1 rows
    if row.empty:                                 # nothing matched
        return {"error": "not found"}
    return {"id": item_id, "price": float(row["price"].iloc[0])}   # numpy -> python float


client = TestClient(app)
print(client.get("/items").json())
print(client.get("/items/1").json(), client.get("/items/9").json())

# Output:
# [{'id': 1, 'price': 9.5}, {'id': 2, 'price': None}, {'id': 3, 'price': 12.0}]
# {'id': 1, 'price': 9.5} {'error': 'not found'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `s[0]` on a Series whose index is integers but not 0..n-1
✅ Correct: use `iloc` for positions, `loc` for labels

```python
import pandas as pd
s = pd.Series([1, 2, 3], index=[2, 1, 0])
# Wrong — s[0] is the LABEL 0, so you get 3, not the first item
print(s[0])                           # 3
# Right
print(s.iloc[0])                      # 1  (first by position)
```

❌ Mistake 2: Confusing `df["a"]` (Series) with `df[["a"]]` (DataFrame)
✅ Correct: check `.shape` when a function needs 2-D input (scikit-learn does)

```python
import pandas as pd
df = pd.DataFrame({"a": [1, 2]})
print(df["a"].shape, df[["a"]].shape)   # (2,) (2, 1)
```

❌ Mistake 3: Forgetting that a filtered frame keeps its OLD index
✅ Correct: `reset_index(drop=True)` if you need 0..n-1 again

```python
import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3]})
f = df[df.a > 1]
# Wrong — f.loc[0] raises KeyError (label 0 was filtered out)
print(f.index.tolist(), f.loc[1, "a"])  # [1, 2] 2
# Right
f = f.reset_index(drop=True)
print(f.loc[0, "a"])                  # 2
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import pandas as pd
s = pd.Series([1, 2, 3], index=[2, 1, 0])
print(s[0], s.iloc[0])
a = pd.Series([1, 2], index=["x", "y"])
b = pd.Series([10, 20], index=["y", "x"])
print((a + b).to_dict())
```
Answer: `3 1` then `{'x': 21, 'y': 12}`. With an integer index `s[0]` means label 0 (value 3), while `iloc[0]` means the first position (value 1). Addition aligns on labels, not positions: x pairs with x (1+20) and y with y (2+10), even though `b` is stored in the other order. If a label exists in only one Series the result is `NaN`.

---

## ⚫ Interview Questions + Answers

Q1: Series vs DataFrame vs ndarray?
A1: ndarray is raw typed numbers with positions only. Series adds an index and a name to a 1-D array. DataFrame is a table of Series with a shared index and a dtype per column (mixed types allowed).

Q2: `loc` vs `iloc` vs `at`/`iat`?
A2: `loc` = labels, `iloc` = positions, `at`/`iat` = fast scalar access by label/position. Use `at` in tight loops and `loc`/`iloc` for slices.

Q3: What is the index for and when should you set it?
A3: It labels rows for fast lookup and alignment. Set it to a unique key (`set_index("user_id")`) when you look up or join by that key; keep the default RangeIndex when rows have no natural key.

Q4: What is `category` dtype?
A4: A column with few repeated string values stored as integer codes + a lookup table. It uses far less memory and is faster for groupby (e.g. plan names, cities, status).

Q5: How do you convert a DataFrame for an API?
A5: `df.to_dict(orient="records")` gives a list of row dicts. Replace NaN with None and numpy scalars with Python types first. For a single row use `df.loc[key].to_dict()`.

---

## 🔷 When to Use + When Not to Use
✅ Use Series when:
- You have one column, or a labelled vector (prices per SKU)

✅ Use DataFrame when:
- You have several columns with different types that share row labels

❌ Avoid when:
- You only need a plain list of 5 items (a list is simpler)
- You need row-by-row inserts in a hot loop - DataFrame appends are slow; collect in a list, then build once

---

## 📊 Visual Diagram
```
DataFrame df
index   name     age   city
  0     Asha     25    Delhi     <- row (df.loc[0])
  1     Ravi     31    Pune
  2     Meera    28    Delhi
          ^        ^
          |        +-- df["age"]  -> Series (shares the same index)
          +----------- df["name"] -> Series

Series "age":  index [0,1,2] -> values [25,31,28], dtype int64
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Series | Labelled 1-D array | Labelled 1-D array |
| DataFrame | Table of Series | Series की table |
| Index | Row labels | Row labels |
| `loc` | Select by label | Label से चुनना |
| `iloc` | Select by position | Position से चुनना |
| Alignment | Matching by label before maths | Maths से पहले labels मिलाना |
| dtype | Data type of a column | Column का data type |

---

## ⚡ 3-Line Summary
English: A Series is a labelled column; a DataFrame is a table of Series sharing one index. Use `loc` for labels, `iloc` for positions, and remember maths aligns on labels. Convert with `to_dict('records')` for APIs.
Hindi: Series एक labelled column है; DataFrame एक index share करने वाली Series की table है। Labels के लिए `loc`, positions के लिए `iloc` इस्तेमाल करें, और याद रखें कि maths labels पर align होता है। APIs के लिए `to_dict('records')` से convert करें।

---

## ➡️ Next Topic
**379. Pandas Operations** — filtering, sorting, groupby, merge, apply, pivot and cumulative operations.
