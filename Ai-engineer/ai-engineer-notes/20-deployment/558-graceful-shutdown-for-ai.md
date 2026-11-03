---

# 558. Graceful Shutdown for AI
# हिंदी में: AI के लिए Graceful Shutdown

---

## 🔵 Simple Definition (English)
Graceful shutdown means that when a server is told to stop (deploy, scale-down), it stops taking new requests, finishes the in-flight ones (like long LLM streams), closes connections cleanly, and only then exits.

## 🔵 सरल परिभाषा (Hindi)
Graceful shutdown का मतलब: जब server को बंद करने को कहा जाता है (deploy, scale-down), वह नए requests लेना बंद करता है, चल रहे requests (जैसे लंबी LLM streams) पूरे करता है, connections ठीक से बंद करता है और तब exit होता है।

---

## 🔴 Problem it Solves
A hard kill cuts a user's streaming answer mid-sentence, loses background jobs, leaves half-written DB rows, and wastes the tokens already paid for. LLM calls take 5-60 s, so deploys happen during live requests far more often than in classic CRUD APIs.

## 🔴 यह क्यों बना? (Hindi)
Hard kill user का streaming जवाब बीच में काट देता है, background jobs खो जाते हैं, DB rows अधूरी रह जाती हैं और जो tokens खर्च हो चुके वो बेकार जाते हैं। LLM calls 5-60 सेकंड लेती हैं, इसलिए deploy के समय live requests मिलना आम है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Orchestrator sends SIGTERM to the process
Step 2 → App flips readiness to 503 so the LB stops sending new traffic
Step 3 → Wait a few seconds for the LB to notice (deregistration delay)
Step 4 → uvicorn stops accepting new connections, waits for in-flight requests
Step 5 → Track own background tasks; await them with a deadline
Step 6 → Close clients: HTTP pool, DB, Redis, flush logs/traces
Step 7 → Exit 0. If deadline passes, orchestrator sends SIGKILL (hard stop)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Orchestrator process को SIGTERM भेजता है
Step 2 → App readiness 503 कर देता है ताकि LB नया traffic न भेजे
Step 3 → LB को पता चलने के लिए कुछ सेकंड रुको
Step 4 → uvicorn नए connections लेना बंद करता है, चल रहे requests का इंतज़ार करता है
Step 5 → अपने background tasks को deadline के साथ await करो
Step 6 → HTTP pool, DB, Redis बंद करो, logs/traces flush करो
Step 7 → Exit 0। Deadline बीती तो SIGKILL
```

---

## 🟡 Real World Example
**Tariff Classification System**: A bulk job classifies 500 invoice lines in the background, each calling the LLM. On deploy, the pod receives SIGTERM. The app stops accepting new jobs, finishes the current line, saves progress (last line id) to the DB, and exits. The next pod resumes from the saved line, so no tokens are paid twice.

**Zomato-style**: A chat assistant's live stream finishes its answer before the pod disappears.

## 🟡 Real Example Hindi mein
**Tariff System**: Bulk job background में 500 invoice lines classify करता है, हर line LLM call करती है। Deploy पर pod को SIGTERM मिलता है। App नए jobs लेना बंद करता है, मौजूदा line पूरी करता है, progress (last line id) DB में save करता है और exit होता है। अगला pod वहीं से resume करता है, इसलिए tokens दोबारा नहीं लगते।

---

## 💻 Code Example — Basic
```python
# Basic: lifespan hook runs cleanup after uvicorn handles SIGTERM
from contextlib import asynccontextmanager   # for lifespan
import httpx                                  # async HTTP client
from fastapi import FastAPI                   # framework


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(timeout=30)   # shared client for LLM calls
    yield                                            # serve requests
    await app.state.http.aclose()                    # cleanup runs on shutdown


app = FastAPI(lifespan=lifespan)                     # attach lifespan


@app.get("/ping")
async def ping() -> dict[str, str]:
    return {"ok": "yes"}                             # trivial route
# Run: uvicorn main:app --timeout-graceful-shutdown 30
```

## 💻 Code Example — Advanced
```python
# Production: track in-flight background tasks, drain with deadline, flip readiness
import asyncio                                # tasks + timeouts
import logging                                # logs
from contextlib import asynccontextmanager    # lifespan
from fastapi import FastAPI, HTTPException    # framework

log = logging.getLogger("shutdown")           # logger
DRAIN_SECONDS = 25.0                          # must be < orchestrator grace period (e.g. 30s)


class JobTracker:
    """Keeps references to background tasks so we can await them on shutdown."""

    def __init__(self) -> None:
        self.tasks: set[asyncio.Task[None]] = set()   # live tasks
        self.accepting: bool = True                   # false after SIGTERM

    def spawn(self, coro: "asyncio.Future[None] | object") -> None:
        if not self.accepting:                        # refuse new work while draining
            raise HTTPException(status_code=503, detail="shutting down")
        task = asyncio.create_task(coro)              # type: ignore[arg-type]
        self.tasks.add(task)                          # keep a strong reference
        task.add_done_callback(self.tasks.discard)    # auto-remove when done

    async def drain(self, timeout: float) -> None:
        self.accepting = False                        # stop intake
        if not self.tasks:
            return                                    # nothing to wait for
        done, pending = await asyncio.wait(self.tasks, timeout=timeout)  # bounded wait
        for t in pending:                             # deadline passed
            t.cancel()                                # cancel stragglers (save progress in their finally)
        log.info("drained=%d cancelled=%d", len(done), len(pending))


tracker = JobTracker()                                # shared tracker


async def classify_line(line_id: int) -> None:
    try:
        await asyncio.sleep(1)                        # stands in for an LLM call
    except asyncio.CancelledError:
        log.warning("line %s interrupted, saving checkpoint", line_id)
        raise                                         # always re-raise cancellation


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ready = True                            # ready
    yield                                             # serving
    app.state.ready = False                           # readiness -> 503
    await asyncio.sleep(2)                            # let LB deregister us
    await tracker.drain(DRAIN_SECONDS)                # finish or cancel jobs


app = FastAPI(lifespan=lifespan)                      # app


@app.post("/bulk/{line_id}")
async def bulk(line_id: int) -> dict[str, int]:
    tracker.spawn(classify_line(line_id))             # fire-and-track
    return {"queued": line_id}
```

---

## 🟠 FastAPI Integration
uvicorn already handles SIGTERM/SIGINT: it stops accepting connections and waits for requests. Add `--timeout-graceful-shutdown N` to cap the wait. Streaming responses (`StreamingResponse`) count as in-flight, so they finish unless the timeout hits. Your lifespan code runs after that.

```python
# Streaming route that survives a graceful stop as long as it ends within the timeout
from fastapi import FastAPI                       # framework
from fastapi.responses import StreamingResponse   # streaming
import asyncio                                    # sleep

app = FastAPI()                                   # app


async def token_stream():
    for word in ["HS", " code", " is", " 8517"]:  # fake tokens
        yield f"data: {word}\n\n"                 # SSE format
        await asyncio.sleep(0.2)                  # simulate model latency


@app.get("/stream")
async def stream() -> StreamingResponse:
    return StreamingResponse(token_stream(), media_type="text/event-stream")
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph with a checkpointer (Postgres/Redis) makes shutdown safe: if a run is interrupted, call `graph.ainvoke(None, config)` with the same `thread_id` to resume from the last completed node. Close the checkpointer connection in lifespan.

```python
# Resume pattern (illustrative): same thread_id continues from the last checkpoint
config = {"configurable": {"thread_id": "invoice-42"}}   # identifies the run
# result = await graph.ainvoke({"line": 1}, config)       # first attempt (may be killed)
# result = await graph.ainvoke(None, config)              # resume on next pod
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Grace period shorter than the longest LLM call
✅ Correct: Set `terminationGracePeriodSeconds` > drain timeout > longest expected stream.
```python
# Wrong: grace 10s, streams take 40s -> SIGKILL mid-answer
# Right: grace 45s, DRAIN_SECONDS=40, request timeout 30s
```

❌ Mistake 2: Fire-and-forget tasks with no reference
✅ Correct: keep them in a set and await on shutdown.
```python
# Wrong
asyncio.create_task(job())          # may be garbage collected, never awaited
# Right
t = asyncio.create_task(job()); tracker.add(t)   # tracked and drained
```

---

## 🧠 Tricky Interview Question
**Q**: "You added graceful shutdown, but users still see errors during deploys. Why?"

**Answer**: Race between SIGTERM and the load balancer. The LB may keep sending requests for a few seconds after the pod is told to stop. Fix: flip readiness to 503 first, sleep a few seconds (or use a `preStop` hook) before closing the listener, and set the LB deregistration delay. Also make sure the proxy (Nginx) does not buffer or cut streams.

---

## ⚫ Interview Questions + Answers

Q1: What signal does Kubernetes/ECS send first?
A1: SIGTERM, then SIGKILL after the grace period.

Q2: Why can't you catch SIGKILL?
A2: The kernel kills the process directly; no handler runs.

Q3: How do you avoid losing a long background job?
A3: Checkpoint progress, make jobs idempotent, and use a queue (SQS/Celery/Redis) so another worker retries.

Q4: Why re-raise `CancelledError`?
A4: Swallowing it breaks asyncio cancellation and the task never really stops.

Q5: Design deploys for a streaming chat product with zero cut streams.
A5: Rolling or blue-green deploy, readiness flips first, long preStop/drain (longer than the max stream), sticky nothing, clients auto-reconnect with `Last-Event-ID` and server-side conversation state in Redis so a reconnect continues.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production service with streams or background jobs

❌ Avoid when:
- Never skip it; only the length of the drain should be tuned (short for stateless quick APIs)

---

## 📊 Visual Diagram
```
 SIGTERM
   │
   ▼
 readiness=503 ──► LB stops new traffic
   │
   ▼
 wait for in-flight streams/jobs  (deadline = DRAIN)
   │            │
   │ done       └─ timeout → cancel + checkpoint
   ▼
 close HTTP/DB/Redis, flush traces
   │
   ▼
 exit 0   (else SIGKILL at grace period end)
```

---

## 💰 Cost Impact
A killed stream or job means its tokens were paid but the result lost, and a retry pays again. If 1% of requests are cut by each deploy and a request averages 1,500 tokens, frequent deploys quietly waste tokens. Optimise: drain properly, checkpoint partial work, and make retries resume instead of restart.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SIGTERM | Polite stop signal | विनम्र बंद करने का signal |
| SIGKILL | Forced kill, uncatchable | ज़बरदस्ती kill |
| Drain | Finish in-flight work | चल रहा काम पूरा करना |
| Grace period | Time allowed before kill | Kill से पहले मिला समय |
| Idempotent | Safe to repeat | दोबारा चलाना सुरक्षित |

---

## ⚡ 3-Line Summary
English: On SIGTERM, go unready, stop intake, finish in-flight streams and jobs, close clients, then exit. Keep drain time below the orchestrator grace period but above your longest request. Checkpoint long jobs so retries resume.
Hindi: SIGTERM पर unready हों, नया काम बंद करें, चल रही streams और jobs पूरी करें, clients बंद करें और exit करें। Drain time को grace period से कम पर सबसे लंबे request से ज़्यादा रखें। लंबे jobs checkpoint करें।

---

## ➡️ Next Topic
**559. CI/CD for AI Apps** — automating build, test and deploy so these safe rollouts happen on every merge.
