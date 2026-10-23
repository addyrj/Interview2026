# M03. Hermes + App Startup Time
# हिंदी में: Hermes + App Startup Time — Hermes, React Native का अपना JavaScript engine जो JS को पहले से bytecode में बदलकर ऐप जल्दी खोलता है; और ऐप खुलने का समय (cold start) कैसे नापें और घटाएँ

---

## 🔵 Simple Definition (English)
**Hermes** is a JavaScript engine built by Meta specifically for React Native. Instead of parsing and compiling JS on the device at launch (like JavaScriptCore or V8 with JIT), Hermes **compiles JS to optimized bytecode at build time (AOT)**. On launch, the bytecode is **memory-mapped and executed immediately**, giving faster startup, lower memory use and a smaller app. It has no JIT (predictable memory), and uses a concurrent garbage collector (**Hades**). It's been the default since RN 0.70.
**App startup time** is the time from tapping the icon to a **usable first screen**:
- **Cold start**: process not running, everything from scratch (slowest, the most important to measure)
- **Warm start**: process alive but activity/screen recreated
- **Hot start**: app brought back from background (fastest)
Metrics: **TTID** (time to initial display, first frame) and **TTFD/TTI** (time to full display / interactive, real content shown and responsive).

## 🔵 सरल परिभाषा (Hindi)
Hermes Meta का बनाया JavaScript engine है जो ख़ास React Native के लिए है — JS को build के समय ही bytecode में बदल देता है, इसलिए फ़ोन पर ऐप खुलते समय parse/compile नहीं करना पड़ता; नतीजा: तेज़ startup, कम memory, छोटा ऐप। RN 0.70 से default।
App startup time = icon दबाने से काम लायक पहली screen तक का समय; Cold start (ऐप बिल्कुल बंद से — सबसे धीमा और सबसे ज़रूरी), Warm, Hot (background से वापस)। नाप: TTID (पहला frame) और TTFD/TTI (असली content दिखे और जवाब दे)।

---

## 🔴 Problem it Solves
- **Users abandon slow apps.** Startup is the first impression, and Android vitals flag cold starts ≥ 5 s as excessive. On a ₹8,000 Android phone with a slow CPU and eMMC storage, a heavy RN app could take 4–8 s to show content.
- Traditional JS engines **parse and compile the whole bundle at launch**, so JS time grows with app size. JIT compilers also use more memory, which is bad on 2–3 GB RAM phones.
- Startup is often wasted on **work nobody needs yet**: initializing all SDKs (analytics, ads, chat), reading big storage synchronously, importing every screen, fetching data serially before showing anything.
Hermes plus disciplined startup work makes apps **open fast on low-end devices**, improving retention, ratings and conversion.

## 🔴 यह क्यों बना? (Hindi)
धीमा ऐप यूज़र छोड़ देते हैं — startup पहली छाप है; Android vitals 5 सेकंड से ज़्यादा cold start को ख़राब मानता है; ₹8,000 के फ़ोन पर भारी RN ऐप 4–8 सेकंड ले सकता था।
पुराने engines हर बार पूरा bundle parse/compile करते थे (ऐप बड़ा = और धीमा), JIT ज़्यादा memory खाता; ऊपर से startup पर बेकार काम — सारे SDKs init, बड़ा storage पढ़ना, हर screen import, एक के बाद एक API calls। Hermes + समझदारी वाला startup = सस्ते फ़ोन पर भी तेज़ ऐप।

---

## 🟢 How it Works — Step by Step

### Hermes vs traditional engine at launch

```
Traditional (JSC/V8):  load JS text → parse → compile (bytecode/JIT) → execute → render
                       ^^^^^^^^^^^^ done on the DEVICE, every cold start, grows with bundle size

Hermes:   BUILD TIME: JS → hermesc → optimized bytecode (.hbc) inside the app
          DEVICE:     mmap bytecode (load pages lazily) → execute immediately → render
          + no JIT warmup, lower memory (no JIT code cache), smaller download
          + Hades concurrent GC → shorter GC pauses
          - peak compute for long-running hot loops can be slower than a JIT (rarely matters in UI apps)
          (Static Hermes — typed, native-compiled JS — is in development for further speedups)
```

### Cold start phases (React Native)

```
Tap icon
 │ 1. OS creates process, loads native libraries          (native: Application.onCreate / didFinishLaunching)
 │ 2. Native init: RN host, TurboModules (lazy), SDKs     ← heavy SDK init here hurts everyone
 │ 3. Load JS bundle (Hermes bytecode mmap)
 │ 4. Execute JS module top-levels (imports!)             ← every eager import executes code
 │ 5. Render root component + navigation                  ← first frame (TTID)
 │ 6. Read local data (auth token, cached feed), API calls
 ▼ 7. Real content visible & responsive                   ← TTFD / TTI (the number users feel)
Splash screen covers 1–5; hide it when meaningful content (or skeleton with cached data) is ready
```

### Startup optimization checklist

```
JS side
✅ Hermes enabled (default) — verify release build uses it
✅ Inline requires (Metro inlineRequires: true) → modules execute only when first used
✅ Lazy-load screens/features (React Navigation screens mount on demand; dynamic import for heavy libs)
✅ Avoid heavy work at module top-level (big JSON, regex compilation, i18n loading of all locales)
✅ Shrink bundle: remove unused deps (moment → dayjs, lodash full → per-method), analyze with
   react-native-bundle-visualizer / Expo Atlas
✅ Defer non-critical work after first render: InteractionManager.runAfterInteractions / setTimeout,
   or after navigation ready (analytics init, prefetching, Sentry replay, remote config refresh)
✅ First screen from cache: persisted React Query cache / local DB → render instantly, refresh in background
✅ Fast sync storage for boot data: MMKV (JSI) instead of AsyncStorage for token/flags
✅ Avoid serial waterfalls: start auth check + config + feed fetch in parallel

Native side
✅ Lazy native SDK initialization (ads, chat, maps) — init on first use, not in Application.onCreate
✅ Fewer/lighter native modules at startup (TurboModules are lazy by default)
✅ Android: baseline profiles (ART precompiles hot paths), R8/minify, avoid main-thread disk I/O
✅ iOS: reduce dynamic frameworks, avoid heavy work in didFinishLaunching
✅ Images/fonts: small splash assets, don't block on remote images
```

### Measure properly

```
Measure on a LOW-END Android device in RELEASE mode (debug builds are much slower)
Android: adb shell am start -W (TotalTime), Logcat "Displayed" (TTID), reportFullyDrawn() for TTFD,
         Android vitals in Play Console (startup percentiles in the field), Perfetto traces
iOS: Xcode Instruments (App Launch template), MetricKit launch metrics, Xcode Organizer
RN: react-native-performance marks (nativeLaunchStart → runJsBundleEnd → contentAppeared),
    Sentry/Firebase Performance app start traces (cold/warm), Flashlight for Android perf scoring
Track p50/p90 per device class & app version; set a budget (e.g., cold start p90 < 2.5 s on mid-tier)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Hermes build के समय JS को bytecode में बदल देता है; फ़ोन पर ऐप खुलते ही bytecode सीधे memory में map होकर चलता है — parse/compile का समय बचता, JIT नहीं तो memory कम, Hades GC से छोटे pause।
2. Cold start के कदम: process बनना → native init (SDKs) → bundle load → JS imports चलना → पहली screen (TTID) → local डेटा/API → असली content (TTFD) — splash तब हटाओ जब काम लायक content (या cache वाला skeleton) तैयार हो।
3. JS में: inline requires, screens lazy, module top-level पर भारी काम नहीं, bundle छोटा (moment की जगह dayjs), analytics/prefetch जैसे काम पहली screen के बाद, पहली screen cache से, MMKV से token/flags, calls parallel।
4. Native में: ads/chat/maps SDKs पहली ज़रूरत पर init, Android baseline profiles, main thread पर disk I/O नहीं।
5. नापो release build में, सस्ते Android पर: adb `am start -W`, Play Console vitals, Xcode Instruments, Sentry/Firebase app start; p90 का budget तय करो (जैसे < 2.5 s)।

---

## 🟡 Real World Example

**Meta (Hermes launch, 2019)** — introduced Hermes for RN, reporting significantly improved time-to-interactive, smaller APK size and lower memory use in their tests on Android. It became the default engine across RN and later on iOS too.

**Shopify, Discord and others** — publicly shared RN startup work: Hermes adoption, lazy initialization of modules, trimming bundles, and showing cached content first to bring cold start down on mid-range Android.

**Android vitals (Google Play)** — Play Console shows cold, warm and hot startup times from real users. Excessive startup times are considered bad behaviour that can affect visibility, so Indian apps targeting low-end devices watch these closely.

**Lite apps (Facebook Lite, YouTube Go historically, Flipkart's lighter clients)** — exist because startup and size on low-end Android in markets like India directly affect adoption.

## 🟡 Real Example Hindi में
Meta ने 2019 में Hermes लॉन्च किया — Android पर time-to-interactive काफ़ी तेज़, APK छोटा और memory कम बताई; बाद में iOS पर भी default बना।
Google Play Console असली यूज़र्स का cold/warm/hot start दिखाता है, और बहुत धीमा startup "ख़राब व्यवहार" माना जाता है; भारत जैसे बाज़ार में Facebook Lite जैसे "lite" ऐप इसलिए बने क्योंकि सस्ते फ़ोन पर startup और size सीधे adoption तय करते हैं।

---

## 🟠 My Stack Example

### Metro config: inline requires
```js
// metro.config.js (Expo)
const { getDefaultConfig } = require('expo/metro-config');
const config = getDefaultConfig(__dirname);
config.transformer.getTransformOptions = async () => ({ transform: { experimentalImportSupport: false, inlineRequires: true } });
module.exports = config;
```

### Boot sequence: parallel, cached-first, splash hidden at the right moment
```tsx
// app/_layout.tsx (Expo Router)
import * as SplashScreen from 'expo-splash-screen';
import { storage } from '@/data/kv';                       // MMKV — synchronous, fast
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [ready, setReady] = useState(false);
  useEffect(() => {
    (async () => {
      const hasSession = !!storage.getString('session.userId');          // sync, ~µs
      await Promise.all([
        restorePersistedQueryCache(),                                  // cached feed for instant first screen
        hasSession ? refreshTokenSilently().catch(() => {}) : null,    // don't block forever on network
      ]);
      setReady(true);
    })();
  }, []);

  const onLayout = useCallback(() => { if (ready) SplashScreen.hideAsync(); }, [ready]);
  if (!ready) return null;
  return <View style={{ flex: 1 }} onLayout={onLayout}><Stack /></View>;
}
```

### Defer non-critical init until after first interactions
```ts
import { InteractionManager } from 'react-native';
export function deferredStartup() {
  InteractionManager.runAfterInteractions(async () => {
    await analytics.init();                 // not needed for first frame
    remoteConfig.fetchAndActivate();        // use cached values for this session
    prefetchImages(topRestaurantImages());
    import('@/features/chat-support').then((m) => m.init());   // heavy SDK lazily
  });
}
```

### Lazy heavy screen/library
```tsx
// Only load the map stack when the user opens tracking
const TrackScreen = React.lazy(() => import('@/features/tracking/TrackScreen'));
```

### Measure in code (react-native-performance)
```ts
import performance from 'react-native-performance';
// mark when first meaningful content renders
useEffect(() => { performance.mark('homeContentVisible'); }, [hasFeedItems]);
performance.measure('coldStartToContent', 'nativeLaunchStart', 'homeContentVisible');
const [m] = performance.getEntriesByName('coldStartToContent');
analytics.track('startup', { ms: Math.round(m.duration), device: DeviceInfo.getModel(), version: appVersion });
```

### Android: report fully drawn & check release startup
```bash
adb shell am force-stop in.quickbite.app
adb shell am start -W -n in.quickbite.app/.MainActivity     # TotalTime = cold start to first frame
# In native code (MainActivity) call reportFullyDrawn() when JS signals content is ready → TTFD in vitals
```

---

## ⚫ Interview Questions + Answers

**Q1: What is Hermes and why is it faster for app startup?**
A1: Hermes is Meta's JavaScript engine optimized for React Native. It compiles JavaScript ahead of time into compact bytecode during the build, so at launch the app memory-maps and executes bytecode directly instead of parsing and compiling source on the device. That cuts startup time and memory, and there's no JIT, so memory use is lower and more predictable. It also produces smaller app sizes and uses a concurrent GC (Hades) to reduce pauses. The trade-off is potentially slower peak throughput for long-running compute-heavy JS, which rarely matters for UI apps.

**Q2: How would you reduce the cold start time of a React Native app?**
A2: Measure first, in release builds on low-end devices, with phase marks. Then make sure Hermes is on and enable inline requires. Lazy-load screens and heavy libraries, and remove top-level side effects. Trim the bundle and dependencies. Defer non-critical SDK initialization (analytics, ads, chat) until after first render. Lazily initialize native SDKs and avoid main-thread disk I/O. Use fast synchronous storage (MMKV) for boot data and parallelize boot requests. Render the first screen from cached data with skeletons, and hide the splash screen when meaningful content is ready. Add Android baseline profiles and track startup percentiles per release.

**Q3: What's the difference between cold, warm and hot start?**
A3: A cold start launches the app process from scratch: loading native libraries, initializing the runtime, loading and executing the JS bundle and rendering the first screen. It's the slowest and most important to optimize. A warm start happens when the process exists but the activity or UI must be recreated (e.g., after the system destroyed it under memory pressure). A hot start brings an app already in memory back to the foreground, which is the fastest. Measure all three, but budget primarily on cold start.

**Q4: Why can analytics and other SDKs slow startup, and what do you do?**
A4: Many SDKs initialize eagerly in native application startup or at JS import time. They read config from disk, open network connections, register lifecycle hooks and sometimes do synchronous work on the main thread, adding hundreds of milliseconds before the first frame. Audit startup traces and initialize SDKs lazily (on first use) or after the first screen renders. Batch analytics events captured before init. Choose lighter SDKs and remove unused ones.

**Q5: How do you show content quickly even when the network is slow?**
A5: Persist server-state caches (React Query persistence or a local DB) and render the last known data immediately on launch, marked as possibly stale, then refresh in the background. Show skeletons for missing pieces rather than blocking spinners. Avoid gating the first screen on network calls such as token refresh (use cached session state and refresh in parallel with timeouts). Prefetch critical data on the previous session's exit or via background fetch where allowed.

---

## 🔷 Trade-offs
✅ Hermes: fast startup, low memory, smaller app — ❌ no JIT peak speed; some JS features/debugging differences historically.
✅ Lazy initialization: fast first frame — ❌ first use of a feature may be slower (prefetch after startup).
✅ Cached-first render: instant content — ❌ stale data briefly; need clear refresh indicators.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hermes | RN-optimized JS engine | RN का JS engine |
| AOT bytecode | Compiled at build time | build के समय compile |
| JIT | Compile while running | चलते-चलते compile |
| Cold start | Launch from scratch | बिल्कुल बंद से खुलना |
| Warm / hot start | Partial / from background | आधा / background से |
| TTID | Time to initial display | पहला frame |
| TTFD / TTI | Time to full display / interactive | असली content और जवाब |
| Inline requires | Execute modules on first use | पहली ज़रूरत पर module |
| Baseline profile | Android precompiled hot code | Android का पहले से compile |
| Splash screen | Launch screen while loading | खुलते समय की screen |

---

## ⚡ 3-Line Summary
**English:**
1. Hermes compiles JS to bytecode at build time → mmap & run on launch: faster startup, less memory, smaller app.
2. Cold start = process + native init + bundle + JS imports + first render + data; optimize each: lazy SDKs/screens, inline requires, small bundle, MMKV, parallel boot, cached-first UI.
3. Measure in release on low-end devices (Play vitals, Instruments, performance marks) and enforce a startup budget per release.

**Hindi:**
1. Hermes JS को build के समय bytecode बनाता है → तेज़ startup, कम memory, छोटा ऐप।
2. Cold start के हर कदम को घटाओ: SDKs/screens lazy, inline requires, छोटा bundle, MMKV, parallel boot, cache से पहली screen।
3. Release build में सस्ते फ़ोन पर नापो और हर release के लिए startup budget रखो।

---

## ➡️ Next Topic Suggestion
**M04. App Lifecycle + Background Tasks** — Once the app is open, the OS can pause or kill it at any moment. Next: app states on iOS and Android, what you can and can't do in the background, and how to run uploads, sync and location reliably.
