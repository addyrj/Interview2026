---

# Q187. Build Event Bus
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build an `EventBus` with `on(event, handler)`, `once(event, handler)`, `off(event, handler)` and `emit(event, *args)`. `on` must return an unsubscribe function, and handlers may safely unsubscribe themselves during `emit`.

```python
bus.on("greet", print)
bus.emit("greet", "hi")
```

---

## 💡 Quick Concept (2 lines only)
A dict mapping event name -> list of handlers (`defaultdict(list)`). `emit` iterates over a COPY of the list so removal during iteration is safe.
हिंदी: Event के नाम से handlers की list रखो; emit पर list की copy पर loop चलाओ ताकि बीच में unsubscribe सुरक्षित रहे।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections import defaultdict  # auto-list dict
from typing import Any, Callable  # type hints

class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[..., Any]]] = defaultdict(list)  # event -> handlers

    def on(self, event: str, handler: Callable[..., Any]) -> Callable[[], None]:
        self._handlers[event].append(handler)  # subscribe
        return lambda: self.off(event, handler)  # return an unsubscribe function

    def once(self, event: str, handler: Callable[..., Any]) -> None:
        def wrapper(*a: Any, **kw: Any) -> None:
            self.off(event, wrapper)  # remove itself first
            handler(*a, **kw)  # then run
        self.on(event, wrapper)  # subscribe wrapper

    def off(self, event: str, handler: Callable[..., Any]) -> None:
        if handler in self._handlers.get(event, []):
            self._handlers[event].remove(handler)  # unsubscribe

    def emit(self, event: str, *a: Any, **kw: Any) -> int:
        handlers = list(self._handlers.get(event, []))  # copy: safe if handlers unsubscribe
        for h in handlers:
            h(*a, **kw)  # call each
        return len(handlers)  # how many ran

# ============================================
# TEST CASES
# ============================================
bus = EventBus()  # create bus
off = bus.on("greet", lambda n: print("hello", n))  # permanent handler
bus.once("greet", lambda n: print("once", n))  # one-shot handler
print(bus.emit("greet", "Aditya"))  # Expected: hello Aditya / once Aditya / 2
print(bus.emit("greet", "Ravi"))  # Expected: hello Ravi / 1
off()  # unsubscribe
print(bus.emit("greet", "Neha"))  # Expected: 0
print(bus.emit("nobody"))  # Expected: 0
```

---

## 🔍 Why This Works (3 lines max)
`on` returns a closure that remembers `(event, handler)` so callers can unsubscribe without keeping references. `once` wraps the handler so it removes itself before running. Copying the list stops "mutated during iteration" skips.
हिंदी: `on` unsubscribe function लौटाता है; `once` खुद को हटाकर चलता है; list की copy से iteration सुरक्षित रहता है।

---

## ⚡ Alternative Solution
```python
import asyncio  # async
from collections import defaultdict  # dict

class AsyncBus:  # handlers are coroutines, run concurrently
    def __init__(self) -> None:
        self._h = defaultdict(list)  # handlers

    def on(self, event, coro_fn) -> None:
        self._h[event].append(coro_fn)  # subscribe coroutine function

    async def emit(self, event, *a):
        results = await asyncio.gather(*(h(*a) for h in self._h[event]), return_exceptions=True)  # run all concurrently
        return results  # handler results/exceptions

async def h1(x): await asyncio.sleep(0.01); return f"h1:{x}"  # fast handler
async def h2(x): raise RuntimeError("h2 failed")  # failing handler

async def main():
    bus = AsyncBus()  # bus
    bus.on("e", h1); bus.on("e", h2)  # two handlers
    print(await bus.emit("e", 5))  # Expected: ['h1:5', RuntimeError('h2 failed')]
asyncio.run(main())
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: iterating the live list while a handler removes itself skips the next handler (not run)
# for h in self._handlers[event]:   # once() removes from this list mid-loop!
#     h(*a)

# ❌ Also: one failing handler stops all the rest

# ✅ Correct: iterate over list(self._handlers[event]) (a copy); decide if errors should be isolated
```

---

## 🎯 Interview Tip (1 line)
Say: "Observer/pub-sub: decoupled producers and consumers; I return an unsubscribe handle to avoid memory leaks."

---

## 🔗 Related Questions
→ Q096 (event emitter) | Q097 (pub/sub) | Q156 (complete pub/sub) | Q263 (observer pattern)
