---

# Evaluation Cheatsheet — Evaluation, Observability, Guardrails, Fine-Tuning (Quick Revision)
# हिंदी में: Evaluation, Observability, Guardrails, Fine-Tuning का Quick Revision (Phases 14, 15, 17, 18)

Condensed from topics 389-440 and 461-505. Each topic: gist, one key code line, Hindi hint.
> Prices, model names and IDs shown in the source notes are illustrative; always verify on the provider's official pricing/model pages.

---

## Phase 14 — Evaluation (389-416)

- **389 Why Evaluation Matters** — Evaluation turns "looks fine" into measurable scores on a golden dataset. It catches regressions and shows which component (retriever or generator) is failing. Combine offline gates in CI with online monitoring.
  हिंदी: Evaluation "ठीक लग रहा है" को golden dataset पर measurable scores में बदलता है।
- **390 RAG Evaluation Metrics** — RAG metrics split into retrieval (precision, recall) and generation (faithfulness, relevancy, correctness). Reading their pattern tells you whether to fix the retriever or the prompt/model.
  `faithfulness = overlap(answer, ' '.join(contexts))` · हिंदी: RAG metrics दो भागों में हैं: retrieval (precision, recall) और generation (faithfulness, relevancy, correctness)।
- **391 Faithfulness Score** — Faithfulness = supported claims / total claims, judged against the retrieved context. It catches hallucination but does not prove truth. Use it as an offline metric and a sampled runtime guardrail.
  `score, bad = faithfulness(answer, context)` · हिंदी: Faithfulness = supported claims / कुल claims, retrieved context के against judge किया हुआ। ये hallucination पकड़ता है पर सच साबित नहीं करता।
- **392 Answer Relevancy Score** — Answer relevancy checks that the answer actually responds to the question, using questions generated back from the answer and cosine similarity. It ignores factual truth, so pair it with faithfulness.
  हिंदी: Answer relevancy जाँचता है कि answer सच में सवाल का जवाब देता है, answer से वापस बनाए सवालों और cosine similarity से।
- **393 Context Precision Score** — Context precision rewards putting relevant chunks at the top of the retrieved list (average of Precision@k at relevant ranks). Low precision means noisy or badly ordered retrieval, fixed by reranking and filters.
  हिंदी: Context precision उस retrieval को पुरस्कृत करता है जो relevant chunks को list में ऊपर रखे (relevant ranks पर Precision@k का average)।
- **394 Context Recall Score** — Context recall = share of reference claims found in retrieved context. It tests the retriever, not the generator. It needs ground-truth answers.
  हिंदी: Context recall = reference के कितने claims retrieved context में मिले। ये retriever को test करता है, generator को नहीं।
- **395 Context Relevancy** — Context relevancy = relevant retrieved text / all retrieved text. It needs no ground truth and finds noisy retrieval. Pair it with recall.
  हिंदी: Context relevancy = relevant retrieved text / कुल retrieved text। इसे ground truth नहीं चाहिए और ये noisy retrieval पकड़ता है।
- **396 Answer Correctness** — Answer correctness scores the final answer against a reference using claim F1 plus semantic similarity. It is the end-to-end quality metric. Judge noise and extra true claims affect it.
  हिंदी: Answer correctness final जवाब को reference से claim F1 और semantic similarity से score करता है। ये end-to-end quality metric है।
- **397 Ragas — Complete Guide** — Ragas scores RAG apps with standard LLM-judged metrics over a dataset. Use a pinned, temperature-0 judge and enough rows. Gate releases on trends, not single numbers.
  `dataset = EvaluationDataset.from_list(samples)` · हिंदी: Ragas dataset पर standard LLM-judged metrics से RAG apps को score करता है। Pinned, temperature-0 judge और काफ़ी rows इस्तेमाल करो।
- **398 Ragas Setup** — Install pinned Ragas, set keys in the environment, and configure judge LLM and embeddings. Use the 0.2+ column names and a RunConfig. Always smoke-test with a few rows first.
  `issues = check_env() + check_rows(rows)` · हिंदी: Pinned Ragas install करो, keys environment में रखो, और judge LLM व embeddings configure करो। 0.2+ column names और RunConfig इस्तेमाल करो।
- **399 Ragas Dataset Creation** — A Ragas dataset is rows of question, contexts, response and reference. Build it by running your RAG per question and wrapping outputs in SingleTurnSample. Keep it versioned, diverse and free of leakage.
  हिंदी: Ragas dataset में question, contexts, response और reference की rows होती हैं। हर question पर RAG चलाकर SingleTurnSample में रखो।
- **400 Ragas Evaluation Pipeline** — Pipeline = dataset + metrics + pinned judge + evaluate + thresholds. Use per-row output to debug, not only the mean. Pin the judge, handle NaN, and gate CI.
  `agg = aggregate(scores_per_row)` · हिंदी: Pipeline = dataset + metrics + pinned judge + evaluate + thresholds। Debug के लिए सिर्फ mean नहीं, per-row output देखो।
- **401 Ragas with OpenAI** — Ragas with OpenAI = ChatOpenAI judge + OpenAIEmbeddings wrapped for Ragas. Pin temperature 0, control concurrency with RunConfig, and watch NaN rows. Use a cheap judge daily and a strong one for calibration.
  `PRICES: dict[str, tuple[float, float]] = {'gpt-4o-mini': (0.15, 0.6), 'gpt-4o': (2.5, 10.0)}` · हिंदी: Ragas with OpenAI = ChatOpenAI judge + OpenAIEmbeddings, Ragas के लिए wrap किए हुए।
- **402 Ragas with Claude** — Use ChatAnthropic wrapped with LangchainLLMWrapper as a Ragas judge; embeddings come from another provider. Never compare absolute scores across different judges. Validate the judge against human labels.
  हिंदी: ChatAnthropic को LangchainLLMWrapper से wrap करके Ragas judge बनाओ; embeddings दूसरे provider से।
- **403 LLM as Judge Pattern** — LLM-as-judge grades outputs with a rubric and structured JSON. Control bias with order swapping, clear rubrics and temperature 0. Always calibrate against human labels.
  `v = parse(fake_judge(build_prompt('HS code for iPhone?', '8517.13')))` · हिंदी: LLM-as-judge rubric और structured JSON से outputs grade करता है। Order swap, साफ rubric और temperature 0 से bias कम करो।
- **404 G-Eval Framework** — G-Eval = criteria, auto steps, form prompt, probability-weighted score. It gives smoother scores than plain judges. Still validate against humans and avoid over-reading small gaps.
  `fake = {'4': math.log(0.6), '3': math.log(0.25), '5': math.log(0.1), 'The': math.log(0.05)}` · हिंदी: G-Eval = criteria, auto steps, form prompt, probability-weighted score। यह साधारण judges से smooth scores देता है।
- **405 DeepEval Library** — DeepEval brings pytest-style testing to LLM apps with ready metrics and thresholds. Build LLMTestCases, run `deepeval test run`, and gate CI. Control flakiness and cost with pinned judge and tiered suites.
  `tc = TestCase('HS code?', 'Code is 8507.60', ['8507.60 covers lithium-ion accumulators'])` · हिंदी: DeepEval LLM apps में pytest-style testing लाता है, ready metrics और thresholds के साथ।
- **406 TruLens Library** — TruLens traces your app and scores each record with feedback functions, centred on the RAG Triad. Compare versions in the dashboard and fix the weakest triad leg. Sample production traffic to control cost.
  हिंदी: TruLens आपके app को trace करता है और हर record को feedback functions से score करता है, RAG Triad पर केंद्रित।
- **407 Evaluation Dataset Creation** — A good eval dataset is representative, labelled, tagged, de-duplicated, split and versioned. Freeze the test split and report per-slice scores. Feed it with production logs, expert cases and every bug.
  `clean = dedupe(rows)` · हिंदी: अच्छा eval dataset representative, labelled, tagged, de-duplicated, split और versioned होता है।
- **408 Synthetic Test Data** — Synthetic data is LLM-generated test rows grounded in your documents. Add personas, filter for answerability, dedupe and human-check a sample. Never rely on it alone.
  हिंदी: Synthetic data आपके documents पर आधारित LLM-generated test rows हैं।
- **409 Golden Dataset** — A golden dataset is a small expert-verified, locked and versioned test set. Check annotator agreement, adjudicate and keep it out of prompts. Use it for release gates and judge calibration.
  हिंदी: Golden dataset छोटा expert-verified, locked और versioned test set है। Annotator agreement जाँचो, adjudicate करो और इसे prompts से बाहर रखो।
- **410 Human Evaluation** — Human evaluation is the trusted but expensive standard: blind, randomised, rubric-based, multiple raters. Measure agreement and adjudicate conflicts. Use it to build golden sets and calibrate automated judges.
  हिंदी: Human evaluation भरोसेमंद पर महँगा standard है: blind, random, rubric-आधारित, कई raters। Agreement नापो और मतभेद सुलझाओ।
- **411 A/B Testing RAG Systems** — A/B test RAG changes on live users with deterministic bucketing, a primary metric and guardrails. Fix sample size, avoid peeking, and use a z-test. Watch cost and latency per arm.
  `z, p = z_test(1560, 2000, 1630, 2000)` · हिंदी: RAG बदलावों को live users पर deterministic bucketing, primary metric और guardrails के साथ A/B test करो।
- **412 Retrieval Evaluation** — Retrieval evaluation tests the retriever alone with labelled relevant chunks and metrics like Recall@k, MRR and nDCG. It shows whether failures come from retrieval or generation. Report by slice and keep labels in sync with chunking.
  हिंदी: Retrieval evaluation labelled relevant chunks और Recall@k, MRR, nDCG जैसे metrics से सिर्फ retriever को परखता है।
- **413 Generation Evaluation** — Evaluate generation separately using gold context, deterministic checks, reference comparisons and LLM-judged dimensions. Faithfulness is not correctness, so track both. Fix the weakest dimension first.
  `HS = re.compile('^\\d{4}\\.\\d{2}')` · हिंदी: Generation को gold context, deterministic checks, reference तुलना और LLM-judged dimensions से अलग evaluate करो।
- **414 End-to-End Evaluation** — E2E evaluation runs the full production pipeline on a golden dataset and scores the final answers. It catches integration bugs that component metrics miss, but needs component evals and traces to find the root cause.
  हिंदी: E2E evaluation golden dataset पर पूरा production pipeline चलाकर final answers को score करता है।
- **415 Evaluation in CI/CD Pipeline** — CI/CD evaluation runs your golden dataset automatically on every PR and blocks merges if accuracy falls below a floor or regresses against the main baseline. Use a small smoke set per PR and a full suite nightly, with temperature 0 to reduce noise.
  `CASES: list[tuple[str, str]] = [('power bank', '8507'), ('laptop', '8471'), ('banana', '0803')]` · हिंदी: CI/CD evaluation हर PR पर golden dataset चलाता है और accuracy floor से नीचे या baseline से कम हो तो merge रोकता है।
- **416 Evaluation Best Practices** — Good evals use a representative, versioned golden dataset, a held-out test set, several focused metrics and a judge calibrated against humans. Prefer deterministic checks and watch for overfitting and judge bias.
  `random.seed(42)` · हिंदी: अच्छे evals में representative और versioned golden dataset, held-out test set, कई focused metrics और human से calibrate किया हुआ judge होता…

**Key snippet — 390 RAG Evaluation Metrics**
```python
def words(text: str) -> set[str]:
    """Lowercase word set without punctuation."""
    return set(re.findall('[a-z0-9.]+', text.lower()))
def overlap(a: str, b: str) -> float:
    """Fraction of words of `a` that also appear in `b`."""
    wa = words(a)
    return len(wa & words(b)) / len(wa) if wa else 0.0
```

**Key snippet — 399 Ragas Dataset Creation**
```python
class Row(TypedDict):
    user_input: str
    retrieved_contexts: list[str]
    response: str
    reference: str
```

**Key snippet — 408 Synthetic Test Data**
```python
CHUNKS: dict[str, str] = {'8507.60': 'lithium-ion accumulators', '8517.13': 'smartphones', '6109.10': 'cotton T-shirts'}
TEMPLATES: list[str] = ['What is the HS code for {item}?', 'hs code {item} pls', 'Which heading covers {item} for import?']
def typo(s: str, rng: random.Random) -> str:
    if len(s) < 6:
        return s
    i = rng.randrange(1, len(s) - 2)
    return s[:i] + s[i + 1] + s[i] + s[i + 2:]
```

---

## Phase 15 — Observability (417-440)

- **417 LangSmith — What + Why** — LangSmith records every step of an LLM request as a trace, with tokens, cost, latency and errors. It also holds datasets, evaluations, prompts and monitoring. Set three env vars for LangChain apps, or use `@traceable` for any other code.
  `answer('power bank')` · हिंदी: LangSmith LLM request के हर step को trace के रूप में record करता है, tokens, cost, latency और errors के साथ।
- **418 LangSmith Setup** — Install `langsmith`, create an API key, and set `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY` and `LANGSMITH_PROJECT`. Use separate keys and projects per environment, and validate the setup at startup without crashing the app.
  हिंदी: `langsmith` install करो, API key बनाओ और `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT` set करो।
- **419 Tracing in LangSmith** — Tracing captures every step of a request as a tree of runs with inputs, outputs, tokens, latency and errors. LangChain/LangGraph are traced automatically; other code uses `@traceable` and `wrap_openai`.
  `classify('power bank')` · हिंदी: Tracing request के हर step को runs के tree के रूप में inputs, outputs, tokens, latency और errors के साथ पकड़ती है।
- **420 Projects in LangSmith** — A project groups traces; set it with `LANGSMITH_PROJECT` or `tracing_context(project_name=...)`. Use `<app>-<env>` names and keep versions/users in tags and metadata. Separate projects give clean metrics, access control and cost views.
  हिंदी: Project traces को group करता है; इसे `LANGSMITH_PROJECT` या `tracing_context(project_name=...)` से set करो।
- **421 Runs in LangSmith** — A run is one step execution with inputs, outputs, timing, tokens and status; the root run is the trace. Query runs with `client.list_runs` and filters to find slow, failing or costly steps.
  हिंदी: Run एक step का execution है जिसमें inputs, outputs, timing, tokens और status होते हैं; root run ही trace है।
- **422 Feedback in LangSmith** — Feedback attaches scores and comments to runs from users, reviewers or evaluators. Return the run id with each answer and post feedback in the background without blocking users.
  `STORE: dict[str, list[Feedback]] = defaultdict(list)` · हिंदी: Feedback users, reviewers या evaluators से runs पर score और comment जोड़ता है।
- **423 Datasets in LangSmith** — A LangSmith dataset stores examples with inputs, reference outputs and metadata, versioned automatically. Use splits to separate tuning from honest testing, and feed expert-corrected production failures back in.
  `DATASET.append(Example({'product': 'silk saree'}, {'hs_code': '5007.20'}))` · हिंदी: LangSmith dataset में inputs, reference outputs और metadata वाले examples रहते हैं, और versioning अपने-आप होती है।
- **424 Evaluation in LangSmith** — `evaluate()` runs your target over a dataset, scores outputs with evaluators and stores an experiment you can compare. Use code evaluators first and LLM judges for fuzzy qualities, with temperature 0 and repetitions to measure noise.
  हिंदी: `evaluate()` आपके target को dataset पर चलाता है, evaluators से outputs score करता है और compare करने लायक experiment सहेजता है।
- **425 LangSmith Hub (Prompts)** — The Hub stores prompts with commits and tags so they can be edited, evaluated and rolled back without redeploying code. Pull by tag, cache with a TTL and keep a local fallback. Always evaluate before moving the `prod` tag.
  `reg = PromptRegistry()` · हिंदी: Hub prompts को commits और tags के साथ रखता है ताकि बिना redeploy के edit, evaluate और rollback हो सके।
- **426 LangSmith Monitoring** — LangSmith monitoring shows traffic, errors, latency percentiles, tokens, cost and feedback for live projects. Add automation rules for online evaluation and alerts on error rate, tail latency, cost and quality. Monitor quality, not only uptime.
  `data = [RunRec(1.0, False, 1400)] * 90 + [RunRec(14.0, True, 0)] * 10` · हिंदी: LangSmith monitoring live projects के लिए traffic, errors, latency percentiles, tokens, cost और feedback दिखाता है।
- **427 Langfuse — Alternative** — Langfuse is an open-source, self-hostable alternative to LangSmith for traces, evals and prompt management. It is framework neutral and good for data-residency needs. Mask PII and flush events before exit.
  हिंदी: Langfuse LangSmith का open-source, self-host होने वाला विकल्प है: traces, evals और prompt management के लिए।
- **428 Langfuse Setup** — Create a project, get public/secret keys, install the SDK and set env vars. Verify with auth_check and a smoke-test trace. Flush on shutdown and keep one project per environment.
  `REQUIRED = ('LANGFUSE_PUBLIC_KEY', 'LANGFUSE_SECRET_KEY', 'LANGFUSE_HOST')` · हिंदी: Project बनाओ, public/secret keys लो, SDK install करो और env vars set करो। auth_check और smoke-test trace से verify करो।
- **429 Langfuse Tracing** — Langfuse records each request as a trace of nested spans and generations with latency, tokens and cost. Use `@observe`, the OpenAI drop-in client or the LangChain callback, and always set user and session ids.
  हिंदी: Langfuse हर request को trace के रूप में record करता है, nested spans और generations के साथ latency, tokens और cost।
- **430 Langfuse Evaluation** — Langfuse evaluation = datasets plus scores. Run your app on golden items, score with code, LLM judge and user feedback, and compare runs. Put it in CI to catch regressions and sample live traffic for drift.
  हिंदी: Langfuse evaluation = datasets और scores। Golden items पर app चलाओ, code, LLM judge और user feedback से score करो और runs की तुलना करो।
- **431 Phoenix (Arize) Tracing** — Phoenix is an OTel-native, open-source tracing and eval tool. Register a tracer provider, call the instrumentor once, and every OpenAI or LangChain call is traced. Great for notebooks and retrieval debugging; secure it in production.
  `llm_span('gpt-4o-mini', 'HS code for Bluetooth speaker?', '8518.22')` · हिंदी: Phoenix OTel-native open-source tracing और eval tool है।
- **432 OpenTelemetry for AI Apps** — OpenTelemetry is the vendor-neutral standard for traces, metrics and logs. For AI apps, add spans with GenAI attributes, token and latency metrics, and propagate context across services. Use the Collector for sampling, redaction and vendor choice.
  `resource = Resource.create({'service.name': 'tariff-api'})` · हिंदी: OpenTelemetry traces, metrics और logs का vendor-neutral standard है।
- **433 AI Observability Metrics** — Track reliability, performance, cost and quality together; HTTP 200 does not mean a correct answer. Use percentiles, low-cardinality labels, and SLOs with burn-rate alerts. Always add a sampled quality metric.
  `PRICE_IN, PRICE_OUT = (0.15 / 1000000.0, 0.6 / 1000000.0)` · हिंदी: Reliability, performance, cost और quality चारों साथ track करो; HTTP 200 का मतलब सही जवाब नहीं।
- **434 Cost Tracking per Request** — Compute cost from `usage` tokens and a versioned price table, and sum every call per request with a contextvar. Tag by user, feature and model, enforce budgets, and reconcile with the invoice.
  `PRICES: dict[str, tuple[float, float]] = {'gpt-4o-mini': (0.15, 0.6), 'gpt-4o': (2.5, 10.0)}` · हिंदी: `usage` tokens और versioned price table से cost निकालो और contextvar से हर request की सारी calls जोड़ो।
- **435 Latency Tracking** — Time every step with a monotonic clock, record TTFT and tokens per second for streams, and report percentiles by step. The tail (p95/p99) is what users feel. Fix the dominant step first: usually output length, rerank or queueing.
  `SAMPLES: dict[str, list[float]] = defaultdict(list)` · हिंदी: हर step को monotonic clock से नापो, streams के लिए TTFT और tokens/sec रखो और step के हिसाब से percentiles report करो।
- **436 Error Tracking in AI Apps** — Track hard, soft and silent errors separately. Retry only transient failures with backoff and jitter, validate outputs with schemas, and fall back safely. Log with request ids and alert on error types.
  `COUNTS: Counter[str] = Counter()` · हिंदी: Hard, soft और silent errors अलग track करो।
- **437 Token Usage Monitoring** — Monitor input, output and cached tokens by feature and prompt version, with part-wise breakdown. Alert on relative jumps and on truncation (`finish_reason=length`). Fix bloat by trimming history, reducing top_k and caching prefixes.
  `WINDOW: deque[int] = deque(maxlen=50)` · हिंदी: Feature और prompt version के हिसाब से input, output और cached tokens को part-wise नापो।
- **438 Model Performance Monitoring** — Monitor answer quality, not just uptime: sample and label production traffic, run a daily golden canary, and slice metrics by segment. Pin model snapshots and alert on drops with enough samples. Feed failures back into the golden set.
  `results: dict[str, deque[int]] = defaultdict(lambda: deque(maxlen=WINDOW))` · हिंदी: सिर्फ uptime नहीं, जवाबों की quality monitor करो: production traffic sample और label करो, रोज़ golden canary चलाओ और segment के हिसाब से me…
- **439 Drift Detection** — Drift detection compares current inputs, retrieval scores and outputs with a reference window using PSI, KS tests or embedding distance. It warns you before labelled accuracy drops. Respond by updating data, prompts and golden sets.
  `score = psi(ref, cur)` · हिंदी: Drift detection current inputs, retrieval scores और outputs की तुलना reference window से PSI, KS test या embedding distance से करता है।
- **440 AI Observability Best Practices** — Trace everything with version tags, track tokens, cost, latency and quality. Redact PII, sample sensibly and alert on cost, latency and quality drops. Feed failures into regression evals.
  हिंदी: हर चीज़ version tags के साथ trace करो, tokens, cost, latency और quality track करो।

**Key snippet — 419 Tracing in LangSmith**
```python
current_run: contextvars.ContextVar[str | None] = contextvars.ContextVar('current_run', default=None)
RUNS: list[dict[str, Any]] = []
```

**Key snippet — 426 LangSmith Monitoring**
```python
@dataclass
class RunRec:
    latency_s: float
    error: bool
    tokens: int
```

**Key snippet — 434 Cost Tracking per Request**
```python
PRICES: dict[str, tuple[float, float]] = {'gpt-4o-mini': (0.15, 0.6), 'gpt-4o': (2.5, 10.0)}
def cost_usd(model: str, in_tok: int, out_tok: int) -> float:
    if model not in PRICES:
        raise KeyError(f'no price for model {model}')
    pin, pout = PRICES[model]
    return (in_tok * pin + out_tok * pout) / 1000000
```

---

## Phase 17 — Guardrails (461-485)

- **461 AI Safety — Why Critical** — AI safety prevents harm from hallucination, data leaks, injection and toxic output. Use layered checks, fail closed, and monitor everything. Prompts alone are not safety.
  हिंदी: AI safety hallucination, data leak, injection और toxic output से नुकसान रोकती है।
- **462 Hallucination — Types + Causes** — Hallucination is confident but unsupported output, caused by next-token prediction, missing knowledge and weak context. Main types are factual, fabricated source, contradiction and reasoning errors. Name the type first, then choose the fix.
  हिंदी: Hallucination आत्मविश्वासी लेकिन unsupported output है, जिसका कारण next-token prediction, missing knowledge और कमज़ोर context है।
- **463 Hallucination Detection** — Detection compares answers with evidence using rules, claim-level judges and consistency checks. Always verify against external truth like a database, not the model's own opinion. Pick thresholds from labelled data.
  हिंदी: Detection में जवाब की evidence से तुलना rules, claim-level judges और consistency checks से होती है।
- **464 Hallucination Prevention** — Prevent hallucination by giving evidence, using tools for exact data, constraining output and verifying. Always allow the model to say "I don't know". Prompts alone do not work.
  हिंदी: Evidence देकर, exact data के लिए tools लगाकर, output सीमित करके और verify करके hallucination रोको।
- **465 Grounding Responses** — Grounding ties each claim to a retrieved source with an id. Instruct the model to use only sources, cite ids, and abstain if missing. Verify citations in code.
  हिंदी: Grounding हर claim को id के साथ retrieved source से जोड़ती है।
- **466 Citation + Source Verification** — Verify that citations exist, come from trusted current sources and truly support the claim. Use cheap deterministic checks first, then a judge. Never render model-written URLs.
  हिंदी: Verify करो कि citations मौजूद हैं, भरोसेमंद ताज़ा sources से हैं और claim को सच में support करते हैं।
- **467 Fact Checking in RAG** — Fact checking extracts claims from a RAG answer and verifies them against a database or evidence. Route typed facts to authoritative data and text facts to a judge. Fix, remove or escalate failures.
  हिंदी: Fact checking RAG answer से claims निकालकर database या evidence से verify करती है।
- **468 Guardrails AI Library** — Guardrails AI wraps LLM calls with validators and policies like reask, fix and exception. Use Pydantic schemas plus Hub validators. Cap reasks to control cost.
  `conf_range = lambda d: None if 0 <= d.get('confidence', -1) <= 1 else 'bad confidence'` · हिंदी: Guardrails AI LLM calls को validators और reask, fix, exception जैसी policies से घेरती है। Pydantic schemas और Hub validators use करो।
- **469 NeMo Guardrails** — NeMo Guardrails adds input, dialog and output rails defined in YAML and Colang. It controls topics and conversation flows outside the prompt. Self-check rails add LLM calls, so watch latency and cost.
  `ALLOWED_TOPICS = ('tariff', 'customs', 'hs code', 'duty', 'import', 'export')` · हिंदी: NeMo Guardrails YAML और Colang में तय input, dialog और output rails जोड़ता है।
- **470 Input Guardrails** — Input guardrails validate, clean and screen all text before the model sees it. Combine size limits, rate limits, injection detection and PII redaction. Treat documents and tool results as untrusted too.
  `PHONE = re.compile('\\b\\d{10}\\b')` · हिंदी: Input guardrails model के देखने से पहले सारा text validate, साफ और screen करते हैं।
- **471 Output Guardrails** — Output guardrails validate structure, redact PII and secrets, and check policy and grounding before delivery. Retry once with feedback, then fall back safely. They are the last line of defence.
  `PHONE = re.compile('\\b\\d{10}\\b')` · हिंदी: Output guardrails delivery से पहले structure validate करते हैं, PII और secrets redact करते हैं, और policy व grounding जाँचते हैं।
- **472 PII Detection + Redaction** — Detect PII with regex plus NER, then mask or tokenise it before the LLM, logs and caches. Keep the mapping on your server and restore values only for authorised users. Measure recall.
  हिंदी: Regex और NER से PII खोजो, फिर LLM, logs और caches से पहले उसे mask या tokenise करो।
- **473 Toxic Content Detection** — Toxic content detection scores input and output by category and applies per-category actions. Combine a fast blocklist with a classifier and test on Hindi and Hinglish. Tune thresholds with real labelled data.
  हिंदी: Toxic content detection input और output को category के हिसाब से score करता है और हर category की अलग कार्रवाई करता है।
- **474 Prompt Injection Detection** — Prompt injection hides instructions in user or fetched content; detect with normalisation, rules and a judge model. Scan retrieved content too, not only user input. Detection is one layer; limit tool privileges to limit damage.
  हिंदी: Prompt injection user या fetched content में instructions छुपाता है; normalisation, rules और judge model से पहचानो।
- **475 Off-Topic Detection** — Off-topic detection keeps the assistant inside its domain using keywords, embedding similarity and a small LLM fallback. It runs before the main LLM and saves tokens. Use conversation context and fail open to avoid annoying users.
  हिंदी: Off-topic detection keywords, embedding similarity और छोटे LLM fallback से assistant को domain में रखता है।
- **476 Confidence Scoring** — Confidence scores combine logprobs, sample agreement, retrieval support and hard validation. Calibrate on labelled data and route by threshold: auto, review, fallback. Do not trust the model's own verbal confidence.
  हिंदी: Confidence score logprobs, sample agreement, retrieval support और hard validation को मिलाता है।
- **477 Uncertainty Quantification** — UQ measures how unsure and why, using sampling entropy and retrieval support. Ambiguous input means ask the user; missing knowledge means retrieve or escalate. It cannot catch consistent errors, so keep ground-truth validation.
  `normalised = entropy(vague) / max_entropy(len(vague))` · हिंदी: UQ sampling entropy और retrieval support से बताता है कि model कितना और क्यों अनिश्चित है।
- **478 Fallback Responses** — Fallbacks give safe, honest replies when the normal path fails or is unsure. Use a ladder: retry, backup model, cache or rules, ask for details, human. Always mark and log fallbacks and never present guesses as facts.
  `KEYWORDS = {'phone': '85 (electrical machinery)', 'shirt': '62 (apparel)'}` · हिंदी: Fallbacks तब सुरक्षित, ईमानदार जवाब देते हैं जब normal रास्ता fail या अनिश्चित हो।
- **479 Content Filtering** — Content filtering checks inputs and outputs against policy and blocks, redacts or flags violations. Layer cheap rules, classifiers and human review, and tune thresholds per category. Blocked inputs save LLM tokens.
  हिंदी: Content filtering inputs और outputs को policy से check करके violations block, redact या flag करता है।
- **480 Safety Layer in FastAPI** — A safety layer wraps every LLM call with an input guard and an output guard. Use middleware for cheap, global checks and `Depends` for content checks. Blocking early saves tokens and money.
  `PHONE_RE = re.compile('\\b\\d{10}\\b')` · हिंदी: Safety layer हर LLM call को input guard और output guard से घेरता है।
- **481 OWASP LLM Top 10** — OWASP LLM Top 10 is the standard checklist of LLM risks: injection, disclosure, output handling, excessive agency, unbounded consumption and more. Map every applicable risk to a control and a test.
  हिंदी: OWASP LLM Top 10 LLM risks की standard checklist है: injection, disclosure, output handling, excessive agency, unbounded consumption आदि।
- **482 LLM Security Best Practices** — Stack many controls: least privilege, role separation, input and output validation, usage limits, secret hygiene, logging and red-team tests. Treat the model and its output as untrusted, and the system prompt as not secret.
  हिंदी: कई controls साथ लगाओ: least privilege, role separation, input/output validation, usage limits, secret hygiene, logging और red-team tests।
- **483 Responsible AI Principles** — Responsible AI turns values into tests: fairness, privacy, transparency, accountability, oversight.
  हिंदी: Responsible AI values को tests में बदलता है: fairness, privacy, transparency, accountability, oversight।
- **484 Bias Detection** — Bias detection measures gaps between groups instead of trusting average accuracy.
  `acc = group_accuracy(rows)` · हिंदी: Bias detection average accuracy पर भरोसा करने की जगह groups के gap मापता है।
- **485 Fairness in AI Systems** — Fairness needs a chosen definition tied to real harm.
  हिंदी: Fairness के लिए real harm से जुड़ी एक definition चुननी पड़ती है।

**Key snippet — 461 AI Safety — Why Critical**
```python
RISKS: dict[str, dict[str, int]] = {'hallucination': {'impact': 5, 'likelihood': 4}, 'pii_leak': {'impact': 5, 'likelihood': 2}, 'prompt_injection': {'impact': 4, 'likelihood': 3}, 'toxicity': {'impact': 3, 'likelihood': 1}}
ranked = sorted(RISKS.items(), key=lambda kv: kv[1]['impact'] * kv[1]['likelihood'], reverse=True)
for name, r in ranked:
    print(f"{name:18} score={r['impact'] * r['likelihood']}")
```

**Key snippet — 470 Input Guardrails**
```python
MAX_CHARS = 2000
INJECTION = re.compile('(ignore (all |your )?(previous|prior)? ?(rules|instructions)|reveal (the )?system prompt)', re.I)
PHONE = re.compile('\\b\\d{10}\\b')
```

**Key snippet — 477 Uncertainty Quantification**
```python
def entropy(samples: list[str]) -> float:
    counts = Counter(samples)
    total = len(samples)
    return -sum((c / total * math.log2(c / total) for c in counts.values()))
```

---

## Phase 18 — Fine-Tuning (486-505)

- **486 Fine Tuning — What + Why** — Fine tuning trains a pre-trained model further on your examples so it learns style, format and narrow tasks.
  `base_tokens: int = rough_tokens(few_shot_prompt)` · हिंदी: Fine tuning pre-trained model को आपके examples पर और train करती है ताकि वह style, format और narrow task सीखे।
- **487 Fine Tuning vs RAG** — RAG is for knowledge that changes or is private; fine tuning is for behaviour, format and narrow skills.
  हिंदी: RAG बदलती या private knowledge के लिए है; fine tuning behaviour, format और narrow skills के लिए।
- **488 When to Fine Tune** — Fine tune only after prompting and RAG fail to meet the quality bar.
  `score: int = sum(signals.values())` · हिंदी: Fine tune तभी करो जब prompting और RAG quality bar पूरा न करें।
- **489 When NOT to Fine Tune** — Do not fine tune for changing facts, tiny or noisy data, missing evals or when prompts already work.
  हिंदी: बदलते facts, छोटे या noisy data, eval न होने पर या prompt पहले से चल रहा हो तो fine tune मत करो।
- **490 OpenAI Fine Tuning** — Upload JSONL, create a job on a supported base model, wait for status succeeded.
  `client = OpenAI()` · हिंदी: JSONL upload करो, supported base model पर job बनाओ, status succeeded का इंतज़ार करो।
- **491 Fine Tuning Data Format (JSONL)** — Chat fine tuning data is JSONL with a `messages` list per line, ending with the assistant answer.
  हिंदी: Chat fine tuning data JSONL होता है, हर line में `messages` list और आख़िर में assistant का जवाब।
- **492 Training Data Preparation** — Prepare data by cleaning, deduplicating, masking PII, reviewing labels, balancing and splitting by group.
  `seen = set()` · हिंदी: Data को साफ़ करो, dedupe करो, PII mask करो, labels review करो, balance करो और group के हिसाब से split करो।
- **493 Fine Tuning Hyperparameters** — Epochs, batch size and learning rate control how strongly the model is changed.
  हिंदी: Epochs, batch size और learning rate तय करते हैं कि model कितना बदले।
- **494 Fine Tuning Cost Estimation** — Training cost is tokens x epochs x price; serving cost depends on tokens per call.
  `tokens_per_epoch: int = sum((approx_tokens(r) for r in rows))` · हिंदी: Training cost = tokens x epochs x price; serving cost हर call के tokens पर निर्भर है।
- **495 Fine Tuning Evaluation** — Evaluate tuned models on a held-out test set against the best baseline.
  `preds = [parse(o) for o, _ in results]` · हिंदी: Tuned model को held-out test set पर सबसे अच्छे baseline से compare करो।
- **496 LoRA — What + Why** — LoRA freezes the base model and trains two tiny matrices per chosen layer. It cuts GPU memory and gives small, swappable adapters. Best for style, format and domain adaptation, not for adding lots of facts.
  हिंदी: LoRA base model को freeze करके हर चुनी layer में दो छोटे matrices train करता है।
- **497 QLoRA — What + Why** — QLoRA trains LoRA adapters on top of a frozen 4-bit quantized model. It makes 7B-70B fine-tuning possible on small GPUs. Merge carefully because of quantization error.
  हिंदी: QLoRA frozen 4-bit quantized model के ऊपर LoRA adapters train करता है। इससे छोटे GPUs पर 7B-70B fine-tuning संभव होती है।
- **498 Hugging Face Fine Tuning** — Hugging Face gives datasets, transformers, peft and trl to fine-tune open models you control. Prepare chat-format JSONL, use LoRA with SFTTrainer, and always evaluate on held-out data. Best when privacy and unit cost matter.
  हिंदी: Hugging Face datasets, transformers, peft और trl देता है ताकि आप अपने control वाले open models fine-tune करें।
- **499 Supervised Fine Tuning (SFT)** — SFT teaches a model by imitation on labelled prompt-answer pairs, with loss on answer tokens only. It fixes format and style, not missing knowledge. Data quality matters more than quantity.
  हिंदी: SFT labelled prompt-answer pairs की नक़ल से model सिखाता है, loss सिर्फ़ answer tokens पर।
- **500 RLHF Basics** — RLHF = SFT, then a reward model learned from human comparisons, then RL (PPO) with a KL penalty. It optimises subjective qualities beyond imitation. It is costly and fragile, so try prompting, SFT and DPO first.
  हिंदी: RLHF = SFT, फिर human comparisons से reward model, फिर KL penalty के साथ RL (PPO)। यह imitation से आगे subjective quality सुधारता है।
- **501 DPO — Direct Preference Optimization** — DPO trains a model on (prompt, chosen, rejected) pairs using a simple loss against a frozen reference. It needs no reward model or RL loop, and works best after SFT. Build pairs that differ only in quality and judge with a task eval.
  हिंदी: DPO (prompt, chosen, rejected) pairs और frozen reference से सीधे model train करता है।
- **502 Continued Pre-training** — CPT trains an open base model on raw domain text to learn vocabulary and facts. Mix in general data, use a low learning rate, and follow with SFT. Use it only for stable, specialised knowledge; use RAG for changing facts.
  `out = pack_tokens(docs, block=6, eos=0)` · हिंदी: CPT open base model को raw domain text पर train करता है ताकि vocabulary और facts सीखे।
- **503 Domain Adaptation** — Domain adaptation is a ladder: prompt, RAG, SFT, DPO, continued pre-training. Build an eval set first and climb only as far as the measured gap needs. Put changing facts in retrieval and behaviour in weights.
  हिंदी: Domain adaptation एक सीढ़ी है: prompt, RAG, SFT, DPO, continued pre-training। पहले eval set बनाओ और जितना gap हो उतना ही ऊपर चढ़ो।
- **504 Fine Tuning for Tariff System** — Fine-tune a small model on verified (description -> JSON) pairs so format and abstention are reliable and prompts stay short. Split by product family, keep the same prompt at train and serve time, and combine with RAG for current rules.
  `out = Path('tariff_train.jsonl')` · हिंदी: Verified (description -> JSON) pairs पर छोटा model fine-tune करो ताकि format और abstain भरोसेमंद हों और prompt छोटा रहे।
- **505 Fine Tuning Best Practices** — Define a metric, try prompt and RAG first, and fine-tune with small, clean, deduplicated data. Freeze a golden set, change one thing at a time and gate on baseline and regression checks. Roll out with shadow and canary, and keep a rollback.
  `seen: Counter = Counter((norm(r['desc']) for r in rows))` · हिंदी: Metric तय करो, पहले prompt और RAG आज़माओ, फिर छोटे, साफ़, deduplicated data से fine-tune करो।

**Key snippet — 486 Fine Tuning — What + Why**
```python
def rough_tokens(text: str) -> int:
    """Very rough token estimate: about 4 characters per token (illustrative only)."""
    return max(1, len(text) // 4)
few_shot_prompt: str = 'You classify products into HS codes. Reply ONLY as JSON.\nExample: \'iPhone 15\' -> {"hs_code": "8517.13"}\nExample: \'Cotton T-shirt\' -> {"hs_code": "6109.10"}\nExample: \'Laptop 14 inch\' -> {"hs_code": "8471.30"}\nNow classify: Bluetooth headphones'
```

**Key snippet — 494 Fine Tuning Cost Estimation**
```python
def approx_tokens(text: str) -> int:
    """Rough token estimate, about 4 chars per token. Use tiktoken in real work."""
    return max(1, len(text) // 4)
rows: List[str] = ['Classify: Bluetooth headphones -> 8518.30'] * 1000
```

**Key snippet — 500 RLHF Basics**
```python
def pairwise_loss(score_chosen: float, score_rejected: float) -> float:
    """Loss = -log(sigmoid(chosen - rejected)); small when chosen scores higher."""
    diff = score_chosen - score_rejected
    return -math.log(1.0 / (1.0 + math.exp(-diff)))
```

---

## Top 10 interview questions

**1. RAG Evaluation Metrics: Which metrics evaluate retrieval and which evaluate generation?** (390)
Retrieval: context precision, context recall (and context relevancy). Generation: faithfulness, answer relevancy. Answer correctness evaluates the final output against a reference.

**2. Faithfulness Score: Write the faithfulness formula.** (391)
Faithfulness = (number of answer claims supported by context) / (total number of claims in the answer).

**3. LLM as Judge Pattern: What is LLM-as-judge?** (403)
Using an LLM to grade other outputs against a rubric.

**4. Golden Dataset: What makes a dataset "golden"?** (409)
Expert-verified labels, high agreement, locked and versioned.

**5. Evaluation in CI/CD Pipeline: Why run evals in CI?** (415)
To catch quality regressions from prompt, model or retrieval changes before they reach users, automatically and consistently.

**6. AI Observability Metrics: What is TTFT?** (433)
Time To First Token: delay until the first streamed token arrives. It drives perceived speed in chat UIs.

**7. Hallucination Detection: What is a faithfulness score?** (463)
Fraction of answer claims supported by the retrieved context.

**8. Input Guardrails: What are input guardrails?** (470)
Checks on content entering the LLM app: size, format, injection, PII, topic, rate.

**9. Prompt Injection Detection: What is direct vs indirect prompt injection?** (474)
Direct: the user types the malicious instruction. Indirect: it hides inside content the app fetches (documents, web pages, emails, tool results).

**10. Fine Tuning vs RAG: One line difference between RAG and fine tuning?** (487)
RAG changes the input (adds retrieved facts); fine tuning changes the model (weights).

