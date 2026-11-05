# 11. Site Reliability Engineering (SRE)
# हिंदी में: Site Reliability Engineering (SRE)

---

## 🔵 Simple Definition (English)
**SRE** is an approach, created at Google, that applies software engineering to operations problems. SRE teams define reliability targets (SLOs), measure them (SLIs), allow a small "error budget" for failures, automate repetitive work (toil), and use data to balance new features against stability. Google's phrase: "class SRE implements interface DevOps".

## 🔵 सरल परिभाषा (Hindi)
**SRE** एक approach है, जिसे Google ने बनाया, जो operations की problems पर software engineering लगाती है। SRE teams reliability targets (SLOs) तय करती हैं, उन्हें नापती हैं (SLIs), एक छोटा "error budget" असफलताओं के लिए रखती हैं, बार-बार का काम (toil) automate करती हैं, और data से नए features बनाम stability का संतुलन करती हैं। Google का वाक्य: "class SRE implements interface DevOps"।

---

## 🔴 Problem it Solves
"Make it 100% reliable" is impossible and extremely expensive; every extra "nine" of uptime costs 10x more. Meanwhile product teams want speed and ops teams want stability, leading to conflict decided by opinions. SRE replaces opinion with numbers: if reliability is above target, ship faster; if the budget is exhausted, freeze features and fix reliability.

## 🔴 यह क्यों बना? (Hindi)
"100% reliable बनाओ" असंभव और बहुत महँगा है; uptime में हर अतिरिक्त "nine" 10 गुना खर्च कराता है। उधर product teams गति चाहती हैं और ops teams stability, जिससे टकराव राय के आधार पर सुलझता है। SRE राय की जगह आँकड़े रखता है: reliability target से ऊपर है तो तेज़ ship करो; budget खत्म हो तो features रोककर reliability ठीक करो।

---

## 🟢 How it Works — Step by Step

```
Step 1 -> Pick SLIs  : what to measure (successful requests %, latency p99)
Step 2 -> Set SLO    : target, e.g. 99.9% of requests succeed in 30 days
Step 3 -> Error budget = 100% - SLO = 0.1% (about 43 minutes of downtime per 30 days)
Step 4 -> Measure continuously (Prometheus, CloudWatch) and alert on budget burn rate
Step 5 -> Budget left  -> ship features faster
          Budget spent -> freeze risky releases, fix reliability
Step 6 -> Incident -> on-call responds -> blameless post-mortem -> action items
Step 7 -> Automate toil (manual repetitive work) to keep ops work under ~50% of time
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 -> SLIs चुनो : क्या नापना है (सफल requests %, latency p99)
Step 2 -> SLO तय करो : target, जैसे 30 दिन में 99.9% requests सफल
Step 3 -> Error budget = 100% - SLO = 0.1% (30 दिन में लगभग 43 मिनट downtime)
Step 4 -> लगातार नापो (Prometheus, CloudWatch) और budget burn rate पर alert लगाओ
Step 5 -> Budget बचा है  -> features तेज़ ship करो
          Budget खत्म   -> risky releases रोको, reliability ठीक करो
Step 6 -> Incident -> on-call जवाब देता है -> blameless post-mortem -> action items
Step 7 -> Toil (बार-बार का manual काम) automate करो ताकि ops काम ~50% समय से कम रहे
```

---

## 🟡 Real World Example
**UPI payment service.** SLO: 99.95% of payment requests succeed within 2 seconds per month. Error budget: about 21 minutes. A bad release burns 15 minutes of budget in one day. SRE policy says remaining budget is low, so next week only reliability fixes ship. Customers get a stable service, and the team has a clear, agreed rule, not an argument.

**Your VPS:** SLI = share of `/health` checks that return 200. SLO = 99.5% per month (about 3.6 hours of allowed downtime). Uptime Kuma gives you the measurement.

## 🟡 Real Example Hindi mein
**UPI payment service।** SLO: महीने में 99.95% payment requests 2 सेकंड में सफल हों। Error budget: लगभग 21 मिनट। एक बुरी release एक दिन में 15 मिनट का budget खा जाती है। SRE नीति कहती है budget कम बचा है, इसलिए अगले हफ्ते सिर्फ reliability fixes जाएँगे। ग्राहकों को stable service मिलती है और team के पास बहस की जगह तय नियम है।

**आपका VPS:** SLI = `/health` checks का वह हिस्सा जो 200 लौटाता है। SLO = महीने में 99.5% (लगभग 3.6 घंटे अनुमत downtime)। Uptime Kuma आपको measurement देता है।

---

## 💻 Code / Config Example — Basic
Compute the error budget from an SLO (Python, runs anywhere).

```python
# error_budget.py - how much downtime does an SLO allow?
def allowed_downtime_minutes(slo_percent: float, days: int = 30) -> float:
    """Return minutes of downtime allowed in the window."""
    total_minutes = days * 24 * 60                      # total minutes in the window
    error_fraction = (100.0 - slo_percent) / 100.0      # share of time allowed to fail
    return total_minutes * error_fraction               # minutes of allowed failure

for slo in (99.0, 99.5, 99.9, 99.95, 99.99):            # common SLO targets
    minutes = allowed_downtime_minutes(slo)             # compute budget
    print(f"SLO {slo}% -> {minutes:.1f} minutes per 30 days")   # show result
```

## 💻 Code / Config Example — Advanced
Prometheus SLO alert rules (request success ratio with a burn-rate alert) plus a synthetic health check workflow. Assumes your app exports a counter `http_requests_total{status=...}`. Rules are syntax-checked as YAML only, not with `promtool` (not installed).

```yaml
# slo-rules.yml - load via rule_files in prometheus.yml
groups:
  - name: api-slo                                           # rule group name
    rules:
      - record: job:http_success_ratio:rate5m               # recording rule: success ratio over 5 minutes
        expr: |                                             # PromQL expression
          sum(rate(http_requests_total{job="api",status!~"5.."}[5m]))
          /
          sum(rate(http_requests_total{job="api"}[5m]))
      - record: job:http_success_ratio:rate1h               # same over 1 hour
        expr: |                                             # PromQL expression
          sum(rate(http_requests_total{job="api",status!~"5.."}[1h]))
          /
          sum(rate(http_requests_total{job="api"}[1h]))
      - alert: ErrorBudgetFastBurn                          # alert name
        expr: |                                             # both windows are bad = real, ongoing problem
          job:http_success_ratio:rate5m < 0.985
          and
          job:http_success_ratio:rate1h < 0.985
        for: 5m                                             # must hold for 5 minutes (avoid flapping)
        labels:
          severity: page                                    # wake someone up
        annotations:
          summary: "API is burning error budget fast (success ratio under 98.5%)"   # message text
```

```yaml
# .github/workflows/synthetic-check.yml
name: Synthetic check                          # simple SLI probe from outside your server
on:
  schedule:
    - cron: "*/15 * * * *"                     # every 15 minutes (GitHub may delay scheduled runs)
permissions: {}                                # no repository permissions needed
jobs:
  probe:
    runs-on: ubuntu-latest                     # runner
    steps:
      - name: Check health endpoint            # label
        run: curl -fsS --max-time 10 --retry 2 https://example.com/health   # replace with your URL; non-200 fails the run
```

---

## 🟠 My Stack Integration
- **Node.js:** `prom-client` exposes `/metrics`; **FastAPI:** `prometheus-fastapi-instrumentator` does the same.
- **Nginx:** enable `stub_status` or log format with `$request_time` and `$status`; ship to Prometheus (nginx exporter) or Loki.
- **VPS:** Uptime Kuma or Better Stack for external checks; `docker compose` restart policies cut toil.
- **AWS:** CloudWatch alarms, ALB 5xx metrics and Route 53 health checks as SLIs.
- Write a one-page **runbook** for each alert: what it means, first 3 things to check, how to roll back.

```yaml
# prometheus.yml fragment: scrape your app and load SLO rules
global:
  scrape_interval: 15s                          # collect metrics every 15 seconds
rule_files:
  - slo-rules.yml                               # recording and alert rules above
scrape_configs:
  - job_name: api                               # matches job="api" in the rules
    static_configs:
      - targets: ["api:8000"]                   # container name and port on the compose network
```
Security: metrics endpoints can leak internals; do not expose `/metrics` publicly (restrict in Nginx or the network). On-call access needs MFA and audit logs.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Setting SLO to 100% or 99.999% "to be safe".
✅ Correct: Choose a level users actually notice; each extra nine multiplies cost and slows delivery.

❌ Mistake 2: Measuring server health (CPU) instead of user experience.
✅ Correct: SLIs reflect users: success rate, latency, freshness.

❌ Mistake 3: Alerting on every blip.
✅ Correct: Alert on symptoms and budget burn that need human action; everything else goes to dashboards.

❌ Mistake 4: SRE becomes a ticket-taking ops team.
✅ Correct: Cap toil, spend time on automation and reliability engineering.

---

## 🧠 Tricky Interview Question
**"Our service has been 100% available for 6 months. Is the SRE team doing a great job?"**

Answer: Not necessarily. A 100% record against a 99.9% SLO means the error budget was never used, so the team may be too cautious: releasing too slowly, over-investing in reliability users do not need, or the SLO is too loose to detect problems. SRE aims for hitting the target, not exceeding it by far. Use spare budget for faster releases, experiments or chaos testing. Also verify the SLIs really measure what users feel.

---

## ⚫ Interview Questions + Answers

Q1: SLI vs SLO vs SLA?
A1: SLI is the measurement (e.g., % successful requests). SLO is the internal target for that measurement (99.9%). SLA is a contract with customers with penalties if missed; it is usually looser than the SLO.

Q2: What is an error budget?
A2: The allowed unreliability = 100% minus SLO. It turns reliability into a shared resource: spend it on releases, and slow down when it is gone.

Q3: What is toil?
A3: Manual, repetitive, automatable work that scales linearly with service growth and has no lasting value (e.g., restarting a service by hand). SRE aims to keep it below about 50% of time.

Q4: SRE vs DevOps?
A4: DevOps is a culture and set of practices. SRE is a concrete implementation with defined roles, SLOs, error budgets and on-call. They share goals: shared ownership, automation, measurement.

Q5: What are the "four golden signals"?
A5: Latency, traffic, errors and saturation. Monitor these for any service.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have users who depend on uptime and real traffic.
- Reliability debates need data, not opinions.

❌ Avoid (full formal SRE) when:
- A tiny team with one small app: use a light version (one SLO, one uptime check, a runbook) instead of a dedicated team.

---

## 📊 Visual Diagram
```
  SLI (measure)  ---->  SLO (target)  ---->  Error budget = 100% - SLO
        |                                          |
        |                      budget left?  ------+------ budget spent?
        v                          |                           |
   dashboards, alerts        ship features faster       freeze, fix reliability
                                   \_______________  ______________/
                                                   v
                                    incidents -> post-mortem -> automation
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SLI | Measured indicator of service quality | सेवा की गुणवत्ता का मापा गया संकेतक |
| SLO | Target value for an SLI | SLI का लक्ष्य |
| SLA | Customer contract with penalties | दंड वाला ग्राहक अनुबंध |
| Error budget | Allowed amount of failure | अनुमत असफलता की मात्रा |
| Toil | Repetitive manual operational work | बार-बार का manual काम |
| Burn rate | Speed of using up the error budget | Error budget खर्च होने की गति |
| MTTR | Mean time to recover | औसत recovery समय |

---

## ⚡ 3-Line Summary
English: SRE treats operations as a software problem using SLIs, SLOs and error budgets.
It balances feature speed with reliability using data, and removes toil with automation.
Pick realistic SLOs and alert on user-facing symptoms.

Hindi: SRE operations को software समस्या मानकर SLI, SLO और error budget इस्तेमाल करता है।
यह data से feature गति और reliability का संतुलन करता है और automation से toil हटाता है।
यथार्थवादी SLO चुनें और user-facing लक्षणों पर alert लगाएँ।

---

## ➡️ Next Topic
**12. Platform Engineering Basics** — how large teams give developers self-service tools so every team need not reinvent pipelines and infrastructure.
