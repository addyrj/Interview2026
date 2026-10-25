# 232. Service Communication (REST/gRPC)
# हिंदी में: Service Communication (REST/gRPC)

---

## 🔵 Simple Definition (English)
Service communication is how microservices talk to each other over the network. REST uses HTTP with JSON payloads — simple, human-readable, widely supported. gRPC uses HTTP/2 with Protocol Buffers (binary) — faster, strongly typed, and supports streaming, but less human-friendly and needs code generation.

## 🔵 सरल परिभाषा (Hindi)
Service communication यह है कि microservices network पर एक-दूसरे से कैसे बात करती हैं। REST HTTP के साथ JSON payloads use करता है — simple, human-readable, widely supported। gRPC HTTP/2 के साथ Protocol Buffers (binary) use करता है — faster, strongly typed, और streaming support करता है, लेकिन less human-friendly है और code generation चाहिए।

---

## 🔴 Problem it Solves
Once an app splits into microservices, they need a reliable, well-defined way to exchange data across the network. Without a chosen protocol/contract, teams end up with inconsistent ad-hoc formats, no type safety, and poor performance for high-throughput internal calls. REST solves "simple, universal interoperability" (any client/language can call it). gRPC solves "high-performance, strongly-typed, low-latency internal communication" especially important when a service is called thousands of times per second by other internal services.

## 🔴 यह क्यों बना? (Hindi)
App microservices में split होने के बाद, उन्हें network पर data exchange करने का reliable, well-defined तरीका चाहिए। बिना चुने हुए protocol/contract के, teams inconsistent ad-hoc formats, no type safety, और high-throughput internal calls के लिए poor performance में फंस जाती हैं। REST "simple, universal interoperability" solve करता है (कोई भी client/language इसे call कर सके)। gRPC "high-performance, strongly-typed, low-latency internal communication" solve करता है, खासकर जब एक service हजारों बार per second अन्य internal services से call होती है।

---

## 🟢 How it Works — Step by Step

Step 1 (REST) → Define HTTP endpoints with verbs (GET/POST/PUT/DELETE) and JSON request/response bodies.
Step 2 (REST) → Client sends an HTTP request; server parses JSON, processes, responds with JSON + status code.
Step 3 (REST) → Documentation (OpenAPI/Swagger) describes the contract; no compile-time type checking across services.

Step 1 (gRPC) → Define a `.proto` file describing service methods and message types (strongly typed schema).
Step 2 (gRPc) → Generate client/server code from the `.proto` file for each language (code generation step).
Step 3 (gRPC) → Client calls a generated method like a local function; under the hood it's serialized via Protocol Buffers and sent over HTTP/2.
Step 4 (gRPC) → Server implements the generated interface; gRPC handles serialization, streaming, and connection multiplexing.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 (REST) → HTTP endpoints verbs (GET/POST/PUT/DELETE) और JSON request/response bodies के साथ define करो।
Step 2 (REST) → Client HTTP request भेजता है; server JSON parse करता है, process करता है, JSON + status code के साथ respond करता है।
Step 3 (REST) → Documentation (OpenAPI/Swagger) contract describe करती है; services के बीच compile-time type checking नहीं होती।

Step 1 (gRPC) → एक `.proto` file define करो जो service methods और message types describe करे (strongly typed schema)।
Step 2 (gRPC) → `.proto` file से हर language के लिए client/server code generate करो।
Step 3 (gRPC) → Client generated method को local function जैसे call करता है; internally यह Protocol Buffers से serialize होकर HTTP/2 पर भेजा जाता है।
Step 4 (gRPC) → Server generated interface implement करता है; gRPC serialization, streaming, connection multiplexing handle करता है।

---

## 🟡 Real World Example
**Razorpay's internal services:** The public-facing Payment API (used by merchants/developers) is REST — because it needs to be easy to integrate for thousands of external developers using any language, with clear documentation. But internally, the Fraud Detection service might call the Risk Scoring service thousands of times per second for every transaction — here Razorpay-style systems often use gRPC internally for lower latency and strongly-typed contracts between Node/Go/Java services, since both ends are controlled internally and performance matters more than human-readability.

## 🟡 Real Example Hindi mein
**Razorpay की internal services:** Public-facing Payment API (merchants/developers के लिए) REST है — क्योंकि इसे हजारों external developers के लिए किसी भी language में easily integrate होना चाहिए, clear documentation के साथ। लेकिन internally, Fraud Detection service हर transaction के लिए Risk Scoring service को हजारों बार per second call कर सकती है — यहाँ ऐसे systems अक्सर gRPC internally use करते हैं lower latency और strongly-typed contracts के लिए Node/Go/Java services के बीच, क्योंकि दोनों ends internally controlled हैं और performance human-readability से ज्यादा matter करती है।

---

## 💻 Code Example — Basic

```javascript
// rest-service.js — simple REST microservice
// Run: node rest-service.js
const express = require('express');
const app = express();
app.use(express.json());

// Simple, human-readable JSON API — any client (curl, browser, any language) can call this
app.get('/users/:id', (req, res) => {
  res.json({ id: req.params.id, name: 'Rahul Sharma', plan: 'premium' });
});

app.listen(5001, () => console.log('REST User Service on 5001'));

// Calling it from anywhere:
// curl http://localhost:5001/users/42
// → {"id":"42","name":"Rahul Sharma","plan":"premium"}
```

## 💻 Code Example — Advanced

```javascript
// grpc-service.js — gRPC microservice using @grpc/grpc-js and @grpc/proto-loader
// Run: node grpc-service.js (requires: npm i @grpc/grpc-js @grpc/proto-loader)

// user.proto (saved as a separate file):
// syntax = "proto3";
// service UserService {
//   rpc GetUser (UserRequest) returns (UserResponse);
// }
// message UserRequest { string id = 1; }
// message UserResponse { string id = 1; string name = 2; string plan = 3; }

const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

// Load the strongly-typed contract from the .proto file
const packageDef = protoLoader.loadSync('user.proto', {});
const userProto = grpc.loadPackageDefinition(packageDef);

// Implement the service method defined in the .proto contract
function getUser(call, callback) {
  const { id } = call.request;   // strongly typed — matches .proto message shape
  const user = { id, name: 'Rahul Sharma', plan: 'premium' };
  callback(null, user);   // gRPC handles binary serialization automatically
}

const server = new grpc.Server();
server.addService(userProto.UserService.service, { getUser });

server.bindAsync('0.0.0.0:5002', grpc.ServerCredentials.createInsecure(), () => {
  console.log('gRPC User Service running on 5002');
  server.start();
});

// A gRPC CLIENT (in another service) calling this:
// const client = new userProto.UserService('localhost:5002', grpc.credentials.createInsecure());
// client.getUser({ id: '42' }, (err, response) => console.log(response));
// Calling it feels like calling a local function — gRPC handles network + serialization
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

const app = express();

// Express (REST, public-facing) acting as a bridge to an internal gRPC service.
// This is a common real-world pattern: REST at the edge, gRPC internally.
const packageDef = protoLoader.loadSync('user.proto', {});
const userProto = grpc.loadPackageDefinition(packageDef);
const grpcClient = new userProto.UserService('user-grpc-service:5002', grpc.credentials.createInsecure());

app.get('/api/users/:id', (req, res) => {
  // External client sees simple REST; internally we call gRPC for speed
  grpcClient.getUser({ id: req.params.id }, (err, grpcResponse) => {
    if (err) return res.status(502).json({ error: 'User service unavailable' });
    res.json(grpcResponse);   // translate gRPC response into a REST JSON response
  });
});

app.listen(8080, () => console.log('REST-to-gRPC gateway on 8080'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using gRPC for public-facing APIs consumed by many unknown external clients
✅ Correct: Use REST (or GraphQL) for external APIs where ease of integration matters more than raw speed

```javascript
// Wrong: forcing third-party developers to generate gRPC clients just to call your public API
// Right: expose a REST/JSON API publicly; use gRPC only for internal service-to-service calls
```

❌ Mistake 2: No timeout/deadline on inter-service calls (both REST and gRPC)
✅ Correct: Always set deadlines so a slow/dead dependency doesn't hang the caller forever

```javascript
// Wrong (gRPC) — no deadline
client.getUser({ id }, callback);

// Right (gRPC) — deadline set
const deadline = new Date(Date.now() + 2000);   // 2s deadline
client.getUser({ id }, { deadline }, callback);
```

---

## 🧠 Tricky Interview Question

```javascript
// Service A calls Service B via REST (JSON over HTTP/1.1).
// Service A then migrates the SAME call to gRPC (Protobuf over HTTP/2).
// Both services are on the same internal network, same payload size (~2KB).
// Why might gRPC still be noticeably faster even for a single small request?
```
Answer: Even for small payloads, gRPC benefits from: (1) HTTP/2 multiplexing — multiple requests share one TCP connection without head-of-line blocking, avoiding repeated TCP/TLS handshake overhead that HTTP/1.1 REST calls often incur (unless connection pooling/keep-alive is well tuned), (2) Protocol Buffers being a compact binary format that serializes/deserializes faster than JSON parsing, and (3) gRPC's generated code skipping a lot of the manual JSON (de)serialization and validation overhead REST frameworks do per request. The gains compound heavily at high request volumes, which is why gRPC shines for high-throughput internal service meshes.

---

## ⚫ Interview Questions + Answers

Q1: What are the main differences between REST and gRPC?
A1: REST: HTTP/1.1 (or 1.1-style semantics), JSON (text, human-readable), resource-oriented (URLs + verbs), no strict schema enforcement, widely supported by every client/language and tool (curl, browsers, Postman). gRPC: HTTP/2, Protocol Buffers (binary, compact), RPC-style (method calls), strict schema via `.proto` contracts (compile-time type safety), supports bidirectional streaming, generally faster and more efficient but requires code generation and is less human-debuggable (can't easily `curl` it).

Q2: When would you choose gRPC over REST for a Node.js microservice?
A2: Choose gRPC when: both the client and server are internal services you control (so code generation and tooling aren't a burden), performance/latency at high request volume matters, you need streaming (e.g., real-time data feeds between services), or you want strict, versioned contracts enforced at compile time. Avoid gRPC for public APIs meant to be consumed by arbitrary external clients/browsers, since browser support for gRPC is limited (needs gRPC-Web) and the barrier to entry for third-party developers is higher.

Q3: What is Protocol Buffers (protobuf) and why is it faster than JSON?
A3: Protobuf is a binary serialization format defined by a `.proto` schema. It's faster than JSON because: (1) it's binary, not text, so there's no string parsing/escaping overhead, (2) field names aren't repeated in every message (they're encoded as numbered tags per the schema), making payloads smaller, (3) serialization/deserialization code is generated and optimized per-language rather than using generic reflection-based JSON parsing. The trade-off is that protobuf messages aren't human-readable without the schema, unlike JSON.

Q4: How does gRPC support streaming, and why is that useful?
A4: gRPC supports four modes: unary (single request/response, like REST), server streaming (one request, stream of responses), client streaming (stream of requests, one response), and bidirectional streaming (both sides stream independently). This is useful for use cases like live price updates (server streaming), uploading large files in chunks (client streaming), or real-time chat/collaboration (bidirectional). REST over plain HTTP/1.1 can't natively do this as cleanly — you'd need WebSockets or long-polling workarounds.

Q5: What are the downsides/trade-offs of adopting gRPC in a Node.js microservices system?
A5: Downsides: (1) harder to debug manually — can't just `curl` or inspect in a browser without special tooling (grpcurl, BloomRPC), (2) requires maintaining `.proto` files and a code-generation step in the build pipeline, (3) less mature/ubiquitous browser support (needs a proxy like grpc-web or Envoy for browser clients), (4) smaller ecosystem of middleware compared to Express's vast REST middleware ecosystem, (5) team needs to learn protobuf schema design and versioning practices (backward/forward compatibility rules).

---

## 🔷 When to Use + When Not to Use
✅ Use REST when:
- Public-facing APIs consumed by many external developers/clients
- Simplicity, debuggability, and broad tooling support matter most
- Browser clients need to call the API directly

✅ Use gRPC when:
- High-throughput, low-latency internal service-to-service communication
- Strict typed contracts and streaming are needed
- All services are under your control (so code-gen tooling is manageable)

---

## 📊 Visual Diagram
```
REST (external-facing):
  Browser/External Client ──HTTP/JSON──▶  Service A
  (easy to debug, universal, slightly heavier payloads)

gRPC (internal, high-throughput):
  Service A ──HTTP/2 + Protobuf (binary, multiplexed)──▶ Service B
  (fast, strongly typed, needs .proto + codegen, streaming supported)

Common pattern:
  External Client ──REST──▶ API Gateway ──gRPC──▶ Internal Services
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| REST | HTTP+JSON resource-oriented API style | HTTP+JSON resource-oriented API style |
| gRPC | RPC framework over HTTP/2 + Protobuf | HTTP/2 + Protobuf पर RPC framework |
| Protocol Buffers | Binary serialization format | Binary serialization format |
| .proto file | Schema contract for gRPC services | gRPC services का schema contract |
| Streaming | Continuous flow of messages, not single request/response | Messages का continuous flow |
| Deadline | Max time a gRPC call will wait | gRPC call के wait करने का max time |

---

## ⚡ 3-Line Summary
**English:**
1. REST uses HTTP+JSON — simple, universal, best for public/external APIs.
2. gRPC uses HTTP/2+Protobuf — faster, strongly typed, best for internal high-throughput service communication.
3. A common real-world pattern is REST at the edge (API Gateway) and gRPC internally between services.

**Hindi:**
1. REST HTTP+JSON use करता है — simple, universal, public/external APIs के लिए best।
2. gRPC HTTP/2+Protobuf use करता है — faster, strongly typed, internal high-throughput communication के लिए best।
3. Common pattern: edge पर (API Gateway) REST और services के बीच internally gRPC।

---

## ➡️ Next Topic
**233. Message Queues with Node** — Asynchronous communication between services using queues instead of direct calls.
