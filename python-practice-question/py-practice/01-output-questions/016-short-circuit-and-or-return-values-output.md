---

# Q016. Short-circuit and/or return values output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```python
print(0 or "" or None)     # (a)
print(0 or "hi")           # (b)
print(1 and 2)             # (c)
print(0 and 2)             # (d)
print([] or {})            # (e)
print(None or 0)           # (f)

def g():
    print("g called")      # side effect
    return 1

print(0 and g())           # (g)
print(1 or g())            # (h)
print(0 or g())            # (i)
```

---

## 💡 Quick Concept (2 lines only)
`and` / `or` return one of their OPERANDS (not True/False): `or` gives the first truthy (else the last), `and` gives the first falsy (else the last).
हिंदी: `and`/`or` bool नहीं, असली operand लौटाते हैं और जैसे ही जवाब पता चले, रुक जाते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
print(0 or "" or None)     # (a) all falsy -> returns the LAST operand: None
print(0 or "hi")           # (b) first truthy operand: "hi"
print(1 and 2)             # (c) all truthy -> returns the LAST operand: 2
print(0 and 2)             # (d) first falsy operand: 0

print([] or {})            # (e) both falsy -> last operand: {}
print(None or 0)           # (f) both falsy -> last operand: 0

def g() -> int:            # Function with a visible side effect
    print("g called")      # Shows if g is executed
    return 1               # Truthy return value

print(0 and g())           # (g) 0 is falsy -> g() never runs -> 0
print(1 or g())            # (h) 1 is truthy -> g() never runs -> 1
print(0 or g())            # (i) must evaluate g(): prints "g called", then 1

# ============================================
# TEST CASES
# ============================================
# Expected output (real run, Python 3.13):
# None
# hi
# 2
# 0
# {}
# 0
# 0
# 1
# g called
# 1
```

---

## 🔍 Why This Works (3 lines max)
Python evaluates operands left to right and returns the operand that decided the result; the rest is skipped. That is why `x or default` works as a default-value idiom.
हिंदी: Result वही operand है जिस पर फैसला हुआ — आगे का code चलता ही नहीं।

---

## ⚡ Alternative Solution
```python
# Default-value idiom and guard idiom
name = None                          # Missing value
print(name or "anon")                # -> anon (None is falsy)

user = {"profile": {"city": "Pune"}} # Sample nested data
print(user and user.get("profile") and user["profile"].get("city"))  # -> Pune

# Ternary is clearer when 0/"" are VALID values
count = 0                            # Valid value that is falsy
print(count or 10)                   # -> 10 (surprise!)
print(count if count is not None else 10)  # -> 0 (correct)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: assuming `or` returns True/False
# result = 0 or "hi"  -> thinking result is True
# ✅ Correct: result is "hi" (the operand itself)
result = 0 or "hi"        # Returns the operand
print(result)             # hi
print(bool(result))       # True  <- convert explicitly if you need a bool
```

---

## 🎯 Interview Tip (1 line)
Say: "`and`/`or` return an operand and short-circuit; `x or default` breaks when 0, '' or [] are valid values — use `is None` instead."

---

## 🔗 Related Questions
→ Q015 (chained comparisons) | Q017 (truthy/falsy) | Q049 (any/all empty)
