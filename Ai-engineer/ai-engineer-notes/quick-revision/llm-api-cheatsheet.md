---

# LLM API Cheatsheet — Phases 00-03 (Quick Revision)
# हिंदी में: LLM APIs, Prompting, Structured Output का Quick Revision

Condensed from topics 001-100: foundation (Python/FastAPI), LLM APIs, prompt engineering, structured output. Each topic: gist, one key code line, Hindi hint.
> Prices, model names and IDs shown in the source notes are illustrative; always verify on the provider's official pricing/model pages.

---

## Phase 00 — Foundation: Python + FastAPI (001-020)

- **001 Python async/await — Complete Guide** — `async`/`await` lets one thread serve many waiting LLM calls. Use `gather` with a semaphore, timeouts and retries; never block the loop. It saves time, not tokens.
  हिंदी: `async`/`await` से एक thread कई waiting LLM calls संभालता है। `gather` के साथ semaphore, timeout और retry लगाओ; loop को कभी block मत करो।
- **002 Python Decorators for AI Apps** — A decorator wraps a function to add retry, timing, caching or logging without touching its body. Use `functools.wraps` and async-aware wrappers. Good caching and retry decorators cut tokens and failures.
  हिंदी: Decorator function की body बदले बिना उसमें retry, timing, caching या logging जोड़ता है। `functools.wraps` और async wrappers use करो।
- **003 Python Classes + OOP for LangChain** — Classes bundle state and behaviour; ABCs define contracts so parts are swappable. LangChain extension points (retriever, callback, tool) are classes. Prefer composition, Pydantic at boundaries, and never share mutable class attributes.
  `clf = RuleClassifier({'phone': '8517', 'shoe': '6403'})` · हिंदी: Classes state और behaviour को जोड़ती हैं; ABC contract देकर parts बदलना आसान करता है। LangChain के extension points classes हैं।
- **004 Python Type Hints for AI Code** — Type hints document code and let tools check it, but Python does not enforce them at runtime. Pydantic, FastAPI and LangChain turn hints into validation and JSON schemas. Always validate LLM output at the boundary.
  हिंदी: Type hints code document करते हैं और tools उन्हें check करते हैं, पर Python runtime पर enforce नहीं करता।
- **005 Python Error Handling in AI Apps** — Catch specific exceptions, retry only transient failures with backoff and jitter, and validate LLM output. Always have a fallback and map errors to correct HTTP codes. Retries cost tokens, so cap them.
  हिंदी: Specific exceptions पकड़ो, सिर्फ़ transient failures को backoff और jitter से retry करो, और LLM output validate करो।
- **006 Python List Comprehensions + Generators for Data Processing** — Comprehensions build lists concisely; generators produce items lazily with constant memory. Chain generators to stream, clean, dedupe and batch large datasets before calling LLM or embedding APIs. Remember generators are single-use.
  `chapter_85 = [c for c in codes if c.startswith('85')]` · हिंदी: Comprehensions छोटे code में list बनाती हैं; generators constant memory में items lazily देते हैं।
- **007 FastAPI Route Creation** — A route maps method + URL to a function, and FastAPI uses type hints to validate input and build docs. Use `async def` for non-blocking I/O, keep routes thin, and bound inputs to control tokens. Group routes with `APIRouter`.
  `app = FastAPI(title='Tariff API')` · हिंदी: Route method + URL को function से जोड़ता है, और FastAPI type hints से input validate और docs बनाता है।
- **008 FastAPI Pydantic Models** — Pydantic models validate and convert data for requests, responses and LLM output. FastAPI returns 422 on bad input and filters output with `response_model`. Keep separate In/Out models, bound every field, and reuse models as LLM schemas.
  `ok = ClassifyRequest(description='Android phone', declared_value='199.5')` · हिंदी: Pydantic models requests, responses और LLM output का data validate और convert करते हैं।
- **009 FastAPI Dependency Injection** — `Depends` lets routes receive shared resources (LLM client, DB session, user) built and cleaned up by FastAPI. Create expensive clients once in `lifespan`, use `yield` for cleanup, and override dependencies in tests.
  `app = FastAPI()` · हिंदी: `Depends` से routes को shared resources (LLM client, DB session, user) मिलते हैं जिन्हें FastAPI बनाता और साफ़ करता है।
- **010 FastAPI Background Tasks** — BackgroundTasks run functions after the response is sent, ideal for logs and usage tracking. They are in-process and not durable, so long or critical jobs need a real queue. Always catch and log errors inside tasks.
  `app = FastAPI()` · हिंदी: BackgroundTasks response भेजने के बाद functions चलाते हैं, logs और usage tracking के लिए बढ़िया।
- **011 FastAPI Error Responses** — Use correct status codes (422, 429, 413, 502, 504) with one consistent JSON error shape and a request id. Register handlers for your own exceptions, validation errors and a catch-all that never leaks details. Early 4xx rejections save tokens.
  `app = FastAPI()` · हिंदी: सही status codes (422, 429, 413, 502, 504) के साथ एक जैसा JSON error shape और request id दो।
- **012 FastAPI Async Routes** — Use `async def` with async clients for I/O-bound AI routes and `gather` for independent calls. Never block the event loop; use `to_thread` or workers for blocking and CPU work. Add timeouts and semaphores to stay safe under load.
  `app = FastAPI()` · हिंदी: I/O-bound AI routes के लिए async clients के साथ `async def` लो और independent calls के लिए `gather`।
- **013 FastAPI Streaming Responses** — Streaming sends LLM tokens to the client as they are generated, giving a fast first token. Use an async generator with `StreamingResponse` and SSE, validate before streaming, and send errors as events.
  `app = FastAPI()` · हिंदी: Streaming में LLM tokens बनते ही client को भेजे जाते हैं, इसलिए पहला token जल्दी मिलता है।
- **014 FastAPI + PostgreSQL (asyncpg)** — Use asyncpg with a pool created once in `lifespan`, borrow connections per request, and always use `$1` parameters. Keep transactions short and never hold a connection during an LLM call. Store usage and results to audit, cache and bill.
  हिंदी: `lifespan` में एक बार pool बनाकर asyncpg use करो, हर request में connection उधार लो, और हमेशा `$1` parameters लगाओ।
- **015 FastAPI + Redis Integration** — Use `redis.asyncio` with a client created in `lifespan` for caching LLM answers, atomic rate limits and token budgets. Version your keys, set TTLs, and decide fail-open or fail-closed. A cache hit costs zero tokens.
  हिंदी: `lifespan` में बने `redis.asyncio` client से LLM answers cache करो, atomic rate limits और token budgets लगाओ।
- **016 FastAPI Project Structure for AI** — Split an AI service into api, services, llm, repositories, schemas and core, with dependencies pointing inward. Use an app factory, settings from env and versioned prompts. This makes tests cheap and model or prompt changes safe.
  `app = FastAPI()` · हिंदी: AI service को api, services, llm, repositories, schemas और core में बाँटो, dependencies अंदर की ओर रखो।
- **017 FastAPI Middleware** — Middleware wraps every request to add request ids, logging, CORS, size limits and auth in one place. The last added runs first, so order carefully (CORS outside auth). Use pure ASGI middleware for streaming and dependencies for route-specific logic.
  `app = FastAPI()` · हिंदी: Middleware हर request को लपेटकर request id, logging, CORS, size limits और auth एक जगह जोड़ता है।
- **018 FastAPI Testing** — Test FastAPI apps with `TestClient` or `httpx.AsyncClient` and replace the LLM, DB and cache using `dependency_overrides`. Fakes make tests fast, free and deterministic; separate evaluation sets measure real model quality.
  `app = FastAPI()` · हिंदी: FastAPI apps को `TestClient` या `httpx.AsyncClient` से test करो और `dependency_overrides` से LLM, DB, cache बदलो।
- **019 PostgreSQL Async Queries** — Use asyncpg with `$` parameters, the right fetch method, bulk COPY/executemany for writes, and keyset pagination for big tables. Use transactions and row locks for race-free budgets, and separate pooled connections for parallel queries.
  हिंदी: asyncpg में `$` parameters, सही fetch method, writes के लिए bulk COPY/executemany और बड़ी tables के लिए keyset pagination use करो।
- **020 Connection Pooling in FastAPI** — Create DB, Redis and HTTP pools once per process in `lifespan`, with size limits, acquire timeouts and shared clients. Hold a connection only for the milliseconds you need it, never during an LLM call.
  हिंदी: DB, Redis और HTTP pools `lifespan` में प्रति process एक बार बनाओ, size limits, acquire timeouts और shared clients के साथ।

**Key snippet — 001 Python async/await — Complete Guide**
```python
async def classify(product: str) -> str:
    await asyncio.sleep(1)
    return f'{product} -> HS 8517'
```

**Key snippet — 005 Python Error Handling in AI Apps**
```python
try:
    raise ValueError('context too long')
except ValueError as err:
    print('handled:', err)
```

**Key snippet — 009 FastAPI Dependency Injection**
```python
app = FastAPI()
def get_api_key(x_api_key: str=Header(default='')) -> str:
    if x_api_key != 'secret':
        raise HTTPException(status_code=401, detail='bad api key')
    return x_api_key
```

**Key snippet — 013 FastAPI Streaming Responses**
```python
app = FastAPI()
async def fake_llm_stream(prompt: str) -> AsyncIterator[str]:
    for token in ['Smart', 'phones', ' fall', ' under', ' 8517.']:
        await asyncio.sleep(0.05)
        yield token
```

---

## Phase 01 — LLM APIs (021-050)

- **021 What is an LLM — How it Works** — An LLM is a transformer neural network trained to predict the next token — scaled to billions of parameters, it develops emergent reasoning abilities. It generates responses token by token until a stop condition.
  `client = OpenAI()` · हिंदी: LLM transformer neural network है — billions of parameters से emergent reasoning आती है। Token-by-token response generate होता है।
- **022 Tokens — Complete Guide** — Tokens are subword units (~4 chars each) — the currency of LLM APIs. Count with `tiktoken` before sending large documents to avoid silent truncation and unexpected costs.
  `enc = tiktoken.encoding_for_model('gpt-4o-mini')` · हिंदी: Tokens LLM API की currency हैं (~4 chars each)। Large documents भेजने से पहले `tiktoken` से count करो।
- **023 Context Window — What it Means** — The context window is the total token limit for input plus output in one request. Count tokens, reserve room for the answer, and trim or retrieve instead of stuffing everything. Bigger windows cost more and do not guarantee better answers.
  हिंदी: Context window एक request में input + output tokens की कुल limit है।
- **024 Temperature + Top-p + Top-k** — Temperature, top-p, and top-k control how the model samples the next token. Use 0 for classification and extraction, and 0.7 to 1.0 for creative text. Tune only one of temperature or top-p, and never assume zero means perfectly deterministic.
  `probs = softmax(logits, 1.0)` · हिंदी: Temperature, top-p और top-k तय करते हैं कि model अगला token कैसे चुने।
- **025 OpenAI API — Complete Guide** — The OpenAI API gives pay-per-token access to chat, embeddings, audio, and moderation models. Use one reusable client, keep the key in the environment, and always handle errors and log `usage`. Pick the smallest model that meets quality needs.
  `client = OpenAI()` · हिंदी: OpenAI API chat, embeddings, audio और moderation models का pay-per-token access देती है।
- **026 OpenAI Chat Completions API** — Chat Completions takes a list of role-tagged messages and returns the next assistant message. It is stateless, so you must re-send history and manage its size. Check `finish_reason` and `usage` on every call.
  `client = OpenAI()` · हिंदी: Chat Completions role वाले messages की list लेकर अगला assistant message देता है।
- **027 OpenAI Models Overview (gpt-4o, gpt-4o-mini etc)** — OpenAI offers a ladder of models, from cheap mini to flagship and reasoning models. Pick by evaluating on your own data, and route easy tasks to the cheap model. Pin dated snapshots and re-check prices, because both change often.
  `PRICES: Dict[str, tuple] = {'gpt-4o-mini': (0.15, 0.6), 'gpt-4o': (2.5, 10.0)}` · हिंदी: OpenAI cheap mini से flagship और reasoning तक models की सीढ़ी देता है। अपने data पर evaluate करके चुनो और आसान tasks सस्ते model को दो।
- **028 OpenAI API — Sync vs Async Client** — Use `AsyncOpenAI` with `await` in async servers so slow LLM calls do not block other users. Combine `asyncio.gather` with a semaphore for fast but rate-limit-safe batches. Sync is fine for scripts and plain `def` endpoints.
  `items = [f'product-{i}' for i in range(6)]` · हिंदी: Async servers में `AsyncOpenAI` और `await` use करो ताकि धीमी LLM calls बाकी users को block न करें।
- **029 OpenAI API — Streaming** — Streaming returns the answer in chunks with `stream=True`, improving time to first token. Handle `None` deltas, request usage with `include_usage`, and make sure proxies do not buffer. Serve it from FastAPI with `StreamingResponse`.
  `client = OpenAI()` · हिंदी: `stream=True` से जवाब chunks में आता है, जिससे पहला token जल्दी दिखता है।
- **030 OpenAI API — Token Usage + Cost** — Read `response.usage` on every call and compute cost with current per-model prices. Log it by user and feature, set budgets and alerts, and cap `max_tokens`. Include streaming, retries, and non-chat endpoints so your numbers match the invoice.
  `PRICES = {'gpt-4o-mini': (0.15, 0.6), 'gpt-4o': (2.5, 10.0)}` · हिंदी: हर call में `response.usage` पढ़ो और मौजूदा model prices से cost निकालो।
- **031 OpenAI API — Error Handling** — Catch specific OpenAI exceptions and split them into retryable (429, 5xx, timeout, connection) and permanent (400, 401, quota). Retry with a limit and backoff, log request ids, and return friendly errors. Add fallbacks so users still get an answer.
  `client = OpenAI(max_retries=0)` · हिंदी: OpenAI की specific exceptions पकड़ो और retryable (429, 5xx, timeout, connection) व permanent (400, 401, quota) में बाँटो।
- **032 OpenAI API — Rate Limits** — Rate limits (RPM, TPM) are account-wide, and exceeding them gives HTTP 429. Use a token-aware limiter, honour Retry-After, read the rate-limit headers, and share the budget across pods. For huge offline jobs use the Batch API.
  `bucket = TokenBucket(rate=2.0, capacity=2.0)` · हिंदी: Rate limits (RPM, TPM) पूरे account पर लागू होती हैं और पार करने पर HTTP 429 मिलता है।
- **033 OpenAI API — Retry Strategy** — Retry only transient errors, using exponential backoff with jitter and limits on attempts and total time. Keep one retry layer, protect side effects, and add a circuit breaker and fallback for real outages.
  `T = TypeVar('T')` · हिंदी: सिर्फ़ transient errors retry करो, exponential backoff + jitter के साथ और attempts व कुल समय की सीमा के साथ।
- **034 Claude (Anthropic) API** — Claude is called through the Messages API with a required `max_tokens` and a top-level `system` field. The reply is a list of content blocks, and usage is `input_tokens`/`output_tokens`.
  `client = anthropic.Anthropic()` · हिंदी: Claude को Messages API से call करते हैं, जिसमें `max_tokens` ज़रूरी है और `system` top-level field है।
- **035 Claude API vs OpenAI API** — OpenAI puts system in `messages` and returns `choices`; Claude uses a top-level `system`, requires `max_tokens`, and returns content blocks. Hide the differences behind one adapter so you can fall back, route, and compare providers.
  `text_c = ''.join((b['text'] for b in claude_response['content'] if b['type'] == 'text'))` · हिंदी: OpenAI system को `messages` में रखता है और `choices` लौटाता है; Claude में top-level `system`, ज़रूरी `max_tokens` और content blocks होते ह…
- **036 Claude — System Prompt Difference** — Claude takes the system prompt in a top-level `system` field; `messages` hold only user and assistant turns. Keep `system` static so it can be cached, and put per-request data in `messages`. Do not rely on the system prompt for security.
  `system, messages = split_system(openai_style)` · हिंदी: Claude में system prompt top-level `system` field में जाता है; `messages` में सिर्फ़ user और assistant turns होते हैं।
- **037 Claude — Content Blocks** — Claude messages hold lists of typed content blocks (text, image, tool_use, tool_result). Loop over `message.content`, branch on `type`, and answer each `tool_use` with a matching `tool_result`.
  हिंदी: Claude के messages में typed content blocks की list होती है (text, image, tool_use, tool_result)।
- **038 Claude — Streaming** — Use `client.messages.stream()` and iterate `text_stream` to show Claude's reply as it is generated. Call `get_final_message()` for usage and stop_reason, and handle errors that appear mid-stream.
  `client = anthropic.Anthropic()` · हिंदी: Claude का reply generate होते ही दिखाने के लिए `client.messages.stream()` और `text_stream` iterate करो।
- **039 Gemini API Basics** — Use the `google-genai` SDK: `genai.Client().models.generate_content(model, contents, config)`. The system prompt is `system_instruction`, and the async API lives under `client.aio`. Handle empty or blocked responses and keep model names in config.
  `client = genai.Client()` · हिंदी: `google-genai` SDK use करो: `genai.Client().models.generate_content(model, contents, config)`।
- **040 Groq API (Fast Inference)** — Groq serves open models with very low latency through an OpenAI-shaped API (`groq` SDK or OpenAI client with a custom base URL). Use it for real-time, simple tasks, and keep stronger models and a fallback for hard cases.
  `client = Groq()` · हिंदी: Groq open models को OpenAI जैसी API (`groq` SDK या custom base URL वाले OpenAI client) से बहुत कम latency पर serve करता है।
- **041 Ollama (Local Models)** — Ollama runs open LLMs locally with a simple API on port 11434, including an OpenAI-compatible `/v1` endpoint. It gives privacy and zero per-token cost, but you manage hardware and accept lower quality from small models.
  हिंदी: Ollama port 11434 पर simple API के साथ open LLMs locally चलाता है, जिसमें OpenAI-compatible `/v1` endpoint भी है।
- **042 LiteLLM — Unified API** — LiteLLM gives one OpenAI-style interface to many providers, so switching is a model-string change. Its Router adds retries, fallbacks, and load balancing, and its proxy adds budgets and logging.
  `response = completion(model=model, messages=messages, temperature=0, max_tokens=30)` · हिंदी: LiteLLM कई providers के लिए एक OpenAI-style interface देता है, इसलिए बदलना सिर्फ़ model string बदलना है।
- **043 Model Selection Strategy** — Pick models using your own golden set, not hype. Choose the cheapest model that passes the quality bar and route hard cases to a bigger one. Re-evaluate regularly because models and prices change.
  `candidates = [Candidate('small', 0.15, 0.6, 0.75), Candidate('large', 2.5, 10.0, 1.0)]` · हिंदी: Model अपने golden set से चुनो, hype से नहीं। सबसे सस्ता model लो जो quality bar पास करे और कठिन cases बड़े model को भेजो।
- **044 Cost Optimization — Models** — Measure tokens and cost per feature first. Then trim prompts, cap outputs, cache, route and batch. Always re-check quality after every saving.
  `base = cost(3000, 400) * requests` · हिंदी: पहले हर feature का token और cost measure करो। फिर prompt छोटा करो, output cap करो, cache, routing और batching लगाओ।
- **045 Latency Optimization — Models** — Latency depends mostly on output tokens, model size and sequential steps. Stream, parallelise independent calls, use smaller models and cap output. Measure TTFT and p95, not only averages.
  हिंदी: Latency ज़्यादातर output tokens, model size और sequential steps से बनती है।
- **046 OpenAI Responses API (new)** — The Responses API is OpenAI's newer unified interface with `input`, `instructions`, tools and optional server-side state. Read answers from `output_text` and handle tool calls via output items. Decide on `store` for privacy.
  `client = OpenAI()` · हिंदी: Responses API OpenAI का नया unified interface है जिसमें `input`, `instructions`, tools और optional server state है।
- **047 OpenAI Assistants API** — Assistants API = Assistant + Thread + Message + Run with polling and built-in tools. It is deprecated in favour of the Responses API. Know it for legacy code and for migration questions.
  `client = OpenAI()` · हिंदी: Assistants API = Assistant + Thread + Message + Run, polling और built-in tools के साथ। इसे Responses API के पक्ष में deprecate किया गया है।
- **048 OpenAI Batch API** — Batch API runs large JSONL jobs asynchronously in up to 24 hours at about half price. Match results using `custom_id` and retry failed lines. Never use it for live user requests.
  `path = Path('batch_input.jsonl')` · हिंदी: Batch API बड़े JSONL jobs को 24 घंटे तक में लगभग आधी कीमत पर चलाता है। Results `custom_id` से match करो और failed lines retry करो।
- **049 Model Fallback Strategy** — Plan for failure: retry transient errors with backoff, then switch models or providers, then use cache or manual review. Use circuit breakers and log every fallback. Validate output formats on every model.
  हिंदी: Failure के लिए plan बनाओ: transient errors पर backoff के साथ retry, फिर model/provider बदलो, फिर cache या manual review।
- **050 LLM API Best Practices** — Secure keys, set timeouts and retries, validate every output, and log tokens and cost. Treat user and document text as untrusted data. Test with evals and monitor in production.
  हिंदी: Keys secure रखो, timeouts और retries लगाओ, हर output validate करो और tokens/cost log करो। User और document text को untrusted data मानो।

**Key snippet — 021 What is an LLM — How it Works**
```python
client = OpenAI()
response = client.chat.completions.create(model='gpt-4o-mini', messages=[{'role': 'system', 'content': 'You are a helpful tariff classification assistant.'}, {'role': 'user', 'content': 'What is an LLM?'}], max_tokens=500, temperature=0.7)
text = response.choices[0].message.content
```

**Key snippet — 028 OpenAI API — Sync vs Async Client**
```python
def fake_llm_sync(item: str) -> str:
    time.sleep(0.5)
    return f'HS for {item}'
async def fake_llm_async(item: str) -> str:
    await asyncio.sleep(0.5)
    return f'HS for {item}'
```

**Key snippet — 036 Claude — System Prompt Difference**
```python
Msg = Dict[str, str]
def split_system(openai_messages: List[Msg]) -> Tuple[str, List[Msg]]:
    system_parts = [m['content'] for m in openai_messages if m['role'] == 'system']
    chat = [m for m in openai_messages if m['role'] in ('user', 'assistant')]
    return ('\n\n'.join(system_parts), chat)
```

**Key snippet — 044 Cost Optimization — Models**
```python
PRICE_IN = 2.5 / 1000000
PRICE_OUT = 10.0 / 1000000
SMALL_IN = 0.15 / 1000000
SMALL_OUT = 0.6 / 1000000
```

---

## Phase 02 — Prompt Engineering (051-080)

- **051 What is Prompt Engineering** — Prompt engineering is writing and testing instructions so LLM output is accurate and parseable. Be specific, give format and examples, and evaluate on a test set. Change one thing at a time.
  हिंदी: Prompt engineering यानी instructions लिखना और test करना ताकि LLM output सही और parse होने लायक हो।
- **052 Zero-Shot Prompting** — Zero-shot means instructions only, no examples. It is cheap, fast and good for common tasks. Improve it with clear labels and format before adding examples.
  हिंदी: Zero-shot यानी सिर्फ़ instructions, examples नहीं। यह सस्ता, तेज़ और आम tasks के लिए अच्छा है।
- **053 Few-Shot Prompting** — Few-shot adds a few examples so the model copies your pattern. Use diverse, balanced, consistent examples and test the gain. Consider dynamic selection or fine-tuning for scale.
  `prompt = few_shot_prompt('usb-c cable 2m braided', EXAMPLES)` · हिंदी: Few-shot में कुछ examples जोड़े जाते हैं ताकि model आपका pattern दोहराए। Diverse, balanced और consistent examples लो और फ़ायदा test करो।
- **054 Chain of Thought (CoT)** — CoT makes the model reason in steps before answering, improving multi-step accuracy. It costs extra output tokens and the reasoning may not be faithful. Use it for hard cases and parse only the final line.
  `out = mock_llm(cot_prompt('Smart watch with cellular calling'))` · हिंदी: CoT model को जवाब से पहले steps में सोचने को कहता है, जिससे multi-step accuracy बढ़ती है।
- **055 Tree of Thought (ToT)** — ToT explores multiple reasoning branches, scores them and keeps the best. It can beat CoT on search-like tasks but costs 10-20x more. Use verifiable evaluators and strict budgets.
  `best = tree_of_thought('Kit: phone holder + charger + cable')` · हिंदी: ToT कई reasoning branches खोजता है, score देता है और सबसे अच्छी रखता है। Search जैसे tasks में CoT से बेहतर हो सकता है पर 10-20x महँगा है।
- **056 Self-Consistency** — Sample several reasoning answers and take the majority vote. The vote share gives a useful confidence score. Cost rises with N and it cannot fix systematic errors.
  `random.seed(7)` · हिंदी: कई reasoning answers sample करके majority vote लो। Vote share से उपयोगी confidence score मिलता है।
- **057 ReAct Prompting** — ReAct alternates Thought, Action and Observation so answers are grounded in tools and data. Always set step limits, validate tool arguments and handle tool errors. Cost grows with each loop because history is re-sent.
  हिंदी: ReAct में Thought, Action और Observation बारी-बारी से चलते हैं, इसलिए जवाब tools और data पर आधारित होते हैं।
- **058 System Prompt Design** — A system prompt sets identity, scope, rules, tone and format for every turn. Keep it short, ordered and versioned, and enforce security in code. Test it with normal and adversarial inputs.
  `text = sp.render()` · हिंदी: System prompt हर turn के लिए पहचान, scope, rules, tone और format तय करता है।
- **059 System Prompt Best Practices** — Write specific, positive, well-separated instructions with reasons and an "if unsure" path. Keep the prompt short and versioned, and test every change on a regression set. Never rely on the prompt alone for security.
  हिंदी: Specific, सकारात्मक और साफ़ अलग किए instructions लिखो, कारण और "पक्का न हो तो" रास्ते के साथ।
- **060 Role Prompting** — Role prompting sets persona, audience and focus, mostly improving style and structure. It does not add facts, so pair it with tools or retrieval. Test whether the role really helps.
  हिंदी: Role prompting persona, audience और focus तय करता है, ज़्यादातर style और structure सुधारता है।
- **061 Instruction Following** — Write numbered, atomic, non-conflicting instructions and specify the exact format. Verify output in code and repair with targeted feedback. Measure the follow rate on a test set.
  हिंदी: Numbered, atomic और बिना विरोधाभास वाले instructions लिखो और ठीक-ठीक format बताओ।
- **062 Output Format Control** — Use structured outputs (schema) or JSON mode, then validate with pydantic; prompts alone are fragile. A schema guarantees shape, not truth, so add semantic checks. Watch `max_tokens` and refusals.
  हिंदी: Structured outputs (schema) या JSON mode इस्तेमाल करो और pydantic से validate करो; सिर्फ़ prompt कमज़ोर है।
- **063 JSON Output Prompting** — JSON output prompting makes the model reply in a fixed machine-readable shape. Always extract, parse and validate, and retry with the error. For guarantees, use native JSON mode or structured outputs.
  हिंदी: JSON output prompting से model fixed machine-readable shape में जवाब देता है।
- **064 Markdown Output Prompting** — Markdown prompting makes answers easy for humans to scan using headings, bullets and tables. Give an exact template, lint the reply, and sanitize before rendering. Use JSON when a program reads the output.
  हिंदी: Markdown prompting से जवाब headings, bullets और tables के साथ इंसानों के लिए आसान बनता है।
- **065 Negative Prompting** — Negative prompting sets clear boundaries such as "do not guess". Always add a positive fallback like UNKNOWN. Enforce important rules in code, because prompts are only probabilistic.
  `raw = fake_llm(SYSTEM, user)` · हिंदी: Negative prompting साफ़ सीमाएँ तय करता है जैसे "अंदाज़ा मत लगाओ"। हमेशा UNKNOWN जैसा positive fallback जोड़ो।
- **066 Prompt Chaining** — Prompt chaining breaks a big task into small focused prompts, each feeding the next. Validate between steps and use plain code for deterministic work. Watch error compounding and total latency.
  `items_json = fake_llm(f'EXTRACT items as JSON list from: {invoice}')` · हिंदी: Prompt chaining बड़े काम को छोटे focused prompts में बाँटती है, हर एक अगले को input देता है।
- **067 Meta Prompting** — Meta prompting uses an LLM to draft or fix prompts from task descriptions and failures. Accept a new prompt only if the eval score improves on held-out data. Keep a human in the loop and version the result.
  `meta = build_meta_prompt('Classify products to HS codes', current_prompt, failures)` · हिंदी: Meta prompting में LLM task और failures से prompts बनाता या सुधारता है। नया prompt तभी रखो जब held-out data पर eval score बढ़े।
- **068 Prompt Compression** — Prompt compression cuts input tokens with shorter instructions, fewer but better chunks and summarised history. Measure tokens per part first and re-run evals after every change. Savings in cost and latency are real only if quality holds.
  `short = compress(verbose)` · हिंदी: Prompt compression छोटे instructions, कम पर बेहतर chunks और summarised history से input tokens घटाता है।
- **069 Prompt Caching (Anthropic + OpenAI)** — Prompt caching reuses a processed prompt prefix, making repeated long prefixes cheaper and faster. Put static content first, dynamic content last, and verify hits in usage fields.
  हिंदी: Prompt caching processed prefix को दोबारा इस्तेमाल करके दोहराए लंबे prefix को सस्ता और तेज़ बनाता है।
- **070 Prompt Versioning** — Prompt versioning stores every prompt change as an immutable version with metadata and scores. Use aliases for promotion and rollback, and log the version with every call. Version the model and parameters too.
  `add('classify', 'Give the HS code for {product}.', 'initial')` · हिंदी: Prompt versioning हर बदलाव को metadata और scores के साथ immutable version के रूप में रखती है।
- **071 Prompt Testing Strategy** — Prompt testing runs a prompt on a sliced golden dataset and compares scores with a baseline. Use metrics, repeated runs and gates, not gut feeling. Feed every production failure back into the dataset.
  `report = evaluate(CASES)` · हिंदी: Prompt testing sliced golden dataset पर prompt चलाकर scores की baseline से तुलना करती है।
- **072 Prompt Injection Attack** — Prompt injection hides instructions in untrusted text so the LLM obeys the attacker. It is worst when the model has tools, private data and untrusted input. There is no perfect fix, so use layered defences and test with a red-team set.
  हिंदी: Prompt injection untrusted text में निर्देश छुपाता है ताकि LLM attacker की बात माने।
- **073 Prompt Injection Prevention** — You cannot fully stop prompt injection with wording alone, so use layers: sanitise, label data, constrain outputs, validate in code, and limit privileges. Design so a tricked model cannot cause serious harm. Test with a red-team set and monitor.
  हिंदी: सिर्फ शब्दों से prompt injection पूरी तरह नहीं रुकता, इसलिए परतें लगाओ: sanitise, data label, output सीमित, code में validate और privileges…
- **074 Jailbreak Attacks** — Jailbreaks try to make the model break its safety or policy rules using personas, fiction, encodings and multi-turn pressure. They target model behaviour, usually from the user. You can only reduce risk, so test, monitor and layer defences.
  हिंदी: Jailbreaks personas, fiction, encodings और multi-turn दबाव से model के safety या policy rules तुड़वाने की कोशिश हैं।
- **075 Jailbreak Prevention** — Prevent jailbreaks with layers: input checks, a clear policy prompt, output moderation, least-privilege tools, rate limits and monitoring. Fail closed and measure both attack success and over-refusal. Keep red-teaming as a regular process.
  हिंदी: Jailbreaks से बचाव परतों में करो: input checks, साफ़ policy prompt, output moderation, least-privilege tools, rate limits और monitoring।
- **076 Context Stuffing** — Context stuffing pastes everything into the prompt: simple, but costly, slow and sometimes less accurate. Use it for small corpora and prototypes; use RAG for production scale. Measure tokens and quality instead of assuming a bigger window is better.
  हिंदी: Context stuffing सब कुछ prompt में डाल देता है: सरल, पर महँगा, धीमा और कभी-कभी कम सटीक।
- **077 Lost in the Middle Problem** — LLMs often miss facts in the middle of long prompts, giving a U-shaped accuracy curve. Use fewer, reranked chunks, place the best at the edges and repeat the question at the end. Always test your own model and data by position.
  हिंदी: LLM अक्सर लंबे prompts के बीच के facts चूक जाते हैं, जिससे accuracy का U-आकार वक्र बनता है।
- **078 Prompt Length Optimization** — The best prompt is the shortest one that meets your quality target. Measure tokens per section, ablate parts with an eval set, and enforce a token budget in CI. Use conditional prompts and caching for rarely used or static text.
  `counts = {name: rough_tokens(text) for name, text in SECTIONS.items()}` · हिंदी: सबसे अच्छा prompt वह है जो quality target पूरा करते हुए सबसे छोटा हो।
- **079 Temperature for Different Tasks** — Temperature controls randomness: near 0 for classification, extraction and JSON; moderate for explanations; high for creative work. Do not assume 0 is perfectly deterministic. Set values per task in one policy, not globally.
  हिंदी: Temperature randomness नियंत्रित करता है: classification, extraction और JSON के लिए 0 के आसपास; explanations के लिए मध्यम; creative काम के…
- **080 Production Prompt Best Practices** — Production prompts need structure, structured outputs, versioning, tests, safety layers, cost control and monitoring. Bound every call with timeouts, retries and fallbacks, and fail safely.
  हिंदी: Production prompts को structure, structured outputs, versioning, tests, safety layers, cost control और monitoring चाहिए।

**Key snippet — 051 What is Prompt Engineering**
```python
def build_prompt(role: str, task: str, context: str, rules: list[str], output_format: str) -> str:
    rule_text = '\n'.join((f'- {r}' for r in rules))
    return f'Role: {role}\nTask: {task}\nContext: {context}\nRules:\n{rule_text}\nOutput format: {output_format}'
prompt = build_prompt(role='Customs classification expert', task='Give the 6-digit HS code for the product.', context='Wireless earbuds with charging case', rules=['Use only the international 6-digit level', 'If unsure return null'], output_format='JSON: {"hs_code": string|null, "reason": string}')
```

**Key snippet — 058 System Prompt Design**
```python
sp = SystemPrompt(identity='You are TariffBot, an assistant for customs brokers.', scope=['HS code classification', 'Import duty questions'], rules=['Never invent HS codes', 'If unsure, say so and ask one question'], tone='Concise and professional.', output_format='JSON: {"hs_code": str|null, "confidence": number, "reason": str}')
text = sp.render()
```

**Key snippet — 067 Meta Prompting**
```python
current_prompt = 'Give the HS code for the product.'
failures = [{'input': 'phone case', 'expected': '3926.90', 'got': '8517.13'}, {'input': 'usb charger', 'expected': '8504.40', 'got': '8517.13'}]
def build_meta_prompt(task: str, prompt: str, fails: list[dict[str, str]]) -> str:
    lines = [f"- input: {f['input']} | expected: {f['expected']} | got: {f['got']}" for f in fails]
    return f'You are a prompt engineer.\nTASK: {task}\nCURRENT PROMPT:\n{prompt}\nFAILURES:\n' + '\n'.join(lines) + '\nRewrite the prompt to fix these failures without breaking other cases.\nReturn ONLY the new prompt text.'
```

**Key snippet — 074 Jailbreak Attacks**
```python
JAILBREAK_PATTERNS: dict[str, str] = {'persona': '\\b(you are now|pretend (to be|you are)|act as)\\b.*\\b(no rules|unrestricted|dan)\\b', 'override': '\\bignore (your|all|previous) (rules|guidelines|instructions)\\b', 'fiction': '\\b(in a (story|novel|movie)|hypothetically)\\b', 'prefix': '\\bstart (your )?(answer|reply|response) with\\b', 'encoding': '\\b(base64|rot13|decode this)\\b'}
def tag_attempt(prompt: str) -> list[str]:
    tags = [name for name, pat in JAILBREAK_PATTERNS.items() if re.search(pat, prompt, flags=re.IGNORECASE | re.DOTALL)]
    return tags
```

---

## Phase 03 — Structured Output (081-100)

- **081 Structured Output — What + Why** — Structured output makes the LLM return schema-shaped data that code can use directly, enforced by the provider instead of hoped for in a prompt. It guarantees structure, not truth, so keep validators and evals.
  हिंदी: Structured output LLM से schema के आकार का data दिलाता है जिसे code सीधे इस्तेमाल करे; यह prompt की उम्मीद नहीं, provider द्वारा लागू होता…
- **082 JSON Mode in OpenAI** — OpenAI JSON mode (`response_format={"type": "json_object"}`) guarantees valid JSON syntax but not your keys or types. Mention JSON in the prompt, check `finish_reason` for truncation, and validate with Pydantic.
  हिंदी: OpenAI JSON mode (`response_format={"type": "json_object"}`) valid JSON syntax की गारंटी देता है, आपके keys या types की नहीं।
- **083 Structured Output in OpenAI** — Structured Output makes OpenAI return JSON that matches your schema, enforced by the API. Use Pydantic with `parse()` and check `refusal`. It guarantees shape, not factual correctness.
  हिंदी: Structured Output में OpenAI आपके schema जैसा JSON देता है, API इसे enforce करती है। Pydantic और `parse()` use करो और `refusal` check करो।
- **084 response_format Parameter** — `response_format` has three modes: text, json_object and json_schema. Only json_schema with strict guarantees your keys and types. Always check `finish_reason` for truncation.
  हिंदी: `response_format` के तीन modes हैं: text, json_object और json_schema। सिर्फ strict json_schema आपकी keys और types की guarantee देता है।
- **085 Pydantic + OpenAI Integration** — Pass a Pydantic class as `response_format` to `parse()` and get a typed object back. The class is schema, validator and type hints in one. Always handle ValidationError, refusal and truncation.
  `schema = TariffResult.model_json_schema()` · हिंदी: Pydantic class को `parse()` के `response_format` में दो और typed object पाओ। Class एक साथ schema, validator और type hints है।
- **086 Instructor Library** — Instructor wraps LLM clients and returns Pydantic objects via `response_model`. It retries automatically with validator error messages. Keep retries low because each one costs tokens.
  हिंदी: Instructor LLM clients को wrap करके `response_model` से Pydantic objects देता है।
- **087 Structured Output in Claude** — With Claude, structured output is done via tool use: define `input_schema`, force the tool, read `block.input`. Validate with Pydantic afterwards. Prompt caching makes the tool definition cheap.
  हिंदी: Claude में structured output tool use से होता है: `input_schema` define करो, tool force करो, `block.input` पढ़ो।
- **088 Tool Use for Structured Output** — Tool use turns function arguments into structured output, even if you never run the function. It shines when the model must choose between several shapes. Parse, validate and use `tool_choice` to force a call.
  हिंदी: Tool use में function के arguments ही structured output बन जाते हैं, भले function कभी run न हो।
- **089 Parsing LLM Output** — Parsing turns raw LLM text into data by stripping fences, finding the JSON block and validating it. Use it for models without native structured output. Keep a clear error path for retries.
  हिंदी: Parsing fences हटाकर, JSON block ढूँढकर और validate करके raw LLM text को data बनाती है।
- **090 Output Validation** — Validate in layers: syntax, schema, semantics and business rules. Never trust LLM facts; verify against your source of truth. Decide accept, retry or human review.
  हिंदी: Layers में validate करो: syntax, schema, semantics और business rules। LLM के facts पर भरोसा मत करो; अपने source of truth से जाँचो।
- **091 Retry on Invalid Output** — Retry invalid LLM output with error feedback and a small cap. Handle transient API errors separately with backoff and jitter. Watch cost because retries resend the whole conversation.
  `script = iter([ConnectionError('timeout'), '8518.99', '8518.30'])` · हिंदी: Invalid LLM output पर error feedback और छोटी limit के साथ retry करो। Transient API errors को backoff और jitter से अलग संभालो।
- **092 Nested Structured Output** — Nested outputs mirror real documents using models inside models. Keep depth small, compute totals in code and watch output length. Pydantic validates every level.
  `schema = Declaration.model_json_schema()` · हिंदी: Nested outputs models के अंदर models से असली documents जैसे होते हैं। Depth छोटी रखो, totals code में निकालो और output length देखो।
- **093 Array Output** — Wrap arrays in an object and give every item an id. Verify that every input id comes back exactly once. Batch moderately and chunk big inputs.
  `result = BatchResult.model_validate_json(reply)` · हिंदी: Arrays को object में wrap करो और हर item को id दो। Verify करो कि हर input id ठीक एक बार लौटी।
- **094 Enum in Structured Output** — Enums force the model to choose from allowed values, giving consistent outputs. Always add an "other" option and keep the list short. Prefilter big label sets with retrieval.
  हिंदी: Enums model को allowed values में से चुनने पर मजबूर करते हैं, जिससे outputs consistent रहते हैं। हमेशा "other" option रखो और list छोटी रखो।
- **095 Optional Fields** — Optional fields let the model say "unknown" instead of inventing values. In strict mode that means required-but-nullable. Handle None in code and ask the user for missing data.
  हिंदी: Optional fields model को values गढ़ने की जगह "पता नहीं" कहने देते हैं। Strict mode में इसका मतलब है required-but-nullable।
- **096 Streaming + Structured Output** — Streaming shows structured output early but JSON is incomplete until the end. Display partial data, act only on the final validated object. Use SSE in FastAPI and the SDK helpers.
  `final = json.loads(buffer)` · हिंदी: Streaming structured output जल्दी दिखाती है पर JSON अंत तक अधूरा रहता है। Partial data दिखाओ, पर काम सिर्फ अंतिम validated object पर करो।
- **097 Structured Output in FastAPI** — Use one Pydantic model family for request, LLM output and response. Share one async client and map errors to correct HTTP codes. Log tokens and latency for every request.
  `app = FastAPI(title='Tariff API')` · हिंदी: Request, LLM output और response के लिए Pydantic models का एक परिवार use करो।
- **098 Schema Design Best Practices** — A schema is part of the prompt: clear names, real types, good descriptions and reasoning first. Keep it small and shallow. Version it and evaluate every change.
  हिंदी: Schema prompt का हिस्सा है: साफ names, असली types, अच्छे descriptions और reasoning पहले। इसे छोटा और shallow रखो।
- **099 Common Structured Output Patterns** — Most structured-output features are five patterns: extract, classify, route, score and decide with evidence. Add confidence, evidence and null/other options. Build one generic helper to reuse everywhere.
  हिंदी: ज़्यादातर structured-output features पाँच patterns हैं: extract, classify, route, score और evidence के साथ decide।
- **100 Structured Output for Tariff System** — The Tariff output contract combines nested schema, enums, optional fields, evidence and confidence. The LLM selects the code from retrieved candidates while the duty comes from the official table. Routing sends uncertain cases to users or humans.
  `fake = HSDecision(reasoning='guess', evidence_quote='?', hs_code='9999.99', confidence=0.99)` · हिंदी: Tariff output contract में nested schema, enums, optional fields, evidence और confidence सब मिलते हैं।

**Key snippet — 081 Structured Output — What + Why**
```python
class TariffResult(BaseModel):
    hs_code: Literal['8518.30', '8517.13', '3926.90']
    confidence: float = Field(ge=0, le=1)
    needs_review: bool
    reasons: list[str] = Field(default_factory=list)
```

**Key snippet — 085 Pydantic + OpenAI Integration**
```python
class TariffResult(BaseModel):
    hs_code: str = Field(pattern='^\\d{4}\\.\\d{2}$', description='HS code like 8518.30')
    duty_percent: float = Field(ge=0, le=100, description='Duty in percent')
    confidence: float = Field(ge=0, le=1)
```

**Key snippet — 091 Retry on Invalid Output**
```python
class RetryExhausted(RuntimeError):
    """All attempts failed."""
```

**Key snippet — 095 Optional Fields**
```python
class ProductInfo(BaseModel):
    name: str
    country_of_origin: Optional[str]
    unit_value_usd: Optional[float]
```

---

## Top 10 interview questions

**1. Tokens: What is BPE (Byte Pair Encoding)?** (022)
BPE is the tokenization algorithm used by GPT models. It starts with individual bytes, then iteratively merges the most frequent adjacent pairs.

**2. Temperature + Top-p + Top-k: What does temperature do?** (024)
It scales the logits before softmax. Low values make the distribution sharp (predictable); high values flatten it (more random).

**3. OpenAI API: What does `stream=True` do?** (029)
The API returns chunks as they are generated instead of one final response.

**4. OpenAI API: What is exponential backoff?** (033)
Waiting longer after each failure, for example 1s, 2s, 4s, 8s, usually with a cap.

**5. Few-Shot Prompting: What is few-shot prompting?** (053)
Including a few input-output examples in the prompt to show the model the pattern.

**6. Chain of Thought (CoT): What is Chain of Thought prompting?** (054)
Asking the model to write its reasoning steps before the final answer.

**7. Prompt Injection Attack: What is prompt injection?** (072)
Untrusted input contains instructions that override or alter the developer's intended behaviour of an LLM.

**8. Structured Output in OpenAI: What is Structured Output?** (083)
A feature where the model's reply is forced to match a JSON Schema you give, so you get predictable, parseable data.

**9. Output Validation: What are the layers of output validation?** (090)
Syntax, schema, semantics (and business/safety rules).

**10. Retry on Invalid Output: Why add the error message when retrying?** (091)
So the model knows what to fix; blind retries often repeat the same mistake.

