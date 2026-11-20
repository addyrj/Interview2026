---

# 127. AutoGen vs v0.2 Differences
# हिंदी में: AutoGen v0.4 और पुराने v0.2 में अंतर
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
AutoGen v0.2 (package `pyautogen`) was a synchronous, chat-centric library built around `ConversableAgent`, `initiate_chat` and `llm_config` dictionaries. AutoGen v0.4 (packages `autogen-agentchat`, `autogen-core`, `autogen-ext`) is a rewrite: asynchronous, event-driven (actor model), layered (Core / AgentChat / Extensions) and with typed model clients.

## 🔵 सरल परिभाषा (Hindi)
AutoGen v0.2 (package `pyautogen`) एक synchronous, chat-आधारित library थी जो `ConversableAgent`, `initiate_chat` और `llm_config` dict पर टिकी थी। AutoGen v0.4 (packages `autogen-agentchat`, `autogen-core`, `autogen-ext`) पूरा rewrite है: async, event-driven (actor model), तीन layers (Core / AgentChat / Extensions) और typed model clients के साथ।

---

## 🔴 Problem it Solves
v0.2 had real production pain: blocking `initiate_chat` calls that fight FastAPI's event loop, untyped `llm_config` dicts that fail at runtime, agents tightly coupled to a single in-process conversation, hard-to-test code that always needed a live LLM, and no clean way to distribute agents across processes or languages. In interviews, candidates who mix v0.2 and v0.4 APIs (very common in old blog posts) fail the 'do you actually know current AutoGen' check.

## 🔴 यह क्यों बना? (Hindi)
v0.2 में असली production दिक्कतें थीं: blocking `initiate_chat` जो FastAPI के event loop से टकराता है, untyped `llm_config` dict जो runtime पर फेल होती थी, agents एक ही process की conversation से कसकर जुड़े थे, testing के लिए हमेशा live LLM चाहिए था, और agents को अलग processes या languages में बाँटना मुश्किल था। Interview में पुराने blogs से v0.2 और v0.4 के APIs मिला देना सबसे आम गलती है।

---

## 🟢 How it Works

```
Step 1 -> v0.2: pip install pyautogen -> import autogen -> llm_config dict
Step 2 -> v0.2: ConversableAgent / AssistantAgent / UserProxyAgent(human_input_mode=...)
Step 3 -> v0.2: user.initiate_chat(assistant, message=...)   (blocking, sync)
Step 4 -> v0.2: GroupChat + GroupChatManager for many agents
Step 5 -> v0.4: pip install autogen-agentchat autogen-ext[openai]
Step 6 -> v0.4: model_client = OpenAIChatCompletionClient(model=...) (object, not dict)
Step 7 -> v0.4: AssistantAgent(name, model_client, tools=[fn])  (tools passed directly)
Step 8 -> v0.4: result = await agent.run(task=...) / team.run_stream(...)
Step 9 -> v0.4: Teams (RoundRobin/Selector/Swarm/MagenticOne/GraphFlow) replace GroupChat+Manager
Step 10 -> v0.4 Core: RoutedAgent + SingleThreadedAgentRuntime for event-driven, distributed designs
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> v0.2: pip install pyautogen -> import autogen -> llm_config dict
Step 2 -> v0.2: ConversableAgent / AssistantAgent / UserProxyAgent(human_input_mode=...)
Step 3 -> v0.2: user.initiate_chat(assistant, message=...)   (blocking, sync)
Step 4 -> v0.2: कई agents के लिए GroupChat + GroupChatManager
Step 5 -> v0.4: pip install autogen-agentchat autogen-ext[openai]
Step 6 -> v0.4: model_client = OpenAIChatCompletionClient(model=...) (dict नहीं, object)
Step 7 -> v0.4: AssistantAgent(name, model_client, tools=[fn])  (tools सीधे पास)
Step 8 -> v0.4: result = await agent.run(task=...) / team.run_stream(...)
Step 9 -> v0.4: GroupChat+Manager की जगह Teams (RoundRobin/Selector/Swarm/MagenticOne/GraphFlow)
Step 10 -> v0.4 Core: event-driven और distributed design के लिए RoutedAgent + SingleThreadedAgentRuntime
```

---

## 🟡 Real World Example
**Tariff Agent migration.** Your team has a v0.2 script: a `UserProxyAgent` calls `initiate_chat` on an `AssistantAgent` that has `register_for_llm` tools for HS-code and duty lookup. You must expose it as a FastAPI service handling 200 concurrent requests. In v0.2 you would wrap the blocking call in a thread pool. In v0.4 you build an `AssistantAgent` with `tools=[get_tariff_rate]` and `await agent.run(...)` directly inside an async endpoint, with a timeout and per-request usage accounting.

## 🟡 Real Example Hindi mein
**Tariff Agent migration.** आपकी team के पास v0.2 script है: `UserProxyAgent`, `AssistantAgent` पर `initiate_chat` चलाता है, जिसमें HS-code और duty lookup के `register_for_llm` tools हैं। इसे 200 concurrent requests वाली FastAPI service बनाना है। v0.2 में आप blocking call को thread pool में लपेटते। v0.4 में `AssistantAgent` को `tools=[get_tariff_rate]` के साथ बनाकर async endpoint में सीधे `await agent.run(...)` करते हैं, timeout और per-request usage accounting के साथ।

---

## 💻 Code Example — Basic
Basic: the new v0.4 way of building a Tariff Agent. The v0.2 equivalent is kept as a comment only (not run, needs `pyautogen`).

```python
# v0.4 Tariff Agent -- the NEW way (autogen-agentchat 0.7.5, runs offline)
import asyncio                                                    # v0.4 is async-first
from autogen_agentchat.agents import AssistantAgent              # high-level agent (AgentChat layer)
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM: returns canned replies, no API key

# --- v0.2 (OLD, shown only as a comment; needs `pip install pyautogen`, NOT run here) ---
# assistant = autogen.AssistantAgent("tariff", llm_config={"config_list": [...]})
# user = autogen.UserProxyAgent("user", human_input_mode="NEVER")
# user.initiate_chat(assistant, message="Duty for HS 6109.10?")   # blocking, sync call

def get_tariff_rate(hs_code: str) -> str:                         # plain typed function = tool (type hints required)
    """Return the import duty rate for an HS code."""             # docstring becomes the tool description
    return {"6109.10": "20%"}.get(hs_code, "unknown")             # fake tariff table

async def main() -> None:                                         # entry point is a coroutine
    info = {"function_calling": True, "vision": False, "json_output": False,  # tell the fake model it supports tools
            "family": "unknown", "structured_output": False}      # required ModelInfo keys
    client = ReplayChatCompletionClient(["The duty for 6109.10 is 20%."], model_info=info)  # swap for OpenAIChatCompletionClient(model=...) in prod
    agent = AssistantAgent(                                       # build the agent
        name="tariff_agent",                                      # unique name inside a team
        model_client=client,                                      # v0.4: model client object, NOT llm_config dict
        tools=[get_tariff_rate],                                  # v0.4: tools passed directly, no register_for_llm
        system_message="You are a tariff expert.",                # system prompt
    )
    result = await agent.run(task="Duty for HS 6109.10?")         # v0.4: await run(), not initiate_chat()
    last = result.messages[-1]                                    # final message of the run
    print(last.source, "->", last.content)                        # tariff_agent -> The duty ...
    print("usage:", last.models_usage)                            # RequestUsage(prompt_tokens, completion_tokens)

if __name__ == "__main__":                                        # script entry
    asyncio.run(main())                                           # start the event loop
```

## 💻 Code Example — Advanced
Advanced: the v0.4 migration target as an async FastAPI service: a fresh team per request, timeout, error mapping to HTTP codes and token accounting from `models_usage`.

```python
# Production-style v0.4 migration target: FastAPI + async + error handling + usage tracking
import asyncio                                                    # async runtime
from typing import Any                                            # type hints
from fastapi import FastAPI, HTTPException                        # web framework
from fastapi.testclient import TestClient                         # lets us call the API without a server
from pydantic import BaseModel                                    # request/response validation
from autogen_agentchat.agents import AssistantAgent               # AgentChat agent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination  # stop rules
from autogen_agentchat.teams import RoundRobinGroupChat           # simplest team
from autogen_ext.models.replay import ReplayChatCompletionClient  # offline fake LLM

app = FastAPI(title="Tariff service (AutoGen v0.4)")              # one app object

class AskRequest(BaseModel):                                      # input schema
    question: str                                                 # user question

class AskResponse(BaseModel):                                     # output schema
    answer: str                                                   # final text
    prompt_tokens: int                                            # token accounting
    completion_tokens: int                                        # token accounting

def build_team() -> RoundRobinGroupChat:                          # NEW team per request (agents hold state!)
    client = ReplayChatCompletionClient(["Duty is 20%.", "APPROVE"])  # replace with a real client in prod
    worker = AssistantAgent("worker", model_client=client)        # answers
    reviewer = AssistantAgent("reviewer", model_client=ReplayChatCompletionClient(["APPROVE"]))  # approves
    stop = TextMentionTermination("APPROVE") | MaxMessageTermination(6)  # combine conditions with |
    return RoundRobinGroupChat([worker, reviewer], termination_condition=stop)  # v0.2 GroupChat equivalent

@app.post("/ask", response_model=AskResponse)                     # async endpoint
async def ask(req: AskRequest) -> AskResponse:
    team = build_team()                                           # fresh state per request
    try:
        result = await asyncio.wait_for(team.run(task=req.question), timeout=30)  # never wait forever
    except asyncio.TimeoutError:                                  # model/tool hung
        raise HTTPException(status_code=504, detail="agent timeout")
    except Exception as exc:                                      # any framework error
        raise HTTPException(status_code=500, detail=f"agent failed: {exc}")
    pt = ct = 0                                                   # token counters
    for m in result.messages:                                     # walk the transcript
        usage: Any = getattr(m, "models_usage", None)             # only LLM messages carry usage
        if usage:                                                 # skip the user task message
            pt += usage.prompt_tokens                             # sum prompt tokens
            ct += usage.completion_tokens                         # sum completion tokens
    answer = next(str(m.content) for m in result.messages if m.source == "worker")  # worker reply
    return AskResponse(answer=answer, prompt_tokens=pt, completion_tokens=ct)  # typed response

if __name__ == "__main__":                                        # demo without uvicorn
    print(TestClient(app).post("/ask", json={"question": "Duty for 6109.10?"}).json())
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Programming model | Graph of nodes + state | Role/task/crew objects | Agent + Runner loop | v0.4: async agents + event runtime (v0.2: sync chat) |
| Async support | Yes (ainvoke) | Partial (kickoff_async) | Yes (Runner.run) | v0.4 async-first; v0.2 sync only |
| Multi-agent | Explicit edges/Send | Crew processes | Handoffs / agents-as-tools | Teams (v0.4), GroupChat (v0.2) |
| Tools | bind_tools / ToolNode | @tool / Tool classes | @function_tool | tools=[fn] (v0.4), register_for_llm (v0.2) |
| Offline testing | Fake chat models | Mock LLMs, harder | Custom Model class | ReplayChatCompletionClient (v0.4) |
| Distributed | LangGraph Platform | Not core | Not core | Core runtime supports gRPC workers |

---

## ⚠️ Common Mistakes
❌ Mistake: Following a 2023 blog and writing `import autogen; autogen.AssistantAgent(llm_config=...)` against a v0.4 install.
✅ Correct: Check the package: `autogen-agentchat` uses `from autogen_agentchat.agents import AssistantAgent` and `model_client=`.

❌ Mistake: Calling `initiate_chat` or `register_for_llm` on v0.4 objects.
✅ Correct: Use `await agent.run(task=...)` and pass `tools=[...]` at construction.

❌ Mistake: Assuming `ConversableAgent`, `GroupChatManager` and `MultimodalConversableAgent` exist in v0.4. In 0.7.5 none of them is exported (checked with `hasattr`).
✅ Correct: Map them: ConversableAgent -> BaseChatAgent/AssistantAgent, GroupChatManager -> internal to a team, Multimodal -> MultiModalMessage with a vision model.

❌ Mistake: Mixing `pyautogen` and `autogen-agentchat` in one environment. Both claim the `autogen` import namespace in different ways.
✅ Correct: Use one virtualenv per version; migrate module by module.

---

## 🧠 Tricky Interview Question
Interviewer: 'We have 30 v0.2 agents. Do we migrate to v0.4 or switch framework?'

Answer: A good answer is a decision, not a preference. (1) Inventory: which agents are chat-style (map to `AssistantAgent` + a team) and which need custom control flow (map to `BaseChatAgent` or Core `RoutedAgent`). (2) Check maintenance status of AutoGen versus Microsoft's newer agent framework and the community AG2 fork on their release pages at decision time, because this changes quickly (verify). (3) Estimate migration cost: the API surface changes (async, model_client, tools, termination conditions), but the prompts and tool functions carry over almost unchanged. (4) Build a thin adapter: keep your tool functions framework-free, so they work in v0.4, LangGraph or OpenAI SDK. (5) Migrate the most-used flow first behind a feature flag and compare outputs on a fixed eval set. The signal the interviewer wants: you separate prompts and tools (portable) from orchestration (not portable).

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is the biggest architectural change from v0.2 to v0.4?
A1: v0.4 is a rewrite into three layers (Core, AgentChat, Extensions) built on an async, event-driven actor runtime. v0.2 was a synchronous conversation object model around `ConversableAgent.initiate_chat`.

Q2: [Medium] How do you define a tool in v0.4 compared with v0.2?
A2: v0.2: decorate with `register_for_llm` on one agent and `register_for_execution` on another. v0.4: pass a typed Python function (or `FunctionTool`) in `tools=[...]` of `AssistantAgent`; the same agent calls and executes it.

Q3: [Hard] What replaced `GroupChat` and `GroupChatManager`?
A3: Teams: `RoundRobinGroupChat`, `SelectorGroupChat`, `Swarm`, `MagenticOneGroupChat`, `GraphFlow`. The manager role exists internally (for example `SelectorGroupChatManager`) and you configure it via team parameters: termination_condition, max_turns, selector_func.

Q4: [Hard] Why can't you just call `initiate_chat` inside a FastAPI endpoint in v0.2?
A4: It is blocking: it ties up the event loop (or a thread). You need a thread pool and manual cancellation. v0.4 methods are coroutines with a `CancellationToken`, so they fit `async def` handlers and `asyncio.wait_for`.

Q5: [System Design] Design a migration plan for a production v0.2 service with zero downtime.
A5: Keep tools and prompts framework-agnostic; build a v0.4 implementation behind the same HTTP contract; shadow-run both on mirrored traffic and compare answers and cost with an eval set; roll out with a feature flag by tenant; keep v0.2 in a separate virtualenv/container until parity is proven; then remove it.

---

## 💰 Cost Impact
Migration itself does not change per-call token cost much; what changes is control. v0.4 gives you `models_usage` on every LLM message, so you can sum prompt and completion tokens per request. Formula: `cost = (prompt_tokens * input_price + completion_tokens * output_price) / 1e6`. Prices differ by model and change often (approximate, from public pricing at time of writing -- verify). Typical savings come from: a cheaper model for the selector in teams, `reflect_on_tool_use=False` when the raw tool output is enough (saves one LLM call), and termination conditions that stop loops early. A 3-agent round-robin that runs until `MaxMessageTermination(12)` can cost several times more than one that stops on `TextMentionTermination('APPROVE')` after 3 turns.

---

## 🔷 When to Use
✅ Use when:
- You are starting a new AutoGen project: use v0.4+ (`autogen-agentchat`).
- You need async FastAPI integration, streaming and cancellation.
- You want offline tests with `ReplayChatCompletionClient`.
- You need agents in different processes (Core runtime).

❌ Avoid when:
- You depend on v0.2-only features or the `autogen.` namespace plugins: pin `pyautogen` in an isolated environment instead.
- You mix both versions in one virtualenv.
- You need graph-level durable checkpoints and time travel: consider LangGraph for that part.

---

## 📊 Visual Diagram
```
 v0.2 (pyautogen)                       v0.4 (autogen-agentchat/core/ext)
 ----------------                       ---------------------------------
 llm_config dict                        model_client object
      |                                        |
 ConversableAgent  <-- initiate_chat    AssistantAgent  --await run()-->  TaskResult
      |  (sync, blocking)                      |  tools=[fn]                    |
 GroupChat + GroupChatManager           Team (RoundRobin / Selector / Swarm)  |
      |                                        |                              v
   chat history                        Core: RoutedAgent + Runtime      messages + models_usage
                                        (events, topics, subscriptions)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pyautogen | The v0.2 PyPI package | v0.2 वाला package |
| autogen-agentchat | High-level v0.4 package with agents and teams | v0.4 का high-level package |
| autogen-core | Event-driven runtime layer | Event-driven runtime layer |
| autogen-ext | Extensions: model clients, executors, tools | Extensions: model clients, executors, tools |
| llm_config | v0.2 dict with model + keys | v0.2 की config dict |
| model_client | v0.4 typed object that calls the LLM | LLM को call करने वाला typed object |
| initiate_chat | v0.2 blocking chat start | v0.2 में chat शुरू करने वाला blocking call |
| Team | v0.4 group of agents with a turn policy | agents का समूह + turn नियम |

---

## ⚡ 3-Line Summary
English: AutoGen v0.4 is a ground-up async, layered rewrite of v0.2; the APIs are not compatible.
Tools and prompts migrate easily, orchestration (initiate_chat, GroupChat) must be rewritten as `run()` and teams.
Always check which package (`pyautogen` vs `autogen-agentchat`) a tutorial uses before copying code.
Hindi: AutoGen v0.4, v0.2 का पूरा async और layered rewrite है; दोनों के APIs compatible नहीं हैं।
Tools और prompts आसानी से migrate होते हैं, orchestration (initiate_chat, GroupChat) को `run()` और teams में दोबारा लिखना पड़ता है।
कोई भी tutorial कॉपी करने से पहले देखें कि वह `pyautogen` है या `autogen-agentchat`।

---

## ➡️ Next Topic
128. Core Concepts v0.4 -- the Core layer (agents, messages, runtime, topics) is what everything else is built on, and interviews love asking 'how does the runtime actually deliver messages'.

---
