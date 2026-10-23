---

# 184. os Module + 186. pathlib — Complete Guide
# हिंदी में: os Module + pathlib — पूरी Guide

---

## 🔵 Simple Definition (English)
`os` module provides OS-level operations: file system, environment variables, process management. `pathlib` (Python 3.4+) provides an OOP interface to file paths — cleaner and preferred over `os.path`. Rule: use `pathlib.Path` for paths, `os.environ` for env vars, `os.getpid()` for process info. Both are cross-platform (Windows/Mac/Linux).

## 🔵 सरल परिभाषा (Hindi)
`os` module = OS-level operations: file system, env vars, process। `pathlib` = file paths का OOP interface — `os.path` से cleaner। Rule: paths के लिए `pathlib.Path`, env vars के लिए `os.environ`, process info के लिए `os.getpid()`। दोनों cross-platform हैं।

---

## 💻 Code Example — os Module
```python
import os

# ─── Environment variables ────────────────────────────────────────
# Read (returns None if not set):
api_key = os.environ.get("OPENAI_API_KEY")
api_key = os.getenv("OPENAI_API_KEY")   # same thing

# Read with default:
debug = os.getenv("DEBUG", "false").lower() == "true"
port = int(os.getenv("PORT", "8000"))

# Set (only affects current process and children):
os.environ["MY_VAR"] = "value"

# All env vars:
for key, value in os.environ.items():
    if "KEY" in key:
        print(f"{key}=***")    # redact secrets

# ─── Current directory ────────────────────────────────────────────
print(os.getcwd())        # current working directory
os.chdir("/tmp")          # change working directory (avoid in code!)

# ─── File system operations ───────────────────────────────────────
# List directory:
files = os.listdir(".")              # returns list of names (no paths)
files_paths = [os.path.join(".", f) for f in files]  # add path prefix

# Create/remove directories:
os.mkdir("new_dir")                  # create single directory
os.makedirs("path/to/nested", exist_ok=True)   # create nested
os.rmdir("empty_dir")               # remove EMPTY directory only
os.remove("file.txt")               # remove file

# Rename/move:
os.rename("old_name.txt", "new_name.txt")

# File info:
stat = os.stat("file.txt")
print(stat.st_size)   # size in bytes
print(stat.st_mtime)  # modification time (unix timestamp)

# ─── os.path — path manipulation ─────────────────────────────────
# Join paths (cross-platform):
path = os.path.join("data", "reports", "2024.csv")   # "data/reports/2024.csv"

# Split:
dir_name = os.path.dirname("/data/report.csv")   # "/data"
file_name = os.path.basename("/data/report.csv") # "report.csv"
name, ext = os.path.splitext("report.csv")        # ("report", ".csv")

# Check:
os.path.exists("file.txt")   # True if exists (file or dir)
os.path.isfile("file.txt")   # True only if file
os.path.isdir("mydir")       # True only if directory

# Absolute path:
abs_path = os.path.abspath("relative/path.txt")

# ─── Walk directory tree ──────────────────────────────────────────
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            full_path = os.path.join(root, file)
            print(full_path)
```

## 💻 Code Example — pathlib (Modern, Preferred)
```python
from pathlib import Path

# ─── Creating Path objects ────────────────────────────────────────
p = Path(".")                          # current directory
p = Path("/Users/priya/data")          # absolute path
p = Path.home()                        # home directory: /Users/priya
p = Path.cwd()                         # current working directory

# Join with / operator (cross-platform!):
config_path = Path("config") / "settings" / "prod.json"
print(config_path)   # config/settings/prod.json

# ─── Path properties ─────────────────────────────────────────────
p = Path("/Users/priya/data/report.csv")

print(p.name)         # "report.csv"
print(p.stem)         # "report" (name without extension)
print(p.suffix)       # ".csv" (extension with dot)
print(p.suffixes)     # [".csv"] (list — useful for .tar.gz)
print(p.parent)       # /Users/priya/data
print(p.parents[1])   # /Users/priya (grandparent)
print(p.parts)        # ('/', 'Users', 'priya', 'data', 'report.csv')
print(p.root)         # "/"
print(p.absolute())   # guaranteed absolute path

# ─── File operations ──────────────────────────────────────────────
p = Path("config.json")

# Read/write text:
p.write_text('{"key": "value"}', encoding="utf-8")
content = p.read_text(encoding="utf-8")

# Read/write bytes:
p.write_bytes(b"\x00\x01\x02")
data = p.read_bytes()

# ─── Check and create ────────────────────────────────────────────
p = Path("data/reports")

p.exists()                         # True if exists
p.is_file()                        # True if regular file
p.is_dir()                         # True if directory
p.mkdir(parents=True, exist_ok=True)   # create directory (nested OK)

# ─── Listing and searching ────────────────────────────────────────
base = Path(".")

# List immediate children:
for item in base.iterdir():
    print(item)

# Glob — find files by pattern:
for py_file in base.glob("*.py"):           # current dir only
    print(py_file)

for py_file in base.rglob("*.py"):          # recursive!
    print(py_file)

# rglob = recursive glob:
all_configs = list(Path(".").rglob("*.json"))
all_logs = list(Path("/var/log").rglob("*.log"))

# ─── Rename / move / delete ──────────────────────────────────────
p = Path("old_name.txt")
p.rename("new_name.txt")        # rename (must be same dir on some OS)
p.replace("new_location.txt")   # move/rename (replaces if dest exists)
p.unlink()                      # delete file
p.unlink(missing_ok=True)       # delete if exists, ignore if not
p.rmdir()                       # delete EMPTY directory

# ─── Real-world: find all Python files in project ────────────────
project_root = Path(".")
py_files = sorted(project_root.rglob("*.py"))
print(f"Found {len(py_files)} Python files")
for f in py_files[:5]:
    print(f"  {f.relative_to(project_root)}")

# ─── Path in FastAPI (loading static files) ──────────────────────
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# __file__ = path to current script
# parent = directory containing current script
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)))

# Load file relative to current script (reliable, not cwd):
def load_prompt_template(name: str) -> str:
    template_path = Path(__file__).parent / "prompts" / f"{name}.txt"
    return template_path.read_text(encoding="utf-8")
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python pathlib:
from pathlib import Path
config = Path(__file__).parent / "config" / "prod.json"
content = config.read_text()

# os.path (older):
import os
config = os.path.join(os.path.dirname(__file__), "config", "prod.json")
with open(config) as f:
    content = f.read()
```

```javascript
// Node.js path module:
import path from 'path';
import { readFileSync } from 'fs';

const configPath = path.join(__dirname, 'config', 'prod.json');
const content = readFileSync(configPath, 'utf8');

// Modern (import.meta.url):
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
```

Key similarities: both use `/` as separator in code (auto-converted on Windows). Both have `__file__`/`__dirname` for script-relative paths.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Hardcoded path separators
```python
# Wrong — breaks on Windows (\) vs Mac/Linux (/):
path = "data\\reports\\2024.csv"   # Windows-only!
path = "data/reports/2024.csv"     # Unix-only if Windows user

# Correct — use pathlib:
path = Path("data") / "reports" / "2024.csv"   # works everywhere
```

❌ Mistake 2: Using `os.getcwd()` to build paths instead of `__file__`
```python
# Wrong — breaks when script is run from different directory:
config = os.path.join(os.getcwd(), "config.json")   # fragile!

# Correct — path relative to the script itself:
config = Path(__file__).parent / "config.json"   # always works
```

---

## 🧠 Tricky Interview Question

**Q**: What is the difference between `Path.glob("*.py")` and `Path.rglob("*.py")`?

**Answer**: `glob("*.py")` searches only in the **current directory** — one level deep. `rglob("*.py")` is **recursive** — searches the directory and ALL subdirectories. `rglob("*.py")` is equivalent to `glob("**/*.py")`. The `**` pattern means "any number of directories." Important: `rglob` can be slow on large directory trees. For very large trees, use `os.walk()` or limit depth manually.

---

## ⚫ Interview Questions + Answers

Q1: How do you load environment variables in a FastAPI app?
A1: Use Pydantic Settings (recommended): `from pydantic_settings import BaseSettings; class Settings(BaseSettings): db_url: str; api_key: str = Field(alias="OPENAI_API_KEY")`. Auto-reads from env vars, validates types, raises on missing required vars. Can also load from `.env` file: `model_config = SettingsConfigDict(env_file=".env")`. In production: set actual env vars (never `.env` file in Docker/K8s). Get instance: `settings = Settings()` — call once at module level, reuse everywhere.

Q2: What does `Path(__file__).parent` give you?
A2: `__file__` is the absolute path to the current Python script being executed. `.parent` gives the directory containing that script. Example: if script is `/Users/priya/myapp/main.py`, then `Path(__file__).parent` = `/Users/priya/myapp`. Use it to build paths relative to your script — works regardless of what directory the script is run from. Very common in FastAPI: `templates_dir = Path(__file__).parent / "templates"`.

Q3: What is the difference between `os.makedirs()` and `Path.mkdir()`?
A3: `os.makedirs("a/b/c")` creates all intermediate directories. Without `exist_ok=True`: raises `FileExistsError` if any directory already exists. `Path("a/b/c").mkdir(parents=True, exist_ok=True)`: `parents=True` creates intermediate dirs, `exist_ok=True` suppresses error if already exists. For idiomatic modern Python: `Path("a/b/c").mkdir(parents=True, exist_ok=True)`. Always use `exist_ok=True` in production — concurrent processes might create the same directory.

Q4: How do you check free disk space with Python?
A4: `shutil.disk_usage("/")` returns `(total, used, free)` in bytes. Example: `total, used, free = shutil.disk_usage("/"); free_gb = free / (1024**3); print(f"Free: {free_gb:.1f} GB")`. For production monitoring: check in startup health check — alert if `free < threshold`. Use `psutil.disk_usage("/")` for more detailed info (percent used). Important for apps that write files: S3 upload queue, log rotation, temp file cleanup.

Q5: What is `os.environ` vs `os.getenv()` vs `os.environ.get()`?
A5: `os.environ` is a dict-like object. `os.environ["KEY"]` raises `KeyError` if missing. `os.getenv("KEY")` = `os.environ.get("KEY")` — returns `None` if missing. `os.getenv("KEY", "default")` = `os.environ.get("KEY", "default")` — returns default if missing. Best practice: `os.getenv("KEY")` for optional vars, `os.environ["KEY"]` where absence is a bug (fail fast). In FastAPI: use Pydantic Settings — it validates all env vars at startup rather than failing at random runtime points.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Path | OOP file path object | OOP file path object |
| os.environ | Environment variables dict | Environment variables |
| glob | Find files by pattern | Pattern से files ढूंढना |
| rglob | Recursive glob | Recursive glob |
| __file__ | Current script's path | Current script का path |
| makedirs | Create nested directories | Nested directories बनाना |
| exist_ok=True | No error if already exists | Already exist तो error नहीं |

---

## ⚡ 3-Line Summary
English: Use `pathlib.Path` for all path operations — `Path(__file__).parent / "file.json"` for script-relative paths, `/` operator for joining, `.rglob("*.py")` for recursive search. Use `os.getenv("KEY", "default")` for environment variables, never hardcode secrets. `Path.mkdir(parents=True, exist_ok=True)` is the modern way to create directories.
Hindi: Path operations के लिए `pathlib.Path` use करो। Script-relative paths: `Path(__file__).parent / "file.json"`। Env vars: `os.getenv("KEY", "default")`। Directories: `Path.mkdir(parents=True, exist_ok=True)`।

---

## ➡️ Next Topic
**190. json Module** — json.loads, json.dumps, custom encoders. **192. datetime Module** — timezone-aware datetimes. **199. Logging** — production logging setup.
