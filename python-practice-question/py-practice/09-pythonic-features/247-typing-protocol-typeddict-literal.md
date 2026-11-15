---

# Q247. typing: Protocol, TypedDict, Literal
# Category: Pythonic + Modern Python Features
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Explain and demo `Protocol` (structural typing / duck typing), `TypedDict` (typed dict shapes) and `Literal` (restrict to exact values). Do they enforce anything at runtime?

---

## 💡 Quick Concept (2 lines only)
These are STATIC typing tools (checked by mypy/pyright). `Protocol` = "anything with these methods", `TypedDict` = dict with known keys, `Literal["a","b"]` = only these values.
हिंदी: ये type-checker के लिए हैं — runtime पर Python खुद enforce नहीं करता (सिवाय `@runtime_checkable` के)।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Literal, NotRequired, Protocol, TypedDict, get_args, runtime_checkable  # imports

@runtime_checkable                                    # allows isinstance() on the Protocol
class Speaker(Protocol):                              # Step 1: structural interface
    def speak(self) -> str: ...                       # any class with speak() -> str fits

class Dog:                                            # NOT inheriting from Speaker
    def speak(self) -> str:                           # has the right method
        return "woof"                                 # dog sound

class Rock:                                           # has no speak()
    pass                                              # nothing here

def talk(s: Speaker) -> str:                          # accepts anything Speaker-shaped
    return s.speak()                                  # call the protocol method

class UserDict(TypedDict):                            # Step 2: dict shape
    id: int                                           # required key
    name: str                                         # required key
    email: NotRequired[str]                           # optional key (3.11+)

Mode = Literal["r", "w", "a"]                         # Step 3: only these 3 strings

def open_file(path: str, mode: Mode) -> str:         # type checker rejects other modes
    return f"{path}:{mode}"                           # just echo for the demo

# ============================================
# TEST CASES
# ============================================
print(talk(Dog()))                                    # Expected: woof
print(isinstance(Dog(), Speaker))                     # Expected: True  (has speak)
print(isinstance(Rock(), Speaker))                    # Expected: False (no speak)

u: UserDict = {"id": 1, "name": "Ana"}                # valid shape (email optional)
print(u, type(u))                                     # Expected: {'id': 1, 'name': 'Ana'} <class 'dict'>
print(UserDict.__required_keys__)                     # Expected: frozenset({'id', 'name'}) (set order may vary)

print(open_file("a.txt", "r"))                        # Expected: a.txt:r
print(get_args(Mode))                                 # Expected: ('r', 'w', 'a')
print(open_file("a.txt", "x"))                        # Expected: a.txt:x  <- runs fine! mypy would flag it
```

---

## 🔍 Why This Works (3 lines max)
Python ignores annotations at runtime, so the wrong `"x"` mode still runs; only the static checker complains. `Protocol` matches by method names (no inheritance), and `TypedDict` instances are plain `dict`s at runtime.
हिंदी: Annotations runtime पर ignore होते हैं — गलती mypy/pyright पकड़ता है, Python नहीं।

---

## ⚡ Alternative Solution
```python
# Runtime validation when you need it: Pydantic enforces the same shapes
from typing import Literal                            # import Literal
from pydantic import BaseModel, ValidationError       # runtime validation library

class Req(BaseModel):                                 # model with a Literal field
    mode: Literal["r", "w", "a"]                      # only these values allowed

print(Req(mode="r"))                                  # Expected: mode='r'
try:                                                  # try an invalid value
    Req(mode="x")                                     # not allowed
except ValidationError as e:                          # pydantic raises
    print(e.error_count(), "error")                   # Expected: 1 error
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: believing TypedDict/Literal are enforced at runtime
# data: UserDict = {"id": "oops"}      # no error at runtime, just a dict

# ❌ Wrong: isinstance() on a Protocol without @runtime_checkable -> TypeError
# ✅ Correct: add @runtime_checkable (checks only method NAMES, not signatures),
#             and run mypy/pyright (or use Pydantic) for real checking
```

---

## 🎯 Interview Tip (1 line)
Say: "Protocol is static duck typing (structural), ABC is nominal (inheritance); TypedDict/Literal only help the type checker — for runtime validation I use Pydantic."

---

## 🔗 Related Questions
→ Q246 (dataclasses) | Q248 (enum use cases) | Q245 (match/case) | Q233 (response models)
