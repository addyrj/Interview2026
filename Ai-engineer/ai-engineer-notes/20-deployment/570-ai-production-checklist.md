---

# 570. AI Production Checklist
# हिंदी में: AI Production Checklist

---

## 🔵 Simple Definition (English)
An AI production checklist is a short, repeatable list of checks you must pass before (and after) launching an LLM app: quality evals, reliability, security, privacy, cost control, monitoring, and rollback. It turns "it works on my laptop" into "it is safe to serve real users".

## 🔵 सरल परिभाषा (Hindi)
AI production checklist उन checks की छोटी, दोहराने योग्य list है जो LLM app launch करने से पहले (और बाद में) पास करने होते हैं: quality evals, reliability, security, privacy, cost control, monitoring और rollback। यह "मेरे laptop पर चल रहा है" को "असली users को serve करना सुरक्षित है" में बदलती है।

---

## 🔴 Problem it Solves
Demos hide the hard parts. In production, LLM apps hit timeouts, provider outages, hallucinations, prompt injection, cost spikes, and privacy issues. Teams forget items under deadline pressure (no timeout, no fallback, no eval set, logs full of PII). A checklist makes the review consistent and auditable.

## 🔴 यह क्यों बना? (Hindi)
Demos में मुश्किल हिस्से छुपे रहते हैं। Production में LLM apps को timeouts, provider outages, hallucinations, prompt injection, cost spikes और privacy issues मिलते हैं। Deadline के दबाव में टीमें चीज़ें भूल जाती हैं (timeout नहीं, fallback नहीं, eval set नहीं, PII भरे logs)। Checklist review को consistent और auditable बनाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Quality: golden eval set, pass threshold, regression tests in CI (hallucination, refusals)
Step 2 → Reliability: timeouts, retries with backoff, fallback model, circuit breaker, health checks
Step 3 → Performance: p95 latency target, streaming, caching, concurrency limits, load test
Step 4 → Security: auth, tenant isolation, input caps, injection defences, secrets in vault (see 568)
Step 5 → Privacy: PII redaction, DPA, retention, erasure path (see 569)
Step 6 → Cost: token budgets, max_tokens, per-tenant limits, cost dashboard + alerts (see 566, 567)
Step 7 → Observability: traces, version tags, quality sampling, alerts, on-call runbook (see 565)
Step 8 → Release: prompt/model versioning, canary or blue-green, rollback tested (see 563, 564)
Step 9 → Post-launch: review metrics at 1 day, 1 week; feed failures into the eval set
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Quality: golden eval set, pass threshold, CI में regression tests (hallucination, refusals)
Step 2 → Reliability: timeouts, backoff के साथ retries, fallback model, circuit breaker, health checks
Step 3 → Performance: p95 latency target, streaming, caching, concurrency limits, load test
Step 4 → Security: auth, tenant isolation, input caps, injection बचाव, secrets vault में (568)
Step 5 → Privacy: PII redaction, DPA, retention, erasure path (569)
Step 6 → Cost: token budgets, max_tokens, per-tenant limits, cost dashboard + alerts (566, 567)
Step 7 → Observability: traces, version tags, quality sampling, alerts, on-call runbook (565)
Step 8 → Release: prompt/model versioning, canary या blue-green, rollback का test (563, 564)
Step 9 → Launch के बाद: 1 दिन, 1 हफ्ते पर metrics देखो; failures को eval set में जोड़ो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Before launch the team walks the checklist. Eval: 500 labelled items, target >= 90% on 8-digit codes. Reliability: 20 s timeout, fallback to a second model, and "low confidence -> route to human broker". Security: tenant-scoped retrieval. Privacy: redact importer names. Cost: $50/day cap per tenant. Release: canary 5% for a day. One item failed: no rollback drill. They run the drill, then launch.

**Amazon-style**: A product-QA bot launch is blocked until the "unsafe answer" eval and the escalation-to-human path pass.

## 🟡 Real Example Hindi mein
**Tariff System**: Launch से पहले टीम checklist चलाती है। Eval: 500 labelled items, 8-digit codes पर लक्ष्य >= 90%। Reliability: 20 s timeout, दूसरे model पर fallback और "कम confidence -> human broker को भेजो"। Security: tenant-scoped retrieval। Privacy: importer names redact। Cost: प्रति tenant $50/day cap। Release: एक दिन 5% canary। एक item fail: rollback drill नहीं हुई थी। Drill करके फिर launch।

**Amazon-style**: Product-QA bot का launch तब तक रुका रहता है जब तक "unsafe answer" eval और human escalation path पास नहीं होते।

---

## 💻 Code Example — Basic
```python
# Basic checklist runner (pure Python, runs directly)
from dataclasses import dataclass                # simple record type
from typing import Callable                      # type hint


@dataclass
class Check:
    name: str                                    # what is being verified
    category: str                                # quality / security / cost ...
    test: Callable[[], bool]                     # returns True if passed
    blocker: bool = True                         # blockers must pass to launch


# Fake config standing in for the real app settings
CONFIG = {"timeout_s": 20, "max_tokens": 400, "fallback_model": "backup-model",
          "daily_budget_usd": 50, "pii_redaction": True, "rollback_tested": False}

CHECKS = [
    Check("request timeout set", "reliability", lambda: 0 < CONFIG["timeout_s"] <= 60),
    Check("max_tokens capped", "cost", lambda: 0 < CONFIG["max_tokens"] <= 1000),
    Check("fallback model defined", "reliability", lambda: bool(CONFIG["fallback_model"])),
    Check("budget cap set", "cost", lambda: CONFIG["daily_budget_usd"] > 0),
    Check("PII redaction on", "privacy", lambda: CONFIG["pii_redaction"]),
    Check("rollback tested", "release", lambda: CONFIG["rollback_tested"]),
]


def run(checks: list[Check]) -> bool:
    ok = True                                    # overall verdict
    for c in checks:
        try:
            passed = c.test()                    # run the check
        except Exception:                        # a crashing check counts as failed
            passed = False
        print(f"[{'PASS' if passed else 'FAIL'}] {c.category:12} {c.name}")
        if not passed and c.blocker:
            ok = False                           # a failed blocker stops the launch
    return ok


print("LAUNCH OK" if run(CHECKS) else "LAUNCH BLOCKED")        # rollback_tested is False -> blocked
```

## 💻 Code Example — Advanced
```python
# Production style: async readiness probes + eval gate as a CI/CD script
from __future__ import annotations
import asyncio                                   # run probes concurrently
import json                                      # machine-readable report
import sys                                       # exit code for CI
from dataclasses import asdict, dataclass        # report rows
from typing import Awaitable, Callable           # type hints

Probe = Callable[[], Awaitable[str]]             # returns detail text, raises on failure


@dataclass
class Result:
    name: str
    passed: bool
    detail: str


async def run_probe(name: str, probe: Probe, timeout: float = 10.0) -> Result:
    try:
        detail = await asyncio.wait_for(probe(), timeout=timeout)   # never hang CI
        return Result(name, True, detail)
    except asyncio.TimeoutError:
        return Result(name, False, "timeout")
    except Exception as exc:                                         # any error = fail
        return Result(name, False, f"{type(exc).__name__}: {exc}")


async def eval_probe() -> str:
    # In reality: run the golden set against the candidate (prompt, model) and compute accuracy.
    accuracy = 0.93                                                  # placeholder value
    if accuracy < 0.90:
        raise AssertionError(f"accuracy {accuracy:.2f} below 0.90")
    return f"accuracy {accuracy:.2f}"


async def llm_reachable_probe() -> str:
    # In reality: send a 1-token request to the provider and to the fallback.
    await asyncio.sleep(0.01)
    return "primary + fallback reachable (simulated)"


async def main() -> int:
    probes: dict[str, Probe] = {"golden-eval": eval_probe, "llm-reachable": llm_reachable_probe}
    results = await asyncio.gather(*(run_probe(n, p) for n, p in probes.items()))
    print(json.dumps([asdict(r) for r in results], indent=2))
    return 0 if all(r.passed for r in results) else 1                # non-zero blocks the pipeline


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
```

---

## 🟠 FastAPI Integration
Provide liveness and readiness endpoints. Readiness verifies dependencies (vector DB, LLM reachability, prompt registry), so the load balancer routes traffic only to healthy replicas.

```python
import asyncio
from fastapi import FastAPI, Response                  # framework

app = FastAPI()


async def check_vector_db() -> bool:
    await asyncio.sleep(0)                             # replace with a real ping
    return True


async def check_llm() -> bool:
    await asyncio.sleep(0)                             # replace with a tiny cached call
    return True


@app.get("/healthz")                                   # liveness: process is up
async def healthz() -> dict:
    return {"status": "alive"}


@app.get("/readyz")                                    # readiness: dependencies ok
async def readyz(response: Response) -> dict:
    vdb, llm = await asyncio.gather(check_vector_db(), check_llm(), return_exceptions=True)
    ready = vdb is True and llm is True                # exceptions are not True
    if not ready:
        response.status_code = 503                     # tell the load balancer to wait
    return {"vector_db": vdb is True, "llm": llm is True}
```

---

## 🔗 LangChain / LangGraph Connection
Production hardening of chains and graphs: `llm.with_retry()` / `max_retries`, `with_fallbacks([backup_llm])` for model fallback, `timeout=` on model constructors, `recursion_limit` and `max_concurrency` in run config, a checkpointer for durable state, and LangSmith tracing plus datasets for evals.

```python
from langchain_openai import ChatOpenAI

primary = ChatOpenAI(model="gpt-4o-mini", timeout=20, max_retries=2)   # timeout + retries
backup = ChatOpenAI(model="gpt-4o", timeout=30)                        # illustrative fallback
llm = primary.with_fallbacks([backup])                                 # auto-fallback on error
# await graph.ainvoke(state, config={"recursion_limit": 10, "max_concurrency": 4})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No timeout on LLM calls, so requests hang and workers pile up.
✅ Correct: always set timeouts and a fallback.

```python
# Wrong
resp = await client.chat.completions.create(model=m, messages=msgs)
# Right
resp = await asyncio.wait_for(client.chat.completions.create(model=m, messages=msgs, max_tokens=400), 20)
```

❌ Mistake 2: Launching with no eval set, judging quality by "looks fine" on five examples.
✅ Correct: a versioned golden set with a pass threshold in CI.

❌ Mistake 3: Having a rollback plan that was never tested. Run a rollback drill before launch.

---

## 🧠 Tricky Interview Question
**Q**: "Everything on your checklist is green and you launch. Within an hour, answers are subtly wrong for a new product category. What did the checklist miss?"

**Answer**: Checklists cover known risks; evals only cover the distribution you tested. This is a distribution shift. Add: production sampling with LLM-judge scoring, feedback buttons, alerts on low retrieval scores and low-confidence rate, "unknown category" detection, fast human escalation, and a loop that turns production failures into new eval cases. A checklist is a floor, not a guarantee, which is why post-launch monitoring and a rollback path are on it.

---

## ⚫ Interview Questions + Answers

Q1: Name five things to verify before launching an LLM app.
A1: Eval pass, timeouts and fallbacks, auth and tenant isolation, cost caps, and monitoring with rollback.

Q2: What is a fallback and when is it used?
A2: A secondary model or a degraded response used when the primary fails or times out. Example: switch to a backup model, or return cached/human-review result.

Q3: Liveness vs readiness probe?
A3: Liveness says the process is alive (restart if not). Readiness says it can serve traffic (dependencies OK); failing readiness removes it from the load balancer without restarting.

Q4: Why set `max_tokens`?
A4: It bounds output cost and latency, and prevents runaway generation.

Q5: (Hard) How would you build a quality gate in CI for prompt changes?
A5: Keep a versioned golden dataset, run candidate prompt/model on it in CI, compute metrics (exact match, schema validity, judge score, token count, latency), compare against the production baseline, fail the build on regression beyond a margin, and publish a diff report. Fix random seeds/temperature 0 where possible and run multiple trials for noisy tasks.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Before every launch, major prompt/model change, or new tenant onboarding

❌ Avoid when:
- A full formal review is too heavy for throwaway demos; use a mini version (timeout, cap, key safety)

---

## 📊 Visual Diagram
```
        ┌───────────────────────── PRE-LAUNCH ─────────────────────────┐
        │ Quality  Reliability  Security  Privacy  Cost  Observability │
        │  eval     timeout     authZ     redact   caps   traces       │
        │  gate     fallback    inject    DPA      limits alerts       │
        └───────────────┬──────────────────────────────────────────────┘
                        ▼ all blockers pass?
                  Canary / Blue-Green ─► rollback drill OK
                        ▼
                  LAUNCH ─► monitor ─► new failures ─► add to eval set ─┐
                        ▲                                               │
                        └───────────────────────────────────────────────┘
```

---

## 💰 Cost Impact
- Checklist items directly control spend: `max_tokens`, per-tenant budgets, caching, model routing, and rate limits. Illustrative: capping output at 400 tokens instead of unbounded can cut worst-case output cost by 5-10x on verbose prompts.
- Running evals costs tokens: 500 items x 1,500 tokens = 750K tokens per run (about $0.11 at an illustrative $0.15/1M input, plus output). Run full evals before release, smaller smoke sets on every commit.
- Use token usage metrics from monitoring to revisit the budget after one week.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Golden set | Fixed labelled test data | Fixed labelled test data |
| Fallback | Backup model/path when primary fails | Primary fail होने पर backup |
| Circuit breaker | Stop calling a failing dependency | Failing service को बुलाना रोकना |
| Readiness probe | Can this instance serve traffic? | क्या यह instance traffic ले सकता है? |
| Runbook | Step-by-step incident guide | Incident में क्या करें की guide |
| Canary | Small first rollout | छोटा पहला rollout |

---

## ⚡ 3-Line Summary
English: Before launch, verify quality evals, reliability (timeouts, fallbacks), security, privacy, cost caps, monitoring, and a tested rollback. Automate the checks in CI and readiness probes. After launch, feed production failures back into the eval set.
Hindi: Launch से पहले quality evals, reliability (timeouts, fallbacks), security, privacy, cost caps, monitoring और tested rollback जाँचो। इन checks को CI और readiness probes में automate करो। Launch के बाद production failures को eval set में वापस जोड़ो।

---

## ➡️ Next Topic
**571. Build Basic LLM Chat (FastAPI)** — the first interview problem: put these ideas into a small, working chat service.
