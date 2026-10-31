---

# Q237. localStorage Wrapper
# Category: DOM Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write a `storage` wrapper around `localStorage` that: stores/reads JSON safely, supports default values, optional expiry (TTL), a namespace prefix, and never throws.

---

## 💡 Quick Concept (2 lines only)
localStorage stores only strings, so wrap values with `JSON.stringify/parse` and add try/catch for quota and private-mode errors.
हिंदी: localStorage सिर्फ़ string रखता है, इसलिए JSON convert करो और errors के लिए try/catch लगाओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Factory with namespace prefix
// Step 2: set stores { value, expires } as JSON
// Step 3: get parses, checks expiry, returns fallback on any problem

function createStorage(namespace = 'app') {
  const k = (key) => `${namespace}:${key}`;              // build prefixed key

  return {
    set(key, value, ttlMs) {
      try {
        const item = {
          value,                                         // actual data
          expires: ttlMs ? Date.now() + ttlMs : null,    // expiry timestamp or null
        };
        localStorage.setItem(k(key), JSON.stringify(item)); // save as string
        return true;                                     // success
      } catch (e) {
        return false;                                    // quota full / blocked
      }
    },
    get(key, fallback = null) {
      try {
        const raw = localStorage.getItem(k(key));        // read string
        if (raw === null) return fallback;               // missing key
        const item = JSON.parse(raw);                    // parse JSON
        if (item.expires && Date.now() > item.expires) { // expired?
          localStorage.removeItem(k(key));               // delete it
          return fallback;                               // return default
        }
        return item.value;                               // valid value
      } catch (e) {
        return fallback;                                 // corrupted JSON / blocked
      }
    },
    remove(key) {
      try { localStorage.removeItem(k(key)); } catch (e) { /* ignore */ } // safe delete
    },
    clear() {
      try {
        Object.keys(localStorage)                        // all keys
          .filter((x) => x.startsWith(namespace + ':'))  // only our namespace
          .forEach((x) => localStorage.removeItem(x));   // remove each
      } catch (e) { /* ignore */ }
    },
  };
}

// ============================================
// TEST CASES
// ============================================

const storage = createStorage('demo');                   // namespaced storage
storage.set('user', { name: 'Aditya', age: 25 });        // store object
console.log(storage.get('user'));                        // Expected: { name: 'Aditya', age: 25 }
console.log(storage.get('missing', 'default'));          // Expected: 'default'
storage.set('token', 'abc', 100);                        // 100ms TTL
setTimeout(() => console.log(storage.get('token')), 200); // Expected: null (expired)
localStorage.setItem('demo:bad', '{oops');               // corrupt JSON manually
console.log(storage.get('bad', 'safe'));                 // Expected: 'safe' (no throw)
storage.clear();                                         // remove only demo:* keys
```

---

## 🔍 Why This Works (3 lines max)
Wrapping each value in `{ value, expires }` allows TTL without extra keys. try/catch handles `QuotaExceededError`, disabled storage and bad JSON. A namespace prevents clashes with other keys.
हिंदी: `{ value, expires }` में रखने से TTL मिलता है, और try/catch से कभी crash नहीं होता।

---

## ⚡ Alternative Solution
```javascript
// Minimal version without TTL
const ls = {
  get: (k, d = null) => { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } }, // safe read
  set: (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },                         // safe write
};
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: storing object directly -> saved as "[object Object]"
localStorage.setItem('user', { name: 'A' });

// ✅ Correct: JSON.stringify on write, JSON.parse on read
localStorage.setItem('user', JSON.stringify({ name: 'A' }));
```

---

## 🎯 Interview Tip (1 line)
Say: "localStorage is sync, string-only, ~5MB, same-origin, and never for secrets; sessionStorage is per-tab; large data belongs in IndexedDB."

---

## 🔗 Related Questions
→ Q195 (local storage wrapper) | Q185 (cache with TTL) | Q238 (IndexedDB wrapper) | Q231 (dark mode)
