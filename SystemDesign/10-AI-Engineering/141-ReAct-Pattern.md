# 141. ReAct Pattern
# हिंदी में: ReAct Pattern (Reason + Act) — agent का मूल तरीका: सोचो (क्या करना है) → काम करो (tool चलाओ) → नतीजा देखो → फिर सोचो… जब तक लक्ष्य पूरा न हो; साथ में रुकने के नियम, ग़लतियों से सँभलना और भरोसेमंद agents बनाना

---

## 🔵 Simple Definition (English)
**ReAct** (Reasoning + Acting) is a pattern where an LLM **interleaves reasoning with actions**:
1. **Thought**: decide what to do next given the goal and what's known.
2. **Action**: call a tool (search, API, calculator, code) with arguments.
3. **Observation**: read the tool result.
4. Repeat until the goal is met, then give the **final answer**.
Introduced in the 2022 paper "ReAct: Synergizing Reasoning and Acting in Language Models", it's the foundation of most **LLM agents**. Today it's implemented with **native tool calling** (Topic 140) in a loop, where the model's text or thinking between tool calls plays the "thought" role.
Making ReAct reliable in production requires:
- **stopping conditions** (max steps, budget, timeouts) and **loop detection**
- **error recovery** and **state/memory management**
- **guardrails** on actions and **observability** of every step (traces)
Related patterns: **plan-and-execute** (plan first, then run steps), **reflection** (critique and retry), and **router/workflow** designs (fixed steps where possible, agentic only where needed).

## 🔵 सरल परिभाषा (Hindi)
ReAct = LLM सोच और काम को बारी-बारी करता है: Thought (लक्ष्य और जानकारी देखकर आगे क्या करना है) → Action (tool चलाओ — search, API, calculator) → Observation (नतीजा पढ़ो) → दोहराओ जब तक लक्ष्य पूरा न हो → अंतिम जवाब।
2022 के paper "ReAct" से आया, ज़्यादातर LLM agents की नींव; आज native tool calling के loop से लागू होता है। Production में चाहिए: रुकने के नियम (अधिकतम steps, budget, timeout), loop पकड़ना, ग़लती से सँभलना, state/memory, actions पर guardrails, हर step की tracing। मिलते-जुलते: plan-and-execute, reflection, और जहाँ हो सके तय workflow।

---

## 🔴 Problem it Solves
Many real tasks need **multiple dependent steps** where the next step depends on what you learn:
- "My payment failed but money was debited. What should I do?" → check the payment status → see it's PENDING at the bank → check the auto-reversal policy → check whether the order was created → answer with an ETA and options.
- "Find me a vegetarian restaurant open now with delivery under 30 min and rating above 4" → search → filter → check availability → present options.
- An ops analyst asks: "Why did cancellations spike in Pune yesterday?" → query metrics → drill into reasons → correlate with rider supply or weather → summarize.
Pure prompting can't fetch information mid-reasoning, and fixed pipelines can't adapt to what they discover. ReAct lets the model **gather information and adapt its plan dynamically**. Uncontrolled agents, however, can loop, take wrong actions or burn tokens, so the pattern comes with **engineering guardrails**.

## 🔴 यह क्यों बना? (Hindi)
कई असली कामों में कई जुड़े कदम होते हैं जहाँ अगला कदम पिछले नतीजे पर निर्भर: "Payment fail पर पैसे कट गए, क्या करूँ?" → payment status देखो → bank पर PENDING → auto-reversal नीति → order बना या नहीं → ETA और विकल्प; "अभी खुला veg restaurant, 30 मिनट में delivery, 4+ rating" → खोज → filter → उपलब्धता; "कल Pune में cancellations क्यों बढ़े?" → metrics → कारण → riders/मौसम से मिलान → सारांश।
सिर्फ़ prompt बीच में जानकारी नहीं ला सकता, तय pipeline नई खोज के हिसाब से ढल नहीं सकती; ReAct जानकारी जुटाकर योजना बदलने देता है — पर बेलगाम agent loop में फँस सकता है, ग़लत काम कर सकता है, tokens जला सकता है, इसलिए guardrails ज़रूरी।

---

## 🟢 How it Works — Step by Step

### The loop

```
GOAL: "Paise kat gaye par order nahi hua (UPI). Kya karoon?"
Thought 1: Need payment status for the user's latest attempt.
Action 1:  get_payment_attempts(limit=1)
Obs 1:     {payment_id: P9, status: "PENDING", bank: "XYZ", debited: true, order_created: false, age_min: 7}
Thought 2: Pending with debit and no order → check auto-reversal policy & timeline.
Action 2:  search_help("UPI debited but order not placed auto reversal")
Obs 2:     [S1] "If an order isn't created, the amount is auto-refunded within 48 hours (often in minutes)…"
Thought 3: Enough info; also offer retry since no order exists.
Final:     "Your ₹349 UPI payment is pending at your bank and no order was created. It will auto-refund within
            48 hours (usually sooner) [S1]. You can place the order again now — you won't be charged twice for the failed attempt."
```

### Implementation with native tool calling

```
messages = [system(goal, rules, tools usage policy), user(request)]
for step in 1..MAX_STEPS:
    resp = llm(messages, tools)
    if resp is final text → return
    for each tool_call → validate & execute (parallel if independent) → append tool_result
    append any errors as tool_result(is_error) → model can recover
    check budgets (tokens, time, cost), loop detection (same call+args repeated) → stop/escalate
return graceful fallback (handoff to human, partial answer)
```

### Reliability engineering for agents

```
Stopping: MAX_STEPS (e.g., 6–10), wall-clock timeout, token/cost budget per task
Loop detection: same tool + same args twice → inject "You already tried X; choose a different approach or answer"
Error handling: tool errors returned to model with guidance; retries for transient failures in code
State: keep a compact scratchpad/summary for long tasks (avoid context bloat); persist state for long-running
       agents (checkpoints — LangGraph, Topic 143)
Guardrails: write actions gated (confirmation, policy limits, human approval); allow-lists of tools per task
Determinism where possible: if the sequence is known (always: fetch order → check policy), use a WORKFLOW
       (code-orchestrated steps) and reserve ReAct for open-ended parts
Observability: trace every thought/action/observation with latency & tokens (Topic 147); replay failures
Evals: task-success rate, steps per task, cost per task, safety violations, human-escalation rate
```

### Variants

```
Plan-and-execute: LLM writes a plan (steps) → executor runs steps (possibly with smaller model) →
                  re-plan on failure → fewer expensive reasoning calls, clearer control
Reflection / self-critique: after an attempt, critique result vs goal → retry with fixes (bounded)
Router: classify request → send to specialized agent/workflow (support, payments, search)
Multi-agent (Topic 144): orchestrator delegates sub-tasks to specialist agents
```

### When NOT to use an agent

```
Single-step answers (FAQ RAG), fixed workflows, strict latency SLAs (<1 s), high-risk actions without
human review, or when a simple deterministic script does it → prefer workflows; agents add cost & variance
```

## 🟢 कैसे काम करता है? (Hindi)
1. Loop: Thought (क्या जानना/करना है) → Action (tool call) → Observation (नतीजा) → फिर Thought… → Final; जैसे UPI पैसे कटे पर order नहीं: payment status → PENDING, order नहीं बना → auto-reversal नीति खोजो → जवाब: 48 घंटे में पैसे वापस, दोबारा order कर सकते हो।
2. लागू करना: system (लक्ष्य, नियम, tools) + user → हर step पर LLM — final text तो लौटाओ, tool calls तो जाँचकर चलाओ (स्वतंत्र हों तो साथ-साथ), errors भी model को बताओ, budget और loop जाँचो → सीमा पर graceful fallback (इंसान को सौंपना)।
3. भरोसा: अधिकतम steps (6–10), समय और tokens/ख़र्च की सीमा, एक ही tool + arguments दोबारा = loop (model को बताओ), छोटा scratchpad, लंबे कामों के लिए checkpoints, write actions पर पुष्टि/सीमा/इंसान, हर कदम का trace।
4. जहाँ क्रम पहले से पता हो (order लाओ → नीति देखो) वहाँ code वाला workflow, ReAct सिर्फ़ खुले हिस्सों में; प्रकार: plan-and-execute (पहले योजना), reflection (ख़ुद जाँचकर सुधार), router, multi-agent।
5. कब agent नहीं: एक कदम वाले जवाब, तय workflows, 1 सेकंड से कम latency, बिना इंसानी जाँच के बड़े जोखिम वाले काम, या जब साधारण script काफ़ी हो; नाप: task success, steps/task, ख़र्च/task, सुरक्षा उल्लंघन, escalation दर।

---

## 🟡 Real World Example

**ReAct paper (Yao et al., Princeton & Google, 2022)** — showed that interleaving reasoning traces with actions (e.g., Wikipedia search) improved performance on multi-hop QA and interactive decision-making benchmarks, with more interpretable trajectories than acting or reasoning alone.

**Coding agents (Claude Code, GitHub Copilot agent mode, Devin and others)** — run ReAct-style loops: read files, run tests, edit code, observe failures and iterate, with step limits, sandboxing and human approval for risky commands.

**Anthropic's "Building effective agents" guidance (2024)** — recommends starting with simple, composable workflows (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer) and using autonomous agent loops only where flexibility is needed. That's widely adopted in production design.

**Support automation** — many companies deploy agents that diagnose issues across several systems (payments, orders, logistics) using ReAct loops with strict tool permissions, escalating to humans when confidence is low or limits are reached.

## 🟡 Real Example Hindi में
ReAct paper (Yao et al., Princeton और Google, 2022) ने दिखाया कि सोच और काम (जैसे Wikipedia search) को बारी-बारी करने से कई कदम वाले सवालों और फ़ैसलों में बेहतर नतीजे और समझने लायक रास्ता मिलता है।
Coding agents (Claude Code, Copilot agent mode, Devin) files पढ़ते, tests चलाते, code बदलते, failures देखकर दोहराते हैं — step सीमा, sandbox और जोखिम वाले commands पर इंसान की मंज़ूरी के साथ; Anthropic की "Building effective agents" (2024) सलाह: पहले सरल workflows (chaining, routing, parallel, orchestrator-workers), autonomous loop सिर्फ़ जहाँ लचीलापन चाहिए।

---

## 🟠 My Stack Example

### ReAct agent loop with budgets, loop detection and escalation (Python)
```python
MAX_STEPS, MAX_SECONDS, MAX_OUTPUT_TOKENS = 8, 45, 6000

AGENT_SYSTEM = """You are QuickBite's payments-support agent.
Goal: resolve the user's payment/refund issue using tools. Think briefly about what you need before each tool call.
Rules: use tools for facts (never guess statuses or amounts); cite help articles as [S#];
if you cannot resolve within policy, call escalate_to_human with a short summary."""

async def react_agent(user, question: str) -> str:
    messages = [{"role": "user", "content": question}]
    seen_calls, started, out_tokens = set(), time.monotonic(), 0
    for step in range(MAX_STEPS):
        if time.monotonic() - started > MAX_SECONDS or out_tokens > MAX_OUTPUT_TOKENS:
            break
        resp = await aclient.messages.create(model="claude-sonnet-5-5", max_tokens=1000, system=AGENT_SYSTEM,
                                             tools=PAYMENT_TOOLS, messages=messages)
        out_tokens += resp.usage.output_tokens
        await trace_step(user.id, step, resp)                                        # Topic 147
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for call in (b for b in resp.content if b.type == "tool_use"):
            sig = (call.name, json.dumps(call.input, sort_keys=True))
            if sig in seen_calls:                                                    # loop detection
                results.append({"type": "tool_result", "tool_use_id": call.id, "is_error": True,
                                "content": "You already called this with the same arguments. Use the earlier result or try a different approach."})
                continue
            seen_calls.add(sig)
            out, err = await execute_payment_tool(call.name, call.input, user)       # authz + policy in code
            results.append({"type": "tool_result", "tool_use_id": call.id, "content": out, "is_error": err})
        messages.append({"role": "user", "content": results})
    await escalate(user, question, messages)                                          # graceful fallback
    return "I've passed this to our payments team with all the details. You'll hear back within 2 hours."
```

### Workflow first, agent for the open-ended part
```python
async def handle_payment_issue(user, question):
    intent = await classify_intent(question)                       # cheap router (haiku)
    if intent == "REFUND_STATUS":                                  # deterministic workflow, no agent
        order = await orders.latest(user.id)
        status = await payments.refund_status(order.id)
        return await write_reply(question, {"order": order.summary(), "refund": status})
    return await react_agent(user, question)                       # ambiguous/multi-step → agent
```

### Plan-and-execute sketch
```python
plan = await llm_json("Create a numbered plan (max 5 steps) of tool calls to answer: " + question, schema=PlanSchema)
results = {}
for step in plan.steps:
    results[step.id] = await execute_payment_tool(step.tool, step.args | resolve_refs(step, results), user)
    if is_error(results[step.id]):
        plan = await replan(question, plan, results)               # bounded re-planning
answer = await synthesize(question, results)
```

### Agent eval harness (task success, steps, cost)
```python
async def eval_agent(cases):
    stats = []
    for c in cases:                                                # {question, user_fixture, expected: {"resolved": True, "escalated": False}}
        with fixture_user(c["user_fixture"]) as user:
            t0 = time.monotonic(); answer = await react_agent(user, c["question"])
            stats.append({"success": judge(answer, c["expected"]), "secs": time.monotonic() - t0, "steps": last_trace_steps()})
    return summarize(stats)                                        # success rate, p95 latency, avg steps, cost/task
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the ReAct pattern?**
A1: ReAct interleaves reasoning and acting: the model thinks about what it needs, takes an action (a tool call), observes the result, and repeats until it can answer. Grounding each reasoning step in real observations makes agents more accurate and interpretable than reasoning alone (which can hallucinate facts) or acting alone (which lacks planning). Modern implementations use native tool calling in a loop, where the model's intermediate text or thinking serves as the "thought".

**Q2: How do you prevent agents from looping or running away?**
A2: Impose hard limits (maximum steps, wall-clock timeouts, token and cost budgets per task). Detect repeated identical tool calls or oscillation and inject feedback or stop. Return informative tool errors so the model can change approach. Keep tool sets small and well-described per task. Summarize state to avoid context bloat. Always end with a graceful fallback (partial answer, human handoff) when limits are hit, and monitor steps per task and budget-exhaustion rates in production.

**Q3: When should you use a fixed workflow instead of an agent?**
A3: When the steps are known in advance and don't depend on intermediate discoveries (fetch order, check policy, respond), when latency must be predictable and low, when actions are high-risk and require deterministic control and auditability, or when cost per request must be tight. Workflows (code-orchestrated chains, routers, parallel calls) are cheaper, faster and easier to test. Reserve agentic loops for open-ended tasks where the path varies, and often combine them: workflow routing plus an agent for the ambiguous branch.

**Q4: How do you evaluate and monitor an agent?**
A4: Build scenario-based eval suites with fixtures (mock users, orders, tool responses) and expected outcomes. Measure task success (automated checks plus LLM-as-judge with human calibration), tool-call correctness, steps per task, latency, cost, safety-policy violations and escalation rates. In production, trace every step (prompts, tool calls, arguments, results, tokens, latency), sample traces for review, collect user feedback, alert on spikes in errors, loops or cost, and replay failed traces after fixes.

**Q5: What's plan-and-execute and how does it differ from ReAct?**
A5: Plan-and-execute separates planning from execution. The model first generates an explicit multi-step plan, then an executor (code, or a cheaper model) carries out the steps, re-planning only if something fails. ReAct decides one step at a time based on the latest observation. Plan-and-execute can be cheaper and more controllable, with fewer expensive reasoning calls and plans that can be validated or approved up front, but it's less adaptive to surprises. ReAct adapts continuously at higher per-step cost.

---

## 🔷 Trade-offs
✅ ReAct agents: adaptive, handle open-ended multi-step tasks — ❌ latency, cost, variance, harder testing.
✅ Workflows: predictable, cheap, auditable — ❌ rigid; can't handle surprises.
✅ Plan-and-execute: controllable, cheaper — ❌ less adaptive mid-task.
✅ Higher step limits: more task completion — ❌ runaway cost & risk.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ReAct | Reason + Act loop | सोचो + करो loop |
| Thought | Model's reasoning step | model की सोच |
| Action | Tool invocation | tool चलाना |
| Observation | Tool result fed back | tool का नतीजा |
| Agent loop | Repeated LLM-tool cycle | बार-बार LLM-tool चक्र |
| Stopping condition | When to end the loop | loop कब रुके |
| Loop detection | Catch repeated actions | दोहराव पकड़ना |
| Plan-and-execute | Plan first, then run steps | पहले योजना, फिर कदम |
| Reflection | Self-critique and retry | ख़ुद जाँच और सुधार |
| Human handoff | Escalate to a person | इंसान को सौंपना |

---

## ⚡ 3-Line Summary
**English:**
1. ReAct = Thought → Action (tool) → Observation, repeated until done; implemented via native tool-calling loops.
2. Make it reliable: step/time/cost limits, loop detection, error feedback, compact state, gated write actions, full tracing and evals.
3. Prefer workflows for known sequences; use agents (or plan-and-execute) for open-ended tasks, with graceful human handoff.

**Hindi:**
1. ReAct = सोच → काम (tool) → नतीजा, पूरा होने तक; tool-calling loop से लागू।
2. भरोसा: step/समय/ख़र्च सीमा, loop पकड़ना, errors बताना, छोटा state, write actions पर नियंत्रण, tracing और evals।
3. तय क्रम हो तो workflow; खुले कामों के लिए agent या plan-and-execute, और इंसान को सौंपने का रास्ता।

---

## ➡️ Next Topic Suggestion
**142. LangChain Basics** — Frameworks package these patterns (prompts, models, retrievers, tools, chains). Next: LangChain's core abstractions, LCEL composition, and when a framework helps or hurts.
