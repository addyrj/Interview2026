# 237. Build Release IPA (Expo)
# हिंदी में: Expo (EAS) से Release IPA बनाना
# Platform: Android ❌ | iOS ✅

> Expo SDK 52+ (React Native 0.76+)। Expo SDK 52 (check current docs — APIs change between SDKs). `eas.json` के keys और `eas-cli` version के options docs से verify करें; Apple developer account ($99) ज़रूरी है।

---

## 🔵 Simple Definition (English)
An **IPA** is the iOS app package you upload to App Store Connect. With Expo, **EAS Build** compiles your app on Apple-hardware cloud machines, signs it with your credentials and gives you an IPA — no Mac required.

## 🔵 सरल परिभाषा (Hindi)
**IPA** iOS app का package है जो App Store Connect पर upload होता है। Expo में **EAS Build** आपके app को Apple hardware वाले cloud machines पर compile करता है, आपके credentials से sign करता है और IPA देता है — Mac की ज़रूरत नहीं।

---

## 🔴 Problem it Solves
- Windows/Linux पर iOS build नहीं हो सकता।
- Local Xcode/signing की झंझट और "मेरी machine पर चलता है" समस्या।

## 🔴 यह क्यों बना? (Hindi)
EAS cloud build हर बार एक जैसे environment में build करता है, signing अपने आप संभालता है और `eas submit` से सीधे App Store Connect तक भेज देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → npm i -g eas-cli ; eas login
Step 2 → eas build:configure   (eas.json बनेगा)
Step 3 → app.json में bundleIdentifier, version, buildNumber जाँचो
Step 4 → eas build --platform ios --profile production
Step 5 → Apple ID + 2FA से login; EAS certificate + profile बनाने को पूछे → Yes
Step 6 → Build queue → cloud में compile → IPA तैयार (link/QR)
Step 7 → eas submit --platform ios --latest   (App Store Connect पर upload)
Step 8 → App Store Connect → TestFlight में build दिखेगा (processing 10-30 मिनट)
```

## 🟢 कैसे काम करता है? (Hindi)
1. आपका code EAS server पर upload होता है।
2. EAS macOS machine पर dependencies install, `pod install`, `xcodebuild archive` चलाता है।
3. Credentials (cert, profile) सुरक्षित server से लेकर sign करता है।
4. Output IPA store होता है; build page पर Download बटन।
**Terminal/Web screen:** Terminal में progress "Build queued... Build in progress... Build finished" और अंत में build details URL। expo.dev के build page पर Status, Platform, Profile, और "Install"/"Download" बटन।

---

## 🟡 Real World Example
एक छोटी Indian startup की टीम (सब Windows laptops) अपना food-delivery app इसी तरह publish करती है: `eas build --platform ios --profile production` फिर `eas submit` — बिना Mac के TestFlight पर build पहुँच जाता है।

## 🟡 Real Example Hindi mein
Swiggy-जैसे bigger teams CI (GitHub Actions) से `eas build --non-interactive --no-wait` चलाती हैं ताकि हर release tag पर अपने आप build बने।

---

## 💻 Code Example — Basic
```jsx
// eas.json
// {
//   "cli": { "version": ">= 5.0.0", "appVersionSource": "remote" }, // version EAS में track
//   "build": {
//     "development": { "developmentClient": true, "distribution": "internal" }, // dev build
//     "preview": { "distribution": "internal" },                    // testers के लिए (Ad Hoc)
//     "production": { "autoIncrement": true }                       // buildNumber अपने आप बढ़े
//   },
//   "submit": { "production": {} }                                   // submit config
// }

// Commands:
// eas build --platform ios --profile production    // release IPA
// eas submit --platform ios --latest               // App Store Connect पर भेजो
```

## 💻 Code Example — Advanced
```jsx
// GitHub Actions workflow (YAML) — release पर IPA बनाना और submit
// name: ios-release
// on:
//   push:
//     tags: ['v*']                                  # v1.0.0 जैसे tag पर चलेगा
// jobs:
//   build:
//     runs-on: ubuntu-latest                        # cloud build है, Mac runner नहीं चाहिए
//     steps:
//       - uses: actions/checkout@v4                 # code लाओ
//       - uses: actions/setup-node@v4               # Node setup
//         with: { node-version: 20 }
//       - uses: expo/expo-github-action@v8          # eas-cli setup
//         with:
//           eas-version: latest
//           token: ${{ secrets.EXPO_TOKEN }}        # Expo access token (secret)
//       - run: npm ci                               # dependencies
//       - run: eas build --platform ios --profile production --non-interactive   # build
//       - run: eas submit --platform ios --latest --non-interactive              # submit

// Non-interactive में पहले एक बार local पर `eas credentials` से credentials setup करना होता है।
// Submit के लिए App Store Connect API Key (topic 226) eas.json/credentials में दें।
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Output | .aab (store) / .apk (test) | .ipa |
| Signing | Keystore (EAS manage) | Cert + Profile (EAS manage) |
| Account | Play Console $25 | Apple Developer $99/yr |
| Test distribution | APK link | `distribution: internal` में device UDID register करना पड़ता है |
| Version field | versionCode | buildNumber |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// eas build --platform ios --profile production   // Mac के बिना
// eas submit --platform ios --latest
```
CLI way:
```jsx
// Mac + Xcode: Product → Archive → Distribute App (topic 238)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `buildNumber` वही रखना → App Store Connect duplicate reject करता है।
✅ Correct: `autoIncrement: true` या हाथ से बढ़ाओ।

❌ Mistake 2: Production profile को `distribution: internal` रखना।
✅ Correct: Store build के लिए default (store) distribution।

❌ Mistake 3: Apple 2FA code CI में माँगना।
✅ Correct: App Store Connect API key या पहले से credentials सेट।

---

## 🧠 Tricky Interview Question
Q: EAS build सफल रहा, पर TestFlight में build नहीं दिख रहा। क्यों?

Answer: Build बनना और upload अलग हैं — `eas submit` चलाना होगा। Upload के बाद Apple processing में 10-30 मिनट लगते हैं; export compliance या missing metadata सवाल हो तो build "Missing Compliance" दिखा सकता है।

---

## ⚫ Interview Questions + Answers
Q1: IPA क्या है?
A1: iOS app archive जो device/Store पर install होता है।

Q2: Mac के बिना IPA कैसे?
A2: EAS Build।

Q3: preview और production profile?
A3: preview internal testers (Ad Hoc), production App Store के लिए।

Q4: `eas submit` क्या करता है?
A4: IPA को App Store Connect पर upload करता है।

Q5: Credentials कहाँ रहते हैं?
A5: EAS server पर (remote) या local credentials.json।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Mac नहीं है, CI/CD चाहिए, Expo managed/prebuild project है।

❌ Avoid when:
- Native debugging/custom Xcode steps ज़रूरी हों (तब local build)।

---

## 📊 Visual Diagram
```
 Code ─► eas build (cloud Mac) ─► sign (EAS credentials) ─► IPA ─► eas submit ─► App Store Connect ─► TestFlight
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| IPA | iOS app package | iOS app पैकेज |
| EAS Build | Expo cloud build | Expo का cloud build |
| Profile | eas.json build config | build config |
| autoIncrement | Auto bump build number | build नंबर अपने आप बढ़ाना |
| Submit | Upload to store | store पर भेजना |

---

## ⚡ 3-Line Summary
English: EAS Build creates a signed IPA in the cloud.
English: eas submit uploads it to App Store Connect.
English: Bump buildNumber every time.
Hindi: EAS Build cloud में signed IPA बनाता है।
Hindi: eas submit उसे App Store Connect पर भेजता है।
Hindi: हर बार buildNumber बढ़ाओ।

---

## ➡️ Next Topic
238. Build Release IPA (CLI) — Xcode/xcodebuild से manual build।
