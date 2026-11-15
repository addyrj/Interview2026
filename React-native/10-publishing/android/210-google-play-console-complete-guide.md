# 210. Google Play Console — Complete Guide
# हिंदी में: Google Play Console — पूरी Guide
# Platform: Android ✅ | iOS ❌

> Target: **Expo SDK 52 (React Native 0.76)** — check current docs. Play Console's UI, fees and policy requirements (target API level, tester counts) change often — verify at https://support.google.com/googleplay/android-developer before relying on any number here.

---

## 🔵 Simple Definition (English)
Google Play Console is the web dashboard (play.google.com/console) where you create your app listing, upload builds, run tests, answer policy forms and release the app to users. A one-time **US$25** developer registration fee applies.

## 🔵 सरल परिभाषा (Hindi)
Google Play Console वह web dashboard है (play.google.com/console) जहाँ आप app listing बनाते हो, builds upload करते हो, testing चलाते हो, policy forms भरते हो और app release करते हो। एक बार का **US$25** registration fee लगता है।

---

## 🔴 Problem it Solves
- Central place to control distribution, versions, rollouts and policy compliance.
- Google needs app details (data safety, content rating) before users can install.

## 🔴 यह क्यों बना? (Hindi)
- Distribution, versions, rollout और policy compliance का एक केंद्र।
- Users के install करने से पहले Google को app की जानकारी (data safety, content rating) चाहिए।

---

## 🟢 How it Works — Step by Step
```
PART 1 — Account
Step 1 → Go to play.google.com/console → sign in with a Google account → Sign up
Step 2 → Choose account type: Personal or Organization (Organization needs a D-U-N-S number)
Step 3 → Pay $25, complete identity verification (government ID; phone/email verification)

PART 2 — Create app
Step 4 → Dashboard → "Create app" → App name, Default language, App or Game, Free or Paid
Step 5 → Accept Developer Program Policies and US export laws → Create app

PART 3 — Set up (Dashboard "Set up your app" checklist)
Step 6 → Privacy policy URL (public page)
Step 7 → App access (login credentials for reviewers if app requires login)
Step 8 → Ads declaration (does the app contain ads?)
Step 9 → Content rating questionnaire (IARC) → get rating
Step 10 → Target audience and content (age groups; kids policy if applicable)
Step 11 → Data safety form (what data is collected/shared, encryption, deletion)
Step 12 → Government apps / financial features / health declarations if shown

PART 4 — Store listing (Grow users → Store presence → Main store listing)
Step 13 → App name (30 chars), short description (80), full description (4000)
Step 14 → Graphics: app icon 512x512 PNG, feature graphic 1024x500, phone screenshots (min 2; 16:9 or 9:16, JPEG/PNG)
Step 15 → Category and contact details (email, optional phone/website)

PART 5 — Testing and release
Step 16 → Test and release → Testing → Internal testing → Create release → upload AAB → add testers (email list) → Save → Review → Roll out
Step 17 → Closed testing: required for NEW personal accounts — Google has required a minimum number of testers (recently 12) opted-in for 14 continuous days before applying for production access; verify current rule
Step 18 → Test and release → Production → Create new release → upload AAB (or promote from testing) → release notes → Next → fix errors → Start rollout to Production (choose % for staged rollout)
Step 19 → "Publishing overview" shows changes in review; first review can take from a few hours to several days
```

## 🟢 कैसे काम करता है? (Hindi)
```
भाग 1 — Account
Step 1 → play.google.com/console पर Google account से sign up
Step 2 → Account type: Personal या Organization (Organization को D-U-N-S number चाहिए)
Step 3 → $25 दो और identity verification (government ID) पूरा करो

भाग 2 — App बनाओ
Step 4 → "Create app" → नाम, भाषा, App/Game, Free/Paid
Step 5 → Policies accept करो → Create

भाग 3 — Setup checklist
Step 6-12 → Privacy policy, App access, Ads, Content rating, Target audience, Data safety भरो

भाग 4 — Store listing
Step 13-15 → नाम, short/full description, icon 512x512, feature graphic 1024x500, screenshots, category, contact

भाग 5 — Testing और release
Step 16 → Internal testing में AAB upload करके testers जोड़ो
Step 17 → नए personal accounts के लिए closed testing ज़रूरी (अभी 12 testers, 14 दिन — नियम verify करो)
Step 18 → Production → नया release → AAB → release notes → Start rollout (staged % चुन सकते हो)
Step 19 → Review में कुछ घंटे से कई दिन लग सकते हैं
```

**Console screens (described):**
- **All apps page:** grid of app cards with name, package and status (Draft, In review, Published); a blue "Create app" button on top right.
- **Dashboard of an app:** top banner "Finish setting up your app" with a checklist of tasks (each shows a green tick when done); right panel shows "Publishing status".
- **Left navigation:** Dashboard; Inbox; Statistics; Publishing overview; Test and release (Latest releases and bundles, Testing → Internal/Closed/Open, Production, App integrity, Pre-registration); Grow users (Store presence → Main store listing, Custom listings); Monitor and improve (Android vitals → Crashes & ANRs, Ratings and reviews); Policy and programs (App content).
- **Create release page:** "App bundles" box with Upload button; below "Release name" (auto-filled with version) and "Release notes" tabs per language using `<en-US>...</en-US>` tags; bottom right "Next".
- **Release review page:** lists Errors (red; block rollout), Warnings (yellow) and Messages; a "Start rollout to production" button.

---

## 🟡 Real World Example
Before a festive sale, a Swiggy/Flipkart-style team rolls out an update to 10% of users, watches **Android vitals** (crash rate, ANR rate) for a day, then increases to 50% and 100%. If crash rate spikes, they **halt rollout**.

## 🟡 Real Example Hindi mein
त्योहार की sale से पहले Swiggy/Flipkart जैसी team update 10% users को देती है, **Android vitals** (crash, ANR rate) एक दिन देखती है, फिर 50% और 100%। Crash बढ़े तो rollout **halt** कर देती है।

---

## 💻 Code Example — Basic
Pre-flight checklist script (Node) to validate `app.json` before uploading:
```js
// preflight.js - run: node preflight.js
const app = require('./app.json').expo;                 // read Expo config
const errors = [];                                      // collect problems

// package name must look like com.company.app
if (!/^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$/.test(app.android?.package || ''))
  errors.push('android.package missing/invalid');       // invalid package id
// versionCode must be a positive integer (or use remote versioning)
if (app.android?.versionCode !== undefined && !Number.isInteger(app.android.versionCode))
  errors.push('android.versionCode must be integer');   // wrong type
// icon is required for a good listing
if (!app.icon) errors.push('icon missing');             // no icon
// version string must exist
if (!app.version) errors.push('version missing');       // no version

if (errors.length) { console.error(errors.join('\n')); process.exit(1); } // fail
console.log('Preflight OK');                                              // pass
```

## 💻 Code Example — Advanced
Typical release flow commands and a store-listing text file kept in repo (for copy-paste into Console):
```bash
# 1. Build the production AAB
eas build -p android --profile production
# 2. FIRST release only: download AAB from expo.dev and upload manually in Play Console
# 3. Later releases: submit by CLI to the internal track
eas submit -p android --latest --profile production
# 4. In Play Console: Internal testing -> verify -> Promote release -> Production
```
```text
# store-listing/en-IN.txt (keep in git as source of truth)
Title (<=30):       FoodApp - Order Food Online
Short (<=80):       Order food from nearby restaurants in minutes.
Full (<=4000):      FoodApp lets you discover restaurants, track delivery live ...
Release notes:      <en-IN>Bug fixes and faster checkout.</en-IN>
```
**Handling rejection:** Policy and App content → read the email/Inbox message, fix the cited policy (common: privacy policy missing, permissions use not declared, misleading metadata), upload a new build with higher versionCode and resubmit. Use "Appeal" if you believe it is a mistake.

---

## 📱 Android vs iOS Difference
| Feature | Google Play Console | App Store Connect |
|---------|---------------------|-------------------|
| Fee | $25 one-time | $99/year |
| Review time | Hours to few days | Usually 24-48h |
| Testing | Internal / Closed / Open tracks | TestFlight internal/external |
| Staged rollout | Any % you choose | 7-day phased release (fixed schedule) |
| Rollback | Halt rollout; cannot remove a versionCode | Remove from sale / submit new build |
| Metadata | Store listing + Data safety form | App Information + App Privacy |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas submit -p android --latest   # uploads AAB via API (after first manual release)
```
CLI way:
```bash
# Manual upload in Console, or Fastlane
fastlane supply --aab app-release.aab --track internal --json_key key.json --package_name com.mycompany.foodapp
```
Console steps are identical for both — only how the AAB is produced/uploaded differs.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No privacy policy URL or an unreachable page.
✅ Correct: Host a public HTTPS page describing data use.

❌ Mistake 2: Wrong Data safety answers (mismatch with SDKs like analytics/ads).
✅ Correct: Audit every SDK; declare collected data accurately.

❌ Mistake 3: Skipping testing track requirements on a new personal account and being blocked from production.
✅ Correct: Read current "testing requirements for new personal accounts" and start closed testing early.

❌ Mistake 4: Ignoring target API level requirement (new apps/updates must target a recent API level; Google raises it yearly).
✅ Correct: Check the current requirement; Expo SDK sets `targetSdkVersion` — upgrade the SDK when needed.

---

## 🧠 Tricky Interview Question
"You uploaded a new AAB with the same `versionCode` after fixing a bug. Play Console refuses. How do you fix it?"

Answer: Each upload needs a strictly higher `versionCode`, even if the previous release was never published. Increase it (`autoIncrement` with EAS remote versioning or edit `android.versionCode`), rebuild, upload. You also cannot delete a used versionCode.

---

## ⚫ Interview Questions + Answers
Q1: Difference between internal, closed and open testing?
A1: Internal: up to 100 testers, instant availability. Closed: invited testers via email lists/Google Groups. Open: anyone can join from the store listing.

Q2: What is Play App Signing?
A2: Google holds the app signing key; you sign uploads with an upload key, which can be reset if lost.

Q3: What is the Data safety section?
A3: A mandatory form disclosing data collection, sharing, encryption and deletion options, shown on the listing.

Q4: How to stop a bad release?
A4: Halt the staged rollout in Production; release a fixed build with higher versionCode.

Q5: What are Android vitals?
A5: Crash/ANR/battery/startup metrics Google collects; bad numbers reduce visibility.

---

## 🔷 When to Use + When Not to Use
✅ Use when: publishing/updating any Android app on Google Play.

❌ Avoid when: you only need internal distribution — use EAS internal APK or Firebase App Distribution.

---

## 📊 Visual Diagram
```
 Create account ($25, verify ID)
        ▼
 Create app ─► Set up checklist (privacy, rating, data safety, audience)
        ▼
 Store listing (icon 512, feature 1024x500, screenshots)
        ▼
 Internal test ─► Closed test (14 days, testers) ─► Production (staged rollout)
        ▼
 Review ─► Live ─► Monitor Android vitals ─► Halt / Update
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Track | Release lane | Release lane |
| Staged rollout | Gradual release | धीरे-धीरे release |
| Data safety | Data use disclosure | Data उपयोग की जानकारी |
| Android vitals | Quality metrics | Quality metrics |
| Play App Signing | Google-managed signing | Google-managed signing |
| ANR | App Not Responding | App जवाब नहीं दे रहा |

---

## ⚡ 3-Line Summary
English: Register ($25), create the app, complete the setup checklist and store listing.
Test via internal/closed tracks, then roll out to production in stages.
Watch Android vitals and always raise versionCode.

Hindi: Register करो ($25), app बनाओ, setup checklist और store listing पूरी करो।
Internal/closed testing के बाद production में stage-wise rollout करो।
Android vitals देखो और versionCode हमेशा बढ़ाओ।

---

## ➡️ Next Topic
**211+ (iOS Publishing)** — Apple Developer account, certificates और App Store Connect।
