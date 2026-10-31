---

# 462. Hallucination — Types + Causes
# हिंदी में: Hallucination — प्रकार और कारण

---

## 🔵 Simple Definition (English)
Hallucination is when an LLM produces text that sounds confident but is false, made up, or not supported by the given sources. The model predicts likely words, not verified facts, so it can invent an HS code, a law clause or a URL that does not exist.

## 🔵 सरल परिभाषा (Hindi)
Hallucination तब होता है जब LLM ऐसा text बनाता है जो आत्मविश्वास से भरा लगता है लेकिन गलत, मनगढ़ंत या दिए गए sources से unsupported होता है। Model सबसे संभावित शब्द predict करता है, verified facts नहीं, इसलिए वह ऐसा HS code, कानून की धारा या URL बना सकता है जो मौजूद ही नहीं।

---

## 🔴 Problem it Solves
Understanding the types and causes lets you pick the right fix. Without that, teams try one trick (lower temperature) for every type and fail. The problem: you cannot fix what you cannot name.

## 🔴 यह क्यों बना? (Hindi)
Types और causes समझने से सही fix चुनना आसान होता है। इसके बिना teams हर type के लिए एक ही trick (temperature कम करना) आज़माती हैं और fail होती हैं। समस्या: जिसे नाम नहीं दे सकते उसे ठीक नहीं कर सकते।

---

## 🟢 How it Works — Step by Step

```
Step 1 → LLM is trained to predict the next token, not to check truth
Step 2 → Question arrives; model has weak or no knowledge about it
Step 3 → It still must output something, so it picks fluent likely tokens
Step 4 → Each token makes the next lie more consistent (snowballing)
Step 5 → Result sounds confident, has no warning
Types: (a) factual  (b) fabricated source  (c) contradiction with context
       (d) instruction drift  (e) reasoning/arithmetic error
Causes: stale training data, rare facts, ambiguous prompt, missing context,
        long context loss, high temperature, pressure to always answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → LLM अगला token predict करना सीखता है, सच check करना नहीं
Step 2 → सवाल आता है; model को उसके बारे में कम या कोई ज्ञान नहीं
Step 3 → फिर भी उसे कुछ बोलना है, इसलिए fluent संभावित tokens चुनता है
Step 4 → हर token अगले झूठ को और consistent बना देता है (snowballing)
Step 5 → नतीजा आत्मविश्वासी लगता है, कोई चेतावनी नहीं
Types: (a) factual  (b) मनगढ़ंत source  (c) context से विरोधाभास
       (d) instruction भटकना  (e) reasoning/arithmetic गलती
Causes: पुराना training data, दुर्लभ facts, अस्पष्ट prompt, context की कमी,
        लंबे context में खो जाना, ऊँचा temperature, हर हाल में जवाब देने का दबाव
```

---

## 🟡 Real World Example
**Tariff Classification System**: User asks "HS code for a smart ring". The model answers `8517.62.99` with a confident explanation. The code looks real but is not the right sub-heading in that country's schedule (factual hallucination). Another time it cites "Customs Circular 14/2023", which does not exist (fabricated source). Third, the retrieved text says duty 10% but the answer says 5% (contradiction with context, also called unfaithfulness).

**Amazon AI**: A shopping assistant claims a laptop has 32 GB RAM when the listing says 16 GB.

## 🟡 Real Example Hindi mein
**Tariff System**: User पूछता है "smart ring का HS code"। Model आत्मविश्वास से `8517.62.99` बताता है। Code असली दिखता है लेकिन उस देश की schedule में सही sub-heading नहीं है (factual hallucination)। दूसरी बार वह "Customs Circular 14/2023" cite करता है जो है ही नहीं (मनगढ़ंत source)। तीसरी बार retrieved text में duty 10% है पर जवाब में 5% (context से विरोधाभास, यानी unfaithfulness)।

**Amazon AI**: Shopping assistant कहता है laptop में 32 GB RAM है जबकि listing में 16 GB है।

---

## 💻 Code Example — Basic
```python
# Basic: label hallucination types with simple rules - pure Python
SOURCE = "Duty on cotton t-shirts under HS 6109.10 is 10 percent."  # trusted text


def classify(answer: str, source: str) -> str:
    """Very simple demo classifier for hallucination type."""
    if "circular" in answer.lower() and "circular" not in source.lower():
        return "fabricated_source"  # cites something not in the source
    if "10 percent" in source and "5 percent" in answer:
        return "contradiction"  # disagrees with the source
    if answer.strip() == "":
        return "empty"
    return "no_issue_found"  # not proof of truth, just no rule hit


tests = [
    "Duty is 5 percent.",
    "Per Customs Circular 14/2023 the duty is 10 percent.",
    "Duty is 10 percent.",
]
for t in tests:  # run each example
    print(t, "->", classify(t, SOURCE))
```

## 💻 Code Example — Advanced
```python
# Production style: measure hallucination rate on a test set with an async LLM judge
import asyncio  # async runtime
import json  # parse judge output
from dataclasses import dataclass  # result object
from typing import Literal  # label type

HType = Literal["none", "factual", "fabricated_source", "contradiction", "reasoning"]


@dataclass
class Case:
    question: str  # input
    context: str  # retrieved context
    answer: str  # model answer


async def judge(case: Case) -> HType:
    """Ask a cheap LLM to label the answer. Mocked offline when no API key."""
    import os  # check key

    if not os.getenv("OPENAI_API_KEY"):  # offline mock so the file runs anywhere
        return "contradiction" if "5 percent" in case.answer else "none"
    from openai import AsyncOpenAI  # openai>=1

    client = AsyncOpenAI()  # client
    prompt = (
        "Compare ANSWER with CONTEXT. Reply JSON {\"label\": one of "
        "none|factual|fabricated_source|contradiction|reasoning}.\n"
        f"CONTEXT: {case.context}\nANSWER: {case.answer}"
    )
    try:
        r = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,  # stable judging
            response_format={"type": "json_object"},  # force JSON
            messages=[{"role": "user", "content": prompt}],
            max_tokens=30,  # label is tiny
        )
        return json.loads(r.choices[0].message.content or "{}").get("label", "none")
    except Exception:  # judge failure should not crash the batch
        return "none"


async def main() -> None:
    ctx = "Duty on HS 6109.10 is 10 percent."
    cases = [Case("duty?", ctx, "5 percent"), Case("duty?", ctx, "10 percent")]
    labels = await asyncio.gather(*[judge(c) for c in cases])  # judge in parallel
    rate = sum(1 for x in labels if x != "none") / len(labels)  # hallucination rate
    print(labels, f"rate={rate:.0%}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Return a confidence/grounded flag with every answer so the UI can show a warning.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()


class Out(BaseModel):
    answer: str  # model text
    grounded: bool  # supported by retrieved context?
    warning: str | None = None  # shown in UI


@app.get("/answer", response_model=Out)
async def answer(q: str) -> Out:
    text = "Duty is 10 percent."  # LLM result here
    context = "Duty on HS 6109.10 is 10 percent."  # retrieved text
    grounded = "10 percent" in context and "10 percent" in text  # naive check
    return Out(answer=text, grounded=grounded,
               warning=None if grounded else "Unverified - check with a broker")
```

---

## 🔗 LangChain / LangGraph Connection
RAG chains reduce factual hallucination by injecting context. Add a "grounded?" node after generation in LangGraph, and loop back to retrieval if the answer is unsupported.

```python
from langchain_core.prompts import ChatPromptTemplate  # prompt builder

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer ONLY from the context. If missing, say 'I don't know'."),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])
# chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0) | StrOutputParser()
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Believing "temperature 0 means no hallucination"
✅ Correct: It only makes output stable, not true.

```python
# Wrong
llm = ChatOpenAI(temperature=0)  # "safe now"
# Right
llm = ChatOpenAI(temperature=0)  # plus grounding + verification
```

❌ Mistake 2: No "I don't know" path
✅ Correct: Allow and reward abstention.

```python
# Wrong prompt
"Always give a final HS code."
# Right prompt
"Give an HS code only if the context supports it; otherwise say 'insufficient information'."
```

---

## 🧠 Tricky Interview Question
**Q**: "The RAG answer is wrong even though the right chunk was retrieved. Is that hallucination?"

**Answer**: Yes, it is a faithfulness (intrinsic) hallucination: the model had the right context but ignored or misread it. Causes: too many chunks, the key chunk lost in the middle, a conflicting chunk, or a weak prompt. Fixes: fewer, reranked chunks, put the best chunk first or last, require quote-then-answer, and check faithfulness after generation.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is hallucination?
A1: Confident but false or unsupported LLM output.

Q2: [Easy] Give two causes.
A2: Missing knowledge (rare or new facts) and pressure to answer. Also high temperature and ambiguous prompts.

Q3: [Medium] Intrinsic vs extrinsic hallucination?
A3: Intrinsic contradicts the provided context. Extrinsic adds claims that cannot be verified from the context (may be true or false).

Q4: [Medium] Why do fabricated citations happen?
A4: The model learned the pattern of citations (author, year, number) and generates plausible ones without a lookup tool. Fix with retrieval-provided IDs and verification.

Q5: [Hard] How would you measure hallucination rate in production?
A5: Sample real traffic, label with a judge LLM plus human spot checks, report faithfulness per segment (language, product category), track over time, and tie releases to this metric. Use RAG metrics like faithfulness and answer relevance.

---

## 🔷 When to Use + When Not to Use
✅ Use this knowledge when:
- Designing evaluation and guardrails
- Choosing between RAG, tools and fine-tuning

❌ Do not assume:
- That a bigger model removes the problem
- That users will notice errors themselves

---

## 📊 Visual Diagram
```
                 Hallucination
      ┌────────────┬─────────────┬──────────────┐
   Factual     Fabricated    Contradicts     Reasoning
  (wrong fact)  (fake cite)   (context)      (math/logic)
      │             │             │              │
 stale/rare     no lookup     long/noisy     no tool/
  knowledge      tool          context        steps
```

---

## 💰 Cost Impact
Hallucinations cost money indirectly: retries, human review, support tickets, and penalties. A faithfulness judge on gpt-4o-mini with 800 input tokens is about $0.00015 per check; 1M checks cost about $150. Sample 5% of traffic to cut this to about $7.50. Cheaper than reviewing every answer by hand. Reduce cost further by shortening context and caching verdicts.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hallucination | Confident false output | आत्मविश्वासी गलत जवाब |
| Faithfulness | Answer matches context | जवाब का context से मेल |
| Intrinsic | Contradicts given text | दिए text के विरुद्ध |
| Extrinsic | Unverifiable extra claim | बिना प्रमाण अतिरिक्त दावा |
| Abstention | Saying "I don't know" | "पता नहीं" कहना |
| Snowballing | One error leads to more | एक गलती से और गलतियाँ |

---

## ⚡ 3-Line Summary
English: Hallucination is confident but unsupported output, caused by next-token prediction, missing knowledge and weak context. Main types are factual, fabricated source, contradiction and reasoning errors. Name the type first, then choose the fix.
Hindi: Hallucination आत्मविश्वासी लेकिन unsupported output है, जिसका कारण next-token prediction, missing knowledge और कमज़ोर context है। मुख्य types हैं factual, मनगढ़ंत source, contradiction और reasoning errors। पहले type पहचानो, फिर fix चुनो।

---

## ➡️ Next Topic
**463. Hallucination Detection** - once you know the types, learn how to catch them automatically.
