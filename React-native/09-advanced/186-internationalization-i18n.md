# 186. Internationalization (i18n) in RN
# हिंदी में: React Native में बहु-भाषा (i18n) Support
# Platform: Both ✅ (Android ✅ | iOS ✅)

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs). Libraries: `i18next` + `react-i18next` + `expo-localization` (Expo) या `react-native-localize` (CLI). Version-dependent: `i18next` v23+ में `compatibilityJSON: 'v4'` default है।

---

## 🔵 Simple Definition (English)
**i18n** (internationalization) means building the app so text, dates, numbers and currency can change per language and region without changing code. **l10n** is the actual translation work. Typical stack: `i18next` + `react-i18next` for strings, `expo-localization` to detect device language.

## 🔵 सरल परिभाषा (Hindi)
**i18n** यानी app ऐसे बनाना कि text, तारीख, number और currency भाषा/region के हिसाब से बदल सकें — code बदले बिना। **l10n** असली translation का काम है। आम stack: strings के लिए `i18next` + `react-i18next`, device की भाषा जानने के लिए `expo-localization`।

---

## 🔴 Problem it Solves
```
बिना i18n:
  ❌ Text code में hard-coded: <Text>Welcome</Text>
  ❌ भारत में Hindi, Tamil, Bengali users छूट जाते हैं
  ❌ नई भाषा जोड़ने के लिए हर screen बदलनी पड़ती है
  ❌ Date/currency गलत format (₹1,00,000 vs 100,000)
i18n के साथ:
  ✅ t('welcome') → भाषा के हिसाब से text
  ✅ नई भाषा = सिर्फ नई JSON file
  ✅ RTL (Arabic/Urdu) layout support
```

## 🔴 यह क्यों बना? (Hindi)
```
भारत में 22 official भाषाएँ हैं।
Hard-coded text हर भाषा में नया version माँगता है।
i18n से text अलग file में, code एक ही।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Install: npx expo install expo-localization ; npm i i18next react-i18next
Step 2 → translations JSON बनाओ: en.json, hi.json
Step 3 → i18n.js में i18next.init({ resources, lng, fallbackLng })
Step 4 → App के root पर i18n import करो (side-effect import)
Step 5 → Components में const { t } = useTranslation(); <Text>{t('welcome')}</Text>
Step 6 → Device language: getLocales()[0].languageCode
Step 7 → User की चुनी भाषा AsyncStorage में save, अगली बार वही load
Step 8 → Plural/interpolation: t('items', { count: 3 })
Step 9 → Dates/numbers: Intl.NumberFormat / Intl.DateTimeFormat
```

## 🟢 कैसे काम करता है? (Hindi)
```
JSON files में key → translation।
t('key') current भाषा की value देता है।
भाषा बदलो (i18n.changeLanguage) → सारे components re-render।
Missing key हो तो fallbackLng (English) दिखता है।
```

---

## 🟡 Real World Example
**Swiggy/Zomato** Hindi, Tamil, Telugu, Bengali आदि में चलते हैं — "Order placed" हर भाषा में अलग, और "₹349" Indian format में। **Paytm** में भाषा चुनने की screen होती है (Settings → Language), जो चुनी जाने पर पूरा UI तुरंत बदल देती है। **Amazon India** में Hindi toggle भी यही pattern है।

## 🟡 Real Example Hindi mein
Swiggy में Hindi चुनो → "Add to cart" की जगह "कार्ट में जोड़ें"। Paytm में Language setting बदलते ही पूरी app की भाषा बदल जाती है — सब translation files से।

---

## 💻 Code Example — Basic
```jsx
// ---------- i18n.js ----------
import i18n from 'i18next';                              // core library
import { initReactI18next } from 'react-i18next';       // React binding
import { getLocales } from 'expo-localization';          // device language (Expo)

const resources = {                                      // translations
  en: { translation: { welcome: 'Welcome', items_one: '{{count}} item', items_other: '{{count}} items' } },
  hi: { translation: { welcome: 'स्वागत है', items_one: '{{count}} वस्तु', items_other: '{{count}} वस्तुएँ' } },
};

const deviceLang = getLocales()[0]?.languageCode ?? 'en'; // e.g. 'hi' (fallback 'en')

i18n.use(initReactI18next).init({                        // initialise
  resources,                                             // all strings
  lng: deviceLang,                                       // start language
  fallbackLng: 'en',                                     // if key missing
  interpolation: { escapeValue: false },                 // React already escapes
});

export default i18n;                                     // export instance

// ---------- App.jsx ----------
import React from 'react';
import { View, Text, Button } from 'react-native';
import { useTranslation } from 'react-i18next';          // hook
import './i18n';                                         // run init once (side effect)

export default function App() {
  const { t, i18n } = useTranslation();                  // t = translate fn
  return (
    <View style={{ padding: 24 }}>
      <Text>{t('welcome')}</Text>                        {/* translated text */}
      <Text>{t('items', { count: 3 })}</Text>            {/* plural: "3 items" / "3 वस्तुएँ" */}
      <Button title="हिंदी" onPress={() => i18n.changeLanguage('hi')} />   {/* switch */}
      <Button title="English" onPress={() => i18n.changeLanguage('en')} />
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// ---------- i18n.js — persisted language + RTL + safe formatting ----------
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import { getLocales } from 'expo-localization';
import AsyncStorage from '@react-native-async-storage/async-storage'; // npx expo install ...
import { I18nManager } from 'react-native';              // RTL control

const KEY = 'app_lang';                                  // storage key
const RTL = ['ar', 'ur', 'he'];                          // right-to-left languages

export async function initI18n(resources) {
  let lng = 'en';                                        // default
  try {
    const saved = await AsyncStorage.getItem(KEY);       // user-chosen language?
    lng = saved ?? getLocales()[0]?.languageCode ?? 'en'; // else device language
  } catch (e) {
    console.warn('lang load failed', e);                 // storage error: use default
  }

  await i18n.use(initReactI18next).init({
    resources, lng, fallbackLng: 'en',
    interpolation: { escapeValue: false },
    returnNull: false,                                   // never return null
  });
  return i18n;
}

export async function setLanguage(lng) {
  await i18n.changeLanguage(lng);                        // UI update
  await AsyncStorage.setItem(KEY, lng);                  // remember choice
  const isRTL = RTL.includes(lng);                       // direction needed?
  if (I18nManager.isRTL !== isRTL) {                     // only if different
    I18nManager.allowRTL(isRTL);                         // permit
    I18nManager.forceRTL(isRTL);                         // force
    // NOTE: RTL change app restart के बाद पूरी तरह लागू होता है
    // Expo: expo-updates का Updates.reloadAsync() call कर सकते हैं
  }
}

// Currency/date formatting — Indian style
export function formatINR(amount, lng = 'en-IN') {
  return new Intl.NumberFormat(lng, { style: 'currency', currency: 'INR' }).format(amount);
  // 100000 → "₹1,00,000.00"
}
// NOTE: Hermes पर Intl support RN 0.70+ के साथ बेहतर है, पर edge locales पर
// verify करो (check current docs). ज़रूरत हो तो `intl-pluralrules` polyfill।
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Device language | `getLocales()` — दोनों | दोनों |
| RTL | `forceRTL` + restart; manifest में `android:supportsRtl="true"` | `forceRTL` + restart |
| App-level language setting | Android 13+ per-app language (locale config XML) | iOS Settings में per-app language (CFBundleLocalizations) |
| Store listing/app name translate | `res/values-hi/strings.xml` | `InfoPlist.strings` |
| Font for Devanagari/Tamil | System font mostly OK | System font OK |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-localization
import { getLocales } from 'expo-localization';
const lang = getLocales()[0].languageCode;          // 'hi', 'en'
// App Store/Play में supported languages के लिए app.json:
// "ios": { "infoPlist": { "CFBundleAllowMixedLocalizations": true } },
// "locales": { "hi": "./locales/hi.json" }  // app name/permission text translate
```
CLI way:
```jsx
// npm i react-native-localize
import * as RNLocalize from 'react-native-localize';
const lang = RNLocalize.getLocales()[0].languageCode;
// iOS: pod install ; Xcode में project localizations जोड़ो
// Android: res/values-hi/strings.xml बनाओ
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: String जोड़कर बनाना: `t('hello') + name`
✅ Correct: Interpolation: `t('hello', { name })` → `"Hello {{name}}"`

❌ Mistake 2: Plural को `count === 1 ? ... : ...` से हाथ से करना
✅ Correct: i18next plural keys (`_one`, `_other`, और ज़रूरत हो तो `_few` आदि)

❌ Mistake 3: Fixed-width buttons — Hindi/German text लंबा होकर कट जाता
✅ Correct: Flexible layout, `flexShrink`, `numberOfLines` जाँचो

❌ Mistake 4: `marginLeft` बनाम RTL
✅ Correct: `marginStart/marginEnd`, `paddingStart` (logical properties)

❌ Mistake 5: Currency/date को manual format
✅ Correct: `Intl.NumberFormat`/`DateTimeFormat` या date-fns locale

---

## 🧠 Tricky Interview Question
```jsx
const { t } = useTranslation();
const label = t('welcome');            // module-level पर नहीं, component के अंदर
i18n.changeLanguage('hi');
console.log(label);
```
Q: `label` में कौन सी भाषा होगी?

Answer: पुरानी भाषा (English)। `t('welcome')` call के समय का string लौटाता है — वह plain string है, reactive नहीं। UI तभी बदलता है जब `useTranslation()` hook वाला component re-render हो और `t` दोबारा call हो। इसलिए `t()` को render के अंदर call करो; module-level constants (जैसे `const TITLE = t('x')`) में भाषा बदलने पर update नहीं होता।

---

## ⚫ Interview Questions + Answers
Q1: i18n और l10n में फर्क?
A1: i18n = app को multi-language के लिए तैयार करना (architecture); l10n = किसी specific भाषा/region का actual translation और formatting।

Q2: Device की भाषा कैसे पता करें?
A2: Expo: `expo-localization` का `getLocales()`; CLI: `react-native-localize`। पुराने `Localization.locale` की जगह `getLocales()` use करें (check current docs)।

Q3: RTL कैसे support करें?
A3: Logical style props (start/end), `I18nManager.forceRTL`, और layout बदलने के लिए app restart।

Q4: भाषा चुनाव persist कैसे?
A4: AsyncStorage/MMKV में save करो और startup पर `i18n.init` से पहले पढ़ो।

Q5: Translation files बड़ी हों तो?
A5: Namespaces में बाँटो और lazy load (`i18next-http-backend` या dynamic import); OTA translations के लिए server/Expo Updates।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- India जैसे multi-language market (Hindi, Tamil, Bengali...)
- Global release, Play/App Store में कई देश
- Currency/date region के हिसाब से

❌ Avoid when:
- Internal tool जो सिर्फ एक भाषा में रहेगा (पर तब भी strings अलग रखना अच्छा है)

---

## 📊 Visual Diagram
```
  Device lang (hi) ─┐
  Saved choice ─────┼─► i18next.init(lng)
                    │
  en.json  hi.json ─┘
       │
  t('welcome') ──► "स्वागत है"
       │
  changeLanguage('en') ──► सारे useTranslation components re-render
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| i18n | Make app translatable | बहु-भाषा तैयारी |
| l10n | Actual localisation | स्थानीयकरण |
| Locale | Language + region (hi-IN) | भाषा+क्षेत्र |
| Fallback | Default when missing | विकल्प भाषा |
| Plural | Count-based forms | बहुवचन रूप |
| RTL | Right-to-left layout | दाएँ से बाएँ |

---

## ⚡ 3-Line Summary
English: Keep text in JSON files and read it with `t('key')` via i18next.
Detect device language, persist user choice, use Intl for currency/dates.
Use logical styles (start/end) for RTL.

Hindi: Text JSON files में रखो और `t('key')` से पढ़ो।
Device भाषा पहचानो, user की चुनी भाषा save करो, Intl से currency/date।
RTL के लिए start/end styles।

---

## ➡️ Next Topic
**187. TypeScript in React Native** — props, navigation और API के लिए type safety।

---
