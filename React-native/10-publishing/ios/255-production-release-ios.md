# 255. Production Release (iOS)
# हिंदी में: iOS Production Release — App Store पर live करना
# Platform: Android ❌ | iOS ✅

> Expo SDK 52+ examples (check current docs — APIs change between SDKs). App Store Connect labels can change; verify in the console.

---

## 🔵 Simple Definition (English)
Production release is the final step after Apple approves your build: you choose when and how the app goes live on the App Store (automatically, manually, on a scheduled date, or via a 7-day phased release).

## 🔵 सरल परिभाषा (Hindi)
Production release वह आख़िरी step है जब Apple build approve कर देता है और आप चुनते हैं कि app कब और कैसे live होगा: automatically, manually, तय तारीख पर, या 7 दिन के phased release से।

---

## 🔴 Problem it Solves
```
PROBLEM: Approval time is unpredictable; you may want launch on a fixed day (e.g. before IPL).
         Also, a bug in a full 100% release hits every user at once.
SOLUTION: Release options + phased rollout + ability to pause.
```

## 🔴 यह क्यों बना? (Hindi)
Approval कब आएगा पता नहीं होता, पर launch की तारीख तय हो सकती है। साथ ही अगर bug हो तो 100% users एक साथ प्रभावित हों — phased release से जोखिम कम होता है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → eas build --platform ios --profile production --auto-submit   (or build then submit)
Step 2 → Wait for build "Processing" in App Store Connect, then TestFlight smoke test
Step 3 → Create version (e.g. 2.4.0): "What's New", screenshots, build selected
Step 4 → Choose Version Release: Manually / Automatically / Scheduled date
Step 5 → (Optional) tick "Release update over 7-day period using phased release for automatic updates"
Step 6 → Submit for review; on approval -> release button or automatic go-live
Step 7 → Monitor crashes (Sentry/Crashlytics), App Store Connect Analytics
Step 8 → If broken: Pause Phased Release; ship hotfix (OTA if JS-only, or new build)
```

### Phased release schedule (automatic updates only)
| Day | % of users who auto-update |
|-----|----------------------------|
| 1 | 1% |
| 2 | 2% |
| 3 | 5% |
| 4 | 10% |
| 5 | 20% |
| 6 | 50% |
| 7 | 100% |
Users who tap "Update" manually in the App Store can still get it at any time; the phased release only affects automatic updates. You can pause for up to 30 days.

### Console screens (in words)
- **App Store Connect → My Apps → App → version page**: scroll to bottom section **"Version Release"** with three radio buttons: "Manually release this version", "Automatically release this version", "Automatically release this version after App Review, no earlier than [date picker]".
- Below it: **"Phased Release for Automatic Updates"** checkbox (iOS apps only).
- After approval, a blue **"Release This Version"** button appears at the top right if you chose manual.
- Once live, the version page shows a **Phased Release** panel with Day N/7, a "Pause" and "Release to All Users" button.

## 🟢 कैसे काम करता है? (Hindi)
1. Production build बनाओ और TestFlight पर जल्दी test करो।
2. नई version page बनाओ: What's New, screenshots, build चुनो।
3. Release type चुनो: Manual / Automatic / तारीख के बाद।
4. चाहो तो 7-day phased release on करो (1% से 100% तक)।
5. Review submit करो; approve होने पर release करो।
6. Crash monitoring देखते रहो; problem हो तो phased release pause करो और hotfix दो।

---

## 🟡 Real World Example
Swiggy/Zomato जैसी कंपनियाँ बड़े release (नया UI) phased rollout से देती हैं, और Android पर staged rollout भी साथ चलाती हैं ताकि crash rate बढ़ने पर रुक सकें। IPL final से पहले की release "Scheduled / manual" रखी जाती है ताकि marketing campaign के साथ live हो।

## 🟡 Real Example Hindi mein
Swiggy जैसे apps नया version पहले 1-2% users को देते हैं, crash rate देखते हैं और फिर बढ़ाते हैं। बड़ी campaign के दिन release manual रखी जाती है ताकि सही समय पर live हो।

---

## 💻 Code Example — Basic (eas.json + commands)
```json
{
  "cli": { "version": ">= 12.0.0", "appVersionSource": "remote" },
  "build": {
    "production": {
      "autoIncrement": true,
      "channel": "production"
    }
  },
  "submit": {
    "production": {
      "ios": { "ascAppId": "1234567890" }
    }
  }
}
```
```bash
# Build and submit in one go (EAS CLI)
eas build --platform ios --profile production --auto-submit
# Or step by step
eas build --platform ios --profile production
eas submit --platform ios --latest --profile production
```
Note: `autoIncrement` with `appVersionSource: "remote"` makes EAS manage the build number. Check the current EAS docs for the CLI version you use.

## 💻 Code Example — Advanced (in-app "update available" prompt using App Store version)
```jsx
// useStoreUpdateCheck.js - checks if a newer store version exists and prompts user
import { useEffect } from 'react';                                // run on mount
import { Alert, Linking, Platform } from 'react-native';         // dialogs, open store, platform
import Constants from 'expo-constants';                          // reads app version (expo-constants)

const APP_STORE_ID = '1234567890';                               // your numeric App Store id

export function useStoreUpdateCheck() {                          // hook
  useEffect(() => {                                              // runs once
    if (Platform.OS !== 'ios') return;                           // iOS-only logic here
    const check = async () => {                                  // async checker
      try {                                                      // handle offline errors
        const res = await fetch(`https://itunes.apple.com/lookup?id=${APP_STORE_ID}`); // public iTunes lookup API
        const json = await res.json();                           // parse JSON
        const storeVersion = json?.results?.[0]?.version;        // latest live version
        const current = Constants.expoConfig?.version;           // installed version
        if (storeVersion && current && storeVersion !== current) { // naive compare (use semver in prod)
          Alert.alert('Update available', `Version ${storeVersion} is live.`, [
            { text: 'Later', style: 'cancel' },                  // dismiss
            { text: 'Update', onPress: () => Linking.openURL(`itms-apps://apps.apple.com/app/id${APP_STORE_ID}`) }, // open App Store
          ]);
        }
      } catch (e) {
        console.warn('Update check failed', e);                   // never crash app for this
      }
    };
    check();                                                     // call once
  }, []);
}
```
Not run (needs device and a live App Store id).

---

## 📱 Android vs iOS Difference
| Feature | Android (Play) | iOS (App Store) |
|---------|----------------|-----------------|
| Gradual rollout | Staged rollout %, you choose any % | Phased release fixed 7-day schedule |
| Halt | Halt rollout in Play Console | Pause phased release (up to 30 days) |
| Scheduled launch | Managed publishing | Release after date / manual |
| Rollback | Can roll back to earlier tracks only by new build | Cannot roll back; ship new version (or remove from sale) |
| Review time before release | Hours-days | ~1-2 days |
| Pre-release testing | Internal/closed/open tracks | TestFlight |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas build -p ios --profile production --auto-submit   # certs, build, upload handled
```
CLI way:
```bash
# Xcode: bump CFBundleVersion, Product > Archive
# Organizer > Distribute App > App Store Connect > Upload
# Then do the same App Store Connect release steps manually
fastlane pilot upload   # optional, if you use fastlane
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to bump `buildNumber` (CFBundleVersion).
✅ Correct: Use `autoIncrement` or bump manually; duplicates are refused on upload.

❌ Mistake 2: Choosing "Automatically release" for risky launches.
✅ Correct: Use manual or scheduled release and phased rollout.

❌ Mistake 3: Expecting phased release to stop manual updaters.
✅ Correct: It only controls automatic updates.

❌ Mistake 4: No crash monitoring after release.
✅ Correct: Add Sentry/Crashlytics and watch the first 24 hours.

---

## 🧠 Tricky Interview Question
You paused the phased release at day 3, but users still report the new version. Why?

Answer: Phased release limits automatic updates only. Users who open the App Store and tap Update, or who already downloaded it, still get the new version. Pausing prevents further auto-updates; it is not a rollback. Fix with a new build or an OTA JS fix.

---

## ⚫ Interview Questions + Answers
Q1: Can you roll back an iOS release?
A1: Not directly. You release a new version with the fix (or removal from sale).

Q2: What are the release options?
A2: Manual, automatic after approval, or automatic after approval no earlier than a chosen date.

Q3: How long can a phased release be paused?
A3: Up to 30 days.

Q4: Does `eas submit` publish to users?
A4: No. It uploads to App Store Connect; you still submit for review and release.

Q5: What is the best hotfix path?
A5: JS-only: EAS Update. Native change: new build + review (request expedited if critical).

---

## 🔷 When to Use + When Not to Use
✅ Use phased release when:
- Large user base, major UI/feature change

❌ Avoid when:
- Urgent security fix that must reach everyone immediately (release to all users)

---

## 📊 Visual Diagram
```
 Approved
    |
    +--Manual-------> [Release This Version] --> Live
    +--Automatic----> Live
    +--Scheduled----> Live at date
                         |
              Phased: 1% 2% 5% 10% 20% 50% 100%
                         |
                monitor crashes -> Pause / Release to all
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Phased release | 7-day gradual auto-update | धीरे-धीरे release |
| Build number | Unique upload number | Build क्रमांक |
| Auto-submit | Upload right after build | Build के बाद auto upload |
| Pause | Stop further auto-updates | रोक देना |
| Ready for Distribution | Live status | Live स्थिति |

---

## ⚡ 3-Line Summary
English: After approval choose manual, automatic, or scheduled release.
Phased release gives 1% to 100% over 7 days for automatic updates.
There is no rollback; monitor and ship a fix.

Hindi: Approval के बाद manual, automatic या scheduled release चुनो।
Phased release में 7 दिन में 1% से 100% तक auto-update जाता है।
Rollback नहीं होता; monitor करो और fix भेजो।

---

## ➡️ Next Topic
**256. App Updates (iOS)** — live app को नए versions से कैसे update करें।
