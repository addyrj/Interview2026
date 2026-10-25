# 191. Socket.io Rooms + Namespaces
# हिंदी में: Socket.io Rooms + Namespaces

---

## 🔵 Simple Definition (English)
**Rooms** let you group arbitrary connected sockets under a label so you can broadcast to just that subset (e.g., all users watching order #123). **Namespaces** split your entire Socket.io server into separate logical endpoints (e.g., `/chat`, `/admin`) each with its own connection lifecycle, events, and middleware — like having multiple mini Socket.io servers sharing one underlying connection.

## 🔵 सरल परिभाषा (Hindi)
**Rooms** connected sockets को किसी label के नीचे group करते हैं ताकि सिर्फ उस subset को broadcast किया जा सके (जैसे order #123 देख रहे सब users)। **Namespaces** पूरे Socket.io server को अलग logical endpoints में बांटते हैं (`/chat`, `/admin`) — हर एक की अपनी connection lifecycle, events, middleware होती है।

---

## 🔴 Problem it Solves
```
WITHOUT ROOMS/NAMESPACES:
  io.emit() sends to EVERY connected client — no way to scope
  You'd have to manually track socket.id lists per feature
  Admin events and chat events mixed in the same event names → collisions
  No clean way to isolate auth/middleware per feature area

WITH ROOMS:
  socket.join('order_123') → scoped broadcast to just that group
  Automatic cleanup — socket leaves all rooms on disconnect

WITH NAMESPACES:
  io.of('/admin') → totally separate auth middleware, events, connections
  Keeps features isolated: /chat traffic never leaks into /admin logic
```

## 🔴 यह क्यों बना? (Hindi)
```
बिना rooms/namespaces: io.emit() सबको जाता है, scope करने का तरीका नहीं
Manually socket.id list track करना पड़ता
Rooms: socket.join() से scoped group बनाओ, disconnect पर auto cleanup
Namespaces: /admin और /chat को पूरी तरह अलग रखो — अलग middleware, events
```

---

## 🟢 How it Works — Step by Step

Step 1 → **Rooms**: any socket can `join(roomName)` any number of rooms, and `leave(roomName)`; Socket.io automatically removes it from all rooms on disconnect
Step 2 → Broadcasting: `io.to(room).emit(...)` sends to everyone in that room (sender included if they're in it); `socket.to(room).emit(...)` excludes the sender
Step 3 → **Namespaces**: created with `io.of('/admin')` — returns its own namespace object with its own `connection` event, middleware (`.use()`), and rooms
Step 4 → Default namespace is `/` — every `io.on('connection')` without `.of()` is scoped to `/`
Step 5 → A client must explicitly connect to a namespace: `io('http://host/admin')` — this opens a SEPARATE logical connection (though often multiplexed over the same transport)

## 🟢 कैसे काम करता है? (Hindi)
```
1. Rooms: socket.join(room), socket.leave(room) — disconnect पर auto remove
2. Broadcasting: io.to(room) sender को include करता है, socket.to(room) exclude करता है
3. Namespaces: io.of('/admin') से अलग namespace बनता है — अपनी middleware, events
4. Default namespace '/' होता है
5. Client को namespace से explicitly connect करना होता है: io('host/admin')
```

---

## 🟡 Real World Example
**Flipkart live seller dashboard vs customer order tracking:** Flipkart's backend runs one Socket.io server but needs two very different real-time features: (1) customers tracking their order status, and (2) sellers watching live sales dashboards. These use separate **namespaces** — `/orders` and `/sellers` — each with its own auth (customer JWT vs seller API key) and its own event names, so a bug in the seller dashboard code can never accidentally leak into customer sockets. Within `/orders`, each order gets its own **room** (`order_98765`) so only the customer and the delivery partner assigned to that order receive updates — not every customer on the platform.

## 🟡 Real Example Hindi mein
**Flipkart:** एक ही Socket.io server पर दो features: customer order tracking और seller dashboard। दोनों के लिए अलग namespaces — `/orders` और `/sellers` — अलग auth, अलग events। `/orders` के अंदर हर order का अपना room (`order_98765`) होता है ताकि सिर्फ संबंधित customer और delivery partner को update मिले।

---

## 💻 Code Example — Basic

```javascript
// rooms-basic.js
// Run: npm install socket.io   then  node rooms-basic.js
const { Server } = require('socket.io');
const io = new Server(5000);

io.on('connection', (socket) => {
  // Client tells server which "order room" it wants to watch
  socket.on('watchOrder', (orderId) => {
    socket.join(`order_${orderId}`);          // add socket to this room
    console.log(`${socket.id} joined order_${orderId}`);
  });

  // Simulates a delivery-status update being pushed to that room
  socket.on('updateStatus', ({ orderId, status }) => {
    // Send ONLY to sockets that joined this specific order's room
    io.to(`order_${orderId}`).emit('statusChanged', { orderId, status });
  });

  socket.on('stopWatching', (orderId) => {
    socket.leave(`order_${orderId}`);          // remove from room
  });
});

console.log('Rooms demo server on port 5000');
```

## 💻 Code Example — Advanced

```javascript
// namespaces-advanced.js
// Production pattern: separate namespaces for customers vs admins,
// each with its own auth middleware and rooms.
const { Server } = require('socket.io');
const http = require('http');

const server = http.createServer();
const io = new Server(server, { cors: { origin: '*' } });

// --- Customer namespace ---
const customerNs = io.of('/customers');

customerNs.use((socket, next) => {
  const token = socket.handshake.auth?.token;
  if (!token) return next(new Error('Customer auth required'));
  socket.customerId = token;  // simplified — verify JWT in real app
  next();
});

customerNs.on('connection', (socket) => {
  socket.on('trackOrder', (orderId) => {
    socket.join(`order_${orderId}`);
  });
  console.log(`Customer ${socket.customerId} connected on /customers`);
});

// --- Admin namespace: completely separate auth + events ---
const adminNs = io.of('/admin');

adminNs.use((socket, next) => {
  const apiKey = socket.handshake.auth?.apiKey;
  if (apiKey !== 'secret-admin-key') {
    return next(new Error('Unauthorized admin'));  // reject bad admins
  }
  next();
});

adminNs.on('connection', (socket) => {
  console.log('Admin connected on /admin');

  // Admin triggers a push that reaches customers in the OTHER namespace
  socket.on('pushOrderUpdate', ({ orderId, status }) => {
    // Note: must reference customerNs explicitly — namespaces don't share rooms
    customerNs.to(`order_${orderId}`).emit('statusChanged', { orderId, status });
  });
});

server.listen(5000, () => console.log('Namespace demo on port 5000'));
```

---

## 🟠 Express.js Integration

```javascript
// REST endpoint triggers a namespace+room scoped real-time push
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server);
const customerNs = io.of('/customers');

customerNs.on('connection', (socket) => {
  socket.on('trackOrder', (orderId) => socket.join(`order_${orderId}`));
});

app.use(express.json());

// Internal service calls this when an order's status changes in the DB
app.post('/internal/orders/:id/status', (req, res) => {
  const { status } = req.body;
  // Push to just the room for this order, inside the /customers namespace
  customerNs.to(`order_${req.params.id}`).emit('statusChanged', {
    orderId: req.params.id,
    status,
  });
  res.json({ pushed: true });
});

server.listen(3000, () => console.log('Express + namespaced rooms on 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Assuming rooms are shared across namespaces
✅ Correct: Rooms are scoped PER namespace — `order_123` in `/customers` is a completely different room than `order_123` in `/`. Always emit from the correct namespace object.

```javascript
// Wrong — io.to() here operates on default '/' namespace, won't reach /customers sockets
io.to('order_123').emit('update', data);

// Right — explicitly target the namespace that holds those sockets
io.of('/customers').to('order_123').emit('update', data);
```

❌ Mistake 2: Not cleaning up room membership on business logic changes (e.g., user stops tracking an order but code never calls `leave()`), causing stale broadcasts and memory growth over long-lived connections.
✅ Correct: Explicitly `socket.leave(room)` when the client's "interest" in that room ends, and rely on automatic cleanup only for full disconnects.

❌ Mistake 3: Putting sensitive, high-privilege admin events in the default namespace mixed with public customer events — any customer socket code change risks accidentally exposing admin events.
✅ Correct: Isolate privilege boundaries into separate namespaces with their own auth middleware.

---

## 🧠 Tricky Interview Question

```javascript
const ns1 = io.of('/a');
const ns2 = io.of('/b');

ns1.on('connection', (socket) => socket.join('team1'));
ns2.on('connection', (socket) => socket.join('team1'));

ns1.to('team1').emit('msg', 'hello from a');
```
Answer: Only sockets connected to namespace `/a` AND in room `team1` receive the message. Even though `ns2` also has sockets in a room literally named `'team1'`, **rooms are namespace-scoped** — `team1` under `/a` and `team1` under `/b` are entirely separate room registries internally. `ns1.to('team1').emit()` can never reach a socket connected only to `/b`, regardless of matching room names. This trips people up because the room *name* is identical, but Socket.io keeps a per-namespace room map.

---

## ⚫ Interview Questions + Answers

Q1: What's the default namespace in Socket.io?
A1: `/` — when you write `io.on('connection', ...)` without calling `.of()`, you're implicitly working with the default namespace. All clients that connect with just `io(url)` (no path) land here.

Q2: Can a single client be connected to multiple namespaces at once?
A2: Yes. `io('http://host/chat')` and `io('http://host/admin')` from the same client create two logically separate Socket.io connections (often multiplexed over the same underlying transport/engine.io connection to save resources), each with its own socket.id, events, and middleware.

Q3: How do you broadcast to everyone in a room except the sender vs including the sender?
A3: `socket.to(room).emit(event, data)` excludes the sender. `io.to(room).emit(event, data)` (or the namespace equivalent `nsObj.to(room).emit(...)`) includes every socket in that room, including the sender if it's a member.

Q4: Are rooms shared between namespaces?
A4: No. Each namespace maintains its own independent room registry. A room named `order_123` in the `/customers` namespace is unrelated to a room with the same name in `/admin` or the default `/` namespace.

Q5: When would you use namespaces instead of just rooms?
A5: Use namespaces when you need to separate entire FEATURES/concerns with different authentication, middleware, and event vocabularies (e.g., public chat vs internal admin tooling vs a separate IoT device channel). Use rooms when sockets share the same auth/feature context but you need to scope broadcasts to a dynamic subset (e.g., "everyone watching this specific order" within the customer-facing feature).

---

## 🔷 When to Use + When Not to Use
✅ Use rooms when:
- You need dynamic, per-resource broadcast scoping (chat room, order tracking, live auction)

✅ Use namespaces when:
- You have distinct features/privilege levels needing separate auth and event namespaces on one server

❌ Avoid when:
- Your app has only a handful of total users/connections and a single global broadcast is simpler — added complexity of rooms/namespaces isn't justified for a tiny app

---

## 📊 Visual Diagram
```
SOCKET.IO SERVER
────────────────────────────────────────────────
  Namespace: /customers            Namespace: /admin
  ┌─────────────────────┐          ┌──────────────────┐
  │ Room: order_123      │          │ (no rooms needed) │
  │  ├─ socket A         │          │  socket D          │
  │  └─ socket B         │          └──────────────────┘
  │ Room: order_456      │
  │  └─ socket C         │
  └─────────────────────┘

  ns.to('order_123').emit() → reaches A, B only (within /customers)
  Admin namespace completely isolated — different auth, different rooms
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Room | Dynamic group of sockets for scoped broadcast | Scoped broadcast के लिए sockets का dynamic group |
| Namespace | Isolated communication channel | Isolated communication channel |
| join/leave | Add/remove socket from a room | Socket को room में जोड़ना/हटाना |
| of() | Creates/accesses a namespace | Namespace बनाने/access करने का method |
| Default namespace | The `/` namespace | `/` नाम का default namespace |

---

## ⚡ 3-Line Summary
English:
1. Rooms scope broadcasts to a dynamic subset of sockets within a namespace; namespaces isolate entire features with their own auth and events.
2. Rooms are namespace-scoped — identical room names in different namespaces are unrelated.
3. Use `io.of('/name')` for features needing separate auth, and `socket.join()/leave()` for dynamic resource-based grouping.

Hindi:
1. Rooms namespace के अंदर sockets के subset को scope करते हैं; namespaces पूरे features को अलग करते हैं।
2. अलग namespaces में same नाम के rooms भी अलग-अलग होते हैं।
3. अलग auth वाले features के लिए namespace, dynamic grouping के लिए rooms use करो।

---

## ➡️ Next Topic
**192. Server-Sent Events (SSE)** — A simpler one-directional alternative for server-to-client streaming.
