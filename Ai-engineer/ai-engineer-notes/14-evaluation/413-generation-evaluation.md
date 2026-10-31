---

# 413. Generation Evaluation
# हिंदी में: Generation Evaluation

---

## 🔵 Simple Definition (English)
Generation evaluation measures the quality of the LLM's answer given the retrieved context: is it correct, grounded in the context (faithful), relevant to the question, complete, well-formatted and safe? It isolates the "G" in RAG so you can fix prompts and models independently of retrieval.

## 🔵 सरल परिभाषा (Hindi)
Generation evaluation retrieved context दिए जाने पर LLM के answer की quality नापता है: क्या वह सही है, context पर आधारित (faithful), सवाल से relevant, पूरा, सही format में और safe है? यह RAG के "G" को अलग करता है ताकि retrieval से अलग prompts और models ठीक किए जा सकें।

---

## 🔴 Problem it Solves
Even with perfect retrieval, LLMs can hallucinate, ignore context, answer a different question, or break the output format. One overall score hides which of these happens. Splitting generation quality into dimensions tells you exactly what to fix.

## 🔴 यह क्यों बना? (Hindi)
Retrieval सही होने पर भी LLM hallucinate कर सकता है, context अनदेखा कर सकता है, दूसरे सवाल का जवाब दे सकता है या output format तोड़ सकता है। एक कुल score यह छुपा देता है। Generation quality को dimensions में बाँटने से ठीक-ठीक पता चलता है क्या सुधारना है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Fix the context: use gold chunks (isolates generation from retrieval)
Step 2 → Generate answers with the system prompt/model under test
Step 3 → Deterministic checks first: JSON valid? HS code regex? length? citations present?
Step 4 → Reference-based: exact match / token F1 / semantic similarity vs reference
Step 5 → LLM-judge dimensions: faithfulness, relevancy, completeness, tone, safety
Step 6 → Compare models/prompts on the same rows; analyse by slice
Step 7 → Fix the weakest dimension; re-run
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Context fix करो: gold chunks इस्तेमाल करो (generation को retrieval से अलग करने के लिए)
Step 2 → Test हो रहे system prompt/model से answers बनाओ
Step 3 → पहले deterministic checks: JSON valid? HS code regex? length? citations?
Step 4 → Reference-based: exact match / token F1 / reference से semantic similarity
Step 5 → LLM-judge dimensions: faithfulness, relevancy, completeness, tone, safety
Step 6 → उन्हीं rows पर models/prompts compare करो; slice-wise विश्लेषण
Step 7 → सबसे कमज़ोर dimension सुधारो; दोबारा चलाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: With gold chunks fixed, the generator must output JSON `{hs_code, reasoning, cited_note}`. Checks: JSON valid (100%), HS code matches regex `^\d{4}\.\d{2}`, code equals reference (87%), reasoning faithful to the note (judge, 0.91), cited note actually in context (deterministic, 96%). Switching from gpt-4o-mini to gpt-4o lifts exact match to 92% but costs ~15x more; the team uses mini plus a verifier step instead.

**Amazon-style**: Product answer must not mention features absent from the listing (faithfulness) and must stay under 60 words.

## 🟡 Real Example Hindi mein
**Tariff System**: Gold chunks तय करके generator को JSON `{hs_code, reasoning, cited_note}` देना है। Checks: JSON valid (100%), HS code regex `^\d{4}\.\d{2}`, code reference के बराबर (87%), reasoning note के प्रति faithful (judge, 0.91), cited note सच में context में है (deterministic, 96%)। gpt-4o-mini से gpt-4o पर जाने से exact match 92% होता है पर cost ~15x; team mini + verifier step चुनती है।

**Amazon-style**: Product answer में listing में न मौजूद features का ज़िक्र न हो (faithfulness) और 60 शब्दों से कम हो।

---

## 💻 Code Example — Basic
```python
# Basic: deterministic generation checks (pure Python, offline)
import json  # parse model output
import re  # HS code pattern

HS = re.compile(r"^\d{4}\.\d{2}")  # e.g. 8507.60


def check_output(raw: str, context: str, reference_code: str) -> dict[str, bool]:
    result = {"json_valid": False, "format_ok": False, "matches_ref": False, "note_in_context": False}  # defaults
    try:
        data = json.loads(raw)  # parse
        result["json_valid"] = True  # parsed fine
    except json.JSONDecodeError:  # not JSON
        return result  # stop checks
    code = str(data.get("hs_code", ""))  # predicted code
    result["format_ok"] = bool(HS.match(code))  # regex check
    result["matches_ref"] = code.startswith(reference_code)  # compare with reference
    note = str(data.get("cited_note", ""))  # cited note text
    result["note_in_context"] = bool(note) and note.lower() in context.lower()  # grounded citation
    return result  # all flags


ctx = "Note 3 to Chapter 85: lithium-ion accumulators are classified in 8507.60."
out = '{"hs_code": "8507.60", "reasoning": "battery", "cited_note": "Note 3 to Chapter 85"}'
print(check_output(out, ctx, "8507.60"))  # all True
print(check_output("not json", ctx, "8507.60"))  # all False
```

## 💻 Code Example — Advanced
```python
# Advanced: multi-dimension generation eval — deterministic checks + async LLM-judge faithfulness
# pip install openai pydantic
import asyncio  # async
import json  # parse
import logging  # logs
from statistics import mean  # averages

from openai import AsyncOpenAI, APIError, RateLimitError  # client + errors
from pydantic import BaseModel, Field, ValidationError  # validation

log = logging.getLogger("gen_eval")  # logger
client = AsyncOpenAI()  # OPENAI_API_KEY


class Case(BaseModel):  # one generation test case
    question: str
    gold_context: str  # fixed context isolates generation
    reference_code: str


class Faith(BaseModel):  # judge output
    score: float = Field(ge=0, le=1)  # fraction of claims supported
    unsupported: list[str] = []  # unsupported claims


async def judge_faithfulness(context: str, answer: str, retries: int = 3) -> Faith:
    prompt = ("List the claims in ANSWER and mark which are supported by CONTEXT.\n"
              f"CONTEXT:\n{context}\nANSWER:\n{answer}\n"
              'Reply JSON: {"score": <supported/total 0..1>, "unsupported": ["..."]}')  # judge prompt
    for attempt in range(retries):  # retry loop
        try:
            r = await client.chat.completions.create(
                model="gpt-4o-mini", temperature=0,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}])
            return Faith(**json.loads(r.choices[0].message.content))  # validated
        except RateLimitError:  # 429
            await asyncio.sleep(2 ** attempt)
        except (APIError, json.JSONDecodeError, ValidationError) as exc:  # others
            log.warning("judge failed (%d): %s", attempt, exc)
    return Faith(score=0.0, unsupported=["judge_failed"])  # conservative fallback


async def eval_generation(cases: list[Case], generate) -> dict:
    """`generate(question, context) -> str` is an async function under test."""
    sem = asyncio.Semaphore(6)  # limit concurrency

    async def one(c: Case) -> dict:
        async with sem:
            try:
                out = await generate(c.question, c.gold_context)  # generate
            except Exception as exc:  # generation failure
                log.error("generation failed: %s", exc)
                return {"det": {"json_valid": False}, "faith": 0.0}
            det = check_output(out, c.gold_context, c.reference_code)  # deterministic checks
            f = await judge_faithfulness(c.gold_context, out) if det["json_valid"] else Faith(score=0.0)
            return {"det": det, "faith": f.score}  # per-case result

    rows = await asyncio.gather(*(one(c) for c in cases))  # run all
    keys = ["json_valid", "format_ok", "matches_ref", "note_in_context"]
    summary = {k: round(mean(r["det"].get(k, False) for r in rows), 3) for k in keys}  # rates
    summary["faithfulness"] = round(mean(r["faith"] for r in rows), 3)  # judge mean
    return summary  # report
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # web

app = FastAPI()  # app


async def gen_stub(q: str, ctx: str) -> str:  # stand-in generator
    return '{"hs_code": "8507.60", "reasoning": "battery", "cited_note": "Note 3 to Chapter 85"}'


@app.post("/eval/generation")  # evaluate generation quality
async def eval_gen(cases: list[Case]) -> dict:
    if not cases or len(cases) > 100:  # input guard
        raise HTTPException(400, "send 1-100 cases")
    return await eval_generation(cases, gen_stub)  # run eval
```

---

## 🔗 LangChain / LangGraph Connection
Your LCEL generation chain (`prompt | llm | parser`) is the function under test; use `with_structured_output` to enforce the schema so JSON-validity failures disappear. Ragas Faithfulness and AnswerRelevancy implement the judged dimensions; in LangGraph you can add a "verify" node that re-checks faithfulness and regenerates.

```python
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_openai import ChatOpenAI  # model
from pydantic import BaseModel  # schema

class TariffAnswer(BaseModel):  # output schema
    hs_code: str
    reasoning: str
    cited_note: str

chain = (ChatPromptTemplate.from_messages([("system", "Answer only from the context."),
                                            ("human", "Context: {context}\nQuestion: {question}")])
         | ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(TariffAnswer))  # typed output
# result = chain.invoke({"context": "...", "question": "..."})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Evaluating generation with live retrieval (cannot tell which part failed)
✅ Correct: fix gold context first

```python
# Wrong
answer = rag.invoke(q)            # retrieval noise mixed in
# Right
answer = generate(q, gold_context)  # isolates generation
```

❌ Mistake 2: Using only an LLM judge for things code can check
✅ Correct: JSON/regex/length/citation checks first (free, exact).

❌ Mistake 3: Optimising a single "quality" score
✅ Correct: track faithfulness, correctness, completeness and format separately.

---

## 🧠 Tricky Interview Question
**Q**: "Faithfulness is 0.97 but answers are wrong in production. Explain."

**Answer**: Faithfulness only checks that the answer is supported by the provided context, not that the context is right or the answer is correct. If retrieval supplies the wrong chunk, a faithful answer is still wrong. Pair faithfulness with reference-based correctness (golden set), retrieval metrics, and answer relevancy to see the full picture.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is faithfulness?
A1: The share of claims in the answer that are supported by the retrieved context.

Q2: [Easy] Why test generation with gold context?
A2: It removes retrieval errors, so failures are due to the prompt or model.

Q3: [Medium] Name deterministic checks for generation.
A3: JSON/schema validity, regex formats, length limits, presence of citations, banned phrases, citation-in-context check.

Q4: [Medium] Faithfulness vs correctness?
A4: Faithfulness is relative to the context; correctness is relative to ground truth. An answer can be faithful but wrong, or correct but unfaithful (from model memory).

Q5: [Hard] How do you compare two models fairly?
A5: Same rows, same context, temperature 0, multiple runs for variance, paired statistical tests, a judge from a different family, per-dimension and per-slice results, and cost/latency alongside quality.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Tuning prompts, models, output formats
- Diagnosing hallucination

❌ Avoid when:
- Retrieval is clearly broken (fix that first)

---

## 📊 Visual Diagram
```
 question + GOLD context ─► generator (prompt, model)
                                  │
                  ┌───────────────┼────────────────┐
           deterministic     reference-based     LLM-judge
        (JSON, regex, cite)  (exact/F1/embed)  (faithful, relevant, complete)
                  └───────────────┼────────────────┘
                                  ▼
                  per-dimension scores ─► fix weakest dimension
```

---

## 💰 Cost Impact
Generation eval costs generation tokens (~1.5K in, ~150 out per case) plus judge tokens (~1K per case per judged dimension). 200 cases on gpt-4o-mini ≈ 0.5M tokens ≈ $0.1. Comparing against gpt-4o multiplies generation cost by ~15x.
Optimise: run deterministic checks first and skip the judge for outputs that already failed; cache by (prompt version, case id); compare models on a 50-row subset before a full run.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Faithfulness | Answer supported by context | Answer context से समर्थित |
| Answer relevancy | Answer addresses the question | Answer सवाल से जुड़ा |
| Completeness | Covers all needed points | सभी ज़रूरी बातें शामिल |
| Gold context | Known-correct chunks | सही माने गए chunks |
| Structured output | Schema-enforced reply | Schema-बद्ध जवाब |

---

## ⚡ 3-Line Summary
English: Evaluate generation separately using gold context, deterministic checks, reference comparisons and LLM-judged dimensions. Faithfulness is not correctness, so track both. Fix the weakest dimension first.
Hindi: Generation को gold context, deterministic checks, reference तुलना और LLM-judged dimensions से अलग evaluate करो। Faithfulness का मतलब correctness नहीं, इसलिए दोनों देखो। सबसे कमज़ोर dimension पहले सुधारो।

---

## ➡️ Next Topic
**414. Next in the evaluation series** - continue with the following topic in the 14-evaluation folder.
