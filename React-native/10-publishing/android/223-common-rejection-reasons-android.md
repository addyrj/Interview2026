---

# 223. Common Rejection Reasons (Android)
# हिंदी में: आम Rejection कारण (Android)
# Platform: Android ✅ | iOS ❌ (iOS ke alag reasons hote hain)

> Expo SDK 53/54 (check current docs — APIs change between SDKs). Google policies aur targetSdk requirement har saal badalti hai; yahan ki list representative hai, official Policy Center final hai.

---

## 🔵 Simple Definition (English)
App rejections on Google Play happen when your app or listing breaks a **Developer Program Policy**. The most common causes: missing/incorrect privacy policy or Data safety, risky permissions without justification, crashes/broken features, misleading metadata, wrong payment method for digital goods, outdated target API level, and missing account deletion.

## 🔵 सरल परिभाषा (Hindi)
Google Play पर rejection तब होता है जब आपकी app या listing किसी **Developer Program Policy** को तोड़ती है। सबसे आम कारण: privacy policy या Data safety का न होना/गलत होना, बिना justification के risky permissions, crashes/टूटे features, भ्रामक metadata, digital goods के लिए गलत payment तरीका, पुराना target API level, और account deletion का न होना।

---

## 🔴 Problem it Solves
- Knowing the top reasons lets you fix issues **before** submitting (saves days).
- Avoids repeated rejections that could lead to account-level action.
- Gives a checklist for interviews and real releases.

## 🔴 यह क्यों बना? (Hindi)
- शीर्ष कारण जानकर आप submit करने **से पहले** ही सुधार कर सकते हो (दिन बचते हैं)।
- बार-बार rejection से account-level action का ख़तरा नहीं रहता।
- Interview और असली releases के लिए checklist मिलती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Rejection email aata hai: "Issue found: <Policy name>"
Step 2 → Console → Policy and programs → Policy status → details dekho
Step 3 → Reason pehchano (neeche table)
Step 4 → Fix karo (code / listing / Console form)
Step 5 → Naya versionCode agar code badla; listing-only ho to resubmit
Step 6 → Release notes / "Notes for review" me kya fix kiya likho
Step 7 → Dobara "Send for review"
Step 8 → Galat laga to Appeal (with evidence)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Rejection email आता है: "Issue found: <Policy name>"
Step 2 → Console → Policy and programs → Policy status → विवरण देखो
Step 3 → कारण पहचानो (नीचे की table)
Step 4 → Fix करो (code / listing / Console form)
Step 5 → Code बदला हो तो नया versionCode; सिर्फ़ listing हो तो resubmit
Step 6 → Release notes / "Notes for review" में लिखो क्या ठीक किया
Step 7 → दोबारा "Send for review"
Step 8 → गलत लगे तो Appeal (सबूत के साथ)
```

**Common reasons table:**
```
Reason                           Fix
────────────────────────────────────────────────────────────────────
Privacy policy missing / broken  Public HTTPS URL, matches Data safety
Data safety mismatch             Declare every SDK's data (analytics, ads, crash)
Restricted permissions (SMS,     Remove, or fill Permissions Declaration form
 call log, background location)
Crashes / broken login           Test release build; give reviewer demo account
Misleading metadata              No fake claims, no keyword stuffing, no emojis in title
Payments (digital goods)         Use Google Play Billing, not UPI/cards, for in-app digital goods
Target API level too low         Upgrade Expo SDK / targetSdkVersion
Missing account deletion         In-app delete + web link
Impersonation / IP               Don't use others' brand names/logos
Families/children policy         Ads SDK must be certified if kids are targeted
Deceptive behaviour              No hidden features, no behavior change after review
```

**Console screens (described in words):**
- **Policy status page:** Table rows: Policy name, "Rejected"/"Warning", date, aur "View details". Details me exact violation text aur "Fix and resubmit" instructions.
- **Rejection email:** Subject "Action required: Your app has been rejected", app name, versionCode, aur policy link.

---

## 🟡 Real World Example
Ek chhota Indian shopping app ne **UPI / Razorpay** se digital subscription bech di aur reject hua — Google ke payments policy ke hisaab se in-app **digital goods** ke liye Google Play Billing zaroori hota hai (physical goods jaise Zomato/Swiggy ke food orders ke liye external payment chalta hai). Dusra example: ek loan app ne contacts/SMS permission bina declaration li, aur remove hui.

## 🟡 Real Example Hindi mein
एक छोटी Indian shopping app ने **UPI / Razorpay** से digital subscription बेची और reject हुई — Google की payments policy के अनुसार in-app **digital goods** के लिए Google Play Billing ज़रूरी है (physical goods जैसे Zomato/Swiggy के food orders के लिए external payment चलता है)। दूसरा उदाहरण: एक loan app ने बिना declaration contacts/SMS permission ली और हटा दी गई।

---

## 💻 Code Example — Basic
Pre-submission checklist runner (Node): `app.json` aur `eas.json` ke basic checks.

```js
// checklist.js — run: node checklist.js
const fs = require('fs');                                     // file system
// helper: JSON safely read
const read = (p) => { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return null; } };
// config files
const app = read('./app.json');
const eas = read('./eas.json');
// issues list
const issues = [];
// app.json hona chahiye
if (!app) issues.push('app.json not found/invalid');
// package placeholder check
const pkg = app?.expo?.android?.package;
if (!pkg) issues.push('android.package missing');
else if (/^(com\.example|host\.exp)/.test(pkg)) issues.push('placeholder package: ' + pkg);
// build type AAB hona chahiye
const bt = eas?.build?.production?.android?.buildType;
if (bt && bt !== 'app-bundle') issues.push('production buildType should be app-bundle');
// service account JSON ko git me nahi hona chahiye
if (fs.existsSync('./.gitignore') && !/play-service-account/.test(fs.readFileSync('./.gitignore', 'utf8'))) {
  issues.push('add play-service-account.json to .gitignore');
}
// result
console.log(issues.length ? 'Issues:\n- ' + issues.join('\n- ') : 'Basic checks passed');
process.exit(issues.length ? 1 : 0);
```

## 💻 Code Example — Advanced
Digital goods ke liye Google Play Billing ke bajay external payment ka galat use na ho, uske liye platform guard — pattern (library: `react-native-iap` ya `expo-iap`; native, *not run*):

```jsx
// Paywall.jsx — Android digital goods => Play Billing
import React from 'react';                                   // React
import { Platform, Pressable, Text, Alert } from 'react-native'; // RN components

// Product ke type ke hisaab se payment route
// 'digital' => Play Billing (IAP); 'physical' => UPI/Razorpay allowed
export default function Paywall({ product, startIap, startUpi }) {
  // press handler
  const buy = async () => {
    try {
      // digital goods => store billing (Google policy)
      if (product.type === 'digital') {
        // Android + iOS dono me store IAP use karo
        await startIap(product.sku);
        return;
      }
      // physical goods (food, groceries) => external payment ok
      await startUpi(product.id);
    } catch (e) {
      // user cancel ya payment error
      Alert.alert('Payment failed', String(e?.message || e));
    }
  };
  // UI
  return (
    <Pressable onPress={buy}>
      <Text>{product.type === 'digital' ? `Subscribe (${Platform.OS} store)` : 'Pay with UPI'}</Text>
    </Pressable>
  );
}
```

```json
{
  "expo": {
    "android": {
      "package": "in.foodie.app",
      "blockedPermissions": ["android.permission.READ_SMS", "android.permission.READ_CALL_LOG"]
    }
  }
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android rejection | iOS rejection |
|---------|-------------------|---------------|
| Top reason | Policy: privacy/Data safety/permissions | Guideline 2.1 crashes/bugs, 4.x design, 5.x legal |
| Payments | Play Billing for digital goods | In-App Purchase for digital goods |
| Account deletion | Required | Required |
| Test credentials | App access section | App Review Information |
| Metadata | Title/description policy | Metadata guideline 2.3 |
| Login required | Provide demo account | Provide demo account |

---

## 🟠 Expo vs CLI Difference
Expo way:
```json
{ "expo": { "android": { "blockedPermissions": ["android.permission.READ_SMS"] } } }
```
CLI way:
```xml
<!-- AndroidManifest.xml me permission hatao -->
<uses-permission android:name="android.permission.READ_SMS" tools:node="remove" />
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Placeholder icon, "lorem ipsum" description.
✅ **Correct:** Final assets aur real description.

❌ **Mistake 2:** Review team login nahi kar pa rahi.
✅ **Correct:** App access me working demo credentials + steps.

❌ **Mistake 3:** Kids ko target karke generic ads SDK lagana.
✅ **Correct:** Families policy: certified ads SDK ya ads hatao.

❌ **Mistake 4:** Purana targetSdk.
✅ **Correct:** Expo SDK upgrade (current required target API Google docs me dekho).

❌ **Mistake 5:** Rejection ke baad bina badlaav ke resubmit.
✅ **Correct:** Reason fix karo; notes likho.

---

## 🧠 Tricky Interview Question
**Q: App "Zomato jaisi" hai aur Zomato jaise logo/colors use kiye, kya problem hai?**

**Answer:** **Impersonation / Intellectual Property** policy violation. Kisi doosre brand ka naam, logo, ya misleading similarity reject/removal ka karan hai. Fix: apna original branding, title me kisi dusre brand ka naam nahi, screenshots me apni UI. Agar authorised partner ho to written permission/evidence appeal me do.

---

## ⚫ Interview Questions + Answers

**Q1: Sabse common rejection reasons?**
A1: Privacy/Data safety issues, restricted permissions, crashes/login problems, misleading metadata, payments policy, targetSdk, account deletion.

**Q2: Digital goods ke liye UPI chalega?**
A2: In-app digital goods/subscriptions ke liye Google Play Billing zaroori hai; physical goods/services me external payments allowed (policy exceptions ke saath — current policy check karo).

**Q3: Restricted permission chahiye to?**
A3: Permissions Declaration form, core-functionality justification, kabhi video.

**Q4: Galat rejection ho to?**
A4: Appeal form (evidence ke saath), ya fix aur resubmit.

**Q5: Rejection se bachne ka best tareeka?**
A5: Pre-launch report, release build test, honest declarations, demo credentials, up-to-date targetSdk.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Har release se pehle ek final checklist ke roop me.

❌ Avoid when:
- (Skip mat karo.) Sirf is list par depend mat raho — Policy Center updates padho.

---

## 📊 Visual Diagram
```
 REJECTION → read email → identify policy
    │
    ├─ Privacy/Data safety ─► fix forms + policy URL
    ├─ Permissions ──────────► remove / declare
    ├─ Crash / login ────────► demo account + test release
    ├─ Metadata ─────────────► honest title/screenshots
    ├─ Payments ─────────────► Play Billing for digital goods
    ├─ targetSdk ────────────► upgrade Expo SDK
    └─ Account deletion ─────► in-app + web
          │
          ▼
    resubmit (new versionCode if code changed) / appeal
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Policy Center | Google's rules site | Google के नियमों की साइट |
| Permissions Declaration | Form for sensitive permissions | संवेदनशील permissions का form |
| Play Billing | Google's payment system | Google का payment system |
| Impersonation | Pretending to be another brand | दूसरे brand की नकल |
| targetSdk | Android API target | Android API लक्ष्य |
| Appeal | Dispute a rejection | Rejection को चुनौती |

---

## ⚡ 3-Line Summary
**English:**
1. Top causes: privacy/Data safety, permissions, crashes, metadata, payments, targetSdk, account deletion.
2. Read the policy name in the email, fix it, resubmit or appeal.
3. Prevent with a pre-launch checklist and honest declarations.

**Hindi:**
1. मुख्य कारण: privacy/Data safety, permissions, crashes, metadata, payments, targetSdk, account deletion।
2. Email में policy का नाम पढ़ो, ठीक करो, resubmit या appeal करो।
3. Pre-launch checklist और ईमानदार declarations से इनसे बचो।

---

## ➡️ Next Topic
**iOS Publishing** — App Store Connect और TestFlight (ios folder), Android publishing complete।
