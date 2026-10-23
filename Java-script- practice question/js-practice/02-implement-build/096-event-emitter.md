---

# Q096. Implement Event Emitter
# Category: Implement / Build
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement an `EventEmitter` class with:
- `on(event, listener)` — subscribe to an event
- `off(event, listener)` — unsubscribe
- `emit(event, ...args)` — trigger all listeners for an event
- `once(event, listener)` — listen once then auto-remove

```javascript
const emitter = new EventEmitter();
emitter.on('login', (user) => console.log(`${user} logged in`));
emitter.emit('login', 'Arjun');  // 'Arjun logged in'
```

---

## 💡 Quick Concept (2 lines only)
Observer pattern: listeners register for events, emitter notifies all listeners when event fires. Node.js EventEmitter is built on this exact pattern.
हिंदी: Observer pattern — listeners events subscribe करते हैं, emit होने पर सब notify होते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

class EventEmitter {
  constructor() {
    this.events = {};  // Step 1: store events as { eventName: [listeners] }
  }
  
  // Subscribe to event
  on(event, listener) {
    if (!this.events[event]) {
      this.events[event] = [];  // Step 2: create array for new event
    }
    this.events[event].push(listener);  // Step 3: add listener
    return this;  // enable chaining: emitter.on('a', fn).on('b', fn2)
  }
  
  // Unsubscribe from event
  off(event, listener) {
    if (!this.events[event]) return this;
    
    this.events[event] = this.events[event].filter(
      fn => fn !== listener  // Step 4: remove matching listener
    );
    return this;
  }
  
  // Emit event — call all listeners
  emit(event, ...args) {
    if (!this.events[event]) return false;
    
    this.events[event].forEach(listener => {
      listener.apply(this, args);  // Step 5: call each listener with args
    });
    return true;
  }
  
  // Subscribe once — auto-remove after first call
  once(event, listener) {
    const wrapper = (...args) => {
      listener.apply(this, args);  // Step 6: call original listener
      this.off(event, wrapper);    // Step 7: remove wrapper after calling
    };
    wrapper._original = listener;  // store ref for off() by original function
    this.on(event, wrapper);
    return this;
  }
  
  // Get listener count (bonus)
  listenerCount(event) {
    return this.events[event] ? this.events[event].length : 0;
  }
  
  // Remove all listeners for an event
  removeAllListeners(event) {
    if (event) {
      delete this.events[event];
    } else {
      this.events = {};
    }
    return this;
  }
}

// ============================================
// TEST CASES
// ============================================

const emitter = new EventEmitter();

// Basic on/emit:
emitter.on('login', (user) => console.log(`${user} logged in`));
emitter.on('login', (user) => console.log(`Welcome, ${user}!`));
emitter.emit('login', 'Arjun');
// Expected: "Arjun logged in", "Welcome, Arjun!"

// Multiple args:
emitter.on('purchase', (item, price) => console.log(`${item}: ₹${price}`));
emitter.emit('purchase', 'Phone', 499);
// Expected: "Phone: ₹499"

// once:
let count = 0;
emitter.once('increment', () => count++);
emitter.emit('increment');  // count = 1
emitter.emit('increment');  // ignored — listener removed
console.log(count);  // Expected: 1

// off:
const handler = () => console.log('message received');
emitter.on('message', handler);
emitter.emit('message');   // fires
emitter.off('message', handler);
emitter.emit('message');   // nothing — listener removed

// Chaining:
emitter
  .on('data', d => console.log('Handler 1:', d))
  .on('data', d => console.log('Handler 2:', d))
  .emit('data', 'hello');
// Expected: "Handler 1: hello", "Handler 2: hello"
```

---

## 🔍 Why This Works (3 lines max)
Map event names to arrays of listeners. `on` adds, `off` filters out, `emit` calls all. `once` wraps the listener to auto-remove itself after first call.
हिंदी: Events का map रखो listeners के साथ — `on` add करे, `off` remove करे, `emit` सब call करे।

---

## ⚡ Alternative Solution
```javascript
// Using Map for better performance with many events:
class EventEmitter2 {
  #events = new Map();  // private field (ES2022)
  
  on(event, fn) {
    if (!this.#events.has(event)) this.#events.set(event, new Set());
    this.#events.get(event).add(fn);  // Set prevents duplicate listeners
    return () => this.off(event, fn);  // return unsubscribe function
  }
  
  off(event, fn) {
    this.#events.get(event)?.delete(fn);
  }
  
  emit(event, ...args) {
    this.#events.get(event)?.forEach(fn => fn(...args));
  }
  
  once(event, fn) {
    const off = this.on(event, (...args) => { fn(...args); off(); });
  }
}

// Real-world: Node.js EventEmitter (built-in):
const EventEmitter = require('events');
const myEmitter = new EventEmitter();

myEmitter.on('event', () => console.log('event fired!'));
myEmitter.emit('event');
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: once() listener stays after first call
once(event, listener) {
  this.on(event, listener);  // wrong — doesn't auto-remove!
}

// ✅ Correct: wrap in function that removes itself
once(event, listener) {
  const wrapper = (...args) => {
    listener(...args);
    this.off(event, wrapper);  // remove wrapper, not listener!
  };
  this.on(event, wrapper);
}

// ❌ Wrong: modifying events array while iterating during emit
emit(event, ...args) {
  this.events[event].forEach(fn => fn(...args));
  // If fn calls off() → mutates array during forEach → skip/double-call bugs
}
// ✅ Snapshot the array first:
emit(event, ...args) {
  const listeners = [...(this.events[event] || [])];
  listeners.forEach(fn => fn.apply(this, args));
}
```

---

## 🎯 Interview Tip (1 line)
Say: "EventEmitter is Observer pattern — store listeners in map, emit calls all; Node.js built-in works same way; React uses SyntheticEvents on a similar model."

---

## 🔗 Related Questions
→ Q097 (pub/sub) | Q263 (Observer pattern) | Q187 (build event bus)
