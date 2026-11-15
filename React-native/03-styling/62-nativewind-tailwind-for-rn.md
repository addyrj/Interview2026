# 62. NativeWind (Tailwind for RN)
# हिंदी में: NativeWind — React Native के लिए Tailwind
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (React Native 0.76)**, **NativeWind v4** + Tailwind CSS 3.x. Setup differs a lot between NativeWind v2/v4 — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
**NativeWind** lets you style React Native components with Tailwind CSS utility classes: `<View className="p-4 bg-white rounded-xl" />`. At build time Tailwind generates the styles and NativeWind maps them to React Native styles.

## 🔵 सरल परिभाषा (Hindi)
**NativeWind** से React Native components को Tailwind CSS की utility classes से style करते हैं: `<View className="p-4 bg-white rounded-xl" />`। Build time पर Tailwind styles बनाता है और NativeWind उन्हें React Native styles में बदलता है।

---

## 🔴 Problem it Solves
```
StyleSheet:
  Naam sochna: container, wrapper, innerBox...
  Alag style file, repetitive values
  Dark mode / responsive = manual code

NATIVEWIND:
  ✅ className me hi style: "p-4 bg-red-500"
  ✅ dark: variant → "bg-white dark:bg-black"
  ✅ Design tokens (spacing, colors) consistent
  ✅ Web + mobile same classes (Expo Router web)
```

## 🔴 यह क्यों बना? (Hindi)
```
हर style के लिए नाम सोचना और अलग StyleSheet लिखना थकाऊ है।
Tailwind classes छोटी, consistent और तेज़ हैं।
dark: और md: जैसे variants से dark mode और responsive आसान।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Install: npx expo install nativewind react-native-reanimated react-native-safe-area-context
          and: npm i -D tailwindcss@^3.4.17 prettier-plugin-tailwindcss
Step 2 → npx tailwindcss init  → tailwind.config.js (content paths + nativewind/preset)
Step 3 → global.css with @tailwind base; @tailwind components; @tailwind utilities;
Step 4 → babel.config.js: presets: [['babel-preset-expo', { jsxImportSource: 'nativewind' }], 'nativewind/babel']
Step 5 → metro.config.js: withNativeWind(config, { input: './global.css' })
Step 6 → Import './global.css' in root file (App/_layout)
Step 7 → Use className on RN components
Step 8 → (TS) add nativewind-env.d.ts: /// <reference types="nativewind/types" />
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → nativewind + tailwindcss install
Step 2 → tailwind.config.js में content paths और nativewind/preset
Step 3 → global.css में तीन @tailwind lines
Step 4 → babel.config.js और metro.config.js में NativeWind जोड़ो
Step 5 → root में global.css import
Step 6 → components पर className लिखो
```

---

## 🟡 Real World Example
**A Swiggy-like restaurant card:** `className="m-3 rounded-2xl bg-white p-3 shadow-md"` for the card, `className="text-lg font-bold text-gray-900"` for the title, and `dark:bg-neutral-900` for dark mode. A designer's Tailwind design system maps directly into code.

## 🟡 Real Example Hindi mein
**Swiggy जैसा restaurant card:** card पर `m-3 rounded-2xl bg-white p-3 shadow-md`, title पर `text-lg font-bold text-gray-900`, dark mode के लिए `dark:bg-neutral-900`। Designer का Tailwind design system सीधे code में आ जाता है।

---

## 💻 Code Example — Basic
```jsx
// Basic NativeWind component (v4)
// Prereq: global.css imported once at app root
import React from 'react'; // React
import { View, Text, Pressable } from 'react-native'; // RN components (className works on them)

export default function Basic() { // component
  return (
    <View className="flex-1 items-center justify-center bg-white">{/* full screen, centered, white */}
      <Text className="text-2xl font-bold text-red-600">Zomato Gold</Text>{/* big bold red text */}
      <Pressable className="mt-4 rounded-lg bg-red-600 px-6 py-3 active:opacity-70">{/* active: = pressed state */}
        <Text className="font-semibold text-white">Join now</Text>{/* button label */}
      </Pressable>
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: dark mode, platform variants, conditional classes, config files
import React, { useState } from 'react'; // React + state
import { View, Text, Pressable, FlatList } from 'react-native'; // RN
import { useColorScheme } from 'nativewind'; // NativeWind v4 hook for theme control

const items = [{ id: '1', name: 'Paneer Tikka', price: 220 }, { id: '2', name: 'Dal Makhani', price: 180 }]; // data

export default function Menu() {
  const { colorScheme, toggleColorScheme } = useColorScheme(); // read/toggle theme
  const [selected, setSelected] = useState(null); // selected item id

  return (
    <View className="flex-1 bg-white p-4 dark:bg-neutral-900">{/* dark: variant */}
      <Pressable onPress={toggleColorScheme} className="mb-4 self-end">{/* toggle theme */}
        <Text className="text-sm text-gray-500 dark:text-gray-300">Theme: {colorScheme}</Text>
      </Pressable>
      <FlatList
        data={items} // list data
        keyExtractor={(i) => i.id} // keys
        renderItem={({ item }) => {
          const active = selected === item.id; // is selected
          return (
            <Pressable
              onPress={() => setSelected(item.id)} // select
              // template string for conditional classes; ios:/android: platform variants
              className={`mb-3 rounded-xl border p-4 shadow-md ${active ? 'border-red-500 bg-red-50' : 'border-gray-200 bg-white dark:bg-neutral-800'}`}
            >
              <Text className="text-base font-semibold text-gray-900 dark:text-white">{item.name}</Text>
              <Text className="text-gray-500 dark:text-gray-300">₹{item.price}</Text>
            </Pressable>
          );
        }}
      />
    </View>
  );
}

/* ---- tailwind.config.js (v4 NativeWind with Tailwind 3.x) ----
module.exports = {
  content: ['./App.{js,jsx,ts,tsx}', './app/**/*.{js,jsx,ts,tsx}', './components/**/*.{js,jsx,ts,tsx}'],
  presets: [require('nativewind/preset')],
  theme: { extend: { colors: { brand: '#e23744' } } },
  plugins: [],
};
-------------------------------------------------------------- */
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| className support | Yes | Yes |
| `shadow-*` classes | Rendered as elevation (check docs) | Rendered as shadow props |
| Platform variants | `android:` prefix | `ios:` prefix |
| Dark mode | Follows system / `useColorScheme` | Same |
| Font | System Roboto | System SF; use `font-*` with loaded fonts for consistency |
| Hover/focus variants | `active:` / `focus:` only | Same (no hover on touch) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo SDK 52 — metro.config.js
// const { getDefaultConfig } = require('expo/metro-config');
// const { withNativeWind } = require('nativewind/metro');
// module.exports = withNativeWind(getDefaultConfig(__dirname), { input: './global.css' });
// then restart with cache clear: npx expo start -c
```
CLI way:
```jsx
// Bare React Native CLI — metro.config.js
// const { getDefaultConfig, mergeConfig } = require('@react-native/metro-config');
// const { withNativeWind } = require('nativewind/metro');
// module.exports = withNativeWind(mergeConfig(getDefaultConfig(__dirname), {}), { input: './global.css' });
// Also: babel preset 'nativewind/babel'; run `cd ios && pod install` (reanimated is native)
```
Exact steps vary by NativeWind version — follow the official installation page.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to import `global.css`.
✅ Correct: `import './global.css'` in the root entry file.

❌ Mistake 2: `content` paths in tailwind.config.js don't match your folders — classes missing.
✅ Correct: Include every folder that has components.

❌ Mistake 3: Building class names dynamically: `` `bg-${color}-500` ``.
✅ Correct: Use full class names (`'bg-red-500'`) so Tailwind can detect them at build time.

❌ Mistake 4: Not clearing Metro cache after config changes.
✅ Correct: `npx expo start -c`.

---

## 🧠 Tricky Interview Question
**Q:** `<Text className={`text-${size}`}>` — works in dev for `text-xl` but not for `text-3xl` in release. Why?

**Answer:** Tailwind scans source text for complete class names. `text-${size}` never appears as a full string, so only classes seen somewhere else get generated. Use a lookup object: `{ sm: 'text-sm', xl: 'text-xl', '3xl': 'text-3xl' }[size]` or add to `safelist`.

---

## ⚫ Interview Questions + Answers
Q1: How does NativeWind work?
A1: Tailwind compiles classes at build time (via Metro/Babel); NativeWind turns `className` into style props at runtime with a small runtime.

Q2: How to enable dark mode?
A2: Use `dark:` variants; follows system by default; `useColorScheme` from nativewind to toggle manually (config `darkMode: 'class'` for manual control — check docs).

Q3: NativeWind vs StyleSheet?
A3: NativeWind: faster authoring, design tokens, variants. StyleSheet: no extra dependency, slightly less overhead.

Q4: How to use className on third-party components?
A4: `cssInterop(Component, { className: 'style' })` (v4) maps className to style prop.

Q5: Does it work on web?
A5: Yes with react-native-web / Expo Router web — same classes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Team knows Tailwind
- Need quick, consistent UI with dark mode and responsive variants

❌ Avoid when:
- Tiny app where setup is overkill
- You cannot upgrade Metro/Babel config
- You need runtime-generated arbitrary class names

---

## 📊 Visual Diagram
```
className="p-4 bg-white"
     │  Tailwind (build) generates style rules
     ▼
NativeWind runtime maps → { padding:16, backgroundColor:'#fff' }
     ▼
<View style=... /> → Native view (Android + iOS)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Utility class | Small single-purpose class | छोटी utility class |
| className | Prop for Tailwind classes | className prop |
| Variant | Prefix like dark:, ios: | Prefix (शर्त) |
| cssInterop | Enable className on custom components | className सक्षम करना |
| Safelist | Always-generate class list | हमेशा बनने वाली classes |

---

## ⚡ 3-Line Summary
English: NativeWind brings Tailwind classes to React Native via `className`.
Needs Babel, Metro and `global.css` setup; use full class names only.
Variants like `dark:`, `ios:`, `android:` make theming easy.

Hindi: NativeWind `className` से Tailwind classes React Native में लाता है।
Babel, Metro और `global.css` setup चाहिए; पूरे class names ही लिखो।
`dark:`, `ios:`, `android:` variants से theming आसान।

---

## ➡️ Next Topic
**63. Navigation in React Native** — styling khatam; ab screens ke beech move karna (navigation concepts).
