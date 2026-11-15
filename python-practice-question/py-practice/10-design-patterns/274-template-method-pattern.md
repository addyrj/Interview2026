---

# Q274. Template Method Pattern
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Create a data-import pipeline with an abstract base class whose `run()` method fixes the steps (read -> parse -> save) while subclasses (`CsvImporter`, `JsonImporter`) fill in the varying steps.

---

## 💡 Quick Concept (2 lines only)
A base class defines the skeleton of an algorithm in one method; subclasses override only specific steps. The base controls the order, subclasses control the details.
हिंदी: Base class algorithm का ढाँचा तय करती है, और subclasses सिर्फ कुछ steps अपने हिसाब से बदलती हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import json  # Step 1: used by JsonImporter
from abc import ABC, abstractmethod  # abstract base class tools


class Importer(ABC):  # Step 2: the template class
    def run(self, raw: str) -> list[dict]:  # the template method - do not override
        rows = self.parse(raw)  # step 1: subclass-specific parsing
        rows = [r for r in rows if self.is_valid(r)]  # step 2: shared filter (hook)
        self.save(rows)  # step 3: shared saving
        return rows  # return stored rows

    @abstractmethod
    def parse(self, raw: str) -> list[dict]:  # must be implemented
        ...

    def is_valid(self, row: dict) -> bool:  # Step 3: hook with default behaviour
        return True  # by default accept all rows

    def save(self, rows: list[dict]) -> None:
        print(f"saved {len(rows)} rows")  # common saving logic


class CsvImporter(Importer):  # Step 4: concrete subclass 1
    def parse(self, raw: str) -> list[dict]:
        head, *lines = raw.strip().splitlines()  # first line = header
        keys = head.split(",")  # column names
        return [dict(zip(keys, ln.split(","))) for ln in lines]  # rows as dicts

    def is_valid(self, row: dict) -> bool:
        return row["name"] != ""  # override hook: name is required


class JsonImporter(Importer):  # concrete subclass 2
    def parse(self, raw: str) -> list[dict]:
        return json.loads(raw)  # JSON array of objects


# ============================================
# TEST CASES
# ============================================
print(CsvImporter().run("name,age\nAsha,30\n,5\nRavi,41"))
# Expected: saved 2 rows
# Expected: [{'name': 'Asha', 'age': '30'}, {'name': 'Ravi', 'age': '41'}]
print(JsonImporter().run('[{"name": "Zed"}]'))
# Expected: saved 1 rows
# Expected: [{'name': 'Zed'}]
try:
    Importer()  # abstract class cannot be created
except TypeError as e:
    print(e)  # Expected: Can't instantiate abstract class Importer without an implementation for abstract method 'parse'
```

---

## 🔍 Why This Works (3 lines max)
`run()` fixes the order, and calls `parse`, `is_valid`, `save` on `self`, which dispatch to the subclass. `@abstractmethod` forces required steps; hooks like `is_valid` are optional.
हिंदी: `run()` क्रम तय करता है और `self` के methods subclass तक पहुँचते हैं; abstract method ज़रूरी है, hook वैकल्पिक।

---

## ⚡ Alternative Solution
```python
# Function-based: pass the varying steps as arguments (no inheritance)
from collections.abc import Callable  # type hint


def run_import(raw: str, parse: Callable[[str], list[dict]],
               valid: Callable[[dict], bool] = lambda r: True) -> list[dict]:
    rows = [r for r in parse(raw) if valid(r)]  # same skeleton, steps injected
    print(f"saved {len(rows)} rows")  # shared saving
    return rows  # result


print(run_import("a;b", lambda s: [{"v": x} for x in s.split(";")]))
# Expected: saved 2 rows
# Expected: [{'v': 'a'}, {'v': 'b'}]
```

---

## ⚠️ Common Mistake
```python
# NOT RUN - illustrative (continues from the solution above)
# ❌ Wrong: subclass overrides run() and breaks the fixed order
class Broken(CsvImporter):
    def run(self, raw: str) -> list[dict]:
        self.save([])  # saves before parsing!
        return self.parse(raw)  # skeleton is no longer guaranteed

# ✅ Correct: override only the steps (parse / is_valid), never run()
# Tip: document run() as "final" (Python has typing.final)
```

---

## 🎯 Interview Tip (1 line)
Say: "Template Method uses inheritance to fix the algorithm order; if steps vary a lot I prefer Strategy (composition) instead."

---

## 🔗 Related Questions
→ Q264 (strategy) | Q149 (complete abstract base class) | Q031 (inheritance + super)
