---

# 487. Fine Tuning vs RAG
# हिंदी में: Fine Tuning बनाम RAG

---

## 🔵 Simple Definition (English)
RAG gives the model facts at question time by fetching documents and putting them in the prompt. Fine tuning changes the model itself so it behaves differently. Rule of thumb: RAG is for what the model should KNOW, fine tuning is for how the model should BEHAVE.

## 🔵 सरल परिभाषा (Hindi)
RAG सवाल पूछने के समय documents लाकर prompt में डाल देती है, यानी model को facts देती है। Fine tuning model को ही बदल देती है ताकि वह अलग तरह से behave करे। Rule of thumb: RAG वह है जो model को पता होना चाहिए (KNOW), fine tuning वह है कि model कैसे behave करे (BEHAVE)।

---

## 🔴 Problem it Solves
Teams often pick the wrong tool. They fine tune to add knowledge and get hallucinations, or they stuff a huge prompt to force a format and pay too much. Knowing which technique solves which problem saves weeks of work and money.

## 🔴 यह क्यों बना? (Hindi)
Teams अक्सर गलत tool चुन लेती हैं। Knowledge डालने के लिए fine tune करती हैं और hallucination मिलता है, या format के लिए बहुत बड़ा prompt भरकर ज़्यादा पैसे देती हैं। सही tool पता हो तो हफ्तों का काम और पैसा बचता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Ask: is the problem missing KNOWLEDGE or wrong BEHAVIOUR?
Step 2 → Knowledge changes often or is private → choose RAG
Step 3 → Format, tone, classification skill → choose fine tuning
Step 4 → Need both → fine tune for behaviour, add RAG for facts
Step 5 → Build an eval set and compare options on the same questions
Step 6 → Pick the cheapest option that meets the quality bar
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पूछो: समस्या KNOWLEDGE की कमी है या BEHAVIOUR गलत है?
Step 2 → Knowledge बार-बार बदलती है या private है → RAG चुनो
Step 3 → Format, tone, classification skill → fine tuning चुनो
Step 4 → दोनों चाहिए → behaviour के लिए fine tune, facts के लिए RAG
Step 5 → Eval set बनाओ और एक ही सवालों पर options compare करो
Step 6 → सबसे सस्ता option चुनो जो quality bar पूरा करे
```

---

## 🟡 Real World Example
**Tariff Classification System**: Customs duty rates change every budget. Putting rates into model weights means retraining each time, so rates come from RAG (retrieve the latest notification). But the JSON output format and the habit of citing the HS chapter note are behaviour, so we fine tune a small model for that. Final design: fine tuned model plus RAG context.

**Amazon-style**: Product Q&A bot uses RAG over the product catalog (facts change daily), while a fine tuned model keeps the brand voice.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs duty rates हर budget में बदलते हैं। Rates को weights में डालने का मतलब हर बार retrain, इसलिए rates RAG से आते हैं (latest notification retrieve करो)। लेकिन JSON format और HS chapter note cite करने की आदत behaviour है, इसलिए उसके लिए छोटा model fine tune करते हैं। Final design: fine tuned model + RAG context।

**Amazon-style**: Product Q&A bot catalog पर RAG चलाता है (facts रोज़ बदलते हैं), और fine tuned model brand voice बनाए रखता है।

---

## 💻 Code Example — Basic
```python
# Basic: a tiny decision helper that picks RAG, fine tuning or both
from typing import Literal  # restrict return values

Choice = Literal["rag", "fine_tune", "both", "prompt_only"]  # allowed answers


def choose(knowledge_changes: bool, needs_special_format: bool, needs_private_facts: bool) -> Choice:
    """Return the suggested technique based on three yes/no questions."""
    needs_rag = knowledge_changes or needs_private_facts  # facts problem?
    if needs_rag and needs_special_format:  # both problems
        return "both"
    if needs_rag:  # only facts
        return "rag"
    if needs_special_format:  # only behaviour
        return "fine_tune"
    return "prompt_only"  # neither: a good prompt is enough


# Tariff system: rates change AND strict JSON needed
print(choose(True, True, True))  # both
# Sentiment tagging: static task, special labels
print(choose(False, True, False))  # fine_tune
# FAQ over company wiki: changing facts, normal answer style
print(choose(True, False, True))  # rag
```

## 💻 Code Example — Advanced
```python
# Production style: run the same eval questions through RAG and tuned model and compare
import asyncio  # async execution
from dataclasses import dataclass  # result container
from typing import Awaitable, Callable, List  # type hints

Answerer = Callable[[str], Awaitable[str]]  # async function: question -> answer


@dataclass
class EvalCase:
    question: str  # input question
    expected: str  # expected answer substring


async def score(answerer: Answerer, cases: List[EvalCase]) -> float:
    """Fraction of cases where the expected text appears in the answer."""
    if not cases:  # avoid divide by zero
        raise ValueError("cases must not be empty")
    answers = await asyncio.gather(*(answerer(c.question) for c in cases))  # run in parallel
    hits = sum(1 for a, c in zip(answers, cases) if c.expected.lower() in a.lower())  # count hits
    return hits / len(cases)  # accuracy


async def fake_rag(q: str) -> str:
    """Stub: pretend RAG returns the latest rate (replace with real pipeline)."""
    return "Duty rate is 20% per latest notification"


async def fake_tuned(q: str) -> str:
    """Stub: pretend tuned model returns an old memorised rate."""
    return "Duty rate is 10%"


async def main() -> None:
    cases = [EvalCase("Duty on smartphones?", "20%")]  # tiny eval set
    print("RAG:", await score(fake_rag, cases))  # RAG accuracy
    print("Tuned only:", await score(fake_tuned, cases))  # tuned accuracy


if __name__ == "__main__":
    asyncio.run(main())  # run demo (offline, uses stubs)
```

---

## 🟠 FastAPI Integration
One endpoint can combine both: retrieve context (RAG) and call the tuned model.

```python
import os  # env variables
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # schema
from openai import AsyncOpenAI  # client

app = FastAPI()  # app
client = AsyncOpenAI()  # needs OPENAI_API_KEY
MODEL = os.getenv("TARIFF_MODEL", "gpt-4o-mini")  # tuned model id in production


class Ask(BaseModel):
    question: str  # user question


async def retrieve(question: str) -> str:
    """Placeholder retriever: replace with your vector DB search."""
    return "Notification 12/2024: smartphones BCD 20%"


@app.post("/ask")
async def ask(body: Ask) -> dict:
    context = await retrieve(body.question)  # RAG gives fresh facts
    resp = await client.chat.completions.create(
        model=MODEL,  # tuned model gives format/behaviour
        messages=[{"role": "user", "content": f"Context: {context}\nQ: {body.question}"}],
        max_tokens=150,
    )
    return {"answer": resp.choices[0].message.content, "tokens": resp.usage.total_tokens}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain is built around RAG (retrievers, vector stores). A tuned model plugs in as the LLM of the same chain, so you can combine both easily.

```python
from langchain_openai import ChatOpenAI  # chat model
from langchain_core.prompts import ChatPromptTemplate  # prompts

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # swap with ft: model id
prompt = ChatPromptTemplate.from_template("Context: {context}\nQuestion: {question}")  # RAG prompt
chain = prompt | llm  # context comes from a retriever step in a full chain
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using fine tuning for frequently changing data
✅ Correct: Use RAG so updating a document updates the answer immediately.

```python
# Wrong: retrain every time a rate changes
# Right: update the vector DB document, no training needed
```

❌ Mistake 2: Using RAG to enforce style
✅ Correct: Use fine tuning or a clear system prompt for style and format.

```python
# Wrong: retrieve "style guide" chunks and hope the model follows them
# Right: fine tune on examples that already follow the style
```

---

## 🧠 Tricky Interview Question
**Q**: "Our support bot must answer from 5,000 internal docs and always reply in our brand tone with a fixed JSON schema. RAG or fine tuning?"

**Answer**: Both, for different jobs. RAG supplies the facts, with source citations and easy updates. Fine tuning (or structured outputs) handles tone and JSON. If JSON can be enforced by structured output features, you may not need fine tuning at all. Test it before paying for training.

---

## ⚫ Interview Questions + Answers

Q1: One line difference between RAG and fine tuning? (Easy)
A1: RAG changes the input (adds retrieved facts); fine tuning changes the model (weights).

Q2: Which one is better for fresh data? (Easy)
A2: RAG, because you just update the documents.

Q3: Which has the higher upfront cost? (Medium)
A3: Fine tuning needs data prep and training. RAG needs an index and retrieval infrastructure but no training; its cost is per call (extra context tokens).

Q4: Can they be combined? (Medium)
A4: Yes. A common pattern is a small fine tuned model for format and tone, with RAG supplying facts. This is often called RAFT-style or hybrid setup.

Q5: How do you decide with evidence? (Hard)
A5: Build an eval set of real questions with graded answers. Measure baseline prompt, prompt plus RAG, fine tuned model, and fine tuned plus RAG. Compare quality, latency and cost per 1000 calls. Choose the cheapest option meeting the bar, and re-evaluate when data or traffic changes.

---

## 🔷 When to Use + When Not to Use
✅ Use RAG when:
- Knowledge is large, private or changes often
- You need citations and traceability

✅ Use fine tuning when:
- You need stable format, tone or a narrow skill
- You want shorter prompts at high volume

❌ Avoid when:
- RAG for pure style problems
- Fine tuning for facts that change monthly

---

## 📊 Visual Diagram
```
            RAG                         FINE TUNING
 Question ─► Retriever ─► Docs      Examples ─► Training ─► New weights
     │                      │                                  │
     └──────► Prompt + Docs ┘                 Question ───────►│──► Answer
                    │
                    ▼
                  LLM ─► Answer

 Knowledge lives in: DOCUMENTS        Knowledge/behaviour lives in: WEIGHTS
 Update by: edit docs                 Update by: retrain
```

---

## 💰 Cost Impact
- RAG adds tokens on every call (retrieved chunks, e.g. 1,500 extra input tokens). Reduce with better chunking, reranking and top-k tuning.
- Fine tuning adds a one time training cost and a higher per-token price for tuned models (illustrative; check current pricing), but cuts prompt size.
- Hybrid: tuned small model plus 3 short chunks is often cheaper than a large model plus 10 chunks.
- Measure cost per 1,000 correct answers, not just cost per call.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RAG | Retrieve docs then generate | Documents लाकर जवाब बनाना |
| Fine tuning | Train model on examples | Examples पर model train करना |
| Hybrid | Use both together | दोनों साथ इस्तेमाल करना |
| Grounding | Answer based on given sources | Sources पर आधारित जवाब |
| Eval set | Graded test questions | जाँच के लिए graded सवाल |
| Hallucination | Confident but wrong output | आत्मविश्वास से गलत जवाब |

---

## ⚡ 3-Line Summary
English: RAG is for knowledge that changes or is private; fine tuning is for behaviour, format and narrow skills.
They solve different problems and work well together.
Decide using an eval set and cost per correct answer.
Hindi: RAG बदलती या private knowledge के लिए है; fine tuning behaviour, format और narrow skills के लिए।
दोनों अलग समस्याएँ हल करती हैं और साथ में अच्छा काम करती हैं।
Eval set और cost per correct answer से फैसला लो।

---

## ➡️ Next Topic
**488. When to Fine Tune** — concrete signals that tell you fine tuning is worth the effort.
