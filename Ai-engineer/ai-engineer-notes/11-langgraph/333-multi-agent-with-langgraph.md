---

# 333. Multi-Agent with LangGraph
# हिंदी में: LangGraph के साथ Multi-Agent

---

## 🔵 Simple Definition (English)
A multi-agent system splits a big job between several small agents, each with its own prompt, tools and responsibility (for example a "classifier", a "legal checker" and a "writer"). In LangGraph each agent is a node (or a sub-graph) and the edges decide who works next. All agents share one state, so they can see each other's results.

## 🔵 सरल परिभाषा (Hindi)
Multi-agent system एक बड़े काम को कई छोटे agents में बाँटता है, हर agent का अपना prompt, tools और ज़िम्मेदारी होती है (जैसे "classifier", "legal checker", "writer")। LangGraph में हर agent एक node (या sub-graph) होता है और edges तय करते हैं कि अगला कौन काम करेगा। सब agents एक shared state use करते हैं, इसलिए एक-दूसरे के results देख सकते हैं।

---

## 🔴 Problem it Solves
One agent with 25 tools and a 3,000-token prompt gets confused: it picks wrong tools, forgets instructions and is hard to test. Mixing unrelated skills in one prompt lowers quality. Separate agents give focused prompts, fewer tools per agent, independent testing, and different models per job (cheap model for routing, strong model for legal reasoning).

## 🔴 यह क्यों बना? (Hindi)
25 tools और 3,000-token prompt वाला एक agent confuse हो जाता है: गलत tool चुनता है, instructions भूलता है और test करना कठिन होता है। असंबंधित skills को एक prompt में मिलाने से quality गिरती है। अलग agents से focused prompts, कम tools, independent testing और काम के हिसाब से अलग model (routing के लिए सस्ता, legal reasoning के लिए मज़बूत) मिलते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decide the roles (classifier, legal_checker, writer)
Step 2 → Define one shared State (messages + fields like hs_code, findings)
Step 3 → Implement each agent as a node: reads state, calls LLM/tools, returns a partial update
Step 4 → Choose a coordination pattern: supervisor (334), swarm (335), pipeline, or parallel
Step 5 → Wire edges / Command(goto=...) so control passes between agents
Step 6 → Add a checkpointer, recursion limit and a max-steps guard
Step 7 → Compile and run; trace in LangSmith to see who did what
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Roles तय करो (classifier, legal_checker, writer)
Step 2 → एक shared State बनाओ (messages + hs_code, findings जैसे fields)
Step 3 → हर agent एक node: state पढ़ता है, LLM/tools call करता है, partial update देता है
Step 4 → Coordination pattern चुनो: supervisor (334), swarm (335), pipeline, या parallel
Step 5 → Edges / Command(goto=...) से control agents के बीच पास करो
Step 6 → Checkpointer, recursion limit और max-steps guard जोड़ो
Step 7 → Compile करो और चलाओ; LangSmith में trace देखो कि किसने क्या किया
```

---

## 🟡 Real World Example
**Tariff Classification System**: three agents. (1) `classifier` proposes an HS code from the product description. (2) `legal_checker` verifies the code against import restrictions and notes. (3) `writer` produces the final customs-ready explanation. If the legal checker rejects the code, control goes back to the classifier with feedback. **Amazon AI**: one agent handles returns, another handles shipping, a third handles payments.

## 🟡 Real Example Hindi mein
**Tariff System**: तीन agents। (1) `classifier` product description से HS code सुझाता है। (2) `legal_checker` code को import restrictions और notes से verify करता है। (3) `writer` customs-ready final explanation लिखता है। Legal checker code reject करे तो feedback के साथ control वापस classifier को जाता है। **Amazon AI**: एक agent returns, दूसरा shipping, तीसरा payments संभालता है।

---

## 💻 Code Example — Basic
```python
# Three cooperating "agents" in one graph - runs offline (pip install langgraph)
from typing import TypedDict  # state typing

from langgraph.graph import END, START, StateGraph  # graph API


class State(TypedDict):  # shared state all agents read/write
    product: str  # input
    hs_code: str  # written by classifier
    legal_ok: bool  # written by legal_checker
    report: str  # written by writer


def classifier(state: State) -> dict:  # agent 1 (a real one would call an LLM)
    code = "8517.13" if "phone" in state["product"] else "9999.00"  # fake decision
    return {"hs_code": code}  # write result into shared state


def legal_checker(state: State) -> dict:  # agent 2 reads agent 1's output
    return {"legal_ok": state["hs_code"] != "9999.00"}  # reject unknown codes


def writer(state: State) -> dict:  # agent 3 composes the final text
    status = "approved" if state["legal_ok"] else "needs review"  # choose wording
    return {"report": f"{state['product']}: {state['hs_code']} ({status})"}  # final report


def after_legal(state: State) -> str:  # router: retry classification or write
    return "writer" if state["legal_ok"] else END  # stop early when illegal


builder = StateGraph(State)  # builder
for name, fn in [("classifier", classifier), ("legal_checker", legal_checker), ("writer", writer)]:  # register nodes
    builder.add_node(name, fn)  # add each agent
builder.add_edge(START, "classifier")  # start with the classifier
builder.add_edge("classifier", "legal_checker")  # then the checker
builder.add_conditional_edges("legal_checker", after_legal, ["writer", END])  # branch after checking
builder.add_edge("writer", END)  # finish
graph = builder.compile()  # compile

print(graph.invoke({"product": "smart phone", "hs_code": "", "legal_ok": False, "report": ""}))  # full pipeline
print(graph.invoke({"product": "mystery", "hs_code": "", "legal_ok": False, "report": ""}))  # stops after checker
```

## 💻 Code Example — Advanced
```python
# Feedback loop between agents, step cap, timeouts, async, error isolation
import asyncio  # async + timeout
from typing import Annotated, Literal, TypedDict  # typing
import operator  # list reducer

from langgraph.graph import END, START, StateGraph  # graph API


class State(TypedDict):  # shared state
    product: str  # input
    hs_code: str  # current proposal
    feedback: Annotated[list[str], operator.add]  # accumulated critiques
    approved: bool  # legal verdict
    steps: int  # global guard against endless ping-pong


async def classifier(state: State) -> dict:  # agent 1
    await asyncio.sleep(0)  # stands in for LLM call
    attempt = len(state["feedback"])  # more feedback -> better answer (fake)
    code = "8517.13" if attempt >= 1 else "8471.30"  # first guess wrong, second right
    return {"hs_code": code, "steps": state["steps"] + 1}


async def legal_checker(state: State) -> dict:  # agent 2
    try:
        async with asyncio.timeout(5):  # per-agent timeout (Python 3.11+)
            await asyncio.sleep(0)  # stands in for tool call
            ok = state["hs_code"] == "8517.13"  # fake rule
    except TimeoutError:  # slow dependency
        return {"approved": False, "feedback": ["legal service timeout"], "steps": state["steps"] + 1}
    if ok:
        return {"approved": True, "steps": state["steps"] + 1}  # pass
    return {"approved": False, "feedback": [f"{state['hs_code']} is a computer, not a phone"], "steps": state["steps"] + 1}


def route(state: State) -> Literal["classifier", "__end__"]:  # loop controller
    if state["approved"] or state["steps"] >= 6:  # success OR step cap hit
        return END
    return "classifier"  # ask classifier to try again with feedback


builder = StateGraph(State)  # builder
builder.add_node("classifier", classifier)  # node
builder.add_node("legal_checker", legal_checker)  # node
builder.add_edge(START, "classifier")  # entry
builder.add_edge("classifier", "legal_checker")  # always check
builder.add_conditional_edges("legal_checker", route)  # loop or end
graph = builder.compile()  # compile


async def main() -> None:
    out = await graph.ainvoke(
        {"product": "phone", "hs_code": "", "feedback": [], "approved": False, "steps": 0},
        config={"recursion_limit": 15},  # extra safety net
    )
    print(out["hs_code"], out["approved"], out["feedback"])  # 8517.13 True [one critique]


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Run the multi-agent graph behind a single endpoint, and return which agents ran so you can debug. Use `astream` with `stream_mode="updates"` to collect the agent trail.

```python
from fastapi import FastAPI, HTTPException  # web
from pydantic import BaseModel  # validation

app = FastAPI()  # app


class Req(BaseModel):  # request
    product: str


@app.post("/classify")
async def classify(req: Req) -> dict[str, object]:  # route
    trail: list[str] = []  # which agents ran
    final: dict = {}  # last merged state values
    try:
        async for update in graph.astream(  # stream node-by-node
            {"product": req.product, "hs_code": "", "feedback": [], "approved": False, "steps": 0},
            stream_mode="updates",  # one dict per node: {node_name: partial_update}
        ):
            for node, delta in update.items():  # usually one key
                trail.append(node)  # record agent name
                final.update(delta)  # accumulate latest values
    except Exception as exc:  # agent crashed
        raise HTTPException(status_code=502, detail=f"agent failure: {exc}")
    return {"hs_code": final.get("hs_code"), "approved": final.get("approved"), "trail": trail}
```

---

## 🔗 LangChain / LangGraph Connection
Each agent is usually a LangChain runnable (prompt | model | parser) or a prebuilt ReAct agent used as a node. LangGraph provides ready-made patterns: `langgraph-supervisor` (`create_supervisor`) and `langgraph-swarm` (`create_swarm`) as add-on packages, but understanding the hand-built version (topics 334-336) is what interviews ask.

```python
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_openai import ChatOpenAI  # model

classifier_chain = (  # LCEL chain used inside the classifier node
    ChatPromptTemplate.from_template("Give only the HS code for: {product}")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
)


def classifier_node(state: dict) -> dict:  # node wraps the chain
    return {"hs_code": classifier_chain.invoke({"product": state["product"]}).content}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Agents with overlapping responsibilities
✅ Correct: One clear job per agent; document inputs and outputs in state.

```python
# Wrong - both agents classify AND validate, they argue forever
def agent_a(state): ...  # "classify and validate"
def agent_b(state): ...  # "validate and classify"

# Right - single responsibility
def classifier(state): ...   # only proposes hs_code
def legal_checker(state): ... # only approves / rejects
```

❌ Mistake 2: No exit condition between agents (ping-pong)
✅ Correct: Count steps in state and set `recursion_limit`.

```python
# Wrong
builder.add_conditional_edges("legal_checker", lambda s: "classifier")  # loops forever

# Right
def route(s):
    return END if s["approved"] or s["steps"] >= 6 else "classifier"
```

---

## 🧠 Tricky Interview Question

**Q**: "You split one agent into five, and quality improved but cost tripled and latency doubled. Was multi-agent the right call?"

**Answer**: Not automatically. Every extra agent adds an LLM call plus repeated context (each agent re-reads shared messages). Keep multi-agent only where specialisation gives measurable gains. Reduce cost by: (1) passing agents only the fields they need, not the full message history, (2) using cheaper models for routing and formatting agents, (3) running independent agents in parallel, (4) merging agents that always run together, (5) replacing LLM routers with rules. Measure with an eval set: accuracy gain per extra dollar.

---

## ⚫ Interview Questions + Answers

Q1: What is a multi-agent system? (Easy)
A1: Several focused agents (each with own prompt and tools) cooperating on one task, usually through shared state and a coordination pattern.

Q2: How do agents share information in LangGraph? (Easy)
A2: Through the shared graph state; each node reads fields and returns partial updates, merged by reducers.

Q3: Name the main coordination patterns. (Medium)
A3: Pipeline (fixed sequence), supervisor (a central LLM routes to workers), swarm (agents hand off to each other directly), hierarchical (supervisors of supervisors), and parallel fan-out/fan-in.

Q4: How do you prevent infinite loops between agents? (Medium)
A4: A step counter in state with a router that ends or escalates, `recursion_limit` in config, per-agent timeouts, and tests that simulate permanent disagreement.

Q5: How would you evaluate and debug a multi-agent system in production? (Hard)
A5: Trace each run (LangSmith) to see node order, inputs, outputs and tokens per agent. Build an offline dataset with expected outputs and score end-to-end plus per-agent metrics. Replay failing threads from checkpoints. Track cost, latency and loop counts per agent, and alert on step-cap hits.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Distinct skills/tools need distinct prompts
- Different models are best for different steps
- You need review/critique loops between roles

❌ Avoid when:
- A single prompt with 2-3 tools already works well
- Latency and cost budgets are tight
- The "agents" are really just sequential functions (use a plain pipeline)

---

## 📊 Visual Diagram
```
                 ┌─────────────── shared State ───────────────┐
                 │ product | hs_code | feedback[] | approved   │
                 └──────▲──────────────▲─────────────▲────────┘
                        │              │             │
START ─► [classifier] ─►[legal_checker]─ approved? ─► [writer] ─► END
              ▲                │ no
              └── feedback ────┘   (max N loops)
```

---

## 💰 Cost Impact
- Cost = sum of tokens in every agent call. Three agents of ~800 tokens each = ~2,400 tokens per request, about $0.0004 with `gpt-4o-mini` at mixed pricing, versus ~$0.01 if all three used `gpt-4o`.
- Loops multiply cost: a 3-round critique loop is 3x the classifier + checker tokens.
- Optimise: pass minimal context per agent, small model for routing/formatting, parallelise independent agents (cuts latency, not tokens), cache repeated lookups, and cap loops.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Agent | LLM + prompt + tools with one job | एक काम वाला LLM agent |
| Shared state | State all agents read/write | सबका साझा state |
| Orchestration | Controlling who runs when | कौन कब चले, इसका नियंत्रण |
| Fan-out / fan-in | Run in parallel, then merge | Parallel चलाकर merge करना |
| Step cap | Max iterations guard | अधिकतम steps की सीमा |
| Specialisation | Narrow, focused role | विशेष भूमिका |

---

## ⚡ 3-Line Summary
English: Multi-agent splits work among focused agents that share one LangGraph state. Edges or `Command` decide who acts next. Use it only when specialisation beats the extra cost, and always cap loops.
Hindi: Multi-agent में काम focused agents में बँटता है जो एक LangGraph state share करते हैं। Edges या `Command` तय करते हैं कि अगला कौन करेगा। तभी use करो जब specialisation extra cost से ज़्यादा फायदा दे, और loops हमेशा सीमित रखो।

---

## ➡️ Next Topic
**334. Supervisor Pattern** — one central agent that decides which worker agent runs next and when to finish.
