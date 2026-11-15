---

# 221. Staged Rollout
# हिंदी में: Staged Rollout (धीरे-धीरे Release)
# Platform: Android ✅ | iOS ❌ (iOS: Phased Release for Automatic Updates)

> Expo SDK 53/54 (check current docs — APIs change between SDKs). `rollout` field in `eas submit` EAS CLI version par depend karta hai — `eas submit` docs se verify karo.

---

## 🔵 Simple Definition (English)
**Staged rollout** releases a new production version to only a **percentage of users** (for example 10%), then increases it (25%, 50%, 100%) while you watch crashes and reviews. You can **halt** it if problems appear. You can increase the percentage but not decrease it.

## 🔵 सरल परिभाषा (Hindi)
**Staged rollout** नए production version को पहले सिर्फ़ **कुछ प्रतिशत users** (जैसे 10%) तक पहुँचाता है, फिर आप crashes और reviews देखते हुए उसे बढ़ाते हो (25%, 50%, 100%)। समस्या दिखे तो **halt** कर सकते हो। Percentage बढ़ा सकते हो, घटा नहीं सकते।

---

## 🔴 Problem it Solves
- A bad release to 100% of millions of users is a disaster.
- Staged rollout limits the blast radius.
- You get real-world crash data before full exposure.

## 🔴 यह क्यों बना? (Hindi)
- करोड़ों users को 100% पर खराब release देना बड़ी आपदा है।
- Staged rollout असर का दायरा छोटा रखता है।
- पूरे exposure से पहले असली crash data मिलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Production → Create release → AAB
Step 2 → "Next" ke baad "Rollout percentage" field me 10 (ya jo chahiye)
Step 3 → "Start rollout to Production" → review → live for 10% users
Step 4 → Dashboard "Release dashboard" me crash rate, ANR, ratings monitor
Step 5 → Sab theek → "Update rollout" → 25 → 50 → 100%
Step 6 → Problem → "Halt rollout" → fix → naya versionCode release
Step 7 → Fix ko 100% tak le jao; "Resume rollout" bhi possible (halted ke baad)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Production → Create release → AAB
Step 2 → "Next" के बाद "Rollout percentage" में 10 (या जो चाहिए)
Step 3 → "Start rollout to Production" → review → 10% users के लिए live
Step 4 → "Release dashboard" में crash rate, ANR, ratings देखो
Step 5 → सब ठीक → "Update rollout" → 25 → 50 → 100%
Step 6 → समस्या → "Halt rollout" → fix → नया versionCode release
Step 7 → Fix को 100% तक ले जाओ; halted के बाद "Resume rollout" भी संभव
```

**Console screens (described in words):**
- **Release screen:** "Rollout percentage" ke liye ek slider/number box (1-100). Neeche "Start rollout" button.
- **Release dashboard:** Cards: "Rollout %" (progress ring), "Crash rate", "ANR rate", "Reviews". Upar right "Update rollout" aur "Halt rollout" buttons. Halt karne par banner "Rollout halted".

---

## 🟡 Real World Example
**Paytm** ya **PhonePe** jaisi payment apps UPI flow ke naye version ko pehle 5-10% users par daalti hain. Agar payment success rate gir jaaye ya crash badhe, wo rollout halt karke fix dete hain. Isse crores users ke paise-sambandhi flow par asar nahi padta. **Zomato** bhi badi UI changes ko staged rollout se bhejta hai.

## 🟡 Real Example Hindi mein
**Paytm** या **PhonePe** जैसी payment apps UPI flow का नया version पहले 5-10% users को देती हैं। अगर payment success rate गिरे या crashes बढ़ें, तो rollout halt करके fix देती हैं। इससे करोड़ों users के पैसे वाले flow पर असर नहीं पड़ता। **Zomato** भी बड़े UI बदलाव staged rollout से भेजता है।

---

## 💻 Code Example — Basic
`eas.json` — 10% rollout ke saath submit (EAS `releaseStatus: "inProgress"` + `rollout` fraction; version-dependent, docs verify karo):

```json
{
  "cli": { "version": ">= 12.0.0" },
  "submit": {
    "production-staged": {
      "android": {
        "serviceAccountKeyPath": "./secrets/play-service-account.json",
        "track": "production",
        "releaseStatus": "inProgress",
        "rollout": 0.1
      }
    }
  }
}
```

```bash
# 10% par release
eas submit -p android --profile production-staged --latest
# Baad me percentage badhana — Console me "Update rollout" se (EAS Submit sirf nayi submission karta hai)
```

## 💻 Code Example — Advanced
Rollout decision logic: crash-free users % aur ANR ke basis par agla step suggest karne wala function (pure Node, runnable). Thresholds apne team ke hisaab se badlo.

```js
// rolloutPlanner.js — run: node rolloutPlanner.js
// rollout steps jo hum follow karte hain
const STEPS = [10, 25, 50, 100];

// metrics ke basis par decision
function decide({ percent, crashFreeUsers, anrRate }) {
  // gambhir problem => halt
  if (crashFreeUsers < 98 || anrRate > 0.5) return { action: 'halt', reason: 'vitals bad' };
  // abhi 100% ho chuka => kuch nahi
  if (percent >= 100) return { action: 'done' };
  // agla step dhundo
  const next = STEPS.find((s) => s > percent);
  // advance
  return { action: 'advance', to: next };
}

// sample runs
console.log(decide({ percent: 10, crashFreeUsers: 99.4, anrRate: 0.1 })); // advance to 25
console.log(decide({ percent: 25, crashFreeUsers: 96.0, anrRate: 0.1 })); // halt
console.log(decide({ percent: 100, crashFreeUsers: 99.9, anrRate: 0.0 })); // done
```

```bash
# JS-only issue ke liye fast fix: EAS Update (store review ke bina), runtimeVersion same ho to
eas update --branch production --message "fix crash on checkout"
```

---

## 📱 Android vs iOS Difference
| Feature | Android Staged Rollout | iOS Phased Release |
|---------|------------------------|--------------------|
| Control | Aap percentage chunte ho | Apple ka fixed 7-day schedule |
| Halt | Haan, halt/resume | Pause up to 30 days |
| Decrease % | Nahi | N/A |
| Applies to | Updates (and new release) | Automatic updates only |
| New installs | Rollout % ko bhi lagu (new users bhi %) | Sabko latest version milta hai |
| Manual update users | Staged ke dauran bhi unhe mil sakta hai (platform behaviour) | Manual update se latest mil jata hai |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas submit -p android --profile production-staged --latest   # inProgress + rollout fraction
```
CLI way:
```bash
# fastlane: supply --rollout 0.1 (10%) — version-dependent, docs check karo
fastlane supply --aab app-release.aab --track production --rollout 0.1
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** 1% par rollout karke kuch na dekhna.
✅ **Correct:** Har step par vitals + business metrics (orders, payments) dekho.

❌ **Mistake 2:** Soch lena ki rollout ko kam kar sakte hain.
✅ **Correct:** Percentage sirf badhta hai; problem me halt karo.

❌ **Mistake 3:** Halt ke baad purana versionCode wapas live karna chaha.
✅ **Correct:** Naya fix, bada versionCode.

❌ **Mistake 4:** Server-side compatibility sochna bhool jana.
✅ **Correct:** Purana aur naya app version dono API se chalna chahiye.

---

## 🧠 Tricky Interview Question
**Q: 10% rollout par users ke 50% ko naya version kyun mila?**

**Answer:** "Rollout percentage" users ke us hisse par lagta hai jinhe Play update offer karta hai; par kuch users **manually Play Store kholkar update** karte hain, ya jo "Early access"/testing tracks me hain, ya device jo update check karta hai. Isliye exact adoption % rollout % se mel na khaye. Staged rollout ko "exposure cap" samjho, exact number nahi. Metrics hamesha version-wise (Crashlytics/Android vitals filter by version) dekho.

---

## ⚫ Interview Questions + Answers

**Q1: Staged rollout kyun?**
A1: Risk kam, real crash data, halt option.

**Q2: Halt kab karte hain?**
A2: Crash rate/ANR spike, payment/order drop, critical bug reports.

**Q3: Rollout ko kam kar sakte hain?**
A3: Nahi, sirf halt ya badhana.

**Q4: Hotfix ke liye kya?**
A4: Naya versionCode, build, aur sahi percentage; JS-only bug me OTA update.

**Q5: Staged rollout me backend ko kya dhyan rakhna chahiye?**
A5: Backward compatible APIs, feature flags, kill switches.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Major update, large user base, payment/critical flows.

❌ Avoid when:
- Critical security patch jo sabko turant chahiye (tab bhi fast staged ho sakta hai).

---

## 📊 Visual Diagram
```
 v2.0 AAB
   │
   ▼
 10% ──ok──► 25% ──ok──► 50% ──ok──► 100%
   │          │           │
   └─ bad? ───┴───────────┘
            HALT → fix → v2.0.1 (higher versionCode)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Staged rollout | % based release | % के आधार पर release |
| Halt | Stop rollout | Rollout रोकना |
| Blast radius | Users affected by bug | Bug से प्रभावित users |
| Crash-free users | % users without crash | बिना crash वाले users |
| Kill switch | Remote feature off | Remote से feature बंद |

---

## ⚡ 3-Line Summary
**English:**
1. Release to a small % first, then increase while monitoring.
2. Percentage only goes up; use halt on problems.
3. Fix = new higher versionCode (or OTA for JS-only).

**Hindi:**
1. पहले छोटे % को release करो, फिर monitor करते हुए बढ़ाओ।
2. Percentage सिर्फ़ बढ़ता है; समस्या में halt करो।
3. Fix = नया बड़ा versionCode (या JS-only के लिए OTA)।

---

## ➡️ Next Topic
**222. App Review Process (Android)** — Google review कैसे काम करता है।
