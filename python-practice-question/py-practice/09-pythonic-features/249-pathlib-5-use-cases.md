---

# Q249. pathlib — 5 Use Cases
# Category: Pythonic + Modern Python Features
# Difficulty: ⭐ Easy

---

## ❓ Question
Show 5 everyday `pathlib.Path` use cases: build paths with `/`, read/write files, inspect name/suffix/parent, glob files, and create/delete directories.

---

## 💡 Quick Concept (2 lines only)
`Path` is an object-oriented replacement for `os.path` string juggling: `/` joins, `.read_text()` reads, `.glob()` searches. Works on Windows and Linux.
हिंदी: `pathlib.Path` = file paths को objects की तरह use करो — `/` से join, `.read_text()` से पढ़ो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import tempfile                                       # safe temp dir so nothing is left behind
from pathlib import Path                              # Step 1: import Path

with tempfile.TemporaryDirectory() as tmp:            # auto-deleted on exit
    base = Path(tmp)                                  # Use case 1: wrap a directory

    f = base / "notes" / "todo.txt"                   # build path with the / operator
    f.parent.mkdir(parents=True, exist_ok=True)       # Use case 5: make dirs (like mkdir -p)

    f.write_text("buy milk\nlearn python\n")          # Use case 2: write a text file
    print(f.read_text().splitlines())                 # Expected: ['buy milk', 'learn python']

    print(f.name, f.stem, f.suffix, f.parent.name)    # Use case 3: Expected: todo.txt todo .txt notes
    print(f.exists(), f.is_file(), f.is_dir())        # Expected: True True False

    (base / "notes" / "a.py").touch()                 # create empty files
    (base / "notes" / "b.py").touch()                 # another one
    names = sorted(p.name for p in (base / "notes").glob("*.py"))  # Use case 4: glob
    print(names)                                      # Expected: ['a.py', 'b.py']

    all_files = sorted(p.name for p in base.rglob("*") if p.is_file())  # recursive search
    print(all_files)                                  # Expected: ['a.py', 'b.py', 'todo.txt']

    # ============================================
    # TEST CASES
    # ============================================
    print(f.with_suffix(".md").name)                  # Expected: todo.md
    print(f.relative_to(base))                        # Expected: notes/todo.txt (notes\todo.txt on Windows)
    f.unlink()                                        # delete the file
    print(f.exists())                                 # Expected: False
```

---

## 🔍 Why This Works (3 lines max)
`Path` overloads `/` so joins are OS-independent, and methods like `read_text`, `glob`, `mkdir` replace many `os`/`open` calls. `exist_ok=True` + `parents=True` makes `mkdir` idempotent.
हिंदी: `/` operator OS के हिसाब से सही separator लगाता है — `mkdir(parents=True, exist_ok=True)` बार-बार safe है।

---

## ⚡ Alternative Solution
```python
# Same job with the old os.path style (more verbose)
import os                                             # old module
import tempfile                                       # temp dir

with tempfile.TemporaryDirectory() as tmp:            # auto cleanup
    path = os.path.join(tmp, "notes", "todo.txt")     # string join
    os.makedirs(os.path.dirname(path), exist_ok=True) # make folders
    with open(path, "w") as fh:                       # open for writing
        fh.write("hi")                                # write text
    print(os.path.basename(path), os.path.splitext(path)[1])  # Expected: todo.txt .txt
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: building paths with string concatenation (breaks on Windows)
# path = base + "/" + "notes" + "/" + "todo.txt"

# ❌ Wrong: Path.read_text() on a missing file -> FileNotFoundError
# ✅ Correct: use `/` and check .exists() (or catch FileNotFoundError)
from pathlib import Path                              # import
print(Path("a") / "b" / "c.txt")                      # Expected: a/b/c.txt
```

---

## 🎯 Interview Tip (1 line)
Say: "I prefer pathlib over os.path: `/` for joins, `.read_text()`/`.write_text()` for small files, `.glob()` for searching, and `mkdir(parents=True, exist_ok=True)`."

---

## 🔗 Related Questions
→ Q119 (context manager class) | Q253 (contextlib) | Q257 (string method tricks) | Q181 (real-world file tasks)
