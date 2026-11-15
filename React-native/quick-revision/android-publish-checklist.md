# React Native — Android Publish Checklist
# Keystore → AAB → Play Console → Testing → Rollout
# Quick Revision

> Condensed from `10-publishing/android/` (topics 191-225). Target in those notes: Expo SDK 52 / React Native 0.76 (some Play Console topics: SDK 53/54). Check current docs — APIs change between SDKs. Play Console menus, fees, tester counts, target API level and review times change often: verify against current docs (support.google.com/googleplay/android-developer). Commands in the notes were not run.

---

## 🔑 Stage 1 — Keystore & App Signing

**Gist:** Signing proves an update comes from you. With Play App Signing the real app-signing key stays at Google and you sign uploads with an **upload key**, which can be reset if lost (191). The classic raw-keystore advice (never lose it) still applies if you are NOT enrolled.

**हिंदी:** Keystore आपकी digital signature है; असली key Google के पास रहती है, आप upload key से sign करते हैं।

```bash
# Create upload keystore ONCE (JDK keytool)
keytool -genkeypair -v -storetype PKCS12 \
  -keystore upload-keystore.jks \
  -alias upload \
  -keyalg RSA -keysize 2048 -validity 10000

# See SHA1 / SHA256 fingerprints (Firebase / Google Sign-In)
keytool -list -v -keystore upload-keystore.jks -alias upload
```

- [ ] Generate the upload keystore once with `keytool` (validity 10000 days, ~27 years — Play needs 25+) — एक बार बनाओ
- [ ] Back up keystore + passwords in a password manager + 2 encrypted copies — backup ज़रूर रखो
- [ ] Add `*.jks` and `*.keystore` to `.gitignore`; never commit the keystore — repo में commit मत करो
- [ ] Keep passwords in `~/.gradle/gradle.properties` (outside repo) or CI secrets — passwords सुरक्षित रखो
- [ ] Use a separate release/upload keystore (not the debug keystore) — debug key से release मत करो
- [ ] Enrol in Play App Signing (default for new apps; AAB needs it) — Play App Signing चालू रखो
- [ ] Firebase / Google Sign-In: add SHA-1/256 of the **App signing key certificate** (from Play Console) as well as the upload key — दोनों SHA जोड़ो
- [ ] Expo: let EAS generate and store the keystore; inspect with `eas credentials` — EAS खुद keystore संभालता है
- [ ] Know the recovery path: Play Console → Setup → App signing → Request upload key reset — upload key खोई तो reset

```groovy
// android/app/build.gradle (bare RN / prebuild) — props come from gradle.properties
android {
    signingConfigs {
        release {
            if (project.hasProperty('MYAPP_UPLOAD_STORE_FILE')) {
                storeFile file(MYAPP_UPLOAD_STORE_FILE)
                storePassword MYAPP_UPLOAD_STORE_PASSWORD
                keyAlias MYAPP_UPLOAD_KEY_ALIAS
                keyPassword MYAPP_UPLOAD_KEY_PASSWORD
            }
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true   // R8 shrink
        }
    }
}
```

---

## 📦 Stage 2 — AAB vs APK & Building

**Gist:** Play Store wants an **AAB** (Android App Bundle). Play uses it to generate per-device split APKs (ABI, density, language) and signs them with the app signing key. An **APK** is one universal file for sideloading / sharing with testers (195, 196).

**हिंदी:** Play Store को AAB चाहिए; APK सिर्फ सीधे install या testers को भेजने के लिए।

| | AAB | APK |
|---|---|---|
| Use | Upload to Play Store | Sideload / QA share |
| Content | Blueprint; Play splits per device | One universal package |
| Gradle | `bundleRelease` | `assembleRelease` |
| EAS `buildType` | `app-bundle` | `apk` |
| Base module limit | 200MB compressed (Play limit, verify in docs) | - |

```bash
# Local (bare / prebuild)
cd android && ./gradlew bundleRelease      # AAB -> app/build/outputs/bundle/release/
cd android && ./gradlew assembleRelease    # APK -> app/build/outputs/apk/release/
adb install app-release.apk                # APK onto a phone
jarsigner -verify -verbose -certs app/build/outputs/bundle/release/app-release.aab | tail -5

# Cloud (Expo, no Android SDK on your laptop)
eas build --platform android --profile production   # AAB
eas build -p android --profile preview               # APK for QA
```

- [ ] Release build, not debug (debug loads JS from Metro; release embeds Hermes bytecode) — release build ही ship करो
- [ ] JDK 17 for RN 0.73+ (check your RN version's docs) — JDK version जाँचो
- [ ] Production profile uses `app-bundle`; QA profile uses `apk` — profile अलग रखो
- [ ] Verify the AAB is signed with the upload key (`jarsigner -verify`) — signature जाँचो

---

## 🔢 Stage 3 — Versions, Config & Assets

**Gist:** `versionCode` is an integer that must always increase per upload; `versionName` is user-visible and flexible (193). Expo config lives in `app.json` / `app.config.js`; `eas.json` defines build and submit profiles (208).

**हिंदी:** हर upload पर versionCode बढ़ाना ज़रूरी है, versionName कुछ भी हो सकता है।

```json
{
  "expo": {
    "version": "2.1.0",
    "android": {
      "versionCode": 15,
      "package": "com.yourcompany.yourapp"
    }
  }
}
```

```json
{
  "cli": { "version": ">= 12.0.0", "appVersionSource": "remote" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "android": { "buildType": "apk" }
    },
    "preview": {
      "distribution": "internal",
      "android": { "buildType": "apk" }
    },
    "production": {
      "autoIncrement": true,
      "android": { "buildType": "app-bundle" }
    }
  },
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "./secrets/play-service-account.json",
        "track": "internal",
        "releaseStatus": "draft"
      }
    }
  }
}
```

- [ ] Bump `versionCode` (or `autoIncrement: true` in `eas.json`) before every upload — हर बार बढ़ाओ
- [ ] Set unique `android.package` (applicationId) — upload के बाद package name lock हो जाता है
- [ ] App icon 512×512 PNG, no alpha — alpha transparency नहीं
- [ ] Adaptive icon: foreground square and large enough; `monochromeImage` needs a recent SDK (verify) — adaptive icon जाँचो
- [ ] Splash configured via `expo-splash-screen` plugin (older SDKs used top-level `splash`) — splash सेट करो
- [ ] Declare only needed permissions; restricted ones (SMS, call log, background location) need a declaration form — बेवजह permission मत माँगो
- [ ] Target API level is recent (Google raises it yearly) — upgrade SDK if Console errors — target API level अपडेट रखो
- [ ] Secrets (service account JSON, keystore) never committed — secrets git में नहीं

---

## 🏪 Stage 4 — Play Console Setup

**Gist:** One-time $25 developer account with identity verification, then create the app, fill the App content forms, store listing, and upload the first AAB (193, 210-216).

**हिंदी:** Developer account बनाओ, app बनाओ, सारे forms भरो, फिर पहला AAB upload करो।

### Account
- [ ] Dedicated Google account/email (not personal) — अलग email रखो
- [ ] Register at play.google.com/console, pay $25 one-time (international card) — $25 एक बार
- [ ] Choose Personal or Organization; org needs D-U-N-S + website verify — account type चुनो
- [ ] Verify identity (government ID, selfie/address proof), phone SMS and Android device — verification में कई दिन लग सकते हैं

### Create app
- [ ] Create app: name (max 30 chars), default language, App/Game, **Free or Paid (free cannot become paid later)** — Free से Paid नहीं बन सकता
- [ ] Accept Developer Program Policies + US export laws — declarations accept करो

### App content forms
- [ ] Content rating (IARC questionnaire): answer honestly; redo after big changes (UGC, chat) — rating honest भरो
- [ ] Privacy Policy: public HTTPS URL; link in store listing and in-app Settings; matches Data safety form — privacy policy ज़रूरी, free app में भी
- [ ] Data safety: declare every SDK's data (email, phone, name, location, Crashlytics, analytics) — SDK का data भी declare करो
- [ ] Target audience, ads declaration, app access (give reviewer a demo login) — reviewer को test account दो
- [ ] Account-creating app: in-app account deletion + web deletion link — account deletion का तरीका दो

### Store listing
- [ ] Title (max 30), short description (max 80), full description (max 4000)
- [ ] Feature graphic 1024×500 PNG
- [ ] Screenshots: 2-8 per device type, phone minimum 2 (16:9 or 9:16)
- [ ] No fake claims, keyword stuffing or emojis in title — misleading metadata पर reject होता है

---

## 🧪 Stage 5 — Testing Tracks

**Gist:** Promote the same release through tracks instead of rebuilding (217-219). Every new upload needs a new `versionCode`.

**हिंदी:** पहले Internal, फिर Closed, फिर Open, और आखिर में Production — हर step पर testers से feedback।

```
Internal Testing  -> no review, available in minutes, up to 100 testers (email list)
Closed (Alpha)    -> limited group via email list / Google Group, goes through review
Open (Beta)       -> anyone can join; store shows "Join the beta" / Early access
Production        -> live to everyone
```

- [ ] Internal: create tester email list (Gmail IDs), upload AAB, share the opt-in link — Internal में review नहीं लगता
- [ ] Testers open the link → "Become a tester" → install from Play Store — link से join करवाओ
- [ ] Bug found → fix → new `versionCode` → new AAB — नया versionCode
- [ ] Closed: create track, choose testers + countries, send for review — Closed में review होता है
- [ ] **New personal accounts:** 12+ testers opted in for 14 continuous days, then "Apply for production" (rule changes: verify in current docs) — नियम verify करो
- [ ] Open: set countries, optional tester cap, feedback email/URL (avoids public bad reviews) — feedback email दो
- [ ] Promote release (Internal → Closed → Open → Production) once stable — "Promote release" दबाओ

```bash
# Automate upload to a track (needs Play service account key in eas.json)
eas submit --platform android
```

---

## 🚀 Stage 6 — Production & Staged Rollout

**Gist:** Pre-flight all App content tasks, create the Production release, then roll out gradually and watch vitals (220, 221).

**हिंदी:** पहले 10% users को release करो, crash देखो, फिर धीरे-धीरे 100% तक ले जाओ।

- [ ] Pre-flight green: rating, privacy, data safety, target audience, ads declaration, app access, listing — सब tasks पूरे
- [ ] Production → countries → Create new release → upload AAB (or promote) — release बनाओ
- [ ] Release name + release notes (add language tags) — notes लिखो
- [ ] Fix Console errors/warnings (target API level, permission declarations) — errors साफ़ करो
- [ ] Set rollout percentage: start at 10 — 10% से शुरू
- [ ] "Send changes for review"; optionally use managed publishing so you press Publish after approval — approval के बाद खुद publish
- [ ] Watch crash rate, ANR, ratings in the release dashboard; Firebase Crashlytics — crash/ANR देखो
- [ ] Healthy → "Update rollout" 25 → 50 → 100% — धीरे-धीरे बढ़ाओ
- [ ] Problem → "Halt rollout" → fix → new `versionCode` release (halted rollout can be resumed) — दिक्कत हो तो halt
- [ ] JS-only bug? Prefer an OTA via `eas update --branch production` (see `expo-vs-cli.md`) — JS bug पर OTA

---

## 🚫 Stage 7 — Review & Rejection Reasons

**Gist:** Automated scan (malware, permissions, API level), then human review if needed. Updates: hours to days; new apps/accounts around 7 days or more. Policy checks continue after publishing (223, 222).

**हिंदी:** Rejection email में policy का नाम होता है; fix करो, notes लिखो, दोबारा review के लिए भेजो।

| Reason | Fix |
|---|---|
| Privacy policy missing / broken | Public HTTPS URL, matches Data safety |
| Data safety mismatch | Declare every SDK's data (analytics, ads, crash) |
| Restricted permissions (SMS, call log, background location) | Remove, or fill Permissions Declaration form |
| Crashes / broken login | Test the release build; give reviewer a demo account |
| Misleading metadata | No fake claims, keyword stuffing, emojis in title |
| Payments for digital goods | Use Google Play Billing, not UPI/cards |
| Target API level too low | Upgrade Expo SDK / `targetSdkVersion` |
| Missing account deletion | In-app delete + web link |
| Impersonation / IP | Don't use others' brand names/logos |
| Families/children policy | Ads SDK must be certified if kids are targeted |
| Deceptive behaviour | No hidden features, no behaviour change after review |

- [ ] Rejection email → Console → Policy and programs → Policy status → read the exact violation — details देखो
- [ ] Fix code / listing / Console form — fix करो
- [ ] New `versionCode` if code changed; listing-only fixes just resubmit — code बदला तो नया versionCode
- [ ] Write what you fixed in "Notes for review"; Send for review again — notes में लिखो
- [ ] Wrongly rejected? Appeal with evidence; serious cases can mean suspension/removal — गलत लगे तो appeal

---

## 🧠 Quick Q&A

**Lost the upload keystore, can I still update?** Yes if enrolled in Play App Signing: the app signing key is at Google; request an upload key reset (Play Console → Setup → App signing).
हिंदी: Play App Signing में हों तो upload key reset हो सकती है।

**AAB vs APK on Play?** Upload AAB; Google builds device-specific split APKs and signs them. Sideloading APK signs with your own key.
हिंदी: Store के लिए AAB, sideload के लिए APK।

**Fastest fix after a bad release?** Halt rollout; if JS-only, push `eas update --branch production`; else new `versionCode` build.
हिंदी: Halt करो, फिर OTA या नया build।

---

## ✅ Final Pre-Submit Glance

- [ ] Signed AAB, upload key backed up
- [ ] `versionCode` bumped
- [ ] Privacy policy URL + Data safety + content rating done
- [ ] Icon 512×512, feature graphic 1024×500, 2+ screenshots
- [ ] Reviewer demo account in App access
- [ ] Internal track tested on a real device
- [ ] Staged rollout starting at 10%
