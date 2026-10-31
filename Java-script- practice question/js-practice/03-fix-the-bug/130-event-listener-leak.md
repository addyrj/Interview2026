---

# Q130. Fix Event Listener Memory Leak
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Each `mount()` adds a listener but never removes it, so handlers pile up. Add proper cleanup.

```javascript
// BUGGY CODE:
function mount(emitter) {
  emitter.on('tick', () => console.log('tick'));  // anonymous, cannot be removed
}
// calling mount() 3 times -> 3 handlers fire per event
```

---

## 💡 Quick Concept (2 lines only)
Listeners keep their closures alive. Keep a reference to the handler and return an unsubscribe function that removes it.
हिंदी: handler का reference रखो और cleanup function से हटाओ, वरना listeners जमा होते रहते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

const EventEmitter = require('events');            // Step 1: Node's emitter

function mount(emitter) {
  const handler = () => console.log('tick');       // Step 2: named reference to the handler
  emitter.on('tick', handler);                     // add listener
  return () => emitter.off('tick', handler);       // Step 3 (FIX): return cleanup function
}

// ============================================
// TEST CASES
// ============================================

const em = new EventEmitter();
const unmount1 = mount(em);
const unmount2 = mount(em);
console.log(em.listenerCount('tick'));             // Expected: 2
unmount1();                                        // clean first
unmount2();                                        // clean second
console.log(em.listenerCount('tick'));             // Expected: 0
```

---

## 🔍 Why This Works (3 lines max)
`off` needs the exact same function reference that was passed to `on`. Returning a cleanup function lets callers (like React useEffect) release it on unmount.
हिंदी: `off` को वही function reference चाहिए जो `on` में दिया था, इसलिए cleanup function return करो।

---

## ⚡ Alternative Solution
```javascript
// AbortController (browser + Node 15+) removes listeners with one signal
const ac = new AbortController();
const target = new EventTarget();
target.addEventListener('x', () => console.log('x'), { signal: ac.signal });
ac.abort();                       // listener removed
target.dispatchEvent(new Event('x')); // prints nothing
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: new arrow each time, so removal does nothing
// el.addEventListener('click', () => go()); el.removeEventListener('click', () => go());
// ✅ Correct: same reference
// const h = () => go(); el.addEventListener('click', h); el.removeEventListener('click', h);
```

---

## 🎯 Interview Tip (1 line)
Say: "Every subscribe needs an unsubscribe — in React, return the cleanup from useEffect."

---

## 🔗 Related Questions
→ Q022 (this in event listener) | Q096 (event emitter) | Q125 (memory leak) | Q286 (efficient event listeners)
