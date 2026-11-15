# 189. React Native + Stripe Payments
# हिंदी में: React Native में Stripe से Payment
# Platform: Both ✅ (Android ✅ | iOS ✅) — Expo Go ❌ (custom dev build चाहिए)

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs). Package: `@stripe/stripe-react-native` (Expo में `npx expo install @stripe/stripe-react-native`, config plugin `@stripe/stripe-react-native`)। भारत में Stripe account/INR support की शर्तें बदलती रहती हैं — Stripe docs देखो; Indian apps में अक्सर Razorpay/UPI use होता है।

---

## 🔵 Simple Definition (English)
**Stripe** is a payment platform. In React Native you use `@stripe/stripe-react-native`: the **server** creates a PaymentIntent using your **secret key**, and the app shows Stripe's **PaymentSheet** (prebuilt secure UI) using the client secret and **publishable key**. Card data never touches your server — that keeps you out of heavy PCI scope.

## 🔵 सरल परिभाषा (Hindi)
**Stripe** एक payment platform है। RN में `@stripe/stripe-react-native` use होता है: **server** आपकी **secret key** से PaymentIntent बनाता है, और app उसका client secret + **publishable key** लेकर Stripe की तैयार **PaymentSheet** (सुरक्षित UI) दिखाता है। Card का data आपके server को छूता ही नहीं — PCI बोझ कम रहता है।

---

## 🔴 Problem it Solves
```
❌ Card details खुद collect/store करना = PCI-DSS compliance, बहुत जोखिम
❌ 3D Secure / SCA, Apple Pay, Google Pay खुद integrate करना कठिन
❌ Secret key app में डालना = key leak, कोई भी charge कर देगा
Stripe SDK:
  ✅ Card UI + validation + 3DS + wallets तैयार
  ✅ Card data सीधे Stripe को
  ✅ Server आपका payment amount तय करता है
```

## 🔴 यह क्यों बना? (Hindi)
```
Card data संभालना कानूनी और सुरक्षा के हिसाब से भारी है।
Stripe सब संभालता है, आप सिर्फ intent बनाते हैं और sheet दिखाते हैं।
Secret key हमेशा server पर, app में सिर्फ publishable key।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Stripe dashboard से publishable key (pk_...) और secret key (sk_...)
Step 2 → App: <StripeProvider publishableKey="pk_test_..."> से wrap
Step 3 → App → आपका server: "order #123 का payment बनाओ" (amount server तय करे)
Step 4 → Server: stripe.paymentIntents.create({amount, currency}) → client_secret लौटाए
Step 5 → App: initPaymentSheet({ paymentIntentClientSecret, merchantDisplayName })
Step 6 → App: presentPaymentSheet() → user card/Google Pay डालता है, 3DS होता है
Step 7 → Result: { error } या success
Step 8 → Server webhook (payment_intent.succeeded) से order confirm — app के result पर भरोसा मत करो
```

## 🟢 कैसे काम करता है? (Hindi)
```
Server intent बनाता है → client secret app को देता है।
App PaymentSheet खोलता है; user pay करता है।
असली confirmation webhook से — order तभी "paid" करो।
```

---

## 🟡 Real World Example
**Global apps (जैसे Uber/Airbnb style)** में checkout पर Stripe PaymentSheet आती है। भारतीय context में: **Zomato/Swiggy/Paytm** अपने payment gateways/UPI (Razorpay, PayU, in-house) use करते हैं; पर अगर कोई Indian startup international customers को SaaS/subscription बेचे तो Stripe use करता है। Flow वही: server intent → app sheet → webhook।

## 🟡 Real Example Hindi mein
Indian apps अक्सर UPI/Razorpay use करते हैं, पर international payments के लिए Stripe। हर जगह pattern एक: server intent बनाए, app sheet दिखाए, webhook से order confirm।

---

## 💻 Code Example — Basic
```jsx
// ---------- App.jsx ----------
import React from 'react';                                      // React
import { StripeProvider } from '@stripe/stripe-react-native';   // Stripe provider
import CheckoutScreen from './CheckoutScreen';                  // screen

export default function App() {
  return (
    // publishableKey सिर्फ pk_... (public)। secret key (sk_...) कभी app में नहीं
    <StripeProvider
      publishableKey="pk_test_REPLACE_ME"                       // test key
      merchantIdentifier="merchant.com.example.app"             // Apple Pay के लिए (iOS)
      urlScheme="myapp"                                         // redirect-based payment methods के लिए
    >
      <CheckoutScreen />
    </StripeProvider>
  );
}

// ---------- CheckoutScreen.jsx ----------
import React, { useState } from 'react';
import { View, Button, Alert } from 'react-native';
import { useStripe } from '@stripe/stripe-react-native';        // hook

const API = 'https://your-server.com';                          // आपका backend

export default function CheckoutScreen() {
  const { initPaymentSheet, presentPaymentSheet } = useStripe(); // sheet functions
  const [loading, setLoading] = useState(false);                // button disable

  async function pay() {
    setLoading(true);                                           // start
    try {
      // 1) Server से intent माँगो (amount server पर तय होता है, यहाँ सिर्फ order id)
      const res = await fetch(`${API}/create-payment-intent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ orderId: 'order_123' }),
      });
      const { clientSecret } = await res.json();                // PaymentIntent secret

      // 2) Sheet initialise
      const init = await initPaymentSheet({
        paymentIntentClientSecret: clientSecret,                // intent
        merchantDisplayName: 'My Shop',                         // sheet पर नाम
      });
      if (init.error) throw new Error(init.error.message);      // init failed

      // 3) Sheet दिखाओ
      const result = await presentPaymentSheet();
      if (result.error) {
        // user ने cancel किया (code 'Canceled') या card fail
        if (result.error.code !== 'Canceled') Alert.alert('Payment failed', result.error.message);
        return;                                                 // आगे नहीं
      }
      Alert.alert('Success', 'Payment received! Order confirm हो रहा है.'); // webhook final
    } catch (e) {
      Alert.alert('Error', e.message);                          // network etc.
    } finally {
      setLoading(false);                                        // हमेशा बंद
    }
  }

  return <View style={{ padding: 24 }}><Button title="Pay ₹499" onPress={pay} disabled={loading} /></View>;
}
```

## 💻 Code Example — Advanced
```jsx
// ---------- Node/Express server (server.js) — secret key सिर्फ यहाँ ----------
const express = require('express');                             // web server
const Stripe = require('stripe');                               // Stripe Node SDK
const stripe = Stripe(process.env.STRIPE_SECRET_KEY);           // sk_... env से
const app = express();

// webhook को raw body चाहिए (signature verify के लिए) — json parser से पहले
app.post('/webhook', express.raw({ type: 'application/json' }), (req, res) => {
  let event;
  try {
    event = stripe.webhooks.constructEvent(                     // signature verify
      req.body, req.headers['stripe-signature'], process.env.STRIPE_WEBHOOK_SECRET);
  } catch (err) { return res.status(400).send(`Webhook Error: ${err.message}`); }

  if (event.type === 'payment_intent.succeeded') {
    const pi = event.data.object;                               // PaymentIntent
    // DB में order paid mark करो (idempotent रखो: दो बार आ सकता है)
    console.log('Paid order', pi.metadata.orderId);
  }
  res.json({ received: true });                                 // 200 जल्दी दो
});

app.use(express.json());                                        // बाकी routes के लिए JSON

app.post('/create-payment-intent', async (req, res) => {
  try {
    const order = await getOrder(req.body.orderId);             // DB से असली price (client पर भरोसा नहीं)
    const intent = await stripe.paymentIntents.create({
      amount: order.totalInPaise,                               // smallest unit (paise/cents)
      currency: 'inr',                                          // currency
      automatic_payment_methods: { enabled: true },             // dashboard में enabled methods
      metadata: { orderId: order.id },                          // reconcile के लिए
    }, { idempotencyKey: `order-${order.id}` });                // duplicate charge से बचाव
    res.json({ clientSecret: intent.client_secret });
  } catch (e) { res.status(500).json({ error: 'server_error' }); }
});

app.listen(3000);
// ---------- app.json (Expo) ----------
// "plugins": [["@stripe/stripe-react-native", { "merchantIdentifier": "merchant.com.example.app" }]]
// Not run here — needs Stripe keys, server, and device/dev build.
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Wallet | Google Pay (`googlePay` config in initPaymentSheet) | Apple Pay (merchantIdentifier + Apple capability) |
| Setup | Google Pay test/prod merchant setting | Apple Developer में Merchant ID + certificate |
| minSdk/Deployment | Android minSdk (SDK docs देखो) | iOS deployment target (SDK docs देखो) |
| Redirect payment | `urlScheme` / intent filter | URL scheme in Info.plist |
| Simulator testing | Emulator OK (Google Pay limited) | Simulator पर Apple Pay सीमित, real device बेहतर |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install @stripe/stripe-react-native
// app.json plugins में Stripe plugin जोड़ो
// Expo Go ❌ — npx expo prebuild / EAS Build development build से चलाओ
```
CLI way:
```jsx
// npm i @stripe/stripe-react-native
// iOS: cd ios && pod install ; Apple Pay के लिए Xcode capability
// Android: autolinking; MainActivity/theme AppCompat requirements Stripe docs से
//         (activity must extend FragmentActivity — RN default OK)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Secret key (sk_) app में डालना
✅ Correct: सिर्फ server पर; app में pk_

❌ Mistake 2: Amount client से भेजना ("amount: 1")
✅ Correct: Server DB से amount निकाले

❌ Mistake 3: `presentPaymentSheet` success पर ही order "paid" कर देना
✅ Correct: Webhook `payment_intent.succeeded`

❌ Mistake 4: Amount को rupees में भेजना (499)
✅ Correct: Smallest unit (paise) → 49900

❌ Mistake 5: Cancel को error की तरह दिखाना
✅ Correct: `error.code === 'Canceled'` पर चुप रहो

❌ Mistake 6: Live key से test card
✅ Correct: Test mode में `4242 4242 4242 4242`

---

## 🧠 Tricky Interview Question
User ने payment किया, sheet ने success दिया, पर app बंद हो गया (crash) इससे पहले server को बताने का मौका मिला। Order का क्या होगा?

Answer: Webhook की वजह से order फिर भी confirm होगा — Stripe सीधे server को `payment_intent.succeeded` भेजता है, app पर निर्भर नहीं। इसीलिए "client success = paid" नहीं मानते। Edge case: webhook delay — app खुलने पर server से order status poll करो। Webhook handler idempotent रखो क्योंकि Stripe retry कर सकता है।

---

## ⚫ Interview Questions + Answers
Q1: PaymentIntent क्या है?
A1: Stripe object जो एक payment का lifecycle track करता है (created → requires_payment_method → processing → succeeded)। Client secret से app उसे confirm करता है।

Q2: Publishable key और secret key में फर्क?
A2: Publishable (pk_) public है, app में; secret (sk_) server पर, charge बनाने की शक्ति।

Q3: PaymentSheet vs CardField?
A3: PaymentSheet पूरा prebuilt flow (card, wallets, saved methods)। CardField सिर्फ card input, UI और confirmPayment खुद संभालना।

Q4: 3D Secure / SCA कैसे?
A4: SDK अपने आप authentication screen दिखाता है; automatic_payment_methods और PaymentIntent से।

Q5: Subscription के लिए?
A5: Server पर Customer + Subscription/ Checkout; app में SetupIntent से card save; Ephemeral key + customerId sheet को दो।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- International cards/wallets, subscriptions, marketplaces
- Fast, compliant checkout चाहिए

❌ Avoid when:
- सिर्फ भारतीय users + UPI-first (Razorpay/Cashfree/PhonePe PG ज़्यादा उपयुक्त)
- Digital goods/in-app content जहाँ Apple/Google IAP अनिवार्य है — store rules देखो

---

## 📊 Visual Diagram
```
  App ──(orderId)──► Your Server ──(sk_)──► Stripe API
   ▲                      │                      │
   │◄── clientSecret ─────┘◄── PaymentIntent ────┘
   │
   │ initPaymentSheet + presentPaymentSheet (pk_) ──► Stripe (card data सीधे)
   │
   └─ result (UI)           Stripe ──webhook──► Your Server → order = paid
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| PaymentIntent | One payment's record | एक payment का object |
| Client secret | Token app uses for intent | Intent का गुप्त token |
| PaymentSheet | Prebuilt payment UI | तैयार payment screen |
| Webhook | Server callback from Stripe | Stripe का server को संदेश |
| PCI-DSS | Card data security standard | Card सुरक्षा मानक |
| Idempotency key | Prevent duplicate charge | दोहरे charge से बचाव |

---

## ⚡ 3-Line Summary
English: Server creates a PaymentIntent with the secret key; app shows PaymentSheet with the publishable key.
Never trust the client for amount or success; confirm via webhook.
Needs a dev build (not Expo Go).

Hindi: Server secret key से PaymentIntent बनाता है; app publishable key से PaymentSheet दिखाता है।
Amount और success के लिए client पर भरोसा नहीं; webhook से confirm।
Dev build चाहिए (Expo Go नहीं)।

---

## ➡️ Next Topic
**190. React Native + Firebase Complete** — Auth, Firestore, Storage, Messaging सब एक जगह।

---
