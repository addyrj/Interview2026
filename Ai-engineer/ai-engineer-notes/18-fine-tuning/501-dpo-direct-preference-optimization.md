
---

# 501. DPO — Direct Preference Optimization
# हिंदी में: DPO — सीधे Preference से Model को Train करना

---

## 🔵 Simple Definition (English)
DPO is a fine-tuning method where you show the model pairs of answers for the same prompt: one **preferred** (good) and one **non-preferred** (bad). The model is trained to raise the chance of the good answer and lower the chance of the bad one. It needs no separate reward model and no reinforcement-learning loop.

## 🔵 सरल परिभाषा (Hindi)
DPO एक fine-tuning method है जिसमें एक ही prompt के लिए दो answers दिखाए जाते हैं: एक **preferred** (अच्छा) और एक **non-preferred** (खराब)। Model को सिखाया जाता है कि अच्छे answer की probability बढ़ाए और खराब की घटाए। इसमें अलग reward model या RL loop की ज़रूरत नहीं होती।

---

## 🔴 Problem it Solves
SFT (supervised fine-tuning) only shows "the right answer". It never says "this answer is worse than that one". Style, tone, refusal behaviour and "prefer the safer HS code" are hard to teach with only positive examples. RLHF solved this but needs a reward model, PPO, and a lot of GPU and tuning, which is unstable and expensive. DPO gets a similar effect with a simple classification-style loss on preference pairs.

## 🔴 यह क्यों बना? (Hindi)
SFT सिर्फ "सही answer" दिखाता है, यह नहीं बताता कि कौन सा answer दूसरे से बेहतर है। Tone, refusal और "safer HS code चुनो" जैसी चीज़ें सिर्फ positive examples से सीखना मुश्किल है। RLHF में reward model + PPO चाहिए, जो महंगा और unstable है। DPO simple loss से preference pairs पर वही काम कर देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Collect prompts (e.g. tariff questions) from real traffic
Step 2 → For each prompt get 2 answers: preferred (chosen) and non-preferred (rejected)
Step 3 → Usually do SFT first so the model already knows the task/format
Step 4 → Keep a frozen copy of the model as the "reference" model
Step 5 → Loss = -log sigmoid( beta * [ (logp_chosen - ref_logp_chosen)
                                      - (logp_rejected - ref_logp_rejected) ] )
Step 6 → Gradient step: chosen answer probability goes up, rejected goes down
Step 7 → beta controls how far the model may drift from the reference
Step 8 → Evaluate on held-out pairs + your eval set before shipping
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Real traffic से prompts लो (जैसे tariff questions)
Step 2 → हर prompt के लिए 2 answers: preferred (chosen) और non-preferred (rejected)
Step 3 → पहले SFT करो ताकि model task और format जानता हो
Step 4 → Model की एक frozen copy "reference" model बनाओ
Step 5 → Loss = -log sigmoid( beta * [ chosen का फ़ायदा - rejected का फ़ायदा ] )
Step 6 → Chosen की probability बढ़ती है, rejected की घटती है
Step 7 → beta तय करता है कि model reference से कितना दूर जा सकता है
Step 8 → Ship करने से पहले held-out pairs पर evaluate करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The model sometimes gives a very confident but wrong HS code, and sometimes a hedged correct one. Customs officers mark which answer they prefer. We build pairs: preferred = correct 8-digit code with a short reason and a "verify with officer" note when unsure; rejected = confident wrong code. After DPO the model stops overclaiming.

**Zomato-style**: Two reply drafts for a refund complaint; the polite and policy-correct one is preferred over the rude one. DPO teaches brand tone without writing thousands of perfect replies.

## 🟡 Real Example Hindi mein
**Tariff System**: Model कभी-कभी गलत HS code बहुत confidently दे देता है। Customs officers बताते हैं कौन सा answer बेहतर है। Preferred = सही code + छोटा कारण; rejected = confident गलत code। DPO के बाद model overclaim करना बंद कर देता है।

**Zomato-style**: Refund complaint के दो reply drafts; polite और policy-सही वाला preferred, rude वाला rejected।

---

## 💻 Code Example — Basic
```python
# Pure Python: compute the DPO loss for ONE preference pair (no libraries needed)
import math  # math gives us log and exp

def log_sigmoid(x: float) -> float:
    """Numerically safe log(sigmoid(x))."""
    if x >= 0:  # for positive x use the stable form
        return -math.log1p(math.exp(-x))  # -log(1 + e^-x)
    return x - math.log1p(math.exp(x))  # x - log(1 + e^x) for negative x

def dpo_loss(
    logp_chosen: float,      # log-prob of chosen answer under the policy being trained
    logp_rejected: float,    # log-prob of rejected answer under the policy
    ref_logp_chosen: float,  # log-prob of chosen answer under the frozen reference
    ref_logp_rejected: float,  # log-prob of rejected answer under the reference
    beta: float = 0.1,       # strength of the KL-like constraint
) -> float:
    """Return the DPO loss (lower is better)."""
    chosen_gain = logp_chosen - ref_logp_chosen  # how much policy raised the chosen answer
    rejected_gain = logp_rejected - ref_logp_rejected  # how much policy raised the rejected answer
    margin = beta * (chosen_gain - rejected_gain)  # reward margin (implicit reward)
    return -log_sigmoid(margin)  # loss is small when the margin is large and positive

# Before training: policy equals reference, so margin = 0 and loss = log(2)
print("start :", round(dpo_loss(-10.0, -10.0, -10.0, -10.0), 4))  # ~0.6931
# After training: chosen went up, rejected went down
print("better:", round(dpo_loss(-8.0, -14.0, -10.0, -10.0), 4))  # smaller loss
# Wrong direction: chosen went down, rejected went up
print("worse :", round(dpo_loss(-14.0, -8.0, -10.0, -10.0), 4))  # larger loss
```

## 💻 Code Example — Advanced
```python
# Production: build + validate a DPO dataset and start an OpenAI DPO fine-tuning job
# pip install openai   (needs OPENAI_API_KEY; model names/support change - check the docs)
import asyncio  # for the async version
import json  # JSONL writing
import logging  # structured logs
from pathlib import Path  # file paths
from typing import TypedDict  # typed dicts for rows

from openai import AsyncOpenAI, OpenAIError  # official async client

log = logging.getLogger("dpo")  # module logger

class PrefRow(TypedDict):
    prompt: str    # user question
    chosen: str    # preferred answer
    rejected: str  # non-preferred answer

SYSTEM = "You are a customs tariff assistant. Give HS codes with a short reason."  # fixed system prompt

def to_dpo_line(row: PrefRow) -> dict:
    """Convert one pair to OpenAI's DPO JSONL schema."""
    return {
        "input": {"messages": [  # shared context for both answers
            {"role": "system", "content": SYSTEM},  # system turn
            {"role": "user", "content": row["prompt"]},  # user turn
        ]},
        "preferred_output": [{"role": "assistant", "content": row["chosen"]}],  # good answer
        "non_preferred_output": [{"role": "assistant", "content": row["rejected"]}],  # bad answer
    }

def write_jsonl(rows: list[PrefRow], path: Path) -> int:
    """Validate and write rows; return how many were kept."""
    kept = 0  # counter of valid rows
    with path.open("w", encoding="utf-8") as f:  # open output file
        for r in rows:  # loop over pairs
            if not r["prompt"].strip() or r["chosen"].strip() == r["rejected"].strip():
                log.warning("skip bad pair: %r", r["prompt"][:40])  # identical/empty pairs teach nothing
                continue  # drop it
            f.write(json.dumps(to_dpo_line(r), ensure_ascii=False) + "\n")  # one JSON per line
            kept += 1  # count it
    return kept  # number written

async def start_dpo(train: Path, val: Path, beta: float = 0.1) -> str:
    """Upload files and create a DPO job; return the job id."""
    client = AsyncOpenAI()  # reads OPENAI_API_KEY from env
    try:
        tf = await client.files.create(file=train.open("rb"), purpose="fine-tune")  # upload train
        vf = await client.files.create(file=val.open("rb"), purpose="fine-tune")  # upload validation
        job = await client.fine_tuning.jobs.create(
            model="gpt-4o-mini-2024-07-18",  # base model (check which models support DPO)
            training_file=tf.id,  # train file id
            validation_file=vf.id,  # validation file id
            method={"type": "dpo", "dpo": {"hyperparameters": {"beta": beta}}},  # DPO config
        )
        return job.id  # poll this id later
    except OpenAIError as exc:  # API/network/auth errors
        log.error("DPO job failed to start: %s", exc)  # log it
        raise  # let caller decide

if __name__ == "__main__":
    pairs: list[PrefRow] = [
        {"prompt": "HS code for a lithium power bank?",
         "chosen": "8507.60 (lithium-ion accumulators). Verify with an officer if capacity is unusual.",
         "rejected": "8504.40, definitely, no need to check."},
    ]
    print(write_jsonl(pairs, Path("dpo_train.jsonl")), "rows written")  # local validation only
    # asyncio.run(start_dpo(Path("dpo_train.jsonl"), Path("dpo_val.jsonl")))  # needs key + enough rows
```

---

## 🟠 FastAPI Integration
Training is offline, but FastAPI collects the preference data: an officer clicks "A is better than B" and the API stores the pair.

```python
from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel, Field  # request validation

app = FastAPI()  # app instance
STORE: list[dict] = []  # demo store; use a real DB in production

class Preference(BaseModel):
    prompt: str = Field(min_length=3)  # the tariff question
    chosen: str  # answer officer preferred
    rejected: str  # answer officer rejected

@app.post("/feedback/preference")
async def save_preference(p: Preference) -> dict:
    """Store one preference pair for the next DPO run."""
    if p.chosen.strip() == p.rejected.strip():  # identical answers are useless
        raise HTTPException(status_code=422, detail="chosen and rejected are identical")
    STORE.append(p.model_dump())  # save the pair
    return {"stored": len(STORE)}  # running count; train when you have hundreds+
```

---

## 🔗 LangChain / LangGraph Connection
LangChain does not train models, but it produces the data. A LangGraph workflow can generate two candidate answers (different temperature or model), let a judge node or a human pick the better one, and write the pair to your dataset. LangSmith feedback can also be exported as preference pairs.

```python
from langchain_openai import ChatOpenAI  # LangChain chat model wrapper

llm_a = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)  # candidate A
llm_b = ChatOpenAI(model="gpt-4o-mini", temperature=1.0)  # candidate B (more random)

async def make_pair(q: str) -> dict:
    a = (await llm_a.ainvoke(q)).content  # answer A
    b = (await llm_b.ainvoke(q)).content  # answer B
    return {"prompt": q, "a": a, "b": b}  # a judge/human then labels chosen vs rejected
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Pairs that differ in length/style only
✅ Correct: Make the pair differ in the quality you care about (correctness, safety).
```python
# Wrong: chosen is just longer, so model learns "be wordy"
pair = {"chosen": "Long long detailed answer ...", "rejected": "8517.13"}
# Right: both similar length, only the correctness differs
pair = {"chosen": "8517.13 - smartphones.", "rejected": "8517.62 - routers."}
```

❌ Mistake 2: Running DPO on a base model that never saw the task
✅ Correct: Do SFT first, then DPO.
```python
# Wrong: DPO directly on a model that does not know the output format
# Right: SFT on gold examples -> DPO on preference pairs -> evaluate
```

❌ Mistake 3: Setting beta too low and over-optimising
✅ Correct: Start near 0.1 and compare against your eval set; lower beta lets the model drift more.

---

## 🧠 Tricky Interview Question

**Q**: "After DPO your tariff model's answers got longer and the accuracy did not improve. Why, and what do you do?"

**Answer**: DPO optimises the *relative* likelihood of chosen vs rejected. If chosen answers were systematically longer or more polite, the model learns that shortcut (length bias) instead of correctness. Fix: balance lengths, build pairs where only correctness differs, add a length-normalised variant or filter, raise beta to stay near the reference, and judge success with an accuracy eval on held-out HS codes, not with loss.

---

## ⚫ Interview Questions + Answers

Q1: What does DPO stand for and what is its input?
A1: Direct Preference Optimization. Input is triples of (prompt, preferred answer, non-preferred answer).

Q2: Do you need a reward model for DPO?
A2: No. The reward is implicit in the log-probability ratio between the policy and a frozen reference. That is the main simplification over RLHF.

Q3: What does beta do?
A3: It scales the implicit reward margin and acts like a leash to the reference model. Higher beta keeps the model closer to the reference; lower beta lets it move further and risks over-fitting or degraded fluency.

Q4: When would you choose DPO over SFT?
A4: When the goal is to change preferences (tone, safety, calibration, refusing to overclaim) and you can get ranked pairs. Use SFT to teach a new format or knowledge; DPO to refine behaviour after SFT.

Q5: How do you know DPO helped and did not just game the loss?
A5: Track held-out preference accuracy, but mostly run a task eval (HS-code exact match, hallucination rate, refusal calibration) and a regression set for old abilities. Also inspect length distribution and sample outputs by hand. Compare to a prompt-engineering baseline, which is often cheaper.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have preference data (human or judge-labelled) and SFT is already done
- You want to fix tone, verbosity, overconfidence, safety behaviour

❌ Avoid when:
- You only need new knowledge (use RAG)
- You have under a few hundred clean pairs
- A better prompt or few-shot examples already fixes it

---

## 📊 Visual Diagram
```
 prompt ──► model ──► answer A ─┐
        └─► model ──► answer B ─┤  human / judge picks
                                ▼
                  (prompt, chosen, rejected)
                                │
          ┌─────────────────────┴─────────────────────┐
          │ policy (trainable)      reference (frozen)│
          │  logp(chosen/rejected)   ref_logp(...)    │
          └─────────────────────┬─────────────────────┘
                                ▼
             loss = -log sigmoid(beta * margin)
                                ▼
          chosen prob UP   |   rejected prob DOWN
```

---

## 💰 Cost Impact
Training cost is billed by trained tokens (the pairs count both answers, so roughly double an SFT row). Prices change, so check the provider pricing page; any number here is illustrative. After training, a fine-tuned model is usually priced higher per token than the base model, but a smaller fine-tuned model with shorter prompts can replace a large model with long few-shot prompts.
Optimise: use a small base model, 200-2,000 high-quality pairs rather than 50,000 noisy ones, deduplicate pairs, keep prompts short (drop few-shot examples after tuning), and run a validation file to stop early. Token usage: each pair is about prompt + 2 answers, e.g. 150 + 2x120 = ~390 tokens, so 1,000 pairs is about 0.4M tokens per epoch.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| DPO | Train directly on preference pairs | Preference pairs से सीधा training |
| Chosen / Preferred | The better answer | बेहतर answer |
| Rejected / Non-preferred | The worse answer | खराब answer |
| Reference model | Frozen copy used as anchor | Frozen anchor model |
| Beta | Strength of the anchor | Anchor की मज़बूती |
| RLHF | RL with a reward model | Reward model वाला RL |
| Length bias | Model prefers long answers | लंबे answers की आदत |

---

## ⚡ 3-Line Summary
English: DPO trains a model on (prompt, chosen, rejected) pairs using a simple loss against a frozen reference. It needs no reward model or RL loop, and works best after SFT. Build pairs that differ only in quality and judge with a task eval.
Hindi: DPO (prompt, chosen, rejected) pairs और frozen reference से सीधे model train करता है। Reward model या RL loop नहीं चाहिए, SFT के बाद सबसे अच्छा चलता है। Pairs ऐसे बनाओ जो सिर्फ quality में अलग हों और task eval से जाँचो।

---

## ➡️ Next Topic
**502. Continued Pre-training** — when you must teach the model a whole new domain vocabulary before any SFT or DPO.
