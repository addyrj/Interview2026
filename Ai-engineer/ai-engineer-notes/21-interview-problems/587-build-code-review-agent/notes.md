---

# 587. Build Code Review Agent
# हिंदी में: Code Review Agent बनाना

---

## 🔵 Simple Definition (English)
A code review agent first runs cheap, deterministic checks (here, Python `ast` rules) to find real problems, then lets an LLM write a human summary from those verified findings only. The result is structured so CI can post it as PR comments.

## 🔵 सरल परिभाषा (Hindi)
Code review agent पहले सस्ते, deterministic checks (यहाँ Python `ast` rules) से असली problems ढूँढता है, फिर LLM सिर्फ़ उन verified findings से human summary लिखता है। Result structured होता है ताकि CI उसे PR comments में डाल सके।

---

## 🔴 Problem it Solves
Pure-LLM reviewers hallucinate issues, miss obvious ones (hard-coded secrets) and cost tokens on every line. Human reviewers get tired of flagging the same mistakes (bare except, mutable defaults) again and again.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ़ LLM reviewer गलत issues बना देते हैं, साफ़ गलतियाँ (hard-coded secret) छोड़ देते हैं और हर line पर tokens खर्च करते हैं। Human reviewers बार-बार वही गलतियाँ (bare except, mutable default) बताकर थक जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → ast.parse(source); SyntaxError -> verdict "block"
Step 2 → ast.walk the tree and apply rules: no-eval, bare-except,
         mutable-default, hardcoded-secret
Step 3 → Each hit becomes Finding(line, severity, rule, message)
Step 4 → Sort findings by line
Step 5 → mock_llm_summary(findings): summary from verified findings only
Step 6 → verdict = "block" if any high severity, else "approve"
Step 7 → Return dict (asdict findings) for CI to post
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → ast.parse(source); SyntaxError आए तो verdict "block"
Step 2 → tree पर ast.walk करके rules: no-eval, bare-except,
         mutable-default, hardcoded-secret
Step 3 → हर hit Finding(line, severity, rule, message) बनता है
Step 4 → findings को line के हिसाब से sort करो
Step 5 → mock_llm_summary(findings): सिर्फ़ verified findings से summary
Step 6 → कोई high severity हो तो "block", वरना "approve"
Step 7 → CI के लिए dict (asdict) लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: every PR to the classifier repo is reviewed automatically. A developer who commits `API_KEY = "sk-live-123456"` is blocked with a high-severity finding on line 3 before the key reaches production.

**Other**: Amazon-style internal bots that comment on pull requests; Zomato backend teams enforcing "no bare except".

## 🟡 Real Example Hindi mein
**Tariff System**: classifier repo के हर PR का automatic review होता है। जो developer `API_KEY = "sk-live-123456"` commit करता है उसे line 3 पर high-severity finding के साथ block किया जाता है, key production तक नहीं पहुँचती।

**Other**: Amazon जैसे internal bots जो PR पर comment करते हैं; Zomato backend teams "no bare except" लागू करती हैं।

---

## 💻 Code Example — Basic
```python
import ast

code = "try:\n    x = eval('1+1')\nexcept:\n    pass\n"
tree = ast.parse(code)                                    # parse source into a tree
for node in ast.walk(tree):                               # visit every node
    if isinstance(node, ast.ExceptHandler) and node.type is None:
        print("bare except at line", node.lineno)         # bare except at line 3
```

## 💻 Code Example — Advanced
Run: `python3 main.py`. Observed output of my run:
```
block - 4 issues, 2 high severity. Fix high items before merge.
{'line': 3, 'severity': 'high', 'rule': 'hardcoded-secret', 'message': 'secret in source code'}
{'line': 5, 'severity': 'medium', 'rule': 'mutable-default', 'message': 'mutable default argument'}
{'line': 7, 'severity': 'high', 'rule': 'no-eval', 'message': 'eval() on dynamic input is unsafe'}
{'line': 8, 'severity': 'medium', 'rule': 'bare-except', 'message': 'bare except hides real errors'}
```
Excerpt from `main.py` (verdict logic):
```python
import ast
import asyncio
from dataclasses import dataclass, asdict


@dataclass
class Finding:
    line: int
    severity: str  # high | medium | low
    rule: str
    message: str


def static_checks(source: str) -> list[Finding]:
    out: list[Finding] = []
    tree = ast.parse(source)                              # may raise SyntaxError
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            out.append(Finding(node.lineno, "medium", "bare-except", "bare except hides real errors"))
    return sorted(out, key=lambda f: f.line)


async def review(source: str) -> dict[str, object]:
    try:
        findings = static_checks(source)
    except SyntaxError as exc:                            # broken code blocks the merge
        return {"verdict": "block", "summary": f"syntax error line {exc.lineno}", "findings": []}
    verdict = "block" if any(f.severity == "high" for f in findings) else "approve"
    return {"verdict": verdict, "summary": f"{len(findings)} issues", "findings": [asdict(f) for f in findings]}
```
The real `static_checks` also covers eval/exec, mutable defaults and secrets.

---

## 🟠 FastAPI Integration
A webhook endpoint receives changed file contents and returns the review JSON that a CI step turns into comments.

```python
from fastapi import FastAPI

from main import review                                  # our module

app = FastAPI()


@app.post("/review")
async def review_endpoint(source: str) -> dict:
    result = await review(source)                        # never raises on SyntaxError
    return result                                        # CI fails the job if verdict == "block"
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph fits well: a `static` node, an `llm_review` node for subtle issues, and a `verdict` node. Static findings are passed into the LLM prompt as ground truth.

```python
from typing import TypedDict


class ReviewState(TypedDict):
    source: str
    findings: list[dict]
    summary: str
    verdict: str


# graph.add_node("static", static_node); graph.add_node("summarise", llm_node)
# graph.add_edge("static", "summarise"); graph.add_edge("summarise", "verdict")
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Asking the LLM to find all bugs with no tool results.
✅ Correct: run deterministic checks first and give the LLM only verified findings.

```python
# Wrong: prompt = "Review this code: " + source
# Right: prompt = "Summarise these verified findings: " + json.dumps(findings)
```

❌ Mistake 2: Crashing on code that does not parse.
✅ Correct: catch `SyntaxError` and return a "block" verdict with the line number.

❌ Mistake 3: Executing the code under review. `ast.parse` only reads it; never `exec` it.

---

## 🧠 Tricky Interview Question
**Q**: "Your rule `hardcoded-secret` flags `PRIMARY_KEY = 'id'` in a database model. How do you cut false positives?"

**Answer**: The rule matches any string assigned to a name containing "key" or "secret". Improve precision: skip short values or known words, check entropy or known token prefixes (`sk-`, `AKIA`), use an allowlist/inline `# noqa`, and give the severity "medium" when unsure. Track false-positive rate, since a noisy reviewer gets ignored.

---

## ⚫ Interview Questions + Answers

Q1: Why AST checks before the LLM?
A1: They are free, fast, deterministic and cannot hallucinate; the LLM then only explains.

Q2: What does `Finding` contain and why?
A2: Line, severity, rule, message: enough for CI to post an inline comment.

Q3: How is the verdict decided?
A3: Any high-severity finding blocks; otherwise approve. Syntax errors also block.

Q4: Why `sorted(out, key=lambda f: f.line)`?
A4: `ast.walk` is not in source order, so sorting gives stable, readable output.

Q5 (Hard): How do you extend this to multi-language repos and large diffs?
A5: Use tree-sitter or language linters per file type, review only changed hunks plus context, run files in parallel, cap tokens per file, and let the LLM handle only the subtle semantic checks on top of tool output.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have well-defined rules (security, style, anti-patterns)
- You want automated PR gating

❌ Avoid when:
- Rules are fuzzy design opinions (keep a human in the loop)

---

## 📊 Visual Diagram
```
 PR source ─► ast.parse ──(SyntaxError)──► block
                 │
                 ▼
        rules: eval | bare except | mutable default | secret
                 │
                 ▼
          list[Finding] ─► LLM summary (verified only)
                 │
                 ▼
   verdict: any high? ─ yes ─► block   no ─► approve
                 │
                 ▼
          CI posts PR comments
```

---

## 💰 Cost Impact
The static pass costs zero tokens. The LLM sees only the short findings list, not the whole file, so input stays small. Run the LLM only when findings exist or the diff is non-trivial; use a small model for summaries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AST | Tree form of source code | Code का tree रूप |
| Finding | One detected issue | एक पकड़ी गई समस्या |
| Severity | How serious (high/medium/low) | गंभीरता |
| Static analysis | Checking code without running it | बिना चलाए code जाँचना |
| False positive | Wrong alarm | गलत alarm |

---

## ⚡ 3-Line Summary
English: Run deterministic AST rules first. Let the LLM summarise only verified findings. Block merges on high severity or syntax errors.
Hindi: पहले deterministic AST rules चलाओ। LLM सिर्फ़ verified findings का summary लिखे। High severity या syntax error पर merge block करो।

---

## ➡️ Next Topic
**588. Build Research Agent** — from reviewing code to gathering information: plan sub-questions, search in parallel, cite sources.
