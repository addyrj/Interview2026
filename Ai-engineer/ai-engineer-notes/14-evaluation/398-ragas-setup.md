---

# 398. Ragas Setup
# हिंदी में: Ragas Setup

---

## 🔵 Simple Definition (English)
Ragas setup means getting a working evaluation environment: install `ragas`, give it a judge LLM and embeddings model, set API keys safely, and run a first small evaluation to confirm everything works.

## 🔵 सरल परिभाषा (Hindi)
Ragas setup का मतलब है काम करने वाला evaluation environment बनाना: `ragas` install करना, उसे judge LLM और embeddings model देना, API keys सुरक्षित रखना, और छोटा पहला evaluation चलाकर जाँचना कि सब ठीक चल रहा है।

---

## 🔴 Problem it Solves
Most Ragas failures are setup failures: missing judge LLM, missing embeddings for relevancy metrics, wrong dataset column names, rate limits, or version drift between tutorials. A clean, pinned setup makes results reproducible.

## 🔴 यह क्यों बना? (Hindi)
Ragas की ज़्यादातर failures setup की होती हैं: judge LLM न होना, relevancy metrics के लिए embeddings न होना, dataset के column names गलत, rate limits, या tutorials के बीच version drift। साफ़, pinned setup से results reproducible होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a virtualenv and install pinned versions (ragas, langchain-openai)
Step 2 → Put OPENAI_API_KEY in the environment (never in code)
Step 3 → Build judge LLM: LangchainLLMWrapper(ChatOpenAI(temperature=0))
Step 4 → Build embeddings: LangchainEmbeddingsWrapper(OpenAIEmbeddings)
Step 5 → Make a 3-5 row EvaluationDataset with the right column names
Step 6 → Run evaluate() with one cheap metric as a smoke test
Step 7 → Add RunConfig (timeout, workers, retries) before scaling up
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → virtualenv बनाओ और pinned versions install करो (ragas, langchain-openai)
Step 2 → OPENAI_API_KEY environment में रखो (code में कभी नहीं)
Step 3 → Judge LLM बनाओ: LangchainLLMWrapper(ChatOpenAI(temperature=0))
Step 4 → Embeddings बनाओ: LangchainEmbeddingsWrapper(OpenAIEmbeddings)
Step 5 → सही column names के साथ 3-5 rows का EvaluationDataset बनाओ
Step 6 → एक सस्ते metric से evaluate() का smoke test चलाओ
Step 7 → Scale करने से पहले RunConfig (timeout, workers, retries) जोड़ो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A new engineer clones the repo, runs `make eval-setup`, which creates a venv, installs `requirements-eval.txt` (pinned ragas), and runs a 3-row smoke test against the tariff golden set. If it prints scores, CI can run the same command. **Zomato-style**: the support-bot team keeps eval dependencies separate from the production image so the app stays small.

## 🟡 Real Example Hindi mein
**Tariff System**: नया engineer repo clone करके `make eval-setup` चलाता है, जो venv बनाता है, `requirements-eval.txt` (pinned ragas) install करता है और tariff golden set की 3 rows पर smoke test चलाता है। Scores print हों तो CI वही command चला सकती है। **Zomato-style**: support-bot team eval dependencies को production image से अलग रखती है ताकि app हल्का रहे।

---

## 💻 Code Example — Basic
```python
# Setup check that runs offline: verifies env, package and dataset columns BEFORE spending money.
# Shell steps (run once):
#   python3 -m venv .venv && source .venv/bin/activate
#   pip install "ragas>=0.2" langchain-openai
#   export OPENAI_API_KEY="sk-..."          # never commit this
import importlib.util                                         # check if a package exists
import os                                                     # read environment variables

REQUIRED_COLUMNS = {"user_input", "retrieved_contexts", "response", "reference"}   # Ragas 0.2+ names

def check_env() -> list[str]:
    problems: list[str] = []                                  # collected issues
    if not os.environ.get("OPENAI_API_KEY"):                  # key present?
        problems.append("OPENAI_API_KEY is not set")
    for pkg in ("ragas", "langchain_openai"):                 # packages installed?
        if importlib.util.find_spec(pkg) is None:
            problems.append(f"package missing: {pkg}")
    return problems

def check_rows(rows: list[dict]) -> list[str]:
    problems: list[str] = []
    for i, row in enumerate(rows):                            # validate every row
        missing = REQUIRED_COLUMNS - set(row)                 # which columns are absent
        if missing:
            problems.append(f"row {i} missing {sorted(missing)}")
        elif not isinstance(row["retrieved_contexts"], list): # must be list[str]
            problems.append(f"row {i}: retrieved_contexts must be a list")
    return problems

rows = [{"user_input": "Duty on batteries?", "retrieved_contexts": ["HS 8507.60 duty 20 percent"],
         "response": "20 percent", "reference": "20 percent"}]
issues = check_env() + check_rows(rows)                       # run all checks
print("OK, ready to evaluate" if not issues else "\n".join(issues))
```

## 💻 Code Example — Advanced
```python
# Production setup: typed config, judge/embeddings factory, RunConfig, async-safe runner, errors.
import asyncio                                                # async
import logging                                                # logs
import os                                                     # env
from dataclasses import dataclass                             # config object

log = logging.getLogger("ragas_setup")                        # logger

@dataclass(frozen=True)
class EvalConfig:
    judge_model: str = "gpt-4o-mini"                          # pin the judge
    embed_model: str = "text-embedding-3-small"               # embeddings for relevancy
    timeout: int = 180                                        # seconds per LLM call
    max_workers: int = 8                                      # parallel judge calls
    max_retries: int = 5                                      # retry on 429/5xx

def build(cfg: EvalConfig):
    """Create (llm, embeddings, run_config). Imports are inside so the module loads without ragas."""
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.run_config import RunConfig
    llm = LangchainLLMWrapper(ChatOpenAI(model=cfg.judge_model, temperature=0))
    emb = LangchainEmbeddingsWrapper(OpenAIEmbeddings(model=cfg.embed_model))
    rc = RunConfig(timeout=cfg.timeout, max_workers=cfg.max_workers, max_retries=cfg.max_retries)
    return llm, emb, rc

def run(rows: list[dict], cfg: EvalConfig = EvalConfig()) -> dict[str, float]:
    if "OPENAI_API_KEY" not in os.environ:
        raise RuntimeError("Set OPENAI_API_KEY first")        # fail fast
    from ragas import evaluate, EvaluationDataset
    from ragas.metrics import Faithfulness, ResponseRelevancy
    llm, emb, rc = build(cfg)
    ds = EvaluationDataset.from_list(rows)
    res = evaluate(ds, metrics=[Faithfulness(), ResponseRelevancy()], llm=llm, embeddings=emb, run_config=rc)
    return {k: float(v) for k, v in res.to_pandas().select_dtypes("number").mean().items()}

async def run_async(rows: list[dict]) -> dict[str, float]:
    try:
        return await asyncio.to_thread(run, rows)             # evaluate() blocks, so use a thread
    except Exception as exc:
        log.error("evaluation failed: %s", exc)
        raise
```
Not run here: needs `ragas`, an API key and network.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, BackgroundTasks                  # app + bg tasks
from pydantic import BaseModel                                # models
import uuid                                                   # job ids

app = FastAPI()                                               # app
jobs: dict[str, dict] = {}                                    # job_id -> state (Redis in prod)

class Rows(BaseModel):
    rows: list[dict]                                          # evaluation rows

async def _job(job_id: str, rows: list[dict]) -> None:
    try:
        jobs[job_id] = {"status": "done", "scores": await run_async(rows)}
    except Exception as exc:
        jobs[job_id] = {"status": "failed", "error": str(exc)}

@app.post("/eval/jobs")
async def start(body: Rows, bg: BackgroundTasks) -> dict[str, str]:
    job_id = uuid.uuid4().hex                                 # unique id
    jobs[job_id] = {"status": "running"}
    bg.add_task(_job, job_id, body.rows)                      # evaluation can take minutes
    return {"job_id": job_id}

@app.get("/eval/jobs/{job_id}")
async def status(job_id: str) -> dict:
    return jobs.get(job_id, {"status": "unknown"})
```

---

## 🔗 LangChain / LangGraph Connection
```python
# Ragas does not require LangChain, but the wrappers let you reuse any LangChain model as judge:
from langchain_openai import ChatOpenAI                       # could also be ChatAnthropic, AzureChatOpenAI...
from ragas.llms import LangchainLLMWrapper

judge = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", temperature=0))
# For Azure/other providers swap the LangChain class only; Ragas code stays the same.
# LangGraph: export state["docs"] and state["answer"] from each run into the dataset rows,
# so the evaluation measures the real graph, not a simplified copy.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Old column names from tutorials (`question`, `contexts`, `answer`, `ground_truth`)
✅ Correct: Ragas 0.2+ uses `user_input`, `retrieved_contexts`, `response`, `reference`.

```python
# Wrong (Ragas < 0.2 style)
{"question": q, "contexts": c, "answer": a, "ground_truth": g}
# Right (0.2+)
{"user_input": q, "retrieved_contexts": c, "response": a, "reference": g}
```

❌ Mistake 2: Unpinned versions and hard-coded keys
✅ Correct: pin in requirements and read keys from the environment.

```python
# Wrong
os.environ["OPENAI_API_KEY"] = "sk-abc"
# Right
# export OPENAI_API_KEY in shell / CI secret; requirements: ragas==<version you tested>
```

---

## 🧠 Tricky Interview Question
**Q**: "Evaluation works on your laptop but hangs or times out in CI. Why?"

**Answer**: Usually rate limits and concurrency. Too many parallel judge calls hit 429s; defaults retry slowly; CI has no key or restricted network. Fix: set `RunConfig(max_workers, timeout, max_retries)`, lower concurrency, use a dedicated key with higher limits, run a small smoke subset on PRs and the full set nightly.

---

## ⚫ Interview Questions + Answers

Q1: What do you need to run Ragas? (Easy)
A1: The package, an LLM judge, (for some metrics) an embeddings model, and a dataset in the expected format.

Q2: Where should API keys live? (Easy)
A2: Environment variables or a secret manager, never in code or git.

Q3: What is RunConfig for? (Medium)
A3: Controls timeouts, retries and worker concurrency of judge calls so large runs are stable.

Q4: Why a smoke test first? (Medium)
A4: Catches key, version and column problems cheaply before launching a costly full evaluation.

Q5: How do you keep evaluation reproducible? (Hard)
A5: Pin library and judge model versions, temperature 0, version the dataset, log config with every score set, store raw per-row outputs, and avoid mixing results from different judges.

---

## 🔷 When to Use + When Not to Use
✅ Use a dedicated eval environment when:
- CI runs evaluation
- Several people compare results

❌ Avoid installing eval dependencies in the production image when:
- Image size and attack surface matter

---

## 📊 Visual Diagram
```
 venv ──► pip install ragas langchain-openai
   │
 env: OPENAI_API_KEY
   │
 judge LLM ─┐
 embeddings ┼─► evaluate(dataset, metrics, run_config) ─► scores
 dataset ───┘        ▲
                     └─ smoke test (3 rows) before full run
```

---

## 💰 Cost Impact
Setup itself is free; the smoke test costs a few cents (3 rows x 2 metrics is roughly 10K tokens, under $0.01 on gpt-4o-mini). Mistakes in setup (wrong columns, retries without limits) can waste money by re-running large jobs. Use a small subset during development and cap workers to avoid retry storms.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Virtualenv | Isolated Python env | अलग Python environment |
| Judge LLM | Model that grades | grade करने वाला model |
| Embeddings wrapper | Embedding model adapter | embedding model adapter |
| RunConfig | Timeouts, retries, workers | timeout, retry, workers settings |
| Smoke test | Tiny first run | छोटा पहला परीक्षण |

---

## ⚡ 3-Line Summary
English: Install pinned Ragas, set keys in the environment, and configure judge LLM and embeddings. Use the 0.2+ column names and a RunConfig. Always smoke-test with a few rows first.
Hindi: Pinned Ragas install करो, keys environment में रखो, और judge LLM व embeddings configure करो। 0.2+ column names और RunConfig इस्तेमाल करो। पहले कुछ rows से smoke test ज़रूर करो।

---

## ➡️ Next Topic
**399. Ragas Dataset Creation** - building good evaluation datasets, including synthetic test generation.
