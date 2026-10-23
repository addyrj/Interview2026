# 02. How to Answer a Frontend / Mobile System Design Round
# हिंदी में: Frontend/Mobile System Design Round कैसे दें — web (React/Next.js) या mobile (React Native) ऐप के client हिस्से को 45–60 मिनट में ढाँचे से डिज़ाइन करना: ज़रूरतें → architecture → data/state → API → performance, offline, real-time, a11y, security जैसी गहराइयाँ

---

## 🔵 Simple Definition (English)
A **frontend or mobile system design round** asks you to design the **client application** (and its contract with the backend) for a product: a news feed, autocomplete, chat, video player, e-commerce product page, collaborative editor, ride-tracking screen, offline notes app.
It's scored on **client architecture, state and data flow, API design from the client's view, performance, UX states, accessibility, offline and real-time behaviour, security and trade-offs**, not on drawing Kafka clusters.
Frameworks to use:
- **Web: RADIO** (F01), i.e. Requirements → Architecture → Data model → Interface (API) → Optimizations.
- **Mobile** (M01): Requirements → App architecture (layers + platform services) → Data and local storage → API and sync contract → Deep dives (offline/sync, performance, push and background, security, releases and old versions).
You should still **sketch the backend touchpoints** (BFF, real-time channel, CDN), but keep the focus on the client.

## 🔵 सरल परिभाषा (Hindi)
Frontend/Mobile design round में किसी product के client ऐप (और backend से उसका contract) का design पूछा जाता है — news feed, autocomplete, chat, video player, product page, collaborative editor, ride tracking, offline notes।
नंबर मिलते हैं: client architecture, state और डेटा का बहाव, client की नज़र से API, performance, loading/error/empty states, accessibility, offline/real-time, security और trade-offs पर — Kafka clusters बनाने पर नहीं। Web के लिए RADIO (Requirements → Architecture → Data → Interface → Optimizations), mobile के लिए M01 वाला ढाँचा (ज़रूरतें → app परतें + platform services → local storage → API/sync → गहराइयाँ); backend के छूने वाले हिस्से (BFF, real-time, CDN) थोड़े में दिखाओ।

---

## 🔴 Problem it Solves
Frontend and mobile candidates often:
- **Start coding components** or debating Redux vs Zustand before understanding requirements.
- Treat it like a **backend round** (databases and sharding) and miss client concerns.
- Forget **non-happy paths**: loading, empty, error, offline, slow network, permissions denied.
- Ignore **performance on real devices** (low-end Android, 3G), **accessibility** and **i18n** (Hindi/RTL).
- Skip **API design**: what the client needs, pagination, real-time updates, versioning for old app versions.
- Run out of time before showing depth.
A clear structure shows **product sense plus engineering depth**, the combination these rounds look for, especially at Meta, Uber, Airbnb, Flipkart, Swiggy, CRED and Razorpay.

## 🔴 यह क्यों बना? (Hindi)
Frontend/mobile उम्मीदवार अक्सर: ज़रूरतें समझे बिना components या Redux बनाम Zustand पर बहस शुरू; backend round जैसा जवाब (DB, sharding) और client की बातें छूट जाती हैं; loading, empty, error, offline, धीमा नेटवर्क, permission मना जैसी स्थितियाँ भूलना; सस्ते Android/3G पर performance, accessibility और हिंदी/RTL को नज़रअंदाज़ करना; API design छोड़ देना (client को क्या चाहिए, pagination, real-time, पुराने app versions); गहराई से पहले समय ख़त्म।
साफ़ ढाँचा product की समझ + engineering गहराई दिखाता है — Meta, Uber, Airbnb, Flipkart, Swiggy, CRED, Razorpay यही देखते हैं।

---

## 🟢 How it Works — Step by Step

### Time plan (45 min)

```
0–6    Requirements: functional flows, platforms, scale/data volume, performance & a11y targets, offline,
       real-time, SEO (web), devices/networks, i18n, out of scope
6–16   Architecture diagram: layers (UI → state/hooks → data/repository → network/realtime → storage),
       rendering strategy (web: CSR/SSR/ISR), navigation/routing, cross-cutting (auth, analytics, flags)
16–22  Data model & state: entities, normalization, server state vs UI state vs URL state vs persisted,
       local DB (mobile), cache policy
22–28  Interface: REST/GraphQL/BFF endpoints, pagination, real-time channel (SSE/WS/push), error format,
       versioning, component APIs if relevant
28–42  Deep dives (2–3): performance (virtualization, images, bundle/startup), network resilience
       (retry, offline queue), real-time correctness (ordering, dedupe), a11y, security, observability
42–45  Trade-offs, testing strategy, monitoring, what you'd do next
```

### Requirements checklist (say these out loud)

```
Web: browsers & devices, SEO needs, initial load budget (LCP < 2.5 s), INP, offline/PWA?, auth state
Mobile: iOS/Android/RN, min OS, offline read/write, background behaviour & push, device features
        (camera, location), low-end devices (2–3 GB RAM), app size, force-update policy
Both: data volume (1k vs 100k items), update frequency (real-time?), a11y level (WCAG AA / screen readers),
      languages (Hindi/Hinglish/RTL), analytics/experiments, security (XSS, token storage)
```

### Architecture you can draw for almost any prompt

```
┌──────────────────────── Client ─────────────────────────┐
│ Screens/Pages + Components (design system)             │
│      ▲ hooks/view-models                                 │
│ State: server-state cache (React Query/Apollo) | UI     │
│        store (Zustand) | URL state | forms               │
│ Data layer: API client (auth refresh, retry, cancel),   │
│   realtime client (WS/SSE), repository + local DB       │
│   (mobile: SQLite/MMKV), offline outbox                  │
│ Platform: router/navigation, push, deep links, perms,   │
│   background tasks, storage, i18n, analytics, errors    │
└─────────────────────────────────────────────────────────┘
   │ BFF/API Gateway (REST/GraphQL) │ WS/SSE │ CDN (images/video) │ FCM/APNs
```

### Deep-dive menu by prompt

```
News feed / Instagram: virtualization (FlashList/TanStack Virtual), image pipeline & placeholders,
  infinite scroll + cursor API, optimistic likes, video autoplay & preload, new-posts pill (F12, M12–M13)
Autocomplete: debounce, cancel stale requests, cache, combobox a11y, highlight safely (P06)
Chat (WhatsApp): local DB source of truth, outbox & receipts, WS reconnect/resume, ordering, push (P01, M06)
Video player: ABR, preload, captions, PiP, offline downloads, QoE metrics (P07)
E-commerce PDP/checkout: SSR/ISR + dynamic islands, LCP image, cart sync, idempotent place-order (P08)
Collaborative editor: OT/CRDT, presence, offline, comments anchoring (P05)
Ride tracking map: location streams, interpolation, battery, background (P03, M20)
Dashboard/table: big data grid virtualization, URL filters, live updates throttling (P10)
```

### Must-mention cross-cutting concerns (pick briefly)

```
UX states: skeletons, empty, error + retry, offline banner, optimistic updates with rollback
Performance budgets: bundle size/startup time, 60 fps lists, image sizes, memory on low-end phones
Accessibility: semantic elements/roles, keyboard & screen reader, focus management, contrast
i18n: translations, ₹/date formatting, RTL, longer strings
Security: XSS-safe rendering, token storage (HttpOnly cookie / Keychain), CSP, deep-link validation
Observability: crash/error reporting, RUM/Web Vitals, analytics events, feature flags
Testing: unit (logic), component (RTL), E2E (Playwright/Maestro/Detox), visual regression
Mobile-only: app lifecycle, background limits, push, OTA vs store releases, old-version compatibility
```

### Web vs mobile emphasis

```
Web: rendering strategy (SSR/ISR/RSC), SEO, bundle splitting, browser caching/service worker, CORS/CSRF
Mobile: offline-first & sync, startup time (Hermes), list/image memory, background tasks, push & deep links,
        secure storage, release/versioning, battery & data usage
```

## 🟢 कैसे काम करता है? (Hindi)
1. पहले 6 मिनट ज़रूरतें: मुख्य flows, platform (web/iOS/Android), डेटा कितना, real-time?, offline?, SEO (web), सस्ते फ़ोन/3G, performance लक्ष्य (LCP, 60 fps, startup), a11y, भाषाएँ, क्या scope से बाहर — बोलकर लिखो।
2. 10 मिनट architecture: UI → hooks → state (server-state cache, UI store, URL, forms) → data layer (API client — auth refresh, retry, cancel; WS/SSE; repository + local DB; offline outbox) → platform services (navigation, push, deep links, permissions, background, i18n, analytics); web में rendering तरीका (CSR/SSR/ISR); नीचे BFF, WS, CDN, FCM/APNs।
3. Data/state (entities, normalization, कौन-सा state कहाँ) और Interface (endpoints, cursor pagination, real-time channel, error format, versioning) — 12 मिनट।
4. 14 मिनट गहराई prompt के हिसाब से: feed → virtualization, images, infinite scroll, optimistic like; autocomplete → debounce, cancel, a11y; chat → local DB, outbox, receipts, reconnect; video → ABR, preload; checkout → SSR + islands, idempotent order; editor → OT/CRDT; ride map → location, interpolation, battery।
5. संक्षेप में cross-cutting: UX states, performance budgets, a11y, i18n (₹, हिंदी, RTL), security (XSS, token कहाँ), observability, testing; mobile में lifecycle, background, push, OTA बनाम store, पुराने versions; अंत में trade-offs, testing और आगे क्या।

---

## 🟡 Real World Example

**Meta "Front End System Design" and Uber/Airbnb mobile design rounds** — these companies run dedicated client-side design interviews (news feed, chat client, image loader library, offline-first apps) with rubrics on architecture, state management, performance, network handling and UX completeness.

**GreatFrontEnd / Frontend Interview Handbook** — popularized RADIO and worked examples (news feed, autocomplete, image carousel, video player), which many candidates and interviewers now use as a shared vocabulary.

**Indian companies** — Flipkart, Swiggy, Zomato, PhonePe, CRED and Razorpay ask client designs such as "Design Swiggy's restaurant menu page", "Design an offline-first delivery partner app", "Design a UPI payment screen flow" and "Design a dashboard table for 100k transactions", with strong emphasis on low-end devices, flaky networks and vernacular users.

## 🟡 Real Example Hindi में
Meta का "Front End System Design" और Uber/Airbnb के mobile rounds अलग से client design पूछते हैं — news feed, chat client, image loader library, offline-first ऐप — rubric: architecture, state, performance, नेटवर्क, UX की पूर्णता; GreatFrontEnd/Frontend Interview Handbook ने RADIO और उदाहरण लोकप्रिय किए।
Flipkart, Swiggy, Zomato, PhonePe, CRED, Razorpay — "Swiggy का menu page", "offline-first delivery partner ऐप", "UPI payment screen flow", "1 लाख transactions की table" — सस्ते फ़ोन, कमज़ोर नेटवर्क और vernacular यूज़र्स पर ज़ोर।

---

## 🟠 My Stack Example

### 45-minute script: "Design the Swiggy restaurant menu screen (React Native)"
```
[Req] "Show restaurant info, 200–400 dishes in categories with sticky headers, veg filter, search within menu,
 add/remove items with live cart total, item availability updates, works on 3G & ₹8k Android, a11y, Hindi."
[Arch] "Screen → hooks (useMenu via React Query, useCart via Zustand+MMKV) → API client (BFF /mobile/v1/menu)
 → image CDN. Realtime: availability changes via polling on focus (30 s) or SSE when restaurant is 'busy'."
[Data] "Menu normalized: categories[] → dishIds[]; dishes by id {name, pricePaise, veg, available, image:{template,w,h,blurhash}}.
 Cart local-first (MMKV) + server repricing on checkout."
[API] "GET /mobile/v1/restaurants/{id}/menu (ETag, cache 60 s) → sections; POST /cart/ops {op, dishId} idempotent."
[Deep 1] "List perf: FlashList with getItemType header/dish, stickyHeaderIndices, memoized rows with per-dish selector,
 sized images via expo-image + recyclingKey; JS/UI fps checks on low-end device."
[Deep 2] "Availability correctness: menu cache short TTL + server validation at checkout; unavailable → disable button."
[Deep 3] "Accessibility & i18n: labels like 'Add Paneer Tikka, 249 rupees', Hindi strings via i18next, ₹ formatting."
[Wrap] "Trade-offs: polling vs SSE; monitoring: screen load time, frozen frames, add-to-cart errors; tests: RNTL + Maestro."
```

### Diagram labels that impress
```
Annotate arrows: "cursor pagination", "ETag 304", "SSE /orders/:id/events", "optimistic update + rollback",
"image ?w=360&fm=webp via CDN", "outbox (SQLite) → retry with Idempotency-Key"
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you structure a frontend system design answer?**
A1: Clarify requirements first (flows, platforms, data scale, real-time, offline, SEO, devices and networks, performance and accessibility targets, languages). Draw a layered client architecture (UI, state and hooks, data and network layer, storage, platform services) and choose a rendering strategy for web. Define the data model and state categories, then the API contract (pagination, real-time, errors, versioning). Spend most time on two or three deep dives relevant to the prompt (performance, network resilience, real-time correctness, accessibility, security), and close with trade-offs, testing and monitoring.

**Q2: What do interviewers look for that's specific to frontend and mobile rounds?**
A2: Sound state ownership and data flow, API design driven by UI needs, attention to all UX states (loading, empty, error, offline, optimistic), performance on realistic devices and networks (virtualization, images, bundle size, startup), accessibility and i18n, security in the client (XSS, token storage), and for mobile: lifecycle, background limits, push, offline sync and release realities (old versions, OTA). They also want trade-off reasoning, not just library names.

**Q3: How much backend should you include?**
A3: Enough to define the client contract and data sources: a BFF or API shape, real-time channel (SSE, WebSocket or push), CDN for media, auth flow and key backend constraints (pagination, consistency). Avoid deep backend scaling discussions unless asked. The interviewer wants client-side depth, so mention backend choices briefly and move on.

**Q4: How do you show depth in performance?**
A4: Quantify budgets (LCP under 2.5 s, INP under 200 ms, cold start under 2 s, 60 fps lists) and map them to techniques. For web: rendering strategy, code splitting, image optimization and caching. For mobile: Hermes, lazy init, FlashList recycling, sized images, UI-thread animations. Also cover measurement (Web Vitals RUM, profilers, Perf Monitor on low-end devices) and regression prevention (budgets in CI). Concrete numbers and tools signal real experience.

**Q5: What are common mistakes in these rounds?**
A5: Jumping into component code or library debates, ignoring requirements and constraints, designing only the happy path, forgetting accessibility, i18n and security, skipping API and pagination design, treating mobile like web (no lifecycle, offline or old-version thinking), over-engineering (micro-frontends for a small app), and not managing time. Fix these by following the framework, narrating trade-offs and asking the interviewer which deep dive they prefer.

---

## 🔷 Trade-offs
✅ Structured RADIO/mobile frameworks: complete & calm — ❌ adapt depth to prompt; skip irrelevant parts quickly.
✅ Naming libraries (React Query, FlashList): shows practicality — ❌ always explain the underlying concept.
✅ Covering many cross-cutting concerns briefly: breadth — ❌ still go deep on 2–3 areas.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RADIO | Frontend design framework | frontend design का ढाँचा |
| Client architecture | Layers of the app | ऐप की परतें |
| Server state | Cached backend data | backend डेटा की cache |
| UX states | Loading/empty/error/offline | स्क्रीन की स्थितियाँ |
| Rendering strategy | CSR/SSR/SSG/ISR choice | page बनाने का तरीका |
| Virtualization | Render visible items only | सिर्फ़ दिखने वाले items |
| Offline-first | Local DB as source of truth | पहले local |
| BFF | Backend for frontend | frontend का backend |
| Performance budget | Max size/time targets | performance की सीमा |
| Old-version compatibility | Supporting shipped apps | पुराने ऐप चलते रहें |

---

## ⚡ 3-Line Summary
**English:**
1. Web: RADIO; mobile: requirements → app layers + platform services → local data → API/sync → deep dives.
2. Draw a layered client architecture, define state ownership and the API contract, and cover non-happy paths.
3. Go deep on 2–3 prompt-specific areas (performance, offline/real-time, a11y, security) with numbers and trade-offs; keep backend brief.

**Hindi:**
1. Web: RADIO; mobile: ज़रूरतें → परतें + platform services → local डेटा → API/sync → गहराई।
2. परतों वाला client ढाँचा, state का मालिक, API contract, और सब स्थितियाँ (loading, error, offline)।
3. Prompt के हिसाब से 2–3 गहराइयाँ numbers और trade-offs के साथ; backend संक्षेप में।

---

## ➡️ Next Topic Suggestion
**03. Back-of-the-Envelope Estimation** — Both rounds benefit from quick numbers. Next: a repeatable method for estimating QPS, storage, bandwidth, cache and server counts in minutes.
