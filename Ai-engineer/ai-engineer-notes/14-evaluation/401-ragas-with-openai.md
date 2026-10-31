---

# 401. Ragas with OpenAI
# हिंदी में: Ragas को OpenAI के साथ इस्तेमाल करना

---

## 🔵 Simple Definition (English)
Ragas needs a judge LLM and an embedding model. "Ragas with OpenAI" means using an OpenAI chat model (like gpt-4o-mini) as the judge and an OpenAI embedding model (like text-embedding-3-small) for similarity-based metrics. It is the default and the easiest setup.

## 🔵 सरल परिभाषा (Hindi)
Ragas को एक judge LLM और एक embedding model चाहिए। "Ragas with OpenAI" का मतलब है OpenAI chat model (जैसे gpt-4o-mini) को judge बनाना और OpenAI embedding model (जैसे text-embedding-3-small) को similarity metrics के लिए इस्तेमाल करना। यह सबसे आसान setup है।

---

## 🔴 Problem it Solves
Without explicit configuration, Ragas picks defaults that may use a costly model, read the wrong API key, or hit rate limits mid-run. Teams get surprise bills and half-finished runs with NaN scores.

## 🔴 यह क्यों बना? (Hindi)
Explicit configuration के बिना Ragas defaults लेता है जो महँगा model चला सकते हैं, गलत API key पढ़ सकते हैं या run के बीच rate limit में फँस सकते हैं। नतीजा: अचानक बड़ा बिल और अधूरे runs में NaN scores।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Set OPENAI_API_KEY in environment (never in code)
Step 2 → Create ChatOpenAI(model, temperature=0) from langchain-openai
Step 3 → Wrap with LangchainLLMWrapper
Step 4 → Create OpenAIEmbeddings and wrap with LangchainEmbeddingsWrapper
Step 5 → Set RunConfig(timeout, max_retries, max_workers) for rate limits
Step 6 → evaluate(dataset, metrics, llm, embeddings, run_config)
Step 7 → Read token usage / cost and compare judge models
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → OPENAI_API_KEY environment में रखो (code में कभी नहीं)
Step 2 → langchain-openai से ChatOpenAI(model, temperature=0) बनाओ
Step 3 → LangchainLLMWrapper से wrap करो
Step 4 → OpenAIEmbeddings बनाकर LangchainEmbeddingsWrapper से wrap करो
Step 5 → Rate limits के लिए RunConfig(timeout, max_retries, max_workers) सेट करो
Step 6 → evaluate(dataset, metrics, llm, embeddings, run_config)
Step 7 → Token usage / cost देखो और judge models की तुलना करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The team evaluates with gpt-4o-mini as judge (cheap, fast). Once a month, they re-score a 50-row sample with gpt-4o to check that the cheap judge agrees with the strong one (agreement > 90%). If the two disagree a lot, the cheap judge is not trustworthy for that metric.

**Zomato-style**: Daily eval of a restaurant-search chatbot with 300 rows, concurrency capped at 8 so it stays under the requests-per-minute limit.

## 🟡 Real Example Hindi mein
**Tariff System**: Team judge के रूप में gpt-4o-mini इस्तेमाल करती है (सस्ता, तेज़)। महीने में एक बार 50 rows gpt-4o से दोबारा score करती है ताकि देखें कि सस्ता judge मजबूत judge से सहमत है (agreement > 90%)। ज़्यादा असहमति हो तो सस्ता judge उस metric के लिए भरोसेमंद नहीं।

**Zomato-style**: Restaurant-search chatbot की रोज़ 300 rows की eval, concurrency 8 पर सीमित ताकि requests-per-minute limit के अंदर रहे।

---

## 💻 Code Example — Basic
```python
# Basic: estimate judge cost before spending money (pure Python, runs offline)
PRICES: dict[str, tuple[float, float]] = {  # (input, output) USD per 1M tokens, example values
    "gpt-4o-mini": (0.15, 0.60),  # cheap judge
    "gpt-4o": (2.50, 10.00),  # strong judge
}


def estimate_cost(model: str, rows: int, metrics: int,
                  in_tok: int = 1500, out_tok: int = 200) -> float:
    """Rough judge cost: rows x metrics x calls-per-metric(2) x tokens."""
    if model not in PRICES:  # unknown model guard
        raise KeyError(f"unknown model {model}")  # fail clearly
    p_in, p_out = PRICES[model]  # unpack prices
    calls = rows * metrics * 2  # assume ~2 judge calls per metric per row
    return calls * (in_tok * p_in + out_tok * p_out) / 1_000_000  # USD total


for m in PRICES:  # compare both judges
    print(m, f"${estimate_cost(m, rows=100, metrics=3):.3f}")  # print estimate
# gpt-4o-mini ~ $0.21, gpt-4o ~ $3.75 (estimates, not billing data)
```

## 💻 Code Example — Advanced
```python
# Advanced: OpenAI judge with retries, rate-limit control, and async execution
# pip install ragas langchain-openai
import asyncio  # async wrapper
import logging  # logs
import os  # environment access

from langchain_openai import ChatOpenAI, OpenAIEmbeddings  # OpenAI via LangChain
from ragas import EvaluationDataset, evaluate  # Ragas core
from ragas.embeddings import LangchainEmbeddingsWrapper  # embedding wrapper
from ragas.llms import LangchainLLMWrapper  # LLM wrapper
from ragas.metrics import Faithfulness, ResponseRelevancy  # two metrics
from ragas.run_config import RunConfig  # concurrency / retry settings

log = logging.getLogger("ragas_openai")  # logger


def build_models(judge_model: str = "gpt-4o-mini"):  # returns (llm, embeddings)
    if not os.getenv("OPENAI_API_KEY"):  # fail early without key
        raise RuntimeError("OPENAI_API_KEY is not set")  # clear message
    llm = LangchainLLMWrapper(  # wrap chat model
        ChatOpenAI(model=judge_model, temperature=0, timeout=60, max_retries=3)  # pinned judge
    )
    emb = LangchainEmbeddingsWrapper(OpenAIEmbeddings(model="text-embedding-3-small"))  # cheap embeddings
    return llm, emb  # both wrappers


def score(rows: list[dict], judge_model: str = "gpt-4o-mini") -> dict[str, float]:
    llm, emb = build_models(judge_model)  # construct models
    ds = EvaluationDataset.from_list(rows)  # dataset
    cfg = RunConfig(timeout=90, max_retries=5, max_workers=8)  # stay under rate limits
    res = evaluate(ds, metrics=[Faithfulness(), ResponseRelevancy()],
                   llm=llm, embeddings=emb, run_config=cfg,
                   raise_exceptions=False)  # NaN instead of crash
    df = res.to_pandas()  # per-row results
    nan_rows = int(df.isna().any(axis=1).sum())  # how many rows failed
    if nan_rows:  # warn the user
        log.warning("%d rows have NaN scores", nan_rows)  # visible warning
    return df.select_dtypes("number").mean(skipna=True).round(3).to_dict()  # means


async def compare_judges(rows: list[dict]) -> dict[str, dict[str, float]]:
    cheap, strong = await asyncio.gather(  # run both judges concurrently
        asyncio.to_thread(score, rows, "gpt-4o-mini"),
        asyncio.to_thread(score, rows, "gpt-4o"),
    )
    return {"gpt-4o-mini": cheap, "gpt-4o": strong}  # side-by-side results
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel  # validation

app = FastAPI()  # app


class EvalRequest(BaseModel):  # request
    rows: list[dict]  # dataset rows
    judge_model: str = "gpt-4o-mini"  # judge choice


ALLOWED = {"gpt-4o-mini", "gpt-4o"}  # whitelist stops expensive surprises


@app.post("/eval/openai")  # endpoint
async def eval_openai(req: EvalRequest) -> dict:
    if req.judge_model not in ALLOWED:  # guard cost
        raise HTTPException(400, f"judge must be one of {sorted(ALLOWED)}")  # reject
    if len(req.rows) > 200:  # cap size per request
        raise HTTPException(413, "max 200 rows per request")  # too large
    try:
        scores = await asyncio.to_thread(score, req.rows, req.judge_model)  # run off-loop
    except RuntimeError as exc:  # missing key etc.
        raise HTTPException(500, str(exc))  # report config issue
    return {"scores": scores}  # response
```

---

## 🔗 LangChain / LangGraph Connection
Ragas uses the same `ChatOpenAI` class as your app, so one config (model, timeout, retries) can be shared. You can also add a LangGraph "evaluate" node that scores sampled production answers and logs them to LangSmith.

```python
from langchain_openai import ChatOpenAI  # same class as app

app_llm = ChatOpenAI(model="gpt-4o", temperature=0.2)  # production generator
judge_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # separate cheap judge
# Tip: judge should be a different (or stronger) model than the generator
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the same model as generator and judge (self-preference bias)
✅ Correct: use a different model family or a stronger judge

```python
# Wrong
judge = generator = ChatOpenAI(model="gpt-4o-mini")
# Right
judge = ChatOpenAI(model="gpt-4o", temperature=0)
```

❌ Mistake 2: No concurrency limit, so 429 errors give NaN scores
✅ Correct: `RunConfig(max_workers=8, max_retries=5)`.

❌ Mistake 3: Hard-coding the API key in notebooks
✅ Correct: environment variable or secret manager.

---

## 🧠 Tricky Interview Question
**Q**: "Your Ragas run on 500 rows returns 60 NaN values. The mean looks fine. Is it OK to ship?"

**Answer**: No. NaN rows are skipped by the mean, so the score only reflects rows that were easy enough to score (or that did not hit timeouts). Investigate causes: rate limits (429), context too long for the judge, JSON parse failures from the judge. Re-run only the failed rows with lower concurrency and report coverage (440/500 scored) along with the mean.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Which two models does Ragas need?
A1: A judge LLM and an embedding model.

Q2: [Easy] Where should the OpenAI key live?
A2: In `OPENAI_API_KEY` environment variable or a secrets manager.

Q3: [Medium] Why use a cheap judge in CI but a stronger one occasionally?
A3: Cost control. Periodically check the cheap judge's agreement with the strong one to confirm it is still reliable.

Q4: [Medium] What does `RunConfig` control?
A4: Timeouts, retries and the number of parallel workers - the main levers against rate-limit errors.

Q5: [Hard] How do you detect judge bias toward OpenAI outputs?
A5: Evaluate the same dataset with a judge from another family (e.g. Claude) and compare rankings of systems; if rankings flip, the judge has self-preference bias. Also use human-labelled calibration rows.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You already use OpenAI and want the simplest setup
- You need strong structured-output reliability from the judge

❌ Avoid when:
- Data cannot leave your network (use a local judge)
- You judge OpenAI-generated answers with an OpenAI judge only (bias)

---

## 📊 Visual Diagram
```
 .env OPENAI_API_KEY
        │
 ChatOpenAI(gpt-4o-mini, temp=0) ─► LangchainLLMWrapper ──┐
 OpenAIEmbeddings(3-small) ───────► LangchainEmbeddingsWrapper ─┤
 RunConfig(workers=8, retries=5) ───────────────────────────────┤
                                                                ▼
                                   evaluate(dataset, metrics) ─► scores
```

---

## 💰 Cost Impact
Judge tokens dominate. Ballpark 100 rows x 3 metrics: gpt-4o-mini about $0.2, gpt-4o about $3-4 (check current prices). Embeddings for relevancy are tiny (text-embedding-3-small is ~$0.02 per 1M tokens).
Optimise: cheap judge by default, sample rows, cache results by row hash, use OpenAI Batch API (50% cheaper) for nightly non-urgent runs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Judge model | LLM scoring outputs | Score करने वाला LLM |
| RunConfig | Retry/concurrency settings | Retry और concurrency settings |
| 429 error | Rate limit hit | Rate limit पार हो गई |
| Self-preference bias | Judge favours its own style | Judge का अपने जैसे जवाब पसंद करना |
| Embedding model | Text to vectors | Text को vectors में बदलना |

---

## ⚡ 3-Line Summary
English: Ragas with OpenAI = ChatOpenAI judge + OpenAIEmbeddings wrapped for Ragas. Pin temperature 0, control concurrency with RunConfig, and watch NaN rows. Use a cheap judge daily and a strong one for calibration.
Hindi: Ragas with OpenAI = ChatOpenAI judge + OpenAIEmbeddings, Ragas के लिए wrap किए हुए। Temperature 0 रखो, RunConfig से concurrency control करो, NaN rows देखो। रोज़ सस्ता judge, calibration के लिए मजबूत judge।

---

## ➡️ Next Topic
**402. Ragas with Claude** - use Anthropic models as the judge to avoid self-preference bias.
