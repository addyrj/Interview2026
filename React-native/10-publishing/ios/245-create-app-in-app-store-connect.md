# 245. Create App in App Store Connect
# हिंदी में: App Store Connect में App बनाना
# Platform: Android ❌ | iOS ✅ (Android का equivalent: Play Console → Create app)

> Targets: **Expo SDK 52 (check current docs — APIs change between SDKs)**.

---

## 🔵 Simple Definition (English)
Creating an app in App Store Connect means making an empty "app record" with a name, bundle ID, language and SKU. This record is where your builds, TestFlight and store listing will live.

## 🔵 सरल परिभाषा (Hindi)
App Store Connect में app बनाने का मतलब है एक खाली "app record" बनाना — जिसमें name, bundle ID, language और SKU होती है। आगे builds, TestFlight और store listing इसी record में रहेंगे।

---

## 🔴 Problem it Solves
- Apple को पता होना चाहिए कि कौन सा bundle ID आपका है, वरना upload reject होगा।
- App का नाम reserve करना (नाम unique होना चाहिए)।

## 🔴 यह क्यों बना? (Hindi)
Upload से पहले Apple को app की पहचान चाहिए। Record बनाने से नाम reserve होता है और builds सही app से जुड़ती हैं।

---

## 🟢 How it Works — Step by Step
1. **Apple Developer → Certificates, Identifiers & Profiles → Identifiers → +** → App IDs → App → Bundle ID (Explicit) डालो, capabilities (Push, Sign in with Apple) चुनो। (EAS पहली build पर यह अपने-आप कर देता है।)
2. ASC → **Apps → + → New App**।
3. Form भरो:
   - **Platforms:** iOS
   - **Name:** 2-30 chars, App Store पर unique
   - **Primary Language:** जैसे English (India)
   - **Bundle ID:** dropdown से (जो ऊपर register हुआ)
   - **SKU:** आपका internal unique code (जैसे `foodapp-ios-001`)
   - **User Access:** Full Access / Limited Access
4. **Create** दबाओ।
5. नया app "Prepare for Submission" status में दिखता है।
6. App page से **Apple ID** (numeric) note करो → `ascAppId` में काम आएगा।

```
Step 1 → Bundle ID register (या EAS auto)
Step 2 → ASC → Apps → + → New App
Step 3 → Name, Language, Bundle ID, SKU
Step 4 → Create → "Prepare for Submission"
Step 5 → Apple ID (ascAppId) note
```

## 🟢 कैसे काम करता है? (Hindi)
1. Bundle ID Apple Developer में register करो (या EAS करवा दे)।
2. ASC में New App पर क्लिक करो।
3. Name, language, bundle ID, SKU भरो।
4. Create करके numeric Apple ID नोट करो।

**Console screen (description):** Apps page पर ऊपर बाएँ नीला "+" बटन → dropdown "New App" → modal खुलता है। Modal में Platforms के checkboxes (iOS, macOS, tvOS), Name का text box, Primary Language dropdown, Bundle ID dropdown, SKU text box, और User Access के radio buttons। नीचे "Create" बटन। अगर Bundle ID dropdown खाली है तो मतलब ID register नहीं हुई।

---

## 🟡 Real World Example
**Zomato** अपने हर regional/brand app (जैसे Hyperpure, Blinkit-जैसे अलग apps) के लिए अलग bundle ID और ASC record रखता है। **Swiggy** नया "Instamart" जैसा app निकाले तो अलग record बनता है।

## 🟡 Real Example Hindi mein
Zomato अपने अलग-अलग apps के लिए अलग bundle ID और अलग ASC record रखता है। नया app निकालो तो नया record बनता है।

---

## 💻 Code Example — Basic
```json
// app.json — bundle ID जो ASC के New App form में चुना है
{
  "expo": {
    "name": "FoodApp",
    "slug": "foodapp",
    "ios": {
      "bundleIdentifier": "com.mycompany.foodapp"
    }
  }
}
```
```bash
# Bundle ID Expo से register कराने के लिए (credentials के साथ) पहली build
eas build -p ios --profile production
# ASC में app बनने के बाद, Apple ID (numeric) eas.json में डालो
```
## 💻 Code Example — Advanced
```json
// eas.json — submit config जिसमें ASC का numeric app ID है
{
  "submit": {
    "production": {
      "ios": {
        "ascAppId": "1234567890",
        "appleTeamId": "ABCDE12345",
        "sku": "foodapp-ios-001"
      }
    }
  }
}
```
```js
// validate-bundle-id.js — ASC form भरने से पहले naming check (Node)
const id = process.argv[2] || '';                     // CLI argument से bundle id
// reverse-domain: letters, digits, hyphen, dot; कम से कम 2 segments
const ok = /^[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$/.test(id);
if (!ok) {                                            // अगर pattern fail
  console.error('Invalid bundle id:', id);            // error दिखाओ
  process.exit(1);                                    // exit code 1
}
console.log('Bundle id looks valid:', id);            // success
```
`ascAppId`, `appleTeamId` और `sku` eas.json submit config के valid keys हैं (eas-cli docs)। ASC console steps not run.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Create | Play Console → Create app | ASC → Apps → + → New App |
| Identifier | package name (permanent) | Bundle ID (permanent) |
| Name rule | Play पर duplicate चल सकता है | App Store पर unique नाम चाहिए |
| Extra field | Free/Paid, Declarations | SKU, Primary Language |
| Fee | $25 once | $99/year membership |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# EAS पहली build पर Bundle ID Apple portal में register कर देता है
eas build -p ios
```
CLI way:
```bash
# Xcode: Signing & Capabilities → Automatically manage signing → Team चुनो
# Xcode खुद Bundle ID register करता है; फिर ASC में record बनाओ
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: ASC में App name पहले से लिया हुआ होना।
✅ Correct: कुछ unique नाम; बाद में subtitle से keyword जोड़ो।

❌ Mistake 2: Bundle ID typos (`com.mycompny...`)।
✅ Correct: app.json और ASC में copy-paste।

❌ Mistake 3: SKU को public समझना।
✅ Correct: SKU सिर्फ internal है; user को नहीं दिखती, बाद में बदलती नहीं।

❌ Mistake 4: Bundle ID dropdown खाली होने पर इंतज़ार करना।
✅ Correct: Developer portal में Identifier register करो।

---

## 🧠 Tricky Interview Question
"ASC में App बनाया पर Bundle ID dropdown में आपका ID नहीं दिख रहा, जबकि Xcode में प्रोजेक्ट चल रहा है।"

Answer: ID Apple Developer portal में registered नहीं है (Xcode simulator build पर register नहीं करता) या वह दूसरी team के under है। Certificates, Identifiers & Profiles → Identifiers में explicit App ID बनाओ, या एक बार `eas build -p ios` चलाओ जो इसे register कर देगा। फिर ASC refresh करो।

---

## ⚫ Interview Questions + Answers
Q1: Bundle ID बाद में बदल सकते हैं?
A1: नहीं, app बनने के बाद नहीं।

Q2: SKU क्या है?
A2: Internal unique string; reports में दिखती है।

Q3: App name की limit?
A3: 30 characters।

Q4: App ID (numeric) कहाँ मिलता है?
A4: App page → General → App Information → Apple ID।

Q5: Explicit और Wildcard App ID?
A5: Explicit = एक app; Wildcard = कई apps पर (push/IAP नहीं चलते)।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- पहली बार publish या नया app।

❌ Avoid when:
- सिर्फ TestFlight bypass के लिए test (ad-hoc में record ज़रूरी नहीं)।

---

## 📊 Visual Diagram
```
 Developer Portal            App Store Connect
 ┌──────────────────┐        ┌────────────────────────┐
 │ Identifier       │ ─────► │ New App                │
 │ com.co.foodapp   │ choose │ Name / Lang / SKU      │
 └──────────────────┘        └──────────┬─────────────┘
                                         ▼
                              App record + Apple ID (ascAppId)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| App record | Entry for your app in ASC | ASC में app की entry |
| SKU | Internal code | internal code |
| Apple ID (app) | Numeric app ID | app की numeric ID |
| Explicit App ID | ID for one app | एक app की ID |

---

## ⚡ 3-Line Summary
English: Register the bundle ID, then create a New App in ASC.
Fill name, language, bundle ID and SKU.
Note the numeric Apple ID for EAS Submit.

Hindi: Bundle ID register करो, फिर ASC में New App बनाओ।
Name, language, bundle ID और SKU भरो।
EAS Submit के लिए numeric Apple ID नोट करो।

---

## ➡️ Next Topic
**246. App Information Setup** — app record के general fields (category, age rating, etc.)।
