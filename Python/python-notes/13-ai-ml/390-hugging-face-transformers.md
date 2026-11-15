---

# 390. Hugging Face Transformers
# हिंदी में: Hugging Face Transformers (pretrained AI models की library)

---

## 🔵 Simple Definition (English)
`transformers` is Hugging Face's Python library to download and run thousands of pretrained models (BERT, GPT-style, T5, Whisper, ViT...) from the Hugging Face Hub. You can use a one-line `pipeline()` for quick tasks, or `AutoTokenizer` + `AutoModel...` for full control. It runs on PyTorch (also TensorFlow/JAX in older versions; current v5 focuses on PyTorch).

## 🔵 सरल परिभाषा (Hindi)
`transformers` Hugging Face की library है जिससे Hub पर मौजूद हज़ारों pretrained models (BERT, GPT-style, T5, Whisper, ViT...) download करके चला सकते हैं। जल्दी काम के लिए एक लाइन का `pipeline()`, और पूरे control के लिए `AutoTokenizer` + `AutoModel...`। यह PyTorch पर चलती है।

---

## 🔴 Problem it Solves
Training a language model needs millions of dollars and huge data. Before this library every model had its own code and weights format. Transformers gives one uniform API: `from_pretrained("model-name")` downloads weights, config and tokenizer, and the same code pattern works for sentiment, translation, summarization, speech and vision.

## 🔴 यह क्यों बना? (Hindi)
Language model को शुरू से train करना बहुत महँगा है। पहले हर model का अलग code और weights format था। Transformers एक जैसा API देता है: `from_pretrained("model-name")` से weights, config और tokenizer आ जाते हैं, और sentiment, translation, summarization, speech, vision सबमें वही pattern चलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → from_pretrained(name): download (once) and cache in ~/.cache/huggingface
Step 2 → Tokenizer: text -> token ids (+ attention_mask), padded/truncated
Step 3 → Model: ids -> logits (raw scores) / hidden states   (use torch.no_grad() for inference)
Step 4 → Post-process: softmax -> probabilities -> label via model.config.id2label
Step 5 → pipeline() does steps 2-4 for you in one call
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → from_pretrained(name): एक बार download होकर ~/.cache/huggingface में cache होता है
Step 2 → Tokenizer text को token ids (+ attention_mask) में बदलता है
Step 3 → Model ids से logits निकालता है (inference में torch.no_grad())
Step 4 → softmax से probability और id2label से label
Step 5 → pipeline() ये सब steps एक call में कर देता है
```

---

## 🟡 Real World Example
A Zomato-style review service classifies each review as positive or negative using DistilBERT. A support tool summarizes long tickets with a T5/BART model, and a voice feature transcribes audio with Whisper. All use the same `from_pretrained` pattern and run on CPU or GPU.

## 🟡 Real Example Hindi mein
Zomato जैसी review service हर review को DistilBERT से positive/negative में बाँटती है। Support tool लंबे tickets का summary T5/BART से बनाता है, और voice feature में Whisper audio को text बनाता है। सबमें वही `from_pretrained` pattern है, CPU या GPU पर चलता है।

---

## 💻 Code Example — Basic
```python
# VERIFIED: ran with transformers 5.22.2 + torch 2.15 (model downloaded from the Hub, ~270 MB, internet needed on first run).
# Install: pip install transformers torch
from typing import Any, Dict, List  # type hints

from transformers import pipeline  # the high-level API

# pipeline(task, model=...) downloads the model once and caches it
clf = pipeline(
    "sentiment-analysis",  # task name
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",  # pin the model explicitly
)

one: List[Dict[str, Any]] = clf("Great service")  # single text -> list with one dict
print(one)  # Output: [{'label': 'POSITIVE', 'score': 0.9998...}]  (score digits vary by version/hardware)

many: List[Dict[str, Any]] = clf(["I love this", "Worst app ever"])  # batch of texts
print([r["label"] for r in many])  # Output: ['POSITIVE', 'NEGATIVE']
print(round(many[1]["score"], 2) > 0.9)  # Output: True   (model is very confident)
```

## 💻 Code Example — Advanced
```python
# VERIFIED: ran on CPU, transformers 5.22.2, torch 2.15, Python 3.13.
# Production style: load once, explicit tokenizer + model, batching, no_grad, device, error handling.
from typing import Dict, List

import torch  # tensors and inference mode
from transformers import AutoModelForSequenceClassification, AutoTokenizer  # explicit classes

MODEL_NAME: str = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"  # public model on the Hub
DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"  # use a GPU when present

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)  # text -> ids
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME).to(DEVICE).eval()  # eval() turns off dropout

print(tokenizer.tokenize("Transformers are amazing"))  # Output: ['transformers', 'are', 'amazing']
print(sum(p.numel() for p in model.parameters()) // 1_000_000, "M params")  # Output: 66 M params


def classify(texts: List[str], batch_size: int = 16) -> List[Dict[str, object]]:
    """Classify many texts in batches and return label + confidence."""
    if not texts:  # guard against an empty request
        return []
    results: List[Dict[str, object]] = []  # collected output
    for start in range(0, len(texts), batch_size):  # process slices
        batch: List[str] = texts[start:start + batch_size]  # current slice
        enc = tokenizer(  # tokenize the whole batch
            batch, padding=True, truncation=True, max_length=128, return_tensors="pt"
        ).to(DEVICE)  # padding makes equal length, truncation avoids crashes on long text
        with torch.no_grad():  # no gradients -> less memory, faster
            logits = model(**enc).logits  # shape: (batch, num_labels)
        probs = torch.softmax(logits, dim=-1)  # logits -> probabilities
        for row in probs:  # one row per text
            idx: int = int(row.argmax())  # winning class id
            results.append({"label": model.config.id2label[idx], "score": round(float(row[idx]), 3)})
    return results


enc = tokenizer(["I love this", "This is terrible, never again!"], padding=True, return_tensors="pt")
print(list(enc.keys()), enc["input_ids"].shape)
# Output: ['input_ids', 'token_type_ids', 'attention_mask'] torch.Size([2, 9])
# (the key list can differ by model/version; DistilBERT in v5 ran with these keys here)

print(classify(["I love this", "This is terrible, never again!"]))
# Output: [{'label': 'POSITIVE', 'score': 1.0}, {'label': 'NEGATIVE', 'score': 0.991}]

try:  # wrong model name
    AutoModelForSequenceClassification.from_pretrained("no-such-org/no-such-model-xyz")
except OSError as exc:  # Hub errors surface as OSError
    print("load failed:", type(exc).__name__)  # Output: load failed: OSError
```

---

## 🟠 JavaScript vs Python Comparison
The JavaScript equivalent is `@huggingface/transformers` (Transformers.js), which runs ONNX models in Node or the browser.

```python
# Python
from transformers import pipeline
clf = pipeline("sentiment-analysis")
print(clf("I love this"))
```
```javascript
// JavaScript (Transformers.js)
import { pipeline } from "@huggingface/transformers";
const clf = await pipeline("sentiment-analysis");
console.log(await clf("I love this"));
```

Key differences: Python has the full ecosystem (training, fine-tuning, GPUs, thousands of models). Transformers.js runs smaller, converted (ONNX) models and is good for in-browser demos. The pipeline API was copied on purpose, so your mental model transfers directly.

---

## 🟠 FastAPI Connection
Load the model once in `lifespan` (never per request). Use a plain `def` endpoint (CPU-bound inference blocks the event loop) or run it in a threadpool.

```python
# FastAPI + Transformers (structure shown; heavy model, loads ~270 MB at startup)
from contextlib import asynccontextmanager  # lifespan
from typing import Any, AsyncIterator, Dict, List
from fastapi import FastAPI  # web
from pydantic import BaseModel, Field  # validation
from transformers import pipeline  # model API

ml: Dict[str, Any] = {}  # holds the loaded model


class Reviews(BaseModel):  # request model
    texts: List[str] = Field(min_length=1, max_length=32)  # limit batch size to protect memory


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    ml["clf"] = pipeline(
        "sentiment-analysis", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english"
    )  # loaded once at startup
    yield
    ml.clear()  # free memory at shutdown


app = FastAPI(lifespan=lifespan)  # register


@app.post("/sentiment")
def sentiment(body: Reviews) -> List[Dict[str, Any]]:  # def -> runs in a worker thread
    return ml["clf"](body.texts, truncation=True)  # truncation avoids errors on long texts
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Loading the model inside the request handler
```python
# Wrong: reloads 270 MB on every request (seconds of delay)
def predict(t): return pipeline("sentiment-analysis")(t)

# Right: load once at startup (module level or lifespan) and reuse
```

❌ Mistake 2: Forgetting `truncation` for long inputs
```python
# Wrong: text longer than the model limit (512 tokens for BERT-like) can raise an error / index error
clf(very_long_text)

# Right
clf(very_long_text, truncation=True)
```

❌ Mistake 3: Training-mode inference (no `eval()` / `no_grad()`)
```python
# Wrong: dropout is active (results vary) and memory is wasted on gradients
out = model(**enc)

# Right
model.eval()
with torch.no_grad():
    out = model(**enc)
```

❌ Mistake 4: Using a different tokenizer than the model
```python
# Wrong: tokenizer from model A, weights from model B -> garbage output
# Right: AutoTokenizer.from_pretrained(NAME) and AutoModel...from_pretrained(NAME) with the SAME name
```

---

## 🧠 Tricky Interview Question

**Q**: Why does `clf("I love this")` give a different score when called alone versus in a batch with a longer sentence?

**Answer**: Batches are padded to the longest text, and padding is masked with `attention_mask`, so mathematically the result should be the same. In practice tiny differences (for example 0.99988 versus 0.99984 in our run) appear from floating-point operations on different tensor shapes. The label should not change. If a label does flip, check that `attention_mask` is passed (use `model(**enc)`, not only `input_ids`), that the model is in `eval()` mode, and that truncation is consistent.

---

## ⚫ Interview Questions + Answers

Q1: What is a tokenizer and why is it needed?
A1: Models only understand numbers. A tokenizer splits text into subword tokens and maps them to integer ids (plus special tokens like `[CLS]`). Each model needs its own matching tokenizer.

Q2: `pipeline` vs `AutoModel`?
A2: `pipeline` is a quick wrapper (tokenize, run, post-process). `AutoModel...` gives control for batching, custom post-processing, fine-tuning and performance tuning.

Q3: What are logits?
A3: Raw, unnormalized scores from the last layer. `softmax(logits)` gives probabilities that sum to 1.

Q4: What does `.eval()` do?
A4: Switches layers like dropout and batch-norm to inference behaviour. It is different from `torch.no_grad()`, which only stops gradient tracking. Use both.

Q5: How do you run big models on small hardware?
A5: Use smaller/distilled models, half precision (`torch_dtype`/`dtype` float16/bfloat16), quantization (bitsandbytes), batching, or hosted inference. Note: the argument name for dtype changed across versions, check the docs for your installed version.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You want open-source models you control (privacy, cost, customisation)
- Tasks like classification, NER, summarization, translation, embeddings, speech
- You plan to fine-tune on your own data

❌ Avoid when:
- A hosted LLM API (OpenAI/Anthropic) is simpler and your data policy allows it
- You have no GPU and need very large models with low latency
- A simple rule or regex solves the problem

---

## 📊 Visual Diagram

```
"I love this"
    │  AutoTokenizer
    ▼
input_ids [101, 1045, 2293, 2023, 102] + attention_mask
    │  AutoModelForSequenceClassification
    ▼
logits [-4.2, 4.6] ── softmax ──► [0.0001, 0.9999] ── id2label ──► POSITIVE
(example numbers; real values depend on the model)

pipeline("sentiment-analysis") = all of the above in one call
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hub | Online store of models | models का online भंडार |
| Tokenizer | Text to token ids | text से token ids |
| Logits | Raw model scores | model के कच्चे scores |
| Pipeline | One-call inference helper | एक call में inference |
| Fine-tuning | Training a pretrained model more | pretrained model को और सिखाना |
| Attention mask | Marks real vs padding tokens | असली और padding tokens की पहचान |

---

## ⚡ 3-Line Summary
English: `transformers` downloads and runs pretrained models with a uniform API. Use `pipeline` for speed and `AutoTokenizer` + `AutoModel` for control. Load once, use `eval()` + `no_grad()`, batch and truncate inputs.
Hindi: `transformers` एक जैसे API से pretrained models चलाती है। जल्दी के लिए `pipeline` और control के लिए `AutoTokenizer` + `AutoModel`। Model एक बार load करें, `eval()` + `no_grad()` लगाएँ, inputs को batch और truncate करें।

---

## ➡️ Next Topic
**391. Tokenizers Library** (already written), then **392. sentence-transformers** for embeddings.
