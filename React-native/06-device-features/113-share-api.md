# 113. Share API
# हिंदी में: Share API — Native Share Sheet खोलना
# Platform: Android ✅ | iOS ✅ | Both ✅

---

**Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs).** `Share` core React Native में built-in है, अलग install नहीं चाहिए। File share करने के लिए `expo-sharing` (SDK 52 में available) use होता है।

---

## 🔵 Simple Definition (English)
The **Share API** opens the phone's built-in share sheet so the user can send text, a link or a file to WhatsApp, Instagram, Gmail, SMS and other apps. You do not build any share UI yourself. The OS shows the list of apps.

## 🔵 सरल परिभाषा (Hindi)
**Share API** phone की built-in share sheet खोलती है, जिससे user text, link या file को WhatsApp, Instagram, Gmail, SMS जैसे apps में भेज सकता है। Share UI आपको खुद नहीं बनानी पड़ती, list OS दिखाता है।

---

## 🔴 Problem it Solves
```
BEFORE:
  Developer WhatsApp का deep link, Gmail का intent, SMS का URL
  सब अलग-अलग लिखता था.
  नया app (Telegram, Signal) आए तो code update करना पड़ता.

SHARE API:
  ✅ एक call -> OS सारे installed apps दिखाता है
  ✅ User अपना पसंदीदा app चुनता है
  ✅ Same code Android + iOS
  ✅ Referral / "Invite friends" growth feature आसान
```

## 🔴 यह क्यों बना? (Hindi)
पहले हर app (WhatsApp, Gmail, SMS) के लिए अलग link/intent लिखना पड़ता था। नया app आए तो code बदलना पड़ता। Share API एक ही call से OS की share sheet खोल देती है, user जो app चाहे चुन ले। Referral और invite जैसे growth features बहुत आसान हो जाते हैं।

---

## 🟢 How it Works — Step by Step
```
Step 1 → import { Share } from 'react-native'
Step 2 → Button press पर Share.share({ message, url?, title? }) call करो
Step 3 → OS native share sheet दिखाता है (Android: chooser, iOS: UIActivityViewController)
Step 4 → User app चुनता है या sheet बंद कर देता है
Step 5 → Promise resolve होता है: { action: Share.sharedAction | Share.dismissedAction }
Step 6 → Error आए तो catch में handle करो
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → react-native से Share import करो
Step 2 → Button दबाने पर Share.share({ message }) call करो
Step 3 → OS अपनी native share sheet दिखाता है
Step 4 → User कोई app चुनता है या sheet बंद कर देता है
Step 5 → Promise में action मिलता है (shared या dismissed)
Step 6 → Error को try/catch से संभालो
```

---

## 🟡 Real World Example
**Zomato** पर restaurant page का "Share" बटन: restaurant का नाम + link share होता है, "Check out Meghana Foods on Zomato https://..." WhatsApp पर चला जाता है। **Paytm** और **PhonePe** का "Refer & Earn" भी यही करता है: referral code वाला message share होता है। **Swiggy** order tracking link भी ऐसे ही दोस्त को भेजता है।

## 🟡 Real Example Hindi mein
Zomato में restaurant के Share बटन पर दबाते ही WhatsApp, Instagram आदि की list खुलती है और restaurant का link भेजा जाता है। PhonePe/Paytm का "Refer & Earn" भी referral code को इसी तरह share कराता है।

---

## 💻 Code Example — Basic
```jsx
// ShareBasic.jsx — सबसे simple share button
import React from 'react';                                   // React import
import { View, Button, Share, Alert } from 'react-native';   // core components + Share API

export default function ShareBasic() {                       // component शुरू
  const onShare = async () => {                              // async function क्योंकि Share.share Promise देता है
    try {                                                    // error पकड़ने के लिए try
      const result = await Share.share({                     // share sheet खोलो
        message: 'Zomato पर यह restaurant देखो!',              // भेजा जाने वाला text (दोनों OS पर काम करता है)
      });                                                    // call खत्म
      if (result.action === Share.sharedAction) {            // user ने share किया
        console.log('Shared via', result.activityType);      // iOS पर app का नाम मिल सकता है, Android पर अक्सर undefined
      } else if (result.action === Share.dismissedAction) {  // user ने बंद कर दिया
        console.log('Dismissed');                            // कुछ करने की ज़रूरत नहीं
      }                                                      // if खत्म
    } catch (e) {                                            // कोई error आया
      Alert.alert('Share failed', e.message);                // user को बताओ
    }                                                        // catch खत्म
  };                                                         // function खत्म

  return (                                                   // UI
    <View style={{ flex: 1, justifyContent: 'center', padding: 24 }}>{/* centered container */}
      <Button title="Share" onPress={onShare} />{/* button जो sheet खोलता है */}
    </View>
  );                                                         // return खत्म
}                                                            // component खत्म
```

## 💻 Code Example — Advanced
```jsx
// ShareAdvanced.jsx — referral link + Platform handling + file share (expo-sharing)
import React, { useCallback, useState } from 'react';        // hooks
import { View, Text, Pressable, Share, Platform, StyleSheet } from 'react-native'; // UI + Share
import * as Sharing from 'expo-sharing';                     // npx expo install expo-sharing (file share के लिए)
import * as FileSystem from 'expo-file-system';              // npx expo install expo-file-system

const REFERRAL_CODE = 'RAHUL100';                            // example code
const LINK = `https://example.com/invite?code=${REFERRAL_CODE}`; // invite link

export default function ShareAdvanced() {                    // component
  const [status, setStatus] = useState('');                  // UI में result दिखाने को

  const shareText = useCallback(async () => {                // text/link share
    try {                                                    // error handling
      const result = await Share.share(                      // पहला argument content
        Platform.select({                                    // OS के हिसाब से content
          ios: { message: 'App try करो, ₹100 पाओ!', url: LINK },   // iOS: url अलग field में चलता है
          default: { message: `App try करो, ₹100 पाओ! ${LINK}` },  // Android: url field ignore होता है, इसलिए message में डालो
        }),                                                  // select खत्म
        { dialogTitle: 'Invite friends', subject: 'Invite' } // दूसरा argument: Android dialogTitle, subject (email के लिए)
      );                                                     // call खत्म
      setStatus(result.action === Share.sharedAction ? 'Shared' : 'Cancelled'); // status दिखाओ
    } catch (e) {                                            // failure
      setStatus('Error: ' + e.message);                      // error दिखाओ
    }                                                        // catch खत्म
  }, []);                                                    // कोई dependency नहीं

  const shareFile = useCallback(async () => {               // local file share
    try {                                                    // error handling
      if (!(await Sharing.isAvailableAsync())) {             // कुछ platforms (web) पर available नहीं
        setStatus('Sharing not available');                  // बताओ
        return;                                              // बाहर निकलो
      }                                                      // if खत्म
      const uri = FileSystem.cacheDirectory + 'invoice.txt'; // cache में file path
      await FileSystem.writeAsStringAsync(uri, 'Invoice #1'); // file बनाओ
      await Sharing.shareAsync(uri, { mimeType: 'text/plain', dialogTitle: 'Share invoice' }); // file share
    } catch (e) {                                            // failure
      setStatus('Error: ' + e.message);                      // error दिखाओ
    }                                                        // catch खत्म
  }, []);                                                    // dependency नहीं

  return (                                                   // UI
    <View style={s.c}>{/* container */}
      <Pressable style={s.b} onPress={shareText}><Text style={s.t}>Share link</Text></Pressable>{/* text button */}
      <Pressable style={s.b} onPress={shareFile}><Text style={s.t}>Share file</Text></Pressable>{/* file button */}
      <Text>{status}</Text>{/* result */}
    </View>
  );                                                         // return खत्म
}                                                            // component खत्म

const s = StyleSheet.create({                                // styles
  c: { flex: 1, justifyContent: 'center', padding: 24, gap: 12 }, // layout
  b: { backgroundColor: '#e23744', padding: 14, borderRadius: 8 }, // button style
  t: { color: '#fff', textAlign: 'center', fontWeight: '600' },    // button text
});                                                          // styles खत्म
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Native UI | Chooser sheet | UIActivityViewController |
| `url` field | Ignore होता है (message में डालो) | Supported |
| `title` / `dialogTitle` | `dialogTitle` chooser का title | `subject` email subject बनता है |
| `result.activityType` | Usually undefined | Chosen activity का नाम मिलता है |
| `sharedAction` accuracy | Dismissed vs shared हमेशा सही नहीं पता चलता | ज़्यादा भरोसेमंद |
| File share | `expo-sharing` / FileProvider | `expo-sharing` / UIActivityViewController |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: Share (core) काम करता है, file के लिए expo-sharing
import { Share } from 'react-native';           // core, कोई install नहीं
import * as Sharing from 'expo-sharing';        // npx expo install expo-sharing
await Share.share({ message: 'Hello' });        // text share
await Sharing.shareAsync(fileUri);              // file share
```
CLI way:
```jsx
// CLI: text के लिए वही core Share; file के लिए react-native-share library
import { Share } from 'react-native';           // core Share
import RNShare from 'react-native-share';       // npm i react-native-share, फिर cd ios && pod install
await Share.share({ message: 'Hello' });        // text share
await RNShare.open({ url: 'file:///path/a.pdf' }); // file/social-specific share
```
Android पर CLI में FileProvider config खुद करना पड़ता है; Expo `expo-sharing` यह संभाल लेता है।

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Android पर `url` field में link डालना, link गायब हो जाता है।
✅ Correct: Link को `message` के अंदर भी डालो (या `Platform.select` use करो)।

❌ Mistake 2: `Share.share()` को `await`/`catch` के बिना call करना।
✅ Correct: `try/catch` लगाओ, error आने पर user को बताओ।

❌ Mistake 3: `Share.share` से local image/PDF file भेजने की कोशिश।
✅ Correct: File के लिए `expo-sharing` या `react-native-share` use करो।

❌ Mistake 4: मान लेना कि `sharedAction` का मतलब message पहुँच गया।
✅ Correct: इसका मतलब सिर्फ user ने sheet से कुछ चुना; delivery की गारंटी नहीं।

---

## 🧠 Tricky Interview Question
```jsx
const r = await Share.share({ message: 'Hi', url: 'https://x.com' });
console.log(r.action);
```
Android पर user ने WhatsApp चुना। Message में link आएगा क्या?

Answer: Android पर `url` ignore होता है, इसलिए सिर्फ "Hi" जाएगा। iOS पर link भी जाएगा। इसलिए cross-platform code में link को `message` में जोड़ना चाहिए। साथ ही Android पर `action` हमेशा `sharedAction` आ सकता है, चाहे user ने असल में भेजा हो या नहीं, इसे delivery proof न मानो।

---

## ⚫ Interview Questions + Answers
Q1: Share API क्या है?
A1: Core RN module जो OS की native share sheet खोलता है। Install नहीं चाहिए।

Q2: Share.share के parameters क्या हैं?
A2: पहला: `{ message, url (iOS), title (Android) }`। दूसरा: `{ dialogTitle, subject, excludedActivityTypes, tintColor }` जैसे options।

Q3: File कैसे share करोगे?
A3: Expo में `expo-sharing`, CLI में `react-native-share`। Core `Share` सिर्फ text/URL के लिए है।

Q4: User ने cancel किया यह कैसे पता चलेगा?
A4: `result.action === Share.dismissedAction`; iOS पर भरोसेमंद, Android पर सीमित।

Q5: Share sheet का style बदल सकते हैं?
A5: नहीं, यह OS की sheet है; सिर्फ कुछ options (iOS `tintColor`, Android `dialogTitle`) बदलते हैं।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Referral / invite / "share restaurant" जैसे features
- Text या link share करना हो
- Custom UI बनाए बिना सारे apps चाहिए

❌ Avoid when:
- किसी specific app (सिर्फ WhatsApp) में सीधे भेजना हो, तब Linking या react-native-share
- Share delivery tracking चाहिए
- Background में auto-send करना हो (यह allowed नहीं)

---

## 📊 Visual Diagram
```
 [Share button]
      |
      v
 Share.share({message, url})
      |
      v
 +-------------------------+
 |  OS Share Sheet         |
 |  WhatsApp  Gmail  SMS   |
 +-------------------------+
      |            |
  user चुनता     user cancel
      |            |
 sharedAction   dismissedAction
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Share sheet | OS UI listing apps to share with | Share करने वाले apps की list |
| sharedAction | User picked an app | User ने app चुना |
| dismissedAction | User closed sheet | User ने sheet बंद की |
| dialogTitle | Android chooser title | Android chooser का शीर्षक |
| expo-sharing | Expo library to share files | File share की library |

---

## ⚡ 3-Line Summary
English: Share API opens the native share sheet with one call.
Use `message` for text (and for links on Android), and `expo-sharing` for files.
The result tells you if the sheet was used, not if the message was delivered.

Hindi: Share API एक call में native share sheet खोलती है।
Text और Android पर link के लिए `message` use करो, file के लिए `expo-sharing`।
Result बताता है sheet use हुई या नहीं, message deliver हुआ या नहीं यह नहीं।

---

## ➡️ Next Topic
**114. Linking API (Open URLs, Maps, Phone)**, Share से अगला कदम: user को बाहर के apps (Maps, Dialer, Browser) में सीधे भेजना।
