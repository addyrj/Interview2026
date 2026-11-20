---

# 55. stream_events()
# हिंदी में: stream_events() (iterator की पूरी जानकारी)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with a scripted model. Verified: the iterator ends by itself, `final_output`/`is_complete`/`current_turn`/`to_input_list()` after draining, guardrail and max-turns exceptions raised during iteration, and `cancel(mode='after_turn')` behaviour (the run completed with `final_output = None` in my test).

---

## 🔵 Simple Definition (2-3 lines)
`RunResultStreaming.stream_events()` is an async iterator that yields every event of a run in order: raw model events, SDK-level run items and agent switches. When it ends, the run is finished and the result object (final output, usage, history) is filled in. It is also where exceptions of the run are raised.

## 🔵 सरल परिभाषा (Hindi)
`RunResultStreaming.stream_events()` एक async iterator है जो run के हर event को क्रम से देता है: raw model events, SDK-level run items और agent switches। यह ख़त्म होने पर run पूरा हो चुका होता है और result object (final output, usage, history) भर जाता है। Run के exceptions भी यहीं उठते हैं।

---

## 🔴 Problem it Solves
With streaming you no longer get a single result or exception from one await. You need to know when it is safe to read the final output, where errors appear, how to stop a run midway and how to continue a conversation from a streamed run. `stream_events()` is the contract for all of that.

## 🔴 यह क्यों बना? (Hindi)
Streaming में आपको एक await से एक ही result या exception नहीं मिलता। आपको जानना होता है कि final output कब पढ़ना सुरक्षित है, errors कहाँ दिखते हैं, run को बीच में कैसे रोकें और streamed run से बातचीत आगे कैसे बढ़ाएँ। `stream_events()` इन सबका अनुबंध है।

---

## 🟢 How it Works

```
Step 1 -> result = Runner.run_streamed(...)  (run starts in background)
Step 2 -> async for ev in result.stream_events():  (consume ALL)
Step 3 -> each ev has ev.type:
          raw_response_event | run_item_stream_event |
          agent_updated_stream_event
Step 4 -> Exceptions are raised from the loop:
          MaxTurnsExceeded, guardrail tripwires, model errors
Step 5 -> Loop ends -> result.is_complete == True
          final_output, last_agent, current_turn, usage ready
Step 6 -> result.to_input_list() -> history for the next turn
          result.cancel(mode) to stop early (keep draining)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> result = Runner.run_streamed(...)  (run background में शुरू)
Step 2 -> async for ev in result.stream_events():  (सब consume करो)
Step 3 -> हर ev का ev.type:
          raw_response_event | run_item_stream_event |
          agent_updated_stream_event
Step 4 -> Exceptions loop से उठते हैं:
          MaxTurnsExceeded, guardrail tripwires, model errors
Step 5 -> Loop खत्म -> result.is_complete == True
          final_output, last_agent, current_turn, usage तैयार
Step 6 -> result.to_input_list() -> अगले turn की history
          जल्दी रोकने के लिए result.cancel(mode) (drain जारी रखो)
```

**Verified in 0.24.0:** `stream_events() -> AsyncIterator[StreamEvent]`; its docstring says it raises `MaxTurnsExceeded` and guardrail tripwire exceptions. `cancel(mode: 'immediate' | 'after_turn' = 'immediate')`: `immediate` cancels tasks and clears queues; `after_turn` lets the current model response and pending tool calls finish, then stops before the next turn. The docstring tells you to keep consuming events after calling `cancel()`.

**Attributes seen after a two-turn run:** `is_complete=True`, `current_turn=2`, `last_agent.name`, `to_input_list()` (4 items: user message, tool call, tool output, assistant message), `context_wrapper.usage.requests == 2`. Other public attributes include `last_response_id`, `final_output_as(...)`, `to_state()` and `run_loop_exception`.

**Observation:** in my cancel test (cancelled right after the first `tool_called`) the run ended complete with `final_output=None`, so always handle a `None` output when you cancel.

**Hindi नोट:** तीन नियम: (1) loop पूरा drain करो, (2) exceptions को loop के चारों ओर try/except से पकड़ो, (3) cancel के बाद भी loop चलने दो।

---

## 🟡 Real World Example
**Tariff Agent.** A support console streams the agent. When a manager clicks 'Stop', the server calls `result.cancel(mode='after_turn')` so the tool call that already started finishes and its audit entry is saved, then the run stops. The input guardrail for secrets is raised from the same loop and shown as a polite refusal.

**Customer Support Agent:** after the stream ends, `to_input_list()` is stored as the conversation history.

## 🟡 Real Example Hindi mein
**Tariff Agent.** Support console agent को stream करता है। Manager 'Stop' दबाता है तो server `result.cancel(mode='after_turn')` बुलाता है ताकि शुरू हो चुका tool call पूरा हो और उसकी audit entry सुरक्षित हो, फिर run रुकता है। Secrets वाला input guardrail उसी loop से उठता है और विनम्र refusal के रूप में दिखता है।

**Customer Support Agent:** stream खत्म होने पर `to_input_list()` को बातचीत के history के रूप में सहेजा जाता है।

---

## 💻 Code Example — Basic
Runs offline. Collects the event types, then prints what is available after the stream is drained (final output, turn count, history length, usage requests).

```python
# Basic: everything stream_events() gives you, and what is available after it finishes (offline)
import asyncio                                           # async runner
from agents import Agent, Runner, function_tool         # SDK
from agents.testing import ScriptedModel, assistant_message, function_call  # fake LLM

@function_tool
def hs_duty(code: str) -> str:
    """Duty percent for an HS code."""
    return "20%"

async def main() -> None:
    model = ScriptedModel([[function_call("hs_duty", {"code": "6109.10"}, call_id="c1")],
                           [assistant_message("Duty is 20%.")]])
    agent = Agent(name="Tariff Agent", instructions="x", model=model, tools=[hs_duty])
    result = Runner.run_streamed(agent, "Duty?")
    types: list[str] = []
    async for ev in result.stream_events():              # an async iterator; ends when the run is over
        types.append(ev.type)
    print("distinct event types:", sorted(set(types)))
    print("count:", len(types))
    print("final_output:", result.final_output)          # set after the stream is drained
    print("is_complete:", result.is_complete, "| turns:", result.current_turn)
    print("last_agent:", result.last_agent.name)
    print("input list items:", len(result.to_input_list()))   # replayable history for the next turn
    print("usage requests:", result.context_wrapper.usage.requests)

asyncio.run(main())
```

## 💻 Code Example — Advanced
Four behaviours in one script: a guardrail tripwire raised from the iterator, `MaxTurnsExceeded` raised from the iterator, `cancel(mode='after_turn')`, and an `asyncio.wait_for` timeout around consumption. Offline.

```python
# Advanced: cancel() modes, guardrail/max-turn exceptions surfaced by stream_events(), timeouts (offline)
import asyncio                                           # timeouts
from agents import (Agent, Runner, function_tool, GuardrailFunctionOutput, input_guardrail,
                    InputGuardrailTripwireTriggered, MaxTurnsExceeded)  # SDK
from agents.testing import ScriptedModel, assistant_message, function_call  # fake LLM

@function_tool
def hs_duty(code: str) -> str:
    """Duty percent for an HS code."""
    return "20%"

@input_guardrail(run_in_parallel=False)
async def no_secrets(ctx, agent, user_input):            # trips on a forbidden word
    return GuardrailFunctionOutput(output_info=None, tripwire_triggered="secret" in str(user_input))

def agent_with(steps, **kw) -> Agent:
    return Agent(name="Tariff Agent", instructions="x", model=ScriptedModel(steps), tools=[hs_duty], **kw)

async def consume(result) -> list[str]:
    seen: list[str] = []
    async for ev in result.stream_events():
        seen.append(ev.name if ev.type == "run_item_stream_event" else ev.type)
    return seen

async def main() -> None:
    steps = lambda: [[function_call("hs_duty", {"code": "1"}, call_id="1")], [assistant_message("done")]]
    # 1) guardrail tripwire is raised FROM the stream iteration
    try:
        await consume(Runner.run_streamed(agent_with(steps(), input_guardrails=[no_secrets]), "my secret"))
    except InputGuardrailTripwireTriggered:
        print("1) tripwire raised while streaming")
    # 2) max_turns exceeded is raised from the stream iteration
    loop = [[function_call("hs_duty", {"code": "1"}, call_id=str(i))] for i in range(5)]
    try:
        await consume(Runner.run_streamed(agent_with(loop), "q", max_turns=2))
    except MaxTurnsExceeded:
        print("2) MaxTurnsExceeded raised while streaming")
    # 3) cancel after the first tool_called event; keep draining so cleanup completes
    r = Runner.run_streamed(agent_with(steps()), "q")
    seen = []
    async for ev in r.stream_events():
        seen.append(ev.type)
        if ev.type == "run_item_stream_event" and ev.name == "tool_called":
            r.cancel(mode="after_turn")                  # finish the current turn gracefully; 'immediate' stops at once
    print("3) cancelled run: is_complete =", r.is_complete, "| final_output =", r.final_output)
    # 4) wall-clock timeout around the whole consumption
    try:
        await asyncio.wait_for(consume(Runner.run_streamed(agent_with(steps()), "q")), timeout=5)
        print("4) finished inside the timeout")
    except asyncio.TimeoutError:
        print("4) timed out")

asyncio.run(main())
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Event iterator | `astream` / `astream_events` | Not a first-class event iterator | `result.stream_events()` | `run_stream()` async generator |
| Final result after stream | Last chunk / state | Crew output | `final_output`, `to_input_list()` | `TaskResult` as the last item |
| Early stop | Cancel the task | Limited | `cancel('immediate'|'after_turn')` | `CancellationToken` |
| Errors | Raised in iteration | Raised from kickoff | Raised in iteration | Raised in iteration |
| History for next turn | Checkpointer/state | Memory | `to_input_list()` / sessions | Team/agent state save |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Breaking out of the `async for` early without cancelling.
✅ Correct: Call `result.cancel()` first; otherwise the background run continues.

❌ Mistake 2: Stopping to read events after `cancel()`.
✅ Correct: Keep draining so cleanup completes (docstring guidance).

❌ Mistake 3: Not wrapping iteration in try/except.
✅ Correct: Guardrail and max-turn errors are raised from the loop.

❌ Mistake 4: Assuming `final_output` is non-None after cancel.
✅ Correct: Check for `None` and show a 'stopped' message.

❌ Mistake 5: Using `immediate` cancel when a tool is mid-write.
✅ Correct: Use `after_turn` so pending tool calls finish and state is saved.

---

## 🧠 Tricky Interview Question
A user clicks Stop in your chat while the agent is in the middle of a database-writing tool. After `result.cancel()` the DB has a half-applied change. How should this have been designed?

**Answer:** `cancel()` defaults to `immediate`, which cancels running tasks, so a tool in the middle of a write can be interrupted. Design for it: (1) use `cancel(mode='after_turn')` so already-requested tool calls complete before the run stops; (2) make writing tools idempotent and transactional (single transaction, commit or rollback, idempotency keys) so a cancelled or retried call cannot half-apply; (3) split risky writes behind `needs_approval` and an explicit user confirmation rather than being cancelable mid-way; (4) record intent first (outbox) and apply in a worker; (5) log the cancellation reason in traces; (6) keep draining the iterator so SDK cleanup runs. Test by cancelling at each event in an integration test.

---

## ⚫ Interview Questions + Answers

**Q1:** What does `stream_events()` return and when does it end?

**A1:** An async iterator of events (raw, run item, agent updated). It ends when the run is finished, after which `is_complete` is True.

**Q2:** Where are run exceptions raised when streaming?

**A2:** During iteration of `stream_events()`; wrap the loop in try/except.

**Q3:** `cancel('immediate')` vs `cancel('after_turn')`?

**A3:** Immediate cancels tasks and clears queues; after_turn lets the current response and pending tool calls finish, saves state and stops before the next turn.

**Q4:** How do you continue a conversation after a streamed run?

**A4:** Call `result.to_input_list()` and append the next user message, or use a session.

**Q5:** Design a stoppable long-running research agent.

**A5:** Stream to a websocket, keep a run id, store cancel requests in Redis, call `cancel('after_turn')` on request, persist `to_input_list()`/state so it can be resumed, make tools idempotent, show partial results, set a hard timeout with `asyncio.wait_for`, and emit audit events.

---

## 💰 Cost Impact
Iterating events costs nothing extra; the model cost is the same as `run`. The savings come from stopping early: cancelling avoids further turns (each re-sends history) and unread output tokens. Timeouts and `max_turns` bound the worst case. Approximate relationship only: cancelled_cost = tokens of turns completed; measure with `context_wrapper.usage` (counts only completed model calls, so check how your provider bills partially streamed responses).

---

## 🔷 When to Use
✅ Use when:
- You need ordered events and exceptions in one place
- Cancel/stop buttons, timeouts
- Continuing conversations from `to_input_list()`

❌ Avoid when:
- Fire-and-forget runs with no consumer (use `Runner.run`)
- Breaking out of the loop without cancelling

---

## 📊 Visual Diagram
```
  Runner.run_streamed()  --> background run loop (turns 1..N)
                                  |
                          internal event queue
                                  |
  async for ev in stream_events() <+  (you drain it)
        |            |            |
        |  exceptions raised here (MaxTurns / tripwire / model error)
        |
        +--> loop ends --> is_complete=True
                           final_output, last_agent, current_turn
                           to_input_list(), context_wrapper.usage

  cancel("immediate") -> stop now        cancel("after_turn") -> finish turn, then stop
  (keep draining after cancel)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| stream_events() | Async iterator over run events | run events का async iterator |
| is_complete | True when the run has finished | run खत्म होने पर True |
| cancel(mode) | Stop a streaming run early | streaming run को जल्दी रोकना |
| to_input_list() | History to feed the next run | अगले run को देने वाला history |
| Drain | Consume all remaining events | बचे सारे events consume करना |

---

## ⚡ 3-Line Summary
English: `stream_events()` yields every event in order and raises run exceptions while you iterate.
When it ends, the result (final output, history, usage) is ready.
Cancel with `after_turn` for safe stops and keep draining after cancelling.

Hindi: `stream_events()` हर event क्रम से देता है और iterate करते समय run के exceptions उठाता है।
खत्म होने पर result (final output, history, usage) तैयार होता है।
सुरक्षित stop के लिए `after_turn` से cancel करें और cancel के बाद भी drain करते रहें।

---

## ➡️ Next Topic
**#56 Event Types in Stream** - the three event families and their names (`tool_called`, `handoff_occured`, raw deltas) and how to route them to a UI.

---
