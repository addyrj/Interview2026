---

# Q162. Explain Descriptors with Example
# Category: Tricky Concepts
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What is a descriptor in Python? Build a reusable validated attribute (`Positive`) and explain the difference between data and non-data descriptors.

---

## 💡 Quick Concept (2 lines only)
A descriptor is an object with `__get__`, `__set__` and/or `__delete__`, stored as a CLASS attribute, that controls access to an attribute. `property`, methods and `classmethod` are all descriptors.
हिंदी: Descriptor वह class attribute है जिसमें `__get__/__set__` होते हैं और जो attribute access को control करता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class Positive:                                   # Step 1: a data descriptor (has __set__)
    def __set_name__(self, owner, name: str) -> None:   # Step 2: called once at class creation
        self.private = "_" + name                 # store values under "_price" etc. in the instance

    def __get__(self, obj, objtype=None):         # Step 3: runs on obj.attr / Class.attr
        if obj is None:                           # accessed on the class itself
            return self                           # return the descriptor
        return getattr(obj, self.private)         # read from the instance's own storage

    def __set__(self, obj, value) -> None:        # Step 4: runs on obj.attr = value
        if value <= 0:                            # validation lives in ONE place
            raise ValueError("must be positive")  # reject bad input
        setattr(obj, self.private, value)         # store per instance

class Product:                                    # Step 5: use the descriptor
    price = Positive()                            # class attribute, shared by all instances
    qty = Positive()                              # reuse for another field

    def __init__(self, price: float, qty: int) -> None:   # constructor
        self.price = price                        # triggers Positive.__set__
        self.qty = qty                            # triggers Positive.__set__

# ============================================
# TEST CASES
# ============================================
p = Product(9.5, 3)                               # valid values
print(p.price, p.qty)                             # Expected: 9.5 3
try:                                              # invalid assignment
    p.price = -1                                  # calls __set__ -> raises
except ValueError as e:                           # catch it
    print("error:", e)                            # Expected: error: must be positive
print(p.__dict__)                                 # Expected: {'_price': 9.5, '_qty': 3}
print(type(Product.price).__name__)               # Expected: Positive  (__get__ with obj=None)

# Data vs non-data: a non-data descriptor (only __get__) can be shadowed by the instance dict
class Const:                                      # non-data descriptor
    def __get__(self, obj, objtype=None):         # only __get__
        return 42                                 # always 42
class A:                                          # holder
    x = Const()                                   # class attribute
a = A()                                           # instance
print(a.x)                                        # Expected: 42
a.x = 7                                           # allowed: goes into the instance __dict__
print(a.x)                                        # Expected: 7   (instance dict wins over non-data)
```

---

## 🔍 Why This Works (3 lines max)
Attribute lookup checks the class for a data descriptor first, then the instance `__dict__`, then non-data descriptors/class attributes. `Positive` defines `__set__`, so it always intercepts assignment. Functions are non-data descriptors, which is how `obj.method` becomes a bound method.
हिंदी: Lookup में data descriptor सबसे ऊपर है, फिर instance `__dict__`, फिर non-data descriptor।

---

## ⚡ Alternative Solution
```python
# The same validation with property (fine for one field, repetitive for many)
class Product2:                                   # property-based version
    def __init__(self, price: float) -> None:     # constructor
        self.price = price                        # goes through the setter

    @property                                     # getter
    def price(self) -> float:                     # read access
        return self._price                        # backing field

    @price.setter                                 # setter
    def price(self, value: float) -> None:        # write access
        if value <= 0:                            # validate
            raise ValueError("must be positive")  # reject
        self._price = value                       # store

print(Product2(5).price)                          # Expected: 5

# Proof that functions are descriptors:
class B:                                          # simple class
    def hello(self) -> str:                       # plain function
        return "hi"                               # result
b = B()                                           # instance
print(B.__dict__["hello"].__get__(b, B)())        # Expected: hi   (manual __get__ makes a bound method)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: storing the value ON the descriptor -> shared by ALL instances
class BadPositive:
    def __init__(self): self.value = None          # one slot for the whole class
    def __get__(self, obj, objtype=None): return self.value
    def __set__(self, obj, value): self.value = value   # overwrites for every instance

class T:
    n = BadPositive()
t1, t2 = T(), T()
t1.n = 1
t2.n = 2
print(t1.n)                                        # Actual: 2   (leaked state!)

# ✅ Correct: store per instance (setattr(obj, ...) or obj.__dict__) as Positive does
```

---

## 🎯 Interview Tip (1 line)
Say: "Descriptors live on the class; `property`, methods, `classmethod` and `__slots__` all use them. Data descriptors (with `__set__`) take priority over the instance dict."

---

## 🔗 Related Questions
→ Q036 (property setter) | Q037 (staticmethod vs classmethod) | Q169 (__slots__) | Q178 (__getattr__ vs __getattribute__) | Q306 (dunder methods)
