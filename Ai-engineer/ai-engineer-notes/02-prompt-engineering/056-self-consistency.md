---

# 056. Self-Consistency
# हिंदी में: Self-Consistency

---

## 🔵 Simple Definition (English)
Self-consistency means asking the model the same question several times with some randomness (temperature above 0), then taking the most common final answer (majority vote). Different reasoning paths that reach the same answer give more confidence than one path.

## 🔵 सरल परिभाषा (Hindi)
Self-consistency में एक ही सवाल model से कई बार (temperature 0 से ऊपर, थोड़ी randomness के साथ) पूछा जाता है और सबसे ज़्यादा आने वाला final answer (majority vote) चुना जाता है। अलग-अलग reasoning रास्ते अगर एक ही answer पर पहुँचें तो एक रास्ते से ज़्यादा भरोसा मिलता है।

---

## 🔴 Problem it Solves
- A single CoT sample can be wrong by chance.
- With temperature 0 you get one answer and no confidence measure.
- Voting reduces random errors, and the vote share is a useful confidence score.

## 🔴 यह क्यों बना? (Hindi)
- एक CoT sample संयोग से गलत हो सकता है।
- Temperature 0 पर एक ही answer मिलता है और confidence का कोई माप नहीं।
- Voting random गलतियाँ घटाती है, और vote share एक उपयोगी confidence score है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Use a CoT-style prompt that ends with a parsable FINAL answer
Step 2 → Sample N times (for example 5) with temperature ~0.7
Step 3 → Parse the FINAL answer from each sample
Step 4 → Normalise answers (strip spaces, same format)
Step 5 → Count votes; the most frequent answer wins
Step 6 → Confidence = winner votes / valid votes
Step 7 → If confidence is low (for example < 0.6), escalate to human or a stronger model
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → CoT-style prompt लो जो parse होने लायक FINAL answer पर खत्म हो
Step 2 → temperature ~0.7 पर N बार (जैसे 5) sample करो
Step 3 → हर sample से FINAL answer parse करो
Step 4 → Answers normalise करो (spaces हटाओ, एक जैसा format)
Step 5 → Votes गिनो; सबसे ज़्यादा वाला जीतता है
Step 6 → Confidence = winner के votes / valid votes
Step 7 → Confidence कम (जैसे < 0.6) हो तो human या stronger model को भेजो
```

---

## 🟡 Real World Example
**Tariff Classification System**: For each item we sample 5 CoT answers. Item "Bluetooth speaker with FM radio": votes 8518 x4, 8527 x1, so answer 8518 with confidence 0.8, auto-approved. Item "kit with charger and holder": 8504 x2, 8517 x2, 8544 x1, confidence 0.4, so it goes to a human officer. We get both better accuracy and a trustworthy "needs review" flag.

**Zomato-style**: Estimating the cuisine type of a restaurant from messy descriptions: vote across samples.

## 🟡 Real Example Hindi mein
**Tariff System**: हर item के लिए 5 CoT answers sample करते हैं। Item "FM radio वाला Bluetooth speaker": 8518 x4, 8527 x1, इसलिए answer 8518, confidence 0.8, auto-approve। Item "charger और holder का kit": 8504 x2, 8517 x2, 8544 x1, confidence 0.4, इसलिए human officer के पास। हमें बेहतर accuracy और भरोसेमंद "review चाहिए" flag दोनों मिलते हैं।

**Zomato-style**: गंदे descriptions से restaurant की cuisine तय करना: samples में vote।

---

## 💻 Code Example — Basic
```python
# Basic: majority vote over several samples (mock sampler, runs offline)
import random  # to simulate randomness
from collections import Counter  # vote counting

random.seed(7)  # reproducible demo

def mock_sample(product: str) -> str:
    # Pretend the model is right 70% of the time, otherwise picks another code
    return "8518" if random.random() < 0.7 else random.choice(["8527", "8517"])

def self_consistency(product: str, n: int = 5) -> tuple[str, float, Counter]:
    answers = [mock_sample(product) for _ in range(n)]  # n independent samples
    votes = Counter(answers)  # count each answer
    winner, count = votes.most_common(1)[0]  # most frequent answer
    return winner, count / n, votes  # answer, confidence, raw votes

answer, conf, votes = self_consistency("Bluetooth speaker with FM radio")
print("Votes:", dict(votes))  # distribution
print(f"Answer: {answer}  confidence: {conf:.2f}")  # decision + confidence
print("Route:", "auto" if conf >= 0.6 else "human review")  # simple routing rule
```

## 💻 Code Example — Advanced
```python
# Production-style: async self-consistency using n= in one request, with parsing and confidence
import asyncio  # async runtime
import re  # parse FINAL
from collections import Counter  # voting
from dataclasses import dataclass  # result object
from openai import AsyncOpenAI, APIError  # openai>=1

client = AsyncOpenAI(timeout=30.0)  # shared client
FINAL_RE = re.compile(r"FINAL:\s*(\d{4})\s*$", re.MULTILINE)  # answer pattern

SYSTEM = ("You are a customs classifier. Reason in at most 4 short lines, "
          "then end with: FINAL: <4-digit heading>")

@dataclass
class Vote:
    answer: str | None  # winning answer
    confidence: float  # winner share of valid votes
    votes: dict[str, int]  # full distribution
    tokens: int  # total tokens (cost tracking)

async def self_consistent(product: str, n: int = 5) -> Vote:
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini", n=n,  # n samples in ONE request: input billed once
            temperature=0.7, max_tokens=200,
            messages=[{"role": "system", "content": SYSTEM},
                      {"role": "user", "content": product}])
    except APIError:
        return Vote(None, 0.0, {}, 0)  # caller routes to review
    answers: list[str] = []
    for choice in resp.choices:  # parse each sample
        m = FINAL_RE.search((choice.message.content or "").strip())
        if m:
            answers.append(m.group(1))
    if not answers:  # nothing parsable
        return Vote(None, 0.0, {}, resp.usage.total_tokens)
    counts = Counter(answers)
    winner, wins = counts.most_common(1)[0]
    return Vote(winner, wins / len(answers), dict(counts), resp.usage.total_tokens)

# print(asyncio.run(self_consistent("Bluetooth speaker with FM radio")))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel, Field  # validation

app = FastAPI()  # app

class Q(BaseModel):
    product: str = Field(min_length=3, max_length=500)  # product text
    samples: int = Field(default=5, ge=1, le=9)  # limit samples to control cost

@app.post("/classify-vote")
async def classify_vote(q: Q) -> dict:
    v = await self_consistent(q.product, n=q.samples)  # run voting
    decision = "auto" if v.answer and v.confidence >= 0.6 else "human_review"
    return {"answer": v.answer, "confidence": round(v.confidence, 2),
            "votes": v.votes, "decision": decision, "tokens": v.tokens}
```

---

## 🔗 LangChain / LangGraph Connection
In LangChain, run the chain N times with `abatch([input] * n)` (set temperature above 0) and vote in a final function; in LCEL: `RunnableLambda(vote)` after the batch. In LangGraph, a "sample" node can fan out (parallel branches via `Send`) and a "vote" node reduces results.

```python
from collections import Counter  # voting
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_core.runnables import RunnableLambda  # custom step
from langchain_openai import ChatOpenAI  # model

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)  # randomness is needed
prompt = ChatPromptTemplate.from_messages([("system", "Answer with only a 4-digit HS heading."),
                                           ("human", "{p}")])
one = prompt | llm | RunnableLambda(lambda m: m.content.strip())  # one sample -> string

def vote(answers: list[str]) -> tuple[str, float]:
    top, c = Counter(answers).most_common(1)[0]  # winner and count
    return top, c / len(answers)

# answers = await one.abatch([{"p": "Bluetooth speaker"}] * 5)  # 5 parallel samples
# print(vote(answers))
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using temperature 0
✅ Correct: Use some randomness, or all samples are identical.

```python
# Wrong: temperature=0, n=5   # five copies of the same answer
# Right: temperature=0.7, n=5
```

❌ Mistake 2: Voting on free-form text
✅ Correct: Vote on a short normalised final answer (code, label, number).

```python
# Wrong: Counter(full_paragraphs)   # no two strings equal
# Right: Counter(parse_final(x) for x in samples)
```

---

## 🧠 Tricky Interview Question
**Q**: "All 5 samples agree (confidence 1.0) but the answer is wrong. Is self-consistency broken?"

**Answer**: No, but agreement is not correctness. Samples come from the same model, so they share the same systematic bias or knowledge gap (correlated errors). Voting only fixes random errors. Fix systematic errors with better prompts, retrieval of the legal notes, tools, different models in the ensemble, or a verifier against ground truth. Calibrate: measure on a labelled set how often confidence 1.0 is actually right.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is self-consistency?
A1: Sample multiple reasoning answers and choose the most frequent final answer.

Q2: [Easy] Why do we need temperature above 0?
A2: To get diverse reasoning paths. At temperature 0 all samples would be nearly identical.

Q3: [Medium] How is it different from Tree of Thought?
A3: Self-consistency samples independent full chains and votes at the end. ToT builds and prunes branches step by step with evaluation. Self-consistency is simpler and parallelisable.

Q4: [Medium] How do you use the vote share?
A4: As a confidence score for routing: high agreement auto-approve, low agreement go to a human or a stronger model.

Q5: [Hard] How do you reduce its cost?
A5: Use `n=` in a single request so input tokens are billed once, limit reasoning length, use a small model, use adaptive sampling (stop early when the first 3 agree), and apply it only to hard or high-value items.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Answers are short and checkable (labels, numbers, codes)
- You want a confidence estimate

❌ Avoid when:
- Open-ended text (no clear vote)
- Tight latency/cost budgets, or the model has systematic bias

---

## 📊 Visual Diagram
```
 Question ─┬─► sample 1 ─► 8518
           ├─► sample 2 ─► 8518
           ├─► sample 3 ─► 8527
           ├─► sample 4 ─► 8518
           └─► sample 5 ─► 8518
                         │
                    majority vote
                         ▼
             8518  (confidence 4/5 = 0.8)
```

---

## 💰 Cost Impact
- Output tokens grow N times (N samples x reasoning length). With `n=` in one request, the input prompt is billed once, but each sample's output is billed.
- Example: 200 output tokens x 5 samples = 1,000 tokens per item (5x). Illustrative `gpt-4o-mini`: 100,000 items x 1,000 x $0.60/1M = $60/day vs $12/day for a single sample.
- Optimise: adaptive stopping, apply only when a quick pass has low confidence, short reasoning, cache.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Self-consistency | Sample many, vote | कई बार sample करके vote |
| Majority vote | Most frequent answer wins | सबसे ज़्यादा वाला answer |
| Sampling | Random generation | Random generation |
| Confidence | Agreement share | सहमति का अनुपात |
| Correlated errors | Same mistake repeats | एक ही गलती बार-बार |
| Adaptive stopping | Stop when agreement reached | सहमति मिलते ही रुकना |

---

## ⚡ 3-Line Summary
English: Sample several reasoning answers and take the majority vote. The vote share gives a useful confidence score. Cost rises with N and it cannot fix systematic errors.
Hindi: कई reasoning answers sample करके majority vote लो। Vote share से उपयोगी confidence score मिलता है। N बढ़ने से cost बढ़ती है और systematic errors ठीक नहीं होतीं।

---

## ➡️ Next Topic
**057. ReAct Prompting** — interleave reasoning with actions (tool calls) to ground answers in real data.
