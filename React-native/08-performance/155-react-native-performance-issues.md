# 155. React Native Performance Issues
# हिंदी में: React Native की Performance समस्याएँ और उनके हल
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (check current docs — APIs change between SDKs)**, React Native 0.76 (New Architecture default, Hermes default).

---

## 🔵 Simple Definition (English)
A **performance issue** is anything that makes the app drop below 60 FPS (16.6 ms per frame), start slowly, use too much memory, or feel laggy on touch. In React Native most issues come from too many re-renders, heavy JS work on the JS thread, big lists, and large images.

## 🔵 सरल परिभाषा (Hindi)
**Performance issue** वह है जिससे app 60 FPS (हर frame 16.6 ms) से नीचे गिरे, देर से खुले, ज़्यादा memory खाए या touch पर अटके। React Native में ज़्यादातर समस्याएँ ज़्यादा re-renders, JS thread पर भारी काम, बड़ी lists और बड़ी images से आती हैं।

---

## 🔴 Problem it Solves
```
Users on Rs 8,000 Android phones (2GB RAM) are the majority in India.
Slow app → uninstall within seconds.

Typical symptoms:
  ❌ Scroll lag in FlatList (Zomato restaurant list)
  ❌ Button press delay (JS thread busy)
  ❌ App start takes 6+ seconds
  ❌ Memory crash (OOM) on image-heavy screens
  ❌ Animation stutter (JS-driven animation)
```

## 🔴 यह क्यों बना? (Hindi)
```
भारत में ज़्यादातर users सस्ते Android phones (2GB RAM) पर हैं।
Slow app = कुछ सेकंड में uninstall।

लक्षण:
  ❌ List scroll में अटकना
  ❌ Button दबाने पर देर से response
  ❌ App शुरू होने में 6+ सेकंड
  ❌ Image-heavy screen पर crash (Out of Memory)
```

---

## 🟢 How it Works — Step by Step
```
React Native has (mainly) 2 threads that matter:
  JS thread  → runs your React code, state, logic
  UI thread  → draws the pixels (native)

Step 1 → Measure FIRST (React DevTools Profiler, Perf Monitor, Hermes profiler)
Step 2 → Find which thread is slow:
          JS FPS low  → too much JS / re-render
          UI FPS low  → heavy native views, shadows, big images
Step 3 → Fix biggest cause: re-renders, list config, images, startup
Step 4 → Re-measure on a LOW-END release build (never judge by dev mode)
```

Quick checklist:
```
Re-renders   → React.memo, useCallback, useMemo, split components
Lists        → FlatList + keyExtractor + getItemLayout + windowSize
Images       → right size, WebP, caching (expo-image)
Startup      → Hermes, inline requires, lazy screens
Animations   → useNativeDriver / Reanimated worklets
Logs         → remove console.log in production
```

## 🟢 कैसे काम करता है? (Hindi)
```
दो मुख्य threads:
  JS thread → आपका React code, state, logic
  UI thread → screen पर pixels draw करता है

Step 1 → पहले MEASURE करो (Profiler, Perf Monitor)
Step 2 → पता करो कौन सा thread slow है
Step 3 → सबसे बड़ा कारण ठीक करो
Step 4 → सस्ते Android पर RELEASE build में दोबारा मापो
```

---

## 🟡 Real World Example
**Swiggy/Zomato** home screens show hundreds of restaurant cards with images. Without optimization, each state change (cart count) re-renders every card and loads full-size images → lag. They use list virtualization, small CDN-resized images, memoized cards, and skeleton loaders to keep scroll smooth even on budget phones.

## 🟡 Real Example Hindi mein
**Swiggy/Zomato** के home screen पर सैकड़ों restaurant cards और images होते हैं। Optimization के बिना cart count बदलते ही हर card re-render होता और बड़ी images load होतीं → lag। इसलिए वे list virtualization, CDN से छोटी images, memoized cards और skeleton loaders इस्तेमाल करते हैं।

---

## 💻 Code Example — Basic
```jsx
// Basic: एक slow screen (BAD) और उसका fix (GOOD)
import React, { useState, useCallback, memo } from 'react';        // React + hooks
import { View, Text, Pressable, FlatList } from 'react-native';    // UI components

// ---- GOOD: memo से card सिर्फ तब re-render होगा जब props बदलें ----
const Row = memo(function Row({ item, onPress }) {                 // memo wrapper
  return (
    <Pressable onPress={() => onPress(item.id)}>                   {/* tap पर id भेजो */}
      <Text>{item.name}</Text>                                     {/* नाम दिखाओ */}
    </Pressable>
  );
});

export default function Screen() {
  const [count, setCount] = useState(0);                           // cart count state
  const data = Array.from({ length: 500 }, (_, i) => ({ id: String(i), name: `Item ${i}` })); // demo data

  const onPress = useCallback(() => setCount(c => c + 1), []);     // stable function reference

  return (
    <View style={{ flex: 1 }}>
      <Text>Cart: {count}</Text>
      <FlatList
        data={data}                                                // list data
        keyExtractor={i => i.id}                                   // stable key
        renderItem={({ item }) => <Row item={item} onPress={onPress} />} // memoized row
      />
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: JS thread को खाली रखना — भारी काम को टालना और slow render ढूँढना
import React, { Profiler, useEffect, useState } from 'react';      // Profiler = render time मापता है
import { InteractionManager, Platform, View, Text } from 'react-native'; // animation के बाद काम चलाने के लिए

// onRender हर commit पर चलता है: id, phase, actualDuration (ms)
function onRender(id, phase, actualDuration) {
  if (__DEV__ && actualDuration > 16) {                            // 16ms से ज़्यादा = frame drop
    console.warn(`[perf] ${id} ${phase} took ${actualDuration.toFixed(1)}ms`); // warning
  }
}

export default function Feed() {
  const [ready, setReady] = useState(false);                       // भारी UI तैयार है या नहीं

  useEffect(() => {
    // Navigation animation खत्म होने के बाद भारी काम चलाओ
    const task = InteractionManager.runAfterInteractions(() => {   // animation के बाद callback
      setReady(true);                                              // अब भारी content render करो
    });
    return () => task.cancel();                                    // unmount पर रद्द करो
  }, []);

  return (
    <Profiler id="Feed" onRender={onRender}>                       {/* इस subtree का time मापो */}
      <View style={{ flex: 1 }}>
        {ready ? <HeavyList /> : <Text>Loading…</Text>}            {/* पहले हल्का placeholder */}
        {Platform.OS === 'android' && <Text>Tip: test on low-end</Text>} {/* platform note */}
      </View>
    </Profiler>
  );
}

function HeavyList() {
  return <Text>Imagine 1000 rows here</Text>;                      // असली list यहाँ आएगी
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Typical device | Wide range, many low-end (2-3GB RAM) | Fewer, powerful devices |
| Common bottleneck | Memory, JS thread, overdraw | Shadows, large images |
| Hermes | Default (RN 0.70+) | Default (RN 0.70+) |
| Shadows | `elevation` (cheap) | `shadow*` props (costly if many) |
| Image decoding | Bitmap memory heavy | Generally efficient |
| Profiling tools | Android Studio Profiler, Perf Monitor | Xcode Instruments |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Dev menu → "Show Performance Monitor"; React DevTools: npx react-devtools
// Release-like test: npx expo start --no-dev --minify
// Better images: npx expo install expo-image
```
CLI way:
```jsx
// Dev menu (shake / Cmd+M) → "Perf Monitor"
// Release build: npx react-native run-android --mode release
// iOS: Xcode → Product → Scheme → Run → Build Configuration = Release
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Dev mode में performance judge करना।
✅ Correct: Release build, real low-end device पर मापो (dev mode बहुत slow होता है)।

❌ Mistake 2: हर चीज़ पर `useMemo`/`useCallback` लगाना।
✅ Correct: पहले profile करो; सिर्फ वहाँ लगाओ जहाँ memoized child या महँगा calculation हो।

❌ Mistake 3: `ScrollView` में 1000 items map करना।
✅ Correct: `FlatList`/`FlashList` इस्तेमाल करो (virtualization)।

❌ Mistake 4: Production में `console.log` छोड़ना।
✅ Correct: Logs हटाओ (babel plugin `transform-remove-console`)।

---

## 🧠 Tricky Interview Question
"Button दबाने पर 1 सेकंड बाद response आता है, पर FPS monitor में UI thread 60 दिखा रहा है। क्यों?"

Answer: Touch events JS thread पर handle होते हैं। UI thread खाली है पर JS thread किसी भारी loop/re-render में फँसा है, इसलिए JS FPS गिरा हुआ है। Fix: काम को छोटा करो, `InteractionManager`, memoization, या worker/native module में shift करो। (Reanimated worklets animation को UI thread पर चलाते हैं, पर onPress logic फिर भी JS में है।)

---

## ⚫ Interview Questions + Answers
Q1: React Native में 60 FPS का मतलब?
A1: हर frame 16.6 ms में बनना चाहिए, JS और UI दोनों threads के लिए।

Q2: JS FPS और UI FPS का अंतर?
A2: JS FPS = React code/state की गति; UI FPS = native drawing की गति। दोनों अलग मापे जाते हैं।

Q3: सबसे आम कारण क्या हैं?
A3: अनावश्यक re-renders, बड़ी lists बिना virtualization, बड़ी images, भारी JS computation, production में logs।

Q4: Performance कैसे मापते हैं?
A4: React DevTools Profiler, Perf Monitor, Hermes sampling profiler, Android Studio Profiler, Xcode Instruments।

Q5: New Architecture का क्या फ़ायदा?
A5: Bridge की जगह JSI — synchronous native calls, कम serialization; Fabric से बेहतर rendering। (Expo SDK 52 में default; पुराने SDK में flag से।)

---

## 🔷 When to Use + When Not to Use
✅ Optimize when:
- Profiler में frame drops या slow screens दिखें
- Low-end devices पर complaints हों
- Lists 100+ items की हों

❌ Avoid when:
- Premature optimization — measurement के बिना
- Code को unreadable बना दे और gain नगण्य हो

---

## 📊 Visual Diagram
```
 Touch ─► JS thread (React, state, logic) ─► Bridge/JSI ─► UI thread ─► Pixels
              ▲ भारी काम यहाँ = lag               ▲ भारी views/images = jank
 Goal: दोनों threads हर 16.6ms में खाली
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| FPS | Frames per second | प्रति सेकंड frames |
| JS thread | Runs React code | JavaScript चलाने वाला thread |
| UI thread | Draws native views | Screen बनाने वाला thread |
| Re-render | Component runs again | Component का दोबारा चलना |
| Profiler | Measures render time | Render समय मापने का tool |
| Jank | Visible stutter | अटकना |

---

## ⚡ 3-Line Summary
English: Performance work starts with measuring on a release build. Most lag is re-renders, big lists, big images, or a blocked JS thread. Fix the biggest cause first and re-measure.
Hindi: Performance का काम release build पर मापने से शुरू होता है। ज़्यादातर lag re-renders, बड़ी lists, बड़ी images या blocked JS thread से आता है। सबसे बड़ा कारण ठीक करो और दोबारा मापो।

---

## ➡️ Next Topic
**158. useCallback + useMemo in RN** — re-renders रोकने के सबसे आम tools (156-157 पहले से हैं)।
