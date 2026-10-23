# F01. Frontend System Design Framework (RADIO)
# हिंदी में: Frontend System Design Framework — frontend इंटरव्यू में किसी भी UI (news feed, chat, autocomplete) को ढाँचे में डिज़ाइन करने का तरीका: Requirements → Architecture → Data model → Interface (API) → Optimizations

---

## 🔵 Simple Definition (English)
**Frontend system design** interviews ask you to design the **client side** of a product (a news feed, chat app, autocomplete, video player, e-commerce PDP, Google Docs-like editor) for **web and/or mobile**: components, state, data fetching, APIs with the backend, performance, accessibility, offline and real-time behaviour, security, i18n and testing.
**RADIO** is a popular structure to answer them:
- **R**equirements (functional + non-functional)
- **A**rchitecture (high-level components & data flow)
- **D**ata model (client state, entities, normalization, caching)
- **I**nterface (API between client & server, component APIs)
- **O**ptimizations & deep dives (performance, network, a11y, i18n, security, offline, observability)

## 🔵 सरल परिभाषा (Hindi)
Frontend system design इंटरव्यू में आपको किसी ऐप का client हिस्सा डिज़ाइन करना होता है — components, state, डेटा लाना, API, performance, accessibility, offline, real-time, security।
जवाब का ढाँचा RADIO: Requirements (क्या चाहिए) → Architecture (मुख्य हिस्से और डेटा का बहाव) → Data model (client का state) → Interface (API) → Optimizations (performance, a11y, i18n, security, offline)।

---

## 🔴 Problem it Solves
Without a structure, candidates:
- Jump straight into React code or a component tree and miss **requirements** (offline? SEO? mobile? scale?).
- Ignore **data flow and state** (where does the data live? how is it cached and invalidated?).
- Forget **performance** (bundle size, rendering, images), **accessibility**, **security (XSS)**, and **network realities** (slow 3G, retries).
- Run out of time without covering trade-offs.

RADIO gives a **repeatable 45-minute plan** that shows senior-level thinking: breadth first, then depth where it matters.

## 🔴 यह क्यों बना? (Hindi)
बिना ढाँचे के लोग सीधे React code लिखने लगते हैं और ज़रूरी बातें छूट जाती हैं — offline, SEO, state कहाँ रहेगा, cache कैसे, performance, accessibility, XSS, धीमा नेटवर्क।
RADIO 45 मिनट का दोहराने लायक प्लान देता है जो senior-level सोच दिखाता है।

---

## 🟢 How it Works — Step by Step

### Time plan (45–60 min interview)

```
R  Requirements ............ 5–8 min   (clarify! write them down)
A  Architecture ............ 8–10 min  (diagram of components/modules + data flow)
D  Data model .............. 5–8 min   (entities, client state shape, cache)
I  Interface (APIs) ........ 5–8 min   (REST/GraphQL/WebSocket contracts, pagination)
O  Optimizations/deep dives  15–20 min (perf, network, a11y, i18n, security, offline, testing)
Leave 2–3 min for trade-offs & questions.
```

### R — Requirements (ask, then confirm)

```
Functional (what users do):
  - Core flows: e.g. feed: view posts, infinite scroll, like, comment, create post with image
  - Which platforms: web (desktop/mobile web), native apps (React Native)?
  - Real-time? (new posts appear live, chat), offline? drafts?
Non-functional (quality):
  - Performance targets: LCP < 2.5 s, INP < 200 ms, 60 fps scrolling, JS budget
  - Scale: number of items, frequency of updates, users on low-end Android + 3G
  - SEO needs (public pages → SSR/SSG)
  - Accessibility (WCAG AA), i18n (Hindi/English, RTL?), browsers supported
  - Security & privacy (auth, XSS, PII), analytics/observability
Out of scope: say explicitly (e.g., backend ranking, ads)
```

### A — Architecture

```
                 ┌──────────────────────────── Client app ───────────────────────────┐
  Server/APIs ◄──┤ Network layer (fetch/axios/Apollo, retries, auth refresh, cache)  │
  (REST/GraphQL/ │        ▲                         ▼                                │
   WebSocket)    │ Data store / server-state cache (React Query / Apollo / Redux)    │
                 │        ▲                         ▼                                │
                 │ Controller/hooks (business logic: useFeed, useLike)               │
                 │        ▲                         ▼                                │
                 │ View: components (FeedList → PostCard → Media, Actions, Comments) │
                 │ Cross-cutting: router, auth, i18n, analytics, error boundary,     │
                 │                feature flags, offline storage (IndexedDB/MMKV)    │
                 └─────────────────────────────────────────────────────────────────┘
Also decide: rendering strategy (CSR/SSR/SSG/ISR — Topic F03), routing, code splitting boundaries.
```

### D — Data model (client side)

```
Entities: Post {id, author:UserRef, text, media[], likeCount, likedByMe, createdAt}, User {id, name, avatar}
State categories (Topic F09):
  server state  → cached copies of API data (React Query / Apollo normalized cache)
  client/UI     → modal open, input text, selected tab
  URL state     → filters, page, search query (shareable)
  persisted     → drafts, auth tokens (secure), offline queue
Normalization: store entities by id (users once, referenced by posts) → consistent updates
Pagination state: pages + cursors; optimistic updates & rollback
```

### I — Interface (API design from the client's perspective)

```
GET  /feed?cursor=&limit=20          → { items: Post[], nextCursor }      (cursor pagination, Topic 39)
POST /posts/{id}/like                 → 200 { likeCount, likedByMe }        (idempotent)
POST /posts { text, mediaIds }        → 201 Post   (media via presigned upload first)
WS   /realtime → events: post.created, post.liked (or SSE)
Component interfaces: <Feed fetchPage={...} renderItem={...} />, accessibility props, loading/error states
Consider: GraphQL/BFF to fetch exactly what a screen needs in one call (Topics 07a, 93a)
```

### O — Optimizations & deep dives (pick the most relevant)

```
Performance:  rendering strategy, code splitting, lazy loading, list virtualization, image optimization
              (responsive sizes, WebP/AVIF, lazy, placeholders), memoization, avoiding layout shift,
              prefetching, caching (HTTP, SW), Web Vitals budgets
Network:      batching, debounce/throttle, request dedup, retries w/ backoff, offline queue, compression,
              HTTP/2, preconnect
UX:           skeletons, optimistic updates, error & empty states, infinite scroll vs pagination
Accessibility: semantic HTML, keyboard nav, focus management, ARIA, screen readers, color contrast
i18n:         translations, plurals, dates/numbers/currency (₹), RTL
Security:     XSS (escape, sanitize, CSP), CSRF, token storage, clickjacking, dependency risk
Offline/real-time: service worker, IndexedDB, sync; WebSocket/SSE/polling
Observability: error tracking (Sentry), RUM (Web Vitals), logging, feature flags/A-B tests
Testing:      unit (components/hooks), integration, E2E (Playwright/Detox), visual regression
```

### Common FE design questions
```
News feed (FB/Twitter) · Autocomplete/typeahead · Chat app (WhatsApp Web) · Image carousel/gallery ·
Video player (YouTube) · E-commerce PDP/checkout · Google Docs collaborative editor · Data table with
sort/filter (dashboard) · Kanban board (drag & drop) · Poll/quiz widget · Photo upload flow ·
Notifications center · Maps-based tracking UI · Calendar (Google Calendar)
→ Full examples in 09-FullStack-Design-Problems (P01–P10).
```

## 🟢 कैसे काम करता है? (Hindi)
1. R: पहले सवाल पूछो — कौन-से फ़ीचर, web या mobile, real-time/offline, performance लक्ष्य, SEO, accessibility, भाषाएँ; और क्या scope में नहीं है।
2. A: ढाँचा बनाओ — network layer → डेटा cache → hooks/logic → components; साथ में router, auth, i18n, error boundary; rendering तरीका (CSR/SSR)।
3. D: client का डेटा — entities (Post, User), state के प्रकार (server, UI, URL, persisted), normalization, pagination।
4. I: API — cursor pagination, idempotent like, WebSocket events; components के props।
5. O: सबसे ज़रूरी गहराइयाँ — performance (virtualization, images, code splitting), network (debounce, retry), a11y, i18n, XSS, offline, monitoring, testing।

---

## 🟡 Real World Example

**Meta / Google / Uber frontend interviews** — Meta's "front-end system design" round and Google's "UI design" variants commonly ask for a news feed, autocomplete, or a component library piece. Interviewers look for requirement clarification, state and data flow, performance at scale and accessibility, not pixel-perfect code.

**GreatFrontEnd / frontendinterviewhandbook** — popularized the RADIO framework with worked examples (news feed, autocomplete, image carousel).

**Indian product companies (Flipkart, Swiggy, Razorpay, CRED, Atlassian India)** — ask for designs such as "design the Swiggy menu page", "design a checkout widget", "design a real-time order tracking UI" or "design a data table with 100k rows", focusing on performance on low-end devices and slow networks.

## 🟡 Real Example Hindi में
Meta, Google, Uber के frontend इंटरव्यू में news feed, autocomplete जैसे सवाल आते हैं — वो requirements, state/data flow, performance और accessibility देखते हैं, pixel-perfect code नहीं।
Flipkart, Swiggy, Razorpay, CRED जैसी कंपनियाँ "Swiggy menu page डिज़ाइन करो" या "1 लाख rows वाली table" पूछती हैं — कमज़ोर फ़ोन और धीमे नेटवर्क पर performance पर ज़ोर।

---

## 🟠 My Stack Example

### A template you can sketch for any problem (React / Next.js / React Native)
```
src/
  features/feed/
    api.ts            ← typed fetchers (getFeed, likePost) — Interface
    hooks.ts          ← useFeed (useInfiniteQuery), useLike (optimistic mutation) — Controller
    components/
      Feed.tsx        ← virtualized list, empty/error/loading states — View
      PostCard.tsx    ← memoized, a11y labels
      PostActions.tsx
    types.ts          ← Post, User — Data model
  shared/
    http.ts           ← axios instance: auth header, refresh on 401, retry/backoff, request id
    queryClient.ts    ← React Query defaults (staleTime, retries)
    i18n/             ← en.json, hi.json
    analytics.ts, errorBoundary.tsx, featureFlags.ts
```

### Data + interface in code (works for Next.js and RN)
```ts
// features/feed/api.ts
export type Post = { id: string; author: { id: string; name: string; avatar: string }; text: string;
                     media: { url: string; w: number; h: number; blurhash?: string }[];
                     likeCount: number; likedByMe: boolean; createdAt: string };
export const getFeed = (cursor?: string) =>
  http.get<{ items: Post[]; nextCursor: string | null }>('/feed', { params: { cursor, limit: 20 } }).then(r => r.data);

// features/feed/hooks.ts
export const useFeed = () => useInfiniteQuery({
  queryKey: ['feed'], queryFn: ({ pageParam }) => getFeed(pageParam),
  initialPageParam: undefined as string | undefined,
  getNextPageParam: (last) => last.nextCursor ?? undefined, staleTime: 30_000,
});
```

### How to speak in the interview (script)
```
"Let me first clarify requirements… (list). I'll assume web + mobile web, SEO not needed for the feed,
 users on mid/low-end Android with 4G, 60 fps scrolling, WCAG AA.
 Architecture: network layer with auth & retry → React Query cache → hooks → virtualized components.
 Data: normalized Post/User entities, cursor pagination…
 API: GET /feed?cursor, POST /like idempotent, SSE for new posts…
 Deep dives: virtualization, image strategy, optimistic likes with rollback, a11y of infinite scroll
 (announce new content, focus), XSS-safe rendering of user text, offline drafts, Web Vitals monitoring."
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you approach a frontend system design interview?**
A1: Follow a structure like RADIO. Clarify requirements (functional flows, platforms, scale, performance and accessibility targets, SEO, offline and real-time needs, out-of-scope items). Sketch the architecture (network layer, data/cache layer, controllers/hooks, view components, cross-cutting concerns, rendering strategy). Define the client data model and state categories, then the interfaces (APIs, real-time channels, component contracts). Spend most of the time on the deep dives that matter for this product (performance, network resilience, UX states, a11y, i18n, security, offline, observability), discussing trade-offs.

**Q2: What's different between frontend and backend system design?**
A2: Backend design focuses on scalability, data storage, consistency and distributed systems for many users at once. Frontend design focuses on one user's device: rendering performance, network efficiency on unreliable connections, state management and caching on the client, UX states (loading, error, empty, optimistic), accessibility, internationalization, browser and device constraints (low-end phones, memory), security in the browser (XSS), and how the client contract shapes the API. Both need good API design and trade-off reasoning.

**Q3: What non-functional requirements would you ask about for a news feed?**
A3: Target devices and networks (low-end Android, 3G or 4G), performance budgets (LCP, INP, scroll at 60 fps, bundle size), expected item volume and update frequency (real-time?), SEO needs, offline or flaky network support, accessibility level (WCAG AA, screen readers, keyboard), supported locales and RTL, browser support, privacy and security constraints, analytics and experimentation needs, and whether it runs on web, native or both.

**Q4: How do you decide what to deep dive into?**
A4: Pick the areas with the highest risk or impact for that product, and mention the rest briefly. Feeds and tables: virtualization, pagination, image loading, optimistic updates. Autocomplete: debouncing, caching, race conditions, keyboard a11y. Chat: real-time transport, ordering, offline queue. Editors: conflict resolution (OT/CRDT), performance of large documents. Checkout: correctness, security, validation, payment SDK integration. Ask the interviewer which areas interest them.

**Q5: How do you show "senior" thinking in a frontend design round?**
A5: Drive the conversation with clarifying questions and explicit assumptions. Separate concerns cleanly (network, cache, state, view). Reason about data flow and state ownership, quantify performance budgets, and consider real users (slow devices, networks, screen readers, Indian languages). Design APIs that serve the UI (pagination, batching, error formats), address failure modes (retries, offline, partial data), security (XSS, CSP, token storage), observability (RUM, error tracking) and testing, and articulate trade-offs and alternatives.

---

## 🔷 Trade-offs
✅ Structured framework: covers breadth, manages time, shows maturity.
❌ Don't be robotic: adapt depth to the problem and interviewer's interest; skip irrelevant sections quickly.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RADIO | Requirements, Architecture, Data, Interface, Optimizations | इंटरव्यू का ढाँचा |
| Functional req. | What the UI must do | क्या करना है |
| Non-functional req. | Performance, a11y, SEO, security | गुणवत्ता की माँगें |
| Server state | Cached API data on client | client पर API डेटा |
| Client/UI state | Local UI-only state | सिर्फ़ UI की स्थिति |
| Normalization | Store entities by id | id से डेटा रखना |
| Virtualization | Render only visible items | सिर्फ़ दिखने वाले items |
| Optimistic update | Update UI before server confirms | पुष्टि से पहले UI बदलना |
| Web Vitals | Core performance metrics | मुख्य performance नाप |
| a11y / i18n | Accessibility / internationalization | सुलभता / अंतरराष्ट्रीयकरण |

---

## ⚡ 3-Line Summary
**English:**
1. Use RADIO: Requirements → Architecture → Data model → Interface → Optimizations, with a time plan.
2. Architecture = network layer → server-state cache → hooks/controllers → components + cross-cutting (auth, i18n, errors, analytics).
3. Deep dive on what matters for the product: performance, network resilience, UX states, a11y, i18n, security, offline, observability.

**Hindi:**
1. RADIO: Requirements → Architecture → Data → Interface → Optimizations, समय के प्लान के साथ।
2. ढाँचा: network layer → डेटा cache → hooks → components + auth, i18n, errors, analytics।
3. ज़रूरी गहराई: performance, नेटवर्क, UX states, a11y, i18n, security, offline, monitoring।

---

## ➡️ Next Topic Suggestion
**F02. How the Browser Renders a Page (Critical Rendering Path)** — To optimize anything on the web, you must know what the browser does with HTML, CSS and JS. Next: parsing, DOM/CSSOM, layout, paint, compositing, and render-blocking resources.
