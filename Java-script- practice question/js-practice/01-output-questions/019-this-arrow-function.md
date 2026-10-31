---

# Q019. this in Arrow Function
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print (Node.js CommonJS)?

```javascript
const obj = {
  name: 'Aditya',
  regular() { return this.name; },
  arrow: () => this === module.exports,
  nested() { const inner = () => this.name; return inner(); },
};
console.log(obj.regular());
console.log(obj.arrow());
console.log(obj.nested());
```

---

## 💡 Quick Concept (2 lines only)
Arrow functions have no own `this`; they inherit it from the surrounding scope where they were written.
हिंदी: Arrow function का अपना this नहीं होता, वह आसपास के (lexical) scope से this लेता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: regular() is a method -> this = obj
// Step 2: arrow is defined at module level -> this = module.exports (not obj)
// Step 3: inner arrow inside nested() inherits nested's this = obj

const obj = {
  name: 'Aditya',                                  // property
  regular() { return this.name; },                 // this = obj
  arrow: () => this === module.exports,            // this from module scope
  nested() {
    const inner = () => this.name;                 // inherits this from nested
    return inner();                                // this = obj
  },
};

// ============================================
// TEST CASES
// ============================================

console.log(obj.regular());                        // Expected: Aditya
console.log(obj.arrow());                          // Expected: true
console.log(obj.nested());                         // Expected: Aditya
```

---

## 🔍 Why This Works (3 lines max)
`this` in an arrow is fixed at definition time by lexical scope, not by how it is called. At module top level in CommonJS that is `module.exports`.
हिंदी: Arrow में this define होने की जगह से तय होता है, call करने के तरीके से नहीं।

---

## ⚡ Alternative Solution
```javascript
// Arrow ignores call/bind for this
const f = () => this === module.exports;           // arrow at module level
console.log(f.call({ x: 1 }));                     // Expected: true (call can't change it)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Using arrow as an object method and expecting this = object
// const o = { n: 1, get: () => this.n };  // undefined
// ✅ Use a regular method; use arrows for callbacks inside methods
```

---

## 🎯 Interview Tip (1 line)
Say: "Arrows capture this lexically, so they're great for callbacks but wrong for object methods."

---

## 🔗 Related Questions
→ Q018 (this in regular function) | Q020 (this in class) | Q021 (this in setTimeout) | Q298 (arrow vs regular)
