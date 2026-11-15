---

# 214. Privacy Policy — Required
# हिंदी में: Privacy Policy — ज़रूरी
# Platform: Both ✅ (Android Play Store + iOS App Store dono me required)

> Expo SDK 53/54 (check current docs — APIs change between SDKs). Yeh legal/policy topic hai, legal advice nahi — final text ke liye lawyer se check karao. Google ke rules (Data safety, account deletion) badalte rehte hain.

---

## 🔵 Simple Definition (English)
A **privacy policy** is a public web page that explains what personal data your app collects, why, how it is stored/shared, and how users can delete it. Google Play requires a working **privacy policy URL** (HTTPS, public, not a PDF download) for apps that handle personal or sensitive data — which is almost every app.

## 🔵 सरल परिभाषा (Hindi)
**Privacy policy** एक public web page है जो बताता है कि आपकी app कौन-सा personal data लेती है, क्यों लेती है, कैसे store/share करती है, और user उसे कैसे delete करवा सकता है। Google Play को लगभग हर app के लिए एक चालू **privacy policy URL** (HTTPS, public) चाहिए।

---

## 🔴 Problem it Solves
- Apps secretly collected contacts, location, and device IDs.
- Laws demand transparency: GDPR (EU), CCPA (US), and India's **DPDP Act 2023**.
- Users and Google need a reference to compare with your **Data safety** form.

## 🔴 यह क्यों बना? (Hindi)
- Apps चुपके से contacts, location और device IDs ले लेती थीं।
- कानून पारदर्शिता माँगते हैं: GDPR (EU), CCPA (US), और भारत का **DPDP Act 2023**।
- Users और Google को आपके **Data safety** form से मिलाने के लिए एक reference चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Audit: app kaun-sa data leti hai? (email, phone, location, device ID,
         analytics, crash logs, ads SDK, payment)
Step 2 → Policy likho: kya data, kyun, kahan store, kis ke saath share, retention
Step 3 → User rights: access, correction, delete request ka tareeka + contact email
Step 4 → Publicly host karo (HTTPS) — apni website / GitHub Pages / Notion public page
Step 5 → Play Console → App content → Privacy policy → URL daalo
Step 6 → Store listing me bhi link; app ke andar Settings me bhi link
Step 7 → Data safety form se EXACT match karo
Step 8 → Account banane wali app ho to in-app account deletion + web deletion link
Step 9 → Naya SDK/data add ho to policy update
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Audit: app कौन-सा data लेती है? (email, phone, location, device ID,
         analytics, crash logs, ads SDK, payment)
Step 2 → Policy लिखो: कौन-सा data, क्यों, कहाँ store, किसके साथ share, कितने समय तक
Step 3 → User rights: access, correction, delete का तरीका + contact email
Step 4 → Publicly host करो (HTTPS) — अपनी website / GitHub Pages / public Notion page
Step 5 → Play Console → App content → Privacy policy → URL डालो
Step 6 → Store listing में भी link; app के अंदर Settings में भी link
Step 7 → Data safety form से बिल्कुल match करो
Step 8 → Account बनाने वाली app हो तो in-app account deletion + web deletion link
Step 9 → नया SDK/data जुड़े तो policy update करो
```

**Console screens (described in words):**
- **App content → Privacy policy:** Ek text field "Privacy policy URL" aur "Save" button. Galat/404 URL par laal error.
- **Store listing:** Neeche "Contact details" me email, website, aur privacy policy link.

---

## 🟡 Real World Example
**Paytm / PhonePe** jaisi apps payment aur KYC data lete hain, isliye unki policies bahut detailed hain — kaun-sa data (PAN, phone), kis partner bank ke saath share, retention period. **Zomato / Swiggy** location aur order history use karti hain; policy me likha hota hai ki location delivery ke liye li jaati hai aur user permission dekar band kar sakta hai.

## 🟡 Real Example Hindi mein
**Paytm / PhonePe** जैसी apps payment और KYC data लेती हैं, इसलिए उनकी policies बहुत विस्तृत होती हैं — कौन-सा data (PAN, phone), किस partner bank से share, कितने समय तक रखा। **Zomato / Swiggy** location और order history इस्तेमाल करती हैं; policy में लिखा होता है कि location delivery के लिए ली जाती है और user permission बंद कर सकता है।

---

## 💻 Code Example — Basic
App ke andar privacy policy ka link kholna (Expo + CLI dono me chalta hai, `Linking` RN core me hai).

```jsx
// PrivacyLink.jsx — Settings screen me use karo
import React from 'react';                         // React import
import { Linking, Pressable, Text, Alert } from 'react-native'; // RN core components

// Public HTTPS URL jo Play Console me bhi diya hai
const POLICY_URL = 'https://example.com/privacy';

// Link component
export default function PrivacyLink() {
  // press handler
  const open = async () => {
    try {
      // URL khul sakta hai ya nahi, check
      const ok = await Linking.canOpenURL(POLICY_URL);
      // khul sakta hai to open
      if (ok) await Linking.openURL(POLICY_URL);
      // nahi to user ko batao
      else Alert.alert('Link nahi khul raha');
    } catch (e) {
      // koi error aaye to alert
      Alert.alert('Error', String(e));
    }
  };
  // UI render
  return (
    <Pressable onPress={open} accessibilityRole="link">
      <Text style={{ color: '#2563eb' }}>Privacy Policy</Text>
    </Pressable>
  );
}
```

## 💻 Code Example — Advanced
Account deletion Play policy ke liye zaroori hai (account banane wali apps ke liye in-app + web option). Ek safe delete flow:

```jsx
// DeleteAccount.jsx — in-app account deletion with confirmation
import React, { useState } from 'react';                                    // React + state
import { Alert, Linking, Platform, Pressable, Text, View } from 'react-native'; // RN components

// Backend endpoint (apna daalo)
const API = 'https://api.example.com/account';
// Web par bhi deletion ka page (Play Console me ye URL batana padta hai)
const WEB_DELETE_URL = 'https://example.com/delete-account';

export default function DeleteAccount({ token, onDone }) {
  // loading flag
  const [busy, setBusy] = useState(false);

  // actual delete call
  const doDelete = async () => {
    setBusy(true);                                 // spinner on
    try {
      // server ko DELETE request
      const res = await fetch(API, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } });
      // non-2xx ho to error throw
      if (!res.ok) throw new Error('HTTP ' + res.status);
      // success: parent ko batao (logout + local data clear)
      onDone();
    } catch (e) {
      // fail hone par message (platform-specific text)
      Alert.alert('Delete failed', Platform.OS === 'android' ? 'Try again or use web link' : 'Please try again');
    } finally {
      setBusy(false);                              // spinner off
    }
  };

  // confirm dialog
  const confirm = () =>
    Alert.alert('Delete account?', 'This cannot be undone.', [
      { text: 'Cancel', style: 'cancel' },                 // cancel
      { text: 'Delete', style: 'destructive', onPress: doDelete }, // confirm
    ]);

  // UI
  return (
    <View>
      <Pressable disabled={busy} onPress={confirm}><Text>{busy ? 'Deleting...' : 'Delete my account'}</Text></Pressable>
      <Pressable onPress={() => Linking.openURL(WEB_DELETE_URL)}><Text>Request deletion on web</Text></Pressable>
    </View>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android (Google Play) | iOS (App Store) |
|---------|----------------------|-----------------|
| Policy URL | Required in Play Console | Required in App Store Connect |
| Data declaration | Data safety form | App Privacy "nutrition labels" |
| Account deletion | In-app + web link required (if account creation) | In-app deletion required |
| Tracking | Advertising ID declaration | App Tracking Transparency prompt |
| URL format | Public HTTPS, not PDF, not geo-blocked | Public URL |

---

## 🟠 Expo vs CLI Difference
Expo way:
```json
{
  "expo": {
    "privacy": "public",
    "android": { "package": "in.foodie.app" }
  }
}
```
(`expo.privacy` Expo-hosted project visibility ke liye hai — yeh store privacy policy NAHI hai. Policy URL sirf Play Console me jata hai.)

CLI way:
```jsx
// Bare RN: koi config nahi — policy URL Play Console me; app me Linking.openURL se link do
Linking.openURL('https://example.com/privacy'); // Settings screen me
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Policy URL 404 ya login-wall ke peeche.
✅ **Correct:** Public, HTTPS, bina login ke khulne wala page.

❌ **Mistake 2:** Policy me "hum data nahi lete" likhna jabki Firebase Analytics / ads SDK chal rahe hain.
✅ **Correct:** Har SDK ka data list karo; Data safety form se match karo.

❌ **Mistake 3:** Template copy karke company/contact details na badalna.
✅ **Correct:** Apna naam, address, contact email, effective date likho.

❌ **Mistake 4:** Account deletion ka rasta na dena.
✅ **Correct:** In-app delete + web request link (Play Console me web URL declare karo).

---

## 🧠 Tricky Interview Question
**Q: Aapki app me login nahi hai, koi analytics bhi nahi. Kya privacy policy phir bhi chahiye?**

**Answer:** Haan, practically chahiye. Ads SDK, crash reporting, ya device ID jaisi cheezein bhi data collection hain. Agar sach me kuch collect nahi hota, tab bhi Google generally privacy policy URL maangta hai (khaaskar jab sensitive permissions ya target audience me bachche ho). Safe rasta: ek chhoti policy likho jo clearly bataye "hum kuch collect nahi karte" aur Data safety form me "No data collected" declare karo — par tabhi jab har SDK check kar liya ho.

---

## ⚫ Interview Questions + Answers

**Q1: Privacy policy kahan add hoti hai?**
A1: Play Console → App content → Privacy policy; store listing ke contact section me bhi, aur app ke andar Settings me.

**Q2: Policy aur Data safety form me kya fark hai?**
A2: Policy = poora legal document. Data safety = Console me bhara hua structured summary. Dono me contradiction nahi hona chahiye.

**Q3: India me kaun-sa kanoon relevant hai?**
A3: Digital Personal Data Protection (DPDP) Act, 2023 — consent aur data principal rights. Detail ke liye legal advice lo.

**Q4: Free generator se policy bana sakte hain?**
A4: Haan starting point ke liye, par content ko apni app ke actual behaviour ke hisaab se edit karna padega.

**Q5: Account deletion requirement kya hai?**
A5: Agar app me user account bana sakta hai, to in-app delete option aur web par deletion request ka link dena hota hai (Google policy).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Kisi bhi personal/sensitive data, login, analytics, ads, location, camera, contacts ka use ho.

❌ Avoid when:
- (Skip nahi kar sakte.) Sirf content me "copy-paste" jhoot mat likho.

---

## 📊 Visual Diagram
```
 App code + SDKs ──► Data audit
                         │
                         ▼
               Privacy policy (public HTTPS)
                    │            │
                    ▼            ▼
        Play Console URL    In-app Settings link
                    │
                    ▼
         Data safety form (must match)
                    │
                    ▼
        Account deletion: in-app + web link
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Privacy policy | Public data-handling document | Data उपयोग का सार्वजनिक दस्तावेज़ |
| Data safety | Console form on data collection | Data collection का form |
| PII | Personally identifiable information | व्यक्तिगत पहचान वाला data |
| DPDP Act | India's data protection law | भारत का data सुरक्षा कानून |
| Retention | How long data is kept | Data कितने समय रखा जाएगा |

---

## ⚡ 3-Line Summary
**English:**
1. Host a public HTTPS privacy policy and add its URL in Play Console.
2. It must match your real SDK/data usage and the Data safety form.
3. Apps with accounts need in-app and web account-deletion options.

**Hindi:**
1. Public HTTPS privacy policy host करो और URL Play Console में डालो।
2. यह आपके असली SDK/data उपयोग और Data safety form से match होनी चाहिए।
3. Account वाली apps में in-app और web account-deletion विकल्प चाहिए।

---

## ➡️ Next Topic
**215. Store Listing (Title, Description, Screenshots)** — app की दुकान की शक्ल सजाना।
