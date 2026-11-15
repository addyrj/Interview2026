---

# 188. glob Module
# हिंदी में: glob Module (pattern से files खोजना)

---

## 🔵 Simple Definition (English)
`glob` finds file and folder names that match a Unix shell style pattern such as `*.py`, `data?.csv` or `**/*.log`. It returns a list (`glob.glob`) or a lazy iterator (`glob.iglob`). It only matches names; it does not read file contents.

## 🔵 सरल परिभाषा (Hindi)
`glob` उन files और folders के नाम खोजता है जो Unix shell जैसे pattern से मिलते हों, जैसे `*.py`, `data?.csv` या `**/*.log`। यह list (`glob.glob`) या lazy iterator (`glob.iglob`) देता है। यह सिर्फ नाम match करता है, file के अंदर का content नहीं पढ़ता।

---

## 🔴 Problem it Solves
Before `glob`, you had to call `os.listdir`, loop, and filter names with string checks or regex. That is long and easy to get wrong, especially for nested folders. `glob` gives one readable pattern, e.g. `logs/2025-*/*.gz`, and handles directory walking for you.

## 🔴 यह क्यों बना? (Hindi)
`glob` से पहले `os.listdir`, loop और string/regex filter लिखना पड़ता था। यह लंबा है और nested folders में गलती आसान है। `glob` एक पढ़ने लायक pattern देता है, जैसे `logs/2025-*/*.gz`, और directory walking खुद संभालता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pattern is split into path parts at "/"
Step 2 → Parts with wildcards (* ? [..]) list the directory and filter names
Step 3 → "*" matches any chars, "?" one char, "[0-9]" one char of a set, "[!a]" not a
Step 4 → "**" matches any depth ONLY when recursive=True
Step 5 → Names starting with "." are skipped unless include_hidden=True (3.11+)
Step 6 → Result order is filesystem order (arbitrary) → sort it yourself
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Pattern "/" पर parts में बँट जाता है
Step 2 → जिस part में wildcard (* ? [..]) हो, उस directory को list करके names filter होते हैं
Step 3 → "*" कोई भी chars, "?" एक char, "[0-9]" set का एक char, "[!a]" a नहीं
Step 4 → "**" हर depth तभी match करता है जब recursive=True हो
Step 5 → "." से शुरू होने वाले नाम छोड़े जाते हैं (include_hidden=True हो तो 3.11+ में शामिल)
Step 6 → Result का order filesystem पर निर्भर है (तय नहीं) → खुद sort करें
```

---

## 🟡 Real World Example
A Zomato data team has `exports/2025-11-*/orders_*.csv.gz` created daily. One line of `glob` collects every file for the month before loading into the warehouse. A log cleaner finds `**/*.log` older than 7 days. An ML pipeline collects `images/*/*.jpg` to build a training list.

## 🟡 Real Example Hindi mein
Zomato की data team के पास रोज़ बनने वाली `exports/2025-11-*/orders_*.csv.gz` files हैं। `glob` की एक line warehouse में load करने से पहले महीने की सारी files इकट्ठा कर देती है। Log cleaner `**/*.log` में 7 दिन से पुरानी files खोजता है। ML pipeline training list के लिए `images/*/*.jpg` इकट्ठा करती है।

---

## 💻 Code Example — Basic
```python
# Basic glob examples - every line commented
import glob  # pattern based file search
import os  # chdir for the demo
import tempfile  # sandbox
from pathlib import Path  # create demo files

with tempfile.TemporaryDirectory() as tmp:  # sandbox folder
    base: Path = Path(tmp)  # root
    for name in ["a.py", "b.py", "notes.txt", "data1.csv", "data2.csv", "data10.csv", ".hidden.py"]:
        (base / name).write_text("x")  # create files
    (base / "sub").mkdir()  # sub folder
    (base / "sub" / "c.py").write_text("x")  # nested file
    os.chdir(base)  # patterns are relative to cwd

    print(sorted(glob.glob("*.py")))  # * = any chars; hidden files are skipped
    print(sorted(glob.glob("data?.csv")))  # ? = exactly one char
    print(sorted(glob.glob("data[0-9].csv")))  # [..] = one char from a set
    print(sorted(glob.glob("*.py", include_hidden=True)))  # include dot files (3.11+)
    print(sorted(glob.glob("*/*.py")))  # one folder deep
    print(sorted(glob.glob("**/*.py")))  # ** without recursive=True acts like *
    print(sorted(glob.glob("**/*.py", recursive=True)))  # ** now means any depth
    print(sorted(glob.glob("*.py", root_dir=base / "sub")))  # search in another dir (3.10+)
    print(glob.glob("*.nothing"))  # no match -> empty list, no error
    print(glob.escape("report[1].txt"))  # escape special chars for literal names
```

Output (verified by running; ids/timestamps/paths may vary):
```
['a.py', 'b.py']
['data1.csv', 'data2.csv']
['data1.csv', 'data2.csv']
['.hidden.py', 'a.py', 'b.py']
['sub/c.py']
['sub/c.py']
['a.py', 'b.py', 'sub/c.py']
['c.py']
[]
report[[]1].txt
```

## 💻 Code Example — Advanced
```python
# Production style: lazy search, natural sort, newest file, glob vs pathlib, translate (3.13)
import glob  # glob functions
import os  # utime and chdir
import re  # for natural sort
import tempfile  # sandbox
from pathlib import Path  # create demo files
from typing import Iterator, List, Optional  # type hints


def natural_key(name: str) -> List[object]:
    """Sort 'file2' before 'file10' by splitting digits from text."""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name)]  # mixed list


def newest(pattern: str, root: Path) -> Optional[Path]:
    """Return the most recently modified file matching pattern, or None."""
    files: List[str] = glob.glob(pattern, root_dir=root)  # relative names
    if not files:  # nothing found
        return None  # explicit None
    best: str = max(files, key=lambda f: (root / f).stat().st_mtime)  # latest mtime
    return root / best  # full path


def lazy_logs(root: Path) -> Iterator[str]:
    """Iterate huge folders without building a list."""
    yield from glob.iglob("**/*.log", root_dir=root, recursive=True)  # generator


with tempfile.TemporaryDirectory() as tmp:  # sandbox
    base: Path = Path(tmp)  # root
    for i in (1, 2, 10):  # three numbered files
        p: Path = base / f"report{i}.csv"  # name
        p.write_text("x")  # create
        os.utime(p, (1_000_000_000 + i, 1_000_000_000 + i))  # fake increasing mtime
    (base / "deep" / "er").mkdir(parents=True)  # nested folders
    (base / "deep" / "er" / "app.log").write_text("x")  # nested log
    (base / "top.log").write_text("x")  # top level log

    names: List[str] = glob.glob("report*.csv", root_dir=base)  # raw glob order is arbitrary
    print(sorted(names))  # plain sort: report1, report10, report2
    print(sorted(names, key=natural_key))  # natural sort: 1, 2, 10
    print(newest("report*.csv", base))  # newest by mtime -> report10
    print(newest("*.xlsx", base))  # no match -> None
    print(sorted(lazy_logs(base)))  # lazy generator, sorted for display

    print(sorted(p.name for p in base.glob("report*.csv")))  # pathlib equivalent, returns Paths
    print(type(glob.iglob("*")).__name__)  # iglob is an iterator, not a list

print(glob.translate("**/*.py", recursive=True, include_hidden=False))  # 3.13+: pattern -> regex
```

Output (verified by running; ids/timestamps/paths may vary):
```
['report1.csv', 'report10.csv', 'report2.csv']
['report1.csv', 'report2.csv', 'report10.csv']
/var/folders/8q/198sl3md25x9fpmg5jwxlm4c0000gn/T/tmpz2koj0vw/report10.csv
None
['deep/er/app.log', 'top.log']
['report1.csv', 'report10.csv', 'report2.csv']
generator
(?s:(?:[^/.][^/]*/)*(?!\.)[^/]*\.py)\Z
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import glob
files = sorted(glob.glob("src/**/*.py", recursive=True))   # built in
for name in glob.iglob("*.csv"):                           # lazy
    print(name)
```

```javascript
// JavaScript (Node.js 22+ has fs.glob; older projects use the "glob"/"fast-glob" package)
import { glob } from "node:fs/promises";
for await (const f of glob("src/**/*.js")) console.log(f);   // async iterator
// import fg from "fast-glob"; const files = await fg("src/**/*.js");
```

Key differences: In Python, `glob` has been in the standard library forever and is synchronous. In Node it was a third party package for years; the built in version is newer and async. Python needs `recursive=True` for `**`; Node's patterns treat `**` as recursive by default.

---

## 🟠 FastAPI Connection
FastAPI services sometimes list files (reports, models, exports) with `glob`. The danger is user input inside the pattern: `*` or `../` can expose other files. Validate the input with a strict `Query(pattern=...)` and wrap it with `glob.escape()`.

```python
# FastAPI: list available report files by pattern (pip install fastapi httpx)
import glob  # pattern search
import tempfile  # demo folder
from pathlib import Path  # paths
from typing import Dict, List  # type hints
from fastapi import FastAPI, Query  # app + validation

REPORT_DIR: Path = Path(tempfile.mkdtemp())  # real app: a configured folder
for n in ("sales_2025-01.csv", "sales_2025-02.csv", "refunds_2025-01.csv"):
    (REPORT_DIR / n).write_text("x")  # demo files
app: FastAPI = FastAPI()  # create app


@app.get("/reports")  # GET /reports?prefix=sales
def reports(prefix: str = Query("sales", pattern=r"^[a-z]+$")) -> Dict[str, List[str]]:
    # pattern validation stops users sending '*' or '../' into glob
    found: List[str] = sorted(glob.glob(f"{glob.escape(prefix)}_*.csv", root_dir=REPORT_DIR))
    return {"files": found}  # JSON list of names
```

Output (verified by running; ids/timestamps/paths may vary):
```
{'files': ['sales_2025-01.csv', 'sales_2025-02.csv']}
{'files': ['refunds_2025-01.csv']}
422
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting `**` to be recursive by default
```python
# Wrong - ** acts like * without recursive=True
glob.glob("**/*.py")                    # misses top level and deep files

# Correct
glob.glob("**/*.py", recursive=True)    # includes top level and all depths
```

❌ Mistake 2: Relying on the result order
```python
# Wrong - order is arbitrary (depends on filesystem)
first = glob.glob("*.csv")[0]

# Correct
first = sorted(glob.glob("*.csv"))[0]
```

❌ Mistake 3: Forgetting hidden files and special characters
```python
# Wrong - ".env.py" is skipped, and "[1]" in a real file name is read as a pattern
glob.glob("*.py")
glob.glob("report[1].txt")              # will NOT match a file literally named "report[1].txt"

# Correct
glob.glob("*.py", include_hidden=True)  # 3.11+
glob.glob(glob.escape("report[1].txt"))
```

---

## 🧠 Tricky Interview Question

**Q**: Folder has `a.py`, `.b.py`, `c.txt` and a folder `d/` containing `e.py`. What is the output?

```python
import glob
print(sorted(glob.glob("*")))
print(sorted(glob.glob("**/*.py")))
print(sorted(glob.glob("**/*.py", recursive=True)))
print(sorted(glob.glob("[!a]*")))
```

**Answer**:
```
['a.py', 'c.txt', 'd']
['d/e.py']
['a.py', 'd/e.py']
['c.txt', 'd']
```
Hidden `.b.py` never appears because `*` does not match a leading dot. Without `recursive=True`, `**` is just `*`, so `**/*.py` means "one folder level, then .py" and misses `a.py`. With it, `**` also matches zero folders. `[!a]*` means "does not start with a", and `.b.py` is still hidden. (Verified by running.)

---

## ⚫ Interview Questions + Answers

Q1: `glob.glob` vs `glob.iglob`?
A1: `glob` builds a full list in memory. `iglob` returns an iterator and yields matches one by one, which is better for huge folders.

Q2: Is `glob` a regex?
A2: No. It uses shell wildcard syntax (`*`, `?`, `[seq]`, `[!seq]`) via `fnmatch`. Curly braces like `{a,b}` are not supported.

Q3: `glob.glob` or `Path.glob`?
A3: `glob.glob` returns strings, `Path.glob` returns `Path` objects and is relative to that path. Both are fine; `pathlib` is nicer in new code. `root_dir=` (3.10+) lets `glob.glob` search another folder without `chdir`.

Q4: How do you match a file whose name contains `[` or `*`?
A4: Use `glob.escape(name)` before passing it as the pattern.

Q5: What is new in Python 3.13 for glob?
A5: `glob.translate(pattern, recursive=..., include_hidden=...)` converts a glob pattern into a regular expression string.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Selecting files by simple name patterns
- Batch jobs: all CSVs of a month, all logs, all images
- You want a quick one-line search without writing a walker

❌ Avoid when:
- You need filtering by size, date or content (use `os.scandir` / `Path.stat`)
- Patterns come straight from users (validate and escape)
- You need complex rules (use `re` on `Path.rglob("*")`)

---

## 📊 Visual Diagram

```
pattern:  logs/2025-*/app_?.log
            │     │        │
   folder "logs" │        └── ? = exactly one char
                 └── * = any characters

recursive=True:   src/**/*.py
   src/a.py            ✔ (** = zero folders)
   src/x/b.py          ✔
   src/x/y/c.py        ✔
   src/.hidden/d.py    ✖ (hidden unless include_hidden=True)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Wildcard | Special char in a pattern (`*`, `?`) | pattern का खास अक्षर |
| `**` | Any depth of folders (needs recursive) | किसी भी गहराई के folders |
| iglob | Lazy version of glob | lazy glob |
| root_dir | Folder in which to search (3.10+) | जहाँ खोजना है वो folder |
| escape | Make special chars literal | खास अक्षरों को सामान्य बनाना |
| Hidden file | Name starting with a dot | "." से शुरू होने वाली file |

---

## ⚡ 3-Line Summary
English: `glob` finds paths by shell wildcards (`*`, `?`, `[..]`, `**`). Use `recursive=True` for `**`, `iglob` for huge folders, `sorted()` for a stable order, and `escape()` plus validation for user input.
Hindi: `glob` shell wildcards (`*`, `?`, `[..]`, `**`) से paths खोजता है। `**` के लिए `recursive=True`, बड़े folders के लिए `iglob`, stable order के लिए `sorted()` और user input के लिए `escape()` व validation इस्तेमाल करें।

---

## ➡️ Next Topic
**189. tempfile Module** — create safe temporary files and folders for the results of searches and processing.
