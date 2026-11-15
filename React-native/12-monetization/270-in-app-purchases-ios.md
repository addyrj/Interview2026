# 270. In-App Purchases (iOS)
# हिंदी में: iOS में In-App Purchases (StoreKit)
# Platform: iOS ✅ | Android ❌ (Android = topic 269) | iOS only
# Expo SDK 54 (React Native 0.81) — check current docs — APIs change between SDKs

---

## 🔵 Simple Definition (English)
On iOS, in-app purchases run on Apple's **StoreKit** framework. You create products in **App Store Connect**, the user pays with their Apple ID, and Apple returns a signed transaction. Apple's rule: digital content/features sold inside an iOS app **must** use IAP (guideline 3.1.1), and apps with IAP must offer a **Restore Purchases** option.

## 🔵 सरल परिभाषा (Hindi)
iOS पर in-app purchases Apple के **StoreKit** framework से चलते हैं। आप **App Store Connect** में products बनाते हो, user अपनी Apple ID से pay करता है और Apple signed transaction लौटाता है। Apple का नियम: iOS app में बिकने वाला digital content/feature **IAP से ही** बिकना चाहिए (guideline 3.1.1) और **Restore Purchases** का option ज़रूरी है।

---

## 🔴 Problem it Solves
```
❌ Without IAP: you'd handle cards, taxes, refunds, family sharing yourself
❌ Apple REJECTS apps that sell digital goods via external payment (typical case)
❌ Users switching iPhones lose purchases without a restore mechanism
✅ StoreKit: Apple handles payment, receipts, parental controls, refunds
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ IAP के बिना: card, tax, refund सब खुद संभालना
❌ बाहरी payment से digital सामान बेचने पर Apple app reject करता है
❌ नया iPhone लेने पर purchases गायब — restore ज़रूरी
✅ StoreKit: payment, receipt, parental control, refund सब Apple संभालता है
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Apple Developer: accept "Paid Applications Agreement",
         add bank + tax info (App Store Connect → Business)
Step 2 → App Store Connect → your app → Monetization → In-App Purchases
         → create product (Consumable / Non-Consumable / Subscription)
         with Product ID e.g. "com.myapp.coins100", price tier, screenshot
Step 3 → Add the "In-App Purchase" capability in Xcode (Expo: handled by plugin/EAS)
Step 4 → App: connect, fetch products by ID, show localized price
Step 5 → requestPurchase → Face ID / Apple ID password sheet
Step 6 → Transaction returned → verify with App Store Server API
Step 7 → Grant item → finishTransaction (else Apple keeps re-sending)
Step 8 → Provide a "Restore Purchases" button
Step 9 → Test with Sandbox Apple ID; submit IAP with app version for review
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Paid Applications Agreement accept करो, bank + tax info भरो
Step 2 → App Store Connect → Monetization → In-App Purchases → product बनाओ
         (Product ID जैसे "com.myapp.coins100", price, screenshot)
Step 3 → Xcode में In-App Purchase capability (Expo में plugin/EAS करता है)
Step 4 → App में Product ID से products लाओ, local price दिखाओ
Step 5 → requestPurchase → Face ID / Apple ID sheet
Step 6 → Transaction मिलता है → App Store Server API से verify
Step 7 → Item दो → finishTransaction (नहीं तो Apple बार-बार भेजता है)
Step 8 → "Restore Purchases" button दो
Step 9 → Sandbox Apple ID से test; IAP को app version के साथ review में भेजो
```

---

## 🟡 Real World Example
**Hotstar / JioCinema** style apps and **Duolingo-like** learning apps sell premium plans. On iPhone, the "Go Premium" price shows in ₹ via StoreKit. When a user installs the app on a new iPhone, "Restore Purchases" brings the premium back.

## 🟡 Real Example Hindi mein
**Hotstar / JioCinema** जैसे apps और **Duolingo** जैसे learning apps premium plan बेचते हैं। iPhone पर "Go Premium" का price StoreKit से ₹ में दिखता है। नए iPhone पर "Restore Purchases" से premium वापस मिल जाता है।

---

## 💻 Code Example — Basic

```jsx
import React, { useEffect } from 'react';                    // React
import { View, Text, Button, Platform, Alert } from 'react-native'; // UI
import { useIAP, withIAPContext } from 'react-native-iap';   // IAP hook (v12-style API)

// Product ID created in App Store Connect
const SKUS = ['com.myapp.premium_unlock'];

function PremiumScreen() {
  const {
    connected, products, getProducts, requestPurchase,
    currentPurchase, finishTransaction, getAvailablePurchases,
  } = useIAP();

  // Load products once StoreKit is connected
  useEffect(() => { if (connected) getProducts({ skus: SKUS }); }, [connected]);

  // When Apple confirms the purchase
  useEffect(() => {
    (async () => {
      if (!currentPurchase) return;                 // nothing to do
      // Verify on server here (recommended), then unlock
      await finishTransaction({ purchase: currentPurchase, isConsumable: false });
      Alert.alert('Unlocked', 'Premium activated');
    })();
  }, [currentPurchase]);

  // iOS-only screen text
  if (Platform.OS !== 'ios') return <Text>iOS only</Text>;

  return (
    <View style={{ padding: 20 }}>
      {products.map((p) => (
        <Button key={p.productId}
          title={`Unlock ${p.localizedPrice}`}
          // iOS: request by sku
          onPress={() => requestPurchase({ sku: p.productId })} />
      ))}
      {/* Apple REQUIRES a restore option */}
      <Button title="Restore Purchases" onPress={() => getAvailablePurchases()} />
    </View>
  );
}
export default withIAPContext(PremiumScreen);
```

## 💻 Code Example — Advanced

Entitlement store with restore + error handling:
```jsx
import { useEffect, useState, useCallback } from 'react';
import { Alert, Linking } from 'react-native';
import {
  initConnection, endConnection, getAvailablePurchases,
  purchaseUpdatedListener, purchaseErrorListener, finishTransaction,
} from 'react-native-iap';

// Returns { premium, restore, manage }
export function useIosPremium(verifyOnServer) {
  const [premium, setPremium] = useState(false);       // entitlement flag

  // Restore past purchases from Apple
  const restore = useCallback(async () => {
    try {
      const purchases = await getAvailablePurchases(); // list of owned items
      const owned = purchases.some(p => p.productId === 'com.myapp.premium_unlock');
      setPremium(owned);                                // update UI
      Alert.alert(owned ? 'Restored' : 'Nothing to restore');
    } catch (e) { Alert.alert('Restore failed', String(e)); }
  }, []);

  useEffect(() => {
    let a, b;
    (async () => {
      await initConnection();                           // connect to StoreKit
      a = purchaseUpdatedListener(async (purchase) => {
        try {
          // iOS: send transactionReceipt / transactionId to your server
          const ok = await verifyOnServer(purchase);    // server talks to Apple
          if (ok) { setPremium(true); }
          // ALWAYS finish, otherwise Apple re-delivers each launch
          await finishTransaction({ purchase, isConsumable: false });
        } catch (e) { console.warn('verify failed', e); }
      });
      b = purchaseErrorListener((e) => {
        if (e.code !== 'E_USER_CANCELLED') Alert.alert('Purchase error', e.message);
      });
    })();
    return () => { a?.remove(); b?.remove(); endConnection(); };
  }, [verifyOnServer]);

  // Deep link to iOS subscription management
  const manage = () => Linking.openURL('https://apps.apple.com/account/subscriptions');
  return { premium, restore, manage };
}
```
Not run here — StoreKit needs a real device/simulator with App Store Connect products and a sandbox account.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Framework | Play Billing | StoreKit 1/2 |
| Products | Play Console | App Store Connect |
| Restore button | Not mandatory (auto via Play) | MANDATORY (review rule) |
| Review of IAP | No separate review | IAP reviewed with app (screenshot needed) |
| Testing | License testers | Sandbox testers (Settings → Developer on device) |
| Pending finish | 3-day auto-refund | Re-delivery until finished |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo install react-native-iap
# plugins: ["react-native-iap"] in app.json, then dev build:
eas build --profile development --platform ios
```
CLI way:
```bash
npm install react-native-iap && cd ios && pod install && cd ..
# Xcode → Signing & Capabilities → + Capability → In-App Purchase
npx react-native run-ios
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** No Restore Purchases button
✅ **Correct:** Add it; Apple rejects apps without it.

❌ **Mistake 2:** Product stays "Missing Metadata" in App Store Connect so fetch returns empty
✅ **Correct:** Fill name, price, localization, review screenshot; agreements active.

❌ **Mistake 3:** Testing with real Apple ID
✅ **Correct:** Create Sandbox tester in App Store Connect → Users and Access.

❌ **Mistake 4:** Linking to external website for digital purchase
✅ **Correct:** Use IAP (external link entitlements exist only in specific regions — check Apple's current rules).

---

## 🧠 Tricky Interview Question
**Q:** `getProducts` returns an empty array on iOS even though the product exists. List causes.

**Answer:** (1) Paid Apps Agreement not active; (2) product status "Missing Metadata"/not ready; (3) wrong Product ID or bundle ID mismatch; (4) in-app purchase capability missing; (5) using simulator without StoreKit config / network issue; (6) products created minutes ago (propagation delay up to hours). Check each in this order.

---

## ⚫ Interview Questions + Answers

**Q1: Why does Apple demand Restore Purchases?**
A1: Users reinstall/switch devices; non-consumables and subscriptions must be recoverable.

**Q2: StoreKit 1 vs 2?**
A2: StoreKit 2 is Swift-async with signed JWS transactions and simpler verification; libraries wrap whichever they support — check library notes.

**Q3: How to verify?**
A3: Server calls App Store Server API (or validates JWS signature) — never trust client.

**Q4: How are IAPs reviewed?**
A4: First IAP must be submitted with a new app version; later ones can go with any version.

**Q5: Can Razorpay be used for a digital subscription on iOS?**
A5: Generally no — must use IAP (with narrow exceptions by region/program).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Selling digital goods/subscriptions to iOS users

❌ Avoid when:
- Physical goods/services (food delivery, cabs) — use normal gateways

---

## 📊 Visual Diagram
```
 App ─ getProducts ─► StoreKit ─► App Store Connect (product list)
 App ─ requestPurchase ─► Apple sheet (Face ID) ─► charge
 Apple ─► purchaseUpdatedListener ─► App ─► your server ─► Apple Server API
                                        └─► finishTransaction
 New phone ─► Restore Purchases ─► getAvailablePurchases
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| StoreKit | Apple's purchase framework | Apple का purchase framework |
| Sandbox | Fake payment test environment | नकली payment वाला test environment |
| Restore | Get old purchases back | पुरानी purchases वापस लाना |
| Paid Apps Agreement | Contract needed to sell | बेचने के लिए ज़रूरी contract |
| finishTransaction | Mark transaction done | Transaction पूरा चिह्नित करना |

---

## ⚡ 3-Line Summary
**English:**
1. iOS IAP uses StoreKit; products live in App Store Connect.
2. Verify server-side, always finish transactions, always offer Restore.
3. Test with Sandbox accounts; Apple reviews the IAP.

**Hindi:**
1. iOS IAP StoreKit से; products App Store Connect में।
2. Server पर verify, transaction finish, Restore button ज़रूर।
3. Sandbox accounts से test; Apple IAP को review करता है।

---

## ➡️ Next Topic
**271. Subscriptions Setup** — monthly/yearly plans, trials, grace period, renewals।
