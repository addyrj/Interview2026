---

# 151. Swarm Team
# हिंदी में: Swarm Team (handoff से काम सौंपने वाली team)
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
`Swarm` is a team where the agent that is currently speaking decides who goes next by calling a handoff. You declare `handoffs=[...]` on an `AssistantAgent`; AutoGen turns each into a tool named `transfer_to_<target>`. When called, the agent emits a `HandoffMessage` and the target agent takes over. The first participant speaks first. A handoff to `"user"` can pause the run for a human (`HandoffTermination`).

## 🔵 सरल परिभाषा (Hindi)
`Swarm` ऐसी team है जिसमें अभी बोल रहा agent handoff call करके तय करता है कि अगला कौन बोलेगा। `AssistantAgent` पर `handoffs=[...]` घोषित करते हैं; AutoGen हर एक को `transfer_to_<target>` नाम का tool बना देता है। call होने पर agent `HandoffMessage` निकालता है और target agent कमान सँभालता है। पहला participant सबसे पहले बोलता है। `"user"` को handoff करने पर run इंसान के लिए रुक सकता है (`HandoffTermination`)।

---

## 🔴 Problem it Solves
In a support or customs workflow the current specialist knows best who should handle the case next. A central selector adds a routing call and can guess wrong. Handoffs let the agent that has the context transfer control explicitly, and also hand the conversation to a human.

## 🔴 यह क्यों बना? (Hindi)
Support या customs workflow में मौजूदा specialist सबसे अच्छा जानता है कि केस आगे किसे देना है। केंद्रीय selector एक routing call जोड़ता है और गलत भी हो सकता है। Handoff से जिस agent के पास context है वही साफ़ तौर पर नियंत्रण सौंपता है, और बातचीत इंसान को भी दे सकता है।

---

## 🟢 How it Works

```
Step 1 -> Declare handoffs=['customs'] on the front agent
Step 2 -> AutoGen adds a tool transfer_to_customs to that agent
Step 3 -> Model calls the tool when the case needs customs
Step 4 -> Agent emits HandoffMessage(source, target, content)
Step 5 -> Target agent becomes the next speaker and sees the shared history
Step 6 -> Handoff to 'user' + HandoffTermination(target='user') pauses for a human
Step 7 -> Resume with team.run(task=HandoffMessage(source='user', target='broker', content=reply))
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> front agent पर handoffs=['customs'] घोषित करो
Step 2 -> AutoGen उस agent में transfer_to_customs tool जोड़ता है
Step 3 -> केस को customs चाहिए तो model वह tool call करता है
Step 4 -> Agent HandoffMessage(source, target, content) निकालता है
Step 5 -> Target agent अगला वक्ता बनता है और साझा history देखता है
Step 6 -> 'user' को handoff + HandoffTermination(target='user') इंसान के लिए रोकता है
Step 7 -> team.run(task=HandoffMessage(source='user', target='broker', content=reply)) से जारी रखो
```

---

## 🟡 Real World Example
**Tariff Agent desk.** `front` receives 'Clear my shipment', decides it is a customs case and calls `transfer_to_customs`; `customs` answers 'Cleared. TERMINATE'. The observed trace: `[('TextMessage','user'), ('ToolCallRequestEvent','front'), ('ToolCallExecutionEvent','front'), ('HandoffMessage','front'), ('TextMessage','customs')]`. In the advanced version a `broker` agent hands to the human for an invoice number, the API returns, and a second request resumes.

## 🟡 Real Example Hindi mein
**Tariff Agent desk.** `front` को 'Clear my shipment' मिलता है, वह इसे customs केस समझकर `transfer_to_customs` call करता है; `customs` जवाब देता है 'Cleared. TERMINATE'। देखा गया trace: `[('TextMessage','user'), ('ToolCallRequestEvent','front'), ('ToolCallExecutionEvent','front'), ('HandoffMessage','front'), ('TextMessage','customs')]`। Advanced में `broker` agent invoice number के लिए इंसान को handoff करता है, API लौट जाती है और दूसरी request उसे आगे बढ़ाती है।

---

## 💻 Code Example — Basic
Basic: two agents; the scripted model for `front` 'decides' to call `transfer_to_customs`. Note the model client must declare `function_calling` in `model_info` or tool/handoff calls are rejected.

```python
# Basic: Swarm: agents hand off to each other via HandoffMessage (scripted model)
import asyncio  # loop
from autogen_core import FunctionCall  # tool call type
from autogen_core.models import CreateResult, RequestUsage  # fake reply types
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake model
from autogen_agentchat.agents import AssistantAgent  # agent
from autogen_agentchat.teams import Swarm  # handoff team
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination  # stops

MI = {"vision": False, "function_calling": True, "json_output": False, "family": "unknown", "structured_output": False}  # fake caps

async def main() -> None:  # entry
    handoff = CreateResult(finish_reason="function_calls", content=[FunctionCall(id="h1", name="transfer_to_customs", arguments="{}")],
                           usage=RequestUsage(prompt_tokens=0, completion_tokens=0), cached=False)  # model 'decides' to hand off
    front = AssistantAgent("front", ReplayChatCompletionClient([handoff], model_info=MI), handoffs=["customs"])  # handoffs create transfer_to_<name> tools
    customs = AssistantAgent("customs", ReplayChatCompletionClient(["Cleared. TERMINATE"]))  # receives control
    team = Swarm([front, customs], termination_condition=TextMentionTermination("TERMINATE") | MaxMessageTermination(8))  # first participant speaks first
    res = await team.run(task="Clear my shipment")  # run
    print([(type(m).__name__, m.source) for m in res.messages])  # see HandoffMessage

asyncio.run(main())  # go
```

## 💻 Code Example — Advanced
Advanced: human-in-the-loop over two HTTP calls. `HandoffTermination(target='user')` stops the run, the session's team is kept in a dict, and `/reply` resumes with `HandoffMessage`. In production persist `save_state()` instead of keeping teams in memory.

```python
# Advanced: human-in-the-loop handoff: Swarm stops on HandoffTermination(target="user"), FastAPI resumes with the reply
from fastapi import FastAPI  # web
from fastapi.testclient import TestClient  # test
from pydantic import BaseModel  # body
from autogen_core import FunctionCall  # call
from autogen_core.models import CreateResult, RequestUsage  # fake
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake model
from autogen_agentchat.agents import AssistantAgent  # agent
from autogen_agentchat.teams import Swarm  # team
from autogen_agentchat.conditions import HandoffTermination, MaxMessageTermination, TextMentionTermination  # stops
from autogen_agentchat.messages import HandoffMessage  # resume message

MI = {"vision": False, "function_calling": True, "json_output": False, "family": "unknown", "structured_output": False}  # caps
app = FastAPI()  # app
TEAMS: dict[str, Swarm] = {}  # session_id -> team (in prod use a store + save_state)

def call(name: str) -> CreateResult:  # build scripted handoff
    return CreateResult(finish_reason="function_calls", content=[FunctionCall(id="x", name=name, arguments="{}")],
                        usage=RequestUsage(prompt_tokens=0, completion_tokens=0), cached=False)  # fake tool call

class Start(BaseModel):  # body
    task: str  # task

class Reply(BaseModel):  # body
    text: str  # human answer

@app.post("/start/{sid}")  # begin
async def start(sid: str, s: Start) -> dict[str, object]:  # handler
    agent = AssistantAgent("broker", ReplayChatCompletionClient([call("transfer_to_user"), "Thanks, filing entry. DONE"], model_info=MI), handoffs=["user"])  # asks the human
    TEAMS[sid] = Swarm([agent], termination_condition=HandoffTermination(target="user") | TextMentionTermination("DONE") | MaxMessageTermination(6))  # stop on handoff to user, or when the agent says DONE
    res = await TEAMS[sid].run(task=s.task)  # run until handoff
    return {"stop": res.stop_reason, "last": type(res.messages[-1]).__name__}  # report

@app.post("/reply/{sid}")  # resume
async def reply(sid: str, r: Reply) -> dict[str, object]:  # handler
    res = await TEAMS[sid].run(task=HandoffMessage(source="user", target="broker", content=r.text))  # continue the same team
    return {"final": str(res.messages[-1].content)}  # answer

with TestClient(app) as c:  # context manager keeps ONE event loop (a team is bound to the loop it first ran on)
    print(c.post("/start/s1", json={"task": "need invoice"}).json())  # step 1
    print(c.post("/reply/s1", json={"text": "invoice #42"}).json())  # step 2
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline (scripted `ReplayChatCompletionClient` or no model at all, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates, not real billing. Because a team is bound to the event loop it first ran on, the FastAPI demo uses `with TestClient(app) as c:` so both requests share one loop.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---|---|---|---|---|
| Handoff concept | Command(goto=...) / conditional edge | Delegation between agents | Handoffs (first-class) | Swarm + handoffs=[...] (transfer_to_<name> tools) |
| Who decides | Node or router | Manager or agent | The current agent via handoff tool | The current agent via handoff tool |
| Human handoff | interrupt | human_input | Return to caller | HandoffTermination(target='user') + HandoffMessage resume |
| Shared history | Shared state | Task context | Passed to next agent | Shared thread to all |
| Extra routing LLM call | Router node (optional) | Manager | No | No (the speaking agent's own call) |
| Best for | Complex graphs | Role crews | Customer support triage | Support desks, escalation chains |

---

## ⚠️ Common Mistakes
❌ Mistake: Forgetting `function_calling=True` in the model's capabilities.
✅ Correct: Handoffs are tools; the model client must support function calling (real OpenAI clients do; scripted fakes need `model_info`).

❌ Mistake: Handoff target name that does not match a participant.
✅ Correct: Targets are participant names (or 'user'); check spelling.

❌ Mistake: Keeping Team objects in a global dict in a multi-worker deployment.
✅ Correct: Persist `await team.save_state()` per session and rebuild on each request.

❌ Mistake: No termination on handoff to user.
✅ Correct: Add `HandoffTermination(target='user')` or the run keeps going or ends oddly.

---

## 🧠 Tricky Interview Question
Two agents keep handing the case back to each other. How do you debug and prevent it?

Answer: Log every HandoffMessage with source/target and reason. Loops come from vague instructions ('transfer if unsure'). Give each agent explicit ownership rules (who may transfer to whom and under what condition), add a hop counter or `MaxMessageTermination`, make one agent a terminal owner that must answer or escalate to the human, and test with scripted models for each branch before using a real LLM.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How do you define a handoff?
A1: `AssistantAgent(..., handoffs=['target'])`; the target is a participant name or 'user'.

Q2: [Medium] What tool does AutoGen create for a handoff?
A2: One named `transfer_to_<target>`; the model calls it and the agent emits a HandoffMessage.

Q3: [Hard] How do you pause for a human and resume?
A3: Handoff to 'user', stop with `HandoffTermination(target='user')`, then call `team.run(task=HandoffMessage(source='user', target=<agent>, content=<reply>))` on the same (or state-restored) team.

Q4: [Hard] Why is Swarm cheaper than SelectorGroupChat?
A4: The speaking agent chooses the next one inside its own call; no separate selector call per turn.

Q5: [System Design] Design a customs support desk.
A5: front triage -> classification -> duties -> payments agents with explicit handoff rules; human escalation on low confidence; session state saved per case; audit of every handoff; caps on hops and tokens.

---

## 💰 Cost Impact
No separate routing call, so cost is just each speaking agent's call. A handoff turn adds the tool schema tokens for each declared handoff plus a short tool call/result. Formula: `cost ~ turns * (history_tokens + handoff_schema_tokens) * in_price + outputs`. Tips: few handoffs per agent, concise descriptions, summarise long histories before escalation. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Escalation chains and triage (support, customs).
- Specialists know when to transfer.
- Human-in-the-loop pauses are needed.

❌ Avoid when:
- A central planner should decide (Magentic-One / Selector).
- You need strict graph branching.
- Model has no function calling.

---

## 📊 Visual Diagram
```
 user --> [front] --transfer_to_customs--> [customs] --transfer_to_user--> (human)
                |                                       ^                  |
                | HandoffMessage(source=front,target=customs)              |
                +---------------------------------------+                  |
                                                                           v
                  HandoffTermination(target='user') stops the run   reply comes back as
                  HandoffMessage(source='user', target=<agent>, content=...) 
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|---|---|---|
| Swarm | Team driven by handoffs | handoffs से चलने वाली team |
| handoff | Transfer of control to another agent | दूसरे agent को नियंत्रण सौंपना |
| HandoffMessage | Message that carries the transfer | transfer ले जाने वाला message |
| transfer_to_<name> | Auto-created handoff tool | अपने आप बना handoff tool |
| HandoffTermination | Stop when a handoff targets someone | किसी को handoff पर रुकना |
| human in the loop | Pause for a person | इंसान के लिए रुकना |
| escalation | Moving to a higher level | ऊपर के स्तर पर भेजना |

---

## ⚡ 3-Line Summary
English: Swarm lets each agent hand work to another with transfer_to_<name> tools and HandoffMessage.
Handoff to 'user' plus HandoffTermination pauses for a human; resume with a HandoffMessage.
No separate router call, but you must guard against handoff loops.
Hindi: Swarm में हर agent transfer_to_<name> tools और HandoffMessage से काम दूसरे को सौंपता है।
'user' को handoff और HandoffTermination इंसान के लिए रोकते हैं; HandoffMessage से जारी रखें।
अलग router call नहीं लगता, पर handoff loops से बचाव ज़रूरी है।

---

## ➡️ Next Topic
152. AutoGen Core API -- the low-level actor-style layer under AgentChat.

---
