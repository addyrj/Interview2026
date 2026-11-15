---

# 424. Builder Pattern
# हिंदी में: Builder Pattern (जटिल object को कदम-दर-कदम बनाना)

---

## 🔵 Simple Definition (English)
Builder separates how a complex object is built from the object itself. You call small methods one by one (`.size()`, `.topping()`) and finish with `.build()` that returns the finished, validated object.

## 🔵 सरल परिभाषा (Hindi)
Builder जटिल object बनाने के तरीके को object से अलग करता है। आप छोटे methods एक-एक करके बुलाते हैं (`.size()`, `.topping()`) और अंत में `.build()` से तैयार, validated object मिलता है।

---

## 🔴 Problem it Solves
A constructor with 12 parameters is unreadable: `Report('a', None, None, True, False, 10, None, ...)`. Many parameters are optional, some depend on others, and invalid combinations should be rejected. Builder gives named steps, optional parts, and one place to validate before the object exists.

## 🔴 यह क्यों बना? (Hindi)
12 parameters वाला constructor पढ़ने लायक नहीं रहता: `Report('a', None, None, True, False, 10, None, ...)`। कई parameters optional होते हैं, कुछ दूसरों पर निर्भर होते हैं, और गलत combinations reject होने चाहिए। Builder नाम वाले steps, optional हिस्से और object बनने से पहले validate करने की एक जगह देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a builder object holding the partial state
Step 2 → Call step methods (where(), order_by(), limit()), each returns self
Step 3 → Each step validates its own input (reject bad column names)
Step 4 → Call build(): final checks across all fields
Step 5 → build() returns an immutable product (frozen dataclass)
Step 6 → The product is used; the builder can be thrown away
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Builder object बनाओ जो अधूरी state रखता है
Step 2 → Step methods बुलाओ (where(), order_by(), limit()), हर एक self लौटाता है
Step 3 → हर step अपना input खुद validate करता है (गलत column नाम reject)
Step 4 → build() बुलाओ: सारे fields पर आखिरी जांच
Step 5 → build() immutable product लौटाता है (frozen dataclass)
Step 6 → Product इस्तेमाल होता है; builder फेंका जा सकता है
```

---

## 🟡 Real World Example
SQLAlchemy's `select().where().order_by().limit()` is a builder. A Zomato search service builds an Elasticsearch query from optional filters (city, veg, rating). An email library builds a message (`to`, `cc`, `attachments`) before sending. An LLM app builds a prompt from system message, context chunks, and user question.

## 🟡 Real Example Hindi mein
SQLAlchemy का `select().where().order_by().limit()` एक builder है। Zomato search service optional filters (city, veg, rating) से Elasticsearch query बनाती है। Email library भेजने से पहले message (`to`, `cc`, `attachments`) बनाती है। LLM app system message, context chunks और user question से prompt बनाता है।

---

## 💻 Code Example — Basic
```python
# Basic Builder: build a complex object step by step with chaining
from dataclasses import dataclass, field      # simple data holder


@dataclass
class Pizza:
    size: str = "medium"                      # default size
    toppings: list[str] = field(default_factory=list)   # safe mutable default
    extra_cheese: bool = False                # default no cheese


class PizzaBuilder:
    def __init__(self) -> None:
        self._pizza: Pizza = Pizza()          # object being built

    def size(self, s: str) -> "PizzaBuilder":
        self._pizza.size = s                  # set size
        return self                           # return self for chaining

    def topping(self, t: str) -> "PizzaBuilder":
        self._pizza.toppings.append(t)        # add one topping
        return self

    def cheese(self) -> "PizzaBuilder":
        self._pizza.extra_cheese = True       # turn on cheese
        return self

    def build(self) -> Pizza:
        return self._pizza                    # hand over finished object


p: Pizza = PizzaBuilder().size("large").topping("onion").topping("paneer").cheese().build()
print(p)

# Output:
# Pizza(size='large', toppings=['onion', 'paneer'], extra_cheese=True)
```

## 💻 Code Example — Advanced
```python
# Production style: immutable result + validation in build() + SQL query builder with params
from dataclasses import dataclass             # immutable config


@dataclass(frozen=True)
class Query:
    sql: str                                  # final SQL text
    params: tuple[object, ...]                # bound parameters (no string formatting!)


class QueryBuilder:
    def __init__(self, table: str) -> None:
        self._table: str = table              # table name
        self._where: list[str] = []           # conditions
        self._params: list[object] = []       # values for placeholders
        self._order: str | None = None        # optional order
        self._limit: int | None = None        # optional limit

    def where(self, column: str, value: object) -> "QueryBuilder":
        if not column.isidentifier():         # block SQL injection via column names
            raise ValueError(f"bad column: {column!r}")
        self._where.append(f"{column} = ?")   # placeholder, value stays separate
        self._params.append(value)
        return self

    def order_by(self, column: str) -> "QueryBuilder":
        if not column.isidentifier():
            raise ValueError(f"bad column: {column!r}")
        self._order = column
        return self

    def limit(self, n: int) -> "QueryBuilder":
        if n <= 0:
            raise ValueError("limit must be positive")
        self._limit = n
        return self

    def build(self) -> Query:
        sql: str = f"SELECT * FROM {self._table}"       # base
        if self._where:
            sql += " WHERE " + " AND ".join(self._where)
        if self._order:
            sql += f" ORDER BY {self._order}"
        if self._limit:
            sql += f" LIMIT {self._limit}"
        return Query(sql, tuple(self._params))          # frozen result


q: Query = QueryBuilder("orders").where("status", "paid").where("city", "Pune").order_by("created_at").limit(10).build()
print(q.sql)
print(q.params)
try:
    QueryBuilder("orders").where("status; DROP TABLE orders", 1)
except ValueError as e:
    print("Error:", e)

# Output:
# SELECT * FROM orders WHERE status = ? AND city = ? ORDER BY created_at LIMIT 10
# ('paid', 'Pune')
# Error: bad column: 'status; DROP TABLE orders'
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Optional arguments | keyword args with defaults (often enough) | options object `{a, b}` |
| Fluent chaining | return `self` | return `this` |
| Immutable result | `@dataclass(frozen=True)` | `Object.freeze()` |
| Real examples | SQLAlchemy `select()` | Knex.js, jQuery chaining |

```python
# Python way
q = QueryBuilder("orders").where("status", "paid").limit(10).build()   # fluent chain
```
```javascript
// JavaScript way (Knex.js style)
const q = knex("orders").where("status", "paid").limit(10).toSQL();    // same idea
```

Key difference: Python has keyword arguments and dataclass defaults, so many 'builders' are unnecessary: `Pizza(size='large', toppings=[...])` is already readable. Use a Builder when steps have order, validation across fields, or the product is built in stages (queries, prompts, HTTP requests).

---

## 🟠 FastAPI Connection
FastAPI query parameters are optional by nature, so a builder is a neat way to turn them into a database filter or search query inside a route. Keep the builder free of FastAPI types so you can unit test it alone.

```python
# FastAPI example (run with fastapi.testclient — no server needed)
from fastapi import FastAPI
from fastapi.testclient import TestClient

app: FastAPI = FastAPI()


class FilterBuilder:                          # builds a filter from optional query params
    def __init__(self) -> None:
        self.parts: dict[str, str] = {}
    def city(self, c: str | None) -> "FilterBuilder":
        if c: self.parts["city"] = c          # only add when given
        return self
    def veg(self, v: bool | None) -> "FilterBuilder":
        if v is not None: self.parts["veg"] = str(v)
        return self
    def build(self) -> dict[str, str]:
        return dict(self.parts)


@app.get("/restaurants")
def restaurants(city: str | None = None, veg: bool | None = None) -> dict[str, dict[str, str]]:
    return {"filter": FilterBuilder().city(city).veg(veg).build()}


c = TestClient(app)
print(c.get("/restaurants", params={"city": "Pune", "veg": True}).json())
print(c.get("/restaurants").json())

# Output:
# {'filter': {'city': 'Pune', 'veg': 'True'}}
# {'filter': {}}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `return self` in a step method
✅ Correct: every step returns the builder

```python
class Wrong:
    def size(self, s: str) -> None:        # Wrong: returns None
        self.s = s
# Wrong().size("L").build()                # AttributeError: 'NoneType' object has no attribute 'build'
class Right:
    def size(self, s: str) -> "Right":
        self.s = s
        return self                        # Right: chain continues
```

❌ Mistake 2: Putting user text directly into SQL strings
✅ Correct: validate identifiers and keep VALUES as bound parameters

```python
# Wrong
sql = f"SELECT * FROM t WHERE name = '{name}'"     # SQL injection
# Right
sql, params = "SELECT * FROM t WHERE name = ?", (name,)   # driver escapes the value
```

❌ Mistake 3: Returning the builder's internal mutable state from `build()`
✅ Correct: return a copy or a frozen object

```python
# Wrong: return self._items   # next .add() silently changes the 'finished' product
# Right: return tuple(self._items)  # or a frozen dataclass
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class B:
    def __init__(self): self.items = []
    def add(self, x): self.items.append(x); return self
    def build(self): return self.items        # returns internal list
b = B()
first = b.add("a").build()
second = b.add("b").build()
print(first, first is second)
```
Answer: Output: `['a', 'b'] True`. `build()` returns the builder's own internal list, not a copy. `first` and `second` are the same list object, so after the second `add('b')` the 'earlier product' also contains `'b'`. Fix: return `list(self.items)` or a tuple/frozen dataclass.

---

## ⚫ Interview Questions + Answers

Q1: When should you use Builder instead of keyword arguments?
A1: When construction has several steps, validation across fields, or optional parts that depend on each other (queries, prompts, HTTP requests). For plain optional values, dataclass defaults and keyword arguments are simpler.

Q2: Why return `self` from each method?
A2: It enables fluent chaining: `b.a().b().c().build()`. It is only a convenience; the pattern still works with separate statements.

Q3: Why should the product be immutable?
A3: After `build()` nobody should change it by accident, and the builder can be reused. A frozen dataclass or tuple prevents shared-state bugs.

Q4: What is a Director?
A4: In the classic GoF version, a Director class knows the recipe (which steps to call). In Python we usually skip it and write a plain function such as `make_standard_query(builder)`.

Q5: How does Builder differ from Factory?
A5: A Factory returns a finished object in one call. A Builder constructs it over many calls and returns it at the end. Factory answers 'which class?'; Builder answers 'how to assemble?'.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many optional parameters or construction in stages
- You must validate combinations before creating the object
- Building queries, prompts, emails, HTTP requests, test data

❌ Avoid when:
- Two or three simple fields: use the constructor or a dataclass
- Object never needs staged construction
- You would only wrap keyword arguments in extra code

---

## 📊 Visual Diagram
```
QueryBuilder("orders")
   .where("status","paid")   -> adds condition 1
   .where("city","Pune")     -> adds condition 2
   .order_by("created_at")   -> sets order
   .limit(10)                -> sets limit
   .build()                  -> Query(sql, params)   (frozen, final)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Builder | Object that assembles another step by step | दूसरा object कदम-दर-कदम बनाने वाला object |
| Fluent interface | Methods return self for chaining | Chaining के लिए self लौटाने वाले methods |
| Product | The final object that gets built | अंत में बनने वाला object |
| Director | Optional class that knows the recipe | Recipe जानने वाली optional class |
| Bound parameter | Value passed separately from SQL text | SQL text से अलग भेजी गई value |

---

## ⚡ 3-Line Summary
English: Builder assembles a complex object through small named steps and validates it in `build()`. Return `self` for chaining and return an immutable product. In Python, prefer plain keyword arguments unless staging or validation is really needed.
Hindi: Builder छोटे नाम वाले steps से जटिल object बनाता है और `build()` में validate करता है। Chaining के लिए `self` लौटाएं और immutable product दें। Python में जब तक staging या validation जरूरी न हो, सामान्य keyword arguments बेहतर हैं।

---

## ➡️ Next Topic
**425. Observer Pattern** — let many subscribers react when one subject changes.
