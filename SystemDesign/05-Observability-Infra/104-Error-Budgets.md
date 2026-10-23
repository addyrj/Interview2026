# 104. Error Budgets
# हिंदी में: Error Budget — SLO के हिसाब से कितनी ग़लतियाँ/downtime "मंज़ूर" है (100% − SLO); budget बचा हो तो तेज़ी से नए features, ख़त्म हो तो पहले reliability ठीक करो

---

## 🔵 Simple Definition (English)
An **error budget** is the **amount of unreliability you're allowed** in a period, defined as **100% − SLO**. With a 99.9% availability SLO over 30 days, the budget is **0.1%**: about **43 minutes** of downtime, or **1 in 1,000 requests** failing.
Teams **spend** the budget on risk (deploys, experiments, migrations, incidents). An **error budget policy** says what happens when it runs out (e.g. a feature freeze and reliability work). It turns reliability into a **shared, data-driven trade-off** between shipping speed and stability.

## 🔵 सरल परिभाषा (Hindi)
Error budget = 100% − SLO। अगर SLO 30 दिन में 99.9% है, तो 0.1% (लगभग 43 मिनट या हर 1000 में 1 request) फ़ेल होने की "छूट" है।
Budget बचा है तो टीम तेज़ी से नए features और प्रयोग कर सकती है; ख़त्म हो गया तो नए features रोककर पहले सिस्टम मज़बूत करना होता है।

---

## 🔴 Problem it Solves
The eternal conflict:
- **Product/dev:** "Ship faster! More features!"
- **Ops/SRE:** "Every deploy risks an outage. Slow down!"

Without a shared rule, decisions are political. The error budget gives an **objective mechanism**:
- Budget **remaining** → reliability is good enough → **ship, experiment, take risks**.
- Budget **exhausted** → users are suffering → **slow down, fix reliability**, until it recovers.
It also prevents **over-investing** in reliability beyond what users need, since unused budget means you could move faster.

## 🔴 यह क्यों बना? (Hindi)
Product कहता है "जल्दी features भेजो", ops कहता है "हर deploy ख़तरा है, रुको" — बिना नियम के यह राजनीति बन जाती है।
Error budget साफ़ नियम देता है: budget बचा है → तेज़ी से भेजो; ख़त्म → रुककर reliability ठीक करो। और ज़रूरत से ज़्यादा reliability पर पैसा बर्बाद होने से भी बचाता है।

---

## 🟢 How it Works — Step by Step

### Budget math

```
SLO 99.9% over 30 days
  Time-based:    30 × 24 × 60 = 43,200 min × 0.1% = 43.2 min of "bad minutes"
  Request-based: 100M requests/month × 0.1% = 100,000 failed requests allowed

Budget consumed by:
  - incident on 5th: 15 min full outage           → 35% of budget
  - bad deploy on 12th: 2% errors for 1 hour       → 2% × 60 min = 1.2 bad-min eq. (~3%)
  - slow dependency latency SLO misses             → ...
Remaining: tracked live on a dashboard
```

### Burn rate (how fast you're spending)

```
burn rate = observed error rate / allowed error rate (1 − SLO)
  SLO 99.9% → allowed 0.1%
  Current error rate 1.4% → burn rate 14 → you'd exhaust a 30-day budget in ~2 days

Multi-window, multi-burn-rate alerts (Google SRE recommendation):
┌───────────────┬─────────────┬────────────┬────────────────────────────┬──────────┐
│ Burn rate     │ Long window │ Short win. │ Meaning                    │ Action   │
├───────────────┼─────────────┼────────────┼────────────────────────────┼──────────┤
│ 14.4          │ 1 h         │ 5 min      │ 2% budget in 1 hour         │ PAGE     │
│ 6             │ 6 h         │ 30 min     │ 5% budget in 6 hours        │ PAGE     │
│ 1             │ 3 days      │ 6 h        │ 10% budget in 3 days        │ TICKET   │
└───────────────┴─────────────┴────────────┴────────────────────────────┴──────────┘
Short window confirms the problem is still happening (fast reset after recovery).
```

### Error budget policy (agreed in writing by product + engineering)

```
Budget > 50% remaining   → normal velocity; experiments & risky migrations allowed
Budget 0–50%             → extra review for risky changes; prioritize top reliability bugs
Budget exhausted         → FEATURE FREEZE for that service (except security/critical fixes);
                           team works on reliability (postmortem actions, tests, capacity)
                           until budget recovers (rolling window) or SLO met for N days
Single incident > 20% of budget → mandatory postmortem with action items
Disagreements → escalate to agreed decision-maker (e.g. VP Eng)
```

### Spending the budget intentionally
```
- Faster deploy cadence, canary experiments, chaos tests (Topic 108), dependency upgrades,
  planned maintenance — all "spend" budget knowingly
- If budget is ALWAYS untouched → SLO may be too loose or you're too cautious → ship faster
- If budget is ALWAYS blown → SLO too strict for current architecture or real reliability problem
```

### Who owns what
```
Service team owns its SLO & budget; dependencies' failures still count (users don't care whose fault)
→ motivates graceful degradation, timeouts, fallbacks, and better dependency SLOs
```

## 🟢 कैसे काम करता है? (Hindi)
1. Budget निकालो: SLO 99.9% → 30 दिन में 43 मिनट या 1000 में 1 request फ़ेल होने की छूट।
2. हर incident और ख़राब deploy budget में से कुछ ख़र्च करता है — dashboard पर बचा हुआ budget दिखता है।
3. Burn rate = अभी की error दर / अनुमत दर; 14 गुना रफ़्तार = 2 दिन में पूरा budget ख़त्म → तुरंत alert (page)।
4. Policy पहले से लिखी हो: budget बचा → सामान्य रफ़्तार; ख़त्म → feature freeze, reliability का काम।
5. Budget कभी इस्तेमाल न हो तो आप ज़रूरत से ज़्यादा सावधान हैं; हमेशा टूटे तो SLO या architecture ठीक करो।

---

## 🟡 Real World Example

**Google SRE** — introduced error budgets. If a service exhausts its budget, launches are halted until reliability improves. SRE teams can also hand back pager responsibility to the dev team if reliability work isn't prioritized. This is described in the SRE book and *The Site Reliability Workbook* (Evernote and Home Depot case studies).

**Spotify, LinkedIn, Atlassian** — adopted SLO + error budget practices to decide release velocity per service, using burn-rate alerts instead of static thresholds to reduce pager fatigue.

**Indian SaaS / fintech (Freshworks, Razorpay-scale)** — teams track SLOs for critical APIs (payments, login) with burn-rate alerting, and freeze risky changes during high-traffic events (festive sales) when budgets are tight.

## 🟡 Real Example Hindi में
Google SRE ने error budget शुरू किया — budget ख़त्म तो नए launches रुकते हैं जब तक reliability ठीक न हो। Spotify, LinkedIn, Atlassian ने भी यही अपनाया और static threshold alerts की जगह burn-rate alerts लगाए।
त्योहारी सेल के समय भारतीय कंपनियाँ budget कम होने पर जोखिम वाले बदलाव रोक देती हैं।

---

## 🟠 My Stack Example

### Prometheus recording rules + burn-rate alerts (SLO 99.9% for checkout)
```yaml
groups:
- name: slo-checkout
  rules:
  - record: slo:checkout_errors:ratio_rate5m
    expr: |
      sum(rate(http_request_duration_seconds_count{route="/api/v1/checkout",status_class="5xx"}[5m]))
      / sum(rate(http_request_duration_seconds_count{route="/api/v1/checkout"}[5m]))
  - record: slo:checkout_errors:ratio_rate1h
    expr: |
      sum(rate(http_request_duration_seconds_count{route="/api/v1/checkout",status_class="5xx"}[1h]))
      / sum(rate(http_request_duration_seconds_count{route="/api/v1/checkout"}[1h]))

  - alert: CheckoutErrorBudgetFastBurn
    expr: slo:checkout_errors:ratio_rate1h > (14.4 * 0.001) and slo:checkout_errors:ratio_rate5m > (14.4 * 0.001)
    labels: { severity: page }
    annotations:
      summary: "Checkout burning error budget 14x (2% of monthly budget per hour)"
      runbook: "https://wiki/runbooks/checkout-errors"
```

### Remaining budget panel (Grafana, 30d)
```promql
1 - (
  (sum(increase(http_request_duration_seconds_count{route="/api/v1/checkout",status_class="5xx"}[30d]))
   / sum(increase(http_request_duration_seconds_count{route="/api/v1/checkout"}[30d])))
  / 0.001
)
# 1.0 = full budget left, 0 = exhausted, negative = SLO breached
```

### Gate deploys on the budget (CI/CD — GitHub Actions step)
```yaml
- name: Check error budget before prod deploy
  run: |
    REMAINING=$(curl -s "$PROM/api/v1/query?query=slo:checkout_budget_remaining" | jq -r '.data.result[0].value[1]')
    echo "Budget remaining: $REMAINING"
    if (( $(echo "$REMAINING < 0" | bc -l) )) && [ "${{ github.event.inputs.override }}" != "true" ]; then
      echo "Error budget exhausted → feature deploys frozen (use override for critical fixes)"; exit 1
    fi
```

### Make budget-spending safer
```
- Canary deploys (5% traffic) + automatic rollback on error spike (Argo Rollouts / Flagger / CodeDeploy)
- Feature flags → turn off a bad feature without redeploy
- Graceful degradation & timeouts → dependency failures cost less budget
```

### Error budget report (monthly, for product + eng)
```
Service: Checkout  SLO 99.9%  Budget used: 72%
Top consumers: payment gateway timeout incident (45%), Diwali traffic spike (18%), bad deploy v2.31 (9%)
Actions: add second payment gateway fallback, pre-scale for sales, canary for checkout releases
Decision: continue feature work with mandatory canary; next month target < 60% usage
```

---

## ⚫ Interview Questions + Answers

**Q1: What is an error budget?**
A1: The allowed amount of unreliability implied by an SLO: 100% minus the SLO target over the SLO window. For a 99.9% monthly availability SLO, that's about 43 minutes of downtime or 0.1% of requests failing. It's spent by incidents, risky changes and planned maintenance, and an error budget policy dictates actions (like freezing features) when it's exhausted.

**Q2: How do error budgets balance velocity and reliability?**
A2: They make the trade-off objective and pre-agreed. When budget remains, users are getting the promised reliability, so teams can ship quickly and take risks. When it's exhausted, users are hurting, so effort shifts to reliability until the budget recovers. Product and engineering agree on the policy in advance, which removes political debates, and the same mechanism discourages over-engineering reliability beyond what users need.

**Q3: What is a burn rate and how do you alert on it?**
A3: Burn rate is how fast the error budget is being consumed relative to a steady rate that would exactly use it up over the window: observed error ratio divided by (1 − SLO). A burn rate of 1 uses the whole budget in 30 days, and 14.4 uses 2% of it per hour. Use multi-window, multi-burn-rate alerts: page on high burn over 1 h confirmed by 5 min (and 6 h / 30 min), and ticket on slow burns over days. This catches both sudden outages and slow degradations with few false alarms.

**Q4: What should an error budget policy contain?**
A4: SLO definitions and owners; thresholds and corresponding actions (normal, caution, freeze); what changes are still allowed during a freeze (security and critical fixes, reliability work); requirements for postmortems (e.g. any incident consuming more than 20% of the budget); how the freeze ends (budget recovery or a period meeting the SLO); and an escalation path for disagreements. It must be agreed and signed off by product and engineering leadership.

**Q5: Your team never uses its error budget. Is that good?**
A5: Not necessarily. It may mean the SLO is too loose, or the team is too risk-averse and slower than necessary. Either tighten the SLO if users would benefit, or use the budget: deploy more frequently, run experiments and chaos tests, and do overdue migrations. Error budgets are meant to be spent wisely, not hoarded. It also helps to check that the SLI measures the right thing (it could be missing real user pain).

---

## 🔷 Trade-offs
✅ Advantages:
- Data-driven release decisions; aligns teams; fewer, better alerts; avoids over/under-investing in reliability.

❌ Disadvantages:
- Needs trustworthy SLIs and organizational buy-in; freezes can frustrate product teams.
- Dependency-caused failures still consume budget (can feel unfair but encourages resilience).
- Gaming risk if SLIs are poorly chosen.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Error budget | Allowed unreliability (100% − SLO) | मंज़ूर ग़लती की मात्रा |
| Burn rate | Speed of budget consumption | budget ख़र्च होने की रफ़्तार |
| Error budget policy | Agreed actions by budget level | budget के हिसाब से नियम |
| Feature freeze | Pause feature releases | नए features रोकना |
| Multi-window alert | Long + short window confirmation | दो समय-खिड़की वाला alert |
| Canary | Small % rollout | थोड़े ट्रैफ़िक पर पहले |
| Postmortem | Blameless incident review | बिना दोष की incident समीक्षा |
| Rolling window | Moving period (30 days) | खिसकती अवधि |

---

## ⚡ 3-Line Summary
**English:**
1. Error budget = 100% − SLO (99.9% → ~43 min or 0.1% requests per month) — the reliability you're allowed to "spend".
2. Alert on burn rate (multi-window: page for fast burn, ticket for slow); track remaining budget on dashboards.
3. A written policy links budget to actions: ship freely when budget remains, freeze features and fix reliability when exhausted.

**Hindi:**
1. Error budget = 100% − SLO — कितनी ग़लती "ख़र्च" करने की छूट है।
2. Burn rate पर alert (तेज़ → page, धीमा → ticket); बचा budget dashboard पर।
3. लिखी policy: budget बचा → तेज़ी से भेजो; ख़त्म → features रोककर reliability ठीक करो।

---

## ➡️ Next Topic Suggestion
**105. Disaster Recovery (RPO/RTO)** — Error budgets cover everyday failures. Next: planning for disasters (region outages, data corruption, ransomware, accidental deletes) with RPO, RTO, backups and DR strategies.
