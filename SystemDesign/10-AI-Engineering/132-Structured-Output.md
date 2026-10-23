# 132. Structured Output
# हिंदी में: Structured Output — LLM से ऐसा जवाब लेना जिसे code सीधे पढ़ सके (JSON, तय schema के साथ): schema-constrained output, tool के ज़रिए पक्का format, Pydantic/zod से जाँच, और ग़लत होने पर दोबारा कोशिश

---

## 🔵 Simple Definition (English)
**Structured output** means getting LLM responses in a **machine-readable format that matches a schema** (usually JSON), so your code can use them directly: database writes, API calls, UI rendering or next pipeline steps.
Approaches, from weakest to strongest guarantees:
1. **Prompt-only**: "Respond with JSON like {...}". Usually works, but can break (extra text, missing fields, invalid JSON).
2. **JSON mode**: the provider guarantees syntactically valid JSON, but not your schema.
3. **Schema-constrained decoding**: you provide a **JSON Schema**, and the provider constrains generation so output **conforms to it**. Examples: OpenAI Structured Outputs (`strict: true`) and Anthropic's structured outputs.
4. **Tool/function calling as a schema**: define a tool whose `input_schema` is your output schema and **force** the model to call it (Anthropic `tool_choice`). The tool input is your structured data.
Always pair these with **validation in code** (Pydantic in Python, zod in TypeScript), **business-rule checks**, and **retry with error feedback** on failure.

## 🔵 सरल परिभाषा (Hindi)
Structured output = LLM का जवाब ऐसे format (आम तौर पर JSON, तय schema के साथ) में लेना जिसे code सीधे इस्तेमाल करे — DB में लिखना, API call, UI दिखाना।
तरीके (कमज़ोर से मज़बूत): सिर्फ़ prompt में "JSON दो" (अक्सर चलता, कभी टूटता); JSON mode (सही JSON, पर आपका schema नहीं); schema-constrained (JSON Schema दो, provider उसी के हिसाब से लिखवाए); tool calling को schema की तरह — tool का input_schema = आपका schema और model को वही tool call करने पर मजबूर करो। हमेशा code में जाँच (Pydantic/zod), business नियम, और ग़लती पर error बताकर दोबारा कोशिश।

---

## 🔴 Problem it Solves
LLMs naturally produce prose, but applications need data:
- **Extract** fields from messy inputs: a complaint ("order 4521 late by 40 min, biryani cold") → `{order_id, issue_type, delay_min}`. GST invoices and KYC documents → amounts, GSTIN, dates. Resumes → skills.
- **Classify** into fixed enums for routing.
- **Generate** UI cards, product attributes or agent action plans.
Without structure, code breaks on "Sure! Here's the JSON: ```json …```", missing fields, wrong types ("₹249" as a string vs 24900 paise), hallucinated enum values or truncated output. Structured output plus validation makes LLM features **dependable components** in pipelines instead of fragile string parsing.

## 🔴 यह क्यों बना? (Hindi)
LLM स्वाभाविक रूप से गद्य लिखता है, पर ऐप को डेटा चाहिए: गड़बड़ शिकायत ("order 4521 40 मिनट लेट, biryani ठंडी") से `{order_id, issue_type, delay_min}`; GST invoice/KYC से राशि, GSTIN, तारीख़; तय श्रेणियों में बाँटना; UI cards या agent की योजना बनाना।
बिना structure के code टूटता है — "Sure! Here's the JSON…" जैसा अतिरिक्त text, fields ग़ायब, ग़लत type ("₹249" string बनाम 24900 paise), गढ़ी हुई श्रेणी, अधूरा output। Structured output + जाँच = LLM features भरोसेमंद हिस्से बनते हैं।

---

## 🟢 How it Works — Step by Step

### Design the schema first

```
{
  "type": "object",
  "properties": {
    "order_id":   {"type": ["string", "null"], "description": "Order number if mentioned, else null"},
    "issue_type": {"type": "string", "enum": ["DELIVERY_DELAY", "FOOD_QUALITY", "MISSING_ITEM",
                                              "PAYMENT_DEBITED_NO_ORDER", "REFUND_STATUS", "OTHER"]},
    "delay_minutes": {"type": ["integer", "null"], "minimum": 0},
    "items_affected": {"type": "array", "items": {"type": "string"}},
    "sentiment": {"type": "string", "enum": ["calm", "upset", "angry"]},
    "language": {"type": "string", "enum": ["en", "hi", "hinglish", "other"]}
  },
  "required": ["order_id", "issue_type", "delay_minutes", "items_affected", "sentiment", "language"],
  "additionalProperties": false
}
Principles:
- Enums for categories (no free text), integers for money in paise, ISO dates as strings
- NULLABLE fields for unknowns → gives the model a way to say "not present" instead of inventing
- descriptions on fields = instructions to the model
- keep schemas small & flat where possible; split huge extractions into multiple calls
- version the schema; downstream code validates against the same definition
```

### Getting conformant output

```
OpenAI: response_format = { type: "json_schema", json_schema: { name, schema, strict: true } }
        (or SDK helpers that take Pydantic/zod models) → output conforms to schema (subset of JSON Schema)
Anthropic:
  a) Structured outputs (schema-constrained JSON) where supported by the model/API
  b) Tool-forcing: tools=[{name:"record_complaint", input_schema: SCHEMA}],
     tool_choice={"type":"tool","name":"record_complaint"} → read tool_use.input
Fallback (any model): prompt with schema + examples + prefill "{" + strict parser + retries
```

### Validate → repair → retry loop

```
LLM output ──► parse JSON ──► validate schema (Pydantic/zod) ──► business checks
                    │ fail             │ fail                        │ fail (e.g., delay_minutes > 600,
                    ▼                  ▼                             ▼  order_id not owned by user)
              retry with the error message: "Your previous output failed validation: <errors>.
              Return corrected JSON only." (max 1–2 retries) → else fallback (human review / default)
Also handle stop_reason == "max_tokens" (truncated JSON) → raise max_tokens or reduce output size
```

### Structured output vs tool calling

```
Structured output → "give me data in this shape" (extraction, classification, generation)
Tool calling      → "decide whether/which action to take and with what arguments" (Topic 140)
Same mechanism (JSON schema), different intent; forcing a single tool = structured output
```

### Streaming structured output

```
Partial JSON streams token by token → use incremental parsers (partial-json, SDK helpers) to render
progressively (e.g., show title then bullet points) → validate fully at the end
```

## 🟢 कैसे काम करता है? (Hindi)
1. पहले schema बनाओ: श्रेणियों के लिए enum (खुला text नहीं), पैसे paise में integer, तारीख़ ISO string, अनजानी चीज़ के लिए nullable (ताकि model गढ़े नहीं), हर field का description (model के लिए निर्देश), schema छोटा और सपाट, version रखो।
2. Output पक्का करो: OpenAI में `response_format` json_schema + `strict: true`; Anthropic में structured outputs या tool-forcing (tool का input_schema = आपका schema, tool_choice से मजबूर, `tool_use.input` पढ़ो); पुराने models पर schema + उदाहरण + strict parser + retries।
3. जाँच-सुधार-दोबारा: JSON parse → Pydantic/zod से schema जाँच → business नियम (देरी 600 मिनट से ज़्यादा नहीं, order इसी यूज़र का हो) → fail हो तो error बताकर 1–2 बार दोबारा → फिर भी नहीं तो human review/default।
4. stop_reason `max_tokens` का मतलब JSON अधूरा — max_tokens बढ़ाओ या output छोटा करो।
5. Structured output = "इस shape में डेटा दो"; tool calling = "कौन-सा काम करना है और किन arguments से" — तरीका एक, इरादा अलग; streaming में partial JSON parser से धीरे-धीरे दिखाओ, अंत में पूरी जाँच।

---

## 🟡 Real World Example

**OpenAI Structured Outputs (Aug 2024)** — introduced schema-constrained generation with `strict: true`. OpenAI reported near-perfect schema adherence on its evals with structured outputs, versus significantly lower adherence with prompting alone. That became standard for extraction pipelines.

**Anthropic tool use for JSON** — Anthropic documents forcing a tool call (`tool_choice`) as a reliable way to get schema-shaped JSON, and later added structured-output support, which is widely used for document extraction (invoices, contracts, KYC).

**Document AI in Indian fintech and logistics (illustrative)** — extracting GSTIN, invoice numbers, amounts, HSN codes and dates from GST invoices, or fields from e-way bills, uses LLM structured extraction plus deterministic validation (GSTIN checksum, totals match) before posting to ERPs.

**Instructor library and Vercel AI SDK `generateObject`** — popular developer tools that wrap Pydantic or zod schemas with validation and automatic retries, showing that validation plus retry is the norm, not an afterthought.

## 🟡 Real Example Hindi में
OpenAI ने अगस्त 2024 में Structured Outputs (`strict: true`) लाया — schema का पालन लगभग पूरा, सिर्फ़ prompt से काफ़ी कम; Anthropic tool-forcing (`tool_choice`) से पक्का JSON लेने का तरीका बताता है और बाद में structured outputs भी जोड़े — invoices, contracts, KYC निकालने में आम।
भारतीय fintech/logistics में GST invoice से GSTIN, invoice नंबर, राशि, HSN, तारीख़ निकालना + पक्की जाँच (GSTIN checksum, totals मिलें) के बाद ही ERP में; Instructor और Vercel AI SDK का `generateObject` validation + retry देते हैं।

---

## 🟠 My Stack Example

### Python: Pydantic schema + Claude tool-forcing + validation + retry
```python
from pydantic import BaseModel, Field, ValidationError
from typing import Literal, Optional

class Complaint(BaseModel):
    order_id: Optional[str] = Field(None, description="Order number if mentioned, else null")
    issue_type: Literal["DELIVERY_DELAY", "FOOD_QUALITY", "MISSING_ITEM", "PAYMENT_DEBITED_NO_ORDER", "REFUND_STATUS", "OTHER"]
    delay_minutes: Optional[int] = Field(None, ge=0, le=600)
    items_affected: list[str] = Field(default_factory=list)
    sentiment: Literal["calm", "upset", "angry"]
    language: Literal["en", "hi", "hinglish", "other"]

TOOL = {"name": "record_complaint", "description": "Record structured fields extracted from a customer complaint.",
        "input_schema": Complaint.model_json_schema()}

def extract_complaint(text: str, retries: int = 1) -> Complaint | None:
    messages = [{"role": "user", "content": f"Extract the complaint fields.\n<message>{text}</message>"}]
    for attempt in range(retries + 1):
        r = client.messages.create(model="claude-haiku-5-5", max_tokens=400, temperature=0,
                                   tools=[TOOL], tool_choice={"type": "tool", "name": "record_complaint"},
                                   messages=messages)
        block = next(b for b in r.content if b.type == "tool_use")
        try:
            return Complaint.model_validate(block.input)                       # schema + type validation
        except ValidationError as e:
            messages += [{"role": "assistant", "content": r.content},
                         {"role": "user", "content": [{"type": "tool_result", "tool_use_id": block.id, "is_error": True,
                                                       "content": f"Validation failed: {e.errors()}. Call the tool again with corrected fields."}]}]
    return None                                                                 # → human review queue

c = extract_complaint("Order #4521 40 min late tha aur biryani thandi thi 😡")
# Complaint(order_id='4521', issue_type='DELIVERY_DELAY', delay_minutes=40, items_affected=['biryani'], sentiment='angry', language='hinglish')
```

### OpenAI: strict JSON schema with Pydantic helper
```python
from openai import OpenAI
oai = OpenAI()
completion = oai.chat.completions.parse(                 # SDK helper; older SDKs: oai.beta.chat.completions.parse
    model=os.environ["OPENAI_MODEL"],
    messages=[{"role": "system", "content": "Extract complaint fields."}, {"role": "user", "content": text}],
    response_format=Complaint,                            # converted to strict json_schema
)
complaint = completion.choices[0].message.parsed          # already a Complaint instance (or refusal)
```

### Node: zod + Vercel AI SDK generateObject (with Anthropic provider)
```ts
import { generateObject } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';
import { z } from 'zod';

const Invoice = z.object({
  gstin: z.string().regex(/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$/).nullable(),
  invoiceNumber: z.string(),
  invoiceDate: z.string().describe('ISO date YYYY-MM-DD'),
  lines: z.array(z.object({ description: z.string(), hsn: z.string().nullable(), amountPaise: z.number().int().nonnegative() })),
  totalPaise: z.number().int().nonnegative(),
});

const { object } = await generateObject({
  model: anthropic('claude-sonnet-5-5'), schema: Invoice,
  prompt: `Extract invoice fields from this OCR text:\n<invoice>${ocrText}</invoice>`,
});
// Business validation beyond schema
const sum = object.lines.reduce((s, l) => s + l.amountPaise, 0);
if (Math.abs(sum - object.totalPaise) > 100) await reviewQueue.add({ reason: 'TOTAL_MISMATCH', object });
```

### Handling truncation & refusals
```python
if r.stop_reason == "max_tokens":
    raise OutputTruncated("increase max_tokens or reduce requested fields")
# Some APIs return a refusal field for disallowed requests (e.g., OpenAI message.refusal) → handle explicitly
```

### Store the schema version with results
```sql
INSERT INTO complaint_extractions (ticket_id, schema_version, model, data, valid)
VALUES ($1, 'complaint_v3', 'claude-haiku-5-5', $2::jsonb, true);
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you reliably get JSON from an LLM?**
A1: Use the strongest mechanism the provider offers: schema-constrained structured outputs (a JSON Schema with strict mode) or forcing a tool call whose input schema is the desired output. Design a compact schema with enums, typed fields, nullable unknowns and field descriptions. Always parse and validate in code (Pydantic or zod) plus business checks. On failure, retry once or twice with the validation errors fed back, and handle truncation (`max_tokens`) and refusals. Route persistent failures to fallbacks or human review.

**Q2: Why make fields nullable in extraction schemas?**
A2: If every field is required and non-nullable, the model is pressured to produce a value even when the information isn't in the input, which encourages hallucinated order IDs, dates or amounts. Nullable fields (with instructions to use null when absent) give the model a legitimate way to express "not present", improving precision. Downstream code can then decide what to do with missing data (ask the user, flag for review).

**Q3: What's the difference between JSON mode and structured outputs with a schema?**
A3: JSON mode guarantees syntactically valid JSON but not that it matches your fields, types or enums. The model may omit required keys or invent extra ones. Schema-constrained structured output uses the provided JSON Schema during decoding so the output conforms to the schema (within the supported subset), dramatically reducing parsing and validation failures. Even with schemas, you still validate semantics and business rules in code.

**Q4: How would you build an invoice extraction pipeline?**
A4: Upload the document, run OCR or a vision-capable model, then do LLM structured extraction into a versioned schema (GSTIN, invoice number, date, line items with HSN and amounts in paise, taxes, total). Validate deterministically: schema, GSTIN format and checksum, date sanity, line totals summing to the invoice total, tax rates consistent. Use confidence and validation results to auto-approve or send to human review, store raw text, extraction and schema version for audit, and monitor field-level accuracy on a labelled eval set.

**Q5: When should you split a structured extraction into multiple calls?**
A5: When the schema is very large or deeply nested (models make more errors and outputs risk truncation), when parts need different context (per-page extraction of long documents), when some fields require reasoning while others are simple, or when you want parallelism and partial retries. Splitting into focused extractions (header fields, line items per page, classification) and merging in code often improves accuracy and debuggability, at the cost of more calls.

---

## 🔷 Trade-offs
✅ Schema-constrained output: near-guaranteed shape — ❌ schema feature subsets, small latency overhead.
✅ Tool-forcing: works broadly — ❌ slightly more verbose integration.
✅ Strict validation + retries: correctness — ❌ extra calls on failures.
✅ Large single schema: one call — ❌ more errors/truncation; split when big.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Structured output | Schema-conforming machine-readable output | तय ढाँचे वाला जवाब |
| JSON Schema | Standard for describing JSON shape | JSON का ढाँचा बताने का मानक |
| JSON mode | Valid JSON, no schema guarantee | सही JSON, schema पक्का नहीं |
| Constrained decoding | Generation restricted to schema | schema के अंदर लिखवाना |
| Tool forcing | Require a specific tool call | ख़ास tool call पर मजबूर |
| Pydantic / zod | Validation libraries | जाँच libraries |
| Nullable field | Allows null for unknown | अनजान के लिए null |
| Enum | Fixed allowed values | तय विकल्प |
| Repair retry | Retry with error feedback | ग़लती बताकर दोबारा |
| Truncation | Output cut by max_tokens | अधूरा output |

---

## ⚡ 3-Line Summary
**English:**
1. Design small, versioned schemas with enums, typed fields (paise integers, ISO dates), nullable unknowns and field descriptions.
2. Use schema-constrained outputs or forced tool calls; validate with Pydantic/zod + business rules; retry with error feedback; handle truncation/refusals.
3. Split big extractions, stream partial JSON for UX, store schema version + model with results, and route failures to human review.

**Hindi:**
1. छोटे versioned schemas: enums, सही types (paise integer, ISO तारीख़), अनजान के लिए null, descriptions।
2. Schema-constrained output या forced tool; Pydantic/zod + business नियमों से जाँच; ग़लती पर दोबारा; अधूरे output का ध्यान।
3. बड़ी extraction बाँटो, partial JSON stream करो, schema version save करो, fail पर human review।

---

## ➡️ Next Topic Suggestion
**133. Embeddings** — From generating text to representing meaning as numbers. Next: what embeddings are, how semantic similarity works, choosing embedding models, and using them for search, clustering, dedupe and RAG.
