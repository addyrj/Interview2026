# 71. CQRS Pattern
# हिंदी में: CQRS — लिखने (Commands) और पढ़ने (Queries) के लिए अलग-अलग मॉडल/डेटाबेस रखना, ताकि दोनों को अलग से तेज़ और स्केल किया जा सके

---

## 🔵 Simple Definition (English)
**CQRS (Command Query Responsibility Segregation)** separates the **write side** (commands that change state: `PlaceOrder`, `CancelOrder`) from the **read side** (queries that return data: "my orders screen", "restaurant dashboard"). Each side gets its **own model**, and often its **own datastore**: a normalized, validated **write model** and one or more denormalized, query-optimized **read models (projections)**, kept in sync via **events**.

## 🔵 सरल परिभाषा (Hindi)
CQRS में डेटा बदलने वाले काम (commands) और डेटा पढ़ने वाले काम (queries) अलग कर दिए जाते हैं।
लिखने के लिए एक सही-सलामत (normalized) मॉडल, और पढ़ने के लिए अलग तेज़ मॉडल (जैसे Elasticsearch, Redis) — दोनों events से sync होते हैं।

---

## 🔴 Problem it Solves
One model trying to serve both writes and reads struggles:
- **Reads and writes have different shapes:** writes need validation, invariants and normalization. Reads need joined, denormalized, pre-aggregated views (dashboards, search, feeds).
- **Different scale:** reads are often **100–1000×** more than writes; you want to scale them independently.
- **Complex queries** on the write DB (joins across 8 tables, aggregations) **slow down** transactional writes.
- **Many different views** of the same data: the customer app, restaurant app, admin panel, search and analytics each want a different shape.

CQRS lets each side be **optimized for its job**.

## 🔴 यह क्यों बना? (Hindi)
एक ही मॉडल से लिखना और पढ़ना दोनों करो तो दिक़्क़त: लिखने को नियम और normalized टेबल चाहिए, पढ़ने को joined, तैयार views; reads writes से सैकड़ों गुना ज़्यादा होते हैं; और भारी queries writes को धीमा कर देती हैं।
CQRS दोनों तरफ़ को अपने काम के हिसाब से अलग बनाकर तेज़ और स्केलेबल करता है।

---

## 🟢 How it Works — Step by Step

```
                       COMMANDS (write)                               QUERIES (read)
 App ── POST /orders ──► Command Handler                    App ── GET /orders/me ──► Query Handler
                          │ validate, enforce rules                                   │
                          ▼                                                           ▼
                 ┌──────────────────┐                                    ┌──────────────────────┐
                 │  Write Model DB  │                                    │  Read Model(s)       │
                 │  (Postgres,      │                                    │  - Redis: order cards│
                 │  normalized,     │──── events / CDC ────►  Projector ─►│  - Elasticsearch:    │
                 │  ACID)           │   "OrderPlaced"         (updates   │    search            │
                 └──────────────────┘   "OrderDelivered"       views)    │  - ClickHouse: stats │
                                                                         │  - Mongo: dashboards │
                                                                         └──────────────────────┘
Write path: correctness.  Read path: speed.  Sync: asynchronous (eventually consistent).
```

### Levels of CQRS (you don't have to go all the way)

```
Level 1: Separate code paths (command handlers vs query services) on the SAME DB
         → clearer code; queries may use raw SQL/views; writes use domain model
Level 2: Same DB engine, separate READ store (read replicas, materialized views, summary tables)
Level 3: Different stores per side, synced by events (Postgres → Kafka → Elastic/Redis/ClickHouse) ⭐
Level 4: + Event Sourcing — write side stores events as source of truth (Topic 72)
```

### Projections (read models)
```
A projection = a consumer that listens to events and maintains a view.

on OrderPlaced(orderId, userId, restaurant, total, ts):
   UPSERT user_order_cards[userId] += {orderId, restaurantName, total, status:"PLACED", ts}
   INCR restaurant_stats[restaurant].orders_today
on OrderStatusChanged(orderId, status):
   UPDATE user_order_cards SET status = ...
Rebuildable: replay all events / re-scan the write DB to rebuild a projection from scratch.
```

### Consistency between sides
```
Read models lag behind writes by ms–seconds (eventual consistency).
UX fixes:
  - Return the new state in the command response (client shows it immediately)
  - Read-your-writes: for the user who just wrote, read from write model for a few seconds
  - Version numbers: client waits until read model version ≥ command's version
  - Show "updating…" for aggregated dashboards
```

### When to use (and when NOT)
```
✅ Read/write load very different; many read views; complex domain with rich write rules;
   search/analytics views; event-driven microservices; high-scale feeds/dashboards
❌ Simple CRUD apps — CQRS adds complexity (two models, sync, eventual consistency) for no gain
   → start with Level 1 (separate query code) and evolve
```

## 🟢 कैसे काम करता है? (Hindi)
1. Command (जैसे PlaceOrder) write मॉडल पर जाता है — नियम जाँचे जाते हैं और Postgres में सुरक्षित सेव होता है।
2. हर बदलाव एक event (OrderPlaced) बनता है, जो Kafka/CDC से projectors तक जाता है।
3. Projectors पढ़ने वाले मॉडल अपडेट करते हैं — Redis में order cards, Elasticsearch में search, ClickHouse में stats।
4. Query (जैसे "मेरे orders") सीधे तैयार read मॉडल से — बहुत तेज़, कोई भारी join नहीं।
5. Read मॉडल कुछ सेकंड पीछे हो सकता है — इसलिए command के जवाब में नई स्थिति लौटाओ; साधारण CRUD ऐप में CQRS मत लगाओ।

---

## 🟡 Real World Example

**Swiggy / Zomato** — orders are written to a transactional store (write model). Separate read models serve the customer's "Orders" tab, the restaurant partner dashboard (live orders, today's sales), search, and analytics, all fed by order events. Each is optimized for its own query pattern and scale.

**Amazon product pages** — product data is written in catalog services, and a denormalized "detail page" read model (title, price, availability, reviews summary) is assembled and cached for very fast reads.

**Banking apps** — the ledger (write model) is strictly consistent. Account statements, spending insights and the "recent transactions" view are read models built from transaction events, sometimes lagging by seconds.

**Microsoft (where the term spread)** — Greg Young and Udi Dahan popularized CQRS in the .NET and DDD community. Many large Azure systems use it with event sourcing.

## 🟡 Real Example Hindi में
Swiggy में ऑर्डर एक transactional DB में लिखे जाते हैं; ग्राहक का "Orders" tab, रेस्टोरेंट का live dashboard, search और analytics — सब अलग read मॉडल हैं, जिन्हें order events अपडेट करते हैं।
बैंकिंग ऐप में ledger (write मॉडल) पूरी तरह सही रहता है, और statement व "spending insights" read मॉडल हैं जो कुछ सेकंड पीछे हो सकते हैं।

---

## 🟠 My Stack Example

### Level 1 — separate command and query code (same Postgres)
```
src/orders/
  commands/place-order.ts      ← validation, invariants, transaction, outbox event
  commands/cancel-order.ts
  queries/my-orders.ts         ← optimized SQL / view, returns DTOs for the screen
  queries/restaurant-live.ts
```
```ts
// commands/place-order.ts
export async function placeOrder(cmd: PlaceOrderCmd, user: User) {
  return withTx(async (tx) => {
    const menu = await loadMenu(tx, cmd.restaurantId);
    const total = priceCart(cmd.items, menu);                 // business rules on write model
    const order = await insertOrder(tx, user.id, cmd, total);
    await tx.query("INSERT INTO outbox(event_type, payload) VALUES ('OrderPlaced', $1)",
      [{ orderId: order.id, userId: user.id, restaurantId: cmd.restaurantId, total, at: new Date() }]);
    return { orderId: order.id, status: 'PLACED', total };    // return new state to client
  });
}

// queries/my-orders.ts — read-optimized SQL (could hit a replica)
export const myOrders = (userId: string, cursor?: string) => reader.query(`
  SELECT o.id, o.status, o.total, o.created_at, r.name AS restaurant, r.logo_url
  FROM orders o JOIN restaurants r ON r.id = o.restaurant_id
  WHERE o.user_id = $1 ORDER BY o.created_at DESC LIMIT 20`, [userId]);
```

### Level 3 — projector building a Redis read model (Node + Kafka)
```js
consumer.run({ eachMessage: async ({ topic, message }) => {
  const e = JSON.parse(message.value);
  if (topic === 'OrderPlaced') {
    const card = { id: e.orderId, restaurant: await restaurantName(e.restaurantId), total: e.total, status: 'PLACED', at: e.at };
    await redis.multi()
      .hSet(`order_card:${e.orderId}`, { json: JSON.stringify(card) })
      .zAdd(`user_orders:${e.userId}`, { score: Date.parse(e.at), value: String(e.orderId) })
      .hIncrBy(`rest_stats:${e.restaurantId}:${e.at.slice(0, 10)}`, 'orders', 1)
      .hIncrByFloat(`rest_stats:${e.restaurantId}:${e.at.slice(0, 10)}`, 'revenue', e.total)
      .exec();
  }
  if (topic === 'OrderStatusChanged') {
    const raw = await redis.hGet(`order_card:${e.orderId}`, 'json');
    if (raw) await redis.hSet(`order_card:${e.orderId}`, { json: JSON.stringify({ ...JSON.parse(raw), status: e.status }) });
  }
}});

// Query side: super fast "my orders"
app.get('/api/v1/me/orders', authenticate, async (req, res) => {
  const ids = await redis.zRange(`user_orders:${req.user.id}`, 0, 19, { REV: true });
  const cards = await Promise.all(ids.map((id) => redis.hGet(`order_card:${id}`, 'json')));
  res.json(cards.filter(Boolean).map((c) => JSON.parse(c)));
});
```

### FastAPI — restaurant dashboard read model in Postgres summary table
```python
# projector (consumer) keeps a denormalized table
async def on_order_placed(e):
    await db.execute(text("""
      INSERT INTO restaurant_daily_stats(restaurant_id, day, orders, revenue)
      VALUES (:r, :d, 1, :t)
      ON CONFLICT (restaurant_id, day) DO UPDATE
      SET orders = restaurant_daily_stats.orders + 1, revenue = restaurant_daily_stats.revenue + :t
    """), {"r": e["restaurantId"], "d": e["at"][:10], "t": e["total"]})

@app.get("/partner/dashboard")
async def dashboard(rid: int):
    return await db.fetch_all("SELECT * FROM restaurant_daily_stats WHERE restaurant_id=:r ORDER BY day DESC LIMIT 30", {"r": rid})
```

### Client side
```ts
// After command, update the client cache from the command response (don't wait for the projection)
const placeOrder = useMutation({ mutationFn: api.placeOrder,
  onSuccess: (o) => qc.setQueryData(['myOrders'], (old: any[] = []) => [o, ...old]) });
```

---

## ⚫ Interview Questions + Answers

**Q1: What is CQRS?**
A1: A pattern that separates the responsibility of changing state (commands) from reading state (queries) into different models, and often different datastores. The write model enforces business rules and consistency (normalized, transactional). Read models are denormalized projections optimized for specific queries and scaled independently, kept up to date asynchronously from write-side events.

**Q2: What are the benefits and costs of CQRS?**
A2: Benefits: independent scaling and optimization of reads and writes, query-specific read models (search, dashboards, feeds) without burdening the transactional DB, simpler write logic focused on invariants, and multiple views of the same data for different clients. Costs: more components and code, eventual consistency between write and read sides, projection maintenance and rebuilds, event schema evolution, and harder debugging. Overkill for simple CRUD.

**Q3: How do you keep read models in sync with the write model?**
A3: Publish domain events from the write side reliably (transactional outbox or CDC from the DB log) to a broker. Projector services consume them idempotently, in order per aggregate (partition by entity ID), and update their read stores. Track the last processed offset or version. Support full rebuilds by replaying events or re-scanning the write DB. Monitor projection lag.

**Q4: How do you deal with the user reading stale data right after a command?**
A4: Return the resulting state in the command response and update the client cache optimistically. Provide read-your-writes, routing that user's reads to the write model or primary briefly. Or include a version or sequence number in the response and have the query side wait until the projection has caught up to it (or fall back to the write model). Show "updating" for aggregate views.

**Q5: Is CQRS the same as event sourcing?**
A5: No. They're often used together but are independent. CQRS separates read and write models. Event sourcing stores state changes as an immutable sequence of events, which becomes the write-side source of truth, with current state derived by replay. You can do CQRS with a normal relational write model (state stored, events published via outbox), and event sourcing almost always uses CQRS, because querying an event log directly is impractical.

---

## 🔷 Trade-offs
✅ Advantages:
- Read and write sides optimized & scaled independently; fast tailored queries; clean domain logic.

❌ Disadvantages:
- Complexity (two models, sync pipeline, projections); eventual consistency; more infrastructure.
- Not worth it for simple CRUD.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CQRS | Separate write and read models | लिखने और पढ़ने के अलग मॉडल |
| Command | Request to change state | डेटा बदलने का आदेश |
| Query | Request to read state | डेटा पढ़ने का अनुरोध |
| Write model | Normalized, rule-enforcing model | नियम वाला लिखने का मॉडल |
| Read model / Projection | Query-optimized view | पढ़ने के लिए तैयार view |
| Projector | Consumer building read models | read मॉडल बनाने वाला |
| Domain event | Fact that something happened | कुछ हुआ, उसका तथ्य |
| Rebuild | Recreate projection from history | इतिहास से view दोबारा बनाना |

---

## ⚡ 3-Line Summary
**English:**
1. CQRS separates commands (writes, rules, normalized) from queries (reads, denormalized projections).
2. Sync read models via events (outbox/CDC → projectors); they're eventually consistent — return new state to the client.
3. Use when read/write needs differ a lot or many views exist; start simple (separate code) before separate stores.

**Hindi:**
1. CQRS = लिखने (commands) और पढ़ने (queries) के अलग मॉडल।
2. Events (outbox/CDC) से read मॉडल sync होते हैं — थोड़े पीछे, इसलिए client को नई स्थिति लौटाओ।
3. जब पढ़ने-लिखने की ज़रूरत बहुत अलग हो तब इस्तेमाल करो; पहले सिर्फ़ code अलग करो।

---

## ➡️ Next Topic Suggestion
**72. Event Sourcing** — What if, instead of storing current state, you store every change as an event and derive the state? Next: event sourcing, its powers (audit, time travel, replay) and its pains (schema evolution, complexity).
