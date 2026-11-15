# 40. StatusBar Component
# हिंदी में: StatusBar Component (ऊपर की Status पट्टी)
# Platform: Android ✅ | iOS ✅ | Both ✅ (कुछ props सिर्फ Android)

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs)। Expo में `expo-status-bar` भी मिलता है। Android edge-to-edge का व्यवहार SDK/RN version के साथ बदला है (SDK 52+ में नए projects में default behaviour जाँच लो)।

---

## 🔵 Simple Definition (English)
`StatusBar` controls the system bar at the top of the screen (time, battery, network). You can change its text colour (light/dark), background (Android), and hide it.

## 🔵 सरल परिभाषा (Hindi)
`StatusBar` स्क्रीन के ऊपर की system पट्टी (समय, बैटरी, network) को control करता है। आप उसका text रंग (light/dark), background (Android) बदल सकते हो और छुपा भी सकते हो।

---

## 🔴 Problem it Solves
```
❌ Dark header पर काले status icons दिखते ही नहीं
❌ App का brand रंग और status bar का रंग मेल नहीं खाते
❌ Video/Splash पर status bar छुपाना हो
```

## 🔴 यह क्यों बना? (Hindi)
```
Status bar OS की चीज़ है, JS से सीधे नहीं बदल सकते। StatusBar component यह पुल बनाता है,
ताकि हर screen अपनी ज़रूरत के हिसाब से style चुने।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → import { StatusBar } from 'react-native' (या expo-status-bar)
Step 2 → <StatusBar barStyle="light-content" /> → सफ़ेद icons
Step 3 → Android: backgroundColor="#e23744" (RN StatusBar में) रंग बदलता है
Step 4 → hidden={true} से छुपाओ
Step 5 → जो StatusBar आख़िरी mount हुआ वही जीतता है (stack की तरह)
Step 6 → Imperative API: StatusBar.setBarStyle('dark-content')
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → StatusBar import करो
Step 2 → barStyle="light-content" से सफ़ेद icons
Step 3 → Android में backgroundColor से रंग
Step 4 → hidden से छुपाओ
Step 5 → आख़िरी mount हुआ StatusBar जीतता है
Step 6 → StatusBar.setBarStyle() से code द्वारा भी बदल सकते हो
```

---

## 🟡 Real World Example
**Swiggy** की orange header पर सफ़ेद status icons, **Zomato** की सफ़ेद home screen पर काले icons, **Paytm** की light-blue header पर dark icons, **Instagram** Stories में status bar छुपी या transparent होती है।

## 🟡 Real Example Hindi mein
Swiggy की नारंगी header में status bar के icons सफ़ेद रखे जाते हैं ताकि पढ़े जा सकें; सफ़ेद background वाली screen पर काले icons।

---

## 💻 Code Example — Basic
```jsx
// Basic: dark header + light icons
import React from 'react';                                      // React
import { View, Text, StatusBar, StyleSheet } from 'react-native'; // core

export default function Basic() {
  return (
    <View style={styles.header}>
      <StatusBar
        barStyle="light-content"                                 // सफ़ेद icons
        backgroundColor="#e23744"                                // Android: रंग (iOS पर ignore)
      />
      <Text style={styles.title}>Zomato Clone</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flex: 1, backgroundColor: '#e23744', justifyContent: 'center', alignItems: 'center' }, // लाल बैकग्राउंड
  title: { color: '#fff', fontSize: 22 },                       // सफ़ेद title
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: Screen focus पर status bar बदलना (react-navigation) + Platform handling
// Install: npm i @react-navigation/native (project में पहले से हो तो ज़रूरत नहीं)
import React, { useCallback } from 'react';                     // useCallback
import { View, Text, StatusBar, Platform, StyleSheet } from 'react-native'; // core
import { useFocusEffect } from '@react-navigation/native';      // focus hook

export default function DetailScreen() {
  // इस screen पर आने पर बदलो, छोड़ने पर पुराना वापस रखो
  useFocusEffect(
    useCallback(() => {
      StatusBar.setBarStyle('light-content');                   // सफ़ेद icons (दोनों OS)
      if (Platform.OS === 'android') {
        StatusBar.setBackgroundColor('#111');                   // सिर्फ Android
        StatusBar.setTranslucent(false);                        // Android: content नीचे से शुरू
      }
      return () => {                                            // screen छोड़ते समय
        StatusBar.setBarStyle('dark-content');                  // वापस पुराना
        if (Platform.OS === 'android') StatusBar.setBackgroundColor('#fff');
      };
    }, []),
  );

  return (
    <View style={styles.box}>
      <Text style={{ color: '#fff' }}>Dark detail screen</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  box: { flex: 1, backgroundColor: '#111', justifyContent: 'center', alignItems: 'center' }, // dark screen
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `backgroundColor` | ✅ | ❌ (header View को रंग दो / safe area) |
| `translucent` | ✅ (content ऊपर तक) | ❌ (हमेशा translucent जैसा) |
| `barStyle` | `light-content` / `dark-content` (API 23+) | `light-content` / `dark-content` / `default` |
| `networkActivityIndicatorVisible` | ❌ | ✅ (पुराना, deprecated जैसा) |
| `showHideTransition` | ❌ | ✅ `fade` / `slide` |
| Edge-to-edge | नए Android/SDK में default हो सकता है; `backgroundColor` का असर बदल सकता है (version-dependent) | लागू नहीं |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// expo-status-bar: सरल wrapper (SDK के साथ आता है)
import { StatusBar } from 'expo-status-bar';
<StatusBar style="light" />   // style: light / dark / auto / inverted
```
CLI way:
```jsx
// react-native का StatusBar
import { StatusBar } from 'react-native';
<StatusBar barStyle="light-content" backgroundColor="#e23744" />
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: iOS पर `backgroundColor` से रंग बदलने की उम्मीद
✅ Correct: iOS में status bar के पीछे का रंग आपके View/SafeAreaView का होता है।

❌ Mistake 2: Dark mode में `dark-content` रखना → icons दिखते नहीं
✅ Correct: Theme के हिसाब से `barStyle` बदलो (`useColorScheme`) या `expo-status-bar` में `style="auto"`।

❌ Mistake 3: कई screens पर StatusBar डालकर भूल जाना कि आख़िरी mount जीतता है
✅ Correct: हर screen पर स्पष्ट style दो, या `useFocusEffect` इस्तेमाल करो।

---

## 🧠 Tricky Interview Question
```jsx
<StatusBar barStyle="light-content" />
// header सफ़ेद है
```
**Q: Status bar के icons क्यों नहीं दिख रहे?**

Answer: `light-content` का मतलब **सफ़ेद icons** है। सफ़ेद header पर सफ़ेद icons गायब दिखते हैं। नाम "content का रंग" बताता है, background का नहीं। सफ़ेद background पर `dark-content` चाहिए।

---

## ⚫ Interview Questions + Answers
Q1: `light-content` का मतलब?
A1: सफ़ेद text/icons (dark background के लिए)।

Q2: `translucent` क्या है (Android)?
A2: Status bar पारदर्शी हो जाती है और app content उसके पीछे तक फैलता है; इसलिए ऊपर padding चाहिए।

Q3: Expo का `StatusBar` और RN का फ़र्क?
A3: `expo-status-bar` में `style` (`light/dark/auto`), RN में `barStyle`; Expo वाला कुछ Android बारीकियाँ सँभालता है।

Q4: Status bar छुपाना?
A4: `<StatusBar hidden />`।

Q5: Notch/SafeArea से रिश्ता?
A5: Status bar की ऊँचाई के लिए `SafeAreaView`/`useSafeAreaInsets` इस्तेमाल करो।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Header रंग के हिसाब से icons का रंग बदलना
- Full-screen media में छुपाना

❌ Avoid when:
- हर component में बिना सोचे डालना (conflicts)
- iOS पर रंग बदलने के लिए (वहाँ View का रंग काम करेगा)

---

## 📊 Visual Diagram
```
┌──────────────────────────┐
│ 9:41      📶 🔋          │ ← StatusBar (barStyle, hidden)
├──────────────────────────┤
│  Header (backgroundColor)│
│  App content             │
└──────────────────────────┘
Android: StatusBar.backgroundColor | iOS: header View का रंग
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| barStyle | Icons का रंग-style | icons का style |
| translucent | पारदर्शी bar (Android) | पारदर्शी |
| hidden | छुपाना | छुपा हुआ |
| edge-to-edge | पूरी screen तक content | किनारे-से-किनारे |
| light-content | सफ़ेद icons | सफ़ेद content |

---

## ⚡ 3-Line Summary
English:
1. `StatusBar` styles the system bar: icon colour, hide, and background (Android).
2. `light-content` means white icons for dark backgrounds.
3. On iOS, the colour comes from your own view behind it.

Hindi:
1. `StatusBar` system पट्टी का icon रंग, छुपाना और background (Android) control करता है।
2. `light-content` = dark background के लिए सफ़ेद icons।
3. iOS में रंग आपके अपने View से आता है।

---

## ➡️ Next Topic
**41. SafeAreaView Component** — notch और status bar से बचकर content रखना।
