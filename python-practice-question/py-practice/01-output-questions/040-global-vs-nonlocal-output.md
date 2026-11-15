---

# Q040. global vs nonlocal output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What does this print, and why does `bad()` fail?

```python
x = 0
def g():
    global x
    x += 1

def outer():
    n = 0
    def inc():
        nonlocal n
        n += 1
    inc(); inc()
    return n

g(); g()
print(x, outer())

def bad():
    x += 1
bad()
```

---

## 💡 Quick Concept (2 lines only)
`global` rebinds a module-level name, `nonlocal` rebinds a name in the nearest enclosing function. Assigning to a name without either makes it local to that function.
हिंदी: `global` module का variable बदलता है, `nonlocal` बाहरी function का; declare किए बिना assignment नया local बना देता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
x = 0                              # module-level variable

def g() -> None:
    global x                       # bind name x to the module scope
    x += 1                         # modifies the global

def outer() -> int:
    n = 0                          # enclosing-function variable
    def inc() -> None:
        nonlocal n                 # bind n to outer's n
        n += 1                     # modifies outer's n
    inc(); inc()                   # call twice
    return n                       # returns 2

def bad() -> None:
    try:
        x += 1                     # assignment makes x LOCAL -> read before assign fails
    except UnboundLocalError as e:
        print("UnboundLocalError:", e)

# ============================================
# TEST CASES
# ============================================
g(); g()                           # global x becomes 2
print(x, outer())                  # Expected: 2 2
bad()
# Expected: UnboundLocalError: cannot access local variable 'x' where it is not associated with a value

def outer2() -> int:
    n = 0
    def inc() -> None:
        n = 5                      # creates a NEW local n, outer's n untouched
    inc()
    return n
print(outer2())                    # Expected: 0

try:
    exec("nonlocal q")             # nonlocal needs an enclosing function
except SyntaxError as e:
    print("SyntaxError:", e.msg)   # Expected: SyntaxError: nonlocal declaration not allowed at module level
```

---

## 🔍 Why This Works (3 lines max)
The compiler decides scope per function: any assignment to a name (without `global`/`nonlocal`) makes it local for the whole function body, so reading it earlier raises `UnboundLocalError`. The 3.13 message is "cannot access local variable ... where it is not associated with a value".
हिंदी: पूरा function compile होते समय तय हो जाता है कि नाम local है — इसलिए assign से पहले read करने पर error आता है।

---

## ⚡ Alternative Solution
```python
# Avoid nonlocal: use a closure over a mutable object or a class
def make_counter():
    state = {"n": 0}                 # mutable container, mutated not rebound
    def inc() -> int:
        state["n"] += 1              # no nonlocal needed
        return state["n"]
    return inc

c = make_counter()                   # create counter
c(); print(c())                      # Expected: 2
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: n = 5 inside inner() expecting to change outer's n (silently creates a local)
# ✅ Correct: add `nonlocal n` (or `global x` for module level)
```

---

## 🎯 Interview Tip (1 line)
Say: "Reading uses LEGB lookup; assigning needs `global`/`nonlocal`, otherwise Python creates a local — and prefer returning values or classes over global state."

---

## 🔗 Related Questions
→ Q041 (LEGB scope) | Q002 (late binding closure) | Q161 (closures) | Q122 (fix late binding closure bug)
