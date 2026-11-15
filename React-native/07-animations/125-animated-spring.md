# 125. Animated.spring
# हिंदी में: Animated.spring — Physics आधारित Bouncy Animation
# Platform: Android ✅ | iOS ✅ | Both ✅

---

**Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs).** `Animated.spring` core RN में है।

---

## 🔵 Simple Definition (English)
**Animated.spring** moves a value to a target using spring physics, like a real spring: it can overshoot and bounce before settling. You control it with `friction` + `tension`, or `speed` + `bounciness`, or `stiffness` + `damping` + `mass`. There is no fixed duration.

## 🔵 सरल परिभाषा (Hindi)
**Animated.spring** असली spring की तरह physics से value को target तक ले जाता है: यह target से आगे निकलकर उछल सकता है और फिर ठहरता है। नियंत्रण `friction` + `tension`, या `speed` + `bounciness`, या `stiffness` + `damping` + `mass` से होता है। इसमें fixed duration नहीं होती।

---

## 🔴 Problem it Solves
```
PROBLEM:
  timing की animation कभी-कभी रोबोट जैसी (mechanical) लगती है.
  Gesture छोड़ने पर बटन/कार्ड का "natural" व्यवहार चाहिए.

SPRING:
  ✅ Natural, जीवंत motion (overshoot + settle)
  ✅ बीच में interrupt करने पर भी smooth (velocity बनी रहती है)
  ✅ Gesture release (velocity से शुरू) के लिए आदर्श
```

## 🔴 यह क्यों बना? (Hindi)
Fixed duration वाली animations मशीनी लगती हैं। असली दुनिया में चीज़ें spring की तरह व्यवहार करती हैं। Spring animation बीच में बदलने पर भी velocity संभालती है, इसलिए gestures और tap feedback में natural लगती है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → value = useRef(new Animated.Value(1)).current
Step 2 → Animated.spring(value, { toValue, ...physics, useNativeDriver }) बनाओ
Step 3 → Physics चुनो (तीनों में से सिर्फ एक set):
         A) bounciness + speed (आसान)
         B) tension + friction (Origami-style)
         C) stiffness + damping + mass (असली physics)
Step 4 → .start(cb) से चलाओ; spring तब रुकती है जब velocity और displacement बहुत छोटे हों
Step 5 → overshootClamping: true हो तो target से आगे नहीं जाएगी
Step 6 → restDisplacementThreshold / restSpeedThreshold से कब "ठहरा" तय होता है
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → value बनाओ
Step 2 → Animated.spring(value, {toValue, ...}) बनाओ
Step 3 → physics का एक set चुनो (bounciness/speed, tension/friction, stiffness/damping/mass)
Step 4 → .start() से चलाओ; velocity बहुत कम होने पर रुकती है
Step 5 → overshootClamping से उछाल रोक सकते हो
Step 6 → thresholds से "ठहरना" तय होता है
```

---

## 🟡 Real World Example
**Zomato** में "Add" बटन दबाने पर थोड़ा सिकुड़कर उछलना (scale spring)। **Instagram** में like का heart उछलकर बैठना। **Paytm/PhonePe** में card swipe छोड़ने पर वापस अपनी जगह स्प्रिंग जैसी लौटना। **Swiggy** की bottom sheet drag छोड़ने पर snap होना।

## 🟡 Real Example Hindi mein
Zomato का Add बटन दबाते ही सिकुड़कर उछलता है, Instagram का heart उछलकर बैठता है, और Paytm का card छोड़ने पर spring की तरह वापस अपनी जगह आता है।

---

## 💻 Code Example — Basic
```jsx
// SpringBasic.jsx — button press पर scale-bounce
import React, { useRef } from 'react';                               // hooks
import { Animated, Pressable, Text, View } from 'react-native';      // core

export default function SpringBasic() {                              // component
  const scale = useRef(new Animated.Value(1)).current;               // scale 1 = सामान्य

  const pressIn = () => {                                            // उंगली दबाई
    Animated.spring(scale, { toValue: 0.92, useNativeDriver: true }).start(); // थोड़ा सिकुड़ो
  };                                                                 // खत्म

  const pressOut = () => {                                           // उंगली उठाई
    Animated.spring(scale, {                                         // spring से लौटो
      toValue: 1,                                                    // सामान्य size
      friction: 3,                                                   // कम friction = ज़्यादा उछाल
      tension: 120,                                                  // spring की कसावट
      useNativeDriver: true,                                         // native thread
    }).start();                                                      // चलाओ
  };                                                                 // खत्म

  return (                                                           // UI
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>{/* centered */}
      <Pressable onPressIn={pressIn} onPressOut={pressOut}>{/* touch events */}
        <Animated.View style={{ backgroundColor: '#e23744', paddingHorizontal: 40, paddingVertical: 14, borderRadius: 10, transform: [{ scale }] }}>{/* animated button */}
          <Text style={{ color: '#fff', fontWeight: '700' }}>ADD</Text>{/* label */}
        </Animated.View>
      </Pressable>
    </View>
  );                                                                 // return खत्म
}                                                                    // component खत्म
```

## 💻 Code Example — Advanced
```jsx
// SnapCard.jsx — drag, छोड़ने पर velocity के साथ spring से वापस; dismiss threshold
import React, { useRef } from 'react';                               // hooks
import { Animated, PanResponder, Text, View, StyleSheet, Dimensions } from 'react-native'; // core

const { width } = Dimensions.get('window');                          // screen चौड़ाई
const THRESHOLD = width * 0.35;                                      // इतना खींचो तो dismiss

export default function SnapCard({ onDismiss }) {                    // prop: dismiss callback
  const pos = useRef(new Animated.ValueXY()).current;                // card की position

  const responder = useRef(PanResponder.create({                     // gesture handler
    onMoveShouldSetPanResponder: (_, g) => Math.abs(g.dx) > 5,       // हल्की हरकत पर pan मानो (तीर-चिह्न scroll से टकराव कम)
    onPanResponderMove: Animated.event([null, { dx: pos.x, dy: pos.y }], { useNativeDriver: false }), // उंगली के साथ चलो
    onPanResponderRelease: (_, g) => {                               // छोड़ने पर
      if (Math.abs(g.dx) > THRESHOLD) {                              // काफी खींचा
        Animated.spring(pos, {                                       // बाहर फेंको
          toValue: { x: Math.sign(g.dx) * width * 1.2, y: g.dy },    // स्क्रीन के बाहर
          velocity: { x: g.vx, y: g.vy },                            // gesture की गति से शुरू (natural!)
          useNativeDriver: false,                                    // PanResponder event के साथ JS driver
        }).start(({ finished }) => { if (finished) onDismiss?.(); });// हट गया तो बताओ
      } else {                                                       // कम खींचा
        Animated.spring(pos, {                                       // वापस केंद्र में
          toValue: { x: 0, y: 0 },                                   // origin
          friction: 5,                                               // हल्का उछाल
          useNativeDriver: false,                                    // वही driver
        }).start();                                                  // चलाओ
      }                                                              // if खत्म
    },                                                               // release खत्म
  })).current;                                                       // स्थिर responder

  const rotate = pos.x.interpolate({ inputRange: [-width, 0, width], outputRange: ['-15deg', '0deg', '15deg'] }); // खींचने पर झुकना

  return (                                                           // UI
    <View style={s.wrap}>{/* container */}
      <Animated.View {...responder.panHandlers} style={[s.card, { transform: [...pos.getTranslateTransform(), { rotate }] }]}>{/* draggable card */}
        <Text style={s.t}>Swipe me away</Text>{/* text */}
      </Animated.View>
    </View>
  );                                                                 // return खत्म
}                                                                    // component खत्म

const s = StyleSheet.create({                                        // styles
  wrap: { flex: 1, alignItems: 'center', justifyContent: 'center' }, // layout
  card: { width: 260, height: 160, borderRadius: 16, backgroundColor: '#fc8019', alignItems: 'center', justifyContent: 'center' }, // card
  t: { color: '#fff', fontWeight: '700' },                           // text
});                                                                  // खत्म
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Physics | वही engine | वही engine |
| Native driver | transform/opacity | transform/opacity |
| Perceived bounce | कम-शक्ति devices पर थोड़ा कम smooth | आम तौर पर ज़्यादा smooth |
| iOS rubber-band | N/A | System scroll bounce अलग है, spring उससे मिलती-जुलती दिख सकती है |
| Gesture + native driver | PanResponder के साथ `useNativeDriver: false` | वही |
| Haptic pair | `expo-haptics` हल्का | Taptic पर बेहतर |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: core API
import { Animated } from 'react-native';                   // core
Animated.spring(v, { toValue: 1, friction: 4, useNativeDriver: true }).start(); // चलाओ
// बेहतर विकल्प: Reanimated  withSpring(1, { damping: 10, stiffness: 120 })
```
CLI way:
```jsx
// CLI: वही core API
import { Animated } from 'react-native';                   // core
Animated.spring(v, { toValue: 1, friction: 4, useNativeDriver: true }).start(); // चलाओ
// Reanimated के लिए: npm i react-native-reanimated + babel plugin + pod install
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `duration` देना (spring में काम नहीं करता)।
✅ Correct: physics params (friction/tension आदि) बदलो।

❌ Mistake 2: Physics के दो अलग sets (bounciness और tension) मिलाना।
✅ Correct: तीनों sets में से सिर्फ एक का उपयोग।

❌ Mistake 3: बहुत कम friction से अंतहीन झूलना।
✅ Correct: friction बढ़ाओ या `overshootClamping: true`।

❌ Mistake 4: Gesture release पर `velocity` न देना।
✅ Correct: `velocity: gestureState.vx` देकर natural feel।

---

## 🧠 Tricky Interview Question
```jsx
Animated.spring(v, { toValue: 1, duration: 2000, useNativeDriver: true }).start();
```
क्या यह 2 सेकंड में पूरी होगी?

Answer: नहीं। Spring में `duration` option नहीं है (RN docs में नहीं); यह physics (friction/tension, stiffness/damping/mass) से तय होता है कि कब ठहरेगा। Property अनदेखी हो जाएगी। फिक्स्ड समय चाहिए तो `Animated.timing` इस्तेमाल करो। (Reanimated के `withSpring` में अलग से duration-based config अलग version में उपलब्ध हो सकता है, docs देखो।)

---

## ⚫ Interview Questions + Answers
Q1: spring बनाम timing?
A1: spring physics और velocity-aware, उछाल देती है, duration नहीं; timing fixed duration/easing।

Q2: Physics के तीन config sets?
A2: bounciness+speed; tension+friction; stiffness+damping+mass।

Q3: `overshootClamping` क्या?
A3: True हो तो value target से आगे नहीं जाती (उछाल बंद)।

Q4: Spring कब "रुकी" मानी जाती है?
A4: जब displacement और speed थ्रेशोल्ड (`restDisplacementThreshold`, `restSpeedThreshold`) से कम हों।

Q5: Gesture के बाद velocity क्यों?
A5: ताकि छोड़ने की गति से animation जारी रहे, झटका न लगे।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Button press feedback
- Gesture release / snap-back
- Playful UI (like, add to cart)

❌ Avoid when:
- सटीक समय चाहिए (progress bar, toast)
- Formal/serious UI (banking forms) में ज़्यादा उछाल
- Reduce motion सक्षम हो

---

## 📊 Visual Diagram
```
 value
 1.2|       .-.
  1 |------/   '-._.-'-----  (target = 1)
    |     /      overshoot -> settle
  0 |____/_______________ time

 timing: सीधा 0 -> 1     spring: 1 से आगे जाकर लौटती है
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| friction | Resistance | घर्षण/रोक |
| tension | Spring tightness | कसावट |
| bounciness | How bouncy | उछालपन |
| overshoot | Goes past target | target से आगे जाना |
| velocity | Starting speed | शुरुआती गति |

---

## ⚡ 3-Line Summary
English: Animated.spring animates with physics, overshooting and settling naturally.
Pick one physics set, pass gesture velocity, and use clamping if needed.
It has no duration option.

Hindi: Animated.spring physics से animate करता है, उछलकर natural ढंग से ठहरता है।
physics का एक set चुनो, gesture velocity दो, ज़रूरत हो तो clamping लगाओ।
इसमें duration नहीं होती।

---

## ➡️ Next Topic
**126. Animated.decay**, अब gesture के बाद momentum (फिसलकर धीमे रुकना) सीखेंगे।
