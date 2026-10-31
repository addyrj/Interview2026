---

# Q263. Observer Pattern
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a `Subject` with `subscribe`, `unsubscribe` and `notify`. Observers get notified when state changes.

---

## 💡 Quick Concept (2 lines only)
A subject keeps a list of observers and calls each one when something changes (one-to-many).
हिंदी: Subject बदलते ही अपने सारे observers को खुद खबर देता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Store observers in a Set
// Step 2: subscribe adds, unsubscribe removes
// Step 3: notify calls every observer with new data

class Subject {
  #observers = new Set();                        // Set avoids duplicate subscriptions

  subscribe(fn) {
    this.#observers.add(fn);                     // add observer
    return () => this.unsubscribe(fn);           // return a cleanup function
  }

  unsubscribe(fn) {
    this.#observers.delete(fn);                  // remove observer
  }

  notify(data) {
    this.#observers.forEach((fn) => fn(data));   // push data to all observers
  }
}

// ============================================
// TEST CASES
// ============================================

const news = new Subject();                              // create subject
const off = news.subscribe((d) => console.log('A got', d)); // observer A
news.subscribe((d) => console.log('B got', d));          // observer B
news.notify('hello');                                    // Expected: A got hello
                                                         // Expected: B got hello
off();                                                   // A unsubscribes
news.notify('bye');                                      // Expected: B got bye
```

---

## 🔍 Why This Works (3 lines max)
Subject and observers only share a function signature, so they are loosely coupled. Returning an unsubscribe function makes cleanup easy.
हिंदी: Subject को observers की details नहीं पता, बस function call करता है।

---

## ⚡ Alternative Solution
```javascript
// Using Node's built-in EventEmitter
const { EventEmitter } = require('events');   // import emitter
const em = new EventEmitter();                // create
em.on('tick', (n) => console.log('tick', n)); // observe
em.emit('tick', 1);                           // Expected: tick 1
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: never unsubscribing → memory leak, stale callbacks fire
// subject.subscribe(handler);  // component unmounted but handler remains

// ✅ Correct: keep the returned unsubscribe and call it on cleanup
```

---

## 🎯 Interview Tip (1 line)
Distinguish Observer (subject knows observers) from Pub/Sub (broker in between) — see Q273.

---

## 🔗 Related Questions
→ Q273 (Pub/Sub) | Q096 (Event emitter) | Q098 (Observable)
