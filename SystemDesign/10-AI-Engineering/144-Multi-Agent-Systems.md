# 144. Multi-Agent Systems
# हिंदी में: Multi-Agent Systems — एक बड़े काम को कई विशेषज्ञ agents में बाँटना (जैसे orders वाला, payments वाला, policy वाला), एक orchestrator उन्हें काम देता है और नतीजे जोड़ता है — कब फ़ायदेमंद, कब बेकार, और ख़र्च व तालमेल कैसे संभालें

---

## 🔵 Simple Definition (English)
A **multi-agent system** uses **several LLM agents**, each with its own **role, instructions, tools and context**, that collaborate on a task. Common patterns:
- **Orchestrator-workers (supervisor)**: a lead agent plans, delegates subtasks to specialist workers (possibly in parallel) and synthesizes their results.
- **Router / handoff**: a triage agent hands the conversation to the right specialist (payments, orders, account), which can hand back or onward.
- **Pipeline (sequential specialists)**: research → draft → review → format.
- **Generator-critic (evaluator-optimizer)**: one agent produces, another critiques against criteria, and they iterate (bounded).
- **Parallel workers + aggregator**: the same question explored from multiple angles or sources, then merged (voting or synthesis).
- **Hierarchical**: supervisors of supervisors for large tasks.
Benefits: **separation of concerns** (smaller, focused prompts and tool sets), **parallelism** and **context isolation**, since each worker uses its own context window. Costs: **many more tokens and latency**, **coordination failures**, and **harder debugging and evaluation**.
Frameworks: LangGraph (supervisor and swarm patterns), OpenAI Agents SDK (handoffs), Claude Agent SDK (subagents), CrewAI, Microsoft AutoGen.

## 🔵 सरल परिभाषा (Hindi)
Multi-agent system = कई LLM agents, हर एक की अपनी भूमिका, निर्देश, tools और context, मिलकर काम करें: orchestrator-workers (मुख्य agent योजना बनाकर विशेषज्ञों को काम बाँटे, साथ-साथ भी, फिर नतीजे जोड़े), router/handoff (triage agent बातचीत सही विशेषज्ञ — payments, orders — को सौंपे), pipeline (research → draft → review), generator-critic (एक बनाए, दूसरा जाँचे, सीमित बार दोहराओ), parallel + aggregator, hierarchical।
फ़ायदे: हर agent का छोटा, केंद्रित prompt और tools, साथ-साथ काम, हर worker का अलग context; क़ीमत: बहुत ज़्यादा tokens और देर, तालमेल की ग़लतियाँ, debugging और evaluation कठिन।

---

## 🔴 Problem it Solves
A single agent with 40 tools and a 5,000-word system prompt becomes **confused and unreliable**: it picks wrong tools, forgets rules and fills its context with irrelevant intermediate results. Some tasks are also naturally **decomposable**:
- A **customer support** platform spans orders, payments and refunds, account and KYC, and restaurant partner issues, each with different tools, policies and permissions.
- A **research or analysis** task ("Compare quick-commerce delivery times across 5 cities from our data and public reports") benefits from parallel investigators.
- **Content pipelines** (a product description, then compliance review, then Hindi translation) benefit from specialist roles and a critic.
- **Coding agents** delegate exploration, implementation and test-running to subagents to keep the main context clean.
Multi-agent designs give **modularity, parallel speed-ups and better focus**, when the task genuinely needs it. Otherwise they add cost and failure modes.

## 🔴 यह क्यों बना? (Hindi)
40 tools और 5,000 शब्दों के system prompt वाला एक agent उलझ जाता है — ग़लत tools, नियम भूलना, context बेकार बीच के नतीजों से भरना। कई काम स्वाभाविक रूप से बँट सकते हैं: support (orders, payments/refunds, account/KYC, restaurant partner — अलग tools, नीतियाँ, अनुमतियाँ); research ("5 शहरों में quick-commerce delivery समय की तुलना") में साथ-साथ जाँच; content (product विवरण → compliance जाँच → हिंदी अनुवाद); coding agents में खोज, लिखना, tests subagents को।
सही काम पर multi-agent = modularity, तेज़ी, बेहतर ध्यान; ग़लत काम पर बस ज़्यादा ख़र्च और ग़लतियाँ।

---

## 🟢 How it Works — Step by Step

### Patterns at a glance

```
1) ORCHESTRATOR-WORKERS                         2) ROUTER / HANDOFF
   Lead agent ──plan──► worker A (orders)          Triage agent ──► Payments agent ──handoff──► Refund agent
        │        ──────► worker B (payments)                    └─► Orders agent
        │        ──────► worker C (policy RAG)     (one active agent owns the conversation at a time)
        ◄── results ── synthesize final answer
3) GENERATOR ↔ CRITIC (evaluator-optimizer)     4) PARALLEL + AGGREGATE
   Writer → Critic (rubric) → Writer (fix) …       Q → [agent₁, agent₂, agent₃] → aggregator (vote/merge)
   (max N rounds, stop when rubric passes)
```

### Design rules that make it work

```
1. Clear contracts: each agent has a narrow role, its OWN tool set (least privilege) & output schema
2. Structured handoffs: pass a compact task brief {goal, constraints, known facts, expected output format}
   — not the entire conversation (context isolation saves tokens & confusion)
3. Orchestrator owns the plan & final answer; workers return structured results (JSON + citations)
4. Budgets per agent (steps, tokens, time) + global budget; stop & synthesize partial results when exceeded
5. Parallelize independent subtasks; serialize dependent ones
6. Shared state/blackboard (e.g., LangGraph state) for facts discovered; avoid duplicated work
7. Permissions don't propagate magically: each worker's tools enforce the end-user's authz
8. Observability: trace tree (orchestrator span → worker spans → tool spans) with tokens & latency
9. Evaluate each agent alone (unit evals) AND the whole system (task success, cost, latency)
```

### When multi-agent helps vs hurts

```
HELPS: broad tasks with independent parts (research across sources), distinct domains with different
       tools/permissions (support verticals), heavy context per subtask (code exploration), need for
       review/critique loops, parallel speed-ups
HURTS: tightly coupled tasks needing shared detailed context (one agent does better), simple Q&A,
       strict latency/cost budgets, when coordination errors (contradictions, dropped info) outweigh gains
Rule: start with ONE agent + good tools + workflow; split only when evals show tool confusion,
      context overflow, or clear parallelism benefits
```

### Cost reality

```
Every agent call = its own prompt + reasoning + tool results → token usage multiplies (often several-fold
to an order of magnitude vs single chat). Mitigate: cheaper models for workers, concise briefs, cap
parallel fan-out, cache shared context, only use multi-agent for high-value tasks
```

### Failure modes

```
- Lost information between agents (brief missing a constraint) → structured briefs + checklists
- Contradictory worker results → orchestrator reconciles with evidence/citations, or asks a verifier
- Infinite delegation / ping-pong handoffs → max handoffs, explicit ownership
- Over-spawning workers for trivial tasks → orchestrator guidance on effort scaling ("simple: 1 worker")
- Error propagation: a worker's hallucination becomes "fact" → require sources, verify critical facts
```

## 🟢 कैसे काम करता है? (Hindi)
1. Patterns: orchestrator-workers (मुख्य agent योजना बनाकर orders/payments/policy workers को काम, नतीजे जोड़कर जवाब), router/handoff (एक समय में एक agent बातचीत का मालिक), generator ↔ critic (rubric से जाँच, सीमित दौर), parallel + aggregate (कई agents, फिर vote/merge)।
2. नियम: हर agent की पतली भूमिका, अपने tools (least privilege), output schema; handoff में पूरी बातचीत नहीं, छोटा brief (लक्ष्य, सीमाएँ, ज्ञात तथ्य, अपेक्षित format); orchestrator योजना और अंतिम जवाब का मालिक; हर agent और कुल budget; स्वतंत्र काम साथ-साथ; साझा state; हर worker के tools यूज़र की अनुमति ख़ुद जाँचें।
3. कब फ़ायदा: स्वतंत्र हिस्सों वाले बड़े काम, अलग domains/tools/अनुमतियाँ, हर subtask में भारी context, review loops, तेज़ी; कब नुक़सान: आपस में गुँथे काम, सरल Q&A, सख़्त latency/ख़र्च — शुरुआत एक agent से, evals दिखाएँ तभी बाँटो।
4. ख़र्च: हर agent का अपना prompt + सोच + tool results — tokens कई गुना (कभी दस गुना तक); workers के लिए सस्ते models, छोटे briefs, सीमित fan-out, साझा context cache, सिर्फ़ क़ीमती कामों पर।
5. ग़लतियाँ: brief में शर्त छूटना, workers के उलटे नतीजे (सबूत/citations से सुलझाओ), handoff का ping-pong (सीमा, साफ़ मालिक), छोटे काम पर बहुत workers, एक worker की गढ़ी बात "तथ्य" बन जाए (स्रोत माँगो, ज़रूरी तथ्य जाँचो); trace tree से निगरानी, हर agent और पूरे system के evals।

---

## 🟡 Real World Example

**Anthropic's multi-agent research system (2025)** — Anthropic described the architecture behind Claude's Research feature: a lead agent plans and spawns parallel subagents that search in their own context windows, then synthesizes with citations. They reported it significantly outperformed a single agent on their internal research evals (about 90% better), while using far more tokens (multi-agent systems about 15× the tokens of a chat interaction). It's a clear statement of the value and cost trade-off.

**OpenAI Agents SDK handoffs and Swarm (2024–2025)** — popularized the router/handoff pattern for customer-service style systems (triage agent → refund agent → sales agent), with guardrails and tracing.

**Microsoft AutoGen and CrewAI** — open-source frameworks for role-based agent teams (planner, coder, reviewer), widely used for prototyping research and automation workflows.

**Enterprise support (illustrative)** — large Indian consumer and fintech companies with many product lines (food, grocery, payments, lending) naturally map to specialist agents with separate tools and permissions behind a triage layer, mirroring how human support is organized into queues.

## 🟡 Real Example Hindi में
Anthropic ने 2025 में Claude के Research feature का ढाँचा बताया — मुख्य agent योजना बनाकर साथ-साथ subagents चलाता है (हर एक का अपना context), फिर citations के साथ जोड़ता है; internal evals पर एक agent से ~90% बेहतर, पर chat से ~15 गुना tokens — क़ीमत और फ़ायदे का साफ़ हिसाब।
OpenAI Agents SDK/Swarm ने handoff pattern लोकप्रिय किया (triage → refund → sales); AutoGen और CrewAI भूमिका वाली agent टीमों (planner, coder, reviewer) के लिए; भारत की कई product lines वाली कंपनियों (food, grocery, payments, lending) में triage के पीछे विशेषज्ञ agents — जैसे इंसानी support की queues।

---

## 🟠 My Stack Example

### Orchestrator-workers with parallel subagents and structured briefs (Python, Claude)
```python
from pydantic import BaseModel
class Brief(BaseModel):
    goal: str; constraints: list[str]; known_facts: dict; output_format: str

WORKERS = {
    "orders":   {"system": "You investigate order & delivery facts using order tools only. Return JSON {findings, evidence}.",
                 "tools": ORDER_TOOLS, "model": "claude-haiku-5-5"},
    "payments": {"system": "You investigate payment & refund facts using payment tools only. Return JSON {findings, evidence}.",
                 "tools": PAYMENT_TOOLS, "model": "claude-haiku-5-5"},
    "policy":   {"system": "You find applicable policy clauses via search_help. Quote clauses with [S#]. Return JSON {findings, evidence}.",
                 "tools": [SEARCH_HELP_TOOL], "model": "claude-haiku-5-5"},
}

async def run_worker(name: str, brief: Brief, user) -> dict:
    w = WORKERS[name]
    msgs = [{"role": "user", "content": brief.model_dump_json()}]
    return await tool_loop(model=w["model"], system=w["system"], tools=w["tools"], messages=msgs,
                           user=user, max_rounds=4, max_output_tokens=1500)            # per-worker budget

async def orchestrate(user, question: str) -> str:
    plan = await llm_structured("claude-sonnet-5-5",
        system="Plan which specialists are needed (orders, payments, policy). Use the fewest needed. "
               "For each, write a brief: goal, constraints, known facts, output format.",
        user=question, schema=PlanSchema)                                              # {tasks: [{worker, brief}]}
    tasks = plan.tasks[:3]                                                             # cap fan-out
    results = await asyncio.gather(*[run_worker(t.worker, t.brief, user) for t in tasks], return_exceptions=True)
    findings = {t.worker: (r if not isinstance(r, Exception) else {"error": str(r)}) for t, r in zip(tasks, results)}
    final = await aclient.messages.create(model="claude-sonnet-5-5", max_tokens=600, system=
        "Synthesize a customer reply from specialist findings. Resolve conflicts using evidence; cite policy [S#]. "
        "If findings are insufficient, say what's missing and offer human help.",
        messages=[{"role": "user", "content": f"<question>{question}</question>\n<findings>{json.dumps(findings, ensure_ascii=False)}</findings>"}])
    await trace_tree(user.id, question, plan, findings, final)                         # orchestrator → worker spans
    return final.content[0].text
```

### Router / handoff pattern (triage → specialist), bounded handoffs
```python
SPECIALISTS = {"PAYMENTS": payments_agent, "ORDERS": orders_agent, "ACCOUNT": account_agent}
async def handle(user, conversation):
    owner, handoffs = await triage(conversation), 0
    while True:
        result = await SPECIALISTS[owner](user, conversation)          # returns {reply} or {handoff_to, reason}
        if "handoff_to" not in result or handoffs >= 2:
            return result.get("reply") or await escalate(user, conversation)
        owner, handoffs = result["handoff_to"], handoffs + 1
        conversation.append({"role": "user", "content": f"[handoff note] {result['reason']}"})
```

### Generator ↔ critic loop (bounded) for content (e.g., Hindi product descriptions)
```python
async def write_with_review(product, max_rounds=2):
    draft = await writer(product)                                      # claude-sonnet-5-5
    for _ in range(max_rounds):
        review = await critic(draft, rubric=["factual vs specs", "no medical claims", "≤ 80 words", "natural Hindi"])  # JSON {pass, issues}
        if review["pass"]: return draft
        draft = await writer(product, feedback=review["issues"])
    return draft                                                       # flag for human review if still failing
```

### LangGraph supervisor sketch
```python
# Supervisor node decides next worker or FINISH; workers are subgraphs with their own tools
g.add_conditional_edges("supervisor", lambda s: s["next"], {"orders": "orders", "payments": "payments", "policy": "policy", "FINISH": END})
for w in ("orders", "payments", "policy"): g.add_edge(w, "supervisor")
```

---

## ⚫ Interview Questions + Answers

**Q1: When would you use a multi-agent system instead of a single agent?**
A1: When the task decomposes into parts that benefit from separation: independent subtasks that can run in parallel (research across sources), distinct domains with different tools, policies and permissions (payments vs orders vs account), subtasks needing large private context (code exploration), or quality loops with a dedicated critic. A single agent is better for tightly coupled tasks, simple Q&A, and strict latency or cost budgets. Start with one well-tooled agent and split only when evals show tool confusion, context overflow or clear parallelism gains.

**Q2: Describe the orchestrator-worker pattern.**
A2: A lead (orchestrator) agent analyzes the request, makes a plan and delegates subtasks to specialist worker agents with structured briefs (goal, constraints, known facts, output format). Workers run with their own focused prompts, tools and context windows, often in parallel, and return structured findings with evidence. The orchestrator synthesizes the final result, reconciles conflicts, possibly requests more work within budget, and owns the final answer. Budgets, fan-out caps and tracing keep it controlled.

**Q3: What are the main costs and risks of multi-agent systems?**
A3: Token usage and latency multiply because every agent has its own prompts, reasoning and tool outputs, often several-fold to an order of magnitude more than a single chat. Coordination failures occur: lost constraints in handoffs, contradictory results, duplicated work, infinite delegation or handoff loops, and error propagation where one agent's hallucination is treated as fact. Debugging and evaluation are harder, and there are more surfaces for prompt injection and permission mistakes. Mitigate with clear contracts, structured briefs, budgets, cheaper worker models, verification of critical facts, and end-to-end tracing and evals.

**Q4: How do agents share information safely and efficiently?**
A4: Through explicit, structured interfaces rather than dumping full conversations: concise briefs in, and structured results with evidence or citations out, plus a shared state or blackboard (e.g., LangGraph state) for discovered facts the orchestrator curates. Pass only what each agent needs (context isolation), keep identities and permissions from the authenticated session (every worker's tools enforce authz), and treat other agents' outputs as claims to verify when they drive important decisions.

**Q5: How do you evaluate a multi-agent system?**
A5: At two levels. Per agent: unit evals for each specialist on its subtask (tool selection accuracy, correctness of findings, format adherence). End to end: scenario suites measuring task success, answer quality and faithfulness, latency, cost per task, number of agents and steps used, handoff loops, and safety violations. Compare against a single-agent baseline to justify the added complexity. In production, use trace trees (orchestrator to workers to tools), sample reviews, and dashboards for cost and failure patterns.

---

## 🔷 Trade-offs
✅ Specialization, parallelism, context isolation, modular ownership — ❌ token/latency multiplication, coordination bugs.
✅ Critic loops: higher quality — ❌ extra rounds & cost (bound them).
✅ Handoff routing: clean domain separation — ❌ conversation ownership & loop risks.
✅ Single agent: simpler, cheaper — ❌ tool confusion and context overload at scale.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Multi-agent system | Several cooperating agents | कई सहयोगी agents |
| Orchestrator / supervisor | Plans & delegates | योजना बनाकर काम बाँटने वाला |
| Worker / subagent | Specialist executing subtask | विशेषज्ञ agent |
| Handoff | Transfer conversation ownership | बातचीत सौंपना |
| Brief | Structured task description | काम का संक्षिप्त विवरण |
| Context isolation | Separate context per agent | हर agent का अलग context |
| Critic / evaluator | Reviews and scores output | जाँचने वाला agent |
| Fan-out | Parallel delegation | साथ-साथ काम बाँटना |
| Blackboard / shared state | Common fact store | साझा तथ्य भंडार |
| Error propagation | Mistakes spread across agents | ग़लती का फैलना |

---

## ⚡ 3-Line Summary
**English:**
1. Patterns: orchestrator-workers, router/handoff, pipeline, generator-critic, parallel + aggregate — each agent with narrow role, own tools, structured I/O.
2. Benefits: focus, parallelism, context isolation; costs: many more tokens, latency, coordination failures → budgets, briefs, cheaper workers, verification.
3. Start single-agent; go multi-agent when evals justify it; trace trees and per-agent + end-to-end evals keep it reliable.

**Hindi:**
1. Patterns: orchestrator-workers, handoff, pipeline, critic, parallel — हर agent की पतली भूमिका, अपने tools, structured input/output।
2. फ़ायदे: ध्यान, साथ-साथ काम, अलग context; क़ीमत: बहुत tokens, देर, तालमेल की ग़लतियाँ — budgets, briefs, सस्ते workers।
3. पहले एक agent; evals दिखाएँ तभी multi-agent; trace trees और evals से भरोसा।

---

## ➡️ Next Topic Suggestion
**145. Agent Memory Types** — Agents need to remember: within a conversation, across sessions, and how to do things. Next: short-term vs long-term memory (semantic, episodic, procedural), what to store, retrieval, and privacy.
