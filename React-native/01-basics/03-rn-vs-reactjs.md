# 03. React Native vs React.js — Key Differences
# हिंदी में: React Native और React.js में क्या फर्क है?
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**React.js** runs in a browser — renders HTML elements to the DOM. **React Native** runs on a mobile device — renders native UI components (not HTML). Both use the same React concepts: components, hooks, state, props, JSX — but the output platform and available components are completely different.

## 🔵 सरल परिभाषा (Hindi)
**React.js** browser में run होता है — HTML elements को DOM में render करता है। **React Native** mobile device पर run होता है — native UI components render करता है (HTML नहीं)। दोनों same React concepts use करते हैं: components, hooks, state, props, JSX — लेकिन output platform और available components बिल्कुल अलग हैं।

---

## 🔴 Problem it Solves
```
React.js developer mobile app बनाना चाहता है।
Problems without React Native:
❌ Swift/Kotlin सीखना पड़ता
❌ Mobile-specific concepts (gestures, navigation, device APIs) अलग से सीखना
❌ React knowledge waste हो जाती

React Native: Same React skills → Mobile apps!
✅ JSX works the same
✅ Hooks work the same (useState, useEffect, useContext)
✅ Same state management (Zustand, Redux)
✅ Same JS libraries where possible
```

## 🔴 यह क्यों बना? (Hindi)
```
React.js developers mobile apps बना सकें — इसीलिए React Native।
Same React knowledge, same hooks, same patterns —
बस platform-specific components और APIs अलग हैं।
```

---

## 🟢 How it Works — Step by Step

```
REACT.JS:
Step 1 → Write JSX with HTML elements (div, p, img, button)
Step 2 → Babel compiles JSX to React.createElement()
Step 3 → React creates Virtual DOM
Step 4 → ReactDOM renders to browser's real DOM
Step 5 → Browser displays HTML/CSS rendered page

REACT NATIVE:
Step 1 → Write JSX with RN components (View, Text, Image, Pressable)
Step 2 → Babel compiles JSX to React.createElement()
Step 3 → React creates Virtual DOM (same as web!)
Step 4 → React Native renderer maps to native widgets (NOT HTML!)
Step 5 → Platform renders native UI (Android/iOS widgets)
```

## 🟢 कैसे काम करता है? (Hindi)
```
React.js: JSX → Virtual DOM → ReactDOM → Browser DOM → HTML page
React Native: JSX → Virtual DOM → RN Renderer → Native widgets → App screen
Step 3 तक same है! उसके बाद platform अलग हो जाता है।
```

---

## 🟡 Real World Example
**Swiggy**: The website (`swiggy.com`) is React.js — runs in browser, uses `<div>`, `<button>`, CSS. The **Swiggy app** on your phone is React Native — same React team built it, but uses `<View>`, `<Pressable>`, StyleSheet. Same developers, same React patterns, different output.

## 🟡 Real Example Hindi mein
**Swiggy**: `swiggy.com` website React.js से बनी है — browser में, `<div>` और CSS। Phone पर **Swiggy app** React Native से बनी है — same React team, same patterns, लेकिन `<View>`, `<Pressable>`, StyleSheet use होते हैं।

---

## 💻 Code Example — Basic

```jsx
// ══ SIDE BY SIDE COMPARISON ══

// ── REACT.JS (Web) ─────────────────────────
// Runs in browser, HTML elements
import React, { useState } from 'react';

function CounterWeb() {
  const [count, setCount] = useState(0);

  return (
    <div className="container">          {/* HTML div */}
      <h1>Count: {count}</h1>            {/* HTML h1 */}
      <p>Click to increment</p>          {/* HTML p */}
      <button onClick={() => setCount(c => c + 1)}>
        +1
      </button>                          {/* HTML button */}
    </div>
  );
}
// Styling: CSS file or styled-components (class names)
// .container { padding: 20px; background: #fff; }


// ── REACT NATIVE (Mobile) ──────────────────
// Runs on Android + iOS, Native components
import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

function CounterMobile() {
  const [count, setCount] = useState(0); // SAME useState!

  return (
    <View style={styles.container}>      {/* NOT div — View */}
      <Text style={styles.heading}>Count: {count}</Text>  {/* NOT h1 — Text */}
      <Text style={styles.info}>Tap to increment</Text>   {/* NOT p — Text */}
      <TouchableOpacity
        style={styles.button}
        onPress={() => setCount(c => c + 1)}  {/* onPress not onClick! */}
      >
        <Text style={styles.buttonText}>+1</Text>
      </TouchableOpacity>
    </View>
  );
}

// Styling: StyleSheet.create (JavaScript object, no class names)
const styles = StyleSheet.create({
  container: { padding: 20, backgroundColor: '#fff' },
  heading: { fontSize: 24, fontWeight: 'bold' },  // fontSize not font-size!
  info: { fontSize: 16, color: '#666' },
  button: { backgroundColor: '#f97316', padding: 12, borderRadius: 8 },
  buttonText: { color: '#fff', fontWeight: 'bold', textAlign: 'center' },
});

// KEY DIFFERENCE: useState, logic, JSX structure — ALL THE SAME!
// Only components and styling are different.
```

## 💻 Code Example — Advanced

```jsx
// ══ COMPLETE DIFFERENCES SHOWCASE ══

// React.js (Web):
function ProductCardWeb({ product, onAddToCart }) {
  const [isAdded, setIsAdded] = useState(false);

  return (
    <div                                // ← HTML element
      className="product-card"          // ← className (CSS classes)
      style={{ border: '1px solid #eee' }}
    >
      <img                              // ← HTML img
        src={product.image}
        alt={product.name}
        style={{ width: '100%' }}
      />
      <h2>{product.name}</h2>           // ← HTML h2
      <p>₹{product.price}</p>           // ← HTML p
      <button                           // ← HTML button
        onClick={() => {               // ← onClick
          setIsAdded(true);
          onAddToCart(product.id);
        }}
        style={{ cursor: 'pointer' }}
      >
        {isAdded ? 'Added ✓' : 'Add to Cart'}
      </button>
    </div>
  );
}

// React Native (Mobile):
import { View, Text, Image, Pressable, StyleSheet } from 'react-native';

function ProductCardMobile({ product, onAddToCart }) {
  const [isAdded, setIsAdded] = useState(false); // SAME!

  return (
    <View                               // ← RN View (not div)
      style={styles.card}              // ← style (not className)
    >
      <Image                            // ← RN Image
        source={{ uri: product.image }} // ← source.uri (not src)
        style={styles.image}
        resizeMode="cover"              // ← native resize
      />
      <Text style={styles.name}>{product.name}</Text>  // ← RN Text
      <Text style={styles.price}>₹{product.price}</Text>
      <Pressable                        // ← Pressable (not button)
        onPress={() => {               // ← onPress (not onClick)
          setIsAdded(true);
          onAddToCart(product.id);
        }}
        style={({ pressed }) => [      // ← feedback on press
          styles.button,
          pressed && styles.buttonPressed
        ]}
      >
        <Text style={styles.buttonText}>
          {isAdded ? 'Added ✓' : 'Add to Cart'}
        </Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    overflow: 'hidden',               // clips image to borderRadius
    margin: 8,
    elevation: 2,                     // Android shadow
  },
  image: { width: '100%', height: 200 },
  name: { fontSize: 16, fontWeight: '700', padding: 12 },
  price: { fontSize: 14, color: '#f97316', paddingHorizontal: 12 },
  button: {
    backgroundColor: '#f97316',
    margin: 12,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonPressed: { opacity: 0.8 },
  buttonText: { color: '#fff', fontWeight: '700' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Tap feedback | `TouchableNativeFeedback` ripple | `TouchableOpacity` fade |
| Back navigation | Hardware back button | Swipe from edge |
| Font | Roboto (system) | SF Pro (system) |
| Alert style | Material Design dialog | iOS native dialog |
| Status bar | Can be transparent/translucent | Has notch/Dynamic Island |

---

## 🟠 Expo vs CLI Difference

Expo way: (Web developers can start immediately)
```bash
npx create-expo-app MyApp --template blank-typescript
# Opens in browser-like dev tools, same React experience
```

CLI way:
```bash
npx react-native@latest init MyApp --template react-native-template-typescript
# More like traditional mobile dev setup
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using HTML elements in React Native
```jsx
// WRONG:
<div>Hello</div>          // ❌ Error in RN!
<p>Paragraph</p>          // ❌ Error in RN!
<button>Click</button>    // ❌ Error in RN!
<img src="..." />         // ❌ Error in RN!

// CORRECT:
<View>                    // ✅ div → View
  <Text>Paragraph</Text>  // ✅ p → Text
  <Pressable>             // ✅ button → Pressable
    <Text>Click</Text>
  </Pressable>
  <Image source={{uri:'...'}} />  // ✅ img → Image
</View>
```

❌ **Mistake 2:** Using `onClick` instead of `onPress`
```jsx
// WRONG:
<Pressable onClick={handleTap}>  // ❌ onClick doesn't work on mobile

// CORRECT:
<Pressable onPress={handleTap}>  // ✅ onPress for mobile
```

❌ **Mistake 3:** Using CSS properties instead of JS camelCase
```jsx
// WRONG: CSS syntax doesn't work in StyleSheet
const styles = StyleSheet.create({
  text: {
    'font-size': 16,         // ❌ CSS hyphen syntax
    'background-color': '#fff', // ❌
  }
});

// CORRECT: camelCase
const styles = StyleSheet.create({
  text: {
    fontSize: 16,            // ✅ camelCase
    backgroundColor: '#fff', // ✅ camelCase
  }
});
```

---

## 🧠 Tricky Interview Question

**Q: If React Native and React.js use the same hooks (useState, useEffect), can I share custom hooks between a React web app and React Native app?**

**Answer:** YES! Custom hooks are pure JavaScript functions — they don't care about the platform. A `useFetch(url)` hook, `useDebounce(value)`, `useForm(fields)` — all work identically in both React.js and React Native. The only thing you CAN'T share is UI code (components with `<div>` vs `<View>`). Business logic, custom hooks, utility functions, API calls, Zustand/Redux stores — all shareable. This is why monorepos (sharing code between web and mobile) are powerful.

---

## ⚫ Interview Questions + Answers

**Q1: What is the main architectural difference between React.js and React Native?**
A1: React.js uses ReactDOM to render to a browser's DOM — the output is HTML/CSS. React Native uses a native renderer that communicates with iOS/Android native APIs via Bridge/JSI — the output is actual native widgets. The React layer (reconciliation, Virtual DOM, component model) is identical. Only the renderer and available components differ.

**Q2: Name 5 differences between React.js and React Native.**
A2: (1) Elements: `div/p/button` vs `View/Text/Pressable`. (2) Styling: CSS classes vs `StyleSheet.create` (JS objects, camelCase). (3) Events: `onClick` vs `onPress`. (4) Layout: CSS `display: flex` vs default flexbox (column direction). (5) Navigation: React Router (`<Link>`, `useNavigate`) vs React Navigation (`navigation.navigate()`).

**Q3: Can I use CSS in React Native?**
A3: No — React Native doesn't run in a browser, so there's no CSS engine. Use `StyleSheet.create()` with JavaScript objects. Properties are camelCase (`fontSize` not `font-size`). Not all CSS properties exist (no `float`, no `z-index` in all cases, no `display: grid`). Layouts use Flexbox (column direction by default, unlike web's row default).

**Q4: What React concepts work identically in React Native?**
A4: Everything in the React core: `useState`, `useEffect`, `useContext`, `useReducer`, `useMemo`, `useCallback`, `useRef`, custom hooks, `React.memo`, Context API, error boundaries, the component lifecycle, JSX syntax, conditional rendering, list rendering with `.map()` + `key` prop, props, composition. React Native extends React — it doesn't replace its core model.

**Q5: Can I use npm packages from React.js in React Native?**
A5: Pure JavaScript packages: YES (lodash, axios, date-fns, zustand, redux, etc.). Packages that touch the DOM or browser APIs: NO (`document`, `window`, `localStorage` don't exist). Packages with native code (camera, notifications): need React Native-specific versions. Rule: if a package uses browser/DOM APIs internally, it won't work in RN. Many popular libraries have RN-compatible versions (`react-navigation` vs `react-router`, `AsyncStorage` vs `localStorage`).

---

## 🔷 When to Use + When Not to Use
✅ **React Native when:**
- Need a mobile app alongside your React web app
- Your team knows React.js
- Want code sharing between web and mobile
- Building standard mobile apps (e-commerce, delivery, social)

✅ **React.js when:**
- Building web applications (browser)
- SEO is important (Next.js)
- Complex web-specific interactions

---

## 📊 Visual Diagram

```
REACT.JS vs REACT NATIVE — SAME CORE, DIFFERENT OUTPUT:
──────────────────────────────────────────────────────────
  SAME (React Core):
  ┌──────────────────────────────────────────┐
  │  JSX syntax, Hooks, State, Props,        │
  │  Component Model, Virtual DOM,           │
  │  Custom Hooks, Context, Redux/Zustand    │
  └──────────────────────────────────────────┘
           │                      │
           ▼                      ▼
  REACT.JS (Web)          REACT NATIVE (Mobile)
  ┌──────────────┐        ┌──────────────────┐
  │ div, p, span │        │ View, Text, Image│
  │ button, img  │        │ Pressable, FlatList│
  │ CSS classes  │        │ StyleSheet.create│
  │ onClick      │        │ onPress          │
  │ React Router │        │ React Navigation │
  │ localStorage │        │ AsyncStorage/MMKV│
  │ Browser DOM  │        │ Native widgets   │
  └──────────────┘        └──────────────────┘
         │                        │
         ▼                        ▼
  Browser screen           Mobile app screen
  (Chrome/Firefox)         (Android + iOS)

ELEMENT MAPPING:
──────────────────────────────────────────────────────────
  React.js   →   React Native  →  Native
  div        →   View          →  UIView / android.view.View
  p, h1-h6   →   Text          →  UILabel / TextView
  img        →   Image         →  UIImageView / ImageView
  button     →   Pressable     →  UIButton / Button
  input      →   TextInput     →  UITextField / EditText
  ul + li    →   FlatList      →  UITableView / RecyclerView
  <a>        →   Pressable     →  (handled by navigation)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| View | RN equivalent of div | div का RN equivalent |
| Text | RN equivalent of p/h1/span | p/h1/span का RN equivalent |
| Pressable | RN equivalent of button | button का RN equivalent |
| StyleSheet | RN styling (JS object, no CSS) | RN styling (JS object, CSS नहीं) |
| onPress | Mobile tap event (vs onClick) | Mobile tap event |
| Native widget | Platform's own UI element | Platform का खुद का UI element |
| ReactDOM | Web renderer for React | Web के लिए React renderer |

---

## ⚡ 3-Line Summary
**English:**
1. Same React (JSX, hooks, state, props) — different output: React.js → browser HTML, React Native → mobile native widgets.
2. Replace: `div→View`, `p→Text`, `button→Pressable`, `onClick→onPress`, `CSS→StyleSheet.create`.
3. Custom hooks, business logic, state management — 100% shareable between React.js and React Native.

**Hindi:**
1. Same React (JSX, hooks, state, props) — अलग output: React.js → browser HTML, React Native → mobile native widgets।
2. Replace करो: `div→View`, `p→Text`, `button→Pressable`, `onClick→onPress`, `CSS→StyleSheet.create`।
3. Custom hooks, business logic, state management — React.js और React Native के बीच 100% shareable।

---

## ➡️ Next Topic
**04. How React Native Works — Bridge/JSI** — JavaScript और Native code के बीच communication कैसे होती है।
