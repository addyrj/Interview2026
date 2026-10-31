---

# Q262. Factory Pattern
# Category: Design Patterns
# Difficulty: ⭐ Easy

---

## ❓ Question
Create a `createUser(type, name)` factory that returns an Admin, Editor or Guest object with different permissions, without the caller using `new` directly.

---

## 💡 Quick Concept (2 lines only)
A factory function hides object creation logic and returns the right object based on input.
हिंदी: Factory input देखकर सही तरह का object बनाकर देता है, caller को `new` की चिंता नहीं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Define classes for each type
// Step 2: Map type string -> class
// Step 3: Factory looks up the class and instantiates it

class Admin {
  constructor(name) { this.name = name; this.perms = ['read', 'write', 'delete']; } // full access
}
class Editor {
  constructor(name) { this.name = name; this.perms = ['read', 'write']; }           // limited access
}
class Guest {
  constructor(name) { this.name = name; this.perms = ['read']; }                    // read only
}

const registry = { admin: Admin, editor: Editor, guest: Guest }; // type -> class lookup

function createUser(type, name) {
  const Cls = registry[type];                          // find class for this type
  if (!Cls) throw new Error(`Unknown type: ${type}`);  // fail loudly on bad input
  return new Cls(name);                                // create and return instance
}

// ============================================
// TEST CASES
// ============================================

console.log(createUser('admin', 'Asha').perms);          // Expected: [ 'read', 'write', 'delete' ]
console.log(createUser('guest', 'Bob').perms);           // Expected: [ 'read' ]
console.log(createUser('editor', 'Cy') instanceof Editor); // Expected: true
try { createUser('hacker', 'X'); } catch (e) { console.log(e.message); } // Expected: Unknown type: hacker
```

---

## 🔍 Why This Works (3 lines max)
The caller only knows the factory and a type string. Adding a new type means adding one registry entry, not touching callers.
हिंदी: नया type जोड़ना हो तो सिर्फ registry में एक line, बाकी code वैसा ही रहता है।

---

## ⚡ Alternative Solution
```javascript
// Plain-object factory (no classes)
const makeShape = (kind, size) => ({ kind, area: kind === 'square' ? size ** 2 : Math.PI * size ** 2 }); // object literal per call
console.log(makeShape('square', 3).area); // Expected: 9
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: giant if/else in every caller
// if (type === 'admin') user = new Admin(n); else if (...) ...

// ✅ Correct: centralise in one factory / registry
```

---

## 🎯 Interview Tip (1 line)
Say: "Factory decouples creation from usage and follows open/closed — e.g. React.createElement is a factory."

---

## 🔗 Related Questions
→ Q261 (Singleton) | Q264 (Strategy) | Q111 (Object.create)
