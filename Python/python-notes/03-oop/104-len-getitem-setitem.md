---

# 104. __len__ __getitem__ __setitem__
# हिंदी में: Container Methods (len(), x[i], x[i] = v अपनी Class पर)

---

## 🔵 Simple Definition (English)
These three magic methods make your class act like a list or dict. `__len__` powers `len(obj)`, `__getitem__` powers `obj[key]` (reading), and `__setitem__` powers `obj[key] = value` (writing). With `__getitem__` alone you also get iteration and `in` for free.

## 🔵 सरल परिभाषा (Hindi)
ये तीन magic methods आपकी class को list या dict जैसा बनाते हैं। `__len__` से `len(obj)`, `__getitem__` से `obj[key]` (पढ़ना) और `__setitem__` से `obj[key] = value` (लिखना) चलता है। सिर्फ `__getitem__` से iteration और `in` भी मुफ्त में मिल जाते हैं।

---

## 🔴 Problem it Solves
A custom collection (shopping cart, paginated results, a matrix, a config store) with methods like `cart.get_item(2)`, `cart.set_item(2, x)`, `cart.size()` is unfamiliar for every reader. Users already know `len(c)`, `c[2]`, `c[2] = x`, `for x in c`. These methods let your class use that familiar syntax and work with built-ins (`sorted`, `list`, `reversed`, `in`).

## 🔴 यह क्यों बना? (Hindi)
Custom collection (shopping cart, paginated results, matrix, config store) में `cart.get_item(2)`, `cart.set_item(2, x)`, `cart.size()` जैसे methods हर पढ़ने वाले के लिए अनजाने हैं। Users `len(c)`, `c[2]`, `c[2] = x`, `for x in c` पहले से जानते हैं। ये methods आपकी class को वही जाना-पहचाना syntax देते हैं और built-ins (`sorted`, `list`, `reversed`, `in`) के साथ काम करने देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → len(obj)        -> obj.__len__()               must return int >= 0
Step 2 → obj[key]        -> obj.__getitem__(key)        key can be int, str, slice, tuple...
Step 3 → obj[key] = v    -> obj.__setitem__(key, v)
Step 4 → del obj[key]    -> obj.__delitem__(key)
Step 5 → obj[1:3]        -> __getitem__(slice(1, 3, None))  you decide how to handle slices
Step 6 → for x in obj / x in obj work through __getitem__(0), (1), ... until IndexError
         (old "sequence protocol"); define __iter__ / __contains__ for speed and clarity
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → len(obj)        -> obj.__len__()               int >= 0 लौटाना ज़रूरी
Step 2 → obj[key]        -> obj.__getitem__(key)        key int, str, slice, tuple... कुछ भी हो सकती है
Step 3 → obj[key] = v    -> obj.__setitem__(key, v)
Step 4 → del obj[key]    -> obj.__delitem__(key)
Step 5 → obj[1:3]        -> __getitem__(slice(1, 3, None))  slice कैसे संभालना है आप तय करें
Step 6 → for x in obj / x in obj, __getitem__(0), (1), ... को IndexError आने तक चलाकर काम करते हैं
         (पुराना "sequence protocol"); तेज़ी और साफ़ी के लिए __iter__ / __contains__ लिखें
```

---

## 🟡 Real World Example
An e-commerce `Cart` class: `len(cart)` gives item count, `cart["SKU-1"]` returns the line item, `cart["SKU-1"] = 3` sets quantity (with validation). A `Page` class from a paginated API acts like a list of results. pandas `df["col"]`, NumPy `arr[0, 1]`, `os.environ["HOME"]`, and `requests` headers (`resp.headers["Content-Type"]`) are all `__getitem__`.

## 🟡 Real Example Hindi mein
E-commerce `Cart` class: `len(cart)` से items की गिनती, `cart["SKU-1"]` से line item, `cart["SKU-1"] = 3` से quantity set (validation के साथ)। Paginated API की `Page` class results की list जैसी चलती है। pandas `df["col"]`, NumPy `arr[0, 1]`, `os.environ["HOME"]` और `requests` के headers (`resp.headers["Content-Type"]`) सब `__getitem__` हैं।

---

## 💻 Code Example — Basic
```python
# Basic container methods
class Playlist:                                 # behaves like a list of songs
    def __init__(self, songs: list[str]) -> None:     # constructor
        self._songs: list[str] = list(songs)    # private copy

    def __len__(self) -> int:                   # len(p)
        return len(self._songs)

    def __getitem__(self, i: int | slice) -> "str | list[str]":    # p[i] and p[1:3]
        return self._songs[i]                   # delegate to the list (handles slices too)

    def __setitem__(self, i: int, value: str) -> None:    # p[i] = "new"
        self._songs[i] = value                  # delegate

    def __delitem__(self, i: int) -> None:      # del p[i]
        del self._songs[i]


p: Playlist = Playlist(["a", "b", "c", "d"])    # create
print(len(p), p[0], p[-1], p[1:3])              # length, index, negative index, slice
p[1] = "B"                                      # setitem
del p[0]                                        # delitem
print([s for s in p])                           # iteration works through __getitem__
print("c" in p, list(reversed(p)))              # `in` and reversed() also work
try:                                            # out of range
    p[10]                                       # list raises IndexError
except IndexError as e:
    print("Error:", e)

# Output:
# 4 a d ['b', 'c']
# ['B', 'c', 'd']
# True ['d', 'c', 'B']
# Error: list index out of range
```

## 💻 Code Example — Advanced
```python
# Production style: dict-like Cart with validation, slices, KeyError and a Matrix with tuple keys
from collections.abc import Iterator            # type for __iter__


class Cart:
    """Maps SKU -> quantity with validation."""

    def __init__(self) -> None:
        self._items: dict[str, int] = {}        # internal storage

    def __len__(self) -> int:                   # number of distinct SKUs
        return len(self._items)

    def __getitem__(self, sku: str) -> int:     # cart["A1"]
        try:
            return self._items[sku]
        except KeyError:
            raise KeyError(f"SKU not in cart: {sku}") from None   # clean message

    def __setitem__(self, sku: str, qty: int) -> None:    # cart["A1"] = 2
        if not isinstance(qty, int) or qty < 0:    # validate
            raise ValueError("qty must be a non-negative int")
        if qty == 0:                            # zero means remove
            self._items.pop(sku, None)
        else:
            self._items[sku] = qty

    def __delitem__(self, sku: str) -> None:    # del cart["A1"]
        del self._items[sku]

    def __contains__(self, sku: object) -> bool:    # "A1" in cart (fast, no scan)
        return sku in self._items

    def __iter__(self) -> Iterator[str]:        # for sku in cart
        return iter(self._items)

    def __bool__(self) -> bool:                 # if cart:
        return bool(self._items)


class Matrix:
    """2D grid accessed as m[row, col] - key is a tuple."""

    def __init__(self, rows: int, cols: int) -> None:
        self._rows, self._cols = rows, cols     # shape
        self._data: list[float] = [0.0] * (rows * cols)    # flat storage

    def _idx(self, key: tuple[int, int]) -> int:    # tuple -> flat index
        r, c = key                              # unpack the tuple key
        if not (0 <= r < self._rows and 0 <= c < self._cols):
            raise IndexError(f"({r}, {c}) outside {self._rows}x{self._cols}")
        return r * self._cols + c

    def __getitem__(self, key: tuple[int, int]) -> float:
        return self._data[self._idx(key)]

    def __setitem__(self, key: tuple[int, int], v: float) -> None:
        self._data[self._idx(key)] = v

    def __len__(self) -> int:                   # number of rows, like NumPy
        return self._rows


cart: Cart = Cart()
cart["A1"] = 2                                  # setitem
cart["B7"] = 1
cart["A1"] = 5                                  # update
print(len(cart), cart["A1"], "B7" in cart, list(cart))
cart["B7"] = 0                                  # zero removes
print(len(cart), bool(cart))
for bad in (lambda: cart["ZZ"], lambda: cart.__setitem__("A1", -1)):
    try:
        bad()
    except (KeyError, ValueError) as e:
        print(type(e).__name__, "-", e)

m: Matrix = Matrix(2, 3)
m[1, 2] = 9.5                                   # key is the tuple (1, 2)
print(m[1, 2], m[0, 0], len(m))
try:
    m[2, 0]
except IndexError as e:
    print("Error:", e)

# Output:
# 2 5 True ['A1', 'B7']
# 1 True
# KeyError - 'SKU not in cart: ZZ'
# ValueError - qty must be a non-negative int
# 9.5 0.0 2
# Error: (2, 0) outside 2x3
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Length | `len(obj)` -> `__len__` | `arr.length` property |
| Index read | `obj[i]` -> `__getitem__` | `arr[i]` (built in); custom via `Proxy` |
| Index write | `obj[i] = v` -> `__setitem__` | same, custom via `Proxy` |
| Delete | `del obj[i]` -> `__delitem__` | `delete obj[i]` |
| Slicing | `obj[1:3]` -> `slice` object | `arr.slice(1, 3)` method |
| Negative index | Built-in lists; you handle it in custom classes | `arr.at(-1)` |

```python
# Python way
class Box:
    def __init__(self) -> None:
        self._d: dict[str, int] = {}
    def __getitem__(self, k: str) -> int:
        return self._d[k]
    def __setitem__(self, k: str, v: int) -> None:
        self._d[k] = v
    def __len__(self) -> int:
        return len(self._d)

b = Box(); b["a"] = 1
print(b["a"], len(b))         # 1 1
```
```javascript
// JavaScript way — needs a Proxy to intercept bracket access
class Box {
  constructor() {
    this._d = {};
    return new Proxy(this, {                       // intercept b["a"]
      get: (t, k) => (k in t ? t[k] : t._d[k]),
      set: (t, k, v) => { t._d[k] = v; return true; },
    });
  }
  get size() { return Object.keys(this._d).length; }   // no len(): use a property
}
const b = new Box(); b["a"] = 1;
console.log(b["a"], b.size);                       // 1 1
```

Key difference: Python makes `[]` and `len()` hookable with simple methods. JavaScript needs `Proxy` for custom bracket behavior, and `length` is a property, not a protocol.

---

## 🟠 FastAPI Connection
Request objects behave like dicts: `request.headers["user-agent"]`, `request.query_params["q"]`, and `request.cookies` all use `__getitem__`. Your own response wrappers (like a paginated `Page`) can implement `__len__` and `__getitem__` so templates and serializers handle them as lists.

```python
# FastAPI example — headers use __getitem__; a Page object acts like a list
from fastapi import FastAPI, Request          # app and request object
from fastapi.testclient import TestClient     # test client


class Page:                                   # paginated results
    def __init__(self, items: list[str], page: int) -> None:
        self.items: list[str] = items
        self.page: int = page

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, i: int) -> str:
        return self.items[i]


app: FastAPI = FastAPI()                      # create app


@app.get("/search")
def search(request: Request) -> dict[str, object]:
    ua: str = request.headers["user-agent"]   # __getitem__ on Headers
    page: Page = Page(["x", "y", "z"], 1)
    return {"ua": ua, "count": len(page), "first": page[0], "all": list(page)}   # list() uses __getitem__


client: TestClient = TestClient(app)          # test client
r = client.get("/search", headers={"user-agent": "demo"})
print(r.json())

# Output:
# {'ua': 'demo', 'count': 3, 'first': 'x', 'all': ['x', 'y', 'z']}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Raising the wrong exception from `__getitem__`
✅ Correct: sequences raise `IndexError`, mappings raise `KeyError` (iteration over a sequence relies on `IndexError` to stop)

```python
class Wrong:
    def __getitem__(self, i: int) -> int:
        if i > 2:
            raise ValueError("done")     # for loop never stops cleanly
        return i

class Right:
    def __getitem__(self, i: int) -> int:
        if i > 2:
            raise IndexError(i)          # for loop stops correctly
        return i

print(list(Right()))                     # [0, 1, 2]
try:
    list(Wrong())
except ValueError as e:
    print("Error:", e)                   # done
```

❌ Mistake 2: Ignoring slices (`obj[1:3]` gives a `slice` object)
✅ Correct: pass slices through or handle `isinstance(key, slice)`

```python
class Wrong:
    def __init__(self) -> None:
        self.d = [10, 20, 30, 40]
    def __getitem__(self, i: int) -> int:
        return self.d[int(i)]            # int(slice) fails

try:
    Wrong()[1:3]
except TypeError as e:
    print("Error:", e)                   # int() argument must be ... not 'slice'

class Right(Wrong):
    def __getitem__(self, i):            # type: ignore[override]
        return self.d[i]                 # list handles slice itself

print(Right()[1:3])                      # [20, 30]
```

❌ Mistake 3: `__len__` returning a non-int or negative number
✅ Correct: return a non-negative `int`; also remember `len()` makes the object falsy when 0

```python
class Wrong:
    def __len__(self) -> int:
        return -1

try:
    len(Wrong())
except ValueError as e:
    print("Error:", e)                   # __len__() should return >= 0

class Empty:
    def __len__(self) -> int:
        return 0

print(bool(Empty()))                     # False  <- empty container is falsy
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class Weird:
    def __getitem__(self, i: int) -> int:
        if i >= 3:
            raise IndexError
        return i * 10

w = Weird()
print(list(w))
print(20 in w)
print(sum(w))
print(len(w))
```
Answer: `[0, 10, 20]`, `True`, `30`, then `TypeError: object of type 'Weird' has no len()`. With only `__getitem__`, Python falls back to the old sequence protocol: it calls `w[0]`, `w[1]`, ... until `IndexError`. So `list`, `in` and `sum` work, but `len()` needs its own `__len__`.

---

## ⚫ Interview Questions + Answers

Q1: What does `obj[1:3]` pass to `__getitem__`?
A1: A `slice(1, 3, None)` object. Use `key.indices(len(self))` to get normalized start/stop/step values, or delegate to an underlying list.

Q2: Can `__getitem__` take non-integer keys?
A2: Yes: strings (dict-like), tuples (`m[1, 2]` passes the tuple `(1, 2)`), slices, Ellipsis. NumPy and pandas use all of these.

Q3: How is iteration possible without `__iter__`?
A3: The legacy sequence protocol: Python calls `__getitem__(0)`, `__getitem__(1)`, ... until `IndexError`. Prefer defining `__iter__` explicitly.

Q4: What is `__missing__`?
A4: A dict subclass hook called by `dict.__getitem__` when a key is absent. `collections.defaultdict` uses it. Normal classes do not call it; it is only for dict subclasses.

Q5: Easiest way to build a full custom sequence or mapping?
A5: Inherit from `collections.abc.MutableSequence` / `MutableMapping` and implement the few abstract methods (`__getitem__`, `__setitem__`, `__delitem__`, `__len__`, plus `insert` or `__iter__`). You then get `append`, `pop`, `get`, `items`, `update` etc. for free.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building list-like or dict-like collections (carts, pages, grids, config)
- Wrapping a list/dict while adding validation
- Giving DSL-like access (`config["db.host"]`)

❌ Avoid when:
- A plain list or dict already does the job
- You only need one operation (a method is clearer)
- Subclassing `list`/`dict` is enough (but beware: built-in methods bypass your overrides)

---

## 📊 Visual Diagram
```
 syntax              method called
 ------------------  ------------------------
 len(c)              c.__len__()
 c[2]                c.__getitem__(2)
 c["A1"]             c.__getitem__("A1")
 c[1:3]              c.__getitem__(slice(1,3,None))
 c[1, 2]             c.__getitem__((1, 2))
 c[2] = 5            c.__setitem__(2, 5)
 del c[2]            c.__delitem__(2)
 for x in c          c.__iter__()  (or __getitem__(0..) until IndexError)
 x in c              c.__contains__(x) (or scans via iteration)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `__len__` | Number of items for `len()` | `len()` के लिए items की संख्या |
| `__getitem__` | Read with `[]` | `[]` से पढ़ना |
| `__setitem__` | Write with `[]` | `[]` से लिखना |
| Slice | `a[1:3]` range object | `a[1:3]` वाला range object |
| Sequence protocol | Index-based iteration | Index से iteration का तरीका |
| Mapping | Key-based container (dict-like) | Key वाला container |

---

## ⚡ 3-Line Summary
English: `__len__`, `__getitem__` and `__setitem__` make your class work with `len()`, `obj[key]` and `obj[key] = v`. Raise `IndexError` for sequences and `KeyError` for mappings, and handle slices. For full collections, inherit from `collections.abc`.
Hindi: `__len__`, `__getitem__` और `__setitem__` आपकी class को `len()`, `obj[key]` और `obj[key] = v` के साथ चलाते हैं। Sequences में `IndexError` और mappings में `KeyError` उठाएं, और slices संभालें। पूरी collection के लिए `collections.abc` से inherit करें।

---

## ➡️ Next Topic
**105. `__eq__`, `__lt__`, `__gt__`** — comparison magic methods that make your objects equal, sortable and usable in `sorted()` and `max()`.
