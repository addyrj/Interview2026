# M18. App Release, Versioning + Force Update
# हिंदी में: App Release, Versioning + Force Update — mobile ऐप को Play Store / App Store पर सुरक्षित तरीके से कैसे release करें: version नंबर, नियमित release train, testing tracks, धीरे-धीरे rollout, hotfix, और बहुत पुराने versions को ज़बरदस्ती update करवाना

---

## 🔵 Simple Definition (English)
Mobile releases go through **app stores**, so you need a disciplined process:
- **Versioning**: a user-visible **version** (iOS `CFBundleShortVersionString`, Android `versionName`, e.g., `5.14.0`, semver-style) plus a monotonically increasing **build number** (iOS `CFBundleVersion`, Android `versionCode`, e.g., `51400` or auto-incremented).
- **Release cadence**: a **release train** (e.g., weekly or bi-weekly code freeze → QA → submit), with **feature flags** decoupling *deploying code* from *releasing features*.
- **Testing tracks**: TestFlight (internal/external) on iOS; Play **internal → closed → open testing** on Android; dogfooding by employees.
- **Staged rollout**: Play **percentage rollout** (halt/resume/increase) and App Store **phased release** (7-day automatic ramp: 1% → 2% → 5% → 10% → 20% → 50% → 100%, pausable).
- **Hotfix process**: release branch, cherry-pick, **expedited review** (Apple) if critical, OTA for JS-only fixes (M17).
- **Update enforcement**: **soft update** prompts, **force update** (blocking) for unsupported versions via remote config plus a server-side `426` (M09), and Google Play **In-App Updates API** (flexible/immediate).

## 🔵 सरल परिभाषा (Hindi)
Mobile release app store से होती है, इसलिए अनुशासन चाहिए: version (दिखने वाला 5.14.0) + build number (हर build पर बढ़ता); नियमित release train (हर हफ़्ते/दो हफ़्ते — code freeze → QA → submit) और feature flags (code deploy अलग, feature चालू करना अलग); testing tracks (TestFlight, Play internal/closed/open); धीरे-धीरे rollout (Play में %, App Store में 7 दिन का phased release); hotfix का तरीका; और पुराने versions के लिए soft/force update।

---

## 🔴 Problem it Solves
Unlike web deploys, a bad mobile release **can't be instantly rolled back**. Users who updated keep the broken binary until you ship another version, which takes review time again. Without process:
- A crash on one Android OEM reaches **100% of users** at once.
- Ad-hoc releases mean **unpredictable quality**, merge chaos and missed store review windows before big events.
- **Version number confusion** breaks analytics, crash grouping and force-update logic (strings compared wrongly: "5.10" < "5.9"?).
- **Very old versions** (2 years old) hit APIs that no longer exist, or have security holes, with no way to move users off.
- Teams wait on each other ("my feature isn't ready, delay the release").
A release process gives **predictability, safety (staged rollout + monitoring) and control over the version long tail**.

## 🔴 यह क्यों बना? (Hindi)
Web की तरह mobile release तुरंत वापस नहीं ले सकते — ख़राब binary update करने वालों के पास रहती है जब तक नया version (फिर review) न आए। बिना प्रक्रिया के: किसी एक Android कंपनी के फ़ोन पर crash एक साथ 100% यूज़र्स तक; मनमर्ज़ी की releases से गुणवत्ता अनिश्चित; version नंबर की गड़बड़ ("5.10" < "5.9"?) से analytics और force update टूटे; 2 साल पुराने versions ख़त्म हो चुके APIs या security holes के साथ; टीमें एक-दूसरे का इंतज़ार करें।
Release प्रक्रिया = अनुमान लगाने लायक, सुरक्षित (धीरे rollout + निगरानी) और पुराने versions पर नियंत्रण।

---

## 🟢 How it Works — Step by Step

### Versioning scheme

```
Version (user-visible): MAJOR.MINOR.PATCH → 5.14.0
   MINOR bump each train release (weekly 5.14 → 5.15), PATCH for hotfixes (5.14.1)
Build number (store-unique, always increasing): Android versionCode int (max 2,100,000,000)
   e.g., versionCode = 5*1_000_000 + 14*1_000 + 1*10 + build → or CI auto-increment (EAS autoIncrement)
Compare versions with SEMVER logic, never string comparison
Send both to backend & analytics: X-App-Version: 5.14.1, X-App-Build: 5014013, X-Platform: android
OTA updates (RN) add a third dimension: updateId per runtime (M17)
```

### Release train (example weekly cadence)

```
Mon            Tue–Wed               Thu                    Fri → next week
──────────     ────────────────      ───────────────────    ─────────────────────────────────
Branch cut     QA regression on      Submit to stores;      Staged rollout ramps; monitor;
release/5.15   release builds;       internal + beta        hotfix branch if needed;
(code freeze   dogfood (employees)   tracks updated         main continues with 5.16 work
 for 5.15)     fix-only cherry-picks
Rules: features not ready ship DARK behind flags (code in, flag off) → train never waits
       release branch accepts only bug fixes (cherry-picked from main)
```

### Store tracks & staged rollout

```
Android (Google Play):
  internal testing (≤100 testers, minutes) → closed testing (QA/beta groups) → open testing (public beta)
  → production staged rollout: 1% → 5% → 10% → 20% → 50% → 100% (manual), HALT if crash/ANR spike
  Play Console vitals: crash rate, ANR rate (bad-behavior thresholds ~1.09% crash / 0.47% ANR user-perceived)
iOS (App Store):
  TestFlight internal (instant) / external (beta review) → App Review → Phased Release over 7 days
  (auto-update users only; manual downloads get it anytime) → pause up to 30 days if problems
  Expedited review request for critical bug fixes
```

### Rollout gates (automate the go/no-go)

```
Metrics per version (Sentry/Crashlytics + analytics):
  crash-free users ≥ 99.8%, ANR rate below threshold, startup p90 not regressed,
  checkout conversion & payment success not down, API error rate for this version normal
Automated: if crash-free < threshold at 5% → halt rollout + alert release captain
```

### Hotfix flow

```
Critical bug found in 5.15.0 at 20% rollout
  1. HALT rollout (Play) / pause phased release (iOS)
  2. JS-only? → OTA fix to 5.15.0 runtime (M17) + verify
     Native?  → hotfix branch from release/5.15 → fix → 5.15.1 (new build number) → expedited review
  3. Remote kill switch for the broken feature via feature flag (instant, no release)
  4. Resume rollout with 5.15.1; post-mortem
```

### Version long tail & update enforcement

```
Policy: support last N versions (e.g., ≥ 6 months old); measure % active users per version weekly
Soft update: banner/sheet for versions < recommended (dismissible, remind later)
Force update: blocking screen for versions < minSupported (security, legal, breaking backend change)
  - Remote config (Firebase Remote Config / own config API) fetched at startup, cached for offline
  - Server safety net: 426 Upgrade Required on critical endpoints
  - Android: Play In-App Updates API (IMMEDIATE flow = full-screen; FLEXIBLE = background download)
  - iOS: link to App Store page (no official in-app update API); check iTunes lookup for latest
Use force update sparingly; consider users with low storage (allow freeing space / lite flows)
```

### Release checklist highlights

```
[ ] Version & build bumped (CI)  [ ] Release notes (localized)  [ ] Feature flags defaults correct
[ ] Store screenshots/metadata   [ ] Privacy labels / Data safety form updated for new SDKs
[ ] Target SDK requirements met (Play requires recent targetSdk each year)
[ ] Crash/ANR baseline captured  [ ] Rollback plan (halt + hotfix/OTA) documented
```

## 🟢 कैसे काम करता है? (Hindi)
1. Version: MAJOR.MINOR.PATCH (हर train पर MINOR, hotfix पर PATCH) + हमेशा बढ़ता build number; तुलना semver से (string से नहीं); backend/analytics को version, build, platform भेजो; RN में OTA updateId भी।
2. Release train: सोमवार branch cut (code freeze), मंगल-बुध QA + कर्मचारी इस्तेमाल करें, गुरुवार submit, फिर staged rollout; जो feature तैयार नहीं वो flag के पीछे बंद होकर जाए — train किसी का इंतज़ार न करे।
3. Play: internal → closed → open testing → production में 1% → 5% → … → 100%, crash/ANR बढ़े तो HALT; iOS: TestFlight → review → 7 दिन का phased release (रोक सकते हैं), ज़रूरी fix पर expedited review।
4. Hotfix: rollout रोको; JS-only तो OTA, native तो hotfix branch से 5.15.1 + expedited review; तुरंत राहत के लिए feature flag kill switch; फिर rollout आगे।
5. पुराने versions: हर हफ़्ते देखो कितने यूज़र किस version पर; soft update सुझाव, बहुत पुराने के लिए force update (remote config + सर्वर 426 + Android In-App Updates API) — कम से कम इस्तेमाल करो।

---

## 🟡 Real World Example

**Facebook / Meta** — moved its mobile apps to a weekly release train (described in "Rapid release at massive scale", 2017), with dogfooding by employees, alpha/beta channels and staged rollouts, using feature flags (Gatekeeper) to decouple shipping code from turning features on.

**Google Play staged rollouts & App Store phased release** — standard practice at Uber, Airbnb, Swiggy, Zomato and other large apps: start at 1–5%, watch crash and ANR vitals and business metrics, then ramp. Halting a rollout has saved many apps from full-scale outages.

**Indian fintech force updates** — UPI and banking apps periodically force updates to comply with new NPCI/RBI requirements or to retire insecure versions, using blocking screens and Play In-App Updates.

**Expedited reviews before big events** — teams plan releases around events (Big Billion Days, Diwali, IPL). Code freeze happens well before the event, with only flagged features and OTA-capable fixes during the event window.

## 🟡 Real Example Hindi में
Meta ने mobile ऐप्स को हर हफ़्ते की release train पर लाया (2017) — कर्मचारी पहले इस्तेमाल करते, alpha/beta, धीरे rollout, और feature flags से code और feature अलग।
Uber, Airbnb, Swiggy, Zomato जैसे ऐप Play staged rollout और App Store phased release से 1–5% से शुरू करके crash/ANR देखते हैं; भारतीय UPI/बैंक ऐप NPCI/RBI नियमों के लिए force update करवाते हैं; Big Billion Days, दिवाली, IPL से पहले code freeze।

---

## 🟠 My Stack Example

### EAS build profiles with auto-incremented build numbers
```json
// eas.json
{ "cli": { "appVersionSource": "remote" },
  "build": {
    "production": { "channel": "production", "autoIncrement": true, "env": { "APP_ENV": "production" } },
    "beta":       { "channel": "beta", "autoIncrement": true, "distribution": "store" } },
  "submit": {
    "production": { "android": { "track": "production", "rollout": 0.05, "releaseStatus": "inProgress" },   // 5% staged rollout
                    "ios": { "ascAppId": "1234567890" } } } }
```
```ts
// app.config.ts — version from package.json (single source of truth)
export default ({ config }) => ({ ...config, version: require('./package.json').version });   // "5.15.0"
```

### Version helper + headers
```ts
import * as Application from 'expo-application';
import * as Updates from 'expo-updates';
export const appInfo = {
  version: Application.nativeApplicationVersion!,          // 5.15.0
  build: Application.nativeBuildVersion!,                  // 5015003
  updateId: Updates.updateId ?? 'embedded',
};
http.interceptors.request.use((c) => { c.headers['X-App-Version'] = appInfo.version; c.headers['X-App-Build'] = appInfo.build; c.headers['X-Platform'] = Platform.OS; return c; });
```

### Soft/force update with Play In-App Updates on Android
```ts
import SpInAppUpdates, { IAUUpdateKind } from 'sp-react-native-in-app-updates';
const inApp = new SpInAppUpdates(false);

export async function enforceUpdatePolicy() {
  const cfg = await remoteConfig.get();                                    // { minSupported, recommended }
  const v = appInfo.version;
  if (semverLt(v, cfg.minSupported)) {
    if (Platform.OS === 'android') {
      const r = await inApp.checkNeedsUpdate();
      if (r.shouldUpdate) return inApp.startUpdate({ updateType: IAUUpdateKind.IMMEDIATE });   // full-screen Play flow
    }
    return router.replace('/force-update');                                 // iOS: App Store link screen
  }
  if (semverLt(v, cfg.recommended) && Platform.OS === 'android') {
    const r = await inApp.checkNeedsUpdate();
    if (r.shouldUpdate) inApp.startUpdate({ updateType: IAUUpdateKind.FLEXIBLE });   // download in background
  }
}
```

### Version adoption & rollout gate (SQL on analytics warehouse)
```sql
-- Active users by version (last 7 days)
SELECT app_version, COUNT(DISTINCT user_id) AS users,
       ROUND(100.0 * COUNT(DISTINCT user_id) / SUM(COUNT(DISTINCT user_id)) OVER (), 2) AS pct
FROM app_sessions WHERE started_at > now() - interval '7 days' AND platform = 'android'
GROUP BY app_version ORDER BY app_version DESC;
```
```js
// Rollout guard job (Node): halt Play rollout if crash-free drops (Play Developer API + Sentry)
const crashFree = await sentry.releaseHealth({ release: 'in.quickbite.app@5.15.0+5015003', stat: 'crash_free_users' });
if (crashFree < 0.995) { await play.edits.tracks.update({ track: 'production', releases: [{ versionCodes: ['5015003'], status: 'halted' }] }); alertSlack('#release', '5.15.0 halted: crash-free ' + crashFree); }
```

### Release branch automation (GitHub Actions)
```yaml
name: release-train
on: { schedule: [{ cron: '30 4 * * MON' }] }       # Monday 10:00 IST branch cut
jobs:
  cut:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          NEXT=$(node -p "require('./package.json').version")
          git checkout -b release/$NEXT && git push origin release/$NEXT
          npm version minor --no-git-tag-version && git commit -am "chore: start next train" && git push origin main
```

---

## ⚫ Interview Questions + Answers

**Q1: How would you set up a release process for a large mobile app?**
A1: A fixed release train (weekly or bi-weekly) with a scheduled branch cut and code freeze. Main stays releasable, and unfinished features ship dark behind flags. Release branches accept only cherry-picked fixes. QA regression and employee dogfooding run on release builds, then beta tracks (TestFlight, Play testing). Production uses staged rollouts with automated gates on crash-free rate, ANRs, startup time and business metrics, with clear ownership (a release captain) and a documented hotfix path (halt, OTA if JS-only, or expedited native hotfix). Feature flags provide kill switches.

**Q2: How do staged rollouts work on Android and iOS?**
A2: On Google Play you release the production build to a chosen percentage of users and manually increase it (1%, 5%, 20%, 50%, 100%). You can halt at any point to stop new installs or updates, then ship a fix. On the App Store, phased release automatically ramps auto-updating users over seven days (1%, 2%, 5%, 10%, 20%, 50%, 100%) and can be paused for up to 30 days, while users can still manually download the update. In both cases, watch crash and ANR vitals and key metrics per version before progressing.

**Q3: Version name vs build number — why both?**
A3: The version name (5.15.0) is the human-readable marketing version that users see, used for release notes, support and semver comparisons for update policies. The build number (versionCode or CFBundleVersion) is a monotonically increasing integer that stores use to order and uniquely identify uploads. Each submission needs a higher build number even for the same version, such as rebuilds and hotfix builds. Both should be sent in telemetry and API headers, compared with semver logic, and auto-managed by CI.

**Q4: When and how do you force users to update?**
A4: Only when necessary: security vulnerabilities, legal or regulatory requirements, or backend changes that make old versions unworkable. Maintain `minSupportedVersion` and a recommended version in remote config, fetched at startup with cached fallbacks. Show a blocking update screen below the minimum (Play In-App Updates IMMEDIATE on Android, an App Store link on iOS) and a dismissible prompt below the recommended version. Add a server-side 426 safety net on critical endpoints, communicate the reason, and track version adoption to set thresholds without stranding many users.

**Q5: A crash spike appears at 10% rollout. What do you do?**
A5: Halt the Play rollout or pause the phased release immediately, and turn off the suspected feature via its flag if possible. Triage with crash reports (stack traces, devices, OS versions, update ID) and identify whether it's JS-only (fix via OTA to that runtime) or native (cut a hotfix build with a bumped patch version and build number, and request expedited review). Verify the fix on beta tracks, resume the rollout with the fixed build, communicate status, and write a post-mortem adding tests or gates to prevent recurrence.

---

## 🔷 Trade-offs
✅ Release trains: predictable, fewer surprises — ❌ features wait for the next train (flags help).
✅ Staged rollouts: limit blast radius — ❌ slower full adoption; iOS manual downloads bypass phasing.
✅ Force update: removes insecure/old versions — ❌ user friction, churn on low-storage devices.
✅ Supporting many old versions: user-friendly — ❌ backend complexity & security risk.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Version name | User-visible version (5.15.0) | दिखने वाला version |
| Build number | Increasing store build id | बढ़ता build नंबर |
| Release train | Fixed release schedule | तय release समय-सारिणी |
| Code freeze | Stop adding features to release | release में नया code बंद |
| Dogfooding | Employees use pre-release | कर्मचारी पहले इस्तेमाल करें |
| Staged rollout | Gradual % release (Play) | धीरे-धीरे % release |
| Phased release | 7-day ramp (App Store) | 7 दिन का rollout |
| Hotfix | Urgent fix release | तुरंत सुधार release |
| Force update | Blocking update requirement | ज़बरदस्ती update |
| In-App Updates API | Play in-app update flows | Play का ऐप में update |

---

## ⚡ 3-Line Summary
**English:**
1. Version = semver name + increasing build number (CI-managed), sent in telemetry/headers; compare with semver.
2. Release train with branch cut, flags for dark features, beta tracks, staged rollout (Play %) / phased release (iOS) gated on crash/ANR/business metrics.
3. Hotfix via halt + OTA or expedited native build; manage the long tail with soft/force update (remote config, 426, Play In-App Updates), used sparingly.

**Hindi:**
1. Version = semver नाम + बढ़ता build नंबर (CI से), हर request और telemetry में भेजो।
2. Release train, branch cut, flags के पीछे अधूरे features, beta tracks, धीरे rollout — crash/ANR/business metrics देखकर।
3. Hotfix: rollout रोको + OTA या तुरंत native build; पुराने versions के लिए soft/force update सोच-समझकर।

---

## ➡️ Next Topic Suggestion
**M19. Mobile CI/CD (EAS Build, Fastlane, GitHub Actions)** — A release process needs automation. Next: building, signing, testing and shipping iOS and Android apps automatically from GitHub Actions with EAS Build and Fastlane.
