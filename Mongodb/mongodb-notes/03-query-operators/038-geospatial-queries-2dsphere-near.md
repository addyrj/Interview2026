# 38. Geospatial Queries (2dsphere, $near)
# हिंदी में: Geospatial Queries (2dsphere, $near)

---

## 🔵 Simple Definition (English)
**Geospatial queries** let MongoDB answer location questions: "which restaurants are within 3 km of me?", "is this point inside this delivery zone?". Locations are stored as **GeoJSON** (`{ type: "Point", coordinates: [longitude, latitude] }`) and indexed with a **2dsphere** index, which models the Earth as a sphere. Key operators: `$near`, `$nearSphere`, `$geoWithin`, `$geoIntersects`, and the aggregation stage `$geoNear`.

## 🔵 सरल परिभाषा (Hindi)
**Geospatial queries** से MongoDB location वाले सवालों का जवाब देता है: "मेरे 3 km के अंदर कौन से restaurants हैं?", "क्या यह point delivery zone के अंदर है?"। Location **GeoJSON** (`{ type: "Point", coordinates: [longitude, latitude] }`) में store होती है और **2dsphere** index से index होती है, जो पृथ्वी को गोले (sphere) की तरह मानता है। मुख्य operators: `$near`, `$nearSphere`, `$geoWithin`, `$geoIntersects` और aggregation stage `$geoNear`।

---

## 🔴 Problem it Solves
Without geo support you would compare latitude/longitude ranges manually (a bounding box), which is inaccurate near the poles and for real distances, and it cannot sort by "nearest first". Computing Haversine distance for every document in application code means a full collection scan. A 2dsphere index lets MongoDB walk only nearby cells and return results already sorted by distance.

## 🔴 यह क्यों बना? (Hindi)
Geo support के बिना latitude/longitude की ranges (bounding box) manually compare करनी पड़तीं, जो असली distance के लिए सही नहीं है और "सबसे पास वाला पहले" sort भी नहीं कर सकती। Application code में हर document का Haversine distance निकालना मतलब full collection scan। 2dsphere index MongoDB को सिर्फ पास की cells देखने देता है और results पहले से distance के हिसाब से sorted मिलते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Store location as GeoJSON Point: `{ type: "Point", coordinates: [lng, lat] }`. **Order is longitude first, then latitude** (opposite of what people say aloud).
Step 2 → Create the index: `db.places.createIndex({ loc: "2dsphere" })`.
Step 3 → Query nearby: `$near` with `$geometry` and optional `$maxDistance` / `$minDistance` (in **metres** for GeoJSON).
Step 4 → `$near` returns documents sorted nearest to farthest automatically. It **requires** a geospatial index (otherwise error `NoQueryExecutionPlans`, verified).
Step 5 → For "inside a shape" use `$geoWithin` (`$geometry` polygon, or `$centerSphere` with radius in **radians** = km / 6378.1). It does not sort and can work without an index.
Step 6 → When you also need the distance value or a pipeline, use `$geoNear` (must be the first stage) with `distanceField`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Location को GeoJSON Point में रखो: `{ type: "Point", coordinates: [lng, lat] }`। **पहले longitude, फिर latitude** आता है।
Step 2 → Index बनाओ: `db.places.createIndex({ loc: "2dsphere" })`।
Step 3 → पास की query: `$near` + `$geometry` और optional `$maxDistance` / `$minDistance` (GeoJSON में **metres**)।
Step 4 → `$near` results अपने-आप नज़दीक से दूर sorted देता है। इसे geospatial index **ज़रूरी** है (वरना error `NoQueryExecutionPlans`, verified)।
Step 5 → किसी shape के अंदर के लिए `$geoWithin` (polygon, या `$centerSphere` जिसमें radius **radians** में = km / 6378.1)। यह sort नहीं करता।
Step 6 → Distance value चाहिए या pipeline में, तो `$geoNear` (पहला stage होना चाहिए) और `distanceField`।

---

## 🟡 Real World Example
**Swiggy** shows "restaurants near you". Each restaurant document stores `loc` as a GeoJSON point. When you open the app at Delhi (77.2090, 28.6139), the backend runs `$near` with `$maxDistance: 5000` and gets restaurants within 5 km, nearest first. Delivery-zone checks use `$geoIntersects`/`$geoWithin` with a polygon per hub.

## 🟡 Real Example Hindi mein
**Swiggy** "आपके पास के restaurants" दिखाता है। हर restaurant document में `loc` GeoJSON point है। जब आप Delhi (77.2090, 28.6139) में app खोलते हैं, backend `$near` और `$maxDistance: 5000` चलाता है और 5 km के अंदर के restaurants नज़दीक से दूर मिलते हैं। Delivery zone check के लिए हर hub का polygon बनाकर `$geoWithin`/`$geoIntersects` use होता है।

---

## 💻 Code Example — Basic

```javascript
// mongosh (verified on MongoDB 8.0.4)
use geo_demo

// 1. Insert places as GeoJSON points: [longitude, latitude]
db.places.insertMany([
  { name: "Connaught Place",   loc: { type: "Point", coordinates: [77.2167, 28.6315] } },
  { name: "India Gate",        loc: { type: "Point", coordinates: [77.2295, 28.6129] } },
  { name: "Qutub Minar",       loc: { type: "Point", coordinates: [77.1855, 28.5245] } },
  { name: "Gurgaon Cyber Hub", loc: { type: "Point", coordinates: [77.0890, 28.4950] } }
])

// 2. $near WITHOUT a geo index fails
db.places.find({ loc: { $near: { $geometry: { type: "Point", coordinates: [77.2090, 28.6139] } } } })
// Error: NoQueryExecutionPlans (needs a geospatial index)

// 3. Create the 2dsphere index
db.places.createIndex({ loc: "2dsphere" })   // returns "loc_2dsphere"

// 4. Places within 5000 metres of Delhi centre, nearest first
db.places.find(
  { loc: { $near: { $geometry: { type: "Point", coordinates: [77.2090, 28.6139] }, $maxDistance: 5000 } } },
  { name: 1, _id: 0 }
)
// Output: [ { name: 'India Gate' }, { name: 'Connaught Place' } ]

// 5. $geoWithin with a circle: radius 10 km -> radians (10 / 6378.1)
db.places.find(
  { loc: { $geoWithin: { $centerSphere: [[77.2090, 28.6139], 10 / 6378.1] } } },
  { name: 1, _id: 0 }
)
// Output: India Gate, Connaught Place (Qutub Minar is 10.2 km away, excluded)
```

## 💻 Code Example — Advanced

```javascript
// $geoNear aggregation: get the DISTANCE in the result and combine with other stages
db.places.aggregate([
  {
    $geoNear: {                                   // must be the FIRST stage
      near: { type: "Point", coordinates: [77.2090, 28.6139] },
      distanceField: "dist",                      // output field with distance in metres
      spherical: true                             // use sphere maths
    }
  },
  { $project: { _id: 0, name: 1, dist: { $round: ["$dist", 0] } } }
])
// Output (verified):
// [ { name: 'India Gate', dist: 2006 },
//   { name: 'Connaught Place', dist: 2099 },
//   { name: 'Qutub Minar', dist: 10214 },
//   { name: 'Gurgaon Cyber Hub', dist: 17688 } ]

// Polygon check: is a point inside a delivery zone?
db.zones.insertOne({
  hub: "CP-hub",
  area: { type: "Polygon", coordinates: [[   // ring must be CLOSED: first point == last point
    [77.20, 28.62], [77.24, 28.62], [77.24, 28.65], [77.20, 28.65], [77.20, 28.62]
  ]] }
})
db.zones.createIndex({ area: "2dsphere" })
db.zones.find({ area: { $geoIntersects: { $geometry: { type: "Point", coordinates: [77.2167, 28.6315] } } } })
// Matches CP-hub because Connaught Place lies inside the polygon
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose schema with a 2dsphere index
const mongoose = require('mongoose');
const placeSchema = new mongoose.Schema({
  name: String,
  loc: {
    type: { type: String, enum: ['Point'], default: 'Point' }, // GeoJSON type
    coordinates: { type: [Number], required: true },            // [lng, lat]
  },
});
placeSchema.index({ loc: '2dsphere' }); // Mongoose creates it on startup (autoIndex)
const Place = mongoose.model('Place', placeSchema);

// GET /api/nearby?lng=77.209&lat=28.6139&km=5
app.get('/api/nearby', async (req, res) => {
  const lng = parseFloat(req.query.lng), lat = parseFloat(req.query.lat);
  if (Number.isNaN(lng) || Number.isNaN(lat)) return res.status(400).json({ error: 'lng/lat required' });
  const places = await Place.find({
    loc: { $near: { $geometry: { type: 'Point', coordinates: [lng, lat] },
                    $maxDistance: (parseFloat(req.query.km) || 5) * 1000 } }, // km -> metres
  }).limit(20);
  res.json(places);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Swapping latitude and longitude
```javascript
// Wrong — [lat, lng]; no error (77.2 is a valid latitude!) but the point lands in the Arctic, so queries silently miss it
{ type: "Point", coordinates: [28.6139, 77.2090] }
// Right — GeoJSON is [longitude, latitude]
{ type: "Point", coordinates: [77.2090, 28.6139] }
```

❌ Mistake 2: Using `$near` without a 2dsphere index, or mixing units
✅ Correct: create `{ loc: "2dsphere" }` first. `$maxDistance` is **metres** with GeoJSON but **radians** inside `$centerSphere` (km / 6378.1).

❌ Mistake 3: Polygon ring not closed — the first and last coordinates must be identical.

---

## 🧠 Tricky Interview Question

```javascript
db.places.find({ loc: { $near: { $geometry: P } } }).sort({ name: 1 })
```
Answer: The `sort({ name: 1 })` **overrides** the automatic distance ordering, so you lose "nearest first" (and it can no longer stop early). `$near` already sorts by distance; do not add a sort unless you truly want another order. Also remember `$near` cannot be used inside `$match` of an aggregation pipeline (use `$geoNear` stage as the first stage instead).

---

## ⚫ Interview Questions + Answers

Q1: What is the order of coordinates in GeoJSON?
A1: `[longitude, latitude]`. Legacy coordinate pairs also store `[x, y]`, so longitude comes first in both cases.

Q2: Difference between `2d` and `2dsphere` index?
A2: `2d` treats the plane as flat (legacy coordinate pairs, Euclidean distance). `2dsphere` supports GeoJSON on a sphere with correct Earth distances. Use `2dsphere` for real-world locations.

Q3: `$near` vs `$geoWithin`?
A3: `$near` needs an index, sorts by distance and supports `$maxDistance`. `$geoWithin` just checks containment inside a shape, returns unsorted results, and is cheaper when order does not matter.

Q4: When do you use `$geoNear`?
A4: When you need the computed distance in the output or need to chain further pipeline stages. It must be the first stage and needs a geo index.

Q5: What units are used?
A5: Metres for GeoJSON `$maxDistance`/`$minDistance` and `$geoNear` distances; radians for `$centerSphere` (km divided by 6378.1 for Earth's radius).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- "Nearby" search (restaurants, drivers, ATMs, stores)
- Geofencing / delivery-zone checks with polygons

❌ Avoid when:
- You only need exact city-name match (a normal indexed string field is simpler)
- Heavy GIS work (routing, road networks) — use a dedicated GIS system

---

## 📊 Visual Diagram
```
$near query: centre = (77.209, 28.6139), maxDistance = 5000 m

            . Gurgaon (17.7 km)  OUT
     * centre
   ( 5 km circle )
     CP (2.1 km) IN   India Gate (2.0 km) IN
                                   . Qutub (10.2 km) OUT

Result order: India Gate -> Connaught Place   (nearest first, automatic)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| GeoJSON | JSON format for geographic shapes | Geographic shapes का JSON format |
| 2dsphere | Index for spherical geometry | गोलाकार geometry का index |
| $near | Nearest-first search | नज़दीक से दूर search |
| $geoWithin | Inside a shape | Shape के अंदर |
| $geoNear | Pipeline stage that returns distances | Distance देने वाला pipeline stage |
| Radian | Angle unit (km / 6378.1) | कोण की इकाई |

---

## ⚡ 3-Line Summary
English:
1. Store `[lng, lat]` GeoJSON points and create a `2dsphere` index.
2. `$near` gives nearest-first results with `$maxDistance` in metres; `$geoWithin` checks containment; `$geoNear` returns distances.
3. Watch coordinate order, units (metres vs radians) and closed polygon rings.

Hindi:
1. `[lng, lat]` GeoJSON points रखो और `2dsphere` index बनाओ।
2. `$near` नज़दीक से दूर देता है (`$maxDistance` metres में); `$geoWithin` containment check; `$geoNear` distance देता है।
3. Coordinate order, units (metres बनाम radians) और बंद polygon ring का ध्यान रखो।

---

## ➡️ Next Topic
**39. distinct() and Query Patterns** — Getting unique values and common query patterns.
