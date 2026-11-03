# 116. RTK Query vs React Query
# हिंदी में: RTK Query बनाम React Query — कब कौन-सी Library चुनें

---

## 🔵 Simple Definition (English)
Both are server-state libraries that fetch, cache and update API data. **RTK Query** is part of Redux Toolkit and stores its cache inside the Redux store, while **TanStack Query (React Query)** is a standalone library with its own cache and no Redux needed.

## 🔵 सरल परिभाषा (Hindi)
दोनों server-state libraries हैं जो API data को fetch, cache और update करती हैं। **RTK Query** Redux Toolkit का हिस्सा है और अपना cache Redux store के अंदर रखती है, जबकि **TanStack Query (React Query)** एक स्वतंत्र library है जिसका अपना cache है और Redux की ज़रूरत नहीं।

---

## 🔴 Problem it Solves

Writing `useEffect + fetch + useState` for every API call leads to duplicated code, no caching, and stale data. Teams also ask: "We already use Redux, do we need a second library?" Choosing wrongly gives either two overlapping state systems or a lot of hand-written thunks. This topic helps you pick the right tool and explain the trade-offs in an interview.

```jsx
// PROBLEM: hand-written fetching in every component
useEffect(() => {
  let ignore = false;                              // manual race-condition guard
  fetch('/api/orders').then(r => r.json()).then(d => { if (!ignore) setOrders(d); });
  return () => { ignore = true; };                 // no cache, no dedupe, no retry
}, []);

// SOLUTION (either library): one hook, cache + dedupe + refetch built in
const { data, isLoading } = useGetOrdersQuery();                  // RTK Query
const { data: d2, isPending } = useQuery({ queryKey: ['orders'], queryFn: getOrders }); // React Query
```

## 🔴 यह क्यों बना? (Hindi)
हर API call के लिए `useEffect + fetch + useState` लिखने से code दोहराता है, cache नहीं मिलता और data पुराना रह जाता है। Teams पूछती हैं: "हम पहले से Redux इस्तेमाल करते हैं, क्या दूसरी library चाहिए?" गलत चुनाव से या तो दो overlapping state systems बनते हैं या बहुत सारे हाथ से लिखे thunks। यह topic सही tool चुनना और interview में trade-offs समझाना सिखाता है।

---

## 🟢 How it Works — Step by Step

```
RTK Query:
Step 1 → createApi({ baseQuery, endpoints }) defines ALL endpoints in one place
Step 2 → It auto-generates hooks: useGetOrdersQuery, useAddOrderMutation
Step 3 → Add api.reducer and api.middleware to configureStore (cache lives in Redux)
Step 4 → Tags (providesTags / invalidatesTags) decide which cached data to refetch

React Query:
Step 1 → Wrap the app in QueryClientProvider (cache lives in QueryClient)
Step 2 → In any component, call useQuery({ queryKey, queryFn }) with your own fetch function
Step 3 → useMutation + queryClient.invalidateQueries({ queryKey }) refreshes data after writes
Step 4 → Query keys (arrays) identify and invalidate cached data

SAME IDEA: cache by key, dedupe requests, refetch when stale, show loading/error states
```

## 🟢 कैसे काम करता है? (Hindi)
```
RTK Query:
Step 1 → createApi({ baseQuery, endpoints }) में सारे endpoints एक जगह define होते हैं
Step 2 → यह hooks अपने आप बनाता है: useGetOrdersQuery, useAddOrderMutation
Step 3 → configureStore में api.reducer और api.middleware जोड़ो (cache Redux में रहता है)
Step 4 → Tags (providesTags / invalidatesTags) तय करते हैं कौन-सा cached data दोबारा आएगा

React Query:
Step 1 → App को QueryClientProvider में wrap करो (cache QueryClient में रहता है)
Step 2 → किसी भी component में अपने fetch function के साथ useQuery({ queryKey, queryFn }) बुलाओ
Step 3 → useMutation + queryClient.invalidateQueries({ queryKey }) से write के बाद data refresh होता है
Step 4 → Query keys (arrays) cached data की पहचान और invalidate करने का काम करती हैं

एक जैसा idea: key से cache, requests का dedupe, stale होने पर refetch, loading/error states
```

---

## 🟡 Real World Example
**Flipkart-style app:** The team already has Redux for the cart, user session and feature flags. For product lists and order history they pick **RTK Query**, so the whole app uses one store, one DevTools and one mental model, and tags refresh the order list after "Place order". Another team building a new Zomato-style dashboard with no Redux picks **React Query**: it needs only server state, so a global store would be extra weight, and they enjoy features like `useInfiniteQuery`, `placeholderData`, and `useSuspenseQuery`.

## 🟡 Real Example Hindi mein
**Flipkart जैसा app:** Team के पास cart, user session और feature flags के लिए पहले से Redux है। Product lists और order history के लिए वे **RTK Query** चुनते हैं, इसलिए पूरे app में एक store, एक DevTools और एक सोच रहती है, और "Place order" के बाद tags order list refresh कर देते हैं। Zomato जैसे नए dashboard की दूसरी team जिसमें Redux नहीं है, **React Query** चुनती है: उसे सिर्फ server state चाहिए, global store अतिरिक्त बोझ होता, और `useInfiniteQuery`, `placeholderData`, `useSuspenseQuery` जैसे features मिलते हैं।

---

## 💻 Code Example — Basic

```jsx
// Basic: the SAME feature (list orders + add an order) with both libraries

// ---------- A) RTK Query ----------
import { configureStore } from '@reduxjs/toolkit';                       // Redux Toolkit store
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'; // React flavour of RTK Query
import { Provider } from 'react-redux';                                  // makes the store available

export const api = createApi({
  reducerPath: 'api',                                    // key in the Redux state: state.api
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),        // tiny wrapper around fetch
  tagTypes: ['Order'],                                   // cache tags used for invalidation
  endpoints: build => ({
    getOrders: build.query({                             // READ endpoint
      query: () => '/orders',                            // GET /api/orders
      providesTags: ['Order'],                           // this data is tagged "Order"
    }),
    addOrder: build.mutation({                           // WRITE endpoint
      query: body => ({ url: '/orders', method: 'POST', body }), // POST with JSON body
      invalidatesTags: ['Order'],                        // refetch everything tagged "Order"
    }),
  }),
});
export const { useGetOrdersQuery, useAddOrderMutation } = api; // auto-generated hooks

export const store = configureStore({
  reducer: { [api.reducerPath]: api.reducer },           // cache stored in Redux
  middleware: gDM => gDM().concat(api.middleware),       // handles caching + invalidation
});

function OrdersRTK() {
  const { data = [], isLoading } = useGetOrdersQuery();  // fetch + cache + subscribe
  const [addOrder, { isLoading: saving }] = useAddOrderMutation(); // mutation trigger
  if (isLoading) return <p>Loading...</p>;               // first load
  return (
    <div>
      <ul>{data.map(o => <li key={o.id}>{o.item}</li>)}</ul>
      <button disabled={saving} onClick={() => addOrder({ item: 'Biryani' })}>Add</button>
    </div>
  );
}
// Mount: <Provider store={store}><OrdersRTK /></Provider>

// ---------- B) TanStack Query ----------
import { QueryClient, QueryClientProvider, useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const queryClient = new QueryClient();                    // cache lives here, not in Redux

function OrdersRQ() {
  const qc = useQueryClient();                            // access the cache
  const { data = [], isPending } = useQuery({
    queryKey: ['orders'],                                 // identifies this cache entry
    queryFn: () => fetch('/api/orders').then(r => r.json()), // YOU write the fetcher
  });
  const add = useMutation({
    mutationFn: body => fetch('/api/orders', {            // YOU write the mutation
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
    }).then(r => r.json()),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['orders'] }), // refetch the list
  });
  if (isPending) return <p>Loading...</p>;                // v5 name: isPending (was isLoading in v4)
  return (
    <div>
      <ul>{data.map(o => <li key={o.id}>{o.item}</li>)}</ul>
      <button disabled={add.isPending} onClick={() => add.mutate({ item: 'Biryani' })}>Add</button>
    </div>
  );
}
// Mount: <QueryClientProvider client={queryClient}><OrdersRQ /></QueryClientProvider>
```

## 💻 Code Example — Advanced

```jsx
// Advanced: optimistic update in both libraries + using cached data from Redux selectors

// ---------- RTK Query: optimistic update with onQueryStarted ----------
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const todosApi = createApi({
  reducerPath: 'todosApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  tagTypes: ['Todo'],
  endpoints: build => ({
    getTodos: build.query({ query: () => '/todos', providesTags: ['Todo'] }),
    toggleTodo: build.mutation({
      query: ({ id, done }) => ({ url: `/todos/${id}`, method: 'PATCH', body: { done } }),
      async onQueryStarted({ id, done }, { dispatch, queryFulfilled }) {
        // 1) patch the cached list immediately (optimistic)
        const patch = dispatch(
          todosApi.util.updateQueryData('getTodos', undefined, draft => { // immer draft: mutate directly
            const t = draft.find(x => x.id === id);                       // find the todo
            if (t) t.done = done;                                         // flip it in the cache
          })
        );
        try {
          await queryFulfilled;                                           // wait for the server
        } catch {
          patch.undo();                                                   // 2) rollback on failure
        }
      },
      invalidatesTags: ['Todo'],                                          // 3) sync with server at the end
    }),
  }),
});

// ---------- React Query: optimistic update with onMutate ----------
import { useMutation, useQueryClient } from '@tanstack/react-query';

export function useToggleTodo() {
  const qc = useQueryClient();                                            // cache access
  return useMutation({
    mutationFn: ({ id, done }) =>
      fetch(`/api/todos/${id}`, {
        method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ done }),
      }).then(r => { if (!r.ok) throw new Error('Failed'); return r.json(); }),
    onMutate: async ({ id, done }) => {
      await qc.cancelQueries({ queryKey: ['todos'] });                    // stop in-flight refetches
      const previous = qc.getQueryData(['todos']);                        // snapshot for rollback
      qc.setQueryData(['todos'], old => old.map(t => (t.id === id ? { ...t, done } : t))); // optimistic
      return { previous };                                                // passed to onError
    },
    onError: (_err, _vars, ctx) => qc.setQueryData(['todos'], ctx.previous), // rollback
    onSettled: () => qc.invalidateQueries({ queryKey: ['todos'] }),       // always resync
  });
}
```

---

## 🟠 Next.js Connection

Both work in the App Router, but only in Client Components (`'use client'`). In Next.js you often fetch in Server Components directly with `fetch` and only use these libraries for interactive client data (filters, polling, mutations). For SSR hydration: React Query has `HydrationBoundary` + `dehydrate`; RTK Query needs a per-request store (`makeStore`) and can prefetch with `dispatch(api.endpoints.getOrders.initiate())` plus `next-redux-wrapper`-style hydration (version-dependent; check current docs).

```jsx
// app/providers.jsx ('use client'): per-request store, safe for the App Router
'use client';
import { useRef } from 'react';                              // keep the store between renders
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { api } from '@/lib/api';                             // the createApi() from above

const makeStore = () => configureStore({                     // factory: a NEW store per request on the server
  reducer: { [api.reducerPath]: api.reducer },
  middleware: gDM => gDM().concat(api.middleware),
});

export default function Providers({ children }) {
  const storeRef = useRef(null);                             // created once per component instance
  if (!storeRef.current) storeRef.current = makeStore();     // avoids sharing state between users
  return <Provider store={storeRef.current}>{children}</Provider>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using both libraries for the same data (or copying server data into Redux slices)
✅ **Correct:** Pick one for server state; keep client state (modals, theme) in Redux/Zustand/useState

```jsx
// Wrong: duplicated source of truth
const { data } = useQuery({ queryKey: ['user'], queryFn: getUser });
useEffect(() => { dispatch(setUser(data)); }, [data]);   // ❌ copy into Redux, now they can disagree

// Right: read from the query cache directly
const { data: user } = useQuery({ queryKey: ['user'], queryFn: getUser }); // ✅ single source
```

❌ **Mistake 2:** Forgetting `api.middleware` in RTK Query (caching and invalidation silently break)
✅ **Correct:** Always add both `api.reducer` and `api.middleware`

```jsx
// Wrong
configureStore({ reducer: { [api.reducerPath]: api.reducer } });                        // ❌ no middleware
// Right
configureStore({ reducer: { [api.reducerPath]: api.reducer }, middleware: g => g().concat(api.middleware) });
```

❌ **Mistake 3:** Unstable query keys in React Query (new object identity or missing variables)
✅ **Correct:** Include every variable that changes the result in the key

```jsx
// Wrong: filter is not in the key → stale data for every filter
useQuery({ queryKey: ['orders'], queryFn: () => getOrders(filter) });
// Right: the key changes when the filter changes
useQuery({ queryKey: ['orders', { filter }], queryFn: () => getOrders(filter) });
```

---

## 🧠 Tricky Interview Question

```jsx
// RTK Query endpoint
getOrders: build.query({ query: () => '/orders', providesTags: ['Order'] }),
addOrder:  build.mutation({ query: b => ({ url: '/orders', method: 'POST', body: b }) }), // no invalidatesTags

// In a component
const { data } = useGetOrdersQuery();
const [addOrder] = useAddOrderMutation();
await addOrder({ item: 'Pizza' });   // succeeds with 201
// Does the list on screen update?
```
**Answer:** No. The mutation succeeds, but RTK Query does not know which cached data it affects because there is no `invalidatesTags: ['Order']`. The list stays stale until a refetch trigger (focus, reconnect, `refetchOnMountOrArgChange`, or manual `refetch`) happens. In React Query the same mistake is forgetting `queryClient.invalidateQueries({ queryKey: ['orders'] })` in `onSuccess`. Neither library guesses relationships between your reads and writes: you declare them (tags in RTK Query, query keys in React Query).

---

## ⚫ Interview Questions + Answers

Q1: What is the main architectural difference between RTK Query and React Query?
A1: RTK Query is built on Redux Toolkit: its cache is a slice in the Redux store, its endpoints are declared centrally with `createApi`, and invalidation is tag-based. React Query has its own `QueryClient` cache, you write hooks with your own `queryFn`, and invalidation is by query key. React Query needs no Redux.

Q2: When would you choose RTK Query?
A2: When the project already uses Redux Toolkit, wants centralized API definitions, auto-generated typed hooks, one DevTools, and the ability to read cached API data in selectors or other slices. It is also good for codegen from OpenAPI/GraphQL schemas.

Q3: When would you choose React Query?
A3: When there is no Redux (or you are moving away), you want the most flexible and feature-rich server-state tool: infinite queries, `useSuspenseQuery`, `placeholderData`, per-query `staleTime`/`gcTime`, offline/persist plugins, framework-agnostic adapters (Vue, Solid, Svelte), and a larger community.

Q4: How do they differ in cache invalidation?
A4: RTK Query uses tags: queries `providesTags`, mutations `invalidatesTags`, and matching queries refetch. React Query uses `invalidateQueries({ queryKey })`, which matches by key prefix and marks queries stale, refetching the active ones.

Q5: Do they replace Redux completely?
A5: No. They manage server state (data owned by the backend). Client state such as UI toggles, wizard steps or theme still needs `useState`, context, Redux or Zustand. Using them removes most of the loading/error/data boilerplate from Redux.

---

## 🔷 When to Use + When Not to Use
✅ **Use RTK Query when:**
- The app already uses Redux Toolkit
- You want centralized endpoints, codegen, and cache data visible in the Redux store

✅ **Use React Query when:**
- You have no Redux, or want maximum features and flexibility
- You need infinite queries, Suspense, offline persistence or non-React frameworks

❌ **Avoid both when:**
- The data is fetched once on the server and never changes on the client (use Server Components with `fetch`)
- You only need one tiny request (a plain `fetch` in an effect or a Server Component is enough)

---

## 📊 Visual Diagram

```
        RTK Query                              React Query
 ┌──────────────────────┐             ┌──────────────────────────┐
 │ createApi(endpoints) │             │ useQuery({queryKey,fn})  │
 └─────────┬────────────┘             └────────────┬─────────────┘
           ▼                                       ▼
 ┌──────────────────────┐             ┌──────────────────────────┐
 │ Redux store          │             │ QueryClient (own cache)  │
 │  state.api.queries   │             │  Map<queryKey, data>     │
 └─────────┬────────────┘             └────────────┬─────────────┘
           │ invalidatesTags                       │ invalidateQueries(key)
           ▼                                       ▼
   refetch tagged queries                 refetch matching queries

 Re-render: components re-render only when THEIR subscribed data changes.
 Performance: both dedupe identical requests; RTK adds Redux dispatch overhead (small).
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Server state | Data owned by the backend, cached on client | Backend का data जो client पर cache होता है |
| createApi | RTK Query function to define endpoints | Endpoints define करने वाला RTK function |
| Tag | Label used to invalidate cached data in RTK Query | Cache invalidate करने वाला label |
| Query key | Array that identifies cached data in React Query | Cache की पहचान करने वाला array |
| Invalidation | Marking cache stale so it refetches | Cache को stale बनाकर refetch कराना |
| staleTime | How long data counts as fresh | Data कब तक fresh माना जाए |
| Optimistic update | Update UI before server confirms | Server के confirm से पहले UI बदलना |
| Middleware | Redux layer that handles RTK Query caching | RTK Query की caching संभालने वाली Redux layer |

---

## ⚡ 3-Line Summary
**English:**
1. RTK Query lives inside Redux (tag-based, centralized endpoints); React Query is standalone (key-based, flexible).
2. Both give caching, dedupe, loading/error states and mutations, so pick based on your existing stack.
3. Use one library for server state and keep client state elsewhere.

**Hindi:**
1. RTK Query Redux के अंदर रहती है (tag-based, centralized endpoints); React Query स्वतंत्र है (key-based, flexible)।
2. दोनों caching, dedupe, loading/error states और mutations देती हैं, इसलिए अपने मौजूदा stack के हिसाब से चुनो।
3. Server state के लिए एक ही library इस्तेमाल करो और client state दूसरी जगह रखो।

---

## ➡️ Next Topic
**117. SWR Library** — Vercel की हल्की data fetching library, जिसका नाम "stale-while-revalidate" strategy से आया है, और जो React Query का एक सरल विकल्प है।
