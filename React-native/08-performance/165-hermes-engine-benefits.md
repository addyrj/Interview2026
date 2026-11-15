# 165. Hermes Engine Benefits
# हिंदी में: Hermes Engine के फ़ायदे
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (check current docs — APIs change between SDKs)**, RN 0.76। Hermes Android पर RN 0.70 से और iOS पर RN 0.70 से default (0.64+ में optional)। Expo में SDK 48+ से Hermes default है।

---

## 🔵 Simple Definition (English)
**Hermes** is a JavaScript engine made by Meta specially for React Native. It compiles your JS into **bytecode at build time**, so the app starts faster, uses less memory and has a smaller download size than the older JavaScriptCore (JSC).

## 🔵 सरल परिभाषा (Hindi)
**Hermes** Meta का बनाया JavaScript engine है जो खास React Native के लिए है। यह आपकी JS को **build के समय ही bytecode** में बदल देता है, इसलिए app जल्दी खुलता है, कम memory लेता है और पुराने JavaScriptCore (JSC) से छोटा download होता है।

---

## 🔴 Problem it Solves
```
पुराना तरीका (JSC):
  App खुलते ही 2-5 MB JS bundle को phone पर parse + compile करना पड़ता
  → startup धीमा (सस्ते Android पर 3-6 सेकंड)
  → JIT की वजह से ज़्यादा memory
  → Android पर JSC app size में बड़ा जुड़ता था

Hermes:
  Build पर bytecode (.hbc) → phone पर सीधे चलाओ → parse/compile skip
```

## 🔴 यह क्यों बना? (Hindi)
```
JSC में app खुलते ही बड़ा JS bundle phone पर parse + compile होता था
→ सस्ते Android पर startup धीमा, memory ज़्यादा।
Hermes ने यह काम build के समय कर दिया: bytecode सीधे चलता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Metro आपका JS bundle बनाता है
Step 2 → Build के दौरान hermesc (Hermes compiler) bundle को bytecode (.hbc) में बदलता है
Step 3 → APK/IPA में bytecode भेजा जाता है (text JS नहीं)
Step 4 → App खुलने पर Hermes bytecode को सीधे memory-map करता है
Step 5 → Parsing/compiling नहीं → TTI (time to interactive) कम
Step 6 → Garbage collector (Hades, concurrent) memory कम और pauses छोटे रखता है
Step 7 → Debug: Chrome DevTools / React Native DevTools, Hermes profiler
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Metro JS bundle बनाता है
Step 2 → Build में hermesc उसे bytecode (.hbc) में बदलता है
Step 3 → APK/IPA में bytecode जाता है
Step 4 → App खुलने पर bytecode सीधे चलता है (parse/compile नहीं)
Step 5 → Startup तेज़
Step 6 → GC (Hades) से memory कम और pauses छोटे
```

---

## 🟡 Real World Example
Meta ने Hermes को Facebook/Instagram जैसे बड़े apps के लिए बनाया। भारतीय संदर्भ में: **Swiggy/Zomato जैसे apps** का cold-start सस्ते Android phone पर Hermes से कुछ सेकंड तक घट सकता है (असली संख्या आपके app पर निर्भर — खुद measure करो)। Microsoft और Shopify ने भी Hermes अपनाने के बाद startup/memory सुधार बताया है।

## 🟡 Real Example Hindi mein
Hermes Meta ने बड़े apps के लिए बनाया। Swiggy/Zomato जैसे apps का cold-start सस्ते Android पर Hermes से घट सकता है (असली संख्या आपके app पर निर्भर, खुद measure करो)।

---

## 💻 Code Example — Basic
```jsx
// Basic: जाँचो कि app Hermes पर चल रहा है या नहीं
import React from 'react';                                           // React
import { View, Text } from 'react-native';                           // UI

// global.HermesInternal Hermes पर मौजूद होता है (JSC पर undefined)
const isHermes = () => !!global.HermesInternal;                      // true अगर Hermes

export default function EngineInfo() {
  return (
    <View style={{ padding: 24 }}>
      <Text>Engine: {isHermes() ? 'Hermes ✅' : 'JSC / other'}</Text>{/* engine का नाम */}
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: startup समय मापना + Hermes-specific सावधानियाँ
import React, { useEffect, useState } from 'react';
import { View, Text, Platform } from 'react-native';

// JS bundle जब load हुआ तब का समय (module-level, सबसे पहले चलता है)
const jsStart = Date.now();                                          // JS शुरू होने का समय

export default function App() {
  const [ttiMs, setTti] = useState(null);                            // first render के बाद का समय

  useEffect(() => {
    setTti(Date.now() - jsStart);                                    // JS शुरू → पहली screen mount
  }, []);

  // Hermes के बारे में सावधानी:
  // 1) Intl support Hermes में Android/iOS पर RN 0.70+ में अलग-अलग स्तर का रहा है;
  //    date/number formatting के लिए अपने target versions पर test करो।
  // 2) Proxy / Reflect: Hermes में अब supported है (पुराने versions में नहीं था) — version जाँचो।
  // 3) eval/new Function सीमित है → ऐसी libraries से बचो।
  const info = global.HermesInternal?.getRuntimeProperties?.();      // Hermes version/bytecode info (dev)
  return (
    <View style={{ padding: 24 }}>
      <Text>JS → first mount: {ttiMs ?? '…'} ms</Text>
      <Text>Platform: {Platform.OS}</Text>
      <Text>Hermes: {info?.['OSS Release Version'] ?? 'not Hermes'}</Text>
    </View>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Default Hermes since | RN 0.70 | RN 0.70 |
| Startup gain | बड़ा (सस्ते phones) | छोटा-मध्यम (JSC iOS में system के साथ था) |
| App size | JSC bundle जोड़ना बंद → बड़ी बचत | JSC system का था, पर Hermes framework जुड़ता है |
| Bytecode in build | Gradle task में | Xcode build phase में |
| Debugging | Hermes inspector / DevTools | वही |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// SDK 48+ में default Hermes। बदलना हो तो app.json में:
// { "expo": { "jsEngine": "hermes" } }   // या "jsc" (पुराना)
// (SDK 52 docs में jsEngine key जाँचो — कुछ वर्शन में per-platform भी है)
```
CLI way:
```jsx
// android/gradle.properties:  hermesEnabled=true
// ios/Podfile: :hermes_enabled => true   (RN 0.70+ में default true)
// फिर: cd ios && pod install
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: मानना कि Hermes हर JS feature support करता है।
✅ Correct: ज़रूरी APIs (Intl, Proxy आदि) अपने version पर test करो।

❌ Mistake 2: Dev mode में speed-up ढूँढना।
✅ Correct: Hermes bytecode का फ़ायदा release build में मिलता है।

❌ Mistake 3: पुराने ज़माने के Chrome-debugger पर निर्भर रहना।
✅ Correct: Hermes inspector / React Native DevTools इस्तेमाल करो।

❌ Mistake 4: Hermes + पुरानी library जो JSC-specific हो।
✅ Correct: Library की Hermes compatibility जाँचो।

---

## 🧠 Tricky Interview Question
"Hermes पर app का RAM उपयोग घटा, पर peak CPU वही। क्यों Hermes फिर भी 'तेज़' माना जाता है?"

Answer: Hermes का मुख्य लाभ steady-state raw JS throughput नहीं, बल्कि **startup (TTI) और memory** है। कोई JIT नहीं होता, इसलिए लंबे चलने वाले tight loops में JSC/V8 आगे हो सकते हैं। पर mobile apps में startup और memory ही उपयोगकर्ता अनुभव तय करते हैं।

---

## ⚫ Interview Questions + Answers
Q1: Hermes क्या है?
A1: React Native के लिए Meta का open-source JS engine, जो AOT bytecode compile करता है।

Q2: Hermes में JIT क्यों नहीं?
A2: JIT memory और startup बढ़ाता है और iOS में JIT की अनुमति सीमित है; Hermes bytecode interpreter + छोटा footprint चुनता है।

Q3: Hermes के मुख्य फ़ायदे?
A3: तेज़ startup (TTI), कम memory, छोटा app size (खासकर Android), बेहतर GC।

Q4: Hermes चालू है यह कैसे जाँचें?
A4: `global.HermesInternal` की जाँच।

Q5: Bytecode क्या है?
A5: JS का पहले से compiled रूप (.hbc) जिसे engine को parse करने की ज़रूरत नहीं।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- लगभग हमेशा (RN 0.70+ में default)
- सस्ते Android devices target हों

❌ Avoid when:
- कोई library सिर्फ JSC पर निर्भर हो (दुर्लभ)
- आपको कोई ऐसा JS feature चाहिए जो Hermes में नहीं है — तब docs देखकर निर्णय लो

---

## 📊 Visual Diagram
```
 JSC :  [bundle.js] ──► phone: parse ─► compile ─► run   (धीमा start)
 Hermes: [bundle.js] ─(build: hermesc)─► [bundle.hbc] ──► phone: run  (तेज़ start)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hermes | RN-focused JS engine | RN के लिए JS engine |
| JSC | JavaScriptCore (older engine) | पुराना JS engine |
| Bytecode | Precompiled JS | पहले से compiled JS |
| TTI | Time to interactive | उपयोग-योग्य होने का समय |
| AOT | Ahead-of-time compile | पहले से compile |
| GC (Hades) | Garbage collector | Memory साफ़ करने वाला |

---

## ⚡ 3-Line Summary
English: Hermes precompiles JS to bytecode at build time. This gives faster startup, lower memory and smaller apps. It is the default in modern React Native and Expo.
Hindi: Hermes build पर JS को bytecode में compile करता है। इससे तेज़ startup, कम memory और छोटा app मिलता है। आधुनिक React Native और Expo में यह default है।

---

## ➡️ Next Topic
**166. RAM Bundles** — बड़े bundle को टुकड़ों में load करना।
