# F21. Micro-Frontends + Monorepo
# हिंदी में: Micro-Frontends — एक बड़े frontend को टीमों के हिसाब से छोटे, अलग-अलग deploy होने वाले हिस्सों में बाँटना (जैसे backend में microservices); Monorepo — कई apps और packages को एक ही Git repo में रखना ताकि code साझा करना और एक साथ बदलना आसान हो

---

## 🔵 Simple Definition (English)
- **Micro-frontends (MFE)**: split a large web app into **independently developed and deployed frontend pieces owned by different teams** (e.g., Search, Product page, Cart/Checkout, Account), composed into one product for the user. Composition options: **route-level split** (different apps per path behind a proxy), **build-time packages**, **runtime composition** (Webpack/Rspack **Module Federation**, import maps / single-spa), **iframes**, or **server-side composition** (edge includes, Next.js Multi-Zones).
- **Monorepo**: a **single repository containing many apps and libraries** (web app, React Native app, admin panel, BFF, design system, shared types) with tooling for **task orchestration, caching and dependency graphs**: **Turborepo**, **Nx**, pnpm/Yarn workspaces.
They solve different problems. A monorepo is about **code organization and sharing**. Micro-frontends are about **runtime/deploy independence and team autonomy**. You can use either, both or neither.

## 🔵 सरल परिभाषा (Hindi)
Micro-frontends = बड़े web app को टीमों के हिसाब से हिस्सों में बाँटना (Search, Product, Cart, Account), हर हिस्सा अलग बने और अलग deploy हो, पर यूज़र को एक ही ऐप दिखे — route से बाँटकर, Module Federation से runtime पर जोड़कर, iframe या server पर जोड़कर।
Monorepo = कई apps और libraries (web, React Native, admin, BFF, design system, shared types) एक ही Git repo में, Turborepo/Nx जैसे tools के साथ। Monorepo code साझा करने के लिए है, micro-frontends अलग deploy और टीम की आज़ादी के लिए।

---

## 🔴 Problem it Solves
Big companies with 10–50 frontend teams on one app hit:
- **Deployment coupling**: one team's bug blocks everyone's release, and release trains slow down.
- **Ownership confusion**: a giant codebase where nobody owns the checkout folder.
- **Build times** of 20+ minutes, and merge conflicts.
- **Tech migration** is all-or-nothing (Angular → React needs a big-bang rewrite).

Micro-frontends give **team autonomy, independent deploys and incremental migration**.

Separately, many repos (polyrepo) cause:
- **Version drift** of shared libraries and duplicated config.
- Painful cross-repo changes (an API type change touches 5 repos and 5 PRs).

A **monorepo** gives **atomic changes, shared code and tooling, and a single source of truth**, with smart caching so CI stays fast.

## 🔴 यह क्यों बना? (Hindi)
10–50 frontend टीमों वाले एक ऐप में: एक टीम का bug सबकी release रोकता है, कोई folder किसका है पता नहीं, 20+ मिनट का build, merge conflicts, और पुरानी tech से नई पर जाना एक बार में पूरा rewrite। Micro-frontends टीम को आज़ादी, अलग deploy और धीरे-धीरे migration देते हैं।
दूसरी तरफ़ बहुत सारे repos में shared libraries के versions बिखर जाते हैं, एक API type बदलने पर 5 repos में 5 PRs। Monorepo एक साथ बदलाव, साझा code/tooling और caching से तेज़ CI देता है।

---

## 🟢 How it Works — Step by Step

### Micro-frontend composition options

```
1) Route-level (simplest, most common ✅)
   CDN / reverse proxy / Next.js Multi-Zones
     /            → home app (Team Discovery)
     /search/*    → search app (Team Search)
     /p/*         → product app (Team Catalog)
     /checkout/*  → checkout app (Team Payments)
   Each is a separate deploy; navigation between them is a full page load (or soft with shared shell)

2) Runtime composition — Module Federation
   Host (shell) app loads remote modules at runtime:
     shell ──loads──► https://cart.cdn.com/remoteEntry.js → exposes "./MiniCart"
   Shared singletons (react, react-dom, design system) negotiated to avoid duplicates
   + independent deploys of widgets; − version contracts, runtime failures, complexity

3) Build-time integration (npm packages)
   Teams publish packages; shell installs versions → simple, but deploys are coupled (rebuild shell)

4) iframes
   Strong isolation (security, legacy apps, third-party widgets) — clunky UX, a11y, routing, perf

5) Server/edge composition
   Edge-side includes / server fragments assembled per request (Zalando "Project Mosaic", IKEA)
```

### Cross-cutting concerns you must solve

```
- Shared shell: header, auth session, navigation, analytics, error boundaries, feature flags
- Design system: shared tokens/components (F20) → consistent look; version alignment
- Communication: URL/query params, custom browser events, or a tiny shared event bus — avoid shared global stores
- Auth: same-origin cookies/session shared across apps (route-level under one domain)
- Performance: avoid shipping React 3 times; shared deps; budget per MFE; prefetch next MFE
- Contracts: TS types for exposed modules; contract tests; graceful fallback if a remote fails to load
- Observability: tag errors/RUM with the owning MFE/team
```

### Monorepo structure (Turborepo + pnpm)

```
quickbite/
  apps/
    web/            (Next.js customer site)
    mobile/         (Expo React Native app)
    partner/        (restaurant panel, Vite + React)
    admin/          (internal tools)
    bff/            (Node/Express BFF)  ·  api/ (FastAPI — Python lives here too, or separate)
  packages/
    ui-web/  ui-native/  tokens/  icons/
    api-client/     (typed client generated from OpenAPI)
    config/         (eslint, tsconfig, prettier presets)
    utils/          (formatting ₹, dates, validation schemas — zod shared by web, RN, BFF)
  turbo.json  pnpm-workspace.yaml
Task graph: build packages before apps; only rebuild/test what changed (affected); remote cache → CI skips
           unchanged work ("cache hit") → minutes instead of an hour
CODEOWNERS: /apps/partner @team-partner, /packages/ui-* @team-design-system
```

### When (not) to use micro-frontends

```
Use when: many teams (5+) on one product surface, need independent release cadence, distinct domains,
          incremental migration from legacy (strangler pattern), acquisitions with different stacks
Avoid when: small team, one product, performance-critical consumer app where bundle duplication hurts,
            no platform team to own the shell/tooling — a well-modularized monolith (+ monorepo) is better
"Modular monolith first": clear module boundaries + ownership in one deployable app
```

## 🟢 कैसे काम करता है? (Hindi)
1. सबसे आसान micro-frontend: route से बाँटो — `/search` एक टीम का ऐप, `/checkout` दूसरी का; proxy/CDN या Next.js Multi-Zones से जोड़ो; हर एक अलग deploy।
2. Module Federation: shell ऐप runtime पर दूसरी टीम का component (जैसे MiniCart) लोड करता है; react और design system एक ही बार shared — पर version contract और लोड fail होने का ध्यान।
3. साझा चीज़ें: shell (header, auth, analytics), design system, आपसी बात URL या browser events से (shared global store नहीं), एक domain पर cookies, React तीन बार न आए, हर टीम की errors अलग tag।
4. Monorepo: `apps/` (web, mobile, partner, admin, bff) और `packages/` (ui, tokens, api-client, utils, config); Turborepo/Nx task graph से सिर्फ़ बदला हुआ build/test, remote cache से CI तेज़; CODEOWNERS से मालिकाना।
5. छोटी टीम या एक product हो तो micro-frontends मत लाओ — modular monolith + monorepo काफ़ी; 5+ टीमें, अलग release, पुराने ऐप से धीरे migration हो तब MFE।

---

## 🟡 Real World Example

**IKEA, Zalando, Spotify (desktop), DAZN** — well-known micro-frontend adopters. Zalando composed pages from team-owned fragments on the server (Project Mosaic, later its "Interface Framework"). Spotify's desktop app historically used iframes per feature team, later consolidated for performance and consistency. This shows the cost.

**Module Federation** — introduced in Webpack 5 (2020) and now also in Rspack and Vite plugins. Used by large enterprises to load team-owned widgets into a shell at runtime.

**Google, Meta, Uber (monorepos)** — Google's single monorepo (billions of lines) with Bazel. Uber moved to monorepos for Go and other languages. Vercel's Turborepo and Nx brought monorepo tooling to JS teams.

**Indian scale-ups** — many (e.g., teams at Razorpay, Swiggy) use JS monorepos to share design systems, typed API clients and configs across web, RN and dashboard apps. Route-level splits are common for large dashboards owned by different teams.

## 🟡 Real Example Hindi में
IKEA, Zalando, DAZN micro-frontends के मशहूर उदाहरण — Zalando ने server पर टीमों के fragments जोड़कर pages बनाए; Spotify desktop में पहले हर टीम का iframe था, बाद में performance के लिए एक किया (क़ीमत दिखाता है)।
Google का एक विशाल monorepo (Bazel), Uber भी monorepo पर गया; भारत की कई कंपनियाँ (जैसे Razorpay, Swiggy की टीमें) JS monorepo से web, RN और dashboards में design system और typed API client साझा करती हैं।

---

## 🟠 My Stack Example

### Turborepo config
```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": { "dependsOn": ["^build"], "outputs": ["dist/**", ".next/**", "!.next/cache/**"] },
    "test":  { "dependsOn": ["^build"], "outputs": ["coverage/**"] },
    "lint":  {},
    "dev":   { "cache": false, "persistent": true }
  }
}
```
```yaml
# pnpm-workspace.yaml
packages: ["apps/*", "packages/*"]
```
```yaml
# .github/workflows/ci.yml — only affected packages, remote cache
- run: pnpm install --frozen-lockfile
- run: pnpm turbo run lint test build --filter="...[origin/main]"     # changed + dependents only
  env: { TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}, TURBO_TEAM: quickbite }
```

### Shared validation schema used by web, React Native and the Node BFF
```ts
// packages/utils/src/schemas.ts
import { z } from 'zod';
export const AddressSchema = z.object({
  line1: z.string().min(3), city: z.string(), pincode: z.string().regex(/^[1-9][0-9]{5}$/, 'Invalid PIN code'),
  phone: z.string().regex(/^[6-9]\d{9}$/, 'Invalid mobile number'),
});
export type Address = z.infer<typeof AddressSchema>;
// apps/web form, apps/mobile form, apps/bff route all import { AddressSchema } from '@quickbite/utils'
```

### Route-level micro-frontends with Next.js Multi-Zones
```js
// apps/web/next.config.js (main zone)
module.exports = {
  async rewrites() {
    return [
      { source: '/partner', destination: `${process.env.PARTNER_URL}/partner` },
      { source: '/partner/:path*', destination: `${process.env.PARTNER_URL}/partner/:path*` },
    ];
  },
};
// apps/partner/next.config.js: basePath: '/partner'  → separately deployed by Team Partner
```

### Runtime composition with Module Federation (Rspack/Webpack)
```js
// cart app (remote) — rspack.config.js
new ModuleFederationPlugin({
  name: 'cart', filename: 'remoteEntry.js',
  exposes: { './MiniCart': './src/MiniCart.tsx' },
  shared: { react: { singleton: true, requiredVersion: '^19.0.0' }, 'react-dom': { singleton: true }, '@quickbite/ui-web': { singleton: true } },
});
// shell (host)
new ModuleFederationPlugin({
  name: 'shell',
  remotes: { cart: 'cart@https://cart.cdn.quickbite.in/remoteEntry.js' },
  shared: { react: { singleton: true }, 'react-dom': { singleton: true }, '@quickbite/ui-web': { singleton: true } },
});
```
```tsx
// shell: lazy-load remote with a fallback if it fails
const MiniCart = lazy(() => import('cart/MiniCart').catch(() => ({ default: () => <a href="/cart">Cart</a> })));
<ErrorBoundary fallback={<a href="/cart">Cart</a>}><Suspense fallback={<CartSkeleton />}><MiniCart /></Suspense></ErrorBoundary>
```

### Cross-MFE communication via browser events (no shared store)
```ts
// cart MFE publishes
window.dispatchEvent(new CustomEvent('cart:updated', { detail: { count: 3 } }));
// header (shell) listens
useEffect(() => { const h = (e: Event) => setCount((e as CustomEvent).detail.count); window.addEventListener('cart:updated', h); return () => window.removeEventListener('cart:updated', h); }, []);
```

### CODEOWNERS for ownership
```
/apps/partner/        @quickbite/team-partner
/apps/mobile/         @quickbite/team-mobile
/packages/ui-web/     @quickbite/design-system
/packages/api-client/ @quickbite/platform
```

---

## ⚫ Interview Questions + Answers

**Q1: What are micro-frontends and when would you use them?**
A1: Micro-frontends split a frontend into independently built and deployed parts owned by different teams, composed into one experience via route-level splits, runtime composition (Module Federation, single-spa), build-time packages, iframes or server/edge composition. Use them when many teams work on a large product and need autonomy and independent releases, when domains are clearly separable, or for incremental migration from a legacy app. Avoid them for small teams or performance-sensitive apps where a modular monolith is simpler and faster.

**Q2: What are the main challenges of micro-frontends?**
A2: Duplicate dependencies and bigger bundles (multiple React copies) if sharing isn't configured. Inconsistent UX without a shared design system. Cross-app communication and shared state. Auth and session sharing. Routing and navigation between apps. Version contracts and runtime failures when a remote breaks. Testing the integrated whole. Observability per team. The operational overhead of more pipelines. You need a platform team owning the shell, shared deps, standards and fallbacks.

**Q3: Monorepo vs polyrepo — trade-offs?**
A3: A monorepo enables atomic cross-project changes, easy code sharing (design system, types, configs), consistent tooling and dependency versions, a single CI view and simpler refactoring. It needs build tooling (Turborepo, Nx, Bazel) for affected-only builds and caching, careful access control (CODEOWNERS) and can strain Git at huge scale. A polyrepo gives strong isolation and independent tooling and permissions, but causes version drift, duplicated config and painful multi-repo changes. A monorepo doesn't force a single deploy: apps can still deploy independently.

**Q4: How does Module Federation share dependencies safely?**
A4: Each federated build declares `shared` modules with version requirements. At runtime the host and remotes negotiate one instance of shared singletons (react, react-dom, design system) when versions are compatible, preventing duplicates and the bugs of multiple React copies (hooks errors). Mismatched versions either load a separate copy or fail per configuration. Teams must coordinate major upgrades of shared singletons and keep exposed module contracts typed and backward-compatible, with fallbacks if a remote fails to load.

**Q5: How do micro-frontends communicate?**
A5: Prefer loose coupling: the URL (route and query params) as shared state, browser CustomEvents or a minimal pub/sub bus for notifications (cart updated), shared backend APIs as the source of truth (each MFE fetches what it needs, possibly via a shared query cache), and props or contracts at composition points for embedded widgets. Avoid a shared global store across MFEs because it recreates coupling. Keep cross-app messages versioned and documented.

---

## 🔷 Trade-offs
✅ MFE: team autonomy, independent deploys, incremental migration — ❌ complexity, performance overhead, consistency risk.
✅ Monorepo: shared code, atomic changes, unified tooling — ❌ tooling investment, CI scaling, repo size.
✅ Modular monolith: simplest fast path — ❌ coupled deploys as org grows.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Micro-frontend | Independently deployed UI slice | अलग deploy होने वाला UI हिस्सा |
| Shell / host | App composing MFEs | MFEs को जोड़ने वाला ऐप |
| Remote | MFE loaded at runtime | runtime पर लोड हिस्सा |
| Module Federation | Runtime module sharing | runtime पर module साझा |
| Multi-Zones | Next.js route-level composition | Next.js में route से बाँटना |
| Monorepo | Many projects in one repo | एक repo में कई projects |
| Workspace | Package manager multi-package setup | कई packages का setup |
| Affected builds | Build only changed + dependents | सिर्फ़ बदला हुआ build |
| Remote cache | Shared build cache in CI | CI में साझा cache |
| CODEOWNERS | Ownership rules per path | folder का मालिक |

---

## ⚡ 3-Line Summary
**English:**
1. Micro-frontends = team-owned, independently deployed UI slices composed by route (simplest), Module Federation, packages, iframes or edge.
2. They need a shell, shared design system & singleton deps, loose communication (URL/events), fallbacks and per-team observability — use only at multi-team scale.
3. Monorepos (Turborepo/Nx + pnpm) share code, types and configs across web, RN, BFF with affected-only builds and remote caching.

**Hindi:**
1. Micro-frontends = टीमों के अलग deploy होने वाले UI हिस्से — route से (सबसे आसान), Module Federation, packages, iframe।
2. चाहिए: shell, साझा design system, एक React, URL/events से बात, fallback — सिर्फ़ कई टीमों पर।
3. Monorepo (Turborepo/Nx) से web, RN, BFF में code/types साझा, सिर्फ़ बदला हुआ build, remote cache।

---

## ➡️ Next Topic Suggestion
**F22. Frontend Observability + Feature Flags + A/B Testing** — Once code ships, how do you know it works for real users and roll out safely? Next: error tracking, RUM, logging, feature flags and experimentation on the frontend.
