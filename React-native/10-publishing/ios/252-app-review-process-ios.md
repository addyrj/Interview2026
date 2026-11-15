# 252. App Review Process (iOS)
# हिंदी में: iOS App Review Process — Apple कैसे आपका app check करता है
# Platform: Android ❌ | iOS ✅

> Expo SDK 52+ examples (check current docs — APIs change between SDKs). Review timelines and App Store Connect UI labels change often — always verify on developer.apple.com.

---

## 🔵 Simple Definition (English)
App Review is Apple's mandatory check (automated + human) that every iOS app and every update must pass before it appears on the App Store. A reviewer installs your build, uses it, and checks it against the App Review Guidelines. Most submissions are reviewed within about 24-48 hours, but it can take longer.

## 🔵 सरल परिभाषा (Hindi)
App Review Apple का mandatory check है (automated + human) जिसे हर iOS app और हर update को App Store पर आने से पहले pass करना पड़ता है। Reviewer आपका build install करके चलाता है और App Review Guidelines से match करता है। ज़्यादातर submissions 24-48 घंटे में review हो जाते हैं, पर कभी-कभी ज़्यादा समय लग सकता है।

---

## 🔴 Problem it Solves
```
WITHOUT REVIEW:
  - Malware / scam apps on the store
  - Apps that crash on launch
  - Fake apps copying Paytm / PhonePe branding
  - Apps stealing user data silently

WITH REVIEW:
  - Every build checked by Apple before users see it
  - Basic quality + privacy + safety bar
  - Users trust the App Store
```

## 🔴 यह क्यों बना? (Hindi)
Review के बिना कोई भी fake banking app, malware या crash होने वाला app store पर डाल सकता था। Apple चाहता है कि user का भरोसा बना रहे — इसलिए हर build पहले check होता है। Developer के लिए इसका मतलब: release plan में review time हमेशा जोड़ो, आख़िरी दिन submit मत करो।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Upload build (eas submit / Xcode Organizer) → App Store Connect "Processing"
Step 2 → Build appears in TestFlight tab → pick it in the app version page
Step 3 → Fill metadata, screenshots, privacy, review notes, demo account
Step 4 → Click "Add for Review" → "Submit to App Review"
Step 5 → Status: Waiting for Review
Step 6 → Status: In Review (reviewer tests app on a real device)
Step 7a → Pending Developer Release / Ready for Distribution  (approved)
Step 7b → Rejected / Metadata Rejected (fix + resubmit, or reply in Resolution Center)
```

### Status meanings
| Status | Meaning |
|--------|---------|
| Prepare for Submission | You are still editing metadata |
| Waiting for Review | In Apple's queue |
| In Review | Reviewer is testing now (usually minutes to hours) |
| Pending Developer Release | Approved, you chose manual release |
| Ready for Distribution | Live on the App Store |
| Rejected | Binary has issue; see Resolution Center |
| Metadata Rejected | Only text/screenshots issue; no new build needed |
| Developer Rejected | You pulled the submission yourself |

## 🟢 कैसे काम करता है? (Hindi)
1. Build upload करो — App Store Connect में "Processing" दिखेगा (10-30 मिनट)।
2. Version page पर वह build select करो।
3. Metadata, screenshots, privacy details, review notes और demo account भरो।
4. "Submit to App Review" दबाओ।
5. Status "Waiting for Review" से "In Review" बनेगा — reviewer real device पर app चलाएगा।
6. Approve हुआ तो release option के हिसाब से live; reject हुआ तो Resolution Center में कारण मिलेगा।

### Console screen description (screenshot in words)
- **App Store Connect → My Apps → [App] → left sidebar "iOS App" → version (e.g. 1.0)**: Page के ऊपर status badge (पीला dot = Waiting for Review), बीच में Previews and Screenshots, फिर Promotional Text, Description, Keywords, Support URL, और नीचे **Build** section जहाँ "+" से build चुनते हैं।
- **App Review Information** section (नीचे): Sign-in required checkbox, Username/Password fields, Notes box, Contact first name / last name / phone / email।
- **Top right**: नीला "Add for Review" button, फिर "Submit to App Review"।
- **Resolution Center**: App page में "App Review" tab → reviewer के messages thread, जहाँ आप reply कर सकते हैं और attachments (video) भेज सकते हैं।

---

## 🟡 Real World Example
Swiggy / Zomato जैसे apps का login phone OTP पर होता है। Reviewer के पास Indian phone number नहीं होता, इसलिए अगर आप review notes में "demo account: phone 9999999999, OTP always 123456 (only for review)" न दें तो reject होना तय है (Guideline 2.1). Zomato-style team पहले TestFlight पर बाहरी testers से test करती है, फिर App Review में भेजती है, और critical hotfix के लिए "Expedited Review" request करती है।

## 🟡 Real Example Hindi mein
Swiggy/Zomato में login OTP से होता है। Apple reviewer के पास भारतीय number नहीं होता, इसलिए review notes में demo number और fixed OTP देना ज़रूरी है, वरना "2.1 App Completeness" में reject। Production crash आए तो team Apple से "Expedited Review" माँगती है।

---

## 💻 Code Example — Basic (build + submit for review)
```bash
# Expo SDK 52+ with EAS CLI (npm i -g eas-cli)
eas login                                            # login to your Expo account
eas build --platform ios --profile production       # cloud build, signs the IPA for you
eas submit --platform ios --latest                   # uploads latest build to App Store Connect
# After upload: open App Store Connect and press "Submit to App Review" yourself
```

```json
{
  "submit": {
    "production": {
      "ios": {
        "ascAppId": "1234567890",
        "appleTeamId": "ABCDE12345"
      }
    }
  }
}
```

## 💻 Code Example — Advanced (review-friendly demo mode in app)
```jsx
// ReviewDemoLogin.jsx - lets Apple reviewer log in without a real SMS OTP
import React, { useState } from 'react';                       // React + state hook
import { View, Text, TextInput, Pressable, Alert, Platform, StyleSheet } from 'react-native'; // UI

// Reviewer credentials documented in App Store Connect > App Review Information
const REVIEW_PHONE = '9999999999';                              // demo phone given in review notes
const REVIEW_OTP = '123456';                                    // fixed OTP only accepted for that phone

export default function ReviewDemoLogin({ onLoggedIn }) {       // onLoggedIn: parent callback
  const [phone, setPhone] = useState('');                       // phone input state
  const [otp, setOtp] = useState('');                           // otp input state

  const verify = async () => {                                  // called on button press
    try {                                                       // guard network errors
      if (phone === REVIEW_PHONE && otp === REVIEW_OTP) {       // demo path for reviewer
        onLoggedIn({ token: 'demo-token', demo: true });        // skip backend SMS verification
        return;                                                 // stop here
      }
      const res = await fetch('https://api.example.com/verify', { // real path for normal users
        method: 'POST',                                         // POST request
        headers: { 'Content-Type': 'application/json' },        // JSON body
        body: JSON.stringify({ phone, otp, os: Platform.OS }),  // send phone, otp, platform
      });
      if (!res.ok) throw new Error('Invalid OTP');              // handle non-2xx
      onLoggedIn(await res.json());                             // real login success
    } catch (e) {                                               // show friendly error
      Alert.alert('Login failed', e.message);                   // never crash on bad input
    }
  };

  return (
    <View style={styles.box}>
      <Text style={styles.title}>Login</Text>
      <TextInput style={styles.input} placeholder="Phone" keyboardType="phone-pad" value={phone} onChangeText={setPhone} />
      <TextInput style={styles.input} placeholder="OTP" keyboardType="number-pad" value={otp} onChangeText={setOtp} />
      <Pressable style={styles.btn} onPress={verify}><Text style={styles.btnText}>Verify</Text></Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  box: { padding: 24 },                                         // outer spacing
  title: { fontSize: 22, fontWeight: '700', marginBottom: 12 }, // heading
  input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 10, marginBottom: 12 }, // field
  btn: { backgroundColor: '#fc8019', padding: 14, borderRadius: 8 },  // Swiggy-orange button
  btnText: { color: '#fff', textAlign: 'center', fontWeight: '600' }, // button label
});
```
Note: a hard-coded demo path is a security trade-off. Safer option: server-side allowlist for the review phone number, controlled by a feature flag.

---

## 📱 Android vs iOS Difference
| Feature | Android (Play Store) | iOS (App Store) |
|---------|---------------------|-----------------|
| Review type | Mostly automated, some human | Automated + human on real device |
| Typical time | Hours to a few days (new accounts longer) | Usually ~24-48 hrs |
| Demo account | Recommended | Practically mandatory if login exists |
| Sideload bypass | Possible (APK) | Not possible (outside EU DMA / enterprise) |
| Expedited review | Not a formal feature | "Request an Expedited App Review" form |
| Rejection channel | Play Console policy status | Resolution Center messages |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas build --platform ios --profile production   # EAS handles certs + provisioning
eas submit --platform ios --latest               # EAS uploads to App Store Connect
```
CLI way (bare React Native):
```bash
cd ios && pod install                            # install native pods
# Xcode: select "Any iOS Device" -> Product > Archive
# Organizer > Distribute App > App Store Connect > Upload
# (or: xcrun altool / Transporter app to upload the .ipa)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No demo credentials for login apps.
✅ Correct: Fill App Review Information with working username/password or OTP bypass.

❌ Mistake 2: Submitting a build whose backend is down or behind VPN.
✅ Correct: Keep production API live during review; reviewers test from the US/Cupertino.

❌ Mistake 3: Submitting on Friday evening before a launch Monday.
✅ Correct: Submit with a buffer of at least 3-5 days; use manual release to control launch date.

❌ Mistake 4: Ignoring Resolution Center messages.
✅ Correct: Reply promptly; a clear reply or demo video often resolves it without a new build.

---

## 🧠 Tricky Interview Question
Your app was "In Review" for 5 days and nothing happened. What do you do?

Answer: Do not resubmit (you lose queue position). First check Resolution Center for a message asking for info. If none, wait ~48-72 hrs, then use Apple's "Contact Us" > App Review > "Request status update". For urgent bugs, request Expedited Review. Never cancel and re-add unless Apple asks.

---

## ⚫ Interview Questions + Answers
Q1: Does an OTA update (EAS Update) need App Review?
A1: Not for JS/asset-only changes, as long as the app's primary purpose does not change (Guideline 2.5.2). Native changes need a new build + review.

Q2: What is a Metadata Rejected?
A2: Only text/screenshots/privacy answers are wrong. You edit them and resubmit without uploading a new binary.

Q3: Who is the audience for review notes?
A3: The human reviewer. Include demo account, how to reach hidden features, hardware needs, and region-specific steps.

Q4: Can you appeal a rejection?
A4: Yes. Reply in Resolution Center, or use the App Review Board appeal from the Apple Developer site if you believe the guideline was misapplied.

Q5: What is Expedited Review?
A5: A request form for critical bug fixes or time-sensitive events (e.g. IPL release). Apple may accept it, but it is not guaranteed.

---

## 🔷 When to Use + When Not to Use
✅ Use (plan for) when:
- Any new app, native change, new permission, or new SDK is added
- Changing metadata, pricing, or in-app purchases

❌ Avoid / not required when:
- Pure JS bug fix that can go via EAS Update (still keep it consistent with the reviewed behaviour)
- TestFlight internal testing (no review needed)

---

## 📊 Visual Diagram
```
 Dev  --eas submit-->  App Store Connect (Processing)
                              |
                         Select build + metadata
                              |
                        Submit for Review
                              |
                       Waiting --> In Review
                                     |
                      +--------------+--------------+
                      |                             |
                  Approved                      Rejected
                      |                             |
            Release (manual/auto/phased)   Fix -> Resolution Center -> Resubmit
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| App Review | Apple's check before release | Apple की जाँच |
| Resolution Center | Chat thread with reviewer | Reviewer से बातचीत |
| Binary | The uploaded IPA build | Upload किया हुआ build |
| Expedited Review | Request faster review | जल्दी review की request |
| Metadata | Name, screenshots, description | App की जानकारी |

---

## ⚡ 3-Line Summary
English: Every iOS app and update is reviewed by Apple before release.
Give a demo account, keep the backend live, and read Resolution Center messages.
Plan buffer time; reject means fix and resubmit, not panic.

Hindi: हर iOS app और update Apple review से गुज़रता है।
Demo account दो, backend चालू रखो और Resolution Center ध्यान से पढ़ो।
Buffer time रखो; reject हो तो fix करके दोबारा submit करो।

---

## ➡️ Next Topic
**253. Common Rejection Reasons (iOS)** — review process समझने के बाद जानो कि ज़्यादातर apps किन कारणों से reject होते हैं।
