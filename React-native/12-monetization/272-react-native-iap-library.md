# 272. react-native-iap Library
# हिंदी में: react-native-iap Library
# Platform: Android ✅ | iOS ✅ | Both ✅
# Expo SDK 54 (React Native 0.81) — check current docs — APIs change between SDKs

---

## 🔵 Simple Definition (English)
**react-native-iap** is a community library that wraps Google Play Billing (Android) and StoreKit (iOS) behind one JavaScript API. You call `initConnection`, fetch products, `requestPurchase` and `finishTransaction` — the library talks to the native store SDKs. It has native code, so it does **not** run in Expo Go; use a development build.

⚠️ This library's API changed across major versions (v12 → v13 → v14 with Nitro modules). Always read the docs for the version you install.

## 🔵 सरल परिभाषा (Hindi)
**react-native-iap** एक community library है जो Google Play Billing (Android) और StoreKit (iOS) को एक JavaScript API में लपेटती है। आप `initConnection`, products fetch, `requestPurchase`, `finishTransaction` call करते हो — बाकी native काम library करती है। इसमें native code है, इसलिए **Expo Go में नहीं चलती**; development build चाहिए।

⚠️ Major versions (v12 → v13 → v14) में API बदली है — install किए version की docs ज़रूर पढ़ो।

---

## 🔴 Problem it Solves
```
❌ Writing Kotlin (BillingClient) + Swift (StoreKit) wrappers yourself
❌ Two different purchase models to learn
✅ One JS API (hook or functions) for both stores
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ Kotlin (BillingClient) + Swift (StoreKit) wrappers खुद लिखना
❌ दो अलग purchase models सीखना
✅ दोनों stores के लिए एक JS API (hook या functions)
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → npx expo install react-native-iap  (or npm i for bare)
Step 2 → Add "react-native-iap" to app.json plugins; build dev client
Step 3 → initConnection() (or useIAP() which does it for you)
Step 4 → Fetch: getProducts / getSubscriptions (v12) — names differ in newer versions
Step 5 → requestPurchase / requestSubscription
Step 6 → purchaseUpdatedListener fires with the purchase object
Step 7 → Verify on server → finishTransaction
Step 8 → endConnection() on unmount
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → npx expo install react-native-iap
Step 2 → app.json plugins में जोड़ो; dev client build करो
Step 3 → initConnection() (या useIAP() खुद कर देता है)
Step 4 → products fetch: getProducts / getSubscriptions (v12; नए version में नाम अलग)
Step 5 → requestPurchase / requestSubscription
Step 6 → purchaseUpdatedListener में purchase आता है
Step 7 → Server पर verify → finishTransaction
Step 8 → unmount पर endConnection()
```

---

## 🟡 Real World Example
A small Indian edtech startup (like **Unacademy-style** apps) with a React Native app wants Android + iOS premium unlock without a paid service. They use `react-native-iap`, write their own Node verification endpoint, and avoid RevenueCat's revenue-based fee. Trade-off: they maintain receipt validation + notification handling themselves.

## 🟡 Real Example Hindi mein
**Unacademy** जैसा छोटा edtech startup बिना paid service के Android + iOS premium unlock चाहता है। वे `react-native-iap` + अपना Node verification endpoint इस्तेमाल करते हैं और RevenueCat की fee बचाते हैं। बदले में receipt validation और notifications खुद संभालनी पड़ती हैं।

---

## 💻 Code Example — Basic

Function API (no hook), one-time product:
```jsx
import React, { useEffect, useState } from 'react';             // React
import { View, Text, Button, Alert } from 'react-native';       // UI
import {
  initConnection, endConnection, getProducts,
  requestPurchase, purchaseUpdatedListener, finishTransaction,
} from 'react-native-iap';                                       // v12-style functions

const SKUS = ['remove_ads'];                                     // product id (same on both stores)

export default function RemoveAds() {
  const [product, setProduct] = useState(null);                  // loaded product

  useEffect(() => {
    let sub;                                                     // listener handle
    (async () => {
      await initConnection();                                    // connect to store
      const items = await getProducts({ skus: SKUS });           // fetch product info
      setProduct(items[0] ?? null);                              // save first product
      // Listen for successful purchases
      sub = purchaseUpdatedListener(async (purchase) => {
        await finishTransaction({ purchase, isConsumable: false }); // acknowledge
        Alert.alert('Thanks!', 'Ads removed');                   // feedback
      });
    })().catch((e) => Alert.alert('IAP error', String(e)));
    // Cleanup on unmount
    return () => { sub?.remove(); endConnection(); };
  }, []);

  if (!product) return <Text>Loading store...</Text>;            // while loading
  return (
    <View style={{ padding: 20 }}>
      <Text>{product.title} — {product.localizedPrice}</Text>
      <Button title="Buy" onPress={() => requestPurchase({ skus: [product.productId] })} />
    </View>
  );
}
```

## 💻 Code Example — Advanced

Version-safe wrapper so UI code does not break when the library API changes:
```jsx
// iapService.js — the ONLY file that imports react-native-iap
import { Platform } from 'react-native';
import * as IAP from 'react-native-iap';

// Normalised product shape used by the rest of the app
const toProduct = (p) => ({
  id: p.productId ?? p.id,                  // names differ by version
  title: p.title ?? p.displayName,
  price: p.localizedPrice ?? p.displayPrice,
});

export const iapService = {
  async init() {
    await IAP.initConnection();             // connect
    if (Platform.OS === 'android') {
      // Android-only cleanup of stuck pending purchases
      await IAP.flushFailedPurchasesCachedAsPendingAndroid?.().catch(() => {});
    }
  },
  async loadProducts(skus) {
    // v12 API; if you upgrade, change ONLY this line (e.g. fetchProducts in newer versions)
    const list = await IAP.getProducts({ skus });
    return list.map(toProduct);
  },
  buy(sku) {
    return Platform.OS === 'ios'
      ? IAP.requestPurchase({ sku })        // iOS
      : IAP.requestPurchase({ skus: [sku] }); // Android
  },
  onPurchase(handler) {
    // returns unsubscribe fn
    const s = IAP.purchaseUpdatedListener(handler);
    return () => s.remove();
  },
  finish(purchase, consumable) {
    return IAP.finishTransaction({ purchase, isConsumable: consumable });
  },
  restore: () => IAP.getAvailablePurchases(),
  close: () => IAP.endConnection(),
};
```
Why: wrapping isolates version-dependent calls; screens and tests depend on `iapService` only. Not run (native module).

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Request call | `requestPurchase({ skus: [..] })` | `requestPurchase({ sku })` (v12) |
| Subscriptions | needs `offerToken` | sku only |
| Extra APIs | `acknowledgePurchaseAndroid`, `flushFailedPurchasesCachedAsPendingAndroid` | `getReceiptIOS`, `clearTransactionIOS`, `presentCodeRedemptionSheetIOS` |
| Verify | purchaseToken | transaction receipt / JWS |
| Local testing | License testers | Sandbox / StoreKit config |

---

## 🟠 Expo vs CLI Difference
Expo way:
```json
{ "expo": { "plugins": ["react-native-iap"] } }
```
```bash
eas build --profile development --platform all
```
CLI way:
```bash
npm i react-native-iap
cd ios && pod install
# Android: autolinked; check README for any Gradle flavour settings
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Copying a StackOverflow snippet from another major version
✅ **Correct:** Match code to your installed version; wrap in a service file.

❌ **Mistake 2:** Calling functions before `initConnection`
✅ **Correct:** Await connection (or wait for `connected` in `useIAP`).

❌ **Mistake 3:** Not removing listeners
✅ **Correct:** Remove in cleanup to avoid duplicate grants.

❌ **Mistake 4:** Running in Expo Go
✅ **Correct:** Development build.

---

## 🧠 Tricky Interview Question
**Q:** Why can the purchase listener fire twice for one purchase and double-credit coins?

**Answer:** Listener registered multiple times (re-render without cleanup, React StrictMode double effects), or the purchase is re-delivered because it was never finished. Make the handler idempotent (store processed transaction ids/tokens, server credits once) and always remove listeners in cleanup.

---

## ⚫ Interview Questions + Answers

**Q1: Hook vs functions?**
A1: `useIAP` manages connection/state for you; functions give control outside components.

**Q2: Why does it not work in Expo Go?**
A2: Custom native code not bundled in Expo Go.

**Q3: What does `finishTransaction` do per platform?**
A3: Android: consume (consumable) or acknowledge; iOS: finish the StoreKit transaction.

**Q4: react-native-iap vs RevenueCat?**
A4: IAP lib = client wrapper only; RevenueCat = wrapper + backend validation, entitlements, analytics (fee).

**Q5: How to test locally?**
A5: Android: license testers + Play-installed build; iOS: sandbox account or StoreKit configuration file.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Want free/open-source, own backend

❌ Avoid when:
- Small team without backend time (use RevenueCat)

---

## 📊 Visual Diagram
```
 Your UI ─► iapService ─► react-native-iap ─┬─► Play Billing (Android)
                                            └─► StoreKit (iOS)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| useIAP | Hook managing IAP state | IAP state संभालने वाला hook |
| initConnection | Connect to store | Store से connect |
| finishTransaction | Complete purchase | Purchase पूरा करना |
| Nitro | New native module system used by v14 | v14 का नया native module system |
| Idempotent | Safe to repeat | दोहराने पर भी सुरक्षित |

---

## ⚡ 3-Line Summary
**English:**
1. One JS API over Play Billing and StoreKit.
2. Needs a dev build; API differs by major version.
3. Wrap it in a service and verify purchases on a server.

**Hindi:**
1. Play Billing और StoreKit के ऊपर एक JS API।
2. Dev build चाहिए; major version के साथ API बदलती है।
3. Service में wrap करो और server पर verify करो।

---

## ➡️ Next Topic
**273. RevenueCat** — बिना अपने backend के subscriptions manage करना।
