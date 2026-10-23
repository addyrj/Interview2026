# F10. Data Fetching + Server State (React Query / SWR)
# हिंदी में: Data Fetching + Server State — API से डेटा लाना, उसे client पर cache करना, कब पुराना माना जाए, कब दोबारा लाना है, और बदलाव (mutation) के बाद cache को सही रखना — React Query/SWR यह सब अपने-आप करते हैं

---

## 🔵 Simple Definition (English)
**Server state** is data that lives on the server and is only **borrowed** by the client: product lists, feeds, orders, profiles. Unlike UI state, it can be **changed by others**, can become **stale**, and needs **async fetching, caching, deduplication, background refresh, pagination, retries and invalidation**.
**TanStack Query (React Query)**, **SWR**, **Apollo Client** (GraphQL) and **RTK Query** are libraries that manage server state declaratively:
- `useQuery(key, fn)` gives cached data plus `isPending/isError/isFetching` status.
- `useMutation` handles changes, with **cache invalidation** or **optimistic updates**.
They implement **stale-while-revalidate** on the client: show cached data instantly, refetch in the background.

## 🔵 सरल परिभाषा (Hindi)
Server state वो डेटा है जो सर्वर पर रहता है और client सिर्फ़ उसकी कॉपी रखता है (products, feed, orders) — इसे दूसरे भी बदल सकते हैं, यह पुराना हो सकता है।
React Query / SWR / Apollo यह सब अपने-आप संभालते हैं: डेटा लाना, cache, एक जैसी requests को एक करना, पीछे से ताज़ा करना, pagination, retry, और बदलाव के बाद cache ठीक करना (invalidate या optimistic update)। पहले cache दिखाओ, पीछे से ताज़ा लाओ।

---

## 🔴 Problem it Solves
Hand-written `useEffect + fetch + useState` code has many bugs:
- **Race conditions**: you type "piz", then "pizza", and the response for "piz" arrives last and overwrites the results.
- **Duplicate requests**: 5 components need `/me`, so 5 network calls go out.
- **No caching**: going back to a page shows a spinner again.
- **Stale data**: no refetch on focus or reconnect; the order status never updates.
- **Manual loading/error flags** everywhere, memory leaks on unmount, no retries on flaky 4G.
- **After a mutation**, every place showing that data must be updated manually.

Server-state libraries solve all of this with a **shared cache keyed by query keys**.

## 🔴 यह क्यों बना? (Hindi)
हाथ से लिखे `useEffect + fetch` में बहुत bugs: पुराना जवाब बाद में आकर नया overwrite कर दे (race), 5 components के लिए 5 बार वही request, वापस आने पर फिर spinner, order status अपने-आप ताज़ा न होना, हर जगह loading/error flags, धीमे नेटवर्क पर retry नहीं, और बदलाव के बाद हर जगह हाथ से update।
React Query/SWR query key वाली एक साझा cache से ये सब हल करते हैं।

---

## 🟢 How it Works — Step by Step

### The query cache

```
useQuery({ queryKey: ['menu', 42], queryFn })      (Component A)
useQuery({ queryKey: ['menu', 42], queryFn })      (Component B — same key)
            │
            ▼
   ┌──────────────── QueryClient cache ─────────────────┐
   │ ['menu', 42] → { data, status, dataUpdatedAt,      │  ← ONE request (deduped),
   │                  observers: [A, B] }               │    both components subscribe
   │ ['orders', 'active'] → {...}                        │
   └─────────────────────────────────────────────────────┘
Query key = identity of the data. Include every variable the fetch depends on:
  ['products', { category: 'shoes', sort: 'price', page: 2 }]
```

### Freshness lifecycle

```
fetch success → data is FRESH for staleTime (default 0 in React Query!)
      │
      ▼ after staleTime → STALE (still shown) → refetch triggers:
           - new component mounts with that key
           - window refocus (refetchOnWindowFocus)
           - network reconnect (refetchOnReconnect)
           - refetchInterval (polling)
           - manual invalidateQueries()
      │
      ▼ no observers for gcTime (default 5 min) → removed from cache (garbage collected)

UI states: isPending (no data yet) vs isFetching (background refresh with data shown)
→ show skeleton only when isPending; show a subtle indicator when isFetching
```

### Choosing staleTime (interview gold)

```
Restaurant menu / product catalog   staleTime 1–5 min   (changes rarely)
User profile                        staleTime 5 min, invalidate on edit
Feed                                staleTime 30 s, + "new posts" banner via SSE/WS
Order status / live score           staleTime 0 + refetchInterval 5–10 s, or WebSocket push → setQueryData
Static config / feature flags       staleTime Infinity (refresh on app start)
```

### Mutations: invalidate vs optimistic

```
A) Invalidate after success (simple, always correct):
   mutate → server OK → queryClient.invalidateQueries({ queryKey: ['cart'] }) → refetch

B) Optimistic update (instant UI):
   onMutate:  cancel in-flight queries for key → snapshot old data → setQueryData(new guess)
   onError:   rollback to snapshot + toast "Couldn't like post"
   onSettled: invalidate to sync with server truth
   Use for likes, toggles, adding to cart, reordering — low-risk, high-frequency actions
   Avoid for payments/orders where showing success before confirmation is misleading
```

### Pagination & infinite queries

```
useInfiniteQuery({ queryKey: ['feed'], queryFn: ({ pageParam }) => getFeed(pageParam),
                   getNextPageParam: (last) => last.nextCursor })
→ data.pages = [page1, page2, ...]; fetchNextPage() on scroll end (F12)
placeholderData: keepPreviousData → page 2 → 3 without flashing an empty list
```

### Race conditions handled

```
Query key changes ("piz" → "pizza") → the old query is no longer observed;
the component only renders data for the current key; AbortSignal passed to queryFn cancels old fetch
queryFn: ({ signal }) => fetch(url, { signal })
```

### SSR / prefetch / hydration (Next.js)

```
Server: queryClient.prefetchQuery(...) → dehydrate(queryClient) → <HydrationBoundary state={...}>
Client: same keys → data already in cache → no loading flash, then normal SWR behaviour
With RSC: fetch directly in Server Components for initial data; use React Query for client interactivity
(polling, infinite scroll, optimistic mutations)
```

### SWR vs React Query vs Apollo vs RTK Query

```
SWR          → tiny, simple (Vercel); great for read-heavy; fewer mutation helpers
React Query  → most features: infinite, mutations, optimistic, devtools, persistence, RN-ready
Apollo       → GraphQL normalized cache (entities by __typename:id), fragments, subscriptions
RTK Query    → if already on Redux Toolkit; cache tags for invalidation; codegen from OpenAPI
```

## 🟢 कैसे काम करता है? (Hindi)
1. हर डेटा की पहचान query key से (`['menu', 42]`); एक ही key वाले कई components = एक ही request, सब उसी cache से पढ़ते हैं।
2. staleTime तक डेटा ताज़ा (दोबारा नहीं लाता); उसके बाद पुराना (पर दिखता रहता है) और focus, reconnect, नए mount या polling पर पीछे से ताज़ा होता है।
3. staleTime डेटा के हिसाब से चुनो — menu 1–5 मिनट, feed 30 सेकंड, order status 0 + polling या WebSocket।
4. बदलाव के बाद: या तो invalidate (सर्वर से दोबारा) या optimistic (UI पहले बदलो, ग़लती पर rollback) — like/cart के लिए optimistic, payment के लिए नहीं।
5. `useInfiniteQuery` से cursor pagination; key बदलने पर पुरानी request रद्द (AbortSignal) — race नहीं; SSR में prefetch + hydrate से loading flash नहीं।

---

## 🟡 Real World Example

**TanStack Query** — very widely used across React and React Native codebases. Many teams report deleting large amounts of Redux "loading/error/data" boilerplate after adopting it.

**Swiggy/Zomato-style order tracking** — the order status screen uses polling (`refetchInterval`) or WebSocket events that write into the same query cache, so every component showing the order (banner, tracking screen) updates together.

**Facebook (Relay) / GitHub / Shopify (Apollo, GraphQL)** — normalized client caches mean that when you like a post, every view of that post (feed, profile, notifications) updates from one cache entry.

**Vercel dashboard (SWR)** — SWR was built by Vercel and popularized "stale-while-revalidate" UX on the client: instant cached data plus focus revalidation.

## 🟡 Real Example Hindi में
Swiggy/Zomato जैसी order tracking में status polling या WebSocket से उसी query cache में लिखा जाता है — banner और tracking screen दोनों एक साथ बदलते हैं।
Facebook/GitHub की GraphQL normalized cache में like करते ही feed, profile, notifications — हर जगह वही post update। SWR Vercel ने बनाया था।

---

## 🟠 My Stack Example

### QueryClient setup (Next.js / React Native)
```tsx
// shared/queryClient.ts
import { QueryClient } from '@tanstack/react-query';
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: (count, err: any) => err?.status >= 500 && count < 3,   // don't retry 4xx
      retryDelay: (n) => Math.min(1000 * 2 ** n, 8000),              // exponential backoff
      refetchOnWindowFocus: true,
    },
  },
});
// app/providers.tsx: <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
```

### Typed query hooks with cancellation
```ts
// features/menu/hooks.ts
export const menuKeys = { all: ['menu'] as const, byRestaurant: (id: string) => ['menu', id] as const };

export function useMenu(restaurantId: string) {
  return useQuery({
    queryKey: menuKeys.byRestaurant(restaurantId),
    queryFn: ({ signal }) => http.get<Menu>(`/restaurants/${restaurantId}/menu`, { signal }).then((r) => r.data),
    staleTime: 5 * 60_000,
    enabled: !!restaurantId,
  });
}
```

### Optimistic "add to cart" with rollback
```ts
export function useAddToCart() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (item: { itemId: string; qty: number }) =>
      http.post<Cart>('/cart/items', item, { headers: { 'Idempotency-Key': crypto.randomUUID() } }).then((r) => r.data),
    onMutate: async (item) => {
      await qc.cancelQueries({ queryKey: ['cart'] });
      const prev = qc.getQueryData<Cart>(['cart']);
      qc.setQueryData<Cart>(['cart'], (c) => c && { ...c, items: [...c.items, { ...item, pending: true }] });
      return { prev };
    },
    onError: (_e, _item, ctx) => { qc.setQueryData(['cart'], ctx?.prev); toast.error('Could not add item'); },
    onSettled: () => qc.invalidateQueries({ queryKey: ['cart'] }),
  });
}
```

### Live order status: polling that stops when delivered
```ts
export function useOrder(orderId: string) {
  return useQuery({
    queryKey: ['order', orderId],
    queryFn: () => http.get<Order>(`/orders/${orderId}`).then((r) => r.data),
    refetchInterval: (q) => (q.state.data?.status === 'DELIVERED' ? false : 5000),
    refetchIntervalInBackground: false,
  });
}
// Or WebSocket push: socket.on('order.updated', (o) => queryClient.setQueryData(['order', o.id], o));
```

### Next.js: prefetch on server, hydrate on client
```tsx
// app/restaurant/[id]/page.tsx (Server Component)
import { dehydrate, HydrationBoundary, QueryClient } from '@tanstack/react-query';
export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const qc = new QueryClient();
  await qc.prefetchQuery({ queryKey: ['menu', id], queryFn: () => getMenuServer(id) });
  return <HydrationBoundary state={dehydrate(qc)}><MenuClient restaurantId={id} /></HydrationBoundary>;
}
```

### React Native: persist cache for instant cold start + online manager
```ts
import { persistQueryClient } from '@tanstack/react-query-persist-client';
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';
import { onlineManager, focusManager } from '@tanstack/react-query';
import NetInfo from '@react-native-community/netinfo';
import { AppState } from 'react-native';
import { MMKV } from 'react-native-mmkv';

const mmkv = new MMKV();
persistQueryClient({ queryClient, persister: createSyncStoragePersister({
  storage: { getItem: (k) => mmkv.getString(k) ?? null, setItem: (k, v) => mmkv.set(k, v), removeItem: (k) => mmkv.delete(k) },
}), maxAge: 24 * 3600_000 });

onlineManager.setEventListener((setOnline) => NetInfo.addEventListener((s) => setOnline(!!s.isConnected)));  // pause when offline
AppState.addEventListener('change', (s) => focusManager.setFocused(s === 'active'));                        // "window focus" on RN
```

### SWR equivalent (lightweight)
```tsx
const { data, error, isLoading, mutate } = useSWR(`/api/restaurants/${id}`, fetcher, { revalidateOnFocus: true, dedupingInterval: 5000 });
```

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between server state and client state?**
A1: Client (UI) state is owned by the app: modal open, form input, selected tab. It's synchronous and fully controlled. Server state is owned by the backend and the client holds a cached snapshot. It's async, shared, can be changed by other users or processes, and becomes stale. It needs fetching, caching, deduplication, refetching, pagination, invalidation and error handling, which is why dedicated libraries like React Query or SWR handle it rather than Redux or Context.

**Q2: Explain staleTime vs gcTime in React Query.**
A2: `staleTime` is how long fetched data counts as fresh. During that window, new mounts or focus events don't refetch. After it, data is stale: still shown, but refetched in the background on triggers. `gcTime` (formerly cacheTime) is how long an unused query (no subscribed components) stays in memory before being garbage-collected. Tune `staleTime` per data type: high for catalogs, low or polling for live data.

**Q3: How do optimistic updates work and when shouldn't you use them?**
A3: Before the server responds, cancel in-flight fetches for the affected key, snapshot the current cached data and write the expected new state into the cache so the UI updates instantly. On error, roll back to the snapshot and notify the user. On settle, invalidate to resync with the server. Use them for frequent, low-risk, likely-to-succeed actions (likes, toggles, cart quantity, reordering). Avoid them, or show a pending state instead, for high-stakes or likely-to-fail operations like payments, placing orders and irreversible actions.

**Q4: How do you prevent race conditions in data fetching?**
A4: Tie each request to a unique key (all params in the query key) so components render only data for the current key. Pass AbortSignal to cancel outdated requests. With manual code, use an `ignore` flag or AbortController in the effect cleanup and compare request IDs before setting state. Debounce rapid inputs like search. Libraries like React Query handle most of this by default.

**Q5: How do you keep cached data in sync after a mutation?**
A5: Options, in order of simplicity: invalidate the affected queries (`invalidateQueries` by key prefix) to refetch the server truth; directly update the cache with the mutation response (`setQueryData`) to avoid an extra request; use optimistic updates with rollback for instant feedback; or use a normalized cache (Apollo/Relay) where returning the updated entity updates every view. For real-time collaboration, push events (WebSocket/SSE) that update or invalidate the cache.

---

## 🔷 Trade-offs
✅ Huge reduction in boilerplate; caching, dedupe, retries, refetch, pagination built in.
✅ Great UX: instant cached screens, background refresh, optimistic updates.
❌ Must design query keys & staleTime carefully; misuse → over-fetching or stale data.
❌ Another dependency/abstraction; overlapping with RSC data fetching in Next.js (decide who owns what).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Server state | Backend-owned data cached on client | सर्वर का डेटा, client पर कॉपी |
| Query key | Identity of cached data | cache की पहचान |
| staleTime | How long data counts as fresh | कितनी देर ताज़ा |
| gcTime | How long unused data stays cached | बिना इस्तेमाल कितनी देर रहे |
| Deduplication | One request for identical queries | एक जैसी requests एक |
| Invalidation | Mark data stale → refetch | cache को पुराना मानकर दोबारा |
| Optimistic update | UI updated before server response | पहले UI बदलना |
| Rollback | Revert on error | ग़लती पर वापस |
| Infinite query | Paged data appended | पन्ने जुड़ते जाना |
| Hydration (query) | Server-prefetched cache on client | सर्वर cache client में |

---

## ⚡ 3-Line Summary
**English:**
1. Server state is async, shared and goes stale — manage it with React Query/SWR/Apollo, not hand-written effects or Redux.
2. Query keys identify data; staleTime controls freshness; background refetch on focus/reconnect/interval; dedupe + cancellation prevent waste and races.
3. After mutations: invalidate, set cache from response, or optimistic update with rollback; prefetch + hydrate for SSR; persist cache on mobile.

**Hindi:**
1. Server state async, साझा और पुराना होने वाला — React Query/SWR से संभालो, हाथ के useEffect से नहीं।
2. Query key = पहचान; staleTime = ताज़गी; focus/reconnect पर पीछे से ताज़ा; dedupe और cancel से race नहीं।
3. बदलाव के बाद invalidate, setQueryData या optimistic + rollback; SSR में prefetch + hydrate; mobile पर cache persist।

---

## ➡️ Next Topic Suggestion
**F11. API Layer for Frontend (REST vs GraphQL vs BFF)** — What should the API look like from the UI's point of view? Next: designing a clean API layer in the client, and choosing between REST, GraphQL and a Backend-for-Frontend.
