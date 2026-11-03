
---

# 502. Continued Pre-training
# हिंदी में: Continued Pre-training — Model को नए Domain का Raw Text पढ़ाना

---

## 🔵 Simple Definition (English)
Continued pre-training (CPT) means taking an already pre-trained open model and training it further on a large pile of raw, unlabelled domain text (law, medicine, customs rules) using the same next-token objective. There are no question-answer pairs. The model absorbs the domain's vocabulary and facts.

## 🔵 सरल परिभाषा (Hindi)
Continued pre-training में पहले से pre-trained open model को domain के बहुत सारे raw, बिना label वाले text (कानून, medicine, customs rules) पर उसी next-token objective से आगे train किया जाता है। इसमें question-answer pairs नहीं होते। Model domain की भाषा और facts सोख लेता है।

---

## 🔴 Problem it Solves
A general model sees words like "Harmonized System", "ad valorem" or "GRI 3(b)" rarely, so it tokenizes them poorly and knows little about them. SFT on a few thousand Q&A pairs teaches format, not deep vocabulary. CPT fills the knowledge gap at the base-model level, for cases where RAG alone is not enough (very specialised language, offline use, low-resource language).

## 🔴 यह क्यों बना? (Hindi)
General model "Harmonized System", "ad valorem" जैसे शब्द कम देखता है, इसलिए इनकी समझ कमज़ोर होती है। कुछ हज़ार Q&A पर SFT format सिखाता है, गहरी vocabulary नहीं। CPT base-model स्तर पर यह कमी भरता है, जहाँ सिर्फ RAG काफ़ी नहीं (बहुत specialised भाषा, offline use, कम resource वाली भाषा)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick an open-weights base model (Llama, Mistral, Qwen family etc.)
Step 2 → Collect raw domain text: tariff schedules, rulings, legal notes (licensed!)
Step 3 → Clean: remove duplicates, boilerplate, PII; filter low quality
Step 4 → Mix in 10-30% general text ("replay") to avoid forgetting
Step 5 → Pack text into fixed-length sequences (e.g. 4096 tokens)
Step 6 → Train with next-token loss, small learning rate (lower than original)
Step 7 → Watch general benchmarks + domain perplexity
Step 8 → Then run SFT (and maybe DPO) on top for instruction-following
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Open-weights base model चुनो (Llama, Mistral, Qwen आदि)
Step 2 → Raw domain text जमा करो: tariff schedules, rulings (licence के साथ)
Step 3 → Clean करो: duplicates, boilerplate, PII हटाओ
Step 4 → 10-30% general text मिलाओ ताकि पुराना knowledge न भूले
Step 5 → Text को fixed-length sequences में pack करो (जैसे 4096 tokens)
Step 6 → Next-token loss से, छोटे learning rate पर train करो
Step 7 → General benchmarks और domain perplexity दोनों देखो
Step 8 → फिर SFT (और ज़रूरत हो तो DPO) करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs authority has 40 million tokens of tariff notes, rulings and chapter explanatory notes in English and Hindi. A general 8B model mixes up heading vs subheading wording. After CPT on this corpus (with 20% general replay) and then SFT on classification examples, it handles the jargon natively, and RAG on top becomes more accurate.

**Amazon-style**: Product catalog text in many Indian languages is used for CPT so the base model understands seller-style abbreviations before it is tuned for listing generation.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs authority के पास 4 करोड़ tokens के notes और rulings हैं (English + Hindi)। General 8B model heading और subheading की भाषा में गड़बड़ करता है। 20% general replay के साथ CPT, फिर SFT करने पर model jargon खुद समझता है और ऊपर से RAG और सटीक हो जाता है।

**Amazon-style**: कई भारतीय भाषाओं के catalog text पर CPT, ताकि model seller की abbreviations समझे।

---

## 💻 Code Example — Basic
```python
# Pure Python: pack raw documents into fixed-length token blocks (core step of CPT data prep)
from typing import Iterable  # type hint for iterables

def pack_tokens(docs: Iterable[list[int]], block: int, eos: int) -> list[list[int]]:
    """Concatenate token lists (with EOS between docs) and cut into equal blocks."""
    buffer: list[int] = []  # rolling buffer of tokens
    blocks: list[list[int]] = []  # finished training sequences
    for doc in docs:  # go through each tokenised document
        buffer.extend(doc + [eos])  # add the doc and a separator token
        while len(buffer) >= block:  # while we can fill a block
            blocks.append(buffer[:block])  # take one full block
            buffer = buffer[block:]  # keep the remainder
    return blocks  # incomplete tail is dropped (common practice)

# Fake token ids stand in for a real tokenizer's output
docs = [[1, 2, 3, 4, 5], [6, 7, 8], [9, 10, 11, 12, 13, 14]]  # three tiny "documents"
out = pack_tokens(docs, block=6, eos=0)  # pack into blocks of 6
for b in out:  # print every block
    print(b)  # e.g. [1,2,3,4,5,0]
print("blocks:", len(out))  # how many sequences we got

# Replay mixing: 80% domain, 20% general
def mix(domain: list[str], general: list[str], general_ratio: float = 0.2) -> list[str]:
    """Return a list with about general_ratio of general text mixed in."""
    n_general = int(len(domain) * general_ratio / (1 - general_ratio))  # how many general docs
    return domain + general[:n_general]  # take that many general docs

print(len(mix(["d"] * 80, ["g"] * 100)))  # 80 domain + 20 general = 100
```

## 💻 Code Example — Advanced
```python
# Production-style: dedup + clean corpus builder, async file reading, then a training config
# Actual training uses GPUs, e.g. Hugging Face transformers/TRL/Axolotl (not installed here).
import asyncio  # async IO
import hashlib  # hashing for exact dedup
import logging  # logs
import re  # regex cleaning
from pathlib import Path  # paths
from typing import Iterator  # generator type

log = logging.getLogger("cpt")  # logger

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")  # crude email PII pattern

def clean(text: str) -> str:
    """Remove emails and collapse whitespace."""
    text = EMAIL.sub("<EMAIL>", text)  # mask emails
    return re.sub(r"\s+", " ", text).strip()  # normalise spaces

async def read_file(path: Path) -> str:
    """Read a file without blocking the event loop."""
    try:
        return await asyncio.to_thread(path.read_text, encoding="utf-8")  # offload blocking read
    except (OSError, UnicodeDecodeError) as exc:  # missing or bad encoding
        log.warning("skip %s: %s", path, exc)  # log and continue
        return ""  # treat as empty

def dedup(texts: list[str], min_chars: int = 200) -> Iterator[str]:
    """Yield unique, long-enough documents."""
    seen: set[str] = set()  # hashes seen so far
    for t in texts:  # loop docs
        t = clean(t)  # clean first
        if len(t) < min_chars:  # too short to be useful
            continue  # skip
        h = hashlib.sha256(t.lower().encode()).hexdigest()  # content hash
        if h in seen:  # duplicate
            continue  # skip
        seen.add(h)  # remember
        yield t  # keep

async def build_corpus(folder: Path, out: Path) -> int:
    """Read all .txt files, clean, dedup, write one JSONL-like text file."""
    files = sorted(folder.glob("*.txt"))  # list files
    texts = await asyncio.gather(*(read_file(p) for p in files))  # read concurrently
    n = 0  # counter
    with out.open("w", encoding="utf-8") as f:  # open output
        for doc in dedup(list(texts)):  # unique docs
            f.write(doc.replace("\n", " ") + "\n")  # one doc per line
            n += 1  # count
    return n  # docs kept

# Typical CPT hyper-parameters (illustrative, tune per model):
CPT_CONFIG: dict[str, object] = {
    "learning_rate": 2e-5,  # lower than original pre-training to limit forgetting
    "seq_len": 4096,  # block size
    "replay_ratio": 0.2,  # share of general text
    "epochs": 1,  # usually 1-2 passes over domain data
    "warmup_ratio": 0.03,  # gentle start
}

if __name__ == "__main__":
    print(asyncio.run(build_corpus(Path("./tariff_txt"), Path("cpt_corpus.txt"))))  # run on a folder
```

---

## 🟠 FastAPI Integration
CPT produces a self-hosted model. FastAPI serves it (often via vLLM, which exposes an OpenAI-compatible endpoint) and your API simply points the OpenAI client at it.

```python
from fastapi import FastAPI, HTTPException  # web framework
from openai import AsyncOpenAI, OpenAIError  # OpenAI-compatible client
from pydantic import BaseModel  # schema

app = FastAPI()  # app
llm = AsyncOpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")  # local vLLM server

class Q(BaseModel):
    question: str  # tariff question

@app.post("/classify")
async def classify(q: Q) -> dict:
    """Ask the domain-adapted self-hosted model."""
    try:
        r = await llm.chat.completions.create(
            model="tariff-cpt-sft",  # your served model name
            messages=[{"role": "user", "content": q.question}],  # prompt
            max_tokens=200,  # cap output cost/latency
        )
    except OpenAIError as exc:  # server down, timeout etc.
        raise HTTPException(status_code=502, detail=str(exc))  # bad gateway
    return {"answer": r.choices[0].message.content, "tokens": r.usage.total_tokens if r.usage else None}
```

---

## 🔗 LangChain / LangGraph Connection
Once served, the CPT model is just another chat model for LangChain/LangGraph, so you can swap it in a node with no graph changes.

```python
from langchain_openai import ChatOpenAI  # works with any OpenAI-compatible server

domain_llm = ChatOpenAI(
    model="tariff-cpt-sft",  # name served by vLLM
    base_url="http://localhost:8000/v1",  # local endpoint
    api_key="not-needed",  # placeholder
    temperature=0,  # deterministic classification
)
# Use domain_llm inside a LangGraph node exactly like any other model.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using CPT when RAG would do
✅ Correct: Try RAG + prompting first; CPT needs GPUs, big data and weeks of work.
```python
# Wrong: "our rules change monthly, let's pre-train on them"  (stale in a week)
# Right: put changing facts in a vector DB; use CPT only for stable domain language
```

❌ Mistake 2: No general replay data
✅ Correct: Mix in general text.
```python
# Wrong: corpus = domain_docs                 # catastrophic forgetting of chat/code skills
# Right: corpus = domain_docs + general_docs[:20% of total]
```

❌ Mistake 3: Training on copyrighted or private data
✅ Correct: Check licences, strip PII, and keep an audit trail of the sources.

---

## 🧠 Tricky Interview Question

**Q**: "After CPT on tariff text, your model scores better on tariff perplexity but now refuses to follow instructions and writes poor JSON. What happened?"

**Answer**: CPT used raw text, so the model drifted away from chat/instruction behaviour (forgetting) or you started from an instruct model whose alignment got overwritten. Raw text teaches continuation, not obeying. Fix: start CPT from a base model, include replay data, lower the learning rate, and then run SFT with instruction/JSON examples (and optionally DPO). Perplexity is not an end-task metric; evaluate on classification accuracy and format validity.

---

## ⚫ Interview Questions + Answers

Q1: What data does continued pre-training use?
A1: Large amounts of raw, unlabelled domain text with the same next-token prediction loss as original pre-training.

Q2: How is CPT different from SFT?
A2: CPT adds knowledge/vocabulary from raw text; SFT teaches behaviour and format from labelled instruction-answer pairs. Usually CPT comes first, then SFT.

Q3: Why mix in general data?
A3: To prevent catastrophic forgetting, where the model loses general abilities while specialising.

Q4: When is CPT better than RAG?
A4: When the language is highly specialised, low-resource, or must work offline with low latency, and the knowledge is stable. RAG is better for fast-changing facts and for citing sources.

Q5: How would you evaluate a CPT run?
A5: Domain perplexity on a held-out set, general benchmarks for regression, and, after SFT, task accuracy (HS-code exact match). Also check data contamination so the eval set was not in the corpus.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have tens of millions of domain tokens and GPU budget
- Domain language or a low-resource language is poorly handled
- You must self-host

❌ Avoid when:
- Knowledge changes often (use RAG)
- You only have a few thousand examples (use SFT / LoRA)
- You use a closed API model you cannot pre-train

---

## 📊 Visual Diagram
```
 General base model
        │   + raw tariff text (80%)  + general text replay (20%)
        ▼
 ┌───────────────────────────┐
 │ next-token loss, low LR   │   Continued Pre-training
 └─────────────┬─────────────┘
               ▼
 Domain-aware base model
        │  SFT (Q&A, JSON format)
        ▼
        │  DPO (preferences)   [optional]
        ▼
 Tariff assistant  ──►  vLLM  ──►  FastAPI
```

---

## 💰 Cost Impact
CPT is the most expensive form of tuning: GPU hours scale with tokens x parameters. As a rough rule, training compute is about 6 x parameters x tokens FLOPs, so 8B params x 1B tokens is about 4.8e19 FLOPs (illustrative). Hosted fine-tuning APIs generally do not offer CPT; you rent GPUs.
Optimise: use LoRA/QLoRA-style continued training on a smaller model, dedupe aggressively (fewer tokens, same knowledge), use a 1-epoch pass, and checkpoint often. At inference there is no per-token vendor fee, but you pay for GPUs; shorter prompts (no few-shot) cut tokens per request.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CPT | Further pre-training on raw text | Raw text पर आगे pre-training |
| Corpus | Collection of training text | Training text का संग्रह |
| Perplexity | How surprised the model is by text | Model कितना "हैरान" है |
| Replay data | General text mixed in | मिलाया गया general text |
| Catastrophic forgetting | Losing old skills | पुरानी skills भूल जाना |
| Packing | Fit docs into equal blocks | Docs को equal blocks में बाँधना |
| Base model | Not instruction-tuned | Instruction-tuned नहीं |

---

## ⚡ 3-Line Summary
English: CPT trains an open base model on raw domain text to learn vocabulary and facts. Mix in general data, use a low learning rate, and follow with SFT. Use it only for stable, specialised knowledge; use RAG for changing facts.
Hindi: CPT open base model को raw domain text पर train करता है ताकि vocabulary और facts सीखे। General data मिलाओ, learning rate कम रखो और बाद में SFT करो। सिर्फ stable, specialised knowledge के लिए; बदलते facts के लिए RAG।

---

## ➡️ Next Topic
**503. Domain Adaptation** — the umbrella view: choosing between prompting, RAG, CPT, SFT and DPO for a new domain.
