# 21. View Component
# हिंदी में: View Component (Layout का बुनियादी डिब्बा)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs)। `View` core component है, कोई install नहीं चाहिए।

---

## 🔵 Simple Definition (English)
`View` is the most basic container in React Native. It maps to `UIView` on iOS and `android.view.ViewGroup` on Android, and is used for layout, styling and grouping other components. It is like a `<div>` on the web, but text must go inside `<Text>`.

## 🔵 सरल परिभाषा (Hindi)
`View` React Native का सबसे बुनियादी container है। यह iOS में `UIView` और Android में `ViewGroup` बनता है। Layout, styling और components को group करने के लिए इस्तेमाल होता है। वेब के `<div>` जैसा, पर text हमेशा `<Text>` के अंदर रखना होता है।

---

## 🔴 Problem it Solves
```
❌ Mobile पर <div> नहीं होता; native UI के लिए native views चाहिए
❌ Components को row/column में रखने, padding, border, shadow देने का साधन चाहिए
❌ iOS और Android के अलग-अलग native containers को एक नाम से सँभालना
```

## 🔴 यह क्यों बना? (Hindi)
```
हर UI को कोई parent चाहिए जो layout (Flexbox), रंग, border और touch को संभाले।
View वही parent है, और यह दोनों OS के native view में बदल जाता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → <View style={...}> लिखते हो
Step 2 → React Native (Yoga engine) Flexbox से size और position निकालता है
Step 3 → Native side पर UIView (iOS) / ViewGroup (Android) बनता है
Step 4 → Style props (backgroundColor, borderRadius, padding) लागू होते हैं
Step 5 → Children (Text, Image, दूसरे View) अंदर रखे जाते हैं
Step 6 → Default: flexDirection 'column', और display 'flex'
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → <View style={...}> लिखो
Step 2 → Yoga engine Flexbox से size/position निकालता है
Step 3 → Native view (UIView / ViewGroup) बनता है
Step 4 → Style लागू होती है
Step 5 → अंदर children रखे जाते हैं
Step 6 → Default direction column (ऊपर से नीचे) होती है
```

---

## 🟡 Real World Example
**Zomato** का restaurant card: बाहर एक `View` (card, shadow), उसके अंदर image, नाम, rating और delivery time के अलग `View` rows। **Swiggy** की bottom "View Cart" bar भी एक `View` है। **Paytm** के home grid में हर icon-tile एक `View` है।

## 🟡 Real Example Hindi mein
Zomato में हर restaurant का card एक `View` है जिसके अंदर photo, नाम और rating दूसरे Views/Text में रखे हैं। सब कुछ boxes के अंदर boxes है।

---

## 💻 Code Example — Basic
```jsx
// Basic: Card बनाना View से
import React from 'react';                                    // React
import { View, Text, StyleSheet } from 'react-native';        // core components

export default function RestaurantCard() {
  return (
    <View style={styles.card}>{/* बाहर का card */}
      <View style={styles.row}>{/* row: नाम + rating */}
        <Text style={styles.name}>Biryani House</Text>{/* नाम */}
        <View style={styles.badge}>{/* छोटा badge */}
          <Text style={styles.badgeText}>4.3 ★</Text>{/* rating */}
        </View>
      </View>
      <Text style={styles.sub}>North Indian • 30 min</Text>{/* sub text */}
    </View>
  );
}

const styles = StyleSheet.create({
  card: { margin: 16, padding: 12, borderRadius: 12, backgroundColor: '#fff' }, // card style
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }, // बगल-बगल
  name: { fontSize: 18, fontWeight: '700' },                  // नाम
  badge: { backgroundColor: '#24963f', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 6 }, // हरा badge
  badgeText: { color: '#fff', fontWeight: '600' },            // सफ़ेद text
  sub: { marginTop: 6, color: '#666' },                       // हल्का text
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: Platform-aware shadow, accessibility, pointerEvents, onLayout
import React, { useState } from 'react';                      // state
import { View, Text, Platform, StyleSheet } from 'react-native'; // core

export default function Panel({ disabled = false }) {
  const [size, setSize] = useState({ w: 0, h: 0 });           // measured size

  return (
    <View
      style={[styles.panel, disabled && styles.disabled]}     // शर्त के साथ style
      accessible                                              // screen reader के लिए group
      accessibilityLabel="Offer panel"                        // पढ़ा जाने वाला label
      pointerEvents={disabled ? 'none' : 'auto'}             // disabled तो touch नहीं
      onLayout={(e) => {                                      // layout बनने पर चलता है
        const { width, height } = e.nativeEvent.layout;       // असली size
        setSize({ w: Math.round(width), h: Math.round(height) });
      }}
    >
      <Text>Flat 50% off</Text>
      <Text style={styles.meta}>{size.w} x {size.h}</Text>{/* measured size दिखाओ */}
    </View>
  );
}

const styles = StyleSheet.create({
  panel: {
    margin: 16, padding: 16, borderRadius: 12, backgroundColor: '#fff',
    ...Platform.select({                                      // OS के हिसाब से shadow
      ios: { shadowColor: '#000', shadowOpacity: 0.15, shadowRadius: 8, shadowOffset: { width: 0, height: 4 } },
      android: { elevation: 4 },                              // Android में elevation
    }),
  },
  disabled: { opacity: 0.5 },                                 // धुंधला
  meta: { color: '#888', marginTop: 4 },                      // छोटा text
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Native class | `ViewGroup` (ReactViewGroup) | `UIView` (RCTView) |
| Shadow | `elevation` | `shadowColor/Opacity/Radius/Offset` |
| `overflow` default | `visible` (RN 0.57+ में सही काम) | `visible` |
| `collapsable` prop | ✅ (extra-view हटाने का optimisation) | ❌ ignore |
| Border में बड़े radius + `overflow:'hidden'` | children clip होते हैं | children clip होते हैं |
| Touch ripple | खुद नहीं (Pressable चाहिए) | खुद नहीं |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// View Expo Go में सीधे चलता है
import { View } from 'react-native';
<View style={{ flex: 1 }} />
```
CLI way:
```jsx
// CLI में भी बिल्कुल वही — कोई extra setup नहीं
import { View } from 'react-native';
<View style={{ flex: 1 }} />
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `View` के अंदर सीधे string लिखना
```jsx
<View>Hello</View>   // ❌ error: Text strings must be rendered within a <Text>
```
✅ Correct: `<View><Text>Hello</Text></View>`

❌ Mistake 2: `flex: 1` भूलना, तो View की height content जितनी ही रहती है
✅ Correct: Parent chain में `flex: 1` दो ताकि पूरी screen भरे।

❌ Mistake 3: iOS shadow के साथ `overflow: 'hidden'` लगाना (shadow कट जाती है)
✅ Correct: Shadow वाला outer View और clip वाला inner View अलग रखो।

---

## 🧠 Tricky Interview Question
```jsx
<View style={{ flexDirection: 'row' }}>
  <View style={{ width: 100, height: 50, backgroundColor: 'red' }} />
  <View style={{ flex: 1, height: 50, backgroundColor: 'blue' }} />
</View>
```
**Q: लाल और नीला box कितनी चौड़ाई लेंगे (screen 360 wide)?**

Answer: लाल 100, नीला बाकी यानी 260। `flex: 1` बचा हुआ जगह भर देता है। (Parent row में है, इसलिए main axis horizontal है।)

---

## ⚫ Interview Questions + Answers
Q1: View और div में क्या फ़र्क?
A1: View native view बनता है, default `flexDirection: column`, text सिर्फ `Text` में, CSS नहीं बल्कि StyleSheet objects।

Q2: View clickable होता है?
A2: Plain View नहीं; `onTouchStart` जैसे low-level हैं। `Pressable`/`TouchableOpacity` इस्तेमाल करो।

Q3: `pointerEvents` क्या करता है?
A3: View और उसके children touch events लें या नहीं (`auto`, `none`, `box-none`, `box-only`)।

Q4: `collapsable={false}` कब चाहिए?
A4: Android पर जब layout-only View हटाया जा रहा हो पर आपको उसका native ref चाहिए (जैसे `measure`)।

Q5: Shadow Android पर कैसे?
A5: `elevation` (iOS shadow props Android पर ignore)।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Layout/grouping/card/row/column बनानी हो
- Background, border, shadow, padding देना हो

❌ Avoid when:
- Scrolling list चाहिए (FlatList), text दिखाना (Text), touch चाहिए (Pressable)
- बेवजह गहरे nested Views (performance घटती है)

---

## 📊 Visual Diagram
```
<View style=card>
 ├─ <View style=row>
 │    ├─ <Text> Name </Text>
 │    └─ <View badge><Text>4.3★</Text></View>
 └─ <Text> sub </Text>

JS View ──► Yoga layout ──► Android ViewGroup / iOS UIView
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| View | Basic container | बुनियादी डिब्बा |
| Yoga | Layout engine | layout निकालने वाला engine |
| Flexbox | Layout model | लचीला layout तरीका |
| pointerEvents | Touch control | touch नियंत्रण |
| elevation | Android shadow | Android की छाया |

---

## ⚡ 3-Line Summary
English:
1. `View` is the basic layout container; it maps to native UIView/ViewGroup.
2. Default direction is column; text must be inside `<Text>`.
3. Use Pressable for touch and Platform-specific shadows.

Hindi:
1. `View` बुनियादी layout container है; native view बनता है।
2. Default direction column है; text `<Text>` में ही रखो।
3. Touch के लिए Pressable और OS के हिसाब से shadow इस्तेमाल करो।

---

## ➡️ Next Topic
**22. Text Component** — `View` के अंदर text कैसे दिखाते हैं।
