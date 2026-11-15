# 269. In-App Purchases (Android)
# हिंदी में: Android में In-App Purchases (Google Play Billing)
# Platform: Android ✅ | iOS ❌ (iOS = topic 270) | Android only
# Expo SDK 54 (React Native 0.81) — check current docs — APIs change between SDKs

---

## 🔵 Simple Definition (English)
**In-App Purchase (IAP)** lets users pay for digital items *inside your app* — coins, premium features, ad removal. On Android this is done through **Google Play Billing Library**: Google shows the payment sheet, charges the user, and tells your app the purchase succeeded. In React Native you use a library such as `react-native-iap` or RevenueCat — it needs a **development build / bare app** (not Expo Go).

## 🔵 सरल परिभाषा (Hindi)
**In-App Purchase (IAP)** से user app के *अंदर* digital चीज़ें खरीदता है — coins, premium features, ads हटाना। Android पर यह **Google Play Billing Library** से होता है: Google payment sheet दिखाता है, पैसे काटता है और app को बताता है कि purchase सफल हुआ। React Native में `react-native-iap` या RevenueCat इस्तेमाल होता है — **development build / bare app** चाहिए (Expo Go में नहीं चलता)।

---

## 🔴 Problem it Solves
```
BEFORE IAP:
❌ Collecting card details yourself = PCI compliance + fraud risk
❌ Users don't trust typing cards in small apps
❌ Google Play POLICY: digital goods in an app MUST use Play Billing
❌ Refunds, taxes, UPI/cards/carrier billing — you'd build everything
```

## 🔴 यह क्यों बना? (Hindi)
```
IAP से पहले:
❌ Card details खुद लेना = PCI compliance + fraud का risk
❌ छोटे app में card डालने पर users को भरोसा नहीं
❌ Google Play POLICY: app के digital सामान के लिए Play Billing ज़रूरी
❌ Refund, tax, UPI/cards — सब खुद बनाना पड़ता
Play Billing: Google सब संभालता है (15-30% commission पर)।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Play Console: create app, upload a build to at least internal testing
Step 2 → Monetize → Products → In-app products: create product id
         e.g. "coins_100" (type: consumable / non-consumable)
Step 3 → App: initConnection() to Play Billing
Step 4 → App: fetch product details by SKU (price shown in user's currency, e.g. ₹79)
Step 5 → App: requestPurchase(sku) → Google Pay sheet appears
Step 6 → User pays → purchase event arrives in app (purchaseUpdatedListener)
Step 7 → VERIFY on your backend with Google Play Developer API (purchaseToken)
Step 8 → Grant item, then finishTransaction (consume / acknowledge)
         ⚠️ Not acknowledged within 3 days → Google auto-refunds!
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Play Console में app बनाओ, internal testing में build upload
Step 2 → Monetize → In-app products: product id बनाओ ("coins_100")
Step 3 → App में initConnection() से Play Billing से connect
Step 4 → SKU से product details लाओ (user की currency में price, ₹79)
Step 5 → requestPurchase(sku) → Google payment sheet खुलती है
Step 6 → User pay करता है → purchaseUpdatedListener में event आता है
Step 7 → अपने BACKEND पर purchaseToken verify करो (Google Play Developer API)
Step 8 → Item दो, फिर finishTransaction (consume / acknowledge)
         ⚠️ 3 दिन में acknowledge नहीं किया → Google पैसे वापस कर देता है!
```

---

## 🟡 Real World Example
**Dream11 / Games24x7-style** apps and **Zomato Gold**-like memberships sell coins and passes. A game sells "100 coins for ₹79" (consumable — can buy again) and "Remove ads" (non-consumable — bought once). Google collects via UPI/cards/Play balance; developer gets ~85% (15% for small developers / subscriptions after year one, 30% otherwise — check current Play fee policy).

## 🟡 Real Example Hindi mein
**Dream11 जैसे games** और **Zomato Gold** जैसी memberships coins/passes बेचते हैं। Game "100 coins ₹79 में" (consumable — बार-बार खरीद सकते हैं) और "Remove ads" (non-consumable — एक बार) बेचता है। Google UPI/cards/Play balance से पैसे लेता है; developer को लगभग 85% मिलता है (Play की current fee policy देखो)।

---

## 💻 Code Example — Basic

Using `react-native-iap` hook API (v12-style; v13/v14 renamed some functions — check the library's current docs):
```jsx
import React, { useEffect } from 'react';           // React + effect hook
import { View, Text, Button, Alert, Platform } from 'react-native'; // UI
import { useIAP, withIAPContext } from 'react-native-iap'; // IAP hook + provider

// Product ids exactly as created in Play Console
const SKUS = ['coins_100'];

function Store() {
  // useIAP gives connection state, product list and helper functions
  const {
    connected, products, getProducts, requestPurchase,
    currentPurchase, finishTransaction,
  } = useIAP();

  // When connected to Play Billing, load product details
  useEffect(() => {
    if (connected) getProducts({ skus: SKUS }); // fetch price, title
  }, [connected]);

  // When a purchase arrives, grant item and finish it
  useEffect(() => {
    const complete = async () => {
      if (!currentPurchase) return;                 // nothing yet
      // TODO: send currentPurchase.purchaseToken to YOUR server for verification
      await finishTransaction({
        purchase: currentPurchase,
        isConsumable: true,                         // coins can be bought again
      });
      Alert.alert('Done', '100 coins added!');      // user feedback
    };
    complete();
  }, [currentPurchase]);

  return (
    <View style={{ padding: 20 }}>
      {/* Only Android in this topic */}
      {Platform.OS === 'android' && products.map((p) => (
        <View key={p.productId} style={{ marginBottom: 12 }}>
          <Text>{p.title} — {p.localizedPrice}</Text>
          <Button title="Buy"
            onPress={() => requestPurchase({ skus: [p.productId] })} />
        </View>
      ))}
    </View>
  );
}

// withIAPContext wraps the component so useIAP works
export default withIAPContext(Store);
```
`app.json` (Expo dev build) — add the plugin:
```json
{ "expo": { "plugins": ["react-native-iap"] } }
```

## 💻 Code Example — Advanced

Server-verified purchase with error handling (client + Node snippet). Pattern is real; exact function names depend on library version.
```jsx
import { useEffect, useRef, useState } from 'react';
import { Alert } from 'react-native';
import {
  initConnection, endConnection,
  purchaseUpdatedListener, purchaseErrorListener,
  finishTransaction, flushFailedPurchasesCachedAsPendingAndroid,
} from 'react-native-iap';

export function usePlayPurchases(userId) {
  const [busy, setBusy] = useState(false);       // disable buy button while processing
  const seen = useRef(new Set());                // avoid processing same token twice

  useEffect(() => {
    let updateSub, errorSub;
    (async () => {
      try {
        await initConnection();                  // connect to Play Billing
        // Clear stuck pending purchases (Android only API)
        await flushFailedPurchasesCachedAsPendingAndroid().catch(() => {});
      } catch (e) { Alert.alert('Billing not available', String(e)); }

      // Called whenever a purchase succeeds or is restored
      updateSub = purchaseUpdatedListener(async (purchase) => {
        const token = purchase.purchaseToken;
        if (!token || seen.current.has(token)) return; // duplicate guard
        seen.current.add(token);
        try {
          // 1) Verify on YOUR server (never trust the client!)
          const res = await fetch('https://api.example.com/iap/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ userId, sku: purchase.productId, token }),
          });
          if (!res.ok) throw new Error('Verification failed');
          // 2) Only after server granted item: consume/acknowledge
          await finishTransaction({ purchase, isConsumable: true });
        } catch (e) {
          seen.current.delete(token);            // allow retry later
          Alert.alert('Purchase issue', 'We will retry automatically.');
        } finally { setBusy(false); }
      });

      // User cancelled or payment error
      errorSub = purchaseErrorListener((err) => {
        setBusy(false);
        if (err.code !== 'E_USER_CANCELLED') Alert.alert('Payment error', err.message);
      });
    })();
    // Cleanup listeners + connection
    return () => { updateSub?.remove(); errorSub?.remove(); endConnection(); };
  }, [userId]);

  return { busy, setBusy };
}
```
Backend idea (Node, `googleapis`): call `androidpublisher.purchases.products.get({packageName, productId, token})`, check `purchaseState === 0`, store the token to prevent replay, grant coins. Not run here — needs Play Console.

---

## 📱 Android vs iOS Difference
| Feature | Android (Play Billing) | iOS (StoreKit) |
|---------|------------------------|----------------|
| Product setup | Play Console → In-app products | App Store Connect → In-App Purchases |
| Must finish? | Acknowledge within 3 days or auto-refund | `finishTransaction` or it re-delivers |
| Test | License testers + internal testing track | Sandbox testers + TestFlight |
| Verification | Purchase token + Play Developer API | App Store Server API / receipt |
| Fee | 15% / 30% | 15% / 30% |
| Restore | `getAvailablePurchases` (queries Play) | Restore button mandatory |

---

## 🟠 Expo vs CLI Difference
Expo way (development build, not Expo Go):
```bash
npx expo install react-native-iap expo-build-properties
# add "react-native-iap" to plugins in app.json, then:
eas build --profile development --platform android
```
CLI way (bare):
```bash
npm install react-native-iap
# Autolinking handles native part. Ensure android/app/build.gradle
# has missingDimensionStrategy 'store', 'play' if the library docs ask for it.
npx react-native run-android
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Testing with Expo Go or an app NOT uploaded to Play
✅ **Correct:** Upload at least to internal testing; install from Play link with a license-tester account.

❌ **Mistake 2:** Trusting the client ("purchase succeeded" → unlock)
✅ **Correct:** Verify token server-side with Google API.

❌ **Mistake 3:** Not acknowledging / consuming
✅ **Correct:** Call `finishTransaction` (consumable → consume, non-consumable → acknowledge).

❌ **Mistake 4:** Different `applicationId` or signing key than the Play build
✅ **Correct:** Test with a build signed with the upload/app-signing configuration Play expects.

---

## 🧠 Tricky Interview Question
**Q:** A user buys "100 coins" but kills the app right after paying. Next launch coins are missing, yet the user was charged. How do you prevent this?

**Answer:** The purchase is stored by Play as *pending acknowledgement*. On every launch, `initConnection()` and the purchase listener re-deliver unfinished purchases (or call `getAvailablePurchases`). Your handler must be **idempotent**: verify the token on the server, credit coins once (store token), then consume. Never rely on in-memory state. If you never finish within 3 days, Google refunds the user.

---

## ⚫ Interview Questions + Answers

**Q1: Consumable vs non-consumable?**
A1: Consumable (coins) can be bought repeatedly and must be consumed; non-consumable (remove ads) is bought once and acknowledged.

**Q2: Why verify on server?**
A2: Client can be hacked/rooted; fake purchases are common. Server calls Google API with the token.

**Q3: Can we use Razorpay/UPI for digital goods in an Android app?**
A3: Google policy requires Play Billing for in-app digital goods in apps distributed via Play (with limited regional exceptions/programs — check current policy). Physical goods/services (Zomato order) can use other gateways.

**Q4: Does it work in Expo Go?**
A4: No — native module; use a dev build.

**Q5: Where do I see test purchases?**
A5: Play Console → Setup → License testing adds tester Gmail accounts; they are not charged.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Selling digital goods/features in a Play-distributed app
- Subscriptions (see 271)

❌ Avoid when:
- Selling physical goods or real-world services (use Razorpay/Stripe)
- You only need cross-platform subscription logic without backend (use RevenueCat — 273)

---

## 📊 Visual Diagram
```
 App ──requestPurchase(sku)──► Play Billing ──► Google pay sheet
  ▲                                                 │ user pays
  │ purchaseUpdatedListener(purchase+token)         ▼
  └──────────────────────────────────────────  Google charges
  │
  ├─ send token ─► Your server ─► Google Play Developer API (verify)
  │                     │ grant coins
  └─ finishTransaction (consume/acknowledge ≤ 3 days)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SKU / productId | Unique product identifier | Product की unique id |
| Consumable | Can be bought again | बार-बार खरीदने लायक |
| Acknowledge | Tell Google item was delivered | Google को बताना कि item मिल गया |
| purchaseToken | Proof of purchase | Purchase का सबूत |
| License tester | Test account, not charged | Test account, पैसे नहीं कटते |

---

## ⚡ 3-Line Summary
**English:**
1. Android IAP = Google Play Billing; products are defined in Play Console.
2. Flow: connect, fetch products, request purchase, verify on server, finish.
3. Not acknowledging within 3 days means an automatic refund.

**Hindi:**
1. Android IAP = Google Play Billing; products Play Console में बनते हैं।
2. Flow: connect, products लाओ, purchase माँगो, server पर verify, finish।
3. 3 दिन में acknowledge नहीं किया तो automatic refund।

---

## ➡️ Next Topic
**270. In-App Purchases (iOS)** — StoreKit, sandbox testers और Apple की rules।
