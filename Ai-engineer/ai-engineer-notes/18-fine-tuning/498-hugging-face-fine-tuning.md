
# 498. Hugging Face Fine Tuning
# हिंदी में: Hugging Face Fine Tuning

---

## 🔵 Simple Definition (English)
Hugging Face gives you an open toolchain to fine-tune open-weight models: `datasets` (data), `transformers` (models, tokenizers, Trainer), `peft` (LoRA/QLoRA), `trl` (SFT, DPO trainers) and the Hub (store and share models). You own the weights and the training loop, unlike hosted fine-tuning APIs.

## 🔵 सरल परिभाषा (Hindi)
Hugging Face open-weight models को fine-tune करने का open toolchain देता है: `datasets` (data), `transformers` (models, tokenizers, Trainer), `peft` (LoRA/QLoRA), `trl` (SFT, DPO trainers) और Hub (models store/share)। Weights और training loop आपके पास रहते हैं, hosted fine-tuning API की तरह नहीं।

---

## 🔴 Problem it Solves
Hosted fine-tuning APIs only work with the vendor's models, hide the weights and set price and data-residency rules. Customs data may not be allowed to leave your network. Writing a training loop from scratch (tokenizing, batching, mixed precision, checkpoints, distributed training) is slow and error-prone. Hugging Face standardises all of it.

## 🔴 यह क्यों बना? (Hindi)
Hosted APIs सिर्फ़ vendor के models पर चलती हैं, weights छुपाती हैं और price/data-residency vendor तय करता है। Customs data network से बाहर न जा सके, ऐसा हो सकता है। Training loop scratch से लिखना (tokenizing, batching, mixed precision, checkpoints) धीमा और error-prone है। Hugging Face यह सब standardise करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Prepare data as JSONL (messages or prompt/completion) and load with datasets.load_dataset
Step 2 → Load tokenizer + base model (optionally 4-bit for QLoRA)
Step 3 → Format examples with the model's chat template
Step 4 → Wrap model with a LoraConfig (peft)
Step 5 → Configure trainer (TrainingArguments / trl SFTConfig): lr, epochs, batch, eval steps
Step 6 → trainer.train() -> checkpoints and logs (loss curves)
Step 7 → Evaluate on a held-out set, then save adapter (or merge) and push to the Hub / registry
Step 8 → Serve with vLLM / TGI / transformers pipeline
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Data JSONL में तैयार करो और datasets.load_dataset से load करो
Step 2 → Tokenizer + base model load करो (QLoRA के लिए 4-bit optional)
Step 3 → Model के chat template से examples format करो
Step 4 → Model को LoraConfig (peft) से wrap करो
Step 5 → Trainer configure करो: lr, epochs, batch, eval steps
Step 6 → trainer.train() -> checkpoints और loss logs
Step 7 → Held-out set पर evaluate करो, adapter save/merge करो और Hub/registry में push करो
Step 8 → vLLM / TGI / transformers pipeline से serve करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Customs rulings cannot leave the company VPC. The team builds `tariff_train.jsonl` from 10,000 historical rulings, fine-tunes an open 8B model with LoRA using `trl`'s `SFTTrainer`, evaluates exact-match on the 6-digit HS code, and pushes the adapter to a private Hub repo.

**Zomato AI**: Fine-tune a small open model to extract dish, spice level and allergens from messy review text, then run it in-house to avoid per-token API fees.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs rulings company VPC से बाहर नहीं जा सकतीं। Team 10,000 पुरानी rulings से `tariff_train.jsonl` बनाती है, `trl` के `SFTTrainer` से open 8B model को LoRA से fine-tune करती है, 6-digit HS code पर exact-match evaluate करती है और adapter private Hub repo में push करती है।

**Zomato AI**: Review text से dish, spice level और allergens निकालने के लिए छोटा open model fine-tune करो और in-house चलाओ, ताकि per-token API fee न लगे।

---

## 💻 Code Example — Basic
```python
# Pure-Python data prep for HF fine-tuning: build a chat-format JSONL (no HF install needed)
import json  # write JSONL
from pathlib import Path  # file handling
from typing import Iterable  # type hints

SYSTEM = "You are a customs tariff classifier. Reply with JSON."  # system message


def to_example(description: str, hs_code: str) -> dict:
    """Turn one labelled row into the chat 'messages' format."""
    return {
        "messages": [
            {"role": "system", "content": SYSTEM},  # fixed instruction
            {"role": "user", "content": description},  # product text
            {"role": "assistant", "content": json.dumps({"hs_code": hs_code})},  # target answer
        ]
    }


def write_jsonl(rows: Iterable[tuple[str, str]], path: Path) -> int:
    """Write rows to JSONL and return how many were written."""
    count = 0  # counter
    with path.open("w", encoding="utf-8") as f:  # open file for writing
        for desc, code in rows:  # loop over labelled rows
            f.write(json.dumps(to_example(desc, code), ensure_ascii=False) + "\n")  # one JSON per line
            count += 1  # increment
    return count  # total examples


if __name__ == "__main__":
    data = [("Wireless earbuds", "8518.30"), ("Cotton t-shirt", "6109.10")]  # tiny sample
    n = write_jsonl(data, Path("tariff_train.jsonl"))  # write to current dir
    print(f"wrote {n} examples")  # confirm
```

## 💻 Code Example — Advanced
```python
# LoRA SFT with trl + peft + datasets (pip install transformers datasets peft trl accelerate)
# trl's API changes between versions: treat argument names as illustrative and check your version's docs.
import asyncio  # async wrapper
import logging  # logging

from datasets import load_dataset  # dataset loader
from peft import LoraConfig  # LoRA settings
from trl import SFTConfig, SFTTrainer  # supervised fine-tuning trainer

logger = logging.getLogger("hf-ft")  # logger


def train(model_id: str, data_path: str, out_dir: str) -> str:
    """Fine-tune with LoRA and return the output directory."""
    try:
        ds = load_dataset("json", data_files=data_path, split="train")  # read JSONL
    except FileNotFoundError as exc:  # missing data file
        logger.error("data missing: %s", exc)  # log
        raise  # re-raise
    split = ds.train_test_split(test_size=0.1, seed=42)  # hold out 10% for eval
    cfg = SFTConfig(
        output_dir=out_dir,  # where checkpoints go
        num_train_epochs=2,  # keep epochs low to avoid overfitting
        per_device_train_batch_size=4,  # micro batch
        gradient_accumulation_steps=4,  # effective batch = 16
        learning_rate=2e-4,  # typical LoRA learning rate
        logging_steps=10,  # log loss often
        eval_strategy="steps",  # evaluate during training
        eval_steps=100,  # every 100 steps
        bf16=True,  # mixed precision on modern GPUs
    )
    trainer = SFTTrainer(
        model=model_id,  # trl can load from the id string
        args=cfg,  # training config
        train_dataset=split["train"],  # training split
        eval_dataset=split["test"],  # eval split
        peft_config=LoraConfig(r=16, lora_alpha=32, target_modules="all-linear", task_type="CAUSAL_LM"),
    )
    trainer.train()  # run training
    trainer.save_model(out_dir)  # save adapter
    return out_dir  # path to artifacts


async def train_async(model_id: str, data_path: str, out_dir: str) -> str:
    """Run blocking training off the event loop."""
    return await asyncio.to_thread(train, model_id, data_path, out_dir)  # thread offload
```
Token usage: training tokens = sum of tokens per example x epochs. Count them with the model's tokenizer before launching.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel  # validation
from transformers import pipeline  # inference helper

app = FastAPI()  # app
generator = None  # loaded at startup


@app.on_event("startup")  # older style hook; lifespan is preferred in new code
async def load() -> None:
    global generator  # module-level cache
    # generator = pipeline("text-generation", model="./out/tariff-merged")  # illustrative path


class Req(BaseModel):
    description: str  # product text


@app.post("/classify")
async def classify(req: Req) -> dict:
    if generator is None:  # model not loaded
        raise HTTPException(status_code=503, detail="model not loaded")  # service unavailable
    out = generator(req.description, max_new_tokens=64)  # cap output tokens
    return {"raw": out[0]["generated_text"]}  # return text
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has `HuggingFacePipeline` and `ChatHuggingFace` (package `langchain-huggingface`) for local models, or point `ChatOpenAI` at a vLLM server hosting your adapter. In LangGraph the tuned model becomes one node, with a fallback edge to a larger model when confidence is low.

```python
from langchain_huggingface import HuggingFacePipeline  # local HF model wrapper

llm = HuggingFacePipeline.from_model_id(
    model_id="./out/tariff-merged",  # your fine-tuned model (illustrative path)
    task="text-generation",  # pipeline task
    pipeline_kwargs={"max_new_tokens": 64},  # cap output
)
print(llm.invoke("Classify: running shoes"))  # standard LangChain call
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Ignoring the chat template and hand-building prompt strings
✅ Correct: Use `tokenizer.apply_chat_template` (or let `SFTTrainer` do it) so training matches inference format.
```python
# Wrong: "### Question: ... ### Answer:" at train time, but chat format at serve time
# Right:
# text = tokenizer.apply_chat_template(messages, tokenize=False)
```

❌ Mistake 2: No held-out evaluation, trusting training loss
✅ Correct: Split data, track eval loss and a task metric (exact-match HS code).
```python
# Wrong: trainer = SFTTrainer(..., train_dataset=ds)  # no eval
# Right: split = ds.train_test_split(0.1); pass eval_dataset=split["test"]
```

---

## 🧠 Tricky Interview Question
**Q**: "Training loss keeps falling, but production accuracy on new HS codes is worse than the base model with a prompt. What happened?"

**Answer**: Overfitting or data leakage/skew: the model memorised training rows (or duplicates leaked into eval), and fine-tuning may have caused forgetting of general ability. Check dedup between train/eval, use a time-based or product-family split, lower epochs or learning rate, lower LoRA rank, mix in general instruction data, and compare against the prompt baseline on the same held-out set before shipping.

---

## ⚫ Interview Questions + Answers

Q1: Which Hugging Face libraries are used for fine-tuning?
A1: `transformers` (models, Trainer), `datasets`, `peft` (LoRA/QLoRA), `trl` (SFT/DPO trainers), `accelerate` (multi-GPU), plus the Hub for storage.

Q2: What is a chat template?
A2: A per-model format that turns a list of messages into the exact token string with special tokens. Training and inference must use the same one.

Q3: Why use gradient accumulation?
A3: To get a large effective batch size on limited memory by summing gradients over several small batches before updating.

Q4: How do you save and reuse a LoRA result?
A4: `save_pretrained` saves the adapter; load with `PeftModel.from_pretrained(base, path)`, or merge with `merge_and_unload()` for a standalone model.

Q5: How would you decide between hosted fine-tuning and Hugging Face open models?
A5: Compare data-privacy needs, quality on my eval set, per-token and GPU costs at expected volume, ops skill, and latency. Hosted is faster to start; open models give control, privacy and lower unit cost at scale but need MLOps.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Data must stay in your network
- You want control over weights, serving and cost
- You need open models, DPO, custom training

❌ Avoid when:
- A hosted fine-tuning API meets quality and privacy needs with less effort
- You lack GPUs and MLOps skills
- Prompting/RAG is enough

---

## 📊 Visual Diagram
```
 JSONL data --> datasets --> tokenizer + chat template
                                   |
 base model (4/16-bit) --> peft LoRA --> SFTTrainer --> checkpoints
                                                |
                                          eval on held-out
                                                |
                              adapter --> Hub / registry --> vLLM serve
```

---

## 💰 Cost Impact
Costs = GPU hours + engineering time; no per-token vendor fee for training or inference if self-hosted (illustrative). Example: 10,000 examples x 350 tokens x 2 epochs = 7M tokens.

Optimise: use QLoRA on smaller GPUs, cap max sequence length, deduplicate data, use spot instances with checkpointing, stop early on eval plateau, and cache tokenized datasets. At serve time a tuned small model can remove long few-shot prompts, saving input tokens per call.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| transformers | Core model library | मुख्य model library |
| datasets | Data loading library | Data load करने की library |
| peft | Parameter-efficient tuning | कम parameters की tuning |
| trl | Trainers for SFT/DPO/RLHF | SFT/DPO/RLHF trainers |
| Chat template | Message to token format | Messages को tokens का format |
| Hub | Model hosting platform | Models रखने का platform |
| Gradient accumulation | Combine small batches | छोटे batches जोड़ना |

---

## ⚡ 3-Line Summary
English: Hugging Face gives datasets, transformers, peft and trl to fine-tune open models you control. Prepare chat-format JSONL, use LoRA with SFTTrainer, and always evaluate on held-out data. Best when privacy and unit cost matter.
Hindi: Hugging Face datasets, transformers, peft और trl देता है ताकि आप अपने control वाले open models fine-tune करें। Chat-format JSONL बनाओ, SFTTrainer के साथ LoRA use करो और हमेशा held-out data पर evaluate करो। Privacy और unit cost important हो तो best।

---

## ➡️ Next Topic
**499. Supervised Fine Tuning (SFT)** — what SFT really is, how loss masking works and how to build good instruction data.
