---

# 220. Production Release
# हिंदी में: Production Release (सबके लिए Live)
# Platform: Android ✅ | iOS ❌ (iOS: App Store release)

> Expo SDK 53/54 (check current docs — APIs change between SDKs). Console labels aur policies (target API level, review times) badalte rehte hain.

---

## 🔵 Simple Definition (English)
A **production release** publishes your AAB to the **public Google Play Store** so every eligible user in the chosen countries can find and install it. It goes through Google's review, can be rolled out fully or gradually, and updates existing users automatically.

## 🔵 सरल परिभाषा (Hindi)
**Production release** आपके AAB को **public Google Play Store** पर publish करता है ताकि चुने हुए देशों का हर योग्य user उसे ढूँढकर install कर सके। इसका Google review होता है, इसे पूरा या धीरे-धीरे rollout किया जा सकता है, और मौजूदा users को automatic update मिलता है।

---

## 🔴 Problem it Solves
- Testing tracks reach limited audiences; production is the real distribution.
- Need a controlled gate (review + checklist) before the public gets the app.
- Updates must reach all existing users safely.

## 🔴 यह क्यों बना? (Hindi)
- Testing tracks सीमित audience तक पहुँचते हैं; production असली distribution है।
- Public तक पहुँचने से पहले एक नियंत्रित gate (review + checklist) चाहिए।
- Updates सभी मौजूदा users तक सुरक्षित पहुँचने चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pre-flight checklist: rating ✅, privacy ✅, data safety ✅,
         target audience ✅, ads declaration ✅, app access ✅, listing ✅
Step 2 → Play Console → Test and release → Production
Step 3 → Countries/regions select (India + others)
Step 4 → Create new release → AAB upload (ya Open/Closed se "Promote")
Step 5 → Release name + Release notes
Step 6 → Next → errors fix (target API level, permissions declarations)
Step 7 → Rollout percentage (100% ya staged — topic 221)
Step 8 → "Save" → Publishing overview → "Send changes for review"
Step 9 → Review pass → Live ("Available on Google Play")
Step 10 → Monitor: Android vitals, crashes, reviews, Firebase Crashlytics
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Pre-flight checklist: rating ✅, privacy ✅, data safety ✅,
         target audience ✅, ads declaration ✅, app access ✅, listing ✅
Step 2 → Play Console → Test and release → Production
Step 3 → Countries/regions चुनो (India + अन्य)
Step 4 → Create new release → AAB upload (या Open/Closed से "Promote")
Step 5 → Release name + Release notes
Step 6 → Next → errors ठीक करो (target API level, permissions declarations)
Step 7 → Rollout percentage (100% या staged — topic 221)
Step 8 → "Save" → Publishing overview → "Send changes for review"
Step 9 → Review पास → Live ("Available on Google Play")
Step 10 → Monitor: Android vitals, crashes, reviews, Firebase Crashlytics
```

**Console screens (described in words):**
- **Dashboard checklist:** Upar progress bar "Set up your app" ke saath sabhi tasks par hara tick; red ya blue dot wale tasks incomplete.
- **Production → Create release:** App bundles box, release name field, release notes (language tags). Warnings (yellow) aur errors (red) neeche list me.
- **Publishing overview:** "Changes ready to send for review" list aur "Send N changes for review" button. Agar "Managed publishing" on hai, to approval ke baad aap khud "Publish" dabate ho.

---

## 🟡 Real World Example
**Swiggy** ka production release: festive sale se pehle QA ne internal + beta me verify kiya, fir production par **managed publishing** ke saath submit kiya, taaki approval aane ke baad marketing team ke time par ek saath publish ho. Release ke turant baad Crashlytics aur Android vitals dekhe jaate hain; spike aane par rollout halt.

## 🟡 Real Example Hindi mein
**Swiggy** का production release: त्योहारी sale से पहले QA ने internal + beta में verify किया, फिर production पर **managed publishing** के साथ submit किया, ताकि approval आने के बाद marketing team के समय पर एक साथ publish हो। Release के तुरंत बाद Crashlytics और Android vitals देखे जाते हैं; spike आने पर rollout halt।

---

## 💻 Code Example — Basic
`eas.json` production submit:

```json
{
  "cli": { "version": ">= 12.0.0", "appVersionSource": "remote" },
  "build": {
    "production": {
      "autoIncrement": true,
      "android": { "buildType": "app-bundle" }
    }
  },
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "./secrets/play-service-account.json",
        "track": "production",
        "releaseStatus": "completed"
      }
    }
  }
}
```

```bash
# build + submit ek saath
eas build -p android --profile production --auto-submit
# ya alag-alag
eas build -p android --profile production
eas submit -p android --profile production --latest
```

## 💻 Code Example — Advanced
Release se pehle pre-flight script: `app.json` check (versionCode, package) — Node, runnable.

```js
// preflight.js — run: node preflight.js ./app.json
const fs = require('fs');                        // file system
// argv se path (default ./app.json)
const path = process.argv[2] || './app.json';
// JSON read + parse; fail hone par saaf error
let cfg;
try { cfg = JSON.parse(fs.readFileSync(path, 'utf8')); }
catch (e) { console.error('Cannot read/parse', path, e.message); process.exit(2); }

// expo section
const expo = cfg.expo || {};
// android section
const a = expo.android || {};
// problems list
const problems = [];
// package name honi chahiye aur placeholder nahi
if (!a.package) problems.push('android.package missing');
if (a.package && /^com\.example\b/.test(a.package)) problems.push('placeholder package');
// version (user-visible) honi chahiye
if (!expo.version) problems.push('expo.version missing');
// versionCode integer hona chahiye (ya EAS remote autoIncrement)
if (a.versionCode !== undefined && !Number.isInteger(a.versionCode)) problems.push('versionCode must be integer');
// result
if (problems.length) { console.error('FAIL:\n- ' + problems.join('\n- ')); process.exit(1); }
console.log('Preflight OK');
```

```bash
# release ke baad monitoring: Console → Quality → Android vitals
# crash rate / ANR rate dekho; bad threshold cross hone par visibility affect ho sakti hai
```

---

## 📱 Android vs iOS Difference
| Feature | Android Production | iOS App Store |
|---------|-------------------|----------------|
| Review time | Hours to few days (new apps zyada) | ~24-48 hrs typical |
| Gradual release | Staged rollout % (halt/increase) | Phased release (7 days) |
| Manual publish | Managed publishing | Manual release option |
| Rollback | Previous version re-release (higher versionCode) | New build/submit |
| Update | Auto-update (user setting) | Auto-update |
| Min requirements | targetSdk policy | Xcode/SDK version policy |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas build -p android --profile production --auto-submit   # build+upload production track
```
CLI way:
```bash
cd android && ./gradlew bundleRelease                      # local AAB
fastlane supply --aab app-release.aab --track production   # production upload
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Direct 100% production release bina testing ke.
✅ **Correct:** Internal -> closed/open -> staged production (10%).

❌ **Mistake 2:** Data safety / permissions declaration adhoora (SMS, location, call log).
✅ **Correct:** Sensitive permissions ka declaration form + video/justification complete.

❌ **Mistake 3:** Debug keys/test API URLs ke saath release.
✅ **Correct:** Release signing + production env; JS bundle me secrets nahi.

❌ **Mistake 4:** Crash monitoring na hona.
✅ **Correct:** Crashlytics/Sentry + Android vitals alerts.

---

## 🧠 Tricky Interview Question
**Q: Production me release ke baad pata chala "versionCode 20" me bug hai. Kya aap versionCode 19 wapas live kar sakte ho?**

**Answer:** Nahi, versionCode kabhi kam nahi ja sakta. "Rollback" ka matlab: purane **code/build ko naye, bade versionCode (21)** se dobara build/release karna. Ya agar bug JS-only hai to `eas update` se purani JS bundle push (agar EAS Update configured ho aur runtimeVersion compatible ho). Staged rollout me halt karke naya fix tezi se release karte hain. Isliye staged rollout + kill switch recommend hai.

---

## ⚫ Interview Questions + Answers

**Q1: Production release se pehle kya check karte ho?**
A1: Dashboard checklist (rating, privacy, data safety, listing), versionCode, targetSdk, crash-free test, release notes.

**Q2: Managed publishing kya hai?**
A2: Approval ke baad automatically live nahi hota; aap manually "Publish" karte ho — timing control.

**Q3: Release ke baad kya monitor karte ho?**
A3: Android vitals (crash/ANR), Crashlytics, ratings, uninstall rate, backend errors.

**Q4: Production tak kitna time lagta hai?**
A4: Updates aam taur par kuch ghante-din; new apps/accounts me zyada.

**Q5: Promote vs naya upload?**
A5: Promote same tested AAB ko aage le jaata hai — recommended.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Testing complete aur metrics acche hain.

❌ Avoid when:
- Open crash/ANR spikes, legal/policy forms incomplete, ya backend ready nahi.

---

## 📊 Visual Diagram
```
 Testing tracks pass
        │
        ▼
 Production → Create release → Review
        │                       │
        │     fail ◄────────────┤ (fix, resubmit)
        ▼                       ▼
   Staged 10% ─► 25 ─► 50 ─► 100%   (monitor vitals)
        │
        └── problem? Halt → fix → new versionCode
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Production | Public release track | Public release track |
| Managed publishing | Manual go-live after approval | Approval के बाद खुद publish |
| Android vitals | Crash/ANR metrics | Crash/ANR के आँकड़े |
| Halt | Stop rollout | Rollout रोकना |
| Promote | Move build to next track | अगले track पर ले जाना |

---

## ⚡ 3-Line Summary
**English:**
1. Production = public Play Store release after review.
2. Complete the checklist, use a tested AAB, prefer staged rollout.
3. Monitor vitals; rollback means shipping a higher versionCode.

**Hindi:**
1. Production = review के बाद public Play Store release।
2. Checklist पूरी करो, test किया हुआ AAB लो, staged rollout को प्राथमिकता दो।
3. Vitals देखो; rollback का मतलब है बड़े versionCode के साथ नया release।

---

## ➡️ Next Topic
**221. Staged Rollout** — धीरे-धीरे users तक पहुँचाना।
