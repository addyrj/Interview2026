---

# 386. OpenAI SDK — Complete Guide
# हिंदी में: OpenAI SDK — पूरी Guide

---

## 🔵 Simple Definition (English)
The OpenAI Python SDK (`openai` package) is the official client for calling GPT-4o, GPT-4o-mini, text-embedding-3-small, DALL-E, and other OpenAI models. Key classes: `OpenAI` (sync) and `AsyncOpenAI` (async). Main operations: `chat.completions.create()` for text generation, `embeddings.create()` for vector embeddings, `images.generate()` for images. Always use `AsyncOpenAI` in FastAPI to avoid blocking the event loop.

## 🔵 सरल परिभाषा (Hindi)
OpenAI Python SDK GPT-4o, embeddings, DALL-E call करने का official client है। `OpenAI` (sync) और `AsyncOpenAI` (async) — FastAPI में `AsyncOpenAI` use करो। Main: `chat.completions.create()`, `embeddings.create()`, `images.generate()`।

---

## 💻 Code Example — Basic
```python
from openai import AsyncOpenAI
import os

# ─── Client setup ─────────────────────────────────────────────────
client = AsyncOpenAI(
    api_key=os.environ["OPENAI_API_KEY"],  # never hardcode!
    timeout=30.0,         # request timeout in seconds
    max_retries=3,        # auto-retry on 429/5xx
)

# ─── Chat completion (GPT-4o-mini) ───────────────────────────────
async def chat(user_message: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",   "content": user_message},
        ],
        temperature=0.7,      # 0=deterministic, 1=creative, 2=wild
        max_tokens=1000,      # max tokens in response
        top_p=1.0,            # nucleus sampling (leave at 1.0 usually)
    )
    return response.choices[0].message.content

# ─── Multi-turn conversation ──────────────────────────────────────
async def chat_with_history(messages: list[dict]) -> dict:
    """messages format: [{"role": "user/assistant/system", "content": "..."}]"""
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.5,
    )
    
    # Response message to add to history:
    assistant_message = response.choices[0].message
    return {
        "role": "assistant",
        "content": assistant_message.content,
    }

# Usage:
history = [{"role": "system", "content": "You are a tariff classification expert."}]
history.append({"role": "user", "content": "What is HS code for iPhones?"})
reply = await chat_with_history(history)
history.append(reply)   # maintain conversation

# ─── Token counting (avoid surprises) ────────────────────────────
import tiktoken

def count_tokens(messages: list[dict], model: str = "gpt-4o-mini") -> int:
    enc = tiktoken.encoding_for_model(model)
    total = 0
    for msg in messages:
        total += 4  # per-message overhead
        total += len(enc.encode(msg["content"]))
        total += len(enc.encode(msg["role"]))
    total += 2  # reply priming
    return total

# gpt-4o-mini context: 128K tokens ≈ ~300 pages of text
```

## 💻 Code Example — Advanced
```python
import asyncio
from openai import AsyncOpenAI
from pydantic import BaseModel
import json

client = AsyncOpenAI()

# ─── Streaming responses ──────────────────────────────────────────
async def chat_stream(user_message: str):
    """Stream tokens as they arrive — better UX for long responses."""
    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_message}],
        stream=True,     # ← enable streaming
    )
    
    async for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content   # yield each token

# FastAPI SSE streaming endpoint:
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/chat/stream")
async def stream_chat(query: str):
    async def generate():
        async for token in chat_stream(query):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

# ─── Structured output (JSON mode) ───────────────────────────────
class TariffClassification(BaseModel):
    hs_code: str
    description: str
    confidence: float
    reasoning: str

async def classify_product(product_description: str) -> TariffClassification:
    """Use Pydantic model for structured output — no manual JSON parsing."""
    response = await client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Classify products with HS tariff codes."},
            {"role": "user", "content": f"Classify: {product_description}"},
        ],
        response_format=TariffClassification,   # ← Pydantic model!
    )
    return response.choices[0].message.parsed   # TariffClassification object

# ─── Tool calling (function calling) ─────────────────────────────
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_tariff_database",
            "description": "Search the tariff database for HS codes matching a product",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Product search query"},
                    "limit": {"type": "integer", "description": "Max results", "default": 5},
                },
                "required": ["query"],
            },
        },
    }
]

async def agent_classify(product: str) -> str:
    messages = [{"role": "user", "content": f"What is the HS code for: {product}"}]
    
    while True:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        
        msg = response.choices[0].message
        messages.append(msg)   # add assistant message to history
        
        if response.choices[0].finish_reason == "stop":
            return msg.content    # final text response
        
        if response.choices[0].finish_reason == "tool_calls":
            for tool_call in msg.tool_calls:
                args = json.loads(tool_call.function.arguments)
                result = await search_tariff_database(**args)   # execute tool
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,   # MUST include this
                    "content": json.dumps(result),
                })

# ─── Embeddings ───────────────────────────────────────────────────
async def embed(text: str) -> list[float]:
    response = await client.embeddings.create(
        input=text,
        model="text-embedding-3-small",   # 1536 dims, $0.02/1M tokens
    )
    return response.data[0].embedding

# Batch embed (more efficient — one API call for many texts):
async def embed_batch(texts: list[str]) -> list[list[float]]:
    response = await client.embeddings.create(
        input=texts,          # list of strings (up to 2048)
        model="text-embedding-3-small",
    )
    return [item.embedding for item in response.data]

# ─── Cost tracking ────────────────────────────────────────────────
async def chat_with_cost(prompt: str) -> tuple[str, float]:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    
    usage = response.usage
    # gpt-4o-mini: $0.15/1M input tokens, $0.60/1M output tokens:
    cost = (usage.prompt_tokens * 0.15 + usage.completion_tokens * 0.60) / 1_000_000
    
    return response.choices[0].message.content, cost
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (AsyncOpenAI):
client = AsyncOpenAI()
response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}],
)
text = response.choices[0].message.content
```

```javascript
// JavaScript (openai npm):
import OpenAI from 'openai';
const client = new OpenAI();
const response = await client.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: "Hello" }],
});
const text = response.choices[0].message.content;
```

Key differences:
- API is identical (same endpoint, same params). SDK wrappers are very similar.
- Python: `AsyncOpenAI` for async. JS: always async (Promises).
- Python has `.beta.chat.completions.parse()` with Pydantic. JS needs manual JSON parsing.
- Python SDK: `max_retries` and `timeout` in constructor. JS: same options.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `OpenAI()` (sync) in FastAPI
```python
# Wrong — blocks event loop, kills performance:
client = OpenAI()   # sync client in async context

@app.post("/chat")
async def chat(q: str):
    response = client.chat.completions.create(...)   # BLOCKS!

# Correct:
client = AsyncOpenAI()

@app.post("/chat")
async def chat(q: str):
    response = await client.chat.completions.create(...)   # non-blocking
```

❌ Mistake 2: Not handling rate limit errors
```python
# Wrong — crashes on rate limit:
response = await client.chat.completions.create(...)

# Correct — use SDK's built-in retry (max_retries=3 in constructor):
# Or handle manually with exponential backoff:
from openai import RateLimitError
import asyncio

for attempt in range(3):
    try:
        response = await client.chat.completions.create(...)
        break
    except RateLimitError:
        await asyncio.sleep(2 ** attempt)
```

---

## 🧠 Tricky Interview Question

**Q**: GPT-4o vs GPT-4o-mini — when do you use which? What's the cost difference?

**Answer**: 
- **GPT-4o**: $2.50/1M input, $10/1M output. Use for: complex reasoning, code generation, nuanced analysis.
- **GPT-4o-mini**: $0.15/1M input, $0.60/1M output — **~17x cheaper on input, ~17x cheaper on output**. Use for: simple extraction, classification, summarization, high-volume operations.
- Rule: start with gpt-4o-mini, move to gpt-4o only when quality is insufficient. For RAG (retrieval + generation): gpt-4o-mini is usually fine. For agentic reasoning: gpt-4o may be needed.

---

## ⚫ Interview Questions + Answers

Q1: What is `temperature` and how does it affect output?
A1: Temperature controls randomness of token selection. 0 = deterministic (always picks highest probability token — same output every time). 0.7 = moderate creativity (good for conversational AI). 1.0 = more varied. 2.0 = very random/creative, may be incoherent. For classification/extraction: use 0. For creative writing: 0.7-1.0. For code generation: 0.2-0.4. Note: even at temperature=0, model can be non-deterministic due to parallel processing — not truly 100% reproducible.

Q2: What is the difference between `max_tokens` and context window?
A2: **Context window** = total tokens the model can "see" at once: input + output. GPT-4o-mini: 128K tokens ≈ 100K words. **max_tokens** = maximum tokens in the **response** (output only). If you don't set it, model uses its default (usually 4096). If your prompt is 10K tokens and max_tokens=5000, you need a 15K+ context window. Always estimate your prompt tokens with `tiktoken` before sending to avoid truncation.

Q3: What is structured output and when should you use it over prompt-based JSON?
A3: Structured output (`response_format=PydanticModel` with `.beta.chat.completions.parse()`) guarantees the model returns valid JSON matching your schema — no parsing errors, no hallucinated fields. Prompt-based JSON (`"Return as JSON: {field: value}"`) can fail (invalid JSON, missing fields, extra text). Use structured output when: you need reliable machine-readable output, schema is known in advance, or JSON parsing failures would break your app. For exploration/chat: plain text is fine.

Q4: How does tool calling (function calling) work?
A4: (1) Send messages + tool definitions (JSON schemas). (2) Model returns `finish_reason="tool_calls"` with tool name + arguments. (3) You execute the tool with those arguments. (4) Send result back as `{"role": "tool", "tool_call_id": "...", "content": "result"}`. (5) Model returns final text response. MUST include `tool_call_id` in step 4. Loop continues until `finish_reason="stop"`. Model never actually executes tools — it just tells you what to call.

Q5: How do you handle streaming in FastAPI?
A5: Use `StreamingResponse` with an async generator. Set `stream=True` in `client.chat.completions.create()`. Iterate chunks with `async for chunk in stream:`. Yield Server-Sent Events (SSE) format: `yield f"data: {json.dumps({'token': token})}\n\n"`. Send `data: [DONE]\n\n` at end. On client: use `EventSource` (JS) or `httpx` async streaming (Python). For mobile/app clients: Vercel AI SDK handles SSE parsing automatically.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AsyncOpenAI | Async client for FastAPI | FastAPI के लिए async client |
| temperature | Output randomness (0-2) | Output की randomness |
| max_tokens | Max response length | Response की max length |
| stream | Return tokens as generated | Tokens आते आते return |
| tool_calls | Function calling mechanism | Function calling |
| response_format | Structured JSON output | Structured JSON output |
| tiktoken | Token counting library | Tokens count करना |

---

## ⚡ 3-Line Summary
English: Use `AsyncOpenAI` in FastAPI — never the sync `OpenAI` client. Use `gpt-4o-mini` for cost-efficiency (17x cheaper), `gpt-4o` only when quality requires it. Use structured output (`.beta.chat.completions.parse()`) over prompt-based JSON for reliable machine-readable responses.
Hindi: FastAPI में `AsyncOpenAI` use करो। Cost के लिए `gpt-4o-mini` (17x सस्ता), quality चाहिए तो `gpt-4o`। Reliable JSON के लिए `.beta.chat.completions.parse()` use करो।

---

## ➡️ Next Topic
**387. Anthropic SDK** — Claude API, Messages API, system prompts. **388. LangChain** — chains, LCEL, retrieval chains. **396. tiktoken** — token counting and cost estimation.
