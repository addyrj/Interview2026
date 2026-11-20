---

# 149. SelectorGroupChat
# हिंदी में: SelectorGroupChat (अगला वक्ता चुनने वाली team)
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
`SelectorGroupChat` picks the next speaker after every message, using a model (`model_client`), a custom `selector_func`, or both. `candidate_func` narrows which agents the model may choose from. Other 0.7.5 parameters: `selector_prompt`, `allow_repeated_speaker`, `max_selector_attempts`, `model_client_streaming`, `model_context`. Agents need a good `description` because the selector reads it.

## 🔵 सरल परिभाषा (Hindi)
`SelectorGroupChat` हर message के बाद अगला वक्ता चुनती है: model (`model_client`), अपने `selector_func`, या दोनों से। `candidate_func` तय करता है कि model किन agents में से चुन सकता है। 0.7.5 के और parameters: `selector_prompt`, `allow_repeated_speaker`, `max_selector_attempts`, `model_client_streaming`, `model_context`। Agents का `description` अच्छा होना चाहिए क्योंकि selector उसे पढ़ता है।

---

## 🔴 Problem it Solves
Specialists should speak only when relevant: the classifier first, the rate agent next, the reviewer last. Round robin would make every agent speak every cycle. A selector routes dynamically, at the cost of one extra model call per turn.

## 🔴 यह क्यों बना? (Hindi)
Specialists सिर्फ़ तब बोलें जब ज़रूरी हो: पहले classifier, फिर rate agent, आखिर में reviewer। Round robin हर चक्र में सबको बुलाता। Selector dynamic routing करता है, पर हर turn एक अतिरिक्त model call की कीमत पर।

---

## 🟢 How it Works

```
Step 1 -> Each agent has a clear name and description
Step 2 -> After a message, selector_func(messages) may return a name directly (or None)
Step 3 -> If None: candidate_func(messages) can narrow the candidate list
Step 4 -> Selector prompt (roles + history) goes to model_client
Step 5 -> Model returns an agent name; invalid names are retried up to max_selector_attempts
Step 6 -> allow_repeated_speaker=False prevents the same agent twice in a row
Step 7 -> Chosen agent speaks; termination is checked
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> हर agent का साफ़ नाम और description होता है
Step 2 -> message के बाद selector_func(messages) सीधे नाम लौटा सकता है (या None)
Step 3 -> None हो तो: candidate_func(messages) candidate सूची छोटी कर सकता है
Step 4 -> Selector prompt (roles + history) model_client को जाता है
Step 5 -> Model agent का नाम लौटाता है; गलत नाम max_selector_attempts तक retry होते हैं
Step 6 -> allow_repeated_speaker=False एक ही agent को लगातार दो बार बोलने से रोकता है
Step 7 -> चुना गया agent बोलता है; termination जाँची जाती है
```

---

## 🟡 Real World Example
**Tariff Agent routing.** Task 'duty on shoes'. `candidate_func` allows only `classifier` first (the observed order was `['user', 'classifier', 'rate_agent', 'reviewer']`). The selector model (scripted here) then picks `rate_agent` and `reviewer`. In production the selector is a real LLM, so each turn adds one routing call.

## 🟡 Real Example Hindi mein
**Tariff Agent routing.** Task 'shoes पर duty'। `candidate_func` पहले सिर्फ़ `classifier` की अनुमति देता है (देखा गया क्रम `['user', 'classifier', 'rate_agent', 'reviewer']`)। फिर selector model (यहाँ scripted) `rate_agent` और `reviewer` चुनता है। Production में selector असली LLM होता है, इसलिए हर turn एक routing call जुड़ती है।

---

## 💻 Code Example — Basic
Basic: `selector_func` for deterministic routing with no model call for the first two hops; it returns `None` to fall back to the model. A `model_client` is still required by the constructor.

```python
# Basic: SelectorGroupChat with selector_func (deterministic routing, no LLM selection call)
import asyncio  # loop
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM
from autogen_agentchat.agents import AssistantAgent  # agent
from autogen_agentchat.teams import SelectorGroupChat  # LLM/func-selected team
from autogen_agentchat.conditions import MaxMessageTermination  # stop

def pick(messages) -> str | None:  # return an agent name, or None to let the LLM pick
    last = messages[-1]  # latest message
    if last.source == "user":  # fresh task
        return "classifier"  # first specialist
    if last.source == "classifier":  # classifier spoke
        return "rate_agent"  # then rates
    return None  # otherwise fall back to the model selector

async def main() -> None:  # entry
    c = AssistantAgent("classifier", ReplayChatCompletionClient(["HS 6403"]), description="Finds HS codes")  # specialist 1
    r = AssistantAgent("rate_agent", ReplayChatCompletionClient(["25%"]), description="Looks up duty rates")  # specialist 2
    team = SelectorGroupChat([c, r], model_client=ReplayChatCompletionClient(["classifier"]), selector_func=pick, termination_condition=MaxMessageTermination(3))  # selector needs a model client
    res = await team.run(task="duty on leather shoes?")  # run
    print([m.source for m in res.messages])  # routing order

asyncio.run(main())  # go
```

## 💻 Code Example — Advanced
Advanced: `candidate_func` narrows choices, `allow_repeated_speaker=False`, scripted selector replies, behind FastAPI. Selection costs an extra LLM call per turn in real use.

```python
# Advanced: LLM-driven selector (scripted here) with candidate_func + FastAPI. Selector = extra LLM call per turn.
from fastapi import FastAPI  # web
from fastapi.testclient import TestClient  # test
from pydantic import BaseModel  # body
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake
from autogen_agentchat.agents import AssistantAgent  # agent
from autogen_agentchat.teams import SelectorGroupChat  # team
from autogen_agentchat.conditions import MaxMessageTermination  # stop

app = FastAPI()  # app

def candidates(messages) -> list[str]:  # narrow who the LLM may choose (cheaper, safer)
    if messages[-1].source == "user":  # first turn
        return ["classifier"]  # only classifier allowed
    return ["rate_agent", "reviewer"]  # later: either

class Req(BaseModel):  # body
    task: str  # text

@app.post("/route")  # endpoint
async def route(req: Req) -> dict[str, object]:  # handler
    agents = [AssistantAgent("classifier", ReplayChatCompletionClient(["HS 6403"]), description="HS classification"),
              AssistantAgent("rate_agent", ReplayChatCompletionClient(["25%"]), description="Duty rates"),
              AssistantAgent("reviewer", ReplayChatCompletionClient(["ok"]), description="Final check")]  # specialists
    selector_llm = ReplayChatCompletionClient(["classifier", "rate_agent", "reviewer"])  # scripted selector replies (a real LLM in prod)
    team = SelectorGroupChat(agents, model_client=selector_llm, candidate_func=candidates, allow_repeated_speaker=False,
                             termination_condition=MaxMessageTermination(4))  # build team
    res = await team.run(task=req.task)  # run
    return {"order": [m.source for m in res.messages], "stop": res.stop_reason}  # response

print(TestClient(app).post("/route", json={"task": "duty on shoes"}).json())  # try
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing. In these runs the selector was a scripted `ReplayChatCompletionClient`; real selector quality (does a real LLM pick well?) was NOT tested.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---|---|---|---|---|
| Dynamic routing | Conditional edges / router node | Hierarchical process with manager | Triage agent + handoffs | SelectorGroupChat |
| Router type | Your function or LLM | Manager LLM | LLM chooses handoff tool | LLM and/or Python selector_func |
| Restrict choices | Edge map | allowed agents in task | handoffs list | candidate_func |
| Extra LLM cost | If LLM router | Manager calls | Handoff tool call | One selector call per turn (unless selector_func answers) |
| Control over prompt | Full | Limited | Instructions | selector_prompt template |
| Repeat speaker | Your logic | Your logic | Your logic | allow_repeated_speaker |

---

## ⚠️ Common Mistakes
❌ Mistake: Vague agent descriptions.
✅ Correct: The selector chooses by description; write what the agent does and when to use it.

❌ Mistake: Letting the selector choose among all agents every turn.
✅ Correct: Use `candidate_func` or `selector_func` for obvious transitions: cheaper and safer.

❌ Mistake: Forgetting that model_client is required.
✅ Correct: The constructor needs it even if `selector_func` handles most turns.

❌ Mistake: Infinite ping-pong between two agents.
✅ Correct: Set `allow_repeated_speaker=False`, add MaxMessageTermination and a clear finish rule.

---

## 🧠 Tricky Interview Question
The selector keeps choosing the reviewer before the classifier has spoken. Fix it without raising cost.

Answer: Do not rely on the LLM for ordering that is known. Use `selector_func` to return 'classifier' when the last message is from the user and 'rate_agent' after the classifier; return None only for genuinely ambiguous steps. Add `candidate_func` to remove invalid choices (reviewer cannot speak before the rate agent). Improve descriptions ('Use ONLY after an HS code exists'). This removes selector calls on the deterministic hops so cost falls and errors vanish.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does SelectorGroupChat do differently from RoundRobinGroupChat?
A1: It chooses the next speaker dynamically instead of a fixed cycle.

Q2: [Medium] Difference between selector_func and candidate_func?
A2: `selector_func` returns the exact next agent name (or None to let the model choose); `candidate_func` returns a list of allowed names for the model to choose from.

Q3: [Hard] What is the cost trade-off?
A3: Extra model call every turn (input = selector prompt + history). Mitigate with selector_func/candidate_func and a small cheap selector model.

Q4: [Hard] What happens if the model returns an invalid name?
A4: The team retries up to `max_selector_attempts`; keep descriptions clear to avoid it.

Q5: [System Design] Design a support desk with billing, tariff and legal agents.
A5: SelectorGroupChat with descriptions, candidate_func by intent classifier (cheap rule or small model), allow_repeated_speaker=False, termination on resolved/handoff to human, per-session state, monitor selector accuracy.

---

## 💰 Cost Impact
Per turn: selector call (roles + history) plus the speaker's call. For N turns you pay roughly 2x the calls of round robin unless `selector_func` covers most hops. Use a small model for selection. Formula: `cost ~ N * (selector_tokens + speaker_tokens) * price`. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Several specialists, only one relevant per turn.
- Routing depends on content.
- You want flexibility without a hard-coded graph.

❌ Avoid when:
- Order is fixed (use round robin).
- Selection must be 100% deterministic (use selector_func only or a graph).
- Very tight cost budgets.

---

## 📊 Visual Diagram
```
 messages so far
     |
     v
 selector_func? --name--> speaker
     | None
     v
 candidate_func narrows list
     |
     v
 selector LLM(model_client) --name--> speaker (not same twice)
     |
     v
 speaker replies -> broadcast -> termination check -> loop
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|---|---|---|
| selector_func | Python rule to pick next speaker | अगला वक्ता चुनने का Python नियम |
| candidate_func | Narrows allowed speakers | allowed वक्ताओं को सीमित करता है |
| selector_prompt | Template sent to the router LLM | router LLM को भेजा जाने वाला template |
| description | Text selector uses to choose | जिससे selector चुनता है |
| allow_repeated_speaker | Same agent twice in a row? | एक ही agent लगातार दो बार? |
| max_selector_attempts | Retries for invalid choice | गलत चुनाव पर retries |
| routing | Choosing the next agent | अगला agent चुनना |

---

## ⚡ 3-Line Summary
English: SelectorGroupChat picks the next speaker with an LLM and/or your function.
Use selector_func and candidate_func to cut cost and errors.
Write precise agent descriptions; each LLM selection costs a call.
Hindi: SelectorGroupChat अगला वक्ता LLM और/या आपके function से चुनती है।
खर्च और गलतियाँ घटाने के लिए selector_func और candidate_func इस्तेमाल करें।
Agent descriptions सटीक लिखें; हर LLM चुनाव एक call है।

---

## ➡️ Next Topic
150. MagenticOneGroupChat -- an orchestrator that plans, tracks progress and re-plans.

---
