"""ReAct agent: Thought -> Action -> Observation loop parsed from plain text.

Offline: `mock_llm` emits a scripted ReAct transcript, one step per call.
"""
from __future__ import annotations

import asyncio
import re
from typing import Callable

RATES = {"8517.13": 0.20, "8471.30": 0.0}


def search_hs(query: str) -> str:
    """Tool: product -> HS code."""
    return {"smartphone": "8517.13", "laptop": "8471.30"}.get(query.strip().lower(), "NOT_FOUND")


def duty_rate(code: str) -> str:
    """Tool: HS code -> duty rate."""
    code = code.strip()
    return str(RATES[code]) if code in RATES else "NOT_FOUND"


TOOLS: dict[str, Callable[[str], str]] = {"search_hs": search_hs, "duty_rate": duty_rate}

SCRIPT = [
    "Thought: I need the HS code first.\nAction: search_hs[smartphone]",
    "Thought: Now I need its rate.\nAction: duty_rate[8517.13]",
    "Thought: I have everything.\nFinal Answer: smartphone (8517.13) has 20% duty",
]


def mock_llm(prompt: str) -> str:
    """Return the next scripted step based on how many Observations are already in the prompt."""
    return SCRIPT[min(prompt.count("Observation:"), len(SCRIPT) - 1)]


ACTION_RE = re.compile(r"Action:\s*(\w+)\[(.*?)\]")


def react(question: str, max_steps: int = 6) -> str:
    """Loop: ask LLM, parse Action, run tool, append Observation, stop on Final Answer."""
    prompt = f"Question: {question}\n"
    for _ in range(max_steps):
        out = mock_llm(prompt)
        prompt += out + "\n"
        if "Final Answer:" in out:
            return out.split("Final Answer:", 1)[1].strip()
        m = ACTION_RE.search(out)
        if not m:  # malformed output: tell the model instead of crashing
            prompt += "Observation: could not parse an Action, use Action: tool[input]\n"
            continue
        name, arg = m.groups()
        tool = TOOLS.get(name)
        obs = tool(arg) if tool else f"unknown tool {name}"
        prompt += f"Observation: {obs}\n"
    return "No answer within max_steps"


async def areact(question: str) -> str:
    """Async wrapper for web servers."""
    return await asyncio.to_thread(react, question)


if __name__ == "__main__":
    print(asyncio.run(areact("What is the duty on a smartphone?")))
