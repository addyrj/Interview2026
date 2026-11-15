---

# 211. Create Developer Account (Play Store)
# हिंदी में: Play Store Developer Account बनाना
# Platform: Android ✅ | iOS ❌

> Expo SDK 53/54 (check current docs — APIs change between SDKs). Yeh topic mostly Google Play Console ka web process hai, isliye Expo SDK par depend nahi karta. Play Console ke menu names aur policies badalte rehte hain — hamesha current Google docs check karo.

---

## 🔵 Simple Definition (English)
A **Google Play Developer account** is the account you must own before you can publish any app on the Play Store. You register at play.google.com/console, pay a one-time fee of **USD 25**, verify your identity, and then you get access to **Play Console** (the dashboard to upload and manage apps).

## 🔵 सरल परिभाषा (Hindi)
**Google Play Developer account** वह account है जो Play Store पर app publish करने से पहले ज़रूरी है। आप play.google.com/console पर register करते हो, एक बार **25 USD** fee देते हो, अपनी identity verify करते हो, और फिर आपको **Play Console** (app upload और manage करने का dashboard) मिलता है।

---

## 🔴 Problem it Solves
- Anyone could upload fake, spam, or malware apps anonymously.
- Google needs to know **who** is responsible for an app (legal name, address, contact) for policy and legal reasons.
- Users need trust: the "Developer" name on the store page must be a verified person or company.
- The one-time fee + ID verification reduces mass spam accounts.

## 🔴 यह क्यों बना? (Hindi)
- कोई भी anonymously fake, spam या malware app upload कर सकता था।
- Google को पता होना चाहिए कि app का **ज़िम्मेदार कौन** है (legal name, address, contact)।
- Users का trust: store page पर "Developer" का नाम verified person या company होना चाहिए।
- One-time fee + ID verification से spam accounts कम होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Google account banao (Gmail) — dedicated email use karo, personal nahi
Step 2 → play.google.com/console par jao → "Create account"
Step 3 → Account type choose karo: Personal ya Organization
Step 4 → Developer name, address, phone, contact email daalo
Step 5 → USD 25 one-time registration fee pay karo (international card chahiye)
Step 6 → Identity verification: government ID (Aadhaar/PAN/Passport/DL) + selfie/address proof
Step 7 → Organization ho to D-U-N-S number + website verify karo
Step 8 → Phone verify (SMS) + Android device verify (Play Console app se)
Step 9 → Verification approve hone ka wait (kuch din — kabhi zyada)
Step 10 → Play Console unlock → "Create app" kar sakte ho
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → एक Google account बनाओ — personal की जगह dedicated email रखो
Step 2 → play.google.com/console खोलो → "Create account"
Step 3 → Account type चुनो: Personal या Organization
Step 4 → Developer name, address, phone, contact email भरो
Step 5 → 25 USD one-time fee दो (international card लगेगा)
Step 6 → Identity verification: government ID + selfie / address proof
Step 7 → Organization है तो D-U-N-S number + website verify
Step 8 → Phone (SMS) verify + Android device verify (Play Console app से)
Step 9 → Approval का इंतज़ार (कुछ दिन, कभी ज़्यादा)
Step 10 → Play Console खुल गया → "Create app" कर सकते हो
```

**Console screens (described in words):**
- **Sign-up screen:** Ek simple form — "Developer account type" ke do radio-style cards: *Yourself* (personal) aur *An organization*. Neeche developer name field aur "I agree to Developer Distribution Agreement" checkbox.
- **Payment screen:** Standard Google Pay checkout jisme "Registration fee USD 25.00" line dikhti hai, card details aur "Pay" button.
- **Identity verification screen:** Document type dropdown (ID type), photo upload area, aur verification status ka banner — "Verification in progress" (peela) ya "Verified" (hara).
- **Play Console home (after approval):** Left sidebar me "Home, Inbox, All apps, Users and permissions, Settings". Beech me "Create app" ka blue button.

---

## 🟡 Real World Example
**Zomato / Swiggy / Paytm** are published under **Organization accounts** (registered companies with D-U-N-S numbers). Their Play Store page shows the company name (e.g. "Zomato Limited") — that is the verified developer identity. A solo Indian developer shipping a small side-project would typically use a **Personal account** with their own name.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy / Paytm** जैसी apps **Organization accounts** (registered company, D-U-N-S number) से publish होती हैं। Play Store page पर company का नाम (जैसे "Zomato Limited") दिखता है — वही verified developer identity है। एक solo Indian developer जो छोटा side-project डालता है वह आमतौर पर अपने नाम से **Personal account** लेता है।

---

## 💻 Code Example — Basic
Account banana code se nahi hota, par pehle ye checklist script se verify kar sakte ho (Node, kuch install nahi chahiye).

```js
// checklist.js — account banane se pehle readiness check (run: node checklist.js)
const readiness = {
  // dedicated Google account hai? true/false
  dedicatedGoogleAccount: true,
  // international card (credit/debit with international payments on)
  internationalCard: true,
  // government ID ready
  governmentId: true,
  // organization ke liye D-U-N-S number
  dunsNumber: false,
  // account type
  accountType: 'personal',
};

// organization ho to D-U-N-S zaroori hai
const needsDuns = readiness.accountType === 'organization';

// missing items collect karo
const missing = Object.entries(readiness)
  // accountType skip karo — woh checklist item nahi hai
  .filter(([k]) => k !== 'accountType')
  // D-U-N-S sirf organization ke liye zaroori
  .filter(([k, v]) => !v && (k !== 'dunsNumber' || needsDuns))
  // sirf key naam rakho
  .map(([k]) => k);

// result print karo
console.log(missing.length ? 'Missing: ' + missing.join(', ') : 'Ready to register');
```

## 💻 Code Example — Advanced
Account ban jaane ke baad project ko us account se jodne ke liye `app.json` me unique package name aur EAS config chahiye.

```json
{
  "expo": {
    "name": "MyFoodApp",
    "slug": "my-food-app",
    "version": "1.0.0",
    "android": {
      "package": "com.mycompany.myfoodapp",
      "versionCode": 1
    }
  }
}
```

```json
{
  "cli": { "version": ">= 12.0.0" },
  "build": {
    "production": {
      "android": { "buildType": "app-bundle" }
    }
  }
}
```

```bash
# EAS CLI install + login (Expo account chahiye, Play account se alag hai)
npm install -g eas-cli
# Expo account me login
eas login
# project ko EAS se link karo
eas init
# production AAB build — Play Console me upload ke liye
eas build --platform android --profile production
```

`package` ek baar Play Console me app create hone ke baad **change nahi hota** — sochkar rakho.

---

## 📱 Android vs iOS Difference
| Feature | Android (Google Play) | iOS (Apple) |
|---------|----------------------|-------------|
| Fee | USD 25 one-time | USD 99 per year |
| Individual / Org | Personal ya Organization | Individual ya Organization |
| Org verification | D-U-N-S number | D-U-N-S number |
| Identity check | Government ID + phone/device verify | Apple ID + ID verification |
| Approval time | Kuch din (kabhi zyada) | Usually 1-2 din (org me zyada) |
| Testing requirement for new personal accounts | Closed test (12 testers, 14 din) production se pehle — current rule check karo | Aisa koi rule nahi |
| Dashboard | Play Console | App Store Connect |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Expo EAS Build — Play account se koi direct link nahi, bas AAB banta hai
eas build --platform android --profile production
```
CLI way:
```bash
# Bare React Native — local Gradle build se AAB
cd android && ./gradlew bundleRelease
```
Dono me Play Developer account same lagta hai. Fark sirf AAB banane aur signing manage karne me hai.

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Personal Gmail se account banana aur baad me company ko transfer karna chahna.
✅ **Correct:** Shuru se dedicated email + sahi account type (Personal/Organization) chuno. Type baad me aasani se nahi badalta.

❌ **Mistake 2:** Developer name me brand ya kisi aur company ka naam likhna jo aapka nahi.
✅ **Correct:** Wahi naam daalo jo government ID / company registration se match kare, warna verification fail.

❌ **Mistake 3:** Domestic-only debit card se payment ki koshish.
✅ **Correct:** International transactions enabled card use karo.

❌ **Mistake 4:** Personal account bana kar sochna ki turant production release ho jayega.
✅ **Correct:** Naye personal accounts ko pehle closed testing (testers + 14 din) complete karna pad sakta hai — pehle se plan karo.

---

## 🧠 Tricky Interview Question
**Q: Client ne ek Play account banaya aur aapko "Admin" access diya. Kya aap us app ke owner ho gaye?**

**Answer:** Nahi. **Owner** account holder (jisne register kiya) hota hai. Aap "Users and permissions" me invited user ho — aapke paas jo permissions diye gaye wahi chalenge (release manager, admin etc.). App, uska package name aur data account se bandha hai. Isliye agencies ko client ke account me access lena chahiye, apne account me client ka app publish nahi karna chahiye — warna baad me transfer ka jhanjhat.

---

## ⚫ Interview Questions + Answers

**Q1: Play Developer account ki fee kitni hai?**
A1: USD 25, one-time. iOS ki tarah yearly renewal nahi hota.

**Q2: Personal aur Organization account me kya fark hai?**
A2: Organization me D-U-N-S number aur company details/website verify hoti hai; store par company name dikhta hai. Personal me aapka legal naam aur address verify hota hai. Naye personal accounts par closed-testing requirement lag sakti hai (current policy check karo).

**Q3: Kya ek account se multiple apps publish ho sakte hain?**
A3: Haan, ek account me bahut saari apps ban sakti hain, har app ka unique package name hota hai.

**Q4: Verification fail ho jaye to kya karein?**
A4: Console ka message padho — usually naam mismatch ya blur document hota hai. Sahi documents dobara upload karo ya Play support se contact karo.

**Q5: Team members ko access kaise dein?**
A5: Play Console → Users and permissions → Invite new users. Role-based permissions (app-level ya account-level) dete hain.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Aap Android app publicly Play Store par daalna chahte ho.
- Company ki app hai — Organization account lo.
- Testing tracks (Internal/Closed) chahiye — woh bhi Console se hi milte hain.

❌ Avoid when:
- Sirf APK direct share karni hai (sideload) — tab account zaroori nahi, par distribution limited.
- Sirf internal enterprise app hai — managed Google Play ya Firebase App Distribution consider karo.

---

## 📊 Visual Diagram
```
 Google Account
      │
      ▼
 play.google.com/console ── Create account
      │
      ├── Type: Personal ──────────┐
      └── Type: Organization ──┐   │
                               ▼   ▼
                    Pay USD 25 (one-time)
                               │
                               ▼
              ID verification (+ D-U-N-S for org)
                               │
                               ▼
                    Phone + device verify
                               │
                               ▼
                      Approved ✅ → Play Console
                               │
                               ▼
                         Create app (212)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Play Console | Google's dashboard to manage apps | Apps manage करने का dashboard |
| Developer account | Registered publisher identity | Publisher की पहचान |
| D-U-N-S | Business identification number | Company की unique ID |
| Verification | Identity/business check | पहचान की जाँच |
| Package name | Unique app ID (com.x.y) | App की unique ID |
| Owner | Account holder with full control | Account का मालिक |

---

## ⚡ 3-Line Summary
**English:**
1. Register at play.google.com/console, pay USD 25 once, choose Personal or Organization.
2. Verify identity (ID, phone, device; D-U-N-S for organizations) and wait for approval.
3. Plan for extra testing rules on new personal accounts before production release.

**Hindi:**
1. play.google.com/console पर register करो, एक बार 25 USD दो, Personal या Organization चुनो।
2. Identity verify करो (ID, phone, device; Organization के लिए D-U-N-S) और approval का इंतज़ार करो।
3. नए personal accounts पर production से पहले extra testing rules के लिए पहले से plan करो।

---

## ➡️ Next Topic
**212. Create New App in Play Console** — account ready hai, ab app ka entry banate hain.
