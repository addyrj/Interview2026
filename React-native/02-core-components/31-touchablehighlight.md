# 31. TouchableHighlight
# हिंदी में: TouchableHighlight (दबने पर Background Highlight)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से examples (check current docs — APIs change between SDKs). `TouchableHighlight` अभी भी core में है पर नए code में `Pressable` को prefer किया जाता है।

---

## 🔵 Simple Definition (English)
`TouchableHighlight` makes a view tappable and, while pressed, darkens/colours the background with an `underlayColor` showing through. It must have **exactly one child** view.

## 🔵 सरल परिभाषा (Hindi)
`TouchableHighlight` view को tappable बनाता है और दबे हुए समय में child के पीछे `underlayColor` दिखाता है (background highlight होता है)। इसमें **सिर्फ एक child** होना ज़रूरी है।

---

## 🔴 Problem it Solves
```
❌ List rows (settings, menu items) में tap पर highlight चाहिए
❌ Opacity fade (TouchableOpacity) सब कुछ फीका कर देता है, हमें सिर्फ background बदलना है
❌ iOS-style "row selected" look चाहिए
```

## 🔴 यह क्यों बना? (Hindi)
```
iOS के table rows दबने पर grey हो जाते हैं।
RN में वही behaviour चाहिए था।
TouchableHighlight: child के ऊपर underlay रंग दिखाता है
→ row/menu items के लिए बढ़िया।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → TouchableHighlight एक wrapper View बनाता है
Step 2 → Press शुरू होते ही child की opacity activeOpacity (default 0.85) करता है
Step 3 → साथ में underlayColor पीछे दिखाता है (child का background पारदर्शी हो तो ही दिखे)
Step 4 → उँगली उठाने पर onPress, फिर वापस normal
Step 5 → onShowUnderlay / onHideUnderlay callbacks मिलते हैं
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक wrapper View बनता है
Step 2 → दबते ही child की opacity ~0.85 हो जाती है
Step 3 → पीछे से underlayColor दिखता है
Step 4 → उँगली उठाने पर onPress चलता है
Step 5 → onShowUnderlay / onHideUnderlay से state पता चलती है
```

---

## 🟡 Real World Example
**Paytm** के Profile/Settings menu की rows ("Language", "Help & Support") दबने पर हल्की grey होती हैं। **Zomato** के "Your orders" list की rows में भी ऐसा highlight दिखता है। **Swiggy** के address selection list में चुनी हुई row का background बदलता है।

## 🟡 Real Example Hindi mein
Paytm के settings menu की हर row दबाने पर grey highlight होती है। Zomato के "Your Orders" की rows भी ऐसी ही हैं — यह TouchableHighlight जैसा behaviour है।

---

## 💻 Code Example — Basic
```jsx
// Basic TouchableHighlight — दोनों platforms
import React from 'react';
import { TouchableHighlight, Text, View, StyleSheet, Alert } from 'react-native';

export default function MenuRow() {
  return (
    <TouchableHighlight
      underlayColor="#e0e0e0"                          // दबने पर पीछे का रंग
      onPress={() => Alert.alert('Language', 'Hindi चुनी')} // tap
      style={styles.row}                                // wrapper style
    >
      {/* सिर्फ एक child View — ज़रूरी */}
      <View style={styles.inner}>
        <Text style={styles.label}>Language</Text>
        <Text style={styles.value}>हिंदी ›</Text>
      </View>
    </TouchableHighlight>
  );
}

const styles = StyleSheet.create({
  row: { backgroundColor: '#fff' },                    // normal background
  inner: { flexDirection: 'row', justifyContent: 'space-between', padding: 16 }, // row layout
  label: { fontSize: 16 },
  value: { color: '#888' },
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: selectable list (Swiggy address) + show/hide underlay state + a11y
import React, { useState } from 'react';
import { TouchableHighlight, Text, View, FlatList, StyleSheet } from 'react-native';

const addresses = [
  { id: '1', title: 'Home', line: 'Sector 62, Noida' },
  { id: '2', title: 'Office', line: 'Cyber City, Gurugram' },
];

function AddressRow({ item, selected, onSelect }) {
  const [pressed, setPressed] = useState(false);       // underlay दिख रहा है?

  return (
    <TouchableHighlight
      underlayColor="#fde8d7"                          // हल्का orange
      activeOpacity={0.9}                              // child बस हल्का फीका
      onPress={() => onSelect(item.id)}                // चुनो
      onShowUnderlay={() => setPressed(true)}          // दबा
      onHideUnderlay={() => setPressed(false)}         // छूटा
      accessibilityRole="radio"                        // screen reader के लिए
      accessibilityState={{ selected }}                // selected state
      style={styles.touch}
    >
      <View style={[styles.row, selected && styles.selected]}>
        <Text style={[styles.title, pressed && { color: '#f97316' }]}>{item.title}</Text>
        <Text style={styles.line}>{item.line}</Text>
      </View>
    </TouchableHighlight>
  );
}

export default function AddressList() {
  const [selectedId, setSelectedId] = useState('1');   // चुना हुआ address
  return (
    <FlatList
      data={addresses}
      keyExtractor={a => a.id}
      renderItem={({ item }) => (
        <AddressRow item={item} selected={item.id === selectedId} onSelect={setSelectedId} />
      )}
    />
  );
}

const styles = StyleSheet.create({
  touch: { borderRadius: 8, marginHorizontal: 12, marginTop: 8 },
  row: { padding: 14, borderRadius: 8, backgroundColor: '#fff', borderWidth: 1, borderColor: '#eee' },
  selected: { borderColor: '#f97316' },
  title: { fontWeight: '700', fontSize: 16 },
  line: { color: '#777', marginTop: 2 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Highlight look | underlay + opacity (flat) | underlay + opacity (native table-row जैसा) |
| Ripple | ❌ नहीं (`TouchableNativeFeedback`) | N/A |
| Default `underlayColor` | black (बहुत गहरा लग सकता है) | black |
| Single child rule | ✅ ज़रूरी | ✅ ज़रूरी |
| Common usage | कम (ripple ज़्यादा पसंद) | ज़्यादा (rows) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Core component है — Expo Go में बिना किसी install के चलता है
import { TouchableHighlight, Text } from 'react-native';
<TouchableHighlight underlayColor="#ddd" onPress={() => {}}><Text>Row</Text></TouchableHighlight>
```
CLI way:
```jsx
// CLI में भी वही। कोई pod/gradle कदम नहीं
import { TouchableHighlight, Text } from 'react-native';
<TouchableHighlight underlayColor="#ddd" onPress={() => {}}><Text>Row</Text></TouchableHighlight>
// Native setup में कोई अंतर नहीं — core RN का हिस्सा है
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: एक से ज़्यादा children देना
```jsx
<TouchableHighlight><Text>A</Text><Text>B</Text></TouchableHighlight> // ❌ error
```
✅ Correct: सबको एक `View` में लपेटो।

❌ Mistake 2: Child को `backgroundColor` देना और underlay न दिखना (child background underlay को ढक देता है)
✅ Correct: Highlight रंग चाहिए तो background `TouchableHighlight` की style में दो, child पारदर्शी रखो।

❌ Mistake 3: `underlayColor` न देना (default काला जैसा लगता है)
✅ Correct: हल्का रंग दो।

---

## 🧠 Tricky Interview Question
**Q: TouchableHighlight में child पर `backgroundColor: '#fff'` है, और underlayColor 'red'। दबाने पर red दिखेगा?**

Answer: नहीं (या लगभग नहीं)। Underlay child के **पीछे** दिखता है; opaque child background उसे ढक देता है। सिर्फ child की opacity थोड़ी घटती है जिससे हल्का सा underlay झलकता है। सही तरीका: background रंग wrapper (`style` of TouchableHighlight) पर दो और child पारदर्शी रखो, या `Pressable` से pressed state में style बदलो।

---

## ⚫ Interview Questions + Answers
Q1: TouchableHighlight और TouchableOpacity में अंतर?
A1: Opacity सिर्फ children फीके करता है; Highlight पीछे underlay रंग भी दिखाता है और एक ही child लेता है।

Q2: `underlayColor` क्या है?
A2: दबे समय में child के पीछे दिखने वाला रंग।

Q3: `activeOpacity` default?
A3: TouchableHighlight में लगभग 0.85 (TouchableOpacity में 0.2)।

Q4: इसके callbacks?
A4: `onPress`, `onLongPress`, `onShowUnderlay`, `onHideUnderlay`, `onPressIn`, `onPressOut`।

Q5: इसे Pressable से कैसे बदलें?
A5: `<Pressable style={({pressed}) => [base, pressed && {backgroundColor:'#e0e0e0'}]}>`।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- List/menu rows में tap highlight
- iOS-style selected look

❌ Avoid when:
- Android ripple चाहिए (`Pressable android_ripple`)
- एक से ज़्यादा direct children हों
- Fully custom pressed animation

---

## 📊 Visual Diagram
```
Normal:                      Pressed:
┌──────────────────────┐     ┌──────────────────────┐
│ Language       हिंदी ›│     │▒Language      हिंदी ›▒│  ← underlayColor दिखा
└──────────────────────┘     └──────────────────────┘
  background: white            background: #e0e0e0
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| underlayColor | Colour shown behind child | child के पीछे का रंग |
| onShowUnderlay | Called when highlight appears | highlight दिखने पर call |
| Single child | Only one direct child allowed | सिर्फ एक child |
| activeOpacity | Child opacity when pressed | दबे समय की opacity |

---

## ⚡ 3-Line Summary
English:
1. TouchableHighlight shows a background colour (`underlayColor`) while pressed.
2. It needs exactly one child and a non-opaque child background.
3. For new code, `Pressable` gives the same plus more control.

Hindi:
1. TouchableHighlight दबने पर background रंग (`underlayColor`) दिखाता है।
2. इसमें एक ही child चाहिए और child का background opaque नहीं होना चाहिए।
3. नए code में `Pressable` से यही और ज़्यादा control मिलता है।

---

## ➡️ Next Topic
**32. TouchableNativeFeedback** — Android का Material ripple effect।
