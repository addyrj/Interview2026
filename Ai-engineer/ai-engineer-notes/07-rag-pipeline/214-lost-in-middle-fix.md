---

# 214. Lost in Middle — Fix
# हिंदी में: Lost in Middle — समाधान

---

## 🔵 Simple Definition (English)
"Lost in the middle" is a known LLM weakness: models use information at the start and end of a long prompt better than information in the middle. The fix is to reorder chunks so the most relevant ones sit at the edges, and to send fewer chunks.

## 🔵 सरल परिभाषा (Hindi)
"Lost in the middle" LLM की जानी-मानी कमज़ोरी है: लंबे prompt में शुरुआत और अंत की जानकारी बीच की जानकारी से बेहतर इस्तेमाल होती है। समाधान: सबसे relevant chunks को किनारों पर रखो और कम chunks भेजो।

---

## 🔴 Problem it Solves
Research (Liu et al., 2023, "Lost in the Middle") showed accuracy forms a U-shape: high when the answer is first or last, lower when it is in the middle. In RAG, the best chunk (rank 1) is placed first, but the second and third best may be buried in the middle of ten chunks, and get ignored.

## 🔴 यह क्यों बना? (Hindi)
Research (Liu et al., 2023) में accuracy U-shape में दिखी: answer पहले या आख़िर में हो तो ज़्यादा, बीच में हो तो कम। RAG में rank 1 chunk पहले रखा जाता है, पर दूसरा और तीसरा best दस chunks के बीच दब सकता है और ignore हो जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Rerank chunks: rank 1 = most relevant ... rank N = least
Step 2 → Reorder in a U-shaped way:
         place rank 1 FIRST, rank 2 LAST, rank 3 second, rank 4 second-last, ...
         least relevant ends up in the MIDDLE
Step 3 → Reduce N (3-6 chunks is usually enough)
Step 4 → Put the question again at the end (or repeat key instruction)
Step 5 → Optionally label chunks and ask the model to quote the supporting text
Step 6 → Evaluate: needle position test (move gold chunk across positions)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Chunks rerank करो: rank 1 = सबसे relevant ... rank N = सबसे कम
Step 2 → U-shape में reorder करो:
         rank 1 सबसे PEHLE, rank 2 सबसे AAKHIR में, rank 3 दूसरे नंबर पर, rank 4 दूसरे आख़िर में...
         सबसे कम relevant बीच में चला जाता है
Step 3 → N घटाओ (3-6 chunks आमतौर पर काफ़ी)
Step 4 → Question को आख़िर में दोबारा रखो (या मुख्य instruction दोहराओ)
Step 5 → Chunks को label करो और model से supporting text quote करवाओ
Step 6 → Evaluate: needle position test (gold chunk को अलग positions पर रखो)
```

---

## 🟡 Real World Example
**Tariff Classification System**: Ten chunks are retrieved for "duty on refurbished smartphones". The key exception clause is rank 2, but with the default order it lands in position 2 of 10 (early middle) and the model answers with the general 20 percent rate. After U-shape reordering, it is last (right before the question) and the model correctly cites the exception. **Zomato**: policy snippets reordered so the most relevant one is last. **Amazon**: long-review answering with key reviews at the edges.

## 🟡 Real Example Hindi mein
**Tariff System**: "refurbished smartphones पर duty" के लिए दस chunks आते हैं। मुख्य exception clause rank 2 है, पर default order में position 2/10 पर दब जाती है और model general 20 percent बता देता है। U-shape reorder के बाद वह आख़िरी position (question से ठीक पहले) पर आती है और model exception cite करता है। **Zomato**: सबसे relevant policy snippet आख़िर में। **Amazon**: लंबे reviews में key reviews किनारों पर।

---

## 💻 Code Example — Basic
```python
# Pure Python: U-shaped reorder of ranked chunks. Runs offline.
from typing import List, TypeVar  # type hints

T = TypeVar("T")  # any item type


def long_context_reorder(ranked: List[T]) -> List[T]:
    """Input best-first. Output: best at start, second best at end, worst in the middle."""
    front: List[T] = []  # items for the beginning
    back: List[T] = []  # items for the end (kept reversed later)
    for i, item in enumerate(ranked):  # walk in rank order
        if i % 2 == 0:  # ranks 1,3,5... go to the front
            front.append(item)  # front list
        else:  # ranks 2,4,6... go to the back
            back.append(item)  # back list
    return front + back[::-1]  # reverse back so rank 2 ends up LAST


if __name__ == "__main__":
    ranked = ["R1", "R2", "R3", "R4", "R5", "R6"]  # best to worst
    print(long_context_reorder(ranked))  # expected ['R1','R3','R5','R6','R4','R2']
```

## 💻 Code Example — Advanced
```python
# Production: reorder + top-k cap + optional "needle position" evaluation harness (async).
import logging  # logs
import random  # shuffle positions
from typing import Awaitable, Callable  # typing

logger = logging.getLogger("lim")  # logger


def prepare_context(ranked_chunks: list[str], max_chunks: int = 6) -> list[str]:
    """Cap chunk count, then apply U-shaped ordering."""
    if max_chunks < 1:  # validate
        raise ValueError("max_chunks must be >= 1")  # fail early
    top = ranked_chunks[:max_chunks]  # fewer chunks, less middle
    front, back = top[0::2], top[1::2]  # split alternate ranks
    return front + back[::-1]  # best first, second-best last


async def needle_position_test(
    ask: Callable[[str, list[str]], Awaitable[str]],  # async function: (question, chunks) -> answer
    question: str, gold: str, distractors: list[str], expected: str, trials: int = 5,
) -> dict[int, float]:
    """For each position of the gold chunk, measure how often the answer contains `expected`."""
    results: dict[int, float] = {}  # position -> accuracy
    n = len(distractors) + 1  # total chunks
    for pos in range(n):  # every possible position
        hits = 0  # correct answers
        for _ in range(trials):  # repeat with shuffled distractors
            ds = distractors[:]  # copy
            random.shuffle(ds)  # vary distractor order
            chunks = ds[:pos] + [gold] + ds[pos:]  # insert gold at position
            try:  # model call may fail
                out = await ask(question, chunks)  # get answer
                hits += int(expected.lower() in out.lower())  # count correct
            except Exception as exc:  # network error
                logger.warning("trial failed: %s", exc)  # log and continue
        results[pos] = hits / trials  # accuracy at this position
    return results  # U-shape shows up here
```

---

## 🟠 FastAPI Integration
Apply reordering right before prompt assembly, and expose a debug flag to return the order used.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()  # app


class Req(BaseModel):
    question: str  # question
    debug: bool = False  # show order


@app.post("/ask")  # route
async def ask(req: Req) -> dict:
    ranked = ["best chunk", "2nd chunk", "3rd chunk", "4th chunk"]  # from reranker
    ordered = prepare_context(ranked, max_chunks=4)  # U-shaped
    prompt = "\n".join(f"[{i}] {c}" for i, c in enumerate(ordered, 1)) + f"\n\nQuestion: {req.question}"  # question last
    return {"order": ordered if req.debug else None, "prompt_chars": len(prompt)}  # response
```

---

## 🔗 LangChain / LangGraph Connection
`LongContextReorder` is a built-in document transformer in `langchain_community.document_transformers`. It takes documents sorted by relevance and reorders them using this exact idea.

```python
from langchain_community.document_transformers import LongContextReorder  # built-in reorderer

# reordering = LongContextReorder()  # no config needed
# docs = await retriever.ainvoke("duty on refurbished smartphones")  # best first
# reordered = reordering.transform_documents(docs)  # U-shaped order
# In LangGraph: add a `reorder` node between `rerank` and `generate`.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Reordering chunks that are NOT sorted by relevance
✅ Correct: Reorder only after reranking.

```python
# Wrong: input is in document order, so "best" positions get random chunks
ordered = long_context_reorder(chunks_in_page_order)

# Right: rank first
ordered = long_context_reorder(sorted(chunks, key=score, reverse=True))
```

❌ Mistake 2: Sending 20 chunks and relying on reordering
✅ Correct: Reduce chunk count first; reorder is a helper, not a cure.

```python
# Wrong: 20 chunks, 12 irrelevant ones fill the middle
prompt = build(reorder(top20))

# Right: rerank, threshold, then 4-6 chunks
prompt = build(reorder(top20[:5]))
```

---

## 🧠 Tricky Interview Question
**Q**: "You use a 1M-token model and the claim is 'long context solved lost-in-the-middle'. Your tests still show misses when the evidence is in the middle of 200K tokens. What do you do?"

**Answer**: Newer models improved but did not fully remove positional effects, and accuracy also drops with distractor density and multi-hop needs. Measure with your own needle test across positions and context sizes. Mitigations: retrieve and rerank so the prompt is small, order by relevance at the edges, repeat the question after the context, ask the model to quote the supporting evidence first and then answer (forces it to find the passage), split into map-reduce passes for very large inputs, and use prompt caching for the stable part.

---

## ⚫ Interview Questions + Answers

Q1: What is "lost in the middle"?
A1: LLMs recall facts at the beginning and end of a long context better than facts in the middle.

Q2: Name one simple fix.
A2: Reorder retrieved chunks so the most relevant are at the start and end.

Q3: What does LangChain's LongContextReorder do?
A3: It rearranges documents (given best-first) into a U-shaped order: best at the edges, weakest in the middle.

Q4: Besides reordering, how else can you reduce the problem?
A4: Fewer chunks (rerank and cut), compression, repeating the question at the end, quote-then-answer prompting, map-reduce over chunk groups.

Q5: How would you prove the fix works?
A5: Run a controlled needle-position experiment: insert the gold chunk at each position among distractors, measure accuracy per position with and without reordering over many trials and questions, and report the minimum accuracy across positions plus overall answer faithfulness on a labelled set. Compare cost too, since fewer chunks reduce tokens.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You send more than about 5 chunks
- Prompts are long (above ~4K tokens)
- Key evidence is often ranked 2nd-5th

❌ Avoid when:
- You send 1-3 chunks (little middle to lose)
- Chunks are ordered logically and order matters (e.g. chronological steps)

---

## 📊 Visual Diagram
```
 Accuracy by evidence position (typical U-shape)
 100% │ ●                                   ●
      │   ●                              ●
  70% │      ●                       ●
      │          ●   ●   ●   ●  ●
  50% │               (middle)
      └─────────────────────────────────────
        start                        end

 Reorder ranked [R1 R2 R3 R4 R5 R6]
     →  [R1 R3 R5 R6 R4 R2]
         ▲ edges = best      middle = weakest ▲
```

---

## 💰 Cost Impact
- Reordering itself is free (no tokens).
- The real saving comes with it: sending 5 chunks instead of 15 cuts input by about two thirds (for 300-token chunks: 1,500 vs 4,500 tokens).
- Repeating the question at the end adds only about 20 tokens.
- Optimise: rerank, set a threshold, use 4-6 chunks, test with a needle benchmark before increasing K.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lost in the middle | Middle info is used less | बीच की जानकारी कम इस्तेमाल होती है |
| U-shaped curve | High at edges, low in middle | किनारों पर ज़्यादा, बीच में कम |
| Needle test | Hide a fact, test recall | छुपे fact की जाँच |
| LongContextReorder | LangChain reorder transformer | LangChain का reorder tool |
| Distractor | Irrelevant chunk | बेकार chunk |

---

## ⚡ 3-Line Summary
English: LLMs remember the start and end of a prompt best, so key chunks should not sit in the middle. Rerank, cut to a few chunks, then reorder so the best ones are at the edges. Verify with a needle-position test.
Hindi: LLM prompt की शुरुआत और अंत सबसे अच्छा याद रखते हैं, इसलिए key chunks बीच में नहीं होने चाहिए। Rerank करो, कुछ chunks तक घटाओ, फिर best को किनारों पर reorder करो। Needle-position test से verify करो।

---

## ➡️ Next Topic
**215. RAG Response Generation** — the final generation step: controlling the answer's style, grounding, and format.
