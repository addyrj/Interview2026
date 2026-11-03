# 114. Optimistic Updates
# हिंदी में: Optimistic Updates — Server के जवाब से पहले UI बदलना

---

## 🔵 Simple Definition (English)
An **optimistic update** changes the UI immediately, assuming the server request will succeed, and **rolls back** if it fails. In TanStack Query v5 there are two ways: update the **cache** in `onMutate` (with rollback in `onError`), or render the pending **`variables`** of the mutation directly in the UI.

## 🔵 सरल परिभाषा (Hindi)
**Optimistic update** में UI तुरंत बदल दिया जाता है, यह मानकर कि server request सफल होगी, और fail होने पर पुरानी state पर **rollback** कर देते हैं। TanStack Query v5 में दो तरीके हैं: `onMutate` में **cache** update करना (`onError` में rollback के साथ), या mutation के pending **`variables`** को सीधे UI में दिखाना।

---

## 🔴 Problem it Solves

When the user taps "Like", waiting 400 ms for the server before the heart turns red feels slow, especially on mobile networks. Showing a spinner for every tiny action makes an app feel sluggish. But if you update the UI blindly and the request fails, the UI lies to the user.

```jsx
// PROBLEM: UI waits for the network
await api.like(postId);          // 400ms with no feedback
setLiked(true);                  // heart changes only now

// SOLUTION: change UI first, then confirm. If the request fails → restore the old state
setLiked(true);                  // instant
api.like(postId).catch(() => setLiked(false)); // rollback on failure
```

## 🔴 यह क्यों बना? (Hindi)
User "Like" दबाता है और heart लाल होने के लिए server के 400 ms इंतज़ार करना धीमा लगता है, खासकर mobile network पर। हर छोटी action पर spinner दिखाने से app सुस्त लगता है। लेकिन UI को आँख बंद करके बदल दें और request fail हो जाए तो UI user से झूठ बोलता है। Optimistic update में UI तुरंत बदलता है और fail पर पुराना state लौट आता है।

---

## 🟢 How it Works — Step by Step

```
Approach A: cache-based (works across many components)
Step 1 → onMutate(vars): cancel in-flight queries for the key (cancelQueries) so they don't overwrite us
Step 2 → Snapshot the previous cache value: previous = qc.getQueryData(key)
Step 3 → Write the optimistic value: qc.setQueryData(key, (old) => newValue)
Step 4 → Return { previous } from onMutate → becomes `context` in the other callbacks
Step 5 → onError(err, vars, context): restore with qc.setQueryData(key, context.previous)
Step 6 → onSettled: qc.invalidateQueries({ queryKey: key }) → refetch the truth from the server

Approach B: variables-based (simplest, one place in UI)
Step 1 → const m = useMutation(...)
Step 2 → While m.isPending, render m.variables as an extra (ghost) item in the list
Step 3 → On error, show it with a "Retry" button; on success the invalidation refetches the real list
```

## 🟢 कैसे काम करता है? (Hindi)
```
तरीका A: cache-based (कई components में काम करता है)
Step 1 → onMutate(vars): key की in-flight queries cancel करो (cancelQueries) ताकि वे हमारा update overwrite न करें
Step 2 → पुरानी cache value का snapshot लो: previous = qc.getQueryData(key)
Step 3 → Optimistic value लिखो: qc.setQueryData(key, (old) => newValue)
Step 4 → onMutate से { previous } return करो → बाकी callbacks में यही `context` बनता है
Step 5 → onError(err, vars, context): qc.setQueryData(key, context.previous) से restore करो
Step 6 → onSettled: qc.invalidateQueries({ queryKey: key }) → server से सच्चा data दोबारा लो

तरीका B: variables-based (सबसे सरल, UI में एक ही जगह)
Step 1 → const m = useMutation(...)
Step 2 → m.isPending के दौरान m.variables को list में एक अतिरिक्त (ghost) item की तरह दिखाओ
Step 3 → Error पर "Retry" button के साथ दिखाओ; success पर invalidation असली list refetch कर देता है
```

---

## 🟡 Real World Example
**Instagram like / Swiggy "Add to favourites":** Tapping the heart turns it red instantly and the count goes from 120 to 121. The request goes out in the background. If the network is down, the heart turns grey again, the count returns to 120 and a small toast says "Couldn't save. Try again." The user felt no delay in the normal case.

## 🟡 Real Example Hindi mein
**Instagram like / Swiggy "Add to favourites":** Heart दबाते ही तुरंत लाल हो जाता है और count 120 से 121 हो जाता है। Request background में जाती है। Network बंद हो तो heart फिर grey हो जाता है, count 120 पर लौटता है और छोटा toast कहता है "Couldn't save. Try again."। सामान्य स्थिति में user को कोई देरी महसूस नहीं होती।

---

## 💻 Code Example — Basic

```jsx
// Basic (Approach B): show the pending variables as a ghost item, no cache surgery needed
import { QueryClient, QueryClientProvider, useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { createRoot } from 'react-dom/client';

const queryClient = new QueryClient();

let db = [{ id: 1, text: 'Buy milk' }];                         // fake server data
const api = {
  list: async () => [...db],
  add: async (text) => {
    await new Promise((r) => setTimeout(r, 800));               // simulate a slow network
    if (text.includes('fail')) throw new Error('Server said no'); // simulate an error
    db = [...db, { id: Date.now(), text }];
    return db.at(-1);
  },
};

function Todos() {
  const qc = useQueryClient();
  const [text, setText] = useState('');
  const todos = useQuery({ queryKey: ['todos'], queryFn: api.list });

  const add = useMutation({
    mutationFn: api.add,
    onSettled: () => qc.invalidateQueries({ queryKey: ['todos'] }), // always refetch the truth
  });

  return (
    <div>
      <input value={text} onChange={(e) => setText(e.target.value)} />
      <button onClick={() => { add.mutate(text); setText(''); }}>Add</button>
      <ul>
        {todos.data?.map((t) => <li key={t.id}>{t.text}</li>)}
        {add.isPending && <li style={{ opacity: 0.5 }}>{add.variables}</li>} {/* optimistic ghost item */}
        {add.isError && (
          <li style={{ color: 'red' }}>
            {add.variables} — failed
            <button onClick={() => add.mutate(add.variables)}>Retry</button> {/* retry with same variables */}
          </li>
        )}
      </ul>
    </div>
  );
}

createRoot(document.getElementById('root')).render(
  <QueryClientProvider client={queryClient}><Todos /></QueryClientProvider>
);
```

## 💻 Code Example — Advanced

```jsx
// Advanced (Approach A): optimistic "like" in the cache with snapshot, rollback and re-sync
import { useMutation, useQueryClient } from '@tanstack/react-query';

// Hook that toggles a like for a post shown in a ['posts'] list cache
export function useToggleLike() {
  const qc = useQueryClient();
  const key = ['posts'];                                         // the cache entry we edit

  return useMutation({
    mutationFn: async ({ id, liked }) => {                       // server call
      const res = await fetch(`/api/posts/${id}/like`, {
        method: liked ? 'DELETE' : 'POST',                       // unlike : like
      });
      if (!res.ok) throw new Error('Like failed');
      return res.json();
    },

    // 1) BEFORE the request
    onMutate: async ({ id, liked }) => {
      await qc.cancelQueries({ queryKey: key });                 // stop refetches that would overwrite us
      const previous = qc.getQueryData(key);                     // snapshot for rollback

      qc.setQueryData(key, (old = []) =>                         // optimistic write (immutable update)
        old.map((p) =>
          p.id === id
            ? { ...p, liked: !liked, likes: p.likes + (liked ? -1 : 1) }
            : p
        )
      );

      return { previous };                                       // → `context` in onError / onSettled
    },

    // 2) ON FAILURE → restore the snapshot
    onError: (_err, _vars, context) => {
      if (context?.previous) qc.setQueryData(key, context.previous); // rollback
      // toast.error('Could not update like')                    // tell the user
    },

    // 3) ALWAYS → sync with the server (fixes any drift)
    onSettled: () => qc.invalidateQueries({ queryKey: key }),
  });
}

// Usage
export function LikeButton({ post }) {
  const { mutate } = useToggleLike();
  return (
    <button
      aria-pressed={post.liked}                                  // a11y: toggle state
      onClick={() => mutate({ id: post.id, liked: post.liked })} // UI flips instantly from the cache
    >
      {post.liked ? '♥' : '♡'} {post.likes}
    </button>
  );
}
```

Re-render behavior: `setQueryData` notifies every component observing `['posts']`, so all of them re-render with the new value at once (the list, the header counter). After `onSettled` the invalidation fetches the truth and, if it equals the optimistic value, structural sharing keeps references equal, so no extra visual change happens. Performance impact: very cheap (one in-memory write), and it removes perceived latency.

---

## 🟠 Next.js Connection

React 19 (used by Next.js 15 App Router) adds `useOptimistic`, which fits Server Actions and forms without TanStack Query. The optimistic value exists only while the action runs and is replaced by the real server state afterwards.

```jsx
// app/posts/LikeButton.jsx
'use client';                                                    // hooks → Client Component
import { useOptimistic, startTransition } from 'react';          // React 19 hook
import { toggleLikeAction } from './actions';                    // 'use server' action (see below)

export default function LikeButton({ postId, liked, likes }) {
  const [optimistic, setOptimistic] = useOptimistic(             // base state comes from the server props
    { liked, likes },
    (state, nextLiked) => ({ liked: nextLiked, likes: state.likes + (nextLiked ? 1 : -1) })
  );

  function onClick() {
    startTransition(async () => {                                // actions run inside a transition
      setOptimistic(!optimistic.liked);                          // instant UI change
      await toggleLikeAction(postId, !optimistic.liked);         // server work; on throw, state reverts
    });
  }
  return <button onClick={onClick}>{optimistic.liked ? '♥' : '♡'} {optimistic.likes}</button>;
}
```

```jsx
// app/posts/actions.js
'use server';
import { revalidatePath } from 'next/cache';                     // refresh server-rendered data
export async function toggleLikeAction(postId, nextLiked) {
  // await db.likes.set(postId, nextLiked)   → your database write (placeholder)
  revalidatePath('/posts');                                      // new props flow back to the client
}
```

`useOptimistic` is a React 19 API (version-dependent: not in React 18 stable).

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Not cancelling in-flight queries in `onMutate`
✅ **Correct:** `await qc.cancelQueries({ queryKey })` first

```jsx
// Wrong: an older refetch lands after our optimistic write and overwrites it → UI flickers back
onMutate: (vars) => { qc.setQueryData(key, update(vars)); },               // ❌ no cancel

// Right
onMutate: async (vars) => {
  await qc.cancelQueries({ queryKey: key });                               // ✅ stop overwrites
  qc.setQueryData(key, update(vars));
},
```

❌ **Mistake 2:** No rollback snapshot, or mutating the cache object in place
✅ **Correct:** Save `previous`, return it as context, and always create new objects

```jsx
// Wrong: mutating the cached array → no re-render, impossible to roll back
qc.getQueryData(key).push(newItem);                                         // ❌ in-place mutation

// Right
const previous = qc.getQueryData(key);                                      // ✅ snapshot
qc.setQueryData(key, (old = []) => [...old, newItem]);                      // ✅ new array
return { previous };
```

❌ **Mistake 3:** Skipping `onSettled` invalidation
✅ **Correct:** Always refetch at the end so the UI matches the server

```jsx
// Wrong: optimistic id/timestamp stays forever, may differ from server values
useMutation({ mutationFn, onMutate });                                      // ❌ no resync

// Right
useMutation({ mutationFn, onMutate, onSettled: () => qc.invalidateQueries({ queryKey: key }) }); // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
useMutation({
  mutationFn: saveName,
  onMutate: async (name) => {
    qc.setQueryData(['user'], (u) => ({ ...u, name }));   // optimistic, NO cancelQueries
  },
  onError: () => { /* nothing */ },
});
// A background refetch of ['user'] was already in flight when the user clicked Save.
// What does the user see?
```
**Answer:** The name changes instantly, then **flips back to the old name** when the in-flight refetch (started before the save) resolves with the old server data and replaces the optimistic value. After the mutation finishes the old name is still shown until another refetch. Also, on error nothing restores the previous value. The fix: `await qc.cancelQueries({ queryKey: ['user'] })` in `onMutate`, return a `previous` snapshot, restore it in `onError`, and invalidate in `onSettled`.

---

## ⚫ Interview Questions + Answers

Q1: What is an optimistic update and why use it?
A1: Updating the UI before the server confirms, assuming success, then rolling back on failure. It makes interactions feel instant, ideal for likes, toggles, reordering and adding items.

Q2: What does `onMutate` return and who receives it?
A2: Whatever you return (usually `{ previous }`) is passed as the `context`: the third argument of `onError` and the fourth of `onSettled`. It carries the rollback snapshot.

Q3: Why call `cancelQueries`?
A3: To prevent an in-flight refetch from resolving later and overwriting the optimistic cache value.

Q4: What are the two optimistic styles in v5?
A4: (1) Cache-based: `onMutate` + `setQueryData` + rollback, affects all components using the key. (2) UI-based using `useMutation`'s `variables` and `isPending`, simpler and scoped to the component with no rollback code.

Q5: When should you avoid optimistic updates?
A5: For operations with high failure rate or business consequences (payments, order placement, stock-limited purchases), or when the server result is unknowable (generated IDs, price calculations). Show a pending state instead.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Actions almost always succeed (like, bookmark, toggle, reorder, mark as read)
- Instant feedback matters (mobile, slow networks)
- You can express the result locally and roll back cleanly

❌ **Avoid when:**
- Payments, bookings, inventory-limited actions
- The server computes the result (totals, discounts, ids you need immediately)
- Failure is common or the rollback would confuse users

---

## 📊 Visual Diagram

```
 click "Like"
    │
    ├─► onMutate: cancelQueries ─► snapshot(previous) ─► setQueryData(optimistic)
    │                                       │                     │
    │                                       │                     └─► UI shows ♥ 121 instantly
    ▼                                       │
 POST /like ─────────┬── success ───────────┼──────────────► onSettled: invalidate ─► refetch truth
                     │                      │
                     └── error ─► onError: setQueryData(previous) ─► UI back to ♡ 120 (+ toast)

 time:  0ms (UI changes)           400ms (server answers)          450ms (refetch confirms)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Optimistic update | Change UI before server confirms | Server confirm से पहले UI बदलना |
| Rollback | Restore the previous state | पुरानी state लौटाना |
| onMutate | Callback before the request starts | Request शुरू होने से पहले का callback |
| context | Value returned by onMutate | onMutate का return value |
| cancelQueries | Stop in-flight refetches | चल रही refetch रोकना |
| setQueryData | Write directly into the cache | Cache में सीधे लिखना |
| variables | Arguments of the pending mutation | Pending mutation के arguments |
| useOptimistic | React 19 hook for optimistic state | React 19 का optimistic state hook |

---

## ⚡ 3-Line Summary
**English:**
1. Optimistic updates change the UI first and confirm with the server later, rolling back on error.
2. In TanStack Query: `cancelQueries`, snapshot, `setQueryData`, restore in `onError`, invalidate in `onSettled`.
3. Use it for low-risk toggles; avoid it for payments or server-computed results.

**Hindi:**
1. Optimistic updates पहले UI बदलते हैं और server से बाद में confirm करते हैं, error पर rollback करते हैं।
2. TanStack Query में: `cancelQueries`, snapshot, `setQueryData`, `onError` में restore, `onSettled` में invalidate।
3. कम जोखिम वाले toggles के लिए इस्तेमाल करो; payments या server-computed results के लिए नहीं।

---

## ➡️ Next Topic
**122. React.memo — Prevent Re-renders** — Data fetching पूरा हुआ, अब performance: अनावश्यक re-renders कैसे रोकें और `memo` कब काम करता है।
