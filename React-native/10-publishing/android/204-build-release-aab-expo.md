# 204. Build Release AAB (Expo)
# हिंदी में: Expo से Release AAB बनाना
# Platform: Android ✅ | iOS ❌

> Target: **Expo SDK 52 (React Native 0.76)** with `eas-cli` — check current docs — APIs change between SDKs and EAS CLI versions.

---

## 🔵 Simple Definition (English)
An **AAB (Android App Bundle, `.aab`)** is the format Google Play requires for new apps. You upload it; Google generates small optimized APKs for each user's device. EAS Build makes an AAB by default for the `production` profile.

## 🔵 सरल परिभाषा (Hindi)
**AAB (Android App Bundle, `.aab`)** वह format है जो Google Play नए apps के लिए माँगता है। आप इसे upload करते हो; Google हर device के लिए छोटे optimized APK बनाता है। EAS Build `production` profile में default रूप से AAB बनाता है।

---

## 🔴 Problem it Solves
- A universal APK includes resources for all languages/screen densities → big download (e.g. 80 MB).
- AAB lets Play deliver only what the device needs → typically 15-30% smaller download.
- Play App Signing: Google keeps the final signing key; you only keep the upload key.

## 🔴 यह क्यों बना? (Hindi)
- Universal APK में सभी भाषाओं/densities के resources होते हैं → size बड़ा।
- AAB से Play सिर्फ ज़रूरी हिस्सा देता है → download छोटा।
- Play App Signing: final signing key Google के पास, आपके पास सिर्फ upload key।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Ensure app.json has: expo.android.package and expo.android.versionCode (or autoIncrement)
Step 2 → eas.json has a "production" profile (default build type = app-bundle)
Step 3 → Run: eas build --platform android --profile production
Step 4 → EAS uses (or creates) your upload keystore, runs ./gradlew bundleRelease in cloud
Step 5 → Build finishes → download app-release.aab from expo.dev build page
Step 6 → Upload the .aab in Play Console (manually) or run: eas submit -p android --latest
Step 7 → Google re-signs with the app signing key and creates device-specific APKs
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → app.json में android.package और versionCode (या autoIncrement) रखो
Step 2 → eas.json में "production" profile (default build type = app-bundle)
Step 3 → चलाओ: eas build --platform android --profile production
Step 4 → EAS upload keystore इस्तेमाल करके cloud में bundleRelease चलाता है
Step 5 → Build पूरा होने पर expo.dev से .aab download करो
Step 6 → Play Console में upload करो या eas submit -p android --latest
Step 7 → Google अपनी key से re-sign करके device-specific APK बनाता है
```

**Console screens (described):**
- **Terminal prompts (first run):** "What would you like your Android application id to be?" (shown only if `android.package` missing), "Generate a new Android Keystore?" (answer Yes).
- **expo.dev build page:** Header shows build number, profile `production`, status chip. The **Artifact** row lists `.aab` with a Download button (no QR install because AAB cannot be installed directly). A **Submit to Google Play Store** button/menu may appear.

---

## 🟡 Real World Example
Zomato-scale apps ship AAB: a user on a low-end 720p phone in Patna downloads only `hdpi` resources and the Hindi language split, not 4K images or 40 other languages — faster installs on 4G.

## 🟡 Real Example Hindi mein
Zomato जैसे बड़े apps AAB देते हैं: Patna में 720p वाले सस्ते phone पर सिर्फ `hdpi` resources और हिंदी language split download होता है — 4G पर install तेज़ होता है।

---

## 💻 Code Example — Basic
```json
{
  "cli": { "version": ">= 12.0.0", "appVersionSource": "remote" },
  "build": {
    "production": {
      "autoIncrement": true,
      "android": { "buildType": "app-bundle" }
    }
  }
}
```
```bash
# Build the AAB in the cloud
eas build --platform android --profile production
```

## 💻 Code Example — Advanced
Build + auto-submit to internal testing track, env vars, and a version check:
```json
{
  "cli": { "version": ">= 12.0.0", "appVersionSource": "remote" },
  "build": {
    "production": {
      "autoIncrement": true,
      "channel": "production",
      "env": { "API_URL": "https://api.foodapp.in" },
      "android": { "buildType": "app-bundle" }
    }
  },
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "./play-service-account.json",
        "track": "internal",
        "releaseStatus": "draft"
      }
    }
  }
}
```
```bash
# Build then submit automatically when build finishes
eas build -p android --profile production --auto-submit
# Check which versionCode EAS will use next (remote versioning)
eas build:version:get -p android
# Inspect artifact locally (needs bundletool) – builds universal APKs from AAB for testing
java -jar bundletool.jar build-apks --bundle=app.aab --output=app.apks --mode=universal
```
> `autoIncrement` + `appVersionSource: "remote"`: EAS keeps the `versionCode` on its server; every build increments it. Never reuse a versionCode — Play rejects it.
`play-service-account.json` is a secret: add to `.gitignore`.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Store artifact | `.aab` | `.ipa` |
| Optimisation | Play creates per-device APKs | App Thinning by App Store |
| Version number | `versionCode` (int) + `versionName` | `buildNumber` + `version` |
| Signing | Upload key, Play App Signing | Distribution cert + provisioning profile |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// eas build -p android --profile production
```
CLI way:
```bash
cd android
./gradlew bundleRelease
# Output: android/app/build/outputs/bundle/release/app-release.aab
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Same `versionCode` as earlier upload → "Version code already used".
✅ Correct: `autoIncrement: true` or bump manually.

❌ Mistake 2: Trying to install `.aab` on phone.
✅ Correct: Use bundletool or build an APK profile for testing.

❌ Mistake 3: Losing the upload key.
✅ Correct: Keep EAS-managed keystore, backup via `eas credentials`; Play support can reset an upload key if Play App Signing is on.

❌ Mistake 4: Changing `android.package` after first upload.
✅ Correct: Package name is permanent for a Play app.

---

## 🧠 Tricky Interview Question
"Your AAB is 40 MB but Play Console shows 'download size 22 MB'. Why?"

Answer: Play shows the compressed, device-optimised download. Split APKs exclude other ABIs, densities and languages, and use compression — so the download is smaller than the bundle file.

---

## ⚫ Interview Questions + Answers
Q1: Why AAB over APK?
A1: Smaller downloads, Play App Signing, dynamic features, and it is mandatory for new apps (since Aug 2021).

Q2: How is `versionCode` managed in EAS?
A2: `autoIncrement` with remote `appVersionSource` or set it in `app.json`.

Q3: Can I use an existing keystore?
A3: Yes: `eas credentials` → Android → upload your keystore.

Q4: What is the upload key?
A4: Key you sign the AAB with; Google verifies it and re-signs with the app signing key.

Q5: Which command builds AAB locally in Expo?
A5: `eas build -p android --profile production --local` (or prebuild + `./gradlew bundleRelease`).

---

## 🔷 When to Use + When Not to Use
✅ Use when: publishing to Google Play (all tracks).

❌ Avoid when: sharing directly with testers (APK is easier).

---

## 📊 Visual Diagram
```
 eas build (production) ─► app.aab ─► Play Console
                                          │ Play App Signing
                                          ▼
              ┌──────────── split APKs per device ───────────┐
              │ base.apk + arm64 + xxhdpi + hi (Hindi) ...    │
              └───────────────────────────────────────────────┘
                                          ▼
                                    User's phone
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AAB | Android App Bundle | Play के लिए bundle format |
| Upload key | Key you sign with | Upload के लिए key |
| App signing key | Google-held final key | Google की final key |
| versionCode | Increasing integer | बढ़ता हुआ integer |
| Split APK | Device-specific APK | Device के हिसाब से APK |

---

## ⚡ 3-Line Summary
English: Run `eas build -p android --profile production` to get an AAB.
Keep versionCode increasing and package name fixed.
Upload to Play Console or use `eas submit`.

Hindi: `eas build -p android --profile production` से AAB बनाओ।
versionCode बढ़ाते रहो और package name कभी मत बदलो।
Play Console में upload करो या `eas submit` चलाओ।

---

## ➡️ Next Topic
**205. Build Release AAB (CLI)** — Expo के बिना, Gradle से सीधे AAB।
