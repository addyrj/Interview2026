# 258. OTA Updates — What + Why
# हिंदी में: OTA Updates — क्या और क्यों
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52+ examples (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
OTA (Over-The-Air) update means delivering new JavaScript code and assets to an installed app over the internet, without a new store release. A React Native app is a native shell plus a JS bundle; OTA replaces only the bundle.

## 🔵 सरल परिभाषा (Hindi)
OTA (Over-The-Air) update का मतलब है इंटरनेट से installed app में नया JavaScript code और assets पहुँचाना, बिना नए store release के। React Native app = native shell + JS bundle; OTA सिर्फ bundle बदलता है।

---

## 🔴 Problem it Solves
```
BEFORE OTA:
  Bug -> fix -> build -> store review (hours to days) -> users must update manually
  Many users stay on the buggy version for weeks.

WITH OTA:
  Bug -> fix -> publish bundle (minutes) -> app downloads on next launch
```

## 🔴 यह क्यों बना? (Hindi)
OTA के बिना हर छोटी bug के लिए store review और user के manual update का इंतज़ार करना पड़ता था। OTA से fix मिनटों में users तक पहुँचता है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → App binary contains: native code + embedded JS bundle + runtimeVersion
Step 2 → You publish a new JS bundle for that runtimeVersion (eas update)
Step 3 → On launch, app asks the update server: "Any update for my runtimeVersion + channel?"
Step 4 → If yes, app downloads bundle + changed assets
Step 5 → Bundle is stored locally; applied on next launch (or immediate reload if coded)
Step 6 → If new bundle crashes, expo-updates falls back to the previous / embedded one (see its docs for exact rollback behaviour)
```

```
What is inside a RN app:
┌───────────────────────────────┐
│ Native shell (Java/Kotlin/ObjC/Swift, libs, permissions)  <- store only
│ JS bundle (your React code)                               <- OTA can replace
│ Assets (images, fonts)                                    <- OTA can replace
└───────────────────────────────┘
```

## 🟢 कैसे काम करता है? (Hindi)
1. App में native code + embedded JS bundle + runtimeVersion होता है।
2. आप उसी runtimeVersion के लिए नया bundle publish करते हो।
3. App launch पर server से पूछता है: "मेरे लिए कोई update?"
4. Update मिले तो bundle और बदले assets download होते हैं।
5. अगले launch पर (या तुरंत reload करके) नया code चलता है।
6. नया bundle crash करे तो पिछले bundle पर वापस जाने की व्यवस्था होती है।

---

## 🟡 Real World Example
Swiggy/Zomato जैसी टीमें festival offers की banner text, checkout screen की छोटी गलती या feature flag जैसी चीज़ें OTA से ठीक कर सकती हैं। Dream11 जैसे apps match-day पर तेज़ JS fixes OTA से भेजना पसंद करते हैं (अपनी internal policy के अनुसार)।

## 🟡 Real Example Hindi mein
Diwali sale के दिन checkout button की गलती दिखे तो Zomato-जैसी टीम 5 मिनट में OTA fix भेज सकती है, store review का इंतज़ार नहीं।

---

## 💻 Code Example — Basic (install + config)
```bash
npx expo install expo-updates          # correct version for your Expo SDK
eas update:configure                   # adds updates.url, runtimeVersion, channel config
```
```json
{
  "expo": {
    "runtimeVersion": { "policy": "appVersion" },
    "updates": { "url": "https://u.expo.dev/YOUR-PROJECT-ID" }
  }
}
```
Replace `YOUR-PROJECT-ID` with the value `eas update:configure` writes. Policies supported include `appVersion`, `nativeVersion`, `sdkVersion`, `fingerprint` (fingerprint available from SDK 50+; verify in docs).

## 💻 Code Example — Advanced (show "new version ready" banner with the useUpdates hook)
```jsx
// UpdateBanner.jsx - uses expo-updates hook to show and apply downloaded update
import React from 'react';                                         // React
import { View, Text, Pressable, StyleSheet } from 'react-native';  // UI
import * as Updates from 'expo-updates';                           // OTA API

export default function UpdateBanner() {                           // small banner component
  const { isUpdateAvailable, isUpdatePending, isChecking, isDownloading } = Updates.useUpdates(); // live state from native module

  if (!Updates.isEnabled) return null;                             // expo-updates is off in dev client/dev mode

  if (isUpdatePending) {                                           // update already downloaded
    return (
      <View style={styles.bar}>
        <Text style={styles.t}>New version ready</Text>
        <Pressable onPress={() => Updates.reloadAsync()}>          {/* restart with new bundle */}
          <Text style={styles.b}>Restart</Text>
        </Pressable>
      </View>
    );
  }
  if (isDownloading) return <Text style={styles.t}>Downloading update...</Text>; // progress hint
  if (isChecking) return null;                                     // silent check
  if (isUpdateAvailable) {                                         // available but not downloaded yet
    return (
      <Pressable style={styles.bar} onPress={() => Updates.fetchUpdateAsync()}>
        <Text style={styles.t}>Update available - tap to download</Text>
      </Pressable>
    );
  }
  return null;                                                     // nothing to show
}

const styles = StyleSheet.create({
  bar: { flexDirection: 'row', justifyContent: 'space-between', padding: 12, backgroundColor: '#222' }, // banner
  t: { color: '#fff' },                                            // text
  b: { color: '#fc8019', fontWeight: '700' },                      // action
});
```
Not run: expo-updates needs a real build; UI shell syntax-checked only.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| OTA allowed by store? | Yes (Play policy: no deceptive changes) | Yes, if interpreted JS and primary purpose unchanged (2.5.2) |
| Where bundle is stored | App internal storage | App sandbox |
| Default apply time | Next cold start | Next cold start |
| Store review risk | Low | Low if fixes/improvements only |
| Native changes | Not via OTA | Not via OTA |
| Same runtimeVersion needed | Yes | Yes |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas update --branch production --message "fix checkout"   # publish OTA
```
CLI way (bare React Native):
```bash
npx expo install expo-updates   # works in bare RN after "npx install-expo-modules"
npx expo-updates codesigning:generate ... # optional signing; see docs
# or alternatives: Revopush / self-hosted expo-updates server (custom server implementing the Expo Updates protocol)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Shipping JS that calls a native module not in the installed binary.
✅ Correct: Match runtimeVersion; native changes need a store build.

❌ Mistake 2: Testing OTA in dev mode.
✅ Correct: Test in a release/preview build (`Updates.isEnabled` is false in dev).

❌ Mistake 3: No rollback plan.
✅ Correct: Publish a fix or republish the previous update; test on a staging channel first.

❌ Mistake 4: Assuming users get it instantly.
✅ Correct: Default is download on launch, apply on next launch.

---

## 🧠 Tricky Interview Question
You published an OTA that adds `expo-camera` usage, but the installed app (built last month) never had expo-camera. What happens?

Answer: The JS tries to load a native module that does not exist in the binary, so it crashes or errors. This is why runtimeVersion exists: the update should target only binaries that contain the needed native code, so you must ship a new build and bump runtimeVersion.

---

## ⚫ Interview Questions + Answers
Q1: What does OTA replace?
A1: JS bundle and assets only.

Q2: When does the update apply?
A2: Downloaded at launch, applied on the next launch unless you reload manually.

Q3: What is runtimeVersion?
A3: A compatibility label tying an update to binaries with matching native code.

Q4: Is OTA allowed on iOS?
A4: Yes within the 2.5.2 limits (no change of primary purpose, no store-in-store).

Q5: Name OTA solutions.
A5: EAS Update, CodePush (retired by Microsoft), Revopush, self-hosted expo-updates server.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- JS bug fixes, copy/UI tweaks, feature flags, config changes

❌ Avoid when:
- New native module, permission, SDK upgrade, app icon/splash changes

---

## 📊 Visual Diagram
```
 Dev --eas update--> Update server (CDN)
                          ^
 App launch --- "anything new for runtime X / channel Y?" ---+
        |
   download bundle -> store -> next launch runs new JS
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OTA | Over-the-air update | हवा से update |
| Bundle | Packaged JS code | JS का package |
| runtimeVersion | Native compatibility tag | Native compatibility |
| Channel | Build's update stream | Update की धारा |
| Rollback | Return to old update | पुराने पर वापसी |

---

## ⚡ 3-Line Summary
English: OTA replaces JS bundle and assets without store review.
It must match the installed native code via runtimeVersion.
Great for quick fixes, not for native changes.

Hindi: OTA store review के बिना JS bundle और assets बदलता है।
इसे runtimeVersion से installed native code से match होना चाहिए।
तेज़ fixes के लिए बढ़िया, native बदलाव के लिए नहीं।

---

## ➡️ Next Topic
**259. Expo Updates (OTA)** — expo-updates library की details और API।
