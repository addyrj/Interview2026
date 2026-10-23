---

# Q185. PostgreSQL LISTEN / NOTIFY — Real-Time Events
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL only

---

## ❓ Question
What is LISTEN/NOTIFY in PostgreSQL? How does it work? Build a real-time notification system using LISTEN/NOTIFY with Node.js. When should you use it vs a dedicated message queue?

---

## 💡 Quick Concept (2 lines only)
LISTEN/NOTIFY is PostgreSQL's built-in pub/sub — any connection can NOTIFY a channel, all LISTENing connections receive it asynchronously after COMMIT. No polling, no external message broker needed for DB-driven events.
हिंदी: PostgreSQL का built-in pub/sub। NOTIFY = message publish, LISTEN = subscribe। COMMIT के बाद async notification — polling की जरूरत नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- HOW IT WORKS
-- ============================================

-- Session A (subscriber):
LISTEN new_orders;        -- subscribe to channel "new_orders"
LISTEN user_updates;      -- can listen to multiple channels

-- Session B (publisher):
BEGIN;
  INSERT INTO orders (user_id, amount, status)
  VALUES (42, 149.99, 'pending');
  NOTIFY new_orders, '{"order_id": 1234, "user_id": 42}';  -- payload (max 8000 chars)
COMMIT;
-- ← Notification fires AFTER COMMIT (not during transaction)
-- If transaction rolls back → NOTIFY is NOT sent! ← transactionally safe!

-- Session A receives immediately after Session B commits:
-- Asynchronous notification received:
-- channel = "new_orders"
-- payload = {"order_id": 1234, "user_id": 42}
-- pid     = 12345  (Session B's backend PID)

-- ============================================
-- TRIGGER-BASED NOTIFY (practical pattern)
-- ============================================

-- Auto-notify on every INSERT — no need to add NOTIFY to every query!

CREATE OR REPLACE FUNCTION notify_new_order()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM pg_notify(
    'new_orders',
    json_build_object(
      'id',      NEW.id,
      'user_id', NEW.user_id,
      'amount',  NEW.amount,
      'status',  NEW.status
    )::text
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_notify_new_order
  AFTER INSERT ON orders
  FOR EACH ROW
  EXECUTE FUNCTION notify_new_order();

-- Now ANY insert triggers a notification automatically:
INSERT INTO orders (user_id, amount, status) VALUES (42, 149.99, 'pending');
-- ← Automatically fires: pg_notify('new_orders', '{"id":1, "user_id":42, ...}')

-- ============================================
-- UPDATE NOTIFICATION (notify on status change)
-- ============================================

CREATE OR REPLACE FUNCTION notify_order_status_change()
RETURNS TRIGGER AS $$
BEGIN
  IF OLD.status IS DISTINCT FROM NEW.status THEN  -- only fire on actual status change
    PERFORM pg_notify(
      'order_status_changed',
      json_build_object(
        'id',         NEW.id,
        'user_id',    NEW.user_id,
        'old_status', OLD.status,
        'new_status', NEW.status
      )::text
    );
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_order_status
  AFTER UPDATE OF status ON orders
  FOR EACH ROW
  EXECUTE FUNCTION notify_order_status_change();

-- ============================================
-- NODE.JS SUBSCRIBER (pg library)
-- ============================================

/*
const { Client } = require('pg');

async function startOrderListener() {
  const client = new Client({
    host: 'localhost',
    database: 'myapp',
    user: 'postgres',
    password: 'secret'
  });

  await client.connect();

  // Subscribe to channels
  await client.query('LISTEN new_orders');
  await client.query('LISTEN order_status_changed');

  console.log('Listening for order events...');

  // Handle notifications
  client.on('notification', async (msg) => {
    const payload = JSON.parse(msg.payload);

    if (msg.channel === 'new_orders') {
      console.log('New order:', payload);
      // Push to WebSocket clients:
      wss.clients.forEach(ws => {
        if (ws.userId === payload.user_id) {
          ws.send(JSON.stringify({ type: 'order_created', data: payload }));
        }
      });
      // Or add to job queue:
      await queue.add('send-confirmation-email', payload);
    }

    if (msg.channel === 'order_status_changed') {
      console.log('Order status changed:', payload);
      // Real-time update to customer UI
      await pushNotificationToUser(payload.user_id, {
        message: `Order ${payload.id} is now ${payload.new_status}`
      });
    }
  });

  // Handle connection errors — reconnect on disconnect!
  client.on('error', async (err) => {
    console.error('Listener connection error:', err);
    await reconnectWithBackoff();
  });
}

// IMPORTANT: Use a DEDICATED connection for LISTEN (not from connection pool!)
// Pool connections are borrowed/returned — UNLISTEN happens on connection return
// A dedicated persistent connection is required for LISTEN
startOrderListener();
*/

-- ============================================
-- ARCHITECTURE: POSTGRES NOTIFY + WEBSOCKETS
-- ============================================

/*
                 ┌──────────────────────────────────────┐
                 │           PostgreSQL                  │
                 │                                       │
  Application ──→│ INSERT/UPDATE → TRIGGER → pg_notify  │
                 │                          (channel)   │
                 └──────────────────────────────────────┘
                                    │
                            NOTIFY delivered
                                    │
                 ┌──────────────────▼──────────────────┐
                 │         Node.js Listener             │
                 │  (dedicated pg.Client connection)    │
                 │  client.on('notification', handler)  │
                 └──────────────────────────────────────┘
                          │               │
               Process event        Push to WebSocket
               (send email,          clients / SSE /
                queue job)           real-time UI update
*/

-- ============================================
-- MULTI-INSTANCE SCALING (Multiple Node Processes)
-- ============================================

/*
Problem: 3 Node.js instances, each has a LISTEN connection.
A notification goes to ALL listeners — all 3 instances will process the same event!

Solution 1: Use a coordinator (Redis pub/sub or sticky sessions)
Solution 2: Idempotent processing — each handler checks if already processed:
  - Insert to processed_events table with ON CONFLICT DO NOTHING
  - Only process if INSERT succeeds (1 row affected)

Solution 3: Advisory lock — first to acquire processes, others skip:
  IF NOT pg_try_advisory_lock(order_id) THEN RETURN; END IF;
  -- process event
  pg_advisory_unlock(order_id);

In practice: for 3-5 instances, idempotency is simplest.
For larger deployments: use a message queue (NOTIFY triggers queue push, consumers process from queue)
*/

-- ============================================
-- WHEN TO USE LISTEN/NOTIFY vs MESSAGE QUEUE
-- ============================================

/*
Use LISTEN/NOTIFY when:
  ✅ Events originate from DB changes (INSERT/UPDATE triggers)
  ✅ Small payload (< 8000 chars)
  ✅ Low-to-medium volume (< 10,000 events/second)
  ✅ You want to avoid external infrastructure (Redis, RabbitMQ, Kafka)
  ✅ Event triggers need to be transactionally safe (NOTIFY on rollback = not sent)
  ✅ Simple fan-out to connected clients (admin dashboard, real-time updates)

Use message queue (Redis Pub/Sub, RabbitMQ, Kafka) when:
  ❌ LISTEN/NOTIFY doesn't persist messages — if listener is down, notifications are lost!
     → Kafka/RabbitMQ retain messages until consumed
  ❌ Need guaranteed delivery (exactly-once, at-least-once semantics)
  ❌ Very high volume (100,000+ events/sec)
  ❌ Complex routing (topic filters, dead-letter queues, delayed messages)
  ❌ Cross-service messaging (events from non-Postgres sources)
  ❌ Large payloads (> 8KB)

Hybrid: NOTIFY + outbox pattern
  INSERT into orders + INSERT into outbox table (same transaction)
  Trigger NOTIFY → app reads from outbox table
  Outbox guarantees persistence even if listener was down
*/

-- ============================================
-- PRACTICAL: ONLINE USER STATUS
-- ============================================

-- Track which users are currently connected via LISTEN:
CREATE TABLE user_presence (
  user_id    INT PRIMARY KEY,
  status     VARCHAR(20) DEFAULT 'online',
  last_seen  TIMESTAMPTZ DEFAULT NOW()
);

-- When user connects: notify others
-- When user disconnects (pg connection closes): trigger cleanup
CREATE OR REPLACE FUNCTION notify_user_online()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM pg_notify('user_presence', json_build_object(
    'user_id', NEW.user_id,
    'status', NEW.status
  )::text);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_user_presence
  AFTER INSERT OR UPDATE ON user_presence
  FOR EACH ROW EXECUTE FUNCTION notify_user_online();
```

---

## 🔍 Why This Works (3 lines max)
NOTIFY fires after COMMIT within the same transaction context — this transactional guarantee means no spurious notifications for rolled-back changes. Each listening connection is maintained by PostgreSQL's background process and receives notifications via the async message channel without polling. Triggers automate NOTIFY so application code doesn't need to manually call pg_notify on every relevant operation.
हिंदी: NOTIFY COMMIT के बाद fire होता है — rollback पर notification नहीं जाती (transactionally safe)। Trigger + pg_notify = auto notification, application code में manually नहीं।

---

## ⚡ Alternative Solution

```sql
-- pg_notify as a function call (can be used anywhere in PL/pgSQL):
SELECT pg_notify('channel_name', 'payload string');
-- Or from Node.js directly:
-- await client.query("SELECT pg_notify('channel', $1)", [JSON.stringify(data)]);

-- NOTIFY with no payload:
NOTIFY my_channel;  -- listener receives channel name, empty payload

-- Check who is listening (admin):
SELECT pid, wait_event_type, wait_event, application_name
FROM pg_stat_activity
WHERE wait_event = 'ClientRead'
  AND query ILIKE '%listen%';
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Using a pooled connection for LISTEN
-- const pool = new Pool({...});
-- pool.query('LISTEN orders');  -- ← pool may return connection, listen stops when returned!
-- ✅ Fix: dedicated non-pooled Client for LISTEN:
-- const listenerClient = new Client({...});
-- await listenerClient.connect();
-- await listenerClient.query('LISTEN orders');
-- Keep this connection alive for the app's lifetime

-- ❌ Wrong: Assuming NOTIFY works across databases
-- NOTIFY is per-database — if your app has multiple databases,
-- each database needs its own listener connection
-- ✅ One listener per database

-- ❌ Wrong: Sending large payloads via NOTIFY
-- Max payload = 8000 bytes
-- ✅ Fix: send only the ID in NOTIFY, subscriber fetches full data from DB:
-- PERFORM pg_notify('new_order', NEW.id::text);
-- App: SELECT * FROM orders WHERE id = $1 (on notification)

-- ❌ Wrong: Not handling listener reconnection
-- If the listener connection drops (DB restart, network blip):
-- the subscription is gone and new notifications are missed!
-- ✅ Fix: reconnect loop with backoff + re-subscribe after reconnect
```

---

## 🎯 Interview Tip (1 line)
Say: "LISTEN/NOTIFY is PostgreSQL's built-in pub/sub — I use it with triggers so any INSERT/UPDATE automatically notifies a channel transactionally (no notification if the transaction rolls back). The subscriber is a dedicated persistent pg.Client in Node.js, not a pool connection. Trade-off: messages are not persisted — if the listener is down, events are lost — so for critical events I combine it with an outbox table."

---

## 🔗 Related Questions
→ Q181 (JSONB operators) | Q190 (materialized views) | Q196 (row-level security) | Q044 (multi-tenancy)
