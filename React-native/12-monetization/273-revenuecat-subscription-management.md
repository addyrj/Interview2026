# 273. RevenueCat — Subscription Management
# हिंदी में: RevenueCat — Subscription Management
# Platform: Android ✅ | iOS ✅ | Both ✅
# Expo SDK 54 (React Native 0.81) — check current docs — APIs change between SDKs

---

## 🔵 Simple Definition (English)
**RevenueCat** is a hosted service + SDK (`react-native-purchases`) that handles in-app purchases and subscriptions for Android and iOS. It validates receipts on its servers, tracks **entitlements** ("is this user Pro?"), syncs across devices, and gives dashboards — so you don't build a backend. It needs a development build (not Expo Go, though it has a preview mode there).

## 🔵 सरल परिभाषा (Hindi)
**RevenueCat** एक hosted service + SDK (`react-native-purchases`) है जो Android और iOS के in-app purchases और subscriptions संभालती है। Receipt validation अपने servers पर करती है, **entitlements** ("क्या यह user Pro है?") track करती है, devices में sync रखती है और dashboard देती है — आपको backend नहीं बनाना पड़ता। Development build चाहिए (Expo Go में सिर्फ preview/mock mode)।

---

## 🔴 Problem it Solves
```
❌ Receipt validation for 2 stores = backend work + security
❌ Subscription state machine: trial, grace, renewal, refund, upgrade
❌ Same user on Android + iOS + web — who is Pro?
❌ No revenue analytics (MRR, churn)
✅ RevenueCat: SDK + dashboard + webhooks
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ दो stores के receipt validation = backend काम + security
❌ Subscription के states: trial, grace, renewal, refund, upgrade
❌ एक user Android + iOS + web पर — Pro कौन?
❌ Revenue analytics (MRR, churn) नहीं
✅ RevenueCat: SDK + dashboard + webhooks
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create RevenueCat project; add Android app (Play) + iOS app (App Store)
Step 2 → Connect stores: Play service-account JSON; App Store Connect API key
Step 3 → Create products in the stores; import them in RevenueCat → Products
Step 4 → Create ENTITLEMENT "pro" and attach products
Step 5 → Create OFFERING "default" with packages ($rc_monthly, $rc_annual)
Step 6 → App: Purchases.configure({ apiKey }) (public SDK key per platform)
Step 7 → Purchases.getOfferings() → show packages
Step 8 → Purchases.purchasePackage(pkg) → customerInfo returned
Step 9 → Check customerInfo.entitlements.active["pro"]
Step 10 → Optional: webhooks to your backend; Purchases.logIn(userId) to link accounts
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → RevenueCat project बनाओ; Android (Play) + iOS (App Store) apps जोड़ो
Step 2 → Stores connect करो: Play service-account JSON; App Store Connect API key
Step 3 → Stores में products बनाओ; RevenueCat में import
Step 4 → ENTITLEMENT "pro" बनाओ और products attach करो
Step 5 → OFFERING "default" बनाओ (packages: monthly, annual)
Step 6 → App में Purchases.configure({ apiKey })
Step 7 → Purchases.getOfferings() से packages दिखाओ
Step 8 → Purchases.purchasePackage(pkg) → customerInfo मिलता है
Step 9 → customerInfo.entitlements.active["pro"] से check
Step 10 → Webhooks और Purchases.logIn(userId) से accounts link
```

---

## 🟡 Real World Example
A meditation app (like **Headspace**-style, or an Indian one like **Wysa-type** apps) offers ₹299/month and ₹1999/year. With RevenueCat the team changes the price/offer order from the dashboard (A/B paywall experiments) without releasing a new app version.

## 🟡 Real Example Hindi mein
Meditation app (**Headspace** जैसा या **Wysa** जैसे Indian apps) ₹299/month और ₹1999/year देता है। RevenueCat से team dashboard से ही price/offer का क्रम बदल सकती है (A/B paywall experiments) — नया app version release किए बिना।

---

## 💻 Code Example — Basic

```jsx
import React, { useEffect, useState } from 'react';                // React
import { View, Text, Button, Platform, ActivityIndicator, Alert } from 'react-native'; // UI
import Purchases from 'react-native-purchases';                    // RevenueCat SDK

// Public SDK keys (safe to ship) — one per platform from RevenueCat dashboard
const API_KEY = Platform.select({
  ios: 'appl_XXXXXXXXXXXX',        // placeholder
  android: 'goog_XXXXXXXXXXXX',    // placeholder
});

export default function Paywall() {
  const [packages, setPackages] = useState([]);                    // available packages
  const [isPro, setIsPro] = useState(false);                       // entitlement flag
  const [loading, setLoading] = useState(true);                    // spinner

  useEffect(() => {
    (async () => {
      Purchases.configure({ apiKey: API_KEY });                    // init once
      const info = await Purchases.getCustomerInfo();              // current user state
      setIsPro(!!info.entitlements.active['pro']);                 // is "pro" active?
      const offerings = await Purchases.getOfferings();            // paywall products
      setPackages(offerings.current?.availablePackages ?? []);     // default offering
      setLoading(false);
    })().catch((e) => { Alert.alert('Error', String(e)); setLoading(false); });
  }, []);

  const buy = async (pkg) => {
    try {
      const { customerInfo } = await Purchases.purchasePackage(pkg); // store sheet
      setIsPro(!!customerInfo.entitlements.active['pro']);          // update access
    } catch (e) {
      if (!e.userCancelled) Alert.alert('Purchase failed', e.message); // ignore cancel
    }
  };

  if (loading) return <ActivityIndicator />;
  if (isPro) return <Text>You are Pro!</Text>;
  return (
    <View style={{ padding: 20 }}>
      {packages.map((p) => (
        <Button key={p.identifier}
          title={`${p.product.title} ${p.product.priceString}`}
          onPress={() => buy(p)} />
      ))}
      {/* Restore button (required by Apple) */}
      <Button title="Restore" onPress={() => Purchases.restorePurchases()} />
    </View>
  );
}
```
Expo `app.json`: `{ "expo": { "plugins": ["react-native-purchases"] } }` (check docs for current plugin guidance).

## 💻 Code Example — Advanced

Context provider: user login linking, live updates, safe listener cleanup:
```jsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import Purchases from 'react-native-purchases';

const ProContext = createContext({ isPro: false, ready: false });

// userId = your own backend user id (null when logged out)
export function ProProvider({ userId, children }) {
  const [state, setState] = useState({ isPro: false, ready: false });

  useEffect(() => {
    // Convert RevenueCat customerInfo -> app state
    const apply = (info) =>
      setState({ isPro: !!info.entitlements.active['pro'], ready: true });

    (async () => {
      try {
        // Link purchases to your user so Android + iOS + web share entitlement
        const { customerInfo } = userId
          ? await Purchases.logIn(userId)
          : { customerInfo: await Purchases.getCustomerInfo() };
        apply(customerInfo);
      } catch (e) {
        console.warn('RC error', e);
        setState((s) => ({ ...s, ready: true })); // do not block app forever
      }
    })();

    // Fires on renewals / expiry / purchases from other devices
    Purchases.addCustomerInfoUpdateListener(apply);
    // Cleanup — remove the SAME function
    return () => { Purchases.removeCustomerInfoUpdateListener(apply); };
  }, [userId]);

  return <ProContext.Provider value={state}>{children}</ProContext.Provider>;
}

export const usePro = () => useContext(ProContext);
```
For ready-made paywalls see `react-native-purchases-ui` (`RevenueCatUI.presentPaywall()`), check docs. Not run here (native SDK + store setup required).

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| SDK key | `goog_...` | `appl_...` |
| Store link | Service-account JSON (needs Play API permissions) | App Store Connect API key + shared secret |
| Restore | Automatic via Play | `restorePurchases()` button |
| Webhook event names | Mapped to common events | Mapped to common events |
| Test | License testers | Sandbox testers |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo install react-native-purchases
eas build --profile development --platform all   # dev build; Expo Go only runs a mock "Preview API mode"
```
CLI way:
```bash
npm i react-native-purchases
cd ios && pod install
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Using secret API key in the app
✅ **Correct:** Only the public SDK key goes in the app; secret keys stay on server.

❌ **Mistake 2:** Checking product ids instead of entitlements
✅ **Correct:** Check `entitlements.active['pro']` — products can change.

❌ **Mistake 3:** Not calling `logIn` → anonymous IDs per install
✅ **Correct:** `logIn(userId)` after authentication.

❌ **Mistake 4:** Treating `userCancelled` as an error
✅ **Correct:** Ignore silently.

---

## 🧠 Tricky Interview Question
**Q:** A user subscribed on iPhone and then opens your Android app, logged in. They are not Pro. Why, and how to fix it?

**Answer:** Each install got a different anonymous RevenueCat App User ID. Subscription is attached to the iPhone's anonymous id. Fix: call `Purchases.logIn(yourUserId)` on both platforms so purchases are merged under one ID; entitlements then show everywhere (Apple/Google subscriptions themselves remain store-specific; RevenueCat merges the entitlement).

---

## ⚫ Interview Questions + Answers

**Q1: Entitlement vs offering vs package?**
A1: Entitlement = access level; offering = set of products to show; package = one purchasable item in an offering.

**Q2: Why use RevenueCat?**
A2: No backend validation, cross-platform sync, analytics, experiments; trade-off = fee after revenue threshold and vendor dependency.

**Q3: Does it replace Play Billing/StoreKit?**
A3: No — it wraps them; users still pay through the stores.

**Q4: How to know purchases on your backend?**
A4: Webhooks or REST API.

**Q5: Expo Go support?**
A5: Only preview mode; real purchases need a dev build.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Small team, subscriptions, need analytics

❌ Avoid when:
- Cannot use third-party for compliance, or very high revenue where fee matters

---

## 📊 Visual Diagram
```
 App SDK ──► RevenueCat servers ──► Play / App Store (validate)
    ▲              │ entitlements, analytics, webhooks
    └──────────────┘ customerInfo ("pro" active?)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Entitlement | Access level | Access स्तर |
| Offering | Group of packages for paywall | Paywall के packages का समूह |
| Package | Purchasable unit | खरीदने योग्य इकाई |
| customerInfo | User's purchase state | User की purchase स्थिति |
| App User ID | Identifier of customer | Customer की id |

---

## ⚡ 3-Line Summary
**English:**
1. RevenueCat = SDK + backend for purchases; you check entitlements.
2. Configure stores, products, entitlement, offering, then `purchasePackage`.
3. Use `logIn` to share access across devices.

**Hindi:**
1. RevenueCat = purchases के लिए SDK + backend; आप entitlements check करते हो।
2. Stores, products, entitlement, offering set करो, फिर `purchasePackage`।
3. Devices में access share करने के लिए `logIn` use करो।

---

## ➡️ Next Topic
**274. Ads Integration (AdMob)** — subscription के अलावा ads से कमाई।
