
---

# 503. Domain Adaptation
# हिंदी में: Domain Adaptation — Model को किसी खास क्षेत्र के लिए ढालना

---

## 🔵 Simple Definition (English)
Domain adaptation means making a general LLM work well in one specific field (customs tariffs, legal, medical, food delivery). It is a toolbox: better prompts, RAG, fine-tuning (SFT/LoRA), continued pre-training, and preference tuning. You pick the cheapest tool that closes the gap.

## 🔵 सरल परिभाषा (Hindi)
Domain adaptation का मतलब general LLM को एक खास क्षेत्र (customs tariff, legal, medical, food delivery) में अच्छा बनाना है। यह एक toolbox है: बेहतर prompts, RAG, fine-tuning (SFT/LoRA), continued pre-training और preference tuning। सबसे सस्ता tool चुनो जो gap भर दे।

---

## 🔴 Problem it Solves
A general model is "okay at everything": it may miss domain terms, use the wrong output format, hallucinate codes, or be too slow/costly. Teams often jump to fine-tuning when the real issue is missing context (RAG fixes) or an unclear prompt. Domain adaptation gives a decision order so you do not waste weeks.

## 🔴 यह क्यों बना? (Hindi)
General model "सब में ठीक-ठाक" होता है: domain शब्द चूक जाता है, format गलत देता है, codes hallucinate करता है। Teams अक्सर सीधे fine-tuning पर कूद जाती हैं जबकि असली दिक्कत context की कमी (RAG) या अस्पष्ट prompt होती है। Domain adaptation एक decision क्रम देता है ताकि हफ़्ते बर्बाद न हों।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build an eval set first (100-300 real domain questions with gold answers)
Step 2 → Measure baseline: general model + simple prompt
Step 3 → Diagnose failures: knowledge gap? format gap? behaviour gap? cost/latency?
Step 4 → Knowledge changes often or needs citations → add RAG
Step 5 → Format/style/behaviour gap with examples available → SFT (LoRA)
Step 6 → Preference/safety/calibration gap → DPO on pairs
Step 7 → Deep stable vocabulary gap + huge corpus → continued pre-training
Step 8 → Re-run eval after each step; stop when target met; monitor drift in production
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले eval set बनाओ (100-300 असली domain सवाल + सही जवाब)
Step 2 → Baseline मापो: general model + साधारण prompt
Step 3 → Failure का कारण: knowledge gap? format gap? behaviour gap? cost/latency?
Step 4 → Knowledge बदलती है या citation चाहिए → RAG
Step 5 → Format/style/behaviour gap + examples उपलब्ध → SFT (LoRA)
Step 6 → Preference/safety gap → DPO
Step 7 → गहरी stable vocabulary gap + बड़ा corpus → continued pre-training
Step 8 → हर step के बाद eval दोबारा चलाओ; production में drift देखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Baseline GPT-style model gets 58% exact match on 8-digit HS codes. Failures: (a) 40% are stale/missing rule text, so add RAG over the current tariff schedule: 71%. (b) 15% are format errors (code with extra prose), so SFT on 1,500 examples: 82%. (c) Overconfident wrong answers, so DPO with officer preferences: calibrated "needs review" flags. CPT was judged not worth it.

**Zomato AI**: Menu and dish names in Hinglish confuse the model. RAG over the menu DB plus a small SFT for dish-tagging JSON was enough; no pre-training.

## 🟡 Real Example Hindi mein
**Tariff System**: Baseline पर 8-digit HS code exact match 58%। (a) 40% failures पुराने/गायब rule text से, RAG जोड़ा: 71%। (b) 15% format errors, 1,500 examples पर SFT: 82%। (c) Overconfident गलत answers, officers की preference पर DPO। CPT ज़रूरी नहीं लगा।

**Zomato AI**: Hinglish dish names पर confusion। Menu DB पर RAG + dish-tagging JSON के लिए छोटा SFT काफ़ी रहा।

---

## 💻 Code Example — Basic
```python
# Pure Python: a tiny decision helper that recommends an adaptation method from failure counts
from dataclasses import dataclass  # simple data container

@dataclass
class Diagnosis:
    knowledge_gap: float   # share of failures caused by missing/stale facts (0-1)
    format_gap: float      # share caused by wrong output format/style
    behaviour_gap: float   # share caused by overconfidence/unsafe answers
    vocab_gap: float       # share caused by not understanding domain language at all
    data_changes_often: bool  # do facts change monthly or faster?

def recommend(d: Diagnosis) -> list[str]:
    """Return an ordered list of techniques to try."""
    plan: list[str] = ["better prompt + few-shot"]  # always cheapest first
    if d.knowledge_gap > 0.2 or d.data_changes_often:  # missing facts -> retrieval
        plan.append("RAG")
    if d.format_gap > 0.1:  # format/style problems -> supervised tuning
        plan.append("SFT / LoRA")
    if d.behaviour_gap > 0.1:  # calibration/safety -> preference tuning
        plan.append("DPO")
    if d.vocab_gap > 0.3 and not d.data_changes_often:  # deep stable language gap
        plan.append("continued pre-training")
    return plan  # ordered plan

print(recommend(Diagnosis(0.4, 0.15, 0.1, 0.05, True)))  # tariff example
# -> ['better prompt + few-shot', 'RAG', 'SFT / LoRA']
```

## 💻 Code Example — Advanced
```python
# Production: evaluate candidate "adapters" (prompt, RAG, fine-tuned model) on the same eval set
import asyncio  # concurrency
import json  # JSON eval file
import logging  # logging
from pathlib import Path  # paths
from typing import Awaitable, Callable  # callable types

log = logging.getLogger("adapt")  # logger

Answerer = Callable[[str], Awaitable[str]]  # async function: question -> HS code text

async def exact_match_rate(answer: Answerer, rows: list[dict], conc: int = 5) -> float:
    """Share of rows where predicted code equals gold code."""
    sem = asyncio.Semaphore(conc)  # limit parallel calls (rate limits/cost)

    async def one(row: dict) -> bool:
        async with sem:  # wait for a free slot
            try:
                pred = (await answer(row["question"])).strip()  # call candidate
            except Exception as exc:  # any provider failure counts as a miss
                log.warning("error on %s: %s", row["question"][:30], exc)  # log it
                return False  # miss
        return pred.startswith(row["gold"])  # allow prefix match for 6-digit vs 8-digit

    results = await asyncio.gather(*(one(r) for r in rows))  # run all
    return sum(results) / max(len(results), 1)  # accuracy

async def compare(candidates: dict[str, Answerer], eval_path: Path) -> dict[str, float]:
    """Run every candidate on the same eval set."""
    rows = json.loads(eval_path.read_text(encoding="utf-8"))  # load gold set
    scores: dict[str, float] = {}  # name -> score
    for name, fn in candidates.items():  # one by one to keep logs readable
        scores[name] = await exact_match_rate(fn, rows)  # evaluate
        log.info("%s: %.1f%%", name, scores[name] * 100)  # report
    return scores  # compare and choose the cheapest that meets the target

# Offline demo with fake answerers (no API key needed):
async def baseline(q: str) -> str: return "8517"  # always same code
async def with_rag(q: str) -> str: return "8517.13" if "phone" in q else "0000"  # pretends to retrieve

if __name__ == "__main__":
    demo = [{"question": "smart phone?", "gold": "8517.13"}, {"question": "laptop?", "gold": "8471.30"}]
    Path("demo_eval.json").write_text(json.dumps(demo))  # tiny eval set
    print(asyncio.run(compare({"baseline": baseline, "rag": with_rag}, Path("demo_eval.json"))))
```

---

## 🟠 FastAPI Integration
Expose the adapted pipeline behind one route and add a `strategy` header so you can A/B test adapters in production.

```python
from fastapi import FastAPI, Header  # framework + header param
from pydantic import BaseModel  # schema

app = FastAPI()  # app

class Q(BaseModel):
    question: str  # user question

async def run_prompt_only(q: str) -> str: return "prompt-only answer"  # stub
async def run_rag(q: str) -> str: return "rag answer"  # stub
async def run_finetuned(q: str) -> str: return "fine-tuned answer"  # stub

STRATEGIES = {"prompt": run_prompt_only, "rag": run_rag, "ft": run_finetuned}  # registry

@app.post("/classify")
async def classify(q: Q, x_strategy: str = Header(default="rag")) -> dict:
    """Pick the adaptation strategy per request (A/B test)."""
    fn = STRATEGIES.get(x_strategy, run_rag)  # unknown -> default to RAG
    return {"strategy": x_strategy, "answer": await fn(q.question)}  # result
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph lets you combine adaptations: retrieve (RAG) then call a fine-tuned model, then route low-confidence cases to a stronger general model or a human.

```python
from langgraph.graph import StateGraph, END  # graph builder
from typing import TypedDict  # state schema

class S(TypedDict):
    question: str  # input
    context: str   # retrieved text
    answer: str    # output

def retrieve(s: S) -> dict: return {"context": "tariff rules ..."}  # RAG node (stub)
def generate(s: S) -> dict: return {"answer": "8517.13"}  # fine-tuned model node (stub)

g = StateGraph(S)  # create graph
g.add_node("retrieve", retrieve)  # add node
g.add_node("generate", generate)  # add node
g.set_entry_point("retrieve")  # start
g.add_edge("retrieve", "generate")  # RAG then model
g.add_edge("generate", END)  # finish
app_graph = g.compile()  # runnable
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Fine-tuning before measuring
✅ Correct: Build the eval set and baseline first.
```python
# Wrong: train on 5,000 examples, then "it feels better"
# Right: score baseline -> adapt -> score again on the SAME held-out set
```

❌ Mistake 2: Fine-tuning to inject changing facts
✅ Correct: Facts go in retrieval, behaviour goes in weights.
```python
# Wrong: fine-tune on this month's duty rates
# Right: store rates in a DB/vector store; fine-tune only output style and reasoning
```

❌ Mistake 3: Eval data leaks into training data
✅ Correct: Split by question/source before any tuning and never reuse the test set for tuning.

---

## 🧠 Tricky Interview Question

**Q**: "Management says: fine-tune GPT on our 3,000 tariff PDFs so it 'knows' them. Do you agree?"

**Answer**: Not as a first step. Fine-tuning on documents teaches style and weakly encodes facts; it hallucinates details and cannot cite. Rules also change. I would use RAG for knowledge and, if format or tone issues remain, SFT on labelled Q&A examples. Only if the language itself is alien and stable, and we have a big corpus, would I consider continued pre-training. Decide with an eval set, not opinion.

---

## ⚫ Interview Questions + Answers

Q1: What is domain adaptation in LLM work?
A1: Making a general model perform well in a specific field using prompting, RAG, fine-tuning, continued pre-training or preference tuning.

Q2: RAG or fine-tuning for fresh facts?
A2: RAG. Weights are slow and costly to update; retrieval is instant and can cite sources.

Q3: What does SFT fix that RAG cannot?
A3: Output format, style, task behaviour, shorter prompts and lower latency. RAG supplies knowledge but does not reliably change behaviour.

Q4: How do you decide the order of techniques?
A4: Cheapest and most reversible first: prompt, then RAG, then SFT/LoRA, then DPO, then continued pre-training. Move on only when an eval shows the remaining gap.

Q5: How do you handle drift after deployment?
A5: Log inputs/outputs, sample for human review, track accuracy and cost metrics, refresh RAG data continuously, and retrain adapters on a schedule using new labelled failures, always re-checking the regression set.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Generic accuracy is below your target on a domain eval
- You see repeated, consistent failure patterns

❌ Avoid when:
- You have no eval set
- A prompt change has not been tried
- You cannot maintain the adapted system over time

---

## 📊 Visual Diagram
```
            ┌────────────────────┐
 Eval set ─►│ Baseline score     │
            └─────────┬──────────┘
                      ▼
   missing facts? ─► RAG ───────────┐
   bad format?    ─► SFT / LoRA ────┤  re-evaluate
   bad behaviour? ─► DPO ───────────┤  after each
   alien language?─► Continued PT ──┘
                      ▼
          target met?  yes ─► deploy + monitor
                       no  ─► next technique
```

---

## 💰 Cost Impact
Order by cost: prompting (near zero) < RAG (embedding + vector DB + extra context tokens) < SFT/LoRA (training tokens + possibly higher per-token price for hosted fine-tuned models) < DPO < CPT (GPU heavy). Token usage: RAG adds retrieved chunks (e.g. 3 x 300 = ~900 input tokens per call), while SFT can remove long few-shot examples (e.g. save 800 tokens per call). At 1M calls/month, saving 800 input tokens at an illustrative $0.15 per 1M input tokens is $120/month; compare this against training cost to see the break-even. Prices are illustrative; check current pricing.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Domain adaptation | Specialising a model for a field | किसी क्षेत्र के लिए model ढालना |
| Baseline | Score before any change | बदलाव से पहले का score |
| Eval set | Gold questions for testing | जाँच के लिए सही-जवाब वाले सवाल |
| LoRA | Train small adapter weights | छोटे adapter weights train करना |
| Drift | Quality changes over time | समय के साथ quality बदलना |
| Data leakage | Test data seen in training | Test data का training में आ जाना |
| Regression set | Checks old skills still work | पुरानी skills जाँचने का set |

---

## ⚡ 3-Line Summary
English: Domain adaptation is a ladder: prompt, RAG, SFT, DPO, continued pre-training. Build an eval set first and climb only as far as the measured gap needs. Put changing facts in retrieval and behaviour in weights.
Hindi: Domain adaptation एक सीढ़ी है: prompt, RAG, SFT, DPO, continued pre-training। पहले eval set बनाओ और जितना gap हो उतना ही ऊपर चढ़ो। बदलते facts retrieval में, behaviour weights में।

---

## ➡️ Next Topic
**504. Fine Tuning for Tariff System** — applying this ladder concretely to the HS-code classifier.
