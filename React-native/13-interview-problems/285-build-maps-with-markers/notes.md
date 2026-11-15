# 285. Interview Problem: Build a Map with Markers
# हिंदी में: Markers के साथ Map बनाओ
# Platform: Both ✅ (Android ✅ | iOS ✅)
# Difficulty: ⭐⭐⭐ Medium | Asked at: Swiggy, Zomato, Ola, Uber, Rapido

File: `MapScreen.jsx`.
Target: Expo SDK 52 with `react-native-maps` (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
Show a map, place a pin (marker) for every restaurant, and when the user taps a pin, zoom the camera to it and show its details in a card.

## 🔵 सरल परिभाषा (Hindi)
एक map दिखाओ, हर restaurant के लिए एक pin (marker) लगाओ, और user pin पर tap करे तो camera उस पर zoom करे और नीचे card में details दिखें।

---

## 🔴 Problem it Solves
Location-based apps (food, cabs, hotels) need users to see "what is near me". A list alone can not show distance and spread. A map gives instant spatial context.

## 🔴 यह क्यों बना? (Hindi)
Food, cab, hotel apps में user को "मेरे आसपास क्या है" देखना होता है। सिर्फ list से दूरी और फैलाव नहीं दिखता। Map से तुरंत जगह का अंदाज़ा मिलता है।

---

## 🔴 Problem Statement
Render a `MapView` centred on Delhi with 3 restaurant markers. Tapping a marker highlights it (colour change), animates the camera to it and shows a bottom card with its name.

## 💡 Approach
```
Data: [{ id, name, lat, lng }]
MapView (flex: 1, must have size!) + ref -> mapRef.animateToRegion(...)
Marker per item: coordinate, title, onPress, pinColor
state: selected -> highlight + bottom card
```

## 🟢 How it Works — Step by Step
```
Step 1 → MapView mounts with initialRegion (lat, lng, latitudeDelta, longitudeDelta)
Step 2 → Data array is mapped to <Marker key coordinate title />
Step 3 → onPress of a marker -> setSelected(r)
Step 4 → mapRef.current.animateToRegion(region, 400ms) zooms smoothly
Step 5 → Selected marker turns blue, bottom card shows the name
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → MapView initialRegion (lat, lng, delta) के साथ खुलता है
Step 2 → Data array से हर item के लिए <Marker> बनता है
Step 3 → Marker press -> setSelected(r)
Step 4 → mapRef.animateToRegion(...) से smooth zoom होता है
Step 5 → Selected marker नीला हो जाता है और नीचे card में नाम दिखता है
```

---

## 🟡 Real World Example
Swiggy / Zomato "Restaurants near you" map view, Ola / Uber showing nearby cabs, Rapido captain location, Airbnb-style listings on a map.

## 🟡 Real Example Hindi mein
Swiggy / Zomato का "आपके पास के restaurants" map view, Ola / Uber में आसपास की cabs, Rapido captain की location, Airbnb जैसी listings।

---

## 💻 Code Example — Basic
```jsx
import React from 'react';                                       // React
import { StyleSheet } from 'react-native';                       // styles
import MapView, { Marker } from 'react-native-maps';             // map + pin

export default function BasicMap() {
  return (
    <MapView
      style={StyleSheet.absoluteFill}                            // MapView needs a size, else invisible
      initialRegion={{ latitude: 28.6139, longitude: 77.209, latitudeDelta: 0.2, longitudeDelta: 0.2 }} // start view
    >
      {/* One pin with a title shown in the callout */}
      <Marker coordinate={{ latitude: 28.6139, longitude: 77.209 }} title="Connaught Place" />
    </MapView>
  );
}
```

## 💻 Code Example — Advanced
From `MapScreen.jsx` (selection + camera animation):
```jsx
const mapRef = useRef(null);                                     // access map methods
const [selected, setSelected] = useState(null);                  // tapped marker

const onSelect = (r) => {
  setSelected(r);                                                // remember
  mapRef.current?.animateToRegion(                               // smooth zoom
    { latitude: r.lat, longitude: r.lng, latitudeDelta: 0.05, longitudeDelta: 0.05 },
    400                                                          // duration ms
  );
};

<MapView ref={mapRef} style={styles.flex} initialRegion={...} showsUserLocation={false}>
  {RESTAURANTS.map((r) => (
    <Marker key={r.id} coordinate={{ latitude: r.lat, longitude: r.lng }}
            title={r.name} onPress={() => onSelect(r)}
            pinColor={selected?.id === r.id ? 'blue' : 'red'}>
      <Callout><Text>{r.name}</Text></Callout>
    </Marker>
  ))}
</MapView>
{selected && <View style={styles.card}><Text>{selected.name}</Text></View>}
```
Production notes: use `showsUserLocation` only after the location permission is granted; for 100+ markers cluster them (`react-native-map-clustering`); set `tracksViewChanges={false}` on custom-view markers for performance.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Map provider | Google Maps (API key needed in a dev/prod build) | Apple Maps by default, no key |
| Google on iOS | - | `provider={PROVIDER_GOOGLE}` + dev build + key |
| Expo Go | Has a built-in Google key for testing | Apple Maps works |
| Marker pin colour | `pinColor` works | `pinColor` works (Apple pin) |
| Permissions | `ACCESS_FINE_LOCATION` for user dot | `NSLocationWhenInUseUsageDescription` |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install react-native-maps
// app.json:
// { "expo": { "android": { "config": { "googleMaps": { "apiKey": "YOUR_KEY" } } } } }
// Needs a development / production build for your own key (Expo Go uses its own key)
```
CLI way:
```jsx
// npm i react-native-maps ; cd ios && pod install
// AndroidManifest.xml: <meta-data android:name="com.google.android.geo.API_KEY" android:value="YOUR_KEY"/>
// iOS Google Maps: add the GoogleMaps pod + AppDelegate key (see library docs)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: MapView without a size (blank screen).
✅ Correct: `style={{ flex: 1 }}` inside a parent with `flex: 1`.

❌ Mistake 2: Using `region` (controlled) and never updating it - the map can not move.
✅ Correct: Use `initialRegion` + `animateToRegion`.

❌ Mistake 3: Missing Google Maps API key on Android release build (grey map).
✅ Correct: Set it in app.json / manifest and restrict it in Google Cloud.

❌ Mistake 4: `key={index}` for markers.
✅ Correct: Stable ids.

---

## 🧠 Tricky Interview Question
The map shows grey tiles on Android but works on iOS. Why?

Answer: iOS uses Apple Maps (no key). Android uses Google Maps, which needs a valid API key with "Maps SDK for Android" enabled (and correct SHA-1 / package restrictions). A missing or restricted key gives a grey map.

---

## ⚫ Interview Questions + Answers
Q1: `region` vs `initialRegion`?
A1: `region` is controlled (you must update it on every change); `initialRegion` is only the starting view.

Q2: What do latitudeDelta / longitudeDelta mean?
A2: Visible span in degrees; smaller = more zoom.

Q3: How to fit all markers?
A3: `mapRef.current.fitToCoordinates(coords, { edgePadding })`.

Q4: How to show the user's location?
A4: Ask permission (`expo-location`), then `showsUserLocation`.

Q5: Many markers are slow, what do you do?
A5: Cluster, render only visible ones, `tracksViewChanges={false}`, avoid heavy custom views.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Location is the main decision factor (nearby, delivery tracking)

❌ Avoid when:
- A sorted list is enough; maps cost battery, data and API fees

---

## 📊 Visual Diagram
```
 ┌───────────────────────────┐
 │  MapView (flex:1)         │
 │      📍 Karims            │
 │            📍 Indian Accent│   tap pin ──► animateToRegion
 │   📍 Bukhara  (selected)  │               + setSelected
 │                           │
 │ ┌───────────────────────┐ │
 │ │ Bukhara   (card)      │ │
 │ └───────────────────────┘ │
 └───────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Marker | Pin on map | नक्शे का pin |
| Region | Visible area (lat/lng + delta) | दिखने वाला क्षेत्र |
| Callout | Bubble shown on pin tap | pin का popup |
| Latitude / Longitude | Coordinates | अक्षांश / देशांतर |
| API key | Google Maps access key | API कुंजी |

---

## ⚡ 3-Line Summary
English: `MapView` + one `Marker` per item; keep a ref to move the camera.
Store the selected marker in state to highlight it and show a card.
Android needs a Google Maps key; iOS uses Apple Maps.

Hindi: `MapView` + हर item के लिए एक `Marker`; camera घुमाने के लिए ref रखें।
Selected marker को state में रखकर highlight और card दिखाएँ।
Android को Google Maps key चाहिए; iOS में Apple Maps चलता है।

---

## ✅ What was verified
The file passes an esbuild JSX syntax check. The screen was also run under jsdom with a mocked `react-native-maps` only: tapping a marker called `animateToRegion` and showed the card. The real map, API keys, and tiles were not run (native module, no device).

---

## ➡️ Next Topic
286. Build Chat UI (WhatsApp style) — another screen built around `FlatList`.
