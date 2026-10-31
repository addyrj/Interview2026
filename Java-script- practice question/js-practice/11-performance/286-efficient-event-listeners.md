---

# Q286. Efficient Event Listeners
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Handle clicks on 1,000 list items using ONE delegated listener instead of 1,000, and show how `once` and `AbortController` keep listeners tidy. (Uses Node's EventTarget plus a tiny fake event.)

---

## 💡 Quick Concept (2 lines only)
Attach one listener to a parent (event delegation) and inspect `event.target`, instead of one listener per child.
हिंदी: हर child पर listener लगाने के बजाय parent पर एक listener लगाओ और target देखो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: One listener on the parent
// Step 2: Read which child was hit from event.detail (stand-in for event.target)
// Step 3: Clean up with once / AbortController

const { getEventListeners } = require('events');   // Node helper to count listeners

const list = new EventTarget();                    // stand-in for <ul>
const clicked = [];                                // records handled ids

list.addEventListener('click', (e) => {            // ONE delegated handler
  const id = e.detail.id;                          // which "li" was clicked (browser: e.target.closest('li'))
  clicked.push(id);                                // handle it
});

for (let i = 1; i <= 1000; i++) {                  // 1000 "items" need no own listener
  if (i === 7 || i === 500) list.dispatchEvent(new CustomEvent('click', { detail: { id: i } })); // simulate clicks
}

// once: auto-removed after first call
const btn = new EventTarget();                     // stand-in for a button
let onceCount = 0;                                 // counter
btn.addEventListener('go', () => onceCount++, { once: true }); // fires once only

// AbortController: remove many at once
const ac = new AbortController();                  // controller
btn.addEventListener('a', () => {}, { signal: ac.signal }); // tied to signal
btn.addEventListener('b', () => {}, { signal: ac.signal }); // tied to signal

// ============================================
// TEST CASES
// ============================================

console.log(getEventListeners(list, 'click').length); // Expected: 1
console.log(clicked);                                 // Expected: [ 7, 500 ]
btn.dispatchEvent(new Event('go'));                   // first dispatch
btn.dispatchEvent(new Event('go'));                   // second dispatch ignored
console.log(onceCount);                               // Expected: 1
console.log(getEventListeners(btn, 'a').length);      // Expected: 1
ac.abort();                                           // remove both
console.log(getEventListeners(btn, 'a').length);      // Expected: 0
```

---

## 🔍 Why This Works (3 lines max)
Events bubble up, so a single parent handler sees events from every child, including ones added later. `once` and `signal` guarantee removal without keeping references.
हिंदी: Event ऊपर bubble होता है, इसलिए parent का एक listener सभी children को संभाल लेता है।

---

## ⚡ Alternative Solution
```javascript
// Browser delegation with closest() and passive scroll listener
// ul.addEventListener('click', (e) => {
//   const li = e.target.closest('li');       // find clicked item
//   if (li && ul.contains(li)) handle(li.dataset.id);
// });
// window.addEventListener('scroll', onScroll, { passive: true }); // never blocks scrolling
console.log('browser snippet'); // Expected: browser snippet
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: items.forEach((li) => li.addEventListener('click', fn)); // N listeners, lost on re-render
// ✅ Correct: one delegated listener on the stable parent
```

---

## 🎯 Interview Tip (1 line)
Mention delegation, `{ passive: true }`, `{ once: true }`, and removing listeners on unmount.

---

## 🔗 Related Questions
→ Q221 (Event delegation) | Q310 (Bubbling vs capturing) | Q282 (Avoid memory leaks)
