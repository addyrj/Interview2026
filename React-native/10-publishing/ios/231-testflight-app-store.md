# 231. TestFlight & App Store Submission
# हिंदी में: TestFlight और App Store — iOS Distribution
# Platform: Android ❌ | iOS ✅

---

## 🔵 Simple Definition (English)
**TestFlight** is Apple's official beta testing platform (part of App Store Connect). Upload your IPA → distribute to up to 10,000 testers before going live. **App Store submission** is the formal process: TestFlight build → App Store review → public release. iOS review is stricter than Android and typically takes 1-3 days for new submissions.

## 🔵 सरल परिभाषा (Hindi)
**TestFlight** Apple का official beta testing platform है (App Store Connect का part)। IPA upload करो → live होने से पहले 10,000 testers तक distribute करो। **App Store submission**: TestFlight build → App Store review → public release। iOS review Android से stricter है — new submissions के लिए typically 1-3 days।

---

## 🔴 What You Need Before Submitting
```
iOS SUBMISSION CHECKLIST:
  ✅ Apple Developer Account ($99/year)
  ✅ App Store Connect account (same Apple ID)
  ✅ iOS Distribution Certificate + Provisioning Profile (see topic 230)
  ✅ Signed IPA (or EAS Build)
  ✅ App icon: 1024×1024 PNG (no rounded corners, no alpha)
  ✅ Screenshots per device:
     iPhone 6.7" (iPhone 14 Pro Max) — REQUIRED
     iPhone 5.5" (iPhone 8 Plus) — REQUIRED
     iPad Pro 12.9" — if supports iPad
  ✅ App name (max 30 chars)
  ✅ Subtitle (max 30 chars)
  ✅ Description (max 4000 chars)
  ✅ Keywords (max 100 chars, comma-separated — ASO!)
  ✅ Support URL + Privacy Policy URL (REQUIRED)
  ✅ Review notes for Apple (test account credentials if login required!)
  ✅ App category
  ✅ Age rating answers (content questionnaire)
  ✅ buildNumber incremented (CFBundleVersion)
```

---

## 🟢 Submission Steps — Step by Step

```
IOS RELEASE FLOW:
──────────────────────────────────────────────────────

  OPTION A: EAS Build + Submit (Recommended)
  ─────────────────────────────────────────────
  Step 1: eas build --platform ios --profile production
    → Builds on Mac cloud, handles signing automatically
    → Returns IPA download URL or uploads directly

  Step 2: eas submit --platform ios
    → Asks for App Store Connect API key (or Apple ID + password)
    → Uploads IPA to App Store Connect
    → Triggers TestFlight processing (10-30 min)

  OPTION B: Manual via Xcode
  ─────────────────────────────────────────────
  Step 1: Xcode → Product → Archive
    → Builds and archives the app

  Step 2: Xcode Organizer → Distribute App
    → App Store Connect
    → Upload IPA to App Store Connect

  TESTFLIGHT (BETA) FLOW:
  ─────────────────────────────────────────────
  Step 1: Build appears in TestFlight tab (App Store Connect)
  Step 2: Internal Testing (immediate, no review needed)
    → Add up to 25 testers (Apple Developer team members)
    → Available within minutes of upload
  Step 3: External Testing (Beta App Review required)
    → Submit for Beta App Review (1-2 business days)
    → Add up to 10,000 external testers via email
    → Or: public link (anyone with link can join)
    → Build expires after 90 days

  APP STORE SUBMISSION FLOW:
  ─────────────────────────────────────────────
  Step 1: App Store Connect → My Apps → New App (first time)
    OR: existing app → + Version

  Step 2: Fill metadata
    → App name, subtitle, description
    → Keywords (for search ranking!)
    → Screenshots (specific device sizes required)
    → Privacy choices, age rating questionnaire

  Step 3: Select build
    → Choose the TestFlight build to submit

  Step 4: Add review information
    → Test account (if login required — CRITICAL!)
    → Demo video or notes for reviewer
    → Contact info

  Step 5: Submit for Review
    → Status: "Waiting for Review" → "In Review" → "Approved"
    → Or: "Rejected" (reasons given — must fix and resubmit)

  AFTER APPROVAL:
    → "Approved — Ready for Sale"
    → Choose: "Manually release" or "Automatically release"
    → Phased release option: 1% → 2% → 5% → 10% → 20% → 50% → 100% over 7 days
```

---

## 💻 Code Example — Build & Submit

```bash
# ─── EAS BUILD (production iOS) ─────────────────────────────────────────────
eas build --platform ios --profile production

# app.json iOS config:
{
  "expo": {
    "ios": {
      "bundleIdentifier": "com.yourcompany.yourapp",
      "buildNumber": "42",          # MUST increment every upload
      "supportsTablet": false,
      "config": {
        "googleMapsApiKey": "YOUR_KEY"
      }
    },
    "version": "2.1.0"
  }
}

# Increment buildNumber automatically:
eas build --platform ios --auto-increment  # bumps buildNumber
```

```bash
# ─── EAS SUBMIT (upload to TestFlight / App Store) ───────────────────────────
eas submit --platform ios

# EAS will ask:
# "How would you like to authenticate to App Store Connect?"
# → Apple ID + password (may need app-specific password if 2FA)
# → App Store Connect API Key (recommended for CI)

# API Key (from App Store Connect → Users and Access → Keys):
eas submit --platform ios \
  --apple-api-key-id XXXXXXXXXX \
  --apple-api-issuer-id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx \
  --apple-api-key-path ./AuthKey_XXXXXXXXXX.p8
```

```
# SCREENSHOT REQUIREMENTS (critical — wrong sizes = rejection):
# Required devices for 2024 App Store submissions:

iPhone (6.7"): iPhone 15 Pro Max, 14 Pro Max  — 1290×2796 pixels
iPhone (5.5"): iPhone 8 Plus                  — 1242×2208 pixels
iPad Pro 12.9" (if supports iPad)             — 2048×2732 pixels

Minimum: 2 screenshots, maximum: 10 screenshots per device
File format: PNG or JPEG, no alpha channel
Generate with: real device/simulator screenshots
Tools: Fastlane Snapshot, Pictura, AppScreens.io
```

---

## 📱 Apple Review — Common Rejection Reasons

```
TOP REASONS FOR APP STORE REJECTION:
──────────────────────────────────────────────────────
  1. Crashes / Bugs during review
     → Always test on real device before submitting
     → Include test account in review notes

  2. Missing test credentials (login required)
     → App Store review team can't test app
     → ALWAYS provide: username, password in review notes
     → Or: test mode / guest access

  3. Broken links / incomplete features
     → No placeholder buttons
     → All navigation paths must work

  4. Misleading metadata (screenshots don't match app)
     → Screenshots must match actual app UI
     → Don't use competitor screenshots
     → No fake reviews shown in screenshots

  5. Privacy Policy missing or broken URL
     → Required for any app with login, location, or user data
     → URL must be accessible (no 404!)

  6. In-App Purchases not using Apple IAP
     → If selling digital goods: MUST use Apple IAP (30% fee)
     → Physical goods / services: can use Stripe, Razorpay etc.
     → Hiding purchase options = immediate rejection

  7. Guideline 4.2 — Minimum Functionality
     → App must have enough features to be useful
     → Basic web wrapper apps rejected
     → Add real app-specific functionality

  8. 2.3.3 — Accurate Screenshots
     → Must show actual app content/UI
     → Must match app's functionality claims

  9. Data collection without disclosure
     → Any analytics, crash reporting = must be in privacy policy
     → App Tracking Transparency (ATT) required for tracking
```

---

## 🟠 EAS vs Manual Xcode Submission

EAS way:
```bash
eas build --platform ios --profile production
eas submit --platform ios
# Handles: signing, upload, TestFlight processing
# Works from: Windows, Linux, Mac (no Xcode required!)
```

Manual (Xcode):
```
Requires macOS + Xcode
Product → Archive → Distribute → App Store Connect → Upload
More control, useful for debugging signing issues
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Submitting without test account credentials
```
Review team gets app → can't log in → rejects for "incomplete information"
ALWAYS add in App Store Connect → App Information → Review Notes:
  "Test Account: test@yourapp.com / Password123"
  "Use OTP: 123456 (fixed test OTP)"
```

❌ **Mistake 2:** Not incrementing buildNumber
```
ERROR: "This bundle is invalid. The value for key CFBundleVersion [42]
        has already been used for a previous build submission."
Fix: Increment buildNumber before EVERY upload to TestFlight/App Store
     Even if you're just re-uploading the same code
     EAS: --auto-increment handles this automatically
```

❌ **Mistake 3:** Wrong screenshot sizes
```
App Store Connect will reject upload if screenshot dimensions wrong
Required: iPhone 6.7" (1290×2796) + iPhone 5.5" (1242×2208)
Check: Xcode simulator → take screenshots at exact sizes
```

---

## 🧠 Tricky Interview Question

**Q: Your iOS app gets rejected with "Guideline 3.1.1 — In-App Purchases". You have a subscription feature using Stripe. What do you do?**

**Answer:** Apple's guideline 3.1.1 requires that digital goods and subscriptions sold within iOS apps must use Apple In-App Purchases (IAP) — Apple takes 15-30%. This applies to: digital subscriptions, virtual currency, unlocking features, digital content. Stripe (or Razorpay, Paytm) is fine for physical goods and real-world services. Solution: (1) Implement `StoreKit` / `expo-in-app-purchases` for in-app subscription purchase on iOS. (2) If your service is also available on web/Android at a lower price (no Apple fee), Apple now allows mentioning your website for account management, but you cannot link to external purchase from within the iOS app. (3) If it's a cross-platform subscription (user pays on web), use the "reader" app exception — you can provide access but not prompt to purchase. This is a very common interview question because it's a painful real-world gotcha for Indian devs shipping on both Android + iOS.

---

## ⚫ Interview Questions + Answers

**Q1: What is TestFlight and how is it different from App Store?**
A1: TestFlight is Apple's beta testing platform. Upload a build to App Store Connect → it appears in TestFlight → distribute to testers. Internal testers (team members, up to 25): available immediately, no review. External testers (up to 10,000): requires Beta App Review (1-2 days), then invite via email or public link. Builds expire after 90 days. App Store: public release, full App Store Review, no expiry.

**Q2: What is `buildNumber` and how is it different from `version`?**
A2: `version` (`CFBundleShortVersionString`): user-visible version string ("1.2.0") — shown on App Store page. `buildNumber` (`CFBundleVersion`): integer string, must increment for every TestFlight/App Store upload (even if version stays same). Apple rejects duplicate build numbers. You can have version "1.0.0" with buildNumbers 1, 2, 3... as you iterate. EAS `--auto-increment` automates this.

**Q3: What is phased release on App Store?**
A3: Phased release gradually delivers an update over 7 days: 1% → 2% → 5% → 10% → 20% → 50% → 100% of auto-update users per day. Useful for monitoring crash rate on new versions before full exposure. You can pause the rollout at any stage. Note: users who manually check for updates always get the new version regardless of phased rollout percentage. Different from Play Store's rolling release (you control %).

**Q4: How do you handle the App Tracking Transparency (ATT) requirement?**
A4: iOS 14.5+ requires apps to show an ATT prompt before tracking users across apps/websites (e.g., Facebook Ads, AppsFlyer). Add `NSUserTrackingUsageDescription` to Info.plist, use `expo-tracking-transparency` or `react-native-tracking-transparency` to show the prompt at the right time (after onboarding, not at launch). If user denies: don't track. IDFA becomes zeros. Failure to implement when tracking = App Store rejection.

**Q5: What are the screenshot requirements for App Store submission?**
A5: Required device sizes (2024): iPhone 6.7" (1290×2796 px, iPhone 15 Pro Max) and iPhone 5.5" (1242×2208 px, iPhone 8 Plus) are minimum required. iPad Pro 12.9" required if app supports iPad. Min 2 screenshots, max 10 per device. PNG or JPEG, no transparency. Must accurately represent the app — fake UI or competitor screenshots = rejection. App Store Preview videos (optional) can increase conversion.

---

## 📊 Visual Diagram

```
iOS RELEASE PIPELINE:
──────────────────────────────────────────────────────

  eas build --platform ios
         │
         ▼
  Signed IPA on Expo CDN
         │
  eas submit --platform ios
         │
         ▼
  App Store Connect
  ├── TestFlight
  │   ├── Internal Testing (instant, 25 testers)
  │   │   → QA team tests → ✅
  │   └── External Testing (Beta Review: 1-2 days)
  │       → 10,000 testers → feedback → ✅
  │
  └── App Store Submission
      │
      ├── Fill metadata (name, desc, screenshots, keywords)
      ├── Select TestFlight build
      ├── Add review notes + test account
      ├── Submit for Review
      │
      ▼
  Apple Review (1-3 days new, hours for updates)
  │
  ├── APPROVED ✅ → Ready for Sale
  │   → Phased release (optional)
  │   → Goes live on App Store
  │
  └── REJECTED ❌ → Fix issues → Resubmit
      (Common: missing test creds, crashes, guideline violations)

BUILDNUMBER RULE:
  Every upload (any track): buildNumber MUST increase
  1 → 2 → 3 → 4 → 5... (never reuse, never go back)
  EAS: --auto-increment handles this automatically
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TestFlight | Apple's beta testing platform | Apple का beta testing |
| buildNumber | Must-increment upload version | हर upload पर बढ़ने वाला number |
| App Store Connect | Apple's app management dashboard | App management dashboard |
| Phased release | Gradual % rollout (App Store) | Gradual rollout |
| Internal testing | Team member testing (instant) | Team member testing |
| External testing | Public beta (Beta Review needed) | Public beta testing |
| Review notes | Notes for Apple reviewer | Apple reviewer के लिए notes |
| CFBundleVersion | iOS build number key | iOS build number |
| IAP | In-App Purchase (Apple mandatory for digital goods) | Digital goods के लिए mandatory |

---

## ⚡ 3-Line Summary
**English:**
1. TestFlight: internal testing (instant, 25 team testers) → external testing (Beta App Review 1-2 days, 10,000 testers) → App Store (full review 1-3 days).
2. Always increment `buildNumber` for every upload; provide test account credentials in review notes if login is required — missing credentials is the #1 rejection reason.
3. Digital subscriptions/purchases on iOS MUST use Apple IAP (StoreKit) — Stripe/Razorpay only for physical goods/services.

**Hindi:**
1. TestFlight: internal (instant, 25 testers) → external (Beta Review 1-2 days, 10,000 testers) → App Store (review 1-3 days)।
2. हर upload पर `buildNumber` increment। Review notes में test account credentials दो — missing credentials = #1 rejection reason।
3. iOS पर digital subscriptions: Apple IAP (StoreKit) MANDATORY। Physical goods/services पर Stripe/Razorpay OK।

---

## ➡️ Next Topic
**232. App Store Optimization (ASO)** — Keywords, screenshots, ratings strategy।
