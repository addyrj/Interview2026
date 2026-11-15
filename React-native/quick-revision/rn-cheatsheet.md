# React Native — Core Cheatsheet
# Components, Styling, Hooks, Lists, Networking, Storage, Animations, Performance, New Architecture
# Quick Revision

> Condensed from folders 01-09 and 07b-networking. Notes target Expo SDK 52 (some SDK 54) / React Native 0.76-0.81. Check current docs — APIs change between SDKs. Library versions (React Query v5, MMKV v3 vs v4, Reanimated v3) change: verify before copying code.

---

## 🏗️ How React Native Works (01-basics)

```
JS Thread     -> your code        UI Thread     -> rendering, touches
Native Thread -> device APIs      Never block the UI thread
Old: async JSON Bridge            New: JSI (direct C++) + Fabric + TurboModules
```

- **JSI:** C++ layer; JS holds native object references directly, no JSON, sync calls possible. TurboModules, Fabric, Reanimated, MMKV sit on it. हिंदी: JSI से JS सीधे native से बात करता है।
- **Hermes:** Pre-compiles JS to bytecode at build time (AOT); faster startup and lower memory (note 07 says 50-70% faster start than JSC); default since RN 0.64. Does not fix bad re-renders. हिंदी: Hermes startup तेज़ करता है, re-render की समस्या नहीं।
- **Metro:** Dev bundler server with Fast Refresh; prod bundles JS into the app. हिंदी: Metro JS को bundle करता है।

---

## 🧩 Core Components (02-core-components)

| Component | Gist | हिंदी |
|---|---|---|
| `View` | Basic layout container (UIView/ViewGroup); default direction column; text must be inside `<Text>` | बुनियादी container |
| `Text` | Only way to show text; nested Text inherits style; `numberOfLines`, `onPress` | text सिर्फ Text में |
| `Image` | `source={{uri}}` or `require()`; set explicit width + height or it is invisible; `resizeMode` cover/contain | size ज़रूर दो |
| `ImageBackground` | Image + children on top; `style` = container, `imageStyle` = image | image के ऊपर children |
| `TextInput` | Use `onChangeText`, match `keyboardType`; wrap forms in KeyboardAvoidingView | input के लिए |
| `ScrollView` | Renders ALL children at once; small content only | छोटे content के लिए |
| `FlatList` | Virtualized; renders visible items + buffer | लंबी list के लिए |
| `SectionList` | Virtualized with grouped sections: `[{ title, data }]`, `renderSectionHeader` | grouped data |
| `VirtualizedList` | Base of FlatList/SectionList; for non-array data | FlatList का base |
| `Pressable` | Modern touchable: `pressed` state, `android_ripple`, `hitSlop` | नया touch component |
| `TouchableOpacity` | Fades on press; Pressable is the modern alternative | पुराना, चलता है |
| `TouchableNativeFeedback` | Android-only ripple; prefer Pressable + `android_ripple` | सिर्फ Android |
| `Button` | Simplest; no `style` prop; use Pressable for real apps | customise नहीं होता |
| `Switch` | Controlled toggle: update state in `onValueChange` | on/off toggle |
| `Slider` | Removed from core; use `@react-native-community/slider`; API call in `onSlidingComplete` | अलग package |
| `ActivityIndicator` | Native spinner; reset loading in `finally` | loading spinner |
| `Modal` | Overlay; set `onRequestClose` (Android back); use navigation for full screens | overlay dialog |
| `Alert` | `Alert.alert` native dialog; Android max 3 buttons; `prompt` iOS-only | native dialog |
| `StatusBar` | Icon colour / hide; `light-content` = white icons | status bar |
| `SafeAreaView` | Built-in is iOS-only; use `react-native-safe-area-context` for both | notch से बचाव |
| `KeyboardAvoidingView` | `behavior={Platform.OS === 'ios' ? 'padding' : 'height'}` | keyboard ढके नहीं |
| `RefreshControl` | Pull-to-refresh; `tintColor` iOS, `colors` Android | pull to refresh |

**हिंदी:** Button की जगह Pressable से custom button बनाओ, `pressed` से style बदलो।

---

## 🎨 Styling & Flexbox (03-styling)

- **Gist:** Styles are JS objects, no CSS. Arrays merge, last one wins. `StyleSheet.create` at module level; `useMemo` for dynamic styles. हिंदी: Styling JS objects से होती है, CSS नहीं।
- **Flexbox:** Default `flexDirection` is column; `justifyContent` = main axis, `alignItems` = cross axis; `flex` shares leftover space. No grid, float, cascade or CSS units. हिंदी: Default direction column है।
- **Dimensions:** Prefer `useWindowDimensions` (re-renders on rotation) over `Dimensions.get('window')`; `window` = usable area, `screen` = full screen. हिंदी: Rotation पर auto-update।
- **Responsive:** flex, percentages, `aspectRatio`, breakpoints; safe-area insets; limit font scaling.
- **Platform:** `Platform.OS` / `Platform.select` for small differences; `.ios.js` / `.android.js` (order: platform, `.native`, default) for big ones.
- **Shadows:** iOS `shadow*` props (need a background colour; no `overflow: 'hidden'` on that view), Android `elevation`.
- **Fonts:** Expo `useFonts`, CLI `react-native-asset`; iOS uses PostScript names. **Icons:** `@expo/vector-icons`; CLI needs native font linking else `?` shows.
- **Libraries:** `styled-components/native`; NativeWind = Tailwind via `className` (needs Babel, Metro, `global.css`).
- **Absolute:** removed from flex flow; `StyleSheet.absoluteFill` to cover.

```jsx
import React from 'react';
import { View, Text, StyleSheet, Platform, useWindowDimensions } from 'react-native';

export default function ShadowCard() {
  const { width } = useWindowDimensions();
  return (
    <View style={styles.screen}>
      <View style={[styles.card, { width: width - 48 }]}>
        <Text style={styles.title}>Biryani House</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#f2f2f2', padding: 24, justifyContent: 'center' },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.2,
        shadowRadius: 6,
      },
      android: { elevation: 4 },
    }),
  },
  title: { fontSize: 18, fontWeight: '700' },
});
```

**हिंदी:** Shadow के लिए iOS में `shadow*`, Android में `elevation`; `Platform.select` से जोड़ो।

---

## 🪝 Hooks & State (05-hooks-state)

| Tool | Gist | हिंदी |
|---|---|---|
| All React hooks | Same React, so core hooks work unchanged; mind mobile lifecycle (background does not unmount): `AppState`, `useFocusEffect` | सारे hooks चलते हैं |
| RN hooks | `useWindowDimensions`, `useColorScheme` | RN के extra hooks |
| `useState` | Updates batched; use functional updates; never mutate | कभी mutate मत करो |
| `useEffect` | Return cleanup; no async effect function; watch stale closures | cleanup ज़रूर |
| `useRef` | Persistent box, no re-render; native handles, timer ids | re-render नहीं करता |
| `useContext` | Avoids prop drilling; all consumers re-render on change: memoise, split contexts | prop drilling से बचाव |
| Custom hooks | `useX` reuses logic; each call has its own state; always cleanup | logic reuse |
| Zustand | `create()` for state + actions, no Provider; use selectors; `persist` + MMKV | हल्का global state |
| Redux Toolkit | `configureStore` + `createSlice` + thunks; `Provider`, `useSelector`, `dispatch` | बड़े apps के लिए |
| React Query | Server state: cache, retry, refetch; link `focusManager` to AppState, `onlineManager` to NetInfo; v5 object syntax, `gcTime`, `isPending` | server data |

**हिंदी:** `useEffect` में cleanup return करो और timer में functional update रखो।

---

## 📜 Lists (FlatList & friends)

- **Which one:** ScrollView = all children rendered (small content); FlatList = virtualized (long lists); SectionList = grouped + sticky headers. Never nest FlatList inside ScrollView. हिंदी: लंबी list = FlatList।
- **Perf recipe:** `React.memo` row, `useCallback` on `renderItem`, stable `keyExtractor` (never index / random), `getItemLayout` only for fixed-height rows (wrong values cause jumps).
- **Window tuning:** `initialNumToRender`, `maxToRenderPerBatch`, `windowSize` (smaller = less memory, risk of blank areas); `removeClippedSubviews` helps Android, can blank on iOS. Tune on a release build on a low-end phone.
- **Extras:** `ListEmptyComponent`, `refreshControl`, `onEndReached` + `onEndReachedThreshold` (infinite scroll); changing `numColumns` needs a new `key`.

```jsx
import React, { useCallback, memo } from 'react';
import { FlatList, View, Text, Image, StyleSheet } from 'react-native';

const RestaurantCard = memo(function RestaurantCard({ item }) {
  return (
    <View style={styles.card}>
      <Image source={{ uri: item.imageUrl }} style={styles.image} resizeMode="cover" />
      <Text style={styles.name}>{item.name}</Text>
    </View>
  );
});

export default function RestaurantList({ restaurants }) {
  const keyExtractor = useCallback((item) => item.id, []);
  const renderItem = useCallback(({ item }) => <RestaurantCard item={item} />, []);
  const ITEM_HEIGHT = 200;
  const getItemLayout = useCallback(
    (data, index) => ({ length: ITEM_HEIGHT, offset: ITEM_HEIGHT * index, index }),
    []
  );

  return (
    <FlatList
      data={restaurants}
      keyExtractor={keyExtractor}
      renderItem={renderItem}
      getItemLayout={getItemLayout}
      initialNumToRender={8}
      maxToRenderPerBatch={10}
      windowSize={10}
      removeClippedSubviews={true}
    />
  );
}

const styles = StyleSheet.create({
  card: { height: 200, marginHorizontal: 16, marginVertical: 8, borderRadius: 12, overflow: 'hidden' },
  image: { width: '100%', height: 130 },
  name: { fontSize: 16, fontWeight: '700', padding: 8 },
});
```

**हिंदी:** Row को memo करो, key में id रखो, fixed height हो तभी `getItemLayout` दो।

---

## 🌐 Networking (07b-networking)

| Topic | Gist | हिंदी |
|---|---|---|
| `fetch` | Built-in; rejects only on network failure, so check `res.ok`; `AbortController` for timeout/cancel | `res.ok` ज़रूर जाँचो |
| Axios | Auto JSON, throws on errors, timeouts, interceptors; one instance; never use it for the refresh call | interceptors में token |
| Error handling | Classify network / timeout / 4xx / 5xx / parse; retry only safe cases with backoff; never retry payments blindly | payment retry मत करो |
| Loading states | One `status` instead of many booleans; render exactly one of loading/error/empty/success; guard stale responses | एक status रखो |
| Offline | Cache + show first; queue offline actions, flush when online; idempotency keys + TTL | offline queue |
| NetInfo | Check `isConnected` and `isInternetReachable !== false`; unsubscribe | दोनों जाँचो |
| Background fetch | OS runs short task, timing not guaranteed; use push for urgent | समय की गारंटी नहीं |
| WebSocket | Close on unmount, check `readyState`, reconnect with backoff; unreliable in background | unmount पर close |
| GraphQL | Apollo Client; check the `errors` array even on HTTP 200 | HTTP 200 पर भी errors |
| Upload | `FormData` with `{uri, name, type}`; axios for progress; presigned URLs for big videos | multipart upload |
| Download | `createDownloadResumable`; save in `documentDirectory` | progress के साथ |
| Cert pinning | Trust only your server key hash; ship a backup pin; test on a dev build, not Expo Go | backup pin रखो |

```jsx
import React, { useEffect, useState } from 'react';
import { Text, FlatList, ActivityIndicator } from 'react-native';

export default function FetchBasic() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    const load = async () => {
      try {
        const res = await fetch('https://jsonplaceholder.typicode.com/posts?_limit=10', {
          signal: controller.signal,
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        setData(await res.json());
      } catch (e) {
        if (e.name !== 'AbortError') setError(e.message);
      } finally {
        setLoading(false);
      }
    };
    load();
    return () => controller.abort();
  }, []);

  if (loading) return <ActivityIndicator style={{ marginTop: 40 }} />;
  if (error) return <Text>Error: {error}</Text>;

  return (
    <FlatList
      data={data}
      keyExtractor={(i) => String(i.id)}
      renderItem={({ item }) => <Text style={{ padding: 12 }}>{item.title}</Text>}
    />
  );
}
```

**हिंदी:** fetch 404/500 पर throw नहीं करता, इसलिए `res.ok` देखो और unmount पर abort करो।

---

## 💾 Storage

| Store | Gist | Use for |
|---|---|---|
| AsyncStorage | Async, string-only, Expo Go OK, slower; `JSON.stringify/parse`; never secrets | simple apps |
| MMKV | Synchronous, typed, optional encryption via JSI; 10-30x faster per the notes; needs a development build (not Expo Go); create ONE instance; check v3 vs v4 API | tokens (see SecureStore), prefs, hot small data |
| SecureStore | Keychain/Keystore, OS-encrypted; small secrets only; delete on logout; iOS may keep data after uninstall | tokens, PIN hashes |
| SQLite (`expo-sqlite`) | Single-file SQL DB; parameter binding, transactions, `PRAGMA user_version` migrations | structured offline data |
| WatermelonDB / Realm | Larger local databases | big datasets |

**हिंदी:** छोटा data = AsyncStorage/MMKV, secret = SecureStore, बड़ा structured data = SQLite।

```ts
// Zustand persisted in MMKV (needs a development build)
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { MMKV } from 'react-native-mmkv';

const storage = new MMKV({ id: 'zustand-store' });

const mmkvStorage = {
  getItem: (name: string) => storage.getString(name) ?? null,
  setItem: (name: string, value: string) => storage.set(name, value),
  removeItem: (name: string) => storage.delete(name),
};

type AppStore = {
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
};

export const useAppStore = create<AppStore>()(
  persist(
    (set) => ({
      theme: 'system',
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'app-store',
      storage: createJSONStorage(() => mmkvStorage),
      partialize: (state) => ({ theme: state.theme }),
    }
  )
);
```

---

## 🎬 Animations (07-animations)

- **Animated API:** `Animated.Value` drives styles without re-renders; keep it in `useRef` (or `useAnimatedValue`, RN 0.71+). `timing` (duration + easing), `spring` (physics, no duration), `decay` (velocity, no target); compose with `sequence` (sum of time), `parallel` (max), `stagger`. Start only the wrapper. हिंदी: Animated.Value बिना re-render के style चलाता है।
- **Native driver:** `useNativeDriver: true` for transform/opacity (60fps on UI thread); not for colour/layout; never mix drivers on one value.
- **Interpolation:** map one range to another; `extrapolate: 'clamp'` avoids overshoot.
- **Reanimated v3:** All animations on the UI thread via JSI: `useSharedValue`, `useAnimatedStyle` (worklet), `withTiming`, `withSpring`, `withSequence`, `withDelay`, `withRepeat(-1 = infinite)`; `runOnJS` to reach setState; `cancelAnimation` to stop. हिंदी: Reanimated UI thread पर चलता है।
- **Gesture Handler:** wrap root in `GestureHandlerRootView`; `GestureDetector` + `Gesture.Pan()` / Pinch; compose with Simultaneous / Exclusive / Race; finish with `withSpring` (snap) or `withDecay` (fling).
- **Others:** Lottie (JSON vector, keep files small); skeleton loaders (animate transform/opacity); shared element transition is experimental (needs native-stack + New Architecture); navigator `animation` / `presentation` options.
- **Accessibility:** respect Reduce Motion.

```jsx
// Animated: slide with native driver
import React, { useRef } from 'react';
import { Animated, Button, Easing, View } from 'react-native';

export default function TimingBasic() {
  const x = useRef(new Animated.Value(0)).current;

  const slide = () => {
    Animated.timing(x, {
      toValue: 200,
      duration: 500,
      easing: Easing.out(Easing.cubic),
      useNativeDriver: true,
    }).start();
  };

  return (
    <View style={{ flex: 1, justifyContent: 'center', padding: 24, gap: 20 }}>
      <Animated.View style={{ width: 80, height: 80, backgroundColor: '#e23744', transform: [{ translateX: x }] }} />
      <Button title="Slide" onPress={slide} />
    </View>
  );
}
```

---

## ⚡ Performance (08-performance)

- **Method:** Measure first on a **release build** and a low-end device. Most lag = re-renders, big lists, big images, or a blocked JS thread. Fix the biggest cause, re-measure. हिंदी: पहले release build पर मापो।
- **Tools:** Perf Monitor (UI FPS vs JS FPS shows which thread is slow), React Profiler (renders), Hermes profiler (JS), Instruments / Android Studio (native). Flipper is legacy: use React Native DevTools / Reactotron; never ship it.
- **Re-renders:** `React.memo` + stable props, colocate state, split Context. `useCallback` / `useMemo` only help with memoized children or expensive work; wrong deps = stale closures.
- **Lists:** see Lists section (memo rows, `keyExtractor`, `getItemLayout`, window tuning).
- **Images:** correctly sized WebP from a CDN, cache, placeholders; decoded memory matters more than file size; `expo-image` is the modern default (CLI alternative in notes: `react-native-fast-image`).
- **Startup:** Hermes (default); inline requires delay a module until first use (don't inline modules with import-time side effects); RAM bundles are a legacy JSC-era optimisation, usually unneeded with Hermes; lazy screens.

---

## 🚀 New Architecture & Advanced (01 + 09-advanced)

- **What:** JSI + Fabric + TurboModules + Codegen; no async JSON bridge. Gives lazy module loading, sync access, concurrent React features, type safety. हिंदी: पुराने Bridge की जगह JSI।
- **Default since (notes disagree, verify):** 01-basics says RN 0.74+ (and Expo SDK 50+ for new projects); 09-advanced says RN 0.76+ / SDK 52+. Check the current docs for your SDK.
- **Enable:** Expo `app.json` `"newArchEnabled": true`, then rebuild (`npx expo run:android`); CLI: `newArchEnabled=true` in `android/gradle.properties` (+ iOS Podfile). Check every third-party library supports it; libs that use the old bridge APIs may break in Bridgeless mode.
- **Fabric:** C++ shadow tree + Yoga layout, then native mount; sync layout reads; view flattening (`collapsable={false}` when needed).
- **TurboModules:** lazy, JSI-based, type-safe. Write `NativeXxx.ts` spec; Codegen (`codegenConfig` in package.json) generates native interfaces; missing methods fail at compile time. Keep sync methods tiny.
- **Native modules:** Kotlin/Swift for proprietary SDKs; return Promises, always resolve or reject; prefer community packages / Expo SDK first; iOS `RCT_EXPORT_MODULE` or Expo Modules API.
- **C++:** share logic across platforms via JSI; risky for memory bugs.
- **Also in folder 09:** react-native-web (`Platform.OS` / `.web.js`), monorepos (one copy of React), micro frontends (Re.Pack + Module Federation, JS-only remotes), Jest + RNTL, Detox E2E (native build, not Expo Go), accessibility (labels, roles, 44-48 targets, TalkBack/VoiceOver), i18n (i18next, `Intl`), TypeScript (`tsc --noEmit`, prefer `unknown`), WebView (whitelist URLs, `postMessage`), Stripe (server PaymentIntent, confirm via webhook, dev build).

```ts
// NativeDeviceInfoModule.ts: TurboModule spec
import type { TurboModule } from 'react-native';
import { TurboModuleRegistry } from 'react-native';

export interface Spec extends TurboModule {
  getDeviceName(): string;
  getBatteryLevel(): Promise<number>;
  logEvent(name: string, value: number): void;
}

export default TurboModuleRegistry.getEnforcing<Spec>('DeviceInfoModule');
```

