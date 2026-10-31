---

# Q150. Complete Observable Pattern
# Category: Complete the Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks for a simple Subject with subscribe, unsubscribe and notify.

```javascript
class Subject {
  constructor() { this.observers = ____; }          // list of observers
  subscribe(fn) {
    this.observers.____(fn);                        // add observer
    return () => {
      this.observers = this.observers.____(o => o !== fn); // remove it
    };
  }
  next(value) {
    this.observers.____(fn => fn(value));           // notify all
  }
}
```

---

## 💡 Quick Concept (2 lines only)
A Subject keeps a list of listeners and calls each one when a new value is emitted. `subscribe` returns an unsubscribe function.
हिंदी: Subject listeners की list रखता है और नई value आने पर सबको call करता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

class Subject {
  constructor() { this.observers = []; }                     // blank 1: empty list
  subscribe(fn) {
    this.observers.push(fn);                                 // blank 2: add observer
    return () => {                                           // unsubscribe handle
      this.observers = this.observers.filter(o => o !== fn); // blank 3: remove observer
    };
  }
  next(value) {
    this.observers.forEach(fn => fn(value));                 // blank 4: notify everyone
  }
}

// ============================================
// TEST CASES
// ============================================

const s = new Subject();
const unsub = s.subscribe(v => console.log('A got', v));     // observer A
s.subscribe(v => console.log('B got', v));                   // observer B
s.next(1);                  // Expected: A got 1 / B got 1
unsub();                    // remove A
s.next(2);                  // Expected: B got 2
```

---

## 🔍 Why This Works (3 lines max)
Observers are plain callbacks stored in an array; `next` loops and calls them. The returned function filters one out, preventing leaks.
हिंदी: observers callbacks होते हैं जो array में रहते हैं; unsubscribe उन्हें filter कर देता है।

---

## ⚡ Alternative Solution
```javascript
// Use a Set for O(1) add/remove
class Subject2 {
  observers = new Set();
  subscribe(fn) { this.observers.add(fn); return () => this.observers.delete(fn); }
  next(v) { this.observers.forEach(f => f(v)); }
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: no unsubscribe, handlers pile up and leak memory
// ✅ Correct: always return/call the unsubscribe function
```

---

## 🎯 Interview Tip (1 line)
Say: "Observer = one-to-many notification; RxJS and React state libraries are built on it."

---

## 🔗 Related Questions
→ Q096 (event emitter) | Q098 (observable) | Q263 (observer pattern) | Q158 (complete pub/sub)
