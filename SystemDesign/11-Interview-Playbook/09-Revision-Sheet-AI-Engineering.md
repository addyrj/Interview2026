# 09. Revision Sheet — AI Engineering
# हिंदी में: AI Engineering की Revision Sheet — LLM की बुनियाद, OpenAI/Claude APIs, prompting (few-shot, CoT, structured output), embeddings, vector DBs, chunking, RAG, hybrid search, reranking, tools, ReAct, LangChain/LangGraph, multi-agent, memory, evals, observability, caching, guardrails, fine-tuning, बड़े पैमाने का design, hallucinations, ख़र्च, streaming और deployment (Topics 127–155)

---

## 🔵 Simple Definition (English)
A **compact refresher** for `10-AI-Engineering/` (Topics 127–155): what each concept is, the key design rules and the interview traps. AI questions now appear as **standalone rounds** ("Design a RAG support bot", "Design ChatGPT", "Design an AI agent for refunds") and as **features inside classic designs** ("add AI search to Swiggy").

## 🔵 सरल परिभाषा (Hindi)
`10-AI-Engineering/` (127–155) की संक्षिप्त दोहराई — हर concept, मुख्य design नियम और इंटरव्यू के जाल; AI सवाल अब अलग rounds ("RAG support bot डिज़ाइन करो", "ChatGPT", "refund वाला AI agent") और पुराने designs के अंदर features ("Swiggy में AI search जोड़ो") दोनों रूपों में आते हैं।

---

## 🔴 Problem it Solves
AI system design is new for many engineers, and interviewers probe **practical production concerns** more than theory: retrieval quality, hallucinations, prompt injection, cost per conversation, latency (TTFT), evaluation and safe rollouts. A sheet helps you speak precisely ("hybrid BM25 + vector with RRF, then a cross-encoder rerank, faithfulness ≥ 0.9 gated in CI") instead of hand-waving ("we'll use an LLM").

## 🔴 यह क्यों बना? (Hindi)
AI system design कई engineers के लिए नया है, और interviewer theory से ज़्यादा production की बातें पूछते हैं — retrieval की गुणवत्ता, hallucinations, prompt injection, प्रति बातचीत ख़र्च, TTFT, evals, सुरक्षित rollout; sheet से सटीक बोल पाओगे ("BM25 + vector को RRF से, फिर cross-encoder rerank, CI में faithfulness ≥ 0.9") — "LLM लगा देंगे" जैसा नहीं।

---

## 🟢 How it Works — Step by Step (the cheat sheet)

### Foundations & APIs (127–132)

```
127 LLM basics: Transformer next-token prediction; pretraining → SFT → preference tuning (RLHF/DPO);
    tokens (Hindi often 2–4× English), context window, temperature; prefill vs decode (output tokens drive
    latency); stateless API; hallucinations & knowledge cutoff
128 APIs: Claude Messages API (system, messages, max_tokens → content blocks, stop_reason, usage);
    OpenAI Chat/Responses; keys server-side only; timeouts, retries on 429/5xx/529 with backoff;
    model routing (Haiku/Sonnet/Opus tiers); LLM gateway; batch APIs ~50% off
129 Prompting: role + goal + audience + tagged context + constraints with reasons + output format +
    "I don't know" path; separate untrusted data; prompts versioned & evaluated
130 Few/zero-shot: start zero-shot; add 2–10 diverse, balanced examples for format/judgement; dynamic few-shot
    via embeddings; cache static examples
131 Chain of thought: reasoning in <thinking>, parse <answer>; self-consistency votes; reasoning models with
    thinking budgets; use only where multi-step; code/tools for math & rules
132 Structured output: schema-constrained outputs or forced tool calls; Pydantic/zod validation; enums,
    nullable unknowns, paise integers; retry with error feedback; handle truncation
```

### Retrieval & RAG (133–139)

```
133 Embeddings: meaning vectors; cosine similarity; choose by your retrieval eval (incl. Hindi/Hinglish);
    query vs document types; version embeddings (re-embed on model change); weak on IDs/numbers
134 Vector DBs: ANN (HNSW: M, ef_search; IVF: nprobe; quantization); recall@k vs latency; filtered search &
    multi-tenancy (namespaces/partitions, server-enforced tenant filter)
135 pgvector vs Pinecone: pgvector = Postgres-native, transactions, RLS, residency, ≤ tens of millions;
    Pinecone = managed serverless scale, namespaces, hybrid; sync via CDC/outbox
136 Chunking: structure-aware (headings, FAQ pairs, tables with headers, code by function), ~300–800 tokens +
    10–20% overlap, contextual enrichment, parent-child, rich metadata
137 RAG pipeline: ingest (parse→chunk→enrich→embed→index with ACLs) + query (guard → condense → hybrid
    retrieve with filters → rerank → assemble → generate with citations → validate → trace)
138 Hybrid search: BM25 (exact IDs/codes) + vectors (meaning) fused with RRF (1/(60+rank)); query-aware weights
139 Reranking: cross-encoder on top 30–100 → best 3–8; thresholds enable abstention; MMR for diversity;
    measure nDCG/MRR
```

### Tools & agents (140–145)

```
140 Tool use: tools = name + description + JSON schema; loop: tool_use → your code validates/authorizes/
    executes → tool_result; parallel calls; confirmations for writes; idempotency; MCP standard
141 ReAct: thought → action → observation loop; step/time/cost limits; loop detection; workflows for known
    paths, agents for open-ended; plan-and-execute variant
142 LangChain: Runnables + LCEL (prompt | model | parser), loaders/splitters/retrievers/tools; pin versions
143 LangGraph: typed state + nodes + conditional edges (cycles); checkpointers (Postgres) per thread;
    interrupts for human approval; recursion limits; idempotent nodes
144 Multi-agent: orchestrator-workers, handoffs, critic loops; context isolation & parallelism vs many more
    tokens & coordination bugs; start single-agent
145 Memory: short-term (window + summary + task state) vs long-term (semantic facts, episodic events,
    procedural rules); careful writes (consent, confidence), retrieval by relevance × recency × importance,
    user view/delete (DPDP)
```

### Quality, safety & operations (146–155)

```
146 Evals: retrieval (context recall/precision, recall@k, MRR) vs generation (faithfulness, relevancy,
    correctness); golden + production + synthetic datasets incl. unanswerable & Hindi; Ragas/LLM judges
    calibrated with humans; CI gates + online sampling
147 Observability: trace every step (prompt version, retrieved IDs, tool calls, tokens, cost, TTFT);
    feedback; dashboards & alerts; LangSmith/Langfuse/OTel; PII redaction
148 Caching: provider prompt caching (stable prefix first), exact & semantic response caches (scoped, versioned
    keys, thresholds), embedding/retrieval/tool caches; never share personalized answers
149 Guardrails: defense in depth (input PII/abuse/injection/scope → ACL retrieval → tool limits & approvals →
    output moderation/commitments/grounding/safe rendering); assume injection may succeed; OWASP LLM Top 10
150 Fine-tuning: for behaviour/format/narrow tasks/cost (SFT, LoRA/QLoRA, DPO, distillation); RAG for changing
    knowledge; quality data + held-out evals + safety regression
151 AI at scale: tokens → TPM → cost; LLM gateway (routing, fallback, quotas, cache, metering); orchestrator
    with guards, workflows, bounded agents, RAG, tools, memory; degraded modes; shadow → A/B; human handoff
152 Hallucinations: prevent (grounding, abstention thresholds, quote-first, tools for facts, schemas), detect
    (citation & claim verification, numeric/action validators), contain (deterministic decisions, human
    review, sources UX), measure
153 Cost: tokens × price; cut tokens (lean per-route prompts, top-k, summaries, short outputs), calls
    (workflows, caching, early exits), price (routing/cascades, prompt caching, batch, small models);
    budgets & attribution
154 Streaming: SSE deltas through backend (no buffering, long LB timeouts, heartbeats); cancel on disconnect;
    tool status events; guardrails per sentence; RN via expo/fetch/SSE/WS; resumable buffers
155 Deploy: Docker (slim, non-root, health/readiness) → ECR → ECS Fargate/EKS behind ALB (300 s idle);
    RDS+pgvector, Redis, S3, SQS+DLQ workers; Secrets Manager + IAM roles + OIDC CI; eval-gated
    blue/green; Bedrock option; data in ap-south-1/2
```

### Reference architecture to draw (AI support assistant)

```
Clients ─► API gateway (auth, rate limits) ─► Conversation svc ─► Orchestrator
   Orchestrator: input guard → router (small model) → workflow | bounded agent (tools via tool gateway w/ authz)
                 → RAG (hybrid + rerank, ACL filters) → memory → output guard (grounding, commitments, PII)
   ─► LLM gateway (routing, fallback, quotas, caching, metering) ─► providers / self-hosted vLLM
Async: ingestion workers (S3 → chunk → embed → index), batch jobs, eval service; Observability + feedback loop
```

### Numbers to quote

```
TTFT ~0.3–1.5 s; 30–150 tokens/s; English ~4 chars/token, Hindi 2–4× tokens; chunks 300–800 tokens;
rerank top 30–100 → 3–8; RRF k = 60; recall@10 target ≥ 0.95 (ANN vs exact); faithfulness launch bar ~≥ 0.9;
batch APIs ~50% cheaper; prompt caching large input discounts on stable prefixes
```

## 🟢 कैसे काम करता है? (Hindi)
1. बुनियाद: LLM = अगला token अनुमान (pretraining → SFT → RLHF/DPO), tokens (हिंदी में ज़्यादा), stateless API; Claude/OpenAI APIs (keys सर्वर पर, timeout, 429/5xx retry, model tiers, gateway); prompting (भूमिका, tags वाला context, सीमाएँ, format, "पता नहीं"), few-shot, CoT (सिर्फ़ ज़रूरत पर), structured output (schema/forced tool + Pydantic)।
2. Retrieval: embeddings (अपने eval से चुनो, version रखो), vector DBs (HNSW, recall बनाम latency, tenant filter), pgvector बनाम Pinecone, chunking (ढाँचे वाला, 300–800 tokens, enrichment), RAG pipeline (ingest + query), hybrid (BM25 + vector + RRF), reranking (30–100 → 3–8, threshold, MMR)।
3. Tools/agents: tool loop (आपका code जाँचकर चलाए, writes पर पुष्टि, idempotency, MCP), ReAct (सीमाएँ, loop पकड़ना, जहाँ हो सके workflow), LangChain (LCEL), LangGraph (state, checkpoints, interrupts), multi-agent (फ़ायदा बनाम tokens), memory (short/long-term, सहमति, मिटाने का अधिकार)।
4. गुणवत्ता/सुरक्षा: evals (retrieval और generation अलग, CI gates), observability (हर कदम का trace, ख़र्च, feedback), caching (prompt cache, scoped semantic), guardrails (कई परतें, injection मानकर design), fine-tuning (व्यवहार के लिए, ज्ञान के लिए RAG)।
5. Operations: बड़े पैमाने पर tokens → TPM → ख़र्च, LLM gateway, degraded modes, shadow → A/B, इंसान को सौंपना; hallucinations (रोको, पकड़ो, सीमित करो); ख़र्च (tokens, calls, क़ीमत घटाओ); streaming (buffering बंद, cancel); deploy (Docker → ECS, RDS+pgvector, Redis, SQS, Secrets, OIDC, eval-gated blue/green, डेटा भारत में)।

---

## 🟡 Real World Example
- **Klarna's assistant (2024)** handled most support chats early on, and later rebalanced with humans, which shows both scale and limits.
- **Anthropic's Contextual Retrieval (2024)** showed contextual embeddings plus BM25 plus reranking cutting retrieval failures. **Air Canada (2024)** shows why grounding and commitment guardrails matter.
- **Indian context**: Jugalbandi (government schemes over WhatsApp in Indian languages), Zomato AI, Flipkart's Flippi, Sarvam/AI4Bharat Indic models, plus data residency in ap-south-1.

## 🟡 Real Example Hindi में
- Klarna का assistant (2024) शुरू में ज़्यादातर support chats संभालता था, बाद में इंसानों के साथ संतुलन — पैमाना और सीमा दोनों।
- Anthropic के Contextual Retrieval (2024) में contextual embeddings + BM25 + reranking से retrieval failures घटे; Air Canada (2024) बताता है कि grounding और वादों पर guardrails क्यों ज़रूरी।
- भारत: Jugalbandi (WhatsApp पर भारतीय भाषाओं में सरकारी योजनाएँ), Zomato AI, Flipkart Flippi, Sarvam/AI4Bharat के Indic models, और ap-south-1 में डेटा।

---

## 🟠 My Stack Example

### The 12-line RAG answer you should be able to sketch
```python
async def answer(user, question):
    q, verdict = await guard_input(user, question)                 # PII redaction, abuse/injection/scope
    if verdict != "ok": return policy_reply(verdict)
    query = await condense(q, history=user.history)                # small model
    cands = await hybrid_search(query, tenant=user.tenant_id, acl=user.groups, k=40)   # BM25 + vector + RRF
    top = (await rerank(query, cands))[:6]                         # cross-encoder + threshold
    if not top or top[0].score < 0.25: return abstain_with_handoff()
    draft = await llm("answer", grounded_prompt(q, top))           # gateway: routing, cache, fallback, metering
    issues = validate(draft, top, tools_trace=None)                # citations, claims, commitments, PII
    return draft if not issues else safe_fallback(issues)
```

---

## ⚫ Interview Questions + Answers (rapid fire)

**Q1: Design a RAG chatbot in two minutes.**
A1: Ingestion is event-driven: parse documents, chunk by structure with metadata and ACLs, embed and index into vector and BM25 indexes. At query time: an input guard, then query condensation, hybrid retrieval with permission filters, cross-encoder reranking with an abstention threshold, and a grounded prompt with tagged sources and citation instructions, streamed to the user. Output checks cover citations, unsupported claims and PII, and everything is traced. Evals gate changes in CI (retrieval recall, faithfulness, Hindi and Hinglish segments), and online judges plus feedback monitor production. Cost and latency are managed with routing, prompt caching and top-k limits.

**Q2: How do you stop an agent from issuing wrong refunds?**
A2: Keep business rules and permissions in code: the refund tool checks ownership from the session, amount caps, frequency limits and policy, requires explicit user confirmation and routes larger amounts to human approval. Make it idempotent and audit-logged. Report only refunds confirmed by successful tool results, validate outputs for unbacked commitments, and test with red-team prompts, including injection through emails or tickets.

**Q3: RAG vs fine-tuning?**
A3: Use RAG for knowledge that is private, large, changing or must be cited and permission-filtered: update the index rather than the model. Use fine-tuning to change behaviour (format, tone, narrow-task accuracy, multilingual fluency) or to cut cost and latency with a smaller model at high volume. They combine: a fine-tuned small model can be the generator, and fine-tuned embeddings or rerankers can improve retrieval.

**Q4: How do you control LLM cost at scale?**
A4: Estimate tokens per turn and TPM first. Then route tasks to the smallest adequate model (with cascades), use workflows instead of LLM calls for known paths, keep prompts lean and per-route with stable cacheable prefixes, rerank to few chunks, summarize history, cap outputs, cache FAQ responses (scoped), use batch APIs offline, bound agent steps, and attribute cost per feature and tenant with budgets and alerts, verifying quality with evals after each optimization.

**Q5: How do you evaluate an AI feature before launch?**
A5: Build a versioned eval set from expert golden answers, sampled production questions and reviewed synthetic cases, including unanswerable, adversarial and multilingual items. Measure retrieval (recall@k, context recall and precision) and generation (faithfulness, correctness, refusal accuracy, tool-call correctness), plus safety red-team success rate, latency and cost. Gate in CI against baselines, run shadow mode against humans, then A/B with guardrail metrics, and keep online sampling and feedback loops running after launch.

---

## 🔷 Trade-offs
✅ Strong AI answers combine retrieval, tools, guardrails, evals and cost — ❌ don't over-architect agents where a workflow + RAG suffices.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RAG | Retrieval-augmented generation | खोजकर जवाब |
| Hybrid search | BM25 + vector | keyword + vector |
| Reranker | Second-stage relevance model | दूसरे चरण का ranker |
| Tool use | Model calls your functions | model आपके functions बुलाए |
| Agent loop | Reason–act–observe cycle | सोच–काम–नतीजा चक्र |
| Checkpointer | Persisted agent state | agent state save |
| Faithfulness | Grounded in sources | स्रोत पर आधारित |
| Prompt caching | Discounted repeated prefix | दोहराए prefix पर छूट |
| Guardrails | Layered safety controls | सुरक्षा की परतें |
| LLM gateway | Central model access layer | models की केंद्रीय परत |

---

## ⚡ 3-Line Summary
**English:**
1. Foundations: tokens, APIs, prompting, structured output; retrieval: embeddings, vector DBs, chunking, hybrid + rerank RAG with ACLs.
2. Agents: tool loops with code-enforced authz, bounded ReAct/LangGraph with checkpoints & approvals, careful multi-agent and memory.
3. Production: evals in CI + online, tracing, caching, guardrails, hallucination controls, token cost discipline, streaming, and secure in-region deployment.

**Hindi:**
1. बुनियाद: tokens, APIs, prompting, structured output; retrieval: embeddings, vector DBs, chunking, ACL वाला hybrid + rerank RAG।
2. Agents: code में अनुमति वाले tool loops, सीमित ReAct/LangGraph, checkpoints और मंज़ूरी, सोच-समझकर multi-agent और memory।
3. Production: evals, tracing, caching, guardrails, hallucination नियंत्रण, ख़र्च, streaming, भारत में सुरक्षित deployment।

---

## ➡️ Next Topic Suggestion
**10. Top 100 Most-Asked Questions** — Now test yourself: 100 frequently asked system design questions across backend, frontend, mobile and AI, each with a crisp answer and a pointer to the detailed file.
