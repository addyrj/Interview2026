---

# 027. OpenAI Models Overview (gpt-4o, gpt-4o-mini etc)
# हिंदी में: OpenAI Models का Overview (gpt-4o, gpt-4o-mini आदि)

---

## 🔵 Simple Definition (English)
OpenAI offers several model families: flagship general models (gpt-4o), small cheap models (gpt-4o-mini), reasoning models (o-series), and specialised models (embeddings, whisper for speech-to-text, moderation, image). You choose by balancing quality, speed, and cost. Model names and prices change often, so always confirm on the official models page.

## 🔵 सरल परिभाषा (Hindi)
OpenAI कई model families देता है: flagship general models (gpt-4o), छोटे सस्ते models (gpt-4o-mini), reasoning models (o-series), और specialised models (embeddings, speech-to-text के लिए whisper, moderation, image)। आप quality, speed और cost का balance देखकर चुनते हैं। Model names और prices बदलते रहते हैं, इसलिए official models page पर confirm करो।

---

## 🔴 Problem it Solves
One model cannot be best at everything. A giant model is slow and expensive for simple tagging; a tiny model fails on hard reasoning. Offering a ladder of models lets teams match the model to the task and avoid overpaying.

## 🔴 यह क्यों बना? (Hindi)
एक model हर चीज़ में best नहीं हो सकता। सरल tagging के लिए बड़ा model धीमा और महंगा है; छोटा model कठिन reasoning में fail होता है। Models की सीढ़ी से team task के हिसाब से model चुनकर ज़्यादा खर्च से बच सकती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define the task (classify, extract, chat, reason, embed, transcribe)
Step 2 → Build a small evaluation set (50-200 real examples with correct answers)
Step 3 → Test the cheapest model first (gpt-4o-mini)
Step 4 → If accuracy is too low, try the next tier (gpt-4o or a reasoning model)
Step 5 → Compare quality, latency p95, and cost per 1,000 requests
Step 6 → Pick the cheapest model that meets your quality bar
Step 7 → Add routing: easy queries to small model, hard ones to big model
Step 8 → Pin a dated snapshot in production and re-run evals before upgrading
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Task तय करो (classify, extract, chat, reason, embed, transcribe)
Step 2 → छोटा evaluation set बनाओ (50-200 असली examples सही जवाब के साथ)
Step 3 → सबसे सस्ता model पहले test करो (gpt-4o-mini)
Step 4 → Accuracy कम हो तो अगला tier आज़माओ (gpt-4o या reasoning model)
Step 5 → Quality, latency p95 और 1,000 requests की cost compare करो
Step 6 → वो सबसे सस्ता model चुनो जो quality bar पूरा करे
Step 7 → Routing जोड़ो: आसान queries छोटे model को, कठिन बड़े को
Step 8 → Production में dated snapshot pin करो, upgrade से पहले evals दोबारा चलाओ
```

---

## 🟡 Real World Example
**Tariff Classification System** uses a model ladder:
- `text-embedding-3-small`: embed tariff chapters for retrieval.
- `gpt-4o-mini`: handles about 90 percent of simple products ("cotton t-shirt").
- `gpt-4o` (or a reasoning model): handles ambiguous items ("smart watch with cellular modem and health sensors") where the legal reading of chapter notes matters.
- Router rule: if the small model's confidence is below a threshold or the product matches several chapters, escalate.

**Zomato AI**: mini for menu Q&A, a larger model for complex multi-constraint meal planning.

## 🟡 Real Example Hindi mein
**Tariff Classification System** model ladder use करता है:
- `text-embedding-3-small`: retrieval के लिए tariff chapters embed करना।
- `gpt-4o-mini`: करीब 90 प्रतिशत आसान products ("cotton t-shirt") संभालता है।
- `gpt-4o` (या reasoning model): उलझे items ("cellular modem और health sensors वाली smart watch") जहाँ chapter notes की legal reading मायने रखती है।
- Router rule: छोटे model का confidence threshold से कम हो या product कई chapters से match हो तो escalate करो।

**Zomato AI**: Menu Q&A के लिए mini, कई शर्तों वाले meal planning के लिए बड़ा model।

---

## 💻 Code Example — Basic
```python
# Pure Python model picker: compare cost across models (no API key needed)
from typing import Dict                          # type hints

# Illustrative prices in USD per 1M tokens: (input, output). VERIFY on the pricing page!
PRICES: Dict[str, tuple] = {
    "gpt-4o-mini": (0.15, 0.60),                 # small and cheap
    "gpt-4o": (2.50, 10.00),                     # flagship general model
}

def call_cost(model: str, in_tok: int, out_tok: int) -> float:
    # Look up the price pair for this model
    p_in, p_out = PRICES[model]
    # Cost = tokens times price per token, for input and output
    return in_tok * p_in / 1_000_000 + out_tok * p_out / 1_000_000

# A typical classification call: 800 tokens in, 50 tokens out
for name in PRICES:                              # loop over models
    c = call_cost(name, 800, 50)                 # one call
    print(f"{name:12s} 1 call = ${c:.6f} | 100k calls = ${c * 100_000:,.2f}")
```

## 💻 Code Example — Advanced
```python
# Production: model router with escalation, sync + async, error handling
import asyncio                                           # async runner
import logging                                           # logs
from typing import Optional, Tuple                       # type hints

from openai import APIStatusError, AsyncOpenAI           # client + error

logger = logging.getLogger(__name__)                     # logger
client = AsyncOpenAI(timeout=30.0, max_retries=2)        # shared client

SMALL = "gpt-4o-mini"                                    # cheap default
LARGE = "gpt-4o"                                         # escalation target
HARD_WORDS = ("modem", "multi-function", "kit", "set of")  # simple hardness hint


def pick_model(product: str) -> str:
    # Route to large model when text looks ambiguous or long
    hard = len(product) > 120 or any(w in product.lower() for w in HARD_WORDS)
    return LARGE if hard else SMALL                      # decision


async def classify(product: str) -> Tuple[Optional[str], str]:
    model = pick_model(product)                          # choose tier
    try:
        r = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Return only the 6-digit HS code."},
                {"role": "user", "content": product},
            ],
            temperature=0,
            max_tokens=20,
        )
        return r.choices[0].message.content, model       # answer and model used
    except APIStatusError as exc:
        logger.error("model %s failed with %s", model, exc.status_code)
        if model == LARGE:                               # fall back to small on failure
            r = await client.chat.completions.create(
                model=SMALL,
                messages=[{"role": "user", "content": f"HS code for {product}"}],
                max_tokens=20,
            )
            return r.choices[0].message.content, SMALL
        return None, model


if __name__ == "__main__":
    print(asyncio.run(classify("cotton t-shirt")))       # goes to mini
```

---

## 🟠 FastAPI Integration
Expose the model as a request option, but validate it against an allow-list so users cannot pick expensive models.

```python
from typing import Literal                       # restrict allowed values
from fastapi import FastAPI                      # framework
from pydantic import BaseModel                   # models
from openai import AsyncOpenAI                   # client

app = FastAPI()                                  # app
client = AsyncOpenAI()                           # shared client


class Req(BaseModel):
    product: str                                 # input text
    tier: Literal["fast", "accurate"] = "fast"   # only two allowed values


TIERS = {"fast": "gpt-4o-mini", "accurate": "gpt-4o"}   # map tiers to models


@app.post("/classify")
async def classify(req: Req) -> dict:
    model = TIERS[req.tier]                      # safe lookup
    r = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": f"HS code for {req.product}? digits only"}],
        max_tokens=20,
    )
    return {"model": r.model, "hs_code": r.choices[0].message.content,
            "tokens": r.usage.total_tokens}
```

---

## 🔗 LangChain / LangGraph Connection
Use a conditional edge in LangGraph to route between a small and a large model, or use `with_fallbacks` for reliability.

```python
from langchain_openai import ChatOpenAI          # wrapper

small = ChatOpenAI(model="gpt-4o-mini", temperature=0)   # cheap model
large = ChatOpenAI(model="gpt-4o", temperature=0)        # strong model

# Reliability: if small fails (rate limit / outage), try large
resilient = small.with_fallbacks([large])
# resilient.invoke("HS code for a cotton t-shirt?")

# LangGraph routing idea (pseudo):
# graph.add_conditional_edges("router", lambda s: "large" if s["hard"] else "small",
#                             {"small": "small_node", "large": "large_node"})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the biggest model for everything
✅ Correct: Start small, measure, escalate only when needed.

```python
# Wrong — flagship for a trivial tag
model = "gpt-4o"
# Right — evaluate mini first
model = "gpt-4o-mini"
```

❌ Mistake 2: Using a floating alias in production
✅ Correct: Pin a dated snapshot (for example `gpt-4o-2024-08-06`) so behaviour does not change silently, and re-run evals before moving.

❌ Mistake 3: Choosing by benchmark hype instead of your own data
✅ Correct: Build your own eval set from real tariff queries.

---

## 🧠 Tricky Interview Question

**Q**: "gpt-4o-mini scores 92 percent and gpt-4o scores 96 percent on your eval. gpt-4o costs about 15x more. Which do you ship?"

**Answer**: It depends on the cost of an error, not just accuracy. For customs, a wrong HS code can mean duty penalties, so 4 points may be worth a lot. Best answer: route. Use mini first, get a confidence signal (for example self-reported certainty, agreement between two runs, or retrieval score), and escalate low-confidence cases to gpt-4o or to human review. Often 85 percent of traffic stays on mini, so blended accuracy approaches 96 percent at a fraction of the cost. Measure it on the eval set before deciding.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Difference between gpt-4o and gpt-4o-mini?
A1: Both are multimodal general models. mini is smaller, much cheaper, and faster; 4o is stronger on hard tasks.

Q2: [Easy] Which model do you use for embeddings?
A2: A dedicated embedding model such as `text-embedding-3-small` (cheap) or `text-embedding-3-large` (higher quality), not a chat model.

Q3: [Medium] What are reasoning models (o-series)?
A3: Models trained to think through a problem before answering, using hidden reasoning tokens that you pay for. Better on math, logic, and complex planning; slower and more expensive; some sampling parameters such as temperature may be restricted.

Q4: [Medium] Why pin a dated snapshot?
A4: Aliases like `gpt-4o` can move to a newer snapshot. Pinning keeps outputs stable and lets you test upgrades on purpose.

Q5: [Hard] How do you choose a model systematically?
A5: Create an eval set, define metrics (accuracy, latency, cost per request, failure rate), run candidate models, plot quality against cost, pick the knee of the curve, add routing and fallbacks, and re-evaluate on each new release. Also check context window, rate limits, and data-privacy terms.

---

## 🔷 When to Use + When Not to Use
✅ Use mini when:
- Classification, extraction, simple Q&A, high volume

✅ Use flagship or reasoning when:
- Ambiguous legal text, multi-step reasoning, complex code

❌ Avoid when:
- Choosing without evals
- Using reasoning models for latency-critical simple tasks

---

## 📊 Visual Diagram
```
Quality / Cost
   ^
   |                          [ reasoning (o-series) ]  slow, costly, best on hard logic
   |                 [ gpt-4o ]                          strong, general
   |        [ gpt-4o-mini ]                              cheap, fast, good for 90% tasks
   |  [ embeddings / whisper / moderation ]              specialised, very cheap
   +------------------------------------------------------------> task difficulty

Router:  easy --> mini    ambiguous --> 4o    low confidence --> human review
```

---

## 💰 Cost Impact
- Price differences between tiers are large (often 10x or more per token). Model choice is your biggest cost lever.
- Example with the illustrative prices above: 100K classification calls of 800 in / 50 out cost about $15 on mini versus about $250 on 4o.
- Reasoning models also bill hidden reasoning tokens as output, so cost per call can be much higher than the visible answer suggests.
- Optimise: route by difficulty, cache, shorten prompts, use Batch API for offline work, and re-check pricing regularly.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| gpt-4o | Flagship multimodal model | Flagship multimodal model |
| gpt-4o-mini | Small, cheap model | छोटा, सस्ता model |
| Reasoning model | Thinks before answering | जवाब से पहले सोचने वाला model |
| Snapshot | Dated fixed model version | तारीख़ वाला fixed version |
| Router | Picks model per request | हर request के लिए model चुनने वाला |
| Eval set | Test examples with answers | जवाब के साथ test examples |

---

## ⚡ 3-Line Summary
English: OpenAI offers a ladder of models, from cheap mini to flagship and reasoning models. Pick by evaluating on your own data, and route easy tasks to the cheap model. Pin dated snapshots and re-check prices, because both change often.
Hindi: OpenAI cheap mini से flagship और reasoning तक models की सीढ़ी देता है। अपने data पर evaluate करके चुनो और आसान tasks सस्ते model को दो। Dated snapshots pin करो और prices दोबारा देखो, क्योंकि दोनों बदलते रहते हैं।

---

## ➡️ Next Topic
**028. OpenAI API — Sync vs Async Client** — how to serve many requests at once without blocking.
