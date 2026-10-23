---

# Q236. MQTT vs HTTP — When to Use Each
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
You are designing an IoT system. When would you choose MQTT over HTTP, and when would HTTP be better? Give a concrete production example for each.

---

## 💡 Quick Concept (2 lines only)
MQTT = lightweight pub/sub for constrained devices with unreliable networks + real-time bidirectional needs. HTTP = heavier request/response, better for one-time commands, webhooks, and human-readable REST APIs.
हिंदी: MQTT छोटे devices के लिए, real-time bidirectional data के लिए best है। HTTP one-time requests, REST APIs, और webhooks के लिए।

---

## ✅ Answer / Solution

```javascript
// ============================================
// MQTT EXAMPLE — Temperature sensor streaming
// Use: continuous telemetry, low-power device
// ============================================

const mqtt = require('mqtt');

// Device connects ONCE — keeps connection alive
const client = mqtt.connect('mqtts://broker.myapp.com:8883', {
  clientId: 'sensor-device-001',
  username: 'device',
  password: process.env.DEVICE_TOKEN,
  keepalive: 60,          // send PINGREQ every 60s to keep alive
  clean: false,           // persistent session — no msg loss on reconnect
  reconnectPeriod: 5000,  // auto-reconnect every 5s
  will: {                 // Last Will — broker sends if device disconnects
    topic: 'devices/sensor-001/status',
    payload: JSON.stringify({ online: false }),
    qos: 1,
    retain: true
  }
});

// Publish every 10 seconds — tiny overhead (no HTTP header per request)
setInterval(() => {
  client.publish(
    'devices/sensor-001/temperature',    // topic
    JSON.stringify({ value: 23.5, unit: 'C', ts: Date.now() }),
    { qos: 1, retain: false },
    (err) => { if (err) console.error('Publish failed:', err); }
  );
}, 10000);

// MQTT overhead per message: ~2 bytes header + topic length
// vs HTTP: ~700 bytes headers per request!
// For 1000 devices × 6 publishes/min = 6000 req/min
// MQTT bandwidth: ~48KB/min | HTTP bandwidth: ~4.2MB/min
// MQTT wins by 87x on bandwidth!

// ============================================
// HTTP EXAMPLE — Send command to device once
// Use: non-real-time, human triggers, webhooks
// ============================================

const express = require('express');
const app = express();

// Operator clicks "Set threshold" in dashboard
// HTTP POST is perfect — happens rarely, needs confirmation
app.post('/api/devices/:deviceId/config', async (req, res) => {
  const { deviceId } = req.params;
  const { threshold, interval } = req.body;

  // Validate + store config
  await db.devices.update(
    { id: deviceId },
    { $set: { threshold, interval, updatedAt: new Date() } }
  );

  // If device is online → push via MQTT
  mqttClient.publish(
    `devices/${deviceId}/commands`,
    JSON.stringify({ action: 'setConfig', threshold, interval }),
    { qos: 1 }
  );

  res.json({ success: true, message: 'Config sent' });
  // HTTP response confirms the operation → great UX for dashboard
});

// ============================================
// DECISION TABLE
// ============================================

/*
Scenario                          | MQTT | HTTP
──────────────────────────────────┼──────┼──────
Continuous sensor telemetry       |  ✅  |  ❌
Low-power microcontroller (ESP32) |  ✅  |  ❌
Real-time bidirectional updates   |  ✅  |  ❌
10,000 concurrent devices         |  ✅  |  ❌
Unreliable cellular/WiFi network  |  ✅  |  ❌
Message delivery guarantee (QoS1) |  ✅  |  ❌
Fan-out: 1 msg → 1000 subscribers |  ✅  |  ❌
Webhook to external service       |  ❌  |  ✅
REST API for mobile app           |  ❌  |  ✅
One-time device registration      |  ❌  |  ✅
File/firmware download (OTA)      |  ❌  |  ✅
Human-readable API docs           |  ❌  |  ✅
Stateless microservice calls      |  ❌  |  ✅
*/
```

---

## 🔍 Why This Works (3 lines max)
MQTT uses a persistent TCP connection — after the initial handshake, each message adds only ~2 bytes overhead. HTTP creates a new TCP connection (or reuses keep-alive) per request with ~700 bytes of headers. For constrained devices sending data every few seconds, MQTT is dramatically more efficient in bandwidth, battery, and server connections.
हिंदी: MQTT एक persistent connection रखता है — हर message पर सिर्फ 2 bytes overhead। HTTP हर request पर 700+ bytes headers भेजता है।

---

## ⚡ Alternative / Comparison

```
Protocol    | Overhead | Direction      | QoS   | Best For
────────────┼──────────┼────────────────┼───────┼────────────────────
MQTT        | ~2 bytes | Bidirectional  | 0,1,2 | Continuous telemetry
HTTP/REST   | ~700B    | Request/Reply  | None  | One-off commands, API
CoAP        | ~4 bytes | Request/Reply  | 0,1,2 | Constrained + RESTful
WebSocket   | ~6 bytes | Bidirectional  | None  | Real-time dashboard
AMQP        | ~60 bytes| Bidirectional  | Yes   | Enterprise messaging

Rule of thumb:
→ Device sends data frequently (>1x/min) → MQTT
→ Human triggers an action once            → HTTP
→ Real-time browser dashboard              → WebSocket
→ Ultra-constrained (no TCP stack)         → CoAP
```

---

## ⚠️ Common Mistake

```
❌ Wrong: Using HTTP polling for real-time IoT data
  setInterval(() => fetch('/api/device/temperature'), 1000);
  // Creates 1 HTTP request/second × 10,000 devices = 10,000 req/sec
  // Each request: new connection + headers + auth = heavy

✅ Correct: MQTT subscription for real-time data
  client.subscribe('devices/+/temperature');
  client.on('message', (topic, msg) => updateDashboard(topic, msg));
  // One persistent connection per device
  // Push-based — no polling overhead

❌ Also Wrong: Using MQTT for file transfer (OTA firmware)
  // MQTT max message size is limited (broker-dependent, usually 256MB)
  // But 10MB firmware over MQTT on poor network = nightmare
✅ Correct: HTTP pre-signed URL for firmware download
  // Publish MQTT message with firmware URL → device downloads via HTTPS
```

---

## 🎯 Interview Tip (1 line)
At 5+ YOE level, say: "I use MQTT for device-to-cloud telemetry and cloud-to-device commands; HTTP for the management API, OTA URL delivery, and integrations with third-party services — they complement each other."

---

## 🔗 Related Questions
→ Q031 (MQTT vs CoAP) | Q034 (HTTP vs MQTT full analysis) | Q237 (QoS scenarios) | Q047 (Topic design)
