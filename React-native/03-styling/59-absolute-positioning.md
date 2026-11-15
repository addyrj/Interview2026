# 59. Absolute Positioning
# हिंदी में: Absolute Positioning — Element को कहीं भी रखना
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (React Native 0.76)** — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
In React Native every view is `position: 'relative'` by default. With `position: 'absolute'` a view is taken out of the normal flex layout and placed using `top`, `left`, `right`, `bottom` relative to its **parent**. Siblings ignore it, and it can overlap other views.

## 🔵 सरल परिभाषा (Hindi)
React Native में हर view default रूप से `position: 'relative'` होता है। `position: 'absolute'` देने पर view normal flex layout से बाहर निकल जाता है और `top`, `left`, `right`, `bottom` से अपने **parent** के हिसाब से रखा जाता है। Siblings उसे ignore करते हैं और वह दूसरे views के ऊपर आ सकता है।

---

## 🔴 Problem it Solves
```
FLEX LAYOUT ALONE:
  Views ek ke baad ek (row/column) lagte hain
  Overlap mushkil: badge on icon, close button on image, FAB on list

ABSOLUTE:
  ✅ Badge icon ke corner par
  ✅ Floating Action Button list ke upar
  ✅ Full-screen overlay / loader
  ✅ Image ke upar text
```

## 🔴 यह क्यों बना? (Hindi)
```
Flexbox views को line में रखता है।
पर UI में कई बार एक चीज़ दूसरी के ऊपर चाहिए:
cart icon पर लाल badge, image पर discount tag, list पर floating button।
Absolute positioning यही देता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Parent view (position relative by default) defines the box
Step 2 → Child gets position: 'absolute'
Step 3 → Child removed from flex flow (siblings behave as if it is absent)
Step 4 → top/left/right/bottom measured from PARENT edges
Step 5 → Later siblings draw on top (or use zIndex)
Step 6 → StyleSheet.absoluteFillObject = {position:'absolute', top:0, left:0, right:0, bottom:0}
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Parent एक box define करता है
Step 2 → Child पर position:'absolute'
Step 3 → Child flex flow से बाहर
Step 4 → top/left/right/bottom parent के edges से नापे जाते हैं
Step 5 → zIndex से ऊपर-नीचे का order
```

---

## 🟡 Real World Example
**Swiggy home screen:** the cart icon in the header has a small orange circle with item count at its top-right corner (absolute badge). The "View Cart" bar sticks at the bottom of the restaurant menu above the scrolling list (absolute, `bottom: 0`). Food images have a discount tag "50% OFF" in the bottom-left (absolute).

## 🟡 Real Example Hindi mein
**Swiggy:** header के cart icon पर ऊपर-दाएँ कोने में item count वाला छोटा orange circle (absolute badge)। Menu के नीचे चिपका "View Cart" bar (`bottom: 0`)। Food image पर बाएँ-नीचे "50% OFF" tag भी absolute है।

---

## 💻 Code Example — Basic
```jsx
// Basic: badge on icon using absolute positioning
import React from 'react'; // React
import { View, Text, StyleSheet } from 'react-native'; // core components

export default function BadgeDemo() { // component
  return (
    <View style={styles.screen}>{/* page container */}
      <View style={styles.iconBox}>{/* PARENT: positioning reference */}
        <Text style={styles.icon}>🛒</Text>{/* the icon (emoji for demo) */}
        <View style={styles.badge}>{/* CHILD: absolute */}
          <Text style={styles.badgeText}>3</Text>{/* count */}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, justifyContent: 'center', alignItems: 'center' }, // center
  iconBox: { width: 60, height: 60, backgroundColor: '#eee', borderRadius: 30, justifyContent: 'center', alignItems: 'center' }, // circle
  icon: { fontSize: 28 }, // icon size
  badge: {
    position: 'absolute', // leave normal flow
    top: -4, // 4px above parent top edge
    right: -4, // 4px beyond parent right edge
    backgroundColor: '#fc8019', // Swiggy orange
    minWidth: 20, height: 20, borderRadius: 10, // pill/circle
    justifyContent: 'center', alignItems: 'center', // center text
  },
  badgeText: { color: '#fff', fontSize: 12, fontWeight: '700' }, // count text
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: sticky bottom bar + FAB + full-screen loader overlay
import React, { useState } from 'react'; // React + state
import { View, Text, FlatList, Pressable, ActivityIndicator, StyleSheet, Platform } from 'react-native'; // core

const DATA = Array.from({ length: 30 }, (_, i) => ({ id: String(i), name: `Dish ${i + 1}` })); // fake list

export default function Menu() {
  const [loading, setLoading] = useState(false); // overlay flag

  const checkout = () => { // simulate API call
    setLoading(true); // show overlay
    setTimeout(() => setLoading(false), 1500); // hide after 1.5s
  };

  return (
    <View style={{ flex: 1 }}>{/* PARENT must have size (flex:1) */}
      <FlatList
        data={DATA} // items
        keyExtractor={(i) => i.id} // key
        contentContainerStyle={{ paddingBottom: 90 }} // space so last item is not hidden behind bar
        renderItem={({ item }) => <Text style={styles.row}>{item.name}</Text>} // row
      />

      <Pressable style={styles.fab} onPress={() => {}}>{/* floating button */}
        <Text style={styles.fabText}>+</Text>
      </Pressable>

      <View style={styles.bar}>{/* sticky bottom bar */}
        <Text style={styles.barText}>3 items | ₹420</Text>
        <Pressable onPress={checkout}><Text style={styles.barText}>View Cart ›</Text></Pressable>
      </View>

      {loading && ( // overlay only when loading
        <View style={styles.overlay} pointerEvents="auto">{/* blocks touches underneath */}
          <ActivityIndicator size="large" color="#fff" />
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { padding: 16, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: '#ccc' }, // list row
  fab: { position: 'absolute', right: 16, bottom: 90, width: 56, height: 56, borderRadius: 28, backgroundColor: '#e23744', justifyContent: 'center', alignItems: 'center', ...Platform.select({ android: { elevation: 6 }, ios: { shadowOpacity: 0.3, shadowRadius: 4, shadowOffset: { width: 0, height: 2 } } }) }, // FAB
  fabText: { color: '#fff', fontSize: 28 }, // plus sign
  bar: { position: 'absolute', left: 0, right: 0, bottom: 0, height: 64, backgroundColor: '#60b246', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 16 }, // bottom bar stretches full width via left+right
  barText: { color: '#fff', fontWeight: '700', fontSize: 16 }, // bar text
  overlay: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', alignItems: 'center' }, // fill entire parent
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Basic `position: 'absolute'` | Same | Same |
| Touch on child outside parent bounds | Often NOT touchable (parent bounds clip touch) | Touchable in many cases |
| `zIndex` | Works; `elevation` also affects order | Works |
| Negative `top/right` (badge outside) | Visible, but touches outside may fail | Visible and usually touchable |
| Safe area (notch/status bar) | Not automatic; use insets | Not automatic; use `SafeAreaView`/insets |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: handle safe-area for absolute bottom bar
import { useSafeAreaInsets } from 'react-native-safe-area-context'; // included in Expo templates
// const insets = useSafeAreaInsets();
// style={{ position:'absolute', bottom: insets.bottom, left:0, right:0 }}
```
CLI way:
```jsx
// Bare CLI: install react-native-safe-area-context yourself
// npm i react-native-safe-area-context && cd ios && pod install
import { useSafeAreaInsets } from 'react-native-safe-area-context'; // same API
// same style code as Expo
```
Absolute positioning itself is core RN — identical in both.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expecting absolute to be relative to the screen.
✅ Correct: It is relative to the nearest parent view. Make the parent `flex: 1` if you want screen-level placement.

❌ Mistake 2: Bottom bar hides the last list item.
✅ Correct: Add `paddingBottom` to the list `contentContainerStyle`.

❌ Mistake 3: Absolute bottom bar overlaps the home indicator/nav bar.
✅ Correct: Add `insets.bottom` from `useSafeAreaInsets`.

❌ Mistake 4: Badge outside parent not tappable on Android.
✅ Correct: Keep touchable area inside the parent bounds or enlarge the parent with padding.

---

## 🧠 Tricky Interview Question
**Q:** A child has `position:'absolute'` but no `top/left/right/bottom`. Where does it appear?

**Answer:** At the position it would have had in the normal flow (static position), but it no longer takes space — siblings behave as if it is not there. So it can overlap the next sibling. Setting `top: 0; left: 0` puts it at the parent's corner.

---

## ⚫ Interview Questions + Answers
Q1: What is the default `position` in RN?
A1: `relative`. Only `relative` and `absolute` exist (no `fixed`/`sticky` in core RN styles).

Q2: How to make a view fill its parent completely?
A2: `StyleSheet.absoluteFill` (or `absoluteFillObject`) — top/left/right/bottom all 0.

Q3: Absolute is relative to what?
A3: Nearest parent view (every View acts as the reference), not the screen.

Q4: How to control which overlapping view is on top?
A4: `zIndex` (and `elevation` on Android). Otherwise later siblings draw on top.

Q5: How to create a sticky header in a scroll view?
A5: `stickyHeaderIndices` on ScrollView/FlatList, not absolute positioning.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Badges, tags, close buttons, FABs, overlays, loaders
- Overlay text on images

❌ Avoid when:
- Normal page layout (use flexbox, it adapts to screen sizes)
- Content with dynamic size (absolute can overlap or get clipped)

---

## 📊 Visual Diagram
```
┌────────────── Parent (flex:1) ─────────────┐
│  ┌─ normal flow ─┐                    (3)  │ ← badge: absolute, top:0, right:0
│  │ Item 1        │                         │
│  │ Item 2        │                         │
│  └───────────────┘                         │
│                                      (+)   │ ← FAB: absolute, right:16, bottom:90
│ ┌─────────────────────────────────────────┐│
│ │ 3 items | ₹420          View Cart ›     ││ ← bar: absolute, left:0,right:0,bottom:0
│ └─────────────────────────────────────────┘│
└────────────────────────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| position absolute | Out of flow, placed by offsets | Flow से बाहर, offsets से |
| absoluteFill | Shortcut to fill parent | Parent पूरा भरना |
| zIndex | Stack order | ऊपर-नीचे का क्रम |
| Overlay | View above other content | ऊपर की परत |
| Safe area | Area free of notch/system bars | Safe क्षेत्र |

---

## ⚡ 3-Line Summary
English: `absolute` removes a view from flex flow and positions it from parent edges.
Use it for badges, FABs, overlays; use `absoluteFill` for full cover.
Mind safe areas and Android touch limits outside parent bounds.

Hindi: `absolute` view को flex flow से निकालकर parent के edges से रखता है।
Badges, FAB, overlays के लिए use करो; पूरा ढकने को `absoluteFill`।
Safe area और Android में parent के बाहर touch की सीमा याद रखो।

---

## ➡️ Next Topic
**60. Dynamic Styling** — ab styles ko state/props/theme ke hisaab se badalna (dark mode, selected state, conditional styles).
