# 226. Apple Developer Account Setup ($99/year)
# हिंदी में: Apple Developer Account कैसे बनाएँ
# Platform: Android ❌ | iOS ✅

> Expo SDK 52+ (React Native 0.76+)। Expo SDK 52 (check current docs — APIs change between SDKs). फीस, enrollment screens और शर्तें Apple बदलता रहता है — developer.apple.com पर verify करें।

---

## 🔵 Simple Definition (English)
The Apple Developer Program is a paid membership (USD 99/year for individuals and organizations) that lets you sign apps, use TestFlight, and publish on the App Store. Without it you can only run apps on your own device for 7 days using a free Apple ID.

## 🔵 सरल परिभाषा (Hindi)
Apple Developer Program एक paid membership है (individual और organization दोनों के लिए $99/साल) जिससे आप app sign कर सकते हैं, TestFlight use कर सकते हैं और App Store पर publish कर सकते हैं। Free Apple ID से सिर्फ अपने device पर 7 दिन तक test कर सकते हैं।

---

## 🔴 Problem it Solves
- Apple चाहता है कि हर app का एक verified developer identity हो (security + trust)।
- बिना account के real users को app distribute नहीं हो सकता (iOS में sideload लगभग बंद है)।

## 🔴 यह क्यों बना? (Hindi)
iOS closed ecosystem है। Apple हर developer को verify करता है, इसलिए fake/malicious apps कम होते हैं। Account से आपको certificates, App IDs, TestFlight और App Store Connect मिलते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Apple ID बनाओ (appleid.apple.com), Two-Factor Auth ON करो
Step 2 → developer.apple.com/programs/enroll पर जाओ
Step 3 → Entity चुनो: Individual ya Organization
Step 4 → Identity verify (ID/legal name), payment ($99, कार्ड से)
Step 5 → Approval: Individual कभी minutes-48 घंटे, Organization में दिन-हफ्ते
Step 6 → Approve होने पर App Store Connect + Certificates, IDs & Profiles access
```

## 🟢 कैसे काम करता है? (Hindi)
**Individual:** आपके नाम से app store पर दिखेगा। Apple ID + 2FA + payment, और कभी-कभी identity verification।
**Organization:** company के नाम से। इसके लिए **D-U-N-S Number** (Dun & Bradstreet से free), legal entity proof और website domain चाहिए। भारत में Pvt Ltd / LLP आदि।
**Screens (शब्दों में):** Enroll पेज पर "Start Your Enrollment" बटन, फिर Apple ID login, फिर legal name/address form, फिर plan summary और "Purchase" बटन। Success पर email आता है "Welcome to the Apple Developer Program"।

---

## 🟡 Real World Example
Swiggy जैसी company अपना app **Organization** account से publish करती है ताकि App Store पर "Bundl Technologies" जैसा company नाम दिखे और कई team members (Admin, Developer, App Manager) को roles मिल सकें। एक freelance developer अपना छोटा app Individual account से डालता है — उसका निजी नाम seller के रूप में दिखता है।

## 🟡 Real Example Hindi mein
Zomato जैसी कंपनी Organization account रखती है; team में 20 developers हैं, सब अलग-अलग role से App Store Connect में काम करते हैं। Student/freelancer Individual account लेकर अपने नाम से app डालता है।

---

## 💻 Code Example — Basic
```jsx
// Account setup के बाद Expo project में Apple Team ID जोड़ना
// app.json का हिस्सा (comment रूप में):
// {
//   "expo": {
//     "ios": {
//       "bundleIdentifier": "com.mycompany.foodapp", // reverse-DNS, अगला topic 229 देखो
//       "buildNumber": "1"                            // हर upload पर बढ़ाओ
//     }
//   }
// }

// Terminal:
// eas login                        // Expo account में login
// eas credentials                  // Apple login करके credentials manage (Apple ID + 2FA माँगेगा)
```

## 💻 Code Example — Advanced
```jsx
// eas.json — submit के लिए App Store Connect API Key (2FA से बचने का बेहतर तरीका)
// {
//   "cli": { "version": ">= 5.0.0" },
//   "submit": {
//     "production": {
//       "ios": {
//         "ascAppId": "1234567890",          // App Store Connect में app का Apple ID (number)
//         "appleTeamId": "ABCDE12345"        // Developer account का Team ID
//       }
//     }
//   }
// }
// API key बनाने के steps (App Store Connect → Users and Access → Integrations → App Store Connect API):
//  1. "Generate API Key" → Name + Access: App Manager
//  2. .p8 file download (सिर्फ एक बार मिलती है!) + Key ID + Issuer ID note करो
//  3. EAS secrets / eas submit में इन्हें दो

// CI में Team ID check करने की छोटी JS script (Node):
const teamId = process.env.APPLE_TEAM_ID; // env से Team ID पढ़ो
if (!/^[A-Z0-9]{10}$/.test(teamId || '')) { // Team ID 10 अक्षर का होता है
  throw new Error('APPLE_TEAM_ID invalid'); // गलत हो तो fail करो
}
console.log('Team ID OK'); // सही है
```

---

## 📱 Android vs iOS Difference
| Feature | Android (Play Console) | iOS (Apple Developer) |
|---------|---------|-----|
| फीस | $25 एक बार | $99 हर साल |
| Verification | ID + (नए personal accounts पर testing requirement) | ID/D-U-N-S, कड़ा |
| Approval समय | कुछ घंटे-दिन | मिनट से हफ्ते |
| Renewal | नहीं | हर साल, वरना app store से हट जाता है |
| Free testing | APK sideload आसान | 7 दिन, सिर्फ अपना device |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo/EAS: Apple login एक बार, बाकी (certs, profiles) EAS अपने आप बनाता है
// eas build --platform ios   // Apple ID पूछेगा, credentials auto-generate
```
CLI way:
```jsx
// CLI: सब हाथ से — Xcode → Settings → Accounts → Apple ID जोड़ो
// Xcode में Team select करके "Automatically manage signing" चालू करो
// (details topic 232)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Organization के लिए D-U-N-S के बिना apply करना।
✅ Correct: पहले D-U-N-S number (free) लो — इसमें कई दिन लग सकते हैं।

❌ Mistake 2: Membership expire होने देना।
✅ Correct: Auto-renewal ON रखो; expire पर app store से हट सकता है।

❌ Mistake 3: .p8 API key खो देना।
✅ Correct: सुरक्षित secret manager में रखो; दोबारा download नहीं होती।

---

## 🧠 Tricky Interview Question
Q: क्या बिना $99 के real iPhone पर app चला सकते हैं?

Answer: हाँ, free Apple ID से Xcode के ज़रिए अपने device पर, पर profile 7 दिन में expire होती है, TestFlight/App Store नहीं मिलता और कई capabilities (Push, IAP आदि) बंद रहती हैं।

---

## ⚫ Interview Questions + Answers
Q1: Individual vs Organization में क्या फर्क?
A1: Individual में आपका नाम seller; Organization में company नाम, D-U-N-S चाहिए, team roles मिलते हैं।

Q2: Team ID क्या है?
A2: 10-character ID जो आपके developer team को पहचानती है; signing में लगती है।

Q3: Membership expire हो जाए तो?
A3: नए updates submit नहीं हो सकते और app store से हट सकता है।

Q4: Fee waiver?
A4: कुछ nonprofits/शिक्षण संस्थाओं के लिए Apple waiver देता है — Apple की site पर देखें।

Q5: Account roles?
A5: Account Holder, Admin, App Manager, Developer, Marketing आदि।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- App Store/TestFlight पर publish करना हो, push/IAP जैसे capabilities चाहिए।

❌ Avoid when:
- सिर्फ अपना prototype अपने device पर देखना है — free Apple ID काफी है।

---

## 📊 Visual Diagram
```
 Apple ID (2FA) ─► Enroll ─► Pay $99 ─► Approval
                                         │
        ┌────────────────────────────────┴─────────────┐
   App Store Connect                  Certificates, IDs & Profiles
   (app listing, TestFlight)          (signing assets)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Team ID | 10-char developer team id | team की पहचान |
| D-U-N-S | Company business ID | कंपनी की business ID |
| 2FA | Two-factor authentication | दो-स्तरीय सुरक्षा |
| App Store Connect | App management portal | app management पोर्टल |
| .p8 | API key file | API key फ़ाइल |

---

## ⚡ 3-Line Summary
English: Apple Developer Program costs $99/year and is required to publish on iOS.
English: Choose Individual or Organization (D-U-N-S needed).
English: Keep membership active and secure your API keys.
Hindi: iOS पर publish के लिए $99/साल का Apple Developer Program चाहिए।
Hindi: Individual या Organization चुनो (Org में D-U-N-S)।
Hindi: Membership active रखो और API key सुरक्षित रखो।

---

## ➡️ Next Topic
227. iOS App Signing — Complete Guide: certificate, App ID और profile का आपसी संबंध।
