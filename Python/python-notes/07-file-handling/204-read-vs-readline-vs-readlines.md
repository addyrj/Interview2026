---

# 204. read() vs readline() vs readlines()
# हिंदी में: read() बनाम readline() बनाम readlines()

---

## 🔵 Simple Definition (English)
`read()` returns the whole file (or N characters) as one string. `readline()` returns one line at a time. `readlines()` returns a list of all lines. For big files, the best choice is none of them: loop directly over the file object (`for line in f`), which reads lazily.

## 🔵 सरल परिभाषा (Hindi)
`read()` पूरी file (या N characters) एक string में देता है। `readline()` एक बार में एक line देता है। `readlines()` सभी lines की list देता है। बड़ी files के लिए इनमें से कोई नहीं, बल्कि सीधे `for line in f` बेहतर है, जो lazily पढ़ता है।

---

## 🔴 Problem it Solves
Files come in all sizes. A 5 KB config can be read in one call, but a 5 GB log file loaded with `read()` crashes the server with `MemoryError` or gets it killed. Python gives different read methods so you choose between convenience (all at once) and memory safety (one line or chunk at a time).

## 🔴 यह क्यों बना? (Hindi)
Files अलग-अलग size की होती हैं। 5 KB की config एक call में पढ़ सकते हैं, पर 5 GB की log file `read()` से लोड करने पर server crash या kill हो सकता है। Python अलग-अलग read methods देता है ताकि आप सुविधा (सब एक साथ) और memory safety (एक line या chunk) में से चुन सकें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Opening a file puts a "cursor" (position) at the start
Step 2 → read()        : returns from cursor to END, cursor moves to end
Step 3 → read(n)       : returns n characters, cursor moves n forward
Step 4 → readline()    : returns up to and including the next "\n"
Step 5 → readlines()   : repeats readline() and collects results in a list
Step 6 → At the end of file, all methods return empty ('' or [] ), not an error
Step 7 → for line in f : asks for one line per loop turn (memory stays tiny)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → file खुलने पर cursor शुरुआत में होता है
Step 2 → read() cursor से अंत तक सब देता है, cursor अंत में चला जाता है
Step 3 → read(n) n characters देता है
Step 4 → readline() अगली "\n" तक (उसके साथ) एक line देता है
Step 5 → readlines() सभी lines की list बनाता है
Step 6 → file के अंत पर खाली मिलता है ('' या []), error नहीं
Step 7 → for line in f हर चक्र में एक line देता है (memory बहुत कम)
```

---

## 🟡 Real World Example
Swiggy's ops team scans a 3 GB nginx access log for lines with status 500: they loop `for line in f` and count. Razorpay reads a small 2 KB `config.txt` with `read()`. A RAG pipeline reads a PDF's bytes in 1 MB chunks with `read(n)`. A CSV importer calls `readline()` once to get the header, then loops for the rows.

## 🟡 Real Example Hindi mein
Swiggy की ops team 3 GB की nginx access log में status 500 वाली lines गिनने के लिए `for line in f` चलाती है। Razorpay 2 KB की `config.txt` `read()` से पढ़ता है। RAG pipeline PDF के bytes 1 MB chunks में `read(n)` से पढ़ती है। CSV importer पहले `readline()` से header लेता है, फिर बाकी rows पर loop चलाता है।

---

## 💻 Code Example — Basic
```python
# read vs readline vs readlines - every line commented
import tempfile  # temp folder
from pathlib import Path  # paths

d: Path = Path(tempfile.mkdtemp())  # temporary directory
p: Path = d / "r.txt"  # sample file
p.write_text("alpha\nbeta\ngamma", encoding="utf-8")  # 3 lines, last has no \n

with open(p, encoding="utf-8") as f:  # open for reading
    print(repr(f.read()))  # whole file as ONE string
# Output: 'alpha\nbeta\ngamma'

with open(p, encoding="utf-8") as f:  # reopen: cursor back at start
    print(repr(f.read(3)), repr(f.read(3)))  # read 3 characters, then next 3
# Output: 'alp' 'ha\n'

with open(p, encoding="utf-8") as f:  # reopen
    print(repr(f.readline()), repr(f.readline()))  # one line each call (keeps \n)
    print(repr(f.readline()), repr(f.readline()))  # third line, then end of file
# Output: 'alpha\n' 'beta\n'
# Output: 'gamma' ''

with open(p, encoding="utf-8") as f:  # reopen
    print(f.readlines())  # list of lines, \n included
# Output: ['alpha\n', 'beta\n', 'gamma']

with open(p, encoding="utf-8") as f:  # reopen
    print([line.rstrip("\n") for line in f])  # iterate + strip newline
# Output: ['alpha', 'beta', 'gamma']

with open(p, encoding="utf-8") as f:  # reopen
    print(f.read().splitlines())  # another way to get lines without \n
# Output: ['alpha', 'beta', 'gamma']

with open(p, encoding="utf-8") as f:  # cursor behaviour
    f.read()  # cursor moves to the end
    print(repr(f.read()), f.readlines())  # nothing left: empty results, no error
# Output: '' []
    f.seek(0)  # go back to the start
    print(f.tell(), f.readline(3))  # position 0; readline(3) reads max 3 characters
# Output: 0 alp
```

## 💻 Code Example — Advanced
```python
# Production style: lazy line loop, chunk reader, tail of a file, memory proof
import tempfile  # temp folder
import tracemalloc  # measure peak memory
from collections import deque  # fixed-size queue
from pathlib import Path  # paths
from typing import Iterator, List  # type hints


def count_errors(path: Path) -> int:
    """Count ERROR lines using constant memory."""
    total: int = 0  # counter
    with open(path, encoding="utf-8") as fh:  # open once
        for line in fh:  # file object is a lazy iterator
            if "ERROR" in line:  # simple filter
                total += 1  # count
    return total  # result


def read_chunks(path: Path, size: int = 1024 * 1024) -> Iterator[bytes]:
    """Yield binary chunks; works for any file, even without newlines."""
    with open(path, "rb") as fh:  # binary
        while chunk := fh.read(size):  # empty bytes ends the loop (walrus, 3.8+)
            yield chunk  # hand one chunk at a time


def last_n_lines(path: Path, n: int) -> List[str]:
    """Like `tail -n`: keep only the last n lines in memory."""
    with open(path, encoding="utf-8") as fh:  # open
        return list(deque(fh, maxlen=n))  # older lines are dropped automatically


d: Path = Path(tempfile.mkdtemp())  # temp folder
log: Path = d / "log.txt"  # log file
log.write_text("INFO a\nERROR b\nERROR c\n", encoding="utf-8")  # sample log
print(count_errors(log))  # two ERROR lines
# Output: 2

sample: Path = d / "r.txt"  # another file
sample.write_text("alpha\nbeta\ngamma", encoding="utf-8")  # content
print(list(read_chunks(sample, 8)))  # 8-byte pieces
# Output: [b'alpha\nbe', b'ta\ngamma']
print(last_n_lines(sample, 2))  # last 2 lines
# Output: ['beta\n', 'gamma']

# Memory proof: 200,000 lines
big: Path = d / "big.txt"  # big file
with open(big, "w", encoding="utf-8") as out:  # create it
    for i in range(200_000):  # many lines
        out.write(f"line {i}\n")  # one line each

tracemalloc.start()  # start tracking Python memory
with open(big, encoding="utf-8") as fh:  # lazy way
    n: int = sum(1 for _ in fh)  # count lines
lazy_peak: int = tracemalloc.get_traced_memory()[1]  # peak bytes
tracemalloc.reset_peak()  # reset the peak (3.9+)
with open(big, encoding="utf-8") as fh:  # eager way
    lines: List[str] = fh.readlines()  # everything in a list
eager_peak: int = tracemalloc.get_traced_memory()[1]  # peak bytes
tracemalloc.stop()  # stop tracking
print(n, lazy_peak < 200_000, eager_peak > 5_000_000)  # lazy < 200 KB, eager > 5 MB
# Output: 200000 True True
```
Verified on Python 3.13.3; exact byte counts for memory vary by machine.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python way
with open("log.txt", encoding="utf-8") as f:
    for line in f:                 # lazy, one line at a time
        print(line.rstrip())
text = open("log.txt", encoding="utf-8").read()   # whole file
```
```javascript
// JavaScript way (Node.js)
import { readFileSync, createReadStream } from "node:fs";
import readline from "node:readline";
const text = readFileSync("log.txt", "utf-8");           // whole file (like read())
const lines = text.split("\n");                           // like readlines()
const rl = readline.createInterface({ input: createReadStream("log.txt") });
for await (const line of rl) console.log(line);           // lazy, one line at a time
```

Key differences: In Python the file object is itself the line iterator, so one `for` loop is enough. In Node you need `readline` + a stream for lazy lines. Python keeps the trailing `\n` in each line; JS `split("\n")` removes it.

---

## 🟠 FastAPI Connection
For a big file download, do not `read()` it in an endpoint: return `FileResponse` or a `StreamingResponse` fed by a generator that yields chunks. A log-tail endpoint can use `deque(f, maxlen=n)`.

```python
# FastAPI: stream a big file in chunks (pip install fastapi)
import tempfile  # temp folder
from pathlib import Path  # paths
from typing import Iterator  # type hints
from fastapi import FastAPI  # framework
from fastapi.responses import StreamingResponse  # streaming

app: FastAPI = FastAPI()  # app
FILE: Path = Path(tempfile.mkdtemp()) / "big.txt"  # demo file
FILE.write_text("".join(f"row {i}\n" for i in range(5)), encoding="utf-8")  # sample data


def iter_file(path: Path, size: int = 64 * 1024) -> Iterator[bytes]:
    with open(path, "rb") as fh:  # binary
        while chunk := fh.read(size):  # 64 KB at a time
            yield chunk  # send piece


@app.get("/download")  # GET /download
def download() -> StreamingResponse:
    return StreamingResponse(iter_file(FILE), media_type="text/plain")  # constant memory
# (Not executed as a server in this note; iter_file logic is identical to read_chunks above, which was run.)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `read()` or `readlines()` on a huge file
✅ Correct:

```python
# Wrong - loads gigabytes into RAM
lines = open("huge.log").readlines()
# Right - lazy loop
with open("huge.log", encoding="utf-8") as f:
    for line in f:
        ...
```

❌ Mistake 2: Forgetting the trailing `\n`
✅ Correct:

```python
# Wrong - 'ERROR\n' != 'ERROR'
if line == "ERROR": ...
# Right
if line.rstrip("\n") == "ERROR": ...
```

❌ Mistake 3: Reading twice without `seek(0)`
✅ Correct:

```python
# Wrong - second read returns '' because the cursor is at the end
text1 = f.read(); text2 = f.read()
# Right
text1 = f.read(); f.seek(0); text2 = f.read()
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
# file content: "alpha\nbeta\ngamma"
with open("r.txt") as f:
    print(repr(f.readline()))
    print(f.readlines())
    print(f.readlines())
with open("r.txt") as f:
    next(f)
    try:
        f.tell()
    except OSError as e:
        print("OSError:", e)
```

**Answer**:
```
'alpha\n'
['beta\n', 'gamma']
[]
OSError: telling position disabled by next() call
```
The cursor is shared, so `readlines()` continues after the first line and the second call finds nothing (`[]`, not an error). In text mode, using the iterator protocol (`next(f)` or `for line in f`) disables `tell()` until you call `seek()`. (Message verified on Python 3.13.)

---

## ⚫ Interview Questions + Answers

Q1: Which is best for a 10 GB log?
A1: `for line in f` (or `read(n)` in chunks for binary). It uses constant memory.

Q2: What do these return at end of file?
A2: `read()` -> `''`, `readline()` -> `''`, `readlines()` -> `[]`. Never an exception.

Q3: Does `readline()` keep the newline?
A3: Yes. A blank line in the file returns `'\n'`, while `''` means end of file.

Q4: What does `readlines(hint)` do?
A4: It stops after reading lines totalling about `hint` bytes/characters: `readlines(8)` on our sample returns `['alpha\n', 'beta\n']`.

Q5: What is the difference between `f.read().splitlines()` and `f.readlines()`?
A5: `splitlines()` removes the line endings, `readlines()` keeps them. Both load the whole file into memory.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- `read()`: small files (config, template, JSON text)
- `readline()`: header row, or manual line-by-line control
- `for line in f`: logs, CSV-like data, large text
- `read(n)`: chunks of binary or very long single-line files

❌ Avoid when:
- `read()`/`readlines()` on files bigger than free memory
- `readlines()` just to loop (a `for` loop on `f` does the same lazily)
- Mixing `next(f)` and `tell()` without `seek`

---

## 📊 Visual Diagram

```
file:  a l p h a \n b e t a \n g a m m a
       ^cursor
read()       -> everything                  cursor -> END
read(3)      -> "alp"                       cursor -> after 'p'
readline()   -> "alpha\n"                   cursor -> start of "beta"
readlines()  -> ["alpha\n","beta\n","gamma"]
for line in f -> one line per loop turn (lazy, tiny memory)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cursor | Current read/write position | file में वर्तमान position |
| Lazy | Load only when needed | ज़रूरत पर ही load |
| Chunk | Fixed-size piece of data | तय size का टुकड़ा |
| EOF | End of file | file का अंत |
| Iterator | Object giving items one by one | एक-एक item देने वाला object |
| seek / tell | Move / read the cursor | cursor हिलाना / देखना |

---

## ⚡ 3-Line Summary
English: `read()` gets everything, `readline()` one line, `readlines()` a list; all return empty at end of file. For large files iterate `for line in f` or read chunks. The cursor is shared, so re-reading needs `seek(0)`.
Hindi: `read()` सब कुछ देता है, `readline()` एक line, `readlines()` list; file के अंत पर सब खाली लौटाते हैं। बड़ी files के लिए `for line in f` या chunks इस्तेमाल करें। Cursor साझा है, इसलिए दोबारा पढ़ने के लिए `seek(0)` चाहिए।

---

## ➡️ Next Topic
**205. write() vs writelines()** — writing strings and lists of strings, and the missing-newline trap.
