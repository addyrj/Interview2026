# 115. Chat Application (WhatsApp)
# हिंदी में: Chat Application — WhatsApp जैसी सेवा का backend: 1:1 और group chats, तुरंत message पहुँचाना, ✓✓ (delivered/read), online स्थिति, offline यूज़र्स को बाद में देना, media और करोड़ों users का स्केल

---

## 🔵 Simple Definition (English)
Design a messaging system like **WhatsApp / Messenger / Slack DMs** that supports **1:1 and group chat**, **real-time delivery** over persistent connections, **message ordering**, **sent/delivered/read receipts**, **presence (online/last seen)**, **typing indicators**, **offline delivery** with push notifications, **media sharing** (images, video, voice notes), **multi-device sync**, and optionally **end-to-end encryption**, for **billions of messages per day**.

## 🔵 सरल परिभाषा (Hindi)
WhatsApp जैसा chat backend: 1:1 और group में तुरंत messages, सही क्रम, ✓ भेजा / ✓✓ पहुँचा / नीला ✓✓ पढ़ा, online/last seen, typing…, offline यूज़र को बाद में message + push notification, फ़ोटो/वीडियो/voice, कई devices पर sync — रोज़ अरबों messages।

---

## 🔴 Problem it Solves
Real-time chat at scale combines several hard problems:
- Millions of **persistent connections** (Topic 96) and routing a message to the recipient's server.
- **Reliability:** no lost messages despite flaky mobile networks; no duplicates; correct ordering.
- **Offline users:** store until delivered, then notify via push.
- **Groups:** fan-out to hundreds or thousands of members efficiently.
- **Media:** large files must not flow through chat servers.
- **Privacy:** end-to-end encryption so the server can't read messages.

## 🔴 यह क्यों बना? (Hindi)
बड़े स्केल पर chat में कई कठिन समस्याएँ: करोड़ों खुले कनेक्शन, message सही सर्वर तक पहुँचाना, कमज़ोर नेटवर्क पर भी कोई message न खोए, न दोहराए, सही क्रम में; offline यूज़र के लिए रखना; groups में सैकड़ों लोगों तक भेजना; भारी media; और end-to-end encryption।

---

## 🟢 How it Works — Step by Step (Interview Design)

### 1. Requirements

```
Functional:
  - 1:1 chat, group chat (up to 1,024 members), text + media + voice notes
  - Receipts: sent ✓ (server got it), delivered ✓✓ (device got it), read (blue ✓✓)
  - Presence (online / last seen), typing indicator
  - Offline delivery + push notification; chat history sync across devices (phone + web/desktop)
  - (Optional) E2E encryption, message delete/edit, reactions, search
Non-functional:
  - Low latency: < 200–500 ms delivery when both online
  - No message loss; at-least-once delivery + dedup; per-conversation ordering
  - Massive scale: 1B+ DAU, 100B messages/day; HA; mobile battery/data efficient
```

### 2. Estimation

```
DAU 500M × 40 msgs/day = 20B msgs/day ≈ 230k msgs/s avg, peak ~700k/s (New Year's Eve: way more)
Avg message 100 bytes (+ metadata ~200 B) → ~6 TB/day of text if stored long-term
Concurrent connections: ~300M at peak → ÷ 500k per gateway ≈ 600+ gateway servers
Media: 10% of messages with media avg 200 KB → 2B × 200 KB = 400 TB/day → object storage + CDN
(WhatsApp's model: store-until-delivered → much less long-term server storage)
```

### 3. API / protocol (over WebSocket or MQTT-like binary protocol)

```
Client → server frames:
  send     { clientMsgId, conversationId, type: "text|media", body | mediaRef, ts }
  ack      { msgId | upToSeq }                 (delivered)
  read     { conversationId, upToSeq }         (read receipt)
  typing   { conversationId }
  sync     { conversationId, afterSeq } / { sinceCursor } on reconnect
Server → client:
  msg      { msgId, seq, conversationId, from, body, ts }
  receipt  { msgId, status: "sent|delivered|read", by }
  presence { userId, online, lastSeen }
REST: POST /media/upload-url (presigned), GET /conversations, GET /conversations/{id}/messages?before=
```

### 4. High-level architecture

```
 📱 A                                                                              📱 B
  │ WSS                                                                             │ WSS
  ▼                                                                                 ▼
┌──────────────┐   ┌──────────────────────────────────────────────┐        ┌──────────────┐
│ Gateway-1    │──►│ CHAT SERVICE (stateless)                      │◄──────►│ Gateway-7    │
│ holds A's    │   │ 1. dedup (clientMsgId) 2. assign seq per conv │        │ holds B's    │
│ connection   │   │ 3. persist message  4. ack "sent" to A        │        │ connection   │
└──────────────┘   │ 5. route: presence lookup B → gw-7 → deliver   │        └──────────────┘
                   │    B offline → offline queue + push           │
                   └──┬───────────┬────────────┬───────────┬──────┘
                      ▼           ▼            ▼           ▼
              Message store   Presence /    Group svc   Push svc (FCM/APNs)
              (Cassandra/     session store (members)
              ScyllaDB/HBase) (Redis: user→gw)
 Media: client → presigned upload → S3/object store → CDN; message carries mediaRef (+ thumbnail)
```

### 5. Message flow (1:1, both online)

```
1. A → gw-1: send {clientMsgId: c1, conv: AB, body}
2. Chat svc: if c1 seen → return previous ack (idempotent); else seq = next seq for conv AB (e.g. 1045)
3. Persist (conv AB, seq 1045, msgId) → ack to A: "sent ✓" (+ server msgId, seq)
4. Lookup presence: B → gw-7 → push frame to B's socket
5. B's device ACKs → chat svc marks delivered → receipt to A: "delivered ✓✓"
6. B opens chat → read {upToSeq 1045} → receipt to A: blue ✓✓ (batched, read up to seq)
```

### 6. Offline & reconnect

```
B offline: message stored with status "pending for B" (offline inbox per user/device)
  → push notification via FCM/APNs ("A: Hey!" — or generic text when E2E encrypted)
B reconnects: sends last received seq/cursor → server streams pending messages → B ACKs → delete from
  offline queue (WhatsApp deletes from servers after delivery to all devices) → sender gets ✓✓
```

### 7. Group chat fan-out

```
Group G (200 members): A sends → persist ONCE in conversation G (seq) → fan-out:
  for each member: online → deliver via their gateway; offline → offline queue + push
Small/medium groups: fan-out on write (per-member delivery records)
Very large groups/channels (100k+): fan-out on read (members pull from conversation log by seq) +
  lightweight "new messages" signal → avoids writing 100k delivery rows per message
Receipts in groups: aggregate ("read by 150 of 200"), don't send 200 receipts to everyone
```

### 8. Data model (Cassandra-style)

```
messages_by_conversation:
  PRIMARY KEY ((conversation_id, bucket), seq)     bucket = month/week to bound partition size
  columns: msg_id, sender_id, type, body/ciphertext, media_ref, created_at, edited, deleted
user_conversations:
  PRIMARY KEY (user_id, last_activity DESC, conversation_id)  → chat list screen
conversation_members: (conversation_id, user_id, role, joined_at)
device_inbox (pending delivery): PRIMARY KEY ((user_id, device_id), seq_global)  TTL 30 days
receipts: (conversation_id, user_id) → last_delivered_seq, last_read_seq        (compact!)
```

### 9. Ordering, dedup, multi-device

```
Ordering: server assigns monotonically increasing seq per conversation (single writer per conversation:
  partition chat service by conversation id, or atomic counter in Redis/DB); clients sort by seq
Dedup: clientMsgId (UUID from sender) unique per sender → retries never create duplicates
Multi-device: each device has its own delivery cursor; messages delivered to all registered devices
  (with E2E: sender encrypts separately per device key)
```

### 10. End-to-end encryption (Signal protocol, high level)

```
Each device has identity + prekeys; public keys on server (key directory)
Sender fetches recipient device keys → X3DH key agreement → Double Ratchet session keys
Messages encrypted on device; server stores/forwards CIPHERTEXT only (can't read)
Groups: sender keys distributed to members; media encrypted with random key sent inside message
Consequences: server-side search/moderation impossible; push previews generic; backups encrypted
```

### 11. Presence & typing (cheap, ephemeral)

```
Presence: heartbeat → Redis key with TTL; publish changes only to contacts who have chat open/subscribed;
  "last seen" stored lazily; privacy settings respected
Typing: ephemeral, throttled (every 3 s), never stored, auto-expire 5 s
```

## 🟢 कैसे काम करता है? (Hindi)
1. हर यूज़र का फ़ोन एक gateway सर्वर से WebSocket पर जुड़ा रहता है; Redis में "B किस gateway पर" सेव रहता है।
2. A का message: chat service duplicate जाँचती है (clientMsgId), बातचीत में अगला क्रम नंबर (seq) देती है, सेव करती है, A को ✓ भेजती है।
3. B ऑनलाइन → उसके gateway से तुरंत; B का फ़ोन ACK करे → A को ✓✓; B पढ़े → नीला ✓✓। B ऑफ़लाइन → offline queue + push notification; जुड़ने पर आख़िरी seq से छूटे messages।
4. Group: message एक बार सेव, फिर हर सदस्य तक (ऑनलाइन → gateway, ऑफ़लाइन → queue); बहुत बड़े groups में सदस्य ख़ुद खींचते हैं।
5. Media सीधे S3 पर (presigned URL), message में सिर्फ़ link; E2E encryption में सर्वर सिर्फ़ encrypted डेटा आगे भेजता है, पढ़ नहीं सकता।

---

## 🟡 Real World Example

**WhatsApp** — Erlang/FreeBSD servers handling millions of connections each, with a store-and-forward design where messages are deleted from servers after delivery. It uses the Signal protocol for E2E encryption (since 2016), and handled ~100B messages/day with a famously small engineering team (around 50 engineers at the Facebook acquisition in 2014).

**Facebook Messenger** — used MQTT for mobile efficiency. Its Iris system orders messages per user in a queue-like structure for sync across devices.

**Discord** — stores trillions of messages in ScyllaDB (migrated from Cassandra), partitioned by channel plus time bucket. Its Elixir gateways handle millions of concurrent users.

**Slack** — WebSocket gateways plus channel servers using consistent hashing, with messages stored in MySQL (Vitess-sharded) and searchable, since Slack isn't E2E encrypted.

**Telegram** — cloud-based chats (synced across devices, server-side storage) vs WhatsApp's device-centric E2E model. It's a good trade-off discussion for interviews.

## 🟡 Real Example Hindi में
WhatsApp Erlang सर्वरों पर लाखों कनेक्शन हर सर्वर पर संभालता है, message पहुँचते ही सर्वर से हटा देता है, और Signal protocol से E2E encryption करता है — 2014 में लगभग 50 इंजीनियरों की टीम रोज़ अरबों messages चलाती थी।
Discord ने खरबों messages ScyllaDB में (channel + समय के हिसाब से) रखे। Telegram cloud में chats रखता है (कई devices पर sync), WhatsApp device पर — दोनों के अलग फ़ायदे।

---

## 🟠 My Stack Example

### Message schema (Cassandra/ScyllaDB CQL)
```sql
CREATE TABLE messages_by_conversation (
  conversation_id uuid, bucket int, seq bigint,
  msg_id timeuuid, sender_id bigint, type text, body text, media_ref text, created_at timestamp,
  PRIMARY KEY ((conversation_id, bucket), seq)
) WITH CLUSTERING ORDER BY (seq DESC);

CREATE TABLE user_conversations (
  user_id bigint, last_activity timestamp, conversation_id uuid, last_preview text, unread int,
  PRIMARY KEY (user_id, last_activity, conversation_id)
) WITH CLUSTERING ORDER BY (last_activity DESC);
```

### Chat service send path (Node + Socket.IO emitter + Redis seq)
```js
socket.on('send', async ({ clientMsgId, conversationId, body, mediaRef }, ack) => {
  const uid = socket.data.user.id;
  if (!(await isMember(conversationId, uid))) return ack({ error: 'FORBIDDEN' });

  // idempotency: same clientMsgId → same result
  const existing = await redis.get(`cmid:${uid}:${clientMsgId}`);
  if (existing) return ack(JSON.parse(existing));

  const seq = await redis.incr(`conv:seq:${conversationId}`);           // per-conversation ordering
  const msg = { msgId: uuidv1(), seq, conversationId, from: uid, body, mediaRef, ts: Date.now() };
  await cassandra.execute(INSERT_MSG, [conversationId, bucketOf(msg.ts), seq, msg.msgId, uid, mediaRef ? 'media' : 'text', body, mediaRef, new Date(msg.ts)],
                          { prepare: true, consistency: localQuorum });
  const result = { msgId: msg.msgId, seq, status: 'sent' };
  await redis.set(`cmid:${uid}:${clientMsgId}`, JSON.stringify(result), { EX: 86_400 });
  ack(result);                                                            // ✓ to sender

  const members = await conversationMembers(conversationId);              // cached
  for (const m of members.filter((m) => m !== uid)) {
    const online = await redis.exists(`presence:${m}`);
    if (online) emitter.to(`user:${m}`).emit('msg', msg);
    else await pushQueue.add('chat-push', { userId: m, conversationId, preview: previewOf(msg) }, { jobId: `${msg.msgId}:${m}` });
  }
  await updateConversationLists(conversationId, members, msg);            // chat list ordering (async ok)
});

socket.on('ack', async ({ conversationId, upToSeq }) => {                 // delivered
  await setCursor(conversationId, socket.data.user.id, 'delivered', upToSeq);
  emitter.to(`conv:${conversationId}:senders`).emit('receipt', { conversationId, upToSeq, by: socket.data.user.id, status: 'delivered' });
});
```

### Sync on reconnect (REST or socket)
```js
app.get('/api/v1/conversations/:id/messages', authenticate, async (req, res) => {
  const after = BigInt(req.query.afterSeq ?? 0);
  res.json(await fetchMessagesAfter(req.params.id, after, 200));          // client fills gaps by seq
});
```

### Media upload (presigned, never through chat servers)
```js
app.post('/api/v1/media/upload-url', authenticate, async (req, res) => {
  const key = `media/${req.user.id}/${crypto.randomUUID()}`;
  res.json({ url: await presignPut(key, req.body.contentType, 16 * 1024 * 1024), mediaRef: key });
});
// client uploads (encrypted if E2E) → sends message with mediaRef + thumbnail (blurhash) → recipients download via CDN signed URL
```

### React Native client essentials
```ts
// local DB (WatermelonDB/SQLite) is the UI source of truth; outbox for unsent messages
async function sendMessage(conv: string, body: string) {
  const clientMsgId = uuid.v4();
  await localDb.messages.insert({ clientMsgId, conv, body, status: 'pending', ts: Date.now() });   // optimistic ⏱
  socket.emit('send', { clientMsgId, conversationId: conv, body }, (r) => localDb.messages.update(clientMsgId, { status: r.status, seq: r.seq }));
}
socket.on('connect', async () => {                       // retry outbox + sync gaps
  for (const m of await localDb.messages.pending()) socket.emit('send', m, (r) => localDb.messages.update(m.clientMsgId, r));
  for (const c of await localDb.conversations.all()) socket.emit('sync', { conversationId: c.id, afterSeq: c.lastSeq });
});
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you deliver a message from user A to user B in real time?**
A1: Both clients keep persistent connections (WebSocket or MQTT) to gateway servers, and presence in Redis maps each user to their gateway. A sends a message with a client-generated ID. The chat service deduplicates, assigns a per-conversation sequence number, persists it and acks "sent" to A. It looks up B's gateway and pushes the message to B's socket. B's device acks, the service records "delivered" and notifies A, and read receipts follow when B opens the chat. If B is offline, the message waits in B's pending queue and a push notification is sent. On reconnect, B syncs from its last sequence number.

**Q2: How do you guarantee no lost or duplicated messages and correct order?**
A2: Persist before acknowledging the sender. Senders retry with the same client message ID, which the server deduplicates. The server assigns a monotonically increasing sequence per conversation (a single writer per conversation, or an atomic counter). Recipients ack by sequence, and on reconnect they request messages after their last sequence to fill gaps. Clients sort by sequence and dedupe by message ID. Delivery is at-least-once with idempotent handling at every hop.

**Q3: How would you implement group messaging efficiently?**
A3: Store each group message once in the conversation log, then fan out notifications. For normal groups (up to about 1,000), deliver to each online member's gateway, and enqueue offline members with pushes. Track per-member read and delivery cursors (last seq) rather than per-message rows, and aggregate receipts. For very large channels, use fan-out on read: members pull from the log by sequence and the server sends only lightweight "new activity" signals. With E2E encryption, use sender keys so the sender encrypts once per message rather than per member.

**Q4: Which database would you use for messages and why?**
A4: A wide-column store such as Cassandra, ScyllaDB or HBase: massive append-heavy writes, a primary access pattern of "latest N messages in a conversation" (partition by conversation ID plus a time bucket, clustered by sequence descending), linear horizontal scaling and multi-datacenter replication. User profiles and group metadata can live in a relational DB, presence and sessions in Redis, media in object storage behind a CDN, and search in Elasticsearch (if not E2E encrypted).

**Q5: How does end-to-end encryption change the design?**
A5: Encryption and decryption happen on devices (Signal protocol: X3DH plus Double Ratchet). The server distributes public keys and stores and forwards only ciphertext, so it can't do server-side search, spam scanning of content, or rich push previews. Multi-device requires encrypting per device, or device-linking protocols. Group messages use sender keys. Media is encrypted with per-file keys sent in the message. Backups must be client-encrypted. Metadata (who talks to whom, when) is still visible to the server unless further minimized.

---

## 🔷 Trade-offs
✅ Store-and-forward (delete after delivery): less storage, privacy — ❌ no cloud history/search (WhatsApp).
✅ Cloud-stored history: multi-device sync, search — ❌ storage cost, privacy concerns (Telegram/Slack).
✅ Fan-out on write for groups: fast reads — ❌ heavy writes for large groups.
✅ E2E encryption: privacy — ❌ no server features on content, complex multi-device.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Gateway server | Holds persistent client connections | कनेक्शन रखने वाला सर्वर |
| Presence | Online status / which server | ऑनलाइन स्थिति |
| Sequence number | Per-conversation ordering | बातचीत में क्रम संख्या |
| clientMsgId | Sender-generated dedup id | भेजने वाले की id |
| Delivery receipt | Device received message | पहुँचने की पुष्टि |
| Read receipt | User read message | पढ़ने की पुष्टि |
| Offline queue | Pending messages for offline user | ऑफ़लाइन के लिए रुके messages |
| Fan-out | Delivering to many recipients | कई लोगों तक भेजना |
| E2E encryption | Only devices can decrypt | सिर्फ़ devices पढ़ सकें |
| Signal protocol | E2E crypto protocol | E2E का प्रोटोकॉल |

---

## ⚡ 3-Line Summary
**English:**
1. Persistent connections via gateways + presence registry; chat service dedups (clientMsgId), assigns per-conversation seq, persists, then routes or queues for offline users with push.
2. Receipts via cursors (delivered/read up to seq); groups store once and fan out (or fan-out on read for huge channels); media via presigned upload + CDN.
3. Cassandra/Scylla for messages, Redis for presence, idempotent at-least-once delivery with resync; E2E encryption limits server-side features.

**Hindi:**
1. Gateway कनेक्शन + presence; chat service duplicate रोके, seq दे, सेव करे, फिर भेजे या offline queue + push।
2. ✓✓ cursors से; group में एक बार सेव, सबको भेजो; media presigned upload + CDN से।
3. Messages Cassandra/Scylla में, presence Redis में; resync के साथ भरोसेमंद delivery; E2E से सर्वर की सुविधाएँ सीमित।

---

## ➡️ Next Topic Suggestion
**116. Instagram Design** — From messaging to media social networks: next, photo/video upload pipelines, the feed, stories, likes and comments, followers, and serving billions of images through CDNs.
