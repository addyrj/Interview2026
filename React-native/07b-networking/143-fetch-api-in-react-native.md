# 143. Fetch API in React Native
# हिंदी में: React Native में Fetch API — Server से data लाना
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 target (check current docs — APIs change between SDKs).** React Native 0.76। `fetch`, `Headers`, `Request`, `Response`, `AbortController`, `FormData` global में मिलते हैं — कोई install नहीं।

---

## 🔵 Simple Definition (English)
**fetch** is the built-in way to make HTTP requests in React Native. It returns a Promise. You call `fetch(url, options)`, then read the body with `response.json()`. It does **not** throw on HTTP errors like 404 or 500.

## 🔵 सरल परिभाषा (Hindi)
**fetch** React Native में HTTP request भेजने का built-in तरीका है। यह Promise देता है। `fetch(url, options)` call करो, फिर `response.json()` से body पढ़ो। 404 या 500 पर यह **error throw नहीं करता** — खुद `response.ok` जाँचना पड़ता है।

---

## 🔴 Problem it Solves
```
मोबाइल app का data server पर रहता है (restaurants, orders, users)।
App को उसे लाना/भेजना है — JSON में।

fetch के बिना: पुराना XMLHttpRequest — verbose, callback-heavy।
fetch के साथ: Promise/async-await, साफ़ code, सभी platforms पर same।
```

## 🔴 यह क्यों बना? (Hindi)
```
Web standard है, RN ने वही API दी ताकि web developers आसानी से सीखें।
Promise-based है तो async/await से code सरल रहता है।
Extra library के बिना basic API calls हो जाती हैं।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → fetch(url, { method, headers, body }) call
Step 2 → Native networking layer (OkHttp on Android, NSURLSession on iOS) request भेजता है
Step 3 → Response headers आते ही Promise resolve (body अभी बाकी हो सकती है)
Step 4 → if (!res.ok) → खुद error बनाओ (status 4xx/5xx पर भी Promise resolve होता है!)
Step 5 → await res.json() → body parse
Step 6 → Network down / DNS fail / abort पर ही Promise reject होता है
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. fetch request भेजता है (native layer के ज़रिए)।
2. Response आने पर Promise resolve होता है।
3. res.ok देखो — false हो तो error बनाओ।
4. res.json() से data निकालो।
5. Network fail पर ही reject होता है।
```

---

## 🟡 Real World Example
**Zomato:** Home खुलते ही `GET /restaurants?lat=..&lng=..` से nearby restaurants fetch होते हैं। **Swiggy:** Order place करने पर `POST /orders` में JSON body और `Authorization` header भेजा जाता है। **Paytm:** Balance check के लिए token header के साथ GET।

## 🟡 Real Example Hindi mein
**Zomato** खुलते ही आपकी location भेजकर nearby restaurants की list fetch करता है। **Swiggy** में order करते समय JSON body और token header के साथ POST जाता है।

---

## 💻 Code Example — Basic

```jsx
// FetchBasic.jsx — GET data and show in list
import React, { useEffect, useState } from 'react';              // hooks
import { View, Text, FlatList, ActivityIndicator } from 'react-native'; // UI

export default function FetchBasic() {                           // component
  const [data, setData] = useState([]);                          // list state
  const [loading, setLoading] = useState(true);                  // loading flag
  const [error, setError] = useState(null);                      // error message

  useEffect(() => {                                              // run once on mount
    const load = async () => {                                   // async helper
      try {
        const res = await fetch('https://jsonplaceholder.typicode.com/posts?_limit=10'); // GET
        if (!res.ok) throw new Error(`HTTP ${res.status}`);      // fetch 404/500 पर throw नहीं करता
        const json = await res.json();                           // body parse
        setData(json);                                           // save
      } catch (e) {
        setError(e.message);                                     // network या HTTP error
      } finally {
        setLoading(false);                                       // loading band
      }
    };
    load();                                                      // call
  }, []);                                                        // [] = सिर्फ एक बार

  if (loading) return <ActivityIndicator style={{ marginTop: 40 }} />; // spinner
  if (error) return <Text>Error: {error}</Text>;                 // error UI

  return (
    <FlatList
      data={data}                                                // items
      keyExtractor={(i) => String(i.id)}                         // unique key
      renderItem={({ item }) => <Text style={{ padding: 12 }}>{item.title}</Text>} // row
    />
  );
}
```

## 💻 Code Example — Advanced

```jsx
// api.js — reusable fetch wrapper: timeout, JSON, auth, typed error
const BASE_URL = 'https://api.example.com';                      // तुम्हारा backend

export class ApiError extends Error {                            // custom error class
  constructor(message, status, body) {
    super(message);                                              // message set
    this.name = 'ApiError';                                      // name
    this.status = status;                                        // HTTP status
    this.body = body;                                            // server error body
  }
}

export async function request(path, { method = 'GET', body, token, timeoutMs = 10000 } = {}) {
  const controller = new AbortController();                      // cancel करने के लिए
  const timer = setTimeout(() => controller.abort(), timeoutMs); // timeout पर abort

  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      method,                                                    // GET/POST...
      headers: {
        'Content-Type': 'application/json',                      // JSON भेज रहे हैं
        Accept: 'application/json',                              // JSON चाहिए
        ...(token ? { Authorization: `Bearer ${token}` } : {}),  // token हो तो जोड़ो
      },
      body: body ? JSON.stringify(body) : undefined,             // object → string
      signal: controller.signal,                                 // abort signal
    });

    const text = await res.text();                               // पहले text (empty body safe)
    const data = text ? JSON.parse(text) : null;                 // parse अगर है

    if (!res.ok) throw new ApiError(`Request failed: ${res.status}`, res.status, data); // HTTP error
    return data;                                                 // success
  } catch (e) {
    if (e.name === 'AbortError') throw new ApiError('Request timed out', 0, null); // timeout
    if (e instanceof ApiError) throw e;                          // already typed
    throw new ApiError('Network error', 0, null);                // offline/DNS
  } finally {
    clearTimeout(timer);                                         // timer साफ़
  }
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Native layer | OkHttp | NSURLSession |
| Plain HTTP (`http://`) | Android 9+ पर default blocked (`usesCleartextTraffic` / expo-build-properties) | ATS blocks, exception Info.plist में |
| localhost | Emulator पर `10.0.2.2` | Simulator पर `localhost` |
| Cookies | Native cookie jar | NSHTTPCookieStorage |
| Default timeout | Native default (config के हिसाब से) | 60 sec (NSURLSession default) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// fetch built-in. HTTP (non-HTTPS) के लिए app.json में:
// "plugins": [["expo-build-properties", { "android": { "usesCleartextTraffic": true } }]]
// (dev के लिए; production में HTTPS ही रखो)
// Expo की अपनी fetch: `import { fetch } from 'expo/fetch'` (SDK 52+ में available, streaming support — docs देखो)
```
CLI way:
```jsx
// fetch built-in।
// Android: AndroidManifest.xml में android:usesCleartextTraffic="true" (सिर्फ dev)
// iOS: Info.plist में NSAppTransportSecurity exceptions (सिर्फ dev)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: सोचना कि 404/500 पर `catch` चलेगा।
✅ Correct: `if (!res.ok) throw new Error(...)` खुद करो।

❌ Mistake 2: `res.json()` को `await` न करना।
✅ Correct: `const data = await res.json();`

❌ Mistake 3: POST में `Content-Type` न देना / object सीधे `body` में देना।
✅ Correct: `body: JSON.stringify(obj)` + `'Content-Type': 'application/json'`।

❌ Mistake 4: Emulator पर `localhost` use करना।
✅ Correct: Android emulator पर `10.0.2.2`, real device पर PC का LAN IP।

❌ Mistake 5: Component unmount के बाद setState।
✅ Correct: `AbortController` से cancel और effect cleanup में `abort()`।

---

## 🧠 Tricky Interview Question
```js
fetch('https://api.example.com/missing')
  .then(() => console.log('A'))
  .catch(() => console.log('B'));
```
Server 404 देता है। क्या print होगा?

Answer: **A**। fetch सिर्फ network failure पर reject होता है; 404 में भी response मिलता है, इसलिए `.then` चलता है। `res.ok` / `res.status` खुद check करना होता है।

---

## ⚫ Interview Questions + Answers
Q1: fetch और XMLHttpRequest में क्या फर्क?
A1: fetch Promise-based और modern है; XHR callback-based। RN में fetch अंदर से XHR-जैसे native networking पर बना है।

Q2: Request cancel कैसे करें?
A2: `AbortController`; `signal` को fetch में दो, फिर `controller.abort()`।

Q3: Timeout कैसे लगाएँ?
A3: fetch में built-in timeout नहीं; `AbortController` + `setTimeout` (ऊपर Advanced example)।

Q4: Auth token कहाँ भेजें?
A4: `Authorization: Bearer <token>` header में; token को SecureStore/Keychain में रखो, plain AsyncStorage में नहीं।

Q5: fetch vs axios?
A5: fetch built-in पर verbose; axios में interceptors, auto JSON, timeout, non-2xx पर auto throw (अगले topic में)।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- सरल GET/POST calls हों, bundle size छोटा रखना हो
- Extra dependency नहीं चाहिए

❌ Avoid when:
- Interceptors, retry, upload progress चाहिए (axios/ky बेहतर)
- Complex caching चाहिए (React Query/TanStack Query के साथ भी fetch चलता है)

---

## 📊 Visual Diagram
```
 App ── fetch(url) ──► Native network (OkHttp / NSURLSession) ──► Server
                                                                    │
 App ◄─ Promise resolve (status + headers) ◄────────────────────────┘
   │
   ├─ res.ok ? ── yes ──► await res.json() ──► state
   └─ no ───────► throw Error(status)
 (network fail / abort ► Promise reject ► catch)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Promise | Future result | भविष्य में आने वाला नतीजा |
| res.ok | status 200-299 | सफल status |
| AbortController | Cancel request | Request रद्द करना |
| Header | Request metadata | Request की अतिरिक्त जानकारी |
| JSON | Data format | Data का format |

---

## ⚡ 3-Line Summary
English: fetch is the built-in Promise-based HTTP client in React Native.
It only rejects on network failure, so always check `res.ok`.
Use AbortController for timeout and cancellation.

Hindi: fetch RN का built-in Promise-based HTTP client है।
यह सिर्फ network fail पर reject होता है, इसलिए `res.ok` हमेशा जाँचो।
Timeout और cancel के लिए AbortController use करो।

---

## ➡️ Next Topic
**144. Axios in React Native** — interceptors और auto error handling वाली popular library।
