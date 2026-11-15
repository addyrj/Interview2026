# 145. API Error Handling
# हिंदी में: API Error Handling — Network/HTTP errors को सही तरह संभालना
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 target (check current docs — APIs change between SDKs).** React Native 0.76। Pure JS patterns; `@react-native-community/netinfo` (Expo में `npx expo install @react-native-community/netinfo`)।

---

## 🔵 Simple Definition (English)
**API error handling** means catching every way a request can fail (no internet, timeout, 4xx, 5xx, bad JSON) and showing the user a clear message with a way to retry, instead of crashing or showing a blank screen.

## 🔵 सरल परिभाषा (Hindi)
**API error handling** का मतलब है request fail होने के हर तरीके (internet नहीं, timeout, 4xx, 5xx, गलत JSON) को पकड़ना और user को साफ़ message व retry का option देना — crash या खाली screen नहीं।

---

## 🔴 Problem it Solves
```
मोबाइल network अविश्वसनीय है (लिफ्ट, मेट्रो, 2G)।
बिना handling:
  ❌ Infinite spinner
  ❌ "undefined is not an object" crash
  ❌ User को पता नहीं क्या गलत हुआ
```

## 🔴 यह क्यों बना? (Hindi)
```
Mobile network बार-बार टूटता है।
हर error का अलग मतलब है: 401 = login दोबारा, 404 = item नहीं, 500 = server गलती।
सही handling से user को सही संदेश और retry मिलता है।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Request को try/catch में रखो
Step 2 → Error को classify करो:
          NETWORK (response नहीं) | TIMEOUT | HTTP 4xx | HTTP 5xx | PARSE
Step 3 → हर class को user-friendly message map करो
Step 4 → Retryable (network, timeout, 5xx) vs non-retryable (4xx) तय करो
Step 5 → UI में error state + "Retry" button
Step 6 → Unexpected errors को log करो (Sentry आदि), user को generic message
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. try/catch लगाओ।
2. Error का प्रकार पहचानो (network / timeout / 4xx / 5xx / parse)।
3. हर प्रकार के लिए सरल Hindi/English message।
4. Retry सिर्फ़ उन्हीं पर जो ठीक हो सकते हैं।
5. UI में retry button, और log भेजो।
```

---

## 🟡 Real World Example
**Zomato:** Internet बंद → "No internet. Check connection" + Retry। **Swiggy:** 500 पर "Something went wrong, try again"; 401 पर login screen। **Paytm UPI:** Timeout पर status unknown दिखाने की जगह "Check payment status" flow — double payment से बचाव।

## 🟡 Real Example Hindi mein
**Paytm:** Payment के दौरान timeout आए तो app तुरंत "fail" नहीं दिखाता, बल्कि status check करता है — ताकि पैसा कटा हो तो दोबारा charge न हो। यही सोच-समझकर की गई error handling है।

---

## 💻 Code Example — Basic

```jsx
// ErrorBasic.jsx — show error + retry button
import React, { useCallback, useEffect, useState } from 'react'; // hooks
import { View, Text, Button, ActivityIndicator } from 'react-native'; // UI

export default function ErrorBasic() {
  const [state, setState] = useState({ status: 'loading', data: null, error: null }); // one state object

  const load = useCallback(async () => {                          // reusable loader
    setState({ status: 'loading', data: null, error: null });     // reset
    try {
      const res = await fetch('https://jsonplaceholder.typicode.com/users/1'); // request
      if (!res.ok) throw new Error(`HTTP ${res.status}`);         // HTTP error
      const data = await res.json();                              // parse
      setState({ status: 'success', data, error: null });         // ok
    } catch (e) {
      setState({ status: 'error', data: null, error: e.message }); // fail
    }
  }, []);

  useEffect(() => { load(); }, [load]);                           // पहली बार load

  if (state.status === 'loading') return <ActivityIndicator style={{ marginTop: 40 }} />; // spinner
  if (state.status === 'error') {
    return (
      <View style={{ padding: 20 }}>
        <Text>कुछ गलत हुआ: {state.error}</Text>                   {/* message */}
        <Button title="Retry" onPress={load} />                   {/* retry */}
      </View>
    );
  }
  return <Text style={{ padding: 20 }}>{state.data.name}</Text>;  // success UI
}
```

## 💻 Code Example — Advanced

```jsx
// errors.js — classify errors + retry with exponential backoff (logic only)
export const ErrorKind = {                                        // error types
  NETWORK: 'NETWORK', TIMEOUT: 'TIMEOUT', AUTH: 'AUTH',
  CLIENT: 'CLIENT', SERVER: 'SERVER', PARSE: 'PARSE', UNKNOWN: 'UNKNOWN',
};

export function classifyError(err) {                              // fetch या axios error → kind
  if (err?.name === 'AbortError' || err?.code === 'ECONNABORTED') return ErrorKind.TIMEOUT; // timeout
  if (err instanceof SyntaxError) return ErrorKind.PARSE;         // bad JSON
  const status = err?.status ?? err?.response?.status;            // fetch-wrapper / axios
  if (status === 401 || status === 403) return ErrorKind.AUTH;    // auth
  if (status >= 400 && status < 500) return ErrorKind.CLIENT;     // 4xx
  if (status >= 500) return ErrorKind.SERVER;                     // 5xx
  if (err?.message === 'Network request failed' || err?.message === 'Network Error') return ErrorKind.NETWORK; // RN fetch / axios message
  return ErrorKind.UNKNOWN;                                       // बाकी
}

export function userMessage(kind) {                               // user-friendly text
  switch (kind) {
    case ErrorKind.NETWORK: return 'इंटरनेट नहीं है। कनेक्शन जाँचें।';
    case ErrorKind.TIMEOUT: return 'सर्वर जवाब नहीं दे रहा। दोबारा कोशिश करें।';
    case ErrorKind.AUTH:    return 'कृपया दोबारा login करें।';
    case ErrorKind.CLIENT:  return 'अनुरोध सही नहीं था।';
    case ErrorKind.SERVER:  return 'सर्वर में समस्या है। थोड़ी देर बाद कोशिश करें।';
    default:                return 'कुछ गलत हो गया।';
  }
}

const RETRYABLE = new Set([ErrorKind.NETWORK, ErrorKind.TIMEOUT, ErrorKind.SERVER]); // retry योग्य

export async function withRetry(fn, { retries = 3, baseMs = 500 } = {}) {
  let attempt = 0;                                                // कोशिश गिनती
  for (;;) {
    try {
      return await fn();                                          // सफल तो return
    } catch (e) {
      const kind = classifyError(e);                              // type
      if (attempt >= retries || !RETRYABLE.has(kind)) throw e;    // सीमा/non-retryable
      const delay = baseMs * 2 ** attempt + Math.random() * 100;  // exponential + jitter
      await new Promise((r) => setTimeout(r, delay));             // wait
      attempt += 1;                                               // अगली कोशिश
    }
  }
}
// ध्यान: POST (payment) जैसी non-idempotent calls पर auto-retry मत करो (idempotency key चाहिए)।
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| RN fetch network error message | `Network request failed` | `Network request failed` |
| SSL error | Cert error → network failed | ATS/cert error → network failed |
| Cleartext HTTP | Blocked (9+) | Blocked by ATS |
| Background/doze में request | Throttle हो सकती है | App suspend होने पर रुकती है |
| Error handling code | Same | Same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install @react-native-community/netinfo
// Errors → Sentry: npx expo install @sentry/react-native (config plugin)
```
CLI way:
```jsx
// npm i @react-native-community/netinfo && cd ios && pod install
// Sentry: npx @sentry/wizard -i reactNative
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Empty `catch {}`।
✅ Correct: Log करो और UI state बदलो।

❌ Mistake 2: Raw server message user को दिखाना।
✅ Correct: Mapped, friendly message।

❌ Mistake 3: सब errors पर retry।
✅ Correct: सिर्फ network/timeout/5xx पर, backoff के साथ।

❌ Mistake 4: Payment POST को auto-retry करना।
✅ Correct: Idempotency key या status-check flow।

---

## 🧠 Tricky Interview Question
`try { const r = await fetch(url); const d = await r.json(); } catch(e) {}` — server 500 के साथ HTML error page देता है। क्या होगा?

Answer: `fetch` resolve होगा, फिर `r.json()` HTML को parse नहीं कर पाएगा और `SyntaxError` throw करेगा। यानी असली कारण (HTTP 500) छिप जाता है। सही तरीका: पहले `r.ok` जाँचो, फिर parse।

---

## ⚫ Interview Questions + Answers
Q1: Network error और HTTP error में फर्क?
A1: Network error में response ही नहीं मिलता (fetch reject); HTTP error में response मिलता है पर status 4xx/5xx।

Q2: Exponential backoff क्यों?
A2: Server पर एक साथ load न पड़े; हर कोशिश के बीच delay दोगुना, साथ में jitter।

Q3: Global error handling कहाँ?
A3: axios response interceptor, React Error Boundary (render errors), और `ErrorUtils.setGlobalHandler`।

Q4: Error Boundary API error पकड़ता है?
A4: नहीं — सिर्फ render/lifecycle errors; async errors खुद catch करने होंगे।

Q5: 401 कैसे संभालें?
A5: Token refresh → retry; fail पर logout/login screen।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- हर network call पर (हमेशा)
- Retry योग्य read-only calls

❌ Avoid when:
- Non-idempotent writes पर blind auto-retry

---

## 📊 Visual Diagram
```
 request ─► ok? ──yes──► data
              │
              no
              ▼
   classify: NETWORK/TIMEOUT/5xx ─► retry (backoff) ─► अब भी fail ─► error UI + Retry
             4xx ─► message (retry नहीं)
             401 ─► refresh / login
             parse ─► log + generic message
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Backoff | Growing delay between retries | बढ़ती देरी |
| Jitter | Random extra delay | यादृच्छिक अतिरिक्त देरी |
| Idempotent | Safe to repeat | दोहराने पर वही नतीजा |
| Error Boundary | Catches render errors | Render error पकड़ने वाला |
| Retryable | Worth retrying | दोबारा कोशिश योग्य |

---

## ⚡ 3-Line Summary
English: Classify errors into network, timeout, 4xx, 5xx and parse.
Show friendly messages and retry only safe cases with backoff.
Log unexpected errors and never retry payments blindly.

Hindi: Errors को network, timeout, 4xx, 5xx, parse में बाँटो।
Friendly message दिखाओ और सिर्फ़ सुरक्षित cases में backoff के साथ retry करो।
अनपेक्षित errors log करो; payment कभी आँख बंद करके retry मत करो।

---

## ➡️ Next Topic
**146. Loading States Pattern** — loading, success, error, empty states UI में कैसे दिखाएँ।
