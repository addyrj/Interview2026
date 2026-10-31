---

# 344. LangGraph for RAG
# हिंदी में: RAG के लिए LangGraph

---

## 🔵 Simple Definition (English)
Normal RAG is a straight line: retrieve chunks, then generate an answer. LangGraph for RAG turns that line into a **graph** with decisions and loops: retrieve, grade the chunks, rewrite the query if they are bad, retry, and only then answer. This is called **Corrective / Adaptive RAG**.

## 🔵 सरल परिभाषा (Hindi)
सामान्य RAG एक सीधी लाइन है: chunks निकालो, फिर answer बनाओ। RAG के लिए LangGraph इस लाइन को **graph** बना देता है जिसमें decisions और loops होते हैं: retrieve करो, chunks को grade करो, खराब हों तो query rewrite करो, दोबारा try करो, और तब answer दो। इसे **Corrective / Adaptive RAG** कहते हैं।

---

## 🔴 Problem it Solves
A simple chain `retriever | prompt | llm` has no way to notice that retrieval failed. If the top-4 chunks are irrelevant, the LLM still answers and often hallucinates. A chain cannot loop, cannot branch, and cannot say "I don't know". We need conditional edges, retry limits and a fallback path.

## 🔴 यह क्यों बना? (Hindi)
सीधी chain `retriever | prompt | llm` को पता ही नहीं चलता कि retrieval fail हो गया। Top-4 chunks बेकार हों तब भी LLM answer दे देता है और अक्सर hallucinate करता है। Chain loop नहीं कर सकती, branch नहीं कर सकती, और "मुझे नहीं पता" भी नहीं कह सकती। इसलिए conditional edges, retry limit और fallback path चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → State holds: question, documents, generation, retries
Step 2 → Node "retrieve": vector search -> documents
Step 3 → Node "grade": keep only relevant documents (LLM or score threshold)
Step 4 → Conditional edge: any relevant docs left?
Step 5 → NO  -> node "rewrite_query" -> back to "retrieve" (retries + 1)
Step 6 → YES -> node "generate": answer using only relevant docs
Step 7 → retries >= max -> node "fallback": "I don't know / escalate to human"
Step 8 → END -> return answer with sources and token usage
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → State में रखो: question, documents, generation, retries
Step 2 → Node "retrieve": vector search -> documents
Step 3 → Node "grade": सिर्फ relevant documents रखो (LLM या score threshold)
Step 4 → Conditional edge: क्या relevant docs बचे?
Step 5 → नहीं -> "rewrite_query" -> वापस "retrieve" (retries + 1)
Step 6 → हाँ -> "generate": सिर्फ relevant docs से answer
Step 7 → retries >= max -> "fallback": "पता नहीं / human को भेजो"
Step 8 → END -> sources और token usage के साथ answer return
```

---

## 🟡 Real World Example
**Tariff Classification System**: User asks "duty on lithium cells for e-bikes". First retrieval returns chunks about toys (wrong HS chapter). The grader marks 0 of 4 chunks relevant. The graph rewrites the query to "HS 8507 lithium-ion accumulators import duty", retrieves again, gets the correct heading, and only then generates the answer. A plain chain would have confidently quoted the toy tariff.

**Amazon-style**: A product-help bot retrieves return-policy chunks. If they are about "Prime Video" and not "returns", the graph rewrites the query instead of answering wrongly.

## 🟡 Real Example Hindi mein
**Tariff System**: User पूछता है "e-bike के lithium cells पर duty"। पहली retrieval खिलौनों (toys) के chunks लाती है (गलत HS chapter)। Grader 4 में से 0 chunks को relevant बताता है। Graph query को "HS 8507 lithium-ion accumulators import duty" में rewrite करता है, दोबारा retrieve करता है, सही heading मिलती है, तब answer बनता है। सादी chain toy tariff को पूरे भरोसे से बता देती।

**Amazon-style**: Product-help bot return-policy के chunks लाता है। अगर वे "Prime Video" के हैं तो graph गलत answer देने के बजाय query rewrite करता है।

---

## 💻 Code Example — Basic
```python
# Pure Python simulation of the Corrective-RAG loop (no API key needed)
from typing import TypedDict  # TypedDict gives the state a fixed shape

# The shared state that every node reads and updates
class RagState(TypedDict):
    question: str          # current (possibly rewritten) question
    documents: list[str]   # retrieved chunks
    answer: str            # final answer text
    retries: int           # how many rewrites we already did

# Tiny fake knowledge base (stands in for a vector store)
KB: list[str] = [
    "HS 8507: lithium-ion accumulators, basic customs duty 20 percent",
    "HS 9503: toys, basic customs duty 70 percent",
    "HS 8517: smartphones, basic customs duty 20 percent",
]

def retrieve(state: RagState) -> RagState:
    # Naive keyword match: keep chunks sharing any word with the question
    words = set(state["question"].lower().split())  # words of the question
    state["documents"] = [d for d in KB if words & set(d.lower().split())]  # overlap test
    return state  # return updated state

def grade(state: RagState) -> RagState:
    # Keep only chunks that mention the HS heading we need (toy grader)
    state["documents"] = [d for d in state["documents"] if "8507" in d]  # relevance filter
    return state

def rewrite(state: RagState) -> RagState:
    # Rewrite the vague question into a precise one
    state["question"] = "hs 8507 lithium-ion accumulators duty"  # fixed rewrite for demo
    state["retries"] += 1  # count the retry
    return state

def generate(state: RagState) -> RagState:
    # Answer only from graded documents
    state["answer"] = f"Based on: {state['documents'][0]}"  # use best chunk
    return state

def run(question: str, max_retries: int = 2) -> RagState:
    state: RagState = {"question": question, "documents": [], "answer": "", "retries": 0}
    while True:  # this loop is what a chain cannot do
        state = grade(retrieve(state))  # retrieve then grade
        if state["documents"]:  # good chunks found
            return generate(state)  # answer and stop
        if state["retries"] >= max_retries:  # out of retries
            state["answer"] = "I don't know. Escalating to a human."  # safe fallback
            return state
        state = rewrite(state)  # try a better query

if __name__ == "__main__":
    print(run("toys duty"))             # no 8507 chunk -> rewrite -> answer
    print(run("lithium accumulators"))  # direct hit on the first try
```

## 💻 Code Example — Advanced
```python
# Production style: async nodes, typed state, token tracking, error handling
import asyncio  # async runtime
from dataclasses import dataclass, field  # light typed containers
from typing import Literal  # for route names

@dataclass
class State:
    question: str                                   # user question
    docs: list[str] = field(default_factory=list)   # graded documents
    answer: str = ""                                # final answer
    retries: int = 0                                # rewrite counter
    tokens: int = 0                                 # running token estimate

class MockLLM:
    """Stands in for ChatOpenAI so the file runs offline."""
    async def ainvoke(self, prompt: str) -> str:
        await asyncio.sleep(0)  # simulate non-blocking I/O
        return "yes" if "8507" in prompt else "no"  # fake grader decision

llm = MockLLM()  # swap with ChatOpenAI(model="gpt-4o-mini", temperature=0)

async def retrieve(s: State) -> State:
    await asyncio.sleep(0)  # pretend vector DB call
    s.docs = ["HS 8507 lithium-ion duty 20 percent", "HS 9503 toys duty 70 percent"]  # fake hits
    return s

async def grade(s: State) -> State:
    # Grade all docs in parallel: one cheap LLM call per doc
    verdicts = await asyncio.gather(*(llm.ainvoke(f"relevant? {d}") for d in s.docs))
    s.tokens += 40 * len(s.docs)  # rough grading token cost
    s.docs = [d for d, v in zip(s.docs, verdicts) if v == "yes"]  # keep relevant ones
    return s

def route(s: State, max_retries: int = 2) -> Literal["generate", "rewrite", "fallback"]:
    if s.docs:  # we have good evidence
        return "generate"
    return "rewrite" if s.retries < max_retries else "fallback"  # bounded loop

async def run(question: str) -> State:
    s = State(question=question)  # fresh state per request
    try:
        while True:  # graph loop
            s = await grade(await retrieve(s))  # retrieve -> grade
            nxt = route(s)  # decide next node
            if nxt == "generate":
                s.answer = f"Answer from {s.docs[0]}"  # generation step
                s.tokens += 300  # approx prompt+completion
                return s
            if nxt == "fallback":
                s.answer = "Not enough evidence; escalating."  # honest failure
                return s
            s.retries += 1  # rewrite step
            s.question = s.question + " HS heading"  # simple rewrite
    except Exception as exc:  # never crash the API
        s.answer = f"Error: {exc}"  # surface error safely
        return s

if __name__ == "__main__":
    print(asyncio.run(run("lithium cells duty")))  # run one request
```

---

## 🟠 FastAPI Integration
Expose the compiled graph as one endpoint. Use `ainvoke` so the event loop is never blocked, and return the sources and token usage so the frontend can show citations.

```python
from fastapi import FastAPI, HTTPException  # web framework + errors
from pydantic import BaseModel  # request/response models (pydantic v2)

app = FastAPI()  # create the app

class AskIn(BaseModel):
    question: str  # user question

class AskOut(BaseModel):
    answer: str          # final answer
    sources: list[str]   # chunks used
    retries: int         # how many rewrites happened

@app.post("/rag/ask", response_model=AskOut)
async def ask(body: AskIn) -> AskOut:
    try:
        # rag_graph is the compiled LangGraph (see next section)
        result = await rag_graph.ainvoke({"question": body.question, "documents": [], "retries": 0})
    except Exception as exc:  # graph or LLM failure
        raise HTTPException(status_code=502, detail=str(exc))  # upstream error
    return AskOut(answer=result["answer"], sources=result["documents"], retries=result["retries"])
```

---

## 🔗 LangChain / LangGraph Connection
```python
from typing import TypedDict  # state schema
from langgraph.graph import StateGraph, START, END  # graph builder + markers

class GraphState(TypedDict):
    question: str          # current question
    documents: list[str]   # retrieved chunks
    answer: str            # output
    retries: int           # loop guard

def retrieve_node(state: GraphState) -> dict:
    docs = retriever.invoke(state["question"])  # LangChain retriever (Chroma, FAISS...)
    return {"documents": [d.page_content for d in docs]}  # partial state update

def grade_node(state: GraphState) -> dict:
    kept = [d for d in state["documents"] if grader_chain.invoke({"q": state["question"], "d": d}) == "yes"]
    return {"documents": kept}  # keep only relevant

def rewrite_node(state: GraphState) -> dict:
    new_q = rewrite_chain.invoke({"q": state["question"]})  # LCEL prompt | llm | parser
    return {"question": new_q, "retries": state["retries"] + 1}

def generate_node(state: GraphState) -> dict:
    return {"answer": answer_chain.invoke({"q": state["question"], "ctx": state["documents"]})}

def fallback_node(state: GraphState) -> dict:
    return {"answer": "I could not find reliable information."}

def decide(state: GraphState) -> str:
    if state["documents"]:
        return "generate"
    return "rewrite" if state["retries"] < 2 else "fallback"

g = StateGraph(GraphState)  # build graph
g.add_node("retrieve", retrieve_node)
g.add_node("grade", grade_node)
g.add_node("rewrite", rewrite_node)
g.add_node("generate", generate_node)
g.add_node("fallback", fallback_node)
g.add_edge(START, "retrieve")
g.add_edge("retrieve", "grade")
g.add_conditional_edges("grade", decide, {"generate": "generate", "rewrite": "rewrite", "fallback": "fallback"})
g.add_edge("rewrite", "retrieve")  # the loop
g.add_edge("generate", END)
g.add_edge("fallback", END)
rag_graph = g.compile()  # runnable with invoke / ainvoke / stream
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: A rewrite loop with no limit
✅ Correct: always keep a `retries` counter and a fallback node.

```python
# Wrong: loops forever if the KB has no answer, burning tokens
def decide(state): return "generate" if state["documents"] else "rewrite"

# Right: bounded loop
def decide(state): 
    if state["documents"]: return "generate"
    return "rewrite" if state["retries"] < 2 else "fallback"
```

❌ Mistake 2: Generating even when no chunk passed grading
✅ Correct: route to a fallback ("I don't know") instead of letting the LLM guess.

```python
# Wrong: always generate
g.add_edge("grade", "generate")
# Right: conditional edge with a fallback branch
g.add_conditional_edges("grade", decide)
```

---

## 🧠 Tricky Interview Question
**Q**: "Your Corrective-RAG graph improved accuracy but the bill doubled. Why, and what do you do?"

**Answer**: Every grading call and every rewrite is an extra LLM call, and a loop can run several times. Fixes: grade with a cheap model (gpt-4o-mini) or a cross-encoder reranker instead of an LLM, grade chunks in one batched call, cap retries at 1-2, skip grading when the vector similarity score is already high, cache rewrites, and measure the rewrite rate. Accuracy gain must be weighed against cost per answered query.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Why use LangGraph instead of a simple RAG chain?
A1: A chain is linear. LangGraph supports conditional edges and loops, so we can grade retrieval, rewrite queries, retry, and fall back.

Q2: [Easy] What is the state in a RAG graph?
A2: A typed dict (or pydantic model) with question, documents, answer, retries. Each node returns a partial update that LangGraph merges into the state.

Q3: [Medium] What is Corrective RAG versus Adaptive RAG?
A3: Corrective RAG grades retrieved documents and re-retrieves or searches the web if they are poor. Adaptive RAG first routes the question (no retrieval needed, vectorstore, or web search) based on its type, then may also correct.

Q4: [Medium] How do you prevent infinite loops?
A4: Keep a retries counter in state, stop at a limit with a fallback node, and also set `recursion_limit` in the run config as a hard safety net.

Q5: [Hard] How would you evaluate whether the graph is better than a plain chain?
A5: Build a labelled test set of tariff questions. Compare answer correctness, faithfulness (answer supported by sources), retrieval hit rate, latency p95, and cost per query for both. Track the rewrite rate and fallback rate in production; a high fallback rate means the knowledge base has gaps, not a graph problem.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Retrieval quality varies and wrong answers are costly (legal, tariff, medical)
- You need fallbacks, human escalation or web search as a second source
- Queries are vague and benefit from rewriting

❌ Avoid when:
- A small FAQ bot where plain RAG already scores well
- Strict latency budget (each loop adds seconds)
- Very tight cost limits with no budget for grading calls

---

## 📊 Visual Diagram
```
        START
          |
      [retrieve] <------------------+
          |                         |
       [grade]                [rewrite_query]
          |                         ^
     docs relevant?  --- no, retries<2 ---+
       |        \
      yes        no, retries>=2
       |               \
   [generate]        [fallback]
       |                 |
      END               END
```

---

## 💰 Cost Impact
- Plain RAG: 1 generation call (about 1,500 prompt + 300 completion tokens).
- Corrective RAG: add grading (about 4 x 150 tokens), plus rewrite (about 100 tokens) per loop. Worst case with 2 retries can be 2-3x the plain cost.
- Optimise: cheap grader model or reranker, batch grading in one prompt, retries cap of 1-2, skip grading on high similarity, cache the final answers, send only the top-k graded chunks to the generator.
- Always return `usage` metadata and log tokens per node.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Corrective RAG | RAG that grades and fixes retrieval | Retrieval को जाँचकर सुधारने वाला RAG |
| Grader | Judge that scores chunk relevance | Chunk की relevance जाँचने वाला |
| Query rewrite | Making the question search-friendly | Question को बेहतर बनाना |
| Conditional edge | Edge chosen by a function | शर्त के आधार पर चुना गया रास्ता |
| Fallback | Safe path when evidence is missing | सुरक्षित वैकल्पिक रास्ता |
| Recursion limit | Max steps allowed in a run | अधिकतम steps की सीमा |

---

## ⚡ 3-Line Summary
English: LangGraph turns RAG into a loop of retrieve, grade, rewrite and generate. Conditional edges let the system retry or admit it does not know. Always bound the loop and watch the extra token cost.
Hindi: LangGraph RAG को retrieve, grade, rewrite और generate के loop में बदल देता है। Conditional edges से system दोबारा कोशिश कर सकता है या मान सकता है कि उसे पता नहीं। Loop हमेशा सीमित रखो और extra token cost पर नज़र रखो।

---

## ➡️ Next Topic
**345. LangGraph for Tariff System** — applying all these graph patterns to build the complete Tariff Classification workflow.
