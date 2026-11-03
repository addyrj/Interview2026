
# 496. LoRA — What + Why
# हिंदी में: LoRA — क्या है और क्यों

---

## 🔵 Simple Definition (English)
LoRA (Low-Rank Adaptation) fine-tunes a big model by freezing all original weights and training only two tiny matrices (A and B) added next to selected layers. The model learns a small "delta" instead of changing billions of numbers. The result is a small adapter file (often a few MB to a few hundred MB) that you can load on top of the base model.

## 🔵 सरल परिभाषा (Hindi)
LoRA (Low-Rank Adaptation) में बड़े model के सारे original weights freeze रहते हैं और सिर्फ़ दो छोटे matrices (A और B) train होते हैं जो selected layers के साथ जुड़ते हैं। Billions of numbers बदलने की जगह model एक छोटा "delta" सीखता है। Output एक छोटी adapter file होती है जिसे base model के ऊपर load किया जाता है।

---

## 🔴 Problem it Solves
Full fine-tuning updates every weight. For a 7B model in 16-bit that means about 14 GB for weights, plus gradients and optimizer states (Adam needs roughly 2 more copies), so you need several GPUs. Each task also produces a full 14 GB copy of the model. This is slow, expensive and hard to serve for many customers.

LoRA trains well under 1% of the parameters, needs far less GPU memory, and each task is just a small adapter file.

## 🔴 यह क्यों बना? (Hindi)
Full fine-tuning में हर weight update होता है। 7B model (16-bit) के weights ही लगभग 14 GB, ऊपर से gradients और optimizer states, यानी कई GPUs चाहिए। हर task के लिए पूरे model की नई copy भी बनती है।

LoRA में 1% से भी कम parameters train होते हैं, GPU memory बहुत कम लगती है, और हर task की सिर्फ़ छोटी adapter file बनती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Take a frozen weight matrix W (shape d x k), e.g. attention q_proj
Step 2 → Add two small matrices: A (r x k) and B (d x r), where rank r is small (8, 16, 32)
Step 3 → B starts as zeros, A starts random -> at start the change is exactly 0
Step 4 → Forward pass: output = W·x + (alpha / r) · B·(A·x)
Step 5 → Backprop updates ONLY A and B (W stays frozen)
Step 6 → Save only A and B (the adapter)
Step 7 → At inference: load base + adapter, or merge: W' = W + (alpha/r)·B·A (no extra latency)
```

Parameter math: full matrix = d x k. LoRA = r x (d + k). For d = k = 4096, r = 8: 16.7M vs 65,536 (about 0.4%).

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक frozen weight matrix W लो (d x k), जैसे attention की q_proj
Step 2 → दो छोटे matrices जोड़ो: A (r x k) और B (d x r), rank r छोटा (8, 16, 32)
Step 3 → B शुरू में zeros, A random -> शुरुआत में बदलाव ठीक 0
Step 4 → Forward: output = W·x + (alpha / r) · B·(A·x)
Step 5 → Backprop सिर्फ़ A और B update करता है (W frozen)
Step 6 → सिर्फ़ A और B (adapter) save करो
Step 7 → Inference में base + adapter load करो, या merge करो: W' = W + (alpha/r)·B·A
```

---

## 🟡 Real World Example
**Tariff Classification System**: We want a model that outputs HS codes in a strict JSON format using customs terms ("CIF value", "heading 8517"). Full fine-tuning an 8B model is too costly. With LoRA (r=16 on attention layers) we train on about 5,000 labelled product-description to HS-code pairs on one GPU and get a 50-100 MB adapter. We can keep separate adapters: one for India customs, one for EU TARIC.

**Zomato AI**: A single base model serves many cities. Each city gets its own small LoRA adapter for local dish names and slang, hot-swapped per request.

## 🟡 Real Example Hindi mein
**Tariff System**: हमें ऐसा model चाहिए जो HS code strict JSON में दे और customs terms समझे। 8B model का full fine-tuning महँगा है। LoRA (r=16) से लगभग 5,000 examples पर एक GPU में train करके 50-100 MB का adapter मिलता है। India और EU के लिए अलग adapters रख सकते हैं।

**Zomato AI**: एक base model, हर शहर का अपना छोटा LoRA adapter, local dish names और slang के लिए, request के हिसाब से swap होता है।

---

## 💻 Code Example — Basic
```python
# Pure-Python LoRA math: no GPU, no libraries needed
from typing import Tuple  # type hints for clarity


def full_params(d: int, k: int) -> int:
    """Parameters in one full weight matrix."""
    return d * k  # d rows times k columns


def lora_params(d: int, k: int, r: int) -> int:
    """Parameters in the LoRA pair A (r x k) and B (d x r)."""
    return r * (d + k)  # r*k for A plus d*r for B


def compare(d: int, k: int, r: int) -> Tuple[int, int, float]:
    """Return full count, LoRA count and the percentage trained."""
    full = full_params(d, k)  # count full matrix params
    lora = lora_params(d, k, r)  # count LoRA params
    return full, lora, 100.0 * lora / full  # percentage of full


if __name__ == "__main__":
    for rank in (4, 8, 16, 64):  # try several ranks
        full, lora, pct = compare(4096, 4096, rank)  # a typical 7B attention matrix
        print(f"r={rank:<3} full={full:,} lora={lora:,} trained={pct:.2f}%")  # show result
```

## 💻 Code Example — Advanced
```python
# Production style LoRA training setup with Hugging Face PEFT (pip install transformers peft)
# Model name is an example; use a model you are licensed to use.
import asyncio  # async wrapper so FastAPI is not blocked
import logging  # structured logs
from dataclasses import dataclass  # config container

from peft import LoraConfig, TaskType, get_peft_model  # PEFT = Parameter-Efficient Fine-Tuning
from transformers import AutoModelForCausalLM  # base model loader

logger = logging.getLogger("lora")  # module logger


@dataclass
class LoraSettings:
    base_model: str = "meta-llama/Llama-3.1-8B"  # illustrative base model id
    r: int = 16  # rank of the update
    alpha: int = 32  # scaling factor (scale = alpha / r)
    dropout: float = 0.05  # regularisation on the LoRA path
    targets: tuple[str, ...] = ("q_proj", "k_proj", "v_proj", "o_proj")  # attention layers


def build_lora_model(cfg: LoraSettings):
    """Load the base model and wrap it with LoRA adapters."""
    try:
        model = AutoModelForCausalLM.from_pretrained(cfg.base_model)  # load frozen base
    except OSError as exc:  # bad model id, no network, or no access
        logger.error("cannot load base model: %s", exc)  # log the failure
        raise  # let the caller decide
    lora_cfg = LoraConfig(
        r=cfg.r,  # rank
        lora_alpha=cfg.alpha,  # alpha
        lora_dropout=cfg.dropout,  # dropout
        target_modules=list(cfg.targets),  # which layers get adapters
        task_type=TaskType.CAUSAL_LM,  # decoder-only language model
    )
    peft_model = get_peft_model(model, lora_cfg)  # inject A and B matrices
    peft_model.print_trainable_parameters()  # prints trainable vs total params
    return peft_model  # ready for a Trainer


async def build_async(cfg: LoraSettings):
    """Async version: run the heavy load in a worker thread."""
    return await asyncio.to_thread(build_lora_model, cfg)  # keep the event loop free


def save_adapter(model, path: str) -> None:
    """Save ONLY the adapter weights (small file)."""
    model.save_pretrained(path)  # writes adapter_config.json + adapter weights
```
Token usage: LoRA changes training cost, not the token price model. Training tokens = dataset tokens x epochs (see Cost Impact).

---

## 🟠 FastAPI Integration
Serve a base model once and attach adapters per request. The route below uses PEFT's adapter switching (`load_adapter` / `set_adapter`). Illustrative: production servers like vLLM have built-in multi-LoRA support.

```python
# FastAPI route that picks an adapter per request
from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel  # request validation

app = FastAPI()  # app instance
ADAPTERS = {"india": "./adapters/tariff-india", "eu": "./adapters/tariff-eu"}  # name -> path


class Req(BaseModel):
    description: str  # product description
    region: str = "india"  # which adapter to use


@app.post("/classify")
async def classify(req: Req) -> dict:
    if req.region not in ADAPTERS:  # validate input
        raise HTTPException(status_code=400, detail="unknown region")  # client error
    # model.set_adapter(req.region)  # switch adapter (model loaded at startup, illustrative)
    # output = generate(model, req.description)  # run generation
    return {"region": req.region, "hs_code": "8517.13"}  # placeholder response
```

---

## 🔗 LangChain / LangGraph Connection
LoRA models plug into LangChain as a normal LLM: serve the merged or adapter model behind an OpenAI-compatible endpoint (vLLM, TGI) and point `ChatOpenAI` at it. In LangGraph you can use the cheap fine-tuned model in a "classify" node and a larger model in a "reason" node.

```python
from langchain_openai import ChatOpenAI  # OpenAI-compatible client

llm = ChatOpenAI(
    model="tariff-lora",  # adapter name exposed by the server
    base_url="http://localhost:8000/v1",  # vLLM style endpoint
    api_key="not-needed",  # local server ignores it
)
print(llm.invoke("HS code for a smartphone?").content)  # normal LangChain call
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Rank too high "to be safe"
✅ Correct: Start with r=8 or 16, raise only if validation loss stalls.
```python
# Wrong: r=512 on every layer, almost as costly as full fine-tuning
LoraConfig(r=512, lora_alpha=1024, target_modules=["q_proj", "v_proj"])
# Right: modest rank, evaluate, then scale up
LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"])
```

❌ Mistake 2: Merging an adapter onto a different base model version
✅ Correct: Adapter and base must match exactly. Store the base model id and revision in your registry next to the adapter.
```python
# Wrong: adapter trained on base v1, loaded on base v2 -> garbage or silent quality drop
# Right: pin the base revision used for training
# AutoModelForCausalLM.from_pretrained(base_id, revision="<commit-sha>")
```

---

## 🧠 Tricky Interview Question
**Q**: "LoRA trains only 0.5% of the parameters. Why does it still work, and when does it fail?"

**Answer**: Research on fine-tuning suggests the weight change needed to adapt to a task has low intrinsic rank, so a low-rank product B·A can approximate it. It works well for style, format and domain vocabulary. It struggles when you need to inject lots of new knowledge or a big behaviour shift (for example a new language), where the update is not low-rank. Then you need higher rank, more target layers, or continued pre-training.

---

## ⚫ Interview Questions + Answers

Q1: What does LoRA stand for and what is its main idea?
A1: Low-Rank Adaptation. Freeze the base weights and learn a low-rank update B·A for chosen layers.

Q2: What are `r` and `alpha`?
A2: `r` is the rank (size of the bottleneck, controls capacity). `alpha` scales the update by alpha/r. Common start: r=16, alpha=32.

Q3: Why is B initialised to zeros?
A3: So that at step 0 the adapter output is zero and the model behaves exactly like the base model. Training then moves smoothly away from that point.

Q4: How can LoRA add no inference latency?
A4: After training you merge: W' = W + (alpha/r)·B·A and ship a normal model. Keeping the adapter separate costs a small extra matmul but allows hot-swapping adapters.

Q5: You serve 200 customers, each with a custom tariff style. How do you design it?
A5: One base model on GPU, 200 small adapters stored in object storage, loaded on demand into an adapter cache (multi-LoRA serving, for example in vLLM). Route by customer id, batch requests across adapters, version adapters with the base revision, and monitor per-adapter quality. This is much cheaper than 200 full model copies.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need style, format or domain adaptation on limited GPU memory
- You need many task or customer variants of one base model
- You want fast experiments and small artifacts to version

❌ Avoid when:
- Prompting or RAG already solves it (cheaper, no training)
- You need to teach large amounts of new facts (use RAG)
- Data is tiny or noisy (adapter will overfit)

---

## 📊 Visual Diagram
```
            input x
               |
       +-------+--------+
       |                |
       v                v
  [ W frozen ]     [ A (r x k) ]  <- trainable
   (d x k)              |
       |                v
       |           [ B (d x r) ]  <- trainable
       |                |
       |         x (alpha / r)
       |                |
       +------> (+) <---+
                 |
                 v
              output
```

---

## 💰 Cost Impact
LoRA lowers **training** cost (GPU memory and hours), not per-token inference price if you self-host. Illustrative numbers: dataset 5,000 examples x 400 tokens x 3 epochs = 6M training tokens. Hosted fine-tuning APIs charge per training token (check current pricing). Self-hosted: one 24-80 GB GPU for a few hours.

Optimise: use shorter prompts in training data, deduplicate examples, start with 1 epoch, use r=8/16, and serve many adapters on one base. A fine-tuned small model can replace long few-shot prompts, saving input tokens on every call.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LoRA | Low-rank adapter training | Low-rank adapter training |
| Rank (r) | Size of the bottleneck | Bottleneck का size |
| Alpha | Scaling of the update | Update का scale |
| Adapter | Small trained add-on weights | छोटे add-on weights |
| PEFT | Parameter-efficient fine-tuning | कम parameters से fine-tuning |
| Merge | Fold adapter into base weights | Adapter को base में मिलाना |
| Target modules | Layers that receive LoRA | जिन layers पर LoRA लगता है |

---

## ⚡ 3-Line Summary
English: LoRA freezes the base model and trains two tiny matrices per chosen layer. It cuts GPU memory and gives small, swappable adapters. Best for style, format and domain adaptation, not for adding lots of facts.
Hindi: LoRA base model को freeze करके हर चुनी layer में दो छोटे matrices train करता है। इससे GPU memory कम लगती है और छोटे, बदले जा सकने वाले adapters मिलते हैं। Style, format और domain adaptation के लिए best है, ज़्यादा facts सिखाने के लिए नहीं।

---

## ➡️ Next Topic
**497. QLoRA — What + Why** — LoRA on top of a 4-bit quantized base model, so even large models fit on a single consumer GPU.
