# 57. Icons — Expo Icons
# हिंदी में: Icons — Expo Icons (@expo/vector-icons)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (React Native 0.76)** — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
**Expo Icons** (`@expo/vector-icons`) is a ready-made icon library that comes with Expo. It wraps famous icon sets (Ionicons, MaterialIcons, FontAwesome, Feather, etc.) as React components. You use them like `<Ionicons name="home" size={24} color="red" />`.

## 🔵 सरल परिभाषा (Hindi)
**Expo Icons** (`@expo/vector-icons`) Expo के साथ आने वाली ready-made icon library है। इसमें Ionicons, MaterialIcons, FontAwesome, Feather जैसे famous icon sets React components की तरह मिलते हैं। इस्तेमाल: `<Ionicons name="home" size={24} color="red" />`।

---

## 🔴 Problem it Solves
```
BEFORE:
  Har icon ke liye PNG image (1x, 2x, 3x sizes) banana padta tha
  Color change = nayi image
  App size badhta tha
  Android/iOS dono ke liye alag assets

WITH VECTOR ICONS:
  ✅ Icon = font glyph (text jaisa) → kisi bhi size par sharp
  ✅ Color = simple prop
  ✅ Ek hi component, dono platforms
  ✅ 10,000+ icons ready
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले हर icon के लिए PNG (@1x, @2x, @3x) बनानी पड़ती थी।
Color बदलना = नई image। App size भी बढ़ता था।
Vector icons font की तरह काम करते हैं:
size और color props से बदल जाते हैं, हमेशा sharp रहते हैं।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Install: npx expo install @expo/vector-icons
Step 2 → Import a set: import { Ionicons } from '@expo/vector-icons'
Step 3 → Each set = a font file (.ttf) + a "glyph map" (name → unicode char)
Step 4 → Component loads the font (Expo bundles it) and renders ONE character
Step 5 → size → fontSize, color → text color
Step 6 → Result: sharp icon at any resolution
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → npx expo install @expo/vector-icons
Step 2 → Icon set import करो (Ionicons, MaterialIcons...)
Step 3 → हर set एक font file + name → character का map होता है
Step 4 → Component सिर्फ एक character render करता है (text की तरह)
Step 5 → size = fontSize, color = text color
```

---

## 🟡 Real World Example
**Swiggy / Zomato bottom tab bar:** Home (house), Search (magnifier), Cart (bag), Profile (person). Selected tab = filled orange icon, unselected = grey outline icon. All of this is just `Ionicons` with `name` switching between `home` and `home-outline` and a `color` prop.

## 🟡 Real Example Hindi mein
**Swiggy/Zomato bottom tabs:** Home, Search, Cart, Profile icons। Selected tab में filled orange icon, unselected में grey outline। यह सब सिर्फ `Ionicons` का `name` (`home` / `home-outline`) और `color` prop बदलने से होता है।

---

## 💻 Code Example — Basic
```jsx
// Basic icon usage
import React from 'react'; // React import
import { View, Text, StyleSheet } from 'react-native'; // core components
import { Ionicons, MaterialIcons, Feather } from '@expo/vector-icons'; // 3 icon sets

export default function IconsBasic() { // component
  return (
    <View style={styles.row}>{/* horizontal row of icons */}
      <Ionicons name="home" size={28} color="#e23744" />{/* Ionicons home, red */}
      <MaterialIcons name="shopping-cart" size={28} color="#333" />{/* Material cart */}
      <Feather name="user" size={28} color="#0a84ff" />{/* Feather user icon */}
      <Text style={styles.label}>Icons work on Android + iOS</Text>{/* plain text next to icons */}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', gap: 16, padding: 20 }, // row layout with gap
  label: { fontSize: 14, color: '#555' }, // label style
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: reusable Icon button + tab icons with fallback
import React from 'react'; // React
import { Pressable, View, Text, StyleSheet, Platform } from 'react-native'; // components
import { Ionicons } from '@expo/vector-icons'; // icon set

// Reusable icon button with press feedback and accessibility
export function IconButton({ name, size = 24, color = '#222', onPress, label, badge }) {
  return (
    <Pressable
      onPress={onPress} // handler from parent
      accessibilityRole="button" // screen reader role
      accessibilityLabel={label} // screen reader text (icons have NO text!)
      hitSlop={10} // bigger touch area than the 24px icon
      android_ripple={{ color: '#ddd', borderless: true }} // Android ripple only
      style={({ pressed }) => [styles.btn, Platform.OS === 'ios' && pressed && { opacity: 0.5 }]} // iOS fade
    >
      <Ionicons name={name} size={size} color={color} />{/* the icon */}
      {badge > 0 && ( // show badge only if count > 0
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{badge > 9 ? '9+' : badge}</Text>{/* cap at 9+ */}
        </View>
      )}
    </Pressable>
  );
}

// Tab icon helper: filled when focused, outline when not
export function tabIcon(routeName, focused, color, size) {
  const map = { Home: 'home', Search: 'search', Cart: 'bag', Profile: 'person' }; // base names
  const base = map[routeName] || 'help-circle'; // fallback icon for unknown routes
  const name = focused ? base : `${base}-outline`; // Ionicons has -outline variants
  return <Ionicons name={name} size={size} color={color} />; // render
}

const styles = StyleSheet.create({
  btn: { padding: 6 }, // padding around icon
  badge: { position: 'absolute', top: 0, right: 0, backgroundColor: '#e23744', borderRadius: 8, minWidth: 16, alignItems: 'center' }, // red dot
  badgeText: { color: '#fff', fontSize: 10, fontWeight: '700' }, // count text
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| @expo/vector-icons | Works same | Works same |
| Ionicons names | `md-` / `ios-` prefixes were removed in newer versions | Same unified names (`home`, `home-outline`) |
| Press feedback | `android_ripple` | Opacity change via `pressed` |
| SF Symbols (native iOS icons) | Not available | Available via `expo-symbols` (iOS only) |
| Material icons look | Native feel | Looks "foreign" but works |
| Font loading | Bundled, loads instantly | Same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: already included — no linking
// npx expo install @expo/vector-icons  (usually pre-installed in templates)
import { Ionicons } from '@expo/vector-icons'; // import directly
export const A = () => <Ionicons name="home" size={24} color="red" />; // use
```
CLI way:
```jsx
// Bare CLI: install react-native-vector-icons (check its docs for current setup)
// npm i react-native-vector-icons
// Android: add fonts via gradle config; iOS: add fonts to Info.plist (UIAppFonts) + pod install
import Ionicons from 'react-native-vector-icons/Ionicons'; // different package, per-set import
export const B = () => <Ionicons name="home" size={24} color="red" />; // same usage
```
Note: In bare projects you can also install `@expo/vector-icons` via the `expo` package (expo modules), but the font setup differs — check docs.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using a wrong icon name (e.g. `name="Home"`) — shows "?" or TypeScript error.
✅ Correct: Names are lowercase, kebab-case: `name="home"`. Browse them at the Expo icons directory (icons.expo.fyi).

❌ Mistake 2: Importing the whole library `import * as Icons from '@expo/vector-icons'`.
✅ Correct: Import only the set you need: `import { Ionicons } from '@expo/vector-icons'`.

❌ Mistake 3: Icon-only button without `accessibilityLabel`.
✅ Correct: Always add a label so screen readers (TalkBack/VoiceOver) can read it.

❌ Mistake 4: Tiny touch area (icon 20px, no padding).
✅ Correct: Use `hitSlop` or padding so the touch target is at least 44x44.

---

## 🧠 Tricky Interview Question
**Q:** Your icons render as "?" boxes in a release build but work in dev. Why?

**Answer:** The icon font did not load/bundle. In Expo, `@expo/vector-icons` fonts are loaded asynchronously; if you render before the font is ready (or in a custom-font setup with `useFonts` splash logic), you see empty boxes. Also in bare CLI, forgetting to add fonts to `Info.plist`/gradle gives exactly this. Fix: make sure the font is loaded (`Font.loadAsync` / `useFonts(Ionicons.font)`) before hiding the splash screen, or use the proper native setup in CLI.

---

## ⚫ Interview Questions + Answers
Q1: Why use vector icons instead of PNG images?
A1: Vector icons are font glyphs: sharp on every screen density, tiny size, and color/size are just props. PNG needs multiple resolutions and separate files per color.

Q2: Which package for icons in Expo and in bare CLI?
A2: Expo: `@expo/vector-icons`. Bare CLI: `react-native-vector-icons` (needs native font setup).

Q3: How do you show a filled icon when a tab is selected?
A3: In `tabBarIcon: ({ focused, color, size })` switch `name` between `home` and `home-outline` based on `focused`.

Q4: What if the icon you need is not in any set?
A4: Use an SVG with `react-native-svg`, or create a custom icon font with `createIconSet` / IcoMoon. Avoid PNG unless it is multi-color artwork.

Q5: How do you make icons accessible?
A5: Wrap in `Pressable` with `accessibilityRole="button"` and `accessibilityLabel`; decorative icons can be hidden with `accessibilityElementsHidden`/`importantForAccessibility="no"`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Single-color UI icons (tab bar, header buttons, list rows)
- You want color/size from props or theme
- You need quick prototyping in Expo

❌ Avoid when:
- Multi-color brand logos or illustrations (use SVG/PNG)
- You need very custom shapes (use custom SVG)
- App size is critical and you import many full sets (load only what you need)

---

## 📊 Visual Diagram
```
<Ionicons name="home" size={24} color="red" />
        │
        ▼
 Glyph map: "home" ─► ""
        │
        ▼
 Ionicons.ttf font ─► draws ONE character
        │
        ▼
 Text renderer: fontSize=24, color=red
        │
        ▼
      🏠 (sharp on any screen)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Vector icon | Icon drawn from font/SVG, scales without blur | Vector icon (साफ़ रहता है) |
| Glyph | One character in a font | Glyph (font का एक अक्षर) |
| Icon set | Collection like Ionicons | Icon set |
| hitSlop | Extra touch area around element | Touch area बढ़ाना |
| tabBarIcon | Tab navigator icon option | Tab का icon |

---

## ⚡ 3-Line Summary
English: `@expo/vector-icons` gives font-based icons as components.
Props `name`, `size`, `color` control everything; works on Android and iOS.
In bare CLI use `react-native-vector-icons` with native font setup.

Hindi: `@expo/vector-icons` font-based icons components की तरह देता है।
`name`, `size`, `color` props से सब कुछ control होता है; Android और iOS दोनों पर चलता है।
Bare CLI में `react-native-vector-icons` और native font setup चाहिए।

---

## ➡️ Next Topic
**58. Shadows (Android vs iOS difference)** — icons ke baad cards/buttons ko depth dene ke liye shadows, jahan Android aur iOS bilkul alag tarah kaam karte hain.
