---

# 147. AutoGen Teams
# हिंदी में: AutoGen Teams (कई agents की टीम)
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
A team in AutoGen AgentChat is a group of participants plus a termination condition. All teams share the same API: `run`, `run_stream`, `reset`, `save_state` and `load_state`. Built-in team classes in 0.7.5: `RoundRobinGroupChat`, `SelectorGroupChat`, `MagenticOneGroupChat`, `Swarm` and `GraphFlow`.

## 🔵 सरल परिभाषा (Hindi)
AutoGen AgentChat में team यानी participants का समूह और एक termination condition। सभी teams का API एक जैसा है: `run`, `run_stream`, `reset`, `save_state`, `load_state`। 0.7.5 में built-in teams: `RoundRobinGroupChat`, `SelectorGroupChat`, `MagenticOneGroupChat`, `Swarm` और `GraphFlow`।

---

## 🔴 Problem it Solves
One agent doing everything gets a long prompt, mixes roles and has no second opinion. Hand-coded multi-agent loops need turn management, stop rules, state saving and streaming. A team packages these so you pick a coordination style and a stop rule.

## 🔴 यह क्यों बना? (Hindi)
एक agent सब कुछ करे तो prompt लंबा होता है, भूमिकाएँ मिल जाती हैं और दूसरी राय नहीं मिलती। हाथ से लिखे multi-agent loops में turn management, stop rules, state saving और streaming खुद बनाने पड़ते हैं। Team यह सब पैक कर देती है; आप सिर्फ़ coordination style और stop rule चुनते हैं।

---

## 🟢 How it Works

```
Step 1 -> Create participants (AssistantAgent, CodeExecutorAgent, custom agents)
Step 2 -> Choose a team class (round robin, selector, magentic-one, swarm)
Step 3 -> Compose a termination condition with | (OR) and & (AND)
Step 4 -> team.run(task=...) or run_stream(task=...) starts the shared conversation
Step 5 -> Every message is broadcast to all participants (one shared thread)
Step 6 -> Termination condition fires; TaskResult has messages and stop_reason
Step 7 -> save_state() snapshots the team; reset() clears it for a new task
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Participants बनाओ (AssistantAgent, CodeExecutorAgent, custom agents)
Step 2 -> Team class चुनो (round robin, selector, magentic-one, swarm)
Step 3 -> Termination condition को | (OR) और & (AND) से जोड़ो
Step 4 -> team.run(task=...) या run_stream(task=...) साझा बातचीत शुरू करता है
Step 5 -> हर message सभी participants को broadcast होता है (एक साझा thread)
Step 6 -> Termination condition लगती है; TaskResult में messages और stop_reason होते हैं
Step 7 -> save_state() team का snapshot लेता है; reset() नए task के लिए साफ़ करता है
```

---

## 🟡 Real World Example
**Tariff Agent team.** `writer` drafts an HS classification, `reviewer` checks it and says APPROVE when satisfied. The team stops on 'APPROVE', on 8 messages, or after 30 seconds, whichever comes first. The observed run stopped with: `Text 'APPROVE' mentioned`.

## 🟡 Real Example Hindi mein
**Tariff Agent team.** `writer` HS classification का draft लिखता है, `reviewer` जाँचकर संतुष्ट होने पर APPROVE कहता है। Team 'APPROVE' पर, 8 messages पर, या 30 सेकंड बाद, जो पहले हो, रुकती है। देखा गया stop reason: `Text 'APPROVE' mentioned`।

---

## 💻 Code Example — Basic
Basic: a two-agent round-robin team with OR-combined termination (`TextMentionTermination | MaxMessageTermination | TimeoutTermination`), streaming with `run_stream`, then `save_state()` and `reset()`.

```python
# Basic: what a team is: participants + termination + run/run_stream/save_state/reset
import asyncio  # loop
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM
from autogen_agentchat.agents import AssistantAgent  # agent
from autogen_agentchat.teams import RoundRobinGroupChat  # simplest team
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination, TimeoutTermination  # stop rules
from autogen_agentchat.base import TaskResult  # final result type

async def main() -> None:  # entry
    writer = AssistantAgent("writer", ReplayChatCompletionClient(["Draft: duty is 25%"]))  # agent 1
    reviewer = AssistantAgent("reviewer", ReplayChatCompletionClient(["APPROVE"]))  # agent 2
    stop = TextMentionTermination("APPROVE") | MaxMessageTermination(8) | TimeoutTermination(30)  # OR-combine stop rules
    team = RoundRobinGroupChat([writer, reviewer], termination_condition=stop)  # build team
    async for item in team.run_stream(task="Classify shoes"):  # stream messages as they happen
        if isinstance(item, TaskResult):  # last item is the result
            print("STOP:", item.stop_reason)  # why it stopped
        else:  # normal message
            print(item.source, "->", getattr(item, "content", ""))  # who said what
    state = await team.save_state()  # JSON-able snapshot (history etc.)
    print(sorted(state.keys()))  # state keys
    await team.reset()  # clear for a fresh task (also reset termination)

asyncio.run(main())  # go
```

## 💻 Code Example — Advanced
Advanced: a team built per request (teams hold state), streamed to the client as Server-Sent Events from FastAPI, with a hard token budget via `TokenUsageTermination` and in-band error events.

```python
# Advanced: team per request, streaming SSE endpoint, token budget, error handling
import json  # serialise events
from typing import AsyncIterator  # type
from fastapi import FastAPI  # web
from fastapi.responses import StreamingResponse  # SSE
from fastapi.testclient import TestClient  # test
from pydantic import BaseModel  # body
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake
from autogen_agentchat.agents import AssistantAgent  # agent
from autogen_agentchat.teams import RoundRobinGroupChat  # team
from autogen_agentchat.conditions import MaxMessageTermination, TokenUsageTermination  # budget rules
from autogen_agentchat.base import TaskResult  # result

app = FastAPI()  # app

class Req(BaseModel):  # body
    task: str  # user task

def build_team() -> RoundRobinGroupChat:  # teams hold state -> build one per request
    a = AssistantAgent("classifier", ReplayChatCompletionClient(["HS 6403"]))  # agent a
    b = AssistantAgent("reviewer", ReplayChatCompletionClient(["looks right"]))  # agent b
    stop = MaxMessageTermination(3) | TokenUsageTermination(max_total_token=2000)  # hard budget
    return RoundRobinGroupChat([a, b], termination_condition=stop)  # team

async def events(task: str) -> AsyncIterator[str]:  # SSE generator
    try:  # protect stream
        async for item in build_team().run_stream(task=task):  # stream
            if isinstance(item, TaskResult):  # end
                yield f"data: {json.dumps({'done': True, 'stop': item.stop_reason})}\n\n"  # final event
            else:  # message
                yield f"data: {json.dumps({'from': item.source, 'text': str(getattr(item, 'content', ''))})}\n\n"  # event
    except Exception as e:  # runtime failure
        yield f"data: {json.dumps({'error': str(e)})}\n\n"  # report in-band

@app.post("/team")  # endpoint
async def team(req: Req) -> StreamingResponse:  # handler
    return StreamingResponse(events(req.task), media_type="text/event-stream")  # stream

print(TestClient(app).post("/team", json={"task": "classify shoes"}).text)  # try
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---|---|---|---|---|
| Multi-agent unit | Graph with multiple nodes | Crew of agents + tasks | Agents with handoffs / agents-as-tools | Team (RoundRobin, Selector, MagenticOne, Swarm) |
| Stop rule | END node | Task completion / max_iter | max_turns / final output | Termination conditions composable with | and & |
| Streaming | stream / astream_events | Kickoff callbacks | Runner.run_streamed | team.run_stream() |
| State save | Checkpointer | Limited | Sessions | team.save_state()/load_state() |
| Message sharing | Shared state | Task context passing | Explicit handoff | All participants see the shared thread |
| Reuse across requests | Compiled graph is reusable | Crew per kickoff | Agents reusable | Team keeps state: build per request or reset() |

---

## ⚠️ Common Mistakes
❌ Mistake: Sharing one team object across concurrent requests.
✅ Correct: Teams hold conversation state and are bound to one event loop; build one per request or session.

❌ Mistake: No termination condition.
✅ Correct: Always combine a semantic stop (TextMention) with a hard cap (MaxMessage, TokenUsage, Timeout).

❌ Mistake: Forgetting `reset()` between tasks on a reused team.
✅ Correct: Call `await team.reset()` or the new task inherits old history.

❌ Mistake: Ignoring the final item of run_stream.
✅ Correct: The last item is a `TaskResult`; check `isinstance(item, TaskResult)` for the stop reason.

---

## 🧠 Tricky Interview Question
Your team sometimes runs 40 turns and costs 10x the average. How do you control this?

Answer: Add hard budgets: `MaxMessageTermination`, `TokenUsageTermination(max_total_token=...)` and `TimeoutTermination`, OR-combined with the semantic stop. Reduce participants' system prompts, use a cheaper model for the reviewer, and log `stop_reason` so you can see which rule fires. If it stops by cap often, the agents are not converging: fix prompts or add a stronger reviewer criterion instead of only raising the cap.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is the minimum to create a team?
A1: A list of participants (and normally a termination_condition): `RoundRobinGroupChat([a, b], termination_condition=...)`.

Q2: [Medium] How do you combine stop rules?
A2: Use `|` for OR and `&` for AND on termination conditions.

Q3: [Hard] Why build a team per request in FastAPI?
A3: Team state and the event loop binding make a shared instance unsafe for concurrent users; per-request teams or `load_state` from a store are safe.

Q4: [Hard] How do you stream partial progress?
A4: `async for item in team.run_stream(task=...)`; items are messages or events, and the final item is a TaskResult.

Q5: [System Design] Design a resumable multi-agent job.
A5: Store `save_state()` JSON per session in a DB, rebuild the team on each request, `load_state`, run until termination, save again; add idempotency keys and a budget per session.

---

## 💰 Cost Impact
Every participant sees the whole shared thread, so input tokens per turn grow with history and number of turns: cost is roughly the sum over turns of `history_tokens * in_price` plus outputs. Tips: tight MaxMessage/TokenUsage caps, concise system prompts, cheaper models for simple roles, summarise or reset between tasks. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- The task benefits from roles (writer/reviewer, coder/executor).
- You want standard stop rules, streaming and state for free.
- Conversation among agents is the right shape.

❌ Avoid when:
- A single agent with tools is enough.
- You need strict graph branching (consider a graph framework).
- Tight latency budgets with many turns.

---

## 📊 Visual Diagram
```
 task
   |
   v
 +--------------- Team ----------------+
 | participants: [writer] [reviewer]   |
 | shared message thread (broadcast)   |
 | termination: Text | MaxMsg | Timeout|
 +-----+-------------------------------+
       | run_stream yields messages ... TaskResult(stop_reason)
       v
 save_state() <-> load_state()    reset()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|---|---|---|
| Team | Group of agents with a stop rule | stop rule वाला agents का समूह |
| participant | An agent in the team | team में एक agent |
| termination condition | Rule that ends the run | run खत्म करने वाला नियम |
| run_stream | Streams messages as they happen | messages होते ही stream करता है |
| TaskResult | Final result object | अंतिम result object |
| stop_reason | Why the team stopped | team क्यों रुकी |
| save_state | JSON snapshot of the team | team का JSON snapshot |

---

## ⚡ 3-Line Summary
English: A team is participants plus a termination condition with a shared API.
Use run/run_stream, combine stops with | and &, build per request.
Cap messages, tokens and time to control cost.
Hindi: Team यानी participants और termination condition, साझा API के साथ।
run/run_stream इस्तेमाल करें, stops को | और & से जोड़ें, हर request पर नई team बनाएँ।
खर्च नियंत्रित करने के लिए messages, tokens और समय सीमित रखें।

---

## ➡️ Next Topic
148. RoundRobinGroupChat -- the simplest team: fixed turn order.

---
