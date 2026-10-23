---

# 081. OOP Introduction — Complete Guide
# हिंदी में: OOP Introduction — पूरी Guide

---

## 🔵 Simple Definition (English)
Object-Oriented Programming (OOP) organizes code around **objects** — bundles of data (attributes) and behavior (methods). Python supports 4 OOP pillars: **Encapsulation** (hide internal state), **Inheritance** (reuse code), **Polymorphism** (same interface, different behavior), **Abstraction** (hide complexity). In Python, everything is an object — numbers, strings, functions, classes.

## 🔵 सरल परिभाषा (Hindi)
OOP code को **objects** के around organize करता है — data (attributes) + behavior (methods) का bundle। Python के 4 OOP pillars: **Encapsulation** (internal state hide), **Inheritance** (code reuse), **Polymorphism** (same interface, different behavior), **Abstraction** (complexity hide)। Python में सब कुछ object है।

---

## 💻 Code Example — Basic
```python
# ─── Class and Object ─────────────────────────────────────────────
class BankAccount:
    """A bank account with basic operations."""
    
    # Class attribute — shared by ALL instances:
    bank_name = "Python Bank"
    interest_rate = 0.05
    
    # Constructor:
    def __init__(self, owner: str, balance: float = 0.0):
        # Instance attributes — unique to each instance:
        self.owner = owner
        self._balance = balance    # _ prefix = "private by convention"
    
    # Instance method — has access to self:
    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount
        print(f"Deposited ${amount:.2f}. New balance: ${self._balance:.2f}")
    
    def withdraw(self, amount: float) -> None:
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount
        print(f"Withdrew ${amount:.2f}. New balance: ${self._balance:.2f}")
    
    def get_balance(self) -> float:
        return self._balance
    
    # @property — access like attribute, not method:
    @property
    def balance(self) -> float:
        return self._balance
    
    # @classmethod — has access to class (not instance):
    @classmethod
    def create_savings(cls, owner: str, initial: float = 100.0) -> "BankAccount":
        """Factory method — alternative constructor."""
        account = cls(owner, initial)
        print(f"Savings account created for {owner}")
        return account
    
    # @staticmethod — no access to class or instance:
    @staticmethod
    def validate_amount(amount: float) -> bool:
        return amount > 0 and isinstance(amount, (int, float))
    
    # __repr__ — for debugging:
    def __repr__(self) -> str:
        return f"BankAccount(owner={self.owner!r}, balance={self._balance:.2f})"
    
    # __str__ — for display:
    def __str__(self) -> str:
        return f"{self.owner}'s account (${self._balance:.2f})"

# ─── Creating objects ─────────────────────────────────────────────
account1 = BankAccount("Priya", 1000.0)
account2 = BankAccount.create_savings("Raj")   # using classmethod

account1.deposit(500)
account1.withdraw(200)
print(account1.balance)    # using @property
print(repr(account1))      # __repr__
print(str(account1))       # __str__

# Class attribute access:
print(BankAccount.bank_name)   # "Python Bank"
print(account1.bank_name)      # also works — searches instance then class
```

## 💻 Code Example — Advanced (Inheritance + Polymorphism)
```python
from abc import ABC, abstractmethod

# ─── Abstraction — Abstract Base Class ───────────────────────────
class PaymentProcessor(ABC):
    """Abstract base class — cannot be instantiated directly."""
    
    @abstractmethod
    async def process_payment(self, amount: float, currency: str) -> dict:
        """Subclasses MUST implement this."""
        ...
    
    @abstractmethod
    async def refund(self, transaction_id: str, amount: float) -> dict:
        ...
    
    # Non-abstract method — inherited as-is:
    def validate(self, amount: float) -> bool:
        return amount > 0

# ─── Inheritance + Polymorphism ────────────────────────────────────
class StripeProcessor(PaymentProcessor):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def process_payment(self, amount: float, currency: str) -> dict:
        # Stripe-specific implementation:
        return {
            "processor": "stripe",
            "amount": amount,
            "currency": currency,
            "status": "success",
            "transaction_id": "txn_stripe_123",
        }
    
    async def refund(self, transaction_id: str, amount: float) -> dict:
        return {"refund_id": f"ref_{transaction_id}", "amount": amount}

class RazorpayProcessor(PaymentProcessor):
    def __init__(self, key_id: str, key_secret: str):
        self.key_id = key_id
        self.key_secret = key_secret
    
    async def process_payment(self, amount: float, currency: str) -> dict:
        # Razorpay-specific implementation:
        return {
            "processor": "razorpay",
            "amount": amount * 100,   # Razorpay uses paise (not rupees)
            "currency": currency,
            "status": "captured",
            "payment_id": "pay_razorpay_456",
        }
    
    async def refund(self, transaction_id: str, amount: float) -> dict:
        return {"refund_id": f"rfnd_{transaction_id}", "amount": amount * 100}

# Polymorphism — same interface, different behavior:
async def checkout(processor: PaymentProcessor, amount: float) -> dict:
    """Works with ANY PaymentProcessor — doesn't care which one."""
    if not processor.validate(amount):
        raise ValueError("Invalid amount")
    return await processor.process_payment(amount, "USD")

# Works with Stripe:
stripe = StripeProcessor("sk_test_...")
result = await checkout(stripe, 99.99)

# Works with Razorpay:
razorpay = RazorpayProcessor("rzp_key", "rzp_secret")
result = await checkout(razorpay, 999.99)

# ─── isinstance and issubclass ────────────────────────────────────
print(isinstance(stripe, StripeProcessor))    # True
print(isinstance(stripe, PaymentProcessor))   # True (parent class too!)
print(issubclass(StripeProcessor, PaymentProcessor))  # True

# ─── Multiple inheritance (MRO) ──────────────────────────────────
class Loggable:
    def log(self, message: str) -> None:
        print(f"[{self.__class__.__name__}] {message}")

class Cacheable:
    _cache: dict = {}
    
    def cache_key(self) -> str:
        return f"{self.__class__.__name__}_{id(self)}"

class SmartStripeProcessor(StripeProcessor, Loggable, Cacheable):
    """Multiple inheritance — MRO: SmartStripe → Stripe → PaymentProcessor → Loggable → Cacheable"""
    
    async def process_payment(self, amount: float, currency: str) -> dict:
        self.log(f"Processing ${amount} via Stripe")
        result = await super().process_payment(amount, currency)  # calls StripeProcessor
        self.log(f"Success: {result['transaction_id']}")
        return result

# Check MRO:
print(SmartStripeProcessor.__mro__)
# (SmartStripeProcessor, StripeProcessor, PaymentProcessor, Loggable, Cacheable, object)
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python class:
class Animal:
    def __init__(self, name: str):
        self.name = name
    
    def speak(self) -> str:
        raise NotImplementedError

class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} says Woof!"

dog = Dog("Rex")
print(dog.speak())   # "Rex says Woof!"
print(isinstance(dog, Animal))  # True
```

```javascript
// JavaScript class:
class Animal {
    constructor(name) {
        this.name = name;
    }
    
    speak() {
        throw new Error("Not implemented");
    }
}

class Dog extends Animal {
    speak() {
        return `${this.name} says Woof!`;
    }
}

const dog = new Dog("Rex");
console.log(dog.speak());       // "Rex says Woof!"
console.log(dog instanceof Animal); // true
```

Key differences:
- Python uses `self` (explicit). JS uses `this` (implicit, can change with `bind()`).
- Python `__init__`. JS `constructor`.
- Python `super().__init__()`. JS `super()`.
- Python has multiple inheritance. JS doesn't (single prototype chain).
- Python has `@classmethod`, `@staticmethod`. JS has `static` keyword.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `self` parameter
```python
# Wrong — missing self in method:
class Counter:
    def increment():    # TypeError: takes 0 args, 1 given
        self.count += 1

# Correct:
class Counter:
    def __init__(self):
        self.count = 0
    def increment(self):   # self is always first!
        self.count += 1
```

❌ Mistake 2: Mutable class attribute shared across instances
```python
# Wrong — list is shared! Adding to one instance affects all:
class Student:
    grades = []   # CLASS attribute — one list for ALL students!
    
    def add_grade(self, grade):
        self.grades.append(grade)   # modifies shared list!

s1 = Student(); s1.add_grade(90)
s2 = Student()
print(s2.grades)   # [90] ← surprise!

# Correct — create in __init__:
class Student:
    def __init__(self):
        self.grades = []   # INSTANCE attribute — unique per student
```

---

## 🧠 Tricky Interview Question

**Q**: What is the difference between `@classmethod` and `@staticmethod`?

**Answer**: `@classmethod`: first parameter is `cls` (the class itself) — has access to class attributes and can call other class methods. Use for: alternative constructors (`cls(...)`) and factory methods. `@staticmethod`: no implicit first parameter — just a regular function namespaced inside the class. No access to class or instance. Use for: utility functions logically related to the class but not needing class state. Example: `BankAccount.create_savings()` needs `cls` to call `cls(owner, initial)` — use `@classmethod`. `BankAccount.validate_amount(100)` doesn't need the class — use `@staticmethod`.

---

## ⚫ Interview Questions + Answers

Q1: What are the 4 pillars of OOP?
A1: (1) **Encapsulation**: bundling data + methods, hiding internal state. Python: `_private` (convention), `__mangled` (name mangling). (2) **Inheritance**: subclass inherits parent's attributes/methods — code reuse. Python supports multiple inheritance. (3) **Polymorphism**: same interface works with different types — `process_payment()` works for Stripe, Razorpay, PayPal. (4) **Abstraction**: hide complex implementation behind simple interface — user calls `process_payment()`, doesn't know it's making HTTP calls to Stripe API.

Q2: What is `self` in Python and why is it explicit?
A2: `self` refers to the current instance. Python requires it explicitly as the first parameter of every instance method — unlike Java/JS which use implicit `this`. Guido van Rossum: explicit is better than implicit (Zen of Python). When you call `account.deposit(100)`, Python translates it to `BankAccount.deposit(account, 100)` — `account` becomes `self`. `self` is just a convention — you could name it anything, but don't.

Q3: What is Method Resolution Order (MRO) in Python?
A3: MRO defines the order Python searches for methods in an inheritance hierarchy. Python uses C3 linearization algorithm. `ClassName.__mro__` shows the order. For `class C(A, B)`: Python searches C → A → B → object. With diamond inheritance: `class D(B, C)` where both B, C inherit A: MRO ensures A is only searched once. `super()` follows MRO — it doesn't just call the parent class, it calls the NEXT class in MRO. This makes cooperative multiple inheritance work correctly.

Q4: What is the difference between `__repr__` and `__str__`?
A4: `__repr__`: developer-facing representation — should be unambiguous, ideally valid Python code to recreate the object: `BankAccount(owner='Priya', balance=1000.00)`. Called by `repr()` and in REPL. `__str__`: user-facing representation — readable for display: `"Priya's account ($1000.00)"`. Called by `str()`, `print()`, and `f"{obj}"`. If only `__repr__` is defined, `__str__` falls back to it. If only `__str__` is defined, `__repr__` stays as the default memory address. Rule: always define `__repr__` — it helps debugging.

Q5: When should you use `@property` instead of `get_balance()` method?
A5: Use `@property` when: the value is an attribute conceptually (balance, name, age), computation is cheap, no side effects, no arguments needed. Use a regular method when: it takes arguments, has significant side effects, or involves heavy computation. `account.balance` (property) reads more naturally than `account.get_balance()`. Properties also allow validation in setters: `@balance.setter def balance(self, v): if v < 0: raise ValueError(...)`. Java-style `get_x()/set_x()` is not Pythonic — use properties or direct attribute access.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Class | Blueprint for objects | Objects का blueprint |
| Instance | Specific object from class | Class से बना specific object |
| self | Current instance reference | Current instance |
| Inheritance | Subclass reuses parent code | Subclass parent का code reuse |
| Polymorphism | Same interface, diff behavior | Same interface, अलग behavior |
| Encapsulation | Hide internal state | Internal state hide करना |
| @property | Attribute-style method access | Attribute की तरह method access |

---

## ⚡ 3-Line Summary
English: OOP organizes code into classes (blueprints) and objects (instances) with attributes (data) and methods (behavior). The 4 pillars: Encapsulation (hide state), Inheritance (reuse code), Polymorphism (same interface), Abstraction (hide complexity). Python's `@property`, `@classmethod`, `@staticmethod` and `__dunder__` methods make OOP expressive and Pythonic.
Hindi: OOP code को classes और objects में organize करता है। 4 pillars: Encapsulation, Inheritance, Polymorphism, Abstraction। Python के `@property`, `@classmethod`, `@staticmethod` OOP को Pythonic बनाते हैं।

---

## ➡️ Next Topic
**082. Classes and Objects Deep Dive** — `__slots__`, `__dict__`, class vs instance namespace. **086. classmethod + staticmethod** — when to use each. **090. Inheritance Complete** — super(), MRO, diamond problem.
