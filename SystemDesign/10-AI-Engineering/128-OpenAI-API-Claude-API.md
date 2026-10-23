# 128. OpenAI API + Claude API
# हिंदी में: OpenAI API + Claude API — अपने backend से LLM providers को सही तरीके से call करना: messages, system prompt, streaming, tools, errors, rate limits, retries, और कौन-सा model कब चुनें

---

## 🔵 Simple Definition (English)
**LLM provider APIs** let your application send prompts and receive model outputs over HTTPS:
- **Anthropic Claude API** (Messages API): `POST /v1/messages` with `model`, `max_tokens`, optional `system`, and `messages` (alternating user/assistant). Responses contain **content blocks** (text, tool_use) plus `usage` and a `stop_reason`. It supports streaming (SSE), tool use, vision (images/PDFs), prompt caching and a Message Batches API. Model families: **Opus** (most capable), **Sonnet** (balanced) and **Haiku** (fast, cheap).
- **OpenAI API**: Chat Completions (`/v1/chat/completions`) and the newer **Responses API**, with system/developer/user messages, tools (function calling), structured outputs (JSON schema), streaming, embeddings and a Batch API.
- Both are also available through cloud platforms: Claude via **Amazon Bedrock** and **Google Vertex AI**, OpenAI models via **Azure OpenAI**.
Production use requires **API key security, timeouts, retries with backoff for 429/5xx/overloaded errors, rate-limit handling, cost and usage logging, model selection and fallback**, and usually an internal **LLM gateway** wrapping the providers.

## 🔵 सरल परिभाषा (Hindi)
LLM provider APIs से आपका ऐप HTTPS पर prompt भेजकर model का जवाब पाता है: Claude API (`/v1/messages` — model, max_tokens, system, messages; जवाब में content blocks — text, tool_use — और usage; streaming, tools, images/PDF, prompt caching, batches; Opus सबसे सक्षम, Sonnet संतुलित, Haiku तेज़/सस्ता) और OpenAI API (Chat Completions और नया Responses API; tools, JSON schema, streaming, embeddings)।
Claude Amazon Bedrock और Google Vertex AI पर भी, OpenAI Azure पर भी। Production में: API key सुरक्षित, timeout, 429/5xx पर backoff से retry, rate limits, ख़र्च का हिसाब, model चुनना और fallback — अक्सर एक internal "LLM gateway" से।

---

## 🔴 Problem it Solves
Calling an LLM in a demo is one line, but production apps hit real issues:
- **Secrets in clients**: putting an API key in a React/React Native app means anyone can extract it and run up your bill. Calls must go through **your backend**.
- **Rate limits and overload**: providers return 429 (rate limit) or overloaded/5xx errors during peaks. Without retries and backoff, users see failures.
- **Latency**: 5–30 s responses need streaming, timeouts and async patterns.
- **Cost surprises**: no token logging means no idea which feature or tenant is spending lakhs.
- **Vendor lock-in and outages**: one provider down means your feature is down.
- **Different API shapes** between providers make switching painful without an abstraction.
Knowing the APIs deeply, plus a thin gateway layer, gives **security, reliability, observability and flexibility**.

## 🔴 यह क्यों बना? (Hindi)
Demo में LLM call एक line है, पर production में: API key को React/RN ऐप में रखा तो कोई भी निकालकर आपका बिल बढ़ा देगा — call हमेशा अपने backend से; peak पर 429/overloaded errors — बिना retry के यूज़र को failure; 5–30 सेकंड के जवाब के लिए streaming, timeout, async; token logging नहीं तो पता नहीं कौन-सा feature/ग्राहक लाखों ख़र्च कर रहा; एक provider बंद तो आपका feature बंद; providers के API अलग-अलग।
API की गहरी समझ + पतली gateway परत = सुरक्षा, भरोसा, निगरानी और लचीलापन।

---

## 🟢 How it Works — Step by Step

### Request/response anatomy (Claude Messages API)

```
POST https://api.anthropic.com/v1/messages
Headers: x-api-key: $ANTHROPIC_API_KEY, anthropic-version: 2023-06-01, content-type: application/json
{
  "model": "claude-sonnet-5-5",
  "max_tokens": 1024,                     ← REQUIRED cap on output tokens
  "system": "You are a helpful support agent for QuickBite...",
  "messages": [ {"role": "user", "content": "Where is my order #123?"} ],
  "temperature": 0.2,
  "tools": [ ... ]                        ← optional function definitions (Topic 140)
}
→ { "id": "msg_…", "content": [ {"type":"text","text":"…"} ],
    "stop_reason": "end_turn" | "max_tokens" | "tool_use" | "stop_sequence",
    "usage": { "input_tokens": 812, "output_tokens": 143, "cache_read_input_tokens": 0 } }
```

### OpenAI Chat Completions (comparable shape)

```
POST https://api.openai.com/v1/chat/completions   Authorization: Bearer $OPENAI_API_KEY
{ "model": "<model>", "messages": [ {"role":"system","content":"…"}, {"role":"user","content":"…"} ],
  "max_completion_tokens": 512, "temperature": 0.2, "tools": [...], "response_format": {...} }
→ { "choices": [ { "message": { "role":"assistant", "content":"…", "tool_calls":[…] },
                   "finish_reason":"stop|length|tool_calls" } ], "usage": {…} }
(OpenAI's newer Responses API offers a unified interface for tools, state and multimodal — same ideas)
```

### Key differences to remember

```
┌──────────────────────┬─────────────────────────────────┬──────────────────────────────────┐
│                      │ Claude (Anthropic)               │ OpenAI                           │
├──────────────────────┼─────────────────────────────────┼──────────────────────────────────┤
│ System prompt        │ top-level "system" field         │ system/developer message          │
│ Output cap           │ max_tokens (required)            │ max_completion_tokens (optional)  │
│ Response             │ content blocks (text/tool_use)   │ choices[].message (+tool_calls)   │
│ Tool results         │ user msg with tool_result block  │ role:"tool" message               │
│ Prompt caching       │ explicit cache_control breakpoints│ automatic for long prefixes      │
│ Batch                │ Message Batches API (~50% off)   │ Batch API (~50% off)              │
│ Clouds               │ Bedrock, Vertex AI               │ Azure OpenAI                      │
└──────────────────────┴─────────────────────────────────┴──────────────────────────────────┘
```

### Choosing a model (routing)

```
Simple classification, extraction, short replies, high volume  → small/fast tier (e.g., Claude Haiku)
General assistant, RAG answers, coding help                      → balanced tier (e.g., Claude Sonnet)
Hard reasoning, complex agents, long analysis, critical quality  → top tier (e.g., Claude Opus)
Decide by evals on YOUR tasks (quality vs latency vs cost), not by benchmarks alone
```

### Reliability: errors, retries, timeouts

```
400 invalid request (fix code/prompt)      401/403 auth (rotate key)      404 model not found
413 request too large (trim context)       429 rate limited → backoff, respect retry-after header
500/502/503 server error, 529 overloaded (Anthropic) → retry with exponential backoff + jitter
Timeouts: set client timeouts (e.g., 60–120 s non-streaming); prefer streaming for long outputs
Retries: official SDKs retry some errors automatically (configurable max_retries)
Idempotency: LLM calls aren't idempotent in output, but safe to retry (no side effects) — tool
  executions with side effects must be idempotent on YOUR side
Fallback: on repeated failure → smaller model / alternate provider / cached answer / graceful message
```

### Rate limits & capacity

```
Limits per org/workspace: requests/min, input tokens/min, output tokens/min (tiers grow with usage)
→ client-side token-bucket per tenant/feature, queue + concurrency limits in workers,
  batch API for offline jobs, monitor 429 rate; request higher limits before launches (sale/IPL)
```

### Security & data

```
Keys only on the server (secrets manager), separate keys per environment/feature, rotate
Never expose provider keys to browsers/mobile apps → your backend proxies with your own auth & limits
Data: send only necessary data; redact PII where possible; check provider data retention/training
  policies and enterprise/zero-retention options; regional hosting (e.g., via cloud providers) if needed
```

### LLM gateway pattern

```
App services ─► LLM Gateway (your service) ─► Anthropic / OpenAI / Bedrock / self-hosted
  - unified request/response format, model aliases ("support-default" → claude-sonnet-5-5)
  - auth, per-tenant quotas & rate limits, retries/fallback, timeouts
  - prompt/response logging (with PII redaction), token & cost accounting per feature/tenant
  - caching (Topic 148), guardrails hooks (Topic 149), A/B model experiments
Libraries: LiteLLM, Portkey, or a thin in-house wrapper
```

## 🟢 कैसे काम करता है? (Hindi)
1. Claude: `POST /v1/messages` — model, max_tokens (ज़रूरी), system, messages; जवाब में content blocks, stop_reason (end_turn, max_tokens, tool_use) और usage (tokens); OpenAI में choices[].message, finish_reason और system message अलग तरीके से।
2. Model चुनो काम के हिसाब से: आसान/भारी मात्रा — Haiku जैसा तेज़; आम सहायक/RAG — Sonnet; कठिन reasoning/agents — Opus; फ़ैसला अपने evals से।
3. Errors: 429 पर retry-after मानकर backoff, 5xx/529 (overloaded) पर backoff + jitter, 4xx पर code/prompt ठीक करो; timeout लगाओ, लंबे जवाब के लिए streaming; बार-बार fail पर छोटा model/दूसरा provider/सधा हुआ संदेश।
4. Rate limits (requests/min, tokens/min): ग्राहक/feature के हिसाब से token bucket, workers में concurrency सीमा, offline काम के लिए Batch API (~50% सस्ता), sale/IPL से पहले limits बढ़वाओ।
5. Keys सिर्फ़ सर्वर पर (secrets manager), browser/RN ऐप में कभी नहीं; ज़रूरत भर डेटा, PII हटाओ; एक LLM gateway बनाओ — एक जैसा format, model aliases, quotas, retries/fallback, logging, cost हिसाब, caching, guardrails।

---

## 🟡 Real World Example

**Zomato AI (2023)** — Zomato announced a generative-AI assistant that helps users discover food conversationally. Features like this call LLM APIs from the backend, combine them with the restaurant catalog and need careful cost control at food-delivery scale.

**Duolingo Max, Khan Academy Khanmigo, Notion AI** — early, well-known products built on hosted LLM APIs, all serving millions of users through backend integrations with rate-limit handling, caching and model routing.

**Amazon Bedrock & Vertex AI** — enterprises (including Indian banks and IT services firms) often consume Claude through Bedrock or Vertex for consolidated billing, VPC networking, regional hosting and existing compliance agreements, using the same Messages API concepts.

**LLM gateways in practice** — companies commonly put an internal gateway (or tools like LiteLLM/Portkey) in front of providers to standardize logging, budgets per team, retries and fallbacks, and to swap models without touching product code.

## 🟡 Real Example Hindi में
Zomato ने 2023 में "Zomato AI" बताया — बातचीत से खाना खोजने वाला सहायक; ऐसे features backend से LLM API call करते हैं, restaurant catalog से जोड़ते हैं और ख़र्च पर कड़ा नियंत्रण रखते हैं।
Duolingo Max, Khanmigo, Notion AI hosted LLM APIs पर बने; बहुत सी कंपनियाँ (भारतीय बैंक/IT कंपनियाँ भी) Claude को Amazon Bedrock या Vertex AI से इस्तेमाल करती हैं — एक बिल, VPC, क्षेत्रीय hosting; और providers के आगे internal LLM gateway (LiteLLM/Portkey) रखती हैं।

---

## 🟠 My Stack Example

### Python (FastAPI): Claude call with timeouts, retries, usage logging
```python
import anthropic, time, logging
from fastapi import FastAPI, HTTPException

client = anthropic.AsyncAnthropic(max_retries=3, timeout=60.0)     # async client (don't block FastAPI's event loop);
                                                                    # SDK retries 429/5xx/overloaded with backoff
app = FastAPI()

@app.post("/api/support/answer")
async def answer(q: Question, user=Depends(current_user)):
    await rate_limit(user.id, "support_llm", per_minute=10)          # your own per-user limit
    t0 = time.perf_counter()
    try:
        msg = await client.messages.create(
            model="claude-sonnet-5-5", max_tokens=600, temperature=0.2,
            system="You are QuickBite's support assistant. Be concise. If unsure, say so and offer human help.",
            messages=[{"role": "user", "content": q.text}],
            metadata={"user_id": hash_id(user.id)},                    # abuse tracking without PII
        )
    except anthropic.RateLimitError:
        raise HTTPException(503, "Busy, please retry shortly")
    except anthropic.APIStatusError as e:
        logging.warning("llm_error status=%s", e.status_code)
        raise HTTPException(502, "Assistant unavailable")
    log_usage(feature="support", tenant=user.tenant_id, model=msg.model,
              input_tokens=msg.usage.input_tokens, output_tokens=msg.usage.output_tokens,
              latency_ms=int((time.perf_counter() - t0) * 1000))
    text = "".join(b.text for b in msg.content if b.type == "text")
    return {"answer": text, "truncated": msg.stop_reason == "max_tokens"}
```

### Node: thin multi-provider gateway with model aliases & fallback
```js
import Anthropic from '@anthropic-ai/sdk';
import OpenAI from 'openai';
const anthropic = new Anthropic({ maxRetries: 2, timeout: 60_000 });
const openai = new OpenAI({ maxRetries: 2, timeout: 60_000 });

const ALIASES = {
  'support-default': [{ provider: 'anthropic', model: 'claude-sonnet-5-5' }, { provider: 'openai', model: process.env.OPENAI_FALLBACK_MODEL }],
  'classify-fast':   [{ provider: 'anthropic', model: 'claude-haiku-5-5' }],
  'deep-reasoning':  [{ provider: 'anthropic', model: 'claude-opus-5-5' }],
};

export async function complete(alias, { system, messages, maxTokens = 512, temperature = 0.2 }) {
  let lastErr;
  for (const target of ALIASES[alias]) {
    try {
      if (target.provider === 'anthropic') {
        const r = await anthropic.messages.create({ model: target.model, system, messages, max_tokens: maxTokens, temperature });
        return { text: r.content.filter((b) => b.type === 'text').map((b) => b.text).join(''), usage: r.usage, model: r.model };
      }
      const r = await openai.chat.completions.create({ model: target.model, max_completion_tokens: maxTokens, temperature,
        messages: [{ role: 'system', content: system }, ...messages] });
      return { text: r.choices[0].message.content ?? '', usage: r.usage, model: r.model };
    } catch (e) { lastErr = e; metrics.inc('llm_fallback', { alias, from: target.model }); }
  }
  throw lastErr;
}
```

### Vision: send an image (e.g., damaged-food complaint photo)
```python
import base64
img_b64 = base64.standard_b64encode(open("complaint.jpg", "rb").read()).decode()
msg = client.messages.create(model="claude-sonnet-5-5", max_tokens=300, messages=[{
    "role": "user", "content": [
        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64}},
        {"type": "text", "text": "Does this photo show spilled or damaged food packaging? Answer YES/NO and one line why."},
    ]}])
```

### Offline bulk jobs with the Message Batches API (cheaper, async)
```python
batch = client.messages.batches.create(requests=[
    {"custom_id": f"review-{r.id}", "params": {"model": "claude-haiku-5-5", "max_tokens": 50,
     "messages": [{"role": "user", "content": f"Sentiment (positive/neutral/negative) of: {r.text}"}]}}
    for r in reviews_batch])
# poll client.messages.batches.retrieve(batch.id) → when ended, iterate results and store sentiments
```

### Never call providers from the client — proxy via your API (RN)
```ts
// ✅ React Native talks to YOUR backend with user auth; backend holds provider keys & limits
const r = await http.post('/api/support/answer', { text: question });
```

---

## ⚫ Interview Questions + Answers

**Q1: How would you integrate an LLM API into a production backend?**
A1: Keep provider keys server-side in a secrets manager and expose your own authenticated endpoint with per-user and per-tenant rate limits. Call the provider via the official SDK with timeouts, bounded retries (exponential backoff and jitter for 429/5xx/overloaded) and streaming for long outputs. Log usage (tokens, latency, model, feature, tenant) for cost dashboards. Validate and post-process outputs. Add fallbacks (alternate model or provider, cached or graceful responses). Wrap it all in an internal LLM gateway with model aliases so product code doesn't depend on a single vendor.

**Q2: How do you choose between models like Haiku, Sonnet and Opus (or OpenAI equivalents)?**
A2: Build an evaluation set from real tasks and measure quality, latency and cost per model. Route simple, high-volume tasks (classification, extraction, short replies) to the fastest, cheapest tier, use the balanced tier for general assistants and RAG answers, and reserve the most capable tier for complex reasoning, coding and agentic workflows or for escalation when a cheaper model is uncertain. Revisit choices as new models ship, and use aliases for easy switching.

**Q3: How do you handle rate limits and provider outages?**
A3: Track limits for requests and tokens per minute. Enforce your own per-tenant quotas and concurrency upstream, queue non-interactive work, use batch APIs for bulk jobs, respect retry-after headers and back off with jitter. For outages or overload, use circuit breakers, fall back to alternate models or providers (same prompts tested on both), serve cached answers when appropriate, degrade gracefully ("assistant busy, here are help articles") and alert on rising error rates. Request limit increases ahead of known peaks.

**Q4: Why shouldn't mobile or web apps call the LLM provider directly?**
A4: The API key would be embedded in the client and trivially extractable, allowing anyone to use your account and run up costs or abuse it. You'd also lose server-side controls: authentication, per-user rate limits, prompt templates and guardrails, PII redaction, logging, cost attribution, caching and the ability to change models without app releases. Clients should call your backend, which calls the provider. Ephemeral, scoped tokens exist for specific realtime use cases but still need server issuance.

**Q5: What should you log for LLM calls, and what shouldn't you log?**
A5: Log request IDs, timestamps, feature and tenant, model and version, prompt template version, token counts (input, output, cached), latency (TTFT and total), stop reason, errors and retries, cost, and evaluation or feedback signals, so you can debug, attribute costs and run evals. Avoid storing raw sensitive data unnecessarily: redact PII and secrets, apply retention limits and access controls, and follow provider and regulatory data policies (DPDP Act), possibly sampling full prompts only in secure, access-controlled stores for debugging.

---

## 🔷 Trade-offs
✅ Hosted APIs: best models, no GPUs — ❌ cost per token, rate limits, data governance, vendor risk.
✅ Multi-provider gateway: resilience & leverage — ❌ prompt behaviour differs across models (needs evals per model).
✅ Cloud marketplaces (Bedrock/Vertex/Azure): compliance & billing — ❌ feature lag vs direct API sometimes.
✅ Batch APIs: ~50% cheaper — ❌ async (hours), not for interactive use.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Messages API | Claude chat endpoint | Claude का chat API |
| System prompt | Global instructions for the model | model के लिए मुख्य निर्देश |
| Content block | Typed piece of a message | संदेश का हिस्सा |
| stop_reason | Why generation stopped | क्यों रुका |
| max_tokens | Output token cap | जवाब की सीमा |
| Rate limit (429) | Too many requests/tokens | बहुत ज़्यादा requests |
| Overloaded (529) | Provider capacity issue | provider पर भार |
| Model routing | Pick model per task | काम के हिसाब से model |
| LLM gateway | Internal proxy for providers | providers के आगे अपना proxy |
| Batch API | Async discounted bulk calls | सस्ता async bulk |

---

## ⚡ 3-Line Summary
**English:**
1. Claude Messages API (system + messages + max_tokens → content blocks + usage + stop_reason) and OpenAI Chat/Responses APIs share concepts: roles, tools, streaming, structured output.
2. Production: server-side keys, timeouts, retries/backoff for 429/5xx/529, per-tenant limits, usage & cost logging, model routing by evals, fallbacks.
3. Wrap providers in an LLM gateway (aliases, quotas, caching, guardrails, logging); use batch APIs for bulk; never call providers from clients.

**Hindi:**
1. Claude Messages API और OpenAI APIs के concepts एक जैसे: roles, tools, streaming, structured output।
2. Production: keys सर्वर पर, timeout, 429/5xx पर backoff retry, सीमाएँ, tokens/ख़र्च का हिसाब, evals से model, fallback।
3. Providers के आगे LLM gateway; bulk के लिए batch API; client से कभी सीधे provider नहीं।

---

## ➡️ Next Topic Suggestion
**129. Prompt Engineering** — The same model can give poor or excellent results depending on the prompt. Next: writing clear system prompts, giving context, structuring with tags and examples, and iterating with evals.
