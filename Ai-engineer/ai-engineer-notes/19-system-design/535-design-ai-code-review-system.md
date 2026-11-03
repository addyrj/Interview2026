---

# 535. Design: AI Code Review System
# हिंदी में: AI Code Review System का Design

---

## 🔵 Simple Definition (English)
An AI code review system listens to pull request events, reads the diff plus relevant context, asks an LLM for structured review comments, filters noise, and posts inline comments back to the Git host. It supports human reviewers; it does not replace them.

## 🔵 सरल परिभाषा (Hindi)
AI code review system pull request events सुनता है, diff और ज़रूरी context पढ़ता है, LLM से structured review comments माँगता है, noise हटाता है और inline comments Git host पर वापस post करता है। यह human reviewers की मदद करता है, उनकी जगह नहीं लेता।

---

## 🔴 Problem it Solves
Human reviewers are slow, inconsistent, and tired on big PRs. Linters catch style but not logic bugs. Naive "send the whole diff to an LLM" fails: diffs exceed context, the model lacks repo knowledge, and it floods developers with low-value comments.

## 🔴 यह क्यों बना? (Hindi)
Human reviewers धीमे होते हैं और बड़े PRs पर थक जाते हैं। Linters style पकड़ते हैं, logic bugs नहीं। पूरा diff LLM को भेजना भी काम नहीं करता: diff context से बड़ा हो सकता है, model को repo की जानकारी नहीं होती और बेकार comments की भरमार हो जाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Git host webhook (pull_request opened/synchronize) hits our API
Step 2 → Verify webhook signature (HMAC), enqueue a job, return 200 fast
Step 3 → Worker fetches diff, splits per file, skips lockfiles/generated/binary
Step 4 → For each hunk, add context: surrounding lines, related functions, team rules
Step 5 → LLM returns JSON: [{file, line, severity, message, suggestion}]
Step 6 → Validate JSON (Pydantic), drop low severity / duplicates / wrong line numbers
Step 7 → Post inline comments + one summary comment via the Git host API
Step 8 → Store feedback (resolved/dismissed) to tune prompts
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Git host का webhook हमारे API को hit करता है
Step 2 → Signature verify करो (HMAC), job queue में डालो, तुरंत 200 लौटाओ
Step 3 → Worker diff लेता है, file-wise बाँटता है, lockfiles/generated/binary skip करता है
Step 4 → हर hunk के साथ आसपास की lines, related functions और team rules जोड़ता है
Step 5 → LLM JSON देता है: [{file, line, severity, message, suggestion}]
Step 6 → Pydantic से validate, कम severity/duplicates/गलत line numbers हटाओ
Step 7 → Inline comments + एक summary comment post करो
Step 8 → Feedback (resolved/dismissed) store करो ताकि prompts बेहतर हों
```

---

## 🟡 Real World Example
**Tariff Classification System**: The team's PR changes the HS-code lookup function. The reviewer bot flags "line 42: you compare codes as int, so leading zeros in '0101' are lost. Keep codes as strings." That is a real domain bug a linter misses.
**Amazon-style**: A PR touching the pricing service gets an automated comment warning that a float is used for currency.

## 🟡 Real Example Hindi mein
**Tariff System**: Team का PR HS-code lookup function बदलता है। Bot comment करता है "line 42: codes को int में compare कर रहे हो, '0101' का leading zero खो जाएगा। Codes को string रखो।" यह असली domain bug है जो linter नहीं पकड़ता।
**Amazon-style**: Pricing service वाले PR पर bot चेतावनी देता है कि currency के लिए float इस्तेमाल हो रहा है।

---

## 💻 Code Example — Basic
```python
# Basic: parse a unified diff and list added lines with their new line numbers (pure Python)
import re                                              # regex for hunk headers

DIFF = """@@ -10,3 +10,4 @@ def lookup(code):
 def lookup(code):
-    return int(code)
+    value = int(code)
+    return value
"""                                                    # tiny sample diff


def added_lines(diff: str) -> list[tuple[int, str]]:
    """Return (new_line_number, text) for every added line."""
    result: list[tuple[int, str]] = []                 # output list
    new_no = 0                                         # current new-file line number
    for line in diff.splitlines():                     # go line by line
        m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", line)   # hunk header gives start line
        if m:                                          # found a header
            new_no = int(m.group(1)) - 1               # set counter before first line
            continue                                   # go to next line
        if line.startswith("-"):                       # removed line: not in new file
            continue                                   # do not advance counter
        new_no += 1                                    # context or added line advances
        if line.startswith("+"):                       # added line
            result.append((new_no, line[1:]))          # store without the '+'
    return result                                      # done


for no, text in added_lines(DIFF):                     # print findings
    print(no, text)
```

## 💻 Code Example — Advanced
```python
# Production style: async review of one file with structured output, validation, filtering
import asyncio                                         # async and gather
import json                                            # parse LLM JSON
from typing import Literal                             # restricted values

from pydantic import BaseModel, Field, ValidationError  # schema validation


class Comment(BaseModel):
    file: str                                          # path of file
    line: int = Field(ge=1)                            # line number, must be positive
    severity: Literal["low", "medium", "high"]         # importance
    message: str                                       # what is wrong
    suggestion: str | None = None                      # optional fix


PROMPT = ("Review this diff hunk. Return ONLY a JSON list of objects with keys "
          "file, line, severity, message, suggestion. Report real bugs, not style.\n\n{hunk}")   # template


async def call_llm(prompt: str) -> str:
    """Replace with a real client; mocked so it runs offline."""
    await asyncio.sleep(0.01)                          # fake latency
    return '[{"file":"a.py","line":42,"severity":"high","message":"int() drops leading zeros","suggestion":"keep str"}]'


async def review_hunk(file: str, hunk: str, valid_lines: set[int]) -> list[Comment]:
    """Review one hunk and return validated comments."""
    try:
        raw = await asyncio.wait_for(call_llm(PROMPT.format(hunk=hunk)), timeout=30)   # bounded call
        items = json.loads(raw)                        # parse JSON
    except (asyncio.TimeoutError, json.JSONDecodeError):   # model slow or bad JSON
        return []                                      # skip this hunk instead of failing the PR
    out: list[Comment] = []                            # accepted comments
    for item in items:                                 # check each
        try:
            c = Comment(**item)                        # validate shape
        except ValidationError:                        # malformed item
            continue                                   # drop it
        if c.line in valid_lines and c.severity != "low":   # real line and worth saying
            out.append(c)                              # keep
    return out


async def review_pr(hunks: dict[str, tuple[str, set[int]]]) -> list[Comment]:
    """Review all files concurrently (cap concurrency in prod with a Semaphore)."""
    results = await asyncio.gather(*(review_hunk(f, h, v) for f, (h, v) in hunks.items()))   # parallel
    return [c for group in results for c in group]     # flatten
```

---

## 🟠 FastAPI Integration
The webhook endpoint must be fast and safe: verify the HMAC signature, enqueue, return.

```python
import hmac, hashlib, os                               # signature tools
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks   # FastAPI

app = FastAPI()                                        # app
SECRET = os.getenv("WEBHOOK_SECRET", "dev").encode()   # shared secret from env


async def process_pr(payload: dict) -> None:
    """Fetch diff, run review_pr, post comments (omitted)."""
    return None                                        # placeholder


@app.post("/webhooks/pr")
async def pr_hook(req: Request, bg: BackgroundTasks) -> dict:
    body = await req.body()                            # raw bytes needed for signature
    sent = req.headers.get("X-Hub-Signature-256", "")  # GitHub-style header
    good = "sha256=" + hmac.new(SECRET, body, hashlib.sha256).hexdigest()   # expected value
    if not hmac.compare_digest(sent, good):            # constant-time compare
        raise HTTPException(401, "bad signature")      # reject forged calls
    bg.add_task(process_pr, await req.json())          # do work after responding
    return {"queued": True}                            # fast 200
```

---

## 🔗 LangChain / LangGraph Connection
Use `llm.with_structured_output(Schema)` for reliable JSON. In LangGraph, model the flow as nodes: `split_diff` -> `review_hunks` (fan out) -> `dedupe_and_rank` -> `post_comments`. A second "critic" node can re-check high severity findings to cut false positives.

```python
# LangChain structured output (needs API key)
from pydantic import BaseModel                         # schema base
from langchain_openai import ChatOpenAI                # chat model


class Finding(BaseModel):
    line: int                                          # line number
    message: str                                       # issue text


class Findings(BaseModel):
    items: list[Finding]                               # list wrapper


reviewer = ChatOpenAI(model="gpt-4o-mini").with_structured_output(Findings)   # illustrative model
# result = await reviewer.ainvoke("Review this diff: ...")                    # returns Findings
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Trusting LLM line numbers
✅ Correct: build the set of valid changed lines from the diff and drop comments outside it.

```python
# Wrong: post whatever line the model says (API error or comment on wrong line)
# Right: if c.line in valid_lines: post(c)
```

❌ Mistake 2: Commenting on everything
✅ Correct: severity threshold, dedupe, and a cap (say 10 comments per PR). Noisy bots get muted.

❌ Mistake 3: Skipping webhook signature check
✅ Correct: verify HMAC so strangers cannot trigger paid LLM calls.

---

## 🧠 Tricky Interview Question
**Q**: "The bot approves a PR that deleted an authorization check. The diff looked harmless. Why did it miss it?"

**Answer**: A hunk-only view shows the removed lines but not who calls the function or what depends on the check. Add context: callers via code search, the full function, tests, and security rules. Make deletions a special case in the prompt, run static analyzers (Semgrep) for known patterns, and never let AI be the only gate. Also evaluate on a dataset of known-bug PRs.

---

## ⚫ Interview Questions + Answers

Q1: Why use a queue behind the webhook?
A1: Git hosts expect a response within seconds. Reviews take much longer, so enqueue and respond immediately; also gives retries.

Q2: How do you handle a huge diff?
A2: Skip generated files, split by file and hunk, review in parallel, prioritise risky files, and summarise at the end. Cap total tokens per PR.

Q3: How do you reduce false positives?
A3: Severity filter, line validation, a critic pass, static analysis cross-check, and learning from dismissed comments.

Q4: How do you give the model repo knowledge?
A4: Retrieve related files by embeddings or symbol search, include a project guideline file, and add the PR description.

Q5: (Hard) How do you measure quality?
A5: Offline: a labelled set of PRs with known bugs, track precision and recall. Online: acceptance rate of comments (resolved vs dismissed), time to merge, escaped bugs. Optimise precision first, since trust is hard to win back.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many PRs and reviewer bandwidth is low
- You want a consistent first-pass reviewer

❌ Avoid when:
- It is the only approval for security-critical code
- Code cannot leave your network and no private model is available

---

## 📊 Visual Diagram
```
 Git host ──webhook──▶ API (verify HMAC) ──▶ Queue ──▶ Worker
                                                         │
                       fetch diff ◀──────────────────────┤
                       split + context (repo search)     │
                       LLM per hunk (parallel) ──▶ JSON ─▶ validate/filter
                                                         │
 Git host ◀── inline comments + summary ◀────────────────┘
```

---

## 💰 Cost Impact
Cost scales with changed lines, not repo size. A 400-line diff with context is perhaps 6-10k input tokens, and output is small (illustrative). Each extra pass (critic) multiplies cost.
Optimize: skip generated/lock files, use a small model first and escalate only risky hunks, cache by hunk hash for re-pushes (review only new commits), limit context size, set `max_tokens`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Diff / Hunk | Changed lines / one changed block | बदली हुई lines / एक बदला हुआ block |
| Webhook | HTTP callback on an event | Event पर आने वाला HTTP call |
| HMAC | Signature to prove sender | भेजने वाले की पहचान का signature |
| Precision | Share of comments that are correct | सही comments का अनुपात |
| False positive | Wrong warning | गलत चेतावनी |
| Structured output | Model returns a fixed schema | तय schema में output |

---

## ⚡ 3-Line Summary
English: Webhook, queue, per-hunk LLM review, validate, then post comments. Add repo context and filter noise to keep trust. Measure precision and keep humans as the final gate.
Hindi: Webhook, queue, हर hunk पर LLM review, validate, फिर comments post। Repo context जोड़ो और noise हटाओ ताकि भरोसा बना रहे। Precision मापो और final gate इंसान ही रहे।

---

## ➡️ Next Topic
**536. Design: Tariff Classification System**: the main running example, designed end to end.
