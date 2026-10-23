# M14. Mobile Performance (JS Thread vs UI Thread, Memory, Re-renders)
# हिंदी में: Mobile Performance — React Native ऐप को तेज़ और smooth रखना: दो धागे (JS thread पर logic, UI thread पर drawing), बेवजह re-render रोकना, animations को सही धागे पर चलाना, memory leaks पकड़ना और profiling tools से नापना

---

## 🔵 Simple Definition (English)
React Native performance is about keeping two threads under their **frame budget (16.7 ms at 60 fps, 8.3 ms at 120 fps)**:
- **JS thread**: runs React renders, state updates, business logic, JS-driven animations and event handlers. If it's busy, **taps feel laggy, lists show blanks, and JS animations stutter**.
- **UI (main) thread**: native layout mounting, drawing, native gestures and animations. If it's busy (too many views, overdraw, heavy images, layout thrash), **everything janks**.
Main levers:
- **Fewer and cheaper re-renders** (memo, selectors, state colocation, React Compiler)
- **Animations on the UI thread** (Reanimated worklets, `useNativeDriver`)
- **Off-thread heavy work** (native modules, workers)
- **Fast storage** (MMKV)
- **Optimized lists and images** (M12–M13)
- **Lean navigation** (native-stack, freezing inactive screens)
- **Memory hygiene** (clean up listeners and timers, bounded caches, image sizes)
- **Measuring in release builds on low-end devices** with profilers

## 🔵 सरल परिभाषा (Hindi)
RN performance = दोनों धागों को हर frame के बजट में रखना (60 fps पर 16.7 ms): JS thread (React render, state, logic, handlers) व्यस्त हो तो tap धीमे, list में ख़ाली जगह, JS animation अटके; UI thread (native views बनाना, drawing, gestures) व्यस्त हो तो सब कुछ झटकेदार।
तरीके: कम और सस्ते re-renders (memo, selectors, React Compiler), animations UI thread पर (Reanimated), भारी काम thread से बाहर, MMKV, सही lists/images, हल्का navigation, memory साफ़ रखना, और release build में सस्ते फ़ोन पर नापना।

---

## 🔴 Problem it Solves
Users judge apps by **smoothness and responsiveness**:
- A tap on "Add to cart" that takes 400 ms to respond feels broken.
- Screen transitions that stutter, a bottom sheet that lags behind the finger, or a typing input that drops characters.
- Memory leaks that crash the app after 20 minutes of browsing (OOM), especially on 2–3 GB Android phones.
- High-end iPhones hide problems that **₹8,000–15,000 Android devices** (most Indian users) expose immediately.
Typical root causes are **unnecessary re-renders, heavy work on the JS thread, JS-driven animations, huge view hierarchies, unoptimized images and leaks**. A systematic approach fixes them and keeps them from coming back.

## 🔴 यह क्यों बना? (Hindi)
यूज़र ऐप को smoothness से परखते हैं: "Add to cart" पर 400 ms बाद जवाब = टूटा हुआ लगता है; अटकते transitions, उँगली से पीछे चलती bottom sheet, typing में अक्षर छूटना; 20 मिनट browsing के बाद memory leak से crash।
महँगे iPhone पर समस्याएँ छुप जाती हैं, पर ₹8,000–15,000 के Android (ज़्यादातर भारतीय यूज़र) पर तुरंत दिखती हैं। मूल कारण: बेवजह re-render, JS thread पर भारी काम, JS animations, बहुत सारे views, बड़ी images, leaks।

---

## 🟢 How it Works — Step by Step

### Diagnose: which thread is the problem?

```
Perf Monitor (dev menu) shows TWO fps numbers:
  JS fps low, UI fps fine   → JS thread busy: re-renders, heavy logic, JSON parse, sync storage,
                              console.log spam, JS animations (Animated without native driver)
  UI fps low                → UI thread busy: too many/nested views, overdraw (stacked backgrounds),
                              big images decoding, shadows/blur on Android, layout-heavy animations,
                              many simultaneous native updates
  Both low                  → heavy rendering → big commits mounting many views
Always profile RELEASE builds (dev mode is 2–5× slower) on a low-end Android device.
```

### Re-render control

```
Why components re-render: own state change, parent re-render, context value change, hook subscription change
Tools: React DevTools Profiler ("why did this render?"), why-did-you-render, highlight updates
Fixes:
- Colocate state (keep it in the smallest component that needs it)
- Selectors for stores: useCart(s => s.items[id]?.qty) instead of useCart() whole state
- Split contexts; memoize provider values
- React.memo for list rows/heavy children; useCallback/useMemo for props passed to memo children
- React Compiler (auto-memoization) — reduces manual memo work
- Avoid creating objects/arrays/functions inline as props to memoized children
- Derived data via useMemo/selectors, not effects that set state (double render)
- Don't store fast-changing values (scroll position, animation values) in React state → use
  Reanimated shared values / refs
```

### Animations & gestures on the UI thread

```
❌ Animated with useNativeDriver: false, or setState per frame → JS thread drives every frame
✅ Animated with useNativeDriver: true (transform/opacity only)
✅ Reanimated: useSharedValue + useAnimatedStyle → worklets run on UI thread; gestures via
   react-native-gesture-handler (native recognizers) → smooth even if JS is busy
✅ LayoutAnimation / Reanimated layout transitions for list insert/remove
✅ Animate transform & opacity; avoid animating width/height/top (layout work)
```

### Keep the JS thread free

```
- Defer non-urgent work after transitions: InteractionManager.runAfterInteractions, requestIdleCallback-like
- Break big computations into chunks or move to native/worklets (react-native-worklets-core) / server
- Avoid large JSON.parse at startup (paginate, local DB queries)
- Use MMKV (sync, fast) instead of awaiting AsyncStorage in hot paths
- Strip console.* in release (babel-plugin-transform-remove-console) — logging is slow on device
- Debounce input handlers (search), throttle scroll handlers
- Avoid heavy third-party JS libs on hot paths (moment, big lodash)
```

### Navigation performance

```
- @react-navigation/native-stack (native UIViewController / Fragment transitions) ✅
- Lazy tabs (screens mount on first focus); freeze inactive screens (react-native-screens enableFreeze)
  → background screens don't re-render on global state changes
- Avoid heavy work in screen mount: fetch in parallel, render skeleton, then content
- Pass ids in params, not big objects
```

### Memory: leaks & budgets

```
Common leaks: event listeners/subscriptions not removed (AppState, NetInfo, sockets, Keyboard),
  setInterval not cleared, closures held in global caches/maps, unbounded arrays (logs, analytics buffer),
  retained images, navigation stacks growing forever (push without pop)
Tools: Hermes heap snapshots (Chrome DevTools / React Native DevTools), Android Studio Memory Profiler,
       Xcode Instruments (Allocations, Leaks), LeakCanary for native Android leaks
Rules: every useEffect that subscribes returns cleanup; bounded caches (LRU); images at display size;
       reset/replace navigation stacks for flows (checkout → success → replace home)
```

### View hierarchy & layout

```
- Fewer nested Views (Fabric flattens layout-only views, but keep it lean)
- Avoid unnecessary absolute overlays & transparent backgrounds (overdraw on Android)
- Prefer FastImage/expo-image; avoid large shadows on Android (use elevation carefully)
- Text: avoid huge single Text nodes with thousands of chars (paginate)
- Keep re-mounts low: stable keys, conditional rendering vs display toggling as appropriate
```

### Profiling toolbox

```
React Native DevTools (RN 0.76+): Profiler, components, Hermes debugger
Hermes sampling profiler → .cpuprofile → Chrome DevTools flame chart (JS hotspots)
Android: Perfetto/systrace, Android Studio Profiler (CPU, memory), GPU overdraw debug, Flashlight score
iOS: Xcode Instruments (Time Profiler, Core Animation FPS, Allocations), MetricKit hang reports
Production: Sentry/Firebase Performance (slow/frozen frames, app start, screen load), ANR rate in Play vitals
```

## 🟢 कैसे काम करता है? (Hindi)
1. Perf Monitor में दो fps: JS fps कम = JS thread व्यस्त (re-render, भारी logic, बड़ा JSON, console.log, JS animations); UI fps कम = UI thread व्यस्त (बहुत views, overdraw, बड़ी images, Android shadows); हमेशा release build में सस्ते फ़ोन पर नापो।
2. Re-render घटाओ: state उसी component में जहाँ ज़रूरत, store से selector (सिर्फ़ अपना हिस्सा), context बाँटो, `memo` + `useCallback`, React Compiler; scroll/animation जैसे तेज़ बदलते मान state में नहीं — shared values/refs में।
3. Animations UI thread पर: Reanimated worklets, gesture-handler, `useNativeDriver: true`; सिर्फ़ transform/opacity animate करो।
4. JS thread ख़ाली रखो: transition के बाद भारी काम (InteractionManager), बड़ा काम टुकड़ों में या native में, MMKV, release में console हटाओ, search में debounce; navigation में native-stack, lazy tabs, पीछे की screens freeze।
5. Memory: हर subscription/timer का cleanup, सीमित cache, सही आकार की images, navigation stack बेवजह न बढ़े; Hermes heap snapshot, Android Profiler, Instruments; production में Sentry slow/frozen frames और Play vitals ANR।

---

## 🟡 Real World Example

**Discord** — publicly discussed making its React Native app fast on Android: moving to Hermes, optimizing chat list rendering, reducing re-renders and moving heavy work off the JS thread. Chat is the hottest path.

**Shopify** — runs performance budgets and CI measurements for RN apps (startup, screen load, FPS), built FlashList, and shares profiling practices for low-end Android.

**Coinbase** — after migrating to RN, focused on render performance (memoization, avoiding unnecessary context updates) and startup time to match native quality for price-tickers and charts.

**Indian consumer apps** — performance on budget Android phones is a top priority for Swiggy, Zomato, PhonePe, Meesho and others (most users are on ₹10–15k devices). Play Console's ANR and slow-frame vitals affect store visibility.

## 🟡 Real Example Hindi में
Discord ने Android पर RN ऐप तेज़ करने के लिए Hermes, chat list rendering, कम re-renders और भारी काम JS thread से बाहर किया; Shopify RN ऐप के लिए CI में startup, screen load और FPS budgets रखता है।
भारत में Swiggy, Zomato, PhonePe, Meesho जैसे ऐप्स के लिए ₹10–15 हज़ार के Android पर performance सबसे ज़रूरी — Play Console में ANR और slow frames store में दिखने पर असर डालते हैं।

---

## 🟠 My Stack Example

### Selector-based subscriptions (only the affected row re-renders)
```tsx
// ❌ every consumer re-renders on any cart change
const cart = useCart();
// ✅ subscribe to exactly what you render
const qty = useCart((s) => s.items[dishId]?.qty ?? 0);
const total = useCart(useShallow((s) => [s.subtotal, s.deliveryFee]));   // zustand/react/shallow for tuples
```

### Bottom sheet / drag on UI thread (Reanimated + Gesture Handler)
```tsx
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import Animated, { useSharedValue, useAnimatedStyle, withSpring, runOnJS } from 'react-native-reanimated';

export function CartSheet({ onClose }: { onClose: () => void }) {
  const y = useSharedValue(0);
  const pan = Gesture.Pan()
    .onChange((e) => { y.value = Math.max(0, y.value + e.changeY); })               // UI thread
    .onEnd((e) => {
      if (y.value > 200 || e.velocityY > 1200) runOnJS(onClose)();                   // hop to JS only once
      else y.value = withSpring(0);
    });
  const style = useAnimatedStyle(() => ({ transform: [{ translateY: y.value }] }));
  return <GestureDetector gesture={pan}><Animated.View style={[styles.sheet, style]}>{/* … */}</Animated.View></GestureDetector>;
}
```

### Defer heavy work until the transition finishes
```tsx
function OrderHistoryScreen() {
  const [ready, setReady] = useState(false);
  useFocusEffect(useCallback(() => {
    const task = InteractionManager.runAfterInteractions(() => setReady(true));     // after push animation
    return () => task.cancel();
  }, []));
  return ready ? <OrderList /> : <OrderListSkeleton />;
}
```

### Leak-free subscriptions
```tsx
useEffect(() => {
  const sub = AppState.addEventListener('change', onAppState);
  const unsubNet = NetInfo.addEventListener(onNet);
  const id = setInterval(pollEta, 10_000);
  const off = realtime.subscribe(`order:${orderId}`, onOrderEvent);
  return () => { sub.remove(); unsubNet(); clearInterval(id); off(); };            // ✅ cleanup everything
}, [orderId]);
```

### Navigation setup for performance
```tsx
import { enableFreeze } from 'react-native-screens';
enableFreeze(true);                                          // inactive screens don't re-render
const Stack = createNativeStackNavigator();                  // native transitions
const Tabs = createBottomTabNavigator();
<Tabs.Navigator screenOptions={{ lazy: true, freezeOnBlur: true }}>{/* … */}</Tabs.Navigator>
// Flows: after successful checkout → navigation.reset({ index: 0, routes: [{ name: 'Home' }, { name: 'OrderSuccess' }] })
```

### Strip console logs in release (babel)
```js
// babel.config.js
module.exports = (api) => {
  api.cache(true);
  return { presets: ['babel-preset-expo'], env: { production: { plugins: ['transform-remove-console'] } } };
};
```

### Track frozen/slow frames in production (Sentry RN)
```ts
Sentry.init({ dsn, tracesSampleRate: 0.1, enableNativeFramesTracking: true });     // slow & frozen frames per screen
// Dashboard: "Menu screen frozen frames > 1%" on Android 10, Redmi 9 → investigate
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you find whether jank comes from the JS thread or the UI thread?**
A1: Use the Perf Monitor or a profiler to look at JS FPS and UI FPS separately during the janky interaction, in a release build on a low-end device. If JS FPS drops while UI FPS stays high, the JS thread is overloaded (re-renders, heavy logic, JS-driven animations). Profile with the React DevTools Profiler and the Hermes sampling profiler. If UI FPS drops, the native side is overloaded (complex view hierarchies, overdraw, image decoding, layout-heavy animations). Use Android Studio/Perfetto or Xcode Instruments. Production metrics (slow and frozen frames per screen) help prioritize.

**Q2: How do you reduce unnecessary re-renders in a React Native app?**
A2: Colocate state close to where it's used. Subscribe to global stores via fine-grained selectors. Split and memoize context values. Wrap expensive or list-row components in `React.memo` with stable props, using `useCallback`/`useMemo` for callbacks and objects passed to them (or adopt the React Compiler). Compute derived data with memoized selectors instead of effects. Keep fast-changing values (scroll, animation) in shared values or refs rather than React state. Freeze inactive screens. Verify with the Profiler.

**Q3: Why use Reanimated instead of the Animated API with setState?**
A3: Driving animations through React state or JS-thread Animated updates every frame from the JS thread, so any JS work (renders, network parsing) causes stutter, and gestures lag behind the finger. Reanimated runs animation logic as worklets on the UI thread using shared values, and combines with native gesture recognizers, so animations and gesture-driven UI stay at 60 or 120 fps even when JS is busy. The Animated API with `useNativeDriver: true` also offloads simple transform and opacity animations, but is less flexible.

**Q4: How do you find and fix memory leaks?**
A4: Reproduce a long session (navigate back and forth, scroll feeds) while monitoring memory in Android Studio Profiler or Xcode Instruments, and take Hermes heap snapshots before and after to compare retained objects. Common causes are unremoved listeners and subscriptions, uncleared intervals, global caches holding screen data or closures, unbounded arrays, oversized images and ever-growing navigation stacks. Fix with cleanup functions in every subscribing effect, bounded LRU caches, image downsampling, and resetting navigation for completed flows. LeakCanary helps for native Android leaks.

**Q5: What's your checklist for a smooth screen on low-end Android?**
A5: Lean view hierarchy, a recycled list with memoized lightweight cells, properly sized and cached images, selector-based state subscriptions, no heavy work during transitions (defer with InteractionManager), animations and gestures on the UI thread, MMKV for synchronous reads, no console logging in release, native-stack navigation with frozen inactive screens, paginated data from a local DB rather than huge in-memory arrays, and measuring FPS, slow frames and memory in release builds with budgets in CI.

---

## 🔷 Trade-offs
✅ Memoization: fewer renders — ❌ added complexity & memory if overused (React Compiler helps).
✅ UI-thread animations: smooth — ❌ worklet constraints, harder debugging.
✅ Freezing screens: less background work — ❌ frozen screens show stale data until focused (refresh on focus).
✅ Profiling discipline: catches regressions — ❌ requires device lab/CI time.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Frame budget | Time per frame (16.7 ms @60fps) | हर frame का समय |
| JS thread | Runs React/JS logic | JS चलाने वाला धागा |
| UI thread | Draws native views | drawing वाला धागा |
| Jank | Visible stutter | झटका |
| Re-render | Component renders again | दोबारा render |
| Selector | Pick specific store slice | store का हिस्सा चुनना |
| Worklet | Function running on UI thread | UI thread पर चलने वाला function |
| Overdraw | Drawing pixels multiple times | एक pixel कई बार बनाना |
| Memory leak | Memory never released | memory वापस न होना |
| ANR | App Not Responding (Android) | ऐप जवाब नहीं दे रहा |

---

## ⚡ 3-Line Summary
**English:**
1. Diagnose by thread: JS fps (renders/logic) vs UI fps (views/images/layout), in release builds on low-end devices with profilers.
2. JS side: colocated state, selectors, memo/React Compiler, deferred work, MMKV, no console in release; UI side: lean views, sized images, UI-thread animations (Reanimated/native driver).
3. Navigation and memory: native-stack, lazy/frozen screens, cleanup every subscription, bounded caches; monitor slow/frozen frames and ANRs in production.

**Hindi:**
1. धागे से पहचानो: JS fps (render/logic) बनाम UI fps (views/images), release में सस्ते फ़ोन पर।
2. JS: state पास में, selectors, memo, काम टालो, MMKV; UI: हल्के views, सही images, Reanimated animations।
3. Navigation और memory: native-stack, freeze screens, हर subscription का cleanup; production में slow frames और ANR देखो।

---

## ➡️ Next Topic Suggestion
**M15. Mobile Security (Secure Storage, SSL Pinning, Root/Jailbreak)** — A fast app also has to be a safe one. Next: the mobile threat model, secure storage, transport security and certificate pinning, root and jailbreak detection, app attestation, and keeping secrets out of the binary.
