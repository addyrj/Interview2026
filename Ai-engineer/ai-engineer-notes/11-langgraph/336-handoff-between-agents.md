---

# 336. Handoff Between Agents
# हिंदी में: Agents के बीच Handoff

---

## 🔵 Simple Definition (English)
A handoff is the moment one agent passes control (and some context) to another agent. In LangGraph it is done by returning `Command(goto="other_agent", update={...})`, either from a node or from a tool that the LLM calls (a "handoff tool"). `goto` says who runs next, `update` says which state to pass along.

## 🔵 सरल परिभाषा (Hindi)
Handoff वह क्षण है जब एक agent control (और कुछ context) दूसरे agent को देता है। LangGraph में यह `Command(goto="other_agent", update={...})` return करके होता है, या तो node से, या ऐसे tool से जिसे LLM call करता है ("handoff tool")। `goto` बताता है अगला कौन चलेगा, `update` बताता है कौन सी state साथ जाएगी।

---

## 🔴 Problem it Solves
Without a clean handoff, agents either lose context (the second agent asks the user everything again) or receive too much context (the whole 10,000-token history, slow and costly). Also, an LLM that "says" 'transfer me to legal' in plain text does nothing; the graph needs a structured action. A handoff mechanism makes the transfer explicit, validated, loggable and context-controlled.

## 🔴 यह क्यों बना? (Hindi)
साफ़ handoff के बिना agents या तो context खो देते हैं (दूसरा agent user से सब कुछ फिर पूछता है) या बहुत ज़्यादा context पाते हैं (पूरी 10,000-token history, धीमी और महँगी)। LLM अगर text में "legal को transfer करो" लिख दे तो कुछ नहीं होता; graph को structured action चाहिए। Handoff mechanism transfer को explicit, validated, loggable और context-नियंत्रित बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Agent A decides another agent is needed (rule or LLM tool call)
Step 2 → It produces Command(goto="B", update={...context...})
Step 3 → Update fields are merged into shared state by reducers
Step 4 → LangGraph schedules node B next
Step 5 → B reads the handed-over fields (summary, hs_code, reason) + messages
Step 6 → If the handoff came from a TOOL, the tool must also add a ToolMessage
         (so the AI tool_call has a matching result) and use graph=Command.PARENT
         when the tool runs inside a sub-graph
Step 7 → B finishes, or hands back / onwards
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Agent A तय करता है कि दूसरा agent चाहिए (rule या LLM tool call)
Step 2 → वह Command(goto="B", update={...context...}) बनाता है
Step 3 → Update fields reducers से shared state में merge होते हैं
Step 4 → LangGraph अगला node B schedule करता है
Step 5 → B handed-over fields (summary, hs_code, reason) + messages पढ़ता है
Step 6 → अगर handoff TOOL से आया है तो tool को ToolMessage भी जोड़ना होगा
         (ताकि AI के tool_call का matching result रहे) और sub-graph के अंदर चलने पर
         graph=Command.PARENT use करना होगा
Step 7 → B काम खत्म करता है, या वापस / आगे handoff करता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: `classifier` finds HS 8517.13 for a phone, then the officer asks about import restrictions. The classifier hands off to `legal` with `update={"hs_code": "8517.13", "handoff_reason": "restriction check"}`. Legal does not need the classifier's reasoning; it only needs the code and the reason, which keeps tokens low. **Amazon AI**: the shipping agent hands off to the refund agent with `order_id` and `damage_reason` only.

## 🟡 Real Example Hindi mein
**Tariff System**: `classifier` phone के लिए HS 8517.13 पाता है, फिर officer import restrictions पूछता है। Classifier `update={"hs_code": "8517.13", "handoff_reason": "restriction check"}` के साथ `legal` को handoff करता है। Legal को classifier की पूरी reasoning नहीं चाहिए; सिर्फ code और reason, जिससे tokens कम रहते हैं। **Amazon AI**: shipping agent सिर्फ `order_id` और `damage_reason` के साथ refund agent को handoff करता है।

---

## 💻 Code Example — Basic
```python
# Handoff with context passing - runs offline (pip install langgraph)
from typing import Literal, TypedDict  # typing

from langgraph.graph import END, START, StateGraph  # graph API
from langgraph.types import Command  # goto + update


class State(TypedDict):  # shared state
    question: str  # what the officer asked
    hs_code: str  # context passed along
    handoff_reason: str  # why the transfer happened
    answer: str  # final text


def classifier(state: State) -> Command[Literal["legal"]]:  # agent A
    code = "8517.13"  # pretend we classified a phone
    return Command(  # return both routing and context
        goto="legal",  # who runs next
        update={"hs_code": code, "handoff_reason": "restriction check"},  # minimal context to pass
    )


def legal(state: State) -> Command[Literal["__end__"]]:  # agent B
    answer = f"HS {state['hs_code']} ({state['handoff_reason']}): no import ban, licence not needed"  # uses handed context
    return Command(goto=END, update={"answer": answer})  # finish


builder = StateGraph(State)  # builder
builder.add_node("classifier", classifier)  # node
builder.add_node("legal", legal)  # node
builder.add_edge(START, "classifier")  # entry
graph = builder.compile()  # compile

print(graph.invoke({"question": "can I import a phone?", "hs_code": "", "handoff_reason": "", "answer": ""})["answer"])
```

## 💻 Code Example — Advanced
```python
# Handoff TOOL that returns a Command (what an LLM-driven agent does), plus a validated, async dispatcher
import asyncio  # async
from typing import Annotated, Literal, TypedDict  # typing

from langchain_core.messages import AIMessage, ToolMessage  # message types
from langchain_core.tools import InjectedToolCallId, tool  # tool decorator + injected id
from langgraph.graph import END, START, StateGraph  # graph API
from langgraph.graph.message import add_messages  # reducer for messages
from langgraph.types import Command  # routing + update


class State(TypedDict):  # state with chat history
    messages: Annotated[list, add_messages]
    hs_code: str


@tool
def transfer_to_legal(
    reason: str,  # LLM fills this: why we transfer (becomes context)
    tool_call_id: Annotated[str, InjectedToolCallId],  # injected: the id of THIS tool call
) -> Command:
    """Hand the conversation to the legal agent for import restrictions."""  # docstring = tool description for the LLM
    result = ToolMessage(content=f"Transferred to legal: {reason}", tool_call_id=tool_call_id)  # required reply to the tool call
    return Command(goto="legal", update={"messages": [result]})  # route + record the tool result


async def classifier(state: State) -> Command[Literal["legal", "__end__"]]:  # node simulating an LLM that calls the tool
    await asyncio.sleep(0)  # LLM latency placeholder
    ai = AIMessage(  # fake LLM message with a tool call
        content="",
        tool_calls=[{"name": "transfer_to_legal", "args": {"reason": "restriction check"}, "id": "call_1"}],
    )
    call = ai.tool_calls[0]  # read the requested call
    try:
        # Execute the tool; passing a full tool-call dict lets LangChain inject tool_call_id
        cmd = await transfer_to_legal.ainvoke({**call, "type": "tool_call"})  # returns a Command
    except Exception as exc:  # tool failure must not kill the run
        return Command(goto=END, update={"messages": [AIMessage(content=f"handoff failed: {exc}")]})
    update = dict(cmd.update or {})  # copy the tool's update
    update["messages"] = [ai] + list(update["messages"])  # keep AI tool_call BEFORE its ToolMessage
    update["hs_code"] = "8517.13"  # pass context
    return Command(goto=cmd.goto, update=update)  # route to legal


async def legal(state: State) -> dict:  # receiving agent
    return {"messages": [AIMessage(content=f"Legal: HS {state['hs_code']} allowed")]}  # answer


builder = StateGraph(State)  # builder
builder.add_node("classifier", classifier)  # node
builder.add_node("legal", legal)  # node
builder.add_edge(START, "classifier")  # entry
builder.add_edge("legal", END)  # exit
graph = builder.compile()  # compile


async def main() -> None:
    out = await graph.ainvoke({"messages": [("user", "can I import a phone?")], "hs_code": ""})
    for m in out["messages"]:  # show the transcript
        print(type(m).__name__, "|", m.content or m.tool_calls)  # human, ai(tool call), tool, ai


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Expose handoff events so the UI (or logs) can show "Transferred: classifier -> legal". Use `stream_mode="updates"` and detect node changes.

```python
from fastapi import FastAPI  # web
from pydantic import BaseModel  # validation

app = FastAPI()  # app


class Q(BaseModel):  # request
    text: str


@app.post("/ask")
async def ask(q: Q) -> dict[str, object]:  # route
    path: list[str] = []  # agents visited in order
    last = ""  # last text answer
    async for chunk in graph.astream({"messages": [("user", q.text)], "hs_code": ""}, stream_mode="updates"):
        for node, delta in chunk.items():  # node name + its partial update
            path.append(node)  # record order -> reveals handoffs
            msgs = (delta or {}).get("messages") or []  # may be empty
            if msgs:
                last = msgs[-1].content or last  # remember latest text
    return {"path": path, "answer": last}  # e.g. path = [classifier, legal]
```

---

## 🔗 LangChain / LangGraph Connection
In `langgraph-swarm` / `langgraph-supervisor`, `create_handoff_tool(agent_name="legal")` builds exactly such a tool: it returns a `Command(goto=agent_name, graph=Command.PARENT, update={...})` including the `ToolMessage`. `graph=Command.PARENT` is needed because the tool executes inside a sub-agent graph, but the target agent lives in the parent graph. When agents are plain nodes in the same graph (as in Basic), no PARENT is needed.

```python
from typing import Annotated  # typing
from langchain_core.messages import ToolMessage  # tool result
from langchain_core.tools import InjectedToolCallId, tool  # tool utils
from langgraph.types import Command  # command


@tool
def transfer_to_duty(tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Transfer to the duty calculation agent."""
    msg = ToolMessage("Transferred to duty agent", tool_call_id=tool_call_id)  # satisfy the tool call
    return Command(goto="duty", graph=Command.PARENT, update={"messages": [msg]})  # jump in the PARENT graph
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Handoff tool returns a string instead of a Command
✅ Correct: Return `Command(goto=..., update=...)` so LangGraph actually routes.

```python
# Wrong - the LLM "transfers" but the graph never moves
@tool
def transfer_to_legal() -> str:
    return "Transferring to legal"

# Right
@tool
def transfer_to_legal(tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    return Command(goto="legal", graph=Command.PARENT,
                   update={"messages": [ToolMessage("ok", tool_call_id=tool_call_id)]})
```

❌ Mistake 2: Missing ToolMessage, or passing the entire history
✅ Correct: Always answer the tool call; pass only the context the next agent needs.

```python
# Wrong - provider error: assistant tool_call has no matching tool message
return Command(goto="legal")

# Right - tool call is closed and compact context is passed
return Command(goto="legal", update={"messages": [ToolMessage("ok", tool_call_id=tid)], "hs_code": code})
```

---

## 🧠 Tricky Interview Question

**Q**: "After a handoff, the OpenAI API returns 400: 'An assistant message with tool_calls must be followed by tool messages'. Why?"

**Answer**: The handoff tool changed routing but did not append a `ToolMessage` with the matching `tool_call_id`. The next agent then sends a history that contains an AI `tool_call` with no result, which providers reject. Fix: the handoff tool must add `ToolMessage(content=..., tool_call_id=tool_call_id)` in `update["messages"]` (use `InjectedToolCallId`). Also watch for parallel tool calls: if the LLM calls the handoff tool and another tool in the same turn, you need results for all of them, so many frameworks disable parallel tool calls for handoffs.

---

## ⚫ Interview Questions + Answers

Q1: How do you hand off control in LangGraph? (Easy)
A1: Return `Command(goto="target", update={...})` from a node or tool.

Q2: What does `update` in a handoff do? (Easy)
A2: It writes values to the shared state (merged by reducers) so the next agent receives context such as `hs_code` or a summary.

Q3: Why do handoff tools need `InjectedToolCallId`? (Medium)
A3: The tool must reply with a `ToolMessage` carrying the id of the call it answers. `InjectedToolCallId` gives the tool that id at runtime without exposing it to the LLM as an argument.

Q4: What does `graph=Command.PARENT` mean? (Medium)
A4: It tells LangGraph that `goto` refers to a node in the parent graph, not in the current sub-graph. Needed when an agent (sub-graph) hands off to a sibling agent in the parent.

Q5: How do you decide how much context to pass in a handoff? (Hard)
A5: Pass the minimum the receiver needs: structured fields (ids, codes, constraints), a short summary of the conversation, and the last user message. Full history is only worth it when the receiver must reason over details. Measure with evals: if accuracy stays the same with less context, keep the smaller one. Redact PII or sensitive data that the receiving agent has no right to see.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A task crosses specialist boundaries
- You want explicit, loggable transfers
- Context must be controlled (cost, privacy)

❌ Avoid when:
- One agent can finish the task (extra hops waste tokens)
- The "handoff" is really a fixed step (use a normal edge)

---

## 📊 Visual Diagram
```
 [classifier]
     │  LLM calls tool: transfer_to_legal(reason)
     ▼
  tool returns Command(
     goto   = "legal",
     update = { messages:[ToolMessage], hs_code:"8517.13" },
     graph  = PARENT )            ← only when inside a sub-graph
     │
     ▼
  [legal]  reads hs_code + short reason  ──► answer ──► END
```

---

## 💰 Cost Impact
- A handoff itself costs one tool-call completion (~50-100 output tokens) and the tool schema tokens (each handoff tool adds ~60-100 tokens to every prompt of that agent).
- The big lever is context size: passing 5,000 tokens of history vs 300 tokens of structured context saves ~4,700 input tokens per hop. At `gpt-4o-mini` input pricing ($0.15 / 1M) that is about $0.0007 per handoff, which matters at 1M requests/month (~$700).
- Optimise: pass structured fields + summary, trim history, give each agent only the handoff tools it truly needs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Handoff | Passing control to another agent | दूसरे agent को control देना |
| Handoff tool | Tool whose result is a Command | Handoff करने वाला tool |
| Command | goto + update return object | goto + update वाला object |
| Command.PARENT | Target node is in parent graph | Target parent graph में है |
| InjectedToolCallId | Runtime-injected id of the tool call | Runtime पर मिला tool call id |
| ToolMessage | Result message answering a tool call | Tool call का जवाब |

---

## ⚡ 3-Line Summary
English: A handoff transfers control with `Command(goto, update)`, either from a node or an LLM-called tool. Tools must also return a matching `ToolMessage` and use `graph=Command.PARENT` when crossing sub-graph boundaries. Pass minimal structured context to save tokens.
Hindi: Handoff `Command(goto, update)` से control transfer करता है, node से या LLM के call किए tool से। Tool को matching `ToolMessage` भी लौटाना होता है और sub-graph की सीमा पार करने पर `graph=Command.PARENT` लगाना होता है। Tokens बचाने के लिए कम, structured context पास करो।

---

## ➡️ Next Topic
**337. LangGraph Streaming** — stream tokens, node updates and custom events to the user while agents work.
