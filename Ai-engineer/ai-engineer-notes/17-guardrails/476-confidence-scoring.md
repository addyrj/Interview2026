
---

# 476. Confidence Scoring
# हिंदी में: Confidence Scoring

---

## 🔵 Simple Definition (English)
Confidence scoring attaches a number (0 to 1) to an LLM answer that says how much we should trust it. Sources of signal: token log-probabilities, agreement across multiple samples, retrieval similarity scores, validation checks (does the HS code exist?), and a judge model. The score decides: auto-answer, add a warning, or send to a human.

## 🔵 सरल परिभाषा (Hindi)
Confidence scoring LLM answer के साथ 0 से 1 का एक number जोड़ता है जो बताता है कि answer पर कितना भरोसा करें। Signals: token log-probabilities, कई samples में सहमति, retrieval similarity, validation checks (क्या HS code मौजूद है?), और judge model। Score तय करता है: auto-answer, warning, या human को भेजना।

---

## 🔴 Problem it Solves
LLMs sound equally confident when right and when wrong. Without a score, every answer is treated the same, so wrong classifications reach customers. With a score we can automate the easy 80% and route the uncertain 20% to review, balancing cost, speed and risk.

## 🔴 यह क्यों बना? (Hindi)
LLM सही और ग़लत दोनों में एक जैसे आत्मविश्वास से बोलता है। Score के बिना हर answer एक जैसा माना जाता है और ग़लत classification customers तक पहुँचती है। Score से आसान 80% automate और अनिश्चित 20% review में भेजे जा सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Generate the answer (ask for structured output: code + reason)
Step 2 → Signal A: logprobs of the key tokens (e.g. the HS code digits)
Step 3 → Signal B: self-consistency, sample N times, measure agreement
Step 4 → Signal C: retrieval score (is the answer supported by top chunks?)
Step 5 → Signal D: hard checks (code exists in tariff table, format valid)
Step 6 → Combine into one score (weighted or a small calibrated model)
Step 7 → Thresholds: >= 0.85 auto, 0.5-0.85 warn/review, < 0.5 fallback
Step 8 → Calibrate against labelled data so 0.9 really means ~90% correct
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Answer generate करो (structured output: code + reason)
Step 2 → Signal A: key tokens (HS code digits) के logprobs
Step 3 → Signal B: N बार sample करके agreement नापो
Step 4 → Signal C: retrieval score (क्या top chunks answer को support करते हैं?)
Step 5 → Signal D: hard checks (code tariff table में है, format सही है)
Step 6 → सबको एक score में मिलाओ
Step 7 → Thresholds: >= 0.85 auto, 0.5-0.85 warn/review, < 0.5 fallback
Step 8 → Labelled data से calibrate करो कि 0.9 का मतलब सच में ~90% सही हो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The model proposes HS 8517.13. Logprob probability is 0.97, 5 of 5 samples agree, the code exists in the official table and the top retrieved chunk mentions smartphones: score 0.95, auto-answer. For "multi-function printer with fax", samples split between 8443 and 8517: score 0.55, route to a customs expert. **Amazon-style**: product category auto-tagging uses the score to decide which items get human review.

## 🟡 Real Example Hindi mein
**Tariff System**: Model HS 8517.13 बताता है। Logprob probability 0.97, 5 में से 5 samples सहमत, code official table में है और top chunk में smartphones लिखा है: score 0.95, auto-answer। "Fax वाला multi-function printer" में samples 8443 और 8517 में बँटते हैं: score 0.55, customs expert के पास। **Amazon-style**: product category tagging में score तय करता है किन items को human review मिले।

---

## 💻 Code Example — Basic
```python
# Basic: combine signals into one confidence score (pure Python, runs offline)
import math                                                # exp() for logprob -> probability
from collections import Counter                            # count votes

def logprob_to_prob(logprobs: list[float]) -> float:
    return math.exp(sum(logprobs) / len(logprobs))         # geometric mean token probability

def agreement(samples: list[str]) -> float:
    top, count = Counter(samples).most_common(1)[0]        # most frequent answer
    return count / len(samples)                            # fraction that agree

def combine(p_tokens: float, agree: float, valid: bool, retrieval: float) -> float:
    if not valid:                                          # invalid code = no confidence
        return 0.0
    return round(0.35 * p_tokens + 0.35 * agree + 0.30 * retrieval, 3)   # illustrative weights

score = combine(
    p_tokens=logprob_to_prob([-0.02, -0.05, -0.01]),       # confident tokens
    agree=agreement(["8517.13"] * 5),                      # 5/5 agree
    valid=True,                                            # exists in tariff table
    retrieval=0.88,                                        # top chunk similarity
)
print(score)                                               # high score -> auto answer
```

## 💻 Code Example — Advanced
```python
# Production: async confidence scoring with logprobs + self-consistency + validation
import asyncio                                             # parallel samples
import math                                                # exp
from collections import Counter                            # voting
from dataclasses import dataclass                          # result type
from openai import AsyncOpenAI                             # client

client = AsyncOpenAI()                                     # shared client
VALID = {"8517.13", "8471.30", "8443.31"}                  # demo; use the full tariff table

@dataclass
class Scored:
    code: str                                              # chosen HS code
    confidence: float                                      # 0..1
    action: str                                            # auto / review / fallback

async def one_sample(question: str, temperature: float) -> tuple[str, float]:
    r = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=temperature, max_tokens=12,
        logprobs=True,                                     # ask for token logprobs
        messages=[{"role": "system", "content": "Reply with ONLY the 6-digit HS code like 8517.13."},
                  {"role": "user", "content": question}],
    )
    choice = r.choices[0]
    code = (choice.message.content or "").strip()          # the answer
    lps = [t.logprob for t in (choice.logprobs.content or [])]   # per-token logprobs
    p = math.exp(sum(lps) / len(lps)) if lps else 0.0      # avg token probability
    return code, p

async def score_answer(question: str, retrieval_score: float, n: int = 5) -> Scored:
    try:
        results = await asyncio.gather(*(one_sample(question, 0.7) for _ in range(n)))   # n samples
    except Exception:
        return Scored("", 0.0, "fallback")                 # provider error
    codes = [c for c, _ in results]
    top, votes = Counter(codes).most_common(1)[0]          # majority answer
    p_tok = sum(p for c, p in results if c == top) / max(votes, 1)   # avg prob of the winners
    if top not in VALID:
        return Scored(top, 0.0, "review")                  # failed hard check
    conf = 0.35 * p_tok + 0.35 * (votes / n) + 0.30 * retrieval_score
    action = "auto" if conf >= 0.85 else "review" if conf >= 0.5 else "fallback"
    return Scored(top, round(conf, 3), action)
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI                                # framework
from pydantic import BaseModel                             # schema

app = FastAPI()

class Q(BaseModel):
    question: str                                          # user question

@app.post("/classify")
async def classify(body: Q) -> dict:
    s = await score_answer(body.question, retrieval_score=0.85)   # retrieval score from your RAG step
    if s.action == "auto":
        return {"hs_code": s.code, "confidence": s.confidence}    # confident answer
    if s.action == "review":
        return {"hs_code": s.code, "confidence": s.confidence, "needs_review": True}   # human queue
    return {"message": "Not sure. Please provide more product details.", "confidence": s.confidence}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain chat models can return logprobs via `.bind(logprobs=True)`; check `response.response_metadata["logprobs"]`. In LangGraph, add a **confidence gate** node with conditional edges to "auto answer", "human review" (using `interrupt`) or "fallback".

```python
from langchain_openai import ChatOpenAI                    # chat model

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind(logprobs=True)   # request logprobs
msg = await llm.ainvoke("HS code for smartphone? Reply code only.")
lp = msg.response_metadata.get("logprobs")                 # token logprobs when supported

def gate(state: dict) -> str:                              # conditional edge function
    c = state["confidence"]
    return "answer" if c >= 0.85 else "human_review" if c >= 0.5 else "fallback"
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Asking the model "how confident are you?" and trusting it
```python
# Wrong — verbalised confidence is often overconfident and uncalibrated:
conf = float(llm("Rate your confidence 0-1"))

# Correct — use measurable signals (logprobs, agreement, validation) and calibrate on labels
```

❌ Mistake 2: Using an uncalibrated threshold
```python
# Wrong — "0.8 sounds good"
# Correct — pick the threshold from a labelled set so accuracy above it meets your target
```

❌ Mistake 3: Logprob of the whole sentence
```python
# Wrong — long explanations dilute the signal
# Correct — score only the decision tokens (the code), force short structured output
```

---

## 🧠 Tricky Interview Question
**Q**: "Logprobs show 0.99 probability for the answer, yet it is wrong. How is that possible, and what do you do?"

**Answer**: Token probability measures how likely the model finds the text given its training and context, not whether it is true. Models can be confidently wrong (a familiar-looking but outdated code, or a misleading retrieved chunk). Also RLHF-tuned models are often overconfident. Fix: combine independent signals (validation against ground truth, retrieval support, self-consistency), calibrate on labelled data (e.g. isotonic regression, reliability diagram), and measure Expected Calibration Error. High confidence plus failed validation must lead to rejection.

---

## ⚫ Interview Questions + Answers

Q1: What is a confidence score used for?
A1: To decide whether to auto-answer, warn, or escalate to a human/fallback.

Q2: Name three signals for confidence.
A2: Token logprobs, agreement across samples (self-consistency), retrieval/validation checks.

Q3: What is calibration?
A3: Making scores match reality: among answers scored 0.8, about 80% should be correct. Check with a reliability diagram or ECE.

Q4: What is the cost of self-consistency?
A4: N times the output cost (and input if not cached). Use it only for uncertain or high-value cases, or sample cheaply with a small model.

Q5: (Hard) Design a confidence-based routing system for 1M classifications/day.
A5: Single cheap pass with logprobs and validation for everyone; run multi-sample consistency only if the first score is in a grey zone; send low scores to a stronger model, then to humans. Calibrate monthly using human-reviewed labels; track auto-rate, error rate among auto answers and review queue size to tune thresholds.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Wrong answers are costly and a human fallback exists
- Volume is high and you want to automate the easy part

❌ Avoid when:
- Free-form creative text with no ground truth
- You cannot get labelled data to calibrate (scores would be misleading)

---

## 📊 Visual Diagram
```
 answer ─► logprobs ─┐
 answer ─► samples ──┤
 answer ─► retrieval ┼─► combine ─► confidence
 answer ─► validation┘                │
                          ┌───────────┼────────────┐
                       >= 0.85     0.5-0.85       < 0.5
                          │           │             │
                       auto        review        fallback
```

---

## 💰 Cost Impact
- Logprobs are free with the same call (slightly larger response). Self-consistency multiplies output tokens by N (5 samples of ~10 tokens is small for code-only answers, but large for long answers).
- Savings: automating 80% of cases removes human review cost, which is usually far higher than tokens.
- Optimise: short structured outputs, `max_tokens` tiny, sample only in the grey zone, cheap model first then escalate.
- Prices illustrative.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Confidence score | Trust level of an answer | answer पर भरोसे का स्तर |
| Logprob | Log probability of a token | token की log probability |
| Self-consistency | Agreement across samples | samples में सहमति |
| Calibration | Scores match real accuracy | score और सच्चाई का मेल |
| ECE | Expected Calibration Error | calibration की ग़लती |
| Threshold | Cut-off for decisions | निर्णय की सीमा |

---

## ⚡ 3-Line Summary
English: Confidence scores combine logprobs, sample agreement, retrieval support and hard validation. Calibrate on labelled data and route by threshold: auto, review, fallback. Do not trust the model's own verbal confidence.
Hindi: Confidence score logprobs, sample agreement, retrieval support और hard validation को मिलाता है। Labelled data से calibrate करो और threshold से route करो: auto, review, fallback। Model के खुद बताए confidence पर भरोसा मत करो।

---

## ➡️ Next Topic
**477. Uncertainty Quantification** — a deeper look at types of uncertainty and how to measure them.
