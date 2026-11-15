# 294. Build Dark Mode Toggle
# हिंदी में: Dark Mode Toggle बनाओ
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 / React Native 0.76** पर target (check current docs — APIs change between SDKs).
> Files: [`ThemeContext.jsx`](./ThemeContext.jsx) (theme logic) · [`DarkModeScreen.jsx`](./DarkModeScreen.jsx) (demo UI)
> Packages: `npx expo install @react-native-async-storage/async-storage`

---

## 🔵 Simple Definition (English)
A **dark mode toggle** lets the user choose Light, Dark or System theme. We keep the choice in a React Context, read the phone's theme with `useColorScheme()`, and save the choice in AsyncStorage so it stays after the app restarts.

## 🔵 सरल परिभाषा (Hindi)
**Dark mode toggle** से user Light, Dark या System theme चुन सकता है। हम choice को React Context में रखते हैं, फ़ोन की theme `useColorScheme()` से पढ़ते हैं, और choice को AsyncStorage में save करते हैं ताकि app restart के बाद भी वही theme रहे।

---

## 🔴 Problem it Solves
```
❌ Raat ko white screen = आँखों में चुभती है + OLED पर battery ज़्यादा खर्च
❌ Har screen me alag-alag colour hard-code = theme बदलना मुश्किल
❌ User ने dark चुना, app restart हुआ -> फिर light (choice save नहीं हुई)
❌ Phone की system theme और app की theme mismatch
```

## 🔴 यह क्यों बना? (Hindi)
```
Interview में यह सबसे common "machine coding" सवाल है क्योंकि इसमें
Context + Hooks + Storage + Platform API चारों आते हैं।
Real apps (Swiggy, Zomato, Paytm, Instagram) तीनों option देते हैं:
Light / Dark / System default.
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Define two colour palettes (lightColors, darkColors)
Step 2 → ThemeProvider keeps `mode` state: 'system' | 'light' | 'dark'
Step 3 → On app start, read saved mode from AsyncStorage
Step 4 → useColorScheme() gives the phone theme ('light'/'dark')
Step 5 → effective theme = mode === 'system' ? phoneTheme : mode
Step 6 → Every screen calls useTheme() and uses colors.background, colors.text
Step 7 → When user taps a chip/switch -> setMode() -> state + AsyncStorage updated
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → दो colour palettes बनाओ (light और dark)
Step 2 → ThemeProvider में `mode` state रखो: system / light / dark
Step 3 → App start पर AsyncStorage से पुरानी choice पढ़ो
Step 4 → useColorScheme() से फ़ोन की theme मिलती है
Step 5 → असली theme = mode 'system' हो तो फ़ोन की theme, वरना user की choice
Step 6 → हर screen useTheme() से colours लेती है
Step 7 → user tap करे -> setMode() -> state और storage दोनों update
```

---

## 🟡 Real World Example
**Swiggy, Zomato, Paytm, PhonePe, Instagram** all have Appearance settings: "Light", "Dark", "System default". Instagram stores your choice on the phone and re-applies it at launch - exactly the pattern in this exercise.

## 🟡 Real Example Hindi mein
**Swiggy, Zomato, Paytm, PhonePe, Instagram** सब में Settings -> Appearance में "Light / Dark / System default" मिलता है। आपकी choice phone में save रहती है और app खुलते ही apply होती है - यही pattern हम बना रहे हैं।

---

## 💻 Code Example — Basic
Smallest version: only follow the system theme (no storage, no Context).

```jsx
// Basic: follow system theme only
import React from 'react'; // React
import { View, Text, useColorScheme, StyleSheet } from 'react-native'; // useColorScheme = system theme hook

export default function BasicTheme() {
  const scheme = useColorScheme(); // 'light' | 'dark' | null
  const isDark = scheme === 'dark'; // boolean

  return (
    // background depends on theme
    <View style={[styles.box, { backgroundColor: isDark ? '#121212' : '#ffffff' }]}>
      {/* text colour also depends on theme */}
      <Text style={{ color: isDark ? '#fff' : '#000' }}>Theme: {scheme}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  box: { flex: 1, alignItems: 'center', justifyContent: 'center' }, // centre content
});
```

## 💻 Code Example — Advanced
Full production version is in [`ThemeContext.jsx`](./ThemeContext.jsx) and [`DarkModeScreen.jsx`](./DarkModeScreen.jsx). Key part:

```jsx
// Key part of ThemeContext.jsx
const systemScheme = useColorScheme(); // phone theme
const [mode, setMode] = useState('system'); // user choice

useEffect(() => {
  AsyncStorage.getItem('theme-mode')            // read saved choice
    .then((saved) => { if (['light','dark','system'].includes(saved)) setMode(saved); }) // validate
    .catch(() => {})                              // never crash on storage error
    .finally(() => setReady(true));               // render only after load (no white flash)
}, []);

const effective = mode === 'system' ? systemScheme ?? 'light' : mode; // final theme
const value = useMemo(() => ({ mode, isDark: effective === 'dark',
  colors: effective === 'dark' ? darkColors : lightColors, setMode: changeMode }), [mode, effective]);
```

Usage in `App.js`:
```jsx
import DarkModeScreen from './13-interview-problems/294-build-dark-mode-toggle/DarkModeScreen'; // adjust path
export default DarkModeScreen; // already wrapped with <ThemeProvider>
```

> Verified: logic + render tested under jsdom (react-native-web, mocked AsyncStorage): selecting DARK updates label to "dark (dark)". `useColorScheme`/StatusBar native behaviour: not run on device.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| System dark setting | Settings -> Display -> Dark theme | Settings -> Display & Brightness |
| `useColorScheme()` | Works (Android 10+) | Works (iOS 13+) |
| Status bar | `StatusBar` `backgroundColor` prop works | `backgroundColor` ignored; only `barStyle` |
| Navigation bar | Can be styled (expo-navigation-bar) | No nav bar |
| `app.json` `userInterfaceStyle` | `"automatic"` needed so app follows system | `"automatic"` needed (Info.plist UIUserInterfaceStyle) |
| Pure black on OLED | Saves battery | Saves battery (OLED iPhones) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```json
// app.json — without this, Expo apps may stay light and useColorScheme returns 'light'
{ "expo": { "userInterfaceStyle": "automatic" } }
```
```bash
npx expo install @react-native-async-storage/async-storage   # picks SDK-compatible version
```
CLI way:
```bash
npm install @react-native-async-storage/async-storage         # install
cd ios && pod install && cd ..                                 # link iOS native pod
# Android: auto-linked. Also remove `android:forceDarkAllowed`/ensure Theme.AppCompat.DayNight in styles.xml
# iOS: remove UIUserInterfaceStyle = Light from Info.plist if present
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Forgetting `"userInterfaceStyle": "automatic"` in app.json (Expo).
✅ **Correct:** Add it, rebuild/reload; otherwise `useColorScheme()` may always return light.

❌ **Mistake 2:** Using `Appearance.getColorScheme()` once, not a hook.
```jsx
const scheme = Appearance.getColorScheme(); // ❌ does not update when user changes system theme
```
✅ **Correct:** `useColorScheme()` re-renders automatically.

❌ **Mistake 3:** Rendering UI before reading storage -> white flash then dark.
✅ **Correct:** Keep `ready` flag, return `null` (or splash) until storage is read.

❌ **Mistake 4:** Creating new context `value` object every render -> all consumers re-render.
✅ **Correct:** `useMemo` for the value.

❌ **Mistake 5:** Hard-coded `color: '#000'` in some components.
✅ **Correct:** Always take colours from `useTheme()`.

---

## 🧠 Tricky Interview Question
**Q:** User picked "System". Phone is Light. User switches phone to Dark while app is in the background and returns. Does your UI update without restart?

**Answer:** Yes, because `useColorScheme()` is a hook subscribed to Appearance changes, so ThemeProvider re-renders and `effective` recomputes. If we had used `Appearance.getColorScheme()` once it would NOT update. Also note: `useColorScheme()` can return `null` on some devices, so we fall back to `'light'`.

---

## ⚫ Interview Questions + Answers

**Q1: Difference between `useColorScheme` and `Appearance`?**
A1: `useColorScheme` is a hook that re-renders on change. `Appearance.getColorScheme()` is a one-time read; `Appearance.addChangeListener` is the manual subscription. Prefer the hook inside components.

**Q2: Why Context and not props?**
A2: Theme is needed by almost every component; Context avoids prop drilling.

**Q3: Why AsyncStorage?**
A3: Context lives in memory and resets on restart. AsyncStorage persists the choice on disk. For large/fast data use MMKV.

**Q4: How do you avoid the light flash on startup?**
A4: Delay rendering (or keep splash screen via `expo-splash-screen`) until the saved mode is loaded.

**Q5: How would you theme React Navigation?**
A5: Pass `theme={isDark ? DarkTheme : DefaultTheme}` (from `@react-navigation/native`) to `NavigationContainer`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- App is used at night (food delivery, reading, social)
- Brand wants System / Light / Dark choices
- OLED battery saving matters

❌ Avoid when:
- Single-theme brand (e.g. a kids game with fixed art) - extra QA cost
- Theme only 1-2 colours - simple `useColorScheme` is enough (see Basic)

---

## 📊 Visual Diagram
```
 AsyncStorage ──load──▶ mode ('system'|'light'|'dark')
                          │
 useColorScheme() ───────▶ effective theme ──▶ colors object
                                                  │ (Context)
              ┌───────────────────────────────────┼─────────────┐
              ▼                                   ▼             ▼
          HomeScreen                         Settings       Any component
 User taps chip ──▶ setMode() ──▶ state + AsyncStorage.setItem()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| useColorScheme | Hook returning system theme | System theme बताने वाला hook |
| Context | Global state without prop drilling | Prop drilling के बिना global state |
| AsyncStorage | Disk key-value storage | Phone में key-value storage |
| useMemo | Cache a computed value | Computed value cache करना |
| userInterfaceStyle | app.json key for theme support | Theme support की setting |

---

## ⚡ 3-Line Summary
**English:**
1. Keep `mode` (system/light/dark) in Context and compute the effective theme.
2. Save the mode in AsyncStorage and load it before first render.
3. Screens read colours via `useTheme()`; never hard-code colours.

**Hindi:**
1. `mode` को Context में रखो और असली theme निकालो।
2. Mode को AsyncStorage में save करो और पहली render से पहले load करो।
3. Screens `useTheme()` से colours लें; hard-code मत करो।

---

## ➡️ Next Topic
**295. Build Multi-Language App** - theme के बाद दूसरा आम setting: भाषा (Hindi/English) बदलना।
