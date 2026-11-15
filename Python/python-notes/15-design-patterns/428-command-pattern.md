---

# 428. Command Pattern
# हिंदी में: Command Pattern (Action को object बनाना)

---

## 🔵 Simple Definition (English)
Command turns an action into an object that has `execute()` and often `undo()`. Because the action is now data, you can store it, queue it, log it, send it elsewhere, or undo it later.

## 🔵 सरल परिभाषा (Hindi)
Command किसी action को ऐसा object बना देता है जिसमें `execute()` और अक्सर `undo()` होता है। Action अब data है, इसलिए उसे store, queue, log, कहीं और भेज या बाद में undo किया जा सकता है।

---

## 🔴 Problem it Solves
A direct call like `wallet.withdraw(200)` happens immediately and leaves no trace. You cannot undo it, retry it later, show it in an audit log, or put it in a job queue. Command wraps the call plus its arguments into an object so the caller (invoker) and the real worker (receiver) are decoupled.

## 🔴 यह क्यों बना? (Hindi)
`wallet.withdraw(200)` जैसा सीधा call तुरंत हो जाता है और कोई निशान नहीं छोड़ता। उसे undo, बाद में retry, audit log में दिखाना या job queue में डालना संभव नहीं। Command call और उसके arguments को object में लपेट देता है ताकि caller (invoker) और असली काम करने वाला (receiver) अलग रहें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a Command interface: execute() and undo()
Step 2 → Each command stores its receiver and its arguments (Deposit(wallet, 500))
Step 3 → The invoker calls cmd.execute()
Step 4 → If execute() succeeds, the invoker pushes cmd on a history stack
Step 5 → undo() pops the stack and calls cmd.undo(); the command goes to the redo stack
Step 6 → A new command clears the redo stack
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Command interface तय करो: execute() और undo()
Step 2 → हर command अपना receiver और arguments रखता है (Deposit(wallet, 500))
Step 3 → Invoker cmd.execute() बुलाता है
Step 4 → execute() सफल हो तो invoker cmd को history stack में डालता है
Step 5 → undo() stack से pop करके cmd.undo() बुलाता है; command redo stack में जाता है
Step 6 → नया command आने पर redo stack खाली हो जाता है
```

---

## 🟡 Real World Example
Text editors (undo/redo), Celery/RQ jobs (a task = a command with arguments, run later), database migrations (up/down), and a wallet or ledger with an audit trail. A Swiggy-style system stores 'RefundOrder(order_id)' commands in a queue so a worker can retry them.

## 🟡 Real Example Hindi mein
Text editors (undo/redo), Celery/RQ jobs (task = arguments वाला command, बाद में चलता है), database migrations (up/down), और audit trail वाला wallet या ledger। Swiggy जैसा system 'RefundOrder(order_id)' commands queue में रखता है ताकि worker उन्हें retry कर सके।

---

## 💻 Code Example — Basic
```python
# Basic Command: wrap an action as an object with execute() and undo()
from typing import Protocol                   # interface


class Command(Protocol):
    def execute(self) -> None: ...
    def undo(self) -> None: ...


class Editor:
    def __init__(self) -> None:
        self.text: str = ""                   # document text


class AppendCommand:
    def __init__(self, ed: Editor, s: str) -> None:
        self.ed, self.s = ed, s               # receiver and data

    def execute(self) -> None:
        self.ed.text += self.s                # do the action

    def undo(self) -> None:
        self.ed.text = self.ed.text[: -len(self.s)]   # reverse it


ed: Editor = Editor()
history: list[Command] = []                   # stack of executed commands
for word in ("Hello", " World"):
    cmd = AppendCommand(ed, word)
    cmd.execute()
    history.append(cmd)
print(ed.text)
history.pop().undo()                          # undo last
print(repr(ed.text))

# Output:
# Hello World
# 'Hello'
```

## 💻 Code Example — Advanced
```python
# Production style: wallet commands with undo/redo stack, validation, and an audit log
from dataclasses import dataclass, field      # data classes
from typing import Protocol                   # interface


class Command(Protocol):
    def execute(self) -> None: ...
    def undo(self) -> None: ...


class InsufficientFunds(Exception):
    pass


@dataclass
class Wallet:
    balance: int = 0


@dataclass
class Deposit:
    w: Wallet
    amount: int
    def execute(self) -> None: self.w.balance += self.amount
    def undo(self) -> None: self.w.balance -= self.amount


@dataclass
class Withdraw:
    w: Wallet
    amount: int
    def execute(self) -> None:
        if self.w.balance < self.amount:      # validate BEFORE changing state
            raise InsufficientFunds(f"balance {self.w.balance} < {self.amount}")
        self.w.balance -= self.amount
    def undo(self) -> None: self.w.balance += self.amount


@dataclass
class Invoker:
    done: list[Command] = field(default_factory=list)
    redo_stack: list[Command] = field(default_factory=list)
    log: list[str] = field(default_factory=list)

    def run(self, cmd: Command) -> None:
        cmd.execute()                         # may raise: then nothing is recorded
        self.done.append(cmd)
        self.redo_stack.clear()               # new action invalidates redo
        self.log.append(repr(cmd))

    def undo(self) -> None:
        if self.done:
            cmd = self.done.pop(); cmd.undo(); self.redo_stack.append(cmd)

    def redo(self) -> None:
        if self.redo_stack:
            cmd = self.redo_stack.pop(); cmd.execute(); self.done.append(cmd)


w: Wallet = Wallet()
inv: Invoker = Invoker()
inv.run(Deposit(w, 500)); inv.run(Withdraw(w, 200))
print(w.balance)                              # 300
inv.undo(); print(w.balance)                  # 500
inv.redo(); print(w.balance)                  # 300
try:
    inv.run(Withdraw(w, 1000))
except InsufficientFunds as e:
    print("Error:", e)
print(len(inv.log), w.balance)                # failed command not logged

# Output:
# 300
# 500
# 300
# Error: balance 300 < 1000
# 2 300
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Simple command | closure / `functools.partial` | closure / arrow function |
| Full command | class with `execute`/`undo` | class with `execute`/`undo` |
| Job queue | Celery, RQ, `asyncio.Queue` | BullMQ, Redux actions |
| Undo/redo | two stacks | two stacks (Redux time-travel) |

```python
# Python way
from functools import partial
cmd = partial(send_email, "a@x.com")       # action + arguments frozen into a callable
queue.append(cmd)                          # run later
queue.pop()()                              # execute
```
```javascript
// JavaScript way
const cmd = () => sendEmail("a@x.com");    // closure = tiny command
queue.push(cmd);                           // run later
queue.pop()();                             // execute
```

Key difference: Redux 'actions' are commands as plain data (`{type: 'ADD', payload}`) handled by reducers. In Python, a callable or `functools.partial` is the lightest command; use a class only when you need `undo()`, logging, or serialization.

---

## 🟠 FastAPI Connection
FastAPI endpoints that return 202 Accepted and queue a command are Command in action: the route builds the command and hands it to `BackgroundTasks`, Celery, or an `asyncio.Queue`. The command object can be stored in a database as an audit record.

```python
# FastAPI example (run with fastapi.testclient — no server needed)
from typing import Callable
from fastapi import FastAPI
from fastapi.testclient import TestClient

app: FastAPI = FastAPI()
queue: list[Callable[[], str]] = []           # commands stored now, run later (like a job queue)


def make_email_job(to: str) -> Callable[[], str]:
    return lambda: f"emailed {to}"            # closure = tiny command object


@app.post("/jobs")
def enqueue(to: str) -> dict[str, int]:
    queue.append(make_email_job(to))
    return {"queued": len(queue)}


@app.post("/jobs/run")
def run_all() -> dict[str, list[str]]:
    results = [job() for job in queue]        # execute stored commands
    queue.clear()
    return {"results": results}


c = TestClient(app)
c.post("/jobs", params={"to": "a@x.com"}); c.post("/jobs", params={"to": "b@x.com"})
print(c.post("/jobs/run").json())

# Output:
# {'results': ['emailed a@x.com', 'emailed b@x.com']}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Recording the command before `execute()` succeeds
✅ Correct: execute first, record only on success

```python
# Wrong
history.append(cmd); cmd.execute()    # if execute raises, history has a command that never ran
# Right
cmd.execute()                         # may raise
history.append(cmd)                   # only successful commands can be undone
```

❌ Mistake 2: `undo()` that is not an exact inverse
✅ Correct: store what is needed to reverse (or validate in `execute`)

```python
# Wrong: text[:-len(s)]  when s == ""  -> text[:-0] -> "" (wipes everything!)
# Right
self.ed.text = self.ed.text[: len(self.ed.text) - len(self.s)]
```

❌ Mistake 3: Not clearing the redo stack after a new command
✅ Correct: clear it

```python
# Wrong: redo() after a new action replays an old, now-invalid command
# Right: in run(): self.redo_stack.clear()
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
text = "Hello"
s = ""                                        # command appended empty string
print(repr(text[: -len(s)]))
```
Answer: Output: `''` (empty string). `-len(s)` with `s = ''` is `-0`, which is `0`, so `text[:0]` is an empty slice. An `undo()` written as `text[:-len(s)]` therefore wipes the whole document when the appended string was empty. Use `text[: len(text) - len(s)]` or store the previous text in the command (a memento).

---

## ⚫ Interview Questions + Answers

Q1: What are the parts of the Command pattern?
A1: Command (execute/undo), Receiver (does the real work, e.g. Wallet), Invoker (runs commands and keeps history), and Client (creates commands).

Q2: How do you implement undo/redo?
A2: Keep two stacks. On run: execute, push to `done`, clear `redo`. On undo: pop from `done`, call `undo()`, push to `redo`. On redo: pop from `redo`, call `execute()`, push to `done`.

Q3: Command vs Strategy?
A3: Strategy swaps HOW something is done (an algorithm). Command packages WHAT to do (an action with arguments) so it can be delayed, queued, or reversed.

Q4: Why is Command useful for task queues?
A4: A command is serializable data (name + arguments). Celery stores it in Redis/RabbitMQ and a worker runs it later, possibly with retries.

Q5: What about operations that cannot be undone?
A5: Sending an email cannot be un-sent. Either mark the command non-undoable, or make `undo()` do a compensating action (send a correction, issue a refund).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Undo/redo or audit history
- Queue, delay, schedule, or retry actions
- Macro commands (a batch of actions)
- Decouple the button/route from the business operation

❌ Avoid when:
- A simple direct function call is enough
- Actions are irreversible and need no history
- Creating a class per tiny action adds noise: use closures

---

## 📊 Visual Diagram
```
Invoker.run(Deposit(w,500))   -> execute -> balance 500 -> done=[Deposit]
Invoker.run(Withdraw(w,200))  -> execute -> balance 300 -> done=[Deposit,Withdraw]
Invoker.undo()                -> Withdraw.undo -> balance 500; redo=[Withdraw]
Invoker.redo()                -> Withdraw.execute -> balance 300
Invoker.run(Withdraw(w,1000)) -> raises InsufficientFunds, NOT recorded
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Command | Action as an object | Object बना हुआ action |
| Invoker | Runs commands, keeps history | Commands चलाने वाला, history रखने वाला |
| Receiver | Object that does the real work | असली काम करने वाला object |
| Undo/Redo | Reverse/replay an action | Action उलटना/दोहराना |
| Memento | Saved previous state | सहेजी हुई पुरानी state |

---

## ⚡ 3-Line Summary
English: Command wraps an action and its arguments in an object with `execute()` and `undo()`. This allows history, undo/redo, queues, retries and audit logs. Record a command only after it succeeds, and make `undo()` a true inverse.
Hindi: Command किसी action और उसके arguments को `execute()` और `undo()` वाले object में लपेटता है। इससे history, undo/redo, queues, retries और audit logs संभव होते हैं। Command तभी record करें जब वह सफल हो, और `undo()` को सही उलट बनाएं।

---

## ➡️ Next Topic
**429. Repository Pattern** — hide the database behind a collection-like interface.
