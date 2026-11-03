# 112. useMutation Hook
# हिंदी में: useMutation Hook — Server पर Data भेजना और Cache Update करना

---

## 🔵 Simple Definition (English)
**`useMutation`** is the TanStack Query v5 hook for **changing** server data (POST, PUT, PATCH, DELETE). Unlike `useQuery`, it does not run automatically: you call `mutate(variables)` yourself. It tracks `isPending`, `isError`, `isSuccess` and lets you run side effects like invalidating the cache.

## 🔵 सरल परिभाषा (Hindi)
**`useMutation`** TanStack Query v5 का hook है जो server का data **बदलने** (POST, PUT, PATCH, DELETE) के लिए है। `useQuery` की तरह यह अपने आप नहीं चलता: आप खुद `mutate(variables)` call करते हो। यह `isPending`, `isError`, `isSuccess` track करता है और cache invalidate करने जैसे side effects देता है।

---

## 🔴 Problem it Solves

After you write data (add to cart, place an order), the screen shows old data because the cached list is stale. Manual code needs `loading` / `error` flags per button, double-click protection, and a manual refetch of related lists. It is easy to forget one list, and the UI shows wrong data.

```jsx
// PROBLEM: manual write flow
const [saving, setSaving] = useState(false);
async function add() {
  setSaving(true);
  try {
    await fetch('/api/cart', { method: 'POST', body: JSON.stringify(item) });
    await refetchCart();                // easy to forget; other lists stay stale
  } finally { setSaving(false); }
}

// SOLUTION: useMutation + invalidateQueries
const add = useMutation({ mutationFn: addToCart, onSuccess: () => qc.invalidateQueries({ queryKey: ['cart'] }) });
```

## 🔴 यह क्यों बना? (Hindi)
Data लिखने (cart में add, order place) के बाद screen पर पुराना data दिखता है क्योंकि cached list stale है। Manual code में हर button के लिए `loading` / `error` flags, double-click से बचाव और related lists का manual refetch चाहिए। कोई list भूल गए तो UI गलत data दिखाता है। `useMutation` और `invalidateQueries` से यह साफ़ तरीके से होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → const m = useMutation({ mutationFn: (vars) => api(vars), ...callbacks })
Step 2 → User action calls m.mutate(vars) (fire and forget) or await m.mutateAsync(vars)
Step 3 → status 'pending' (m.isPending = true) → disable the button / show spinner
Step 4 → mutationFn runs once (mutations are NOT retried by default)
Step 5 → Success → onSuccess(data, vars) → usually queryClient.invalidateQueries({ queryKey })
Step 6 → Error → onError(error, vars) → show a toast
Step 7 → onSettled runs in both cases (cleanup, close modal)
Step 8 → Invalidated queries that are active refetch automatically → UI shows fresh data

v5 notes: object signature only; isPending replaces isLoading; per-hook callbacks (onSuccess)
          still exist for useMutation (they were removed only from useQuery)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → const m = useMutation({ mutationFn: (vars) => api(vars), ...callbacks })
Step 2 → User action m.mutate(vars) (fire and forget) या await m.mutateAsync(vars) call करता है
Step 3 → status 'pending' (m.isPending = true) → button disable / spinner दिखाओ
Step 4 → mutationFn एक बार चलता है (mutations default में retry नहीं होते)
Step 5 → Success → onSuccess(data, vars) → आम तौर पर queryClient.invalidateQueries({ queryKey })
Step 6 → Error → onError(error, vars) → toast दिखाओ
Step 7 → onSettled दोनों case में चलता है (cleanup, modal बंद)
Step 8 → Active invalidated queries अपने आप refetch होती हैं → UI ताज़ा data दिखाता है

v5 notes: सिर्फ object signature; isLoading की जगह isPending; useMutation में callbacks (onSuccess)
          अब भी हैं (सिर्फ useQuery से हटाए गए)
```

---

## 🟡 Real World Example
**Amazon "Add to Cart":** Clicking the button posts the product to the server. While pending, the button shows "Adding..." and is disabled so double clicks don't add two items. On success, the cart count in the header (query `['cart']`) is invalidated and refetches, so the badge shows the new count. On failure, a toast says "Could not add item".

## 🟡 Real Example Hindi mein
**Amazon "Add to Cart":** Button दबाने पर product server को POST होता है। Pending के दौरान button "Adding..." दिखाता है और disabled रहता है ताकि double click से दो items न जुड़ें। Success पर header के cart count की query `['cart']` invalidate होकर refetch होती है और badge में नया count दिखता है। Fail होने पर toast कहता है "Could not add item"।

---

## 💻 Code Example — Basic

```jsx
// Basic useMutation: add a todo then refresh the list
import { QueryClient, QueryClientProvider, useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';                             // local input state
import { createRoot } from 'react-dom/client';                // root API

const queryClient = new QueryClient();                         // shared cache

// fake in-memory "server" so this runs without a backend
let db = [{ id: 1, title: 'Learn React Query' }];
const api = {
  list: async () => [...db],                                   // GET
  add: async (title) => { db = [...db, { id: Date.now(), title }]; return db.at(-1); }, // POST
};

function Todos() {
  const qc = useQueryClient();                                 // access the client inside components
  const [text, setText] = useState('');                        // controlled input

  const todos = useQuery({ queryKey: ['todos'], queryFn: api.list }); // read

  const addTodo = useMutation({
    mutationFn: api.add,                                       // receives whatever mutate() gets
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['todos'] });           // mark stale + refetch active ones
      setText('');                                             // clear the input
    },
  });

  return (
    <div>
      <input value={text} onChange={(e) => setText(e.target.value)} />
      <button disabled={addTodo.isPending || !text} onClick={() => addTodo.mutate(text)}>
        {addTodo.isPending ? 'Adding...' : 'Add'}              {/* pending feedback */}
      </button>
      {addTodo.isError && <p>{addTodo.error.message}</p>}      {/* error feedback */}
      <ul>{todos.data?.map((t) => <li key={t.id}>{t.title}</li>)}</ul>
    </div>
  );
}

createRoot(document.getElementById('root')).render(
  <QueryClientProvider client={queryClient}><Todos /></QueryClientProvider>
);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: reusable mutation hook, mutateAsync, per-call callbacks, invalidating multiple keys,
// and a global MutationCache error handler
import { QueryClient, QueryClientProvider, MutationCache, useMutation, useQueryClient } from '@tanstack/react-query';

// 1) Global handler: runs for every mutation error (central place for toasts)
export const queryClient = new QueryClient({
  mutationCache: new MutationCache({
    onError: (error) => console.error('Mutation failed:', error.message), // replace with toast.error()
  }),
});

// 2) Reusable domain hook: components do not know about URLs or cache keys
export function useAddToCart() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ productId, qty }) => {                 // single object variable
      const res = await fetch('/api/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productId, qty }),
      });
      if (!res.ok) throw new Error('Could not add item');       // turn HTTP errors into rejections
      return res.json();                                        // new cart summary
    },
    onSuccess: (data) => {
      qc.setQueryData(['cart', 'summary'], data);               // update one cache entry directly (no refetch)
    },
    onSettled: () => {
      // refetch anything that depends on the cart, success or failure → server is source of truth
      return qc.invalidateQueries({ queryKey: ['cart'] });      // returning the promise keeps isPending true until refetch ends
    },
  });
}

// 3) Usage with per-call callbacks and mutateAsync
export function AddButton({ productId }) {
  const add = useAddToCart();

  async function handleClick() {
    try {
      const summary = await add.mutateAsync({ productId, qty: 1 }); // await the result
      console.log('Items in cart:', summary.count);                 // runs only on success
    } catch {
      /* error already handled by the global MutationCache and shown below */
    }
  }

  return (
    <>
      <button onClick={handleClick} disabled={add.isPending}>
        {add.isPending ? 'Adding...' : 'Add to cart'}
      </button>
      {add.isError && <p role="alert">{add.error.message}</p>}
    </>
  );
}

// Alternative: mutate() with callbacks that only fire if the component is still mounted
// add.mutate({ productId, qty: 1 }, { onSuccess: () => toast('Added!') });
```

Re-render behavior: the component re-renders when the mutation state changes (`idle` → `pending` → `success` / `error`). `mutate` has a stable identity, so it is safe in dependency arrays. Performance impact: each `useMutation` call has its own state, so ten buttons do not share `isPending`; use `useMutationState` if you need cross-component status (version-dependent API detail).

---

## 🟠 Next.js Connection

In the App Router, **Server Actions** are the built-in way to mutate data. You can still use `useMutation` with a Server Action as the `mutationFn` when you want TanStack's pending/error state and cache invalidation on the client.

```jsx
// app/cart/actions.js
'use server';                                                   // Server Action module
export async function addToCartAction({ productId, qty }) {     // runs only on the server
  // await db.cart.add(...)  → write to your database here (placeholder)
  return { ok: true, productId, qty };                          // return serializable data
}
```

```jsx
// app/cart/AddToCart.jsx
'use client';                                                   // uses hooks
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { addToCartAction } from './actions';                    // import the server action

export default function AddToCart({ productId }) {
  const qc = useQueryClient();
  const m = useMutation({
    mutationFn: addToCartAction,                                // calls the server function directly
    onSuccess: () => qc.invalidateQueries({ queryKey: ['cart'] }), // refresh client cache
  });
  return (
    <button disabled={m.isPending} onClick={() => m.mutate({ productId, qty: 1 })}>
      {m.isPending ? 'Adding...' : 'Add to cart'}
    </button>
  );
}
// If you do not need client cache, use <form action={serverAction}> + useActionState / revalidatePath instead.
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting to invalidate or update related queries after success
✅ **Correct:** Call `invalidateQueries` (or `setQueryData`) in `onSuccess` / `onSettled`

```jsx
// Wrong: server changed but the list on screen is stale
useMutation({ mutationFn: addTodo });                                   // ❌ nothing refreshes

// Right
useMutation({
  mutationFn: addTodo,
  onSuccess: () => qc.invalidateQueries({ queryKey: ['todos'] }),       // ✅ list refetches
});
```

❌ **Mistake 2:** Using `useQuery` for write operations
✅ **Correct:** Use `useMutation` for POST/PUT/DELETE

```jsx
// Wrong: useQuery refetches on focus/mount → could POST the same order again
useQuery({ queryKey: ['placeOrder'], queryFn: () => postOrder(cart) });  // ❌ dangerous

// Right: the write only happens when the user clicks
const placeOrder = useMutation({ mutationFn: postOrder });               // ✅
<button onClick={() => placeOrder.mutate(cart)}>Place order</button>
```

❌ **Mistake 3:** Passing several arguments to `mutate`
✅ **Correct:** `mutate` accepts ONE variables argument (plus an options object), so pass an object

```jsx
// Wrong: second argument is treated as options, not data
add.mutate(productId, qty);                                              // ❌

// Right
add.mutate({ productId, qty });                                          // ✅ one object
```

---

## 🧠 Tricky Interview Question

```jsx
const m = useMutation({
  mutationFn: (n) => api.save(n),
  onSuccess: () => console.log('hook onSuccess'),
});

function onClick() {
  m.mutate(1, { onSuccess: () => console.log('call onSuccess') });
  m.mutate(2, { onSuccess: () => console.log('call onSuccess') });
}
```
**Answer:** Both `mutationFn` calls run, and the **hook-level** `onSuccess` fires for each (twice). The **per-call** `onSuccess` (second argument of `mutate`) only fires for the **last** `mutate` call, and only if the component is still mounted. When a new `mutate` starts, the observer starts tracking the new mutation, so the first call's per-call callback is dropped. This is why shared logic (cache invalidation) belongs in the hook-level callbacks, and UI-only actions (close a modal) in the per-call ones.

---

## ⚫ Interview Questions + Answers

Q1: How is `useMutation` different from `useQuery`?
A1: `useQuery` reads data and runs automatically (on mount, focus, key change) with caching and retries. `useMutation` writes data, runs only when you call `mutate`, is not cached by key and does not retry by default.

Q2: `mutate` vs `mutateAsync`?
A2: `mutate` returns nothing and swallows errors (use callbacks and state). `mutateAsync` returns a Promise, so you can `await` it, but you must handle rejections with try/catch to avoid unhandled errors.

Q3: How do you refresh the UI after a mutation?
A3: `queryClient.invalidateQueries({ queryKey })` marks queries stale and refetches active ones. Or `queryClient.setQueryData` to write the new value directly without a refetch. For instant feedback see optimistic updates (next topics).

Q4: What are the lifecycle callbacks?
A4: `onMutate` (before the function runs, used for optimistic updates), `onSuccess`, `onError`, `onSettled` (always). They can return Promises; TanStack waits for them.

Q5: Are mutations retried?
A5: No, the default is `retry: 0`, because repeating a write might duplicate it. You can set `retry` explicitly for idempotent endpoints.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- You send POST/PUT/PATCH/DELETE from the client
- You want pending/error state and a central place to invalidate the cache
- You want optimistic updates with rollback

❌ **Avoid when:**
- You are reading data (use `useQuery`)
- A Server Action with a plain `<form action>` is enough (no client cache involved)
- The write is a fire-and-forget analytics ping (a plain `fetch`/`sendBeacon` is simpler)

---

## 📊 Visual Diagram

```
 click ─► mutate(vars)
             │
             ▼
        status: idle ─► pending ─────────────► success ─► onSuccess ─┐
                          │  onMutate (before)                       │
                          │                                          ├─► onSettled
                          └──────────────────► error ─► onError ─────┘
                                                                     │
                       invalidateQueries(['cart']) ◄─────────────────┘
                                │
                                ▼
              active ['cart'] query refetches ─► UI updates
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| useMutation | Hook to change server data | Server data बदलने वाला hook |
| mutationFn | Function that performs the write | Write करने वाला function |
| mutate | Trigger the mutation (no return) | Mutation चलाओ (return नहीं) |
| mutateAsync | Trigger and return a Promise | चलाओ और Promise पाओ |
| invalidateQueries | Mark queries stale and refetch | Queries को stale मार्क कर refetch |
| onSettled | Runs after success or error | Success या error के बाद चलता है |
| MutationCache | Global store for mutations and handlers | Mutations का global store/handlers |
| Idempotent | Safe to repeat with the same result | दोहराने पर भी वही नतीजा |

---

## ⚡ 3-Line Summary
**English:**
1. `useMutation` runs writes on demand through `mutate(vars)` and tracks pending/error/success.
2. After success, invalidate or update related queries so the UI is fresh.
3. Mutations are not retried by default; pass one variables object to `mutate`.

**Hindi:**
1. `useMutation` writes को `mutate(vars)` से on demand चलाता है और pending/error/success track करता है।
2. Success के बाद related queries को invalidate या update करो ताकि UI ताज़ा रहे।
3. Mutations default में retry नहीं होते; `mutate` को एक ही variables object दो।

---

## ➡️ Next Topic
**113. React Query Caching** — `staleTime`, `gcTime`, query keys और invalidation की गहराई से समझ। इसी से तय होता है कि कब refetch हो और कब cache से जवाब मिले।
