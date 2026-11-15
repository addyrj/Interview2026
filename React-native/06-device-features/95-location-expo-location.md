# 95. Location — expo-location
# हिंदी में: Location — expo-location (GPS / स्थान)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: Expo SDK 52 (React Native 0.76) + expo-location (check current docs — APIs change between SDKs).
> Note: repo me `93-location.md` pehle se hai (overview); ye file expo-location API ko interview angle se detail me cover karti hai.

---

## 🔵 Simple Definition (English)
**expo-location** gives access to the device's GPS/network location. You can get the current position once (`getCurrentPositionAsync`), watch it continuously (`watchPositionAsync`), convert coordinates to an address (`reverseGeocodeAsync`) and track in the background.

## 🔵 सरल परिभाषा (Hindi)
**expo-location** से phone की GPS/network location मिलती है। एक बार position (`getCurrentPositionAsync`), लगातार tracking (`watchPositionAsync`), coordinates से address (`reverseGeocodeAsync`) और background tracking संभव है।

---

## 🔴 Problem it Solves
```
❌ Android (FusedLocation) aur iOS (CoreLocation) ke alag native APIs
❌ Permission flows alag (foreground vs background)
❌ Address nikalna (lat/lng -> "Koramangala, Bengaluru") mushkil
✅ Ek JS API: permission + position + geocoding + geofencing
```

## 🔴 यह क्यों बना? (Hindi)
```
Android और iOS के location APIs बिल्कुल अलग हैं।
Permission का तरीका भी अलग (foreground / background)।
expo-location एक ही JavaScript API देता है जो दोनों पर चलता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install expo-location
Step 2 → requestForegroundPermissionsAsync() → { status }
Step 3 → status === 'granted'? nahi to message + Settings
Step 4 → Location.hasServicesEnabledAsync() (GPS on hai?)
Step 5 → getCurrentPositionAsync({ accuracy }) → { coords: { latitude, longitude } }
Step 6 → watchPositionAsync(options, cb) → subscription; unmount par .remove()
Step 7 → reverseGeocodeAsync(coords) → address
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Package install करें।
Step 2 → Foreground permission माँगें।
Step 3 → Granted हो तो getCurrentPositionAsync से latitude/longitude लें।
Step 4 → लगातार ट्रैकिंग के लिए watchPositionAsync; screen बंद हो तो subscription .remove() करें।
Step 5 → reverseGeocodeAsync से address का नाम निकालें।
```

---

## 🟡 Real World Example
**Swiggy/Zomato delivery address:** on opening the app it asks "Allow location while using the app". The "Use current location" button calls `getCurrentPositionAsync`, then `reverseGeocodeAsync` to fill "Indiranagar, Bengaluru". **Ola/Uber** track the driver with `watchPositionAsync` (foreground) and background location for the live trip.

## 🟡 Real Example Hindi mein
**Swiggy:** "Use current location" दबाने पर `getCurrentPositionAsync` से lat/lng, फिर `reverseGeocodeAsync` से "Indiranagar, Bengaluru" भर जाता है। **Ola/Uber** driver को `watchPositionAsync` से live track करते हैं।

---

## 💻 Code Example — Basic
```jsx
// CurrentLocation.jsx — ek baar location + address
import React, { useState } from 'react';                     // React + state
import { View, Text, Button } from 'react-native';           // RN UI
import * as Location from 'expo-location';                   // expo-location API

export default function CurrentLocation() {
  const [coords, setCoords] = useState(null);                // lat/lng
  const [address, setAddress] = useState('');                // text address
  const [error, setError] = useState('');                    // error message

  const getLocation = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync(); // permission prompt
    if (status !== 'granted') {                              // user ne mana kiya
      setError('Permission denied');                         // message dikhao
      return;                                                // aage mat badho
    }
    const pos = await Location.getCurrentPositionAsync({     // current position
      accuracy: Location.Accuracy.Balanced,                  // balance of speed + battery
    });
    setCoords(pos.coords);                                   // coords save
    const [place] = await Location.reverseGeocodeAsync(pos.coords); // address lookup
    setAddress(`${place?.name ?? ''}, ${place?.city ?? ''}`);// "name, city"
  };

  return (
    <View style={{ padding: 24 }}>
      <Button title="Use current location" onPress={getLocation} />
      {coords && <Text>{coords.latitude}, {coords.longitude}</Text>}
      {!!address && <Text>{address}</Text>}
      {!!error && <Text style={{ color: 'red' }}>{error}</Text>}
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// useLiveLocation.js — watch hook with cleanup, GPS-off check, Settings link
import { useEffect, useState } from 'react';
import { Alert, Linking, Platform } from 'react-native';
import * as Location from 'expo-location';

export function useLiveLocation(enabled = true) {
  const [position, setPosition] = useState(null);            // latest coords
  const [error, setError] = useState(null);                  // error string

  useEffect(() => {
    if (!enabled) return undefined;                          // off hai to kuch nahi
    let sub;                                                 // subscription
    let cancelled = false;                                   // unmount flag

    (async () => {
      try {
        const services = await Location.hasServicesEnabledAsync(); // GPS toggle
        if (!services) { setError('GPS is off'); return; }   // user ko batao

        let { status, canAskAgain } = await Location.getForegroundPermissionsAsync(); // current state
        if (status !== 'granted' && canAskAgain) {           // sirf tab prompt jab ho sake
          ({ status } = await Location.requestForegroundPermissionsAsync());
        }
        if (status !== 'granted') {                          // abhi bhi mana
          Alert.alert('Location needed', 'Open settings?', [
            { text: 'Cancel' },
            { text: 'Settings', onPress: () => (Platform.OS === 'ios' ? Linking.openURL('app-settings:') : Linking.openSettings()) },
          ]);
          return;
        }
        sub = await Location.watchPositionAsync(
          { accuracy: Location.Accuracy.High, timeInterval: 5000, distanceInterval: 20 }, // 5s ya 20m
          (loc) => { if (!cancelled) setPosition(loc.coords); }  // update state
        );
      } catch (e) {
        setError(String(e.message || e));                    // unexpected error
      }
    })();

    return () => { cancelled = true; sub && sub.remove(); }; // cleanup: tracking band
  }, [enabled]);

  return { position, error };                                // hook output
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Permissions | `ACCESS_COARSE_LOCATION`, `ACCESS_FINE_LOCATION` | `NSLocationWhenInUseUsageDescription` |
| Precision choice | User approximate/precise chun sakta hai (Android 12+) | "Precise Location" toggle (iOS 14+) |
| Background | `ACCESS_BACKGROUND_LOCATION` + foreground service notification | `NSLocationAlwaysAndWhenInUseUsageDescription` + background mode |
| Permission denied | "Don't ask again" → `canAskAgain=false` | Ek baar deny → Settings |
| Simulator | Emulator me mock location | Xcode → Features → Location |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-location
// app.json: ["expo-location", { "locationWhenInUsePermission": "Delivery address ke liye location chahiye" }]
import * as Location from 'expo-location';
```
CLI way:
```jsx
// npm i expo-location (+ expo modules install) ya
// npm i @react-native-community/geolocation / react-native-geolocation-service
// iOS: Info.plist NSLocationWhenInUseUsageDescription + pod install
// Android: manifest me ACCESS_FINE_LOCATION
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Permission check kiye bina `getCurrentPositionAsync` — error throw.
✅ Correct: pehle `requestForegroundPermissionsAsync`.

❌ Mistake 2: `watchPositionAsync` ka subscription remove na karna — battery drain + memory leak.
✅ Correct: `useEffect` cleanup me `sub.remove()`.

❌ Mistake 3: Hamesha `Accuracy.Highest` — battery khatam.
✅ Correct: zarurat ke hisaab se `Balanced`/`High`.

❌ Mistake 4: GPS off hone ko handle na karna.
✅ Correct: `hasServicesEnabledAsync()`.

❌ Mistake 5: iOS permission text na dena (App Store rejection).
✅ Correct: config plugin me clear Hindi/English message.

---

## 🧠 Tricky Interview Question
```jsx
const loc = await Location.getCurrentPositionAsync();
// Android emulator par kabhi kabhi hang hota hai. Kyu?
```
Answer: Emulator par koi location fix nahi hota jab tak mock location set na ho; `getCurrentPositionAsync` fix ka intezaar karta hai. Real device par bhi indoors slow ho sakta hai. Solution: `getLastKnownPositionAsync()` fallback ya `timeout`/lower accuracy.

---

## ⚫ Interview Questions + Answers
Q1: Foreground vs background location?
A1: Foreground app dikhne par; background app band/minimize par bhi (extra permission, TaskManager, review rules strict).

Q2: `getCurrentPositionAsync` vs `watchPositionAsync`?
A2: Pehla ek baar position; doosra continuous updates (subscription).

Q3: Reverse geocoding kya hai?
A3: Coordinates → address. `reverseGeocodeAsync`. Reverse ki limits: platform geocoder rate-limit kar sakta hai.

Q4: Battery kaise bachayein?
A4: Kam accuracy, `distanceInterval`, tracking tabhi jab screen needed, cleanup.

Q5: Permission denied handle?
A5: `canAskAgain` check karo, false ho to `Linking.openSettings()`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Address autofill, nearby restaurants, delivery tracking
- Geofencing/attendance

❌ Avoid when:
- City level kaafi hai (IP / user input)
- Background tracking bina strong reason ke (store rejection)

---

## 📊 Visual Diagram
```
 App → requestForegroundPermissionsAsync → granted?
          │ yes
          ▼
 getCurrentPositionAsync ──► {lat,lng} ──► reverseGeocodeAsync ──► "Indiranagar"
          │
 watchPositionAsync ──► callback every 5s/20m ──► sub.remove() on unmount
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Geocoding | Address → coordinates | पता से coordinates |
| Reverse geocoding | Coordinates → address | Coordinates से पता |
| Accuracy | Precision vs battery | सटीकता |
| Geofence | Virtual boundary | आभासी घेरा |
| canAskAgain | Can prompt again | दोबारा पूछ सकते हैं |

---

## ⚡ 3-Line Summary
English: expo-location gives current/live position, geocoding and background tracking.
Always request permission, check GPS, and remove watchers.
Use balanced accuracy to save battery.

Hindi: expo-location current/live location, geocoding और background tracking देता है।
हमेशा permission माँगें, GPS जाँचें और watcher हटाएँ।
Battery के लिए balanced accuracy रखें।

---

## ➡️ Next Topic
**96. Maps — react-native-maps** — location को map पर दिखाना।

---
