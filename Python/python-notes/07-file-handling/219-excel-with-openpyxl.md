---

# 219. Excel with openpyxl
# हिंदी में: Excel with openpyxl (.xlsx files बनाना और पढ़ना)

---

## 🔵 Simple Definition (English)
`openpyxl` is a third-party library (`pip install openpyxl`) to read and write modern Excel `.xlsx` files without needing Excel installed. You work with a Workbook, its Worksheets and Cells, and can add formulas, styles, column widths and multiple sheets.

## 🔵 सरल परिभाषा (Hindi)
`openpyxl` एक third-party library है (`pip install openpyxl`) जिससे Excel installed हुए बिना `.xlsx` files पढ़ी और लिखी जा सकती हैं। आप Workbook, उसकी Worksheets और Cells के साथ काम करते हैं, और formulas, styles, column widths व कई sheets जोड़ सकते हैं।

---

## 🔴 Problem it Solves
Business users live in Excel: finance wants monthly reports, ops wants bulk uploads. CSV cannot hold multiple sheets, formatting, formulas or number formats, and copying data by hand is slow and error-prone. `openpyxl` lets a Python service generate polished spreadsheets and import user-edited ones automatically.

## 🔴 यह क्यों बना? (Hindi)
Business users Excel में काम करते हैं: finance को monthly reports चाहिए, ops को bulk upload। CSV में कई sheets, formatting, formulas या number formats नहीं रख सकते, और हाथ से data copy करना धीमा और गलत होता है। `openpyxl` से Python service सुंदर spreadsheets अपने-आप बना सकती है और users की edit की हुई sheets import कर सकती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Workbook() creates a workbook with one sheet; wb.active is that sheet
Step 2 → ws.append([...]) adds a row; ws['A1'] = value sets a cell
Step 3 → Formulas are stored as text ("=SUM(B2:B9)") and calculated when Excel opens the file
Step 4 → Style cells: Font, PatternFill, Alignment, number_format, column width
Step 5 → wb.save(path_or_BytesIO) writes the .xlsx (a zip of XML files)
Step 6 → load_workbook(path, data_only=True, read_only=True) reads values back
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Workbook() एक sheet वाला workbook बनाता है; wb.active वही sheet है
Step 2 → ws.append([...]) row जोड़ता है; ws['A1'] = value cell सेट करता है
Step 3 → Formulas text के रूप में store होते हैं ("=SUM(B2:B9)") और Excel में खोलने पर calculate होते हैं
Step 4 → Cells style करो: Font, PatternFill, Alignment, number_format, column width
Step 5 → wb.save(path_or_BytesIO) .xlsx लिखता है (असल में XML files की zip)
Step 6 → load_workbook(path, data_only=True, read_only=True) से values वापस पढ़ो
```

---

## 🟡 Real World Example
A Zomato finance tool exports the monthly restaurant payout as a styled Excel report with totals. An HR portal lets recruiters upload a candidate sheet and validates every row before inserting into the database. A FastAPI endpoint returns an `.xlsx` download of the filtered orders table.

## 🟡 Real Example Hindi mein
Zomato का finance tool monthly restaurant payout को totals वाली styled Excel report के रूप में export करता है। HR portal में recruiters candidates की sheet upload करते हैं और database में डालने से पहले हर row validate होती है। FastAPI endpoint filter किए गए orders table का `.xlsx` download देता है।

---

## 💻 Code Example — Basic
```python
import tempfile, os
from openpyxl import Workbook, load_workbook
wb = Workbook()  # new workbook
ws = wb.active  # first sheet
ws.title = "Sales"
ws.append(["Item", "Qty", "Price"])  # header row
ws.append(["Pen", 10, 5.5])
ws.append(["Book", 3, 120])
ws["D1"] = "Total"
ws["D2"] = "=B2*C2"  # formulas are stored as text
ws["D3"] = "=B3*C3"
ws.cell(row=4, column=1, value="Sum")
ws["D4"] = "=SUM(D2:D3)"
ws2 = wb.create_sheet("Notes")
ws2["A1"] = "hello"
d = tempfile.mkdtemp(); p = os.path.join(d, "s.xlsx")
wb.save(p)
print(wb.sheetnames)
wb2 = load_workbook(p)  # formulas as text
print(wb2["Sales"]["D2"].value)
wb3 = load_workbook(p, data_only=True)  # cached values - none, never opened in Excel
print(wb3["Sales"]["D2"].value)
for row in wb2["Sales"].iter_rows(min_row=2, max_col=3, values_only=True):
    print(row)
print(ws.max_row, ws.max_column, ws.dimensions)
```

**Real output** (Python 3.13.3):
```
['Sales', 'Notes']
=B2*C2
None
('Pen', 10, 5.5)
('Book', 3, 120)
('Sum', None, None)
4 4 A1:D4
```

Notes: `data_only=True` returns the value Excel last CACHED for a formula. A file created by openpyxl was never opened in Excel, so the cache is empty and you get `None`. openpyxl does not calculate formulas.

## 💻 Code Example — Advanced
```python
from __future__ import annotations
import tempfile
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from typing import Iterable

Row = tuple[str, int, float]


def write_report(path: Path, rows: Iterable[Row]) -> int:
    wb = Workbook(write_only=False)
    ws = wb.active
    ws.title = "Orders"
    ws.append(["Customer", "Qty", "Amount"])
    for c in ws[1]:  # style header
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="305496")
        c.alignment = Alignment(horizontal="center")
    n = 0
    for r in rows:
        ws.append(list(r)); n += 1
    for cell in ws["C"][1:]:
        cell.number_format = '#,##0.00'
    ws.freeze_panes = "A2"
    for i, col in enumerate(ws.columns, 1):  # auto width
        ws.column_dimensions[get_column_letter(i)].width = max(len(str(c.value or "")) for c in col) + 2
    ws.append(["Total", f"=SUM(B2:B{n+1})", f"=SUM(C2:C{n+1})"])
    wb.save(path)
    return n


def read_report(path: Path) -> list[dict[str, object]]:
    wb = load_workbook(path, read_only=True, data_only=True)  # streaming read
    try:
        ws = wb["Orders"]
        it = ws.iter_rows(values_only=True)
        header = next(it)
        return [dict(zip(header, r)) for r in it if r[0] != "Total"]
    finally:
        wb.close()


with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "r.xlsx"
    print(write_report(p, [("Asha", 2, 1999.5), ("Ravi", 1, 250.0)]))
    print(read_report(p))
    wb = load_workbook(p)
    print(wb["Orders"].freeze_panes, wb["Orders"]["A1"].font.b, wb["Orders"]["C3"].number_format)
    try:
        load_workbook(Path(d) / "none.xlsx")
    except FileNotFoundError:
        print("FileNotFoundError")
    bad = Path(d) / "bad.xlsx"; bad.write_text("not a zip")
    try:
        load_workbook(bad)
    except Exception as e:
        print(type(e).__name__)
```

**Real output** (Python 3.13.3):
```
2
[{'Customer': 'Asha', 'Qty': 2, 'Amount': 1999.5}, {'Customer': 'Ravi', 'Qty': 1, 'Amount': 250}]
A2 True #,##0.00
FileNotFoundError
BadZipFile
```

`read_only=True` streams rows with low memory (use for big files); `write_only=True` is the same idea for huge exports. An integer-valued float such as `250.0` comes back as `250` because Excel stores one number type.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
from openpyxl import Workbook, load_workbook
wb = Workbook(); ws = wb.active
ws.append(["Item", "Qty"]); ws.append(["Pen", 10])
wb.save("a.xlsx")
rows = list(load_workbook("a.xlsx").active.iter_rows(values_only=True))
```

```javascript
// JavaScript (npm i exceljs)
const ExcelJS = require("exceljs");
const wb = new ExcelJS.Workbook();
const ws = wb.addWorksheet("Sheet1");
ws.addRow(["Item", "Qty"]); ws.addRow(["Pen", 10]);
await wb.xlsx.writeFile("a.xlsx");
// or SheetJS: XLSX.utils.aoa_to_sheet([...])
```

The APIs are very similar (workbook, worksheet, row, cell). Node uses `exceljs` or SheetJS; Python also has `pandas.DataFrame.to_excel` (uses openpyxl underneath) and `xlsxwriter` (write-only, great formatting). Excel dates are numbers formatted as dates, so check `number_format` in both.

---

## 🟠 FastAPI Connection
FastAPI Excel export: build the workbook in `io.BytesIO`, `seek(0)` and return a `StreamingResponse` with the xlsx media type and `Content-Disposition: attachment`. For uploads, read `UploadFile` into `BytesIO` and open with `load_workbook(..., read_only=True)`; validate every row and cap size.

```python
import io
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient
from openpyxl import Workbook, load_workbook
app = FastAPI()
@app.get("/export.xlsx")
def export() -> StreamingResponse:
    wb = Workbook(); ws = wb.active; ws.append(["id", "amount"]); ws.append([1, 99.5])
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": 'attachment; filename="export.xlsx"'})
c = TestClient(app); r = c.get("/export.xlsx")
print(r.status_code, load_workbook(io.BytesIO(r.content)).active["B2"].value)
```

**Real output** (Python 3.13.3):
```
200 99.5
```


---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting formula results from openpyxl
```python
# Wrong - None, because nothing calculated the formula yet
ws["D2"] = "=B2*C2"
print(load_workbook(p, data_only=True).active["D2"].value)   # None

# Right - compute in Python as well, or open/save once with Excel/LibreOffice
ws["D2"] = qty * price
```

❌ Mistake 2: Loading a huge file normally
```python
# Wrong - 1 million rows can use gigabytes of RAM
wb = load_workbook("big.xlsx")

# Right
wb = load_workbook("big.xlsx", read_only=True)
for row in wb.active.iter_rows(values_only=True): ...
wb.close()            # read_only workbooks keep the file open
```

❌ Mistake 3: Supporting the old .xls format or trusting file extension
```python
# Wrong - openpyxl cannot open .xls (Excel 97-2003)
load_workbook("old.xls")      # InvalidFileException

# Right - convert to .xlsx first, or use pandas with xlrd for .xls
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from openpyxl import Workbook
ws = Workbook().active
ws["A1"] = 1
print(ws.max_row); _ = ws["A100"]; print(ws.max_row)
ws["B1"] = "=1+1"; print(ws["B1"].value, ws["B1"].data_type)
ws["C1"] = "007"; print(ws["C1"].value, ws["C1"].data_type)
ws["D1"] = 5; ws["E1"] = 5.0; print(type(ws["D1"].value).__name__, ws["E1"].data_type)
```

**Answer** (real run on Python 3.13.3):
```
1
100
=1+1 f
007 s
int n
```
Just READING `ws['A100']` creates the cell, so `max_row` jumps to 100 (use `iter_rows` or `ws.cell` carefully on big sheets). Formulas are stored with `data_type 'f'`; the text `'007'` stays a string `'s'` (leading zeros kept), while numbers become `int`/`float`.

---

## ⚫ Interview Questions + Answers

Q1: openpyxl vs pandas vs xlsxwriter?
A1: pandas: quick tables (`df.to_excel`), uses openpyxl/xlsxwriter underneath. openpyxl: read AND write, edit existing files, styles. xlsxwriter: write-only, fast, rich formatting and charts.

Q2: How do you read a large Excel file?
A2: `load_workbook(path, read_only=True, data_only=True)` and iterate `iter_rows(values_only=True)`; close the workbook after.

Q3: How do you read computed formula values?
A3: Use `data_only=True`, but values exist only if the file was saved by Excel/LibreOffice. openpyxl never evaluates formulas.

Q4: How do you write dates correctly?
A4: Assign a `datetime`/`date` object and set `cell.number_format = 'DD-MM-YYYY'`. Excel stores dates as serial numbers.

Q5: Is openpyxl safe for uploads?
A5: It parses XML inside a zip, so limit upload size, avoid untrusted macros (`.xlsm`/`keep_vba` off), and be aware of XML bomb style files; the `defusedxml` package is used automatically if installed.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Business users want formatted Excel reports
- You import spreadsheets that users fill in
- You must edit an existing .xlsx and keep its styles

❌ Avoid when:
- A plain CSV is enough (simpler and much faster)
- You need charts with full control (xlsxwriter) or formula evaluation
- Files are huge and you do not use read_only/write_only mode

---

## 📊 Visual Diagram

```
Workbook (report.xlsx = zip of XML)
 |-- Worksheet "Orders"
 |     A1 "Customer" | B1 "Qty" | C1 "Amount"   <- header (bold, fill)
 |     A2 "Asha"     | B2 2     | C2 1999.5
 |     A4 "Total"    | B4 =SUM(B2:B3)             <- text formula
 +-- Worksheet "Notes"

write: wb.save()      read: load_workbook(read_only=True, data_only=True)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Workbook | The whole Excel file | पूरी Excel file |
| Worksheet | One tab/sheet | एक sheet/tab |
| Cell | One box, like B2 | एक खाना, जैसे B2 |
| Formula | Text starting with = | = से शुरू होने वाला text |
| read_only | Low-memory streaming read | कम memory में streaming read |
| number_format | How a number/date looks | number/date कैसा दिखे |

---

## ⚡ 3-Line Summary
English: `openpyxl` creates, edits and reads `.xlsx` files: append rows, style cells, add formulas (not evaluated), and use `read_only=True` for big files. In FastAPI save the workbook into `BytesIO` and stream it.
Hindi: `openpyxl` `.xlsx` files बनाता, edit करता और पढ़ता है: rows append करें, cells style करें, formulas जोड़ें (calculate नहीं होते), और बड़ी files के लिए `read_only=True` लें। FastAPI में workbook को `BytesIO` में save करके stream करें।

---

## ➡️ Next Topic
**220. PDF Handling Basics** — extract text, merge and split PDFs with pypdf.
