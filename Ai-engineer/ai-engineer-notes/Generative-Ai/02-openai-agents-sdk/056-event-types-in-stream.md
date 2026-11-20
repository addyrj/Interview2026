---

# 56. Event Types in Stream
# हिंदी में: Stream में Event Types (तीन परिवार)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with scripted models, including a real handoff between two agents and a tool call. The exact event order and names printed below come from that run. Raw event details for a real provider (many small deltas, reasoning events) were not observed.

---

## 🔵 Simple Definition (2-3 lines)
The stream contains three event families: `raw_response_event` (events passed straight from the model provider, such as text deltas), `run_item_stream_event` (SDK-level items with a `name` like `tool_called`, `tool_output`, `message_output_created`, `handoff_requested`) and `agent_updated_stream_event` (the active agent changed).

## 🔵 सरल परिभाषा (Hindi)
Stream में तीन event परिवार होते हैं: `raw_response_event` (model provider से सीधे आए events, जैसे text deltas), `run_item_stream_event` (SDK-level items जिनका `name` होता है, जैसे `tool_called`, `tool_output`, `message_output_created`, `handoff_requested`) और `agent_updated_stream_event` (active agent बदल गया)।

---

## 🔴 Problem it Solves
If you forward everything, the UI gets noise (about 23 raw events for a tiny two-agent run) and breaks when the SDK adds new event kinds. If you forward too little you cannot show tool progress or handoffs. You must know the families and route each one deliberately.

## 🔴 यह क्यों बना? (Hindi)
अगर आप सब कुछ forward करेंगे तो UI को शोर मिलेगा (एक छोटे दो-agent run में लगभग 23 raw events) और SDK में नए event kinds आने पर वह टूट सकता है। बहुत कम forward करेंगे तो tool progress या handoffs नहीं दिखा पाएँगे। आपको परिवार जानकर हर एक को सोच-समझकर route करना होगा।

---

## 🟢 How it Works

```
Observed order for triage -> handoff -> tool -> answer:
 1 agent_updated_stream_event  (Triage starts)
 2 raw_response_event x N      (model streaming)
 3 run_item_stream_event  handoff_requested
 4 run_item_stream_event  handoff_occured   (SDK spelling!)
 5 agent_updated_stream_event  (Duty Specialist)
 6 raw_response_event x N
 7 run_item_stream_event  tool_called
 8 run_item_stream_event  tool_output
 9 raw_response_event x N  (text delta: the answer)
10 run_item_stream_event  message_output_created
```

## 🟢 कैसे काम करता है? (Hindi)

```
Triage -> handoff -> tool -> answer का देखा गया क्रम:
 1 agent_updated_stream_event  (Triage शुरू)
 2 raw_response_event x N      (model streaming)
 3 run_item_stream_event  handoff_requested
 4 run_item_stream_event  handoff_occured   (SDK की spelling!)
 5 agent_updated_stream_event  (Duty Specialist)
 6 raw_response_event x N
 7 run_item_stream_event  tool_called
 8 run_item_stream_event  tool_output
 9 raw_response_event x N  (text delta: जवाब)
10 run_item_stream_event  message_output_created
```

**Event names verified in 0.24.0** (`RunItemStreamEvent.name` Literal): `message_output_created`, `handoff_requested`, `handoff_occured` (misspelled in the SDK; the source says it cannot be changed), `tool_called`, `tool_search_called`, `tool_search_output_created`, `tool_output`, `reasoning_item_created`, `mcp_approval_requested`, `mcp_approval_response`, `mcp_list_tools`.

**Fields:** `RunItemStreamEvent.item` is a run item (`item.type` e.g. `tool_call_item`, `tool_call_output_item`, `handoff_call_item`, `handoff_output_item`, `message_output_item`) with the provider object in `item.raw_item`. `AgentUpdatedStreamEvent.new_agent` is the agent. `RawResponsesStreamEvent.data` is the provider event; the text one is `ResponseTextDeltaEvent` with `.delta`.

**Forward-compat rule:** the `name` list grows between versions (it already includes MCP and tool-search names). Route known names and silently ignore the rest; do not raise on unknown ones.

**Raw event counts:** in our runs 23 raw events vs 5 item events for the handoff + tool run, so raw events are the high-volume family.

**Hindi नोट:** `handoff_occured` की spelling गलत है, पर code में वही लिखनी है। Interview में यह छोटी बात आपको practical अनुभव वाला दिखाती है।

---

## 🟡 Real World Example
**Tariff Agent UI.** Triage routes to the Duty Specialist. The UI shows 'Transferred to Duty Specialist' on `agent_updated_stream_event`, a spinner 'Checking tariff table' on `tool_called`, the tool result (truncated) on `tool_output`, and streams the answer from text deltas only. All other raw events are dropped.

**Code Agent:** show each shell command from `tool_called` in a log panel.

## 🟡 Real Example Hindi mein
**Tariff Agent UI.** Triage, Duty Specialist को route करता है। UI `agent_updated_stream_event` पर 'Duty Specialist को transfer हुआ' दिखाता है, `tool_called` पर 'Tariff table जाँच रहा हूँ' spinner, `tool_output` पर (छोटा किया हुआ) tool result, और जवाब सिर्फ़ text deltas से stream करता है। बाकी सभी raw events छोड़ दिए जाते हैं।

**Code Agent:** हर shell command को `tool_called` से log panel में दिखाओ।

---

## 💻 Code Example — Basic
Runs offline. A triage agent hands off to a specialist that calls a tool; the script prints the item and agent events and counts the raw ones.

```python
# Basic: the three event families, printed in order (offline, tool + handoff)
import asyncio                                           # async runner
from agents import Agent, Runner, function_tool          # SDK
from agents.testing import ScriptedModel, assistant_message, function_call  # fake LLM

@function_tool
def hs_duty(code: str) -> str:
    """Duty percent for an HS code."""
    return "20%"

async def main() -> None:
    specialist = Agent(name="Duty Specialist", instructions="x", model=ScriptedModel([
        [function_call("hs_duty", {"code": "6109.10"}, call_id="t1")], [assistant_message("Duty is 20%.")]]), tools=[hs_duty])
    triage = Agent(name="Triage", instructions="Route.", handoffs=[specialist], model=ScriptedModel([
        [function_call("transfer_to_duty_specialist", {}, call_id="h1")]]))   # handoffs are exposed to the LLM as tools
    result = Runner.run_streamed(triage, "Duty on t-shirts?")
    raw = 0
    async for ev in result.stream_events():
        if ev.type == "raw_response_event":              # family 1: provider events (many)
            raw += 1
        elif ev.type == "run_item_stream_event":         # family 2: SDK-level items (few, meaningful)
            print("item  :", ev.name, "->", ev.item.type)
        elif ev.type == "agent_updated_stream_event":    # family 3: active agent changed
            print("agent :", ev.new_agent.name)
    print("raw events:", raw, "| final:", result.final_output)

asyncio.run(main())
```

## 💻 Code Example — Advanced
A typed router that maps SDK events to compact JSON lines for a UI (text, tool start/end, agent, handoff), ignores unknown events, truncates tool output, and reports event counts. FastAPI, offline.

```python
# Advanced: typed event router -> JSON lines for a UI (tool progress, handoffs, text), with allow-listed raw events (offline)
import asyncio                                           # runner
import json                                              # UI payloads
from collections import Counter                          # stats
from typing import Any, AsyncIterator                    # types
from fastapi import FastAPI                              # web
from fastapi.responses import StreamingResponse          # streaming body
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel                           # schema
from openai.types.responses import ResponseTextDeltaEvent  # the only raw event we forward
from agents import Agent, Runner, function_tool, StreamEvent  # SDK
from agents.testing import ScriptedModel, assistant_message, function_call  # fake LLM

@function_tool
def hs_duty(code: str) -> str:
    """Duty percent for an HS code."""
    return "20%"

def route(ev: StreamEvent) -> dict[str, Any] | None:     # one place that maps SDK events -> UI messages
    if ev.type == "raw_response_event":
        if isinstance(ev.data, ResponseTextDeltaEvent):  # ignore the ~15 other raw event kinds
            return {"kind": "text", "delta": ev.data.delta}
        return None
    if ev.type == "agent_updated_stream_event":
        return {"kind": "agent", "name": ev.new_agent.name}
    if ev.type == "run_item_stream_event":
        raw = ev.item.raw_item
        if ev.name == "tool_called":
            return {"kind": "tool_start", "tool": getattr(raw, "name", "?"), "args": getattr(raw, "arguments", "")}
        if ev.name == "tool_output":
            out = raw.get("output") if isinstance(raw, dict) else getattr(raw, "output", "")   # dict for function outputs
            return {"kind": "tool_end", "output": str(out)[:200]}   # truncate before sending to the browser
        if ev.name in ("handoff_requested", "handoff_occured"):      # note the SDK's spelling: 'occured'
            return {"kind": ev.name}
    return None                                          # unknown/new event names are ignored, not fatal (SDK adds new ones)

def make_agents() -> Agent:
    spec = Agent(name="Duty Specialist", instructions="x", tools=[hs_duty], model=ScriptedModel([
        [function_call("hs_duty", {"code": "6109.10"}, call_id="t1")], [assistant_message("Duty is 20%.")]]))
    return Agent(name="Triage", instructions="Route.", handoffs=[spec], model=ScriptedModel([
        [function_call("transfer_to_duty_specialist", {}, call_id="h1")]]))

app = FastAPI()

class Ask(BaseModel):
    question: str

@app.post("/events")
async def events(b: Ask) -> StreamingResponse:
    result = Runner.run_streamed(make_agents(), b.question, max_turns=5)
    async def gen() -> AsyncIterator[str]:
        stats: Counter = Counter()
        async for ev in result.stream_events():
            stats[ev.type] += 1
            msg = route(ev)
            if msg:
                yield json.dumps(msg) + "\n"
        yield json.dumps({"kind": "done", "final": result.final_output, "event_counts": dict(stats)}) + "\n"
    return StreamingResponse(gen(), media_type="application/x-ndjson")

if __name__ == "__main__":
    print(TestClient(app).post("/events", json={"question": "Duty on t-shirts?"}).text)
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Raw model events | `astream_events` (v2) raw model events | Not exposed | `raw_response_event` | `ModelClientStreamingChunkEvent` |
| Tool call event | `on_tool_start`/`on_tool_end` events | Step callback | `run_item_stream_event` (`tool_called`, `tool_output`) | `ToolCallRequestEvent`, `ToolCallExecutionEvent` |
| Handoff/agent switch | Node/edge change events | Task change | `handoff_requested`, `handoff_occured`, `agent_updated_stream_event` | `HandoffMessage` |
| Final message | Last chain event | Crew output | `message_output_created` | `TextMessage` / `TaskResult` |
| New event kinds over time | Yes | Yes | Yes (ignore unknown names) | Yes |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Printing every raw event to the UI.
✅ Correct: Allow-list: text deltas only, plus the item/agent events you display.

❌ Mistake 2: Raising an error on an unknown `name`.
✅ Correct: Ignore unknown names; new ones are added across SDK versions.

❌ Mistake 3: Spelling the handoff event `handoff_occurred`.
✅ Correct: The SDK name is `handoff_occured` (single r); a typo means a silent mismatch.

❌ Mistake 4: Sending full tool outputs to the browser.
✅ Correct: Truncate and redact before forwarding.

❌ Mistake 5: Using `run_item_stream_event` for token streaming.
✅ Correct: Items arrive per completed item; use raw `ResponseTextDeltaEvent` for tokens.

---

## 🧠 Tricky Interview Question
After an SDK upgrade your UI's progress panel silently stops showing handoffs, although nothing crashed. What probably happened and how do you make the system robust?

**Answer:** Most likely a name or shape changed or a new event kind was added and your router only handled the old ones (for example a typo-sensitive string such as `handoff_occured`, or code that assumed `raw_item` is an object when some items expose a dict, as we saw for tool outputs). Because the router returns None for unknown events, the UI just shows nothing. Make it robust: pin the SDK version and upgrade deliberately; keep a golden-event contract test that runs a scripted handoff + tool run and asserts the sequence of `(type, name)`; handle both dict and object `raw_item`s; log counts of unhandled event names as a metric and alert when the unhandled share changes; and feature-flag the UI panels so one change cannot blank the whole screen. This is precisely why a scripted model is valuable: the test runs without an API key.

---

## ⚫ Interview Questions + Answers

**Q1:** What are the three stream event types?

**A1:** `raw_response_event`, `run_item_stream_event`, `agent_updated_stream_event`.

**Q2:** Which event signals a tool started and finished?

**A2:** `run_item_stream_event` with name `tool_called` and then `tool_output`.

**Q3:** How do you stream tokens to the UI?

**A3:** Filter `raw_response_event` whose `data` is a `ResponseTextDeltaEvent` and forward `.delta`.

**Q4:** Which events show a handoff?

**A4:** `handoff_requested`, `handoff_occured` (SDK spelling) as items, and an `agent_updated_stream_event` with the new agent.

**Q5:** Design the event contract between agent server and a React UI.

**A5:** Define a small versioned JSON schema (text, tool_start, tool_end, agent, handoff, error, done); map SDK events through one router; truncate/redact; ignore unknown; test against golden scripted runs; include run id and sequence numbers for resume; backpressure handling.

---

## 💰 Cost Impact
Events cost no tokens; they expose them. Forwarding fewer events reduces bandwidth and UI work: in my run only about 7 of 30 events (5 item + 2 agent events) were useful to display (counts from the scripted run, not a benchmark). Show tool progress to reduce user retries (each retry is a new paid run). Use `message_output_created` and `context_wrapper.usage` for per-run cost logging.

---

## 🔷 When to Use
✅ Use when:
- Rich UIs with progress and handoff indicators
- Auditing tool calls live
- Debug consoles and trace viewers

❌ Avoid when:
- Forwarding raw events untouched to clients
- Relying on exact event order across SDK versions without tests

---

## 📊 Visual Diagram
```
  stream_events()
      |
      +-- raw_response_event ------------- provider events (high volume)
      |        data: ResponseTextDeltaEvent(.delta)  -> tokens to UI
      |
      +-- run_item_stream_event ---------- SDK items (few, meaningful)
      |        name: tool_called | tool_output | message_output_created
      |              handoff_requested | handoff_occured | reasoning_item_created
      |              mcp_* | tool_search_*
      |        item: .type, .raw_item
      |
      +-- agent_updated_stream_event ----- new_agent (after handoff)

  router(ev) -> known? JSON line to UI : ignore (never crash)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| raw_response_event | Event passed through from the provider | provider से सीधे आया event |
| run_item_stream_event | SDK-level event wrapping a run item | run item को लपेटने वाला SDK-level event |
| agent_updated_stream_event | Active agent changed | active agent बदला |
| tool_called / tool_output | Tool start and result events | tool शुरू और result के events |
| handoff_occured | Handoff completed (SDK spelling) | handoff पूरा (SDK की spelling) |

---

## ⚡ 3-Line Summary
English: Streams carry three event families: raw provider events, SDK run-item events with names, and agent-updated events.
Route only what the UI needs, ignore unknown names and keep a golden test for the sequence.
Use text deltas for tokens and item events for progress and handoffs.

Hindi: Streams में तीन event परिवार होते हैं: raw provider events, नाम वाले SDK run-item events और agent-updated events।
सिर्फ़ वही route करें जो UI को चाहिए, अज्ञात नामों को अनदेखा करें और क्रम के लिए golden test रखें।
Tokens के लिए text deltas और progress/handoffs के लिए item events इस्तेमाल करें।

---

## ➡️ Next Topic
**#57 Agents as Tools** - with events and streaming understood, we look at exposing one agent as a tool of another, the building block of orchestrator designs.

---
