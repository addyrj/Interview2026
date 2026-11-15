---

# Q196. Build CSV to JSON Converter
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `csv_to_json(text)` that converts CSV text (first row = headers) to a JSON array of objects. Handle quoted commas (`"Delhi, IN"`), infer ints/floats/booleans, and turn empty cells into `null`.

```python
csv_to_json('name,age\nAditya,25')   # [{"name": "Aditya", "age": 25}]
```

---

## 💡 Quick Concept (2 lines only)
Use `csv.DictReader` (handles quotes, escapes, newlines) and `json.dumps`. Never `split(",")` — it breaks on quoted commas.
हिंदी: `csv.DictReader` quotes और commas सही संभालता है; `split(",")` से कभी CSV parse मत करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import csv  # csv parsing
import io  # in-memory file
import json  # output
from typing import Any  # type hints

def infer(v: str) -> Any:
    if v == "":
        return None  # empty -> null
    for cast in (int, float):  # try int then float
        try:
            return cast(v)  # numeric
        except ValueError:
            pass  # try next
    if v.lower() in ("true", "false"):
        return v.lower() == "true"  # boolean
    return v  # plain string

def csv_to_json(text: str, infer_types: bool = True, indent: int | None = 2) -> str:
    rows = csv.DictReader(io.StringIO(text))  # header row -> dict keys; handles quotes/commas
    data = [{k: infer(v) if infer_types else v for k, v in row.items()} for row in rows]  # convert values
    return json.dumps(data, indent=indent)  # serialize

# ============================================
# TEST CASES
# ============================================
text = 'name,age,city,active\nAditya,25,"Delhi, IN",true\nRavi,,Mumbai,false\n'  # sample CSV with quoted comma
print(csv_to_json(text, indent=None))  # Expected: [{"name": "Aditya", "age": 25, "city": "Delhi, IN", "active": true}, {"name": "Ravi", "age": null, "city": "Mumbai", "active": false}]
print(csv_to_json("a,b\n1,2.5", infer_types=False, indent=None))  # Expected: [{"a": "1", "b": "2.5"}]
```

---

## 🔍 Why This Works (3 lines max)
`DictReader` maps each row to the header names and correctly parses quoted fields. `StringIO` lets us treat a string as a file. `infer` tries int, then float, then bool, falling back to the original string.
हिंदी: `DictReader` header से dict बनाता है; `StringIO` string को file जैसा बनाता है; `infer` types पहचानता है।

---

## ⚡ Alternative Solution
```python
# Manual split approach (breaks on quoted commas!) vs csv module
text = 'name,city\nAditya,"Delhi, IN"\n'  # quoted comma
lines = text.strip().split("\n")  # lines
header = lines[0].split(",")  # header
naive = [dict(zip(header, l.split(","))) for l in lines[1:]]  # naive split
print(naive)  # Expected: [{'name': 'Aditya', 'city': '"Delhi'}]   (wrong)
import csv, io  # the right tool
print(list(csv.DictReader(io.StringIO(text))))  # Expected: [{'name': 'Aditya', 'city': 'Delhi, IN'}]   (right)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: split(",") and eager type guessing (not run)
# row = line.split(",")                 # "Delhi, IN" is cut in two
# if v.isdigit(): int(v)                # fails for "-5" and "2.5"; leading zeros ("007") lose meaning

# ✅ Correct: csv module for parsing; be careful inferring types for IDs/zip codes ("007", "0123")
#             (keep them as strings) and open real files with newline="" and encoding="utf-8".
```

---

## 🎯 Interview Tip (1 line)
Say: "Use the csv module, not split; for huge files stream rows with a generator instead of loading everything."

---

## 🔗 Related Questions
→ Q116 (json.dumps) | Q117 (json.loads) | Q220 (stream large data with async generators) | Q249 (pathlib)
