---

# Q232. Debounce Input Search
# Category: DOM Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Attach a search input so that the search function runs only 400ms after the user stops typing. Ignore empty/unchanged queries.

---

## 💡 Quick Concept (2 lines only)
Debounce resets a timer on every keystroke, so the handler runs only after typing pauses.
हिंदी: हर keystroke पर timer reset होता है, इसलिए typing रुकने के बाद ही search चलता है।

---

## ✅ Answer / Solution

```html
<input id="search" placeholder="Search...">
<ul id="results"></ul>
```

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Write a debounce helper
// Step 2: Write the search function
// Step 3: Attach debounced handler to input event

function debounce(fn, delay) {
  let timer;                                             // holds pending timeout id
  return function (...args) {                            // wrapper returned
    clearTimeout(timer);                                 // cancel previous call
    timer = setTimeout(() => fn.apply(this, args), delay); // schedule new call
  };
}

const input = document.getElementById('search');         // input element
const results = document.getElementById('results');      // output list
let last = '';                                           // last searched query

function search(query) {
  const q = query.trim();                                // remove spaces
  if (!q || q === last) return;                          // skip empty/duplicate
  last = q;                                              // remember
  results.innerHTML = '';                                // clear old results
  const li = document.createElement('li');               // fake result row
  li.textContent = 'Results for: ' + q;                  // textContent avoids XSS
  results.appendChild(li);                               // show
  console.log('search ->', q);                           // log call
}

const debounced = debounce((e) => search(e.target.value), 400); // debounced handler
input.addEventListener('input', debounced);              // on every keystroke

// ============================================
// TEST CASES
// ============================================

// Test 1: type "react" quickly      -> Expected: ONE log "search -> react" after ~400ms
// Test 2: type "re", wait, type "act" -> Expected: two logs: "re" then "react"
// Test 3: type "a", delete it       -> Expected: no log (empty query ignored)
// Test 4: type the same text again  -> Expected: no log (same as last)
```

---

## 🔍 Why This Works (3 lines max)
`clearTimeout` kills the previous scheduled call, so only the last keystroke's timer survives. The closure keeps `timer` between calls. Guarding empty/duplicate queries saves API calls.
हिंदी: Closure में timer बचा रहता है, और पुराना timer clear होने से सिर्फ़ आख़िरी call चलती है।

---

## ⚡ Alternative Solution
```javascript
// Debounce + cancel stale fetch with AbortController
let controller;                                          // current request controller
async function fetchSearch(q) {
  controller?.abort();                                   // cancel previous request
  controller = new AbortController();                    // new controller
  const res = await fetch('/api?q=' + encodeURIComponent(q), { signal: controller.signal }); // request
  return res.json();                                     // parse
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: creating a new debounce on every event — timer is never shared
input.addEventListener('input', (e) => debounce(search, 400)(e.target.value));

// ✅ Correct: create the debounced function ONCE, outside the listener
```

---

## 🎯 Interview Tip (1 line)
Say: "Debounce waits for silence (search box), throttle limits rate (scroll); also cancel stale requests to avoid out-of-order responses."

---

## 🔗 Related Questions
→ Q081 (implement debounce) | Q181 (search with debounce) | Q233 (autocomplete) | Q214 (debounce async)
