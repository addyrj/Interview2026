---

# 453. FizzBuzz
# हिंदी में: FizzBuzz (3 और 5 से भाग की classic पहेली)

Runnable solution with asserts: `main.py` in this folder (`python3 main.py` prints the 15 values and `All FizzBuzz tests passed`, verified on Python 3.13.3).

---

## 🔵 Simple Definition (English)
For numbers 1 to n: print `Fizz` if divisible by 3, `Buzz` if divisible by 5, `FizzBuzz` if divisible by both, otherwise the number itself.

## 🔵 सरल परिभाषा (Hindi)
1 से n तक की संख्याओं के लिए: 3 से भाग जाए तो `Fizz`, 5 से भाग जाए तो `Buzz`, दोनों से भाग जाए तो `FizzBuzz`, वरना संख्या खुद print करो।

---

## 🔴 Problem it Solves
It is a screening question that quickly shows whether a candidate can use the modulo operator, order conditions correctly and write clean loops. A good answer also discusses extensibility (what if a new rule "7 -> Bazz" is added?).

## 🔴 यह क्यों बना? (Hindi)
यह screening सवाल जल्दी बता देता है कि candidate modulo operator, conditions का सही क्रम और साफ़ loop लिख पाता है या नहीं। अच्छा जवाब extensibility पर भी बात करता है (अगर नया rule "7 -> Bazz" जुड़ जाए तो?)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Loop i from 1 to n inclusive: range(1, n + 1)
Step 2 → Check i % 15 == 0 FIRST (divisible by both 3 and 5)
Step 3 → Else check i % 3 == 0 -> "Fizz"
Step 4 → Else check i % 5 == 0 -> "Buzz"
Step 5 → Else use str(i)
Alt    → Build "Fizz" + "Buzz" pieces; if the result is empty, use the number
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → i को 1 से n तक चलाओ: range(1, n + 1)
Step 2 → सबसे पहले i % 15 == 0 जाँचो (3 और 5 दोनों से भाग)
Step 3 → वरना i % 3 == 0 -> "Fizz"
Step 4 → वरना i % 5 == 0 -> "Buzz"
Step 5 → वरना str(i)
विकल्प → "Fizz" + "Buzz" के टुकड़े जोड़ो; अगर खाली रहे तो संख्या इस्तेमाल करो
```

---

## 🟡 Real World Example
The rule-table version mirrors real business rules: a Swiggy promo engine tags orders "FREE_DELIVERY" if the order number is a multiple of 3 and "GIFT" if it is a multiple of 5; both tags apply together on multiples of 15. Rules live in a dictionary so product teams can add new ones without touching the loop.

## 🟡 Real Example Hindi mein
Rule-table वाला version असली business rules जैसा है: Swiggy का promo engine order number 3 का गुणज हो तो "FREE_DELIVERY" और 5 का गुणज हो तो "GIFT" tag लगाता है; 15 के गुणज पर दोनों tag साथ लगते हैं। Rules dictionary में रहते हैं, इसलिए product team loop छुए बिना नए rule जोड़ सकती है।

---

## 💻 Code Example — Basic
```python
# Basic FizzBuzz (full version with tests in main.py)
def fizzbuzz(n: int) -> list[str]:  # returns a list of strings
    out: list[str] = []  # collect results
    for i in range(1, n + 1):  # 1..n inclusive
        if i % 15 == 0:  # both 3 and 5 -> must be checked first
            out.append("FizzBuzz")
        elif i % 3 == 0:  # only 3
            out.append("Fizz")
        elif i % 5 == 0:  # only 5
            out.append("Buzz")
        else:  # neither
            out.append(str(i))
    return out  # finished list


print(", ".join(fizzbuzz(15)))  # join with commas
# Output: 1, 2, Fizz, 4, Buzz, Fizz, 7, 8, Fizz, Buzz, 11, Fizz, 13, 14, FizzBuzz
print(fizzbuzz(0))  # n = 0 gives an empty list
# Output: []
```

## 💻 Code Example — Advanced
```python
# From main.py: extensible, lazy rule-based version (generator = O(1) memory)
from typing import Dict, Iterator  # type hints


def fizzbuzz_rules(n: int, rules: Dict[int, str]) -> Iterator[str]:
    """Any divisor -> word rules; words are concatenated in dict order."""
    for i in range(1, n + 1):  # each number
        word: str = "".join(w for d, w in rules.items() if i % d == 0)  # all matching words
        yield word or str(i)  # empty string is falsy -> fall back to the number


print(list(fizzbuzz_rules(15, {3: "Fizz", 5: "Buzz"}))[-1])  # classic rules
# Output: FizzBuzz
print(list(fizzbuzz_rules(7, {3: "Fizz", 5: "Buzz", 7: "Bazz"}))[-1])  # add a new rule, no code change
# Output: Bazz
for line in fizzbuzz_rules(1_000_000_000, {3: "Fizz", 5: "Buzz"}):  # a billion numbers, lazily
    break  # we only take the first one; nothing else is computed
print(line)  # Output: 1
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
for i in range(1, 16):
    print("Fizz" * (i % 3 == 0) + "Buzz" * (i % 5 == 0) or i)   # bool * str trick
```
```javascript
// JavaScript
for (let i = 1; i <= 15; i++) {
  console.log((i % 3 === 0 ? "Fizz" : "") + (i % 5 === 0 ? "Buzz" : "") || i);
}
```

Key differences: both use `%` and the `or`/`||` fallback on an empty string. Python's `range(1, 16)` excludes 16, while JS needs `i <= 15`. In Python `"Fizz" * True` is `"Fizz"` because `True == 1`; JS needs a ternary.

---

## 🟠 FastAPI Connection
FizzBuzz-style rule tables are how real APIs apply configurable business rules. A query parameter controls the range; `Query(le=...)` protects the server from huge inputs.

```python
# FastAPI: FizzBuzz endpoint (pip install fastapi)
from fastapi import FastAPI, Query  # framework

app: FastAPI = FastAPI()  # create app
RULES: dict[int, str] = {3: "Fizz", 5: "Buzz"}  # configurable rules


@app.get("/fizzbuzz")  # GET /fizzbuzz?n=15
def fizzbuzz(n: int = Query(15, ge=1, le=10_000)) -> list[str]:  # validate 1..10000
    return ["".join(w for d, w in RULES.items() if i % d == 0) or str(i) for i in range(1, n + 1)]
```

Not run as a server here; the same logic is verified in `main.py`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Checking 3 and 5 before 15
✅ Correct: check 15 first (or use the concatenation trick).

```python
# Wrong: 15 prints "Fizz" because the first branch wins
for i in (15,):
    if i % 3 == 0: print("Fizz")
    elif i % 15 == 0: print("FizzBuzz")   # never reached
# Right
for i in (15,):
    if i % 15 == 0: print("FizzBuzz")
```

❌ Mistake 2: Off-by-one: `range(1, n)` misses n
✅ Correct: `range(1, n + 1)`.

❌ Mistake 3: Printing numbers as ints and words as strs mixed in a list
✅ Correct: convert with `str(i)` so the return type is consistently `list[str]`.

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
print(["Fizz" * (i % 3 == 0) + "Buzz" * (i % 5 == 0) or i for i in range(13, 16)])
```

**Answer**: `[13, 14, 'FizzBuzz']`. For 13 both pieces are empty strings, so `"" or 13` gives `13` (an int, not a str). For 15 both multiplications give their words and the join is `"FizzBuzz"`. Note the mixed types in the list.

---

## ⚫ Interview Questions + Answers

Q1: Why must 15 be checked first?
A1: Any multiple of 15 is also a multiple of 3 and 5, so `i % 3` would match first and `FizzBuzz` would never print.

Q2: How do you avoid checking 15 explicitly?
A2: Build the output by concatenating `"Fizz"` if divisible by 3 and `"Buzz"` if divisible by 5; use the number if the result is empty.

Q3: How do you make it extensible to more rules?
A3: Use a dict or list of `(divisor, word)` pairs and join the matching words, as in `fizzbuzz_rules`.

Q4: What is the time and space complexity?
A4: O(n) time. Space is O(n) for a list or O(1) with a generator.

Q5: Can you print without a loop?
A5: Yes, with a list comprehension or `map`, but a plain loop is clearer; interviewers care about correctness and clarity, not cleverness.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want to demonstrate modulo logic and clean branching
- Business rules map divisors/conditions to labels
- You need a lazy stream of labelled values (generator version)

❌ Avoid when:
- Rules depend on complex state (use a rule engine or strategy pattern)
- You hard-code every rule in nested `if` statements that will keep growing
- You need performance on enormous n without a generator

---

## 📊 Visual Diagram

```
 i :   1  2  3     4  5     6  ... 15
 %3 :  -  -  ✔     -  -     ✔      ✔
 %5 :  -  -  -     -  ✔     -      ✔
 out:  1  2 Fizz   4 Buzz  Fizz    FizzBuzz

 rules = {3:"Fizz", 5:"Buzz"}  ->  join(matching words) or str(i)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Modulo `%` | Remainder after division | भाग के बाद शेषफल |
| Divisible | Remainder is 0 | पूरा भाग जाता है |
| Generator | Lazy value producer | आलसी (lazy) value बनाने वाला |
| Falsy | Treated as False (e.g. `""`) | False की तरह माना जाने वाला |
| Off-by-one | Boundary mistake | सीमा की एक की गलती |
| Rule table | Data-driven rules | data से चलने वाले नियम |

---

## ⚡ 3-Line Summary
English: Use `%` to test divisibility and check the combined case (15) first. The concatenation trick or a rule dictionary removes the special case and makes it extensible. A generator keeps memory constant.
Hindi: Divisibility के लिए `%` इस्तेमाल करें और संयुक्त case (15) सबसे पहले जाँचें। Concatenation trick या rule dictionary special case हटाकर extensible बनाती है। Generator से memory स्थिर रहती है।

---

## ➡️ Next Topic
**454. Fibonacci Series** — recursion vs memoization vs iteration, and why naive recursion is slow.
