# 232. Xcode Setup for Publishing
# हिंदी में: Publishing के लिए Xcode सेटअप
# Platform: Android ❌ | iOS ✅ (सिर्फ macOS पर)

> Expo SDK 52+ (React Native 0.76+)। Expo SDK 52 (check current docs — APIs change between SDKs). Xcode version SDK के अनुसार बदलती है; minimum Xcode requirement Expo/React Native docs में देखें।

---

## 🔵 Simple Definition (English)
Xcode is Apple's IDE. For publishing, you use it to open the iOS project, pick your Team, set Bundle ID and version, manage signing, and **Archive** the app so it can be uploaded to App Store Connect.

## 🔵 सरल परिभाषा (Hindi)
Xcode Apple का IDE है। Publishing में इससे iOS project खोलते हैं, Team चुनते हैं, Bundle ID और version सेट करते हैं, signing संभालते हैं और app को **Archive** करके App Store Connect पर upload करते हैं।

---

## 🔴 Problem it Solves
- iOS build सिर्फ Apple के toolchain से बन सकता है (Windows/Linux पर नहीं)।
- Signing, capabilities, schemes एक जगह दिखें।

## 🔴 यह क्यों बना? (Hindi)
iOS का compiler, simulator और signing tools Xcode के साथ आते हैं। बिना Xcode (या EAS cloud Mac) के IPA नहीं बन सकता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Mac App Store से Xcode install (बहुत बड़ा, ~10+ GB), एक बार खोलकर license accept
Step 2 → Command Line Tools: xcode-select --install
Step 3 → Xcode → Settings → Accounts → ➕ → Apple ID (developer account) जोड़ो
Step 4 → Project: Expo हो तो पहले `npx expo prebuild --platform ios` (ios/ folder बनेगा)
Step 5 → cd ios && pod install   (CocoaPods dependencies)
Step 6 → ios/<App>.xcworkspace खोलो  (.xcodeproj नहीं!)
Step 7 → Target → Signing & Capabilities → Team चुनो, ✔ Automatically manage signing
Step 8 → General → Identity: Display Name, Bundle Identifier, Version, Build
Step 9 → Device: "Any iOS Device (arm64)" चुनो (simulator नहीं)
Step 10 → Product → Archive → Organizer खुलेगा → Distribute App → App Store Connect → Upload
```

## 🟢 कैसे काम करता है? (Hindi)
**Screens का वर्णन:** बाईं तरफ project navigator में आपका project; बीच में target settings के tabs — General, Signing & Capabilities, Info, Build Settings। Signing tab में "Team" dropdown और "Automatically manage signing" checkbox; सफल होने पर नीचे "Provisioning Profile: Xcode Managed Profile" दिखता है। ऊपर toolbar में scheme और device selector। Archive के बाद **Organizer** window में आपके archives की list और दाईं तरफ "Distribute App" बटन।

---

## 🟡 Real World Example
Zomato की release engineer हर release पर Xcode में Version (जैसे 17.4.0) और Build number बढ़ाती है, Archive करती है और Organizer से App Store Connect पर upload करती है — या यही काम CI में `xcodebuild` से होता है।

## 🟡 Real Example Hindi mein
Paytm का developer नए Mac पर Xcode setup करता है: Xcode install → Apple ID जोड़ना → `pod install` → workspace खोलना → Team चुनना। 30 मिनट में release के लिए तैयार।

---

## 💻 Code Example — Basic
```jsx
// Terminal commands (Mac) — हर line का काम comment में
// xcode-select --install                 // Command Line Tools install
// sudo xcodebuild -license accept        // license मान लो
// xcodebuild -version                    // Xcode version जाँचो
// npx expo prebuild --platform ios       // Expo से ios/ folder बनाओ
// cd ios && pod install && cd ..         // CocoaPods dependencies install
// open ios/MyApp.xcworkspace             // workspace खोलो (नाम अपने app का)
```

## 💻 Code Example — Advanced
```jsx
// Command line से Archive + export (CI-friendly) — नाम अपने project के अनुसार बदलो
// xcodebuild -workspace ios/MyApp.xcworkspace \   // workspace
//   -scheme MyApp \                                // scheme
//   -configuration Release \                       // Release config
//   -destination 'generic/platform=iOS' \          // किसी भी real device के लिए
//   -archivePath build/MyApp.xcarchive \           // archive output
//   archive                                        // archive action

// ExportOptions.plist (App Store के लिए, XML):
// <?xml version="1.0" encoding="UTF-8"?>
// <plist version="1.0"><dict>
//   <key>method</key><string>app-store-connect</string>   // नए Xcode में; पुराने में "app-store"
//   <key>teamID</key><string>ABCDE12345</string>          // आपकी Team ID
// </dict></plist>

// xcodebuild -exportArchive -archivePath build/MyApp.xcarchive \
//   -exportOptionsPlist ExportOptions.plist -exportPath build/ipa   // .ipa बनाओ
// नोट: ExportOptions की method values Xcode version पर निर्भर हैं — `xcodebuild -help` / Apple docs देखें।
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| IDE | Android Studio (Win/Mac/Linux) | Xcode (सिर्फ Mac) |
| Build tool | Gradle | xcodebuild + CocoaPods |
| Output | .aab / .apk | .ipa (via Archive) |
| Signing setup | build.gradle + keystore | Signing & Capabilities + Team |
| Cloud alternative | EAS Build | EAS Build (Mac cloud) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Mac के बिना भी: eas build --platform ios --profile production
// Xcode की ज़रूरत नहीं (Apple के cloud Macs पर EAS build चलता है)
```
CLI way:
```jsx
// Mac + Xcode ज़रूरी
// cd ios && pod install && cd ..
// Xcode में Product → Archive
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `.xcodeproj` खोलना, `.xcworkspace` नहीं।
✅ Correct: Pods के साथ हमेशा `.xcworkspace` खोलो।

❌ Mistake 2: Simulator target पर Archive करना (option grey रहता है)।
✅ Correct: "Any iOS Device (arm64)" चुनो।

❌ Mistake 3: `expo prebuild` के बाद ios/ folder हाथ से बदलकर फिर prebuild चलाना।
✅ Correct: बदलाव config plugins में रखो, वरना `--clean` पर खो जाएँगे।

---

## 🧠 Tricky Interview Question
Q: Archive menu grey है, क्यों?

Answer: Selected destination simulator है, या scheme/Release config सही नहीं। "Any iOS Device (arm64)" चुनें और सही scheme। साथ ही signing errors भी Archive रोक सकती हैं।

---

## ⚫ Interview Questions + Answers
Q1: Windows पर iOS build कैसे?
A1: EAS Build (cloud Mac) या किराये का Mac/CI macOS runner।

Q2: Workspace vs Project?
A2: Workspace में Pods भी जुड़े होते हैं; RN के लिए हमेशा workspace।

Q3: Automatic signing क्या करता है?
A3: Xcode अपने आप cert, App ID, profile बनाता/अपडेट करता है।

Q4: Version और Build में फर्क?
A4: Version (CFBundleShortVersionString) user को दिखता है; Build (CFBundleVersion) हर upload पर अलग होना चाहिए।

Q5: Organizer क्या है?
A5: Archives देखने, validate और distribute करने की window।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Bare/prebuild project, native debugging, manual Archive।

❌ Avoid when:
- Mac नहीं है या सिर्फ cloud build चाहिए — EAS Build बेहतर।

---

## 📊 Visual Diagram
```
 Code ─► pod install ─► open .xcworkspace ─► Signing (Team) ─► Any iOS Device
        ─► Product ▸ Archive ─► Organizer ─► Distribute ─► App Store Connect
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Archive | Release build package | release build का पैकेज |
| Scheme | Build configuration set | build का सेट |
| Workspace | Project + Pods | project + Pods |
| Organizer | Archives manager | archives का प्रबंधक |
| Target | App to build | बनने वाला app |

---

## ⚡ 3-Line Summary
English: Install Xcode, add Apple ID, run pod install, open workspace.
English: Set Team, Bundle ID, version, then Archive on a real-device target.
English: Without a Mac, use EAS Build.
Hindi: Xcode install, Apple ID जोड़ो, pod install, workspace खोलो।
Hindi: Team, Bundle ID, version सेट करके real device target पर Archive।
Hindi: Mac न हो तो EAS Build।

---

## ➡️ Next Topic
233. Info.plist — iOS app की configuration फ़ाइल।
