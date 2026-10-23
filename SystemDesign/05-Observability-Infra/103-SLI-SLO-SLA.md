# 103. SLI / SLO / SLA
# हिंदी में: SLI — सेवा कितनी अच्छी है उसे नापने का पैमाना; SLO — उस पैमाने का अंदरूनी लक्ष्य (जैसे 99.9%); SLA — ग्राहक से किया गया लिखित वादा, टूटने पर जुर्माना

---

## 🔵 Simple Definition (English)
- **SLI (Service Level Indicator):** a **measurement** of service quality from the user's perspective, usually a ratio of good events to total events. Example: "% of checkout requests that succeed in under 500 ms".
- **SLO (Service Level Objective):** the **target** for an SLI over a time window. Example: "99.9% of checkout requests succeed under 500 ms, measured over 30 days". It's an internal engineering goal.
- **SLA (Service Level Agreement):** a **contractual promise** to customers, with **consequences** (refunds or credits) if breached. Example: "99.9% monthly uptime or 10% service credit". SLAs should be **looser** than SLOs.

## 🔵 सरल परिभाषा (Hindi)
SLI = नाप (जैसे कितने % requests 500 ms में सफल हुईं)। SLO = उस नाप का लक्ष्य (30 दिन में 99.9%) — टीम का अंदरूनी लक्ष्य।
SLA = ग्राहक से लिखित वादा, टूटा तो पैसे/क्रेडिट लौटाने पड़ते हैं; इसलिए SLA हमेशा SLO से थोड़ा ढीला रखते हैं।

---

## 🔴 Problem it Solves
Without explicit reliability targets:
- "Is the system reliable enough?" becomes an **opinion fight** between product (ship features) and ops (stop changes).
- Teams chase **100%**, which is impossible and infinitely expensive, or ignore reliability until customers churn.
- Alerts fire on **infrastructure noise** (CPU 80%) instead of **user pain**.
- No objective way to decide "should we freeze deploys and fix reliability, or keep shipping?"

SLIs/SLOs give a **shared, measurable, user-centric definition of "good enough"**, plus **error budgets** (next topic) to balance speed vs stability.

## 🔴 यह क्यों बना? (Hindi)
बिना तय लक्ष्य के "सिस्टम काफ़ी भरोसेमंद है?" एक बहस बन जाता है — product कहे features भेजो, ops कहे बदलाव रोको। लोग 100% के पीछे भागते हैं (नामुमकिन और बहुत महँगा), या reliability को नज़रअंदाज़ करते हैं।
SLI/SLO यूज़र के नज़रिए से "काफ़ी अच्छा" का साफ़, नापने लायक मतलब देते हैं।

---

## 🟢 How it Works — Step by Step

### The hierarchy

```
SLI  (what we measure)     → successful_checkouts_under_500ms / all_checkouts
SLO  (what we aim for)     → ≥ 99.9% over rolling 30 days
SLA  (what we promise)     → ≥ 99.5% monthly, else 10% credit      ← looser than SLO = safety margin
Error budget               → 100% − SLO = 0.1% of requests may fail (Topic 104)
```

### Good SLIs are user-centric ratios

```
┌────────────────┬─────────────────────────────────────────────────────────────────┐
│ SLI type       │ Example (good events / valid events)                            │
├────────────────┼─────────────────────────────────────────────────────────────────┤
│ Availability   │ non-5xx responses / all requests (exclude 4xx client errors)    │
│ Latency        │ requests faster than 300 ms / all requests (p-threshold style)  │
│ Quality        │ responses served without degradation / all (e.g. with recs)     │
│ Freshness      │ search index updated within 5 min / all updates                 │
│ Correctness    │ payments reconciled correctly / all payments                    │
│ Throughput     │ batch jobs completed within window / all jobs                   │
│ Durability     │ objects retrievable / objects stored                            │
└────────────────┴─────────────────────────────────────────────────────────────────┘
Measure as close to the USER as possible: load balancer logs > app metrics; RUM / synthetic
probes for client-side experience.
```

### Choosing SLO targets

```
- Based on what users need and what the business can afford, NOT "as high as possible"
- Different journeys → different SLOs:
    Checkout/payment:  99.95% availability, 95% < 800 ms
    Browse menu:       99.9%, 95% < 300 ms
    Recommendations:   99.0% (degrades gracefully)
    Analytics export:  99% complete within 1 hour
- Start from current performance (measure 4 weeks), set slightly better, iterate
- Remember: your SLO can't exceed the product of your hard dependencies' availability
- Window: rolling 28/30 days is common
```

### Nines → allowed bad minutes (30-day window, for time-based SLOs)

```
99%     → 7.2 hours
99.5%   → 3.6 hours
99.9%   → 43.2 minutes
99.95%  → 21.6 minutes
99.99%  → 4.3 minutes
(request-based SLOs count bad requests instead of minutes)
```

### SLA specifics
```
- Legal/business document: scope, measurement method, exclusions (planned maintenance,
  customer misuse, force majeure), claim process, credits (10–25% of monthly fee)
- Examples: AWS EC2 99.99% region-level, S3 99.9%, many SaaS 99.9%
- Internal teams use SLOs; external customers get SLAs; some services have SLOs but NO SLA
```

### SLO-based alerting (preview)
```
Alert when the error budget is burning too fast (burn rate), e.g.:
  fast burn: 2% of monthly budget consumed in 1 hour → page
  slow burn: 10% in 3 days → ticket
→ far fewer, more meaningful pages than threshold alerts
```

## 🟢 कैसे काम करता है? (Hindi)
1. SLI चुनो — यूज़र के नज़रिए से अच्छे events / कुल events (जैसे 500 ms में सफल checkouts / सारे checkouts)।
2. SLO तय करो — उस SLI का लक्ष्य, एक समय-खिड़की में (30 दिन में 99.9%)।
3. SLA ग्राहक के साथ अनुबंध है — SLO से ढीला (99.5%), टूटने पर credit/refund।
4. अलग-अलग features के अलग SLO: पेमेंट सख़्त (99.95%), recommendations ढीला (99%)।
5. 100% मत माँगो; मौजूदा प्रदर्शन नापकर शुरुआत करो; alerts SLO के "burn rate" पर लगाओ।

---

## 🟡 Real World Example

**Google SRE** — Google popularized SLOs and error budgets. Every user-facing service has SLOs agreed between product and SRE, and missing an SLO triggers reliability work instead of feature launches. The SRE books (free online) are the reference.

**AWS SLAs** — public SLAs, e.g. EC2's region-level monthly uptime commitment with service credits for breaches, and S3's monthly uptime SLA. Customers must file claims. AWS's internal SLOs are much stricter than the published SLAs.

**Razorpay / Stripe / payment gateways** — publish uptime and status pages, offer enterprise SLAs, and track internal SLIs like payment success rate and API latency per method (UPI, cards).

**Banks and UPI (NPCI)** — NPCI publishes technical decline rates per bank. These act as public reliability indicators, and banks are pushed to meet regulatory thresholds.

## 🟡 Real Example Hindi में
Google SRE ने SLO और error budget लोकप्रिय किए — SLO टूटा तो नए features रुककर reliability का काम होता है। AWS अपने public SLA में तय uptime का वादा करता है, टूटने पर service credit देता है।
NPCI हर बैंक के "technical decline" दर प्रकाशित करता है — ये बैंकों के लिए public SLI जैसे हैं।

---

## 🟠 My Stack Example

### Define SLIs from your existing metrics (Prometheus)
```promql
# Availability SLI for checkout: non-5xx / all (last 30 days)
sum(rate(http_request_duration_seconds_count{route="/api/v1/checkout", status_class!="5xx"}[30d]))
  / sum(rate(http_request_duration_seconds_count{route="/api/v1/checkout"}[30d]))

# Latency SLI: fraction of checkout requests under 500 ms (bucket le="0.5")
sum(rate(http_request_duration_seconds_bucket{route="/api/v1/checkout", le="0.5"}[30d]))
  / sum(rate(http_request_duration_seconds_count{route="/api/v1/checkout"}[30d]))
```

### SLO spec as code (OpenSLO / Sloth style)
```yaml
version: prometheus/v1
service: checkout
slos:
  - name: availability
    objective: 99.9
    sli:
      events:
        error_query: sum(rate(http_request_duration_seconds_count{route="/api/v1/checkout",status_class="5xx"}[{{.window}}]))
        total_query: sum(rate(http_request_duration_seconds_count{route="/api/v1/checkout"}[{{.window}}]))
    alerting:
      page_alert: { labels: { severity: page } }
      ticket_alert: { labels: { severity: ticket } }
# Sloth generates multi-window burn-rate alert rules + recording rules for Grafana
```

### AWS CloudWatch: ALB-based availability SLI
```
SLI = 1 − (HTTPCode_Target_5XX_Count + HTTPCode_ELB_5XX_Count) / RequestCount
CloudWatch Application Signals → define SLOs on latency/availability per operation
```

### FastAPI / Node: measure what users feel
```
- Count at the edge (ALB/Nginx logs) to include gateway errors and timeouts the app never sees
- Synthetic checks (CloudWatch Synthetics / Checkly) that log in, add to cart, pay (sandbox) every minute
- Mobile RUM (Sentry/Firebase): "API success rate as seen by devices", app start time SLO
```

### Example SLO doc for your food app
```
Service: Ordering API              Owner: orders-team        Window: rolling 30 days
SLI 1 Availability: valid requests (exclude 4xx) returning non-5xx at ALB   SLO 99.9%
SLI 2 Latency: POST /checkout completed < 800 ms                             SLO 95%
SLI 3 Order freshness: order status visible in app within 10 s of change    SLO 99%
Dependencies: payments (SLO 99.95%), catalog (99.9%), Postgres (99.95%)
Error budget policy: if > 100% budget consumed → feature freeze for orders-team until recovered
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between SLI, SLO and SLA?**
A1: An SLI is a quantitative measure of service level from the user's perspective, typically good events over valid events (successful requests, requests under X ms). An SLO is the target value for an SLI over a window (99.9% over 30 days), an internal goal guiding engineering decisions. An SLA is a contract with customers that specifies the promised level and the consequences (credits, refunds) if missed. It's usually set looser than the SLO to leave a safety margin.

**Q2: Why not set a 100% SLO?**
A2: 100% is impossible in practice (networks, dependencies, deploys and hardware all fail) and the cost rises exponentially with each nine. It also blocks change, because any risk becomes unacceptable. Users can't tell the difference above a certain level, since their own networks and devices fail more often. A realistic SLO gives an error budget for innovation and planned risk.

**Q3: What makes a good SLI?**
A3: It reflects real user experience (measured as close to the user as possible: load balancer, client RUM, synthetic probes), it's expressed as a ratio of good to valid events, it excludes events that aren't the service's fault (such as 4xx client errors), it's tied to important user journeys (checkout, login, search), and it's simple enough that everyone understands it. Avoid internal metrics like CPU as SLIs.

**Q4: How do you choose SLO targets?**
A4: Start with user and business needs per journey (payments stricter than recommendations), then look at historical performance (weeks of data) and set achievable targets, slightly above today's to drive improvement. Account for dependencies, since you can't exceed what hard dependencies provide. Agree on the targets with product and engineering, document them with owners and an error budget policy, and review them quarterly.

**Q5: How should alerting relate to SLOs?**
A5: Alert on SLO burn rate, the speed at which the error budget is being consumed, using multiple windows: a fast burn (e.g. 14× the normal rate over 1 h and 5 min windows) pages immediately, and a slow burn (e.g. 1× to 3× over days) creates tickets. This focuses on-call on user-impacting problems, reduces noisy threshold alerts, and catches both sudden outages and slow degradations.

---

## 🔷 Trade-offs
✅ Advantages:
- Objective, user-centric reliability targets; aligns product & engineering; better alerting; prioritization.

❌ Disadvantages:
- Requires good measurement infrastructure; choosing SLIs is hard.
- Too many SLOs = noise; wrong SLIs = optimizing the wrong thing.
- SLAs create legal/financial exposure.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SLI | Measured indicator of service quality | सेवा की गुणवत्ता का नाप |
| SLO | Target for an SLI | नाप का लक्ष्य |
| SLA | Contract with penalties | ग्राहक से अनुबंध |
| Error budget | Allowed unreliability (100% − SLO) | ग़लती की अनुमति |
| Good / valid events | Successful / counted requests | सफल / गिनी जाने वाली requests |
| Rolling window | Moving time period (30 days) | खिसकती समय-खिड़की |
| Burn rate | Speed of budget consumption | budget ख़र्च होने की रफ़्तार |
| RUM | Real user monitoring | असली यूज़र का अनुभव नापना |
| Synthetic monitoring | Scripted probes | नक़ली यूज़र से जाँच |
| Service credit | SLA compensation | SLA टूटने पर मुआवज़ा |

---

## ⚡ 3-Line Summary
**English:**
1. SLI = user-centric measurement (good/valid events); SLO = target over a window; SLA = customer contract with penalties (looser than SLO).
2. Pick SLIs per critical journey (availability, latency, freshness), measure close to users, set realistic targets — never 100%.
3. SLOs create error budgets and drive burn-rate alerting and prioritization.

**Hindi:**
1. SLI = यूज़र के नज़रिए से नाप; SLO = लक्ष्य; SLA = ग्राहक से अनुबंध (SLO से ढीला)।
2. ज़रूरी यूज़र रास्तों के लिए SLI, यूज़र के पास से नापो, यथार्थवादी लक्ष्य — 100% कभी नहीं।
3. SLO से error budget बनता है, जिससे alerts और प्राथमिकताएँ तय होती हैं।

---

## ➡️ Next Topic Suggestion
**104. Error Budgets** — An SLO of 99.9% means 0.1% is allowed to fail. Next: how to spend that budget, burn-rate alerts, and error budget policies that balance feature speed and reliability.
