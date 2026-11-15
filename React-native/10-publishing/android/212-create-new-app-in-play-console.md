---

# 212. Create New App in Play Console
# हिंदी में: Play Console में नया App बनाना
# Platform: Android ✅ | iOS ❌

> Expo SDK 53/54 (check current docs — APIs change between SDKs). Console labels aur menu positions Google badalta rehta hai — screens ka description approximate hai.

---

## 🔵 Simple Definition (English)
Creating an app in Play Console means making an **empty app entry** (name, language, app/game, free/paid, declarations) that will later hold your store listing, releases, and policy forms. It does not upload any code yet. The app's **package name** gets locked when you upload your first AAB.

## 🔵 सरल परिभाषा (Hindi)
Play Console में app बनाने का मतलब है एक **खाली app entry** बनाना (नाम, भाषा, app/game, free/paid, declarations) जिसमें बाद में store listing, releases और policy forms भरे जाएँगे। अभी कोई code upload नहीं होता। पहला AAB upload करते ही app का **package name lock** हो जाता है।

---

## 🔴 Problem it Solves
- Google needs a container per app to track policy, releases, ratings, and statistics.
- Declarations (free/paid, ads, app vs game) must be made upfront because some of them (free -> paid) cannot be reversed.
- Teams need one place for listing, tracks, testers, and reports.

## 🔴 यह क्यों बना? (Hindi)
- Google को हर app के लिए एक container चाहिए जहाँ policy, releases, ratings और statistics track हों।
- कुछ declarations (जैसे free -> paid) बाद में बदले नहीं जा सकते, इसलिए शुरू में ही भरवाए जाते हैं।
- Team को listing, tracks, testers और reports के लिए एक ही जगह चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Play Console → "Create app" button
Step 2 → App name (max 30 chars, store par dikhega)
Step 3 → Default language (e.g. English (United States) ya Hindi)
Step 4 → App ya Game choose karo
Step 5 → Free ya Paid choose karo (free se paid baad me NAHI ho sakta)
Step 6 → Declarations: Developer Program Policies + US export laws accept
Step 7 → "Create app" → Dashboard khulta hai with setup checklist
Step 8 → Checklist ke tasks pura karo (rating, privacy, listing, ...)
Step 9 → Pehla AAB upload karo → package name lock
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Play Console → "Create app" button दबाओ
Step 2 → App name (अधिकतम 30 characters, store पर दिखेगा)
Step 3 → Default language चुनो (English (US) या Hindi)
Step 4 → App या Game चुनो
Step 5 → Free या Paid चुनो (free से paid बाद में नहीं हो सकता)
Step 6 → Declarations accept करो: Developer Program Policies + US export laws
Step 7 → "Create app" दबाओ → setup checklist वाला Dashboard खुलता है
Step 8 → Checklist के tasks पूरे करो (rating, privacy, listing ...)
Step 9 → पहला AAB upload करो → package name lock हो जाता है
```

**Console screens (described in words):**
- **All apps screen:** Upar right me neela "Create app" button. Beech me aapki apps ki list (icon, name, status).
- **Create app form:** "App name", "Default language" dropdown, "App or game" aur "Free or paid" ke radio buttons. Neeche "Declarations" ke checkboxes (policies, export laws) aur "Create app" button.
- **App dashboard:** Left sidebar: "Dashboard, Statistics, Publishing overview, Test and release, Grow users, Monetize, Policy and programs". Beech me "Set up your app" checklist — har task ke saamne tick ya arrow.

---

## 🟡 Real World Example
Jab **Swiggy** ya **Zomato** ek naya alag app launch karta hai (jaise Zomato ka "Blinkit" jaisa separate product, ya Swiggy ka Instamart standalone), to company ke existing Organization account me **naya app entry** banti hai — naya package name, alag listing, alag tracks. Purana app untouched rehta hai.

## 🟡 Real Example Hindi mein
जब **Swiggy** या **Zomato** कोई नया अलग app launch करता है, तो company के मौजूदा Organization account में **नई app entry** बनती है — नया package name, अलग listing, अलग tracks। पुराना app वैसा ही रहता है।

---

## 💻 Code Example — Basic
Console me app banane se pehle package name aur version ko app.json me taiyar rakho.

```json
{
  "expo": {
    "name": "FoodieIndia",
    "slug": "foodie-india",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "android": {
      "package": "in.foodie.app",
      "versionCode": 1,
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      }
    }
  }
}
```

## 💻 Code Example — Advanced
Package name validate karne ka script (Android rules: segments dot se alag, har segment letter se shuru, sirf letters/digits/underscore, kam se kam 2 segments).

```js
// validatePackage.js — run: node validatePackage.js
// Android applicationId ke liye regex: kam se kam do segments
const PACKAGE_RE = /^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)+$/;

// package name check karne wala function
function validatePackage(name) {
  // type check
  if (typeof name !== 'string') return { ok: false, reason: 'string chahiye' };
  // regex se format check
  if (!PACKAGE_RE.test(name)) return { ok: false, reason: 'format galat' };
  // Java keywords segments ke liye allowed nahi (kuch common)
  const reserved = ['new', 'class', 'public', 'int', 'package'];
  // har segment ko reserved se compare karo
  const bad = name.split('.').find((s) => reserved.includes(s));
  // reserved mila to reject
  if (bad) return { ok: false, reason: `reserved word: ${bad}` };
  // sab theek
  return { ok: true };
}

// tests
console.log(validatePackage('in.foodie.app'));   // ok
console.log(validatePackage('foodie'));          // fail: ek hi segment
console.log(validatePackage('com.1app.test'));   // fail: digit se shuru
console.log(validatePackage('com.new.app'));     // fail: reserved
```

```bash
# Build karke AAB do taiyar rakho — pehli upload ke liye (212 ke baad 216 me upload)
eas build --platform android --profile production
```

---

## 📱 Android vs iOS Difference
| Feature | Android (Play Console) | iOS (App Store Connect) |
|---------|------------------------|-------------------------|
| Unique ID | Package name (`com.x.y`) | Bundle ID (`com.x.y`) |
| ID lock | Pehle AAB upload par lock | App record banate hi Bundle ID lock |
| App name limit | 30 characters | 30 characters |
| Free to paid | Nahi ho sakta | Price change ho sakta hai |
| Create flow | "Create app" form | "New App" form + SKU |
| First upload | Console se manual (API se nahi) | Xcode / Transporter / EAS Submit |

---

## 🟠 Expo vs CLI Difference
Expo way:
```json
{ "expo": { "android": { "package": "in.foodie.app", "versionCode": 1 } } }
```
CLI way:
```groovy
// android/app/build.gradle
android {
    defaultConfig {
        // unique application id
        applicationId "in.foodie.app"
        // first release number
        versionCode 1
        // user ko dikhne wala version
        versionName "1.0.0"
    }
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** `com.example.app` ya `host.exp.exponent` jaise placeholder package name rakhna.
✅ **Correct:** Apni domain ulti karke naam rakho — `in.company.app`. Placeholders reject ho sakte hain ya conflict karte hain.

❌ **Mistake 2:** Free app banana jabki baad me paid karna hai.
✅ **Correct:** Free se paid nahi ho sakta. Paid chahiye to shuru me paid chuno, ya free + in-app purchase model use karo.

❌ **Mistake 3:** App name me keywords stuff karna ("Best Food App India Cheap Fast").
✅ **Correct:** Chhota brand name rakho; keywords description me. Spam title policy violation hai.

❌ **Mistake 4:** Package name baad me badalna chaha.
✅ **Correct:** Upload ke baad package name fix hai — badalna = naya app. Pehle hi finalize karo.

---

## 🧠 Tricky Interview Question
**Q: Aapne galti se `com.test.app` se production app upload kar diya aur ab users aa gaye. Package name kaise badlenge?**

**Answer:** Badal nahi sakte. Package name app ki identity hai. Naya package name = naya app entry. Existing users ko naye app par migrate karne ke liye purani app me message/redirect dena padega, aur reviews/downloads reset ho jayenge. Isliye pehle hi sahi `applicationId` fix karo. Expo me `android.package` aur bare me `applicationId` — dono same hone chahiye release se pehle.

---

## ⚫ Interview Questions + Answers

**Q1: App aur Game me choose karne se kya farak padta hai?**
A1: Category aur kuch policy sections (jaise ratings questions) alag hote hain. Baad me category Store listing se badli ja sakti hai, par shuru ka declaration sochkar do.

**Q2: Package name kab lock hota hai?**
A2: Pehla AAB (kisi bhi track me) upload karte hi lock ho jata hai.

**Q3: Kya app delete ho sakti hai?**
A3: Unpublish kar sakte ho; Play Console se app ka entry permanently delete aam taur par nahi hota. Package name dobara use nahi ho sakta.

**Q4: Default language kya hoti hai?**
A4: Store listing ki base language. Doosri languages ke liye translations add kar sakte ho.

**Q5: Ek hi package name se do apps ban sakti hain?**
A5: Nahi, package name Google Play par globally unique hai.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Naya product/brand launch kar rahe ho.
- Alag audience ya alag monetization chahiye.

❌ Avoid when:
- Sirf app ka naya version hai — wahi app me naya release banao.
- Alag flavors (staging) chahiye — internal track use karo, naya app nahi.

---

## 📊 Visual Diagram
```
 Play Console
    │
    ▼
 Create app  ──►  App name + language + App/Game + Free/Paid
    │
    ▼
 Dashboard checklist
    ├── Privacy policy (214)
    ├── Content rating (213)
    ├── Data safety / App content
    ├── Store listing (215)
    └── Release: upload AAB (216)  ← package name LOCK
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Package name | Unique app ID | App की unique ID |
| App entry | Record inside Play Console | Console में app का record |
| Declarations | Policy confirmations | Policy की स्वीकृति |
| Dashboard | App overview page | App का overview page |
| Free/Paid | Pricing type | मुफ़्त/भुगतान वाला |

---

## ⚡ 3-Line Summary
**English:**
1. "Create app" makes an empty app entry with name, language, app/game, free/paid.
2. Package name locks at first AAB upload; free cannot become paid later.
3. Then complete the dashboard checklist: rating, privacy, listing, release.

**Hindi:**
1. "Create app" नाम, भाषा, app/game, free/paid के साथ खाली app entry बनाता है।
2. पहले AAB upload पर package name lock होता है; free app बाद में paid नहीं हो सकती।
3. फिर dashboard checklist पूरी करो: rating, privacy, listing, release।

---

## ➡️ Next Topic
**213. App Content Rating** — IARC questionnaire भरकर age rating लेना।
