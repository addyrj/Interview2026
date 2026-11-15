---

# 182. Circular Imports — How to Fix
# हिंदी में: Circular Imports — कैसे ठीक करें

---

## 🔵 Simple Definition (English)
A circular import happens when module A imports module B while B (directly or through others) imports A. Python starts running A, pauses at the import of B, runs B, and B asks for something from A that A has not defined yet. The result is an `ImportError` or `AttributeError`.

## 🔵 सरल परिभाषा (Hindi)
Circular import तब होता है जब module A, module B को import करता है और B (सीधे या दूसरों के ज़रिए) A को import करता है। Python A चलाना शुरू करता है, B के import पर रुककर B चलाता है, और B, A से कुछ माँगता है जो A ने अभी बनाया ही नहीं। नतीजा `ImportError` या `AttributeError`।

---

## 🔴 Problem it Solves
This topic is about avoiding a bug, not a feature. Circular imports usually signal tangled design: two modules know too much about each other. Fixing them gives cleaner layers and faster start-up, and prevents confusing "partially initialized module" crashes.

## 🔴 यह क्यों बना? (Hindi)
यह topic feature नहीं बल्कि bug से बचने का है। Circular imports आमतौर पर उलझे design का संकेत हैं: दो modules एक-दूसरे के बारे में बहुत जानते हैं। इन्हें ठीक करने से layers साफ होती हैं, start-up तेज़ होता है और "partially initialized module" वाले confusing crash रुकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → python main.py → `import a` ; a is added to sys.modules (EMPTY, still running)
Step 2 → a.py line 1: `from b import B` → b starts running
Step 3 → b.py line 1: `from a import A` → a is in sys.modules but A not defined yet
Step 4 → ImportError: cannot import name 'A' from partially initialized module 'a'
Fixes → (1) move shared code to a third module   (2) import inside the function
        (3) `import a` instead of `from a import A`  (4) TYPE_CHECKING for type hints
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `import a` ; a, sys.modules में खाली रूप में जुड़ जाता है (अभी चल रहा है)
Step 2 → a.py की line 1: `from b import B` → b चलना शुरू
Step 3 → b.py की line 1: `from a import A` → a cache में है पर A अभी बना नहीं
Step 4 → ImportError: cannot import name 'A' from partially initialized module 'a'
हल → (1) साझा code तीसरे module में   (2) function के अंदर import
     (3) `from a import A` की जगह `import a`   (4) type hints के लिए TYPE_CHECKING
```

---

## 🟡 Real World Example
In a FastAPI shop: `models/user.py` imports `Order` for a relationship, and `models/order.py` imports `User`. Importing either crashes. Or `services/billing.py` imports `api/deps.py` which imports `services/billing.py`. Fix: SQLAlchemy string references (`relationship("Order")`), or a shared `schemas`/`core` module.

## 🟡 Real Example Hindi mein
FastAPI shop में: `models/user.py` relationship के लिए `Order` import करता है और `models/order.py` `User`। कोई भी import करें तो crash। या `services/billing.py`, `api/deps.py` को import करता है जो वापस `services/billing.py` को। हल: SQLAlchemy के string references (`relationship("Order")`) या साझा `schemas`/`core` module।

---

## 💻 Code Example — Basic
```python
# Reproduce a circular import and the simplest fix (import inside the function).
import sys  # sys.path / sys.modules
import tempfile  # sandbox
from pathlib import Path  # files

BROKEN: dict[str, str] = {  # a.py <-> b.py import each other at the top
    "a.py": "from b import B\nclass A:\n    def make(self): return B()\n",
    "b.py": "from a import A\nclass B:\n    def make(self): return A()\n",
}
FIXED: dict[str, str] = {  # b2 imports a2 lazily, inside the method
    "a2.py": "import b2\nclass A:\n    def make(self): return b2.B()\n",
    "b2.py": "class B:\n    def make(self):\n        from a2 import A  # lazy import\n        return A()\n",
}

with tempfile.TemporaryDirectory() as tmp:  # sandbox
    for name, text in {**BROKEN, **FIXED}.items():  # write all files
        Path(tmp, name).write_text(text)  # create module
    sys.path.insert(0, tmp)  # importable
    try:
        import a  # type: ignore[import-not-found]  # triggers the cycle
    except ImportError as exc:  # the classic failure
        print(str(exc).split(" (")[0])  # shorten the message
    # Output: cannot import name 'A' from partially initialized module 'a'

    import a2  # type: ignore[import-not-found]  # works: no cycle at import time
    print(type(a2.A().make().make()).__name__)  # A -> B -> A
    # Output: A
    sys.path.remove(tmp)  # cleanup
    for n in ("a", "b", "a2", "b2"):
        sys.modules.pop(n, None)  # forget temp modules
```

## 💻 Code Example — Advanced
```python
# Production fixes: shared base module + TYPE_CHECKING for hints + a cycle detector.
import ast  # parse imports without running code
import tempfile  # sandbox
from pathlib import Path  # files
from typing import Dict, List, Optional, Set  # type hints

FILES: Dict[str, str] = {  # a realistic "fixed" design
    "base.py": (  # shared module: depends on nothing
        "class Entity:\n    id: int = 0\n"
    ),
    "user.py": (  # uses TYPE_CHECKING so the Order import never runs
        "from __future__ import annotations\n"
        "from typing import TYPE_CHECKING\n"
        "from base import Entity\n"
        "if TYPE_CHECKING:\n    from order import Order   # only for type checkers\n"
        "class User(Entity):\n    orders: list[Order]\n"
    ),
    "order.py": "from base import Entity\nfrom user import User\nclass Order(Entity):\n    owner: User\n",
}


def import_graph(folder: Path) -> Dict[str, Set[str]]:
    """Return {module: runtime imports} (skips `if TYPE_CHECKING:` blocks)."""
    graph: Dict[str, Set[str]] = {}  # result
    names = {p.stem for p in folder.glob("*.py")}  # our own modules
    for path in folder.glob("*.py"):  # each file
        tree = ast.parse(path.read_text())  # syntax tree
        deps: Set[str] = set()  # imports of this file
        for node in tree.body:  # only top-level statements
            if isinstance(node, ast.ImportFrom) and node.module in names:
                deps.add(node.module)  # from x import ...
            elif isinstance(node, ast.Import):
                deps.update(a.name for a in node.names if a.name in names)  # import x
        graph[path.stem] = deps  # store
    return graph  # adjacency list


def find_cycle(graph: Dict[str, Set[str]]) -> Optional[List[str]]:
    """Depth-first search for a cycle; returns the path or None."""
    def visit(node: str, trail: List[str]) -> Optional[List[str]]:
        if node in trail:  # we came back to a node on the path
            return trail[trail.index(node):] + [node]  # the loop
        for nxt in sorted(graph.get(node, ())):  # follow each dependency
            found = visit(nxt, trail + [node])  # recurse
            if found:
                return found
        return None  # no cycle from here
    for start in sorted(graph):  # try every start
        found = visit(start, [])
        if found:
            return found
    return None


with tempfile.TemporaryDirectory() as tmp:  # sandbox
    for name, text in FILES.items():
        Path(tmp, name).write_text(text)  # write the fixed design
    print(find_cycle(import_graph(Path(tmp))))  # TYPE_CHECKING breaks the loop
    # Output: None
    Path(tmp, "user.py").write_text("from order import Order\nclass User: ...\n")  # re-break it
    print(find_cycle(import_graph(Path(tmp))))  # now a real cycle
    # Output: ['order', 'user', 'order']
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: cycle -> error at the moment the missing name is requested
# a.py: from b import B ; b.py: from a import A   -> ImportError
# Fix: import module, use attribute later:  import a  ... a.A()  (inside a function)
```

```javascript
// JavaScript ES modules: cycles are allowed, bindings are live, but TDZ can bite
// a.js: import { B } from "./b.js"; export class A {}
// b.js: import { A } from "./a.js"; export class B { make() { return new A(); } }
// Works if A is used only AFTER both modules finish loading;
// using A at top level of b.js -> ReferenceError (Temporal Dead Zone).
// CommonJS: require() returns a PARTIAL exports object (similar to Python).
```

Key difference: ES modules have live bindings that fill in later; Python's `from a import A` needs `A` to exist right now.

---

## 🟠 FastAPI Connection
Typical FastAPI cycles: routers importing `deps`, deps importing services, services importing routers' schemas, plus SQLAlchemy models referencing each other. Fixes: put Pydantic schemas and shared dependencies in lower-level modules, use string-based `relationship("Order")`, and `TYPE_CHECKING` for hints.

```python
# models.py style (needs: pip install sqlalchemy)
from __future__ import annotations  # annotations stay as strings
from typing import TYPE_CHECKING, List  # hints
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship  # ORM bits

if TYPE_CHECKING:  # skipped at runtime -> no cycle
    from order import Order  # only for type checkers / IDE


class Base(DeclarativeBase):  # shared declarative base
    pass


class User(Base):  # model
    __tablename__ = "users"  # table name
    # Mapped[...] needs an id column in a real model; omitted for brevity
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="owner")  # string ref
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Hiding the cycle with imports at the bottom of the file
```python
# Wrong - works by accident, breaks when order changes:
# class A: ...
# from b import B     # at the bottom

# Correct: remove the cycle (extract shared code), or import inside the function.
```

❌ Mistake 2: Using `from x import y` inside tightly coupled modules
```python
# Wrong: from a import A      (needs A right now)
# Correct: import a           (resolve a.A later, at call time)
```

❌ Mistake 3: Fixing with lazy imports everywhere
```python
# Wrong - 20 function-level imports hide a bad design
# Correct - lazy import is a last resort; first fix the dependency direction
```

---

## 🧠 Tricky Interview Question

**Q**: `a.py` is `import b` then `x = 1`. `b.py` is `import a` then `print(a.x)`. What do `python a.py` and `python b.py` do?

**Answer**:
```
python a.py  ->  1
python b.py  ->  AttributeError: module 'a' has no attribute 'x'   (exact wording varies by version)
```
`python a.py`: the file runs as `__main__`. Its `import b` runs b, whose `import a` loads a FRESH copy of the file under the name `a` (the entry script is stored as `__main__`, not `a`). That copy imports the half-loaded `b`, then defines `x = 1`, finishes, and b prints `1`. `python b.py` is the mirror image, but now `print(a.x)` runs while `a` is still stuck on its first line `import b`, so `x` does not exist yet. The result depends on the entry point and line order, which is why cycles are fragile.

---

## ⚫ Interview Questions + Answers

Q1: Why does a circular import fail for `from a import A` but sometimes not for `import a`?
A1: `import a` only needs the module object, which exists in `sys.modules` already. `from a import A` needs attribute `A` immediately, and it may not be defined yet.

Q2: Name four ways to fix a cycle.
A2: Extract shared code to a third module; import inside the function; use `import a` and access `a.A` later; use `TYPE_CHECKING` for annotation-only imports.

Q3: What does `TYPE_CHECKING` do?
A3: `typing.TYPE_CHECKING` is `False` at runtime and `True` for type checkers, so imports under it are never executed, yet mypy/IDEs still see the types. Use string or `from __future__ import annotations` hints.

Q4: Is a lazy (function-level) import slow?
A4: After the first call it is a `sys.modules` lookup, which is cheap but not free. Avoid it in hot loops.

Q5: How do you find cycles in a big project?
A5: Run `python -X importtime`, tools like `pycycle` or `import-linter`, or write an AST graph check as in the advanced example.

---

## 🔷 When to Use + When Not to Use

✅ Use a lazy import when:
- Breaking a cycle you cannot restructure right now
- Delaying a heavy import (pandas, torch) until needed

✅ Use `TYPE_CHECKING` when:
- The import is only needed for annotations

❌ Avoid when:
- A clean layer split would remove the cycle
- It sits inside a hot loop

---

## 📊 Visual Diagram

```
   BROKEN                              FIXED
   a.py ──imports──► b.py              a.py ──► base.py ◄── b.py
     ▲                 │                      (shared types
     └───────imports───┘                       depend on nothing)
     cycle → ImportError
                                       or:  b.py:  def f(): import a   (lazy)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Circular import | A needs B and B needs A | गोलाकार import |
| Partially initialized | Module still running | अधूरा चला हुआ module |
| Lazy import | Import inside function | ज़रूरत पर import |
| `TYPE_CHECKING` | True only for type checkers | केवल type checker के लिए |
| Dependency direction | Who imports whom | कौन किसे import करे |
| Extract module | Move shared code out | साझा code अलग करना |

---

## ⚡ 3-Line Summary
English: A circular import fails because one module needs a name another has not finished defining. Fix by extracting shared code, importing inside functions, using `import module` style, or `TYPE_CHECKING`. Best fix: a one-way dependency design.
Hindi: Circular import इसलिए fail होता है कि एक module को वह नाम चाहिए जो दूसरे ने अभी बनाया नहीं। हल: साझा code अलग करें, function में import, `import module` style या `TYPE_CHECKING`। सबसे अच्छा हल एक दिशा वाला design है।

---

## ➡️ Next Topic
**183. Standard Library Overview** — the "batteries included" modules you should know before reaching for pip.
