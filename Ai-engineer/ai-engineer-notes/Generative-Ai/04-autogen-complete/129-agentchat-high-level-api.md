---

# 129. AgentChat — High Level API
# हिंदी में: AgentChat — High Level API
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
AgentChat (`autogen-agentchat`) is the high-level, opinionated layer on top of Core. You build agents (`AssistantAgent`, `UserProxyAgent`, `CodeExecutorAgent`), combine them into teams (`RoundRobinGroupChat`, `SelectorGroupChat`, `Swarm`), stop them with termination conditions and run them with `run()` or `run_stream()`.

## 🔵 सरल परिभाषा (Hindi)
AgentChat (`autogen-agentchat`) Core के ऊपर की high-level layer है। आप agents बनाते हैं (`AssistantAgent`, `UserProxyAgent`, `CodeExecutorAgent`), उन्हें teams में जोड़ते हैं (`RoundRobinGroupChat`, `SelectorGroupChat`, `Swarm`), termination conditions से रोकते हैं और `run()` या `run_stream()` से चलाते हैं।

---

## 🔴 Problem it Solves
Writing actor handlers for every chat app is too much work. Teams need common behaviours: a shared transcript, turn-taking, stopping rules, streaming to a UI, saving and restoring state, tool calling, human approval. AgentChat packages these so a working multi-agent app is about 20 lines.

## 🔴 यह क्यों बना? (Hindi)
हर chat app के लिए actor handlers लिखना बहुत मेहनत है। Teams को सामान्य चीज़ें चाहिए: साझा transcript, turn-taking, रुकने के नियम, UI तक streaming, state save/restore, tool calling, human approval। AgentChat यह सब पैक देता है, इसलिए काम करने वाला multi-agent app लगभग 20 lines में बन जाता है।

---

## 🟢 How it Works

```
Step 1 -> Create a model client (OpenAIChatCompletionClient or any ChatCompletionClient)
Step 2 -> Create agents: AssistantAgent(name, model_client, tools=[...], system_message=...)
Step 3 -> Optional: group them into a team + termination_condition (e.g. TextMentionTermination | MaxMessageTermination)
Step 4 -> result = await team_or_agent.run(task=...)  OR  async for m in run_stream(...)
Step 5 -> Stream yields messages/events, last item is TaskResult(messages, stop_reason)
Step 6 -> Inspect message.source, content and models_usage (token counts)
Step 7 -> state = await team.save_state(); later await team.load_state(state)
Step 8 -> await team.reset() to start a fresh conversation
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> model client बनाओ (OpenAIChatCompletionClient या कोई भी ChatCompletionClient)
Step 2 -> agents बनाओ: AssistantAgent(name, model_client, tools=[...], system_message=...)
Step 3 -> optional: team + termination_condition (जैसे TextMentionTermination | MaxMessageTermination)
Step 4 -> result = await team_or_agent.run(task=...)  या  async for m in run_stream(...)
Step 5 -> stream में messages/events आते हैं, आखिरी item TaskResult(messages, stop_reason) होता है
Step 6 -> message.source, content और models_usage (token counts) देखो
Step 7 -> state = await team.save_state(); बाद में await team.load_state(state)
Step 8 -> नई conversation के लिए await team.reset()
```

---

## 🟡 Real World Example
**Tariff Agent with a tool and streaming.** The user asks for the duty on HS 6109.10. The `AssistantAgent` decides to call `get_tariff_rate`, AgentChat executes the Python function, feeds the result back (with `reflect_on_tool_use=True` the model writes a natural-language answer) and `Console(...)` prints each event as it happens: request, tool call, tool result, final answer.

## 🟡 Real Example Hindi mein
**Tool और streaming वाला Tariff Agent.** User HS 6109.10 की duty पूछता है। `AssistantAgent` `get_tariff_rate` call करने का फ़ैसला करता है, AgentChat Python function चलाता है, result model को लौटाता है (`reflect_on_tool_use=True` हो तो model प्राकृतिक भाषा में जवाब लिखता है) और `Console(...)` हर event live print करता है: request, tool call, tool result, final answer।

---

## 💻 Code Example — Basic
Basic: one `AssistantAgent` with a tool, streamed through `Console`. The tool call is scripted in the replay client so it runs offline.

```python
# AgentChat high-level API: agent + tool + Console streaming (offline via ReplayChatCompletionClient)
import asyncio                                                    # async entry
from autogen_agentchat.agents import AssistantAgent              # the main high-level agent
from autogen_agentchat.ui import Console                          # pretty-prints a message stream
from autogen_core.models import CreateResult, RequestUsage        # to script a tool-call reply
from autogen_core import FunctionCall                             # a model "decision" to call a tool
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake model

def get_tariff_rate(hs_code: str) -> str:                         # typed tool
    """Return duty rate for an HS code."""                        # description for the LLM
    return {"6109.10": "20%"}.get(hs_code, "unknown")             # fake data

async def main() -> None:
    info = {"function_calling": True, "vision": False, "json_output": False,
            "family": "unknown", "structured_output": False}      # capabilities of the fake model
    call = FunctionCall(id="c1", name="get_tariff_rate", arguments='{"hs_code": "6109.10"}')  # scripted tool call
    client = ReplayChatCompletionClient([                         # replies are consumed in order
        CreateResult(finish_reason="function_calls", content=[call],
                     usage=RequestUsage(prompt_tokens=0, completion_tokens=0), cached=False),  # step 1: call tool
        "Duty for 6109.10 is 20%.",                               # step 2: final answer (reflect_on_tool_use)
    ], model_info=info)
    agent = AssistantAgent("tariff", model_client=client, tools=[get_tariff_rate], reflect_on_tool_use=True)
    await Console(agent.run_stream(task="Duty for 6109.10?"))     # streams events: tool request, result, answer

if __name__ == "__main__":
    asyncio.run(main())
```

## 💻 Code Example — Advanced
Advanced: a team served via FastAPI Server-Sent Events, with per-session `save_state` / `load_state` and in-stream error reporting (once streaming starts you cannot change the HTTP status code).

```python
# AgentChat in production shape: team + termination + SSE streaming + state save/load + errors
import asyncio, json                                              # stdlib
from fastapi import FastAPI                                       # web
from fastapi.responses import StreamingResponse                   # server-sent events
from fastapi.testclient import TestClient                         # offline test
from pydantic import BaseModel                                    # schema
from autogen_agentchat.agents import AssistantAgent               # agent
from autogen_agentchat.base import TaskResult                     # final item of a stream
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination  # stop rules
from autogen_agentchat.messages import TextMessage                # chat message type
from autogen_agentchat.teams import RoundRobinGroupChat           # team
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

app = FastAPI()
STATES: dict[str, dict] = {}                                      # session_id -> saved team state (use Redis/DB in prod)

class Req(BaseModel):
    session_id: str                                               # conversation key
    task: str                                                     # user message

def build_team() -> RoundRobinGroupChat:
    w = AssistantAgent("writer", ReplayChatCompletionClient(["Draft: duty 20%"]))   # offline stand-in
    r = AssistantAgent("reviewer", ReplayChatCompletionClient(["APPROVE"]))
    return RoundRobinGroupChat([w, r], termination_condition=TextMentionTermination("APPROVE") | MaxMessageTermination(8))

@app.post("/chat")
async def chat(req: Req) -> StreamingResponse:
    team = build_team()                                           # agents are stateful -> build per session
    if req.session_id in STATES:                                  # resume previous conversation
        await team.load_state(STATES[req.session_id])
    async def events():
        try:
            async for item in team.run_stream(task=req.task):     # yields messages then TaskResult
                if isinstance(item, TaskResult):                  # last item
                    STATES[req.session_id] = await team.save_state()  # persist state for next call
                    yield f"data: {json.dumps({'done': item.stop_reason})}\n\n"
                elif isinstance(item, TextMessage):               # skip internal events
                    yield f"data: {json.dumps({'source': item.source, 'content': item.content})}\n\n"
        except Exception as exc:                                  # surface errors in-stream (headers already sent)
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
    return StreamingResponse(events(), media_type="text/event-stream")

if __name__ == "__main__":
    c = TestClient(app)
    print(c.post("/chat", json={"session_id": "s1", "task": "duty?"}).text)
    print("saved state keys:", list(STATES["s1"].keys()))
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Level | Low-level graph API | High-level crew API | High-level agent API | AgentChat high-level; Core low-level |
| Run API | graph.invoke / astream | crew.kickoff() | Runner.run / run_streamed | agent.run / run_stream |
| Termination | Graph END / recursion limit | Task completion / max_iter | max_turns on Runner | Composable TerminationConditions |
| State save | Checkpointers | Limited | Sessions (SDK feature) | team.save_state()/load_state() (you store it) |
| Streaming | Stream modes | Callbacks | Event stream | run_stream yields messages |
| Human in the loop | interrupt / breakpoints | human_input flag | Guardrails / approvals in tools | UserProxyAgent / HandoffTermination |

---

## ⚠️ Common Mistakes
❌ Mistake: Reusing one team object across unrelated users. Agents keep their conversation context.
✅ Correct: Build a team per session, or `await team.reset()`, or load saved state for the right session.

❌ Mistake: No termination condition, or only `TextMentionTermination` that the model never says.
✅ Correct: Always OR it with `MaxMessageTermination(n)` as a hard cap.

❌ Mistake: Using `reflect_on_tool_use=True` everywhere without thinking: it adds a second LLM call per tool use.
✅ Correct: Turn it on when the user needs prose; keep it off when returning raw tool output is fine.

❌ Mistake: Forgetting that exceptions during `run_stream` after the first yield cannot change the HTTP status.
✅ Correct: Send an `error` event inside the stream, or collect the result with `run()` when you want proper status codes.

---

## 🧠 Tricky Interview Question
A user closes the browser tab in the middle of a long team run. What happens, and what should you do?

Answer: The run keeps consuming tokens unless you cancel it. In FastAPI, detect the disconnect (`request.is_disconnected()` or the generator being closed) and call `cancellation_token.cancel()`; pass the same `CancellationToken` to `run_stream(..., cancellation_token=token)`. Also persist state with `save_state()` in a `finally` block if you want resume. Mention timeouts (`asyncio.wait_for`) as a second line of defence and `MaxMessageTermination` as a third, since a runaway loop is a cost incident.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What do `run()` and `run_stream()` return?
A1: `run()` returns a `TaskResult` (messages plus stop_reason). `run_stream()` is an async generator that yields messages/events and finally the `TaskResult`.

Q2: [Medium] How do you stop a team?
A2: Pass `termination_condition`; combine with `|` (OR) and `&` (AND); also `max_turns`. A `CancellationToken` stops from outside.

Q3: [Hard] How do you get token usage per request?
A3: Each LLM-produced message has `models_usage` (prompt_tokens, completion_tokens). Sum over `result.messages`, skipping `None`.

Q4: [Hard] How do you keep conversation context across HTTP requests?
A4: Persist `await team.save_state()` keyed by session id (Redis/DB) and `load_state` into a freshly built team on the next request. State is a JSON-serialisable dict.

Q5: [System Design] Design a streaming multi-agent chat backend for 1,000 concurrent users.
A5: Stateless FastAPI workers; per-session team built on demand; state in Redis; SSE or WebSocket streaming; timeouts and cancellation tokens; a cheap model for any selector; rate limiting and per-tenant token budgets from `models_usage`; metrics on stop_reason; retry only idempotent tools.

---

## 💰 Cost Impact
Each agent turn is one LLM call whose prompt contains the whole shared transcript, so cost grows roughly quadratically with turns in a team: turn k pays for about k messages of context. Formula: `tokens ~ sum over turns of (system + history_k + new_output)`. Ways to cut it: a bounded `model_context` (for example a buffered context that keeps the last N messages), short `system_message`s, `reflect_on_tool_use=False` when possible, cheap models for routing, and hard `MaxMessageTermination`. Numbers printed in the offline examples come from the replay client and are not billing figures. Real prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Most chat/tool-calling agents and small teams.
- You want streaming, termination, state saving without writing runtime code.
- Prototype fast, then drop to Core only if needed.

❌ Avoid when:
- You need event-driven pub-sub across processes: use Core.
- You need exact graph control with checkpoints and branching: consider LangGraph.
- Single prompt with no tools: a direct model client call is simpler.

---

## 📊 Visual Diagram
```
 FastAPI /chat
     |
     v
 build_team()  <-- load_state(session)          +---------------------+
     |                                          |  TerminationCondition|
     v                                          +----------^----------+
 RoundRobinGroupChat([writer, reviewer]) ----------------+  |
     |  run_stream(task)                                    |
     |--> TextMessage(user) --> writer(LLM) --> reviewer(LLM) --> "APPROVE"
     v
 TaskResult(messages, stop_reason)  --> save_state(session) --> SSE events to client
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AssistantAgent | LLM agent with tools | tools वाला LLM agent |
| Team | Group of agents with a turn policy | turn नियम वाला agents का समूह |
| TerminationCondition | Rule that ends a run | run रोकने का नियम |
| TaskResult | Final result: messages + stop_reason | final result: messages + stop_reason |
| run_stream | Async generator of events | events का async generator |
| Console | Helper that prints a stream | stream print करने वाला helper |
| save_state | Serialise team state to a dict | team state को dict में सहेजना |
| models_usage | Token counts on a message | message पर token गिनती |

---

## ⚡ 3-Line Summary
English: AgentChat gives agents, teams, termination, streaming and state in a few lines.
Always combine a semantic stop (APPROVE) with a hard cap (MaxMessageTermination).
Build per session, save and load state, and read `models_usage` for cost.
Hindi: AgentChat कुछ ही lines में agents, teams, termination, streaming और state देता है।
हमेशा semantic stop (APPROVE) के साथ hard cap (MaxMessageTermination) जोड़ें।
हर session के लिए team बनाएँ, state save/load करें और cost के लिए `models_usage` पढ़ें।

---

## ➡️ Next Topic
130. ConversableAgent -- the v0.2 workhorse; you need to know what replaced it in v0.4 (a very common interview trap).

---
