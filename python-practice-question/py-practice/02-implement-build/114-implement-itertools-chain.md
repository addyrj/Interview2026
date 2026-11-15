---

# Q114. Implement itertools.chain
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `chain(*iterables)` that lazily yields every item of the first iterable, then the second, and so on. Also implement `chain_from_iterable(iterables)`.

```python
list(chain([1, 2], (3, 4), "ab"))   # [1, 2, 3, 4, 'a', 'b']
```

---

## 💡 Quick Concept (2 lines only)
A generator that loops over each iterable and yields from it — nothing is computed until you ask for the next item.
हिंदी: Generator हर iterable को एक के बाद एक yield करता है — items lazily आते हैं, पहले से list नहीं बनती।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Iterable, Iterator, TypeVar        # type hints
T = TypeVar("T")                                      # generic item type

def chain(*iterables: Iterable[T]) -> Iterator[T]:
    for it in iterables:          # Step 1: go through each iterable in order
        for item in it:           # Step 2: pull items lazily one by one
            yield item            # Step 3: hand item to the caller

def chain_from_iterable(iterables: Iterable[Iterable[T]]) -> Iterator[T]:
    for it in iterables:          # outer iterable may itself be lazy/infinite
        yield from it             # delegate to the inner iterable

# ============================================
# TEST CASES
# ============================================
print(list(chain([1, 2], (3, 4), "ab")))             # Expected: [1, 2, 3, 4, 'a', 'b']
print(list(chain()))                                 # Expected: []
print(list(chain_from_iterable([[1], [2, 3], []])))  # Expected: [1, 2, 3]
g = chain([1, 2], [3])                               # create generator
print(next(g), next(g), next(g))                     # Expected: 1 2 3
try:
    next(g)                                          # exhausted
except StopIteration:
    print("StopIteration")                           # Expected: StopIteration

def nums():
    print("producing")                               # side effect shows laziness
    yield 1
c = chain(nums())                                    # nothing runs yet
print("created, nothing printed yet")                # Expected: created, nothing printed yet
print(list(c))                                       # Expected: producing  then  [1]
import itertools                                     # compare with the real one
print(list(itertools.chain([1, 2], (3, 4), "ab")) == list(chain([1, 2], (3, 4), "ab")))  # Expected: True
```

---

## 🔍 Why This Works (3 lines max)
`yield` turns the function into a generator, so each item is produced only when requested and no intermediate list is built. `chain_from_iterable` accepts a lazy outer iterable, so it even works with infinite streams.
हिंदी: `yield` से function generator बनता है, इसलिए memory में बड़ी list नहीं बनती।

---

## ⚡ Alternative Solution
```python
# Shorter: generator expression with a double loop
def chain2(*its):
    return (x for it in its for x in it)        # outer loop first, inner loop second

print(list(chain2("ab", range(3))))             # Output: ['a', 'b', 0, 1, 2]

# Infinite outer iterable still works with chain_from_iterable:
import itertools
print(list(itertools.islice(chain_from_iterable(itertools.repeat([7, 8])), 5)))
# Output: [7, 8, 7, 8, 7]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: passing a list of lists to chain(*iterables) as ONE argument
print(list(chain([[1, 2], [3]])))     # Output: [[1, 2], [3]]  (items are the inner lists)

# ✅ Correct: unpack with * or use chain_from_iterable
print(list(chain(*[[1, 2], [3]])))    # Output: [1, 2, 3]
print(list(chain_from_iterable([[1, 2], [3]])))  # Output: [1, 2, 3]
```

---

## 🎯 Interview Tip (1 line)
Say: "It's a lazy generator, O(1) extra memory; `yield from` delegates, and `chain.from_iterable` is the right tool for flattening one level."

---

## 🔗 Related Questions
→ Q058 (flatten a nested list) | Q120 (iterator class) | Q115 (groupby) | Q250 (itertools examples)
