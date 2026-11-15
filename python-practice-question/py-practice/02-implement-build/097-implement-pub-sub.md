---

# Q097. Implement Pub/Sub
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement a `PubSub` class: `subscribe(topic, handler)` returns an **unsubscribe function**, and `publish(topic, message)` delivers the message to all current subscribers and returns how many received it. Publishers and subscribers must not know each other.

```python
unsub = bus.subscribe("news", handler)
bus.publish("news", "hello")   # handler called
unsub()                        # stop receiving
```

---

## 💡 Quick Concept (2 lines only)
Pub/sub decouples senders from receivers through named topics. Each subscription gets a unique id so it can be removed individually, even if the same function is subscribed twice.
हिंदी: Pub/sub में publisher और subscriber एक-दूसरे को नहीं जानते — बीच में topic होता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections import defaultdict  # auto-creating dicts
from typing import Any, Callable  # type hints


class PubSub:
    def __init__(self) -> None:
        self._topics: dict[str, dict[int, Callable[[Any], None]]] = defaultdict(dict)  # Step 1: topic -> {id: handler}
        self._next_id = 0  # Step 2: unique id counter

    def subscribe(self, topic: str, handler: Callable[[Any], None]) -> Callable[[], None]:
        sub_id = self._next_id  # Step 3: allocate id
        self._next_id += 1  # bump counter
        self._topics[topic][sub_id] = handler  # store handler

        def unsubscribe() -> None:  # Step 4: closure remembers topic + id
            self._topics[topic].pop(sub_id, None)  # safe even if called twice
        return unsubscribe  # hand it back to the subscriber

    def publish(self, topic: str, message: Any) -> int:
        handlers = list(self._topics.get(topic, {}).values())  # Step 5: snapshot before calling
        for h in handlers:
            h(message)  # deliver
        return len(handlers)  # number of receivers


# ============================================
# TEST CASES
# ============================================
bus = PubSub()  # create bus
unsub_a = bus.subscribe("news", lambda m: print("A got", m))  # subscriber A
bus.subscribe("news", lambda m: print("B got", m))  # subscriber B
bus.subscribe("sport", lambda m: print("C got", m))  # different topic
print(bus.publish("news", "hello"))  # Expected: A got hello / B got hello / 2
unsub_a()  # A unsubscribes
print(bus.publish("news", "again"))  # Expected: B got again / 1
print(bus.publish("weather", "rain"))  # Expected: 0
unsub_a()  # calling twice is harmless
```

---

## 🔍 Why This Works (3 lines max)
Topics map to `{id: handler}`, so each subscription is independent and removable in O(1). Returning an `unsubscribe` closure avoids having to pass the handler around.
हिंदी: हर subscription का अपना id है, इसलिए unsubscribe सुरक्षित और तेज़ है।

---

## ⚡ Alternative Solution
```python
import asyncio  # async queue variant
import fnmatch  # wildcard topic matching


class WildPubSub(PubSub):  # topics like "user.*"
    def publish(self, topic, message):
        n = 0  # receiver count
        for pattern, subs in list(self._topics.items()):  # check every stored pattern
            if fnmatch.fnmatch(topic, pattern):  # does it match?
                for h in list(subs.values()):
                    h(message)  # deliver
                    n += 1
        return n


w = WildPubSub()
w.subscribe("user.*", lambda m: print("user event", m))
print(w.publish("user.created", 1), w.publish("order.created", 2))  # Expected: user event 1 / 1 0


class AsyncPubSub:  # each subscriber owns an asyncio.Queue
    def __init__(self):
        self.subs = defaultdict(list)
    def subscribe(self, topic):
        q = asyncio.Queue(); self.subs[topic].append(q); return q  # subscriber reads from q
    async def publish(self, topic, msg):
        for q in self.subs[topic]:
            await q.put(msg)  # deliver to every queue


async def main():
    ps = AsyncPubSub(); q = ps.subscribe("t")
    await ps.publish("t", "m1"); await ps.publish("t", "m2")
    print(await q.get(), await q.get())  # Expected: m1 m2


asyncio.run(main())
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: storing handlers in a list and removing by function value
b = PubSub()
f = lambda m: print("got", m)
b.subscribe("t", f); b.subscribe("t", f)  # same handler subscribed twice
print(b.publish("t", "x"))  # got x / got x / 2  — removing by value would drop the wrong one
# ✅ Correct: unique subscription ids + an unsubscribe closure (as in the solution)
# ❌ Also: calling handlers on the live dict -> "dictionary changed size during iteration"
```

---

## 🎯 Interview Tip (1 line)
Say: "Topic dict of id-keyed handlers, publish over a snapshot, return an unsubscribe closure — and note the async variant with a queue per subscriber."

---

## 🔗 Related Questions
→ Q096 (event emitter) | Q098 (observable) | Q156 (complete pub/sub) | Q187 (event bus) | Q263 (observer pattern)
