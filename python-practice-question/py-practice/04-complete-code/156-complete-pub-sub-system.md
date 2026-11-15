---

# Q156. Complete Pub/Sub System
# Category: Complete the Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks (`____`) to finish a `PubSub` class with `subscribe` (returns an unsubscribe function), `publish`, and `unsubscribe`.

```python
from collections import defaultdict
from typing import Any, Callable

Handler = Callable[[Any], None]

class PubSub:
    def __init__(self) -> None:
        self._topics: dict[str, list[Handler]] = defaultdict(____)   # blank 1: default factory

    def subscribe(self, topic: str, handler: Handler) -> Callable[[], None]:
        self._topics[topic].____(handler)                            # blank 2: register handler
        return lambda: self.unsubscribe(topic, ____)                 # blank 3: which handler to remove

    def unsubscribe(self, topic: str, handler: Handler) -> None:
        if handler in self._topics[topic]:
            self._topics[topic].____(handler)                        # blank 4: remove it

    def publish(self, topic: str, data: Any) -> int:
        for handler in ____(self._topics[topic]):                    # blank 5: iterate over a COPY
            handler(data)
        return len(self._topics[topic])
```

---

## 💡 Quick Concept (2 lines only)
Publishers send messages to a topic; the bus calls every subscriber of that topic, so the two sides never know each other.
हिंदी: Pub/Sub में publisher और subscriber एक-दूसरे को नहीं जानते — बीच में topic का bus होता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections import defaultdict       # Step 1: auto-create list per topic
from typing import Any, Callable          # Step 2: type hints

Handler = Callable[[Any], None]           # Step 3: alias for a handler type

class PubSub:                             # Step 4: the message bus
    def __init__(self) -> None:           # constructor
        self._topics: dict[str, list[Handler]] = defaultdict(list)  # Blank 1 -> list

    def subscribe(self, topic: str, handler: Handler) -> Callable[[], None]:  # Step 5
        self._topics[topic].append(handler)                    # Blank 2 -> append
        return lambda: self.unsubscribe(topic, handler)        # Blank 3 -> handler

    def unsubscribe(self, topic: str, handler: Handler) -> None:  # Step 6
        if handler in self._topics[topic]:                     # only remove if present
            self._topics[topic].remove(handler)                # Blank 4 -> remove

    def publish(self, topic: str, data: Any) -> int:           # Step 7: notify everyone
        for handler in list(self._topics[topic]):              # Blank 5 -> list (a copy!)
            handler(data)                                      # call each subscriber
        return len(self._topics[topic])                        # how many are still subscribed

# ============================================
# TEST CASES
# ============================================
bus = PubSub()                                       # create the bus
received: list[str] = []                             # collect messages here
unsub_a = bus.subscribe("news", lambda d: received.append(f"A:{d}"))  # subscriber A
bus.subscribe("news", lambda d: received.append(f"B:{d}"))            # subscriber B
bus.publish("news", "hello")                         # both get it
print(received)                                      # Expected: ['A:hello', 'B:hello']
unsub_a()                                            # A unsubscribes
bus.publish("news", "bye")                           # only B gets it
print(received)                                      # Expected: ['A:hello', 'B:hello', 'B:bye']
print(bus.publish("other", 1))                       # Expected: 0  (no subscribers)

# Self-unsubscribing handler works because we iterate over a copy:
bus2 = PubSub()                                      # new bus
calls: list[int] = []                                # record calls
def once(d: int) -> None:                            # handler that removes itself
    calls.append(d)                                  # record
    bus2.unsubscribe("t", once)                      # mutate list during publish
bus2.subscribe("t", once)                            # subscribe
bus2.subscribe("t", lambda d: calls.append(d * 10))  # second handler must still run
bus2.publish("t", 1)                                 # publish once
print(calls)                                         # Expected: [1, 10]
```

---

## 🔍 Why This Works (3 lines max)
`defaultdict(list)` gives each topic its own handler list on first use. `subscribe` returns a closure that remembers `topic` and `handler`, giving a ready-made unsubscribe. Iterating over `list(...)` (a copy) stops a handler that unsubscribes itself from skipping the next one.
हिंदी: Copy पर loop करने से handler के बीच में unsubscribe होने पर भी कोई subscriber skip नहीं होता।

---

## ⚡ Alternative Solution
```python
# Using a set of handlers per topic and a decorator-style subscribe
from collections import defaultdict       # per-topic container
from typing import Any, Callable          # type hints

class PubSub2:                            # variant using sets (no duplicate handlers)
    def __init__(self) -> None:
        self._topics: dict[str, set[Callable[[Any], None]]] = defaultdict(set)  # set per topic

    def on(self, topic: str):             # decorator: @bus.on("x")
        def register(fn):                 # receives the function
            self._topics[topic].add(fn)   # sets ignore duplicates
            return fn                     # keep the function usable
        return register                   # return the real decorator

    def emit(self, topic: str, data: Any) -> None:
        for fn in tuple(self._topics[topic]):  # snapshot, order not guaranteed
            fn(data)                           # notify

bus = PubSub2()                           # create
out: list[str] = []                       # results
@bus.on("greet")                          # register via decorator
def hello(name: str) -> None:             # handler
    out.append(f"hi {name}")              # record
bus.emit("greet", "Ada")                  # publish
print(out)                                # Expected: ['hi Ada']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: mutating the list while iterating it -> skips handlers
class Bad:
    def __init__(self):
        self.handlers = []                      # shared list
    def publish(self, d):
        for h in self.handlers:                 # iterating the live list
            h(d)                                # a self-removing handler shifts the list

# ✅ Correct: iterate over a copy
#     for h in list(self.handlers): h(d)
```

---

## 🎯 Interview Tip (1 line)
Say: "Subscribe returns an unsubscribe function, and publish iterates over a copy so handlers can safely unsubscribe during dispatch."

---

## 🔗 Related Questions
→ Q096 (event emitter) | Q097 (implement pub/sub) | Q098 (observable) | Q263 (observer pattern) | Q187 (event bus)
