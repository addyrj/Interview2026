# 228. Certificates (Development + Distribution)
# हिंदी में: Certificates — Development और Distribution
# Platform: Android ❌ | iOS ✅

> Expo SDK 52+ (React Native 0.76+)। Expo SDK 52 (check current docs — APIs change between SDKs). Apple portal के नाम (जैसे "Apple Development", "Apple Distribution") बदल सकते हैं।

---

## 🔵 Simple Definition (English)
An iOS certificate is a digital ID issued by Apple. **Development certificate** signs builds you run on your test devices. **Distribution certificate** signs builds you send to TestFlight, the App Store, or Ad Hoc testers.

## 🔵 सरल परिभाषा (Hindi)
iOS certificate Apple का जारी किया digital ID है। **Development certificate** से आप अपने test devices पर चलने वाले builds sign करते हैं। **Distribution certificate** से TestFlight, App Store या Ad Hoc testers को भेजे builds sign होते हैं।

---

## 🔴 Problem it Solves
- Apple को पता चले कि build किस developer/team का है।
- Test builds और release builds अलग रहें (security)।

## 🔴 यह क्यों बना? (Hindi)
अगर कोई भी बिना पहचान के app बना सके तो malware फैलेगा। Certificate में public key Apple के साथ जुड़ी होती है और private key सिर्फ आपके Mac में — इसलिए सिर्फ आप ही sign कर सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Mac पर Keychain Access खोलो
Step 2 → Certificate Assistant → "Request a Certificate From a Certificate Authority"
Step 3 → Email + Common Name भरो, "Saved to disk" चुनो → CertificateSigningRequest.certSigningRequest बनेगी
Step 4 → developer.apple.com → Certificates, IDs & Profiles → Certificates → ➕
Step 5 → Type चुनो: "Apple Development" या "Apple Distribution"
Step 6 → CSR upload → Continue → Download (.cer)
Step 7 → .cer पर double-click → Keychain में install (private key से जुड़ जाएगा)
Step 8 → Keychain में cert + key चुनो → Export → .p12 (password के साथ) → backup/CI के लिए
```

## 🟢 कैसे काम करता है? (Hindi)
**Screens का वर्णन:** Certificates पेज पर नीले ➕ बटन से नया certificate। Type की list में radio buttons — "Apple Development" (test) और "Apple Distribution" (App Store + Ad Hoc)। अगला screen "Upload a Certificate Signing Request" जिसमें "Choose File" बटन। अंत में "Download" बटन।
Private key सिर्फ उसी Mac के Keychain में होती है जिसने CSR बनाई — इसीलिए .p12 export करना ज़रूरी है।
**ध्यान:** एक team के लिए Distribution certificates की संख्या सीमित होती है (आमतौर पर 3) — सीमा Apple की site पर देखें।

---

## 🟡 Real World Example
Swiggy की iOS team ने एक Distribution certificate बनाकर .p12 company vault में रखा और CI में use किया। जब पुराना certificate एक साल बाद expire होने वाला था, उन्होंने नया बनाया, नई profile generate की और CI secret बदल दिया — release बिना रुके चला।

## 🟡 Real Example Hindi mein
Paytm में नया developer आया। उसे अपना Development certificate बनाना पड़ा (हर developer का अपना), पर Distribution certificate team का shared रहता है और CI से use होता है।

---

## 💻 Code Example — Basic
```jsx
// Expo में certificate हाथ से बनाने की ज़रूरत नहीं:
// eas credentials                       // menu खुलेगा
//   → iOS → production → Distribution Certificate → "Set up a new one"
// EAS Apple login करके certificate बनाता और रखता है

// CSR terminal से बनाना (वैकल्पिक, Mac/Linux openssl):
// openssl genrsa -out ios.key 2048                         // private key
// openssl req -new -key ios.key -out ios.csr \             // CSR
//   -subj "/emailAddress=dev@example.com/CN=My Name/C=IN"
```

## 💻 Code Example — Advanced
```jsx
// .cer + key से .p12 बनाना (openssl) — CI में उपयोगी
// openssl x509 -inform DER -in distribution.cer -out distribution.pem   // .cer को PEM में
// openssl pkcs12 -export -inkey ios.key -in distribution.pem \          // .p12 बनाओ
//   -out distribution.p12 -password pass:CHANGE_ME                      // password बदलो

// GitHub Actions में base64 secret से keychain में import (shell):
// echo "$P12_BASE64" | base64 --decode > cert.p12                       // secret decode
// security create-keychain -p tmp ci.keychain                           // temp keychain
// security import cert.p12 -k ci.keychain -P "$P12_PASSWORD" -T /usr/bin/codesign // import
// security set-key-partition-list -S apple-tool:,apple: -s -k tmp ci.keychain       // codesign access

// Node में certificate expiry reminder logic:
function daysToExpiry(dateStr) { // expiry date string लो
  return Math.floor((new Date(dateStr) - Date.now()) / 86400000); // दिन गिनो
}
console.log(daysToExpiry('2027-03-01') < 30 ? 'Renew now' : 'Fine'); // 30 दिन से कम तो renew
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Dev vs Release identity | Debug keystore / Release keystore | Development / Distribution certificate |
| कौन देता है | आप खुद बनाते हैं | Apple जारी करता है |
| वैधता | ~25+ साल | ~1 साल |
| बैकअप file | .jks | .p12 |
| Per-developer? | नहीं | Dev cert हर developer का अलग |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// eas credentials   // EAS बनाता + रखता है, Keychain की ज़रूरत नहीं
```
CLI way:
```jsx
// Xcode → Settings → Accounts → Manage Certificates → ➕ → Apple Distribution
// Xcode CSR + private key खुद Keychain में बना देता है
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: दूसरे Mac पर .cer install करना पर private key न होना।
✅ Correct: .p12 export/import करो।

❌ Mistake 2: .p12 का password भूल जाना।
✅ Correct: password manager में रखो।

❌ Mistake 3: Certificate revoke करने से पहले सोचना नहीं।
✅ Correct: Revoke से उस cert पर बने profiles invalid होते हैं; पहले नया बनाकर profiles update करो।

---

## 🧠 Tricky Interview Question
Q: Certificate expire हो गया तो क्या App Store पर live app बंद हो जाएगा?

Answer: नहीं। Live app चलता रहता है। Expire होने से सिर्फ नए builds sign नहीं हो सकते। नया certificate बनाकर नई profile से अगला update भेजना होगा।

---

## ⚫ Interview Questions + Answers
Q1: Development और Distribution certificate में फर्क?
A1: Development test devices पर run करने के लिए; Distribution TestFlight/App Store/Ad Hoc के लिए।

Q2: .cer और .p12 में फर्क?
A2: .cer सिर्फ public certificate; .p12 में certificate + private key दोनों होते हैं।

Q3: CSR किसलिए?
A3: Apple को आपकी public key देने के लिए; certificate उसी से जारी होता है।

Q4: Key खो गई तो?
A4: पुराना certificate revoke करके नया CSR/cert बनाओ।

Q5: EAS क्यों आसान है?
A5: Certificates cloud में रखता है और अपने आप बनाता है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- हर signed iOS build पर।

❌ Avoid when:
- Simulator-only work।

---

## 📊 Visual Diagram
```
 Keychain (private key) ─► CSR ─► Apple Portal ─► .cer ─► install ─► .p12 backup
                                       │
                         ┌─────────────┴──────────────┐
                  Apple Development            Apple Distribution
                  (test devices)               (TestFlight/App Store)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CSR | Certificate Signing Request | certificate का अनुरोध |
| .cer | Public certificate | सार्वजनिक certificate |
| .p12 | Cert + private key bundle | cert + private key |
| Revoke | Cancel certificate | certificate रद्द करना |
| Keychain | Mac secure store | Mac का सुरक्षित भंडार |

---

## ⚡ 3-Line Summary
English: Development cert for testing, Distribution cert for release.
English: Private key lives only in your Keychain; export .p12.
English: EAS can create and store certificates for you.
Hindi: Testing के लिए Development, release के लिए Distribution।
Hindi: Private key सिर्फ आपके Keychain में; .p12 export करो।
Hindi: EAS certificates खुद बना और रख सकता है।

---

## ➡️ Next Topic
229. App ID + Bundle ID — app की unique पहचान।
