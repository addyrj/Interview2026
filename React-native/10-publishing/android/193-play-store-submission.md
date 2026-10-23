# 193. Play Store Submission — Complete Guide
# हिंदी में: Play Store पर App Submit करना
# Platform: Android ✅ | iOS ❌

---

## 🔵 Simple Definition (English)
**Play Store submission** is the process of uploading your signed Android app to Google Play Console for public distribution. Steps: create app listing → fill metadata → upload signed AAB → set pricing/availability → submit for review. Google's review typically takes a few hours for new apps. Updates can be submitted as rolling releases (10% of users first, then 100%).

## 🔵 सरल परिभाषा (Hindi)
**Play Store submission** signed Android app को Google Play Console पर public distribution के लिए upload करना है। Steps: app listing बनाओ → metadata भरो → signed AAB upload करो → pricing/availability set करो → review के लिए submit। Google review: new apps के लिए कुछ घंटे। Updates को rolling release (10% users पहले, फिर 100%) में submit कर सकते हो।

---

## 🔴 What You Need Before Submitting
```
PREREQUISITES CHECKLIST:
  ✅ Google Play Developer Account ($25 one-time fee)
  ✅ Signed AAB (app-release.aab) — see topic 192
  ✅ App icon: 512×512 PNG (no alpha transparency!)
  ✅ Feature graphic: 1024×500 PNG (for store listing header)
  ✅ Screenshots: 2-8 per device type (phone, tablet, etc.)
     Phone: minimum 2, 16:9 or 9:16 aspect ratio
  ✅ App title (max 30 chars)
  ✅ Short description (max 80 chars)
  ✅ Full description (max 4000 chars)
  ✅ Privacy Policy URL (REQUIRED — even for free apps)
  ✅ Content rating answers (IARC questionnaire)
  ✅ Data safety section (what data you collect/share)
```

---

## 🟢 Submission Steps — Step by Step

```
PLAY CONSOLE SUBMISSION FLOW:
──────────────────────────────────────────────────────

  Step 1: Create New App
    play.google.com/console
    → All apps → Create app
    → App name, language, app/game, free/paid

  Step 2: Fill Store Listing
    → Main store listing:
      Title, short desc, full desc
      Upload icon (512×512), feature graphic (1024×500)
      Upload screenshots (minimum 2 phone screenshots)
    → Contact details: email, website, phone (optional)

  Step 3: App Content / Ratings
    → Content rating: complete IARC questionnaire
      (your honest answers determine rating: Everyone, Teen, Mature)
    → Target audience: which age groups
    → Data safety: what personal data collected, shared, encrypted
      (REQUIRED since April 2022 — users see this on store page)

  Step 4: Upload App Bundle
    → Production → Create new release
    → Upload app-release.aab
    → versionCode must be HIGHER than previous release
    → Add release notes (what's new in this version)
    → Enable Play App Signing if not already done

  Step 5: Set Pricing & Distribution
    → Countries: select all 190+ or specific countries
    → Free or paid (can't change free to paid after publishing!)
    → Declare if contains ads

  Step 6: Review & Submit
    → Play Console will show checklist of issues
    → Fix all red items
    → Submit for review
    → New apps: 1-7 days review (usually hours for established accounts)
    → Updates: often minutes to a few hours

  AFTER APPROVAL:
    Status: "Published" or "Available on Google Play"
    Rolling releases: start at 10% → monitor crash rate → expand to 100%
    Or: Full rollout (100% immediately)
```

---

## 💻 Code Example — Build & Version Management

```bash
# ─── BUILD SIGNED AAB ────────────────────────────────────────────────────────
# From project root:
cd android && ./gradlew bundleRelease

# Output: android/app/build/outputs/bundle/release/app-release.aab

# EAS BUILD (cloud build — recommended):
eas build --platform android --profile production
# Download AAB from EAS dashboard, upload manually to Play Console
# OR use EAS Submit to upload automatically:
eas submit --platform android
```

```
# android/app/build.gradle — version management
android {
    defaultConfig {
        applicationId "com.yourcompany.yourapp"

        # MUST INCREMENT for every Play Store upload:
        versionCode 15          # integer, 1, 2, 3... (no limit, use incrementally)

        # User-visible version string (can repeat):
        versionName "2.1.0"    # semantic version, shown on store

        # After Play Store upload: versionCode 16, 17, 18...
        # Rule: versionCode ALWAYS increases. versionName is flexible.
    }
}
```

```json
// app.json (Expo) — version management
{
  "expo": {
    "version": "2.1.0",
    "android": {
      "versionCode": 15,
      "package": "com.yourcompany.yourapp"
    }
  }
}

// Automate version increment with EAS:
// eas build --auto-increment  →  bumps versionCode automatically
```

```
# DATA SAFETY SECTION — what to declare:
# (Google requires this — you fill it in Play Console)

Data you MUST declare if collecting:
  - Email addresses (account creation) → Collected, Not Shared, Encrypted
  - Phone number (OTP login) → Collected, Not Shared, Encrypted
  - Name (profile) → Collected, Not Shared, Encrypted
  - Location (if you request it) → Collected, May be Shared, Encrypted
  - Crash logs (Firebase Crashlytics) → Collected, Not Shared
  - Analytics events (Firebase) → Collected, Not Shared

NOT declaring when you should = Google rejection!
```

---

## 📱 Android vs iOS Difference
| Feature | Android (Play Store) | iOS (App Store) |
|---------|---------------------|----------------|
| Developer fee | $25 one-time | $99/year |
| Review time (new) | Hours–2 days | 1–3 days |
| Review time (update) | Minutes–hours | Hours–1 day |
| Bundle format | AAB (.aab) | IPA (.ipa) |
| Rolling releases | ✅ (% of users) | ✅ (phased release) |
| Immediate update | Internal testing | TestFlight internal |
| App rejection rate | Lower | Higher (stricter guidelines) |

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Not incrementing `versionCode`
```
ERROR: "Version code 14 has already been used"
Fix: Always increment versionCode before building for Play Store
Use EAS --auto-increment or a script to automate this
```

❌ **Mistake 2:** App icon with transparency
```
ERROR: "Your app icon cannot have transparency"
Fix: 512×512 PNG, RGB (not RGBA), white/solid background
Tool: Remove.bg, Figma, or just ensure no alpha channel
```

❌ **Mistake 3:** Missing privacy policy for apps that collect any data
```
If your app: has login, uses analytics, tracks location, shows ads
→ MUST have privacy policy URL
Get free one from: privacypolicygenerator.info, app-privacy-policy.com
Enter URL in Play Console → Store Listing → Privacy Policy
Without it: app rejected or removed
```

❌ **Mistake 4:** Wrong content rating from questionnaire
```
NEVER lie on IARC questionnaire
If app has: in-app purchases, user-generated content, realistic violence
→ Answer honestly → accept appropriate rating
False rating = app removed from Play Store
```

---

## 🧠 Tricky Interview Question

**Q: You just published version 2.0.0 (versionCode 10) with a critical bug. You have a hotfix ready. What's the fastest path to get it to users?**

**Answer:** Two parallel tracks: (1) **OTA Update (if JS-only bug):** Run `eas update --branch production` — users get it on next app launch, typically within minutes. No store review needed. (2) **Play Store update:** Increment `versionCode` to 11, build new AAB, upload to Play Console as a new release. Use **internal testing** track to verify, then promote to production with a **10% rolling release** (not 100% immediately). Monitor the Android Vitals (crash rate) in Play Console. If crash rate improves, expand to 25%, 50%, 100%. If OTA doesn't cover it (native change), you need the store update route. Typical timeline: Play Store update from submit to live: 2-6 hours for apps with good history.

---

## ⚫ Interview Questions + Answers

**Q1: What is a rolling release on Play Store?**
A1: Rolling release means releasing an update to a percentage of users first — e.g., 10% — before expanding to everyone. Allows monitoring crash rate, ANR rate, and reviews on the new version before full exposure. If something breaks, halt the rollout and fix. Play Console shows "Rollout stopped" if you pause. Recommended for major updates. For minor bug fixes: full rollout (100%) is fine.

**Q2: What is the difference between Internal Testing, Closed Testing, Open Testing, and Production tracks?**
A2: **Internal Testing**: up to 100 testers, available within minutes of upload (no review). **Closed Testing (Alpha)**: limited group, needs email list. **Open Testing (Beta)**: anyone can opt-in on Play Store. **Production**: public release, goes through review. Workflow: Internal → Closed → Open → Production. For fast iteration: upload to Internal first, verify, promote to Production. No need to re-upload the AAB — promote the same build between tracks.

**Q3: What is the Data Safety section and why is it critical?**
A3: Google required since April 2022 that all apps declare what data they collect, why, how they share it, and whether it's encrypted. Users see this on the app's Play Store page. You fill it in Play Console → App Content → Data Safety. If your declarations don't match your actual privacy policy or app behavior, Google can remove the app. Common declarations: email/phone for login, analytics events, crash logs, location (if used). False or incomplete declarations = policy violation.

**Q4: Can you change a free app to paid after publishing?**
A4: No — Google's policy doesn't allow changing a free app to paid. Once published as free, it must remain free. The workaround: publish a new paid app separately. You can switch from paid to free (but not back). This is why monetization strategy must be decided before first publish. Most apps use free + in-app purchases (IAP) rather than paid upfront.

**Q5: What are `versionCode` and `versionName` and what are the rules?**
A5: `versionCode`: integer used internally by Play Store, must increment with every upload (including to any track — internal, alpha, beta, production). No maximum, but must be higher than previous. `versionName`: the user-visible version string ("2.1.0", "3.0", "1.0-beta") — no rules from Play Store, but follow semantic versioning. `versionCode` and `versionName` are independent: you can have `versionCode: 47, versionName: "2.0.0"`.

---

## 📊 Visual Diagram

```
PLAY STORE RELEASE TRACKS:
──────────────────────────────────────────────────────

  Upload AAB (versionCode must increase)
         │
         ▼
  ┌─────────────────┐
  │ Internal Testing │ → Up to 100 emails, instant live (no review)
  └────────┬────────┘   Use for: QA, developer testing
           │ Promote build ↓
  ┌────────▼────────┐
  │ Closed Testing  │ → Limited opt-in testers (email list)
  └────────┬────────┘   Use for: beta testers, stakeholders
           │ Promote ↓
  ┌────────▼────────┐
  │  Open Testing   │ → Anyone on Play Store can join beta
  └────────┬────────┘   Use for: public beta program
           │ Promote ↓
  ┌────────▼────────┐
  │   Production    │ → All users
  │  (10% rollout)  │   Start at 10% → monitor → 25 → 50 → 100%
  └─────────────────┘

RELEASE CHECKLIST:
  □ versionCode incremented
  □ versionName updated (e.g., "2.1.0")
  □ Signed AAB built and tested
  □ Release notes written
  □ Screenshots updated if UI changed
  □ Data safety section accurate
  □ Privacy policy URL working
  □ OTA update also pushed (for JS-only changes)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| versionCode | Internal Play Store version integer | Internal version integer |
| versionName | User-visible version string | User को दिखने वाला version |
| AAB | Android App Bundle — upload format | Play Store upload format |
| Rolling release | Gradual % rollout | Gradually % users को release |
| Play Console | Google's app management dashboard | App management dashboard |
| Content rating | IARC age rating for your app | App की age rating |
| Data safety | Declaration of data collection | Data collection का declaration |
| Internal testing | Instant testing track (no review) | Instant testing track |

---

## ⚡ 3-Line Summary
**English:**
1. Play Store submission: signed AAB + metadata (icon, screenshots, description, privacy policy) + content rating questionnaire + data safety section → Submit for review (hours for updates, days for new apps).
2. Always increment `versionCode` for every upload; use rolling releases (10% first) for major updates to monitor crash rate before full rollout.
3. EAS Submit (`eas submit --platform android`) automates the upload — connects directly to Play Console via API key.

**Hindi:**
1. Play Store: signed AAB + metadata (icon, screenshots, description, privacy policy) + content rating + data safety → Submit (updates: hours, new apps: days)।
2. हर upload पर `versionCode` increment करो। Major updates: rolling release (10% पहले) → crash rate monitor करो।
3. `eas submit --platform android` upload automate करता है — Play Console API key से direct connect।

---

## ➡️ Next Topic
**194. App Store Connect & TestFlight** — iOS app submission, TestFlight beta distribution।
