---

# 165. dis Module
# हिंदी में: dis Module (Bytecode को पढ़ने वाला Disassembler)

---

## 🔵 Simple Definition (English)
The `dis` module shows the bytecode instructions Python generates for your code, in human-readable form. It helps you see what really happens behind a line of Python: which operations run, which constants are folded and where time is spent.

## 🔵 सरल परिभाषा (Hindi)
`dis` module आपके code के लिए Python द्वारा बनाए गए bytecode instructions को पढ़ने लायक रूप में दिखाता है। इससे आप देख सकते हैं कि Python की एक line के पीछे असल में क्या चलता है: कौन से operations, कौन से constants पहले ही जोड़ दिए गए और समय कहाँ जाता है।

---

## 🔴 Problem it Solves
Two pieces of code can look similar but behave differently: a loop versus `sum()`, a list comprehension versus `append`, `a + b + c` versus `"".join`. Guessing about performance is unreliable. `dis` shows the exact instructions so you can reason from facts, learn how the interpreter works, and debug surprises such as late-binding closures or why `x = 1 if True else 2` has no branch.

## 🔴 यह क्यों बना? (Hindi)
दो code टुकड़े एक जैसे दिख सकते हैं पर अलग चलते हैं: loop बनाम `sum()`, list comprehension बनाम `append`, `a + b + c` बनाम `"".join`। Performance का अंदाज़ा लगाना भरोसेमंद नहीं है। `dis` सटीक instructions दिखाता है ताकि आप तथ्यों से सोचें, interpreter को समझें और आश्चर्यजनक बातें debug करें, जैसे late-binding closures या `x = 1 if True else 2` में branch क्यों नहीं है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python compiles your function into a code object (bytecode)
Step 2 → dis.dis(fn) reads fn.__code__.co_code
Step 3 → It decodes each 2-byte instruction into: offset, opname, arg, argval
Step 4 → It prints a table: line number | offset | OPNAME | arg (meaning)
Step 5 → dis.get_instructions(fn) gives the same data as Instruction objects
Step 6 → dis.Bytecode(fn) wraps it for iteration and .dis() text
```

How to read one line:  `LOAD_FAST_LOAD_FAST 1 (a, b)` means "push local variables a and b on the stack", `BINARY_OP 0 (+)` means "pop two values, add them, push the result", `RETURN_VALUE` means "pop and return".

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python आपके function को code object (bytecode) में compile करता है
Step 2 → dis.dis(fn) fn.__code__.co_code पढ़ता है
Step 3 → हर 2-byte instruction को decode करता है: offset, opname, arg, argval
Step 4 → Table print करता है: line number | offset | OPNAME | arg (अर्थ)
Step 5 → dis.get_instructions(fn) वही data Instruction objects में देता है
Step 6 → dis.Bytecode(fn) उसे iteration और .dis() text के लिए wrap करता है
```

एक line कैसे पढ़ें:  `LOAD_FAST_LOAD_FAST 1 (a, b)` का मतलब "local variables a और b को stack पर रखो", `BINARY_OP 0 (+)` का मतलब "दो values निकालो, जोड़ो, नतीजा रखो", `RETURN_VALUE` का मतलब "निकालो और लौटाओ"।

---

## 🟡 Real World Example
A performance engineer at a fintech company sees that a hot path does `total = total + x` for 10 million rows. Using `dis`, they compare a loop to `sum(...)`: the loop executes extra instructions on every iteration, while `sum` runs inside C. In interviews, "what does Python do for `a, b = b, a`?" is answered with `dis`.

## 🟡 Real Example Hindi mein
Fintech कंपनी के performance engineer को दिखता है कि hot path में 1 करोड़ rows पर `total = total + x` चलता है। `dis` से वे loop और `sum(...)` की तुलना करते हैं: loop हर iteration में अतिरिक्त instructions चलाता है, जबकि `sum` C के अंदर चलता है। Interview में "`a, b = b, a` पर Python क्या करता है?" का जवाब `dis` से दिया जाता है।

---

## 💻 Code Example — Basic
```python
# Basic dis examples
import dis                                        # disassembler


def add(a: int, b: int) -> int:                   # sample function
    return a + b                                  # to be disassembled


dis.dis(add)                                      # print human-readable bytecode
print([i.opname for i in dis.get_instructions(add)])   # same info as data

# Output:
#   5           RESUME                   0
#
#   6           LOAD_FAST_LOAD_FAST      1 (a, b)
#               BINARY_OP                0 (+)
#               RETURN_VALUE
# ['RESUME', 'LOAD_FAST_LOAD_FAST', 'BINARY_OP', 'RETURN_VALUE']
```

(Line numbers and opcode names such as `LOAD_FAST_LOAD_FAST` and `RETURN_CONST` are Python 3.13 output. 3.10 and older, and even 3.11/3.12, print different names.)

## 💻 Code Example — Advanced
```python
# Production style: compare two implementations by bytecode and timing
import dis                                        # disassembler
import timeit                                     # micro benchmark
from collections import Counter                   # opcode counting


def loop_sum(n: int) -> int:                      # explicit loop version
    total: int = 0                                # accumulator
    for i in range(n):                            # loop
        total += i                                # add
    return total


def builtin_sum(n: int) -> int:                   # builtin version
    return sum(range(n))                          # C loop


def fold() -> int:                                # constant folding demo
    return 24 * 60 * 60                           # folded at compile time


def ops(fn) -> Counter[str]:                      # count each opcode name
    return Counter(i.opname for i in dis.get_instructions(fn))


print(len(list(dis.get_instructions(loop_sum))), len(list(dis.get_instructions(builtin_sum))))   # loop has more
print(ops(loop_sum)["BINARY_OP"], ops(builtin_sum)["BINARY_OP"])   # arithmetic ops executed per loop body
print([i.argval for i in dis.get_instructions(fold) if i.opname == "RETURN_CONST"])   # [86400]

t1: float = timeit.timeit(lambda: loop_sum(10_000), number=200)       # time the loop
t2: float = timeit.timeit(lambda: builtin_sum(10_000), number=200)    # time builtin
print("builtin faster:", t2 < t1)                 # almost always True

info = dis.code_info(fold)                        # summary text of a code object
print(info.splitlines()[0])                       # Name:              fold
print(dis.Bytecode(fold).dis().splitlines()[-1].split()[-2:])   # last line: RETURN_CONST 1 (86400)

# Output:
# 17 7
# 1 0
# [86400]
# builtin faster: True
# Name:              fold
# ['1', '(86400)']
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript (Node) |
|---------|--------|-------------------|
| See bytecode | `dis.dis(fn)` | `node --print-bytecode file.js` |
| Programmatic access | `dis.get_instructions` | none (internal) |
| Stack machine | yes | Ignition is a register machine |
| Stable across versions | no | no |

```python
# Python way
import dis
dis.dis("a + b")                                # disassemble a source string
```
```javascript
// JavaScript way - command line only
// node --print-bytecode --print-bytecode-filter=add script.js
function add(a, b) { return a + b; }
```

Key difference: Python lets you disassemble from inside the program, so you can write tests or tools around it. In Node you inspect bytecode only with V8 flags.

---

## 🟠 FastAPI Connection
You normally do not disassemble FastAPI code, but `dis` is handy for understanding costs in hot endpoints, and for explaining why `async def` handlers become coroutine objects (look for `RETURN_GENERATOR` in their bytecode). The demo below returns the opcodes of a handler.

```python
# FastAPI: debug endpoint that returns bytecode of a given handler
import dis                                        # disassembler
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # in-process client

app: FastAPI = FastAPI()                          # create app


@app.get("/ping")                                 # a normal route
def ping() -> dict[str, bool]:
    return {"ok": True}                           # trivial handler


@app.get("/debug/opcodes")                        # internal-only debug route
def opcodes() -> dict[str, list[str]]:
    names: list[str] = [i.opname for i in dis.get_instructions(ping)]   # opcodes of ping
    return {"ping": names}                        # return their names


client: TestClient = TestClient(app)              # test client
print(client.get("/debug/opcodes").json())        # opcode list (version dependent)

# Output:
# {'ping': ['RESUME', 'LOAD_CONST', 'LOAD_CONST', 'BUILD_MAP', 'RETURN_VALUE']}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Treating opcode counts as exact timings
✅ Correct: measure with `timeit` or a profiler; opcodes differ widely in cost

❌ Mistake 2: Relying on opcode names in production code
✅ Correct: use `dis` for learning only; names changed in 3.11, 3.12 and 3.13

❌ Mistake 3: Disassembling a decorated function and seeing wrapper code
✅ Correct: disassemble the original (`fn.__wrapped__` when `functools.wraps` is used)

```python
import dis, functools
def deco(f):
    @functools.wraps(f)
    def w(*a, **k): return f(*a, **k)
    return w
@deco
def g(): return 1
dis.dis(g.__wrapped__)                          # shows g's own code, not wrapper w
```

❌ Mistake 4: Expecting `dis` to show machine code or the specialised form
✅ Correct: use `dis.dis(fn, adaptive=True)` (3.11+) after the function ran a few times to see specialised instructions

---

## 🧠 Tricky Interview Question

```python
# What does the bytecode of this contain?
import dis
dis.dis("x = 1 if True else 2")
```
Answer (verified on 3.13): there is no conditional jump at all.
```
LOAD_CONST   1 (1)
STORE_NAME   0 (x)
RETURN_CONST 2 (None)
```
The compiler knows `True` is always true, so it removes the dead `else` branch and the test. Bytecode is not a literal translation of your source: constant folding and dead-branch elimination happen first.

---

## ⚫ Interview Questions + Answers

Q1: What does `dis.dis` show and why use it?
A1: The bytecode instructions of a function, class, module or source string. Use it to understand what the interpreter does, compare two implementations, and explain behaviour such as closures or optimisations.

Q2: What is a stack-based VM?
A2: Instructions push and pop values on an evaluation stack. `a + b` loads `a`, loads `b`, then `BINARY_OP` pops both and pushes the sum.

Q3: What is constant folding? Show with `dis`.
A3: The compiler computes constant expressions at compile time. `86400` replaces `24 * 60 * 60`, so the function contains one `RETURN_CONST 86400` and no multiplication.

Q4: What does the specialising adaptive interpreter (3.11+) change?
A4: Hot instructions are rewritten at runtime to faster, type-specific forms, for example `BINARY_OP` to an int-add variant. `dis.dis(fn, adaptive=True)` shows them.

Q5: How would you find out why a loop is slower than `sum()`?
A5: Use `dis` to see the extra instructions per iteration (load, add, store, jump), then confirm with `timeit`. The builtin runs the loop in C.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Learning or teaching how Python executes code
- Comparing two code styles
- Checking if an optimisation (folding, dead-code removal) happened

❌ Avoid when:
- Doing real profiling (use `cProfile`, `timeit`, `py-spy`)
- Building tools that depend on stable opcode names
- Trying to micro-optimise code that is not the bottleneck

---

## 📊 Visual Diagram
```
 return a + b                      evaluation stack
 ─────────────────────────────     ─────────────────
 LOAD_FAST a                       [a]
 LOAD_FAST b                       [a, b]
 BINARY_OP +                       [a+b]
 RETURN_VALUE                      []  -> value goes to caller

 columns of dis output:  line | offset | OPNAME | arg (human meaning)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Disassembler | Shows bytecode as text | bytecode को text में दिखाने वाला |
| Opcode | One instruction name | एक instruction का नाम |
| Stack machine | VM using a value stack | value stack वाली मशीन |
| `LOAD_FAST` | Push a local variable | local variable stack पर रखना |
| Constant folding | Compute constants early | constants पहले ही निकालना |
| Adaptive/specialised | Runtime-optimised instruction | runtime में तेज़ किया instruction |

---

## ⚡ 3-Line Summary
English: `dis` prints the bytecode behind your code. It shows stack operations, constant folding and the cost of loops versus builtins. Use it to learn and compare, but measure with `timeit`.
Hindi: `dis` आपके code के पीछे का bytecode दिखाता है। इसमें stack operations, constant folding और loop बनाम builtins की लागत दिखती है। सीखने और तुलना के लिए use करें, पर नापने के लिए `timeit`।

---

## ➡️ Next Topic
**166. Introspection in Python** — inspecting objects at runtime: type, attributes, methods and documentation.
