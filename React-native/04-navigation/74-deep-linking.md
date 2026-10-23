# 74. Deep Linking
# हिंदी में: Deep Linking — URL से App Screen खोलना
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**Deep Linking** allows opening a specific screen in your app via a URL — either a custom scheme (`myapp://product/123`) or a universal/app link (`https://myapp.com/product/123`). When a user taps a link in WhatsApp, email, or browser, it opens directly to the relevant screen in your app instead of the home screen.

## 🔵 सरल परिभाषा (Hindi)
**Deep Linking** URL के through app में specific screen खोलने की capability है — custom scheme (`myapp://product/123`) या universal/app link (`https://myapp.com/product/123`)। User WhatsApp, email, या browser में link tap करे → app सीधे relevant screen पर खुले, home screen पर नहीं।

---

## 🔴 Problem it Solves
```
WITHOUT DEEP LINKING:
  WhatsApp: "Check this product: https://zomato.com/restaurants/123"
  User taps → Opens mobile browser → zomato.com website
  User must manually open Zomato app + search restaurant

WITH DEEP LINKING:
  User taps → Zomato app opens directly on Restaurant #123
  Seamless experience!

USE CASES:
  ✅ Promotional links: "50% off — tap to view deal" → Opens deal screen
  ✅ Order tracking: SMS "Your order is out" → Opens order tracking screen
  ✅ Email verification: "Verify email" button → App opens + auto-verifies
  ✅ Payment return: After bank redirect → App reopens on success screen
  ✅ Share product: "Share" button → Link opens product screen in app
  ✅ Push notification tap → Navigate to specific screen
```

---

## 🟢 How It Works — Step by Step

```
DEEP LINK TYPES:
──────────────────────────────────────────────────────
  1. Custom Scheme (URI Scheme):
     myapp://product/123
     myapp://cart
     myapp://profile/userId
     Simple to set up, works offline
     Limitation: only works if app is installed

  2. Universal Links (iOS) / App Links (Android):
     https://myapp.com/product/123
     If app installed → opens app directly
     If app NOT installed → opens website (fallback!)
     More seamless, but requires server configuration
     (AASA file for iOS, assetlinks.json for Android)

FLOW (Custom Scheme):
  App registers: "I handle myapp:// URLs" in native config
  User taps: myapp://product/123
  OS checks: which app handles myapp:// ?
  → Opens your app
  → App receives URL
  → React Navigation parsing: /product/123 → ProductDetail screen, id=123
  → Navigates directly to ProductDetail
```

---

## 🟡 Real World Example
**Swiggy order notification:** Backend sends push notification: "Your order is ready for pickup!" with data `{ url: 'swiggy://order/ORD-789' }`. User taps notification → Swiggy app opens → navigates directly to OrderTracking screen with orderId=ORD-789. Same link in WhatsApp works: friend shares `https://swiggy.com/order/track/ORD-789` → installed app opens directly, web browser as fallback.

---

## 💻 Code Example — Expo Setup

```json
// app.json — declare custom scheme
{
  "expo": {
    "name": "MyApp",
    "slug": "myapp",
    "scheme": "myapp",                // → myapp:// scheme
    "android": {
      "intentFilters": [              // App Links (https)
        {
          "action": "VIEW",
          "autoVerify": true,
          "data": [
            {
              "scheme": "https",
              "host": "*.myapp.com",
              "pathPrefix": "/"
            }
          ],
          "category": ["BROWSABLE", "DEFAULT"]
        }
      ]
    },
    "ios": {
      "associatedDomains": [          // Universal Links (https)
        "applinks:myapp.com",
        "applinks:www.myapp.com"
      ]
    }
  }
}
```

```tsx
// App.tsx — React Navigation + Deep Linking config
import React from 'react';
import { NavigationContainer, LinkingOptions } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

type RootStackParamList = {
  Home: undefined;
  ProductDetail: { productId: string };
  OrderTracking: { orderId: string };
  Profile: { userId: string };
  EmailVerify: { token: string };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

// LINKING CONFIGURATION — maps URLs to screens
const linking: LinkingOptions<RootStackParamList> = {
  prefixes: [
    'myapp://',                    // custom scheme
    'https://myapp.com',           // universal link
    'https://www.myapp.com',       // with www
  ],
  config: {
    screens: {
      Home: 'home',
      // myapp://product/123 → ProductDetail screen with productId='123'
      ProductDetail: 'product/:productId',

      // myapp://order/ORD-789 → OrderTracking with orderId='ORD-789'
      OrderTracking: 'order/:orderId',

      // myapp://profile/user-456 → Profile with userId='user-456'
      Profile: 'profile/:userId',

      // myapp://verify-email?token=abc123 → EmailVerify with token='abc123'
      EmailVerify: {
        path: 'verify-email',
        parse: {
          token: (token: string) => token,  // query param parsing
        },
      },
    },
  },
};

export default function App() {
  return (
    <NavigationContainer linking={linking}>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="ProductDetail" component={ProductDetailScreen} />
        <Stack.Screen name="OrderTracking" component={OrderTrackingScreen} />
        <Stack.Screen name="Profile" component={ProfileScreen} />
        <Stack.Screen name="EmailVerify" component={EmailVerifyScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

```tsx
// TESTING DEEP LINKS:
// Expo Go:
// expo go: myapp://product/123  (in Expo Go's "Enter URL" field)

// Development build / simulator:
// iOS Simulator:
// xcrun simctl openurl booted "myapp://product/123"

// Android Emulator:
// adb shell am start -W -a android.intent.action.VIEW -d "myapp://product/123"

// Or in terminal (development):
// npx uri-scheme open "myapp://product/123" --android
// npx uri-scheme open "myapp://product/123" --ios
```

```tsx
// HANDLING DEEP LINKS MANUALLY (for analytics, logging, etc.)
import { Linking } from 'react-native';
import { useEffect } from 'react';

function useDeepLinkTracking() {
  useEffect(() => {
    // App opened FROM a deep link (killed state)
    Linking.getInitialURL().then(url => {
      if (url) {
        console.log('App opened from deep link:', url);
        // Track in analytics
      }
    });

    // App was already open (background state) → link received
    const subscription = Linking.addEventListener('url', ({ url }) => {
      console.log('Deep link received while app open:', url);
    });

    return () => subscription.remove();
  }, []);
}
// React Navigation's `linking` prop handles the NAVIGATION automatically
// You only need manual Linking for analytics/logging
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Custom scheme | `intentFilters` in app.json | `scheme` in app.json |
| App Links (https) | `autoVerify: true` + `assetlinks.json` on server | Universal Links + `apple-app-site-association` on server |
| Test command | `adb shell am start -d "myapp://..."` | `xcrun simctl openurl booted "myapp://..."` |
| Back behavior | Back button returns to caller app | Swipe-back returns to caller app |

---

## 🟠 Expo vs CLI Difference

Expo way:
```json
// app.json: just add "scheme" and intentFilters/associatedDomains
// React Navigation handles the rest via linking prop
// No native code changes needed!
```

CLI way:
```xml
<!-- AndroidManifest.xml — add intent filter to MainActivity -->
<intent-filter android:autoVerify="true">
  <action android:name="android.intent.action.VIEW" />
  <category android:name="android.intent.category.DEFAULT" />
  <category android:name="android.intent.category.BROWSABLE" />
  <data android:scheme="myapp" />
  <data android:scheme="https" android:host="myapp.com" />
</intent-filter>
```

```xml
<!-- iOS Info.plist — add URL type -->
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLSchemes</key>
    <array><string>myapp</string></array>
  </dict>
</array>
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Not testing the killed state
```tsx
// App opens FROM a link (was completely closed)
// React Navigation handles this with `linking` prop automatically
// But: test manually! iOS/Android behave slightly differently
// Test: kill the app → run adb command → app should open on right screen
```

❌ **Mistake 2:** Missing fallback for Universal Links
```
If you use https:// App Links:
MUST have a real website at that URL as fallback
If app not installed → browser opens → should show web page (not 404)
Minimum: a download page ("Get the app") or the web version
```

❌ **Mistake 3:** Not handling optional URL params
```tsx
// If URL is: myapp://product/123 (id present)
// AND: myapp://products (no id — list view)
// ProductDetail must handle: route.params?.productId being undefined
// OR define separate screens for each pattern
```

---

## ⚫ Interview Questions + Answers

**Q1: What is deep linking and what are the two types?**
A1: Deep linking opens a specific screen in your app via a URL. (1) **Custom scheme** (`myapp://product/123`): app registers `myapp://` as its URL scheme — only works if app is installed. (2) **Universal Links (iOS) / App Links (Android)** (`https://myapp.com/product/123`): uses regular https URLs — if app installed, opens app; if not, opens website as fallback. Universal/App Links require a verification file on your server (`apple-app-site-association` for iOS, `assetlinks.json` for Android).

**Q2: How does React Navigation handle deep links?**
A2: React Navigation's `NavigationContainer` accepts a `linking` prop with `prefixes` (which URL schemes/domains to handle) and `config` (maps URL patterns to screen names and params). `'product/:productId'` maps `/product/123` to the ProductDetail screen with `{ productId: '123' }` as route params. React Navigation parses the URL and navigates automatically when the app is opened via a deep link.

**Q3: How do you test deep links during development?**
A3: iOS Simulator: `xcrun simctl openurl booted "myapp://product/123"`. Android Emulator: `adb shell am start -W -a android.intent.action.VIEW -d "myapp://product/123"`. Expo CLI: `npx uri-scheme open "myapp://product/123" --ios`. In Expo Go: use the "Enter URL manually" option. Always test the killed state (app fully closed when link is tapped) — this is where bugs often hide.

**Q4: What is the difference between `getInitialURL` and `Linking.addEventListener`?**
A4: `Linking.getInitialURL()` — called once on app startup, returns the URL that launched the app (if app was opened FROM a link while in killed state). `Linking.addEventListener('url', callback)` — fires when a link arrives while the app is already running (background/foreground state). React Navigation's `linking` prop handles both automatically. You only need to call these directly for analytics tracking or custom handling.

---

## ⚡ 3-Line Summary
**English:**
1. Deep linking opens specific app screens via URLs — custom scheme (`myapp://`) for simplicity, Universal/App Links (`https://`) for fallback to website when app isn't installed.
2. React Navigation: add `linking={{ prefixes: ['myapp://'], config: { screens: { ProductDetail: 'product/:productId' } } }}` to NavigationContainer — handles killed/background states automatically.
3. Test three states: app open (background), app in background (foreground), app killed (cold start from link) — each behaves differently.

**Hindi:**
1. Deep linking specific screens को URLs से खोलता है — custom scheme (`myapp://`) simple, Universal/App Links (`https://`) app install न होने पर website fallback।
2. React Navigation: NavigationContainer में `linking` prop add करो — killed/background states automatically handle।
3. तीन states test करो: app open, app background, app killed — तीनों अलग behave करते हैं।

---

## ➡️ Next Topic
**75. Auth Flow Navigation** — Conditional navigators based on login state।
