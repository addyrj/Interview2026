---

# Q187. Build Event Bus
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a global `EventBus` so unrelated modules/components can communicate: `on`, `once`, `off`, `emit`. `on` should return an unsubscribe function.

```javascript
const unsub = bus.on('login', user => console.log(user));
bus.emit('login', { name: 'Adi' });
unsub();
```

---

## 💡 Quick Concept (2 lines only)
A map of `eventName -> Set of handlers`; `emit` calls every handler with the payload.
हिंदी: Event के नाम पर handlers जमा करो और emit पर सबको call करो — modules आपस में decoupled रहते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

class EventBus {
  constructor() {
    this.handlers = new Map();                   // Step 1: event -> Set(handlers)
  }

  on(event, handler) {
    if (!this.handlers.has(event)) this.handlers.set(event, new Set()); // Step 2: create set
    this.handlers.get(event).add(handler);       // register handler
    return () => this.off(event, handler);       // Step 3: return unsubscribe fn
  }

  once(event, handler) {
    const wrapper = (...args) => {               // wrapper removes itself after first call
      this.off(event, wrapper);                  // unsubscribe first
      handler(...args);                          // then run handler
    };
    return this.on(event, wrapper);              // register wrapper
  }

  off(event, handler) {
    this.handlers.get(event)?.delete(handler);   // remove handler if present
  }

  emit(event, ...args) {
    const set = this.handlers.get(event);        // Step 4: find handlers
    if (!set) return false;                      // nobody listening
    [...set].forEach((h) => h(...args));         // copy so off() inside handler is safe
    return true;                                 // delivered
  }
}

// ============================================
// TEST CASES
// ============================================

const bus = new EventBus();
const unsub = bus.on('login', (u) => console.log('A got', u.name)); // permanent listener
bus.once('login', (u) => console.log('B once', u.name));            // one-time listener

bus.emit('login', { name: 'Adi' });              // Expected: A got Adi  then  B once Adi
bus.emit('login', { name: 'Raj' });              // Expected: A got Raj
unsub();                                         // remove A
console.log(bus.emit('login', { name: 'Sam' })); // Expected: true (set exists, but no handlers run)
console.log(bus.emit('logout'));                 // Expected: false
```

---

## 🔍 Why This Works (3 lines max)
A `Set` prevents duplicate handlers and gives O(1) removal. Returning an unsubscribe function makes cleanup (e.g. React `useEffect`) trivial.
हिंदी: Set से duplicate नहीं होते, और unsubscribe function से cleanup आसान हो जाता है।

---

## ⚡ Alternative Solution
```javascript
// Browser-native: EventTarget + CustomEvent
const target = new EventTarget();                // built-in bus
target.addEventListener('ping', (e) => console.log(e.detail)); // listen
target.dispatchEvent(new CustomEvent('ping', { detail: 42 })); // emit -> 42
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: anonymous handler can never be removed -> memory leak
bus.on('x', () => doStuff());
bus.off('x', () => doStuff());   // different function reference!

// ✅ Correct: keep the reference or use the returned unsubscribe
const off = bus.on('x', () => doStuff());
off();
```

---

## 🎯 Interview Tip (1 line)
Mention memory leaks from forgotten listeners and when a bus becomes spaghetti (prefer a store for shared state).

---

## 🔗 Related Questions
→ Q096 (event emitter) | Q097 (pub/sub) | Q151 (complete event emitter) | Q273 (pub/sub pattern)
