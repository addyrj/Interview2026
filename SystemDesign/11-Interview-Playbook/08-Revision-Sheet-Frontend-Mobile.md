# 08. Revision Sheet — Frontend + Mobile
# हिंदी में: Frontend + Mobile की Revision Sheet — RADIO, browser rendering, CSR/SSR/SSG/ISR, Server Components, Web Vitals, bundling, browser caching, service workers, state और React Query, API layer, pagination/virtualization, real-time, XSS/CSRF/CSP, CORS, token storage, images, a11y, i18n, design systems, micro-frontends, observability; और React Native architecture, Hermes, lifecycle, storage, offline sync, conflicts, networking, mobile APIs, push, deep links, lists, performance, security, auth, OTA, releases, CI/CD, location, uploads, crash reporting (F01–F22, M01–M22)

---

## 🔵 Simple Definition (English)
A **compact refresher** for `07-Frontend-System-Design/` (F01–F22) and `08-Mobile-System-Design/` (M01–M22): the one-line essence, the key numbers and techniques, and the interview trap for each topic. Read it before frontend or mobile rounds, or full-stack designs where client depth matters.

## 🔵 सरल परिभाषा (Hindi)
`07-Frontend-System-Design/` (F01–F22) और `08-Mobile-System-Design/` (M01–M22) की संक्षिप्त दोहराई — हर topic का सार, ज़रूरी numbers/तकनीकें और इंटरव्यू का जाल; frontend/mobile rounds या client की गहराई वाले full-stack designs से पहले पढ़ो।

---

## 🔴 Problem it Solves
Client-side rounds probe many small but specific concepts: Web Vitals thresholds, why hydration hurts INP, where to store tokens, FlatList vs FlashList, OTA limits, background execution rules, push token lifecycle. Quick recall prevents vague answers like "use React Query" without explaining **staleTime, invalidation or optimistic rollback**.

## 🔴 यह क्यों बना? (Hindi)
Client rounds कई छोटे पर ख़ास concepts पूछते हैं — Web Vitals की सीमाएँ, hydration से INP क्यों बिगड़ता है, tokens कहाँ रखें, FlatList बनाम FlashList, OTA की सीमा, background के नियम, push token का जीवन; जल्दी याद रहे तो "React Query लगाओ" जैसे धुंधले जवाब की जगह staleTime, invalidation, optimistic rollback समझा सकोगे।

---

## 🟢 How it Works — Step by Step (the cheat sheet)

### Web: rendering & performance (F01–F08)

```
F01 RADIO: Requirements → Architecture → Data model → Interface → Optimizations (time-box ~45 min)
F02 Critical rendering path: HTML→DOM, CSS→CSSOM (render-blocking), JS (parser-blocking unless defer/async)
    → layout → paint → composite; animate transform/opacity; avoid layout thrashing; long tasks > 50 ms hurt INP
F03 Rendering: CSR (SPA, login apps), SSR (per request, SEO, personalized), SSG (build time, fastest), ISR
    (static + background/on-demand revalidation); hydration cost; choose per route
F04 React Server Components: server-only components (0 KB JS), 'use client' islands at leaves, serializable
    props, Suspense streaming, Server Actions (public endpoints → auth + validate)
F05 Core Web Vitals (p75 field): LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1; lab (Lighthouse/TBT) vs field (CrUX/RUM)
F06 Bundling: tree shaking (ESM), route & component code splitting, lazy + prefetch, budgets in CI,
    hashed filenames; handle ChunkLoadError after deploy
F07 HTTP caching: hashed assets max-age=1y immutable; HTML no-cache + ETag; private for personalized;
    no-store for sensitive; stale-while-revalidate; versioned URLs instead of CDN invalidation
F08 Service workers/PWA: install (precache) → activate (cleanup) → fetch strategies (cache-first static,
    network-first HTML/data, SWR semi-static, network-only payments); background sync outbox; update prompt
```

### Web: data, state, real-time (F09–F13)

```
F09 State types: server (React Query/SWR/Apollo), URL (filters), form, local, global client (Context for
    rarely-changing; Zustand/Redux with selectors), persisted; derive don't duplicate; normalize entities
F10 React Query: query keys = identity; staleTime (fresh) vs gcTime (unused retention); refetch on focus/
    reconnect; dedupe; AbortSignal; optimistic updates (snapshot → set → rollback → invalidate); infinite queries
F11 API layer: REST vs GraphQL vs BFF; one http client (auth refresh single-flight, timeouts, safe retries,
    normalized errors, request IDs, types via OpenAPI codegen); screen-shaped BFF for mobile
F12 Lists: pagination (SEO/tables) vs infinite scroll (feeds) vs load more; cursor API; IntersectionObserver
    sentinel; virtualization (TanStack Virtual) for long lists; scroll restoration; role="feed"
F13 Real-time: polling (rare/CDN-cacheable), SSE (server→client, auto-reconnect, LLM streaming), WebSocket
    (two-way); heartbeats, backoff+jitter reconnect, resume via last seq, dedupe; write events into query cache
```

### Web: security & quality (F14–F22)

```
F14 Security: XSS (React escapes; sanitize HTML with DOMPurify; validate URLs; strict nonce CSP; Trusted Types),
    CSRF (SameSite cookies, CSRF tokens, Origin checks), clickjacking (frame-ancestors), SRI, no secrets in bundles
F15 CORS: browser-enforced; preflight OPTIONS for non-simple requests; exact origin + Allow-Credentials with
    cookies; Vary: Origin; same-origin proxy avoids CORS; CORS ≠ API security
F16 Frontend auth: access token in memory + refresh in HttpOnly Secure SameSite cookie (rotation, reuse
    detection) or BFF sessions; silent refresh; single-flight; server-side route protection; multi-tab sync
F17 Images: AVIF/WebP, srcset/sizes, LCP image priority (never lazy), lazy below fold, dimensions/aspect-ratio
    (no CLS), blurhash placeholders, image CDN; fonts WOFF2 subset + swap
F18 a11y: semantic HTML, names/labels, keyboard + visible focus, focus management (dialogs, route change),
    contrast 4.5:1, aria-live, reduced motion; test with axe + screen readers
F19 i18n: message catalogs + ICU plurals; Intl for ₹/dates (en-IN lakh grouping); locale routing + hreflang;
    RTL logical CSS; lazy-load catalogs; localized backend content; transliteration in search
F20 Design systems: tokens (global → semantic → component), accessible components, Storybook, visual tests,
    semver + codemods; share tokens across web & RN
F21 Micro-frontends (route split, Module Federation) only at multi-team scale; monorepos (Turborepo/Nx) for
    shared code with affected builds & remote cache
F22 Observability: Sentry + source maps, RUM/Web Vitals, traces; feature flags (gradual rollout, kill switch,
    deterministic bucketing, server-side eval); A/B tests (power, SRM, guardrails)
```

### Mobile: platform & architecture (M01–M05)

```
M01 Framework: requirements (offline, background, devices, releases) → layers + platform services → local data
    → API/sync contract → deep dives; local DB as source of truth; old versions in the wild
M02 React Native: JS (Hermes) → renderer → native views; old Bridge (async JSON) vs New Architecture (JSI direct
    calls, Fabric renderer, TurboModules lazy & typed via Codegen, bridgeless); keep JS thread free
M03 Startup: Hermes bytecode; cold vs warm vs hot start; inline requires, lazy screens/SDKs, MMKV boot data,
    cached first screen, splash until meaningful content; measure release builds on low-end Android
M04 Lifecycle: iOS active/background/suspended; Android process death; background URLSession / WorkManager for
    transfers; BGTask/periodic best-effort; foreground services for tracking; OEM battery killers in India
M05 Storage: Keychain/Keystore (secrets), MMKV (fast KV), SQLite/WatermelonDB (structured, migrations, FTS),
    files (media); encrypt sensitive data; wipe on logout; versioned migrations across version jumps
```

### Mobile: data & network (M06–M11)

```
M06 Offline-first: read from local DB; write locally + outbox in one transaction; sync engine (ordered push with
    idempotency + backoff, delta pull with cursors + tombstones); sync states in UI; payments/OTP online-only
M07 Conflicts: detect via server versions/If-Match (not device clocks); resolve per data type: field LWW,
    server-authoritative rules (terminal states), 3-way merge, operations (qty += 1), CRDT/OT, user choice
M08 Networking: timeouts; retries only safe/idempotent + retryable errors (backoff + jitter); batching (radio
    tail energy); dedupe; compression; HTTP/2–3 (QUIC connection migration); network-aware quality
M09 Mobile APIs: screen-shaped BFF, minimal fields, paise integers, UTC ISO dates; additive changes only,
    tolerant readers (unknown enums/widgets), versioning, X-App-Version, soft/force update (426), SDUI
M10 Push: token from APNs/FCM → backend; alert vs data/silent (throttled); channels, collapse keys, TTL; token
    refresh/prune/logout detach; quiet hours & caps; push is best-effort (not source of truth)
M11 Deep links: Universal/App Links (https + .well-known files) > custom schemes; deferred links for installs;
    validate params; auth-gated pending destination; UPI intents verified server-side
```

### Mobile: performance, security, releases (M12–M22)

```
M12 Images: bitmap = w×h×4 bytes → request CDN sizes + decode at view size; memory LRU (bytes) + disk cache;
    dedupe, prioritize, cancel off-screen; recyclingKey; blurhash; expo-image (Glide/SDWebImage)
M13 Lists: FlatList virtualizes (mount/unmount) vs FlashList recycles cells by type (fastest on low-end);
    memoized rows, per-row selectors, getItemType, no stale state in recycled cells, inverted chat lists
M14 Performance: JS fps vs UI fps; selectors/memo/React Compiler; Reanimated worklets on UI thread;
    InteractionManager after transitions; native-stack + freeze; cleanup subscriptions; strip console in release
M15 Security: no secrets in app; Keychain/Keystore; HTTPS-only + SPKI pinning with backup pins (high-risk apps);
    root/jailbreak as signal + Play Integrity/App Attest server-verified; R8; FLAG_SECURE; device binding
M16 Auth: OTP (SMS Retriever, abuse controls), Google/Apple sign-in verified server-side, OAuth via system
    browser + PKCE; refresh in Keychain with rotation; device-bound keys; biometrics unlock local secrets
M17 OTA: JS/assets only; runtime version (fingerprint) compatibility; channels, staged %, signing, rollback;
    CodePush (App Center) retired Mar 2025 → EAS Update/self-hosted
M18 Releases: version name + build number; release trains + flags; Play staged rollout / iOS phased release;
    halt + hotfix/OTA; soft/force update via remote config + Play In-App Updates
M19 CI/CD: PR checks + fingerprint → OTA preview vs native build; EAS Build/Fastlane; signing (Play App Signing,
    match/managed credentials); Maestro/Detox E2E; device farms for budget phones
M20 Location: adaptive accuracy/frequency by trip state, geofences, batching, foreground service; permissions
    (foreground first, background only if essential); interpolate markers; mock-location detection; Indian addresses
M21 Uploads: compress on device; presigned direct-to-S3; multipart (≥5 MB parts) or tus; persist part ETags;
    resume after kill; background transfers; idempotent complete; async processing; lifecycle cleanup
M22 Crash & analytics: JS/native crashes, ANRs, hangs; symbolication (source maps, dSYMs, R8 maps); crash-free
    users ≥ 99.5%+; typed tracking plan, batched events, no PII, consent (DPDP/ATT)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Web rendering: CRP (CSS paint रोकती, script parsing रोकती — defer), CSR/SSR/SSG/ISR हर route के हिसाब से, RSC (0 KB JS, 'use client' पत्तियों पर), Web Vitals (LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1, p75), code splitting + prefetch, HTTP caching (hash वाली files 1 साल, HTML no-cache), service worker strategies।
2. Web data/state: state के प्रकार (server, URL, form, local, global), React Query (keys, staleTime, optimistic + rollback), एक http client (single-flight refresh, safe retry), cursor + virtualization, real-time (polling/SSE/WebSocket, reconnect, resume)।
3. Web सुरक्षा/गुणवत्ता: XSS (escape, DOMPurify, CSP), CSRF (SameSite, tokens), CORS (preflight, exact origin), tokens (memory + HttpOnly refresh), images (LCP priority, srcset, blurhash), a11y, i18n (₹, हिंदी, RTL), design system, micro-frontends सिर्फ़ बड़ी टीमों में, Sentry + flags + A/B।
4. Mobile platform/data: RN New Architecture (JSI, Fabric, TurboModules), Hermes startup, lifecycle और background नियम (WorkManager, URLSession, foreground service, OEM killers), storage (Keychain, MMKV, SQLite), offline-first (local DB + outbox + sync), conflicts (versions, नियम, operations, CRDT), networking (timeout, safe retry, batching, QUIC), mobile APIs (additive, tolerant, force update), push (tokens, channels, best-effort), deep links (Universal/App Links)।
5. Mobile performance/सुरक्षा/release: images (w×h×4 memory, सही आकार में decode), FlashList recycling, JS बनाम UI thread, security (कोई secret नहीं, pinning, Play Integrity/App Attest), auth (OTP, PKCE, device binding, biometric), OTA (सिर्फ़ JS, fingerprint), staged rollout + force update, CI/CD, location (adaptive), resumable uploads, crash-free % और typed analytics।

---

## 🟡 Real World Example
- **Flipkart Lite / Twitter Lite / Pinterest** (PWAs: code splitting, service workers) were the early proof that web performance drives engagement in India.
- **Shopify FlashList, Meta Hermes and the New Architecture** pushed RN performance on low-end Android.
- **WhatsApp offline-first, Swiggy/Zomato live tracking and Indian UPI intent flows** recur constantly as design prompts.

## 🟡 Real Example Hindi में
- Flipkart Lite, Twitter Lite, Pinterest (PWAs — code splitting, service workers) ने भारत में साबित किया कि web performance से engagement बढ़ता है।
- Shopify के FlashList, Meta के Hermes और New Architecture ने सस्ते Android पर RN तेज़ किया।
- WhatsApp का offline-first, Swiggy/Zomato की live tracking और UPI intents बार-बार design सवालों में आते हैं।

---

## 🟠 My Stack Example

### Numbers to quote
```
Web: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 (p75); initial JS ≲ 150–200 KB gz; long task > 50 ms
Mobile: cold start p90 < 2–2.5 s on mid/low-end; 60 fps (16.7 ms/frame); crash-free users ≥ 99.5–99.8%;
        Play bad-behaviour thresholds ~1.09% crashes / ~0.47% ANRs; S3 multipart part ≥ 5 MB
```

---

## ⚫ Interview Questions + Answers (rapid fire)

**Q1: How would you improve a slow product page on mobile web?**
A1: Measure with field RUM and Lighthouse first. For LCP, serve SSR or ISR HTML from a CDN, preload a correctly sized AVIF/WebP hero image with high fetch priority, inline critical CSS and defer JS. For INP, reduce JS and hydration (RSC, code splitting), break long tasks and audit third-party scripts. For CLS, reserve space for images, ads and fonts. Then cache hashed assets for a year, prefetch likely next routes, and add bundle and Web Vitals budgets in CI.

**Q2: Where do you store auth tokens on web and on mobile?**
A2: On web, keep the short-lived access token in memory and the refresh token in an HttpOnly, Secure, SameSite cookie with rotation, or use BFF server sessions so no tokens reach JS, with CSRF protections on cookie-authenticated endpoints. On mobile, store the refresh token in the Keychain or Keystore (optionally biometric-gated) and the access token in memory, with single-flight refresh and device-bound keys for sensitive apps. Never use localStorage or AsyncStorage for long-lived secrets.

**Q3: How do you design an offline-first mobile feature?**
A3: Make the local database (SQLite or WatermelonDB) the UI's source of truth. Writes update local rows and append to an outbox in one transaction, and a sync engine pushes outbox items in order with idempotency keys and backoff, then pulls server deltas with cursors and tombstones. Resolve conflicts with server versions and domain rules, show pending, synced and failed states, trigger sync on foreground, connectivity and background tasks, and keep payments and OTP online-only.

**Q4: FlatList vs FlashList?**
A4: Both avoid rendering entire lists. FlatList virtualizes by mounting items near the viewport and unmounting distant ones, which creates JS work and blank areas on slow devices. FlashList recycles mounted cells per item type, re-rendering them with new data like RecyclerView, so it's much faster on low-end Android. It needs care with local state in cells and item types for heterogeneous lists. In both, use memoized rows, stable keys, sized images and per-row state selectors.

**Q5: What can and can't OTA updates fix?**
A5: OTA (EAS Update) replaces the JavaScript bundle and assets for binaries with a matching runtime version (fingerprint): JS bug fixes, UI changes and logic tweaks within store policy. It can't change native code or dependencies, RN or Expo SDK versions, permissions, entitlements, icons or native config. Those require a store release. Roll OTA out gradually with signing, monitoring by update ID and a rollback path.

---

## 🔷 Trade-offs
✅ Knowing thresholds & tools: concrete answers — ❌ always tie them to the user problem in the prompt.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hydration | Attach JS to server HTML | HTML में JS जोड़ना |
| ISR | Background static regeneration | पीछे से static बनाना |
| INP | Interaction responsiveness | tap का जवाब |
| staleTime | Freshness window for cached data | ताज़गी की अवधि |
| CSP | Allowed script sources policy | script स्रोत नीति |
| JSI / Fabric | RN direct calls / renderer | RN सीधा रास्ता / renderer |
| Outbox | Pending local writes queue | भेजने की कतार |
| Universal/App Links | Verified https deep links | verified deep links |
| Recycling (FlashList) | Reuse cells | cells दोबारा इस्तेमाल |
| Runtime version | OTA compatibility key | OTA की संगतता |

---

## ⚡ 3-Line Summary
**English:**
1. Web: per-route rendering (CSR/SSR/ISR/RSC), Web Vitals budgets, splitting + caching, React Query state, safe API layer, virtualization, SSE/WS, XSS/CSRF/CORS, tokens, images, a11y, i18n, observability.
2. Mobile: RN New Architecture + Hermes, lifecycle/background rules, secure & fast storage, offline-first sync + conflicts, resilient networking, compatible APIs, push, deep links.
3. Mobile performance/security/releases: images & lists (FlashList), threads, pinning/attestation, OTP/biometric auth, OTA vs store, staged rollouts, CI/CD, location, resumable uploads, crash-free metrics.

**Hindi:**
1. Web: route के हिसाब से rendering, Web Vitals, splitting + caching, React Query, सुरक्षित API, virtualization, real-time, सुरक्षा, a11y, i18n।
2. Mobile: New Architecture + Hermes, background नियम, storage, offline sync + conflicts, networking, compatible APIs, push, deep links।
3. Performance/सुरक्षा/release: images और FlashList, threads, pinning, OTP/biometric, OTA बनाम store, staged rollout, uploads, crash-free।

---

## ➡️ Next Topic Suggestion
**09. Revision Sheet — AI Engineering** — Next: the AI refresher covering LLM basics, prompting, structured output, embeddings and vector DBs, RAG with hybrid search and reranking, tools and agents, memory, evals, observability, caching, guardrails, fine-tuning, scale, hallucinations, cost, streaming and deployment (Topics 127–155).
