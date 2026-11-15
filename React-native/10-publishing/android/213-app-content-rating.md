---

# 213. App Content Rating
# हिंदी में: App Content Rating (Age Rating)
# Platform: Android ✅ | iOS ❌ (iOS me alag age rating questionnaire hoti hai)

> Expo SDK 53/54 (check current docs — APIs change between SDKs). Rating Play Console ka form hai, Expo SDK se koi lena-dena nahi. Question wording Google/IARC badalta rehta hai.

---

## 🔵 Simple Definition (English)
**Content rating** is an age label (like Everyone, Teen, Mature 17+) that Google Play assigns to your app after you answer the **IARC questionnaire** in Play Console. It tells users and parents what kind of content the app contains. Every app **must** have a rating, or it can be blocked or removed.

## 🔵 सरल परिभाषा (Hindi)
**Content rating** एक age label है (जैसे Everyone, Teen, Mature 17+) जो Play Console में **IARC questionnaire** भरने के बाद Google Play आपकी app को देता है। यह users और parents को बताता है कि app में किस तरह का content है। हर app पर rating **ज़रूरी** है, वरना वह block या remove हो सकती है।

---

## 🔴 Problem it Solves
- Parents and users need to know if an app is suitable for kids.
- Each country has different rules (ESRB in US, PEGI in Europe, IARC regional ratings for India/Brazil/etc.). One questionnaire gives all ratings.
- Apps without a rating are not visible in some countries/devices.

## 🔴 यह क्यों बना? (Hindi)
- Parents और users को जानना होता है कि app बच्चों के लिए सही है या नहीं।
- हर देश के नियम अलग हैं (US में ESRB, Europe में PEGI वगैरह)। एक ही questionnaire से सभी ratings मिल जाती हैं।
- Rating के बिना app कुछ देशों/devices में दिखती ही नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Play Console → app select → Policy and programs → App content
Step 2 → "Content ratings" section → "Start questionnaire"
Step 3 → Email address daalo (rating certificates ke liye)
Step 4 → Category chuno: Game / Social / Utility, productivity... / Other
Step 5 → Questions ka honest jawab: violence, sexual content, language,
         gambling, drugs, user-generated content, location sharing, purchases
Step 6 → "Save" → "Calculate rating" → summary dekho
Step 7 → "Submit" — rating apply
Step 8 → Badi app change (naya feature, UGC, chat) → questionnaire dobara bharo
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Play Console → app चुनो → Policy and programs → App content
Step 2 → "Content ratings" section → "Start questionnaire"
Step 3 → Email डालो (rating certificates के लिए)
Step 4 → Category चुनो: Game / Social / Utility, productivity... / Other
Step 5 → सच्चे जवाब दो: violence, sexual content, language,
         gambling, drugs, user-generated content, location sharing, purchases
Step 6 → "Save" → "Calculate rating" → summary देखो
Step 7 → "Submit" दबाओ — rating लग जाती है
Step 8 → बड़ा बदलाव (नया feature, UGC, chat) → questionnaire फिर से भरो
```

**Console screens (described in words):**
- **App content page:** Cards ki list — "Privacy policy", "Ads", "App access", "Content ratings", "Target audience", "Data safety". Har card par status: "Start" (neela) ya "Done" (hara tick).
- **Questionnaire screen:** Upar progress steps (Category → Questionnaire → Summary). Beech me Yes/No radio questions, jaise "Does your app contain user-generated content?".
- **Summary screen:** Ek table jisme regions ke saamne rating (jaise "Everyone / 3+ / 12+"). Neeche "Apply rating" button.

---

## 🟡 Real World Example
**Zomato / Swiggy** (food delivery) usually "Everyone"-type rating paate hain. Par agar app me **user reviews/photos** (UGC) ya **chat with delivery partner** hota hai, to questionnaire me "users can interact" = Yes bolna padta hai, jo rating thodi badha sakta hai (jaise Teen). **Dream11** jaise apps real-money gaming ki wajah se alag, sakht declarations aur eligibility restrictions se guzarte hain.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy** (food delivery) को आमतौर पर "Everyone"-type rating मिलती है। लेकिन अगर app में **user reviews/photos** (UGC) या **delivery partner से chat** है, तो questionnaire में "users can interact" = Yes बोलना पड़ता है, जिससे rating थोड़ी बढ़ सकती है। **Dream11** जैसी real-money gaming apps पर अलग और सख़्त declarations होते हैं।

---

## 💻 Code Example — Basic
Rating form me kya jawab doge — ye ek JSON me likh lo (internal documentation).

```json
{
  "app": "FoodieIndia",
  "category": "Utility/Other",
  "answers": {
    "violence": false,
    "sexualContent": false,
    "profanity": false,
    "controlledSubstances": false,
    "gambling": false,
    "userGeneratedContent": true,
    "sharesLocation": true,
    "inAppPurchases": true,
    "usersCanInteract": true
  }
}
```

## 💻 Code Example — Advanced
Ye Node script answers dekhkar andaza deti hai kaun se flags rating badha sakte hain (sirf planning helper — asli rating IARC deta hai).

```js
// ratingPlanner.js — run: node ratingPlanner.js
// Ye sirf ek rough planner hai, official rating IARC calculate karta hai
const answers = {
  violence: false,          // violence hai?
  sexualContent: false,     // sexual content?
  profanity: false,         // gaali / strong language?
  gambling: false,          // gambling ya real-money?
  userGeneratedContent: true, // UGC (reviews, photos)?
  usersCanInteract: true,   // chat/comments?
  sharesLocation: true,     // location share hota hai?
};

// aise flags jinse rating ya extra labels par asar ho sakta hai
const sensitive = ['violence', 'sexualContent', 'profanity', 'gambling'];
// jo sensitive flags true hain unko nikalo
const high = sensitive.filter((k) => answers[k]);
// interaction flags (rating ke saath "Users interact" label)
const social = ['userGeneratedContent', 'usersCanInteract', 'sharesLocation'].filter((k) => answers[k]);

// message banao
console.log('Sensitive flags:', high.length ? high.join(', ') : 'none');
console.log('Interaction labels:', social.join(', ') || 'none');
// reminder
console.log('Reminder: UGC hai to moderation + report/block feature zaroori (policy).');
```

```bash
# Rating form ke baad build+submit (216) — rating complete ho tabhi release rollout hota hai
eas build --platform android --profile production
```

---

## 📱 Android vs iOS Difference
| Feature | Android (Google Play) | iOS (App Store) |
|---------|----------------------|-----------------|
| System | IARC questionnaire | Apple age rating questionnaire (App Store Connect) |
| Rating labels | Everyone, Teen, Mature 17+ etc. (region-wise) | 4+, 9+, 12+, 17+ (Apple updated scheme in recent years) |
| Where | Play Console → App content | App Store Connect → App Information |
| Re-do needed | Major content change par | Major content change par |
| Missing rating | App block/remove ho sakti hai | Submit nahi kar sakte |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Rating Console ka kaam hai — Expo config me kuch nahi. Par UGC ho to app me report/block UI do.
import { Pressable, Text } from 'react-native'; // UI components
export const ReportButton = ({ onReport }) => ( // report button component
  <Pressable onPress={onReport}><Text>Report</Text></Pressable> // press par report call
);
```
CLI way:
```jsx
// Bare RN me bhi bilkul same — rating Play Console me hi hoti hai, code me nahi
import { Pressable, Text } from 'react-native'; // same imports
export const ReportButton = ({ onReport }) => ( // same component
  <Pressable onPress={onReport}><Text>Report</Text></Pressable> // same behaviour
);
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** "Sab No" bol dena taaki rating kam aaye.
✅ **Correct:** Honest jawab do. Galat jawab = app removal ya account strike.

❌ **Mistake 2:** UGC / chat hai par "No" likhna.
✅ **Correct:** Yes likho aur moderation, report, block features implement karo.

❌ **Mistake 3:** Naya feature (live chat, gambling) add karke questionnaire dobara na bharna.
✅ **Correct:** Content badalne par questionnaire update karo.

❌ **Mistake 4:** Rating aur Target audience ko ek hi cheez samajhna.
✅ **Correct:** Rating = content ka label. Target audience = aap kis age group ko target kar rahe ho (Families policy yahan lagti hai).

---

## 🧠 Tricky Interview Question
**Q: Aapki app me koi violence nahi, phir bhi rating "Teen" aa gayi. Kyon?**

**Answer:** IARC me sirf violence nahi, **user interaction** (chat, UGC), **location sharing**, **in-app purchases**, gambling-simulation, ya "digital purchases" jaise elements bhi labels/rating par asar daal sakte hain. Questionnaire ke jawab dobara check karo; sahi hone par rating accept karo. Appeal karna ho to Play Console se IARC ko rating dispute bhej sakte ho.

---

## ⚫ Interview Questions + Answers

**Q1: IARC kya hai?**
A1: International Age Rating Coalition — ek questionnaire se alag-alag deshon ki rating systems (ESRB, PEGI, etc.) ke liye ratings deta hai.

**Q2: Kya rating ke bina app publish ho sakti hai?**
A2: Nahi; rating complete hone par hi release publish ho paata hai. Bina rating wali apps hat sakti hain.

**Q3: Rating baad me badal sakti hai?**
A3: Haan, content change par questionnaire dobara bharte ho.

**Q4: Content rating aur Target audience me fark?**
A4: Rating = content kitna mature hai; Target audience = kis age group ke liye hai. Bachhon ko target karne par Families policy aur extra rules lagte hain.

**Q5: Galat jawab dene par kya hota hai?**
A5: Google app ki rating badal sakta hai, app suspend/remove ya account par action le sakta hai.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Naya app pehli baar release kar rahe ho.
- App me naya content type (chat, UGC, purchases) add hua.

❌ Avoid when:
- (Skip nahi kar sakte) — ye mandatory hai; sirf jawab sochkar do.

---

## 📊 Visual Diagram
```
  Play Console → App content
          │
          ▼
  Content ratings → Start questionnaire
          │
   email → category → Yes/No questions
          │
          ▼
  IARC calculates ──► ESRB / PEGI / regional labels
          │
          ▼
  Rating applied to store listing
          │
  Content change? ──► redo questionnaire
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| IARC | Age-rating coalition | Age rating संस्था |
| UGC | User-generated content | Users का बनाया content |
| ESRB/PEGI | Regional rating boards | क्षेत्रीय rating boards |
| Target audience | Age groups you aim at | लक्षित उम्र वर्ग |
| Questionnaire | Form you answer | प्रश्नावली |

---

## ⚡ 3-Line Summary
**English:**
1. Answer the IARC questionnaire honestly in Play Console → App content.
2. One answer set gives ratings for many regions; UGC, chat, and purchases affect it.
3. Redo it when content changes; false answers risk removal.

**Hindi:**
1. Play Console → App content में IARC questionnaire सच्चाई से भरो।
2. एक ही जवाब-सेट से कई regions की rating मिलती है; UGC, chat, purchases असर डालते हैं।
3. Content बदले तो फिर भरो; गलत जवाब से app हट सकती है।

---

## ➡️ Next Topic
**214. Privacy Policy — Required** — rating के बाद privacy policy URL ज़रूरी है।
