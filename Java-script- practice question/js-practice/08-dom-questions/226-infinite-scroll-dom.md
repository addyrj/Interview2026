---

# Q226. Infinite Scroll DOM
# Category: DOM Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build infinite scroll: when the user reaches the bottom of `#feed`, load the next page of items and append them. Prevent duplicate loads while one is in flight.

---

## 💡 Quick Concept (2 lines only)
Place a sentinel element at the bottom and use `IntersectionObserver`; when it becomes visible, fetch and append the next page.
हिंदी: नीचे एक sentinel element रखो; जब वह दिखे तब अगला page load करके append करो।

---

## ✅ Answer / Solution

```html
<div id="feed"></div>
<div id="sentinel">Loading...</div>
```

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Keep page + loading flag
// Step 2: loadMore() fetches data and appends via DocumentFragment
// Step 3: Observer on sentinel triggers loadMore

const feed = document.getElementById('feed');            // list container
const sentinel = document.getElementById('sentinel');    // bottom marker
let page = 0;                                            // current page
let loading = false;                                     // guard against double load
const MAX_PAGES = 5;                                     // stop after 5 pages

function fakeFetch(p) {                                  // simulate API call
  return new Promise((resolve) => {
    setTimeout(() => resolve(Array.from({ length: 10 }, (_, i) => `Item ${p * 10 + i + 1}`)), 300);
  });
}

async function loadMore() {
  if (loading) return;                                   // already loading -> skip
  loading = true;                                        // lock
  const items = await fakeFetch(page);                   // get data
  const frag = document.createDocumentFragment();        // batch DOM writes
  items.forEach((text) => {                              // build each node
    const div = document.createElement('div');           // create row
    div.textContent = text;                              // set text
    frag.appendChild(div);                               // add to fragment
  });
  feed.appendChild(frag);                                // single DOM insertion
  page++;                                                // next page
  loading = false;                                       // unlock
  if (page >= MAX_PAGES) observer.disconnect();          // no more data
}

const observer = new IntersectionObserver((entries) => { // watch sentinel
  if (entries[0].isIntersecting) loadMore();             // visible -> load
}, { rootMargin: '200px' });                             // preload slightly early
observer.observe(sentinel);                              // start

// ============================================
// TEST CASES
// ============================================

// Test 1: open page            -> Expected: first 10 items ("Item 1".."Item 10")
// Test 2: scroll to bottom     -> Expected: feed.children.length becomes 20
// Test 3: after 5 pages        -> Expected: feed.children.length === 50, no more loading
```

---

## 🔍 Why This Works (3 lines max)
The sentinel only intersects at the bottom, so there is no scroll polling. The `loading` flag stops duplicate calls and a fragment gives one reflow per page. After the last page we disconnect.
हिंदी: `loading` flag double-load रोकता है, और fragment से DOM एक ही बार में update होता है।

---

## ⚡ Alternative Solution
```javascript
// Scroll listener version (simpler, but runs on every scroll)
window.addEventListener('scroll', () => {
  const nearBottom = window.innerHeight + window.scrollY >= document.body.offsetHeight - 200; // 200px from end
  if (nearBottom) loadMore();                            // load when close
});
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: no loading guard -> same page requested many times
// observer callback calls fetch on every intersect event

// ✅ Correct: use `loading` flag and increment page only after success
```

---

## 🎯 Interview Tip (1 line)
Say: "I'd use IntersectionObserver with a sentinel, a loading guard, and mention virtualization for very long lists."

---

## 🔗 Related Questions
→ Q182 (infinite scroll logic) | Q223 (intersection observer) | Q227 (virtual scroll)
