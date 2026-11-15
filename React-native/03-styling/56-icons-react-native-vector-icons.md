# 56. Icons — React Native Vector Icons
# हिंदी में: React Native में Vector Icons का इस्तेमाल
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK version:** examples target **Expo SDK 52 (React Native 0.76)** — check current docs — APIs change between SDKs.
> `@expo/vector-icons` Expo में pre-installed आता है। CLI में `react-native-vector-icons` अलग से install होता है (नए versions में package structure बदला है — docs देखें)।

---

## 🔵 Simple Definition (English)
**Vector icons** are icons drawn from a **font file** (like Ionicons, MaterialIcons, FontAwesome). You render them with a component: `<Ionicons name="home" size={24} color="red" />`. Because they are vectors, they stay sharp at any size and can be recoloured with a simple `color` prop.

## 🔵 सरल परिभाषा (Hindi)
**Vector icons** वो icons हैं जो एक **font file** से आते हैं (जैसे Ionicons, MaterialIcons, FontAwesome)। आप इन्हें component से दिखाते हो: `<Ionicons name="home" size={24} color="red" />`। ये vector हैं, इसलिए किसी भी size पर sharp रहते हैं और `color` prop से रंग बदल सकते हैं।

---

## 🔴 Problem it Solves
```
BEFORE vector icons:
❌ Har icon ke liye PNG: icon_home.png, icon_home@2x.png, icon_home@3x.png
❌ Colour change karna ho (dark mode) -> naya image banao
❌ Bahut saare images = bada app size
❌ Chhota PNG bada karo to blur ho jata hai
```

## 🔴 यह क्यों बना? (Hindi)
```
Vector icons से पहले:
❌ हर icon के लिए PNG: @1x, @2x, @3x अलग-अलग
❌ Dark mode में रंग बदलना हो तो नई image बनाओ
❌ बहुत सारी images = app size बड़ा
❌ PNG बड़ा करो तो blur हो जाता है
Vector icons: एक font file, हज़ारों icons, color/size सिर्फ prop से!
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Icon set is packaged as a font file (.ttf) with glyphs
Step 2 → Library maps names ("home") -> glyph codepoint
Step 3 → Font must be LOADED in the app (Expo: auto/at startup; CLI: link in native project)
Step 4 → <Icon name size color/> renders a <Text> with that glyph
Step 5 → Android/iOS draw the glyph using the font -> sharp at any size
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Icon set एक font file (.ttf) में glyphs की तरह होता है
Step 2 → Library नाम ("home") को glyph code से map करती है
Step 3 → Font app में LOAD होना ज़रूरी है (Expo: automatic; CLI: native में link)
Step 4 → <Icon name size color/> अंदर से एक <Text> render करता है
Step 5 → Android/iOS font से glyph draw करते हैं -> हर size पर sharp
```

---

## 🟡 Real World Example
**Zomato** bottom tab bar (Home, Search, Cart, Profile) and **Swiggy** star-rating and location pin icons are classic icon use cases. **Paytm** uses icon + label grids for "Recharge", "Bill Pay", "Send Money". In RN you would use an icon component plus `<Text>` label for each tile.

## 🟡 Real Example Hindi mein
**Zomato** के bottom tab bar (Home, Search, Cart, Profile) और **Swiggy** के star-rating व location pin icons इसके classic use cases हैं। **Paytm** में "Recharge", "Bill Pay", "Send Money" जैसे grid में icon + label होता है। RN में हर tile के लिए icon component + `<Text>` label लगाते हैं।

---

## 💻 Code Example — Basic
```jsx
// Basic: show icons from different sets (Expo)
// Install (usually already present in Expo): npx expo install @expo/vector-icons
import React from 'react';                                   // React import
import { View, Text, StyleSheet } from 'react-native';       // core components
import { Ionicons, MaterialIcons, FontAwesome } from '@expo/vector-icons'; // 3 icon sets

export default function BasicIcons() {                       // component
  return (
    <View style={styles.row}>{/* horizontal row */}
      <Ionicons name="home" size={32} color="#f97316" />{/* Ionicons home, orange */}
      <MaterialIcons name="delivery-dining" size={32} color="#e23744" />{/* Material icon */}
      <FontAwesome name="star" size={28} color="gold" />{/* FontAwesome star */}
      <Text style={styles.label}>Icons ready!</Text>{/* normal text next to icons */}
    </View>
  );
}

const styles = StyleSheet.create({                           // styles object
  row: { flexDirection: 'row', alignItems: 'center', gap: 16, padding: 20 }, // row layout
  label: { fontSize: 16 },                                   // label font
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: reusable <AppIcon /> with name type-safety, platform-aware
// icon names and a pressable icon button with accessibility
import React from 'react';                                   // React
import { Pressable, Platform, StyleSheet, View, Text } from 'react-native'; // RN parts
import { Ionicons } from '@expo/vector-icons';               // Ionicons set

// Map of our own semantic names -> actual icon names per platform
const ICONS = {
  share: Platform.select({                                   // iOS & Android share look different
    ios: 'share-outline',                                    // iOS style share icon
    default: 'share-social-outline',                         // Android style share icon
  }),
  cart: 'cart-outline',                                      // same on both
  back: Platform.select({ ios: 'chevron-back', default: 'arrow-back' }), // iOS chevron, Android arrow
};

// Reusable icon component: change icon library in ONE place later
export function AppIcon({ name, size = 24, color = '#111' }) {
  const glyph = ICONS[name];                                 // look up real icon name
  if (!glyph) {                                              // guard: unknown semantic name
    if (__DEV__) console.warn(`AppIcon: unknown icon "${name}"`); // warn only in dev
    return null;                                             // render nothing instead of crashing
  }
  return <Ionicons name={glyph} size={size} color={color} />; // actual icon
}

// Icon button with big touch area + accessibility label
export function IconButton({ name, onPress, label, badge }) {
  return (
    <Pressable
      onPress={onPress}                                      // tap handler
      accessibilityRole="button"                             // screen readers: it's a button
      accessibilityLabel={label}                             // screen readers read this
      hitSlop={10}                                           // bigger touch area than the icon
      style={({ pressed }) => [styles.btn, pressed && styles.pressed]} // pressed feedback
    >
      <AppIcon name={name} size={26} />{/* the icon */}
      {badge > 0 && (                                        // show badge only when count > 0
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{badge}</Text>{/* cart count */}
        </View>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: { padding: 8 },                                       // padding around icon
  pressed: { opacity: 0.5 },                                 // fade when pressed
  badge: {                                                   // red count bubble
    position: 'absolute', top: 0, right: 0,                  // top-right corner
    minWidth: 16, height: 16, borderRadius: 8,               // circle
    backgroundColor: '#e23744', alignItems: 'center', justifyContent: 'center',
  },
  badgeText: { color: '#fff', fontSize: 10, fontWeight: '700' }, // white count
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Design language | Material icons (`arrow-back`) | SF-style icons (`chevron-back`) |
| Font loading (CLI) | Fonts copied via `android/app/build.gradle` (`fonts.gradle`/auto) | Fonts listed in `Info.plist` -> `UIAppFonts` |
| Font loading (Expo) | Automatic with `@expo/vector-icons` | Automatic |
| Back icon convention | Arrow | Chevron |
| Tap feedback | Ripple (`android_ripple`) | Opacity fade |
| Size rendering | Same sharp glyph | Same sharp glyph |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: nothing to link. Just import.
import { Ionicons } from '@expo/vector-icons';              // pre-installed in managed Expo
<Ionicons name="home" size={24} color="red" />;              // use directly
```
CLI way:
```jsx
// CLI: npm install react-native-vector-icons  (check current docs: newer versions split into per-set packages)
// Then link fonts: iOS -> add font names in Info.plist (UIAppFonts) + pod install
//                  Android -> apply fonts.gradle in android/app/build.gradle (version-dependent)
import Ionicons from 'react-native-vector-icons/Ionicons';   // import ONE set (smaller bundle)
<Ionicons name="home" size={24} color="red" />;              // same usage
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Wrong icon name (shows "?" box)
```jsx
<Ionicons name="Home" size={24} />   // ❌ name is case-sensitive, 'Home' doesn't exist
```
✅ Correct:
```jsx
<Ionicons name="home" size={24} />   // ✅ check names on icons.expo.fyi
```

❌ Mistake 2: Importing the whole library / many sets
```jsx
import * as Icons from '@expo/vector-icons';  // ❌ pulls every set into bundle
```
✅ Correct: `import { Ionicons } from '@expo/vector-icons';` — only the set you use.

❌ Mistake 3: Icon-only button without accessibility label or touch area
```jsx
<Ionicons name="cart" size={16} onPress={go} />   // ❌ tiny touch target, no label
```
✅ Correct: wrap in `Pressable` with `hitSlop` + `accessibilityLabel` (see Advanced example).

❌ Mistake 4 (CLI): icons show as "?" in release build because fonts were not linked.
✅ Correct: link fonts (Info.plist / gradle) and rebuild the native app — Fast Refresh won't fix it.

---

## 🧠 Tricky Interview Question
**Q: Your icons work in Expo Go but show `?` in the CLI app (or in the production build). Why?**

**Answer:** Vector icons are **fonts**. In Expo, the font is loaded for you. In a bare/CLI app the `.ttf` must be bundled natively (Info.plist `UIAppFonts` on iOS, gradle font copy on Android). If the native project was not updated (or you only reloaded JS, not rebuilt), the glyph cannot be found and the OS draws a "?" box. Fix: link fonts, `pod install`, rebuild. In Expo with `expo-font` and custom icon fonts, make sure the font is loaded (`useFonts`) **before** rendering.

---

## ⚫ Interview Questions + Answers

**Q1: Why use vector icons over PNG images?**
A1: Scalable without blur, tinted via `color`, small app size (one font for thousands of icons), easy dark-mode support.

**Q2: How do you add a custom icon set (e.g. from IcoMoon/Fontello)?**
A2: Generate a font + JSON glyph map, then use `createIconSet(glyphMap, 'FontName', 'font.ttf')` (exists in both `@expo/vector-icons` and `react-native-vector-icons`). In Expo load the font with `expo-font`.

**Q3: What is the difference between `@expo/vector-icons` and `react-native-vector-icons`?**
A3: `@expo/vector-icons` is a wrapper bundled with Expo that handles font loading automatically. `react-native-vector-icons` is the original library needing native font linking in CLI projects.

**Q4: When should you use SVG instead of icon fonts?**
A4: For multi-colour icons, brand logos, or custom illustrations — use `react-native-svg`. Icon fonts are single-colour only.

**Q5: How do you make an icon accessible?**
A5: Icon itself is decorative; wrap in `Pressable` with `accessibilityRole="button"` and `accessibilityLabel`, and give a minimum ~44x44 touch area (`hitSlop`/padding).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Single-colour UI icons (tabs, headers, buttons, ratings)
- You want colour/size changes by props (themes, dark mode)

❌ Avoid when:
- Multi-colour logos/illustrations (use SVG / PNG)
- Very custom animated icons (use Lottie / Reanimated + SVG)
- You only need 1-2 icons and want zero dependency (a small SVG may be lighter)

---

## 📊 Visual Diagram
```
<Ionicons name="home" size={24} color="red" />
        │
        ▼
 glyph map: "home" -> U+F144
        │
        ▼
 Font file Ionicons.ttf (loaded natively)
        │
        ▼
 <Text style={{fontFamily:'Ionicons', fontSize:24, color:'red'}}></Text>
        │
        ▼
 Android TextView / iOS UILabel draws glyph  -> sharp icon
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Icon font | Font whose characters are icons | ऐसा font जिसके characters icons हैं |
| Glyph | One drawable character in a font | Font का एक drawable character |
| Glyph map | Name -> codepoint mapping | नाम से code का mapping |
| `hitSlop` | Extra touchable area | Extra touch area |
| SVG | Vector image, can be multi-colour | Multi-colour vector image |
| `createIconSet` | Build custom icon component | Custom icon set बनाने का function |

---

## ⚡ 3-Line Summary
**English:**
1. Vector icons are font glyphs rendered via `<Ionicons name size color />`.
2. Expo auto-loads fonts; CLI needs native font linking, else you see `?`.
3. Import one set only, and add accessibility label + touch area for icon buttons.

**Hindi:**
1. Vector icons font के glyphs होते हैं जो `<Ionicons name size color />` से दिखते हैं।
2. Expo font खुद load करता है; CLI में native linking ज़रूरी है वरना `?` दिखता है।
3. सिर्फ एक icon set import करो, और icon button में accessibility label + touch area दो।

---

## ➡️ Next Topic
**57. Icons — Expo Icons** — `@expo/vector-icons` की details और icon directory से नाम खोजना।
