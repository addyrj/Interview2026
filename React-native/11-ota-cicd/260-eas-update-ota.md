# 260. EAS Update — OTA Updates
# हिंदी में: EAS Update — Over-The-Air Updates
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**EAS Update** (Over-The-Air / OTA Update) lets you push JavaScript bundle changes to users **without going through Play Store or App Store review**. Users get the update silently on next app launch. Only JS/assets changes (no native code). A critical production tool: fix a bug in 5 minutes instead of waiting 1-7 days for store review.

## 🔵 सरल परिभाषा (Hindi)
**EAS Update** (OTA Update) JavaScript bundle changes users तक **Play Store/App Store review के बिना** push करने देता है। अगले app launch पर users को update silently मिल जाती है। सिर्फ JS/assets changes (no native code)। Production में critical tool: bug 5 minutes में fix करो, store review के 1-7 days नहीं।

---

## 🔴 Problem it Solves
```
WITHOUT OTA UPDATES:
  Bug found in production at 2 PM
  → Fix code (30 min)
  → Build new AAB/IPA (20 min)
  → Submit to Play Store / App Store
  → Wait for review: Android 1-3 hours, iOS 1-3 days
  → Users on broken version for hours/days

WITH EAS UPDATE (OTA):
  Bug found at 2 PM
  → Fix code (30 min)
  → eas update --branch production --message "fix cart crash"  (2 min)
  → Users get update on next app launch (minutes later)
  Total: ~35 minutes vs potentially days!

WHAT CAN BE OTA UPDATED:
  ✅ JavaScript/TypeScript code
  ✅ React components and business logic
  ✅ Images, fonts, JSON files (assets)
  ✅ API endpoint URLs
  ✅ Feature flags, UI copy

WHAT CANNOT BE OTA UPDATED:
  ❌ Native code (Kotlin/Swift/C++)
  ❌ New native dependencies (pods, gradle packages)
  ❌ App permissions (AndroidManifest, Info.plist)
  ❌ App icon, splash screen (native assets)
  ❌ SDK upgrades (new Expo SDK version)
```

---

## 🟢 How It Works — Step by Step

```
EAS UPDATE FLOW:
──────────────────────────────────────────────────────
  DEVELOPER SIDE:
  1. Fix bug in JavaScript code
  2. Run: eas update --branch production
  3. EAS: bundles new JS → uploads to Expo CDN
  4. Update stored with: branch, runtime version, message

  USER SIDE (next app launch):
  1. App launches → checks EAS servers for updates
  2. EAS: "New update available for your runtime version"
  3. App downloads new JS bundle (background or foreground)
  4. On next app restart: new bundle is active
  (OR: immediately if configured with expo-updates)

  RUNTIME VERSION MATCHING:
  Runtime version = your app's native code version
  Update applies only if: update's runtimeVersion == app's runtimeVersion
  → Prevents JS-only update from running on incompatible native code
  → Example: update requires new native module → won't apply to old app

  BRANCHES:
  Like git branches for your OTA updates
  production → live app users
  staging → TestFlight / internal testers
  development → dev builds
  Rule: each native build tracks a branch
```

---

## 🟡 Real World Example
**Myntra flash sale bug:** 3 PM sale starts, cart discount not applying correctly. 2 million users shopping. Fix: one line of JavaScript. `eas update --branch production --message "fix sale discount calc"`. 3 minutes later, new bundle on CDN. Users launching app from 3:05 PM onwards get correct discount. Without OTA: 8+ hours before store review passes, sale is over. OTA updates save real revenue for e-commerce apps.

---

## 💻 Code Example

```bash
# ─── SETUP ──────────────────────────────────────────────────────────────────
# 1. Install EAS CLI
npm install -g eas-cli

# 2. Login
eas login

# 3. Configure project (app.json)
eas update:configure
# → adds "updates" config to app.json

# ─── app.json / app.config.js ────────────────────────────────────────────────
{
  "expo": {
    "name": "MyApp",
    "runtimeVersion": {
      "policy": "sdkVersion"   // runtime version = Expo SDK version
      // OR: "appVersion"     // = your app's version number
      // OR: "nativeVersion"  // = custom (most control)
    },
    "updates": {
      "url": "https://u.expo.dev/your-project-id",
      "enabled": true,
      "checkAutomatically": "ON_LOAD",          // check on every launch
      "fallbackToCacheTimeout": 0               // don't wait; use cache immediately
    }
  }
}
```

```bash
# ─── PUBLISHING AN UPDATE ────────────────────────────────────────────────────
# Publish to 'production' branch
eas update --branch production --message "fix cart discount calculation"

# Publish to specific channel with preview
eas update --branch staging --message "test new home screen layout"

# List recent updates
eas update:list

# View details of a specific update
eas update:view <update-id>

# Rollback: re-publish the previous bundle
# (EAS doesn't have a direct rollback command — republish old commit)
git checkout <previous-commit>
eas update --branch production --message "rollback: cart discount fix"
```

```tsx
// ─── MANUAL UPDATE CHECK (in-app) ────────────────────────────────────────────
import * as Updates from 'expo-updates';
import { useEffect, useState } from 'react';
import { Alert } from 'react-native';

export function useOTAUpdate() {
  const [updateAvailable, setUpdateAvailable] = useState(false);

  useEffect(() => {
    // Only check in production (not development)
    if (__DEV__) return;

    async function checkForUpdate() {
      try {
        const update = await Updates.checkForUpdateAsync();

        if (update.isAvailable) {
          // Download the update
          await Updates.fetchUpdateAsync();
          setUpdateAvailable(true);

          // Prompt user to restart (for critical updates)
          Alert.alert(
            'Update Available',
            'A new version has been downloaded. Restart to apply?',
            [
              { text: 'Later', style: 'cancel' },
              {
                text: 'Restart Now',
                onPress: () => Updates.reloadAsync(),  // applies the update
              },
            ]
          );
        }
      } catch (error) {
        // Silent fail — user continues with current version
        console.warn('OTA check failed:', error);
      }
    }

    checkForUpdate();
  }, []);

  return { updateAvailable };
}

// USAGE in App.tsx:
// useOTAUpdate();   // checks on mount, prompts if update available
```

```yaml
# ─── CI/CD: AUTO-DEPLOY ON MERGE TO MAIN ─────────────────────────────────────
# .github/workflows/ota-update.yml
name: OTA Update on Main

on:
  push:
    branches: [ main ]

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Install EAS CLI
        run: npm install -g eas-cli

      - name: Publish OTA Update
        env:
          EXPO_TOKEN: ${{ secrets.EXPO_TOKEN }}  # from Expo dashboard → access tokens
        run: |
          eas update \
            --branch production \
            --message "Auto deploy: ${{ github.event.head_commit.message }}" \
            --non-interactive
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| OTA speed | Same | Same |
| Store policy | Google allows OTA | Apple allows OTA (JS-only, same functionality) |
| Silent update | ✅ | ✅ |
| Forced update | Possible (reload immediately) | Same |

**Important iOS note:** Apple allows OTA JS-only updates. You cannot use OTA to add new features that weren't in the original App Store review. Changing core functionality bypasses Apple's review = guideline violation. OTA is for bug fixes and minor improvements.

---

## 🟠 Expo vs CLI Difference

EAS Update is an Expo service:
```bash
# Expo projects: built-in expo-updates package
npx expo install expo-updates

# CLI (bare React Native): can still use EAS Update
npm install expo-modules-core expo-updates
# Extra setup needed: AppDelegate.mm changes, MainActivity changes
# Easier to use with Expo managed/bare workflow
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** OTA-updating native code changes
```
WRONG: Added react-native-camera (new native dependency)
       → pushed eas update thinking it works
RESULT: App crashes on launch (JS expects native module, doesn't exist)
CORRECT: Native changes = always need new store build (eas build + submit)
Rule: Did you run pod install or change build.gradle? → Store build, not OTA.
```

❌ **Mistake 2:** Mismatched runtime versions
```
SCENARIO: Production app runtimeVersion="1.0.0"
          New update published with runtimeVersion="2.0.0"
RESULT: Update is ignored by old app (version mismatch — intentional!)
CORRECT: OTA update's runtimeVersion must match the installed app's build
When you release a new native build → update the runtimeVersion
Then future OTA updates use the new runtimeVersion
```

❌ **Mistake 3:** Not testing the update before pushing to production
```
WRONG: Fix on main → eas update --branch production immediately
CORRECT:
  1. eas update --branch staging
  2. Test on TestFlight / internal build
  3. eas update --branch production (after validation)
  Consider: --rollout percentage for gradual rollouts
```

---

## 🧠 Tricky Interview Question

**Q: A user has your app version 2.0.0 installed from 6 months ago. You've pushed 15 OTA updates since then. What happens when they open the app?**

**Answer:** They get the **latest OTA update** for their runtime version (version 2.0.0), not all 15 sequentially. EAS Update is not incremental — each update is a complete JS bundle. The app downloads the latest bundle in their channel/branch that matches their `runtimeVersion`. There's no "update chain" to walk through. However: if you released a new native build (version 2.1.0) with a new `runtimeVersion` between then and now, OTA updates published for version 2.1.0 won't apply to their old 2.0.0 install — those updates have a different `runtimeVersion`. The user would need to update through the store to get those changes.

---

## ⚫ Interview Questions + Answers

**Q1: What is OTA update and how does EAS Update work?**
A1: OTA (Over-The-Air) update pushes a new JavaScript bundle to users without requiring a new store submission. EAS Update: developer runs `eas update --branch production`, EAS bundles the JS, uploads to CDN. On the user's next app launch, the app checks for updates, downloads the new bundle, and applies it on next restart. No App Store/Play Store involvement for JS-only changes.

**Q2: What CANNOT be updated via OTA?**
A2: Anything that requires native compilation: new native dependencies (pods/gradle packages), changes to AndroidManifest.xml or Info.plist (permissions, deep link schemes), native code (Kotlin/Swift/C++), app icon, splash screen, SDK major version upgrades. Rule: if you had to run `pod install` or change `build.gradle` → it's a native change requiring a full store build.

**Q3: What is a "runtime version" in EAS Update?**
A3: Runtime version identifies which native build an OTA update is compatible with. An update will only apply if its `runtimeVersion` matches the installed app's `runtimeVersion`. This prevents a JS bundle from running on an incompatible native layer (e.g., a JS bundle that calls a native module that doesn't exist in the old build). Policies: `sdkVersion` (auto from Expo SDK), `appVersion` (your version string), or a custom string.

**Q4: What are EAS Update branches?**
A4: Branches are named channels that your app build tracks. Similar to git branches. A production build tracks the `production` branch; a staging build tracks `staging`. When you run `eas update --branch production`, only users on production builds receive it. Allows separate update streams for different user groups. Use `eas channel:list` to see all channels and which build profiles point to them.

**Q5: Can you use OTA updates with a vanilla React Native CLI project (no Expo)?**
A5: Yes, with additional setup. Install `expo-updates` and `expo-modules-core`, configure AppDelegate and MainActivity, update metro config. Alternatively: use CodePush (Microsoft/App Center) — another OTA solution for bare React Native projects that doesn't require Expo toolchain. Both work similarly: push JS bundle to CDN, app checks on launch and applies. EAS Update is simpler for Expo projects; CodePush works better in fully native-integrated projects.

---

## 📊 Visual Diagram

```
EAS UPDATE FLOW:
──────────────────────────────────────────────────────

  DEVELOPER:
  Fix bug → git commit → eas update --branch production
                          │
                          ▼
                    EAS Servers (Expo CDN)
                    Stores: JS bundle + metadata
                    Key: {branch: "production",
                          runtimeVersion: "1.0.0",
                          updateId: "abc123"}

  USER'S DEVICE:
  App launches:
  ┌─────────────────────────────────────────────────┐
  │ 1. Check: GET https://u.expo.dev/<project-id>   │
  │    → "Any updates for runtime v1.0.0/production?"│
  │                                                 │
  │ 2. Download new bundle (background)             │
  │                                                 │
  │ 3. On next app restart:                         │
  │    Uses new bundle → bug is fixed!              │
  └─────────────────────────────────────────────────┘

OTA vs STORE BUILD — Decision:
  ┌─────────────────────────────────────────────────┐
  │ Changed JS/TS code, images, fonts, JSON?        │
  │ → OTA update (eas update)                       │
  │                                                 │
  │ Added native dependency? Changed native config? │
  │ Updated Expo SDK major version?                 │
  │ → Store build (eas build + eas submit)          │
  └─────────────────────────────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OTA Update | Over-The-Air update (no store) | Store के बिना update |
| eas update | CLI command to push JS bundle | JS bundle push करने का command |
| branch | Named channel for updates | Updates के लिए named channel |
| runtimeVersion | Native compatibility version | Native compatibility version |
| expo-updates | Package that checks/applies updates | Updates check/apply करने वाला package |
| Updates.reloadAsync() | Restart app to apply update | Update apply करने के लिए restart |
| rollback | Re-deploy previous bundle | Previous bundle फिर deploy करना |
| non-interactive | CI/CD flag (no prompts) | CI/CD के लिए flag |

---

## ⚡ 3-Line Summary
**English:**
1. EAS Update pushes JS bundle changes to users without store review — fix bugs in minutes instead of days; only JS/assets can be updated, not native code.
2. Updates are branch-based: `eas update --branch production` reaches production users; runtime versions must match for an update to apply.
3. In CI/CD: automate with `eas update --branch production --non-interactive` on every merge to main using `EXPO_TOKEN` secret.

**Hindi:**
1. EAS Update store review के बिना JS bundle changes push — bugs minutes में fix, days नहीं। सिर्फ JS/assets update होते हैं, native code नहीं।
2. Branch-based: `eas update --branch production` → production users। Runtime versions match होने चाहिए।
3. CI/CD में: `eas update --branch production --non-interactive` को main merge पर automate करो `EXPO_TOKEN` secret से।

---

## ➡️ Next Topic
**261. GitHub Actions CI/CD for React Native** — Automated builds, tests, and deployments।
