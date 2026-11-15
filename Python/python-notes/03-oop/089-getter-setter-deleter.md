---

# 089. Getter + Setter + Deleter
# हिंदी में: Getter + Setter + Deleter

---

## 🔵 Simple Definition (English)
A property can have three parts: a getter (runs on read), a setter (runs on assignment) and a deleter (runs on `del`). Together they let you validate, clean and protect an attribute while callers keep using simple `obj.x` syntax.

## 🔵 सरल परिभाषा (Hindi)
Property के तीन हिस्से हो सकते हैं: getter (पढ़ने पर चलता है), setter (value डालने पर चलता है) और deleter (`del` पर चलता है)। इनसे आप attribute को validate, साफ़ और सुरक्षित रख सकते हैं जबकि callers सरल `obj.x` ही लिखते हैं।

---

## 🔴 Problem it Solves
If any code can write `user.age = -50` or `product.price = 'abc'`, bad data silently enters the system and breaks something far away. A setter checks the value at the exact moment of assignment and fails early with a clear error. A deleter makes `del obj.x` release resources (close a connection) instead of just removing a key.

## 🔴 यह क्यों बना? (Hindi)
अगर कोई भी code `user.age = -50` या `product.price = 'abc'` लिख सकता है तो गलत data चुपचाप system में घुस जाता है और कहीं दूर जाकर कुछ तोड़ता है। Setter value डालने के ठीक समय उसे जाँचता है और साफ़ error से जल्दी fail करता है। Deleter `del obj.x` पर resources (जैसे connection) बंद करता है, सिर्फ key नहीं हटाता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `@property def name` defines the getter and creates the property
Step 2 → `@name.setter` returns a COPY of the property with a setter added
Step 3 → `@name.deleter` does the same for `del`
Step 4 → All three functions must use the SAME name so the final property has all parts
Step 5 → `obj.name = v` → setter runs → validate → store in `_name`
Step 6 → `del obj.name` → deleter runs → cleanup
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `@property def name` getter बनाता है और property तैयार करता है
Step 2 → `@name.setter` setter जुड़ी property की COPY लौटाता है
Step 3 → `@name.deleter` `del` के लिए यही करता है
Step 4 → तीनों functions का नाम SAME होना चाहिए ताकि आखिरी property में सारे हिस्से हों
Step 5 → `obj.name = v` → setter चलता है → validate → `_name` में store
Step 6 → `del obj.name` → deleter चलता है → cleanup
```

---

## 🟡 Real World Example
A signup `User` setter trims and title-cases the name and rejects empty ones. A `Config.rate_limit` setter allows only 1 to 1000. A `Temperature` object exposes `celsius` and `fahrenheit` as two linked properties. A DB `Session.conn` deleter closes the connection when you `del session.conn`.

## 🟡 Real Example Hindi mein
Signup `User` का name setter trim और title-case करता है और खाली name reject करता है। `Config.rate_limit` setter सिर्फ 1 से 1000 मानता है। `Temperature` object `celsius` और `fahrenheit` दो linked properties देता है। DB `Session.conn` का deleter `del session.conn` पर connection बंद करता है।

---

## 💻 Code Example — Basic
```python
# Basic: full property with getter, setter and deleter
class Person:
    def __init__(self, name: str) -> None:
        self._name: str = name                    # real storage

    @property                                     # GETTER: p.name
    def name(self) -> str:
        print("getting")
        return self._name

    @name.setter                                  # SETTER: p.name = "x"
    def name(self, value: str) -> None:
        print("setting")
        if not value.strip():                     # validate
            raise ValueError("name cannot be empty")
        self._name = value.strip().title()        # clean the data

    @name.deleter                                 # DELETER: del p.name
    def name(self) -> None:
        print("deleting")
        del self._name


p: Person = Person("asha")
print(p.name)
p.name = "  raj kumar "
print(p.name)
try:
    p.name = "   "
except ValueError as e:
    print("Error:", e)
del p.name
print(hasattr(p, "_name"))
try:
    p.name
except AttributeError as e:
    print("Error:", e)

# Output:
# getting
# asha
# setting
# getting
# Raj Kumar
# setting
# Error: name cannot be empty
# deleting
# False
# getting
# Error: 'Person' object has no attribute '_name'
```

## 💻 Code Example — Advanced
```python
# Advanced: temperature with two linked properties, plus a reusable validator descriptor-free pattern
from __future__ import annotations


class Temperature:
    ABS_ZERO_C = -273.15

    def __init__(self, celsius: float = 0.0) -> None:
        self.celsius = celsius                    # setter runs here too

    @property
    def celsius(self) -> float:
        return self._c

    @celsius.setter
    def celsius(self, v: float) -> None:
        if v < self.ABS_ZERO_C:
            raise ValueError(f"below absolute zero: {v}")
        self._c = float(v)

    @property
    def fahrenheit(self) -> float:                # second view of the same data
        return round(self._c * 9 / 5 + 32, 2)

    @fahrenheit.setter
    def fahrenheit(self, f: float) -> None:
        self.celsius = (f - 32) * 5 / 9           # reuse the validating setter


t = Temperature(100)
print(t.celsius, t.fahrenheit)
t.fahrenheit = 32
print(t.celsius)
try:
    t.celsius = -300
except ValueError as e:
    print("Error:", e)


class Session:                                    # deleter releases resources
    def __init__(self) -> None:
        self._conn: str | None = "conn-1"

    @property
    def conn(self) -> str | None:
        return self._conn

    @conn.deleter
    def conn(self) -> None:
        print("closing", self._conn)
        self._conn = None


s = Session()
del s.conn
print(s.conn)

# Output:
# 100.0 212.0
# 0.0
# Error: below absolute zero: -300
# closing conn-1
# None
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Getter | `@property` | `get x() {}` |
| Setter | `@x.setter` | `set x(v) {}` |
| Deleter | `@x.deleter` | no equivalent (use `delete` with Proxy) |
| Names must match | yes, same function name | yes, same property name |
| Trigger setter in init | `self.x = v` in `__init__` | `this.x = v` in constructor |

```python
# Python way
class P:
    def __init__(self) -> None:
        self._age = 0
    @property
    def age(self) -> int:
        return self._age
    @age.setter
    def age(self, v: int) -> None:
        if v < 0:
            raise ValueError("age must be >= 0")
        self._age = v

p = P()
p.age = 30
```
```javascript
// JavaScript way
class P {
  #age = 0;
  get age() { return this.#age; }
  set age(v) {
    if (v < 0) throw new RangeError("age must be >= 0");
    this.#age = v;
  }
}
const p = new P();
p.age = 30;
```

Key difference: Python has an official `deleter` for `del obj.x`; JavaScript has no property deleter (you would need a `Proxy`). In both languages the setter also runs inside the constructor if you assign through the public name.

---

## 🟠 FastAPI Connection
Config objects and domain models use setters to enforce rules at assignment time. For request data FastAPI uses Pydantic validators instead (`field_validator`), which run when the body is parsed. Use setters for objects that live longer than one request and are mutated.

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


class Config:
    def __init__(self) -> None:
        self._rate_limit = 10

    @property
    def rate_limit(self) -> int:
        return self._rate_limit

    @rate_limit.setter
    def rate_limit(self, v: int) -> None:
        if not 1 <= v <= 1000:
            raise ValueError("rate_limit must be 1..1000")
        self._rate_limit = v


cfg = Config()


@app.put("/admin/rate/{n}")
def set_rate(n: int):
    try:
        cfg.rate_limit = n                        # setter validates
    except ValueError as e:
        return {"error": str(e)}
    return {"rate_limit": cfg.rate_limit}


c = TestClient(app)
print(c.put("/admin/rate/50").json(), c.put("/admin/rate/5000").json())

# Output:
# {'rate_limit': 50} {'error': 'rate_limit must be 1..1000'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assigning to the property name inside its own setter
✅ Correct: store in the underscore name

```python
class A:
    @property
    def x(self) -> int:
        return self._x
    @x.setter
    def x(self, v: int) -> None:
        self.x = v          # Wrong: calls the setter again
a = A()
try:
    a.x = 1
except RecursionError:
    print("RecursionError")
class B:
    @property
    def x(self) -> int:
        return self._x
    @x.setter
    def x(self, v: int) -> None:
        self._x = v         # Right
b = B(); b.x = 1
print(b.x)
```

❌ Mistake 2: Giving the setter a different function name
✅ Correct: use the same name as the property

```python
class C:
    @property
    def v(self) -> int:
        return 1
    @v.setter
    def set_v(self, val: int) -> None:   # Wrong: creates a second property set_v
        pass
print(type(C.v).__name__, type(C.set_v).__name__)
try:
    C().v = 5                            # v still has no setter
except AttributeError as e:
    print("Error:", e)
```

❌ Mistake 3: Bypassing the setter in `__init__`
✅ Correct: assign through the public name so validation runs

```python
class D:
    def __init__(self, age: int) -> None:
        self._age = age       # Wrong: no validation
    @property
    def age(self) -> int:
        return self._age
    @age.setter
    def age(self, v: int) -> None:
        if v < 0:
            raise ValueError("negative")
        self._age = v
print(D(-5).age)              # -5 slipped through
class E(D):
    def __init__(self, age: int) -> None:
        self.age = age        # Right
try:
    E(-5)
except ValueError as e:
    print("Error:", e)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    def __init__(self):
        self._x = 0
    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, v):
        self._x = v * 2
a = A()
a.x = 5
a.x += 1
print(a.x)
a.__dict__["x"] = 777
print(a.x)
class B:
    @property
    def p(self): return 1
    @p.setter
    def q(self, v): pass
print(type(B.p).__name__, type(B.q).__name__, B.p is B.q)
```

Output:
```
22
22
property property False
```

Answer: `a.x = 5` runs the setter, so `_x` becomes 10. `a.x += 1` means read (10), add 1, then assign 11 through the setter, which doubles it to 22; printed `22`. Putting 777 in `__dict__` has no effect because the property is a data descriptor and wins, so it prints `22` again. In class `B`, `@p.setter` applied to a function named `q` creates a NEW property `q` (a copy of `p` with a setter), so both are `property` objects but different ones: `property property False`.

---

## ⚫ Interview Questions + Answers

Q1: How do you add validation to an attribute without changing callers?
A1: Rename storage to `_x`, add `@property` getter and `@x.setter` setter. Callers keep writing `obj.x = value`; the setter validates and stores.

Q2: What does `@x.setter` actually do?
A2: It calls `property.setter(func)`, which returns a new property object that copies the getter and adds your function as the setter. That is why all methods must share the same name: the last assignment to the name is the final combined property.

Q3: When does the deleter run?
A3: When code executes `del obj.x`. Use it for cleanup like closing a connection or removing a cache entry. It does not run on garbage collection; that is `__del__`.

Q4: Can you make an attribute write-once?
A4: Yes: in the setter check if `_x` already exists (`hasattr`) and raise `AttributeError` on a second assignment. Or use a frozen dataclass for fully immutable objects.

Q5: Property setters vs Pydantic validators?
A5: Setters validate mutable objects at assignment time. Pydantic validators run when data is parsed (request bodies, settings). Pydantic models can also validate on assignment with `validate_assignment=True`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Validate or clean values on assignment
- Keep two views of the same data in sync (celsius/fahrenheit)
- Release resources when an attribute is deleted
- Enforce invariants (rate limit between 1 and 1000)

❌ Avoid when:
- Simple attributes with no rules
- Heavy side effects in setters (network calls); use explicit methods
- When a frozen dataclass or Pydantic model fits better

---

## 📊 Visual Diagram
```
p.name            -> getter   -> return self._name
p.name = "x"      -> setter   -> validate -> self._name = clean("x")
del p.name        -> deleter  -> cleanup  -> del self._name

        +---------------- property "name" ----------------+
        | fget (getter) | fset (setter) | fdel (deleter)  |
        +-----------------------------------------------+
                         |
                  stored in self._name
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Getter | Runs when reading | पढ़ते समय चलता है |
| Setter | Runs when assigning | value डालते समय चलता है |
| Deleter | Runs on `del` | `del` पर चलता है |
| Validation | Checking data is allowed | Data सही है या नहीं जाँचना |
| Invariant | Rule that must always hold | हमेशा सही रहने वाला नियम |
| Encapsulation | Hide details behind an interface | Details छुपाकर interface देना |

---

## ⚡ 3-Line Summary
English: A property can have a getter, a setter and a deleter, all with the same name. The setter validates every assignment and stores in `_name`. Assign through the public name in `__init__` so validation also runs there.
Hindi: Property में getter, setter और deleter हो सकते हैं, तीनों का नाम एक ही होता है। Setter हर assignment validate करता है और `_name` में store करता है। `__init__` में public name से assign करें ताकि validation वहाँ भी चले।

---

## ➡️ Next Topic
**090. Inheritance — Complete Guide** — how a child class reuses and overrides a parent, `super()`, abstract classes and composition vs inheritance.
