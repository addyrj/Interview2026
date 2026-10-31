---

# 467. Fact Checking in RAG
# हिंदी में: RAG में Fact Checking

---

## 🔵 Simple Definition (English)
Fact checking in RAG is a post-generation step that extracts the factual claims from the answer and verifies each against retrieved evidence and authoritative data (databases, APIs). Unsupported or contradicted claims are fixed, removed or escalated.

## 🔵 सरल परिभाषा (Hindi)
RAG में fact checking generation के बाद का step है जो answer से तथ्यात्मक claims निकालता है और हर एक को retrieved evidence और authoritative data (databases, APIs) से verify करता है। Unsupported या contradicted claims को ठीक किया जाता है, हटाया जाता है या escalate किया जाता है।

---

## 🔴 Problem it Solves
RAG reduces hallucination but does not remove it. Retrieval may miss the right chunk, the model may mix chunks, or the chunk itself may be wrong. A final fact-check layer is the safety net before the answer reaches the user.

## 🔴 यह क्यों बना? (Hindi)
RAG hallucination घटाता है पर खत्म नहीं करता। Retrieval सही chunk चूक सकता है, model chunks मिला सकता है, या chunk खुद गलत हो सकता है। अंतिम fact-check layer user तक पहुँचने से पहले safety net है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → RAG produces a draft answer and keeps the retrieved chunks
Step 2 → Extract atomic claims: ("HS=6109.10"), ("duty=10%"), ("effective=2026-04-01")
Step 3 → Typed claims → authoritative check (tariff DB, date API)
Step 4 → Free-text claims → evidence check (NLI / judge vs chunks)
Step 5 → Label each claim: SUPPORTED / CONTRADICTED / NOT_ENOUGH_INFO
Step 6 → Policy: contradicted → correct with DB value; NEI → remove or soften
Step 7 → Return final answer + fact-check report
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → RAG draft answer बनाता है और retrieved chunks रखता है
Step 2 → Atomic claims निकालो: ("HS=6109.10"), ("duty=10%"), ("effective=2026-04-01")
Step 3 → Typed claims → authoritative check (tariff DB, date API)
Step 4 → Free-text claims → evidence check (NLI / judge बनाम chunks)
Step 5 → हर claim को label दो: SUPPORTED / CONTRADICTED / NOT_ENOUGH_INFO
Step 6 → Policy: contradicted → DB value से सुधारो; NEI → हटाओ या नरम करो
Step 7 → Final answer + fact-check report लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: Draft: "Cotton t-shirts: HS 6109.10, duty 12%, effective 1 April 2026." Check: HS exists (SUPPORTED); duty in DB is 10% (CONTRADICTED, auto-corrected to 10%); effective date has no evidence (NOT_ENOUGH_INFO, removed). Final answer: "HS 6109.10, duty 10%." with a note that the date could not be verified.

**Zomato AI**: "Delivery in 20 minutes" is checked against the live ETA API.

## 🟡 Real Example Hindi mein
**Tariff System**: Draft: "Cotton t-shirts: HS 6109.10, duty 12%, effective 1 April 2026." Check: HS मौजूद है (SUPPORTED); DB में duty 10% है (CONTRADICTED, अपने आप 10% से सुधारी); effective date का कोई evidence नहीं (NOT_ENOUGH_INFO, हटाई)। Final answer: "HS 6109.10, duty 10%।" साथ में note कि date verify नहीं हो सकी।

**Zomato AI**: "20 मिनट में delivery" को live ETA API से check किया जाता है।

---

## 💻 Code Example — Basic
```python
# Basic: typed-claim fact check against a DB - pure Python, runs directly
import re  # regex

TARIFF_DB: dict[str, float] = {"6109.10": 10.0, "8471.30": 0.0}  # code -> duty %


def extract(answer: str) -> dict[str, float | str]:
    code = re.search(r"\b(\d{4}\.\d{2})\b", answer)  # HS code
    duty = re.search(r"duty\s*(?:of|is)?\s*(\d+(?:\.\d+)?)\s*%", answer, re.I)  # duty value
    out: dict[str, float | str] = {}
    if code:
        out["code"] = code.group(1)
    if duty:
        out["duty"] = float(duty.group(1))
    return out


def fact_check(answer: str) -> list[str]:
    claims = extract(answer)  # structured claims
    report: list[str] = []
    code = str(claims.get("code", ""))
    if code and code not in TARIFF_DB:
        report.append(f"CONTRADICTED: code {code} not in DB")
    elif code and "duty" in claims and claims["duty"] != TARIFF_DB[code]:
        report.append(f"CONTRADICTED: duty should be {TARIFF_DB[code]}%")
    else:
        report.append("SUPPORTED")
    return report


print(fact_check("HS 6109.10 with duty 12%"))  # contradicted
print(fact_check("HS 6109.10 with duty 10%"))  # supported
```

## 💻 Code Example — Advanced
```python
# Production: claim extraction + routing (DB vs evidence) + auto-correction, async
import asyncio  # concurrency
import json  # parse
import os  # env
from dataclasses import dataclass  # records
from typing import Literal  # labels

Label = Literal["SUPPORTED", "CONTRADICTED", "NEI"]
DB = {"6109.10": {"duty": 10.0}}  # authoritative data


@dataclass
class Claim:
    kind: str  # "duty" | "text"
    code: str  # HS code context
    value: str  # claimed value or sentence


@dataclass
class Checked:
    claim: Claim
    label: Label
    fix: str | None = None


async def extract_claims(answer: str) -> list[Claim]:
    if not os.getenv("OPENAI_API_KEY"):  # offline mock
        return [Claim("duty", "6109.10", "12"), Claim("text", "6109.10", "effective 1 April 2026")]
    from openai import AsyncOpenAI

    client = AsyncOpenAI()
    r = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=0, max_tokens=300,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content":
                   'Extract claims as JSON {"claims":[{"kind":"duty|text","code":"","value":""}]}\n' + answer}],
    )
    data = json.loads(r.choices[0].message.content or '{"claims": []}')
    return [Claim(**c) for c in data.get("claims", [])]


async def check(claim: Claim, evidence: str) -> Checked:
    if claim.kind == "duty":  # authoritative path
        real = DB.get(claim.code, {}).get("duty")
        if real is None:
            return Checked(claim, "NEI")
        ok = float(claim.value) == real
        return Checked(claim, "SUPPORTED" if ok else "CONTRADICTED", None if ok else f"{real}%")
    # text path: simple substring evidence check (replace with NLI/judge)
    return Checked(claim, "SUPPORTED" if claim.value.lower() in evidence.lower() else "NEI")


async def fact_check(answer: str, evidence: str) -> list[Checked]:
    try:
        claims = await extract_claims(answer)
    except Exception:  # extraction failed -> cannot certify the answer
        return [Checked(Claim("text", "", answer), "NEI")]
    return list(await asyncio.gather(*[check(c, evidence) for c in claims]))


if __name__ == "__main__":
    for item in asyncio.run(fact_check("duty 12%, effective 1 April 2026", "Duty on 6109.10 is 10 percent")):
        print(item.label, item.claim.value, item.fix)
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()


class Req(BaseModel):
    question: str  # user question


@app.post("/rag-answer")
async def rag_answer(body: Req) -> dict[str, object]:
    draft = "duty 12%, effective 1 April 2026"  # RAG draft here
    evidence = "Duty on 6109.10 is 10 percent"  # retrieved chunks
    checked = await fact_check(draft, evidence)  # advanced function
    problems = [c.label for c in checked if c.label != "SUPPORTED"]
    return {
        "report": [{"claim": c.claim.value, "label": c.label, "fix": c.fix} for c in checked],
        "needs_review": bool(problems),
    }
```

---

## 🔗 LangChain / LangGraph Connection
A natural LangGraph design: `retrieve -> generate -> extract_claims -> check_claims -> (correct | END)`. Each node is a function on state; use `Send` or simple async gather for per-claim checks.

```python
from typing import TypedDict  # state


class RagState(TypedDict):
    question: str
    docs: list[str]
    draft: str
    report: list[dict]
    final: str
# builder.add_conditional_edges("check_claims", lambda s: "correct" if s["report"] else "done")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Fact-checking with the same prompt and same model as generation
✅ Correct: Use evidence and a separate judge prompt (ideally a different model or DB).

```python
# Wrong
llm.invoke(f"Is this correct? {draft}")
# Right
check(claim, evidence_or_db)
```

❌ Mistake 2: Dropping NEI claims silently
✅ Correct: Tell the user something could not be verified.

```python
# Wrong
final = " ".join(supported)
# Right
final = " ".join(supported) + "\nNote: some details could not be verified."
```

---

## 🧠 Tricky Interview Question
**Q**: "All claims are SUPPORTED, yet the answer misleads users. How?"

**Answer**: Claim-level checks ignore omission and framing. Example: the answer states the 10% basic duty (supported) but omits an additional anti-dumping duty found in another chunk. Add completeness checks (required fields per question type), retrieve with multiple queries, and test with expert-written golden sets.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is fact checking in RAG?
A1: Verifying the answer's claims against evidence after generation.

Q2: [Easy] Three labels used?
A2: Supported, contradicted, not enough info.

Q3: [Medium] Why route typed claims to a DB?
A3: Numbers, dates and codes should be checked against authoritative data, not judged by an LLM. It is cheaper and exact.

Q4: [Medium] What is the difference between fact checking and grounding?
A4: Grounding shapes generation with sources; fact checking audits the generated output afterward. Use both.

Q5: [Hard] How do you evaluate your fact checker?
A5: Build a labelled set of answers with injected errors, measure precision and recall per label, track false blocks, review disagreements with domain experts, and rerun on every model or prompt change.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Structured facts (numbers, dates, codes) appear in answers
- Compliance or money is involved

❌ Avoid when:
- Opinions or brainstorming
- Very low-stakes chat where latency matters more

---

## 📊 Visual Diagram
```
Draft ─► Extract claims ─┬─ typed ──► DB/API ────┐
                         └─ text ───► NLI/judge ─┤
                                                 ▼
                              SUPPORTED / CONTRADICTED / NEI
                                  │         │          │
                                keep     auto-fix   remove/soften
                                       ▼
                               Final answer + report
```

---

## 💰 Cost Impact
Extraction call: ~400 tokens. DB checks: free. Judge on text claims: ~250 tokens each. Typical total ≈ 1,000 tokens ≈ $0.00015 per answer on gpt-4o-mini, about 70% on top of a basic RAG call. Optimise: extract claims with regex when the format is predictable, only judge text claims, skip checks for cache hits that were already verified, and apply full checking only to high-risk intents.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Claim extraction | Split answer into facts | answer से तथ्य निकालना |
| NEI | Not enough info | पर्याप्त जानकारी नहीं |
| Authoritative source | Official data | आधिकारिक डेटा |
| Auto-correct | Replace with true value | सही मान से बदलना |
| Golden set | Expert-labelled tests | विशेषज्ञ-लेबल वाले tests |
| Completeness | Nothing important missing | कुछ ज़रूरी छूटा नहीं |

---

## ⚡ 3-Line Summary
English: Fact checking extracts claims from a RAG answer and verifies them against a database or evidence. Route typed facts to authoritative data and text facts to a judge. Fix, remove or escalate failures.
Hindi: Fact checking RAG answer से claims निकालकर database या evidence से verify करती है। Typed facts authoritative data से और text facts judge से check करो। Failures को सुधारो, हटाओ या escalate करो।

---

## ➡️ Next Topic
**468. Guardrails AI Library** - a ready-made Python library to define validators for inputs and outputs.
