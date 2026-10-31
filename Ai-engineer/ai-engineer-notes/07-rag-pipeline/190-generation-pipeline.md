---

# 190. Generation Pipeline
# हिंदी में: Generation Pipeline (जनरेशन पाइपलाइन)

---

## 🔵 Simple Definition (English)
The generation pipeline takes the user question plus retrieved chunks and produces the final answer: build a grounded prompt, fit it in the token budget, call the LLM, parse structured output, attach citations, and validate that the answer is supported by the context.

## 🔵 सरल परिभाषा (Hindi)
Generation pipeline user के सवाल और retrieved chunks से final जवाब बनाती है: grounded prompt बनाओ, token budget में फिट करो, LLM call करो, structured output parse करो, citations जोड़ो, और जाँचो कि जवाब context से supported है।

---

## 🔴 Problem it Solves
Even with perfect retrieval, a careless generation step hallucinates, ignores context, overflows the context window, returns unparseable text or answers with no sources. The generation pipeline makes answers faithful, bounded in cost and machine-readable.

## 🔴 यह क्यों बना? (Hindi)
Retrieval perfect हो तब भी लापरवाह generation hallucinate करता है, context ignore करता है, context window overflow करता है, unparseable text देता है या बिना sources के जवाब देता है। Generation pipeline जवाब को faithful, cost में bounded और machine-readable बनाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Receive question + ranked chunks (with ids)
Step 2 → Fit chunks into a token budget (drop lowest ranked first)
Step 3 → Build prompt: rules ("only use context, else say not found") + numbered context + question
Step 4 → Call LLM: low temperature, max_tokens cap, JSON/structured output
Step 5 → Parse and validate with a schema (Pydantic)
Step 6 → Check citations: every cited id must exist in the context
Step 7 → Optional faithfulness check (LLM judge or NLI) -> abstain if unsupported
Step 8 → Return answer + sources + token usage
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → सवाल + ranked chunks (ids के साथ) लो
Step 2 → Chunks को token budget में फिट करो (सबसे नीचे वाले पहले हटाओ)
Step 3 → Prompt: नियम ("सिर्फ context इस्तेमाल करो, वरना not found") + numbered context + सवाल
Step 4 → LLM call: कम temperature, max_tokens cap, JSON/structured output
Step 5 → Schema (Pydantic) से parse + validate
Step 6 → Citations जाँचो: हर cited id context में होनी चाहिए
Step 7 → Optional faithfulness check -> unsupported हो तो abstain
Step 8 → जवाब + sources + token usage लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: The model must return `{"hs_code": "8518.30", "duty_percent": 0, "sources": [2]}`. The prompt says "Use only the numbered context. If the code is not in context, return `hs_code: null`." The validator rejects any `hs_code` that does not appear in the cited chunk, which blocks invented codes.
**Amazon AI**: Product Q&A answers must cite the review or spec line used.

## 🟡 Real Example Hindi mein
**Tariff System**: Model को `{"hs_code": "8518.30", "duty_percent": 0, "sources": [2]}` लौटाना है। Prompt कहता है "सिर्फ numbered context इस्तेमाल करो; code context में नहीं है तो `hs_code: null`"। Validator ऐसा `hs_code` reject कर देता है जो cited chunk में नहीं है, इससे बनावटी codes रुकते हैं।
**Amazon AI**: Product Q&A के जवाब में इस्तेमाल हुई review या spec line cite होनी चाहिए।

---

## 💻 Code Example — Basic
```python
# Grounded prompt builder + citation check (pure Python, offline)
import re
from typing import Dict, List

def fit_budget(chunks: List[Dict[str, str]], max_words: int = 40) -> List[Dict[str, str]]:
    """Keep top-ranked chunks until the word budget is used (proxy for tokens)."""
    kept: List[Dict[str, str]] = []  # chunks that fit
    used = 0  # words used so far
    for c in chunks:  # chunks are already ranked best-first
        n = len(c["text"].split())  # size of this chunk
        if used + n > max_words:  # would overflow
            break
        kept.append(c); used += n
    return kept

def build_prompt(question: str, chunks: List[Dict[str, str]]) -> str:
    """Number the chunks so the model can cite [1], [2]."""
    ctx = "\n".join(f"[{i}] {c['text']}" for i, c in enumerate(chunks, start=1))  # numbered context
    return ("Answer ONLY from the context. Cite like [1]. If missing, say NOT_FOUND.\n"
            f"Context:\n{ctx}\n\nQuestion: {question}\nAnswer:")

def valid_citations(answer: str, n_chunks: int) -> bool:
    """Every [n] in the answer must refer to a real chunk and at least one must exist."""
    cited = [int(x) for x in re.findall(r"\[(\d+)\]", answer)]  # extract numbers
    return bool(cited) and all(1 <= x <= n_chunks for x in cited)

if __name__ == "__main__":
    chunks = [{"text": "HS 8518.30 headphones and earphones duty 0 percent"},
              {"text": "HS 8517.13 smartphones duty 0 percent"}]
    use = fit_budget(chunks)  # budget step
    print(build_prompt("duty on earphones?", use))  # prompt that would go to the LLM
    fake_answer = "Duty is 0 percent [1]."  # pretend LLM output
    print("citations ok:", valid_citations(fake_answer, len(use)))  # True
    print("bad citation ok:", valid_citations("Duty is 5 [9].", len(use)))  # False
```

## 💻 Code Example — Advanced
```python
# Async generation with schema validation, retries, abstention and token tracking
import asyncio
import json
import logging
from typing import Awaitable, Callable, Optional

from pydantic import BaseModel, Field, ValidationError  # pydantic v2

logger = logging.getLogger("generation")  # logger

class TariffAnswer(BaseModel):
    hs_code: Optional[str] = Field(default=None, pattern=r"^\d{4}\.\d{2}$")  # e.g. 8518.30
    duty_percent: Optional[float] = Field(default=None, ge=0, le=500)  # sane range
    sources: list[int] = Field(default_factory=list)  # cited chunk numbers

LLMFn = Callable[[str], Awaitable[tuple[str, int]]]  # returns (text, total_tokens)

class Generator:
    def __init__(self, llm: LLMFn, max_retries: int = 2) -> None:
        self.llm, self.max_retries = llm, max_retries  # deps

    async def answer(self, question: str, chunks: list[str]) -> dict:
        ctx = "\n".join(f"[{i}] {c}" for i, c in enumerate(chunks, 1))  # numbered context
        prompt = (f"Return JSON with hs_code, duty_percent, sources (chunk numbers). "
                  f"Use only the context; use null if unknown.\n{ctx}\nQ: {question}")
        total_tokens = 0  # accumulate across retries
        for attempt in range(self.max_retries + 1):
            try:
                raw, tokens = await self.llm(prompt)  # LLM call
                total_tokens += tokens
                parsed = TariffAnswer.model_validate(json.loads(raw))  # schema check
            except (json.JSONDecodeError, ValidationError) as exc:  # bad format: retry with hint
                logger.warning("attempt %d invalid output: %s", attempt, exc)
                prompt += "\nYour last output was invalid JSON/schema. Return valid JSON only."
                continue
            except Exception:  # network/provider error
                logger.exception("llm failure")
                break
            if any(s < 1 or s > len(chunks) for s in parsed.sources):  # fake citation
                continue
            if parsed.hs_code and not any(parsed.hs_code in chunks[s - 1] for s in parsed.sources):
                continue  # code not in cited chunk -> hallucination guard
            return {"ok": True, "data": parsed.model_dump(), "tokens": total_tokens}
        return {"ok": False, "data": None, "tokens": total_tokens, "reason": "unsupported or invalid"}

async def fake_llm(prompt: str) -> tuple[str, int]:
    return '{"hs_code": "8518.30", "duty_percent": 0, "sources": [1]}', 180  # offline stand-in

if __name__ == "__main__":
    g = Generator(fake_llm)  # build generator
    print(asyncio.run(g.answer("earphones duty?", ["HS 8518.30 earphones duty 0 percent"])))
```

---

## 🟠 FastAPI Integration
Return a typed response model and use streaming (Server-Sent Events) for chat UIs. Convert abstentions to a normal 200 with `answer: null` (not an error), and provider failures to 502/503.

```python
# FastAPI: typed answer endpoint + SSE streaming variant
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()  # app

class AskReq(BaseModel):
    question: str  # user question

@app.post("/answer")
async def answer(req: AskReq) -> dict:
    chunks = await get_chunks(req.question)  # retrieval layer (your function)
    result = await generator.answer(req.question, chunks)  # Generator from Advanced example
    if not result["ok"]:
        return {"answer": None, "message": "Not found in tariff documents", "tokens": result["tokens"]}
    return {"answer": result["data"], "tokens": result["tokens"]}

@app.post("/answer/stream")
async def stream(req: AskReq) -> StreamingResponse:
    async def gen():
        async for piece in llm_stream(req.question):  # async iterator of text pieces (your function)
            yield f"data: {piece}\n\n"  # SSE format
    return StreamingResponse(gen(), media_type="text/event-stream")
```

---

## 🔗 LangChain / LangGraph Connection
LangChain: `ChatPromptTemplate | llm.with_structured_output(Schema)` returns a validated Pydantic object. LangGraph: a `generate` node followed by a `grade_answer` node and a conditional edge to retry or abstain (Self-RAG / Corrective RAG patterns).

```python
# LCEL generation with structured output (needs langchain-core, langchain-openai, pydantic v2)
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

class Out(BaseModel):
    hs_code: Optional[str]  # None when unknown
    duty_percent: Optional[float]  # None when unknown

prompt = ChatPromptTemplate.from_messages([
    ("system", "Use only the context. Use null when unknown."),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])  # grounded prompt
chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Out)  # typed output
# print(chain.invoke({"context": "[1] HS 8518.30 duty 0", "question": "earphones duty?"}))  # needs OPENAI_API_KEY
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Prompt does not tell the model what to do when context lacks the answer.
✅ Correct: Give an explicit abstention rule.

```python
# Wrong
prompt = f"Context: {ctx}\nQuestion: {q}"
# Right
prompt = f"Use only the context. If the answer is not there, reply NOT_FOUND.\nContext: {ctx}\nQuestion: {q}"
```

❌ Mistake 2: Using high temperature and no `max_tokens` for factual answers.
✅ Correct: temperature 0 to 0.2 and a sensible `max_tokens`.

```python
# Wrong
client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=1.0)
# Right
client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=0, max_tokens=300)
```

---

## 🧠 Tricky Interview Question
**Q**: "The retrieved context is correct, yet the LLM gives a wrong HS code. What do you check?"

**Answer**: (1) Position: the key chunk may be in the middle ("lost in the middle"); reorder best-first or best at edges. (2) Conflict: older and newer tariff chunks both present; filter by version. (3) Prompt: does it allow outside knowledge? Tighten the rule. (4) Parametric knowledge overriding context; use temperature 0 and instruct "context wins". (5) Output validation: check the code string exists in the cited chunk. (6) Too much context; reduce k.

---

## ⚫ Interview Questions + Answers

Q1: What is grounding?
A1: Forcing the LLM to base the answer on supplied context, not its memory, and to cite it.

Q2: Why set temperature low in RAG?
A2: Factual tasks need deterministic, faithful output; high temperature increases creative drift and hallucination.

Q3: How do you stop hallucinated citations?
A3: Number the chunks, ask for ids, then programmatically verify each id exists and the quoted fact appears in that chunk.

Q4: What is the "lost in the middle" problem and what is the fix?
A4: Models use information at the start and end of long contexts better than the middle. Put the best chunks first (and last), send fewer chunks, rerank.

Q5: How do you measure generation quality?
A5: Faithfulness (answer supported by context), answer relevance, context utilisation; use RAGAS or an LLM judge on a gold set, plus citation precision. Track abstention rate; too high means retrieval problems, too low means over-confidence.

---

## 🔷 When to Use + When Not to Use
✅ Use strict structured generation when:
- Downstream code consumes the answer (APIs, databases)
- Compliance needs citations
- Wrong answers are costly

❌ Avoid strict schemas when:
- Casual chat where free text is fine
- Very small models that cannot follow JSON reliably (use constrained decoding or simpler format)

---

## 📊 Visual Diagram
```
 chunks (ranked) ─► token budget fit ─► prompt builder
                                          │  "only context, cite [n], else NOT_FOUND"
                                          ▼
                                  LLM (temp 0, max_tokens)
                                          ▼
                              parse + schema validate ──invalid──► retry (max 2)
                                          ▼
                              citation / faithfulness check ──fail──► abstain
                                          ▼
                              answer + sources + token usage
```

---

## 💰 Cost Impact
Generation is the largest cost: input = system prompt (~150) + chunks (4 x 400 = 1600) + question (~30); output ~150 tokens. With gpt-4o-mini (0.15 / 0.60 USD per 1M): about 0.00033 USD per call. A retry doubles it, and a judge call adds ~0.0003.
Optimize: fewer, better chunks; short system prompt; `max_tokens`; prompt caching for the static prefix; route simple queries to a small model; limit retries to 1-2.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Grounding | Answer tied to given context | Context पर आधारित जवाब |
| Citation | Reference to the source chunk | Source का हवाला |
| Abstention | Refusing when unsure | अनिश्चित होने पर मना करना |
| Faithfulness | Answer supported by context | जवाब का context से समर्थित होना |
| Structured output | Schema-valid JSON result | Schema वाला JSON output |
| Token budget | Max tokens allowed in prompt | Prompt की token सीमा |

---

## ⚡ 3-Line Summary
English: Generation turns retrieved chunks into a grounded, cited, schema-valid answer.
Use low temperature, token budgets, explicit abstention rules and validation of citations.
It is the biggest cost centre, so keep prompts tight.
Hindi: Generation retrieved chunks को grounded, cited, schema-valid जवाब में बदलती है।
कम temperature, token budget, साफ़ abstention नियम और citations की validation इस्तेमाल करो।
यह सबसे बड़ा cost centre है, इसलिए prompts छोटे रखो।

---

## ➡️ Next Topic
**191. Document Loaders (PDF, CSV, Web, DB)**: how raw data enters the pipeline in the first place.
