
---

# 477. Uncertainty Quantification
# हिंदी में: Uncertainty Quantification (अनिश्चितता मापना)

---

## 🔵 Simple Definition (English)
Uncertainty quantification (UQ) measures **how unsure** a model is and **why**. Two kinds: **aleatoric** (the question itself is ambiguous or noisy, so more data will not fix it) and **epistemic** (the model lacks knowledge, which more data or retrieval can fix). For LLMs we estimate it with sampling entropy, logprob entropy, semantic agreement and ensembles.

## 🔵 सरल परिभाषा (Hindi)
Uncertainty quantification (UQ) मापता है कि model **कितना अनिश्चित** है और **क्यों**। दो प्रकार: **aleatoric** (सवाल ख़ुद अस्पष्ट है, ज़्यादा data से हल नहीं होगा) और **epistemic** (model को ज्ञान नहीं है, ज़्यादा data या retrieval से हल हो सकता है)। LLM में इसे sampling entropy, logprob entropy, semantic agreement और ensembles से नापते हैं।

---

## 🔴 Problem it Solves
Confidence scores (476) give a number, but not the reason. A low score may mean "the product description is vague" (ask the user for more details) or "the model does not know this code" (retrieve more documents or escalate). Different causes need different fixes. UQ also catches hallucinations: made-up facts tend to vary between samples.

## 🔴 यह क्यों बना? (Hindi)
Confidence score (476) number देता है, कारण नहीं। कम score का मतलब हो सकता है "product description अस्पष्ट है" (user से और details माँगो) या "model को यह code पता नहीं" (और documents retrieve करो या escalate करो)। अलग कारण, अलग इलाज। UQ hallucinations भी पकड़ता है: गढ़े हुए facts अलग-अलग samples में बदलते रहते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Sample the model N times at temperature > 0 for the same question
Step 2 → Group answers by meaning (exact match for codes; embeddings/NLI for text)
Step 3 → Compute entropy over the groups: many groups = high uncertainty
Step 4 → Also compute token-level entropy from top-k logprobs for the key tokens
Step 5 → Diagnose: do answers differ because of ambiguity (aleatoric)?
        e.g. user text fits two products
Step 6 → Or because of missing knowledge (epistemic)? e.g. random different codes
Step 7 → Act: ask clarifying question / retrieve more / escalate / abstain
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक ही सवाल पर temperature > 0 के साथ N बार sample करो
Step 2 → Answers को meaning से group करो (codes के लिए exact match)
Step 3 → Groups पर entropy निकालो: ज़्यादा groups = ज़्यादा uncertainty
Step 4 → Key tokens पर top-k logprobs से token entropy भी निकालो
Step 5 → पहचानो: answers अस्पष्टता (aleatoric) की वजह से अलग हैं?
Step 6 → या ज्ञान की कमी (epistemic) की वजह से? जैसे हर बार अलग random code
Step 7 → Action: clarifying question / और retrieval / escalate / abstain
```

---

## 🟡 Real World Example
**Tariff Classification System**: "Classify: cable". Samples: 8544, 8544, 8536, 8517 (high entropy). Since the description is vague (aleatoric), the system asks "Is it a power cable, HDMI cable or fibre-optic cable?" Another case: a rare chemical. Samples give 5 unrelated codes with no retrieval support (epistemic), so the system retrieves more context or escalates to an expert. **Zomato-style**: "send my order to home" with two saved addresses: ask which one.

## 🟡 Real Example Hindi mein
**Tariff System**: "Classify: cable"। Samples: 8544, 8544, 8536, 8517 (high entropy)। Description अस्पष्ट है (aleatoric), इसलिए system पूछता है "Power cable, HDMI cable या fibre-optic cable?" दूसरा case: rare chemical। 5 अलग-अलग codes और retrieval support नहीं (epistemic), इसलिए और context retrieve करो या expert को भेजो। **Zomato-style**: दो saved addresses हैं, "order घर भेजो" पर पूछो कौन सा।

---

## 💻 Code Example — Basic
```python
# Basic: entropy over sampled answers (pure Python, runs offline)
import math                                                # log for entropy
from collections import Counter                            # count answer groups

def entropy(samples: list[str]) -> float:
    counts = Counter(samples)                              # group identical answers
    total = len(samples)                                   # number of samples
    return -sum((c / total) * math.log2(c / total) for c in counts.values())   # Shannon entropy (bits)

confident = ["8517.13"] * 5                                # all agree
vague = ["8544", "8544", "8536", "8517", "8544"]           # answers vary
print(entropy(confident))                                  # 0.0 -> certain (prints -0.0 or 0.0)
print(round(entropy(vague), 3))                            # >0 -> uncertain

def max_entropy(n_samples: int) -> float:
    return math.log2(n_samples)                            # upper bound if all answers differ

normalised = entropy(vague) / max_entropy(len(vague))      # scale to 0..1
print(round(normalised, 3))                                # normalised uncertainty
```

## 💻 Code Example — Advanced
```python
# Production: async UQ with diagnosis of why we are unsure
import asyncio                                             # parallel sampling
import math                                                # entropy math
from collections import Counter                            # grouping
from dataclasses import dataclass                          # result
from typing import Literal                                 # literals
from openai import AsyncOpenAI                             # client

client = AsyncOpenAI()                                     # shared client

@dataclass
class UQResult:
    answer: str                                            # majority answer
    entropy_norm: float                                    # 0..1
    kind: Literal["certain", "ambiguous", "unknown"]       # diagnosis
    action: Literal["answer", "clarify", "escalate"]       # what to do next

async def sample(question: str, t: float = 0.8) -> str:
    r = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=t, max_tokens=10,
        messages=[{"role": "system", "content": "Reply ONLY with an HS code."},
                  {"role": "user", "content": question}],
    )
    return (r.choices[0].message.content or "").strip()    # one sampled answer

async def quantify(question: str, retrieval_support: float, n: int = 6) -> UQResult:
    try:
        samples = await asyncio.gather(*(sample(question) for _ in range(n)))   # parallel
    except Exception:
        return UQResult("", 1.0, "unknown", "escalate")    # provider failure = escalate
    counts = Counter(samples)
    top, votes = counts.most_common(1)[0]                  # majority answer
    h = -sum((c / n) * math.log2(c / n) for c in counts.values())   # entropy in bits
    h_norm = h / math.log2(n)                              # normalise to 0..1
    if h_norm < 0.25:
        return UQResult(top, h_norm, "certain", "answer")
    # high entropy: decide ambiguity vs missing knowledge using retrieval support
    if retrieval_support >= 0.6:
        return UQResult(top, h_norm, "ambiguous", "clarify")   # data exists, question vague
    return UQResult(top, h_norm, "unknown", "escalate")    # no support: model does not know
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI                                # framework
from pydantic import BaseModel                             # schema

app = FastAPI()

class Q(BaseModel):
    question: str                                          # user text

@app.post("/classify")
async def classify(body: Q) -> dict:
    r = await quantify(body.question, retrieval_support=0.7)   # support from your retriever
    if r.action == "answer":
        return {"hs_code": r.answer, "uncertainty": round(r.entropy_norm, 2)}
    if r.action == "clarify":
        return {"clarify": "Please describe the product material and use.", "uncertainty": round(r.entropy_norm, 2)}
    return {"escalated": True, "message": "Sent to a customs expert."}   # human queue
```

---

## 🔗 LangChain / LangGraph Connection
In LangGraph, UQ becomes the routing function: a node samples N times (e.g. with `llm.abatch([...]*N)`), and conditional edges choose "answer", "ask_user" (using `interrupt` for human-in-the-loop) or "escalate".

```python
from langchain_openai import ChatOpenAI                    # chat model

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)     # sampling temperature > 0
msgs = await llm.abatch(["HS code for cable? code only"] * 6)   # 6 parallel samples
answers = [m.content for m in msgs]                        # collect answers
# then compute entropy(answers) and route:
def route(state: dict) -> str:
    return {"answer": "respond", "clarify": "ask_user", "escalate": "human"}[state["action"]]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Sampling with temperature 0
```python
# Wrong — all samples identical, entropy always 0 (fake certainty)
sample(question, t=0.0)

# Correct — temperature 0.7-1.0 for UQ sampling
sample(question, t=0.8)
```

❌ Mistake 2: Comparing free text by exact string
```python
# Wrong — "It is 8517" vs "8517." look different
# Correct — extract structured fields (code) or cluster by embedding / entailment
```

❌ Mistake 3: Treating all uncertainty the same
```python
# Wrong — always escalate when unsure
# Correct — ambiguous: ask the user; unknown: retrieve/escalate; certain: answer
```

---

## 🧠 Tricky Interview Question
**Q**: "All 10 samples agree on the same wrong HS code. Does UQ fail? What now?"

**Answer**: Yes, consistent errors (systematic bias) are invisible to sampling-based UQ because the model is **confidently wrong**: the samples share the same mistaken knowledge. Mitigations: independent checks (validation against the official tariff table, retrieval grounding, a different model as verifier), a diverse ensemble (different models/prompts), tests on a hard labelled set to find systematic failure areas, and human audits of "certain" answers. UQ lowers risk but never replaces ground-truth validation.

---

## ⚫ Interview Questions + Answers

Q1: What is aleatoric vs epistemic uncertainty?
A1: Aleatoric comes from inherent ambiguity or noise in the input; epistemic comes from the model's lack of knowledge and can be reduced with more data/retrieval.

Q2: How can you estimate uncertainty without model internals?
A2: Sample multiple answers and measure disagreement (entropy, semantic clustering).

Q3: What does a high entropy mean in practice?
A3: The answers vary a lot: ask for clarification, retrieve more, or escalate instead of answering.

Q4: Why is UQ expensive?
A4: It needs N model calls per query. Only use it when needed (grey-zone confidence) and keep outputs short.

Q5: (Hard) What is semantic entropy and why is it better than token entropy for free text?
A5: Semantic entropy groups sampled answers that mean the same thing (using bidirectional entailment or embeddings) before computing entropy, so different wordings of one fact are not counted as uncertainty. It is a recognised research approach for detecting hallucinations; token entropy confuses paraphrase variety with real uncertainty.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You can act differently on different uncertainty types (clarify, retrieve, escalate)
- Hallucination risk is high and answers are short/structured

❌ Avoid when:
- Latency budget is tiny and N-sampling is impossible
- Answers are long free-form text without a way to cluster them

---

## 📊 Visual Diagram
```
 question ─► sample N times (T=0.8)
                 │
         group by meaning ─► entropy H
                 │
   ┌─────────────┼───────────────────┐
  low H       high H +            high H +
 (certain)    retrieval ok         no support
    │         (ambiguous)           (unknown)
  answer         │                     │
              ask user             retrieve more
                                   / escalate
```

---

## 💰 Cost Impact
- N samples cost roughly N x output tokens, with the input tokens counted N times unless the provider caches the shared prefix (check provider support). Example: 6 samples x (200 input + 10 output) = 1,260 tokens, small for code-only answers.
- Optimise: run UQ only when the cheap confidence score is in the grey zone; use a small model; keep outputs structured; use provider batch/parallel calls; set tiny `max_tokens`.
- Cost of NOT doing it: wrong customs classifications can lead to fines far above token costs. Prices illustrative.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Uncertainty | How unsure the model is | model की अनिश्चितता |
| Aleatoric | From ambiguous/noisy input | input की अस्पष्टता से |
| Epistemic | From lack of knowledge | ज्ञान की कमी से |
| Entropy | Measure of disagreement | असहमति का माप |
| Semantic entropy | Entropy over meaning groups | अर्थ-समूहों पर entropy |
| Abstain | Refuse to answer | जवाब देने से बचना |

---

## ⚡ 3-Line Summary
English: UQ measures how unsure and why, using sampling entropy and retrieval support. Ambiguous input means ask the user; missing knowledge means retrieve or escalate. It cannot catch consistent errors, so keep ground-truth validation.
Hindi: UQ sampling entropy और retrieval support से बताता है कि model कितना और क्यों अनिश्चित है। अस्पष्ट input पर user से पूछो; ज्ञान की कमी पर retrieve या escalate करो। यह consistent errors नहीं पकड़ता, इसलिए ground-truth validation रखो।

---

## ➡️ Next Topic
**478. Fallback Responses** — what to say and do when confidence is low or something fails.
