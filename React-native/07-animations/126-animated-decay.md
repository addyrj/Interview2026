# 126. Animated.decay
# हिंदी में: Animated.decay — Momentum के साथ धीमे होकर रुकना
# Platform: Android ✅ | iOS ✅ | Both ✅

---

**Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs).** `Animated.decay` core RN में है।

---

## 🔵 Simple Definition (English)
**Animated.decay** starts a value with an initial **velocity** and slows it down gradually until it stops, like a ball sliding on a floor with friction. There is no target value; the final position depends on the starting speed and the **deceleration** rate.

## 🔵 सरल परिभाषा (Hindi)
**Animated.decay** value को एक शुरुआती **velocity** से शुरू करता है और धीरे-धीरे धीमा करके रोक देता है, जैसे फर्श पर फिसलती गेंद। इसमें कोई target नहीं होता; अंतिम स्थान शुरुआती गति और **deceleration** दर से तय होता है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  उंगली से कार्ड को फेंका और छोड़ा तो वह तुरंत रुक जाता है, अप्राकृतिक.
  फ़ोन के scroll जैसा "फिसलकर रुकना" (inertia) चाहिए.

DECAY:
  ✅ Release के बाद momentum
  ✅ velocity gesture से सीधे
  ✅ deceleration से रुकने की गति नियंत्रित
  ✅ कस्टम draggable (carousel, slider) में natural feel
```

## 🔴 यह क्यों बना? (Hindi)
असली दुनिया में चीज़ें छोड़ने पर तुरंत नहीं रुकतीं, घर्षण से धीरे-धीरे रुकती हैं। Decay यही व्यवहार देता है, इसलिए custom draggable elements में scroll जैसा momentum मिलता है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → value = useRef(new Animated.Value(0)).current
Step 2 → Gesture में उंगली के साथ value बदलो (PanResponder/Animated.event)
Step 3 → Release पर gestureState.vx (px/ms) लो
Step 4 → Animated.decay(value, { velocity: vx, deceleration: 0.997, useNativeDriver }).start()
Step 5 → हर frame में velocity घटती है (decay की दर deceleration से)
Step 6 → जब velocity बहुत कम हो, animation रुकती है और finished = true
Step 7 → Boundary चाहिए तो listener में जाँचो और clamp/spring से वापस लाओ
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → value बनाओ
Step 2 → gesture में value बदलो
Step 3 → छोड़ते समय vx लो
Step 4 → Animated.decay(value, {velocity: vx, deceleration}) चलाओ
Step 5 → हर frame में गति घटती है
Step 6 → बहुत कम गति पर रुक जाती है
Step 7 → सीमा चाहिए तो listener में जाँचकर spring से वापस लाओ
```

---

## 🟡 Real World Example
**Zomato/Swiggy** की custom horizontal cuisine carousel जिसे उंगली से झटका दो तो फिसलकर रुकती है। **Paytm** के custom wheel/picker (amount slider) में flick के बाद धीमा होना। **Games/clock-pickers** में dial घुमाकर छोड़ना।

## 🟡 Real Example Hindi mein
Swiggy की custom carousel झटका देने पर फिसलकर रुकती है। Paytm जैसे app के custom picker/slider में flick के बाद धीरे-धीरे रुकना decay से बनता है। (Normal ScrollView/FlatList में यह पहले से built-in है।)

---

## 💻 Code Example — Basic
```jsx
// DecayBasic.jsx — box को झटका देकर फिसलाना
import React, { useRef } from 'react';                                // hooks
import { Animated, PanResponder, View } from 'react-native';          // core

export default function DecayBasic() {                                // component
  const x = useRef(new Animated.Value(0)).current;                    // box की x position

  const responder = useRef(PanResponder.create({                      // gesture
    onStartShouldSetPanResponder: () => true,                         // touch पकड़ो
    onPanResponderGrant: () => {                                      // छूते समय
      x.stopAnimation();                                              // चल रही decay रोको
      x.extractOffset();                                              // अभी की position को offset बनाओ (jump नहीं होगा)
    },                                                                // grant खत्म
    onPanResponderMove: Animated.event([null, { dx: x }], { useNativeDriver: false }), // उंगली के साथ चलाओ
    onPanResponderRelease: (_, g) => {                                // छोड़ने पर
      x.flattenOffset();                                              // offset + value मिलाओ
      Animated.decay(x, {                                             // momentum शुरू
        velocity: g.vx,                                               // उंगली की गति (px/ms)
        deceleration: 0.997,                                          // जितना 1 के पास, उतना देर तक फिसलेगा
        useNativeDriver: false,                                       // PanResponder के साथ JS driver
      }).start();                                                     // चलाओ
    },                                                                // release खत्म
  })).current;                                                        // स्थिर responder

  return (                                                            // UI
    <View style={{ flex: 1, justifyContent: 'center' }}>{/* container */}
      <Animated.View {...responder.panHandlers} style={{ width: 80, height: 80, backgroundColor: '#e23744', borderRadius: 12, transform: [{ translateX: x }] }} />{/* box */}
    </View>
  );                                                                  // return खत्म
}                                                                     // component खत्म
```

## 💻 Code Example — Advanced
```jsx
// BoundedDecay.jsx — decay + सीमा: किनारे से टकराए तो spring से वापस
import React, { useEffect, useRef } from 'react';                     // hooks
import { Animated, Dimensions, PanResponder, StyleSheet, View } from 'react-native'; // core

const { width } = Dimensions.get('window');                           // स्क्रीन चौड़ाई
const BOX = 80;                                                       // box size
const MIN = 0;                                                        // बायाँ किनारा
const MAX = width - BOX;                                              // दायाँ किनारा

export default function BoundedDecay() {                              // component
  const x = useRef(new Animated.Value(MIN)).current;                  // शुरुआती x
  const decayRef = useRef(null);                                      // चल रही animation
  const lastX = useRef(MIN);                                          // नवीनतम x (listener से)

  useEffect(() => {                                                   // value निगरानी
    const id = x.addListener(({ value }) => {                         // हर बदलाव पर
      lastX.current = value;                                          // रिकॉर्ड करो (setState नहीं, re-render से बचो)
      if (value < MIN || value > MAX) {                               // सीमा पार हुई
        decayRef.current?.stop();                                     // decay रोको
        Animated.spring(x, {                                          // किनारे पर वापस
          toValue: value < MIN ? MIN : MAX,                           // नज़दीकी किनारा
          bounciness: 12,                                             // थोड़ा उछाल
          useNativeDriver: false,                                     // JS driver (listener भी JS में है)
        }).start();                                                   // चलाओ
      }                                                               // if खत्म
    });                                                               // listener खत्म
    return () => x.removeListener(id);                                // cleanup
  }, [x]);                                                            // dependency

  const responder = useRef(PanResponder.create({                      // gesture
    onStartShouldSetPanResponder: () => true,                         // पकड़ो
    onPanResponderGrant: () => {                                      // छूने पर
      decayRef.current?.stop();                                       // पुरानी decay रोको
      x.stopAnimation();                                              // value रोको
      x.setOffset(lastX.current);                                     // मौजूदा position को offset
      x.setValue(0);                                                  // delta 0
    },                                                                // grant खत्म
    onPanResponderMove: Animated.event([null, { dx: x }], { useNativeDriver: false }), // खींचना
    onPanResponderRelease: (_, g) => {                                // छोड़ना
      x.flattenOffset();                                              // offset मिलाओ
      decayRef.current = Animated.decay(x, { velocity: g.vx, deceleration: 0.995, useNativeDriver: false }); // decay बनाओ
      decayRef.current.start();                                       // शुरू
    },                                                                // release खत्म
  })).current;                                                        // स्थिर

  return (                                                            // UI
    <View style={s.track}>{/* ट्रैक */}
      <Animated.View {...responder.panHandlers} style={[s.box, { transform: [{ translateX: x }] }]} />{/* box */}
    </View>
  );                                                                  // return खत्म
}                                                                     // component खत्म

const s = StyleSheet.create({                                         // styles
  track: { flex: 1, justifyContent: 'center' },                       // layout
  box: { width: BOX, height: BOX, borderRadius: 14, backgroundColor: '#5f259f' }, // box
});                                                                   // खत्म
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Default deceleration | `0.998` (RN docs default) | `0.998` वही |
| Native driver | support है, पर PanResponder event से जोड़ना JS driver पर | वही |
| Native scroll momentum | OS के अपने constants (अलग feel) | iOS का अपना (ज़्यादा "फिसलने वाला") |
| Velocity units | px/ms | px/ms |
| Overscroll | Edge glow (native scroll में) | Rubber-band bounce |
| Custom decay का feel | दोनों पर एक जैसा, native scroll से थोड़ा अलग | वही |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: core API
import { Animated } from 'react-native';                   // core
Animated.decay(v, { velocity: 1.5, deceleration: 0.997, useNativeDriver: true }).start(); // चलाओ
// Reanimated: withDecay({ velocity, clamp: [0, 300] })  -> सीमा built-in!
```
CLI way:
```jsx
// CLI: वही core API
import { Animated } from 'react-native';                   // core
Animated.decay(v, { velocity: 1.5, deceleration: 0.997, useNativeDriver: true }).start(); // चलाओ
// Reanimated के लिए: npm i react-native-reanimated; babel plugin; pod install
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `toValue` देना (decay में target नहीं होता)।
✅ Correct: `velocity` और `deceleration`।

❌ Mistake 2: Grant पर चल रही decay न रोकना (उंगली रखने पर भी बॉक्स भागता रहे)।
✅ Correct: `stopAnimation()` + `extractOffset/setOffset`।

❌ Mistake 3: Release पर `flattenOffset()` भूलना।
✅ Correct: offset मिलाकर फिर decay चलाओ।

❌ Mistake 4: सीमा (boundary) की जाँच न करना, box स्क्रीन से बाहर चला जाए।
✅ Correct: listener में clamp/spring, या Reanimated `withDecay({ clamp })`।

---

## 🧠 Tricky Interview Question
```jsx
Animated.decay(v, { velocity: 0, useNativeDriver: true }).start();
```
यह क्या करेगा?

Answer: velocity 0 है, इसलिए value आगे बढ़ेगी ही नहीं; animation तुरंत finished हो जाएगी और value वहीं रहेगी जहाँ थी। Decay का अंतिम स्थान `शुरुआती value + velocity/(1 - deceleration)` के सन्निकट होता है, इसलिए velocity के बिना कोई movement नहीं।

---

## ⚫ Interview Questions + Answers
Q1: decay और spring में फर्क?
A1: Decay में target नहीं, सिर्फ़ velocity घटती है; spring एक तय target की ओर खींचती है।

Q2: `deceleration` का असर?
A2: 1 के जितना पास (0.999) उतना देर और दूर फिसलेगा; कम (0.9) जल्दी रुकेगा।

Q3: Velocity कहाँ से?
A3: PanResponder `gestureState.vx/vy` से (px/ms)।

Q4: Boundary कैसे?
A4: Listener में जाँचो और spring से लौटाओ, या Reanimated `withDecay({ clamp })`।

Q5: FlatList/ScrollView में decay लिखनी चाहिए?
A5: नहीं, native scroll में momentum built-in है; custom draggables के लिए decay।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Custom draggable/carousel/dial में flick
- Release के बाद inertia चाहिए
- Game जैसे UI

❌ Avoid when:
- Standard scroll lists (built-in)
- सटीक final position चाहिए (spring/timing)
- सरल fade/slide

---

## 📊 Visual Diagram
```
 position
    |                 ____ रुकी
    |            ___-'
    |        _-'
    |     _-'     <- घटती गति
    |  _-'
    | /  शुरुआत: तेज़ velocity
    +--------------------------- time
 हर frame: velocity *= deceleration
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| velocity | Speed + direction | गति और दिशा |
| deceleration | Rate of slowing | धीमे होने की दर |
| inertia/momentum | Keep moving after release | छोड़ने के बाद भी चलते रहना |
| flattenOffset | Merge offset into value | Offset को value में मिलाना |
| clamp | Limit range | सीमा बाँधना |

---

## ⚡ 3-Line Summary
English: Animated.decay slows a value from an initial velocity until it stops.
It has no target, so add boundary handling yourself or use Reanimated withDecay clamp.
Stop it on touch and flatten offsets on release.

Hindi: Animated.decay शुरुआती velocity से value को धीरे-धीरे रोकता है।
इसमें target नहीं होता, इसलिए सीमा खुद संभालो या Reanimated का withDecay clamp लो।
छूने पर इसे रोको और छोड़ने पर offset मिलाओ।

---

## ➡️ Next Topic
**127+ (Layout/Gesture animations) और 130. Reanimated v3**, जहाँ decay/spring/timing UI thread पर और ज़्यादा शक्ति के साथ चलते हैं।
