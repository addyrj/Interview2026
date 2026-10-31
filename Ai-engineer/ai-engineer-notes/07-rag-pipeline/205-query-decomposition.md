---

# 205. Query Decomposition
# हिंदी में: Query Decomposition (सवाल को छोटे हिस्सों में तोड़ना)

---

## 🔵 Simple Definition (English)
Query decomposition breaks one complex, multi-part question into several simple sub-questions. Each sub-question is retrieved separately, and the answers are merged. It helps when one vector search cannot find all the facts needed.

## 🔵 सरल परिभाषा (Hindi)
Query decomposition में एक complex, multi-part सवाल को कई simple sub-questions में तोड़ा जाता है। हर sub-question का retrieval अलग होता है और आख़िर में answers merge होते हैं। जब एक vector search सारे facts नहीं ला पाता, तब यह काम आता है।

---

## 🔴 Problem it Solves
A question like "Compare the import duty of smartphones and laptops from China and say which is cheaper" has 4 facts inside it. One embedding of the whole sentence is a blurry average of all of them. Top-k chunks then cover only one topic, and the LLM either hallucinates the rest or says "not found". Decomposition gives every fact its own focused search.

## 🔴 यह क्यों बना? (Hindi)
"Smartphones और laptops की China से import duty compare करो" जैसे सवाल में 4 facts छुपे हैं। पूरे sentence का एक embedding सबका धुंधला average बनता है। Top-k chunks सिर्फ़ एक topic cover करते हैं और LLM बाकी का अंदाज़ा लगाता है। Decomposition हर fact को अपना focused search देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → User asks a complex question
Step 2 → An LLM (or rules) splits it into 2-5 independent sub-questions
Step 3 → Each sub-question runs through retriever (in parallel, asyncio.gather)
Step 4 → Retrieved chunks are de-duplicated and grouped per sub-question
Step 5 → Optional: answer each sub-question alone (sub-answers)
Step 6 → Final LLM call merges sub-answers / all chunks into one answer
Step 7 → Return answer + sources + token usage (N+2 LLM calls total)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → User complex सवाल पूछता है
Step 2 → LLM (या rules) उसे 2-5 independent sub-questions में बाँटता है
Step 3 → हर sub-question retriever से parallel चलता है
Step 4 → Chunks को de-duplicate करके sub-question के हिसाब से group करो
Step 5 → चाहो तो हर sub-question का अलग answer बनाओ
Step 6 → Final LLM call सब answers को merge करता है
Step 7 → Answer + sources + token usage return करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: "What is the duty on a Bluetooth speaker with a built-in power bank, and does it qualify for the India-UAE trade deal?" The system splits it into: (1) HS code of Bluetooth speaker, (2) HS treatment of power-bank goods, (3) India-UAE CEPA eligibility rules. Each hits a different part of the tariff schedule. **Zomato AI**: "Veg places under 500 rupees that are open now and have parking" becomes three filters/lookups. **Amazon**: "Compare iPhone 15 and Galaxy S24 battery" becomes two product lookups.

## 🟡 Real Example Hindi mein
**Tariff System**: "Bluetooth speaker जिसमें power bank है, उस पर duty क्या है और India-UAE deal लगेगी?" Split होता है: (1) speaker का HS code, (2) power-bank goods का treatment, (3) CEPA eligibility rules। हर हिस्सा tariff schedule के अलग section में है। **Zomato**: "500 से कम, veg, अभी खुला, parking वाला" = तीन अलग lookups। **Amazon**: "iPhone 15 vs Galaxy S24 battery" = दो product lookups।

---

## 💻 Code Example — Basic
```python
# Pure Python, no API key needed. Rule-based decomposition + toy keyword retriever.
from typing import Dict, List  # type hints for clarity

# A tiny in-memory "tariff knowledge base": id -> text
KB: Dict[str, str] = {
    "d1": "Smartphones HS 8517.13 basic customs duty is 20 percent from China.",  # fact 1
    "d2": "Laptops HS 8471.30 basic customs duty is 0 percent under IT agreement.",  # fact 2
    "d3": "Antidumping duty on selected Chinese goods is reviewed yearly.",  # fact 3
}


def decompose(question: str) -> List[str]:
    """Split a compound question on ' and ' / ' vs ' (naive rule-based)."""
    parts: List[str] = []  # collect sub-questions here
    for chunk in question.replace(" vs ", " and ").split(" and "):  # normalise then split
        chunk = chunk.strip(" ?")  # trim spaces and question mark
        if chunk:  # skip empty pieces
            parts.append(chunk + "?")  # restore question mark
    return parts  # list of sub-questions


def retrieve(sub_q: str, k: int = 1) -> List[str]:
    """Score docs by shared lowercase words with the sub-question."""
    words = set(sub_q.lower().replace("?", "").split())  # query word set
    scored = []  # (score, doc_id) pairs
    for doc_id, text in KB.items():  # loop over documents
        overlap = len(words & set(text.lower().replace(".", "").split()))  # shared words
        scored.append((overlap, doc_id))  # remember score
    scored.sort(reverse=True)  # best first
    return [KB[doc_id] for _, doc_id in scored[:k]]  # top-k texts


if __name__ == "__main__":
    q = "What is duty on smartphones and laptops from China?"  # complex question
    subs = decompose(q)  # step 1: decompose
    print("Sub-questions:", subs)  # show them
    for s in subs:  # step 2: retrieve for each
        print(s, "->", retrieve(s))  # print best chunk
```

## 💻 Code Example — Advanced
```python
# Production style: LLM decomposition with structured output, parallel retrieval, fallback.
import asyncio  # run retrievals concurrently
import logging  # error logging
from typing import List  # type hints

from openai import AsyncOpenAI  # openai>=1 async client
from pydantic import BaseModel, Field  # pydantic v2 schema

logger = logging.getLogger("decompose")  # module logger
client = AsyncOpenAI()  # reads OPENAI_API_KEY from env


class SubQuestions(BaseModel):
    """Schema the LLM must fill."""
    questions: List[str] = Field(min_length=1, max_length=5)  # 1-5 sub-questions


async def decompose_llm(question: str) -> List[str]:
    """Ask a cheap model to split the question; fall back to the original on error."""
    try:  # network + parsing can fail
        resp = await client.beta.chat.completions.parse(  # structured outputs helper
            model="gpt-4o-mini",  # cheap model is enough for splitting
            messages=[
                {"role": "system", "content": "Split the question into independent sub-questions. If it is already simple, return it unchanged."},
                {"role": "user", "content": question},  # user's question
            ],
            response_format=SubQuestions,  # pydantic model as schema
            temperature=0,  # deterministic splitting
            max_tokens=200,  # sub-questions are short
        )
        parsed = resp.choices[0].message.parsed  # typed object or None
        if parsed is None:  # model refused or invalid
            return [question]  # fallback
        logger.info("decompose tokens=%s", resp.usage.total_tokens)  # track cost
        return parsed.questions  # list of strings
    except Exception as exc:  # never break the whole pipeline
        logger.warning("decompose failed: %s", exc)  # log reason
        return [question]  # graceful fallback


async def retrieve_one(sub_q: str) -> List[str]:
    """Placeholder async retriever; swap with vector DB call."""
    await asyncio.sleep(0)  # yield control like real I/O
    return [f"chunk for: {sub_q}"]  # fake chunk


async def answer(question: str) -> str:
    """Decompose -> parallel retrieve -> merge -> generate."""
    subs = await decompose_llm(question)  # step 1
    results = await asyncio.gather(*(retrieve_one(s) for s in subs))  # step 2 parallel
    seen: set[str] = set()  # de-duplicate chunks
    context: List[str] = []  # final context list
    for group in results:  # each sub-question's chunks
        for chunk in group:  # each chunk
            if chunk not in seen:  # skip duplicates
                seen.add(chunk)  # remember
                context.append(chunk)  # keep
    resp = await client.chat.completions.create(  # final generation
        model="gpt-4o-mini",  # model
        messages=[
            {"role": "system", "content": "Answer only from the context."},
            {"role": "user", "content": "Context:\n" + "\n".join(context) + f"\n\nQuestion: {question}"},
        ],
        max_tokens=400,  # cap output
    )
    return resp.choices[0].message.content or ""  # text answer
```

---

## 🟠 FastAPI Integration
Decomposition is an extra pre-step in the route. Return the sub-questions in the response so the UI and logs can show how the question was understood.

```python
from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel  # request/response models

app = FastAPI()  # app instance


class AskReq(BaseModel):
    question: str  # raw user question


class AskRes(BaseModel):
    answer: str  # final answer
    sub_questions: list[str]  # for transparency/debugging


@app.post("/ask", response_model=AskRes)  # POST /ask
async def ask(req: AskReq) -> AskRes:
    try:  # guard the pipeline
        subs = await decompose_llm(req.question)  # from advanced example
        text = await answer(req.question)  # full pipeline
        return AskRes(answer=text, sub_questions=subs)  # typed response
    except Exception as exc:  # unexpected error
        raise HTTPException(status_code=502, detail="RAG pipeline failed") from exc  # clean 502
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has `MultiQueryRetriever` (generates query variants, not true decomposition). For real decomposition, use an LCEL chain with structured output, then `.abatch` on the retriever. In LangGraph, make `decompose` a node and use `Send` for map-reduce fan-out.

```python
from langchain_core.prompts import ChatPromptTemplate  # prompt object
from langchain_openai import ChatOpenAI  # chat model wrapper
from pydantic import BaseModel  # schema


class Subs(BaseModel):
    questions: list[str]  # sub-questions


prompt = ChatPromptTemplate.from_template("Split into sub-questions: {q}")  # template
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # model
chain = prompt | llm.with_structured_output(Subs)  # LCEL pipe
# subs = await chain.ainvoke({"q": "Compare duty on phones and laptops"})  # run
# docs_per_sub = await retriever.abatch(subs.questions)  # parallel retrieval
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Decomposing every query, even simple ones
✅ Correct: Route only complex queries (contains "and", "compare", multiple entities).

```python
# Wrong: always pay for an extra LLM call
subs = await decompose_llm("HS code of iPhone?")  # wasteful

# Right: cheap gate first
def needs_split(q: str) -> bool:
    return any(w in q.lower() for w in (" and ", " vs ", "compare", " both "))  # heuristic

subs = await decompose_llm(q) if needs_split(q) else [q]  # skip when simple
```

❌ Mistake 2: Running sub-question retrieval one by one
✅ Correct: Use `asyncio.gather` so latency is max(), not sum().

```python
# Wrong: sequential, 5 x 200ms = 1s
for s in subs:
    docs = await retrieve_one(s)

# Right: parallel, about 200ms
all_docs = await asyncio.gather(*(retrieve_one(s) for s in subs))
```

---

## 🧠 Tricky Interview Question
**Q**: "After adding decomposition, accuracy went up but p95 latency doubled and cost rose 3x. How do you fix it without losing the accuracy gain?"

**Answer**: Add a router so simple queries skip decomposition (most traffic is simple). Run sub-retrievals in parallel. Use a small model for decomposition and cache decompositions for repeated questions. Cap sub-questions at 3-4. Merge all chunks into ONE final generation call instead of one generation per sub-question. This keeps LLM calls at 2 for complex queries and 1 for simple ones.

---

## ⚫ Interview Questions + Answers

Q1: What is query decomposition?
A1: Splitting a complex question into simpler sub-questions, retrieving for each, then combining the results.

Q2: When is it useful?
A2: Multi-hop, comparison, or multi-entity questions where one embedding cannot capture every part.

Q3: How is it different from multi-query (query expansion)?
A3: Multi-query rewrites the SAME question in several wordings to improve recall. Decomposition creates DIFFERENT questions that each need their own facts.

Q4: How do you handle sub-questions that depend on earlier answers (multi-hop)?
A4: Run them sequentially: answer step 1, inject the result into step 2's question (e.g. "What is the HS code?" then "What is the duty for <that code>?"). Independent ones go in parallel. LangGraph handles this well with a loop and state.

Q5: How do you evaluate whether decomposition helps?
A5: Build a test set of complex questions with labelled supporting docs. Compare recall@k and answer correctness (LLM-as-judge) with and without decomposition, and also measure latency and cost per query. Only keep it for the question types where the gain is worth the extra cost.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Questions compare things or ask about multiple entities
- Multi-hop reasoning (answer of A is needed to ask B)
- Documents are split across many sections

❌ Avoid when:
- Questions are simple single-fact lookups
- Strict low-latency budgets (under 1 second)
- The decomposer model is weaker than the data complexity (bad splits hurt)

---

## 📊 Visual Diagram
```
 "Duty on phones AND laptops from China?"
                   │
                   ▼
            ┌─────────────┐
            │ Decomposer  │  (LLM, ~150 tokens)
            └──────┬──────┘
       ┌───────────┼───────────┐
       ▼           ▼           ▼
   sub-Q1       sub-Q2      sub-Q3
  (phones)     (laptops)   (China rules)
       │           │           │
   retrieve    retrieve    retrieve     (parallel)
       └───────────┼───────────┘
                   ▼
           merge + de-dupe chunks
                   ▼
             final LLM answer
```

---

## 💰 Cost Impact
- Decomposition call: about 100-200 input + 50-100 output tokens (cheap model).
- Final answer call: grows with merged context (N sub-questions x k chunks x ~300 tokens).
- Example: 3 sub-questions x 3 chunks x 300 tokens = 2,700 context tokens vs 900 for plain RAG (3x).
- Optimise: gate simple queries, use gpt-4o-mini for splitting, cap sub-questions, retrieve k=2 per sub-question, rerank then trim, cache decompositions.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Decomposition | Break a query into parts | सवाल को हिस्सों में तोड़ना |
| Sub-question | One simple part of a big question | छोटा सवाल |
| Multi-hop | Answer needs chained lookups | कई कदम वाला reasoning |
| Fan-out / Fan-in | Run many, then merge | बाँटना और फिर जोड़ना |
| Router | Decides whether to decompose | तय करने वाला gate |

---

## ⚡ 3-Line Summary
English: Query decomposition splits a complex question into simple sub-questions. Each is retrieved in parallel and the results are merged for one answer. Gate it, cap it, and use a cheap model to keep cost and latency low.
Hindi: Query decomposition complex सवाल को simple sub-questions में तोड़ता है। हर एक का retrieval parallel होता है और results merge होते हैं। Gate लगाओ, limit रखो और सस्ता model use करो ताकि cost और latency कम रहे।

---

## ➡️ Next Topic
**206. Reranking — What + Why** — after retrieving many chunks (especially from several sub-questions), reranking picks the truly best ones before they go to the LLM.
