# 187. gRPC with Node.js
# हिंदी में: gRPC with Node.js — High-Performance Service-to-Service Communication

---

## 🔵 Simple Definition (English)
**gRPC** (Google Remote Procedure Call) is a high-performance RPC framework where you define service methods and message types in a `.proto` file, and gRPC generates client/server code that lets you call remote functions as if they were local — using HTTP/2 and binary **Protocol Buffers** serialization instead of JSON over HTTP/1.1. It's built for fast, strongly-typed service-to-service (microservice) communication.

## 🔵 सरल परिभाषा (Hindi)
**gRPC** (Google Remote Procedure Call) एक high-performance RPC framework है जहाँ तुम `.proto` file में service methods और message types define करते हो, और gRPC client/server code generate करता है जो remote functions को local की तरह call करने देता है — HTTP/2 और binary **Protocol Buffers** serialization use करके, JSON over HTTP/1.1 की जगह। यह fast, strongly-typed service-to-service (microservice) communication के लिए बना है।

---

## 🔴 Problem it Solves
JSON-over-HTTP (REST) APIs have overhead that becomes significant at microservice scale:
1. **JSON parsing/serialization is slow** compared to compact binary formats — every request/response pays a text-parsing tax.
2. **HTTP/1.1 limitations** — each request typically needs its own connection/round trip overhead (though HTTP/1.1 keep-alive helps somewhat); no true multiplexing of many concurrent calls over one connection.
3. **No strict contract** — REST/JSON doesn't enforce the shape of request/response bodies at the protocol level; mismatches are often only caught at runtime.

gRPC fixes all three: Protocol Buffers are a compact BINARY format (much smaller/faster than JSON), HTTP/2 provides multiplexed streams over a single connection (many concurrent calls, no per-call connection overhead), and the `.proto` contract is STRONGLY TYPED and code-generated, catching mismatches at compile time in statically-typed languages (and via generated validation in JS/TS).

## 🔴 यह क्यों बना? (Hindi)
JSON-over-HTTP (REST) APIs का overhead microservice scale पर significant हो जाता है:
1. **JSON parsing/serialization slow है** compact binary formats की तुलना में — हर request/response text-parsing tax pay करता है।
2. **HTTP/1.1 limitations** — हर request को typically अपनी connection/round trip overhead चाहिए; एक connection पर कई concurrent calls का true multiplexing नहीं।
3. **कोई strict contract नहीं** — REST/JSON protocol level पर request/response bodies का shape enforce नहीं करता; mismatches अक्सर runtime पर ही पता चलते हैं।

gRPC तीनों fix करता है: Protocol Buffers एक compact BINARY format हैं (JSON से बहुत छोटा/faster), HTTP/2 एक connection पर multiplexed streams देता है, और `.proto` contract STRONGLY TYPED और code-generated है।

---

## 🟢 How it Works — Step by Step

Step 1 → Write a `.proto` file defining a `service` (with RPC methods) and `message` types (request/response shapes).
Step 2 → Use `protoc` (the Protocol Buffers compiler) or a JS library (`@grpc/proto-loader`) to generate/load client and server stubs from the `.proto` file.
Step 3 → Implement the SERVER: write actual functions for each RPC method defined in the `.proto` service.
Step 4 → The CLIENT calls the remote method as if it were a local async function (`client.getUser({ id: 5 }, callback)`) — gRPC handles serialization, the network call over HTTP/2, and deserialization transparently.
Step 5 → gRPC supports 4 call types: unary (single request/response, like a normal function call), server streaming (one request, stream of responses), client streaming (stream of requests, one response), and bidirectional streaming (both sides stream continuously).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक `.proto` file लिखो जो एक `service` (RPC methods के साथ) और `message` types (request/response shapes) define करे।
Step 2 → `protoc` (Protocol Buffers compiler) या एक JS library (`@grpc/proto-loader`) use करके `.proto` file से client और server stubs generate/load करो।
Step 3 → SERVER implement करो: `.proto` service में define किये हर RPC method के लिए actual functions लिखो।
Step 4 → CLIENT remote method को local async function की तरह call करता है (`client.getUser({ id: 5 }, callback)`) — gRPC serialization, HTTP/2 पर network call, deserialization transparently handle करता है।
Step 5 → gRPC 4 call types support करता है: unary (single request/response), server streaming (एक request, responses की stream), client streaming (requests की stream, एक response), bidirectional streaming (दोनों तरफ से continuously stream)।

---

## 🟡 Real World Example
**Netflix, Google, and Uber's internal microservices** use gRPC extensively for service-to-service communication (not usually client-facing browser APIs, since browsers don't support raw gRPC natively without a proxy like gRPC-Web). For example, Netflix's recommendation service might call its user-profile service millions of times per second internally — at that volume, the performance difference between JSON/REST and binary/gRPC (smaller payloads, HTTP/2 multiplexing, lower CPU for serialization) translates into real infrastructure cost savings and lower latency.

## 🟡 Real Example Hindi mein
**Netflix, Google, और Uber का internal microservices** gRPC extensively use करते हैं service-to-service communication के लिए (usually client-facing browser APIs के लिए नहीं, क्योंकि browsers raw gRPC natively support नहीं करते बिना gRPC-Web जैसे proxy के)। जैसे Netflix का recommendation service अपने user-profile service को millions of times per second internally call कर सकता है — उस volume पर, JSON/REST और binary/gRPC के बीच performance difference (छोटे payloads, HTTP/2 multiplexing, कम CPU serialization के लिए) real infrastructure cost savings और lower latency में translate होता है।

---

## 💻 Code Example — Basic

```protobuf
// user.proto -- defines the service contract shared between client and server
syntax = "proto3";

package user;

service UserService {
  rpc GetUser (GetUserRequest) returns (UserResponse);  // a single "unary" RPC method
}

message GetUserRequest {
  string id = 1;   // field number 1 -- used in binary encoding, must be stable once in use
}

message UserResponse {
  string id = 1;
  string name = 2;
  string email = 3;
}
```

```javascript
// basic-grpc-server.js
// Install: npm install @grpc/grpc-js @grpc/proto-loader

const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

// Load the .proto definition at runtime (dynamic loading, no separate compile step needed)
const packageDef = protoLoader.loadSync('user.proto', {});
const userProto = grpc.loadPackageDefinition(packageDef).user;

const users = { '1': { id: '1', name: 'Rahul', email: 'rahul@x.com' } };

// Implement the RPC method defined in the .proto file
function getUser(call, callback) {
  const user = users[call.request.id]; // call.request matches GetUserRequest shape
  if (!user) {
    return callback({ code: grpc.status.NOT_FOUND, message: 'User not found' }); // gRPC status codes, not HTTP codes
  }
  callback(null, user); // first arg: error (null = success), second arg: response matching UserResponse
}

const server = new grpc.Server();
server.addService(userProto.UserService.service, { GetUser: getUser });
server.bindAsync('0.0.0.0:50051', grpc.ServerCredentials.createInsecure(), () => {
  console.log('gRPC server running on :50051');
});
```

```javascript
// basic-grpc-client.js
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

const packageDef = protoLoader.loadSync('user.proto', {});
const userProto = grpc.loadPackageDefinition(packageDef).user;

const client = new userProto.UserService('localhost:50051', grpc.credentials.createInsecure());

// Calling the remote method feels like calling a local function with a callback
client.GetUser({ id: '1' }, (err, response) => {
  if (err) return console.error('Error:', err.message);
  console.log('User:', response); // { id: '1', name: 'Rahul', email: 'rahul@x.com' }
});
```

## 💻 Code Example — Advanced

```protobuf
// orders.proto -- demonstrates server streaming
syntax = "proto3";
package orders;

service OrderService {
  rpc GetOrder (OrderRequest) returns (Order);
  rpc StreamOrderUpdates (OrderRequest) returns (stream OrderStatusUpdate); // SERVER STREAMING
}

message OrderRequest { string orderId = 1; }
message Order { string id = 1; double total = 2; }
message OrderStatusUpdate { string status = 1; string timestamp = 2; }
```

```javascript
// advanced-grpc-streaming.js — server streaming example (one request, stream of responses)

const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

const packageDef = protoLoader.loadSync('orders.proto', {});
const ordersProto = grpc.loadPackageDefinition(packageDef).orders;

const statuses = ['PLACED', 'CONFIRMED', 'SHIPPED', 'DELIVERED'];

// Server-streaming RPC: write multiple messages over time, then end the stream
function streamOrderUpdates(call) {
  let i = 0;
  const interval = setInterval(() => {
    if (i >= statuses.length) {
      clearInterval(interval);
      return call.end(); // signal no more messages coming
    }
    call.write({ status: statuses[i], timestamp: new Date().toISOString() }); // push one update
    i++;
  }, 1000);

  // Handle client disconnecting early -- always clean up resources
  call.on('cancelled', () => clearInterval(interval));
}

function getOrder(call, callback) {
  callback(null, { id: call.request.orderId, total: 1500 });
}

const server = new grpc.Server();
server.addService(ordersProto.OrderService.service, {
  GetOrder: getOrder,
  StreamOrderUpdates: streamOrderUpdates,
});
server.bindAsync('0.0.0.0:50052', grpc.ServerCredentials.createInsecure(), () => {
  console.log('Order gRPC server on :50052');
});

// Client side consumes the stream with an event emitter pattern:
// const call = client.StreamOrderUpdates({ orderId: '5' });
// call.on('data', (update) => console.log('Update:', update));
// call.on('end', () => console.log('Stream ended'));
```

---

## 🟠 Express.js Integration

```javascript
// gRPC is typically used for INTERNAL service-to-service calls, while Express/REST
// stays as the public-facing HTTP API that the browser/mobile app talks to.
// A common pattern: Express route calls a gRPC backend service internally.

const express = require('express');
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

const packageDef = protoLoader.loadSync('user.proto', {});
const userProto = grpc.loadPackageDefinition(packageDef).user;
const grpcClient = new userProto.UserService('user-service:50051', grpc.credentials.createInsecure());

const app = express();

// Public REST endpoint internally calls the gRPC microservice
app.get('/api/users/:id', (req, res) => {
  grpcClient.GetUser({ id: req.params.id }, (err, user) => {
    if (err) return res.status(err.code === grpc.status.NOT_FOUND ? 404 : 500).json({ error: err.message });
    res.json({ success: true, data: user }); // translate gRPC response into the REST API's JSON shape
  });
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Exposing gRPC directly to browsers expecting it to work like a normal fetch() call
✅ Correct: Browsers can't speak raw gRPC (no native HTTP/2 trailers support in fetch/XHR) — use **gRPC-Web** with an Envoy proxy, or keep gRPC internal and expose REST/GraphQL to browsers.

```javascript
// Wrong -- trying to call a raw gRPC server directly from browser JS
fetch('grpc://my-service:50051/GetUser'); // not how browsers work with gRPC

// Right -- browser talks to a REST/GraphQL gateway, which internally calls gRPC services
fetch('/api/users/5'); // gateway translates to gRPC internally
```

❌ Mistake 2: Changing field numbers in a `.proto` message after it's already deployed/in use
✅ Correct: Field numbers are part of the BINARY wire format — changing/reusing them breaks compatibility with already-deployed clients/servers reading old data with new field numbers (or vice versa).

```protobuf
// Wrong -- renumbering an existing field breaks binary compatibility with deployed services
message User { string id = 2; string name = 1; } // id was 1, now 2 -- breaks old clients!

// Right -- keep existing field numbers stable; only ADD new fields with new numbers
message User { string id = 1; string name = 2; string phone = 3; } // phone added safely
```

---

## 🧠 Tricky Interview Question

```javascript
// Why can't a web browser directly call a gRPC server the same way it calls a REST API with fetch()?
```
Answer: gRPC relies on **HTTP/2 trailers** (special metadata sent AFTER the response body, used to communicate the final call status) and raw binary framing that browser `fetch`/`XMLHttpRequest` APIs don't expose or fully support. Browsers' HTTP implementations are designed around REST/HTTP semantics, not gRPC's specific HTTP/2 usage pattern. The workaround is **gRPC-Web**, a browser-compatible protocol variant that gets translated to real gRPC by a proxy (commonly Envoy) sitting between the browser and the actual gRPC backend — the browser never talks "true" gRPC directly.

---

## ⚫ Interview Questions + Answers

Q1: Why is gRPC generally faster than REST/JSON for service-to-service calls?
A1: Protocol Buffers are a compact BINARY serialization format — smaller payload size and much faster parse/serialize than text-based JSON. HTTP/2 (which gRPC uses) supports multiplexing many concurrent calls over a SINGLE TCP connection (avoiding per-call connection setup overhead that can affect HTTP/1.1), and header compression (HPACK) reduces repeated metadata overhead across calls.

Q2: What are the four types of gRPC calls?
A2: **Unary** — single request, single response (like a normal function call). **Server streaming** — single request, server sends back a STREAM of responses over time (e.g., live order status updates). **Client streaming** — client sends a STREAM of requests, server responds once (e.g., uploading chunks of a large file, getting one final confirmation). **Bidirectional streaming** — both sides stream continuously and independently (e.g., a real-time chat/collaboration feature).

Q3: What is a `.proto` file, and why must field numbers be stable once a message is in use?
A3: A `.proto` file defines the SCHEMA (services, RPC methods, message types with typed fields) using Protocol Buffers' IDL (Interface Definition Language). Field NUMBERS (not names) are what's actually encoded in the compact binary wire format — if you change a field's number after deployment, old binary data (encoded with the old number) will be misinterpreted by code expecting the new numbering, corrupting data silently. Field NAMES can be changed freely since they only affect generated code, not the wire format.

Q4: How does gRPC handle errors, compared to REST's HTTP status codes?
A4: gRPC has its OWN set of status codes (`OK`, `NOT_FOUND`, `INVALID_ARGUMENT`, `UNAUTHENTICATED`, `INTERNAL`, etc.) separate from HTTP status codes, communicated via the call's status/trailers rather than the HTTP response code (though under the hood, gRPC still uses HTTP/2, often returning `200 OK` at the HTTP layer regardless of the gRPC-level outcome — similar philosophically to how GraphQL separates HTTP status from its own `errors` field).

Q5: When would you choose gRPC over REST or GraphQL for a new system?
A5: Choose gRPC for internal, high-throughput, low-latency service-to-service communication within a microservices architecture, especially when you control BOTH ends (client and server) and want strict, strongly-typed contracts with code generation across multiple languages (gRPC has first-class support for many languages via the same `.proto` file). Avoid it for public-facing browser APIs (prefer REST/GraphQL, or gRPC-Web with a proxy if truly needed) due to limited native browser support.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Internal, high-performance microservice-to-microservice communication, especially polyglot systems (different languages sharing one `.proto` contract).
- Streaming use cases (server/client/bidirectional streaming) that map awkwardly onto REST.

❌ Avoid when:
- Public-facing browser-consumed APIs (without a gRPC-Web proxy layer) — REST or GraphQL are far more browser-friendly.
- Simple, low-traffic APIs where REST's simplicity/tooling/debuggability (curl, Postman, readable JSON) outweighs gRPC's performance benefits.

---

## 📊 Visual Diagram
```
gRPC ARCHITECTURE:
──────────────────────────────────────────────────
.proto file (shared contract)
   │
   ├──▶ generates/loads SERVER stub ──▶ implement RPC methods
   │
   └──▶ generates/loads CLIENT stub ──▶ call methods like local functions

Client ───HTTP/2, Protocol Buffers (binary)───▶ Server
         (multiplexed, compact, strongly-typed)

Call types:
  Unary:              1 request  ──▶ 1 response
  Server streaming:   1 request  ──▶ N responses (stream)
  Client streaming:   N requests ──▶ 1 response
  Bidirectional:       N requests ◀─▶ N responses (both streaming)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| .proto file | Service/message schema definition | Service/message schema definition |
| Protocol Buffers | Binary serialization format | Binary serialization format |
| Unary call | Single request/response RPC | Single request/response RPC |
| Streaming RPC | Multiple messages over time | समय के साथ कई messages |
| gRPC-Web | Browser-compatible gRPC variant | Browser-compatible gRPC variant |
| Field number | Binary wire-format field identifier | Binary wire-format field identifier |

---

## ⚡ 3-Line Summary
English:
1. gRPC uses Protocol Buffers (binary) and HTTP/2 to make fast, strongly-typed RPC calls, ideal for internal microservice communication.
2. It supports 4 call types (unary, server/client/bidirectional streaming), handling real-time and bulk data patterns natively.
3. It's not natively browser-friendly (needs gRPC-Web + a proxy); keep it internal and expose REST/GraphQL for public-facing APIs.

Hindi:
1. gRPC Protocol Buffers (binary) और HTTP/2 use करके fast, strongly-typed RPC calls बनाता है, internal microservice communication के लिए ideal।
2. यह 4 call types support करता है (unary, server/client/bidirectional streaming), real-time और bulk data patterns natively handle करता है।
3. यह natively browser-friendly नहीं है (gRPC-Web + proxy चाहिए); इसे internal रखो और public-facing APIs के लिए REST/GraphQL expose करो।

---

## ➡️ Next Topic
**188. Protocol Buffers** — gRPC के पीछे का binary serialization format गहराई से समझना।
