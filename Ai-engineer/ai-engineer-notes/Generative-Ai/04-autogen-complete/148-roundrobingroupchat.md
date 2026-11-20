---

# 148. RoundRobinGroupChat
# हिंदी में: RoundRobinGroupChat (बारी-बारी से बोलने वाली team)
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
`RoundRobinGroupChat` makes participants speak in a fixed cyclic order: a, b, c, a, b, c ... Every message is broadcast to everyone. It costs no extra model call for choosing the speaker, so it is the cheapest and most predictable team. Signature in 0.7.5: `RoundRobinGroupChat(participants, name, description, termination_condition, max_turns, runtime, custom_message_types, emit_team_events)`.

## 🔵 सरल परिभाषा (Hindi)
`RoundRobinGroupChat` में participants तय चक्र में बोलते हैं: a, b, c, a, b, c ... हर message सबको broadcast होता है। बोलने वाला चुनने के लिए अतिरिक्त model call नहीं लगता, इसलिए यह सबसे सस्ती और अनुमान लगाने लायक team है। 0.7.5 में signature: `RoundRobinGroupChat(participants, name, description, termination_condition, max_turns, runtime, custom_message_types, emit_team_events)`।

---

## 🔴 Problem it Solves
Many workflows are naturally a loop: draft, review, revise. Using an LLM to choose who speaks next adds cost, latency and randomness. Round robin removes that decision completely.

## 🔴 यह क्यों बना? (Hindi)
कई workflows स्वाभाविक रूप से loop होते हैं: draft, review, revise। अगला वक्ता चुनने के लिए LLM लगाने से खर्च, देरी और अनिश्चितता बढ़ती है। Round robin यह फैसला पूरी तरह हटा देता है।

---

## 🟢 How it Works

```
Step 1 -> Task message goes to the first participant
Step 2 -> First participant replies; reply is broadcast to all
Step 3 -> Next participant in list order speaks (no LLM chooses)
Step 4 -> After the last participant it wraps to the first
Step 5 -> Termination condition is checked after each message
Step 6 -> Stops with a stop_reason such as 'Maximum number of messages 5 reached'
Step 7 -> max_turns can also cap the number of turns
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Task message पहले participant के पास जाता है
Step 2 -> पहला participant जवाब देता है; जवाब सबको broadcast होता है
Step 3 -> सूची के क्रम में अगला participant बोलता है (कोई LLM नहीं चुनता)
Step 4 -> आखिरी के बाद फिर पहले पर लौटता है
Step 5 -> हर message के बाद termination condition जाँची जाती है
Step 6 -> 'Maximum number of messages 5 reached' जैसे stop_reason के साथ रुकता है
Step 7 -> max_turns से भी turns सीमित किए जा सकते हैं
```

---

## 🟡 Real World Example
**Tariff Agent draft/review loop.** `classifier` proposes an HS code, `critic` says 'too vague', `classifier` refines, `critic` says 'good'. The observed message order was `['user', 'classifier', 'critic', 'classifier', 'critic']` and it stopped at the message cap. Predictable and cheap.

## 🟡 Real Example Hindi mein
**Tariff Agent का draft/review loop.** `classifier` HS code सुझाता है, `critic` कहता है 'too vague', `classifier` सुधारता है, `critic` कहता है 'good'। देखा गया क्रम `['user', 'classifier', 'critic', 'classifier', 'critic']` था और यह message सीमा पर रुका। अनुमान लगाने योग्य और सस्ता।

---

## 💻 Code Example — Basic
Basic: two scripted agents; the printed source order proves round robin. Note the count: 1 task message + 4 turns = 5 messages.

```python
# Basic: RoundRobinGroupChat: fixed turn order a -> b -> a -> b
import asyncio  # loop
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM
from autogen_agentchat.agents import AssistantAgent  # agent
from autogen_agentchat.teams import RoundRobinGroupChat  # team
from autogen_agentchat.conditions import MaxMessageTermination  # stop

async def main() -> None:  # entry
    a = AssistantAgent("classifier", ReplayChatCompletionClient(["try 6403", "fixed: 6403.99"]))  # speaks 1st, 3rd
    b = AssistantAgent("critic", ReplayChatCompletionClient(["too vague", "good"]))  # speaks 2nd, 4th
    team = RoundRobinGroupChat([a, b], termination_condition=MaxMessageTermination(5))  # 1 task msg + 4 turns
    res = await team.run(task="Classify leather shoes")  # run
    print([m.source for m in res.messages])  # order proves round robin
    print(res.stop_reason)  # reason

asyncio.run(main())  # go
```

## 💻 Code Example — Advanced
Advanced: draft/review loop that stops on the keyword APPROVE, with retries around the whole team, a hard timeout and FastAPI error mapping (HTTP 502 when all attempts fail).

```python
# Advanced: draft->review loop with explicit approval keyword, retry on failure, FastAPI
import asyncio  # asyncio
from fastapi import FastAPI, HTTPException  # web
from fastapi.testclient import TestClient  # test
from pydantic import BaseModel  # body
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake
from autogen_agentchat.agents import AssistantAgent  # agent
from autogen_agentchat.teams import RoundRobinGroupChat  # team
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination  # stops

app = FastAPI()  # app

class Req(BaseModel):  # body
    product: str  # product text

async def review_loop(product: str, retries: int = 2) -> dict[str, object]:  # core logic
    last: Exception | None = None  # remember error
    for attempt in range(retries + 1):  # retry whole team on transient errors
        writer = AssistantAgent("writer", ReplayChatCompletionClient([f"HS guess for {product}: 6403", "HS 6403.99"]))  # fake writer
        reviewer = AssistantAgent("reviewer", ReplayChatCompletionClient(["add subheading", "APPROVE"]))  # fake reviewer
        team = RoundRobinGroupChat([writer, reviewer], termination_condition=TextMentionTermination("APPROVE") | MaxMessageTermination(8))  # stop on approval or cap
        try:  # run guarded
            res = await asyncio.wait_for(team.run(task=product), timeout=60)  # hard timeout
            return {"final": [m.content for m in res.messages if m.source == "writer"][-1], "turns": len(res.messages), "stop": res.stop_reason}  # last writer draft
        except Exception as e:  # catch
            last = e  # keep
    raise HTTPException(502, f"review loop failed: {last}")  # give up

@app.post("/classify")  # endpoint
async def classify(req: Req) -> dict[str, object]:  # handler
    return await review_loop(req.product)  # delegate

print(TestClient(app).post("/classify", json={"product": "leather shoes"}).json())  # try
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---|---|---|---|---|
| Fixed order | Linear edges / loop | Sequential process | Agent chain / handoff | RoundRobinGroupChat |
| Who speaks next | Edges decide | Process decides | Handoff / manager agent | List order |
| Extra LLM call to route | No | No (sequential) | No | No |
| Loop until approved | Conditional edge | Task retry/guardrail | Loop in your code | TextMentionTermination('APPROVE') |
| Parallelism | Parallel branches | Async tasks | Parallel tool calls | None: one speaker at a time |
| Best for | Complex flows | Role pipelines | Handoffs | Simple draft/review cycles |

---

## ⚠️ Common Mistakes
❌ Mistake: Putting agents in the wrong order.
✅ Correct: List order is speaking order; put the producer first and the reviewer second.

❌ Mistake: Expecting the reviewer to stop the loop without a rule.
✅ Correct: Add a TextMentionTermination('APPROVE') and instruct the reviewer to say exactly that word.

❌ Mistake: Using round robin when only one specialist is needed per turn.
✅ Correct: Use SelectorGroupChat (149) or Swarm (151) so irrelevant agents do not speak.

❌ Mistake: Counting messages wrong in MaxMessageTermination.
✅ Correct: The initial task message counts. `MaxMessageTermination(5)` gave user + 4 turns.

---

## 🧠 Tricky Interview Question
In your round-robin team the reviewer keeps approving bad drafts and the loop ends after one round. How do you make review meaningful?

Answer: The reviewer is an LLM with the same context and it tends to agree. Give it explicit rejection criteria in the system message (checklist: HS code format, chapter exists, evidence cited), make approval require a structured pattern (for example 'APPROVE' only when all criteria pass), add a deterministic validator agent (regex or lookup, zero tokens) before the LLM reviewer, and use a different or stronger model for review. Measure approval rate on a labelled set.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] In what order do agents speak?
A1: In the order of the participants list, cycling back to the first after the last.

Q2: [Medium] Does RoundRobinGroupChat call an LLM to choose the speaker?
A2: No. That is why it is cheaper than SelectorGroupChat.

Q3: [Hard] How do you end a draft/review loop early?
A3: `TextMentionTermination('APPROVE') | MaxMessageTermination(n)`.

Q4: [Hard] How do you handle transient failures?
A4: Wrap `team.run` in try/except with retries and `asyncio.wait_for`; rebuild the team per attempt because a failed run leaves state behind.

Q5: [System Design] Design a content pipeline with writer, fact-checker, editor.
A5: Round robin writer -> fact-checker (tool agent) -> editor; terminate on 'PUBLISH' or 9 messages; persist state per document; human approval before publishing.

---

## 💰 Cost Impact
No router tokens. Cost per turn is `history_tokens * in_price + reply_tokens * out_price`, so a loop of N turns costs about the sum of growing histories (roughly quadratic in N). Cap N, keep replies short and use a cheaper model for the critic. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Draft/review/revise cycles.
- Fixed small teams (2-4 agents).
- You want determinism and low cost.

❌ Avoid when:
- Specialists should speak only when relevant.
- Branching logic or parallel work.
- Large teams (each agent would speak even when useless).

---

## 📊 Visual Diagram
```
 user task
    |
    v
 [classifier] --> [critic] --> [classifier] --> [critic] --> ...
      ^                                                    |
      +---------------- wraps around ----------------------+
 stop when: 'APPROVE' seen OR max messages reached
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|---|---|---|
| Round robin | Fixed cyclic turn order | तय चक्रीय क्रम |
| participants | Agents in the team | team के agents |
| broadcast | Message seen by all agents | सब agents को दिखने वाला message |
| MaxMessageTermination | Stop after N messages | N messages बाद रुकना |
| TextMentionTermination | Stop on a keyword | keyword दिखने पर रुकना |
| critic | Agent that reviews | जाँच करने वाला agent |
| determinism | Predictable behaviour | अनुमानित व्यवहार |

---

## ⚡ 3-Line Summary
English: Round robin gives fixed cyclic turns with no routing LLM.
Pair it with a semantic stop (APPROVE) and a hard message cap.
Cheapest team type; poor when only one specialist is relevant.
Hindi: Round robin बिना routing LLM के तय चक्रीय turns देता है।
इसे semantic stop (APPROVE) और hard message cap के साथ जोड़ें।
सबसे सस्ती team; जब सिर्फ़ एक specialist प्रासंगिक हो तब कमज़ोर।

---

## ➡️ Next Topic
149. SelectorGroupChat -- an LLM (or your function) picks the next speaker.

---
