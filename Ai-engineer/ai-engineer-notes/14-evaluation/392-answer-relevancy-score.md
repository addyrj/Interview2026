---

# 392. Answer Relevancy Score
# हिंदी में: Answer Relevancy Score

---

## 🔵 Simple Definition (English)
Answer relevancy measures how directly the answer addresses the user's question. An answer that is correct but off-topic, incomplete, or full of unnecessary text scores low. It does not check facts; it checks "did you answer what was asked?".

## 🔵 सरल परिभाषा (Hindi)
Answer relevancy नापता है कि answer user के सवाल का सीधा जवाब कितना देता है। सही पर off-topic, अधूरा या फालतू text से भरा answer कम score पाता है। ये facts नहीं जाँचता; ये जाँचता है "जो पूछा गया वही बताया?"।

---

## 🔴 Problem it Solves
A RAG bot can produce a faithful, well-written paragraph that does not answer the question. User asks "What is the duty on lithium batteries?" and the bot explains the history of HS codes. Faithfulness is 1.0, yet the user is unhappy. Relevancy catches this drift and also over-long rambling.

## 🔴 यह क्यों बना? (Hindi)
RAG bot faithful और अच्छा paragraph लिख सकता है जो सवाल का जवाब नहीं देता। User पूछता है "lithium batteries पर duty कितनी है?" और bot HS codes का इतिहास समझाने लगता है। Faithfulness 1.0 है, फिर भी user नाखुश है। Relevancy इस भटकाव और बेवजह लंबे जवाब को पकड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Take the original question and the generated answer
Step 2 → LLM generates N artificial questions (e.g. 3) that the answer would respond to
Step 3 → Embed the original question and each generated question
Step 4 → Compute cosine similarity between original and each generated question
Step 5 → answer_relevancy = mean of the similarities
Step 6 → Off-topic answers produce questions unlike the original, so similarity drops
        (Ragas also gives 0 when the answer is "noncommittal" like "I don't know")
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Original सवाल और generated answer लो
Step 2 → LLM N नकली सवाल बनाता है (जैसे 3) जिनका जवाब ये answer होगा
Step 3 → Original सवाल और हर generated सवाल का embedding बनाओ
Step 4 → Original और हर generated सवाल के बीच cosine similarity निकालो
Step 5 → answer_relevancy = इन similarities का mean
Step 6 → Off-topic answer से ऐसे सवाल बनते हैं जो original से अलग होते हैं, इसलिए similarity गिरती है
        (Ragas "I don't know" जैसे noncommittal answer पर 0 देता है)
```

---

## 🟡 Real World Example
**Tariff Classification System**
Question: "What is the duty on lithium-ion batteries?"
Answer A: "The basic customs duty on lithium-ion batteries is 0 percent." -> generated question: "What is the customs duty on lithium-ion batteries?" -> similarity 0.95.
Answer B: "HS codes were created by the World Customs Organization in 1988 and have 6 digits..." -> generated question: "Who created HS codes?" -> similarity 0.30.
A is relevant, B is faithful maybe, but irrelevant.

**Zomato AI**: Asked "veg options under 200 rupees" the bot lists the full menu including non-veg: partly relevant.

## 🟡 Real Example Hindi mein
**Tariff System**
सवाल: "lithium-ion batteries पर duty कितनी है?"
Answer A: "Lithium-ion batteries पर basic customs duty 0 percent है।" -> generated सवाल: "lithium-ion batteries पर customs duty क्या है?" -> similarity 0.95।
Answer B: "HS codes 1988 में World Customs Organization ने बनाए और इनमें 6 digits होते हैं..." -> generated सवाल: "HS codes किसने बनाए?" -> similarity 0.30।
A relevant है; B शायद faithful हो पर irrelevant है।

**Zomato AI**: "200 रुपये से कम veg options" पूछने पर bot non-veg समेत पूरा menu दिखाए: आंशिक relevant।

---

## 💻 Code Example — Basic
```python
# Basic: relevancy via bag-of-words cosine similarity (offline teaching version).
# The real metric uses LLM-generated questions + embeddings; the math (cosine) is the same.
import math
import re
from collections import Counter


def vec(text: str) -> Counter[str]:
    """Word-count vector."""
    return Counter(re.findall(r"[a-z0-9]+", text.lower()))


def cosine(a: Counter[str], b: Counter[str]) -> float:
    """Cosine similarity between two count vectors."""
    dot = sum(a[w] * b[w] for w in a)                  # shared words
    na = math.sqrt(sum(v * v for v in a.values()))     # length of a
    nb = math.sqrt(sum(v * v for v in b.values()))     # length of b
    return dot / (na * nb) if na and nb else 0.0


def relevancy(question: str, generated_questions: list[str]) -> float:
    """Mean cosine between the original question and questions implied by the answer."""
    q = vec(question)
    sims = [cosine(q, vec(g)) for g in generated_questions]
    return sum(sims) / len(sims) if sims else 0.0


question = "What is the duty on lithium-ion batteries?"
# In real life an LLM writes these from the answer; hard-coded here:
good = ["What is the customs duty on lithium-ion batteries?",
        "How much duty applies to lithium-ion batteries?"]
bad = ["Who created HS codes?", "How many digits does an HS code have?"]
print("relevant answer  :", round(relevancy(question, good), 2))
print("off-topic answer :", round(relevancy(question, bad), 2))
```

## 💻 Code Example — Advanced
```python
# Advanced: async relevancy with injectable question-generator and embedder + noncommittal handling.
# In production: generator = LLM call, embedder = OpenAI embeddings. Fakes keep this runnable offline.
import asyncio
import math
from typing import Awaitable, Callable

GenFn = Callable[[str, int], Awaitable[list[str]]]    # (answer, n) -> questions
EmbFn = Callable[[list[str]], Awaitable[list[list[float]]]]   # texts -> vectors

NONCOMMITTAL = ("i don't know", "i do not know", "cannot answer", "not sure")


def cos(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


async def answer_relevancy(question: str, answer: str, gen: GenFn, emb: EmbFn,
                           n: int = 3) -> float:
    if any(p in answer.lower() for p in NONCOMMITTAL):
        return 0.0                                     # evasive answer: not relevant
    try:
        generated = await gen(answer, n)               # step 2
        vectors = await emb([question, *generated])    # step 3 (one batched call)
    except Exception as exc:                           # network/API failure
        raise RuntimeError(f"relevancy scoring failed: {exc}") from exc
    q_vec, g_vecs = vectors[0], vectors[1:]
    sims = [cos(q_vec, g) for g in g_vecs]             # step 4
    return sum(sims) / len(sims) if sims else 0.0      # step 5


# ---- offline fakes ----
async def fake_gen(answer: str, n: int) -> list[str]:
    return ["What is the customs duty on batteries?"] * n


async def fake_emb(texts: list[str]) -> list[list[float]]:
    vocab = ["duty", "customs", "batteries", "lithium", "hs", "code"]
    return [[float(t.lower().count(w)) for w in vocab] for t in texts]


async def main() -> None:
    s = await answer_relevancy("What is the duty on lithium batteries?",
                               "Duty on batteries is 0 percent.", fake_gen, fake_emb)
    print(round(s, 2))
    print(await answer_relevancy("q", "I don't know", fake_gen, fake_emb))   # 0.0


asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
# FastAPI: attach a relevancy score to each response and log low scores for review
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
review_queue: list[dict] = []                          # use a DB/queue in production


class Q(BaseModel):
    question: str


@app.post("/ask")
async def ask(body: Q) -> dict:
    answer = "Duty on batteries is 0 percent."         # your RAG call
    score = await answer_relevancy(body.question, answer, fake_gen, fake_emb)
    if score < 0.6:                                    # suspicious: save for human review
        review_queue.append({"q": body.question, "a": answer, "score": score})
    return {"answer": answer, "relevancy": round(score, 2)}
```

---

## 🔗 LangChain / LangGraph Connection
Ragas ships this metric as `ResponseRelevancy` (earlier named `AnswerRelevancy`) and needs both an LLM and an embeddings model.

```python
# Ragas + LangChain wrappers (needs OPENAI_API_KEY; shown for reference)
from ragas import SingleTurnSample
from ragas.metrics import ResponseRelevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

metric = ResponseRelevancy(
    llm=LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini")),
    embeddings=LangchainEmbeddingsWrapper(OpenAIEmbeddings()),
)
sample = SingleTurnSample(
    user_input="What is the duty on lithium-ion batteries?",
    response="Basic customs duty is 0 percent.",
    retrieved_contexts=["HS 8507 duty 0 percent."],
)
# score = await metric.single_turn_ascore(sample)   # run inside async code
```
In LangGraph, add a "relevancy check" node after generation; if low, route back to rewrite the prompt with the original question restated.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting relevancy to detect wrong facts
✅ Correct: A confident wrong answer to the right question scores high on relevancy. Pair with faithfulness/correctness.

```python
# Wrong
assert relevancy > 0.9   # "answer is good"
# Right
assert relevancy > 0.9 and faithfulness > 0.9
```

❌ Mistake 2: Forgetting the embeddings model needs to be consistent
✅ Correct: Use the same embedding model across runs, otherwise scores are not comparable.

```python
# Wrong: run1 text-embedding-3-small, run2 ada-002 and compare scores
# Right: fix the embedding model in config
EMBED_MODEL = "text-embedding-3-small"
```

❌ Mistake 3: Ignoring verbose answers
✅ Correct: Long padded answers lower relevancy; tell the prompt to be concise.

---

## 🧠 Tricky Interview Question

**Q**: "Your bot returns 'I don't know' for 30 percent of questions. Faithfulness is 1.0. Relevancy is 0.5. Is the system healthy?"

**Answer**: No. Abstentions are faithful (no claims) but not useful, and relevancy correctly penalises them (noncommittal gets 0). Check context recall: if the info exists in the knowledge base but the retriever missed it, that is a retrieval defect. Track abstention rate as its own KPI and set a target. Also verify that abstentions are justified, because a safe-but-useless bot passes faithfulness trivially.

---

## ⚫ Interview Questions + Answers

Q1: What does answer relevancy measure?
A1: How well the answer addresses the question, penalising incomplete, redundant or off-topic content. It does not measure factual correctness.

Q2: Does it need a reference answer?
A2: No. It only uses the question and the generated answer (plus embeddings), so it works on live traffic.

Q3: Explain the Ragas computation.
A3: An LLM generates several questions from the answer; embeddings of those questions are compared to the embedding of the original question by cosine similarity, and the mean is the score.

Q4: Why generate questions instead of directly asking the LLM "is this relevant?"
A4: Reverse-question generation is more objective and less prone to judge leniency: if the answer's implied questions match the real question, it is relevant. Direct yes/no scoring is more variable.

Q5 (Hard): A relevant, faithful answer gets low relevancy because it is very detailed. Is the metric wrong?
A5: Extra details create generated questions about side topics, reducing similarity. The metric is working as designed (it penalises unrequested content), but whether that is a defect depends on product needs. If detail is wanted, adjust the prompt/test set or use a rubric-based judge (G-Eval) with criteria such as "answers the question and gives needed detail". Always inspect examples before changing thresholds.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Detecting off-topic or rambling answers
- Comparing prompt versions for conciseness/focus
- Reference-free monitoring in production

❌ Avoid when:
- You need factual accuracy (use faithfulness / correctness)
- Answers are intentionally long-form (reports), unless you adapt the rubric

---

## 📊 Visual Diagram
```
 Question ──────────────────────────────┐
                                        ▼ embed
 Answer ──► LLM ──► generated Q1,Q2,Q3 ─► embed ─► cosine(Q, Qi)
                                                       │
                                  answer_relevancy = mean(similarities)
 on-topic  : Q1..Q3 ≈ original  → ~0.9
 off-topic : Q1..Q3 ≠ original  → ~0.3
```

---

## 💰 Cost Impact
- One LLM call generates N questions (about 300-800 input tokens, 100-200 output) plus one embedding call over N+1 short texts (a few hundred tokens at about $0.02 per 1M for text-embedding-3-small). Total roughly $0.0002 per sample on gpt-4o-mini.
- 1,000 evaluation rows cost about $0.20-0.40.
- Optimise: set N=3 (not 10), batch embeddings, cache embeddings of repeated questions, and run on a sample in production.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Answer relevancy | Answer addresses the question | Answer का सवाल से जुड़ा होना |
| Cosine similarity | Angle-based similarity of vectors | Vectors की समानता नापने का तरीका |
| Embedding | Numeric vector of text meaning | Text के मतलब का number vector |
| Noncommittal | Evasive answer like "don't know" | टालमटोल वाला जवाब |
| Reference-free | No gold answer needed | Gold answer की ज़रूरत नहीं |
| Off-topic | Not related to the question | सवाल से हटकर |

---

## ⚡ 3-Line Summary
English: Answer relevancy checks that the answer actually responds to the question, using questions generated back from the answer and cosine similarity. It ignores factual truth, so pair it with faithfulness. It works without reference answers and costs very little.
Hindi: Answer relevancy जाँचता है कि answer सच में सवाल का जवाब देता है, answer से वापस बनाए सवालों और cosine similarity से। ये तथ्यों की सच्चाई नहीं देखता, इसलिए faithfulness के साथ use करो। इसे reference answer नहीं चाहिए और cost बहुत कम है।

---

## ➡️ Next Topic
**393. Context Precision Score** — now the retrieval side: are the useful chunks ranked at the top?
