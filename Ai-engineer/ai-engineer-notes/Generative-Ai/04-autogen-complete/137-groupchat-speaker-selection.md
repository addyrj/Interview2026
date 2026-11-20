---

# 137. GroupChat Speaker Selection
# हिंदी में: GroupChat में speaker selection
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
Speaker selection decides which agent talks next. In `RoundRobinGroupChat` it is a fixed cycle. In `SelectorGroupChat` it is an LLM call using agent names and descriptions and the history, optionally steered by `selector_prompt`, `allow_repeated_speaker`, `selector_func` (deterministic override) and `candidate_func` (narrow the choices).

## 🔵 सरल परिभाषा (Hindi)
Speaker selection तय करता है कि अगला कौन बोलेगा। `RoundRobinGroupChat` में यह तय चक्र है। `SelectorGroupChat` में यह LLM call है जो agent names, descriptions और history देखता है, और जिसे `selector_prompt`, `allow_repeated_speaker`, `selector_func` (deterministic override) और `candidate_func` (विकल्प सीमित करना) से नियंत्रित कर सकते हैं।

---

## 🔴 Problem it Solves
If the wrong agent speaks (the rater before the classifier), the answer is wrong. If the same agent speaks repeatedly, the run loops. If an LLM chooses every time, it adds cost and latency, and sometimes returns invalid names. You need levers to make routing predictable where it can be, and flexible where it must be.

## 🔴 यह क्यों बना? (Hindi)
गलत agent बोले (classifier से पहले rater) तो जवाब गलत होगा। एक ही agent बार-बार बोले तो loop बनता है। हर बार LLM चुने तो cost और latency बढ़ती है और कभी invalid नाम भी लौटता है। ऐसे levers चाहिए जो जहाँ संभव हो routing को predictable बनाएँ और जहाँ ज़रूरी हो flexible रखें।

---

## 🟢 How it Works

```
Step 1 -> After each message, manager calls selector_func(messages) if provided
Step 2 -> selector_func returns a name -> that agent speaks (no LLM call)
Step 3 -> Returns None -> fall back to the LLM selector
Step 4 -> candidate_func(messages) -> list of allowed names, LLM picks among them
Step 5 -> LLM selector fills selector_prompt ({roles}, {participants}, {history})
Step 6 -> allow_repeated_speaker=False excludes the previous speaker
Step 7 -> Invalid name -> retry up to max_selector_attempts, then fall back to the previous speaker or first participant (a warning is logged)
Step 8 -> Chosen agent speaks; loop
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> हर message के बाद manager selector_func(messages) call करता है (अगर दिया हो)
Step 2 -> selector_func नाम लौटाए -> वही agent बोलता है (LLM call नहीं)
Step 3 -> None लौटे -> LLM selector पर fallback
Step 4 -> candidate_func(messages) -> अनुमत नामों की list, LLM उनमें से चुनता है
Step 5 -> LLM selector selector_prompt भरता है ({roles}, {participants}, {history})
Step 6 -> allow_repeated_speaker=False पिछले speaker को हटा देता है
Step 7 -> invalid नाम -> max_selector_attempts तक retry, फिर पिछला speaker या पहला participant (warning log होती है)
Step 8 -> चुना हुआ agent बोलता है; loop
```

---

## 🟡 Real World Example
**Hybrid routing for tariff requests.** After the user message only the classifier may speak (`candidate_func` returns one name). After classification, the LLM chooses between `rater` and `compliance` depending on whether the goods look restricted. Everything else is deterministic. You pay for one small selector call instead of one per turn, and the flow cannot start with the wrong agent.

## 🟡 Real Example Hindi mein
**Tariff requests के लिए hybrid routing।** User message के बाद सिर्फ़ classifier बोल सकता है (`candidate_func` एक नाम लौटाता है)। Classification के बाद LLM तय करता है कि `rater` बोले या `compliance`, इस आधार पर कि माल restricted लगता है या नहीं। बाकी सब deterministic है। आप हर turn की जगह एक छोटा selector call चुकाते हैं और flow गलत agent से शुरू नहीं हो सकता।

---

## 💻 Code Example — Basic
Basic: the three string/flag knobs (`selector_prompt`, `allow_repeated_speaker`, `max_selector_attempts`) with a scripted selector model.

```python
# Speaker selection, 3 knobs of SelectorGroupChat: selector_prompt, allow_repeated_speaker, selector_func
import asyncio                                                    # async
from autogen_agentchat.agents import AssistantAgent               # agent
from autogen_agentchat.conditions import MaxMessageTermination    # stop rule
from autogen_agentchat.teams import SelectorGroupChat            # team
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

PROMPT = (                                                        # placeholders {roles} {participants} {history} are filled by AutoGen
    "Roles:\n{roles}\n\nHistory:\n{history}\n\n"
    "Pick the next speaker from {participants}. Return ONLY the name."
)

async def main() -> None:
    agents = [
        AssistantAgent("classifier", ReplayChatCompletionClient(["HS 6109.10"]), description="Finds HS code"),
        AssistantAgent("rater", ReplayChatCompletionClient(["20%"]), description="Finds duty rate"),
    ]
    team = SelectorGroupChat(
        agents,
        model_client=ReplayChatCompletionClient(["classifier", "rater"]),  # the SELECTOR model (use a cheap one in prod)
        selector_prompt=PROMPT,                                   # custom selection prompt
        allow_repeated_speaker=False,                             # same agent cannot speak twice in a row
        max_selector_attempts=3,                                  # retries if selector returns a bad name
        termination_condition=MaxMessageTermination(3),           # user task + 2 agent turns
    )
    res = await team.run(task="Duty for cotton t-shirt?")
    print([m.source for m in res.messages])                       # ['user', 'classifier', 'rater']

if __name__ == "__main__":
    asyncio.run(main())
```

## 💻 Code Example — Advanced
Advanced: a `candidate_func` limits who the selector LLM may choose, exposed via FastAPI. In the offline run the termination at 3 messages ended before `compliance` was reached.

```python
# Deterministic + LLM hybrid: candidate_func narrows who the LLM may choose; FastAPI; fallbacks
import asyncio                                                    # async
from typing import Sequence                                       # typing
from fastapi import FastAPI, HTTPException                        # web
from fastapi.testclient import TestClient                         # offline test
from autogen_agentchat.agents import AssistantAgent               # agent
from autogen_agentchat.conditions import MaxMessageTermination    # stop rule
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage  # message base types
from autogen_agentchat.teams import SelectorGroupChat            # team
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

def candidates(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> list[str]:
    last = messages[-1]                                           # most recent message
    if last.source == "user":                                     # first turn: only the classifier is allowed
        return ["classifier"]
    if last.source == "classifier":                               # after classification: rater or compliance (LLM decides)
        return ["rater", "compliance"]
    return ["classifier", "rater", "compliance"]                  # otherwise anyone

def build() -> SelectorGroupChat:
    agents = [
        AssistantAgent("classifier", ReplayChatCompletionClient(["HS 6109.10"]), description="HS code"),
        AssistantAgent("rater", ReplayChatCompletionClient(["20%"]), description="duty rate"),
        AssistantAgent("compliance", ReplayChatCompletionClient(["no restrictions"]), description="import restrictions"),
    ]
    # scripted selector replies (used when the selector LLM is asked to choose)
    selector = ReplayChatCompletionClient(["classifier", "rater", "compliance"])
    return SelectorGroupChat(agents, model_client=selector, candidate_func=candidates,
                             termination_condition=MaxMessageTermination(3))

app = FastAPI()

@app.post("/route")
async def route(body: dict) -> dict:
    try:
        res = await asyncio.wait_for(build().run(task=body["task"]), timeout=30)
    except KeyError:
        raise HTTPException(422, "task required")
    except Exception as exc:                                      # e.g. selector failed 3 times
        raise HTTPException(500, str(exc))
    return {"order": [m.source for m in res.messages]}

if __name__ == "__main__":
    print(TestClient(app).post("/route", json={"task": "duty for t-shirt"}).json())
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Routing mechanism | Conditional edges (code or LLM) | Process / delegation | Handoffs chosen by LLM | selector (LLM) / selector_func / candidate_func |
| Deterministic override | Plain edges | Sequential process | Fixed agent chain | selector_func returning a name |
| Restrict choices | Edge map | allowed delegation | handoffs list | candidate_func |
| Selector cost | Router LLM call | Manager LLM calls | The agent itself chooses (no extra call) | One extra LLM call per turn when LLM-selected |
| Failure mode | Bad edge label | Wrong delegation | Wrong handoff | Invalid name -> retries -> fallback speaker |

---

## ⚠️ Common Mistakes
❌ Mistake: Agent `description`s that overlap or are empty: the selector picks randomly.
✅ Correct: Write one distinct sentence per agent describing when it should speak.

❌ Mistake: A selector prompt that forgets `{participants}`, so the model invents roles.
✅ Correct: Keep `{roles}`, `{history}` and `{participants}` in the prompt.

❌ Mistake: `allow_repeated_speaker=False` for an agent that legitimately needs consecutive turns (tool loops are inside one turn, so usually fine).
✅ Correct: Allow repeats only if a workflow needs it, and add a hard cap.

❌ Mistake: Using a flagship model for selection.
✅ Correct: A small, fast model is usually enough for choosing among a handful of names; evaluate it.

---

## 🧠 Tricky Interview Question
Your selector LLM keeps returning 'Let me think... the rater' and you see 'Model failed to select a speaker' warnings. What is happening and how do you fix it?

Answer: The framework expects the reply to contain exactly the agent name; extra prose or wrong names count as failures, and after `max_selector_attempts` it falls back to a default speaker (seen offline: 'Model failed to select a speaker after 3 and there was no previous speaker, using the first participant'). Fixes: tighten `selector_prompt` ('Return ONLY the name'), reduce the number of agents, give them short exact names, use a model with good instruction following at temperature 0, use `candidate_func` to cut options to 1-2, or use `selector_func` for the deterministic parts. Add monitoring on the warning count.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does `selector_func` returning `None` mean?
A1: Fall back to the model-based selection. Returning a name forces that speaker.

Q2: [Medium] What is `candidate_func` for?
A2: It returns the list of agent names the selector model may choose from; useful to prune options and to force order at specific points.

Q3: [Hard] What does `allow_repeated_speaker` do?
A3: If False, the previous speaker is not eligible for the next turn.

Q4: [Hard] How do you reduce selector cost?
A4: Deterministic `selector_func`, `candidate_func` with single candidates, small selector model, fewer agents, concise descriptions.

Q5: [System Design] Design routing for 12 specialist agents.
A5: Do not expose all 12 to the LLM at once. Two-level routing: a triage agent or `candidate_func` first narrows to a domain (3-4 agents), then the selector picks. Use embeddings or rules to pre-filter, log routing decisions, and evaluate routing accuracy on a labelled set; keep a default fallback agent.

---

## 💰 Cost Impact
With LLM selection each turn costs an extra call: prompt = roles (all descriptions) + full history, output = a few tokens. For N agents with long descriptions the roles block repeats every call. Formula: `selector_cost_per_turn ~ (roles_tokens + history_tokens) * in_price + ~5 * out_price`. A `selector_func` removes it entirely for those turns. Estimate: a 10-turn run with selection every turn pays 10 selector calls, usually small compared with the agents' own turns if the selector model is cheap, but not negligible when history is long. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Dynamic flows where the next expert depends on content.
- Hybrid: deterministic skeleton + LLM choice at branch points.
- Teams with unique, well-described roles.

❌ Avoid when:
- Fixed pipelines: use round robin or `GraphFlow`.
- Many overlapping agents with vague descriptions.
- Latency-critical paths where an extra LLM call per turn is unacceptable.

---

## 📊 Visual Diagram
```
 new message
     |
     v
 selector_func(messages) --name--> speaker  (no LLM)
     | None
     v
 candidate_func(messages) --> allowed = [rater, compliance]
     |
     v
 LLM selector (selector_prompt + {roles} {history} {participants})
     |  name valid?  --no--> retry (max_selector_attempts) --> fallback speaker
     v yes
 allow_repeated_speaker filter --> chosen agent speaks
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| selector_prompt | Template for the selector LLM | selector LLM का template |
| selector_func | Deterministic speaker chooser | deterministic speaker चुनने वाला function |
| candidate_func | Narrows allowed speakers | अनुमत speakers सीमित करता है |
| allow_repeated_speaker | Permit same speaker twice in a row | एक ही speaker को लगातार बोलने देना |
| max_selector_attempts | Retries for invalid selection | invalid selection पर retries |
| description | Agent text the selector reads | जो text selector पढ़ता है |
| fallback speaker | Default when selection fails | selection fail होने पर default |
| routing | Choosing the next agent | अगला agent चुनना |

---

## ⚡ 3-Line Summary
English: Speaker selection = fixed (round robin), LLM (selector), or code (selector_func/candidate_func).
Use code for predictable steps and the LLM only at real decision points; write distinct descriptions.
Every LLM-selected turn costs an extra call: use a cheap model and watch fallback warnings.
Hindi: Speaker selection = तय क्रम (round robin), LLM (selector), या code (selector_func/candidate_func)।
अनुमानित steps के लिए code और असली निर्णय बिंदुओं पर ही LLM इस्तेमाल करें; descriptions अलग-अलग लिखें।
LLM से चुने हर turn पर अतिरिक्त call लगती है: सस्ता model लें और fallback warnings पर नज़र रखें।

---

## ➡️ Next Topic
138. GroupChat with Custom Speaker -- building your own state machine on top of selector_func.

---
