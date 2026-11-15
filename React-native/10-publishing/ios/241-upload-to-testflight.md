# 241. Upload to TestFlight
# हिंदी में: TestFlight पर Build Upload करना
# Platform: Android ❌ | iOS ✅ (Android का equivalent: Play Console पर AAB upload)

> Targets: **Expo SDK 52 (check current docs — APIs change between SDKs)**. `eas submit` के flags/prompts eas-cli version के साथ बदल सकते हैं।

---

## 🔵 Simple Definition (English)
Uploading to TestFlight means sending your signed `.ipa` to App Store Connect. You can do it with `eas submit`, Apple's Transporter app, or Xcode Organizer.

## 🔵 सरल परिभाषा (Hindi)
TestFlight पर upload का मतलब है अपनी signed `.ipa` file को App Store Connect भेजना। यह `eas submit`, Apple के Transporter app, या Xcode Organizer से किया जा सकता है।

---

## 🔴 Problem it Solves
- Build बनने के बाद उसे Apple तक पहुँचाने का एक reliable तरीका चाहिए।
- Manual Apple ID + password + 2FA हर बार झंझट है, CI में तो असंभव।
- Wrong bundle ID / duplicate build number जैसी errors upload पर ही पकड़नी हैं।

## 🔴 यह क्यों बना? (Hindi)
Apple ने तीन रास्ते दिए ताकि हर developer अपनी सुविधा से upload कर सके। App Store Connect API Key से CI/CD बिना password के चलता है।

---

## 🟢 How it Works — Step by Step
1. App Store Connect में app बना हो (topic 245) और bundle ID same हो।
2. **API Key** बनाओ: ASC → Users and Access → Integrations → App Store Connect API → "Generate API Key" (Access: App Manager)। `.p8` file एक ही बार download होती है।
3. `eas.json` में key path, key ID, issuer ID डालो।
4. `eas submit -p ios --latest` चलाओ।
5. Apple validate करता है → "Processing" → email "build has finished processing".
6. TestFlight tab में build दिखती है।

```
Step 1 → App record ASC में तैयार
Step 2 → API Key (.p8) generate
Step 3 → eas.json submit.production.ios में config
Step 4 → eas submit -p ios --latest
Step 5 → Apple validation + processing (10-30 min)
Step 6 → Build TestFlight में visible
```

## 🟢 कैसे काम करता है? (Hindi)
1. पहले ASC में app record बनाओ।
2. API Key generate करके `.p8` सुरक्षित रखो (दोबारा download नहीं होती)।
3. `eas.json` में config भरो।
4. `eas submit` चलाओ; upload के बाद processing की email आती है।

**Console screens (description):** ASC → *Users and Access* → ऊपर tab *Integrations* → *App Store Connect API* → नीला "+" बटन → Name और Access (App Manager) चुनो → Generate. Table में **Key ID** और ऊपर **Issuer ID** दिखता है। "Download API Key" बटन सिर्फ एक बार active रहता है।

---

## 🟡 Real World Example
**PhonePe-style** team का GitHub Action merge होने पर `eas build --auto-submit` चलाता है; API key GitHub Secrets में रखी है, इसलिए किसी की Apple ID/2FA की ज़रूरत नहीं। **Swiggy** QA को सुबह तक नई TestFlight build मिल जाती है।

## 🟡 Real Example Hindi mein
PhonePe जैसी team GitHub Actions में merge होते ही build और TestFlight upload चला देती है। API key secrets में रहती है, इसलिए किसी की Apple ID या 2FA नहीं चाहिए।

---

## 💻 Code Example — Basic
```json
// eas.json — API key के साथ submit config
{
  "cli": { "appVersionSource": "remote" },
  "build": { "production": { "autoIncrement": true } },
  "submit": {
    "production": {
      "ios": {
        "ascAppId": "1234567890",
        "ascApiKeyPath": "./secrets/AuthKey_ABC123DEFG.p8",
        "ascApiKeyIssuerId": "11111111-2222-3333-4444-555555555555",
        "ascApiKeyId": "ABC123DEFG"
      }
    }
  }
}
```
```bash
# latest finished build submit करो
eas submit --platform ios --latest
# या किसी specific build ID को
eas submit --platform ios --id <build-id>
```
नोट: `.p8` को कभी git में commit मत करो; `.gitignore` में डालो।

## 💻 Code Example — Advanced
```yaml
# .github/workflows/testflight.yml — CI से upload (syntax example, not run)
name: TestFlight
on:
  push:
    branches: [release]            # सिर्फ release branch पर trigger
jobs:
  ios:
    runs-on: ubuntu-latest         # EAS cloud build करेगा, Mac runner नहीं चाहिए
    steps:
      - uses: actions/checkout@v4  # code लाओ
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - uses: expo/expo-github-action@v8   # eas-cli setup
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }} # Expo access token
      - run: npm ci                         # dependencies
      - run: eas build -p ios --profile production --non-interactive --auto-submit
```
```bash
# Alternative: Transporter CLI (Mac पर) — API key से
xcrun altool --upload-app -f App.ipa -t ios \
  --apiKey ABC123DEFG --apiIssuer 11111111-2222-3333-4444-555555555555
```
(`altool` Apple ने notarization के लिए deprecate किया है, upload के लिए अभी भी चलता है; Apple का नया रास्ता Transporter/`iTMSTransporter` है — current docs देखो।)

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Upload tool | Play Console / `eas submit -p android` | `eas submit -p ios` / Transporter / Xcode |
| Auth | Google Service Account JSON | App Store Connect API Key (.p8) |
| First upload | पहली AAB manually Console में चाहिए | App record पहले ASC में बनाना ज़रूरी |
| Processing | कुछ मिनट | 10-30 min + email |
| Duplicate version | versionCode बढ़ाओ | buildNumber बढ़ाओ |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Expo: एक command
eas submit -p ios --latest
```
CLI way:
```bash
# Bare/Xcode: Archive → Organizer → Distribute App → App Store Connect → Upload
# या fastlane:
fastlane pilot upload --ipa App.ipa --api_key_path ./api_key.json
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: API key (.p8) खो देना / git में डाल देना।
✅ Correct: Password manager / CI secrets में रखो; खो जाए तो नई key बनाओ।

❌ Mistake 2: ASC में app record बनाए बिना submit करना।
✅ Correct: पहले topic 245 के अनुसार app बनाओ; `ascAppId` (numeric Apple ID) डालो।

❌ Mistake 3: Same `buildNumber` दोबारा।
✅ Correct: `autoIncrement: true`।

❌ Mistake 4: Key को "Developer" access देना → upload permission नहीं।
✅ Correct: "App Manager" या "Admin"।

---

## 🧠 Tricky Interview Question
"`eas submit` success बोला, पर TestFlight में 1 घंटे बाद भी build नहीं दिखी। कारण?"

Answer: Upload और processing अलग चीज़ें हैं। Apple बाद में validation करता है (icon alpha channel, missing Info.plist keys, invalid binary)। Fail होने पर Apple email भेजता है ("Invalid Binary" + reason) और build कभी list नहीं होती। Email (Apple ID inbox) और ASC Activity tab देखो।

---

## ⚫ Interview Questions + Answers
Q1: `.p8` file क्या है?
A1: App Store Connect API Key की private key; सिर्फ एक बार download होती है।

Q2: `ascAppId` क्या है?
A2: ASC में app का numeric Apple ID (App Information → General Information में)।

Q3: Upload के तीन तरीके?
A3: `eas submit`, Transporter app, Xcode Organizer (और fastlane)।

Q4: CI के लिए Apple ID password क्यों नहीं?
A4: 2FA की वजह से; API key बेहतर और secure है।

Q5: Processing में कितना टाइम?
A5: आमतौर पर 10-30 मिनट, कभी ज़्यादा।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- हर release पर repeatable upload चाहिए।
- CI/CD pipeline बनानी है।

❌ Avoid when:
- Build अभी testing के लायक नहीं (internal ad-hoc से पहले test करो)।
- Bundle ID/App record तैयार नहीं।

---

## 📊 Visual Diagram
```
 .ipa
  │
  ├── eas submit ────────┐
  ├── Transporter app ───┼──► App Store Connect ──► Validation ──► Processing ──► TestFlight
  └── Xcode Organizer ───┘            │ fail
                                      ▼
                              Email: "Invalid Binary"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Transporter | Apple's upload app | upload करने वाला Apple app |
| API Key (.p8) | Token credential for ASC | ASC की चाबी |
| Issuer ID | Team-level API identifier | team की ID |
| ascAppId | Numeric app ID | app की numeric ID |
| Processing | Apple's validation step | Apple की जाँच |

---

## ⚡ 3-Line Summary
English: Upload your IPA to App Store Connect with EAS Submit, Transporter or Xcode.
Use an App Store Connect API key for CI.
Processing happens after upload and may still fail.

Hindi: IPA को EAS Submit, Transporter या Xcode से App Store Connect पर भेजो।
CI के लिए API key इस्तेमाल करो।
Upload के बाद processing होती है और वह fail भी हो सकती है।

---

## ➡️ Next Topic
**242. Internal Testing on TestFlight** — upload हो गई, अब अपनी team को build बाँटते हैं।
