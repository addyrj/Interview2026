# MQTT Cheatsheet — Quick Revision
# 5+ YOE IoT Interview — Must Know Cold

---

## 🔌 Connection

```javascript
const mqtt = require('mqtt');

// Basic connect:
const client = mqtt.connect('mqtts://broker:8883', {
  clientId: 'device-001',          // unique per device
  username: 'user',
  password: 'pass',
  keepalive: 60,                   // PINGREQ every 60s
  clean: false,                    // persistent session
  reconnectPeriod: 5000,           // auto-reconnect (or 0 = manual)
  connectTimeout: 10000,
  // TLS:
  key:  fs.readFileSync('device.key'),
  cert: fs.readFileSync('device.crt'),
  ca:   fs.readFileSync('ca.crt'),
  rejectUnauthorized: true,        // ALWAYS true in production!
  // Last Will:
  will: {
    topic: 'devices/001/status',
    payload: JSON.stringify({ online: false }),
    qos: 1, retain: true
  }
});
```

---

## 📤 Publish

```javascript
// QoS 0 — fire and forget:
client.publish('topic/here', 'payload', { qos: 0 });

// QoS 1 — at least once (ACK):
client.publish('topic/here', JSON.stringify({ val: 23.5 }), { qos: 1 }, (err) => {
  if (err) console.error('Publish failed:', err);
});

// QoS 1 + Retained (new subscribers get this immediately):
client.publish('devices/001/status', JSON.stringify({ online: true }), {
  qos: 1,
  retain: true
});

// Clear retained message:
client.publish('devices/001/status', '', { retain: true });
```

---

## 📥 Subscribe

```javascript
// Single topic:
client.subscribe('devices/001/commands', { qos: 1 }, (err, granted) => {
  console.log('Granted QoS:', granted[0].qos);
});

// Wildcard + (single level):
client.subscribe('devices/+/temperature');  // matches devices/001/temperature

// Wildcard # (multi level):
client.subscribe('devices/#');             // matches everything under devices/

// Multiple topics:
client.subscribe(['topic1', 'topic2', 'topic3'], { qos: 1 });

// Shared subscription (load balance, MQTT 5.0 / some 3.x brokers):
client.subscribe('$share/workers/devices/+/telemetry');

// Handle messages:
client.on('message', (topic, payload, packet) => {
  const data = JSON.parse(payload.toString());
  console.log(`${topic}: ${JSON.stringify(data)}`);
});
```

---

## 🔄 Events

```javascript
client.on('connect',    (connack) => console.log('Connected'));
client.on('reconnect',  ()        => console.log('Reconnecting...'));
client.on('close',      ()        => console.log('Connection closed'));
client.on('disconnect', (packet)  => console.log('Broker sent DISCONNECT'));
client.on('offline',    ()        => console.log('Client is offline'));
client.on('error',      (err)     => console.error('Error:', err.message));
client.on('message',    (topic, payload, packet) => handleMessage(topic, payload));
client.on('packetsend', (packet)  => {});  // debug: every packet sent
client.on('packetreceive', (packet) => {}); // debug: every packet received
```

---

## 📊 QoS Reference

```
QoS | Name           | Delivery      | Overhead | Use Case
────┼────────────────┼───────────────┼──────────┼──────────────────────
  0 | At most once   | Fire+forget   | 1 msg    | High-freq metrics (1/sec)
  1 | At least once  | ACK required  | 2 msgs   | Events (may duplicate!)
  2 | Exactly once   | 4-way handsh. | 4 msgs   | Billing, financial

QoS downgrade: broker uses LOWER of publisher QoS and subscriber QoS
Publisher QoS 2 + Subscriber QoS 0 → subscriber receives at QoS 0!
```

---

## 📌 Topic Rules

```
VALID topics:
  devices/001/temperature         → specific device, specific metric
  sensors/factory-1/pressure      → hierarchical
  $SYS/broker/clients/connected   → broker system topics (read-only)

WILDCARDS (subscribe only, not publish):
  devices/+/temperature           → + = single level only
  devices/#                       → # = multi-level (must be last)
  +/+/temperature                 → multiple + allowed

RESERVED prefixes:
  $SYS/   → broker statistics (Mosquitto)
  $aws/   → AWS IoT system topics
  $share/ → shared subscriptions

BEST PRACTICES:
  ✅ {company}/{site}/{type}/{id}/{metric}  → hierarchical
  ✅ No leading slash (don't: /devices/001)
  ✅ No spaces (use - or _)
  ✅ Keep depth ≤ 6 levels
  ❌ Don't use # for high-volume subscriptions
```

---

## 🔑 Persistent Session

```
clean: false + stable clientId = persistent session

Broker stores:
  ✓ Subscriptions (re-activate on reconnect)
  ✓ QoS 1/2 messages received while offline (queued, delivered on reconnect)
  ✓ In-flight messages (QoS 1 unACKed)

clean: true = stateless session
  × No queuing, no subscription memory
  × Use for: sensors that don't need missed messages (stream data)
  ✓ Use clean: true for short-lived clients (one-off queries)
  ✓ Use clean: false for devices (always need missed commands)
```

---

## 🪦 Last Will and Testament

```javascript
// Set in connect options — broker publishes IF ungraceful disconnect:
will: {
  topic: 'devices/001/status',
  payload: JSON.stringify({ online: false, ts: Date.now() }),
  qos: 1,
  retain: true    // ← new subscribers see device is offline immediately
}

// On graceful disconnect: DOES NOT trigger LWT
client.end();  // sends DISCONNECT → LWT NOT sent

// On crash/network drop: DOES trigger LWT
// Kill process or pull network → broker publishes LWT after keepalive timeout

// Online status pattern (retained messages):
// On connect: publish { online: true, ts: Date.now() } with retain: true
// LWT:        { online: false } with retain: true
// Any new subscriber immediately knows device status!
```

---

## 🛡️ Security Setup

```javascript
// 1. TLS/SSL:
const client = mqtt.connect('mqtts://broker:8883', {
  key:  fs.readFileSync('/certs/device.key'),
  cert: fs.readFileSync('/certs/device.crt'),
  ca:   fs.readFileSync('/certs/root-ca.crt'),
  rejectUnauthorized: true,   // verify broker cert!
});

// 2. MQTT over WebSocket with auth:
const client = mqtt.connect('wss://broker:443/mqtt', {
  username: 'token',
  password: jwtToken,         // JWT as password
});

// 3. AWS IoT Core (cert-based):
const client = mqtt.connect('mqtts://ENDPOINT.iot.REGION.amazonaws.com:8883', {
  key:  fs.readFileSync('device.private.key'),
  cert: fs.readFileSync('device.cert.pem'),
  ca:   fs.readFileSync('AmazonRootCA1.pem'),
  clientId: 'device-001',
  rejectUnauthorized: true,
});
```

---

## 📈 MQTT 5.0 Key Features

```
1. Message Expiry:
   client.publish('topic', payload, { properties: { messageExpiryInterval: 300 } })
   // Broker drops message after 300s if not delivered

2. User Properties:
   client.publish('topic', payload, {
     properties: { userProperties: { source: 'factory-1', version: '2.0' } }
   })

3. Topic Alias (bandwidth optimization):
   // First message: include full topic + alias number
   // Subsequent: alias number only (saves bandwidth on long topic names)

4. Request/Response:
   client.publish('service/request', payload, {
     properties: {
       responseTopic: 'device-001/response',
       correlationData: Buffer.from('req-123')
     }
   })

5. Shared Subscriptions (load balance):
   client.subscribe('$share/workers/devices/+/telemetry')
   // Multiple workers each get different messages from the same topic
```

---

## 🔧 Debugging Tools

```
1. MQTT Explorer (GUI):
   → Visual pub/sub, topic tree, payload inspector
   → Best for development and debugging

2. mosquitto_sub (CLI):
   mosquitto_sub -h broker -t 'devices/#' -v
   mosquitto_sub -h broker -t 'devices/+/temperature' --retained-only

3. mosquitto_pub (CLI):
   mosquitto_pub -h broker -t 'devices/001/commands' -m '{"action":"restart"}'

4. mqtt-spy (advanced GUI):
   → Scripting, search, filters

5. Node.js debug:
   DEBUG=mqtt* node app.js    → verbose mqtt.js logging

6. Mosquitto logs (/var/log/mosquitto/mosquitto.log):
   → Connection attempts, auth failures, ACL denials

7. MQTT Load Test:
   mqttx bench sub -c 1000 -t 'bench/#' -q 1
   mqttx bench pub -c 100 -t 'bench/test' -q 1 -m '{"val":1}'
```

---

## ⚡ Key Numbers

```
Max message size:    Broker-dependent (Mosquitto default: 256MB, AWS IoT: 128KB)
Max topic length:    65535 bytes
Max clientId length: 23 bytes (MQTT 3.1) | no limit (MQTT 3.1.1+)
keepalive timeout:   1.5 × keepalive seconds (broker closes if no PINGREQ)
QoS 0 overhead:      2 bytes header
QoS 1 overhead:      2 bytes + PUBACK round trip
QoS 2 overhead:      4 message round trips
AWS IoT limits:      500 new connections/sec, 2000 pub/sec/connection
EMQX capacity:       100M+ concurrent connections on cluster
```
