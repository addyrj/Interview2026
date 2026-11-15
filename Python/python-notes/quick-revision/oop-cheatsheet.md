# OOP Cheatsheet — Interview Ready
# हिंदी में: Python OOP Quick Reference

> Condensed from `03-oop/` (outputs verified in the notes).

## 🔷 Classes & Attributes

### 1. Class variable vs instance variable
A class variable is shared by all objects; `self.x = ...` creates a per-object attribute. Assigning through an instance shadows the class value; `del` brings it back.
```python
class Student:
    school: str = "DPS"
    count: int = 0
    def __init__(self, name: str) -> None:
        self.name: str = name
        Student.count += 1
s1: Student = Student("Asha")
s2: Student = Student("Raj")
print(s1.school, s2.school, Student.school)
print(Student.count)
Student.school = "KV"
print(s1.school, s2.school)
s1.school = "Private"
print(s1.school, s2.school, Student.school)
del s1.school
print(s1.school)
```
**हिंदी:** class variable सब objects में shared होता है; instance से assign करने पर वह सिर्फ उसी object की copy बन जाता है। · *Source: 03-oop/084-instance-vs-class-variables.md*

### 2. `a.x += 1` shadows, it does not update the class
`+=` reads the class value and writes the result on the instance. Objects without their own `x` still see the class value.
```python
class C:
    x = 1
a, b = C(), C()
a.x += 1
C.x += 10
print(a.x, b.x, C.x)
b.y = 5
print(hasattr(C, "y"), C().__dict__)
```
**हिंदी:** `a.x += 1` class के x को नहीं बदलता, a पर नया instance attribute बना देता है। · *Source: 03-oop/084-instance-vs-class-variables.md*

### 3. `__new__` runs before `__init__`
`__new__` creates the object; `__init__` runs only if `__new__` returns an instance of the class. `B()` below returns the int 42 and `B init` never prints.
```python
class A:
    def __init__(self):
        print("A init")
        return None
    def __new__(cls):
        print("A new")
        return super().__new__(cls)
class B:
    def __new__(cls):
        return 42
    def __init__(self):
        print("B init")
a = A()
b = B()
print(type(b))
```
**हिंदी:** `__new__` object बनाता है और `__init__` तभी चलता है जब `__new__` उसी class का instance लौटाए। · *Source: 03-oop/083-init-method.md*

### 4. classmethod (factory) and staticmethod
`@classmethod` gets `cls` (works for subclasses, ideal for factories). `@staticmethod` gets nothing: a plain function living in the class namespace.
```python
class Pizza:
    def __init__(self, toppings: list[str]) -> None:
        self.toppings: list[str] = toppings

    @classmethod
    def margherita(cls) -> "Pizza":
        return cls(["mozzarella", "tomato"])

    @classmethod
    def from_string(cls, s: str) -> "Pizza":
        return cls([t.strip() for t in s.split(",")])
class SpicyPizza(Pizza):
    pass
print(Pizza.margherita())
print(Pizza.from_string("corn, olives"))
print(SpicyPizza.margherita())

class MathUtil:
    @staticmethod
    def is_even(n: int) -> bool:
        return n % 2 == 0
    @staticmethod
    def clamp(x: float, lo: float, hi: float) -> float:
        return max(lo, min(x, hi))
print(MathUtil.is_even(4))
print(MathUtil().clamp(15, 0, 10))
```
**हिंदी:** classmethod को `cls` मिलता है (factory के लिए), staticmethod को कुछ नहीं मिलता, वह सिर्फ class में रखा function है। · *Source: 03-oop/086-class-methods.md, 03-oop/087-static-methods.md*

### 5. property
`@property` makes a method read like an attribute; without a setter it is read-only (`AttributeError`). A property is a data descriptor: writing into `__dict__` does not override it. A property returning `self.v` for itself recurses forever.
```python
class Circle:
    def __init__(self, radius: float) -> None:
        self._radius: float = radius

    @property
    def radius(self) -> float:
        return self._radius

    @property
    def area(self) -> float:
        return round(3.14159 * self._radius ** 2, 2)

c: Circle = Circle(2)
print(c.radius, c.area)
c._radius = 3
print(c.area)
try:
    c.area = 5
except AttributeError as e:
    print("Error:", e)
```
**हिंदी:** property method को attribute जैसा बना देता है; setter न हो तो वह read-only रहता है। · *Source: 03-oop/088-properties.md*

## 🔷 Inheritance, super(), MRO

### 6. super() and method overriding
`super().__init__(...)` runs the parent init. `Dog.__mro__` shows the search order. If a child overrides `__init__` without calling super, parent attributes are never set.
```python
class Animal:
    def __init__(self, name: str) -> None:
        self.name: str = name

    def speak(self) -> str:
        return f"{self.name} makes a sound"
class Dog(Animal):
    def __init__(self, name: str, breed: str) -> None:
        super().__init__(name)
        self.breed: str = breed
    def speak(self) -> str:
        base: str = super().speak()
        return f"{base} - Woof!"
d: Dog = Dog("Bruno", "Labrador")
print(d.name, d.breed)
print(d.speak())
print(Dog.__mro__)
```
**हिंदी:** child में `__init__` लिखो तो `super().__init__()` बुलाना मत भूलो, वरना parent के attributes नहीं बनते। · *Source: 03-oop/094-super-function.md*

### 7. MRO and cooperative super()
`D.mro()` is D, B, C, A, object. `super()` calls the NEXT class in the object's MRO, so `D().go()` prints D B C A, while a plain `B()` prints B A.
```python
class A:
    def go(self): print("A", end=" ")
class B(A):
    def go(self):
        print("B", end=" "); super().go()
class C(A):
    def go(self):
        print("C", end=" "); super().go()
class D(B, C):
    def go(self):
        print("D", end=" "); super().go()
D().go(); print()
B().go(); print()
print([k.__name__ for k in D.mro()])
```
**हिंदी:** `super()` अगली class को बुलाता है जो उस object के MRO में आती है, parent को नहीं। · *Source: 03-oop/093-mro-method-resolution-order.md*

### 8. Mixins call super() too
`C(M1, M2, A)` has MRO C, M1, M2, A, object, so the chain prints `M1>M2>A`. A standalone `M1().who()` raises `AttributeError`: a mixin needs a host class that provides the method.
```python
class A:
    def who(self) -> str:
        return "A"

class M1:
    def who(self) -> str:
        return "M1>" + super().who()

class M2:
    def who(self) -> str:
        return "M2>" + super().who()

class C(M1, M2, A):
    pass

print(C().who())
print(M1().who())
```
**हिंदी:** mixin का `super()` तभी काम करता है जब host class में वह method मौजूद हो। · *Source: 03-oop/097-mixins.md*

### 9. Name mangling (double underscore)
`__x` inside class `A` is stored as `_A__x`, inside `B` as `_B__x`. It avoids accidental clashes in subclasses; it is not real privacy.
```python
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
**हिंदी:** `__x` का नाम बदलकर `_ClassName__x` हो जाता है ताकि subclass में टकराव न हो; यह असली privacy नहीं है। · *Source: 03-oop/098-encapsulation.md*

## 🔷 Dunder (Magic) Methods

### 10. Core dunders
`__str__` for users, `__repr__` for developers, `__len__` for `len()`, `__bool__` for truth, `__eq__` for `==` (return `NotImplemented` for other types).
```python
class Product:
    def __init__(self, name: str, price: float, stock: int) -> None:
        self.name = name
        self.price = price
        self.stock = stock

    def __str__(self) -> str:
        """Called by str(), print() — human readable."""
        return f"{self.name} - ₹{self.price:.2f}"
    def __repr__(self) -> str:
        """Called by repr(), REPL — developer readable (should be unambiguous)."""
        return f"Product(name={self.name!r}, price={self.price}, stock={self.stock})"
    def __len__(self) -> int:
        """Called by len() — return stock count."""
        return self.stock
    def __bool__(self) -> bool:
        """Called by bool(), if statements — True if in stock."""
        return self.stock > 0
p = Product("iPhone", 79999, 5)
print(p)
print(repr(p))
print(len(p))
print(bool(p))
if p:
    print("In stock!")
```
**हिंदी:** `__str__` users के लिए, `__repr__` developers के लिए; `len()` और `bool()` भी dunder से तय होते हैं। · *Source: 03-oop/102-magic-methods.md*

### 11. str vs repr in containers
`print(b)` uses `__str__`; lists always show `repr` of items. `!r` and `%r` force repr, `!s` and `%s` force str. Without `__str__`, Python falls back to `__repr__`.
```python
class A:
    def __repr__(self) -> str:
        return "repr-A"

class B(A):
    def __str__(self) -> str:
        return "str-B"

b = B()
print(b)
print([b])
print(f"{b!r} {b!s}")
print("%s %r" % (b, b))
```
**हिंदी:** list के अंदर हमेशा `repr` दिखता है; `print` पहले `__str__` ढूँढता है और न मिले तो `__repr__` पर जाता है। · *Source: 03-oop/103-str-vs-repr.md*

### 12. Old sequence protocol: only `__getitem__`
With just `__getitem__`, `list()`, `in` and `sum()` work (Python calls `w[0]`, `w[1]`, ... until `IndexError`). `len()` still needs `__len__`.
```python
class Weird:
    def __getitem__(self, i: int) -> int:
        if i >= 3:
            raise IndexError
        return i * 10

w = Weird()
print(list(w))
print(20 in w)
print(sum(w))
print(len(w))
```
**हिंदी:** सिर्फ `__getitem__` हो तो भी for, `in`, `sum` चलते हैं, लेकिन `len()` के लिए `__len__` चाहिए। · *Source: 03-oop/104-len-getitem-setitem.md*

### 13. Context manager
`__enter__` / `__exit__` run even when the block raises. If `__exit__` returns `True` the exception is swallowed.
```python
class Resource:
    def __init__(self, name: str) -> None:
        self.name: str = name

    def __enter__(self) -> "Resource":
        print(f"open {self.name}")
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        print(f"close {self.name} (error: {exc_type.__name__ if exc_type else None})")
        return False

with Resource("db") as r:
    print("using", r.name)
```
**हिंदी:** `with` के अंदर error आए तब भी `__exit__` चलता है; वह `True` लौटाए तो error दब जाता है। · *Source: 03-oop/106-enter-exit-context-managers.md*

## 🔷 Dataclasses

### 14. @dataclass basics
Auto `__init__`, `__repr__`, `__eq__`. Mutable defaults need `field(default_factory=...)`. `frozen=True` makes it immutable and hashable; `order=True` adds comparisons. `replace()` returns a changed copy.
```python
from dataclasses import dataclass, field, asdict, astuple, replace

@dataclass
class Product:
    name: str
    price: float
    tags: list[str] = field(default_factory=list) # mutable default must use default_factory
    in_stock: bool = True
p: Product = Product("Laptop", 55000.0)
print(p)
print(p == Product("Laptop", 55000.0))
p.tags.append("electronics")
print(Product("Pen", 10.0).tags)
cheaper: Product = replace(p, price=49999.0)
print(cheaper.price, p.price)
@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int

v1, v2 = Version(1, 2), Version(1, 10)
print(v1 < v2, sorted([v2, v1]))
try:
    v1.major = 5
except Exception as e:
    print(type(e).__name__)
```
**हिंदी:** mutable default के लिए `default_factory` लगाओ; `frozen=True` से object बदला नहीं जा सकता। · *Source: 03-oop/109-dataclasses.md*

### 15. Dataclass field needs an annotation
`y = 5` without an annotation is a plain class variable, not a field: not in `__init__`, `__repr__` or `__eq__`. Use `ClassVar` to make the intent explicit.
```python
from dataclasses import dataclass

@dataclass
class P:
    x: int
    y = 5            # no annotation!

a = P(1)
b = P(1)
P.y = 10
print(a == b, a.y, P.__dataclass_fields__.keys())
try:
    P(1, 2)
except TypeError as e:
    print("TypeError")
```
**हिंदी:** annotation के बिना लिखा attribute dataclass field नहीं होता, वह सिर्फ class variable है। · *Source: 03-oop/109-dataclasses.md*

## 🔷 ABC & Protocol

### 16. Abstract base class
A class with an `@abstractmethod` cannot be instantiated, and neither can a subclass that forgets to implement it (`TypeError`). `Shape.__abstractmethods__` lists the missing names.
```python
from abc import ABC, abstractmethod
import math
class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        ...
class Circle(Shape):
    def __init__(self, r: float) -> None:
        self.r: float = r

    def area(self) -> float:
        return math.pi * self.r ** 2
class Square(Shape):
    pass
try:
    Shape()
except TypeError as e:
    print("Error 1:", e)
print(Shape.__abstractmethods__)
```
**हिंदी:** ABC में abstractmethod लिखा हो तो class का object नहीं बन सकता; subclass में implement करना ज़रूरी है। · *Source: 03-oop/095-abstract-classes-abc.md*

### 17. Patching an abstract method later does not help
The abstract-name set is computed at class creation. Fix with `abc.update_abstractmethods(B)` (Python 3.10+).
```python
from abc import ABC, abstractmethod

class A(ABC):
    @abstractmethod
    def f(self) -> int: ...

class B(A):
    pass

B.f = lambda self: 1          # patch the method AFTER class creation
try:
    print(B().f())
except TypeError as e:
    print("TypeError")
```
**हिंदी:** abstract methods की list class बनते समय तय हो जाती है, बाद में method जोड़ने से class concrete नहीं बनती। · *Source: 03-oop/095-abstract-classes-abc.md*

### 18. Protocol (structural typing)
No inheritance needed: matching method names is enough, and the type checker (mypy) enforces it. `isinstance` works only with `@runtime_checkable`, otherwise `TypeError`. It checks that the name exists, not its type.
```python
from typing import Protocol, runtime_checkable
class Quacker(Protocol):
    def quack(self) -> str: ...
class Duck:
    def quack(self) -> str:
        return "Quack!"
class Cat:
    def meow(self) -> str:
        return "meow"
def make_noise(q: Quacker) -> str:
    return q.quack()
print(make_noise(Duck()))
@runtime_checkable
class Closable(Protocol):
    def close(self) -> None: ...
class Conn:
    def close(self) -> None:
        print("closed")

print(isinstance(Conn(), Closable), isinstance(Cat(), Closable))
try:
    isinstance(Duck(), Quacker)
except TypeError as e:
    print("TypeError:", e)
```
**हिंदी:** Protocol में inheritance नहीं चाहिए, method का नाम मिलना काफ़ी है; `isinstance` के लिए `@runtime_checkable` लगाओ। · *Source: 03-oop/115-protocol-structural-subtyping.md*

---

## 🔷 Key Rules

1. **Class variable** → shared; `obj.x = ...` or `obj.x += 1` shadows it on the instance
2. **`__new__`** creates, **`__init__`** initialises; `__init__` is skipped if `__new__` returns another type
3. **`@classmethod`** → factories (`cls(...)`); **`@staticmethod`** → plain utility
4. **`super()`** → next class in the object's MRO, not "the parent"
5. **Child `__init__`** → call `super().__init__()` or parent attributes are missing
6. **Mutable defaults** → `field(default_factory=list)` in dataclasses
7. **ABC** → nominal (must inherit); **Protocol** → structural (same methods is enough)
