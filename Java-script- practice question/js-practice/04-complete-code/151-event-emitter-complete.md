---

# Q151. Complete Event Emitter
# Category: Complete the Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks to implement `on`, `off`, `emit` and `once`.

```javascript
class Emitter {
  constructor() { this.events = {}; }
  on(name, fn) {
    (this.events[name] ||= []).____(fn);          // add handler
    return this;
  }
  off(name, fn) {
    this.events[name] = (this.events[name] || []).____(f => f !== fn); // remove
    return this;
  }
  emit(name, ...args) {
    (this.events[name] || []).____(fn => fn(____)); // call handlers
  }
  once(name, fn) {
    const wrap = (...a) => { fn(...a); this.____(name, wrap); }; // self-remove
    return this.on(name, wrap);
  }
}
```

---

## 💡 Quick Concept (2 lines only)
An emitter maps event names to arrays of handlers. `emit` calls them, `off` removes them, and `once` removes itself after the first call.
हिंदी: Emitter event name को handlers की list से जोड़ता है; `emit` उन्हें चलाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

class Emitter {
  constructor() { this.events = {}; }                          // Step 1: name -> handlers
  on(name, fn) {
    (this.events[name] ||= []).push(fn);                       // blank 1: push handler
    return this;                                               // allow chaining
  }
  off(name, fn) {
    this.events[name] = (this.events[name] || []).filter(f => f !== fn); // blank 2
    return this;
  }
  emit(name, ...args) {
    (this.events[name] || []).forEach(fn => fn(...args));      // blanks 3+4: spread args
  }
  once(name, fn) {
    const wrap = (...a) => { fn(...a); this.off(name, wrap); }; // blank 5: remove after run
    return this.on(name, wrap);
  }
}

// ============================================
// TEST CASES
// ============================================

const e = new Emitter();
e.on('hi', (n) => console.log('hi', n));                       // permanent handler
e.once('hi', () => console.log('once'));                       // runs one time
e.emit('hi', 'Aman');   // Expected: hi Aman / once
e.emit('hi', 'Riya');   // Expected: hi Riya
```

---

## 🔍 Why This Works (3 lines max)
Handlers are stored by event name; `emit` forwards its arguments. `once` wraps the handler so it unsubscribes itself.
हिंदी: `once` handler को wrap करता है ताकि पहली call के बाद वह खुद हट जाए।

---

## ⚡ Alternative Solution
```javascript
// Node's built-in
const EventEmitter = require('events');
const n = new EventEmitter();
n.once('x', () => console.log('built-in once'));
n.emit('x'); // built-in once
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: off() with a new anonymous function never matches
// e.off('hi', () => {});
// ✅ Correct: pass the same function reference used in on()
```

---

## 🎯 Interview Tip (1 line)
Say: "Emitter is Node's core pattern; I handle off while emitting by iterating over a copy."

---

## 🔗 Related Questions
→ Q096 (event emitter) | Q097 (pub/sub) | Q130 (listener leak) | Q158 (complete pub/sub)
