# 39. Alert Component
# हिंदी में: Alert (Native Popup Dialog)
# Platform: Android ✅ | iOS ✅ | Both ✅ (`Alert.prompt` सिर्फ iOS)

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs)। `Alert` एक API है (component नहीं), core RN में।

---

## 🔵 Simple Definition (English)
`Alert` shows a native dialog box with a title, a message and up to a few buttons. It is called as a function: `Alert.alert(title, message, buttons, options)`.

## 🔵 सरल परिभाषा (Hindi)
`Alert` एक native dialog box दिखाता है जिसमें title, message और कुछ buttons होते हैं। इसे function की तरह बुलाते हैं: `Alert.alert(title, message, buttons, options)`।

---

## 🔴 Problem it Solves
```
❌ User से "क्या आप पक्का हैं?" पूछने के लिए custom modal बनाना पड़ता
❌ Error/success संदेश जल्दी दिखाना हो
❌ OS-native look और behaviour (back button, accessibility) चाहिए
```

## 🔴 यह क्यों बना? (Hindi)
```
Delete, logout, payment-fail जैसे फैसलों पर तुरंत native confirmation चाहिए।
Alert कुछ लाइनों में यह दे देता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → import { Alert } from 'react-native'
Step 2 → Alert.alert('Title', 'Message')  → सिर्फ "OK" button
Step 3 → buttons array दो: [{ text, onPress, style }]
Step 4 → user button दबाता है → उस button का onPress चलता है, alert बंद
Step 5 → options: { cancelable: true, onDismiss } (Android: बाहर tap/back से बंद)
Step 6 → iOS पर Alert.prompt('title', 'msg', callback) से text input भी ले सकते हो
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Alert import करो
Step 2 → Alert.alert('Title', 'Message') → सिर्फ OK
Step 3 → buttons array दो
Step 4 → button दबाने पर उसका onPress चलता है
Step 5 → options में cancelable (Android) दो
Step 6 → iOS पर Alert.prompt से text input भी मिलता है
```

---

## 🟡 Real World Example
**Swiggy** में "Remove item from cart?", **Paytm** में "Payment failed - Retry/Cancel", **Zomato** में "Logout?" जैसे dialogs। **WhatsApp** में "Delete message?" भी यही pattern है।

## 🟡 Real Example Hindi mein
Zomato में Logout दबाओ तो "क्या आप logout करना चाहते हैं?" पूछता है, इसमें Cancel और Logout दो buttons होते हैं।

---

## 💻 Code Example — Basic
```jsx
// Basic: simple alert और confirm
import React from 'react';                                      // React
import { View, Button, Alert, StyleSheet } from 'react-native'; // UI + Alert

export default function Basic() {
  const showInfo = () => Alert.alert('Hello', 'Order placed!'); // सिर्फ OK

  const confirmLogout = () =>
    Alert.alert(
      'Logout',                                                  // title
      'क्या आप पक्का logout करना चाहते हैं?',                       // message
      [
        { text: 'Cancel', style: 'cancel' },                     // cancel button
        { text: 'Logout', style: 'destructive',                  // destructive = iOS पर लाल
          onPress: () => console.log('logged out') },            // action
      ],
    );

  return (
    <View style={styles.box}>
      <Button title="Info" onPress={showInfo} />{/* सरल alert */}
      <Button title="Logout" onPress={confirmLogout} />{/* confirm alert */}
    </View>
  );
}

const styles = StyleSheet.create({ box: { flex: 1, justifyContent: 'center', gap: 12, padding: 16 } });
```

## 💻 Code Example — Advanced
```jsx
// Advanced: Promise-based confirm helper + Android cancelable + iOS prompt fallback
import React from 'react';                                      // React
import { View, Button, Alert, Platform, StyleSheet } from 'react-native'; // UI

// Alert को Promise में लपेटो ताकि await कर सको
export const confirm = (title, message) =>
  new Promise((resolve) => {
    Alert.alert(
      title,
      message,
      [
        { text: 'Cancel', style: 'cancel', onPress: () => resolve(false) }, // false लौटाओ
        { text: 'Yes', onPress: () => resolve(true) },                      // true लौटाओ
      ],
      {
        cancelable: true,                                        // Android: बाहर tap/back से बंद
        onDismiss: () => resolve(false),                         // Android: dismiss = false
      },
    );
  });

export default function Advanced() {
  const deleteAddress = async () => {
    try {
      const ok = await confirm('Delete address', 'यह हटाने के बाद वापस नहीं आएगा'); // user से पूछो
      if (!ok) return;                                           // cancel पर रुको
      // await api.deleteAddress(id)  // असली API यहाँ
      Alert.alert('Done', 'Address हटा दिया');
    } catch (e) {
      Alert.alert('Error', String(e));                           // गड़बड़ी
    }
  };

  const askName = () => {
    if (Platform.OS === 'ios') {                                 // Alert.prompt सिर्फ iOS
      Alert.prompt('Name', 'अपना नाम लिखो', (text) => console.log(text));
    } else {
      Alert.alert('Not supported', 'Android पर custom modal/TextInput इस्तेमाल करो');
    }
  };

  return (
    <View style={styles.box}>
      <Button title="Delete address" onPress={deleteAddress} />
      <Button title="Ask name" onPress={askName} />
    </View>
  );
}

const styles = StyleSheet.create({ box: { flex: 1, justifyContent: 'center', gap: 12, padding: 16 } });
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Buttons की अधिकतम संख्या | 3 (positive/negative/neutral) | कई (vertical list) |
| `style: 'destructive'` | ❌ ignore | ✅ लाल text |
| `Alert.prompt` | ❌ उपलब्ध नहीं | ✅ text input वाला |
| बाहर tap से बंद | केवल `cancelable: true` पर | नहीं होता |
| Back button | `cancelable` पर बंद | लागू नहीं |
| Look | Material dialog | UIAlertController |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Core Alert — Expo Go में सीधा चलता है
import { Alert } from 'react-native';
Alert.alert('Hi', 'Expo से');
```
CLI way:
```jsx
// वही API; styling बदलनी हो तो library (जैसे react-native-modal) या custom Modal
import { Alert } from 'react-native';
Alert.alert('Hi', 'CLI से');
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Android पर 3 से ज़्यादा buttons देना
✅ Correct: अधिकतम 3, ज़्यादा के लिए custom `Modal` / bottom sheet।

❌ Mistake 2: `Alert.prompt` Android पर बुलाना
✅ Correct: `Platform.OS === 'ios'` जाँचो या custom modal बनाओ।

❌ Mistake 3: Web (`react-native-web`) पर `Alert.alert` का चुपचाप न चलना भूलना
✅ Correct: Web के लिए `window.confirm` या custom dialog fallback।

---

## 🧠 Tricky Interview Question
```jsx
Alert.alert('A');
console.log('B');
```
**Q: Output का क्रम क्या होगा?**

Answer: पहले `B` console में आएगा, क्योंकि `Alert.alert` blocking नहीं है; यह dialog दिखाने का अनुरोध भेजकर तुरंत लौट आता है। User के जवाब का इंतज़ार करना हो तो callback या Promise wrapper इस्तेमाल करो।

---

## ⚫ Interview Questions + Answers
Q1: Alert synchronous है?
A1: नहीं, यह non-blocking है; result buttons के `onPress` से मिलता है।

Q2: Alert को custom style (रंग, फ़ॉन्ट) कर सकते हैं?
A2: नहीं, native है। Custom look के लिए `Modal` या library।

Q3: `cancelable` क्या है?
A3: Android पर बाहर tap या back से dialog बंद होना।

Q4: Alert और Toast में फ़र्क?
A4: Alert user के जवाब का इंतज़ार करता है; Toast अपने आप गायब होता है और जवाब नहीं माँगता।

Q5: Await कैसे करें?
A5: Promise में लपेटो (ऊपर का `confirm` helper)।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Delete/logout/payment जैसी confirm चाहिए
- छोटा error संदेश

❌ Avoid when:
- बार-बार दिखने वाले संदेश (Toast/Snackbar)
- Form/rich UI वाला dialog (Modal)

---

## 📊 Visual Diagram
```
Alert.alert(title, msg, buttons)
        │
        ▼
 ┌─────────────────────┐
 │ Logout              │
 │ पक्का logout?        │
 │ [Cancel]  [Logout]  │──► onPress चलता है
 └─────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Alert | Native dialog | popup संदेश |
| cancelable | बाहर tap से बंद (Android) | रद्द किया जा सकने वाला |
| destructive | खतरनाक action का style (iOS) | विनाशकारी बटन |
| Alert.prompt | Text input वाला (iOS) | इनपुट वाला alert |
| Toast | अपने आप गायब संदेश | छोटा संदेश |

---

## ⚡ 3-Line Summary
English:
1. `Alert.alert` shows a native, non-blocking dialog.
2. Buttons are given as an array; Android max is 3 and `prompt` is iOS-only.
3. Wrap it in a Promise to `await` the answer.

Hindi:
1. `Alert.alert` native, non-blocking dialog दिखाता है।
2. Buttons array में दो; Android में अधिकतम 3, `prompt` सिर्फ iOS।
3. जवाब का इंतज़ार करने के लिए Promise में लपेटो।

---

## ➡️ Next Topic
**40. StatusBar Component** — ऊपर की बैटरी/समय वाली पट्टी का रंग और style।
