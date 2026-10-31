---

# 390. RAG Evaluation Metrics
# हिंदी में: RAG Evaluation Metrics

---

## 🔵 Simple Definition (English)
RAG evaluation metrics are scores that check each part of a RAG pipeline. Retrieval metrics (context precision, context recall) ask "did we fetch the right chunks?". Generation metrics (faithfulness, answer relevancy, answer correctness) ask "did the model answer well using those chunks?".

## 🔵 सरल परिभाषा (Hindi)
RAG evaluation metrics वो scores हैं जो RAG pipeline के हर हिस्से को जाँचते हैं। Retrieval metrics (context precision, context recall) पूछते हैं "क्या हमने सही chunks निकाले?"। Generation metrics (faithfulness, answer relevancy, answer correctness) पूछते हैं "क्या model ने उन chunks से अच्छा answer दिया?"।

---

## 🔴 Problem it Solves
A single "is the answer good?" score cannot tell you what to fix. If the answer is wrong, was the retriever bad (missing the tariff note), or did the LLM ignore the context and hallucinate? Component-wise metrics separate the two, so engineers fix the right layer instead of guessing.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ एक "answer अच्छा है?" score से पता नहीं चलता कि क्या ठीक करना है। Answer गलत है तो retriever खराब था (tariff note छूट गया), या LLM ने context को ignore करके hallucinate किया? Component-wise metrics दोनों को अलग करते हैं, ताकि engineers सही layer ठीक करें, अंदाज़े से नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Each test row has: question, retrieved contexts, generated answer, reference (gold) answer
Step 2 → RETRIEVAL checks:
          context_precision = are the relevant chunks ranked at the top?
          context_recall    = did the contexts cover everything in the reference answer?
Step 3 → GENERATION checks:
          faithfulness      = is every claim in the answer supported by the contexts?
          answer_relevancy  = does the answer address the question (no off-topic)?
          answer_correctness= does the answer match the reference (facts + meaning)?
Step 4 → Each metric returns 0..1 (higher is better)
Step 5 → Read the PATTERN to find the failing component
Step 6 → Fix that component, re-run, compare
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हर test row में: question, retrieved contexts, generated answer, reference (gold) answer
Step 2 → RETRIEVAL checks:
          context_precision = relevant chunks ऊपर rank हुए हैं?
          context_recall    = contexts ने reference answer की सारी बातें cover कीं?
Step 3 → GENERATION checks:
          faithfulness      = answer का हर claim contexts से supported है?
          answer_relevancy  = answer सवाल का जवाब देता है (off-topic नहीं)?
          answer_correctness= answer reference से match करता है (facts + meaning)?
Step 4 → हर metric 0..1 देता है (ज़्यादा = बेहतर)
Step 5 → PATTERN पढ़कर failing component पहचानो
Step 6 → उस component को ठीक करो, दोबारा चलाओ, compare करो
```

---

## 🟡 Real World Example
**Tariff Classification System** question: "Duty on lithium-ion batteries from Vietnam?"

| Pattern | Diagnosis | Fix |
|---|---|---|
| Low context recall | Retriever missed the Vietnam trade-agreement chunk | Better chunking, hybrid search, more top-k |
| Low context precision | Right chunk exists but ranked 5th among noise | Add reranker |
| Low faithfulness, good contexts | LLM added a rate not in the documents | Stricter prompt, lower temperature |
| Low relevancy | Answer explains battery chemistry instead of duty | Prompt fix: "answer only the duty question" |

**Zomato AI**: "Best biryani near me" - answer talks about pizza (low relevancy) versus invents a restaurant (low faithfulness).

## 🟡 Real Example Hindi mein
**Tariff System** सवाल: "Vietnam से lithium-ion batteries पर duty?"

- Context recall कम: Retriever ने Vietnam trade-agreement वाला chunk miss किया → chunking सुधारो, hybrid search, top-k बढ़ाओ।
- Context precision कम: सही chunk है पर noise के बीच 5वें नंबर पर → reranker जोड़ो।
- Faithfulness कम, contexts अच्छे: LLM ने ऐसा rate बता दिया जो documents में नहीं था → prompt सख्त करो, temperature कम करो।
- Relevancy कम: Answer battery chemistry समझा रहा है, duty नहीं → prompt: "सिर्फ duty का जवाब दो"।

**Zomato AI**: "आस-पास सबसे अच्छी biryani" - answer pizza की बात करे (relevancy कम) या ऐसा restaurant बना दे जो है ही नहीं (faithfulness कम)।

---

## 💻 Code Example — Basic
```python
# Basic: cheap, offline approximations of the 5 metrics using word overlap.
# These are TEACHING versions; real tools (Ragas/DeepEval) use an LLM judge.
import re                                         # tokenisation


def words(text: str) -> set[str]:
    """Lowercase word set without punctuation."""
    return set(re.findall(r"[a-z0-9.]+", text.lower()))


def overlap(a: str, b: str) -> float:
    """Fraction of words of `a` that also appear in `b`."""
    wa = words(a)                                  # words in a
    return len(wa & words(b)) / len(wa) if wa else 0.0


question = "What is the duty on lithium-ion batteries?"
reference = "Duty on lithium-ion batteries is 0 percent under HS 8507."
contexts = ["HS 8507 covers lithium-ion batteries and the duty is 0 percent.",
            "HS 6109 covers cotton t-shirts."]
answer = "The duty on lithium-ion batteries is 0 percent."

# faithfulness ~ how much of the ANSWER is supported by contexts
faithfulness = overlap(answer, " ".join(contexts))
# answer relevancy ~ how much of the QUESTION topic appears in the answer
relevancy = overlap(question, answer)
# context recall ~ how much of the REFERENCE is covered by contexts
recall = overlap(reference, " ".join(contexts))
# context precision ~ fraction of retrieved contexts that overlap the reference
precision = sum(overlap(c, reference) > 0.5 for c in contexts) / len(contexts)
# answer correctness ~ similarity of answer and reference
correctness = overlap(reference, answer)

for name, val in [("faithfulness", faithfulness), ("answer_relevancy", relevancy),
                  ("context_recall", recall), ("context_precision", precision),
                  ("answer_correctness", correctness)]:
    print(f"{name:20s} {val:.2f}")
```

## 💻 Code Example — Advanced
```python
# Advanced: metric suite with per-metric error isolation, async batch, and diagnosis rules
import asyncio                                    # async runtime
import re
from dataclasses import dataclass


@dataclass
class Row:
    question: str
    contexts: list[str]
    answer: str
    reference: str


def _words(t: str) -> set[str]:
    return set(re.findall(r"[a-z0-9.]+", t.lower()))


def _ov(a: str, b: str) -> float:
    wa = _words(a)
    return len(wa & _words(b)) / len(wa) if wa else 0.0


async def score_row(row: Row) -> dict[str, float]:
    """Score one row. In production each line would be an async LLM-judge call."""
    await asyncio.sleep(0)                         # placeholder for network I/O
    joined = " ".join(row.contexts)
    return {
        "faithfulness": _ov(row.answer, joined),
        "answer_relevancy": _ov(row.question, row.answer),
        "context_recall": _ov(row.reference, joined),
        "context_precision": (sum(_ov(c, row.reference) > 0.5 for c in row.contexts)
                              / max(1, len(row.contexts))),
        "answer_correctness": _ov(row.reference, row.answer),
    }


def diagnose(s: dict[str, float], t: float = 0.6) -> str:
    """Turn scores into an action. Order matters: retrieval first."""
    if s["context_recall"] < t:
        return "RETRIEVER misses info -> improve chunking / top-k / hybrid search"
    if s["context_precision"] < t:
        return "RETRIEVER noisy -> add reranker / filters"
    if s["faithfulness"] < t:
        return "GENERATOR hallucinating -> tighten prompt, lower temperature"
    if s["answer_relevancy"] < t:
        return "GENERATOR off-topic -> fix instructions"
    return "healthy"


async def evaluate(rows: list[Row]) -> list[dict[str, float]]:
    results = await asyncio.gather(*(score_row(r) for r in rows), return_exceptions=True)
    clean: list[dict[str, float]] = []
    for r in results:
        if isinstance(r, Exception):               # one failing row must not kill the run
            print("row failed:", r)
        else:
            clean.append(r)
    return clean


async def main() -> None:
    rows = [Row("Duty on lithium-ion batteries?",
                ["HS 8507 lithium-ion batteries duty is 0 percent."],
                "Duty is 0 percent.", "Duty on lithium-ion batteries is 0 percent."),
            Row("Duty on cotton shirts?", ["HS 8507 lithium-ion batteries"],
                "It is 12 percent.", "Cotton shirts HS 6109 duty is 12 percent.")]
    for s in await evaluate(rows):
        print({k: round(v, 2) for k, v in s.items()}, "->", diagnose(s))


asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
# FastAPI: score one RAG interaction and return a diagnosis (usable as a QA hook)
from fastapi import FastAPI                        # framework
from pydantic import BaseModel, Field              # validation

app = FastAPI()


class EvalRequest(BaseModel):
    question: str
    contexts: list[str] = Field(min_length=1)      # at least one chunk
    answer: str
    reference: str                                 # gold answer


@app.post("/evaluate")
async def evaluate_endpoint(req: EvalRequest) -> dict:
    row = Row(req.question, req.contexts, req.answer, req.reference)
    scores = await score_row(row)                  # from the advanced example
    return {"scores": scores, "diagnosis": diagnose(scores)}
```

---

## 🔗 LangChain / LangGraph Connection
Ragas works directly with LangChain objects (LLM and embedding wrappers) and can evaluate LangChain/LangGraph app outputs.

```python
# Ragas (v0.2+) with a LangChain LLM - needs OPENAI_API_KEY, so shown not executed here
from ragas import evaluate, EvaluationDataset
from ragas.metrics import Faithfulness, ResponseRelevancy, LLMContextPrecisionWithReference, LLMContextRecall
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

dataset = EvaluationDataset.from_list([{
    "user_input": "Duty on lithium-ion batteries?",
    "retrieved_contexts": ["HS 8507 lithium-ion batteries duty is 0 percent."],
    "response": "Duty is 0 percent.",
    "reference": "Duty on lithium-ion batteries is 0 percent.",
}])
result = evaluate(
    dataset,
    metrics=[Faithfulness(), ResponseRelevancy(),
             LLMContextPrecisionWithReference(), LLMContextRecall()],
    llm=LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini")),
    embeddings=LangchainEmbeddingsWrapper(OpenAIEmbeddings()),
)
print(result)
```
In LangGraph, log the retrieved docs in graph state so evaluation can read both `contexts` and `answer` from the final state.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Reporting only answer quality
✅ Correct: Report retrieval and generation metrics separately.

```python
# Wrong
print({"quality": 0.7})
# Right
print({"context_recall": 0.5, "faithfulness": 0.95})   # -> retriever is the problem
```

❌ Mistake 2: Using a reference-free metric to claim correctness
✅ Correct: Faithfulness only says "supported by context", not "true". Wrong context gives a faithful but wrong answer. Use correctness against a reference for truth.

```python
# Wrong: faithfulness = 1.0 so the answer must be right
# Right: also check answer_correctness against the gold answer
```

❌ Mistake 3: Comparing scores across different judge models
✅ Correct: Keep the judge model fixed when comparing versions.

---

## 🧠 Tricky Interview Question

**Q**: "Faithfulness is 0.98 but answer correctness is 0.40. What is happening?"

**Answer**: The model is faithfully repeating the context, but the context is wrong or incomplete (retrieval problem). Check context recall and precision: probably the retriever fetched outdated or irrelevant chunks, so a perfectly "grounded" answer is still wrong. High faithfulness only proves the model did not invent facts beyond the context.

---

## ⚫ Interview Questions + Answers

Q1: Which metrics evaluate retrieval and which evaluate generation?
A1: Retrieval: context precision, context recall (and context relevancy). Generation: faithfulness, answer relevancy. Answer correctness evaluates the final output against a reference.

Q2: Do you always need a reference answer?
A2: No. Faithfulness, answer relevancy and context relevancy are reference-free. Context recall, reference-based precision and answer correctness need a ground-truth reference.

Q3: What does a score of 0.7 mean?
A3: It is a relative number from a judge, not a probability of truth. Compare it across versions on the same dataset; do not treat 0.7 as absolute.

Q4: Why do we use an LLM as the judge for these metrics?
A4: Text meaning cannot be checked by string match. A judge LLM can decompose an answer into claims and check each against context. The cost is tokens, latency and judge bias.

Q5 (Hard): Retrieval metrics look great but users still get bad answers. List possible causes.
A5: (1) Eval set unrepresentative of real queries. (2) Judge misses subtle errors (numbers, units). (3) The right chunk is retrieved but buried in a long context ("lost in the middle"). (4) Prompt allows the model to mix in outside knowledge. (5) Documents changed after the eval set was built. (6) Multi-hop questions need several chunks combined, while per-chunk metrics look fine. Investigate with failure sampling and human review of 30-50 failures.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You run a RAG system and need to decide what to fix
- Comparing chunk size, embedding model, reranker, prompt

❌ Avoid when:
- The app is not retrieval-based (use task-specific metrics instead)
- You have no test questions yet; start with a small golden set first

---

## 📊 Visual Diagram
```
 Question ─► [Retriever] ─► contexts ─► [LLM] ─► answer
                 │             │          │         │
                 │   context_precision    │   answer_relevancy
                 │   context_recall       │   faithfulness (answer vs contexts)
                 │                        │   answer_correctness (answer vs reference)
          RETRIEVAL metrics         GENERATION metrics
```

---

## 💰 Cost Impact
- Each LLM-judged metric makes 1-3 model calls per sample. Four metrics x 200 samples x ~1200 tokens is about 1M tokens: roughly $0.15 input + output cost on gpt-4o-mini, or about $2.50 on a gpt-4o-class model.
- Optimise: judge with a cheap model, evaluate a sample nightly and the full set weekly, cache by hash, skip metrics you will not act on, and run cheap non-LLM retrieval metrics (hit-rate, MRR) on all rows.
- Truncate contexts passed to the judge; long chunks multiply cost.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Faithfulness | Answer supported by context | Answer का context से समर्थित होना |
| Answer relevancy | Answer addresses the question | Answer का सवाल से जुड़ा होना |
| Context precision | Relevant chunks ranked high | सही chunks का ऊपर होना |
| Context recall | Contexts cover the reference | Contexts में पूरा जवाब होना |
| Reference | Gold/ground-truth answer | सही उत्तर (gold) |
| Reference-free | Needs no gold answer | बिना gold answer के |

---

## ⚡ 3-Line Summary
English: RAG metrics split into retrieval (precision, recall) and generation (faithfulness, relevancy, correctness). Reading their pattern tells you whether to fix the retriever or the prompt/model. Scores are relative, so compare versions with the same dataset and judge.
Hindi: RAG metrics दो भागों में हैं: retrieval (precision, recall) और generation (faithfulness, relevancy, correctness)। Pattern पढ़कर पता चलता है कि retriever ठीक करना है या prompt/model। Scores relative हैं, इसलिए same dataset और same judge से versions compare करो।

---

## ➡️ Next Topic
**391. Faithfulness Score** — the most important hallucination metric, explained claim by claim.
