# 268. Automated Screenshots
# हिंदी में: Store Screenshots अपने-आप बनाना
# Platform: Android ✅ | iOS ✅ | Both ✅
# Expo SDK 54 (React Native 0.81) — check current docs — APIs change between SDKs

---

## 🔵 Simple Definition (English)
**Automated screenshots** means a script launches your app on simulators/emulators, navigates to key screens, and saves store-ready images in every device size and language — instead of a designer taking them by hand. Tools: **Maestro** (cross-platform, simplest for RN), **Fastlane snapshot** (iOS), **Fastlane screengrab** (Android), **Detox** (E2E with screenshots).

## 🔵 सरल परिभाषा (Hindi)
**Automated screenshots** में एक script simulator/emulator पर app खोलती है, ज़रूरी screens पर जाती है और हर device size व language में store-ready images सेव करती है — हाथ से नहीं। Tools: **Maestro** (RN के लिए सबसे आसान), **Fastlane snapshot** (iOS), **screengrab** (Android), **Detox**।

---

## 🔴 Problem it Solves
```
BEFORE:
❌ App Store needs 6.9", 6.5", 12.9" iPad... each size = manual shots
❌ 5 languages x 6 screens x 4 devices = 120 screenshots by hand
❌ UI changes → all screenshots outdated → redo everything
❌ Store rejection: "screenshots do not match the app"
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
❌ App Store को हर device size के screenshots चाहिए
❌ 5 भाषाएँ x 6 screens x 4 devices = 120 screenshots हाथ से
❌ UI बदला → सारे screenshots पुराने
❌ Store reject: "screenshots app से match नहीं करते"
Automation: एक command में सब regenerate।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build a debug/release app and install on simulator / emulator
Step 2 → Write a flow (YAML for Maestro or Ruby/Swift for Fastlane)
         that taps through the app
Step 3 → At each key screen call takeScreenshot (Maestro)
         or snapshot("01_Home") (Fastlane snapshot)
Step 4 → Run the flow for each device + language combo
Step 5 → Output PNGs go to a folder (e.g. fastlane/screenshots)
Step 6 → `deliver` / `supply` uploads them to the stores (optional)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → App build करके simulator / emulator पर install
Step 2 → Flow लिखो (Maestro YAML या Fastlane) जो app में tap करे
Step 3 → हर key screen पर takeScreenshot / snapshot("01_Home")
Step 4 → हर device + language के लिए चलाओ
Step 5 → PNG files folder में आ जाती हैं
Step 6 → `deliver` / `supply` से store पर upload (optional)
```

---

## 🟡 Real World Example
**Zomato**-style food app: flow = open app → pick city → open restaurant → add dish → open cart. Screenshots in English, Hindi, Tamil for 3 phone sizes. Marketing then frames them (device bezels + captions) with `frameit`. Each release regenerates all 27 images in 20 minutes.

## 🟡 Real Example Hindi mein
**Zomato** जैसे app का flow: app खोलो → शहर चुनो → restaurant खोलो → dish add करो → cart। English, Hindi, Tamil में 3 phone sizes के screenshots। Marketing `frameit` से device frame और captions लगाती है। हर release पर 27 images 20 मिनट में फिर बन जाती हैं।

---

## 💻 Code Example — Basic

Maestro flow `.maestro/screenshots.yaml` (Maestro is a separate CLI; install per maestro.mobile.dev docs):
```yaml
# appId = Android package / iOS bundle id
appId: com.example.zomatoclone
---
# Start fresh: clear app data and launch
- launchApp:
    clearState: true
# Wait for home to show
- assertVisible: "Restaurants near you"
# Save screenshot as 01-home.png
- takeScreenshot: 01-home
# Tap on first restaurant card
- tapOn: "Pizza Hut"
- assertVisible: "Add to cart"
- takeScreenshot: 02-menu
# Add item and open cart
- tapOn: "Add to cart"
- tapOn:
    id: "cart-button"       # matches testID in RN
- takeScreenshot: 03-cart
```
RN side — give elements a `testID` so flows can find them:
```jsx
import React from 'react';
import { Pressable, Text } from 'react-native';

// testID becomes accessibility id on Android (resource-id) and iOS
export default function CartButton({ onPress }) {
  return (
    // Pressable: tappable area
    <Pressable testID="cart-button" onPress={onPress}>
      {/* Label users and flow can see */}
      <Text>Cart</Text>
    </Pressable>
  );
}
```
Run: `maestro test .maestro/screenshots.yaml`

## 💻 Code Example — Advanced

Fastlane multi-device + multi-language. `ios/fastlane/Snapfile`:
```ruby
# Devices to capture (must exist in Xcode simulators)
devices([
  "iPhone 15 Pro Max",
  "iPhone 8 Plus",
  "iPad Pro (12.9-inch) (6th generation)"
])
# Languages (use store locale codes)
languages(["en-US", "hi"])
# Xcode scheme containing UI tests
scheme("MyAppUITests")
# Where PNGs are saved
output_directory("./fastlane/screenshots")
# Remove old files first
clear_previous_screenshots(true)
```
Android `android/fastlane/Fastfile` lane using `screengrab`:
```ruby
lane :screenshots do
  # Build debug app + androidTest APK that contains Espresso/UI Automator tests
  gradle(task: "assembleDebug assembleAndroidTest")
  # Run tests on connected emulator and pull PNGs
  capture_android_screenshots(
    locales: ["en-US", "hi-IN"],
    clear_previous_screenshots: true
  )
  # Upload to Play (images only)
  upload_to_play_store(skip_upload_apk: true, skip_upload_aab: true,
                       skip_upload_metadata: true)
end
```
Note: Fastlane snapshot needs native XCUITest targets, so it is practical only for bare RN. For Expo/managed apps Maestro is far simpler. CI use: run Maestro on a macOS runner with an emulator/simulator, or use Maestro Cloud. None of this was executed here (needs simulators).

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Fastlane tool | `screengrab` (Espresso/UI Automator) | `snapshot` (XCUITest) |
| Device frames | Emulator AVD sizes | Simulator device list |
| Needs Mac? | No | Yes (simulators) |
| Required store sizes | Min 2 phone screenshots; 16:9 / 9:16 | 6.9"/6.5" iPhone required; iPad if supported |
| testID maps to | `resource-id` / content-desc | `accessibilityIdentifier` |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Build a dev/preview build with EAS, install on simulator, run Maestro
eas build --profile preview --platform ios
maestro test .maestro/screenshots.yaml
```
CLI way:
```bash
# Bare RN: also can use Fastlane snapshot with native UI tests
cd ios && bundle exec fastlane snapshot
```
Expo Go cannot be used if your flow needs your own bundle ID / native modules; use a development build.

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Taking screenshots with real user data (names, phone numbers)
✅ **Correct:** Use a mock/demo API or seeded test account.

❌ **Mistake 2:** Screenshot taken before data loads — spinner visible
✅ **Correct:** `assertVisible` on real content first (Maestro waits), then screenshot.

❌ **Mistake 3:** Forgetting `testID` on elements
✅ **Correct:** Add `testID` to every interactive element used in flows.

❌ **Mistake 4:** Status bar shows 3% battery / odd time
✅ **Correct:** Use `xcrun simctl status_bar booted override --time 9:41 --batteryLevel 100` on iOS simulators (Fastlane `snapshot` does it automatically).

---

## 🧠 Tricky Interview Question
**Q:** Screenshots from CI look fine in English but Hindi text is cut off and shows boxes (□□□). Why?

**Answer:** Emulator/simulator image lacks a Devanagari font or locale is not actually switched, so glyphs fall back to missing-glyph boxes; also longer Hindi strings overflow fixed-width layouts. Fix: use a system image with full fonts, set the locale properly (`languages` in Snapfile / `locales` in screengrab), and design layouts with flexible widths (no fixed `width` on text containers).

---

## ⚫ Interview Questions + Answers

**Q1: Why automate screenshots?**
A1: Many sizes x languages x screens; automation keeps them consistent and current.

**Q2: Maestro vs Detox?**
A2: Maestro: black-box YAML flows, no native setup, quick. Detox: gray-box JS tests synchronized with RN, more code, stronger for deep E2E.

**Q3: What is `testID`?**
A3: A prop that exposes a stable identifier to automation tools.

**Q4: How to add device frames and captions?**
A4: Fastlane `frameit` or design tools; screenshots can also be uploaded raw.

**Q5: Where do screenshots go in stores?**
A5: App Store Connect → app version → media; Play Console → Store listing → Graphics. `deliver`/`supply` can upload them.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multi-language app
- Frequent UI changes
- Release every 2 weeks

❌ Avoid when:
- One-time MVP with 4 screenshots (do by hand)
- Highly dynamic/live content that cannot be stabilised

---

## 📊 Visual Diagram
```
 flow file ──► Maestro/Fastlane ──► Simulator/Emulator (app running)
                                        │ tap, wait, screenshot
                                        ▼
                               screenshots/ (en, hi x devices)
                                        │ frameit (optional)
                                        ▼
                         deliver / supply ──► App Store / Play Console
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Maestro | YAML-based mobile UI testing tool | YAML वाला UI testing tool |
| snapshot | Fastlane iOS screenshot tool | iOS screenshot tool |
| screengrab | Fastlane Android screenshot tool | Android screenshot tool |
| testID | Stable element identifier | Element की पक्की पहचान |
| frameit | Adds device frames | Device frame जोड़ने वाला tool |

---

## ⚡ 3-Line Summary
**English:**
1. A script drives the app and saves store screenshots for each device and language.
2. Maestro is easiest for Expo/RN; Fastlane snapshot/screengrab suit bare apps.
3. Use `testID`, demo data, and wait for content before capturing.

**Hindi:**
1. Script app चलाकर हर device/language के store screenshots सेव करती है।
2. Expo/RN के लिए Maestro आसान; bare apps में Fastlane snapshot/screengrab।
3. `testID`, demo data इस्तेमाल करो और content load होने के बाद capture करो।

---

## ➡️ Next Topic
**269. In-App Purchases (Android)** — Play Billing से app के अंदर products बेचना और पैसे कमाना।
