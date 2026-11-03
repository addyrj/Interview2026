
---

# 504. Fine Tuning for Tariff System
# हिंदी में: Tariff System के लिए Fine Tuning

---

## 🔵 Simple Definition (English)
Here we fine-tune a small model so that, given a product description, it returns a strict JSON with the HS code, a short reason and a confidence flag. We train on past officer-verified classifications. Fresh rules still come from RAG; fine-tuning fixes format, terminology and behaviour.

## 🔵 सरल परिभाषा (Hindi)
यहाँ हम एक छोटे model को fine-tune करते हैं ताकि product description देने पर वह strict JSON दे: HS code, छोटा कारण और confidence flag। Training पुराने officer-verified classifications पर होती है। नए rules RAG से आते हैं; fine-tuning format, terminology और behaviour ठीक करती है।

---

## 🔴 Problem it Solves
The base model wrote long essays, invented codes with wrong digit counts, and used inconsistent JSON keys, which broke the downstream customs form. A long few-shot prompt (1,000+ tokens) reduced errors but cost money on every call. Fine-tuning bakes the format and style into the weights so the prompt becomes short.

## 🔴 यह क्यों बना? (Hindi)
Base model लंबे essays लिखता था, गलत digits वाले codes बनाता था और JSON keys अलग-अलग देता था, जिससे customs form टूट जाता था। लंबा few-shot prompt (1,000+ tokens) errors घटाता था पर हर call पर पैसे लगते थे। Fine-tuning format weights में बैठा देती है, prompt छोटा हो जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Export verified classifications (description, 8-digit HS code, reason) from the DB
Step 2 → Clean: remove PII, wrong/disputed rulings, duplicates
Step 3 → Convert to chat JSONL: system + user description -> assistant JSON
Step 4 → Split by product family: train 80% / validation 10% / test 10%
Step 5 → Upload files, create the fine-tuning job on a small model
Step 6 → Watch training + validation loss; stop if validation rises
Step 7 → Run test set: exact match, 6-digit match, JSON validity, abstain rate
Step 8 → Deploy behind a flag, compare with RAG baseline on live traffic (shadow mode)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → DB से verified classifications निकालो (description, 8-digit HS code, reason)
Step 2 → Clean: PII, गलत/विवादित rulings, duplicates हटाओ
Step 3 → Chat JSONL बनाओ: system + user description -> assistant JSON
Step 4 → Product family के हिसाब से split: train 80% / validation 10% / test 10%
Step 5 → Files upload करो, छोटे model पर fine-tuning job बनाओ
Step 6 → Training + validation loss देखो; validation बढ़े तो रोक दो
Step 7 → Test set पर exact match, 6-digit match, JSON validity जाँचो
Step 8 → Flag के पीछे deploy करो, shadow mode में RAG baseline से तुलना
```

---

## 🟡 Real World Example
**Tariff Classification System**: 4,000 verified rows: "Bluetooth over-ear headphones, plastic, 20 Hz-20 kHz" -> `{"hs_code":"8518.30","reason":"Headphones, whether or not combined with a microphone","needs_review":false}`. Also include ~10% "hard/ambiguous" rows whose target is `needs_review: true`, so the model learns to abstain.

**Amazon-style**: Seller listing categories are classified into a taxonomy with a fine-tuned small model because latency must be under 300 ms at huge volume.

## 🟡 Real Example Hindi mein
**Tariff System**: 4,000 verified rows: "Bluetooth over-ear headphones, plastic" -> `{"hs_code":"8518.30","reason":"...","needs_review":false}`। लगभग 10% मुश्किल rows में `needs_review: true` रखो ताकि model abstain करना सीखे।

**Amazon-style**: Seller listings को taxonomy में classify करने के लिए छोटा fine-tuned model, क्योंकि latency 300 ms से कम चाहिए।

---

## 💻 Code Example — Basic
```python
# Pure Python: turn verified tariff rows into OpenAI chat fine-tuning JSONL and validate them
import json  # for JSON lines
from pathlib import Path  # for file paths

SYSTEM = "Classify the product. Reply with JSON keys: hs_code, reason, needs_review."  # short system prompt

rows = [  # pretend this came from the database
    {"desc": "Bluetooth over-ear headphones", "hs": "8518.30", "why": "Headphones", "review": False},
    {"desc": "Cotton men's t-shirt, knitted", "hs": "6109.10", "why": "T-shirts of cotton, knitted", "review": False},
    {"desc": "Mixed lot of assorted spare parts", "hs": "", "why": "Too vague", "review": True},
]

def to_example(r: dict) -> dict:
    """Build one training example in chat format."""
    target = {"hs_code": r["hs"], "reason": r["why"], "needs_review": r["review"]}  # desired JSON output
    return {"messages": [  # chat format required by the API
        {"role": "system", "content": SYSTEM},  # system turn
        {"role": "user", "content": r["desc"]},  # user turn
        {"role": "assistant", "content": json.dumps(target)},  # what the model must learn to say
    ]}

out = Path("tariff_train.jsonl")  # output file
with out.open("w", encoding="utf-8") as f:  # open for writing
    for r in rows:  # loop rows
        f.write(json.dumps(to_example(r), ensure_ascii=False) + "\n")  # one example per line

# Validate: every line must parse and end with an assistant message
for line in out.read_text(encoding="utf-8").splitlines():  # read back
    ex = json.loads(line)  # parse
    assert ex["messages"][-1]["role"] == "assistant"  # last turn is the target
print("examples:", len(rows))  # count
```

## 💻 Code Example — Advanced
```python
# Production: upload, start a fine-tune job, poll it, and use the result (OpenAI SDK, needs API key)
import asyncio  # async polling
import logging  # logs
from pathlib import Path  # paths
from typing import Optional  # optional types

from openai import AsyncOpenAI, OpenAIError  # async client

log = logging.getLogger("ft")  # logger
client = AsyncOpenAI()  # reads OPENAI_API_KEY

async def launch(train: Path, val: Path, suffix: str = "tariff-v1") -> str:
    """Upload data and create a supervised fine-tuning job."""
    try:
        tf = await client.files.create(file=train.open("rb"), purpose="fine-tune")  # train file
        vf = await client.files.create(file=val.open("rb"), purpose="fine-tune")  # validation file
        job = await client.fine_tuning.jobs.create(
            model="gpt-4o-mini-2024-07-18",  # small, cheap base (verify current options)
            training_file=tf.id,  # train data id
            validation_file=vf.id,  # validation id
            suffix=suffix,  # readable model name part
            hyperparameters={"n_epochs": 3},  # a few epochs is usually enough
        )
        return job.id  # id for polling
    except OpenAIError as exc:  # API errors
        log.error("launch failed: %s", exc)  # log
        raise  # propagate

async def wait(job_id: str, every: float = 30.0) -> Optional[str]:
    """Poll until the job ends; return the fine-tuned model name or None."""
    while True:  # loop until terminal state
        job = await client.fine_tuning.jobs.retrieve(job_id)  # fetch status
        log.info("job %s: %s", job_id, job.status)  # report
        if job.status == "succeeded":  # done
            return job.fine_tuned_model  # e.g. ft:gpt-4o-mini-...:tariff-v1:xxxx
        if job.status in ("failed", "cancelled"):  # terminal failure
            log.error("job ended: %s", job.error)  # show reason
            return None  # no model
        await asyncio.sleep(every)  # wait before next poll

async def classify(model: str, desc: str) -> str:
    """Use the tuned model with the SAME short system prompt used in training."""
    r = await client.chat.completions.create(
        model=model,  # fine-tuned model id
        messages=[{"role": "system", "content": "Classify the product. Reply with JSON keys: hs_code, reason, needs_review."},
                  {"role": "user", "content": desc}],  # prompt must match training format
        temperature=0,  # stable output
        response_format={"type": "json_object"},  # force valid JSON
        max_tokens=120,  # JSON is short
    )
    return r.choices[0].message.content or ""  # JSON string

# asyncio.run(...) is omitted: it needs a key, data and takes minutes to hours.
```

---

## 🟠 FastAPI Integration
```python
import json  # parse model JSON
from fastapi import FastAPI, HTTPException  # framework
from openai import AsyncOpenAI, OpenAIError  # client
from pydantic import BaseModel, ValidationError  # validation

app = FastAPI()  # app
client = AsyncOpenAI()  # client
MODEL = "ft:gpt-4o-mini-2024-07-18:acme:tariff-v1:abc123"  # illustrative id

class Req(BaseModel):
    description: str  # product description

class Out(BaseModel):
    hs_code: str  # HS code
    reason: str  # short reason
    needs_review: bool  # abstain flag

@app.post("/classify", response_model=Out)
async def classify(req: Req) -> Out:
    """Classify with the fine-tuned model and validate its JSON."""
    try:
        r = await client.chat.completions.create(
            model=MODEL, temperature=0, max_tokens=120,  # deterministic and capped
            response_format={"type": "json_object"},  # JSON mode
            messages=[{"role": "system", "content": "Classify the product. Reply with JSON keys: hs_code, reason, needs_review."},
                      {"role": "user", "content": req.description}],
        )
        return Out(**json.loads(r.choices[0].message.content or "{}"))  # parse + validate
    except (OpenAIError, json.JSONDecodeError, ValidationError) as exc:  # all failure types
        raise HTTPException(status_code=502, detail=f"classification failed: {exc}")  # safe error
```

---

## 🔗 LangChain / LangGraph Connection
Use the tuned model as the generator node. A common graph: RAG retrieves rule text, the tuned model classifies, and a conditional edge sends `needs_review=true` to a human-in-the-loop node.

```python
from langchain_openai import ChatOpenAI  # LangChain wrapper
from langchain_core.prompts import ChatPromptTemplate  # prompt template

llm = ChatOpenAI(model="ft:gpt-4o-mini-2024-07-18:acme:tariff-v1:abc123", temperature=0)  # illustrative id
prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify the product. Reply with JSON keys: hs_code, reason, needs_review."),  # same as training
    ("human", "{desc}"),  # user input
])
chain = prompt | llm  # LCEL chain
# result = await chain.ainvoke({"desc": "Bluetooth headphones"})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Different prompt at inference than at training
✅ Correct: Reuse the exact system prompt and format.
```python
# Wrong: trained with a short system prompt, served with a new 500-token prompt
# Right: one shared constant SYSTEM used for both
```

❌ Mistake 2: Random split that leaks near-duplicates
✅ Correct: Split by product family or supplier.
```python
# Wrong: random.shuffle(rows)  # "iPhone 15 128GB" in train, "iPhone 15 256GB" in test
# Right: group by (heading) first, then split groups
```

❌ Mistake 3: No "needs_review" examples
✅ Correct: Include abstain cases, otherwise the model guesses confidently on every vague input.

---

## 🧠 Tricky Interview Question

**Q**: "Validation loss fell nicely but production accuracy on new products dropped versus the RAG baseline. Why?"

**Answer**: Loss measures imitation of training labels, not correctness on new items. Likely causes: near-duplicate leakage making validation easy, the tariff schedule changed after the training snapshot (fine-tuned weights are stale), or the model memorised frequent headings. Fix: group split, a time-based test set of newest products, combine with RAG so current rules are injected, and track exact-match on a golden set rather than loss.

---

## ⚫ Interview Questions + Answers

Q1: What format does chat fine-tuning data use?
A1: JSONL where each line has `messages` with system, user and assistant roles; the assistant message is the target.

Q2: Why include ambiguous examples?
A2: To teach abstention (`needs_review`), reducing confident wrong codes.

Q3: Why keep temperature at 0 for classification?
A3: It makes outputs deterministic and reproducible for audits.

Q4: How many examples are needed?
A4: Small improvements often show with tens to a few hundred, but robust classification typically needs hundreds to a few thousand clean examples. Quality beats quantity; check the provider docs for minimums.

Q5: Design the full production architecture and a retraining policy.
A5: Retrieval of current tariff text feeds a tuned small model, with JSON validation and a human review queue. Log every request with model version. Each month, add newly verified classifications, retrain, evaluate on a frozen golden set plus a newest-products set, and only promote via shadow traffic and canary if exact match improves and abstain rate stays in range. Keep rollback to the previous model id.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have thousands of verified, consistent labelled examples
- Format reliability, latency and per-call cost matter

❌ Avoid when:
- Labels are inconsistent between officers (fix labelling first)
- Rules change weekly and you have no RAG layer
- Fewer than a few hundred examples

---

## 📊 Visual Diagram
```
 DB (verified rows) ─► clean ─► JSONL ─► split(train/val/test by family)
                                              │
                                              ▼
                                   Fine-tuning job (small model)
                                              │
                                              ▼
 user desc ─► RAG rules ─► tuned model ─► JSON {hs_code, reason, needs_review}
                                              │
                          needs_review? ─yes─► human queue
                                         no ─► customs form
```

---

## 💰 Cost Impact
Worked example (illustrative numbers): 4,000 examples x ~120 tokens = 0.48M tokens per epoch, 3 epochs = ~1.4M trained tokens. At an assumed $3 per 1M trained tokens this is about $4.30, which is cheap; always check live pricing. Fine-tuned model inference per token is typically higher than the base model, but removing a 1,000-token few-shot prompt can reduce input tokens by roughly 80%, so total per-call cost often falls.
Optimise: short system prompt, `max_tokens` around 120, JSON mode to avoid retries, cache repeated descriptions (exact-match cache), and use the tuned small model for 90% of traffic with a bigger model only for `needs_review` cases.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HS code | Standard product code for customs | Customs का product code |
| JSONL | One JSON object per line | हर line में एक JSON |
| Abstain | Model says "not sure" | Model का "पक्का नहीं" कहना |
| Golden set | Fixed trusted test set | भरोसेमंद fixed test set |
| Shadow mode | New model runs silently | Model चुपचाप साथ चले |
| Canary | Small % of live traffic | थोड़े live traffic पर test |
| Epoch | One pass over data | Data पर एक पूरा चक्कर |

---

## ⚡ 3-Line Summary
English: Fine-tune a small model on verified (description -> JSON) pairs so format and abstention are reliable and prompts stay short. Split by product family, keep the same prompt at train and serve time, and combine with RAG for current rules. Judge by golden-set accuracy, not loss.
Hindi: Verified (description -> JSON) pairs पर छोटा model fine-tune करो ताकि format और abstain भरोसेमंद हों और prompt छोटा रहे। Product family से split करो, train और serve में एक ही prompt रखो, और ताज़ा rules के लिए RAG जोड़ो। Loss नहीं, golden-set accuracy से परखो।

---

## ➡️ Next Topic
**505. Fine Tuning Best Practices** — a checklist for data, hyper-parameters, evaluation and safe rollout.
