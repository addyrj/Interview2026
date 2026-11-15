# 188. React Native + WebView
# हिंदी में: React Native में WebView
# Platform: Both ✅ (Android ✅ | iOS ✅) — Web ⚠️ (limited, iframe workaround)

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs). Package: `react-native-webview` — Expo में `npx expo install react-native-webview` (Expo Go में bundled है)।

---

## 🔵 Simple Definition (English)
A **WebView** is a component that shows a web page (or local HTML) inside your native app, using the system browser engine (Android System WebView / iOS WKWebView). JS in the page and RN can talk through `postMessage` and `injectedJavaScript`.

## 🔵 सरल परिभाषा (Hindi)
**WebView** एक component है जो आपके native app के अंदर web page (या local HTML) दिखाता है — system browser engine (Android System WebView / iOS WKWebView) से। Page का JS और RN आपस में `postMessage` और `injectedJavaScript` से बात करते हैं।

---

## 🔴 Problem it Solves
```
❌ हर चीज़ native में दोबारा बनाना (T&C, Help Center, Payment gateway page)
❌ Web team का बना content app में चाहिए, store update के बिना बदलना हो
❌ 3rd-party login/payment page (OAuth, 3D Secure) दिखाना
WebView:
  ✅ Existing web content reuse
  ✅ Web update = app update नहीं
  ⚠️ पर native जितना smooth/secure नहीं
```

## 🔴 यह क्यों बना? (Hindi)
```
हर page native में बनाना महँगा है।
Help pages, payment pages web पर पहले से होते हैं।
WebView से वही app के अंदर दिखा देते हैं।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install react-native-webview
Step 2 → <WebView source={{ uri: 'https://...' }} /> (flex:1 container में)
Step 3 → onLoadStart/onLoadEnd/onError से loading और error handle करो
Step 4 → onShouldStartLoadWithRequest से URL allow/block (security)
Step 5 → injectedJavaScript से page में JS चलाओ
Step 6 → Page से RN को: window.ReactNativeWebView.postMessage(string)
Step 7 → RN में onMessage={e => e.nativeEvent.data}
Step 8 → RN से page को: ref.current.postMessage / injectJavaScript
Step 9 → Back: onNavigationStateChange में canGoBack, ref.goBack()
```

## 🟢 कैसे काम करता है? (Hindi)
```
WebView native browser view बनाता है।
JS bridge: page → RN = postMessage, RN → page = injectJavaScript।
सिर्फ string message जाते हैं — object के लिए JSON.stringify करो।
```

---

## 🟡 Real World Example
**Paytm/PhonePe** पर कई bank/3D-Secure OTP pages WebView में खुलते हैं — payment पूरा होते ही page redirect करता है `myapp://success` और app उसे पकड़कर WebView बंद कर देता है। **Zomato/Swiggy** के Help/FAQ और Terms pages WebView हैं। **Razorpay checkout** का web flow भी इसी तरह काम कर सकता है।

## 🟡 Real Example Hindi mein
Paytm में bank का OTP page WebView में खुलता है; payment होते ही redirect URL पकड़कर app WebView बंद कर देता है। Swiggy का Help page भी WebView से।

---

## 💻 Code Example — Basic
```jsx
import React from 'react';                                   // React
import { SafeAreaView, StyleSheet } from 'react-native';     // layout
import { WebView } from 'react-native-webview';              // WebView component

export default function HelpScreen() {
  return (
    <SafeAreaView style={styles.container}>                  {/* container flex:1 ज़रूरी */}
      <WebView
        source={{ uri: 'https://reactnative.dev' }}         // load URL
        style={styles.web}                                   // flex:1 वरना खाली दिखेगा
        startInLoadingState                                  // built-in loader
        javaScriptEnabled                                    // JS allowed (default true)
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },                                    // पूरी screen
  web: { flex: 1 },                                          // WebView भी पूरी जगह ले
});
```

## 💻 Code Example — Advanced
```jsx
import React, { useRef, useState, useCallback } from 'react';
import { View, Text, ActivityIndicator, BackHandler, Platform, StyleSheet, Button } from 'react-native';
import { WebView } from 'react-native-webview';

const ALLOWED_HOSTS = ['pay.example.com'];                   // whitelist
const SUCCESS_URL = 'myapp://payment-success';               // redirect we catch

export default function PaymentWebView({ url, onDone }) {
  const ref = useRef(null);                                  // WebView methods
  const [canGoBack, setCanGoBack] = useState(false);         // history?
  const [loading, setLoading] = useState(true);              // spinner
  const [error, setError] = useState(null);                  // load error

  // Android hardware back → WebView history में पीछे जाओ
  React.useEffect(() => {
    if (Platform.OS !== 'android') return undefined;         // iOS में नहीं चाहिए
    const sub = BackHandler.addEventListener('hardwareBackPress', () => {
      if (canGoBack && ref.current) { ref.current.goBack(); return true; } // consume event
      return false;                                          // default (screen back)
    });
    return () => sub.remove();                               // cleanup
  }, [canGoBack]);

  // हर navigation request check करो
  const onShould = useCallback((req) => {
    if (req.url.startsWith(SUCCESS_URL)) {                   // deep link redirect
      onDone({ ok: true });                                  // tell parent
      return false;                                          // WebView load न करे
    }
    try {
      const host = new URL(req.url).host;                    // hostname निकालो
      return ALLOWED_HOSTS.includes(host);                   // सिर्फ whitelist
    } catch { return false; }                                // invalid URL block
  }, [onDone]);

  const onMessage = (e) => {                                 // page → RN message
    try {
      const msg = JSON.parse(e.nativeEvent.data);            // JSON parse (string आता है)
      if (msg.type === 'CLOSE') onDone({ ok: false });       // page ने close माँगा
    } catch { /* ignore non-JSON */ }
  };

  if (error) return <View style={styles.c}><Text>Load failed</Text><Button title="Retry" onPress={() => { setError(null); ref.current?.reload(); }} /></View>;

  return (
    <View style={styles.c}>
      <WebView
        ref={ref}
        source={{ uri: url }}
        onNavigationStateChange={s => setCanGoBack(s.canGoBack)} // history track
        onShouldStartLoadWithRequest={onShould}              // URL filter
        onMessage={onMessage}                                // bridge
        onLoadEnd={() => setLoading(false)}                  // loaded
        onError={e => setError(e.nativeEvent)}               // network error
        onHttpError={e => console.warn('HTTP', e.nativeEvent.statusCode)}
        injectedJavaScript={`window.isInApp = true; true;`}  // JS inject (end में true ज़रूरी)
        originWhitelist={['https://*']}                      // सिर्फ https
        setSupportMultipleWindows={false}                    // Android popups block
        domStorageEnabled                                    // localStorage allowed
      />
      {loading && <ActivityIndicator style={StyleSheet.absoluteFill} />}
    </View>
  );
}
const styles = StyleSheet.create({ c: { flex: 1 } });
// Not run here — requires device/simulator (native WebView).
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Engine | Android System WebView (Chromium) | WKWebView (WebKit) |
| Hardware back | `BackHandler` से handle करना पड़ता है | नहीं है; swipe-back gesture `allowsBackForwardNavigationGestures` |
| File upload | `<input type=file>` supported, permissions manifest | Supported, Info.plist usage strings |
| Mixed content (http in https) | `mixedContentMode` prop | App Transport Security (ATS) HTTP block |
| Cookies | `sharedCookiesEnabled` limited | `sharedCookiesEnabled` / `thirdPartyCookiesEnabled` iOS/Android अलग |
| Debug | `chrome://inspect` | Safari → Develop menu |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install react-native-webview   (Expo Go में काम करता है)
import { WebView } from 'react-native-webview';
// कोई native config नहीं
```
CLI way:
```jsx
// npm i react-native-webview
// iOS: cd ios && pod install
// Android: autolinking — extra step नहीं
// Android में file-upload/camera permissions manifest में खुद जोड़ो
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: WebView को `flex: 1` नहीं दिया → खाली/0 height
✅ Correct: Parent और WebView दोनों `flex: 1`

❌ Mistake 2: User-supplied URL बिना check load करना (phishing/XSS)
✅ Correct: HTTPS + host whitelist + `onShouldStartLoadWithRequest`

❌ Mistake 3: `injectedJavaScript` के अंत में `true;` नहीं (Android/iOS silent fail)
✅ Correct: `"...; true;"`

❌ Mistake 4: `postMessage` में object भेजना
✅ Correct: `JSON.stringify` / `JSON.parse`

❌ Mistake 5: Android back button WebView history की जगह app बंद कर देता
✅ Correct: `BackHandler` + `canGoBack`

---

## 🧠 Tricky Interview Question
```jsx
<WebView source={{ html: '<h1>Hi</h1>' }} />
```
Q: Android पर text बहुत छोटा दिखता है — क्यों?

Answer: HTML में viewport meta tag नहीं है, इसलिए WebView desktop-width (~980px) मानकर page को scale-down करता है। Fix: `<meta name="viewport" content="width=device-width, initial-scale=1">` जोड़ो (या `scalesPageToFit` — पुराना, अब Android के लिए मुख्यतः viewport meta)। यह web-side का issue है, RN का नहीं।

---

## ⚫ Interview Questions + Answers
Q1: WebView security risks क्या हैं?
A1: Untrusted URLs से XSS/phishing, JS bridge abuse, mixed content, cookie leak। Mitigation: HTTPS only, whitelist, `originWhitelist`, bridge में message validate, sensitive tokens URL में न दो।

Q2: Page और RN में data कैसे भेजें?
A2: Page → RN: `window.ReactNativeWebView.postMessage(str)` + `onMessage`. RN → page: `injectJavaScript` या `ref.postMessage` + page में `message` listener।

Q3: WebView vs `Linking.openURL` vs in-app browser?
A3: WebView app के UI में embed, पूरा control, पर risk ज़्यादा। `Linking.openURL` external browser। `expo-web-browser` (Chrome Custom Tabs/SFSafariViewController) secure OAuth/payment के लिए बेहतर।

Q4: Login cookies कैसे share करें?
A4: `sharedCookiesEnabled`, या token को `injectedJavaScriptBeforeContentLoaded` से set; पर token exposure सोचकर।

Q5: Performance खराब हो तो?
A5: Heavy pages avoid, `cacheEnabled`, lazy load, native screens में critical flows बनाओ, WebView को list items में न रखो।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Static/CMS content (T&C, FAQ), 3rd-party payment/OAuth pages
- Existing web feature जल्दी app में लाना

❌ Avoid when:
- Core flows (home feed, cart) — native feel चाहिए
- OAuth के लिए जब `expo-web-browser`/`expo-auth-session` बेहतर हो
- Offline-first features

---

## 📊 Visual Diagram
```
  ┌─────────────── React Native App ───────────────┐
  │  <WebView/> ── native WebView (WKWebView / Android WebView)
  │       ▲  onMessage                │ postMessage
  │       │                           ▼
  │  RN JS  ◄── JS bridge ──►  Web page JS
  │  injectJavaScript ─────────►
  └────────────────────────────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| WebView | Embedded browser view | App में browser view |
| postMessage | Send string between JS worlds | संदेश भेजना |
| injectedJavaScript | JS run inside page | Page में JS डालना |
| originWhitelist | Allowed origins | अनुमत sites |
| ATS | iOS HTTP security rule | iOS की HTTPS नीति |
| Viewport | Page scaling meta | Page scaling |

---

## ⚡ 3-Line Summary
English: WebView embeds web pages in your app and talks to RN via postMessage.
Whitelist URLs, handle Android back, end injected JS with `true;`.
Use for static/3rd-party pages, not core flows.

Hindi: WebView app में web page दिखाता है; RN से postMessage से बात करता है।
URLs whitelist करो, Android back संभालो, injected JS के अंत में `true;`।
Static/3rd-party pages के लिए, core flows के लिए नहीं।

---

## ➡️ Next Topic
**189. React Native + Stripe Payments** — card payment सुरक्षित तरीके से (PaymentSheet)।

---
