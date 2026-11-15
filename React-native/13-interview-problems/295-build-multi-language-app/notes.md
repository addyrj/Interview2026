# 295. Build Multi-Language App
# हिंदी में: Multi-Language (बहुभाषी) App बनाओ
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 / React Native 0.76** (check current docs — APIs change between SDKs). `expo-localization` `getLocales()` is the API from SDK 51+; older SDKs used `Localization.locale`.
> Files: [`i18n.js`](./i18n.js) · [`LanguageScreen.jsx`](./LanguageScreen.jsx) · [`locales/en.json`](./locales/en.json) · [`locales/hi.json`](./locales/hi.json)
> Install: `npx expo install expo-localization @react-native-async-storage/async-storage && npm i i18next react-i18next`

---

## 🔵 Simple Definition (English)
A **multi-language app** shows all text in the user's chosen language. We store strings in JSON files per language and use **i18next** (`t('key')`) to pick the right text. Changing language re-renders the UI instantly.

## 🔵 सरल परिभाषा (Hindi)
**Multi-language app** user की चुनी हुई भाषा में पूरा text दिखाता है। हम हर भाषा की strings JSON files में रखते हैं और **i18next** (`t('key')`) सही text चुनता है। भाषा बदलते ही UI तुरंत बदल जाती है।

---

## 🔴 Problem it Solves
```
❌ Text code में hard-coded: <Text>Welcome</Text>
❌ भारत में Hindi, Tamil, Bengali... users -> सिर्फ English app से users छूट जाते हैं
❌ हर भाषा के लिए अलग app बनाना impossible
❌ "1 item" vs "2 items" जैसे plural rules हर भाषा में अलग
```

## 🔴 यह क्यों बना? (Hindi)
```
Zomato, Swiggy, PhonePe, Paytm, ShareChat 10+ भारतीय भाषाएँ support करते हैं।
Strings को code से अलग रखने से translators सिर्फ JSON बदलते हैं,
developer को code छूना नहीं पड़ता। इसे i18n (internationalization) कहते हैं।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Create locales/en.json and locales/hi.json with same keys
Step 2 → i18n.js: init i18next with resources + starting language
Step 3 → Starting language = phone language from expo-localization (fallback 'en')
Step 4 → Components call const { t } = useTranslation(); t('welcome')
Step 5 → User taps Hindi -> i18n.changeLanguage('hi') -> all t() re-render
Step 6 → Save choice in AsyncStorage; load it at app start
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → en.json और hi.json बनाओ (keys same, values अलग)
Step 2 → i18n.js में i18next init करो
Step 3 → शुरुआती भाषा = फ़ोन की भाषा (न मिले तो English)
Step 4 → Component में t('welcome') लिखो
Step 5 → Hindi चुनने पर changeLanguage('hi') -> सारा text बदल जाता है
Step 6 → Choice AsyncStorage में save, app start पर load
```

---

## 🟡 Real World Example
**Zomato** and **Swiggy** let you pick Hindi, Tamil, Telugu, Marathi, etc. in Settings. **PhonePe** shows payment instructions in your language, which builds trust for first-time UPI users.

## 🟡 Real Example Hindi mein
**Zomato और Swiggy** Settings में Hindi, Tamil, Telugu, Marathi चुनने देते हैं। **PhonePe** payment steps आपकी भाषा में दिखाता है, जिससे पहली बार UPI चलाने वाले users का भरोसा बढ़ता है।

---

## 💻 Code Example — Basic
No library: a tiny dictionary + state (good for 2-3 screens).

```jsx
// Basic: no library, plain dictionary
import React, { useState } from 'react'; // React + state
import { View, Text, Button } from 'react-native'; // UI

// All strings in one object per language
const STRINGS = {
  en: { welcome: 'Welcome to Zomato', order: 'Order now' }, // English
  hi: { welcome: 'Zomato में आपका स्वागत है', order: 'अभी ऑर्डर करें' }, // Hindi
};

export default function BasicLang() {
  const [lang, setLang] = useState('en'); // current language
  const t = (key) => STRINGS[lang][key] ?? key; // translate, fallback to key

  return (
    <View style={{ padding: 40 }}>
      {/* shows text in selected language */}
      <Text>{t('welcome')}</Text>
      <Button title={t('order')} onPress={() => {}} />
      {/* toggle language */}
      <Button title="EN / हिंदी" onPress={() => setLang((l) => (l === 'en' ? 'hi' : 'en'))} />
    </View>
  );
}
```

## 💻 Code Example — Advanced
Full code: [`i18n.js`](./i18n.js) + [`LanguageScreen.jsx`](./LanguageScreen.jsx). Key part:

```js
// i18n.js (key part)
const deviceLang = getLocales()[0]?.languageCode ?? 'en';          // 'hi' on a Hindi phone
i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, hi: { translation: hi } }, // bundled strings
  lng: SUPPORTED.includes(deviceLang) ? deviceLang : 'en',          // start language
  fallbackLng: 'en',                                                // missing key -> English
  interpolation: { escapeValue: false },                            // React already escapes
});
export async function setLanguage(lang) {
  await i18n.changeLanguage(lang);                                  // re-renders everything
  try { await AsyncStorage.setItem('app-language', lang); } catch (e) {} // persist
}
```
```json
// en.json plural keys (i18next v21+ JSON v4 format; older versions used `_plural`)
"items_count_one": "{{count}} item in cart",
"items_count_other": "{{count}} items in cart"
```
Usage: `t('items_count', { count: 2 })` -> "2 items in cart", `t('hello_user', { name: 'Aditya' })`.

> Verified: rendered and clicked under jsdom (mocked expo-localization + AsyncStorage): starts in Hindi, switches to English, plural "1 item" -> "2 items" worked. Real device locale detection: not run.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Per-app language setting | Android 13+ system "App languages" | iOS 13+ Settings -> App -> Language |
| Declare supported languages | `expo-localization` plugin `supportedLocales` -> `resConfigs` | Plugin -> `CFBundleLocalizations` in Info.plist |
| RTL (Arabic/Urdu) | `I18nManager.forceRTL(true)` + restart | Same, restart needed |
| Device locale | `getLocales()` | `getLocales()` |
| Hindi font | Roboto/Noto Devanagari built in | SF + Devanagari Sangam MN built in |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo install expo-localization                  # SDK-compatible version
```
```json
// app.json (optional: tell stores which languages you support)
{ "expo": { "plugins": [["expo-localization", { "supportedLocales": { "ios": ["en", "hi"], "android": ["en", "hi"] } }]] } }
```
CLI way:
```bash
npm install react-native-localize          # popular CLI alternative to expo-localization
cd ios && pod install && cd ..             # link iOS pod
```
```js
import * as RNLocalize from 'react-native-localize';   // CLI-side API
const lang = RNLocalize.getLocales()[0].languageCode;  // 'hi' / 'en'
```
(`expo-localization` also works in bare RN with `expo` modules installed.)

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Hard-coding text: `<Text>Welcome</Text>`.
✅ **Correct:** `<Text>{t('welcome')}</Text>`.

❌ **Mistake 2:** Building sentences by concatenation: `'Hello ' + name + '!'`.
✅ **Correct:** `t('hello_user', { name })` - word order differs per language.

❌ **Mistake 3:** `count === 1 ? 'item' : 'items'` in code.
✅ **Correct:** plural keys `_one` / `_other` and `t(key, { count })`.

❌ **Mistake 4:** Keys exist in en.json but missing in hi.json -> blank text.
✅ **Correct:** set `fallbackLng: 'en'` and check keys in CI.

❌ **Mistake 5:** Forgetting to import `./i18n` once at app start (so `useTranslation` warns "NO_I18NEXT_INSTANCE").
✅ **Correct:** `import './i18n'` at top of App.js.

---

## 🧠 Tricky Interview Question
**Q:** User sets app language to Hindi, kills the app and reopens. Phone language is English. Which language shows, and for how long might the wrong one flash?

**Answer:** Saved Hindi should win. But AsyncStorage is async, so `init` starts with the device language (English) and `loadSavedLanguage()` switches to Hindi a few milliseconds later - a visible flash. Fix: load the saved language before rendering (keep the splash screen visible via `expo-splash-screen` until `loadSavedLanguage()` resolves) or init i18n inside an async bootstrap.

---

## ⚫ Interview Questions + Answers

**Q1: What is i18n vs l10n?**
A1: i18n (internationalization) = preparing the app to support many languages (keys, no hard-coded text). l10n (localization) = adding actual translations/formats for a region.

**Q2: How to format dates, currency (Rs) per locale?**
A2: `Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' })` - Hermes supports Intl on modern RN. Verify on old Android versions.

**Q3: How to handle RTL languages?**
A3: `I18nManager.allowRTL(true)`, `I18nManager.forceRTL(true)` then restart the app; use `marginStart/End` instead of left/right.

**Q4: i18next vs expo-localization?**
A4: expo-localization only tells you the device locale/region. i18next does translation lookup, plurals, interpolation. They are used together.

**Q5: How to load translations lazily for 10 languages?**
A5: Use `i18next-http-backend` or dynamic `import()` of JSON then `i18n.addResourceBundle(lang, 'translation', data)`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Target is India/global market with many languages
- Marketing/legal requires local language

❌ Avoid when:
- Internal tool in one language (extra overhead)
- Strings are only 3-4 and never change (simple dictionary is enough - see Basic)

---

## 📊 Visual Diagram
```
 en.json ─┐
 hi.json ─┼─▶ i18n.js (i18next.init) ◀── expo-localization (phone language)
 ta.json ─┘          │                  ◀── AsyncStorage (saved choice)
                     ▼
        useTranslation() -> t('key')
                     │
   <Text>{t('welcome')}</Text> ──▶ "Zomato में आपका स्वागत है"
 User taps "English" ─▶ changeLanguage('en') ─▶ all <Text> re-render
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| i18n | Internationalization | अंतर्राष्ट्रीयकरण (भाषा support तैयारी) |
| l10n | Localization | स्थानीयकरण (असली अनुवाद) |
| Locale | Language + region (hi-IN) | भाषा + क्षेत्र |
| Interpolation | Insert values in strings `{{name}}` | String में value डालना |
| Fallback | Default language if key missing | Key न मिलने पर default भाषा |
| RTL | Right-to-left layout | दाएँ से बाएँ layout |

---

## ⚡ 3-Line Summary
**English:**
1. Keep every string in per-language JSON and read with `t('key')`.
2. Start with device language, let user change it, and save it in AsyncStorage.
3. Use plural keys and interpolation instead of string concatenation.

**Hindi:**
1. हर string भाषा-वार JSON में रखो और `t('key')` से पढ़ो।
2. फ़ोन की भाषा से शुरू करो, user को बदलने दो, और AsyncStorage में save करो।
3. String जोड़ने की जगह plural keys और interpolation use करो।

---

## ➡️ Next Topic
**296. Build Custom Hook - useLocation** - अब reusable hooks: GPS location को hook में लपेटना।
