---

# 163. Abstract Syntax Tree (AST)
# हिंदी में: Abstract Syntax Tree (कोड का tree रूप)

---

## 🔵 Simple Definition (English)
An AST is a tree that represents the structure of your source code. Python parses text like `x = 1 + 2` into nodes (`Assign`, `BinOp`, `Constant`). The `ast` module lets you read, check, change and even compile that tree, without running the code.

## 🔵 सरल परिभाषा (Hindi)
AST आपके source code की संरचना का tree है। Python `x = 1 + 2` जैसे text को nodes (`Assign`, `BinOp`, `Constant`) में बदलता है। `ast` module से आप उस tree को पढ़ सकते हैं, जाँच सकते हैं, बदल सकते हैं और compile भी कर सकते हैं, code चलाए बिना।

---

## 🔴 Problem it Solves
Searching code with regex is fragile: it matches inside strings and comments and cannot understand nesting. `eval()` on user input is dangerous. With an AST you analyse code by its real meaning: find every `eval(...)` call, detect mutable default arguments, rewrite code safely or evaluate only literal data. Linters, formatters, pytest assertion rewriting and type checkers all use ASTs.

## 🔴 यह क्यों बना? (Hindi)
Regex से code खोजना कमज़ोर तरीका है: वह strings और comments के अंदर भी match कर देता है और nesting नहीं समझता। User input पर `eval()` खतरनाक है। AST से आप code को उसके असली अर्थ से परखते हैं: हर `eval(...)` call ढूँढना, mutable default arguments पकड़ना, code को सुरक्षित तरीके से बदलना या सिर्फ literal data evaluate करना। Linters, formatters, pytest का assertion rewriting और type checkers सब AST इस्तेमाल करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Tokenizer splits source text into tokens (names, numbers, operators)
Step 2 → Parser builds a tree of nodes from the grammar:  Module -> Assign -> BinOp -> Constant
Step 3 → ast.parse(text) returns that tree (nothing runs yet)
Step 4 → NodeVisitor walks the tree to read it, NodeTransformer rewrites it
Step 5 → compile(tree, ...) turns the tree into a code object (bytecode)
Step 6 → exec() runs it; ast.unparse(tree) gives source text back (3.9+)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Tokenizer source text को tokens में तोड़ता है (names, numbers, operators)
Step 2 → Parser grammar से nodes का tree बनाता है:  Module -> Assign -> BinOp -> Constant
Step 3 → ast.parse(text) वह tree लौटाता है (अभी कुछ चला नहीं)
Step 4 → NodeVisitor tree पढ़ने के लिए चलता है, NodeTransformer उसे बदलता है
Step 5 → compile(tree, ...) tree को code object (bytecode) में बदलता है
Step 6 → exec() उसे चलाता है; ast.unparse(tree) वापस source text देता है (3.9+)
```

---

## 🟡 Real World Example
A code-review bot for a fintech team parses each pull request file with `ast`, then flags `eval()` calls, mutable default arguments and `print` statements left in production code. A low-code calculator in a dashboard accepts formulas like `price * qty + tax`; instead of `eval`, it parses the formula and walks only allowed node types. `ast.literal_eval` safely reads config values like `"[1, 2, {'a': 3}]"`.

## 🟡 Real Example Hindi mein
Fintech team का code-review bot हर pull request की file को `ast` से parse करता है और `eval()` calls, mutable default arguments और production में छूटे `print` statements पर flag लगाता है। Dashboard का low-code calculator `price * qty + tax` जैसे formulas लेता है; `eval` की जगह वह formula parse करके सिर्फ allowed node types पर चलता है। `ast.literal_eval` `"[1, 2, {'a': 3}]"` जैसे config values सुरक्षित रूप से पढ़ता है।

---

## 💻 Code Example — Basic
```python
# Basic AST examples
import ast                                        # the ast module

source: str = "x = 1 + 2 * 3"                     # source code as a string
tree: ast.Module = ast.parse(source)              # text -> tree (nothing is executed)
print(ast.dump(tree.body[0].value))               # dump just the expression node
print(type(tree.body[0]).__name__)                # statement type: Assign
code = compile(tree, "<demo>", "exec")            # tree -> code object
ns: dict[str, int] = {}                           # namespace for exec
exec(code, ns)                                    # run the compiled tree
print(ns["x"])                                    # 7
print(ast.unparse(tree))                          # tree -> source text again
print(ast.literal_eval("[1, 2, {'a': (3, 4)}]"))  # SAFE evaluation of literals only

# Output:
# BinOp(left=Constant(value=1), op=Add(), right=BinOp(left=Constant(value=2), op=Mult(), right=Constant(value=3)))
# Assign
# 7
# x = 1 + 2 * 3
# [1, 2, {'a': (3, 4)}]
```

## 💻 Code Example — Advanced
```python
# Production style: lint checker, transformer, safe calculator
import ast                                        # ast tools
import operator                                   # operator functions for the calculator
from typing import Any                            # typing helper

CODE: str = """
def pay(amount, retries=[]):
    print("paying", amount)
    eval("1+1")
    return amount
"""                                               # sample code to analyse


class Linter(ast.NodeVisitor):
    """Report dangerous or smelly constructs."""

    def __init__(self) -> None:
        self.issues: list[str] = []               # collected problems

    def visit_Call(self, node: ast.Call) -> None:   # called for every function call
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:   # dangerous name
            self.issues.append(f"line {node.lineno}: {node.func.id}() is unsafe")
        self.generic_visit(node)                  # keep walking into children

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:   # every def
        for d in node.args.defaults:              # default values
            if isinstance(d, (ast.List, ast.Dict, ast.Set)):   # mutable default
                self.issues.append(f"line {node.lineno}: mutable default in {node.name}()")
        self.generic_visit(node)                  # walk the body


linter: Linter = Linter()                         # create visitor
linter.visit(ast.parse(CODE))                     # run it
print(*linter.issues, sep="\n")                   # print each issue


class DropPrint(ast.NodeTransformer):
    """Remove every print(...) statement."""

    def visit_Expr(self, node: ast.Expr) -> ast.AST | None:   # expression statements
        v = node.value                            # the expression inside
        if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id == "print":
            return None                           # returning None deletes the node
        return node                               # keep everything else


new_tree: ast.Module = DropPrint().visit(ast.parse(CODE))   # transform
print(ast.unparse(ast.fix_missing_locations(new_tree)))     # show the result

OPS: dict[type, Any] = {ast.Add: operator.add, ast.Sub: operator.sub,
                        ast.Mult: operator.mul, ast.Div: operator.truediv}   # allowed operators


def safe_calc(expr: str) -> float:
    """Evaluate arithmetic only. No names, no calls -> no code execution."""

    def ev(n: ast.AST) -> float:
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):   # a number
            return n.value                        # base case
        if isinstance(n, ast.BinOp) and type(n.op) in OPS:   # allowed operator
            return OPS[type(n.op)](ev(n.left), ev(n.right))  # recurse both sides
        raise ValueError(f"not allowed: {type(n).__name__}")  # everything else rejected

    return ev(ast.parse(expr, mode="eval").body)  # parse as a single expression


print(safe_calc("2 + 3 * 4"))                     # 14
try:                                              # hostile input
    safe_calc("__import__('os').system('ls')")    # blocked: it is a Call node
except ValueError as e:                           # handled
    print("Error:", e)

# Output:
# line 2: mutable default in pay()
# line 4: eval() is unsafe
# def pay(amount, retries=[]):
#     eval('1+1')
#     return amount
# 14
# Error: not allowed: Call
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Built-in parser | `ast` (stdlib) | none in the language; use Acorn / Babel / esprima |
| Parse code | `ast.parse(src)` | `acorn.parse(src)` |
| Walk tree | `NodeVisitor` | `estree-walker`, Babel traverse |
| Rewrite tree | `NodeTransformer` | Babel plugins |
| Tree to code | `ast.unparse` | `escodegen`, `@babel/generator` |
| Safe data parse | `ast.literal_eval` | `JSON.parse` |

```python
# Python way
import ast                                      # stdlib, nothing to install
tree = ast.parse("a + b")                       # parse
print(type(tree.body[0].value).__name__)        # BinOp
```
```javascript
// JavaScript way (needs a package: npm i acorn)
const acorn = require("acorn");                 // third-party parser
const tree = acorn.parse("a + b", { ecmaVersion: 2022 });
console.log(tree.body[0].expression.type);      // BinaryExpression
```

Key difference: Python ships its parser in the standard library, so linters and code tools need no extra dependency. JavaScript tools like Babel and ESLint rely on external parsers.

---

## 🟠 FastAPI Connection
FastAPI itself does not expose the AST, but tools around it do: Ruff, mypy and pytest read ASTs. In your own API you may need to accept a formula from users. Never pass it to `eval`. Parse it with `ast` and allow only safe nodes.

```python
# FastAPI: expose a safe expression calculator (AST based, no eval)
import ast                                        # parse the expression
import operator                                   # arithmetic functions
from fastapi import FastAPI, HTTPException        # app + error type
from fastapi.testclient import TestClient         # in-process client

app: FastAPI = FastAPI()                          # create app
OPS = {ast.Add: operator.add, ast.Mult: operator.mul, ast.Sub: operator.sub}   # whitelist


def ev(n: ast.AST) -> float:
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):   # number
        return n.value
    if isinstance(n, ast.BinOp) and type(n.op) in OPS:   # allowed op
        return OPS[type(n.op)](ev(n.left), ev(n.right))
    raise ValueError("unsupported expression")   # reject everything else


@app.get("/calc")                                 # GET /calc?expr=2*3
def calc(expr: str) -> dict[str, float]:
    try:
        return {"result": ev(ast.parse(expr, mode="eval").body)}   # compute safely
    except (ValueError, SyntaxError):             # bad or hostile input
        raise HTTPException(status_code=400, detail="bad expression")   # 400 reply


client: TestClient = TestClient(app)              # test client
print(client.get("/calc", params={"expr": "2+3*4"}).json())          # {'result': 14}
print(client.get("/calc", params={"expr": "__import__('os')"}).status_code)   # 400

# Output:
# {'result': 14.0}
# 400
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `eval()` on user input
✅ Correct: `ast.literal_eval` for data, or a whitelist walker for formulas

```python
import ast
# Wrong - runs arbitrary code
# eval("__import__('os').system('rm -rf /')")
# Right
print(ast.literal_eval("[1, 2, 3]"))            # [1, 2, 3]
```

❌ Mistake 2: Thinking `literal_eval` is a sandbox for all expressions
✅ Correct: it handles literals only (numbers, strings, lists, dicts, tuples, sets, bool, None), so `"1+2"` fails

```python
import ast
try:
    ast.literal_eval("1+2")                     # ValueError: malformed node or string
except ValueError as e:
    print("ValueError")
```

❌ Mistake 3: Forgetting `generic_visit` in a visitor
✅ Correct: call `self.generic_visit(node)` so children are visited

❌ Mistake 4: Forgetting `ast.fix_missing_locations` after building or editing nodes
✅ Correct: call it before `compile()` (otherwise `lineno` errors)

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import ast
print(ast.dump(ast.parse("a = -1").body[0].value))
print(ast.literal_eval("-1"))
try:
    print(ast.literal_eval("1+2"))
except ValueError:
    print("ValueError")
print(ast.literal_eval("1+2j"))
```
Answer (verified on 3.13):
```
UnaryOp(op=USub(), operand=Constant(value=1))
-1
ValueError
(1+2j)
```
`-1` is not a single constant in the tree: it is a unary minus applied to `1`. `literal_eval` allows unary minus and the special form `number + imaginary` to write complex numbers, but not general arithmetic, so `1+2` is rejected and `1+2j` is accepted.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `ast.parse` and `compile`?
A1: `ast.parse` only builds the tree. `compile` turns source text (or a tree) into a code object that `exec` can run. You can pass an AST to `compile`.

Q2: Why is `ast.literal_eval` safer than `eval`?
A2: It accepts only literal structures. It cannot call functions or read names, so it cannot run code. It can still be slow or use much memory on huge nested input, so limit input size.

Q3: NodeVisitor vs NodeTransformer?
A3: `NodeVisitor` only reads. `NodeTransformer` returns replacement nodes from `visit_X` methods (return `None` to delete). You must call `fix_missing_locations` after transforming.

Q4: How does pytest show nice assertion messages?
A4: It rewrites the AST of test modules at import time, so each `assert a == b` is expanded to code that records sub-expression values. Bytecode is cached in `.pyc`.

Q5: What changes between Python versions?
A5: Node classes change. For example `ast.Num`, `ast.Str` were deprecated in favour of `ast.Constant` (removed in 3.14). `ast.unparse` appeared in 3.9, and the tree of a version may differ. Do not depend on exact dump text across versions.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing linters, code-mod tools, auto-formatters
- Evaluating user formulas safely (whitelist walker)
- Finding patterns in code (dangerous calls, missing type hints)

❌ Avoid when:
- A simple string search is enough
- You only need to read data (use `json` or `literal_eval`)
- You need comments or exact formatting preserved (use `libcst`)

---

## 📊 Visual Diagram
```
 source:  x = 1 + 2 * 3

 Module
  └─ Assign
      ├─ targets: [Name 'x']
      └─ value:   BinOp
                   ├─ left:  Constant 1
                   ├─ op:    Add
                   └─ right: BinOp
                              ├─ left:  Constant 2
                              ├─ op:    Mult
                              └─ right: Constant 3
 (multiplication is deeper, so it is computed first)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AST | Tree form of source code | code का tree रूप |
| Node | One element of the tree | tree का एक हिस्सा |
| Parse | Turn text into a tree | text को tree में बदलना |
| Visitor | Walks the tree to read | tree पर चलकर पढ़ने वाला |
| Transformer | Walks and rewrites the tree | tree बदलने वाला |
| `literal_eval` | Safe evaluation of literals | literals का सुरक्षित evaluation |

---

## ⚡ 3-Line Summary
English: `ast.parse` turns code into a tree without running it. Use `NodeVisitor` to inspect and `NodeTransformer` to rewrite. Use `literal_eval` or a whitelist walker instead of `eval`.
Hindi: `ast.parse` code को बिना चलाए tree बना देता है। देखने के लिए `NodeVisitor` और बदलने के लिए `NodeTransformer` use करें। `eval` की जगह `literal_eval` या whitelist walker इस्तेमाल करें।

---

## ➡️ Next Topic
**164. Bytecode Compilation** — what happens after the AST: code objects, bytecode, and `.pyc` cache files.
