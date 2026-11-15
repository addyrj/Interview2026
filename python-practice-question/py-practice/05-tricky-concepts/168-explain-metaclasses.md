---

# Q168. Explain Metaclasses
# Category: Tricky Concepts
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What is a metaclass? Show that classes are objects created by `type`, write a metaclass that enforces a rule, and mention simpler alternatives.

---

## 💡 Quick Concept (2 lines only)
A metaclass is "the class of a class": `type` creates every class, and a custom metaclass lets you customise class creation (validate, register, modify attributes).
हिंदी: Metaclass class की भी class होती है — जैसे object को class बनाती है, वैसे class को metaclass बनाती है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
# Part 1: a class is just an instance of `type`
Dog = type("Dog", (), {"sound": "woof", "speak": lambda self: self.sound})  # Step 1: build a class by hand
print(Dog().speak())                           # Expected: woof

class RequireDoc(type):                        # Step 2: a metaclass inherits from type
    registry: list[str] = []                   # collects every class it creates

    def __new__(mcls, name, bases, namespace):     # Step 3: runs when a class statement executes
        if name != "Base" and not namespace.get("__doc__"):   # enforce a docstring
            raise TypeError(f"{name} needs a docstring")      # reject at definition time
        cls = super().__new__(mcls, name, bases, namespace)   # build the real class
        mcls.registry.append(name)             # register it (plugin pattern)
        return cls                             # return the new class

    def __call__(cls, *args, **kwargs):        # Step 4: runs on Class(...) instantiation
        print(f"creating {cls.__name__}")      # hook into instance creation
        return super().__call__(*args, **kwargs)   # normal construction

class Base(metaclass=RequireDoc):              # Step 5: use the metaclass
    pass                                       # Base is exempt from the rule

class Good(Base):                              # subclass inherits the metaclass
    """I have a docstring."""                  # satisfies the rule

# ============================================
# TEST CASES
# ============================================
print(type(Good), type(Base))                  # Expected: <class '__main__.RequireDoc'> <class '__main__.RequireDoc'>
print(type(RequireDoc))                        # Expected: <class 'type'>
print(RequireDoc.registry)                     # Expected: ['Base', 'Good']
Good()                                         # Expected: creating Good
try:                                           # defining a class without a docstring
    class Bad(Base):                           # no docstring here
        pass                                   # body is empty
except TypeError as e:                         # error at class-definition time
    print(e)                                   # Expected: Bad needs a docstring
```

---

## 🔍 Why This Works (3 lines max)
Executing a `class` statement calls `metaclass(name, bases, namespace)`; the default metaclass is `type`. Overriding `__new__` lets you inspect or change the namespace before the class exists, and `__call__` controls instance creation. Subclasses inherit the metaclass automatically.
हिंदी: `class` statement असल में `metaclass(name, bases, namespace)` call करता है — `__new__` में हम उसे बदल या रोक सकते हैं।

---

## ⚡ Alternative Solution
```python
# Usually you DON'T need a metaclass: __init_subclass__ covers registries and validation
class Plugin:                                      # base class
    registry: dict[str, type] = {}                 # name -> class

    def __init_subclass__(cls, **kwargs) -> None:  # called for every subclass (3.6+)
        super().__init_subclass__(**kwargs)        # cooperate with other bases
        Plugin.registry[cls.__name__] = cls        # register the subclass

class CSV(Plugin): ...                             # auto-registered
class JSON(Plugin): ...                            # auto-registered
print(sorted(Plugin.registry))                     # Expected: ['CSV', 'JSON']

# A singleton via metaclass (classic interview use)
class Singleton(type):                             # metaclass
    _instances: dict[type, object] = {}            # one instance per class
    def __call__(cls, *a, **k):                    # intercept Class()
        if cls not in Singleton._instances:        # first time only
            Singleton._instances[cls] = super().__call__(*a, **k)   # build and cache
        return Singleton._instances[cls]           # always return the same object

class Config(metaclass=Singleton): ...             # singleton class
print(Config() is Config())                        # Expected: True
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: reaching for a metaclass when a decorator or __init_subclass__ is enough
#    (metaclasses are hard to read and conflict when combining bases)

class M1(type): ...
class M2(type): ...
class A(metaclass=M1): ...
class B(metaclass=M2): ...
# class C(A, B): ...   # TypeError: metaclass conflict (not run)

# ✅ Correct: prefer __init_subclass__, class decorators, or plain functions; use metaclasses only for deep class-creation hooks
```

---

## 🎯 Interview Tip (1 line)
Say: "Classes are instances of `type`; a metaclass customises class creation, but `__init_subclass__` or a class decorator is usually the simpler tool."

---

## 🔗 Related Questions
→ Q030 (__init__ vs __new__) | Q261 (singleton pattern) | Q262 (factory pattern) | Q300 (__init__ vs __new__ classic) | Q306 (dunder methods)
