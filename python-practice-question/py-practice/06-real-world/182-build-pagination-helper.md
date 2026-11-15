---

# Q182. Build Pagination Helper
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build `paginate(data, page, per_page)` returning the page items plus metadata (total, total pages, has_next, has_prev). Validate inputs and handle empty data and out-of-range pages.

---

## 💡 Quick Concept (2 lines only)
Offset pagination: `start = (page - 1) * per_page`, slice `data[start:start + per_page]`; total pages = `ceil(total / per_page)`.
हिंदी: Page का slice `(page-1)*per_page` से शुरू होता है; कुल pages `ceil(total/per_page)` होते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from dataclasses import dataclass                        # Step 1: result container
from math import ceil                                    # round pages up
from typing import Any

@dataclass(frozen=True)
class Page:
    items: list[Any]                                     # rows on this page
    page: int                                            # current page (1-based)
    per_page: int                                        # page size
    total: int                                           # total rows overall
    @property
    def pages(self) -> int:
        return max(1, ceil(self.total / self.per_page))  # at least 1 page, even if empty
    @property
    def has_next(self) -> bool:
        return self.page < self.pages                    # more pages after this?
    @property
    def has_prev(self) -> bool:
        return self.page > 1                             # pages before this?

def paginate(data: list[Any], page: int = 1, per_page: int = 10) -> Page:
    if page < 1 or per_page < 1:                         # Step 2: validate
        raise ValueError("page and per_page must be >= 1")
    start = (page - 1) * per_page                        # Step 3: first index of the page
    return Page(data[start:start + per_page], page, per_page, len(data))  # slicing is safe out of range

# ============================================
# TEST CASES
# ============================================
data = list(range(1, 24))                                # 23 items
p = paginate(data, page=3, per_page=10)
print(p.items, p.pages, p.has_next, p.has_prev)          # Expected: [21, 22, 23] 3 False True
p = paginate(data, page=1, per_page=10)
print(p.items, p.has_next, p.has_prev)                   # Expected: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] True False
print(paginate(data, page=9).items)                      # Expected: []  (out of range -> empty, no crash)
print(paginate([], page=1).pages)                        # Expected: 1
try:
    paginate(data, page=0)                               # invalid page
except ValueError as e:
    print("ValueError:", e)                              # Expected: ValueError: page and per_page must be >= 1
```

---

## 🔍 Why This Works (3 lines max)
Python slicing never raises on out-of-range indexes, so a page past the end simply returns `[]`. `ceil` (not `//`) makes a partial last page count; `frozen=True` keeps the result immutable.
हिंदी: Slicing out-of-range पर error नहीं देती; `ceil` से आखिरी अधूरा page भी गिना जाता है।

---

## ⚡ Alternative Solution
```python
from itertools import islice                             # lazy chunking

def chunks(seq, size: int):
    it = iter(seq)                                       # works with any iterable
    while chunk := list(islice(it, size)):               # walrus: stop on empty chunk
        yield chunk                                      # one page at a time
print(list(chunks(range(7), 3)))                         # Expected: [[0, 1, 2], [3, 4, 5], [6]]

# Cursor (keyset) pagination: stable when rows are inserted/deleted
def paginate_cursor(rows: list[dict], after_id: int | None, limit: int) -> tuple[list[dict], int | None]:
    rows = sorted(rows, key=lambda r: r["id"])           # stable order
    if after_id is not None:
        rows = [r for r in rows if r["id"] > after_id]   # rows after the cursor
    page = rows[:limit]                                  # this page
    return page, (page[-1]["id"] if len(rows) > limit else None)  # next cursor or None

rows = [{"id": i} for i in range(1, 8)]
page, nxt = paginate_cursor(rows, None, 3)
print([r["id"] for r in page], nxt)                      # Expected: [1, 2, 3] 3
page, nxt = paginate_cursor(rows, nxt, 3)
print([r["id"] for r in page], nxt)                      # Expected: [4, 5, 6] 6
page, nxt = paginate_cursor(rows, nxt, 3)
print([r["id"] for r in page], nxt)                      # Expected: [7] None
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: treating page as 0-based while users send 1-based (skips the first page)
def bad(data, page, per_page):
    return data[page * per_page:(page + 1) * per_page]
print(bad(data, 1, 10))                                  # Output: [11, ..., 20]  (page 1 shows page 2!)

# ❌ Also wrong: total pages with floor division
print(len(data) // 10)                                   # Output: 2  (23 items need 3 pages)
# ✅ Correct: ceil(len(data) / 10)                       # Output: 3
```

---

## 🎯 Interview Tip (1 line)
Say: "Offset pagination is simple but slow/unstable on big changing tables (`OFFSET` scans) — mention cursor/keyset pagination as the scalable alternative."

---

## 🔗 Related Questions
→ Q060 (chunk list into groups) | Q229 (pagination endpoint) | Q220 (stream large data) | Q217 (batch API calls)
