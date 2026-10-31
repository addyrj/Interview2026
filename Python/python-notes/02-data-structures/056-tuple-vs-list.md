---

# 056. Tuple vs List
# हिंदी में: Tuple बनाम List

---

## 🔵 Simple Definition (English)
Both tuple and list are ordered collections that can hold any objects. A **list** is mutable (you can add, remove, change items). A **tuple** is immutable (once created, it can never change). Choose list for data that changes, tuple for fixed records.

## 🔵 सरल परिभाषा (Hindi)
Tuple और list दोनों ordered collections हैं। **List** mutable है (items add/remove/change कर सकते हैं)। **Tuple** immutable है (एक बार बनने के बाद बदल नहीं सकता)। बदलने वाले data के लिए list, fixed record के लिए tuple।

---

## 🔴 Problem it Solves
Not all data should be changeable. A (latitude, longitude) pair, an RGB colour, or a database row should never be modified by accident. If everything were a list, any function could silently change it. Also, lists cannot be dictionary keys or set members because they are unhashable. Tuples solve both: they are protected from change and they are hashable (if all items inside are hashable). They also use less memory and are slightly faster to create.

## 🔴 यह क्यों बना? (Hindi)
हर data बदलना नहीं चाहिए। (latitude, longitude), RGB colour या database row गलती से modify नहीं होनी चाहिए। List dict key या set member नहीं बन सकती (unhashable)। Tuple protected है, hashable है, कम memory लेता है और थोड़ा तेज़ बनता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → list  = [1, 2, 3]  → stored as a dynamic array of pointers (over-allocates extra space)
Step 2 → tuple = (1, 2, 3)  → stored as a fixed-size array of pointers (exact size, no extra)
Step 3 → list.append(4)     → allowed, array may grow (resize)
Step 4 → tuple has no append → item assignment t[0] = 9 raises TypeError
Step 5 → hash(tuple)        → computed from items' hashes → usable as dict key
Step 6 → hash(list)         → TypeError: unhashable type: 'list'
```

## 🟢 कैसे काम करता है? (Hindi)
```
List  → dynamic array, extra जगह reserve करती है, बदल सकते हैं
Tuple → fixed-size array, exact जगह, बदल नहीं सकते
Tuple का hash बनता है → dict key / set member बन सकता है
List का hash नहीं → dict key नहीं बन सकती
```

---

## 🟡 Real World Example
Swiggy: a delivery location is stored as a tuple `(12.97, 77.59)` — it is a fixed point and can be a dict key for caching "nearest restaurants". The cart items of a user are a list because items are added and removed. In FastAPI, a database row returned by SQLAlchemy behaves like a tuple (immutable, positional), while a list of such rows is the API response.

## 🟡 Real Example Hindi mein
Swiggy में delivery location tuple `(12.97, 77.59)` है — fixed point है और cache के लिए dict key बन सकता है। User का cart list है क्योंकि items add/remove होते हैं। FastAPI में SQLAlchemy की row tuple जैसी होती है, और rows की list API response बनती है।

---

## 💻 Code Example — Basic
```python
# Basic: tuple vs list differences
import sys                                   # sys.getsizeof gives object size in bytes

nums_list: list[int] = [1, 2, 3]             # list: mutable
nums_tuple: tuple[int, ...] = (1, 2, 3)      # tuple: immutable (any length of ints)

nums_list.append(4)                          # allowed on list
nums_list[0] = 100                           # item change allowed on list
print(nums_list)                             # Output: [100, 2, 3, 4]

try:                                         # tuple change must fail
    nums_tuple[0] = 100                      # type: ignore  (item assignment)
except TypeError as err:                     # catch the error
    print("Error:", err)                     # Output: Error: 'tuple' object does not support item assignment

point: tuple[float, float] = (12.97, 77.59)  # a fixed lat/long pair
cache: dict[tuple[float, float], str] = {}   # tuple is hashable -> valid dict key
cache[point] = "Koramangala"                 # store using tuple key
print(cache[(12.97, 77.59)])                 # Output: Koramangala

try:                                         # list as a key must fail
    bad = {[1, 2]: "x"}                      # type: ignore
except TypeError as err:                     # catch the error
    print("Error:", err)                     # Output: Error: unhashable type: 'list'

single: tuple[int] = (5,)                    # one-item tuple NEEDS the trailing comma
not_tuple: int = (5)                         # this is just int 5 in brackets
print(type(single).__name__, type(not_tuple).__name__)  # Output: tuple int

a, b, c = nums_tuple                         # unpacking works for both types
print(a, b, c)                               # Output: 1 2 3
print(sys.getsizeof([1, 2, 3]) > sys.getsizeof((1, 2, 3)))  # Output: True (tuple is smaller)
```

## 💻 Code Example — Advanced
```python
# Advanced: shallow immutability, hashing, speed and safe API design
from __future__ import annotations           # allow modern hint syntax everywhere
import timeit                                # measure small snippets
from typing import Any                       # for generic hints


def is_hashable(obj: Any) -> bool:
    """Return True if obj can be used as a dict key."""
    try:                                     # hash() raises TypeError if unhashable
        hash(obj)                            # try to hash it
        return True                          # success
    except TypeError:                        # unhashable object
        return False                         # report failure


# 1. Tuple is only SHALLOWLY immutable: inner list can still change
record: tuple[str, list[int]] = ("scores", [1, 2])   # tuple holding a list
record[1].append(3)                          # allowed! the list inside is mutable
print(record)                                # Output: ('scores', [1, 2, 3])
print(is_hashable(record))                   # Output: False (contains a list)
print(is_hashable(("scores", (1, 2))))       # Output: True  (all items hashable)

# 2. += on a tuple holding a list: famous trap (item changes, then error)
trap: tuple[int, list[int]] = (1, [10])      # tuple with list inside
try:                                         # attempt augmented assignment
    trap[1] += [20]                          # type: ignore  list extended, then assignment fails
except TypeError as err:                     # tuple refuses the re-assignment
    print("Error:", err)                     # Output: Error: 'tuple' object does not support item assignment
print(trap)                                  # Output: (1, [10, 20])  <- list WAS changed!

# 3. Speed: tuple creation vs list creation (constant tuple is folded at compile time)
t_time: float = timeit.timeit("(1, 2, 3, 4, 5)", number=500_000)   # build tuple
l_time: float = timeit.timeit("[1, 2, 3, 4, 5]", number=500_000)   # build list
print("tuple faster than list:", t_time < l_time)   # Output: tuple faster than list: True


# 4. Safe API design: return tuple (read-only) from a function, list for caller-owned data
def get_allowed_roles() -> tuple[str, ...]:
    """Return fixed roles; callers cannot mutate the shared source."""
    return ("admin", "editor", "viewer")     # immutable, safe to share/cache


roles: tuple[str, ...] = get_allowed_roles() # get the roles
mutable_roles: list[str] = list(roles)       # convert to list when you need to change
mutable_roles.append("guest")                # change the copy only
print(roles)                                 # Output: ('admin', 'editor', 'viewer')
print(mutable_roles)                         # Output: ['admin', 'editor', 'viewer', 'guest']
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
colors = ["red", "green"]            # list: mutable
colors.append("blue")                # change allowed
point = (10, 20)                     # tuple: immutable, built-in
x, y = point                         # unpack
cache = {point: "home"}              # tuple as dict key works
```

```javascript
// JavaScript
const colors = ["red", "green"];     // array: mutable (const only stops re-assign)
colors.push("blue");                 // change allowed
const point = Object.freeze([10, 20]); // closest to tuple: frozen array (not a real type)
const [x, y] = point;                // destructuring
const cache = new Map([[point, "home"]]); // Map key is by reference, not by value!
cache.get([10, 20]);                 // undefined  (different array object)
```

Key difference: JS has no real tuple. Python tuples compare and hash **by value**, so `{(10, 20): "home"}[(10, 20)]` works. FastAPI link: Pydantic can validate `tuple[float, float]` fields exactly (fixed length), which JS/TypeScript tuples only check at compile time.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting the comma in a single-item tuple
```python
# Wrong:
t = (5)          # this is int 5, NOT a tuple
# Correct:
t = (5,)         # comma makes the tuple
```

❌ Mistake 2: Thinking tuple contents can never change
```python
# Wrong assumption:
t = ([1], [2])
t[0].append(99)          # works! tuple is only shallowly immutable
# Correct: use tuples of immutable items (ints, str, tuples) for truly fixed data
```

❌ Mistake 3: Using a list as a default or dict key
```python
# Wrong:
# d = {[1, 2]: "a"}      # TypeError: unhashable type: 'list'
# Correct:
d = {(1, 2): "a"}        # tuple works
```

---

## 🧠 Tricky Interview Question

**Q**: "Is `t = (1, 2, [3, 4])` hashable? And what happens with `t[2] += [5]`?"

**Answer**: `t` is NOT hashable, because `hash()` of a tuple hashes every item and a list is unhashable, so `hash(t)` raises `TypeError`. For `t[2] += [5]`: Python first runs `list.__iadd__`, which extends the list in place (success), and then tries to assign the result back to `t[2]`, which fails with `TypeError`. So you get an error AND the list is already changed to `[3, 4, 5]`. Lesson: immutability is shallow.

---

## ⚫ Interview Questions + Answers

Q1: What is the main difference between a tuple and a list?
A1: Mutability. A list can change after creation (append, remove, item assignment). A tuple cannot change its structure (no add/remove/replace of items). Because of this, a tuple is hashable (when its items are) and can be a dict key or set member, uses less memory, and is slightly faster. Use tuple for fixed records, list for collections that grow or change.

Q2: Why is tuple faster and smaller than list?
A2: A list is a dynamic array: it over-allocates spare slots so `append` is cheap, and it stores extra bookkeeping. A tuple has a fixed size, so Python allocates exactly what is needed, and constant tuples like `(1, 2, 3)` are even built once at compile time. Smaller objects also mean better cache behaviour. The gain is small per object but real when you hold millions of them.

Q3: Can a tuple be a dictionary key?
A3: Yes, if every item inside is hashable. `{(1, 2): "a"}` works. `{(1, [2]): "a"}` fails with `TypeError` because the list inside is unhashable. This is why coordinates, composite keys such as `(user_id, date)`, and cache keys are commonly tuples.

Q4: Is a tuple truly immutable?
A4: The tuple itself is: you cannot add, remove or rebind its slots. But if an item is a mutable object (like a list), that object can still be changed through the tuple. So immutability is shallow. For deep immutability, use only immutable items or a frozen dataclass / frozenset.

Q5: When would you choose a tuple over a list in a FastAPI project?
A5: For constants (allowed HTTP methods, roles, status codes), for function return values with a fixed shape (`return user, token`), for composite cache keys, and in Pydantic models for fixed-length fields like `tuple[float, float]` coordinates. Use lists for query results, request bodies containing many items, and anything built up in loops.

---

## 🔷 When to Use Tuple vs List

✅ Use tuple when:
- Data is a fixed record (coordinates, RGB, a DB row)
- You need a dict key or set member
- Returning multiple values from a function
- You want to signal "do not change this"

✅ Use list when:
- Items are added, removed or sorted
- The length is unknown in advance
- All items are the same kind (a homogeneous sequence)

❌ Avoid:
- Tuple of mutable items when you need true immutability
- Using a list when a tuple would protect shared constants

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mutable | Can be changed after creation | बनने के बाद बदल सकते हैं |
| Immutable | Cannot be changed | बदल नहीं सकते |
| Hashable | Has a stable hash, usable as key | Hash बनता है, key बन सकता है |
| Unpacking | Assign items to variables at once | Items को variables में बाँटना |
| Shallow immutability | Container fixed, inner objects may change | Container fixed, अंदर की चीज़ें बदल सकती हैं |
| Dynamic array | Resizable array behind list | List के पीछे का resizable array |

---

## ⚡ 3-Line Summary
English: List is mutable and grows; tuple is immutable, hashable (if items are), smaller and faster. Use tuple for fixed records and dict keys, list for changing collections. Tuple immutability is shallow, so a list inside a tuple can still change.
Hindi: List mutable है और बढ़ती है; tuple immutable, hashable, छोटा और तेज़ है। Fixed records और dict keys के लिए tuple, बदलने वाले collections के लिए list। Tuple की immutability shallow है — अंदर की list बदल सकती है।

---

## ➡️ Next Topic
**057. Named Tuple** — tuples with named fields, `collections.namedtuple` vs `typing.NamedTuple`, readable records.
