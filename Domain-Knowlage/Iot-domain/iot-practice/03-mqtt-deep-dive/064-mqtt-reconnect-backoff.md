---

# Q064. MQTT Reconnect with Exponential Backoff
# Category: MQTT Deep Dive
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement a production-grade MQTT client in Node.js with automatic reconnection using exponential backoff. Handle the case where broker is temporarily unavailable, and ensure no messages are lost during reconnect.

---

## 💡 Quick Concept (2 lines only)
Exponential backoff prevents "reconnect storm" — if 10,000 devices all retry every 5s simultaneously, they DDoS their own broker. Backoff spreads retry attempts + jitter randomizes them.
हिंदी: Exponential backoff reconnect storm रोकता है — 10,000 devices एक साथ retry न करें। Jitter randomize करता है ताकि सब एक time पर hit न करें।

---

## ✅ Answer / Solution

```javascript
// ============================================
// PRODUCTION MQTT CLIENT WITH BACKOFF
// ============================================

const mqtt = require('mqtt');
const EventEmitter = require('events');

class IoTMqttClient extends EventEmitter {
  constructor(options) {
    super();

    this.brokerUrl = options.brokerUrl;
    this.clientOptions = {
      clientId: options.clientId,
      username: options.username,
      password: options.password,
      key:      options.key,         // TLS private key
      cert:     options.cert,        // TLS certificate
      ca:       options.ca,          // CA certificate
      keepalive: 60,
      clean: false,                  // persistent session — broker queues missed msgs
      reconnectPeriod: 0,            // ← DISABLE built-in reconnect (we handle it)
      connectTimeout: 10000,
      rejectUnauthorized: true,
    };

    // Backoff config:
    this.backoff = {
      initial: 1000,        // 1 second first retry
      max: 60000,           // cap at 60 seconds
      multiplier: 2,        // double each time
      jitterFactor: 0.3,    // ±30% randomization
    };

    this.reconnectAttempts = 0;
    this.reconnectTimer = null;
    this.isConnected = false;
    this.messageBuffer = [];          // buffer messages while offline
    this.maxBufferSize = 1000;        // don't buffer more than 1000 msgs

    this.client = null;
  }

  connect() {
    console.log(`Connecting to ${this.brokerUrl}...`);
    this.client = mqtt.connect(this.brokerUrl, this.clientOptions);

    this.client.on('connect', (connack) => {
      console.log(`✅ Connected (attempt ${this.reconnectAttempts + 1})`);
      this.isConnected = true;
      this.reconnectAttempts = 0;   // reset counter on successful connect

      // Flush buffered messages:
      this._flushBuffer();

      this.emit('connected', connack);
    });

    this.client.on('message', (topic, payload, packet) => {
      this.emit('message', topic, payload, packet);
    });

    this.client.on('error', (err) => {
      console.error('MQTT error:', err.message);
      this.emit('error', err);
      // Don't reconnect here — 'close' event will fire next
    });

    this.client.on('offline', () => {
      console.log('🔴 Broker unreachable — offline mode');
      this.isConnected = false;
      this.emit('offline');
    });

    this.client.on('close', () => {
      console.log('🔌 Connection closed');
      this.isConnected = false;
      this.emit('disconnected');

      // Schedule reconnect with backoff:
      this._scheduleReconnect();
    });

    this.client.on('reconnect', () => {
      // This fires if reconnectPeriod > 0, but we disabled it
      // (We're handling reconnect manually)
    });
  }

  _scheduleReconnect() {
    if (this.reconnectTimer) return; // already scheduled

    this.reconnectAttempts++;

    // Exponential backoff with jitter:
    const base = Math.min(
      this.backoff.initial * Math.pow(this.backoff.multiplier, this.reconnectAttempts - 1),
      this.backoff.max
    );

    // Add jitter: ±30% random offset (prevents reconnect storm)
    const jitter = base * this.backoff.jitterFactor * (Math.random() * 2 - 1);
    const delay = Math.round(base + jitter);

    console.log(`⏳ Reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);
    // Attempt 1:  ~1s   (1000 × 2^0 = 1000)
    // Attempt 2:  ~2s   (1000 × 2^1 = 2000)
    // Attempt 3:  ~4s   (1000 × 2^2 = 4000)
    // Attempt 4:  ~8s   (1000 × 2^3 = 8000)
    // Attempt 5:  ~16s  (1000 × 2^4 = 16000)
    // Attempt 6:  ~32s  (1000 × 2^5 = 32000)
    // Attempt 7+: ~60s  (capped at max)

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      if (this.client) {
        this.client.end(true);  // force close old connection
      }
      this.connect();           // create new connection
    }, delay);
  }

  // Publish with offline buffering:
  publish(topic, payload, options = {}) {
    const defaults = { qos: 1, retain: false };
    const opts = { ...defaults, ...options };

    if (this.isConnected) {
      return this._publishDirect(topic, payload, opts);
    }

    // Buffer message for when we reconnect:
    if (this.messageBuffer.length < this.maxBufferSize) {
      this.messageBuffer.push({ topic, payload, opts, timestamp: Date.now() });
      console.log(`📦 Buffered message (${this.messageBuffer.length}/${this.maxBufferSize})`);
    } else {
      console.warn('⚠️ Buffer full — oldest message dropped');
      this.messageBuffer.shift(); // drop oldest
      this.messageBuffer.push({ topic, payload, opts, timestamp: Date.now() });
    }
  }

  _publishDirect(topic, payload, opts) {
    return new Promise((resolve, reject) => {
      this.client.publish(topic, payload, opts, (err) => {
        if (err) {
          console.error('Publish failed:', err);
          return reject(err);
        }
        resolve();
      });
    });
  }

  async _flushBuffer() {
    if (this.messageBuffer.length === 0) return;

    console.log(`📤 Flushing ${this.messageBuffer.length} buffered messages`);
    const messages = [...this.messageBuffer];
    this.messageBuffer = [];

    for (const msg of messages) {
      // Skip messages older than 5 minutes (stale data):
      if (Date.now() - msg.timestamp > 5 * 60 * 1000) {
        console.log('Dropped stale buffered message:', msg.topic);
        continue;
      }
      await this._publishDirect(msg.topic, msg.payload, msg.opts);
    }
    console.log('Buffer flushed ✅');
  }

  subscribe(topic, options = { qos: 1 }) {
    this.client.subscribe(topic, options, (err) => {
      if (err) console.error('Subscribe failed:', err);
      else console.log(`Subscribed to: ${topic}`);
    });
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.client) {
      this.client.end();
    }
  }
}

// ============================================
// USAGE EXAMPLE
// ============================================

const fs = require('fs');

const iotClient = new IoTMqttClient({
  brokerUrl: 'mqtts://broker.myapp.com:8883',
  clientId: `device-${process.env.DEVICE_ID}`,
  key:  fs.readFileSync('/certs/device.key'),
  cert: fs.readFileSync('/certs/device.crt'),
  ca:   fs.readFileSync('/certs/root-ca.crt'),
});

iotClient.on('connected', () => {
  iotClient.subscribe('devices/+/commands');
});

iotClient.on('message', (topic, payload) => {
  const cmd = JSON.parse(payload);
  handleCommand(topic, cmd);
});

iotClient.on('offline', () => {
  console.log('Operating in offline mode — messages will be buffered');
});

iotClient.connect();

// Publish sensor data every 10 seconds:
setInterval(() => {
  iotClient.publish(
    `devices/${process.env.DEVICE_ID}/temperature`,
    JSON.stringify({ value: 23.5, ts: Date.now() }),
    { qos: 1 }
  );
}, 10000);

// ============================================
// BACKOFF DELAY TABLE
// ============================================

/*
Attempt | Base (ms) | With ±30% jitter range
────────┼───────────┼────────────────────────
   1    |   1,000   | 700 – 1,300
   2    |   2,000   | 1,400 – 2,600
   3    |   4,000   | 2,800 – 5,200
   4    |   8,000   | 5,600 – 10,400
   5    |  16,000   | 11,200 – 20,800
   6    |  32,000   | 22,400 – 41,600
   7+   |  60,000   | 42,000 – 78,000 (capped)

Without jitter: 10,000 devices all retry at exactly same time → DDoS broker
With jitter: retries spread over a window → broker gets manageable load
*/
```

---

## 🔍 Why This Works (3 lines max)
Without backoff, a broker restart triggers simultaneous reconnects from all devices — a "thundering herd" problem. Exponential backoff gives the broker time to recover before each successive retry wave. Jitter (±30% random offset) ensures devices don't all retry at the exact same backoff interval.
हिंदी: Backoff broker को recover करने का time देता है। Jitter ensure करता है कि 10,000 devices एक exact time पर reconnect न करें।

---

## ⚡ Alternative / Comparison

```javascript
// Simpler version using mqtt.js built-in reconnect
// (Less control but works for small deployments):
const client = mqtt.connect('mqtts://broker', {
  reconnectPeriod: 5000,    // retry every 5s (no backoff — risky at scale!)
  connectTimeout: 10000,
  clean: false,
});

// mqtt.js built-in does NOT do exponential backoff
// For >100 devices: implement custom backoff as shown above

// Even simpler — just use reconnectPeriod for dev:
// {
//   reconnectPeriod: 1000  // fine for dev/test
// }
```

---

## ⚠️ Common Mistake

```javascript
// ❌ Wrong: Reconnecting on every error event
client.on('error', (err) => {
  client.reconnect();  // ERROR events fire for many reasons
  // auth errors, topic permission denied, etc.
  // These won't be fixed by reconnecting!
  // Results in infinite reconnect loop
});

// ✅ Correct: Only reconnect on 'close' event
client.on('close', () => {
  scheduleReconnect();  // connection dropped → reconnect is appropriate
});
client.on('error', (err) => {
  log.error('MQTT error:', err);  // just log it, close will follow if fatal
});

// ❌ Wrong: Clean session on reconnect for persistent devices
{
  clean: true   // loses all queued messages + subscriptions!
}

// ✅ Correct: persistent session for reliable delivery
{
  clean: false,  // broker holds queued QoS 1/2 msgs for offline device
  clientId: 'STABLE-device-001'  // stable ID required for persistent session
}
```

---

## 🎯 Interview Tip (1 line)
Say: "I always disable mqtt.js built-in reconnect and implement exponential backoff with jitter — at scale, the thundering herd from simultaneous reconnects can take down even a well-provisioned broker."

---

## 🔗 Related Questions
→ Q061 (basic MQTT connect) | Q067 (QoS code) | Q077 (10K devices) | Q191 (coding: MQTT auto-reconnect)
