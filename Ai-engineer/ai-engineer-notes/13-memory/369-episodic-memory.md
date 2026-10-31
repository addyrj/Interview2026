---

# 369. Episodic Memory
# हिंदी में: Episodic Memory (घटनाओं की Memory)

---

## 🔵 Simple Definition (English)
Episodic memory stores specific past events — "what happened, when, and with what result" — like a diary. In agents it holds past interactions or task runs (input, actions, outcome) so the agent can recall similar past situations and learn from them.

## 🔵 सरल परिभाषा (Hindi)
Episodic memory खास पुरानी घटनाएँ store करती है — "क्या हुआ, कब हुआ, नतीजा क्या रहा" — diary की तरह। Agents में यह पुराने interactions या task runs (input, actions, outcome) रखती है ताकि agent मिलती-जुलती पुरानी situation याद कर सके और उससे सीख सके।

---

## 🔴 Problem it Solves
- Facts ("user likes INR") do not capture *experiences* ("last time HS 6109 was rejected because of fabric mix").
- Agents repeat the same mistakes without a record of past attempts.
- Few-shot examples are static; episodes give *relevant, real* examples.

## 🔴 यह क्यों बना? (Hindi)
- Facts अनुभव नहीं बताते ("पिछली बार fabric mix की वजह से HS 6109 reject हुआ")।
- Past attempts का record न हो तो agent वही गलती दोहराता है।
- Few-shot examples static होते हैं; episodes असली और relevant examples देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → An interaction/task finishes
Step 2 → Build an EPISODE: {timestamp, situation, actions, outcome, feedback}
Step 3 → Store it with an embedding of the situation (vector DB) + metadata
Step 4 → New task arrives -> embed the new situation
Step 5 → Retrieve top-k similar episodes (filter by user/outcome/recency)
Step 6 → Put them in the prompt as "similar past cases" -> LLM reasons using them
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Interaction/task खत्म होता है
Step 2 → EPISODE बनाओ: {time, situation, actions, outcome, feedback}
Step 3 → Situation के embedding + metadata के साथ store करो
Step 4 → नया task आए -> उसका embedding बनाओ
Step 5 → मिलते-जुलते top-k episodes निकालो (user/outcome/recency से filter)
Step 6 → उन्हें "similar past cases" बनाकर prompt में दो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Episode: "Product: cotton-polyester blend shirt. Tried HS 6109 -> officer corrected to 6206. Reason: women's blouse of man-made fibre." A month later a similar blend shirt arrives; retrieving this episode steers the model straight to the corrected code.
**Zomato AI**: "Last time you ordered late night, delivery was delayed; suggest restaurants nearer".

## 🟡 Real Example Hindi mein
**Tariff System**: Episode: "Product: cotton-polyester blend shirt। HS 6109 try किया -> officer ने 6206 किया। कारण: man-made fibre की women's blouse।" महीने बाद वैसी ही shirt आए तो यह episode retrieve होकर model को सही code पर ले जाता है।
**Zomato AI**: "पिछली बार late night order में देर हुई थी, पास के restaurants suggest करो"।

---

## 💻 Code Example — Basic
```python
# Pure Python (offline): episodes with a toy keyword-overlap similarity
from dataclasses import dataclass                                    # tidy record type

@dataclass
class Episode:                                                       # one remembered event
    situation: str                                                   # what was the case
    action: str                                                      # what the agent did
    outcome: str                                                     # result / feedback
    ts: int                                                          # when (simple counter)

episodes: list[Episode] = []                                         # the episodic memory

def record(situation: str, action: str, outcome: str, ts: int) -> None:   # write an episode
    episodes.append(Episode(situation, action, outcome, ts))        # append to list

def similarity(a: str, b: str) -> float:                             # toy Jaccard similarity
    sa, sb = set(a.lower().split()), set(b.lower().split())          # word sets
    return len(sa & sb) / max(1, len(sa | sb))                       # overlap ratio 0..1

def recall(situation: str, k: int = 2) -> list[Episode]:             # top-k similar episodes
    ranked = sorted(episodes, key=lambda e: similarity(e.situation, situation), reverse=True)  # best first
    return ranked[:k]                                                # keep k

record("cotton polyester blend shirt", "HS 6109", "corrected to 6206", 1)   # past case 1
record("laptop battery pack", "HS 8507", "approved", 2)              # past case 2
for e in recall("blend shirt cotton polyester women"):               # new similar case
    print(e.situation, "->", e.action, "|", e.outcome)               # shows the useful episode
```

## 💻 Code Example — Advanced
```python
# Async episodic memory: embed -> store -> retrieve, with an injectable embedder
import asyncio                                                       # async runtime
import math                                                          # cosine similarity
import time                                                          # timestamps
from dataclasses import dataclass, field                             # data classes
from typing import Awaitable, Callable                               # callable types

Embedder = Callable[[str], Awaitable[list[float]]]                   # async text -> vector


async def toy_embed(text: str) -> list[float]:                       # offline fake embedder
    vec = [0.0] * 8                                                  # 8-dim hashed bag of words
    for w in text.lower().split():                                   # each word
        vec[hash(w) % 8] += 1.0                                      # bump a bucket
    return vec                                                       # return vector


def cosine(a: list[float], b: list[float]) -> float:                 # cosine similarity
    dot = sum(x * y for x, y in zip(a, b))                           # dot product
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))  # norms
    return dot / (na * nb) if na and nb else 0.0                     # avoid divide by zero


@dataclass
class Episode:                                                       # stored event
    user_id: str
    situation: str
    action: str
    outcome: str
    vec: list[float] = field(default_factory=list)                   # embedding of situation
    ts: float = field(default_factory=time.time)                     # creation time


class EpisodicMemory:                                                # service
    def __init__(self, embed: Embedder) -> None:
        self.embed = embed                                           # embedding function
        self.items: list[Episode] = []                               # replace with vector DB

    async def add(self, user_id: str, situation: str, action: str, outcome: str) -> None:
        vec = await self.embed(situation)                            # embed the situation only
        self.items.append(Episode(user_id, situation, action, outcome, vec))  # store

    async def search(self, user_id: str, situation: str, k: int = 3, min_score: float = 0.3) -> list[Episode]:
        try:
            q = await self.embed(situation)                          # embed query
        except Exception:                                            # embedder down -> no recall
            return []
        mine = [e for e in self.items if e.user_id == user_id]       # isolate users
        scored = [(cosine(q, e.vec), e) for e in mine]               # score each
        good = [p for p in scored if p[0] >= min_score]              # drop weak matches
        good.sort(key=lambda p: p[0], reverse=True)                  # best first
        return [e for _, e in good[:k]]                              # top-k

    @staticmethod
    def to_prompt(eps: list[Episode]) -> str:                        # format for the LLM
        return "\n".join(f"- Case: {e.situation} | Did: {e.action} | Result: {e.outcome}" for e in eps)


async def main() -> None:                                            # demo
    mem = EpisodicMemory(toy_embed)                                  # create memory
    await mem.add("u1", "cotton polyester blend shirt", "HS 6109", "corrected to 6206")
    hits = await mem.search("u1", "blend shirt cotton polyester")    # similar query
    print(mem.to_prompt(hits))                                       # prompt block

if __name__ == "__main__":
    asyncio.run(main())                                              # run
```

---

## 🟠 FastAPI Integration
Expose `POST /feedback` so officer corrections become new episodes — this is how the system learns without retraining.

```python
# FastAPI: classify (reads episodes) + feedback (writes episodes)
from fastapi import FastAPI                         # framework
from pydantic import BaseModel                      # schema

app = FastAPI()                                     # app
episodic = EpisodicMemory(toy_embed)                # singleton

class ClassifyIn(BaseModel):
    user_id: str
    product: str

class FeedbackIn(ClassifyIn):                       # adds the human outcome
    predicted: str
    correct: str

@app.post("/classify")
async def classify(body: ClassifyIn) -> dict[str, str]:
    eps = await episodic.search(body.user_id, body.product)   # similar past cases
    return {"similar_cases": episodic.to_prompt(eps) or "none"}   # feed into LLM prompt

@app.post("/feedback")
async def feedback(body: FeedbackIn) -> dict[str, str]:
    await episodic.add(body.user_id, body.product, body.predicted, f"corrected to {body.correct}")
    return {"status": "stored"}
```

---

## 🔗 LangChain / LangGraph Connection
Episodes are usually stored in a LangGraph `Store` with semantic search (an `index` config with an embedding model), or a LangChain vector store with metadata. In LangGraph, a node reads similar episodes before reasoning and a final node writes the new episode.

```python
# LangChain vector store as episodic memory (InMemoryVectorStore from langchain_core)
from langchain_core.vectorstores import InMemoryVectorStore   # simple vector store
from langchain_core.documents import Document                 # document type
from langchain_openai import OpenAIEmbeddings                 # embedding model

vs = InMemoryVectorStore(OpenAIEmbeddings(model="text-embedding-3-small"))   # store
vs.add_documents([Document(
    page_content="cotton polyester blend shirt",             # what we search on
    metadata={"user_id": "u1", "action": "HS 6109", "outcome": "corrected to 6206"},  # the rest
)])
hits = vs.similarity_search("blend shirt", k=2, filter=lambda d: d.metadata["user_id"] == "u1")
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Storing raw full transcripts as episodes
✅ Correct: store a compact structured episode (situation, action, outcome).

```python
# Wrong: vs.add_texts([entire_20_turn_chat])      # noisy, expensive, poor retrieval
# Right: vs.add_texts([f"{situation} -> {action} -> {outcome}"])
```

❌ Mistake 2: Learning from wrong outcomes
✅ Correct: store the outcome/feedback and prefer verified ones.

```python
# Wrong: store every model answer as "good example"
# Right: store only when outcome == "approved" or with a "corrected" label
```

---

## 🧠 Tricky Interview Question
**Q**: "Your episodic retrieval keeps returning old, wrong episodes after tariff rules changed. How do you fix it?"

**Answer**: Add time awareness: store `valid_from`/`rule_version`, boost recency in ranking, filter or down-weight episodes older than the rule change, and mark superseded episodes as `stale`. Also re-validate episodes with a rules check before use. Retrieval by similarity alone has no notion of truth over time.

---

## ⚫ Interview Questions + Answers

Q1: What is episodic memory?
A1: Memory of specific past events with context and outcome.

Q2: How is it different from semantic memory?
A2: Episodic = events ("on 5 Jan HS 6109 was rejected"). Semantic = general facts ("cotton shirts are usually 6109").

Q3: What should an episode contain?
A3: Timestamp, situation, actions taken, outcome/feedback, user/tenant id, optional rule version.

Q4: How do you retrieve episodes?
A4: Embed the current situation, vector search with metadata filters (user, outcome), blend with recency, return top-k above a similarity threshold.

Q5: How would you build a learning loop from episodes without fine-tuning?
A5: Capture human feedback as episodes, retrieve them as dynamic few-shot examples, periodically distil recurring episodes into semantic rules (reviewed by humans), and measure accuracy before/after using an eval set.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Agents repeat similar tasks and feedback exists
- Support/case-based reasoning
- Personal assistants recalling past interactions

❌ Avoid when:
- No feedback or outcomes are known
- Rules change fast and old cases mislead
- Privacy rules forbid keeping interaction logs

---

## 📊 Visual Diagram
```
 Task done ─▶ Episode{situation, action, outcome} ─▶ embed ─▶ Vector DB
 New task  ─▶ embed ─▶ top-k similar episodes ─▶ prompt ─▶ LLM
```

---

## 💰 Cost Impact
- Embedding a 30-token situation with `text-embedding-3-small` costs a tiny fraction of a cent; retrieval of 3 episodes adds ~150 prompt tokens.
- Saves cost indirectly by cutting retries and corrections. Optimise: embed only the situation, cache embeddings, keep k small (2-3).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Episode | One stored event | एक घटना का record |
| Outcome | Result / feedback | नतीजा |
| Similarity search | Find nearest vectors | मिलते-जुलते vectors खोजना |
| Recency boost | Prefer newer items | नए items को प्राथमिकता |
| Stale | Outdated | पुराना / अप्रासंगिक |

---

## ⚡ 3-Line Summary
English: Episodic memory records past events with their outcomes. It is retrieved by similarity to give the agent real examples. Keep episodes compact, verified and time-aware.
Hindi: Episodic memory पुरानी घटनाओं को उनके नतीजों के साथ record करती है। Similarity से retrieve होकर agent को असली examples देती है। Episodes छोटे, verified और time-aware रखो।

---

## ➡️ Next Topic
**370. Semantic Memory** — general facts and knowledge about the user/world, separate from events.
