# 184. E2E Testing (Detox)
# हिंदी में: End-to-End Testing — Detox से
# Platform: Both ✅ (Android ✅ | iOS ✅)

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs). Detox को native build चाहिए — Expo Go में नहीं चलता; Expo में development build / prebuild चाहिए और `@config-plugins/detox` plugin use होता है।

---

## 🔵 Simple Definition (English)
**Detox** is a gray-box end-to-end test framework for React Native. It launches your real app on an emulator/simulator, taps and types like a user, and automatically waits until the app is idle (network, animations, timers) before the next step — so tests are not flaky.

## 🔵 सरल परिभाषा (Hindi)
**Detox** React Native का gray-box E2E testing framework है। यह आपका असली app emulator/simulator पर चलाता है, user की तरह tap और type करता है, और अगली step से पहले app के idle होने (network, animation, timers) का खुद इंतज़ार करता है — इसलिए tests कम flaky होते हैं।

---

## 🔴 Problem it Solves
```
UNIT TESTS की सीमा:
  ❌ Real navigation, keyboard, permissions, native modules नहीं दिखते
  ❌ "Login → Home → Add to cart → Pay" पूरा flow verify नहीं होता
OLD E2E (Appium): 
  ❌ बाहर से black-box, sleep(3000) जैसे hacks, flaky
DETOX:
  ✅ App के अंदर से sync (idle का पता होता है)
  ✅ Real build पर पूरा journey test
```

## 🔴 यह क्यों बना? (Hindi)
```
Unit tests पूरा user journey नहीं देखते।
Appium में sleep/wait से tests flaky होते थे।
Detox app की activity track करके खुद wait करता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npm i -D detox jest ; npx detox init (config + e2e folder)
Step 2 → .detoxrc.js में apps (build command + binary path) और devices (emulator/simulator) define करो
Step 3 → detox build -c ios.sim.debug (या android.emu.debug)
Step 4 → detox test -c ios.sim.debug → app launch होता है
Step 5 → element(by.id('x')).tap() / typeText() से actions
Step 6 → expect(element(by.text('Welcome'))).toBeVisible() से check
Step 7 → Detox native side से network/animation idle track करता है, तब अगला step
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1-2 → Install और config
Step 3 → App का build बनाओ
Step 4 → Test चलाओ, app emulator में खुलता है
Step 5-6 → Actions और expectations
Step 7 → Detox खुद wait करता है — sleep नहीं
```

---

## 🟡 Real World Example
**Zomato** का critical flow: Login (OTP) → Search "Pizza" → Restaurant खोलो → Item add → Cart → Checkout button visible। एक Detox test यह पूरा flow Android emulator और iOS simulator पर release से पहले हर बार चलाता है। **Paytm** में "Send Money" flow (UPI ID डालो → amount → confirm screen दिखे) इसी तरह regression-guard होता है।

## 🟡 Real Example Hindi mein
Zomato का Login → Search → Cart → Checkout flow release से पहले Detox से automatic चलता है। अगर checkout button गायब हुआ तो CI fail और release रुक जाता है।

---

## 💻 Code Example — Basic
```jsx
// ---------- .detoxrc.js (iOS simulator + Android emulator) ----------
/** @type {Detox.DetoxConfig} */
module.exports = {
  testRunner: {                                           // Jest as runner
    args: { $0: 'jest', config: 'e2e/jest.config.js' },   // jest config path
    jest: { setupTimeout: 120000 },                       // allow slow boot
  },
  apps: {
    'ios.debug': {                                        // iOS app definition
      type: 'ios.app',
      binaryPath: 'ios/build/Build/Products/Debug-iphonesimulator/MyApp.app', // built .app
      build: 'xcodebuild -workspace ios/MyApp.xcworkspace -scheme MyApp -configuration Debug -sdk iphonesimulator -derivedDataPath ios/build',
    },
    'android.debug': {                                    // Android app definition
      type: 'android.apk',
      binaryPath: 'android/app/build/outputs/apk/debug/app-debug.apk',
      build: 'cd android && ./gradlew assembleDebug assembleAndroidTest -DtestBuildType=debug',
    },
  },
  devices: {
    simulator: { type: 'ios.simulator', device: { type: 'iPhone 15' } }, // simulator name
    emulator: { type: 'android.emulator', device: { avdName: 'Pixel_4_API_34' } }, // AVD name
  },
  configurations: {                                       // device + app pair
    'ios.sim.debug': { device: 'simulator', app: 'ios.debug' },
    'android.emu.debug': { device: 'emulator', app: 'android.debug' },
  },
};

// ---------- e2e/login.test.js ----------
describe('Login flow', () => {                            // test group
  beforeAll(async () => {
    await device.launchApp();                             // start app once
  });

  beforeEach(async () => {
    await device.reloadReactNative();                     // fresh JS state each test
  });

  it('shows welcome after valid login', async () => {
    await element(by.id('phone-input')).typeText('9876543210'); // type phone
    await element(by.id('login-button')).tap();           // press login
    await expect(element(by.text('Welcome'))).toBeVisible(); // verify result
  });
});
// Component में testID="phone-input" और testID="login-button" लगाना ज़रूरी है
```

## 💻 Code Example — Advanced
```jsx
// ---------- e2e/checkout.test.js — Production style ----------
const { device, element, by, expect, waitFor } = require('detox'); // explicit imports

// Helper: login once, reuse in many tests
async function loginAsTestUser() {
  await element(by.id('phone-input')).replaceText('9999900000'); // replaceText = fast, no keyboard typing
  await element(by.id('login-button')).tap();
  await waitFor(element(by.id('home-screen')))           // wait for async navigation
    .toBeVisible()
    .withTimeout(10000);                                 // fail after 10 sec
}

describe('Checkout', () => {
  beforeAll(async () => {
    await device.launchApp({
      newInstance: true,                                 // always cold start
      permissions: { notifications: 'YES', location: 'inuse' }, // pre-grant permissions (avoid system dialogs)
      launchArgs: { detoxEnableSynchronization: 1 },     // keep auto-sync on (default)
    });
    await loginAsTestUser();
  });

  afterEach(async () => {
    // Take screenshot automatically on failure is configured via artifacts in .detoxrc.js
    await device.reloadReactNative();                    // reset for isolation
    await loginAsTestUser();
  });

  it('adds item and reaches payment', async () => {
    await element(by.id('restaurant-list')).scroll(300, 'down'); // scroll list
    await element(by.id('restaurant-0')).tap();          // open first restaurant
    await element(by.id('add-item-0')).tap();            // add item
    await element(by.id('cart-badge')).tap();            // open cart
    await expect(element(by.id('pay-button'))).toBeVisible(); // pay visible
  });

  it('shows error on offline', async () => {
    // Android: back button; iOS में नहीं है
    if (device.getPlatform() === 'android') {
      await device.pressBack();                          // Android hardware back
    }
    await expect(element(by.id('home-screen'))).toBeVisible();
  });
});
// Run: npx detox build -c ios.sim.debug && npx detox test -c ios.sim.debug
// Not run here — requires emulator/simulator.
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Device | Emulator (AVD) / real device | Simulator (Xcode) — macOS ज़रूरी |
| Build | Gradle `assembleDebug assembleAndroidTest` | `xcodebuild` |
| Back button | `device.pressBack()` available | Hardware back नहीं |
| Permissions | `launchApp({permissions})` supported | Supported (अलग keys) |
| CI | Linux/macOS runner | सिर्फ macOS runner |
| Locator | `by.id` → resource tag / testID | `by.id` → accessibilityIdentifier |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo Go में Detox NAHI चलता — native build चाहिए
// npx expo install expo-dev-client
// npx expo prebuild   → ios/ और android/ बनते हैं
// app.json plugins: ["@config-plugins/detox"]
// फिर .detoxrc.js में binaryPath prebuild के output की ओर
// (EAS Build से .app/.apk बनाकर भी use कर सकते हैं)
```
CLI way:
```jsx
// Bare RN: ios/ और android/ पहले से हैं
// npm i -D detox ; npx detox init
// Android: android/app/build.gradle में androidTest dependency + DetoxTest.java
//          (Detox docs का "Android setup" step)
// iOS: कोई extra native step नहीं (Detox pod autolink)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `await new Promise(r => setTimeout(r, 3000))` से wait
✅ Correct: `waitFor(element).toBeVisible().withTimeout(ms)`

❌ Mistake 2: `testID` नहीं लगाया, text से ढूँढना (language बदलते ही fail)
✅ Correct: Stable `testID` use करो

❌ Mistake 3: Infinite animation / polling timer → Detox कभी idle नहीं मानता, test hang
✅ Correct: Test mode में animation बंद करो या `device.disableSynchronization()` सीमित जगह पर

❌ Mistake 4: Tests एक-दूसरे पर dependent
✅ Correct: हर test independent, `reloadReactNative()` या `newInstance`

❌ Mistake 5: Real production API पर test
✅ Correct: Staging/mock server

---

## 🧠 Tricky Interview Question
Detox test locally pass होता है पर CI पर कभी-कभी fail होता है "element not visible"। App में 1 सेकंड वाला `setInterval` polling चल रहा है। क्या कारण हो सकते हैं?

Answer: Detox synchronization बाकी pending timers/network को track करता है। लगातार चलता `setInterval` या loop वाली animation app को "busy" रखती है, तो Detox wait करता रहता है या timeout होता है। CI की slow machine पर यह timing issue ज़्यादा दिखता है। Fix: test build में polling बंद करो/बड़ा interval करो, `withTimeout` बढ़ाओ, और जरूरी हो तो उस step के आसपास `device.disableSynchronization()` फिर `enableSynchronization()`।

---

## ⚫ Interview Questions + Answers
Q1: Detox gray-box क्यों कहलाता है?
A1: क्योंकि यह app के अंदर native side से activity (network, timers, animations) monitor करता है, सिर्फ बाहर से UI नहीं देखता।

Q2: Detox और Appium में फर्क?
A2: Appium black-box और cross-language है, ज़्यादा flaky; Detox RN-focused है, auto-synchronization देता है, JS में लिखते हैं।

Q3: Detox Expo Go में चलेगा?
A3: नहीं। Custom native build (dev client/prebuild/EAS Build) चाहिए।

Q4: E2E tests कितने लिखें?
A4: सिर्फ critical journeys (login, checkout, payment); बाकी Jest/RNTL में — E2E महँगे और धीमे हैं।

Q5: Maestro क्या है?
A5: YAML-based mobile E2E tool; setup आसान, Expo/EAS के साथ लोकप्रिय; Detox ज़्यादा JS-control और sync देता है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Release से पहले critical flows verify करने हों
- Native integration (permissions, deep links) test करना हो
- CI में regression gate चाहिए

❌ Avoid when:
- Simple component logic (RNTL काफी है)
- Team में setup/maintenance time नहीं
- हर छोटी चीज़ E2E में डालना

---

## 📊 Visual Diagram
```
  Jest test (Node) <--WebSocket--> Detox client in app
        |                                |
   element().tap()                 native sync monitor
        |                                |
   Emulator / Simulator  -->  Real app (RN JS + native)
                                   |
                  idle? (network, timers, animations) → next step
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| E2E | Full user flow test | शुरू से अंत तक test |
| Gray-box | Sees inside app activity | अंदर की जानकारी वाला |
| Synchronization | Auto-wait for idle | खुद wait करना |
| testID | Stable element id | Element की पहचान |
| `.detoxrc.js` | Detox config | Detox की settings |
| Flaky test | Randomly pass/fail | कभी pass कभी fail |

---

## ⚡ 3-Line Summary
English: Detox runs your real app on emulator/simulator and tests full user flows.
It auto-waits for app idle, so fewer flaky tests than black-box tools.
Needs a native build (not Expo Go); keep E2E for critical journeys only.

Hindi: Detox असली app पर पूरा user flow test करता है।
App idle होने का खुद इंतज़ार करता है, इसलिए कम flaky।
Native build चाहिए (Expo Go नहीं); सिर्फ critical flows के लिए।

---

## ➡️ Next Topic
**185. Accessibility in React Native** — सबके लिए usable app: screen readers (TalkBack/VoiceOver), labels, roles।

---
