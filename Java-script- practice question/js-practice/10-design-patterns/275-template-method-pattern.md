---

# Q275. Template Method Pattern
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Create a `DataExporter` base class with a fixed `export()` algorithm (read -> transform -> format -> write) where subclasses override only some steps.

---

## 💡 Quick Concept (2 lines only)
A base class defines the skeleton of an algorithm; subclasses fill in specific steps without changing the order.
हिंदी: Base class में steps का क्रम तय रहता है, subclass सिर्फ अपने हिस्से बदलती है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Base class has template method export()
// Step 2: Some steps have defaults, some are abstract
// Step 3: Subclasses override the varying steps

class DataExporter {
  export(data) {                                 // template method: fixed order
    const cleaned = this.transform(data);        // step 1 (hook with default)
    const out = this.format(cleaned);            // step 2 (abstract)
    return this.write(out);                      // step 3 (default)
  }
  transform(data) { return data; }               // default: no change
  format() { throw new Error('format() must be implemented'); } // abstract step
  write(out) { return `saved -> ${out}`; }       // default writer
}

class CsvExporter extends DataExporter {
  format(rows) { return rows.map((r) => r.join(',')).join(';'); } // CSV-ish
}

class JsonExporter extends DataExporter {
  transform(rows) { return rows.filter((r) => r.length); }   // drop empty rows
  format(rows) { return JSON.stringify(rows); }              // JSON format
}

// ============================================
// TEST CASES
// ============================================

console.log(new CsvExporter().export([[1, 2], [3, 4]]));     // Expected: saved -> 1,2;3,4
console.log(new JsonExporter().export([[1], [], [2]]));      // Expected: saved -> [[1],[2]]
try { new DataExporter().export([]); } catch (e) { console.log(e.message); } // Expected: format() must be implemented
```

---

## 🔍 Why This Works (3 lines max)
`export()` is never overridden, so the step order is guaranteed. Polymorphism picks the right `format` and `transform` at runtime.
हिंदी: export() का क्रम fix है, बस हर step का असली काम subclass तय करती है।

---

## ⚡ Alternative Solution
```javascript
// Functional version: pass the varying steps in
const exporter = ({ format, transform = (d) => d }) => (data) => `saved -> ${format(transform(data))}`; // template as HOF
console.log(exporter({ format: (d) => d.join('|') })([1, 2, 3])); // Expected: saved -> 1|2|3
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: subclass overrides export() and skips steps, breaking the contract
// ✅ Correct: override only the hook steps (transform/format)
```

---

## 🎯 Interview Tip (1 line)
Link to React lifecycle methods and "Hollywood principle: don't call us, we'll call you".

---

## 🔗 Related Questions
→ Q264 (Strategy) | Q147 (Class inheritance) | Q058 (Flatten)
