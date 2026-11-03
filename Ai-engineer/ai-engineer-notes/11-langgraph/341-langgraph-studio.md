
---

# 341. LangGraph Studio
# हिंदी में: LangGraph Studio — Graph को देखने और Debug करने का Tool

---

## 🔵 Simple Definition (English)
LangGraph Studio is a visual IDE for LangGraph apps. It draws your graph, lets you run it, watch each node's input and output, edit state, replay from a past step and pause at breakpoints. You start a local LangGraph dev server and open Studio against it.

## 🔵 सरल परिभाषा (Hindi)
LangGraph Studio LangGraph apps के लिए visual IDE है। यह graph की तस्वीर बनाता है, run करने देता है, हर node का input-output दिखाता है, state edit करने, पुराने step से replay करने और breakpoints पर रुकने देता है। आप local LangGraph dev server चलाते हैं और Studio उससे जुड़ता है।

---

## 🔴 Problem it Solves
Debugging an agent with `print` is painful: you cannot see which branch ran, what the state looked like at step 4, or how a different input would behave. Studio turns the run into a visual timeline so you can find a bad router decision in seconds and re-run from that step without starting over.

## 🔴 यह क्यों बना? (Hindi)
Agent को `print` से debug करना कठिन है: कौन सी branch चली, step 4 पर state कैसी थी, पता नहीं चलता। Studio run को visual timeline बना देता है, खराब router decision सेकंडों में मिल जाता है और उसी step से दोबारा run कर सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Put your compiled graph in a Python module (e.g. agent.py: graph = builder.compile())
Step 2 → Create langgraph.json that points to the graph and your .env file
Step 3 → Install the CLI: pip install -U "langgraph-cli[inmem]"
Step 4 → Run: langgraph dev  (starts a local API server with hot reload)
Step 5 → Open Studio (LangSmith web UI connects to http://127.0.0.1:2024)
Step 6 → Submit an input, watch nodes light up, inspect state at every step
Step 7 → Edit state or a node's output, fork, or replay from an earlier checkpoint
Step 8 → Add interrupts (breakpoints) to pause before sensitive nodes
Step 9 → Fix code (hot reload) and re-run the same thread
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Compiled graph को Python module में रखो (agent.py: graph = builder.compile())
Step 2 → langgraph.json बनाओ जो graph और .env की ओर इशारा करे
Step 3 → CLI install: pip install -U "langgraph-cli[inmem]"
Step 4 → चलाओ: langgraph dev  (local API server, hot reload के साथ)
Step 5 → Studio खोलो (LangSmith web UI http://127.0.0.1:2024 से जुड़ता है)
Step 6 → Input दो, nodes चलते देखो, हर step पर state inspect करो
Step 7 → State या node output edit करो, fork करो, पुराने checkpoint से replay करो
Step 8 → संवेदनशील nodes से पहले interrupt (breakpoint) लगाओ
Step 9 → Code ठीक करो (hot reload) और उसी thread पर दोबारा चलाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: a customs officer reports "this laptop got a footwear code". In Studio the engineer loads the saved thread, sees that `retrieve_rules` returned chapter 64 chunks, edits the retrieved context to chapter 84, re-runs `classify`, and confirms the retriever is the culprit, not the LLM.

**Amazon-style**: a support-bot graph is debugged by replaying a failed refund conversation from the step where the router chose "FAQ" instead of "refund".

## 🟡 Real Example Hindi mein
**Tariff System**: Officer बताता है "laptop को footwear code मिला"। Studio में engineer saved thread खोलता है, देखता है कि `retrieve_rules` ने chapter 64 के chunks दिए, context को chapter 84 से बदलकर `classify` दोबारा चलाता है और पक्का करता है कि गलती retriever की थी, LLM की नहीं।

**Amazon-style**: Refund conversation को उस step से replay करना जहाँ router ने "refund" की जगह "FAQ" चुना।

---

## 💻 Code Example — Basic
```python
# Basic: generate the langgraph.json config and a tiny graph module, using pure Python file writes
import json  # to write the config
from pathlib import Path  # for paths

# langgraph.json tells the CLI where the graph object lives and which env file to load
config = {
    "dependencies": ["."],                      # install the current project
    "graphs": {"tariff": "./agent.py:graph"},   # graph name -> module path:variable
    "env": ".env",                              # API keys loaded from here
}
Path("langgraph.json").write_text(json.dumps(config, indent=2))  # write the config file

# agent.py content (kept as a string here; in a real repo you create the file directly)
agent_py = '''
from typing import TypedDict
from langgraph.graph import StateGraph, END

class S(TypedDict):
    desc: str
    code: str

def classify(s: S) -> dict:
    return {"code": "8518.30"}  # stub node so Studio has something to show

b = StateGraph(S)
b.add_node("classify", classify)
b.set_entry_point("classify")
b.add_edge("classify", END)
graph = b.compile()  # Studio imports this variable
'''
Path("agent.py").write_text(agent_py)  # write the module
print(Path("langgraph.json").read_text())  # show the config
# Then in a terminal:  langgraph dev
```

## 💻 Code Example — Advanced
```python
# Production: a Studio-friendly graph with a breakpoint (interrupt) and a config schema
# Studio builds a form from the graph's config_schema so non-developers can switch models.
from typing import TypedDict  # typing

from langgraph.checkpoint.memory import MemorySaver  # checkpointer (Studio/dev server also manages persistence)
from langgraph.graph import END, StateGraph  # graph API

class State(TypedDict):
    desc: str      # input
    code: str      # candidate code
    approved: bool # set by a human in Studio

class Config(TypedDict, total=False):
    model: str  # shown as an editable field in Studio

def classify(state: State, config: dict | None = None) -> dict:
    """Pick the model from config (default small model) and classify."""
    cfg = (config or {}).get("configurable", {})  # read configurable values
    model = cfg.get("model", "gpt-4o-mini")  # default model name
    return {"code": f"8518.30 (via {model})"}  # stub result; replace with a real LLM call

def submit(state: State) -> dict:
    """Side-effecting node: pretend to file the declaration."""
    if not state.get("approved"):  # guard in case someone resumes without approval
        raise ValueError("not approved")  # fail loudly
    return {}  # filed

builder = StateGraph(State, config_schema=Config)  # attach config schema
builder.add_node("classify", classify)  # node
builder.add_node("submit", submit)  # node
builder.set_entry_point("classify")  # start
builder.add_edge("classify", "submit")  # flow
builder.add_edge("submit", END)  # end

# interrupt_before pauses before "submit": in Studio you inspect state, set approved=True, then continue.
graph = builder.compile(checkpointer=MemorySaver(), interrupt_before=["submit"])
# Note: with `langgraph dev` the server supplies its own persistence; passing a checkpointer
# is needed when you run the same file standalone. Check the current docs for your version.
```

---

## 🟠 FastAPI Integration
Studio is for development, not for production traffic. But the same graph file powers your FastAPI app, so what you debug in Studio is what you serve. A tiny route also lets you replay a thread id that you found in Studio.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # schema
from agent import graph  # the SAME compiled graph Studio uses

app = FastAPI()  # app

class Req(BaseModel):
    thread_id: str  # reuse an id you saw in Studio to reproduce a bug
    description: str  # input text

@app.post("/classify")
async def classify(req: Req) -> dict:
    """Run the same graph that Studio debugs."""
    out = await graph.ainvoke(
        {"desc": req.description, "code": "", "approved": False},  # input state
        {"configurable": {"thread_id": req.thread_id}},  # same thread -> same history
    )
    return {"code": out["code"]}  # response
```

---

## 🔗 LangChain / LangGraph Connection
Studio is part of the LangChain ecosystem and connects to LangSmith: runs started from Studio create traces you can open in LangSmith, add to datasets, and evaluate. Set `LANGSMITH_API_KEY` (and optionally `LANGSMITH_TRACING=true`) in your `.env`.

```python
# .env used by langgraph dev
# LANGSMITH_API_KEY=lsv2_...        # lets Studio/tracing link to your LangSmith workspace
# LANGSMITH_TRACING=true            # send traces
# OPENAI_API_KEY=sk-...             # your model key
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Wrong graph path in langgraph.json
✅ Correct: Use `./file.py:variable` pointing to a compiled graph.
```python
# Wrong: "graphs": {"tariff": "./agent.py"}        # missing :variable
# Right: "graphs": {"tariff": "./agent.py:graph"}  # graph = builder.compile()
```

❌ Mistake 2: Exporting the builder, not the compiled graph
✅ Correct: Call `.compile()`.
```python
# Wrong: graph = StateGraph(S)          # not runnable
# Right: graph = builder.compile()
```

❌ Mistake 3: Debugging with real customer data
✅ Correct: Use sanitized test data, because traces may be sent to LangSmith.

---

## 🧠 Tricky Interview Question

**Q**: "A bug only appears after step 7 of a 12-step run that costs money each time. How do you debug efficiently?"

**Answer**: Use checkpoints. Load the thread in Studio (or fetch its state history), select the checkpoint just before step 7, optionally edit state, and fork/replay from there. Earlier steps are not re-executed so tokens are saved, and you can compare outputs between the original and the forked run. Add a breakpoint with `interrupt_before` on the suspicious node for repeated inspection.

---

## ⚫ Interview Questions + Answers

Q1: What is LangGraph Studio?
A1: A visual IDE to run, inspect, edit and replay LangGraph graphs.

Q2: What command starts the local server?
A2: `langgraph dev` from the langgraph-cli package.

Q3: What does langgraph.json contain?
A3: Dependencies, a mapping of graph names to `file:variable`, and the env file path.

Q4: What is time travel in Studio?
A4: Choosing a past checkpoint, optionally editing state, and re-running from there as a new branch.

Q5: How do Studio, LangSmith and production deployment fit together?
A5: Develop and debug locally in Studio with `langgraph dev`; traces go to LangSmith for evaluation; the same graph code is deployed as an API (self-hosted container or LangGraph Platform) and served to your FastAPI/front-end. Studio is not part of the request path.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Graphs have branches, loops or human review
- You need to show non-developers how the agent decides

❌ Avoid when:
- Single-call apps with no graph
- Data is too sensitive to be traced externally (use local-only settings or self-hosting)

---

## 📊 Visual Diagram
```
 your code ──► agent.py:graph ──► langgraph dev (localhost:2024)
                                      ▲   │ hot reload
          browser: Studio UI ─────────┘   ▼
   [graph view] [state per step] [edit state] [replay/fork] [breakpoints]
                                      │
                                      └──► LangSmith traces (optional)
```

---

## 💰 Cost Impact
Studio itself is a dev tool, but every run you start in it calls your real LLM, so it costs tokens. Replaying from a checkpoint avoids re-paying for earlier steps. Use a cheap model and short test inputs while debugging, and use stubs for expensive nodes. Pricing and plan limits of LangSmith features can change, so check the current pricing page. Token usage: a 5-node graph with 500 tokens per node is about 2,500 tokens per full run; replaying only the last 2 nodes is about 1,000.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Studio | Visual IDE for graphs | Graphs का visual IDE |
| langgraph dev | Local dev server command | Local dev server चलाने की command |
| langgraph.json | Config for CLI/Studio | CLI/Studio की config |
| Checkpoint | Saved state snapshot | State का saved snapshot |
| Breakpoint / interrupt | Pause before a node | Node से पहले रुकना |
| Fork / replay | Re-run from a past step | पुराने step से दोबारा चलाना |
| Hot reload | Auto-reload on code change | Code बदलते ही auto reload |

---

## ⚡ 3-Line Summary
English: Studio visualises and debugs LangGraph runs with state inspection, editing, replay and breakpoints. Start it with `langgraph dev` and a `langgraph.json` pointing at your compiled graph. It is for development; production serves the same graph via an API.
Hindi: Studio LangGraph runs को visualise और debug करता है: state inspect, edit, replay और breakpoints। `langgraph dev` और compiled graph की ओर इशारा करने वाली `langgraph.json` से शुरू करो। यह development के लिए है; production में वही graph API से serve होता है।

---

## ➡️ Next Topic
**342. LangGraph Cloud** — deploying the graph as a managed, scalable API with built-in persistence.
