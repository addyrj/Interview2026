# 271. Subscriptions Setup
# हिंदी में: Subscriptions Setup (Monthly / Yearly Plans)
# Platform: Android ✅ | iOS ✅ | Both ✅
# Expo SDK 54 (React Native 0.81) — check current docs — APIs change between SDKs

---

## 🔵 Simple Definition (English)
A **subscription** is an in-app purchase that renews automatically (weekly, monthly, yearly) until the user cancels. The store (Google Play / App Store) bills the user, handles free trials, grace periods and cancellations, and sends your backend **server notifications** so you can keep the user's access in sync.

## 🔵 सरल परिभाषा (Hindi)
**Subscription** ऐसा in-app purchase है जो अपने-आप renew होता है (weekly, monthly, yearly) जब तक user cancel न करे। Store (Google Play / App Store) billing, free trial, grace period और cancellation संभालता है और आपके backend को **server notifications** भेजता है ताकि user का access sync रहे।

---

## 🔴 Problem it Solves
```
❌ One-time purchases give one payment — no recurring revenue
❌ Building your own renewal + retry-on-failed-card + proration = huge
❌ Users forget to cancel → chargeback/complaints
✅ Stores run recurring billing, retries, trials, refunds for you
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ One-time purchase = एक ही बार पैसा, recurring income नहीं
❌ खुद renewal + failed card retry + proration बनाना बहुत बड़ा काम
✅ Stores recurring billing, retry, trial, refund सब संभालते हैं
```

---

## 🟢 How it Works — Step by Step

```
ANDROID (Play Console → Monetize → Subscriptions):
Step 1 → Create subscription (product id e.g. "pro")
Step 2 → Add BASE PLANS: "monthly" (P1M), "yearly" (P1Y), auto-renewing
Step 3 → Add OFFERS (e.g. 7-day free trial) with eligibility rules
Step 4 → Activate the base plan

iOS (App Store Connect → Subscriptions):
Step 1 → Create a SUBSCRIPTION GROUP ("Pro")
Step 2 → Add subscriptions inside: pro.monthly, pro.yearly (ranked levels)
Step 3 → Add introductory offer (free trial) + localization + price
Step 4 → Submit with app version

BOTH:
Step 5 → App fetches subscription products and shows paywall
Step 6 → User subscribes → app gets purchase → verify on server
Step 7 → Server listens: Google RTDN (Pub/Sub) / Apple App Store Server Notifications
         for RENEWED, CANCELED, EXPIRED, GRACE_PERIOD, REFUND events
Step 8 → App checks entitlement (active until expiry date) on every launch
```

## 🟢 कैसे काम करता है? (Hindi)
```
ANDROID: Play Console → Monetize → Subscriptions
  → subscription बनाओ → Base plans (monthly P1M, yearly P1Y) → Offers (7-day trial) → Activate
iOS: App Store Connect → Subscription Group बनाओ
  → उसमें pro.monthly, pro.yearly → Intro offer (free trial) → price, localization
दोनों:
  → App paywall दिखाता है → user subscribe करता है → server पर verify
  → Server को notifications मिलती हैं: renewed, canceled, expired, grace, refund
  → App हर launch पर expiry date से entitlement check करता है
```

---

## 🟡 Real World Example
**Hotstar, Spotify, Zomato Gold, Swiggy One**-style plans: Monthly ₹149, Yearly ₹999 (best value), 7-day free trial. If the user's card fails, Google/Apple enter a **grace period** so the user keeps access while the store retries.

## 🟡 Real Example Hindi mein
**Hotstar, Spotify, Zomato Gold, Swiggy One** जैसे plans: Monthly ₹149, Yearly ₹999 (best value), 7 दिन free trial। Card fail हो जाए तो Google/Apple **grace period** देते हैं — store retry करता है और user का access चलता रहता है।

---

## 💻 Code Example — Basic

Paywall using `react-native-iap` (v12-style; Android needs `offerToken` from the selected offer):
```jsx
import React, { useEffect } from 'react';                       // React
import { View, Text, Button, Platform } from 'react-native';    // UI
import { useIAP, withIAPContext } from 'react-native-iap';      // IAP hook

const SUB_SKUS = ['pro_monthly', 'pro_yearly']; // iOS product ids (Android: base plan product id)

function Paywall() {
  const { connected, subscriptions, getSubscriptions, requestSubscription } = useIAP();

  // Load subscription products after connect
  useEffect(() => {
    if (connected) getSubscriptions({ skus: SUB_SKUS });
  }, [connected]);

  // Buy handler differs per platform
  const buy = (sub) => {
    if (Platform.OS === 'android') {
      // Android: must pass offerToken of the chosen offer/base plan
      const offerToken = sub.subscriptionOfferDetails?.[0]?.offerToken;
      return requestSubscription({
        sku: sub.productId,
        subscriptionOffers: [{ sku: sub.productId, offerToken }],
      });
    }
    // iOS: only sku needed
    return requestSubscription({ sku: sub.productId });
  };

  return (
    <View style={{ padding: 20 }}>
      <Text style={{ fontSize: 22, fontWeight: '700' }}>Go Pro</Text>
      {subscriptions.map((s) => (
        <Button key={s.productId} title={`${s.title} (${s.productId})`} onPress={() => buy(s)} />
      ))}
    </View>
  );
}
export default withIAPContext(Paywall);
```

## 💻 Code Example — Advanced

Entitlement check from server + grace period handling:
```jsx
import { useEffect, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage'; // offline cache

// Server returns { status: 'active'|'grace'|'expired', expiresAt: ISO date }
export function useEntitlement(userId) {
  const [state, setState] = useState({ loading: true, isPro: false, status: 'unknown' });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        // Ask OUR backend (single source of truth, fed by store notifications)
        const r = await fetch(`https://api.example.com/users/${userId}/entitlement`);
        const data = await r.json();
        // active OR grace period => keep access
        const isPro = data.status === 'active' || data.status === 'grace';
        await AsyncStorage.setItem('ent', JSON.stringify(data)); // cache
        if (!cancelled) setState({ loading: false, isPro, status: data.status });
      } catch {
        // Offline: use cached value but only if not expired
        const raw = await AsyncStorage.getItem('ent');
        const data = raw ? JSON.parse(raw) : null;
        const ok = data && new Date(data.expiresAt) > new Date();
        if (!cancelled) setState({ loading: false, isPro: !!ok, status: data?.status ?? 'unknown' });
      }
    })();
    return () => { cancelled = true; };
  }, [userId]);

  return state;
}
```
Server side concept: Google sends Real-time Developer Notifications to a Pub/Sub topic; Apple POSTs App Store Server Notifications V2 to your URL. Update the user's row on each event. Not run here.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Structure | Subscription → Base plans → Offers | Subscription Group → Subscriptions |
| Buying | needs `offerToken` | only product id |
| Free trial | Offer on base plan | Introductory offer |
| Grace period | Configurable in Play Console | Billing Grace Period toggle in ASC |
| Server events | Real-time developer notifications (Pub/Sub) | App Store Server Notifications V2 |
| Manage page | play.google.com/store/account/subscriptions | Settings → Apple ID → Subscriptions |
| Upgrade/downgrade | Proration modes | Levels within group (auto handled) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo install react-native-iap   # + plugin, dev build via EAS
# or use RevenueCat (react-native-purchases) — also needs dev build
```
CLI way:
```bash
npm i react-native-iap && cd ios && pod install
# Add In-App Purchase capability in Xcode
```
Both ways: no Expo Go support.

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Storing "isPro = true" only on device
✅ **Correct:** Entitlement comes from the server/store with an expiry date.

❌ **Mistake 2:** Android purchase without `offerToken`
✅ **Correct:** Pass the token from `subscriptionOfferDetails`.

❌ **Mistake 3:** Ignoring renewals/cancel notifications
✅ **Correct:** Handle server notifications so expired users lose access.

❌ **Mistake 4:** Putting monthly and yearly in different iOS groups
✅ **Correct:** Same group so users can switch and not hold two at once.

---

## 🧠 Tricky Interview Question
**Q:** A user cancelled yesterday but still sees premium today. Bug?

**Answer:** No. Cancelling only turns off *auto-renew*; the user paid until the period end, so access continues until `expiresAt`. Revoke access only on EXPIRED (or REFUND/REVOKE) events, not on CANCELED.

---

## ⚫ Interview Questions + Answers

**Q1: Auto-renewing vs non-renewing?**
A1: Auto-renewing charges every period; non-renewing is a fixed-term pass you must re-sell manually.

**Q2: What is a grace period?**
A2: Extra days after a failed payment where access continues while the store retries.

**Q3: Free trial abuse?**
A3: Stores allow a trial once per user/account (Apple per group); server must not grant extra trials.

**Q4: How to restore subscriptions?**
A4: iOS Restore button / `getAvailablePurchases`; Android queries Play on launch.

**Q5: Why a backend?**
A5: Cross-device access, fraud resistance, web/Android/iOS entitlement sync.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Ongoing value (content, SaaS, fitness)

❌ Avoid when:
- One-off unlock (use non-consumable)
- No ongoing value — users resent renewals

---

## 📊 Visual Diagram
```
 Subscribe ─► Store bills ─► purchase token ─► your server (verify)
      ▲             │ every period
      │             ▼
  entitlement ◄── Store notification (RENEWED / EXPIRED / GRACE / REFUND)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Base plan | Billing period config (Android) | Billing period का config |
| Offer | Trial/discount on a plan | Trial/discount |
| Subscription group | iOS plan family | iOS plan का समूह |
| Grace period | Access during payment retry | Payment retry के दौरान access |
| RTDN | Google real-time notifications | Google की real-time सूचनाएँ |
| Entitlement | What user is allowed to use | User को क्या use करने की अनुमति |

---

## ⚡ 3-Line Summary
**English:**
1. Subscriptions auto-renew; configure plans in Play Console / App Store Connect.
2. App shows paywall; server verifies and listens to store notifications.
3. Access depends on expiry date, not on "cancelled".

**Hindi:**
1. Subscriptions auto-renew होती हैं; plans Play Console / App Store Connect में।
2. App paywall दिखाता है; server verify करता है और notifications सुनता है।
3. Access expiry date पर निर्भर है, "cancelled" पर नहीं।

---

## ➡️ Next Topic
**272. react-native-iap Library** — इस library की पूरी API और versions का फर्क।
