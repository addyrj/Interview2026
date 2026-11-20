---

# 136. GroupChatManager
# हिंदी में: GroupChatManager — team के अंदर का संचालक
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
In v0.2, `GroupChatManager` was a visible agent that ran the group chat: it selected speakers, broadcast replies and ended the chat. In v0.4 there is no public `GroupChatManager` class (checked: not exported from `autogen_agentchat.teams`). The manager is an internal agent inside each team (for example `SelectorGroupChatManager`, which extends `BaseGroupChatManager`). You control it through team parameters.

## 🔵 सरल परिभाषा (Hindi)
v0.2 में `GroupChatManager` एक दिखने वाला agent था जो group chat चलाता था: speaker चुनना, replies broadcast करना, chat खत्म करना। v0.4 में public `GroupChatManager` class नहीं है (जाँचा: `autogen_agentchat.teams` से export नहीं होती)। Manager हर team के अंदर का internal agent है (जैसे `SelectorGroupChatManager`, जो `BaseGroupChatManager` से बना है)। आप इसे team parameters से नियंत्रित करते हैं।

---

## 🔴 Problem it Solves
Someone has to own the shared thread, decide whose turn it is, check termination and handle state. If that logic is mixed into user-facing agents, every custom team re-implements it. v0.2 solved it with a manager agent that could be misconfigured (its own `llm_config`, `max_round`). v0.4 hides it and exposes only the knobs that matter.

## 🔴 यह क्यों बना? (Hindi)
किसी को साझा thread संभालना है, तय करना है किसकी बारी है, termination जाँचना है और state संभालना है। अगर यह logic user-facing agents में मिल जाए तो हर custom team इसे दोबारा लिखेगी। v0.2 ने इसे manager agent से हल किया जो गलत configure हो सकता था (अपना `llm_config`, `max_round`)। v0.4 इसे छुपाता है और सिर्फ़ ज़रूरी knobs देता है।

---

## 🟢 How it Works

```
Step 1 -> team.run(task) starts a runtime and a hidden manager agent
Step 2 -> Manager stores the task and broadcasts it to all participants
Step 3 -> Manager asks the next speaker(s) to respond (policy depends on team type)
Step 4 -> Participant replies; manager appends to the thread and re-broadcasts
Step 5 -> Manager evaluates termination_condition and max_turns
Step 6 -> If stop: emits TaskResult(stop_reason); termination state resets for the next run
Step 7 -> team.run() again RESUMES with the same thread; team.reset() clears it
Step 8 -> save_state()/load_state() checkpoint the manager thread + every agent
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> team.run(task) runtime और छुपा हुआ manager agent शुरू करता है
Step 2 -> Manager task सहेजकर सभी participants को broadcast करता है
Step 3 -> Manager अगले speaker(s) से जवाब माँगता है (policy team type पर निर्भर)
Step 4 -> Participant जवाब देता है; manager thread में जोड़कर दोबारा broadcast करता है
Step 5 -> Manager termination_condition और max_turns जाँचता है
Step 6 -> रुकना हो तो TaskResult(stop_reason) भेजता है; अगले run के लिए termination state reset होती है
Step 7 -> दोबारा team.run() उसी thread से RESUME करता है; team.reset() thread मिटाता है
Step 8 -> save_state()/load_state() manager thread + हर agent का checkpoint लेते हैं
```

---

## 🟡 Real World Example
**Pausing a tariff review.** A review team runs 2 turns (`max_turns=2`), then pauses so a human can look. Calling `team.run()` again continues the same thread with the next 2 turns. Later the service restarts: you rebuild the team and `load_state()` from the database; the manager's thread comes back, so the agents keep their context.

## 🟡 Real Example Hindi mein
**Tariff review को pause करना।** Review team 2 turns चलती है (`max_turns=2`), फिर रुकती है ताकि human देख सके। दोबारा `team.run()` उसी thread को अगले 2 turns तक आगे बढ़ाता है। बाद में service restart हो तो team दोबारा बनाकर database से `load_state()` करते हैं; manager का thread लौट आता है और agents अपना context रखते हैं।

---

## 💻 Code Example — Basic
Basic: `max_turns` makes the hidden manager stop after N agent turns; a second `run()` resumes; `reset()` clears. (Verified output: run1 = user, a, b; run2 = a, b continuing the script.)

```python
# v0.2 GroupChatManager -> v0.4: the manager is INTERNAL to the team. You control it via team params.
import asyncio                                                    # async
from autogen_agentchat.agents import AssistantAgent               # agent
from autogen_agentchat.conditions import MaxMessageTermination    # stop rule
from autogen_agentchat.teams import RoundRobinGroupChat           # team (owns a hidden manager agent)
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

async def main() -> None:
    a = AssistantAgent("a", ReplayChatCompletionClient(["a1", "a2", "a3"]))
    b = AssistantAgent("b", ReplayChatCompletionClient(["b1", "b2", "b3"]))
    team = RoundRobinGroupChat([a, b], max_turns=2)               # max_turns = manager stops after N agent turns
    r1 = await team.run(task="start")                             # first run: a, b
    print("run1:", [(m.source, m.content) for m in r1.messages], "|", r1.stop_reason)
    r2 = await team.run()                                         # RESUME: manager keeps the shared thread; task optional
    print("run2:", [(m.source, m.content) for m in r2.messages], "|", r2.stop_reason)
    await team.reset()                                            # manager forgets history, agents reset too
    print("reset done")

if __name__ == "__main__":
    asyncio.run(main())
```

## 💻 Code Example — Advanced
Advanced: termination + checkpoint/resume across HTTP requests, rebuilding the team each time and restoring it with `load_state`. The replay clients are module level so the scripted replies continue; a real LLM client is stateless anyway.

```python
# Manager responsibilities in practice: termination, pause/resume via save_state/load_state, FastAPI
import asyncio                                                    # async
from fastapi import FastAPI                                       # web
from fastapi.testclient import TestClient                         # offline test
from autogen_agentchat.agents import AssistantAgent               # agent
from autogen_agentchat.conditions import MaxMessageTermination    # stop rule
from autogen_agentchat.teams import RoundRobinGroupChat           # team
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

app = FastAPI()
SAVED: dict[str, dict] = {}                                       # session -> state (Redis/Postgres in prod)

CLIENT_A = ReplayChatCompletionClient(["a1", "a2", "a3", "a4"])   # module-level so a rebuilt team continues the script
CLIENT_B = ReplayChatCompletionClient(["b1", "b2", "b3", "b4"])   # (a real LLM client is stateless anyway)

def build() -> RoundRobinGroupChat:
    a = AssistantAgent("a", CLIENT_A)
    b = AssistantAgent("b", CLIENT_B)
    return RoundRobinGroupChat([a, b], termination_condition=MaxMessageTermination(3))  # manager checks this after each message

@app.post("/step/{sid}")
async def step(sid: str, body: dict) -> dict:
    team = build()                                                # new process may serve the next call -> rebuild
    if sid in SAVED:
        await team.load_state(SAVED[sid])                         # restores manager thread + each agent's context
    res = await team.run(task=body.get("task"))                   # task None on resume is allowed
    SAVED[sid] = await team.save_state()                          # checkpoint
    return {"new_messages": [(m.source, str(m.content)) for m in res.messages], "stop": res.stop_reason}

if __name__ == "__main__":
    c = TestClient(app)
    print(c.post("/step/s1", json={"task": "begin"}).json())
    print(c.post("/step/s1", json={}).json())                     # resumed in a brand-new team object
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Orchestrator | Graph runtime + conditional edges | Process (sequential/hierarchical) + manager agent | Runner loop | Hidden manager agent inside each team |
| Visible manager object | StateGraph app | Manager agent in hierarchical mode | Orchestrator agent you write | No public class in v0.4 (v0.2: GroupChatManager) |
| Checkpoint | Checkpointer per step | Limited | Sessions | save_state/load_state (manual persistence) |
| Resume | Invoke with thread_id | Re-kickoff | New run with session | run() again continues the thread |
| Customise policy | Edges/functions | Process type | Your code | selector_func / candidate_func / custom team |

---

## ⚠️ Common Mistakes
❌ Mistake: Importing `GroupChatManager` in v0.4.
✅ Correct: Configure the team instead: `termination_condition`, `max_turns`, `selector_func`.

❌ Mistake: Calling `run()` twice and being surprised that history carries over.
✅ Correct: `run()` resumes. Use `reset()` or a new team for a new conversation.

❌ Mistake: Passing `task` again on resume and duplicating the instruction.
✅ Correct: On resume call `run()` with no task, or a new task only if you intend to add a message.

❌ Mistake: Saving state but not storing the version/schema. After a library upgrade `load_state` can fail.
✅ Correct: Store the state with the package version; test restore in CI.

---

## 🧠 Tricky Interview Question
You need the manager to also enforce a per-conversation budget of 20,000 tokens. There is no public GroupChatManager to subclass. What are your options?

Answer: Use composable termination conditions: `TokenUsageTermination(max_total_token=20000)` (check the exact parameter names in the installed version) combined with `MaxMessageTermination` and `TimeoutTermination` using `|`. They are evaluated by the manager after each message. If you need custom logic, `FunctionalTermination` accepts a function over the latest messages, or an `ExternalTermination` you trigger from your own budget monitor (for example, a Redis counter shared across services). Subclassing the internal manager is possible but not a stable public API, so avoid it.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Is there a `GroupChatManager` in v0.4?
A1: Not as a public class. The manager is an internal agent in each team, for example `SelectorGroupChatManager` extending `BaseGroupChatManager`.

Q2: [Medium] How do you limit rounds, as `max_round` did in v0.2?
A2: `max_turns=N` on the team, or `MaxMessageTermination(N)` (which counts the task message too).

Q3: [Hard] What does a second `team.run()` do?
A3: Resumes with the same shared thread. Use `reset()` to start fresh.

Q4: [Hard] How do you persist and restore a team?
A4: `state = await team.save_state()` (a dict with type, version, agent_states), store it, later `await team.load_state(state)` on a freshly built team with the same agents.

Q5: [System Design] Design a resumable long-running review workflow.
A5: Team with `max_turns` or `HandoffTermination` per stage; after every stage `save_state()` into DB with a version and the stop_reason; a scheduler or webhook resumes by rebuilding and loading; idempotent tools; a watchdog `TimeoutTermination`; metrics per stage.

---

## 💰 Cost Impact
The manager adds no cost for RoundRobin; for `SelectorGroupChat` its selector model call happens every turn (prompt = roles + history), which can be a large share of cost. Resuming does not re-bill earlier turns by itself, but each new turn re-sends the full restored history to the speaker, so a long saved thread is expensive per turn. Controls: bounded `model_context` on agents, a small model for the selector, summarising old history into one message before resuming. Formula: `resume_turn_cost ~ (saved_history_tokens + new_tokens) * in_price`. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- You need pause/resume or checkpointing of a team.
- You must understand why a team stopped (`stop_reason`).
- Porting v0.2 `max_round` and manager configuration.

❌ Avoid when:
- Trying to subclass internal managers for production features.
- Resuming extremely long threads without trimming context.

---

## 📊 Visual Diagram
```
 team.run(task)
     |
     v
 +---------------- hidden manager agent ----------------+
 | thread = [user, a1, b1, ...]                          |
 | 1. pick next speaker(s)  (policy of team type)        |
 | 2. send request --> participant --> reply             |
 | 3. append + broadcast                                 |
 | 4. check termination_condition / max_turns            |
 +----------------------+--------------------------------+
                        | stop
                        v
 TaskResult(stop_reason)  --save_state()--> DB --load_state()--> new team --run()--> continues
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| GroupChatManager | v0.2 manager agent (not public in v0.4) | v0.2 का manager agent (v0.4 में public नहीं) |
| BaseGroupChatManager | Internal base of team managers | team managers की internal base |
| max_turns | Agent turns before pausing | रुकने से पहले agent turns |
| save_state | Checkpoint team state | team state checkpoint |
| load_state | Restore a checkpoint | checkpoint वापस लाना |
| reset | Clear the thread | thread साफ़ करना |
| stop_reason | Explanation of the stop | रुकने का कारण |
| thread | Shared message history | साझा message history |

---

## ⚡ 3-Line Summary
English: v0.4 has no public GroupChatManager: the manager is hidden inside each team.
Control it with termination conditions, max_turns, selector functions and save_state/load_state.
A second run() resumes the thread; reset() starts clean.
Hindi: v0.4 में public GroupChatManager नहीं है: manager हर team के अंदर छुपा है।
इसे termination conditions, max_turns, selector functions और save_state/load_state से नियंत्रित करें।
दूसरा run() thread को आगे बढ़ाता है; reset() नया शुरू करता है।

---

## ➡️ Next Topic
137. GroupChat Speaker Selection -- the single most important team knob for quality and cost.

---
