# 93. Location (GPS)
# हिंदी में: Location — GPS और Geolocation
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**Location** in React Native means accessing the device's GPS/network location. Use `expo-location` (Expo) or `react-native-geolocation-service` (CLI). Two types: **Foreground** (app is open, shows location indicator in status bar) and **Background** (app is in background or closed — needs special permission and justified use case). Requires permissions declared in app config AND runtime request.

## 🔵 सरल परिभाषा (Hindi)
**Location** device का GPS/network location access करना है। Use: `expo-location` (Expo) या `react-native-geolocation-service` (CLI)। दो types: **Foreground** (app open है, status bar में location indicator) और **Background** (app background/closed में — special permission + justified use case चाहिए)। Permissions: app config में declare + runtime request — दोनों जरूरी।

---

## 🔴 Problem it Solves
```
USE CASES:
  ✅ Swiggy/Zomato: "Deliver to current location"
  ✅ Ola/Uber: Real-time driver + rider tracking
  ✅ Dunzo: Nearest delivery partner
  ✅ Google Maps clone: Current position, navigation
  ✅ Myntra: Show nearest store location

FOREGROUND LOCATION:
  User has app open → see their location on map
  Delivery address auto-fill from GPS
  "Find nearest restaurant" feature

BACKGROUND LOCATION:
  Ola tracking driver when app is minimized
  Geofencing: alert when near a store
  Fitness app: track route during run
  → Requires explicit justification + Apple/Google review
```

---

## 💻 Code Example — Expo

```tsx
import * as Location from 'expo-location';
import { useState, useEffect } from 'react';

// TYPE
type Coordinates = {
  latitude: number;
  longitude: number;
  accuracy: number | null;    // meters
  altitude: number | null;    // meters
  heading: number | null;     // degrees (0 = north)
  speed: number | null;       // m/s
};

export function useCurrentLocation() {
  const [location, setLocation] = useState<Coordinates | null>(null);
  const [address, setAddress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const getCurrentLocation = async () => {
    setLoading(true);
    setError(null);

    // STEP 1: Request permission
    const { status } = await Location.requestForegroundPermissionsAsync();
    // On Android: triggers permission dialog
    // On iOS: triggers permission dialog with NSLocationWhenInUseUsageDescription

    if (status !== 'granted') {
      setError('Location permission denied');
      setLoading(false);
      return;
    }

    try {
      // STEP 2: Get location
      const loc = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
        // Accuracy levels:
        // Lowest → Balanced → High → Highest → BestForNavigation
        // Higher accuracy = more battery usage + slower
        timeInterval: 5000,   // minimum time between updates (ms)
      });

      setLocation({
        latitude: loc.coords.latitude,
        longitude: loc.coords.longitude,
        accuracy: loc.coords.accuracy,
        altitude: loc.coords.altitude,
        heading: loc.coords.heading,
        speed: loc.coords.speed,
      });

      // STEP 3: Reverse geocode (lat/lng → address)
      const [reverseResult] = await Location.reverseGeocodeAsync({
        latitude: loc.coords.latitude,
        longitude: loc.coords.longitude,
      });

      if (reverseResult) {
        // Compose human-readable address
        const parts = [
          reverseResult.street,
          reverseResult.district,
          reverseResult.city,
          reverseResult.region,
          reverseResult.postalCode,
        ].filter(Boolean);

        setAddress(parts.join(', '));
        // e.g., "MG Road, Indiranagar, Bengaluru, Karnataka, 560038"
      }

    } catch (err) {
      setError('Failed to get location. Make sure GPS is enabled.');
    } finally {
      setLoading(false);
    }
  };

  return { location, address, error, loading, getCurrentLocation };
}

// ─── LIVE LOCATION TRACKING ──────────────────────────────────────────────────
export function useLocationTracking() {
  const [location, setLocation] = useState<Coordinates | null>(null);
  const [subscription, setSubscription] = useState<Location.LocationSubscription | null>(null);

  const startTracking = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') return;

    // Subscribe to location updates
    const sub = await Location.watchPositionAsync(
      {
        accuracy: Location.Accuracy.High,
        timeInterval: 3000,          // update every 3 seconds
        distanceInterval: 10,        // OR update every 10 meters (whichever first)
      },
      (loc) => {
        setLocation({
          latitude: loc.coords.latitude,
          longitude: loc.coords.longitude,
          accuracy: loc.coords.accuracy,
          altitude: loc.coords.altitude,
          heading: loc.coords.heading,
          speed: loc.coords.speed,
        });
      }
    );

    setSubscription(sub);
  };

  const stopTracking = () => {
    subscription?.remove();
    setSubscription(null);
  };

  // IMPORTANT: clean up on unmount!
  useEffect(() => {
    return () => {
      subscription?.remove();
    };
  }, [subscription]);

  return { location, startTracking, stopTracking, isTracking: !!subscription };
}
```

```tsx
// app.json — Expo permissions declaration
{
  "expo": {
    "plugins": [
      [
        "expo-location",
        {
          "locationAlwaysAndWhenInUsePermission":
            "Allow MyApp to use your location to deliver to your address.",
          "locationWhenInUsePermission":
            "Allow MyApp to use your location to show nearby restaurants.",
          "isIosBackgroundLocationEnabled": false,  // true only for background
          "isAndroidBackgroundLocationEnabled": false
        }
      ]
    ]
  }
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Foreground permission | `ACCESS_FINE_LOCATION` | `NSLocationWhenInUseUsageDescription` |
| Background permission | `ACCESS_BACKGROUND_LOCATION` | `NSLocationAlwaysAndWhenInUseUsageDescription` |
| Background restriction | Android 10+ asks separately | iOS 13+ asks "Always" separately |
| GPS accuracy | Same (hardware dependent) | Same |
| Mock location | Developer can mock (for testing) | Simulator can simulate location |

---

## 🟠 Expo vs CLI Difference

Expo way:
```bash
npx expo install expo-location
# Config in app.json under "plugins"
# Works in Development Build (not Expo Go for background)
```

CLI way:
```bash
npm install react-native-geolocation-service
# Android: add permissions to AndroidManifest.xml
# <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
# iOS: add to Info.plist:
# NSLocationWhenInUseUsageDescription
# NSLocationAlwaysAndWhenInUseUsageDescription (if background)
# pod install
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Not stopping location tracking (battery drain)
```tsx
// WRONG: starts tracking, never stops
useEffect(() => {
  Location.watchPositionAsync(..., callback);
}, []);

// CORRECT: always clean up subscription
useEffect(() => {
  let sub: Location.LocationSubscription;
  Location.watchPositionAsync(..., callback).then(s => { sub = s; });
  return () => sub?.remove();  // cleanup!
}, []);
```

❌ **Mistake 2:** Requesting background permission without justification
```
Background location:
- Apple will ask you to justify why you need "Always" access
- Common rejection: requesting "Always" when "When In Use" is sufficient
- Only request background if: real-time tracking, geofencing, fitness
```

❌ **Mistake 3:** Not handling GPS disabled
```tsx
// User has permission but GPS is off:
const providerStatus = await Location.getProviderStatusAsync();
if (!providerStatus.gpsAvailable) {
  // Prompt user to enable GPS in Settings
  Alert.alert('Enable GPS', 'Please enable GPS for location access');
  // Android: Location.enableNetworkProviderAsync() — prompts to enable
}
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between foreground and background location?**
A1: Foreground location: app is open and visible — location indicator shown in status bar. Requires `ACCESS_FINE_LOCATION` (Android) / `NSLocationWhenInUseUsageDescription` (iOS). Background location: app is minimized or screen is off — location updates continue. Requires separate `ACCESS_BACKGROUND_LOCATION` (Android 10+) / `NSLocationAlwaysAndWhenInUseUsageDescription` (iOS). App stores scrutinize background location closely — only approve if clearly justified (Ola, fitness tracking, delivery).

**Q2: What is `watchPositionAsync` vs `getCurrentPositionAsync`?**
A2: `getCurrentPositionAsync` — one-time location fetch. Good for: "deliver to my location" (single point needed). Returns a promise with coordinates. `watchPositionAsync` — continuous tracking, fires callback on each update. Good for: real-time driver tracking, turn-by-turn navigation, fitness apps. Always call `.remove()` on the returned subscription when done — otherwise GPS keeps running, draining battery.

**Q3: What is reverse geocoding?**
A3: Converting GPS coordinates (latitude, longitude) into a human-readable address (street, city, state). `Location.reverseGeocodeAsync({ latitude, longitude })` returns an array of address components. Forward geocoding: address → coordinates (`Location.geocodeAsync('MG Road, Bengaluru')`). Used in delivery apps: "Use my current location" → GPS coordinates → reverse geocoded address shown to user.

**Q4: Why might `getCurrentPositionAsync` return stale location?**
A4: On Android, `getCurrentPositionAsync` may return the last cached GPS fix if `maximumAge` is set. Set `accuracy: Location.Accuracy.High` and allow `timeInterval: 5000` for a fresh fix. On iOS, first call to CoreLocation may use cached location. Using `watchPositionAsync` with a short interval gives fresher locations. For most delivery address cases, the default accuracy is fine — high accuracy (GPS satellite) takes 5-10 seconds to lock.

---

## ⚡ 3-Line Summary
**English:**
1. Location requires two steps: declare permissions in `app.json`/`AndroidManifest`/`Info.plist`, then request runtime permission with `Location.requestForegroundPermissionsAsync()`.
2. `getCurrentPositionAsync` for one-time location; `watchPositionAsync` for continuous tracking — always call `.remove()` on the subscription in cleanup to stop GPS and save battery.
3. Reverse geocode with `Location.reverseGeocodeAsync({ latitude, longitude })` to convert GPS coordinates to human-readable addresses.

**Hindi:**
1. Location के लिए: app config में permissions declare करो, फिर runtime पर `requestForegroundPermissionsAsync()` से request।
2. One-time location: `getCurrentPositionAsync`। Continuous tracking: `watchPositionAsync` — cleanup में `.remove()` call जरूरी (battery drain रोको)।
3. GPS coordinates → readable address: `Location.reverseGeocodeAsync({ latitude, longitude })`।

---

## ➡️ Next Topic
**94. Push Notifications** — FCM, APNs, Expo Notifications।
