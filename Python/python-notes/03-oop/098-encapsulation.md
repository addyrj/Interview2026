---

# 098. Encapsulation
# हिंदी में: Encapsulation (Data को Class के अंदर सुरक्षित रखना)

---

## 🔵 Simple Definition (English)
Encapsulation means bundling data and the methods that work on it inside one class, and controlling how outside code touches that data. Python uses naming conventions (`_name`, `__name`) and `@property` instead of strict `private` keywords.

## 🔵 सरल परिभाषा (Hindi)
Encapsulation का मतलब है data और उस पर काम करने वाले methods को एक class में बांधना, और बाहर का code उस data को कैसे छुए यह नियंत्रित करना। Python में सख्त `private` keyword नहीं है; naming conventions (`_name`, `__name`) और `@property` इस्तेमाल होते हैं।

---

## 🔴 Problem it Solves
If `account.balance = -5000` is allowed from anywhere, no rule can be guaranteed: any module can break your data. Encapsulation puts the rules in one place (`withdraw()` checks the balance), so invariants hold. It also lets you change the internal storage later (cents instead of rupees) without breaking callers.

## 🔴 यह क्यों बना? (Hindi)
अगर कहीं से भी `account.balance = -5000` हो सकता है तो कोई rule guaranteed नहीं: कोई भी module आपका data तोड़ सकता है। Encapsulation नियम एक जगह रखता है (`withdraw()` balance check करता है), इसलिए invariants बने रहते हैं। बाद में internal storage बदलना (rupees की जगह paise) भी callers को तोड़े बिना हो जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → name        public: anyone may use it
Step 2 → _name       "protected" by convention: internal, please do not touch
Step 3 → __name      name mangling: Python renames it to _ClassName__name
Step 4 → @property   a method that looks like an attribute; add validation in the setter
Step 5 → Nothing is truly private: obj._Class__name still works (convention, not security)
Step 6 → Outside code uses the public API (methods/properties), never the raw fields
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → name        public: कोई भी इस्तेमाल कर सकता है
Step 2 → _name       convention से "protected": internal है, कृपया न छुएं
Step 3 → __name      name mangling: Python इसे _ClassName__name नाम दे देता है
Step 4 → @property   attribute जैसा दिखने वाला method; setter में validation जोड़ें
Step 5 → कुछ भी सच में private नहीं: obj._Class__name फिर भी चलता है (convention, security नहीं)
Step 6 → बाहर का code public API (methods/properties) इस्तेमाल करे, raw fields नहीं
```

---

## 🟡 Real World Example
A wallet in a Paytm-like app: the balance is kept in paise inside `_balance_paise`. Outside code can only call `deposit()`, `withdraw()` and read `balance`. The check "no overdraft" lives in one method. A `User` model hides `_password_hash` and exposes only `check_password()`, so the hash never leaks in logs or API responses.

## 🟡 Real Example Hindi mein
Paytm जैसे app में wallet: balance paise में `_balance_paise` के अंदर रहता है। बाहर का code सिर्फ `deposit()`, `withdraw()` call कर सकता है और `balance` पढ़ सकता है। "overdraft नहीं" वाला check एक ही method में है। `User` model `_password_hash` छुपाता है और सिर्फ `check_password()` देता है, ताकि hash logs या API responses में leak न हो।

---

## 💻 Code Example — Basic
```python
# Basic encapsulation example
class Account:                                      # a simple bank account
    def __init__(self, owner: str, balance: int) -> None:    # constructor
        self.owner: str = owner                     # public attribute
        self._balance: int = balance                # protected by convention
        self.__pin: str = "1234"                    # name-mangled attribute

    @property                                       # read access looks like an attribute
    def balance(self) -> int:
        return self._balance                        # return the hidden value

    def withdraw(self, amount: int) -> None:        # the only way to reduce balance
        if amount > self._balance:                  # rule: no overdraft
            raise ValueError("Insufficient funds")  # protect the invariant
        self._balance -= amount                     # safe update


a: Account = Account("Asha", 1000)                  # create account
a.withdraw(300)                                     # use the public method
print(a.balance)                                    # read through the property
try:                                                # property has no setter
    a.balance = 99999                               # cheating attempt
except AttributeError as e:                         # blocked
    print("Error:", e)
print(hasattr(a, "__pin"))                          # False: the real name was mangled
print(a._Account__pin)                              # works, but never do this in real code
print([n for n in vars(a)])                         # the actual stored names

# Output:
# 700
# Error: property 'balance' of 'Account' object has no setter
# False
# 1234
# ['owner', '_balance', '_Account__pin']
```

## 💻 Code Example — Advanced
```python
# Production style: validated property, read-only fields, __slots__, no secret leaks
from dataclasses import dataclass               # for the immutable value object


@dataclass(frozen=True)                         # immutable: fields cannot be reassigned
class Money:
    paise: int                                  # store integers, never floats

    def __post_init__(self) -> None:            # validate after creation
        if self.paise < 0:                      # no negative money in this domain
            raise ValueError("Money cannot be negative")

    @property
    def rupees(self) -> float:                  # derived, read-only view
        return self.paise / 100


class Wallet:
    __slots__ = ("_balance", "_history", "_password_hash")   # block random new attributes

    def __init__(self, password: str) -> None:
        self._balance: int = 0                  # paise, internal
        self._history: list[str] = []           # audit trail, internal
        self._password_hash: int = hash(password)    # demo only: use bcrypt/argon2 for real

    @property
    def balance(self) -> Money:                 # return an immutable copy, not the field
        return Money(self._balance)

    @balance.setter                             # controlled write access
    def balance(self, value: Money) -> None:
        raise AttributeError("use deposit()/withdraw()")    # force the public API

    def deposit(self, amount: Money) -> None:
        self._balance += amount.paise           # update internal state
        self._history.append(f"+{amount.paise}")    # record it

    def withdraw(self, amount: Money) -> None:
        if amount.paise > self._balance:        # enforce the invariant
            raise ValueError("Insufficient funds")
        self._balance -= amount.paise           # update
        self._history.append(f"-{amount.paise}")    # record it

    @property
    def history(self) -> tuple[str, ...]:       # expose a read-only copy
        return tuple(self._history)             # callers cannot mutate our list

    def check_password(self, password: str) -> bool:
        return hash(password) == self._password_hash    # compare without revealing the hash

    def __repr__(self) -> str:                  # safe debug output (no secrets)
        return f"Wallet(balance={self._balance})"


w: Wallet = Wallet("secret")                    # create
w.deposit(Money(50000))                         # +500 rupees
w.withdraw(Money(12000))                        # -120 rupees
print(w.balance.rupees, w.history)              # public API only
print(w, w.check_password("secret"))            # no hash in repr
for bad in (lambda: w.withdraw(Money(10 ** 9)),            # overdraft
            lambda: setattr(w, "balance", Money(1)),       # direct assignment
            lambda: setattr(w, "extra", 1),                # new attribute (slots)
            lambda: Money(-1)):                            # invalid money
    try:
        bad()                                   # run the bad action
    except (ValueError, AttributeError) as e:   # each is rejected
        print(type(e).__name__, "-", e)

# Output:
# 380.0 ('+50000', '-12000')
# Wallet(balance=38000) True
# ValueError - Insufficient funds
# AttributeError - use deposit()/withdraw()
# AttributeError - 'Wallet' object has no attribute 'extra' and no __dict__ for setting new attributes
# ValueError - Money cannot be negative
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Truly private | No (convention) | Yes: `#field` |
| Protected | `_name` convention | `_name` convention |
| Name mangling | `__name` -> `_Class__name` | none |
| Getter/setter | `@property` / `@x.setter` | `get x()` / `set x(v)` |
| Freeze object | `@dataclass(frozen=True)` | `Object.freeze()` |

```python
# Python way
class Counter:
    def __init__(self) -> None:
        self._n: int = 0            # internal by convention

    @property
    def n(self) -> int:             # read-only access
        return self._n

    def inc(self) -> None:
        self._n += 1

c = Counter(); c.inc()
print(c.n)                          # 1
```
```javascript
// JavaScript way
class Counter {
  #n = 0;                           // truly private (language enforced)
  get n() { return this.#n; }       // getter
  inc() { this.#n += 1; }
}
const c = new Counter(); c.inc();
console.log(c.n);                   // 1
// console.log(c.#n);  // SyntaxError - cannot access outside the class
```

Key difference: JavaScript `#private` fields are enforced by the language. Python trusts developers ("we are all consenting adults"): `_x` is a request, `__x` only renames. Security never comes from private attributes in Python.

---

## 🟠 FastAPI Connection
Encapsulation shows up as response models: your ORM object has `password_hash`, but the API must not return it. `response_model` exposes only the public fields, which is encapsulation at the API boundary.

```python
# FastAPI example — hide internal fields with response_model
from fastapi import FastAPI                     # app
from fastapi.testclient import TestClient       # test client
from pydantic import BaseModel                  # schemas


class UserDB(BaseModel):                        # internal shape (has a secret)
    id: int
    email: str
    password_hash: str


class UserPublic(BaseModel):                    # public shape (no secret)
    id: int
    email: str


app: FastAPI = FastAPI()                        # create app


@app.get("/users/{uid}", response_model=UserPublic)    # filters the output
def get_user(uid: int) -> UserDB:
    return UserDB(id=uid, email="a@b.com", password_hash="x$secret")   # returns EVERYTHING


client: TestClient = TestClient(app)            # test client
print(client.get("/users/1").json())            # password_hash is filtered out

# Output:
# {'id': 1, 'email': 'a@b.com'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Treating `__name` as real security
✅ Correct: it only prevents accidental clashes in subclasses; protect secrets by not storing/logging them

```python
class Vault:
    def __init__(self) -> None:
        self.__key = "s3cret"

v = Vault()
# Wrong: assuming nobody can read it
print(v._Vault__key)                 # s3cret  (readable!)
# Right: keep real secrets in environment variables / secret managers
```

❌ Mistake 2: Writing Java-style getters/setters for everything
✅ Correct: start with a plain public attribute; switch to `@property` later when you need validation (callers do not change)

```python
class Wrong:
    def __init__(self) -> None:
        self._age = 0
    def get_age(self) -> int:        # Java style, noisy
        return self._age
    def set_age(self, v: int) -> None:
        self._age = v

class Right:
    def __init__(self) -> None:
        self.age = 0                 # plain attribute

r = Right(); r.age = 5
print(r.age)                         # 5
```

❌ Mistake 3: Returning the internal mutable list directly
✅ Correct: return a copy or a tuple

```python
class Cart:
    def __init__(self) -> None:
        self._items: list[str] = ["pen"]

    def items_wrong(self) -> list[str]:
        return self._items            # caller can change internal state

    def items_right(self) -> tuple[str, ...]:
        return tuple(self._items)     # safe copy

c = Cart()
c.items_wrong().append("hack")
print(c.items_right())                # ('pen', 'hack')  <- the wrong version leaked
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    def __init__(self) -> None:
        self.__x = 1

class B(A):
    def __init__(self) -> None:
        super().__init__()
        self.__x = 2

b = B()
print(b._A__x, b._B__x)
print(hasattr(b, "__x"))
```
Answer: `1 2` then `False`. Name mangling gives each class its own attribute: `A` stores `_A__x` and `B` stores `_B__x`, so they do not overwrite each other. A plain `__x` name does not exist on the object, so `hasattr` is `False`. This is the real purpose of double underscores: avoiding accidental clashes in subclasses.

---

## ⚫ Interview Questions + Answers

Q1: Does Python have private variables?
A1: No true private. `_x` is a convention for internal use; `__x` triggers name mangling to `_Class__x`. Both can still be accessed. Python's philosophy is trust, not enforcement.

Q2: What is the difference between `_x` and `__x`?
A2: `_x` is just a hint ("internal"), and `from module import *` skips such names. `__x` is rewritten to `_ClassName__x` to avoid clashes in subclasses.

Q3: Why use `@property`?
A3: It gives attribute-style access with method logic: validation, computed values, read-only fields. You can start with a plain attribute and upgrade later without changing callers.

Q4: How do you make a read-only attribute?
A4: Define a `@property` without a setter, or use `@dataclass(frozen=True)`, or `__slots__` plus properties. Assigning then raises `AttributeError` (or `FrozenInstanceError` for frozen dataclasses).

Q5: What does `__slots__` do for encapsulation?
A5: It fixes the allowed attribute names and removes `__dict__`, so typos like `w.balence = 5` raise `AttributeError` instead of silently creating a new attribute. It also saves memory.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A field has rules (no negative balance, valid email)
- You may change internal storage later
- Hiding secrets from repr/logs/API output

❌ Avoid when:
- Simple data containers (use a dataclass with public fields)
- You are writing getters/setters that do nothing extra
- You think underscores give security (they do not)

---

## 📊 Visual Diagram
```
 outside code                     class Wallet
 -----------                      +--------------------------------+
 w.deposit(100)  ---public API--> | deposit()  withdraw()  balance |
 w.balance       ---property----> |   (rules and validation here)  |
                                  |                                |
 w._balance      --X convention-- | _balance   _history  (hidden)  |
 w.__x           --X mangled----- | _Wallet__x                     |
                                  +--------------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Encapsulation | Bundle data + methods, control access | Data और methods को बांधकर access नियंत्रित करना |
| Name mangling | `__x` becomes `_Class__x` | `__x` का `_Class__x` बन जाना |
| Property | Method used like an attribute | Attribute की तरह इस्तेमाल होने वाला method |
| Invariant | Rule that must always be true | हमेशा सच रहने वाला नियम |
| `__slots__` | Fixed attribute list, no `__dict__` | तय attributes की सूची |
| Immutable | Cannot be changed after creation | बनने के बाद न बदलने वाला |

---

## ⚡ 3-Line Summary
English: Encapsulation keeps data behind a clear public API so rules (invariants) always hold. Python uses `_x`, `__x` and `@property`; nothing is truly private. Use properties for validation and return copies of mutable internals.
Hindi: Encapsulation data को साफ public API के पीछे रखता है ताकि नियम (invariants) हमेशा बने रहें। Python में `_x`, `__x` और `@property` इस्तेमाल होते हैं; कुछ भी सच में private नहीं। Validation के लिए properties और mutable internals की copy लौटाएं।

---

## ➡️ Next Topic
**099. Polymorphism** — one interface, many behaviors: the same method call does different things depending on the object.
