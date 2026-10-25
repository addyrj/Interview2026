# 158. localStorage + sessionStorage
# हिंदी में: localStorage + sessionStorage — Browser में Data Store करना

---

## 🔵 Simple Definition (English)
`localStorage` and `sessionStorage` are browser APIs that save small key-value string data on the user's device. `localStorage` stays after the tab or browser closes; `sessionStorage` lasts only as long as that tab is open.

## 🔵 सरल परिभाषा (Hindi)
`localStorage` और `sessionStorage` browser APIs हैं जो user के device पर छोटा key-value string data save करते हैं। `localStorage` tab या browser बंद होने के बाद भी रहता है; `sessionStorage` सिर्फ़ तब तक रहता है जब तक वह tab खुला है।

> **Browser-only note:** Both objects exist only in the browser (`window.localStorage`, `window.sessionStorage`). In Node.js, `typeof localStorage` is `"undefined"` (verified on Node 24). Node has no "same sense" equivalent. On the server you store data in files, a database, Redis, or per-user session stores, and the client gets a cookie that identifies the session.

---

## 🔴 Problem it Solves
A page refresh wipes all JavaScript variables. Before storage APIs, sites used cookies for everything, but cookies are sent with every HTTP request (wasting bandwidth) and are limited to about 4 KB. Shopping carts on Flipkart or Amazon, dark-mode settings, and "remember me" flags needed a simple place to keep data across refreshes without sending it to the server each time.

## 🔴 यह क्यों बना? (Hindi)
Page refresh होने पर JavaScript की सारी variables मिट जाती हैं। Storage APIs से पहले sites सब कुछ cookies में रखती थीं, लेकिन cookies हर HTTP request के साथ जाती हैं (bandwidth बर्बाद) और उनकी limit लगभग 4 KB है। Flipkart या Amazon का cart, dark-mode setting और "remember me" flag को refresh के बाद बचाने के लिए एक सरल जगह चाहिए थी, जो हर बार server तक न भेजनी पड़े।

---

## 🟢 How it Works — Step by Step

Step 1 → Data is stored as **strings** only. Objects must go through `JSON.stringify`
Step 2 → `setItem(key, value)` writes; `getItem(key)` reads (returns `null` if missing)
Step 3 → Data is scoped to the **origin** (scheme + host + port), so `https://a.com` cannot read `https://b.com`
Step 4 → `localStorage` persists until code or the user removes it; `sessionStorage` is cleared when the tab closes
Step 5 → Limit is about 5 MB per origin (varies by browser); writing more throws `QuotaExceededError`
Step 6 → Other open tabs of the same origin get a `storage` event when `localStorage` changes (not for `sessionStorage`)

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Data हमेशा **string** के रूप में store होता है। Objects को `JSON.stringify` से गुज़ारना पड़ता है
Step 2 → `setItem(key, value)` लिखता है; `getItem(key)` पढ़ता है (न मिले तो `null`)
Step 3 → Data **origin** (scheme + host + port) से बँधा है, इसलिए `https://a.com` दूसरी site का data नहीं पढ़ सकती
Step 4 → `localStorage` तब तक रहता है जब तक code या user उसे हटाए; `sessionStorage` tab बंद होने पर साफ़ हो जाता है
Step 5 → Limit लगभग 5 MB प्रति origin है (browser के हिसाब से बदलती है); ज़्यादा लिखने पर `QuotaExceededError` आता है
Step 6 → `localStorage` बदलने पर उसी origin के बाकी खुले tabs को `storage` event मिलता है (`sessionStorage` के लिए नहीं)

---

## 🟡 Real World Example
Amazon India's cart: while you browse, the recently viewed items and a "dark mode" choice are kept in `localStorage`, so they survive a closed browser. A checkout wizard (multi-step form) keeps the current step in `sessionStorage`, so a new tab starts fresh and two tabs do not overwrite each other's progress.

## 🟡 Real Example Hindi mein
Amazon India का cart: browse करते समय हाल में देखे गए items और "dark mode" की पसंद `localStorage` में रहती हैं, इसलिए browser बंद होने के बाद भी बची रहती हैं। Checkout wizard (multi-step form) का current step `sessionStorage` में रहता है, ताकि नया tab fresh शुरू हो और दो tabs एक-दूसरे का progress overwrite न करें।

---

## 💻 Code Example — Basic
> Browser-only (uses `window.localStorage`). It cannot run with `node` in this Node version. Runnable example is a self-contained HTML page.
> **How to run:** save as `storage-basic.html`, serve with `python3 -m http.server 8000`, open `http://localhost:8000/storage-basic.html`, add items, then refresh the page and watch the cart survive.

```html
<!-- storage-basic.html — full page, JS inside <script> -->
<!DOCTYPE html>
<!-- HTML5 doctype -->
<html lang="en">
<!-- Root element -->
<head>
  <!-- Head section -->
  <meta charset="UTF-8">
  <!-- UTF-8 for Hindi text -->
  <title>Storage Basic</title>
  <!-- Tab title -->
</head>
<body>
  <!-- Visible content -->
  <h2>Cart (saved in localStorage)</h2>
  <!-- Heading -->
  <button id="add">Add Pizza ₹299</button>
  <!-- Adds an item to the cart -->
  <button id="clear">Clear Cart</button>
  <!-- Empties the cart -->
  <p>Items: <span id="count">0</span></p>
  <!-- Shows item count -->
  <ul id="list"></ul>
  <!-- List of cart items -->

  <script>
    const KEY = "cart";
    // Key name used in localStorage

    // Read the cart array; fall back to empty array if nothing is stored
    function loadCart() {
      // Function to get the cart
      const raw = localStorage.getItem(KEY);
      // Returns a string or null
      return raw ? JSON.parse(raw) : [];
      // Parse JSON string back to an array
    }

    // Save the cart array as a JSON string
    function saveCart(cart) {
      // Function to persist the cart
      localStorage.setItem(KEY, JSON.stringify(cart));
      // Objects must be converted to strings
    }

    // Redraw the list and counter from the stored cart
    function render() {
      // Function to update the UI
      const cart = loadCart();
      // Get the current cart from storage
      document.getElementById("count").textContent = cart.length;
      // Show the number of items
      document.getElementById("list").innerHTML = cart
        .map((item) => `<li>${item}</li>`)
        .join("");
      // Build list items (demo only: do not put user input in innerHTML)
    }

    document.getElementById("add").addEventListener("click", () => {
      // Handler for add button
      const cart = loadCart();
      // Load current cart
      cart.push("Pizza ₹299");
      // Add one item
      saveCart(cart);
      // Save the updated cart
      render();
      // Refresh the screen
    });

    document.getElementById("clear").addEventListener("click", () => {
      // Handler for clear button
      localStorage.removeItem(KEY);
      // Delete the key entirely
      render();
      // Refresh the screen
    });

    render();
    // Draw the cart when the page first loads (survives refresh)
  </script>
  <!-- End script -->
</body>
<!-- End body -->
</html>
<!-- End document -->
```

## 💻 Code Example — Advanced
> The reusable, testable part is pure JavaScript, so this one **runs in Node.js** (`node storage-advanced.js`). It uses an in-memory object that has the same methods as `localStorage` (`getItem`, `setItem`, `removeItem`, `key`, `length`). In the browser you pass `window.localStorage` instead. The code handles JSON errors, quota errors and a versioned schema.

```javascript
// storage-advanced.js — safe storage wrapper; run with: node storage-advanced.js

// In-memory stand-in with the same method names as window.localStorage
class MemoryStorage {
  // Class that mimics the Storage interface
  constructor(limitBytes = 200) {
    // Set a small size limit so we can demonstrate quota errors
    this.map = new Map();
    // Holds key-value string pairs
    this.limitBytes = limitBytes;
    // Max total size in bytes (browsers use about 5 MB)
  }
  get length() {
    // Property returning number of stored keys
    return this.map.size;
    // Map size equals number of keys
  }
  key(i) {
    // Return the key name at index i
    return [...this.map.keys()][i] ?? null;
    // Convert keys to an array and pick by index, or null
  }
  getItem(k) {
    // Read a value by key
    return this.map.has(k) ? this.map.get(k) : null;
    // Return the string or null if not found
  }
  setItem(k, v) {
    // Write a value (always stored as string)
    const used = [...this.map].reduce((s, [a, b]) => s + a.length + b.length, 0);
    // Count bytes already used (rough: string length)
    if (used + String(k).length + String(v).length > this.limitBytes) {
      // Would exceed the quota
      const err = new Error("Quota exceeded");
      // Create an error object
      err.name = "QuotaExceededError";
      // Use the same name browsers use
      throw err;
      // Throw so the caller can handle it
    }
    this.map.set(String(k), String(v));
    // Store the string version (Storage converts values to strings)
  }
  removeItem(k) {
    // Delete one key
    this.map.delete(k);
    // Remove from the Map
  }
  clear() {
    // Delete everything
    this.map.clear();
    // Empty the Map
  }
}

// Wrap any Storage-like object with JSON handling, errors and schema version
function createStore(storage, namespace, version = 1) {
  // storage is localStorage or MemoryStorage; namespace avoids key clashes
  const key = `${namespace}:v${version}`;
  // Versioned key, e.g. "cart:v1"

  return {
    get(fallback = null) {
      // Read and parse the stored JSON
      try {
        // Parsing may throw if someone stored bad JSON
        const raw = storage.getItem(key);
        // Get the raw string
        return raw === null ? fallback : JSON.parse(raw);
        // Parse or return the fallback
      } catch (err) {
        // Corrupt JSON or blocked access
        console.warn(`[store] could not read ${key}:`, err.message);
        // Log the problem for debugging
        return fallback;
        // Recover with the fallback value
      }
    },
    set(value) {
      // Save a value as JSON
      try {
        // Writing may throw QuotaExceededError
        storage.setItem(key, JSON.stringify(value));
        // Store the serialized value
        return true;
        // Report success to the caller
      } catch (err) {
        // Handle quota or privacy-mode failures
        if (err.name === "QuotaExceededError") {
          // Specific handling for storage full
          console.warn("[store] storage full, data not saved");
          // Tell the developer
        }
        return false;
        // Report failure without crashing the app
      }
    },
    remove() {
      // Delete this namespace's key
      storage.removeItem(key);
      // Remove the stored value
    },
  };
}

// ---- demo ----
const storage = new MemoryStorage(120);
// Create the in-memory storage with a small limit
const cartStore = createStore(storage, "cart", 1);
// Create a namespaced store for the cart

console.log(cartStore.get([]));
// [] — nothing stored yet, so fallback is used
console.log(cartStore.set([{ item: "Pizza", price: 299 }]));
// true — saved successfully
console.log(cartStore.get([]));
// [ { item: 'Pizza', price: 299 } ] — read back as an object

storage.setItem("broken:v1", "{not json");
// Put bad JSON under the real versioned key "broken:v1" to test the reader
console.log(createStore(storage, "broken").get("default"));
// Logs a warning and returns "default" instead of crashing

console.log(cartStore.set(Array(50).fill("long item name")));
// false — quota exceeded, handled gracefully
console.log("keys stored:", storage.length);
// Shows how many keys are in storage now
```

---

## 🟠 Express.js Integration
`localStorage` lives only in the browser, so Express never reads it. The server's role is to serve the page with the JavaScript that uses storage, and to receive data the user chooses to sync (for example, a cart saved to a database so it works on another device).

```javascript
// server.js — npm i express, then node server.js
const express = require("express");
// Import Express
const app = express();
// Create the app
app.use(express.json());
// Parse JSON bodies

app.use(express.static("public"));
// Serve storage-basic.html and other static pages

// In-memory "database" for the demo (use a real DB in production)
const carts = new Map();
// Map from userId to cart array

// Client calls this when the user logs in to sync localStorage to the server
app.put("/api/cart/:userId", (req, res) => {
  // PUT replaces the full cart for a user
  const cart = req.body.cart;
  // Read the cart array from the JSON body
  if (!Array.isArray(cart)) {
    // Validate the type
    return res.status(400).json({ error: "cart must be an array" });
    // Reject non-array data
  }
  carts.set(req.params.userId, cart);
  // Save the cart for that user
  res.json({ saved: cart.length });
  // Return how many items were saved
});

// Client calls this on another device to restore the cart
app.get("/api/cart/:userId", (req, res) => {
  // GET returns the saved cart
  res.json({ cart: carts.get(req.params.userId) ?? [] });
  // Return the cart, or an empty array if none exists
});

app.listen(3000, () => console.log("Server on http://localhost:3000"));
// Start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Storing objects directly and getting `[object Object]` back.
✅ Correct: Always `JSON.stringify` before `setItem` and `JSON.parse` after `getItem`.

```javascript
// Wrong — stored as "[object Object]"
localStorage.setItem("user", { name: "Aditya" });
console.log(localStorage.getItem("user")); // "[object Object]"

// Right — serialize and parse
localStorage.setItem("user", JSON.stringify({ name: "Aditya" }));
console.log(JSON.parse(localStorage.getItem("user")).name); // "Aditya"
```

❌ Mistake 2: Calling `JSON.parse` on `null` without checking, which crashes on first visit.
✅ Correct: Check for `null` (or use a fallback) before parsing.

```javascript
// Wrong — first visit: getItem returns null, JSON.parse(null) gives null, then .length throws
const cart = JSON.parse(localStorage.getItem("cart"));
console.log(cart.length); // TypeError on a fresh browser

// Right — provide a default
const cart2 = JSON.parse(localStorage.getItem("cart") || "[]");
console.log(cart2.length); // 0
```

❌ Mistake 3: Storing secrets (JWT, passwords, API keys) in localStorage.
✅ Correct: Any script on the page (including XSS injected code) can read localStorage. Use HttpOnly cookies for session tokens.

---

## 🧠 Tricky Interview Question
What will be printed in the browser console? Assume `localStorage` is empty before the code runs.

```javascript
// Tricky storage code (run in a browser console)
localStorage.setItem("count", 0);
// Store the number 0

const next = localStorage.getItem("count") + 1;
// Read the value and add 1

console.log(next);
// Print the result
console.log(typeof next);
// Print the type
```

Answer: It prints `01` and then `string`. `getItem` always returns a **string**, so `"0" + 1` is string concatenation, which gives `"01"`, not `1`. A number-typed value was stored, but it came back as the text `"0"`. The fix is `Number(localStorage.getItem("count")) + 1`, which gives `1`. This is why storage code should parse values explicitly.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `localStorage` and `sessionStorage`?
A1: `localStorage` persists across tabs and browser restarts until removed. `sessionStorage` is per tab and is cleared when that tab closes.

Q2: What is the storage limit?
A2: About 5 MB per origin in most browsers. Exceeding it throws `QuotaExceededError`.

Q3: Are localStorage values sent to the server?
A3: No. Unlike cookies, they are not sent with HTTP requests, which is why they are good for client-only data.

Q4: Is localStorage secure?
A4: No. It is readable by any JavaScript running on the same origin, so XSS can steal it. Never store sensitive tokens there.

Q5: How does one tab learn about changes in another tab?
A5: Listen for the `storage` event on `window`. It fires in other tabs of the same origin when `localStorage` changes, not in the tab that changed it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You store UI preferences (theme, language, dismissed banners)
- You keep a client-only cart or draft text that survives refresh
- You need multi-step form progress per tab (use `sessionStorage`)

❌ Avoid when:
- You store passwords, JWTs or payment data (XSS can read them)
- The data must be sent to the server with every request (use cookies)
- You store large files or huge JSON (the limit is about 5 MB and it blocks the main thread while reading or writing)

---

## 📊 Visual Diagram
```
Browser tab A                      Browser tab B (same origin)
+----------------------+           +----------------------+
| JS: setItem("cart")  |           |                      |
+----------+-----------+           |                      |
           |                       |                      |
           v                       |                      |
+----------------------------------+                      |
|     localStorage (per origin)    |  -- storage event -->|  listener runs
|  "cart" -> '[{"item":"Pizza"}]'  |                      |
+----------------------------------+                      |
                                                          +----------------------+

sessionStorage: separate copy per tab, gone when tab A closes
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| localStorage | Persistent key-value store per origin | Origin के हिसाब से स्थायी key-value store |
| sessionStorage | Key-value store cleared when tab closes | Tab बंद होने पर साफ़ होने वाला store |
| Origin | Scheme + host + port | Scheme + host + port का combo |
| QuotaExceededError | Error when storage is full | Storage भरने पर आने वाला error |
| storage event | Notifies other tabs about changes | दूसरे tabs को बदलाव की सूचना |
| JSON.stringify | Converts object to string for storage | Object को string में बदलना |
| XSS | Attack that runs injected script to read storage | ऐसा attack जो storage को पढ़ सकता है |

---

## ⚡ 3-Line Summary
English: `localStorage` keeps data across refreshes and restarts, while `sessionStorage` keeps it only for one tab.
English: Values are always strings, so use `JSON.stringify` and `JSON.parse`, and handle `null` and `QuotaExceededError`.
English: Do not store secrets there, and remember Node.js has no equivalent (use a server-side store instead).
Hindi: `localStorage` refresh और restart के बाद भी data रखता है, जबकि `sessionStorage` सिर्फ़ एक tab के लिए रखता है।
Hindi: Values हमेशा string होती हैं, इसलिए `JSON.stringify` और `JSON.parse` use करें, और `null` व `QuotaExceededError` handle करें।
Hindi: Secrets वहाँ न रखें; Node.js में इसका equivalent नहीं है, इसलिए server-side store use करें।

---

## ➡️ Next Topic
159. Cookies in JavaScript: cookies are the other client-side storage mechanism. Unlike localStorage they are sent with every request and can be HttpOnly, so the comparison is a common interview question and it connects directly to the Express session topics.
