# 81. Pagination in React
# हिंदी में: React में Pagination — Data को pages में बाँटकर दिखाना

---

## 🔵 Simple Definition (English)
Pagination ka matlab hai bahut saara data ek saath dikhane ke bajaye chhote pages mein dikhana, jaise "Page 1, 2, 3". React mein page number ya cursor ko state mein rakhte hain, har change par server se sirf us page ka data fetch karte hain, aur page number URL mein sync karte hain.

## 🔵 सरल परिभाषा (Hindi)
Pagination का मतलब है बहुत सारा data एक साथ दिखाने की बजाय छोटे pages में दिखाना, जैसे "Page 1, 2, 3"। React में हम page number या cursor को state में रखते हैं, हर बदलाव पर server से सिर्फ उस page का data fetch करते हैं, और page number को URL में sync करते हैं।

---

## 🔴 Problem it Solves
Agar 2 lakh orders ek API response mein bhejo, to network slow hoga, browser memory bharega, aur page freeze ho sakta hai. Pagination server aur client dono ka kaam kam karta hai. Iske saath do sawal aate hain: page number URL mein kaise rahe (refresh par wahi page dikhe), aur filter badalne par page 1 par wapas kaise jaaye. Aur server ko bhi sure hona chahiye ki `limit` ki koi upper limit ho, warna koi bhi `limit=1000000` bhej kar server ko bhar sakta hai.

## 🔴 यह क्यों बना? (Hindi)
अगर 2 lakh orders एक API response में भेजो, तो network धीमा होगा, browser की memory भरेगी, और page freeze हो सकता है। Pagination server और client दोनों का काम कम करता है। इसके साथ दो सवाल आते हैं: page number URL में कैसे रहे (refresh पर वही page दिखे), और filter बदलने पर page 1 पर वापस कैसे जाएँ। और server को यह भी पक्का करना चाहिए कि `limit` की upper limit हो, वरना कोई `limit=1000000` भेजकर server को भर सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → page (current page) aur pageSize state mein rakho, URL se init karo
Step 2 → Page badlne par API call: GET /api/orders?page=2&limit=10
Step 3 → Server: OFFSET = (page - 1) * limit, LIMIT = limit, aur total count bhejo
Step 4 → Client: totalPages = Math.ceil(total / pageSize)
Step 5 → Page number URL mein sync karo (setSearchParams)
Step 6 → Filter badle to page = 1 reset karo; page > totalPages ho to clamp karo
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → page (current page) और pageSize state में रखो, URL से initialize करो
Step 2 → Page बदलने पर API call: GET /api/orders?page=2&limit=10
Step 3 → Server: OFFSET = (page - 1) * limit, LIMIT = limit, और total count भेजो
Step 4 → Client: totalPages = Math.ceil(total / pageSize)
Step 5 → Page number को URL में sync करो (setSearchParams)
Step 6 → Filter बदले तो page = 1 reset करो; page > totalPages हो तो clamp करो
```

---

## 🟡 Real World Example
**Swiggy order history:** User "My Orders" page par hai. Har page par 10 orders dikhte hain, neeche "1 2 3 ... 12" buttons hain. User page 3 par jaata hai, URL `/orders?page=3` ban jaata hai, aur refresh karne par bhi page 3 hi khulta hai. Status filter "Delivered" lagane par page 1 se shuru hota hai, kyunki purane page ke number naye filter mein galat hote.

## 🟡 Real Example Hindi mein
**Swiggy order history:** User "My Orders" page पर है। हर page पर 10 orders दिखते हैं, नीचे "1 2 3 ... 12" buttons हैं। User page 3 पर जाता है, URL `/orders?page=3` बन जाता है, और refresh करने पर भी page 3 ही खुलता है। Status filter "Delivered" लगाने पर page 1 से शुरू होता है, क्योंकि पुराने page number नए filter में गलत होंगे।

---

## 💻 Code Example — Basic

```jsx
import { useEffect, useState } from 'react';              // hooks

// ── BASIC PAGINATION ──────────────────────────────────
const PAGE_SIZE = 10;                                     // items per page

function OrderList() {
  const [page, setPage] = useState(1);                    // current page number (starts at 1)
  const [orders, setOrders] = useState([]);               // rows for this page only
  const [total, setTotal] = useState(0);                  // total number of rows on the server

  useEffect(() => {
    let ignore = false;                                   // guards against out-of-order responses
    fetch(`/api/orders?page=${page}&limit=${PAGE_SIZE}`)  // request just this page
      .then(res => res.json())                            // parse JSON: { items, total }
      .then(data => {                                     // data arrived
        if (!ignore) {                                    // only apply the latest request
          setOrders(data.items);                          // replace the list with this page
          setTotal(data.total);                           // update the total count
        }
      });
    return () => { ignore = true; };                      // cleanup: mark old response as stale
  }, [page]);                                             // refetch whenever page changes

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE)); // at least 1 page, even if empty

  return (
    <div>
      <ul>
        {orders.map(o => <li key={o.id}>{o.id} — ₹{o.amount}</li>)} {/* one row per order */}
      </ul>
      <button onClick={() => setPage(p => p - 1)} disabled={page <= 1}>Prev</button> {/* can't go below 1 */}
      <span> Page {page} of {totalPages} </span>          {/* "Page 2 of 5" */}
      <button onClick={() => setPage(p => p + 1)} disabled={page >= totalPages}>Next</button> {/* stop at last page */}
    </div>
  );
}

export default OrderList;                                 // make it importable
```

## 💻 Code Example — Advanced

```jsx
import { useEffect, useMemo, useState } from 'react';     // hooks
import { useSearchParams } from 'react-router-dom';       // URL query string helper (React Router v6)

const MAX_PAGE_SIZE = 50;                                 // never let the client ask for more

// Build the visible page-number window: 1 ... 4 5 [6] 7 8 ... 20
function pageWindow(current, last) {
  const pages = new Set([1, last, current, current - 1, current + 1]); // always keep these
  return [...pages]
    .filter(p => p >= 1 && p <= last)                     // stay in range
    .sort((a, b) => a - b);                               // ascending order
}

export function OrderTable({ status }) {
  const [searchParams, setSearchParams] = useSearchParams(); // URL is the source of truth
  const page = Math.max(1, Number(searchParams.get('page')) || 1); // parse, default 1, never below 1
  const pageSize = Math.min(MAX_PAGE_SIZE, Number(searchParams.get('size')) || 10); // clamp size
  const [data, setData] = useState({ items: [], total: 0 }); // server response
  const [error, setError] = useState(null);               // error message, if any

  useEffect(() => {
    const controller = new AbortController();             // cancel the old request on change
    const qs = new URLSearchParams({ page, limit: pageSize, status }); // build query string
    fetch(`/api/orders?${qs}`, { signal: controller.signal }) // request this page
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`); // turn 4xx/5xx into an error
        return res.json();                                // parse the body
      })
      .then(json => { setData(json); setError(null); })   // store data, clear old error
      .catch(err => { if (err.name !== 'AbortError') setError(err.message); }); // ignore cancels
    return () => controller.abort();                      // cleanup on change or unmount
  }, [page, pageSize, status]);                           // refetch on any of these changes

  const totalPages = Math.max(1, Math.ceil(data.total / pageSize)); // derived, not stored
  const pages = useMemo(() => pageWindow(page, totalPages), [page, totalPages]); // window only when inputs change

  // Clamp: if the total shrank (e.g. a filter), jump to the last valid page
  useEffect(() => {
    if (page > totalPages) setSearchParams(prev => { // URL update only
      prev.set('page', String(totalPages));              // last valid page
      return prev;                                       // new query string
    }, { replace: true });                                // replace history, no extra back entry
  }, [page, totalPages, setSearchParams]);

  function goTo(p) {
    setSearchParams(prev => {                             // keep other params (filters, size)
      prev.set('page', String(p));                        // set the new page number
      return prev;                                        // return the updated params
    });
  }

  if (error) return <p role="alert">Could not load orders: {error}</p>; // error state
  return (
    <div>
      {data.items.map(o => <div key={o.id}>{o.id}</div>)} {/* rows for this page */}
      <nav aria-label="Pagination">                       {/* accessible wrapper */}
        <button onClick={() => goTo(page - 1)} disabled={page <= 1}>Prev</button>
        {pages.map(p => (                                 // numbered buttons
          <button key={p} aria-current={p === page ? 'page' : undefined} onClick={() => goTo(p)}>
            {p}
          </button>
        ))}
        <button onClick={() => goTo(page + 1)} disabled={page >= totalPages}>Next</button>
      </nav>
    </div>
  );
}
```

---

## 🟠 Real app integration

Express endpoint with limit clamping and offset math:

```javascript
const express = require('express');                       // web framework
const app = express();                                    // create the app
// db is a pg Pool created elsewhere

app.get('/api/orders', async (req, res) => {              // GET /api/orders?page=&limit=&status=
  const page = Math.max(1, parseInt(req.query.page, 10) || 1);       // integer, minimum 1
  const limit = Math.min(50, Math.max(1, parseInt(req.query.limit, 10) || 10)); // clamp 1..50
  const status = typeof req.query.status === 'string' ? req.query.status : null; // optional filter
  const offset = (page - 1) * limit;                      // skip the rows of earlier pages

  const [rowsResult, countResult] = await Promise.all([    // two queries in parallel
    db.query(
      `SELECT id, amount, status FROM orders
       WHERE ($1::text IS NULL OR status = $1)
       ORDER BY created_at DESC, id DESC                   -- stable order, ties broken by id
       LIMIT $2 OFFSET $3`,                               // parameterized values only
      [status, limit, offset]
    ),
    db.query(`SELECT COUNT(*)::int AS total FROM orders WHERE ($1::text IS NULL OR status = $1)`, [status]), // total rows
  ]);

  res.json({                                              // response shape used by the client
    items: rowsResult.rows,                               // this page only
    total: countResult.rows[0].total,                     // total across all pages
    page,                                                 // echo the page we used
    limit,                                                // echo the limit we used
  });
});
```

Next.js App Router (page number comes from the URL, read on the server):

```jsx
// app/orders/page.js — Server Component
import { getOrders } from '@/lib/orders';                 // your data helper (DB call)

export default async function Page({ searchParams }) {    // Next.js 15+: searchParams is a Promise
  const params = await searchParams;                      // must await before reading
  const page = Math.max(1, Number(params.page) || 1);     // safe number, minimum 1
  const { items, total } = await getOrders({ page, limit: 10 }); // fetch only this page
  return (
    <main>
      {items.map(o => <p key={o.id}>{o.id}</p>)}          {/* rows rendered on the server */}
      <p>Page {page} of {Math.ceil(total / 10)}</p>       {/* totals from the same query */}
    </main>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** URL query values are strings, so `+ 1` concatenates
✅ **Correct:** Convert with `Number()` before doing math.

```jsx
// Wrong: page is the string "2", so "2" + 1 becomes "21"
const page = searchParams.get('page') || 1;             // "2" from the URL
setSearchParams({ page: page + 1 });                    // ❌ page=21

// Right: convert to a number first
const pageNum = Number(searchParams.get('page')) || 1;  // 2
setSearchParams({ page: String(pageNum + 1) });    // ✅ page=3
```

❌ **Mistake 2:** Not resetting the page when a filter changes (empty result pages)
✅ **Correct:** Reset to page 1 in the same update that changes the filter.

```jsx
// Wrong: user is on page 7, switches the filter, and the new result has 2 pages
setStatus('delivered');                                  // ❌ page is still 7 → empty screen

// Right: change the filter and the page together
function changeStatus(next) {
  setSearchParams({ status: next, page: '1' });         // ✅ one URL update, page reset
}
```

❌ **Mistake 3:** Trusting `limit` from the client
✅ **Correct:** Clamp it on the server (and the client), because a bad client can ask for anything.

```javascript
// Wrong: the client controls how many rows the DB returns
const rows = await db.query('... LIMIT $1', [req.query.limit]); // ❌ limit=1000000

// Right: clamp it to a safe range
const limit = Math.min(50, Math.max(1, parseInt(req.query.limit, 10) || 10)); // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
function Pager() {
  const [searchParams, setSearchParams] = useSearchParams(); // URL: /orders?page=2
  const page = searchParams.get('page') || 1;             // read the current page
  return (
    <button onClick={() => setSearchParams({ page: page + 1 })}>
      Next
    </button>
  );
}
// The URL is /orders?page=2. The user clicks Next once. What is the new URL?
```

**Answer:** The new URL is `/orders?page=21`. `searchParams.get()` always returns a string, so `page` is `"2"`, not the number `2`. The `+` operator concatenates when one side is a string: `"2" + 1` gives `"21"`. The `|| 1` fallback only applies when the parameter is missing, so with no `page` in the URL the result would be `1 + 1 = 2`, which is correct by luck. The fix is `Number(...)` before the addition, and `String(...)` when you write it back.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between offset and cursor pagination?**
A1: Offset pagination uses `LIMIT` and `OFFSET` (for example `OFFSET 20`). It can jump to any page, but the database still scans the skipped rows, and data changes shift the pages. Cursor pagination uses the last seen key (`WHERE id < cursor`). It is fast and stable, but you cannot jump to page 50 directly.

**Q2: Why keep the page number in the URL instead of only in state?**
A2: The URL survives refresh, can be shared, and works with the browser's back button. Keep the URL as the source of truth and derive the page from it, so there is no second copy of the state to get out of sync.

**Q3: How do you compute the total number of pages?**
A3: `Math.ceil(total / pageSize)`, computed from the server's `total` count. Use `Math.max(1, ...)` so an empty result still shows page 1. Derive it during render instead of storing it in state.

**Q4: How do you avoid showing stale data when the user clicks quickly?**
A4: Cancel the previous request with `AbortController` in the effect cleanup, or ignore responses with an `ignore` flag. Otherwise an older slow response can overwrite a newer one.

**Q5: Why must the server cap the page size?**
A5: The client can send any `limit` value. Without a cap, one request can ask for millions of rows and exhaust the database or the server memory. Clamp the value on the server, and use a stable `ORDER BY` so pages do not overlap.

---

## 🔷 When to Use + When Not to Use

✅ **Use when:**
- The user needs numbered pages, such as admin tables, order history, or search results
- You want to jump to a specific page or see the total count
- Data is large and changes rarely, so offset stays cheap

❌ **Avoid when:**
- The feed is endless and users only scroll (use infinite scroll with a cursor, topic 80)
- Data changes very fast and users must not miss rows (cursor pagination is safer)
- The dataset is small enough to send in one request and filter on the client

---

## 📊 Visual Diagram

```
URL: /orders?status=delivered&page=3
               │
               ▼
   useSearchParams()  ──► page = 3, pageSize = 10
               │
               ▼
   GET /api/orders?page=3&limit=10
               │
               ▼
   SQL: ... ORDER BY created_at DESC, id DESC  LIMIT 10 OFFSET 20
               │
               ▼
   { items: [rows 21..30], total: 117 }
               │
               ▼
   totalPages = ceil(117 / 10) = 12
   render:  [Prev] 1 2 [3] 4 ... 12 [Next]
               │ user clicks "4"
               ▼
   setSearchParams({ page: 4 })  ──► URL changes ──► effect runs again
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pagination | Data ko pages mein todna | Data को pages में बाँटना |
| Offset | Kitne rows skip karne hain | कितनी rows skip करनी हैं |
| Limit | Ek page mein kitne rows | एक page में कितनी rows |
| Total pages | `Math.ceil(total / limit)` | कुल pages की संख्या |
| Clamp | Value ko ek range mein rakhna | Value को एक range में रखना |
| Source of truth | Jis jagah ki value sach maani jaati hai | जिस जगह की value सच मानी जाती है |

---

## ⚡ 3-Line Summary
**English:**
1. Page number state ya URL mein rakho, aur server se sirf us page ka data fetch karo.
2. Query strings string hoti hain, isliye `Number()` se convert karo, aur `limit` ko server par clamp karo.
3. Filter badle to page 1 par reset karo, aur total pages `Math.ceil` se derive karo.

**Hindi:**
1. Page number state या URL में रखो, और server से सिर्फ उस page का data fetch करो।
2. Query strings string होती हैं, इसलिए `Number()` से convert करो, और `limit` को server पर clamp करो।
3. Filter बदले तो page 1 पर reset करो, और total pages `Math.ceil` से derive करो।

---

## ➡️ Next Topic
**82. Debounce in React** — search input par har keystroke par API call रोकना, और सिर्फ आखिरी value पर कॉल करना।
