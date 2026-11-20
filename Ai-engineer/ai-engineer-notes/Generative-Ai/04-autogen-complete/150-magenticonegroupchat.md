---

# 150. MagenticOneGroupChat
# हिंदी में: MagenticOneGroupChat (planner वाली orchestrated team)
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
`MagenticOneGroupChat` is a team where an orchestrator agent plans the task, keeps a ledger of progress, assigns work to participants and re-plans when progress stalls (`max_stalls`). Signature in 0.7.5: `MagenticOneGroupChat(participants, model_client, name, description, termination_condition, max_turns, runtime, max_stalls, final_answer_prompt, custom_message_types, emit_team_events)`. It is designed for open-ended tasks and uses many model calls.

## 🔵 सरल परिभाषा (Hindi)
`MagenticOneGroupChat` ऐसी team है जिसमें orchestrator agent task की योजना बनाता है, प्रगति का ledger रखता है, participants को काम बाँटता है और प्रगति रुकने पर (`max_stalls`) दोबारा योजना बनाता है। 0.7.5 में signature: `MagenticOneGroupChat(participants, model_client, name, description, termination_condition, max_turns, runtime, max_stalls, final_answer_prompt, custom_message_types, emit_team_events)`। यह open-ended tasks के लिए है और बहुत सारे model calls लेती है।

---

## 🔴 Problem it Solves
Open-ended tasks ('estimate duty for this shipment including shipping and fees') have no fixed order. A fixed loop or a simple selector cannot plan, notice that it is stuck, and try another approach. Magentic-One adds an explicit planner with progress tracking.

## 🔴 यह क्यों बना? (Hindi)
Open-ended tasks ('shipping और fees समेत इस shipment की duty का अनुमान') का कोई तय क्रम नहीं होता। तय loop या साधारण selector न योजना बना सकता है, न यह पहचान सकता है कि वह अटक गया, न दूसरा तरीका आज़मा सकता है। Magentic-One एक स्पष्ट planner और progress tracking जोड़ता है।

---

## 🟢 How it Works

```
Step 1 -> Orchestrator reads the task and writes facts + a plan
Step 2 -> Each turn it fills a progress ledger: is the task done? are we in a loop? who speaks next and with what instruction?
Step 3 -> Chosen participant works on the instruction and reports back
Step 4 -> If no progress for max_stalls rounds, orchestrator updates facts and re-plans
Step 5 -> When done it writes a final answer (final_answer_prompt)
Step 6 -> max_turns and your termination_condition cap the run
Step 7 -> All of this uses model_client calls: many per task
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Orchestrator task पढ़कर तथ्य + योजना लिखता है
Step 2 -> हर turn वह progress ledger भरता है: task पूरा हुआ? loop में हैं? अगला कौन बोलेगा और किस निर्देश से?
Step 3 -> चुना गया participant निर्देश पर काम करके रिपोर्ट देता है
Step 4 -> max_stalls rounds तक प्रगति न हो तो orchestrator तथ्य अपडेट करके दोबारा योजना बनाता है
Step 5 -> पूरा होने पर वह अंतिम जवाब लिखता है (final_answer_prompt)
Step 6 -> max_turns और आपकी termination_condition run को सीमित करती हैं
Step 7 -> यह सब model_client calls से होता है: एक task में कई
```

---

## 🟡 Real World Example
**Tariff Agent for a complex quote.** 'Estimate the duty for 1000 USD of leather shoes from Vietnam.' The orchestrator splits it: researcher finds the HS code and rate, analyst computes the amount, orchestrator checks the result and writes the final answer. NOT RUN: it needs a real LLM; no outputs are claimed here.

## 🟡 Real Example Hindi mein
**जटिल quote के लिए Tariff Agent.** 'वियतनाम से 1000 USD के leather shoes की duty का अनुमान।' Orchestrator इसे बाँटता है: researcher HS code और दर खोजता है, analyst रकम निकालता है, orchestrator नतीजा जाँचकर अंतिम जवाब लिखता है। चलाया नहीं गया: असली LLM चाहिए; कोई output दावा नहीं किया गया।

---

## 💻 Code Example — Basic
Basic: construction and streaming to the terminal with `Console`. NOT RUN end to end (needs a real model and `OPENAI_API_KEY`); executing it here stopped at client creation with `openai.OpenAIError: Missing credentials`, which only proves the code reaches the real client. The file was syntax-checked and imports were checked. Model names change; check your account.

```python
# Basic: MagenticOneGroupChat construction (the orchestrator plans with a REAL LLM; NOT RUN end-to-end: needs an API key)
import asyncio  # loop
from autogen_ext.models.openai import OpenAIChatCompletionClient  # real model client (needs OPENAI_API_KEY at run time)
from autogen_agentchat.agents import AssistantAgent  # agent
from autogen_agentchat.teams import MagenticOneGroupChat  # orchestrated team
from autogen_agentchat.ui import Console  # pretty print stream

async def main() -> None:  # entry
    model = OpenAIChatCompletionClient(model="gpt-4o")  # any ChatCompletionClient works; check your account's model names
    researcher = AssistantAgent("researcher", model, description="Finds tariff facts")  # worker 1 (description guides the planner)
    analyst = AssistantAgent("analyst", model, description="Computes duty and totals")  # worker 2
    team = MagenticOneGroupChat([researcher, analyst], model_client=model, max_turns=10, max_stalls=3)  # orchestrator keeps a ledger + replans on stalls
    await Console(team.run_stream(task="Estimate duty for 1000 USD of leather shoes from Vietnam"))  # stream to terminal

if __name__ == "__main__":  # guard
    asyncio.run(main())  # go
```

## 💻 Code Example — Advanced
Advanced: FastAPI endpoint with guards: `max_turns`, `max_stalls`, a `TokenUsageTermination` budget and a hard `asyncio.wait_for` timeout. NOT RUN (needs a real LLM); syntax and imports checked, objects not exercised.

```python
# Advanced: MagenticOne behind FastAPI with guards (NOT RUN: needs a real LLM; import + construction are checked)
import asyncio  # asyncio
import os  # env
from fastapi import FastAPI, HTTPException  # web
from pydantic import BaseModel  # body
from autogen_ext.models.openai import OpenAIChatCompletionClient  # model client
from autogen_agentchat.agents import AssistantAgent  # agent
from autogen_agentchat.teams import MagenticOneGroupChat  # team
from autogen_agentchat.conditions import TokenUsageTermination  # budget

app = FastAPI()  # app

class Req(BaseModel):  # body
    task: str  # open-ended goal

def build(model_name: str) -> MagenticOneGroupChat:  # factory per request
    model = OpenAIChatCompletionClient(model=model_name)  # one client shared by orchestrator + workers
    workers = [AssistantAgent("researcher", model, description="Finds facts"), AssistantAgent("analyst", model, description="Does maths")]  # workers
    return MagenticOneGroupChat(workers, model_client=model, max_turns=12, max_stalls=2, termination_condition=TokenUsageTermination(max_total_token=60_000))  # caps cost

@app.post("/solve")  # endpoint
async def solve(req: Req) -> dict[str, object]:  # handler
    try:  # guard
        res = await asyncio.wait_for(build(os.environ.get("MODEL", "gpt-4o")).run(task=req.task), timeout=180)  # hard timeout
    except asyncio.TimeoutError:  # slow
        raise HTTPException(504, "magentic-one timed out")  # 504
    return {"answer": str(res.messages[-1].content), "stop": res.stop_reason}  # answer
```

**Verification status:** parameter lists read from the installed package (autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13)). Neither example was executed against a model (not run -- needs an OpenAI-compatible API key). No Magentic-One behaviour (planning quality, number of calls, cost) was measured; statements about it come from the documented design, so verify in your environment.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---|---|---|---|---|
| Planner/orchestrator | Supervisor / plan-and-execute graph | Hierarchical process (manager) | Triage / manager agent | MagenticOneGroupChat orchestrator |
| Progress ledger / re-plan | You build | Limited | You build | Built in (max_stalls) |
| Predictability | High | Medium | Medium | Low: LLM-driven |
| Cost | You control | Manager overhead | Moderate | High: many orchestrator calls |
| Tools needed | Any | Any | Any | Workers bring tools (code, web, files) |
| Best for | Known workflows | Role pipelines | Handoffs | Open-ended exploratory tasks |

---

## ⚠️ Common Mistakes
❌ Mistake: Using Magentic-One for a simple lookup.
✅ Correct: It is overkill and expensive; use one AssistantAgent with a tool.

❌ Mistake: No cost cap.
✅ Correct: Set `max_turns`, `max_stalls` and `TokenUsageTermination`; orchestrators can spend a lot.

❌ Mistake: Giving workers vague descriptions.
✅ Correct: The orchestrator assigns work by description; be specific about each worker's skills.

❌ Mistake: Running powerful workers (code, browser) without sandboxing.
✅ Correct: Magentic-One style teams are meant to run in isolated environments; use Docker for any code or web agent.

---

## 🧠 Tricky Interview Question
Your Magentic-One team spends 30 model calls on a task a rules engine could do. How do you decide where it belongs?

Answer: Measure first: log calls/tokens per task and success rate against a baseline (single agent with tools, or a selector team). Use Magentic-One only for tasks where the path cannot be known in advance and the value per task justifies the cost. For recurring, well-understood tasks, convert the discovered plan into a fixed workflow (round robin, graph) and keep the orchestrator for the exceptions. Add budgets (max_turns, tokens, timeout) and a human escalation path when stalls occur.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is the role of the orchestrator?
A1: It plans, tracks progress in a ledger, picks the next participant with an instruction, re-plans on stalls and writes the final answer.

Q2: [Medium] What does max_stalls do?
A2: Number of consecutive rounds without progress before the orchestrator re-plans (we only checked that the parameter exists in 0.7.5).

Q3: [Hard] Why is cost unpredictable?
A3: Orchestrator calls (plan, ledger every turn, final answer) are on top of worker calls, and re-planning adds more; the number of turns is model-decided.

Q4: [Hard] How do you contain risk?
A4: Budgets, timeouts, sandboxed workers, restricted tools, human approval for side effects, full message logging.

Q5: [System Design] Design a research assistant using Magentic-One.
A5: Workers: web researcher (read-only), analyst (sandboxed code), writer; orchestrator on a strong model, workers on cheaper ones; budgets and timeouts; cache results; evaluate on a task set and compare to a single-agent baseline.

---

## 💰 Cost Impact
Expect many model calls: planning, a progress-ledger call every turn, worker calls, re-plans and a final answer. Do not estimate a fixed figure; instrument your own runs. Formula: `cost = (orchestrator_calls * orch_tokens + worker_calls * worker_tokens) * price`. Tips: strong model only for the orchestrator, cap with `max_turns`/`max_stalls`/`TokenUsageTermination`, cache repeated lookups. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Open-ended, multi-step tasks with unknown path.
- Tasks needing planning and recovery from stalls.
- Workers with real tools (sandboxed).

❌ Avoid when:
- Simple lookups or fixed workflows.
- Strict cost or latency budgets.
- No isolation for code/browser workers.

---

## 📊 Visual Diagram
```
 task
   |
   v
 [ Orchestrator ]  facts + plan
   |   ^   progress ledger every turn (done? stuck? next speaker + instruction)
   v   |
 [ researcher ] [ analyst ] [ coder ] ...   (workers report back)
   |
   +-- stalled > max_stalls ? --> update facts, RE-PLAN
   |
   v
 final answer (final_answer_prompt)   | caps: max_turns, tokens, timeout
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|---|---|---|
| Orchestrator | Planner agent that directs workers | workers को निर्देश देने वाला planner agent |
| ledger | Structured progress record | प्रगति का संरचित रिकॉर्ड |
| stall | A round with no progress | बिना प्रगति वाला round |
| max_stalls | Stalls allowed before re-planning | re-plan से पहले अनुमत stalls |
| re-plan | Make a new plan | नई योजना बनाना |
| final_answer_prompt | Prompt for the closing answer | अंतिम जवाब का prompt |
| worker | Agent that does a sub-task | उप-कार्य करने वाला agent |

---

## ⚡ 3-Line Summary
English: Magentic-One uses an orchestrator that plans, tracks a ledger and re-plans on stalls.
Great for open-ended tasks; expensive and less predictable.
Always cap turns, stalls and tokens, and sandbox workers.
Hindi: Magentic-One में orchestrator योजना बनाता है, ledger रखता है और stall पर re-plan करता है।
Open-ended tasks के लिए बढ़िया; महँगा और कम अनुमानित।
हमेशा turns, stalls और tokens सीमित करें और workers को sandbox में चलाएँ।

---

## ➡️ Next Topic
151. Swarm Team -- agents hand work to each other with HandoffMessage.

---
