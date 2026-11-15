# 123. Animated.Value
# हिंदी में: Animated.Value — Animation की मूल Value
# Platform: Android ✅ | iOS ✅ | Both ✅

---

**Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs).** `Animated.Value`, `Animated.ValueXY` core RN में हैं, कोई install नहीं।

---

## 🔵 Simple Definition (English)
**Animated.Value** is a special number that React Native can change over time and connect directly to a style. You pass it into `<Animated.View style={{ opacity: value }}>`, then animate it with `timing`, `spring` or `decay`. `Animated.ValueXY` holds two numbers (x, y) for movement.

## 🔵 सरल परिभाषा (Hindi)
**Animated.Value** एक खास number है जिसे React Native समय के साथ बदल सकता है और सीधे style से जोड़ सकता है। इसे `<Animated.View style={{ opacity: value }}>` में देते हैं और `timing`, `spring` या `decay` से बदलते हैं। `Animated.ValueXY` movement के लिए दो numbers (x, y) रखता है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  useState(0) में opacity रखकर हर frame setState -> हर बार पूरा component re-render.

ANIMATED.VALUE:
  ✅ बदलने पर component re-render नहीं होता (value सीधे view को जाती है)
  ✅ interpolate() से एक value से कई styles
  ✅ setValue(), setOffset(), addListener() जैसे control
  ✅ Native driver के साथ चलता है
```

## 🔴 यह क्यों बना? (Hindi)
State से animate करने पर हर frame पर component re-render होता है, जो भारी है। `Animated.Value` बदलने पर सिर्फ संबंधित view का style बदलता है, component re-render नहीं होता, इसलिए animation smooth रहती है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → const v = useRef(new Animated.Value(0)).current   (render में स्थिर)
Step 2 → Animated.View/Text/Image की style में v (या v.interpolate) दो
Step 3 → Animated.timing(v, {toValue, duration, useNativeDriver}).start()
Step 4 → v की value बदलती है और view सीधे update होता है
Step 5 → v.setValue(n) से तुरंत किसी value पर कूदो
Step 6 → v.interpolate({inputRange, outputRange}) से रंग/डिग्री/px में बदलो
Step 7 → Animated.ValueXY से x और y साथ में (drag)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → useRef में Animated.Value बनाओ
Step 2 → Animated.View की style में दो
Step 3 → timing/spring से बदलो
Step 4 → value बदलते ही view सीधे update होता है
Step 5 → setValue से तुरंत बदल सकते हो
Step 6 → interpolate से रंग, डिग्री आदि में बदलो
Step 7 → ValueXY से x-y movement
```

---

## 🟡 Real World Example
**Swiggy** में delivery progress bar: एक `Animated.Value` (0..1) से bar की चौड़ाई scale होती है। **Paytm** में balance card flip: value 0..1 को 0deg..180deg में interpolate। **Zomato** में scroll के साथ header का opacity: scroll position एक Animated.Value से जुड़ी होती है।

## 🟡 Real Example Hindi mein
Swiggy का progress bar एक Animated.Value (0..1) से चलता है। Paytm का card flip value को 0 से 180 डिग्री में interpolate करता है। Zomato का header scroll की value के साथ धुँधला होता है।

---

## 💻 Code Example — Basic
```jsx
// ValueBasic.jsx — एक value से opacity + scale (interpolate)
import React, { useRef } from 'react';                              // hooks
import { Animated, Button, View } from 'react-native';              // core

export default function ValueBasic() {                              // component
  const v = useRef(new Animated.Value(0)).current;                  // value 0 से शुरू

  const play = () => {                                              // button handler
    v.setValue(0);                                                  // पहले 0 पर कूदो
    Animated.timing(v, { toValue: 1, duration: 700, useNativeDriver: true }).start(); // 0 -> 1
  };                                                                // खत्म

  const scale = v.interpolate({ inputRange: [0, 1], outputRange: [0.5, 1] }); // 0..1 -> 0.5..1 scale

  return (                                                          // UI
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', gap: 20 }}>{/* centered */}
      <Animated.View style={{ width: 100, height: 100, backgroundColor: '#e23744', opacity: v, transform: [{ scale }] }} />{/* एक value से दो styles */}
      <Button title="Play" onPress={play} />{/* चलाओ */}
    </View>
  );                                                                // return खत्म
}                                                                   // component खत्म
```

## 💻 Code Example — Advanced
```jsx
// ValueAdvanced.jsx — listener, offset, flattenOffset, color interpolate, scroll-linked header, ValueXY
import React, { useEffect, useRef, useState } from 'react';          // hooks
import { Animated, PanResponder, Text, View, StyleSheet } from 'react-native'; // core

export default function ValueAdvanced() {                            // component
  const scrollY = useRef(new Animated.Value(0)).current;            // scroll position
  const pan = useRef(new Animated.ValueXY()).current;                // drag position {x, y}
  const [shown, setShown] = useState(0);                            // listener से मिली value

  useEffect(() => {                                                  // listener सेटअप
    const id = scrollY.addListener(({ value }) => setShown(Math.round(value))); // value देखना (सिर्फ debug; बहुत setState से बचो)
    return () => scrollY.removeListener(id);                         // cleanup ज़रूरी
  }, [scrollY]);                                                     // dependency

  // Scroll के साथ header का opacity: 0..100 px scroll पर 1 -> 0
  const headerOpacity = scrollY.interpolate({ inputRange: [0, 100], outputRange: [1, 0], extrapolate: 'clamp' }); // clamp = सीमा के बाहर नहीं
  // Scroll के साथ रंग बदलना (colors interpolate हो सकते हैं, पर native driver नहीं)
  const bg = scrollY.interpolate({ inputRange: [0, 200], outputRange: ['#ffffff', '#ffe0e3'], extrapolate: 'clamp' }); // सफेद -> गुलाबी

  const responder = useRef(PanResponder.create({                     // drag gesture
    onStartShouldSetPanResponder: () => true,                        // touch पकड़ो
    onPanResponderGrant: () => {                                     // शुरू होने पर
      pan.setOffset({ x: pan.x.__getValue(), y: pan.y.__getValue() });// पुरानी position offset बनाओ (private API, RN docs में यही pattern)
      pan.setValue({ x: 0, y: 0 });                                  // delta 0 से शुरू
    },                                                               // grant खत्म
    onPanResponderMove: Animated.event([null, { dx: pan.x, dy: pan.y }], { useNativeDriver: false }), // gesture -> value
    onPanResponderRelease: () => { pan.flattenOffset(); },           // offset को value में मिलाओ
  })).current;                                                       // responder स्थिर

  return (                                                           // UI
    <View style={{ flex: 1 }}>{/* root */}
      <Animated.View style={[s.header, { opacity: headerOpacity }]}><Text>Header (scroll: {shown})</Text></Animated.View>{/* fading header */}
      <Animated.ScrollView
        scrollEventThrottle={16}                                     // 60fps events
        onScroll={Animated.event([{ nativeEvent: { contentOffset: { y: scrollY } } }], { useNativeDriver: false })} // scroll -> value (bg colour के कारण false)
        style={{ backgroundColor: bg }}                              // रंग value से
      >
        <View style={{ height: 900 }} />{/* लंबा content */}
      </Animated.ScrollView>
      <Animated.View {...responder.panHandlers} style={[s.box, { transform: pan.getTranslateTransform() }]} />{/* draggable box */}
    </View>
  );                                                                 // return खत्म
}                                                                    // component खत्म

const s = StyleSheet.create({                                        // styles
  header: { height: 60, justifyContent: 'center', alignItems: 'center' }, // header
  box: { position: 'absolute', bottom: 40, left: 40, width: 70, height: 70, borderRadius: 12, backgroundColor: '#fc8019' }, // box
});                                                                  // खत्म
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Native driver props | transform, opacity | transform, opacity |
| Color interpolate | JS driver ही (native नहीं) | JS driver ही |
| Scroll-linked values | `scrollEventThrottle` कुछ असर नहीं, पर रखना अच्छा | `scrollEventThrottle` ज़रूरी (वरना कम events) |
| Overscroll | Bounce नहीं (negative values नहीं आतीं) | Bounce में negative scrollY आ सकता है, `clamp` लगाओ |
| `addListener` | वही | वही |
| Performance | Listener में setState से jank जल्दी | वही पर कम |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: core Animated, कोई setup नहीं
import { Animated } from 'react-native';                   // core
const v = new Animated.Value(0);                           // value
```
CLI way:
```jsx
// CLI: बिल्कुल वही API
import { Animated } from 'react-native';                   // core
const v = new Animated.Value(0);                           // value
// Reanimated का useSharedValue(0) विकल्प है (अलग install + babel plugin)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `const v = new Animated.Value(0)` component body में (हर render पर reset)।
✅ Correct: `useRef(...).current`।

❌ Mistake 2: `addListener` हटाना भूलना (memory leak)।
✅ Correct: cleanup में `removeListener`।

❌ Mistake 3: Value को सीधे plain View की style में देना।
✅ Correct: `Animated.View/Text/Image/ScrollView`।

❌ Mistake 4: Native-driven और JS-driven को एक ही value पर मिलाना।
✅ Correct: एक value के लिए एक ही mode रखो।

---

## 🧠 Tricky Interview Question
```jsx
const v = useRef(new Animated.Value(0)).current;
Animated.timing(v, { toValue: 1, duration: 300, useNativeDriver: true }).start();
// बाद में उसी v पर:
Animated.timing(v, { toValue: 0, duration: 300, useNativeDriver: false }).start();
```
क्या होगा?

Answer: Error: एक बार किसी node को native driver से animate कर दिया तो उसे बाद में JS driver से animate नहीं कर सकते ("Attempting to run JS driven animation on animated node that has been moved to native earlier"). Native/JS mode value के लिए एक बार तय हो जाता है। समाधान: दोनों जगह एक ही mode, या अलग values।

---

## ⚫ Interview Questions + Answers
Q1: `Animated.Value` और state में फर्क?
A1: Value बदलने पर component re-render नहीं होता; view सीधे update होता है।

Q2: `setOffset` और `flattenOffset`?
A2: `setOffset` base जोड़ता है (drag की पिछली position); `flattenOffset` offset को value में मिलाकर offset 0 कर देता है।

Q3: `extrapolate: 'clamp'` क्यों?
A3: Input range से बाहर output को सीमा पर रोकता है (overscroll में अजीब values नहीं)।

Q4: Current value कैसे पढ़ें?
A4: `addListener` से; `__getValue()` private API है, सावधानी से।

Q5: `Animated.ValueXY` कब?
A5: जब x और y साथ में बदलें (drag, मूवमेंट); `getTranslateTransform()` से style।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Opacity/scale/translate जैसी animations
- Scroll-linked effects
- Drag gestures (PanResponder के साथ)

❌ Avoid when:
- जटिल gestures (Reanimated बेहतर)
- Value को बार-बार setState में बदलना हो
- सरल show/hide (conditional render काफी)

---

## 📊 Visual Diagram
```
 Animated.Value v (0..1)
      |
      +--> opacity: v
      +--> interpolate -> scale 0.5..1
      +--> interpolate -> rotate 0..180deg
      |
 Animated.timing(v) -> v बदलती है -> सभी जुड़ी styles एक साथ बदलती हैं
 (component re-render नहीं)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Animated.Value | Animatable number | Animate होने वाला number |
| interpolate | Map ranges | Range मैप करना |
| extrapolate | Behaviour outside range | Range के बाहर का व्यवहार |
| Offset | Base added to value | Value में जुड़ा आधार |
| addListener | Watch value changes | Value बदलाव सुनना |

---

## ⚡ 3-Line Summary
English: Animated.Value is a number you animate and bind to styles without re-rendering.
Keep it in useRef, interpolate it into many styles, and clean listeners.
Do not mix native and JS drivers on one value.

Hindi: Animated.Value ऐसा number है जिसे बिना re-render के animate करके styles से जोड़ते हैं।
इसे useRef में रखो, interpolate से कई styles बनाओ और listeners हटाओ।
एक value पर native और JS driver मत मिलाओ।

---

## ➡️ Next Topic
**124. Animated.timing**, अब value को तय समय और easing के साथ बदलना सीखेंगे।
