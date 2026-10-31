---

# 076. Array Module
# हिंदी में: Array Module (Typed Numbers का Compact Array)

---

## 🔵 Simple Definition (English)
`array.array` is a sequence that stores only numbers of ONE fixed type (like all ints or all floats) in a compact C-style memory block. It looks like a list but uses much less memory because it stores raw numbers, not full Python objects.

## 🔵 सरल परिभाषा (Hindi)
`array.array` ऐसी sequence है जो सिर्फ एक fixed type के numbers (सब int या सब float) एक compact C-style memory block में रखती है। यह list जैसी दिखती है, लेकिन बहुत कम memory लेती है क्योंकि इसमें raw numbers होते हैं, पूरे Python objects नहीं।

---

## 🔴 Problem it Solves
A Python `list` of 1 million ints stores 1 million pointers plus 1 million separate int objects (about 8 + 28 bytes each). That is heavy. For plain numeric data (sensor readings, audio samples, pixel values) you need compact storage and an easy way to read/write binary files. NumPy solves this too, but it is a big external dependency; `array` is built in.

## 🔴 यह क्यों बना? (Hindi)
10 लाख ints की Python `list` में 10 लाख pointers और 10 लाख अलग int objects होते हैं (हर एक करीब 8 + 28 bytes)। यह भारी है। सिर्फ numbers वाले data (sensor readings, audio samples, pixel values) के लिए compact storage और binary file में आसानी से read/write चाहिए। NumPy भी यह करता है, पर वो बड़ी external dependency है; `array` built-in है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You choose a type code: "i" (int), "d" (double float), "H" (unsigned short)...
Step 2 → array("i", [1,2,3]) allocates ONE contiguous memory block
Step 3 → Each item takes exactly itemsize bytes (4 bytes for "i")
Step 4 → Values are stored raw (no Python object per item)
Step 5 → Adding a wrong type or too big a value raises TypeError / OverflowError
Step 6 → tofile() / fromfile() / tobytes() move data to/from binary files fast

list:   [ptr][ptr][ptr] -> int obj, int obj, int obj  (scattered)
array:  [01 00 00 00][02 00 00 00][03 00 00 00]       (one block)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप type code चुनते हैं: "i" (int), "d" (float), "H" (unsigned short)...
Step 2 → array("i", [1,2,3]) एक ही contiguous memory block लेता है
Step 3 → हर item exactly itemsize bytes लेता है ("i" के लिए 4 bytes)
Step 4 → Values raw रूप में रखी जाती हैं (हर item का Python object नहीं)
Step 5 → गलत type या बहुत बड़ी value पर TypeError / OverflowError
Step 6 → tofile() / fromfile() / tobytes() से binary data तेजी से आता-जाता है
```

---

## 🟡 Real World Example
An IoT service collects temperature readings every second from 10,000 devices and keeps the last hour in memory as `array("d")` instead of lists of floats. An audio app stores 16-bit samples as `array("h")`. A game server stores player scores as `array("i")` and dumps the whole thing to a binary snapshot file with `tofile()`.

## 🟡 Real Example Hindi mein
IoT service 10,000 devices से हर second temperature readings लेती है और पिछला एक घंटा floats की list की जगह `array("d")` में memory में रखती है। Audio app 16-bit samples `array("h")` में रखती है। Game server players के scores `array("i")` में रखता है और `tofile()` से पूरा data binary snapshot file में डाल देता है।

---

## 💻 Code Example — Basic
```python
# Basic array module examples
from array import array                   # import the array class

a: array = array("i", [1, 2, 3])          # "i" = signed int, 4 bytes each
a.append(4)                               # add one item at the end
a.extend([5, 6])                          # add many items
print(a, a.typecode, a.itemsize)          # array, type code, bytes per item
print(a[1], a[1:3], len(a))               # indexing, slicing, length work like list

try:                                      # type is enforced
    a.append(1.5)                         # float into an int array
except TypeError as e:                    # catch the error
    print("TypeError:", e)                # explains why it failed

print(a.tolist(), a.tobytes()[:8])        # back to list, and raw bytes of 2 items
a.reverse()                               # in-place reverse like list
print(a)                                  # reversed array
print(array("d", [1.5, 2.5]))             # "d" = double (64-bit float)

# Output:
# array('i', [1, 2, 3, 4, 5, 6]) i 4
# 2 array('i', [2, 3]) 6
# TypeError: 'float' object cannot be interpreted as an integer
# [1, 2, 3, 4, 5, 6] b'\x01\x00\x00\x00\x02\x00\x00\x00'
# array('i', [6, 5, 4, 3, 2, 1])
# array('d', [1.5, 2.5])
```

## 💻 Code Example — Advanced
```python
# Production style: memory saving, binary file save/load, overflow handling
import sys                                # to measure object size
import tempfile                           # temp folder for the demo
from array import array                   # compact typed array
from pathlib import Path                  # file paths


def to_array(values: list[int]) -> array:
    """Convert a list of ints to a compact int array."""
    return array("i", values)             # raises on non-int values


def save_array(arr: array, path: Path) -> None:
    """Write raw array bytes to a binary file."""
    with path.open("wb") as f:            # open for binary writing
        arr.tofile(f)                     # fast dump, no loop needed


def load_array(path: Path, count: int) -> array:
    """Read 'count' ints from a binary file."""
    arr: array = array("i")               # empty int array
    with path.open("rb") as f:            # open for binary reading
        arr.fromfile(f, count)            # raises EOFError if file is too short
    return arr                            # filled array


big: list[int] = list(range(1000))        # normal list of 1000 ints
packed: array = array("i", big)           # same numbers, compact
print(sys.getsizeof(packed) < sys.getsizeof(big) + 8000)   # array object is smaller -> True
print(packed.itemsize * len(packed))      # exactly 4 * 1000 = 4000 bytes of data

with tempfile.TemporaryDirectory() as d:  # folder deleted automatically
    p: Path = Path(d) / "nums.bin"        # file location
    save_array(to_array([1, 2, 3, 4]), p) # write 4 ints
    print(p.stat().st_size)               # 16 bytes = 4 items * 4 bytes
    print(load_array(p, 4))               # read them back

try:                                      # overflow protection
    array("b", [200])                     # "b" holds only -128..127
except OverflowError as e:                # catch the error
    print("OverflowError:", e)            # value out of range

try:                                      # type protection
    array("i", [1.5])                     # float not allowed in int array
except TypeError as e:                    # catch the error
    print("TypeError:", e)                # message from Python

print(array("H", [65535]))                # "H" = unsigned short, max 65535

# Output:
# True
# 4000
# 16
# array('i', [1, 2, 3, 4])
# OverflowError: signed char is greater than maximum
# TypeError: 'float' object cannot be interpreted as an integer
# array('H', [65535])
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Typed numeric array | `array("i")` | `Int32Array` |
| Float array | `array("d")` | `Float64Array` |
| Overflow behaviour | `OverflowError` | silently wraps around |
| Mixed-type list | `list` | `Array` |
| Binary file dump | `arr.tofile(f)` | `fs.writeFileSync(buf)` |

```python
# Python way
from array import array                 # import
nums: array = array("i", [1, 2, 3])     # typed int array
nums.append(4)                          # grow
print(nums.tolist())                    # [1, 2, 3, 4]
```
```javascript
// JavaScript way
const nums = new Int32Array([1, 2, 3]); // typed array, FIXED size
// nums.push(4);                        // not available! typed arrays cannot grow
console.log(Array.from(nums));          // [1, 2, 3]
```

Key difference: JS typed arrays have a fixed length and silently wrap overflowing values (`Int8Array` turns 200 into -56). Python's `array` can grow with `append`, and refuses bad values with an error.

---

## 🟠 FastAPI Connection
FastAPI itself returns JSON (lists), so `array` is used inside the service: keeping compact metric buffers, reading binary sensor data, or preparing numeric data. Before returning it, convert with `.tolist()` because JSON cannot encode an `array` object.

```python
# FastAPI example — compact metric buffer, returned as JSON
from array import array                       # compact typed array
from fastapi import FastAPI                   # FastAPI app

app: FastAPI = FastAPI()                      # create app
latencies: array = array("d")                 # response times in ms, as doubles


@app.post("/record/{ms}")                     # POST /record/12.5
def record(ms: float) -> dict[str, int]:
    latencies.append(ms)                      # 8 bytes per reading only
    return {"count": len(latencies)}          # how many stored


@app.get("/latencies")                        # GET /latencies
def get_latencies() -> list[float]:
    return latencies.tolist()                 # convert to list for JSON
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Choosing a type code that is too small
✅ Correct: pick a type that fits your largest value

```python
from array import array
# Wrong — "b" holds only -128..127
# array("b", [200])         # OverflowError
# Right — "i" (4 bytes) or "q" (8 bytes) for big numbers
ok = array("q", [200, 10**12])   # 64-bit signed
```

❌ Mistake 2: Putting strings or mixed types in an array
✅ Correct: use a `list` for mixed data

```python
from array import array
# Wrong
# array("i", ["a", 1])      # TypeError
# Right
mixed = ["a", 1, 2.5]       # list handles mixed types
```

❌ Mistake 3: Returning an `array` directly from an API
✅ Correct: convert with `.tolist()`

```python
from array import array
import json
data = array("i", [1, 2])
# Wrong
# json.dumps(data)          # TypeError: Object of type array is not JSON serializable
# Right
print(json.dumps(data.tolist()))   # [1, 2]
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from array import array
a = array("i", [1, 2, 3])
b = a[:]
b[0] = 99
print(a, b)
print(array("i", [1, 2]) == [1, 2])
print(array("i", [1, 2]) == array("l", [1, 2]))
```
Answer: `array('i', [1, 2, 3]) array('i', [99, 2, 3])` — slicing an array makes a new independent array. Second line is `False`: an array never equals a list even with the same numbers. Third line is `True`: arrays compare by their values, not by type code, so `"i"` and `"l"` arrays with equal numbers are equal.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `list` and `array.array`?
A1: A list holds pointers to any Python objects (mixed types, flexible, more memory). An array holds raw numbers of one type code (compact, fixed type, faster to dump to binary). Lists are the default; use arrays when you have large amounts of plain numeric data and memory matters.

Q2: Array vs NumPy array — when to choose which?
A2: `array.array` is built in, light, good for storage and binary I/O, but has no vector math (no `a + b` element-wise, no matrix ops). NumPy gives fast vectorized math, multi-dimensions, and a huge ecosystem, but is an external dependency. For math or ML use NumPy; for simple compact storage use `array`.

Q3: What does a type code mean? Name a few.
A3: A one-letter code for the C type: `"b"` signed char (1 byte), `"B"` unsigned char, `"h"` short (2), `"i"` int (usually 4), `"l"` long, `"q"` long long (8), `"f"` float (4), `"d"` double (8). `itemsize` tells the byte size on your machine.

Q4: Does an array save memory for 3 items?
A4: Not much; the array object has fixed overhead. The savings show up with large counts, since each item costs only `itemsize` bytes versus around 36 bytes (pointer plus int object) in a list.

Q5: How do you save an array to disk and read it back?
A5: `arr.tofile(f)` writes raw bytes to a binary file; `arr.fromfile(f, n)` reads `n` items. Or use `tobytes()` / `frombytes()`. Be careful about endianness if files move between machines (`arr.byteswap()` swaps byte order).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Large amounts of plain numbers and memory matters
- Reading/writing raw binary numeric files
- You want type safety (only ints, only floats)
- You cannot install NumPy (standard library only)

❌ Avoid when:
- Mixed data types — use `list`
- Math-heavy work (vector operations, matrices) — use NumPy
- Small collections — a list is simpler and fast enough
- You need to return JSON directly — convert to a list first

---

## 📊 Visual Diagram
```
list([1, 2, 3])                      array("i", [1, 2, 3])
+-----+                              +-------------------------+
| ptr |--> [int 1  28 bytes]         | 01 00 00 00 | 4 bytes   |
| ptr |--> [int 2  28 bytes]         | 02 00 00 00 | 4 bytes   |
| ptr |--> [int 3  28 bytes]         | 03 00 00 00 | 4 bytes   |
+-----+                              +-------------------------+
 items are scattered objects          one contiguous block

 typecode "i" -> itemsize 4   |   "d" -> itemsize 8   |   "b" -> itemsize 1
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Typecode | One-letter C type, like "i" or "d" | C type का एक अक्षर का code |
| itemsize | Bytes used by one item | एक item के bytes |
| Contiguous memory | Items stored side by side | पास-पास रखी memory |
| Overflow | Value too large for the type | Type की सीमा से बड़ी value |
| tofile / fromfile | Dump / load raw binary | Binary file में लिखना / पढ़ना |
| Homogeneous | All items same type | सब items एक ही type के |

---

## ⚡ 3-Line Summary
English: `array.array` stores numbers of one C type in one compact memory block, using much less memory than a list. It enforces types, raises OverflowError for big values, and can dump to binary files with `tofile()`. Use NumPy for math and `array` for light storage.
Hindi: `array.array` एक C type के numbers को एक compact memory block में रखती है, list से बहुत कम memory में। यह type enforce करती है, बड़ी value पर OverflowError देती है, और `tofile()` से binary file में dump होती है। Math के लिए NumPy, हल्के storage के लिए `array`।

---

## ➡️ Next Topic
**077. heapq Module** — a min-heap on top of a plain list: priority queues, top-K problems, and task schedulers.
