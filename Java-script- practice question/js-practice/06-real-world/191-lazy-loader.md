---

# Q191. Build Lazy Loader
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a lazy loader: elements are loaded (e.g. `data-src` copied to `src`) only when they enter the viewport, and each element is loaded once. Inject the observer class so the logic runs in Node.

```javascript
const lazy = createLazyLoader(IntersectionObserver, (el) => { el.src = el.dataset.src; });
document.querySelectorAll('img[data-src]').forEach(lazy.watch);
```

---

## 💡 Quick Concept (2 lines only)
Observe each element; when `isIntersecting` is true, run `load(el)` and `unobserve` it so it never loads twice.
हिंदी: Element screen में आते ही उसे load करो और observe करना बंद कर दो — बाकी सब तब तक रुके रहते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function createLazyLoader(ObserverCtor, load, options = { rootMargin: '100px' }) {
  const observer = new ObserverCtor((entries, obs) => { // Step 1: callback gets visibility entries
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;         // Step 2: skip elements still off-screen
      load(entry.target);                        // Step 3: do the real loading
      obs.unobserve(entry.target);               // Step 4: never load again
    });
  }, options);

  return {
    watch: (el) => observer.observe(el),         // start watching an element
    disconnect: () => observer.disconnect(),     // stop everything (cleanup)
  };
}

// ============================================
// TEST CASES
// ============================================

// Fake IntersectionObserver so we can simulate scrolling in Node
class FakeObserver {
  constructor(cb) { this.cb = cb; this.targets = new Set(); }  // keep callback + targets
  observe(el) { this.targets.add(el); }          // track
  unobserve(el) { this.targets.delete(el); }     // untrack
  disconnect() { this.targets.clear(); }         // clear all
  trigger(el, isIntersecting) { this.cb([{ target: el, isIntersecting }], this); } // simulate scroll
}

let observerInstance;                            // capture the fake instance
class Capturing extends FakeObserver {
  constructor(cb, opts) { super(cb, opts); observerInstance = this; }
}

const loaded = [];                               // record loaded ids
const lazy = createLazyLoader(Capturing, (el) => loaded.push(el.id));
const a = { id: 'img-a' }, b = { id: 'img-b' };  // fake elements
lazy.watch(a); lazy.watch(b);

observerInstance.trigger(a, false);              // a not visible yet
console.log(loaded);                             // Expected: []
observerInstance.trigger(a, true);               // a scrolls into view
console.log(loaded);                             // Expected: [ 'img-a' ]
console.log(observerInstance.targets.size);      // Expected: 1 (a is unobserved, b remains)
```

---

## 🔍 Why This Works (3 lines max)
The browser tells us when an element becomes visible, so no scroll listeners or layout math are needed. Unobserving after load avoids repeated work.
हिंदी: Browser खुद बताता है कि element दिख रहा है; load के बाद unobserve करने से दोबारा काम नहीं होता।

---

## ⚡ Alternative Solution
```javascript
// Native lazy loading — zero JS for images/iframes
// <img src="photo.jpg" loading="lazy" alt="photo">
// Dynamic import for components:
const Chart = () => import('./Chart.js');        // loaded only when called
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: scroll listener running getBoundingClientRect on every item, every scroll
window.onscroll = () => imgs.forEach((i) => i.getBoundingClientRect().top < innerHeight && load(i));

// ✅ Correct: IntersectionObserver + unobserve after load
```

---

## 🎯 Interview Tip (1 line)
Mention IntersectionObserver, `rootMargin` for preloading slightly early, and `loading="lazy"`.

---

## 🔗 Related Questions
→ Q182 (infinite scroll) | Q192 (image preloader) | Q223 (intersection observer) | Q228 (lazy load images)
