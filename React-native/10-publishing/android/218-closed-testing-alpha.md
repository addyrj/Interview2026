---

# 218. Closed Testing (Alpha)
# हिंदी में: Closed Testing (Alpha)
# Platform: Android ✅ | iOS ❌ (iOS ka equivalent: TestFlight external groups)

> Expo SDK 53/54 (check current docs — APIs change between SDKs). Naye personal accounts ke liye closed testing ki shart (12 testers x 14 din — 2024-25 rule) badal sakti hai; Play Console help me current requirement dekho.

---

## 🔵 Simple Definition (English)
**Closed testing** lets you release a build to a **limited, invite-only group** (email lists or Google Groups) through the Play Store. Unlike internal testing, closed testing builds go through Google's **review**. For new **personal** developer accounts, a closed test with enough testers for a minimum period is currently required before you can apply for production access.

## 🔵 सरल परिभाषा (Hindi)
**Closed testing** में आप build को Play Store के ज़रिए **सीमित, invite-only group** (email lists या Google Groups) को release करते हो। Internal testing के उलट, closed testing builds का Google **review** होता है। नए **personal** developer accounts के लिए, production access माँगने से पहले पर्याप्त testers के साथ minimum अवधि का closed test फ़िलहाल ज़रूरी है।

---

## 🔴 Problem it Solves
- You want real users (not just your team) to try the app, but not the whole world.
- Collect feedback and crash data before a public release.
- Satisfy Google's requirement for new personal accounts (proof of real testing).

## 🔴 यह क्यों बना? (Hindi)
- आप चाहते हो कि असली users (सिर्फ़ आपकी team नहीं) app आज़माएँ, पर पूरी दुनिया नहीं।
- Public release से पहले feedback और crash data चाहिए।
- नए personal accounts के लिए Google की शर्त पूरी करनी है (असली testing का सबूत)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Play Console → Test and release → Testing → Closed testing
Step 2 → "Create track" (default "Alpha" ya custom naam, e.g. "Beta-Friends")
Step 3 → Testers: email list ya Google Group chuno
Step 4 → Countries/regions chuno
Step 5 → Create release → AAB upload (ya Internal se promote)
Step 6 → Release notes → Save → "Send for review"
Step 7 → Review pass hone par testers ko opt-in link bhejo
Step 8 → Testers join karke install karte hain; feedback URL/email par bhejte hain
Step 9 → New personal account: 12+ testers ko 14 din continuously opted-in rakho
Step 10 → "Apply for production" (Dashboard) → Google review
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Play Console → Test and release → Testing → Closed testing
Step 2 → "Create track" (default "Alpha" या custom नाम, जैसे "Beta-Friends")
Step 3 → Testers: email list या Google Group चुनो
Step 4 → Countries/regions चुनो
Step 5 → Create release → AAB upload (या Internal से promote)
Step 6 → Release notes → Save → "Send for review"
Step 7 → Review पास होने पर testers को opt-in link भेजो
Step 8 → Testers join करके install करते हैं; feedback URL/email पर भेजते हैं
Step 9 → नया personal account: 12+ testers को लगातार 14 दिन opted-in रखो
Step 10 → "Apply for production" (Dashboard) → Google review
```

**Console screens (described in words):**
- **Closed testing page:** Track ki list (Alpha etc.), har ke saamne status ("Active", "Draft") aur "Manage track" button.
- **Testers tab:** "Email lists" ya "Google Groups" selection; tester count; "Copy link" button; feedback email field.
- **Dashboard:** "Apply for production" card jisme progress, jaise "12 testers opted in, 14 days" ka checklist; condition poori hone par button enable hota hai (UI/wording change ho sakti hai).

---

## 🟡 Real World Example
Ek naya Indian fintech startup (Paytm-jaisa wallet app) pehle **closed alpha** me 50 friendly merchants ko app deta hai. Wo real UPI flows chalaate hain, crashes aur ANR (Android vitals) dekhte hain, aur Google Group se feedback aata hai. Phir wahi AAB beta/production me promote hota hai. Chhote solo developers ke liye Google ke rule ki wajah se ye step compulsory ho gaya hai.

## 🟡 Real Example Hindi mein
एक नया Indian fintech startup (Paytm जैसा wallet app) पहले **closed alpha** में 50 दोस्ताना merchants को app देता है। वे असली UPI flows चलाते हैं, crashes और ANR (Android vitals) देखे जाते हैं, और Google Group से feedback आता है। फिर वही AAB beta/production में promote होता है। छोटे solo developers के लिए Google के नियम की वजह से यह step अनिवार्य हो गया है।

---

## 💻 Code Example — Basic
`eas.json` closed track par submit:

```json
{
  "cli": { "version": ">= 12.0.0" },
  "submit": {
    "closed": {
      "android": {
        "serviceAccountKeyPath": "./secrets/play-service-account.json",
        "track": "alpha",
        "releaseStatus": "completed"
      }
    }
  }
}
```

```bash
# latest production build ko alpha (closed) track par bhejo
eas submit -p android --profile closed --latest
```

EAS submit me `track` values: `internal`, `alpha`, `beta`, `production` (Google API ke track names). Custom-named closed tracks ke liye Console UI use karo (version-dependent, EAS docs check karo).

## 💻 Code Example — Advanced
Testers ko feedback dene ke liye in-app "Send feedback" button — email intent ke saath device/build info (`expo-application`, `Linking`):

```jsx
// FeedbackButton.jsx — closed testers ke liye
import React from 'react';                                // React
import { Linking, Platform, Pressable, Text } from 'react-native'; // RN components
import * as Application from 'expo-application';          // npx expo install expo-application

// Feedback email address (Console me bhi yahi do)
const TO = 'beta@example.com';

// Component
export default function FeedbackButton() {
  // press handler
  const send = () => {
    // subject me app version aur platform
    const subject = encodeURIComponent(`Feedback v${Application.nativeApplicationVersion} (${Application.nativeBuildVersion}) ${Platform.OS}`);
    // body me template
    const body = encodeURIComponent('What happened?\n\nSteps to reproduce:\n');
    // mailto URL
    const url = `mailto:${TO}?subject=${subject}&body=${body}`;
    // email app kholo; fail ho to ignore
    Linking.openURL(url).catch(() => {});
  };
  // UI
  return (
    <Pressable onPress={send} accessibilityRole="button">
      <Text>Send feedback</Text>
    </Pressable>
  );
}
```

```bash
# Tester count aur 14 din ka tracking apni spreadsheet me rakho; Console par dashboard status dekho
```

---

## 📱 Android vs iOS Difference
| Feature | Android Closed Testing | iOS TestFlight External |
|---------|-----------------------|-------------------------|
| Review | Google review hota hai | Beta App Review (first build) |
| Testers | Email lists / Google Groups | Email / public link (up to 10,000) |
| Install via | Play Store opt-in | TestFlight app |
| Build expiry | No 90-day TestFlight-style expiry | 90 days |
| New-account rule | Personal accounts: closed test required | None |
| Multiple tracks | Yes (multiple closed tracks) | Multiple groups |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas submit -p android --profile closed --latest   # alpha track
```
CLI way:
```bash
# Fastlane supply
fastlane supply --aab app-release.aab --track alpha
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Testers ko opt-in karwa ke 14 din se pehle hi remove kar dena / opt-out hone dena.
✅ **Correct:** Requirement poori hone tak testers active rakho; zaroorat se zyada testers invite karo.

❌ **Mistake 2:** Sirf install karwa ke chhod dena (no engagement).
✅ **Correct:** Testers actually app use karein, feedback do — genuine testing dikhe.

❌ **Mistake 3:** Closed track me release "Draft" chhod dena.
✅ **Correct:** "Send for review" / rollout complete karo.

❌ **Mistake 4:** Fake/bought testers se kaam chalana.
✅ **Correct:** Real log; Google application review me quality dekhta hai.

---

## 🧠 Tricky Interview Question
**Q: Closed testing me 20 testers add kiye par "Apply for production" disabled hai. Kyon?**

**Answer:** Possible reasons: (1) testers ne opt-in nahi kiya ya kuch ne baad me opt-out kar diya, jisse count kam ho gaya; (2) 14 din ka continuous period abhi poora nahi hua; (3) build review me ya draft state me hai; (4) account personal nahi, organization hai (rule alag); (5) rule/wording update hua ho — Console help dekho. Solution: testers ko dobara opt-in link do, count aur dates dashboard me verify karo.

---

## ⚫ Interview Questions + Answers

**Q1: Internal aur Closed testing me fark?**
A1: Internal: ~100 testers, minutes me, aam taur par no review. Closed: bade invite-only groups, Google review hota hai, Google Groups support.

**Q2: Alpha aur Beta naam kya Google force karta hai?**
A2: Alpha = closed testing ka default track; Beta = open testing track. Aap custom closed tracks bhi bana sakte ho.

**Q3: Closed testing kaun use karta hai?**
A3: Stakeholders, friendly customers, beta groups; aur naye personal accounts production access ke liye.

**Q4: Feedback kaise lete hain?**
A4: Feedback email/URL Console me set karo; Play Console me tester reviews private feedback ki tarah aate hain.

**Q5: Promote kaise?**
A5: Release page → Promote release → Open testing ya Production.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Limited real-user testing chahiye.
- New personal account ke production access ki shart poori karni hai.

❌ Avoid when:
- Sirf team QA — internal track faster.
- Public beta — open testing.

---

## 📊 Visual Diagram
```
 Internal ─► Closed (invite-only, reviewed) ─► Open ─► Production
                │
                ├── Email list / Google Group
                ├── Feedback email
                └── New personal acct: 12+ testers x 14 days → Apply for production
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Alpha | Default closed track | Closed testing track |
| Google Group | Group-based tester list | Group से testers |
| Opt-in | Tester joins test | Test में शामिल होना |
| ANR | App Not Responding | App जवाब नहीं दे रही |
| Apply for production | Request public release access | Production access की माँग |

---

## ⚡ 3-Line Summary
**English:**
1. Closed testing = invite-only Play Store testing with Google review.
2. New personal accounts must run it with enough testers for a minimum period (check current rule).
3. Collect feedback, fix, then promote to open or production.

**Hindi:**
1. Closed testing = Google review के साथ invite-only Play Store testing।
2. नए personal accounts को पर्याप्त testers के साथ minimum अवधि तक चलाना पड़ता है (मौजूदा नियम देखो)।
3. Feedback लो, fix करो, फिर open या production में promote करो।

---

## ➡️ Next Topic
**219. Open Testing (Beta)** — कोई भी Play Store user join कर सके।
