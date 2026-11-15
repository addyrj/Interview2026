---

# 086. Class Methods (@classmethod)
# हिंदी में: Class Methods (@classmethod)

---

## 🔵 Simple Definition (English)
A class method is marked with `@classmethod` and receives the class (usually named `cls`) as its first argument instead of the object. It is used for work that belongs to the whole class, most often for alternate constructors like `from_dict`.

## 🔵 सरल परिभाषा (Hindi)
Class method पर `@classmethod` लगता है और उसे पहले argument में object की जगह class (आमतौर पर `cls`) मिलती है। यह पूरी class से जुड़े काम के लिए होता है, खासकर `from_dict` जैसे alternate constructors के लिए।

---

## 🔴 Problem it Solves
A class has only one `__init__`, but data arrives in many shapes: a JSON string, a dict, environment variables, a database row. Stuffing all of that into `__init__` makes it messy. A class method lets you add named constructors (`Settings.from_env()`), and because it receives `cls`, it creates the right type even for subclasses.

## 🔴 यह क्यों बना? (Hindi)
Class में सिर्फ एक `__init__` होता है, लेकिन data कई रूपों में आता है: JSON string, dict, environment variables, database row। सब कुछ `__init__` में डालना messy है। Class method से named constructors (`Settings.from_env()`) जोड़े जा सकते हैं और `cls` मिलने की वजह से subclass के लिए भी सही type का object बनता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `@classmethod` wraps the function in a classmethod descriptor
Step 2 → You call `Pizza.margherita()` or `obj.margherita()`
Step 3 → Python binds the CLASS (not the object) as the first argument
Step 4 → For `SpicyPizza.margherita()`, `cls` is `SpicyPizza`
Step 5 → Inside, `cls(...)` calls the constructor of that exact class
Step 6 → The new object is returned, correctly typed for the subclass
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `@classmethod` function को classmethod descriptor में लपेटता है
Step 2 → आप `Pizza.margherita()` या `obj.margherita()` call करते हैं
Step 3 → Python पहले argument में CLASS (object नहीं) bind करता है
Step 4 → `SpicyPizza.margherita()` में `cls` = `SpicyPizza`
Step 5 → अंदर `cls(...)` उसी class का constructor चलाता है
Step 6 → नया object return होता है, subclass के लिए सही type का
```

---

## 🟡 Real World Example
Config loading: `Settings.from_env()`, `Settings.from_json(path)`. API layer: `UserOut.from_row(row)` converts a DB row to a response model. Pydantic's own `model_validate` is a class method. Counters per model: each subclass keeps its own instance count through `cls`.

## 🟡 Real Example Hindi mein
Config loading: `Settings.from_env()`, `Settings.from_json(path)`. API layer: `UserOut.from_row(row)` DB row को response model में बदलता है। Pydantic का `model_validate` भी class method है। हर subclass अपनी गिनती `cls` से रखती है।

---

## 💻 Code Example — Basic
```python
# Basic: @classmethod receives the class (cls), not the object
class Pizza:                                      # pizza with toppings
    def __init__(self, toppings: list[str]) -> None:
        self.toppings: list[str] = toppings       # list of toppings

    @classmethod                                  # decorator: first arg is the class
    def margherita(cls) -> "Pizza":               # alternate constructor
        return cls(["mozzarella", "tomato"])      # cls(...) == Pizza(...)

    @classmethod
    def from_string(cls, s: str) -> "Pizza":      # parse "a,b,c"
        return cls([t.strip() for t in s.split(",")])

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.toppings})"


class SpicyPizza(Pizza):                          # subclass
    pass


print(Pizza.margherita())                         # Pizza([...])
print(Pizza.from_string("corn, olives"))          # parsed
print(SpicyPizza.margherita())                    # cls is SpicyPizza here -> correct type!
print(Pizza.margherita().margherita())            # also callable via instance
print(type(Pizza.margherita), Pizza.margherita.__self__ is Pizza)   # bound to the class

# Output:
# Pizza(['mozzarella', 'tomato'])
# Pizza(['corn', 'olives'])
# SpicyPizza(['mozzarella', 'tomato'])
# Pizza(['mozzarella', 'tomato'])
# <class 'method'> True
```

## 💻 Code Example — Advanced
```python
# Advanced: factories, config from env, and a counter that respects subclasses
from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Self


@dataclass
class Settings:                                   # app settings with several constructors
    db_url: str
    debug: bool = False

    @classmethod
    def from_env(cls, env: dict[str, str]) -> Self:           # 12-factor style
        return cls(env["DB_URL"], env.get("DEBUG", "0") == "1")

    @classmethod
    def from_json(cls, raw: str) -> Self:                     # from a JSON string
        try:
            return cls(**json.loads(raw))
        except (json.JSONDecodeError, TypeError) as e:        # bad JSON or bad keys
            raise ValueError(f"bad settings: {e}") from e


print(Settings.from_env({"DB_URL": "sqlite://", "DEBUG": "1"}))
print(Settings.from_json('{"db_url": "pg://x"}'))
try:
    Settings.from_json('{"nope": 1}')
except ValueError as e:
    print("Error:", e)


class Model:                                      # per-subclass state via cls
    _instances: int = 0

    def __init__(self) -> None:
        type(self)._instances += 1                # increments the SUBCLASS counter
    @classmethod
    def instances(cls) -> int:
        return cls._instances


class User(Model): ...
class Post(Model): ...


User(); User(); Post()
print(User.instances(), Post.instances(), Model.instances())   # 2 1 0


class Temp:
    def __init__(self, c: float) -> None:
        self.c = c

    @classmethod
    def from_f(cls, f: float) -> Self:
        return cls(round((f - 32) * 5 / 9, 2))


print(Temp.from_f(212).c)

# Output:
# Settings(db_url='sqlite://', debug=True)
# Settings(db_url='pg://x', debug=False)
# Error: bad settings: Settings.__init__() got an unexpected keyword argument 'nope'
# 2 1 0
# 100.0
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Syntax | `@classmethod def f(cls)` | `static f() {}` |
| Gets the class | `cls` argument | `this` inside static method |
| Alternate constructor | `cls(...)` | `new this(...)` |
| Inherited by subclass | yes, `cls` is the subclass | yes, `this` is the subclass |
| Called on instance | works | not possible |

```python
# Python way
class Pizza:
    def __init__(self, toppings: list[str]) -> None:
        self.toppings = toppings
    @classmethod
    def margherita(cls) -> "Pizza":
        return cls(["mozzarella", "tomato"])   # cls works for subclasses too

print(Pizza.margherita().toppings)
```
```javascript
// JavaScript way
class Pizza {
  constructor(toppings) { this.toppings = toppings; }
  static margherita() {
    return new this(["mozzarella", "tomato"]); // `this` = the class
  }
}
console.log(Pizza.margherita().toppings);
```

Key difference: Python class methods are the equivalent of JS `static` methods that use `this`. Python also has a separate `@staticmethod` for functions that need neither the class nor an object (JS `static` covers both).

---

## 🟠 FastAPI Connection
Pydantic and SQLAlchemy lean on class methods: `Model.model_validate(data)`, `Model.model_validate_json(raw)`, and your own `from_row` or `from_orm_obj` helpers keep conversion code inside the model so routes stay clean.

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel


class UserOut(BaseModel):
    id: int
    name: str

    @classmethod
    def from_row(cls, row: tuple[int, str]) -> "UserOut":     # build API model from a DB row
        return cls(id=row[0], name=row[1])


app = FastAPI()


@app.get("/users/1", response_model=UserOut)
def get_user() -> UserOut:
    return UserOut.from_row((1, "Asha"))


print(TestClient(app).get("/users/1").json())
# pydantic's own constructors are classmethods too:
print(UserOut.model_validate({"id": 2, "name": "Raj"}))

# Output:
# {'id': 1, 'name': 'Asha'}
# id=2 name='Raj'
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Hard-coding the class name inside a factory
✅ Correct: return `cls(...)` so subclasses work

```python
class A:
    @classmethod
    def make_wrong(cls):
        return A()                  # Wrong: always A
    @classmethod
    def make_right(cls):
        return cls()                # Right
class B(A): ...
print(type(B.make_wrong()).__name__, type(B.make_right()).__name__)
```

❌ Mistake 2: Forgetting the decorator
✅ Correct: add `@classmethod`

```python
class C:
    def make(cls):                  # Wrong: cls is actually the instance
        return cls
c = C()
print(c.make() is c)                # True, so it is not the class!

class D:
    @classmethod
    def make(cls):                  # Right
        return cls
print(D().make() is D)              # True
```

❌ Mistake 3: Using a class method when an instance is needed
✅ Correct: use an instance method

```python
class Acc:
    def __init__(self) -> None:
        self.balance = 0
    @classmethod
    def deposit(cls, n: int) -> None:
        try:
            cls.balance += n        # Wrong: no balance on the class
        except AttributeError as e:
            print("Error:", e)
Acc.deposit(5)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    name = "A"
    @classmethod
    def make(cls):
        return cls.name
class B(A):
    name = "B"
print(A.make(), B.make(), B().make())
A.make = lambda: "new"
print(A.make())
```

Output:
```
A B B
new
```

Answer: `cls` is the class used for the call, so `A.make()` reads `A.name` = `A`, and both `B.make()` and `B().make()` read `B.name` = `B`; output `A B B`. Then `A.make = lambda: 'new'` replaces the class method on the class itself with a plain function (not bound), so `A.make()` returns `new` with no arguments needed.

---

## ⚫ Interview Questions + Answers

Q1: What is a class method and when do you use it?
A1: A method that receives the class as `cls`. Use it for alternate constructors (`from_json`, `from_env`), factory logic and operations on class-level data.

Q2: Difference between instance, class and static methods?
A2: Instance methods get `self` and use object data. Class methods get `cls` and use class data or build objects. Static methods get nothing and are plain functions placed in the class for organisation.

Q3: Why use `cls(...)` instead of the class name?
A3: Subclasses calling the factory then get an object of their own type, and renaming the class does not break the code. It follows the open-closed principle.

Q4: Can a class method be called on an instance?
A4: Yes. `obj.method()` still binds the class (`type(obj)`), not the object. It is rarely done because it confuses readers.

Q5: How does Python implement `@classmethod`?
A5: It is a descriptor. Accessing `Class.m` calls `classmethod.__get__`, which returns a bound method whose `__self__` is the class. You can check `Class.m.__self__ is Class`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Alternate constructors (from_dict, from_env, from_row)
- Factory methods that must respect subclasses
- Operations on class-level data (registries, counters)
- Parsing or validating before creating an object

❌ Avoid when:
- Logic that needs an object's own data; use an instance method
- A pure helper that needs neither the class nor an object; use staticmethod or a function
- Complex construction with many steps; consider a builder or factory function

---

## 📊 Visual Diagram
```
class Pizza:
    @classmethod margherita(cls)

Pizza.margherita()        -> cls = Pizza      -> Pizza(...)
SpicyPizza.margherita()   -> cls = SpicyPizza -> SpicyPizza(...)
SpicyPizza().margherita() -> cls = SpicyPizza (type of the object)

 JSON string ----\
 dict ------------+--> from_xxx(cls, data) --> cls(...) --> object
 DB row ---------/
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Class method | Method receiving the class | Class पाने वाला method |
| cls | The class itself | Class खुद |
| Alternate constructor | Extra way to build objects | Object बनाने का अतिरिक्त तरीका |
| Factory | Code that creates objects | Objects बनाने वाला code |
| Decorator | Wrapper written with @ | @ से लगने वाला wrapper |
| Descriptor | Controls attribute binding | Attribute binding चलाने वाला object |

---

## ⚡ 3-Line Summary
English: `@classmethod` gives the method the class as `cls`. Its main job is alternate constructors that also work for subclasses. Always return `cls(...)`, never a hard-coded class name.
Hindi: `@classmethod` method को `cls` के रूप में class देता है। इसका मुख्य काम alternate constructors है जो subclasses के साथ भी चलें। हमेशा `cls(...)` return करें, class का नाम hard-code न करें।

---

## ➡️ Next Topic
**087. Static Methods (`@staticmethod`)** — plain functions grouped inside a class when they need neither the object nor the class.
