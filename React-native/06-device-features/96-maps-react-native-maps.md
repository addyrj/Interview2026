# 96. Maps — react-native-maps
# हिंदी में: Maps — react-native-maps (नक्शा)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: Expo SDK 52 (React Native 0.76) + react-native-maps (Expo Go me bundled version chalta hai; check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
**react-native-maps** renders native maps (Google Maps on Android, Apple Maps or Google Maps on iOS) with `MapView`, `Marker`, `Polyline`, `Circle` and region/camera control. Android always needs a Google Maps API key.

## 🔵 सरल परिभाषा (Hindi)
**react-native-maps** native map दिखाता है (Android पर Google Maps, iOS पर Apple Maps या Google Maps) — `MapView`, `Marker`, `Polyline`, `Circle` और region/camera control के साथ। Android पर हमेशा Google Maps API key चाहिए।

---

## 🔴 Problem it Solves
```
❌ WebView me map = slow, gestures kharab
❌ Native Google/Apple Maps SDK ko alag-alag likhna
✅ Ek <MapView> component: pinch, zoom, rotate native smooth
✅ Markers, route lines, user location dot
```

## 🔴 यह क्यों बना? (Hindi)
```
WebView वाला map धीमा और gestures खराब।
दोनों platforms के native map SDK अलग-अलग।
react-native-maps एक ही component में native smooth map देता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install react-native-maps
Step 2 → Google Maps API key (Android SDK enable) Google Cloud Console se lo
Step 3 → app.json me key daalo (android.config.googleMaps.apiKey)
Step 4 → <MapView style={{flex:1}} initialRegion={...} />
Step 5 → <Marker coordinate title /> add karo
Step 6 → showsUserLocation + expo-location se permission
Step 7 → mapRef.current.animateToRegion / fitToCoordinates
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Package install, API key बनाएँ और app.json में डालें।
Step 2 → <MapView> को flex:1 style और initialRegion दें (height न हो तो map नहीं दिखता)।
Step 3 → <Marker> से pin लगाएँ।
Step 4 → ref से animateToRegion/fitToCoordinates से camera घुमाएँ।
```

---

## 🟡 Real World Example
**Zomato/Swiggy order tracking:** map shows the restaurant marker, home marker, a `Polyline` route and a delivery-partner marker moving every few seconds (position updated from API). **Ola/Rapido** show nearby cabs as markers and animate the camera to the pickup point.

## 🟡 Real Example Hindi mein
**Swiggy tracking:** map पर restaurant और घर का marker, बीच में `Polyline` route और delivery partner का marker हर कुछ सेकंड में हिलता है। **Ola:** आसपास की cabs markers के रूप में।

---

## 💻 Code Example — Basic
```jsx
// MapBasic.jsx — map + 2 markers
import React from 'react';                                    // React
import { StyleSheet, View } from 'react-native';              // RN
import MapView, { Marker } from 'react-native-maps';          // map + marker

export default function MapBasic() {
  return (
    <View style={styles.container}>
      <MapView
        style={styles.map}                                    // IMPORTANT: size zaroori
        initialRegion={{                                      // shuruaati area
          latitude: 12.9716, longitude: 77.5946,              // Bengaluru
          latitudeDelta: 0.05, longitudeDelta: 0.05,          // zoom level (chhota = zyada zoom)
        }}
      >
        <Marker coordinate={{ latitude: 12.9716, longitude: 77.5946 }} title="Restaurant" description="Meghana Foods" />
        <Marker coordinate={{ latitude: 12.9784, longitude: 77.6408 }} title="Home" pinColor="green" />
      </MapView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },                                     // poori screen
  map: { ...StyleSheet.absoluteFillObject },                  // map poora fill
});
```

## 💻 Code Example — Advanced
```jsx
// TrackingMap.jsx — moving driver marker, polyline, fitToCoordinates, error-safe
import React, { useEffect, useRef, useState } from 'react';
import { View, StyleSheet, Platform } from 'react-native';
import MapView, { Marker, Polyline, PROVIDER_GOOGLE } from 'react-native-maps';

const RESTAURANT = { latitude: 12.9716, longitude: 77.5946 };
const HOME = { latitude: 12.9784, longitude: 77.6408 };

export default function TrackingMap({ driver }) {              // driver = {latitude, longitude} from API
  const mapRef = useRef(null);                                 // map ko control karne ke liye
  const [ready, setReady] = useState(false);                   // map load flag

  useEffect(() => {
    if (!ready || !mapRef.current) return;                     // map ready hone ka intezaar
    mapRef.current.fitToCoordinates([RESTAURANT, HOME, ...(driver ? [driver] : [])], {
      edgePadding: { top: 80, right: 60, bottom: 80, left: 60 }, // sab markers fit
      animated: true,                                          // smooth
    });
  }, [ready, driver?.latitude, driver?.longitude]);            // driver move ho to dobara

  return (
    <View style={{ flex: 1 }}>
      <MapView
        ref={mapRef}
        style={StyleSheet.absoluteFill}
        provider={Platform.OS === 'android' ? PROVIDER_GOOGLE : undefined} // Android = Google; iOS default Apple
        showsUserLocation                                      // blue dot (location permission chahiye)
        onMapReady={() => setReady(true)}                      // ready callback
        onError={(e) => console.warn('Map error', e)}          // error log
      >
        <Marker coordinate={RESTAURANT} title="Restaurant" />
        <Marker coordinate={HOME} title="You" pinColor="green" />
        {driver && <Marker coordinate={driver} title="Delivery partner" />}
        <Polyline coordinates={[RESTAURANT, ...(driver ? [driver] : []), HOME]} strokeWidth={4} strokeColor="#fc8019" />
      </MapView>
    </View>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Default provider | Google Maps (key must) | Apple Maps (no key) |
| Google on iOS | Optional, extra setup | `PROVIDER_GOOGLE` + pod config |
| API key | `android.config.googleMaps.apiKey` | `ios.config.googleMapsApiKey` (agar Google) |
| Map style | `customMapStyle` (Google) | Limited (Apple) |
| Marker custom view | `tracksViewChanges` perf issue | Smooth usually |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install react-native-maps
// app.json:
// { "expo": { "android": { "config": { "googleMaps": { "apiKey": "YOUR_KEY" } } } } }
// Expo Go me chalta hai; production build me key zaroori.
```
CLI way:
```jsx
// npm i react-native-maps ; cd ios && pod install
// AndroidManifest.xml <application> me:
// <meta-data android:name="com.google.android.geo.API_KEY" android:value="YOUR_KEY"/>
// iOS Apple Maps ke liye extra kuch nahi
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `MapView` ko height/flex na dena — blank screen.
✅ Correct: `style={{ flex: 1 }}` ya `absoluteFill`.

❌ Mistake 2: Android pe API key na dena — grey map.
✅ Correct: Maps SDK for Android enable + key config.

❌ Mistake 3: `region` ko controlled rakhna bina `onRegionChangeComplete` update kiye — map atak jata hai.
✅ Correct: `initialRegion` use karo.

❌ Mistake 4: Hazaaron markers — lag.
✅ Correct: clustering (`react-native-map-clustering`) ya visible markers.

❌ Mistake 5: API key code me public repo me commit.
✅ Correct: env/EAS secrets aur key restrictions.

---

## 🧠 Tricky Interview Question
`initialRegion` vs `region` me kya fark? Marker move karte time kaun sahi?

Answer: `initialRegion` sirf pehli baar; user pan kare to map apni state rakhta hai. `region` controlled hai — har update par aapko `onRegionChangeComplete` me state set karni padegi warna map wapas snap hota hai. Driver marker ki movement ke liye camera ko `animateToRegion`/`animateCamera` se chalao, aur marker ka `coordinate` state se.

---

## ⚫ Interview Questions + Answers
Q1: Google Maps vs Apple Maps provider?
A1: Android me Google; iOS me default Apple, `PROVIDER_GOOGLE` se Google (extra setup).

Q2: Marker performance?
A2: Custom marker view par `tracksViewChanges={false}`; clustering; image marker.

Q3: Route draw kaise?
A3: Directions API se polyline decode karke `<Polyline coordinates>`.

Q4: Map ko markers me fit?
A4: `fitToCoordinates` with `edgePadding`.

Q5: Expo Go me kyun chalta?
A5: Expo Go me react-native-maps bundled hai; production me API key config zaroori.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Delivery/cab tracking, store locator, location picker

❌ Avoid when:
- Sirf static map image chahiye (Static Maps API / image)
- Bahut heavy GIS — Mapbox (`@rnmapbox/maps`) better

---

## 📊 Visual Diagram
```
 ┌───────────────────────────┐
 │ MapView (native)          │
 │  📍Marker  ── Polyline ── 📍Marker │
 │  🛵 moving marker (state) │
 └──────────┬────────────────┘
   ref.animateToRegion / fitToCoordinates
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Region | Visible map area | दिखने वाला क्षेत्र |
| Marker | Pin on map | Map पर पिन |
| Polyline | Line along points | Route रेखा |
| Delta | Zoom span | Zoom का दायरा |
| Provider | Map engine | Map का इंजन |

---

## ⚡ 3-Line Summary
English: react-native-maps shows native maps with markers and routes.
Android needs a Google Maps API key; give MapView a size.
Use fitToCoordinates and cluster markers for performance.

Hindi: react-native-maps native map, marker और route दिखाता है।
Android पर Google Maps API key चाहिए और MapView को size देना ज़रूरी है।
Performance के लिए fitToCoordinates और clustering इस्तेमाल करें।

---

## ➡️ Next Topic
**97. Push Notifications — expo-notifications** — location के बाद user को notify करना।

---
