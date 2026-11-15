# 253. Common Rejection Reasons (iOS)
# हिंदी में: iOS App Reject होने के आम कारण
# Platform: Android ❌ | iOS ✅

> Expo SDK 52+ examples (check current docs — APIs change between SDKs). Guideline numbers can be renumbered by Apple; verify on developer.apple.com/app-store/review/guidelines.

---

## 🔵 Simple Definition (English)
A rejection happens when Apple finds your app violates a guideline: it crashes, has bugs, is incomplete, collects data wrongly, uses the wrong payment method, or has misleading metadata. Knowing the top reasons lets you fix them before submitting.

## 🔵 सरल परिभाषा (Hindi)
Reject तब होता है जब Apple को लगता है कि आपका app किसी guideline को तोड़ रहा है: crash, incomplete features, गलत data collection, गलत payment method या भ्रामक metadata। आम कारण पहले से जान लो तो submit करने से पहले ही fix हो जाते हैं।

---

## 🔴 Problem it Solves
```
PROBLEM: Teams lose 2-7 days per rejection cycle.
SOLUTION: Pre-submission checklist built from the most frequent rejections.
```

## 🔴 यह क्यों बना? (Hindi)
हर reject का मतलब है कम से कम 1-3 दिन की देरी और launch plan खराब। Checklist से 80% rejections पहले ही पकड़ में आ जाते हैं।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Read the rejection email + Resolution Center message (guideline number given)
Step 2 → Reproduce the issue on a real device with the SAME build
Step 3 → Fix code or metadata (Metadata Rejected needs no new build)
Step 4 → Reply in Resolution Center explaining the fix (add video if useful)
Step 5 → Upload new build if required, resubmit
```

### Top rejection reasons
| Guideline | Reason | Typical fix |
|-----------|--------|-------------|
| 2.1 App Completeness | Crashes, placeholder content, broken links, no demo account | Test release build on real devices, add demo login |
| 2.3 Accurate Metadata | Screenshots/description do not match app | Use real screenshots, no competitor names in keywords |
| 3.1.1 In-App Purchase | Selling digital goods without Apple IAP | Use IAP for digital content (physical goods like Swiggy food orders can use other gateways) |
| 4.0 / 4.2 Design / Minimum Functionality | App is just a website wrapper | Add real native value (push, offline, native UI) |
| 4.8 Login Services | Offers third-party login (Google/Facebook) without an equivalent privacy-friendly option | Add Sign in with Apple (or another qualifying option) |
| 5.1.1 Data Collection | Missing privacy policy, no account deletion option | Add privacy URL, in-app account deletion |
| 5.1.2 Data Use / ATT | Tracking without App Tracking Transparency prompt | Show ATT prompt, fill privacy nutrition labels correctly |
| Permission strings | Missing/vague `NSCameraUsageDescription` etc. | Write clear purpose strings |
| 2.5.x Software Requirements | Private APIs, hot-patching that changes app purpose | Use public APIs only |
| Privacy manifest | Required-reason APIs / listed SDKs missing a privacy manifest | Update SDKs, add `PrivacyInfo.xcprivacy` (Expo: `ios.privacyManifests`) |

## 🟢 कैसे काम करता है? (Hindi)
1. Rejection mail में guideline number पढ़ो।
2. उसी build को real device पर चलाकर issue reproduce करो।
3. Code या metadata fix करो।
4. Resolution Center में reply करो — चाहें तो screen recording attach करो।
5. ज़रूरत हो तो नया build upload करके resubmit करो।

---

## 🟡 Real World Example
Paytm/PhonePe जैसे apps physical-world payments (UPI, bills) चलाते हैं — ये Apple IAP के बिना allowed हैं। लेकिन अगर कोई Hotstar-जैसा app digital subscription बेचे और बाहर के payment page का link दे, तो 3.1.1 में reject हो सकता है (region-specific exceptions exist; check current rules). Zomato-style apps को "Delete account" option देना पड़ा क्योंकि 5.1.1(v) में account deletion अनिवार्य है।

## 🟡 Real Example Hindi mein
Food delivery (Swiggy) और UPI payment (PhonePe) physical services हैं, इसलिए Apple IAP ज़रूरी नहीं। लेकिन digital subscription (जैसे OTT) के लिए Apple IAP चाहिए। जिस app में account बन सकता है, उसमें account delete करने का option भी देना पड़ता है।

---

## 💻 Code Example — Basic (permission strings in app.json)
```json
{
  "expo": {
    "name": "FoodApp",
    "ios": {
      "bundleIdentifier": "com.example.foodapp",
      "infoPlist": {
        "NSCameraUsageDescription": "We use the camera to scan QR codes at your table.",
        "NSLocationWhenInUseUsageDescription": "We use your location to show restaurants near you.",
        "NSPhotoLibraryUsageDescription": "Choose a profile photo from your library."
      }
    }
  }
}
```

## 💻 Code Example — Advanced (in-app account deletion, guideline 5.1.1(v))
```jsx
// DeleteAccount.jsx - minimal account deletion flow Apple expects
import React, { useState } from 'react';                         // React + state
import { View, Text, Pressable, Alert, ActivityIndicator, Platform } from 'react-native'; // UI parts

export default function DeleteAccount({ token, onDeleted }) {    // token: auth token, onDeleted: callback
  const [busy, setBusy] = useState(false);                       // loading flag

  const confirmAndDelete = () => {                               // user pressed Delete
    Alert.alert(                                                 // native confirm dialog
      'Delete account?',                                         // title
      'This permanently removes your data.',                     // message
      [
        { text: 'Cancel', style: 'cancel' },                     // do nothing
        {
          text: 'Delete',                                        // destructive action
          style: 'destructive',                                  // red on iOS
          onPress: async () => {                                 // run deletion
            setBusy(true);                                       // show spinner
            try {                                                // protect from network failure
              const res = await fetch('https://api.example.com/account', { // backend endpoint (example)
                method: 'DELETE',                                // delete request
                headers: { Authorization: `Bearer ${token}` },   // auth header
              });
              if (!res.ok) throw new Error('Server error');      // handle failure
              onDeleted();                                       // clear session, go to login
            } catch (e) {                                        // report the error
              Alert.alert('Could not delete', e.message);        // user feedback
            } finally {
              setBusy(false);                                    // hide spinner
            }
          },
        },
      ]
    );
  };

  return (
    <View style={{ padding: 20 }}>
      <Text>{Platform.OS === 'ios' ? 'Required by App Store policy' : 'Account settings'}</Text>
      {busy ? <ActivityIndicator /> : (
        <Pressable onPress={confirmAndDelete}><Text style={{ color: 'red' }}>Delete my account</Text></Pressable>
      )}
    </View>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Payments for digital goods | Google Play Billing required (with exceptions by region) | Apple IAP required (with exceptions by region/entitlements) |
| Permission text | Optional rationale in code | Mandatory Info.plist usage strings, else crash/reject |
| Third-party login rule | No equivalent requirement | Guideline 4.8 login-service requirement |
| Tracking | Ad ID / data safety form | ATT prompt + privacy nutrition labels |
| Web-wrapper apps | Usually accepted | 4.2 Minimum Functionality rejection common |
| Account deletion | Required via Data safety flow | Required in-app (5.1.1(v)) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```json
{ "expo": { "ios": { "infoPlist": { "NSCameraUsageDescription": "Scan QR codes" } } } }
```
CLI way:
```xml
<!-- ios/YourApp/Info.plist - edit by hand -->
<key>NSCameraUsageDescription</key>
<string>Scan QR codes</string>
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Testing only in dev mode / simulator.
✅ Correct: Test the production release build on a real iPhone (TestFlight).

❌ Mistake 2: Leaving "Lorem ipsum" or "Coming soon" screens.
✅ Correct: Hide unfinished features; Apple treats them as incomplete (2.1).

❌ Mistake 3: Mentioning Android / Google Play in the iOS app or screenshots.
✅ Correct: Remove other-platform references.

❌ Mistake 4: Asking permission on launch with no explanation.
✅ Correct: Ask in context (when the user taps "Scan") with a clear usage string.

---

## 🧠 Tricky Interview Question
You get rejected for 4.8 because you offer "Login with Google" only. Can you just add Facebook login?

Answer: No. The requirement is an equivalent login service that limits data collection to name/email, lets users hide email, and does not track for ads. Sign in with Apple satisfies it; Facebook does not. (Apple's wording was updated in 2024 — read the current 4.8 text.) Expo: `expo-apple-authentication`.

---

## ⚫ Interview Questions + Answers
Q1: Most common reason for rejection?
A1: 2.1 App Completeness — crashes, broken features, and missing demo accounts.

Q2: Why does a missing usage description matter?
A2: The OS terminates the app when it accesses a protected API without the key, and review flags it.

Q3: Can food-delivery apps use Razorpay?
A3: Yes. Physical goods/services are exempt from IAP. Digital goods inside the app are not.

Q4: What is a privacy manifest?
A4: A `PrivacyInfo.xcprivacy` file declaring data collection and required-reason API use; Apple requires it for certain SDKs.

Q5: Metadata rejected vs binary rejected?
A5: Metadata: edit text and resubmit, no new build. Binary: upload a new build.

---

## 🔷 When to Use + When Not to Use
✅ Use this checklist when:
- Before every first submission and every major release

❌ Avoid relying on it when:
- Guidelines changed — always re-read the current guidelines page

---

## 📊 Visual Diagram
```
 Rejected --> read guideline # --> reproduce on device
     |                                   |
     |                             fix code/metadata
     |                                   |
     +---- Resolution Center reply <-----+
                    |
              Resubmit build
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Guideline 2.1 | App completeness | App पूरा और stable हो |
| IAP | In-App Purchase | Apple के through payment |
| ATT | App Tracking Transparency | Tracking की permission |
| Sign in with Apple | Apple login option | Apple से login |
| Privacy manifest | Declares data/API use | Privacy की list |

---

## ⚡ 3-Line Summary
English: Most rejections come from crashes, missing demo accounts, wrong payments, and privacy gaps.
Add usage strings, account deletion, and Sign in with Apple when needed.
Read the guideline number, fix, and reply in Resolution Center.

Hindi: ज़्यादातर reject crash, demo account की कमी, गलत payment और privacy gaps से होते हैं।
Usage strings, account deletion और ज़रूरत पर Sign in with Apple जोड़ो।
Guideline number पढ़ो, fix करो और Resolution Center में reply दो।

---

## ➡️ Next Topic
**254. App Review Guidelines** — rejection के पीछे के असली rules को section-wise समझो।
