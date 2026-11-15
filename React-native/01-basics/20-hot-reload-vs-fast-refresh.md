# 20. Hot Reload vs Fast Refresh
# हिंदी में: Hot Reload बनाम Fast Refresh
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs)। नए RN में पुराना "Hot Reloading" हट चुका है; उसकी जगह **Fast Refresh** है।

---

## 🔵 Simple Definition (English)
Fast Refresh updates your running app instantly when you save a file, keeping component state where possible. Live/Full Reload restarts the whole JS bundle and loses state. The old "Hot Reloading" feature was replaced by Fast Refresh (RN 0.61+).

## 🔵 सरल परिभाषा (Hindi)
Fast Refresh file save करते ही चल रहे app को तुरंत update करता है और जहाँ संभव हो state बचा कर रखता है। Full Reload पूरा JS bundle फिर से चलाता है और state खो जाती है। पुराना "Hot Reloading" RN 0.61 से Fast Refresh में बदल गया।

---

## 🔴 Problem it Solves
```
❌ हर छोटे बदलाव पर app rebuild/restart (मिनटों का इंतज़ार)
❌ Form भरा हुआ था, restart से सब मिट गया
❌ पुराना Hot Reload कभी-कभी टूटा हुआ/अजीब state दिखाता था
```

## 🔴 यह क्यों बना? (Hindi)
```
Developer की speed के लिए। UI बदलो → 1 सेकंड में फोन पर दिखे, और
login/cart जैसी state बनी रहे, ताकि बार-बार वही steps न दोहराने पड़ें।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → आप file save करते हो
Step 2 → Metro बदली हुई module को पहचानता है और सिर्फ वही module भेजता है
Step 3 → Fast Refresh जाँचता है: file में सिर्फ React components export हैं?
Step 4a → हाँ → सिर्फ वे components re-render, hooks state (useState) बची रहती है
Step 4b → नहीं (non-component export भी है) → उस file के importers भी re-run
Step 4c → Syntax error → error overlay, ठीक करो तो अपने आप recover
Step 5 → ज़रूरत पड़े तो Full Reload (state खो जाती है)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → file save करो
Step 2 → Metro सिर्फ बदली हुई module भेजता है
Step 3 → देखता है कि file सिर्फ components export करती है या नहीं
Step 4 → हाँ तो state बची रहती है और component फिर से render होता है
Step 5 → नहीं तो ज़्यादा modules दोबारा चलते हैं; ज़रूरत पर Full Reload
Step 6 → Syntax error में error screen; ठीक करते ही अपने आप ठीक
```

---

## 🟡 Real World Example
**Swiggy** की team cart का UI बदलते समय cart में 3 items डालकर रखती है। Fast Refresh से styling बदलने पर वे 3 items बने रहते हैं, पूरा flow दोबारा नहीं चलाना पड़ता। **Paytm** में OTP screen पर बैठे-बैठे button का color बदला जा सकता है।

## 🟡 Real Example Hindi mein
Zomato के checkout में कई steps के बाद पहुँचते हैं। Fast Refresh के बिना हर बदलाव पर शुरू से जाना पड़ता, इसलिए यह time बचाता है।

---

## 💻 Code Example — Basic
```jsx
// Basic: Fast Refresh से state बचने की demo
// Counter बढ़ाओ, फिर नीचे का text/colour बदलकर save करो — count बना रहेगा
import React, { useState } from 'react';                    // useState hook
import { View, Text, Button, StyleSheet } from 'react-native'; // UI

export default function Counter() {
  const [count, setCount] = useState(0);                    // state — save पर बची रहेगी
  return (
    <View style={styles.box}>
      <Text style={styles.t}>Count: {count}</Text>{/* इस text को बदलकर save करो */}
      <Button title="+1" onPress={() => setCount(count + 1)} />{/* count बढ़ाओ */}
    </View>
  );
}

const styles = StyleSheet.create({
  box: { flex: 1, justifyContent: 'center', alignItems: 'center' }, // बीच में
  t: { fontSize: 24, color: 'tomato' },                     // रंग बदलकर देखो
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: Fast Refresh के नियम — state कब reset होती है
import React, { useState, useEffect } from 'react';         // hooks
import { View, Text, StyleSheet } from 'react-native';      // UI

// 1) // @refresh reset  comment (नीचे) इस file को हर edit पर पूरी तरह reset करता है
// 2) Component और non-component (जैसे constant) एक file में मिलाओगे तो
//    उस file के edit पर importers भी re-run हो सकते हैं
export const API_URL = 'https://example.com/api';           // non-component export

export default function Timer() {
  const [secs, setSecs] = useState(0);                      // state

  useEffect(() => {
    const id = setInterval(() => setSecs((s) => s + 1), 1000); // हर सेकंड +1
    return () => clearInterval(id);                         // cleanup — Fast Refresh में effect दोबारा चलता है
  }, []);

  return (
    <View style={styles.box}>
      <Text>Seconds: {secs}</Text>
    </View>
  );
}

// Class components का state हर edit पर reset होता है (Fast Refresh class state नहीं बचाता)
const styles = StyleSheet.create({ box: { flex: 1, justifyContent: 'center', alignItems: 'center' } });
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Dev menu खोलना (device) | फोन हिलाओ / `adb shell input keyevent 82` | फोन हिलाओ |
| Emulator/Simulator shortcut | `Ctrl+M` (Win/Linux) / `Cmd+M` (Mac) | `Cmd+D` |
| Full Reload shortcut | `R` दो बार | `Cmd+R` |
| Fast Refresh behaviour | एक जैसा (JS layer) | एक जैसा |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo start      # Fast Refresh default ON
# terminal में  r  दबाओ → Full Reload; Dev menu में "Fast Refresh" toggle
```
CLI way:
```bash
npx react-native start       # Metro
# Dev menu → "Enable Fast Refresh" toggle; Full reload: R R (Android) / Cmd+R (iOS)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: "Hot Reload" और "Fast Refresh" को अलग मानना
✅ Correct: नए RN में पुराना Hot Reloading हटाया गया; आज जो दिखता है वह Fast Refresh है।

❌ Mistake 2: Native code (Java/Kotlin/Swift) या `app.json` बदलकर Fast Refresh की उम्मीद
✅ Correct: Native बदलाव के लिए rebuild (`npx expo run:android/ios`) चाहिए।

❌ Mistake 3: Class component की state बचने की उम्मीद
✅ Correct: Function components + hooks इस्तेमाल करो।

---

## 🧠 Tricky Interview Question
```jsx
export const LIMIT = 5;
export default function Cart() { const [n, setN] = useState(0); /* ... */ }
```
**Q: इस file को edit करने पर state क्यों reset हो जाती है?**

Answer: File में component के साथ non-component export (`LIMIT`) है। Fast Refresh तब शर्त पूरी नहीं मानता और importers सहित module फिर से चलाता है, जिससे state reset हो सकती है। हल: constants अलग file में रखो।

---

## ⚫ Interview Questions + Answers
Q1: Fast Refresh और Live Reload में फ़र्क?
A1: Fast Refresh सिर्फ बदला हुआ हिस्सा बदलता है और state बचाता है; Live/Full Reload पूरा app restart करता है।

Q2: Fast Refresh कब काम नहीं करता?
A2: Native code बदलने पर, नई native library जोड़ने पर, या कभी-कभी module-level side effects होने पर।

Q3: `// @refresh reset` क्या करता है?
A3: उस file के components को हर edit पर remount करता है (state reset)।

Q4: Fast Refresh में useEffect क्यों दोबारा चलता है?
A4: Edit के बाद effects फिर से चलाए जाते हैं, इसलिए cleanup सही लिखना ज़रूरी है।

Q5: Fast Refresh बंद कैसे करें?
A5: Dev menu से "Fast Refresh" toggle off।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- UI/styling/logic के छोटे बदलाव
- गहरे navigation के अंदर की screen पर काम

❌ Avoid / Full reload चाहिए जब:
- Native module या config बदला
- Strange state bug लगे (Full Reload से साफ़ करो)

---

## 📊 Visual Diagram
```
 Save file
    │
    ▼
 Metro (HMR) ── बदला module ──► Fast Refresh runtime
                                   │
              सिर्फ components?  ──┤── हाँ ──► re-render, state बची ✅
                                   └── नहीं ─► importers re-run / Full Reload ❌ (state खोई)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fast Refresh | State रखकर instant update | तेज़ refresh |
| Full Reload | पूरा bundle फिर से | पूरा reload |
| HMR | Hot Module Replacement (Metro) | module बदलने की तकनीक |
| Remount | Component नए सिरे से बनना | दोबारा बनना |
| Dev Menu | Debug options menu | developer menu |

---

## ⚡ 3-Line Summary
English:
1. Fast Refresh replaced the old Hot Reload (RN 0.61+) and keeps hook state.
2. It re-runs only changed modules; native changes need a rebuild.
3. Keep components in their own files; use `// @refresh reset` if needed.

Hindi:
1. Fast Refresh ने पुराने Hot Reload की जगह ली (RN 0.61+) और hooks state बचाता है।
2. सिर्फ बदली modules चलती हैं; native बदलाव पर rebuild चाहिए।
3. Components अलग file में रखो; ज़रूरत पर `// @refresh reset` लगाओ।

---

## ➡️ Next Topic
**21. View Component** — हर layout का सबसे बुनियादी building block।
