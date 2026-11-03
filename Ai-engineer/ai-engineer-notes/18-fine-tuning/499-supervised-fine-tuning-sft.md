
# 499. Supervised Fine Tuning (SFT)
# हिंदी में: Supervised Fine Tuning (SFT)

---

## 🔵 Simple Definition (English)
SFT trains a pre-trained model on labelled examples of input and the ideal output ("when asked this, answer like that"). The model learns by imitation using the normal next-token loss, usually only on the answer tokens. It is the first and most common step to make a base model follow instructions or a house style.

## 🔵 सरल परिभाषा (Hindi)
SFT में pre-trained model को labelled examples पर train करते हैं: input और ideal output ("यह पूछा जाए तो ऐसे जवाब दो")। Model नक़ल करके सीखता है, normal next-token loss से, आमतौर पर सिर्फ़ answer tokens पर। Base model को instructions या house style follow कराने का यह पहला और सबसे common step है।

---

## 🔴 Problem it Solves
A pre-trained base model only predicts the next token; it does not reliably follow instructions, answer in JSON, or stay in a persona. Prompting can help but costs tokens every call and is brittle. SFT bakes the desired behaviour into the weights using curated demonstrations.

## 🔴 यह क्यों बना? (Hindi)
Pre-trained base model सिर्फ़ अगला token predict करता है; वह instructions, JSON format या persona भरोसे से follow नहीं करता। Prompting मदद करती है पर हर call पर tokens लगते हैं और fragile है। SFT curated demonstrations से यह behaviour weights में बैठा देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Collect high-quality (prompt, ideal response) pairs
Step 2 → Format with the chat template: system + user + assistant turns
Step 3 → Tokenize and build labels; mask prompt tokens (label = -100) so loss counts only the answer
Step 4 → Forward pass: model predicts next token at every position
Step 5 → Cross-entropy loss on answer tokens only
Step 6 → Backprop + optimizer step (full weights or LoRA adapters)
Step 7 → Repeat for 1-3 epochs, monitor eval loss
Step 8 → Evaluate on held-out tasks, compare with prompt baseline
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → High-quality (prompt, ideal response) pairs जमा करो
Step 2 → Chat template से format करो: system + user + assistant
Step 3 → Tokenize करो और labels बनाओ; prompt tokens mask (label = -100) ताकि loss सिर्फ़ answer पर हो
Step 4 → Forward pass: हर position पर अगला token predict
Step 5 → सिर्फ़ answer tokens पर cross-entropy loss
Step 6 → Backprop + optimizer step (full weights या LoRA)
Step 7 → 1-3 epochs दोहराओ, eval loss देखो
Step 8 → Held-out tasks पर evaluate करो, prompt baseline से compare करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Base model answers tariff questions in rambling prose. SFT data: 6,000 pairs of product description to `{"hs_code": "...", "reason": "..."}` written or verified by customs experts. After SFT the model returns valid JSON 99% of the time without a long format prompt, saving about 400 input tokens per request.

**Amazon-style support bot**: SFT on past agent replies teaches the brand tone and refund policy phrasing.

## 🟡 Real Example Hindi mein
**Tariff System**: Base model tariff सवालों के जवाब लंबे prose में देता है। SFT data: customs experts द्वारा लिखे/verified 6,000 pairs: product description से `{"hs_code": "...", "reason": "..."}`। SFT के बाद model लंबे format prompt के बिना 99% valid JSON देता है, यानी हर request पर लगभग 400 input tokens की बचत।

**Amazon-style support bot**: पुराने agent replies पर SFT से brand tone और refund policy की भाषा सीखता है।

---

## 💻 Code Example — Basic
```python
# Pure-Python demo of SFT label masking (the core idea), no ML libraries
from typing import List, Tuple  # type hints

IGNORE = -100  # label value that the loss function skips


def build_labels(prompt_ids: List[int], answer_ids: List[int]) -> Tuple[List[int], List[int]]:
    """Return input_ids and labels where the prompt part is masked."""
    input_ids = prompt_ids + answer_ids  # model sees prompt then answer
    labels = [IGNORE] * len(prompt_ids) + answer_ids  # loss only on the answer
    if len(input_ids) != len(labels):  # sanity check
        raise ValueError("length mismatch")  # should never happen
    return input_ids, labels  # ready for training


if __name__ == "__main__":
    ids, labels = build_labels([11, 12, 13], [21, 22])  # fake token ids
    print(ids)  # [11, 12, 13, 21, 22]
    print(labels)  # [-100, -100, -100, 21, 22]
```

## 💻 Code Example — Advanced
```python
# Data validation + SFT launch helper (production style)
import asyncio  # async wrapper
import json  # parse JSONL
import logging  # logging
from pathlib import Path  # paths

logger = logging.getLogger("sft")  # logger
VALID_ROLES = {"system", "user", "assistant"}  # allowed roles


def validate_jsonl(path: Path, max_chars: int = 8000) -> dict[str, int]:
    """Check an SFT JSONL file; return counts of good and bad rows."""
    good = bad = 0  # counters
    seen: set[str] = set()  # for duplicate detection
    with path.open(encoding="utf-8") as f:  # open the file
        for line_no, line in enumerate(f, 1):  # iterate rows
            try:
                row = json.loads(line)  # parse JSON
                msgs = row["messages"]  # required key
                roles_ok = all(m["role"] in VALID_ROLES for m in msgs)  # role check
                ends_ok = msgs[-1]["role"] == "assistant"  # last turn is the target
                size_ok = sum(len(m["content"]) for m in msgs) <= max_chars  # length cap
                key = json.dumps(msgs, sort_keys=True)  # dedup key
                if roles_ok and ends_ok and size_ok and key not in seen:  # all checks pass
                    seen.add(key)  # remember
                    good += 1  # count good
                else:
                    bad += 1  # count bad
            except (json.JSONDecodeError, KeyError, IndexError, TypeError):  # malformed row
                logger.warning("bad row %d", line_no)  # log position
                bad += 1  # count bad
    return {"good": good, "bad": bad}  # summary


async def validate_async(path: Path) -> dict[str, int]:
    """Async wrapper (file IO runs in a thread)."""
    return await asyncio.to_thread(validate_jsonl, path)  # offload
```
To train, feed the validated file to `trl.SFTTrainer` (see topic 498). Token usage: count tokens per example with the model tokenizer; training cost scales with total tokens x epochs.

---

## 🟠 FastAPI Integration
Add a data-quality gate endpoint so bad files never reach the GPU.

```python
from pathlib import Path  # path handling
from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel  # validation

app = FastAPI()  # app


class Check(BaseModel):
    path: str  # dataset path on the server


@app.post("/sft/validate")
async def validate(req: Check) -> dict:
    p = Path(req.path)  # build path
    if not p.exists():  # missing file
        raise HTTPException(status_code=404, detail="file not found")  # 404
    # result = await validate_async(p)  # call validator from the advanced example
    result = {"good": 0, "bad": 0}  # placeholder so the route is runnable
    return result  # return counts
```

---

## 🔗 LangChain / LangGraph Connection
LangSmith datasets (topic 423) can store reviewed production traces; export the thumbs-up ones as SFT data. In LangGraph, human-corrected outputs from a review node become new SFT rows (a data flywheel).

```python
# Convert reviewed examples into SFT chat rows
def to_sft(question: str, corrected_answer: str) -> dict:
    return {"messages": [  # chat format
        {"role": "user", "content": question},  # input
        {"role": "assistant", "content": corrected_answer},  # human-verified answer
    ]}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Training on noisy or inconsistent labels
✅ Correct: 1,000 clean examples beat 20,000 messy ones. Review, dedupe, and keep format consistent.
```python
# Wrong: scrape all old agent replies, including wrong ones
# Right: filter by expert approval flag
rows = [r for r in rows if r.get("approved")]
```

❌ Mistake 2: Too many epochs / high learning rate causing forgetting
✅ Correct: 1-3 epochs, watch eval loss, mix in general data.
```python
# Wrong: num_train_epochs=10, learning_rate=1e-3
# Right: num_train_epochs=2, learning_rate=2e-4 (LoRA) or ~1e-5 (full)
```

---

## 🧠 Tricky Interview Question
**Q**: "After SFT your model follows the format perfectly but invents HS codes confidently. Did SFT fail?"

**Answer**: No, SFT taught form, not facts. It makes the model imitate the answer style, and imitation of confident answers can increase hallucination if the data does not include "I don't know" cases or if the facts are not in the model. Fix with RAG (ground answers on the tariff schedule), include refusal/uncertain examples in the SFT data, and add validators that check codes against the official code list.

---

## ⚫ Interview Questions + Answers

Q1: What is SFT?
A1: Fine-tuning on (input, ideal output) pairs with next-token cross-entropy loss.

Q2: Why mask the prompt tokens?
A2: So the model is trained to produce answers, not to reproduce the questions; loss is computed only on the response tokens.

Q3: SFT vs RLHF?
A3: SFT imitates fixed demonstrations. RLHF/DPO optimises against preference signals (which of two answers is better), shaping behaviour beyond imitation.

Q4: How much data do I need?
A4: Often hundreds to a few thousand high-quality examples for style/format tasks; more for complex reasoning. Quality and diversity matter more than count.

Q5: How would you measure whether SFT was worth it?
A5: Build a held-out eval set, compare SFT model vs best prompt (and RAG) baseline on accuracy, format validity, latency and cost per request. Include a regression set of general tasks to detect forgetting. Ship only if the gain beats the added maintenance.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need a consistent format, tone or task behaviour
- You have good labelled examples
- Long prompts are costing too many tokens

❌ Avoid when:
- You need up-to-date facts (use RAG)
- You have few or noisy examples
- Prompt engineering already reaches the target

---

## 📊 Visual Diagram
```
 (prompt, answer) pairs
        |
   chat template
        |
 tokens:  [ system | user ..... | assistant answer ]
 labels:  [ -100   | -100 ..... | answer tokens    ]   <- loss only here
        |
   next-token cross-entropy -> update weights/adapters
        |
   SFT model (follows format)
```

---

## 💰 Cost Impact
Training tokens = total example tokens x epochs. Example: 6,000 x 500 tokens x 2 = 6M tokens. Hosted APIs bill per training token (check current price); self-hosting bills GPU hours.

Optimise: dedupe data, trim system prompts in examples, use LoRA, early stop. Payoff: removing a 400-token instruction block over 1M requests saves 400M input tokens (at an illustrative $0.15/1M that is about $60; at higher-priced models much more).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SFT | Train on input/output demos | Demos पर training |
| Label masking | Ignore prompt in loss | Prompt को loss से हटाना |
| -100 | Ignore index for loss | Loss ignore करने वाला value |
| Epoch | One pass over data | Data पर एक पूरा pass |
| Catastrophic forgetting | Loses old skills | पुरानी skills भूल जाना |
| Instruction data | Prompt/answer pairs | Prompt/answer pairs |
| Eval set | Held-out test data | अलग रखा test data |

---

## ⚡ 3-Line Summary
English: SFT teaches a model by imitation on labelled prompt-answer pairs, with loss on answer tokens only. It fixes format and style, not missing knowledge. Data quality matters more than quantity.
Hindi: SFT labelled prompt-answer pairs की नक़ल से model सिखाता है, loss सिर्फ़ answer tokens पर। यह format और style ठीक करता है, missing knowledge नहीं। Data की quality quantity से ज़्यादा ज़रूरी है।

---

## ➡️ Next Topic
**500. RLHF Basics** — how human preference feedback goes beyond imitation to align model behaviour.
