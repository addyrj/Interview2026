---

# Q260. Exception Groups and add_note (3.11+)
# Category: PYTHONIC + MODERN PYTHON FEATURES
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Python 3.11 added `ExceptionGroup`, `except*`, and `BaseException.add_note()`. Show how to raise several errors at once, handle them by type, and attach extra context to an exception.

```python
# NOT RUN (question stub; it just raises)
raise ExceptionGroup("batch failed", [ValueError("bad"), TypeError("wrong")])
# How do you catch ValueError and TypeError separately?
```

---

## 💡 Quick Concept (2 lines only)
`ExceptionGroup` bundles multiple exceptions (used by `asyncio.TaskGroup`). `except*` matches by type inside the group and each clause gets a sub-group of matches. `add_note("text")` appends context shown in the traceback.
हिंदी: `ExceptionGroup` कई errors एक साथ रखता है, `except*` हर type को अलग से पकड़ता है, और `add_note` extra जानकारी जोड़ता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
def run() -> None:
    try:
        raise ExceptionGroup(                    # bundle several errors
            "batch failed",                      # group message
            [ValueError("bad value"), TypeError("wrong type"), ValueError("another")],
        )
    except* ValueError as eg:                    # matches only the ValueErrors
        print("ValueErrors:", [str(e) for e in eg.exceptions])  # eg is an ExceptionGroup
    except* TypeError as eg:                     # matches the TypeError (runs too!)
        print("TypeErrors:", [str(e) for e in eg.exceptions])   # both clauses run

run()                                            # no error escapes: all were handled

# add_note: attach context to an exception
try:
    try:
        int("abc")                               # raises ValueError
    except ValueError as e:
        e.add_note("while parsing user age")     # add context without wrapping
        e.add_note("row 42")                     # notes accumulate in a list
        raise                                    # re-raise the same exception
except ValueError as e:
    print(e.__notes__)                           # notes are stored in __notes__

# Unhandled leftovers propagate
try:
    try:
        raise ExceptionGroup("g", [ValueError("v"), KeyError("k")])
    except* ValueError:                          # handles only ValueError
        print("handled ValueError")
except ExceptionGroup as rest:                   # KeyError remains in a new group
    print(type(rest).__name__, [type(x).__name__ for x in rest.exceptions])

# Output:
# ValueErrors: ['bad value', 'another']
# TypeErrors: ['wrong type']
# ['while parsing user age', 'row 42']
# handled ValueError
# ExceptionGroup ['KeyError']
```

---

## 🔍 Why This Works (3 lines max)
`except*` splits the group: matching exceptions go to that clause, the rest keep propagating (re-wrapped in an `ExceptionGroup`). Unlike normal `except`, several `except*` clauses can run for one group. `add_note` stores strings in `__notes__`, which are printed under the traceback.
हिंदी: normal `except` में सिर्फ एक clause चलता है, पर `except*` में group के हिसाब से कई clauses चल सकते हैं।

---

## ⚡ Alternative Solution
```python
# Real use: asyncio.TaskGroup raises an ExceptionGroup
import asyncio                                   # event loop

async def fail(msg: str) -> None:
    await asyncio.sleep(0.01)                    # simulated I/O
    raise ValueError(msg)                        # each task fails

async def main() -> None:
    try:
        async with asyncio.TaskGroup() as tg:    # structured concurrency
            tg.create_task(fail("one"))          # task 1 fails
            tg.create_task(fail("two"))          # task 2 fails
    except* ValueError as eg:                    # catches both
        print(sorted(str(e) for e in eg.exceptions))

asyncio.run(main())                              # run the demo

# Output:
# ['one', 'two']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: plain except does NOT match the contents of an ExceptionGroup
try:
    raise ExceptionGroup("g", [ValueError("v")])
except ValueError:                               # never matches: the raised type is ExceptionGroup
    print("caught")
except ExceptionGroup:
    print("only ExceptionGroup matched")         # ✅ the group itself is caught here

# ✅ Correct: use except* ValueError to match members of the group

# Output:
# only ExceptionGroup matched
```

---

## 🎯 Interview Tip (1 line)
Say: "`except*` is for ExceptionGroup (TaskGroup, concurrent errors); you can't mix `except` and `except*` in one try, and `add_note` adds context without losing the original exception."

---

## 🔗 Related Questions
→ Q044 (exception chaining) | Q208 (handle multiple async errors) | Q130 (too-broad except) | Q042 (try/except/else/finally)
