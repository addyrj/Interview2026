---

# Q200. Build undo/redo system
# Category: REAL WORLD PROBLEMS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a `History` class with `push(state)`, `undo()`, `redo()`, `can_undo`, `can_redo`. A new `push` after an undo must discard the redo branch.

```python
h = History("")
h.push("a"); h.push("ab")
h.undo()   # 'a'
h.redo()   # 'ab'
```

---

## 💡 Quick Concept (2 lines only)
Two stacks: `undo` holds the past, `redo` holds undone states. A new edit clears `redo`.
हिंदी: दो stacks — undo और redo; नई edit करने पर redo stack खाली हो जाता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Generic, TypeVar                  # generic history container

T = TypeVar("T")                                     # type of the state we track

class History(Generic[T]):
    def __init__(self, initial: T) -> None:
        self._undo: list[T] = []                     # past states (stack)
        self._redo: list[T] = []                     # undone states (stack)
        self.current: T = initial                    # present state

    def push(self, state: T) -> None:
        self._undo.append(self.current)              # save present into undo stack
        self.current = state                         # move to the new state
        self._redo.clear()                           # new edit kills the redo branch

    def undo(self) -> T:
        if self._undo:                               # only if there is history
            self._redo.append(self.current)          # present becomes redo-able
            self.current = self._undo.pop()          # go back one step
        return self.current                          # return (possibly unchanged) state

    def redo(self) -> T:
        if self._redo:                               # only if something was undone
            self._undo.append(self.current)          # present goes back to undo stack
            self.current = self._redo.pop()          # re-apply the undone state
        return self.current                          # return state

    @property
    def can_undo(self) -> bool:
        return bool(self._undo)                      # True if undo has items

    @property
    def can_redo(self) -> bool:
        return bool(self._redo)                      # True if redo has items

# ============================================
# TEST CASES
# ============================================
h = History("")                                      # start with empty text
h.push("a"); h.push("ab"); h.push("abc")             # three edits
print(h.undo(), h.undo())                            # Expected: ab a
print(h.redo())                                      # Expected: ab
h.push("abX")                                        # new edit after undo
print(h.can_redo, h.current)                         # Expected: False abX
print(h.undo(), h.undo(), h.undo())                  # Expected: ab a  (then stays '' at the start)

# --- Real output (Python 3.13) ---
# ab a
# ab
# False abX
# ab a
```

---

## 🔍 Why This Works (3 lines max)
`push` moves the current state onto the undo stack and clears redo. `undo` moves current to redo and pops from undo; `redo` does the reverse. Undo at the start of history is a safe no-op that returns the same state.
हिंदी: push पर redo clear, undo/redo में current state एक stack से दूसरे stack में जाती है।

---

## ⚡ Alternative Solution
```python
# ============================================
# ALTERNATIVE: Command pattern (store actions, not whole states)
# ============================================
from dataclasses import dataclass                    # tiny command class

@dataclass
class Append:
    text: str                                        # what this command adds
    def do(self, doc: list[str]) -> None:
        doc.append(self.text)                        # apply the change
    def undo(self, doc: list[str]) -> None:
        doc.pop()                                    # reverse the change

doc: list[str] = []                                  # the document
done: list[Append] = []                              # executed commands
undone: list[Append] = []                            # undone commands

def run(cmd: Append) -> None:
    cmd.do(doc); done.append(cmd); undone.clear()    # execute, record, drop redo branch

run(Append("Hello")); run(Append("World"))           # two edits
print(doc)                                           # Expected: ['Hello', 'World']
c = done.pop(); c.undo(doc); undone.append(c)        # undo last command
print(doc)                                           # Expected: ['Hello']
c = undone.pop(); c.do(doc); done.append(c)          # redo it
print(doc)                                           # Expected: ['Hello', 'World']

# --- Real output (Python 3.13) ---
# ['Hello', 'World']
# ['Hello']
# ['Hello', 'World']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: saving the SAME mutable object — every history entry changes together
state = {"n": 0}; undo = []
undo.append(state); state["n"] = 1; undo.append(state)
print(undo)   # [{'n': 1}, {'n': 1}]  (real run) — history is corrupted

# ✅ Correct: store immutable states or copies (copy.deepcopy / tuples / frozen dataclasses)
```

---

## 🎯 Interview Tip (1 line)
Say: "Two stacks, O(1) per operation; for big documents store commands/diffs (Command pattern) instead of full snapshots, and cap the stack size."

---

## 🔗 Related Questions
→ Q100 (stack) | Q188 (state manager) | Q267 (command pattern) | Q154 (stack class)
