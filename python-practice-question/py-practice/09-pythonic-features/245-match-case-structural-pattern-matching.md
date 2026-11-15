---

# Q245. match/case (Structural Pattern Matching)
# Category: Pythonic + Modern Python Features
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Use `match/case` (Python 3.10+) to handle: literals, `|` alternatives, sequence patterns, dict (mapping) patterns, class patterns, guards (`if`), and a wildcard default.

---

## 💡 Quick Concept (2 lines only)
`match` compares a value against patterns by STRUCTURE and binds names at the same time. It is not a C-style switch — it can destructure lists, dicts and objects.
हिंदी: `match/case` structure देखकर match करता है और variables भी bind कर देता है — switch से कहीं ज़्यादा powerful।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from dataclasses import dataclass                    # for class patterns

@dataclass                                           # auto __init__ + __match_args__
class Point:                                         # simple 2D point
    x: int                                           # x coordinate
    y: int                                           # y coordinate

def describe(obj: object) -> str:                    # classify any object
    match obj:                                       # Step 1: subject to match
        case 0 | 1:                                  # literal alternatives with |
            return "zero or one"                     # matched 0 or 1
        case int(n) if n < 0:                        # class pattern + guard
            return f"negative {n}"                   # n is bound by the pattern
        case str() as s:                             # any str, bind to s
            return f"string {s!r}"                   # report it
        case [x]:                                    # sequence of exactly 1 item
            return f"one item {x}"                   # bind that item
        case [first, *rest]:                         # sequence with >= 1 items
            return f"first={first} rest={rest}"      # star collects rest
        case {"type": "user", "name": name}:         # mapping pattern (extra keys ok)
            return f"user {name}"                    # bind name from dict
        case Point(x=0, y=0):                        # class pattern with keywords
            return "origin"                          # point at 0,0
        case Point(x, y):                            # positional via __match_args__
            return f"point {x},{y}"                  # bind x and y
        case _:                                      # wildcard = default
            return "unknown"                         # nothing matched

# ============================================
# TEST CASES
# ============================================
print(describe(1))                                   # Expected: zero or one
print(describe(-5))                                  # Expected: negative -5
print(describe("hi"))                                # Expected: string 'hi'
print(describe([9]))                                 # Expected: one item 9
print(describe([1, 2, 3]))                           # Expected: first=1 rest=[2, 3]
print(describe({"type": "user", "name": "Ana"}))     # Expected: user Ana
print(describe(Point(0, 0)))                         # Expected: origin
print(describe(Point(3, 4)))                         # Expected: point 3,4
print(describe(3.5))                                 # Expected: unknown
```

---

## 🔍 Why This Works (3 lines max)
Cases are tried top-to-bottom; the first matching pattern (and passing guard) wins. A bare name captures; dotted names/literals compare. `str`/`bytes` are NOT treated as sequences, so `"hi"` never hits `[first, *rest]`.
हिंदी: ऊपर से नीचे पहला match जीतता है — plain name capture करता है, तुलना नहीं।

---

## ⚡ Alternative Solution
```python
# Typical real use: parse a command / HTTP-like event
def handle(cmd: str) -> str:                         # cmd is a text command
    match cmd.split():                               # split into a list of words
        case ["go", ("north" | "south") as d]:       # nested alternatives + capture
            return f"going {d}"                      # report direction
        case ["pick", item]:                         # exactly 2 words
            return f"picked {item}"                  # report item
        case ["quit" | "exit"]:                      # either word alone
            return "bye"                             # exit message
        case _:                                      # anything else
            return "?"                               # unknown command

print(handle("go north"))                            # Expected: going north
print(handle("pick key"))                            # Expected: picked key
print(handle("exit"))                                # Expected: bye
print(handle("dance"))                               # Expected: ?
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: bare name as a constant -> it CAPTURES (always matches) instead of comparing
# RED = "red"                                        # constant
# def bad(c):                                        # buggy matcher
#     match c:                                       # subject
#         case RED:                                  # irrefutable capture, not a comparison
#             return "red"                           # would match everything
#         case "blue":                               # never reachable
#             return "blue"                          # dead code
# Verified by compile(): SyntaxError: name capture 'RED' makes remaining patterns unreachable (not run as code)

# ✅ Correct: use a dotted name (Color.RED) or a literal "red" to compare by value
```

---

## 🎯 Interview Tip (1 line)
Say: "match/case is structural: it destructures sequences, mappings and classes, supports guards, and `_` is the default — bare names capture, only dotted names or literals compare."

---

## 🔗 Related Questions
→ Q242 (unpacking) | Q246 (dataclasses) | Q247 (typing Literal) | Q248 (enum use cases)
