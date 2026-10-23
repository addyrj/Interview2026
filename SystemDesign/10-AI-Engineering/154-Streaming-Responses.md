# 154. Streaming Responses
# हिंदी में: Streaming Responses — LLM का पूरा जवाब बनने का इंतज़ार किए बिना शब्द-दर-शब्द (token-by-token) यूज़र तक भेजना: provider के SSE events → आपका backend → web और React Native ऐप; बीच में रुकवाना (cancel), tools के साथ status दिखाना, guardrails और proxy की सेटिंग

---

## 🔵 Simple Definition (English)
**Streaming** sends the model's output **incrementally as it's generated**, instead of waiting for the full response. LLMs decode token by token, so a 300-token answer may take 3–6 s to complete, but the **first token arrives in a few hundred milliseconds**. Streaming shows text immediately, making the app feel much faster (better **time-to-first-token**, TTFT) and letting users **stop** generation early.
End to end:
1. **Provider → backend**: provider APIs stream **Server-Sent Events** (Anthropic: `message_start`, `content_block_delta` with `text_delta` or `input_json_delta` for tool input, `message_delta` with stop reason and usage, `message_stop`). SDKs expose helpers such as `messages.stream()` and `text_stream`.
2. **Backend → client**: relay as **SSE** (`text/event-stream`), chunked HTTP, or WebSocket (e.g., FastAPI `StreamingResponse`, Express `res.write`, Next.js route handlers returning a `ReadableStream`, or the Vercel AI SDK `streamText` + `useChat`).
3. **Client rendering**: append deltas, render Markdown incrementally and safely, show status for tool calls ("Checking your order…"), handle errors and reconnection, and **cancel** via `AbortController`.
Infrastructure must **not buffer** (Nginx `proxy_buffering off`, no gzip on SSE) and must allow **long idle timeouts** (load balancers).

## 🔵 सरल परिभाषा (Hindi)
Streaming = model का जवाब पूरा होने का इंतज़ार किए बिना, बनते-बनते भेजना। LLM एक-एक token बनाता है — 300 tokens के जवाब में 3–6 सेकंड, पर पहला token कुछ सौ ms में; streaming से text तुरंत दिखता है (बेहतर TTFT) और यूज़र बीच में रोक सकता है।
पूरा रास्ता: (1) provider → backend: SSE events (Anthropic में `content_block_delta` में text या tool input के टुकड़े, `message_delta` में stop reason/usage), SDK के `messages.stream()`/`text_stream`; (2) backend → client: SSE, chunked HTTP या WebSocket (FastAPI StreamingResponse, Next.js ReadableStream, Vercel AI SDK); (3) client: टुकड़े जोड़ो, Markdown सुरक्षित दिखाओ, tool चलते समय status ("आपका order देख रहे हैं…"), errors, AbortController से cancel। Proxy buffering बंद और load balancer का idle timeout लंबा।

---

## 🔴 Problem it Solves
Without streaming:
- Users stare at a spinner for 5–15 s (long answers, agents with tools), assume the app is broken and retry, doubling cost, or leave.
- On mobile networks, a long wait plus a timeout means a lost answer.
- Users can't stop a wrong or long answer early, so you pay for every token.
- Agents seem frozen while they call tools.
Streaming improves **perceived latency** dramatically. Users start reading within ~1 s, and the total time matters less. It's the standard UX for chat assistants. But streaming adds engineering concerns: **proxy buffering, timeouts, cancellation, partial Markdown, mid-stream errors, guardrails on partial output, mobile support and reconnection**.

## 🔴 यह क्यों बना? (Hindi)
बिना streaming के: यूज़र 5–15 सेकंड spinner देखता है (लंबे जवाब, tools वाले agents), सोचता है ऐप टूटा, दोबारा भेजता है (दोगुना ख़र्च) या चला जाता है; mobile नेटवर्क पर लंबा इंतज़ार + timeout = जवाब ग़ायब; ग़लत/लंबा जवाब बीच में रोक नहीं सकते — हर token का पैसा; tools चलाते agent अटके लगते हैं।
Streaming से महसूस होने वाली देर बहुत घटती है — ~1 सेकंड में पढ़ना शुरू; chat assistants का मानक UX; पर नई engineering चिंताएँ — proxy buffering, timeouts, cancel, अधूरा Markdown, बीच में error, अधूरे output पर guardrails, mobile और reconnection।

---

## 🟢 How it Works — Step by Step

### End-to-end pipeline

```
Client (web/RN)                 Backend (FastAPI/Node)                      Provider (Claude API)
  POST /api/chat (SSE accept) ──►  auth, guards, retrieval, prompt
                                   messages.stream(...) ───────────────────►  SSE: message_start
  ◄── event: status "searching"                                           ◄── content_block_delta (text_delta "Your")
  ◄── event: delta {"t":"Your"}  ◄── relay each delta immediately          ◄── content_block_delta (" refund")
  ◄── event: delta {"t":" refund"}                                         ◄── … message_delta (stop_reason, usage)
  ◄── event: done {sources, usage, run_id}  ◄── post-checks (citations)    ◄── message_stop
User taps "Stop" → AbortController.abort() → connection closes → backend detects disconnect → cancels
provider stream (stop paying for more output tokens)
```

### Anthropic streaming event types (what you handle)

```
message_start            → message id, model, input usage
content_block_start      → type: text | tool_use (name, id)
content_block_delta      → text_delta {text} | input_json_delta {partial_json} (tool arguments stream)
content_block_stop       → block finished (tool_use input complete → execute tool)
message_delta            → stop_reason (end_turn | tool_use | max_tokens), output usage
message_stop             → done ; ping events keep connection alive ; error events possible mid-stream
SDK helpers: client.messages.stream(...) → text_stream iterator, get_final_message()
```

### Infrastructure checklist (most streaming bugs live here)

```
Nginx/ingress: proxy_buffering off; proxy_cache off; X-Accel-Buffering: no; disable gzip for event-stream
Load balancer idle timeout > longest stream (AWS ALB default 60 s → raise, e.g., 300 s); send heartbeats
  (": ping\n\n" comment lines every 15 s) to keep connections alive through proxies
HTTP/1.1 browsers limit ~6 connections per origin → use HTTP/2 or a single shared stream per tab
Serverless: ensure the platform supports response streaming (and its time limits)
Backpressure: don't buffer whole response server-side; write each chunk & flush
```

### Tools + streaming

```
Model streams text → decides tool_use → stream stops with stop_reason=tool_use
Backend executes tool (send client a status event: "Checking order 4521…") → sends tool_result → new
streaming call → continues text. UI shows progress steps, not silence.
Stream tool arguments (input_json_delta) only if you need live UI (e.g., showing a SQL query being drafted)
```

### Guardrails & citations with streaming

```
Options:
  a) Stream immediately, run lightweight per-sentence checks (PII, banned phrases); if a violation
     appears, stop the stream and replace with a safe message (UI retracts) — fast, small risk window
  b) Buffer by sentence/paragraph, check, then flush — slight delay, safer for regulated content
  c) Generate fully, then stream the verified text (simulated streaming) for high-stakes answers
Citations: validate [S#] at the end → send a final "done" event with verified sources list
```

### Client rendering

```
Append deltas to state with throttling (requestAnimationFrame / 30–60 ms batches) to avoid re-render per token
Incremental Markdown: tolerate unclosed code fences/lists; sanitize HTML (XSS — never inject raw HTML)
Accessibility: aria-live="polite" region, but avoid announcing every token (announce on completion)
States: connecting → streaming → tool-running → done | stopped | error (offer Retry)
Reconnection: if stream drops, either restart (idempotent request id) or resume from a server-side buffer
  (generation runs in background & writes to Redis stream; client reconnects with last event id)
```

### React Native specifics

```
RN's classic fetch doesn't expose response.body streams on all setups → use:
  - Expo SDK 52+ `expo/fetch` (streaming ReadableStream support), or
  - react-native-sse (EventSource polyfill), or WebSocket
Keep screen awake during long answers; handle app background (stream may be killed → resume/refetch final)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Client `POST /api/chat` → backend auth, guards, retrieval, prompt → `messages.stream()` → provider के हर `text_delta` को तुरंत client को आगे भेजो (event: delta) → अंत में `done` event (sources, usage, run_id); यूज़र "Stop" दबाए → AbortController → कनेक्शन बंद → backend provider stream भी रद्द करे (आगे के tokens का पैसा नहीं)।
2. Anthropic events: message_start, content_block_start (text या tool_use), content_block_delta (text_delta या tool input का input_json_delta), content_block_stop, message_delta (stop_reason, usage), message_stop, बीच में ping/error; SDK में `text_stream`।
3. Infrastructure (ज़्यादातर bugs यहीं): Nginx `proxy_buffering off`, `X-Accel-Buffering: no`, event-stream पर gzip बंद; load balancer idle timeout बढ़ाओ (ALB default 60 s) और हर 15 सेकंड heartbeat; HTTP/2; हर chunk तुरंत flush।
4. Tools: model tool_use पर रुकता है → backend tool चलाए और client को status ("order 4521 देख रहे हैं…") → tool_result के साथ नई streaming call; guardrails — या तो stream करते हुए वाक्य-दर-वाक्य जाँच (गड़बड़ी पर रोककर सुरक्षित संदेश), या वाक्य/अनुच्छेद buffer करके जाँच फिर भेजो, या ज़्यादा जोखिम पर पूरा बनाकर जाँचो फिर दिखाओ; citations अंत में जाँचकर `done` में।
5. Client: हर token पर re-render नहीं — 30–60 ms में batch; अधूरा Markdown सहन करो, HTML sanitize (XSS); aria-live पर पूरा होने पर घोषणा; states (connecting, streaming, tool चल रहा, done/stopped/error + Retry); कनेक्शन टूटे तो idempotent दोबारा या server buffer से resume; RN में `expo/fetch` (SDK 52+), react-native-sse या WebSocket।

---

## 🟡 Real World Example

**ChatGPT / Claude.ai** — popularized token-streaming chat UX with a stop button. Both providers' APIs stream via SSE, and their apps show tool or "thinking" progress indicators, setting user expectations that AI responses start appearing almost instantly.

**Vercel AI SDK** — widely used to stream LLM responses in Next.js and React (`streamText` on the server, `useChat` on the client), handling SSE parsing, tool-call streaming and cancellation. It shows how common the pattern is in web stacks.

**Infrastructure gotchas in production** — teams frequently discover that Nginx buffering, CDN or proxy compression, or load-balancer idle timeouts (e.g., the AWS ALB 60-second default) break streaming in production even though it worked locally. Disabling buffering and adding heartbeats is a standard fix.

**Mobile streaming** — React Native teams historically used WebSockets or SSE polyfills because fetch streaming wasn't available. Expo's newer fetch implementation added streaming support, simplifying AI chat features in RN apps.

## 🟡 Real Example Hindi में
ChatGPT/Claude.ai ने stop बटन वाला token-streaming chat UX लोकप्रिय किया — दोनों के APIs SSE से stream करते हैं और ऐप tools/"सोच" का progress दिखाते हैं; Vercel AI SDK (`streamText` + `useChat`) Next.js/React में streaming, tool-call streaming और cancel संभालता है।
Production में अक्सर पता चलता है कि Nginx buffering, CDN compression या ALB का 60 सेकंड idle timeout streaming तोड़ देता है (local में ठीक चलता था) — buffering बंद + heartbeats आम इलाज; RN में पहले WebSocket या SSE polyfills, अब Expo का नया fetch streaming देता है।

---

## 🟠 My Stack Example

### FastAPI: relay Claude stream as SSE with status events, heartbeats & cancellation
```python
import anthropic, asyncio, json
from fastapi import Request
from fastapi.responses import StreamingResponse
aclient = anthropic.AsyncAnthropic()

def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

@app.post("/api/chat")
async def chat(body: ChatIn, request: Request, user=Depends(current_user)):
    async def gen():
        yield sse("status", {"text": "Searching help articles…"})
        sources = await retrieve_for(body.question, user)                       # RAG (Topic 137)
        full, usage = "", None
        async with aclient.messages.stream(model="claude-sonnet-5-5", max_tokens=600, system=SUPPORT_SYSTEM_V7,
                                           messages=build_messages(sources, body.question)) as stream:
            last_beat = asyncio.get_event_loop().time()
            async for text in stream.text_stream:
                if await request.is_disconnected():                             # user pressed Stop / closed app
                    await stream.close(); return                                # stop paying for more tokens
                full += text
                if contains_blocked_pattern(full):                              # lightweight streaming guard
                    yield sse("replace", {"text": SAFE_FALLBACK}); return
                yield sse("delta", {"t": text})
                now = asyncio.get_event_loop().time()
                if now - last_beat > 15: yield ": ping\n\n"; last_beat = now     # keep proxies alive
            usage = (await stream.get_final_message()).usage
        yield sse("done", {"sources": validated_citations(full, sources), "usage": {"in": usage.input_tokens, "out": usage.output_tokens}})
    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
```

### Nginx config for SSE
```nginx
location /api/chat {
  proxy_pass http://ai_backend;
  proxy_http_version 1.1;
  proxy_set_header Connection "";
  proxy_buffering off;          # flush each chunk
  proxy_cache off;
  gzip off;                     # compression buffers SSE
  proxy_read_timeout 300s;      # long streams
}
```

### Next.js client: parse SSE with fetch + AbortController, throttled rendering
```tsx
'use client';
export function useStreamingChat() {
  const [text, setText] = useState(''); const [status, setStatus] = useState<'idle' | 'streaming' | 'done' | 'stopped' | 'error'>('idle');
  const ctrl = useRef<AbortController>(); const buffer = useRef('');

  async function send(question: string) {
    ctrl.current = new AbortController(); setText(''); setStatus('streaming'); buffer.current = '';
    const flush = setInterval(() => { if (buffer.current) { const b = buffer.current; buffer.current = ''; setText((t) => t + b); } }, 40);
    try {
      const res = await fetch('/api/chat', { method: 'POST', body: JSON.stringify({ question }), headers: { 'Content-Type': 'application/json' }, signal: ctrl.current.signal });
      const reader = res.body!.pipeThrough(new TextDecoderStream()).getReader();
      let pending = '';
      for (;;) {
        const { value, done } = await reader.read(); if (done) break;
        pending += value; const frames = pending.split('\n\n'); pending = frames.pop()!;
        for (const f of frames) {
          if (f.startsWith(':')) continue;                                     // heartbeat
          const event = /event: (\w+)/.exec(f)?.[1]; const data = JSON.parse(/data: (.*)/s.exec(f)?.[1] ?? '{}');
          if (event === 'delta') buffer.current += data.t;
          if (event === 'replace') { buffer.current = ''; setText(data.text); }
          if (event === 'done') setStatus('done');
        }
      }
    } catch (e: any) { setStatus(e.name === 'AbortError' ? 'stopped' : 'error'); }
    finally { clearInterval(flush); if (buffer.current) setText((t) => t + buffer.current); }
  }
  return { text, status, send, stop: () => ctrl.current?.abort() };
}
```

### React Native (Expo): streaming with expo/fetch
```ts
import { fetch } from 'expo/fetch';                         // Expo SDK 52+: supports streaming response bodies
export async function streamChat(question: string, onDelta: (t: string) => void, signal: AbortSignal) {
  const res = await fetch(`${API}/api/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${session.access()}` },
                                               body: JSON.stringify({ question }), signal });
  const reader = res.body!.getReader(); const dec = new TextDecoder(); let pending = '';
  for (;;) {
    const { value, done } = await reader.read(); if (done) break;
    pending += dec.decode(value, { stream: true });
    const frames = pending.split('\n\n'); pending = frames.pop()!;
    for (const f of frames) if (f.includes('event: delta')) onDelta(JSON.parse(f.split('data: ')[1]).t);
  }
}
```

### Resumable generation via Redis Streams (for flaky mobile networks)
```python
async def generate_to_buffer(req_id, messages):            # background task writes chunks
    async with aclient.messages.stream(model="claude-sonnet-5-5", max_tokens=600, messages=messages) as s:
        async for t in s.text_stream:
            await redis.xadd(f"gen:{req_id}", {"t": t}, maxlen=5000)
    await redis.xadd(f"gen:{req_id}", {"done": "1"}); await redis.expire(f"gen:{req_id}", 600)

@app.get("/api/chat/{req_id}/stream")                       # client reconnects with Last-Event-ID
async def resume(req_id: str, request: Request):
    last = request.headers.get("last-event-id", "0-0")
    async def gen():
        nonlocal last
        while True:
            for _, entries in await redis.xread({f"gen:{req_id}": last}, block=15000, count=100) or []:
                for eid, fields in entries:
                    last = eid
                    if fields.get("done"): yield f"id: {eid}\nevent: done\ndata: {{}}\n\n"; return
                    yield f"id: {eid}\nevent: delta\ndata: {json.dumps({'t': fields['t']})}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream", headers={"X-Accel-Buffering": "no"})
```

---

## ⚫ Interview Questions + Answers

**Q1: Why stream LLM responses and how does it work?**
A1: LLMs generate tokens sequentially, so full responses take seconds, but the first token arrives quickly. Streaming forwards tokens as they're produced, cutting perceived latency (time to first token), keeping users engaged and enabling early cancellation to save cost. The provider streams SSE events (deltas plus a final stop reason and usage). The backend consumes them via the SDK and relays deltas to the client over SSE, chunked HTTP or WebSockets, flushing each chunk. The client appends deltas, renders progressively and handles completion, errors and stop.

**Q2: What infrastructure issues break streaming in production?**
A2: Reverse proxies or ingress buffering responses (Nginx `proxy_buffering`), compression middleware or CDNs buffering event streams, load-balancer or proxy idle timeouts closing long connections (raise them and send heartbeat comments), serverless platforms without response streaming or with short limits, HTTP/1.1 connection limits in browsers, and application frameworks that accumulate the whole response before sending. Fix with `X-Accel-Buffering: no`, disabled buffering and gzip for SSE, longer timeouts and periodic pings.

**Q3: How do you handle cancellation?**
A3: The client aborts the request (AbortController in browsers, a closed connection in RN) when the user taps Stop or navigates away. The server detects the disconnect (e.g., `request.is_disconnected()` in FastAPI, or the `close` event in Node), stops iterating and closes the provider stream so generation and billing stop, and records the partial output and usage. With background generation (resumable streams), an explicit cancel endpoint stops the job.

**Q4: How do you apply guardrails and citations when streaming?**
A4: Choose based on risk. For low-risk chat, stream immediately while running lightweight incremental checks (PII patterns, banned phrases, policy markers) on accumulated text, stopping and replacing the output if a violation appears. For moderate risk, buffer and check per sentence or paragraph before flushing. For high-stakes answers, generate fully, verify (claims, citations, commitments), then send the verified text, possibly with simulated streaming. Validate citations at the end and send the verified source list in a final "done" event.

**Q5: How do you stream responses that involve tool calls?**
A5: When the model decides to use a tool, its stream ends with stop reason `tool_use` (with the tool arguments streamed as JSON deltas). The backend executes the tool, sending the client a status event ("Checking your order…") so the UI isn't silent, then calls the model again with the tool result and streams the continuing text. For multi-step agents, emit step events (searching, calling payments API, drafting answer) and keep the connection alive with heartbeats, and enforce step and time budgets so streams don't hang.

---

## 🔷 Trade-offs
✅ Streaming: much better perceived latency, early stop — ❌ more complex infra & client code.
✅ Immediate streaming with incremental guards: fast — ❌ brief window where unsafe text may show.
✅ Buffer-then-verify: safer — ❌ slower first visible text.
✅ SSE: simple, HTTP-friendly — ❌ one-way; WebSocket: bidirectional — ❌ more infra/state.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Streaming | Send output incrementally | बनते-बनते भेजना |
| TTFT | Time to first token | पहला token आने का समय |
| SSE | Server-Sent Events | सर्वर से events की धारा |
| Delta | Incremental chunk of output | output का छोटा टुकड़ा |
| Proxy buffering | Proxy holds response until done | proxy का रोककर रखना |
| Heartbeat / ping | Keep-alive message | कनेक्शन ज़िंदा रखने का संदेश |
| AbortController | Cancel fetch in JS | fetch रद्द करना |
| Backpressure | Flow control for streams | धारा का नियंत्रण |
| Resumable stream | Continue after reconnect | दोबारा जुड़कर आगे |
| Incremental Markdown | Render partial Markdown safely | अधूरा Markdown दिखाना |

---

## ⚡ 3-Line Summary
**English:**
1. Stream provider SSE deltas through your backend (flush each chunk) to clients via SSE/WebSocket for fast TTFT and early stop.
2. Fix infra: no proxy buffering/gzip on SSE, long LB timeouts + heartbeats; handle disconnects to cancel provider streams and save tokens.
3. Handle tools (status events), guardrails (incremental or buffered checks), citations at the end, throttled safe rendering, and RN via expo/fetch, SSE polyfills or WebSocket.

**Hindi:**
1. Provider के SSE deltas backend से तुरंत client तक — तेज़ TTFT और बीच में रोकना।
2. Infra: proxy buffering/gzip बंद, लंबे timeouts + heartbeat; disconnect पर provider stream रद्द।
3. Tools पर status, guardrails (चलते-चलते या buffer से), अंत में citations, सुरक्षित rendering, RN में expo/fetch या SSE/WebSocket।

---

## ➡️ Next Topic Suggestion
**155. Deploy AI App (Docker + AWS)** — The final AI topic: packaging an AI service (API, workers, vector DB, cache) with Docker and deploying it on AWS with CI/CD, secrets, scaling, streaming-friendly load balancing, and data residency in India.
