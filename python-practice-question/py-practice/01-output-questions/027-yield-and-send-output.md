---

# Q027. yield and send() output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What will the following code print?

```python
def acc():
    total = 0
    while True:
        v = yield total          # yield is an expression
        print("got", v)
        if v is None:
            continue
        total += v

a = acc()
print(next(a))                   # (a)
print(a.send(5))                 # (b)
print(a.send(10))                # (c)
print(next(a))                   # (d)

b = acc()
try:
    b.send(1)                    # (e)
except TypeError as e:
    print(e)
```

---

## 💡 Quick Concept (2 lines only)
`yield` is an expression: `send(x)` resumes the generator and makes the paused `yield` evaluate to `x`, then runs to the next `yield` and returns its value. `next(g)` is `send(None)`.
हिंदी: `send(x)` पिछले `yield` की जगह x रख देता है और अगला yield value लौटाता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
def acc():                              # Step 1: running-total coroutine
    total = 0                           # State kept between sends
    while True:                         # Loop forever
        v = yield total                 # Pause: emit total, receive the sent value into v
        print("got", v)                 # Show what we received
        if v is None:                   # next() sends None
            continue                    # Ignore it
        total += v                      # Add the sent number

a = acc()                               # Step 2: create (no code has run yet)
print(next(a))                          # (a) runs to first yield -> 0
print(a.send(5))                        # (b) prints "got 5", then 5
print(a.send(10))                       # (c) prints "got 10", then 15
print(next(a))                          # (d) prints "got None", then 15

b = acc()                               # Step 3: fresh generator
try:
    b.send(1)                           # (e) not started: no yield to receive the value
except TypeError as e:
    print(e)                            # can't send non-None value to a just-started generator

# ============================================
# TEST CASES
# ============================================
# Expected output (real run, Python 3.13):
# 0
# got 5
# 5
# got 10
# 15
# got None
# 15
# can't send non-None value to a just-started generator
```

---

## 🔍 Why This Works (3 lines max)
The first `next()` ("priming") runs up to the first `yield`; only then can a value be received. Each `send` delivers the value, runs the body until the next `yield`, and returns that yielded value.
हिंदी: पहले `next()` से generator को "prime" करना ज़रूरी है, फिर `send()`।

---

## ⚡ Alternative Solution
```python
def g2():                                # Generator with return value
    x = yield 1                          # Receive into x
    print("x", x)                        # Show it
    y = yield 2                          # Receive into y
    print("y", y)                        # Show it
    return "done"                        # Becomes StopIteration.value

h = g2()                                 # Create
print(next(h))                           # 1
print(h.send("A"))                       # x A, then 2
try:
    h.send("B")                          # y B, then generator finishes
except StopIteration as e:
    print("val", e.value)                # val done

def g3():                                # throw() raises inside the generator
    try:
        yield 1                          # Paused here
    except ValueError:                   # Exception arrives at the yield
        print("caught")                  # Handle it
        yield 99                         # Keep going
k = g3(); next(k)                        # Prime
print(k.throw(ValueError))               # caught, then 99
k.close()                                # Stops generator (GeneratorExit)

def g4():                                # yield from delegates and returns sub-generator's value
    r = yield from g2()                  # Sub-generator receives None via list()
    print("r", r)                        # r done
    yield 3                              # Extra value
print(list(g4()))                        # x None, y None, r done, then [1, 2, 3]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: sending before priming
c = acc()                                # acc from above
# c.send(5)   # TypeError: can't send non-None value to a just-started generator

# ✅ Correct: prime first (next() or send(None)), or wrap with a decorator
c = acc()                                # New generator
next(c)                                  # Prime -> 0
print(c.send(5))                         # got 5, then 5
```

---

## 🎯 Interview Tip (1 line)
Say: "yield is an expression; prime with next(), `send()` pushes values in, `throw()`/`close()` push exceptions — the basis of coroutines before async/await."

---

## 🔗 Related Questions
→ Q025 (generator exhaustion) | Q026 (generator laziness) | Q120 (iterator class)
