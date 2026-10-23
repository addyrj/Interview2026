# React Native — Top 50 Interview Q&A
# Quick Revision Cheatsheet
# 3-5 Year Experience Level

---

## 🏗️ Architecture (8 Q)

**Q1. What is React Native?**
Cross-platform mobile framework using JavaScript/TypeScript that renders actual native UI components (not WebView). Write once, run on Android + iOS. Built by Meta.

**Q2. How does React Native communicate between JS and Native?**
Old: Bridge (JSON serialization, async). New Architecture: JSI (JavaScript Interface) — direct C++ references, synchronous possible, no JSON.

**Q3. What are the 3 threads in React Native?**
JS Thread (your code), UI Thread/Main Thread (renders native components, handles touches), Native Modules Thread (device APIs like camera, location).

**Q4. What is the New Architecture?**
JSI (Bridge replacement) + Fabric (new synchronous renderer) + TurboModules (lazy-loaded native modules). Enabled in RN 0.74+ by default. Enables React 18 Concurrent Mode.

**Q5. What is Hermes?**
Meta's JS engine for React Native. Pre-compiles JS to bytecode at build time (AOT) — 50-70% faster app startup vs JSC. Default since RN 0.64. Especially impactful on budget Android phones.

**Q6. What is Metro Bundler?**
React Native's JavaScript bundler (like Webpack for web). Dev: runs as local server, enables Fast Refresh. Prod: transforms TypeScript → JS, bundles all files into `index.android.bundle`.

**Q7. What is JSI?**
JavaScript Interface — New Architecture's direct C++ bridge. JS holds native object references directly. No JSON serialization. Synchronous calls possible. Powers TurboModules, Fabric, Reanimated v3.

**Q8. Expo vs React Native CLI?**
Expo: no native setup, EAS cloud builds (iOS on Windows!), 80+ pre-built modules, OTA updates. CLI: full native control, custom C++/Java/Swift, brownfield. Expo is the default for new projects.

---

## 🧩 Core Components (8 Q)

**Q9. Name 10 core React Native components.**
View, Text, Image, TextInput, ScrollView, FlatList, SectionList, Pressable, Modal, SafeAreaView, ActivityIndicator, StatusBar, KeyboardAvoidingView, Switch.

**Q10. FlatList vs ScrollView — when to use each?**
ScrollView: renders ALL children immediately — good for < 30 items (forms, settings, detail screens). FlatList: virtualized — renders only visible items — use for any dynamic list (feed, search results, 50+ items).

**Q11. What are required FlatList props?**
`data` (array), `renderItem` (function returning component), `keyExtractor` (function returning unique string key per item).

**Q12. Why is using array index as `keyExtractor` bad?**
When list items reorder/filter, React uses keys to match old and new items. Index-based keys cause wrong items to animate/update. Use stable unique IDs (`item.id`).

**Q13. How does Image work in React Native? Why does it need explicit width/height?**
`<Image source={{ uri: '...' }}>` for network, `source={require('./img.png')}` for local. Native ImageView has no intrinsic size — browser calculates it from metadata, native doesn't wait. Always set `style={{ width, height }}`.

**Q14. What is `Pressable` vs `TouchableOpacity`?**
`Pressable` is modern (RN 0.63+) with full control: `onPress`, `onLongPress`, `onPressIn`, `onPressOut`, plus `style={({ pressed }) => ...}` for per-state styles. `TouchableOpacity` is older — adds opacity feedback only.

**Q15. What is `KeyboardAvoidingView`?**
Adjusts its height/padding when the keyboard appears, preventing the keyboard from covering input fields. Use `behavior={Platform.OS === 'ios' ? 'padding' : 'height'}`.

**Q16. What is SafeAreaView?**
Renders content within the safe area — avoids notch, Dynamic Island, rounded corners (iOS), and Android cutouts. Use it as the root container for each screen.

---

## 🎨 Styling (5 Q)

**Q17. How is React Native styling different from CSS?**
No CSS files — use `StyleSheet.create({})` with JS objects. camelCase (`fontSize` not `font-size`). No CSS units (px, em, rem) — just numbers. No `float`. Flexbox is column-first by default (unlike web's row-first). No class names.

**Q18. What is `StyleSheet.create()` and why use it?**
Creates an immutable style object with integer IDs. Benefits: validates styles at build time (TypeScript), sends styles to native once (not every render), enables native optimization. Prefer it over inline objects.

**Q19. How is Flexbox different in React Native vs CSS?**
Default `flexDirection`: RN = `'column'` (top-to-bottom), CSS = `'row'` (left-to-right). Default `alignContent`: RN = `'flex-start'`, CSS = `'normal'`. No `flex-wrap` by default in RN. `flex` in RN is a single number (like `flex-grow`).

**Q20. How do you add shadows cross-platform?**
Android: `elevation: 4` (Material Design, single number). iOS: `shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.15, shadowRadius: 4`. Use `Platform.select` to apply correct properties.

**Q21. What is Platform.select?**
`Platform.select({ ios: valueA, android: valueB, default: fallback })` — picks value for current platform. Common for shadow styles, `KeyboardAvoidingView` behavior, status bar height.

---

## 🗺️ Navigation (5 Q)

**Q22. What is React Navigation?**
Community library for navigation in React Native. Stack Navigator (push/pop screens), Tab Navigator (bottom tabs), Drawer Navigator (side menu). Provides `navigation` and `route` props to screen components.

**Q23. How do you pass data between screens?**
`navigation.navigate('ScreenName', { key: value })` → receive via `route.params.key` or `useRoute().params.key`. Params are in-memory objects — any JS type works. Don't pass large objects or functions.

**Q24. What is `navigation.replace` vs `navigation.navigate`?**
`navigate`: pushes new screen onto stack (back button available). `replace`: replaces current screen (no back button — used after login/OTP so user can't go back). `push`: always pushes even if screen exists in stack.

**Q25. What is Expo Router?**
File-system based routing for React Native (like Next.js for web). Files in `app/` folder become routes. `app/home.tsx` → `/home`. Uses Expo Go / Development Builds. Good for new Expo projects targeting web + native.

**Q26. What is deep linking?**
Opening a specific screen via a URL: `myapp://product/123` or `https://myapp.com/product/123` (Universal Links/App Links). Configured in app.json (Expo) or AndroidManifest/Info.plist (CLI). React Navigation has `linking` prop for URL → screen mapping.

---

## 🪝 Hooks + State (5 Q)

**Q27. Do React hooks work the same in React Native?**
Yes — `useState`, `useEffect`, `useRef`, `useContext`, `useMemo`, `useCallback`, custom hooks all work identically. RN extends React but doesn't modify the core hook API.

**Q28. What is AsyncStorage?**
Key-value storage for React Native (like `localStorage` for web). Async API: `await AsyncStorage.setItem(key, value)`. Stores strings only (JSON.stringify for objects). Persists across app restarts. Slower than MMKV.

**Q29. What is MMKV?**
Tencent's high-performance key-value storage. Synchronous (unlike AsyncStorage), 10x faster (uses mmap), supports TypeScript types. Use for: session tokens, user preferences, any frequently-read data.

**Q30. What is Zustand?**
Minimal state management library (alternative to Redux). Simple: `create((set) => ({ count: 0, increment: () => set(state => ({ count: state.count + 1 })) }))`. No boilerplate, works with hooks, supports middleware.

**Q31. useWindowDimensions vs Dimensions.get()?**
`useWindowDimensions()`: hook, re-renders component when screen size changes (orientation, foldable). `Dimensions.get('window')`: static snapshot, doesn't trigger re-render. Always prefer `useWindowDimensions` in components.

---

## ✨ Animations (4 Q)

**Q32. What is `useNativeDriver`?**
`useNativeDriver: true` in Animated API sends animation to the UI thread — runs at 60fps without involving JS thread. Supported: `transform`, `opacity`. NOT supported: `width`, `height`, `backgroundColor` (use Reanimated v3 for those).

**Q33. Animated.timing vs Animated.spring?**
`timing`: duration-based, linear/eased. `spring`: physics-based, bouncy (overshoots and settles). Use spring for interactive gestures (feels natural), timing for predictable UI transitions.

**Q34. What is Reanimated v3?**
Community animation library using JSI to run animations entirely on the UI thread. Key APIs: `useSharedValue` (C++ stored value), `useAnimatedStyle` (computed on UI thread), `withTiming/withSpring`. Supports ALL CSS properties on UI thread. Required for complex gesture + animation combos.

**Q35. What is react-native-gesture-handler?**
Community library for gesture recognition that runs on the UI thread (not JS thread). `Gesture.Pan()`, `Gesture.Tap()`, `Gesture.Pinch()`. Works with Reanimated v3 for gesture-driven animations. Must wrap app in `GestureHandlerRootView`.

---

## ⚡ Performance (4 Q)

**Q36. What are common causes of dropped frames in RN?**
JS Thread busy during animations (fix: `useNativeDriver: true` or Reanimated), unnecessary re-renders (fix: `React.memo`, `useCallback`), slow FlatList (fix: `React.memo` on items, `keyExtractor`, `getItemLayout`), large images (fix: FastImage, proper sizing).

**Q37. How do you optimize FlatList?**
`React.memo` on renderItem component, `useCallback` on `renderItem` function, stable `keyExtractor` (not index), `getItemLayout` for fixed-height items, `removeClippedSubviews` on Android, `initialNumToRender`, `windowSize`.

**Q38. What is `InteractionManager.runAfterInteractions`?**
Defers heavy work (parsing, state updates) until after animations/interactions complete. Prevents janky transitions when navigating to a screen that loads data.

**Q39. How do you reduce app startup time?**
Hermes bytecode (2x faster startup), lazy imports (dynamic `import()`), defer non-critical operations with `InteractionManager`, reduce initial screen complexity, `useMemo` for heavy computations, proper image sizing.

---

## 📱 Device Features (3 Q)

**Q40. How do permissions work in React Native?**
Two steps: (1) Declare in `AndroidManifest.xml` (Android) / `Info.plist` (iOS). (2) Request at runtime when feature is needed. Expo: declare in `app.json`, use `expo-*` modules. Status: `granted`, `denied`, `blocked` (need Settings redirect), `unavailable`.

**Q41. When is the permission `blocked`?**
User denied twice on iOS or checked "Never ask again" on Android. `request()` does nothing. Only fix: redirect user to Settings with `Linking.openSettings()`. Re-check status when app comes back from background via `AppState`.

**Q42. What is `expo-location` vs `react-native-geolocation-service`?**
`expo-location`: Expo SDK, no native config needed, unified API for foreground + background location. `react-native-geolocation-service`: CLI-only, wraps native GPS APIs, faster for high-frequency GPS, used for real-time tracking.

---

## 🚀 Publishing (8 Q)

**Q43. What is a Keystore file (Android)?**
Keystore is a file containing the cryptographic key used to sign Android apps. Required for Play Store. NEVER LOSE IT — you can't update your app without the original keystore. Store in secure backup (AWS, 1Password). Generated once: `keytool -genkey -v -keystore release.keystore`.

**Q44. What is AAB vs APK?**
APK: complete Android package, runs on any device, larger. AAB (Android App Bundle): upload format for Play Store — Google optimizes and delivers device-specific split APKs. AAB: 20-50% smaller download for users. Play Store requires AAB for new apps.

**Q45. What is EAS Build?**
Expo Application Services Build — cloud build service. `eas build --platform android/ios`. Handles Android signing (keystore) and iOS signing (certificates). Runs Xcode and Android Studio on Expo's cloud servers — iOS builds work on Windows/Linux!

**Q46. What are the required iOS certificates?**
(1) Apple Developer Account ($99/year). (2) Developer Certificate (signs development builds). (3) Distribution Certificate (signs App Store builds). (4) Provisioning Profile (links app ID + certificate + device list). Managed automatically by EAS Build or Xcode's auto-signing.

**Q47. What is TestFlight?**
Apple's beta testing platform. Upload IPA to App Store Connect → distribute to up to 10,000 testers. Internal testers: instant. External testers: requires Beta App Review (1-3 days). TestFlight build expires after 90 days.

**Q48. What is OTA Update?**
Over-The-Air update — update the JS bundle without going through Play Store/App Store review. `eas update` (Expo) pushes new bundle; app downloads it on next launch. Only JS changes (no native code changes). Instant delivery vs 1-7 days for store review.

**Q49. What is the App Store review process?**
Submit IPA → Apple Review Team checks: (1) No crashes. (2) Follows App Store Guidelines. (3) All metadata (screenshots, description). First submission: 1-3 days typically. Rejections: fix → resubmit. Common rejections: missing privacy policy, incomplete info, demo credentials not provided.

**Q50. What is `versionCode` (Android) and `buildNumber` (iOS)?**
`versionCode` (Android): integer, must increment with every Play Store upload. `buildNumber` (iOS): numeric string, must increment for every TestFlight/App Store upload. `version` (both): user-visible version (e.g., "2.1.0"). Rule: can reuse `version` but `versionCode`/`buildNumber` must always increase.

---

## 📋 Quick Reference Card

```
ELEMENT MAPPING:
div → View       | p/h1/h2/h3 → Text    | img → Image
button → Pressable | input → TextInput  | ul+li → FlatList
<a> → Pressable  | textarea → TextInput (multiline)

STYLE UNITS:
Unitless numbers = dp (density-independent pixels)
Platform.select() for Android vs iOS differences

SHADOW SHORTCUT:
Android: elevation: 4
iOS: shadowColor + shadowOffset + shadowOpacity + shadowRadius

NAVIGATION ACTIONS:
navigate → push (or show existing)    | replace → swap current
push → always push                    | goBack → go back one
popToTop → go to root                 | reset → reset entire stack

PERMISSION STATUS:
granted → proceed  | denied → request again  | blocked → Settings
unavailable → no feature on device    | limited → iOS partial

THREAD RULES:
JS Thread: logic, state, React       | UI Thread: rendering, touches
Never block UI thread                | Use useNativeDriver: true for animations
Reanimated v3 = UI thread via JSI    | Hermes = faster JS

BUILD FORMATS:
Android dev: APK    | Android release: AAB (Play Store)
iOS dev: .app       | iOS release: .ipa (TestFlight + App Store)

BUNDLE COMMAND (Android production):
npx react-native bundle --platform android --dev false
  --entry-file index.js --bundle-output android/app/src/main/assets/index.android.bundle
```

---

## 🔥 Most Asked in Senior RN Interviews
1. Bridge vs JSI (Old vs New Architecture)
2. How to prevent dropped frames in animations
3. FlatList optimization — all techniques
4. Permissions flow (BLOCKED state especially)
5. How to publish to Play Store + App Store (EAS Build)
6. Keystore — what happens if you lose it
7. OTA updates — what can/can't be OTA updated
8. React Native vs Flutter (architecture difference)
9. Native Module — when and how to write one
10. Expo vs CLI — production readiness
