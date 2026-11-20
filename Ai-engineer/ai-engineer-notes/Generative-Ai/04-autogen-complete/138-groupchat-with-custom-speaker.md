---

# 138. GroupChat with Custom Speaker
# हिंदी में: Custom speaker logic के साथ GroupChat
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
A custom speaker policy in v0.4 is a Python function passed as `selector_func` to `SelectorGroupChat`. It receives the message history and returns the next agent's name (or `None` to let the LLM decide). It can be async. With it you implement state machines, retry loops and content-based routing with zero selector LLM calls. For handoff-style control there is also `Swarm`.

## 🔵 सरल परिभाषा (Hindi)
v0.4 में custom speaker policy एक Python function है जिसे `SelectorGroupChat` के `selector_func` में दिया जाता है। यह message history लेता है और अगले agent का नाम लौटाता है (या `None` ताकि LLM तय करे)। यह async भी हो सकता है। इससे state machines, retry loops और content-based routing बिना selector LLM call के बनते हैं। handoff-style नियंत्रण के लिए `Swarm` भी है।

---

## 🔴 Problem it Solves
LLM routing is probabilistic. For regulated flows (customs filing) you want a guaranteed order: classify, then rate, then review, and if the reviewer rejects, go back to classify. LLM selectors may skip a step or loop forever. A deterministic policy encodes the business process, while agents still use LLMs for their own work.

## 🔴 यह क्यों बना? (Hindi)
LLM routing probabilistic होती है। नियमबद्ध flows (customs filing) में गारंटीशुदा क्रम चाहिए: classify, फिर rate, फिर review, और reviewer reject करे तो वापस classify। LLM selector कोई step छोड़ सकता है या अनंत loop में जा सकता है। Deterministic policy business process को code में रखती है, जबकि agents अपने काम के लिए LLM इस्तेमाल करते रहते हैं।

---

## 🟢 How it Works

```
Step 1 -> Write selector_func(messages) -> str | None (sync or async)
Step 2 -> Look at messages[-1].source and, if needed, its text content
Step 3 -> Map state to the next speaker name (dict lookup or if/else)
Step 4 -> Return None only for 'unknown state' to allow LLM fallback
Step 5 -> Pass selector_func= to SelectorGroupChat (model_client still required)
Step 6 -> Add termination (APPROVE) AND a hard cap, because your loop can cycle
Step 7 -> Unit-test the function alone with fake messages (no LLM needed)
Step 8 -> Alternative: Swarm, where agents decide handoffs via transfer_to_<name> tools
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> selector_func(messages) -> str | None लिखो (sync या async)
Step 2 -> messages[-1].source और ज़रूरत हो तो उसका text देखो
Step 3 -> state को अगले speaker के नाम से जोड़ो (dict lookup या if/else)
Step 4 -> सिर्फ़ 'अज्ञात state' पर None लौटाओ ताकि LLM fallback हो सके
Step 5 -> SelectorGroupChat में selector_func= दो (model_client फिर भी चाहिए)
Step 6 -> termination (APPROVE) और hard cap दोनों जोड़ो, क्योंकि आपका loop चक्कर काट सकता है
Step 7 -> function को बिना LLM के fake messages से अलग से unit-test करो
Step 8 -> विकल्प: Swarm, जहाँ agents transfer_to_<name> tools से handoff तय करते हैं
```

---

## 🟡 Real World Example
**Filing workflow with retry.** classifier -> rater -> reviewer. If the reviewer's message contains APPROVE the run ends; otherwise control returns to the classifier. This is a bounded loop (hard cap 12 messages). The same logic with a pure LLM selector would sometimes skip the reviewer, which in customs means an unreviewed filing.

## 🟡 Real Example Hindi mein
**Retry वाला filing workflow।** classifier -> rater -> reviewer। Reviewer के message में APPROVE हो तो run खत्म; वरना control वापस classifier को। यह सीमित loop है (hard cap 12 messages)। यही logic सिर्फ़ LLM selector से चलाएँ तो वह कभी reviewer को छोड़ सकता है, जो customs में बिना review की filing होगी।

---

## 💻 Code Example — Basic
Basic: a dict-based state machine as `selector_func`. The selector model is an empty replay client, proving it is never called.

```python
# Custom speaker selection with selector_func: a deterministic Tariff workflow state machine (no selector LLM calls)
import asyncio                                                    # async
from typing import Sequence                                       # typing
from autogen_agentchat.agents import AssistantAgent               # agent
from autogen_agentchat.conditions import MaxMessageTermination    # stop rule
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage  # message types
from autogen_agentchat.teams import SelectorGroupChat            # team
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

NEXT = {"user": "classifier", "classifier": "rater", "rater": "reviewer"}  # who speaks after whom

def selector_func(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
    return NEXT.get(messages[-1].source)                          # return a NAME to force; return None to fall back to the LLM selector

async def main() -> None:
    agents = [AssistantAgent(n, ReplayChatCompletionClient([f"{n} done"])) for n in ("classifier", "rater", "reviewer")]
    team = SelectorGroupChat(
        agents,
        model_client=ReplayChatCompletionClient([]),              # never called because selector_func always answers
        selector_func=selector_func,
        termination_condition=MaxMessageTermination(4),           # user + 3 agents
    )
    res = await team.run(task="Duty for cotton t-shirt?")
    print([m.source for m in res.messages])                       # ['user','classifier','rater','reviewer']

if __name__ == "__main__":
    asyncio.run(main())
```

## 💻 Code Example — Advanced
Advanced: an async `selector_func` reading the reviewer's text to loop back until approval; the verified order was user, classifier, rater, reviewer, classifier, rater, reviewer, then stop on APPROVE.

```python
# Custom speaker logic reading message CONTENT (retry loop until reviewer approves), async selector_func, FastAPI
import asyncio                                                    # async
from typing import Sequence                                       # typing
from fastapi import FastAPI                                       # web
from fastapi.testclient import TestClient                         # offline test
from autogen_agentchat.agents import AssistantAgent               # agent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination  # stop rules
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage  # message types
from autogen_agentchat.teams import SelectorGroupChat            # team
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

async def selector_func(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:  # async allowed
    last = messages[-1]
    if last.source == "user":
        return "classifier"                                       # start
    if last.source == "classifier":
        return "rater"
    if last.source == "rater":
        return "reviewer"
    if last.source == "reviewer":                                 # decide by CONTENT
        text = last.to_text() if isinstance(last, BaseChatMessage) else ""
        return None if "APPROVE" in text else "classifier"        # rejected -> loop back; approved -> termination fires anyway
    return None                                                   # unknown -> let LLM selector decide

def build() -> SelectorGroupChat:
    agents = [
        AssistantAgent("classifier", ReplayChatCompletionClient(["HS 6109.1", "HS 6109.10"])),
        AssistantAgent("rater", ReplayChatCompletionClient(["20%", "20%"])),
        AssistantAgent("reviewer", ReplayChatCompletionClient(["REJECT: code incomplete", "APPROVE"])),
    ]
    return SelectorGroupChat(agents, model_client=ReplayChatCompletionClient([]), selector_func=selector_func,
                             termination_condition=TextMentionTermination("APPROVE") | MaxMessageTermination(12))  # cap prevents infinite loops

app = FastAPI()

@app.post("/workflow")
async def workflow(body: dict) -> dict:
    res = await build().run(task=body["task"])
    return {"order": [m.source for m in res.messages], "stop": res.stop_reason}

if __name__ == "__main__":
    print(TestClient(app).post("/workflow", json={"task": "t-shirt duty"}).json())
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Custom routing | Conditional edge function | Custom process / hierarchical | Handoff logic in code | selector_func (SelectorGroupChat) or Swarm |
| Deterministic loops | Cycles in graph + limit | Task retries | Runner loop in your code | Function returning previous agent + hard cap |
| Testability | Test edge function | Hard | Test Python | Test selector_func standalone |
| LLM involvement | Optional | Optional | LLM picks handoffs | Optional (None => LLM fallback) |
| Visualise | Graph diagram | No | No | No built-in; GraphFlow offers an explicit graph |

---

## ⚠️ Common Mistakes
❌ Mistake: Returning an agent name that does not exist: runtime error or fallback.
✅ Correct: Return names from a constant set; unit-test every branch.

❌ Mistake: A loop with no hard cap: reject forever means cost forever.
✅ Correct: Always `| MaxMessageTermination(n)` (or `TokenUsageTermination`).

❌ Mistake: Checking `messages[-1].content` without handling non-text events.
✅ Correct: Use `isinstance(msg, BaseChatMessage)` and `to_text()`.

❌ Mistake: Not providing a `model_client` because 'we never call it': it is still a required argument.
✅ Correct: Pass any client (e.g. the cheap one); it is used only when the function returns None.

---

## 🧠 Tricky Interview Question
How do you make the retry loop converge instead of cycling between classifier and reviewer forever?

Answer: Give the loop memory and a budget. The selector function can count how many times the classifier has spoken (scan `messages`) and, after 2 rejections, route to a human or to an escalation agent instead. Combine with `MaxMessageTermination`, `TokenUsageTermination` and `TimeoutTermination`. Feed the reviewer's rejection reason to the classifier (the shared thread already does) and change something each retry (e.g. allow the classifier to use a retrieval tool on the second attempt), otherwise the same input produces the same output. Log retry counts as a quality metric.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What can a `selector_func` return?
A1: A participant name (forces that speaker) or None (use the LLM selector). It may be sync or async.

Q2: [Medium] Is the selector model called when `selector_func` always returns a name?
A2: No. Offline we passed an empty `ReplayChatCompletionClient([])` and the run succeeded, which shows no call happened.

Q3: [Hard] When use `Swarm` instead?
A3: When agents themselves should decide to hand off (`handoffs=['rate_agent']` creates a `transfer_to_rate_agent` tool), e.g. support triage; use selector_func when the workflow is owned by your code.

Q4: [Hard] How do you test a selector function?
A4: Build fake messages (`TextMessage(content=..., source='reviewer')`), call the function, assert the returned name; no LLM, no runtime.

Q5: [System Design] Design a four-eyes customs approval flow in AutoGen.
A5: selector_func state machine: prepare -> review_1 -> review_2 (different agent/model) -> final; any rejection returns to prepare with the reason; after 2 rejections hand off to a human via `UserProxyAgent`; all decisions logged with message hashes; hard caps on turns, tokens and time.

---

## 💰 Cost Impact
A deterministic `selector_func` removes selector LLM calls completely: saving roughly one small call per turn. Retry loops add full agent turns, so cost scales with retries: `cost ~ (1 + retries) * (classifier + rater + reviewer turn costs)`. Put a limit on retries (2-3), shrink context with a bounded `model_context`, and send only the rejection reason forward rather than the whole draft when possible. Measure the retry rate: if 30 percent of runs retry, fix the classifier prompt before scaling. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Regulated or auditable workflows with required order.
- Retry/approval loops.
- You want routing logic covered by unit tests.

❌ Avoid when:
- Open-ended collaboration where the next expert is unpredictable.
- Highly dynamic handoffs better expressed with Swarm.

---

## 📊 Visual Diagram
```
 user -----> classifier -----> rater -----> reviewer
                ^                              |
                |        "REJECT: ..."         |  "APPROVE"
                +------------------------------+----------> stop (TextMentionTermination)

 selector_func(messages):
    last.source == "user"       -> "classifier"
    last.source == "classifier" -> "rater"
    last.source == "rater"      -> "reviewer"
    last.source == "reviewer"   -> None if APPROVE else "classifier"
 hard cap: MaxMessageTermination(12)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| selector_func | Code that picks the next speaker | अगला speaker चुनने वाला code |
| state machine | States + transitions | states + transitions |
| Swarm | Handoff-driven team | handoff-आधारित team |
| handoff | Passing control to another agent | दूसरे agent को control देना |
| retry loop | Repeat until accepted | स्वीकार होने तक दोहराना |
| hard cap | Absolute turn limit | अधिकतम turns की सीमा |
| escalation | Send to human/senior agent | human/senior agent को भेजना |
| BaseChatMessage | Base type of chat messages | chat messages का base type |

---

## ⚡ 3-Line Summary
English: selector_func turns speaker selection into plain Python: deterministic, testable and free of selector tokens.
Return None only to fall back to the LLM; always keep a hard cap against infinite loops.
Use Swarm when agents should decide handoffs themselves.
Hindi: selector_func speaker selection को सादे Python में बदलता है: deterministic, testable और selector tokens के बिना।
LLM fallback के लिए ही None लौटाएँ; अनंत loops के खिलाफ हमेशा hard cap रखें।
जब agents खुद handoff तय करें तो Swarm इस्तेमाल करें।

---

## ➡️ Next Topic
139. AutoGen Tools -- how functions become tools the LLM can call.

---
