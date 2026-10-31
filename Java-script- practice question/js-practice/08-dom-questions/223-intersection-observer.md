---

# Q223. Intersection Observer
# Category: DOM Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Use `IntersectionObserver` to add a class `visible` to every `.card` when at least 30% of it enters the viewport.
Stop observing an element once it has become visible.

---

## 💡 Quick Concept (2 lines only)
`IntersectionObserver` tells you asynchronously when an element enters or leaves the viewport, without scroll listeners.
हिंदी: `IntersectionObserver` बिना scroll event के बताता है कि element screen में आया या नहीं।

---

## ✅ Answer / Solution

```html
<div class="card">One</div>
<div class="card">Two</div>
<div class="card">Three</div>
```

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Create observer with callback + threshold option
// Step 2: In callback, check isIntersecting
// Step 3: Add class and unobserve to save work
// Step 4: Observe each .card

const observer = new IntersectionObserver(           // create the observer
  (entries, obs) => {                                // callback gets changed entries
    entries.forEach((entry) => {                     // loop each changed element
      if (entry.isIntersecting) {                    // is it in view?
        entry.target.classList.add('visible');       // reveal it
        obs.unobserve(entry.target);                 // stop watching it
      }
    });
  },
  { threshold: 0.3, rootMargin: '0px' }              // fire at 30% visibility
);

document.querySelectorAll('.card').forEach((card) => { // find all cards
  observer.observe(card);                              // start observing each
});

// ============================================
// TEST CASES
// ============================================

// Test 1: scroll until a card is 30% visible
//   -> Expected: card.classList.contains('visible') === true
// Test 2: scroll back up, then down again
//   -> Expected: no repeat callback (already unobserved)
// Test 3: Console: document.querySelectorAll('.card.visible').length
//   -> Expected: number of cards you have scrolled into view
```

---

## 🔍 Why This Works (3 lines max)
The browser computes intersection off the main thread and calls back only on changes. `threshold: 0.3` means fire when 30% is visible. `unobserve` avoids needless future callbacks.
हिंदी: Browser खुद visibility check करता है, इसलिए scroll listener से ज़्यादा fast और हल्का है।

---

## ⚡ Alternative Solution
```javascript
// Old way: scroll listener + getBoundingClientRect (heavier, causes reflow)
window.addEventListener('scroll', () => {            // runs on every scroll
  document.querySelectorAll('.card').forEach((c) => {
    const r = c.getBoundingClientRect();             // forces layout calc
    if (r.top < window.innerHeight) c.classList.add('visible'); // reveal
  });
});
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: checking entry without isIntersecting — fires also when leaving view
new IntersectionObserver((entries) => {
  entries.forEach((e) => e.target.classList.add('visible')); // adds on exit too
});

// ✅ Correct: check entry.isIntersecting first (see above)
```

---

## 🎯 Interview Tip (1 line)
Say: "IntersectionObserver is async and avoids layout thrashing from scroll+getBoundingClientRect; used for lazy loading, infinite scroll, and analytics."

---

## 🔗 Related Questions
→ Q226 (infinite scroll) | Q228 (lazy load images) | Q224 (mutation observer) | Q191 (lazy loader)
