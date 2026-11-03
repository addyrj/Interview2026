
---

# 343. Common LangGraph Patterns
# हिंदी में: आम LangGraph Patterns

---

## 🔵 Simple Definition (English)
LangGraph patterns are reusable graph shapes for common agent problems: a router (pick a path), a ReAct loop (think, call tool, observe, repeat), reflection (generate, critique, revise), plan-and-execute, parallel fan-out/fan-in, and human approval. Learning the shapes lets you design a new agent quickly.

## 🔵 सरल परिभाषा (Hindi)
LangGraph patterns आम agent समस्याओं के लिए दोबारा इस्तेमाल होने वाले graph आकार हैं: router (रास्ता चुनो), ReAct loop (सोचो, tool चलाओ, देखो, दोहराओ), reflection (बनाओ, critique, सुधारो), plan-and-execute, parallel fan-out/fan-in और human approval। आकार सीख लिए तो नया agent जल्दी design हो जाता है।

---

## 🔴 Problem it Solves
Beginners build one huge prompt that tries to do everything, or wire nodes randomly. That leads to unpredictable behaviour, high token cost and hard debugging. Named patterns give a proven structure with clear control flow and known failure modes.

## 🔴 यह क्यों बना? (Hindi)
नए लोग एक विशाल prompt में सब कुछ डालते हैं या nodes बेतरतीब जोड़ते हैं। नतीजा: अप्रत्याशित व्यवहार, ज़्यादा token cost और कठिन debugging। Named patterns सिद्ध structure, साफ़ control flow और ज्ञात failure modes देते हैं।

---

## 🟢 How it Works — Step by Step

```
Pattern 1  Router:        classify input -> conditional edge -> specialised node
Pattern 2  ReAct loop:    LLM decides tool call -> tool node runs -> back to LLM -> until no tool call
Pattern 3  Reflection:    generate -> critique -> (good? END : revise -> critique ...) with max rounds
Pattern 4  Plan-Execute:  planner makes steps -> executor runs each -> replanner may adjust
Pattern 5  Fan-out/in:    split work to parallel nodes (or Send API) -> reducer merges results
Pattern 6  Human gate:    interrupt before risky node -> human approves/edits -> resume
Pattern 7  Supervisor:    one LLM routes to worker agents and decides when to finish
Always: typed state, loop cap, checkpointer, tests with fake LLM
```

## 🟢 कैसे काम करता है? (Hindi)
```
Pattern 1  Router:        input classify -> conditional edge -> विशेष node
Pattern 2  ReAct loop:    LLM tool call तय करे -> tool चले -> LLM पर वापस -> जब तक tool call न हो
Pattern 3  Reflection:    generate -> critique -> (ठीक? END : revise) अधिकतम rounds के साथ
Pattern 4  Plan-Execute:  planner steps बनाए -> executor चलाए -> replanner बदलाव करे
Pattern 5  Fan-out/in:    काम parallel nodes (या Send API) में बाँटो -> reducer से जोड़ो
Pattern 6  Human gate:    जोखिम वाले node से पहले interrupt -> इंसान approve/edit -> resume
Pattern 7  Supervisor:    एक LLM workers को route करे और finish तय करे
हमेशा: typed state, loop cap, checkpointer, fake LLM से tests
```

---

## 🟡 Real World Example
**Tariff Classification System**: Router sends "classify" vs "duty calculation" vs "FAQ". The classify path is a ReAct loop with tools `search_tariff_db` and `get_chapter_notes`. A reflection step has a critic check the code against the chapter notes (max 2 rounds). High-value shipments (> a threshold) hit a human gate before the declaration is filed. Multi-line invoices use fan-out: one classify per line in parallel.

**Amazon-style**: a product-listing agent uses plan-and-execute: plan (title, bullets, category) then execute each part.

## 🟡 Real Example Hindi mein
**Tariff System**: Router "classify", "duty calculation" और "FAQ" में बाँटता है। Classify path ReAct loop है जिसमें tools `search_tariff_db` और `get_chapter_notes` हैं। Reflection में critic chapter notes से code जाँचता है (अधिकतम 2 rounds)। ऊँची value की shipments पर human gate। Multi-line invoice में हर line के लिए parallel classify।

**Amazon-style**: Product-listing agent plan-and-execute से: पहले plan (title, bullets, category), फिर हर हिस्सा बनाओ।

---

## 💻 Code Example — Basic
```python
# Pure Python demo of two patterns: Router and Reflection-with-cap (no libraries needed)
from typing import Callable  # type for functions

# ---- Pattern 1: Router ----
def route(question: str) -> str:
    """Pick a handler name from keywords (a real router would use an LLM or classifier)."""
    q = question.lower()  # normalise
    if "duty" in q or "tax" in q:  # money question
        return "duty"
    if "code" in q or "classify" in q:  # classification question
        return "classify"
    return "faq"  # default path

handlers: dict[str, Callable[[str], str]] = {  # node name -> function
    "duty": lambda q: "duty calc node",
    "classify": lambda q: "classify node",
    "faq": lambda q: "faq node",
}
for q in ["What is the HS code for tea?", "How much duty on laptops?", "Opening hours?"]:
    print(q, "->", handlers[route(q)](q))  # show routing result

# ---- Pattern 3: Reflection with a round cap ----
def generate(round_no: int) -> str:
    return "8518.3" if round_no == 0 else "8518.30"  # first draft is wrong, revision is right

def critique(code: str) -> bool:
    return len(code.replace(".", "")) == 6  # accept only 6-digit codes

code, rounds = "", 0  # state
while rounds < 3:  # hard cap prevents endless self-critique
    code = generate(rounds)  # produce or revise
    rounds += 1  # count
    if critique(code):  # critic approves
        break  # stop
print("final:", code, "after", rounds, "rounds")  # 8518.30 after 2 rounds
```

## 💻 Code Example — Advanced
```python
# LangGraph ReAct-style loop with a conditional edge (router) and tool node, async and typed
# pip install langgraph langchain-openai ; needs OPENAI_API_KEY to run with a real model
import logging  # logs
from typing import Annotated, TypedDict  # typing

from langchain_core.messages import AnyMessage  # message type
from langchain_core.tools import tool  # tool decorator
from langchain_openai import ChatOpenAI  # chat model
from langgraph.graph import END, StateGraph  # graph API
from langgraph.graph.message import add_messages  # message reducer
from langgraph.prebuilt import ToolNode  # runs tool calls from the last AI message

log = logging.getLogger("react")  # logger

@tool
def search_tariff_db(query: str) -> str:
    """Search the tariff database for matching HS headings."""
    return "8518.30: Headphones and earphones"  # stub; query a real DB/vector store here

tools = [search_tariff_db]  # tool list
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)  # model that can request tools

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]  # reducer appends messages

async def agent(state: State) -> dict:
    """LLM step: either answers or requests a tool call."""
    try:
        reply = await llm.ainvoke(state["messages"])  # call model
    except Exception as exc:  # provider failures
        log.error("llm error: %s", exc)  # log
        raise  # let LangGraph surface it
    return {"messages": [reply]}  # append reply

def should_continue(state: State) -> str:
    """Router: continue to tools if the last message has tool calls, else end."""
    last = state["messages"][-1]  # most recent message
    return "tools" if getattr(last, "tool_calls", None) else END  # loop or stop

g = StateGraph(State)  # create graph
g.add_node("agent", agent)  # LLM node
g.add_node("tools", ToolNode(tools))  # tool node
g.set_entry_point("agent")  # start at the LLM
g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})  # decide
g.add_edge("tools", "agent")  # observe result then think again
app = g.compile()  # runnable graph

# result = await app.ainvoke({"messages": [("user", "HS code for bluetooth headphones?")]},
#                            {"recursion_limit": 8})  # loop cap
```

---

## 🟠 FastAPI Integration
Expose the loop with streaming so the UI can show tool steps as they happen.

```python
import json  # serialise events
from fastapi import FastAPI  # framework
from fastapi.responses import StreamingResponse  # streaming
from pydantic import BaseModel  # schema

app = FastAPI()  # app
# `graph_app` is the compiled graph from the advanced example (import it in real code)

class Q(BaseModel):
    question: str  # user question

@app.post("/ask/stream")
async def ask_stream(q: Q) -> StreamingResponse:
    """Stream node updates as server-sent lines."""
    async def gen():
        async for event in graph_app.astream(  # noqa: F821
            {"messages": [("user", q.question)]},  # input
            {"recursion_limit": 8},  # loop cap
            stream_mode="updates",  # one chunk per node
        ):
            yield json.dumps({k: str(v)[:200] for k, v in event.items()}) + "\n"  # trimmed line
    return StreamingResponse(gen(), media_type="application/x-ndjson")  # newline-delimited JSON
```

---

## 🔗 LangChain / LangGraph Connection
`langgraph.prebuilt.create_react_agent` builds the ReAct loop for you from a model and tools. Write the loop by hand when you need custom state, extra validation nodes or a human gate. Parallel fan-out uses multiple edges from one node, or the `Send` API for a dynamic number of branches.

```python
from langgraph.prebuilt import create_react_agent  # ready-made ReAct agent

# agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), tools)  # one-liner version
# await agent.ainvoke({"messages": [("user", "HS code for headphones?")]})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Reflection without a cap
✅ Correct: Max rounds in state.
```python
# Wrong: while not critique_ok: revise()      # can loop forever, burning tokens
# Right: while rounds < 3 and not critique_ok: revise(); rounds += 1
```

❌ Mistake 2: Using a supervisor/agent when a fixed chain works
✅ Correct: Prefer the simplest pattern that solves the task.
```python
# Wrong: multi-agent supervisor for "extract fields from invoice"
# Right: one extract node with structured output + one validate node
```

❌ Mistake 3: Parallel branches writing the same key without a reducer
✅ Correct: Give that key a reducer (e.g. `operator.add`) or write to separate keys.

---

## 🧠 Tricky Interview Question

**Q**: "Your ReAct agent calls the same search tool 10 times with slightly different queries and then hits the recursion limit. What do you change?"

**Answer**: The agent has no stopping signal or good observations. Improve the tool (return richer, ranked results with ids), tell the model in the system prompt when to stop and to answer with what it has, add a tool-call counter in state with a forced "final answer" node after N calls, dedupe repeated calls (cache by arguments), lower the `recursion_limit` and return a graceful "needs human review" instead of an error. Also check that the tool output is not an unhelpful empty string.

---

## ⚫ Interview Questions + Answers

Q1: What is the ReAct pattern?
A1: The model alternates reasoning and acting: it decides to call a tool, reads the observation, and repeats until it can answer.

Q2: What is a conditional edge?
A2: An edge whose next node is chosen by a function reading the state; it implements routers and loop exits.

Q3: When use reflection?
A3: When output quality can be checked (against rules or notes) and one more pass likely improves it; always with a round cap.

Q4: Plan-and-execute versus ReAct?
A4: Plan-and-execute writes a full plan first (fewer LLM calls per step, better for long tasks) but is less adaptive; ReAct decides step by step, more flexible but can wander and costs more calls.

Q5: Design a graph to classify a 200-line invoice quickly and safely.
A5: Split lines (map step), fan out with the `Send` API to parallel classify nodes with limited concurrency, each with a validate step and capped retries, merge results with a reducer, route low-confidence lines to a human gate, then a final aggregation node. Use a cheap model, cache repeated descriptions, and a checkpointer so a failure resumes without redoing finished lines.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The task needs branching, tools, loops, review or parallel work

❌ Avoid when:
- One prompt or a linear chain is enough
- Latency budget is tiny (every extra LLM hop adds seconds)

---

## 📊 Visual Diagram
```
 ROUTER             ReAct LOOP               REFLECTION
 in ─► route ─► A   agent ─► tool? ─yes─► tools     gen ─► critic ─ok─► END
          ├───► B     ▲        │no                   ▲        │bad
          └───► C     └────────┘ ► END               └─revise─┘ (max N)

 FAN-OUT/IN                          HUMAN GATE
      ┌► node1 ┐                      classify ─► [interrupt] ─► human ─► file
 in ──┼► node2 ┼─► merge(reducer)
      └► node3 ┘
```

---

## 💰 Cost Impact
Each loop iteration is another LLM call, and message history grows, so cost grows faster than linearly in a ReAct loop (each step re-sends the history). Illustration: a 5-step loop with 800 tokens of history growing by 300 per step sends about 800+1100+1400+1700+2000 = 7,000 input tokens. Optimise: cap steps, trim/summarise history, use a cheap model for routing, parallelise independent work (latency, not tokens), cache tool results and repeated questions, and prefer a router + fixed chain over a free-roaming agent when possible.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Router | Picks the path | रास्ता चुनने वाला |
| ReAct | Reason + Act loop | सोचो + करो loop |
| Reflection | Self-critique and revise | खुद की जाँच और सुधार |
| Fan-out / fan-in | Parallel split and merge | समानांतर बाँटना और जोड़ना |
| Send API | Dynamic parallel branches | Dynamic parallel branches |
| Supervisor | Router agent over workers | Workers का मैनेजर agent |
| Human gate | Pause for approval | मंज़ूरी के लिए रुकना |

---

## ⚡ 3-Line Summary
English: Learn the standard shapes: router, ReAct loop, reflection, plan-and-execute, fan-out/in, human gate. Choose the simplest one that fits and always cap loops. Parallel branches need reducers.
Hindi: मानक आकार सीखो: router, ReAct loop, reflection, plan-and-execute, fan-out/in, human gate। जो सबसे सरल फिट हो वही चुनो और loops हमेशा सीमित रखो। Parallel branches के लिए reducers चाहिए।

---

## ➡️ Next Topic
**344. LangGraph for RAG** — applying the router, retrieve and reflect patterns to retrieval-augmented generation.
