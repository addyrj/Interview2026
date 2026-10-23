# 12. "Tell me about a system you designed" — how to present your own projects
# हिंदी में: "आपने जो system बनाया उसके बारे में बताइए" — अपने project को इंटरव्यू में असरदार तरीके से पेश करना: संदर्भ और पैमाना, आपकी भूमिका, architecture, मुख्य फ़ैसले और trade-offs, मुश्किलें/incidents, नतीजे (numbers के साथ), और आज होता तो क्या बदलते — ईमानदारी से

---

## 🔵 Simple Definition (English)
The **project deep-dive** (also called "past project", "technical retrospective" or the system-design part of behavioural rounds) asks you to explain a real system you built or significantly shaped. Interviewers evaluate **ownership, technical depth, decision-making, impact and honesty**, and probe with follow-ups like "Why not X?", "How did you measure that?", "What broke?" and "What would you change?"
A strong answer follows a clear structure, sometimes called **C-R-A-D-C-R-L**:
1. **Context**: the business problem, users and scale.
2. **Role**: what you owned ("I" vs "we").
3. **Requirements and constraints**: functional, non-functional, deadlines, team.
4. **Architecture**: a diagram of the main components and data flow.
5. **Decisions and trade-offs**: 2–3 key choices with alternatives considered.
6. **Challenges**: incidents, scaling issues, bugs and how you solved them.
7. **Results and Learnings**: metrics, impact, what you'd do differently.

## 🔵 सरल परिभाषा (Hindi)
Project deep-dive में आपसे कोई असली system समझाने को कहा जाता है जो आपने बनाया या जिसमें बड़ी भूमिका निभाई; interviewer मालिकाना (ownership), तकनीकी गहराई, फ़ैसले लेने का तरीका, असर और ईमानदारी देखते हैं, और पूछते हैं "X क्यों नहीं?", "कैसे नापा?", "क्या टूटा?", "अब क्या बदलते?"।
ढाँचा: संदर्भ (business समस्या, यूज़र्स, पैमाना) → आपकी भूमिका ("मैं" बनाम "हम") → ज़रूरतें और सीमाएँ → architecture (diagram) → 2–3 मुख्य फ़ैसले और विकल्प → मुश्किलें/incidents और हल → नतीजे (numbers) और सीख।

---

## 🔴 Problem it Solves
Candidates often:
- tell a **feature list** ("we built login, cart, payments") instead of engineering decisions
- claim team work as their own, or **understate their role**
- have **no numbers** (scale, latency, cost, business impact)
- get stuck on follow-ups because they **didn't own** the parts they described
- pick a project that's too small, or too confidential to explain
A prepared, structured story shows **senior-level thinking from real experience**, often weighted heavily for mid and senior roles, and it's also where a self-built or side project (Node/FastAPI + React Native + AWS) can shine if presented well.

## 🔴 यह क्यों बना? (Hindi)
उम्मीदवार अक्सर: engineering फ़ैसलों की जगह features की सूची ("login, cart, payments बनाए"); टीम का काम अपना बताना या अपनी भूमिका कम बताना; कोई numbers नहीं (पैमाना, latency, ख़र्च, business असर); follow-ups पर अटकना क्योंकि वो हिस्से ख़ुद नहीं बनाए; बहुत छोटा या बहुत गोपनीय project चुनना।
तैयार, ढाँचे वाली कहानी असली अनुभव से senior सोच दिखाती है — mid/senior roles में इसका वज़न ज़्यादा; और अपना side project (Node/FastAPI + React Native + AWS) भी अच्छे से पेश हो तो चमक सकता है।

---

## 🟢 How it Works — Step by Step

### Pick the right project (prepare 2–3)

```
✓ You owned meaningful parts (design decisions, not just tickets)
✓ Non-trivial: scale, reliability, performance, data consistency, real-time, migration, cost, or AI
✓ Has measurable outcomes (latency ↓, conversion ↑, cost ↓, incidents ↓, users served)
✓ You can explain it without violating confidentiality (abstract names/numbers if needed)
Variety: one backend/distributed, one frontend/mobile-heavy, one "incident/migration" or AI project
```

### The 8–10 minute structure (then follow-ups)

```
1. Context (1 min): "QuickBite (food delivery, 2M orders/month in 3 cities) needed live order tracking;
   support tickets 'where is my order' were 40% of all tickets."
2. Role (15 s): "I led backend design and built the tracking service & RN tracking screen; 2 teammates
   did the rider app changes."
3. Requirements & constraints (1 min): "Location freshness ≤ 10 s, 99.9% availability at dinner peak,
   low-end Android riders, 6-week deadline, team of 3, AWS Mumbai."
4. Architecture (2–3 min): draw it — rider app → location ingest (FastAPI) → Redis GEO + Kafka →
   tracking service → SSE to customer app/web; push for milestones; Postgres for order state.
5. Key decisions (2 min): "SSE vs WebSocket: one-way updates + HTTP infra → SSE.
   Redis for live positions vs Postgres: 60k writes/s at peak → in-memory.
   Interpolated marker on client to hide 5 s update gaps."
6. Challenges (1–2 min): "ALB idle timeout killed streams at 60 s → heartbeats + 300 s timeout.
   OEM battery killers stopped rider updates → foreground service + in-app OEM guide; gaps dropped 70%."
7. Results (30 s): "'Where is my order' tickets −35%, p95 freshness 6 s, cost ₹X/month."
8. Learnings (30 s): "I'd add replayable buffers for reconnects from day one and load-test streaming earlier."
```

### Prepare for follow-ups (typical probes)

```
Why X instead of Y? → have 1–2 alternatives + reason per major decision
How did you measure success? → metrics, dashboards, A/B or before/after, data source
What was the hardest bug/incident? → timeline, root cause, fix, prevention
How would it scale 10×? → bottleneck & evolution (sharding, partitioning, multi-region)
What would you do differently? → honest, specific improvements
What did others do vs you? → precise ownership boundaries
Security/privacy? cost? testing? rollout? on-call? → 1–2 sentences each
```

### Honesty rules

```
- Say "I" for your work, "we" for team work; never inflate
- If you don't know a detail ("I didn't own the billing part"), say so and explain the interface
- Keep numbers approximate but real ("about 300 orders/s at peak"); don't invent precision
- It's fine to present a personal/side project — be clear it's personal and what scale you tested
```

### For students / early-career / side projects

```
Pick a project you built end-to-end (e.g., Expo RN app + FastAPI + Postgres/pgvector + AWS), show:
- deliberate design (why this DB, why this auth), load tests (k6/Locust numbers), CI/CD, monitoring
- one real problem you debugged deeply (memory leak, slow query, streaming timeout)
- how you'd scale it (numbers from Playbook 03) — shows you can reason beyond your current scale
```

## 🟢 कैसे काम करता है? (Hindi)
1. 2–3 projects तैयार रखो: जिनमें आपके अपने design फ़ैसले हों, कुछ कठिन हो (पैमाना, भरोसा, performance, consistency, real-time, migration, ख़र्च, AI), नापने लायक नतीजे हों, और गोपनीयता तोड़े बिना समझा सको; एक backend, एक frontend/mobile, एक incident/migration या AI वाला।
2. 8–10 मिनट का ढाँचा: संदर्भ (1 मिनट — business समस्या और पैमाना) → भूमिका (15 सेकंड) → ज़रूरतें/सीमाएँ (1 मिनट) → architecture diagram (2–3 मिनट) → मुख्य फ़ैसले और विकल्प (2 मिनट) → मुश्किलें/incidents (1–2 मिनट) → नतीजे numbers के साथ (30 सेकंड) → सीख (30 सेकंड)।
3. Follow-ups की तैयारी: हर बड़े फ़ैसले के 1–2 विकल्प और कारण, सफलता कैसे नापी, सबसे कठिन bug/incident (समय-रेखा, मूल कारण, हल, रोकथाम), 10× पर क्या टूटेगा, क्या अलग करते, आपने क्या किया बनाम दूसरों ने।
4. ईमानदारी: अपने काम के लिए "मैंने", टीम के लिए "हमने"; जो नहीं जानते वो कहो और interface समझाओ; numbers मोटे पर सच्चे; side project हो तो साफ़ बताओ।
5. Students/शुरुआती: end-to-end बनाया project (Expo RN + FastAPI + Postgres/pgvector + AWS) — सोचे-समझे फ़ैसले, load test के numbers, CI/CD, monitoring, एक गहरा debug किया हुआ bug, और Playbook 03 के numbers से scale करने का तरीका।

---

## 🟡 Real World Example
Many companies run a dedicated "project deep dive" or "past experience" round (common at Amazon in leadership-principle-driven interviews, at Uber and Stripe, and at Indian product companies like Flipkart, Razorpay and Swiggy for senior roles). Interviewers drill into one project for 30–45 minutes. Candidates who bring a clear diagram, two or three well-reasoned trade-offs, an incident story and real metrics consistently score higher than those listing features.

## 🟡 Real Example Hindi में
कई कंपनियाँ अलग "project deep dive" या "past experience" round रखती हैं — Amazon (leadership principles वाले इंटरव्यू), Uber, Stripe, और senior roles के लिए Flipkart, Razorpay, Swiggy; 30–45 मिनट तक एक ही project की गहराई — साफ़ diagram, 2–3 सोचे-समझे trade-offs, एक incident की कहानी और असली numbers वाले उम्मीदवार features गिनाने वालों से हमेशा बेहतर करते हैं।

---

## 🟠 My Stack Example

### Fill-in worksheet (prepare one per project)
```
Project name / domain: ______________________   Timeframe: ________   Team size: ___
Context (problem, users, scale): ____________________________________________
My role & ownership (I vs we): _______________________________________________
Requirements & constraints (latency, availability, deadline, budget): __________
Architecture (sketch): clients → ______ → ______ → data stores ______ → async ______
Decision 1: chose ______ over ______ because ______ (trade-off: ______)
Decision 2: chose ______ over ______ because ______
Decision 3: chose ______ over ______ because ______
Hardest problem / incident: symptom ______ root cause ______ fix ______ prevention ______
Results (numbers): ______________________   How measured: __________________
What I'd change now: _______________________________________________________
10× scale plan: bottleneck ______ → solution ______
```

### Sample 60-second opener (stack: React Native + FastAPI + Postgres + Redis + AWS)
```
"I designed the offline-first delivery-proof feature for our logistics app. Riders in basements lost
uploads, causing ~8% disputed deliveries. I owned the mobile sync engine and the FastAPI upload service.
We stored proofs locally in SQLite with an outbox, uploaded photos via S3 multipart with resumable parts,
and confirmed deliveries idempotently. The key trade-off was local-first writes with eventual sync versus
blocking on network — we chose local-first plus server-side conflict rules (cancelled orders win).
Disputed deliveries dropped to ~2% and upload success rose to 99.3%. If I redid it, I'd add device-level
telemetry for sync failures from day one."
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you structure your answer to "Tell me about a system you designed"?**
A1: Give the context and scale, then your role, then requirements and constraints. Draw the architecture and walk through key flows, then explain two or three major decisions with the alternatives and trade-offs, describe a significant challenge or incident and how you resolved it, share measurable results, and close with what you learned or would change. Keep the first pass to about ten minutes and invite deeper questions.

**Q2: How do you handle questions about parts you didn't build?**
A2: Be honest about ownership boundaries: say who owned it, describe the interface and contract between your component and theirs, explain how it affected your design, and share what you understand about how it works without overstating. Interviewers respect precision and honesty far more than inflated claims, which collapse under follow-ups.

**Q3: What if your project wasn't at large scale?**
A3: Focus on the quality of your decisions, testing and measurement at the scale you had (load tests, profiling, cost), the hardest problem you solved deeply, and how the design would evolve at 10× or 100× using estimates. Clear reasoning about scaling paths shows the same competence interviewers look for in large-scale experience.

**Q4: How do you show impact?**
A4: Tie technical work to user or business outcomes with numbers: latency reduced (p95 1.8 s to 600 ms), error rates, uptime, cost savings (₹/month), support tickets reduced, conversion or retention changes, and developer productivity (deploy time). Explain how you measured (dashboards, A/B tests, before and after) and any caveats.

**Q5: What makes a "lessons learned" answer strong?**
A5: Specific, technical and honest reflections that show growth: what assumption was wrong, what you'd design differently (e.g., idempotency or observability from day one, a different data model), and how you've applied that lesson since. Avoid generic answers like "better communication" without concrete examples.

---

## 🔷 Trade-offs
✅ Rehearsed structure: confident & complete — ❌ don't sound memorized; adapt depth to the interviewer's interests.
✅ Bold claims impress briefly — ❌ follow-ups expose them; precise honesty wins.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Project deep dive | Detailed discussion of past work | पुराने काम की गहराई |
| Ownership | What you were responsible for | आपकी ज़िम्मेदारी |
| Trade-off | Choice with pros and cons | फ़ायदे-नुक़सान वाला चुनाव |
| Impact | Measurable outcome | नापने लायक असर |
| Incident | Production problem/outage | production की समस्या |
| Retrospective | Reflection on what to improve | पीछे देखकर सीख |

---

## ⚡ 3-Line Summary
**English:**
1. Prepare 2–3 projects you truly owned, with a diagram, 2–3 key trade-offs, one incident story and real metrics.
2. Present in ~10 minutes: context → role → requirements → architecture → decisions → challenges → results → learnings.
3. Expect deep follow-ups: be precise about ownership, explain alternatives and measurement, and show how it would scale 10×.

**Hindi:**
1. 2–3 ऐसे projects जो सच में आपके हों — diagram, 2–3 trade-offs, एक incident, असली numbers।
2. ~10 मिनट: संदर्भ → भूमिका → ज़रूरतें → architecture → फ़ैसले → मुश्किलें → नतीजे → सीख।
3. गहरे follow-ups के लिए तैयार: ईमानदार मालिकाना, विकल्प, नापने का तरीका, 10× का plan।

---

## ➡️ Next Topic Suggestion
**🎉 You've completed the entire System Design guide!** Next: follow the 12-week roadmap in [README.md](../README.md). Revise with Playbook sheets 05–09, self-test with the Top 100 (10), and run weekly 45-minute mock designs using Playbook 01/02 with problems from `06-Backend-Design-Problems/` and `09-FullStack-Design-Problems/`.
