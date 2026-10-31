---

# 024. Comments + Docstrings
# हिंदी में: Comments + Docstrings — code को document करना

---

## 🔵 Simple Definition (English)
A **comment** starts with `#` and is ignored by Python; it explains *why* the code does something. A **docstring** is a triple-quoted string placed as the first statement of a module, class or function; Python stores it in `__doc__`, so tools like `help()`, IDEs and FastAPI's `/docs` page can read it.

## 🔵 सरल परिभाषा (Hindi)
**Comment** `#` से शुरू होता है और Python उसे ignore करता है; यह बताता है कि code *क्यों* ऐसा है। **Docstring** module, class या function की पहली line में triple-quote string होती है; Python उसे `__doc__` में रखता है, इसलिए `help()`, IDE और FastAPI का `/docs` page उसे पढ़ सकते हैं।

---

## 🔴 Problem it Solves
Code is read ten times more than it is written. Six months later even you forget why a strange `if` exists. Without documentation, new team members waste hours guessing. Comments explain intent and warnings; docstrings describe the public contract (what goes in, what comes out, what errors) in a form that tools can extract.

## 🔴 यह क्यों बना? (Hindi)
Code लिखा एक बार जाता है, पढ़ा दस बार जाता है। छह महीने बाद आप खुद भूल जाते हैं कि कोई अजीब `if` क्यों है। Documentation न हो तो नए लोग घंटों अंदाज़ा लगाते हैं। Comments intent और warning बताते हैं; docstrings public contract (क्या अंदर, क्या बाहर, कौन सी errors) बताते हैं, और tools उन्हें निकाल सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python's tokenizer sees "#" and ignores the rest of that line
Step 2 → A string literal that is the FIRST statement of a module/class/def
         is NOT ignored: the compiler stores it as __doc__
Step 3 → help(obj), obj.__doc__, IDE hover and doc generators read __doc__
Step 4 → Any other triple-quoted string in the middle of code is just an
         unused string expression (not a docstring, not a real comment)
Step 5 → Doc tools (Sphinx, pydoc, FastAPI) turn docstrings into docs pages
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → "#" दिखते ही Python उस line का बाकी हिस्सा ignore करता है
Step 2 → module/class/def की पहली statement अगर string है तो वह __doc__ बनती है
Step 3 → help(), __doc__, IDE hover और doc tools उसे पढ़ते हैं
Step 4 → बीच में कहीं और triple-quote string सिर्फ एक unused expression है
Step 5 → Sphinx, pydoc, FastAPI इन्हीं से docs page बनाते हैं
```

---

## 🟡 Real World Example
At Razorpay-style payment teams, a function `refund(payment_id, amount)` has a docstring that lists arguments, return value and exceptions (`Raises: ValueError if amount > captured`). Inline comments mark business rules: `# RBI rule: refunds must be within 180 days`. In FastAPI, the docstring of an endpoint function becomes the description in Swagger UI (`/docs`), so frontend developers read your docstring as API documentation.

## 🟡 Real Example Hindi mein
Payment company में `refund(payment_id, amount)` function का docstring arguments, return value और exceptions लिखता है। Inline comment business rule बताता है: `# RBI rule: 180 दिन के अंदर refund`। FastAPI में endpoint function का docstring Swagger UI (`/docs`) का description बन जाता है, यानी frontend developer आपका docstring API documentation की तरह पढ़ता है।

---

## 💻 Code Example — Basic
```python
# Comments and docstrings basics

# 1. Single-line comment: whole line
x: int = 10                      # 2. Inline comment: after code (two spaces before #)

# 3. Multi-line "comment": just use several # lines (Python has no /* */)
# Line one of the explanation
# Line two of the explanation

# 4. Docstring: first statement inside a function
def area(width: float, height: float) -> float:
    """Return the area of a rectangle."""       # one-line docstring
    return width * height                       # the actual work


# 5. Multi-line docstring: summary, blank line, details
def greet(name: str) -> str:
    """Return a greeting.

    Args:
        name: Person to greet.

    Returns:
        A greeting message.
    """
    return f"Hello, {name}"                     # build the message


# 6. Read the docstring at runtime
print(area.__doc__)              # Output: Return the area of a rectangle.
print(area(3, 4))                # Output: 12
print(greet("Priya"))            # Output: Hello, Priya

# 7. help() shows the docstring nicely
help(area)                       # prints signature + docstring

# 8. Comment out code while debugging
# print("this line will not run")
print("done")                    # Output: done
```

## 💻 Code Example — Advanced
```python
"""Payments module.

Module docstring: first statement of the file. Describes the whole module.
"""
from dataclasses import dataclass       # for a small model
import inspect                          # to read docs programmatically


@dataclass
class Payment:
    """A captured payment.

    Attributes:
        payment_id: Unique id such as ``pay_123``.
        captured: Amount captured, in rupees.
        refunded: Amount already refunded, in rupees.
    """

    payment_id: str                     # unique id
    captured: float                     # money received
    refunded: float = 0.0               # money returned so far

    def refund(self, amount: float) -> float:
        """Refund part of the payment.

        Args:
            amount: Rupees to refund. Must be > 0 and <= remaining balance.

        Returns:
            The new total refunded amount.

        Raises:
            ValueError: If the amount is invalid or exceeds what is left.

        Example:
            >>> p = Payment("pay_1", 500.0)
            >>> p.refund(200.0)
            200.0
        """
        remaining: float = self.captured - self.refunded    # money still refundable
        if amount <= 0:                                      # reject zero / negative
            raise ValueError("amount must be positive")
        # WHY (not what): gateways reject refunds above the captured amount,
        # so we fail early and avoid a paid API round trip.
        if amount > remaining:                               # more than available
            raise ValueError(f"only {remaining} left to refund")
        self.refunded += amount                              # update state
        return self.refunded                                 # report new total


def main() -> None:
    payment: Payment = Payment("pay_1", 500.0)   # create a payment
    print(Payment.__doc__.splitlines()[0])       # Output: A captured payment.
    print(inspect.getdoc(Payment.refund).splitlines()[0])
    # Output: Refund part of the payment.
    print(payment.refund(200.0))                 # Output: 200.0

    try:
        payment.refund(900.0)                    # too much
    except ValueError as exc:                    # documented in "Raises"
        print("Error:", exc)                     # Output: Error: only 300.0 left to refund

    # TODO / FIXME / NOTE tags are searchable conventions
    # TODO: add idempotency key support
    # FIXME: partial refunds are not rounded to paise

    # Doctest: run the >>> examples inside docstrings as tests
    import doctest                               # standard library tool
    result = doctest.testmod(verbose=False)      # runs examples found in this file
    print("doctest failures:", result.failed)    # Output: doctest failures: 0


if __name__ == "__main__":
    main()                                       # run only when executed directly
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
# single line comment
x = 5  # inline comment

def add(a: int, b: int) -> int:
    """Add two numbers.

    The docstring is available at runtime: add.__doc__
    """
    return a + b

print(add.__doc__)        # docstring is real data on the function object
```
```javascript
// JavaScript
// single line comment
let x = 5; // inline comment

/* multi-line
   comment */

/**
 * Add two numbers.
 * @param {number} a
 * @param {number} b
 * @returns {number}
 */
function add(a, b) {
  return a + b;
}

console.log(add.toString()); // JSDoc is only a comment, NOT available at runtime
```

Key differences: Python has **no multi-line comment syntax**; use several `#` lines. JSDoc comments are thrown away at runtime, but Python docstrings are stored in `__doc__` and can be read by code (that is how `help()`, pytest doctest and FastAPI work).

---

## 🟠 FastAPI Connection
FastAPI uses your docstring as the endpoint description in Swagger UI and ReDoc. You can also pass `summary=` and `description=` explicitly. Markdown in the docstring is rendered in the docs page. The text after `\f` (form feed) is hidden from the docs, handy for internal notes.

```python
# FastAPI example (needs: pip install fastapi)
from fastapi import FastAPI                          # the web framework

app: FastAPI = FastAPI()                             # create the app


@app.post("/refunds", summary="Create a refund")     # shown as title in /docs
async def create_refund(payment_id: str, amount: float) -> dict[str, float]:
    """
    Refund part of a captured payment.

    - **payment_id**: id of the payment
    - **amount**: rupees to refund (must be positive)

    Returns the refunded amount.
    \f
    Internal note: this part is NOT shown in the OpenAPI docs.
    """
    return {"refunded": amount}                      # JSON response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Comment that repeats the code
```python
# Wrong: says what the code already says
i = 0        # set i to zero

# Right: explain WHY
retry_count = 0   # gateway allows max 3 retries, we count from zero
```

❌ Mistake 2: Putting the docstring after the code
```python
# Wrong: this is just an unused string, NOT a docstring
def f():
    x = 1
    """I am not a docstring"""
    return x

print(f.__doc__)     # Output: None

# Right: docstring must be the FIRST statement
def g():
    """I am a docstring"""
    return 1

print(g.__doc__)     # Output: I am a docstring
```

❌ Mistake 3: Outdated comments
```python
# Wrong: comment lies, code changed
# tax is 5%
tax_rate = 0.18

# Right: update or delete comments when code changes
# GST is 18% for this category
tax_rate = 0.18
```

❌ Mistake 4: Commenting out dead code and leaving it forever
```python
# Wrong: old_price = price * 0.9   <- dead code stays in the file for years
# Right: delete it; Git history remembers everything
price = 100
print(price)
```

---

## 🧠 Tricky Interview Question

```python
def a():
    "first"
    "second"

def b():
    x = 1
    "not doc"

class C:
    '''class doc'''

print(a.__doc__)
print(b.__doc__)
print(C.__doc__)
print(len((lambda: 1).__doc__ or ""))
```

**Answer:**
```
first
None
class doc
0
```
Only the **first** string statement is the docstring, so `a.__doc__` is `"first"` (`"second"` is ignored). In `b`, the string comes after `x = 1`, so it is not a docstring: `None`. Class docstring works the same. Lambdas cannot contain statements, so they have no docstring (`None`), and `None or ""` gives an empty string of length 0. Also remember: `python -OO` strips docstrings completely, so never put required logic in `__doc__`.

---

## ⚫ Interview Questions + Answers

Q1: How do you write a multi-line comment in Python?
A1: Python has no block comment syntax. Use a `#` on every line (editors toggle this with Ctrl+/). A bare triple-quoted string is sometimes used, but it is really an unused string expression, not a comment, and it wastes a little memory in some cases. Use it only as a real docstring.

Q2: What is the difference between a comment and a docstring?
A2: A comment is removed by the tokenizer and never exists at runtime. A docstring is a real string object stored in `__doc__`, accessible with `help()`, `inspect.getdoc()`, and used by tools (Sphinx, pytest `--doctest-modules`, FastAPI). Comments explain *why* for maintainers; docstrings explain *what/how to use* for callers.

Q3: What are common docstring styles?
A3: Google style (`Args:`, `Returns:`, `Raises:`), NumPy style (underlined sections), and reStructuredText/Sphinx style (`:param x:`). Pick one per project. PEP 257 defines the basic conventions: triple double quotes, one-line summary, blank line, then details.

Q4: What is a doctest?
A4: Examples written as `>>> code` followed by expected output inside a docstring. `python -m doctest file.py` or `doctest.testmod()` runs them and compares output. It keeps documentation honest because broken examples fail. It is good for simple pure functions, but not a replacement for pytest.

Q5: Why are type hints considered better than comments for types?
A5: A comment like `# x is int` can silently go stale. A type hint `x: int` is part of the code, checked by mypy/pyright, read by IDEs and used by FastAPI/Pydantic for validation. Use docstrings for meaning, hints for types. Do not repeat types in both unless your style guide asks for it.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Explaining *why* (business rule, workaround, link to a bug)
- Every public module, class and function (docstring)
- API endpoints (shows in Swagger)
- Warnings: `# NOTE: order matters here`

❌ Avoid when:
- The comment only repeats the code
- You can rename a variable/function to be self-explanatory
- You are tempted to keep dead code (use Git)
- Docstring would hide required behaviour (docstrings can be stripped with `-OO`)

---

## 📊 Visual Diagram
```
 source file
 ├── # comment            ──► tokenizer drops it  (not in bytecode)
 ├── """module docstring""" ─► module.__doc__
 ├── def f():
 │       """f docs"""     ──► f.__doc__
 │       code...
 └── class C:
         """C docs"""     ──► C.__doc__

 __doc__ ──► help() / IDE hover / Sphinx / pytest doctest / FastAPI /docs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Comment | Note ignored by Python, starts with `#` | Python जिसे ignore करता है |
| Docstring | String documenting a module/class/function | Documentation string |
| `__doc__` | Attribute storing the docstring | Docstring रखने वाला attribute |
| PEP 257 | Docstring conventions | Docstring के नियम |
| doctest | Tests written inside docstrings | Docstring के अंदर tests |
| Inline comment | Comment on the same line as code | Code वाली line पर comment |
| TODO | Marker for future work | आगे करने वाला काम |

---

## ⚡ 3-Line Summary
English: Comments (`#`) explain *why* and are ignored by Python. Docstrings (`"""..."""` as the first statement) are stored in `__doc__` and power `help()`, IDEs, doctest and FastAPI docs. Python has no block comment, and a docstring placed after other code is not a docstring.
Hindi: Comments (`#`) *क्यों* बताते हैं और Python उन्हें ignore करता है। Docstring (पहली statement में `"""..."""`) `__doc__` में रहता है और `help()`, IDE, doctest, FastAPI docs में काम आता है। Block comment नहीं होता, और code के बाद लिखा string docstring नहीं होता।

---

## ➡️ Next Topic
**025. Python Indentation Rules** — how Python uses whitespace instead of braces, and the errors that come with it.
