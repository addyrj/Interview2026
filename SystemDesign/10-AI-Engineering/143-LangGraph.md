# 143. LangGraph
# हिंदी में: LangGraph — LLM agents और workflows को graph (nodes + edges) की तरह बनाने का framework: साझा state, शर्तों वाले रास्ते, loops (agent का tool चक्र), हर कदम पर checkpoint (रुककर बाद में आगे), और इंसान की मंज़ूरी के लिए बीच में रुकना (interrupt)

---

## 🔵 Simple Definition (English)
**LangGraph** is a framework (Python and JS, from the LangChain team) for building **stateful, controllable LLM applications as graphs**:
- **State**: a typed object (e.g., `TypedDict`) shared across the graph, with **reducers** defining how updates merge (e.g., `messages` appended via `add_messages`).
- **Nodes**: functions (LLM calls, tool execution, retrieval, business logic) that read state and return updates.
- **Edges**: normal edges (A → B) and **conditional edges** (route based on state, e.g., "if the model requested tools, go to the tools node; else END"). Cycles are allowed, which is what lets an **agent loop** be built.
- **Checkpointers** (in-memory, SQLite, **Postgres**, Redis): persist state after every step per **thread** (conversation), enabling **memory across turns, crash recovery, resuming long-running tasks and time travel** (inspect or replay earlier states).
- **Human-in-the-loop**: `interrupt()` pauses execution (e.g., before issuing a refund), and you resume with a human decision via `Command(resume=…)`.
- **Streaming** of state updates, tokens and events. Subgraphs support modular and multi-agent designs, and prebuilt helpers (`ToolNode`, ReAct agents) cover common patterns.
It gives **explicit control flow** instead of opaque agent loops, which matters for production reliability.

## 🔵 सरल परिभाषा (Hindi)
LangGraph = LLM ऐप को graph की तरह बनाना: State (पूरे graph में साझा typed डेटा, reducers से बदलाव जुड़ते हैं — जैसे messages जुड़ते जाएँ), Nodes (LLM call, tool चलाना, retrieval, business logic), Edges (सीधे A → B या शर्त वाले — "model ने tool माँगा तो tools node, वरना END"; loops की अनुमति = agent चक्र), Checkpointers (Postgres आदि में हर कदम के बाद state save — हर बातचीत की याद, crash के बाद वापसी, लंबे काम फिर से शुरू, पुराने states देखना), Human-in-the-loop (`interrupt()` से रुककर, जैसे refund से पहले, इंसान के फ़ैसले से `Command(resume=…)`), streaming, subgraphs।
अपारदर्शी agent loops की जगह साफ़ control flow — production के लिए ज़रूरी।

---

## 🔴 Problem it Solves
Simple chains are linear, while real assistants need:
- **Branching**: route a support query to the RAG path, the order-tools path or a human, based on classification.
- **Loops**: an agent calls tools repeatedly until done, with limits.
- **Memory and persistence**: continue the same conversation tomorrow, or resume a 10-minute research task after a pod restart.
- **Approvals**: pause before refunding ₹2,000 or emailing a customer, wait hours for a supervisor, then continue exactly where it left off.
- **Observability and debugging**: see each step's state, replay from a checkpoint, fix and retry.
Hand-rolled `while` loops with ad-hoc state dictionaries become unmaintainable and fragile. LangGraph makes the **control flow explicit (a state machine)**, durable and inspectable, a natural fit for production agents and multi-step workflows.

## 🔴 यह क्यों बना? (Hindi)
साधारण chains सीधी लाइन होती हैं, पर असली सहायकों को चाहिए: शाखाएँ (classification से RAG, order tools या इंसान), loops (agent बार-बार tools, सीमा के साथ), याद और स्थायित्व (कल वही बातचीत आगे, pod restart के बाद 10 मिनट का काम फिर शुरू), मंज़ूरी (₹2,000 refund या ग्राहक को email से पहले रुको, supervisor का घंटों इंतज़ार, फिर ठीक वहीं से आगे), और हर कदम का state देखना/दोबारा चलाना।
हाथ से लिखे `while` loops और मनमाने state dict जल्दी उलझ जाते हैं; LangGraph control flow को साफ़ state machine बनाता है — टिकाऊ और जाँचने लायक।

---

## 🟢 How it Works — Step by Step

### Graph anatomy (support assistant)

```
            ┌────────────┐
 START ───► │  classify  │ ── intent = FAQ ─────────────► ┌──────────┐
            └────────────┘ ── intent = ORDER/PAYMENT ──┐  │   rag    │ ──► END
                         └── intent = ABUSE ──► END    │  └──────────┘
                                                       ▼
                                                ┌────────────┐  tool calls?  ┌──────────┐
                                                │   agent    │ ────yes─────► │  tools   │
                                                │ (LLM+tools)│ ◄──────────── │(ToolNode)│
                                                └────────────┘               └──────────┘
                                                       │ wants refund > ₹500
                                                       ▼
                                                ┌──────────────┐  interrupt() → wait for supervisor
                                                │ human_review │  resume(approved/denied)
                                                └──────────────┘ ──► agent ──► END
State: {messages: [...], intent, user_id, order_id?, pending_refund?, steps}
Checkpointer: PostgresSaver → state saved after every node, keyed by thread_id (conversation id)
```

### Key concepts

```
StateGraph(State)         : define graph over a typed state
add_node(name, fn)        : fn(state) → partial state update (dict)
add_edge(a, b)            : unconditional transition
add_conditional_edges(a, router_fn, {label: node})  : branching / loops
START / END               : entry & exit
compile(checkpointer=...) : runnable graph with persistence
invoke/stream(input, config={"configurable": {"thread_id": "conv-123"}})
Reducers: Annotated[list, add_messages] → append messages instead of overwrite
interrupt(value)          : pause & surface value to caller; resume with Command(resume=decision)
Recursion limit           : max steps per run (loop guard), configurable
```

### Persistence & memory

```
Thread = one conversation/task; checkpoints = snapshots after each step
Short-term memory: messages in thread state (trim/summarize to control tokens)
Long-term memory: a separate store across threads (user preferences, facts) (Topic 145)
Durability: worker crashes mid-run → resume from last checkpoint (idempotent nodes!)
Time travel: list checkpoints → inspect → re-run from an earlier checkpoint with edits (debugging)
```

### Production considerations

```
- Make nodes idempotent (they may re-run after failures); side effects via idempotency keys
- Bound loops (recursion_limit, step counters in state), timeouts per node
- Keep state small & serializable (ids, summaries, not huge documents)
- Separate deterministic nodes (code) from LLM nodes; test nodes independently
- Stream updates to UI ("Checking your order…", "Waiting for approval")
- Deploy as a service (FastAPI wrapper or LangGraph Platform/Server); observe with LangSmith/OTel
```

## 🟢 कैसे काम करता है? (Hindi)
1. Graph: START → classify node → intent के हिसाब से: FAQ तो rag node → END; order/payment तो agent node (LLM + tools) ↔ tools node का loop; ₹500 से बड़ा refund तो human_review node पर `interrupt()` — supervisor के फ़ैसले से resume; abuse तो END।
2. State (messages, intent, user_id, order_id, pending_refund, steps) हर node पढ़ता और हिस्सा लौटाता है; `add_messages` reducer messages जोड़ता है; `add_conditional_edges` से शाखाएँ और loops; `recursion_limit` से loop सीमा।
3. Checkpointer (PostgresSaver) हर node के बाद thread_id (बातचीत) के हिसाब से state save — बातचीत की याद, crash के बाद आख़िरी checkpoint से आगे, पुराने checkpoints देखकर दोबारा चलाना (debugging); लंबी याद अलग store में।
4. Human-in-the-loop: `interrupt(value)` पर graph रुकता है और value (जैसे refund विवरण) बाहर देता है; घंटों बाद `Command(resume={"approved": True})` से वहीं से आगे।
5. Production: nodes idempotent (दोबारा चल सकते हैं), loops सीमित, state छोटा, deterministic और LLM nodes अलग और अलग से test, UI को updates stream ("order देख रहे हैं…", "मंज़ूरी का इंतज़ार"), FastAPI या LangGraph Platform पर deploy, LangSmith/OTel से निगरानी।

---

## 🟡 Real World Example

**LangGraph adoption (2024–2025)** — the LangChain team introduced LangGraph to address the limits of earlier opaque agent executors. It became their recommended way to build agents, and companies have publicly described using it for customer support agents, coding assistants and internal copilots needing persistence and human approval.

**Human-in-the-loop in regulated workflows** — banks, insurers and healthcare companies require human approval for actions such as refunds above thresholds, account changes or clinical summaries. Graph-based orchestration with interrupts and checkpoints maps cleanly to these maker-checker processes, familiar in Indian banking operations.

**Durable execution trend** — similar ideas appear in Temporal workflows, AWS Step Functions and agent platforms: explicit state, retries, persistence and resumability, applied to LLM agents so long tasks survive failures.

**Anthropic's "Building effective agents" patterns** — routing, prompt chaining, orchestrator-workers and evaluator-optimizer loops are naturally expressed as LangGraph graphs, which is why the two are often discussed together.

## 🟡 Real Example Hindi में
LangChain टीम ने पुराने अपारदर्शी agent executors की कमियों के जवाब में LangGraph लाया — अब agents बनाने का उनका सुझाया तरीका; कंपनियाँ इसे support agents, coding assistants और internal copilots के लिए इस्तेमाल बताती हैं जहाँ याद और मंज़ूरी चाहिए।
बैंक/insurance/healthcare में तय सीमा से बड़े refund या खाते के बदलाव पर इंसान की मंज़ूरी ज़रूरी — interrupts और checkpoints वाला graph भारतीय बैंकों के maker-checker तरीके से मेल खाता है; यही विचार Temporal, AWS Step Functions में भी — explicit state, retries, persistence।

---

## 🟠 My Stack Example

### Support graph with routing, tool loop, human approval and Postgres checkpoints (Python)
```python
# pip install langgraph langgraph-checkpoint-postgres langchain-anthropic
from typing import Annotated, TypedDict, Literal, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt, Command
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_anthropic import ChatAnthropic

class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str
    intent: Optional[Literal["FAQ", "ORDER", "ABUSE"]]
    pending_refund: Optional[dict]

tools = [get_order_status, get_refund_status, propose_refund]     # @tool functions; authz inside
llm = ChatAnthropic(model="claude-sonnet-5-5", temperature=0.1).bind_tools(tools)
router_llm = ChatAnthropic(model="claude-haiku-5-5", temperature=0).with_structured_output(IntentSchema)

def classify(state: State):
    return {"intent": router_llm.invoke(state["messages"][-1].content).intent}

def rag(state: State):
    return {"messages": [("assistant", rag_chain.invoke(state["messages"][-1].content))]}   # Topic 142 chain → text

def agent(state: State):
    return {"messages": [llm.invoke([SUPPORT_SYSTEM_MSG, *state["messages"]])]}

def after_tools(state: State):
    # propose_refund tool writes a pending refund into its tool result; detect & route to approval if large
    pr = extract_pending_refund(state["messages"][-1])
    return {"pending_refund": pr} if pr else {}

def needs_approval(state: State) -> Literal["human_review", "agent"]:
    pr = state.get("pending_refund")
    return "human_review" if pr and pr["amount_paise"] > 50_000 else "agent"

def human_review(state: State):
    decision = interrupt({"type": "REFUND_APPROVAL", "refund": state["pending_refund"]})   # ⏸ wait for supervisor
    if decision.get("approved"):
        refunds.create(**state["pending_refund"], approved_by=decision["by"])           # idempotency key inside
        note = f"Supervisor approved refund of ₹{state['pending_refund']['amount_paise'] / 100:.0f}."
    else:
        note = "Supervisor declined the refund; explain politely and offer alternatives."
    return {"pending_refund": None, "messages": [("user", f"[system note] {note}")]}

g = StateGraph(State)
g.add_node("classify", classify); g.add_node("rag", rag); g.add_node("agent", agent)
g.add_node("tools", ToolNode(tools)); g.add_node("after_tools", after_tools); g.add_node("human_review", human_review)
g.add_edge(START, "classify")
g.add_conditional_edges("classify", lambda s: s["intent"], {"FAQ": "rag", "ORDER": "agent", "ABUSE": END})
g.add_edge("rag", END)
g.add_conditional_edges("agent", tools_condition, {"tools": "tools", "__end__": END})   # loop while tools requested
g.add_edge("tools", "after_tools")
g.add_conditional_edges("after_tools", needs_approval, {"human_review": "human_review", "agent": "agent"})
g.add_edge("human_review", "agent")

with PostgresSaver.from_conn_string("postgresql://app:***@db:5432/app") as saver:
    saver.setup()                                                   # creates checkpoint tables (first run)
    graph = g.compile(checkpointer=saver)
    cfg = {"configurable": {"thread_id": "conv-7f3a"}, "recursion_limit": 20}
    for update in graph.stream({"messages": [("user", "Order 4521 mein raita missing tha, refund do")], "user_id": "u42"},
                               cfg, stream_mode="updates"):
        print(update)                                              # stream node-by-node progress to UI
    # Later (supervisor UI clicked Approve):
    graph.invoke(Command(resume={"approved": True, "by": "sup_19"}), cfg)
```

### FastAPI wrapper: start/continue a thread, surface interrupts to the UI
```python
@app.post("/api/support/{thread_id}/message")
async def message(thread_id: str, body: Msg, user=Depends(current_user)):
    cfg = {"configurable": {"thread_id": f"{user.id}:{thread_id}"}, "recursion_limit": 20}   # thread scoped to user
    result = await graph.ainvoke({"messages": [("user", body.text)], "user_id": user.id}, cfg)
    state = await graph.aget_state(cfg)
    if state.next and state.tasks and state.tasks[0].interrupts:                            # paused for approval
        return {"status": "WAITING_APPROVAL", "details": state.tasks[0].interrupts[0].value}
    return {"status": "OK", "reply": result["messages"][-1].content}

@app.post("/api/support/{thread_id}/approve")          # supervisor endpoint (RBAC: supervisors only)
async def approve(thread_id: str, body: Decision, sup=Depends(require_role("supervisor"))):
    cfg = {"configurable": {"thread_id": body.thread_key}}
    result = await graph.ainvoke(Command(resume={"approved": body.approved, "by": sup.id}), cfg)
    return {"reply": result["messages"][-1].content}
```
(For async FastAPI use the async checkpointer, `AsyncPostgresSaver`, when compiling the graph.)

### Prebuilt ReAct agent for quick starts
```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
quick_agent = create_react_agent(ChatAnthropic(model="claude-sonnet-5-5"), tools, checkpointer=MemorySaver())
quick_agent.invoke({"messages": [("user", "Where is order 4521?")]}, {"configurable": {"thread_id": "t1"}})
```

---

## ⚫ Interview Questions + Answers

**Q1: What is LangGraph and why use it over simple chains?**
A1: LangGraph models an LLM application as a graph of nodes (functions) over a shared typed state, with normal and conditional edges, including cycles. That makes branching, agent loops, persistence, human approval steps and multi-agent coordination explicit and controllable. Simple chains are linear pipelines. LangGraph adds stateful orchestration with checkpointing, so conversations and long tasks can resume after failures, be inspected step by step and be paused for humans, which is critical for production agents.

**Q2: How do checkpointers work and what do they enable?**
A2: A checkpointer persists the graph state after each step under a thread ID, in memory, SQLite, Postgres or Redis. On the next invocation with the same thread ID, the graph loads the latest state, giving multi-turn memory. If a process crashes, execution can resume from the last checkpoint. Interrupts rely on checkpoints to pause and later resume, and you can list historical checkpoints to inspect or re-run from earlier states (time travel) for debugging. Nodes should be idempotent, because a step may re-run after failure.

**Q3: How do you implement human-in-the-loop approval?**
A3: Put the sensitive action behind a node that calls `interrupt()` with the details to review (refund amount, customer, reason). The graph pauses, the state is checkpointed, and the caller sees the interrupt payload, which you surface in a supervisor UI or queue. When a human decides, resume the same thread with `Command(resume=decision)`. The node continues with that decision (executing an idempotent action, or declining), and the graph proceeds. Enforce RBAC on who can resume, and audit-log decisions.

**Q4: How do you prevent infinite loops in LangGraph agents?**
A4: Set a recursion limit per run, track step counts or budgets in state and route to END or escalation when they're exceeded, add loop-detection logic (repeated identical tool calls), use timeouts per node, and design conditional edges with clear exit conditions (e.g., `tools_condition` exits when the model stops requesting tools). Monitor runs that hit limits, and route them to human fallback.

**Q5: How would you structure a production agent with LangGraph?**
A5: A typed, compact state (messages, IDs, flags, summaries). A cheap classification or router node, with deterministic nodes for known workflows and an LLM-plus-tools loop only for open-ended paths. Tool nodes enforce authz and policy. Approval interrupts guard high-impact actions. A Postgres checkpointer keys threads by user and conversation. Recursion limits and timeouts apply throughout, updates stream to the UI, and the whole thing is wrapped in an API service with tracing (LangSmith or OpenTelemetry), evals per node and end-to-end, and versioned prompts and graphs.

---

## 🔷 Trade-offs
✅ Explicit control flow, persistence, interrupts, streaming — ❌ more upfront design than a simple chain.
✅ Checkpointing: resilience & memory — ❌ storage growth, state schema migrations.
✅ Prebuilt agents: fast start — ❌ less control; customize graphs for production.
✅ Framework ecosystem (LangSmith, Platform) — ❌ dependency on fast-evolving libraries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| StateGraph | Graph over shared typed state | साझा state वाला graph |
| Node | Step function | कदम वाला function |
| Edge / conditional edge | Transition / routed transition | रास्ता / शर्त वाला रास्ता |
| Reducer | How state updates merge | state कैसे जुड़े |
| Checkpointer | Persists state per step | हर कदम पर state save |
| Thread | Conversation/task identity | बातचीत की पहचान |
| Interrupt | Pause for human input | इंसान के लिए रुकना |
| Command(resume) | Continue after interrupt | रुकने के बाद आगे |
| Recursion limit | Max steps per run | अधिकतम कदम |
| Time travel | Inspect/replay past checkpoints | पुराने states देखना |

---

## ⚡ 3-Line Summary
**English:**
1. LangGraph builds agents/workflows as graphs: typed state + nodes + (conditional) edges, cycles for agent loops.
2. Checkpointers (e.g., Postgres) persist state per thread → memory, crash recovery, time travel; interrupts enable human approvals with resume.
3. Production: idempotent nodes, bounded loops, compact state, deterministic nodes where possible, streaming updates, RBAC on resumes, tracing & evals.

**Hindi:**
1. LangGraph: typed state + nodes + शर्त वाले edges, loops से agent चक्र।
2. Checkpointer (Postgres) हर thread का state save — याद, crash recovery; interrupt से इंसान की मंज़ूरी और फिर आगे।
3. Production: idempotent nodes, सीमित loops, छोटा state, जहाँ हो सके deterministic nodes, streaming, resume पर RBAC, tracing।

---

## ➡️ Next Topic Suggestion
**144. Multi-Agent Systems** — Some tasks are best split across specialized agents. Next: orchestrator-worker, router/handoff and critic patterns, when multiple agents help, and how to control their cost and coordination.
