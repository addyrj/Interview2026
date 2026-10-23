# 92. Service Discovery
# हिंदी में: Service Discovery — microservices में किसी service के चालू (healthy) instances का पता (IP:port) अपने आप ढूँढने का तरीका, क्योंकि instances लगातार बदलते रहते हैं

---

## 🔵 Simple Definition (English)
**Service discovery** is how services **find the network locations** (IP:port) of other services' **healthy instances** at runtime. Instances are created, destroyed, scaled and moved constantly (containers, autoscaling, deploys), so addresses can't be hardcoded. A **service registry** keeps the current list of instances (registered on startup, removed when unhealthy), and clients look up instances by **service name**.
Implementations: **DNS-based** (Kubernetes Services, AWS Cloud Map), **registry-based** (Consul, Eureka, etcd, ZooKeeper), and **load-balancer/mesh-based** (ALB, Envoy/Istio).

## 🔵 सरल परिभाषा (Hindi)
Microservices में instances लगातार बनते-मिटते रहते हैं, इसलिए IP हाथ से लिखना नामुमकिन है। Service discovery में एक registry होती है जो हर service के चालू instances की सूची रखती है।
Order service सिर्फ़ नाम ("payment-service") से पूछती है और उसे healthy instances का पता मिल जाता है — Kubernetes DNS, Consul, Eureka इसके उदाहरण हैं।

---

## 🔴 Problem it Solves
In the old days: `PAYMENT_URL=http://10.0.1.15:8080` in a config file.
Now:
- Payment service runs **3–50 containers**, scaling every few minutes.
- Each deploy replaces all instances with **new IPs**.
- Instances crash and get rescheduled on other hosts.
- Multiple versions run at once (canary).

Hardcoded addresses break immediately. Discovery provides **dynamic, health-aware name → instances resolution**.

## 🔴 यह क्यों बना? (Hindi)
पहले config में IP लिख देते थे। आज payment service के 3 से 50 containers हैं, हर deploy पर नए IP, crash होकर दूसरी मशीन पर — हाथ से लिखा पता तुरंत टूट जाएगा।
Service discovery नाम से healthy instances का ताज़ा पता अपने आप देता है।

---

## 🟢 How it Works — Step by Step

### Registration
```
Self-registration:   instance registers itself on startup (Eureka client, Consul agent API),
                     sends heartbeats, deregisters on shutdown
Third-party:         platform registers it (Kubernetes endpoints controller, ECS + Cloud Map,
                     Consul catalog sync) based on health checks ⭐ (no app code)
Registry entry:      service=payment, instance=10.0.3.21:8080, zone=ap-south-1a, version=1.9, healthy=true
```

### Client-side discovery

```
 Order Svc ── "where is payment?" ──► Registry (Consul/Eureka)
     │◄────────── [10.0.3.21:8080, 10.0.4.7:8080, 10.0.5.2:8080]
     │ client-side load balancing (round robin / least requests), caches list, watches changes
     └────────► 10.0.4.7:8080
✅ no extra hop, smart LB in client   ❌ discovery logic in every language/client (Netflix Ribbon)
```

### Server-side discovery

```
 Order Svc ──► http://payment.internal (LB / K8s Service / proxy) ──► picks healthy instance
                         ▲
                   Registry updates LB targets
✅ simple clients (just a name)   ❌ extra hop; LB must be highly available
Examples: AWS ALB/NLB target groups, Kubernetes Service (kube-proxy/iptables/IPVS), Nginx with Consul template
```

### DNS-based discovery (most common today)
```
Kubernetes:  payment-service.default.svc.cluster.local → ClusterIP (virtual IP) → kube-proxy → pod IPs
             headless service (clusterIP: None) → DNS returns ALL pod IPs (for client-side LB / StatefulSets)
Docker Compose: service name "payment" resolves via embedded DNS
AWS Cloud Map / ECS Service Connect: payment.local → healthy task IPs
Consul DNS: payment.service.consul
Caveats: DNS caching/TTL (stale IPs), clients that resolve once at startup and never again
```

### Service mesh discovery
```
Sidecar proxy (Envoy) next to each service gets endpoint lists from the control plane (Istio/Linkerd);
app calls http://payment:8080 → sidecar routes to a healthy endpoint with retries, mTLS, LB (Topic 94)
```

### Health integration
```
Registry only returns HEALTHY instances: health checks (HTTP /health/ready, TTL heartbeats)
Unhealthy/terminating instances removed quickly (draining)
Zone awareness: prefer same-AZ instances (lower latency, no cross-AZ data cost)
```

### Discovery for external clients
```
Mobile/web apps don't use internal discovery — they hit a stable public DNS name
(api.myapp.com → CDN/ALB/API Gateway), which routes inward.
```

## 🟢 कैसे काम करता है? (Hindi)
1. हर instance शुरू होते ही registry में दर्ज होता है (ख़ुद या platform जैसे Kubernetes करवाता है), health check पास करते रहने तक बना रहता है।
2. Client-side: Order service registry से सूची लेकर ख़ुद किसी instance को चुनती है।
3. Server-side: Order service सिर्फ़ एक नाम/LB को कॉल करती है; LB healthy instance चुनता है।
4. आजकल सबसे आम DNS-based: Kubernetes में `payment-service` नाम अपने आप सही pods तक पहुँचता है।
5. ध्यान: DNS caching से पुराने IP; registry में सिर्फ़ healthy instances; same-AZ instance को प्राथमिकता।

---

## 🟡 Real World Example

**Netflix Eureka + Ribbon** — Netflix pioneered client-side discovery on AWS. Every service registered with Eureka, and clients used Ribbon for load balancing across instances. Netflix later moved toward a service mesh with Envoy-based proxies.

**Kubernetes everywhere** — most companies (including Indian startups on EKS/GKE) rely on Kubernetes Services and CoreDNS: `http://payment-service:8080` just works as pods come and go.

**HashiCorp Consul** — used by companies running mixed VM + container fleets, with DNS and HTTP APIs, health checks, and a KV store for config.

**Airbnb SmartStack (Nerve + Synapse)** — an early sidecar-style discovery system using ZooKeeper, which was a precursor to service meshes.

## 🟡 Real Example Hindi में
Netflix ने Eureka (registry) + Ribbon (client-side LB) से discovery शुरू की, बाद में Envoy वाले service mesh की ओर गए।
आज ज़्यादातर कंपनियाँ Kubernetes Services + CoreDNS इस्तेमाल करती हैं — `http://payment-service:8080` लिखो, pods बदलते रहें, फिर भी सही जगह पहुँचोगे।

---

## 🟠 My Stack Example

### Docker Compose (built-in DNS discovery)
```yaml
services:
  order-service:
    build: ./order
    environment: { PAYMENT_URL: "http://payment-service:8000" }   # name, not IP
  payment-service:
    build: ./payment
    deploy: { replicas: 3 }      # Docker DNS round-robins across replicas
```

### Kubernetes Service
```yaml
apiVersion: v1
kind: Service
metadata: { name: payment-service }
spec:
  selector: { app: payment }               # pods with this label are endpoints
  ports: [{ port: 80, targetPort: 8000 }]
# Only pods passing readinessProbe are added to endpoints.
# Order service calls: http://payment-service (same namespace) or http://payment-service.payments.svc.cluster.local
```

### Node.js — avoid stale DNS and use keep-alive pools
```js
// Node resolves DNS per new connection via OS (getaddrinfo). With keep-alive pools,
// connections to dead pods are dropped on error and re-resolved on reconnect.
import { Agent, setGlobalDispatcher } from 'undici';
setGlobalDispatcher(new Agent({ keepAliveTimeout: 10_000, connections: 50 }));
const PAYMENT_URL = process.env.PAYMENT_URL ?? 'http://payment-service';
await fetch(`${PAYMENT_URL}/v1/charges`, { method: 'POST', body, signal: AbortSignal.timeout(3000) });
```

### Consul — register & discover (Node)
```js
import Consul from 'consul';
const consul = new Consul({ host: 'consul' });

// register on startup (self-registration) with HTTP health check
await consul.agent.service.register({
  id: `payment-${process.env.HOSTNAME}`, name: 'payment', address: process.env.POD_IP, port: 8000,
  check: { http: `http://${process.env.POD_IP}:8000/health/ready`, interval: '10s', deregistercriticalserviceafter: '1m' },
});
process.on('SIGTERM', () => consul.agent.service.deregister(`payment-${process.env.HOSTNAME}`));

// discover healthy instances (client-side) + simple round robin
const nodes = await consul.health.service({ service: 'payment', passing: true });
const target = nodes[Math.floor(Math.random() * nodes.length)].Service;
await fetch(`http://${target.Address}:${target.Port}/v1/charges`, { method: 'POST', body });
```

### AWS ECS + Cloud Map / Service Connect
```
ECS service "payment" with Service Connect namespace "prod.local"
Other services call http://payment.prod.local:8000 → Envoy-based proxy picks healthy task (zone-aware)
```

### FastAPI calling another service by name
```python
PAYMENT_URL = os.getenv("PAYMENT_URL", "http://payment-service")
async with httpx.AsyncClient(base_url=PAYMENT_URL, timeout=3) as client:
    r = await client.post("/v1/charges", json=payload)
```

---

## ⚫ Interview Questions + Answers

**Q1: What is service discovery and why is it needed in microservices?**
A1: A mechanism to dynamically find the network addresses of healthy instances of a service by name. In containerized, autoscaled environments, instances constantly appear, disappear and change IPs, so static configuration breaks. A registry tracks instances (via registration and health checks), and clients or load balancers query it to route requests to live instances.

**Q2: Client-side vs server-side discovery?**
A2: Client-side: the client queries the registry, caches the instance list and load-balances itself (Eureka + Ribbon, gRPC with xDS). There's no extra hop and LB can be smart, but every client needs discovery logic, so it's language-specific. Server-side: the client calls a stable endpoint (load balancer, Kubernetes Service, proxy), which uses the registry to pick an instance. Clients stay simple, at the cost of an extra hop and an HA requirement on the LB. Service meshes put the "server-side" proxy in a local sidecar.

**Q3: How does service discovery work in Kubernetes?**
A3: Pods matching a Service's label selector, and passing readiness probes, become its endpoints (EndpointSlices). CoreDNS resolves `service.namespace.svc.cluster.local` to the Service's ClusterIP (a virtual IP), and kube-proxy (iptables or IPVS) or an eBPF data plane load-balances connections to pod IPs. Headless Services return pod IPs directly for client-side balancing or StatefulSets.

**Q4: What problems can DNS-based discovery cause?**
A4: Caching: clients or runtimes caching DNS results longer than TTLs keep calling dead IPs (the JVM's old infinite cache was a classic problem). Long-lived keep-alive connections stick to old instances, leading to uneven load after scaling. DNS round robin isn't health-aware or load-aware, and TTL propagation delays matter. Mitigations: short TTLs, respecting TTL in clients, recycling connections, using a virtual IP or proxy, or a service mesh with active health checking.

**Q5: How do you make the service registry itself highly available?**
A5: Run it as a replicated cluster (Consul or etcd servers with Raft, typically 3 or 5 nodes across AZs, and Eureka peers). Clients cache the last known instance lists, so a registry outage doesn't immediately break traffic. Use agents on each node to reduce load on the central servers. Monitor registry health, and use the platform's managed discovery (Kubernetes control plane, AWS Cloud Map) where possible.

---

## 🔷 Trade-offs
✅ Advantages:
- Dynamic, health-aware routing; enables autoscaling, rolling deploys, self-healing.

❌ Disadvantages:
- Registry is critical infrastructure; stale caches cause misrouting.
- Client-side discovery adds library complexity; server-side adds a hop.
- Debugging "which instance did I hit?" needs good observability.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Service discovery | Finding instances by name | नाम से instances ढूँढना |
| Service registry | Database of live instances | चालू instances की सूची |
| Self-registration | Instance registers itself | ख़ुद को दर्ज करना |
| Client-side discovery | Client picks instance | client ख़ुद चुने |
| Server-side discovery | LB/proxy picks instance | LB चुने |
| ClusterIP | K8s virtual service IP | K8s का आभासी IP |
| Headless service | DNS returns pod IPs | DNS से सारे pod IP |
| Health check | Determines registry membership | सूची में रहने की शर्त |
| Zone awareness | Prefer same-AZ instances | उसी AZ को प्राथमिकता |

---

## ⚡ 3-Line Summary
**English:**
1. Service discovery maps a service name to its current healthy instances via a registry, because container IPs constantly change.
2. Client-side (Eureka/Consul + client LB) vs server-side (LB/K8s Service/mesh sidecar); DNS-based is the common default.
3. Watch DNS caching and long-lived connections; keep the registry HA; only healthy instances should be returned.

**Hindi:**
1. Service discovery = नाम से healthy instances का ताज़ा पता, क्योंकि IP बदलते रहते हैं।
2. Client-side (Consul/Eureka) बनाम server-side (LB/K8s Service); DNS सबसे आम।
3. DNS caching और लंबे connections का ध्यान; registry HA हो; सिर्फ़ healthy instances लौटें।

---

## ➡️ Next Topic Suggestion
**93. API Gateway** — Internally, services find each other via discovery. Externally, mobile and web clients need one front door. Next: the API gateway, with routing, auth, rate limiting, aggregation and transformations.
