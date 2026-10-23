# M17. OTA Updates (EAS Update / CodePush)
# हिंदी में: OTA (Over-The-Air) Updates — React Native ऐप का JavaScript bundle और assets बिना app store release के सीधे यूज़र्स के फ़ोन पर update करना; पर सिर्फ़ तब जब native हिस्सा न बदला हो

---

## 🔵 Simple Definition (English)
A React Native app = a **native binary** (Swift/Kotlin code, native libraries, permissions, app icon), shipped through the stores, **plus a JavaScript bundle + assets** that the binary loads at runtime.
**OTA updates** download a **new JS bundle and assets** from your update server and run them on the next launch (or immediately), **without an app-store release**.
- **EAS Update (Expo)**: the main hosted service, with channels/branches, runtime versions, rollouts, rollbacks and code signing. It works for Expo and bare RN apps via `expo-updates`.
- **CodePush (Microsoft App Center)**: was the classic option, but **App Center was retired on March 31, 2025**. Teams moved to EAS Update or self-hosted alternatives (open-source code-push-server forks, hot-updater, Revopush and others).
**Key constraint, compatibility**: an OTA update can only contain JS/asset changes that work with the **native code already installed**. If you add a native module, change permissions or upgrade RN, you need a **new store build** and a new **runtime version**.

## 🔵 सरल परिभाषा (Hindi)
React Native ऐप = native binary (Swift/Kotlin, native libraries, permissions, icon — store से आता है) + JavaScript bundle और assets (जो binary चलाते समय लोड करती है)।
OTA update = नया JS bundle और assets अपने update server से download करके अगली बार खुलने पर (या तुरंत) चलाना — store release के बिना। EAS Update (Expo) मुख्य सेवा; Microsoft CodePush (App Center) 31 मार्च 2025 को बंद हो गया। शर्त: OTA में सिर्फ़ वही JS बदलाव जो पहले से installed native code के साथ चलें — native module जोड़ा, permission या RN version बदला तो नया store build और नया runtime version।

---

## 🔴 Problem it Solves
Store releases are slow and leaky:
- **Review delays** (hours to days), then **slow adoption**: after a week, a large share of users may still be on the old version.
- A **critical bug** (checkout button broken, a crash on a popular screen, a wrong price calculation) can't wait days during a sale (Big Billion Days, IPL final, Diwali).
- **Copy, layout and config tweaks** don't justify a full binary release.
- **Experiments** need fast iteration.
OTA lets RN teams **hotfix in minutes and roll out gradually**, reaching even users who never update from the store, as long as the change is JS-only.

## 🔴 यह क्यों बना? (Hindi)
Store release धीमी: review में घंटे-दिन, फिर यूज़र देर से update करते हैं — एक हफ़्ते बाद भी बहुत से पुराने version पर। Big Billion Days, IPL final या दिवाली के समय checkout का bug या crash दिनों तक इंतज़ार नहीं कर सकता; छोटे text/layout बदलाव के लिए पूरा release बेकार।
OTA से RN टीम मिनटों में hotfix और धीरे-धीरे rollout कर सकती है — store से update न करने वालों तक भी, बशर्ते बदलाव सिर्फ़ JS का हो।

---

## 🟢 How it Works — Step by Step

### Architecture

```
Developer: eas update --channel production --message "Fix coupon rounding"
   → bundles JS + assets → uploads to update server/CDN, tagged with RUNTIME VERSION + channel/branch
                                         │
App (binary with expo-updates, runtimeVersion "5.12.0" or fingerprint "a91f…")
   launch → (optionally) check server: "any update for channel=production & runtime=5.12.0?"
          → download manifest + changed assets (in background)
          → apply: next cold start (default, safest) OR Updates.reloadAsync() now (critical fixes)
   fallback: if new update crashes on launch repeatedly → roll back to previous / embedded bundle
```

### Runtime version = the compatibility contract

```
Native binary built with runtimeVersion R
OTA updates published for R run ONLY on binaries with R
Policies (Expo):
  "appVersion"  → R = 5.12.0 → bump app version when native code changes
  "fingerprint" → R = hash of native project files/deps → automatically changes when native changes ⭐
Native change (new native lib, permission, RN/Expo SDK upgrade, config plugin) → new binary + new R
JS-only change (bug fix, UI tweak, copy, logic, new screen using existing native modules) → OTA OK
Mismatch danger: JS calling a native module that doesn't exist in the installed binary → crash
```

### Rollout strategy

```
Channels:   production / staging / preview (per build profile); branches map to channels
Staged rollout: publish to 5% → watch crash-free rate & key metrics (Sentry tagged with updateId) →
                25% → 100%; or roll back by republishing the previous update
Critical update: flag in update metadata → app reloads immediately with a gentle prompt
Check strategy: on launch (with timeout, don't block startup), background download, apply next launch
Code signing: sign updates; app verifies signature → prevents malicious bundles if CDN compromised
```

### Store policy

```
Apple (App Review Guidelines 2.5.2 / 3.3.1(B) context): downloaded interpreted code is allowed if it doesn't
  change the app's primary purpose, add new major features bypassing review, or create a storefront
  for other code. Use OTA for fixes & incremental improvements, not to sneak in features review would reject.
Google Play: similar — updates outside Play must not change core functionality deceptively; no
  downloading executable native code (dex/so) — JS bundles via RN frameworks are standard practice
```

### What OTA cannot fix

```
✗ Native crashes (Swift/Kotlin/C++), native module bugs, OS permission changes
✗ App icon, splash (native part), push entitlements, deep link domains
✗ Users who never open the app (they get it on next launch)
✗ RN/Expo SDK upgrades → need store release
```

## 🟢 कैसे काम करता है? (Hindi)
1. Developer `eas update` चलाता है → JS + assets bundle बनकर server/CDN पर, runtime version और channel के साथ; ऐप (expo-updates) खुलते समय जाँचता है, पीछे से download करता है, और अगले cold start पर (सबसे सुरक्षित) या तुरंत reload से लागू करता है।
2. Runtime version = compatibility का वादा: उसी runtime वाले binary पर ही update चलेगा; "fingerprint" policy native बदलने पर अपने-आप runtime बदल देती है; JS ऐसा native module बुलाए जो installed binary में नहीं → crash।
3. Rollout: पहले 5%, Sentry में updateId से crash-free और metrics देखो, फिर 25%, 100%; गड़बड़ हो तो पिछला update दोबारा publish (rollback); ज़रूरी fix पर तुरंत reload।
4. Update को sign करो ताकि CDN हैक होने पर भी नक़ली bundle न चले; launch पर जाँच timeout के साथ, startup न रुके; बार-बार crash हो तो पुराने/embedded bundle पर वापस।
5. Store नियम: OTA से fixes और छोटे सुधार ठीक, पर ऐप का मूल उद्देश्य या review से बचने वाले बड़े features नहीं; native crash, permissions, icon, RN upgrade OTA से ठीक नहीं होते।

---

## 🟡 Real World Example

**Microsoft CodePush retirement (2025)** — App Center, including CodePush, was retired on March 31, 2025. Many RN teams migrated to EAS Update or self-hosted servers, which shows the risk of depending on a single OTA vendor.

**Expo EAS Update** — used by many production RN apps to ship hotfixes within minutes, with runtime-version safety, channel-based staging (QA builds on staging, users on production) and rollbacks.

**Sale-day hotfixes** — Indian e-commerce and food apps on RN face events like Big Billion Days and IPL. An OTA hotfix lets them fix a JS bug (wrong coupon logic, broken banner deep link) the same day, instead of waiting for store review while traffic peaks.

**Microsoft (Office/Teams on RN), Shopify** — large RN users run their own release pipelines combining store releases for native changes with JS updates for rapid fixes, gated by monitoring.

## 🟡 Real Example Hindi में
Microsoft का App Center (CodePush सहित) 31 मार्च 2025 को बंद हुआ — कई RN टीमें EAS Update या अपने server पर गईं; सबक: एक ही OTA vendor पर पूरी निर्भरता ख़तरनाक।
Big Billion Days या IPL जैसे दिनों में RN वाले भारतीय ऐप JS bug (ग़लत coupon logic, टूटा banner link) उसी दिन OTA से ठीक कर सकते हैं, store review का इंतज़ार किए बिना।

---

## 🟠 My Stack Example

### app.json / app.config: updates + runtime policy + code signing
```json
{ "expo": {
  "runtimeVersion": { "policy": "fingerprint" },
  "updates": {
    "url": "https://u.expo.dev/your-project-id",
    "checkAutomatically": "ON_LOAD",
    "fallbackToCacheTimeout": 0,                         // don't block launch waiting for update
    "codeSigningCertificate": "./certs/certificate.pem",
    "codeSigningMetadata": { "keyid": "main", "alg": "rsa-v1_5-sha256" }
  } } }
```
```json
// eas.json — build profiles map to update channels
{ "build": {
    "production": { "channel": "production", "autoIncrement": true },
    "preview":    { "channel": "staging", "distribution": "internal" } } }
```

### Publish, roll out gradually, roll back
```bash
# Hotfix JS-only bug to staging first
eas update --channel staging --message "Fix coupon rounding for ₹ values"
# After QA: publish to production for 10% of users
eas update --channel production --message "Fix coupon rounding" --rollout-percentage 10
# Increase rollout after monitoring (or roll back to the previous update)
eas update:edit            # adjust rollout percentage
eas update:rollback        # republish previous update / embedded bundle for the channel
```

### In-app update handling (check, download, apply safely)
```ts
import * as Updates from 'expo-updates';

export async function checkForOtaUpdate() {
  if (__DEV__ || !Updates.isEnabled) return;
  try {
    const res = await Updates.checkForUpdateAsync();
    if (!res.isAvailable) return;
    const fetched = await Updates.fetchUpdateAsync();                 // download in background
    // convention: set `extra.critical: true` in app config for that publish
    const critical = (fetched.manifest as any)?.extra?.expoClient?.extra?.critical === true;
    if (critical) {
      showToast('Applying an important fix…');
      await Updates.reloadAsync();                                    // restart JS now
    }                                                                 // else applied on next cold start
  } catch (e) { Sentry.captureException(e); }
}

// Tag errors with the running update so dashboards can compare versions
Sentry.setTag('updateId', Updates.updateId ?? 'embedded');
Sentry.setTag('runtimeVersion', Updates.runtimeVersion ?? 'unknown');
```

### Hook into lifecycle without hurting startup
```ts
// After first screen renders (M03), not during splash
InteractionManager.runAfterInteractions(checkForOtaUpdate);
AppState.addEventListener('change', (s) => s === 'active' && checkForOtaUpdate());   // throttle to e.g. every 30 min
```

### CI: publish OTA on merge to release branch (GitHub Actions)
```yaml
name: ota-update
on: { push: { branches: [release/*] } }
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - uses: expo/expo-github-action@v8
        with: { eas-version: latest, token: '${{ secrets.EXPO_TOKEN }}' }
      - run: npm ci && npm test
      - run: eas update --channel staging --message "${{ github.event.head_commit.message }}" --non-interactive
```

### Decision checklist before an OTA
```
[ ] Change is JS/assets only (no new native deps, permissions, config plugins)?
[ ] Fingerprint/runtime unchanged (eas fingerprint:compare)?
[ ] Tested on staging channel with a production-like build?
[ ] Rollout % chosen + monitoring dashboard (crash-free by updateId) ready?
[ ] Rollback command ready? Store-policy compliant (fix/improvement, not a new major feature)?
```

---

## ⚫ Interview Questions + Answers

**Q1: What can and can't be updated over the air in React Native?**
A1: OTA can update the JavaScript bundle and bundled assets: bug fixes, UI changes, copy, business logic, new screens using existing native modules, and images and fonts in the bundle. It can't change native code (Swift, Kotlin, C++), native dependencies, React Native or Expo SDK versions, permissions and entitlements, the app icon or native splash, deep-link domain config, or anything in the native project. Those require a new store build with a new runtime version.

**Q2: How do you prevent an OTA update from crashing incompatible app binaries?**
A2: Use runtime versions as a compatibility contract. Each binary is built with a runtime version (ideally a fingerprint hash of the native layer) and updates are published for that runtime only, so they're served only to compatible binaries. Native changes automatically produce a new fingerprint and require a store release. Add pre-publish checks that compare fingerprints, test on a staging channel with release builds, and rely on expo-updates' crash recovery, which falls back to the previous or embedded bundle if a new update fails at launch.

**Q3: How would you roll out an OTA hotfix safely?**
A3: Publish to a staging channel and verify on internal builds. Then publish to production with a small rollout percentage. Monitor crash-free sessions, errors and key business metrics segmented by update ID, then expand gradually to 100%. Keep a rollback ready (republish the previous update). Apply on next launch by default, and force an immediate reload only for critical fixes. Sign updates so the app verifies authenticity, and keep update checks from blocking startup.

**Q4: Are OTA updates allowed by Apple and Google?**
A4: Generally yes, for interpreted code like React Native JS bundles, provided updates don't change the app's primary purpose, add significant features that bypass review, or create a storefront or platform for other code. They must also comply with all other policies. Use OTA for bug fixes and incremental improvements, and ship major features through store releases. Downloading executable native code is prohibited. Keep release notes and an audit trail.

**Q5: What are the risks of relying heavily on OTA updates?**
A5: Compatibility mistakes can crash apps (a JS bundle calling missing native modules) without runtime-version discipline. Bad updates reach users fast without staged rollouts and monitoring. Dependence on the OTA vendor is a risk (CodePush's retirement forced migrations). Security depends on update integrity (use code signing and HTTPS). Policy violations are possible if OTA is used to bypass review, and debugging is harder with multiple JS versions on the same binary. Mitigate with fingerprints, staging channels, gradual rollouts, update-tagged telemetry, signing and clear policies on what goes OTA versus store.

---

## 🔷 Trade-offs
✅ Minutes-to-fix for JS bugs, reaches non-updating users — ❌ JS-only; native issues still need store releases.
✅ Staged rollouts & instant rollback — ❌ more versions in the wild (binary × update) to support/debug.
✅ Hosted EAS Update: easy — ❌ vendor dependency & cost; self-hosting: control — ❌ ops burden.
✅ Immediate reload for critical fixes — ❌ disrupts user session; prefer next-launch apply.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OTA update | Update JS without store | store के बिना update |
| JS bundle | Compiled app JavaScript | ऐप का JS पैकेट |
| Native binary | Store-installed app code | store से आया ऐप |
| Runtime version | Compatibility key binary↔update | संगतता की चाबी |
| Fingerprint | Hash of native layer | native हिस्से का hash |
| Channel / branch | Update stream (prod/staging) | update की धारा |
| Rollout percentage | Share of users getting update | कितने % को update |
| Rollback | Revert to previous update | पिछले update पर लौटना |
| Code signing | Verify update authenticity | update असली है जाँच |
| Embedded bundle | JS shipped inside binary | binary के अंदर का JS |

---

## ⚡ 3-Line Summary
**English:**
1. OTA updates replace the JS bundle/assets without store releases (EAS Update; CodePush retired 2025) — only for changes compatible with installed native code.
2. Runtime versions (fingerprint policy) gate compatibility; channels, staged rollout %, code signing and rollback make it safe.
3. Apply on next launch by default, reload for critical fixes, tag telemetry with updateId, follow store policy (fixes, not major features), ship native changes via stores.

**Hindi:**
1. OTA से JS bundle/assets बिना store के बदलते हैं (EAS Update; CodePush 2025 में बंद) — सिर्फ़ installed native code के साथ चलने वाले बदलाव।
2. Runtime version (fingerprint) से संगतता; channels, धीरे-धीरे rollout, signing और rollback से सुरक्षा।
3. आम तौर पर अगली बार खुलने पर लागू, ज़रूरी fix पर reload; updateId से निगरानी; store नियम मानो; native बदलाव store से।

---

## ➡️ Next Topic Suggestion
**M18. App Release, Versioning + Force Update** — OTA complements, but doesn't replace, store releases. Next: version numbers, release trains, staged rollouts on Play and the App Store, hotfix processes, and force-update strategies.
