# 243. External Testing on TestFlight
# हिंदी में: TestFlight पर External Testing
# Platform: Android ❌ | iOS ✅ (Android का equivalent: Closed/Open testing track)

> Targets: **Expo SDK 52 (check current docs — APIs change between SDKs)**. Review time और limits Apple बदल सकता है।

---

## 🔵 Simple Definition (English)
External testing lets up to 10,000 people outside your team test your app through TestFlight, using email invites or a public link. The first build of each version needs a light Beta App Review.

## 🔵 सरल परिभाषा (Hindi)
External testing में आपकी team के बाहर के अधिकतम 10,000 लोग TestFlight से app test कर सकते हैं — email invite या public link से। हर version की पहली build पर हल्का Beta App Review लगता है।

---

## 🔴 Problem it Solves
- Real users की बड़ी संख्या पर beta test करना जो आपकी team में नहीं हैं।
- Clients, investors, college beta groups तक app पहुँचाना।

## 🔴 यह क्यों बना? (Hindi)
Internal सिर्फ 100 team members तक सीमित है। असली feedback के लिए बड़े external group की ज़रूरत थी — Apple ने public link और review के साथ यह दिया।

---

## 🟢 How it Works — Step by Step
1. TestFlight tab → **External Testing → +** → group का नाम दो।
2. **Test Information** भरो: Beta App Description, Feedback Email, Contact info, (login हो तो) demo account, "What to Test" notes।
3. Testers add करो: email से, CSV import, या **Public Link** enable करो (limit सेट करो)।
4. Build चुनकर **Submit for Review** करो — Beta App Review (आमतौर पर 24 घंटे तक, कभी जल्दी)।
5. Approved → testers को email आती है; TestFlight से install।
6. उसी version की आगे की builds अक्सर review के बिना मिलती हैं; नया version number आने पर फिर review।

```
Step 1 → External group बनाओ
Step 2 → Test Information भरो
Step 3 → Testers / Public Link
Step 4 → Submit build for Beta App Review
Step 5 → Approved → Testers install
Step 6 → New version → फिर review
```

## 🟢 कैसे काम करता है? (Hindi)
1. External group बनाओ और test information भरो।
2. Testers add करो या public link बनाओ।
3. Build को Beta Review के लिए submit करो।
4. Approve होने पर testers को email मिलती है।

**Console screen (description):** TestFlight → External Testing → group page पर ऊपर "Public Link" toggle और link (जैसे `testflight.apple.com/join/XXXX`), उसके नीचे "Limit" बॉक्स (1–10,000)। **Builds** section में build के आगे status badge: "Waiting for Review" (पीला), "In Review", "Approved" (हरा) या "Rejected".

---

## 🟡 Real World Example
**Paytm** नया UPI feature 2000 beta users को public link से देता है। **Zomato** खास cities के power users का group बनाता है। Link social media/WhatsApp पर share होता है।

## 🟡 Real Example Hindi mein
Paytm नया feature 2000 beta users को public link से देता है। Zomato चुनिंदा शहरों के users का group बनाता है। Link WhatsApp पर share हो जाता है।

---

## 💻 Code Example — Basic
```jsx
// BetaInvite.jsx — app में beta join link दिखाओ
import React from 'react';                          // React
import { View, Text, Pressable, Linking } from 'react-native'; // UI

// TestFlight public link (ASC से मिला)
const BETA_LINK = 'https://testflight.apple.com/join/XXXXXXXX';

export default function BetaInvite() {
  return (
    <View style={{ padding: 16 }}>
      {/* Info text */}
      <Text>Try new features early on iOS.</Text>
      <Pressable onPress={() => Linking.openURL(BETA_LINK)}>
        {/* Link tap → TestFlight खुलता है */}
        <Text style={{ color: 'blue' }}>Join the beta</Text>
      </Pressable>
    </View>
  );
}
```
## 💻 Code Example — Advanced
```jsx
// BetaGate.jsx — safe Linking + Android fallback
import React, { useCallback, useState } from 'react';        // hooks
import { View, Text, Pressable, Platform, Alert, Linking } from 'react-native';

const IOS_LINK = 'https://testflight.apple.com/join/XXXXXXXX';  // iOS beta
const ANDROID_LINK = 'https://play.google.com/apps/testing/com.mycompany.foodapp'; // Play beta

export default function BetaGate() {
  const [busy, setBusy] = useState(false);             // double tap रोकने के लिए

  const join = useCallback(async () => {
    const url = Platform.OS === 'ios' ? IOS_LINK : ANDROID_LINK; // OS के हिसाब से link
    setBusy(true);
    try {
      const ok = await Linking.canOpenURL(url);         // क्या खुल सकता है?
      if (!ok) throw new Error('Cannot open link');     // नहीं तो error
      await Linking.openURL(url);                       // खोलो
    } catch (e) {
      Alert.alert('Oops', 'Beta link खुल नहीं पाया, बाद में कोशिश करें.'); // user को बताओ
    } finally {
      setBusy(false);                                   // flag reset
    }
  }, []);

  return (
    <View style={{ padding: 16 }}>
      <Pressable disabled={busy} onPress={join}>
        <Text>{busy ? 'Opening...' : 'Join beta'}</Text>
      </Pressable>
    </View>
  );
}
```
(`canOpenURL` iOS पर https के लिए `LSApplicationQueriesSchemes` नहीं माँगता; custom schemes के लिए माँगता है।)

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Limit | Open testing: unlimited | 10,000 external |
| Review | Open: basic Play review | Beta App Review |
| Join link | `play.google.com/apps/testing/<pkg>` | `testflight.apple.com/join/<code>` |
| Build expiry | नहीं | 90 दिन |
| Tester requirement | Google account | Apple ID + iOS 13+ (TestFlight app) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# build + submit; फिर ASC web UI में external group पर build assign
eas build -p ios --profile production --auto-submit
```
CLI way:
```bash
# fastlane से external distribution (review submit सहित)
fastlane pilot distribute --groups "Beta Users" --distribute_external true \
  --changelog "Fixed login bug"
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Test Information (description/email) खाली छोड़ना → review submit नहीं होता।
✅ Correct: सब required fields भरो।

❌ Mistake 2: Login वाला app बिना demo account के review में भेजना → rejection।
✅ Correct: Demo credentials दो।

❌ Mistake 3: Public link बिना limit के छोड़ना।
✅ Correct: Limit सेट करो; ज़रूरत ख़त्म होने पर link बंद करो।

❌ Mistake 4: Placeholder/crashing build भेजना।
✅ Correct: पहले internal में test करो।

---

## 🧠 Tricky Interview Question
"External group को build 1.0.0 (5) approve हो गई। अब 1.0.0 (6) डाली — क्या फिर से review लगेगा?"

Answer: आमतौर पर नहीं — same version (1.0.0) की नई build बिना full Beta Review के external testers को मिल सकती है। लेकिन version बदलकर 1.1.0 करो तो पहली build पर फिर review लगता है। (Apple बड़े बदलाव पर फिर review माँग सकता है — नियम बदल सकते हैं।)

---

## ⚫ Interview Questions + Answers
Q1: External limit?
A1: 10,000 testers।

Q2: Beta App Review क्या है?
A2: Apple की हल्की जाँच (policy/crash), App Store review से कम सख़्त।

Q3: Public link का फायदा?
A3: बिना email collect किए कोई भी जुड़ सकता है (limit तक)।

Q4: Tester जुड़ने के लिए क्या चाहिए?
A4: iPhone/iPad + TestFlight app + Apple ID।

Q5: Build कब expire होती है?
A5: 90 दिन बाद।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Real users का feedback चाहिए।
- Client demo, large beta।

❌ Avoid when:
- Confidential feature है जो leak नहीं होना चाहिए (internal use करो)।
- Review का time नहीं है।

---

## 📊 Visual Diagram
```
 Build ──► Test Information ──► Beta App Review ──► Approved
                                       │ rejected → fix → resubmit
                                       ▼
        Email invite ─┐
        Public link ──┼──► TestFlight app ──► Feedback/Crashes ──► Dev
        CSV import ───┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| External tester | Non-team beta user | बाहरी tester |
| Public link | Open join URL | सबके लिए link |
| Beta App Review | Apple's beta check | beta जाँच |
| What to Test | Notes for testers | testers के लिए निर्देश |

---

## ⚡ 3-Line Summary
English: External testing reaches up to 10,000 outside testers.
Fill test information and pass Beta App Review once per version.
Use a public link with a limit.

Hindi: External testing में 10,000 बाहरी testers तक पहुँचते हैं।
Test information भरो और हर version पर Beta App Review पास करो।
Public link limit के साथ इस्तेमाल करो।

---

## ➡️ Next Topic
**244. App Store Connect — Complete Guide** — beta के बाद असली release का पूरा console समझते हैं।
