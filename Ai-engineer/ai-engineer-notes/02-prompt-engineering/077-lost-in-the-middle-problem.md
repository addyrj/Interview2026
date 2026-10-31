---

# 077. Lost in the Middle Problem
# हिंदी में: Lost in the Middle — लंबे prompt के बीच की जानकारी खो जाना

---

## 🔵 Simple Definition (English)
"Lost in the middle" is the observed effect that LLMs use information at the start and end of a long prompt better than information in the middle. Research (Liu et al., 2023) showed a U-shaped accuracy curve: high when the answer is first or last, lower when it sits in the middle. Newer models improve but the effect has not fully disappeared.

## 🔵 सरल परिभाषा (Hindi)
"Lost in the middle" वह देखा गया असर है कि LLM लंबे prompt की शुरुआत और अंत की जानकारी को बीच की जानकारी से बेहतर इस्तेमाल करता है। Research (Liu et al., 2023) में accuracy का U-आकार वक्र दिखा: जवाब पहले या आख़िर में हो तो ऊँची, बीच में हो तो कम। नए models बेहतर हैं पर असर पूरी तरह खत्म नहीं हुआ।

---

## 🔴 Problem it Solves
(This describes a failure mode.) In RAG you retrieve 20 chunks and paste them in rank order. The best evidence may land in position 10 of 20, exactly where the model pays least attention. The answer is in the prompt, yet the model misses it or hallucinates.

Knowing this guides how you order and how many chunks you include.

## 🔴 यह क्यों बना? (Hindi)
(यह एक failure mode है।) RAG में आप 20 chunks retrieve करके rank के क्रम में paste करते हैं। सबसे अच्छा evidence 20 में से 10वें स्थान पर आ सकता है, ठीक वहाँ जहाँ model सबसे कम ध्यान देता है। जवाब prompt में है, फिर भी model चूक जाता है या hallucinate करता है। यह जानना बताता है कि chunks का क्रम और संख्या कैसे तय करें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Long prompt: [instructions][chunk1 ... chunkN][question]
Step 2 → Attention is not uniform; positional effects favour the beginning (primacy) and the end (recency)
Step 3 → Evidence in the middle gets less weight
Step 4 → Accuracy vs position forms a U-shape (high - low - high)
Step 5 → More chunks = deeper "middle" = bigger drop
Step 6 → Mitigate:
         - fewer, better chunks (rerank, small k)
         - place best chunks at start and end (reorder)
         - put the question (and key rules) at the end, also restate at the start
         - split into multiple smaller calls (map-reduce)
         - evaluate by position
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → लंबा prompt: [instructions][chunk1 ... chunkN][question]
Step 2 → Attention समान नहीं होता; positional असर शुरुआत (primacy) और अंत (recency) को तरजीह देता है
Step 3 → बीच के evidence को कम वज़न मिलता है
Step 4 → Position के साथ accuracy का U-आकार वक्र बनता है (ऊँची - कम - ऊँची)
Step 5 → ज़्यादा chunks = गहरा "बीच" = बड़ी गिरावट
Step 6 → उपाय:
         - कम पर बेहतर chunks (rerank, छोटा k)
         - सबसे अच्छे chunks शुरुआत और अंत में रखो (reorder)
         - सवाल (और ज़रूरी rules) आख़िर में रखो, शुरुआत में भी दोहराओ
         - कई छोटी calls में बाँटो (map-reduce)
         - Position के हिसाब से evaluate करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The retriever returns 15 heading descriptions ranked by similarity. The correct heading (8518) is rank 6, in the middle. In tests the model picks the heading ranked first (wrong but prominent) 30% of the time. After reranking, keeping 5 chunks and placing the top-1 at the start and top-2 at the end, accuracy rises noticeably in our eval.

**Amazon-style**: A review-summary bot misses a critical safety complaint located in the middle of 200 pasted reviews.

## 🟡 Real Example Hindi mein
**Tariff System**: Retriever similarity के क्रम में 15 heading descriptions देता है। सही heading (8518) rank 6 पर, यानी बीच में है। Tests में model 30% बार rank 1 वाली (गलत पर प्रमुख) heading चुनता है। Rerank करके 5 chunks रखने और top-1 को शुरुआत व top-2 को अंत में रखने के बाद हमारे eval में accuracy साफ़ बढ़ती है।

**Amazon-style**: 200 paste किए reviews के बीच में दबी एक ज़रूरी safety शिकायत review-summary bot से छूट जाती है।

---

## 💻 Code Example — Basic
```python
# Basic: reorder ranked chunks so the best sit at the edges (pure Python)

def edge_order(ranked: list[str]) -> list[str]:
    """ranked[0] is the best chunk. Put best at the start, 2nd best at the end,
    3rd best second, 4th best second-from-end ... weakest end up in the middle."""
    front: list[str] = []                       # items for the beginning
    back: list[str] = []                        # items for the end (reversed later)
    for i, chunk in enumerate(ranked):          # walk best to worst
        if i % 2 == 0:
            front.append(chunk)                 # even ranks go to the front
        else:
            back.append(chunk)                  # odd ranks go to the back
    return front + back[::-1]                   # reverse back so rank 2 is the very last

ranked = ["R1 best", "R2", "R3", "R4", "R5", "R6 weakest"]
print(edge_order(ranked))
# ['R1 best', 'R3', 'R5', 'R6 weakest', 'R4', 'R2']  -> best and 2nd best sit at the edges

# Also repeat the question at the end of the prompt:
question = "Which heading covers headphones?"
prompt = "Use the context to answer.\n" + "\n".join(edge_order(ranked)) + f"\nQuestion: {question}"
print(prompt)
```

## 💻 Code Example — Advanced
```python
# Production: measure the position effect with a needle test, and apply a mitigation (async)
from __future__ import annotations

import asyncio                                    # async runner
from typing import Awaitable, Callable            # type hints

LLM = Callable[[str], Awaitable[str]]             # prompt -> reply

FILLER = "Heading {n}: general description of unrelated goods and rules."   # distractor text
NEEDLE = "Heading 8518: headphones and earphones are classified here."      # the key fact

def build_prompt(position: int, total: int, question: str) -> str:
    chunks = [FILLER.format(n=i) for i in range(total)]     # distractors
    chunks.insert(position, NEEDLE)                         # hide the needle at this index
    return "Answer from the context only.\n" + "\n".join(chunks) + f"\nQuestion: {question}"

async def needle_test(llm: LLM, total: int = 20, trials: int = 3) -> dict[int, float]:
    """Accuracy by needle position. A U-shape means the lost-in-the-middle effect."""
    positions = [0, total // 4, total // 2, 3 * total // 4, total]   # start ... end
    result: dict[int, float] = {}
    async def one(pos: int) -> bool:
        try:
            out = await llm(build_prompt(pos, total, "Which heading covers headphones?"))
        except Exception:
            return False                                    # API failure counts as miss
        return "8518" in out                                # did it find the needle?
    for pos in positions:
        wins = await asyncio.gather(*(one(pos) for _ in range(trials)))   # repeated trials
        result[pos] = sum(wins) / trials                    # accuracy at this position
    return result

async def _demo() -> None:
    async def sim(prompt: str) -> str:
        # Simulated model that misses the needle when it is in the middle of the prompt
        lines = prompt.splitlines()
        idx = next(i for i, l in enumerate(lines) if "8518" in l)
        middle = len(lines) * 0.3 < idx < len(lines) * 0.7
        return "unknown" if middle else "8518"
    print(await needle_test(sim))

if __name__ == "__main__":
    asyncio.run(_demo())
```
Token usage: the needle test sends `total` chunks per call; 20 chunks x ~15 tokens = ~300 tokens per call, cheap. For real long-context tests (50K+ tokens) costs grow quickly, so sample positions and cap trials.

---

## 🟠 FastAPI Integration
Apply the reorder inside the retrieval-to-prompt step, so the fix is invisible to API clients. Log chunk ranks so you can later analyse which positions the cited evidence came from.

```python
from fastapi import FastAPI                       # framework
from pydantic import BaseModel                    # models
from openai import AsyncOpenAI                    # openai>=1

app = FastAPI()                                   # app
client = AsyncOpenAI()                            # client

class Q(BaseModel):
    question: str                                 # user question

async def retrieve_ranked(q: str, k: int) -> list[str]:   # placeholder: best first
    return ["Heading 8518 headphones", "Heading 8517 phones", "Heading 3926 plastics articles"][:k]

@app.post("/ask")
async def ask(q: Q) -> dict[str, str]:
    ranked = await retrieve_ranked(q.question, k=5)            # best-first chunks
    context = "\n".join(edge_order(ranked))                    # edge_order from basic block
    r = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=0, max_tokens=150,
        messages=[{"role": "system", "content": "Answer ONLY from the context."},
                  {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {q.question}"}])
    return {"answer": r.choices[0].message.content or ""}
```

---

## 🔗 LangChain / LangGraph Connection
`LongContextReorder` (in `langchain_community.document_transformers`) implements exactly this: it reorders documents so the most relevant are at the beginning and end. Use it after the retriever. In LangGraph add a "rerank and reorder" node between retrieval and generation.

```python
from langchain_community.document_transformers import LongContextReorder   # pip install langchain-community
from langchain_core.documents import Document                               # doc type

docs = [Document(page_content=f"chunk {i}") for i in range(1, 7)]           # best-first order
reordered = LongContextReorder().transform_documents(docs)                  # edges get the best
print([d.page_content for d in reordered])
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Dumping 30 chunks in rank order
✅ Correct: Rerank, keep fewer, and reorder.
```python
# Wrong
context = "\n".join(top_30)

# Right
context = "\n".join(edge_order(rerank(top_30)[:6]))
```

❌ Mistake 2: Assuming bigger/newer models have no position bias
✅ Correct: Test with your own data by position.
```python
# Wrong
# "Model X has 1M context, so position does not matter"

# Right
accuracy_by_position = await needle_test(llm)
```

❌ Mistake 3: Burying the question or critical rules in the middle. Put instructions at the start and the question at the end.

---

## 🧠 Tricky Interview Question
**Q**: "Your RAG answer is wrong, but logs show the correct chunk WAS in the prompt. What do you check next?"

**Answer**: Check where it sat (middle of a long context?), how many distractor chunks surround it, whether a conflicting chunk ranked earlier, and whether the prompt told the model to quote its evidence. Fixes: rerank and cut k, reorder to the edges, ask the model to cite the chunk id before answering, use a verification step, and add position-based cases to the eval set.

---

## ⚫ Interview Questions + Answers

Q1: What is the lost-in-the-middle problem?
A1: Models use information at the start and end of long prompts better than information in the middle.

Q2: What does the accuracy curve look like?
A2: U-shaped: high at the beginning, dip in the middle, high at the end.

Q3: Name two mitigations.
A3: Reduce and rerank retrieved chunks, and reorder so the most relevant are at the edges (e.g. LangChain `LongContextReorder`). Also restating the question at the end and splitting into multiple calls.

Q4: Does a bigger context window fix it?
A4: Not by itself. Bigger windows let you add more text, which can deepen the middle. Quality depends on the model and the task, so measure it.

Q5 (Hard): How would you test and monitor for this in production?
A5: Offline: a needle-in-a-haystack style eval using your real documents, varying the evidence position and number of distractors. Online: log the rank/position of cited chunks and compare correctness by position, sample failures with human review, and A/B test reordering and k. Alert if accuracy for middle positions drops after a model or prompt change.

---

## 🔷 When to Use + When Not to Use
(Use = when to apply the mitigations.)

✅ Apply when:
- Prompts contain many chunks or long documents
- Answers depend on one small piece of evidence
- You see correct evidence in the prompt but wrong answers

❌ Not needed when:
- Prompts are short (a few hundred tokens)
- You use only 1-3 highly relevant chunks

---

## 📊 Visual Diagram
```
 Accuracy
   ^
 high |*                                  *
      | *                                *
      |   *                            *
 low  |      *  *   *   *   *   *    *
      +-----------------------------------> position of the key fact
       start          middle              end

 Mitigation: put key chunks at the edges

 [BEST] [3rd] [5th] ... weak ... [6th] [4th] [2nd BEST] [QUESTION]
```

---

## 💰 Cost Impact
- Each extra chunk is extra input tokens, and in the middle it often adds noise but little value.
- Reducing k from 15 to 5 cuts roughly two thirds of the context tokens and often improves accuracy.
- Multi-call strategies (map-reduce) use more calls but smaller prompts, which can be cheaper per call and more accurate.

Optimisation: rerank with a cross-encoder (cheap compared with LLM tokens), use a small k, deduplicate, reorder with `LongContextReorder`, and monitor tokens plus accuracy per position.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lost in the middle | Middle facts get ignored | बीच के facts अनदेखे रह जाते हैं |
| Primacy | Better use of the start | शुरुआत का बेहतर उपयोग |
| Recency | Better use of the end | अंत का बेहतर उपयोग |
| Needle in a haystack | Test hiding a fact in long text | लंबे text में तथ्य छुपाकर test |
| Reorder | Move best items to edges | सबसे अच्छे items किनारों पर रखना |
| Distractor | Irrelevant chunk | भटकाने वाला बेकार chunk |

---

## ⚡ 3-Line Summary
English: LLMs often miss facts in the middle of long prompts, giving a U-shaped accuracy curve. Use fewer, reranked chunks, place the best at the edges and repeat the question at the end. Always test your own model and data by position.
Hindi: LLM अक्सर लंबे prompts के बीच के facts चूक जाते हैं, जिससे accuracy का U-आकार वक्र बनता है। कम और reranked chunks रखो, सबसे अच्छे किनारों पर और सवाल आख़िर में दोहराओ। अपने model और data पर position के हिसाब से हमेशा test करो।

---

## ➡️ Next Topic
**078. Prompt Length Optimization** — finding the right prompt size: enough guidance, no waste.
