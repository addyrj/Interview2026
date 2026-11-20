---

# 185. Ensemble Pattern
# हिंदी में: Ensemble Pattern (कई Agents की राय मिलाना)
# Framework: All
# Already Known: No

> Verified offline with fake agents (no API key). Python 3.13, fastapi 0.163.1, httpx 0.28.1, pydantic 2.14.3. Real LLM calls: not run, needs an LLM API key. Token figures are approximate formulas only.

---

## 🔵 Simple Definition (2-3 lines)
The Ensemble pattern asks several independent agents (different prompts, models or temperatures) the same question and then combines their answers, usually by majority vote or a weighted merge. Like asking three customs experts and going with the consensus.

## 🔵 सरल परिभाषा (Hindi)
Ensemble pattern में कई स्वतंत्र agents (अलग prompts, models या temperature) से एक ही सवाल पूछा जाता है और उनके जवाबों को majority vote या weighted merge से जोड़ा जाता है। जैसे तीन customs विशेषज्ञों से पूछकर बहुमत की राय लेना।

---

## 🔴 Problem it Solves
One LLM answer is a single random sample. It can be wrong in a way that looks confident. For high-stakes classification you want lower variance and a confidence signal. Disagreement between agents is itself useful: it tells you when to send the case to a human.

## 🔴 यह क्यों बना? (Hindi)
एक LLM का जवाब सिर्फ़ एक random नमूना है; वह गलत होकर भी आत्मविश्वासी दिख सकता है। High-stakes classification में variance कम और confidence का संकेत चाहिए। Agents में असहमति खुद एक उपयोगी संकेत है: वह बताती है कि केस इंसान को भेजना है।

---

## 🟢 How it Works

```
Step 1 → Send the same task to N agents (diverse: different model/prompt/temp)
Step 2 → Run them in parallel (asyncio.gather) with a timeout each
Step 3 → Collect answers; drop failed or invalid ones
Step 4 → Aggregate: majority vote / weighted vote / merge / judge model
Step 5 → Compute agreement = winner_votes / valid_votes
Step 6 → agreement >= threshold → return answer; else → escalate to human or judge
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → वही task N agents को भेजो (विविधता: अलग model/prompt/temperature)
Step 2 → उन्हें parallel चलाओ (asyncio.gather) और हर एक पर timeout लगाओ
Step 3 → जवाब इकट्ठा करो; fail या invalid जवाब हटाओ
Step 4 → Aggregate करो: majority vote / weighted vote / merge / judge model
Step 5 → agreement = winner_votes / valid_votes निकालो
Step 6 → agreement >= threshold तो जवाब लौटाओ; वरना इंसान या judge को भेजो
```

---

## 🟡 Real World Example
**Tariff Agent**: Three classifiers propose HS codes for "wireless earbuds": 8518.30, 8518.30, 8517.62. Majority vote returns 8518.30 with agreement 2/3 = 0.67. If the threshold is 0.75, the case is flagged for human review. Other examples: Code Agent (three patches, choose the one that passes tests), Customer Support (three drafts, judge picks the best tone).

## 🟡 Real Example Hindi mein
**Tariff Agent**: "wireless earbuds" के लिए तीन classifiers HS codes सुझाते हैं: 8518.30, 8518.30, 8517.62। Majority vote 8518.30 देता है, agreement 2/3 = 0.67। Threshold 0.75 हो तो केस human review के लिए flag होता है। अन्य उदाहरण: Code Agent (तीन patches, जो tests पास करे वह चुनो), Customer Support (तीन drafts, judge सबसे अच्छा tone चुने)।

---

## 💻 Code Example — Basic
```python
# Basic ensemble: three fake classifiers vote; majority wins. Runs offline.
from collections import Counter                   # counts votes


def agent_a(product: str) -> str:                 # fake agent A (stands in for an LLM)
    return "8518.30"


def agent_b(product: str) -> str:                 # fake agent B
    return "8518.30"


def agent_c(product: str) -> str:                 # fake agent C disagrees
    return "8517.62"


def ensemble(product: str, threshold: float = 0.75) -> dict[str, object]:
    agents = [agent_a, agent_b, agent_c]          # the panel
    votes = [a(product) for a in agents]          # collect each answer
    winner, count = Counter(votes).most_common(1)[0]  # most frequent answer
    agreement = count / len(votes)                # fraction that agreed
    return {"answer": winner, "agreement": round(agreement, 2),
            "needs_review": agreement < threshold}  # low agreement -> human


if __name__ == "__main__":
    print(ensemble("wireless earbuds"))           # agreement 0.67 -> needs_review True
```

## 💻 Code Example — Advanced
```python
# Advanced: async parallel ensemble with per-agent timeout, error isolation,
# weighted vote, FastAPI endpoint, and approximate token accounting. Offline.
import asyncio                                    # gather + wait_for
from collections import defaultdict               # weighted tally
from fastapi import FastAPI                       # web framework
from fastapi.testclient import TestClient         # offline client
from pydantic import BaseModel                    # request model


class Req(BaseModel):
    product: str


def est(text: str) -> int:                        # rough tokens (~4 chars/token)
    return max(1, len(text) // 4)


async def make_agent(name: str, answer: str, delay: float = 0.0, fail: bool = False):
    async def run(product: str) -> str:           # fake async LLM call
        await asyncio.sleep(delay)                # simulate latency
        if fail:                                  # simulate provider outage
            raise RuntimeError(f"{name} failed")
        return answer
    return name, run


async def call_safe(name: str, fn, product: str, timeout: float):
    try:
        return name, await asyncio.wait_for(fn(product), timeout)  # bounded call
    except Exception as exc:                      # one failure must not kill the panel
        return name, exc                          # return exception as a value


async def run_ensemble(product: str, threshold: float = 0.6) -> dict:
    weights = {"gpt-like": 1.0, "claude-like": 1.0, "small": 0.5}  # trust per agent
    panel = [await make_agent("gpt-like", "8518.30"),
             await make_agent("claude-like", "8518.30", delay=0.01),
             await make_agent("small", "8517.62", fail=True)]      # this one fails
    results = await asyncio.gather(*(call_safe(n, f, product, 1.0) for n, f in panel))
    tally: dict[str, float] = defaultdict(float)  # answer -> total weight
    errors: list[str] = []
    tokens = 0
    for name, res in results:
        if isinstance(res, Exception):            # skip failed agents
            errors.append(name)
            continue
        tally[res] += weights[name]               # weighted vote
        tokens += est(product) + est(res)         # approximate per-agent tokens
    if not tally:                                 # everyone failed
        return {"answer": None, "needs_review": True, "errors": errors}
    winner = max(tally, key=lambda k: tally[k])   # highest weight wins
    agreement = tally[winner] / sum(tally.values())
    return {"answer": winner, "agreement": round(agreement, 2),
            "needs_review": agreement < threshold, "errors": errors,
            "approx_tokens": tokens}


app = FastAPI()


@app.post("/classify")
async def classify(req: Req) -> dict:
    return await run_ensemble(req.product)


if __name__ == "__main__":
    print(TestClient(app).post("/classify", json={"product": "earbuds"}).json())
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Parallel agents | Several nodes from one edge, merged by a reducer | Multiple agents/tasks, own aggregation code | `asyncio.gather` over several runs | Parallel runs or a team with a selector |
| Aggregation | Aggregator node over state | Final aggregator agent/task | Your Python code | Aggregator agent or your code |
| Different models per agent | Yes, per node | Yes, per agent | Yes, per agent | Yes, per agent |
| Failure isolation | Per-node handling | Per-task handling | try/except per run | try/except per agent |
| Fit | Explicit fan-out/fan-in | Panel of role agents | Lightweight voting | Debate-style panels |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Three copies of the same model with the same prompt and temperature 0.
✅ Correct: Make members diverse (different models, prompts, retrieval context); identical members give identical errors.

❌ Mistake 2: Counting free-text answers as votes ("8518.30" vs "HS 8518.30").
✅ Correct: Normalize to a strict schema first, then vote.

❌ Mistake 3: One failed agent crashes the whole call.
✅ Correct: Isolate failures, vote among valid answers, and require a minimum quorum.

❌ Mistake 4: Ignoring the agreement score.
✅ Correct: Use low agreement to escalate; it is the most useful output.

---

## 🧠 Tricky Interview Question
Your 5-model ensemble is 3x the cost of one model but accuracy rose only 1 point. Why, and what now?

Answer: Errors are correlated: the models share training data and similar failure modes, so they are wrong on the same items. Ensembles help only with independent errors. Check pairwise error correlation on an eval set. Fixes: add diversity (retrieval-grounded agent, rule-based classifier, different prompt framings), drop redundant members, and use the ensemble selectively: run a single cheap model first and invoke the panel only on low-confidence items. Measure marginal accuracy per extra member and stop at the knee.

---

## ⚫ Interview Questions + Answers

Q1: (Easy) What is an ensemble of agents?
A1: Several agents answer the same task independently and their outputs are combined, usually by voting.

Q2: (Medium) Majority vote vs weighted vote vs judge?
A2: Majority is simple but treats all equal. Weighted uses measured accuracy per member. A judge model reads all answers and reasons, but adds cost and its own bias.

Q3: (Hard) Why use an odd number of members?
A3: To avoid ties in binary or small-label votes; with more labels you still need a tie-break rule (weights or judge).

Q4: (Hard) How do you evaluate whether the ensemble is worth it?
A4: On a labelled set compare accuracy, cost and latency of single model vs ensemble, measure error correlation, and compute cost per correct answer.

Q5: (System Design) Design an ensemble classifier for 100 requests per second.
A5: Cheap model first; if its confidence is below a threshold, fan out to a panel in parallel with per-call timeouts and a quorum rule; aggregate with weights learned from eval data; escalate low agreement to a review queue; cache by input hash; monitor agreement rate, per-member accuracy and cost.

---

## 💰 Cost Impact
- Token formula (approximate): `total ≈ N × (prompt + answer tokens)`, so cost scales roughly linearly with N. Latency stays near the slowest member because they run in parallel.
- Tips: cascade (single cheap model first, ensemble only when uncertain), use small models for members, cache, short structured outputs, and cap N at 3-5.
- Pricing: approximate, from public pricing at time of writing, verify.

---

## 🔷 When to Use
✅ Use when:
- Errors are costly and answers are discrete (codes, labels, yes/no)
- You need a confidence signal from agreement
- Members can be made genuinely diverse

❌ Avoid when:
- Open-ended generation where "voting" is meaningless (use a judge instead)
- Tight budget or latency with no cascade
- All members would share the same blind spot

---

## 📊 Visual Diagram
```
                 +--> Agent A (model 1) --+
 task ---------> +--> Agent B (model 2) --+--> Aggregator --> answer
 (same input)    +--> Agent C (prompt 3) -+   (vote/weights)     +
                                                              agreement
                                                                 |
                                       agreement < threshold --> human review
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ensemble | Group of agents combined | समूह |
| Majority vote | Most common answer wins | बहुमत मत |
| Agreement | Share of members that agree | सहमति |
| Quorum | Minimum valid answers needed | न्यूनतम कोरम |
| Diversity | Members differ in errors | विविधता |
| Cascade | Cheap first, panel if unsure | चरणबद्ध जाँच |

---

## ⚡ 3-Line Summary
English: Ask several diverse agents the same question and combine answers by vote or merge.
Agreement gives a confidence signal; low agreement should escalate.
Cost scales with members, so use cascades and diverse, cheap members.

Hindi: कई विविध agents से एक ही सवाल पूछकर vote या merge से जवाब जोड़ो।
Agreement से confidence का संकेत मिलता है; कम agreement पर escalate करो।
Cost members के साथ बढ़ती है, इसलिए cascade और सस्ते विविध members इस्तेमाल करो।

---

## ➡️ Next Topic
186. Router Pattern (Deep): instead of asking everyone, route each request to the single best agent.

---
