# 36. Slider Component
# हिंदी में: Slider Component (Range में value चुनना)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs)। **Core RN से `Slider` हटा दिया गया है**; अब `@react-native-community/slider` इस्तेमाल होता है।

---

## 🔵 Simple Definition (English)
A Slider lets the user pick a number from a range by dragging a thumb along a track. React Native's built-in Slider was removed, so we use the community package `@react-native-community/slider`.

## 🔵 सरल परिभाषा (Hindi)
Slider में user thumb को track पर खींचकर range में से कोई number चुनता है। RN का अपना Slider हटा दिया गया, इसलिए `@react-native-community/slider` package इस्तेमाल करते हैं।

---

## 🔴 Problem it Solves
```
❌ Price range, volume, brightness जैसी लगातार value TextInput से चुनना अजीब है
❌ सही min/max के अंदर रखने के लिए validation का झंझट
❌ Native look (Material / UISlider) एक ही component से चाहिए
```

## 🔴 यह क्यों बना? (Hindi)
```
Range वाली value खींचकर चुनना सबसे आसान है, इसलिए slider बना।
Core RN को हल्का रखने के लिए इसे अलग community package में डाल दिया गया।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Install:  npx expo install @react-native-community/slider
Step 2 → import Slider from '@react-native-community/slider'
Step 3 → state बनाओ: const [v, setV] = useState(0)
Step 4 → <Slider minimumValue={0} maximumValue={100} value={v} onValueChange={setV} />
Step 5 → drag करते समय onValueChange बार-बार चलता है
Step 6 → छोड़ने पर onSlidingComplete एक बार चलता है (API call यहाँ करो)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → npx expo install @react-native-community/slider
Step 2 → Slider import करो
Step 3 → state बनाओ
Step 4 → minimumValue, maximumValue, value और onValueChange दो
Step 5 → drag पर onValueChange बार-बार चलता है
Step 6 → छोड़ने पर onSlidingComplete एक बार चलता है; API call वहीं करो
```

---

## 🟡 Real World Example
**Zomato** के filters में "Cost for two" range, **Swiggy** में distance/price filter, और **Paytm** में loan amount चुनने का slider। **Spotify**-जैसे apps में volume/seek bar भी slider है।

## 🟡 Real Example Hindi mein
Paytm में personal loan का amount चुनने के लिए ₹10,000 से ₹5,00,000 तक का slider मिलता है, जिसे खींचकर रकम चुनते हैं।

---

## 💻 Code Example — Basic
```jsx
// Basic: Slider + value दिखाना
// Install: npx expo install @react-native-community/slider
import React, { useState } from 'react';                       // state
import { View, Text, StyleSheet } from 'react-native';         // UI
import Slider from '@react-native-community/slider';           // community slider

export default function PriceSlider() {
  const [price, setPrice] = useState(500);                     // वर्तमान value

  return (
    <View style={styles.box}>
      <Text style={styles.label}>Max price: ₹{price}</Text>{/* value दिखाओ */}
      <Slider
        style={styles.slider}                                  // चौड़ाई/ऊँचाई
        minimumValue={100}                                     // न्यूनतम
        maximumValue={2000}                                    // अधिकतम
        step={50}                                              // 50 के कदम
        value={price}                                          // वर्तमान value
        onValueChange={setPrice}                               // drag पर update
        minimumTrackTintColor="#e23744"                        // बाएँ हिस्से का रंग
        maximumTrackTintColor="#ccc"                           // दाएँ हिस्से का रंग
        thumbTintColor="#e23744"                               // thumb (Android + iOS)
      />
    </View>
  );
}

const styles = StyleSheet.create({
  box: { padding: 16 },                                        // padding
  label: { fontSize: 16, marginBottom: 8 },                    // label
  slider: { width: '100%', height: 40 },                       // बिना height के Android पर छोटा दिखता है
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: drag पर सिर्फ UI update; छोड़ने पर debounce की जगह onSlidingComplete से API call
// साथ में accessibility और disabled state
import React, { useState, useCallback } from 'react';          // hooks
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native'; // UI
import Slider from '@react-native-community/slider';           // slider

// fake API: असली में fetch/axios
const fetchRestaurants = (maxPrice) =>
  new Promise((res) => setTimeout(() => res(Math.floor(maxPrice / 40)), 500));

export default function FilterSlider() {
  const [price, setPrice] = useState(800);                     // live value
  const [count, setCount] = useState(null);                    // नतीजों की संख्या
  const [loading, setLoading] = useState(false);               // loading flag
  const [error, setError] = useState(null);                    // error

  const onDone = useCallback(async (v) => {                    // छोड़ने पर एक बार
    setLoading(true); setError(null);                          // शुरू
    try {
      setCount(await fetchRestaurants(v));                     // API call
    } catch (e) {
      setError('कुछ गलत हुआ, फिर try करो');                    // error संदेश
    } finally {
      setLoading(false);                                       // खत्म
    }
  }, []);

  return (
    <View style={styles.box}>
      <Text>Up to ₹{Math.round(price)}</Text>
      <Slider
        style={styles.slider}
        minimumValue={100} maximumValue={2000} step={50}
        value={price}
        onValueChange={setPrice}                               // हर movement
        onSlidingComplete={onDone}                             // सिर्फ अंत में
        disabled={loading}                                     // load के दौरान बंद
        accessibilityLabel="Maximum price filter"              // screen reader
        accessibilityValue={{ min: 100, max: 2000, now: price }} // बताओ कितना है
      />
      {loading ? <ActivityIndicator /> : count !== null && <Text>{count} restaurants</Text>}
      {error && <Text style={styles.err}>{error}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  box: { padding: 16 },
  slider: { width: '100%', height: 40 },
  err: { color: 'crimson' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Native view | Material SeekBar / Slider | `UISlider` |
| Thumb size | अपेक्षाकृत बड़ा, `thumbTintColor` से रंग | पतला thumb, `thumbTintColor` से रंग |
| `thumbImage`, `trackImage` | `thumbImage` ✅ | ✅ दोनों (ज़्यादा options) |
| Height न दो तो | बहुत छोटा/touch कठिन | आमतौर पर default दिखता है |
| `step` | ✅ | ✅ |
| `inverted` (RTL जैसी) | ✅ | ✅ (props पर version देखो) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Expo SDK के साथ compatible version अपने आप चुनता है
npx expo install @react-native-community/slider
```
CLI way:
```bash
# Bare RN: install + iOS pods
npm install @react-native-community/slider
cd ios && pod install && cd ..    # iOS native link
npx react-native run-android      # rebuild ज़रूरी
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `import { Slider } from 'react-native'`
✅ Correct: `import Slider from '@react-native-community/slider'` (core से हट चुका है)।

❌ Mistake 2: Slider को width/height न देना
✅ Correct: `style={{ width: '100%', height: 40 }}`।

❌ Mistake 3: `onValueChange` में हर बार API call
✅ Correct: API call `onSlidingComplete` में करो।

---

## 🧠 Tricky Interview Question
```jsx
<Slider minimumValue={0} maximumValue={10} step={3} />
```
**Q: कौन-कौन सी values चुनी जा सकती हैं?**

Answer: 0, 3, 6, 9 (step 3 के गुणज)। अधिकतम 10, step का गुणज नहीं है, इसलिए आख़िरी छोर पर 10 मिलेगा या नहीं, यह library/platform version पर निर्भर है (जाँच लो)। सुरक्षित तरीका: range को step का गुणज बनाओ, जैसे 0 से 9।

---

## ⚫ Interview Questions + Answers
Q1: Core `Slider` कहाँ गया?
A1: RN 0.60 के आसपास lean core पहल में हटाकर `@react-native-community/slider` में डाला गया।

Q2: `onValueChange` बनाम `onSlidingComplete`?
A2: पहला drag के दौरान बार-बार, दूसरा छोड़ने पर एक बार।

Q3: Range slider (दो thumbs) चाहिए तो?
A3: यह package single thumb देता है; दो thumbs के लिए दूसरी library (जैसे `@ptomasroos/react-native-multi-slider`) या custom Reanimated gesture।

Q4: Slider controlled है?
A4: हाँ, `value` + `onValueChange` से controlled रखा जाता है।

Q5: Expo Go में चलता है?
A5: हाँ, यह Expo Go में शामिल है (`npx expo install` से सही version)।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Price/distance/volume/brightness जैसी लगातार range
- Approximate value काफ़ी हो

❌ Avoid when:
- सटीक number चाहिए (TextInput/Stepper बेहतर)
- कुछ ही fixed विकल्प (chips/segmented control)

---

## 📊 Visual Diagram
```
min 100                                       max 2000
  |━━━━━━━━━━━━━●─────────────────────────────|
   filled(min track)  thumb  empty(max track)

drag → onValueChange(v)  (बार-बार)
leave → onSlidingComplete(v) (एक बार → API call)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Thumb | खींचने वाला गोला | thumb/हैंडल |
| Track | Slider की पट्टी | track |
| step | Value का कदम | कदम |
| onSlidingComplete | छोड़ने पर callback | छोड़ने पर चलने वाला |
| Controlled | state से चलने वाला | state-नियंत्रित |

---

## ⚡ 3-Line Summary
English:
1. Slider picks a value in a range; use `@react-native-community/slider`.
2. Control it with `value` and `onValueChange`.
3. Make API calls in `onSlidingComplete`.

Hindi:
1. Slider range से value चुनता है; `@react-native-community/slider` इस्तेमाल करो।
2. `value` और `onValueChange` से control करो।
3. API call `onSlidingComplete` में करो।

---

## ➡️ Next Topic
**37. ActivityIndicator Component** — loading दिखाने वाला spinner।
