# F22. Frontend Observability + Feature Flags + A/B Testing
# हिंदी में: Frontend Observability — असली यूज़र्स के ब्राउज़र/फ़ोन में क्या हो रहा है (errors, धीमापन, crashes) यह देखना; Feature Flags — बिना नया deploy किए किसी feature को चालू/बंद या धीरे-धीरे कुछ % यूज़र्स के लिए खोलना; A/B Testing — दो versions आज़माकर डेटा से तय करना कि कौन बेहतर है

---

## 🔵 Simple Definition (English)
- **Frontend observability**: collecting signals from **real users' devices** to understand failures and performance:
  - **error tracking** (JS exceptions, unhandled promise rejections, React error boundaries, crash reports) with **source maps**
  - **RUM** (Real User Monitoring: Web Vitals, page/screen load, API latency from the client)
  - **structured client logs and breadcrumbs**
  - **session replay** (privacy-masked)
  - **distributed tracing** from browser/app to backend (`traceparent` header)
  - **release health** (crash-free sessions per version)
  Tools: **Sentry**, Datadog RUM, New Relic, Firebase Crashlytics/Performance, OpenTelemetry Web, LogRocket.
- **Feature flags (toggles)**: runtime switches that turn code paths on or off **per user/segment/percentage** without redeploying. Types: **release flags**, **ops kill switches**, **experiment flags**, **permission/entitlement flags**. Tools: LaunchDarkly, Unleash, GrowthBook, Statsig, Flagsmith, Firebase Remote Config, or in-house.
- **A/B testing (experimentation)**: randomly assign users to **control (A)** and **variant (B)**, measure a **primary metric** (conversion, orders per user) and **guardrails** (latency, crashes, cancellations), and use statistics to decide whether B is really better.

## 🔵 सरल परिभाषा (Hindi)
Observability = असली यूज़र्स के devices से संकेत इकट्ठा करना: JS errors और crashes (source maps के साथ सही line), Web Vitals और API की गति (RUM), logs/breadcrumbs, session replay (निजी जानकारी छुपाकर), और ब्राउज़र से backend तक trace।
Feature flag = code में switch जिससे बिना deploy किसी feature को कुछ यूज़र्स/शहरों/% के लिए चालू या बंद करो (kill switch भी)। A/B testing = यूज़र्स को random दो समूहों में बाँटकर देखना कि नया version सच में बेहतर है या नहीं — एक मुख्य metric और सुरक्षा (guardrail) metrics के साथ।

---

## 🔴 Problem it Solves
- Backend dashboards can be **all green while users suffer**: a JS error on one Android WebView version breaks checkout, a slow third-party script ruins INP in Tier-2 cities, or a new release crashes on iOS 17 only. Without client-side signals, you hear about it from **angry tweets or 1-star reviews**.
- **Big-bang releases are risky**: if the new checkout breaks, you need a rollback deploy (and on mobile, app-store review takes days).
- Opinions ("the green button converts better") lead to **wrong product decisions**. Changes need **causal evidence**.
Observability finds and fixes problems fast. Flags make releases **safe, gradual and reversible**. Experiments make decisions **data-driven**.

## 🔴 यह क्यों बना? (Hindi)
Backend के dashboard हरे हो सकते हैं जबकि यूज़र परेशान हैं — किसी Android WebView पर checkout टूटा, Tier-2 शहरों में कोई बाहरी script धीमी, iOS 17 पर ही crash; client के संकेतों के बिना पता Twitter या 1-star reviews से चलता है।
एक साथ पूरी release ख़तरनाक है (mobile पर rollback में app store के दिन लगते हैं); और राय से फ़ैसले ग़लत होते हैं। Observability से जल्दी पता, flags से सुरक्षित धीरे-धीरे release, experiments से डेटा वाले फ़ैसले।

---

## 🟢 How it Works — Step by Step

### Frontend observability pipeline

```
Browser / RN app
  ├─ window.onerror, unhandledrejection, React ErrorBoundary, native crash handler
  ├─ Web Vitals (LCP/INP/CLS), screen load time, API timings, custom marks
  ├─ breadcrumbs: route changes, clicks, console, network calls (last 100 events before an error)
  ├─ context: release version, environment, device, OS, browser, network (4g), locale, userId (hashed), flags
  └─ traceparent header on API calls → backend spans join the same trace (OpenTelemetry)
        │ batched, sampled, sent via sendBeacon / background
        ▼
  Collector (Sentry / Datadog / OTel collector) → symbolication with source maps (uploaded in CI,
  NOT public) → grouping (fingerprints) → dashboards & alerts:
     "Crash-free sessions < 99.5% for v5.12"   "New error spike in /checkout"   "p75 INP > 300 ms on Android"
```

### Key practices

```
- Upload source maps (web) / dSYM + ProGuard mappings (native) per release in CI; tag events with release
- Sample: 100% errors, 5–20% performance traces, 1–5% session replays (cost + privacy)
- Privacy: mask PII (phone, address, card fields) in replays & logs; DPDP Act (India) / GDPR consent
- Error budgets/SLOs for the client too: crash-free users ≥ 99.8%, checkout JS error rate < 0.1%
- Alert on regressions per release; link errors to the owning team (CODEOWNERS, MFE tags)
- Correlate: client error → requestId/traceId → backend logs → root cause
```

### Feature flags: lifecycle

```
1. Create flag "new_checkout" (off) → merge code behind flag (trunk-based development)
2. Enable for employees/internal → QA in production
3. Gradual rollout: 1% → 5% → 25% → 50% → 100%, watching errors, latency, conversion (guardrails)
4. Kill switch: something breaks → turn off instantly (no deploy, no app-store review)
5. 100% stable for a few weeks → REMOVE flag + old code path (flag debt is real tech debt)

Targeting rules: userId %, city (BLR, DEL first), platform (android ≥ 5.12), plan (Gold members), app version
Deterministic bucketing: bucket = hash(flagKey + userId) % 100 → same user always same variant
```

### Where to evaluate flags

```
Server-side (BFF/Next.js server/middleware): no flicker, secrets safe, SSR renders correct variant ✅
Client-side SDK: bootstrap flags in the initial HTML/app start, cache locally (MMKV/localStorage), stream
                 updates; avoid "flash of old UI" by waiting for bootstrap or using defaults carefully
Mobile: fetch at startup with cached last-known values; OFFLINE default must be safe
Never put security decisions only in client flags (client can be tampered) — backend enforces permissions
```

### A/B testing done right

```
1. Hypothesis: "Showing delivery fee upfront increases checkout completion by ≥ 1%"
2. Unit of randomization: user (not session/pageview) → consistent experience
3. Metrics: primary (order conversion), guardrails (cancellation rate, support tickets, page latency, crashes)
4. Sample size & duration: power analysis (baseline rate, minimum detectable effect, α=0.05, power 0.8);
   run full weeks (weekday/weekend patterns, salary-day effects in India)
5. Exposure logging: log when the user ACTUALLY saw the variant (not just assigned)
6. Checks: Sample Ratio Mismatch (50/50 expected but 52/48 → bug), A/A tests, no peeking/early stopping
   (or use sequential testing methods), novelty effect, multiple-testing corrections
7. Decide: ship / iterate / kill; document learnings
Assignment on the server avoids flicker and keeps web + app consistent for the same user
```

## 🟢 कैसे काम करता है? (Hindi)
1. ब्राउज़र/ऐप में errors (onerror, unhandledrejection, ErrorBoundary, native crash), Web Vitals, API समय और breadcrumbs (error से पहले क्या हुआ) इकट्ठा करो; साथ में release version, device, network, flags।
2. CI में source maps upload (public नहीं) ताकि minified error सही line दिखाए; 100% errors, 5–20% traces, 1–5% replays; replay/logs में phone, पता, card छुपाओ (DPDP Act)।
3. API calls पर `traceparent` header — client error से backend logs तक एक ही trace; हर release पर crash-free % और error spike पर alert।
4. Feature flag: code flag के पीछे merge → पहले कर्मचारी → 1% → 5% → 25% → 100% (guardrails देखते हुए); टूटे तो kill switch; पूरा होने पर flag और पुराना code हटाओ; `hash(flag + userId) % 100` से हर यूज़र का समूह पक्का।
5. A/B test: hypothesis, यूज़र स्तर पर random, मुख्य metric + guardrails, पहले से sample size, पूरे हफ़्ते चलाओ, असली exposure log करो, SRM जाँच, बीच में झाँककर जल्दी मत रोको; server पर assignment ताकि UI न झपके।

---

## 🟡 Real World Example

**Booking.com** — famous for running around a thousand concurrent experiments. Almost every change is A/B tested, with a strong culture of guardrail metrics and trustworthy experimentation.

**Facebook (Gatekeeper) / Google / LinkedIn (XLNT)** — internal flag and experiment platforms with gradual rollouts to employees, then small percentages, then everyone. LinkedIn and Microsoft published widely on experiment pitfalls (SRM, novelty).

**Netflix** — A/B tests UI changes including personalized artwork, and uses its Atlas/Edgar and Sentry-like client telemetry to catch device-specific playback issues across thousands of TV models.

**Indian apps (Swiggy, Zomato, Flipkart, PhonePe)** — large Indian consumer apps commonly run in-house experimentation platforms and use Firebase Remote Config, Crashlytics or Sentry for mobile, rolling features out city by city (e.g., launch in Bengaluru first) with kill switches for festival-sale traffic.

## 🟡 Real Example Hindi में
Booking.com एक साथ लगभग हज़ार experiments चलाने के लिए मशहूर है; Facebook (Gatekeeper), LinkedIn (XLNT) पहले कर्मचारियों, फिर कुछ %, फिर सबके लिए rollout करते हैं; Netflix personalized artwork तक A/B test करता है।
Swiggy, Zomato, Flipkart, PhonePe जैसे ऐप आम तौर पर अपने experimentation platform, Firebase Remote Config, Crashlytics/Sentry इस्तेमाल करते हैं — features पहले एक शहर (जैसे बेंगलुरु) में, और सेल के दिनों के लिए kill switch।

---

## 🟠 My Stack Example

### Sentry in Next.js (errors + tracing + replay with masking)
```ts
// instrumentation-client.ts (Next.js) — or sentry.client.config.ts in older setups
import * as Sentry from '@sentry/nextjs';
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  release: process.env.NEXT_PUBLIC_RELEASE,                 // git SHA set in CI
  environment: process.env.NEXT_PUBLIC_ENV,
  tracesSampleRate: 0.1,                                    // 10% performance traces
  tracePropagationTargets: [/^https:\/\/api\.quickbite\.in/], // adds sentry-trace/traceparent to API calls
  replaysSessionSampleRate: 0.02, replaysOnErrorSampleRate: 1.0,
  integrations: [Sentry.browserTracingIntegration(), Sentry.replayIntegration({ maskAllText: true, blockAllMedia: true })],
  beforeSend(event) { if (event.user) event.user = { id: event.user.id }; return event; },   // drop PII
});
```
```yaml
# CI: upload source maps privately, then delete them from the public build output
- run: npx @sentry/cli sourcemaps inject ./.next && npx @sentry/cli sourcemaps upload --release $GITHUB_SHA ./.next
  env: { SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}, SENTRY_ORG: quickbite, SENTRY_PROJECT: web }
```

### Error boundary with context + user-friendly fallback
```tsx
'use client';
import * as Sentry from '@sentry/nextjs';
export function CheckoutBoundary({ children }: { children: React.ReactNode }) {
  return (
    <Sentry.ErrorBoundary
      beforeCapture={(scope) => { scope.setTag('area', 'checkout'); scope.setTag('team', 'payments'); }}
      fallback={({ resetError }) => (<div role="alert"><p>Something went wrong with checkout.</p><button onClick={resetError}>Try again</button></div>)}>
      {children}
    </Sentry.ErrorBoundary>
  );
}
```

### React Native (Sentry or Crashlytics)
```ts
import * as Sentry from '@sentry/react-native';
Sentry.init({ dsn: SENTRY_DSN, release: `${appVersion}+${buildNumber}`, dist: String(buildNumber),
              tracesSampleRate: 0.1, enableAutoSessionTracking: true });   // crash-free sessions per release
export default Sentry.wrap(App);
// EAS build hooks upload source maps + dSYMs; OTA updates (M17) tagged with update id
```

### Feature flags: deterministic bucketing (shared util for BFF, web, RN)
```ts
// packages/utils/src/flags.ts
import murmur from 'murmurhash-js';
type Rule = { key: string; enabled: boolean; rolloutPercent: number; cities?: string[]; minAppVersion?: string; allowUserIds?: string[] };

export function isEnabled(rule: Rule, ctx: { userId: string; city?: string; appVersion?: string }): boolean {
  if (!rule.enabled) return false;                                         // kill switch
  if (rule.allowUserIds?.includes(ctx.userId)) return true;                 // employees / QA
  if (rule.cities && !rule.cities.includes(ctx.city ?? '')) return false;
  if (rule.minAppVersion && ctx.appVersion && semverLt(ctx.appVersion, rule.minAppVersion)) return false;
  const bucket = murmur.murmur3(`${rule.key}:${ctx.userId}`) % 100;        // stable per user per flag
  return bucket < rule.rolloutPercent;
}
```

### Evaluate on the server (no flicker), bootstrap into the client
```tsx
// app/checkout/page.tsx (Server Component)
const flags = await getFlagsForUser(user);                 // from Unleash/GrowthBook/own service, cached 30 s
return (
  <FlagsProvider value={flags}>
    {flags.new_checkout ? <NewCheckout /> : <OldCheckout />}
  </FlagsProvider>
);
// Client components read useFlag('upi_intent_button') from context — same values as SSR
```

### A/B experiment: assignment + exposure + metric events
```ts
// BFF: assign variant deterministically
const variant = murmur.murmur3(`exp_fee_upfront:${userId}`) % 100 < 50 ? 'control' : 'treatment';

// Client: log exposure only when the variant is actually rendered
useEffect(() => { analytics.track('experiment_exposure', { experiment: 'exp_fee_upfront', variant }); }, [variant]);
// Metric events: 'checkout_started', 'order_placed' { orderValue } → warehouse (ClickHouse/BigQuery)
```
```sql
-- Analysis sketch: conversion per variant (+ SRM check on exposure counts)
SELECT variant, COUNT(DISTINCT user_id) AS exposed,
       COUNT(DISTINCT CASE WHEN placed THEN user_id END)::float / COUNT(DISTINCT user_id) AS conversion
FROM exp_fee_upfront_users GROUP BY variant;
```

### Firebase Remote Config on React Native (simple flags + kill switch)
```ts
import remoteConfig from '@react-native-firebase/remote-config';
await remoteConfig().setDefaults({ new_checkout: false, min_supported_version: '5.0.0' });   // safe offline defaults
await remoteConfig().fetchAndActivate();
const newCheckout = remoteConfig().getValue('new_checkout').asBoolean();
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you monitor a frontend in production?**
A1: Capture errors (global handlers, unhandled rejections, error boundaries, native crashes) with release tags and privately uploaded source maps. Collect RUM: Web Vitals, route and screen load times, API latency and errors from the client, segmented by device, network, region and version. Record breadcrumbs and context, sampled session replays with PII masking, and propagate trace context to the backend for end-to-end traces. Build dashboards and alerts on error spikes, crash-free rate and vitals regressions per release, and route issues to owning teams.

**Q2: What are feature flags and their risks?**
A2: Runtime switches that control code paths per user, segment or percentage without deploying. They enable trunk-based development, safe gradual rollouts, instant kill switches, beta programs and experiments. Risks: flag debt (stale flags and dead code paths), combinatorial complexity in testing, flicker or inconsistent UX if evaluated late on the client, security mistakes if permissions rely only on client flags, and outages if the flag service is down (use cached values and safe defaults). Manage flags with owners, expiry dates and cleanup tasks.

**Q3: How do you roll out a risky new checkout flow?**
A3: Build it behind a flag and test internally in production (employees, allowlist). Roll out gradually (1% → 5% → 25% → 100%), possibly city by city, while monitoring guardrails: JS errors and crashes, API error rates, latency, payment success rate, conversion and support contacts. Use deterministic bucketing so users have a consistent experience. Keep a kill switch to revert instantly, and on mobile ensure old app versions and offline defaults are safe. Once stable, remove the flag and the old code.

**Q4: What can go wrong with A/B tests?**
A4: An underpowered test (too small a sample or too short) gives inconclusive or false results. Peeking and stopping early inflates false positives. Sample ratio mismatch points to assignment or logging bugs. Randomizing by session instead of user gives inconsistent experiences. Novelty or primacy effects distort results. Network effects and interference matter in marketplaces (riders shared between groups). Testing many metrics without correction finds spurious wins, and ignoring guardrails ships changes that hurt other metrics. Client-side assignment flicker biases results. Mitigate with power analysis, pre-registered metrics, SRM checks, A/A tests and proper statistics.

**Q5: Why use source maps and how do you keep them secure?**
A5: Production JS is minified and bundled, so stack traces point to unreadable locations. Source maps translate them back to original files and lines, making errors actionable. Generate them in CI per release, upload them privately to the error-tracking service tied to the release identifier, and don't serve them publicly (delete them from the deploy artifacts or restrict access), since they expose source code. For React Native, also upload Hermes bytecode maps, dSYMs (iOS) and ProGuard/R8 mappings (Android).

---

## 🔷 Trade-offs
✅ Client observability catches real-user problems — ❌ data volume cost, privacy/compliance, SDK weight on bundle.
✅ Feature flags: safe releases & kill switches — ❌ flag debt, testing combinations, flag service dependency.
✅ A/B testing: causal decisions — ❌ needs traffic, time, statistical rigor; can slow bold changes.
✅ Server-side evaluation: no flicker — ❌ less dynamic for purely client experiences.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RUM | Real User Monitoring | असली यूज़र की निगरानी |
| Source map | Maps minified code to source | छोटे code से असली line |
| Breadcrumbs | Events before an error | error से पहले के कदम |
| Session replay | Recorded user session (masked) | यूज़र session की recording |
| Crash-free rate | % sessions without crash | बिना crash sessions % |
| Feature flag | Runtime on/off switch | बिना deploy का switch |
| Kill switch | Instantly disable a feature | तुरंत बंद करने का switch |
| Gradual rollout | Increase % over time | धीरे-धीरे % बढ़ाना |
| Guardrail metric | Must-not-worsen metric | बिगड़ना नहीं चाहिए वाला metric |
| SRM | Sample ratio mismatch | समूहों का अनुपात गड़बड़ |

---

## ⚡ 3-Line Summary
**English:**
1. Observe real users: errors with source maps, RUM/Web Vitals, breadcrumbs, masked replays, trace propagation, per-release health and alerts.
2. Feature flags enable trunk-based dev, gradual rollouts with guardrails, instant kill switches — evaluate server-side, bucket deterministically, clean up debt.
3. A/B tests need hypothesis, user-level randomization, primary + guardrail metrics, power analysis, exposure logging, SRM checks and no peeking.

**Hindi:**
1. असली यूज़र देखो: errors + source maps, RUM, breadcrumbs, छुपी जानकारी वाले replays, trace, हर release की सेहत।
2. Feature flags: धीरे-धीरे rollout, kill switch, server पर evaluation, पक्का bucketing, पुराने flags हटाओ।
3. A/B test: hypothesis, यूज़र स्तर पर random, मुख्य + guardrail metrics, sample size, exposure log, SRM जाँच।

---

## ➡️ Next Topic Suggestion
**🎉 Frontend System Design complete!** Next: **M01. Mobile System Design Framework** in `08-Mobile-System-Design/`. Mobile design rounds add new constraints: app lifecycle, offline-first, battery, app-store releases and old app versions in the wild.
