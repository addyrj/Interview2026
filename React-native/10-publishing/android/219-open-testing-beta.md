---

# 219. Open Testing (Beta)
# हिंदी में: Open Testing (Beta)
# Platform: Android ✅ | iOS ❌ (iOS ka equivalent: TestFlight public link)

> Expo SDK 53/54 (check current docs — APIs change between SDKs). Console menu names badal sakte hain.

---

## 🔵 Simple Definition (English)
**Open testing** is a public beta: your app appears on the Play Store with a **"Early access"** label, and **anyone** can join the test (no email list needed). You can optionally cap the number of testers. Builds go through Google review.

## 🔵 सरल परिभाषा (Hindi)
**Open testing** एक public beta है: आपकी app Play Store पर **"Early access"** label के साथ दिखती है और **कोई भी** test join कर सकता है (email list ज़रूरी नहीं)। आप चाहें तो testers की संख्या सीमित कर सकते हो। Builds का Google review होता है।

---

## 🔴 Problem it Solves
- Closed groups are small; you want large-scale real-world feedback and device coverage.
- Test on thousands of device models/network conditions before production.
- Build hype and gather reviews/feedback privately before launch.

## 🔴 यह क्यों बना? (Hindi)
- Closed groups छोटे होते हैं; आपको बड़े पैमाने पर असली feedback और device coverage चाहिए।
- Production से पहले हज़ारों device models/network conditions पर test।
- Launch से पहले hype बनाना और private feedback लेना।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Play Console → Test and release → Testing → Open testing
Step 2 → Countries/regions chuno
Step 3 → (Optional) Tester cap set karo (e.g. 1000)
Step 4 → Feedback email / URL do (public reviews se bachne ke liye)
Step 5 → Create release → AAB upload / Closed se promote
Step 6 → Store listing aur App content complete honi chahiye (privacy, rating, data safety)
Step 7 → Send for review → pass
Step 8 → Store par "Join the beta" button / "Early access" label dikhta hai
Step 9 → Users join → install → feedback
Step 10 → Stable hone par Production me promote
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Play Console → Test and release → Testing → Open testing
Step 2 → Countries/regions चुनो
Step 3 → (Optional) Testers की सीमा set करो (जैसे 1000)
Step 4 → Feedback email / URL दो (public reviews से बचने के लिए)
Step 5 → Create release → AAB upload / Closed से promote
Step 6 → Store listing और App content पूरा होना चाहिए (privacy, rating, data safety)
Step 7 → Send for review → पास
Step 8 → Store पर "Join the beta" button / "Early access" label दिखता है
Step 9 → Users join करते हैं → install → feedback
Step 10 → Stable होने पर Production में promote
```

**Console screens (described in words):**
- **Open testing page:** Tabs "Releases", "Countries/regions", "Testers". Testers tab me toggle/field "Limit number of testers" aur "Feedback URL or email address".
- **Play Store (user side):** App page par "Early access" tag, "Join the beta" button; join ke baad "Install" aur "Leave" option.

---

## 🟡 Real World Example
**WhatsApp** aur **Instagram** jaisi badi apps ke public beta programs hote hain jahan koi bhi Play Store se join karke naye features pehle try kar sakta hai. India me gaming ya fintech apps (Paytm, PhonePe jaise) festive season se pehle beta me naya UI test kar sakti hain jo alag device models (budget Android phones) par check hota hai.

## 🟡 Real Example Hindi mein
**WhatsApp** और **Instagram** जैसी बड़ी apps के public beta programs होते हैं जहाँ कोई भी Play Store से join करके नए features पहले आज़मा सकता है। भारत में gaming या fintech apps (Paytm, PhonePe जैसी) त्योहारों से पहले beta में नया UI test कर सकती हैं, जो अलग device models (budget Android phones) पर जाँचा जाता है।

---

## 💻 Code Example — Basic
`eas.json` beta track par submit:

```json
{
  "cli": { "version": ">= 12.0.0" },
  "submit": {
    "beta": {
      "android": {
        "serviceAccountKeyPath": "./secrets/play-service-account.json",
        "track": "beta",
        "releaseStatus": "completed"
      }
    }
  }
}
```

```bash
# beta (open testing) par latest build
eas submit -p android --profile beta --latest
```

## 💻 Code Example — Advanced
Beta users ke liye feature flag (remote config se) — risky feature sirf beta channel pe dikhao. Pure JS logic, Node me chal sakta hai:

```js
// flags.js — run: node flags.js
// channel env se aata hai (EAS build profile ya app config extra)
function isBeta(channel) {
  // sirf 'beta' / 'alpha' ko beta maano
  return channel === 'beta' || channel === 'alpha';
}

// feature ko flag ke saath define karo
const FEATURES = {
  newCheckout: { betaOnly: true },   // naya checkout sirf beta me
  darkMode: { betaOnly: false },     // sabke liye
};

// feature on/off decide karne wala function
function enabled(name, channel) {
  // feature ka config
  const f = FEATURES[name];
  // unknown feature => off
  if (!f) return false;
  // betaOnly hai to sirf beta channel me
  return f.betaOnly ? isBeta(channel) : true;
}

// quick tests
console.log(enabled('newCheckout', 'beta'));        // true
console.log(enabled('newCheckout', 'production'));  // false
console.log(enabled('darkMode', 'production'));     // true
console.log(enabled('unknown', 'beta'));            // false
```

```bash
# Production me promote karte hi newCheckout band rahega jab tak flag badla nahi jata
```

---

## 📱 Android vs iOS Difference
| Feature | Android Open Testing | iOS TestFlight Public Link |
|---------|----------------------|----------------------------|
| Who joins | Anyone from Play Store | Anyone with the link |
| Visibility | Store par "Early access" | Link se (store par nahi) |
| Tester cap | Optional cap | Up to 10,000 |
| Review | Google review | Beta App Review |
| Reviews | Private feedback (beta reviews alag) | Private feedback |
| Expiry | None | 90 days |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas submit -p android --profile beta --latest   # beta track
```
CLI way:
```bash
fastlane supply --aab app-release.aab --track beta   # beta track
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Unfinished/unstable build ko open beta me daalna.
✅ **Correct:** Pehle internal/closed me stabilise karo.

❌ **Mistake 2:** Tester cap set na karna aur server overload ho jana.
✅ **Correct:** Backend capacity ke hisaab se cap rakho.

❌ **Mistake 3:** Feedback email na dena.
✅ **Correct:** Feedback channel do, taaki critical bugs public review me na aayein.

❌ **Mistake 4:** Beta aur production ke liye alag backend config bhool jana.
✅ **Correct:** Env/channel se API URL alag rakho.

---

## 🧠 Tricky Interview Question
**Q: Beta me 10 lakh users aa gaye aur backend crash. Beta ko turant band kaise karte hain?**

**Answer:** Play Console → Open testing → "Pause track" ya track ko "Stop testing"/release halt karo; naye users join nahi kar payenge. Pehle se install log wo build rakhenge — unhe server side se **kill switch/remote config** se feature band karna padega ya force-update dena padega. Isliye cap + kill switch + rate-limiting pehle se rakhte hain. Tester cap launch se pehle hi set karna sahi hai.

---

## ⚫ Interview Questions + Answers

**Q1: Open testing me kaun join kar sakta hai?**
A1: Koi bhi Play Store user (countries jo aapne select kiye).

**Q2: Open testing me review hota hai?**
A2: Haan, Google review hota hai.

**Q3: Beta users production me automatically update hote hain?**
A3: Jab production release newer versionCode se rollout hota hai, beta users bhi use paa sakte hain (versionCode ordering par depend).

**Q4: Tester limit kyun lagate hain?**
A4: Server load control aur controlled feedback ke liye.

**Q5: Beta ko production me kaise le jaate hain?**
A5: "Promote release" → Production, same AAB.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Large-scale device/network coverage chahiye.
- Major redesign ka public feedback.

❌ Avoid when:
- Confidential feature/unreleased brand — closed testing.
- Security-sensitive unfinished build.

---

## 📊 Visual Diagram
```
 Internal ─► Closed ─► OPEN (public beta) ─► Production
                         │
              ┌──────────┴──────────┐
              │ Anyone joins        │
              │ cap + feedback mail │
              └─────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Early access | Beta label on store | Beta का label |
| Tester cap | Max beta users | Testers की सीमा |
| Kill switch | Remote off for a feature | Feature बंद करने का स्विच |
| Feedback URL | Where bugs go | Feedback भेजने का पता |
| Pause track | Stop new joins | नए users रोकना |

---

## ⚡ 3-Line Summary
**English:**
1. Open testing = public beta on Play Store, anyone can join.
2. Set cap, feedback email, and kill switches.
3. Promote the same AAB to production when stable.

**Hindi:**
1. Open testing = Play Store पर public beta, कोई भी join कर सकता है।
2. Cap, feedback email और kill switch रखो।
3. Stable होने पर वही AAB production में promote करो।

---

## ➡️ Next Topic
**220. Production Release** — अब सबके लिए app live।
