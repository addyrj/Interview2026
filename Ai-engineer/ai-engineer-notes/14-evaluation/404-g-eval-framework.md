---

# 404. G-Eval Framework
# हिंदी में: G-Eval Framework

---

## 🔵 Simple Definition (English)
G-Eval is an LLM-as-judge method from a 2023 paper. You give only the **criteria** (e.g. "coherence"). The LLM first writes its own evaluation steps (chain-of-thought), then fills a form with a score. The final score is the **probability-weighted average** of the score tokens, which gives smoother, more fine-grained numbers than a single integer.

## 🔵 सरल परिभाषा (Hindi)
G-Eval 2023 के एक paper से आया LLM-as-judge तरीका है। आप सिर्फ **criteria** देते हैं (जैसे "coherence")। LLM पहले अपने evaluation steps (chain-of-thought) लिखता है, फिर form भरकर score देता है। Final score score-tokens का **probability-weighted average** होता है, जिससे एक integer से ज़्यादा बारीक number मिलता है।

---

## 🔴 Problem it Solves
Simple judge prompts give coarse, clumpy scores (almost always 4). Hand-written rubrics are hard to get right for every criterion. G-Eval auto-generates steps and uses token probabilities, so it separates "slightly better" from "slightly worse" and correlates better with human judgement on summarisation-style tasks.

## 🔴 यह क्यों बना? (Hindi)
सरल judge prompts मोटे, एक जैसे scores देते हैं (लगभग हमेशा 4)। हर criterion के लिए हाथ से rubric लिखना कठिन है। G-Eval steps खुद बनाता है और token probabilities इस्तेमाल करता है, इसलिए "थोड़ा बेहतर" और "थोड़ा खराब" में फर्क कर पाता है और summarisation जैसे tasks में human judgement से बेहतर मेल खाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write task description + criteria (e.g. "Faithfulness to the tariff text")
Step 2 → LLM generates numbered evaluation steps (auto CoT) - done once, cached
Step 3 → Build form prompt: steps + input + output + "Score (1-5):"
Step 4 → Call LLM, request logprobs for the score token
Step 5 → Take top-k token probabilities for "1".."5"
Step 6 → Final = sum(score_i x prob_i), normalised over the valid score tokens
Step 7 → Average across rows; compare with human labels
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Task description + criteria लिखो (जैसे "Tariff text के प्रति faithfulness")
Step 2 → LLM numbered evaluation steps खुद बनाता है - एक बार, cache करो
Step 3 → Form prompt बनाओ: steps + input + output + "Score (1-5):"
Step 4 → LLM call करो और score token का logprobs माँगो
Step 5 → "1".."5" tokens की top-k probabilities लो
Step 6 → Final = sum(score_i x prob_i), valid tokens पर normalise
Step 7 → Rows पर average लो; human labels से तुलना करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Criterion: "The explanation must follow General Rules of Interpretation and not contradict the tariff note." G-Eval generates steps like "1. Find the classification. 2. Check the cited note. 3. Look for contradictions." Two explanations both get "4" from a plain judge; G-Eval gives 4.3 and 3.6 from token probabilities, so you can rank them.

**Amazon-style**: Scoring coherence of auto-generated product-description summaries.

## 🟡 Real Example Hindi mein
**Tariff System**: Criterion: "Explanation General Rules of Interpretation का पालन करे और tariff note से न टकराए।" G-Eval steps बनाता है जैसे "1. Classification खोजो। 2. Cited note जाँचो। 3. Contradiction देखो।" साधारण judge दोनों को "4" देता है; G-Eval token probabilities से 4.3 और 3.6 देता है, इसलिए ranking संभव है।

**Amazon-style**: Auto-generated product-description summaries की coherence scoring।

---

## 💻 Code Example — Basic
```python
# Basic: the G-Eval scoring math with fake logprobs (pure Python, runs offline)
import math  # exp to convert logprob -> probability


def weighted_score(top_logprobs: dict[str, float]) -> float:
    """top_logprobs maps token text (e.g. '4') to its log-probability."""
    probs: dict[int, float] = {}  # valid score -> probability
    for tok, lp in top_logprobs.items():  # go through candidate tokens
        t = tok.strip()  # remove spaces
        if t.isdigit() and 1 <= int(t) <= 5:  # keep only valid scores
            probs[int(t)] = math.exp(lp)  # logprob -> prob
    total = sum(probs.values())  # normaliser
    if total == 0:  # no valid score token
        raise ValueError("no valid score tokens in logprobs")  # clear error
    return sum(s * p for s, p in probs.items()) / total  # expected score


fake = {"4": math.log(0.6), "3": math.log(0.25), "5": math.log(0.1), "The": math.log(0.05)}  # model output
print(round(weighted_score(fake), 3))  # (4*.6+3*.25+5*.1)/.95 = 3.789...
```

## 💻 Code Example — Advanced
```python
# Advanced: real G-Eval style scorer with OpenAI logprobs (async, retries, validation)
# pip install openai
import asyncio  # async
import logging  # logs
import math  # exp

from openai import AsyncOpenAI, APIError, RateLimitError  # client and errors

log = logging.getLogger("geval")  # logger
client = AsyncOpenAI()  # uses OPENAI_API_KEY
STEPS_CACHE: dict[str, str] = {}  # criteria -> generated steps


async def get_steps(criteria: str) -> str:
    if criteria in STEPS_CACHE:  # generate once per criterion
        return STEPS_CACHE[criteria]  # reuse (saves tokens)
    r = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=0,
        messages=[{"role": "user", "content":
                   f"Write 3-5 numbered steps to evaluate text for: {criteria}. Steps only."}])
    STEPS_CACHE[criteria] = r.choices[0].message.content or ""  # store steps
    return STEPS_CACHE[criteria]  # return


async def geval(criteria: str, source: str, output: str, retries: int = 3) -> float:
    steps = await get_steps(criteria)  # CoT steps
    prompt = (f"Criteria: {criteria}\nEvaluation steps:\n{steps}\n\n"
              f"Source:\n{source}\n\nOutput:\n{output}\n\n"
              "Score from 1 to 5. Reply with the digit only.\nScore:")  # form prompt
    for attempt in range(retries):  # retry loop
        try:
            r = await client.chat.completions.create(
                model="gpt-4o-mini", temperature=0, max_tokens=1,  # one token: the score
                logprobs=True, top_logprobs=5,  # ask for top-5 alternatives
                messages=[{"role": "user", "content": prompt}])
            tops = r.choices[0].logprobs.content[0].top_logprobs  # candidate tokens
            probs = {int(t.token): math.exp(t.logprob) for t in tops
                     if t.token.strip().isdigit() and 1 <= int(t.token) <= 5}  # valid digits
            if not probs:  # model replied with non-digit
                raise ValueError("no digit in top logprobs")  # trigger retry
            z = sum(probs.values())  # normaliser
            return sum(s * p for s, p in probs.items()) / z  # expected score
        except RateLimitError:  # 429
            await asyncio.sleep(2 ** attempt)  # backoff
        except (APIError, ValueError, AttributeError) as exc:  # other issues
            log.warning("geval attempt %d failed: %s", attempt, exc)  # log
    raise RuntimeError("geval failed")  # give up


async def geval_batch(criteria: str, items: list[tuple[str, str]]) -> list[float]:
    sem = asyncio.Semaphore(8)  # limit concurrency
    async def one(src: str, out: str) -> float:  # score one pair
        async with sem:  # respect limit
            return await geval(criteria, src, out)  # call
    return await asyncio.gather(*(one(s, o) for s, o in items))  # run all
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # web
from pydantic import BaseModel, Field  # validation

app = FastAPI()  # app


class GEvalReq(BaseModel):  # request
    criteria: str = Field(min_length=5)  # what to measure
    source: str  # input/source text
    output: str  # text being graded


@app.post("/eval/geval")  # endpoint
async def geval_endpoint(req: GEvalReq) -> dict:
    try:
        score = await geval(req.criteria, req.source, req.output)  # score
    except RuntimeError as exc:  # judge failure
        raise HTTPException(502, str(exc))  # upstream error
    return {"criteria": req.criteria, "score": round(score, 3)}  # response
```

---

## 🔗 LangChain / LangGraph Connection
The DeepEval library ships G-Eval as a ready metric, usable in LangChain/LangGraph test suites. In a LangGraph app, add a G-Eval node on sampled traffic and log scores to LangSmith.

```python
# DeepEval's G-Eval metric (pip install deepeval)
from deepeval.metrics import GEval  # metric class
from deepeval.test_case import LLMTestCase, LLMTestCaseParams  # test case + params

metric = GEval(
    name="Tariff Faithfulness",  # label in reports
    criteria="Output must follow the tariff note and not invent rules.",  # criteria
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],  # fields judged
    threshold=0.7,  # pass level on 0..1 scale
)
case = LLMTestCase(input="HS code for iPhone?", actual_output="8517.13 per note 3.")  # one test
# metric.measure(case); print(metric.score, metric.reason)   # needs an OpenAI key
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Regenerating evaluation steps on every call
✅ Correct: generate once per criterion and cache

```python
# Wrong - extra LLM call per row
steps = await generate_steps(criteria)
# Right
steps = STEPS_CACHE.get(criteria) or await get_steps(criteria)
```

❌ Mistake 2: Using a model that does not return logprobs and then reading `.logprobs` blindly
✅ Correct: check support; fall back to sampling n=10 and averaging.

❌ Mistake 3: Using one criterion for many qualities ("good, fluent, accurate")
✅ Correct: one G-Eval metric per criterion.

---

## 🧠 Tricky Interview Question
**Q**: "G-Eval gives 4.3 for system A and 4.1 for system B on 30 rows. Can you claim A is better?"

**Answer**: Not safely. Fine-grained scores look precise but judge noise and small samples make a 0.2 gap meaningless. Run more rows, compute confidence intervals (paired bootstrap), check agreement with humans on the criterion, and use pairwise comparison for close calls.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What are the main ingredients of G-Eval?
A1: Criteria, auto-generated CoT evaluation steps, a form-filling prompt, and probability-weighted scoring.

Q2: [Easy] Why use probabilities rather than the printed score?
A2: They capture the judge's uncertainty and give continuous scores, reducing ties.

Q3: [Medium] Which API features are needed?
A3: Logprobs for the output token (OpenAI `logprobs=True, top_logprobs=N`). Where unavailable, sample multiple times and average.

Q4: [Medium] How does G-Eval differ from Ragas faithfulness?
A4: Ragas faithfulness is a fixed claim-by-claim procedure for RAG; G-Eval is a flexible, criteria-driven judge for any quality.

Q5: [Hard] How would you validate G-Eval for a new criterion?
A5: Collect 100+ human-labelled examples, compute Spearman correlation with G-Eval scores, inspect worst disagreements, refine criteria wording, re-test, and track correlation after judge model upgrades.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need custom, subjective criteria (coherence, tone, compliance)
- You want finer-grained scores than 1-5 integers

❌ Avoid when:
- A deterministic check works
- The provider returns no logprobs and budget is tight

---

## 📊 Visual Diagram
```
 criteria ─► LLM writes steps (cached)
                  │
 source + output + steps + "Score:" ─► LLM (max_tokens=1, logprobs)
                  │
        P("1")..P("5") ─► Σ score × prob ─► 4.3
```

---

## 💰 Cost Impact
Steps generation: ~200 tokens once per criterion (cached). Each scoring call: ~500-1,500 input tokens, 1 output token. 1,000 rows on gpt-4o-mini ≈ 1M input tokens ≈ $0.15. Output cost is almost zero.
Optimise: cache steps, shorten source text, use top_logprobs=5 only, batch with async limits.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| G-Eval | CoT + token-probability judging | CoT + token probability से judging |
| Logprobs | Log probabilities of tokens | Tokens की log probability |
| Form-filling | Prompt ends with "Score:" | Prompt का "Score:" पर खत्म होना |
| Spearman | Rank correlation | Rank correlation |
| Bootstrap | Resampling to get confidence interval | Resampling से confidence interval |

---

## ⚡ 3-Line Summary
English: G-Eval = criteria, auto steps, form prompt, probability-weighted score. It gives smoother scores than plain judges. Still validate against humans and avoid over-reading small gaps.
Hindi: G-Eval = criteria, auto steps, form prompt, probability-weighted score। यह साधारण judges से smooth scores देता है। फिर भी humans से validate करो और छोटे gap को ज़्यादा मत पढ़ो।

---

## ➡️ Next Topic
**405. DeepEval Library** - pytest-style LLM testing with G-Eval and many ready metrics.
