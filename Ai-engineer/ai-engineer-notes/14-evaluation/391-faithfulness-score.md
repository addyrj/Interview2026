---

# 391. Faithfulness Score
# हिंदी में: Faithfulness Score

---

## 🔵 Simple Definition (English)
Faithfulness measures whether every claim in the AI's answer is supported by the retrieved context. Formula: supported claims divided by total claims. A score of 1.0 means no hallucination beyond the documents; 0.5 means half the claims are invented.

## 🔵 सरल परिभाषा (Hindi)
Faithfulness नापता है कि AI के answer का हर claim retrieved context से supported है या नहीं। Formula: supported claims / कुल claims। Score 1.0 का मतलब documents से बाहर कोई hallucination नहीं; 0.5 का मतलब आधे claims बनाए हुए हैं।

---

## 🔴 Problem it Solves
RAG is supposed to ground answers in documents, but LLMs mix in memorised knowledge or invent details. A fluent answer "duty is 5 percent plus a 2 percent cess" sounds right even if the cess is not in any document. Faithfulness catches this "plausible but unsupported" failure that humans skim past.

## 🔴 यह क्यों बना? (Hindi)
RAG का मकसद answers को documents पर टिकाना है, पर LLM अपनी याद की बातें मिला देता है या details गढ़ देता है। "duty 5 percent और 2 percent cess है" fluent और सही लगता है, भले ही cess किसी document में न हो। Faithfulness इसी "plausible पर unsupported" गलती को पकड़ता है जो इंसान जल्दी में miss कर देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Take the generated answer
Step 2 → LLM judge splits it into atomic claims (one fact per statement)
Step 3 → For each claim, judge asks: "Can this be inferred from the context?" (yes/no)
Step 4 → supported = number of "yes" verdicts
Step 5 → faithfulness = supported / total_claims   (range 0..1)
Step 6 → Inspect the unsupported claims -> these are your hallucinations
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Generated answer लो
Step 2 → LLM judge उसे atomic claims में तोड़ता है (हर statement में एक fact)
Step 3 → हर claim के लिए पूछता है: "क्या ये context से निकाला जा सकता है?" (हाँ/नहीं)
Step 4 → supported = "हाँ" verdicts की गिनती
Step 5 → faithfulness = supported / total_claims   (range 0..1)
Step 6 → Unsupported claims देखो -> यही तुम्हारे hallucinations हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**
Context: "HS 8507 lithium-ion batteries. Basic customs duty 0 percent. IGST 18 percent."
Answer: "Lithium-ion batteries fall under HS 8507, duty is 0 percent, and they need a BIS certificate."
Claims: (1) HS 8507 - supported. (2) duty 0 percent - supported. (3) needs BIS certificate - NOT in context.
Faithfulness = 2/3 = 0.67. The BIS claim might be true in real life, but it is not grounded, so a compliance system must flag it.

**Amazon AI**: Product Q&A says "battery lasts 10 hours" when the listing says nothing about battery life.

## 🟡 Real Example Hindi mein
**Tariff System**
Context: "HS 8507 lithium-ion batteries। Basic customs duty 0 percent। IGST 18 percent।"
Answer: "Lithium-ion batteries HS 8507 में आती हैं, duty 0 percent है, और BIS certificate चाहिए।"
Claims: (1) HS 8507 - supported। (2) duty 0 percent - supported। (3) BIS certificate चाहिए - context में NAHI।
Faithfulness = 2/3 = 0.67। असल दुनिया में BIS बात सही हो सकती है, पर grounded नहीं है, इसलिए compliance system को flag करना चाहिए।

**Amazon AI**: Product Q&A कहे "battery 10 घंटे चलती है" जबकि listing में battery life का ज़िक्र ही नहीं।

---

## 💻 Code Example — Basic
```python
# Basic: claim-level faithfulness with a stub judge (offline). The judge here is a
# simple rule: a claim is "supported" if most of its content words appear in context.
import re


def split_claims(answer: str) -> list[str]:
    """Naive claim splitter: sentences and comma-joined clauses."""
    parts = re.split(r"[.;]|, and |, ", answer)         # break on punctuation
    return [p.strip() for p in parts if p.strip()]      # drop empty parts


def is_supported(claim: str, context: str) -> bool:
    """Stub judge: 70% of content words of the claim must be in the context."""
    stop = {"the", "a", "is", "are", "and", "they", "it", "need", "under", "fall"}
    words = [w for w in re.findall(r"[a-z0-9]+", claim.lower()) if w not in stop]
    if not words:
        return True                                      # nothing to verify
    hit = sum(w in context.lower() for w in words)       # words found in context
    return hit / len(words) >= 0.7


def faithfulness(answer: str, context: str) -> tuple[float, list[str]]:
    claims = split_claims(answer)                        # step 2
    verdicts = [is_supported(c, context) for c in claims]   # step 3
    score = sum(verdicts) / len(claims) if claims else 0.0  # step 5
    unsupported = [c for c, v in zip(claims, verdicts) if not v]
    return score, unsupported


context = "HS 8507 lithium-ion batteries. Basic customs duty 0 percent. IGST 18 percent."
answer = "Lithium-ion batteries are HS 8507, duty is 0 percent, and they need a BIS certificate"
score, bad = faithfulness(answer, context)
print(round(score, 2), "unsupported:", bad)
```

## 💻 Code Example — Advanced
```python
# Advanced: real LLM-as-judge faithfulness with OpenAI structured output, async + retries.
# Requires: pip install "openai>=1" pydantic ; env OPENAI_API_KEY. The judge call is
# injectable so you can run this file offline with a fake judge (see main()).
import asyncio
import json
from typing import Awaitable, Callable
from pydantic import BaseModel, Field, ValidationError

JudgeFn = Callable[[str], Awaitable[str]]            # prompt -> raw JSON string


class Verdict(BaseModel):
    claim: str
    supported: bool
    reason: str = ""


class Judgement(BaseModel):
    verdicts: list[Verdict] = Field(default_factory=list)


PROMPT = """You are a strict fact checker.
Context:
{context}

Answer:
{answer}

1) Split the answer into atomic claims.
2) For each claim say whether it can be directly inferred from the context.
Return JSON: {{"verdicts":[{{"claim":"...","supported":true,"reason":"..."}}]}}"""


async def openai_judge(prompt: str) -> str:
    """Real judge. Imported lazily so the file runs without openai installed."""
    from openai import AsyncOpenAI                    # openai>=1
    client = AsyncOpenAI()
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,                                # deterministic judging
        response_format={"type": "json_object"},      # force valid JSON
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content or "{}"


async def faithfulness_llm(answer: str, context: str, judge: JudgeFn,
                           retries: int = 2) -> float:
    prompt = PROMPT.format(context=context, answer=answer)
    for attempt in range(retries + 1):
        try:
            raw = await judge(prompt)                 # call judge
            data = Judgement.model_validate(json.loads(raw))   # validate shape
            if not data.verdicts:
                return 0.0                            # no claims -> no evidence
            return sum(v.supported for v in data.verdicts) / len(data.verdicts)
        except (json.JSONDecodeError, ValidationError):
            if attempt == retries:
                raise                                 # give up after retries
            await asyncio.sleep(2 ** attempt)         # backoff then retry
    return 0.0


async def fake_judge(prompt: str) -> str:
    """Offline stand-in that returns fixed verdicts."""
    return json.dumps({"verdicts": [
        {"claim": "HS 8507", "supported": True},
        {"claim": "duty 0 percent", "supported": True},
        {"claim": "needs BIS", "supported": False, "reason": "not in context"}]})


async def main() -> None:
    print(await faithfulness_llm("answer text", "context text", fake_judge))   # 0.666...


asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
# FastAPI: runtime hallucination guard - score every answer before returning it
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
THRESHOLD = 0.8                                       # business rule


class Ask(BaseModel):
    question: str


async def rag_answer(q: str) -> tuple[str, str]:
    """Return (answer, context). Replace with your real RAG chain."""
    return "Duty is 0 percent and BIS is required.", "HS 8507 duty is 0 percent."


@app.post("/ask")
async def ask(body: Ask) -> dict:
    answer, context = await rag_answer(body.question)
    score = await faithfulness_llm(answer, context, fake_judge)   # use openai_judge in prod
    if score < THRESHOLD:                              # guardrail: do not show risky answer
        return {"answer": "I could not verify this from the documents.",
                "faithfulness": round(score, 2), "escalate_to_human": True}
    return {"answer": answer, "faithfulness": round(score, 2)}
```
Online judging adds one extra LLM call per request, so sample (e.g. 10 percent) unless the domain is high risk.

---

## 🔗 LangChain / LangGraph Connection
```python
# LangGraph: generate -> check faithfulness -> retry once if low (self-correction loop)
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class S(TypedDict):
    question: str
    context: str
    answer: str
    score: float
    tries: int


def generate(s: S) -> dict:
    # real node: prompt | llm | StrOutputParser(); stricter on retry
    strict = " Answer ONLY from context." if s["tries"] > 0 else ""
    return {"answer": "Duty 0 percent." + ("" if strict else " BIS needed."),
            "tries": s["tries"] + 1}


def check(s: S) -> dict:
    return {"score": faithfulness(s["answer"], s["context"])[0]}   # basic version


def route(s: S) -> str:
    return END if s["score"] >= 0.8 or s["tries"] >= 2 else "generate"


g = StateGraph(S)
g.add_node("generate", generate)
g.add_node("check", check)
g.add_edge(START, "generate")
g.add_edge("generate", "check")
g.add_conditional_edges("check", route)
app = g.compile()
print(app.invoke({"question": "duty?", "context": "HS 8507 duty is 0 percent.",
                  "answer": "", "score": 0.0, "tries": 0}))
```
Ragas equivalent: `from ragas.metrics import Faithfulness`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Treating faithfulness as truth
✅ Correct: It checks grounding in the given context only. Wrong context yields a faithful wrong answer.

```python
# Wrong
if faithfulness == 1.0: print("answer is correct")
# Right
if faithfulness == 1.0 and context_recall >= 0.8: print("grounded AND complete")
```

❌ Mistake 2: Judging with high temperature
✅ Correct: temperature=0 for repeatable verdicts.

```python
# Wrong
client.chat.completions.create(model=m, temperature=1.0, messages=msgs)
# Right
client.chat.completions.create(model=m, temperature=0, messages=msgs)
```

❌ Mistake 3: Giving the judge truncated context
✅ Correct: Judge must see the same context the generator saw, or supported claims look unsupported.

---

## 🧠 Tricky Interview Question

**Q**: "The answer says 'I don't know'. What is its faithfulness score, and is that good?"

**Answer**: An abstention contains no factual claims, so many implementations return 0 or NaN/undefined, or 1 (no unsupported claims), depending on the library. Do not read it as good or bad. Handle abstentions separately: count abstention rate, and check with context recall whether abstaining was justified (context really lacked the info) or a retrieval miss. Otherwise a model that always says "I don't know" gets perfect faithfulness while being useless.

---

## ⚫ Interview Questions + Answers

Q1: Write the faithfulness formula.
A1: Faithfulness = (number of answer claims supported by context) / (total number of claims in the answer).

Q2: Does faithfulness need a reference answer?
A2: No. It uses question-independent comparison of answer and context only, so it works on live production traffic.

Q3: How is faithfulness different from answer correctness?
A3: Faithfulness compares answer to retrieved context (grounding). Correctness compares answer to the gold reference (truth). A grounded answer can be wrong if retrieval was wrong.

Q4: What are weaknesses of LLM-judged faithfulness?
A4: Judge errors on numbers/units, claim-splitting differences, sensitivity to prompt wording, cost per sample, and bias toward fluent text. Mitigate with temperature 0, a stronger judge for audits, and human spot checks.

Q5 (Hard): Faithfulness dropped from 0.93 to 0.81 after switching to a cheaper generator model. What do you do?
A5: First segment: which question types dropped (numbers, multi-hop)? Read the unsupported claims; they show the failure pattern (e.g. adds outside facts). Try prompt fixes ("use only the context; say unknown otherwise"), lower temperature, and fewer but better chunks. Add a verification step (answer, then check, then regenerate). Then decide on trade-off: if the fix cannot recover quality, compute cost saved versus risk and keep the larger model for high-risk queries via routing.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need a hallucination metric for any grounded generation (RAG, summarisation)
- Runtime guardrail for high-risk domains (customs, legal, medical)

❌ Avoid when:
- No context exists (pure creative writing/chat)
- You need truth, not grounding (use correctness with references)

---

## 📊 Visual Diagram
```
 Answer: "HS 8507, duty 0 percent, needs BIS"
                │ split
                ▼
   claim1: HS 8507          ──► in context? ✅
   claim2: duty 0 percent   ──► in context? ✅
   claim3: needs BIS        ──► in context? ❌
                │
                ▼
   faithfulness = 2 / 3 = 0.67
```

---

## 💰 Cost Impact
- One judge call per answer: about 600-1500 input tokens (context + answer + instructions) and 100-300 output tokens. On gpt-4o-mini ($0.15 / $0.60 per 1M) that is roughly $0.0002-0.0004 per check.
- Checking every one of 100K daily answers costs about $20-40/day; sampling 10 percent costs $2-4/day.
- Optimise: judge only low-confidence or high-risk queries, shorten contexts to cited chunks, cache by hash, batch rows, and use a cheaper judge after validating agreement with a stronger one.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Claim | One atomic fact in the answer | Answer का एक छोटा fact |
| Supported | Can be inferred from context | Context से निकल सकता है |
| Hallucination | Unsupported invented content | गढ़ी हुई जानकारी |
| Grounding | Answer based on provided docs | Docs पर आधारित answer |
| Abstention | Model declines to answer | Model का जवाब न देना |
| Judge | LLM that grades outputs | Grading करने वाला LLM |

---

## ⚡ 3-Line Summary
English: Faithfulness = supported claims / total claims, judged against the retrieved context. It catches hallucination but does not prove truth. Use it as an offline metric and a sampled runtime guardrail.
Hindi: Faithfulness = supported claims / कुल claims, retrieved context के against judge किया हुआ। ये hallucination पकड़ता है पर सच साबित नहीं करता। इसे offline metric और sampled runtime guardrail की तरह use करो।

---

## ➡️ Next Topic
**392. Answer Relevancy Score** — a faithful answer can still ignore the question; relevancy checks that it actually answers what was asked.
