---

# 217. Internal Testing Track
# हिंदी में: Internal Testing Track
# Platform: Android ✅ | iOS ❌ (iOS ka equivalent: TestFlight internal testing)

> Expo SDK 53/54 (check current docs — APIs change between SDKs). Tester limits aur Console menu names Google badalta rehta hai.

---

## 🔵 Simple Definition (English)
**Internal testing** is the fastest Play Store track: you upload an AAB and up to about 100 testers (by email) can install it within minutes, usually **without Google's full review**. It is meant for your own team and QA to check builds before wider testing.

## 🔵 सरल परिभाषा (Hindi)
**Internal testing** Play Store का सबसे तेज़ track है: AAB upload करो और लगभग 100 testers (email से) कुछ ही मिनटों में उसे install कर सकते हैं, आमतौर पर **Google के पूरे review के बिना**। यह आपकी team और QA के लिए है, ताकि बड़े testing से पहले build जाँचा जा सके।

---

## 🔴 Problem it Solves
- Sending APK files over WhatsApp/Drive is messy and insecure.
- Testing a release build from the real Play Store (with Play signing, Play services, in-app billing) is different from a debug APK.
- Production release is slow; teams need quick feedback loops.

## 🔴 यह क्यों बना? (Hindi)
- WhatsApp/Drive पर APK भेजना गड़बड़ और असुरक्षित है।
- असली Play Store से release build test करना (Play signing, Play services, in-app billing) debug APK से अलग होता है।
- Production release धीमा है; teams को जल्दी feedback चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Play Console → Test and release → Testing → Internal testing
Step 2 → "Testers" tab → Create email list (e.g. "QA team") → Gmail IDs add
Step 3 → "Releases" tab → Create new release → AAB upload
Step 4 → Release notes → Save → "Start rollout to Internal testing"
Step 5 → "Testers" tab se opt-in link copy karo
Step 6 → Testers link kholte hain → "Become a tester" → Play Store se install
Step 7 → Bug mila → fix → naya versionCode → naya AAB upload
Step 8 → Sab theek → "Promote release" → Closed / Production
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Play Console → Test and release → Testing → Internal testing
Step 2 → "Testers" tab → Email list बनाओ (जैसे "QA team") → Gmail IDs जोड़ो
Step 3 → "Releases" tab → Create new release → AAB upload
Step 4 → Release notes → Save → "Start rollout to Internal testing"
Step 5 → "Testers" tab से opt-in link copy करो
Step 6 → Testers link खोलते हैं → "Become a tester" → Play Store से install
Step 7 → Bug मिला → fix → नया versionCode → नया AAB upload
Step 8 → सब ठीक → "Promote release" → Closed / Production
```

**Console screens (described in words):**
- **Internal testing page:** Upar teen tabs: "Releases", "Testers", "Countries/regions". Releases tab me current release card (version, status "Available to internal testers").
- **Testers tab:** Table of email lists with checkbox; "Create email list" button; neeche "Feedback URL or email address" aur "Copy link" button.
- **Tester ka phone:** Opt-in page — "You're invited to test X" + "Become a tester"; baad me Play Store listing par "Install" aur "(Internal test)" label.

---

## 🟡 Real World Example
**Swiggy** jaisi teams har merge ke baad CI se build ko internal track par push karti hain. QA aur product team usi Play Store link se install karti hai, aur **in-app purchase / UPI intent / Play services** jaisi cheezein real environment me test hoti hain. Internal track pe approval ka wait nahi hota, isliye sprint ke beech daily builds possible hain.

## 🟡 Real Example Hindi mein
**Swiggy** जैसी teams हर merge के बाद CI से build को internal track पर push करती हैं। QA और product team उसी Play Store link से install करती है, और **in-app purchase / UPI intent / Play services** जैसी चीज़ें असली environment में test होती हैं। Internal track पर approval का इंतज़ार नहीं होता, इसलिए sprint के बीच रोज़ builds संभव हैं।

---

## 💻 Code Example — Basic
`eas.json` — internal track par automatic submit:

```json
{
  "cli": { "version": ">= 12.0.0" },
  "build": {
    "preview": {
      "distribution": "internal",
      "android": { "buildType": "apk" }
    },
    "production": {
      "autoIncrement": true,
      "android": { "buildType": "app-bundle" }
    }
  },
  "submit": {
    "internal": {
      "android": {
        "serviceAccountKeyPath": "./secrets/play-service-account.json",
        "track": "internal",
        "releaseStatus": "completed"
      }
    }
  }
}
```

```bash
# production AAB banao
eas build -p android --profile production
# internal track par bhejo
eas submit -p android --profile internal --latest
```

Note: `distribution: "internal"` EAS ka apna internal distribution hai (direct APK link) — Play ke "Internal testing track" se alag cheez hai. Dono ka naam milta-julta hai, interview me confuse mat karna.

## 💻 Code Example — Advanced
App me build ka version dikhana taaki testers bug report me sahi build bata sakein (`expo-application` se, Expo SDK 53/54):

```jsx
// BuildInfo.jsx — Settings me chhota footer
import React from 'react';                          // React
import { Text, View, Platform } from 'react-native'; // RN components
import * as Application from 'expo-application';     // npx expo install expo-application

// Build info component
export default function BuildInfo() {
  // Android me versionCode, iOS me buildNumber = Application.nativeBuildVersion
  const build = Application.nativeBuildVersion;
  // User ko dikhne wala version = Application.nativeApplicationVersion
  const version = Application.nativeApplicationVersion;
  // UI
  return (
    <View style={{ padding: 12 }}>
      <Text>v{version} ({build}) - {Platform.OS}</Text>
      {/* dev builds me extra flag */}
      {__DEV__ ? <Text>DEBUG build</Text> : null}
    </View>
  );
}
```

```bash
# Testers ke liye opt-in link ko Slack/Notion me share karo
# Sirf wahi Gmail IDs jo email list me hain install kar sakte hain
```

---

## 📱 Android vs iOS Difference
| Feature | Android Internal Testing | iOS TestFlight Internal |
|---------|--------------------------|-------------------------|
| Testers | ~100 (email list) | Up to 100 App Store Connect team members |
| Review | Usually no full review | No review for internal |
| Availability | Minutes | After build processing |
| Install via | Play Store opt-in link | TestFlight app |
| Expiry | No fixed 90-day limit like TestFlight builds | Builds expire in 90 days |
| Account | Gmail / Google account | Apple ID in team |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas submit -p android --profile internal --latest   # latest build ko internal track par
```
CLI way:
```bash
# Fastlane supply se internal track par upload
fastlane supply --aab app-release.aab --track internal
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Tester ka email list me add na hona (ya alag Google account se install).
✅ **Correct:** Wahi Gmail jo list me hai, usi se Play Store me login.

❌ **Mistake 2:** Opt-in link ke bina Play Store me search karna.
✅ **Correct:** Pehle opt-in link se "Become a tester".

❌ **Mistake 3:** Internal build ko release samajh lena.
✅ **Correct:** Production me promote karna alag step hai.

❌ **Mistake 4:** Internal testing ko Expo "internal distribution" samajhna.
✅ **Correct:** Dono alag hain; ek Play ka track hai, doosra EAS ka direct APK/ad-hoc link.

---

## 🧠 Tricky Interview Question
**Q: Internal track par build install nahi ho raha ("Item not found") — kya wajah ho sakti hai?**

**Answer:** Common reasons: (1) tester ne opt-in link accept nahi kiya, (2) tester ka Google account email list me nahi hai, (3) device ka Play Store usi account se login nahi hai, (4) release abhi "Draft" hai — "Start rollout" nahi hua, (5) device un countries/devices me nahi hai jo release me supported hain, (6) minSdk device se zyada hai. Console me "Releases" me status check karo aur tester se opt-in dobara karwao.

---

## ⚫ Interview Questions + Answers

**Q1: Internal testing me review hota hai kya?**
A1: Aam taur par full review nahi hota, isliye minutes me available hota hai (policy checks background me ho sakte hain).

**Q2: Kitne testers?**
A2: Lagbhag 100 tak (Console ka limit dekho).

**Q3: Promote kaise karte hain?**
A3: Internal testing → Release page par "Promote release" → Closed testing / Production; same AAB reuse hota hai.

**Q4: Internal testing se Android vitals milte hain?**
A4: Crash/ANR data testers ke sessions se aata hai; chhote sample ke kaaran limited hota hai.

**Q5: Internal track par pehla upload kaise?**
A5: Console me manual; baad me `eas submit` track `internal`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Daily QA builds, UAT, stakeholders demo.
- Real Play environment me payments/billing test.

❌ Avoid when:
- Badi public beta chahiye — open testing use karo.
- Sirf quick debugging — local APK ya EAS internal distribution.

---

## 📊 Visual Diagram
```
 CI build ─► AAB ─► Internal track ─► QA (≤100 Gmail)
                         │
             fix? ◄──────┘ (new versionCode)
                         │ ok
                         ▼
                  Promote → Closed → Open → Production
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Track | Release channel | Release channel |
| Email list | Allowed testers | Testers की सूची |
| Opt-in link | Tester join link | Join करने का link |
| Promote | Move build to next track | Build को अगले track पर ले जाना |
| UAT | User acceptance test | उपयोगकर्ता स्वीकृति परीक्षण |

---

## ⚡ 3-Line Summary
**English:**
1. Internal track = fast, no-review test channel for ~100 testers.
2. Testers join via opt-in link with an email on the list.
3. Promote the same AAB onward when it passes QA.

**Hindi:**
1. Internal track = लगभग 100 testers के लिए तेज़, बिना-review वाला test channel।
2. Testers list वाले email से opt-in link के ज़रिए जुड़ते हैं।
3. QA पास होने पर वही AAB आगे promote करो।

---

## ➡️ Next Topic
**218. Closed Testing (Alpha)** — बड़े चुने हुए group के साथ test करना।
