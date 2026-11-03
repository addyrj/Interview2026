---

# 490. OpenAI Fine Tuning
# हिंदी में: OpenAI Fine Tuning

---

## 🔵 Simple Definition (English)
OpenAI offers a managed fine tuning service. You upload a JSONL training file, create a fine tuning job, wait, and get a new model id (starting with `ft:`) that you call like a normal model. OpenAI handles GPUs and training code.

## 🔵 सरल परिभाषा (Hindi)
OpenAI एक managed fine tuning service देता है। आप JSONL training file upload करते हैं, fine tuning job बनाते हैं, इंतज़ार करते हैं और एक नया model id (जो `ft:` से शुरू होता है) मिलता है जिसे आप सामान्य model की तरह call करते हैं। GPUs और training code OpenAI संभालता है।

---

## 🔴 Problem it Solves
Training an LLM yourself needs GPUs, distributed training code and serving infrastructure. The managed API removes all of that: you only provide data and pay per training token, then serve through the same chat API.

## 🔴 यह क्यों बना? (Hindi)
खुद LLM train करने के लिए GPUs, distributed training code और serving infrastructure चाहिए। Managed API यह सब हटा देती है: आप सिर्फ़ data देते हैं और training token के हिसाब से पैसे देते हैं, फिर उसी chat API से serve करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Prepare train.jsonl (and optional validation.jsonl)
Step 2 → client.files.create(file=..., purpose="fine-tune") → file id
Step 3 → client.fine_tuning.jobs.create(training_file=id, model=base_model)
Step 4 → Poll client.fine_tuning.jobs.retrieve(job_id) until status "succeeded"
Step 5 → Read events/metrics (training loss) with jobs.list_events
Step 6 → job.fine_tuned_model gives the "ft:..." model id
Step 7 → Call chat.completions.create(model="ft:...") and evaluate
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → train.jsonl तैयार करो (और optional validation.jsonl)
Step 2 → client.files.create(file=..., purpose="fine-tune") → file id
Step 3 → client.fine_tuning.jobs.create(training_file=id, model=base_model)
Step 4 → "succeeded" होने तक jobs.retrieve(job_id) poll करो
Step 5 → jobs.list_events से events/metrics (training loss) पढ़ो
Step 6 → job.fine_tuned_model में "ft:..." model id मिलता है
Step 7 → chat.completions.create(model="ft:...") call करो और evaluate करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: We upload 800 examples (product description to HS JSON) and create a job on a small base model such as `gpt-4o-mini-2024-07-18` (check the docs for currently supported base models). In about an hour (illustrative) we get `ft:gpt-4o-mini-2024-07-18:acme::abc123`. The FastAPI service switches one env variable to the new id.

**Zomato-style**: Tune a small model for review tagging and swap the model id in config.

## 🟡 Real Example Hindi mein
**Tariff System**: हम 800 examples (product description से HS JSON) upload करते हैं और `gpt-4o-mini-2024-07-18` जैसे छोटे base model पर job बनाते हैं (अभी कौन से base models supported हैं, docs में देखें)। लगभग एक घंटे में (illustrative) `ft:gpt-4o-mini-2024-07-18:acme::abc123` मिलता है। FastAPI service में सिर्फ़ एक env variable बदलकर नया id लगा देते हैं।

**Zomato-style**: Review tagging के लिए छोटा model tune करो और config में model id बदल दो।

---

## 💻 Code Example — Basic
```python
# Basic: the OpenAI fine tuning flow (needs OPENAI_API_KEY and a real train.jsonl)
# pip install openai
import time  # for polling sleep
from openai import OpenAI  # sync client

client = OpenAI()  # reads OPENAI_API_KEY from environment

# 1) Upload the training file
with open("train.jsonl", "rb") as f:  # open dataset in binary mode
    train_file = client.files.create(file=f, purpose="fine-tune")  # upload
print("file id:", train_file.id)  # show id

# 2) Create the fine tuning job
job = client.fine_tuning.jobs.create(
    training_file=train_file.id,  # uploaded file id
    model="gpt-4o-mini-2024-07-18",  # base model (check docs for supported ones)
)
print("job id:", job.id)  # show job id

# 3) Poll until finished
while True:  # loop until terminal status
    job = client.fine_tuning.jobs.retrieve(job.id)  # refresh status
    print("status:", job.status)  # queued/running/succeeded/failed/cancelled
    if job.status in ("succeeded", "failed", "cancelled"):  # done states
        break
    time.sleep(30)  # wait before next poll

# 4) Use the tuned model
if job.status == "succeeded":  # only if it worked
    out = client.chat.completions.create(
        model=job.fine_tuned_model,  # the ft: model id
        messages=[{"role": "user", "content": "Classify: Bluetooth headphones"}],
    )
    print(out.choices[0].message.content)  # model answer
```

## 💻 Code Example — Advanced
```python
# Production style: async job runner with validation file, hyperparameters, timeouts and errors
import asyncio  # async
from typing import Optional  # optional types
from openai import AsyncOpenAI, OpenAIError  # async client and base error

client = AsyncOpenAI()  # needs OPENAI_API_KEY


async def upload(path: str) -> str:
    """Upload a JSONL file and return its file id."""
    with open(path, "rb") as f:  # open file
        obj = await client.files.create(file=f, purpose="fine-tune")  # upload
    return obj.id  # file id


async def run_finetune(
    train_path: str,
    val_path: Optional[str] = None,
    base_model: str = "gpt-4o-mini-2024-07-18",
    n_epochs: int = 3,
    poll_seconds: int = 30,
    timeout_seconds: int = 6 * 3600,
) -> str:
    """Create a job, wait for it, return the tuned model id."""
    try:
        train_id = await upload(train_path)  # upload train data
        val_id = await upload(val_path) if val_path else None  # optional validation data
        job = await client.fine_tuning.jobs.create(
            training_file=train_id,  # training data
            validation_file=val_id,  # None is accepted
            model=base_model,  # base
            hyperparameters={"n_epochs": n_epochs},  # keep epochs explicit
            suffix="tariff-v1",  # readable suffix in model name
        )
        waited = 0  # seconds waited
        while waited < timeout_seconds:  # bounded wait
            job = await client.fine_tuning.jobs.retrieve(job.id)  # refresh
            if job.status == "succeeded":  # success
                return job.fine_tuned_model  # model id
            if job.status in ("failed", "cancelled"):  # failure
                raise RuntimeError(f"job {job.id} ended with {job.status}: {job.error}")
            await asyncio.sleep(poll_seconds)  # non blocking wait
            waited += poll_seconds  # track time
        raise TimeoutError(f"job {job.id} did not finish in time")  # too slow
    except OpenAIError as exc:  # API related errors
        raise RuntimeError(f"OpenAI error: {exc}") from exc


# asyncio.run(run_finetune("train.jsonl", "val.jsonl"))  # needs real key and data
```

---

## 🟠 FastAPI Integration
Wrap job creation in an admin API and keep the tuned model id in config. Polling is better in a background task or worker than in the HTTP request.

```python
from fastapi import BackgroundTasks, FastAPI  # framework
from openai import AsyncOpenAI  # client

app = FastAPI()  # app
client = AsyncOpenAI()  # client
JOBS: dict = {}  # in memory store (use a DB in production)


@app.post("/admin/finetune")
async def start(train_file_id: str) -> dict:
    """Start a fine tuning job and return its id immediately."""
    job = await client.fine_tuning.jobs.create(
        training_file=train_file_id, model="gpt-4o-mini-2024-07-18"
    )
    JOBS[job.id] = job.status  # remember
    return {"job_id": job.id, "status": job.status}


@app.get("/admin/finetune/{job_id}")
async def status(job_id: str) -> dict:
    """Return current job status and model id when ready."""
    job = await client.fine_tuning.jobs.retrieve(job_id)  # fetch
    return {"status": job.status, "model": job.fine_tuned_model}
```

---

## 🔗 LangChain / LangGraph Connection
`ChatOpenAI` accepts the `ft:` model id as `model`. Everything else (prompts, parsers, LangGraph nodes) stays the same.

```python
from langchain_openai import ChatOpenAI  # wrapper
from langchain_core.output_parsers import StrOutputParser  # parser

llm = ChatOpenAI(model="ft:gpt-4o-mini-2024-07-18:acme:tariff-v1:abc123", temperature=0)  # placeholder id
chain = llm | StrOutputParser()  # simple chain
# print(chain.invoke("Classify: Bluetooth headphones"))  # needs API key
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a base model name that does not support fine tuning
✅ Correct: Check the current docs list and use the dated snapshot id.

```python
# Wrong: model="gpt-4o-mini"  (undated alias may be rejected for tuning)
# Right: model="gpt-4o-mini-2024-07-18"  (verify in the docs)
```

❌ Mistake 2: Blocking the web request while polling
✅ Correct: Return a job id and poll in a worker or via status endpoint.

```python
# Wrong: while job.status != "succeeded": time.sleep(30)  # inside the route
# Right: return job_id now; client calls GET /admin/finetune/{id}
```

---

## 🧠 Tricky Interview Question
**Q**: "The job succeeded but the tuned model answers worse than the base model with a good prompt. Why?"

**Answer**: Common causes: too few or noisy examples, train data format different from how you call it at inference (for example you trained with a system prompt but now omit it), too many epochs (overfitting), or no validation set to spot it. Compare training vs validation loss, call the model with the same message format used in training, and evaluate on a held-out set.

---

## ⚫ Interview Questions + Answers

Q1: What is the output of a fine tuning job? (Easy)
A1: A new model id starting with `ft:` that you use in the normal chat completions API.

Q2: What file format is needed? (Easy)
A2: JSONL where each line has a `messages` list in chat format.

Q3: Why add a validation file? (Medium)
A3: It reports validation loss during training, so you can detect overfitting.

Q4: Which hyperparameters can you set? (Medium)
A4: `n_epochs`, `batch_size` and `learning_rate_multiplier` (defaults are chosen automatically if not set).

Q5: How do you roll out a tuned model safely? (Hard)
A5: Evaluate on held-out data, shadow test against production traffic, canary a small percent with the model id in config, monitor quality and cost, and keep the old id for instant rollback.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want managed training with no GPU work
- Your task fits a supported base model

❌ Avoid when:
- Data cannot leave your environment (consider open models)
- You need full control over training or weights

---

## 📊 Visual Diagram
```
 train.jsonl ──► files.create ──► file id
                                    │
                                    ▼
                    fine_tuning.jobs.create(model=base)
                                    │  (queued → running)
                                    ▼
                       status: succeeded
                                    │
                                    ▼
                    fine_tuned_model = "ft:..."
                                    │
                                    ▼
                  chat.completions.create(model="ft:...")
```

---

## 💰 Cost Impact
- Training cost is roughly training tokens x epochs x price per training token (illustrative; check the pricing page).
- Inference on tuned models is billed at a tuned-model rate, usually higher than the base.
- Optimise: dedupe data, use the smallest model that works, 2 to 3 epochs, and test on 50 examples before the full run.
- Track `usage` (prompt_tokens, completion_tokens) per request to confirm savings.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fine tuning job | A training run on the platform | Platform पर training run |
| `ft:` model id | Name of your tuned model | आपके tuned model का नाम |
| Training file | JSONL of examples | Examples की JSONL file |
| Validation file | Held-out set for loss | Loss जाँच के लिए अलग file |
| Snapshot | Dated model version | Dated model version |
| Suffix | Custom label in model name | Model नाम में custom label |

---

## ⚡ 3-Line Summary
English: Upload JSONL, create a job on a supported base model, wait for status succeeded.
Use the returned `ft:` model id in normal chat calls.
Add a validation file and evaluate before rollout.
Hindi: JSONL upload करो, supported base model पर job बनाओ, status succeeded का इंतज़ार करो।
मिले `ft:` model id को सामान्य chat calls में use करो।
Validation file जोड़ो और rollout से पहले evaluate करो।

---

## ➡️ Next Topic
**491. Fine Tuning Data Format (JSONL)** — exactly how each training line must look.
