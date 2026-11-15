---

# 490. Build CSV Import/Export
# हिंदी में: CSV Import/Export बनाना (validation + streaming)

Full runnable solution: [main.py](main.py) (needs `pip install fastapi httpx pydantic python-multipart`; upload endpoint with row-level errors and a streaming download).

---

## 🔵 Simple Definition (English)
CSV import reads an uploaded file row by row, validates each row, saves the good ones and reports the bad ones with line numbers. CSV export writes rows back as a file, streamed so memory stays small.

## 🔵 सरल परिभाषा (Hindi)
CSV import upload हुई file को row-by-row पढ़ता है, हर row validate करता है, सही rows सेव करता है और गलत rows को line number के साथ बताता है। Export rows को file में लिखता है, stream करके ताकि memory कम लगे।

---

## 🔴 Problem it Solves
Business users live in Excel. Bulk-loading customers or downloading orders by hand is slow. Naive `split(",")` breaks on quoted commas, one bad row can crash the whole upload, and loading millions of rows into memory crashes the server.

## 🔴 यह क्यों बना? (Hindi)
Business users Excel में काम करते हैं। Customers bulk upload या orders download हाथ से करना धीमा है। साधारण `split(",")` quote के अंदर के comma पर टूट जाता है, एक गलत row पूरा upload गिरा सकती है, और लाखों rows memory में भरने से server crash हो सकता है।

---

## 🟢 How it Works — Step by Step

```
Import:
Step 1 → Upload file; decode with utf-8-sig (strips Excel BOM)
Step 2 → csv.DictReader maps each row to {header: value}
Step 3 → Validate each row with a Pydantic model
Step 4 → Valid -> good list; invalid -> {"line": n, "error": ...}
Step 5 → Save good rows (in one transaction), return summary

Export:
Step 1 → csv.DictWriter + StringIO buffer
Step 2 → yield header, then yield one row at a time
Step 3 → StreamingResponse sends chunks as they are produced
```

## 🟢 कैसे काम करता है? (Hindi)
```
Import:
Step 1 → File upload होती है; utf-8-sig से decode (Excel BOM हटता है)
Step 2 → csv.DictReader हर row को {header: value} बनाता है
Step 3 → हर row Pydantic model से validate होती है
Step 4 → सही -> good list; गलत -> {"line": n, "error": ...}
Step 5 → सही rows save (एक transaction में), summary लौटाओ

Export:
Step 1 → csv.DictWriter + StringIO buffer
Step 2 → पहले header yield, फिर एक-एक row
Step 3 → StreamingResponse chunks बनते ही भेजता है
```

---

## 🟡 Real World Example
An HR tool bulk-uploads 5,000 employees: 4,980 import, 20 are returned as "line 17: invalid email" so HR fixes only those. An accounting team downloads a year of Razorpay settlements as CSV that opens in Excel.

## 🟡 Real Example Hindi mein
HR tool में 5,000 employees bulk upload होते हैं: 4,980 import हो जाते हैं और 20 "line 17: invalid email" जैसे errors में लौटते हैं, HR सिर्फ़ वही ठीक करता है। Accounting team साल भर के Razorpay settlements CSV में download करती है जो Excel में खुलता है।

---

## 💻 Code Example — Basic
```python
# csv module handles quotes and commas correctly
import csv  # standard library
import io  # in-memory text file

text = 'name,age\n"Lee, Jr",40\nAsha,30\n'  # note the comma inside quotes
rows = list(csv.DictReader(io.StringIO(text)))  # list of dicts
print(rows[0])  # quoted comma preserved
print(sum(int(r["age"]) for r in rows))  # values are strings: convert yourself

out = io.StringIO()  # write side
w = csv.writer(out)  # plain writer
w.writerow(["a,b", 'say "hi"'])  # needs quoting
print(out.getvalue().strip())  # csv quoted it for us
# Output:
# {'name': 'Lee, Jr', 'age': '40'}
# 70
# "a,b","say ""hi"""
```

## 💻 Code Example — Advanced
```python
# Excerpt from main.py: validated import + streaming export
def import_csv(text: str) -> tuple[list[UserRow], list[dict]]:
    good, errors = [], []
    reader = csv.DictReader(io.StringIO(text, newline=""))
    for line_no, row in enumerate(reader, start=2):  # line 1 is the header
        try:
            good.append(UserRow(**row))
        except (ValidationError, TypeError) as exc:
            msg = "; ".join(f"{e['loc'][0]}: {e['msg']}" for e in exc.errors()) if isinstance(exc, ValidationError) else str(exc)
            errors.append({"line": line_no, "error": msg})
    return good, errors

def export_csv(rows: list[dict]) -> Iterator[str]:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["name", "email", "age"])
    writer.writeheader()
    yield buf.getvalue()
    for r in rows:
        buf.seek(0); buf.truncate()  # reuse buffer: constant memory
        writer.writerow(r)
        yield buf.getvalue()
```
Real output of `python main.py`:
```
{'imported': 2, 'errors': [{'line': 3, 'error': 'email: Value error, invalid email'}, {'line': 4, 'error': 'age: Input should be a valid integer, unable to parse string as an integer'}]}
name,email,age
Asha,asha@x.com,30
"Lee, Jr",lee@x.com,40

all ok
```

---

## 🟠 JavaScript vs Python Comparison
JS needs `papaparse` or `csv-parse`; Python ships `csv` in the standard library. `DictReader` is like Papa's `header: true`.

```python
rows = list(csv.DictReader(f))  # list of dicts
```
```javascript
const { data } = Papa.parse(text, { header: true }); // array of objects
```

---

## 🟠 FastAPI Connection
Uploads use `UploadFile` (needs `python-multipart`). Exports use `StreamingResponse` with `text/csv`. Validation reuses the same Pydantic models as your JSON API. For big files, process in chunks in a background job.

```python
@app.post("/import")
async def import_endpoint(file: UploadFile = File(...)) -> dict:
    text = (await file.read()).decode("utf-8-sig")  # BOM-safe
    good, errors = import_csv(text)
    return {"imported": len(good), "errors": errors}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Parsing with `line.split(",")`.
✅ Correct: use the `csv` module.

```python
# Wrong
'"Lee, Jr",40'.split(",")   # ['"Lee', ' Jr"', '40']
# Right
next(csv.reader(['"Lee, Jr",40']))   # ['Lee, Jr', '40']
```

❌ Mistake 2: Opening files without `newline=""` (blank lines on Windows) and ignoring the BOM.
✅ Correct: `open(path, newline="", encoding="utf-8-sig")`.

❌ Mistake 3: CSV injection: a cell starting with `=`, `+`, `-`, `@` runs as a formula in Excel.
✅ Correct: when exporting user-supplied text, prefix such cells with `'`. (Not implemented in main.py.)

---

## 🧠 Tricky Interview Question
```python
import csv, io
r = csv.DictReader(io.StringIO("a,b\n1,2\n"))
print(list(r)); print(list(r))
```
Answer: `[{'a': '1', 'b': '2'}]` then `[]`. A reader is an iterator; after one pass it is exhausted. Also every value is a string.

---

## ⚫ Interview Questions + Answers

Q1: Why streaming export?
A1: Memory stays constant and the user starts receiving bytes immediately.

Q2: Import all-or-nothing or partial?
A2: Depends on the business. Partial with an error report is friendlier; all-or-nothing is safer for money data. Use a DB transaction either way.

Q3: How to import 1M rows fast?
A3: Batch inserts (`executemany` / `COPY`), chunked reading, run as a background job with progress.

Q4: Why `utf-8-sig`?
A4: Excel adds a BOM; plain `utf-8` leaves `﻿` glued to the first header name.

Q5: CSV vs JSON?
A5: CSV is flat, compact and spreadsheet-friendly; JSON handles nesting and types.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Bulk loads, spreadsheet exchange, simple data exports

❌ Avoid when:
- Nested data, strict types, or very large analytic data (use Parquet/JSON lines)

---

## 📊 Visual Diagram
```
 upload ─► decode(utf-8-sig) ─► DictReader ─► Pydantic row check
                                    ├─ ok  ─► DB
                                    └─ bad ─► errors[{line, msg}]
 DB rows ─► DictWriter ─► yield chunk ─► StreamingResponse ─► users.csv
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CSV | Comma separated values | comma से अलग किए मान |
| BOM | Byte order mark | file की शुरुआती पहचान bytes |
| DictReader | Rows as dicts | rows को dict में बदलना |
| Streaming | Send in pieces | टुकड़ों में भेजना |
| Row validation | Check each record | हर record की जाँच |

---

## ⚡ 3-Line Summary
English: Use the csv module, never split on commas.
Validate every row and report line-numbered errors.
Stream exports so memory stays small.
Hindi: csv module इस्तेमाल करो, comma पर split कभी नहीं।
हर row validate करो और line number के साथ errors बताओ।
Export को stream करो ताकि memory कम लगे।

---

## ➡️ Next Topic
491. Async Concurrent Requests: after files, learn to call many external APIs at the same time.

---
