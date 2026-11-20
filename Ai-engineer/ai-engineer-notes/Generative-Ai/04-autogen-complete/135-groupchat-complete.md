---

# 135. GroupChat — Complete
# हिंदी में: GroupChat — पूरा विवरण (v0.4 में Teams)
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
A group chat lets several agents share one conversation and take turns. In v0.2 this was `GroupChat` + `GroupChatManager`. In v0.4 AgentChat the equivalent is a team: `RoundRobinGroupChat` (fixed order), `SelectorGroupChat` (LLM or function picks the next speaker), `Swarm` (agents hand off to each other), `MagenticOneGroupChat` (orchestrated general-purpose team) and `GraphFlow` (directed graph of agents).

## 🔵 सरल परिभाषा (Hindi)
Group chat में कई agents एक ही conversation साझा करते हैं और बारी-बारी बोलते हैं। v0.2 में यह `GroupChat` + `GroupChatManager` था। v0.4 AgentChat में इसके बराबर teams हैं: `RoundRobinGroupChat` (तय क्रम), `SelectorGroupChat` (LLM या function अगला speaker चुनता है), `Swarm` (agents एक-दूसरे को handoff करते हैं), `MagenticOneGroupChat` (orchestrated general-purpose team) और `GraphFlow` (agents का directed graph)।

---

## 🔴 Problem it Solves
One agent with 20 tools and a giant prompt becomes confused and expensive. Splitting roles (classifier, rater, compliance, reviewer) gives smaller prompts, specialised tools and checks and balances. The problem is coordination: who speaks next, when to stop, how to keep the shared history manageable. Group chat provides these mechanics.

## 🔴 यह क्यों बना? (Hindi)
20 tools और विशाल prompt वाला एक agent उलझ जाता है और महँगा पड़ता है। Roles बाँटने (classifier, rater, compliance, reviewer) से prompts छोटे, tools विशेष और checks-and-balances मिलते हैं। समस्या coordination की है: अगला कौन बोले, कब रुके, साझा history कैसे संभले। Group chat यह mechanics देता है।

---

## 🟢 How it Works

```
Step 1 -> Create specialised agents with clear names and descriptions
Step 2 -> Choose a team type: RoundRobin | Selector | Swarm | MagenticOne | GraphFlow
Step 3 -> Add termination_condition (semantic + hard cap) and/or max_turns
Step 4 -> run_stream(task): the task goes to every agent's context
Step 5 -> Manager picks the next speaker per the team policy
Step 6 -> Speaker's reply is broadcast to all participants (shared thread)
Step 7 -> Termination checked after each message; stop_reason recorded
Step 8 -> Result = ordered messages; read models_usage for cost
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> साफ़ names और descriptions वाले specialised agents बनाओ
Step 2 -> team type चुनो: RoundRobin | Selector | Swarm | MagenticOne | GraphFlow
Step 3 -> termination_condition (semantic + hard cap) और/या max_turns जोड़ो
Step 4 -> run_stream(task): task हर agent के context में जाता है
Step 5 -> Manager team policy से अगला speaker चुनता है
Step 6 -> Speaker का जवाब सभी participants को broadcast होता है (साझा thread)
Step 7 -> हर message के बाद termination जाँच; stop_reason दर्ज होता है
Step 8 -> नतीजा = क्रम में messages; cost के लिए models_usage पढ़ो
```

---

## 🟡 Real World Example
**Tariff team.** `classifier` finds the HS code, `rater` gives the duty for that code, `checker` reviews and says APPROVE. With `RoundRobinGroupChat` the order is fixed, which is predictable and cheap. When a request needs compliance only sometimes (restricted goods), switch to `SelectorGroupChat` so the compliance agent speaks only when relevant.

## 🟡 Real Example Hindi mein
**Tariff team.** `classifier` HS code खोजता है, `rater` उस code की duty बताता है, `checker` जाँचकर APPROVE कहता है। `RoundRobinGroupChat` में क्रम तय रहता है, जो predictable और सस्ता है। जब compliance सिर्फ़ कभी-कभी चाहिए (restricted goods), तब `SelectorGroupChat` लें ताकि compliance agent तभी बोले जब ज़रूरी हो।

---

## 💻 Code Example — Basic
Basic: a 3-agent `RoundRobinGroupChat` with scripted replies, printed with `Console`. Termination = APPROVE OR a hard cap of 10 messages.

```python
# Group chat in v0.4 = "teams". RoundRobinGroupChat: fixed turn order, shared transcript.
import asyncio                                                    # async
from autogen_agentchat.agents import AssistantAgent               # agent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination  # stop rules
from autogen_agentchat.teams import RoundRobinGroupChat           # team
from autogen_agentchat.ui import Console                          # printer
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

async def main() -> None:
    classifier = AssistantAgent("classifier", ReplayChatCompletionClient(["HS code: 6109.10"]), system_message="Classify goods.")
    rater = AssistantAgent("rater", ReplayChatCompletionClient(["Duty on 6109.10 is 20%."]), system_message="Give duty rate.")
    checker = AssistantAgent("checker", ReplayChatCompletionClient(["Looks right. APPROVE"]), system_message="Review. Say APPROVE when correct.")
    team = RoundRobinGroupChat(
        [classifier, rater, checker],                             # order of speaking
        termination_condition=TextMentionTermination("APPROVE") | MaxMessageTermination(10),  # ALWAYS add a hard cap
    )
    await Console(team.run_stream(task="Duty on a cotton t-shirt?"))

if __name__ == "__main__":
    asyncio.run(main())
```

## 💻 Code Example — Advanced
Advanced: a `SelectorGroupChat` behind FastAPI with a separate selector model client, cancellation token, timeout and token totals from `models_usage` (the number printed offline is a replay estimate).

```python
# Selector group chat service: LLM (or function) picks the next speaker. FastAPI + usage totals + cancel.
import asyncio                                                    # async
from fastapi import FastAPI, HTTPException                        # web
from fastapi.testclient import TestClient                         # offline test
from autogen_agentchat.agents import AssistantAgent               # agent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination  # stop rules
from autogen_agentchat.teams import SelectorGroupChat             # team with a selector
from autogen_core import CancellationToken                        # cancel a run
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

app = FastAPI()

def build() -> SelectorGroupChat:
    agents = [
        AssistantAgent("classifier", ReplayChatCompletionClient(["HS 6109.10"]), description="Finds the HS code"),   # description is what the selector reads!
        AssistantAgent("rater", ReplayChatCompletionClient(["Duty 20%. APPROVE"]), description="Gives duty rate for an HS code"),
    ]
    selector_llm = ReplayChatCompletionClient(["classifier", "rater"])  # scripted speaker choices (real: a cheap model)
    return SelectorGroupChat(agents, model_client=selector_llm,
                             termination_condition=TextMentionTermination("APPROVE") | MaxMessageTermination(8))

@app.post("/group")
async def group(body: dict) -> dict:
    team = build()
    token = CancellationToken()                                   # call token.cancel() from another task to abort
    try:
        res = await asyncio.wait_for(team.run(task=body["task"], cancellation_token=token), timeout=60)
    except asyncio.TimeoutError:
        token.cancel()                                            # stop in-flight LLM calls
        raise HTTPException(504, "group chat timeout")
    tokens = sum((m.models_usage.prompt_tokens + m.models_usage.completion_tokens) for m in res.messages if m.models_usage)
    return {"speakers": [m.source for m in res.messages], "stop": res.stop_reason, "agent_tokens": tokens}

if __name__ == "__main__":
    print(TestClient(app).post("/group", json={"task": "duty for cotton t-shirt"}).json())
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Group abstraction | Subgraph / supervisor pattern | Crew + Process | Handoffs / manager agent as tool | Teams (RoundRobin/Selector/Swarm/MagenticOne/GraphFlow) |
| Dynamic routing | Conditional edges | Hierarchical process | LLM handoff | SelectorGroupChat / selector_func |
| Fixed pipeline | Linear edges | Sequential process | Chain of agents | RoundRobin / GraphFlow |
| Shared history | Shared state | Task context passing | Per-agent context | Shared broadcast thread |
| Stop rules | END / limits | Task done / max_iter | max_turns | Composable termination conditions |
| Scale concern | State size | Token growth | Token growth | History grows quadratic cost; bound it |

---

## ⚠️ Common Mistakes
❌ Mistake: No hard cap in termination. Agents politely thank each other forever.
✅ Correct: `TextMentionTermination('APPROVE') | MaxMessageTermination(n)`.

❌ Mistake: Vague agent descriptions in a `SelectorGroupChat`: the selector LLM chooses badly because it reads descriptions.
✅ Correct: Write precise, distinct `description`s per agent.

❌ Mistake: Using a team when one agent with tools would do: 3x calls for no gain.
✅ Correct: Start with a single agent; split only when roles or tool sets conflict.

❌ Mistake: Reusing a team across requests.
✅ Correct: Build per session or `reset()`; agents keep history.

---

## 🧠 Tricky Interview Question
Your 4-agent team gives good answers but each request costs 6x the single-agent version. How do you cut cost without hurting quality?

Answer: Measure first: log tokens per agent from `models_usage`. Typical causes: every agent re-reads the whole shared history; a verbose reviewer; the selector call using a big model; redundant turns. Actions: (1) cheaper model for selector and reviewer; (2) bounded `model_context` for agents that need only the last few messages; (3) replace LLM agents that only validate with deterministic Python agents; (4) a stricter termination condition; (5) `selector_func` for the predictable parts of the flow; (6) ask whether the checker is needed on every request or only low-confidence ones. Verify quality on a fixed eval set after each change.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What replaced `GroupChat` in v0.4?
A1: Teams: `RoundRobinGroupChat`, `SelectorGroupChat`, `Swarm`, `MagenticOneGroupChat`, `GraphFlow` (all exported by `autogen_agentchat.teams` in 0.7.5).

Q2: [Medium] How is the next speaker chosen in `RoundRobinGroupChat` vs `SelectorGroupChat`?
A2: Round robin follows participant order. Selector asks a model (using agent names and descriptions and the history) or runs your `selector_func`/`candidate_func`.

Q3: [Hard] How do agents see each other's messages?
A3: Each agent's reply is broadcast to the team, so every agent's context holds the shared thread.

Q4: [Hard] What are common termination conditions?
A4: `TextMentionTermination`, `MaxMessageTermination`, `HandoffTermination`, `TokenUsageTermination`, `TimeoutTermination`, `ExternalTermination`, `SourceMatchTermination`, `StopMessageTermination`; combine with `|` and `&`. Check the installed version for the exact list.

Q5: [System Design] Design a support triage team (billing, tech, refunds) with SLAs.
A5: Swarm or Selector with a triage agent and specialists; each specialist has narrow tools; `HandoffTermination` to a human for refunds over a limit; per-conversation token and time budgets (`TokenUsageTermination`, `TimeoutTermination`); state saved per ticket; metrics: resolution rate, handoff count, cost per ticket.

---

## 💰 Cost Impact
Cost grows with number of turns and the length of the shared history: each turn re-sends the full thread to the speaking agent, so tokens grow roughly quadratically in turns. Selector teams add one selector model call per turn. Formula: `total = sum over turns (history_k * in_price + output_k * out_price) + selector_calls * selector_prompt * in_price`. Controls: hard turn caps, cheap selector model, deterministic agents, bounded context, early APPROVE. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Roles with distinct tools or prompts.
- Review/critique loops (writer + reviewer).
- Workflows with dynamic routing (selector/swarm).

❌ Avoid when:
- Tasks one agent can do in one tool call.
- Strict latency budgets: each turn is an LLM round trip.
- Unbounded open-ended chats without termination.

---

## 📊 Visual Diagram
```
 task
  |
  v
 +-------------------- Team (manager inside) --------------------+
 |  shared thread:  user -> classifier -> rater -> checker ...    |
 |                                                                |
 |  RoundRobin: fixed order          Selector: LLM/func picks     |
 |  Swarm: handoff tools             GraphFlow: DAG edges         |
 |                                                                |
 |  after every message --> TerminationCondition? --> TaskResult  |
 +----------------------------------------------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Team | AgentChat group chat object | AgentChat group chat object |
| RoundRobinGroupChat | Fixed-order team | तय क्रम वाली team |
| SelectorGroupChat | Next speaker chosen by model/func | अगला speaker model/func चुनता है |
| Swarm | Agents hand off via tools | agents tools से handoff करते हैं |
| MagenticOneGroupChat | Orchestrated generalist team | orchestrated generalist team |
| GraphFlow | Directed-graph workflow of agents | agents का directed-graph workflow |
| shared thread | Common message history | साझा message history |
| stop_reason | Why the run ended | run क्यों रुका |

---

## ⚡ 3-Line Summary
English: Group chat in v0.4 means teams: RoundRobin, Selector, Swarm, MagenticOne, GraphFlow.
Always add termination with a hard cap, and write clear agent descriptions for selectors.
Shared history makes cost grow fast: bound context and use cheap models for routing.
Hindi: v0.4 में group chat का मतलब teams है: RoundRobin, Selector, Swarm, MagenticOne, GraphFlow।
हमेशा hard cap के साथ termination जोड़ें और selectors के लिए agent descriptions साफ़ लिखें।
साझा history से cost तेज़ी से बढ़ती है: context सीमित करें और routing के लिए सस्ते models इस्तेमाल करें।

---

## ➡️ Next Topic
136. GroupChatManager -- what actually runs inside a team and how to control it.

---
