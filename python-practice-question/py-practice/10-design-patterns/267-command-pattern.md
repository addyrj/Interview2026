---

# Q267. Command Pattern
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement the Command pattern for a text editor: each action (`Insert`, `Delete`) is an object with `execute()` and `undo()`. An `Editor` invoker keeps a history so you can undo the last action.

---

## 💡 Quick Concept (2 lines only)
Command wraps a request as an object, so you can store, queue, log and undo it. Invoker only calls `execute()` — it does not know what the command does.
हिंदी: Command पैटर्न में हर action एक object बन जाता है, इसलिए उसे save, queue या undo किया जा सकता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Protocol  # Step 1: Protocol describes the command interface


class Command(Protocol):  # Step 2: every command must have execute + undo
    def execute(self) -> None: ...  # run the action
    def undo(self) -> None: ...  # reverse the action


class Document:  # Step 3: the receiver - the object that does real work
    def __init__(self) -> None:
        self.text = ""  # current text of the document


class Insert:  # Step 4: concrete command for appending text
    def __init__(self, doc: Document, s: str) -> None:
        self.doc, self.s = doc, s  # store receiver and the text to add

    def execute(self) -> None:
        self.doc.text += self.s  # append text to the document

    def undo(self) -> None:
        self.doc.text = self.doc.text[: -len(self.s)]  # remove what we added


class Delete:  # Step 5: concrete command for deleting last n chars
    def __init__(self, doc: Document, n: int) -> None:
        self.doc, self.n = doc, n  # store receiver and count
        self.removed = ""  # remember removed text so undo can restore it

    def execute(self) -> None:
        self.removed = self.doc.text[-self.n:]  # save the tail before cutting
        self.doc.text = self.doc.text[: -self.n]  # cut the last n chars

    def undo(self) -> None:
        self.doc.text += self.removed  # put the saved text back


class Editor:  # Step 6: the invoker - runs commands and keeps history
    def __init__(self) -> None:
        self.history: list[Command] = []  # stack of executed commands

    def run(self, cmd: Command) -> None:
        cmd.execute()  # execute the command
        self.history.append(cmd)  # remember it for undo

    def undo(self) -> None:
        if self.history:  # only undo if something was executed
            self.history.pop().undo()  # pop latest command and reverse it


# ============================================
# TEST CASES
# ============================================
doc = Document()  # create receiver
ed = Editor()  # create invoker
ed.run(Insert(doc, "Hello"))  # add "Hello"
ed.run(Insert(doc, " World"))  # add " World"
print(repr(doc.text))  # Expected: 'Hello World'
ed.run(Delete(doc, 6))  # delete " World"
print(repr(doc.text))  # Expected: 'Hello'
ed.undo()  # undo the delete
print(repr(doc.text))  # Expected: 'Hello World'
ed.undo()  # undo second insert
ed.undo()  # undo first insert
ed.undo()  # nothing left - safe no-op
print(repr(doc.text))  # Expected: ''
```

---

## 🔍 Why This Works (3 lines max)
The editor only knows the `execute`/`undo` interface, never the details. Each command stores the state it needs (like `removed`) to reverse itself. A history stack gives undo for free.
हिंदी: Editor सिर्फ execute/undo जानता है; हर command अपना undo खुद संभालता है, stack से undo मिल जाता है।

---

## ⚡ Alternative Solution
```python
# Pythonic: commands as closures (function pairs) - no classes needed
from collections.abc import Callable  # type for callables

history: list[tuple[Callable[[], None], Callable[[], None]]] = []  # (do, undo) pairs
items: list[int] = []  # the receiver is a plain list


def add(x: int) -> None:
    do = lambda: items.append(x)  # action: append x
    undo = lambda: items.pop()  # reverse: pop it back
    do()  # execute right away
    history.append((do, undo))  # store the pair


add(1)  # items -> [1]
add(2)  # items -> [1, 2]
print(items)  # Expected: [1, 2]
history.pop()[1]()  # call the undo of the last command
print(items)  # Expected: [1]
```

---

## ⚠️ Common Mistake
```python
# NOT RUN - illustrative
# ❌ Wrong: Delete.undo() cannot restore text because nothing was saved
class BadDelete:
    def execute(self):
        self.doc.text = self.doc.text[:-self.n]  # text is lost forever
    def undo(self):
        ...  # impossible - state was never stored

# ✅ Correct: save the removed text in execute() (see Delete above)
```

---

## 🎯 Interview Tip (1 line)
Say: "Command = request as object; gives undo/redo, queues, macros and logging — used in editors, task queues, CLI tools."

---

## 🔗 Related Questions
→ Q200 (undo/redo system) | Q264 (strategy) | Q263 (observer)
