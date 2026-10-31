---

# Q195. Build Local Storage Wrapper
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a safe `createStorage(storage, namespace)` wrapper over `localStorage`: auto JSON serialize/parse, key prefix, optional expiry (`ttl`), and no crashes if storage is full/unavailable or JSON is corrupt. Inject `storage` for Node testing.

```javascript
const store = createStorage(window.localStorage, 'app');
store.set('user', { id: 1 }, 60000);
```

---

## 💡 Quick Concept (2 lines only)
`localStorage` only stores strings: wrap values with `JSON.stringify`/`parse`, store `{ value, expiresAt }`, and put everything in try/catch.
हिंदी: localStorage सिर्फ string रखता है — JSON में बदलो, expiry जोड़ो और try/catch से सुरक्षित रखो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function createStorage(storage, namespace = 'app', now = () => Date.now()) {
  const k = (key) => `${namespace}:${key}`;      // Step 1: prefix avoids key collisions

  return {
    set(key, value, ttl) {
      try {
        const record = { value, expiresAt: ttl ? now() + ttl : null }; // Step 2: wrap with expiry
        storage.setItem(k(key), JSON.stringify(record)); // serialize
        return true;                             // saved
      } catch { return false; }                  // quota exceeded / private mode
    },
    get(key, fallback = null) {
      try {
        const raw = storage.getItem(k(key));     // Step 3: read string
        if (raw === null) return fallback;       // missing
        const { value, expiresAt } = JSON.parse(raw); // parse (may throw if corrupt)
        if (expiresAt && now() >= expiresAt) {   // Step 4: expired?
          storage.removeItem(k(key));            // cleanup
          return fallback;
        }
        return value;                            // fresh value
      } catch { return fallback; }               // corrupt JSON -> fallback
    },
    remove(key) { storage.removeItem(k(key)); }, // delete one key
    clear() {                                    // delete only OUR namespace
      Object.keys(storage).filter((x) => x.startsWith(`${namespace}:`)).forEach((x) => storage.removeItem(x));
    },
  };
}

// ============================================
// TEST CASES
// ============================================

// Fake localStorage for Node
const fake = {
  setItem(key, v) { this[key] = String(v); },    // store as string like real one
  getItem(key) { return key in this ? this[key] : null; },
  removeItem(key) { delete this[key]; },
};

let time = 0;                                    // fake clock
const store = createStorage(fake, 'app', () => time);
store.set('user', { id: 1, name: 'Adi' });
console.log(store.get('user'));                  // Expected: { id: 1, name: 'Adi' }

store.set('token', 'abc', 1000);                 // expires in 1s
console.log(store.get('token'));                 // Expected: abc
time = 1500;                                     // 1.5s later
console.log(store.get('token', 'gone'));         // Expected: gone

fake['app:bad'] = '{not json';                   // corrupt data
console.log(store.get('bad', 'safe'));           // Expected: safe
store.clear();
console.log(store.get('user'));                  // Expected: null
```

---

## 🔍 Why This Works (3 lines max)
JSON wrapping preserves types, the namespace stops collisions, and try/catch converts every failure into a harmless fallback. Expiry is checked lazily on read.
हिंदी: JSON से types बचते हैं, prefix से टकराव नहीं होता, और try/catch से app crash नहीं होता।

---

## ⚡ Alternative Solution
```javascript
// Minimal typed helpers
const save = (k, v) => localStorage.setItem(k, JSON.stringify(v));    // write
const load = (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } }; // read
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: storing objects directly -> saved as "[object Object]"
localStorage.setItem('user', { id: 1 });

// ✅ Correct: serialize first (and never store secrets/tokens you can't afford to leak to XSS)
localStorage.setItem('user', JSON.stringify({ id: 1 }));
```

---

## 🎯 Interview Tip (1 line)
Mention ~5MB limit, synchronous blocking API, string-only values, and XSS risk for tokens.

---

## 🔗 Related Questions
→ Q185 (cache with TTL) | Q196 (cookie manager) | Q237 (localStorage wrapper) | Q238 (IndexedDB wrapper)
