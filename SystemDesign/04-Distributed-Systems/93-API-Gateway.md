# 93. API Gateway
# हिंदी में: API Gateway — सारे clients (web, mobile, partners) के लिए एक मुख्य दरवाज़ा, जो request को सही microservice तक भेजता है और रास्ते में auth, rate limit, logging जैसे साझा काम करता है

---

## 🔵 Simple Definition (English)
An **API gateway** is a **single entry point** for client requests into a set of backend services. It **routes** each request to the right service and handles **cross-cutting concerns** centrally: authentication, authorization, rate limiting, request validation, TLS, caching, request/response transformation, aggregation, logging, metrics and tracing.
Examples: **AWS API Gateway, Kong, Apigee, Tyk, Envoy Gateway, Traefik, NGINX, Spring Cloud Gateway**, Netflix Zuul.

## 🔵 सरल परिभाषा (Hindi)
API Gateway सारे clients के लिए एक दरवाज़ा है — `api.myapp.com` पर आई request को देखकर सही service (orders, payments, users) तक भेजता है।
रास्ते में साझा काम भी करता है: login token जाँचना, rate limit, logging, caching — ताकि हर service को ये बार-बार न बनाना पड़े।

---

## 🔴 Problem it Solves
Without a gateway, in a microservices system:
- Clients must know **dozens of service URLs** (orders.myapp.com, payments.myapp.com …) and change when services split or merge.
- **Every service** re-implements auth, rate limiting, CORS, logging, TLS → inconsistent and buggy.
- Mobile screens need data from **many services** → many round trips on slow networks.
- Internal services are **exposed** to the internet.
- Hard to do **versioning, canary releases, API keys and quotas** for partners.

The gateway provides **one stable, secure facade** and centralizes edge policies.

## 🔴 यह क्यों बना? (Hindi)
बिना gateway के clients को दर्जनों service URLs याद रखने पड़ते, हर service अपना auth, rate limit, logging अलग बनाती, मोबाइल को एक स्क्रीन के लिए कई कॉल करनी पड़तीं, और अंदर की services इंटरनेट पर खुली रहतीं।
Gateway एक स्थिर, सुरक्षित दरवाज़ा देता है और ये साझा नियम एक जगह लागू करता है।

---

## 🟢 How it Works — Step by Step

```
  📱 RN App   🌐 Next.js   🤝 Partner API (API key)
        \          |          /
         ▼         ▼         ▼
 ┌───────────────────────────────────────────────────────────┐
 │                       API GATEWAY                         │
 │ 1. TLS termination                                         │
 │ 2. AuthN: verify JWT / API key / OAuth token               │
 │ 3. Rate limit / quota per user / API key / plan            │
 │ 4. Request validation, size limits, WAF rules              │
 │ 5. Route: /orders/* → order-svc, /payments/* → payment-svc │
 │ 6. Transform (headers, paths, protocol REST→gRPC)          │
 │ 7. (optional) aggregate multiple services into one response│
 │ 8. Cache GET responses, compress                           │
 │ 9. Logs, metrics, tracing (add trace id), canary routing   │
 └──────────┬──────────────┬───────────────┬─────────────────┘
            ▼              ▼               ▼
      order-svc       payment-svc       user-svc     (private network)
```

### Gateway responsibilities

```
Edge security       → TLS, WAF, IP allow/deny, bot protection, request size limits, CORS
Identity            → validate JWT/OAuth tokens (JWKS), API keys; pass user claims downstream
                      (X-User-Id header / internal token) so services don't re-verify externally
Traffic management  → routing by path/host/header, canary & blue-green weights, retries, timeouts,
                      circuit breaking, load balancing
Rate limiting       → per user/key/plan; quotas (10k calls/day for free tier)
Transformation      → path rewrite (/api/v2/orders → order-svc /orders), header injection,
                      protocol translation (REST ↔ gRPC), response shaping
Aggregation         → compose several service calls (better done in a BFF, Topic 93a)
Observability       → access logs, metrics per route, distributed tracing
Monetization/DevEx  → API keys, developer portal, usage analytics, plans (Apigee, Kong, AWS usage plans)
```

### Gateway vs Load Balancer vs Reverse Proxy vs Service Mesh

```
Reverse proxy  → generic forwarding (Nginx) — can be configured as a simple gateway
Load balancer  → spread traffic across instances of ONE service (L4/L7)
API gateway    → edge entry point for MANY services + API concerns (auth, keys, quotas, transforms)
Service mesh   → east-west (service-to-service) traffic inside the cluster: mTLS, retries, LB (Topic 94)
North-south traffic (client → system) = gateway; east-west (service → service) = mesh.
```

### Pitfalls
```
✗ Putting BUSINESS LOGIC in the gateway → becomes a monolith bottleneck owned by one team
✗ Single gateway for ALL clients with client-specific hacks → use BFFs per client type
✗ Gateway as SPOF → run multiple instances across AZs (managed gateways do this)
✗ Extra latency hop → keep plugins light; avoid synchronous calls to auth service per request (verify JWT locally)
✗ Trusting headers from clients (X-User-Id) → gateway must STRIP incoming identity headers and set its own
```

### Managed vs self-hosted
```
AWS API Gateway (REST/HTTP/WebSocket APIs): Lambda/HTTP integrations, JWT authorizers, usage plans,
  throttling, caching — pay per request; 29s integration timeout (REST), payload limits
Kong / Tyk / KrakenD / Envoy Gateway / Traefik: self-hosted, plugins, run on K8s
Apigee / Azure APIM: enterprise API management & monetization
```

## 🟢 कैसे काम करता है? (Hindi)
1. हर client (web, mobile, partner) एक ही पते `api.myapp.com` पर आता है।
2. Gateway TLS खोलता है, JWT/API key जाँचता है, rate limit और validation लगाता है।
3. Path/host देखकर सही service पर भेजता है (`/orders` → order-svc); ज़रूरत हो तो path/headers बदलता है।
4. यूज़र की पहचान (X-User-Id) अंदर भेजता है ताकि services दोबारा न जाँचें — client से आए ऐसे headers पहले हटा देता है।
5. Gateway में business logic मत डालो; हर client के लिए अलग ज़रूरत हो तो BFF बनाओ; कई instances चलाओ ताकि SPOF न बने।

---

## 🟡 Real World Example

**Netflix Zuul** — Netflix's edge gateway handles all device traffic (TVs, phones, browsers): routing, authentication, canary testing, load shedding and regional failover. It's one of the best-known gateways.

**Amazon API Gateway + Lambda** — the standard serverless architecture used by thousands of startups: the gateway handles auth (Cognito/JWT authorizers), throttling and routing to Lambda functions.

**Razorpay / Stripe-style public APIs** — gateways manage API keys, per-merchant rate limits, request logging, versioning headers and quotas for millions of merchants.

**Swiggy / Zomato** — mobile apps talk to edge gateways or BFFs that authenticate users, rate-limit, and route to hundreds of internal microservices hidden behind them.

## 🟡 Real Example Hindi में
Netflix का Zuul हर device (TV, फ़ोन, ब्राउज़र) की request संभालता है — routing, auth, canary, load shedding।
AWS API Gateway + Lambda हज़ारों startups का serverless ढाँचा है। Razorpay जैसे public APIs में gateway हर merchant की API key, rate limit और logging संभालता है।

---

## 🟠 My Stack Example

### Kong (declarative config, DB-less) in Docker/K8s
```yaml
_format_version: "3.0"
services:
  - name: order-svc
    url: http://order-service:3000
    routes: [{ name: orders, paths: ["/api/v1/orders"], strip_path: false }]
    plugins:
      - name: jwt                      # verify tokens (or openid-connect plugin)
      - name: rate-limiting
        config: { minute: 100, policy: redis, redis_host: redis }
  - name: payment-svc
    url: http://payment-service:8000
    routes: [{ name: payments, paths: ["/api/v1/payments"] }]
    plugins:
      - name: rate-limiting
        config: { minute: 20, policy: redis, redis_host: redis }
plugins:
  - name: cors
    config: { origins: ["https://myapp.com"], credentials: true }
  - name: correlation-id
    config: { header_name: X-Request-ID, generator: uuid }
  - name: prometheus
```

### Minimal Node.js gateway (Express + http-proxy-middleware) — for small teams
```js
import { createProxyMiddleware } from 'http-proxy-middleware';

app.use(helmet(), express.json({ limit: '1mb' }));
app.use((req, _res, next) => { delete req.headers['x-user-id']; delete req.headers['x-user-role']; next(); }); // never trust client
app.use('/api', authenticate);                                  // verify JWT locally via JWKS (Topic 54)
app.use('/api', limit(apiLimiter, (req) => req.user.id));       // Topic 59

const proxy = (target) => createProxyMiddleware({
  target, changeOrigin: true, proxyTimeout: 10_000, timeout: 10_000,
  on: { proxyReq: (proxyReq, req) => {
    proxyReq.setHeader('X-User-Id', req.user.id);
    proxyReq.setHeader('X-User-Role', req.user.role);
    proxyReq.setHeader('X-Request-ID', req.id);
  } },
});
app.use('/api/v1/orders', proxy('http://order-service:3000'));
app.use('/api/v1/payments', proxy('http://payment-service:8000'));
app.use('/api/v1/users', proxy('http://user-service:3000'));
```

### AWS API Gateway (HTTP API) with JWT authorizer (Terraform-ish)
```hcl
resource "aws_apigatewayv2_authorizer" "jwt" {
  api_id = aws_apigatewayv2_api.main.id  authorizer_type = "JWT"  identity_sources = ["$request.header.Authorization"]
  jwt_configuration { issuer = "https://auth.myapp.com"  audience = ["myapp-api"] }
}
resource "aws_apigatewayv2_route" "orders" {
  api_id = aws_apigatewayv2_api.main.id  route_key = "ANY /api/v1/orders/{proxy+}"
  target = "integrations/${aws_apigatewayv2_integration.orders_alb.id}"
  authorization_type = "JWT"  authorizer_id = aws_apigatewayv2_authorizer.jwt.id
}
# Stage-level throttling: rate 1000 rps, burst 2000 (token bucket — Topic 60)
```

### Downstream services trust the gateway (FastAPI)
```python
# service sits in private network; only accepts traffic from gateway (security group / mTLS)
async def current_user(x_user_id: str = Header(...), x_user_role: str = Header("user")):
    return {"id": x_user_id, "role": x_user_role}
```
(Defense in depth: services can still verify a signed internal JWT forwarded by the gateway.)

---

## ⚫ Interview Questions + Answers

**Q1: What is an API gateway and what does it do?**
A1: A single entry point for external clients to a microservices backend. It routes requests to the appropriate services and centralizes cross-cutting edge concerns: TLS termination, authentication (JWT, OAuth, API keys), rate limiting and quotas, request validation and size limits, CORS, caching, request and response transformation, protocol translation, canary routing, logging, metrics and tracing. It hides internal service topology from clients.

**Q2: API gateway vs load balancer vs service mesh?**
A2: A load balancer distributes traffic across instances of a service (L4/L7). An API gateway sits at the edge for north-south traffic, routing to many services and adding API-level policies (auth, keys, quotas, transformations). A service mesh handles east-west service-to-service traffic inside the cluster, with sidecar or ambient proxies providing mTLS, retries, timeouts, load balancing and telemetry. Many architectures use all three.

**Q3: What should NOT go into an API gateway?**
A3: Business logic and domain rules (pricing, order validation), heavy data aggregation tied to specific UIs (put that in a BFF), and anything that makes the gateway a coordination bottleneck owned by one team. Also avoid per-request synchronous calls to external auth services (verify tokens locally with JWKS) and complex stateful logic. Keep it thin, declarative and highly available.

**Q4: How does authentication work with a gateway in front of microservices?**
A4: The gateway validates the client's credential (JWT signature and claims via JWKS, an OAuth introspection result, or an API key lookup with caching), rejects invalid requests, and forwards identity to services, either as trusted headers after stripping any client-supplied versions, or as a short-lived internal signed token. Services still enforce authorization (resource ownership and RBAC) and only accept traffic from the gateway (network policies, mTLS).

**Q5: Isn't the API gateway a single point of failure and bottleneck?**
A5: It can be, so run multiple gateway instances across AZs behind a load balancer (managed gateways do this), autoscale them, keep plugins lightweight, avoid blocking calls, and set timeouts and circuit breakers to backends. For large organizations, use multiple gateways or BFFs per client domain to avoid one giant shared choke point and team bottleneck.

---

## 🔷 Trade-offs
✅ Advantages:
- Single stable entry point; centralized security & policies; hides internal topology.
- Easier versioning, canary, monetization; consistent observability.

❌ Disadvantages:
- Extra network hop & latency; another critical component (HA needed).
- Risk of becoming a bloated "god" layer with business logic.
- Configuration sprawl; vendor lock-in with managed gateways (timeouts, payload limits).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| API Gateway | Single entry point for APIs | APIs का मुख्य दरवाज़ा |
| Cross-cutting concern | Shared behaviour (auth, logs) | सबके साझा काम |
| North-south traffic | Client ↔ system | बाहर से अंदर का ट्रैफ़िक |
| East-west traffic | Service ↔ service | services के बीच का ट्रैफ़िक |
| Routing | Choosing backend by path/host | सही service चुनना |
| Authorizer | Gateway auth check | gateway की auth जाँच |
| Usage plan / quota | Limits per API key | API key की सीमा |
| Request transformation | Modify request/response | request बदलना |
| Developer portal | Docs & keys for API consumers | API उपयोगकर्ताओं का पोर्टल |

---

## ⚡ 3-Line Summary
**English:**
1. An API gateway is the single front door: routes requests to services and centralizes TLS, auth, rate limits, validation, transforms, observability.
2. It handles north-south traffic; service meshes handle east-west; load balancers spread instances.
3. Keep it thin (no business logic), highly available, strip untrusted identity headers, and use BFFs for client-specific aggregation.

**Hindi:**
1. API Gateway = एक मुख्य दरवाज़ा: routing + TLS, auth, rate limit, validation, logging एक जगह।
2. बाहर से अंदर का ट्रैफ़िक gateway, services के बीच mesh, instances में बाँटना LB।
3. हल्का रखो (business logic नहीं), कई instances, client के headers पर भरोसा नहीं, client-विशेष काम के लिए BFF।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [ByteByteGo — API Gateway](https://www.youtube.com/results?search_query=api+gateway+system+design+bytebytego) | Rate limiting, auth, routing — visual explanation |
| 📺 YouTube | [Hussein Nasser — API Gateway vs Load Balancer](https://www.youtube.com/results?search_query=api+gateway+vs+load+balancer+hussein+nasser) | Why these are different and when to use each |
| 📝 Article | [Kong API Gateway Docs](https://docs.konghq.com/gateway/latest/) | Most popular open-source gateway — see plugin system |
| 📝 Article | [AWS API Gateway Developer Guide](https://docs.aws.amazon.com/apigateway/latest/developerguide/) | REST vs HTTP vs WebSocket APIs on AWS |
| 🐙 GitHub | [system-design-primer — API Gateway](https://github.com/donnemartin/system-design-primer#api-gateway) | API gateway vs reverse proxy, microservices entry point |

---

## ➡️ Next Topic Suggestion
**93a. BFF — Backend For Frontend** — One generic gateway can't give the web, iOS and Android apps exactly what each screen needs. Next: the BFF pattern, a dedicated backend per client experience that aggregates and shapes data.
