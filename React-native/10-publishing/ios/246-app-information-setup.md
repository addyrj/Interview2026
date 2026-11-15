# 246. App Information Setup
# हिंदी में: App Information भरना
# Platform: Android ❌ | iOS ✅ (Android का equivalent: Play Console → Store settings / App content)

> Targets: **Expo SDK 52 (check current docs — APIs change between SDKs)**. Age rating questionnaire Apple ने हाल में बदला है — current ASC form देखो।

---

## 🔵 Simple Definition (English)
App Information is the general section in App Store Connect with your app's name, subtitle, category, content rights, age rating and legal links. It is shared across all versions of the app.

## 🔵 सरल परिभाषा (Hindi)
App Information ASC का general section है जिसमें app का name, subtitle, category, content rights, age rating और legal links होते हैं। यह app के सभी versions पर लागू होता है।

---

## 🔴 Problem it Solves
- Users और Apple को app की basic पहचान चाहिए (category, उम्र के लायक या नहीं)।
- Search में सही category/नाम से app मिले।

## 🔴 यह क्यों बना? (Hindi)
हर app की category और age rating अलग है। Apple parental controls और search के लिए यह जानकारी ज़रूरी मानता है।

---

## 🟢 How it Works — Step by Step
1. ASC → App → left sidebar **General → App Information**।
2. **Localizable Information:** Name (≤30), Subtitle (≤30) — हर language के लिए।
3. **General Information:** Bundle ID (read-only), SKU, Apple ID, Primary Language।
4. **Category:** Primary (जैसे Food & Drink) और optional Secondary।
5. **Content Rights:** क्या app में third-party content है? Yes/No।
6. **Age Rating:** questionnaire (violence, gambling, user-generated content आदि) → rating auto बनती है।
7. **License Agreement:** Apple Standard EULA या custom।
8. **Privacy Policy URL** (यहाँ या version page पर), Save।

```
Step 1 → General → App Information
Step 2 → Name + Subtitle (per language)
Step 3 → Category (Primary/Secondary)
Step 4 → Content Rights
Step 5 → Age Rating questionnaire
Step 6 → EULA + Privacy Policy URL
Step 7 → Save
```

## 🟢 कैसे काम करता है? (Hindi)
1. App Information खोलो।
2. Name, subtitle, category भरो।
3. Content rights और age rating questionnaire पूरा करो।
4. Privacy policy URL डालकर Save करो।

**Console screen (description):** पेज के ऊपर "Localizable Information" box जिसमें language dropdown (English U.S. आदि) और Name/Subtitle fields हर के पास character counter (जैसे 12/30)। नीचे "General Information" में read-only Bundle ID और SKU। फिर "Age Rating" के पास "Edit" बटन — क्लिक करने पर radio buttons (None / Infrequent / Frequent) वाले सवालों की सूची। ऊपर दाएँ नीला "Save" बटन।

---

## 🟡 Real World Example
**Swiggy** category "Food & Drink" रखता है और subtitle जैसे "Food, Instamart, Dineout" से search में दिखता है। **Paytm** "Finance" category और खास age rating (financial/transactions) रखता है। **Zomato** Hindi localization भी जोड़ता है।

## 🟡 Real Example Hindi mein
Swiggy "Food & Drink" category में है और subtitle से search में दिखता है। Paytm "Finance" में है। Zomato Hindi localization भी जोड़ता है।

---

## 💻 Code Example — Basic
```json
// app.json — ASC info से match करने वाले fields (JSON में comments हटाओ)
{
  "expo": {
    "name": "FoodApp",
    "ios": {
      "bundleIdentifier": "com.mycompany.foodapp",
      "infoPlist": {
        "CFBundleDisplayName": "FoodApp",
        "CFBundleAllowMixedLocalizations": true
      }
    },
    "locales": {
      "hi": "./locales/hi.json"
    }
  }
}
```
```json
// locales/hi.json — Home screen पर Hindi display name
{
  "CFBundleDisplayName": "फूडऐप"
}
```
(`locales` Expo config का valid key है जो iOS में localized InfoPlist strings बनाता है — Expo localization docs देखो।)

## 💻 Code Example — Advanced
```js
// check-store-text.js — ASC limits (name/subtitle ≤30) पहले जाँचो (Node)
const meta = {                                              // आपका planned text
  name: 'FoodApp: Order Food Fast',
  subtitle: 'Biryani, pizza and more',
  keywords: 'food,delivery,biryani,pizza,restaurant',
};
const limits = { name: 30, subtitle: 30, keywords: 100 };   // Apple limits
let bad = false;                                            // flag
for (const [k, max] of Object.entries(limits)) {            // हर field जाँचो
  const len = [...meta[k]].length;                          // unicode-safe length
  if (len > max) { console.error(`${k}: ${len}/${max} too long`); bad = true; }
  else console.log(`${k}: ${len}/${max} ok`);
}
process.exit(bad ? 1 : 0);                                  // CI के लिए exit code
```
Node script चल सकती है (logic only); ASC UI not run।

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| App name | 30 chars (Play) | 30 chars |
| Short text | Short description 80 chars | Subtitle 30 chars |
| Category | Category + Tags | Primary + Secondary category |
| Age rating | IARC questionnaire | Apple age rating questionnaire |
| Content rights | Declarations | Content Rights question |

---

## 🟠 Expo vs CLI Difference
Expo way:
```json
{ "expo": { "ios": { "infoPlist": { "CFBundleDisplayName": "FoodApp" } } } }
```
CLI way:
```xml
<!-- ios/App/Info.plist में सीधे -->
<key>CFBundleDisplayName</key>
<string>FoodApp</string>
```
ASC के fields दोनों में web portal से ही भरते हैं।

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Age rating झूठी/कम रखना।
✅ Correct: सही जवाब दो; mismatch पर rejection (guideline 2.3.6).

❌ Mistake 2: Subtitle में competitor/misleading शब्द।
✅ Correct: साफ़, सच्चा description।

❌ Mistake 3: गलत category चुनना।
✅ Correct: असली main use के हिसाब से चुनो।

❌ Mistake 4: Privacy policy URL खाली।
✅ Correct: Working public URL।

---

## 🧠 Tricky Interview Question
"Name 'FoodApp' देने पर 'name already in use' आया। आप क्या करेंगे?"

Answer: App Store पर नाम unique होता है (दूसरे developer का हो सकता है)। Name बदलो (जैसे "FoodApp - Order Biryani"), या दूसरे नाम से record बनाओ। Home screen पर दिखने वाला नाम (`CFBundleDisplayName`) ASC name से अलग रखा जा सकता है।

---

## ⚫ Interview Questions + Answers
Q1: Name और subtitle की limit?
A1: दोनों 30 characters।

Q2: Age rating कैसे तय होती है?
A2: Questionnaire के जवाबों से Apple automatically निकालता है।

Q3: Primary/Secondary category क्यों?
A3: Search और browse के लिए; Primary ज़्यादा ज़रूरी।

Q4: Content Rights क्या है?
A4: Third-party content (जैसे music, news) का अधिकार है या नहीं।

Q5: Info सभी versions पर लागू है?
A5: Name/subtitle/category आदि app-level हैं; description/screenshots version-level।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Submit से पहले हर app-level field पूरा करना है।

❌ Avoid when:
- Version-specific content (What's New) यहाँ नहीं; वह Version page पर है।

---

## 📊 Visual Diagram
```
 App Information
 ├── Name / Subtitle   (per language, ≤30)
 ├── Category          (Primary + Secondary)
 ├── Content Rights
 ├── Age Rating        (questionnaire → 4+/9+/12+/17+)
 ├── EULA
 └── Privacy Policy URL
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Subtitle | Short line under name | नाम के नीचे छोटी line |
| Category | App type group | app की श्रेणी |
| Age Rating | Suitable age | उम्र की रेटिंग |
| EULA | Licence agreement | उपयोग की शर्तें |
| Localization | Per-language text | भाषा-अनुसार text |

---

## ⚡ 3-Line Summary
English: App Information holds name, subtitle, category and age rating.
It applies to all versions.
Answer the age rating questionnaire honestly.

Hindi: App Information में name, subtitle, category और age rating होती है।
यह सभी versions पर लागू होती है।
Age rating के सवाल ईमानदारी से भरो।

---

## ➡️ Next Topic
**247. Pricing + Availability** — app free है या paid, और किन देशों में मिलेगा।
