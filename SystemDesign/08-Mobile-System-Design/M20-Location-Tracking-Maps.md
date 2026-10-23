# M20. Location Tracking + Maps
# हिंदी में: Location Tracking + Maps — फ़ोन से सही और battery-बचाऊ तरीके से location लेना (GPS, Wi-Fi, mobile tower), permissions, सर्वर को updates भेजना, और नक़्शे पर rider/driver को smooth तरीके से चलते हुए दिखाना

---

## 🔵 Simple Definition (English)
Location features have two halves:
1. **Getting location on the device**:
   - Sources: GPS/GNSS (precise, power-hungry), Wi-Fi and cell towers (coarse, cheap), fused by **Android's Fused Location Provider** and **iOS Core Location**.
   - Modes: one-time, foreground continuous, background continuous (rides, deliveries), **significant-change** and **geofencing** (enter/exit region, e.g., "arrived at restaurant").
   - Controls: accuracy, `distanceFilter` and interval to balance precision and battery.
   - Permissions: foreground vs background ("Always"), and precise vs approximate (iOS 14+, Android 12+).
2. **Showing and using location**:
   - Map SDKs: `react-native-maps` (Google Maps / Apple Maps), **Mapbox/MapLibre**, Indian providers like **Mappls (MapmyIndia)** and **Ola Maps**.
   - Features: markers, polylines (routes), live-tracking marker **interpolation**, clustering, geocoding/reverse geocoding, place autocomplete, ETA and routing (server side), snap-to-road (map matching).
Backend pieces (geohash/H3 indexing, nearby search, dispatch) are covered in Topic 125 (Uber/Ola).

## 🔵 सरल परिभाषा (Hindi)
Location के दो हिस्से: (1) फ़ोन पर location लेना — GPS (सटीक पर battery खाऊ), Wi-Fi और mobile tower (मोटा अंदाज़ा, सस्ता), जिन्हें Android Fused Location Provider और iOS Core Location मिलाते हैं; तरीके — एक बार, foreground लगातार, background लगातार (ride/delivery), significant-change, geofence (जगह पर पहुँचना); accuracy, दूरी और समय के अंतराल से battery का संतुलन; permissions — foreground/background, सटीक/अंदाज़न।
(2) दिखाना — react-native-maps, Mapbox/MapLibre, Mappls, Ola Maps; markers, route lines, चलते marker को smooth बनाना (interpolation), पते से जगह और जगह से पता, ETA।

---

## 🔴 Problem it Solves
Location powers core flows: delivery addresses (Swiggy/Zomato/Blinkit), ride pickup and live tracking (Uber, Ola, Rapido), store locators, attendance and field force, safety sharing. Naive implementations fail:
- **Battery drain**: high-accuracy GPS every second, all day, gets a "This app is using significant battery" warning, uninstalls and OS restrictions.
- **Jumpy markers**: the rider icon teleports every 10 s and drifts through buildings (GPS noise in dense Indian streets).
- **Wrong addresses**: imprecise pins and poor geocoding for Indian addresses ("near Hanuman temple, 2nd cross") cause failed deliveries.
- **Permission rejection**: asking "Always allow" at first launch makes users deny, and background permission is rejected by store review without justification.
- **Fraud**: mock-location apps fake delivery or attendance.
- **Cost**: maps and geocoding API bills grow quickly at scale.

## 🔴 यह क्यों बना? (Hindi)
Location मुख्य flows चलाती है: delivery का पता (Swiggy/Zomato/Blinkit), ride pickup और live tracking (Uber, Ola, Rapido), field force की हाज़िरी। लापरवाह implementation से: हर सेकंड high-accuracy GPS = battery ख़त्म और ऐप हटाना; rider का icon हर 10 सेकंड कूदे और इमारतों से गुज़रे (भीड़ वाली गलियों में GPS noise); ग़लत pin और भारतीय पतों ("हनुमान मंदिर के पास, 2nd cross") की कमज़ोर geocoding = failed delivery; पहली बार में "Always allow" माँगना = मना; mock location से नक़ली delivery/हाज़िरी; और maps API का भारी बिल।

---

## 🟢 How it Works — Step by Step

### Accuracy vs battery

```
┌──────────────────────────┬────────────────┬────────────┬─────────────────────────────────────┐
│ Mode                     │ Typical acc.   │ Battery    │ Use                                 │
├──────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┤
│ GPS high accuracy, 1–5 s │ 3–10 m         │ High       │ Active trip/delivery navigation     │
│ Balanced (Wi-Fi + cell + │ 20–100 m       │ Medium     │ Nearby restaurants, city detection  │
│ occasional GPS)          │                │            │                                     │
│ Low power / passive      │ 100 m – km     │ Low        │ Region-level personalization        │
│ Significant change (iOS) │ ~500 m moves   │ Very low   │ Wake app on big moves               │
│ Geofencing               │ ~100 m+ radius │ Low        │ "Arrived at restaurant/customer"    │
└──────────────────────────┴────────────────┴────────────┴─────────────────────────────────────┘
Adaptive strategy (delivery partner):
  OFFLINE → no tracking
  ONLINE, idle → balanced, every 60 s or 100 m
  ASSIGNED, en route → high accuracy, every 5 s or 20 m
  NEAR destination → geofence trigger + high accuracy
  Stationary detected (speed ~0 for 2 min) → reduce frequency
  Low battery / power saver → reduce accuracy, inform user
```

### Permissions UX

```
1. Explain first (pre-permission screen): "Allow location to show restaurants near you"
2. Request FOREGROUND ("While using the app") at the moment of need (e.g., address selection)
3. Request BACKGROUND ("Allow all the time") ONLY for features that need it (partner tracking), separately,
   after foreground granted, with clear justification (Play requires a declaration + video; Apple review)
4. Handle approximate location (user chose not precise): show manual pin adjustment; request temporary
   precise (iOS) for checkout address
5. Denied → graceful fallback: manual address search / pincode; link to Settings
```

### Live tracking pipeline (partner app → customer app)

```
Partner phone: location every 5 s → buffer locally → batch upload every 10–15 s (or WebSocket stream)
   payload: [{lat, lng, accuracy, speed, bearing, ts}, ...]  ← filter: drop points with accuracy > 50 m
Backend: map-match/snap to road (optional), update rider position (Redis GEO / H3), compute ETA,
   publish to order channel (pub/sub)
Customer phone: receives position every ~5–10 s via WebSocket/SSE (M13/F13) or polling
   → ANIMATE marker from previous to new position over the interval (interpolation), rotate by bearing
   → never teleport; if gap > 60 s, show "Updating location…" instead of a stale marker
Maps cost: draw route polyline once (from server/directions API), not per update
```

### Smoothing & quality

```
- Discard low-accuracy points (accuracy > 50–100 m), duplicates, impossible jumps (> 150 km/h)
- Kalman/simple smoothing on device or server; snap-to-road via map matching
- Interpolate marker movement: linear over the update interval with bearing rotation
- Indian addresses: combine pin (lat/lng) + structured fields (house/flat, floor, landmark) + pincode;
  let users drag the pin; store "how to reach" notes; reverse geocode for suggestions only
```

### Maps rendering performance

```
- Limit markers (cluster when > ~100; e.g., supercluster), use custom marker images (not complex views)
  with tracksViewChanges={false} after first render
- Avoid re-rendering the whole map on each update; update only the moving marker (animated region/marker)
- Offline/low-data: cache tiles (Mapbox/MapLibre offline packs), static map images for history screens
- Choose SDK by cost & features: Google Maps (rich data, cost per load/API), Mapbox/MapLibre (custom styles,
  offline), Mappls/Ola Maps (India-focused, pricing), Apple Maps on iOS (free)
```

### Anti-fraud & privacy

```
Mock location detection: Android Location.isMock() (API 31+) / isFromMockProvider; developer options enabled;
  impossible speed; server-side cross-checks (cell/IP, GPS jumps)
Privacy: collect only while needed, show tracking status (notification/indicator), retention limits,
  share live location with customer only during active order, DPDP Act consent & purpose limitation
```

## 🟢 कैसे काम करता है? (Hindi)
1. Accuracy बनाम battery: active delivery पर high accuracy हर 5 सेकंड/20 मीटर; online पर खाली बैठे हों तो balanced हर 60 सेकंड; offline पर बंद; रुके हों तो कम; मंज़िल के पास geofence; battery कम हो तो accuracy घटाओ।
2. Permission: पहले समझाओ, फिर ज़रूरत के समय "ऐप इस्तेमाल करते समय"; "हमेशा" (background) सिर्फ़ partner tracking के लिए अलग से और कारण के साथ (Play declaration, Apple review); सटीक न दें तो pin खिसकाने का विकल्प; मना करें तो manual पता/pincode।
3. Live tracking: partner फ़ोन हर 5 सेकंड location लेकर 10–15 सेकंड में batch भेजे (ख़राब accuracy वाले points हटाओ) → सर्वर snap-to-road, ETA, pub/sub → customer ऐप WebSocket से पाकर marker को पिछली से नई जगह तक animate करे (कूदे नहीं), देर हो तो "location अपडेट हो रही है"।
4. भारतीय पते: pin + मकान/मंज़िल/landmark/pincode, यूज़र pin खिसका सके, "कैसे पहुँचें" नोट; map पर बहुत markers हों तो cluster, सिर्फ़ चलता marker बदलो, route line एक बार।
5. धोखा और निजता: mock location की पहचान (isMock), असंभव रफ़्तार की जाँच; सिर्फ़ ज़रूरत तक location, tracking की सूचना दिखाओ, customer को सिर्फ़ active order में, DPDP सहमति।

---

## 🟡 Real World Example

**Uber / Ola / Rapido** — driver apps stream GPS every few seconds during trips via foreground services, the backend matches to roads and computes ETAs, and rider apps animate the car smoothly with bearing rotation. In 2024 **Ola** moved from Google Maps to its own **Ola Maps**, citing large cost savings, a notable example of map API cost at Indian scale.

**Swiggy / Zomato / Zepto** — partner apps use adaptive tracking (more frequent on active orders) and geofences around restaurants and customers for auto "arrived" events. Customer apps show interpolated rider movement and live ETA, and address capture combines a draggable pin with landmarks and flat numbers.

**Google Maps location sharing / WhatsApp live location** — time-boxed, user-initiated sharing with clear indicators, which is a good privacy pattern.

**MapmyIndia (Mappls)** — India-focused maps and geocoding with detailed Indian addresses (including rural and pin-code-level data), used by government and enterprises as an alternative to global providers.

## 🟡 Real Example Hindi में
Uber/Ola/Rapido के driver ऐप trip के दौरान हर कुछ सेकंड GPS भेजते हैं, सर्वर road पर बैठाकर ETA निकालता है और rider ऐप गाड़ी को smooth घुमाते हुए दिखाता है; 2024 में Ola ने Google Maps छोड़कर अपना **Ola Maps** अपनाया और बड़ी बचत बताई।
Swiggy/Zomato/Zepto partner ऐप active order पर ज़्यादा बार location लेते हैं और restaurant/customer के पास geofence से "पहुँच गए" event; पता लेने में खिसकने वाला pin + landmark + flat नंबर; MapmyIndia (Mappls) भारतीय पतों के लिए मज़बूत विकल्प।

---

## 🟠 My Stack Example

### Adaptive tracking for a delivery partner (expo-location + task manager)
```ts
// src/platform/location.ts
import * as Location from 'expo-location';
import * as TaskManager from 'expo-task-manager';
const TASK = 'partner-location';

type Mode = 'IDLE' | 'EN_ROUTE' | 'NEAR';
const PROFILES: Record<Mode, Location.LocationTaskOptions> = {
  IDLE:     { accuracy: Location.Accuracy.Balanced, timeInterval: 60_000, distanceInterval: 100 },
  EN_ROUTE: { accuracy: Location.Accuracy.High, timeInterval: 5_000, distanceInterval: 20 },
  NEAR:     { accuracy: Location.Accuracy.BestForNavigation, timeInterval: 3_000, distanceInterval: 10 },
};

TaskManager.defineTask(TASK, async ({ data, error }) => {
  if (error) return;
  const pts = (data as { locations: Location.LocationObject[] }).locations
    .filter((l) => (l.coords.accuracy ?? 999) <= 50 && !l.mocked)            // drop noisy & mock points
    .map((l) => ({ lat: l.coords.latitude, lng: l.coords.longitude, acc: l.coords.accuracy, speed: l.coords.speed, bearing: l.coords.heading, ts: l.timestamp }));
  await locationBuffer.append(pts);                                          // MMKV/SQLite
  await locationBuffer.flushIfDue(15_000);                                   // batch POST every 15 s
});

export async function setTrackingMode(mode: Mode) {
  if (await Location.hasStartedLocationUpdatesAsync(TASK)) await Location.stopLocationUpdatesAsync(TASK);
  await Location.startLocationUpdatesAsync(TASK, {
    ...PROFILES[mode],
    foregroundService: { notificationTitle: 'Delivering order', notificationBody: 'Sharing live location with customer' },
    pausesUpdatesAutomatically: mode === 'IDLE', showsBackgroundLocationIndicator: true,
  });
}

// Geofence: auto "arrived" near restaurant/customer
export async function watchArrival(order: Order) {
  await Location.startGeofencingAsync('arrival', [
    { identifier: `rest-${order.id}`, latitude: order.restaurant.lat, longitude: order.restaurant.lng, radius: 100, notifyOnEnter: true },
    { identifier: `cust-${order.id}`, latitude: order.drop.lat, longitude: order.drop.lng, radius: 100, notifyOnEnter: true },
  ]);
}
```

### Backend ingestion (FastAPI + Redis GEO + pub/sub)
```python
@app.post("/partner/locations")
async def ingest(points: list[LocPoint], partner=Depends(current_partner)):
    good = [p for p in points if p.acc <= 50 and plausible_speed(partner.id, p)]   # server-side sanity/fraud checks
    if not good: return {"ok": True}
    last = good[-1]
    await redis.geoadd("partners:geo", (last.lng, last.lat, str(partner.id)))       # nearby search (Topic 125)
    await redis.hset(f"partner:{partner.id}:pos", mapping=last.model_dump())
    if order_id := await active_order(partner.id):
        eta = await eta_service.estimate(order_id, last)                           # route-aware ETA
        await redis.publish(f"order:{order_id}", json.dumps({"type": "rider.location", **last.model_dump(), "etaMin": eta}))
    return {"ok": True}
```

### Customer app: smooth animated marker (react-native-maps)
```tsx
import MapView, { Marker, AnimatedRegion, Polyline } from 'react-native-maps';

export function LiveTrackMap({ order }: { order: Order }) {
  const coord = useRef(new AnimatedRegion({ latitude: order.rider.lat, longitude: order.rider.lng, latitudeDelta: 0, longitudeDelta: 0 })).current;
  const [bearing, setBearing] = useState(0);
  const markerRef = useRef<any>(null);

  useEffect(() => realtime.subscribe(`order:${order.id}`, (e) => {
    if (e.type !== 'rider.location') return;
    setBearing(e.bearing ?? 0);
    coord.timing({ latitude: e.lat, longitude: e.lng, duration: 4500, useNativeDriver: false } as any).start();   // interpolate between updates
  }), [order.id]);

  return (
    <MapView style={{ flex: 1 }} initialRegion={{ latitude: order.drop.lat, longitude: order.drop.lng, latitudeDelta: 0.03, longitudeDelta: 0.03 }}>
      <Polyline coordinates={decodePolyline(order.routePolyline)} strokeWidth={4} />          {/* drawn once */}
      <Marker.Animated ref={markerRef} coordinate={coord as any} rotation={bearing} anchor={{ x: 0.5, y: 0.5 }}
                       image={require('@/assets/scooter.png')} tracksViewChanges={false} />
      <Marker coordinate={{ latitude: order.drop.lat, longitude: order.drop.lng }} title="You" />
    </MapView>
  );
}
```

### Address capture with draggable pin + structured fields
```tsx
<MapView onRegionChangeComplete={(r) => setPin({ lat: r.latitude, lng: r.longitude })} /* center pin overlay */ />
<Text>{reverseGeocoded?.formatted ?? 'Move the map to set your location'}</Text>
<TextInput placeholder="House / Flat no." /><TextInput placeholder="Floor (optional)" />
<TextInput placeholder="Landmark (e.g., near Hanuman Mandir)" /><TextInput placeholder="Pincode" keyboardType="number-pad" maxLength={6} />
// Save lat/lng from PIN (truth) + structured text; reverse geocode only to prefill suggestions
```

---

## ⚫ Interview Questions + Answers

**Q1: How would you implement battery-efficient location tracking for delivery partners?**
A1: Use an adaptive state machine: no tracking when offline, balanced accuracy at low frequency when online and idle, high accuracy every few seconds with distance filters during active deliveries, and geofences near pickup and drop to trigger arrival and higher precision. Run it in an Android foreground service and iOS background location mode with clear user-visible indicators. Detect stationary periods to reduce frequency, batch points and upload every 10–15 s, drop low-accuracy points, persist buffers for offline periods, and lower accuracy in low-battery or power-saver modes. Measure battery impact per hour of tracking.

**Q2: How do you show a smooth moving rider marker on the customer's map?**
A2: The partner app sends positions with bearing and timestamps every few seconds, and the backend filters or snaps them to roads and publishes them on the order's real-time channel. The customer app keeps the last position and, on each new point, animates the marker along the path from old to new over roughly the update interval (interpolation), rotating it by bearing. It never teleports, only re-renders the marker (not the whole map), draws the route polyline once, and if updates stop for too long shows a "location updating" state instead of a stale or wrong position.

**Q3: How should an app request location permissions?**
A3: Ask at the moment of need with a pre-permission explanation of the benefit. Request foreground ("While using") first, and request background ("Always") only for features that truly need it, as a separate step after foreground is granted, with store-required justifications (Play background location declaration, Apple review). Handle approximate-only grants (offer manual pin adjustment or a temporary precise request), provide fallbacks like manual address or pincode entry when denied, link to Settings for re-enabling, and re-check permissions on app foreground because users can revoke them anytime.

**Q4: How do you handle GPS noise and fraud?**
A4: On device, drop points with poor reported accuracy, duplicates and mock-provider points (`isMock`). On the server, reject impossible jumps or speeds, smooth with filters (Kalman or simple averaging), and map-match points to the road network. For fraud (fake delivery or attendance), combine mock-location detection, developer-options checks, attestation (Play Integrity), cross-checks with network or cell data and timing patterns, geofenced proof (photos with timestamps, OTP at handover), and anomaly detection, with penalties or manual review.

**Q5: How do you design address capture for Indian deliveries?**
A5: Use the map pin as the source of truth for coordinates, with the user dragging the map to set it precisely and reverse geocoding only to prefill a suggested address. Collect structured fields: house or flat number, floor, building or society, landmark, area and pincode, plus optional "how to reach" instructions and address labels (Home, Work). Validate pincode serviceability, save multiple addresses, and let delivery partners add corrections or notes that improve future deliveries. Geocoding Indian free-form text is unreliable, so precise pins plus landmarks matter most.

---

## 🔷 Trade-offs
✅ High-frequency GPS: precise live tracking — ❌ battery & data drain → adaptive modes.
✅ Server-side map matching & ETA: consistent, cheaper on device — ❌ backend compute & latency.
✅ Google Maps: rich POI data — ❌ cost at scale; Mapbox/MapLibre/Ola Maps/Mappls: cost/control — ❌ data coverage/feature differences.
✅ Background tracking: continuous updates — ❌ permission friction, store scrutiny, privacy obligations.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| GPS/GNSS | Satellite positioning | उपग्रह से location |
| Fused Location Provider | Android combined location | Android की मिली-जुली location |
| Accuracy radius | Error estimate in meters | ग़लती का दायरा |
| Distance filter | Min movement before update | न्यूनतम दूरी पर update |
| Geofence | Virtual boundary trigger | आभासी सीमा |
| Significant change | iOS low-power big-move updates | बड़ी हलचल पर update |
| Interpolation | Animate between points | बिंदुओं के बीच animate |
| Map matching | Snap points to roads | points को सड़क पर बैठाना |
| Reverse geocoding | Coordinates → address | जगह से पता |
| Mock location | Fake GPS provider | नक़ली location |

---

## ⚡ 3-Line Summary
**English:**
1. Balance accuracy and battery with adaptive modes (idle/en-route/near), distance filters, geofences, batching; foreground service/background mode with clear indicators.
2. Ask permissions at the moment of need (foreground first, background only if essential, handle approximate/denied) and protect privacy (purpose, retention, active-order-only sharing).
3. Live tracking: filter & snap points, publish via real-time channels, interpolate markers smoothly, draw routes once, detect mock locations, and design robust Indian address capture.

**Hindi:**
1. Accuracy और battery का संतुलन: adaptive modes, दूरी filter, geofence, batching; foreground service और साफ़ सूचना।
2. Permission ज़रूरत के समय (पहले foreground, background सिर्फ़ ज़रूरी हो तो), निजता का ध्यान।
3. Live tracking: points साफ़ करो, real-time से भेजो, marker smooth animate, route एक बार, mock location पकड़ो, भारतीय पते सही लो।

---

## ➡️ Next Topic Suggestion
**M21. Media Upload from Mobile (Chunked + Resumable)** — Delivery proofs, chat media, reels and documents all need uploading over flaky networks. Next: compressing on the device, presigned URLs, chunked and resumable uploads, background transfers and server-side processing.
