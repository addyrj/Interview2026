---

# 191. csv Module
# हिंदी में: csv Module (table data पढ़ना और लिखना)

---

## 🔵 Simple Definition (English)
`csv` reads and writes comma separated values: plain text tables where each line is a row and commas separate columns. It handles the hard parts for you: quotes, commas inside a value, line breaks inside a value and different delimiters.

## 🔵 सरल परिभाषा (Hindi)
`csv` comma से अलग किए values (comma separated values) पढ़ता और लिखता है: plain text tables जहाँ हर line एक row है और comma columns को अलग करता है। यह मुश्किल हिस्से खुद संभालता है: quotes, value के अंदर comma, value के अंदर नई line और अलग delimiters।

---

## 🔴 Problem it Solves
`line.split(",")` breaks on `"Delhi, NCR"` (comma inside a value), on quoted quotes (`"He said ""hi"""`) and on multi-line cells. Writing CSV by hand forgets quoting rules. The `csv` module implements the real rules so Excel, Google Sheets and databases can open your file.

## 🔴 यह क्यों बना? (Hindi)
`line.split(",")` `"Delhi, NCR"` (value में comma), quotes के अंदर quotes (`"He said ""hi"""`) और multi-line cells पर टूट जाता है। हाथ से CSV लिखने में quoting rules छूट जाते हैं। `csv` module असली rules लागू करता है ताकि Excel, Google Sheets और databases आपकी file खोल सकें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Open the file with newline="" (csv does its own newline handling)
Step 2 → reader(fh) yields each row as a list of STRINGS
Step 3 → DictReader uses the first row as keys: each row is a dict
Step 4 → writer(fh).writerow(list) quotes a value only when needed (QUOTE_MINIMAL)
Step 5 → Everything read is text; you convert to int / Decimal / date yourself
Step 6 → Rows are streamed one at a time → large files use little memory
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → File को newline="" के साथ खोलें (csv अपनी newline handling खुद करता है)
Step 2 → reader(fh) हर row को STRINGS की list की तरह देता है
Step 3 → DictReader पहली row को keys बनाता है: हर row एक dict
Step 4 → writer(fh).writerow(list) value को सिर्फ ज़रूरत पर quote करता है (QUOTE_MINIMAL)
Step 5 → जो भी पढ़ा जाता है वह text है; int / Decimal / date में खुद बदलें
Step 6 → Rows एक-एक करके आती हैं → बड़ी files में कम memory लगती है
```

---

## 🟡 Real World Example
A Razorpay finance team downloads a settlement CSV every day and a Python job reads it with `DictReader`, converts amounts to `Decimal`, and reports mismatches. A Zomato admin panel exports orders to CSV for the accountants. An AI team keeps labelled training samples in CSV and streams them into a loader.

## 🟡 Real Example Hindi mein
Razorpay की finance team रोज़ settlement CSV download करती है और Python job उसे `DictReader` से पढ़कर amounts को `Decimal` में बदलती है और mismatch बताती है। Zomato के admin panel से orders CSV में export होते हैं ताकि accountants उन्हें देख सकें। AI team labelled training samples CSV में रखती है और loader में stream करती है।

---

## 💻 Code Example — Basic
```python
# Basic csv examples - every line commented
import csv  # standard csv library
import io  # in-memory text files for the demo
import tempfile  # sandbox
from pathlib import Path  # paths

with tempfile.TemporaryDirectory() as tmp:  # sandbox
    f: Path = Path(tmp) / "people.csv"  # file path
    with f.open("w", newline="", encoding="utf-8") as fh:  # newline="" is REQUIRED for csv
        w = csv.writer(fh)  # row writer
        w.writerow(["name", "city", "salary"])  # header row
        w.writerow(["Asha", "Pune", 50000])  # numbers are converted to text
        w.writerows([["Ravi", "Delhi, NCR", 62000], ["Meera", 'He said "hi"', 45000]])  # many rows
    print(f.read_text(encoding="utf-8"))  # see the raw file (quotes added where needed)

    with f.open(newline="", encoding="utf-8") as fh:  # open for reading
        for row in csv.reader(fh):  # each row is a list of strings
            print(row)  # ['name', 'city', 'salary'] ...

    with f.open(newline="", encoding="utf-8") as fh:  # reopen
        for rec in csv.DictReader(fh):  # each row is a dict keyed by header
            print(rec["name"], int(rec["salary"]) + 1000)  # convert text to int yourself

    with f.open("w", newline="", encoding="utf-8") as fh:  # rewrite with DictWriter
        dw = csv.DictWriter(fh, fieldnames=["id", "ok"])  # fixed columns
        dw.writeheader()  # header line
        dw.writerow({"id": 1, "ok": True})  # dict row
    print(f.read_text(encoding="utf-8").splitlines())  # ['id,ok', '1,True']

data = io.StringIO("a;b\n1;2\n")  # semicolon separated text
print(list(csv.reader(data, delimiter=";")))  # custom delimiter
```

Output (verified by running; ids/timestamps/paths may vary):
```
name,city,salary
Asha,Pune,50000
Ravi,"Delhi, NCR",62000
Meera,"He said ""hi""",45000

['name', 'city', 'salary']
['Asha', 'Pune', '50000']
['Ravi', 'Delhi, NCR', '62000']
['Meera', 'He said "hi"', '45000']
Asha 51000
Ravi 63000
Meera 46000
['id,ok', '1,True']
[['a', 'b'], ['1', '2']]
```

## 💻 Code Example — Advanced
```python
# Production style: validation, streaming, dialect sniffing, injection guard, utf-8-sig
import csv  # csv library
import io  # in-memory files
from dataclasses import dataclass  # typed rows
from decimal import Decimal, InvalidOperation  # exact money
from typing import Dict, Iterator, List, Tuple  # type hints


@dataclass(frozen=True)
class Txn:
    txn_id: str  # id
    amount: Decimal  # money
    city: str  # text


def parse_txns(fh: io.TextIOBase) -> Iterator[Tuple[int, Txn]]:
    """Stream rows one by one; raise a clear error with the line number."""
    reader = csv.DictReader(fh)  # header based reader
    required = {"txn_id", "amount", "city"}  # columns we need
    if not required <= set(reader.fieldnames or []):  # header check
        raise ValueError(f"missing columns: {sorted(required - set(reader.fieldnames or []))}")
    for rec in reader:  # lazily, constant memory
        try:  # validate each row
            yield reader.line_num, Txn(rec["txn_id"].strip(), Decimal(rec["amount"]), rec["city"].strip())
        except (InvalidOperation, KeyError) as exc:  # bad value
            raise ValueError(f"line {reader.line_num}: bad row {rec}") from exc  # context


good = io.StringIO("txn_id,amount,city\nT1,199.90,Pune\nT2,50,\"Delhi, NCR\"\n")  # sample file
print([(n, t.txn_id, str(t.amount), t.city) for n, t in parse_txns(good)])  # parsed

try:  # bad amount
    list(parse_txns(io.StringIO("txn_id,amount,city\nT1,abc,Pune\n")))  # invalid decimal
except ValueError as exc:  # expected
    print("ValueError:", exc)  # message with line number

try:  # missing column
    list(parse_txns(io.StringIO("txn_id,city\nT1,Pune\n")))  # no amount column
except ValueError as exc:  # expected
    print("ValueError:", exc)  # message


def safe_cell(value: object) -> object:
    """Stop CSV/Excel formula injection: a cell starting with = + - @ runs as a formula."""
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@"):  # dangerous start
        return "'" + value  # neutralise with a leading quote
    return value  # normal value


out = io.StringIO()  # in-memory output
w = csv.writer(out, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")  # explicit line ending
w.writerow(["name", "note"])  # header
w.writerow(["Asha", safe_cell('=HYPERLINK("http://evil")')])  # sanitised user text
print(out.getvalue(), end="")  # show output

sample = "id|name\n1|Asha\n"  # unknown delimiter
dialect = csv.Sniffer().sniff(sample, delimiters=",;|\t")  # detect delimiter
print(repr(dialect.delimiter), list(csv.reader(io.StringIO(sample), dialect)))  # parse with it

raw: bytes = "﻿name,city\nAsha,Pune\n".encode("utf-8")  # Excel adds a BOM
print(list(csv.reader(io.StringIO(raw.decode("utf-8")))) [0])  # BOM sticks to first header
print(list(csv.reader(io.StringIO(raw.decode("utf-8-sig"))))[0])  # utf-8-sig removes the BOM

csv.field_size_limit(1_000_000)  # raise per-field limit for large cells (default 131072)
print(csv.field_size_limit())  # new limit
```

Output (verified by running; ids/timestamps/paths may vary):
```
[(2, 'T1', '199.90', 'Pune'), (3, 'T2', '50', 'Delhi, NCR')]
ValueError: line 2: bad row {'txn_id': 'T1', 'amount': 'abc', 'city': 'Pune'}
ValueError: missing columns: ['amount']
name,note
Asha,"'=HYPERLINK(""http://evil"")"
'|' [['id', 'name'], ['1', 'Asha']]
['\ufeffname', 'city']
['name', 'city']
1000000
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (standard library)
import csv
with open("a.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))      # [{'name': 'Asha', ...}, ...]
```

```javascript
// JavaScript (no built in CSV; use a package like csv-parse or papaparse)
import { parse } from "csv-parse/sync";
import fs from "node:fs";
const rows = parse(fs.readFileSync("a.csv", "utf-8"), { columns: true });
```

Key differences: Python ships `csv` in the standard library; JavaScript and Node need a package. Both return strings only, so you convert numbers yourself. Writing `line.split(",")` is wrong in both languages.

---

## 🟠 FastAPI Connection
FastAPI endpoints often export reports (`StreamingResponse` with `text/csv`) and import bulk data (`UploadFile`). Stream rows instead of building one giant string, wrap uploaded bytes with `io.TextIOWrapper(..., encoding="utf-8-sig")` to strip an Excel BOM, and validate every row (Pydantic) before saving.

```python
# FastAPI: export a CSV download and import a CSV upload (pip install fastapi httpx python-multipart)
import csv  # csv library
import io  # in-memory text
from typing import Dict, Iterator, List  # type hints
from fastapi import FastAPI, UploadFile  # app + upload
from fastapi.responses import StreamingResponse  # streamed download

app: FastAPI = FastAPI()  # create app
ROWS: List[Dict[str, object]] = [{"id": i, "name": f"user{i}"} for i in range(1, 4)]  # fake DB


def csv_lines() -> Iterator[str]:
    buf = io.StringIO()  # reusable buffer
    w = csv.DictWriter(buf, fieldnames=["id", "name"], lineterminator="\n")  # writer
    w.writeheader()  # header first
    yield buf.getvalue()  # send header
    for row in ROWS:  # stream rows
        buf.seek(0); buf.truncate(0)  # clear buffer
        w.writerow(row)  # write one row
        yield buf.getvalue()  # send it


@app.get("/export.csv")  # GET /export.csv
def export() -> StreamingResponse:
    return StreamingResponse(csv_lines(), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=users.csv"})


@app.post("/import")  # POST /import
def import_csv(file: UploadFile) -> Dict[str, int]:
    text = io.TextIOWrapper(file.file, encoding="utf-8-sig", newline="")  # decode bytes safely
    return {"rows": sum(1 for _ in csv.DictReader(text))}  # count data rows
```

Output (verified by running; ids/timestamps/paths may vary):
```
text/csv; charset=utf-8 'id,name\n1,user1\n2,user2\n3,user3\n'
{'rows': 2}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Opening without `newline=""`
```python
# Wrong - on Windows you get blank lines between rows, and quoted newlines break
# open("a.csv", "w")

# Correct
# open("a.csv", "w", newline="", encoding="utf-8")
```

❌ Mistake 2: Splitting manually and trusting types
```python
# Wrong - breaks on "Delhi, NCR"; and amount is still a str
# name, city, amount = line.split(",")
# total += amount            # TypeError / string concatenation

# Correct
# for rec in csv.DictReader(fh):
#     total += Decimal(rec["amount"])
```

❌ Mistake 3: Ignoring Excel quirks (BOM and formula injection)
```python
# Wrong - first header becomes '﻿name'; a user cell "=cmd|..." runs in Excel
# csv.DictReader(open("excel.csv", encoding="utf-8"))

# Correct
# open("excel.csv", newline="", encoding="utf-8-sig")   # strips the BOM
# prefix risky cells (= + - @) with a quote when exporting
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import csv, io
print(list(csv.reader(io.StringIO('a,"b,c",d\n'))))
print(list(csv.reader(io.StringIO('1,2\n\n3,4\n'))))
print(list(csv.DictReader(io.StringIO('x,y\n1\n1,2,3\n'))))
o = io.StringIO(); csv.writer(o).writerow([None, "", 0, "a\nb"]); print(repr(o.getvalue()))
```

**Answer**:
```
[['a', 'b,c', 'd']]
[['1', '2'], [], ['3', '4']]
[{'x': '1', 'y': None}, {'x': '1', 'y': '2', None: ['3']}]
',,0,"a\nb"\r\n'
```
A comma inside quotes is data, not a separator. A blank line becomes an empty list `[]` in `reader` (while `DictReader` skips fully blank rows). A short row gets `None` for missing columns (`restval`), and extra values are stored under the key `None` (`restkey`). `None` and `""` are both written as an empty field, and the default line ending of `writer` is `\r\n`. (Verified by running.)

---

## ⚫ Interview Questions + Answers

Q1: Why `newline=""` when opening CSV files?
A1: The `csv` module handles `\r\n` and newlines inside quoted cells itself. Without `newline=""`, Python's own translation corrupts them (blank rows on Windows, broken multi-line cells).

Q2: `reader` vs `DictReader`?
A2: `reader` gives lists by position; `DictReader` gives dicts by header name, so code survives column re-ordering. Use `DictReader` for named columns.

Q3: How do you handle a semicolon or tab separated file?
A3: `csv.reader(fh, delimiter=";")` or `"\t"`. `csv.Sniffer().sniff(sample)` can guess the delimiter, but explicit is safer.

Q4: `csv` vs `pandas.read_csv`?
A4: `csv` streams plain rows with tiny memory and no dependencies, and gives you strings. `pandas` infers types and is great for analysis but loads data into a DataFrame (heavier).

Q5: What is CSV injection?
A5: A cell that starts with `=`, `+`, `-` or `@` can be executed as a formula when opened in Excel. Sanitise user text before exporting (prefix with `'`).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Importing or exporting flat tables for spreadsheets and finance teams
- Streaming millions of rows with low memory
- You want zero dependencies

❌ Avoid when:
- Data is nested (use JSON)
- You need types and speed for analytics (use pandas/polars/Parquet)
- Values contain mixed encodings and you cannot control the source

---

## 📊 Visual Diagram

```
Text file                        csv.reader            csv.DictReader
name,city,salary                 ['name','city',..]    (header = keys)
Asha,Pune,50000      ──────►     ['Asha','Pune','50000']   {'name':'Asha','city':'Pune',...}
Ravi,"Delhi, NCR",62000          ['Ravi','Delhi, NCR',..]  {'name':'Ravi',...}
                                  ▲ quotes protect the comma
Everything is str → convert with int() / Decimal() / date.fromisoformat()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Delimiter | Character that separates columns | columns अलग करने वाला अक्षर |
| Quoting | Wrapping values in `"` when needed | ज़रूरत पर `"` में रखना |
| DictReader | Reader giving dict rows | dict rows देने वाला reader |
| BOM | Hidden marker at file start (Excel) | file की शुरुआत का छिपा निशान |
| Dialect | A set of format rules | format rules का समूह |
| CSV injection | Formula attack via cell text | cell text से formula attack |

---

## ⚡ 3-Line Summary
English: Use `csv.reader` / `DictReader` and `writer` / `DictWriter`, always with `newline=""`. Everything read is a string, so convert and validate. Guard against BOM and formula injection.
Hindi: `csv.reader` / `DictReader` और `writer` / `DictWriter` हमेशा `newline=""` के साथ इस्तेमाल करें। पढ़ा गया सब कुछ string है, इसलिए convert और validate करें। BOM और formula injection से बचें।

---

## ➡️ Next Topic
**192. datetime Module** — dates, times, time zones and the amounts of time between them.
