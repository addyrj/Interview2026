# React Native — Expo vs CLI
# Decision Table, Prebuild, EAS Build/Update, Dev Client, Config Plugins, OTA
# Quick Revision

> Condensed from `01-basics/` (topics 08, 09) and `11-ota-cicd/` (topics 258-267). Notes target Expo SDK 52+ (some SDK 54, RN 0.76-0.81). Check current docs — APIs change between SDKs. `eas.json` keys, EAS CLI flags, runtimeVersion policies and CI action versions change: verify against current docs (docs.expo.dev). Commands in the notes were not run.

---

## ⚖️ The Short Answer

**Gist:** Expo = a platform on top of React Native: pre-built native modules (SDK), Expo Go for instant testing, EAS cloud builds, OTA updates. CLI = the official bare setup where you own `android/` and `ios/`. For new projects (2024+) the notes default to Expo; native code is still possible via dev builds, config plugins and prebuild.

**हिंदी:** नए project के लिए Expo default रखो; native code चाहिए तो भी Expo छोड़ना ज़रूरी नहीं।

---

## 📊 Decision Table

| Situation | Pick | हिंदी |
|---|---|---|
| New app, small/medium team, fast MVP | Expo (EAS + dev builds) | तेज़ शुरुआत के लिए Expo |
| Only common features (camera, push, maps, storage) | Expo (Expo Go, then dev build) | common features = Expo |
| Need OTA updates | Expo + EAS Update | OTA के लिए EAS Update |
| No Mac on the team but need iOS builds | Expo + EAS Build (cloud Mac) | Mac नहीं तो EAS |
| Custom/private native SDK (AAR / iOS framework) | Expo + config plugin / prebuild + dev build, OR CLI | SDK के लिए plugin या CLI |
| Custom Kotlin/Swift/C++ modules | Expo dev build + local Expo module, OR CLI | custom native code |
| Brownfield (RN screens inside an existing native app) | CLI-style native integration | पुराने native app में RN |
| Very custom native build pipeline / strict internal tooling | CLI | बहुत custom pipeline |
| Large enterprise with dedicated native team | CLI | native team हो तो CLI |
| Library that only supports CLI | CLI (very rare now) | बहुत कम |
| Team not experienced with native setup | Expo | native setup से बचो |

```
                Need custom native code?
                   /              \
                 NO               YES
                 |                 |
          Expo (Expo Go,     Expo dev build + config plugin
          then dev build)         (prebuild)  or  CLI
                 |                 |
              EAS Build  ------  EAS Build / local Gradle+Xcode
```

---

## 🧱 Expo vs CLI Side by Side

| | Expo | CLI |
|---|---|---|
| Create | `npx create-expo-app@latest MyApp` | `npx @react-native-community/cli@latest init MyApp` |
| Run | `npx expo start` (press `a` / `i`, or scan QR in Expo Go) | `npx react-native run-android` / `run-ios` |
| Native folders | Generated on demand (`expo prebuild`) | Always in the repo |
| Build | `eas build --platform all` (cloud) | `./gradlew assembleRelease`; Xcode Archive |
| Submit | `eas submit` | Play Console / App Store Connect manually or Fastlane |
| OTA | `eas update` | Not built in (CodePush hosted service retired in 2025) |
| Machine for iOS | Any OS via EAS Build | Mac only (Xcode) |
| Setup time | Minutes | Notes say ~2-4 hours of environment setup |
| Native module setup | `npx expo install`, usually no Gradle/Podfile edits | Edit Gradle / Podfile / manifest / Info.plist yourself |

**हिंदी:** Expo में native setup कम, CLI में पूरा control पर मेहनत ज़्यादा।

---

## 📱 Expo Go vs Development Build

**Gist:** Expo Go is a pre-built sandbox app: scan a QR code, no build needed, but only Expo SDK modules work. A **development build** is your own app with dev tools (`developmentClient`), so any native module works (MMKV, Detox, Stripe, cert pinning, custom SDKs).

**हिंदी:** Custom native module Expo Go में नहीं चलेगा, development build बनाओ।

```bash
npx expo run:android                       # local dev build (needs native tooling)
eas build --profile development            # cloud dev build
```

- [ ] Using a custom native library? Make a dev build, never test it in Expo Go
- [ ] Gate native-only features so one codebase works in Expo Go and dev builds (see snippet)
- [ ] `distribution: "internal"` = shareable link/QR; `"store"` = for stores

---

## 🧬 Prebuild, CNG and "Eject"

**Gist:** `npx expo prebuild` generates `android/` and `ios/` from `app.json` + config plugins (Continuous Native Generation, CNG), so those folders need not be committed and can be regenerated. The notes say this replaces one-way "eject": use prebuild instead.

**हिंदी:** Eject अब ज़रूरी नहीं; prebuild से native folders कभी भी बन जाते हैं।

```bash
npx expo install react-native-vision-camera   # library with native code
npx expo prebuild                            # generate android/ ios/ from app.json
npx expo run:android                         # run with native code
npx expo prebuild --platform ios             # iOS only (Xcode flow)
```

When to prebuild / leave managed:

- [ ] Library has native code and needs config -> prebuild + dev build (or config plugin)
- [ ] Need to open Xcode / Android Studio -> prebuild
- [ ] Simple Expo SDK modules only -> stay managed, no native folders
- [ ] Brownfield or fully custom native pipeline -> consider CLI instead

---

## 🔌 Config Plugins

**Gist:** Config plugins edit native config (manifest, Info.plist, Gradle, Podfile) automatically during prebuild, so you can add native SDKs without hand-editing native files. List them in `app.json` `plugins`; Info.plist values go in `ios.infoPlist`.

**हिंदी:** Config plugin native config अपने-आप बदलता है, हाथ से edit नहीं करना पड़ता।

```json
{
  "expo": {
    "name": "FoodApp",
    "slug": "foodapp",
    "version": "2.5.0",
    "runtimeVersion": { "policy": "appVersion" },
    "plugins": ["expo-router"],
    "ios": {
      "bundleIdentifier": "com.mycompany.foodapp",
      "buildNumber": "3",
      "infoPlist": {
        "NSCameraUsageDescription": "Camera is needed to take food photos"
      }
    },
    "android": {
      "package": "com.mycompany.foodapp",
      "versionCode": 15
    }
  }
}
```

- [ ] Private payment SDK (AAR + iOS framework): write a config plugin or local Expo module that adds it during prebuild, then use a dev build / EAS Build: no rewrite in CLI needed
- [ ] Changing plugins or native config means a new binary (see OTA section)
- [ ] `app.config.js` (dynamic) when config must depend on the environment

---

## ☁️ EAS Build, Submit and `eas.json`

**Gist:** EAS = Expo Application Services: **EAS Build** (cloud builds for Android/iOS, handles signing, returns APK/AAB/IPA), **EAS Submit** (uploads to Play / App Store Connect), **EAS Update** (OTA). iOS can be built from Windows/Linux; submitting still needs an Apple Developer account.

**हिंदी:** EAS = cloud build + submit + OTA, Mac के बिना iOS build भी।

```json
{
  "cli": { "version": ">= 12.0.0", "appVersionSource": "remote" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "channel": "development",
      "android": { "buildType": "apk" }
    },
    "staging": {
      "distribution": "internal",
      "channel": "staging",
      "env": { "APP_ENV": "staging" },
      "android": { "buildType": "apk" }
    },
    "production": {
      "autoIncrement": true,
      "channel": "production",
      "env": { "APP_ENV": "production" },
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

```bash
npm install -g eas-cli && eas login
eas build:configure
eas build --platform android --profile production    # AAB
eas build --platform ios --profile production        # IPA, cloud Mac
eas submit --platform android
eas submit --platform ios --latest
eas credentials                                      # inspect / manage keystore & Apple creds
```

- [ ] `profile.channel` ties a build to an EAS Update channel (OTA)
- [ ] `autoIncrement` bumps versionCode / buildNumber per build
- [ ] CI: `EXPO_TOKEN` secret + `eas build --non-interactive`; `--auto-submit` to push to stores
- [ ] CI caveat: `--no-wait` green only means "queued", not "built"
- [ ] iOS in CI: store credentials beforehand with `eas credentials`; Android submit needs a Google Service Account key (verify against current EAS docs)
- [ ] Other CI options in the notes: GitHub Actions (`expo/expo-github-action`), Fastlane, Bitrise, Codemagic, EAS Workflows (verify tool names/prices)

---

## 📡 OTA Updates (EAS Update + expo-updates)

**Gist:** An RN app = native shell + JS bundle. OTA replaces only the JS bundle and assets, with no store review, so a fix can ship in minutes. The update only applies when its `runtimeVersion` matches the installed binary. Users usually get it on next launch.

**हिंदी:** OTA सिर्फ JS और assets बदलता है; store review नहीं लगता, पर runtimeVersion match होना चाहिए।

```bash
npm install -g eas-cli
eas update:configure                                   # adds updates config to app.json
eas update --branch production --message "fix cart discount calculation"
eas update --branch staging --message "test new home screen layout"
eas update:list
eas update:view <update-id>
# Rollback: no direct command in the notes; republish the old commit
git checkout <previous-commit>
eas update --branch production --message "rollback: cart discount fix"
```

```json
{
  "expo": {
    "version": "2.5.0",
    "runtimeVersion": { "policy": "appVersion" },
    "updates": {
      "url": "https://u.expo.dev/YOUR-PROJECT-ID",
      "checkAutomatically": "WIFI_ONLY",
      "fallbackToCacheTimeout": 0
    }
  }
}
```

| Key | Purpose |
|---|---|
| `updates.url` | `https://u.expo.dev/<projectId>` |
| `updates.checkAutomatically` | `ON_LOAD` (default), `ON_ERROR_RECOVERY`, `WIFI_ONLY`, `NEVER` |
| `updates.fallbackToCacheTimeout` | ms to wait for download at launch (0 = launch immediately) |
| `runtimeVersion` | String or `{ policy }`: `appVersion`, `nativeVersion`, `sdkVersion`, `fingerprint` (SDK 50+, verify) |

- [ ] Branches are like git branches for OTA (`production`, `staging`, `development`); each native build tracks a channel/branch
- [ ] Test on staging, verify on a real device, then promote to production
- [ ] Test OTA in a release/preview build: `Updates.isEnabled` is false in dev mode
- [ ] Automate: `eas update --branch production --non-interactive` on merge to main with `EXPO_TOKEN`
- [ ] CodePush: Microsoft's hosted service (App Center) retired 31 March 2025; for bare RN use EAS Update or a self-hosted/third-party option (verify current status)

```jsx
// Manual OTA check (expo-updates)
import React, { useState } from 'react';
import { View, Text, Button, Alert } from 'react-native';
import * as Updates from 'expo-updates';

export default function CheckUpdate() {
  const [msg, setMsg] = useState('');

  const run = async () => {
    if (!Updates.isEnabled) { setMsg('Updates disabled in dev'); return; }
    try {
      setMsg('Checking...');
      const r = await Updates.checkForUpdateAsync();
      if (!r.isAvailable) { setMsg('You are up to date'); return; }
      setMsg('Downloading...');
      await Updates.fetchUpdateAsync();
      Alert.alert('Update ready', 'Restart now?', [
        { text: 'Later', style: 'cancel' },
        { text: 'Restart', onPress: () => Updates.reloadAsync() },
      ]);
    } catch (e) {
      setMsg('Error: ' + e.message);
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <Text>Runtime: {Updates.runtimeVersion ?? 'n/a'}</Text>
      <Text>Channel: {Updates.channel ?? 'n/a'}</Text>
      <Button title="Check for update" onPress={run} />
      <Text>{msg}</Text>
    </View>
  );
}
```

**हिंदी:** Payment के बीच अचानक reload मत करो; update download करके user से Restart पूछो।

---

## 🔍 OTA or Full Build?

**OTA is enough when** the change touches only JS/TS, styles, JSON config and bundled assets, and the installed binary already has every native module the new JS needs (e.g. change offer text, fix a cart-total bug, new pure-JS screen).

**Full build required when** (OTA cannot change what is compiled into the binary):

| Trigger | Why |
|---|---|
| Add/remove/upgrade a native module (expo-camera, maps, notifications SDK) | Native code lives in the binary |
| Change permissions (AndroidManifest / Info.plist) | Declared at install time |
| Change icon, splash, adaptive icon, app name, bundle id / package | Native resources |
| Expo SDK / React Native upgrade | New native runtime |
| Change URL schemes, deep-link intent filters, associated domains | Native config |
| Add config plugins, edit entitlements (push, Apple Sign-In) | Native project changes |
| Hermes / New Architecture settings | Native build config |
| `google-services.json` / `GoogleService-Info.plist` changes | Bundled at build |
| Native crash fix | Native layer bug |

**हिंदी:** JS बदला तो OTA, native बदला तो नया build और store release।

Full-build flow:

- [ ] Identify the trigger from the table
- [ ] Bump `version` (+ `buildNumber` / `versionCode`) and `runtimeVersion` if needed
- [ ] `eas build --platform all --profile production`
- [ ] Test on devices (preview / internal testing)
- [ ] `eas submit` to Play Console / App Store Connect
- [ ] After rollout, publish OTAs against the NEW runtimeVersion only

```bash
# @expo/fingerprint hashes native-relevant project state (SDK 50+ policy "fingerprint" uses it)
npx @expo/fingerprint . > fingerprint.json
npx @expo/fingerprint diff old-fingerprint.json fingerprint.json   # same hash: OTA safe; different: build needed
```

Verify subcommand names and flags in current `@expo/fingerprint` docs; the notes did not run this. A CI guard can also flag changed `ios/`, `android/`, `app.json`/`app.config.*`, `package.json` and lockfiles, but that is only a heuristic: `package.json` changes can be JS-only deps, so a human review (or fingerprint) decides.

Store-policy caution from the iOS notes: hot-patching that changes the app's purpose conflicts with guideline 2.5.2 (verify current wording).

---

## 🧠 Quick Q&A

**Can I build iOS without a Mac?** Yes, with EAS Build (`eas build --platform ios`); you still need an Apple Developer account to submit.
हिंदी: EAS Build से Mac के बिना iOS build।

**Does Expo support any npm native library?** Yes with a development build and, if needed, a config plugin. Not inside Expo Go.
हिंदी: dev build + config plugin से हाँ।

**When is CLI still better?** Brownfield apps, heavy custom native build setups, strict internal tooling.
हिंदी: Brownfield या बहुत custom native pipeline में CLI।

**What is CNG?** `android/` and `ios/` are generated from `app.json` + config plugins by `expo prebuild`, so they need not be committed.
हिंदी: native folders config से बनते हैं।

**What stops an OTA update from applying?** `runtimeVersion` mismatch with the installed binary (e.g. update needs a new native module).
हिंदी: runtimeVersion match न हो तो update नहीं लगता।

**Expo apps are "not real" apps?** Wrong: Expo apps ship on both stores and Expo docs recommend it as the default way to start.
हिंदी: Expo app production में जाते हैं।
