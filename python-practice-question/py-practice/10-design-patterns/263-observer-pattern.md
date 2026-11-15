---

# Q263. Observer Pattern
# Category: DESIGN PATTERNS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement the Observer pattern: a `Subject` (e.g. a stock price) that notifies all subscribed observers when its state changes. Support subscribe and unsubscribe.

```python
stock = Stock("AAPL")
stock.subscribe(lambda price: print("got", price))
stock.price = 150      # observers are notified
```

---

## 💡 Quick Concept (2 lines only)
Observer = one-to-many dependency: when the subject changes, all registered observers are called automatically. In Python, observers are just callables, and a `property` setter is a natural trigger.
हिंदी: Observer में subject बदलते ही सारे subscribers को अपने-आप notify किया जाता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections.abc import Callable             # observer type

Observer = Callable[[float], None]               # an observer takes the new price

class Stock:
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol                     # stock name
        self._price = 0.0                        # current price
        self._observers: list[Observer] = []     # subscribers

    def subscribe(self, fn: Observer) -> Callable[[], None]:
        self._observers.append(fn)               # register
        return lambda: self._observers.remove(fn)  # handy unsubscribe function

    @property
    def price(self) -> float:
        return self._price                       # read access

    @price.setter
    def price(self, value: float) -> None:
        if value != self._price:                 # notify only on real change
            self._price = value                  # update state
            for fn in list(self._observers):     # copy: observers may unsubscribe while notified
                fn(value)                        # push the new value

# ============================================
# TEST CASES
# ============================================
stock = Stock("AAPL")                            # subject
unsub = stock.subscribe(lambda p: print("A got", p))   # observer A
stock.subscribe(lambda p: print("B got", p))     # observer B
stock.price = 150                                # both notified
unsub()                                          # A unsubscribes
stock.price = 155                                # only B notified
stock.price = 155                                # unchanged -> nobody notified

# Output:
# A got 150
# B got 150
# B got 155
```

---

## 🔍 Why This Works (3 lines max)
The subject keeps a list of callables and invokes each on change, so it knows nothing about who listens (loose coupling). The property setter hooks notification into plain attribute assignment. Iterating over a copy (`list(...)`) makes unsubscribing during a notification safe.
हिंदी: Subject को observers के बारे में सिर्फ इतना पता है कि वे callable हैं — यही loose coupling है।

---

## ⚡ Alternative Solution
```python
# Weak references: observers are removed automatically when garbage collected
import weakref                                   # WeakSet holds weak refs

class Subject:
    def __init__(self) -> None:
        self._obs: "weakref.WeakSet[Listener]" = weakref.WeakSet()  # does not keep listeners alive

    def attach(self, o: "Listener") -> None:
        self._obs.add(o)                         # register weakly

    def notify(self, msg: str) -> None:
        for o in list(self._obs):                # snapshot
            o.update(msg)                        # call each live listener

class Listener:
    def update(self, msg: str) -> None:
        print("got", msg)

s = Subject()
l = Listener()
s.attach(l)
s.notify("one")                                  # listener alive
del l                                            # drop last strong ref (CPython frees immediately)
s.notify("two")                                  # nothing printed: auto-removed

# Output:
# got one
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: removing from the list while iterating over it
obs = [1, 2, 3, 4]
for o in obs:
    if o % 2 == 0:
        obs.remove(o)                            # skips elements!
print(obs)                                       # [1, 3] looks right here, but...

obs = [2, 4, 6]
for o in obs:
    obs.remove(o)                                # skips every other one
print(obs)                                       # [4]

# ✅ Correct: iterate over a copy -> for o in list(obs)

# Output:
# [1, 3]
# [4]
```

---

## 🎯 Interview Tip (1 line)
Say: "Observer decouples publisher from subscribers; I iterate over a copy, return an unsubscribe handle, and use weak references to avoid memory leaks."

---

## 🔗 Related Questions
→ Q096 (event emitter) | Q097 (pub/sub) | Q170 (weak references) | Q187 (event bus)
