# 166. RAM Bundles
# हिंदी में: RAM Bundles (JS code को टुकड़ों में load करना)
# Platform: Android ✅ | iOS ✅ | Both ✅ (legacy / JSC-era feature)

> Target: **Expo SDK 52 (check current docs — APIs change between SDKs)**, RN 0.76। **महत्वपूर्ण:** RAM bundles JSC के ज़माने का optimization है। **Hermes** bytecode को memory-map करके पहले ही lazy-load जैसा लाभ देता है, इसलिए नए projects में अलग से RAM bundle की ज़रूरत लगभग नहीं पड़ती। RN docs में यह section अब legacy माना जाता है — अपने version के docs जाँचो।

---

## 🔵 Simple Definition (English)
A **RAM bundle** (Random Access Module bundle) splits your JavaScript into many small modules stored in a format where each module can be loaded **on demand** instead of parsing the whole bundle at startup. Two formats existed: **Indexed RAM bundle** (iOS, one file with an index) and **File RAM bundle** (Android, many `js-modules/` files).

## 🔵 सरल परिभाषा (Hindi)
**RAM bundle** (Random Access Module bundle) आपकी JavaScript को कई छोटे modules में बाँट देता है, ऐसे format में कि हर module **ज़रूरत पड़ने पर** load हो — startup पर पूरा bundle parse न करना पड़े। दो formats थे: **Indexed RAM bundle** (iOS, index वाली एक file) और **File RAM bundle** (Android, `js-modules/` में कई files)।

---

## 🔴 Problem it Solves
```
बड़ा app: 5 MB JS bundle
JSC में startup पर पूरा parse करना पड़ता → 2-4 सेकंड

RAM bundle:
  सिर्फ पहली screen के modules load
  बाकी (Settings, Help, Reports) तब जब पहली बार import/require हों
  → startup तेज़, शुरू की memory कम
```

## 🔴 यह क्यों बना? (Hindi)
```
5 MB का JS bundle पूरा parse करना धीमा था (JSC)।
RAM bundle में सिर्फ ज़रूरी modules पहले load होते हैं, बाकी बाद में।
इससे startup तेज़ और शुरुआती memory कम।
(अब Hermes यह समस्या bytecode से काफ़ी हद तक हल कर देता है।)
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Metro हर module को अलग id देकर bundle बनाता है
Step 2 → Format चुनो: indexed (एक file + lookup table) या file (हर module अलग file)
Step 3 → App start पर सिर्फ "startup modules" (entry + उनकी dependencies) load
Step 4 → बाकी modules की जगह stub; पहली बार require() होने पर native से load
Step 5 → Inline requires के साथ मिलकर सबसे अच्छा काम (require देर से चले, 167)
Step 6 → Hermes पर: bytecode पहले से mmap → अलग RAM bundle की ज़रूरत नहीं
```

Metro config (RN CLI, JSC-era):
```js
// metro.config.js — RAM bundle के लिए inline requires ज़रूरी
module.exports = {
  transformer: {
    getTransformOptions: async () => ({
      transform: { experimentalImportSupport: false, inlineRequires: true }, // require देर से
    }),
  },
};
```
Build command (पुराने versions; flags आपके RN/Metro version में जाँचो):
```bash
# iOS indexed RAM bundle (JSC); Android file RAM bundle
npx react-native bundle --platform ios --dev false --entry-file index.js \
  --bundle-output ios/main.jsbundle --indexed-ram-bundle
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Metro हर module को id देता है
Step 2 → Format: indexed (एक file + table) या file (हर module अलग)
Step 3 → Start पर सिर्फ startup modules load
Step 4 → बाकी तब load जब पहली बार require हों
Step 5 → Inline requires के साथ सबसे बढ़िया
Step 6 → Hermes पर अलग से ज़रूरत नहीं
```

---

## 🟡 Real World Example
Facebook के पुराने बड़े app में सैकड़ों screens थीं; RAM bundles से startup पर सिर्फ News Feed का code load होता था। भारतीय संदर्भ में **Paytm जैसे super-app** (Wallet, Bus, Movies, Bills...) में हर mini-section का JS पहली बार खुलने पर ही चाहिए — यही lazy-loading का विचार है, जो आज Hermes + inline requires + lazy screens से किया जाता है।

## 🟡 Real Example Hindi mein
Paytm जैसे super-app में Wallet, Bus, Movies, Bills जैसे कई sections हैं। हर section का JS पहली बार खुलने पर ही चाहिए — यही RAM bundle का विचार है, जो आज Hermes + inline requires + lazy screens से होता है।

---

## 💻 Code Example — Basic
```jsx
// Basic: भारी screen को lazy import करना (RAM bundle जैसी सोच, modern तरीका)
import React, { useState } from 'react';                             // React + state
import { View, Text, Pressable } from 'react-native';                // UI

export default function Home() {
  const [Reports, setReports] = useState(null);                      // भारी component यहाँ आएगा

  const openReports = () => {
    // require() यहाँ चलने पर ही module load होगा (inline require)
    const Mod = require('./ReportsScreen').default;                  // देर से load
    setReports(() => Mod);                                           // function-state: component रखो
  };

  return (
    <View style={{ padding: 24 }}>
      <Pressable onPress={openReports}><Text>Open Reports</Text></Pressable>
      {Reports ? <Reports /> : null}
    </View>
  );
}
```
```jsx
// ReportsScreen.jsx — भारी module (charts आदि) जो शुरू में load नहीं होना चाहिए
import React from 'react';                                           // React
import { Text } from 'react-native';                                 // UI
export default function ReportsScreen() {                            // component
  return <Text>Heavy reports screen</Text>;                          // नमूना content
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: React.lazy + Suspense से screen-level lazy loading और error handling
import React, { Suspense, lazy, useState } from 'react';
import { ActivityIndicator, View, Text, Pressable } from 'react-native';

// lazy(): पहली बार render होने पर ही module load होता है (RN में Metro इसे सपोर्ट करता है; 
// bundle फिर भी एक ही रहता है — बचत parse/execution में होती है, download में नहीं)
const Settings = lazy(() => import('./SettingsScreen'));             // dynamic import

class Boundary extends React.Component {                             // load fail पर fallback
  state = { err: null };                                             // error state
  static getDerivedStateFromError(err) { return { err }; }           // error पकड़ो
  render() {
    if (this.state.err) return <Text>Couldn't load screen</Text>;    // fallback UI
    return this.props.children;                                      // सब ठीक
  }
}

export default function Root() {
  const [show, setShow] = useState(false);                           // screen दिखाएँ?
  return (
    <View style={{ flex: 1, padding: 24 }}>
      <Pressable onPress={() => setShow(true)}><Text>Open Settings</Text></Pressable>
      {show && (
        <Boundary>
          <Suspense fallback={<ActivityIndicator />}>                {/* load होते समय spinner */}
            <Settings />
          </Suspense>
        </Boundary>
      )}
    </View>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Legacy format | File RAM bundle (`js-modules/` folder) | Indexed RAM bundle (एक file) |
| Loaded by | Native से हर module file पढ़ना | Index से offset पर पढ़ना |
| Hermes के साथ | ज़रूरत नहीं (bytecode पहले से mmap) | ज़रूरत नहीं |
| Status | Legacy | Legacy |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo में RAM bundle manually सेट नहीं करते; Hermes default है।
// Lazy loading के लिए React.lazy / expo-router के lazy routes इस्तेमाल करो।
const Settings = React.lazy(() => import('./SettingsScreen'));
```
CLI way:
```jsx
// Legacy: metro.config.js में inlineRequires + bundle command में --indexed-ram-bundle (JSC)
// आज: Hermes चालू रखो; यही काफ़ी है
const Settings = React.lazy(() => import('./SettingsScreen'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Hermes पर भी RAM bundle को ज़रूरी मानना।
✅ Correct: Hermes bytecode पहले ही तेज़ है; पहले measure करो।

❌ Mistake 2: Inline requires बंद रखकर RAM bundle बनाना।
✅ Correct: दोनों साथ; वरना सारे modules start पर ही require हो जाते हैं।

❌ Mistake 3: Top-level में सारे imports (`import X from ...`) और मानना कि lazy हो गया।
✅ Correct: Lazy के लिए `require()` या `import()` function के अंदर।

❌ Mistake 4: मानना कि `React.lazy` download size घटाता है।
✅ Correct: RN में bundle एक ही फ़ाइल है; बचत startup execution में होती है।

---

## 🧠 Tricky Interview Question
"आपने `React.lazy` से 10 screens lazy कीं, पर APK का size नहीं बदला। क्यों?"

Answer: React Native में Metro पूरा JS एक ही bundle में डालता है (web की तरह code-splitting chunks नहीं)। `lazy`/inline-require सिर्फ यह टालते हैं कि module कब **execute** हो, इसलिए startup तेज़ होता है, पर bundle/APK size वही रहता है। Size घटाने के लिए unused libraries हटाओ, Hermes, Proguard/R8 और asset compression।

---

## ⚫ Interview Questions + Answers
Q1: RAM bundle क्या है?
A1: JS modules का ऐसा packaging जिसमें modules on-demand load होते हैं।

Q2: Indexed vs File RAM bundle?
A2: Indexed = एक file + index (iOS); File = हर module अलग file (Android)।

Q3: Hermes के साथ RAM bundle की ज़रूरत क्यों नहीं?
A3: Hermes bytecode mmap होता है, पूरा parse नहीं करना पड़ता, इसलिए लाभ पहले ही मिल जाता है।

Q4: RAM bundle किसके साथ सबसे अच्छा?
A4: Inline requires (167) के साथ।

Q5: Lazy loading RN में code-splitting है?
A5: नहीं; execution lazy है, bundle एक ही रहता है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- पुराना JSC-आधारित बड़ा app हो
- Startup पर बहुत भारी module graph हो और Hermes उपलब्ध नहीं

❌ Avoid when:
- Hermes चालू है (आज का default)
- नया project; पहले profile करो

---

## 📊 Visual Diagram
```
 Normal bundle:   [A][B][C][D][E][F]  ─ सब parse+run at start
 RAM bundle:      [A][B] load now ;  [C][D][E][F] stubs
                              require(C) → तब load ✅
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RAM bundle | Random-access module bundle | On-demand modules वाला bundle |
| Indexed bundle | One file with index | Index वाली एक file |
| Module | One JS file/unit | एक JS इकाई |
| Lazy loading | Load when needed | ज़रूरत पर load |
| Stub | Placeholder for unloaded module | अभी न load हुए module की जगह |

---

## ⚡ 3-Line Summary
English: RAM bundles load JS modules on demand to speed up startup. They are a legacy JSC-era optimization. With Hermes you usually don't need them; use inline requires and lazy screens instead.
Hindi: RAM bundles JS modules को ज़रूरत पर load करके startup तेज़ करते हैं। यह JSC के ज़माने का legacy optimization है। Hermes के साथ आम तौर पर ज़रूरत नहीं; inline requires और lazy screens इस्तेमाल करो।

---

## ➡️ Next Topic
**167. Inline Requires** — modules को पहली बार इस्तेमाल होने तक टालना।
