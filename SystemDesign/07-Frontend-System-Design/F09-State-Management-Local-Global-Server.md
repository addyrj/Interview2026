# F09. State Management (Local vs Global vs Server State)
# हिंदी में: State Management — ऐप का डेटा (कौन-सा tab खुला, cart में क्या है, API से आया डेटा) कहाँ रखें और कैसे बदलें, ताकि UI सही दिखे और बेवजह re-render न हो

---

## 🔵 Simple Definition (English)
**State** is any data that can change over time and affects what the UI shows. **State management** is deciding **where each piece of state lives, who owns it, and how changes flow** to the components that need it.
The main categories:
- **Local (component) state**: `useState`/`useReducer` inside one component (input text, modal open, hover).
- **Shared/global client state**: needed across distant components (theme, logged-in user, cart, feature flags). Use Context, **Zustand**, **Redux Toolkit**, Jotai or MobX.
- **Server state**: data owned by the backend and **cached** on the client (feed, products, orders). Use **React Query/TanStack Query**, SWR, Apollo or RTK Query (F10).
- **URL state**: filters, search query, page, selected tab (shareable, back button works).
- **Form state**: React Hook Form / Formik.
- **Persisted state**: localStorage/IndexedDB on web, MMKV/AsyncStorage on React Native (drafts, preferences).

## 🔵 सरल परिभाषा (Hindi)
State = वो डेटा जो बदलता है और UI पर असर डालता है। State management = तय करना कि हर डेटा कहाँ रहेगा, उसका मालिक कौन, और बदलाव ज़रूरी components तक कैसे पहुँचे।
प्रकार: local (एक component का — input, modal), global (कई जगह — theme, user, cart → Context/Zustand/Redux), server state (backend का डेटा जिसकी client पर cache → React Query), URL state (filters, search), form state, और persisted (localStorage/MMKV)।

---

## 🔴 Problem it Solves
Bad state management causes most frontend bugs and slowness:
- **Prop drilling** through 6 levels of components.
- **Duplicated state** that gets out of sync (cart count in header ≠ cart page).
- Storing **server data in Redux manually**: loading flags, caching, refetching, invalidation and race conditions all hand-written.
- **Unnecessary re-renders**: one Context update re-renders the whole app, causing jank (bad INP).
- **Lost state** on refresh or navigation (filters not in URL, drafts not persisted).

The right tool per category gives **a single source of truth**, minimal re-renders and less code.

## 🔴 यह क्यों बना? (Hindi)
ज़्यादातर frontend bugs ग़लत state से आते हैं: 6 levels तक props भेजना (prop drilling), एक ही डेटा दो जगह और आपस में मेल न खाना (header का cart count ≠ cart page), API डेटा को Redux में हाथ से संभालना (loading, cache, refetch, race), एक Context बदलने पर पूरा ऐप re-render, refresh पर filters/draft खो जाना।
हर तरह के state के लिए सही tool = एक सच्चा स्रोत, कम re-render, कम कोड।

---

## 🟢 How it Works — Step by Step

### Decision tree: where should this state live?

```
Is it data from the server (owned by backend)?
   └─ YES → Server-state cache (React Query / SWR / Apollo / RTK Query)   ← don't copy into Redux
Should it survive refresh / be shareable / work with back button?
   └─ YES → URL (search params / route params)        e.g. ?q=pizza&veg=1&sort=rating
Is it form input with validation?
   └─ YES → Form library (React Hook Form) or local state
Used by one component (or a parent + few children)?
   └─ YES → Local state (useState/useReducer), lift up to nearest common parent if needed
Used across many distant components (theme, auth user, cart UI, toasts)?
   └─ YES → Global client store: Context (rarely-changing values) or Zustand/Redux (frequently changing)
Must persist across app restarts (drafts, onboarding done, preferences)?
   └─ YES → + persistence (localStorage/IndexedDB on web, MMKV on RN), never secrets in localStorage
Derived from other state? (total = sum(cart items))
   └─ Don't store it — compute it (useMemo/selectors)
```

### Tools compared

```
┌──────────────────┬──────────────────────────────────────┬─────────────────────────────────────┐
│ Tool             │ Strengths                            │ Watch out                           │
├──────────────────┼──────────────────────────────────────┼─────────────────────────────────────┤
│ useState/Reducer │ Simple, colocated                    │ Prop drilling if shared widely      │
│ Context          │ Built-in, good for rarely-changing   │ Every consumer re-renders on value  │
│                  │ values (theme, locale, auth user)    │ change → split contexts, memo value │
│ Zustand          │ Tiny, hooks, selectors → only        │ Less structure for very large teams │
│                  │ subscribed slices re-render; no      │                                     │
│                  │ provider; works in RN                │                                     │
│ Redux Toolkit    │ Predictable, devtools, middleware,   │ More boilerplate; don't put server  │
│ (+ RTK Query)    │ large-team conventions, RTK Query    │ cache in slices manually            │
│                  │ for server state                     │                                     │
│ Jotai/Recoil     │ Atomic state, fine-grained updates   │ Many atoms to organize              │
│ MobX             │ Observable, automatic tracking       │ "Magic", class-heavy style          │
│ React Query/SWR  │ Server state: caching, dedupe,       │ Not for pure client UI state        │
│                  │ refetch, pagination, optimistic      │                                     │
│ XState           │ Complex flows as state machines      │ Learning curve                      │
│                  │ (checkout, upload, video call)       │                                     │
└──────────────────┴──────────────────────────────────────┴─────────────────────────────────────┘
```

### Re-render mechanics (why it matters)

```
setState in component C → C and all its children re-render (unless memoized)
Context value changes → ALL consumers re-render (even if they use a field that didn't change)
Zustand/Redux with selectors → component re-renders only if selected slice changed (shallow/===)
Fixes: colocate state (keep it low in the tree), split contexts, memoize provider values,
       selectors, React.memo for heavy children, useCallback for stable handlers passed to memo'd children,
       React Compiler (auto-memoization) where available
```

### Normalization (for complex client data)

```
❌ Nested duplicates:   posts: [{ id: 1, author: { id: 7, name: 'Asha' } }, { id: 2, author: { id: 7, name: 'Asha' } }]
✅ Normalized:          users: { 7: { id: 7, name: 'Asha' } }, posts: { 1: { id: 1, authorId: 7 }, 2: {...} }
Update user 7 once → every post shows the new name. (Apollo cache & RTK createEntityAdapter do this)
```

### State machines for complex flows

```
Checkout: idle → addressSelected → paymentPending → (success | failed → retry) → confirmed
Explicit states prevent impossible combos like { loading: true, error: 'x', success: true }
Use a discriminated union: type State = {status:'idle'} | {status:'loading'} | {status:'error', error} | {status:'success', data}
```

## 🟢 कैसे काम करता है? (Hindi)
1. पहले पूछो — डेटा server का है? तो React Query जैसी server-state cache में, Redux में copy नहीं।
2. Share करने या refresh के बाद भी चाहिए (filters, search)? तो URL में; एक component का है? useState; कई दूर के components का? Zustand/Redux; कम बदलने वाला (theme, भाषा)? Context।
3. Context बदलने पर उसके सारे consumers re-render होते हैं — इसलिए context छोटे-छोटे बाँटो; Zustand/Redux selectors से सिर्फ़ ज़रूरी हिस्सा re-render।
4. जो गिना जा सकता है (cart total) उसे store मत करो, compute करो; एक ही डेटा दो जगह मत रखो; nested डेटा को id से normalize करो।
5. Checkout/upload जैसे जटिल flows को state machine या discriminated union से लिखो ताकि "loading भी और error भी" जैसी असंभव स्थिति न बने।

---

## 🟡 Real World Example

**Redux origins at Facebook-scale apps** — Flux and Redux arose when shared mutable state across many components (notification counts, chat) caused inconsistent UIs. Many large apps later moved server data out of Redux into React Query, Apollo or RTK Query and cut a lot of boilerplate.

**Zustand in React Native apps** — popular in Expo/RN apps for cart, auth and session UI state because it's tiny, needs no provider, and has built-in `persist` middleware with MMKV or AsyncStorage.

**URL state in e-commerce (Flipkart, Amazon)** — search filters, sort and pagination live in the URL (`?q=shoes&brand=nike&sort=price_asc`), so results are shareable, bookmarkable and SEO-friendly, and the back button works.

**XState in complex flows** — used for checkout, media upload and video-call state where many transitions and edge cases exist.

## 🟡 Real Example Hindi में
Facebook जैसे बड़े ऐप में कई components में फैले state से UI बेमेल होता था (notification count), इसलिए Flux/Redux आया; बाद में कई टीमों ने API डेटा Redux से निकालकर React Query/Apollo में डाला और बहुत कोड घटा।
Flipkart/Amazon पर search filters URL में रहते हैं (`?q=shoes&brand=nike`) — share, bookmark, SEO और back बटन सब काम करते हैं। React Native ऐप्स में cart/auth के लिए Zustand + MMKV लोकप्रिय।

---

## 🟠 My Stack Example

### Local + lifted state
```tsx
function QuantityStepper({ value, onChange }: { value: number; onChange: (n: number) => void }) {
  return (<div role="group" aria-label="Quantity">
    <button onClick={() => onChange(Math.max(0, value - 1))} aria-label="Decrease">−</button>
    <span aria-live="polite">{value}</span>
    <button onClick={() => onChange(value + 1)} aria-label="Increase">+</button>
  </div>);
}
```

### Global client state with Zustand (+ persistence) — works in Next.js and React Native
```ts
// store/cart.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

type CartItem = { itemId: string; name: string; price: number; qty: number };
type CartState = {
  restaurantId: string | null; items: Record<string, CartItem>;
  add: (restaurantId: string, item: Omit<CartItem, 'qty'>) => void;
  setQty: (itemId: string, qty: number) => void; clear: () => void;
};

export const useCart = create<CartState>()(persist((set, get) => ({
  restaurantId: null, items: {},
  add: (rid, item) => set((s) => {
    const items = s.restaurantId && s.restaurantId !== rid ? {} : { ...s.items };   // one restaurant per cart
    const qty = (items[item.itemId]?.qty ?? 0) + 1;
    return { restaurantId: rid, items: { ...items, [item.itemId]: { ...item, qty } } };
  }),
  setQty: (id, qty) => set((s) => {
    const items = { ...s.items };
    if (qty <= 0) delete items[id]; else items[id] = { ...items[id], qty };
    return { items };
  }),
  clear: () => set({ restaurantId: null, items: {} }),
}), { name: 'cart', storage: createJSONStorage(() => localStorage) }));   // RN: MMKV adapter

// Derived via selectors (not stored) → components re-render only when their slice changes
export const useCartCount = () => useCart((s) => Object.values(s.items).reduce((n, i) => n + i.qty, 0));
export const useCartTotal = () => useCart((s) => Object.values(s.items).reduce((t, i) => t + i.qty * i.price, 0));
```
```tsx
function HeaderCartBadge() { const count = useCartCount(); return <span aria-label={`${count} items in cart`}>{count}</span>; }
```

### Server state with React Query (don't put it in Zustand/Redux)
```tsx
const { data: menu, isPending, error } = useQuery({
  queryKey: ['menu', restaurantId], queryFn: () => api.getMenu(restaurantId), staleTime: 60_000,
});
```

### URL state for filters (Next.js App Router)
```tsx
'use client';
import { useRouter, useSearchParams, usePathname } from 'next/navigation';
export function VegToggle() {
  const params = useSearchParams(); const router = useRouter(); const pathname = usePathname();
  const veg = params.get('veg') === '1';
  const toggle = () => { const p = new URLSearchParams(params); veg ? p.delete('veg') : p.set('veg', '1'); router.replace(`${pathname}?${p}`); };
  return <button aria-pressed={veg} onClick={toggle}>Pure Veg</button>;
}
// Server Component page reads searchParams → fetches filtered data → SEO + shareable
```

### Context only for rarely-changing values (split + memoized)
```tsx
const ThemeContext = createContext<'light' | 'dark'>('light');
const AuthContext = createContext<{ user: User | null } | null>(null);
export function Providers({ children, user }: { children: React.ReactNode; user: User | null }) {
  const auth = useMemo(() => ({ user }), [user]);                // stable value → fewer re-renders
  return <AuthContext.Provider value={auth}><ThemeContext.Provider value="light">{children}</ThemeContext.Provider></AuthContext.Provider>;
}
```

### Explicit state for a complex flow (discriminated union)
```ts
type PaymentState =
  | { status: 'idle' } | { status: 'creatingOrder' }
  | { status: 'awaitingUpi'; orderId: string } | { status: 'failed'; reason: string; retryable: boolean }
  | { status: 'success'; paymentId: string };
type PaymentEvent = { type: 'PAY' } | { type: 'ORDER_CREATED'; orderId: string } | { type: 'UPI_SUCCESS'; paymentId: string } | { type: 'FAIL'; reason: string } | { type: 'RETRY' };
function reducer(s: PaymentState, e: PaymentEvent): PaymentState {
  switch (s.status) {
    case 'idle':          return e.type === 'PAY' ? { status: 'creatingOrder' } : s;
    case 'creatingOrder': return e.type === 'ORDER_CREATED' ? { status: 'awaitingUpi', orderId: e.orderId }
                               : e.type === 'FAIL' ? { status: 'failed', reason: e.reason, retryable: true } : s;
    case 'awaitingUpi':   return e.type === 'UPI_SUCCESS' ? { status: 'success', paymentId: e.paymentId }
                               : e.type === 'FAIL' ? { status: 'failed', reason: e.reason, retryable: true } : s;
    case 'failed':        return e.type === 'RETRY' && s.retryable ? { status: 'creatingOrder' } : s;
    default:              return s;                          // success is terminal
  }
}
```

### React Native specifics
```
- Zustand + MMKV persist (fast, synchronous) for cart/session flags; tokens → Keychain/Keystore (M15/M16)
- React Query + persistQueryClient (MMKV) → instant screens on cold start, refetch in background
- Navigation params for screen-specific state; avoid huge objects in params (pass ids)
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you decide where state should live?**
A1: Classify it. Server-owned data goes in a server-state cache like React Query, not a global store. Shareable or bookmarkable view state (filters, search, pagination) goes in the URL. Form inputs go in a form library or local state. State used by one component, or a small subtree, stays local and is lifted to the nearest common parent. Truly app-wide client state (auth user, theme, cart UI, toasts) goes in Context (if it rarely changes) or a store like Zustand or Redux (if it changes often). Persist only what must survive restarts, and derive computed values instead of storing them.

**Q2: Why shouldn't you put API data in Redux by default?**
A2: Server data needs caching, deduplication, background refetching, staleness rules, pagination, retries, invalidation after mutations, optimistic updates and race-condition handling. Writing that manually in reducers and thunks is a lot of error-prone boilerplate. Server-state libraries (React Query, SWR, Apollo, RTK Query) solve it declaratively. Redux or Zustand then hold only true client state, which keeps the store small and simple.

**Q3: What are the performance pitfalls of React Context?**
A3: When a provider's value changes (including a new object identity on every render), every component consuming that context re-renders, even if it only uses an unrelated field. A single big context with frequently changing data can re-render the whole app. Mitigate by splitting contexts by concern and update frequency, memoizing provider values, keeping fast-changing state in stores with selector-based subscriptions (Zustand, Redux, `useSyncExternalStore`), and colocating state lower in the tree.

**Q4: How do you avoid inconsistent duplicated state?**
A4: Keep a single source of truth for each piece of data. Derive values (totals, counts, filtered lists) with selectors or `useMemo` instead of storing copies. Normalize entities by ID so an update is reflected everywhere. Read server data from the shared query cache (the same query key) rather than copying it into local state. Synchronize to the URL rather than mirroring it in state. After mutations, invalidate or update the cache instead of patching multiple stores.

**Q5: When would you use a state machine?**
A5: For flows with many states, transitions and edge cases where boolean flags create impossible combinations: checkout and payment, multi-step onboarding, file upload with pause, resume and retry, video calls, and auth flows. Modeling explicit states and allowed transitions (XState or a reducer with a discriminated union) makes behaviour predictable and testable, and makes it easy to render the correct UI for each state.

---

## 🔷 Trade-offs
✅ Local state: simplest, fastest — ❌ prop drilling when shared widely.
✅ Context: built-in — ❌ broad re-renders for frequently changing values.
✅ Zustand: tiny, selector-based — ❌ fewer conventions for huge teams.
✅ Redux Toolkit: structure, devtools, middleware — ❌ more ceremony.
✅ Server-state libs: huge code reduction — ❌ another abstraction; cache keys must be designed well.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Local state | State inside one component | एक component का state |
| Global state | Shared app-wide client state | पूरे ऐप का state |
| Server state | Cached backend data | backend डेटा की cache |
| URL state | State in query/route params | URL में state |
| Prop drilling | Passing props through many levels | कई levels तक props |
| Single source of truth | One owner for each data | हर डेटा का एक मालिक |
| Selector | Function picking a slice of state | state का हिस्सा चुनना |
| Normalization | Entities stored by id | id से डेटा रखना |
| Derived state | Computed from other state | गिना हुआ state |
| State machine | Explicit states & transitions | तय स्थितियाँ और बदलाव |

---

## ⚡ 3-Line Summary
**English:**
1. Classify state: server (React Query), URL (filters), form, local (useState), global client (Context/Zustand/Redux), persisted.
2. Single source of truth: derive instead of duplicating, normalize entities, don't copy server data into stores.
3. Control re-renders: colocate state, split contexts, use selectors; model complex flows as state machines.

**Hindi:**
1. State के प्रकार पहचानो: server (React Query), URL, form, local, global (Context/Zustand/Redux), persisted।
2. एक सच्चा स्रोत: copy नहीं, compute करो; id से normalize; server डेटा store में copy मत करो।
3. Re-render कम: state नीचे रखो, context बाँटो, selectors; जटिल flows के लिए state machine।

---

## ➡️ Next Topic Suggestion
**F10. Data Fetching + Server State (React Query / SWR)** — Server state deserves its own tool. Next: how React Query caches, dedupes, refetches, paginates and does optimistic updates, plus stale-while-revalidate on the client.
