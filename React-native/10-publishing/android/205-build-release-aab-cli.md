# 205. Build Release AAB (CLI)
# हिंदी में: React Native CLI से Release AAB बनाना
# Platform: Android ✅ | iOS ❌

> Target: **React Native 0.76 (bare CLI project; also valid for Expo SDK 52 after `expo prebuild`)** — check current docs — Gradle/AGP versions change between RN releases.

---

## 🔵 Simple Definition (English)
Building an AAB with the CLI means using Gradle on your own computer (`./gradlew bundleRelease`) with your own keystore. You need Android Studio/SDK, JDK and a signing config.

## 🔵 सरल परिभाषा (Hindi)
CLI से AAB बनाने का मतलब अपने computer पर Gradle (`./gradlew bundleRelease`) चलाना है, अपनी keystore के साथ। इसके लिए Android Studio/SDK, JDK और signing config चाहिए।

---

## 🔴 Problem it Solves
- Teams without Expo/EAS (bare RN, company CI servers) need full control of the build.
- Offline/private builds; custom Gradle plugins; strict company security rules.

## 🔴 यह क्यों बना? (Hindi)
- जिन teams के पास Expo/EAS नहीं है (bare RN, company CI) उन्हें पूरा control चाहिए।
- Offline/private builds, custom Gradle plugins और company security rules के लिए।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Install JDK 17 and Android Studio (SDK Platform + Build-Tools); set ANDROID_HOME
Step 2 → Generate upload keystore (one time):
         keytool -genkeypair -v -storetype PKCS12 -keystore upload-keystore.jks \
                 -alias upload -keyalg RSA -keysize 2048 -validity 10000
Step 3 → Put file in android/app/ (DO NOT commit to git)
Step 4 → Put passwords in ~/.gradle/gradle.properties (NOT in project)
Step 5 → Edit android/app/build.gradle: add signingConfigs.release and use it in buildTypes.release
Step 6 → Bump versionCode / versionName in android/app/build.gradle
Step 7 → cd android && ./gradlew clean bundleRelease
Step 8 → Output: android/app/build/outputs/bundle/release/app-release.aab
Step 9 → Upload to Play Console → Release → Production/Testing → Create new release
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → JDK 17 और Android Studio install करो; ANDROID_HOME set करो
Step 2 → Upload keystore बनाओ (सिर्फ एक बार) — keytool command
Step 3 → File android/app/ में रखो (git में commit मत करो)
Step 4 → Passwords ~/.gradle/gradle.properties में रखो (project में नहीं)
Step 5 → build.gradle में signingConfigs.release जोड़ो
Step 6 → versionCode / versionName बढ़ाओ
Step 7 → cd android && ./gradlew clean bundleRelease
Step 8 → Output: android/app/build/outputs/bundle/release/app-release.aab
Step 9 → Play Console में upload करो
```

**Console screens (described):**
- **Play Console → your app → Release → Production → Create new release:** a page with "App bundles" drop zone ("Upload" button), then "Release name" and "Release notes" text boxes; the "Next" button leads to a review page showing errors (red) and warnings (yellow).
- **Terminal:** Gradle prints tasks (`:app:bundleReleaseJsAndAssets`, `:app:packageReleaseBundle`) and ends with `BUILD SUCCESSFUL in 3m`.

---

## 🟡 Real World Example
A fintech like **Paytm/PhonePe** builds on its own CI (Jenkins/GitHub Actions) with `./gradlew bundleRelease`, reading the keystore from a secured vault, because compliance forbids third-party cloud builds.

## 🟡 Real Example Hindi mein
**Paytm/PhonePe** जैसी fintech अपनी CI (Jenkins/GitHub Actions) में `./gradlew bundleRelease` चलाती हैं और keystore secure vault से लेती हैं, क्योंकि compliance में third-party cloud build मना होता है।

---

## 💻 Code Example — Basic
`~/.gradle/gradle.properties` (outside the repo):
```properties
# Keystore details kept out of git
MYAPP_UPLOAD_STORE_FILE=upload-keystore.jks
MYAPP_UPLOAD_KEY_ALIAS=upload
MYAPP_UPLOAD_STORE_PASSWORD=*****
MYAPP_UPLOAD_KEY_PASSWORD=*****
```
`android/app/build.gradle`:
```groovy
android {
    // Signing configs section
    signingConfigs {
        release {
            // Only configure if properties exist (so debug builds still work)
            if (project.hasProperty('MYAPP_UPLOAD_STORE_FILE')) {
                storeFile file(MYAPP_UPLOAD_STORE_FILE)         // keystore file
                storePassword MYAPP_UPLOAD_STORE_PASSWORD       // keystore password
                keyAlias MYAPP_UPLOAD_KEY_ALIAS                 // key alias
                keyPassword MYAPP_UPLOAD_KEY_PASSWORD           // key password
            }
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release  // use release key (not debug!)
            minifyEnabled true                    // shrink with R8
            shrinkResources true                  // remove unused resources
            proguardFiles getDefaultProguardFile("proguard-android.txt"), "proguard-rules.pro"
        }
    }
}
```
```bash
cd android
./gradlew bundleRelease
```

## 💻 Code Example — Advanced
CI-friendly script with checks, env-var based secrets and verification:
```bash
#!/usr/bin/env bash
set -euo pipefail                                   # stop on first error / unset var

# Fail early if secrets are missing
: "${KEYSTORE_B64:?Missing KEYSTORE_B64}"            # base64 keystore from CI secret
: "${MYAPP_UPLOAD_STORE_PASSWORD:?Missing password}"

# Restore keystore from secret
echo "$KEYSTORE_B64" | base64 --decode > android/app/upload-keystore.jks

# Pass credentials as Gradle properties for this run only
cd android
./gradlew clean bundleRelease \
  -PMYAPP_UPLOAD_STORE_FILE=upload-keystore.jks \
  -PMYAPP_UPLOAD_KEY_ALIAS=upload \
  -PMYAPP_UPLOAD_STORE_PASSWORD="$MYAPP_UPLOAD_STORE_PASSWORD" \
  -PMYAPP_UPLOAD_KEY_PASSWORD="$MYAPP_UPLOAD_KEY_PASSWORD"

# Verify AAB is signed with the upload key
jarsigner -verify -verbose -certs app/build/outputs/bundle/release/app-release.aab | tail -5

# Remove keystore from the runner
rm -f app/upload-keystore.jks
```
Test the release bundle on a device with bundletool:
```bash
java -jar bundletool.jar build-apks --bundle=app-release.aab --output=app.apks \
  --ks=upload-keystore.jks --ks-key-alias=upload     # sign test APKs
java -jar bundletool.jar install-apks --apks=app.apks # install on connected device
```
Also test a release APK on device before upload: `npx react-native run-android --mode release` (flag name `--mode` in RN CLI 0.7x; older used `--variant`).

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Tool | Gradle (`bundleRelease`) | Xcode Archive / `xcodebuild` |
| Signing | Keystore (.jks) | Certificate + Provisioning Profile |
| Machine | Windows/Mac/Linux | macOS only |
| Output | `.aab` | `.ipa` |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// eas build -p android --profile production  (cloud, keystore handled)
```
CLI way:
```bash
cd android && ./gradlew bundleRelease   # local, you manage keystore + SDK
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Committing keystore/passwords to git.
✅ Correct: `.gitignore` the keystore; use `~/.gradle/gradle.properties` or CI secrets.

❌ Mistake 2: Signing release with debug keystore (default template does this!).
✅ Correct: Change `signingConfig` in release buildType.

❌ Mistake 3: Forgetting to bump `versionCode`.
✅ Correct: Increase before each upload.

❌ Mistake 4: App crashes in release only due to R8/Proguard stripping.
✅ Correct: Add keep rules for reflection-based libs; test the release build.

---

## 🧠 Tricky Interview Question
"Release build works but images/JS look old after code change."

Answer: Stale caches. Run `./gradlew clean`, and delete `android/app/build`; for JS bundle also `npx react-native start --reset-cache`. The release build embeds `index.android.bundle` created at build time, so you must rebuild for any JS change.

---

## ⚫ Interview Questions + Answers
Q1: Why minify/shrink?
A1: Smaller size and light obfuscation (R8).

Q2: Where is the AAB?
A2: `android/app/build/outputs/bundle/release/app-release.aab`.

Q3: Which JDK?
A3: JDK 17 for RN 0.73+ (check your RN version's docs).

Q4: How to keep secrets out of repo?
A4: Global gradle.properties or CI secret + base64 keystore.

Q5: How to test the AAB before upload?
A5: bundletool `build-apks` + `install-apks`.

---

## 🔷 When to Use + When Not to Use
✅ Use when: bare RN, custom native setup, strict compliance, own CI.

❌ Avoid when: small team wanting speed — EAS saves setup time.

---

## 📊 Visual Diagram
```
 JS code ─► Metro bundle ─┐
 Native code (Kotlin/Java)─┼► Gradle bundleRelease ─► sign (upload key) ─► app-release.aab
 Resources ───────────────┘                                                    │
                                                                               ▼
                                                                         Play Console
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Gradle | Android build tool | Android build tool |
| Keystore (.jks) | Signing key file | Signing key file |
| R8/Proguard | Code shrinker | Code छोटा करने वाला tool |
| bundletool | Tool to test AAB | AAB test करने का tool |

---

## ⚡ 3-Line Summary
English: Set a release signing config, keep secrets out of git, run `./gradlew bundleRelease`.
Bump versionCode each upload.
Test the release build before uploading.

Hindi: Release signing config set करो, secrets git से बाहर रखो, `./gradlew bundleRelease` चलाओ।
हर upload पर versionCode बढ़ाओ।
Upload से पहले release build test करो।

---

## ➡️ Next Topic
**206. EAS Build — Expo Application Services** — cloud build service का पूरा overview।
