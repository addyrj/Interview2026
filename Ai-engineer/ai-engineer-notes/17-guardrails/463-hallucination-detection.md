---

# 463. Hallucination Detection
# हिंदी में: Hallucination की पहचान (Detection)

---

## 🔵 Simple Definition (English)
Hallucination detection is the automatic check that decides whether an LLM answer is supported by trusted evidence. Common methods: compare the answer with retrieved context (faithfulness), ask a judge LLM, check consistency across several samples, and verify facts like codes or citations against a database.

## 🔵 सरल परिभाषा (Hindi)
Hallucination detection वह automatic जाँच है जो तय करती है कि LLM का जवाब भरोसेमंद evidence से supported है या नहीं। आम तरीके: जवाब की retrieved context से तुलना (faithfulness), judge LLM से पूछना, कई samples में consistency देखना, और codes या citations को database से verify करना।

---

## 🔴 Problem it Solves
Humans cannot read every answer. Without detection, wrong answers reach users silently and you only learn from complaints. Detection gives a score you can use to block, warn, retry or send to a human.

## 🔴 यह क्यों बना? (Hindi)
इंसान हर जवाब नहीं पढ़ सकते। Detection के बिना गलत जवाब चुपचाप users तक पहुँचते हैं और आपको शिकायत से पता चलता है। Detection एक score देता है जिससे block, warn, retry या human को भेजना तय हो सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Collect answer + evidence (retrieved chunks, DB rows)
Step 2 → Rule check: does every HS code in the answer exist in the tariff DB?
Step 3 → Split answer into atomic claims
Step 4 → For each claim: is it entailed by the evidence? (NLI model or judge LLM)
Step 5 → Optional: SelfCheck - sample N answers; disagreement = likely hallucination
Step 6 → Combine into a score (supported_claims / total_claims)
Step 7 → score < threshold → block / warn / retry / human review
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Answer + evidence (retrieved chunks, DB rows) इकट्ठा करो
Step 2 → Rule check: क्या answer का हर HS code tariff DB में मौजूद है?
Step 3 → Answer को छोटे claims में बाँटो
Step 4 → हर claim के लिए: क्या evidence उसे support करता है? (NLI model या judge LLM)
Step 5 → Optional: SelfCheck - N answers sample करो; असहमति = संभावित hallucination
Step 6 → Score बनाओ (supported_claims / total_claims)
Step 7 → score < threshold → block / warn / retry / human review
```

---

## 🟡 Real World Example
**Tariff Classification System**: The answer says "HS 6109.10, duty 10%, see Note 3 of Chapter 61". Detection: (1) `6109.10` exists in the DB - pass; (2) duty 10% matches the DB row - pass; (3) "Note 3 of Chapter 61" is not in the retrieved text - flagged as unsupported. Score 2/3, so the answer is returned with a warning and the unsupported sentence removed.

**Zomato AI**: Bot says "this restaurant is open till 2 AM". Check against the opening-hours API; mismatch is caught.

## 🟡 Real Example Hindi mein
**Tariff System**: Answer कहता है "HS 6109.10, duty 10%, Chapter 61 का Note 3 देखें"। Detection: (1) `6109.10` DB में है - pass; (2) duty 10% DB row से मेल खाती है - pass; (3) "Chapter 61 का Note 3" retrieved text में नहीं - unsupported flag। Score 2/3, इसलिए जवाब warning के साथ और unsupported वाक्य हटाकर लौटाया जाता है।

**Zomato AI**: Bot कहता है "restaurant रात 2 बजे तक खुला है"। Opening-hours API से मिलान करने पर mismatch पकड़ में आता है।

---

## 💻 Code Example — Basic
```python
# Basic: rule + overlap based detection - pure Python, runs directly
import re  # regex for HS codes

TARIFF_DB: dict[str, float] = {"6109.10": 10.0, "8471.30": 0.0}  # code -> duty percent


def extract_codes(text: str) -> list[str]:
    return re.findall(r"\b\d{4}\.\d{2}\b", text)  # find codes like 6109.10


def detect(answer: str, context: str) -> dict[str, object]:
    codes = extract_codes(answer)  # codes mentioned
    unknown = [c for c in codes if c not in TARIFF_DB]  # not in database
    words = set(re.findall(r"[a-z0-9.%]+", answer.lower()))  # answer words
    ctx_words = set(re.findall(r"[a-z0-9.%]+", context.lower()))  # context words
    overlap = len(words & ctx_words) / len(words) if words else 0.0  # support ratio
    return {"unknown_codes": unknown, "overlap": round(overlap, 2),
            "suspicious": bool(unknown) or overlap < 0.5}


ctx = "cotton t-shirts hs 6109.10 duty 10%"
print(detect("t-shirts are 6109.10 duty 10%", ctx))  # looks fine
print(detect("t-shirts are 9999.99 duty 3%", ctx))  # unknown code, suspicious
```

## 💻 Code Example — Advanced
```python
# Production: claim-level faithfulness with async judge + SelfCheck consistency
import asyncio  # concurrency
import json  # parse JSON
import os  # env
import re  # split sentences
from collections import Counter  # voting
from dataclasses import dataclass  # result


@dataclass
class DetectionResult:
    score: float  # 0..1 supported ratio
    unsupported: list[str]  # claims without support
    action: str  # allow / warn / block


def split_claims(answer: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", answer) if s.strip()]  # sentences


async def claim_supported(claim: str, context: str) -> bool:
    if not os.getenv("OPENAI_API_KEY"):  # offline fallback: word overlap
        cw = set(claim.lower().split())
        return len(cw & set(context.lower().split())) / max(len(cw), 1) > 0.5
    from openai import AsyncOpenAI  # openai>=1

    client = AsyncOpenAI()
    try:
        r = await client.chat.completions.create(
            model="gpt-4o-mini", temperature=0, max_tokens=10,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content":
                       f'Is the CLAIM fully supported by CONTEXT? JSON {{"supported": true|false}}\n'
                       f"CONTEXT: {context}\nCLAIM: {claim}"}],
        )
        return bool(json.loads(r.choices[0].message.content or "{}").get("supported"))
    except Exception:
        return False  # fail closed: treat as unsupported


async def detect(answer: str, context: str, threshold: float = 0.8) -> DetectionResult:
    claims = split_claims(answer)  # step 3
    flags = await asyncio.gather(*[claim_supported(c, context) for c in claims])  # parallel
    bad = [c for c, ok in zip(claims, flags) if not ok]  # unsupported claims
    score = (len(claims) - len(bad)) / len(claims) if claims else 1.0
    action = "allow" if score >= threshold else ("warn" if score >= 0.5 else "block")
    return DetectionResult(score, bad, action)


def self_consistency(samples: list[str]) -> float:
    """SelfCheck idea: if sampled answers disagree, confidence is low."""
    top = Counter(samples).most_common(1)[0][1]  # count of most common answer
    return top / len(samples)  # 1.0 = all agree


if __name__ == "__main__":
    ctx = "Cotton t-shirts fall under HS 6109.10. Duty is 10 percent."
    print(asyncio.run(detect("T-shirts fall under HS 6109.10. Duty is 10 percent. See Note 3.", ctx)))
    print(self_consistency(["6109.10", "6109.10", "6110.20"]))  # 0.67
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()


class Check(BaseModel):
    answer: str  # model answer
    context: str  # evidence


@app.post("/detect-hallucination")
async def detect_route(body: Check) -> dict[str, object]:
    result = await detect(body.answer, body.context)  # from advanced example
    return {"score": result.score, "unsupported": result.unsupported, "action": result.action}
```

---

## 🔗 LangChain / LangGraph Connection
Use a structured-output judge in an LCEL chain, or add a `verify` node after `generate` in LangGraph. If `action == "block"`, loop back to `retrieve` once, then fall back to "I don't know".

```python
from pydantic import BaseModel  # schema


class Judge(BaseModel):
    supported: bool  # is claim supported?


# judge_chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Judge)
# graph: generate -> verify -> (ok? END : retrieve)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Asking the same model "are you sure?"
✅ Correct: Compare with external evidence, not self-belief.

```python
# Wrong
llm.invoke("Are you sure about your answer?")
# Right
verify_against_db(answer.codes)
```

❌ Mistake 2: Judge LLM with temperature > 0 and no JSON format
✅ Correct: temperature 0, structured output.

```python
# Wrong
client.chat.completions.create(model="gpt-4o-mini", temperature=1, messages=m)
# Right
client.chat.completions.create(model="gpt-4o-mini", temperature=0,
                               response_format={"type": "json_object"}, messages=m)
```

---

## 🧠 Tricky Interview Question
**Q**: "Your judge LLM says the answer is faithful, but a human says it's wrong. Why?"

**Answer**: The judge only checks support against the given context. If the retrieved context itself is wrong or outdated, the answer is faithful yet incorrect. Also judges are biased toward fluent text. Measure judge accuracy against human labels, and add external checks (DB lookups) and context-freshness checks.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is a faithfulness score?
A1: Fraction of answer claims supported by the retrieved context.

Q2: [Easy] Name two detection methods.
A2: Rule/database checks and LLM-as-judge. Also NLI models and SelfCheck sampling.

Q3: [Medium] What is SelfCheckGPT?
A3: Sample several answers; true facts repeat across samples, hallucinations vary. Low agreement signals risk. Costs N calls.

Q4: [Medium] Why split into claims?
A4: A long answer may be mostly right with one false sentence. Claim-level checks find and remove just that part.

Q5: [Hard] How do you choose the threshold?
A5: Build a labelled set, plot precision/recall vs threshold, pick by cost of a missed hallucination versus cost of a false block. Use different thresholds per risk level (duty rate: strict; general info: loose).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Answers affect money, legal or safety outcomes
- You use RAG and have evidence to compare
- You want production metrics

❌ Avoid when:
- Creative writing (no ground truth)
- Latency budget is tiny and risk is low

---

## 📊 Visual Diagram
```
Answer ─► split claims ─► [DB / rule check] ─┐
                      └─► [Judge vs context] ─┼─► score ─► ≥0.8 allow
Evidence ──────────────────────────────────────┘         0.5-0.8 warn
Samples x N ─► [Consistency] ────────────────────────────  <0.5 block/human
```

---

## 💰 Cost Impact
Rule/DB checks are free. A claim judge costs roughly 150-300 tokens per claim; five claims on gpt-4o-mini is about 1,000 tokens, roughly $0.00015 per answer. SelfCheck with 5 samples multiplies generation cost by 5, so use it only for high-risk queries. Optimise: run rules first, judge only uncertain answers, batch claims in one call, cache verdicts, and sample traffic.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Claim | One checkable statement | जाँचने योग्य एक कथन |
| Entailment (NLI) | Evidence implies claim | evidence से claim निकलना |
| LLM-as-judge | LLM scores another output | LLM द्वारा मूल्यांकन |
| SelfCheck | Consistency across samples | samples में एकरूपता |
| Threshold | Score cut-off | सीमा-मान |
| Fail closed | Block when unsure | शक पर रोक |

---

## ⚡ 3-Line Summary
English: Detection compares answers with evidence using rules, claim-level judges and consistency checks. Always verify against external truth like a database, not the model's own opinion. Pick thresholds from labelled data.
Hindi: Detection में जवाब की evidence से तुलना rules, claim-level judges और consistency checks से होती है। हमेशा बाहरी सच (जैसे database) से verify करो, model की अपनी राय से नहीं। Thresholds labelled data से चुनो।

---

## ➡️ Next Topic
**464. Hallucination Prevention** - detection catches errors after the fact; prevention reduces them before they happen.
