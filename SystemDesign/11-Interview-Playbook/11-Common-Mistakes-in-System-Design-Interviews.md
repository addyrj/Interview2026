# 11. Common Mistakes in System Design Interviews
# हिंदी में: System Design इंटरव्यू की आम ग़लतियाँ — वो चूकें जिनसे अच्छे engineers भी offer खो देते हैं (बिना पूछे design, बिना numbers, buzzwords, ज़रूरत से ज़्यादा जटिल design, failures भूलना, चुप रहना, समय ख़त्म) — और हर एक से बचने का तरीका

---

## 🔵 Simple Definition (English)
A checklist of the **most frequent failure patterns** in system design interviews (backend, frontend, mobile and AI), each with **what it looks like**, **why it hurts your evaluation** and **the fix**. Most rejections aren't caused by missing knowledge but by **process, communication and judgement** mistakes.

## 🔵 सरल परिभाषा (Hindi)
System design इंटरव्यू (backend, frontend, mobile, AI) की सबसे आम असफलताओं की सूची — हर एक: कैसी दिखती है, नंबर क्यों कटते हैं, और ठीक कैसे करें। ज़्यादातर rejection ज्ञान की कमी से नहीं, बल्कि तरीके, बातचीत और समझदारी की ग़लतियों से होते हैं।

---

## 🔴 Problem it Solves
Strong engineers often underperform because the interview format differs from daily work: it's time-boxed, ambiguous and evaluated on visible reasoning. Knowing the traps in advance lets you **self-correct in real time** ("I'm going deep too early, let me finish the end-to-end flow first").

## 🔴 यह क्यों बना? (Hindi)
मज़बूत engineers भी कम नंबर लाते हैं क्योंकि इंटरव्यू रोज़ के काम से अलग है — समय सीमित, सवाल अस्पष्ट, और जाँच दिखने वाली सोच की; जाल पहले से पता हों तो उसी समय ख़ुद को सुधार सकते हो ("मैं बहुत जल्दी गहराई में जा रहा हूँ, पहले पूरा flow ख़त्म करूँ")।

---

## 🟢 How it Works — Step by Step (mistakes → fixes)

### Process mistakes

```
1. Designing before clarifying
   Looks like: drawing boxes in minute 1
   Fix: 5 minutes of requirements + scale + non-functional + out-of-scope; write them down
2. No numbers (or numbers never used)
   Fix: 3–5 min estimation; then say "because writes are 200k/s, I'll shard by user_id"
3. Going deep too early
   Fix: complete end-to-end HLD first; park deep topics in a visible list; then deep dive
4. Running out of time / no wrap-up
   Fix: time plan (Playbook 01/02); check the clock at 15, 30, 40 min; leave 3 min for trade-offs & summary
5. Ignoring interviewer hints
   Fix: when they ask "what about X?", it's a signal — pause, explore X; ask "is this the direction you'd like?"
```

### Design-judgement mistakes

```
6. Buzzword architecture ("Kafka + Kubernetes + microservices + Cassandra") without reasons
   Fix: justify each component by a requirement/number; mention the simpler alternative and why not
7. Over-engineering (multi-region active-active for 1k users)
   Fix: design for stated scale, explain how it evolves at 10×/100×
8. Under-engineering (one MySQL for 1M writes/s, no cache for 100:1 reads)
   Fix: let estimates drive scaling choices
9. One-size consistency (strong everywhere or eventual everywhere)
   Fix: per-data decisions — money/inventory strong; likes/feeds eventual; say why
10. Forgetting idempotency & retries (double charges, duplicate messages)
   Fix: idempotency keys, dedupe on consumers, at-least-once assumption
11. Caching without invalidation/stampede plan
   Fix: specify pattern (cache-aside), TTL, invalidation on write, stampede protection, what's never cached
12. Ignoring hot spots (celebrity users, viral posts, big tenants, flash sales)
   Fix: discuss hot keys: sharding strategy, special handling (fan-out on read), queues, rate limits
13. Ignoring failure modes
   Fix: for each critical component: "if it fails, users see…, we recover by…"; timeouts, circuit breakers, DLQs
14. Forgetting non-functional concerns: security, privacy, observability, cost
   Fix: 1–2 sentences each in wrap-up: auth/authz, PII & DPDP, metrics/alerts/SLOs, cost drivers
```

### Communication mistakes

```
15. Silence while thinking
   Fix: think aloud ("I'm weighing two options: …")
16. Messy, unlabeled diagram
   Fix: left-to-right flow, labeled arrows (protocol, payload), numbered steps
17. Arguing instead of collaborating
   Fix: ask what concern they have; adapt or defend with reasoning politely
18. Not stating assumptions
   Fix: "I'll assume India-first, 50M DAU, mobile-heavy; tell me if different"
19. Monologue without check-ins
   Fix: brief check-ins after requirements, HLD, and before deep dives
```

### Role-specific mistakes

```
Frontend: only happy path (no loading/empty/error/offline), no a11y/i18n, no API/pagination design, no
  performance numbers, XSS-unsafe rendering, "just use Redux" without state reasoning
Mobile: treating it like web (no lifecycle/background/offline), ignoring old app versions & force update,
  storing tokens insecurely, forgetting push/deep links, no low-end device thinking
AI: "the LLM will handle it" (no retrieval/eval), security only via prompts, no cost/token estimate,
  no hallucination plan, no streaming/latency budget, unbounded agents, no human handoff
Backend: single DB for every workload, no queues for slow work, synchronous chains of 10 services,
  no read/write path distinction
```

### 60-second self-check during the interview

```
□ Did I write requirements & scale?      □ Do my numbers justify my components?
□ Is the end-to-end flow complete?       □ Where's my SPOF / failure plan?
□ Consistency choice per data type?      □ Idempotency & retries covered?
□ Caching + invalidation explained?      □ Security, observability, cost mentioned?
□ Have I checked in with the interviewer in the last 10 minutes?
```

## 🟢 कैसे काम करता है? (Hindi)
1. तरीके की ग़लतियाँ: बिना पूछे design (5 मिनट ज़रूरतें लिखो), numbers नहीं या इस्तेमाल नहीं (अनुमान से फ़ैसले), बहुत जल्दी गहराई (पहले पूरा flow, गहरे विषय "parking list" में), समय ख़त्म (15, 30, 40 मिनट पर घड़ी देखो), hints अनदेखे (interviewer का "X का क्या?" एक संकेत है)।
2. Design की ग़लतियाँ: buzzwords बिना कारण, 1k users के लिए multi-region (ज़्यादा जटिल) या 10 लाख writes/s के लिए एक MySQL (कम), हर जगह एक ही consistency, idempotency/retries भूलना, cache का invalidation/stampede नहीं, hot spots (celebrity, flash sale) नहीं, failures नहीं, security/privacy/निगरानी/ख़र्च भूलना।
3. बातचीत की ग़लतियाँ: चुप रहना (ज़ोर से सोचो), गड़बड़ diagram (बाएँ से दाएँ, labels, क्रमांक), बहस (चिंता पूछो, तर्क से समझाओ), assumptions न बताना, बिना रुके बोलते जाना (बीच-बीच में पूछो)।
4. Role के हिसाब से: frontend — सिर्फ़ happy path, a11y/i18n/API/performance नहीं; mobile — web जैसा (lifecycle, offline, पुराने versions, push नहीं); AI — "LLM संभाल लेगा" (retrieval, evals, ख़र्च, hallucination, streaming, सीमित agents नहीं); backend — हर काम एक DB, queues नहीं, 10 services की लंबी sync कड़ी।
5. 60 सेकंड की self-check सूची: ज़रूरतें और पैमाना लिखा? numbers से components साबित? पूरा flow? SPOF/failure? consistency हर डेटा के हिसाब से? idempotency? cache + invalidation? security/निगरानी/ख़र्च? पिछले 10 मिनट में interviewer से पूछा?

---

## 🟡 Real World Example
Interview debrief notes at large tech companies commonly cite: "didn't clarify requirements", "jumped to a specific technology without justification", "couldn't explain trade-offs", "ran out of time before discussing scaling", and "didn't consider failure scenarios". The strongest positive signals are "drove the discussion", "quantified decisions" and "adapted well to feedback". Candidates who practise with a timer and a checklist fix most of these quickly.

## 🟡 Real Example Hindi में
बड़ी कंपनियों के debrief notes में आम बातें: "ज़रूरतें नहीं पूछीं", "बिना कारण technology पर कूदे", "trade-offs नहीं समझा पाए", "scaling से पहले समय ख़त्म", "failures नहीं सोचे"; सबसे अच्छे संकेत — "बातचीत ख़ुद चलाई", "फ़ैसले numbers से", "feedback पर अच्छे से ढले"; timer और checklist के साथ अभ्यास से ज़्यादातर ग़लतियाँ जल्दी सुधरती हैं।

---

## 🟠 My Stack Example

### Turning a weak answer into a strong one
```
Weak:  "We'll use Kafka and MongoDB and Redis and deploy on Kubernetes."
Strong: "Orders are ~300/s at peak with strong consistency needs, so Postgres with idempotent writes is enough;
         the outbox publishes events to Kafka because 5 downstream consumers (notifications, analytics, rider
         assignment…) need decoupling and replay. Menu reads are 100× writes, so cache-aside in Redis with a
         60 s TTL and invalidation on edits. ECS is sufficient; Kubernetes would add ops cost we don't need yet."
```

---

## ⚫ Interview Questions + Answers

**Q1: What's the single most common mistake?**
A1: Starting to design before clarifying requirements and scale. It leads to solving the wrong problem, unjustified components and wasted time. Spend the first five minutes on functional and non-functional requirements, scale assumptions and scope, and write them down.

**Q2: How do you avoid over-engineering?**
A2: Design for the stated scale and requirements, justify every component with a requirement or a number, prefer the simplest architecture that works, and explicitly describe how it would evolve at 10× or 100× (sharding, multi-region, more async processing). Interviewers reward judgement about when complexity is warranted.

**Q3: How do you recover if you realize you've gone off track?**
A3: Say so briefly and steer back: "I've spent a while on storage. Let me finish the end-to-end flow and come back to it." Interviewers value self-awareness and time management. Use the parking-lot list to keep open threads visible.

**Q4: How should you respond when the interviewer challenges your design?**
A4: Treat it as collaboration. Ask what concern drives the question (latency, consistency, cost, failure), then either explain your reasoning with trade-offs or adapt the design. Acknowledge good points quickly. Defensiveness and stubbornness are negative signals, while thoughtful adaptation is positive.

**Q5: What should the last three minutes look like?**
A5: Summarize the design against the requirements, highlight key trade-offs and their alternatives, mention failure handling, monitoring, security and cost briefly, note what you'd improve with more time or at larger scale, and ask the interviewer one or two thoughtful questions.

---

## 🔷 Trade-offs
✅ Checklists prevent omissions — ❌ don't recite them mechanically; adapt to the conversation.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Scope creep | Expanding beyond needs | ज़रूरत से ज़्यादा फैलाव |
| Over-engineering | More complexity than needed | ज़रूरत से ज़्यादा जटिल |
| Hot spot | Overloaded key/partition | भीड़ वाला हिस्सा |
| Parking lot | List of deferred topics | बाद के विषयों की सूची |
| Check-in | Brief alignment question | बीच में पुष्टि |
| Debrief | Interviewer feedback discussion | इंटरव्यू के बाद की चर्चा |

---

## ⚡ 3-Line Summary
**English:**
1. Process traps: no clarification, no numbers, premature depth, poor time management, ignored hints.
2. Judgement traps: buzzwords, over/under-engineering, uniform consistency, no idempotency/invalidation/hot-spot/failure plans, missing security/observability/cost.
3. Communication & role traps: silence, messy diagrams, arguing, no assumptions; frontend/mobile/AI-specific omissions — fix with a timer and the 60-second self-check.

**Hindi:**
1. तरीके के जाल: बिना पूछे, बिना numbers, जल्दी गहराई, समय, hints अनदेखे।
2. समझदारी के जाल: buzzwords, ज़्यादा/कम जटिलता, एक ही consistency, idempotency/cache/hot spot/failure नहीं, security/ख़र्च नहीं।
3. बातचीत और role के जाल — timer और 60 सेकंड की self-check से सुधारो।

---

## ➡️ Next Topic Suggestion
**12. "Tell me about a system you designed"** — The last playbook topic: presenting your own projects convincingly in project deep-dive rounds, with a structure, metrics and honest trade-offs.
