---

# 186. Router Pattern — Deep
# हिंदी में: Router Pattern (सही Agent तक रास्ता दिखाना) — विस्तार से
# Framework: All
# Already Known: No

> Verified offline with fake router and specialists (no API key). Python 3.13, fastapi 0.163.1, httpx 0.28.1, pydantic 2.14.3. Real LLM calls: not run, needs an LLM API key. Token figures are approximate formulas only.

---

## 🔵 Simple Definition (2-3 lines)
A router looks at an incoming request and sends it to exactly one specialist agent, tool, model or workflow. The router does classification, not the real work. Think of a reception desk that points you to the right department.

## 🔵 सरल परिभाषा (Hindi)
Router आने वाले request को देखकर उसे ठीक एक specialist agent, tool, model या workflow तक भेजता है। Router सिर्फ़ classification करता है, असली काम नहीं। जैसे reception desk जो आपको सही विभाग का रास्ता बताता है।

---

## 🔴 Problem it Solves
One giant agent with 40 tools and a long prompt is slow, expensive and confused. Tool selection accuracy falls as tool count grows. Easy questions also waste a large model. A router lets each specialist have a small prompt and few tools, and lets simple requests go to cheap models.

## 🔴 यह क्यों बना? (Hindi)
40 tools और लंबे prompt वाला एक बड़ा agent धीमा, महँगा और भ्रमित होता है; tools बढ़ने पर tool चुनने की सटीकता घटती है। आसान सवालों पर भी बड़ा model खर्च होता है। Router से हर specialist का prompt छोटा और tools कम रहते हैं, और सरल requests सस्ते model पर जाते हैं।

---

## 🟢 How it Works

```
Step 1 → Request arrives
Step 2 → Router classifies intent -> {route, confidence}
         (rules / keywords, embeddings, or a small LLM with a strict enum)
Step 3 → confidence >= threshold → call the chosen specialist
Step 4 → confidence < threshold  → fallback (general agent or ask a clarifying question)
Step 5 → Specialist answers; response returned (router is not in the answer)
Step 6 → Log (request, route, confidence) -> later find misroutes and retrain rules
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Request आता है
Step 2 → Router intent classify करता है -> {route, confidence}
         (rules / keywords, embeddings, या छोटा LLM जिसे strict enum मिले)
Step 3 → confidence >= threshold → चुने गए specialist को बुलाओ
Step 4 → confidence < threshold  → fallback (general agent या स्पष्टीकरण का सवाल)
Step 5 → Specialist जवाब देता है; router जवाब में शामिल नहीं होता
Step 6 → (request, route, confidence) log करो -> गलत routes ढूँढकर सुधारो
```

---

## 🟡 Real World Example
**Tariff Agent platform**: "What is the HS code for a laptop?" goes to the classification agent. "What is the duty on 8471.30 into India?" goes to the duty-calculator agent. "Is this product restricted?" goes to the compliance agent. "hello" goes to a cheap small-talk model. Unclear queries get a clarifying question.

## 🟡 Real Example Hindi mein
**Tariff Agent platform**: "Laptop का HS code क्या है?" classification agent को जाता है। "8471.30 पर India में duty कितनी?" duty-calculator agent को। "क्या यह product restricted है?" compliance agent को। "hello" सस्ते small-talk model को। अस्पष्ट सवाल पर स्पष्टीकरण पूछा जाता है।

---

## 💻 Code Example — Basic
```python
# Basic keyword router with a safe fallback. Runs offline.
from typing import Callable                       # for the handler type


def classify_agent(q: str) -> str:                # specialist 1 (fake)
    return f"[classify] HS code lookup for: {q}"


def duty_agent(q: str) -> str:                    # specialist 2 (fake)
    return f"[duty] duty calculation for: {q}"


def general_agent(q: str) -> str:                 # fallback specialist
    return f"[general] could you rephrase? ({q})"


ROUTES: dict[str, Callable[[str], str]] = {       # route name -> handler
    "classify": classify_agent,
    "duty": duty_agent,
}


def route(q: str) -> str:                         # the router itself: returns a route name
    text = q.lower()                              # normalize
    if "hs code" in text or "classify" in text:   # rule 1
        return "classify"
    if "duty" in text or "tariff" in text:        # rule 2
        return "duty"
    return "general"                              # default route


def handle(q: str) -> str:
    name = route(q)                               # step 1: decide
    handler = ROUTES.get(name, general_agent)     # step 2: lookup, never KeyError
    return handler(q)                             # step 3: run specialist


if __name__ == "__main__":
    for q in ["HS code for laptop", "duty on 8471.30", "hello there"]:
        print(handle(q))                          # each goes to a different agent
```

## 💻 Code Example — Advanced
```python
# Advanced: async LLM-style router with strict enum output, confidence threshold,
# fallback, per-route timeout, FastAPI endpoint, approximate tokens. Offline.
import asyncio                                    # async + timeout
import json                                       # fake router returns JSON text
from enum import Enum                             # closed set of routes
from fastapi import FastAPI                       # web framework
from fastapi.testclient import TestClient         # offline client
from pydantic import BaseModel, Field, ValidationError  # pydantic v2


class Route(str, Enum):                           # router can ONLY return these
    classify = "classify"
    duty = "duty"
    general = "general"


class Decision(BaseModel):                        # strict router output
    route: Route
    confidence: float = Field(ge=0, le=1)


class Req(BaseModel):
    query: str


def est(t: str) -> int:                           # rough tokens (~4 chars/token)
    return max(1, len(t) // 4)


async def fake_router_llm(q: str) -> str:         # stands in for a small, cheap LLM
    await asyncio.sleep(0)
    if "hs" in q.lower():
        return json.dumps({"route": "classify", "confidence": 0.93})
    if "duty" in q.lower():
        return json.dumps({"route": "duty", "confidence": 0.88})
    return json.dumps({"route": "classify", "confidence": 0.30})  # unsure


async def specialist(route: Route, q: str) -> str:  # fake async specialists
    await asyncio.sleep(0)
    return f"[{route.value}] answer to: {q}"


async def decide(q: str) -> Decision:
    try:
        raw = await asyncio.wait_for(fake_router_llm(q), 2.0)  # bounded router latency
        return Decision.model_validate_json(raw)   # reject invalid enum values
    except (asyncio.TimeoutError, ValidationError):  # router failure -> safe default
        return Decision(route=Route.general, confidence=0.0)


app = FastAPI()


@app.post("/ask")
async def ask(req: Req) -> dict:
    d = await decide(req.query)                    # step 1: route
    chosen = d.route if d.confidence >= 0.6 else Route.general  # confidence gate
    try:
        answer = await asyncio.wait_for(specialist(chosen, req.query), 10.0)
    except asyncio.TimeoutError:                   # specialist too slow
        answer = "Service busy, please retry."
    return {"route": chosen.value, "confidence": d.confidence, "answer": answer,
            "approx_router_tokens": est(req.query) + 8}  # small: routing is cheap


if __name__ == "__main__":
    c = TestClient(app)
    for q in ["HS code for laptop", "duty on 8471.30", "blah blah"]:
        print(c.post("/ask", json={"query": q}).json())
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Routing mechanism | Conditional edges from a router node | Your code picks which agent/crew runs (or a manager) | Triage agent with handoffs, or your code | Selector-style team or custom routing code |
| Router type | Function or LLM node returning a key | Function or LLM | LLM triage or function | LLM selector or function |
| Fallback | Default branch in mapping | Your code | Your code / default agent | Default speaker |
| Shared state | Typed state | Task context | Run context | Message history |
| Best for | Explicit, testable routing | Role teams | Triage and handoffs | Chat-style teams |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Free-text router output ("I think billing").
✅ Correct: Constrain to an enum/schema and validate it.

❌ Mistake 2: No fallback when confidence is low or the router fails.
✅ Correct: Route to a general agent or ask a clarifying question.

❌ Mistake 3: Using a big, slow model for routing.
✅ Correct: Use rules first, then embeddings, then a small LLM; routing should cost a tiny fraction of the answer.

❌ Mistake 4: Never reviewing misroutes.
✅ Correct: Log decisions, sample them, build a routing eval set.

---

## 🧠 Tricky Interview Question
Users often send multi-intent messages: "What is the HS code for a laptop and what duty will I pay in India?" Your router picks one route and half the question is lost. How do you fix it?

Answer: Detect multi-intent. Options: (1) router returns a list of routes with sub-queries and you run specialists in parallel then merge (this becomes scatter-gather, note 191); (2) a planner decomposes the query first; (3) route to a supervisor agent (note 187) that can call both specialists; (4) ask the user to split the question. Keep the router single-label for simple traffic and add the multi-label path behind a classifier flag so cost stays low. Add multi-intent cases to the routing eval set.

---

## ⚫ Interview Questions + Answers

Q1: (Easy) What does a router do?
A1: It picks which specialist handles a request, and only that. It does not generate the final answer.

Q2: (Medium) Rule-based vs embedding vs LLM router?
A2: Rules are fastest and free but brittle; embeddings handle paraphrase cheaply but need examples; an LLM handles nuance but costs latency and money. Cascade them: rules, then embeddings, then LLM for the uncertain remainder.

Q3: (Hard) How do you evaluate a router?
A3: Build a labelled set of queries with correct routes, measure accuracy, per-route precision and recall, and the cost of each type of misroute (some are worse than others). Re-run on every prompt or model change.

Q4: (Hard) Router vs supervisor?
A4: A router makes one decision and exits. A supervisor stays in the loop, can call several workers, and decides after each result. Router is cheaper and simpler; supervisor is more flexible.

Q5: (System Design) Design routing for 20 specialist agents with changing tools.
A5: Registry of agents with descriptions and example queries; embed descriptions for top-k retrieval; small LLM picks among top-k with enum output; confidence threshold plus general fallback; log all decisions; shadow-test new routing prompts against recorded traffic before rollout.

---

## 💰 Cost Impact
- Router tokens (approximate): `prompt + query + short JSON`, usually tens to a few hundred tokens with a small model. Rule routers cost zero tokens.
- Savings: simple requests go to cheap models, and each specialist has a short prompt, so total tokens per request usually fall compared with one giant agent (measure on your own traffic).
- Tips: rules first, cache routing decisions by normalized query, small model for routing, keep the route list short.
- Pricing: approximate, from public pricing at time of writing, verify.

---

## 🔷 When to Use
✅ Use when:
- Distinct intents map to distinct specialists or tools
- You want to cut cost by sending easy requests to cheap models
- One agent has too many tools

❌ Avoid when:
- Requests are mostly multi-intent (use planner or supervisor)
- Only one or two intents exist (plain if/else is enough)

---

## 📊 Visual Diagram
```
                          +--> Classification Agent
 request --> [ Router ] --+--> Duty Agent
              (enum +     +--> Compliance Agent
            confidence)   +--> General / clarify (fallback, low confidence)
                 |
                 +--> log (request, route, confidence)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Router | Picks one specialist | मार्ग-निर्धारक |
| Intent | What the user wants | उद्देश्य |
| Confidence | Router's certainty | विश्वास स्तर |
| Fallback | Safe default route | वैकल्पिक मार्ग |
| Misroute | Wrong specialist chosen | गलत रूटिंग |
| Triage | First-level sorting | प्राथमिक छँटाई |

---

## ⚡ 3-Line Summary
English: A router picks one specialist for each request and then gets out of the way.
Use a strict enum, a confidence threshold and a fallback.
Keep routing cheap with rules and small models, and evaluate it on labelled queries.

Hindi: Router हर request के लिए एक specialist चुनता है और फिर हट जाता है।
Strict enum, confidence threshold और fallback का इस्तेमाल करो।
Rules और छोटे models से routing सस्ती रखो और labelled queries पर उसे evaluate करो।

---

## ➡️ Next Topic
187. Supervisor Pattern (Deep): when one routing decision is not enough, a supervisor keeps control and delegates repeatedly.

---
