---

# 215. RAG Response Generation
# हिंदी में: RAG Response Generation

---

## 🔵 Simple Definition (English)
Response generation is the last RAG step: the LLM reads the question plus the prepared context and writes the final answer. Good generation is grounded (only from context), well formatted, honest about gaps, and cheap in tokens.

## 🔵 सरल परिभाषा (Hindi)
Response generation RAG का आख़िरी step है: LLM question और तैयार context पढ़कर final answer लिखता है। अच्छी generation grounded (सिर्फ़ context से), सही format में, कमियों के बारे में ईमानदार और tokens में सस्ती होती है।

---

## 🔴 Problem it Solves
Retrieval can be perfect and the answer still bad: the model adds outside facts, ignores the context, writes too long, or states things with false confidence. Controlled generation settings (low temperature, output schema, token caps, a grounding check) turn good chunks into reliable answers.

## 🔴 यह क्यों बना? (Hindi)
Retrieval perfect हो सकता है फिर भी answer खराब: model बाहर के facts जोड़ता है, context ignore करता है, ज़्यादा लंबा लिखता है या झूठे भरोसे से बोलता है। नियंत्रित generation (कम temperature, output schema, token cap, grounding check) अच्छे chunks को भरोसेमंद answers में बदलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Receive question + final ranked/compressed chunks (with ids)
Step 2 → Build messages (system rules + labelled context + question)
Step 3 → Pick settings: temperature 0-0.2, max_tokens cap, structured output
Step 4 → Call the LLM (sync, async, or stream)
Step 5 → Parse + validate: citations real? status OK/NOT_FOUND? length OK?
Step 6 → Optional grounding check (does each claim appear in context?)
Step 7 → Return answer + sources + usage (prompt/completion tokens)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Question + final ranked/compressed chunks (ids के साथ) मिलते हैं
Step 2 → Messages बनाओ (system rules + labelled context + question)
Step 3 → Settings: temperature 0-0.2, max_tokens cap, structured output
Step 4 → LLM call करो (sync, async या stream)
Step 5 → Parse + validate: citations असली? status OK/NOT_FOUND? length ठीक?
Step 6 → चाहो तो grounding check (हर claim context में है?)
Step 7 → Answer + sources + usage (prompt/completion tokens) लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: Output schema: `{hs_code, duty_percent, reasoning, sources[], confidence}`. A post-check verifies that the `hs_code` string literally appears in one of the cited chunks; if not, status becomes NEEDS_REVIEW and a human officer sees it. **Zomato**: answer in 2 sentences with the refund amount. **Amazon**: product answer with "based on 12 reviews" and links.

## 🟡 Real Example Hindi mein
**Tariff System**: Output schema: `{hs_code, duty_percent, reasoning, sources[], confidence}`। Post-check देखता है कि `hs_code` string सच में cited chunk में है; नहीं तो status NEEDS_REVIEW हो जाता है और human officer देखता है। **Zomato**: 2 sentences में refund amount के साथ answer। **Amazon**: "12 reviews के आधार पर" और links के साथ product answer।

---

## 💻 Code Example — Basic
```python
# Basic generation step with a fake LLM (offline). Shows the grounding check idea.
import re  # find code patterns
from typing import Dict, List  # type hints


def fake_llm(question: str, context: List[str]) -> Dict[str, str]:
    """Stand-in LLM: returns the first HS code found in context."""
    for i, chunk in enumerate(context, 1):  # loop chunks with ids
        m = re.search(r"\b\d{4}\.\d{2}\b", chunk)  # HS code pattern like 8517.13
        if m:  # found one
            return {"answer": m.group(0), "source": f"S{i}"}  # grounded answer
    return {"answer": "NOT_FOUND", "source": ""}  # nothing in context


def grounded(answer: str, context: List[str]) -> bool:
    """True if the answer string literally appears in the context."""
    return any(answer in c for c in context)  # simple substring check


def generate(question: str, context: List[str]) -> Dict[str, str]:
    out = fake_llm(question, context)  # call model
    if out["answer"] != "NOT_FOUND" and not grounded(out["answer"], context):  # verify
        return {"answer": "NEEDS_REVIEW", "source": ""}  # unsafe -> human review
    return out  # safe answer


if __name__ == "__main__":
    ctx = ["Smartphones are classified under HS 8517.13 with 20 percent duty."]  # context
    print(generate("HS code for smartphone?", ctx))  # answer with source
    print(generate("HS code for a unicorn?", ["Bananas HS code is in chapter 08."]))  # not found
```

## 💻 Code Example — Advanced
```python
# Production: async generation with structured output, usage tracking, grounding check, retries.
import asyncio  # sleep for retry
import logging  # logs
from typing import Literal, Optional  # typing

from openai import APIConnectionError, APIStatusError, AsyncOpenAI, RateLimitError  # errors + client
from pydantic import BaseModel, Field  # pydantic v2

logger = logging.getLogger("generate")  # logger
client = AsyncOpenAI(max_retries=0)  # we control retries ourselves


class TariffAnswer(BaseModel):
    status: Literal["OK", "NOT_FOUND", "NEEDS_REVIEW"]  # result state
    hs_code: Optional[str] = Field(default=None, pattern=r"^\d{4}\.\d{2}$")  # validated code
    reasoning: str  # short explanation
    sources: list[str] = Field(default_factory=list)  # chunk ids


class GenResult(BaseModel):
    answer: TariffAnswer  # structured answer
    prompt_tokens: int  # usage
    completion_tokens: int  # usage


async def generate(question: str, chunks: list[str], retries: int = 3) -> GenResult:
    ctx = "\n".join(f"[S{i}] {c}" for i, c in enumerate(chunks, 1))  # labelled context
    messages = [
        {"role": "system", "content": "Classify using ONLY the context. Cite chunk ids. If absent, status=NOT_FOUND."},
        {"role": "user", "content": f"<context>\n{ctx}\n</context>\nQuestion: {question}"},
    ]
    for attempt in range(retries):  # retry loop
        try:  # API call
            resp = await client.beta.chat.completions.parse(
                model="gpt-4o-mini", messages=messages, response_format=TariffAnswer,
                temperature=0, max_tokens=300,  # deterministic and capped
            )
            ans = resp.choices[0].message.parsed  # typed answer or None
            if ans is None:  # refusal
                ans = TariffAnswer(status="NOT_FOUND", reasoning="Model refused")  # safe
            if ans.hs_code and not any(ans.hs_code in c for c in chunks):  # grounding check
                ans.status = "NEEDS_REVIEW"  # code not in context
            u = resp.usage  # token usage
            return GenResult(answer=ans, prompt_tokens=u.prompt_tokens, completion_tokens=u.completion_tokens)
        except (RateLimitError, APIConnectionError) as exc:  # transient
            logger.warning("retry %d: %s", attempt + 1, exc)  # log
            await asyncio.sleep(2 ** attempt)  # backoff
        except APIStatusError as exc:  # 4xx/5xx other
            logger.error("API error %s", exc.status_code)  # log
            break  # do not retry
    return GenResult(answer=TariffAnswer(status="NEEDS_REVIEW", reasoning="LLM unavailable"), prompt_tokens=0, completion_tokens=0)
```

---

## 🟠 FastAPI Integration
Return structured JSON plus usage so clients can show sources and you can bill or monitor.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()  # app


class Req(BaseModel):
    question: str  # question


@app.post("/classify", response_model=GenResult)  # typed response
async def classify(req: Req) -> GenResult:
    chunks = ["Smartphones HS 8517.13 duty 20 percent."]  # from retrieve -> rerank -> compress
    return await generate(req.question, chunks)  # grounded answer
```

---

## 🔗 LangChain / LangGraph Connection
The generation node in a LangGraph RAG graph reads `state["question"]` and `state["docs"]`, calls the model with `with_structured_output`, and writes `state["answer"]`. A conditional edge can route `NEEDS_REVIEW` to a human-in-the-loop node.

```python
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_openai import ChatOpenAI  # model
from pydantic import BaseModel  # schema


class Out(BaseModel):
    hs_code: str | None  # code or None
    reasoning: str  # why


prompt = ChatPromptTemplate.from_messages([("system", "Use only the context."), ("human", "{context}\n\nQ: {question}")])
chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Out)  # LCEL
# result = await chain.ainvoke({"context": ctx, "question": q})  # typed Out
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: High temperature for factual answers
✅ Correct: Use 0 to 0.2.

```python
# Wrong: creative rates and codes
temperature = 1.0

# Right: stable facts
temperature = 0
```

❌ Mistake 2: Trusting the model's confidence and citations blindly
✅ Correct: Verify against the retrieved chunks.

```python
# Wrong: return whatever the model says
return answer

# Right: check that cited ids exist and the code appears in context
assert all(c in valid_ids for c in answer.sources)
```

---

## 🧠 Tricky Interview Question
**Q**: "Faithfulness score is 0.95 but users say answers are unhelpful. What is happening?"

**Answer**: Faithfulness only measures that claims are supported by the context, not that the answer is complete or relevant. The model may be over-refusing, answering only a part, or retrieval returned supported-but-off-topic text. Track answer relevance, completeness, and context recall too (RAGAS-style metrics), review refusal rate, and check retrieval quality. Optimise the whole chain rather than one metric.

---

## ⚫ Interview Questions + Answers

Q1: What does the generation step receive?
A1: The user question and the final selected context (plus system rules).

Q2: Why use temperature 0 in RAG?
A2: To reduce randomness and hallucination, giving repeatable factual answers.

Q3: What is a grounding check?
A3: A validation that claims, numbers or codes in the answer actually appear in the retrieved context.

Q4: How do you control answer length and cost?
A4: `max_tokens`, instructions for brevity, structured output with short fields, and stop sequences.

Q5: How do you handle a model that cites sources that do not exist?
A5: Validate citation ids against the context ids, drop or flag invalid ones, use structured output with enumerated ids, and run an LLM-judge or NLI faithfulness check on a sample. If failures persist, tighten the prompt and lower context noise through reranking.

---

## 🔷 When to Use + When Not to Use
✅ Use strict grounded generation when:
- Facts, numbers or legal text matter
- You must show citations
- Answers feed other systems (JSON)

❌ Loosen it when:
- Creative or brainstorming outputs are wanted
- The context is only a hint and general knowledge is welcome (state this in the prompt)

---

## 📊 Visual Diagram
```
 question ─┐
 context  ─┼─► [Prompt] ─► LLM (temp 0, max_tokens) ─► raw/structured answer
 rules    ─┘                                               │
                                                           ▼
                                        validate: schema, citations, grounding
                                         │ pass                  │ fail
                                         ▼                       ▼
                                    return answer         NEEDS_REVIEW / retry
```

---

## 💰 Cost Impact
- Generation is usually the biggest cost: input (context) plus output tokens, and output is priced higher per token.
- Example: 1,400 input + 150 output on gpt-4o-mini = about $0.00021 + $0.00009 = $0.0003 per query (using $0.15 and $0.60 per 1M).
- Optimise: smaller model for easy queries, `max_tokens`, compact JSON, prompt caching, fewer chunks, cache answers for repeated questions, escalate to a larger model only when confidence is low.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Generation | LLM writes the answer | LLM का answer लिखना |
| Grounding | Supported by context | Context से समर्थित |
| Faithfulness | No unsupported claims | बिना बेबुनियाद दावों के |
| Structured output | JSON by schema | Schema वाला JSON |
| max_tokens | Output length cap | Output की सीमा |

---

## ⚡ 3-Line Summary
English: Generation turns the prepared context into the final answer. Use low temperature, structured output, token caps and a grounding check. Return sources and usage with every answer.
Hindi: Generation तैयार context को final answer में बदलता है। कम temperature, structured output, token cap और grounding check use करो। हर answer के साथ sources और usage लौटाओ।

---

## ➡️ Next Topic
**216. Source Citation in RAG** — how to attach trustworthy citations to each claim.
