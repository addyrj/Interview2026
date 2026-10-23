# M06. Offline-First Architecture
# हिंदी में: Offline-First Architecture — ऐप ऐसा बनाना कि internet न हो तब भी पूरा चले: डेटा पहले फ़ोन के अपने database से पढ़ा/लिखा जाए, और नेटवर्क मिलते ही चुपचाप सर्वर से मेल (sync) हो जाए

---

## 🔵 Simple Definition (English)
**Offline-first** means the app treats the **network as an optimization, not a requirement**:
- **Reads** come from the **local database** (the single source of truth for the UI), so screens render instantly with or without connectivity.
- **Writes** are applied **locally first** (optimistically), recorded in a durable **outbox/queue**, and **synced to the server in the background** when possible, with retries and idempotency.
- A **sync engine** pulls server changes (delta sync) into the local DB, pushes queued local changes, and resolves **conflicts** (M07).
- The UI shows **sync state**: pending, synced, failed, offline banner.
This differs from "offline-tolerant" apps (cache some screens, block writes when offline). Offline-first apps let users **keep working**: compose messages, place field reports, edit notes, mark deliveries.

## 🔵 सरल परिभाषा (Hindi)
Offline-first = नेटवर्क ज़रूरी नहीं, बस बोनस: पढ़ना फ़ोन के local DB से (UI का असली स्रोत) — screen तुरंत, internet हो या न हो; लिखना पहले local में (optimistic), फिर पक्की outbox कतार में, और नेटवर्क मिलते ही पीछे से सर्वर पर (retry + idempotency)।
Sync engine सर्वर के बदलाव local में लाता है, local बदलाव भेजता है और टकराव (conflict) सुलझाता है; UI बताता है — pending, synced, failed, offline।

---

## 🔴 Problem it Solves
Connectivity in India (and everywhere on mobile) is unreliable: metro tunnels, lifts, basements, rural areas, network handoffs, data packs running out, and "4G" that behaves like 2G.
Online-only apps:
- Show **spinners and errors** constantly and lose user input ("Network error, please try again" after typing a long message or filling a form).
- Feel **slow** even online, because every screen waits for a round trip (200–800 ms on mobile).
- **Can't serve field users**: delivery partners marking drops in basements, sales agents and bank correspondents in villages, ASHA health workers, inspectors.
Offline-first gives **instant UI, zero lost work, and productivity without connectivity**.

## 🔴 यह क्यों बना? (Hindi)
भारत (और हर जगह mobile पर) नेटवर्क भरोसेमंद नहीं — मेट्रो सुरंग, lift, basement, गाँव, data pack ख़त्म, नाम का 4G। Online-only ऐप हर बार spinner/error दिखाते हैं, लंबा message या form लिखने के बाद "Network error" और सब ग़ायब; online में भी हर screen round trip का इंतज़ार करती है; और field के लोग (basement में delivery, गाँव में bank agent, ASHA workers) काम नहीं कर पाते।
Offline-first = तुरंत UI, कोई काम नहीं खोता, बिना नेटवर्क भी काम चलता है।

---

## 🟢 How it Works — Step by Step

### Architecture

```
            ┌──────────────────────────── App ────────────────────────────┐
  User ───► │ UI (observes local DB queries)                               │
            │   ▲ render                       │ action                    │
            │   │                              ▼                           │
            │ Local DB (SQLite/WatermelonDB) ◄── Repository.write():        │
            │   entities + sync metadata         1) apply change locally    │
            │   (status, version, updated_at)    2) append to OUTBOX        │
            │   ▲                                   (same transaction!)     │
            │   │ apply pulled changes            │                         │
            │ SYNC ENGINE ◄───────────────────────┘                         │
            │  - triggers: app foreground, connectivity regained, periodic  │
            │    background task, push "you have changes", manual pull-to-  │
            │    refresh                                                     │
            │  - PUSH: send outbox items in order, Idempotency-Key, backoff │
            │  - PULL: GET /sync?since=token → upserts + tombstones          │
            │  - CONFLICTS: server rules / LWW / merge (M07)                 │
            └──────────────────────────────┬────────────────────────────────┘
                                           │ HTTPS (only when online)
                                           ▼
                                     Backend sync API
```

### Read path

```
Screen mounts → query local DB → render immediately (even offline)
             → if online & data stale → background pull → DB updates → UI re-renders reactively
No "loading spinner" if any cached data exists; show "Last updated 5 min ago" / offline banner
```

### Write path (outbox pattern on the client)

```
User taps "Mark delivered" (offline, in a basement)
 1. TRANSACTION: UPDATE orders SET status='DELIVERED', sync_status='PENDING' WHERE id=…
                 INSERT INTO outbox (id, type, payload, idempotency_key, created_at, attempts=0)
 2. UI shows ✓ Delivered (⏱ syncing)
 3. Sync engine (now or when online): POST /deliveries/{id}/complete  Idempotency-Key: <outbox.id>
      2xx → mark synced, delete outbox row, apply server response (e.g., server timestamp)
      4xx business error (order cancelled) → mark FAILED, surface to user, roll back local state
      5xx / timeout / offline → keep, retry with exponential backoff + jitter
 Ordering: process per-entity in order (create before update; upload photo before "complete"
           referencing it) → dependencies via sequence numbers or a per-entity queue
```

### Pull path (delta sync)

```
GET /sync?since=<cursor>&limit=500
→ { changes: { orders: { created:[…], updated:[…], deleted:[ids] } }, cursor: "c_9182", hasMore }
- Server tracks change log (updated_at + id, or a change sequence per user/tenant)
- Tombstones for deletions (otherwise deleted rows stay forever on devices)
- Page through large deltas; first sync = bootstrap snapshot (maybe a compressed file)
- Apply in a transaction; don't overwrite local PENDING changes blindly (conflict handling)
```

### Connectivity is not binary

```
NetInfo "connected" ≠ internet works (captive portal, weak signal) → treat request failures as offline
Use timeouts (e.g., 10 s) and quick health checks; "lie-fi" detection: slow responses → fall back
Respect data saver / metered: defer big syncs (media) to Wi-Fi if user prefers
```

### What NOT to do offline

```
Payments, OTP verification, seat/slot booking, inventory reservation (needs server truth now)
→ Queue intent only if business allows ("Order will be placed when online" — usually not for food!)
→ Otherwise show clear "Needs internet" state, preserve the user's input
```

### Tools

```
WatermelonDB sync, PowerSync (Postgres ↔ SQLite), ElectricSQL, Replicache/Zero, RxDB, TinyBase,
Couchbase Lite; React Query offline mutations (persist + resumePausedMutations) for simpler cases
```

## 🟢 कैसे काम करता है? (Hindi)
1. Screen हमेशा local DB से पढ़ती है — तुरंत दिखती है; online और डेटा पुराना हो तो पीछे से pull, DB बदलते ही UI अपने-आप बदलता है; "5 मिनट पहले अपडेट" या offline banner दिखाओ।
2. लिखना: एक transaction में local बदलाव + outbox में entry; UI पर ✓ (⏱ syncing); sync engine Idempotency-Key के साथ भेजता है — सफल तो synced, business error तो failed दिखाकर वापस, नेटवर्क error तो backoff से retry।
3. क्रम ज़रूरी: पहले create फिर update, पहले photo upload फिर "delivered"; हर entity की अपनी कतार या sequence।
4. Pull: `GET /sync?since=cursor` से सिर्फ़ बदलाव + हटाए गए ids (tombstones); पहली बार पूरा snapshot; local के pending बदलावों को आँख मूँदकर overwrite मत करो।
5. "Connected" का मतलब internet नहीं (captive portal, कमज़ोर signal) — timeout से पहचानो; payment, OTP, booking जैसे काम offline मत करो, बस input बचाकर "internet चाहिए" दिखाओ।

---

## 🟡 Real World Example

**WhatsApp** — the canonical offline-first app. You can open chats, read history and "send" messages offline. They show ⏱ (pending) and go out automatically when connectivity returns, with ✓/✓✓ updating as acknowledgements arrive.

**Google Docs / Gmail / Google Maps offline** — local storage with later sync (Docs offline edits, queued Gmail sends from the outbox, downloaded offline map regions).

**Field-force apps in India** — logistics PoD (proof of delivery) apps, microfinance and bank correspondent apps, agri-advisory and health-worker apps collect forms, photos and signatures offline in low-coverage areas and sync when back in range. Offline-first is a core requirement there, not a nice-to-have.

**Notion / Linear** — Linear is known for a local-first sync engine (instant UI with all data cached locally), and Notion added offline mode for pages in 2025, highlighting how hard retrofitting offline is.

## 🟡 Real Example Hindi में
WhatsApp offline-first का सबसे अच्छा उदाहरण — offline भी chats खुलती हैं, message "भेजो" तो ⏱ दिखता है और नेटवर्क आते ही अपने-आप चला जाता है, फिर ✓/✓✓।
भारत में logistics की proof-of-delivery, microfinance/bank correspondent, कृषि और स्वास्थ्य कर्मियों के ऐप गाँव में offline forms, फ़ोटो, signature लेकर बाद में sync करते हैं; Linear अपने local-first sync engine के लिए मशहूर है।

---

## 🟠 My Stack Example

### Outbox table + repository write (SQLite)
```ts
// migration
`CREATE TABLE outbox (id TEXT PRIMARY KEY, entity TEXT, entity_id TEXT, type TEXT, payload TEXT,
   seq INTEGER, attempts INTEGER DEFAULT 0, next_attempt_at INTEGER DEFAULT 0, status TEXT DEFAULT 'PENDING',
   last_error TEXT, created_at INTEGER);
 CREATE INDEX idx_outbox_due ON outbox(status, next_attempt_at, seq);`

// src/features/deliveries/repository.ts
export async function markDelivered(orderId: string, proof: { photoPath: string; lat: number; lng: number }) {
  const now = Date.now();
  await db.withTransactionAsync(async () => {
    await db.runAsync(`UPDATE orders SET status='DELIVERED', sync_status='PENDING', delivered_at=? WHERE id=?`, [now, orderId]);
    await enqueue({ entity: 'order', entityId: orderId, type: 'UPLOAD_PROOF', payload: proof });     // seq n
    await enqueue({ entity: 'order', entityId: orderId, type: 'COMPLETE_DELIVERY', payload: { at: now } }); // seq n+1 depends on proof
  });
  syncEngine.kick();                                    // try now; harmless if offline
}
```

### Sync engine: ordered push with backoff, then pull
```ts
// src/data/sync/engine.ts
let running = false;
export const syncEngine = {
  async kick() {
    if (running) return; running = true;
    try { await pushOutbox(); await pull(); } finally { running = false; }
  },
};

async function pushOutbox() {
  while (true) {
    const item = await db.getFirstAsync<OutboxRow>(
      `SELECT * FROM outbox WHERE status='PENDING' AND next_attempt_at <= ? ORDER BY seq LIMIT 1`, [Date.now()]);
    if (!item) return;
    try {
      const res = await send(item);                    // maps type → API call with Idempotency-Key: item.id
      await db.withTransactionAsync(async () => {
        await applyServerResult(item, res);           // e.g., set server ids/timestamps, sync_status='SYNCED'
        await db.runAsync(`DELETE FROM outbox WHERE id=?`, [item.id]);
      });
    } catch (e: any) {
      if (e.status >= 400 && e.status < 500 && e.status !== 408 && e.status !== 429) {
        await db.runAsync(`UPDATE outbox SET status='FAILED', last_error=? WHERE id=?`, [e.code ?? String(e.status), item.id]);
        await markEntityFailed(item);                 // UI shows "Couldn't sync — tap to fix"
        continue;                                     // business error: don't block the queue forever
      }
      const attempts = item.attempts + 1;
      const delay = Math.min(5 * 60_000, 2000 * 2 ** attempts) * (0.5 + Math.random() / 2);
      await db.runAsync(`UPDATE outbox SET attempts=?, next_attempt_at=? WHERE id=?`, [attempts, Date.now() + delay, item.id]);
      return;                                         // network-ish error: stop, retry later (preserve order)
    }
  }
}

async function pull() {
  let cursor = kv.getString('sync.cursor');
  do {
    const { changes, cursor: next, hasMore } = await http.get('/mobile/sync', { params: { since: cursor, limit: 500 } }).then(r => r.data);
    await db.withTransactionAsync(() => applyChanges(changes, { skipIfLocalPending: true }));  // conflicts → M07
    kv.set('sync.cursor', next); cursor = next;
    if (!hasMore) break;
  } while (true);
}

// Triggers
AppState.addEventListener('change', (s) => s === 'active' && syncEngine.kick());
NetInfo.addEventListener((s) => s.isInternetReachable && syncEngine.kick());
```

### Backend sync endpoint (FastAPI + Postgres change log)
```python
@app.get("/mobile/sync")
async def sync(since: str | None = None, limit: int = 500, user=Depends(current_user)):
    since_seq = decode_cursor(since) if since else 0
    rows = await db.fetch("""
        SELECT seq, entity, entity_id, op, data FROM change_log
        WHERE user_id = $1 AND seq > $2 ORDER BY seq LIMIT $3""", user.id, since_seq, limit + 1)
    has_more = len(rows) > limit
    rows = rows[:limit]
    changes = group_changes(rows)                       # {orders: {created, updated, deleted}}
    next_cursor = encode_cursor(rows[-1]["seq"]) if rows else since
    return {"changes": changes, "cursor": next_cursor, "hasMore": has_more}
# Writes use Idempotency-Key table (Topic 64) so retried pushes don't duplicate
```

### UI: sync status + offline banner
```tsx
function SyncBadge({ status }: { status: 'PENDING' | 'SYNCED' | 'FAILED' }) {
  if (status === 'SYNCED') return null;
  return status === 'PENDING'
    ? <Text accessibilityLabel="Waiting to sync">⏱</Text>
    : <Pressable onPress={retry} accessibilityRole="button"><Text>⚠️ Tap to retry</Text></Pressable>;
}
const { isInternetReachable } = useNetInfo();
{isInternetReachable === false && <Banner>You're offline. Changes will sync automatically.</Banner>}
```

### Lightweight alternative: React Query offline mutations
```ts
// Paused mutations persist (MMKV) and resume when online — fine for simple apps
onlineManager.setEventListener((set) => NetInfo.addEventListener((s) => set(!!s.isInternetReachable)));
queryClient.setMutationDefaults(['likePost'], { mutationFn: ({ id }) => http.post(`/posts/${id}/like`) });
// <PersistQueryClientProvider onSuccess={() => queryClient.resumePausedMutations()} …>
```

---

## ⚫ Interview Questions + Answers

**Q1: What does offline-first mean and how is it different from caching?**
A1: Offline-first makes the local database the primary source of truth for the UI. All reads come from local storage and writes are applied locally first and queued durably for background sync, so the app is fully usable without connectivity and the network only keeps the local state in sync. Caching (offline-tolerant) stores some responses for faster or occasional offline reads but still treats the server as the primary path and usually blocks writes when offline. Offline-first adds an outbox, a sync engine, conflict handling and sync-state UI.

**Q2: How do you design the write path for offline actions?**
A2: In a single local transaction, apply the change to the entity (marked pending) and append an outbox record with a unique ID used as the idempotency key, an entity reference, type, payload and sequence. The UI updates optimistically with a pending indicator. A sync engine processes the outbox in order (respecting dependencies) when online, sending requests with idempotency keys. On success it reconciles the server response and removes the item. On transient failure it retries with exponential backoff and jitter. On business errors it marks the item failed, notifies the user and rolls back or offers a fix.

**Q3: How does delta sync work?**
A3: The server maintains a change log or per-row update sequence (monotonic sequence or updated_at plus id) scoped by user or tenant. The client stores a cursor from its last sync and calls `GET /sync?since=cursor`, receiving created, updated and deleted records (tombstones) plus a new cursor, paginated for large deltas. The client applies changes transactionally, skipping or merging records with unsynced local edits (conflict handling), and saves the new cursor. First-time sync uses a snapshot. Tombstones must be kept long enough for infrequent clients, or those clients must re-bootstrap.

**Q4: What should never be done offline?**
A4: Operations that require authoritative, real-time server state or external verification: payments and refunds, OTP or 2FA verification, booking scarce inventory (seats, slots, limited stock), placing time-sensitive orders where prices or availability can change, and security changes (password, device binding). For these, preserve the user's input, show a clear "needs internet" state and resume when online, or queue only an intent the server re-validates.

**Q5: What are the hardest parts of offline-first?**
A5: Conflict resolution when the same data changes on the server and offline devices. Ordering and dependencies within the outbox. Idempotency across retries. Schema migrations on devices with pending unsynced data. Partial sync and storage limits (what subset of data to keep locally). Permission changes (data the user can no longer access must be removed). Large initial bootstrap. Clock skew. Testing combinations of offline and online transitions. Communicating sync state clearly in the UI.

---

## 🔷 Trade-offs
✅ Instant UI, works anywhere, no lost input, great for field users.
❌ Significant complexity: sync engine, conflicts, migrations, storage management, testing.
❌ Eventual consistency: users may see stale data; some actions can't be offline.
✅ Off-the-shelf sync (PowerSync, WatermelonDB sync) reduces effort — ❌ vendor/backend constraints.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Offline-first | Local DB primary, network syncs | पहले local, फिर sync |
| Source of truth | Data UI reads from | UI का असली स्रोत |
| Outbox | Durable queue of pending writes | भेजने की पक्की कतार |
| Sync engine | Pushes/pulls changes | बदलाव भेजने-लाने वाला |
| Delta sync | Only changes since cursor | सिर्फ़ नए बदलाव |
| Cursor / sync token | Position in change log | कहाँ तक sync हुआ |
| Tombstone | Marker of deletion | हटाने का निशान |
| Optimistic write | Apply locally before server | सर्वर से पहले local |
| Idempotency key | Dedupes retries | दोहराव रोकने की key |
| Lie-fi | Connected but not working network | नाम का नेटवर्क |

---

## ⚡ 3-Line Summary
**English:**
1. Offline-first: UI reads from the local DB; writes go local + outbox in one transaction; network only syncs.
2. Sync engine: ordered push with idempotency + backoff, delta pull with cursors and tombstones, triggered on foreground/connectivity/background.
3. Show sync states, handle business failures and conflicts, and keep server-authoritative actions (payments, OTP, bookings) online-only.

**Hindi:**
1. Offline-first: UI local DB से पढ़े; लिखना local + outbox एक transaction में; नेटवर्क सिर्फ़ sync के लिए।
2. Sync engine: क्रम से push (idempotency + backoff), cursor और tombstones से delta pull, foreground/नेटवर्क पर चलाओ।
3. Sync की स्थिति दिखाओ, failures और conflicts संभालो; payment, OTP, booking सिर्फ़ online।

---

## ➡️ Next Topic Suggestion
**M07. Data Sync + Conflict Resolution** — What if the same record was edited offline on the phone and on the web at the same time? Next: conflict detection (versions, vector clocks), strategies (LWW, server-wins, field merge, CRDTs), and how to show conflicts to users.
