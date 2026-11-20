---

# 132. UserProxyAgent
# हिंदी में: UserProxyAgent — human को loop में लाना
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
`UserProxyAgent` is an AgentChat agent that represents a human. When it is its turn, it calls an `input_func` to get the human's reply (default: Python `input()`), and returns it as a message. It does not call an LLM and does not execute code (that is `CodeExecutorAgent` in v0.4).

## 🔵 सरल परिभाषा (Hindi)
`UserProxyAgent` AgentChat का वह agent है जो इंसान को represent करता है। जब इसकी बारी आती है, यह `input_func` से human का जवाब लेता है (default: Python `input()`) और उसे message बनाकर लौटाता है। यह LLM call नहीं करता और code नहीं चलाता (v0.4 में वह `CodeExecutorAgent` का काम है)।

---

## 🔴 Problem it Solves
Autonomous agents make mistakes: wrong HS code, wrong refund, risky action. Many workflows need a human approval gate, a clarification, or a correction mid-run. In v0.2 the `UserProxyAgent` also executed code, which blurred responsibilities and was a security risk. v0.4 isolates 'human input' into one small agent.

## 🔴 यह क्यों बना? (Hindi)
Autonomous agents गलतियाँ करते हैं: गलत HS code, गलत refund, जोखिम भरी action। कई workflows में human approval, clarification या बीच में सुधार चाहिए। v0.2 में `UserProxyAgent` code भी चलाता था, जिससे ज़िम्मेदारियाँ मिल गई थीं और security जोखिम था। v0.4 ने 'human input' को एक छोटे agent में अलग कर दिया।

---

## 🟢 How it Works

```
Step 1 -> Team picks UserProxyAgent as next speaker
Step 2 -> It emits a UserInputRequestedEvent (empty-content event in the transcript)
Step 3 -> It awaits input_func(prompt, cancellation_token) -- sync or async function
Step 4 -> Human (CLI / web UI / Slack) answers
Step 5 -> Answer returned as a TextMessage from source 'human'
Step 6 -> Termination condition checks it (e.g. TextMentionTermination('APPROVE'))
Step 7 -> If not approved, the other agents revise and the loop continues
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Team अगला speaker UserProxyAgent चुनती है
Step 2 -> यह UserInputRequestedEvent भेजता है (transcript में खाली-content वाला event)
Step 3 -> यह input_func(prompt, cancellation_token) का इंतज़ार करता है -- sync या async function
Step 4 -> इंसान (CLI / web UI / Slack) जवाब देता है
Step 5 -> जवाब source 'human' के TextMessage के रूप में लौटता है
Step 6 -> Termination condition उसे जाँचती है (जैसे TextMentionTermination('APPROVE'))
Step 7 -> approve न हुआ तो बाकी agents सुधारते हैं और loop चलता रहता है
```

---

## 🟡 Real World Example
**Customs broker sign-off.** A drafter agent proposes the classification 'HS 6109.10, duty 20%'. Before filing with customs, a licensed broker must approve. The `UserProxyAgent` pauses the run; the web UI shows the draft; the broker types APPROVE or a correction. A wrong filing can mean fines, so the pause is worth the latency.

## 🟡 Real Example Hindi mein
**Customs broker sign-off.** Drafter agent classification सुझाता है 'HS 6109.10, duty 20%'। Customs में file करने से पहले licensed broker को approve करना है। `UserProxyAgent` run को रोक देता है; web UI draft दिखाती है; broker APPROVE या सुधार लिखता है। गलत filing पर जुर्माना हो सकता है, इसलिए latency की कीमत चुकाना ठीक है।

---

## 💻 Code Example — Basic
Basic: a scripted `input_func` replaces the keyboard so the example runs offline. Note the empty `('human', '')` entry: that is the input-requested event.

```python
# UserProxyAgent: human-in-the-loop approval inside a team (input_func scripted for offline run)
import asyncio                                                    # async
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent  # agents
from autogen_agentchat.conditions import TextMentionTermination   # stop rule
from autogen_agentchat.teams import RoundRobinGroupChat           # team
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

def fake_human(prompt: str) -> str:                               # replaces input(); sync or async both allowed
    print(f"[human sees] {prompt!r}")                             # what the human is asked
    return "APPROVE"                                              # what the human types

async def main() -> None:
    drafter = AssistantAgent("drafter", ReplayChatCompletionClient(["Classification: HS 6109.10, duty 20%."]))
    human = UserProxyAgent("human", input_func=fake_human)        # default input_func = built-in input() (blocks the loop!)
    team = RoundRobinGroupChat([drafter, human],
                               termination_condition=TextMentionTermination("APPROVE"))  # stop when human approves
    res = await team.run(task="Classify a cotton t-shirt")
    print([(m.source, m.content) for m in res.messages])          # full transcript
    print("stop:", res.stop_reason)

if __name__ == "__main__":
    asyncio.run(main())
```

## 💻 Code Example — Advanced
Advanced: over HTTP the agent must PAUSE until a second request supplies the answer. An async `input_func` awaits an `asyncio.Future` that `POST /answer/{run_id}` resolves; `token.link_future` makes cancellation work.

```python
# UserProxyAgent over HTTP: the agent PAUSES until a second request delivers the human's answer
import asyncio                                                    # async primitives
from fastapi import FastAPI, HTTPException                        # web
from fastapi.testclient import TestClient                         # offline test (runs app in a thread/loop)
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent  # agents
from autogen_agentchat.conditions import TextMentionTermination   # stop rule
from autogen_agentchat.teams import RoundRobinGroupChat           # team
from autogen_core import CancellationToken                        # passed to async input_func
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

app = FastAPI()
PENDING: dict[str, asyncio.Future[str]] = {}                      # run_id -> future waiting for the human
PROMPTS: dict[str, str] = {}                                      # run_id -> question shown to human

def make_input_func(run_id: str):                                 # closure binds the func to one run
    async def input_func(prompt: str, token: CancellationToken | None = None) -> str:
        fut: asyncio.Future[str] = asyncio.get_running_loop().create_future()  # human answer arrives here
        PENDING[run_id] = fut                                     # register
        PROMPTS[run_id] = prompt                                  # expose question to GET /pending
        try:
            if token is not None:
                token.link_future(fut)                            # cancelling the run cancels the wait
            return await asyncio.wait_for(fut, timeout=300)       # human SLA: 5 minutes
        finally:
            PENDING.pop(run_id, None)                             # cleanup
    return input_func

@app.post("/start/{run_id}")
async def start(run_id: str) -> dict:
    drafter = AssistantAgent("drafter", ReplayChatCompletionClient(["Draft: duty 20%"]))
    human = UserProxyAgent("human", input_func=make_input_func(run_id))
    team = RoundRobinGroupChat([drafter, human], termination_condition=TextMentionTermination("APPROVE"))
    task = asyncio.create_task(team.run(task="classify t-shirt"))  # run in background so the request returns
    TASKS[run_id] = task
    return {"status": "started"}

TASKS: dict[str, asyncio.Task] = {}                               # background runs

@app.post("/answer/{run_id}")
async def answer(run_id: str, body: dict) -> dict:
    fut = PENDING.get(run_id)
    if fut is None:                                               # nothing waiting
        raise HTTPException(404, "no pending question")
    fut.set_result(body["text"])                                  # unblocks the agent
    res = await TASKS[run_id]                                     # wait for team to finish
    return {"stop": res.stop_reason, "transcript": [(m.source, str(m.content)) for m in res.messages]}

if __name__ == "__main__":
    async def demo() -> None:                                     # drive the endpoints with httpx ASGI transport
        import httpx
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            print((await c.post("/start/r1")).json())
            for _ in range(50):                                   # wait until agent asks the human
                if "r1" in PENDING: break
                await asyncio.sleep(0.02)
            print("question:", PROMPTS["r1"])
            print((await c.post("/answer/r1", json={"text": "APPROVE"})).json())
    asyncio.run(demo())
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Human in the loop | interrupt() + resume with Command | human_input=True on task | Approvals / guardrails you code | UserProxyAgent + input_func |
| Pause mechanism | Checkpoint, process can exit | Blocks on console input | Your own tool awaits approval | Awaits input_func (process stays alive) |
| Web friendly | Yes (durable) | Needs custom work | Needs custom work | Needs Future/queue pattern (shown) |
| Code execution by proxy | No | No | No | No (use CodeExecutorAgent) |
| Alternative | - | - | - | HandoffTermination(target='user') |

---

## ⚠️ Common Mistakes
❌ Mistake: Using the default `input()` in a web server: it blocks the event loop and never receives browser input.
✅ Correct: Pass an async `input_func` that awaits a Future/queue fed by an HTTP endpoint.

❌ Mistake: No timeout on the human wait: the run hangs forever and holds memory.
✅ Correct: `asyncio.wait_for(fut, timeout=...)` and a policy on expiry (cancel, escalate, default deny).

❌ Mistake: Assuming the process can restart while waiting. The Future lives in memory.
✅ Correct: For long human delays use `HandoffTermination`: stop the run, save state, resume in a new request after the human replies.

❌ Mistake: Treating the human message as trusted input in later prompts.
✅ Correct: Validate and length-limit it; humans paste secrets and prompt injections too.

---

## 🧠 Tricky Interview Question
Approvals can take 2 days. How do you design this with UserProxyAgent?

Answer: Do not keep a coroutine waiting for 2 days. Use the stop-and-resume pattern: the agent that needs approval hands off to the user (`handoffs=['user']` plus `HandoffTermination(target='user')` in a Swarm) or the team ends with a termination condition; you `save_state()` to a database together with the pending question, notify the human (email/Slack), and when they answer you rebuild the team, `load_state()` and `run(task=human_answer)`. `UserProxyAgent` with a Future is right only for waits of seconds to a few minutes while the connection is open.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does `UserProxyAgent` do in v0.4?
A1: It represents a human: on its turn it calls `input_func` and returns the text as a message. No LLM, no code execution.

Q2: [Medium] What is the default `input_func`?
A2: Python's blocking `input()`. Fine in a terminal, wrong in a web server.

Q3: [Hard] How do you integrate it with FastAPI?
A3: Create an async `input_func` that registers a Future per run id; an endpoint resolves it; the team runs as a background task; protect with timeouts and cancellation.

Q4: [Hard] What is the difference between `UserProxyAgent` and `HandoffTermination`?
A4: UserProxyAgent keeps the run alive and waits (short waits). HandoffTermination ends the run when an agent hands off to the user; you resume later with `run(task=...)` (long waits, serverless friendly).

Q5: [System Design] Design an approval workflow for refunds above a threshold.
A5: Agent computes refund -> tool returns amount; rule: amount <= limit auto-approve; else hand off to user. Persist state + pending approval id in DB, notify approver, resume on webhook with the decision, log decision, approver id and the model's reasoning for audit, and enforce a deadline with default deny.

---

## 💰 Cost Impact
`UserProxyAgent` itself uses no tokens. Waiting time costs infrastructure (an open connection, memory) but no LLM spend, provided no agent is polling the model. The expensive pattern is the revise loop: each human rejection triggers another LLM round with the longer history. Cap rejections (for example `MaxMessageTermination`) and include the human's correction concisely. Formula: `extra_cost = rejections * (history_tokens * in_price + revision_tokens * out_price)`. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- High-stakes actions needing approval.
- Clarifying questions mid-run.
- Demos and CLIs with a human in the conversation.

❌ Avoid when:
- Fully automated batch jobs.
- Multi-day waits with an in-memory Future: use stop-and-resume.
- Any place where the human reply is not validated.

---

## 📊 Visual Diagram
```
 drafter(LLM) --"HS 6109.10, 20%"--> UserProxyAgent
                                          |  UserInputRequestedEvent
                                          v
                                   await input_func(prompt)
                                          |        ^
                       web UI / Slack  <--+        | POST /answer/{run_id}
                                          v        |
                                   "APPROVE" ------+
                                          |
              TextMentionTermination('APPROVE') --> run ends (else drafter revises)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| input_func | Callable that gets the human's reply | human का जवाब लाने वाला callable |
| UserInputRequestedEvent | Event telling UI a human is needed | UI को बताने वाला event कि human चाहिए |
| HandoffTermination | Stops the run on handoff to a target | handoff पर run रोकना |
| approval gate | Mandatory human check | अनिवार्य human जाँच |
| Future | Awaitable result set later | बाद में भरा जाने वाला awaitable result |
| CancellationToken | Lets you abort a waiting call | इंतज़ार करते call को रद्द करने वाला token |
| stop-and-resume | Save state, end, continue later | state सहेजो, रुको, बाद में चलाओ |
| human-in-the-loop | Human inside the agent loop | agent loop में इंसान |

---

## ⚡ 3-Line Summary
English: UserProxyAgent asks a human via `input_func` and returns the answer as a message.
In web apps use an async input_func with a timeout; for long waits use HandoffTermination and resume from saved state.
It costs no tokens itself; rejection loops do.
Hindi: UserProxyAgent `input_func` से human को पूछता है और जवाब message के रूप में लौटाता है।
Web apps में timeout के साथ async input_func इस्तेमाल करें; लंबे इंतज़ार के लिए HandoffTermination और saved state से resume।
यह खुद tokens नहीं लेता; rejection loops लेते हैं।

---

## ➡️ Next Topic
133. CodeExecutorAgent -- executing code the model writes, safely.

---
