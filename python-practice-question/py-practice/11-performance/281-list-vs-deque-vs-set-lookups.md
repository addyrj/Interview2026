---

# Q281. list vs deque vs set Lookups
# Category: PERFORMANCE
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
You must check `x in container` many times on 10,000 items. Compare `list`, `deque` and `set`. Which is fastest for membership, and when is `deque` the right choice instead of `list`?

---

## 💡 Quick Concept (2 lines only)
`in` on a list/deque scans every item (O(n)); `in` on a set hashes the key (O(1) average). `deque` wins only at the ends (O(1) `popleft`/`appendleft`, vs O(n) for `list.pop(0)`).
हिंदी: Lookup के लिए set, दोनों सिरों पर add/remove के लिए deque, बाकी के लिए list।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import timeit                                   # Step 1: timing helper from stdlib
from collections import deque                   # Step 2: double-ended queue

N = 10_000                                      # Step 3: container size
data_list = list(range(N))                      # list of 0..9999
data_deque = deque(data_list)                   # same items in a deque
data_set = set(data_list)                       # same items in a set
target = N - 1                                  # worst case for scans: last element

def bench(container) -> float:                  # time 1000 membership checks
    return timeit.timeit(lambda: target in container, number=1000)  # run and return seconds

t_list = bench(data_list)                       # O(n) scan
t_deque = bench(data_deque)                     # O(n) scan (a bit slower than list)
t_set = bench(data_set)                         # O(1) hash lookup

# ============================================
# TEST CASES
# ============================================
print(t_set < t_list)                           # Expected: True
print(t_set < t_deque)                          # Expected: True
print(t_list / t_set > 100)                     # Expected: True  (measured ~1000x; timings vary by machine)
```

---

## 🔍 Why This Works (3 lines max)
A set stores items in a hash table, so `in` jumps straight to a bucket; list and deque compare element by element. Measured here: list ~0.04s, deque ~0.06s, set ~0.00004s for 1000 checks.
हिंदी: Set hash से सीधे item ढूँढता है, list/deque एक-एक करके देखते हैं।

---

## ⚡ Alternative Solution
```python
# deque's real advantage: O(1) operations at the LEFT end
import timeit                                   # timing helper
from collections import deque                   # deque import

lst = list(range(100_000))                      # big list
dq = deque(range(100_000))                      # big deque

def list_ops() -> None:                         # insert at front then pop it
    lst.insert(0, 1)                            # O(n): shifts all items right
    lst.pop(0)                                  # O(n): shifts all items left

def deque_ops() -> None:                        # same operations on a deque
    dq.appendleft(1)                            # O(1)
    dq.popleft()                                # O(1)

t_l = timeit.timeit(list_ops, number=2000)      # time the list version
t_d = timeit.timeit(deque_ops, number=2000)     # time the deque version
print(t_d < t_l)                                # Expected: True
print(t_l / t_d > 50)                           # Expected: True  (measured ~1000x; varies)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: repeated `in` on a list inside a loop -> O(n*m)
allowed = list(range(10_000))                   # list used as lookup table
hits = [x for x in range(100) if x in allowed]  # each `in` scans the list

# ✅ Correct: convert once to a set -> O(n + m)
allowed_set = set(allowed)                      # one-time O(n) cost
hits = [x for x in range(100) if x in allowed_set]  # each `in` is O(1)
print(len(hits))                                # Expected: 100
```

---

## 🎯 Interview Tip (1 line)
Say: "Membership -> set/dict; queue (FIFO) -> deque; random index access -> list; and sets need hashable items and lose ordering guarantees by value."

---

## 🔗 Related Questions
→ Q288 (efficient dict/set operations) | Q290 (avoiding slow patterns) | Q101 (implement queue) | Q276 (timeit)
