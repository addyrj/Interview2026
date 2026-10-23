# 131. Chain of Thought
# हिंदी में: Chain of Thought (CoT) — model से जवाब देने से पहले कदम-दर-कदम सोचवाना, ताकि कई चरणों वाले सवाल (नियम, गणना, योजना) में ग़लती कम हो; सोच और अंतिम जवाब को अलग रखना, और self-consistency व reasoning models

---

## 🔵 Simple Definition (English)
**Chain-of-thought (CoT) prompting** asks the model to **reason through intermediate steps before giving the final answer**. Examples: "Think step by step", or a structured format like `<thinking>…</thinking><answer>…</answer>`. Because LLMs generate token by token, writing out intermediate steps gives them "working memory" on the page, which improves accuracy on **multi-step problems**: applying several policy rules, arithmetic word problems, logical deductions, planning and complex classification.
Variants:
- **Zero-shot CoT**: "Let's think step by step."
- **Few-shot CoT**: examples that show reasoning steps.
- **Structured CoT**: guided steps ("1. Identify order status 2. Check policy 3. Decide").
- **Self-consistency**: sample several reasoning paths and **majority-vote** the answer.
- **Reasoning models / extended thinking**: models trained to think internally before answering, with a configurable **thinking budget**.
- **Plan-and-execute, tree-of-thought**: explore or plan before acting.
Trade-off: better accuracy on hard tasks in exchange for **more tokens, latency and cost**. Use it selectively.

## 🔵 सरल परिभाषा (Hindi)
Chain-of-thought = model से कहना कि अंतिम जवाब से पहले बीच के कदम सोचकर लिखे ("कदम-दर-कदम सोचो" या `<thinking>…</thinking><answer>…</answer>`); क्योंकि model token-दर-token लिखता है, बीच के कदम लिखना उसे "काग़ज़ पर काम करने की जगह" देता है — कई नियम लगाना, गणना वाले सवाल, तर्क, योजना जैसे कामों में सटीकता बढ़ती है।
प्रकार: zero-shot CoT, उदाहरणों के साथ CoT, तय steps वाला CoT, self-consistency (कई बार सोचकर बहुमत वाला जवाब), reasoning models/extended thinking (thinking budget के साथ)। क़ीमत: ज़्यादा tokens, देर और ख़र्च — सोच-समझकर इस्तेमाल करो।

---

## 🔴 Problem it Solves
Asked to answer immediately, models often **jump to a plausible but wrong conclusion** on tasks needing several steps:
- "Is this order eligible for a refund?" requires checking order status, delivery time versus promise, item type (non-refundable?), the customer's past refund count and the payment method. A one-shot answer may skip a rule.
- "If delivery fee is ₹30, packaging ₹15, 18% GST on platform fee ₹5 and a ₹50 coupon applies on orders above ₹199, what's the total?" Models make arithmetic slips without steps (better still, use a calculator tool).
- Planning an agent's actions or debugging code needs intermediate reasoning.
CoT makes reasoning **explicit, more accurate and inspectable** (useful for debugging and evals), while structured tags let your code **extract only the final answer** for users.

## 🔴 यह क्यों बना? (Hindi)
तुरंत जवाब देने को कहो तो model कई कदम वाले सवालों में अक्सर जल्दी से ग़लत नतीजे पर कूद जाता है: "क्या यह order refund के लायक़ है?" — status, वादे से देरी, item refundable है या नहीं, पिछले refunds, भुगतान तरीका — एक बार में जवाब में कोई नियम छूट जाता है; fee + packaging + GST + coupon वाली गणना में ग़लती (बेहतर: calculator tool); agent की योजना या code debugging में बीच की सोच चाहिए।
CoT सोच को साफ़, ज़्यादा सटीक और जाँचने लायक बनाता है, और tags से code सिर्फ़ अंतिम जवाब यूज़र को दिखाता है।

---

## 🟢 How it Works — Step by Step

### Patterns

```
1) Zero-shot CoT
   "...Think through this step by step before answering."
2) Guided / structured CoT (more reliable in production)
   "Before answering, in <thinking> tags:
     1. Extract order status, promised vs actual delivery time, item categories.
     2. Check each refund rule in <policy> one by one.
     3. Decide eligibility and amount.
    Then give only the final decision in <answer> as JSON."
3) Few-shot CoT
   examples include reasoning steps → model imitates reasoning style
4) Self-consistency
   sample N reasoning paths (temperature ~0.7) → extract answers → majority vote (or pick by verifier)
5) Reasoning models / extended thinking
   model-native thinking with a token budget (e.g., Claude extended thinking) → no need to prompt
   "think step by step"; you get thinking blocks + final answer; budget trades cost/latency for quality
```

### Separate reasoning from the answer

```
Prompt: "...Write your reasoning in <thinking></thinking>, then the final answer in <answer></answer>."
Code:   parse <answer> → show to user / feed next step; log <thinking> for debugging (not shown, may
        contain internal policy details); never execute decisions based only on reasoning text
Note: shown reasoning isn't guaranteed to be the model's true internal process ("faithfulness" caveat)
→ verify final outputs with code/rules/evals, don't trust the narrative alone
```

### When CoT helps vs hurts

```
HELPS: multi-rule policy decisions, math/word problems, multi-hop questions over provided documents,
       planning, code reasoning/debugging, complex classification with exceptions, comparisons
NOT NEEDED: simple lookups, extraction of explicit fields, short classifications with clear labels,
       rewriting/translation → adds latency & tokens with little gain
BETTER ALTERNATIVES: exact arithmetic → calculator/code tool; deterministic business rules → code
       (let the LLM extract facts, code decides); factual knowledge → retrieval
```

### Cost/latency control

```
- Use CoT only on routes that need it (router: simple vs complex)
- Cap reasoning length ("keep reasoning under 150 words") or set a thinking budget
- Use a cheaper model for first pass, escalate hard cases to a reasoning model
- Stream the final answer; do reasoning in background for async tasks
- Self-consistency multiplies cost by N → reserve for high-value decisions or offline batch
```

## 🟢 कैसे काम करता है? (Hindi)
1. तरीके: "कदम-दर-कदम सोचो" (zero-shot CoT); तय steps वाला CoT (1. तथ्य निकालो 2. हर नियम जाँचो 3. फ़ैसला) — production में ज़्यादा भरोसेमंद; उदाहरणों में सोच दिखाना; self-consistency (कई बार सोचो, बहुमत लो); reasoning models में thinking budget दो।
2. सोच `<thinking>` में और जवाब `<answer>` में — code सिर्फ़ answer यूज़र को दिखाए, thinking debugging के लिए log करे; दिखाई गई सोच हमेशा असली अंदरूनी प्रक्रिया नहीं होती — अंतिम output को code/नियम/evals से जाँचो।
3. कब मदद: कई नियम वाले फ़ैसले, गणना, documents पर कई कदम वाले सवाल, योजना, code debugging; कब नहीं: सीधा lookup, field निकालना, साफ़ classification, अनुवाद।
4. बेहतर विकल्प: सही गणना के लिए calculator/code tool; पक्के business नियम code में (LLM तथ्य निकाले, code फ़ैसला करे); तथ्यों के लिए retrieval।
5. ख़र्च पर नियंत्रण: सिर्फ़ ज़रूरी routes पर CoT, सोच की लंबाई सीमित, पहले सस्ता model फिर कठिन cases reasoning model को, self-consistency सिर्फ़ बड़े फ़ैसलों या offline batch में।

---

## 🟡 Real World Example

**Chain-of-Thought paper (Google, 2022)** — "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" showed large gains on arithmetic and commonsense benchmarks when prompts included reasoning steps. A follow-up showed that simply adding "Let's think step by step" (zero-shot CoT) also helps.

**Self-consistency (2022)** — sampling multiple reasoning paths and taking the majority answer further improved accuracy on math and reasoning tasks, a standard technique for high-stakes offline decisions.

**Reasoning models (2024 onward)** — OpenAI's o-series, Claude's extended thinking and Google's Gemini thinking models internalize step-by-step reasoning with configurable effort or budgets, performing strongly on math, coding and agentic tasks, at higher latency and cost.

**Fintech/insurance decision support (illustrative)** — claim or refund triage often uses "LLM extracts facts → rules engine decides → LLM explains", with CoT reserved for ambiguous cases and every decision auditable. Regulators expect explainability, which structured reasoning plus deterministic rules provide.

## 🟡 Real Example Hindi में
Google के 2022 के paper "Chain-of-Thought Prompting…" ने दिखाया कि prompt में सोच के कदम देने से गणित और तर्क वाले सवालों में बड़ा सुधार होता है; बाद में "Let's think step by step" जोड़ना भी मददगार निकला; self-consistency (कई बार सोचकर बहुमत) से और सुधार।
2024 से reasoning models (OpenAI o-series, Claude extended thinking, Gemini thinking) अंदर ही कदम-दर-कदम सोचते हैं — गणित, code, agents में बेहतर, पर धीमे और महँगे; fintech/insurance में "LLM तथ्य निकाले → नियम फ़ैसला करें → LLM समझाए" — CoT सिर्फ़ अस्पष्ट cases में।

---

## 🟠 My Stack Example

### Structured CoT with parsed answer (refund eligibility explanation)
```python
SYSTEM = """You decide refund eligibility for QuickBite orders using ONLY the policy provided.
Before answering, reason in <thinking> tags:
1. List the relevant facts from <order>.
2. Check each rule in <policy> one by one and say whether it applies.
3. Decide eligibility and refund percentage.
Keep the reasoning under 150 words. Then output ONLY JSON in <answer> tags:
{"eligible": true|false, "refund_percent": 0-100, "rule_ids": ["R2", ...], "customer_message": "..."}"""

def decide(order: dict, policy: str):
    r = client.messages.create(model="claude-sonnet-5-5", max_tokens=600, temperature=0, system=SYSTEM,
        messages=[{"role": "user", "content": f"<policy>{policy}</policy>\n<order>{json.dumps(order)}</order>"}])
    text = r.content[0].text
    thinking = re.search(r"<thinking>(.*?)</thinking>", text, re.S)
    answer = json.loads(re.search(r"<answer>(.*?)</answer>", text, re.S).group(1))
    audit_log.write(order_id=order["id"], reasoning=thinking and thinking.group(1), decision=answer)   # explainability
    return validate_against_rules(answer, order)        # deterministic check: never exceed policy caps in code
```

### Self-consistency vote (offline / high-stakes)
```python
from collections import Counter
def self_consistent_label(text: str, n: int = 5) -> str:
    answers = []
    for _ in range(n):
        r = client.messages.create(model="claude-haiku-5-5", max_tokens=300, temperature=0.7,
            system="Think step by step in <thinking>, then give the final label in <answer>.",
            messages=[{"role": "user", "content": f"Is this message a fraud attempt? Labels: FRAUD, SAFE.\n<msg>{text}</msg>"}])
        m = re.search(r"<answer>\s*(\w+)\s*</answer>", r.content[0].text)
        if m: answers.append(m.group(1))
    label, votes = Counter(answers).most_common(1)[0]
    return label if votes >= (n // 2 + 1) else "NEEDS_REVIEW"          # low agreement → human review
```

### Extended thinking with a reasoning budget (Claude) for hard analysis
```python
# Parameter names per Anthropic docs for models supporting extended thinking; check current docs for your model.
r = client.messages.create(
    model="claude-opus-5-5", max_tokens=8000,
    thinking={"type": "enabled", "budget_tokens": 4000},          # trade cost/latency for deeper reasoning
    messages=[{"role": "user", "content": "Given these 30 days of delivery-delay metrics by zone (CSV below), "
                                          "identify the top 3 root causes and propose fixes.\n" + csv_text}])
final_text = "".join(b.text for b in r.content if b.type == "text")       # thinking blocks are separate
```

### Better than CoT for math: let code compute (tool or post-processing)
```python
# LLM extracts structured numbers; Python computes exactly
items = extract_bill_items(bill_text)        # [{"name": "...", "amount_paise": 24900}, ...] via structured output (Topic 132)
total = sum(i["amount_paise"] for i in items) + fees_paise - coupon_paise
gst = round(platform_fee_paise * 0.18)
```

### Router: only use CoT where needed
```js
const complexity = await classify('classify-fast', question);            // SIMPLE | COMPLEX
const res = complexity === 'COMPLEX'
  ? await llm.complete('deep-reasoning', { system: COT_SYSTEM, messages, maxTokens: 1500 })
  : await llm.complete('support-default', { system: DIRECT_SYSTEM, messages, maxTokens: 300 });
```

---

## ⚫ Interview Questions + Answers

**Q1: What is chain-of-thought prompting and why does it work?**
A1: It prompts the model to generate intermediate reasoning steps before the final answer. Because LLMs produce output token by token, writing out steps lets the model condition later tokens on explicit intermediate results, effectively giving it working memory. That improves accuracy on multi-step tasks like math word problems, multi-rule decisions, multi-hop questions and planning, at the cost of more output tokens and latency.

**Q2: How do you use CoT in production without exposing reasoning to users?**
A2: Ask the model to put reasoning in delimited tags (`<thinking>`) and the final result in separate tags or a structured JSON block (`<answer>`). Parse only the answer for the UI or downstream code, and log the reasoning securely for debugging and audits. With reasoning models, thinking content comes in separate blocks from the final text. Keep decisions grounded in validated outputs and deterministic checks, since stated reasoning isn't guaranteed to reflect the model's internal process.

**Q3: What is self-consistency?**
A3: Instead of one reasoning path, you sample multiple chain-of-thought completions at non-zero temperature, extract the final answer from each, and take the majority (or use a verifier to pick the best). Agreement across diverse reasoning paths correlates with correctness, so it improves accuracy and gives a confidence signal: low agreement can route to human review. It multiplies cost and latency by the number of samples, so use it for high-value or offline decisions.

**Q4: When should you avoid chain of thought?**
A4: Avoid it for simple tasks where it adds tokens and latency without accuracy gains: direct field extraction, clear-cut classifications, rewriting, translation, retrieval-backed lookups. Prefer tools or code for exact arithmetic and deterministic business rules, and retrieval for factual knowledge. For latency-sensitive user-facing flows, use a router that applies CoT or reasoning models only to complex queries, and cap reasoning length or thinking budgets.

**Q5: How do reasoning models change prompt design?**
A5: Reasoning models think internally before answering, often with configurable effort or budgets, so you usually don't need explicit "think step by step" prompting or few-shot reasoning traces. High-level guidance about the goal, constraints and success criteria tends to work better than prescriptive step lists. They cost more and respond slower, so you route only appropriate tasks to them, set budgets, stream final answers where possible, and still validate outputs and use tools for exact facts and computation.

---

## 🔷 Trade-offs
✅ CoT: higher accuracy on multi-step tasks, inspectable reasoning — ❌ more tokens, latency, cost.
✅ Self-consistency: accuracy + confidence signal — ❌ N× cost.
✅ Reasoning models: strongest on hard tasks — ❌ slowest/most expensive; overkill for simple queries.
✅ Code/tools for math & rules: exact & auditable — ❌ requires structured extraction first.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Chain of thought | Step-by-step reasoning before answer | कदम-दर-कदम सोच |
| Zero-shot CoT | "Think step by step" trigger | सोचने का संकेत |
| Structured CoT | Guided reasoning steps | तय कदमों वाली सोच |
| Self-consistency | Majority vote over reasoning paths | कई सोच का बहुमत |
| Reasoning model | Model trained to think internally | अंदर सोचने वाला model |
| Thinking budget | Token limit for reasoning | सोच के tokens की सीमा |
| Faithfulness | Whether stated reasoning is real | सोच कितनी सच्ची |
| Verifier | Checks candidate answers | जवाब जाँचने वाला |
| Router | Sends tasks to right approach | सही रास्ते पर भेजना |
| Plan-and-execute | Plan first, then act | पहले योजना, फिर काम |

---

## ⚡ 3-Line Summary
**English:**
1. CoT makes the model reason in steps before answering, improving multi-step accuracy; use structured tags to separate reasoning from the parsed answer.
2. Self-consistency votes across sampled reasoning paths; reasoning models/extended thinking internalize CoT with budgets.
3. Apply selectively (router), cap reasoning, prefer code/tools for math and rules, and validate final outputs — stated reasoning isn't proof.

**Hindi:**
1. CoT से model पहले कदम-दर-कदम सोचता है — कई कदम वाले सवालों में सटीकता; tags से सोच और जवाब अलग।
2. Self-consistency = कई सोच का बहुमत; reasoning models में thinking budget।
3. ज़रूरत पर ही CoT, सोच की सीमा, गणना/नियम के लिए code/tools, और अंतिम output की जाँच।

---

## ➡️ Next Topic Suggestion
**132. Structured Output** — Reasoning is great, but your code needs machine-readable results. Next: getting reliable JSON from LLMs with schemas, tool-forced outputs, validation (Pydantic/zod), retries and streaming partial objects.
