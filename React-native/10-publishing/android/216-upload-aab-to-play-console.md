---

# 216. Upload AAB to Play Console
# हिंदी में: Play Console में AAB Upload करना
# Platform: Android ✅ | iOS ❌

> Expo SDK 53/54 (check current docs — APIs change between SDKs). `eas submit` ke flags/fields EAS CLI version ke saath badal sakte hain; `eas submit --help` aur docs se verify karo.

---

## 🔵 Simple Definition (English)
An **AAB (Android App Bundle, `.aab`)** is the publishing format Google Play requires for new apps. You upload it in Play Console under a release track (internal, closed, open, production). Google then generates optimized APKs per device. The first upload of an app must be done **manually** in the Console; later uploads can be automated with `eas submit`.

## 🔵 सरल परिभाषा (Hindi)
**AAB (Android App Bundle, `.aab`)** वह publishing format है जो Google Play नई apps के लिए माँगता है। इसे Play Console में किसी release track (internal, closed, open, production) में upload करते हैं। फिर Google हर device के हिसाब से optimized APKs बना देता है। App का **पहला upload manually** Console में करना पड़ता है; बाद के uploads `eas submit` से automate हो सकते हैं।

---

## 🔴 Problem it Solves
- One fat APK contained code/resources for every device (big download).
- AAB lets Play deliver only what a device needs (smaller installs).
- Play App Signing lets Google keep the final signing key safe; you only hold an upload key.

## 🔴 यह क्यों बना? (Hindi)
- एक मोटी APK में हर device का code/resources होता था (बड़ा download)।
- AAB से Play हर device को सिर्फ़ ज़रूरी हिस्सा देता है (छोटा install)।
- Play App Signing में final signing key Google सुरक्षित रखता है; आपके पास सिर्फ़ upload key होती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → versionCode badhao (har upload par nayi, pichli se badi)
Step 2 → AAB banao:  eas build -p android --profile production
Step 3 → EAS dashboard se .aab download
Step 4 → Play Console → Test and release → Production (ya Testing → Internal testing)
Step 5 → "Create new release"
Step 6 → Play App Signing opt-in (first time) — upload key se sign hua AAB accept
Step 7 → AAB drag-drop → processing ka wait
Step 8 → Release name (auto) + Release notes (Hindi/English tags)
Step 9 → "Next" → warnings/errors fix → "Save" → "Send for review / Start rollout"
Step 10 → Agli baar: eas submit -p android (service account key ke saath)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → versionCode बढ़ाओ (हर upload पर नया, पिछले से बड़ा)
Step 2 → AAB बनाओ:  eas build -p android --profile production
Step 3 → EAS dashboard से .aab download करो
Step 4 → Play Console → Test and release → Production (या Testing → Internal testing)
Step 5 → "Create new release" दबाओ
Step 6 → पहली बार Play App Signing opt-in — upload key से signed AAB accept होता है
Step 7 → AAB drag-drop करो → processing का इंतज़ार
Step 8 → Release name (auto) + Release notes (भाषा tags के साथ)
Step 9 → "Next" → warnings/errors ठीक करो → "Save" → "Send for review / Start rollout"
Step 10 → अगली बार: eas submit -p android (service account key के साथ)
```

**Console screens (described in words):**
- **Create release page:** Upar "App bundles" section — beech me dotted box "Drop app bundles here to upload" aur "Upload" button. Uploading ke baad table me bundle ka naam, versionCode, size.
- **Release notes box:** Language tag format me text, jaise `<en-US> Bug fixes </en-US>` (Console template deta hai). 500 chars limit per language.
- **Review release screen:** Upar red "Errors" ya yellow "Warnings" list (jaise "Target API level too low"); sab clear hone par "Start rollout to Production" button active hota hai.

---

## 🟡 Real World Example
**Zomato** har hafte naya version nikalta hai: CI (GitHub Actions) AAB banata hai, Play service account se **internal track** par upload hota hai, QA verify karta hai, fir production me promote. Isse manual Console upload ka jhanjhat nahi hota. Chhoti teams pehla build manual upload karti hain, fir `eas submit` use karti hain.

## 🟡 Real Example Hindi mein
**Zomato** हर हफ़्ते नया version निकालता है: CI (GitHub Actions) AAB बनाता है, Play service account से **internal track** पर upload होता है, QA verify करती है, फिर production में promote होता है। इससे manual Console upload की झंझट नहीं रहती। छोटी teams पहला build manual upload करती हैं, फिर `eas submit` इस्तेमाल करती हैं।

---

## 💻 Code Example — Basic
`eas.json` — production build AAB, aur submit profile:

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
        "track": "internal",
        "releaseStatus": "draft"
      }
    }
  }
}
```

```bash
# AAB build (EAS cloud) — signing EAS credentials se
eas build --platform android --profile production
# build ke baad Play Console me automatic upload (service account chahiye)
eas submit --platform android --profile production
# ya ek hi command me build + submit
eas build --platform android --profile production --auto-submit
```

## 💻 Code Example — Advanced
Bare RN / local build + AAB sanity check script (version badha hua hai ya nahi, JSON check — Node):

```js
// checkVersion.js — run: node checkVersion.js 15 14
// argv se naya aur pichla versionCode lo
const [next, prev] = process.argv.slice(2).map(Number);
// dono numbers valid hone chahiye
if (!Number.isInteger(next) || !Number.isInteger(prev)) {
  console.error('Usage: node checkVersion.js <next> <prev>'); // usage message
  process.exit(2);                                              // bad input
}
// Play rule: naya versionCode pichle se bada hona chahiye
if (next <= prev) {
  console.error(`versionCode ${next} must be > ${prev}`);       // error message
  process.exit(1);                                              // CI fail
}
// sab theek
console.log(`OK: ${prev} -> ${next}`);
```

```bash
# Bare RN: local release AAB
cd android && ./gradlew bundleRelease
# output: android/app/build/outputs/bundle/release/app-release.aab
# bundletool se AAB ko device-specific APKs me badal kar local test (optional)
# bundletool build-apks --bundle=app-release.aab --output=app.apks --mode=universal
```

**Service account setup (words):** Google Cloud Console me service account banao → JSON key download → Play Console → Users and permissions me us account ko invite karo (release permissions) → JSON path `eas.json` me do. Is JSON ko git me commit **mat** karo (`.gitignore`).

---

## 📱 Android vs iOS Difference
| Feature | Android (Play Console) | iOS (App Store Connect) |
|---------|------------------------|-------------------------|
| File | `.aab` | `.ipa` |
| Version rule | `versionCode` strictly increasing | `buildNumber` increasing per version |
| First upload | Manual Console upload | EAS Submit / Transporter works |
| Signing | Upload key + Play App Signing | Apple certs/provisioning profile |
| Automation | Service account JSON | App Store Connect API key |
| Processing | Few minutes | Processing 10-30+ min |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas build -p android --profile production   # AAB cloud me
eas submit -p android --latest               # latest build upload
```
CLI way:
```bash
cd android && ./gradlew bundleRelease        # local AAB (keystore signing config chahiye)
# phir Console me manually upload ya fastlane supply se
fastlane supply --aab app-release.aab --track internal
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** "Version code 14 has already been used".
✅ **Correct:** `versionCode` badhao, ya `autoIncrement: true` use karo.

❌ **Mistake 2:** APK upload karna.
✅ **Correct:** New apps ke liye AAB hi chahiye (`buildType: "app-bundle"`).

❌ **Mistake 3:** Service account JSON git me commit kar dena.
✅ **Correct:** `.gitignore` + CI secrets me rakho.

❌ **Mistake 4:** Pehla upload `eas submit` se karne ki koshish.
✅ **Correct:** Pehla AAB Console me manually upload karo; uske baad `eas submit`.

❌ **Mistake 5:** Target API level purana rakhna.
✅ **Correct:** Google ka current minimum targetSdk requirement check karo; Expo SDK upgrade se aata hai.

---

## 🧠 Tricky Interview Question
**Q: AAB upload ho gaya par "You uploaded an APK or Android App Bundle signed with wrong key" aaya. Kya hua?**

**Answer:** Play App Signing ke saath Google ko **upload key** ka certificate register hota hai. Agar aapne alag keystore se sign kiya, ya EAS credentials badal diye, to fingerprint match nahi karega. Fix: sahi upload keystore use karo. Agar upload key kho gayi, to Play Console → Setup → App signing me "Request upload key reset" kar sakte ho (Google support process). Isliye keystore ka backup rakho (EAS credentials ya secure vault).

---

## ⚫ Interview Questions + Answers

**Q1: AAB aur APK me fark?**
A1: APK installable file hai; AAB publishing format. Google AAB se device-specific APKs banata hai — chhota download.

**Q2: Play App Signing kya hai?**
A2: Google final app signing key rakhta hai; aap upload key se sign karte ho. Upload key kho jaye to reset ho sakti hai, app signing key nahi.

**Q3: `eas submit` ke liye kya chahiye?**
A3: Play service account JSON key (release permissions), existing app entry, aur pehla manual upload ho chuka ho.

**Q4: Release notes kahan likhte hain?**
A4: Release screen me language tags (`<en-US>...</en-US>`) ke saath.

**Q5: Same AAB ko tracks ke beech move kar sakte hain?**
A5: Haan, "Promote release" se bina dubara upload kiye.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Naya release/hotfix store par bhejna ho.
- CI/CD se automation chahiye (`eas submit`, fastlane).

❌ Avoid when:
- JS-only chhota fix — `eas update` (OTA) kaafi ho sakta hai (policy ke andar).

---

## 📊 Visual Diagram
```
 eas build (app-bundle)
        │  .aab (upload key se signed)
        ▼
 Play Console ── Create release ── upload
        │
        ▼
 Play App Signing: Google re-signs with app signing key
        │
        ▼
 Device-specific APKs  ──► users
        ▲
 eas submit (service account) ── later releases
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AAB | Android App Bundle | Android App Bundle format |
| versionCode | Increasing build integer | बढ़ता हुआ build number |
| Upload key | Key you sign with | Upload के लिए key |
| Play App Signing | Google holds final key | Google अंतिम key रखता है |
| Service account | Robot account for API | API के लिए robot account |

---

## ⚡ 3-Line Summary
**English:**
1. Build an AAB, bump versionCode, upload under a track in Play Console.
2. First upload is manual; later ones can use `eas submit` with a service account.
3. Keep upload keystore and service-account JSON safe.

**Hindi:**
1. AAB बनाओ, versionCode बढ़ाओ, Play Console में किसी track में upload करो।
2. पहला upload manual है; बाद वाले service account के साथ `eas submit` से हो सकते हैं।
3. Upload keystore और service-account JSON सुरक्षित रखो।

---

## ➡️ Next Topic
**217. Internal Testing Track** — upload के बाद सबसे पहले team में test करो।
