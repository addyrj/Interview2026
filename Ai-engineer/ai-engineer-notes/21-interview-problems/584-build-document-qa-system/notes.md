---

# 584. Build Document Q&A System
# हिंदी में: Document Q&A System बनाना

---

## 🔵 Simple Definition (English)
A document Q&A system answers questions using only the content of your documents and shows where the answer came from. It chunks documents, retrieves the most relevant chunks for a question, and asks the LLM to answer from those chunks with citations, or to say "not found".

## 🔵 सरल परिभाषा (Hindi)
Document Q&A system सिर्फ आपके documents के content से सवालों के जवाब देता है और बताता है जवाब कहाँ से आया। Documents को chunks में बाँटता है, सवाल के लिए सबसे relevant chunks लाता है, और LLM से citations के साथ जवाब दिलवाता है, या "नहीं मिला" कहलवाता है।

---

## 🔴 Problem it Solves
LLMs do not know your private documents, and they guess when unsure. Pasting whole documents does not fit context windows and is costly. Document Q&A grounds answers in evidence and makes them verifiable.

## 🔴 यह क्यों बना? (Hindi)
LLM आपके private documents नहीं जानता और अनिश्चित होने पर अंदाज़ा लगाता है। पूरा document paste करना context में नहीं समाता और महँगा है। Document Q&A जवाब को evidence पर टिकाता है और verifiable बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Load document and split into chunks (paragraph or ~300-500 tokens, small overlap)
Step 2 → Index chunks (embeddings + vector DB, plus keywords if hybrid)
Step 3 → Question arrives; retrieve top-k chunks
Step 4 → If best score is below a threshold, answer "not found"
Step 5 → Prompt: "Answer only from the context; cite chunk ids"
Step 6 → LLM answers; validate that cited ids exist
Step 7 → Return answer + citations
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Document load करके chunks में बाँटो (paragraph या ~300-500 tokens, थोड़ा overlap)
Step 2 → Chunks index करो (embeddings + vector DB, चाहें तो keywords भी)
Step 3 → सवाल आने पर top-k chunks निकालो
Step 4 → Best score threshold से कम हो तो "नहीं मिला" कहो
Step 5 → Prompt: "सिर्फ context से जवाब दो; chunk ids cite करो"
Step 6 → LLM जवाब दे; cited ids मौजूद हैं या नहीं जाँचो
Step 7 → Answer + citations लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs broker asks "What is the duty on smartphones?" The system retrieves Section 1 and answers with citation [Section 1]. Asked "Who won the cricket world cup?", the score is below the threshold so it refuses, which `main.py` demonstrates. **Amazon-style**: seller policy Q&A with links to the policy clause. **Zomato-style**: restaurant onboarding guide Q&A.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs broker पूछता है "Smartphones पर duty?" System Section 1 निकालकर citation के साथ जवाब देता है। "क्रिकेट विश्व कप किसने जीता?" पर score threshold से कम है, इसलिए मना कर देता है (`main.py` में दिखता है)। **Amazon**: seller policy Q&A, clause के link के साथ। **Zomato**: restaurant onboarding guide Q&A।

---

## 💻 Code Example — Basic
Full solution: `main.py` (paragraph chunking, overlap-score retrieval, refusal, citations).

```python
import re  # tokenising

chunks = ["Smartphones: HS 8517.13, duty 20 percent.", "Laptops: HS 8471.30, duty free."]  # tiny corpus

def words(t: str) -> set[str]:  # content words
    return set(re.findall(r"[a-z0-9.]+", t.lower()))  # lowercase tokens

def ask(q: str) -> str:  # retrieve + answer
    scores = [(len(words(q) & words(c)), i) for i, c in enumerate(chunks)]  # overlap per chunk
    best, idx = max(scores)  # best chunk
    return f"{chunks[idx]} [chunk {idx}]" if best >= 2 else "Not found in documents."  # refuse if weak

print(ask("duty on smartphones"))  # cites chunk 0
print(ask("cricket champion"))  # refuses
```

## 💻 Code Example — Advanced
`main.py` returns `{answer, citations}` and refuses below `min_score`. Production version with a real LLM and citation validation (illustrative):

```python
import json
from typing import Any

PROMPT = (  # grounding prompt
    "Answer ONLY from the context. If missing, reply exactly NOT_FOUND. "
    "Return JSON: {\"answer\": str, \"cited_ids\": [int]}.\n\nContext:\n{ctx}\n\nQuestion: {q}"
)

async def answer(client: Any, retrieved: dict[int, str], q: str) -> dict:  # async answerer
    ctx = "\n".join(f"[{i}] {t}" for i, t in retrieved.items())  # label chunks with ids
    resp = await client.chat.completions.create(  # LLM call
        model="gpt-4o-mini", temperature=0, max_tokens=300,  # deterministic, bounded
        response_format={"type": "json_object"},  # force JSON
        messages=[{"role": "user", "content": PROMPT.replace("{ctx}", ctx).replace("{q}", q)}],  # fill prompt
    )
    data = json.loads(resp.choices[0].message.content)  # parse (handle JSONDecodeError in prod)
    bad = [c for c in data.get("cited_ids", []) if c not in retrieved]  # hallucinated citations
    if bad:  # reject fake sources
        return {"answer": "NOT_FOUND", "cited_ids": []}
    return data  # grounded answer
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel, Field
from main import aanswer  # from main.py

app = FastAPI()  # app

class Q(BaseModel):  # request
    question: str = Field(min_length=3, max_length=500)  # user question

@app.post("/qa")  # route
async def qa(body: Q) -> dict:  # handler
    return await aanswer(body.question)  # {"answer":..., "citations":[...]}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain provides loaders, `RecursiveCharacterTextSplitter`, vector stores and retrievers. Compose with LCEL: retriever, prompt, model, parser. In LangGraph add nodes for query rewriting, retrieval grading and retry when context is weak (corrective RAG).

```python
# Illustrative LCEL chain (pip install langchain langchain-openai)
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# chain = {"context": retriever, "question": lambda x: x} | ChatPromptTemplate.from_template(
#     "Answer from context only.\n{context}\nQ: {question}") | llm | StrOutputParser()
print("retriever -> prompt -> llm -> parser")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No refusal path
✅ Correct: Threshold and a "not found" answer.

```python
best_score = 0.05
# Wrong: always answer from top chunk
answer = "top chunk text"
# Right
answer = "Not found" if best_score < 0.2 else "top chunk text"
print(answer)
```

❌ Mistake 2: Chunks that split a table or a sentence
✅ Correct: Chunk by structure (headings, paragraphs) with overlap.

```python
text = "A" * 1000
# Wrong: blind cut can split mid-sentence
bad = [text[i:i + 300] for i in range(0, len(text), 300)]
# Right: split on paragraphs, then merge to size
good = [p for p in "p1\n\np2".split("\n\n")]
print(len(bad), good)
```

---

## 🧠 Tricky Interview Question
**Q**: "Users say the answer is right but cites the wrong section. Retrieval metrics look fine. What is happening?"

**Answer**: The model ignores the provided ids or mixes chunks. Fixes: ask for quote-level citations (exact supporting sentence), validate that each cited quote appears in the cited chunk, label chunks with stable ids, reduce k to cut distractors, and add an automated citation-accuracy metric to evaluation.

---

## ⚫ Interview Questions + Answers

Q1: Why chunk documents? (Easy)
A1: Chunks fit context limits and let retrieval pick only relevant parts, saving cost and improving focus.

Q2: What does "grounded" mean? (Easy)
A2: The answer is supported by retrieved text, not model memory.

Q3: How to pick chunk size? (Medium)
A3: Balance precision (small) and context (large); start around 300-500 tokens with ~10-15% overlap, then tune on a golden set.

Q4: How do you reduce hallucinated answers? (Medium)
A4: Strict prompt, temperature 0, relevance threshold, refusal option, citation validation, and evaluation for faithfulness.

Q5: How do you keep answers fresh when documents change? (Hard)
A5: Version documents, re-embed only changed chunks (content hashes), keep metadata (version, date), soft-delete old chunks, schedule or event-trigger ingestion, and filter retrieval by latest version.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Answers must come from your private, changing documents
- You need citations for trust or compliance

❌ Avoid when:
- Corpus is tiny (put it in the prompt)
- Questions need reasoning across the whole corpus (consider other designs)

---

## 📊 Visual Diagram
```
 Docs ─► chunk ─► embed ─► index
                              │
 Question ─► retrieve top-k ◄─┘
                │ score < threshold ──► "not found"
                ▼
       prompt (context + rules) ─► LLM ─► answer + citations
```

---

## 💰 Cost Impact
Input tokens = system + k chunks + question. Example (illustrative): 4 chunks x 400 tokens + 200 overhead is about 1,800 input tokens per question. Optimise: smaller k with reranking, compress chunks, cache frequent questions, `max_tokens` limits, cheap model for simple lookups, and embed once at ingest (not per query).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Chunk | Piece of document | Document का टुकड़ा |
| Retrieval | Finding relevant chunks | Relevant chunks ढूँढना |
| Grounding | Answer based on evidence | Evidence पर आधारित |
| Citation | Source reference | स्रोत संदर्भ |
| Threshold | Minimum relevance | न्यूनतम relevance |
| Faithfulness | Answer matches context | Answer context से मेल खाए |

---

## ⚡ 3-Line Summary
English: Chunk, retrieve, answer only from context, and cite. Refuse when evidence is weak. Validate citations and measure faithfulness.
Hindi: Chunk करो, retrieve करो, सिर्फ context से जवाब दो और cite करो। Evidence कमजोर हो तो मना करो। Citations validate करो और faithfulness मापो।

---

## ➡️ Next Topic
**585. Build PDF Chat App** — the same idea but starting from PDFs, with page numbers.
