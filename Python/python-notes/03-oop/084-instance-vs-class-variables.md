---

# 084. Instance vs Class Variables
# हिंदी में: Instance Variables बनाम Class Variables

---

## 🔵 Simple Definition (English)
An instance variable belongs to one object (set with `self.x = ...`). A class variable belongs to the class and is shared by every object. Python looks at the object first, then at its class.

## 🔵 सरल परिभाषा (Hindi)
Instance variable एक object का होता है (`self.x = ...` से set)। Class variable class का होता है और सभी objects में share होता है। Python पहले object में ढूँढता है, फिर उसकी class में।

---

## 🔴 Problem it Solves
Some data is different for each object (a user's name) and some data is the same for all (the app name, a tax rate, a counter of created objects). If you store shared data in every object, you waste memory and must update many places. If you store per-object data on the class, objects overwrite each other. Python needs both kinds, and you must know which one you are using.

## 🔴 यह क्यों बना? (Hindi)
कुछ data हर object का अलग होता है (user का name) और कुछ सबका एक जैसा (app का नाम, tax rate, बने objects की गिनती)। Shared data हर object में रखने से memory बर्बाद होती है और कई जगह update करना पड़ता है। Per-object data class पर रखने से objects एक-दूसरे को बदल देते हैं। Python में दोनों तरह के variables हैं और आपको पता होना चाहिए कि कौन सा use कर रहे हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Class body runs: `school = 'DPS'` is stored in `Student.__dict__`
Step 2 → `Student('Asha')` creates an object; `self.name = ...` goes into `obj.__dict__`
Step 3 → Reading `obj.school`: look in `obj.__dict__` first
Step 4 → Not found → look in the class (then parent classes) → found 'DPS'
Step 5 → Writing `obj.school = 'X'` NEVER changes the class; it creates a new instance variable (shadowing)
Step 6 → Writing `Student.school = 'X'` changes it for every object that has no own copy
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Class body चलती है: `school = 'DPS'` `Student.__dict__` में रखा जाता है
Step 2 → `Student('Asha')` object बनाता है; `self.name = ...` `obj.__dict__` में जाता है
Step 3 → `obj.school` पढ़ते समय पहले `obj.__dict__` में देखा जाता है
Step 4 → नहीं मिला → class (फिर parent classes) में देखा → 'DPS' मिला
Step 5 → `obj.school = 'X'` लिखने से class कभी नहीं बदलती; नया instance variable बनता है (shadowing)
Step 6 → `Student.school = 'X'` उन सभी objects के लिए बदल देता है जिनकी अपनी copy नहीं है
```

---

## 🟡 Real World Example
A Swiggy backend keeps `DELIVERY_FEE = 30` and `gst_rate = 0.05` as class variables because every order uses them, while `restaurant_id` and `items` are instance variables. A model registry keeps `registry = {}` on a base class so every subclass can register itself. A request counter on a class tracks how many objects were created.

## 🟡 Real Example Hindi mein
Swiggy backend में `DELIVERY_FEE = 30` और `gst_rate = 0.05` class variables होते हैं क्योंकि हर order यही use करती है, जबकि `restaurant_id` और `items` instance variables हैं। Model registry base class पर `registry = {}` रखती है ताकि हर subclass खुद को register कर सके। Class पर counter बताता है कि कितने objects बने।

---

## 💻 Code Example — Basic
```python
# Basic: class variable (shared) vs instance variable (per object)
class Student:                                    # a student class
    school: str = "DPS"                           # class variable: ONE copy for the class
    count: int = 0                                # counts how many students were created

    def __init__(self, name: str) -> None:        # per-object setup
        self.name: str = name                     # instance variable: each object has its own
        Student.count += 1                        # update the shared counter via the class name


s1: Student = Student("Asha")                     # create first student
s2: Student = Student("Raj")                      # create second student
print(s1.school, s2.school, Student.school)       # all read the same shared value
print(Student.count)                              # 2
Student.school = "KV"                             # change on the class -> everyone sees it
print(s1.school, s2.school)                       # KV KV
s1.school = "Private"                             # assignment on instance CREATES an instance var
print(s1.school, s2.school, Student.school)       # Private KV KV  (shadowing)
print("school" in s1.__dict__, "school" in s2.__dict__)   # True False
del s1.school                                     # remove the shadow
print(s1.school)                                  # back to the class value: KV
print(Student.__dict__["count"], s1.__dict__)     # where each one lives

# Output:
# DPS DPS DPS
# 2
# KV KV
# Private KV KV
# True False
# KV
# 2 {'name': 'Asha'}
```

## 💻 Code Example — Advanced
```python
# Advanced: shared mutable class variable bug, registry pattern, and safe counters
from __future__ import annotations
from itertools import count                       # thread-friendly id generator


class Team:                                       # BUGGY version
    members: list[str] = []                       # one list for every Team!

    def add(self, name: str) -> None:
        self.members.append(name)                 # mutates the shared list


a, b = Team(), Team()
a.add("Asha")
print("buggy:", b.members)                        # b sees Asha


class GoodTeam:                                   # FIXED version
    def __init__(self) -> None:
        self.members: list[str] = []              # new list per object

    def add(self, name: str) -> None:
        self.members.append(name)


c, d = GoodTeam(), GoodTeam()
c.add("Asha")
print("fixed:", d.members)


class Plugin:                                     # registry of subclasses using a class variable
    registry: dict[str, type[Plugin]] = {}        # shared on purpose
    _ids = count(1)                               # shared id generator

    def __init_subclass__(cls, **kw: object) -> None:   # runs when a subclass is defined
        super().__init_subclass__(**kw)
        Plugin.registry[cls.__name__.lower()] = cls     # auto-register

    def __init__(self) -> None:
        self.id: int = next(Plugin._ids)          # unique id per instance


class Email(Plugin): ...                          # auto registered
class Sms(Plugin): ...                            # auto registered


print(sorted(Plugin.registry))                    # ['email', 'sms']
print(Email().id, Sms().id, Email().id)           # 1 2 3


class Config:
    retries: int = 3                              # immutable class default

c1, c2 = Config(), Config()
c1.retries += 1                                   # reads 3 from class, writes 4 on the instance
print(c1.retries, c2.retries, Config.retries)     # 4 3 3

# Output:
# buggy: ['Asha']
# fixed: []
# ['email', 'sms']
# 1 2 3
# 4 3 3
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Per-object data | `self.x = ...` in `__init__` | `this.x = ...` in constructor |
| Shared data | variable in class body | `static x = ...` |
| Access shared | `Class.x` or `obj.x` | `Class.x` only |
| Write via object | creates a shadow copy | not possible (static is not on instance) |
| Inspect | `obj.__dict__`, `Class.__dict__` | `Object.keys(obj)` |

```python
# Python way
class Student:
    school: str = "DPS"                 # class variable
    def __init__(self, name: str) -> None:
        self.name: str = name           # instance variable

s = Student("Asha")
print(s.school, Student.school)         # both work
```
```javascript
// JavaScript way
class Student {
  static school = "DPS";                // static field
  constructor(name) { this.name = name; }
}
const s = new Student("Asha");
console.log(Student.school, s.school);  // DPS undefined
```

Key difference: in JavaScript a static field is not visible through an instance (`s.school` is `undefined`). In Python `obj.school` happily finds the class variable, and assigning to it silently makes a new instance variable. This is a classic source of bugs.

---

## 🟠 FastAPI Connection
A class variable on a service class lives once per worker process, which is useful for config and caches but dangerous for per-user data. With 4 uvicorn workers you get 4 separate copies, so counters kept in a class variable are not global across the whole app. Use Redis or a database for shared state.

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


class Stats:
    total_requests: int = 0                       # class variable = process wide counter


@app.middleware("http")
async def count_requests(request, call_next):     # runs for every request
    Stats.total_requests += 1                     # shared across all requests (per worker process!)
    return await call_next(request)


@app.get("/stats")
def stats() -> dict[str, int]:
    return {"total": Stats.total_requests}


c = TestClient(app)
c.get("/stats"); print(c.get("/stats").json())

# Output:
# {'total': 2}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a mutable class variable as per-object storage
✅ Correct: create the list in `__init__`

```python
class Team:
    members = []                 # Wrong: shared
a, b = Team(), Team()
a.members.append("Asha")
print(b.members)                 # ['Asha']

class Team2:
    def __init__(self) -> None:
        self.members: list[str] = []   # Right
x, y = Team2(), Team2()
x.members.append("Asha")
print(y.members)                 # []
```

❌ Mistake 2: Expecting `obj.count += 1` to update the class counter
✅ Correct: update through the class name

```python
class C:
    count = 0
    def hit_wrong(self) -> None:
        self.count += 1          # Wrong: creates instance variable
    def hit_right(self) -> None:
        C.count += 1             # Right: changes the class variable
a, b = C(), C()
a.hit_wrong(); a.hit_wrong()
print(C.count, a.count)          # 0 2
b.hit_right(); b.hit_right()
print(C.count, b.count)          # 2 2
```

❌ Mistake 3: Changing a class variable through an instance and expecting everyone to see it
✅ Correct: assign on the class

```python
class Cfg:
    debug = False
a, b = Cfg(), Cfg()
a.debug = True                   # Wrong: only a changes
print(b.debug)                   # False
Cfg.debug = True                 # Right: class-wide
print(b.debug)                   # True
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class C:
    x = 1
a, b = C(), C()
a.x += 1
C.x += 10
print(a.x, b.x, C.x)
b.y = 5
print(hasattr(C, "y"), C().__dict__)
```

Output:
```
2 11 11
False {}
```

Answer: `a.x += 1` reads 1 from the class and writes 2 onto `a` as an instance variable (shadowing). `C.x += 10` changes the class variable to 11. `a.x` is still 2, but `b` has no own `x`, so it sees 11. Output: `2 11 11`. Then `b.y = 5` creates an attribute only on `b`; the class has no `y` and a new `C()` has an empty `__dict__`, giving `False {}`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between class and instance variables?
A1: Instance variables are stored per object in `obj.__dict__`; class variables are stored once on the class and shared. Lookup checks the instance first, then the class and its parents.

Q2: What happens when you assign to a class variable through an instance?
A2: Python creates a new instance variable with the same name that hides the class variable for that object only. The class variable and other objects stay unchanged. Delete it with `del obj.x` to see the class value again.

Q3: Why are mutable class variables dangerous?
A3: Lists and dicts are mutated in place, so `obj.items.append(1)` changes the one shared list and all objects see it. No assignment happens, so no shadow is created. Use `__init__` for per-object containers.

Q4: How do you keep a count of created objects?
A4: Use a class variable and update it with the class name or `type(self)`: `Student.count += 1` inside `__init__`. In threaded code protect it with a lock or use `itertools.count()`.

Q5: Do subclasses share class variables with the parent?
A5: They read the parent's value until they define their own. Assigning `Child.x = 5` creates a separate variable on Child and the parent keeps its value. Mutating a shared list affects both.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Constants and config shared by all objects (rates, limits)
- Counters and registries on the class
- Default values that instances may override
- Caches shared at class level (with care)

❌ Avoid when:
- Per-object state such as name, balance or items
- Mutable containers meant for each object
- Data that must be shared across processes (use Redis/DB)

---

## 📊 Visual Diagram
```
Student.__dict__           s1.__dict__        s2.__dict__
+------------------+      +-------------+    +-------------+
| school = "DPS"   |      | name="Asha" |    | name="Raj"  |
| count  = 2       |      +-------------+    +-------------+
+------------------+            |                  |
        ^                       | lookup order     |
        +---- 2. class ---------+---- 1. object ---+

s1.school -> not in s1.__dict__ -> found in Student -> "DPS"
s1.school = "X" -> adds school to s1.__dict__ only (shadow)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Instance variable | Data owned by one object | एक object का अपना data |
| Class variable | Data shared by all objects | सभी objects का shared data |
| Shadowing | Instance attribute hides class one | Instance attribute का class वाले को छुपा देना |
| `__dict__` | Dictionary of attributes | Attributes का dictionary |
| Lookup order | Instance, then class, then parents | पहले object, फिर class, फिर parents |
| Registry | Shared dict of items on a class | Class पर shared सूची |

---

## ⚡ 3-Line Summary
English: Instance variables belong to one object; class variables are shared by the class. Reading checks the object first, then the class. Writing through an object creates a shadow, never a change in the class.
Hindi: Instance variables एक object के होते हैं; class variables class के होते हैं और share होते हैं। पढ़ते समय पहले object, फिर class देखी जाती है। Object से लिखने पर shadow बनता है, class नहीं बदलती।

---

## ➡️ Next Topic
**085. Instance Methods** — the normal methods that work on one object's data through `self`, including method chaining.
