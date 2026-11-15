---

# Q244. Walrus Operator (:=)
# Category: Pythonic + Modern Python Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is the walrus operator `:=`? Show it in `if`, `while` and comprehensions, and explain when NOT to use it.

---

## 💡 Quick Concept (2 lines only)
`:=` (Python 3.8+) assigns a value AND returns it inside an expression. It avoids computing something twice or writing a separate assignment line.
हिंदी: `:=` एक ही expression में value assign भी करता है और वापस भी देता है — दोबारा compute नहीं करना पड़ता।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import re                                           # for regex demo

# 1. In an if: use the match without calling twice
text = "order-1234 shipped"                         # sample text
if (m := re.search(r"\d+", text)) is not None:      # assign AND test in one go
    print(m.group())                                # Expected: 1234

# 2. In a while: read chunks until empty
data = iter(["a", "b", "c", ""])                    # fake stream; "" means end
while (chunk := next(data)) != "":                  # assign then compare
    print(chunk, end=" ")                           # Expected: a b c
print()                                             # newline

# 3. In a comprehension: compute once, reuse in filter AND output
def slow_sq(n: int) -> int:                         # pretend expensive function
    return n * n                                    # square it
res = [y for n in range(6) if (y := slow_sq(n)) > 5]  # call slow_sq once per item
print(res)                                          # Expected: [9, 16, 25]

# ============================================
# TEST CASES
# ============================================
if (n := len("hello")) > 3:                         # n stays available after the if
    print(f"long ({n})")                           # Expected: long (5)
print(n)                                            # Expected: 5
print((x := 10) + x)                                # Expected: 20
```

---

## 🔍 Why This Works (3 lines max)
`(name := expr)` evaluates `expr`, binds it to `name` in the CURRENT scope, then yields the value. The walrus needs parentheses in most places and cannot be used as a bare statement.
हिंदी: `(name := expr)` expr चलाकर name में रखता है और वही value लौटाता है — अकेले statement में नहीं चलता।

---

## ⚡ Alternative Solution
```python
# Without walrus: works, but repeats the call or needs an extra line
import re                                           # regex module
text = "order-1234 shipped"                         # sample text
m = re.search(r"\d+", text)                         # extra assignment line
if m:                                               # test on next line
    print(m.group())                                # Expected: 1234

# Comprehension without walrus calls the function twice per item
def slow_sq(n: int) -> int:                         # same function
    return n * n                                    # square
print([slow_sq(n) for n in range(6) if slow_sq(n) > 5])  # Expected: [9, 16, 25] (2 calls each)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: bare walrus statement -> SyntaxError
# x := 5

# ❌ Wrong: confusing := with ==, or cramming too much in one line (hard to read)
# ✅ Correct: wrap in parentheses
(x := 5)                                            # legal, but pointless as a statement
print(x)                                            # Expected: 5
# Tip: inside a comprehension the walrus variable LEAKS to the enclosing scope
[(z := i) for i in range(3)]                        # z is bound in the outer scope
print(z)                                            # Expected: 2
```

---

## 🎯 Interview Tip (1 line)
Say: "Walrus is for 'compute once, test and reuse' (regex match, read loops, comprehension filters) — if it hurts readability, use a normal assignment."

---

## 🔗 Related Questions
→ Q241 (comprehensions) | Q024 (comprehension variable scope) | Q016 (short-circuit and/or) | Q245 (match/case)
