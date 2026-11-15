---

# 222. App Review Process (Android)
# हिंदी में: App Review Process (Android)
# Platform: Android ✅ | iOS ❌ (iOS: App Review by Apple)

> Expo SDK 53/54 (check current docs — APIs change between SDKs). Review timelines aur policies Google badalta rehta hai; numbers approximate hain.

---

## 🔵 Simple Definition (English)
Google reviews every new app and update using **automated checks plus human reviewers**. They verify policy compliance (content, permissions, data safety, payments, ads, metadata). Results: **Approved** (live), **Rejected** (fix and resubmit), or **Removed/Suspended** (for serious or repeated violations).

## 🔵 सरल परिभाषा (Hindi)
Google हर नई app और update की **automated checks और human reviewers** से जाँच करता है। वे policy compliance (content, permissions, data safety, payments, ads, metadata) देखते हैं। नतीजे: **Approved** (live), **Rejected** (ठीक करके दोबारा भेजो), या **Removed/Suspended** (गंभीर या बार-बार उल्लंघन पर)।

---

## 🔴 Problem it Solves
- Protects users from malware, scams, and abusive apps.
- Enforces consistent rules across millions of apps.
- Keeps store quality high (no misleading listings, no spam).

## 🔴 यह क्यों बना? (Hindi)
- Users को malware, scams और abusive apps से बचाता है।
- करोड़ों apps पर एक जैसे नियम लागू करता है।
- Store की quality ऊँची रखता है (भ्रामक listing, spam नहीं)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Aap "Send changes for review" dabate ho (Publishing overview)
Step 2 → Automated scan: malware, permissions, API level, policy signals
Step 3 → Human review (zaroorat par): listing, screenshots, app behaviour, Data safety match
Step 4 → Outcome email + Console Inbox / Policy status page
Step 5a → Approved → live (ya "managed publishing" me aapka Publish click)
Step 5b → Rejected → email me policy ka naam + reason → fix → naya release → dobara review
Step 5c → Serious → Suspended/Removed → Appeal ka option
Step 6 → Timeline: updates ghante-din; new apps/accounts ~7 din ya zyada ho sakte hain
Step 7 → Review ke baad bhi policy checks continue (post-publish takedown possible)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → आप "Send changes for review" दबाते हो (Publishing overview)
Step 2 → Automated scan: malware, permissions, API level, policy signals
Step 3 → Human review (ज़रूरत पर): listing, screenshots, app behaviour, Data safety मिलान
Step 4 → नतीजे का email + Console Inbox / Policy status page
Step 5a → Approved → live (या "managed publishing" में आपका Publish click)
Step 5b → Rejected → email में policy का नाम + कारण → ठीक करो → नया release → दोबारा review
Step 5c → गंभीर → Suspended/Removed → Appeal का विकल्प
Step 6 → समय: updates घंटे-दिन; नई apps/accounts में ~7 दिन या ज़्यादा लग सकते हैं
Step 7 → Review के बाद भी policy checks चलते रहते हैं (publish के बाद takedown संभव)
```

**Console screens (described in words):**
- **Publishing overview:** "Changes in review" section with status chips: "In review", "Ready to publish". Review me hone par changes edit lock/limited ho sakte hain.
- **Inbox:** Google ke messages — subject jaise "Action required: Your app has a policy issue" ya "Your update is live".
- **Policy status (Policy and programs → App bundle explorer/Policy status):** List jisme issue ka naam, status "Rejected"/"Resolved", aur "Appeal" ya "Fix and resubmit" link.

---

## 🟡 Real World Example
Ek **Indian lending app** (loan apps par Google ki sakht policy hai) ko review me extra documents maange jaate hain — RBI-registered NBFC proof, personal loan declaration. Bina proof ke reject. Dusri taraf **Zomato** ke daily updates jaldi approve ho jaate hain kyunki account ka history acha hai aur changes chhote hote hain.

## 🟡 Real Example Hindi mein
एक **Indian lending app** (loan apps पर Google की सख़्त policy है) से review में extra documents माँगे जाते हैं — RBI-registered NBFC का सबूत, personal loan declaration। सबूत के बिना reject। दूसरी तरफ़ **Zomato** के रोज़ के updates जल्दी approve होते हैं क्योंकि account का history अच्छा है और बदलाव छोटे होते हैं।

---

## 💻 Code Example — Basic
Review se pehle pre-check: AndroidManifest permissions me risky permissions dhundo (Node, runnable). Bare/prebuild project ke manifest par.

```js
// permScan.js — run: node permScan.js path/to/AndroidManifest.xml
const fs = require('fs');                                   // file system
// manifest ka path
const file = process.argv[2];
// path nahi mila to usage dikhao
if (!file) { console.error('Usage: node permScan.js AndroidManifest.xml'); process.exit(2); }
// manifest text read
const xml = fs.readFileSync(file, 'utf8');
// uses-permission tags se names nikalo
const perms = [...xml.matchAll(/<uses-permission[^>]*android:name="([^"]+)"/g)].map((m) => m[1]);
// Google ki restricted/sensitive list (sample — poori list policy center me)
const risky = [
  'android.permission.READ_SMS', 'android.permission.RECEIVE_SMS', 'android.permission.READ_CALL_LOG',
  'android.permission.ACCESS_BACKGROUND_LOCATION', 'android.permission.MANAGE_EXTERNAL_STORAGE',
  'android.permission.REQUEST_INSTALL_PACKAGES',
];
// jo risky list me hain unhe filter
const found = perms.filter((p) => risky.includes(p));
// report
console.log('Total permissions:', perms.length);
console.log(found.length ? 'Needs declaration/justification: ' + found.join(', ') : 'No restricted permissions found');
```

## 💻 Code Example — Advanced
Expo me unnecessary permissions hatana (`app.json`) — review risk kam. `blockedPermissions` Expo config ka valid field hai (SDK 47+; version verify karo).

```json
{
  "expo": {
    "name": "FoodieIndia",
    "slug": "foodie-india",
    "android": {
      "package": "in.foodie.app",
      "permissions": ["ACCESS_COARSE_LOCATION", "CAMERA"],
      "blockedPermissions": [
        "android.permission.READ_EXTERNAL_STORAGE",
        "android.permission.WRITE_EXTERNAL_STORAGE",
        "android.permission.RECORD_AUDIO"
      ]
    }
  }
}
```

```bash
# Rejection mile to: email padho -> issue theek karo -> naya versionCode -> naya release
# Galat reject laga to Console se Appeal karo (policy status page → "Appeal")
eas build -p android --profile production && eas submit -p android --latest
```

---

## 📱 Android vs iOS Difference
| Feature | Android (Google Play) | iOS (App Store) |
|---------|-----------------------|-----------------|
| Review style | Mostly automated + human spot-check | Human review (each submission) |
| Time | Hours to ~7 days | Typically ~24-48 hours |
| Post-publish takedown | Common | Possible |
| Rejection reason shown | Policy name in email/Console | Message in Resolution Center |
| Appeal | Console appeal form | Reply / App Review Board |
| Strictness | Policy-by-policy (Data safety, Permissions) | Guidelines (design, payments, content) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```json
{ "expo": { "android": { "blockedPermissions": ["android.permission.RECORD_AUDIO"] } } }
```
CLI way:
```xml
<!-- android/app/src/main/AndroidManifest.xml: unwanted permission remove karne ke liye -->
<uses-permission android:name="android.permission.RECORD_AUDIO" tools:node="remove" />
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Review ke dauran dobara changes bhejna aur loop me atak jana.
✅ **Correct:** Ek baar me saare fixes bhejo; review khatam hone do.

❌ **Mistake 2:** Rejection email ko ignore karke wahi build resubmit karna.
✅ **Correct:** Policy ka naam padho, specific fix karo, notes me explain karo.

❌ **Mistake 3:** Review team ko login chahiye par test credentials na dena.
✅ **Correct:** App content → App access me demo account do.

❌ **Mistake 4:** Data safety aur asli behaviour me mismatch.
✅ **Correct:** Har SDK ka data declare karo.

---

## 🧠 Tricky Interview Question
**Q: App approve ho gayi, 2 hafte baad "policy violation" se remove ho gayi. Kaise?**

**Answer:** Review sirf pehla gate hai. Google live apps ko bhi continuously scan karta hai (automated + user reports). Possible reasons: updated SDK ne naya data collect kiya jo Data safety me declare nahi hua, policy change (jaise target API/permission rule) ke baad non-compliance, user reports, ya remote config se behaviour badal diya jo review ke waqt dikha nahi (deceptive behavior). Console Inbox me exact policy hota hai — fix, resubmit ya appeal. Isliye "review pass hua = sab safe" mat maano.

---

## ⚫ Interview Questions + Answers

**Q1: Android review kaise hota hai?**
A1: Automated scans + zarurat par human review, policy center ke rules ke hisaab se.

**Q2: Review me kitna time?**
A2: Aam updates ghante-din; naye apps/accounts me ek hafta ya zyada.

**Q3: Rejection aaye to kya karein?**
A3: Email me policy padho, fix karo, naya build/release bhejo ya galat laga to appeal.

**Q4: Review team ko app test kaise karne denge?**
A4: App access section me test credentials aur instructions.

**Q5: Remote code/behaviour change ka risk?**
A5: Review ke baad deceptive behaviour change policy violation hai; OTA updates sirf JS fixes, policy ke andar.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- (Mandatory process.) Fast approval ke liye: clean permissions, honest declarations, test credentials.

❌ Avoid when:
- Policy ko bypass karne ki koshish (hidden features, cloaking).

---

## 📊 Visual Diagram
```
 Send for review
      │
      ▼
 Automated scans ──► flagged? ──► Human review
      │                               │
      ▼                               ▼
  Approved ◄───────────────────── Rejected → fix → resubmit
      │                               │
      ▼                               ▼
    Live                         Appeal / Suspended
      │
  Continuous monitoring (post-publish takedown possible)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Policy | Google rules | Google के नियम |
| Appeal | Dispute a decision | निर्णय को चुनौती |
| Takedown | Removal from store | Store से हटाना |
| App access | Test login for reviewers | Reviewers के लिए test login |
| Restricted permission | Needs declaration | घोषणा चाहिए |

---

## ⚡ 3-Line Summary
**English:**
1. Google reviews with automation plus human checks against policy.
2. Rejections come with a policy name; fix it and resubmit or appeal.
3. Apps are monitored after publishing too.

**Hindi:**
1. Google policy के आधार पर automation और human checks से review करता है।
2. Rejection में policy का नाम मिलता है; ठीक करके दोबारा भेजो या appeal करो।
3. Publish के बाद भी apps की निगरानी होती है।

---

## ➡️ Next Topic
**223. Common Rejection Reasons (Android)** — सबसे आम कारण और उनके fix।
