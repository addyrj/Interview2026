---

# 207. CSV File Handling
# हिंदी में: CSV File Handling (csv module से table data)

---

## 🔵 Simple Definition (English)
CSV (Comma-Separated Values) is a plain-text table format: one row per line, columns split by a delimiter. Python's `csv` module reads and writes it correctly, handling quotes, commas inside values and line breaks. Always open CSV files with `newline=""`.

## 🔵 सरल परिभाषा (Hindi)
CSV (Comma-Separated Values) plain-text table format है: हर line एक row, columns delimiter से अलग। Python का `csv` module इसे सही तरह पढ़ता-लिखता है, यानी quotes, value के अंदर के commas और line breaks भी संभालता है। CSV file हमेशा `newline=""` के साथ खोलें।

---

## 🔴 Problem it Solves
Splitting a line with `line.split(",")` breaks when a value contains a comma (`Ravi, "RK"`) or a line break. Excel, bank statements and reports are exchanged as CSV, so you need a parser that follows the quoting rules (RFC 4180 style). The `csv` module gives that, plus dict-based access by column name.

## 🔴 यह क्यों बना? (Hindi)
`line.split(",")` तब टूट जाता है जब value में comma (`Ravi, "RK"`) या line break हो। Excel, bank statements और reports CSV में ही आते-जाते हैं, इसलिए ऐसा parser चाहिए जो quoting नियम समझे। `csv` module यही देता है, साथ में column name से dict-based access भी।

---

## 🟢 How it Works — Step by Step

```
Step 1 → open(path, newline="", encoding="utf-8")   (newline="" is REQUIRED)
Step 2 → csv.reader(f)      -> each row is a list of strings
Step 3 → csv.DictReader(f)  -> first row = header, each row is a dict
Step 4 → csv.writer(f).writerow(list) / writerows(list_of_lists)
Step 5 → csv.DictWriter(f, fieldnames=[...]) -> writeheader() then writerow(dict)
Step 6 → Everything read is a STRING: convert with int(), float(), Decimal()
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → open(path, newline="", encoding="utf-8")   (newline="" ज़रूरी है)
Step 2 → csv.reader(f) हर row को strings की list में देता है
Step 3 → csv.DictReader(f) पहली row को header मानकर हर row dict में देता है
Step 4 → csv.writer(f).writerow(list) / writerows(list_of_lists)
Step 5 → csv.DictWriter(f, fieldnames=[...]) -> writeheader() फिर writerow(dict)
Step 6 → पढ़ी गई हर value STRING होती है: int(), float(), Decimal() से बदलें
```

---

## 🟡 Real World Example
Razorpay merchants download a settlement CSV every morning, and the finance team's script reads it with `DictReader` to reconcile amounts. Swiggy exports restaurant payouts as CSV for Excel. An AI team keeps an evaluation set as `questions.csv` (question, expected_answer) and loops over it to test a chatbot.

## 🟡 Real Example Hindi mein
Razorpay merchants हर सुबह settlement CSV download करते हैं और finance team की script उसे `DictReader` से पढ़कर amounts मिलाती है। Swiggy restaurant payouts को Excel के लिए CSV में export करता है। AI team evaluation set `questions.csv` (question, expected_answer) में रखकर chatbot को test करने के लिए उस पर loop चलाती है।

---

## 💻 Code Example — Basic
```python
# CSV basics - every line commented
import csv  # standard library
import tempfile  # temp folder
from pathlib import Path  # paths

d: Path = Path(tempfile.mkdtemp())  # temporary directory
p: Path = d / "o.csv"  # CSV file path
rows = [  # header + 3 data rows
    ["id", "name", "amount"],  # header
    [1, "Aditya", 250.5],  # normal row
    [2, 'Ravi, "RK"', 100],  # comma and quotes inside a value
    [3, "Line\nbreak", 0],  # newline inside a value
]

with open(p, "w", newline="", encoding="utf-8") as f:  # newline="" avoids blank lines on Windows
    writer = csv.writer(f)  # create writer
    writer.writerows(rows)  # write all rows at once
print(repr(p.read_text(encoding="utf-8")))  # see the quoting the module added
# Output: 'id,name,amount\n1,Aditya,250.5\n2,"Ravi, ""RK""",100\n3,"Line\nbreak",0\n'
# (writer uses \r\n line endings by default; read_text() shows them as \n)

with open(p, newline="", encoding="utf-8") as f:  # read it back
    for row in csv.reader(f):  # each row is a list of strings
        print(row)  # print it
# Output: ['id', 'name', 'amount']
# Output: ['1', 'Aditya', '250.5']
# Output: ['2', 'Ravi, "RK"', '100']
# Output: ['3', 'Line\nbreak', '0']

with open(p, newline="", encoding="utf-8") as f:  # DictReader: access by column name
    reader = csv.DictReader(f)  # header becomes the keys
    print(reader.fieldnames)  # column names
    # Output: ['id', 'name', 'amount']
    for row in reader:  # each row is a dict
        print(dict(row))  # plain dict
# Output: {'id': '1', 'name': 'Aditya', 'amount': '250.5'}
# Output: {'id': '2', 'name': 'Ravi, "RK"', 'amount': '100'}
# Output: {'id': '3', 'name': 'Line\nbreak', 'amount': '0'}

import io  # in-memory text file for quick tests
print(list(csv.reader(io.StringIO("a;b;c\n1;2;3"), delimiter=";")))  # custom delimiter
# Output: [['a', 'b', 'c'], ['1', '2', '3']]
print(sum(int(x) for x in next(csv.reader(io.StringIO("1,2,3")))))  # values are str -> convert
# Output: 6
```

## 💻 Code Example — Advanced
```python
# Production style: typed rows, bad-row handling, BOM, DictWriter rules
import csv  # csv module
import io  # in-memory files
import tempfile  # temp folder
from dataclasses import dataclass  # typed record
from pathlib import Path  # paths
from typing import Iterator  # type hints


@dataclass
class Txn:
    id: int  # transaction id
    amount: float  # amount (use Decimal for real money)
    status: str  # normalised status


def load_txns(path: Path) -> Iterator[Txn]:
    """Stream rows lazily, skip bad rows, never load the whole file."""
    with open(path, newline="", encoding="utf-8-sig") as fh:  # utf-8-sig removes Excel's BOM
        for line_no, row in enumerate(csv.DictReader(fh), start=2):  # header is line 1
            try:  # convert strings to real types
                yield Txn(int(row["id"]), float(row["amount"]), row["status"].strip().lower())
            except (KeyError, ValueError) as exc:  # missing column or bad number
                print(f"line {line_no} skipped: {exc!r}")  # in production use logging


d: Path = Path(tempfile.mkdtemp())  # temp folder
src: Path = d / "t.csv"  # input file
src.write_text("id,amount,status\n1,10.5, PAID \nx,5,paid\n3,,failed\n4,7,ok\n", encoding="utf-8")
print(list(load_txns(src)))  # only valid rows remain
# Output: line 3 skipped: ValueError("invalid literal for int() with base 10: 'x'")
# Output: line 4 skipped: ValueError("could not convert string to float: ''")
# Output: [Txn(id=1, amount=10.5, status='paid'), Txn(id=4, amount=7.0, status='ok')]

# DictWriter: extra keys raise an error unless extrasaction="ignore"
out: Path = d / "out.csv"  # output path
with open(out, "w", newline="", encoding="utf-8") as f:  # open
    w = csv.DictWriter(f, fieldnames=["id", "name"], extrasaction="ignore")  # ignore unknown keys
    w.writeheader()  # header row
    w.writerow({"id": 1, "name": "A", "zzz": 5})  # "zzz" is dropped
    w.writerow({"id": 2})  # missing key becomes empty (restval="")
print(repr(out.read_text()))  # check
# Output: 'id,name\n1,A\n2,\n'

try:  # default extrasaction="raise"
    with open(out, "w", newline="") as f:  # open
        csv.DictWriter(f, fieldnames=["id"]).writerow({"id": 1, "x": 2})  # extra key
except ValueError as exc:  # ValueError
    print("ValueError:", exc)  # message
# Output: ValueError: dict contains fields not in fieldnames: 'x'

# The BOM problem: plain utf-8 keeps an invisible character in the first header
bom: Path = d / "bom.csv"  # file from Excel
bom.write_bytes("﻿id,name\n1,A\n".encode("utf-8"))  # starts with BOM
print(csv.DictReader(open(bom, encoding="utf-8")).fieldnames)  # wrong key '﻿id'
# Output: ['﻿id', 'name']
print(csv.DictReader(open(bom, encoding="utf-8-sig")).fieldnames)  # correct
# Output: ['id', 'name']

# Quoting options and delimiter guessing
buf = io.StringIO()  # in-memory file
csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\n").writerow([1, "a", None])  # quote all
print(repr(buf.getvalue()))  # None becomes an empty string
# Output: '"1","a",""\n'
print(csv.Sniffer().sniff("a;b;c\n1;2;3\n").delimiter)  # guess the delimiter
# Output: ;

# Field size limit protects memory (default 131072 characters)
try:  # a huge single field
    list(csv.reader(io.StringIO("a" * 200000)))  # too large
except csv.Error as exc:  # csv.Error
    print("csv.Error:", exc)  # message
# Output: csv.Error: field larger than field limit (131072)
```
Verified on Python 3.13.3. Use `Decimal` instead of `float` for real money values.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python way
import csv
with open("data.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):       # dict per row, header = keys
        print(row["name"], float(row["amount"]))
```
```javascript
// JavaScript way (no built-in CSV parser)
// npm install csv-parse   (or papaparse)
import { parse } from "csv-parse/sync";
import { readFileSync } from "node:fs";
const rows = parse(readFileSync("data.csv", "utf-8"), { columns: true });   // like DictReader
for (const row of rows) console.log(row.name, parseFloat(row.amount));
// Naive text.split(",") breaks on quoted commas - same bug as in Python
```

Key differences: Python ships the `csv` module in the standard library; Node needs a package (`csv-parse`, `papaparse`). Both give strings only, so you convert numbers yourself.

---

## 🟠 FastAPI Connection
A common endpoint accepts a CSV upload (`UploadFile`), parses it with `csv.DictReader` over a text wrapper, and validates each row with Pydantic. Another endpoint streams a CSV export with `StreamingResponse`.

```python
# FastAPI: CSV upload and validation (pip install fastapi python-multipart)
import csv  # csv module
import io  # to wrap the byte stream as text
from typing import Dict, List  # type hints
from fastapi import FastAPI, UploadFile  # framework
from pydantic import BaseModel, ValidationError  # row validation

app: FastAPI = FastAPI()  # app


class Row(BaseModel):  # expected row shape
    id: int  # whole number
    amount: float  # number


@app.post("/import")  # POST /import
def import_csv(file: UploadFile) -> Dict[str, object]:
    text = io.TextIOWrapper(file.file, encoding="utf-8-sig", newline="")  # bytes -> text
    good: List[Row] = []  # valid rows
    bad: List[int] = []  # failed line numbers
    for n, raw in enumerate(csv.DictReader(text), start=2):  # line 1 is the header
        try:  # validate
            good.append(Row(**raw))  # pydantic converts "10.5" -> 10.5
        except ValidationError:  # bad data
            bad.append(n)  # remember line number
    return {"imported": len(good), "bad_lines": bad}  # summary
# Tested with TestClient: CSV "id,amount / 1,10.5 / x,2 / 3,4" -> {"imported": 2, "bad_lines": [3]}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Splitting with `split(",")`
✅ Correct:

```python
# Wrong - breaks on 2,"Ravi, RK",100
parts = line.split(",")
# Right
row = next(csv.reader([line]))
```

❌ Mistake 2: Forgetting `newline=""`
✅ Correct:

```python
# Wrong - on Windows you get blank lines between rows, and embedded newlines break
open("o.csv", "w")
# Right
open("o.csv", "w", newline="", encoding="utf-8")
```

❌ Mistake 3: Treating values as numbers
✅ Correct:

```python
# Wrong - "10" + "5" == "105", and "9" > "10" is True (string compare)
total = row["amount"] + row2["amount"]
# Right
total = float(row["amount"]) + float(row2["amount"])
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import csv, io
data = 'name,city\n"Ravi, K",Delhi\n'
print(data.splitlines()[1].split(","))
print(list(csv.reader(io.StringIO(data)))[1])
print(list(csv.DictReader(io.StringIO(data)))[0]["city"])
print(list(csv.reader(io.StringIO("1,2.5,True")))[0])
```

**Answer**:
```
['"Ravi', ' K"', 'Delhi']
['Ravi, K', 'Delhi']
Delhi
['1', '2.5', 'True']
```
Plain `split` cuts inside the quotes and leaves stray quote characters. `csv.reader` understands quoting. Every value read from a CSV is a `str`, even numbers and `True`.

---

## ⚫ Interview Questions + Answers

Q1: Why `newline=""`?
A1: The `csv` module handles line endings itself. Without it, Python's newline translation can add extra `\r` (blank lines on Windows) or break newlines inside quoted fields.

Q2: `reader` vs `DictReader`?
A2: `reader` gives lists (positional), `DictReader` gives dicts keyed by header (clearer, order-independent). `DictReader` rows are plain dicts since Python 3.8.

Q3: How to handle a big CSV?
A3: Iterate the reader lazily and process row by row, or in batches. Do not `list()` it. For heavy analytics use pandas `read_csv(chunksize=...)`.

Q4: How do you read Excel-exported UTF-8 CSV?
A4: Use `encoding="utf-8-sig"` to drop the BOM, otherwise the first header becomes `'﻿id'`.

Q5: CSV vs JSON?
A5: CSV is flat, compact, Excel friendly, all strings. JSON is nested and typed (numbers, booleans, null). Use CSV for tables, JSON for APIs.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Importing/exporting flat tables (finance, reports, datasets)
- Interchange with Excel or Google Sheets
- Streaming large row-based files

❌ Avoid when:
- Data is nested (use JSON)
- You need types and schema guarantees (Parquet, DB)
- Heavy filtering and joins (pandas or SQL)

---

## 📊 Visual Diagram

```
file text:   id,name,amount\r\n
             2,"Ravi, ""RK""",100\r\n
                 |
          csv.reader
                 v
   ['id','name','amount']
   ['2','Ravi, "RK"','100']      all values are str
                 |
          csv.DictReader
                 v
   {'id':'2','name':'Ravi, "RK"','amount':'100'}
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Delimiter | Character separating columns | columns अलग करने वाला character |
| Quoting | Wrapping values in " " | values को " " में लपेटना |
| DictReader | Reader giving dict rows | dict rows देने वाला reader |
| BOM | Invisible mark at file start | file की शुरुआत का छिपा निशान |
| utf-8-sig | Encoding that removes BOM | BOM हटाने वाली encoding |
| Header | First row with column names | column names वाली पहली row |

---

## ⚡ 3-Line Summary
English: Use `csv.reader/DictReader` and `csv.writer/DictWriter`, always with `newline=""` and an explicit encoding. Everything read is a string, so convert and validate. Use `utf-8-sig` for Excel files.
Hindi: `csv.reader/DictReader` और `csv.writer/DictWriter` इस्तेमाल करें, हमेशा `newline=""` और explicit encoding के साथ। पढ़ी गई हर value string है, इसलिए convert और validate करें। Excel files के लिए `utf-8-sig` लगाएँ।

---

## ➡️ Next Topic
**208. JSON File Handling** — `json.load`, `json.dump` and handling dates, errors and big files.
