# 105. When to Use Which State Manager
# हिंदी में: कब कौन सा State Manager चुनें (Decision Framework)

---

## 🔵 Simple Definition (English)
"Which state manager?" का सही जवाब एक tool नहीं, **state के type** पर निर्भर करता है। पहले state को classify करो: local UI state, shared client state, server data, URL state, या form state। फिर हर type के लिए सबसे सरल tool चुनो: `useState`, Context (कम बदलने वाली values), Zustand या Jotai (shared client state), Redux Toolkit (बड़ी team और strict patterns), और RTK Query या TanStack Query (server data)।

## 🔵 सरल परिभाषा (Hindi)
"कौन सा state manager?" का सही जवाब एक tool नहीं, **state के type** पर निर्भर करता है। पहले state को classify करो: local UI state, shared client state, server data, URL state, या form state। फिर हर type के लिए सबसे सरल tool चुनो: `useState`, Context (कम बदलने वाली values के लिए), Zustand या Jotai (shared client state), Redux Toolkit (बड़ी team और सख्त patterns), और RTK Query या TanStack Query (server data)।

---

## 🔴 Problem it Solves
टीमें अक्सर हर चीज़ को Redux में डाल देती हैं, या हर चीज़ `useState` में रखती हैं, या server data को भी global store में manually cache करती हैं। नतीजा: boilerplate बढ़ता है, bugs आते हैं (stale data, duplicate state), और performance गिरती है। समस्या tool की नहीं, **गलत जगह पर सही tool** की है।

**Swiggy example:** Restaurant list (server data) RTK Query में। Search text और sort (URL state) URL params में, ताकि link share हो सके। Cart badge (shared client state) Zustand में। "Address modal open?" (local UI) `useState` में। Checkout form (form state) react-hook-form में। हर state अपनी जगह पर।

## 🔴 यह क्यों ज़रूरी है? (Hindi)
Interview में यह सवाल सिर्फ library नाम पूछने के लिए नहीं होता। यह देखता है कि आप **state के type** को समझते हैं या नहीं। जो उम्मीदवार पहले classify करता है, वह बताता है कि किस चीज़ को global क्यों नहीं बनाना, किसे server cache में रखना, और किसे URL में।

---

## 🟢 How it Works — Step by Step

```
Step 1 → State का type पहचानो
         Kya ye server se aata hai? (server data)
         Kya ye URL mein share hona chahiye? (URL state)
         Kya ye sirf ek component ke liye hai? (local UI)
         Kya ye form input hai? (form state)
         Kya ye kai distant components ko chahiye? (shared client state)

Step 2 → Sabse chhota tool chuno
         local UI   → useState / useReducer
         URL state  → search params (router)
         form       → react-hook-form ya useState
         server     → RTK Query / TanStack Query
         shared     → Zustand / Jotai (chhota), Redux Toolkit (bada, strict)

Step 3 → Derived values store mat karo; select ya compute karo
         (total = items ka sum; state mein duplicate nahi)

Step 4 → Re-render check karo; selectors / atoms se sirf zaroori hissa lo
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → State का type पहचानो: server, URL, local UI, form, या shared client
Step 2 → हर type के लिए सबसे छोटा tool चुनो
Step 3 → Derived values को store मत करो; compute करो
Step 4 → Selectors/atoms से सिर्फ ज़रूरी हिस्सा पढ़ो
```

---

## 🟡 Real World Example
**Zomato-style order page:**
- **Server data:** Order status, restaurant info → RTK Query (cache, polling)
- **URL state:** Selected tab ("Current" / "Past"), date filter → URL search params (share और back button सही)
- **Shared client state:** Delivery address जो header, checkout और cart सब देखते हैं → Zustand
- **Local UI:** "Rating modal open?" → `useState`
- **Form state:** Review text box → react-hook-form

हर state एक जगह, और कोई भी tool दूसरे की जगह नहीं ले रहा।

## 🟡 Real Example Hindi mein
**Zomato-style order page:**
- **Server data:** Order status, restaurant info → RTK Query (cache, polling)
- **URL state:** Selected tab ("Current" / "Past"), date filter → URL search params (share और back button सही रहते हैं)
- **Shared client state:** Delivery address, जो header, checkout और cart सब देखते हैं → Zustand
- **Local UI:** "Rating modal open?" → `useState`
- **Form state:** Review text box → react-hook-form

हर state एक जगह पर है, और कोई भी tool दूसरे का काम नहीं कर रहा।

---

## 💻 Code Example — Basic

```javascript
// Basic: state type se tool chunne ka decision function — ESM file (.mjs ya "type": "module")
const recommend = (state) => {                                    // state ka description leta hai
  if (state.kind === 'server') return 'RTK Query / TanStack Query'; // API se aaya data: cache wala tool
  if (state.kind === 'url') return 'URL search params';            // filter, page, sort: link mein share ho
  if (state.kind === 'form') return 'react-hook-form ya useState';  // form input ke liye
  if (state.scope === 'local') return 'useState / useReducer';     // ek component tak seemit
  if (state.teamSize > 15 && state.needsDevtools) return 'Redux Toolkit'; // bada team + strict patterns
  return 'Zustand / Jotai';                                        // chhota shared client state
};
const cases = [                                                    // alag-alag states ke examples
  { name: 'Restaurant list', kind: 'server' },                     // API data
  { name: 'Sort by rating', kind: 'url' },                         // URL mein rakhna
  { name: 'Review textbox', kind: 'form' },                        // form input
  { name: 'Rating modal open', scope: 'local' },                   // ek component ka UI
  { name: 'Cart badge', scope: 'shared', teamSize: 4 },            // chhoti team, shared state
  { name: 'Admin audit log', scope: 'shared', teamSize: 30, needsDevtools: true }, // bada team
];
cases.forEach((c) => console.log(c.name.padEnd(20), '→', recommend(c))); // table jaisa output
// Expected output:
// Restaurant list     → RTK Query / TanStack Query
// Sort by rating      → URL search params
// Review textbox      → react-hook-form ya useState
// Rating modal open   → useState / useReducer
// Cart badge          → Zustand / Jotai
// Admin audit log     → Redux Toolkit
```

## 💻 Code Example — Advanced

```javascript
// Advanced: layered state — server cache (dedupe) aur client UI state alag-alag — ESM file (.mjs)
import { create } from 'zustand';                                  // dono layers Zustand se bani hain, par alag stores
let serverCalls = 0;                                               // server ko kitni baar call hua
const fakeApi = (url) => new Promise((resolve) => {                // fake network call (30ms)
  serverCalls += 1;                                                // call count badhao
  setTimeout(() => resolve({ url, payload: `data for ${url}` }), 30); // 30ms baad response
});

// Layer 1: SERVER STATE — cache with dedupe (RTK Query / TanStack Query ka simple version)
const useServerCache = create((set, get) => ({
  entries: {},                                                     // URL → { status, data, promise }
  fetchOnce: (url) => {                                            // ek URL, ek hi network call
    const existing = get().entries[url];                           // pehle se entry hai?
    if (existing) return existing.promise;                         // haan: wahi promise (dedupe)
    const promise = fakeApi(url).then((res) => {                   // naya request
      set((s) => ({                                                // response aaya: entry done
        entries: { ...s.entries, [url]: { status: 'done', data: res.payload, promise } },
      }));
      return res.payload;                                          // caller ko data
    });
    set((s) => ({                                                  // request shuru: entry loading
      entries: { ...s.entries, [url]: { status: 'loading', data: null, promise } },
    }));
    return promise;                                                // pehli request ka promise
  },
}));

// Layer 2: CLIENT UI STATE — sirf UI ke liye, server se koi lena dena nahi
const useUiStore = create((set) => ({
  selectedTab: 'menu',                                             // UI tab
  setTab: (tab) => set({ selectedTab: tab }),                      // tab badlo
}));

const main = async () => {                                         // async main
  const [a, b] = await Promise.all([                               // do callers, ek hi URL
    useServerCache.getState().fetchOnce('/restaurants/R1'),        // request 1
    useServerCache.getState().fetchOnce('/restaurants/R1'),        // request 2: dedupe
  ]);
  console.log(a === b, 'server calls:', serverCalls);               // true server calls: 1
  useUiStore.getState().setTab('reviews');                         // UI change
  const entry = useServerCache.getState().entries['/restaurants/R1']; // server cache padho
  console.log(useUiStore.getState().selectedTab, entry.status);    // reviews done
};
main();
// Expected output:
// true server calls: 1
// reviews done
```

---

## 🟠 Real app integration

Next.js App Router mein har state ki jagah alag hoti hai: server data Server Component mein fetch hota hai, URL filters `searchParams` mein rehte hain, aur shared UI state Client Component mein store hota hai. (Syntax-level snippet.)

```jsx
// app/orders/page.jsx — Server Component: server data + URL state
export default async function OrdersPage({ searchParams }) {        // searchParams = URL state
  const tab = searchParams.tab ?? 'current';                       // URL se tab (share ho sakta hai)
  const orders = await fetch(`${process.env.API}/orders?tab=${tab}`, { cache: 'no-store' }).then((r) => r.json());
  return <OrderList orders={orders} />;                            // data props se client ko
}

```

```jsx
// components/OrderTabs.jsx — Client Component: URL state badlna
'use client';
import { useRouter, useSearchParams, usePathname } from 'next/navigation';
export default function OrderTabs() {
  const router = useRouter();                                      // navigation helper
  const params = useSearchParams();                                // current URL params
  const pathname = usePathname();                                  // current path
  const setTab = (tab) => {                                        // tab badlo: URL update
    const next = new URLSearchParams(params.toString());           // purane params copy
    next.set('tab', tab);                                          // naya tab
    router.push(`${pathname}?${next.toString()}`);                 // URL mein state
  };
  return <nav><button onClick={() => setTab('current')}>Current</button></nav>;
}

```

```jsx
// components/AddressChip.jsx — shared client state (Zustand)
'use client';
import { useAddressStore } from '@/store/address';                 // Zustand store
export default function AddressChip() {
  const address = useAddressStore((s) => s.address);               // sirf address select
  return <span>{address?.label ?? 'Address chuno'}</span>;         // header mein dikhao
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Server data ko Redux/Zustand store mein manually daalna (loading/error/cache sab khud likhna)
✅ **Correct:** Server data ke liye RTK Query ya TanStack Query, client UI ke liye store

```javascript
// Wrong
const useRestaurants = create((set) => ({
  list: [], loading: false,
  load: async () => {
    set({ loading: true });                             // ❌ error, cache, dedupe sab missing
    const data = await fetch('/api/restaurants').then((r) => r.json());
    set({ list: data, loading: false });                // ❌ 1 min baad bhi purana data, koi refetch nahi
  },
}));

// Right
// RTK Query: createApi({ endpoints: (b) => ({ getRestaurants: b.query({ query: () => 'restaurants' }) }) })
// Component: const { data, isLoading } = useGetRestaurantsQuery();  // ✅ cache, dedupe, refetch built-in
```

❌ **Mistake 2:** Form input ya modal open state ko global store mein daalna
✅ **Correct:** Jo state ek component ya ek form tak seemit hai, use local rakho

```jsx
// Wrong
const useGlobal = create((set) => ({
  reviewText: '',                                       // ❌ sirf ek textbox ke liye global store
  setReviewText: (t) => set({ reviewText: t }),         // har keystroke par poori store update
}));

// Right
function ReviewBox() {
  const [text, setText] = useState('');                 // ✅ local: component ke saath hi khatm
  return <textarea value={text} onChange={(e) => setText(e.target.value)} />;
}
```

❌ **Mistake 3:** Context mein har render par naya object value bhejna
✅ **Correct:** Value ko `useMemo` se stable rakho, ya frequently badalne wali state ke liye Zustand/Jotai lo

```jsx
// Wrong
function CartProvider({ children }) {
  const [items, setItems] = useState([]);
  return <CartContext.Provider value={{ items, setItems }}>{children}</CartContext.Provider>; // ❌ naya object har render par
}

// Right
function CartProviderFixed({ children }) {
  const [items, setItems] = useState([]);
  const value = useMemo(() => ({ items, setItems }), [items]); // ✅ items badle tabhi naya value
  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}
```

---

## 🧠 Tricky Interview Question

```javascript
// ESM file (.mjs) — derived value ko state mein rakhne ka bug
import { create } from 'zustand';                                 // store library
const useCart = create((set) => ({
  items: [],                                                      // cart items
  total: 0,                                                       // derived value state mein (galti)
  addItem: (item) => set((s) => ({ items: [...s.items, item] })), // total update karna bhool gaye
}));
useCart.getState().addItem({ price: 100 });                       // item 1
useCart.getState().addItem({ price: 200 });                       // item 2
const s = useCart.getState();                                     // latest state
const derived = s.items.reduce((sum, i) => sum + i.price, 0);     // items se asli total
console.log(`items: ${s.items.length} total: ${s.total} derived: ${derived}`); // kya print hoga?
```

**Answer:** Output is `items: 2 total: 0 derived: 300`. Reasoning: `total` ko state mein rakha gaya, lekin `addItem` sirf `items` update karta hai, `total` nahi. Dono state ek-doosre se alag ho gaye (state drift). `items` sahi hai, `total` stale hai. Fix: `total` store mein mat rakho; use selector se compute karo, jaise `useCart((s) => s.items.reduce((sum, i) => sum + i.price, 0))`, ya `total` ko `addItem` ke andar hi update karo. Derived values ko store karne ka rule: "single source of truth" rakho, aur baaki sab derive karo.

---

## ⚫ Interview Questions + Answers

**Q1: Sabse pehle state manager chunne se pehle kya karna chahiye?**
A1: State ka type classify karna: local UI, form, URL, server data, ya shared client state. Tool choice type par depend karta hai, library ke naam par nahi.

**Q2: Server data aur client state ko alag kyon rakhna chahiye?**
A2: Server data bahar se aata hai, purana ho sakta hai, cache, refetch aur error handling chahiye. Client state app ke andar ka hai. RTK Query ya TanStack Query server data ke liye, aur Zustand/Jotai/Redux client state ke liye.

**Q3: URL mein state kab rakhna chahiye?**
A3: Jo state share, bookmark ya back-button se wapas chahiye (filters, tabs, page number, search text), use URL search params mein rakho. Yeh link ko reproducible banata hai.

**Q4: Context kab use karein, aur kab nahi?**
A4: Context theme, locale, current user jaisi kam badalne wali values ke liye achha hai. Bar-bar badalne wali state ke liye Context se har consumer re-render hota hai, isliye Zustand/Jotai ya selectors wali library behtar hai.

**Q5: Ek interview answer mein tradeoffs kaise bataoge?**
A5: "Pehle state type, phir sabse chhota tool. Chhote app mein Zustand, bade team mein Redux Toolkit, server data mein RTK Query. Har choice ka tradeoff: boilerplate vs structure, bundle size vs tooling, aur learning curve vs control."

---

## 🔷 When to Use + When Not to Use

✅ **Use local `useState` when:** state ek component ka hai (modal open, input focus, toggle).
✅ **Use URL state when:** filters, tabs, pagination share ya bookmark karne hain.
✅ **Use RTK Query / TanStack Query when:** server data cache, refetch, dedupe chahiye.
✅ **Use Zustand / Jotai when:** kai components ko shared client state chahiye, aur Redux overkill hai.
✅ **Use Redux Toolkit when:** bada team, strict conventions, DevTools aur audit trail chahiye.

❌ **Avoid global state when:** sirf ek component ya form ko state chahiye.
❌ **Avoid manual server cache when:** RTK Query/TanStack Query se wahi kaam ek line mein ho jaata hai.
❌ **Avoid Context for fast-changing values:** har consumer re-render hota hai.

---

## 📊 Visual Diagram

```
                     Kya state kahan se aata hai?
                                │
     ┌──────────────┬───────────┼──────────────┬──────────────┐
     ▼              ▼           ▼              ▼              ▼
  SERVER         URL        FORM         SHARED CLIENT     LOCAL UI
  (API data)  (filters,    (inputs)     (cart, address,   (modal open,
     │         tabs)          │          theme)            toggle)
     ▼              ▼           ▼              ▼              ▼
 RTK Query     search      react-hook-   Zustand / Jotai   useState /
 TanStack      params      form /        (chhota)          useReducer
 Query                     useState      Redux Toolkit
                                         (bada, strict)

  Rule: derived values ko store mat karo — select ya compute karo.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Local state | Ek component tak seemit state | एक component तक सीमित state |
| Shared client state | Kai components ka client-side state | कई components का client-side state |
| Server state | API se aaya data, cache ke saath | API से आया data, cache के साथ |
| URL state | Search params mein rakha state | Search params में रखा state |
| Form state | Form inputs ka state | Form inputs का state |
| State drift | Duplicate state ka ek-doosre se alag hona | Duplicate state का अलग हो जाना |
| Derived state | Doosre state se compute hone wali value | दूसरे state से compute होने वाली value |
| Dedupe | Same request ko ek baar bhejna | एक ही request को एक बार भेजना |

---

## ⚡ 3-Line Summary
**English:**
1. पहले state का type पहचानो (local, URL, form, server, shared), फिर सबसे छोटा tool चुनो।
2. Server data RTK Query/TanStack Query में, URL state URL में, और shared UI state Zustand/Jotai या Redux में रखो।
3. Derived values कभी store मत करो; select या compute करो, ताकि state drift न हो।

**Hindi:**
1. पहले state का type पहचानो (local, URL, form, server, shared), फिर सबसे छोटा tool चुनो।
2. Server data RTK Query/TanStack Query में, URL state URL में, और shared UI state Zustand/Jotai या Redux में रखो।
3. Derived values कभी store मत करो; select या compute करो, ताकि state drift न हो।

---

## ➡️ Next Topic
**106. Server Components and Data Fetching (Next.js)** — App Router में server पर data fetch करने के तरीके, caching और client state के साथ उसका संबंध, जिससे यह section production में जुड़ता है।
