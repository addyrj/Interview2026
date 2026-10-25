# 199. Build Infinite Scroll
# हिंदी में: Infinite Scroll बनाना — Bottom Detection, Page Loading, Duplicate Guard और Stale Response

---

## 🔵 Simple Definition (English)
Infinite scroll loads the next batch of items when the user gets close to the bottom of a list, instead of showing page numbers. The core logic is small: decide when the user is near the end, request the next page once, add the items, and stop when the server has no more. Interviews test the edge cases: duplicate requests, a slow response that arrives after the user has searched again, errors, and the end of the data.

## 🔵 सरल परिभाषा (Hindi)
Infinite scroll में user list के आख़िर के करीब पहुँचता है, तो अगला batch अपने-आप लोड होता है, page numbers देखने की ज़रूरत नहीं होती। Core logic छोटा है: तय करो कि user आख़िर के करीब है, अगला page एक बार माँगो, items जोड़ो, और server के पास और न होने पर रुक जाओ। Interview में असली सवाल edge cases के होते हैं: एक साथ कई requests, धीमा response जो user के नई search के बाद आए, errors, और data का अंत।

---

## 🔴 Problem it Solves
**Problem Statement:** Build a list that loads 10 items per page. When the user scrolls within 200 px of the bottom, load the next page. Do not send two requests at once, do not show the same item twice, stop at the last page, retry after an error, and ignore a response that arrives after the list was reset.

Without this, a list either loads everything at once (slow for 50,000 products) or uses buttons that interrupt the user. A naive version fires a request on every scroll event, which can be 60 times a second, and it shows stale results after a search.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** एक list बनाओ जो हर बार 10 items लोड करे। जब user नीचे से 200 px के अंदर आए, तब अगला page लोड हो। एक साथ दो requests न जाएँ, कोई item दो बार न दिखे, आख़िरी page पर रुके, error के बाद retry हो, और reset के बाद आने वाला पुराना response नज़रअंदाज़ हो।

इसके बिना list या तो सारा data एक साथ लोड करती है (50,000 products के लिए धीमा), या buttons से user का flow टूटता है। Naive version हर scroll event पर request भेजता है, जो एक सेकंड में 60 बार तक हो सकता है, और search के बाद पुराने results दिखाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Compute the distance to the bottom: `scrollHeight - (scrollTop + clientHeight)`.
Step 2 → If the distance is at most the threshold (200 px), the user is near the end.
Step 3 → Before loading, check the guards: no request already running, and `hasMore` is true.
Step 4 → Remember the list "generation"; if the list is reset while waiting, ignore the response.
Step 5 → Add the items, advance the page, and set `hasMore` false when a page is shorter than `pageSize`.
Step 6 → On error, store the error and clear `loading`, so the next scroll tries again.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Bottom से दूरी निकालो: `scrollHeight - (scrollTop + clientHeight)`।
Step 2 → अगर दूरी threshold (200 px) से कम या बराबर हो, तो user list के आख़िर के करीब है।
Step 3 → Load करने से पहले guards चेक करो: कोई request चल न रही हो, और `hasMore` true हो।
Step 4 → List की "generation" याद रखो; इंतज़ार के दौरान reset हो जाए तो response नज़रअंदाज़ करो।
Step 5 → Items जोड़ो, page आगे बढ़ाओ, और जब page `pageSize` से छोटा हो तो `hasMore` false करो।
Step 6 → Error पर error सेव करो और `loading` हटाओ, ताकि अगला scroll फिर कोशिश करे।

---

## 🟡 Real World Example
Instagram's feed, Flipkart's product grid, and Swiggy's restaurant list all load the next batch near the bottom. A Flipkart search for "shoes" starts at page 1. If the user types "bags" before the "shoes" page 2 arrives, that late response must not appear under "bags". The list uses a generation counter for this.

Scenario: A Paytm transaction history loads 20 rows at a time. The user scrolls fast, and three scroll events arrive while page 2 is loading. Only one request should go out. Later, the server is down for a second, so page 3 fails. The "Retry" message shows, and the next scroll loads page 3 without a page refresh.

## 🟡 Real Example Hindi mein
Instagram का feed, Flipkart का product grid और Swiggy की restaurant list, सब आख़िर के करीब आने पर अगला batch लोड करते हैं। Flipkart पर "shoes" search page 1 से शुरू होती है। अगर user "shoes" का page 2 आने से पहले "bags" लिख दे, तो वह देर से आया response "bags" के नीचे नहीं दिखना चाहिए। इसके लिए list में generation counter होता है।

उदाहरण: Paytm का transaction history एक बार में 20 rows लोड करता है। User तेज़ scroll करता है, और page 2 लोड होते समय तीन scroll events आते हैं। Request सिर्फ एक जानी चाहिए। बाद में server एक सेकंड के लिए बंद होता है, तो page 3 fail होता है। "Retry" message दिखता है, और अगला scroll बिना page refresh के page 3 लोड करता है।

---

## 💻 Code Example — Basic
```javascript
// Run with: node file.js  (this is the node-testable core; the browser version is further below)

// shouldLoadMore: the pure decision, with no DOM. Takes the three numbers a browser gives us.
function shouldLoadMore({ scrollTop, clientHeight, scrollHeight }, threshold = 200) {
  const distanceToBottom = scrollHeight - (scrollTop + clientHeight); // pixels still below the viewport
  return distanceToBottom <= threshold;             // true when we are within threshold px of the end
}

console.log(shouldLoadMore({ scrollTop: 0, clientHeight: 500, scrollHeight: 2000 }));    // Expected output: false (1500 px left)
console.log(shouldLoadMore({ scrollTop: 1400, clientHeight: 500, scrollHeight: 2000 })); // Expected output: true (100 px left)
console.log(shouldLoadMore({ scrollTop: 1300, clientHeight: 500, scrollHeight: 2000 })); // Expected output: true (exactly 200 px left)

// A fake server with 25 items; it returns one page at a time
const ALL_ITEMS = Array.from({ length: 25 }, (_, i) => `item ${i + 1}`); // "item 1" ... "item 25"
const fakeServer = async (page, pageSize) => {      // mimics GET /api/items?page=&limit=
  const start = (page - 1) * pageSize;             // index of the first item on this page
  return ALL_ITEMS.slice(start, start + pageSize); // up to pageSize items; fewer on the last page
};

// Basic paging loop: keep asking for the next page until a page comes back short
(async () => {
  const items = [];                                 // everything loaded so far
  let page = 1;                                     // page numbers start at 1
  while (true) {                                    // loop until we break out
    const batch = await fakeServer(page, 10);       // ask for 10 items
    items.push(...batch);                           // add the new items to the list
    console.log(`page ${page}: got ${batch.length}, total ${items.length}`); // show progress
    if (batch.length < 10) break;                   // a short page means there is nothing after it
    page++;                                         // move on to the next page
  }
})();
// Expected output:
// page 1: got 10, total 10
// page 2: got 10, total 20
// page 3: got 5, total 25
```

## 💻 Code Example — Advanced
```javascript
// shouldLoadMore: same pure decision as the basic example
function shouldLoadMore({ scrollTop, clientHeight, scrollHeight }, threshold = 200) {
  return scrollHeight - (scrollTop + clientHeight) <= threshold; // within threshold px of the end
}

// createInfiniteList: a controller with guards for duplicates, the end, errors, and stale responses
function createInfiniteList({ fetchPage, pageSize = 10, threshold = 200 }) {
  const state = {
    items: [],                                      // loaded items, in order
    page: 1,                                        // next page to request
    loading: false,                                 // true while a request is in flight
    hasMore: true,                                  // false once a short page arrives
    error: null,                                    // last error, cleared on the next attempt
    generation: 0,                                  // changes on reset so stale responses can be ignored
  };

  async function loadNext() {
    if (state.loading || !state.hasMore) return;    // guard: one request at a time, and stop at the end
    state.loading = true;                           // mark the request as in progress
    state.error = null;                             // a new attempt clears the old error
    const generation = state.generation;            // remember which version of the list asked
    const page = state.page;                        // the page we are asking for
    try {
      const batch = await fetchPage(page, pageSize); // wait for the server
      if (generation !== state.generation) return;  // list was reset while waiting: drop this response
      state.items.push(...batch);                   // append the new items
      state.page = page + 1;                        // next time, ask for the following page
      state.hasMore = batch.length === pageSize;    // a short page means the end was reached
    } catch (err) {
      if (generation === state.generation) state.error = err; // keep the error; the next scroll retries
    } finally {
      if (generation === state.generation) state.loading = false; // only the current list clears loading
    }
  }

  return {
    onScroll(metrics) {                             // call this from a scroll handler
      return shouldLoadMore(metrics, threshold) ? loadNext() : null; // load only when near the bottom
    },
    reset() {                                       // called when the query or filter changes
      state.generation++;                           // old in-flight responses now count as stale
      Object.assign(state, { items: [], page: 1, hasMore: true, loading: false, error: null });
    },
    snapshot() {                                    // read-only view for rendering
      return { items: [...state.items], hasMore: state.hasMore, loading: state.loading, error: state.error && state.error.message };
    },
  };
}

// Test 1: near/far scrolls, the end of the data, and the duplicate guard
const ALL = Array.from({ length: 25 }, (_, i) => `item ${i + 1}`); // 25 fake items
let calls = 0;                                      // counts real server requests
const fetchPage = async (page, pageSize) => {
  calls++;                                          // one request to the server
  const start = (page - 1) * pageSize;              // first index of the page
  return ALL.slice(start, start + pageSize);        // the items for this page
};
const near = { scrollTop: 1500, clientHeight: 500, scrollHeight: 2000 }; // 0 px from the bottom
const far = { scrollTop: 0, clientHeight: 500, scrollHeight: 2000 };     // 1500 px from the bottom

const feed = createInfiniteList({ fetchPage, pageSize: 10, threshold: 200 });
(async () => {
  await feed.onScroll(far);                         // far from the bottom: no request
  console.log("after far scroll:", calls, feed.snapshot().items.length); // Expected output: after far scroll: 0 0
  await feed.onScroll(near);                        // loads page 1
  await feed.onScroll(near);                        // loads page 2
  await feed.onScroll(near);                        // loads page 3 (5 items): end reached
  await feed.onScroll(near);                        // hasMore is false: no request
  const s = feed.snapshot();
  console.log("calls:", calls, "items:", s.items.length, "hasMore:", s.hasMore); // Expected output: calls: 3 items: 25 hasMore: false

  // Test 2: two scroll events at once send one request (duplicate guard)
  feed.reset();                                     // start over from page 1
  calls = 0;                                        // count only the new requests
  const a = feed.onScroll(near);                    // starts page 1 and sets loading = true
  const b = feed.onScroll(near);                    // sees loading = true and returns null
  await Promise.all([a, b]);                        // wait for both calls
  console.log("concurrent calls:", calls, feed.snapshot().items.length); // Expected output: concurrent calls: 1 10
})();

// Test 3: a reset while a request is in flight makes the old response stale
const slow = createInfiniteList({
  fetchPage: (page, n) => new Promise((resolve) => setTimeout(() => resolve(ALL.slice(0, n)), 20)), // 20 ms
  pageSize: 10,
});
(async () => {
  const inFlight = slow.onScroll(near);            // request for page 1 starts; it takes 20 ms
  slow.reset();                                     // the user searched again: list is cleared
  await inFlight;                                   // the old response arrives, but it must be ignored
  console.log("stale items:", slow.snapshot().items.length); // Expected output: stale items: 0
})();

// Time:  O(p) per request to append p items; the guards are O(1)
// Space: O(n) for all loaded items; the controller itself is O(1) extra
```

### Edge Cases
```javascript
// shouldLoadMore: the same check as in the advanced example, repeated so this block runs alone
function shouldLoadMore({ scrollTop, clientHeight, scrollHeight }, threshold = 200) {
  return scrollHeight - (scrollTop + clientHeight) <= threshold; // within threshold px of the end
}

// Edge 1: content shorter than the screen gives a negative distance, so the first page loads right away
console.log(shouldLoadMore({ scrollTop: 0, clientHeight: 500, scrollHeight: 300 })); // Expected output: true

// Edge 2: an empty list (all zeros) counts as "at the bottom", so the first page is requested
console.log(shouldLoadMore({ scrollTop: 0, clientHeight: 0, scrollHeight: 0 }));     // Expected output: true

// Edge 3: a page is "full" only when it has pageSize items; a short or empty page means the end
const hasMoreAfter = (batch, pageSize) => batch.length === pageSize; // true when another page may exist
console.log([hasMoreAfter(new Array(10).fill("x"), 10), hasMoreAfter(["x"], 10), hasMoreAfter([], 10)]); // Expected output: [ true, false, false ]
```

---

## 🧠 Tricky Interview Question
```javascript
let requestCount = 0;                               // counts server requests for this question
const pagedFetch = async (page) => { requestCount++; return page < 3 ? ["a"] : []; }; // pages 1 and 2 have 1 item
const tricky = createInfiniteList({ fetchPage: pagedFetch, pageSize: 1 }); // createInfiniteList from the advanced example
const bottom = { scrollTop: 90, clientHeight: 10, scrollHeight: 100 };     // 0 px from the bottom

(async () => {
  await Promise.all([tricky.onScroll(bottom), tricky.onScroll(bottom), tricky.onScroll(bottom)]); // three scroll events
  console.log(requestCount, tricky.snapshot().items.length, tricky.snapshot().hasMore); // line 1
  await tricky.onScroll(bottom);                                              // one more scroll
  console.log(requestCount, tricky.snapshot().items.length, tricky.snapshot().hasMore); // line 2
  await tricky.onScroll(bottom);                                              // and one more
  console.log(requestCount, tricky.snapshot().items.length, tricky.snapshot().hasMore); // line 3
})();
```
Answer:
```
1 1 true
2 2 true
3 2 false
```
Paste this after the advanced example, because it reuses `createInfiniteList`. Three scroll events arrive at once, but the first one sets `loading = true`, so the other two return `null` without sending a request. `Promise.all` waits only for the first request, so line 1 shows one call and one item. Each later scroll loads one page. Page 3 returns an empty array, which is shorter than `pageSize`, so `hasMore` becomes false and the list stops asking.

---

## 🟠 Express.js Integration
The server side of infinite scroll is a paged endpoint. It returns the page, the next page number, and whether more data exists. Asking for `limit + 1` rows is a common trick: if the extra row comes back, another page exists, and the extra row is not sent to the client.

```javascript
// Express.js: GET /api/feed?page=2&limit=10 returns one page of an infinite list
const express = require("express");                 // web framework (install with: npm i express)
const app = express();                              // create the app

// Stand-in for a database call; a real app would run SQL with LIMIT and OFFSET
const db = {
  query: async (sql, params) => Array.from({ length: params[0] }, (_, i) => ({ id: params[1] + i + 1 })),
};

app.get("/api/feed", async (req, res) => {          // handler for one page of the feed
  // Clamp the query values so a client cannot ask for a huge page or a negative offset
  const page = Math.max(1, parseInt(req.query.page, 10) || 1);     // default page 1
  const limit = Math.min(50, Math.max(1, parseInt(req.query.limit, 10) || 10)); // 1..50, default 10
  const offset = (page - 1) * limit;                // rows to skip before this page

  // Fetch one extra row to learn whether a next page exists, without a separate COUNT query
  const rows = await db.query("SELECT id FROM feed LIMIT ? OFFSET ?", [limit + 1, offset]);
  const hasMore = rows.length > limit;              // true when the extra row came back
  res.json({
    items: rows.slice(0, limit),                    // send only the requested number of rows
    nextPage: hasMore ? page + 1 : null,            // the client asks for this next
    hasMore,                                        // the client stops when this is false
  });
});

app.listen(3000, () => console.log("Feed API on 3000")); // start the server
```

---

## 🌐 Browser Version (HTML, not run with node)
This page uses `IntersectionObserver` on an empty sentinel element at the bottom of the list. The browser calls the callback when the sentinel gets close to the visible area, which is the browser equivalent of the `shouldLoadMore` check. Save it as an `.html` file and open it in a browser to see it work.

```html
<!-- Browser version: NOT run with node. Save as a .html file and open it in a browser. -->
<!doctype html>
<html>
<head>
  <meta charset="utf-8">                                        <!-- text encoding for Hindi and other scripts -->
  <title>Infinite scroll demo</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 0; }    /* simple page layout */
    #list { height: 90vh; overflow-y: auto; }                 /* the scrolling box */
    .row { padding: 12px 16px; border-bottom: 1px solid #ddd; } /* one item */
    #status { padding: 8px 16px; color: #666; }               /* loading or end message */
  </style>
</head>
<body>
  <div id="list"></div>                                       <!-- items are added here -->
  <div id="status">Loading...</div>                           <!-- status text -->
  <script>
    const PAGE_SIZE = 10;                                     // items per request
    const TOTAL = 45;                                         // pretend the server has 45 items
    let page = 1, loading = false, hasMore = true;            // the same state as the node version
    const list = document.getElementById("list");             // scrolling container
    const status = document.getElementById("status");         // status text element

    // Fake server call: resolves after 400 ms with one page of items
    function fetchPage(p) {
      return new Promise((resolve) => setTimeout(() => {
        const start = (p - 1) * PAGE_SIZE;                    // first index of this page
        const end = Math.min(start + PAGE_SIZE, TOTAL);       // do not go past the last item
        resolve(Array.from({ length: Math.max(0, end - start) }, (_, i) => `Item ${start + i + 1}`));
      }, 400));
    }

    // Sentinel: an empty element at the end of the list; the observer watches it
    const sentinel = document.createElement("div");           // element used only as a marker
    list.appendChild(sentinel);                               // it always stays at the bottom

    async function loadNext() {
      if (loading || !hasMore) return;                        // same guards as the node version
      loading = true;                                         // one request at a time
      status.textContent = "Loading...";                      // show progress
      try {
        const items = await fetchPage(page);                  // ask for the next page
        for (const text of items) {                           // add each item before the sentinel
          const row = document.createElement("div");          // new row element
          row.className = "row";                              // style it
          row.textContent = text;                             // set the text safely (no HTML injection)
          list.insertBefore(row, sentinel);                   // place it above the sentinel
        }
        page++;                                               // next time ask for the following page
        hasMore = items.length === PAGE_SIZE;                 // a short page means the end
        status.textContent = hasMore ? "" : "No more items";  // message at the end
        if (!hasMore) observer.disconnect();                  // stop watching once there is nothing more
      } finally {
        loading = false;                                      // always clear the flag, even on error
      }
    }

    // IntersectionObserver: call loadNext when the sentinel comes within 200 px of the visible box
    const observer = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) loadNext();  // the user reached the bottom
    }, { root: list, rootMargin: "200px" });                  // rootMargin is the 200 px threshold
    observer.observe(sentinel);                               // start watching
    loadNext();                                               // load the first page right away
  </script>
</body>
</html>
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Sending a request on every scroll event with no guard
✅ Correct: scroll events can fire many times per second. Use a `loading` flag so only one request runs at a time.

```javascript
// Wrong: every scroll event starts a new request
let calls = 0;                                      // counts requests sent to the server
const fetchItems = async () => { calls++; return ["x"]; }; // one request
const onScrollWrong = () => fetchItems();           // no guard at all
Promise.all([onScrollWrong(), onScrollWrong(), onScrollWrong()])
  .then(() => console.log("requests:", calls));     // Expected output: requests: 3
```

```javascript
// Right: a loading flag blocks the duplicates
let calls = 0;                                      // counts requests sent to the server
const fetchItems = async () => { calls++; return ["x"]; }; // one request
let loading = false;                                // true while a request is running
const onScrollRight = async () => {
  if (loading) return;                              // already loading: ignore this scroll event
  loading = true;                                   // lock
  try { await fetchItems(); } finally { loading = false; } // unlock when done
};
Promise.all([onScrollRight(), onScrollRight(), onScrollRight()])
  .then(() => console.log("requests:", calls));     // Expected output: requests: 1
```

❌ **Mistake 2:** Checking for exact bottom with `===`
✅ Correct: on zoomed screens or with fractional pixels, `scrollTop + clientHeight` may never equal `scrollHeight`. Use a threshold.

```javascript
// Wrong: exact equality misses a 0.5 px gap
const m = { scrollTop: 1499.5, clientHeight: 500, scrollHeight: 2000 };
console.log(m.scrollTop + m.clientHeight === m.scrollHeight); // Expected output: false

// Right: a threshold check works with fractions
const threshold = 200;
console.log(m.scrollHeight - (m.scrollTop + m.clientHeight) <= threshold); // Expected output: true
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you decide when to load the next page?**
A1: Compute the distance to the bottom as `scrollHeight - (scrollTop + clientHeight)`, and load when it is at most a threshold such as 200 px. Do not use exact equality, because fractional pixels can make it never true.

**Q2: How do you stop duplicate requests when scroll events fire rapidly?**
A2: Keep a `loading` flag. Set it before the request, and return early while it is true. Clear it in `finally`, so an error does not leave the list stuck.

**Q3: How do you know when the data has ended?**
A3: The server can say so directly with `hasMore`. Without that, a page shorter than `pageSize` means the end. Asking for `limit + 1` rows on the server gives the answer without a separate count query.

**Q4: What is a stale response, and how do you handle it?**
A4: A response for an old query that arrives after the user changed the query. Use a generation counter: each reset increments it, and a response is applied only if the generation still matches the one it started with.

**Q5: Why is infinite scroll sometimes a poor choice?**
A5: Users cannot reach the footer or jump to a page, the scroll position is hard to restore after navigation, and very long lists need virtualization so the DOM does not grow without limit.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The list is long, the user browses it in order, and the server supports paging
- Content is a feed where users rarely need the footer or a page number
- You need to keep the scroll position while new items arrive

❌ Avoid when:
- Users need to jump to a specific page, or to reach the footer
- The data is short; load it all at once
- Users must find an item by position in the list, such as in a long reference table; use paging or a virtual list

---

## 📊 Visual Diagram
```
scrollTop=1300, clientHeight=500, scrollHeight=2000
distance = 2000 - (1300 + 500) = 200  <= threshold 200  -> loadNext()

scroll near, loading? no  -> request page N -> items added -> page N+1
scroll near, loading? yes -> ignored
reset (generation changed) -> old response ignored
error -> loading false, error saved -> next scroll retries
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Infinite scroll | Load the next batch near the bottom | आख़िर के पास अगला batch लोड करना |
| Threshold | Distance from the bottom that starts a load | Load शुरू करने वाली bottom से दूरी |
| Sentinel | An empty element used as a marker at the end | अंत पर रखा खाली marker element |
| Duplicate guard | A flag that blocks a second request | दूसरी request रोकने वाला flag |
| Generation | A counter that changes on reset | Reset पर बदलने वाला counter |
| Stale response | An old response that arrives after a reset | Reset के बाद आने वाला पुराना response |
| hasMore | Whether the server has another page | Server के पास और page है या नहीं |

---

## ⚡ 3-Line Summary
English:
1. Load the next page when the distance to the bottom is within a threshold, not on exact equality.
2. Guard against duplicate requests with a loading flag, and stop when a page is short.
3. Ignore stale responses with a generation counter, and let the next scroll retry after an error.

Hindi:
1. Bottom से दूरी threshold के अंदर हो तो अगला page लोड करो, exact बराबरी पर नहीं।
2. Loading flag से duplicate requests रोको, और छोटा page आए तो रुक जाओ।
3. Generation counter से पुराने responses नज़रअंदाज़ करो, और error के बाद अगला scroll फिर कोशिश करे।

---

## ➡️ Next Topic
**200. Build Simple State Manager** — an infinite list keeps items, loading, and errors in several places. The next topic puts that kind of state in one store, with subscribers that re-render when it changes.
