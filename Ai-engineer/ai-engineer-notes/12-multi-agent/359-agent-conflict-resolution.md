---

# 359. Agent Conflict Resolution
# हिंदी में: Agents के बीच Conflict Resolution

---

## 🔵 Simple Definition (English)
Agent conflict resolution is the rule set for what happens when two or more agents give **different answers** or want to do **incompatible actions**. Common strategies: majority vote, confidence weighting, priority/authority, a judge agent, deterministic validation, and human escalation.

## 🔵 सरल परिभाषा (Hindi)
Agent conflict resolution वे नियम हैं कि जब दो या ज़्यादा agents **अलग-अलग answer** दें या **आपस में टकराने वाले actions** चाहें तो क्या हो। आम तरीके: majority vote, confidence weighting, priority/authority, judge agent, deterministic validation और human escalation।

---

## 🔴 Problem it Solves
Multi-agent systems disagree all the time: one agent says HS 8517, another says 8518. Without a policy the system picks randomly (last write wins), loops forever in debate, or returns two answers. Conflicts also happen on resources: two agents editing the same record. We need a predictable, auditable way to settle them.

## 🔴 यह क्यों बना? (Hindi)
Multi-agent systems में असहमति आम है: एक agent HS 8517 कहता है, दूसरा 8518। नीति न हो तो system random चुनता है (आखिरी write जीतता है), debate में अटक जाता है, या दो answers लौटा देता है। Resources पर भी टकराव होता है: दो agents एक ही record बदलते हैं। इन्हें सुलझाने का अनुमानित और audit-योग्य तरीका चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Detect: compare agent outputs (same field, different values)
Step 2 → Classify the conflict: factual / preference / resource / policy
Step 3 → Try deterministic rules first (validator, tariff table, authority)
Step 4 → Else aggregate: majority vote or confidence-weighted vote
Step 5 → Close call? -> judge agent reads both reasonings and decides
Step 6 → Still unsure (low margin) -> escalate to a human
Step 7 → Log the conflict, the method and the final decision
Step 8 → Feed outcomes back as test cases and prompt improvements
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → पहचानो: agent outputs की तुलना (एक field, अलग values)
Step 2 → Conflict का प्रकार: factual / preference / resource / policy
Step 3 → पहले deterministic rules (validator, tariff table, authority)
Step 4 → वरना aggregate: majority vote या confidence-weighted vote
Step 5 → अंतर कम हो -> judge agent दोनों reasoning पढ़कर तय करे
Step 6 → फिर भी अनिश्चित (कम margin) -> human को भेजो
Step 7 → Conflict, तरीका और अंतिम फैसला log करो
Step 8 → नतीजों को test cases और prompt सुधार में वापस दो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Three classifier agents (different prompts/models) return: A = 8518.30 (0.90), B = 8518.30 (0.80), C = 8517.62 (0.85). Majority says 8518.30. A deterministic validator checks both codes against chapter notes and confirms 8518.30 fits "headphones". Final: 8518.30, with the dissent logged. If the votes were 1-1-1 the case goes to a human officer.

**Zomato-style**: Offers agent wants to apply a 30 percent coupon, finance agent caps discounts at 20 percent. Policy priority says finance rules win.

## 🟡 Real Example Hindi mein
**Tariff System**: तीन classifier agents (अलग prompts/models) लौटाते हैं: A = 8518.30 (0.90), B = 8518.30 (0.80), C = 8517.62 (0.85)। Majority 8518.30 कहती है। Deterministic validator दोनों codes को chapter notes से जाँचता है और पुष्टि करता है कि 8518.30 "headphones" के लिए सही है। अंतिम: 8518.30, असहमति log में। अगर votes 1-1-1 होते तो केस human officer के पास जाता।

**Zomato-style**: Offers agent 30 प्रतिशत coupon लगाना चाहता है, finance agent discount 20 प्रतिशत तक सीमित रखता है। Policy priority में finance के नियम जीतते हैं।

---

## 💻 Code Example — Basic
```python
# Majority vote + confidence tie-break + escalation (runs offline)
from collections import defaultdict  # for grouping votes
from typing import NamedTuple  # simple typed record

class Vote(NamedTuple):
    agent: str         # who voted
    code: str          # proposed HS code
    confidence: float  # 0..1

def resolve(votes: list[Vote], min_margin: float = 0.3) -> tuple[str | None, str]:
    """Return (decision, method). decision None means escalate to a human."""
    if not votes:
        return None, "no_votes"  # nothing to decide
    weight: dict[str, float] = defaultdict(float)  # code -> total confidence
    count: dict[str, int] = defaultdict(int)       # code -> number of votes
    for v in votes:
        weight[v.code] += v.confidence  # confidence-weighted score
        count[v.code] += 1
    ranked = sorted(weight.items(), key=lambda kv: kv[1], reverse=True)  # best first
    top_code, top_w = ranked[0]
    if len(ranked) == 1:
        return top_code, "unanimous"  # everyone agrees
    margin = (top_w - ranked[1][1]) / sum(weight.values())  # lead over runner-up
    if margin >= min_margin:
        return top_code, "weighted_majority"
    return None, "escalate_low_margin"  # too close to call

if __name__ == "__main__":
    votes = [Vote("A", "8518.30", 0.90), Vote("B", "8518.30", 0.80), Vote("C", "8517.62", 0.85)]
    print(resolve(votes))  # ('8518.30', 'weighted_majority')
    tie = [Vote("A", "8518.30", 0.8), Vote("B", "8517.62", 0.8)]
    print(resolve(tie))    # (None, 'escalate_low_margin')
```

## 💻 Code Example — Advanced
```python
# Async resolution: deterministic validator -> vote -> judge -> human
import asyncio  # async runtime
from dataclasses import dataclass  # result record

VALID_CODES = {"8518.30", "8517.62"}  # official tariff table (stub)

@dataclass
class Decision:
    code: str | None      # chosen code, None if escalated
    method: str           # how we decided
    dissent: list[str]    # agents that disagreed (audit)

async def judge_llm(options: list[str], reasons: dict[str, str]) -> str:
    await asyncio.sleep(0)  # real call: cheap strong model reads both reasonings
    return options[0]  # stub choice

async def resolve(proposals: dict[str, tuple[str, float, str]]) -> Decision:
    """proposals: agent -> (code, confidence, reasoning)."""
    try:
        # 1) deterministic filter: drop codes not in the tariff table
        valid = {a: p for a, p in proposals.items() if p[0] in VALID_CODES}
        if not valid:
            return Decision(None, "no_valid_code", list(proposals))
        codes = {p[0] for p in valid.values()}
        if len(codes) == 1:  # all remaining agree
            code = codes.pop()
            return Decision(code, "validated_consensus", [a for a, p in proposals.items() if p[0] != code])
        # 2) weighted vote
        score: dict[str, float] = {}
        for code, conf, _ in valid.values():
            score[code] = score.get(code, 0.0) + conf
        ranked = sorted(score.items(), key=lambda kv: kv[1], reverse=True)
        if ranked[0][1] - ranked[1][1] > 0.5:  # clear winner
            return Decision(ranked[0][0], "weighted_vote", [a for a, p in valid.items() if p[0] != ranked[0][0]])
        # 3) judge agent for close calls
        reasons = {c: next(p[2] for p in valid.values() if p[0] == c) for c in score}
        pick = await judge_llm(list(score), reasons)
        return Decision(pick, "judge", [a for a, p in valid.items() if p[0] != pick])
    except Exception as exc:  # fail safe: escalate
        return Decision(None, f"error:{exc}", [])

if __name__ == "__main__":
    props = {"A": ("8518.30", 0.9, "headphones"), "B": ("8517.62", 0.85, "telecom"), "C": ("9999.99", 0.99, "hallucinated")}
    print(asyncio.run(resolve(props)))  # C removed by validator, then judge decides
```

---

## 🟠 FastAPI Integration
Expose the decision with its method and dissent so reviewers see why. Add a human-queue endpoint for escalations.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()
REVIEW_QUEUE: list[dict] = []  # use a real queue/db in production

class Proposal(BaseModel):
    code: str         # proposed code
    confidence: float # 0..1
    reasoning: str    # explanation

class ResolveIn(BaseModel):
    shipment_id: str                  # case id
    proposals: dict[str, Proposal]    # agent -> proposal

@app.post("/resolve")
async def resolve_endpoint(body: ResolveIn) -> dict:
    props = {a: (p.code, p.confidence, p.reasoning) for a, p in body.proposals.items()}
    d = await resolve(props)  # run the strategy
    if d.code is None:  # nobody trusted
        REVIEW_QUEUE.append({"shipment_id": body.shipment_id, "why": d.method})  # human queue
    return {"code": d.code, "method": d.method, "dissent": d.dissent, "needs_human": d.code is None}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from typing import Annotated, TypedDict  # state
import operator  # append reducer
from langgraph.graph import StateGraph, START, END  # graph

class CState(TypedDict):
    description: str
    proposals: Annotated[list[dict], operator.add]  # each classifier appends one proposal
    decision: str

def make_classifier(name: str):
    def node(s: CState) -> dict:
        # real code: chain.invoke(...) with a different prompt or model per agent
        return {"proposals": [{"agent": name, "code": "8518.30", "conf": 0.8}]}
    return node

def arbiter(s: CState) -> dict:
    best = max(s["proposals"], key=lambda p: p["conf"])  # simple rule; replace with vote/judge
    return {"decision": best["code"]}

g = StateGraph(CState)
for n in ("A", "B", "C"):
    g.add_node(n, make_classifier(n))
    g.add_edge(START, n)          # fan-out: all three run in parallel
    g.add_edge(n, "arbiter")      # fan-in: arbiter waits for all
g.add_node("arbiter", arbiter)
g.add_edge("arbiter", END)
graph = g.compile()
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Letting agents debate until they agree
✅ Correct: cap rounds, then vote, judge or escalate.

```python
# Wrong
while a.answer != b.answer: a.rebut(b); b.rebut(a)
# Right
for _ in range(2):   # at most 2 debate rounds
    ...
decision = resolve(votes)
```

❌ Mistake 2: Using LLM confidence as the only signal
✅ Correct: combine with deterministic validators and calibrated thresholds.

```python
# Wrong
winner = max(votes, key=lambda v: v.confidence)
# Right
valid = [v for v in votes if v.code in VALID_CODES]
winner = weighted_vote(valid)
```

---

## 🧠 Tricky Interview Question
**Q**: "Three agents built on the same model all agree, yet the answer is wrong. Is majority voting enough?"

**Answer**: No. Same-model agents make correlated errors, so agreement is weak evidence. Increase diversity (different models, prompts, retrieval sources), add independent verification (rules, database lookups, tools), and calibrate against labelled data. Voting reduces random noise but not systematic bias.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Why do agents conflict?
A1: Different prompts, models, data and goals produce different outputs or incompatible actions.

Q2: [Easy] Name two resolution strategies.
A2: Majority vote and a judge agent. Others: authority priority, deterministic validators, human escalation.

Q3: [Medium] When is a judge agent better than voting?
A3: When there are only two agents, votes are close, or reasoning quality matters more than counts. The judge reads the arguments.

Q4: [Medium] What is a deterministic validator's role?
A4: It rejects impossible answers (unknown code, rule violations) before voting, so hallucinations cannot win.

Q5: [Hard] How do you prevent two agents from editing the same record?
A5: Field ownership, optimistic locking with version numbers, a single writer agent, or a queue that serialises writes. Reject stale writes and replan.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multiple agents can produce different answers
- Errors are expensive and need audit
- Agents share writable resources

❌ Avoid when:
- A single agent owns the decision
- Extra voting agents multiply cost with no accuracy gain

---

## 📊 Visual Diagram
```
 Agent A ----\                           +--> validator rejects invalid
 Agent B -----+--> [Conflict detected] --+--> vote / weighted vote
 Agent C ----/                           +--> judge agent (close call)
                                         +--> human review (low margin)
                                                  |
                                     Decision + method + dissent -> audit log
```

---

## 💰 Cost Impact
- N voting agents multiply generation cost by N (3 agents = 3x).
- Judge adds one more call (about 800 tokens).
- Optimise: run the second and third agents only when the first has low confidence; use a cheap model for voters; deterministic validator first (free); judge only for close calls; cache resolved cases.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Conflict | Agents disagree | Agents में असहमति |
| Majority vote | Most common answer wins | सबसे ज़्यादा वोट वाला जीतता है |
| Judge agent | Agent that decides between options | विकल्पों में फैसला करने वाला agent |
| Escalation | Send to a human | Human को भेजना |
| Margin | Lead of winner over runner-up | विजेता की बढ़त |
| Dissent | Minority opinion kept in the log | अल्पमत की राय |

---

## ⚡ 3-Line Summary
English: When agents disagree, use deterministic rules first, then voting or a judge, then humans. Log the method and dissent. Same-model agents share errors, so add diversity and independent checks.
Hindi: Agents असहमत हों तो पहले deterministic rules, फिर voting या judge, फिर human। तरीका और dissent log करो। एक ही model के agents की गलतियाँ मिलती-जुलती होती हैं, इसलिए विविधता और स्वतंत्र जाँच जोड़ो।

---

## ➡️ Next Topic
**360. AutoGen Basics** — a popular framework where agents resolve tasks by conversing.
