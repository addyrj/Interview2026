# 21. Load Balancing Basics
# हिंदी में: Load Balancer — आने वाले ट्रैफ़िक को कई सर्वरों में बराबर बाँटने वाला "ट्रैफ़िक पुलिस"

---

## 🔵 Simple Definition (English)
A **load balancer (LB)** sits in front of a group of servers and **distributes incoming requests** across them, so no single server is overloaded. It also runs **health checks** and stops sending traffic to unhealthy servers.

## 🔵 सरल परिभाषा (Hindi)
Load Balancer कई सर्वरों के आगे खड़ा होकर आने वाली requests को उनमें बाँटता है, ताकि कोई एक सर्वर ओवरलोड न हो।
अगर कोई सर्वर बीमार (unhealthy) हो जाए, तो उसे ट्रैफ़िक भेजना बंद कर देता है।

---

## 🔴 Problem it Solves
Horizontal scaling (Topic 16) gives you N servers, but:
- Clients need **one address** (`api.myapp.com`), not N IPs.
- Traffic must be **spread evenly**, or one server melts while others idle.
- If a server **crashes**, users shouldn't hit it.
- You want to **deploy** by taking servers out one at a time (zero downtime).

The load balancer provides: **one entry point + even distribution + automatic failover + safe deploys.**

## 🔴 यह क्यों बना? (Hindi)
कई सर्वर हों तो यूज़र को एक ही पता चाहिए, ट्रैफ़िक बराबर बँटना चाहिए, और कोई सर्वर गिरे तो यूज़र उस पर न जाए।
Load Balancer एक entry point, बराबर बँटवारा, अपने आप failover और बिना downtime के deploy — ये सब देता है।

---

## 🟢 How it Works — Step by Step

```
                     users
                       │
              ┌────────▼────────┐
              │  Load Balancer  │  ← one DNS name / IP
              │  - algorithm    │
              │  - health checks│
              └──┬─────┬─────┬──┘
                 │     │     │
            ┌────▼┐ ┌──▼──┐ ┌▼────┐
            │ S1  │ │ S2  │ │ S3 ✗│  ← health check failed → removed from rotation
            └─────┘ └─────┘ └─────┘

Step 1 → Request arrives at the LB
Step 2 → LB picks a healthy target using an algorithm (round robin, least connections... Topic 22)
Step 3 → LB forwards the request (L4: TCP packets; L7: HTTP request)
Step 4 → Response returns through the LB (or directly, in DSR mode)
Step 5 → In background: health check every N seconds; failing targets removed, recovered ones re-added
```

### L4 vs L7 load balancing (most asked)

```
┌───────────────────────┬──────────────────────────────┬──────────────────────────────┐
│                       │ Layer 4 (Transport)          │ Layer 7 (Application)        │
├───────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Looks at              │ IP + port (TCP/UDP)          │ HTTP: URL, headers, cookies, │
│                       │                              │ method, host                 │
│ Routing decisions     │ Only by IP/port              │ /api → svc A, /img → svc B,  │
│                       │                              │ header-based, canary %       │
│ TLS                   │ Pass-through (usually)       │ Terminates TLS               │
│ Speed                 │ Very fast, millions conn/s   │ Slower (parses HTTP)         │
│ Features              │ Simple                       │ Sticky cookies, rewrites,    │
│                       │                              │ WAF, auth, compression       │
│ Protocols             │ Any TCP/UDP (DB, MQTT, games)│ HTTP/1.1, HTTP/2, gRPC, WS   │
│ AWS                   │ NLB                          │ ALB                          │
│ Others                │ HAProxy (tcp mode), LVS      │ Nginx, HAProxy (http), Envoy │
└───────────────────────┴──────────────────────────────┴──────────────────────────────┘
```

### Health checks

```
Active:   LB calls GET /health/ready every 10s
          healthy threshold: 2 successes → in
          unhealthy threshold: 3 failures → out
Passive:  LB watches real traffic; too many 5xx / timeouts → mark down (outlier detection)

Good health endpoint: checks the app can actually serve (DB reachable), fast, no auth.
Bad: always returns 200 (useless) OR checks too many deps (one slow dep → ALL servers marked dead!)
```

### Where load balancers appear

```
DNS / GSLB        → between regions (Route 53 latency routing)
Edge / CDN        → Cloudflare, CloudFront
External LB       → internet → web/API tier (ALB)
Internal LB       → service → service (internal ALB/NLB, K8s Service, service mesh)
Client-side LB    → client picks server itself (gRPC, Netflix Ribbon)
DB proxy          → PgBouncer/ProxySQL spreading reads across replicas
```

### Other key features
```
Sticky sessions     → same user → same server (cookie). Avoid if possible (breaks even spread).
Connection draining → when removing a server, let in-flight requests finish (deregistration delay)
TLS termination     → decrypt at LB, certs in one place (ACM)
Cross-zone LB       → spread evenly across AZs
Slow start          → new server gets traffic gradually (cache warm-up, JIT)
```

### Is the LB a single point of failure?
```
Managed LBs (ALB/NLB, GCP LB) are redundant internally across AZs.
Self-hosted: run 2 LBs (active-passive with keepalived + floating VIP, or active-active with DNS).
```

## 🟢 कैसे काम करता है? (Hindi)
1. यूज़र की request Load Balancer पर आती है (एक ही DNS नाम)।
2. LB एक नियम (algorithm) से किसी healthy सर्वर को चुनता है और request आगे भेजता है।
3. हर कुछ सेकंड में LB सर्वरों का `/health` चेक करता है — फ़ेल हुआ तो rotation से बाहर।
4. L4 LB सिर्फ़ IP/port देखता है (तेज़); L7 LB URL, header, cookie देखकर smart routing करता है।
5. Deploy के समय connection draining से पुराने requests पूरे होने दिए जाते हैं, फिर सर्वर हटता है।

---

## 🟡 Real World Example

**Google's Maglev** — Google's software L4 load balancer running on commodity servers. It handles all Google traffic using consistent hashing so that connections stay on the same backend even when LBs are added or removed.

**Zomato/Swiggy on AWS** — an ALB routes `/api/orders/*` to the order service target group, `/api/search/*` to search, and `/ws` to the WebSocket gateway, all on one domain, with path-based (L7) routing.

**GitHub GLB** — GitHub built its own load balancer (GLB Director) to handle millions of connections and allow LB maintenance without dropping user Git connections.

**IRCTC / ticket booking** — load balancers plus waiting-room queues protect booking servers from Tatkal spikes.

## 🟡 Real Example Hindi में
Google का Maglev नाम का load balancer पूरी दुनिया का Google ट्रैफ़िक बाँटता है। Swiggy/Zomato AWS ALB से `/api/orders` को order service और `/api/search` को search service पर भेजते हैं — एक ही डोमेन पर।
GitHub ने अपना load balancer बनाया ताकि maintenance के समय भी यूज़र के कनेक्शन न टूटें।

---

## 🟠 My Stack Example

### Nginx as an L7 load balancer (VPS / Docker)
```nginx
upstream api {
  least_conn;
  server 10.0.1.11:3000 max_fails=3 fail_timeout=10s;   # passive health check
  server 10.0.1.12:3000 max_fails=3 fail_timeout=10s;
  server 10.0.1.13:3000 backup;                          # only if others are down
  keepalive 64;
}
server {
  listen 443 ssl;
  location /api/ { proxy_pass http://api; proxy_next_upstream error timeout http_502 http_503; }
}
# Active health checks need Nginx Plus or HAProxy; open-source Nginx uses passive checks.
```

### HAProxy (active health checks, free)
```
backend api
  balance leastconn
  option httpchk GET /health/ready
  http-check expect status 200
  server api1 10.0.1.11:3000 check inter 5s fall 3 rise 2
  server api2 10.0.1.12:3000 check inter 5s fall 3 rise 2
```

### AWS ALB with path routing (Terraform-ish)
```hcl
resource "aws_lb_target_group" "api" {
  port = 3000  protocol = "HTTP"  vpc_id = var.vpc_id  target_type = "ip"
  health_check { path = "/health/ready" interval = 10 healthy_threshold = 2 unhealthy_threshold = 3 }
  deregistration_delay = 30          # connection draining
}
resource "aws_lb_listener_rule" "orders" {
  listener_arn = aws_lb_listener.https.arn
  condition { path_pattern { values = ["/api/orders/*"] } }
  action    { type = "forward" target_group_arn = aws_lb_target_group.orders.arn }
}
```

### Kubernetes: Service = internal L4 LB, Ingress = L7
```yaml
apiVersion: v1
kind: Service
metadata: { name: api }
spec: { selector: { app: api }, ports: [{ port: 80, targetPort: 3000 }] }
---
# readinessProbe decides if a pod gets traffic
readinessProbe: { httpGet: { path: /health/ready, port: 3000 }, periodSeconds: 5, failureThreshold: 3 }
```

### App side: be LB-friendly
```js
app.get('/health/ready', async (_, res) => {
  try { await pool.query('SELECT 1'); res.sendStatus(200); } catch { res.sendStatus(503); }
});
server.keepAliveTimeout = 65_000;   // > ALB idle timeout (60s) — prevents random 502s
process.on('SIGTERM', () => {       // during scale-in/deploy
  isShuttingDown = true;            // readiness starts returning 503 → LB drains
  setTimeout(() => server.close(() => process.exit(0)), 10_000);
});
```

### Mobile/web note
Clients just call `https://api.myapp.com`. Don't hardcode server IPs in the app. Always use the LB's DNS name, so you can change servers freely.

---

## ⚫ Interview Questions + Answers

**Q1: What is a load balancer and why do we need it?**
A1: A component that distributes incoming traffic across multiple backend servers behind a single endpoint. It enables horizontal scaling, improves availability (health checks remove failed servers), allows zero-downtime deploys (draining), and can offload TLS, routing and security features.

**Q2: Explain the difference between L4 and L7 load balancers.**
A2: L4 works at the transport layer. It routes based on IP and port without inspecting content, so it's very fast, protocol-agnostic (any TCP/UDP), and usually passes TLS through. L7 understands HTTP. It can route by path, host, headers or cookies, terminate TLS, do sticky sessions, rewrites, compression and WAF, and supports canary splits, at higher CPU cost. Use L7 for web/API/gRPC routing and L4 for raw TCP/UDP, extreme throughput, or static IPs (AWS NLB).

**Q3: How do health checks work? What makes a good health check?**
A3: The LB probes each target periodically (e.g. HTTP GET `/health` every 10 s) and marks it unhealthy after N consecutive failures and healthy after M successes. Passive checks watch real traffic errors. A good readiness check is fast, unauthenticated, and verifies the instance can truly serve (critical dependencies like the DB reachable). It shouldn't check every downstream service, because one shared dependency failing would mark all instances unhealthy at once. Liveness should be separate and simpler.

**Q4: Isn't the load balancer itself a single point of failure?**
A4: It can be. Managed cloud LBs are built from many nodes across AZs, so they're redundant. Self-hosted ones should run as a pair: active-passive with a floating virtual IP (keepalived/VRRP), or active-active behind DNS or anycast. For global systems, DNS-based global load balancing spreads traffic across regional LBs.

**Q5: What is connection draining and why does it matter?**
A5: When a target is removed (deploy, scale-in, failure), the LB stops sending it new requests but lets in-flight requests and connections finish for a configured period (deregistration delay). Without it, users get errors during every deploy. The app should cooperate: on SIGTERM, fail readiness, stop accepting new work, finish current requests, then exit.

---

## 🔷 Trade-offs
✅ Advantages:
- Scale out, high availability, zero-downtime deploys.
- Central place for TLS, routing, security.
- Hides backend topology from clients.

❌ Disadvantages:
- Extra hop (small latency) and cost.
- Can become a bottleneck/SPOF if self-managed poorly.
- Sticky sessions and long-lived connections (WebSockets) make even distribution harder.
- Misconfigured health checks can take everything out at once.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Load Balancer | Distributes traffic across servers | ट्रैफ़िक बाँटने वाला |
| Target / Backend | Server receiving traffic | ट्रैफ़िक पाने वाला सर्वर |
| Health check | Periodic test of server health | सर्वर की सेहत जाँच |
| L4 LB | Routes by IP/port | IP/port से routing |
| L7 LB | Routes by HTTP content | URL/header से routing |
| Sticky session | Same user → same server | एक यूज़र, एक सर्वर |
| Connection draining | Finish in-flight requests before removal | पुराने request पूरे होने देना |
| Target group | Set of servers behind an LB rule | सर्वरों का समूह |

---

## ⚡ 3-Line Summary
**English:**
1. A load balancer gives one entry point, spreads traffic across healthy servers, and removes failed ones.
2. L4 = fast, IP/port-based; L7 = HTTP-aware routing (path, host, headers), TLS termination.
3. Use good readiness checks, connection draining, and redundant/managed LBs to avoid making the LB a SPOF.

**Hindi:**
1. Load Balancer एक entry point देता है, healthy सर्वरों में ट्रैफ़िक बाँटता है, बीमार को हटाता है।
2. L4 = तेज़, IP/port पर; L7 = URL/header देखकर smart routing।
3. अच्छा health check, connection draining और redundant LB रखो।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [ByteByteGo — Load Balancer](https://www.youtube.com/results?search_query=load+balancer+system+design+bytebytego) | L4 vs L7, health checks, visual architecture |
| 📺 YouTube | [Gaurav Sen — Load Balancing](https://www.youtube.com/results?search_query=load+balancing+gaurav+sen) | Consistent hashing, distributed load balancing |
| 📝 Article | [NGINX Load Balancing Guide](https://www.nginx.com/resources/glossary/load-balancing/) | All algorithms explained with NGINX config examples |
| 📝 Article | [AWS ALB vs NLB official guide](https://aws.amazon.com/elasticloadbalancing/features/) | When to use L4 (NLB) vs L7 (ALB) on AWS |
| 🐙 GitHub | [system-design-primer — Load Balancer](https://github.com/donnemartin/system-design-primer#load-balancer) | Diagrams + active/passive vs active/active |

---

## ➡️ Next Topic Suggestion
**22. Load Balancing Algorithms** — The LB has to "pick a server". Next: HOW it picks — round robin, weighted, least connections, IP hash, consistent hashing, power of two choices — and when to use each.
