---

# Q238. Device Shadow / Digital Twin — What Is It?
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is a device shadow (digital twin)? Why is it needed in IoT? How does it work when a device is offline? Show the data structure and a real code example.

---

## 💡 Quick Concept (2 lines only)
Device shadow is a persistent JSON document in the cloud that mirrors the device's last known state — so apps can read/write device state even when the device is offline. Device syncs when it reconnects.
हिंदी: Device shadow cloud में device की last known state का JSON है — device offline हो तब भी app उससे interact कर सकता है। Reconnect पर device sync कर लेता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// DEVICE SHADOW STRUCTURE (AWS IoT)
// ============================================

/*
Shadow document has 3 sections:
{
  "state": {
    "reported": {          ← what the DEVICE says its current state is
      "temperature": 23.5,
      "fan": "off",
      "firmware": "v2.1.0"
    },
    "desired": {           ← what someone (app/user) WANTS the device to do
      "fan": "on",         ← dashboard said "turn fan on"
      "threshold": 25
    }
  },
  "delta": {               ← AUTO-COMPUTED by AWS: desired - reported
    "fan": "on",           ← device needs to act on this!
    "threshold": 25
  },
  "metadata": { ... },
  "version": 15,           ← increments on every update
  "timestamp": 1640000000
}
*/

// ============================================
// DEVICE SIDE — Report state + Act on desired
// ============================================

const awsIot = require('aws-iot-device-sdk');

const device = awsIot.thingShadow({
  keyPath:  '/certs/device.key',
  certPath: '/certs/device.crt',
  caPath:   '/certs/root-ca.crt',
  clientId: 'device-001',
  host:     process.env.AWS_IOT_ENDPOINT,
});

device.on('connect', () => {
  // Register to listen for shadow updates:
  device.register('device-001', {}, () => {
    // Report current state to cloud:
    const reported = {
      state: {
        reported: {
          temperature: readTemperature(),   // 23.5
          fan: getFanState(),               // 'off'
          firmware: '2.1.0',
          online: true
        }
      }
    };

    device.update('device-001', reported);
    console.log('Reported state to shadow');
  });
});

// When cloud has a "desired" state that differs from "reported":
// AWS auto-computes "delta" and publishes to device
device.on('delta', (thingName, stateObject) => {
  console.log('Shadow delta received:', stateObject.state);
  // stateObject.state = { fan: 'on', threshold: 25 }

  const delta = stateObject.state;

  // Act on each desired change:
  if (delta.fan !== undefined) {
    setFan(delta.fan);                    // physically turn fan on/off
    console.log(`Fan set to: ${delta.fan}`);
  }

  if (delta.threshold !== undefined) {
    setThreshold(delta.threshold);
    console.log(`Threshold set to: ${delta.threshold}°C`);
  }

  // Report NEW state back (close the delta):
  device.update('device-001', {
    state: {
      reported: {
        fan: delta.fan || getFanState(),
        threshold: delta.threshold || getThreshold()
      }
    }
  });
  // Shadow delta will now be empty — desired == reported ✅
});

// ============================================
// APP/BACKEND SIDE — Read + Update desired
// ============================================

const AWS = require('aws-sdk');
const iotData = new AWS.IotData({ endpoint: process.env.AWS_IOT_ENDPOINT });

// Dashboard: get current device state (works even if device offline!):
async function getDeviceState(deviceId) {
  const result = await iotData.getThingShadow({
    thingName: deviceId
  }).promise();

  const shadow = JSON.parse(result.payload);
  return shadow.state.reported;
  // Returns last known state — device may be offline
}

// User clicks "Turn fan ON" in dashboard:
async function setFanOn(deviceId) {
  const params = {
    thingName: deviceId,
    payload: JSON.stringify({
      state: {
        desired: {           // ← set desired, NOT reported
          fan: 'on'
        }
      }
    })
  };

  await iotData.updateThingShadow(params).promise();
  console.log('Desired state updated — device will receive when online');
  // If device is ONLINE: receives delta immediately, acts on it
  // If device is OFFLINE: shadow stores desired, device gets it on reconnect
}

// ============================================
// OFFLINE SCENARIO (Key Feature!)
// ============================================

/*
Timeline:
  9:00 AM  Device goes offline (network outage)
  9:30 AM  User: "Set fan to ON" → app updates desired.fan = 'on'
           Shadow: { desired: { fan: 'on' }, reported: { fan: 'off' } }
           delta: { fan: 'on' }  ← stored in cloud
  10:00 AM Device comes back online
           Device subscribes to delta topic
           AWS delivers: { fan: 'on' }
           Device turns fan on
           Device reports: { fan: 'on' }
           Delta is now empty (desired == reported) ✅

WITHOUT shadow: command would be lost during offline period!
```

---

## 🔍 Why This Works (3 lines max)
The shadow decouples the application from the device's connectivity status — apps always talk to the shadow (cloud), never directly to the device. The shadow uses a "desired vs reported" model: desired = intent, reported = reality, delta = what needs to change. On reconnect, the device gets the accumulated delta and catches up to the desired state.
हिंदी: Shadow app को device connectivity से decouple करता है। App shadow को update करता है, device reconnect पर delta लेकर sync करता है।

---

## ⚡ Alternative / Comparison

```
AWS IoT Device Shadow vs Azure IoT Device Twin:

Feature               | AWS IoT Shadow  | Azure IoT Twin
──────────────────────┼─────────────────┼────────────────
Section names         | reported/desired| reported/desired (same!)
Delta/difference      | delta (auto)    | properties.$version
Multiple shadows      | named shadows   | tags + properties
Query all devices     | Fleet Indexing  | IoT Hub query
Max document size     | 400KB           | 8KB (much smaller!)
Update event to device| $aws/.../delta  | twin updates notification
REST API              | IoT Data API    | IoT Hub direct method

Both use same concept — "desired vs reported" pattern is universal!

Self-implementation (if not using AWS/Azure):
{
  deviceId: "device-001",
  reported: { fan: "off", temp: 23.5, updatedAt: "2024-01-15T10:00:00Z" },
  desired:  { fan: "on",  updatedAt: "2024-01-15T10:30:00Z" },
  version:  15
}
// Compute delta on read: keys where desired !== reported
```

---

## ⚠️ Common Mistake

```
❌ Wrong: Using device shadow for real-time streaming telemetry
  // Updating shadow every 5 seconds with temperature readings
  // Shadow is for STATE, not telemetry!
  // Shadow has version + audit trail overhead — expensive for streaming

✅ Correct separation of concerns:
  Telemetry (frequent)  → MQTT topic → time-series DB
  State (configuration) → Device Shadow → queryable by dashboard
  Commands (one-time)   → MQTT command topic or IoT Jobs

❌ Wrong: Not reporting state after acting on delta
  device.on('delta', (name, obj) => {
    setFan(obj.state.fan);
    // ← Missing: device.update() to report new state
    // Delta stays open → AWS keeps re-delivering it!
  });

✅ Correct: Always close the delta by reporting new state
  device.on('delta', (name, obj) => {
    setFan(obj.state.fan);
    device.update(name, {
      state: { reported: { fan: obj.state.fan } }  // close the delta!
    });
  });
```

---

## 🎯 Interview Tip (1 line)
Say: "Device shadow is essential for offline-tolerant IoT — the app never needs to know if the device is online; it just sets the desired state, and the device catches up on reconnect. I've used this pattern for remote configuration of devices with intermittent connectivity."

---

## 🔗 Related Questions
→ Q019 (device shadow concept) | Q084 (AWS shadow CRUD) | Q148 (device twin vs shadow) | Q186 (offline IoT architecture)
