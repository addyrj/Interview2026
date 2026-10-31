---

# Q238. IndexedDB Wrapper
# Category: DOM Questions
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Wrap the callback-based IndexedDB API into a small Promise-based class with `set(key, value)`, `get(key)`, `delete(key)`, `getAll()`.

---

## 💡 Quick Concept (2 lines only)
IndexedDB is an async, transactional, object-store database in the browser; wrap each `IDBRequest` in a Promise.
हिंदी: IndexedDB browser का async database है; हर request को Promise में लपेटकर async/await से use करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: open() creates DB + object store in onupgradeneeded
// Step 2: tx() helper runs an operation in a transaction
// Step 3: Public methods return Promises

class IDB {
  constructor(dbName = 'myDB', storeName = 'kv') {
    this.dbName = dbName;                                // database name
    this.storeName = storeName;                          // object store name
    this.dbPromise = this.open();                        // open once, reuse
  }

  open() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(this.dbName, 1);        // open version 1
      req.onupgradeneeded = () => {                      // first time / version bump
        req.result.createObjectStore(this.storeName);    // create store (out-of-line keys)
      };
      req.onsuccess = () => resolve(req.result);         // db ready
      req.onerror = () => reject(req.error);             // failed
    });
  }

  async tx(mode, fn) {
    const db = await this.dbPromise;                     // wait for db
    return new Promise((resolve, reject) => {
      const t = db.transaction(this.storeName, mode);    // start transaction
      const store = t.objectStore(this.storeName);       // get store
      const req = fn(store);                             // run operation -> IDBRequest
      t.oncomplete = () => resolve(req.result);          // resolve after commit
      t.onerror = () => reject(t.error);                 // transaction error
      t.onabort = () => reject(t.error);                 // aborted
    });
  }

  set(key, value) { return this.tx('readwrite', (s) => s.put(value, key)); } // insert/update
  get(key) { return this.tx('readonly', (s) => s.get(key)); }                // read one
  delete(key) { return this.tx('readwrite', (s) => s.delete(key)); }         // remove one
  getAll() { return this.tx('readonly', (s) => s.getAll()); }                // read all values
}

// ============================================
// TEST CASES
// ============================================

(async () => {
  const db = new IDB('testDB', 'items');                 // create wrapper
  await db.set('a', { n: 1 });                           // store object
  await db.set('b', [1, 2, 3]);                          // store array
  console.log(await db.get('a'));                        // Expected: { n: 1 }
  console.log(await db.getAll());                        // Expected: [ { n: 1 }, [1, 2, 3] ]
  await db.delete('a');                                  // remove key a
  console.log(await db.get('a'));                        // Expected: undefined
})();
// Verify in DevTools: Application tab -> IndexedDB -> testDB -> items
```

---

## 🔍 Why This Works (3 lines max)
Each operation runs inside a transaction, and we resolve on `oncomplete` so data is really committed. Caching `dbPromise` avoids reopening the database. IndexedDB stores structured-cloneable objects, files and blobs, unlike localStorage.
हिंदी: Transaction complete होने पर resolve करते हैं, इसलिए data पक्का save होता है।

---

## ⚡ Alternative Solution
```javascript
// Use the tiny "idb" library (Promise wrapper by Jake Archibald)
// import { openDB } from 'idb';
// const db = await openDB('myDB', 1, { upgrade(d) { d.createObjectStore('kv'); } });
// await db.put('kv', 'value', 'key');  // set
// await db.get('kv', 'key');           // get
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using the database/object store outside its transaction lifetime
// await fetch(...) inside a transaction -> transaction auto-commits and closes

// ✅ Correct: finish all IndexedDB work first, await other async work outside the transaction
```

---

## 🎯 Interview Tip (1 line)
Say: "IndexedDB is async, transactional, stores large structured data and works in workers; use it (or idb) instead of localStorage for big or offline data."

---

## 🔗 Related Questions
→ Q237 (localStorage wrapper) | Q239 (service worker basics) | Q185 (cache with TTL)
