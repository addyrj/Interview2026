---

# Q237. MQTT QoS 0, 1, 2 — Explain with Real Scenario
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Explain MQTT Quality of Service levels 0, 1, and 2. For each, give a real IoT scenario where you would use it and why. What are the tradeoffs?

---

## 💡 Quick Concept (2 lines only)
QoS 0 = at most once (fire and forget), QoS 1 = at least once (may duplicate), QoS 2 = exactly once (guaranteed, slowest). Choose based on: how bad is data loss vs how bad is a duplicate.
हिंदी: QoS 0 = forget, QoS 1 = at least once (duplicate possible), QoS 2 = exactly once (guarantee)। Data loss vs duplicate — इसी tradeoff के हिसाब से choose करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// QoS 0 — AT MOST ONCE (Fire and Forget)
// ============================================
// No acknowledgment, no retry
// Message may be lost if network drops
// FASTEST — zero overhead
// Use when: data loss is acceptable (next reading arrives soon anyway)
// Real scenario: CPU temperature from server — if one reading drops,
//   the next one arrives in 1 second anyway

const mqtt = require('mqtt');
const client = mqtt.connect('mqtt://broker.myapp.com');

// Scenario: Publish CPU metrics every 1 second
// QoS 0 — if one message lost, next arrives in 1 second = fine
client.publish(
  'servers/srv-001/cpu',
  JSON.stringify({ usage: 73.2, ts: Date.now() }),
  { qos: 0 }    // ← no ACK, no retry
);

// Message flow QoS 0:
//  Publisher ──PUBLISH──► Broker ──PUBLISH──► Subscriber
//  (no ACK in either direction)

// ============================================
// QoS 1 — AT LEAST ONCE (Acknowledged)
// ============================================
// Broker sends PUBACK to publisher
// Publisher retries if no PUBACK received
// Message COULD be delivered more than once (duplicate!)
// Use when: cannot lose a message, but can handle duplicate
// Real scenario: door open/close event — you must not miss it,
//   but receiving "door opened" twice is acceptable (idempotent)

client.publish(
  'building/door-001/event',
  JSON.stringify({ event: 'opened', ts: Date.now() }),
  { qos: 1 },    // ← broker must send PUBACK
  (err) => {
    if (err) console.error('QoS 1 publish failed:', err);
  }
);

// Message flow QoS 1:
//  Publisher ──PUBLISH──► Broker   ← (broker stores msg)
//  Publisher ◄──PUBACK──  Broker   ← (broker sends ACK)
//  Publisher deletes from buffer
//  Broker ──PUBLISH──► Subscriber
//  Broker ◄──PUBACK──  Subscriber
//
// If PUBACK lost:
//  Publisher ──PUBLISH (DUP=1)──► Broker  ← retries with DUP flag
//  Subscriber may receive msg twice!

// Handle duplicates on subscriber side:
const seen = new Map();  // message deduplication
client.on('message', (topic, payload) => {
  const msg = JSON.parse(payload);
  const msgId = `${topic}:${msg.ts}`;  // unique ID using timestamp

  if (seen.has(msgId)) {
    console.log('Duplicate message ignored:', msgId);
    return;
  }
  seen.set(msgId, true);

  // process message...
  processEvent(msg);

  // Clean old entries (keep last 5 min)
  const cutoff = Date.now() - 5 * 60 * 1000;
  for (const [key] of seen) {
    if (parseInt(key.split(':')[1]) < cutoff) seen.delete(key);
  }
});

// ============================================
// QoS 2 — EXACTLY ONCE (4-way handshake)
// ============================================
// 4-way handshake: PUBLISH → PUBREC → PUBREL → PUBCOMP
// Guaranteed delivery — exactly once
// SLOWEST — 4 messages per publish
// Use when: duplicate is a real problem (billing, transactions)
// Real scenario: meter reading for billing — receiving "usage: 100 kWh"
//   twice would bill customer double!

client.publish(
  'meters/meter-001/reading',
  JSON.stringify({ kWh: 1234.56, ts: Date.now(), readingId: 'R-2024-001' }),
  { qos: 2 }    // ← exactly once delivery
);

// Message flow QoS 2:
//  Pub ──PUBLISH──► Broker   ← Broker stores msg with packetId
//  Pub ◄──PUBREC── Broker    ← "I received it, don't resend"
//  Pub ──PUBREL──► Broker    ← "OK, I'll stop tracking this"
//  Pub ◄──PUBCOMP── Broker   ← "Done, message delivered"
//
//  Then: Broker ──QoS2 flow──► Subscriber

// ============================================
// QUICK COMPARISON OUTPUT
// ============================================

/*
Scenario                     | Best QoS | Why
─────────────────────────────┼──────────┼─────────────────────────────
CPU/RAM metrics (1s interval) |   0      | Loss OK — next in 1 second
Video stream frame            |   0      | Loss OK — stale frame anyway
Door open/close event         |   1      | Must not miss, dup is OK
Alert: temperature > 80°C     |   1      | Must receive, dup = extra alert OK
Billing meter reading         |   2      | Dup = double bill = bad
Payment/financial command      |   2      | Exactly once is critical
Firmware update trigger        |   1      | Must receive, idempotent OTA OK
Device registration            |   2      | Register twice = conflict
*/

// ============================================
// LATENCY + OVERHEAD COMPARISON
// ============================================

/*
QoS | Messages | Round trips | Latency  | Use
────┼──────────┼─────────────┼──────────┼──────────
  0 | 1        | 0           | ~10ms    | Streaming
  1 | 2        | 1           | ~20ms    | Events
  2 | 4        | 2           | ~40ms    | Billing
*/
```

---

## 🔍 Why This Works (3 lines max)
QoS is a contract between publisher, broker, and subscriber. The broker queues messages (for offline subscribers) only at QoS 1 and 2 — QoS 0 messages to offline subscribers are simply dropped. Most IoT systems use QoS 1 as the default because losses are unacceptable but exact-once overhead is too high.
हिंदी: QoS broker, publisher, subscriber के बीच delivery guarantee है। QoS 1 most common है — loss नहीं होता, और duplicate को application level पर handle करते हैं।

---

## ⚡ Alternative / Comparison

```
QoS 1 with application-level deduplication = practical "exactly once":
→ Add msgId (UUID or timestamp) to every message payload
→ Subscriber tracks last N message IDs (Redis SET with TTL)
→ On duplicate arrival → skip processing
→ This gives QoS-2-like semantics with QoS-1 speed!

// Redis-based deduplication:
const dedup = async (msgId) => {
  const key = `dedup:${msgId}`;
  const result = await redis.set(key, '1', 'NX', 'EX', 300); // 5 min TTL
  return result === 'OK'; // true = first time, false = duplicate
};
```

---

## ⚠️ Common Mistake

```
❌ Wrong: Using QoS 2 for everything "to be safe"
  // QoS 2 = 4 network roundtrips per message
  // 1000 sensors × 6 msg/min × 4 roundtrips = 24,000 network ops/min
  // At QoS 1: only 12,000 — 2x more efficient

✅ Correct: Choose QoS based on data criticality
  Streaming data (frequent, low value)  → QoS 0
  Events (must receive, dup OK)         → QoS 1 + dedup in code
  Financial/billing (zero duplicates)   → QoS 2

❌ Also Wrong: Thinking QoS 1 means "no duplicates"
  → QoS 1 = AT LEAST ONCE → duplicates ARE possible!
  → Always build idempotent handlers for QoS 1

❌ Also Wrong: QoS only set on publisher side
  → Both publisher AND subscriber set QoS
  → Broker uses the LOWER of the two (downgrade)
  → If publisher sends QoS 2 but subscriber subscribes QoS 0
    → broker delivers at QoS 0 to that subscriber!
```

---

## 🎯 Interview Tip (1 line)
Say: "I default to QoS 1 with application-level deduplication — it gives near-exactly-once semantics at QoS-1 speed; I only use QoS 2 when the protocol layer must guarantee it (billing, financial commands)."

---

## 🔗 Related Questions
→ Q006 (QoS output question) | Q062 (QoS code implementation) | Q205 (message deduplication) | Q236 (MQTT vs HTTP)
