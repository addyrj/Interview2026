---

# Q308. Debounce Real Use Case
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Explain debounce with a real-world use case. Build a working search input with debounce. How is it different from throttle?

---

## 💡 Quick Concept (2 lines only)
Debounce: delays function call until user STOPS doing something for N milliseconds. Used for search inputs — don't call API on every keystroke, only when user pauses.
हिंदी: Debounce user के रुकने का इंतज़ार करता है — हर keystroke पर API call नहीं, pause के बाद एक call।

---

## ✅ Answer / Solution

```javascript
// ============================================
// REAL USE CASE: Search Input
// ============================================

// PROBLEM WITHOUT DEBOUNCE:
// User types "react hooks" = 10 characters = 10 API calls!
// Every keystroke fires searchAPI

// SOLUTION WITH DEBOUNCE:
// Wait until user stops typing for 300ms, THEN call API
// "react hooks" → only 1 API call (300ms after last keystroke)

function debounce(fn, delay) {
  let timerId;
  return function(...args) {
    clearTimeout(timerId);
    timerId = setTimeout(() => fn.apply(this, args), delay);
  };
}

// ─── Browser Example ─────────────────────────────────────────
function searchProducts(query) {
  if (!query.trim()) return;
  
  // API call — only fires 300ms after user stops typing
  fetch(`/api/search?q=${encodeURIComponent(query)}`)
    .then(res => res.json())
    .then(results => displayResults(results))
    .catch(err => console.error('Search failed:', err));
}

const debouncedSearch = debounce(searchProducts, 300);
document.getElementById('search').addEventListener('input', (e) => {
  debouncedSearch(e.target.value);
});

// ─── Node.js/React Example ───────────────────────────────────
// React hook version:
function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = React.useState(value);
  
  React.useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);  // cleanup on new value
  }, [value, delay]);
  
  return debouncedValue;
}

// Usage in component:
function SearchBar() {
  const [query, setQuery] = React.useState('');
  const debouncedQuery = useDebounce(query, 300);
  
  React.useEffect(() => {
    if (debouncedQuery) {
      fetch(`/api/search?q=${debouncedQuery}`)
        .then(/* ... */);
    }
  }, [debouncedQuery]);  // only fires when debounced value changes
  
  return <input value={query} onChange={e => setQuery(e.target.value)} />;
}

// ============================================
// TEST CASES
// ============================================

const mockAPI = debounce((query) => {
  console.log(`API called with: "${query}" at ${Date.now()}`);
}, 300);

mockAPI('r');      // timer set
mockAPI('re');     // timer reset
mockAPI('rea');    // timer reset
mockAPI('reac');   // timer reset
mockAPI('react');  // timer set
// After 300ms:
// Expected: API called with: "react" at [timestamp]
// (only 1 call, not 5!)

// ─── DEBOUNCE vs THROTTLE ─────────────────────────────────────
/*
DEBOUNCE:
- Fires AFTER a pause in activity
- Use: search inputs, form validation, resize recalculation
- "User stopped → now act"
- If calls: ABCDEFG... → waits for pause → one call with last value

THROTTLE:
- Fires AT MOST once per N milliseconds
- Use: scroll handlers, mouse position tracking, resize
- "Keep firing but limit rate"
- If calls: ABCDEFG... → A fires, BCDEF ignored, G fires (if N ms passed)
*/
```

---

## 🔍 Why This Works (3 lines max)
Each keystroke clears the previous timer and sets a new 300ms one. Only the LAST keystroke's timer completes without being cancelled. React's `useDebounce` hook applies the same logic to React state.
हिंदी: हर keystroke पिछला timer cancel करता है — सिर्फ last keystroke के बाद 300ms में API call होती है।

---

## ⚡ Alternative Solution
```javascript
// lodash debounce (production-ready, more options):
import debounce from 'lodash/debounce';

const debouncedSearch = debounce(searchAPI, 300, {
  leading: false,  // don't fire on first call
  trailing: true,  // fire after delay (default)
  maxWait: 1000    // fire at most every 1 second (like throttle)
});

// For React with useCallback (prevent new function on every render):
const debouncedSearch = React.useCallback(
  debounce((query) => searchAPI(query), 300),
  []  // create once
);
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: creating new debounced function on every render
function SearchBar() {
  // WRONG: creates new debounce instance on every render → loses state
  const handleSearch = debounce(searchAPI, 300);
  return <input onChange={e => handleSearch(e.target.value)} />;
}

// ✅ Correct: create once (useCallback or useMemo)
function SearchBar() {
  const handleSearch = React.useCallback(
    debounce(searchAPI, 300),
    []
  );
  return <input onChange={e => handleSearch(e.target.value)} />;
}

// ❌ Wrong: using throttle when debounce is needed
// For search: throttle fires every 300ms while typing — still many API calls
// For search: debounce waits until user STOPS — better UX and fewer calls
```

---

## 🎯 Interview Tip (1 line)
Say: "Debounce fires after pause (search/validation); throttle fires periodically (scroll/resize); both reduce expensive operations — debounce waits for silence."

---

## 🔗 Related Questions
→ Q081 (debounce implementation) | Q082 (throttle) | Q181 (search with debounce) | Q309 (throttle use case)
