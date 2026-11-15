# 244. App Store Connect — Complete Guide
# हिंदी में: App Store Connect — पूरी गाइड
# Platform: Android ❌ | iOS ✅ (Android का equivalent: Google Play Console)

> Targets: **Expo SDK 52 (check current docs — APIs change between SDKs)**. ASC का UI और नाम Apple बार-बार बदलता है; यहाँ दिए menu नाम का सार समझो, exact label docs में जाँचो।

---

## 🔵 Simple Definition (English)
**App Store Connect (ASC)** is Apple's web portal (appstoreconnect.apple.com) where you create your app record, upload builds, run TestFlight, fill the store listing, set price, and submit for review.

## 🔵 सरल परिभाषा (Hindi)
**App Store Connect (ASC)** Apple का web portal है जहाँ आप app record बनाते हैं, builds upload करते हैं, TestFlight चलाते हैं, store listing भरते हैं, price तय करते हैं और review के लिए submit करते हैं।

---

## 🔴 Problem it Solves
- App को App Store पर लाने के लिए एक central जगह चाहिए जहाँ metadata, build, pricing, legal सब हो।
- Team roles (कौन submit कर सकता है, कौन सिर्फ analytics देखे) manage करने हैं।

## 🔴 यह क्यों बना? (Hindi)
Apple का सारा distribution control एक जगह से होता है। Developers के लिए यही "Play Console" का iOS रूप है।

---

## 🟢 How it Works — Step by Step
1. Apple Developer Program ($99/year) में join करो।
2. appstoreconnect.apple.com पर login।
3. **Business** (या Agreements, Tax, and Banking) में Paid Apps Agreement + bank/tax info भरो (सिर्फ paid apps / IAP के लिए)।
4. **Apps → + → New App** (topic 245)।
5. App Information, Pricing, Privacy, Listing भरो (topics 246-250)।
6. Build attach करो और **Add for Review** (topic 251)।
7. Approve होने पर release।

```
Step 1 → Developer Program join
Step 2 → ASC login
Step 3 → Agreements/Tax/Banking (paid apps)
Step 4 → New App बनाओ
Step 5 → Info + Pricing + Privacy + Listing
Step 6 → Build attach + Submit
Step 7 → Review → Release
```

## 🟢 कैसे काम करता है? (Hindi)
1. Developer account लो और ASC में login करो।
2. Paid app हो तो bank/tax भरो।
3. New App बनाकर सारी जानकारी भरो।
4. Build attach करके review में भेजो।

**Console screens (description):**
- **Home:** ऊपर cards: *Apps, Analytics, Sales and Trends, Payments and Financial Reports, Users and Access*.
- **Apps list:** हर app का icon + नाम + status (Prepare for Submission / Waiting for Review / Ready for Sale).
- **App page:** left sidebar में sections: *App Store* (iOS App → version), *General* (App Information, Pricing and Availability, App Privacy), *TestFlight*, *Xcode Cloud*.
- **Version page:** screenshots, Promotional Text, Description, Keywords, Support URL, Build, App Review Information, Version Release।

---

## 🟡 Real World Example
**Swiggy** का product team ASC से ही देखता है कि नया version "Waiting for Review" है या "In Review"। **Paytm** के finance लोग *Sales and Trends/Payments* देखते हैं; developers सिर्फ App Manager role रखते हैं।

## 🟡 Real Example Hindi mein
Swiggy की team ASC में version का status देखती है। Paytm के finance लोग Payments section देखते हैं और developers को सिर्फ App Manager role मिलता है।

---

## 💻 Code Example — Basic
```json
// app.json — ASC के fields से match होने वाले values
{
  "expo": {
    "name": "FoodApp",                       // Home screen पर नाम (ASC में app name अलग भी हो सकता है)
    "version": "1.0.0",                      // ASC का "Version" (CFBundleShortVersionString)
    "ios": {
      "bundleIdentifier": "com.mycompany.foodapp",  // ASC के Bundle ID से EXACT same
      "buildNumber": "1"                     // हर upload पर unique (CFBundleVersion)
    }
  }
}
```
```bash
# Build बनाओ और ASC पर भेजो
eas build -p ios --profile production --auto-submit
```
JSON में comments allowed नहीं — ऊपर `//` सिर्फ समझाने के लिए हैं; असली file में हटाओ।

## 💻 Code Example — Advanced
```js
// check-asc-ready.js — release से पहले config sanity check (Node script)
const fs = require('fs');                          // file read के लिए

const cfg = JSON.parse(fs.readFileSync('app.json', 'utf8')).expo; // config पढ़ो
const errors = [];                                  // errors list

// bundle ID जरूर हो और valid pattern हो
if (!cfg.ios?.bundleIdentifier) errors.push('ios.bundleIdentifier missing');
else if (!/^[A-Za-z0-9.-]+$/.test(cfg.ios.bundleIdentifier)) errors.push('bad bundle id');

// version semver जैसा हो
if (!/^\d+\.\d+\.\d+$/.test(cfg.version || '')) errors.push('version must be x.y.z');

// export compliance key set हो
if (cfg.ios?.infoPlist?.ITSAppUsesNonExemptEncryption === undefined)
  errors.push('ITSAppUsesNonExemptEncryption not set (export compliance prompt aayega)');

// result print करो
if (errors.length) { console.error('NOT READY:\n- ' + errors.join('\n- ')); process.exit(1); }
console.log('Config looks ready for App Store Connect');
```
(Node में चलने लायक logic; native/ASC steps not run.)

---

## 📱 Android vs iOS Difference
| Feature | Android (Play Console) | iOS (App Store Connect) |
|---------|---------|-----|
| Fee | $25 one-time | $99/year |
| Review time | घंटे से कुछ दिन | आमतौर पर 24-48 घंटे |
| Identifier | applicationId (package) | Bundle ID |
| Version fields | versionName/versionCode | Version / Build |
| Testing | Internal/Closed/Open | TestFlight |
| Staged rollout | % rollout | Phased release (7 दिन) |
| Policy forms | Data safety | App Privacy "nutrition labels" |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# eas submit ASC पर upload कर देता है; metadata चाहिए तो eas metadata (आज भी preview/changing feature — docs देखो)
eas submit -p ios --latest
```
CLI way:
```bash
# fastlane deliver से metadata+screenshots push (bare या Expo दोनों में)
fastlane deliver --ipa App.ipa --submit_for_review false
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Bundle ID बाद में बदलना।
✅ Correct: Bundle ID app बनाते समय सोचकर चुनो — बाद में नहीं बदलता।

❌ Mistake 2: Account Holder की जगह हर किसी को Admin बनाना।
✅ Correct: Least privilege roles दो।

❌ Mistake 3: Paid Apps Agreement न भरना।
✅ Correct: Paid app/IAP से पहले agreements + tax + bank पूरा।

❌ Mistake 4: Production में लगातार metadata फिर से लिखना, backup के बिना।
✅ Correct: Metadata `fastlane deliver` या docs में version-control करो।

---

## 🧠 Tricky Interview Question
"ASC में app status 'Prepare for Submission' है, build upload भी हो गई, पर 'Add for Review' बटन disabled है। क्यों?"

Answer: कोई required field बाकी है: screenshots, description, privacy policy URL, App Privacy answers, age rating, price tier/availability, या build select नहीं हुई। ASC पर लाल warning/"Missing" badge वाले सेक्शन देखो।

---

## ⚫ Interview Questions + Answers
Q1: ASC क्या है?
A1: Apple का portal जिसमें app listing, builds, TestFlight, pricing, review होता है।

Q2: Bundle ID और SKU में फर्क?
A2: Bundle ID app की unique technical identity; SKU सिर्फ आपका internal reference (user को नहीं दिखता)।

Q3: Roles कौन से हैं?
A3: Account Holder, Admin, App Manager, Developer, Marketing, Sales, Customer Support, Finance etc.

Q4: ASC API key कहाँ बनती है?
A4: Users and Access → Integrations।

Q5: Version और Build में फर्क?
A5: Version = users को दिखने वाला (1.2.0); Build = हर upload का counter (42)।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- App Store पर publish, TestFlight, pricing, analytics।

❌ Avoid when:
- सिर्फ internal enterprise distribution (Apple Business Manager/Enterprise program अलग है)।

---

## 📊 Visual Diagram
```
 App Store Connect
 ├── Apps ── FoodApp
 │     ├── App Store ── iOS App ── 1.0.0 (version page)
 │     ├── General ── App Information | Pricing & Availability | App Privacy
 │     └── TestFlight ── Internal | External
 ├── Analytics
 ├── Sales & Trends / Payments
 └── Users and Access ── Roles | Integrations (API Keys)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ASC | App Store Connect | Apple का developer portal |
| Bundle ID | Unique app identifier | app की unique ID |
| SKU | Internal app reference | आपका internal code |
| Version / Build | Public / internal number | public / internal number |
| Phased release | Gradual rollout | धीरे-धीरे rollout |

---

## ⚡ 3-Line Summary
English: ASC is Apple's portal to manage apps, builds, testers and releases.
Fill info, price, privacy and listing, then attach a build.
Submit for review when every section is complete.

Hindi: ASC Apple का portal है जहाँ apps, builds, testers और releases manage होते हैं।
Info, price, privacy और listing भरकर build attach करो।
सब सेक्शन पूरे होने पर review के लिए submit करो।

---

## ➡️ Next Topic
**245. Create App in App Store Connect** — सबसे पहला step: app record बनाना।
