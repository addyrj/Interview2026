---

# 025. Python Indentation Rules
# हिंदी में: Python के Indentation नियम

---

## 🔵 Simple Definition (English)
In Python, **indentation (leading whitespace) is the syntax**. Instead of `{ }` braces, Python uses the amount of space at the start of a line to decide which statements belong to a block (an `if`, `for`, `def`, `class`, `try`, etc.). The standard is 4 spaces per level.

## 🔵 सरल परिभाषा (Hindi)
Python में **indentation (line के शुरू की खाली जगह) ही syntax है**। `{ }` braces की जगह Python line के आगे की spacing से तय करता है कि कौन सी statements किस block (`if`, `for`, `def`, `class`, `try` आदि) की हैं। Standard 4 spaces प्रति level है।

---

## 🔴 Problem it Solves
In C/Java/JS, braces define blocks but developers still indent for readability. The two can disagree: code *looks* like it is inside an `if` but the braces say otherwise, which causes real bugs. Python removes this gap: what you see is what runs. One way to write blocks means all Python code looks alike, so reading other people's code is easy.

## 🔴 यह क्यों बना? (Hindi)
C/Java/JS में braces block तय करते हैं, फिर भी developers readability के लिए indent करते हैं। दोनों में फर्क आ जाए तो code देखने में `if` के अंदर लगता है पर असल में बाहर होता है, यानी bug। Python यह gap खत्म करता है: जो दिखता है वही चलता है। Block लिखने का एक ही तरीका है, इसलिए सबका code एक जैसा दिखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → A line ending with ":" (if/for/while/def/class/try/with/else...) opens a block
Step 2 → The NEXT line must be indented more than the header line
Step 3 → The tokenizer keeps a stack of indentation levels
Step 4 → Deeper indent  → emits an INDENT token  (block starts)
Step 5 → Shallower indent → emits DEDENT token(s) (block ends)
Step 6 → A dedent must return to a level that is already on the stack,
         else: IndentationError: unindent does not match any outer indentation level
Step 7 → Blank lines and comment-only lines do not affect indentation
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → ":" पर खत्म होने वाली line (if/for/def/class...) block शुरू करती है
Step 2 → अगली line header से ज्यादा indent होनी चाहिए
Step 3 → Tokenizer indentation levels का stack रखता है
Step 4 → ज्यादा indent → INDENT token (block शुरू)
Step 5 → कम indent → DEDENT token (block खत्म)
Step 6 → Dedent किसी पुराने level पर ही उतरना चाहिए, वरना IndentationError
Step 7 → Blank lines और सिर्फ comment वाली lines गिनी नहीं जातीं
```

---

## 🟡 Real World Example
In a Zomato-style order service, `if order.is_paid:` is followed by an indented block that assigns a delivery partner. A developer adds one more line but accidentally dedents it by one level: now "send notification" runs for *every* order, paid or not. Python code reviewers catch this visually because the structure is the code. Teams enforce 4 spaces automatically with `black`, `ruff format` and an `.editorconfig` file, so indentation errors never reach production.

## 🟡 Real Example Hindi mein
Zomato जैसी order service में `if order.is_paid:` के नीचे indented block delivery partner assign करता है। कोई developer एक line जोड़ता है पर गलती से एक level कम indent कर देता है: अब "notification भेजो" हर order के लिए चलेगा, paid हो या न हो। Python में structure ही code है, इसलिए review में यह दिख जाता है। Teams `black`, `ruff format` और `.editorconfig` से 4 spaces automatic enforce करती हैं।

---

## 💻 Code Example — Basic
```python
# Indentation basics: 4 spaces per level

age: int = 20                                   # top level: no indentation

if age >= 18:                                   # header ends with a colon
    print("adult")                              # inside if: 4 spaces
    if age >= 21:                               # nested if: still inside outer if
        print("can drink in some countries")    # 8 spaces: inside inner if
    else:                                       # else aligns with ITS if (4 spaces)
        print("under 21")                       # Output: under 21
else:                                           # aligns with outer if (0 spaces)
    print("minor")                              # not executed

print("this runs always")                       # back at level 0 = outside the if

# for loop with a block of several lines
for i in range(3):                              # header with colon
    square: int = i * i                         # line 1 of the body
    print(i, square)                            # line 2 of the body, same indent
# Output:
# 0 0
# 1 1
# 2 4

# Function body must be indented
def hello(name: str) -> str:                    # def header
    greeting: str = f"Hello {name}"             # body line 1
    return greeting                             # body line 2

print(hello("Priya"))                           # Output: Hello Priya

# Empty block needs "pass"
def todo() -> None:                             # function we will write later
    pass                                        # placeholder: does nothing

# Long expressions can continue inside brackets with any indent
total: int = (1 +
              2 +
              3)                                # continuation lines inside ( )
print(total)                                    # Output: 6
```

## 💻 Code Example — Advanced
```python
# Advanced indentation: detect errors with compile(), tokenize, and style rules
import ast                                      # parse code to a syntax tree
import io                                       # in-memory file for tokenize
import textwrap                                 # dedent helper
import tokenize                                 # see INDENT / DEDENT tokens


def check_syntax(source: str) -> str:
    """Return 'ok' or the name of the syntax/indent error."""
    try:
        compile(source, "<demo>", "exec")       # try to compile without running
        return "ok"                             # compiled fine
    except IndentationError as exc:             # subclass of SyntaxError, check FIRST
        return f"IndentationError: {exc.msg}"   # message from Python
    except SyntaxError as exc:                  # other syntax problems
        return f"SyntaxError: {exc.msg}"


def show_tokens(source: str) -> list[str]:
    """List INDENT/DEDENT tokens, to see how Python reads blocks."""
    names: list[str] = []                       # collected token names
    reader = io.StringIO(source).readline       # readline callable for tokenize
    for tok in tokenize.generate_tokens(reader):    # stream of tokens
        if tok.type in (tokenize.INDENT, tokenize.DEDENT):  # only block markers
            names.append(tokenize.tok_name[tok.type])       # "INDENT" or "DEDENT"
    return names


def main() -> None:
    good: str = textwrap.dedent("""\
        if True:
            x = 1
            if x:
                y = 2
        z = 3
    """)                                        # valid nested blocks
    print(check_syntax(good))                   # Output: ok
    print(show_tokens(good))                    # Output: ['INDENT', 'INDENT', 'DEDENT', 'DEDENT']

    missing_block: str = "if True:\nx = 1\n"    # no indent after the colon
    print(check_syntax(missing_block))
    # Output: IndentationError: expected an indented block after 'if' statement on line 1

    unexpected: str = "x = 1\n    y = 2\n"      # indent without a header
    print(check_syntax(unexpected))             # Output: IndentationError: unexpected indent

    bad_dedent: str = "if True:\n        a = 1\n    b = 2\n"   # 8 -> 4 never existed
    print(check_syntax(bad_dedent))
    # Output: IndentationError: unindent does not match any outer indentation level

    mixed: str = "if True:\n    a = 1\n\tb = 2\n"   # 4 spaces then a tab
    print(check_syntax(mixed))                  # Output: IndentationError: inconsistent use of tabs and spaces in indentation

    # Meaning changes with indentation: same lines, different behaviour
    def total_a(items: list[int]) -> int:
        total: int = 0                          # start
        for n in items:                         # loop
            total += n                          # inside loop
        return total                            # after loop: runs once

    def total_b(items: list[int]) -> int:
        total: int = 0                          # start
        for n in items:                         # loop
            total += n                          # inside loop
            return total                        # inside loop: returns on first item!

    print(total_a([1, 2, 3]))                   # Output: 6
    print(total_b([1, 2, 3]))                   # Output: 1

    tree = ast.parse(good)                      # the tree mirrors the indentation
    print(type(tree.body[0]).__name__)          # Output: If


if __name__ == "__main__":
    main()                                      # run only when executed directly
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: indentation = structure
def check(n):
    if n > 0:
        for i in range(n):
            print(i)
    else:
        print("non-positive")
# Mistake: wrong indent changes the logic or raises IndentationError
```
```javascript
// JavaScript: braces = structure, indentation = just style
function check(n) {
if (n > 0) {
for (let i = 0; i < n; i++) {
console.log(i);
}
} else {
console.log("non-positive");
}
}
// Works even with zero indentation (ugly but valid). Prettier fixes style.
```

Key differences: in JS, indentation is optional and done by Prettier; in Python it is mandatory and changes meaning. JS `if (x) a(); b();` is a classic trap where `b()` looks like part of the `if`; Python has no such trap. Python allows a one-line block after the colon (`if x: print(1)`), but PEP 8 discourages it.

---

## 🟠 FastAPI Connection
Every FastAPI file is full of nested blocks: the function body, `try/except`, `with` for DB sessions, and `if` for validation. Indentation decides whether a `return` or `raise HTTPException` happens inside the `if` or for every request. Use 4 spaces and a formatter (`black`/`ruff`) so the whole team's endpoints look the same.

```python
# FastAPI example (needs: pip install fastapi)
from fastapi import FastAPI, HTTPException      # framework + error type

app: FastAPI = FastAPI()                        # create app
USERS: dict[int, str] = {1: "Priya"}            # fake database


@app.get("/users/{user_id}")                    # GET /users/1
async def get_user(user_id: int) -> dict[str, str]:
    if user_id not in USERS:                    # block 1 starts
        raise HTTPException(status_code=404, detail="User not found")
    return {"name": USERS[user_id]}             # dedent: runs only if user exists
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mixing tabs and spaces
```python
# Wrong: one line uses a tab, the next uses 4 spaces
# def f():
#     a = 1        <- 4 spaces
# 	b = 2          <- 1 tab  => TabError / IndentationError

# Right: configure the editor to insert 4 spaces when you press Tab
def f() -> int:
    a: int = 1
    b: int = 2
    return a + b

print(f())         # Output: 3
```

❌ Mistake 2: Empty block
```python
# Wrong: IndentationError: expected an indented block
# def todo():
# print("x")

# Right: use pass (or ... or a docstring) as placeholder
def todo() -> None:
    pass

print(todo())      # Output: None
```

❌ Mistake 3: Wrong dedent changes the logic silently
```python
items: list[int] = [1, 2, 3]

# Wrong: print is inside loop? or outside? Be careful
for n in items:
    pass
print("done")      # runs ONCE, after loop (dedented)

# Right: indent only what must repeat
for n in items:
    print(n)       # runs for each item
```

❌ Mistake 4: Unexpected indent
```python
# Wrong: x = 1 then an indented line without a header
# x = 1
#     y = 2      <- IndentationError: unexpected indent

# Right:
x: int = 1
y: int = 2
print(x + y)       # Output: 3
```

---

## 🧠 Tricky Interview Question

```python
for i in range(3):
    if i == 1:
        continue
    print(i)
else:
    print("loop finished")

x = 5
if x > 3:
    print("A")
    if x > 10:
        print("B")
else:
    print("C")
```

**Answer:**
```
0
2
loop finished
A
```
The `for ... else` `else` is aligned with `for`, so it belongs to the loop (runs when the loop ends without `break`): `continue` is not `break`, so it runs. In the second part, `else:` is aligned with the *outer* `if x > 3`, so it belongs to it (not to `if x > 10`). `x` is 5: prints `A`; inner `if` is false; outer `else` is skipped. If you indented `else` four more spaces, it would attach to `if x > 10` and print `C`. Alignment alone decides which `if` an `else` belongs to.

---

## ⚫ Interview Questions + Answers

Q1: How many spaces should you use, and why not tabs?
A1: PEP 8 says 4 spaces per level. Python 3 does not allow mixing tabs and spaces inconsistently (raises `TabError`) because the visual width of a tab differs between editors. Spaces look identical everywhere. Configure your editor to insert spaces when pressing Tab.

Q2: What are IndentationError and TabError?
A2: `IndentationError` (subclass of `SyntaxError`) means the indentation is wrong: unexpected indent, expected an indented block, or unindent does not match any outer level. `TabError` (subclass of `IndentationError`) means tabs and spaces are mixed in an inconsistent way. Both are detected at compile time, before any code runs.

Q3: Can a block be written on one line?
A3: Yes: `if x: print(1)` or `for i in range(3): print(i)`. But compound statements cannot be chained like that (`if x: for ...` is invalid), and PEP 8 discourages it. Use proper blocks for anything beyond trivial code.

Q4: How does Python handle indentation inside parentheses, brackets, and braces?
A4: Inside `()`, `[]`, `{}` newlines do not end the statement and indentation does not matter to the interpreter (implicit line joining). So you can align arguments in any style. A backslash `\` also continues a line, but brackets are preferred.

Q5: Why is `pass` needed?
A5: Because a block cannot be empty. `pass` is a no-op statement that satisfies the grammar. Use it for stubs, abstract-ish methods or empty `except` (but empty `except` hides errors, avoid). `...` (Ellipsis) and a docstring also work as placeholders.

---

## 🔷 When to Use + When Not to Use

✅ Follow strictly:
- Always 4 spaces per level
- Run `black` or `ruff format` automatically on save
- Add `.editorconfig` so every editor agrees
- Keep nesting shallow (use early `return` / `continue`)

❌ Avoid:
- Tabs, or mixing tabs and spaces
- More than 3 or 4 nested levels (extract a function instead)
- One-line compound statements for complex logic
- Copy-pasting code from the web/Word without checking indentation

---

## 📊 Visual Diagram
```
def process(order):            level 0   ◄─ stack: [0]
    if order.paid:             level 1   ◄─ INDENT  stack: [0,4]
        assign(order)          level 2   ◄─ INDENT  stack: [0,4,8]
        notify(order)          level 2
    else:                      level 1   ◄─ DEDENT  stack: [0,4]
        reject(order)          level 2   ◄─ INDENT  stack: [0,4,8]
    log(order)                 level 1   ◄─ DEDENT  stack: [0,4]
done()                         level 0   ◄─ DEDENT  stack: [0]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Indentation | Leading whitespace that defines blocks | Line के आगे की spacing |
| Block / Suite | Group of statements under a header | Statements का समूह |
| INDENT / DEDENT | Tokens for block start / end | Block शुरू / खत्म के tokens |
| IndentationError | Wrong indentation | गलत indentation की error |
| TabError | Inconsistent tabs and spaces | Tab-space mix की error |
| `pass` | Do-nothing placeholder statement | खाली placeholder |
| PEP 8 | Style guide (4 spaces) | Python का style guide |

---

## ⚡ 3-Line Summary
English: Python uses indentation instead of braces; a colon opens a block and the next lines must be indented more. Use 4 spaces, never mix tabs and spaces, and use `pass` for empty blocks. Alignment of `else` decides which `if` or loop it belongs to.
Hindi: Python braces की जगह indentation use करता है; colon block खोलता है और अगली lines ज्यादा indent होती हैं। 4 spaces लो, tab-space मत मिलाओ, खाली block में `pass` लिखो। `else` की alignment तय करती है कि वह किस `if` या loop का है।

---

## ➡️ Next Topic
**026. Operators — Complete Guide** — the full map of Python operators before we study each family in detail.
