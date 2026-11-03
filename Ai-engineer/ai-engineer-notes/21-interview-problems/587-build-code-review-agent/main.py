"""Code review agent: cheap deterministic AST checks first, LLM (mocked) summarises the rest.

Findings are structured so a CI job can post them as PR comments.
"""
from __future__ import annotations

import ast
import asyncio
from dataclasses import dataclass, asdict

SAMPLE = '''
import os
API_KEY = "sk-live-123456"

def add(items=[]):
    try:
        x = eval(input())
    except:
        pass
    return items
'''


@dataclass
class Finding:
    line: int
    severity: str  # high | medium | low
    rule: str
    message: str


def static_checks(source: str) -> list[Finding]:
    """Rule-based checks: free, fast, no hallucinations."""
    out: list[Finding] = []
    tree = ast.parse(source)  # raises SyntaxError for broken code (caller handles)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
            out.append(Finding(node.lineno, "high", "no-eval", f"{node.func.id}() on dynamic input is unsafe"))
        elif isinstance(node, ast.ExceptHandler) and node.type is None:
            out.append(Finding(node.lineno, "medium", "bare-except", "bare except hides real errors"))
        elif isinstance(node, ast.FunctionDef):
            if any(isinstance(d, (ast.List, ast.Dict, ast.Set)) for d in node.args.defaults):
                out.append(Finding(node.lineno, "medium", "mutable-default", "mutable default argument"))
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if any(("key" in n.lower() or "secret" in n.lower()) for n in names):
                out.append(Finding(node.lineno, "high", "hardcoded-secret", "secret in source code"))
    return sorted(out, key=lambda f: f.line)


async def mock_llm_summary(findings: list[Finding]) -> str:
    """Stand-in for an LLM that writes a human summary from the *verified* findings only."""
    await asyncio.sleep(0)
    high = sum(f.severity == "high" for f in findings)
    return f"{len(findings)} issues, {high} high severity. Fix high items before merge."


async def review(source: str) -> dict[str, object]:
    """Run checks, summarise, decide verdict."""
    try:
        findings = static_checks(source)
    except SyntaxError as exc:
        return {"verdict": "block", "summary": f"syntax error line {exc.lineno}", "findings": []}
    summary = await mock_llm_summary(findings)
    verdict = "block" if any(f.severity == "high" for f in findings) else "approve"
    return {"verdict": verdict, "summary": summary, "findings": [asdict(f) for f in findings]}


if __name__ == "__main__":
    result = asyncio.run(review(SAMPLE))
    print(result["verdict"], "-", result["summary"])
    for f in result["findings"]:  # type: ignore[union-attr]
        print(f)
