---

# Q031. Inheritance and super() output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐ Easy

---

## ❓ Question
What will this print? What happens in `Cat` when `super().__init__` is forgotten?

```python
class Animal:
    def __init__(self, name):
        print("Animal.__init__")
        self.name = name

class Dog(Animal):
    def __init__(self, name, breed):
        print("Dog.__init__ start")
        super().__init__(name)
        self.breed = breed
        print("Dog.__init__ end")

Dog("Rex", "Lab")
```

---

## 💡 Quick Concept (2 lines only)
`super()` calls the next class in the MRO; a child `__init__` replaces the parent's, so the parent's runs only if you call it.
हिंदी: Child का `__init__` parent का `__init__` अपने-आप नहीं चलाता — `super().__init__()` खुद call करना पड़ता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class Animal:
    def __init__(self, name: str) -> None:
        print("Animal.__init__")      # parent initializer
        self.name = name              # sets name
    def speak(self) -> str:
        return "..."                  # default sound

class Dog(Animal):
    def __init__(self, name: str, breed: str) -> None:
        print("Dog.__init__ start")   # Step 1
        super().__init__(name)        # Step 2: jumps to Animal.__init__
        self.breed = breed            # Step 3: child state
        print("Dog.__init__ end")     # Step 4
    def speak(self) -> str:
        return super().speak() + " Woof"  # extend parent's behaviour

class Cat(Animal):
    def __init__(self, name: str) -> None:
        print("Cat.__init__")         # forgets super().__init__ -> no self.name

# ============================================
# TEST CASES
# ============================================
d = Dog("Rex", "Lab")
# Expected:
# Dog.__init__ start
# Animal.__init__
# Dog.__init__ end
print(d.speak(), d.name, d.breed)  # Expected: ... Woof Rex Lab
c = Cat("Tom")                     # Expected: Cat.__init__
try:
    print(c.name)                  # name was never set
except AttributeError as e:
    print("AttributeError:", e)    # Expected: AttributeError: 'Cat' object has no attribute 'name'
print(Dog.__mro__)  # Expected: (<class '__main__.Dog'>, <class '__main__.Animal'>, <class 'object'>)
```

---

## 🔍 Why This Works (3 lines max)
`super()` looks at `type(self).__mro__` and starts after the current class. `Dog.speak` overrides `Animal.speak` but reuses it through `super()`. `Cat` skipped the call, so `name` never exists.
हिंदी: `super()` MRO में अगली class पर जाता है — Cat ने call नहीं किया इसलिए `name` नहीं बना।

---

## ⚡ Alternative Solution
```python
# Cooperative style: forward **kwargs so the chain works with multiple inheritance
class Base:
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)    # keep the chain going

class Child(Base):
    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(**kwargs)    # pass the rest up
        self.name = name              # own state

print(Child(name="x").name)           # Expected: x
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: Animal.__init__(self, name)  -> hardcodes the parent, breaks in multiple inheritance
# ❌ Wrong: Python 2 style super(Dog, self).__init__(name) -> verbose
# ✅ Correct: super().__init__(name)
```

---

## 🎯 Interview Tip (1 line)
Say: "`super()` follows the MRO, not 'the parent' — that's what makes cooperative multiple inheritance work."

---

## 🔗 Related Questions
→ Q030 (__init__ vs __new__) | Q032 (diamond MRO) | Q033 (super chain) | Q302 (MRO)
