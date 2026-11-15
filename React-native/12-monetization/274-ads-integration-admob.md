# 274. Ads Integration (AdMob)
# हिंदी में: AdMob से Ads लगाना
# Platform: Android ✅ | iOS ✅ | Both ✅
# Expo SDK 54 (React Native 0.81) — check current docs — APIs change between SDKs

---

## 🔵 Simple Definition (English)
**AdMob** is Google's mobile ad network. You show **banner**, **interstitial** (full-screen) and **rewarded** (watch-to-earn) ads in your app and earn money per impression/click. In React Native the maintained package is **`react-native-google-mobile-ads`** (the old `react-native-admob` and Expo's `expo-ads-admob` are deprecated/removed). Needs a development build.

## 🔵 सरल परिभाषा (Hindi)
**AdMob** Google का mobile ad network है। आप app में **banner**, **interstitial** (full-screen) और **rewarded** (देखकर इनाम) ads दिखाते हो और impression/click पर कमाते हो। React Native में maintained package **`react-native-google-mobile-ads`** है (पुराने `react-native-admob` और `expo-ads-admob` बंद हो चुके हैं)। Development build चाहिए।

---

## 🔴 Problem it Solves
```
❌ Free apps need revenue; not everyone subscribes
❌ Finding advertisers yourself is impossible for a small developer
✅ AdMob auto-fills ads from Google's advertiser pool, pays monthly
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ Free apps को revenue चाहिए; सब subscribe नहीं करते
❌ छोटे developer के लिए advertisers खोजना असंभव
✅ AdMob Google के advertisers से ads भरता है, महीने में पैसे देता है
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create AdMob account → Add app (Android + iOS separately)
         → get App ID (ca-app-pub-xxxx~yyyy)
Step 2 → Create Ad Units (Banner / Interstitial / Rewarded)
         → each gets an Ad Unit ID (ca-app-pub-xxxx/zzzz)
Step 3 → Install react-native-google-mobile-ads; add App IDs in app.json plugin
Step 4 → mobileAds().initialize() once at app start
Step 5 → Render <BannerAd /> or load + show Interstitial / Rewarded
Step 6 → DEV: use TestIds only (real ads on your own device can ban your account!)
Step 7 → iOS: ask App Tracking Transparency; EU: consent form (UMP)
Step 8 → Link AdMob to Play/App Store listing (app-ads.txt), go live
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → AdMob account → app जोड़ो (Android और iOS अलग) → App ID
Step 2 → Ad Units बनाओ (Banner / Interstitial / Rewarded) → Ad Unit ID
Step 3 → react-native-google-mobile-ads install; app.json plugin में App IDs
Step 4 → app start पर mobileAds().initialize()
Step 5 → <BannerAd /> दिखाओ या Interstitial / Rewarded load + show
Step 6 → DEV में सिर्फ TestIds — अपने device पर real ads click करने से account ban हो सकता है!
Step 7 → iOS: App Tracking Transparency; EU: consent form (UMP)
Step 8 → app-ads.txt और store listing link, फिर live
```

---

## 🟡 Real World Example
Free games and utility apps like **Ludo King**-style games show a banner on the home screen, an interstitial after each match, and a rewarded ad: "Watch a video to get 50 extra coins". Rewarded ads give higher eCPM and users opt in.

## 🟡 Real Example Hindi mein
**Ludo King** जैसे free games home screen पर banner, हर match के बाद interstitial और rewarded ad दिखाते हैं: "Video देखो और 50 coins पाओ"। Rewarded ads से eCPM ज़्यादा मिलता है और user अपनी मर्ज़ी से देखता है।

---

## 💻 Code Example — Basic

`app.json` (Expo — config plugin; use your real App IDs in production):
```json
{
  "expo": {
    "plugins": [
      [
        "react-native-google-mobile-ads",
        {
          "androidAppId": "ca-app-pub-3940256099942544~3347511713",
          "iosAppId": "ca-app-pub-3940256099942544~1458002511"
        }
      ]
    ]
  }
}
```
(Those IDs are Google's public sample App IDs.) Banner:
```jsx
import React from 'react';                                          // React
import { View, Text } from 'react-native';                          // UI
import { BannerAd, BannerAdSize, TestIds } from 'react-native-google-mobile-ads'; // ads

// In dev use TestIds; in production use your real Ad Unit ID
const adUnitId = __DEV__ ? TestIds.BANNER : 'ca-app-pub-xxxx/yyyy';

export default function Home() {
  return (
    <View style={{ flex: 1 }}>
      <Text style={{ padding: 20 }}>Home content</Text>
      {/* Banner pinned at the bottom */}
      <BannerAd
        unitId={adUnitId}                                  // which ad unit
        size={BannerAdSize.ANCHORED_ADAPTIVE_BANNER}       // adapts to screen width
        requestOptions={{ requestNonPersonalizedAdsOnly: true }} // privacy-friendly
      />
    </View>
  );
}
```

## 💻 Code Example — Advanced

Initialize SDK + rewarded ad hook with loading/error handling and interstitial frequency cap:
```jsx
import { useEffect, useRef, useState, useCallback } from 'react';
import mobileAds, {
  RewardedAd, RewardedAdEventType, InterstitialAd, AdEventType, TestIds,
} from 'react-native-google-mobile-ads';

// Call once at app start (e.g. in App.js useEffect)
export const initAds = () => mobileAds().initialize();

const REWARDED_ID = __DEV__ ? TestIds.REWARDED : 'ca-app-pub-xxxx/rewarded';
const INTER_ID = __DEV__ ? TestIds.INTERSTITIAL : 'ca-app-pub-xxxx/inter';

// Rewarded hook: const { ready, show } = useRewarded(onReward)
export function useRewarded(onReward) {
  const adRef = useRef(null);                       // current ad object
  const [ready, setReady] = useState(false);        // loaded?

  const load = useCallback(() => {
    setReady(false);
    const ad = RewardedAd.createForAdRequest(REWARDED_ID);   // create
    // Loaded event
    const offLoaded = ad.addAdEventListener(RewardedAdEventType.LOADED, () => setReady(true));
    // User earned reward
    const offReward = ad.addAdEventListener(RewardedAdEventType.EARNED_REWARD, (r) => onReward?.(r));
    // After close, preload the next ad
    const offClosed = ad.addAdEventListener(AdEventType.CLOSED, () => { cleanup(); load(); });
    // Failed to load — retry later (do not loop instantly)
    const offError = ad.addAdEventListener(AdEventType.ERROR, () => { cleanup(); setTimeout(load, 30000); });
    const cleanup = () => { offLoaded(); offReward(); offClosed(); offError(); };
    adRef.current = ad;
    ad.load();                                        // start loading
  }, [onReward]);

  useEffect(() => { load(); }, [load]);
  // Show only when loaded
  const show = () => ready && adRef.current?.show();
  return { ready, show };
}

// Interstitial with cap: at most 1 per 3 minutes, never at app launch
let lastShown = 0;
export function maybeShowInterstitial() {
  if (Date.now() - lastShown < 180000) return;      // too soon
  const ad = InterstitialAd.createForAdRequest(INTER_ID);
  const off = ad.addAdEventListener(AdEventType.LOADED, () => { lastShown = Date.now(); ad.show(); off(); });
  ad.load();
}
```
Not run here — needs native module, AdMob account and device. APIs shown match the library's documented names; confirm against the installed version.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| App ID | Separate AdMob app + ID | Separate AdMob app + ID |
| Tracking permission | Not required | ATT prompt + `NSUserTrackingUsageDescription` |
| Info config | AndroidManifest meta-data (plugin does it) | Info.plist `GADApplicationIdentifier` + SKAdNetwork IDs |
| Consent (EU/UK) | UMP SDK | UMP SDK |
| Test device | Add device id in AdMob | Add device id in AdMob |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo install react-native-google-mobile-ads
# add plugin with androidAppId/iosAppId in app.json
eas build --profile development --platform all
```
CLI way:
```bash
npm i react-native-google-mobile-ads && cd ios && pod install
# add app IDs to a firebase-like "app.json" config (react-native-google-mobile-ads key)
# or AndroidManifest/Info.plist as per README
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Using real ad unit IDs while developing and tapping your own ads
✅ **Correct:** TestIds in `__DEV__`; register test devices.

❌ **Mistake 2:** Showing interstitial on app open or every screen change
✅ **Correct:** At natural breaks with a frequency cap (policy + UX).

❌ **Mistake 3:** Missing App ID in config → app crashes on start
✅ **Correct:** Add in plugin / manifest.

❌ **Mistake 4:** Ads on kids apps without child-directed settings
✅ **Correct:** Set `tagForChildDirectedTreatment` via request configuration if applicable.

---

## 🧠 Tricky Interview Question
**Q:** Your banner is blank in production but works with TestIds. Why?

**Answer:** Usually: new ad units take a few hours to start serving; app not yet published/verified in AdMob; low fill in your region; wrong platform's unit id used; payment/policy review pending. Test IDs always fill, so they prove the code works, not the account setup.

---

## ⚫ Interview Questions + Answers

**Q1: Banner vs interstitial vs rewarded?**
A1: Banner = small persistent strip; interstitial = full-screen at transitions; rewarded = opt-in video for in-app reward.

**Q2: Why test ads?**
A2: Clicking your own live ads is invalid traffic and can disable the account.

**Q3: Is `expo-ads-admob` usable?**
A3: No — removed; use `react-native-google-mobile-ads` with a dev build.

**Q4: What is eCPM?**
A4: Earnings per 1000 impressions.

**Q5: How to be GDPR compliant?**
A5: Show UMP consent form before loading ads.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Free app with large casual audience

❌ Avoid when:
- Premium/finance/health apps where ads hurt trust
- Subscription-first products

---

## 📊 Visual Diagram
```
 App ─ initialize ─► Google Mobile Ads SDK ─ request ─► AdMob ─► advertiser auction
   ▲                                                         │
   └── ad (banner/interstitial/rewarded) shown ◄─────────────┘
                 impression/click ─► earnings
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ad Unit ID | Id of one ad placement | एक ad जगह की id |
| Interstitial | Full-screen ad | Full-screen ad |
| Rewarded ad | Ad for reward | इनाम वाला ad |
| eCPM | Revenue per 1000 views | 1000 views की कमाई |
| ATT | iOS tracking permission | iOS tracking permission |

---

## ⚡ 3-Line Summary
**English:**
1. AdMob via `react-native-google-mobile-ads` shows banner, interstitial, rewarded ads.
2. Use TestIds in dev, real IDs in prod, cap frequency, handle consent.
3. Needs dev build and correct App IDs.

**Hindi:**
1. AdMob `react-native-google-mobile-ads` से banner, interstitial, rewarded ads दिखाता है।
2. Dev में TestIds, prod में real IDs, frequency cap, consent संभालो।
3. Dev build और सही App IDs चाहिए।

---

## ➡️ Next Topic
**275. Stripe Payments in RN** — physical goods/services के लिए card payments।
