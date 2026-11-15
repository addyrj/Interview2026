# 121. Animations in React Native
# हिंदी में: React Native में Animations का परिचय
# Platform: Android ✅ | iOS ✅ | Both ✅

---

**Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs).** Core `Animated` और `LayoutAnimation` बिना install के हैं। Advanced के लिए `react-native-reanimated` v3 (Expo SDK 52 में bundled version, `npx expo install react-native-reanimated`)।

---

## 🔵 Simple Definition (English)
Animation means changing a value smoothly over time (position, size, color, opacity) so the screen feels alive instead of jumping. React Native gives three main tools: the **Animated** API, **LayoutAnimation** (animate layout changes automatically), and **Reanimated** (a faster, UI-thread library).

## 🔵 सरल परिभाषा (Hindi)
Animation यानी किसी value (position, size, color, opacity) को समय के साथ धीरे-धीरे बदलना, ताकि screen झटके से बदलने की जगह जीवंत लगे। React Native में तीन मुख्य tools हैं: **Animated** API, **LayoutAnimation** (layout बदलाव अपने आप animate) और **Reanimated** (तेज़, UI thread पर चलने वाली library)।

---

## 🔴 Problem it Solves
```
PROBLEM:
  setState से हर 16ms पर value बदलकर animate करना = JS thread पर बोझ, झटके (jank).
  Screen अचानक बदलती है तो user समझ नहीं पाता क्या बदला.

ANIMATION TOOLS:
  ✅ Animated: native driver से UI thread पर चलता है (60fps)
  ✅ LayoutAnimation: list/layout बदलाव अपने आप smooth
  ✅ Reanimated: gestures के साथ पूरी तरह UI thread पर
  ✅ बेहतर UX: feedback, ध्यान खींचना, continuity
```

## 🔴 यह क्यों बना? (Hindi)
Animation के लिए हर frame पर setState करने से JS thread पर बोझ पड़ता है और app अटकता है। इसलिए ऐसे APIs बने जो animation का काम native/UI thread को दे देते हैं और value बदलाव को declaratively describe करने देते हैं।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Animation का प्रकार चुनो (Animated / LayoutAnimation / Reanimated)
Step 2 → एक animated value बनाओ (new Animated.Value(0))
Step 3 → उसे style से जोड़ो (<Animated.View style={{opacity: value}}>)
Step 4 → Animation चलाओ (Animated.timing(value, {...}).start())
Step 5 → useNativeDriver: true दो तो calculation native side पर होता है
Step 6 → Value हर frame बदलती है और native view सीधे update होता है
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Tool चुनो (Animated / LayoutAnimation / Reanimated)
Step 2 → Animated value बनाओ
Step 3 → उसे Animated.View की style से जोड़ो
Step 4 → Animated.timing(...).start() से चलाओ
Step 5 → useNativeDriver: true से native thread पर चलाओ
Step 6 → हर frame पर view सीधे update होता है
```

---

## 🟡 Real World Example
**Zomato** में cart में item जाते समय छोटा bounce, **Swiggy** में order tracking पर rider का smooth movement, **Paytm/PhonePe** में payment success का check-mark animation, **Instagram** में like पर heart pop। सब user को बताते हैं कि "action हो गया"।

## 🟡 Real Example Hindi mein
Zomato में item add करने पर bounce, PhonePe में payment सफल होने पर check-mark animation, Instagram में like पर heart pop। हर animation user को बताता है कि action हो गया।

---

## 💻 Code Example — Basic
```jsx
// FadeIn.jsx — सबसे simple animation: fade in
import React, { useEffect, useRef } from 'react';                  // hooks
import { Animated, Text, View } from 'react-native';               // Animated API

export default function FadeIn() {                                 // component
  const opacity = useRef(new Animated.Value(0)).current;           // शुरुआती opacity 0 (re-render पर वही object)

  useEffect(() => {                                                // mount पर
    Animated.timing(opacity, {                                     // समय आधारित animation
      toValue: 1,                                                  // अंत में 1 (पूरा दिखे)
      duration: 600,                                               // 600 ms
      useNativeDriver: true,                                       // native thread पर चलाओ
    }).start();                                                    // शुरू
  }, [opacity]);                                                   // dependency

  return (                                                         // UI
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>{/* centered */}
      <Animated.View style={{ opacity }}>{/* animated wrapper */}
        <Text style={{ fontSize: 24 }}>Welcome to Zomato</Text>{/* text */}
      </Animated.View>
    </View>
  );                                                               // return खत्म
}                                                                  // component खत्म
```

## 💻 Code Example — Advanced
```jsx
// ExpandCard.jsx — LayoutAnimation + Animated + Android flag + reduce-motion respect
import React, { useEffect, useRef, useState } from 'react';        // hooks
import { Animated, LayoutAnimation, Platform, Pressable, Text, UIManager, View, AccessibilityInfo, StyleSheet } from 'react-native'; // core

// Android पर LayoutAnimation के लिए यह flag (old architecture में ज़रूरी)
if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) { // function है तो
  UIManager.setLayoutAnimationEnabledExperimental(true);           // चालू करो
}                                                                  // if खत्म

export default function ExpandCard() {                             // component
  const [open, setOpen] = useState(false);                         // card खुला है?
  const [reduce, setReduce] = useState(false);                     // user ने reduce motion रखा?
  const rotate = useRef(new Animated.Value(0)).current;            // arrow rotation value

  useEffect(() => {                                                // mount पर accessibility check
    AccessibilityInfo.isReduceMotionEnabled().then(setReduce);     // setting पढ़ो
  }, []);                                                          // एक बार

  const toggle = () => {                                           // press handler
    if (!reduce) {                                                 // motion की अनुमति हो तभी
      LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut); // अगले layout बदलाव को animate करो
    }                                                              // if खत्म
    setOpen((o) => !o);                                            // layout बदलो
    Animated.timing(rotate, {                                      // arrow घुमाओ
      toValue: open ? 0 : 1,                                       // बंद->0, खुला->1
      duration: reduce ? 0 : 250,                                  // reduce motion में तुरंत
      useNativeDriver: true,                                       // native
    }).start();                                                    // शुरू
  };                                                               // खत्म

  const deg = rotate.interpolate({ inputRange: [0, 1], outputRange: ['0deg', '180deg'] }); // 0..1 -> डिग्री

  return (                                                         // UI
    <View style={s.card}>{/* card */}
      <Pressable onPress={toggle} style={s.head}>{/* header */}
        <Text style={s.title}>Order details</Text>{/* title */}
        <Animated.Text style={{ transform: [{ rotate: deg }] }}>▼</Animated.Text>{/* घूमता arrow */}
      </Pressable>
      {open && <Text style={s.body}>2 x Biryani, 1 x Raita. Delivery in 25 min.</Text>}{/* खुलने वाला हिस्सा */}
    </View>
  );                                                               // return खत्म
}                                                                  // component खत्म

const s = StyleSheet.create({                                      // styles
  card: { margin: 24, padding: 16, borderRadius: 12, backgroundColor: '#fff', elevation: 3 }, // card
  head: { flexDirection: 'row', justifyContent: 'space-between' }, // header row
  title: { fontWeight: '700' },                                    // title
  body: { marginTop: 12 },                                         // body
});                                                                // खत्म
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| LayoutAnimation | `setLayoutAnimationEnabledExperimental(true)` चाहिए (old arch) | Default चालू |
| Shadow animate | `elevation` (native driver से animate नहीं होता) | `shadow*` props |
| Native driver | सब transform/opacity supported | वही |
| Reduce motion | Settings > Remove animations | Settings > Reduce Motion |
| Performance | Low-end devices पर जल्दी jank | ज़्यादातर smooth |
| Easing feel | Material (ease-out standard) | Spring-जैसी natural feel |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: Animated core + Reanimated bundled version
import { Animated } from 'react-native';                      // core
// npx expo install react-native-reanimated  (SDK के अनुसार सही version)
// babel.config.js: babel-preset-expo में Reanimated plugin अपने आप जुड़ता है (SDK 50+)
```
CLI way:
```jsx
// CLI: Animated core वही; Reanimated खुद configure
import { Animated } from 'react-native';                      // core
// npm i react-native-reanimated; cd ios && pod install
// babel.config.js plugins: ['react-native-reanimated/plugin']  (सबसे आखिर में)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `new Animated.Value(0)` को component body में सीधे बनाना (हर render पर नई value)।
✅ Correct: `useRef(new Animated.Value(0)).current`।

❌ Mistake 2: `useNativeDriver` भूल जाना (JS thread पर चलेगा, jank)।
✅ Correct: transform/opacity पर `useNativeDriver: true`।

❌ Mistake 3: Android पर LayoutAnimation चालू किए बिना चलाना।
✅ Correct: `UIManager.setLayoutAnimationEnabledExperimental(true)` (जहाँ ज़रूरी)।

❌ Mistake 4: Reduce motion को नज़रअंदाज़ करना।
✅ Correct: `AccessibilityInfo.isReduceMotionEnabled()`।

---

## 🧠 Tricky Interview Question
```jsx
Animated.timing(v, { toValue: 100, duration: 500, useNativeDriver: true }).start();
// v को width में use किया: <Animated.View style={{ width: v }} />
```
क्या यह काम करेगा?

Answer: नहीं, error आएगा। Native driver सिर्फ non-layout properties (transform, opacity) animate करता है। `width/height/top/left/margin` layout properties हैं जिन्हें native driver support नहीं करता। समाधान: `useNativeDriver: false` (JS thread पर), या `transform: [{ scaleX }]` use करो, या Reanimated जो layout props भी UI thread पर चला सकता है।

---

## ⚫ Interview Questions + Answers
Q1: Animated और Reanimated में फर्क?
A1: Animated core है और declarative values/native driver देता है; Reanimated UI thread पर worklets चलाता है, gestures के साथ बेहतर और layout props भी।

Q2: `useNativeDriver` क्या करता है?
A2: Animation का description native side भेज देता है, इसलिए JS thread busy हो तब भी smooth।

Q3: LayoutAnimation कब?
A3: जब list/view add-remove या size बदले और आप अपने-आप smooth transition चाहते हैं।

Q4: Animation 60fps पर चले, इसके लिए?
A4: Native driver, transform/opacity, `InteractionManager`, भारी काम JS thread से हटाना।

Q5: Interpolation क्या?
A5: Input range को output range में map करना (0..1 को 0deg..180deg)।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Feedback (tap, success, error)
- Screen/element transitions
- Loading/skeleton effects

❌ Avoid when:
- हर चीज़ पर (user थक जाता है)
- Reduce motion चालू हो
- Low-end devices पर भारी effects

---

## 📊 Visual Diagram
```
 Animated.Value (0 -> 1)
      |
      v
 timing / spring / decay
      |            useNativeDriver: true
      v                    |
 JS thread  ---------->  UI thread
      |                    |
      +------ हर frame ---> View update (60fps)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Animated.Value | Number that changes over time | समय के साथ बदलने वाला number |
| Interpolation | Map input range to output | Range को दूसरी range में बदलना |
| Native driver | Run on native thread | Native thread पर चलाना |
| LayoutAnimation | Auto animate layout changes | Layout बदलाव अपने-आप animate |
| Worklet | Reanimated UI-thread function | UI thread पर चलने वाला function |

---

## ⚡ 3-Line Summary
English: RN animations change values over time using Animated, LayoutAnimation or Reanimated.
Use the native driver for transform and opacity to keep 60fps.
Always keep values in useRef and respect reduce motion.

Hindi: RN में animations Animated, LayoutAnimation या Reanimated से values को समय के साथ बदलती हैं।
60fps के लिए transform और opacity पर native driver use करो।
Values को useRef में रखो और reduce motion का सम्मान करो।

---

## ➡️ Next Topic
**122. Animated API** (पहले से notes में), फिर **123. Animated.Value** जिसमें animation की नींव, value, को विस्तार से देखेंगे।
