# 167. Inline Requires
# हिंदी में: Inline Requires (Modules को देर से load करना)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (check current docs — APIs change between SDKs)**, RN 0.76। Metro की `inlineRequires` transform option से चलता है। नए RN CLI template और Expo के `metro-config` में अलग-अलग default हो सकता है — अपने version की `metro.config.js` जाँचो।

---

## 🔵 Simple Definition (English)
**Inline requires** is a Metro transform that moves `require()` calls from the top of a file to the place where the imported value is **first used**. So a module's code is executed only when needed, not all at app start.

## 🔵 सरल परिभाषा (Hindi)
**Inline requires** Metro का transform है जो `require()` calls को file के ऊपर से हटाकर उस जगह ले जाता है जहाँ imported value **पहली बार इस्तेमाल** होती है। इसलिए module का code तभी चलता है जब ज़रूरत हो, app start पर सब नहीं।

---

## 🔴 Problem it Solves
```
import Chart from 'big-chart-lib';      // file के top पर
import PdfViewer from 'pdf-lib';

App खुलते ही ये दोनों libraries execute हो जाती हैं
(भले ही user Reports screen कभी न खोले)
→ startup धीमा, memory ज़्यादा
```

## 🔴 यह क्यों बना? (Hindi)
```
Top-level imports का मतलब: app खुलते ही हर library execute।
भले user वह screen कभी न खोले।
Inline requires: जिस पल value पहली बार इस्तेमाल हो, तभी module चलता है।
→ startup तेज़, memory कम।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → आप लिखते हो:   import Chart from 'big-chart-lib';
Step 2 → Babel/Metro ES import को require() में बदलता है
Step 3 → inlineRequires चालू: require को उपयोग की जगह पर ले जाता है
         (हर उपयोग पर वही cached module मिलता है — दोबारा execute नहीं)
Step 4 → Start पर big-chart-lib execute नहीं होता
Step 5 → Chart पहली बार render हुआ → तब require चला → module load
Step 6 → बाद में cache से (तेज़)
```

Transform का सरल उदाहरण (concept):
```js
// पहले (आपका code)
import Chart from 'big-chart-lib';
function Reports() { return <Chart />; }

// बाद (transform के बाद, concept)
function Reports() { const Chart = require('big-chart-lib').default; return <Chart />; } // पहली बार call पर ही require
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप top पर import लिखते हो
Step 2 → Metro उसे require() में बदलता है
Step 3 → inlineRequires चालू → require उपयोग की जगह चला जाता है
Step 4 → Start पर library execute नहीं होती
Step 5 → पहली बार इस्तेमाल पर load
Step 6 → बाद में cache से
```

---

## 🟡 Real World Example
**Paytm जैसे super-app** में Bus/Movies/Loans के भारी modules हैं। Inline requires से Home खुलते समय इनके libraries (maps, charts, SDKs) execute नहीं होतीं; जिस दिन user Movies टैब खोले, तभी load। **Swiggy** में Instamart के भारी map-आधारित code का भी यही फ़ायदा।

## 🟡 Real Example Hindi mein
Paytm जैसे super-app में Bus/Movies/Loans के भारी libraries हैं। Inline requires से Home खुलते समय वे execute नहीं होतीं; user Movies खोले तभी load होती हैं। Swiggy के map-आधारित भारी code पर भी यही लागू होता है।

---

## 💻 Code Example — Basic
```js
// metro.config.js (RN CLI) — inline requires चालू करना
const { getDefaultConfig, mergeConfig } = require('@react-native/metro-config'); // default config

const config = {
  transformer: {
    getTransformOptions: async () => ({                              // हर बार transform options
      transform: {
        experimentalImportSupport: false,                            // ES imports → require
        inlineRequires: true,                                        // ← मुख्य flag: require देर से
      },
    }),
  },
};

module.exports = mergeConfig(getDefaultConfig(__dirname), config);   // default + आपका config
```

## 💻 Code Example — Advanced
```jsx
// Advanced: जहाँ transform भरोसेमंद नहीं (side-effect libraries) वहाँ manual require
import React, { useState } from 'react';                             // हल्का: top पर ठीक
import { View, Text, Pressable } from 'react-native';                // core: top पर ठीक

export default function Home() {
  const [QRScanner, setQRScanner] = useState(null);                  // भारी scanner component
  const [error, setError] = useState(null);                          // load error

  const openScanner = () => {
    try {
      // manual inline require: scanner library पहली बार यहीं execute होगी
      const { QRScannerView } = require('./native/QRScannerView');   // भारी module
      setQRScanner(() => QRScannerView);                             // component state में रखो
    } catch (e) {
      setError(e.message);                                           // load fail हुआ तो दिखाओ
    }
  };

  return (
    <View style={{ padding: 24 }}>
      <Pressable onPress={openScanner}><Text>Scan QR</Text></Pressable>
      {error ? <Text>{error}</Text> : null}
      {QRScanner ? <QRScanner /> : null}
    </View>
  );
}

// ⚠️ सावधानी: जिन modules के import पर side-effect चाहिए (जैसे 'react-native-gesture-handler',
// polyfills, analytics init) उन्हें inline न करो — उन्हें index.js के top पर रखो।
// Metro इसके लिए `nonInlinedRequires` list देता है (नाम/उपलब्धता अपने metro version में जाँचो)।
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Metro transform | Same | Same |
| Startup benefit | बड़ा (धीमे CPU) | मध्यम |
| With Hermes | Bytecode के साथ और कम startup work | Same |
| Platform-specific imports | `Platform.select` के साथ सावधानी | Same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```js
// metro.config.js:
const { getDefaultConfig } = require('expo/metro-config');           // Expo का default config
const config = getDefaultConfig(__dirname);
// Expo की metro-config (SDK 50+ से) inline requires को production builds में डिफ़ॉल्ट रूप से
// सक्षम करता है — अपने SDK के docs में पुष्टि करो; manual: config.transformer.getTransformOptions = ...
module.exports = config;
```
CLI way:
```js
// ऊपर वाला @react-native/metro-config उदाहरण — inlineRequires: true
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Side-effect वाले modules inline कर देना (जैसे polyfills)।
✅ Correct: उन्हें entry file में top पर रखो / `nonInlinedRequires`।

❌ Mistake 2: Config बदलकर cache साफ़ न करना।
✅ Correct: `npx react-native start --reset-cache` / `npx expo start -c`।

❌ Mistake 3: मानना कि यह bundle size घटाता है।
✅ Correct: Size वही; सिर्फ execution देर से (startup घटता है)।

❌ Mistake 4: Class/`extends` में top-level उपयोग वाले imports की उम्मीद।
✅ Correct: जो module load पर ही चाहिए (जैसे `class A extends Base`) वहाँ फ़ायदा नहीं।

---

## 🧠 Tricky Interview Question
"Inline requires चालू करने के बाद एक library का global listener register ही नहीं हो रहा। क्यों?"

Answer: वह library import होते ही side-effect (listener लगाना) करती थी। Inline requires से उसका `require` तब तक टल गया जब तक value इस्तेमाल न हुई — और आपने value कभी इस्तेमाल ही नहीं की, इसलिए वह execute ही नहीं हुई। Fix: ऐसी library को entry (`index.js`) में side-effect import (`import 'lib/register'`) से रखो या `nonInlinedRequires` में डालो।

---

## ⚫ Interview Questions + Answers
Q1: Inline requires क्या है?
A1: Metro transform जो require() को उपयोग की जगह ले जाकर module execution टालता है।

Q2: फ़ायदा?
A2: कम startup काम और कम शुरुआती memory।

Q3: Hermes के साथ भी उपयोगी?
A3: हाँ — Hermes parse बचाता है; inline requires module *execution* टालते हैं। दोनों अलग-अलग लाभ।

Q4: जोखिम?
A4: Import-time side effects और initialization-order पर निर्भर code टूट सकता है।

Q5: चालू कैसे?
A5: `metro.config.js` में `transformer.getTransformOptions → transform.inlineRequires: true`।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- बड़ा app, कई भारी libraries
- Startup समय घटाना हो

❌ Avoid when:
- Modules में ज़रूरी import-time side effects
- Initialization order पर कड़ी निर्भरता

---

## 📊 Visual Diagram
```
 बिना inline:  start ─► require(A) require(B) require(C) ─► UI     (सब execute)
 inline:       start ─► UI ─► (A जब चाहिए) ─► require(A)           (B, C शायद कभी नहीं)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Inline require | require moved to first use | पहले उपयोग पर require |
| Metro | RN's JS bundler | RN का bundler |
| Side effect | Work done on import | Import पर होने वाला काम |
| Module cache | Stores executed modules | Executed modules का cache |
| nonInlinedRequires | Exclusion list | Inline से बाहर रखने की सूची |

---

## ⚡ 3-Line Summary
English: Inline requires delay running a module until its first use. This lowers startup time and early memory. Don't inline modules that need import-time side effects.
Hindi: Inline requires module को पहले उपयोग तक चलने से रोकते हैं। इससे startup समय और शुरुआती memory घटती है। जिन modules को import पर side-effect चाहिए उन्हें inline मत करो।

---

## ➡️ Next Topic
**168. Flipper Debugging** — performance ढूँढने का (legacy) debugging tool।
