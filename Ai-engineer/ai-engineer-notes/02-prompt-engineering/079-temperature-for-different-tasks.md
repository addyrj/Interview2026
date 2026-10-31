---

# 079. Temperature for Different Tasks
# हिंदी में: अलग-अलग tasks के लिए Temperature

---

## 🔵 Simple Definition (English)
Temperature is a sampling setting that controls how random the next-token choice is. Low temperature (0 to 0.2) makes the model pick the most likely tokens: consistent and focused. High temperature (0.7 to 1.0+) spreads choices: varied and creative, but less reliable. Pick it per task.

## 🔵 सरल परिभाषा (Hindi)
Temperature एक sampling setting है जो तय करती है कि अगला token चुनना कितना random हो। कम temperature (0 से 0.2) में model सबसे संभावित tokens चुनता है: स्थिर और focused। ज़्यादा temperature (0.7 से 1.0+) में चुनाव फैलता है: विविध और रचनात्मक, पर कम भरोसेमंद। हर task के हिसाब से चुनो।

---

## 🔴 Problem it Solves
One global temperature does not fit all tasks. Using 1.0 for HS-code extraction gives different codes for the same product on different runs. Using 0 for marketing copy gives repetitive, bland text. Wrong temperature causes flaky structured output, inconsistent classification or boring creative output.

## 🔴 यह क्यों बना? (Hindi)
सब tasks के लिए एक ही temperature ठीक नहीं बैठता। HS-code extraction में 1.0 रखने पर एक ही product के लिए अलग runs में अलग codes आते हैं। Marketing copy में 0 रखने पर नीरस, दोहराव वाला text मिलता है। गलत temperature से structured output अस्थिर, classification असंगत या creative output फीका हो जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Model outputs a score (logit) for every token in its vocabulary
Step 2 → Logits are divided by temperature T: logit / T
Step 3 → Softmax turns them into probabilities
         - T small (0.1): the top token gets almost all probability (sharp)
         - T = 1: original distribution
         - T large (1.5): probabilities flatten (more random)
Step 4 → One token is sampled from the distribution
         (T = 0 means "always take the top token", i.e. greedy/near-deterministic)
Step 5 → Repeat for each token
Related knobs: top_p (nucleus sampling), top_k, frequency/presence penalty, seed
Tip: change temperature OR top_p, not both at once.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Model अपनी vocabulary के हर token का score (logit) देता है
Step 2 → Logits को temperature T से भाग दिया जाता है: logit / T
Step 3 → Softmax से probabilities बनती हैं
         - T छोटा (0.1): top token को लगभग सारी probability (तीखा)
         - T = 1: मूल distribution
         - T बड़ा (1.5): probabilities चपटी (ज़्यादा random)
Step 4 → Distribution से एक token sample होता है
         (T = 0 का मतलब "हमेशा top token", यानी greedy/लगभग deterministic)
Step 5 → हर token के लिए दोहराओ
संबंधित knobs: top_p, top_k, frequency/presence penalty, seed
सुझाव: temperature या top_p में से एक बदलो, दोनों नहीं।
```

---

## 🟡 Real World Example
**Tariff Classification System**:
- HS code extraction / classification: temperature 0.
- Explanation for the officer: temperature 0.2-0.3 (clear, slightly varied wording).
- Generating synthetic test products for evals: temperature 0.9 (diversity).
- Query rewriting for retrieval: 0.2-0.4.

**Zomato-style**: Intent classification at 0; a fun push-notification copy generator at 0.9.

## 🟡 Real Example Hindi mein
**Tariff System**:
- HS code extraction / classification: temperature 0।
- Officer के लिए explanation: temperature 0.2-0.3 (साफ़, शब्दों में थोड़ी विविधता)।
- Evals के लिए synthetic test products बनाना: temperature 0.9 (विविधता)।
- Retrieval के लिए query rewriting: 0.2-0.4।

**Zomato-style**: Intent classification 0 पर; मज़ेदार push-notification copy generator 0.9 पर।

---

## 💻 Code Example — Basic
```python
# Basic: see how temperature reshapes probabilities (pure Python, no API)
import math  # for exp

def softmax_with_temperature(logits: list[float], t: float) -> list[float]:
    scaled = [x / t for x in logits]                 # divide logits by temperature
    m = max(scaled)                                  # subtract max for numerical stability
    exps = [math.exp(x - m) for x in scaled]         # exponentiate
    total = sum(exps)                                # normaliser
    return [e / total for e in exps]                 # probabilities

tokens = ["8518.30", "8517.13", "8543.70"]           # candidate answers
logits = [3.0, 2.0, 0.5]                             # model scores (made up)

for t in (0.2, 1.0, 2.0):                            # low, normal, high temperature
    probs = softmax_with_temperature(logits, t)      # distribution at this temperature
    print(t, {tok: round(p, 3) for tok, p in zip(tokens, probs)})
# t=0.2 -> top token ~0.99 ; t=2.0 -> probabilities much closer together
```

## 💻 Code Example — Advanced
```python
# Production: task-based temperature policy + consistency measurement (async)
from __future__ import annotations

import asyncio                                    # async runner
from collections import Counter                   # count distinct answers
from dataclasses import dataclass                 # settings container
from typing import Awaitable, Callable            # type hints

@dataclass(frozen=True)
class Sampling:
    temperature: float                            # randomness
    top_p: float = 1.0                            # nucleus sampling (leave at 1 when tuning temperature)
    max_tokens: int = 300                         # output cap

POLICY: dict[str, Sampling] = {                   # one place that defines settings per task
    "classify":  Sampling(0.0, max_tokens=30),
    "extract":   Sampling(0.0, max_tokens=300),
    "explain":   Sampling(0.3, max_tokens=400),
    "rewrite_q": Sampling(0.3, max_tokens=60),
    "synthetic": Sampling(0.9, max_tokens=200),
}

def settings_for(task: str) -> Sampling:
    try:
        return POLICY[task]                       # known task
    except KeyError as exc:
        raise ValueError(f"no sampling policy for task {task!r}") from exc

LLM = Callable[[str, Sampling], Awaitable[str]]   # (prompt, sampling) -> reply

async def consistency(llm: LLM, prompt: str, s: Sampling, runs: int = 10) -> float:
    """Fraction of runs that return the most common answer (1.0 = fully consistent)."""
    outs = await asyncio.gather(*(llm(prompt, s) for _ in range(runs)))   # repeated calls
    top_count = Counter(o.strip() for o in outs).most_common(1)[0][1]     # most common answer count
    return top_count / runs

async def _demo() -> None:
    import random
    async def sim(prompt: str, s: Sampling) -> str:
        # Simulated model: higher temperature -> more chance of a wrong variant
        return "8518.30" if random.random() > s.temperature * 0.5 else "8517.13"
    print("classify", await consistency(sim, "earbuds?", settings_for("classify")))
    print("synthetic", await consistency(sim, "earbuds?", settings_for("synthetic")))

if __name__ == "__main__":
    asyncio.run(_demo())
```
Token usage: temperature itself does not change token price, but higher temperature can produce longer, wandering outputs, and unstable outputs cause retries.

---

## 🟠 FastAPI Integration
Keep the policy server-side so clients cannot ask for temperature 2.0 on a classification route. Offer an optional, validated override only for creative endpoints.

```python
from fastapi import FastAPI                       # framework
from pydantic import BaseModel, Field             # models
from openai import AsyncOpenAI                    # openai>=1

app = FastAPI()                                   # app
client = AsyncOpenAI()                            # client

class ClassifyIn(BaseModel):
    product: str                                  # input

class CopyIn(BaseModel):
    brief: str                                    # input
    creativity: float = Field(0.8, ge=0.5, le=1.2)   # bounded override for creative route only

@app.post("/classify")
async def classify(body: ClassifyIn) -> dict[str, str]:
    s = settings_for("classify")                  # temperature 0
    r = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=s.temperature, max_tokens=s.max_tokens,
        messages=[{"role": "user", "content": f"HS code for {body.product}. Code only."}])
    return {"hs_code": (r.choices[0].message.content or "").strip()}

@app.post("/marketing-copy")
async def copy(body: CopyIn) -> dict[str, str]:
    r = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=body.creativity, max_tokens=200,
        messages=[{"role": "user", "content": f"Write a short ad line: {body.brief}"}])
    return {"copy": r.choices[0].message.content or ""}
```

---

## 🔗 LangChain / LangGraph Connection
Set temperature on the model object, one model instance per role. In LangGraph, different nodes can use different model instances (a deterministic classifier node and a creative writer node). Use `.bind(temperature=...)` or separate `ChatOpenAI` objects.

```python
from langchain_openai import ChatOpenAI           # model class

classifier = ChatOpenAI(model="gpt-4o-mini", temperature=0)      # deterministic node
explainer = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)     # light variation
writer = ChatOpenAI(model="gpt-4o-mini", temperature=0.9)        # creative node
# graph: classify_node uses classifier -> explain_node uses explainer
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Default temperature (often 1.0) for extraction
✅ Correct: Set 0 for deterministic tasks.
```python
# Wrong
await client.chat.completions.create(model=m, messages=msgs)   # default temperature

# Right
await client.chat.completions.create(model=m, messages=msgs, temperature=0)
```

❌ Mistake 2: Believing temperature 0 is perfectly deterministic
✅ Correct: It is near-deterministic; hardware, batching and model updates can still change outputs. Use `seed` where supported, structured outputs, and validators.
```python
# Wrong
assert reply == expected_exact_text          # flaky in CI

# Right
assert validate(reply)                        # check meaning/format, not exact bytes
```

❌ Mistake 3: Changing temperature and top_p together, making behaviour hard to reason about. Tune one.

Note: some reasoning models do not accept a custom temperature (or fix it); check the model docs before setting it.

---

## 🧠 Tricky Interview Question
**Q**: "With temperature 0 the same prompt still gives slightly different outputs across runs. Why, and what do you do?"

**Answer**: Temperature 0 means greedy decoding, but outputs can still differ because of floating-point non-determinism on GPUs, batching, and tie-breaking when two tokens have nearly equal scores, plus silent model version updates. Mitigate: pin model versions, use the `seed` parameter where available (best-effort), constrain output with structured outputs/enums, validate semantically in tests, and design systems to tolerate small variations.

---

## ⚫ Interview Questions + Answers

Q1: What does temperature do?
A1: It scales logits before sampling; low values make output focused and repeatable, high values make it more random and varied.

Q2: What temperature for classification or data extraction?
A2: 0 or very low (up to 0.2), for consistency.

Q3: What temperature for brainstorming or creative writing?
A3: Higher, about 0.7 to 1.0, to get diverse outputs. Often combined with a diversity check.

Q4: Temperature vs top_p?
A4: Temperature reshapes the whole distribution; top_p keeps only the smallest set of tokens whose probability adds up to p (nucleus). Usually adjust one of them, not both.

Q5 (Hard): How would you run best-of-N generation and pick the best result?
A5: Sample N outputs at moderate temperature (0.7-1.0) for diversity, score them with a verifier (rules, tests, a reward or judge model, or self-consistency voting for answers), return the best. Cost is N times output tokens, so use it only for high-value tasks, parallelise calls, and cap N. For classification, majority vote across samples (self-consistency) often beats a single greedy answer on hard cases.

---

## 🔷 When to Use + When Not to Use
(Use = guidance for settings.)

✅ Low (0-0.2) when:
- Classification, extraction, JSON output, code, math, factual Q&A

✅ Medium (0.3-0.7) when:
- Explanations, summaries, chat assistants

✅ High (0.8-1.2) when:
- Brainstorming, creative writing, synthetic data

❌ Avoid high temperature when:
- Output must follow a schema or be reproducible

---

## 📊 Visual Diagram
```
 Probability of next token (logits 3.0, 2.0, 0.5)

 T = 0.2   |#################### 99%
 (sharp)   |#
           |
 T = 1.0   |##############  73%
           |#####           ~ 27% (rest)
 T = 2.0   |########  52%
 (flat)    |######    ~ 31%
           |####      ~ 17%

 low T  -> consistent (classification)
 high T -> varied (creative)
```

---

## 💰 Cost Impact
- Temperature does not change the per-token price.
- High temperature can lead to longer or off-format outputs, which means more output tokens and retries.
- Best-of-N and self-consistency multiply output tokens by N.
- Low temperature makes caching (response caching by prompt hash) effective because answers repeat.

Optimisation: use 0 for deterministic tasks, enable response caching for repeated queries, cap `max_tokens`, and use best-of-N only where the quality gain pays for N times the cost.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Temperature | Randomness of sampling | Sampling की randomness |
| top_p | Nucleus sampling threshold | Nucleus sampling की सीमा |
| Greedy decoding | Always pick top token | हमेशा सबसे ऊपर वाला token |
| Logit | Raw token score | Token का कच्चा score |
| Softmax | Scores to probabilities | Scores को probabilities में बदलना |
| Self-consistency | Vote across samples | कई samples में वोट |

---

## ⚡ 3-Line Summary
English: Temperature controls randomness: near 0 for classification, extraction and JSON; moderate for explanations; high for creative work. Do not assume 0 is perfectly deterministic. Set values per task in one policy, not globally.
Hindi: Temperature randomness नियंत्रित करता है: classification, extraction और JSON के लिए 0 के आसपास; explanations के लिए मध्यम; creative काम के लिए ज़्यादा। मत मानो कि 0 पूरी तरह deterministic है। मान हर task के लिए एक policy में रखो, global नहीं।

---

## ➡️ Next Topic
**080. Production Prompt Best Practices** — a checklist that ties prompts, testing, safety and cost together for production.
