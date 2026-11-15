# 180. React Native for Web
# हिंदी में: React Native for Web (RN Code को Browser में चलाना)
# Platform: Android ✅ | iOS ✅ | Web ✅ (Both + Web)

> **Expo SDK 54 (React Native 0.81) target** — check current docs — APIs change between SDKs. Web uses `react-native-web` (RNW) with Metro (Expo default) or webpack/Vite/Next.js. Some native-only APIs have no web version.

---

## 🔵 Simple Definition (English)
**React Native for Web** (`react-native-web`) is a library that maps RN components (`View`, `Text`, `Pressable`, `StyleSheet`) to **HTML + CSS** in the browser. The same JSX can run on Android, iOS and the web, giving you a website from your app code.

## 🔵 सरल परिभाषा (Hindi)
**React Native for Web** (`react-native-web`) एक library है जो RN components (`View`, `Text`, `Pressable`, `StyleSheet`) को browser में **HTML + CSS** में map करती है। वही JSX Android, iOS और web पर चल सकता है — यानी app के code से website मिल जाती है।

---

## 🔴 Problem it Solves
```
❌ Mobile app team + separate web team = duplicate UI code
❌ Business logic, API layer, state, forms rewritten for web
❌ Design inconsistency between app and website
✅ Share components/hooks/logic; only platform-specific parts differ
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ Mobile team + अलग web team = duplicate UI code
❌ Business logic, API layer, state, forms web के लिए दोबारा
❌ App और website के design में फ़र्क
✅ Components/hooks/logic share करो; सिर्फ platform-specific हिस्सा अलग
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Install react-native-web + react-dom (Expo: npx expo install)
Step 2 → Bundler aliases 'react-native' -> 'react-native-web'
Step 3 → <View> becomes <div>, <Text> becomes <div>/<span>, <Pressable> gets ARIA + events
Step 4 → StyleSheet styles compile to atomic CSS classes
Step 5 → Platform.OS === 'web' lets you branch behaviour
Step 6 → File extensions: Foo.web.tsx is picked on web, Foo.native.tsx on mobile
Step 7 → Run: npx expo start --web  (or build static: npx expo export --platform web)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → react-native-web + react-dom install करो (Expo: npx expo install)
Step 2 → Bundler 'react-native' को 'react-native-web' से alias करता है
Step 3 → <View> -> <div>, <Text> -> <div>/<span>, <Pressable> में ARIA + events
Step 4 → StyleSheet styles atomic CSS classes बन जाती हैं
Step 5 → Platform.OS === 'web' से web के लिए अलग behaviour
Step 6 → File extensions: Foo.web.tsx web पर, Foo.native.tsx mobile पर चुनी जाती है
Step 7 → चलाओ: npx expo start --web (या static build: npx expo export --platform web)
```

---

## 🟡 Real World Example
**Twitter Lite** (PWA) was built with react-native-web; **Expo's own docs site** and **Bluesky app** run on iOS, Android and web from one codebase. A **Swiggy**-like team could reuse `RestaurantCard`, cart logic and API hooks on `swiggy.com` while only the navigation shell differs.

## 🟡 Real Example Hindi mein
**Twitter Lite** (PWA) react-native-web से बना था; **Bluesky app** iOS, Android और web तीनों एक codebase से चलता है। **Swiggy** जैसी team `RestaurantCard`, cart logic और API hooks को website पर reuse कर सकती है — सिर्फ navigation shell अलग रहेगा।

---

## 💻 Code Example — Basic
```jsx
// Basic: one component, runs on Android, iOS and Web (react-native-web)
import React, { useState } from 'react';                      // React + state
import { View, Text, Pressable, StyleSheet, Platform } from 'react-native'; // RN components

export default function Counter() {
  const [count, setCount] = useState(0);                      // counter state
  return (
    <View style={styles.container}>
      {/* On web this renders as <div>/<span> */}
      <Text style={styles.title}>Running on: {Platform.OS}</Text>
      <Text style={styles.count}>Count: {count}</Text>
      {/* Pressable handles mouse click on web, touch on mobile */}
      <Pressable
        onPress={() => setCount((c) => c + 1)}                // increment on press/click
        style={({ pressed }) => [styles.btn, pressed && styles.btnPressed]} // pressed feedback
      >
        <Text style={styles.btnText}>Add</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center' }, // center everything
  title: { fontSize: 16, color: '#555' },                       // platform label
  count: { fontSize: 32, fontWeight: '700', marginVertical: 12 }, // big number
  btn: { backgroundColor: '#f97316', paddingHorizontal: 24, paddingVertical: 10, borderRadius: 8 }, // button
  btnPressed: { opacity: 0.7 },                                // pressed look
  btnText: { color: '#fff', fontWeight: '700' },               // button text
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: platform-specific files + responsive layout for web
// File 1: components/Share.native.js  (mobile uses Share API)
//   import { Share } from 'react-native';
//   export const share = (text) => Share.share({ message: text });
//
// File 2: components/Share.web.js     (web uses Web Share / clipboard)
//   export const share = async (text) => {
//     if (navigator.share) return navigator.share({ text });          // modern browsers/mobile web
//     await navigator.clipboard.writeText(text);                      // fallback: copy
//   };
//
// The import `import { share } from './Share'` automatically picks the right file.

import React from 'react';
import { View, Text, FlatList, useWindowDimensions, Platform, StyleSheet } from 'react-native';

const DATA = Array.from({ length: 12 }, (_, i) => ({ id: String(i), name: `Dish ${i + 1}` })); // fake menu

export default function Menu() {
  const { width } = useWindowDimensions();            // updates on browser resize too
  // columns: 1 on phones, 2 on tablets, 4 on wide desktop screens
  const columns = width >= 1024 ? 4 : width >= 600 ? 2 : 1;
  return (
    <FlatList
      key={columns}                                   // changing numColumns needs a new key
      data={DATA}
      numColumns={columns}                            // responsive grid
      keyExtractor={(d) => d.id}
      contentContainerStyle={styles.list}
      renderItem={({ item }) => (
        <View style={[styles.card, { flex: 1 / columns }]}>
          <Text style={styles.name}>{item.name}</Text>
          {/* web-only hint, hidden on mobile */}
          {Platform.OS === 'web' && <Text style={styles.hint}>Hover for details</Text>}
        </View>
      )}
    />
  );
}

const styles = StyleSheet.create({
  list: { padding: 12 },                              // outer padding
  card: { margin: 6, padding: 16, backgroundColor: '#fff', borderRadius: 10, borderWidth: 1, borderColor: '#eee' }, // card
  name: { fontSize: 16, fontWeight: '600' },          // dish name
  hint: { fontSize: 12, color: '#999', marginTop: 4 }, // web hint
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS | Web |
|---------|---------|-----|-----|
| Renders to | Android views | UIViews | HTML + CSS |
| Shadows | `elevation` | `shadow*` props | `boxShadow` (RN 0.76+) / `shadow*` mapped by RNW |
| Navigation back | Hardware back | Swipe | Browser back button + URLs |
| Native modules | Yes | Yes | No (needs web equivalent) |
| Input | Touch | Touch | Mouse + keyboard + touch |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Add web support
npx expo install react-dom react-native-web @expo/metro-runtime
npx expo start --web                    # dev server in browser
npx expo export --platform web          # static build in dist/
# app.json: { "expo": { "web": { "bundler": "metro", "output": "static" } } }
```
CLI way:
```bash
# Bare RN: set up webpack/Vite/Next.js with alias manually
npm install react-native-web react-dom
# webpack: resolve.alias = { 'react-native$': 'react-native-web' }
# Vite: resolve.alias = { 'react-native': 'react-native-web' }
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using a native-only library (camera, biometrics) on web
✅ Correct: Guard with `Platform.OS === 'web'` or create `.web.js` fallback.

❌ Mistake 2: Expecting hover/focus/cursor automatically
✅ Correct: Use `Pressable` `onHoverIn`/`onHoverOut` (web) and `cursor` style where supported.

❌ Mistake 3: Ignoring SEO and URLs
✅ Correct: Use a router with URLs (Expo Router) and static rendering for SEO.

---

## 🧠 Tricky Interview Question
**Q: `<Text>` on web wraps in a `<div>`, and `View` inside `Text` breaks layout. Why do text styles not inherit like CSS?**

**Answer:** RN style inheritance is limited: only nested `Text` inherits text styles from parent `Text`, not from `View`. RNW follows RN semantics (flexbox default `display:flex`, `position: relative`, no CSS cascade), so styling must be explicit; that keeps behaviour same on all platforms.

---

## ⚫ Interview Questions + Answers

**Q1: How does RNW render `View`?**
A1: As a `div` with default flex styles (`display:flex; flex-direction:column`).

**Q2: How do you write web-specific code?**
A2: `Platform.OS === 'web'`, `Platform.select`, or `.web.js` files.

**Q3: Does AsyncStorage work on web?**
A3: The community package uses `localStorage` on web.

**Q4: How to handle responsive design?**
A4: `useWindowDimensions`, media-query libs, or flexible layouts.

**Q5: Can you do SSR?**
A5: Yes, with Next.js + RNW or Expo Router static/server rendering.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Dashboard/app with shared UI and logic
- Small team wants app + website

❌ Avoid when:
- Content-heavy SEO site needing pure HTML/CSS control
- Web needs very different UX from mobile

---

## 📊 Visual Diagram
```
        Shared JSX (View, Text, Pressable)
              │
  ┌───────────┼────────────┐
  ▼           ▼            ▼
Android      iOS          Web
(native)   (native)   react-native-web
                       → div, span, CSS
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| react-native-web | RN API for browsers | Browser के लिए RN API |
| Alias | Replace import path | Import path बदलना |
| `.web.js` | Web-only file | सिर्फ web वाली file |
| SSR | Server-side rendering | Server पर render |
| Responsive | Adapts to width | Screen के हिसाब से बदलना |
| PWA | Installable web app | Install होने वाला web app |

---

## ⚡ 3-Line Summary
**English:**
1. react-native-web maps RN components to HTML/CSS.
2. Share code; branch with `Platform.OS` or `.web.js` files.
3. Native-only APIs need web fallbacks.

**Hindi:**
1. react-native-web, RN components को HTML/CSS में map करता है।
2. Code share करो; `Platform.OS` या `.web.js` files से अलग करो।
3. Native-only APIs के लिए web fallback चाहिए।

---

## ➡️ Next Topic
**181. Monorepo (RN + Web sharing code)** — app और web के बीच code share करने की folder structure।
