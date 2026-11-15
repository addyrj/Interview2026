---

# Q248. enum — 5 Use Cases
# Category: Pythonic + Modern Python Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 5 uses of `enum`: basic `Enum`, `auto()`, `IntEnum`, `StrEnum` (3.11+) for JSON/API values, and `Flag` for combinable permissions.

---

## 💡 Quick Concept (2 lines only)
An Enum is a fixed set of named constants, compared by identity, iterable and safe against typos. `StrEnum` members ARE strings; `IntEnum` members ARE ints.
हिंदी: Enum = नाम वाले fixed constants — magic strings/numbers की जगह typo-safe options।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from enum import Enum, Flag, IntEnum, StrEnum, auto   # Step 1: imports

class Color(Enum):                                    # Use case 1: basic Enum
    RED = 1                                           # member with value 1
    GREEN = 2                                         # member with value 2

print(Color.RED, Color.RED.name, Color.RED.value)     # Expected: Color.RED RED 1
print(Color(2), Color["GREEN"])                       # Expected: Color.GREEN Color.GREEN
print(list(Color))                                    # Expected: [<Color.RED: 1>, <Color.GREEN: 2>]

class Status(Enum):                                   # Use case 2: auto() values
    NEW = auto()                                      # becomes 1
    DONE = auto()                                     # becomes 2
print(Status.DONE.value)                              # Expected: 2

class Prio(IntEnum):                                  # Use case 3: behaves like int
    LOW = 1                                           # low priority
    HIGH = 3                                          # high priority
print(Prio.HIGH > Prio.LOW, Prio.HIGH + 1)            # Expected: True 4

class Role(StrEnum):                                  # Use case 4: behaves like str
    ADMIN = "admin"                                   # string value
    USER = "user"                                     # string value
print(Role.ADMIN == "admin", f"role={Role.USER}")     # Expected: True role=user

class Perm(Flag):                                     # Use case 5: combinable bit flags
    R = auto()                                        # read  (1)
    W = auto()                                        # write (2)
    X = auto()                                        # exec  (4)
rw = Perm.R | Perm.W                                  # combine with |
print(rw, Perm.W in rw, Perm.X in rw)                 # Expected: Perm.R|W True False

# ============================================
# TEST CASES
# ============================================
print(Color.RED == 1)                                 # Expected: False (plain Enum != int)
print(Prio.LOW == 1)                                  # Expected: True  (IntEnum == int)
print(Color.RED is Color(1))                          # Expected: True  (singletons)
try:                                                  # invalid lookup
    Color(99)                                         # not a member
except ValueError as e:                               # raised
    print(e)                                          # Expected: 99 is not a valid Color
```

---

## 🔍 Why This Works (3 lines max)
Each member is a singleton instance created once at class definition, so `is` works and members are hashable. Plain `Enum` does NOT equal its raw value; `IntEnum`/`StrEnum` do because they inherit from `int`/`str`.
हिंदी: हर member एक singleton है — plain Enum raw value के बराबर नहीं, IntEnum/StrEnum बराबर हैं।

---

## ⚡ Alternative Solution
```python
# Functional API + iteration + unique alias protection
from enum import Enum, unique                         # imports

Animal = Enum("Animal", "CAT DOG")                    # create an Enum without a class body
print(list(Animal))                                   # Expected: [<Animal.CAT: 1>, <Animal.DOG: 2>]

@unique                                               # forbid duplicate values
class Level(Enum):                                    # enum with unique values
    A = 1                                             # first
    B = 2                                             # second
print([m.name for m in Level])                        # Expected: ['A', 'B']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: comparing a plain Enum to its raw value
from enum import Enum                                 # import
class Color(Enum):                                    # plain enum
    RED = 1                                           # member
print(Color.RED == 1)                                 # Expected: False  (surprise!)

# ✅ Correct: compare with the member, or use .value, or use IntEnum/StrEnum
print(Color.RED.value == 1)                           # Expected: True
```

---

## 🎯 Interview Tip (1 line)
Say: "I use `StrEnum` for API/DB values so they serialise as strings, `IntEnum` for ordered levels, and `Flag` for permission bitmasks."

---

## 🔗 Related Questions
→ Q245 (match/case) | Q247 (typing Literal) | Q246 (dataclasses) | Q012 (dict keys 1, 1.0, True)
