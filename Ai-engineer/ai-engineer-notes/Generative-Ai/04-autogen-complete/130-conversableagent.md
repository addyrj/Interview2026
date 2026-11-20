---

# 130. ConversableAgent
# हिंदी में: ConversableAgent (v0.2 का मुख्य agent और v0.4 में उसकी जगह)
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
`ConversableAgent` is the v0.2 base class for agents that can send and receive messages, call an LLM, run tools and execute code. It does not exist in AutoGen v0.4 (checked in `autogen-agentchat` 0.7.5: the name is not exported). The v0.4 equivalents are `BaseChatAgent` (build your own agent) and `AssistantAgent` (LLM + tools).

## 🔵 सरल परिभाषा (Hindi)
`ConversableAgent` v0.2 की base class है: ऐसे agents जो messages भेज/पा सकें, LLM call करें, tools और code चला सकें। AutoGen v0.4 में यह class नहीं है (`autogen-agentchat` 0.7.5 में जाँचा: नाम export ही नहीं होता)। v0.4 में इसकी जगह `BaseChatAgent` (अपना agent बनाने के लिए) और `AssistantAgent` (LLM + tools) हैं।

---

## 🔴 Problem it Solves
In v0.2 one fat class did everything: reply functions, human input mode, code execution config, termination via `is_termination_msg`, auto-reply counts. It was flexible but hard to reason about and impossible to test without an LLM. v0.4 separates concerns: `BaseChatAgent` is a small contract (`on_messages`, `on_reset`, `produced_message_types`), and behaviours like termination live in teams.

## 🔴 यह क्यों बना? (Hindi)
v0.2 में एक भारी class सब कुछ करती थी: reply functions, human input mode, code execution config, `is_termination_msg` से termination, auto-reply count। यह flexible थी पर समझना कठिन और बिना LLM के test करना असंभव। v0.4 ने चिंताएँ अलग कीं: `BaseChatAgent` छोटा contract है (`on_messages`, `on_reset`, `produced_message_types`) और termination जैसे व्यवहार teams में हैं।

---

## 🟢 How it Works

```
Step 1 -> v0.2 ConversableAgent(name, system_message, llm_config, human_input_mode, code_execution_config, max_consecutive_auto_reply)
Step 2 -> v0.4 mapping: LLM + tools        -> AssistantAgent
Step 3 -> v0.4 mapping: human_input_mode   -> UserProxyAgent (+ input_func)
Step 4 -> v0.4 mapping: code_execution_config -> CodeExecutorAgent(code_executor=...)
Step 5 -> v0.4 mapping: custom reply function -> subclass BaseChatAgent, implement on_messages
Step 6 -> v0.4 mapping: is_termination_msg / max_consecutive_auto_reply -> termination_condition on the team
Step 7 -> Custom agent: on_messages(messages, token) -> Response(chat_message=TextMessage(...))
Step 8 -> Optional: on_messages_stream yields intermediate events then a final Response
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> v0.2 ConversableAgent(name, system_message, llm_config, human_input_mode, code_execution_config, max_consecutive_auto_reply)
Step 2 -> v0.4 mapping: LLM + tools        -> AssistantAgent
Step 3 -> v0.4 mapping: human_input_mode   -> UserProxyAgent (+ input_func)
Step 4 -> v0.4 mapping: code_execution_config -> CodeExecutorAgent(code_executor=...)
Step 5 -> v0.4 mapping: custom reply function -> BaseChatAgent को subclass करके on_messages लिखो
Step 6 -> v0.4 mapping: is_termination_msg / max_consecutive_auto_reply -> team पर termination_condition
Step 7 -> Custom agent: on_messages(messages, token) -> Response(chat_message=TextMessage(...))
Step 8 -> optional: on_messages_stream बीच के events yield करके आखिर में Response देता है
```

---

## 🟡 Real World Example
**Rule-based Tariff agent.** Not every agent needs an LLM. A `BaseChatAgent` that looks up HS codes in a table answers instantly, costs zero tokens and is perfectly deterministic. In a team it sits next to an LLM `AssistantAgent` that writes the customer-friendly summary. This 'hybrid' pattern is how you cut cost and hallucination.

## 🟡 Real Example Hindi mein
**Rule-based Tariff agent.** हर agent को LLM नहीं चाहिए। `BaseChatAgent` जो HS code को table में खोजता है, तुरंत जवाब देता है, 0 tokens लेता है और पूरी तरह deterministic है। Team में यह LLM वाले `AssistantAgent` के साथ बैठता है जो customer के लिए summary लिखता है। यही 'hybrid' pattern cost और hallucination घटाता है।

---

## 💻 Code Example — Basic
Basic: a custom `BaseChatAgent` with no LLM: the closest thing to a v0.2 `ConversableAgent` with a custom reply function.

```python
# v0.2 ConversableAgent has NO class in v0.4. Closest: BaseChatAgent (custom) or AssistantAgent.
import asyncio                                                    # async
from typing import Sequence                                       # typing
from autogen_agentchat.agents import BaseChatAgent               # base class you subclass
from autogen_agentchat.base import Response                       # return type of on_messages
from autogen_agentchat.messages import BaseChatMessage, TextMessage  # message types
from autogen_core import CancellationToken                        # cooperative cancel

class RuleBasedTariffAgent(BaseChatAgent):                        # a "conversable" agent with NO LLM
    def __init__(self, name: str) -> None:
        super().__init__(name, description="Answers HS-code questions from a table")  # name + description (used by selectors)
        self._table = {"6109.10": "20%"}                          # data

    @property
    def produced_message_types(self) -> Sequence[type[BaseChatMessage]]:
        return (TextMessage,)                                     # declare what we emit

    async def on_messages(self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken) -> Response:
        text = messages[-1].to_text()                             # last incoming message as text
        code = next((c for c in self._table if c in text), None)  # find a known HS code in it
        reply = f"rate={self._table[code]}" if code else "unknown code"  # decide
        return Response(chat_message=TextMessage(content=reply, source=self.name))  # reply message

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass                                                      # nothing to clear (stateless)

async def main() -> None:
    agent = RuleBasedTariffAgent("rules")                         # build
    result = await agent.run(task="Duty for 6109.10?")            # same run() API as every agent
    print(result.messages[-1].content)                            # rate=20%

if __name__ == "__main__":
    asyncio.run(main())
```

## 💻 Code Example — Advanced
Advanced: a stateful custom agent that streams an intermediate event (`on_messages_stream`), persists its own state (`save_state`/`load_state`) and sits in a team beside an LLM agent behind FastAPI.

```python
# Custom agent with internal state + streaming + FastAPI + error handling (mix LLM-free and LLM agents in one team)
import asyncio                                                    # async
from typing import AsyncGenerator, Sequence                       # typing
from fastapi import FastAPI, HTTPException                        # web
from fastapi.testclient import TestClient                         # offline test
from autogen_agentchat.agents import AssistantAgent, BaseChatAgent  # agents
from autogen_agentchat.base import Response                       # response type
from autogen_agentchat.conditions import MaxMessageTermination    # stop rule
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage, TextMessage  # messages
from autogen_agentchat.teams import RoundRobinGroupChat           # team
from autogen_core import CancellationToken                        # cancel token
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

class CountingLookupAgent(BaseChatAgent):                         # stateful custom agent
    def __init__(self, name: str) -> None:
        super().__init__(name, description="Rate lookup with call counter")
        self.calls = 0                                            # state that must survive between turns

    @property
    def produced_message_types(self) -> Sequence[type[BaseChatMessage]]:
        return (TextMessage,)

    async def on_messages(self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken) -> Response:
        final: Response | None = None
        async for item in self.on_messages_stream(messages, cancellation_token):  # reuse the streaming path
            if isinstance(item, Response):
                final = item
        assert final is not None
        return final

    async def on_messages_stream(self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken
                                 ) -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]:
        self.calls += 1                                           # mutate state
        yield TextMessage(content="looking up...", source=self.name)  # intermediate event (streamed to the UI)
        await asyncio.sleep(0)                                    # real code would await a DB/API here
        yield Response(chat_message=TextMessage(content=f"rate=20% (call #{self.calls})", source=self.name))

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        self.calls = 0                                            # reset() clears state

    async def save_state(self) -> dict:                           # persist custom state
        return {"calls": self.calls}
    async def load_state(self, state: dict) -> None:              # restore it
        self.calls = state.get("calls", 0)

app = FastAPI()

@app.get("/rate")
async def rate(q: str) -> dict:
    lookup = CountingLookupAgent("lookup")                        # custom, no tokens spent
    summarizer = AssistantAgent("summarizer", ReplayChatCompletionClient(["Summary: duty is 20%."]))  # LLM agent (fake here)
    team = RoundRobinGroupChat([lookup, summarizer], termination_condition=MaxMessageTermination(4))
    try:
        res = await asyncio.wait_for(team.run(task=q), timeout=15)  # bounded wait
    except Exception as exc:
        raise HTTPException(500, f"team failed: {exc}")
    return {"messages": [{"source": m.source, "content": str(m.content)} for m in res.messages]}

if __name__ == "__main__":
    print(TestClient(app).get("/rate", params={"q": "duty for 6109.10"}).json())
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Base agent class | Node function / Runnable | Agent (role, goal, backstory) | Agent dataclass | BaseChatAgent (v0.4); ConversableAgent (v0.2 only) |
| Custom non-LLM logic | Any node | Custom tool/agent subclass | Plain Python in tools | Subclass BaseChatAgent |
| Human in loop | interrupt | human_input | Approvals in tools | UserProxyAgent |
| Code execution | Tool node | Code interpreter tool | Hosted tool/own tool | CodeExecutorAgent |
| Stop rules | Graph edges | max_iter | max_turns | Team termination conditions |
| Reset/state | Checkpointer | Limited | Sessions | on_reset / save_state / load_state |

---

## ⚠️ Common Mistakes
❌ Mistake: Copy-pasting `ConversableAgent(...)` into a v0.4 project: ImportError.
✅ Correct: Use `AssistantAgent` for LLM agents or subclass `BaseChatAgent` for custom logic.

❌ Mistake: Using `is_termination_msg` / `max_consecutive_auto_reply` in v0.4.
✅ Correct: Use `termination_condition=TextMentionTermination(...) | MaxMessageTermination(n)` on the team.

❌ Mistake: Forgetting `produced_message_types` and `on_reset` when subclassing `BaseChatAgent`: both are abstract.
✅ Correct: Implement all three: `produced_message_types`, `on_messages`, `on_reset`.

❌ Mistake: Keeping agent state outside `save_state`: after resume the counter or cache is lost.
✅ Correct: Override `save_state`/`load_state` for custom fields.

---

## 🧠 Tricky Interview Question
A v0.2 `ConversableAgent` used `register_reply` to intercept messages and answer with Python code. How do you port it?

Answer: Create a `BaseChatAgent` subclass. Move the reply function body into `on_messages`, return a `Response(chat_message=TextMessage(...))`. If the old function sometimes returned `(False, None)` to fall through to the LLM, you now compose two agents in a team (rule agent first, LLM agent second) or call a model client inside your agent when the rule does not match. Termination logic moves to the team. Test it without an LLM by calling `await agent.run(task='...')` directly, something v0.2 made hard.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Does `ConversableAgent` exist in v0.4?
A1: No. In `autogen-agentchat` 0.7.5 `hasattr(agents, 'ConversableAgent')` is False. Use `AssistantAgent` or `BaseChatAgent`.

Q2: [Medium] What methods must a `BaseChatAgent` subclass implement?
A2: `produced_message_types` (property), `on_messages(messages, cancellation_token) -> Response`, and `on_reset(cancellation_token)`.

Q3: [Hard] What is the benefit of a non-LLM agent in a team?
A3: Zero tokens, deterministic output, millisecond latency; use it for rules, lookups, validation, routing; keep the LLM for language tasks.

Q4: [Hard] How do you stream partial results from a custom agent?
A4: Override `on_messages_stream` as an async generator: yield events or messages, and yield a final `Response`. `on_messages` can reuse it.

Q5: [System Design] Design a hybrid team for tariff classification.
A5: Rule agent (exact HS table match, 0 tokens) -> if no match, LLM agent with a retrieval tool -> reviewer agent validates code format with regex -> `HandoffTermination` or `UserProxyAgent` for low-confidence cases. Track which path answered, to measure the LLM share of traffic and cost.

---

## 💰 Cost Impact
A custom `BaseChatAgent` that does not call a model costs 0 tokens. That is the whole point: in a 3-agent team where one agent is rule-based, you remove roughly one third of the LLM calls and also shrink later prompts because that agent's replies are short. Formula: `team_cost = llm_agent_turns * (history_tokens * in_price + out_tokens * out_price)`. Prices: approximate, from public pricing at time of writing -- verify. Note: if your custom agent calls a model client, it must report its own usage; nothing counts tokens for you automatically.

---

## 🔷 When to Use
✅ Use when:
- You are porting v0.2 code that used ConversableAgent/register_reply.
- You need a deterministic or rule-based participant.
- You need a custom agent type with its own state.

❌ Avoid when:
- A plain LLM+tools agent: use `AssistantAgent`.
- Heavy logic that really is a workflow: a graph framework may be clearer.

---

## 📊 Visual Diagram
```
 v0.2 ConversableAgent                        v0.4 replacements
 +---------------------------+
 | llm_config + tools        | ------------>  AssistantAgent
 | human_input_mode          | ------------>  UserProxyAgent
 | code_execution_config     | ------------>  CodeExecutorAgent
 | register_reply(fn)        | ------------>  BaseChatAgent.on_messages
 | is_termination_msg        | ------------>  Team termination_condition
 +---------------------------+
 
 Team: [RuleBasedTariffAgent(0 tokens)] -> [AssistantAgent summariser(LLM)] -> ...
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ConversableAgent | v0.2 base agent class (not in v0.4) | v0.2 की base agent class (v0.4 में नहीं) |
| BaseChatAgent | v0.4 base class for custom agents | custom agents की v0.4 base class |
| on_messages | Method returning the agent's Response | agent का Response लौटाने वाला method |
| Response | Wrapper holding the chat message | chat message वाला wrapper |
| register_reply | v0.2 hook for custom replies | v0.2 में custom reply hook |
| produced_message_types | Declares message types an agent emits | agent कौन से message types बनाता है |
| on_reset | Clears agent state | agent state साफ़ करता है |
| hybrid agent | Rules plus LLM in one workflow | rules + LLM एक workflow में |

---

## ⚡ 3-Line Summary
English: ConversableAgent is v0.2 only; in v0.4 use AssistantAgent (LLM) or subclass BaseChatAgent (custom).
Termination and human input moved out of the agent into teams and UserProxyAgent.
Rule-based agents cost zero tokens and make teams cheaper and more predictable.
Hindi: ConversableAgent सिर्फ़ v0.2 में है; v0.4 में AssistantAgent (LLM) या BaseChatAgent subclass (custom) इस्तेमाल करें।
Termination और human input agent से निकलकर teams और UserProxyAgent में चले गए।
Rule-based agents 0 tokens लेते हैं और teams को सस्ता व predictable बनाते हैं।

---

## ➡️ Next Topic
131. AssistantAgent -- the v0.4 agent you will use most: tools, structured output, handoffs, memory.

---
