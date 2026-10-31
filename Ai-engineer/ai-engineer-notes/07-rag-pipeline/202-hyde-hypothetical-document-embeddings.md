---

# 202. HyDE — Hypothetical Document Embeddings
# हिंदी में: HyDE — काल्पनिक Document Embeddings

---

## 🔵 Simple Definition (English)
HyDE asks an LLM to write a **hypothetical answer** to the question (it may contain mistakes), embeds that fake answer, and uses its vector to search. A fake answer looks like a real document, so its embedding is closer to real answer chunks than the short question's embedding is.

## 🔵 सरल परिभाषा (Hindi)
HyDE में LLM सवाल का एक **काल्पनिक जवाब** लिखता है (उसमें गलतियाँ हो सकती हैं), उस नकली जवाब को embed करके उसके vector से search होता है। नकली जवाब असली document जैसा दिखता है, इसलिए उसका embedding छोटे सवाल के embedding से असली answer chunks के ज़्यादा पास होता है।

---

## 🔴 Problem it Solves
Questions and answers live in different "shapes": a question is short and asks, a document is long and states. Embedding models trained on documents place a short question and its answer chunk further apart than two documents on the same topic. HyDE moves the query into "document space". It also helps zero-shot cases where no labeled retrieval data exists.

## 🔴 यह क्यों बना? (Hindi)
सवाल और जवाब की "शक्ल" अलग होती है: सवाल छोटा और पूछने वाला, document लंबा और बताने वाला। Documents पर trained embedding models एक छोटे सवाल और उसके answer chunk को, एक ही topic के दो documents से ज़्यादा दूर रखते हैं। HyDE query को "document space" में ले जाता है। यह zero-shot स्थितियों में भी मदद करता है जहाँ labeled retrieval data नहीं है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → User asks: "Is there duty on imported wireless earbuds?"
Step 2 → LLM writes a short hypothetical passage answering it (no retrieval, may be wrong)
Step 3 → Embed the hypothetical passage (optionally average with the query embedding)
Step 4 → Vector search with that embedding -> real chunks
Step 5 → Discard the fake passage; give ONLY real retrieved chunks to the generator
Step 6 → Generate the final answer from real context with citations
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → User: "Imported wireless earbuds पर duty लगती है?"
Step 2 → LLM एक छोटा काल्पनिक passage लिखता है (बिना retrieval, गलत हो सकता है)
Step 3 → उस passage को embed करो (चाहें तो query embedding के साथ average)
Step 4 → उस embedding से vector search -> असली chunks
Step 5 → नकली passage फेंक दो; generator को सिर्फ असली chunks दो
Step 6 → असली context और citations से final जवाब बनाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: Query "Bluetooth in-ear gadget import tax". HyDE passage: "Wireless earphones and headsets fall under HS heading 8518. Import duty is typically a small percentage of the value." Even with a wrong rate, it contains the words and style of tariff text (heading, HS, duty), so the embedding lands near the real heading 8518 chunk.
**Zomato AI**: "something to cure a hangover" -> hypothetical menu description "spicy broth with noodles, lemon, ginger..." retrieves matching dishes.

## 🟡 Real Example Hindi mein
**Tariff System**: Query "Bluetooth in-ear gadget import tax"। HyDE passage: "Wireless earphones and headsets HS heading 8518 में आते हैं। Import duty आमतौर पर value का छोटा प्रतिशत होती है।" Rate गलत हो तब भी इसमें tariff text के शब्द और शैली है (heading, HS, duty), इसलिए embedding असली 8518 heading chunk के पास पहुँचती है।
**Zomato AI**: "hangover उतारने के लिए कुछ" -> काल्पनिक menu description "तीखा शोरबा, noodles, नींबू, अदरक..." मिलते-जुलते dishes ढूँढती है।

---

## 💻 Code Example — Basic
```python
# HyDE flow with stub LLM and a toy embedding (pure Python): question vs hypothetical passage
import math
import re
from collections import Counter
from typing import Dict, List

DOCS: Dict[str, str] = {
    "d1": "Heading 8518 covers wireless earphones and headsets. Duty on HS 8518.30 is 0 percent.",
    "d2": "Heading 6403 covers leather footwear. Duty on HS 6403.99 is 20 percent.",
    "d3": "Heading 8517 covers smartphones and telephone sets. Duty on HS 8517.13 is 0 percent.",
}

def vec(text: str) -> Counter:
    return Counter(re.findall(r"\w+", text.lower()))  # toy bag-of-words "embedding"

def cos(a: Counter, b: Counter) -> float:
    dot = sum(a[w] * b[w] for w in a)  # overlap
    den = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return dot / den if den else 0.0

def hypothetical_answer(question: str) -> str:
    """Stand-in for an LLM call that writes a plausible (possibly wrong) answer passage."""
    return "Wireless earphones and headsets fall under heading 8518. The import duty is a small percent."

def search(text: str, k: int = 2) -> List[str]:
    q = vec(text)
    return sorted(DOCS, key=lambda d: -cos(q, vec(DOCS[d])))[:k]

if __name__ == "__main__":
    question = "bluetooth in ear gadget import tax"
    print("question  ->", search(question))  # weak: no shared words with d1
    fake = hypothetical_answer(question)  # step 2
    print("hyde      ->", search(fake))  # d1 first: fake answer shares document-style words
```

## 💻 Code Example — Advanced
```python
# Async HyDE retriever: multiple hypotheses, embedding averaging, safeguards, timeouts, fallback
import asyncio
import logging
import math
from typing import Awaitable, Callable, Sequence

logger = logging.getLogger("hyde")  # logger
LLM = Callable[[str], Awaitable[str]]  # prompt -> text
Embed = Callable[[Sequence[str]], Awaitable[list[list[float]]]]  # texts -> vectors
VectorSearch = Callable[[list[float], int], Awaitable[list[str]]]  # vector, k -> chunk ids

PROMPT = ("Write a short passage (max 80 words) in the style of an official customs tariff document "
          "that answers the question. If unsure, still write a plausible passage.\nQuestion: {q}")

def mean_vec(vs: list[list[float]]) -> list[float]:
    dims = len(vs[0])  # vector size
    avg = [sum(v[i] for v in vs) / len(vs) for i in range(dims)]  # element-wise mean
    n = math.sqrt(sum(x * x for x in avg)) or 1.0  # normalise
    return [x / n for x in avg]

class HyDERetriever:
    def __init__(self, llm: LLM, embed: Embed, search: VectorSearch, n_hypotheses: int = 2, timeout_s: float = 6.0) -> None:
        self.llm, self.embed, self.search = llm, embed, search  # deps
        self.n, self.timeout_s = n_hypotheses, timeout_s  # config

    async def _hypothesis(self, q: str) -> str | None:
        try:
            text = await asyncio.wait_for(self.llm(PROMPT.format(q=q)), self.timeout_s)  # bounded
            return text.strip() or None
        except Exception as exc:  # LLM down/slow
            logger.warning("hyde generation failed: %r", exc); return None

    async def retrieve(self, question: str, k: int = 5) -> list[str]:
        hyps = [h for h in await asyncio.gather(*(self._hypothesis(question) for _ in range(self.n))) if h]  # parallel
        texts = [question, *hyps]  # always include the real question
        vecs = await self.embed(texts)  # embed all in one batch
        q_vec = mean_vec(vecs)  # average: question + hypothetical docs (paper's approach averages hypotheses)
        return await self.search(q_vec, k)  # real chunks only; hypotheses are discarded

async def llm_stub(p: str) -> str: return "Wireless earphones fall under HS heading 8518, duty is small."
async def embed_stub(ts: Sequence[str]) -> list[list[float]]: return [[float("8518" in t or "earphones" in t), 0.2, 0.1] for t in ts]
async def search_stub(v: list[float], k: int) -> list[str]: return ["d1"] if v[0] > 0.5 else ["d9"]

if __name__ == "__main__":
    print(asyncio.run(HyDERetriever(llm_stub, embed_stub, search_stub).retrieve("bluetooth in ear gadget tax")))
```

---

## 🟠 FastAPI Integration
HyDE is a pre-retrieval step inside the endpoint. Add a feature flag so you can compare with plain retrieval, and never return the hypothetical text as an answer (it is unverified).

```python
# FastAPI route with a HyDE on/off switch
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()  # app
hyde = HyDERetriever(real_llm, real_embed, real_vector_search)  # build once with real clients

class Q(BaseModel):
    question: str
    use_hyde: bool = True

@app.post("/retrieve")
async def retrieve(q: Q) -> dict:
    if q.use_hyde:
        ids = await hyde.retrieve(q.question, k=5)  # HyDE path (adds 1 LLM call)
    else:
        ids = await real_vector_search((await real_embed([q.question]))[0], 5)  # baseline path
    return {"chunk_ids": ids, "used_hyde": q.use_hyde}
```

---

## 🔗 LangChain / LangGraph Connection
`HypotheticalDocumentEmbedder` in `langchain.chains` wraps a base embedding model: `embed_query` first asks the LLM for a hypothetical document, then embeds it. Use `from_llm(llm, base_embeddings, prompt_key="web_search")`. You can also compose it manually in LCEL.

```python
# Manual HyDE in LCEL (needs langchain-core, langchain-openai, OPENAI_API_KEY)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

hyde_prompt = ChatPromptTemplate.from_template("Write a short tariff-document passage answering: {question}")  # fake doc prompt
hyde_chain = hyde_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0.3) | StrOutputParser()  # question -> passage
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")  # embedder

# passage = hyde_chain.invoke({"question": "tax on imported earbuds"})       # step 1
# vector = embeddings.embed_query(passage)                                   # step 2
# docs = vectorstore.similarity_search_by_vector(vector, k=5)                # step 3: real chunks
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Showing or citing the hypothetical passage as if it were the answer.
✅ Correct: Use it only for retrieval; answer from real chunks.

```python
# Wrong
return hypothetical_answer(question)
# Right
chunks = search(embed(hypothetical_answer(question))); return generate(question, chunks)
```

❌ Mistake 2: Using HyDE for exact-identifier queries.
✅ Correct: Skip HyDE when the query contains codes or names; the LLM may invent wrong codes that mislead retrieval.

```python
# Wrong
hyde_search("what is HS 8518.30?")      # LLM may invent "8518.40" in the passage
# Right
results = keyword_search(q) if looks_like_code(q) else hyde_search(q)
```

---

## 🧠 Tricky Interview Question
**Q**: "HyDE hallucinates facts in the hypothetical passage. Why doesn't that ruin the final answer?"

**Answer**: The hypothetical passage is never shown to the user or used as evidence. It only serves as a search key: its role is to carry the *style and vocabulary* of the target document, which brings the embedding near real chunks. The final answer is generated from real retrieved chunks. The risk exists only when the hallucinated details point retrieval to wrong topics (e.g., an invented code or wrong domain), which is why it fails on niche domains the LLM knows nothing about, and why mixing the original question embedding in (averaging) is a good guard.

---

## ⚫ Interview Questions + Answers

Q1: What does HyDE stand for?
A1: Hypothetical Document Embeddings (Gao et al., 2022).

Q2: Why does a fake answer retrieve better than the question?
A2: Embeddings of statements are closer to document passages than embeddings of short questions are.

Q3: What is HyDE's main cost?
A3: One extra LLM generation (about 100 output tokens) and its latency before retrieval.

Q4: When does HyDE hurt?
A4: Exact-term queries, highly specialised domains where the LLM lacks knowledge, very short factual lookups, and tight latency budgets.

Q5: How would you evaluate and safeguard HyDE in production?
A5: A/B test on a labeled query set (recall@k, answer correctness) per query segment; average the query and hypothesis embeddings; use a router to skip code-like queries; cap hypothesis length; cache by query; fall back to plain retrieval on timeouts; monitor cost and latency.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Short, abstract or conversational queries vs long formal documents
- No labeled data to fine-tune the retriever
- Domain is one the LLM knows reasonably

❌ Avoid when:
- Queries have exact codes/names
- Domain is niche/private and the LLM would guess wildly
- Latency or cost per query is critical

---

## 📊 Visual Diagram
```
 Question ──────────────► embed ──► far from answer chunk  ✗
     │
     └─► LLM writes fake answer ─► embed ──► near real answer chunk ✓
                                               │ vector search
                                               ▼
                                    real chunks (fake text discarded)
                                               ▼
                                   Generator -> grounded final answer
```

---

## 💰 Cost Impact
One extra generation: ~50 prompt + ~100 output tokens on gpt-4o-mini = about 0.00007 USD per query, plus 100-700 ms latency. With n=2 hypotheses double the output. Retrieval embedding cost is negligible.
Optimize: one hypothesis only, `max_tokens=100`, small model, cache, apply HyDE only to vague natural-language queries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HyDE | Search with a fake answer's embedding | नकली जवाब के embedding से search |
| Hypothetical document | LLM-written fake passage | LLM का लिखा नकली passage |
| Zero-shot retrieval | No labeled data needed | बिना labeled data के retrieval |
| Query-document gap | Questions look unlike documents | सवाल और document की शक्ल का अंतर |
| Embedding averaging | Mean of several vectors | कई vectors का औसत |
| Router | Chooses which method to use | तरीका चुनने वाला |

---

## ⚡ 3-Line Summary
English: HyDE embeds an LLM-written hypothetical answer instead of the question to find real chunks.
It bridges the question-document style gap, costs one extra LLM call, and fails on exact codes.
Never show the fake passage; answer only from retrieved real chunks.
Hindi: HyDE सवाल की जगह LLM के लिखे काल्पनिक जवाब को embed करके असली chunks ढूँढता है।
यह सवाल-document की शैली का अंतर पाटता है, एक extra LLM call लेता है, और exact codes पर fail होता है।
नकली passage कभी मत दिखाओ; सिर्फ असली retrieved chunks से जवाब दो।

---

## ➡️ Next Topic
**203. Step-Back Prompting**: ask a broader question first to retrieve background, then answer the specific one.
