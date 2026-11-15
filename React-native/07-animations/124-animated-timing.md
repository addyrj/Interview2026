# 124. Animated.timing
# हिंदी में: Animated.timing — समय आधारित Animation
# Platform: Android ✅ | iOS ✅ | Both ✅

---

**Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs).** `Animated.timing` और `Easing` core RN में हैं।

---

## 🔵 Simple Definition (English)
**Animated.timing** moves an Animated.Value from its current number to a target number in a fixed **duration**, following an **easing** curve (slow start, fast middle, slow end, etc.). It is the most common animation for fades, slides and progress bars.

## 🔵 सरल परिभाषा (Hindi)
**Animated.timing** एक Animated.Value को उसकी मौजूदा संख्या से target संख्या तक तय **duration** में ले जाता है, एक **easing** curve (धीमी शुरुआत, तेज़ बीच, धीमा अंत आदि) के अनुसार। Fade, slide और progress bar के लिए सबसे आम animation है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  Element एकदम से आ जाए तो अचानक लगता है.
  Fixed समय (जैसे 300ms) में exact movement चाहिए.

TIMING:
  ✅ Duration पर पूरा नियंत्रण
  ✅ Easing (linear, ease, bezier, bounce, elastic)
  ✅ delay, और callback (finished)
  ✅ sequence / parallel / stagger / loop में जोड़ना आसान
```

## 🔴 यह क्यों बना? (Hindi)
कई animations को तय समय और तय रफ़्तार वक्र चाहिए (जैसे modal 300ms में स्लाइड हो)। `timing` duration और easing देता है, ताकि समय पूर्वानुमेय हो, और callbacks से अगला काम जोड़ा जा सके।

---

## 🟢 How it Works — Step by Step
```
Step 1 → value = useRef(new Animated.Value(0)).current
Step 2 → Animated.timing(value, config) बनाओ
Step 3 → config: toValue, duration (ms), easing, delay, useNativeDriver
Step 4 → .start(callback) से चलाओ; callback में {finished} मिलता है
Step 5 → बीच में रोकना हो तो animation.stop() या value.stopAnimation()
Step 6 → कई animations: Animated.sequence / parallel / stagger / loop
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → value बनाओ
Step 2 → Animated.timing(value, config)
Step 3 → config में toValue, duration, easing, delay, useNativeDriver
Step 4 → .start(cb) से चलाओ (cb में finished)
Step 5 → रोकने के लिए stop()
Step 6 → कई animations को sequence/parallel/loop में जोड़ो
```

---

## 🟡 Real World Example
**Zomato/Swiggy** में bottom sheet 300ms में नीचे से ऊपर स्लाइड होती है। **Paytm** में splash logo fade-in। **Swiggy** में "Order placed" banner 2 सेकंड बाद अपने आप fade-out। **Zepto** का loading progress bar तय समय में भरता है।

## 🟡 Real Example Hindi mein
Swiggy की bottom sheet 300ms में ऊपर आती है, Paytm का splash logo धीरे से दिखता है, और "Order placed" banner 2 सेकंड बाद fade-out हो जाता है। ये सब `timing` से बनते हैं।

---

## 💻 Code Example — Basic
```jsx
// TimingBasic.jsx — box को slide + fade करना
import React, { useRef } from 'react';                                // hooks
import { Animated, Button, Easing, View } from 'react-native';        // core

export default function TimingBasic() {                               // component
  const x = useRef(new Animated.Value(0)).current;                    // x position value

  const slide = () => {                                               // button handler
    Animated.timing(x, {                                              // timing animation
      toValue: 200,                                                   // target = 200 px दायें
      duration: 500,                                                  // 500 ms
      easing: Easing.out(Easing.cubic),                               // तेज़ शुरू, धीमा अंत
      useNativeDriver: true,                                          // native thread
    }).start();                                                       // चलाओ
  };                                                                  // खत्म

  return (                                                            // UI
    <View style={{ flex: 1, justifyContent: 'center', padding: 24, gap: 20 }}>{/* container */}
      <Animated.View style={{ width: 80, height: 80, backgroundColor: '#e23744', transform: [{ translateX: x }] }} />{/* box */}
      <Button title="Slide" onPress={slide} />{/* button */}
    </View>
  );                                                                  // return खत्म
}                                                                     // component खत्म
```

## 💻 Code Example — Advanced
```jsx
// Toast.jsx — fade in -> wait -> fade out (sequence), cancelable, with callback
import React, { useCallback, useEffect, useRef } from 'react';        // hooks
import { Animated, Easing, Text, StyleSheet } from 'react-native';    // core

export default function Toast({ message, onHidden }) {                // props: message, onHidden callback
  const opacity = useRef(new Animated.Value(0)).current;              // 0 = छुपा
  const y = useRef(new Animated.Value(20)).current;                   // 20px नीचे से आएगा
  const anim = useRef(null);                                          // चल रही animation का handle

  const run = useCallback(() => {                                     // animation चलाओ
    anim.current = Animated.sequence([                                // एक के बाद एक
      Animated.parallel([                                             // दो चीज़ें साथ में
        Animated.timing(opacity, { toValue: 1, duration: 250, useNativeDriver: true }), // fade in
        Animated.timing(y, { toValue: 0, duration: 250, easing: Easing.out(Easing.quad), useNativeDriver: true }), // ऊपर आओ
      ]),                                                             // parallel खत्म
      Animated.delay(1800),                                           // 1.8 सेकंड रुको
      Animated.timing(opacity, { toValue: 0, duration: 300, useNativeDriver: true }), // fade out
    ]);                                                               // sequence बनी
    anim.current.start(({ finished }) => {                            // पूरा होने पर
      if (finished) onHidden?.();                                     // बीच में रोका नहीं गया तो parent को बताओ
    });                                                               // start खत्म
  }, [opacity, y, onHidden]);                                         // dependencies

  useEffect(() => {                                                   // message बदले तो
    opacity.setValue(0); y.setValue(20);                              // reset
    run();                                                            // चलाओ
    return () => anim.current?.stop();                                // unmount पर रोको (leak/warning से बचो)
  }, [message, opacity, y, run]);                                     // dependencies

  return (                                                            // UI
    <Animated.View style={[s.toast, { opacity, transform: [{ translateY: y }] }]}>{/* animated toast */}
      <Text style={s.text}>{message}</Text>{/* message */}
    </Animated.View>
  );                                                                  // return खत्म
}                                                                     // component खत्म

const s = StyleSheet.create({                                         // styles
  toast: { position: 'absolute', bottom: 60, alignSelf: 'center', backgroundColor: '#222', paddingHorizontal: 18, paddingVertical: 10, borderRadius: 20 }, // toast
  text: { color: '#fff' },                                            // text
});                                                                   // खत्म
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Native driver | transform/opacity | transform/opacity |
| Default feel | Material ease-out | iOS ease-in-out जैसा |
| Low-end devices | JS driver पर frame drops ज़्यादा | कम |
| Easing.bounce/elastic | वही | वही |
| Animating `elevation` | native driver से नहीं | N/A (shadow props) |
| Reduce motion | `duration: 0` रखकर सम्मान करो | वही |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: core API
import { Animated, Easing } from 'react-native';           // core
Animated.timing(v, { toValue: 1, duration: 300, easing: Easing.ease, useNativeDriver: true }).start(); // चलाओ
```
CLI way:
```jsx
// CLI: बिल्कुल वही; कोई अलग setup नहीं
import { Animated, Easing } from 'react-native';           // core
Animated.timing(v, { toValue: 1, duration: 300, easing: Easing.ease, useNativeDriver: true }).start(); // चलाओ
// Reanimated विकल्प: withTiming(1, { duration: 300 })  (अलग install)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `useNativeDriver` न देना (RN warning + JS thread)।
✅ Correct: हमेशा explicitly `true`/`false`।

❌ Mistake 2: Unmount के बाद animation चलते रहना।
✅ Correct: cleanup में `stop()`।

❌ Mistake 3: `Animated.sequence` में start() हर एक पर अलग-अलग बुलाना।
✅ Correct: composite पर सिर्फ एक `.start()`।

❌ Mistake 4: `duration` बहुत लंबा (>500ms सामान्य UI के लिए)।
✅ Correct: 200 से 400ms।

---

## 🧠 Tricky Interview Question
```jsx
Animated.loop(
  Animated.timing(v, { toValue: 1, duration: 1000, useNativeDriver: true })
).start();
```
Loop की दूसरी बार v कहाँ से शुरू होगा?

Answer: `loop` हर iteration से पहले animation को reset करता है (`resetBeforeIteration: true` default), इसलिए value फिर शुरुआती (0) से शुरू होती है और दोबारा 1 तक जाती है। अगर reset नहीं चाहिए (जैसे 0 -> 1 -> 0 ping-pong), तो sequence में दोनों दिशाएँ दो और `resetBeforeIteration: false` दो।

---

## ⚫ Interview Questions + Answers
Q1: `timing` और `spring` में फर्क?
A1: timing तय duration और easing curve से; spring physics (tension/friction) से, duration नहीं होती।

Q2: Easing क्या है?
A2: रफ़्तार बदलने का वक्र: linear, ease, `Easing.bezier(...)`, bounce, elastic।

Q3: Animation रोकना?
A3: animation object पर `stop()` या `value.stopAnimation(cb)`।

Q4: Callback में `finished`?
A4: true अगर पूरी हुई, false अगर बीच में रोकी गई।

Q5: दो animations साथ-साथ?
A5: `Animated.parallel([...])`; क्रम से: `Animated.sequence([...])`।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Fade/slide/progress जिन्हें तय समय चाहिए
- Toast, modal, banner
- Sequence/stagger बनाना

❌ Avoid when:
- Natural, bouncy feel चाहिए (spring)
- Gesture release के बाद momentum (decay)
- बहुत जटिल gesture-driven (Reanimated)

---

## 📊 Visual Diagram
```
 value
  1 |            ______  (ease-out)
    |         _-/
    |      _/
    |   _/
  0 |__/______________ time
    0        duration

 linear: सीधी रेखा   ease-out: तेज़ शुरू, धीमा अंत
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| duration | Time in ms | अवधि |
| easing | Speed curve | रफ़्तार का वक्र |
| toValue | Target number | लक्ष्य value |
| delay | Wait before start | शुरू से पहले इंतज़ार |
| sequence/parallel | Run one-by-one / together | क्रम से / साथ में |

---

## ⚡ 3-Line Summary
English: Animated.timing moves a value to a target over a fixed duration with easing.
Compose with sequence, parallel and loop, and always set useNativeDriver.
Stop animations on unmount.

Hindi: Animated.timing value को तय duration में easing के साथ target तक ले जाता है।
sequence, parallel, loop से जोड़ो और useNativeDriver हमेशा दो।
Unmount पर animation रोको।

---

## ➡️ Next Topic
**125. Animated.spring**, अब physics आधारित, bouncy और natural animation सीखेंगे।
