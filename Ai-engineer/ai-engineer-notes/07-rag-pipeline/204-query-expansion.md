---

# 204. Query Expansion
# हिंदी में: Query Expansion (क्वेरी का विस्तार)

---

## 🔵 Simple Definition (English)
Query expansion adds extra terms to the user's query (synonyms, abbreviations, related concepts, domain vocabulary) before searching. The expanded query matches documents that use different words than the user. Methods: synonym dictionaries, thesauri, pseudo-relevance feedback, and LLM-generated keywords.

## 🔵 सरल परिभाषा (Hindi)
Query expansion search से पहले user की query में अतिरिक्त शब्द जोड़ती है (synonyms, abbreviations, related concepts, domain vocabulary)। Expanded query उन documents से भी match करती है जो user से अलग शब्द इस्तेमाल करते हैं। तरीके: synonym dictionaries, thesauri, pseudo-relevance feedback और LLM-generated keywords।

---

## 🔴 Problem it Solves
The vocabulary mismatch problem: users say "mobile", documents say "smartphone" or "cellular telephone"; users say "GST", the tariff says "IGST"; users write short 2-word queries with little signal. Keyword search (BM25) especially fails without shared tokens. Expansion bridges the vocabulary gap and raises recall.

## 🔴 यह क्यों बना? (Hindi)
Vocabulary mismatch की समस्या: user "mobile" कहता है, documents "smartphone" या "cellular telephone"; user "GST" कहता है, tariff में "IGST"; users 2 शब्दों की छोटी queries लिखते हैं जिनमें signal कम है। Keyword search (BM25) बिना साझा tokens के खास तौर पर fail होता है। Expansion शब्दों की खाई पाटती है और recall बढ़ाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Normalise the query (lowercase, expand abbreviations)
Step 2 → Pick expansion source:
          a) Synonym/abbreviation dictionary (fast, controlled, domain-specific)
          b) LLM: "list 5 related search terms" (flexible, costs tokens)
          c) Pseudo-relevance feedback: take top-3 results, extract frequent terms
Step 3 → Add expansion terms to the query with LOWER weight than the original terms
Step 4 → Search (BM25 gets the expanded keywords; dense can use the original + joined terms)
Step 5 → Check for drift: expansion must not dominate or change the meaning
Step 6 → Rerank with the ORIGINAL query
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Query normalise करो (lowercase, abbreviations खोलो)
Step 2 → Expansion source चुनो:
          a) Synonym/abbreviation dictionary (तेज़, नियंत्रित, domain-specific)
          b) LLM: "5 related search terms दो" (लचीला, tokens लगते हैं)
          c) Pseudo-relevance feedback: top-3 results से बार-बार आने वाले शब्द निकालो
Step 3 → Expansion terms को original से कम वज़न देकर जोड़ो
Step 4 → Search करो (BM25 को expanded keywords; dense को original + जोड़े गए terms)
Step 5 → Drift जाँचो: expansion से अर्थ नहीं बदलना चाहिए
Step 6 → ORIGINAL query से rerank करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: User: "duty on mobile". Dictionary expansion: mobile -> smartphone, cellular telephone, "HS 8517". The tariff chunk says "telephones for cellular networks" and now matches. Abbreviations: "BCD" -> basic customs duty, "IGST" -> integrated goods and services tax.
**Zomato AI**: "paneer" -> "cottage cheese, paneer tikka, palak paneer" improves menu search recall.

## 🟡 Real Example Hindi mein
**Tariff System**: User: "mobile पर duty"। Dictionary expansion: mobile -> smartphone, cellular telephone, "HS 8517"। Tariff chunk में "telephones for cellular networks" लिखा है और अब match हो जाता है। Abbreviations: "BCD" -> basic customs duty, "IGST" -> integrated goods and services tax।
**Zomato AI**: "paneer" -> "cottage cheese, paneer tikka, palak paneer" से menu search का recall बढ़ता है।

---

## 💻 Code Example — Basic
```python
# Dictionary-based query expansion + weighted BM25-style scoring (pure Python)
import re
from typing import Dict, List, Tuple

SYNONYMS: Dict[str, List[str]] = {  # domain dictionary maintained by experts
    "mobile": ["smartphone", "cellular", "telephone"],
    "earbuds": ["earphones", "headsets"],
    "bcd": ["basic", "customs", "duty"],
}
DOCS: Dict[str, str] = {
    "d1": "hs 8517.13 smartphones and cellular telephones duty 0 percent",
    "d2": "hs 8518.30 earphones and headsets duty 0 percent",
    "d3": "hs 6403.99 leather footwear duty 20 percent",
}

def expand(query: str, expansion_weight: float = 0.5) -> List[Tuple[str, float]]:
    """Return (term, weight) pairs: original terms weight 1.0, added terms lower."""
    terms = re.findall(r"\w+", query.lower())  # original terms
    weighted = {t: 1.0 for t in terms}  # start with originals
    for t in terms:
        for syn in SYNONYMS.get(t, []):
            weighted.setdefault(syn, expansion_weight)  # add synonym unless already present
    return list(weighted.items())

def score(doc: str, weighted_terms: List[Tuple[str, float]]) -> float:
    words = re.findall(r"\w+", doc.lower())  # doc tokens (naive: plural not handled except prefix)
    return sum(w for t, w in weighted_terms if any(x.startswith(t) for x in words))  # weighted matches

def search(query: str, use_expansion: bool = True, k: int = 2) -> List[str]:
    wt = expand(query) if use_expansion else [(t, 1.0) for t in re.findall(r"\w+", query.lower())]
    ranked = sorted(DOCS, key=lambda d: -score(DOCS[d], wt))  # best first
    return [d for d in ranked if score(DOCS[d], wt) > 0][:k]  # drop non-matches

if __name__ == "__main__":
    print("expanded terms:", expand("duty on mobile"))
    print("without expansion:", search("mobile", use_expansion=False))  # [] -> vocabulary mismatch
    print("with expansion   :", search("mobile"))  # ['d1'] -> found via synonyms
```

## 💻 Code Example — Advanced
```python
# LLM + dictionary expansion with budget, drift guard, caching, async, and pseudo-relevance feedback
import asyncio
import json
import logging
import re
from collections import Counter
from typing import Awaitable, Callable

logger = logging.getLogger("expansion")  # logger
LLM = Callable[[str], Awaitable[str]]  # prompt -> text
Search = Callable[[str, int], Awaitable[list[str]]]  # (query string, k) -> chunk texts

STOP = {"the", "a", "of", "and", "for", "on", "in", "to", "is", "are", "duty", "percent"}  # ignore these in PRF

class QueryExpander:
    def __init__(self, llm: LLM, dictionary: dict[str, list[str]], max_terms: int = 6) -> None:
        self.llm, self.dictionary, self.max_terms = llm, dictionary, max_terms  # deps
        self.cache: dict[str, list[str]] = {}  # query -> expansion terms

    async def llm_terms(self, query: str) -> list[str]:
        prompt = (f"List up to {self.max_terms} synonyms, abbreviations or closely related technical terms "
                  f"for this customs tariff search query. JSON list of strings only.\nQuery: {query}")
        try:
            raw = await asyncio.wait_for(self.llm(prompt), 5)  # time-boxed
            terms = [t.lower().strip() for t in json.loads(raw) if isinstance(t, str)]  # validate shape
            return terms[: self.max_terms]
        except Exception as exc:  # network/JSON error
            logger.warning("llm expansion failed: %r", exc); return []

    async def expand(self, query: str) -> list[str]:
        if query in self.cache:
            return self.cache[query]  # no repeated cost
        words = re.findall(r"\w+", query.lower())
        dict_terms = [s for w in words for s in self.dictionary.get(w, [])]  # free, trusted terms
        extra = await self.llm_terms(query) if len(dict_terms) < 2 else []  # call LLM only if dictionary is thin
        terms = [t for t in dict.fromkeys(dict_terms + extra) if t not in words][: self.max_terms]  # dedupe + cap
        self.cache[query] = terms
        return terms

    @staticmethod
    def prf_terms(top_docs: list[str], query: str, n: int = 3) -> list[str]:
        """Pseudo-relevance feedback: frequent non-stop words in top results."""
        qwords = set(re.findall(r"\w+", query.lower()))
        counts = Counter(w for d in top_docs for w in re.findall(r"[a-z]{4,}", d.lower()) if w not in STOP and w not in qwords)
        return [w for w, _ in counts.most_common(n)]

    async def search(self, query: str, searcher: Search, k: int = 5) -> list[str]:
        terms = await self.expand(query)
        expanded_query = query + " " + " ".join(terms)  # original first so it dominates
        first = await searcher(expanded_query, k)  # first-pass retrieval
        prf = self.prf_terms(first[:3], query)  # feedback terms from the best results
        return await searcher(expanded_query + " " + " ".join(prf), k) if prf else first

async def llm_stub(p: str) -> str: return json.dumps(["smartphone", "cellular telephone", "hs 8517"])
async def search_stub(q: str, k: int) -> list[str]: return ["smartphones and cellular telephones duty 0"]

if __name__ == "__main__":
    qe = QueryExpander(llm_stub, {"bcd": ["basic customs duty"]})
    print(asyncio.run(qe.expand("duty on mobile")))
    print(asyncio.run(qe.search("duty on mobile", search_stub)))
```

---

## 🟠 FastAPI Integration
Do cheap dictionary expansion always, LLM expansion only when needed, and return the final expanded query in debug mode so support engineers can explain results.

```python
# FastAPI search with expansion
from fastapi import FastAPI, Query

app = FastAPI()  # app
expander = QueryExpander(real_llm, DOMAIN_DICTIONARY)  # build once (DOMAIN_DICTIONARY loaded from file/DB)

@app.get("/search")
async def search(q: str = Query(min_length=2, max_length=200), k: int = 5, debug: bool = False) -> dict:
    results = await expander.search(q, real_bm25_search, k)  # expansion + retrieval
    out: dict = {"results": results}
    if debug:
        out["expansion_terms"] = await expander.expand(q)  # served from cache
    return out
```

---

## 🔗 LangChain / LangGraph Connection
No single class named "QueryExpansion", but several pieces implement it: `MultiQueryRetriever` (LLM paraphrases), a custom `RunnableLambda` that appends synonyms before `BM25Retriever`, and `ContextualCompressionRetriever` for post-processing. In LangGraph: an `expand` node that updates `state["query"]`/`state["terms"]` before `retrieve`.

```python
# Expansion step in LCEL feeding BM25 (pip install langchain-core langchain-community rank_bm25)
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda

SYN = {"mobile": ["smartphone", "cellular"]}  # tiny dictionary

def expand(q: str) -> str:
    extra = [s for w in q.lower().split() for s in SYN.get(w, [])]  # synonyms for each word
    return q + " " + " ".join(extra)  # original + expansion

docs = [Document(page_content="smartphone duty zero"), Document(page_content="leather footwear duty twenty")]
bm25 = BM25Retriever.from_documents(docs, k=1)  # keyword retriever
chain = RunnableLambda(expand) | bm25  # expand then retrieve
print(chain.invoke("mobile")[0].page_content)  # smartphone duty zero
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Giving expansion terms the same weight as the original words.
✅ Correct: Original terms dominate; expansion adds recall without hijacking meaning (e.g., use boosts in Elasticsearch: `term^1.0` vs `synonym^0.5`).

```python
# Wrong
query = "mobile smartphone cellular telephone handset device gadget"   # drifted
# Right
terms = [("mobile", 1.0), ("smartphone", 0.5), ("cellular", 0.5)]
```

❌ Mistake 2: Expanding ambiguous words blindly ("apple", "jaguar", "chip").
✅ Correct: Use context or domain-specific dictionaries; for LLM expansion, include the domain in the prompt.

```python
# Wrong
SYN["apple"] = ["fruit", "orange"]       # but user meant iPhone
# Right
prompt = "In customs tariff search, list related terms for: apple"
```

---

## 🧠 Tricky Interview Question
**Q**: "After adding query expansion, recall improved but precision dropped and users complain about irrelevant results. What do you do?"

**Answer**: This is query drift: expansion terms pull in loosely related documents. Fixes: down-weight expansion terms; cap the number of terms; restrict to a curated domain dictionary instead of free LLM terms; apply expansion only when the original query returns few or low-scoring hits (adaptive); rerank with a cross-encoder using the original query; evaluate per query segment (short queries benefit, long queries do not). Also consider hybrid search, which supplies semantic recall without altering the keyword query.

---

## ⚫ Interview Questions + Answers

Q1: What is query expansion?
A1: Adding related terms (synonyms, abbreviations, related concepts) to a query to match more relevant documents.

Q2: Name three sources of expansion terms.
A2: Hand-built synonym dictionaries/thesauri, LLM-generated terms, pseudo-relevance feedback from top results (also word embeddings neighbours).

Q3: What is pseudo-relevance feedback?
A3: Assume the top-k results are relevant, extract their most informative terms, add them to the query and search again (Rocchio / RM3 style).

Q4: Query expansion vs multi-query?
A4: Expansion enlarges one query with extra terms (mostly for keyword search); multi-query creates several separate queries and fuses their results.

Q5: How would you roll out expansion safely?
A5: Build a labeled query set; compare baseline vs expansion on recall@k and nDCG per segment; use curated dictionaries first; add LLM expansion behind a flag; use adaptive triggering (low-recall queries only); log expanded queries for review; monitor precision and latency; cache expansions.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- BM25/keyword retrieval is part of the stack
- Short queries, jargon, abbreviations, multilingual terms
- Domain vocabulary differs from user vocabulary

❌ Avoid when:
- Dense-only retrieval already bridges vocabulary well
- Queries are exact identifiers or codes
- You cannot control drift (no eval set)

---

## 📊 Visual Diagram
```
 "duty on mobile"
       │
       ├─ dictionary ──► smartphone, cellular telephone     (free, trusted)
       ├─ LLM ─────────► hs 8517, handset                   (flexible, costs tokens)
       └─ PRF (top-3) ─► "telephones", "networks"           (data-driven)
       ▼
 expanded query:  mobile^1.0  duty^1.0  smartphone^0.5  cellular^0.5 ...
       ▼
 search ──► rerank with ORIGINAL query ──► results
```

---

## 💰 Cost Impact
Dictionary expansion is free. LLM expansion costs about 60 prompt + 40 output tokens on gpt-4o-mini, roughly 0.00003 USD per query, plus latency; caching removes repeats. PRF costs an extra retrieval pass but no tokens. A bigger keyword query slightly increases BM25 compute, which is negligible.
Optimize: dictionary first, LLM only when results are weak, cache, cap terms at 5-6, and rerank to keep final context small.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Query expansion | Adding related terms to a query | Query में related शब्द जोड़ना |
| Synonym | Different word, same meaning | समानार्थी शब्द |
| Pseudo-relevance feedback | Use top results to expand | Top results से terms लेना |
| Query drift | Meaning shifts after expansion | Expansion से अर्थ भटकना |
| Vocabulary mismatch | Query/doc use different words | Query और doc के शब्द अलग |
| Term boost | Weight given to a term | किसी शब्द का वज़न |

---

## ⚡ 3-Line Summary
English: Query expansion adds synonyms, abbreviations and related terms so searches match documents with different wording.
Use dictionaries first, LLM or feedback terms second, and always weight added terms below the originals.
Watch for drift and rerank with the original query.
Hindi: Query expansion synonyms, abbreviations और related शब्द जोड़ती है ताकि अलग शब्दों वाले documents भी match हों।
पहले dictionaries, फिर LLM या feedback terms, और जोड़े गए terms का वज़न हमेशा original से कम रखो।
Drift पर नज़र रखो और original query से rerank करो।

---

## ➡️ Next Topic
**205. Query Decomposition**: split a complex multi-part question into sub-questions, retrieve for each, and combine the answers.
