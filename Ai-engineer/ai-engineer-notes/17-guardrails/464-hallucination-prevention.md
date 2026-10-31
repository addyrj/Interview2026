---

# 464. Hallucination Prevention
# हिंदी में: Hallucination की रोकथाम

---

## 🔵 Simple Definition (English)
Hallucination prevention means designing the system so the model has less chance to invent facts: give it the right context (RAG), use tools for exact data, write strict prompts that allow "I don't know", lower randomness, constrain the output format, and verify before showing.

## 🔵 सरल परिभाषा (Hindi)
Hallucination prevention का मतलब system ऐसे design करना कि model के पास तथ्य गढ़ने का मौका कम हो: सही context दो (RAG), exact data के लिए tools use करो, ऐसे strict prompts लिखो जिनमें "पता नहीं" कहना allowed हो, randomness कम रखो, output format सीमित करो, और दिखाने से पहले verify करो।

---

## 🔴 Problem it Solves
Detection alone is reactive. If 20% of answers are wrong you waste money on retries and humans. Prevention lowers the base error rate, so detection has less to catch.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ detection बाद में काम करता है। अगर 20% जवाब गलत हैं तो retries और humans पर पैसा बर्बाद होता है। Prevention base error rate घटाता है, इसलिए detection को कम पकड़ना पड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Retrieve relevant, fresh, trusted context (RAG)
Step 2 → Use tools for exact data (DB lookup for HS code and duty rate)
Step 3 → Prompt: "Use only the context. If not found, say 'insufficient information'."
Step 4 → Temperature 0, structured output (enum codes, JSON schema)
Step 5 → Require evidence: the model must quote the supporting sentence
Step 6 → Validate: code exists? quote really in context?
Step 7 → On failure: retry once with feedback, else abstain / human
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → प्रासंगिक, ताज़ा, भरोसेमंद context लाओ (RAG)
Step 2 → Exact data के लिए tools (HS code और duty rate के लिए DB lookup)
Step 3 → Prompt: "सिर्फ context use करो। न मिले तो 'insufficient information' कहो।"
Step 4 → Temperature 0, structured output (enum codes, JSON schema)
Step 5 → Evidence ज़रूरी: model supporting वाक्य quote करे
Step 6 → Validate: code मौजूद है? quote सच में context में है?
Step 7 → Fail होने पर feedback के साथ एक retry, नहीं तो abstain / human
```

---

## 🟡 Real World Example
**Tariff Classification System**: Instead of letting the model invent the duty rate, the pipeline retrieves the top 3 tariff chunks, asks the model to output `{hs_code, quote}` with `hs_code` restricted to codes present in the retrieved chunks, then looks up the duty rate from the database (the model never writes the number). Hallucinated duty rates drop to zero because the number does not come from the model.

**Amazon AI**: Product specs come from the catalogue API; the LLM only writes the friendly sentence around them.

## 🟡 Real Example Hindi mein
**Tariff System**: Model को duty rate गढ़ने देने की जगह pipeline top 3 tariff chunks लाता है, model से `{hs_code, quote}` output माँगता है जहाँ `hs_code` सिर्फ retrieved chunks वाले codes तक सीमित है, और duty rate database से lookup होती है (model वह number कभी नहीं लिखता)। Hallucinated duty rates शून्य हो जाते हैं क्योंकि number model से आता ही नहीं।

**Amazon AI**: Product specs catalogue API से आते हैं; LLM सिर्फ उनके आसपास friendly वाक्य लिखता है।

---

## 💻 Code Example — Basic
```python
# Basic: abstain-by-default answerer using a lookup table - pure Python
TARIFF_DB: dict[str, tuple[str, float]] = {
    "cotton t-shirt": ("6109.10", 10.0),  # product -> (code, duty percent)
    "laptop": ("8471.30", 0.0),
}


def answer(product: str) -> str:
    key = product.lower().strip()  # normalize
    row = TARIFF_DB.get(key)  # exact lookup
    if row is None:  # unknown product: do NOT guess
        return "insufficient information - please send a description to a broker"
    code, duty = row  # unpack
    return f"HS {code}, duty {duty}%"  # numbers come from DB, not from a model


print(answer("Laptop"))  # HS 8471.30, duty 0.0%
print(answer("smart ring"))  # abstains instead of inventing
```

## 💻 Code Example — Advanced
```python
# Production: constrained output + quote verification + one retry, async, typed
import asyncio  # async runtime
import json  # parse
import os  # env
from typing import Optional  # type

from pydantic import BaseModel, ValidationError  # pydantic v2

ALLOWED = {"6109.10", "8471.30"}  # codes present in retrieved chunks


class Out(BaseModel):
    hs_code: Optional[str]  # None means "don't know"
    quote: Optional[str]  # supporting sentence


async def call_llm(context: str, question: str, feedback: str = "") -> str:
    if not os.getenv("OPENAI_API_KEY"):  # offline mock
        return json.dumps({"hs_code": "6109.10", "quote": "Cotton t-shirts fall under 6109.10"})
    from openai import AsyncOpenAI

    client = AsyncOpenAI()
    r = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=0, max_tokens=120,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content":
             "Use ONLY the context. Reply JSON {hs_code, quote}. If unsure use null for both."},
            {"role": "user", "content": f"Context:\n{context}\nQuestion: {question}\n{feedback}"},
        ],
    )
    return r.choices[0].message.content or "{}"


def verify(out: Out, context: str) -> str | None:
    """Return an error message or None if fine."""
    if out.hs_code is None:
        return None  # abstention is allowed
    if out.hs_code not in ALLOWED:
        return f"code {out.hs_code} is not in allowed list"
    if not out.quote or out.quote not in context:
        return "quote not found in context"
    return None


async def safe_answer(context: str, question: str) -> Out:
    feedback = ""
    for _ in range(2):  # one retry only
        try:
            out = Out.model_validate_json(await call_llm(context, question, feedback))
        except (ValidationError, Exception) as exc:  # bad JSON or API error
            feedback = f"Previous output invalid: {exc}"
            continue
        err = verify(out, context)
        if err is None:
            return out  # verified
        feedback = f"Fix this problem: {err}"  # tell the model what was wrong
    return Out(hs_code=None, quote=None)  # abstain


if __name__ == "__main__":
    ctx = "Cotton t-shirts fall under 6109.10 and attract 10 percent duty."
    print(asyncio.run(safe_answer(ctx, "HS code for cotton t-shirts?")))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # framework

app = FastAPI()


@app.get("/classify")
async def classify(q: str) -> dict[str, object]:
    ctx = "Cotton t-shirts fall under 6109.10 and attract 10 percent duty."  # from retriever
    out = await safe_answer(ctx, q)  # from advanced example
    if out.hs_code is None:
        return {"status": "needs_human_review", "hs_code": None}  # abstain path
    duty = 10.0  # duty is looked up from DB by code, never by the model
    return {"status": "ok", "hs_code": out.hs_code, "duty_percent": duty, "evidence": out.quote}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain: `with_structured_output(PydanticModel)` constrains output. LangGraph: build `retrieve -> generate -> verify` with a conditional edge back to `generate` (max 1 retry) or to a `human_review` node.

```python
from langchain_core.prompts import ChatPromptTemplate  # prompt

prompt = ChatPromptTemplate.from_messages([
    ("system", "Use only the context. If the answer is not there, reply exactly: INSUFFICIENT."),
    ("human", "{context}\n\nQ: {question}"),
])
# chain = prompt | llm.with_structured_output(Out)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Letting the model produce numbers that exist in a database
✅ Correct: Look numbers up with code.

```python
# Wrong
duty = llm.invoke("What is the duty for 6109.10?")
# Right
duty = TARIFF_DB["6109.10"]
```

❌ Mistake 2: Stuffing 30 chunks into the prompt
✅ Correct: Rerank and send the best 3-5.

```python
# Wrong
context = "\n".join(all_30_chunks)
# Right
context = "\n".join(reranker.top_k(chunks, k=4))
```

---

## 🧠 Tricky Interview Question
**Q**: "You told the model 'do not hallucinate' in the prompt. Why is that weak?"

**Answer**: The model has no internal signal for when it is wrong, so the instruction cannot be followed reliably. Real prevention changes the system: give evidence, use tools, constrain outputs, verify. Instructions help only when paired with an explicit abstention path ("say INSUFFICIENT").

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Name three ways to prevent hallucination.
A1: RAG with trusted context, tool/DB lookup, strict prompts with abstention.

Q2: [Easy] Why use temperature 0?
A2: Less randomness, more stable answers. It does not guarantee truth.

Q3: [Medium] How does structured output help?
A3: Restricts values (for example an enum of valid codes) so the model cannot invent a field value, and it makes validation simple.

Q4: [Medium] What is quote-then-answer?
A4: The model must quote supporting text first, and code verifies the quote exists in the context. No quote means no answer.

Q5: [Hard] Design prevention for 100K SKUs with daily rule updates.
A5: Index tariff text with versioned embeddings, hybrid retrieval plus rerank, DB-backed duty lookup, enum-constrained codes per retrieved candidates, verification node, abstention to human, nightly re-index, and an eval set re-run on each release.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Facts must be exact (codes, prices, dates)
- A wrong answer is costly

❌ Avoid heavy prevention when:
- Brainstorming or creative tasks
- Latency must be minimal and risk is small

---

## 📊 Visual Diagram
```
Question ─► [Retriever] ─► context ─┐
                                    ├─► [LLM temp=0, JSON schema] ─► {code, quote}
 [Tariff DB tool] ──────────────────┘                                  │
                                              verify(code in allowed, quote in ctx)
                                                    │ok          │fail
                                                 answer     retry once ─► abstain/human
```

---

## 💰 Cost Impact
Context adds input tokens (4 chunks x 300 tokens = about 1,200 tokens, roughly $0.00018 per call on gpt-4o-mini). A retry doubles that for failures only (maybe 5%). Short structured output (about 50 tokens) is cheaper than free text. Savings: fewer escalations to humans. Optimise by limiting top-k, reranking, caching retrieval, and using DB lookups instead of generation.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RAG | Retrieve then generate | पहले खोजो फिर लिखो |
| Abstention | Refusing to guess | अनुमान से मना करना |
| Structured output | Schema-bound output | schema वाला output |
| Enum constraint | Only allowed values | सिर्फ मान्य values |
| Tool call | Model asks code for data | exact data के लिए function call |
| Verification | Check output after | output की जाँच |

---

## ⚡ 3-Line Summary
English: Prevent hallucination by giving evidence, using tools for exact data, constraining output and verifying. Always allow the model to say "I don't know". Prompts alone do not work.
Hindi: Evidence देकर, exact data के लिए tools लगाकर, output सीमित करके और verify करके hallucination रोको। Model को "पता नहीं" कहने की अनुमति हमेशा दो। सिर्फ prompts काम नहीं करते।

---

## ➡️ Next Topic
**465. Grounding Responses** - the core technique behind most prevention: tying every statement to a source.
