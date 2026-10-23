# 140. Tool Use / Function Calling
# हिंदी में: Tool Use / Function Calling — LLM को आपके functions/APIs (order status देखना, refund बनाना, DB query, calculator) इस्तेमाल करने देना: model तय करता है कौन-सा tool किन arguments से, आपका code उसे चलाता है और नतीजा model को लौटाता है — सुरक्षा और अनुमति आपके code में

---

## 🔵 Simple Definition (English)
**Tool use (function calling)** lets an LLM interact with external systems. You describe available **tools** (name, description, JSON-schema parameters). When useful, the model responds with a **tool call** (tool name + arguments) instead of plain text. **Your application executes** the tool (calls your API, DB, search, calculator), sends back the **tool result**, and the model continues, possibly calling more tools, until it produces a final answer.
- Claude: `tools=[{name, description, input_schema}]` → response `stop_reason: "tool_use"` with `tool_use` blocks `{id, name, input}` → you reply with a user message containing `tool_result` blocks `{tool_use_id, content, is_error?}`.
- OpenAI: `tools=[{type:"function", function:{name, description, parameters}}]` → `tool_calls` → messages with `role:"tool"`.
- **tool_choice**: auto (model decides), any/required, a specific tool (forced, also used for structured output), or none.
- **Parallel tool calls**: the model can request several independent tools in one turn.
- **MCP (Model Context Protocol)**: an open standard (introduced by Anthropic in 2024 and adopted widely) for exposing tools and data sources to AI applications through a common protocol.
The model **never executes anything itself**. Your code decides what actually runs, with **authentication, authorization, validation and confirmation**.

## 🔵 सरल परिभाषा (Hindi)
Tool use = LLM को बाहरी systems से जोड़ना: आप tools बताते हो (नाम, विवरण, JSON-schema parameters); ज़रूरत हो तो model सादे text की जगह "tool call" (नाम + arguments) लौटाता है; आपका ऐप उसे चलाता है (API, DB, search, calculator), नतीजा (tool result) वापस देता है, और model आगे बढ़ता है — और tools या अंतिम जवाब।
Claude में `tool_use` blocks और जवाब में `tool_result`; OpenAI में `tool_calls` और `role:"tool"`; tool_choice (auto, any, ख़ास tool, none); एक साथ कई tools; MCP — tools/डेटा जोड़ने का खुला मानक। Model ख़ुद कुछ नहीं चलाता — क्या चलेगा यह आपका code तय करता है (auth, अनुमति, जाँच, पुष्टि के साथ)।

---

## 🔴 Problem it Solves
An LLM alone can only produce text from its training data and prompt. Real assistants must:
- **Fetch live, user-specific data**: "Where is my order?" means calling the order service with the user's order ID. "What's my refund status?" means calling the payments service.
- **Take actions**: raise a refund request, reschedule a delivery, block a lost card, book a cab, create a Jira ticket.
- **Compute exactly**: totals, EMIs, GST, date maths (calculator or code tools instead of mental math).
- **Search** knowledge bases, the web, or databases (RAG as a tool).
Without tools, the model would guess (hallucinate order status) or be useless for transactional tasks. Function calling turns LLMs into **natural-language interfaces to your systems**: conversational support, internal ops copilots, agents. It requires careful engineering so the model can't do anything the user isn't allowed to do.

## 🔴 यह क्यों बना? (Hindi)
अकेला LLM सिर्फ़ training और prompt से text बना सकता है; असली सहायक को: live और यूज़र-विशेष डेटा लाना ("मेरा order कहाँ है?" → order service), काम करना (refund request, delivery बदलना, खोया card block, cab book, ticket बनाना), सटीक गणना (total, EMI, GST, तारीख़ें — calculator/code tool से), और knowledge base/web/DB में खोज।
बिना tools के model अंदाज़ा लगाएगा (गढ़ा हुआ order status) या लेन-देन वाले कामों में बेकार; function calling LLM को आपके systems का "बोलचाल वाला interface" बनाता है — पर इतनी सावधानी से कि model वो न कर सके जिसकी यूज़र को अनुमति नहीं।

---

## 🟢 How it Works — Step by Step

### The tool-call loop

```
User: "Mera order 4521 kahan hai? Bahut late ho gaya"
 1. App → LLM: system + tools [get_order_status, get_refund_status, create_refund_request, search_help] + messages
 2. LLM → App: stop_reason=tool_use, tool_use {id: t1, name: "get_order_status", input: {"order_id": "4521"}}
 3. App: AUTHZ check (order 4521 belongs to this user?) → call order-service → result {status: OUT_FOR_DELIVERY, eta_min: 12, delay_min: 25}
 4. App → LLM: assistant turn (tool_use) + user turn with tool_result {tool_use_id: t1, content: "{...json...}"}
 5. LLM → App: final text "Your order is out for delivery and should arrive in ~12 minutes. Sorry for the 25-min delay…"
    (or another tool call, e.g., check compensation policy) → loop until end_turn or max iterations
```

### Designing good tools

```
Names & descriptions: clear verb_noun names; description says WHEN to use and WHEN NOT to; describe each
  parameter (format, units: amount_paise; examples) — the model relies heavily on these
Narrow & safe: get_order_status(order_id) instead of run_sql(query); separate read vs write tools
Inputs: enums for options, required vs optional, validate everything server-side (never trust model args)
Outputs: concise, structured JSON with only needed fields (tokens!), human-readable error messages
  ("ORDER_NOT_FOUND: no order 4521 for this user") as tool_result with is_error → model can recover
Idempotency: write tools accept/generate idempotency keys; repeated calls don't double-refund
Confirmation: destructive/money-moving actions require explicit user confirmation step (UI) or human approval
Granularity: not too many tools (confusion) — group by domain; 5–20 well-described tools is typical per agent
```

### Security model (critical)

```
- Identity comes from YOUR session, not from the model: tools receive user_id from auth context; the
  model only supplies business args (order_id) which you check against ownership
- Least privilege: each tool can do only what's needed; scoped service credentials; rate limits per user
- Prompt injection: tool results (emails, web pages, tickets) can contain malicious instructions →
  treat as data, don't auto-execute follow-up writes based solely on untrusted content
- Policy limits in code: e.g., create_refund_request max ₹500 auto; above → human queue
- Audit log every tool call: user, tool, args, result, decision, model, prompt version
```

### Controls & performance

```
tool_choice: "auto" default; force a tool for structured extraction; "none" to answer only
Parallel calls: execute independent tool calls concurrently (asyncio.gather) → lower latency
Max iterations / budget: stop loops (e.g., 5 tool rounds), timeouts per tool, circuit breakers
Streaming: stream final text; show "Checking your order…" status while tools run
Caching: cache read-only tool results briefly (order status 10–30 s) within a conversation
```

### MCP (Model Context Protocol) in one paragraph

```
MCP standardizes how AI apps (clients) discover and call tools/resources exposed by MCP servers (e.g., a
"QuickBite Orders" MCP server exposing get_order_status). Benefits: reuse integrations across AI apps,
consistent auth & schemas, ecosystem of ready servers (GitHub, Slack, databases). Same security rules apply.
```

## 🟢 कैसे काम करता है? (Hindi)
1. Loop: ऐप system + tools + messages भेजता है → model `tool_use` लौटाता है (जैसे `get_order_status` {order_id: 4521}) → ऐप अनुमति जाँचकर (order इसी यूज़र का?) service call करता है → `tool_result` वापस → model अंतिम जवाब या अगला tool → max iterations तक।
2. अच्छे tools: साफ़ नाम, description में कब इस्तेमाल करना/कब नहीं, हर parameter का format/इकाई (amount_paise); `run_sql` नहीं, `get_order_status` जैसे सीमित tools; read और write अलग; output छोटा JSON; error भी साफ़ (is_error) ताकि model संभल सके।
3. Write tools idempotent (idempotency key), पैसे/नुक़सान वाले कामों पर यूज़र की पुष्टि या इंसान की मंज़ूरी, बहुत ज़्यादा tools नहीं (5–20 अच्छे)।
4. सुरक्षा: user_id हमेशा आपके session से (model से नहीं), model का दिया order_id मालिकाना जाँचकर; least privilege, rate limits; tool results में छुपे निर्देश (prompt injection) — डेटा मानो; नीति की सीमाएँ code में (₹500 से ऊपर refund इंसान को); हर tool call का audit log।
5. Performance: स्वतंत्र tool calls साथ-साथ चलाओ, हर tool पर timeout, loop सीमा, "आपका order देख रहे हैं…" दिखाओ, read results थोड़ी देर cache; MCP — tools/डेटा को AI ऐप्स से जोड़ने का साझा मानक, वही सुरक्षा नियम।

---

## 🟡 Real World Example

**OpenAI function calling (June 2023) and Claude tool use (2024)** — major providers standardized JSON-schema tool calling, turning chatbots into assistants that can check orders, book appointments and query databases.

**Model Context Protocol (Nov 2024)** — Anthropic open-sourced MCP to standardize connecting AI apps to tools and data. It was quickly adopted across the industry (including OpenAI's agent tooling in 2025) and by many IDEs and enterprise tools, creating an ecosystem of reusable tool servers.

**Customer support agents (food delivery, airlines, banks)** — LLM agents call order, refund and booking APIs with strict policy limits. Mistakes here are costly: in a widely reported 2024 case a tribunal held Air Canada responsible for wrong refund information its chatbot gave. Business rules belong in tools and code.

**Indian context** — conversational commerce on WhatsApp (e.g., JioMart on WhatsApp) and UPI-linked assistants show tool-driven flows: check catalog, add to cart, create order and send a payment link, each a backend action invoked from a conversation, with confirmation steps.

## 🟡 Real Example Hindi में
OpenAI ने जून 2023 में function calling और Claude ने 2024 में tool use मानक बनाया — chatbots अब orders देख सकते, appointments book कर सकते, DB query कर सकते; Anthropic ने नवंबर 2024 में MCP open-source किया — जल्दी ही उद्योग (2025 में OpenAI के agent tools समेत) और IDEs में अपनाया गया।
Support agents (food delivery, airlines, बैंक) सख़्त सीमाओं के साथ order/refund APIs call करते हैं — 2024 में एक tribunal ने Air Canada को उसके chatbot की ग़लत refund जानकारी के लिए ज़िम्मेदार ठहराया; WhatsApp पर JioMart जैसा conversational commerce — catalog देखना, cart, order, payment link — हर कदम पुष्टि के साथ backend action।

---

## 🟠 My Stack Example

### Tool definitions + secure executor + loop (Python, Claude)
```python
TOOLS = [
  {"name": "get_order_status",
   "description": "Get live status, ETA and delay for ONE of the current user's orders. Use when the user asks where/when their order is.",
   "input_schema": {"type": "object", "properties": {"order_id": {"type": "string", "description": "Order number like '4521'"}},
                    "required": ["order_id"]}},
  {"name": "get_refund_status",
   "description": "Get refund status for one of the user's orders.",
   "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}},
  {"name": "create_refund_request",
   "description": "Raise a refund request after the user has CONFIRMED. Only for missing items or quality issues per policy.",
   "input_schema": {"type": "object", "properties": {
       "order_id": {"type": "string"}, "reason": {"type": "string", "enum": ["MISSING_ITEM", "FOOD_QUALITY", "WRONG_ITEM"]},
       "amount_paise": {"type": "integer", "minimum": 1}, "user_confirmed": {"type": "boolean"}},
     "required": ["order_id", "reason", "amount_paise", "user_confirmed"]}},
]

async def execute_tool(name: str, args: dict, user) -> tuple[str, bool]:
    try:
        if name in ("get_order_status", "get_refund_status", "create_refund_request"):
            order = await orders.get(args["order_id"])
            if not order or order.user_id != user.id:                       # AUTHZ from session, not model
                return json.dumps({"error": "ORDER_NOT_FOUND"}), True
        if name == "get_order_status":
            return json.dumps({"status": order.status, "eta_min": order.eta_min, "delay_min": order.delay_min}), False
        if name == "get_refund_status":
            return json.dumps(await payments.refund_status(order.id)), False
        if name == "create_refund_request":
            if not args.get("user_confirmed"): return json.dumps({"error": "NEEDS_CONFIRMATION"}), True
            if args["amount_paise"] > min(order.paid_paise, 50_000):          # policy cap ₹500 auto, in CODE
                await human_queue.add(order.id, args); return json.dumps({"status": "SENT_FOR_REVIEW"}), False
            r = await refunds.create(order.id, args["reason"], args["amount_paise"], idempotency_key=f"llm:{order.id}:{args['reason']}")
            return json.dumps({"status": "CREATED", "refund_id": r.id}), False
        return json.dumps({"error": "UNKNOWN_TOOL"}), True
    finally:
        await audit.log_tool_call(user.id, name, args)

async def run_agent(user, messages, max_rounds=5):
    for _ in range(max_rounds):
        resp = await aclient.messages.create(model="claude-sonnet-5-5", max_tokens=800, system=SUPPORT_SYSTEM,
                                             tools=TOOLS, messages=messages)
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")
        messages.append({"role": "assistant", "content": resp.content})
        calls = [b for b in resp.content if b.type == "tool_use"]
        results = await asyncio.gather(*[execute_tool(c.name, c.input, user) for c in calls])   # parallel
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": c.id, "content": out, "is_error": err} for c, (out, err) in zip(calls, results)]})
    return "Sorry, I couldn't complete that. Connecting you to an agent."    # loop guard
```

### Confirmation UX for write actions (React Native)
```tsx
// When the assistant proposes a refund, the server returns a pending action instead of executing it
{pendingAction?.type === 'REFUND' && (
  <ConfirmSheet title={`Raise refund of ₹${pendingAction.amountPaise / 100} for order ${pendingAction.orderId}?`}
    onConfirm={() => send({ confirmActionId: pendingAction.id })}        // next request sets user_confirmed=true server-side
    onCancel={() => send({ cancelActionId: pendingAction.id })} />
)}
```

### Node: OpenAI-style tool calling (for comparison)
```js
const r = await openai.chat.completions.create({ model: process.env.OPENAI_MODEL, messages,
  tools: [{ type: 'function', function: { name: 'get_order_status', description: 'Get status of one of the user\'s orders',
           parameters: { type: 'object', properties: { order_id: { type: 'string' } }, required: ['order_id'] } } }] });
for (const call of r.choices[0].message.tool_calls ?? []) {
  const args = JSON.parse(call.function.arguments);
  const out = await executeTool(call.function.name, args, req.user);      // same authz rules
  messages.push(r.choices[0].message, { role: 'tool', tool_call_id: call.id, content: JSON.stringify(out) });
}
```

### Exposing tools via an MCP server (TypeScript sketch)
```ts
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';
const server = new McpServer({ name: 'quickbite-orders', version: '1.0.0' });
server.tool('get_order_status', { order_id: z.string() }, async ({ order_id }, ctx) => {
  const user = await authFromContext(ctx);                               // MCP auth → your identity
  const o = await orders.getForUser(order_id, user.id);
  return { content: [{ type: 'text', text: JSON.stringify(o ? { status: o.status, eta_min: o.etaMin } : { error: 'ORDER_NOT_FOUND' }) }] };
});
```

---

## ⚫ Interview Questions + Answers

**Q1: How does function calling work end to end?**
A1: You send the model a list of tools with names, descriptions and JSON-schema parameters, along with the conversation. If the model decides a tool is needed, it returns a structured tool call (name plus arguments) instead of a final answer. Your application validates the arguments, checks authorization, executes the function (API, DB, search) and returns the result as a tool-result message linked to the call ID. The model incorporates the result and either calls more tools or answers. You loop with limits on iterations and time.

**Q2: How do you make tool use safe?**
A2: Never let the model control identity or privileges: tools get the user from the authenticated session and verify ownership of any resource IDs the model provides. Design narrow, least-privilege tools (no generic SQL or shell), validate every argument server-side, enforce business limits in code (refund caps, rate limits), require explicit user confirmation or human approval for destructive or money-moving actions, make write tools idempotent, treat tool outputs and retrieved content as untrusted (prompt injection), and audit-log every call.

**Q3: What makes a tool description good?**
A3: A clear, action-oriented name. A description explaining what the tool does, when to use it and when not to, and any prerequisites (like user confirmation). Precisely described parameters with types, formats, units and examples (`amount_paise`, ISO dates, enums). Concise, structured outputs with only relevant fields, and informative error messages the model can act on. Test with evals, since the model's tool selection depends heavily on these descriptions.

**Q4: How do you handle tool errors and long-running tools?**
A4: Return errors as tool results (flagged as errors) with clear codes and messages so the model can retry with corrected arguments, ask the user for missing info, or apologize and escalate. Apply per-tool timeouts, retries for transient failures and circuit breakers. For long-running operations (report generation, bookings with external providers), return a job ID immediately and let the model tell the user it's in progress, completing asynchronously via notifications or follow-up polling tools.

**Q5: What is MCP and why does it matter?**
A5: The Model Context Protocol is an open standard for connecting AI applications (clients) to external tools, prompts and data resources exposed by servers through a common interface for discovery, invocation and authentication. It avoids building bespoke integrations for every app-tool pair, enables an ecosystem of reusable servers (databases, SaaS, internal APIs) and makes tools portable across AI clients. Teams still apply the same security principles of least privilege, auth and auditing on MCP servers.

---

## 🔷 Trade-offs
✅ Tools: live data & actions, exact computation — ❌ more latency (extra rounds), complexity, security surface.
✅ Many tools: capability — ❌ model confusion; split into sub-agents/routing.
✅ Autonomous actions: speed — ❌ risk; use confirmations/human-in-the-loop for high-impact steps.
✅ MCP: standard integrations — ❌ another protocol layer to secure and operate.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tool / function | External capability for the model | model के लिए बाहरी क्षमता |
| Tool call | Model's request to run a tool | tool चलाने की माँग |
| Tool result | Output returned to the model | tool का नतीजा |
| input_schema | JSON Schema of tool arguments | arguments का ढाँचा |
| tool_choice | Control tool selection | tool चुनने पर नियंत्रण |
| Parallel tool calls | Multiple calls in one turn | एक साथ कई calls |
| Least privilege | Minimal permissions per tool | न्यूनतम अनुमति |
| Human-in-the-loop | Human approval step | इंसान की मंज़ूरी |
| Idempotent write | Safe to retry action | दोहराने पर भी सुरक्षित |
| MCP | Model Context Protocol | tools जोड़ने का मानक |

---

## ⚡ 3-Line Summary
**English:**
1. Describe tools (name, description, schema) → model emits tool calls → your code validates/authorizes/executes → returns tool results → loop until final answer (with limits).
2. Design narrow, well-described, idempotent tools with concise outputs and clear errors; run independent calls in parallel; confirm high-impact actions.
3. Identity & limits live in code, never in the model; treat tool outputs as untrusted; audit everything; MCP standardizes tool integrations.

**Hindi:**
1. Tools बताओ → model tool call दे → आपका code जाँचकर चलाए → नतीजा वापस → अंतिम जवाब तक loop (सीमा के साथ)।
2. सीमित, साफ़ बताए गए, idempotent tools; छोटे outputs और साफ़ errors; साथ-साथ calls; बड़े कामों पर पुष्टि।
3. पहचान और सीमाएँ code में, model में नहीं; tool output पर भरोसा नहीं; सबका audit; MCP से मानक जुड़ाव।

---

## ➡️ Next Topic Suggestion
**141. ReAct Pattern** — Tool use becomes an agent when the model reasons, acts and observes in a loop. Next: the ReAct pattern, how agent loops work, stopping conditions, and making agents reliable.
