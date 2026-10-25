# 157. Geolocation API
# हिंदी में: Geolocation API — Browser से User की Location लेना

---

## 🔵 Simple Definition (English)
The Geolocation API (`navigator.geolocation`) lets a web page ask the user for their current latitude and longitude. The browser asks for permission first, and the result comes back through callbacks (or a watch that keeps updating as the user moves).

## 🔵 सरल परिभाषा (Hindi)
Geolocation API (`navigator.geolocation`) web page को user से उसका current latitude और longitude माँगने देता है। Browser पहले permission माँगता है, और नतीजा callbacks के ज़रिए वापस आता है (या watch के ज़रिए, जो user के चलने पर लगातार update होता है)।

---

## 🔴 Problem it Solves
Before this API, a website could only guess the user's city from their IP address, which is often wrong on mobile networks and VPNs. Apps like Swiggy, Zomato and Ola need the exact location to show nearby restaurants or find a driver. Without a standard API, every app would need its own native mobile app just to read GPS.

## 🔴 यह क्यों बना? (Hindi)
इस API से पहले website सिर्फ IP address से city का अंदाज़ा लगा सकती थी, जो mobile networks और VPN पर अक्सर गलत होता है। Swiggy, Zomato और Ola जैसे apps को सटीक location चाहिए ताकि पास के restaurants दिखें या driver मिले। Standard API के बिना हर app को GPS पढ़ने के लिए अलग native app बनाना पड़ता।

---

## 🟢 How it Works — Step by Step

Step 1 → Page must be a secure context (`https://` or `localhost`), otherwise `navigator.geolocation` is not available
Step 2 → Call `navigator.geolocation.getCurrentPosition(success, error, options)` from a user action
Step 3 → Browser shows a permission prompt (allow / block) the first time
Step 4 → If allowed, `success(position)` runs with `position.coords.latitude`, `longitude`, `accuracy`
Step 5 → If denied or failed, `error(err)` runs; check `err.code` (1 = denied, 2 = unavailable, 3 = timeout)
Step 6 → For live tracking, use `watchPosition` and stop it with `clearWatch(id)`

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Page एक secure context (`https://` या `localhost`) में होना चाहिए, वरना `navigator.geolocation` उपलब्ध नहीं होगा
Step 2 → किसी user action से `navigator.geolocation.getCurrentPosition(success, error, options)` call करें
Step 3 → पहली बार browser permission prompt (allow / block) दिखाता है
Step 4 → Allow होने पर `success(position)` चलता है, जिसमें `position.coords.latitude`, `longitude`, `accuracy` होते हैं
Step 5 → Deny या fail होने पर `error(err)` चलता है; `err.code` check करें (1 = denied, 2 = unavailable, 3 = timeout)
Step 6 → Live tracking के लिए `watchPosition` use करें और `clearWatch(id)` से रोकें

---

## 🟡 Real World Example
Swiggy's "Deliver to my location" button: the user taps the button, the browser asks for location permission, and the app gets the coordinates. It then finds restaurants within a few kilometres. Ola's driver app uses `watchPosition` to send the driver's position every few seconds while the trip is running, and stops the watch when the trip ends.

## 🟡 Real Example Hindi mein
Swiggy का "Deliver to my location" button: user button दबाता है, browser location permission माँगता है, और app को coordinates मिलते हैं। फिर वह कुछ किलोमीटर के अंदर के restaurants ढूँढता है। Ola के driver app में trip चलने के दौरान `watchPosition` हर कुछ सेकंड में driver की position भेजता है, और trip खत्म होने पर watch बंद कर देता है।

---

## 💻 Code Example — Basic
> Browser-only: `navigator.geolocation` does not exist in Node.js. The runnable example is a self-contained HTML page.
> **How to run:** save as `geo-basic.html`, serve with `python3 -m http.server 8000`, open `http://localhost:8000/geo-basic.html` in a browser, and allow location when asked.

```html
<!-- geo-basic.html — full page, JS inside <script> -->
<!DOCTYPE html>
<!-- HTML5 doctype -->
<html lang="en">
<!-- Root element -->
<head>
  <!-- Head section -->
  <meta charset="UTF-8">
  <!-- UTF-8 for Hindi text -->
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <!-- Responsive on phones -->
  <title>Geo Basic</title>
  <!-- Tab title -->
</head>
<body>
  <!-- Visible content -->
  <h2>Find My Location (Swiggy style)</h2>
  <!-- Demo heading -->
  <button id="locBtn">Use my location</button>
  <!-- Button triggers the permission prompt -->
  <p id="out">Click the button to start.</p>
  <!-- Output paragraph -->
  <a id="map" href="#" target="_blank" hidden>Open in Google Maps</a>
  <!-- Map link hidden until we have coordinates -->

  <script>
    const out = document.getElementById("out");
    // Output element
    const mapLink = document.getElementById("map");
    // Map link element

    document.getElementById("locBtn").addEventListener("click", () => {
      // Runs when user clicks (required by most browsers)
      if (!navigator.geolocation) {
        // Check the API exists
        out.textContent = "Geolocation not supported.";
        // Tell the user
        return;
        // Stop here
      }

      out.textContent = "Asking for permission...";
      // Show waiting state

      navigator.geolocation.getCurrentPosition(
        // Ask for one position fix
        (position) => {
          // Success callback receives a GeolocationPosition
          const { latitude, longitude, accuracy } = position.coords;
          // Destructure the numbers we need
          out.textContent =
            `Lat ${latitude.toFixed(5)}, Lng ${longitude.toFixed(5)} (±${Math.round(accuracy)} m)`;
          // Show coordinates and accuracy radius in metres
          mapLink.href = `https://www.google.com/maps?q=${latitude},${longitude}`;
          // Build a Maps link with the coordinates (no API key needed)
          mapLink.hidden = false;
          // Show the link now that we have data
        },
        (err) => {
          // Error callback receives a GeolocationPositionError
          const reasons = { 1: "Permission denied", 2: "Position unavailable", 3: "Timed out" };
          // Map numeric error codes to readable text
          out.textContent = "Error: " + (reasons[err.code] || err.message);
          // Show the reason
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        // Options: use GPS if possible, wait 10 s max, do not use cached fix
      );
    });
  </script>
  <!-- End of script -->
</body>
<!-- End body -->
</html>
<!-- End document -->
```

## 💻 Code Example — Advanced
> The Haversine distance formula is pure math, so this part runs in Node.js. It is the server-side (or shared) logic a delivery app uses to check whether a user is inside a delivery radius. Save as `geo-advanced.js` and run with `node geo-advanced.js`.

```javascript
// geo-advanced.js — Haversine distance + delivery radius check (pure JS, runs in Node)

const EARTH_RADIUS_KM = 6371;
// Mean radius of the Earth in kilometres

// Convert degrees to radians (trig functions need radians)
function toRadians(deg) {
  // Takes a number in degrees
  return (deg * Math.PI) / 180;
  // Multiply by PI and divide by 180
}

// Great-circle distance between two lat/lng points, in kilometres
function haversineKm(a, b) {
  // a and b are objects like { lat, lng }
  const dLat = toRadians(b.lat - a.lat);
  // Difference in latitude in radians
  const dLng = toRadians(b.lng - a.lng);
  // Difference in longitude in radians
  const lat1 = toRadians(a.lat);
  // Start latitude in radians
  const lat2 = toRadians(b.lat);
  // End latitude in radians
  const h =
    Math.sin(dLat / 2) ** 2 +
    // Haversine part for latitude
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2;
  // Haversine part for longitude, combined
  return 2 * EARTH_RADIUS_KM * Math.asin(Math.sqrt(h));
  // Arc length on the sphere = radius times central angle
}

// Ignore fixes that are too inaccurate to trust (GPS drift)
function isUsableFix(fix, maxAccuracyM = 50) {
  // fix has lat, lng, accuracy (metres)
  return Number.isFinite(fix.lat) && Number.isFinite(fix.lng) && fix.accuracy <= maxAccuracyM;
  // Check values are real numbers and accurate enough
}

// Decide if a user is inside a restaurant's delivery radius
function canDeliver(restaurant, userFix, radiusKm = 5) {
  // restaurant has lat/lng, userFix is a GPS fix
  if (!isUsableFix(userFix)) {
    // Reject poor accuracy
    return { ok: false, reason: "Location not accurate enough, please retry" };
    // Explain the reason to the caller
  }
  const distance = haversineKm(restaurant, userFix);
  // Distance from restaurant to user in km
  return {
    ok: distance <= radiusKm,
    // True if within the delivery radius
    distanceKm: Number(distance.toFixed(2)),
    // Round to 2 decimals for display
    reason: distance <= radiusKm ? "Delivery available" : "Outside delivery area",
    // Human-friendly message
  };
}

// ---- demo data (Delhi points) ----
const restaurant = { name: "Spice Hub", lat: 28.6139, lng: 77.2090 };
// Restaurant in Connaught Place area
const userNear = { lat: 28.6200, lng: 77.2150, accuracy: 12 };
// User about 1 km away with accurate GPS
const userFar = { lat: 28.8000, lng: 77.1000, accuracy: 15 };
// User about 25 km away
const userNoisy = { lat: 28.6139, lng: 77.2090, accuracy: 400 };
// User at the same spot but with a bad GPS fix

console.log(canDeliver(restaurant, userNear));
// { ok: true, distanceKm: 0.8..., reason: "Delivery available" }
console.log(canDeliver(restaurant, userFar));
// { ok: false, distanceKm: ~23, reason: "Outside delivery area" }
console.log(canDeliver(restaurant, userNoisy));
// { ok: false, reason: "Location not accurate enough, please retry" }
```

---

## 🟠 Express.js Integration
The browser gets the coordinates, then sends them to the server. Express should **validate** the numbers (never trust the client) and run the distance check server-side, so the client cannot fake being inside the delivery zone.

```javascript
// server.js — npm i express, then node server.js
const express = require("express");
// Import Express
const app = express();
// Create the app
app.use(express.json());
// Parse JSON bodies
app.use(express.static("public"));
// Serve geo-basic.html from the public folder

const RESTAURANT = { lat: 28.6139, lng: 77.2090 };
// Server-side restaurant location (trusted source)

// Haversine helper (same math as the advanced example)
function distanceKm(a, b) {
  // Returns kilometres between two points
  const r = (d) => (d * Math.PI) / 180;
  // Degrees to radians helper
  const h = Math.sin(r(b.lat - a.lat) / 2) ** 2 +
    Math.cos(r(a.lat)) * Math.cos(r(b.lat)) * Math.sin(r(b.lng - a.lng) / 2) ** 2;
  // Haversine intermediate value
  return 2 * 6371 * Math.asin(Math.sqrt(h));
  // Distance in km
}

app.post("/api/check-delivery", (req, res) => {
  // Route receives the browser's coordinates
  const { lat, lng, accuracy } = req.body;
  // Read fields sent by the browser
  if (![lat, lng].every(Number.isFinite) || lat < -90 || lat > 90 || lng < -180 || lng > 180) {
    // Validate numbers and valid lat/lng ranges
    return res.status(400).json({ error: "Invalid coordinates" });
    // Reject bad input with 400
  }
  const km = distanceKm(RESTAURANT, { lat, lng });
  // Compute distance on the server
  res.json({ deliverable: km <= 5, distanceKm: Number(km.toFixed(2)), accuracy });
  // Respond with the decision
});

app.listen(3000, () => console.log("Server on http://localhost:3000"));
// Start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Reading the coordinates synchronously, as if `getCurrentPosition` returns them.
✅ Correct: It is asynchronous. The data only exists inside the success callback (or after a Promise wrapper).

```javascript
// Wrong — position is still null when logged
let position = null;
navigator.geolocation.getCurrentPosition((p) => { position = p; });
console.log(position.coords.latitude); // TypeError: Cannot read properties of null

// Right — use the data inside the callback
navigator.geolocation.getCurrentPosition((p) => {
  console.log(p.coords.latitude); // runs after the browser has the fix
});
```

❌ Mistake 2: Forgetting to handle denial, so the app just hangs.
✅ Correct: Always pass an error callback and handle `err.code === 1`.

```javascript
// Wrong — no error handler
navigator.geolocation.getCurrentPosition(onSuccess);

// Right — explain the failure to the user
navigator.geolocation.getCurrentPosition(onSuccess, (err) => {
  if (err.code === 1) showMessage("Please allow location to see nearby restaurants");
  else showMessage("Could not get location: " + err.message);
});
```

❌ Mistake 3: Calling `watchPosition` and never calling `clearWatch`, which drains the battery.
✅ Correct: Save the id returned by `watchPosition` and call `clearWatch(id)` when the screen closes.

---

## 🧠 Tricky Interview Question
What will be printed (in a browser console)? Assume the user allows location.

```javascript
// Tricky Geolocation code
let lat = null;
// Variable to hold the latitude

navigator.geolocation.getCurrentPosition((pos) => {
  // Success callback
  lat = pos.coords.latitude;
  // Store the value when the callback runs
});

console.log("Latitude is:", lat);
// Printed immediately after the call
```

Answer: It prints `Latitude is: null`. `getCurrentPosition` is asynchronous: it returns immediately and the success callback runs later, after the browser has a fix (or after the user answers the prompt). The `console.log` on the last line runs before that, so `lat` is still `null`. To use the value, read it inside the callback or wrap the call in a Promise and `await` it.

---

## ⚫ Interview Questions + Answers

Q1: What are the three arguments of `getCurrentPosition`?
A1: `success` callback, `error` callback (optional but recommended), and an `options` object with `enableHighAccuracy`, `timeout` and `maximumAge`.

Q2: What do the error codes mean?
A2: `1` = PERMISSION_DENIED, `2` = POSITION_UNAVAILABLE (no GPS or network signal), `3` = TIMEOUT.

Q3: What is the difference between `getCurrentPosition` and `watchPosition`?
A3: `getCurrentPosition` asks for one fix. `watchPosition` calls the success callback again and again as the device moves, and returns an id for `clearWatch`.

Q4: Can you trust the location sent from the browser?
A4: Not fully. Users can fake browser coordinates. The server should validate ranges and make sensitive decisions, or verify with other signals.

Q5: Why does `enableHighAccuracy: true` matter?
A5: It asks the device to use GPS instead of Wi-Fi or cell towers. It is more accurate but uses more battery and may take longer.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need the user's real position for maps, delivery, ride-hailing or "nearby" search
- The user has a clear reason to share location and clicks a button to do it
- You can handle denial and timeouts gracefully

❌ Avoid when:
- You only need the city (use IP-based lookup or let the user type it)
- You ask for location on page load with no explanation (users will block it)
- You are running pure server-side code with no device (Node.js has no GPS)

---

## 📊 Visual Diagram
```
User click
   |
   v
getCurrentPosition(success, error, options)
   |
   v
[ Browser asks: "Allow location?" ]
   |                 |
 Allow              Block
   |                 |
   v                 v
success(pos)      error(err)  -> err.code: 1 denied | 2 unavailable | 3 timeout
   |
   v
pos.coords = { latitude, longitude, accuracy, ... }
   |
   v
POST coordinates to server -> server checks distance (Haversine)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| navigator.geolocation | Entry point for location data | Location data का entry point |
| Coordinates | Latitude and longitude of a point | Latitude और longitude |
| accuracy | Radius of error, in metres | गलती की सीमा (मीटर में) |
| watchPosition | Keeps reporting position as the device moves | चलने के साथ position update करता है |
| clearWatch | Stops a watchPosition | watchPosition को बंद करता है |
| Haversine | Formula for distance on a sphere | गोले पर दूरी निकालने का formula |
| PERMISSION_DENIED | Error code 1, user said no | Error code 1, user ने मना किया |

---

## ⚡ 3-Line Summary
English: The Geolocation API gives latitude and longitude after the user grants permission.
English: It is asynchronous, so read the values in the callbacks and always handle errors (code 1, 2, 3).
English: Validate coordinates on the server and use `clearWatch` to stop live tracking.
Hindi: Geolocation API user की permission के बाद latitude और longitude देता है।
Hindi: यह asynchronous है, इसलिए values callbacks में पढ़ें और errors (code 1, 2, 3) handle करें।
Hindi: Server पर coordinates validate करें और live tracking बंद करने के लिए `clearWatch` use करें।

---

## ➡️ Next Topic
158. localStorage + sessionStorage: once you know how the browser asks for sensitive data, the next question is where to keep small data on the client. Storage APIs are the next step, and they are often asked together with cookies in interviews.
