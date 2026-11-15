# 144. Axios in React Native
# हिंदी में: React Native में Axios — Interceptors वाला HTTP client
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 target (check current docs — APIs change between SDKs).** React Native 0.76, `axios` 1.x (`npm i axios` / `npx expo install axios`)। Axios pure JS है — कोई native setup नहीं।

---

## 🔵 Simple Definition (English)
**Axios** is a popular HTTP client library. Compared to fetch, it parses JSON automatically, throws on 4xx/5xx errors, supports timeouts, and has **interceptors** to run code on every request or response (like adding a token).

## 🔵 सरल परिभाषा (Hindi)
**Axios** एक popular HTTP client library है। fetch के मुकाबले यह JSON खुद parse करता है, 4xx/5xx पर error throw करता है, timeout देता है, और **interceptors** देता है जिनसे हर request/response पर code चलाया जा सकता है (जैसे token जोड़ना)।

---

## 🔴 Problem it Solves
```
fetch में हर call पर दोहराना पड़ता है:
  - base URL, headers, token
  - res.ok check, res.json()
  - timeout
  - 401 पर token refresh

Axios: एक instance बनाओ, interceptors से यह सब एक जगह।
```

## 🔴 यह क्यों बना? (Hindi)
```
बड़े app में 50+ API calls होती हैं।
हर जगह token/headers/error code दोहराना गलती का कारण है।
Axios instance + interceptors से central control मिलता है।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → axios.create({ baseURL, timeout }) से instance
Step 2 → Request interceptor: हर request में token जोड़ो
Step 3 → Request जाती है
Step 4 → Response interceptor: success → data; error → handle (जैसे 401)
Step 5 → 2xx के बाहर status पर Promise reject (error.response.status)
Step 6 → error.response नहीं है → network/timeout error
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. instance बनाओ (baseURL + timeout)।
2. Request interceptor से token लगाओ।
3. Response interceptor से 401 जैसे errors central जगह handle करो।
4. error.response हो तो server ने जवाब दिया; न हो तो network समस्या।
```

---

## 🟡 Real World Example
**Swiggy:** हर API call में auth token और device-id header interceptor से जाता है। Token expire होने पर 401 आता है → interceptor refresh token से नया token लेकर request दोबारा भेजता है — user को पता भी नहीं चलता। **Paytm:** सभी calls पर timeout 15s और common error toast।

## 🟡 Real Example Hindi mein
**Swiggy** में token expire होने पर 401 आता है; interceptor चुपचाप नया token लेकर वही request दोबारा भेज देता है। User को login screen नहीं दिखती।

---

## 💻 Code Example — Basic

```jsx
// AxiosBasic.jsx — GET with axios
import React, { useEffect, useState } from 'react';              // hooks
import { Text, FlatList, ActivityIndicator } from 'react-native'; // UI
import axios from 'axios';                                       // axios

export default function AxiosBasic() {
  const [posts, setPosts] = useState([]);                        // data
  const [loading, setLoading] = useState(true);                  // loading
  const [error, setError] = useState(null);                      // error

  useEffect(() => {
    const controller = new AbortController();                    // cancel support
    axios
      .get('https://jsonplaceholder.typicode.com/posts', {
        params: { _limit: 10 },                                  // query string
        timeout: 8000,                                           // 8s timeout
        signal: controller.signal,                               // abort
      })
      .then((res) => setPosts(res.data))                         // JSON पहले से parsed
      .catch((e) => { if (!axios.isCancel(e)) setError(e.message); }) // cancel ignore
      .finally(() => setLoading(false));                         // done
    return () => controller.abort();                             // unmount पर cancel
  }, []);

  if (loading) return <ActivityIndicator style={{ marginTop: 40 }} />; // spinner
  if (error) return <Text>{error}</Text>;                        // error
  return (
    <FlatList
      data={posts}
      keyExtractor={(p) => String(p.id)}
      renderItem={({ item }) => <Text style={{ padding: 12 }}>{item.title}</Text>}
    />
  );
}
```

## 💻 Code Example — Advanced

```jsx
// apiClient.js — instance + auth interceptor + refresh on 401 (single-flight)
import axios from 'axios';                                       // axios
import * as SecureStore from 'expo-secure-store';                // secure token storage (Expo)

export const api = axios.create({
  baseURL: 'https://api.example.com',                            // backend
  timeout: 15000,                                                // 15s
  headers: { Accept: 'application/json' },                       // default header
});

api.interceptors.request.use(async (config) => {                 // हर request से पहले
  const token = await SecureStore.getItemAsync('accessToken');   // token पढ़ो
  if (token) config.headers.Authorization = `Bearer ${token}`;   // header जोड़ो
  return config;                                                 // आगे जाने दो
});

let refreshPromise = null;                                       // एक ही refresh चले

async function refreshToken() {
  const refresh = await SecureStore.getItemAsync('refreshToken'); // refresh token
  // plain axios (api नहीं) ताकि interceptor loop न बने
  const { data } = await axios.post('https://api.example.com/auth/refresh', { refresh });
  await SecureStore.setItemAsync('accessToken', data.accessToken); // नया token save
  return data.accessToken;                                       // return
}

api.interceptors.response.use(
  (res) => res,                                                  // success pass-through
  async (error) => {
    const original = error.config;                               // failed request
    if (error.response?.status === 401 && !original._retry) {    // पहली बार 401
      original._retry = true;                                    // loop रोकने का flag
      try {
        refreshPromise = refreshPromise || refreshToken();       // parallel calls share करें
        const newToken = await refreshPromise;                   // wait
        original.headers.Authorization = `Bearer ${newToken}`;   // नया token
        return api(original);                                    // request दोबारा
      } catch (e) {
        await SecureStore.deleteItemAsync('accessToken');        // logout जैसा
        return Promise.reject(e);                                // caller को error
      } finally {
        refreshPromise = null;                                   // reset
      }
    }
    return Promise.reject(error);                                // बाकी errors
  }
);
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Axios adapter | RN में XHR adapter (JS) | वही |
| Cleartext HTTP | Blocked by default (9+) | ATS blocks |
| Emulator localhost | `10.0.2.2` | `localhost` |
| Self-signed SSL | Dev में भी fail | Dev में भी fail |
| Behaviour of axios | Same | Same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install axios expo-secure-store
// import axios from 'axios';
```
CLI way:
```jsx
// npm i axios
// Token storage: react-native-keychain (npm i react-native-keychain; cd ios && pod install)
// import axios from 'axios';
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Refresh call भी उसी `api` instance से करना → infinite loop।
✅ Correct: Refresh के लिए plain `axios.post` या अलग instance।

❌ Mistake 2: `error.response.status` बिना check के पढ़ना — network error में `response` undefined।
✅ Correct: `error.response?.status`।

❌ Mistake 3: 10 parallel calls पर 10 बार refresh।
✅ Correct: Shared `refreshPromise` (single-flight)।

❌ Mistake 4: Timeout न लगाना।
✅ Correct: `timeout` instance में रखो।

---

## 🧠 Tricky Interview Question
axios में 404 आने पर `.then` चलेगा या `.catch`? और fetch में?

Answer: Axios में default `validateStatus` 2xx को ही success मानता है, इसलिए 404 पर **`.catch`** चलता है (`error.response.status === 404`)। fetch में `.then` चलता है। यही दोनों में मुख्य behavioural फर्क है।

---

## ⚫ Interview Questions + Answers
Q1: Interceptor क्या है?
A1: Request/response के रास्ते में चलने वाला function — token जोड़ना, logging, 401 handle करना।

Q2: Axios instance क्यों?
A2: Shared baseURL, timeout, headers; अलग APIs के लिए अलग config।

Q3: Request cancel कैसे?
A3: `AbortController` signal (axios 0.22+); पुराना CancelToken deprecated है।

Q4: Upload progress कैसे मिलता है?
A4: `onUploadProgress` callback (अगले topics में)।

Q5: fetch की जगह axios कब?
A5: जब interceptors, auto-JSON, timeout, progress चाहिए; वरना fetch काफी है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Auth + refresh + central error handling चाहिए
- बड़ा app, कई endpoints

❌ Avoid when:
- 2-3 simple calls वाला छोटा app (bundle size बढ़ेगा)

---

## 📊 Visual Diagram
```
 Screen ─► api.get() ─► [Request Interceptor: +token] ─► Server
                                                          │
 Screen ◄─ data ◄─ [Response Interceptor] ◄───────────────┘
                     │ 401?
                     └─► refresh token ─► retry original request
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Interceptor | Hook on every req/res | बीच में चलने वाला hook |
| Instance | Preconfigured axios | पहले से configured axios |
| baseURL | Common URL prefix | साझा URL |
| validateStatus | Which status = success | कौन सा status सफल |
| Single-flight | One refresh at a time | एक समय में एक refresh |

---

## ⚡ 3-Line Summary
English: Axios gives auto JSON, error throwing, timeouts and interceptors.
Create one instance and attach token/refresh logic in interceptors.
Never use the same instance for the refresh call.

Hindi: Axios auto JSON, error throw, timeout और interceptors देता है।
एक instance बनाकर interceptors में token/refresh logic रखो।
Refresh call उसी instance से कभी मत करो।

---

## ➡️ Next Topic
**145. API Error Handling** — network, HTTP और parse errors को सही तरीके से संभालना।
