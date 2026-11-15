---

# Q050. for/while else Clause Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will this code print?

```python
for i in range(3):
    print("i", i)
else:
    print("for-else ran")

for i in range(3):
    if i == 1:
        break
else:
    print("never printed")
print("after break")

n = 0
while n < 2:
    n += 1
else:
    print("while-else ran, n =", n)

for i in []:
    pass
else:
    print("empty loop still runs else")

for i in range(3):
    if i == 1:
        continue
else:
    print("continue does not skip else")
```

---

## 💡 Quick Concept (2 lines only)
The `else` of a loop runs only if the loop finished without hitting `break` — think "no-break". `continue`, an empty loop, or a false `while` condition all still run it.
हिंदी: loop का `else` तभी चलता है जब loop बिना `break` के पूरा हो — यानी "no-break"।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

for i in range(3):                            # Step 1: loop runs 0, 1, 2
    print("i", i)                             # prints each value
else:
    print("for-else ran")                     # no break happened -> else runs

for i in range(3):                            # Step 2: loop with a break
    if i == 1:
        break                                 # break skips the else block
else:
    print("never printed")                    # skipped
print("after break")                          # normal code continues

n = 0                                         # Step 3: while-else works the same way
while n < 2:
    n += 1                                    # condition becomes False after 2 rounds
else:
    print("while-else ran, n =", n)           # condition ended the loop -> else runs

for i in []:                                  # Step 4: zero iterations
    pass
else:
    print("empty loop still runs else")       # no break -> else runs

for i in range(3):                            # Step 5: continue is not a break
    if i == 1:
        continue
else:
    print("continue does not skip else")      # runs

# ============================================
# TEST CASES (real output, Python 3.13)
# ============================================
# i 0
# i 1
# i 2
# for-else ran
# after break
# while-else ran, n = 2
# empty loop still runs else
# continue does not skip else
```

---

## 🔍 Why This Works (3 lines max)
`else` is attached to the loop and runs when the iterator is exhausted (or the `while` condition turns False). Only `break` jumps past it; a `return` or exception leaves the function entirely, so the else does not run either.
हिंदी: `else` loop के पूरा होने पर चलता है; सिर्फ `break` (या `return`/exception) इसे skip करता है।

---

## ⚡ Alternative Solution
```python
def is_prime(k: int) -> bool:
    for d in range(2, int(k ** 0.5) + 1):     # try divisors up to sqrt(k)
        if k % d == 0:
            break                             # found a divisor -> not prime
    else:
        return k > 1                          # no divisor found -> prime (if > 1)
    return False                              # reached only via break

print([x for x in range(2, 20) if is_prime(x)])  # Output: [2, 3, 5, 7, 11, 13, 17, 19]

def find(xs: list[int], t: int) -> None:
    for i, x in enumerate(xs):                # search with index
        if x == t:
            print("found at", i)              # found
            break
    else:
        print("not found")                    # loop exhausted without a find

find([1, 2, 3], 2)   # Output: found at 1
find([1, 2, 3], 9)   # Output: not found
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: reading `else` as "if the loop body never ran"
for i in []:
    pass
else:
    print("runs!")        # many expect no output - but it prints (no break occurred)

# ✅ Correct: use a flag or `if not items` when you mean "empty"
items: list[int] = []
if not items:
    print("empty")        # explicit intent
```

---

## 🎯 Interview Tip (1 line)
Say: "Loop `else` means 'no break' — great for search loops (found → break, else → not found); `continue` and empty loops still run it."

---

## 🔗 Related Questions
→ Q042 (try/except/else/finally) | Q049 (any/all empty) | Q103 (binary search) | Q126 (mutating list while iterating)
