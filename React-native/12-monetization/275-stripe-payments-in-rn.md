# 275. Stripe Payments in RN
# हिंदी में: React Native में Stripe Payments
# Platform: Android ✅ | iOS ✅ | Both ✅
# Expo SDK 54 (React Native 0.81) — check current docs — APIs change between SDKs

---

## 🔵 Simple Definition (English)
**Stripe** is a payment gateway. In React Native you use **`@stripe/stripe-react-native`**: your **server** creates a **PaymentIntent** (the amount and currency), the app receives its `client_secret`, and Stripe's prebuilt **Payment Sheet** collects card details securely and confirms payment. Apple/Google rules: use Stripe for **physical goods and real-world services** — digital goods inside the app must use IAP (269-271).

## 🔵 सरल परिभाषा (Hindi)
**Stripe** एक payment gateway है। React Native में **`@stripe/stripe-react-native`** use होता है: आपका **server** **PaymentIntent** बनाता है (amount और currency), app को उसका `client_secret` मिलता है और Stripe की तैयार **Payment Sheet** card details सुरक्षित तरीके से लेकर payment confirm करती है। Apple/Google नियम: Stripe **physical सामान और real-world services** के लिए; app के अंदर digital सामान के लिए IAP (269-271)।

---

## 🔴 Problem it Solves
```
❌ Handling raw card numbers yourself = PCI-DSS nightmare
❌ 3D Secure / SCA / bank redirects are complex
✅ Payment Sheet handles card UI, validation, 3DS, Apple Pay / Google Pay
✅ Card data goes directly to Stripe, never touches your server
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ Card numbers खुद संभालना = PCI-DSS की बड़ी मुसीबत
❌ 3D Secure / SCA / bank redirect जटिल
✅ Payment Sheet card UI, validation, 3DS, Apple Pay / Google Pay संभालती है
✅ Card data सीधे Stripe को जाता है, आपके server को नहीं
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Stripe Dashboard: get Publishable key (pk_...) and Secret key (sk_...)
Step 2 → Backend endpoint /payment-sheet (uses SECRET key):
         - create/get Customer
         - create Ephemeral Key
         - create PaymentIntent (amount, currency) → client_secret
Step 3 → App: wrap in <StripeProvider publishableKey=...>
Step 4 → App: fetch the 3 values from your backend
Step 5 → initPaymentSheet({ paymentIntentClientSecret, customerId, customerEphemeralKeySecret, merchantDisplayName })
Step 6 → presentPaymentSheet() → user enters card → Stripe confirms
Step 7 → Result: { error } or success
Step 8 → Do NOT trust the app result alone — fulfil order from Stripe webhook
         (payment_intent.succeeded) on your server
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Stripe Dashboard से Publishable key (pk_) और Secret key (sk_)
Step 2 → Backend endpoint /payment-sheet (SECRET key से): Customer, Ephemeral Key, PaymentIntent → client_secret
Step 3 → App में <StripeProvider publishableKey=...>
Step 4 → Backend से 3 values लाओ
Step 5 → initPaymentSheet({...})
Step 6 → presentPaymentSheet() → user card भरता है → Stripe confirm करता है
Step 7 → नतीजा: { error } या success
Step 8 → सिर्फ app के result पर भरोसा मत करो — order Stripe webhook से fulfil करो
```

---

## 🟡 Real World Example
A cross-border fashion store or a **Cult.fit**-style booking app for a class (a real-world service) takes card payment via Stripe. Note for India: RBI rules (e-mandates, card tokenisation) and UPI make **Razorpay / Cashfree / PayU** popular for domestic payments; Stripe is common for international customers — check current Stripe India availability.

## 🟡 Real Example Hindi mein
Cross-border fashion store या **Cult.fit** जैसे class booking app (real-world service) में card payment Stripe से लेते हैं। भारत में RBI नियमों (e-mandate, card tokenisation) और UPI की वजह से घरेलू payments के लिए **Razorpay / Cashfree / PayU** ज़्यादा चलते हैं; Stripe international customers के लिए — Stripe India की current availability देखो।

---

## 💻 Code Example — Basic

App side (client):
```jsx
import React, { useEffect, useState } from 'react';                // React
import { View, Button, Alert } from 'react-native';                // UI
import { StripeProvider, useStripe } from '@stripe/stripe-react-native'; // Stripe SDK

const API = 'https://api.example.com';                             // your backend

function CheckoutButton() {
  const { initPaymentSheet, presentPaymentSheet } = useStripe();   // sheet functions
  const [ready, setReady] = useState(false);                       // sheet initialised?

  // Ask backend to create the PaymentIntent
  const setup = async () => {
    const res = await fetch(`${API}/payment-sheet`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount: 49900, currency: 'inr' }),    // ₹499 in paise
    });
    const { paymentIntent, ephemeralKey, customer } = await res.json();
    // Configure the sheet
    const { error } = await initPaymentSheet({
      merchantDisplayName: 'Demo Store',                           // shown in sheet
      customerId: customer,                                        // saved cards
      customerEphemeralKeySecret: ephemeralKey,                    // short-lived key
      paymentIntentClientSecret: paymentIntent,                    // what to pay
      allowsDelayedPaymentMethods: false,                          // card only now
    });
    if (error) Alert.alert('Setup error', error.message);          // show error
    else setReady(true);                                           // enable button
  };

  useEffect(() => { setup().catch((e) => Alert.alert('Network', String(e))); }, []);

  const pay = async () => {
    const { error } = await presentPaymentSheet();                 // show Stripe UI
    if (error) {
      // 'Canceled' = user closed the sheet — not a real failure
      if (error.code !== 'Canceled') Alert.alert('Payment failed', error.message);
    } else {
      Alert.alert('Success', 'Payment confirmed!');                // show success
    }
  };

  return <Button title="Pay ₹499" disabled={!ready} onPress={pay} />;
}

export default function App() {
  return (
    // Publishable key is safe in the app (pk_test_... for testing)
    <StripeProvider publishableKey="pk_test_XXXX" merchantIdentifier="merchant.com.example">
      <View style={{ flex: 1, justifyContent: 'center', padding: 24 }}>
        <CheckoutButton />
      </View>
    </StripeProvider>
  );
}
```

## 💻 Code Example — Advanced

Backend (Node/Express) with idempotency + webhook; plus client hook with retry:
```js
// server.js — uses SECRET key (never in the app)
const express = require('express');
const Stripe = require('stripe');
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);   // sk_test_...
const app = express();

// JSON for normal routes
app.use('/payment-sheet', express.json());

app.post('/payment-sheet', async (req, res) => {
  try {
    // NEVER trust amount from the client: compute from your DB/cart
    const amount = await getCartTotalPaise(req.body.cartId);
    const customer = await stripe.customers.create();                    // or reuse saved id
    const ephemeralKey = await stripe.ephemeralKeys.create(
      { customer: customer.id },
      { apiVersion: '2024-06-20' }          // must match the SDK-supported version (check docs)
    );
    const pi = await stripe.paymentIntents.create(
      { amount, currency: 'inr', customer: customer.id,
        automatic_payment_methods: { enabled: true } },
      { idempotencyKey: `order-${req.body.cartId}` }   // retry-safe
    );
    res.json({ paymentIntent: pi.client_secret, ephemeralKey: ephemeralKey.secret, customer: customer.id });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// Webhook: raw body needed for signature check
app.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  let event;
  try {
    event = stripe.webhooks.constructEvent(
      req.body, req.headers['stripe-signature'], process.env.STRIPE_WEBHOOK_SECRET);
  } catch { return res.status(400).send('bad signature'); }
  if (event.type === 'payment_intent.succeeded') {
    await markOrderPaid(event.data.object.id);          // fulfil ONLY here
  }
  res.json({ received: true });
});
app.listen(3000);
```
Expo config: `["@stripe/stripe-react-native", { "merchantIdentifier": "merchant.com.example", "enableGooglePay": true }]` in `plugins`; use `returnURL`/`urlScheme` for redirect-based methods. Not run here — needs Stripe keys and a device. The API version string is an example; use the one your Stripe account/SDK documents.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Wallet | Google Pay (`googlePay` option in initPaymentSheet) | Apple Pay (needs merchantIdentifier + Apple Pay capability) |
| Setup | Plugin `enableGooglePay` | Merchant ID + certificate in Apple Developer |
| Redirect return | Deep link scheme | URL scheme / universal link |
| Test cards | 4242 4242 4242 4242 | same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo install @stripe/stripe-react-native
# add config plugin in app.json; works in dev build (Expo Go supports Stripe too, with limits — check docs)
```
CLI way:
```bash
npm i @stripe/stripe-react-native && cd ios && pod install
# Android: minSdk/compileSdk per README; theme must be AppCompat (Theme.AppCompat)
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Secret key in the app
✅ **Correct:** Secret key only on the server.

❌ **Mistake 2:** Trusting amount from client
✅ **Correct:** Compute price on the server.

❌ **Mistake 3:** Marking order paid when `presentPaymentSheet` returns no error
✅ **Correct:** Wait for webhook `payment_intent.succeeded`.

❌ **Mistake 4:** Using Stripe for in-app digital goods on iOS/Android
✅ **Correct:** Use IAP for digital content.

---

## 🧠 Tricky Interview Question
**Q:** User paid successfully but the app crashed before showing success. Order never created. How should the system avoid this?

**Answer:** Order fulfilment must not depend on the client. The Stripe webhook (`payment_intent.succeeded`) reaches your server independent of the app; it marks the order paid. On next launch, the app fetches order status from the server. Add idempotency keys so retries don't double-charge.

---

## ⚫ Interview Questions + Answers

**Q1: PaymentIntent?**
A1: Stripe object tracking one payment lifecycle; its `client_secret` lets the client confirm it.

**Q2: Why an ephemeral key?**
A2: Gives the app temporary scoped access to a customer's saved payment methods.

**Q3: Publishable vs secret key?**
A3: Publishable = client-safe; secret = server only.

**Q4: How is 3D Secure handled?**
A4: Payment Sheet presents authentication automatically.

**Q5: Razorpay vs Stripe in India?**
A5: Razorpay supports UPI, netbanking, wallets natively; Stripe is better for international cards — pick by audience.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Physical goods, bookings, donations, marketplace

❌ Avoid when:
- Selling digital content inside the app (IAP required)
- UPI-first domestic audience (consider Razorpay)

---

## 📊 Visual Diagram
```
 App ─ POST /payment-sheet ─► Your server ─(secret key)─► Stripe API
  ▲ client_secret, ephemeralKey, customer ◄─────────────┘
  │ initPaymentSheet + presentPaymentSheet ─► Stripe (card data direct)
  │
 Stripe ─ webhook payment_intent.succeeded ─► Your server ─► order PAID
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| PaymentIntent | One payment record | एक payment का record |
| client_secret | Token for client to confirm | Client के लिए confirm token |
| Payment Sheet | Prebuilt payment UI | तैयार payment UI |
| Webhook | Server-to-server event | Server-से-server event |
| Idempotency key | Prevents duplicate charge | दोहरे charge से बचाव |

---

## ⚡ 3-Line Summary
**English:**
1. Server creates PaymentIntent; app shows Stripe Payment Sheet.
2. Secret key stays on server; fulfil orders via webhook.
3. Stripe for physical goods/services; IAP for digital goods.

**Hindi:**
1. Server PaymentIntent बनाता है; app Stripe Payment Sheet दिखाता है।
2. Secret key server पर; order webhook से fulfil।
3. Physical सामान/services के लिए Stripe; digital के लिए IAP।

---

## ➡️ Next Topic
**276/277 — Interview Problems** (OTP, Infinite Scroll) के बाद **278. Build Bottom Sheet**।
