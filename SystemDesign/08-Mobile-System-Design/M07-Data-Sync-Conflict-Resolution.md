# M07. Data Sync + Conflict Resolution
# हिंदी में: Data Sync + Conflict Resolution — जब एक ही डेटा फ़ोन पर (offline) और कहीं और (web/दूसरा फ़ोन/सर्वर) एक साथ बदल जाए, तो टकराव (conflict) पहचानना और तय करना कि आख़िरी सही मान क्या होगा

---

## 🔵 Simple Definition (English)
**Data sync** keeps copies of data on multiple devices and the server consistent over time. A **conflict** happens when the **same data is modified concurrently** in two places (e.g., a note edited offline on the phone and on the laptop, or an order cancelled on the server while the delivery app marks it delivered offline) and the changes can't simply both be applied.
Conflict resolution has two parts:
1. **Detection**: knowing that two changes were concurrent, using **version numbers** (optimistic concurrency), **ETags/If-Match**, timestamps (beware of clock skew), **vector clocks / version vectors**, or hybrid logical clocks.
2. **Resolution strategy**:
   - **Last-Writer-Wins (LWW)**, per record or per field
   - **Server-wins / client-wins**
   - **Field-level 3-way merge**
   - **Domain rules** (state machines, monotonic statuses)
   - **Operation-based** changes (send intents like "increment qty", not final state)
   - **CRDTs** (data types that merge automatically and deterministically)
   - **OT** (operational transforms, for collaborative text)
   - **Manual resolution** (ask the user)

## 🔵 सरल परिभाषा (Hindi)
Data sync = फ़ोन, web, दूसरे devices और सर्वर पर डेटा की कॉपियाँ समय के साथ एक जैसी रखना। Conflict = एक ही डेटा दो जगह एक साथ बदल गया (फ़ोन पर offline note बदला और laptop पर भी; या सर्वर पर order cancel हुआ और delivery ऐप ने offline "delivered" कर दिया)।
दो काम: पहचानना (version नंबर, ETag/If-Match, vector clocks — सिर्फ़ समय पर भरोसा ख़तरनाक क्योंकि फ़ोन की घड़ी ग़लत हो सकती है) और सुलझाना (आख़िरी लिखने वाला जीते, सर्वर जीते, field-level merge, business नियम, "1 बढ़ाओ" जैसे operations, CRDTs, OT, या यूज़र से पूछो)।

---

## 🔴 Problem it Solves
Offline-first (M06) and multi-device apps **will** have concurrent edits. Without a strategy:
- **Silent data loss**: the phone syncs an old copy and overwrites the newer laptop edit (the "lost update" problem).
- **Invalid states**: a cancelled order is "delivered", or stock goes negative after two offline sales of the last item.
- **Clock bugs**: a phone with its clock set 2 hours ahead always "wins" with timestamp-based LWW.
- **Duplicates**: retried creates produce two records.
- **Zombie data**: one device deletes a record and another edits it, so the record resurrects or disappears unexpectedly.
A deliberate conflict model gives **predictable, correct and explainable results**.

## 🔴 यह क्यों बना? (Hindi)
Offline-first और कई devices वाले ऐप में एक साथ बदलाव होंगे ही। बिना नियम के: पुरानी कॉपी नए बदलाव को चुपचाप मिटा दे (lost update); cancel हुआ order "delivered" बन जाए या आख़िरी item दो बार बिक जाए; फ़ोन की घड़ी 2 घंटे आगे हो तो वो हमेशा जीते; retry से duplicate records; एक device ने हटाया, दूसरे ने बदला — record वापस ज़िंदा या ग़ायब।
सोचा-समझा conflict model = अनुमानित, सही और समझाने लायक नतीजे।

---

## 🟢 How it Works — Step by Step

### Detection with versions (optimistic concurrency)

```
Server row: note#42 { text: "Buy milk", version: 7 }
Phone (offline) edited from version 7 → push { id: 42, baseVersion: 7, text: "Buy milk + eggs" }
Laptop edited first                   → push { id: 42, baseVersion: 7, text: "Buy milk, bread" } → OK, version 8

Phone push arrives: baseVersion 7 ≠ current 8  → CONFLICT detected (concurrent edits)
                    (if baseVersion == current → apply, version++)
HTTP form: PUT /notes/42  If-Match: "v7"  → 412 Precondition Failed / 409 Conflict + current state
```

### Why timestamps alone are dangerous

```
Device clocks drift / users change time / time zones → "latest timestamp wins" can pick the WRONG one
Use server-assigned versions/sequence numbers for ordering, or Hybrid Logical Clocks (HLC: physical time
+ logical counter) when devices must order events among themselves
Vector clocks / version vectors (per-replica counters) detect true concurrency in multi-master systems
(Topic 90) — e.g., {phone: 3, laptop: 5} vs {phone: 4, laptop: 4} → concurrent
```

### Resolution strategies (choose per data type!)

```
┌───────────────────────────┬──────────────────────────────────────────┬─────────────────────────────┐
│ Strategy                  │ How                                      │ Good for                    │
├───────────────────────────┼──────────────────────────────────────────┼─────────────────────────────┤
│ Last-Writer-Wins (record) │ Latest (by server order/HLC) replaces    │ Simple prefs, profile photo │
│                           │ whole record                             │ — accepts some loss         │
│ LWW per FIELD             │ Each field keeps its own latest value    │ Profiles, settings, forms   │
│                           │ (name from phone, address from web)      │ (Figma uses per-property)   │
│ Server-authoritative      │ Server decides; client rebases or drops  │ Orders, payments, inventory │
│ + domain rules            │ (state machine: CANCELLED is terminal)   │                             │
│ 3-way merge               │ Compare base, mine, theirs; merge non-   │ Notes, documents (non-real- │
│                           │ overlapping changes; true clash → user   │ time), config files         │
│ Operation-based           │ Send intents: "qty += 1", "add tag X",   │ Carts, counters, likes,     │
│                           │ "append message" → commutative ops       │ tags, chat (append-only)    │
│ CRDTs                     │ Data types with mathematically guaranteed│ Collaborative editing, local│
│                           │ convergence (counters, sets, maps, text) │ -first apps (Yjs, Automerge)│
│ OT (operational transform)│ Transform concurrent text ops via server │ Google Docs-style real-time │
│ Manual (user chooses)     │ Show both versions / "conflicted copy"   │ Files, important documents  │
└───────────────────────────┴──────────────────────────────────────────┴─────────────────────────────┘
```

### Domain rules example: delivery status (monotonic state machine)

```
Allowed: PLACED → ACCEPTED → PICKED_UP → OUT_FOR_DELIVERY → DELIVERED
         any non-terminal → CANCELLED
Conflict: server says CANCELLED (customer cancelled at 7:01), partner app (offline) pushes DELIVERED (7:03)
→ Rule: CANCELLED wins unless DELIVERED has proof of delivery before cancellation time → flag for ops
→ Client receives 409 with server state → rolls back local status, shows "Order was cancelled"
Inventory: never let offline devices decrement shared stock blindly → reserve on server, or treat
offline sales as "pending" requiring server confirmation; compensate (refund) if oversold
```

### CRDT basics (what to say)

```
G-Counter: each replica increments its own slot; value = sum → merges by taking max per slot
PN-Counter: two G-Counters (increments, decrements)
OR-Set: add/remove with unique tags → concurrent add & remove resolved deterministically (add wins)
LWW-Register / LWW-Map: per-key timestamps (HLC) → deterministic winner
Sequence CRDTs (RGA, YATA in Yjs; Automerge): collaborative text/lists
Pros: offline + peer-to-peer merges always converge, no central coordination needed
Cons: metadata overhead (tombstones), harder to enforce business invariants (e.g., stock ≥ 0)
```

### Deletes vs edits

```
Delete on device A, edit on device B (concurrent):
  - "Delete wins" (tombstone beats edit) → simple, predictable (most apps)
  - "Edit wins / resurrect" → for collaborative content where losing an edit is worse
Keep tombstones until all clients have synced past them (or force re-bootstrap for very old clients)
```

### Sync protocol with conflict handling (client side)

```
1. PUSH pending change with baseVersion (or operation)
2. Server: if no conflict → apply → return new version
           if conflict → apply strategy:
              auto-merge → return merged record + version
              reject     → 409 + current server record (+ reason code)
3. Client: on merged/accepted → replace local, clear pending
           on 409 → run client-side policy: rebase (reapply my op on top), drop, or mark CONFLICT for user
4. PULL server changes; skip records with local pending changes or merge them (same rules)
```

## 🟢 कैसे काम करता है? (Hindi)
1. पहचान: हर record का version; बदलाव भेजते समय `baseVersion` भी भेजो — सर्वर का version वही है तो लागू करो और version बढ़ाओ, अलग है तो conflict।
2. सिर्फ़ फ़ोन के समय पर भरोसा मत करो (घड़ी ग़लत हो सकती है) — सर्वर के version/sequence या Hybrid Logical Clock; कई masters में vector clocks।
3. हर डेटा के लिए अलग नियम: settings/profile → field-level LWW; orders/payments/stock → सर्वर तय करे + business नियम (CANCELLED अंतिम); notes → 3-way merge; cart/likes/chat → operations ("qty +1", append); साथ में editing → CRDT (Yjs) या OT; ज़रूरी files → यूज़र चुने।
4. Delivery उदाहरण: सर्वर पर CANCELLED और फ़ोन से offline DELIVERED आए → CANCELLED जीते (जब तक cancel से पहले delivery का सबूत न हो) → फ़ोन को 409, local वापस, "Order cancel हो गया" दिखाओ।
5. Delete बनाम edit: ज़्यादातर ऐप में delete जीतता है (tombstone), सहयोगी content में edit; tombstones तब तक रखो जब तक सब clients sync न कर लें।

---

## 🟡 Real World Example

**Google Docs** — uses operational transformation with a central server to merge concurrent keystrokes in real time, so all users converge on the same document.

**Figma** — its multiplayer system (described in Figma's 2019 engineering blog) is server-authoritative with last-writer-wins per property on objects, inspired by CRDTs but simplified because a central server orders changes.

**Dropbox / Google Drive desktop** — when the same file is edited on two machines offline, they keep both and create a "conflicted copy". That's manual resolution for opaque files.

**WhatsApp / chat apps** — avoid most conflicts by design: messages are append-only and immutable (edits and deletes are new events), ordered by the server. A great example of choosing a conflict-free data model.

**Apple Notes / Reminders (CloudKit), Linear, Automerge/Yjs-based apps** — use record versioning (CloudKit server change tokens and record conflict errors) or CRDT-based sync for local-first experiences.

## 🟡 Real Example Hindi में
Google Docs सर्वर के साथ OT से एक साथ टाइप हुए बदलाव मिलाता है; Figma सर्वर-प्रधान है और हर object की हर property पर last-writer-wins (CRDT से प्रेरित); Dropbox दो जगह offline बदली file की "conflicted copy" बना देता है।
WhatsApp में ज़्यादातर conflict होते ही नहीं — messages सिर्फ़ जुड़ते हैं (append-only), edit/delete भी नए events हैं, क्रम सर्वर तय करता है — सही data model चुनकर conflict से बचना।

---

## 🟠 My Stack Example

### Postgres: optimistic concurrency with version column (FastAPI)
```python
@app.put("/notes/{note_id}")
async def update_note(note_id: str, body: NoteUpdate, user=Depends(current_user)):
    row = await db.fetchrow("""
        UPDATE notes SET title = $3, body = $4, version = version + 1, updated_at = now()
        WHERE id = $1 AND owner_id = $2 AND version = $5
        RETURNING id, title, body, version""", note_id, user.id, body.title, body.body, body.base_version)
    if row:
        return dict(row)                                   # applied
    current = await db.fetchrow("SELECT id, title, body, version, base_snapshot FROM notes WHERE id=$1 AND owner_id=$2", note_id, user.id)
    if not current:
        raise HTTPException(404)
    merged = three_way_merge(base=body.base, mine=body, theirs=current)     # field-level
    if merged.clean:
        return await save_merged(current["version"], merged)              # auto-resolved
    raise HTTPException(409, detail={"code": "CONFLICT", "server": dict(current), "conflictingFields": merged.fields})
```

### Field-level merge helper (TypeScript, used client or server side)
```ts
type Rec = Record<string, unknown>;
export function threeWayMerge(base: Rec, mine: Rec, theirs: Rec) {
  const result: Rec = { ...theirs }; const conflicts: string[] = [];
  for (const k of new Set([...Object.keys(mine), ...Object.keys(theirs)])) {
    const b = base[k], m = mine[k], t = theirs[k];
    if (eq(m, t)) continue;                 // same either way
    if (eq(m, b)) continue;                 // only theirs changed → keep theirs
    if (eq(t, b)) { result[k] = m; continue; } // only mine changed → take mine
    conflicts.push(k);                      // both changed differently → true conflict
  }
  return { result, conflicts, clean: conflicts.length === 0 };
}
```

### Domain rule: monotonic order status (Node backend)
```js
const RANK = { PLACED: 0, ACCEPTED: 1, PICKED_UP: 2, OUT_FOR_DELIVERY: 3, DELIVERED: 4 };
const TERMINAL = new Set(['DELIVERED', 'CANCELLED']);

app.post('/partner/orders/:id/status', auth, idempotent, async (req, res) => {
  const { status, occurredAt, proof } = req.body;           // occurredAt from device (advisory only)
  const order = await Orders.get(req.params.id);
  if (TERMINAL.has(order.status) && order.status !== status) {
    return res.status(409).json({ error: { code: 'ORDER_TERMINAL', serverStatus: order.status }, order });
  }
  if (status !== 'CANCELLED' && RANK[status] <= RANK[order.status]) return res.json(order);  // stale/duplicate → no-op
  const updated = await Orders.transition(order.id, status, { proof, deviceTime: occurredAt });
  res.json(updated);
});
```

### Client: handle 409 by rolling back / marking conflict
```ts
async function send(item: OutboxRow) {
  try { return await http.post(item.url, item.payload, { headers: { 'Idempotency-Key': item.id } }); }
  catch (e: any) {
    if (e.status === 409) {
      const server = e.data?.order ?? e.data?.server;
      await db.runAsync(`UPDATE orders SET status=?, sync_status='SYNCED' WHERE id=?`, [server.status, item.entityId]);  // server wins
      notify(`Order ${item.entityId} was ${server.status.toLowerCase()} — your update wasn't applied`);
      return { resolved: true };
    }
    throw e;
  }
}
```

### Operation-based cart (no lost updates across devices)
```ts
// Instead of PUT /cart { items: [...] } (whole state → last writer wins), send ops:
await http.post('/cart/ops', { ops: [{ op: 'add', itemId: 'paneer-tikka', qty: 1, opId: uuid() }] });
// Server applies ops in order, dedupes by opId → phone + web edits combine correctly
```

### CRDT for collaborative notes (Yjs) — converges offline
```ts
import * as Y from 'yjs';
const doc = new Y.Doc();
const text = doc.getText('note');
text.insert(0, 'Shopping: ');
const update = Y.encodeStateAsUpdate(doc);          // store locally (SQLite blob) & send when online
// On receiving remote update: Y.applyUpdate(doc, remoteUpdate) → both replicas converge, no conflicts
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you detect conflicts during sync?**
A1: Track a version per record (an integer incremented by the server on each change, or an ETag). Clients send the base version they edited from. If it matches the current server version, the change applies and the version increments. If not, another change happened concurrently, which is a conflict. HTTP expresses this with `If-Match` and 412/409 responses. For multi-master or peer-to-peer replication, use version vectors or vector clocks to distinguish concurrent from causally ordered updates. Avoid relying on device timestamps due to clock skew. Use server ordering or hybrid logical clocks.

**Q2: What conflict resolution strategies exist and how do you choose?**
A2: Last-writer-wins per record or per field (simple, accepts some loss), server-authoritative with domain rules (orders, payments, inventory), 3-way merge of non-overlapping field changes with manual resolution for true clashes (notes, documents), operation-based updates with commutative intents (counters, carts, sets, append-only logs), CRDTs for automatic convergence in collaborative or local-first apps, OT for real-time text with a central server, and user-driven resolution (conflicted copies) for opaque files. Choose per data type based on how harmful losing an update is, which invariants must hold, and how often concurrent edits occur.

**Q3: Why is last-writer-wins with device timestamps risky?**
A3: Device clocks can be wrong, drift, or be deliberately changed, and time zones or DST mistakes happen. A device with a fast clock would always win, silently discarding newer edits. LWW also inherently loses one of two concurrent changes. Mitigate by using server-assigned ordering, hybrid logical clocks, per-field LWW to reduce the blast radius, or merge/operation-based strategies for important data.

**Q4: How do you handle a delivery app marking an order delivered offline after it was cancelled?**
A4: The server is authoritative and enforces an order state machine where CANCELLED and DELIVERED are terminal. When the offline update arrives, the server compares it with the current state. Since the order is already cancelled, it rejects with 409 and the current state, or, if there is proof of delivery that predates the cancellation, flags it for operations review. The client rolls back the local status, informs the partner, and stops related queued actions. Idempotency keys prevent duplicates on retries, and stale or duplicate transitions are treated as no-ops.

**Q5: What are CRDTs and when would you use them?**
A5: Conflict-free Replicated Data Types are data structures (counters, sets, maps, registers, sequences and text) whose merge operation is commutative, associative and idempotent, so replicas that receive the same updates in any order converge to the same state without coordination. Use them for collaborative editing, local-first apps with peer-to-peer or offline-heavy usage, and presence or reactions. The trade-offs are metadata and tombstone overhead, complexity, and difficulty enforcing global invariants (like non-negative stock or unique usernames), which still need server validation.

---

## 🔷 Trade-offs
✅ LWW: simplest — ❌ silent loss of concurrent edits.
✅ Server-authoritative + rules: correct business invariants — ❌ requires connectivity to confirm; user sees rollbacks.
✅ Merge/operations: preserve more intent — ❌ more design work per entity.
✅ CRDT/OT: great collaboration — ❌ complexity, metadata, invariant enforcement.
✅ Manual resolution: no wrong auto-decisions — ❌ burdens users.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Conflict | Concurrent incompatible changes | एक साथ टकराते बदलाव |
| Optimistic concurrency | Detect via version on write | लिखते समय version जाँच |
| Base version | Version the edit started from | जिस version से बदला |
| Lost update | One edit overwrites another silently | चुपचाप बदलाव मिटना |
| LWW | Last-writer-wins | आख़िरी लिखने वाला जीते |
| 3-way merge | Merge using base, mine, theirs | तीन कॉपी से मिलाना |
| Vector clock | Per-replica counters for causality | हर replica का counter |
| HLC | Hybrid logical clock | मिली-जुली घड़ी |
| CRDT | Auto-merging replicated data type | अपने-आप मिलने वाला डेटा |
| OT | Operational transformation | text बदलावों का रूपांतरण |

---

## ⚡ 3-Line Summary
**English:**
1. Detect conflicts with server versions/ETags (baseVersion, If-Match) or version vectors — not device timestamps.
2. Resolve per data type: field-level LWW, server-authoritative domain rules, 3-way merge, operation-based intents, CRDT/OT, or user choice.
3. Model data to avoid conflicts (append-only, operations), keep invariants on the server, handle deletes via tombstones, and roll back clearly on 409.

**Hindi:**
1. Conflict सर्वर version/ETag (baseVersion, If-Match) या vector clocks से पहचानो — फ़ोन के समय से नहीं।
2. हर डेटा के लिए नियम: field LWW, सर्वर + business नियम, 3-way merge, operations, CRDT/OT, या यूज़र चुने।
3. ऐसा data model कि conflict कम हों (append-only, operations); नियम सर्वर पर; delete के लिए tombstone; 409 पर साफ़ rollback।

---

## ➡️ Next Topic Suggestion
**M08. Networking on Mobile (Flaky Network, Retry, Batching)** — Sync only works if network calls are resilient and efficient. Next: mobile radio behaviour, timeouts, retries, batching, compression, HTTP/2–3 and adapting to network quality.
