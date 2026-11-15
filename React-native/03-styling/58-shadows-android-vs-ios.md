# 58. Shadows (Android vs iOS difference)
# हिंदी में: Shadows — Android और iOS का फ़र्क
# Platform: Android ✅ | iOS ✅ | Both ✅ (different APIs)

> Target: **Expo SDK 52 (React Native 0.76)** — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
A **shadow** gives a card or button depth so it looks lifted above the screen. iOS uses `shadowColor`, `shadowOffset`, `shadowOpacity`, `shadowRadius`. Android uses a single `elevation` number. To look same on both, you write both sets of styles.

## 🔵 सरल परिभाषा (Hindi)
**Shadow** card या button को depth देता है, जैसे वह screen से ऊपर उठा हो। iOS में `shadowColor`, `shadowOffset`, `shadowOpacity`, `shadowRadius` चलते हैं। Android में सिर्फ `elevation` number चलता है। दोनों पर एक जैसा दिखाने के लिए दोनों के styles लिखने पड़ते हैं।

---

## 🔴 Problem it Solves
```
PROBLEM:
  CSS: box-shadow: 0 2px 4px rgba(0,0,0,0.2)   ← React Native me nahi (old arch)
  iOS shadow props → Android par kuch nahi karte
  Android elevation → iOS par kuch nahi karta

RESULT: Card iOS par floating dikhta hai, Android par flat (ya ulta)

SOLUTION: Platform-specific shadow styles (Platform.select)
  or the newer `boxShadow` style (RN 0.76+, New Architecture only)
```

## 🔴 यह क्यों बना? (Hindi)
```
iOS और Android के native shadow systems अलग हैं।
iOS: Core Animation layer shadow (4 props)
Android: Material Design elevation (1 number)
RN ने दोनों को expose किया, इसलिए दोनों के props अलग हैं।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → iOS: set shadowColor + shadowOffset + shadowOpacity + shadowRadius
Step 2 → Android: set elevation (higher number = bigger shadow)
Step 3 → Use Platform.select({ ios: {...}, android: {...} }) to combine
Step 4 → IMPORTANT: iOS shadow needs a background color on the view
Step 5 → IMPORTANT: overflow:'hidden' clips the iOS shadow (use wrapper view)
Step 6 → Optional: boxShadow (RN 0.76+, New Architecture) works on both
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → iOS: shadowColor, shadowOffset, shadowOpacity, shadowRadius
Step 2 → Android: elevation (नंबर जितना बड़ा, shadow उतना बड़ा)
Step 3 → Platform.select से दोनों को जोड़ो
Step 4 → iOS shadow के लिए view पर backgroundColor ज़रूरी है
Step 5 → overflow:'hidden' iOS shadow काट देता है — wrapper view use करो
```

---

## 🟡 Real World Example
**Zomato restaurant card:** a white card with soft shadow, rounded corners and an image on top. Images need `overflow: 'hidden'` for rounded corners, but that clips the iOS shadow, so developers use an outer View (shadow) and an inner View (overflow hidden + borderRadius).

## 🟡 Real Example Hindi mein
**Zomato restaurant card:** सफ़ेद card, हल्की shadow, rounded corners और ऊपर image। Image के corners round करने को `overflow:'hidden'` चाहिए, पर वह iOS shadow काट देता है। इसलिए बाहर वाला View shadow देता है और अंदर वाला View overflow hidden + borderRadius।

---

## 💻 Code Example — Basic
```jsx
// Basic cross-platform shadow
import React from 'react'; // React
import { View, Text, StyleSheet, Platform } from 'react-native'; // core

export default function ShadowBasic() { // component
  return (
    <View style={styles.screen}>{/* grey background so shadow is visible */}
      <View style={styles.card}>{/* the card */}
        <Text style={styles.title}>Biryani House</Text>{/* title */}
        <Text>4.5 ★ • 30 min</Text>{/* meta */}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#f2f2f2', padding: 24, justifyContent: 'center' }, // page
  card: {
    backgroundColor: '#fff', // REQUIRED for iOS shadow to show
    borderRadius: 12, // rounded corners
    padding: 16, // inner spacing
    ...Platform.select({ // pick per platform
      ios: {
        shadowColor: '#000', // shadow color
        shadowOffset: { width: 0, height: 2 }, // x,y distance
        shadowOpacity: 0.2, // 0 to 1
        shadowRadius: 6, // blur
      },
      android: {
        elevation: 4, // Material elevation
      },
    }),
  },
  title: { fontSize: 18, fontWeight: '700', marginBottom: 4 }, // title
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: reusable shadow presets + card with rounded image (no clipped shadow)
import React from 'react'; // React
import { View, Text, Image, StyleSheet, Platform } from 'react-native'; // core

// Build shadow style from a level (1..3) — one place to maintain
export const shadow = (level = 1) => {
  const h = [0, 1, 3, 6][level]; // height per level
  return Platform.select({
    ios: {
      shadowColor: '#000', // color
      shadowOffset: { width: 0, height: h }, // vertical offset grows
      shadowOpacity: 0.08 + level * 0.06, // stronger per level
      shadowRadius: 2 + level * 2, // blur grows
    },
    android: {
      elevation: level * 2, // 2, 4, 6
      shadowColor: '#000', // Android 9+ (API 28+) tints elevation shadow with this
    },
    default: {}, // web fallback: no shadow
  });
};

export function RestaurantCard({ name, uri }) {
  return (
    <View style={[styles.shadowWrap, shadow(2)]}>{/* OUTER: carries shadow, NO overflow hidden */}
      <View style={styles.clip}>{/* INNER: clips image to rounded corners */}
        <Image source={{ uri }} style={styles.img} />{/* restaurant image */}
        <Text style={styles.name}>{name}</Text>{/* name */}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  shadowWrap: { backgroundColor: '#fff', borderRadius: 14, margin: 16 }, // bg needed for iOS
  clip: { borderRadius: 14, overflow: 'hidden' }, // clip children only
  img: { width: '100%', height: 140 }, // image
  name: { padding: 12, fontSize: 16, fontWeight: '600' }, // text
});

// NEW (RN 0.76+, New Architecture only — version dependent):
// style={{ boxShadow: '0 2px 6px rgba(0,0,0,0.2)' }}  → works on both platforms
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Main prop | `elevation` (number) | `shadowColor/Offset/Opacity/Radius` |
| `shadowColor` | Works only API 28+ (colors the elevation shadow) | Works always |
| `shadowOffset`, `shadowOpacity`, `shadowRadius` | Ignored | Used |
| Needs background color | Yes (otherwise weak shadow) | Yes |
| `overflow: 'hidden'` | Shadow may still show | Clips the shadow |
| Shadow direction | Fixed (from light above) | Controlled by offset |
| z-order effect | elevation also changes z-order | Does not change z-order |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: same style props, nothing to install
const s = { backgroundColor: '#fff', elevation: 4, shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 6, shadowOffset: { width: 0, height: 2 } };
```
CLI way:
```jsx
// Bare CLI: identical style props (core React Native feature)
// No difference in code. boxShadow availability depends on RN version (0.76+ New Arch)
const s = { backgroundColor: '#fff', elevation: 4, shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 6, shadowOffset: { width: 0, height: 2 } };
```
Shadows are core RN, so Expo and CLI behave the same; only the RN version matters.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Only writing iOS shadow props and wondering why Android is flat.
✅ Correct: Add `elevation` (via Platform.select).

❌ Mistake 2: No `backgroundColor` on the shadowed view.
✅ Correct: Give a solid background (e.g. `#fff`).

❌ Mistake 3: `overflow: 'hidden'` on the same view as the shadow (iOS).
✅ Correct: Outer view = shadow, inner view = overflow hidden.

❌ Mistake 4: Using huge elevation like 50.
✅ Correct: Material guidelines use small values (1–12).

---

## 🧠 Tricky Interview Question
**Q:** Your card has `borderRadius: 12`, `overflow: 'hidden'` and iOS shadow props. On iOS the shadow is missing. Why, and fix?

**Answer:** On iOS, `overflow: 'hidden'` clips everything outside the view's bounds, including its own shadow (the shadow is drawn outside the layer). Fix: split into two Views — outer one with shadow + background + borderRadius, inner one with `overflow: 'hidden'` + same borderRadius. On Android, `elevation` is not clipped this way, so it seems fine there — that's why the bug shows only on iOS.

---

## ⚫ Interview Questions + Answers
Q1: How do you add shadow on Android?
A1: Use `elevation`. The `shadow*` props are iOS-only (except `shadowColor` on API 28+).

Q2: How to write one style that works on both?
A2: `Platform.select({ ios: {...shadow props}, android: { elevation } })` or the `boxShadow` prop on RN 0.76+ (New Architecture).

Q3: Does elevation affect layering?
A3: Yes. On Android, higher elevation views draw above lower ones regardless of order, unlike zIndex alone.

Q4: Why does my shadow not show on iOS?
A4: Missing backgroundColor, `shadowOpacity` left at 0 (default), or `overflow: 'hidden'` clipping.

Q5: Is there a CSS-like shadow in RN?
A5: `boxShadow` was added in RN 0.76 and works only with the New Architecture. Check docs for your version.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Cards, floating buttons, modals, bottom sheets
- You need visual hierarchy

❌ Avoid when:
- Long lists with hundreds of shadowed items (can hurt scroll performance, especially on low-end Android)
- Flat design where borders are enough

---

## 📊 Visual Diagram
```
iOS (Core Animation)            Android (Material)
┌──────────────┐                ┌──────────────┐
│    CARD      │                │    CARD      │
└──────────────┘                └──────────────┘
  ░░░░░░░░░░░░░░                  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒
 offset + radius + opacity        elevation: 4  (one number)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| elevation | Android shadow depth | Android shadow की गहराई |
| shadowOffset | iOS shadow x/y distance | Shadow की दूरी |
| shadowRadius | iOS blur amount | Blur की मात्रा |
| shadowOpacity | iOS shadow transparency | Shadow की पारदर्शिता |
| Platform.select | Choose value per OS | OS के हिसाब से value |

---

## ⚡ 3-Line Summary
English: iOS uses four `shadow*` props, Android uses `elevation`.
Combine them with `Platform.select`, and keep a background color on the view.
Do not put `overflow: 'hidden'` on the shadow view on iOS.

Hindi: iOS में चार `shadow*` props, Android में `elevation`।
दोनों को `Platform.select` से जोड़ो और view पर background color रखो।
iOS पर shadow वाले view पर `overflow:'hidden'` मत लगाओ।

---

## ➡️ Next Topic
**59. Absolute Positioning** — shadows ke baad badges, floating buttons aur overlays banane ke liye `position: 'absolute'`.
