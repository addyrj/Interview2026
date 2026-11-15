# 55. Fonts — Custom Fonts Setup
# हिंदी में: Custom Fonts जोड़ना
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs)। Expo में `expo-font` और `@expo-google-fonts/*`; CLI में `react-native.config.js` + `npx react-native-asset`।

---

## 🔵 Simple Definition (English)
Custom fonts let you use your own brand typeface (e.g. Poppins, Inter, a Devanagari font) instead of the system font. You add the font files to the app, load them, and then use `fontFamily` in styles.

## 🔵 सरल परिभाषा (Hindi)
Custom fonts से आप system font की जगह अपना brand typeface (जैसे Poppins, Inter, कोई देवनागरी font) इस्तेमाल करते हो। Font files app में जोड़ो, load करो, फिर style में `fontFamily` दो।

---

## 🔴 Problem it Solves
```
❌ सारे apps एक जैसे (Roboto / San Francisco) दिखते हैं
❌ Brand identity (Zomato/Swiggy की अपनी पहचान) नहीं बनती
❌ Hindi/देवनागरी या खास scripts का सुंदर font चाहिए
```

## 🔴 यह क्यों बना? (Hindi)
```
Brand और readability के लिए अपना font चाहिए। मोबाइल में font bundle के साथ
आता है, इसलिए उसे app में जोड़ना और load करना पड़ता है।
```

---

## 🟢 How it Works — Step by Step
```
Expo (expo-font):
Step 1 → npx expo install expo-font
Step 2 → assets/fonts/ में .ttf / .otf files रखो
Step 3 → useFonts({ 'Poppins-Regular': require('./assets/fonts/Poppins-Regular.ttf') })
Step 4 → fonts load होने तक splash रोको (expo-splash-screen)
Step 5 → style में fontFamily: 'Poppins-Regular'

Expo config plugin (build-time, dev build/EAS):
  app.json → "plugins": [["expo-font", { "fonts": ["./assets/fonts/Poppins-Regular.ttf"] }]]
  (SDK 51+ पर उपलब्ध; यह font को native बनाते समय एम्बेड करता है — docs जाँचो)

CLI:
Step 1 → fonts को assets/fonts/ में रखो
Step 2 → react-native.config.js: module.exports = { assets: ['./assets/fonts/'] }
Step 3 → npx react-native-asset  (iOS Info.plist + Android assets में जोड़ता है)
Step 4 → rebuild ज़रूरी
```

## 🟢 कैसे काम करता है? (Hindi)
```
Expo: expo-font install → .ttf files assets/fonts/ में → useFonts से load
      → load होने तक splash रोको → fontFamily में नाम दो
Expo plugin: app.json के plugins में fonts की list (build-time embed)
CLI: react-native.config.js में assets path → npx react-native-asset → rebuild
```

---

## 🟡 Real World Example
**Zomato** का अपना Okra font, **Swiggy** का Proxima/Gotham जैसा geometric font, और **Paytm** का अपना brand font app की पहचान बनाते हैं। **Hindi-news** apps देवनागरी के लिए Noto Sans Devanagari जैसे fonts लगाते हैं।

## 🟡 Real Example Hindi mein
Zomato के हर बटन और title का अलग-सा font उनकी पहचान है। यह वही custom font है जिसे app में bundle करके `fontFamily` से इस्तेमाल किया जाता है।

---

## 💻 Code Example — Basic
```jsx
// Basic (Expo): useFonts से Poppins load करो
// Install: npx expo install expo-font @expo-google-fonts/poppins
import React from 'react';                                      // React
import { View, Text, StyleSheet } from 'react-native';          // core
import { useFonts, Poppins_400Regular, Poppins_700Bold } from '@expo-google-fonts/poppins'; // fonts

export default function App() {
  const [loaded, error] = useFonts({                            // load होने की स्थिति
    Poppins_400Regular,                                         // regular
    Poppins_700Bold,                                            // bold
  });

  if (!loaded && !error) return null;                           // load होने तक कुछ नहीं दिखाओ

  return (
    <View style={styles.box}>
      <Text style={styles.regular}>Hello, Regular font</Text>{/* custom regular */}
      <Text style={styles.bold}>नमस्ते, Bold font</Text>{/* custom bold */}
    </View>
  );
}

const styles = StyleSheet.create({
  box: { flex: 1, justifyContent: 'center', alignItems: 'center' },    // बीच में
  regular: { fontFamily: 'Poppins_400Regular', fontSize: 20 },         // नाम वही जो useFonts में key है
  bold: { fontFamily: 'Poppins_700Bold', fontSize: 20 },               // bold family
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced (Expo): local .ttf + splash screen रोकना + error handling + reusable Text
// Install: npx expo install expo-font expo-splash-screen
import React, { useCallback, useEffect } from 'react';          // hooks
import { View, Text, StyleSheet, Platform } from 'react-native'; // core
import { useFonts } from 'expo-font';                           // font loader
import * as SplashScreen from 'expo-splash-screen';             // splash control

SplashScreen.preventAutoHideAsync();                            // fonts आने तक splash रखो

// Reusable Text: weight को family में map करो
export function AppText({ weight = 'regular', style, ...props }) {
  const family = weight === 'bold' ? 'Brand-Bold' : 'Brand-Regular'; // नाम useFonts वाला
  return (
    <Text
      {...props}
      style={[
        { fontFamily: family },                                 // custom family
        Platform.OS === 'android' && { fontWeight: 'normal' },  // Android: fontWeight family से टकराता है
        style,
      ]}
    />
  );
}

export default function App() {
  const [loaded, error] = useFonts({
    'Brand-Regular': require('./assets/fonts/Brand-Regular.ttf'), // आपकी local file
    'Brand-Bold': require('./assets/fonts/Brand-Bold.ttf'),
  });

  useEffect(() => {
    if (loaded || error) SplashScreen.hideAsync();              // load या error पर splash हटाओ
  }, [loaded, error]);

  if (!loaded && !error) return null;                           // अभी रुको
  // error हो तो system font पर fallback होकर चलता रहेगा

  return (
    <View style={styles.box}>
      <AppText weight="bold" style={styles.title}>Zomato Clone</AppText>
      <AppText>Custom font loaded</AppText>
    </View>
  );
}

const styles = StyleSheet.create({
  box: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 28 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `fontFamily` का नाम | **File name** (extension बिना) | font का **PostScript/family नाम** (file name नहीं) |
| `fontWeight` | Custom font के साथ कभी-कभी ignore/टकराव; हर weight की अलग file रखो | Family में weights हों तो काम करता है |
| Bundle | `android/app/src/main/assets/fonts` | `Info.plist` में `UIAppFonts` |
| Fallback | system font | system font |
| Italic | अलग file (family में नाम) | `fontStyle` से (family में हो तो) |

> Expo में `useFonts({ 'MyName': file })` का key ही runtime नाम है, इसलिए दोनों OS पर एक जैसा रहता है (expo-font runtime loading का फ़ायदा)।

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Runtime loading
import { useFonts } from 'expo-font';
const [loaded] = useFonts({ 'Brand-Regular': require('./assets/fonts/Brand-Regular.ttf') });
// फिर style={{ fontFamily: 'Brand-Regular' }}
```
CLI way:
```jsx
// 1) fonts को ./assets/fonts/ में रखो
// 2) react-native.config.js
//    module.exports = { assets: ['./assets/fonts/'] };
// 3) टर्मिनल: npx react-native-asset   (फिर rebuild)
// 4) style={{ fontFamily: 'Brand-Regular' }}  // iOS पर PostScript name जाँचो
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Font load होने से पहले render करना (पहले system font चमकता है)
✅ Correct: `useFonts` का result जाँचो + splash रोको।

❌ Mistake 2: iOS पर file name को family name समझना
✅ Correct: Font Book/Font info से PostScript name देखो।

❌ Mistake 3: `fontFamily: 'Poppins'` के साथ `fontWeight: 'bold'` पर bold की उम्मीद
✅ Correct: हर weight की अलग file load करो (`Poppins-Bold`) और उसका नाम दो।

❌ Mistake 4: CLI में fonts जोड़कर rebuild न करना
✅ Correct: Native assets बदले हैं, rebuild करो।

---

## 🧠 Tricky Interview Question
```jsx
<Text style={{ fontFamily: 'Poppins-Bold', fontWeight: '900' }}>Hi</Text>
```
**Q: Android पर text अजीब/system font में क्यों दिखता है?**

Answer: Android पर custom `fontFamily` के साथ `fontWeight` देने से RN weight के हिसाब से अलग font variant ढूँढ सकता है, और न मिलने पर system font पर fallback हो सकता है (व्यवहार RN version पर निर्भर)। हल: हर weight की अलग file रखो, उसका नाम `fontFamily` में दो और `fontWeight` हटाओ।

---

## ⚫ Interview Questions + Answers
Q1: Expo में font load कैसे?
A1: `expo-font` का `useFonts` (या `Font.loadAsync`) और splash को `preventAutoHideAsync` से रोकना।

Q2: Build-time और runtime loading का फ़र्क?
A2: Config plugin build में font embed करता है (तुरंत उपलब्ध); `useFonts` runtime पर लोड करता है (थोड़ी देर)।

Q3: Google Fonts आसानी से?
A3: `@expo-google-fonts/<font-name>` packages।

Q4: Font file format?
A4: `.ttf` और `.otf` (दोनों OS)।

Q5: Hindi/देवनागरी के लिए?
A5: Noto Sans Devanagari, Hind, Mukta जैसे fonts; Latin-only fonts में Hindi glyph नहीं होते, system fallback आता है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Brand identity ज़रूरी
- खास script (देवनागरी, तमिल आदि) का बेहतर look

❌ Avoid when:
- हर weight की भारी files (app size बढ़ती है)
- System font से ही काम चल जाए

---

## 📊 Visual Diagram
```
 assets/fonts/Brand-Bold.ttf
        │ useFonts / react-native-asset
        ▼
   App में register (नाम: 'Brand-Bold')
        │
 <Text style={{ fontFamily: 'Brand-Bold' }}>  ──►  स्क्रीन पर custom font
 (load न हुआ? → system font fallback)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| fontFamily | Font का नाम | font परिवार |
| .ttf / .otf | Font file formats | font files |
| useFonts | Expo का loader hook | font लोड करने वाला hook |
| PostScript name | iOS का font नाम | PostScript नाम |
| Splash screen | शुरुआती screen | शुरुआती पर्दा |

---

## ⚡ 3-Line Summary
English:
1. Add `.ttf` files, load them (`useFonts` in Expo, `react-native-asset` in CLI), then use `fontFamily`.
2. Keep splash until fonts load; handle errors.
3. Use separate files per weight; iOS uses PostScript names.

Hindi:
1. `.ttf` files जोड़ो, load करो (Expo: `useFonts`, CLI: `react-native-asset`), फिर `fontFamily` दो।
2. Fonts load होने तक splash रोको; error सँभालो।
3. हर weight की अलग file; iOS में PostScript नाम।

---

## ➡️ Next Topic
**56. Icons — React Native Vector Icons** — fonts की तरह icons का इस्तेमाल।
