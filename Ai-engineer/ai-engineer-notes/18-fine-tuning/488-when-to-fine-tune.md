---

# 488. When to Fine Tune
# हिंदी में: Fine Tune कब करें

---

## 🔵 Simple Definition (English)
Fine tune when prompting and RAG are not enough, you have good example data, and the task is stable and repeated at high volume. Fine tuning is a last-mile tool for consistent behaviour, not a first step.

## 🔵 सरल परिभाषा (Hindi)
Fine tune तब करो जब prompting और RAG काफ़ी न हों, आपके पास अच्छा example data हो, और task stable हो तथा बहुत volume में बार-बार चलता हो। Fine tuning आख़िरी कदम का tool है जो consistent behaviour देता है, पहला कदम नहीं।

---

## 🔴 Problem it Solves
Teams either fine tune too early (wasting money) or too late (paying for huge prompts forever). A clear checklist of signals gives a repeatable decision.

## 🔴 यह क्यों बना? (Hindi)
Teams या तो बहुत जल्दी fine tune करती हैं (पैसा बर्बाद) या बहुत देर से (हमेशा बड़े prompts का खर्च)। Signals की साफ़ checklist से decision repeatable बनता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write the best prompt you can and measure on an eval set
Step 2 → Add few-shot examples and structured output; measure again
Step 3 → Still failing on format/tone/edge labels? Collect failures
Step 4 → Check you have 100+ clean examples (ideally 500+)
Step 5 → Check volume: enough calls that token savings repay training
Step 6 → Check the task is stable (labels will not change next month)
Step 7 → If all yes → fine tune; else improve prompt/data first
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → जितना अच्छा हो सके prompt लिखो और eval set पर नापो
Step 2 → Few-shot examples और structured output जोड़ो; फिर नापो
Step 3 → अब भी format/tone/edge labels में fail? Failures इकट्ठा करो
Step 4 → देखो 100+ साफ़ examples हैं (बेहतर 500+)
Step 5 → Volume देखो: क्या token savings training cost चुका देंगी
Step 6 → देखो task stable है (labels अगले महीने नहीं बदलेंगे)
Step 7 → सब हाँ → fine tune; वरना पहले prompt/data सुधारो
```

---

## 🟡 Real World Example
**Tariff Classification System**: 2 million product descriptions per month, labels are HS chapters (stable for years). The prompted large model gets 82 percent chapter accuracy and costs a lot due to 900 token prompts. We have 20,000 customs-verified examples. All signals say yes, so we fine tune a small model: 91 percent accuracy at lower cost.

**Zomato-style**: Auto-tagging 5 million reviews per month into fixed tags is a classic fine tuning case.

## 🟡 Real Example Hindi mein
**Tariff System**: हर महीने 20 लाख product descriptions, labels HS chapters हैं (सालों तक stable)। Prompted बड़ा model 82 percent chapter accuracy देता है और 900 token prompts की वजह से महँगा है। हमारे पास 20,000 customs-verified examples हैं। सारे signals हाँ हैं, इसलिए छोटा model fine tune करते हैं: 91 percent accuracy कम cost में।

**Zomato-style**: हर महीने 50 लाख reviews को fixed tags में बाँटना fine tuning का classic case है।

---

## 💻 Code Example — Basic
```python
# Basic: a scoring checklist that says whether fine tuning looks worthwhile
from typing import Dict  # type hints

signals: Dict[str, bool] = {  # answer each signal with True/False
    "prompt_baseline_measured": True,  # did we measure the prompt first?
    "prompt_not_good_enough": True,  # quality bar still missed?
    "has_100_plus_clean_examples": True,  # enough labelled data?
    "high_call_volume": True,  # many calls per month?
    "task_is_stable": True,  # labels will not change soon?
}

score: int = sum(signals.values())  # count True values
print(f"Signals met: {score}/{len(signals)}")  # show score
if all(signals.values()):  # every signal must be yes
    print("Fine tuning is worth trying")  # go
else:
    missing = [k for k, v in signals.items() if not v]  # list failed signals
    print("Fix first:", missing)  # what to improve
```

## 💻 Code Example — Advanced
```python
# Production style: an async readiness check using real data statistics
import asyncio  # async version
import json  # read JSONL lines
from dataclasses import dataclass, field  # structured report
from typing import List  # type hints


@dataclass
class Readiness:
    n_examples: int  # number of valid examples
    n_errors: int  # lines that failed to parse
    ready: bool  # final decision
    reasons: List[str] = field(default_factory=list)  # why not ready


async def check_readiness(path: str, min_examples: int = 100) -> Readiness:
    """Read a JSONL file and decide if there is enough usable data."""
    ok, bad = 0, 0  # counters
    try:
        with open(path, "r", encoding="utf-8") as f:  # open dataset
            for line in f:  # each line is one example
                try:
                    row = json.loads(line)  # parse JSON
                    if "messages" in row and len(row["messages"]) >= 2:  # basic shape check
                        ok += 1  # valid example
                    else:
                        bad += 1  # wrong shape
                except json.JSONDecodeError:  # broken line
                    bad += 1
                await asyncio.sleep(0)  # let other tasks run on big files
    except FileNotFoundError:  # missing file
        return Readiness(0, 0, False, ["dataset file not found"])
    reasons: List[str] = []  # collect problems
    if ok < min_examples:  # too few examples
        reasons.append(f"only {ok} valid examples, need {min_examples}")
    if bad > ok * 0.05:  # more than 5 percent broken
        reasons.append(f"{bad} broken lines")
    return Readiness(ok, bad, not reasons, reasons)  # final report


if __name__ == "__main__":
    print(asyncio.run(check_readiness("missing.jsonl")))  # demo: file missing case
```

---

## 🟠 FastAPI Integration
Expose the readiness check as an internal admin endpoint so data teams can validate datasets before any training spend.

```python
from fastapi import FastAPI, UploadFile  # framework + upload type
import json  # parse JSONL

app = FastAPI()  # app


@app.post("/finetune/readiness")
async def readiness(file: UploadFile) -> dict:
    """Count valid examples in an uploaded JSONL file."""
    raw = (await file.read()).decode("utf-8")  # read bytes then text
    valid, invalid = 0, 0  # counters
    for line in raw.splitlines():  # one example per line
        try:
            json.loads(line)  # try to parse
            valid += 1
        except json.JSONDecodeError:
            invalid += 1  # count bad lines
    return {"valid": valid, "invalid": invalid, "ready": valid >= 100 and invalid == 0}
```

---

## 🔗 LangChain / LangGraph Connection
Use LangSmith datasets and evaluators to measure the prompt baseline (step 1 of the flow). Failing traces from production become your training examples later.

```python
# Illustrative: evaluate a chain on a dataset before deciding to fine tune
# from langsmith import Client           # LangSmith client
# client = Client()                      # needs LANGSMITH_API_KEY
# results = client.evaluate(chain.invoke, data="tariff-eval", evaluators=[...])
# Low accuracy on format/tone cases + stable labels => candidate for fine tuning
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Fine tuning with no baseline
✅ Correct: Measure the prompted model first so you know the improvement.

```python
# Wrong: "tuned model feels better"
# Right: baseline 82% vs tuned 91% on the same held-out eval set
```

❌ Mistake 2: Tuning on unstable labels
✅ Correct: Wait until label definitions are stable.

```python
# Wrong: train on categories the business renames every month
# Right: freeze the taxonomy, version it, then train
```

---

## 🧠 Tricky Interview Question
**Q**: "Volume is only 2,000 calls a month but quality is poor. Fine tune?"

**Answer**: Cost savings will not justify it, but quality might. Low volume means the token savings argument is weak; the only reason to tune is a quality gap prompting cannot close. First improve prompts, add few-shot and structured output, maybe use a stronger model. Tune only if quality is still short and you have clean data.

---

## ⚫ Interview Questions + Answers

Q1: Name two good reasons to fine tune. (Easy)
A1: Consistent output format/tone, and reducing prompt size (cost and latency) at high volume.

Q2: How many examples do you need? (Easy)
A2: Providers set a small minimum (OpenAI requires at least 10), but practical quality usually needs hundreds. Start with 50 to 100 clean examples, then scale if the eval improves.

Q3: Why does latency improve after tuning? (Medium)
A3: Shorter prompts mean fewer input tokens to process, and a smaller tuned model often replaces a larger one.

Q4: How do you detect it is time to fine tune? (Medium)
A4: Eval shows persistent errors in format or labels despite good prompts, token bills are dominated by long instructions, and you have stable, labelled data.

Q5: How would you justify fine tuning to a CFO? (Hard)
A5: Show break-even: training cost divided by monthly savings (prompt tokens saved times volume, plus model downgrade savings). Add quality gains in business terms like fewer manual reviews. Include retraining cost when base models are retired.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Prompt and RAG tried, quality gap remains
- Stable task, high volume, clean labelled data
- Strict style or schema needed

❌ Avoid when:
- No eval set or baseline
- Data is tiny, noisy or changing
- Problem is missing knowledge

---

## 📊 Visual Diagram
```
 Prompt engineering ──good enough?──► YES ► stop
        │ NO
        ▼
 Few-shot + structured output ──good enough?──► YES ► stop
        │ NO
        ▼
 Add RAG (if facts missing) ──good enough?──► YES ► stop
        │ NO
        ▼
 Clean data + stable task + volume? ──► YES ► FINE TUNE
```

---

## 💰 Cost Impact
- Break-even months = training cost / (monthly cost before - monthly cost after).
- Largest savings come from dropping long few-shot prompts (input tokens) and moving to a smaller model.
- Example (illustrative): 1M calls, 600 prompt tokens cut to 30 saves about 570M input tokens per month.
- Optimise by training on a small sample first, then scaling only if eval improves.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Baseline | Measured result before changes | बदलाव से पहले का नतीजा |
| Break-even | Point where savings repay cost | जहाँ बचत लागत चुका दे |
| Eval set | Held-out graded questions | अलग रखे graded सवाल |
| Taxonomy | Fixed list of labels | Labels की तय सूची |
| Volume | Number of calls | Calls की संख्या |
| Few-shot | Examples in prompt | Prompt में examples |

---

## ⚡ 3-Line Summary
English: Fine tune only after prompting and RAG fail to meet the quality bar.
You need clean labelled data, a stable task and enough volume.
Always compare against a measured baseline.
Hindi: Fine tune तभी करो जब prompting और RAG quality bar पूरा न करें।
साफ़ labelled data, stable task और पर्याप्त volume चाहिए।
हमेशा measured baseline से तुलना करो।

---

## ➡️ Next Topic
**489. When NOT to Fine Tune** — the common traps and cases where fine tuning hurts.
