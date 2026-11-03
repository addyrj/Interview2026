
# 497. QLoRA — What + Why
# हिंदी में: QLoRA — क्या है और क्यों

---

## 🔵 Simple Definition (English)
QLoRA = LoRA on top of a 4-bit quantized base model. The big frozen model is stored in 4-bit (NF4) to save memory, while the small LoRA adapters are trained in higher precision (bf16/fp16). You get close to LoRA quality with a much smaller GPU memory footprint.

## 🔵 सरल परिभाषा (Hindi)
QLoRA = 4-bit quantized base model के ऊपर LoRA। बड़ा frozen model 4-bit (NF4) में रखा जाता है ताकि memory बचे, और छोटे LoRA adapters higher precision (bf16/fp16) में train होते हैं। LoRA के क़रीब quality मिलती है, पर GPU memory बहुत कम लगती है।

---

## 🔴 Problem it Solves
Even with LoRA, the frozen base model must sit in GPU memory. A 7B model in 16-bit is about 14 GB, a 70B model about 140 GB. Most teams do not have that. Quantizing to 4-bit shrinks weights roughly 4x (7B about 4-5 GB), so a 7B-13B model can be fine-tuned on a single 16-24 GB GPU.

## 🔴 यह क्यों बना? (Hindi)
LoRA में भी frozen base model GPU memory में रहना चाहिए। 7B model 16-bit में लगभग 14 GB, 70B लगभग 140 GB। ज़्यादातर teams के पास इतना नहीं होता। 4-bit quantization से weights लगभग 4x छोटे हो जाते हैं (7B लगभग 4-5 GB), इसलिए 7B-13B model एक 16-24 GB GPU पर fine-tune हो सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Load base weights quantized to 4-bit NormalFloat (NF4) via bitsandbytes
Step 2 → Double quantization: also compress the quantization constants (small extra saving)
Step 3 → Freeze the 4-bit base model
Step 4 → Attach LoRA adapters (bf16/fp16) to the layers
Step 5 → Forward: dequantize a block on the fly to compute, then discard it
Step 6 → Backward: gradients flow through the 4-bit weights into the adapters only
Step 7 → Paged optimizers move optimizer state to CPU RAM during memory spikes
Step 8 → Save adapter; for serving, load on a (quantized or 16-bit) base
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Base weights को bitsandbytes से 4-bit NormalFloat (NF4) में load करो
Step 2 → Double quantization: quantization constants भी compress होते हैं
Step 3 → 4-bit base model freeze करो
Step 4 → Layers पर LoRA adapters (bf16/fp16) जोड़ो
Step 5 → Forward में block को on-the-fly dequantize करके compute, फिर हटा दो
Step 6 → Backward में gradients सिर्फ़ adapters को update करते हैं
Step 7 → Paged optimizers memory spike में optimizer state CPU RAM में भेजते हैं
Step 8 → Adapter save करो; serving में base के ऊपर load करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The team wants an 8B or 13B model for HS-code reasoning but only owns one 24 GB GPU. With QLoRA (4-bit base, r=16) they fine-tune on 8,000 customs rulings in a few hours. Quality on the held-out set is near the 16-bit LoRA run.

**Amazon-style catalogue**: Fine-tune a mid-size model to map seller titles to product categories on one workstation GPU, then A/B test against the prompt-only baseline.

## 🟡 Real Example Hindi mein
**Tariff System**: Team को HS-code reasoning के लिए 8B/13B model चाहिए पर सिर्फ़ एक 24 GB GPU है। QLoRA (4-bit base, r=16) से 8,000 customs rulings पर कुछ घंटों में fine-tune होता है। Held-out quality 16-bit LoRA के क़रीब रहती है।

**Amazon-style catalogue**: Seller titles को product categories में map करने के लिए mid-size model एक workstation GPU पर fine-tune करो, फिर prompt-only baseline से A/B test करो।

---

## 💻 Code Example — Basic
```python
# Pure-Python memory estimator: weights memory by precision (no GPU needed)
BYTES_PER_PARAM = {"fp32": 4.0, "fp16": 2.0, "int8": 1.0, "nf4": 0.5}  # bytes per weight


def weights_gb(params_billion: float, precision: str) -> float:
    """Approximate GB for model weights only (ignores activations and optimizer)."""
    if precision not in BYTES_PER_PARAM:  # validate input
        raise ValueError(f"unknown precision {precision}")  # clear error
    return params_billion * 1e9 * BYTES_PER_PARAM[precision] / 1e9  # bytes -> GB


if __name__ == "__main__":
    for size in (7, 13, 70):  # common model sizes in billions
        row = {p: round(weights_gb(size, p), 1) for p in BYTES_PER_PARAM}  # GB per precision
        print(f"{size}B -> {row}")  # print the table row
```

## 💻 Code Example — Advanced
```python
# QLoRA setup with transformers + peft + bitsandbytes (needs a CUDA GPU)
# pip install transformers peft bitsandbytes accelerate
import asyncio  # to avoid blocking an async server
import logging  # logging for ops

import torch  # dtype definitions
from peft import LoraConfig, TaskType, get_peft_model, prepare_model_for_kbit_training  # PEFT helpers
from transformers import AutoModelForCausalLM, BitsAndBytesConfig  # HF classes

logger = logging.getLogger("qlora")  # logger


def build_qlora(model_id: str, r: int = 16):
    """Load a 4-bit base model and attach LoRA adapters."""
    bnb = BitsAndBytesConfig(
        load_in_4bit=True,  # store weights in 4-bit
        bnb_4bit_quant_type="nf4",  # NormalFloat4 data type
        bnb_4bit_use_double_quant=True,  # quantize the constants too
        bnb_4bit_compute_dtype=torch.bfloat16,  # compute in bf16
    )
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_id,  # base model id
            quantization_config=bnb,  # apply 4-bit config
            device_map="auto",  # place layers on available devices
        )
    except (OSError, RuntimeError) as exc:  # missing model or no GPU / CUDA problem
        logger.error("QLoRA load failed: %s", exc)  # log
        raise  # propagate
    model = prepare_model_for_kbit_training(model)  # enable grad checkpointing, cast norms
    cfg = LoraConfig(
        r=r, lora_alpha=2 * r, lora_dropout=0.05,  # rank, scale, dropout
        target_modules="all-linear",  # adapt every linear layer (supported by PEFT)
        task_type=TaskType.CAUSAL_LM,  # LM task
    )
    return get_peft_model(model, cfg)  # trainable adapters over 4-bit base


async def build_qlora_async(model_id: str, r: int = 16):
    """Async wrapper for use inside a service."""
    return await asyncio.to_thread(build_qlora, model_id, r)  # run in thread
```
Token usage: training tokens = dataset tokens x epochs. QLoRA is slower per step than 16-bit LoRA (dequantization overhead) but needs far less memory.

---

## 🟠 FastAPI Integration
Training is a background job, not a request handler. Expose endpoints to start a job and poll status.

```python
from fastapi import BackgroundTasks, FastAPI  # FastAPI parts
from pydantic import BaseModel  # validation

app = FastAPI()  # app
JOBS: dict[str, str] = {}  # job_id -> status (use a DB in production)


class TrainReq(BaseModel):
    dataset_path: str  # path to JSONL
    base_model: str  # model id


def run_training(job_id: str, req: TrainReq) -> None:
    JOBS[job_id] = "running"  # mark started
    try:
        # build_qlora(req.base_model); train(...)  # real training goes here (illustrative)
        JOBS[job_id] = "done"  # success
    except Exception as exc:  # any failure
        JOBS[job_id] = f"failed: {exc}"  # store error


@app.post("/train/{job_id}")
async def start(job_id: str, req: TrainReq, bg: BackgroundTasks) -> dict:
    bg.add_task(run_training, job_id, req)  # run after response
    return {"job_id": job_id, "status": "queued"}  # immediate reply


@app.get("/train/{job_id}")
async def status(job_id: str) -> dict:
    return {"job_id": job_id, "status": JOBS.get(job_id, "unknown")}  # poll
```
For real workloads use a queue (Celery, Ray, a cloud job) instead of in-process BackgroundTasks.

---

## 🔗 LangChain / LangGraph Connection
A QLoRA-tuned model is consumed like any other model once served (vLLM, TGI, Ollama after conversion). LangChain sees only an endpoint. LangGraph can route easy tariff lookups to this cheap model and hard ones to a hosted frontier model.

```python
from langchain_openai import ChatOpenAI  # OpenAI-compatible client

cheap = ChatOpenAI(model="tariff-qlora", base_url="http://gpu-box:8000/v1", api_key="x")  # tuned model
print(cheap.invoke("Classify: wireless earbuds").content)  # standard call
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using fp16 compute on hardware that prefers bf16 (or the reverse) and getting NaN loss
✅ Correct: Use bf16 compute on Ampere or newer GPUs.
```python
# Wrong
BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)  # may overflow on some setups
# Right (Ampere+)
BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)  # stable range
```

❌ Mistake 2: Skipping `prepare_model_for_kbit_training` and running out of memory or training unstably
✅ Correct: Call it before `get_peft_model`.
```python
# Wrong
model = get_peft_model(model, cfg)
# Right
model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, cfg)
```

---

## 🧠 Tricky Interview Question
**Q**: "You trained with QLoRA. Can you just merge the adapter into the 4-bit weights and ship?"

**Answer**: Not cleanly. Merging into quantized weights causes rounding error because the 4-bit grid cannot represent the exact sum. Common approaches: (1) load the base in 16-bit, merge the adapter, then (optionally) re-quantize for serving; (2) keep the adapter separate and serve base + adapter. Always re-run your eval after merging or re-quantizing.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between LoRA and QLoRA?
A1: LoRA trains adapters over a 16-bit frozen base. QLoRA does the same over a 4-bit quantized base, so memory is much lower.

Q2: What is NF4?
A2: NormalFloat 4-bit, a data type designed for weights that are roughly normally distributed, giving better accuracy than plain 4-bit integers.

Q3: What is double quantization?
A3: Quantizing the quantization constants themselves, saving a further fraction of a bit per parameter.

Q4: What are paged optimizers?
A4: Optimizer states are allocated in unified memory and paged to CPU RAM when GPU memory spikes, preventing out-of-memory crashes.

Q5: When would you choose LoRA over QLoRA?
A5: If GPU memory is sufficient, 16-bit LoRA is faster and avoids quantization error, so it is simpler to merge and evaluate. QLoRA is for memory-bound situations. In production I would compare both on my eval set and pick by quality, time and cost.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- GPU memory is the bottleneck (single 16-24 GB card)
- Prototyping fine-tunes of 7B-70B models cheaply

❌ Avoid when:
- You have ample GPU memory and want maximum speed
- Tiny quality differences matter and you cannot afford quantization error
- Prompting or RAG is enough

---

## 📊 Visual Diagram
```
   16-bit base (14 GB for 7B)            QLoRA
  +---------------------------+   +---------------------------+
  | weights fp16   ~14 GB     |   | weights NF4    ~4-5 GB    |  frozen
  +---------------------------+   +---------------------------+
  | LoRA adapters  small      |   | LoRA adapters  small bf16 |  trained
  +---------------------------+   +---------------------------+
  | grads + Adam   large      |   | grads + Adam   small      |
  +---------------------------+   +---------------------------+
        needs big GPU                   fits on one 16-24 GB GPU
```

---

## 💰 Cost Impact
QLoRA mainly cuts hardware cost: renting one 24 GB GPU instead of multiple 80 GB GPUs (prices vary, illustrative). Training time per step is somewhat longer than 16-bit LoRA. Token math is the same: dataset tokens x epochs.

Optimise: pack short examples, use gradient checkpointing, cap sequence length, stop early using validation loss, and after training serve a distilled or merged model so inference prompts can be short (no big few-shot blocks).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Quantization | Store numbers with fewer bits | कम bits में numbers रखना |
| NF4 | 4-bit NormalFloat type | 4-bit NormalFloat type |
| Double quantization | Quantize the constants too | Constants को भी quantize करना |
| bitsandbytes | Library for 4/8-bit ops | 4/8-bit operations की library |
| Paged optimizer | Optimizer state spills to CPU | Optimizer state CPU में |
| Compute dtype | Precision used for math | Math की precision |
| Adapter | Small trained weights | छोटे trained weights |

---

## ⚡ 3-Line Summary
English: QLoRA trains LoRA adapters on top of a frozen 4-bit quantized model. It makes 7B-70B fine-tuning possible on small GPUs. Merge carefully because of quantization error.
Hindi: QLoRA frozen 4-bit quantized model के ऊपर LoRA adapters train करता है। इससे छोटे GPUs पर 7B-70B fine-tuning संभव होती है। Quantization error के कारण merge सावधानी से करो।

---

## ➡️ Next Topic
**498. Hugging Face Fine Tuning** — the practical toolchain (datasets, transformers, peft, trl) that ties LoRA and QLoRA together.
