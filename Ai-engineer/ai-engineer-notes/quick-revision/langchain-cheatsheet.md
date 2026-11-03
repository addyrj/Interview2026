---

# LangChain Cheatsheet — LangChain, Tool Use, Agents (Quick Revision)
# हिंदी में: LangChain, Tool Use और Agents का Quick Revision (Phases 08-10)

Condensed from topics 231-315: LangChain/LCEL, tool use, agents. Each topic: gist, one key code line, Hindi hint.
> Prices, model names and IDs shown in the source notes are illustrative; always verify on the provider's official pricing/model pages.

---

## Phase 08 — LangChain (231-270)

- **231 LangChain — What + Why** — LangChain provides standard components and LCEL to compose LLM apps. It makes providers swappable and adds retries, streaming and tracing. Use it for RAG, tools and agents; skip it for trivial calls.
  हिंदी: LangChain standard components और LCEL देता है जिससे LLM apps जुड़ते हैं।
- **232 LangChain vs LlamaIndex** — LangChain is broad for agents and workflows; LlamaIndex is deep for data and retrieval. They combine well: LlamaIndex retriever as a LangChain tool in LangGraph. Decide by prototype on real questions and hide frameworks behind interfaces.
  हिंदी: LangChain agents और workflows के लिए broad है; LlamaIndex data और retrieval के लिए deep।
- **233 LangChain Architecture** — LangChain is layered: core interfaces, higher-level langchain, community and partner integrations, plus LangGraph and LangSmith. Everything implements Runnable so it composes with `|`. Keep vendor imports at the edge.
  `prompt = PromptTemplate.from_template('Hello {name}')` · हिंदी: LangChain layered है: core interfaces, langchain, community/partner integrations, साथ में LangGraph और LangSmith।
- **234 LangChain v0.1 vs v0.2 vs v0.3** — v0.1 split packages and introduced LCEL, v0.2 made imports explicit and pushed agents to LangGraph, v0.3 moved to Pydantic v2. Legacy `LLMChain` and memory classes are replaced by LCEL and LangGraph. Migrate with the CLI plus golden tests.
  `prompt = PromptTemplate.from_template('HS code for {product}?')` · हिंदी: v0.1 में packages बँटे और LCEL आया, v0.2 में imports explicit हुए और agents LangGraph की ओर गए, v0.3 में Pydantic v2।
- **235 LCEL — LangChain Expression Language** — LCEL composes Runnables with `|` into chains that automatically support sync, async, streaming and batch. Dicts run branches in parallel. Add retries and fallbacks with one method call.
  `prompt = ChatPromptTemplate.from_template('Context: {context}\nQuestion: {question}')` · हिंदी: LCEL `|` से Runnables जोड़ता है और chain में sync, async, streaming, batch अपने-आप आते हैं। Dict की branches parallel चलती हैं।
- **236 Runnable Interface** — Runnable is the universal interface with invoke, stream and batch (sync and async). Every LangChain component and chain implements it, which is why they compose. Implement native async for real concurrency.
  `v = HSCodeValidator()` · हिंदी: Runnable सबसे common interface है जिसमें invoke, stream, batch (sync और async) हैं।
- **237 Pipe Operator (|)** — `|` composes Runnables left-to-right into a RunnableSequence. Functions and dicts are auto-converted. Non-streaming steps break token streaming.
  `strip = RunnableLambda(lambda s: s.strip())` · हिंदी: `|` Runnables को बाएँ से दाएँ RunnableSequence में जोड़ता है। Functions और dicts अपने-आप convert होते हैं।
- **238 RunnablePassthrough** — RunnablePassthrough forwards its input unchanged, typically beside a retriever branch. `.assign()` adds computed keys while keeping existing ones. Together they let RAG return answer plus sources.
  `fake_retriever = RunnableLambda(lambda q: ['HS 8518 headphones'])` · हिंदी: RunnablePassthrough input को जस का तस आगे भेजता है, आमतौर पर retriever के साथ। `.assign()` पुरानी keys रखकर नई जोड़ता है।
- **239 RunnableParallel** — RunnableParallel runs branches concurrently with the same input and returns a dict. Latency becomes the slowest branch. Handle failures per branch and cap concurrency.
  `t0 = time.perf_counter()` · हिंदी: RunnableParallel एक ही input पर branches साथ चलाता है और dict देता है। Latency सबसे धीमी branch जितनी होती है।
- **240 RunnableLambda** — RunnableLambda turns any function into a Runnable with batch, async and tracing. It takes one input and can return a Runnable for dynamic routing. Prefer async functions and avoid blocking IO.
  `cheap = RunnableLambda(lambda x: f'lookup:{x}')` · हिंदी: RunnableLambda किसी भी function को batch, async और tracing वाला Runnable बनाता है।
- **241 Document Loaders** — Loaders turn files, web and DBs into `Document` objects with text and metadata. Use `lazy_load` and async for large data and isolate errors per file. Keep metadata for citations.
  हिंदी: Loaders files, web और DB को text + metadata वाले `Document` में बदलते हैं।
- **242 Text Splitters** — Splitters cut documents into overlapping chunks that fit limits. Use RecursiveCharacterTextSplitter, measure size in tokens, and respect document structure. Chunking strongly affects retrieval quality and cost.
  `chunks = splitter.split_text(text)` · हिंदी: Splitters documents को overlap वाले chunks में काटते हैं।
- **243 Embeddings in LangChain** — The Embeddings interface (`embed_documents`, `embed_query`) lets any model plug into LangChain vector stores. Use the same model for indexing and querying, and cache to save cost. Switching models means re-embedding everything.
  `emb = ToyEmbeddings()` · हिंदी: Embeddings interface (`embed_documents`, `embed_query`) से कोई भी model LangChain vector stores में लगता है।
- **244 Vector Stores in LangChain** — A VectorStore keeps documents plus embeddings and answers similarity queries, exposed as a retriever. Use metadata filters, upserts with stable ids, and MMR for diversity.
  `vs = InMemoryVectorStore(embedding=Toy())` · हिंदी: VectorStore documents और embeddings रखता है और similarity queries का जवाब देता है, retriever के रूप में।
- **245 Retrievers in LangChain** — A Retriever turns a query into relevant `Document`s through one standard interface. It is a Runnable, so it composes with LCEL and works with any backend. Retrieved chunk size and `k` directly decide your token cost.
  `retriever = KeywordRetriever(docs=corpus, k=2)` · हिंदी: Retriever एक standard interface से query को relevant `Document`s में बदलता है।
- **246 ContextualCompressionRetriever** — ContextualCompressionRetriever retrieves wide, then compresses to what matters for the query. Use a cheap EmbeddingsFilter before an LLM extractor to avoid extra calls. Always measure total tokens across all calls.
  `base = AllDocsRetriever(docs=corpus)` · हिंदी: ContextualCompressionRetriever पहले wide retrieve करता है, फिर query के हिसाब से compress करता है।
- **247 MultiQueryRetriever** — MultiQueryRetriever asks an LLM for several rephrasings, searches with each, and merges unique results. It boosts recall for vague queries but adds one LLM call and more context tokens. Keep the original query and avoid it for exact-code lookups.
  `base = KeywordRetriever(docs=corpus)` · हिंदी: MultiQueryRetriever LLM से कई rephrasings बनवाता है, हर एक से search करता है और unique results मिलाता है।
- **248 EnsembleRetriever** — EnsembleRetriever fuses several retrievers by rank (RRF), the standard way to do hybrid BM25 + vector search. It handles both exact codes and fuzzy meaning. Tune weights with an eval set and cap the final list to control tokens.
  `exact = ExactRetriever(docs=corpus)` · हिंदी: EnsembleRetriever कई retrievers को rank (RRF) से मिलाता है, यही BM25 + vector hybrid search का standard तरीका है।
- **249 Chat Models in LangChain** — Chat models give every provider the same Runnable interface: messages in, AIMessage out. Retry, fallback, streaming, tools and token usage work uniformly. Create one instance and reuse it.
  `llm = FakeListChatModel(responses=['HS 8507 (lithium batteries)', 'second answer'])` · हिंदी: Chat models हर provider को एक जैसा Runnable interface देते हैं: messages अंदर, AIMessage बाहर।
- **250 Prompt Templates** — Prompt templates turn prompts into reusable, validated Runnables with variables. Values are inserted as text, but you still must defend against prompt injection. The template is billed on every call, so keep it short.
  `text = template.format(country='India', product='power bank')` · हिंदी: Prompt templates prompts को variables वाले reusable, validated Runnables में बदलते हैं।
- **251 ChatPromptTemplate** — ChatPromptTemplate builds role-tagged messages, the native input of chat models. Keep rules in `system`, user data in `human`, and escape literal braces. Every message is billed as input tokens, so keep static parts short and first.
  `value = prompt.invoke({'country': 'India', 'product': 'power bank'})` · हिंदी: ChatPromptTemplate role वाले messages बनाता है, जो chat models का native input है।
- **252 MessagesPlaceholder** — MessagesPlaceholder splices a list of role-tagged messages into a prompt, the right way to pass chat history and agent scratchpads. Use `optional=True` for first turns and always trim history. History is re-sent every turn, so cost grows quickly.
  `msgs = prompt.invoke({'history': history, 'input': 'And without battery?'}).to_messages()` · हिंदी: MessagesPlaceholder role वाले messages की list को prompt में जोड़ता है, chat history और agent scratchpad के लिए सही तरीका।
- **253 OutputParsers** — OutputParsers turn raw LLM text into typed data and raise clear errors when the format is wrong. Add format instructions or use `with_structured_output` for reliability. Handle failures with limited retries and a human-review fallback.
  `prompt = ChatPromptTemplate.from_messages([('human', '{q}')])` · हिंदी: OutputParsers LLM के raw text को typed data में बदलते हैं और format गलत होने पर साफ़ error देते हैं।
- **254 StrOutputParser** — StrOutputParser turns an AIMessage into a plain string and streams text pieces. Use it for free-text answers and to chain prompts. It discards tool calls and usage metadata, so track those separately.
  `prompt = ChatPromptTemplate.from_messages([('human', 'Explain HS code for {product}')])` · हिंदी: StrOutputParser AIMessage को plain string में बदलता है और text के टुकड़े stream करता है।
- **255 PydanticOutputParser** — PydanticOutputParser turns model JSON into a validated pydantic object and raises errors on bad data. Add format instructions to the prompt and field descriptions for accuracy.
  `parser = PydanticOutputParser(pydantic_object=TariffResult)` · हिंदी: PydanticOutputParser model के JSON को validated pydantic object में बदलता है और गलत data पर error देता है।
- **256 JsonOutputParser** — JsonOutputParser converts model text into a dict and supplies schema hints for the prompt. It can stream partial dicts, but it does not validate types. For reliability use pydantic validation or native structured output.
  हिंदी: JsonOutputParser model के text को dict में बदलता है और prompt के लिए schema hint देता है।
- **257 Memory in LangChain** — LangChain memory loads past messages into the prompt and saves new ones per session. Use RunnableWithMessageHistory or LangGraph checkpointers, not legacy memory classes. Trim history and use shared storage for production.
  हिंदी: LangChain memory हर session के पुराने messages prompt में डालती है और नए save करती है।
- **258 ConversationBufferMemory** — ConversationBufferMemory stores and replays the whole chat on every turn. It is perfect for short chats but grows without limit and is now legacy. Prefer message-history runnables or LangGraph persistence with trimming.
  हिंदी: ConversationBufferMemory पूरी chat store करके हर turn में दोहराती है। छोटी chats के लिए सही है पर बिना सीमा बढ़ती है और अब legacy है।
- **259 ConversationSummaryMemory** — Summary memory keeps a short, LLM-updated summary instead of the full transcript. It keeps long-chat cost flat, but adds an LLM call and may distort details. Combine with recent raw messages and structured facts for accuracy.
  हिंदी: Summary memory पूरे transcript की जगह LLM से अपडेट होने वाली छोटी summary रखती है।
- **260 Chains — Legacy** — Legacy chains (LLMChain, SequentialChain) bundle prompt, model and parsing with dict keys. They are deprecated and replaced by LCEL for linear flows and LangGraph for stateful flows. Know both: you must read old code and write new code.
  हिंदी: Legacy chains (LLMChain, SequentialChain) prompt, model और parsing को dict keys से जोड़ती हैं।
- **261 RetrievalQA Chain** — RetrievalQA is the legacy one-call RAG chain: retriever, stuff documents in a prompt, answer with sources. It is deprecated in favour of create_retrieval_chain and LCEL. Use strict prompts and score thresholds to avoid made-up answers.
  हिंदी: RetrievalQA legacy एक-call RAG chain है: retriever, documents को prompt में डालना, sources के साथ जवाब।
- **262 ConversationalRetrievalChain** — ConversationalRetrievalChain condenses the follow-up using chat history, retrieves, then answers. It does not store history itself and is deprecated. Use create_history_aware_retriever with create_retrieval_chain, or LangGraph, for new work.
  हिंदी: ConversationalRetrievalChain follow-up को history से condense करती है, फिर retrieve और answer करती है।
- **263 LCEL RAG Chain** — An LCEL RAG chain pipes retriever, prompt, model and parser into one transparent Runnable. It gives streaming, async, batching and tracing for free, and can return sources via RunnableParallel.
  `format_docs = Step(lambda docs: '\n'.join(docs))` · हिंदी: LCEL RAG chain retriever, prompt, model और parser को एक पारदर्शी Runnable में जोड़ती है।
- **264 Callbacks in LangChain** — Callbacks let you hook into LangChain events for logging, token counting, streaming, and tracing without changing chain code. Pass request-scoped handlers via config and use async handlers in async apps. Track tokens and latency to control cost.
  हिंदी: Callbacks से chain का code बदले बिना LangChain events पर logging, token counting, streaming और tracing की जा सकती है।
- **265 LangChain Streaming** — Streaming sends the answer in chunks, so the first token shows in under a second. Use `astream` for output chunks and `astream_events` for internal events; wire it to FastAPI with SSE.
  `llm = GenericFakeChatModel(messages=iter([AIMessage(content=fake_text)] * 2))` · हिंदी: Streaming में answer chunks में आता है, इसलिए पहला token एक सेकंड से पहले दिख जाता है।
- **266 LangChain Async** — Use `ainvoke`, `astream` and `abatch` so waiting on the network never blocks the server. Cap parallelism with `max_concurrency` or a Semaphore, and return errors per item. Async saves time, not tokens.
  `chain = RunnableLambda(fake_classify_sync, afunc=fake_classify)` · हिंदी: Network wait server को block न करे इसलिए `ainvoke`, `astream`, `abatch` use करो।
- **267 LangChain Error Handling** — Retry only transient errors, with backoff and jitter, in ONE layer. Use `with_fallbacks` for backup models or rule-based answers and wrap the full prompt-model-parser unit.
  `chain = RunnableLambda(always_down).with_fallbacks([RunnableLambda(backup_model)])` · हिंदी: सिर्फ transient errors को retry करो, backoff और jitter के साथ, और सिर्फ एक layer में।
- **268 LangChain Caching** — `set_llm_cache` makes repeated identical calls free and instant. Use Redis with TTL and a data version in production, `temperature=0`, and normalized inputs. Exact cache is safe; semantic cache raises hits but risks wrong answers.
  `llm = GenericFakeChatModel(messages=replies)` · हिंदी: `set_llm_cache` से वही call दोबारा मुफ्त और तुरंत मिलती है।
- **269 LangChain Tracing** — Tracing records every step, token and latency of a chain, using callbacks or LangSmith (enabled by env vars). Add run_name, tags and metadata with a request_id so you can find any trace.
  `llm = GenericFakeChatModel(messages=iter([AIMessage(content='HS 8518.30')]))` · हिंदी: Tracing chain के हर step, token और latency को record करता है - callbacks या LangSmith (env vars से on) के ज़रिए।
- **270 LangChain Best Practices** — Compose with LCEL, version prompts, get structured output, and build chains once with injected models. Add timeouts, one retry layer, fallbacks, tracing tags and a golden-set CI gate. Use LangGraph only when you need loops, state or resumability.
  `parser = PydanticOutputParser(pydantic_object=HSResult)` · हिंदी: LCEL से compose करो, prompts version करो, structured output लो, और chains एक बार बनाकर model inject करो।

**Key snippet — 231 LangChain — What + Why**
```python
prompt = ChatPromptTemplate.from_messages([('system', 'You are a tariff assistant.'), ('human', 'HS code for {product}?')])
def fake_llm(messages) -> str:
    text = messages.to_messages()[-1].content
    return f'(fake) Answer for: {text}'
```

**Key snippet — 238 RunnablePassthrough**
```python
fake_retriever = RunnableLambda(lambda q: ['HS 8518 headphones'])
step = {'context': fake_retriever, 'question': RunnablePassthrough()}
print(step | RunnableLambda(lambda d: d)) if False else None
chain = RunnablePassthrough.assign(length=lambda d: len(d['text']), upper=lambda d: d['text'].upper())
```

**Key snippet — 245 Retrievers in LangChain**
```python
corpus = [Document(page_content='HS 8507 lithium-ion batteries and power banks', metadata={'chapter': 85}), Document(page_content='HS 8517 smartphones and telephone sets', metadata={'chapter': 85}), Document(page_content='HS 0901 coffee beans roasted or not', metadata={'chapter': 9})]
retriever = KeywordRetriever(docs=corpus, k=2)
results = retriever.invoke('lithium power banks')
for doc in results:
    print(doc.metadata, '->', doc.page_content)
```

**Key snippet — 252 MessagesPlaceholder**
```python
prompt = ChatPromptTemplate.from_messages([('system', 'You are a tariff assistant.'), MessagesPlaceholder('history'), ('human', '{input}')])
history = [HumanMessage(content='HS code for a power bank?'), AIMessage(content='Heading 8507.')]
msgs = prompt.invoke({'history': history, 'input': 'And without battery?'}).to_messages()
for m in msgs:
    print(f'{type(m).__name__:14}| {m.content}')
```

**Key snippet — 260 Chains — Legacy**
```python
Step = Callable[[Dict[str, str]], Dict[str, str]]
def extract_facts(inputs: Dict[str, str]) -> Dict[str, str]:
    return {'facts': f"electronic, battery powered, audio ({inputs['description']})"}
def classify(inputs: Dict[str, str]) -> Dict[str, str]:
    code = '8518.22' if 'audio' in inputs['facts'] else '9999.99'
    return {'hs_code': code}
```

---

## Phase 09 — Tool Use (271-295)

- **271 Tool Use — What + Why** — Tool use lets the model request function calls with JSON arguments; your code runs them and returns results. This gives fresh data, exact maths and real actions, but you must validate arguments, limit steps and guard against prompt injection.
  `DUTY_TABLE: dict[tuple[str, str], float] = {('8518.30', 'VN'): 0.0, ('8518.30', 'US'): 2.5}` · हिंदी: Tool use में model JSON arguments के साथ function call माँगता है; आपका code उसे चलाकर result लौटाता है।
- **272 Function Calling in OpenAI** — Function calling lets LLMs trigger your code — you define tools as JSON schemas, the LLM returns `tool_calls`, you execute them and send results back, the LLM reads results and generates a final answer. Always loop until `finish_reason == "stop"`.
  `client = AsyncOpenAI()` · हिंदी: Function calling LLMs को आपका code trigger करने देता है।
- **273 Tool Definition Schema** — A tool definition is name + description + JSON Schema, and it decides how well the model picks tools and arguments. Use clear names, "when to use / not use" text, enums and patterns, and generate schemas from Pydantic.
  `generated = DutyArgs.model_json_schema()` · हिंदी: Tool definition = name + description + JSON Schema, और यही तय करती है कि model सही tool और arguments चुनेगा या नहीं।
- **274 Tool Choice Parameter** — `tool_choice` decides if the model may, must, or must not call tools: auto, required/any, specific, none (formats differ per provider). Force a schema tool for guaranteed JSON and force lookups by policy, but never force on every loop turn.
  हिंदी: `tool_choice` तय करता है कि model tool बुला सकता है, बुलाना ही होगा, या नहीं बुला सकता: auto, required/any, specific, none (format provider…
- **275 Parallel Tool Calls** — Parallel tool calls let the model request many independent tools in one message so you run them together. You must return one result per call id. Use for independent reads, avoid for dependent or non-idempotent writes.
  हिंदी: Parallel tool calls में model एक message में कई स्वतंत्र tools माँगता है और आप उन्हें साथ चलाते हैं।
- **276 Tool Results Handling** — Tool result handling means validating, shrinking, labelling errors, sanitising and correctly linking tool output before the model sees it. This improves accuracy, security and cost. Always answer every tool call id, even on failure.
  `KEEP_FIELDS = ('hs_code', 'description', 'duty')` · हिंदी: Tool result handling का मतलब है model को दिखाने से पहले tool output को validate करना, छोटा करना, errors चिह्नित करना, sanitize करना और सही…
- **277 Function Calling in Claude** — Claude tool use returns a tool_use block with stop_reason "tool_use"; you run the function and answer with a tool_result block in a user message. Keep the assistant blocks in history and send all parallel results together.
  हिंदी: Claude tool use में stop_reason "tool_use" के साथ tool_use block आता है; आप function चलाकर user message में tool_result block से जवाब देते…
- **278 Tool Use in Gemini** — Gemini returns a function_call; your code runs the tool and sends back a function_response. The google-genai SDK can automate this, but production code should use a manual, bounded, logged loop.
  `call = FakeFunctionCall(name='get_duty_rate', args={'hs_code': '8517'})` · हिंदी: Gemini function_call देता है; आपका code tool चलाकर function_response भेजता है।
- **279 Tool Use in LangChain** — LangChain gives one tool interface across providers: define with @tool, attach with bind_tools, run the tool_calls and return ToolMessages. The model only requests tools; you or an agent execute them. Schemas and history cost tokens every step.
  `msg = tool_map[fake_tool_call['name']].invoke(fake_tool_call)` · हिंदी: LangChain सभी providers के लिए एक tool interface देता है: @tool से define, bind_tools से attach, tool_calls चलाकर ToolMessage लौटाओ।
- **280 @tool Decorator** — `@tool` converts a typed, documented function into a tool with a schema the LLM can read. Use `args_schema` for validation and `ToolException` with `handle_tool_error` for safe failures.
  हिंदी: `@tool` typed और documented function को ऐसे tool में बदलता है जिसका schema LLM पढ़ सके।
- **281 StructuredTool** — StructuredTool wraps any function with validated multi-argument input. Use from_function to add both sync and async versions and explicit schema. Validation and compact schemas reduce wasted retries and tokens.
  हिंदी: StructuredTool किसी भी function को validated multi-argument input के साथ wrap करता है।
- **282 Custom Tools** — Custom tools subclass BaseTool to carry dependencies, caching and safe error handling. Never keep per-request data on a shared instance. Compact outputs and good errors reduce token cost.
  हिंदी: Custom tools BaseTool subclass करके dependencies, caching और सुरक्षित error handling रखते हैं।
- **283 Built-in Tools** — Built-in tools are ready-made capabilities, either local library tools or provider-hosted ones. Local tools keep data in your infra; hosted tools are easier but add fees and data-leaving risk.
  हिंदी: Built-in tools पहले से बने capabilities हैं, local library या provider-hosted।
- **284 Web Search Tool** — Web search gives LLMs fresh, citable facts. Use hosted tools or custom tools like Tavily, restrict domains, and cap searches. Treat web text as untrusted and watch the extra fee and token cost.
  हिंदी: Web search LLM को ताज़े, citation-योग्य facts देता है।
- **285 Code Execution Tool** — Code execution lets the model write and run Python for exact results and big-file analysis. Safety depends on a true sandbox: no secrets, no network, strict limits. Truncate outputs and cap retries to control tokens.
  `model_code = "rows=[('8517',100,20),('6403',50,25)]\nprint(sum(v*r/100 for _,v,r in rows))"` · हिंदी: Code execution से model सटीक नतीजों और बड़ी file analysis के लिए Python लिखकर चलाता है।
- **286 Calculator Tool** — LLMs cannot do reliable arithmetic, so give them a calculator tool. Never use `eval`; parse with `ast`, whitelist operators, use `Decimal` for money and return errors as strings.
  हिंदी: LLM भरोसेमंद गणित नहीं कर सकता, इसलिए calculator tool दो।
- **287 Database Query Tool** — A DB query tool lets the LLM fetch live data without a raw connection. Use parameterised queries, a read-only user, single-statement validation and row limits. Rows returned are the main token cost, so keep them small.
  `conn = sqlite3.connect(':memory:')` · हिंदी: DB query tool से LLM को raw connection दिए बिना live data मिलता है।
- **288 API Call Tool** — An API call tool lets the LLM reach live external data through typed, validated functions. Fix the base URL, allowlist hosts, set timeouts, hide keys and trim responses. Use idempotency keys for anything with side effects.
  हिंदी: API call tool से LLM live external data तक पहुँचता है, typed और validated functions के ज़रिए।
- **289 File Read/Write Tool** — File tools let agents read inputs and write outputs, but only inside a sandbox. Resolve paths, allowlist extensions, limit sizes and write atomically. File content is the biggest token cost, so truncate or chunk it.
  `SANDBOX = Path(tempfile.mkdtemp(prefix='agent_ws_')).resolve()` · हिंदी: File tools से agent inputs पढ़ता और outputs लिखता है, पर सिर्फ़ sandbox में।
- **290 Tool Error Handling** — Tools must never crash the agent; catch errors and return short structured payloads with type, hint and retryable. Validate arguments with pydantic, use timeouts and cap the loop. Good errors let the LLM self-correct and save tokens.
  हिंदी: Tools agent को crash न करें; errors पकड़कर छोटा structured payload (type, hint, retryable) लौटाओ।
- **291 Tool Retry Logic** — Retry only transient failures, with exponential backoff, jitter and a total deadline. Use idempotency keys for side effects and a circuit breaker for sustained outages. Retry in one layer only to avoid multiplied calls.
  `T = TypeVar('T')` · हिंदी: सिर्फ़ transient failures retry करो: exponential backoff, jitter और कुल deadline के साथ।
- **292 Tool Output Validation** — Validate every tool output with a schema, business rules and size limits before the LLM sees it. Sanitise free text because it can carry prompt injection. Log failures to spot upstream changes early.
  हिंदी: LLM को दिखाने से पहले हर tool output को schema, business rules और size limit से validate करो।
- **293 Tool Use Patterns** — Choose a tool pattern deliberately: single, parallel, chain, router, agent loop or human approval. Use deterministic code for fixed paths and agents only for open-ended work. Always cap rounds and gate risky actions.
  हिंदी: Tool pattern सोच-समझकर चुनो: single, parallel, chain, router, agent loop या human approval।
- **294 Tool Selection Strategy** — Good tool selection comes from sharp descriptions, a small relevant tool list, correct `tool_choice`, and an eval set. Retrieve or route tools when you have many. Fewer schemas also means fewer tokens.
  हिंदी: अच्छा tool selection तेज़ descriptions, छोटी relevant list, सही `tool_choice` और eval set से आता है।
- **295 Tool Use Best Practices** — Production tool use needs focused tools, strict schemas, least privilege, validation, timeouts, structured errors, budgets, logging and tests. Never let the model control identity or permissions.
  हिंदी: Production tool use के लिए focused tools, strict schemas, least privilege, validation, timeouts, structured errors, budgets, logging और tes…

**Key snippet — 271 Tool Use — What + Why**
```python
DUTY_TABLE: dict[tuple[str, str], float] = {('8518.30', 'VN'): 0.0, ('8518.30', 'US'): 2.5}
def get_duty_rate(hs_code: str, country: str) -> dict[str, Any]:
    rate = DUTY_TABLE.get((hs_code, country))
    if rate is None:
        return {'error': f'no rate for {hs_code}/{country}'}
    return {'hs_code': hs_code, 'country': country, 'duty_percent': rate}
```

**Key snippet — 276 Tool Results Handling**
```python
RAW_ROWS: List[Dict[str, Any]] = [{'hs_code': f'8518.{i:02d}', 'description': f'Audio item {i}', 'duty': 10 + i, 'internal_notes': 'x' * 200, 'created_by': 'etl-job'} for i in range(40)]
KEEP_FIELDS = ('hs_code', 'description', 'duty')
MAX_ROWS = 5
MAX_CHARS = 1500
```

**Key snippet — 280 @tool Decorator**
```python
@tool
def get_duty_rate(hs_code: str, country: str='IN') -> float:
    """Return the basic customs duty percent for an HS code in a country."""
    table: dict[str, float] = {'8517': 20.0}
    return table.get(hs_code, -1.0)
```

**Key snippet — 284 Web Search Tool**
```python
@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
```

**Key snippet — 288 API Call Tool**
```python
ALLOWED_HOSTS = {'api.exchangerate.example'}
def fake_http_get(url: str, timeout: float) -> dict[str, Any]:
    """Stand-in for a real HTTP call so the demo works without internet."""
    return {'base': 'USD', 'rates': {'INR': 83.2, 'EUR': 0.92}, 'date': '2026-10-28'}
```

---

## Phase 10 — Agents (296-315)

- **296 ReAct Pattern — What + Why** — ReAct makes an LLM alternate Thought, Action and Observation until it has a Final Answer. It grounds reasoning in real tool results and handles dependent multi-step tasks. Cap the steps because cost and latency grow every loop.
  हिंदी: ReAct में LLM Thought, Action और Observation बारी-बारी करता है जब तक Final Answer न मिले।
- **297 ReAct — Thought, Action, Observation** — Thought is reasoning, Action is the tool call, Observation is the real result. The model writes the first two; your code writes the third, enforced by a stop sequence. Parse strictly, handle format errors as observations and keep observations short.
  `FINAL_RE = re.compile('Final Answer:\\s*(.+)', re.S)` · हिंदी: Thought सोच है, Action tool call है और Observation असली result है। पहले दो model लिखता है; तीसरा आपका code, stop sequence के साथ।
- **298 ReAct Implementation** — A ReAct agent is a loop: call the LLM, parse, run the tool, append the Observation, stop on Final Answer or a limit. Keep state per run, add timeouts, truncation and token tracing.
  `result = ReActAgent(ScriptedLLM(), TOOLS).run('Duty on 100 cotton t-shirts at USD 5 each?')` · हिंदी: ReAct agent एक loop है: LLM call, parse, tool चलाओ, Observation जोड़ो, Final Answer या limit पर रुको।
- **299 ReAct in LangChain** — `create_react_agent` builds a text ReAct agent from an LLM, tools and a prompt with `{tools}`, `{tool_names}`, `{input}`, `{agent_scratchpad}`; `AgentExecutor` runs it. Add `handle_parsing_errors`, `max_iterations` and token tracking.
  `llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)` · हिंदी: `create_react_agent` LLM, tools और prompt (`{tools}`, `{tool_names}`, `{input}`, `{agent_scratchpad}`) से text ReAct agent बनाता है; `Agent…
- **300 ReAct Agent** — A ReAct agent combines an LLM, tools, memory, a prompt and a controller to solve open-ended tasks step by step. Memory and limits are what make it production-safe. Use a plain pipeline when the steps are fixed.
  `agent = ReActAgent(fake_decide, {'get_rate': get_rate})` · हिंदी: ReAct agent LLM, tools, memory, prompt और controller मिलाकर open-ended काम कदम-दर-कदम हल करता है।
- **301 AgentExecutor** — `AgentExecutor` runs the loop: ask the agent, run the tool, store the observation, repeat until finish or limit. Set `max_iterations`, `max_execution_time`, `handle_parsing_errors` and `return_intermediate_steps`.
  `agent = RunnableLambda(plan)` · हिंदी: `AgentExecutor` loop चलाता है: agent से पूछो, tool चलाओ, observation रखो, finish या limit तक दोहराओ।
- **302 Agent Scratchpad** — The scratchpad stores the agent's actions and observations so each turn can build on the last. It is resent every turn, so it drives token cost and needs trimming. In LangGraph, the messages list in state plays this role.
  `pad = Scratchpad()` · हिंदी: Scratchpad agent के actions और observations रखता है ताकि हर turn पिछले पर बने।
- **303 Agent Stop Conditions** — Agents stop naturally when the model gives a final answer, and forcibly through iteration, time, token, repetition and error limits. Always return a partial answer with a stop reason. Limits protect cost, latency and safety.
  `policy, state = (StopPolicy(), LoopState())` · हिंदी: Agent स्वाभाविक रूप से तब रुकता है जब model final answer दे, और जबरन iteration, समय, token, दोहराव व error limits से।
- **304 Agent Max Iterations** — Max iterations caps agent turns (AgentExecutor default 15, LangGraph recursion_limit default 25). Choose it from measured p95 steps, handle the cap gracefully, and combine it with time and token limits.
  `p50, p95, worst = (percentile(steps_used, 0.5), percentile(steps_used, 0.95), max(steps_used))` · हिंदी: Max iterations agent turns की सीमा है (AgentExecutor default 15, LangGraph recursion_limit default 25)।
- **305 OpenAI Functions Agent** — The OpenAI Functions Agent uses structured function calls instead of parsing text, which made agents far more reliable. It is now a legacy path; prefer tool-calling agents or LangGraph. Schemas and scratchpad history cost tokens on every turn.
  हिंदी: OpenAI Functions Agent text parse करने की जगह structured function calls इस्तेमाल करता है, जिससे agents कहीं ज़्यादा भरोसेमंद हुए।
- **306 OpenAI Tools Agent** — A tools agent lets the model pick functions through structured JSON tool calls in a loop. Always append the assistant message and matching tool results, bound the loop, and return errors to the model.
  हिंदी: Tools agent में model JSON tool calls से functions चुनता है और loop चलता है।
- **307 Claude Agent** — A Claude agent loops on `stop_reason="tool_use"`, running tools and returning `tool_result` blocks inside a user message. Keep assistant content unchanged and handle errors with `is_error`. Use prompt caching to reduce the growing token cost.
  हिंदी: Claude agent `stop_reason="tool_use"` पर loop करता है, tools चलाता है और `tool_result` को user message में भेजता है।
- **308 Agent Memory** — LLMs are stateless, so agents add short-term history and long-term stored facts. Trim, summarise and retrieve to control tokens. Store memory externally, namespaced per user.
  हिंदी: LLM stateless है, इसलिए agent में short-term history और long-term facts जोड़ते हैं। Tokens कम रखने के लिए trim, summary और retrieval करो।
- **309 Agent with Human in Loop** — HITL pauses an agent before risky steps so a human can approve, edit or reject. It needs saved state (checkpointer), a review API and fail-safe timeouts. Waiting costs no tokens; side effects must be idempotent.
  हिंदी: HITL में risky step से पहले agent रुकता है और इंसान approve, edit या reject करता है।
- **310 Agent Error Handling** — Classify errors, retry only transient ones with backoff, and return tool errors to the model as text. Validate outputs, fall back to another model, and guard loops with step and token budgets. Never retry side effects without idempotency.
  `T = TypeVar('T')` · हिंदी: Errors को बाँटो, सिर्फ transient errors को backoff के साथ retry करो और tool errors model को text में लौटाओ।
- **311 Agent Streaming** — Stream both tokens and step events so users see progress while the agent works. Use async generators with SSE in FastAPI, disable proxy buffering, and cancel work on disconnect. Remember streamed text is unverified, so guardrails need care.
  हिंदी: Tokens और step events दोनों stream करो ताकि user को progress दिखे।
- **312 Agent Observability** — Observability records every LLM call, tool call, token and error as a linked trace. It lets you debug wrong answers and control cost and latency. Redact sensitive data and track percentiles, not just averages.
  हिंदी: Observability हर LLM call, tool call, token और error को जुड़े हुए trace में record करती है।
- **313 Agent Evaluation** — Evaluate agents on a fixed dataset for both answer quality and trajectory, cost and latency. Use code checks plus a calibrated LLM judge, and gate releases on regressions. Keep growing the dataset from real failures.
  हिंदी: Fixed dataset पर agent का answer quality, trajectory, cost और latency मापो।
- **314 Agent Security** — Assume the model can be tricked by prompt injection and limit damage in code. Use least privilege, argument validation, sandboxing, per-user scopes and approvals for risky actions. Do not rely on the system prompt alone.
  `HS_PATTERN = re.compile('^\\d{4}\\.\\d{2}$')` · हिंदी: मानकर चलो कि prompt injection से model भटक सकता है और नुकसान code से सीमित करो।
- **315 Agent Best Practices** — Start simple, use agents only for unpredictable paths, and keep tools few and clear. Bound loops, validate outputs, secure tools, trace and evaluate before release. Roll out gradually with humans on risky steps.
  हिंदी: सरल से शुरू करो, agent सिर्फ अनिश्चित रास्तों के लिए और tools कम व साफ़ रखो।

**Key snippet — 296 ReAct Pattern — What + Why**
```python
def search_hs_codes(q: str) -> str:
    """Tool 1: fake HS lookup."""
    return '6109.10' if 'shirt' in q.lower() else 'unknown'
def get_tariff_rate(code: str) -> str:
    """Tool 2: fake rate lookup."""
    return {'6109.10': '20'}.get(code, 'unknown')
```

**Key snippet — 300 ReAct Agent**
```python
def get_rate(code: str) -> str:
    return {'6109.10': '20%'}.get(code, 'unknown')
```

**Key snippet — 303 Agent Stop Conditions**
```python
@dataclass
class StopPolicy:
    max_iterations: int = 6
    max_seconds: float = 20.0
    max_tokens: int = 20000
    max_repeats: int = 2
    max_errors: int = 3
```

**Key snippet — 306 OpenAI Tools Agent**
```python
def search_hs_code(product: str) -> str:
    table = {'bluetooth speaker': '8518.22'}
    return table.get(product.lower(), 'UNKNOWN')
def get_duty_rate(hs_code: str, country: str) -> str:
    rates = {('8518.22', 'CN'): '12.5%'}
    return rates.get((hs_code, country), 'N/A')
```

**Key snippet — 309 Agent with Human in Loop**
```python
Decision = Literal['approve', 'reject', 'edit']
@dataclass
class Proposal:
    action: str
    hs_code: str
    confidence: float
```

---

## Top 10 interview questions

**1. LCEL: What does `|` do?** (235)
Calls `Runnable.__or__` to create a `RunnableSequence` where each output feeds the next input.

**2. Runnable Interface: Name core Runnable methods.** (236)
invoke, ainvoke, stream, astream, batch, abatch (plus astream_events).

**3. OutputParsers: What is an OutputParser?** (253)
A Runnable that converts model output into a structured Python value (str, list, dict, pydantic object), usually the last step in an LCEL chain.

**4. Function Calling in OpenAI: What is the difference between `tool_choice="auto"`, `"required"`, and a specific tool?** (272)
`"auto"` (default): LLM decides whether to call a tool or respond directly. `"required"`: LLM MUST call at least one tool (can't respond with text only).

**5. Parallel Tool Calls: What are parallel tool calls?** (275)
The model returns multiple tool calls in a single assistant message so they can be executed together.

**6. Tool Error Handling: Why return errors instead of raising?** (290)
The LLM can read an error and self-correct or explain it. A raised exception crashes the request and loses context.

**7. ReAct Pattern: What does ReAct stand for?** (296)
Reasoning + Acting. The model interleaves reasoning traces with tool actions.

**8. AgentExecutor: What is the difference between an agent and an `AgentExecutor`?** (301)
The agent decides the next step. The executor runs the loop: calls the agent, executes tools, handles errors and limits.

**9. Agent Max Iterations: What is the default max_iterations in AgentExecutor?** (304)
15.

**10. Agent Security: What is prompt injection?** (314)
Malicious text that makes the model follow attacker instructions instead of the developer's. Direct injection comes from the user; indirect injection comes from documents, web pages or tool outputs.

