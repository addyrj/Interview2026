---

# Q182. Build Infinite Scroll Logic
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build the core logic of infinite scroll: when the user scrolls near the bottom, load the next page — never load twice at once, and stop when no more data exists. Keep it DOM-free so it is testable.

```javascript
const scroller = createInfiniteScroll(fetchPage, appendItems);
window.addEventListener('scroll', () => scroller.onScroll({ scrollTop, clientHeight, scrollHeight }));
```

---

## 💡 Quick Concept (2 lines only)
Check `scrollTop + clientHeight >= scrollHeight - threshold`, guard with a `loading` flag, track `page` and `hasMore`.
हिंदी: Bottom के पास पहुँचते ही अगला page लोड करो — loading flag से double call रोको।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function createInfiniteScroll(fetchPage, onAppend, threshold = 100) {
  let page = 1;                                  // Step 1: next page to load
  let loading = false;                           // guard against parallel loads
  let hasMore = true;                            // stops when server has no more

  async function loadMore() {
    if (loading || !hasMore) return;             // Step 2: ignore if busy / finished
    loading = true;                              // lock
    try {
      const items = await fetchPage(page);       // Step 3: fetch current page
      if (items.length === 0) hasMore = false;   // empty page -> end of data
      else { onAppend(items); page++; }          // append and advance page
    } finally {
      loading = false;                           // always unlock
    }
  }

  function onScroll({ scrollTop, clientHeight, scrollHeight }) {
    const nearBottom = scrollTop + clientHeight >= scrollHeight - threshold; // Step 4
    if (nearBottom) return loadMore();           // trigger load
  }

  return { onScroll, loadMore };                 // public API
}

// ============================================
// TEST CASES
// ============================================

const pages = { 1: ['a', 'b'], 2: ['c', 'd'], 3: [] }; // fake server data
const fetchPage = (p) => new Promise((r) => setTimeout(() => r(pages[p] || []), 10));
const s = createInfiniteScroll(fetchPage, (items) => console.log('append', items));

(async () => {
  await s.onScroll({ scrollTop: 0, clientHeight: 500, scrollHeight: 2000 });   // far from bottom -> nothing
  const p1 = s.onScroll({ scrollTop: 1450, clientHeight: 500, scrollHeight: 2000 }); // near bottom
  s.onScroll({ scrollTop: 1460, clientHeight: 500, scrollHeight: 2000 });       // ignored (loading)
  await p1;                                      // Expected: append [ 'a', 'b' ]
  await s.onScroll({ scrollTop: 1500, clientHeight: 500, scrollHeight: 2000 }); // Expected: append [ 'c', 'd' ]
  await s.onScroll({ scrollTop: 1500, clientHeight: 500, scrollHeight: 2000 }); // empty page -> hasMore=false
  await s.onScroll({ scrollTop: 1500, clientHeight: 500, scrollHeight: 2000 }); // nothing more happens
  console.log('done');                           // Expected: done
})();
```

---

## 🔍 Why This Works (3 lines max)
The scroll check is pure math, so no DOM is needed. The `loading` flag prevents duplicate fetches while scroll events fire rapidly; `hasMore` stops useless calls.
हिंदी: Scroll का हिसाब सिर्फ math है; flag double fetch रोकता है और hasMore अंत पर रुकता है।

---

## ⚡ Alternative Solution
```javascript
// Browser: IntersectionObserver on a sentinel element (no scroll listener)
const sentinel = document.querySelector('#sentinel');       // empty div at list end
new IntersectionObserver(([entry]) => {
  if (entry.isIntersecting) scroller.loadMore();            // sentinel visible -> load
}).observe(sentinel);
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: no loading guard -> same page fetched many times while scrolling
if (nearBottom) { fetchPage(page).then(append); page++; }

// ✅ Correct: lock with `loading`, advance page only after success
if (nearBottom && !loading) { loading = true; /* fetch, append, page++, loading=false */ }
```

---

## 🎯 Interview Tip (1 line)
Mention IntersectionObserver over scroll listeners, plus loading/hasMore guards and throttling.

---

## 🔗 Related Questions
→ Q083 (throttle) | Q223 (intersection observer) | Q226 (infinite scroll DOM) | Q227 (virtual scroll)
