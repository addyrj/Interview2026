---

# 65. SDK + FastAPI Integration
# हिंदी में: OpenAI Agents SDK को FastAPI के साथ जोड़ना
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with FastAPI `TestClient` and a scripted model (`fake.py`, full listing in note #57), so no API key was needed. Real model calls were NOT run - they need OPENAI_API_KEY. The streamed text comes from the scripted model.

---

## 🔵 Simple Definition (2-3 lines)
Serving an SDK agent over HTTP means: validate the request with Pydantic, build or reuse the `Agent` once, call `await Runner.run(...)` inside an `async def` endpoint, and map SDK exceptions and usage into clean HTTP responses. For live tokens use `Runner.run_streamed` with a `StreamingResponse`.

## 🔵 सरल परिभाषा (Hindi)
SDK agent को HTTP पर serve करने का मतलब: request को Pydantic से validate करें, `Agent` एक बार बनाएँ या दोबारा इस्तेमाल करें, `async def` endpoint में `await Runner.run(...)` चलाएँ, और SDK exceptions व usage को साफ़ HTTP responses में बदलें। Live tokens के लिए `Runner.run_streamed` और `StreamingResponse` इस्तेमाल करें।

---

## 🔴 Problem it Solves
Running `Runner.run_sync` in a request handler blocks the event loop and kills throughput. Creating a client per request wastes time. Without structure you leak internal errors to users, lose conversation memory between calls and cannot show partial answers, so the user stares at a blank screen for 10 seconds.

## 🔴 यह क्यों बना? (Hindi)
Request handler में `Runner.run_sync` चलाने से event loop block होता है और throughput गिरता है। हर request पर client बनाना समय खराब करता है। Structure के बिना internal errors users को दिख जाते हैं, कॉल के बीच conversation memory खो जाती है और partial answers नहीं दिखते, इसलिए user 10 सेकंड खाली screen देखता है।

---

## 🟢 How it Works

```
App startup  (lifespan)    -> build shared Agent(s) once -> app.state.agent
Request      POST /ask {question, session_id}
Step 1 -> FastAPI validates body with Pydantic (422 if bad)
Step 2 -> Depends(get_agent) injects the Agent (tests can override)
Step 3 -> SQLiteSession(session_id) gives per-conversation memory
Step 4 -> await Runner.run(agent, question, session=session, max_turns=6)
Step 5 -> map errors: MaxTurnsExceeded -> 504, ModelBehaviorError -> 502
Step 6 -> return {answer, tokens}  (usage from result.context_wrapper.usage)
Streaming: Runner.run_streamed(...) -> async for event in run.stream_events()
           -> yield SSE frames "data: {...}\n\n" for text deltas
```

## 🟢 कैसे काम करता है? (Hindi)

```
App startup (lifespan)   -> साझा Agent(s) एक बार बनाएँ -> app.state.agent
Request      POST /ask {question, session_id}
Step 1 -> FastAPI Pydantic से body validate करता है (गलत हो तो 422)
Step 2 -> Depends(get_agent) Agent inject करता है (tests override कर सकते हैं)
Step 3 -> SQLiteSession(session_id) हर बातचीत की memory देता है
Step 4 -> await Runner.run(agent, question, session=session, max_turns=6)
Step 5 -> errors map करें: MaxTurnsExceeded -> 504, ModelBehaviorError -> 502
Step 6 -> {answer, tokens} लौटाएँ (usage result.context_wrapper.usage से)
Streaming: Runner.run_streamed(...) -> async for event in run.stream_events()
           -> text deltas के लिए SSE frames "data: {...}\n\n" भेजें
```

**Verified details (0.24.0):**
- `Runner.run` is a coroutine; `Runner.run_streamed` returns a result object immediately and you iterate `stream_events()`. Token deltas are `raw_response_event` events whose `data.type == "response.output_text.delta"` (advanced sample).
- `SQLiteSession(session_id, db_path=":memory:")` - the default database is in memory, so history is lost on restart. For production pass a file path or use a database-backed session.
- Advanced sample output: `{'answer': 'Duty is 20%', 'tokens': 15}` and the stream `data: {"delta": "Duty "} | data: {"delta": "is "} | data: {"delta": "20%"} | data: {"done": true, "final": "Duty is 20%"}`.

**Hindi नोट:** Agent (instructions + tools) सस्ता object है, पर model client और DB connection साझा रखें। Per-request बदलने वाली चीज़ें (user id, tenant) `context=` में डालें, Agent में नहीं, वरना concurrent requests आपस में मिल जाएँगी।

---

## 🟡 Real World Example
**Tariff Agent.** `POST /ask` takes `{question, session_id}`; the agent calls `get_tariff_rate`, answers in one string and returns token usage for billing. `POST /ask/stream` streams the answer word by word to the browser via Server-Sent Events. A 504 is returned if the loop limit is hit, a 502 if the model misbehaves.

**Customer Support Agent:** the front end calls `/ask/stream` with the ticket id as `session_id`, so follow-up messages continue the same conversation.

## 🟡 Real Example Hindi mein
**Tariff Agent.** `POST /ask` में `{question, session_id}` आता है; agent `get_tariff_rate` बुलाता है, एक string में जवाब देता है और billing के लिए token usage लौटाता है। `POST /ask/stream` जवाब को Server-Sent Events से browser तक शब्द-दर-शब्द भेजता है। Loop limit टकराए तो 504, model गड़बड़ करे तो 502।

**Customer Support Agent:** front end `/ask/stream` को ticket id `session_id` बनाकर बुलाता है, इसलिए अगले संदेश उसी बातचीत को जारी रखते हैं।

---

## 💻 Code Example — Basic
Smallest correct endpoint. Output: `{'answer': 'Duty is 20%'}`.

```python
# Basic: the smallest correct SDK + FastAPI endpoint (offline, TestClient).
# verified against openai-agents 0.24.0 + fastapi 0.163.0
from fastapi import FastAPI
from pydantic import BaseModel
from agents import Agent, Runner, function_tool, set_tracing_disabled
from fake import ScriptedModel, tool_call, text

set_tracing_disabled(True)

@function_tool
def get_tariff_rate(hs_code: str) -> str:
    """Duty percent."""
    return "20%"

class Q(BaseModel):                                               # validated request body
    question: str

app = FastAPI()

@app.post("/ask")
async def ask(q: Q) -> dict[str, str]:                            # async def: Runner.run is a coroutine, never block the loop
    m = ScriptedModel([[tool_call("get_tariff_rate", '{"hs_code":"6109.10"}')], [text("Duty is 20%")]])  # offline script
    agent = Agent(name="Tariff", instructions="Use tools.", tools=[get_tariff_rate], model=m)             # cheap to build per request
    res = await Runner.run(agent, q.question)                     # one full agent loop
    return {"answer": str(res.final_output)}

if __name__ == "__main__":
    from fastapi.testclient import TestClient
    print(TestClient(app).post("/ask", json={"question": "Duty on shirts?"}).json())
```

## 💻 Code Example — Advanced
Lifespan, dependency injection, session memory, SSE streaming and error mapping.

```python
# Advanced: FastAPI with lifespan, dependency-injected agent, session memory, streaming (SSE) and error mapping.
# verified against openai-agents 0.24.0 + fastapi 0.163.0 (TestClient); real model: not run - needs OPENAI_API_KEY
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Any
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agents import Agent, MaxTurnsExceeded, ModelBehaviorError, Runner, SQLiteSession, set_tracing_disabled
from fake import ScriptedModel, text

set_tracing_disabled(True)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:          # build shared things ONCE at startup
    app.state.agent = Agent(name="Tariff", instructions="Be brief.", model=ScriptedModel([[text("Duty is 20%")]]))
    app.state.stream_agent = Agent(name="TariffStream", instructions="Be brief.", model=ScriptedModel([[text("Duty is 20%")]]))
    yield                                                         # app runs here; clean up after yield if needed

app = FastAPI(lifespan=lifespan)

def get_agent(request: Request) -> Agent:                         # dependency: easy to override in tests
    return request.app.state.agent

class Q(BaseModel):
    question: str
    session_id: str = "s1"

@app.post("/ask")
async def ask(q: Q, agent: Annotated[Agent, Depends(get_agent)]) -> dict[str, Any]:
    session = SQLiteSession(q.session_id)                         # in-memory by default: conversation memory per session id
    try:
        res = await Runner.run(agent, q.question, session=session, max_turns=6)
    except MaxTurnsExceeded:
        raise HTTPException(504, "agent loop limit reached")
    except ModelBehaviorError as e:
        raise HTTPException(502, f"model misbehaved: {e}")
    return {"answer": str(res.final_output), "tokens": res.context_wrapper.usage.total_tokens}

@app.post("/ask/stream")
async def ask_stream(q: Q, request: Request) -> StreamingResponse:
    async def gen() -> AsyncIterator[str]:
        run = Runner.run_streamed(request.app.state.stream_agent, q.question, max_turns=6)
        async for ev in run.stream_events():                      # raw events carry token deltas
            if ev.type == "raw_response_event" and ev.data.type == "response.output_text.delta":
                yield f"data: {json.dumps({'delta': ev.data.delta})}\n\n"   # Server-Sent Events frame
        yield f"data: {json.dumps({'done': True, 'final': str(run.final_output)})}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")

if __name__ == "__main__":
    from fastapi.testclient import TestClient
    with TestClient(app) as c:                                    # "with" runs the lifespan
        print(c.post("/ask", json={"question": "rate?"}).json())
        print(c.post("/ask/stream", json={"question": "rate?"}).text.strip().replace("\n\n", " | "))
```

Not shown: mid-stream errors. Once the first SSE byte is sent the HTTP status is already 200, so send an `{"error": ...}` frame instead of raising.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Async entrypoint | `await graph.ainvoke(...)` | `crew.kickoff_async()` | `await Runner.run(...)` | `await agent.run(...)` |
| Streaming | `astream` / `astream_events` | Step callbacks, limited token stream | `Runner.run_streamed().stream_events()` | `run_stream(...)` |
| Conversation memory | Checkpointer + `thread_id` | Memory features | `session=` (SQLite, others) | Chat history in team/agent |
| State/pause across requests | Strong (checkpoints) | Limited | You build it (sessions) | Save/load state |

_OpenAI SDK column verified in openai-agents 0.24.0; other columns are from general knowledge of those libraries (not installed or re-verified here) - check their docs before quoting in an interview._

---

## ⚠️ Common Mistakes
❌ Mistake 1: `Runner.run_sync(...)` inside `async def`.
✅ Correct: `await Runner.run(...)`; sync calls block the event loop for the whole LLM latency.

❌ Mistake 2: Storing per-user data on a shared `Agent` or in module globals.
✅ Correct: Pass it through `context=` per request; build the Agent once.

❌ Mistake 3: Using the default in-memory `SQLiteSession` and expecting history after a restart or on another worker.
✅ Correct: Give a file/DB path or a shared store; with several workers an in-memory DB is per process.

❌ Mistake 4: Returning raw exception text to the user.
✅ Correct: Map SDK errors to 4xx/5xx with safe messages and log the detail.

---

## 🧠 Tricky Interview Question
Your streaming endpoint works locally but users behind nginx see the whole answer at once, after a long delay. Why, and how do you fix it?

**Answer:** A reverse proxy buffers the response before forwarding it, so SSE frames are held back. Fix at the proxy (`proxy_buffering off` / `X-Accel-Buffering: no` header), send `Cache-Control: no-cache`, and flush small frames; check gzip is not buffering. Also confirm the generator really yields per delta and that nothing in between (a middleware) collects the body. Test with `curl -N`. Separately, decide what happens on client disconnect: the generator is cancelled, so the agent run should be allowed to stop (and you should record usage so far).

---

## ⚫ Interview Questions + Answers

**Q1:** Why `async def` and `await Runner.run` in FastAPI?

**A1:** The run mostly waits on network I/O; awaiting keeps the event loop free so other requests are served.

**Q2:** Where should the Agent be created?

**A2:** Once at startup (lifespan) or per request when cheap; request-specific data goes in `context`, not on the Agent.

**Q3:** How do you give each user conversation memory?

**A3:** Pass `session=SQLiteSession(session_id, db_path=...)` (or another session backend) keyed by user/conversation id.

**Q4:** How do you test endpoints without OpenAI?

**A4:** Inject the agent with `Depends` and override it with `app.dependency_overrides` using a scripted model (see #67).

**Q5:** System design: chat API for 1000 concurrent users.

**A5:** Stateless FastAPI workers behind a load balancer, sessions in Postgres/Redis (not in-memory), SSE for streaming with proxy buffering off, per-tenant rate limits and token budgets (#69), timeouts and `max_turns`, usage logged per request, graceful shutdown that lets in-flight streams finish.

---

## 💰 Cost Impact
The HTTP layer adds no tokens, but sessions do: every turn re-sends the stored history as input, so cost grows with conversation length. Cap history (`SessionSettings` limits or trimming), validate `max_length` on the question, set `max_turns`, and return `usage` so billing can track it. Formula: `input_tokens per turn ~ system + history + new message`. Prices approximate - verify.

---

## 🔷 When to Use
✅ Use when:
- Exposing an agent as an HTTP API for web/mobile clients
- Needing streaming UX and per-conversation memory
- You want typed requests, DI and easy testing

❌ Avoid when:
- A request can run for minutes (use a job queue + polling/webhook)
- You need durable pause/resume across days (consider LangGraph checkpoints; see #68)
- You would run `run_sync` in an async handler

---

## 📊 Visual Diagram
```
 Client ---POST /ask-----> FastAPI --validate--> Pydantic Q
                              |
                              +--Depends(get_agent)--> Agent (built in lifespan)
                              |
                              +--SQLiteSession(session_id)  <-- memory
                              v
                       await Runner.run(...)  --> LLM <-> tools
                              |
        errors -> 504 / 502 / 500          usage -> {tokens}
                              v
 Client <---JSON------------- response

 Client ---POST /ask/stream-> Runner.run_streamed -> stream_events()
 Client <---data: {"delta":"Duty "}\n\n ... data: {"done":true}
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| lifespan | Startup/shutdown hook of FastAPI | FastAPI का startup/shutdown hook |
| Depends | Dependency injection | dependency injection |
| Session | Stored conversation history | संग्रहीत बातचीत का history |
| SSE | Server-Sent Events stream | server से events की stream |
| run_streamed | Streaming variant of run | streaming वाला run |
| 504 / 502 | Gateway timeout / bad gateway | gateway timeout / bad gateway |

---

## ⚡ 3-Line Summary
English: Use async endpoints with await Runner.run, build agents once, and pass per-request data in context.
Add sessions for memory, run_streamed + SSE for live tokens, and map SDK errors to HTTP codes.
Override the agent dependency in tests so no real API is called.

Hindi: async endpoints में await Runner.run इस्तेमाल करें, agents एक बार बनाएँ, और per-request data context में दें।
Memory के लिए sessions, live tokens के लिए run_streamed + SSE, और SDK errors को HTTP codes में map करें।
Tests में agent dependency override करें ताकि असली API न बुलाई जाए।

---

## ➡️ Next Topic
**#66 SDK Error Handling** - the exact failure modes (tool errors, max turns, bad model output, timeouts) and how to recover from each.

---
