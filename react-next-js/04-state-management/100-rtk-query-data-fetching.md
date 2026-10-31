# 100. RTK Query — Data Fetching
# हिंदी में: RTK Query — Data Fetching (server data को Redux में cache करना)

---

## 🔵 Simple Definition (English)
**RTK Query** is the data-fetching and caching layer that ships with Redux Toolkit. You describe your API as **endpoints** using `createApi`, and RTK Query gives you auto-generated hooks (for example `useGetRestaurantQuery`), caching, deduplication, refetching, and loading/error state, without writing thunks or reducers by hand.

## 🔵 सरल परिभाषा (Hindi)
**RTK Query** Redux Toolkit के साथ आने वाली data-fetching और caching layer है। `createApi` से आप अपनी API को **endpoints** के रूप में लिखते हैं, और RTK Query अपने आप hooks (जैसे `useGetRestaurantQuery`), caching, duplicate request रोकना, refetch, और loading/error state देता है। इसके लिए हाथ से thunk या reducer लिखने की ज़रूरत नहीं।

---

## 🔴 Problem it Solves
`createAsyncThunk` से हर API के लिए pending/fulfilled/rejected reducer लिखना पड़ता है। फिर cache कौन करेगा? दो components एक ही data मांगें तो दो बार request जाती है। Data बदलने के बाद दूसरी जगह की list stale रहती है। Loading और error flags हर जगह copy होते हैं।

**Swiggy example:** Restaurant card, menu page और cart badge तीनों एक ही restaurant का data दिखाते हैं। RTK Query इसे एक बार fetch करता है, cache में रखता है, और तीनों components एक ही cache entry से पढ़ते हैं।

## 🔴 यह क्यों बना? (Hindi)
Server data और client state अलग चीज़ें हैं। Server data "बाहर से आता है", बासी हो सकता है, और उसे बार-बार fetch करना पड़ता है। RTK Query server data के लिए एक ready-made system देता है, ताकि developer business logic पर ध्यान दे, cache-management के boilerplate पर नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → createApi() में baseQuery और endpoints define करो
         getRestaurant: build.query({ query: (id) => `/restaurants/${id}` })

Step 2 → Store में api.reducer और api.middleware जोड़ो
         api.middleware cache lifetime, polling और invalidation संभालता है

Step 3 → Component hook call करता है: useGetRestaurantQuery('R-42')
         Hook cache entry बनाता है या existing entry से पढ़ता है

Step 4 → Same args पर दूसरी request pending हो तो RTK Query नई request नहीं भेजता
         (deduplication)

Step 5 → Mutation (POST/PUT/DELETE) के tags invalidate होते हैं
         → संबंधित queries अपने आप refetch होती हैं
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → createApi में baseQuery और endpoints लिखो
Step 2 → Store में api.reducer और api.middleware जोड़ो
Step 3 → Hook call होने पर cache check होता है; नहीं मिला तो fetch
Step 4 → एक ही args की pending request दोबारा नहीं जाती (dedupe)
Step 5 → Mutation के invalidatesTags से संबंधित queries refetch होती हैं
```

---

## 🟡 Real World Example
**Swiggy restaurant page:** User restaurant खोलता है। `useGetRestaurantQuery(id)` पहली बार server से data लाता है। Menu tab और cart badge उसी cache से पढ़ते हैं, कोई दूसरी request नहीं। User "Add to cart" करता है, तो `addToCart` mutation `invalidatesTags: ['Cart']` के साथ cart query refetch करवाता है, और badge का count तुरंत सही हो जाता है।

## 🟡 Real Example Hindi mein
**Swiggy restaurant page:** User restaurant खोलता है। `useGetRestaurantQuery(id)` पहली बार server से data लाता है। Menu tab और cart badge उसी cache से data पढ़ते हैं, कोई दूसरी request नहीं जाती। User "Add to cart" दबाता है, तो `addToCart` mutation `invalidatesTags: ['Cart']` से cart query को refetch करवाता है, और badge का count तुरंत सही हो जाता है।

---

## 💻 Code Example — Basic

```javascript
// Basic: RTK Query endpoint with a custom baseQuery (no network) — ESM file (.mjs ya "type": "module")
import { configureStore } from '@reduxjs/toolkit';                 // store banane ke liye
import { createApi } from '@reduxjs/toolkit/query';                // RTK Query ka entry point
let serverHits = 0;                                                // server kitni baar hit hua, count
const api = createApi({                                            // API slice banaya
  reducerPath: 'api',                                              // store mein is key par state rahegi
  baseQuery: async (restaurantId) => {                             // custom baseQuery (fetchBaseQuery ki jagah)
    serverHits += 1;                                               // har network call par count badhao
    return { data: { id: restaurantId, name: 'Biryani House', eta: 25 } }; // success: { data }
  },
  endpoints: (build) => ({                                         // endpoints define karo
    getRestaurant: build.query({                                   // query = read operation (GET jaisa)
      query: (id) => id,                                           // baseQuery ko kya arg jaaye
    }),
  }),
});
const store = configureStore({                                     // store banaya
  reducer: { [api.reducerPath]: api.reducer },                     // { api: <cache reducer> }
  middleware: (getDefault) => getDefault().concat(api.middleware), // cache middleware jodna zaroori
});
const first = await store.dispatch(api.endpoints.getRestaurant.initiate('R-42')); // pehli baar: network
const second = await store.dispatch(api.endpoints.getRestaurant.initiate('R-42')); // cache se milega
console.log('server hits:', serverHits);                            // server hits: 1
const entry = api.endpoints.getRestaurant.select('R-42')(store.getState()); // cache entry padho
console.log(entry.status, entry.data.name, entry.data.eta);        // fulfilled Biryani House 25
// Expected output:
// server hits: 1
// fulfilled Biryani House 25
```

## 💻 Code Example — Advanced

```javascript
// Advanced: tags, mutation, invalidation, optimistic update + rollback — ESM file (.mjs)
import { configureStore } from '@reduxjs/toolkit';                 // store
import { createApi } from '@reduxjs/toolkit/query';                // RTK Query
const db = { cart: [{ id: 'P1', name: 'Paneer Tikka', qty: 1 }] }; // fake server database
const fakeServer = async ({ method, body }) => {                    // baseQuery: server ka behaviour copy
  await new Promise((resolve) => setTimeout(resolve, 50));         // network delay 50ms
  if (method === 'GET') return { data: [...db.cart] };             // GET: cart ki copy
  if (method === 'POST') {                                         // POST: item add karna
    if (body.qty > 10) return { error: { status: 400, data: 'Qty too high' } }; // validation error
    db.cart.push(body);                                            // database mein add
    return { data: body };                                         // success
  }
  return { error: { status: 404, data: 'Not found' } };            // unknown method
};

const api = createApi({
  reducerPath: 'api',                                              // state key
  baseQuery: fakeServer,                                           // hamara fake server
  tagTypes: ['Cart'],                                              // cache tags declare karo
  endpoints: (build) => ({
    getCart: build.query({
      query: () => ({ url: '/cart', method: 'GET' }),              // GET request
      providesTags: ['Cart'],                                      // yeh query "Cart" tag provide karti hai
    }),
    addToCart: build.mutation({
      query: (item) => ({ url: '/cart', method: 'POST', body: item }), // POST request
      invalidatesTags: ['Cart'],                                   // success ke baad Cart queries refetch
      async onQueryStarted(item, { dispatch, queryFulfilled }) {   // optimistic update hook
        const patch = dispatch(                                    // patch = undo karne ka handle
          api.util.updateQueryData('getCart', undefined, (draft) => {
            draft.push(item);                                      // UI mein turant add
          })
        );
        try {
          await queryFulfilled;                                    // server ka final result wait
        } catch {
          patch.undo();                                            // fail hua to rollback
        }
      },
    }),
  }),
});

const store = configureStore({
  reducer: { [api.reducerPath]: api.reducer },                     // cache reducer
  middleware: (getDefault) => getDefault().concat(api.middleware), // cache middleware
});

const main = async () => {                                         // async main
  await store.dispatch(api.endpoints.getCart.initiate());          // cart pehli baar fetch
  console.log(api.endpoints.getCart.select()(store.getState()).data.length); // 1
  await store.dispatch(api.endpoints.addToCart.initiate({ id: 'P2', name: 'Naan', qty: 2 })); // add
  console.log(api.endpoints.getCart.select()(store.getState()).data.map((i) => i.name).join(', ')); // Paneer Tikka, Naan
  const bad = await store.dispatch(api.endpoints.addToCart.initiate({ id: 'P3', name: 'Cake', qty: 99 })); // fail
  await new Promise((resolve) => setTimeout(resolve, 10));         // rollback ka time do
  console.log(bad.error.data);                                     // Qty too high
  console.log(api.endpoints.getCart.select()(store.getState()).data.length); // 2 (rollback ho gaya)
};
main();
// Expected output:
// 1
// Paneer Tikka, Naan
// Qty too high
// 2
```

---

## 🟠 Real app integration

Next.js App Router mein `createApi` ko `lib/api.js` mein rakhte hain, `fetchBaseQuery` ke saath, aur React hooks auto-generated milte hain. Yeh snippet real project ka ek hissa hai (syntax-level).

```jsx
// lib/api.js — fetchBaseQuery se real HTTP calls
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'; // React entry point
export const api = createApi({
  reducerPath: 'api',                                                   // store key
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),                       // fetch wrapper, base URL
  tagTypes: ['Cart'],                                                   // tags
  endpoints: (build) => ({
    getRestaurant: build.query({ query: (id) => `restaurants/${id}` }), // GET /api/restaurants/:id
    addToCart: build.mutation({
      query: (body) => ({ url: 'cart', method: 'POST', body }),         // POST /api/cart
      invalidatesTags: ['Cart'],                                        // cart badge refetch
    }),
  }),
});
// Auto-generated hooks: useGetRestaurantQuery, useAddToCartMutation

// components/RestaurantHeader.jsx — component mein hook use
'use client';
import { useGetRestaurantQuery, useAddToCartMutation } from '@/lib/api'; // generated hooks
export default function RestaurantHeader({ id }) {
  const { data, isLoading, isError } = useGetRestaurantQuery(id);       // cache se ya fetch karke
  const [addToCart, { isLoading: adding }] = useAddToCartMutation();    // mutation trigger
  if (isLoading) return <p>Loading...</p>;                              // spinner
  if (isError) return <p>Restaurant nahi mila.</p>;                     // error UI
  return (
    <header>
      <h1>{data.name}</h1>                                              // restaurant ka naam
      <button disabled={adding} onClick={() => addToCart({ id: data.id, qty: 1 })}>Add</button>
    </header>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** `api.middleware` store mein nahi jodna
✅ **Correct:** Cache lifetime, polling aur invalidation ke liye middleware zaroori hai

```javascript
// Wrong
const store = configureStore({
  reducer: { [api.reducerPath]: api.reducer },    // ❌ middleware missing
});

// Right
const storeFixed = configureStore({
  reducer: { [api.reducerPath]: api.reducer },
  middleware: (getDefault) => getDefault().concat(api.middleware), // ✅ cache sahi chalega
});
```

❌ **Mistake 2:** Mutation ke baad koi tag invalidate nahi karna, aur list stale rehti hai
✅ **Correct:** Mutation par `invalidatesTags` aur query par `providesTags` dono lagao

```javascript
// Wrong
const endpointsWrong = (build) => ({
  addToCart: build.mutation({
    query: (item) => ({ url: '/cart', method: 'POST', body: item }), // ❌ getCart refetch nahi hoga
  }),
});

// Right
const endpointsRight = (build) => ({
  addToCart: build.mutation({
    query: (item) => ({ url: '/cart', method: 'POST', body: item }),
    invalidatesTags: ['Cart'],                    // ✅ getCart (providesTags: ['Cart']) refetch
  }),
});
```

---

## 🧠 Tricky Interview Question

```javascript
// ESM file (.mjs) — dedupe aur cache ka test
import { configureStore } from '@reduxjs/toolkit';                 // store
import { createApi } from '@reduxjs/toolkit/query';                // RTK Query
let serverHits = 0;                                                // server calls ginne ke liye
const api = createApi({
  reducerPath: 'api',                                              // state key
  baseQuery: async (id) => {                                       // har call par 20ms ka delay
    serverHits++;                                                  // count badhao
    await new Promise((r) => setTimeout(r, 20));                   // network jaisa delay
    return { data: `item-${id}` };                                 // data return
  },
  endpoints: (b) => ({ getItem: b.query({ query: (id) => id }) }), // query endpoint
});
const store = configureStore({
  reducer: { [api.reducerPath]: api.reducer },
  middleware: (g) => g().concat(api.middleware),
});
(async () => {                                                     // async IIFE
  const p1 = store.dispatch(api.endpoints.getItem.initiate('A'));  // A: pehli request
  const p2 = store.dispatch(api.endpoints.getItem.initiate('A'));  // A: dobara, pending hai
  const p3 = store.dispatch(api.endpoints.getItem.initiate('B'));  // B: alag args
  const [r1, r2, r3] = await Promise.all([p1, p2, p3]);            // teeno ke results
  console.log(serverHits, r1.data, r2.data, r3.data);              // kya print hoga?
})();
```

**Answer:** Output is `2 item-A item-A item-B`. Reasoning: RTK Query cache key args se banati hai (`getItem("A")` aur `getItem("B")` alag entries). Jab `p2` dispatch hota hai, to `A` ki entry pehle se pending hai, isliye RTK Query nayi network call nahi karta aur usi pending request ko share karta hai (deduplication). `B` ki entry alag hai, isliye uska ek call jata hai. Total server hits = 2 (A ka ek, B ka ek), aur `p1`/`p2` dono ko same data milta hai.

---

## ⚫ Interview Questions + Answers

**Q1: RTK Query kya hai, aur createAsyncThunk se kya alag hai?**
A1: RTK Query server data fetching aur caching ke liye complete system hai: endpoints, auto hooks, cache, refetch, aur tags. `createAsyncThunk` sirf ek async action helper hai, aur cache, dedupe, invalidation sab aapko khud likhna padta hai.

**Q2: Tags kya hain aur kaise kaam karte hain?**
A2: Tags cache entries ke labels hain. Query `providesTags` se bolti hai ki woh kis label ka data hai. Mutation `invalidatesTags` se bolta hai ki kaun se labels stale ho gaye. RTK Query matching queries ko refetch kar deta hai.

**Q3: Optimistic update kaise karte hain?**
A3: Mutation ke `onQueryStarted` mein `api.util.updateQueryData` se cache ko turant change karo, `queryFulfilled` ka wait karo, aur error par `patch.undo()` call karo.

**Q4: Same args ki do requests ek saath aayein to kya hota hai?**
A4: RTK Query dedupe karta hai: pending request ko share karta hai aur naya network call nahi bhejta. Alag args ki entries alag cache hoti hain.

**Q5: Server data ko Redux store mein kyon rakhna chahiye, jab `useState` bhi hai?**
A5: Ek hi data ko kai components ko chahiye ho, cache ka lifetime (`keepUnusedDataFor`) chahiye, ya mutation ke baad automatic refetch chahiye, to RTK Query kaam aata hai. Ek component ka simple UI state `useState` mein hi achha rehta hai.

---

## 🔷 When to Use + When Not to Use

✅ **Use when:**
- REST ya GraphQL server se data laana aur cache karna hai
- Ek hi data kai components mein dikhana hai
- Mutation ke baad lists ko automatically refresh karna hai
- Loading/error flags har endpoint ke liye chahiye

❌ **Avoid when:**
- Sirf ek baar fetch karke ek component mein use karna hai: `useEffect` + `fetch` kaafi hai
- Client-only state hai (modal open, filter tab): Redux slice ya `useState`
- Server Components se data lo aur cache ki zarurat na ho: fetch seedha server par karo
- App mein sirf 1-2 API calls hain aur Redux abhi project mein nahi hai

---

## 📊 Visual Diagram

```
Component A ──┐
              │  useGetRestaurantQuery('R-42')
Component B ──┼──────────▶ Cache key: getRestaurant("R-42")
              │              │
Component C ──┘              ├── pending? → same request share (dedupe)
                             ├── cached?  → data turant
                             └── missing  → baseQuery (network)
                                              │
Mutation addToCart ──▶ invalidatesTags ['Cart'] ──▶ providesTags ['Cart'] queries refetch
                       (cart badge + cart page sahi ho jaate hain)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| createApi | API slice banane wala function | API slice बनाने वाला function |
| baseQuery | Actual network call karne wala function | असली network call करने वाला function |
| fetchBaseQuery | Built-in fetch wrapper | Built-in fetch wrapper |
| build.query | Read endpoint (cache hota hai) | Read endpoint (cache होता है) |
| build.mutation | Write endpoint (POST/PUT/DELETE) | Write endpoint |
| providesTags / invalidatesTags | Cache labels: provide aur invalidate | Cache के labels |
| Dedupe | Pending same request ko share karna | Pending request को share करना |
| updateQueryData | Cache ko manually badalna | Cache को manually बदलना |

---

## ⚡ 3-Line Summary
**English:**
1. RTK Query `createApi` se endpoints define karta hai, aur auto-generated hooks, cache, dedupe dete hain.
2. Store mein `api.reducer` aur `api.middleware` dono jaroori hain; mutation ke `invalidatesTags` se lists refresh hoti hain.
3. Server data RTK Query se aur client-only UI state `useState` ya Redux slice se rakho.

**Hindi:**
1. RTK Query `createApi` से endpoints define करता है, और auto hooks, cache, dedupe देता है।
2. Store में `api.reducer` और `api.middleware` दोनों ज़रूरी हैं; mutation के `invalidatesTags` से lists refresh होती हैं।
3. Server data RTK Query से और client-only UI state `useState` या Redux slice से रखो।

---

## ➡️ Next Topic
**101. Zustand — Complete Guide** — एक छोटी, hook-based global state library, जिसमें Redux जैसा boilerplate नहीं होता और `persist` middleware से state storage में save हो सकती है।
