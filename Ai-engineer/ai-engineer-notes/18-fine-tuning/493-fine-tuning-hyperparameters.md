---

# 493. Fine Tuning Hyperparameters
# हिंदी में: Fine Tuning Hyperparameters

---

## 🔵 Simple Definition (English)
Hyperparameters are settings you choose before training, not numbers the model learns. The main ones: number of epochs (passes over data), batch size (examples per update) and learning rate (step size of weight updates). Wrong values cause underfitting or overfitting.

## 🔵 सरल परिभाषा (Hindi)
Hyperparameters वे settings हैं जो आप training से पहले चुनते हैं, जिन्हें model खुद नहीं सीखता। मुख्य हैं: epochs (data पर कितने passes), batch size (हर update में कितने examples) और learning rate (weights update का step size)। गलत values से underfitting या overfitting होती है।

---

## 🔴 Problem it Solves
Too little training and the model barely changes (underfit). Too much or too aggressive training and it memorises the data and forgets general skills (overfit). Hyperparameters control this balance.

## 🔴 यह क्यों बना? (Hindi)
बहुत कम training में model लगभग बदलता ही नहीं (underfit)। बहुत ज़्यादा या आक्रामक training में वह data रट लेता है और general skills भूल जाता है (overfit)। Hyperparameters इस संतुलन को नियंत्रित करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Start with provider defaults (OpenAI picks automatically)
Step 2 → Train once and watch training vs validation loss
Step 3 → Both high and flat → underfit → more epochs / higher LR multiplier
Step 4 → Train loss falls, validation loss rises → overfit → fewer epochs / lower LR
Step 5 → Output too random or repetitive → lower LR, check data
Step 6 → Change ONE setting at a time and compare on the eval set
Step 7 → Keep the best run's settings in the experiment log
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Provider के defaults से शुरू करो (OpenAI खुद चुनता है)
Step 2 → एक बार train करो और training बनाम validation loss देखो
Step 3 → दोनों ऊँचे और सपाट → underfit → epochs बढ़ाओ / LR multiplier बढ़ाओ
Step 4 → Train loss घटे, validation loss बढ़े → overfit → epochs घटाओ / LR घटाओ
Step 5 → Output बहुत random या repetitive → LR घटाओ, data जाँचो
Step 6 → एक बार में सिर्फ़ एक setting बदलो और eval set पर compare करो
Step 7 → सबसे अच्छे run की settings experiment log में रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: First run with defaults gives 88 percent. Validation loss rises after epoch 2 while training loss keeps dropping: overfitting. We set `n_epochs=2` and accuracy becomes 91 percent. We do not touch other settings until we have a clean eval.

**Zomato-style**: A tag classifier with 300 examples tuned for 10 epochs memorises phrases; 3 epochs generalises better.

## 🟡 Real Example Hindi mein
**Tariff System**: Defaults के साथ पहला run 88 percent देता है। Epoch 2 के बाद validation loss बढ़ने लगता है जबकि training loss घटता रहता है: overfitting। हम `n_epochs=2` करते हैं और accuracy 91 percent हो जाती है। Clean eval मिलने तक बाकी settings नहीं छेड़ते।

**Zomato-style**: 300 examples पर 10 epochs का tag classifier phrases रट लेता है; 3 epochs में बेहतर generalise करता है।

---

## 💻 Code Example — Basic
```python
# Basic: detect overfitting from loss curves (pure Python, runs offline)
from typing import List, Optional  # type hints

train_loss: List[float] = [1.20, 0.80, 0.55, 0.35, 0.20]  # falls every epoch
val_loss: List[float] = [1.25, 0.90, 0.85, 0.95, 1.10]  # falls then rises


def best_epoch(val: List[float]) -> Optional[int]:
    """Return the 1-based epoch with the lowest validation loss."""
    if not val:  # empty input guard
        return None
    return min(range(len(val)), key=lambda i: val[i]) + 1  # index of min + 1


def overfitting(train: List[float], val: List[float]) -> bool:
    """True if train loss still improves while validation loss got worse than its best."""
    return train[-1] < train[0] and val[-1] > min(val)  # simple rule


print("best epoch:", best_epoch(val_loss))  # 3 in this example
print("overfitting:", overfitting(train_loss, val_loss))  # True
```

## 💻 Code Example — Advanced
```python
# Production style: async sweep over epochs using a pluggable trainer, with early stopping logic
import asyncio  # async
from dataclasses import dataclass  # config
from typing import Awaitable, Callable, Dict, List  # types


@dataclass
class HParams:
    n_epochs: int  # passes over data
    batch_size: int  # examples per update
    lr_multiplier: float  # scales the default learning rate


Trainer = Callable[[HParams], Awaitable[float]]  # returns validation score


async def sweep(trainer: Trainer, grid: List[HParams], concurrency: int = 2) -> Dict[str, float]:
    """Run several configs with limited parallelism and return scores by config name."""
    sem = asyncio.Semaphore(concurrency)  # limit parallel jobs (cost control)
    results: Dict[str, float] = {}  # name -> score

    async def run(h: HParams) -> None:
        async with sem:  # wait for a free slot
            try:
                score = await trainer(h)  # train and evaluate
            except Exception as exc:  # one failure should not kill the sweep
                print(f"failed {h}: {exc}")
                return
            results[f"e{h.n_epochs}_b{h.batch_size}_lr{h.lr_multiplier}"] = score  # save

    await asyncio.gather(*(run(h) for h in grid))  # run all
    return results


async def fake_trainer(h: HParams) -> float:
    """Stub: pretend 2 epochs is the sweet spot (replace with a real job + eval)."""
    await asyncio.sleep(0)  # yield
    return 0.9 - 0.02 * abs(h.n_epochs - 2) - 0.01 * abs(h.lr_multiplier - 1.0)


async def main() -> None:
    grid = [HParams(e, 8, lr) for e in (1, 2, 4) for lr in (0.5, 1.0)]  # small grid
    res = await sweep(fake_trainer, grid)  # run sweep
    best = max(res, key=res.get)  # best name
    print(best, round(res[best], 3))  # winner


if __name__ == "__main__":
    asyncio.run(main())  # demo
```

---

## 🟠 FastAPI Integration
Let an admin pass hyperparameters when starting a job, with validation limits to avoid runaway cost.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel, Field  # validation
from openai import AsyncOpenAI  # client

app = FastAPI()  # app
client = AsyncOpenAI()  # client


class TuneRequest(BaseModel):
    training_file: str  # uploaded file id
    n_epochs: int = Field(2, ge=1, le=5)  # keep epochs in a safe range
    batch_size: int | None = Field(None, ge=1, le=64)  # None means provider chooses
    learning_rate_multiplier: float | None = Field(None, gt=0, le=3)  # None means auto


@app.post("/admin/tune")
async def tune(req: TuneRequest) -> dict:
    hp = {"n_epochs": req.n_epochs}  # always send epochs
    if req.batch_size:
        hp["batch_size"] = req.batch_size  # only if set
    if req.learning_rate_multiplier:
        hp["learning_rate_multiplier"] = req.learning_rate_multiplier
    job = await client.fine_tuning.jobs.create(
        training_file=req.training_file, model="gpt-4o-mini-2024-07-18", hyperparameters=hp
    )
    return {"job_id": job.id}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain does not tune weights, but you can wrap a sweep as a LangGraph workflow: node 1 prepares data, node 2 launches jobs, node 3 evaluates, and a conditional edge loops to try new settings until the score is good or the budget ends.

```python
# Illustrative state machine for a tuning loop in LangGraph
def should_continue(state: dict) -> str:
    """Stop when quality is good or budget is spent."""
    if state["best_score"] >= 0.92 or state["spent"] >= state["budget"]:
        return "finish"  # end the loop
    return "try_next_config"  # run another experiment
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Changing many hyperparameters at once
✅ Correct: Change one at a time.

```python
# Wrong: epochs 2->6, LR x1->x3, batch 8->32 in one run (cannot tell what helped)
# Right: only n_epochs changes between run A and run B
```

❌ Mistake 2: Training with no validation file
✅ Correct: Always supply validation data so overfitting is visible.

```python
# Wrong: jobs.create(training_file=tid, model=base)
# Right: jobs.create(training_file=tid, validation_file=vid, model=base)
```

---

## 🧠 Tricky Interview Question
**Q**: "More epochs always means better results, right?"

**Answer**: No. After a point training loss keeps falling but validation loss rises: the model memorises. More epochs also cost more. On small datasets 2 to 4 epochs is common (illustrative); pick the epoch where validation loss is lowest, and prefer more clean data over more epochs.

---

## ⚫ Interview Questions + Answers

Q1: What is an epoch? (Easy)
A1: One full pass through the training dataset.

Q2: What is learning rate? (Easy)
A2: The step size of weight updates. Too big is unstable, too small is slow or does nothing.

Q3: What does batch size change? (Medium)
A3: Number of examples per weight update. Larger batches give smoother gradients but need more memory; smaller are noisier. Batch size interacts with learning rate.

Q4: How do you spot overfitting? (Medium)
A4: Training loss keeps going down while validation loss goes up, and held-out accuracy drops.

Q5: Which hyperparameters matter most in LoRA? (Hard)
A5: Rank `r`, `lora_alpha`, target modules, dropout, learning rate (often higher than full tuning, e.g. around 1e-4 to 2e-4, illustrative) and epochs. Rank controls capacity; alpha/r scales adapter influence.

---

## 🔷 When to Use + When Not to Use
✅ Tune hyperparameters when:
- Defaults give signs of over/underfitting
- You have a trusted eval set

❌ Avoid when:
- Data is bad (fix data first)
- Budget small and defaults already pass the bar

---

## 📊 Visual Diagram
```
 loss
  │\
  │ \___ train loss keeps falling
  │  \   ___________
  │   \_/           \____
  │     val loss ──╮      ╲
  │               ╰───────  rises  → overfit
  └──────────────────────────────► epochs
              ▲
        best epoch (stop here)
```

---

## 💰 Cost Impact
- Training cost scales with epochs: 4 epochs costs about twice 2 epochs (illustrative).
- Sweeps multiply cost: limit concurrency and test on a subset first.
- Token usage = dataset tokens x epochs.
- Optimise: use defaults first, early-stop by validation loss, tune only the one parameter that shows a problem.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Epoch | One pass over data | Data पर एक pass |
| Batch size | Examples per update | हर update में examples |
| Learning rate | Update step size | Update का step size |
| Overfitting | Memorising training data | Training data रटना |
| Underfitting | Not learning enough | कम सीखना |
| Validation loss | Loss on unseen data | अनदेखे data पर loss |

---

## ⚡ 3-Line Summary
English: Epochs, batch size and learning rate control how strongly the model is changed.
Watch training vs validation loss to detect overfitting.
Start with defaults and change one setting at a time.
Hindi: Epochs, batch size और learning rate तय करते हैं कि model कितना बदले।
Training बनाम validation loss देखकर overfitting पकड़ो।
Defaults से शुरू करो और एक बार में एक setting बदलो।

---

## ➡️ Next Topic
**494. Fine Tuning Cost Estimation** — computing training and serving cost before you start.
