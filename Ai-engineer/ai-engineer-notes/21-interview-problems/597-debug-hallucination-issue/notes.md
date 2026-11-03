---

# 597. Debug Hallucination Issue
# हिंदी में: Hallucination की Problem Debug करना

---

## 🔵 Simple Definition (English)
Hallucination is when an LLM states something fluent but false or not supported by the provided sources. Debugging it means finding which stage caused it: retrieval missed the fact, the prompt allowed guessing, or the model invented details.

## 🔵 सरल परिभाषा (Hindi)
Hallucination तब होता है जब LLM fluent लेकिन गलत या sources से unsupported बात कहता है। Debug करने का मतलब है कारण ढूँढना: retrieval ने fact miss किया, prompt ने guess करने दिया, या model ने खुद बना दिया।

---

## 🔴 Problem it Solves
In a tariff system a wrong duty rate or HS code has legal and financial impact. Users cannot tell a confident wrong answer from a right one. Without a method, teams just "tweak the prompt" blindly.

## 🔴 यह क्यों बना? (Hindi)
Tariff system में गलत duty rate या HS code का कानूनी और आर्थिक असर होता है। User confident गलत answer और सही answer में फर्क नहीं कर पाता। Method के बिना team अंधाधुंध prompt बदलती रहती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Reproduce: save question, retrieved chunks, final prompt, answer, params
Step 2 → Is the correct fact in the retrieved chunks?
         no  -> retrieval problem (chunking, embeddings, top-k, filters)
Step 3 → Fact present but answer differs -> generation problem
         (weak instructions, too much context, high temperature)
Step 4 → Split answer into claims; check each against context (grounding check)
Step 5 → Fix the cause: better retrieval / "answer only from context" + "say I don't know" / lower temperature / citations
Step 6 → Add the failing case to the regression test set
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Reproduce: question, retrieved chunks, final prompt, answer, params save करो
Step 2 → सही fact retrieved chunks में है? नहीं -> retrieval problem
Step 3 → Fact है पर answer अलग -> generation problem
Step 4 → Answer को claims में तोड़कर context से check करो
Step 5 → कारण के हिसाब से fix: retrieval सुधारो / "सिर्फ context से जवाब दो" / temperature कम / citations
Step 6 → Failing case को regression test set में जोड़ो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The bot says "Smartphones: HS 8517.13, duty 25% plus luxury surcharge". The knowledge base says duty 0%. The grounding check flags the second sentence (support 0.25) while the first is supported (0.80). Root cause: the prompt said "be helpful" and had no "say I don't know" rule, so the model filled in from memory.

**Amazon-style**: a shopping assistant claims a product has a feature that is not in the listing; grounding check against the listing catches it.

## 🟡 Real Example Hindi mein
**Tariff System**: Bot कहता है "Smartphones: HS 8517.13, duty 25% plus luxury surcharge"। Knowledge base में duty 0% है। Grounding check दूसरी sentence flag करता है (support 0.25), पहली supported है (0.80)। कारण: prompt में "helpful बनो" था, "पता नहीं कहो" rule नहीं था।

**Amazon**: Shopping assistant ऐसा feature बता देता है जो listing में नहीं है; grounding check पकड़ लेता है।

---

## 💻 Code Example — Basic
```python
# Tiny grounding check: how many answer words appear in the context?
context: str = "hs code 8517.13 covers smartphones duty 0 percent"   # retrieved text
answer: str = "smartphones are hs 8517.13 with 25 percent surcharge"  # model output

ctx_words: set[str] = set(context.split())          # words available as evidence
ans_words: list[str] = answer.split()               # words the model claimed
support: float = sum(w in ctx_words for w in ans_words) / len(ans_words)  # share found
print(f"support={support:.2f}")                     # low value -> suspicious answer
```

## 💻 Code Example — Advanced
Full file: `main.py` (sentence-level grounding check plus a diagnosis hint). Observed output:
```
0.80 OK  Smartphones fall under HS code 8517.13.
0.25 BAD The import duty is 25 percent plus a special luxury surcharge.
1/2 claims ungrounded. Check: retrieval recall, prompt allows outside knowledge, temperature, missing 'say I don't know' rule.
```
```python
# Excerpt from main.py
def check_answer(answer: str, context: list[str], threshold: float = 0.6) -> list[ClaimCheck]:
    if not context:                                       # no evidence at all
        raise ValueError("empty context: any answer is ungrounded")
    ctx_words = set().union(*(words(c) for c in context))  # evidence vocabulary
    results = []
    for s in sentences(answer):                           # check claim by claim
        w = words(s)
        support = len(w & ctx_words) / len(w) if w else 1.0   # overlap ratio
        results.append(ClaimCheck(s, round(support, 2), support >= threshold))
    return results
```
This lexical check is a cheap first pass; it misses paraphrases and wrong numbers inside otherwise matching text. Production systems add an NLI model or an LLM judge. Async: wrap an LLM-judge call in `await` and run claims with `asyncio.gather`.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel
from main import check_answer                           # our module

app = FastAPI()


class Verify(BaseModel):
    answer: str
    context: list[str]


@app.post("/verify")
async def verify(req: Verify) -> dict:
    checks = check_answer(req.answer, req.context) if req.context else []
    bad = [c for c in checks if not c.grounded]         # ungrounded claims
    return {"grounded": bool(checks) and not bad,       # empty context -> not grounded
            "ungrounded_claims": [c.sentence for c in bad]}
```
Use it as a guardrail: if not grounded, return "I could not verify this" or regenerate.

---

## 🔗 LangChain / LangGraph Connection
A LangGraph self-check loop: generate -> grade groundedness -> if bad, retrieve again or answer "not found".

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END


class S(TypedDict):
    question: str
    docs: list[str]
    answer: str
    grounded: bool


def grade(state: S) -> S:
    from main import check_answer                       # reuse our checker
    checks = check_answer(state["answer"], state["docs"])
    return {**state, "grounded": all(c.grounded for c in checks)}


g = StateGraph(S)                                       # graph over shared state
g.add_node("grade", grade)                              # (generate/retrieve nodes omitted)
g.set_entry_point("grade")
g.add_edge("grade", END)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Fixing by adding "do not hallucinate" to the prompt only.
✅ Correct: find the stage; ground answers in retrieved context with citations and an allowed "I don't know".

```python
# Wrong
prompt = "Answer the question. Do not hallucinate."
# Right
prompt = "Answer ONLY from the context. If the answer is not in it, say 'Not found'. Cite chunk ids."
```

❌ Mistake 2: Not logging retrieved chunks, so failures cannot be reproduced.
✅ Correct: log question, chunk ids, prompt version, answer.

❌ Mistake 3: Using temperature above 0 for factual lookups without need.

---

## 🧠 Tricky Interview Question
**Q**: "The correct document is in your vector DB, yet the answer is wrong. Where do you look?"

**Answer**: Check whether it was retrieved at all (rank, top-k, filters, chunk boundaries splitting the table, embedding mismatch on codes like 8517.13). If retrieved, check the prompt: too many distractor chunks, instructions allowing outside knowledge, "lost in the middle" placement. Then sampling settings. Measure retrieval recall@k separately from answer faithfulness.

---

## ⚫ Interview Questions + Answers

Q1: What is hallucination?
A1: A fluent output not supported by facts or the provided sources.

Q2: Name two ways to reduce it in RAG.
A2: Ground answers in retrieved context with citations; allow "I don't know"; lower temperature.

Q3: How do you tell retrieval failure from generation failure?
A3: Inspect retrieved chunks: if the fact is absent it is retrieval; if present but ignored it is generation.

Q4: How do you measure hallucination?
A4: Faithfulness/groundedness metrics on a labelled set (LLM judge or NLI), citation accuracy, and human audits of samples.

Q5 (Hard): Design a production guardrail for high-stakes answers.
A5: Require structured output with citations; verify each cited quote exists in the retrieved chunk; run a groundedness judge; on failure retry with more context or return "not found" and escalate to a human; log everything and monitor the failure rate.

---

## 🔷 When to Use + When Not to Use
✅ Use grounding checks when:
- Legal, finance, medical, tariff answers

❌ Avoid heavy checks when:
- Creative writing or brainstorming where invention is the goal

---

## 📊 Visual Diagram
```
 question ─► retrieve ─► chunks ─► prompt ─► LLM ─► answer
               │           │         │        │
        recall too low?  fact in?  rules?  temperature?
               └───────────┴─────────┴────────┘
                           grounding check per claim
                           ┌──────────┴──────────┐
                        grounded            ungrounded
                        return              retry / "not found"
```

---

## 💰 Cost Impact
Checks add cost: a lexical check is free; an LLM judge adds roughly one extra call per answer (input = answer + context). Reduce by checking only high-risk categories, using a small judge model, and sampling in low-risk flows. Fewer wrong answers also cut support and re-ask costs. Fixing retrieval (smaller top-k, rerank) usually lowers tokens too.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hallucination | Confident unsupported output | बिना आधार का आत्मविश्वासी जवाब |
| Grounding | Tying answer to sources | जवाब को sources से जोड़ना |
| Faithfulness | Answer matches context | Answer का context से मेल |
| Recall@k | Fact found in top k | Top k में fact मिलना |
| Guardrail | Safety check | सुरक्षा जाँच |

---

## ⚡ 3-Line Summary
English: Find the stage first: retrieval, prompt, or generation. Ground answers in context, allow "I don't know", and check claims. Log everything and add failures to tests.
Hindi: पहले stage ढूँढो: retrieval, prompt या generation। Answers को context से जोड़ो, "पता नहीं" की अनुमति दो और claims check करो। सब log करो और failures को tests में जोड़ो।

---

## ➡️ Next Topic
**598. Debug Slow RAG Pipeline** — next, find where the latency goes.
