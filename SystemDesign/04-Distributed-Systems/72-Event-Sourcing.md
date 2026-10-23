# 72. Event Sourcing
# हिंदी में: Event Sourcing — मौजूदा स्थिति (state) की जगह हर बदलाव को एक event के रूप में हमेशा के लिए सेव करना; मौजूदा स्थिति उन events को दोबारा चलाकर (replay) निकाली जाती है

---

## 🔵 Simple Definition (English)
In **event sourcing**, the source of truth is an **append-only log of events** describing everything that happened to an entity (`AccountOpened`, `MoneyDeposited ₹500`, `MoneyWithdrawn ₹200`), rather than a row holding only the **current state** (`balance = 300`). The current state is computed by **replaying** the events (often sped up with **snapshots**). Events are **immutable**: you never update or delete them; you append new ones (e.g. `WithdrawalReversed`).

## 🔵 सरल परिभाषा (Hindi)
Event sourcing में "अभी balance = ₹300" सेव करने की जगह हर घटना सेव होती है — खाता खुला, ₹500 जमा, ₹200 निकाले।
मौजूदा स्थिति इन events को शुरू से जोड़कर निकलती है। Events कभी बदले या मिटाए नहीं जाते — ग़लती सुधारनी हो तो नया event जोड़ते हैं।

---

## 🔴 Problem it Solves
A normal table stores **only the latest state**. You lose **how and why** it got there:
- "Why is this balance ₹300?" → no history (unless you built separate audit tables).
- Bugs that corrupt state can't be traced or fixed retroactively.
- New questions about the past ("how many users removed items from cart before checkout last year?") can't be answered.
- Updates overwrite data → concurrency conflicts, lost information.

Event sourcing gives:
- **Complete audit trail** (required in finance, healthcare, legal).
- **Time travel:** reconstruct state at any past moment.
- **Replay:** fix a bug in projection logic and rebuild state correctly; create **new read models** from old history.
- **Natural integration** with event-driven systems and CQRS.

## 🔴 यह क्यों बना? (Hindi)
साधारण टेबल सिर्फ़ आख़िरी स्थिति रखती है — "balance ₹300 क्यों?" का जवाब नहीं, bug से बिगड़ा डेटा पीछे जाकर ठीक नहीं होता, पुराने इतिहास पर नए सवाल नहीं पूछ सकते।
Event sourcing पूरा इतिहास (audit), किसी भी समय की स्थिति (time travel), और bug ठीक करके दोबारा replay — सब देता है।

---

## 🟢 How it Works — Step by Step

### Event store (append-only)

```
stream: wallet-42
┌─────┬──────────────────┬────────────────────────────┬──────────────────────┐
│ ver │ type             │ data                       │ timestamp            │
├─────┼──────────────────┼────────────────────────────┼──────────────────────┤
│  1  │ WalletOpened     │ { userId: 42 }             │ 2024-10-01 10:00     │
│  2  │ MoneyAdded       │ { amount: 500, ref: upi_1 }│ 2024-10-01 10:05     │
│  3  │ MoneySpent       │ { amount: 200, order: 9001}│ 2024-10-02 13:20     │
│  4  │ RefundCredited   │ { amount: 50, order: 9001 }│ 2024-10-02 15:00     │
└─────┴──────────────────┴────────────────────────────┴──────────────────────┘
Current state = fold(events): 0 + 500 − 200 + 50 = 350
```

### Command handling flow

```
Command "Spend ₹100"
  1. Load stream wallet-42 (from snapshot + newer events) → rebuild state (balance 350, version 4)
  2. Validate business rule: balance ≥ 100 ✓
  3. Produce new event(s): MoneySpent {amount: 100}
  4. Append with OPTIMISTIC CONCURRENCY: "append at version 5 only if current version is 4"
       → if someone else appended first → conflict → reload & retry
  5. Publish event → projections / other services update (CQRS read models)
```

### Snapshots (performance)
```
Stream with 1,000,000 events → replay is slow.
Every N events (e.g. 500), save snapshot {state, version}.
Load = latest snapshot + events after it.
```

### Projections (read side — always paired with CQRS)
```
Events ──► Projector ──► "wallet_balances" table (for quick reads)
                     ──► "monthly_spend_by_category" (analytics)
                     ──► "fraud_signals" (new use-case, built by replaying ALL history)
Projections are disposable: drop & rebuild by replaying events.
```

### Hard parts

```
1. Event schema evolution: events are forever → versioned events (MoneyAdded_v2), upcasters that
   transform old events when read, never change meaning of old events
2. Eventual consistency of projections (read side lags)
3. Querying: can't "SELECT WHERE balance > 1000" on events → need projections
4. GDPR "right to be forgotten" vs immutable log → crypto-shredding (encrypt personal data per user,
   delete the key), or store PII outside events
5. Complexity & learning curve; many teams over-apply it
6. Long streams need snapshots; event store choice (EventStoreDB, Kafka?, Postgres table)
```

### Event sourcing vs event-driven vs CQRS (clarify in interviews)
```
Event-driven architecture: services communicate by publishing events (Topic 87). State may be normal tables.
CQRS: separate read & write models (Topic 71).
Event sourcing: the WRITE MODEL's source of truth IS the event log.
Kafka alone isn't an event store for event sourcing in most cases (no per-entity optimistic
concurrency, retention limits) — often used to DISTRIBUTE events, with Postgres/EventStoreDB storing them.
```

### When to use
```
✅ Ledgers/financial systems, audit-heavy domains, workflows with rich history (insurance claims,
   order lifecycles), collaborative editing, systems needing temporal queries/replays
❌ Simple CRUD, content sites, systems where history has no business value
```

## 🟢 कैसे काम करता है? (Hindi)
1. हर entity (जैसे wallet-42) की एक event stream है; नए events सिर्फ़ जोड़े जाते हैं।
2. Command आने पर: पुराने events (snapshot + बाद वाले) चलाकर मौजूदा स्थिति बनाओ, नियम जाँचो, नया event जोड़ो।
3. जोड़ते समय version check (optimistic concurrency) — बीच में किसी और ने जोड़ा हो तो दोबारा कोशिश।
4. Projections events से पढ़ने वाली टेबल बनाते हैं; ग़लती हो तो सब मिटाकर replay से दोबारा बना लो।
5. मुश्किलें: events का format हमेशा के लिए (versioning), GDPR deletion, और जटिलता — साधारण CRUD में मत लगाओ।

---

## 🟡 Real World Example

**Banking ledgers & accounting** — accounting has been "event sourced" for centuries: a ledger of journal entries, where the balance is derived and mistakes are corrected with reversing entries, never by erasing. Modern core banking (Thought Machine Vault, Mambu) and fintech ledgers follow this.

**Git** — a commit history is an event log of changes. Checking out any commit is time travel, and branches are alternate streams.

**LMAX Exchange** — a high-performance trading platform that processes millions of orders per second with an in-memory, event-sourced business logic processor, recovering state by replaying the event journal.

**Shopping cart analytics** — retailers that store cart events (`ItemAdded`, `ItemRemoved`) rather than final cart state can analyze abandonment patterns, which state-only systems lose.

**Walmart, Netflix (some systems), Zalando** — have written about event sourcing in inventory and order domains.

## 🟡 Real Example Hindi में
बैंक का ledger सदियों से event sourcing ही है — हर entry लिखी जाती है, balance उनसे निकलता है, ग़लती पर उल्टी entry (reversal), मिटाना नहीं।
Git भी event log है — किसी भी पुराने commit पर जाना time travel है। LMAX exchange करोड़ों orders events replay करके संभालता है।

---

## 🟠 My Stack Example

### Simple event store in Postgres
```sql
CREATE TABLE events (
  stream_id   TEXT NOT NULL,                 -- 'wallet-42'
  version     INT  NOT NULL,                 -- 1,2,3... per stream
  type        TEXT NOT NULL,
  data        JSONB NOT NULL,
  metadata    JSONB NOT NULL DEFAULT '{}',   -- correlationId, userId, schemaVersion
  global_seq  BIGSERIAL,                     -- ordering across all streams (for projections)
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (stream_id, version)           -- ← optimistic concurrency: duplicate version fails
);
CREATE TABLE snapshots (stream_id TEXT PRIMARY KEY, version INT NOT NULL, state JSONB NOT NULL);
```

### Wallet aggregate (Node/TypeScript)
```ts
type WalletEvent =
  | { type: 'WalletOpened'; data: { userId: string } }
  | { type: 'MoneyAdded'; data: { amount: number; ref: string } }
  | { type: 'MoneySpent'; data: { amount: number; orderId: string } };

type Wallet = { balance: number; version: number };

const apply = (s: Wallet, e: WalletEvent): Wallet => {
  switch (e.type) {
    case 'WalletOpened': return { ...s, balance: 0 };
    case 'MoneyAdded':   return { ...s, balance: s.balance + e.data.amount };
    case 'MoneySpent':   return { ...s, balance: s.balance - e.data.amount };
  }
};

async function load(streamId: string): Promise<Wallet> {
  const snap = await db.oneOrNone('SELECT version, state FROM snapshots WHERE stream_id=$1', [streamId]);
  let state: Wallet = snap ? { ...snap.state, version: snap.version } : { balance: 0, version: 0 };
  const rows = await db.any('SELECT version, type, data FROM events WHERE stream_id=$1 AND version>$2 ORDER BY version', [streamId, state.version]);
  for (const r of rows) state = { ...apply(state, r), version: r.version };
  return state;
}

export async function spend(userId: string, amount: number, orderId: string) {
  const stream = `wallet-${userId}`;
  for (let attempt = 0; attempt < 3; attempt++) {
    const w = await load(stream);
    if (w.balance < amount) throw new AppError(422, 'INSUFFICIENT_BALANCE');   // business rule
    try {
      await db.none('INSERT INTO events(stream_id, version, type, data) VALUES ($1,$2,$3,$4)',
        [stream, w.version + 1, 'MoneySpent', { amount, orderId }]);
      return;                                                                   // appended ✅
    } catch (e: any) {
      if (e.code !== '23505') throw e;          // unique violation = concurrent append → retry
    }
  }
  throw new AppError(409, 'CONCURRENT_MODIFICATION');
}
```

### Projection: balances table (rebuildable)
```js
// tails events by global_seq, idempotent via checkpoint
async function projectBalances() {
  const { last } = await db.one("SELECT last_seq AS last FROM projection_checkpoints WHERE name='balances'");
  const evts = await db.any('SELECT * FROM events WHERE global_seq > $1 ORDER BY global_seq LIMIT 500', [last]);
  for (const e of evts) {
    await db.tx(async (t) => {
      const userId = e.stream_id.replace('wallet-', '');
      const delta = e.type === 'MoneyAdded' ? e.data.amount : e.type === 'MoneySpent' ? -e.data.amount : 0;
      await t.none('INSERT INTO wallet_balances(user_id, balance) VALUES ($1,$2) ON CONFLICT (user_id) DO UPDATE SET balance = wallet_balances.balance + $2', [userId, delta]);
      await t.none("UPDATE projection_checkpoints SET last_seq=$1 WHERE name='balances'", [e.global_seq]);
    });
  }
}
// Rebuild: TRUNCATE wallet_balances; reset checkpoint to 0; run projector.
```

### Event versioning (upcaster)
```js
function upcast(e) {
  if (e.type === 'MoneyAdded' && !e.metadata.schemaVersion) {      // v1 had amount in rupees float
    return { ...e, data: { amountPaise: Math.round(e.data.amount * 100), ref: e.data.ref }, metadata: { schemaVersion: 2 } };
  }
  return e;
}
```

### Tools
```
EventStoreDB (purpose-built), Marten (.NET on Postgres), Axon (Java), Eventuous,
Postgres table (above) + Kafka to distribute events, Temporal (workflow history is event-sourced internally)
```

---

## ⚫ Interview Questions + Answers

**Q1: What is event sourcing?**
A1: Persisting an entity's state as an ordered, append-only sequence of domain events, instead of only its current state. Current state is derived by replaying (folding) the events, optimized with snapshots. Events are immutable facts, and corrections are new compensating events. The event log is the write-side source of truth, typically combined with CQRS projections for queries.

**Q2: What are the benefits of event sourcing?**
A2: A complete, tamper-evident audit trail. Temporal queries: state at any point in time. The ability to rebuild or fix read models by replaying, and to create new projections from historical data. Natural fit with event-driven integration. Optimistic concurrency per stream. Better debugging, since you can see exactly what happened. It's valuable for finance, compliance-heavy and workflow-rich domains.

**Q3: What are the main challenges?**
A3: Event schema evolution (events live forever, so you need versioning and upcasters). Eventually consistent projections. You can't query the current state directly, so projections are required. Performance of long streams needs snapshots. Deleting personal data conflicts with immutability (crypto-shredding or keeping PII outside events). Steeper learning curve and more infrastructure. Easy to misapply to simple CRUD.

**Q4: How do you handle concurrency in event sourcing?**
A4: Optimistic concurrency per stream: the command loads the aggregate at version N and appends new events with an expected version of N+1. The event store enforces uniqueness (for example a primary key on stream_id and version). If another writer appended first, the append fails, and the command reloads the latest state, revalidates business rules and retries, or returns a conflict.

**Q5: How is event sourcing different from just publishing events to Kafka?**
A5: Event-driven publishing means services emit events about changes, but their source of truth may still be normal tables, and events are notifications. In event sourcing the events are the source of truth for the write model: state is reconstructed from them, they're retained forever, and appends are concurrency-controlled per aggregate. Kafka is great for distributing events, but on its own it usually lacks per-entity optimistic concurrency and indefinite, queryable per-stream storage, so event-sourced systems often store events in a DB or event store and stream them via Kafka.

---

## 🔷 Trade-offs
✅ Advantages:
- Full history/audit, time travel, replayable projections, natural event integration, no lost updates.

❌ Disadvantages:
- Complexity, schema evolution forever, eventual consistency of reads, snapshots needed, GDPR challenges.
- Overkill for most CRUD domains.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event sourcing | Store events as source of truth | events को सच का स्रोत बनाना |
| Event store | Append-only event database | सिर्फ़ जोड़ने वाला event DB |
| Stream | Events of one entity | एक entity के events |
| Replay | Rebuild state from events | events से स्थिति दोबारा बनाना |
| Snapshot | Saved state at a version | किसी version की सेव स्थिति |
| Projection | Read model built from events | events से बना read मॉडल |
| Upcaster | Converts old event versions | पुराने event को नए रूप में बदलना |
| Optimistic concurrency | Append only if version matches | version मिलने पर ही जोड़ना |
| Crypto-shredding | Delete key to erase encrypted data | key मिटाकर डेटा मिटाना |
| Compensating event | New event that corrects a past one | ग़लती सुधारने वाला नया event |

---

## ⚡ 3-Line Summary
**English:**
1. Event sourcing stores every change as an immutable event; current state = replay (with snapshots).
2. Gives audit trail, time travel, replayable/new projections; pairs with CQRS for queries.
3. Costs: schema evolution, eventual consistency, complexity, GDPR — use for ledgers/audit-heavy domains, not plain CRUD.

**Hindi:**
1. Event sourcing = हर बदलाव एक अटल event; मौजूदा स्थिति = replay (snapshots के साथ)।
2. पूरा इतिहास, time travel, दोबारा बनने वाले projections; queries के लिए CQRS के साथ।
3. क़ीमत: event versioning, eventual consistency, जटिलता — ledger/audit वाले domain में ही इस्तेमाल करो।

---

## ➡️ Next Topic Suggestion
**73. Circuit Breaker Pattern** — Now the resilience patterns. When a downstream service is failing, calling it again and again makes everything worse. Next: circuit breakers (closed, open, half-open) to fail fast and recover gracefully.
