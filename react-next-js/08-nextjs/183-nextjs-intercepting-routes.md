# 183. Next.js Intercepting Routes
# हिंदी में: Next.js Intercepting Routes — Link click पर modal, direct URL पर पूरा page

---

## 🔵 Simple Definition (English)
**Intercepting routes** let you load a route from another part of the app inside the current layout, usually as a modal, while the URL changes to the real route. If the user opens or refreshes that URL directly, the full page is shown instead.

## 🔵 सरल परिभाषा (Hindi)
**Intercepting routes** किसी दूसरे route को current layout के अंदर (अक्सर modal में) दिखाने देते हैं, जबकि URL असली route का हो जाता है। अगर user उस URL को सीधे खोले या refresh करे तो modal की जगह पूरा page दिखता है।

---

## 🔴 Problem it Solves

Modals built with `useState` have no URL: you cannot share them, the back button closes the whole page instead of the modal, and a refresh loses the modal. Making every modal a full page breaks the browsing flow (you lose the feed scroll position). Intercepting routes give a modal with a real, shareable URL, working back button, and a crawlable full page.

```jsx
// PROBLEM: state-based modal has no URL and refresh loses it
const [open, setOpen] = useState(false);

// SOLUTION: /photo/42 opens as a modal from the feed,
// and as a full page when opened directly
```

## 🔴 यह क्यों बना? (Hindi)
`useState` वाले modal का कोई URL नहीं होता: उसे share नहीं कर सकते, back बटन modal की जगह पूरा page बंद कर देता है, और refresh पर modal गायब हो जाता है। हर modal को पूरा page बना दें तो browsing flow टूटता है (feed की scroll position खो जाती है)। Intercepting routes असली, share करने लायक URL वाला modal देते हैं, जिसमें back बटन चलता है और पूरा page crawl भी हो सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create the real route: app/photo/[id]/page.js (the full page)
Step 2 → Create a parallel slot for the modal: app/@modal in the root layout
Step 3 → Inside it, make an intercepting folder: app/@modal/(.)photo/[id]/page.js
Step 4 → On SOFT navigation (Link click) to /photo/42, Next.js intercepts and renders the modal
Step 5 → The URL changes to /photo/42, the feed stays rendered behind the modal
Step 6 → On HARD navigation (refresh, shared link) the real page app/photo/[id] renders
Step 7 → Close the modal with router.back()

Conventions (based on route segments, not file system folders):
(.)   same level      (..)  one level up      (..)(..)  two levels up      (...)  from root app
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → असली route बनाओ: app/photo/[id]/page.js (पूरा page)
Step 2 → Modal के लिए parallel slot बनाओ: root layout में app/@modal
Step 3 → उसके अंदर intercepting folder बनाओ: app/@modal/(.)photo/[id]/page.js
Step 4 → /photo/42 पर SOFT navigation (Link click) में Next.js intercept करके modal दिखाता है
Step 5 → URL /photo/42 हो जाता है, पीछे feed वैसी ही रहती है
Step 6 → HARD navigation (refresh, shared link) पर असली page app/photo/[id] render होता है
Step 7 → Modal बंद करने के लिए router.back() इस्तेमाल करो

Conventions (route segments पर आधारित, file system folders पर नहीं):
(.)   उसी level पर      (..)  एक level ऊपर      (..)(..)  दो level ऊपर      (...)  root app से
```

---

## 🟡 Real World Example
**Instagram feed:** Clicking a photo in the feed opens it in a modal over the feed, and the address bar changes to `/p/Cxyz`. Press Back and the modal closes with the feed scroll position intact. If you paste `/p/Cxyz` in a new tab, Instagram shows the full post page with comments and SEO tags. Another example is a Flipkart "Quick view" for a product from a listing.

## 🟡 Real Example Hindi mein
**Instagram feed:** Feed में किसी photo पर click करने से वह feed के ऊपर modal में खुलती है और address bar `/p/Cxyz` हो जाता है। Back दबाओ तो modal बंद हो जाता है और feed की scroll position वैसी ही रहती है। नए tab में `/p/Cxyz` paste करो तो पूरा post page comments और SEO tags के साथ दिखता है। दूसरा उदाहरण: Flipkart की listing से product का "Quick view"।

---

## 💻 Code Example — Basic

```
app/
├── layout.jsx                      ← renders {children} and {modal}
├── page.jsx                        ← the feed with links
├── @modal/
│   ├── default.jsx                 ← returns null (no modal)
│   └── (.)photo/[id]/page.jsx      ← intercepted version (modal)
└── photo/[id]/page.jsx             ← the full page
```

```jsx
// app/layout.jsx: root layout has a modal slot
export default function RootLayout({ children, modal }) {
  return (
    <html lang="en">
      <body>
        {children}                                     {/* feed or full photo page */}
        {modal}                                        {/* modal overlay when intercepted */}
      </body>
    </html>
  );
}
```

```jsx
// app/page.jsx: the feed, each photo links to its real URL
import Link from 'next/link';                          // client-side navigation

const photos = [{ id: 1 }, { id: 2 }, { id: 3 }];      // fake feed data

export default function Feed() {
  return (
    <ul>
      {photos.map(p => (
        <li key={p.id}>
          <Link href={`/photo/${p.id}`}>Open photo {p.id}</Link> {/* soft nav → intercepted modal */}
        </li>
      ))}
    </ul>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// app/@modal/(.)photo/[id]/page.jsx: the modal version (Server Component wrapper)
import Modal from '@/components/Modal';                // Client Component for closing behavior

export default async function PhotoModal({ params }) {
  const { id } = await params;                         // Next.js 15+: params is a Promise
  return (
    <Modal>
      <h2>Photo {id}</h2>                              {/* same data as the page, in a dialog */}
      <img src={`https://picsum.photos/seed/${id}/600/400`} alt={`Photo ${id}`} width={600} height={400} />
    </Modal>
  );
}
```

```jsx
// components/Modal.jsx: closes with router.back() so URL and history stay correct
'use client';                                          // uses router and effects
import { useRouter } from 'next/navigation';           // App Router navigation hook
import { useEffect } from 'react';

export default function Modal({ children }) {
  const router = useRouter();                          // navigation controls

  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') router.back(); }; // Esc closes the modal
    document.addEventListener('keydown', onKey);       // listen globally
    return () => document.removeEventListener('keydown', onKey);     // cleanup
  }, [router]);

  return (
    <div
      onClick={() => router.back()}                    // clicking the backdrop closes
      style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,.6)', display: 'grid', placeItems: 'center' }}
    >
      <div
        role="dialog"                                  // accessibility role
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}           // clicks inside do not close
        style={{ background: '#fff', padding: 16, borderRadius: 8 }}
      >
        {children}
        <button onClick={() => router.back()}>Close</button> {/* explicit close */}
      </div>
    </div>
  );
}
```

```jsx
// app/photo/[id]/page.jsx: full page when the URL is opened directly
export default async function PhotoPage({ params }) {
  const { id } = await params;
  return (
    <main>
      <h1>Photo {id}</h1>                              {/* full layout, SEO-friendly */}
      <img src={`https://picsum.photos/seed/${id}/900/600`} alt={`Photo ${id}`} width={900} height={600} />
    </main>
  );
}
```

---

## 🟠 Real App Integration

Typical use: login modal from any page (`/login` as modal, full page on direct visit), product quick view in Flipkart-style listings, image lightbox in galleries. Share the data-fetching function between the modal and the page so both stay consistent.

```jsx
// lib/photos.js: share one data function between the modal and the full page
export async function getPhoto(id) {
  const res = await fetch(`https://jsonplaceholder.typicode.com/photos/${id}`); // example API
  if (!res.ok) return null;                              // handle missing item
  return res.json();                                     // photo data
}
// Both app/@modal/(.)photo/[id]/page.jsx and app/photo/[id]/page.jsx call getPhoto(id).
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Closing the modal with `router.push('/')` instead of `router.back()`
✅ **Correct:** Use `router.back()` to keep history and scroll position

```jsx
// Wrong: pushes a new history entry; Back button then reopens the modal
<button onClick={() => router.push('/')}>Close</button>   {/* ❌ */}

// Right
<button onClick={() => router.back()}>Close</button>     {/* ✅ pops the intercepted entry */}
```

❌ **Mistake 2:** Misreading `(..)`: it is based on route segments, not folders
✅ **Correct:** Count route segments; slots like `@modal` and groups `(group)` do not count

```
// Wrong assumption: app/@modal/(..)photo intercepts "one folder up"  ❌
// @modal is not a segment, so (.)photo is the correct convention for app/photo ✅
app/@modal/(.)photo/[id]/page.jsx   → intercepts /photo/[id]
```

---

## 🧠 Tricky Interview Question

A user is on the feed `/`, clicks a photo link to `/photo/5` (modal opens), then presses the browser Refresh button. What is shown, and why?

**Answer:** The full photo page from `app/photo/[id]/page.jsx` is shown, not the modal. Interception only applies to soft (client-side) navigation, because it depends on the previous layout state staying alive in the browser. A refresh is a hard navigation: the server renders `/photo/5` from scratch and matches the real route. In addition, the `@modal` slot needs a `default.jsx` returning `null` so that on this hard load the modal slot has something to render. This is also why the full page should be good SEO content: crawlers always see the real route.

---

## ⚫ Interview Questions + Answers

Q1: What problem do intercepting routes solve?
A1: They let you show a route inside the current context (a modal) with a real URL, so it is shareable, works with the back button, and falls back to a full page on direct access.

Q2: What do `(.)`, `(..)` and `(...)` mean?
A2: `(.)` matches the same route segment level, `(..)` one level above, `(..)(..)` two levels above, and `(...)` matches from the root `app` directory. They refer to route segments, not file-system folders.

Q3: Why are intercepting routes usually combined with parallel routes?
A3: The modal needs its own slot (`@modal`) next to `children`, so the feed stays rendered behind the modal. The slot also lets the layout render nothing when no modal is active.

Q4: What happens on refresh when a modal is open?
A4: The real full-page route renders, because interception works only on soft navigation.

Q5: How should the modal be closed?
A5: With `router.back()`, so history, URL and the previous scroll position are restored.

---

## 🔷 When to Use + When Not to Use
✅ **Use intercepting routes when:**
- A modal should be shareable and refresh-safe (login, product quick view, photo lightbox)
- You want Back to close the modal
- The same content should also exist as a full SEO page

❌ **Avoid when:**
- A simple confirm dialog does not need a URL (use plain state)
- You cannot maintain two views (modal + full page) of the same content
- The team is new to the App Router, as folder conventions are easy to misread

---

## 📊 Visual Diagram

```
  Feed (/) ── click Link to /photo/5 ──► SOFT navigation
        │
        ▼
  Intercepted by app/@modal/(.)photo/[id]
  ┌───────────────────────────────┐
  │ Feed still rendered behind    │   URL = /photo/5
  │   ┌───────────────┐           │
  │   │  MODAL: photo │ ← router.back() closes
  │   └───────────────┘           │
  └───────────────────────────────┘

  Refresh / shared link (HARD navigation)
        │
        ▼
  app/photo/[id]/page.jsx → full page (SEO, no modal)

  Re-render behavior: the feed does not unmount, so its state and scroll stay.
  Only the @modal slot changes.
  Performance: no full page reload; the modal data is fetched on the server
  and streamed in.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Intercepting route | Route shown in current layout | Current layout में दिखने वाला route |
| `(.)` | Match same level | उसी level पर match |
| `(..)` | Match one level up | एक level ऊपर match |
| `(...)` | Match from app root | root app से match |
| @modal slot | Parallel route holding the modal | Modal रखने वाला parallel route |
| Soft navigation | Client-side navigation | Client-side navigation |
| Hard navigation | Full page load | पूरा page load |
| router.back() | Go to previous history entry | पिछली history entry पर जाना |

---

## ⚡ 3-Line Summary
**English:**
1. Intercepting routes show a route inside the current layout (as a modal) on soft navigation, with a real URL.
2. Direct visits or refresh render the full route, and modals use a `@modal` slot with `default.js`.
3. Close with `router.back()` and remember conventions count route segments, not folders.

**Hindi:**
1. Intercepting routes soft navigation पर किसी route को current layout के अंदर (modal में) असली URL के साथ दिखाते हैं।
2. सीधे खोलने या refresh पर पूरा route render होता है, और modals `default.js` वाले `@modal` slot का उपयोग करते हैं।
3. `router.back()` से बंद करो और याद रखो कि conventions route segments गिनते हैं, folders नहीं।

---

## ➡️ Next Topic
**184. Server Actions in Next.js** — `'use server'` functions से form submit और data mutation बिना अलग API route लिखे करना, validation, `revalidatePath` और `useActionState` के साथ।
