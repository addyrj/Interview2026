# 87. AJAX
# हिंदी में: AJAX — Page Reload किए बिना Server से Data लाना

---

## 🔵 Simple Definition (English)
AJAX (Asynchronous JavaScript And XML) is a technique, not a single API. The browser sends an HTTP request in the background, gets data back (today usually JSON), and updates only a part of the page instead of reloading all of it. `XMLHttpRequest` and `fetch` are the tools used to do AJAX.

## 🔵 सरल परिभाषा (Hindi)
AJAX (Asynchronous JavaScript And XML) एक तकनीक है, कोई एक API नहीं। Browser background में HTTP request भेजता है, data वापस लेता है (आज आमतौर पर JSON), और पूरा page reload करने की जगह सिर्फ page का एक हिस्सा अपडेट करता है। AJAX के लिए `XMLHttpRequest` और `fetch` इस्तेमाल होते हैं।

---

## 🔴 Problem it Solves
Full page reloads were slow and flickered. Every search, filter, or button click repainted the whole page and lost scroll position and typed text. AJAX lets the page ask the server only for the data it needs (for example, search results), and update just the list. This is why a Swiggy search box shows results as you type.

## 🔴 यह क्यों बना? (Hindi)
Full page reload धीमा था और screen झिलमिलाती थी। हर search, filter या button click पूरा page दोबारा बनाता था और scroll position तथा लिखा हुआ text खो जाता था। AJAX page को सिर्फ ज़रूरी data (जैसे search results) server से मांगने देता है, और सिर्फ list अपडेट करता है। इसीलिए Swiggy के search box में type करते ही results बदलते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → A user action (typing, clicking) triggers JavaScript
Step 2 → JavaScript sends an HTTP request in the background (XHR or fetch)
Step 3 → The page shows a loading state, so the user knows something is happening
Step 4 → The server replies with data, usually JSON (not the whole HTML page)
Step 5 → JavaScript updates only the matching part of the DOM with the new data
Step 6 → If responses can arrive out of order, ignore the stale ones (the race condition below)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → User की action (type करना, click करना) JavaScript को चलाती है
Step 2 → JavaScript background में HTTP request भेजता है (XHR या fetch)
Step 3 → Page loading state दिखाता है, ताकि user जाने कि कुछ हो रहा है
Step 4 → Server data लौटाता है, आमतौर पर JSON (पूरा HTML page नहीं)
Step 5 → JavaScript सिर्फ DOM के उस हिस्से को नए data से अपडेट करता है
Step 6 → अगर responses उलटे क्रम में आ सकते हैं, तो पुराने (stale) responses को ignore करो (नीचे race condition देखो)

---

## 🟡 Real World Example
On a Flipkart-style search bar, the user types "b", then "bi", then "bir". Each keystroke sends an AJAX request, and the results list changes without the page reloading. If the response for "b" (large result set, slow) arrives after the response for "bir", the page must still show "bir" results, not the stale "b" results.

## 🟡 Real Example Hindi mein
Flipkart जैसे search bar में user "b", फिर "bi", फिर "bir" लिखता है। हर keystroke पर AJAX request जाती है, और results बिना page reload हुए बदलते हैं। अगर "b" का जवाब (बड़ा और धीमा) "bir" के जवाब के बाद आए, तो page को फिर भी "bir" के results दिखाने चाहिए, पुराने "b" के नहीं।

---

## 💻 Code Example — Basic
```javascript
// Fake "server": a lookup table of responses. No real network is used.
const fakeServer = {
  "/api/menu?q=b": { items: ["Biryani", "Burger"] },    // response for search "b"
  "/api/menu?q=p": { items: ["Pizza", "Paneer Tikka"] }, // response for search "p"
};

// Simulated transport: answers after 30ms, using an error-first callback (old style)
function transport(url, callback) {
  setTimeout(() => {                                     // wait 30ms like a network call
    const data = fakeServer[url];                        // look up the response
    if (!data) return callback(new Error("404 not found")); // unknown URL: error
    callback(null, data);                                // success: (null error, data)
  }, 30);
}

// AJAX helper written in callback style: (error, data) => { ... }
function ajaxGet(url, callback) {
  transport(url, (err, data) => {                        // send the request
    if (err) return callback(err);                       // pass the error on
    callback(null, data);                                // pass the data on
  });
}

// A fake page state: this is what the "DOM" would show
const page = { status: "idle", list: [] };

// User action: search for a term and update only the list
function onSearch(term) {
  page.status = "loading";                               // show a spinner
  console.log(`[${term}] loading...`);                   // user feedback

  ajaxGet(`/api/menu?q=${term}`, (err, data) => {        // request data in the background
    if (err) {                                           // server or network problem
      page.status = "error";                             // show an error message
      console.log(`[${term}] error:`, err.message);      // log it
      return;                                            // stop here
    }
    page.status = "done";                                // hide spinner
    page.list = data.items;                              // update ONLY the list
    console.log(`[${term}] shows:`, page.list);          // what the user now sees
  });
}

onSearch("b");                                           // first search
setTimeout(() => onSearch("p"), 100);                    // second search, later
setTimeout(() => console.log("final status:", page.status), 200); // "done"
```

**Expected output (basic):**
```
[b] loading...
[b] shows: [ 'Biryani', 'Burger' ]
[p] loading...
[p] shows: [ 'Pizza', 'Paneer Tikka' ]
final status: done
```

## 💻 Code Example — Advanced
```javascript
// Advanced: the classic AJAX race condition, and the request-id guard that fixes it.

// Different server latency per search term (ms). Shorter terms are slower here on purpose.
const latency = { a: 120, ab: 20, abc: 60 };

// Simulated transport: returns the search term as the result after latency[q] ms
function transport(q, callback) {
  setTimeout(() => callback(null, { q, items: [`result for ${q}`] }), latency[q]);
}

// BUG version: every response is rendered in ARRIVAL order, so old data can overwrite new data
function naiveSearch(q, render) {
  transport(q, (err, data) => render(data));             // no check at all
}

// FIX: a request id. Only the response for the most recent request is rendered
function createSearch(render) {
  let latestId = 0;                                      // id of the newest request
  return function search(q) {                            // the function the UI calls
    const id = ++latestId;                               // stamp this request with a new id
    transport(q, (err, data) => {                        // send the request
      if (id !== latestId) return;                       // a newer search started: ignore this stale answer
      render(data);                                      // only the latest response is shown
    });
  };
}

// Demo 1: naive version, three searches at once
const seen = [];                                         // record what gets rendered
naiveSearch("a", (d) => seen.push(d.q));                 // arrives at 120ms
naiveSearch("ab", (d) => seen.push(d.q));                // arrives at 20ms
naiveSearch("abc", (d) => seen.push(d.q));               // arrives at 60ms
setTimeout(() => console.log("naive renders:", seen), 200); // [ 'ab', 'abc', 'a' ] (last one is stale)

// Demo 2: guarded version, same three searches
const shown = [];                                        // record what the user sees
const search = createSearch((d) => shown.push(d.q));     // render pushes into `shown`
search("a");                                             // id 1 (ignored, stale)
search("ab");                                            // id 2 (ignored, stale)
search("abc");                                           // id 3 (latest: rendered)

setTimeout(() => {
  console.log("guarded renders:", shown);                // [ 'abc' ]
  search("ab");                                          // a new, single search later
}, 200);

setTimeout(() => console.log("after new search:", shown), 300); // [ 'abc', 'ab' ]
```

**Expected output (advanced):**
```
naive renders: [ 'ab', 'abc', 'a' ]
guarded renders: [ 'abc' ]
after new search: [ 'abc', 'ab' ]
```

---

## 🟠 Express.js Integration
An Express route returns JSON for the AJAX call. The browser side calls it with `fetch` (the modern AJAX tool). Use a short query parameter and return only the fields the UI needs, which keeps the AJAX response small.

```javascript
// Express.js example: JSON endpoint used by an AJAX live search
const express = require("express");                 // import Express
const app = express();                              // create the app

const MENU = [                                      // pretend database table
  { name: "Biryani", price: 299 },
  { name: "Burger", price: 149 },
  { name: "Pizza", price: 399 },
];

app.get("/api/menu", (req, res) => {                // GET /api/menu?q=bi
  const q = (req.query.q || "").toLowerCase();      // read the search term, default ""
  const items = MENU.filter((m) =>                  // keep items whose name matches
    m.name.toLowerCase().includes(q)
  );
  res.json({ items });                              // small JSON body for the AJAX call
});

app.use(express.static("public"));                  // serve the page that contains the AJAX code
app.listen(3000);                                   // start the server

// ---- Browser side (public/app.js), shown as comments because it runs in the browser ----
// document.querySelector("#search").addEventListener("input", async (e) => {
//   const res = await fetch(`/api/menu?q=${encodeURIComponent(e.target.value)}`); // AJAX call
//   if (!res.ok) return showError();                // check status (fetch does not reject on 500)
//   const { items } = await res.json();             // parse JSON
//   renderList(items);                              // update only the list
// });
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Rendering every response, so an old slow response overwrites the newest one
✅ **Correct:** Keep a request id (or `AbortController`, topic 88) and ignore stale responses.

```javascript
// Wrong: order of arrival decides what the user sees
search("a");   search("abc");     // "a" may arrive last and overwrite "abc"

// Right: only the latest id renders (see the guard in the advanced example)
```

❌ **Mistake 2:** Replacing the whole page with the server HTML when only a list changed
✅ **Correct:** Request JSON and update just the part of the DOM that changed.

```javascript
// Wrong: fetches a full HTML page for a small change
const html = await (await fetch("/search-page?q=bi")).text();
document.body.innerHTML = html;      // destroys input focus and scroll position

// Right: fetch JSON and update the list only
const { items } = await (await fetch("/api/menu?q=bi")).json();
document.querySelector("#results").textContent = items.map((i) => i.name).join(", ");
```

❌ **Mistake 3:** Thinking AJAX requires XML
✅ **Correct:** The name is historical. Modern AJAX uses JSON almost everywhere.

```javascript
// Wrong assumption: "AJAX means I must parse XML"
// Right: a JSON response is parsed with response.json() or JSON.parse(text)
```

---

## 🧠 Tricky Interview Output Question
```javascript
const results = [];                                  // what the page would show, in order

function search(term, delayMs) {                     // no guard, just a timer as "network"
  setTimeout(() => results.push(term), delayMs);     // render when the response arrives
}

search("a", 100);                                    // slow response for the first keystroke
search("ab", 10);                                    // fast response for the second keystroke

setTimeout(() => console.log(results), 200);         // what is printed?
```
**Answer:**
```
[ 'ab', 'a' ]
```
**Why:** Both requests run at the same time. The response for `"ab"` arrives at 10ms, so it is pushed first. The response for `"a"` arrives at 100ms, so it is pushed second and overwrites what the user sees with stale data. The order of responses is decided by network timing, not by the order of the requests. The fix is to remember which request is newest and ignore the others, as in the advanced example.

---

## ⚫ Interview Questions + Answers

Q1: Is AJAX an API?
A1: No. AJAX is a technique: send an HTTP request from JavaScript in the background and update part of the page. The APIs used for it are `XMLHttpRequest` and `fetch`.

Q2: What does the "X" in AJAX stand for, and is it still relevant?
A2: XML. It is historical. Most AJAX today uses JSON, though the name stayed the same.

Q3: What is a race condition in AJAX?
A3: When responses arrive in a different order from the requests, an older response can overwrite a newer one. The fix is to track the latest request and ignore the others, or to cancel old requests with `AbortController`.

Q4: Why is AJAX better than a full page reload for search?
A4: It sends only the data needed, avoids repainting the whole page, keeps the user's typed text and scroll position, and feels faster.

Q5: Does AJAX work without JavaScript?
A5: No. The request and the update both need JavaScript. Pages that must work without JavaScript use normal form submissions and full page responses.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Small parts of a page change based on user actions (search, filters, pagination)
- You want to avoid full page reloads for a smoother experience
- You need to show data that changes often, such as stock or order status

❌ Avoid when:
- The whole page changes anyway; a normal navigation is simpler and SEO-friendly
- Data must be fresh on every single keystroke without any guard against stale responses
- The page must work without JavaScript

---

## 📊 Visual Diagram
```
User types "b"  ──► AJAX request #1 ──────────────────────────► response #1 (slow)  ──┐
User types "bi" ──► AJAX request #2 ──────► response #2 (fast) ──┐                     │
                                                                  ▼                    ▼
                                                        render if id == latest?   ignored (stale)
                                                                  │
                                                                  ▼
                                                          list updated (no reload)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AJAX | Technique to fetch data in the background and update part of a page | Background में data लाकर page का हिस्सा अपडेट करना |
| Partial update | Changing only one part of the DOM | DOM का सिर्फ एक हिस्सा बदलना |
| Race condition | Wrong result because responses arrive in a surprising order | गलत क्रम में responses आने से गलत नतीजा |
| Request id | Number that marks which request is newest | कौन सी request सबसे नई है, यह बताने वाला नंबर |
| Stale response | An old answer to an outdated request | पुरानी request का पुराना जवाब |
| Debounce | Waiting for a pause before sending requests | Requests भेजने से पहले थोड़ा रुकना |
| Error-first callback | `callback(err, data)` style | पहले error, फिर data वाला callback |

---

## ⚡ 3-Line Summary
**English:**
1. AJAX is a technique: background HTTP request, then update only the part of the page that changed.
2. Use JSON responses, a loading state, and error handling for every AJAX call.
3. Guard against stale responses with a request id or `AbortController`, because responses can arrive out of order.

**Hindi:**
1. AJAX एक तकनीक है: background में HTTP request, फिर page का सिर्फ बदला हुआ हिस्सा अपडेट करना।
2. हर AJAX call के लिए JSON response, loading state और error handling रखो।
3. Stale responses से request id या `AbortController` से बचो, क्योंकि responses उलटे क्रम में आ सकते हैं।

---

## ➡️ Next Topic
**88. AbortController** — Stale responses are best solved by cancelling old requests. Next, learn `AbortController` and `AbortSignal`, how to cancel `fetch` and timers, and how to combine timeouts with user cancellation.
