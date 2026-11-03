---

# 494. Fine Tuning Cost Estimation
# हिंदी में: Fine Tuning की Cost का अनुमान

---

## 🔵 Simple Definition (English)
Cost estimation means calculating, before you train, how much training will cost (tokens x epochs x price) and how much serving will cost afterwards. All prices in this note are illustrative; always read the provider's current pricing page.

## 🔵 सरल परिभाषा (Hindi)
Cost estimation का मतलब training से पहले यह हिसाब लगाना है कि training कितनी महँगी होगी (tokens x epochs x price) और बाद में serving कितनी। इस note की सारी prices illustrative हैं; हमेशा provider का current pricing page पढ़ें।

---

## 🔴 Problem it Solves
Surprise bills. A dataset with long system prompts repeated in 50,000 rows and 4 epochs can silently cost hundreds of dollars. Estimating first lets you decide go/no-go and compute break-even.

## 🔴 यह क्यों बना? (Hindi)
अचानक आने वाले बिल। 50,000 rows में दोहराए गए लंबे system prompts और 4 epochs वाला dataset चुपचाप सैकड़ों डॉलर खर्च कर सकता है। पहले अनुमान लगाने से आप go/no-go तय कर सकते हैं और break-even निकाल सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Count tokens of every training row with tiktoken
Step 2 → Total training tokens = sum(row tokens) x n_epochs
Step 3 → Training cost = total training tokens / 1M x price per 1M training tokens
Step 4 → Serving cost/call = in_tokens x tuned_in_price + out_tokens x tuned_out_price
Step 5 → Compare with current setup (base model + long prompt)
Step 6 → Monthly saving = (old cost per call - new cost per call) x calls
Step 7 → Break-even months = training cost / monthly saving
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर training row के tokens tiktoken से गिनो
Step 2 → कुल training tokens = sum(row tokens) x n_epochs
Step 3 → Training cost = कुल training tokens / 1M x price per 1M training tokens
Step 4 → Serving cost/call = in_tokens x tuned_in_price + out_tokens x tuned_out_price
Step 5 → मौजूदा setup (base model + लंबा prompt) से तुलना करो
Step 6 → Monthly saving = (पुरानी cost/call - नई cost/call) x calls
Step 7 → Break-even months = training cost / monthly saving
```

---

## 🟡 Real World Example
**Tariff Classification System** (all numbers illustrative): 20,000 rows x 120 tokens = 2.4M tokens per epoch. With 3 epochs = 7.2M training tokens. If training costs $3 per 1M tokens, training is about $21.6. Current prompt 900 tokens on a bigger model; the tuned small model needs 40 tokens. With 1M calls a month the saving is far larger than $21.6, so break-even is under a month.

**Amazon-style**: At only 10,000 calls a month, the same training spend could take years to repay, so do not tune for cost reasons.

## 🟡 Real Example Hindi mein
**Tariff System** (सारे numbers illustrative): 20,000 rows x 120 tokens = प्रति epoch 2.4M tokens। 3 epochs = 7.2M training tokens। अगर training $3 प्रति 1M tokens है तो training लगभग $21.6 की है। अभी prompt 900 tokens का है और बड़े model पर चलता है; tuned छोटे model को 40 tokens चाहिए। महीने के 10 लाख calls पर बचत $21.6 से बहुत ज़्यादा है, इसलिए break-even एक महीने से कम है।

**Amazon-style**: महीने में सिर्फ़ 10,000 calls पर वही खर्च सालों में वसूल होगा, इसलिए cost की वजह से tune मत करो।

---

## 💻 Code Example — Basic
```python
# Basic: estimate training cost from token counts (pure Python, illustrative prices)
from typing import List  # type hints


def approx_tokens(text: str) -> int:
    """Rough token estimate, about 4 chars per token. Use tiktoken in real work."""
    return max(1, len(text) // 4)


rows: List[str] = ["Classify: Bluetooth headphones -> 8518.30"] * 1000  # 1000 example rows
epochs: int = 3  # number of passes
price_per_m: float = 3.00  # illustrative $ per 1M training tokens

tokens_per_epoch: int = sum(approx_tokens(r) for r in rows)  # tokens in one pass
total_tokens: int = tokens_per_epoch * epochs  # all epochs
cost: float = total_tokens / 1_000_000 * price_per_m  # dollars

print(f"tokens per epoch: {tokens_per_epoch}")  # show size
print(f"total training tokens: {total_tokens}")  # show total
print(f"estimated training cost: ${cost:.4f} (illustrative)")  # show cost
```

## 💻 Code Example — Advanced
```python
# Production style: full cost model with break-even, input validation and async wrapper
import asyncio  # async
from dataclasses import dataclass  # config
from typing import Optional  # types


@dataclass(frozen=True)
class Prices:
    train_per_m: float  # $ per 1M training tokens
    old_in_per_m: float  # current model input $ per 1M
    old_out_per_m: float  # current model output $ per 1M
    new_in_per_m: float  # tuned model input $ per 1M
    new_out_per_m: float  # tuned model output $ per 1M


@dataclass(frozen=True)
class Plan:
    train_tokens_per_epoch: int  # dataset size in tokens
    epochs: int  # passes
    calls_per_month: int  # traffic
    old_in: int  # current prompt tokens
    new_in: int  # tuned prompt tokens
    out_tokens: int  # output tokens per call


def estimate(p: Plan, pr: Prices) -> dict:
    """Return training cost, monthly costs and break-even months."""
    if min(p.train_tokens_per_epoch, p.epochs, p.calls_per_month) <= 0:  # validate
        raise ValueError("tokens, epochs and calls must be positive")
    training = p.train_tokens_per_epoch * p.epochs / 1e6 * pr.train_per_m  # one time
    old_call = p.old_in / 1e6 * pr.old_in_per_m + p.out_tokens / 1e6 * pr.old_out_per_m
    new_call = p.new_in / 1e6 * pr.new_in_per_m + p.out_tokens / 1e6 * pr.new_out_per_m
    saving = (old_call - new_call) * p.calls_per_month  # per month
    be: Optional[float] = training / saving if saving > 0 else None  # months
    return {
        "training_usd": round(training, 2),
        "old_monthly_usd": round(old_call * p.calls_per_month, 2),
        "new_monthly_usd": round(new_call * p.calls_per_month, 2),
        "break_even_months": None if be is None else round(be, 2),
    }


async def estimate_async(p: Plan, pr: Prices) -> dict:
    """Async wrapper for use inside web routes."""
    return await asyncio.to_thread(estimate, p, pr)  # run in a worker thread


if __name__ == "__main__":
    prices = Prices(3.0, 2.5, 10.0, 0.30, 1.20)  # all illustrative
    plan = Plan(2_400_000, 3, 1_000_000, 900, 40, 40)  # tariff example
    print(asyncio.run(estimate_async(plan, prices)))  # demo
```

---

## 🟠 FastAPI Integration
A cost calculator endpoint that product managers can call before approving a training run.

```python
import tiktoken  # exact token counting (pip install tiktoken)
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # schema
from typing import List  # types

app = FastAPI()  # app
enc = tiktoken.get_encoding("o200k_base")  # encoding used by recent OpenAI models


class CostRequest(BaseModel):
    rows: List[str]  # example rows as plain text
    epochs: int = 3  # epochs
    price_per_m: float  # $ per 1M training tokens (read from the pricing page)


@app.post("/finetune/cost")
async def cost(req: CostRequest) -> dict:
    if not req.rows:  # guard
        raise HTTPException(422, "rows must not be empty")
    per_epoch = sum(len(enc.encode(r)) for r in req.rows)  # exact tokens
    total = per_epoch * req.epochs  # all epochs
    return {"tokens_per_epoch": per_epoch, "total_tokens": total,
            "estimated_usd": round(total / 1e6 * req.price_per_m, 4)}
```

---

## 🔗 LangChain / LangGraph Connection
For serving cost, LangChain callbacks and LangSmith report token usage per run, so you can measure the real prompt size and compare before/after tuning.

```python
# Illustrative: read usage from a LangChain response
# msg = await llm.ainvoke("Classify: Bluetooth headphones")
# print(msg.usage_metadata)   # {'input_tokens': ..., 'output_tokens': ..., 'total_tokens': ...}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting epochs in the estimate
✅ Correct: Multiply dataset tokens by epochs.

```python
# Wrong: cost = dataset_tokens / 1e6 * price
# Right: cost = dataset_tokens * epochs / 1e6 * price
```

❌ Mistake 2: Comparing only per-token price
✅ Correct: Compare cost per call including prompt length.

```python
# Wrong: "tuned model costs more per token, so it is more expensive"
# Right: 40-token prompt on tuned small model < 900-token prompt on a big model
```

---

## 🧠 Tricky Interview Question
**Q**: "The tuned model has a higher per-token price than the base model. How can the total bill go down?"

**Answer**: The bill is tokens x price. Fine tuning removes long instructions and few-shot examples, so input tokens per call drop sharply, and a small tuned model can replace a much larger one. If tokens drop 20x while price rises 2x, cost falls about 10x. Always compare cost per request, not price per token, and include the one time training cost.

---

## ⚫ Interview Questions + Answers

Q1: Formula for training cost? (Easy)
A1: Dataset tokens x epochs x price per training token.

Q2: Why do system prompts matter for training cost? (Easy)
A2: The same system prompt is counted in every row and every epoch.

Q3: What is break-even? (Medium)
A3: Training cost divided by monthly savings; the time to repay the investment.

Q4: What hidden costs exist? (Medium)
A4: Data labelling, evaluation runs, retraining when base models retire or data drifts, engineering time, and hosting costs for self-hosted models.

Q5: How would you cut cost without losing quality? (Hard)
A5: Dedupe data, shorten system prompt, pick the smallest viable base model, use LoRA/QLoRA for open models, early stop by validation loss, and route easy requests to the tuned small model with hard ones to a bigger model.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Before every training run and before every approval

❌ Avoid when:
- Never skip; but do not rely on stale prices

---

## 📊 Visual Diagram
```
 Dataset tokens ─┐
 Epochs ─────────┼─► Training cost (one time)
 Train price ────┘
                                   ┐
 Old cost/call ─┐                  │
 New cost/call ─┴─► Saving/month ──┴─► Break-even = Training / Saving
 Calls/month ──────►
```

---

## 💰 Cost Impact
- This whole topic is cost. Key levers: shorter prompts, fewer epochs, smaller model, cleaner data.
- Illustrative example: 7.2M training tokens at $3 per 1M is $21.6.
- Serving: 900 to 40 input tokens saves 860 tokens per call; at 1M calls that is 860M input tokens a month.
- Re-estimate when prices change; verify on the provider's page.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Training tokens | Tokens processed in training | Training में process हुए tokens |
| Break-even | When savings repay cost | जब बचत लागत चुका दे |
| Serving cost | Cost of using the model | Model चलाने की लागत |
| Epoch multiplier | Tokens multiply by epochs | Epochs से tokens गुणा |
| tiktoken | OpenAI token counter | Token गिनने की library |
| Illustrative | Example, not real price | उदाहरण, असली price नहीं |

---

## ⚡ 3-Line Summary
English: Training cost is tokens x epochs x price; serving cost depends on tokens per call.
Compute break-even using monthly savings from shorter prompts and smaller models.
Always use current prices from the provider.
Hindi: Training cost = tokens x epochs x price; serving cost हर call के tokens पर निर्भर है।
छोटे prompts और छोटे models की monthly बचत से break-even निकालो।
हमेशा provider की current prices use करो।

---

## ➡️ Next Topic
**495. Fine Tuning Evaluation** — proving the tuned model is actually better.
