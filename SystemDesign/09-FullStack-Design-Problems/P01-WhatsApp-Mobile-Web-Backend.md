# P01. WhatsApp — Mobile App + Web + Backend (End-to-End Design)
# हिंदी में: WhatsApp का पूरा डिज़ाइन — फ़ोन ऐप, WhatsApp Web और backend मिलाकर: messages भेजना/पाना, ✓ ✓✓ नीले ✓✓, offline में भेजना, groups, media, push notifications, कई devices और end-to-end encryption

---

## 🔵 Simple Definition (English)
Design a **WhatsApp-like messaging system end to end**:
- **Mobile apps** (React Native): local-first chat storage, an outbox, receipts, media, push, offline.
- **Web/Desktop client** (WhatsApp Web): a companion device with its own keys, IndexedDB, service worker.
- **Backend**: persistent connection gateways, message routing (store-and-forward), group fan-out, presence, media storage, push delivery and key distribution for **end-to-end encryption (E2EE)**.
Core guarantees:
- Messages are delivered **at least once**, **deduplicated** and shown **in order per chat**.
- Users can send while **offline**.
- Receipts flow back (**sent ✓ / delivered ✓✓ / read ✓✓ blue**).
- Content is **unreadable by the server** (E2EE).
Backend internals are covered in **Topic 115 (Chat Application)**. This file focuses on the **full system: clients + contract + backend working together**.

## 🔵 सरल परिभाषा (Hindi)
WhatsApp जैसा पूरा messaging system डिज़ाइन करना: mobile ऐप (local DB में chats, outbox, receipts, media, push, offline), Web/Desktop (अपनी keys वाला साथी device, IndexedDB), और backend (हमेशा खुले कनेक्शन वाले gateways, message पहुँचाना — store-and-forward, group fan-out, online/last seen, media storage, push, encryption keys)।
वादा: हर message कम से कम एक बार पहुँचे, duplicate न दिखे, हर chat में सही क्रम में; offline भी भेज सको; ✓, ✓✓, नीले ✓✓ वापस आएँ; और सर्वर content पढ़ न सके (E2EE)।

---

## 🔴 Problem it Solves
Messaging looks simple but combines the hardest client and backend problems:
- **Billions of users and persistent connections**: hundreds of millions of devices online at once, each holding a socket.
- **Flaky mobile networks**: messages sent in a lift or train must eventually go through exactly once.
- **Phone off for days**: messages wait on the server and are delivered when it comes back (with a push wake-up).
- **Groups**: one message to 1,000 members' devices.
- **Multi-device**: phone + web + desktop each need the message, encrypted separately.
- **Privacy**: end-to-end encryption means the server routes ciphertext it can't read, so search, previews and backups work on the device.
It's the most common full-stack design question because it tests **real-time, offline-first, delivery semantics, fan-out, push and security** together.

## 🔴 यह क्यों बना? (Hindi)
Messaging आसान दिखता है पर सबसे कठिन समस्याएँ जोड़ता है: अरबों यूज़र और करोड़ों खुले कनेक्शन; lift/train में भेजा message आख़िर में ठीक एक बार पहुँचे; फ़ोन कई दिन बंद तो message सर्वर पर इंतज़ार करे और push से जगाकर पहुँचे; group में एक message 1,000 लोगों के devices तक; फ़ोन + web + desktop सबको अलग-अलग encrypted; और E2EE — सर्वर सिर्फ़ बंद डिब्बा पहुँचाता है, पढ़ नहीं सकता। इसलिए यह सबसे आम full-stack सवाल है।

---

## 🟢 How it Works — Step by Step

### 1. Requirements (clarify in the interview)

```
Functional: 1:1 chat, groups (≤ 1,024 members), text + media (images, video, voice notes, docs),
            receipts (sent/delivered/read), typing indicator, online/last seen, offline send,
            push notifications, multi-device (phone + up to 4 companions: web/desktop/tablet),
            message history on device, delete-for-everyone, search (on device)
Non-functional: low latency (< 200–500 ms when both online), at-least-once + dedupe, per-chat ordering,
            E2E encryption, works on 2G and low-end Android, battery-efficient, highly available
Out of scope (say it): voice/video calls (WebRTC), payments, status/stories, channels
```

### 2. Estimation (back-of-envelope)

```
Users: ~2B; DAU ~1B+ ; messages ~100B/day (WhatsApp publicly cited ~100B/day in 2020)
→ ~1.2M msgs/sec average, peaks (New Year's Eve 00:00, Diwali) 3–5× → ~5M/s
Avg message ~ 100–200 bytes ciphertext + metadata → ~20 TB/day transient (server deletes after delivery)
Concurrent connections: ~500M+ → if one gateway server holds ~1–2M connections (Erlang-era claims ~2M),
   → hundreds to a few thousand gateway servers across regions
Media: hundreds of millions of media files/day → object storage + CDN, encrypted blobs, TTL on server
```

### 3. High-level architecture

```
 ┌──────────── Clients ─────────────┐
 │ Phone (RN/native): SQLite, outbox│        ┌──────────────────── Backend ───────────────────────┐
 │ Web/Desktop: IndexedDB, SW       │  WSS   │ Edge LB (TCP/TLS, sticky by connection)             │
 │ Each device: own identity keys   │◄──────►│ Connection Gateways (persistent sockets, heartbeats)│
 └──────────────────────────────────┘        │   │ register: user+device → gateway (Session store) │
        ▲ push (FCM/APNs) when offline       │   ▼                                                  │
        │                                    │ Chat/Router service ── Session store (Redis):        │
 ┌──────┴───────┐                            │   who is online on which gateway                     │
 │ Push service │◄── offline recipients ─────│   ├─ online → forward to recipient's gateway         │
 └──────────────┘                            │   └─ offline → per-device INBOX (Cassandra/HBase)    │
                                             │ Group service (membership, fan-out per member device)│
 Media: client encrypts → presigned upload ─►│ Media service → S3/blob store + CDN (encrypted blobs)│
                                             │ Key server (identity keys, signed prekeys, one-time  │
                                             │   prekeys per device)                                │
                                             │ Presence service (online/last seen, typing — ephemeral)│
                                             └──────────────────────────────────────────────────────┘
```

### 4. Client architecture (mobile & web)

```
Mobile (React Native)                               Web (React SPA, companion device)
- SQLite: chats, messages (status, server_seq),     - IndexedDB: same schema (Dexie), encrypted at rest
  contacts, media index; FTS for local search         with key from device; service worker for
- Outbox table (pending sends), media upload queue    offline shell + notifications (Web Push)
- Crypto: Signal protocol sessions per remote device - Own identity key; linked by scanning QR from phone
- Connection manager: WS, heartbeat 30 s, backoff,  - WS connection; history sync from phone on link
  resume with last ack'd seq                            (encrypted transfer), then independent
- Push: FCM/APNs; iOS Notification Service Extension- Virtualized chat list & message list
  decrypts preview locally                            (TanStack Virtual / reverse infinite scroll)
- Lists: FlashList inverted; media via expo-image   - Tab visibility: pause typing/presence when hidden
```

### 5. Message lifecycle (the key flow)

```
Sender phone (offline-capable)                Server                          Recipient devices
1. user taps Send → msg {id: uuid (client), chatId, body}
   → INSERT messages(status=PENDING ⏱) + outbox (same txn) → UI shows ⏱
2. encrypt per recipient DEVICE (Signal session) → envelope list
3. WS send {type:"msg", id, to, envelopes[], clientTs} ──►
                                              4. validate, assign server_ts / per-chat seq,
                                                 dedupe by (sender, id) → persist to recipient
                                                 device inboxes (durable) ──► ACK {id, serverTs} ─►
5. on ACK → status=SENT ✓, delete outbox row  ◄──
                                              6. recipient device online? → push over its gateway
                                                 offline? → FCM/APNs push ("New message")
                                                                              7. device receives, decrypts,
                                                                                 stores in SQLite, ACKs ──►
                                              8. delete from inbox (store-and-forward), send
                                                 DELIVERED receipt to sender ──►
9. status=DELIVERED ✓✓                        ◄──
                                                                              10. user opens chat → READ
                                                                                  receipt (batched) ──►
11. status=READ (blue ✓✓)                     ◄── (respect "read receipts off" setting)
Retries: sender resends same id until ACK → server dedupes → exactly-once EFFECT
```

### 6. API / protocol (over WebSocket; REST for non-real-time)

```
WS frames (binary protobuf in production; JSON shown):
  → {t:"auth", token, deviceId}                         ← {t:"ready", pending: n}
  → {t:"msg", id, chatId, to:[{device, ciphertext}], ts} ← {t:"ack", id, serverTs, seq}
  ← {t:"msg", id, from, chatId, ciphertext, serverTs, seq} → {t:"recv_ack", ids:[...]}
  ← {t:"receipt", ids:[...], kind:"delivered|read", by}   → {t:"read", chatId, upToSeq}
  → {t:"typing", chatId, on:true} (ephemeral, not stored) ← {t:"presence", user, online|lastSeen}
  → {t:"ping"} ← {t:"pong"}
REST: POST /keys/prekeys (upload), GET /keys/{user}/devices (fetch prekey bundles),
      POST /media/upload-url, GET /groups/{id}, POST /devices/link, PUT /profile
```

### 7. Data model

```
Server (transient + metadata, no plaintext):
  inbox_by_device (device_id, seq) → envelope (ciphertext, sender, server_ts)   TTL ~30 days if undelivered
  sessions (user_id, device_id) → gateway_id (Redis, TTL refreshed by heartbeat)
  groups (group_id) → members[], admins[], settings;   group_membership(user_id → groups)
  prekeys (user_id, device_id) → identity_pub, signed_prekey, one_time_prekeys[]
  push_tokens (device_id) → token, platform
Client (durable, the real history):
  chats(id, type, title, last_msg_id, unread_count, muted_until)
  messages(id, chat_id, sender_id, body, media_id, status, server_ts, seq, deleted)
  outbox(id, msg_id, payload, attempts, next_attempt_at)
  media(id, msg_id, local_path, cdn_url, key, sha256, size, status)
```

### 8. Groups

```
Small/medium groups: client-side fan-out of ENCRYPTION via Sender Keys (Signal):
  sender encrypts message ONCE with its sender key (distributed to members' devices earlier) →
  server fans out the single ciphertext to every member device inbox
Server fan-out: membership lookup (cached) → enqueue per device → online push via gateways,
  offline via inbox + push (collapse many group messages into one notification)
Large groups (≤1,024) → fan-out workers via queue (Kafka), rate-limited; receipts aggregated
  ("Read by 37") rather than per-member real-time spam
```

### 9. Media

```
Sender: compress (M21) → generate random AES key → encrypt file → upload encrypted blob via presigned URL
        → message contains {mediaUrl, mediaKey, sha256, thumbnail (tiny, encrypted), mime, size}
Recipient: auto-download per settings (Wi-Fi only for video), decrypt locally, verify hash, cache on disk
Server: stores opaque blobs on CDN-backed storage, deletes after a retention window
```

### 10. Multi-device & E2EE (what to say)

```
Each device has its own identity key pair. Linking web: phone shows QR → web scans → keys exchanged
→ phone authorizes device (signed device list) → contacts' clients see new device in the user's device list
Sending = encrypt for EVERY device of recipient + your own other devices (so your web sees your sent msgs)
Signal protocol: X3DH (initial key agreement using prekeys) + Double Ratchet (forward secrecy per message)
Server can't read content; it only sees metadata (who → whom, when, size)
Backups: encrypted with user-chosen password/key (E2EE backups) to iCloud/Google Drive
```

### 11. Presence, typing, last seen

```
Ephemeral, never stored long-term: Redis with TTL; publish only to users currently viewing that chat
(subscribe on chat open) → avoids fan-out storms; throttle typing events (1 per 3 s); privacy settings
("last seen: nobody") enforced server-side
```

## 🟢 कैसे काम करता है? (Hindi)
1. भेजना: फ़ोन पर client id के साथ message SQLite + outbox में (⏱), हर recipient device के लिए encrypt, WebSocket से भेजो → सर्वर (sender, id) से duplicate हटाकर recipient के हर device की inbox में पक्का रखे और ACK दे (✓)।
2. पहुँचाना: recipient online है तो उसके gateway से तुरंत; offline तो inbox में इंतज़ार + FCM/APNs push; device decrypt करके save करे और ACK भेजे → सर्वर inbox से हटाए (store-and-forward) और sender को ✓✓; chat खुलने पर नीले ✓✓।
3. Groups: Sender Keys से message एक बार encrypt, सर्वर हर member device तक fan-out (बड़े groups में queue/workers); बहुत सारे group messages का एक ही notification।
4. Media: फ़ोन पर compress + random key से encrypt → presigned URL से upload → message में URL + key + hash; पाने वाला download करके decrypt; Web/Desktop अपनी keys वाला साथी device है — QR से जुड़ता है, हर device के लिए अलग encryption।
5. Online/typing/last seen अस्थायी (Redis TTL), सिर्फ़ उसी chat को देख रहे लोगों को; client पर WS heartbeat, backoff से reconnect, आख़िरी seq से resume; सर्वर सिर्फ़ metadata देखता है, content नहीं।

---

## 🟡 Real World Example

**WhatsApp's backend lineage** — built on **Erlang** (a modified ejabberd/XMPP) on FreeBSD. In 2012 they publicly described handling ~2 million TCP connections on a single server. When Facebook acquired WhatsApp in 2014 (~450M users), the company had only around 50 engineers, a famous example of an efficient architecture.

**Store-and-forward & E2EE** — WhatsApp rolled out end-to-end encryption by default with the **Signal Protocol** (2016). Messages are deleted from servers once delivered, and media is stored encrypted. E2E encrypted backups arrived in 2021.

**Multi-device (2021)** — WhatsApp re-architected so companion devices (Web, Desktop, later a second phone) work **without the phone online**. Each device has its own identity keys and senders encrypt per device (client fan-out), with an authenticated device list per account.

**India scale** — India is WhatsApp's largest market (~500M+ users). New Year's Eve and Diwali greetings create massive message spikes, and much usage is on low-end Android and 2G/3G, hence aggressive compression, a small app size and a lean binary protocol.

## 🟡 Real Example Hindi में
WhatsApp का backend **Erlang** (बदला हुआ ejabberd/XMPP) पर बना; 2012 में एक server पर ~20 लाख कनेक्शन बताए; 2014 में Facebook के ख़रीदते समय ~45 करोड़ यूज़र्स पर सिर्फ़ ~50 engineers थे।
2016 से Signal Protocol से default E2EE, पहुँचने के बाद सर्वर से message हटाना, 2021 में encrypted backups और multi-device (फ़ोन बंद हो तब भी Web चले); भारत सबसे बड़ा बाज़ार (50 करोड़+) — नए साल और दिवाली पर messages का भारी उछाल।

---

## 🟠 My Stack Example

### Client: send with outbox + state machine (React Native)
```ts
// src/features/chat/send.ts
export async function sendText(chatId: string, body: string) {
  const id = uuid();                                              // client message id = idempotency key
  const now = Date.now();
  await db.withTransactionAsync(async () => {
    await db.runAsync(`INSERT INTO messages (id, chat_id, sender_id, body, status, client_ts) VALUES (?,?,?,?, 'PENDING', ?)`, [id, chatId, me(), body, now]);
    await db.runAsync(`INSERT INTO outbox (id, msg_id, attempts, next_attempt_at) VALUES (?,?,0,0)`, [uuid(), id]);
  });
  outboxPump.kick();                                              // sends when connected
}

// Outbox pump: encrypt per device and send over WS; resend same id until ACK
async function flushOne(row: OutboxRow) {
  const msg = await getMessage(row.msg_id);
  const devices = await keyDirectory.devicesFor(msg.chat_id);    // recipient devices + my other devices
  const envelopes = await Promise.all(devices.map(async (d) => ({ device: d.id, c: await signal.encrypt(d, msg.body) })));
  realtime.send({ t: 'msg', id: msg.id, chatId: msg.chat_id, to: envelopes, ts: msg.client_ts });
}

// Incoming frames update the local DB (UI observes DB)
realtime.on('ack', async ({ id, serverTs, seq }) => {
  await db.runAsync(`UPDATE messages SET status='SENT', server_ts=?, seq=? WHERE id=? AND status='PENDING'`, [serverTs, seq, id]);
  await db.runAsync(`DELETE FROM outbox WHERE msg_id=?`, [id]);
});
realtime.on('receipt', async ({ ids, kind }) => {
  const rank = kind === 'read' ? 3 : 2;                          // never downgrade READ → DELIVERED
  await db.runAsync(`UPDATE messages SET status=? WHERE id IN (${ids.map(() => '?').join(',')})
                     AND (CASE status WHEN 'PENDING' THEN 0 WHEN 'SENT' THEN 1 WHEN 'DELIVERED' THEN 2 ELSE 3 END) < ?`,
                    [kind.toUpperCase(), ...ids, rank]);
});
realtime.on('msg', async (m) => {
  const body = await signal.decrypt(m.from, m.ciphertext);
  await db.runAsync(`INSERT OR IGNORE INTO messages (id, chat_id, sender_id, body, status, server_ts, seq) VALUES (?,?,?,?, 'DELIVERED', ?, ?)`,
                    [m.id, m.chatId, m.from, body, m.serverTs, m.seq]);   // INSERT OR IGNORE = dedupe
  realtime.send({ t: 'recv_ack', ids: [m.id] });
});
```

### Gateway (Node + ws + Redis): register sessions, route, ack
```js
import { WebSocketServer } from 'ws';
const wss = new WebSocketServer({ port: 8080 });
const local = new Map();                                     // deviceId → socket on THIS gateway
const GATEWAY_ID = process.env.GATEWAY_ID;

wss.on('connection', (ws) => {
  let deviceId;
  ws.on('message', async (raw) => {
    const f = JSON.parse(raw);
    if (f.t === 'auth') {
      const dev = await verifyDeviceToken(f.token); deviceId = dev.deviceId;
      local.set(deviceId, ws);
      await redis.set(`sess:${deviceId}`, GATEWAY_ID, 'EX', 90);              // refreshed by pings
      await drainInbox(deviceId, ws);                                         // deliver pending
      return;
    }
    if (f.t === 'ping') { await redis.expire(`sess:${deviceId}`, 90); return ws.send('{"t":"pong"}'); }
    if (f.t === 'msg') {
      const fresh = await redis.set(`dedupe:${deviceId}:${f.id}`, 1, 'NX', 'EX', 86400);   // idempotent
      const serverTs = Date.now();
      if (fresh) await chatRouter.route({ ...f, from: deviceId, serverTs });   // persist to inboxes + forward
      return ws.send(JSON.stringify({ t: 'ack', id: f.id, serverTs }));
    }
    if (f.t === 'recv_ack') return chatRouter.delivered(deviceId, f.ids);    // delete from inbox, notify sender
    if (f.t === 'read') return chatRouter.read(deviceId, f.chatId, f.upToSeq);
  });
  ws.on('close', () => { if (deviceId) { local.delete(deviceId); redis.del(`sess:${deviceId}`); } });
});

// Router: deliver to recipient devices (online → its gateway via pub/sub; offline → inbox + push)
export const chatRouter = {
  async route(m) {
    for (const env of m.to) {
      await inbox.append(env.device, { id: m.id, from: m.from, chatId: m.chatId, ciphertext: env.c, serverTs: m.serverTs });  // durable first
      const gw = await redis.get(`sess:${env.device}`);
      if (gw) await redis.publish(`gw:${gw}`, JSON.stringify({ device: env.device, msgId: m.id }));
      else await push.notify(env.device, { title: 'New message', collapseKey: m.chatId });   // content decrypted on device
    }
  },
};
```

### Durable per-device inbox (Cassandra-style schema)
```sql
CREATE TABLE inbox_by_device (
  device_id text, seq timeuuid, msg_id text, sender text, chat_id text, ciphertext blob, server_ts bigint,
  PRIMARY KEY ((device_id), seq)
) WITH CLUSTERING ORDER BY (seq ASC) AND default_time_to_live = 2592000;   -- 30 days if never delivered
-- drain: SELECT * FROM inbox_by_device WHERE device_id=? LIMIT 500;  delete after recv_ack
```

### Web companion: IndexedDB (Dexie) + reverse infinite scroll
```ts
import Dexie from 'dexie';
export const db = new Dexie('wa-web');
db.version(1).stores({ chats: 'id, lastTs', messages: 'id, [chatId+seq], chatId', outbox: 'id, msgId' });
// Load newest 50 for a chat, then older pages on scroll-up
const page = await db.table('messages').where('[chatId+seq]').between([chatId, Dexie.minKey], [chatId, beforeSeq]).reverse().limit(50).toArray();
```

### Push with on-device decryption (iOS Notification Service Extension idea)
```
APNs payload: { aps: { alert: { title: "New message" }, "mutable-content": 1 }, enc: "<ciphertext>", sender: "<id>" }
NSE (native Swift target) runs before display → loads Signal session from shared App Group keychain →
decrypts → sets title "Mom" body "Reached home?" → OS shows it. Server never had plaintext.
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you guarantee a message is delivered exactly once to the user?**
A1: The network can only give at-least-once delivery, so you make the effect exactly-once with idempotency. The sender assigns a client message ID and stores it in a durable outbox, retrying until the server ACKs. The server dedupes by (sender device, message ID), persists to the recipient device inboxes before ACKing, and delivers repeatedly until the recipient ACKs. The recipient inserts with the message ID as primary key (insert-or-ignore), so duplicates never show. Receipts are monotonic (never downgrade read to delivered).

**Q2: How are messages ordered?**
A2: Per-chat ordering uses server-assigned timestamps or sequence numbers when the server accepts each message, not device clocks. Clients sort by server sequence, with the client timestamp as a fallback for local pending messages. If a gap in sequence is detected, the client syncs missing messages. Global ordering across chats isn't needed. In groups, the server's accept order defines the canonical order, and concurrent sends are ordered by arrival.

**Q3: What happens when the recipient is offline for three days?**
A3: The message stays in the recipient device's durable inbox on the server (store-and-forward), with a retention TTL of around 30 days. A push notification via FCM/APNs wakes or alerts the device, and multiple messages collapse into one notification per chat. When the device reconnects, it authenticates, drains the inbox in order and ACKs. The server then deletes those entries and sends delivered receipts to senders. If the TTL expires undelivered, the message is dropped and the sender keeps a single ✓.

**Q4: How does WhatsApp Web work without the phone being online (multi-device)?**
A4: Each companion device (web, desktop) has its own identity keys and is linked by scanning a QR code with the phone, which signs it into the account's device list. Contacts' clients fetch the user's device list and encrypt each message separately for every device (and senders also encrypt for their own other devices, to sync sent messages). The server routes each envelope to each device's inbox independently, so the web client receives messages directly over its own WebSocket. History is transferred from the phone once at link time, encrypted.

**Q5: How do you scale millions of persistent connections?**
A5: Use dedicated connection gateway servers optimized for many idle sockets (Erlang, Go or tuned Node with epoll), behind L4 load balancers, with lightweight heartbeats. A session registry (Redis or a distributed map) records which gateway holds each device, refreshed by heartbeats. Routers forward via pub/sub or direct RPC to the right gateway, and offline devices get inbox storage plus push. Gateways scale horizontally across regions near users. Clients reconnect with backoff and jitter to avoid storms after gateway restarts, and you drain connections gracefully during deploys.

---

## 🔷 Trade-offs
✅ Store-and-forward (delete after delivery): minimal server storage & privacy — ❌ history lives only on devices (backups needed).
✅ E2EE: privacy — ❌ no server-side search/spam scanning of content; multi-device key complexity.
✅ Client-side fan-out of encryption per device — ❌ more work per send for users with many devices / large groups (sender keys mitigate).
✅ WebSocket while foreground + push while background — ❌ two paths to keep consistent (sync on reconnect).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Connection gateway | Server holding persistent sockets | खुले कनेक्शन रखने वाला सर्वर |
| Store-and-forward | Keep until delivered, then delete | पहुँचने तक रखो, फिर हटाओ |
| Inbox (per device) | Pending messages queue | device की pending कतार |
| Client message ID | Idempotency key for a message | message की अपनी पहचान |
| Delivery receipt | Recipient device got it (✓✓) | पहुँच गया |
| Read receipt | User opened it (blue ✓✓) | पढ़ लिया |
| E2EE | Only endpoints can decrypt | सिर्फ़ दोनों सिरे पढ़ सकें |
| Signal protocol | X3DH + Double Ratchet | Signal encryption तरीका |
| Sender keys | Group encryption optimization | group के लिए एक बार encrypt |
| Companion device | Linked web/desktop with own keys | जुड़ा हुआ साथी device |

---

## ⚡ 3-Line Summary
**English:**
1. Clients are local-first (SQLite/IndexedDB + outbox); gateways hold sockets; router persists to per-device inboxes, forwards online, pushes offline; deletes after delivery.
2. Exactly-once effect via client IDs + server dedupe + idempotent inserts; per-chat server sequence for ordering; monotonic receipts ✓ → ✓✓ → blue.
3. E2EE with Signal per device (sender keys for groups), encrypted media blobs, multi-device via device lists; presence/typing ephemeral; scale gateways horizontally with session registry.

**Hindi:**
1. Client local-first (SQLite/IndexedDB + outbox); gateways sockets रखते; router device inbox में रखकर online को भेजे, offline को push; पहुँचने पर हटाए।
2. Client id + सर्वर dedupe से एक ही बार असर; chat में सर्वर का sequence; receipts ✓ → ✓✓ → नीला।
3. हर device के लिए Signal E2EE (groups में sender keys), encrypted media, multi-device; presence अस्थायी; gateways horizontally scale।

---

## ➡️ Next Topic Suggestion
**P02. Instagram — Feed + Stories + Reels** — From messaging to media consumption: a ranked feed, ephemeral stories and an infinite vertical video player, with heavy client-side media preloading and backend fan-out.
