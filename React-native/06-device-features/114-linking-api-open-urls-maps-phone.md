# 114. Linking API (Open URLs, Maps, Phone)
# हिंदी में: Linking API — URL, Maps, Phone खोलना
# Platform: Android ✅ | iOS ✅ | Both ✅

---

**Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs).** `Linking` core RN में है। Expo में `expo-linking` भी है (deep link URL बनाने/parse करने के लिए)।

---

## 🔵 Simple Definition (English)
The **Linking API** lets your app open other apps or links through URL schemes: `https://` opens the browser, `tel:` opens the dialer, `mailto:` opens email, `geo:`/`maps:` opens the Maps app, `whatsapp://` opens WhatsApp. It also reads the URL that opened your own app.

## 🔵 सरल परिभाषा (Hindi)
**Linking API** URL schemes से दूसरे apps या links खोलती है: `https://` browser, `tel:` dialer, `mailto:` email, `geo:`/`maps:` Maps, `whatsapp://` WhatsApp। यह उस URL को भी पढ़ती है जिससे आपका अपना app खुला।

---

## 🔴 Problem it Solves
```
PROBLEM:
  "Call restaurant" बटन -> dialer कैसे खोलें?
  "Get directions" -> Google Maps कैसे खोलें?
  "Privacy policy" -> browser कैसे खोलें?

LINKING API:
  ✅ Linking.openURL('tel:+911234567890')
  ✅ Linking.canOpenURL(url) से पहले check
  ✅ Linking.getInitialURL() से app खुलने वाला URL
  ✅ Linking.openSettings() से app settings
```

## 🔴 यह क्यों बना? (Hindi)
App के अंदर हर चीज़ (dialer, maps, browser) दोबारा बनाना बेकार है। OS के पास पहले से ये apps हैं। Linking API URL देकर OS से कहती है "यह खोल दो"। साथ ही deep link (दूसरे app से हमारे app में आना) भी इसी से पकड़ते हैं।

---

## 🟢 How it Works — Step by Step
```
Step 1 → URL बनाओ: 'tel:+911234567890' या 'https://...' या maps URL
Step 2 → (ज़रूरी) Linking.canOpenURL(url) से check करो कि कोई app handle कर सकता है
Step 3 → Linking.openURL(url) call करो
Step 4 → OS URL scheme के हिसाब से सही app चुनता है और खोलता है
Step 5 → App background में जाता है; user वापस आ सकता है
Step 6 → Fail पर catch में fallback (जैसे web URL) दिखाओ
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → URL बनाओ (tel:, mailto:, https:, geo: आदि)
Step 2 → canOpenURL से check करो कि handle करने वाला app है
Step 3 → openURL(url) call करो
Step 4 → OS सही app चुनकर खोलता है
Step 5 → आपका app background में चला जाता है
Step 6 → fail हो तो fallback दिखाओ
```

---

## 🟡 Real World Example
**Swiggy** में delivery partner का "Call" बटन `tel:` से dialer खोलता है। **Zomato** में restaurant का "Directions" बटन Google Maps खोलता है (Android `geo:`, iOS `maps:`)। **Paytm** में "Privacy Policy" link in-app browser/Chrome में खुलता है। **Ola/Uber** रास्ता दिखाने के लिए Maps खोलते हैं।

## 🟡 Real Example Hindi mein
Swiggy में delivery partner को call करने का बटन `tel:` URL से dialer खोलता है। Zomato का Directions बटन Maps app खोल देता है। Paytm का privacy policy link browser में खुलता है।

---

## 💻 Code Example — Basic
```jsx
// LinkingBasic.jsx — call, web, mail खोलना
import React from 'react';                                    // React
import { View, Button, Linking, Alert } from 'react-native';  // core

export default function LinkingBasic() {                      // component
  const open = async (url) => {                               // helper: URL खोलो
    try {                                                     // error handling
      await Linking.openURL(url);                             // OS को URL दो
    } catch (e) {                                             // कोई app नहीं मिला / fail
      Alert.alert('Cannot open', url);                        // user को बताओ
    }                                                         // catch खत्म
  };                                                          // helper खत्म

  return (                                                    // UI
    <View style={{ flex: 1, justifyContent: 'center', padding: 24, gap: 12 }}>{/* container */}
      <Button title="Call" onPress={() => open('tel:+911234567890')} />{/* dialer खुलेगा */}
      <Button title="Email" onPress={() => open('mailto:help@example.com?subject=Help')} />{/* mail app */}
      <Button title="Website" onPress={() => open('https://reactnative.dev')} />{/* browser */}
    </View>
  );                                                          // return खत्म
}                                                             // component खत्म
```

## 💻 Code Example — Advanced
```jsx
// LinkingAdvanced.jsx — Maps (Platform), WhatsApp with fallback, settings, incoming URL listener
import React, { useEffect, useState } from 'react';           // hooks
import { View, Text, Pressable, Linking, Platform, Alert, StyleSheet } from 'react-native'; // core

// Platform के हिसाब से maps URL बनाओ
const mapsUrl = (lat, lng, label) =>
  Platform.select({                                           // OS चुनो
    ios: `maps:0,0?q=${encodeURIComponent(label)}@${lat},${lng}`,      // iOS Apple Maps
    default: `geo:0,0?q=${lat},${lng}(${encodeURIComponent(label)})`,  // Android geo: intent
  });                                                         // select खत्म

export default function LinkingAdvanced() {                   // component
  const [incoming, setIncoming] = useState(null);             // app खोलने वाला URL

  useEffect(() => {                                           // mount पर
    Linking.getInitialURL().then(setIncoming);                // cold start URL (deep link)
    const sub = Linking.addEventListener('url', ({ url }) => setIncoming(url)); // app खुला हो तब आया URL
    return () => sub.remove();                                // cleanup
  }, []);                                                     // एक बार

  const openMaps = () =>                                      // directions
    Linking.openURL(mapsUrl(12.9716, 77.5946, 'Meghana Foods'))  // Bengaluru example
      .catch(() => Linking.openURL('https://www.google.com/maps/search/?api=1&query=12.9716,77.5946')); // fallback web

  const openWhatsApp = async () => {                          // WhatsApp chat
    const app = 'whatsapp://send?phone=911234567890&text=Hello'; // app scheme
    const web = 'https://wa.me/911234567890?text=Hello';      // web fallback
    try {                                                     // error handling
      // iOS पर canOpenURL के लिए Info.plist LSApplicationQueriesSchemes में 'whatsapp' चाहिए
      const ok = await Linking.canOpenURL(app);               // installed है?
      await Linking.openURL(ok ? app : web);                  // हाँ तो app, वरना web
    } catch (e) {                                             // fail
      Alert.alert('Error', e.message);                        // बताओ
    }                                                         // catch खत्म
  };                                                          // function खत्म

  return (                                                    // UI
    <View style={s.c}>{/* container */}
      <Pressable style={s.b} onPress={openMaps}><Text style={s.t}>Directions</Text></Pressable>{/* maps */}
      <Pressable style={s.b} onPress={openWhatsApp}><Text style={s.t}>WhatsApp</Text></Pressable>{/* whatsapp */}
      <Pressable style={s.b} onPress={() => Linking.openSettings()}><Text style={s.t}>App Settings</Text></Pressable>{/* settings */}
      <Text>Incoming: {incoming ?? 'none'}</Text>{/* deep link दिखाओ */}
    </View>
  );                                                          // return खत्म
}                                                             // component खत्म

const s = StyleSheet.create({                                 // styles
  c: { flex: 1, justifyContent: 'center', padding: 24, gap: 12 }, // layout
  b: { backgroundColor: '#fc8019', padding: 14, borderRadius: 8 }, // button
  t: { color: '#fff', textAlign: 'center', fontWeight: '600' },    // text
});                                                           // खत्म
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `canOpenURL` for custom schemes | Android 11+ (API 30) पर `<queries>` AndroidManifest में चाहिए | `LSApplicationQueriesSchemes` Info.plist में चाहिए |
| `https://` / `tel:` / `mailto:` | `canOpenURL` में भी package visibility देखो | आम तौर पर बिना config के काम |
| Maps scheme | `geo:` | `maps:` (Apple Maps) |
| `tel:` on tablet/simulator | Dialer न हो तो fail | Simulator पर call नहीं होती |
| Settings | `Linking.openSettings()` app info | `Linking.openSettings()` app settings |
| Intent | `Linking.sendIntent()` (Android only) | नहीं है |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: app.json में config, expo-linking से scheme-aware URL
import * as Linking from 'expo-linking';                // npx expo install expo-linking
const url = Linking.createURL('orders/42');             // myapp://orders/42 (scheme app.json में "scheme": "myapp")
await Linking.openURL('tel:+911234567890');             // expo-linking भी openURL देता है
// iOS queries: app.json -> ios.infoPlist.LSApplicationQueriesSchemes: ["whatsapp"]
```
CLI way:
```jsx
// CLI: core Linking + native files खुद edit
import { Linking } from 'react-native';                 // core
await Linking.openURL('tel:+911234567890');             // वही call
// iOS: ios/App/Info.plist में LSApplicationQueriesSchemes array जोड़ो
// Android 11+: android/app/src/main/AndroidManifest.xml में <queries><intent>... जोड़ो
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: iOS पर `canOpenURL('whatsapp://')` बिना Info.plist entry के, हमेशा false।
✅ Correct: `LSApplicationQueriesSchemes` में scheme जोड़ो।

❌ Mistake 2: `tel:` में spaces या `+` के बिना country code।
✅ Correct: `tel:+911234567890` जैसा साफ़ format।

❌ Mistake 3: `openURL` पर error handling नहीं।
✅ Correct: `try/catch` और web fallback।

❌ Mistake 4: `addEventListener` का subscription remove न करना।
✅ Correct: `sub.remove()` cleanup में।

---

## 🧠 Tricky Interview Question
```jsx
const ok = await Linking.canOpenURL('whatsapp://send?text=Hi');
if (ok) Linking.openURL('whatsapp://send?text=Hi');
```
WhatsApp installed है फिर भी iOS पर `ok === false`। क्यों?

Answer: iOS custom scheme को `canOpenURL` से query करने के लिए Info.plist के `LSApplicationQueriesSchemes` में scheme declare करना होता है, privacy के कारण। Android 11+ पर भी package visibility (`<queries>`) चाहिए। Declare करने के बाद `true` आएगा। (Expo में app.json की `ios.infoPlist` से, और dev build rebuild करना पड़ता है।)

---

## ⚫ Interview Questions + Answers
Q1: Linking से क्या-क्या खोल सकते हैं?
A1: http(s), tel, mailto, sms, geo/maps, custom app schemes और app settings।

Q2: `getInitialURL` और `addEventListener('url')` में फर्क?
A2: पहला app बंद होने पर जिस URL से खुला उसे देता है, दूसरा app चल रहा हो तब आने वाले URL सुनता है।

Q3: `canOpenURL` क्यों fail होता है?
A3: iOS में Info.plist, Android 11+ में `<queries>` declaration नहीं है।

Q4: `Linking` और `expo-linking` में फर्क?
A4: `expo-linking` में `createURL`, `parse` जैसे helpers हैं जो scheme/Expo Go का ध्यान रखते हैं।

Q5: Web page app के अंदर खोलना हो तो?
A5: `expo-web-browser` (in-app browser) use करो; `Linking.openURL` बाहरी browser खोलता है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Call, email, maps, WhatsApp, external website
- Deep link पकड़ना
- Permission denied होने पर settings भेजना

❌ Avoid when:
- Web content app के अंदर दिखाना हो (WebView / expo-web-browser)
- Complex navigation deep linking, तब React Navigation की `linking` config
- User input से आया untrusted URL बिना validate किए

---

## 📊 Visual Diagram
```
 App --openURL(url)--> OS
                        |
    +--------+----------+----------+--------+
    |        |          |          |        |
  tel:     https:     mailto:    geo:/maps: whatsapp:
    |        |          |          |        |
 Dialer   Browser    Mail app    Maps    WhatsApp
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| URL scheme | Prefix that selects the app | URL का prefix जो app तय करता है |
| Deep link | URL that opens your app | App खोलने वाला link |
| canOpenURL | Check handler exists | Handler है या नहीं जाँचना |
| LSApplicationQueriesSchemes | iOS allow-list of schemes | iOS में allowed schemes की list |
| `<queries>` | Android 11+ package visibility | Android की visibility declaration |

---

## ⚡ 3-Line Summary
English: Linking opens URLs and other apps through schemes like tel, mailto and https.
Declare schemes for canOpenURL (Info.plist on iOS, queries on Android 11+).
Always catch errors and keep a web fallback.

Hindi: Linking tel, mailto, https जैसी schemes से URL और दूसरे apps खोलती है।
canOpenURL के लिए iOS में Info.plist और Android 11+ में queries declare करो।
हमेशा error पकड़ो और web fallback रखो।

---

## ➡️ Next Topic
**115. Haptics (Vibration)**, अब user को touch feedback देना सीखेंगे।
