---

# 074. Multiline Strings
# हिंदी में: Multiline Strings (कई लाइन वाली Strings)

---

## 🔵 Simple Definition (English)
A multiline string is a string that spans many lines. In Python you write it with triple quotes (`"""..."""` or `'''...'''`). Every new line and space inside the quotes becomes part of the string. It is also used for docstrings.

## 🔵 सरल परिभाषा (Hindi)
Multiline string वो string है जो कई lines में फैली होती है। Python में इसे triple quotes (`"""..."""` या `'''...'''`) से लिखते हैं। Quotes के अंदर हर नई line और space string का हिस्सा बन जाता है। Docstrings भी इसी से लिखे जाते हैं।

---

## 🔴 Problem it Solves
Long text like SQL queries, HTML, emails, and LLM prompts is painful with single quotes: you need `\n` everywhere and `+` to join pieces. It becomes unreadable. Triple quotes let you write the text exactly how it should look. JavaScript solved this with backticks (template literals); Python uses triple quotes.

## 🔴 यह क्यों बना? (Hindi)
लंबा text जैसे SQL query, HTML, email, LLM prompt single quotes में लिखना मुश्किल है: हर जगह `\n` और `+` लगाना पड़ता है, code पढ़ने लायक नहीं रहता। Triple quotes से text वैसा ही लिख सकते हैं जैसा दिखना चाहिए। JavaScript में यही काम backticks (template literals) करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python sees opening """ and starts collecting text
Step 2 → Every newline (Enter) inside is stored as the character \n
Step 3 → Every leading space / tab is also stored as-is
Step 4 → Python stops at the matching closing """
Step 5 → The result is ONE normal str object
Step 6 → Use textwrap.dedent / strip / splitlines to clean it

"""            <- starts with \n if text begins on next line
  line 1
  line 2
"""            <- ends with \n
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python opening """ देखकर text जमा करना शुरू करता है
Step 2 → अंदर हर Enter, \n character बनकर store होता है
Step 3 → शुरू के spaces / tabs भी वैसे ही store होते हैं
Step 4 → Matching closing """ पर रुकता है
Step 5 → नतीजा एक सामान्य str object है
Step 6 → textwrap.dedent / strip / splitlines से साफ करें
```

---

## 🟡 Real World Example
A Swiggy order service stores its SQL query in a triple-quoted string. An AI app keeps its system prompt (10+ lines) in a multiline string with placeholders like `{name}`. An email service builds the confirmation mail body from a template. Every function docstring (which FastAPI shows in Swagger docs) is a multiline string.

## 🟡 Real Example Hindi mein
Swiggy का order service अपनी SQL query triple-quoted string में रखती है। AI app अपना system prompt (10+ lines) multiline string में रखती है जिसमें `{name}` जैसे placeholders होते हैं। Email service confirmation mail की body template से बनाती है। हर function का docstring (जो FastAPI Swagger docs में दिखाता है) भी multiline string है।

---

## 💻 Code Example — Basic
```python
# Basic multiline string examples
import textwrap                          # helper to remove common indentation

sql: str = """
SELECT id, name
FROM users
WHERE active = 1
"""                                      # starts and ends with a newline
print(repr(sql))                         # repr shows hidden \n characters
print(sql.strip().splitlines())          # strip edges, then split into lines

a: str = "line1\nline2"                  # \n makes a new line in a normal string
b: str = r"C:\new\table"                 # raw string: backslash is NOT special
print(a)                                 # prints on two lines
print(b, len(b))                         # raw path stays as typed, length 12


def build_email(name: str, order_id: int) -> str:
    return textwrap.dedent(f"""\
        Hi {name},
        Your order #{order_id} is confirmed.
        Thanks!""")                      # \ after """ avoids the first empty line


print(build_email("Priya", 42))          # indentation removed by dedent

implicit: str = ("one "
                 "two "
                 "three")                # adjacent literals join automatically
print(implicit)                          # one two three

# Output:
# '\nSELECT id, name\nFROM users\nWHERE active = 1\n'
# ['SELECT id, name', 'FROM users', 'WHERE active = 1']
# line1
# line2
# C:\new\table 12
# Hi Priya,
# Your order #42 is confirmed.
# Thanks!
# one two three
```

## 💻 Code Example — Advanced
```python
# Production style: prompt templates, JSON bodies, docstrings
import textwrap                          # remove indentation
import json                              # build JSON text
from string import Template              # safe substitution with $name
from typing import Any                   # type hint for flexible dict

PROMPT_TEMPLATE: str = textwrap.dedent("""\
    You are a helpful assistant.
    User name: {name}
    Question: {question}
    Answer briefly.""")                  # module level constant, dedented once


def build_prompt(name: str, question: str) -> str:
    """Fill the prompt template with user data."""
    return PROMPT_TEMPLATE.format(name=name, question=question)   # str.format


def build_json_snippet(data: dict[str, Any]) -> str:
    """Return a small report containing pretty JSON."""
    body: str = json.dumps(data, indent=2)     # pretty JSON text
    return f"""Payload:
{body}"""                                      # f-string can be multiline too


def docstring_demo() -> None:
    """Short summary.

    Longer description here.
    """                                        # docstring = multiline string


print(build_prompt("Priya", "What is a slice?"))      # 4 clean lines
print(build_json_snippet({"id": 1, "ok": True}))      # Payload + JSON
doc: str = docstring_demo.__doc__ or ""               # docstring may be None
print(doc.splitlines()[0])                            # Short summary.

t: Template = Template("Hello $user, you owe $$$amount")   # $$ means literal $
print(t.substitute(user="Ravi", amount=50))                # Hello Ravi, you owe $50

text: str = """a
b
c"""                                                   # 3 lines, 2 newlines
print(text.splitlines(), text.count("\n"))             # ['a', 'b', 'c'] 2
print(len("""
"""))                                                  # only one \n -> 1

# Output:
# You are a helpful assistant.
# User name: Priya
# Question: What is a slice?
# Answer briefly.
# Payload:
# {
#   "id": 1,
#   "ok": true
# }
# Short summary.
# Hello Ravi, you owe $50
# ['a', 'b', 'c'] 2
# 1
```

---

## 🟠 JavaScript vs Python Comparison

| Feature | Python | JavaScript |
|---------|--------|-----------|
| Multiline syntax | `"""..."""` | `` `...` `` (backticks) |
| Insert variable | f-string `f"""{x}"""` | `${x}` |
| Raw string | `r"..."` | `String.raw\`...\`` |
| Remove indent | `textwrap.dedent` | manual / library |
| Docstring | built in (`__doc__`) | JSDoc comment only |

```python
# Python way
name: str = "Priya"                    # a variable
msg: str = f"""Hello {name},
Welcome to the app."""                 # f-string + triple quotes
print(msg)                             # two lines printed
```
```javascript
// JavaScript way
const name = "Priya";                  // a variable
const msg = `Hello ${name},
Welcome to the app.`;                  // template literal
console.log(msg);                      // two lines printed
```

Key difference: in Python a normal `"..."` string can NOT span lines (SyntaxError), only triple quotes can. JS normal quotes also cannot, only backticks. Python docstrings are real runtime data (`func.__doc__`), JS comments are not.

---

## 🟠 FastAPI Connection
FastAPI reads the docstring of your path function and shows it in Swagger UI (`/docs`) as the endpoint description. Markdown inside a multiline docstring is rendered. The `description=` argument also accepts a multiline string.

```python
# FastAPI example — docstring becomes API documentation
from fastapi import FastAPI              # import FastAPI

app: FastAPI = FastAPI()                 # create app


@app.get("/health", summary="Health check")      # register route
def health() -> dict[str, str]:
    """
    Check if the service is alive.

    - Returns **ok** when the API is running
    - Used by load balancers and Kubernetes
    """                                  # shown in Swagger UI as markdown
    return {"status": "ok"}              # JSON response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting that indentation inside triple quotes is part of the string
✅ Correct: use `textwrap.dedent` (or keep text at column 0)

```python
# Wrong — every line carries 8 leading spaces
def msg() -> str:
    return """
        Hello
        World
    """
# print(msg()) shows extra spaces and blank lines
# Right
import textwrap
def msg2() -> str:
    return textwrap.dedent("""\
        Hello
        World""")
```

❌ Mistake 2: Backslashes in Windows paths and regex
✅ Correct: use raw strings

```python
# Wrong — \n becomes a newline, \t becomes a tab
path = "C:\new\table"          # broken path, no error!
# Right
path = r"C:\new\table"         # raw string keeps backslashes
```

❌ Mistake 3: Building SQL with f-strings and user input (SQL injection)
✅ Correct: use parameters

```python
# Wrong — attacker controls user_id
user_id = "1 OR 1=1"
query = f"""SELECT * FROM users WHERE id = {user_id}"""
# Right — pass values separately to the driver
query = "SELECT * FROM users WHERE id = %s"     # driver fills %s safely
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
a = """
"""
b = """\
"""
print(len(a), len(b))
x = ("ab"
     "cd"
     , "ef")
print(x)
```
Answer: `1 0` — `a` contains exactly one newline character, `b` has a backslash right after the quotes which cancels the newline, so it is empty. Second print: `('abcd', 'ef')`. Adjacent string literals are joined at compile time, and the comma makes a tuple. A forgotten comma between list items silently joins strings — a famous bug.

---

## ⚫ Interview Questions + Answers

Q1: How do you remove the leading newline in a triple-quoted string?
A1: Put a backslash right after the opening quotes (`"""\`), or call `.strip()` / `.lstrip("\n")`. The backslash-newline is a line continuation inside the literal, so no `\n` is stored.

Q2: What is the difference between a docstring and a comment?
A2: A comment (`#`) is ignored by the interpreter. A docstring is a string literal that is the first statement in a module/class/function; Python stores it in `__doc__`. Tools like `help()`, Sphinx and FastAPI's Swagger read it at runtime.

Q3: What does a raw string do?
A3: Prefix `r` stops Python from processing escape sequences, so `r"\n"` is two characters: backslash and n. Used for regex patterns and Windows paths. A raw string cannot end with an odd number of backslashes.

Q4: How do you keep long text indented in code but without indentation in the value?
A4: Use `textwrap.dedent(text)`, which removes the common leading whitespace from all lines. With f-strings, be careful: dedent runs after the substitution, so inserted values with newlines can break the common indent.

Q5: Can you use triple quotes inside f-strings, and what about `{}`?
A5: Yes, `f"""..."""` works. Literal braces must be doubled: `{{` and `}}`. Since Python 3.12 you can also reuse the same quote type and use backslashes inside the `{}` expression part.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing SQL, HTML, prompts, emails, or help text
- Writing docstrings for modules, classes, functions
- Embedding small JSON or config samples in tests

❌ Avoid when:
- Text is very large — keep it in a separate `.txt` / `.sql` / template file
- Building SQL from user input — use parameterized queries
- Output needs a full template engine (loops, conditions) — use Jinja2

---

## 📊 Visual Diagram
```
sql = """
SELECT id
FROM users
"""

Stored value (each box is one character):

 \n | S E L E C T   i d | \n | F R O M   u s e r s | \n
 ^                        ^                          ^
 starts after the         Enter key                  last Enter
 opening quotes           stored as \n               before closing """

.strip()        -> removes the first and last \n
.splitlines()   -> ["SELECT id", "FROM users"]
textwrap.dedent -> removes common leading spaces from every line
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Triple quotes | `"""` or `'''` for multi-line text | तीन quotes वाली string |
| Docstring | String documenting a function/class | Function का documentation text |
| Raw string | `r"..."`, backslash not special | Backslash को सामान्य मानने वाली string |
| dedent | Remove common indentation | शुरू की indentation हटाना |
| Escape sequence | `\n`, `\t` special characters | खास characters का code |
| Implicit concatenation | Adjacent literals auto-join | पास-पास की strings अपने आप जुड़ना |

---

## ⚡ 3-Line Summary
English: Triple quotes create strings that span many lines and keep every newline and space. Use `textwrap.dedent` to clean indentation and raw strings for paths and regex. Docstrings are multiline strings that tools like Swagger read.
Hindi: Triple quotes से कई lines की string बनती है जिसमें हर newline और space रहता है। Indentation हटाने के लिए `textwrap.dedent` और paths/regex के लिए raw strings इस्तेमाल करें। Docstring भी multiline string है जिसे Swagger जैसे tools पढ़ते हैं।

---

## ➡️ Next Topic
**075. bytes + bytearray** — strings are text, but files, networks, and hashes work with raw bytes. Next we learn how Python represents binary data.
