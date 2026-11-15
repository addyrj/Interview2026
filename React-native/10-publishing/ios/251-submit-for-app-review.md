# 251. Submit for App Review
# हिंदी में: App Review के लिए Submit करना
# Platform: Android ❌ | iOS ✅ (Android का equivalent: Play Console → Publishing overview → Send for review)

> Targets: **Expo SDK 52 (check current docs — APIs change between SDKs)**. Review guidelines Apple अक्सर update करता है — App Store Review Guidelines पढ़ो।

---

## 🔵 Simple Definition (English)
Submitting for App Review means attaching your processed build to a version in App Store Connect, filling review information, and pressing "Add for Review / Submit". Apple's team then checks the app against the App Store Review Guidelines.

## 🔵 सरल परिभाषा (Hindi)
App Review के लिए submit का मतलब है ASC में version के साथ processed build जोड़ना, review जानकारी भरना और "Add for Review / Submit" दबाना। फिर Apple की team app को App Store Review Guidelines से जाँचती है।

---

## 🔴 Problem it Solves
- Apple चाहता है कि store में सिर्फ सुरक्षित, काम करने वाले, नियम मानने वाले apps हों।
- Developer को एक औपचारिक रास्ता चाहिए release का।

## 🔴 यह क्यों बना? (Hindi)
Apple का App Store curated है। Review से crashes, scams, privacy violations पहले पकड़े जाते हैं। इसलिए हर version पर review होता है।

---

## 🟢 How it Works — Step by Step
1. Pre-flight checklist: build processed ✅, screenshots ✅, description ✅, privacy ✅, age rating ✅, price ✅।
2. Version page → **Build** section → "+" → processed build चुनो।
3. Export compliance जवाब (या `ITSAppUsesNonExemptEncryption` set)।
4. **App Review Information:** Contact (नाम, phone, email), **Sign-in required** हो तो demo username/password, और Notes (hidden features, hardware, OTP workaround)।
5. **Version Release:** Manual / Automatically after approval / Scheduled। Optional "Phased Release for Automatic Updates"।
6. ऊपर-दाएँ **Add for Review** → फिर "Submit to App Review"।
7. Status: **Waiting for Review → In Review → Pending Developer Release / Ready for Sale** (या **Rejected / Metadata Rejected**)।
8. Rejected हो तो **Resolution Center** में message पढ़ो, fix करो, reply/resubmit।

```
Step 1 → Checklist complete
Step 2 → Build attach
Step 3 → Review info + demo account
Step 4 → Release option
Step 5 → Add for Review → Submit
Step 6 → Waiting → In Review → Approved / Rejected
Step 7 → Rejected → Resolution Center → fix → resubmit
```

## 🟢 कैसे काम करता है? (Hindi)
1. सब sections पूरे करो और build attach करो।
2. Review info में demo account ज़रूर दो।
3. Release option चुनकर Submit करो।
4. Status देखते रहो; reject हो तो Resolution Center में कारण पढ़कर fix करो।

**Console screen (description):** Version page के ऊपर-दाएँ कोने में नीला "Add for Review" बटन; दबाने पर "Draft Submissions" पेज आता है, जहाँ items की list और "Submit to App Review" बटन। अगर कुछ missing है तो ऊपर लाल banner "Unable to Add for Review" और नीचे missing items की list। Submit के बाद पेज पर status badge (पीला "Waiting for Review")। Rejection पर status लाल और **App Review → Resolution Center** में Apple के messages का thread दिखता है।

---

## 🟡 Real World Example
**Paytm-जैसा** fintech app login के लिए OTP माँगता है — इसलिए review notes में fixed test number + OTP bypass/demo account देता है, वरना Apple login नहीं कर पाएगा और reject कर देगा। **Zomato** location-based है — notes में बताता है "Select Mumbai as location for testing"।

## 🟡 Real Example Hindi mein
Paytm जैसे app OTP पर निर्भर हैं, इसलिए review notes में test number और demo account देते हैं, वरना Apple login नहीं कर पाएगा। Zomato notes में बताता है कि test के लिए कौन सा शहर चुनें।

---

## 💻 Code Example — Basic
```json
// eas.json — submit + auto-submit with release info से सम्बंधित basic config
{
  "build": { "production": { "autoIncrement": true } },
  "submit": {
    "production": {
      "ios": { "ascAppId": "1234567890" }
    }
  }
}
```
```bash
# Build + ASC पर upload; फिर ASC UI में Add for Review दबाओ
eas build -p ios --profile production --auto-submit
```
`eas submit` सिर्फ upload करता है; "Submit for Review" बटन ASC में दबाना पड़ता है (या `eas metadata` / fastlane `deliver --submit_for_review`)।

## 💻 Code Example — Advanced
```jsx
// DemoLogin.jsx — review के लिए demo account (Reviewer mode) — सुरक्षित तरीके से
import React, { useState } from 'react';                          // state
import { View, TextInput, Pressable, Text, Alert } from 'react-native'; // UI

// Reviewer credentials सिर्फ ASC notes में दो; यहाँ hardcode न करो
// Server बताए कि यह demo user है और OTP skip करे (server-side).
export default function DemoLogin({ onLogin }) {
  const [phone, setPhone] = useState('');                         // phone input
  const [otp, setOtp] = useState('');                             // otp input
  const [busy, setBusy] = useState(false);                        // loading

  const submit = async () => {
    setBusy(true);                                                // loading शुरू
    try {
      const res = await fetch('https://api.example.com/login', {  // API call
        method: 'POST',                                           // POST
        headers: { 'Content-Type': 'application/json' },          // JSON
        body: JSON.stringify({ phone, otp }),                     // data
      });
      if (!res.ok) throw new Error('Login failed');               // error check
      onLogin(await res.json());                                  // success → parent
    } catch (e) {
      Alert.alert('Login failed', 'Check phone/OTP');             // user message
    } finally {
      setBusy(false);                                             // loading ख़त्म
    }
  };

  return (
    <View style={{ padding: 16 }}>
      <TextInput placeholder="Phone" value={phone} onChangeText={setPhone} keyboardType="phone-pad" />
      <TextInput placeholder="OTP" value={otp} onChangeText={setOtp} keyboardType="number-pad" />
      <Pressable disabled={busy} onPress={submit}>
        <Text>{busy ? 'Please wait…' : 'Login'}</Text>
      </Pressable>
    </View>
  );
}
```
Not run: network/UI device पर। Syntax check ही।

**Common rejection reasons (guideline numbers बदल सकते हैं):** 2.1 App Completeness (crash/demo account नहीं), 2.3 Accurate Metadata, 3.1.1 In-App Purchase, 4.0 Design/4.2 Minimum Functionality (सिर्फ webview), 5.1.1 Data Collection/account deletion।

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Review time | कुछ घंटे से कुछ दिन (नए accounts में ज़्यादा) | आमतौर पर 24-48 घंटे |
| Demo access | App access instructions | Demo account in Review Info |
| Rejection channel | Policy status page/email | Resolution Center |
| Staged rollout | % rollout | Phased Release 7 दिनों में |
| Expedited review | नहीं | "Request an Expedited Review" form (limited use) |
| Release control | Managed publishing | Manual/Auto/Scheduled |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Upload; बाक़ी ASC UI/EAS Metadata
eas submit -p ios --latest
```
CLI way:
```bash
# fastlane से submit for review भी
fastlane deliver --submit_for_review --automatic_release false
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Demo account/OTP न देना।
✅ Correct: Review Information में working credentials + notes।

❌ Mistake 2: App में crash या placeholder screens।
✅ Correct: TestFlight पर पहले test।

❌ Mistake 3: Digital goods के लिए Razorpay/UPI से बेचना जहाँ Apple IAP चाहिए।
✅ Correct: Guideline 3.1.1 देखो (physical goods/services जैसे food delivery पर लागू नहीं)।

❌ Mistake 4: Account बनाने की सुविधा है पर delete नहीं।
✅ Correct: In-app account deletion।

---

## 🧠 Tricky Interview Question
"Rejected: Guideline 2.1 — 'We were unable to sign in'। आप क्या करेंगे?"

Answer: Resolution Center में Apple का message पढ़ो; demo account की validity/OTP सत्यापित करो (server पर demo user permanently active रखो, IP/geofence block न हो)। Review Notes अपडेट करो, नई build ज़रूरी नहीं हो तो उसी build पर "Reply" करके resubmit करो। Reviewers अमेरिका से test करते हैं — India-only geofence हो तो वह खोलो।

---

## ⚫ Interview Questions + Answers
Q1: Review में कितना समय?
A1: आमतौर पर 24-48 घंटे; कभी ज़्यादा।

Q2: Metadata Rejected क्या है?
A2: सिर्फ listing में समस्या; नई build ज़रूरी नहीं।

Q3: Phased release?
A3: Auto-update users को 7 दिन में धीरे-धीरे release।

Q4: Rejected के बाद क्या?
A4: Resolution Center → fix → resubmit/reply।

Q5: Expedited review?
A5: Critical bug के लिए Apple से request; हर बार मंज़ूर नहीं।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- TestFlight पर stable build, सब sections पूरे।

❌ Avoid when:
- Known crash, incomplete features, demo account बिना।

---

## 📊 Visual Diagram
```
 Build ──► Version page ──► Add for Review ──► Waiting for Review ──► In Review
                                                                         │
                                           ┌─────────────────────────────┤
                                           ▼                             ▼
                                      Rejected                     Approved
                                  Resolution Center        ┌──────────┴──────────┐
                                    fix + resubmit      Auto release        Manual release
                                                              ▼                   ▼
                                                        Ready for Sale (live on App Store)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| App Review | Apple's check | Apple की जाँच |
| Resolution Center | Reviewer messaging | reviewer से बातचीत |
| Metadata Rejected | Listing issue only | सिर्फ listing में दिक्कत |
| Phased Release | Gradual rollout | धीरे-धीरे release |
| Review Notes | Extra info for Apple | Apple के लिए अतिरिक्त जानकारी |

---

## ⚡ 3-Line Summary
English: Attach the build, fill review info with a demo account, and submit.
Watch the status and use Resolution Center if rejected.
Choose manual, automatic or scheduled release.

Hindi: Build attach करो, demo account के साथ review info भरो और submit करो।
Status देखते रहो और reject होने पर Resolution Center इस्तेमाल करो।
Manual, automatic या scheduled release चुनो।

---

## ➡️ Next Topic
**252+ (अगला section)** — iOS publishing पूरी हुई; आगे CI/CD और OTA updates (EAS Update) देखते हैं।
