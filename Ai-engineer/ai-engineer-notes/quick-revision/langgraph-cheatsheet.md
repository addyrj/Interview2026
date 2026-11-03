---

# LangGraph Cheatsheet — LangGraph, Multi-Agent, Memory (Quick Revision)
# हिंदी में: LangGraph, Multi-Agent और Memory का Quick Revision (Phases 11-13)

Condensed from topics 316-388: LangGraph, multi-agent systems, memory. Each topic: gist, one key code line, Hindi hint.
> Prices, model names and IDs shown in the source notes are illustrative; always verify on the provider's official pricing/model pages.

---

## Phase 11 — LangGraph (316-345)

- **316 LangGraph — What + Why** — LangGraph builds LLM apps as stateful graphs with nodes, edges, loops and branches. It adds persistence, human approval and streaming that plain chains lack. Use it when control flow depends on state.
  `g = StateGraph(State)` · हिंदी: LangGraph LLM apps को nodes, edges, loops और branches वाले stateful graph की तरह बनाता है।
- **317 LangGraph vs AgentExecutor** — AgentExecutor hides the agent loop; LangGraph exposes it as a graph you can customise, pause, persist and stream. Migrate with `create_react_agent` or a custom StateGraph. Map `max_iterations` to `recursion_limit`.
  `g = StateGraph(State)` · हिंदी: AgentExecutor agent loop छिपाता है; LangGraph उसे graph बनाकर customise, pause, persist और stream करने देता है।
- **318 State Graph Concept** — A StateGraph shares one state among nodes; nodes return partial updates that reducers merge. Edges and routers choose the next node, supersteps allow parallelism. Keep state small and give shared keys reducers.
  `g = StateGraph(State)` · हिंदी: StateGraph में सभी nodes एक state साझा करते हैं; nodes आंशिक updates लौटाते हैं जिन्हें reducers merge करते हैं।
- **319 State — TypedDict** — LangGraph State is a typed shared object, usually a TypedDict, that nodes read and update. Reducers decide whether updates overwrite or merge. Keep it small, and only send needed parts to the LLM.
  `state = merge(state, {'candidates': ['851830']})` · हिंदी: LangGraph State एक typed साझा object है, आमतौर पर TypedDict, जिसे nodes पढ़ते और update करते हैं।
- **320 Nodes in LangGraph** — A node is a function from state to partial state update, the unit of work in LangGraph. Keep nodes small, make side effects idempotent, and record expected errors in state. Only LLM nodes cost tokens.
  हिंदी: Node state से partial state update तक का function है, LangGraph में काम की इकाई।
- **321 Edges in LangGraph** — Edges connect nodes; normal edges are fixed, conditional edges use a router function on the state. Loops need a guard (tries counter and recursion_limit). Deterministic routers keep both cost and behaviour predictable.
  `START, END = ('__start__', '__end__')` · हिंदी: Edges nodes को जोड़ते हैं; normal edges तय होते हैं, conditional edges state पर router function चलाते हैं।
- **322 Conditional Edges** — A conditional edge lets a function pick the next node from the current state. It enables branching, retry loops and human escalation, and only the chosen branch costs tokens. Keep routers pure, typed with `Literal`, and loops capped.
  `builder = StateGraph(TariffState)` · हिंदी: Conditional edge में एक function state देखकर अगला node चुनता है।
- **323 Entry Point + END** — `START` marks where a graph begins and `END` where it stops; compile() checks the wiring. Use several END paths for success, failure and escalation. Put cheap checks first and exit early to save tokens.
  `builder = StateGraph(State)` · हिंदी: `START` बताता है graph कहाँ शुरू होगा और `END` कहाँ रुकेगा; compile() wiring check करता है।
- **324 StateGraph vs MessageGraph** — `StateGraph` holds typed multi-field state; `MessageGraph` only held messages and is now deprecated. Use `StateGraph(MessagesState)` and extend it with your own fields. Reducers decide how parallel updates merge.
  `builder = StateGraph(State)` · हिंदी: `StateGraph` में कई typed fields की state होती है; `MessageGraph` में सिर्फ messages थे और अब deprecated है।
- **325 Checkpointer — Memory** — A checkpointer saves state after each step, keyed by `thread_id`, giving the graph memory across calls. It also powers resume, human-in-the-loop and time-travel. Use a DB saver in production and cap the history sent to the LLM.
  `builder = StateGraph(MessagesState)` · हिंदी: Checkpointer हर step के बाद `thread_id` के साथ state save करता है, जिससे graph को calls के बीच memory मिलती है।
- **326 MemorySaver** — MemorySaver stores graph checkpoints in RAM, keyed by `thread_id`, giving a graph short-term memory. It needs zero setup, so it is ideal for dev and tests.
  `builder = StateGraph(TariffState)` · हिंदी: MemorySaver graph के checkpoints RAM में `thread_id` के साथ रखता है, जिससे short-term memory मिलती है।
- **327 SqliteSaver** — SqliteSaver stores LangGraph checkpoints in a SQLite file, so memory survives restarts with no extra server. Use the async version for async code and open it once in FastAPI lifespan.
  `builder = StateGraph(State)` · हिंदी: SqliteSaver LangGraph checkpoints को SQLite file में रखता है, इसलिए बिना extra server के restart के बाद भी memory बची रहती है।
- **328 RedisSaver** — RedisSaver stores LangGraph checkpoints in Redis so every pod shares one fast memory. Run `setup()` once and set a TTL so old chats expire. Redis is in-memory, so configure persistence or use Postgres if you need strict durability.
  `builder = StateGraph(State)` · हिंदी: RedisSaver LangGraph checkpoints को Redis में रखता है, जिससे सभी pods एक तेज़ shared memory use करते हैं।
- **329 Human in the Loop (HITL)** — HITL pauses a LangGraph run for human approval using a checkpointer, `interrupt()` and `Command(resume=...)`. Only risky or low-confidence cases need a person, and waiting costs no tokens.
  `builder = StateGraph(State)` · हिंदी: HITL में checkpointer, `interrupt()` और `Command(resume=...)` से LangGraph इंसान की मंज़ूरी के लिए रुकता है।
- **330 Interrupt + Resume** — `interrupt(payload)` pauses and saves; `Command(resume=value)` makes the same call return `value` and continues. On resume the node re-runs from its first line, so keep pre-interrupt code idempotent and interrupt order deterministic.
  `builder = StateGraph(State)` · हिंदी: `interrupt(payload)` रोकता और save करता है; `Command(resume=value)` वही call `value` लौटाकर आगे चलाता है।
- **331 Parallel Execution in LangGraph** — Add several edges from one node to run branches in the same super-step, and join with `add_edge([a, b], "join")`. Use reducers for shared keys and `Send` for a dynamic number of branches (map-reduce).
  `builder = StateGraph(State)` · हिंदी: एक node से कई edges जोड़ने पर branches एक ही super-step में चलती हैं, और `add_edge([a, b], "join")` से जुड़ती हैं।
- **332 Subgraphs** — A subgraph is a compiled graph used as a node, giving modularity and reuse. Add it directly when state keys are shared, or use a wrapper node to map state when schemas differ.
  `child_builder = StateGraph(ClassState)` · हिंदी: Subgraph compiled graph है जो node की तरह use होता है, जिससे modularity और reuse मिलता है।
- **333 Multi-Agent with LangGraph** — Multi-agent splits work among focused agents that share one LangGraph state. Edges or `Command` decide who acts next. Use it only when specialisation beats the extra cost, and always cap loops.
  `builder = StateGraph(State)` · हिंदी: Multi-agent में काम focused agents में बँटता है जो एक LangGraph state share करते हैं। Edges या `Command` तय करते हैं कि अगला कौन करेगा।
- **334 Supervisor Pattern** — A supervisor agent picks the next worker (or FINISH) using the shared state, and every worker reports back to it. This gives central control over dynamic workflows. Keep its prompt compact, validate its output and cap the steps.
  `builder = StateGraph(State)` · हिंदी: Supervisor agent shared state देखकर अगला worker (या FINISH) चुनता है और हर worker उसी के पास लौटता है।
- **335 Swarm Pattern** — A swarm has no manager; agents hand off to each other and the active agent keeps the conversation. Store `active_agent` in state with a checkpointer. Whitelist handoffs and cap them to avoid loops and privilege abuse.
  `builder = StateGraph(State)` · हिंदी: Swarm में manager नहीं होता; agents एक-दूसरे को handoff करते हैं और active agent बातचीत संभालता है।
- **336 Handoff Between Agents** — A handoff transfers control with `Command(goto, update)`, either from a node or an LLM-called tool. Tools must also return a matching `ToolMessage` and use `graph=Command.PARENT` when crossing sub-graph boundaries.
  `builder = StateGraph(State)` · हिंदी: Handoff `Command(goto, update)` से control transfer करता है, node से या LLM के call किए tool से।
- **337 LangGraph Streaming** — Streaming returns chunks while the graph runs, chosen by `stream_mode` (`values`, `updates`, `messages`, `custom`, `debug`). It makes apps feel fast and lets you show progress. Filter tokens by node, stop on disconnect, and disable proxy buffering.
  `builder = StateGraph(MessagesState)` · हिंदी: Streaming में graph चलते समय chunks मिलते हैं, जो `stream_mode` से चुने जाते हैं (`values`, `updates`, `messages`, `custom`, `debug`)।
- **338 LangGraph + FastAPI** — Compile the graph once in `lifespan`, call it with `ainvoke`/`astream`, and give each user their own `thread_id`. Validate input, set timeouts and a recursion limit, and map errors to proper HTTP codes.
  `builder = StateGraph(State)` · हिंदी: Graph को `lifespan` में एक बार compile करो, `ainvoke`/`astream` से चलाओ, और हर user को अलग `thread_id` दो।
- **339 LangGraph Deployment** — Deploy a graph either as your own FastAPI app in Docker or through the LangGraph server configured by `langgraph.json`. Production needs a database checkpointer, env-based secrets, health checks and stateless replicas.
  `graph = build()` · हिंदी: Graph को या तो Docker में अपने FastAPI app के रूप में deploy करो, या `langgraph.json` से configure LangGraph server से।
- **340 LangGraph Best Practices** — Keep state small and typed, nodes single-purpose, routers pure, and loops bounded. Use reducers, checkpointers with unique thread ids, and timeouts with retries. Test with fake LLMs and trace real runs.
  हिंदी: State छोटा और typed रखो, nodes एक काम वाले, routers pure और loops सीमित।
- **341 LangGraph Studio** — Studio visualises and debugs LangGraph runs with state inspection, editing, replay and breakpoints. Start it with `langgraph dev` and a `langgraph.json` pointing at your compiled graph.
  `Path('langgraph.json').write_text(json.dumps(config, indent=2))` · हिंदी: Studio LangGraph runs को visualise और debug करता है: state inspect, edit, replay और breakpoints।
- **342 LangGraph Cloud** — LangGraph Cloud hosts your compiled graph as an API with queues, Postgres checkpoints, streaming and cron. Configure with `langgraph.json`, call with the SDK, and keep FastAPI as the auth gateway. Names and pricing change, so check current docs.
  `Path('langgraph.json').write_text(json.dumps(config, indent=2))` · हिंदी: LangGraph Cloud आपके compiled graph को API की तरह host करता है: queues, Postgres checkpoints, streaming और cron के साथ।
- **343 Common LangGraph Patterns** — Learn the standard shapes: router, ReAct loop, reflection, plan-and-execute, fan-out/in, human gate. Choose the simplest one that fits and always cap loops. Parallel branches need reducers.
  `code, rounds = ('', 0)` · हिंदी: मानक आकार सीखो: router, ReAct loop, reflection, plan-and-execute, fan-out/in, human gate।
- **344 LangGraph for RAG** — LangGraph turns RAG into a loop of retrieve, grade, rewrite and generate. Conditional edges let the system retry or admit it does not know. Always bound the loop and watch the extra token cost.
  हिंदी: LangGraph RAG को retrieve, grade, rewrite और generate के loop में बदल देता है।
- **345 LangGraph for Tariff System** — The tariff workflow is a graph of extract, retrieve, classify, validate and finalize. Low confidence or invalid codes pause at a human node using a checkpointer. Validate with deterministic rules and calibrate the threshold with data.
  हिंदी: Tariff workflow extract, retrieve, classify, validate और finalize का graph है।

**Key snippet — 316 LangGraph — What + Why**
```python
class State(TypedDict):
    product: str
    code: str
    attempts: int
```

**Key snippet — 322 Conditional Edges**
```python
class TariffState(TypedDict):
    product: str
    category: str
    hs_code: str
```

**Key snippet — 328 RedisSaver**
```python
class State(TypedDict):
    log: Annotated[list[str], operator.add]
    count: int
def step(state: State) -> dict:
    n = len(state.get('log', [])) + 1
    return {'log': [f'run-{n}'], 'count': n}
```

**Key snippet — 334 Supervisor Pattern**
```python
class State(TypedDict):
    task: str
    hs_code: str
    duty: float
```

**Key snippet — 340 LangGraph Best Practices**
```python
class State(TypedDict):
    desc: str
    code: str
    attempts: int
```

---

## Phase 12 — Multi-Agent (346-365)

- **346 Multi-Agent — What + Why** — Multi-agent splits one big job into small role-based LLM agents. It improves accuracy, modularity and parallelism, but adds cost, latency and complexity. Start with one agent and split only when measurements justify it.
  `extractor = Agent('extractor', 'Extract product attributes')` · हिंदी: Multi-agent एक बड़े काम को छोटे role-based LLM agents में बाँटता है।
- **347 Agent Types + Roles** — Agent types are standard jobs, and roles are written contracts for them. Give each agent one goal, few tools and a typed output. This makes the system testable, safe and cheaper.
  हिंदी: Agent types standard jobs हैं और roles उनके लिखित contracts। हर agent को एक goal, कम tools और typed output दो।
- **348 Agent Communication** — Agents communicate by messages, shared state or a bus. Use typed, addressed messages with a trace id. Always add loop limits and log everything.
  `bus = Bus()` · हिंदी: Agents messages, shared state या bus से communicate करते हैं। Typed, addressed messages और trace id use करो।
- **349 Supervisor Architecture** — A supervisor picks the next worker and decides when to finish. It gives dynamic paths and central control, but adds LLM calls. Always use enums for decisions and a max-step limit.
  हिंदी: Supervisor अगला worker चुनता है और तय करता है कब रुकना है। इससे dynamic paths और central control मिलता है, पर LLM calls बढ़ती हैं।
- **350 Hierarchical Agents** — Hierarchical agents organise workers into teams under supervisors, and a top manager over the teams. This scales routing and ownership for big systems. Keep depth small and pass compact, typed summaries.
  `summary = [t.run(task) for t in teams]` · हिंदी: Hierarchical agents workers को teams में और teams को top manager के नीचे रखते हैं। इससे बड़े systems में routing और ownership scale होती है।
- **351 Peer-to-Peer Agents** — Peer-to-peer agents hand off directly with no central boss. It is fast and flexible but can loop. Use typed handoffs, hop limits and a fallback owner.
  `msg, current = ('shipment held at customs', 'triage')` · हिंदी: Peer-to-peer agents बिना central boss के सीधे handoff करते हैं। यह तेज़ और flexible है पर loop हो सकता है।
- **352 Specialist Agents** — Specialist agents are narrow, domain-focused agents with their own knowledge and tools. They are more accurate and cheaper per call. Always add routing, refusal and a fallback.
  `sp = route(q)` · हिंदी: Specialist agents narrow, domain-focused होते हैं जिनके पास अपना knowledge और tools होते हैं। वे ज़्यादा accurate और प्रति call सस्ते हैं।
- **353 Orchestrator Agent** — The orchestrator plans sub-tasks at run time, sends them to workers and merges the results. It suits variable-size jobs, but needs concurrency limits, retries and completeness checks. LangGraph uses `Send` for this.
  `subtasks = plan(goal)` · हिंदी: Orchestrator run time पर sub-tasks बनाता है, workers को भेजता है और results merge करता है।
- **354 Researcher + Writer Pattern** — The researcher collects sourced notes with tools, and the writer composes only from those notes. This reduces hallucination and makes output traceable. Add an empty-research stop and a grounding check.
  हिंदी: Researcher tools से sourced notes जमा करता है और writer सिर्फ उन्हीं से लिखता है। इससे hallucination घटता है और output traceable बनता है।
- **355 Planner + Executor Pattern** — A planner writes the steps, an executor performs them, a replanner fixes the plan after surprises. It saves cost and gives an inspectable plan. Always cap steps and replans.
  हिंदी: Planner steps लिखता है, executor उन्हें करता है, replanner surprise के बाद plan ठीक करता है। इससे cost बचती है और plan देखा जा सकता है।
- **356 Critic + Generator Pattern** — A generator drafts, a critic checks with a rubric, and the loop repeats until approved. Use strict rubrics, deterministic checks and a round cap. It improves quality but multiplies token cost.
  हिंदी: Generator draft बनाता है, critic rubric से जाँचता है, और approved होने तक loop चलता है। सख़्त rubric, deterministic checks और round cap रखो।
- **357 Agent State Sharing** — Agents share one typed state instead of long messages. Reducers decide how updates merge, so parallel agents do not overwrite each other. Give each agent only the fields it needs.
  हिंदी: Agents लंबे messages की जगह एक typed state शेयर करते हैं।
- **358 Agent Context Management** — Give each agent only the context it needs. Trim, summarise, offload and redact, and keep must-keep facts in structured state. Measure tokens per agent and test accuracy after every change.
  हिंदी: हर agent को सिर्फ उतना context दो जितना चाहिए। Trim, summarise, offload और redact करो, और ज़रूरी facts structured state में रखो।
- **359 Agent Conflict Resolution** — When agents disagree, use deterministic rules first, then voting or a judge, then humans. Log the method and dissent. Same-model agents share errors, so add diversity and independent checks.
  हिंदी: Agents असहमत हों तो पहले deterministic rules, फिर voting या judge, फिर human। तरीका और dissent log करो।
- **360 AutoGen Basics** — AutoGen lets agents collaborate by chatting inside teams with termination rules. Use `AssistantAgent`, `RoundRobinGroupChat` and `team.run`. Watch cost: transcripts grow every turn.
  हिंदी: AutoGen में agents teams के अंदर बातचीत से सहयोग करते हैं और termination rules से रुकते हैं।
- **361 CrewAI Basics** — CrewAI defines agents by role, tasks by expected output, and a crew that runs them in order. Great for fast role-based pipelines. Use schemas, iteration limits and cheap models to stay stable and affordable.
  `result = crew.kickoff(inputs={'product': 'Bluetooth headphones'})` · हिंदी: CrewAI agents को role से, tasks को expected output से और crew को उन्हें चलाने के लिए परिभाषित करता है।
- **362 Multi-Agent Memory** — Multi-agent memory has private, shared and long-term layers with strict scoping. Retrieve only what is relevant and consolidate regularly. Isolate users and expire old data.
  हिंदी: Multi-agent memory में private, shared और long-term परतें होती हैं और दायरा सख़्त रहता है।
- **363 Multi-Agent Tools** — Give each agent a small, role-specific toolset through a registry with permissions. Validate arguments, add timeouts, and make writes idempotent with approval. Keep tool outputs small to save tokens.
  हिंदी: Registry और permissions के ज़रिए हर agent को छोटा, role-आधारित toolset दो।
- **364 Multi-Agent Evaluation** — Evaluate multi-agent systems on outcome, trajectory, cost and latency using a golden dataset. Test agents individually and compare with a single-agent baseline. Automate in CI and monitor production.
  हिंदी: Multi-agent systems को golden dataset से outcome, trajectory, cost और latency पर परखो।
- **365 Multi-Agent Best Practices** — Start simple, give agents single responsibilities, share typed state, and bound steps, tokens and time. Validate in code, gate risky actions with humans, trace everything and evaluate before rollout. More agents is not more intelligence.
  हिंदी: सरल से शुरू करो, agents को एक-एक ज़िम्मेदारी दो, typed state शेयर करो और steps, tokens व समय सीमित रखो।

**Key snippet — 346 Multi-Agent — What + Why**
```python
def fake_llm(role: str, task: str) -> str:
    return f'[{role}] handled: {task}'
```

**Key snippet — 349 Supervisor Architecture**
```python
State = dict[str, str]
def researcher(s: State) -> State:
    return {**s, 'candidates': '6109.10, 6110.20'}
def classifier(s: State) -> State:
    return {**s, 'code': s['candidates'].split(',')[0]}
```

**Key snippet — 352 Specialist Agents**
```python
@dataclass
class Specialist:
    name: str
    keywords: tuple[str, ...]
    notes: str

    def answer(self, q: str) -> str:
        return f"[{self.name}] using '{self.notes}' -> answer for: {q}"
```

**Key snippet — 355 Planner + Executor Pattern**
```python
def classify_hs(x: str) -> str:
    return '8518.22'
def get_duty(code: str) -> float:
    return 0.2
```

**Key snippet — 358 Agent Context Management**
```python
STATE: dict[str, object] = {'description': 'Bluetooth headphones, contact 9876543210', 'origin': 'VN', 'hs_code': '8518.30', 'retrieved_chunks': ['x' * 500] * 40}
VIEWS: dict[str, list[str]] = {'classifier': ['description'], 'duty': ['hs_code', 'origin']}
def redact(text: str) -> str:
    return re.sub('\\b\\d{10}\\b', '[PHONE]', text)
```

---

## Phase 13 — Memory (366-388)

- **366 Memory in AI Apps — Types** — LLMs forget everything between calls, so memory is code that re-injects useful past info. Types: in-context, external, episodic, semantic, procedural. Always bound memory size because every token costs money.
  `mem = AppMemory()` · हिंदी: LLM हर call के बाद भूल जाता है, इसलिए memory वह code है जो पुरानी जानकारी वापस prompt में डालता है।
- **367 In-Context Memory** — In-context memory is the history you resend inside the prompt. It is simple and fast but grows cost every turn and is capped by the context window. Always enforce a token budget.
  `approx_tokens = sum((len(m['content']) for m in messages)) // 4` · हिंदी: In-context memory वह history है जो आप prompt में दोबारा भेजते हैं।
- **368 External Memory** — External memory keeps information in a database and loads only the relevant part into the prompt. It persists across sessions and workers. Isolate by user, set TTLs and fail soft.
  `conn = sqlite3.connect(':memory:')` · हिंदी: External memory जानकारी को database में रखती है और सिर्फ relevant हिस्सा prompt में लाती है। यह sessions और workers के पार बचती है।
- **369 Episodic Memory** — Episodic memory records past events with their outcomes. It is retrieved by similarity to give the agent real examples. Keep episodes compact, verified and time-aware.
  `record('cotton polyester blend shirt', 'HS 6109', 'corrected to 6206', 1)` · हिंदी: Episodic memory पुरानी घटनाओं को उनके नतीजों के साथ record करती है। Similarity से retrieve होकर agent को असली examples देती है।
- **370 Semantic Memory** — Semantic memory keeps stable facts, usually as a small profile. Extract with structured output, validate, and upsert so latest truth wins. Let users view and delete their data.
  `update_profile('I import from Bangladesh and want duty in INR')` · हिंदी: Semantic memory स्थायी facts रखती है, अक्सर छोटी profile के रूप में।
- **371 Procedural Memory** — Procedural memory stores how the agent should behave, mostly as versioned system-prompt rules. Learn from feedback only through an approval gate. Layer rules (safety, tenant, user) and keep them short.
  हिंदी: Procedural memory agent के behaviour के rules रखती है, ज़्यादातर versioned system prompt के रूप में।
- **372 Short-term vs Long-term Memory** — Short-term memory is per conversation; long-term memory is per user across conversations. Key them differently (thread_id vs user_id). Promote durable facts from short-term to long-term in the background.
  `remember_fact('u1', 'currency', 'INR')` · हिंदी: Short-term memory हर बातचीत की होती है; long-term हर user की, बातचीतों के पार। इन्हें अलग keys से रखो (thread_id बनाम user_id)।
- **373 Conversation History Management** — Manage history by validating, cleaning and selecting a view for the LLM while keeping the full log elsewhere. Pin what must persist and keep tool pairs intact. Track tokens every call.
  `final = select(clean(history))` · हिंदी: History को validate, साफ़ और select करके LLM के लिए एक view बनाओ, पूरा log अलग रखो। जो ज़रूरी है उसे pin करो और tool pairs को साथ रखो।
- **374 Sliding Window Memory** — Sliding window memory keeps only the latest messages or tokens, giving bounded cost with no extra calls. It forgets older details, so pin important facts outside it. Use token-based windows and start on a user turn.
  हिंदी: Sliding window memory सिर्फ नवीनतम messages या tokens रखती है, जिससे बिना अतिरिक्त calls के cost सीमित रहती है।
- **375 Summary Memory** — Summary memory compresses old turns into a short running summary and keeps recent turns raw. It remembers decisions at low token cost but is lossy and needs extra LLM calls. Preserve exact facts in structured form.
  हिंदी: Summary memory पुराने turns को छोटे सारांश में बदलती है और हाल के turns को raw रखती है।
- **376 Entity Memory** — Entity memory keeps exact facts per entity in a key-value store. Only facts for entities in the current message go into the prompt. This keeps prompts small and answers consistent.
  `memory = EntityMemory()` · हिंदी: Entity memory हर entity के exact facts key-value store में रखती है। Current message की entities के facts ही prompt में जाते हैं।
- **377 Vector Memory (MemoryVectorStore)** — Vector memory stores memories as embeddings and recalls the closest ones by meaning. The in-memory store is for demos; production needs a persistent vector DB with user filters. Add recency and conflict handling.
  `mem = VectorMemory()` · हिंदी: Vector memory memories को embeddings में रखती है और meaning से सबसे पास वाली recall करती है।
- **378 Zep Memory Server** — Zep is managed memory: send messages, get a context block. It builds a temporal graph so facts stay current. Always handle failures and keep a few raw turns too.
  `zep = FakeZep()` · हिंदी: Zep managed memory है: messages भेजो, context block लो। ये temporal graph बनाता है ताकि facts current रहें।
- **379 mem0 Library** — mem0 gives `add` and `search` for long-term memory. An LLM extracts facts and decides add, update or delete. Scope by user and control add cost.
  `m = MiniMem0()` · हिंदी: mem0 long-term memory के लिए `add` और `search` देता है। LLM facts निकालता है और add, update या delete तय करता है।
- **380 Memory + RAG Together** — RAG brings public knowledge, memory brings user context. Retrieve both in parallel and trim to a budget. Tell the model which source wins on conflicts.
  हिंदी: RAG public knowledge लाता है, memory user context। दोनों को parallel retrieve करो और budget में trim करो।
- **381 Context Window Management** — Decide per call what enters the window and reserve room for the answer. Pin essentials, rank extras, trim oldest, summarise the rest. Bigger windows do not remove the need.
  `history = [f'turn {i}: ' + 'word ' * 10 for i in range(20)]` · हिंदी: हर call में तय करो window में क्या जाएगा और जवाब के लिए जगह रखो।
- **382 Token Budget Management** — Set token limits per section, request, user and month. Count before the call, cap output, record real usage after. Reserve atomically to avoid races.
  `budget = allocate(1000)` · हिंदी: Section, request, user और month हर level पर token limits रखो। Call से पहले गिनो, output cap करो, बाद में असली usage record करो।
- **383 Memory Compression** — Compress memory by facts, dedupe and rolling summaries. Do it in the background when a threshold is crossed. Keep exact facts separate to avoid drift.
  हिंदी: Facts, dedupe और rolling summary से memory compress करो। Threshold पार होने पर background में करो। Drift से बचने के लिए exact facts अलग रखो।
- **384 Memory Retrieval** — Retrieve memories by blending similarity, recency and importance. Use hybrid search and filter by user. Rewrite vague queries first.
  हिंदी: Similarity, recency और importance मिलाकर memories retrieve करो। Hybrid search और user filter इस्तेमाल करो। अस्पष्ट queries पहले rewrite करो।
- **385 Memory Update Strategy** — Decide ADD, UPDATE, DELETE or NONE for each new fact and version the changes. Run cleanup and merging in the background with TTLs. Gate writes to avoid poisoning.
  `m = VersionedMemory()` · हिंदी: हर नए fact पर ADD, UPDATE, DELETE या NONE तय करो और बदलाव version करो। Cleanup और merge background में TTL के साथ चलाओ।
- **386 Memory for Multi-User Apps** — Key memory by tenant, user and thread so users never see each other's data. Take identity from the verified token and keep memory in a shared store, not in process RAM. Trim and expire history to control token cost.
  `store: dict[str, list[Message]] = defaultdict(list)` · हिंदी: Memory को tenant, user और thread की key से रखो ताकि users का data कभी न मिले।
- **387 Memory Security + Privacy** — Redact PII before saving, encrypt at rest, and treat memory as untrusted data, never as instructions. Block poisoned writes and keep scopes separate. Always provide audit logs and a delete path.
  `SUSPICIOUS = ('ignore previous', 'always say', 'system prompt', 'you must remember')` · हिंदी: Save से पहले PII redact करो, rest पर encrypt करो, और memory को untrusted data मानो, instruction नहीं।
- **388 Memory Best Practices** — Split memory into facts, summary and recent turns, and keep the whole block under a token budget. Store only confirmed, useful facts and let newer facts replace older ones. Test memory and track tokens, because summaries lose exact details.
  `mem = ChatMemory()` · हिंदी: Memory को facts, summary और recent turns में बाँटो और पूरा block token budget में रखो।

**Key snippet — 366 Memory in AI Apps — Types**
```python
mem = AppMemory()
mem.semantic['product'] = 'cotton t-shirt'
mem.semantic['origin'] = 'Bangladesh'
mem.procedural.append('Show duty in INR')
```

**Key snippet — 369 Episodic Memory**
```python
@dataclass
class Episode:
    situation: str
    action: str
    outcome: str
    ts: int
```

**Key snippet — 372 Short-term vs Long-term Memory**
```python
short_term: dict[str, list[str]] = {}
long_term: dict[str, dict[str, str]] = {}
def remember_message(thread_id: str, text: str, window: int=4) -> None:
    msgs = short_term.setdefault(thread_id, [])
    msgs.append(text)
    del msgs[:-window]
```

**Key snippet — 376 Entity Memory**
```python
memory = EntityMemory()
memory.extract('Item A is a lithium-ion battery pack. Item A is 48V.')
memory.extract('Item B is a cotton t-shirt.')
```

**Key snippet — 380 Memory + RAG Together**
```python
MEMORY = {'u1': ['usual shipment: 48V batteries, Vietnam to Mumbai']}
DOCS = ['HS 8507.60: lithium-ion accumulators, duty 20 percent', 'HS 6109.10: cotton t-shirts, duty 25 percent']
def overlap(a: str, b: str) -> int:
    return len(set(a.lower().split()) & set(b.lower().split()))
```

---

## Top 10 interview questions

**1. LangGraph vs AgentExecutor: Why did LangChain move agents to LangGraph?** (317)
Control, persistence and extensibility: explicit state and edges, checkpoints, human-in-the-loop, streaming and easier customisation.

**2. State: What is State in LangGraph?** (319)
The shared, typed data passed between nodes; nodes return partial updates that LangGraph merges.

**3. Conditional Edges: What is the difference between `add_edge` and `add_conditional_edges`?** (322)
`add_edge(a, b)` always goes from a to b. `add_conditional_edges(a, fn)` calls `fn(state)` after a finishes and goes to whichever node `fn` returns.

**4. Checkpointer: What does a checkpointer do?** (325)
It saves graph state after each step, keyed by `thread_id`, so later runs continue from the saved state.

**5. Human in the Loop (HITL): What is Human in the Loop?** (329)
A design where an AI workflow pauses at sensitive steps for a person to approve, edit or reject. It improves safety and trust.

**6. Supervisor Pattern: What does the supervisor do?** (334)
It decides which worker acts next (or FINISH) based on state, and receives control back after each worker.

**7. Planner + Executor Pattern: What are the two roles?** (355)
Planner makes the ordered steps; Executor performs one step at a time using tools.

**8. Agent State Sharing: What is shared state?** (357)
One typed object all agents read and write, used instead of passing long messages.

**9. Short-term vs Long-term Memory: Define short-term memory.** (372)
Context for the current conversation: recent messages and working state, scoped to a thread.

**10. Memory Security + Privacy: What is PII?** (387)
Personally Identifiable Information: data that can identify a person, such as name, phone, email, address, Aadhaar, card number. It should be redacted or minimised before storing or sending to an LLM.

