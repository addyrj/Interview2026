# 241. Event Sourcing in Node
# हिंदी में: Node में Event Sourcing

---

## 🔵 Simple Definition (English)
Event sourcing stores every change to application state as an immutable sequence of events (e.g., "AccountCreated", "MoneyDeposited", "MoneyWithdrawn"), rather than just storing the current state. The current state is derived by replaying all events from the beginning — the event log IS the source of truth, not a snapshot table.

## 🔵 सरल परिभाषा (Hindi)
Event sourcing application state के हर change को events की एक immutable sequence के रूप में store करता है (जैसे "AccountCreated", "MoneyDeposited", "MoneyWithdrawn"), सिर्फ current state store करने के बजाय। Current state सभी events को शुरुआत से replay करके derive किया जाता है — event log ही source of truth है, कोई snapshot table नहीं।

---

## 🔴 Problem it Solves
Traditional systems overwrite old state with new state (UPDATE in SQL), losing history — you can't easily answer "what was this account's balance last Tuesday?" or "why did this value change?" without separate audit logging bolted on. Event sourcing solves this by making history a first-class citizen: every change is permanently recorded, you can reconstruct state at ANY point in time, debug issues by replaying exactly what happened, and rebuild entirely new read models/projections from history whenever requirements change — without losing any information.

## 🔴 यह क्यों बना? (Hindi)
Traditional systems old state को new state से overwrite करते हैं (SQL में UPDATE), history खो जाती है — बिना अलग से audit logging जोड़े आप आसानी से यह answer नहीं दे सकते "पिछले Tuesday इस account का balance क्या था?" या "यह value क्यों बदली?"। Event sourcing history को first-class citizen बनाकर यह solve करता है: हर change permanently record होता है, आप किसी भी point in time पर state reconstruct कर सकते हैं, exactly जो हुआ उसे replay करके issues debug कर सकते हैं, और requirements बदलने पर history से बिना कोई information खोए पूरी तरह नए read models/projections rebuild कर सकते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Instead of updating a row, every state-changing action is recorded as an immutable **event** appended to an event store (e.g., "AccountOpened", "Deposited $100", "Withdrew $30").
Step 2 → Events are stored in order, typically grouped by an aggregate ID (e.g., all events for "account_42").
Step 3 → To get the CURRENT state of an entity, you load all its events and **replay** them in order, applying each one's effect (this is often done via a "reducer" function).
Step 4 → For performance, systems often cache a **snapshot** of state at intervals, so replay only needs to start from the last snapshot forward, not from the very beginning.
Step 5 → New events are only ever APPENDED — never modified or deleted — preserving a perfect audit trail.
Step 6 → Read models/projections (as in CQRS) can be rebuilt at any time by replaying the event log from scratch, enabling new views of historical data without losing anything.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Row update करने के बजाय, हर state-changing action एक immutable **event** के रूप में event store में append होता है (जैसे "AccountOpened", "Deposited $100", "Withdrew $30")।
Step 2 → Events order में store होते हैं, typically एक aggregate ID से group होते हैं (जैसे "account_42" के सभी events)।
Step 3 → किसी entity का CURRENT state पाने के लिए, आप उसके सभी events load करके उन्हें order में **replay** करते हैं, हर एक का effect apply करते हुए (अक्सर एक "reducer" function से)।
Step 4 → Performance के लिए, systems अक्सर intervals पर state का एक **snapshot** cache करते हैं, ताकि replay सिर्फ last snapshot से forward शुरू हो, शुरुआत से नहीं।
Step 5 → नए events सिर्फ APPEND होते हैं — कभी modify या delete नहीं होते — perfect audit trail preserve करते हैं।
Step 6 → Read models/projections (CQRS की तरह) कभी भी event log को scratch से replay करके rebuild किए जा सकते हैं, historical data के नए views enable करते हुए बिना कुछ खोए।

---

## 🟡 Real World Example
**Paytm wallet ledger:** A wallet's balance is never directly "set" — it's derived from a complete, immutable history of events: "WalletCreated", "MoneyAdded ₹500", "MoneySpent ₹200", "CashbackCredited ₹20". If a dispute arises ("why is my balance ₹320?"), Paytm can replay the exact sequence of events for that wallet to show precisely how the balance was derived — this auditability is critical for financial systems and regulatory compliance, which is why event sourcing is common in banking/fintech.

## 🟡 Real Example Hindi mein
**Paytm wallet ledger:** एक wallet का balance कभी directly "set" नहीं होता — यह events की एक complete, immutable history से derive होता है: "WalletCreated", "MoneyAdded ₹500", "MoneySpent ₹200", "CashbackCredited ₹20"। अगर कोई dispute आए ("मेरा balance ₹320 क्यों है?"), Paytm उस wallet के exact events sequence को replay करके दिखा सकता है कि balance exactly कैसे derive हुआ — यह auditability financial systems और regulatory compliance के लिए critical है, इसलिए event sourcing banking/fintech में common है।

---

## 💻 Code Example — Basic

```javascript
// event-sourcing-basic.js
// Run: node event-sourcing-basic.js
// Demonstrates core idea: state is DERIVED by replaying events, never stored directly

// ─── EVENT STORE: an append-only log of events, per aggregate (wallet) ───────
const eventStore = [];   // in real systems: a dedicated event-store DB (EventStoreDB, or a table)

function appendEvent(aggregateId, type, payload) {
  eventStore.push({ aggregateId, type, payload, timestamp: Date.now() });
}

// ─── COMMANDS: validate and append events (never mutate state directly) ─────
function createWallet(walletId) {
  appendEvent(walletId, 'WalletCreated', {});
}

function addMoney(walletId, amount) {
  appendEvent(walletId, 'MoneyAdded', { amount });
}

function spendMoney(walletId, amount) {
  const currentBalance = getWalletBalance(walletId);
  if (currentBalance < amount) throw new Error('Insufficient balance');
  appendEvent(walletId, 'MoneySpent', { amount });
}

// ─── PROJECTION: derive current state by REPLAYING all events in order ──────
function getWalletBalance(walletId) {
  const events = eventStore.filter(e => e.aggregateId === walletId);

  // Reducer: fold over events to compute current balance
  return events.reduce((balance, event) => {
    if (event.type === 'MoneyAdded') return balance + event.payload.amount;
    if (event.type === 'MoneySpent') return balance - event.payload.amount;
    return balance;   // WalletCreated doesn't affect balance
  }, 0);
}

// Demo
createWallet('wallet_1');
addMoney('wallet_1', 500);
spendMoney('wallet_1', 200);
addMoney('wallet_1', 20);   // cashback

console.log('Current balance:', getWalletBalance('wallet_1'));   // 320
console.log('Full event history:', eventStore.filter(e => e.aggregateId === 'wallet_1'));
```

## 💻 Code Example — Advanced

```javascript
// event-sourcing-advanced.js — snapshots for performance + point-in-time reconstruction
class EventSourcedWallet {
  constructor(walletId) {
    this.walletId = walletId;
    this.events = [];
    this.snapshots = [];   // periodic cached states: { afterEventIndex, balance }
  }

  append(type, payload) {
    this.events.push({ type, payload, timestamp: Date.now() });

    // Take a snapshot every 100 events, to avoid replaying the ENTIRE history every time
    if (this.events.length % 100 === 0) {
      this.snapshots.push({
        afterEventIndex: this.events.length,
        balance: this.getCurrentBalance(),
      });
    }
  }

  // Get current balance efficiently: start from the LATEST snapshot, replay only remaining events
  getCurrentBalance() {
    const latestSnapshot = this.snapshots[this.snapshots.length - 1];
    const startIndex = latestSnapshot ? latestSnapshot.afterEventIndex : 0;
    let balance = latestSnapshot ? latestSnapshot.balance : 0;

    for (let i = startIndex; i < this.events.length; i++) {
      const event = this.events[i];
      if (event.type === 'MoneyAdded') balance += event.payload.amount;
      if (event.type === 'MoneySpent') balance -= event.payload.amount;
    }
    return balance;
  }

  // POINT-IN-TIME RECONSTRUCTION: what was the balance at a specific point in history?
  getBalanceAtEventIndex(index) {
    let balance = 0;
    for (let i = 0; i < index && i < this.events.length; i++) {
      const event = this.events[i];
      if (event.type === 'MoneyAdded') balance += event.payload.amount;
      if (event.type === 'MoneySpent') balance -= event.payload.amount;
    }
    return balance;
  }

  deposit(amount) {
    if (amount <= 0) throw new Error('Deposit must be positive');
    this.append('MoneyAdded', { amount });
  }

  withdraw(amount) {
    if (this.getCurrentBalance() < amount) throw new Error('Insufficient balance');
    this.append('MoneySpent', { amount });
  }
}

// Demo
const wallet = new EventSourcedWallet('wallet_42');
wallet.deposit(1000);
wallet.withdraw(300);
wallet.deposit(50);

console.log('Current balance:', wallet.getCurrentBalance());          // 750
console.log('Balance after event 1:', wallet.getBalanceAtEventIndex(1)); // 1000 (before withdrawal)
console.log('Full audit trail:', wallet.events);
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const app = express();
app.use(express.json());

// In-memory event store keyed by wallet ID (use a real DB/event store in production)
const eventStores = new Map();

function getEvents(walletId) {
  if (!eventStores.has(walletId)) eventStores.set(walletId, []);
  return eventStores.get(walletId);
}

function computeBalance(events) {
  return events.reduce((bal, e) => {
    if (e.type === 'MoneyAdded') return bal + e.amount;
    if (e.type === 'MoneySpent') return bal - e.amount;
    return bal;
  }, 0);
}

app.post('/wallets/:id/deposit', (req, res) => {
  const events = getEvents(req.params.id);
  events.push({ type: 'MoneyAdded', amount: req.body.amount, at: new Date() });
  res.json({ balance: computeBalance(events) });
});

app.post('/wallets/:id/withdraw', (req, res) => {
  const events = getEvents(req.params.id);
  const currentBalance = computeBalance(events);
  if (currentBalance < req.body.amount) return res.status(400).json({ error: 'Insufficient balance' });

  events.push({ type: 'MoneySpent', amount: req.body.amount, at: new Date() });
  res.json({ balance: computeBalance(events) });
});

// Full audit trail endpoint — only possible because we kept EVERY event, not just final state
app.get('/wallets/:id/history', (req, res) => {
  res.json({ events: getEvents(req.params.id) });
});

app.listen(3000, () => console.log('Event-sourced wallet API on 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Allowing events to be modified or deleted after being appended
✅ Correct: Events must be strictly immutable and append-only — if a mistake is made, append a CORRECTING event, don't edit history

```javascript
// Wrong — "fixing" a past event by mutating it directly
eventStore[2].payload.amount = 100;   // breaks the audit trail's integrity

// Right — append a correction event
appendEvent(walletId, 'AmountCorrected', { originalEventIndex: 2, correctedAmount: 100 });
```

❌ Mistake 2: Replaying the ENTIRE event history on every single read, with no snapshotting, at scale
✅ Correct: Use periodic snapshots so replay only covers events since the last snapshot

```javascript
// Wrong — replaying 1 million events every time you need the current balance
function getBalance(events) { return events.reduce(reducer, 0); }   // fine for small histories, slow at scale

// Right — snapshot + incremental replay (see Advanced example)
```

---

## 🧠 Tricky Interview Question

```javascript
// An event-sourced order aggregate has events:
// [OrderPlaced, ItemAdded, ItemRemoved, ItemAdded, OrderCancelled]
// A developer wants to "undo" the cancellation by deleting the OrderCancelled event.
// Why is this the wrong approach in event sourcing?
```
Answer: Deleting or mutating a past event breaks the fundamental invariant of event sourcing — the event log is supposed to be an immutable, trustworthy historical record. If events can be silently deleted, you lose auditability (you can no longer prove what actually happened and when) and risk corrupting any downstream read models/snapshots that were already built assuming that event occurred. The correct approach is to append a NEW compensating event — e.g., "OrderReactivated" — which, when replayed, results in the desired current state while preserving the true, complete history that the cancellation did happen and was later reversed.

---

## ⚫ Interview Questions + Answers

Q1: What is the fundamental difference between event sourcing and traditional CRUD persistence?
A1: Traditional CRUD stores and overwrites CURRENT state only (an UPDATE replaces the old value, losing it). Event sourcing stores every CHANGE as an immutable event; current state is a derived/computed value obtained by replaying the full (or snapshot-optimized) event history. This means event sourcing inherently preserves complete history, enables audit trails, and allows rebuilding any past or present state, which traditional CRUD cannot do without bolting on separate audit logging.

Q2: Why are snapshots used in event sourcing, and what trade-off do they introduce?
A2: Snapshots cache the computed state at a point in time so that reconstructing current state doesn't require replaying potentially millions of events from the very beginning — instead, you load the nearest snapshot and replay only the events since then. The trade-off: snapshots are a performance optimization, NOT the source of truth (the event log remains authoritative); snapshots must be invalidated/regenerated correctly, and bugs in snapshot logic can silently produce wrong "current state" if not carefully kept consistent with the actual event replay logic.

Q3: How does event sourcing relate to CQRS, and are they always used together?
A3: They're commonly paired but are independent patterns. Event sourcing is about HOW state is persisted (as an event log rather than current-state snapshots). CQRS is about separating write (command) and read (query) models. In a system using both, commands produce events (event sourcing), and read-model projections are built by subscribing to and replaying those events (fulfilling CQRS's "separate read model" concept). You can do event sourcing without CQRS (reconstructing state directly from events for both reads and writes) and CQRS without event sourcing (using normal CRUD on the write side but separate read models).

Q4: What challenges does event sourcing introduce for schema evolution (versioning events)?
A4: Since old events are immutable and must be replayable forever, changing an event's shape (e.g., renaming a field, changing its structure) requires careful versioning — either supporting multiple event schema versions in your reducer/replay logic (upcasting old events to the new shape when read), or writing migration tooling that rewrites/augments historical events. This is one of the trickier operational aspects of event sourcing, since you can't simply "ALTER TABLE" an immutable append-only log the way you might with a traditional schema.

Q5: What are good and bad use cases for event sourcing?
A5: Good: financial/ledger systems (wallets, banking) where a complete, tamper-evident audit trail is legally/business-critically important; systems that benefit from being able to "replay" history to debug or rebuild projections; domains with complex temporal queries ("what was X at time T?"). Bad: simple CRUD apps where current state is all that matters and audit history has no real value — the added complexity of events, replay logic, and snapshotting isn't justified, and a plain database table is simpler and sufficient.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A full audit trail / history of changes is a business or regulatory requirement (finance, healthcare, compliance-heavy domains)
- You need to reconstruct past states or support "what happened and why" debugging
- You're already using CQRS and want events to drive read-model projections

❌ Avoid when:
- The domain is simple CRUD with no real need for history/audit
- The team isn't prepared for the added complexity of replay logic, snapshotting, and event schema versioning
- Strong, simple, immediately consistent reads of current state are all that's required

---

## 📊 Visual Diagram
```
TRADITIONAL (state overwritten, history lost):
  balance: 500 ──UPDATE──▶ balance: 300 ──UPDATE──▶ balance: 320
  (no record of HOW we got to 320)

EVENT SOURCING (every change preserved, state derived):
  [WalletCreated] → [MoneyAdded +500] → [MoneySpent -200] → [MoneyAdded +20]
                                                                      │
                                                            replay all events
                                                                      ▼
                                                            current balance = 320
                                                      (full history always available)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event store | Append-only log of all events | सभी events का append-only log |
| Aggregate | Entity whose state is derived from its events | अपने events से state derive करने वाला entity |
| Replay | Reconstructing state by reapplying events | Events reapply करके state reconstruct करना |
| Snapshot | Cached state at a point, for faster replay | किसी point का cached state, faster replay के लिए |
| Projection | A read model built from events | Events से बना read model |

---

## ⚡ 3-Line Summary
**English:**
1. Event sourcing stores every state change as an immutable event; current state is derived by replaying events, not stored directly.
2. This gives complete auditability and the ability to reconstruct state at any point in history.
3. Snapshots solve the performance cost of replaying long histories; events must remain immutable and append-only forever.

**Hindi:**
1. Event sourcing हर state change को एक immutable event के रूप में store करता है; current state events replay करके derive होता है, directly store नहीं होता।
2. यह complete auditability और history के किसी भी point पर state reconstruct करने की ability देता है।
3. Snapshots long histories replay करने की performance cost solve करते हैं; events हमेशा immutable और append-only रहने चाहिए।

---

## ➡️ Next Topic
**242. API Gateway Pattern** — Centralizing routing, auth, and cross-cutting concerns in front of microservices.
