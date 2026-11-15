# 209. EAS Submit to Play Store
# हिंदी में: EAS Submit से Play Store पर Upload
# Platform: Android ✅ | iOS ❌ (iOS के लिए App Store Connect submit अलग है)

> Target: **Expo SDK 52 (React Native 0.76)** with `eas-cli` — check current docs — Play Console UI and EAS flags change over time.

---

## 🔵 Simple Definition (English)
`eas submit` uploads your built AAB to Google Play using a **service account** (a robot account with API access). No manual drag-and-drop in Play Console. **The very first release of a new app must be uploaded manually in Play Console** (Google API limitation for new apps) — after that EAS Submit works.

## 🔵 सरल परिभाषा (Hindi)
`eas submit` आपके बने हुए AAB को **service account** (API access वाला robot account) से Google Play पर upload करता है। Play Console में drag-and-drop की ज़रूरत नहीं। **नए app का पहला release Play Console में manually upload करना पड़ता है** (Google API की सीमा) — उसके बाद EAS Submit चलता है।

---

## 🔴 Problem it Solves
- Manual upload each release is slow and error-prone.
- CI/CD wants "build → submit" without a human.

## 🔴 यह क्यों बना? (Hindi)
- हर release पर manual upload धीमा और गलती वाला है।
- CI/CD को "build → submit" बिना इंसान के चाहिए।

---

## 🟢 How it Works — Step by Step
```
A) ONE-TIME: create a Google service account key
Step 1 → Google Cloud Console → select/create project → IAM & Admin → Service Accounts → Create
Step 2 → Name it (e.g. eas-submit); skip roles; Done
Step 3 → Open the account → Keys tab → Add key → Create new key → JSON → file downloads
Step 4 → Enable "Google Play Android Developer API" in APIs & Services → Library
Step 5 → Play Console → Users and permissions → Invite new users → paste the service account email
Step 6 → Grant app permissions (release apps to testing tracks / production) → Invite
Step 7 → Save JSON as ./play-service-account.json (git-ignored)

B) EVERY RELEASE
Step 8 → eas build -p android --profile production   (creates AAB)
Step 9 → eas submit -p android --latest              (submits latest build)
         or:  eas build -p android --auto-submit
Step 10 → Check Play Console → Release → Testing → Internal testing → new release appears
```

## 🟢 कैसे काम करता है? (Hindi)
```
A) एक बार: Google service account key बनाओ
Step 1 → Google Cloud Console → Service Accounts → Create
Step 2 → नाम दो (eas-submit); roles skip; Done
Step 3 → Account खोलो → Keys → Add key → JSON → file download
Step 4 → "Google Play Android Developer API" enable करो
Step 5 → Play Console → Users and permissions → Invite → service account का email
Step 6 → App permissions दो (release permissions) → Invite
Step 7 → JSON को ./play-service-account.json में रखो (git-ignore)

B) हर release
Step 8 → eas build -p android --profile production
Step 9 → eas submit -p android --latest
Step 10 → Play Console में Internal testing में नया release दिखेगा
```

**Console screens (described):**
- **Google Cloud → Service Accounts:** a table with email column (`eas-submit@project-id.iam.gserviceaccount.com`); the **Keys** tab shows "Add key" dropdown → JSON.
- **Play Console → Users and permissions:** a list of users; "Invite new users" button opens a form (email, access expiry, tabs "App permissions" and "Account permissions").
- **Terminal during submit:** prompts for the path of the key if not set in eas.json, shows "Submitting your app to Google Play Store" then a link to the Play Console release.

---

## 🟡 Real World Example
A Zomato-like team: after every merge to `release` branch, CI builds AAB and submits it to the **internal** track; QA verifies, then product manager promotes to **production** in Play Console with 10% staged rollout.

## 🟡 Real Example Hindi mein
Zomato जैसी team: `release` branch पर merge के बाद CI AAB बनाकर **internal** track पर submit करता है; QA जाँचती है, फिर product manager Play Console में 10% staged rollout के साथ **production** में promote करता है।

---

## 💻 Code Example — Basic
```json
{
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "./play-service-account.json",
        "track": "internal"
      }
    }
  }
}
```
```bash
eas submit --platform android --latest
```

## 💻 Code Example — Advanced
```json
{
  "cli": { "version": ">= 12.0.0", "appVersionSource": "remote" },
  "build": { "production": { "autoIncrement": true, "android": { "buildType": "app-bundle" } } },
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "./play-service-account.json",
        "track": "production",
        "releaseStatus": "inProgress",
        "rollout": 0.1,
        "changesNotSentForReview": false
      }
    },
    "internal": {
      "android": {
        "serviceAccountKeyPath": "./play-service-account.json",
        "track": "internal",
        "releaseStatus": "completed"
      }
    }
  }
}
```
```bash
# Submit a specific build by id or a local file
eas submit -p android --id <BUILD_ID> --profile internal
eas submit -p android --path ./app-release.aab --profile internal
# Build and submit in one go
eas build -p android --profile production --auto-submit-with-profile=production
# In CI: write service account JSON from a secret, then submit non-interactively
echo "$PLAY_KEY_JSON" > play-service-account.json
eas submit -p android --latest --non-interactive
rm play-service-account.json
```
> `rollout` (fraction 0-1) applies with `releaseStatus: "inProgress"`. If a flag is rejected by your CLI version, run `eas submit --help` — flag names vary across versions.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Auth | Google service account JSON | Apple ID / App Store Connect API key |
| First release | Must be manual in Play Console | App record must exist in App Store Connect |
| Target | Track (internal/alpha/beta/production) | TestFlight / App Store |
| Review | Automated + manual, hours to days | Human review, ~24-48h |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas submit -p android --latest
```
CLI way (no EAS): upload manually in Play Console, or use Fastlane `supply`:
```bash
fastlane supply --aab app-release.aab --track internal --json_key play-service-account.json --package_name com.mycompany.foodapp
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Trying `eas submit` before first manual upload → error "app not found / no release".
✅ Correct: Create app + first manual upload in Play Console.

❌ Mistake 2: Service account lacks Play permission.
✅ Correct: Invite the email in Play Console with release permissions; wait a few minutes (propagation).

❌ Mistake 3: Submitting to `production` track with draft app (store listing incomplete).
✅ Correct: Complete listing/forms; use `internal` first.

❌ Mistake 4: Committing JSON key.
✅ Correct: Secret in CI, `.gitignore` locally.

---

## 🧠 Tricky Interview Question
"`eas submit` says 'Only draft apps can be created via API' or similar release status error. What does it mean?"

Answer: Google rejects non-draft releases when the app is still in draft state (store listing/content forms incomplete, or no completed release yet). Use `releaseStatus: "draft"` or finish the app setup in Play Console, then submit.

---

## ⚫ Interview Questions + Answers
Q1: What is a service account?
A1: A non-human Google identity used for API calls with a JSON key.

Q2: Which API must be enabled?
A2: Google Play Android Developer API.

Q3: Tracks in Play?
A3: internal, alpha (closed), beta (open), production.

Q4: How to avoid managing keys manually?
A4: EAS can store the service account key (`eas credentials`), so you don't need the file locally.

Q5: How to ship gradually?
A5: `releaseStatus: inProgress` with `rollout` fraction, or staged rollout in Play Console.

---

## 🔷 When to Use + When Not to Use
✅ Use when: repeated releases, CI/CD.

❌ Avoid when: very first release (manual), or you need to fill complex declarations — do those in Console.

---

## 📊 Visual Diagram
```
 eas build (AAB) ──► EAS storage
         │
 eas submit ──► Google Play Developer API ──(service account JSON)──► Play Console
                                                                       │
                         Internal ► Closed ► Open ► Production (staged rollout)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Service account | Robot Google account | Robot Google account |
| Track | Release lane | Release lane |
| Staged rollout | % of users first | पहले कुछ % users |
| Draft | Not yet sent for review | Review के लिए नहीं भेजा |

---

## ⚡ 3-Line Summary
English: Create a service account, give it Play permissions, point eas.json to the key.
Run `eas submit -p android --latest` after building.
First app version must be uploaded manually.

Hindi: Service account बनाओ, Play permissions दो, eas.json में key का path दो।
Build के बाद `eas submit -p android --latest` चलाओ।
पहला version manually upload करना पड़ता है।

---

## ➡️ Next Topic
**210. Google Play Console — Complete Guide** — console के हर हिस्से का walkthrough।
