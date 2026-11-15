# 296. Interview Problem: Build a Custom Hook — useLocation
# हिंदी में: Custom Hook बनाओ — useLocation
# Platform: Both ✅ (Android ✅ | iOS ✅)
# Difficulty: ⭐⭐⭐ Medium | Asked at: Swiggy, Zomato, Ola, Rapido, Uber

Files: `useLocation.js` (the hook), `LocationScreen.jsx` (demo).
Target: Expo SDK 52 with `expo-location` (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
`useLocation` is a reusable hook that hides the details of location permission, fetching the position, errors and cleanup. Any screen can call it and get `{ coords, error, loading, permission, refresh }`.

## 🔵 सरल परिभाषा (Hindi)
`useLocation` एक reusable hook है जो location की permission, position लेना, errors और cleanup की सारी बातें छुपा देता है। कोई भी screen इसे call करके `{ coords, error, loading, permission, refresh }` पा सकती है।

---

## 🔴 Problem it Solves
Without a hook, every screen repeats permission code, loading flags and error handling, and often forgets to stop GPS updates. One tested hook removes duplication and leaks.

## 🔴 यह क्यों बना? (Hindi)
Hook के बिना हर screen में permission code, loading flags और error handling दोहराना पड़ता है, और GPS updates बंद करना अक्सर भूल जाते हैं। एक tested hook से duplication और leaks ख़त्म होते हैं।

---

## 🔴 Problem Statement
Write `useLocation({ watch })`: ask foreground permission; one-time fetch by default; optional live tracking every 5 s / 10 m; expose `refresh()`; report errors (permission denied, GPS off); never set state after unmount; stop tracking on unmount. The screen must offer "Open Settings" after a denial.

## 💡 Approach
```
state: coords, error, loading, permission ('undetermined' | 'granted' | 'denied')
refs : subRef (watch subscription), mounted (avoid setState after unmount)
requestPermission() -> Location.requestForegroundPermissionsAsync()
refresh()           -> permission -> getCurrentPositionAsync -> setCoords   (try/catch/finally loading)
useEffect:
   watch=false -> refresh() once
   watch=true  -> watchPositionAsync(options, cb) ; cleanup -> subscription.remove()
```

## 🟢 How it Works — Step by Step
```
Step 1 → Screen calls useLocation()
Step 2 → Effect runs: request foreground permission (OS dialog)
Step 3 → Denied -> error "Location permission denied" and permission = 'denied'
Step 4 → Granted -> getCurrentPositionAsync({ accuracy: Balanced }) -> coords
Step 5 → watch mode: watchPositionAsync updates coords every 5 s or 10 m
Step 6 → Unmount: mounted=false, subscription.remove() (GPS stops)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Screen useLocation() call करती है
Step 2 → Effect चलता है: foreground permission माँगता है (OS dialog)
Step 3 → मना किया -> error "Location permission denied" और permission = 'denied'
Step 4 → मंज़ूर -> getCurrentPositionAsync({ accuracy: Balanced }) -> coords
Step 5 → watch mode में watchPositionAsync हर 5 सेकंड या 10 मीटर पर coords बदलता है
Step 6 → Unmount: mounted=false, subscription.remove() (GPS बंद)
```

---

## 🟡 Real World Example
Zomato / Swiggy "Deliver to" auto-detect (one-time fetch), Swiggy delivery partner and Rapido captain apps (continuous tracking), Ola "Pickup location".

## 🟡 Real Example Hindi mein
Zomato / Swiggy का "Deliver to" auto-detect (एक बार fetch), Swiggy delivery partner और Rapido captain apps (लगातार tracking), Ola का "Pickup location"।

---

## 💻 Code Example — Basic
```jsx
import { useEffect, useState } from 'react';                     // hooks
import * as Location from 'expo-location';                       // location API

export function useSimpleLocation() {
  const [coords, setCoords] = useState(null);                    // result
  const [error, setError] = useState(null);                      // error text
  useEffect(() => {
    (async () => {
      const { status } = await Location.requestForegroundPermissionsAsync(); // ask permission
      if (status !== 'granted') return setError('Permission denied');        // stop if denied
      const pos = await Location.getCurrentPositionAsync({});                // one-time fetch
      setCoords(pos.coords);                                                 // save
    })();
  }, []);
  return { coords, error };
}
```

## 💻 Code Example — Advanced
From `useLocation.js`:
```jsx
export default function useLocation({ watch = false } = {}) {
  const [coords, setCoords] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [permission, setPermission] = useState('undetermined');
  const subRef = useRef(null);                                   // watch subscription
  const mounted = useRef(true);                                  // no setState after unmount

  const requestPermission = useCallback(async () => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (mounted.current) setPermission(status);
    return status === 'granted';
  }, []);

  const refresh = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      if (!(await requestPermission())) { if (mounted.current) setError('Location permission denied'); return; }
      const pos = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
      if (mounted.current) setCoords(pos.coords);
    } catch (e) {
      if (mounted.current) setError(e.message ?? 'Could not get location');   // e.g. GPS off
    } finally {
      if (mounted.current) setLoading(false);                    // always stop the spinner
    }
  }, [requestPermission]);

  useEffect(() => {
    mounted.current = true;
    if (!watch) { refresh(); return () => { mounted.current = false; }; }
    (async () => {                                               // live tracking
      if (!(await requestPermission())) { setError('Location permission denied'); return; }
      subRef.current = await Location.watchPositionAsync(
        { accuracy: Location.Accuracy.High, timeInterval: 5000, distanceInterval: 10 },
        (pos) => mounted.current && setCoords(pos.coords));
      if (!mounted.current) subRef.current.remove();             // unmounted while awaiting
    })();
    return () => { mounted.current = false; subRef.current?.remove(); };
  }, [watch, refresh, requestPermission]);

  return { coords, error, loading, permission, refresh };
}
```
Foreground only. Background tracking (delivery apps) needs `requestBackgroundPermissionsAsync`, `Location.startLocationUpdatesAsync` with `expo-task-manager`, a development build, and a foreground-service notification on Android; Play Store and App Store review need a clear justification.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Permission | `ACCESS_COARSE/FINE_LOCATION`; user can choose approximate | `NSLocationWhenInUseUsageDescription` text is mandatory; "Precise" toggle |
| Don't-ask-again | After two denials the dialog stops | After one denial the dialog stops |
| Provider | Fused provider; GPS off -> error | CoreLocation; Location Services off -> error |
| Background | Foreground service + notification | "Always" permission + background mode |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-location
// app.json: "plugins": [["expo-location", { "locationWhenInUsePermission": "Allow $(PRODUCT_NAME) to use your location to find restaurants" }]]
```
CLI way:
```jsx
// npm i react-native-geolocation-service   (or @react-native-community/geolocation)
// Info.plist: NSLocationWhenInUseUsageDescription ; AndroidManifest: ACCESS_FINE_LOCATION
// Geolocation.getCurrentPosition(success, error, { enableHighAccuracy: true, timeout: 15000 })
// cd ios && pod install
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Not removing the `watchPositionAsync` subscription -> GPS keeps running, battery drain.
✅ Correct: `subscription.remove()` in cleanup (also if unmounted while awaiting).

❌ Mistake 2: `setState` after unmount.
✅ Correct: `mounted` ref guard (or an abort flag).

❌ Mistake 3: Using `Accuracy.Highest` for a simple address lookup.
✅ Correct: `Balanced` for one-time, `High` only for tracking.

❌ Mistake 4: Showing only "error" after denial.
✅ Correct: Button for `Linking.openSettings()`.

❌ Mistake 5: Missing iOS usage description text.
✅ Correct: Set `locationWhenInUsePermission` in the plugin.

---

## 🧠 Tricky Interview Question
In `watch` mode the effect awaits `watchPositionAsync`. If the user leaves the screen before the promise resolves, what leaks and how does this hook handle it?

Answer: The subscription is created after the cleanup already ran, so `subRef.current?.remove()` in cleanup found nothing, and tracking would continue forever. The hook checks `if (!mounted.current) subRef.current.remove()` right after the await, closing that gap. (Small caveat: in watch mode the `setError('Location permission denied')` call is not guarded by `mounted`; wrap it the same way in production.)

---

## ⚫ Interview Questions + Answers
Q1: Why a custom hook?
A1: Reuse stateful logic, keep screens simple, test it once.

Q2: One-time vs watch?
A2: `getCurrentPositionAsync` once; `watchPositionAsync` for continuous updates with time/distance filters.

Q3: Why `useCallback` for `refresh` / `requestPermission`?
A3: They are effect dependencies; stable identities prevent the effect from re-running every render.

Q4: How to test the hook?
A4: Mock `expo-location` and use `renderHook` from `@testing-library/react-native`.

Q5: Foreground vs background permission?
A5: Foreground works while the app is visible; background needs separate permission, task manager and a justification.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several screens need location (address, nearby, tracking)

❌ Avoid when:
- Only one screen uses it once; a plain function may be enough. Avoid watch mode when you do not need live updates (battery).

---

## 📊 Visual Diagram
```
 Screen ── useLocation({watch}) ──┐
                                  ▼
                requestForegroundPermissionsAsync
                   │ denied                │ granted
                   ▼                       ▼
         error + permission='denied'   watch? ── no ─► getCurrentPositionAsync ─► coords
         [Open Settings]                  └─ yes ─► watchPositionAsync(cb) ─► coords (live)
                                                       unmount ─► subscription.remove()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Custom hook | Reusable stateful logic | अपना hook |
| Coordinates | Latitude / longitude | निर्देशांक |
| Accuracy | Precision vs battery trade-off | सटीकता |
| Subscription | Live listener you must remove | सक्रिय listener |
| Foreground permission | Only while app is visible | App खुला होने पर अनुमति |

---

## ⚡ 3-Line Summary
English: `useLocation` wraps permission, fetch, error and cleanup in one hook.
One-time by default; `watch: true` gives live updates and must be removed on unmount.
Send users to Settings after a denial.

Hindi: `useLocation` permission, fetch, error और cleanup को एक hook में समेटता है।
Default में एक बार; `watch: true` live updates देता है और unmount पर हटाना ज़रूरी है।
मना करने के बाद user को Settings भेजें।

---

## ✅ What was verified
Under react-native-web + jsdom with `expo-location` mocked: the screen shows the fetched coordinates; after a mocked "denied" result and Refresh it shows the error and the "Open Settings" button. Watch mode, real GPS, OS dialogs and background tracking were not run (native, needs a device).

---

## ➡️ Next Topic
297. Build Custom Hook — useCamera: the same pattern (permission + device API) for the camera.
