---

# 335. Swarm Pattern
# हिंदी में: Swarm Pattern (बिना manager के agents का समूह)

---

## 🔵 Simple Definition (English)
In a swarm, there is no central manager. Every agent can hand control directly to another agent when it decides that agent is better suited. The system remembers which agent is currently "active", and the next user message goes to that active agent. It is like a call centre where each person transfers you to a colleague.

## 🔵 सरल परिभाषा (Hindi)
Swarm में कोई central manager नहीं होता। हर agent सीधे दूसरे agent को control दे सकता है जब उसे लगे कि वह agent बेहतर है। System याद रखता है कि अभी कौन सा agent "active" है, और अगला user message उसी active agent के पास जाता है। यह call centre जैसा है जहाँ हर व्यक्ति आपको अपने colleague को transfer करता है।

---

## 🔴 Problem it Solves
A supervisor adds an extra LLM call on every hop and becomes a bottleneck: every message pays a "who should handle this?" cost, even when the conversation obviously stays with one specialist. In a swarm, the user keeps talking to the same specialist until that specialist transfers them. It cuts routing calls and feels more natural for conversations.

## 🔴 यह क्यों बना? (Hindi)
Supervisor हर hop पर extra LLM call जोड़ता है और bottleneck बन जाता है: हर message को "कौन संभालेगा?" की कीमत देनी पड़ती है, भले conversation साफ़ तौर पर एक specialist के साथ चल रही हो। Swarm में user उसी specialist से बात करता रहता है जब तक वह transfer न करे। Routing calls कम होती हैं और conversation ज़्यादा natural लगती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → State has a field active_agent (default = the first agent)
Step 2 → START routes to whichever agent is active_agent
Step 3 → The active agent answers, OR calls a handoff to another agent
Step 4 → Handoff = Command(goto=other_agent, update={"active_agent": other_agent})
Step 5 → The new agent continues using the same shared messages
Step 6 → When an agent finishes without a handoff, the run ends (END)
Step 7 → Checkpointer remembers active_agent, so the next user turn resumes with it
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → State में active_agent field है (default = पहला agent)
Step 2 → START उस agent पर जाता है जो active_agent है
Step 3 → Active agent जवाब देता है, या दूसरे agent को handoff करता है
Step 4 → Handoff = Command(goto=other_agent, update={"active_agent": other_agent})
Step 5 → नया agent वही shared messages लेकर आगे बढ़ता है
Step 6 → Agent बिना handoff के खत्म करे तो run END होता है
Step 7 → Checkpointer active_agent याद रखता है, इसलिए अगला user turn उसी से शुरू होता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: a customs officer chats with `classification_agent`. When they ask "is this item banned from import?" the classifier hands off to `legal_agent`. The following messages ("what about quotas?") go straight to `legal_agent` with no routing call. If the officer asks "what is the HS code of the next item?", legal hands back to classification. **Zomato AI**: `order_agent` transfers to `refund_agent`, which stays active for the rest of the refund conversation.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs officer `classification_agent` से chat करता है। "क्या यह item import के लिए banned है?" पूछने पर classifier `legal_agent` को handoff करता है। अगले messages ("quota का क्या?") बिना routing call के सीधे `legal_agent` को जाते हैं। "अगले item का HS code?" पूछने पर legal वापस classification को handoff करता है। **Zomato AI**: `order_agent` से `refund_agent` को transfer होता है और refund की पूरी बातचीत में वही active रहता है।

---

## 💻 Code Example — Basic
```python
# Swarm with active_agent memory - runs offline (pip install langgraph)
from typing import Literal, TypedDict  # typing

from langgraph.checkpoint.memory import MemorySaver  # remembers active_agent between turns
from langgraph.graph import END, START, StateGraph  # graph API
from langgraph.types import Command  # handoff mechanism


class State(TypedDict):  # shared state
    text: str  # latest user message
    active_agent: str  # who is currently in charge
    reply: str  # latest answer


def entry(state: State) -> Command[Literal["classification", "legal"]]:  # routes to the active agent
    return Command(goto=state.get("active_agent") or "classification")  # default to classification


def classification(state: State) -> Command[Literal["legal", "__end__"]]:  # agent 1
    if "banned" in state["text"]:  # outside my skill -> hand off
        return Command(goto="legal", update={"active_agent": "legal"})  # transfer control
    return Command(goto=END, update={"reply": "classification: HS 8517.13", "active_agent": "classification"})


def legal(state: State) -> Command[Literal["classification", "__end__"]]:  # agent 2
    if "HS code" in state["text"]:  # back to the other specialist
        return Command(goto="classification", update={"active_agent": "classification"})
    return Command(goto=END, update={"reply": "legal: not banned, quota 1000 units", "active_agent": "legal"})


builder = StateGraph(State)  # builder
builder.add_node("entry", entry)  # node
builder.add_node("classification", classification)  # node
builder.add_node("legal", legal)  # node
builder.add_edge(START, "entry")  # all turns enter here
graph = builder.compile(checkpointer=MemorySaver())  # memory keeps active_agent

cfg = {"configurable": {"thread_id": "t1"}}  # one conversation
print(graph.invoke({"text": "HS code of phone?"}, cfg)["reply"])  # classification answers
print(graph.invoke({"text": "is it banned?"}, cfg)["reply"])  # handoff -> legal answers
print(graph.invoke({"text": "what about quota?"}, cfg)["reply"])  # legal still active (no routing)
print(graph.invoke({"text": "HS code of speaker?"}, cfg)["reply"])  # legal -> classification
```

## 💻 Code Example — Advanced
```python
# Swarm with handoff-count guard, allowed-transfer map, async and error handling
import asyncio  # async
from typing import Literal, TypedDict  # typing

from langgraph.checkpoint.memory import MemorySaver  # memory
from langgraph.graph import END, START, StateGraph  # graph
from langgraph.types import Command  # handoff

ALLOWED: dict[str, set[str]] = {  # who may transfer to whom (prevents arbitrary jumps)
    "classification": {"legal", "duty"},
    "legal": {"classification"},
    "duty": {"classification"},
}
MAX_HANDOFFS = 3  # guard against ping-pong inside one turn


class State(TypedDict):
    text: str
    active_agent: str
    handoffs: int  # handoffs in this turn
    reply: str


def handoff(state: State, src: str, dst: str) -> Command:  # helper that validates the transfer
    if dst not in ALLOWED[src]:  # illegal route
        return Command(goto=END, update={"reply": f"error: {src}->{dst} not allowed"})
    if state["handoffs"] >= MAX_HANDOFFS:  # too many transfers
        return Command(goto=END, update={"reply": "error: handoff limit reached"})
    return Command(goto=dst, update={"active_agent": dst, "handoffs": state["handoffs"] + 1})


async def entry(state: State) -> Command:  # start of every turn
    return Command(goto=state.get("active_agent") or "classification", update={"handoffs": 0})  # reset counter


async def classification(state: State) -> Command:
    await asyncio.sleep(0)  # LLM call placeholder
    if "banned" in state["text"]:
        return handoff(state, "classification", "legal")
    if "duty" in state["text"]:
        return handoff(state, "classification", "duty")
    return Command(goto=END, update={"reply": "HS 8517.13", "active_agent": "classification"})


async def legal(state: State) -> Command:
    await asyncio.sleep(0)
    return Command(goto=END, update={"reply": "legal: allowed with licence", "active_agent": "legal"})


async def duty(state: State) -> Command:
    await asyncio.sleep(0)
    return Command(goto=END, update={"reply": "duty: 20 percent", "active_agent": "duty"})


builder = StateGraph(State)
for n, f in [("entry", entry), ("classification", classification), ("legal", legal), ("duty", duty)]:
    builder.add_node(n, f)
builder.add_edge(START, "entry")
graph = builder.compile(checkpointer=MemorySaver())


async def main() -> None:
    cfg = {"configurable": {"thread_id": "t9"}}
    for msg in ["phone HS?", "is it banned?", "ok", "what is the duty?"]:
        try:
            out = await graph.ainvoke({"text": msg}, cfg)
            print(f"{msg!r:22} -> [{out['active_agent']}] {out['reply']}")
        except Exception as exc:  # keep conversation alive on errors
            print("agent error:", exc)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
One thread id per user session; the checkpointer remembers the active agent. Return `active_agent` so the UI can show "You are talking to: Legal".

```python
from fastapi import FastAPI, Header  # web
from pydantic import BaseModel  # validation

app = FastAPI()  # app


class Msg(BaseModel):  # request
    text: str


@app.post("/swarm")
async def swarm_chat(msg: Msg, x_session_id: str = Header(...)) -> dict[str, str]:  # route
    cfg = {"configurable": {"thread_id": f"swarm:{x_session_id}"}}  # per-session memory
    out = await graph.ainvoke({"text": msg.text}, cfg)  # graph from Advanced example
    return {"agent": out["active_agent"], "reply": out["reply"]}  # tell UI who answered
```

---

## 🔗 LangChain / LangGraph Connection
The `langgraph-swarm` package provides `create_swarm([agent_a, agent_b], default_active_agent="a")` and `create_handoff_tool(agent_name=...)`. Each agent is a `create_react_agent` with handoff tools; `active_agent` is stored in swarm state and kept by the checkpointer. Under the hood it is exactly the `Command(goto=...)` pattern above, with LLMs deciding when to call the handoff tool.

```python
# pip install langgraph-swarm langchain-openai
from langchain_openai import ChatOpenAI  # model
from langgraph.checkpoint.memory import MemorySaver  # memory
from langgraph.prebuilt import create_react_agent  # agent factory
from langgraph_swarm import create_handoff_tool, create_swarm  # swarm helpers

llm = ChatOpenAI(model="gpt-4o-mini")  # shared model
classifier = create_react_agent(llm, tools=[create_handoff_tool(agent_name="legal")], name="classifier")  # can hand off to legal
legal = create_react_agent(llm, tools=[create_handoff_tool(agent_name="classifier")], name="legal")  # can hand back
app_graph = create_swarm([classifier, legal], default_active_agent="classifier").compile(checkpointer=MemorySaver())
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not persisting `active_agent`
✅ Correct: Keep it in state and use a checkpointer.

```python
# Wrong - no checkpointer: every turn restarts with the first agent
graph = builder.compile()

# Right
graph = builder.compile(checkpointer=MemorySaver())
```

❌ Mistake 2: Unrestricted handoffs
✅ Correct: Whitelist who may transfer to whom and count handoffs.

```python
# Wrong - any agent can send you anywhere, loops are likely
return Command(goto=llm_chosen_name)

# Right
if llm_chosen_name in ALLOWED[current]:
    return Command(goto=llm_chosen_name, update={"active_agent": llm_chosen_name})
```

---

## 🧠 Tricky Interview Question

**Q**: "In a swarm, two agents keep transferring the user back and forth ('that is not my area'). What happened and how do you fix it?"

**Answer**: Their prompts describe overlapping or incomplete responsibilities, so each thinks the other owns the question. Fix: (1) write each agent's scope and a clear 'answer if unsure within your domain' rule, (2) give one agent a catch-all role, (3) limit handoffs per turn and escalate to a human or default agent after the limit, (4) log handoff pairs and look for A->B->A cycles, (5) add examples of ambiguous queries to the eval set.

---

## ⚫ Interview Questions + Answers

Q1: What is the main idea of the swarm pattern? (Easy)
A1: Agents transfer control directly to each other, and the currently active agent handles the next message. There is no central supervisor.

Q2: Which state field is essential in a swarm? (Easy)
A2: `active_agent`, together with a checkpointer so it persists between turns.

Q3: Supervisor vs swarm: when do you prefer each? (Medium)
A3: Supervisor for task decomposition where one request needs several workers in sequence and you want central control. Swarm for conversational flows where the user stays with one specialist for a while and you want fewer routing calls.

Q4: How is a handoff implemented? (Medium)
A4: As a `Command(goto=target, update={...})` returned by a node, or by a tool that returns a `Command` (with `graph=Command.PARENT` when the tool runs inside a sub-agent). The update changes `active_agent`.

Q5: What are the security risks of swarms and how do you reduce them? (Hard)
A5: Prompt injection can trick an agent into handing off to a more privileged agent (for example one with refund or database-write tools). Mitigate with least privilege per agent, a server-side allowed-transfer map, authorization checks inside tools (not in prompts), logging of every handoff, and human approval for sensitive tools.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Long conversations that stay with one specialist for several turns
- You want to avoid a routing LLM call on every message
- Agents have clear, separate domains

❌ Avoid when:
- One request needs several agents in a fixed order (use supervisor/pipeline)
- You need strict central control or audit of decisions
- Agent domains overlap heavily

---

## 📊 Visual Diagram
```
 Turn 1: user ─► [classification]  ──"is it banned?"──► handoff
 Turn 2: user ─► [legal]   (active_agent = legal, remembered by checkpointer)
 Turn 3: user ─► [legal]   (no routing call)
 Turn 4: user ─► [legal] ──"HS code of X?"──► [classification]

        classification ◄───────────► legal
              ▲  ╲                    
              │    ╲                  
              ▼      ▼                
             duty ◄──┘     (peer-to-peer, no manager)
```

---

## 💰 Cost Impact
- No routing call per message. For a 10-turn legal conversation, a supervisor design would add 10 routing calls (~200 tokens each = ~2,000 tokens). Swarm adds none, except the occasional handoff tool call.
- Cost still grows with shared message history, because every agent receives the full `messages`.
- Optimise: keep history trimmed, give each agent short prompts and only its own tools (fewer tool schema tokens), and use a small model for simple agents.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Swarm | Peer agents handing off directly | बिना manager के agents का समूह |
| active_agent | Agent currently in control | अभी जिसके पास control है |
| Handoff | Transfer of control | Control का transfer |
| Command(goto) | Return value to jump to a node | किसी node पर जाने का command |
| Allowed-transfer map | Whitelist of handoffs | अनुमति वाले transfers की सूची |
| Ping-pong | Agents bouncing a task back and forth | काम का इधर-उधर लौटना |

---

## ⚡ 3-Line Summary
English: A swarm has no manager; agents hand off to each other and the active agent keeps the conversation. Store `active_agent` in state with a checkpointer. Whitelist handoffs and cap them to avoid loops and privilege abuse.
Hindi: Swarm में manager नहीं होता; agents एक-दूसरे को handoff करते हैं और active agent बातचीत संभालता है। `active_agent` को checkpointer के साथ state में रखो। Loops और privilege abuse रोकने के लिए handoffs whitelist करो और सीमित रखो।

---

## ➡️ Next Topic
**336. Handoff Between Agents** — the exact mechanics: `Command`, handoff tools, passing context and state.
