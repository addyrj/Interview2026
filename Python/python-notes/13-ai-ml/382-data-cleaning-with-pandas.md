---

# 382. Data Cleaning with Pandas
# हिंदी में: Pandas से डेटा की सफ़ाई (Data Cleaning)

---

## 🔵 Simple Definition (English)
Data cleaning means fixing messy data before using it: removing duplicates, fixing wrong types, trimming text, and handling missing values (NaN). Pandas gives one-line tools for each job: `drop_duplicates`, `to_numeric`, `str.strip`, `fillna`, `dropna`.

## 🔵 सरल परिभाषा (Hindi)
Data cleaning का मतलब है गंदे डेटा को इस्तेमाल से पहले ठीक करना: duplicates हटाना, गलत types सुधारना, text की extra spaces हटाना और missing values (NaN) संभालना। Pandas में हर काम के लिए एक-लाइन के tools हैं: `drop_duplicates`, `to_numeric`, `str.strip`, `fillna`, `dropna`।

---

## 🔴 Problem it Solves
- Real data (CSV from Razorpay, Excel from sales team, scraped pages) is never clean: " Delhi", "DELHI", "delhi" are three different cities for a computer.
- Numbers arrive as strings ("250.5"), dates arrive as text, and some cells are empty.
- If you feed this to a model or a dashboard, results are wrong: totals are off, `groupby` splits one city into three groups, ML training crashes on NaN.
- "Garbage in, garbage out." Data scientists spend 60-80% of their time cleaning.

## 🔴 यह क्यों बना? (Hindi)
- असली डेटा कभी साफ़ नहीं होता: " Delhi", "DELHI", "delhi" computer के लिए तीन अलग शहर हैं।
- Numbers string ("250.5") में आते हैं, dates text में, और कुछ cells खाली होते हैं।
- ऐसा डेटा model या dashboard में डालो तो नतीजे गलत आते हैं: total गलत, `groupby` एक शहर को तीन हिस्सों में बाँट देता है, ML training NaN पर crash हो जाती है।
- "Garbage in, garbage out।" Data scientists का 60-80% समय cleaning में जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Inspect:    df.info(), df.isna().sum(), df.describe()
Step 2 → Normalise:  column names lower_snake_case, strip/Title text
Step 3 → Fix types:  to_numeric / to_datetime with errors="coerce"
Step 4 → Dedupe:     drop_duplicates(subset=[...])
Step 5 → Missing:    fillna (median/constant) OR dropna (if row unusable)
Step 6 → Validate:   clip impossible values, assert expectations
Step 7 → Save:       return a NEW cleaned DataFrame + a report
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → जाँचो:        df.info(), df.isna().sum(), df.describe()
Step 2 → एक जैसा करो:  column names lower_snake_case, text को strip/Title
Step 3 → Types सुधारो: to_numeric / to_datetime, errors="coerce" के साथ
Step 4 → Duplicates:   drop_duplicates(subset=[...])
Step 5 → Missing:      fillna (median/constant) या dropna (अगर row बेकार है)
Step 6 → Validate:     असंभव values clip करो, assert लगाओ
Step 7 → Save:         नया साफ़ DataFrame + एक report return करो
```

`errors="coerce"` का मतलब: जो value convert न हो सके उसे NaN बना दो (crash मत करो)।

---

## 🟡 Real World Example
A food-delivery company (Swiggy-like) receives a daily orders CSV from 50 restaurant partners. Cities are typed in every possible way, amounts sometimes contain "abc" or are negative because of refunds typed wrongly, and the same order is sometimes uploaded twice. A nightly job cleans the file with pandas, stores a report ("5 rows in, 3 out, 1 duplicate removed") and only then loads it into the warehouse. A FastAPI endpoint lets the ops team upload a CSV and get the cleaning report back.

## 🟡 Real Example Hindi mein
एक food-delivery कंपनी (Swiggy जैसी) को रोज़ 50 restaurant partners से orders की CSV मिलती है। शहर के नाम हर तरह से लिखे होते हैं, amount में कभी "abc" होता है या refund की वजह से negative, और कभी एक ही order दो बार upload हो जाता है। रात को एक job pandas से file साफ़ करती है, एक report बनाती है ("5 rows आईं, 3 बचीं, 1 duplicate हटा") और उसके बाद ही data warehouse में डालती है। FastAPI endpoint से ops team CSV upload करके cleaning report पा सकती है।

---

## 💻 Code Example — Basic
```python
import pandas as pd  # import pandas library

df: pd.DataFrame = pd.DataFrame({  # build a small messy orders table
    "order_id": [1, 2, 2, 3, 4],  # order 2 is duplicated
    "city": [" Delhi", "mumbai ", "mumbai ", None, "DELHI"],  # messy text + one missing
    "amount": ["100", "250.5", "250.5", "abc", None],  # numbers stored as text
})
print(df.isna().sum().to_dict())  # count nulls per column
df = df.drop_duplicates()  # remove fully duplicate rows
df["city"] = df["city"].str.strip().str.title()  # trim spaces + Title Case
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")  # "abc" becomes NaN
df["city"] = df["city"].fillna("Unknown")  # fill missing city
df["amount"] = df["amount"].fillna(df["amount"].median())  # fill missing amount with median
print(df.to_string(index=False))  # print cleaned table
print(df.dtypes.to_dict())  # show final dtypes

# Output (verified with pandas 3.1, Python 3.13):
# {'order_id': 0, 'city': 1, 'amount': 1}
#  order_id    city  amount
#         1   Delhi  100.00
#         2  Mumbai  250.50
#         3 Unknown  175.25
#         4   Delhi  175.25
# {'order_id': dtype('int64'), 'city': <StringDtype(...)>, 'amount': dtype('float64')}
# Note: text columns are the new "str" dtype in pandas 3 (they were "object" in pandas 2).
```

## 💻 Code Example — Advanced
```python
from __future__ import annotations  # allow modern type hints everywhere
import pandas as pd  # pandas
from pydantic import BaseModel  # typed report object


class CleanReport(BaseModel):  # report describing what cleaning did
    rows_in: int  # rows before cleaning
    rows_out: int  # rows after cleaning
    dupes_removed: int  # duplicates dropped
    nulls_filled: int  # nulls found before filling


def clean_orders(raw: pd.DataFrame) -> tuple[pd.DataFrame, CleanReport]:
    """Pure function: never mutates input, returns cleaned copy + report."""
    df = raw.copy()  # defensive copy so the caller's data is safe
    rows_in = len(df)  # remember the original size
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]  # normalise column names
    df = df.drop_duplicates()  # drop duplicate rows
    dupes = rows_in - len(df)  # how many were dropped
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")  # coerce numbers
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)  # parse dates
    nulls_before = int(df.isna().sum().sum())  # total nulls before filling
    df["city"] = df["city"].astype("string").str.strip().str.title().fillna("Unknown")  # clean text
    df["amount"] = df["amount"].clip(lower=0).fillna(0.0)  # no negatives, fill NaN with 0
    df = df.dropna(subset=["created_at"])  # a row without a valid date is unusable
    df["status"] = df["status"].astype("category")  # few distinct values -> category saves memory
    report = CleanReport(rows_in=rows_in, rows_out=len(df),
                         dupes_removed=dupes, nulls_filled=nulls_before)  # build report
    return df.reset_index(drop=True), report  # return cleaned data and report


raw = pd.DataFrame({  # sample dirty data with messy column names
    " order id": [1, 2, 2, 3, 4],
    "city ": ["delhi ", "MUMBAI", "MUMBAI", None, "pune"],
    "Amount": ["10", "-5", "-5", "x", "40"],
    "created at": ["2026-01-01", "2026-01-02", "2026-01-02", "bad-date", "2026-01-05"],
    "Status": ["paid", "paid", "paid", "failed", "paid"],
})
clean, rep = clean_orders(raw)  # run the pipeline
print(clean.to_string(index=False))  # cleaned output
print(rep.model_dump())  # report as dict
print(clean.dtypes.astype(str).to_dict())  # dtypes

# Output (verified):
#  order_id   city  amount                created_at status
#         1  Delhi    10.0 2026-01-01 00:00:00+00:00   paid
#         2 Mumbai     0.0 2026-01-02 00:00:00+00:00   paid
#         4   Pune    40.0 2026-01-05 00:00:00+00:00   paid
# {'rows_in': 5, 'rows_out': 3, 'dupes_removed': 1, 'nulls_filled': 3}
# {'order_id': 'int64', 'city': 'string', 'amount': 'float64',
#  'created_at': 'datetime64[us, UTC]', 'status': 'category'}
# (datetime unit is [us] in pandas 3, [ns] in pandas 2)
```

---

## 🟠 JavaScript vs Python Comparison
In JS you clean arrays of objects with `map/filter/reduce` and write each rule by hand. Pandas works on whole columns at once (vectorised), so one line replaces a loop.

```python
# Python (pandas): column-wise, no explicit loop
import pandas as pd
df = pd.DataFrame({"city": [" Delhi ", "mumbai"]})  # sample data
df["city"] = df["city"].str.strip().str.title()  # clean the whole column
df = df.drop_duplicates()  # dedupe
```
```javascript
// JavaScript: manual loop over objects
let rows = [{ city: " Delhi " }, { city: "mumbai" }];  // sample data
rows = rows.map(r => ({
  ...r,
  city: r.city.trim().replace(/^\w/, c => c.toUpperCase()),  // clean each row
}));
const seen = new Set();  // dedupe by hand
rows = rows.filter(r => !seen.has(r.city) && seen.add(r.city));
```

Key differences:
- Pandas is vectorised (C speed); JS loops run per object.
- Missing value: pandas `NaN`/`pd.NA`, JS `null`/`undefined` (and `NaN` for numbers).
- `errors="coerce"` has no direct JS equivalent: you write `Number(x)` then check `isNaN`.

---

## 🟠 FastAPI Connection
Ops upload a CSV; the API cleans it and returns the report. Pandas is CPU-bound and blocking, so use a plain `def` endpoint (FastAPI runs it in a threadpool) or `run_in_threadpool`.

```python
import io  # in-memory file handling
import pandas as pd  # pandas
from fastapi import FastAPI, UploadFile, HTTPException  # FastAPI pieces

app = FastAPI()  # create the app


@app.post("/orders/clean")  # POST endpoint
def clean_upload(file: UploadFile) -> dict[str, int]:  # plain def -> runs in threadpool
    try:
        raw = pd.read_csv(io.BytesIO(file.file.read()))  # parse uploaded CSV
    except Exception as exc:  # malformed CSV
        raise HTTPException(status_code=400, detail=f"Bad CSV: {exc}")  # tell the client
    before = len(raw)  # rows before
    cleaned = raw.drop_duplicates().dropna(how="all")  # tiny cleaning step
    return {"rows_in": before, "rows_out": len(cleaned)}  # JSON report
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Chained assignment / modifying a slice (`SettingWithCopyWarning`; in pandas 3 with Copy-on-Write it silently does nothing to the original)
✅ Correct: use `.loc` or assign a whole column.

```python
# Wrong
df[df["amount"] < 0]["amount"] = 0  # modifies a temporary copy, original unchanged
# Right
df.loc[df["amount"] < 0, "amount"] = 0  # modifies the real DataFrame
```

❌ Mistake 2: `inplace=True` everywhere (it does not save memory, breaks method chaining, and is being discouraged)
✅ Correct: re-assign.

```python
# Wrong
df.drop_duplicates(inplace=True)
# Right
df = df.drop_duplicates()
```

❌ Mistake 3: Filling NaN with the mean before splitting train/test (data leakage)
✅ Correct: compute the fill value on train only.

---

## 🧠 Tricky Interview Question
```python
import pandas as pd
import numpy as np

s = pd.Series([1, np.nan, 3])
print(s.sum(), s.mean(), (s == s).all(), np.nan == np.nan)
```
Answer: `4.0 2.0 False False`. Pandas skips NaN in `sum`/`mean` by default (`skipna=True`), so sum=4.0 and mean=2.0. But `NaN == NaN` is always False, so `s == s` is False at the NaN position and `.all()` is False. Use `isna()` to test for missing values, never `== np.nan`.

---

## ⚫ Interview Questions + Answers

Q1: `dropna` vs `fillna` — how do you choose?
A1: Drop when the row is useless without that field (no date, no id) or missing data is tiny and random. Fill when the row is still valuable: median for skewed numbers, mean for symmetric ones, a constant like "Unknown" for categories, forward-fill for time series. Always record how many values you changed.

Q2: What does `errors="coerce"` do in `to_numeric`/`to_datetime`?
A2: Invalid values become NaN/NaT instead of raising. It lets the pipeline survive bad rows, but you must then count and handle the new NaNs, otherwise you hide data problems.

Q3: `drop_duplicates()` vs `drop_duplicates(subset=["order_id"], keep="last")`?
A3: The first removes only rows identical in all columns. The second treats rows with the same `order_id` as duplicates and keeps the newest (last) one. Use `subset` for business keys.

Q4: Why convert a text column to `category`?
A4: A column like `status` with 3 distinct values repeated 10 million times stores each string separately as text. `category` stores small integer codes plus one lookup table: large memory savings and faster `groupby`.

Q5: How do you spot outliers?
A5: `describe()`, boxplots, the IQR rule (below Q1 - 1.5*IQR or above Q3 + 1.5*IQR) or z-scores. Then decide: cap with `clip`, remove, or keep if valid (a real Rs 5 lakh order).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Data fits in memory (up to a few GB) and is tabular
- You need quick, repeatable cleaning scripts before ML or reporting
- Files come from humans (CSV/Excel)

❌ Avoid when:
- Data is far bigger than RAM (use Polars, DuckDB or Spark)
- Rules are simple constraints that the database can enforce (NOT NULL, UNIQUE)
- You need row-by-row streaming validation (use Pydantic models)

---

## 📊 Visual Diagram
```
 raw.csv ──► inspect ──► normalise ──► fix types ──► dedupe ──► handle NaN ──► validate
   │          info()     strip/title    to_numeric    drop_dup    fillna/       clip/assert
   │                                    to_datetime                dropna
   ▼                                                                              │
 5 rows ─────────────────────────────────────────────────────────────────────►  3 rows + report
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| NaN | Missing numeric value | गायब संख्या |
| NaT | Missing datetime | गायब तारीख |
| coerce | Turn bad values into NaN | खराब values को NaN बनाना |
| Imputation | Filling missing values | गायब values भरना |
| Outlier | Extreme unusual value | असामान्य चरम value |
| Vectorised | Operation on whole column | पूरे column पर एक साथ operation |

---

## ⚡ 3-Line Summary
English: Cleaning = normalise text, fix types with `errors="coerce"`, drop duplicates, then fill or drop NaN. Write it as a pure function that returns a new DataFrame plus a report. Avoid chained assignment and `inplace=True`.
Hindi: Cleaning = text एक जैसा करो, `errors="coerce"` से types ठीक करो, duplicates हटाओ, फिर NaN भरो या हटाओ। इसे ऐसा pure function बनाओ जो नया DataFrame और report लौटाए। Chained assignment और `inplace=True` से बचो।

---

## ➡️ Next Topic
**383. Matplotlib Basics** — once the data is clean, plot it to see patterns and to explain results.
