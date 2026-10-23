# 95. gRPC
# हिंदी में: gRPC — Google का तेज़ RPC framework, जिसमें services एक-दूसरे के function ऐसे बुलाती हैं जैसे local हों; डेटा Protocol Buffers (binary) में और HTTP/2 पर जाता है

---

## 🔵 Simple Definition (English)
**gRPC** is a high-performance, open-source **Remote Procedure Call** framework (by Google). You define services and messages in a **`.proto` file** (Protocol Buffers). gRPC **generates typed client and server code** in many languages. Calls travel over **HTTP/2** with compact **binary** payloads, support **streaming** (client, server, bidirectional), **deadlines**, **cancellation**, metadata, and pluggable auth and load balancing.
It's mostly used for **internal service-to-service** communication.

## 🔵 सरल परिभाषा (Hindi)
gRPC में एक `.proto` फ़ाइल में service और डेटा का ढाँचा लिखते हो, और उससे Node, Python, Go सबके लिए तैयार client/server code बन जाता है।
डेटा binary (Protobuf) में HTTP/2 पर जाता है — JSON/REST से तेज़ और छोटा; streaming और deadlines भी मिलती हैं। ज़्यादातर अंदर की services के बीच इस्तेमाल होता है।

---

## 🔴 Problem it Solves
REST + JSON between hundreds of internal services has costs:
- **JSON is verbose and slow** to serialize and parse at very high RPS (CPU + bandwidth).
- **No enforced contract:** field names and types drift between teams, so bugs are found at runtime.
- **Hand-written clients** in every language.
- HTTP/1.1 allows one request at a time per connection, and there's no native **streaming**.
- Each service handles **timeouts and cancellation** differently.

gRPC gives **strong contracts, codegen, efficient binary encoding, multiplexed HTTP/2, streaming, and built-in deadlines**.

## 🔴 यह क्यों बना? (Hindi)
सैकड़ों अंदरूनी services में REST + JSON धीमा और भारी पड़ता है, field नाम/type टीमों के बीच बिगड़ते रहते हैं, हर भाषा में client हाथ से लिखना पड़ता है, और streaming नहीं।
gRPC पक्का contract, अपने आप बना code, छोटा binary डेटा, HTTP/2, streaming और deadlines देता है।

---

## 🟢 How it Works — Step by Step

### 1. Define the contract (.proto)

```proto
syntax = "proto3";
package delivery.v1;

service DeliveryService {
  rpc GetEta (GetEtaRequest) returns (GetEtaResponse);                     // unary
  rpc TrackRider (TrackRiderRequest) returns (stream RiderLocation);        // server streaming
  rpc UploadLocations (stream RiderLocation) returns (UploadSummary);       // client streaming
  rpc Chat (stream ChatMessage) returns (stream ChatMessage);               // bidirectional
}

message GetEtaRequest     { int64 order_id = 1; double lat = 2; double lng = 3; }
message GetEtaResponse    { int32 eta_minutes = 1; string rider_name = 2; }
message RiderLocation     { int64 rider_id = 1; double lat = 2; double lng = 3; int64 ts = 4; }
message TrackRiderRequest { int64 order_id = 1; }
message UploadSummary     { int32 count = 1; }
message ChatMessage       { string from = 1; string text = 2; }
```

### 2. Generate code → implement the server → call from the client

```
protoc / buf generate → TypeScript, Python, Go, Java, Kotlin, Swift stubs
Client:  const res = await client.getEta({ orderId: 9001, lat, lng }, { deadline })
          ↓ serialize protobuf (binary, often 3–10× smaller than JSON)
          ↓ HTTP/2 POST /delivery.v1.DeliveryService/GetEta (multiplexed stream)
Server:  generated base class → your handler → returns GetEtaResponse
```

### The 4 RPC types

```
Unary            req → res                        (like a REST call)
Server streaming req → res, res, res...           (live rider location, stock ticks)
Client streaming req, req, req... → res           (upload a batch of GPS points)
Bidirectional    req ⇄ res streams                (chat, real-time collaboration)
```

### Protobuf encoding and evolution

```
Fields are identified by NUMBER, not name → compact binary (varints)
Backward/forward compatibility rules:
  ✓ add new fields with new numbers (old clients ignore them)
  ✓ never change a field's number or type; never reuse a deleted number → mark it `reserved 4;`
  ✓ proto3 fields are optional by default (defaults when missing)
Breaking change → new package version (delivery.v2)
Tooling: buf (lint + breaking-change detection in CI)
```

### Deadlines and status codes

```
Every call should set a DEADLINE; it propagates to downstream calls (Topic 79)
Status codes: OK, CANCELLED, DEADLINE_EXCEEDED, NOT_FOUND, INVALID_ARGUMENT, UNAVAILABLE (retryable),
              RESOURCE_EXHAUSTED (rate limited), PERMISSION_DENIED, UNAUTHENTICATED, INTERNAL
Metadata = headers (auth tokens, trace ids)
```

### Load balancing gotcha

```
HTTP/2 = one long-lived connection carrying many multiplexed requests →
an L4 load balancer pins ALL requests from a client to ONE backend → uneven load ❌
Fixes: an L7 LB that understands HTTP/2/gRPC (Envoy, Istio, ALB gRPC target groups, Linkerd),
       client-side LB (gRPC round_robin over a headless service, or xDS), max connection age
```

### gRPC vs REST vs GraphQL

```
┌────────────────────┬─────────────────────────┬──────────────────────┬──────────────────────┐
│                    │ gRPC                    │ REST/JSON            │ GraphQL              │
├────────────────────┼─────────────────────────┼──────────────────────┼──────────────────────┤
│ Contract           │ .proto, strict, codegen │ OpenAPI (optional)   │ Schema, strict       │
│ Payload            │ Binary protobuf (small) │ JSON text            │ JSON                 │
│ Transport          │ HTTP/2                  │ HTTP/1.1 or 2        │ HTTP                 │
│ Streaming          │ Native, bidirectional   │ No (use SSE/WS)      │ Subscriptions        │
│ Browser support    │ Needs gRPC-Web/Connect  │ Native               │ Native               │
│ Human-readable     │ No (needs tools)        │ Yes (curl)           │ Yes                  │
│ HTTP/CDN caching   │ Hard                    │ Easy                 │ Hard                 │
│ Best for           │ Internal microservices, │ Public APIs, web/    │ Client-driven data   │
│                    │ low latency, polyglot,  │ mobile, simple CRUD  │ fetching, BFF        │
│                    │ streaming               │                      │                      │
└────────────────────┴─────────────────────────┴──────────────────────┴──────────────────────┘
```

## 🟢 कैसे काम करता है? (Hindi)
1. `.proto` फ़ाइल में service (functions) और messages (डेटा) लिखो; हर field का एक नंबर होता है।
2. उससे हर भाषा का typed client और server code अपने आप बनता है।
3. Client function बुलाता है → डेटा binary (Protobuf) में HTTP/2 पर → server handler → जवाब।
4. चार तरह की calls: unary, server streaming (लाइव लोकेशन), client streaming (GPS batch), दोनों तरफ़ streaming (chat)।
5. हर कॉल पर deadline रखो; field नंबर कभी मत बदलो; HTTP/2 की वजह से L7 load balancer या client-side LB चाहिए।

---

## 🟡 Real World Example

**Google** — gRPC grew out of Stubby, Google's internal RPC system that handles billions of calls per second between services.

**Netflix, Square, Dropbox, Lyft, Uber** — use gRPC heavily between internal microservices. Uber moved many services to gRPC and Protobuf for performance and strict contracts, and Dropbox migrated its custom RPC system to gRPC (Courier).

**Kubernetes, etcd, Envoy** — etcd's API is gRPC, Envoy's control-plane API (xDS) is gRPC streaming, and the Kubernetes container runtime interface (CRI) uses gRPC.

**Indian fintech and food-delivery backends** — use gRPC for latency-sensitive internal calls such as pricing, ETA, serviceability and fraud scoring, while exposing REST or GraphQL to mobile and web clients.

## 🟡 Real Example Hindi में
gRPC Google के अंदरूनी Stubby से निकला, जो प्रति सेकंड अरबों calls संभालता है। Netflix, Uber, Dropbox अपनी अंदर की services में gRPC इस्तेमाल करते हैं; etcd और Envoy के API भी gRPC हैं।
भारतीय कंपनियाँ pricing, ETA, fraud scoring जैसी तेज़ अंदरूनी calls gRPC से करती हैं, पर mobile/web को REST या GraphQL देती हैं।

---

## 🟠 My Stack Example

### Node.js server (@grpc/grpc-js + proto-loader)
```js
import grpc from '@grpc/grpc-js';
import protoLoader from '@grpc/proto-loader';

const def = protoLoader.loadSync('delivery.proto', { keepCase: false, longs: Number, defaults: true });
const pkg = grpc.loadPackageDefinition(def).delivery.v1;

const server = new grpc.Server();
server.addService(pkg.DeliveryService.service, {
  async GetEta(call, cb) {
    try {
      const { orderId, lat, lng } = call.request;
      const eta = await computeEta(orderId, lat, lng);
      cb(null, { etaMinutes: eta.minutes, riderName: eta.riderName });
    } catch (e) {
      cb({ code: grpc.status.UNAVAILABLE, message: e.message });
    }
  },
  TrackRider(call) {                                         // server streaming
    const unsubscribe = locationBus.subscribe(call.request.orderId, (loc) => call.write(loc));
    call.on('cancelled', unsubscribe);                       // client went away → stop
  },
});
server.bindAsync('0.0.0.0:50051', grpc.ServerCredentials.createInsecure(), () => {});
// Inside a service mesh, mTLS is handled by the sidecars; otherwise use ServerCredentials.createSsl(...)
```

### Node.js client with deadline and metadata
```js
const client = new pkg.DeliveryService('delivery-service:50051', grpc.credentials.createInsecure(), {
  'grpc.service_config': JSON.stringify({ loadBalancingConfig: [{ round_robin: {} }] }),   // client-side LB
});
const md = new grpc.Metadata();
md.set('x-request-id', req.id);

client.GetEta({ orderId: 9001, lat: 19.07, lng: 72.87 }, md, { deadline: Date.now() + 500 }, (err, res) => {
  if (err?.code === grpc.status.DEADLINE_EXCEEDED) return useFallbackEta();
  console.log(res.etaMinutes);
});
```

### Python server (grpcio) — runs alongside a FastAPI service
```python
import grpc, delivery_pb2, delivery_pb2_grpc
from concurrent import futures

class Delivery(delivery_pb2_grpc.DeliveryServiceServicer):
    def GetEta(self, request, context):
        if context.time_remaining() < 0.05:                       # caller's deadline almost over
            context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, "no time left")
        return delivery_pb2.GetEtaResponse(eta_minutes=eta_for(request.order_id), rider_name="Ravi")

server = grpc.server(futures.ThreadPoolExecutor(max_workers=16))
delivery_pb2_grpc.add_DeliveryServiceServicer_to_server(Delivery(), server)
server.add_insecure_port("[::]:50051")
server.start()
server.wait_for_termination()
# Async variant: grpc.aio
```

### Codegen with buf (shared across services)
```yaml
# buf.gen.yaml
version: v2
plugins:
  - remote: buf.build/bufbuild/es              # TypeScript (protobuf-es / Connect-ES)
    out: gen/ts
  - remote: buf.build/protocolbuffers/python
    out: gen/py
# CI: `buf lint` and `buf breaking --against '.git#branch=main'` → blocks breaking changes
```

### Browser and React Native clients
```
Browsers can't speak raw gRPC → use gRPC-Web through an Envoy proxy, or the Connect protocol
(connectrpc.com), which works over HTTP/1.1 with JSON or binary.
Typical layout: Mobile/Web → REST/GraphQL BFF → gRPC → internal services.
```

### Health checks and tooling
```
grpc.health.v1.Health standard service → Kubernetes gRPC probes (livenessProbe: grpc: { port: 50051 })
grpcurl -plaintext delivery-service:50051 list      # curl for gRPC (needs server reflection)
```

---

## ⚫ Interview Questions + Answers

**Q1: What is gRPC and how does it work?**
A1: A high-performance RPC framework. You define services and messages in Protocol Buffers `.proto` files, and the toolchain generates strongly typed client stubs and server interfaces in many languages. Calls go over HTTP/2 as binary protobuf payloads with metadata (headers). It supports unary and streaming calls, deadlines and cancellation, standard status codes, interceptors (auth, logging, tracing) and pluggable load balancing.

**Q2: Why is gRPC faster than REST/JSON?**
A2: Protobuf is a compact binary format with numbered fields and varint encoding, so payloads are smaller than JSON and serialize and parse faster with less CPU. HTTP/2 multiplexes many concurrent calls over one connection with header compression, avoiding connection setup costs and request queuing at the HTTP layer. Generated code avoids reflection-heavy parsing. The gains are biggest for high-volume internal traffic with small messages.

**Q3: When would you choose gRPC over REST?**
A3: For internal service-to-service calls where performance, low latency and strict contracts matter; in polyglot environments that benefit from codegen; and when you need streaming (live updates, bidirectional, batch uploads). Prefer REST for public APIs, browser clients, cacheable resources, simple CRUD, and when human readability and universal tooling matter. A BFF often translates REST or GraphQL from clients into gRPC calls internally.

**Q4: What are common pitfalls with gRPC?**
A4: Load balancing: long-lived HTTP/2 connections defeat L4 load balancers, so you need L7 or client-side load balancing and a maximum connection age. Missing deadlines cause hung calls and cascading failures. Breaking proto changes (renumbering fields, changing types, reusing numbers) need guarding with buf's breaking-change check. Browsers need gRPC-Web or Connect. Binary payloads need grpcurl and reflection to debug. Large messages hit the default 4 MB limit, so stream them instead.

**Q5: How do you evolve a protobuf API safely?**
A5: Add new fields with new field numbers. Old clients ignore unknown fields, and new clients see defaults when a field is missing. Never change the number or type of an existing field. When removing a field, mark its number and name `reserved` so they're never reused. Avoid making fields semantically required. For incompatible changes, create a new versioned package or service (`v2`) and run both during migration. Enforce all of this with linting and breaking-change detection in CI.

---

## 🔷 Trade-offs
✅ Advantages:
- Fast and compact, typed contracts with codegen, streaming and deadlines; great for polyglot microservices.

❌ Disadvantages:
- Not browser-native; harder to debug and inspect; poor HTTP caching.
- HTTP/2 makes load balancing harder; needs discipline in managing protobuf schemas.
- Less suitable for public or partner APIs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RPC | Calling a remote function like a local one | दूर के function को local जैसा बुलाना |
| Protocol Buffers | Binary, schema-based serialization | binary डेटा format |
| .proto file | Service and message definitions | सेवा और डेटा का ढाँचा |
| Stub | Generated client code | बना हुआ client code |
| Unary / Streaming RPC | Single vs continuous messages | एक बार / लगातार messages |
| Deadline | Absolute time limit for a call | कॉल की समय-सीमा |
| Metadata | gRPC headers | gRPC के headers |
| gRPC-Web / Connect | Browser-compatible variants | ब्राउज़र वाले रूप |
| Field number | Protobuf field identifier | field की पहचान संख्या |

---

## ⚡ 3-Line Summary
**English:**
1. gRPC is contract-first RPC: .proto definitions generate typed clients and servers; protobuf binary travels over HTTP/2.
2. It supports unary and streaming calls, deadlines, metadata and status codes, and is faster and stricter than REST/JSON for internal calls.
3. Use it between services, REST/GraphQL for public and browser clients; watch L7/client-side load balancing, deadlines and safe proto evolution.

**Hindi:**
1. gRPC = .proto से contract → typed code; Protobuf binary, HTTP/2 पर।
2. Unary + streaming, deadlines, status codes; अंदरूनी calls के लिए REST से तेज़ और सख़्त।
3. Services के बीच gRPC, public/browser के लिए REST/GraphQL; L7 LB, deadline और field नंबर नियम का ध्यान।

---

## ➡️ Next Topic Suggestion
**96. WebSocket at Scale** — Streaming between services is covered. Next: streaming to millions of phones and browsers, with connection gateways, pub/sub fan-out, presence, sticky routing and reconnect storms.
