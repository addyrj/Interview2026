---

# 57. Agents as Tools
# हिंदी में: Agents को Tools की तरह इस्तेमाल करना (as_tool)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with a scripted model (`fake.py`, full listing in note #57), so no API key was needed. Real model calls were NOT run - they need OPENAI_API_KEY. Token counts printed below come from the fake model (10 in / 5 out per call), not from a real LLM.

---

## 🔵 Simple Definition (2-3 lines)
`agent.as_tool(...)` wraps a whole agent as a normal function tool. The manager agent calls it like any tool, the specialist runs its own loop, and the result goes back to the manager. The manager stays in control of the conversation (unlike a handoff, where control moves).

## 🔵 सरल परिभाषा (Hindi)
`agent.as_tool(...)` एक पूरे agent को साधारण function tool में बदल देता है। Manager agent इसे किसी भी tool की तरह call करता है, specialist अपना loop चलाता है और result वापस manager के पास आता है। बातचीत का control manager के पास ही रहता है (handoff में control बदल जाता है)।

---

## 🔴 Problem it Solves
With only handoffs, the conversation moves to a specialist and the first agent loses control: it cannot combine two specialists' answers, cannot post-process, and cannot call the same specialist twice. Without agents-as-tools you either build one giant agent with 30 tools (confused, expensive prompt) or write manual glue code between agents.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ़ handoff हो तो बातचीत specialist के पास चली जाती है और पहला agent control खो देता है: वह दो specialists के जवाब जोड़ नहीं सकता, result को process नहीं कर सकता, और एक ही specialist को दो बार call नहीं कर सकता। Agents-as-tools के बिना या तो 30 tools वाला एक बड़ा agent बनता है (confused और महँगा prompt) या agents के बीच हाथ से glue code लिखना पड़ता है।

---

## 🟢 How it Works

```
Step 1 -> specialist = Agent(name="RateAgent", tools=[get_tariff_rate])
Step 2 -> tool = specialist.as_tool(tool_name="rate_lookup",
                                    tool_description="Duty by HS code")
Step 3 -> manager = Agent(..., tools=[tool])        # just another tool
Step 4 -> Manager LLM emits  rate_lookup({"input": "..."})
Step 5 -> SDK runs the specialist in a NESTED Runner.run
          (own loop, own tools, own max_turns)
Step 6 -> specialist final_output (a string) -> tool result
Step 7 -> Manager LLM reads it and writes the final answer
          result.last_agent is still Manager (no handoff)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> specialist = Agent(name="RateAgent", tools=[get_tariff_rate])
Step 2 -> tool = specialist.as_tool(tool_name="rate_lookup",
                                    tool_description="HS code से duty")
Step 3 -> manager = Agent(..., tools=[tool])        # बस एक और tool
Step 4 -> Manager LLM  rate_lookup({"input": "..."})  भेजता है
Step 5 -> SDK specialist को NESTED Runner.run में चलाता है
          (अपना loop, अपने tools, अपना max_turns)
Step 6 -> specialist का final_output (string) -> tool result
Step 7 -> Manager LLM उसे पढ़कर final answer लिखता है
          result.last_agent अब भी Manager है (handoff नहीं हुआ)
```

**Verified in 0.24.0:** `Agent.as_tool(tool_name, tool_description, custom_output_extractor=None, is_enabled=True, on_stream=None, run_config=None, max_turns=None, hooks=None, session=None, failure_error_function=..., needs_approval=False, parameters=None, input_builder=None, ...)`. The tool's input schema is `{"input": "<string>"}` by default, which is why the scripted manager calls `rate_lookup` with `{"input": ...}`.

**Handoff vs agent-as-tool:**

| | Handoff | Agent as tool |
|---|---|---|
| Who talks to the user next | the specialist | still the manager |
| Specialist sees | whole conversation history | only the `input` string the manager wrote |
| Can call 2 specialists and merge | no | yes |
| Token cost | history is re-sent to the specialist | small input, but a nested run (extra LLM calls) |

**Hindi नोट:** Interview का सीधा सूत्र: "सारा काम एक specialist को सौंपना हो तो handoff; कई specialists के जवाब मिलाकर खुद जवाब देना हो तो agent-as-tool।" Nested run के tokens भी parent के `usage` में जुड़ते हैं (basic example में 60 = manager 2 calls + specialist 2 calls, हर call fake 15 tokens)।

---

## 🟡 Real World Example
**Tariff Agent.** A `TariffManager` answers 'What is the landed cost of 1000 cotton shirts to India?'. It calls `classify_agent` (product to HS code), then `rate_agent` (HS code to duty) and finally writes one combined answer with the totals. Each specialist has only its own tools, so the manager prompt stays short.

**Customer Support Agent:** the front agent calls `billing_agent` and `shipping_agent` as tools and replies once.

## 🟡 Real Example Hindi mein
**Tariff Agent.** `TariffManager` से पूछा जाता है 'India में 1000 cotton shirts की landed cost क्या है?'। वह पहले `classify_agent` (product से HS code), फिर `rate_agent` (HS code से duty) call करता है और totals के साथ एक combined जवाब लिखता है। हर specialist के पास सिर्फ़ अपने tools हैं, इसलिए manager का prompt छोटा रहता है।

**Customer Support Agent:** front agent `billing_agent` और `shipping_agent` को tools की तरह call करके एक बार में जवाब देता है।

---

## 💻 Code Example — Basic
Runs offline. The manager calls `rate_lookup` (a wrapped agent), which itself calls `get_tariff_rate`. `fake.py` is listed after this block.

```python
# Basic: a Tariff orchestrator that calls a specialist agent as a TOOL (offline, no API key).
# verified against openai-agents 0.24.0
import asyncio                                                    # run async code from a script
from agents import Agent, Runner, function_tool, set_tracing_disabled  # core SDK pieces
from fake import ScriptedModel, tool_call, text                   # offline scripted model (listing above)

set_tracing_disabled(True)                                        # no trace upload (needs an API key otherwise)

@function_tool                                                    # plain Python function -> tool schema
def get_tariff_rate(hs_code: str) -> str:                         # type hints become the JSON schema
    """Duty percent for an HS code."""                            # docstring becomes the tool description
    return {"6109.10": "20%"}.get(hs_code, "unknown")             # fake rate table

# The specialist: its model first calls get_tariff_rate, then answers in text.
rate_model = ScriptedModel([[tool_call("get_tariff_rate", '{"hs_code":"6109.10"}')], [text("Duty is 20%")]])
rate_agent = Agent(name="RateAgent", instructions="Look up duty.", tools=[get_tariff_rate], model=rate_model)

# The manager: its model calls the tool "rate_lookup", then writes the final answer itself.
mgr_model = ScriptedModel([[tool_call("rate_lookup", '{"input":"cotton shirt 6109.10"}')], [text("Final: 20% duty")]])
manager = Agent(
    name="Manager", instructions="Answer the user. Use rate_lookup for duty questions.", model=mgr_model,
    tools=[rate_agent.as_tool(tool_name="rate_lookup", tool_description="Find duty rate for a product")],
)

result = asyncio.run(Runner.run(manager, "Duty on cotton shirts?"))   # manager stays in control the whole time
print(result.final_output)                                        # Final: 20% duty
print(result.last_agent.name)                                     # Manager (no handoff happened)
print(result.context_wrapper.usage.total_tokens)                  # usage of manager + nested agent runs (fake numbers here)
```

**`fake.py` (shared by notes #57-#70)** - a tiny scripted model so everything runs without an API key. In production you pass `model="<your model name>"` instead. (The SDK also ships `agents.testing.ScriptedModel`; we use our own file because it lets us record `seen_settings` and stream words.)

```python
# Scripted offline model: replays pre-written steps, no API key needed.
import itertools
from typing import Any
from openai.types.responses import (Response, ResponseCompletedEvent, ResponseFunctionToolCall,
                                    ResponseOutputMessage, ResponseOutputText, ResponseTextDeltaEvent)
from agents import Model, ModelResponse, Usage

_ids = itertools.count(1)

def tool_call(name: str, args: str) -> ResponseFunctionToolCall:
    n = next(_ids)
    return ResponseFunctionToolCall(type="function_call", call_id=f"call_{n}", name=name, arguments=args)

def text(msg: str) -> ResponseOutputMessage:
    n = next(_ids)
    return ResponseOutputMessage(id=f"msg_{n}", type="message", role="assistant", status="completed",
        content=[ResponseOutputText(type="output_text", text=msg, annotations=[])])

class ScriptedModel(Model):
    def __init__(self, steps: list[list[Any]]) -> None:
        self.steps = list(steps); self.calls = 0; self.seen_settings = []
    async def get_response(self, system_instructions, input, model_settings, tools, output_schema,
                           handoffs, tracing, *, previous_response_id=None, conversation_id=None, prompt=None):
        self.seen_settings.append(model_settings)
        items = self.steps[min(self.calls, len(self.steps) - 1)]; self.calls += 1
        return ModelResponse(output=items, usage=Usage(requests=1, input_tokens=10, output_tokens=5, total_tokens=15), response_id=None)
    async def stream_response(self, system_instructions, input, model_settings, tools, output_schema,
                              handoffs, tracing, **kw):
        # Streams the FIRST scripted message word by word, then a completed event (text-only scripts).
        msg = self.steps[0][0]; self.calls += 1
        words = msg.content[0].text.split(" ")
        for i, w in enumerate(words):                             # one delta event per word
            yield ResponseTextDeltaEvent(type="response.output_text.delta", item_id=msg.id, output_index=0,
                                         content_index=0, delta=w + (" " if i < len(words) - 1 else ""),
                                         sequence_number=i, logprobs=[])
        resp = Response(id="r1", created_at=0, model="fake", object="response", output=[msg],
                        parallel_tool_calls=False, tool_choice="auto", tools=[])
        yield ResponseCompletedEvent(type="response.completed", response=resp, sequence_number=999)
```

Expected output of the basic sample: `Final: 20% duty`, `Manager`, `60`.

## 💻 Code Example — Advanced
FastAPI endpoint. Shows `custom_output_extractor` (trim what the manager sees), `max_turns` and `failure_error_function` for the nested run, and `is_enabled` to hide the legal tool unless the request context allows it. Output: `{'answer': 'Duty is 20%.', 'total_tokens': 60}`.

```python
# Advanced: agent-as-tool inside FastAPI, with output extractor, error function and conditional enabling.
# verified against openai-agents 0.24.0 + fastapi 0.163.0 (TestClient); real model: not run - needs OPENAI_API_KEY
import json                                                       # build JSON strings
from typing import Any                                            # type hints
from fastapi import FastAPI, HTTPException                        # web layer
from pydantic import BaseModel                                    # request/response models
from agents import (Agent, RunContextWrapper, Runner, RunResult, ModelBehaviorError, MaxTurnsExceeded,
                    function_tool, set_tracing_disabled)           # SDK pieces
from fake import ScriptedModel, tool_call, text                   # offline model; remove in production

set_tracing_disabled(True)                                        # remove if you use OpenAI tracing

class Ctx(BaseModel):                                             # per-request context passed to tools
    tenant: str                                                   # who is calling
    allow_legal: bool = False                                     # feature flag used by is_enabled

@function_tool
def get_tariff_rate(hs_code: str) -> str:                         # tool used by the specialist
    """Duty percent for an HS code."""
    return json.dumps({"hs_code": hs_code, "duty": "20%"})        # tools should return strings/JSON

async def only_duty_json(res: RunResult) -> str:                  # custom_output_extractor: shrink what the parent sees
    data = json.loads(res.final_output)                           # the child answered with JSON text
    return f"duty={data['duty']}"                                 # parent only receives a short string (fewer tokens)

def legal_enabled(ctx: RunContextWrapper[Ctx], agent: Any) -> bool:   # is_enabled callable: decided per run
    return ctx.context.allow_legal                                # hide the tool unless the flag is on

def build_manager(rate_model: Any, mgr_model: Any) -> Agent[Ctx]: # factory so tests can inject models
    rate_agent = Agent[Ctx](name="RateAgent", instructions="Return JSON only.", tools=[get_tariff_rate], model=rate_model)
    legal_agent = Agent[Ctx](name="LegalAgent", instructions="Cite customs law.", model=rate_model)
    return Agent[Ctx](
        name="Manager", instructions="Use tools; never guess rates.", model=mgr_model,
        tools=[
            rate_agent.as_tool("rate_lookup", "Duty rate by HS code",
                               custom_output_extractor=only_duty_json,          # trim child output
                               max_turns=4,                                      # cap the child's loop
                               failure_error_function=lambda ctx, err: f"rate service failed: {type(err).__name__}"),
            legal_agent.as_tool("legal_lookup", "Legal citation", is_enabled=legal_enabled),  # conditional tool
        ],
    )

class Ask(BaseModel):                                             # request body
    question: str
    tenant: str = "acme"

class Answer(BaseModel):                                          # response body
    answer: str
    total_tokens: int

app = FastAPI()                                                   # ASGI app

def make_models() -> tuple[ScriptedModel, ScriptedModel]:         # offline stand-ins; production would pass a model name instead
    rate = ScriptedModel([[tool_call("get_tariff_rate", '{"hs_code":"6109.10"}')], [text('{"duty":"20%"}')]])
    mgr = ScriptedModel([[tool_call("rate_lookup", '{"input":"6109.10"}')], [text("Duty is 20%.")]])
    return rate, mgr

@app.post("/ask", response_model=Answer)
async def ask(body: Ask) -> Answer:                               # async endpoint: Runner.run is awaitable
    rate, mgr = make_models()                                     # fresh scripted models per request (test only)
    manager = build_manager(rate, mgr)                            # build the agent graph
    try:
        res = await Runner.run(manager, body.question, context=Ctx(tenant=body.tenant), max_turns=6)
    except MaxTurnsExceeded:                                      # loop guard hit
        raise HTTPException(status_code=504, detail="agent took too many turns")
    except ModelBehaviorError as e:                               # model called a missing tool / bad JSON
        raise HTTPException(status_code=502, detail=f"bad model behaviour: {e}")
    return Answer(answer=str(res.final_output), total_tokens=res.context_wrapper.usage.total_tokens)

if __name__ == "__main__":
    from fastapi.testclient import TestClient                     # in-process HTTP client, no server needed
    print(TestClient(app).post("/ask", json={"question": "Duty on shirts?"}).json())
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Specialist as a callable unit | Subgraph / node calling another graph | Delegation via `allow_delegation` / hierarchical process | `agent.as_tool(...)` | `AgentTool` wrapping an agent (or team handoffs) |
| Manager keeps control | Yes (you wire the edges) | Yes in hierarchical process | Yes (default for as_tool) | Yes with `AgentTool` |
| Control is explicit in code | Yes | Partly (role prompts) | No - the LLM decides which tool | No - LLM decides |
| Trim child output | Node returns what you choose | `output_pydantic` on Task | `custom_output_extractor` | Tool wrapper / result mapping |
| Per-child turn limit | Per-subgraph recursion limit | `max_iter` per agent | `max_turns=` on as_tool | `max_tool_iterations` on agent |

_OpenAI SDK column verified in openai-agents 0.24.0; the other columns are from general knowledge of those libraries (not installed or re-verified here) - check their docs before quoting in an interview._

---

## ⚠️ Common Mistakes
❌ Mistake: Using a handoff when the manager must combine two answers.
✅ Correct: Use `as_tool` so the manager keeps control and can call both specialists.

❌ Mistake: Assuming the specialist sees the chat history.
✅ Correct: It only sees the `input` string. Tell the manager (in its instructions) to pass all needed details in `input`.

❌ Mistake: Letting the specialist return a long essay to the manager.
✅ Correct: Use `custom_output_extractor` or ask the child for JSON/short text to save tokens.

❌ Mistake: Forgetting nested runs cost extra LLM calls.
✅ Correct: Count them: each as_tool call is at least one more model call (usually 2 with a tool). Cap with `max_turns`.

---

## 🧠 Tricky Interview Question
The manager calls `rate_lookup` but the specialist keeps answering 'which product?' because it has no context. Why, and how do you fix it?

**Answer:** Agent-as-tool runs a fresh nested run whose only input is the tool argument string. The manager's conversation history is not forwarded. Fix: (1) instruct the manager to put product, country and any ids into `input`, (2) or give the tool a typed `parameters` schema (`as_tool(parameters=<pydantic model>)` exists in 0.24.0) so the LLM must fill fields, (3) or pass shared data through the run `context` object which tools can read (not shown to the LLM). If the specialist really needs the whole conversation, a handoff is the right pattern.

---

## ⚫ Interview Questions + Answers

**Q1:** What is `as_tool`?

**A1:** It turns an Agent into a function tool another agent can call; the child runs a nested loop and its final output becomes the tool result.

**Q2:** Handoff vs agent-as-tool?

**A2:** Handoff transfers control and shares history; as_tool keeps the manager in control and passes only a string input.

**Q3:** Does `result.last_agent` change with as_tool?

**A3:** No. In our run it stayed `Manager`.

**Q4:** How do you control the cost of nested agents?

**A4:** `max_turns` on the as_tool call, short specialist instructions, `custom_output_extractor` to trim output, small model for specialists, and logging `context_wrapper.usage` (nested usage is added to the parent).

**Q5:** Design: 6 specialists, but most questions need only 1. How?

**A5:** Use `is_enabled` to expose only the tools allowed for the user/tenant, keep tool descriptions precise so the model picks one, add a cheap router (small model) in front, and set per-tool timeouts and `failure_error_function` so one failing specialist does not break the answer.

---

## 💰 Cost Impact
Each agent-as-tool call adds at least 1 extra LLM call (2 if the specialist uses a tool). A manager with 2 specialist calls is roughly 2 manager calls + 2-4 specialist calls. Formula: cost = sum over calls of (input_tokens x in_price + output_tokens x out_price). Tips: a smaller model for specialists, trim outputs, cap `max_turns`. Exact prices change - approximate, check the current price list. The numbers printed in this note (60 tokens) are from the fake model.

---

## 🔷 When to Use
✅ Use when:
- One agent must combine answers from several specialists
- You need pre/post-processing around a specialist
- Specialists have different tools/models and you want to keep the manager prompt short

❌ Avoid when:
- The specialist needs the full conversation (use handoff)
- A single tool function is enough (nested agent is wasted tokens)
- Latency is critical and the specialist needs many turns

---

## 📊 Visual Diagram
```
  User -> Manager agent (LLM)
              |  tool call: rate_lookup({"input": "..."})
              v
        +-------------------------+
        | nested Runner.run       |   own max_turns
        |  RateAgent (LLM)        |
        |    -> get_tariff_rate() |
        |  final_output "20%"     |
        +-------------------------+
              |  tool result (string)
              v
        Manager (LLM) -> final answer -> User
        (last_agent == Manager)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| as_tool | Wrap an agent as a function tool | Agent को tool बनाना |
| Manager | Agent that stays in control | control रखने वाला agent |
| Nested run | Child Runner.run inside a tool call | tool के अंदर चलता दूसरा run |
| custom_output_extractor | Function that shapes the child's output | child के output को छाँटने वाला function |
| is_enabled | Show tool only when True | शर्त पर tool दिखाना |
| Handoff | Transfer of control to another agent | control दूसरे agent को सौंपना |

---

## ⚡ 3-Line Summary
English: `as_tool` makes a specialist agent callable like a function while the manager keeps control.
The specialist only sees the `input` string and runs its own limited loop.
Nested runs cost extra LLM calls, so cap turns and trim outputs.

Hindi: `as_tool` specialist agent को function की तरह call-able बनाता है और control manager के पास रहता है।
Specialist सिर्फ़ `input` string देखता है और अपना सीमित loop चलाता है।
Nested runs में extra LLM calls लगती हैं, इसलिए turns सीमित करें और output छोटा रखें।

---

## ➡️ Next Topic
**#58 Orchestrator Pattern** - now that agents can be tools, we use one planner agent to coordinate several specialists step by step.

---
