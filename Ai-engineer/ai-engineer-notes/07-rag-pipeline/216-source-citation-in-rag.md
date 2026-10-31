---

# 216. Source Citation in RAG
# हिंदी में: RAG में Source Citation

---

## 🔵 Simple Definition (English)
Source citation means every claim in the RAG answer points to the chunk (document, page, link) it came from. Users can verify the claim, and your system can check that the claim is really supported.

## 🔵 सरल परिभाषा (Hindi)
Source citation का मतलब है कि RAG answer का हर claim उस chunk (document, page, link) की ओर इशारा करे जहाँ से आया। User claim verify कर सकता है और आपका system जाँच सकता है कि claim सच में supported है।

---

## 🔴 Problem it Solves
Without citations users must trust the model blindly. In tariff, legal, medical or finance use, a wrong answer with no source is dangerous and unauditable. Citations build trust, enable audits, and give a way to detect hallucinations (a citation that does not support the claim).

## 🔴 यह क्यों बना? (Hindi)
Citations के बिना users को model पर आँख बंद करके भरोसा करना पड़ता है। Tariff, legal, medical या finance में source के बिना गलत answer खतरनाक और audit-अयोग्य है। Citations भरोसा बनाते हैं, audit संभव करते हैं और hallucination पकड़ने का रास्ता देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → At ingestion store metadata per chunk: doc_id, title, page, url, section
Step 2 → At prompt time label each chunk with a short id: [S1], [S2] ...
Step 3 → Instruct: "cite every claim as [S#]; do not cite anything not provided"
Step 4 → LLM returns answer text with markers (or structured claims + source ids)
Step 5 → Parse markers; validate each id exists in the provided set
Step 6 → Map ids back to metadata (title, page, url) for display
Step 7 → Optional: verify claim <-> chunk support (NLI or LLM judge)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Ingestion पर हर chunk का metadata रखो: doc_id, title, page, url, section
Step 2 → Prompt में हर chunk को छोटा id दो: [S1], [S2] ...
Step 3 → निर्देश: "हर claim [S#] से cite करो; जो दिया नहीं उसे cite मत करो"
Step 4 → LLM markers वाला answer (या structured claims + source ids) देता है
Step 5 → Markers parse करो; हर id दिए गए set में है या नहीं देखो
Step 6 → ids को metadata (title, page, url) से map करके दिखाओ
Step 7 → चाहो तो claim <-> chunk support verify करो (NLI या LLM judge)
```

---

## 🟡 Real World Example
**Tariff Classification System**: Answer: "Smartphones fall under HS 8517.13 [S1]. The basic duty is 20 percent [S1]. Refurbished units need a licence [S2]." The UI shows S1 = "Customs Tariff 2024, page 412" and S2 = "DGFT Notification 12/2023". Officers can click to open the exact page. **Zomato**: "Refund within 7 days [Policy v3, section 4]". **Amazon**: "Battery lasts 2 days [Review by Ravi, 5 stars]".

## 🟡 Real Example Hindi mein
**Tariff System**: Answer: "Smartphones HS 8517.13 में आते हैं [S1]। Basic duty 20 percent है [S1]। Refurbished units को licence चाहिए [S2]।" UI में S1 = "Customs Tariff 2024, page 412" और S2 = "DGFT Notification 12/2023" दिखता है। Officer click करके सही page खोल सकता है। **Zomato**: "7 दिन में refund [Policy v3, section 4]"। **Amazon**: "Battery 2 दिन चलती है [Ravi का review]"।

---

## 💻 Code Example — Basic
```python
# Pure Python: label chunks, parse [S#] markers, validate and expand to metadata.
import re  # find markers
from typing import Dict, List  # type hints

CHUNKS: List[Dict[str, str]] = [  # retrieved chunks with metadata
    {"text": "Smartphones HS 8517.13 duty 20 percent.", "title": "Customs Tariff 2024", "page": "412"},
    {"text": "Refurbished phones need an import licence.", "title": "DGFT Notification 12/2023", "page": "3"},
]

# What an LLM might return (hard-coded for the offline demo):
ANSWER: str = "Smartphones are HS 8517.13 [S1] with 20 percent duty [S1]. Refurbished ones need a licence [S2] [S9]."


def extract_ids(answer: str) -> List[str]:
    """Return unique citation ids in order of appearance."""
    seen: List[str] = []  # ordered unique ids
    for m in re.findall(r"\[(S\d+)\]", answer):  # each [S#]
        if m not in seen:  # de-duplicate
            seen.append(m)  # add
    return seen  # list of ids


def resolve(ids: List[str], chunks: List[Dict[str, str]]) -> Dict[str, List]:
    """Split ids into valid (with metadata) and invalid (hallucinated)."""
    valid: List[Dict[str, str]] = []  # good citations
    invalid: List[str] = []  # fake citations
    for cid in ids:  # check each
        idx = int(cid[1:]) - 1  # S1 -> index 0
        if 0 <= idx < len(chunks):  # in range
            valid.append({"id": cid, "title": chunks[idx]["title"], "page": chunks[idx]["page"]})  # real
        else:  # out of range
            invalid.append(cid)  # fake
    return {"valid": valid, "invalid": invalid}  # report


if __name__ == "__main__":
    ids = extract_ids(ANSWER)  # parse
    print(resolve(ids, CHUNKS))  # S9 should be flagged invalid
```

## 💻 Code Example — Advanced
```python
# Production: structured claims with citations, validation, and a support check. Async.
import logging  # logs
from typing import List  # typing

from openai import AsyncOpenAI  # openai>=1
from pydantic import BaseModel, Field, model_validator  # pydantic v2

logger = logging.getLogger("citations")  # logger
client = AsyncOpenAI()  # env key


class Claim(BaseModel):
    text: str  # one factual statement
    source_ids: List[str] = Field(min_length=1)  # at least one citation per claim
    quote: str = ""  # exact supporting words from the chunk


class CitedAnswer(BaseModel):
    claims: List[Claim]  # answer split into claims

    @model_validator(mode="after")
    def non_empty(self) -> "CitedAnswer":
        if not self.claims:  # must have at least one claim
            raise ValueError("no claims")  # reject
        return self


def verify(answer: CitedAnswer, chunks: dict[str, str]) -> CitedAnswer:
    """Keep only claims whose ids exist and whose quote really occurs in the cited chunk."""
    good: list[Claim] = []  # verified claims
    for c in answer.claims:  # each claim
        ids_ok = all(i in chunks for i in c.source_ids)  # ids real
        quote_ok = (not c.quote) or any(c.quote in chunks[i] for i in c.source_ids if i in chunks)  # quote real
        if ids_ok and quote_ok:  # both true
            good.append(c)  # keep
        else:
            logger.warning("dropped unsupported claim: %s", c.text)  # log
    return CitedAnswer(claims=good) if good else CitedAnswer(claims=[Claim(text="NOT_FOUND", source_ids=["none"])])  # safe


async def answer_with_citations(question: str, chunks: dict[str, str]) -> CitedAnswer:
    ctx = "\n".join(f"[{k}] {v}" for k, v in chunks.items())  # labelled context
    try:  # API call
        resp = await client.beta.chat.completions.parse(
            model="gpt-4o-mini", temperature=0, max_tokens=500, response_format=CitedAnswer,
            messages=[
                {"role": "system", "content": "Answer as separate claims. Each claim needs source_ids from the context and a short exact quote."},
                {"role": "user", "content": f"<context>\n{ctx}\n</context>\nQuestion: {question}"},
            ],
        )
        parsed = resp.choices[0].message.parsed  # typed
        return verify(parsed, chunks) if parsed else CitedAnswer(claims=[Claim(text="NOT_FOUND", source_ids=["none"])])
    except Exception as exc:  # any failure
        logger.error("citation answer failed: %s", exc)  # log
        return CitedAnswer(claims=[Claim(text="Service error", source_ids=["none"])])  # safe default
```

---

## 🟠 FastAPI Integration
Return the answer plus a `sources` array with titles and page links for the UI to render as footnotes.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()  # app
SOURCE_DB = {"S1": {"title": "Customs Tariff 2024", "page": 412, "url": "https://example.org/tariff#p412"}}  # metadata store


class Req(BaseModel):
    question: str  # question


@app.post("/ask")  # route
async def ask(req: Req) -> dict:
    chunks = {"S1": "Smartphones HS 8517.13 duty 20 percent."}  # retrieved
    ans = await answer_with_citations(req.question, chunks)  # cited answer
    used = {i for c in ans.claims for i in c.source_ids}  # ids used
    return {"claims": [c.model_dump() for c in ans.claims], "sources": [SOURCE_DB[i] for i in used if i in SOURCE_DB]}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain: `create_stuff_documents_chain`/LCEL with a prompt that labels docs by `metadata`. `with_structured_output` returns claims with ids. Anthropic's API also has a native Citations feature when you pass documents as content blocks, and responses include cited spans.

```python
from langchain_core.documents import Document  # doc type


def format_docs(docs: list[Document]) -> str:
    """Label docs with ids and show metadata for the model."""
    return "\n".join(f"[S{i}] ({d.metadata.get('source', '?')} p.{d.metadata.get('page', '?')}) {d.page_content}"
                     for i, d in enumerate(docs, 1))  # one line per doc


# chain = {"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm
# LangGraph: keep `state["docs"]` so the final node can map [S#] back to metadata.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Asking the model to invent a URL or page number
✅ Correct: Give ids only; map to metadata in your code.

```python
# Wrong: model writes "see https://..." (often fake)
prompt = "Cite the URL of the source."

# Right: model writes [S1]; code maps to a real URL
url = SOURCE_DB["S1"]["url"]
```

❌ Mistake 2: Showing citations without verifying them
✅ Correct: Validate ids and quotes.

```python
# Wrong: show any [S#] the model wrote
print(answer)

# Right: drop ids not in the provided set
valid = [i for i in ids if i in chunks]
```

---

## 🧠 Tricky Interview Question
**Q**: "All your citations point to real chunk ids, yet auditors find answers that the cited chunk does not support. What now?"

**Answer**: Valid ids do not prove support. This is citation inaccuracy. Add a claim-to-chunk support check: require an exact supporting quote that you verify by string match, or run an NLI model / LLM judge to test entailment per claim, and drop or flag unsupported claims. Use finer chunks so a citation is precise, and measure citation precision and recall on a labelled set.

---

## ⚫ Interview Questions + Answers

Q1: Why add citations to RAG?
A1: Trust, verifiability, auditability, and hallucination detection.

Q2: Where does citation metadata come from?
A2: Ingestion: store title, page, URL, section with each chunk and carry it through retrieval.

Q3: Why use short ids like [S1] instead of URLs?
A3: Fewer tokens, no fake URLs, easy validation, and your code controls the final links.

Q4: What are citation precision and recall?
A4: Precision: share of citations that truly support their claim. Recall: share of claims that have a correct citation.

Q5: How would you design citations for multi-step agentic RAG where many retrieval rounds happen?
A5: Assign globally unique chunk ids (doc_id + chunk index + version) kept in state across steps, renumber for display only at the end, store every retrieved chunk in a trace store, require each final claim to cite ids from that store, verify quotes against stored text, and keep the version/hash of the document so citations remain valid after re-indexing.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Legal, tariff, finance, medical, enterprise search
- Users or auditors need to verify
- You want automatic hallucination checks

❌ Avoid when:
- Casual chat with no sources
- Sources are confidential and cannot be exposed (show internal ids only)

---

## 📊 Visual Diagram
```
 Chunks + metadata        Prompt                     LLM output
 ────────────────         ──────                     ──────────
 S1: Tariff p412   ──►  [S1] text...  ──►  "HS 8517.13 [S1]; licence [S2]"
 S2: DGFT notif.   ──►  [S2] text...                      │
                                                          ▼ validate ids + quotes
                                          ┌───────────────────────────────┐
                                          │ footnotes: S1 → Tariff p.412  │
                                          │            S2 → DGFT 12/2023  │
                                          └───────────────────────────────┘
```

---

## 💰 Cost Impact
- Labels add few tokens (about 3-5 per chunk). Structured claims with quotes add output tokens (about 50-150 more per answer).
- Verification by string match is free; LLM-judge verification doubles the cost for the checked sample.
- Optimise: short ids, short quotes (max 15 words), verify with string match or a small NLI model, judge only a sampled 5-10 percent, drop quotes in low-risk flows.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Citation | Pointer to the source | Source की ओर इशारा |
| Provenance | Origin of information | जानकारी की उत्पत्ति |
| Entailment | Source supports the claim | Source claim का समर्थन करे |
| Metadata | Title, page, URL | Title, page, URL जैसी जानकारी |
| Citation precision | Correct citations share | सही citations का अनुपात |

---

## ⚡ 3-Line Summary
English: Citations tie each claim to a source chunk so users can verify. Label chunks with short ids, parse and validate the ids, and map them to metadata in code. Verify support, not just existence.
Hindi: Citations हर claim को source chunk से जोड़ते हैं ताकि users verify कर सकें। Chunks को छोटे ids दो, ids parse व validate करो और code में metadata से map करो। सिर्फ़ मौजूदगी नहीं, support भी verify करो।

---

## ➡️ Next Topic
**217. RAG with Streaming** — sending the answer token by token while keeping citations intact.
