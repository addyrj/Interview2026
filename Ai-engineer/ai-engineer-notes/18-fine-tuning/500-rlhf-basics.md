
# 500. RLHF Basics
# हिंदी में: RLHF की बुनियादी बातें

---

## 🔵 Simple Definition (English)
RLHF (Reinforcement Learning from Human Feedback) aligns a model with human preferences. Humans rank pairs of answers, a reward model learns those preferences, and then the LLM is optimised with reinforcement learning (commonly PPO) to produce answers the reward model scores highly, while staying close to the SFT model.

## 🔵 सरल परिभाषा (Hindi)
RLHF (Reinforcement Learning from Human Feedback) model को human preferences के हिसाब से align करता है। इंसान दो answers में से बेहतर चुनते हैं, reward model वह preference सीखता है, फिर LLM को reinforcement learning (आमतौर पर PPO) से optimise किया जाता है ताकि reward model से high score वाले answers बनें, और model SFT model के क़रीब रहे।

---

## 🔴 Problem it Solves
SFT only imitates. "Good" answers are hard to write but easy to compare: humans can say which of two answers is better, helpful, or safer. RLHF turns these comparisons into a training signal, reducing harmful, rude or unhelpful outputs and improving things that are hard to specify as rules.

## 🔴 यह क्यों बना? (Hindi)
SFT सिर्फ़ नक़ल करता है। "अच्छा" answer लिखना कठिन है पर दो answers की तुलना आसान है: इंसान बता सकता है कौन सा ज़्यादा helpful या safe है। RLHF इन तुलनाओं को training signal बनाता है, जिससे harmful, rude या unhelpful outputs घटते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → SFT: fine-tune base model on demonstrations -> policy model (reference copy kept)
Step 2 → Collect comparisons: for a prompt, sample 2+ answers, humans pick the better one
Step 3 → Train a reward model (RM) to give a higher scalar score to the preferred answer
Step 4 → RL step: policy generates answers, RM scores them
Step 5 → Update the policy (PPO) to raise the reward
Step 6 → KL penalty: punish drifting too far from the reference SFT model (avoids reward hacking and gibberish)
Step 7 → Evaluate for helpfulness, safety and regressions; iterate
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → SFT: demos पर base model fine-tune -> policy model (reference copy रखो)
Step 2 → Comparisons जमा करो: एक prompt के 2+ answers, इंसान बेहतर चुनता है
Step 3 → Reward model (RM) train करो जो preferred answer को ज़्यादा score दे
Step 4 → RL step: policy answers बनाती है, RM score देता है
Step 5 → Reward बढ़ाने के लिए policy update (PPO)
Step 6 → KL penalty: reference SFT model से ज़्यादा दूर जाने पर सज़ा (reward hacking से बचाव)
Step 7 → Helpfulness, safety और regressions evaluate करो; दोहराओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: Customs officers compare two explanations for the same HS classification: one cites the right legal note and heading, the other is vague. Thousands of such comparisons train a reward model that prefers precise, cited, cautious explanations. RLHF-style tuning then reduces confident wrong justifications.

**Zomato AI**: Raters pick which of two restaurant recommendation replies is more helpful and polite; the reward model learns this taste.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs officers एक ही HS classification के दो explanations compare करते हैं: एक सही legal note और heading cite करता है, दूसरा अस्पष्ट है। हज़ारों ऐसी comparisons से reward model सीखता है कि precise, cited और सतर्क explanations बेहतर हैं। फिर RLHF-style tuning से confident पर ग़लत justifications घटते हैं।

**Zomato AI**: Raters चुनते हैं कि restaurant recommendation के दो replies में कौन ज़्यादा helpful और polite है; reward model यह पसंद सीखता है।

---

## 💻 Code Example — Basic
```python
# Pure-Python reward-model loss (Bradley-Terry) for one preference pair
import math  # for exp and log


def pairwise_loss(score_chosen: float, score_rejected: float) -> float:
    """Loss = -log(sigmoid(chosen - rejected)); small when chosen scores higher."""
    diff = score_chosen - score_rejected  # margin between the two answers
    return -math.log(1.0 / (1.0 + math.exp(-diff)))  # negative log sigmoid


if __name__ == "__main__":
    print(round(pairwise_loss(2.0, 0.5), 4))  # RM agrees with human -> low loss
    print(round(pairwise_loss(0.5, 2.0), 4))  # RM disagrees -> high loss
```

## 💻 Code Example — Advanced
```python
# Preference data pipeline + KL-shaped reward (production style, pure Python)
import asyncio  # async support
import json  # serialise
import logging  # logging
from dataclasses import dataclass  # data container

logger = logging.getLogger("rlhf")  # logger


@dataclass
class Pref:
    prompt: str  # the question
    chosen: str  # answer humans preferred
    rejected: str  # answer humans rejected


def validate(p: Pref) -> bool:
    """Reject empty or identical pairs (useless for training)."""
    return bool(p.prompt and p.chosen and p.rejected) and p.chosen != p.rejected  # basic sanity


def shaped_reward(rm_score: float, logp_policy: float, logp_ref: float, beta: float = 0.1) -> float:
    """RLHF reward = RM score - beta * KL estimate (log-prob ratio) per sample."""
    return rm_score - beta * (logp_policy - logp_ref)  # penalise drifting from reference


def export(prefs: list[Pref], path: str) -> int:
    """Write valid pairs as JSONL (prompt/chosen/rejected is the format used by TRL reward/DPO trainers)."""
    n = 0  # count written
    try:
        with open(path, "w", encoding="utf-8") as f:  # open file
            for p in prefs:  # iterate pairs
                if not validate(p):  # skip bad rows
                    logger.warning("skipped invalid pair")  # log
                    continue  # next
                f.write(json.dumps(p.__dict__, ensure_ascii=False) + "\n")  # write row
                n += 1  # count
    except OSError as exc:  # disk problem
        logger.error("export failed: %s", exc)  # log
        raise  # propagate
    return n  # number written


async def export_async(prefs: list[Pref], path: str) -> int:
    """Async wrapper."""
    return await asyncio.to_thread(export, prefs, path)  # offload
```
Libraries: Hugging Face `trl` provides reward-model and PPO-style trainers; API details change between versions, so check the current docs. Token usage: RLHF generates many samples per step, so training token cost is much higher than SFT.

---

## 🟠 FastAPI Integration
Collect preference data from real users with a feedback endpoint (thumbs or A/B pick).

```python
from fastapi import FastAPI  # web framework
from pydantic import BaseModel  # validation

app = FastAPI()  # app
STORE: list[dict] = []  # use a database in production


class Feedback(BaseModel):
    prompt: str  # user question
    answer_a: str  # first candidate
    answer_b: str  # second candidate
    winner: str  # "a" or "b"


@app.post("/feedback")
async def feedback(fb: Feedback) -> dict:
    chosen = fb.answer_a if fb.winner == "a" else fb.answer_b  # preferred
    rejected = fb.answer_b if fb.winner == "a" else fb.answer_a  # other one
    STORE.append({"prompt": fb.prompt, "chosen": chosen, "rejected": rejected})  # save pair
    return {"saved": len(STORE)}  # count
```

---

## 🔗 LangChain / LangGraph Connection
LangSmith feedback (topic 422) stores human ratings per run; these become preference pairs. LangGraph human-in-the-loop nodes can show two candidate answers and record the pick. Note that LangChain does not run RLHF itself; it helps collect and evaluate data.

```python
# Sketch: attach a human rating to a traced run (requires LangSmith account)
from langsmith import Client  # LangSmith client

client = Client()  # reads LANGSMITH_API_KEY from env
# client.create_feedback(run_id, key="preferred", score=1)  # run_id from your traced call (illustrative)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Skipping the KL penalty
✅ Correct: Keep the policy near the reference or it learns to exploit the reward model (reward hacking).
```python
# Wrong
reward = rm_score
# Right
reward = rm_score - 0.1 * (logp_policy - logp_ref)
```

❌ Mistake 2: Noisy, biased human labels (for example always preferring longer answers)
✅ Correct: Write clear rater guidelines, measure inter-rater agreement, control for length.
```python
# Wrong: pick winner = longer answer
# Right: audit data; check correlation between "chosen" and length, then rebalance
```

---

## 🧠 Tricky Interview Question
**Q**: "Your RLHF model's reward score keeps rising but human raters say it is getting worse. Why?"

**Answer**: Reward hacking (Goodhart's law). The reward model is only a proxy; the policy found outputs that score high but humans dislike (for example verbose, flattering answers). Fixes: stronger KL penalty, early stopping, refresh the reward model with new human comparisons on the policy's current outputs, ensembles of reward models, and always judge by held-out human or strong LLM-judge evals rather than the training reward.

---

## ⚫ Interview Questions + Answers

Q1: What are the three stages of RLHF?
A1: SFT, reward model training from human comparisons, then RL optimisation (PPO) with a KL penalty.

Q2: What does a reward model output?
A2: A single scalar score for a (prompt, response) pair; higher means more preferred by humans.

Q3: Why is a KL penalty used?
A3: To keep the policy close to the reference SFT model, preventing reward hacking and loss of fluency.

Q4: How does DPO relate to RLHF?
A4: DPO (topic 501) trains directly on preference pairs with a simple loss and no separate reward model or RL loop, so it is simpler and cheaper, though RLHF-with-PPO can still be useful at large scale.

Q5: Would you use RLHF for a small tariff product team?
A5: Rarely. It needs rater workforce, reward modelling and unstable RL training. I would first try better prompts, RAG, SFT and then DPO on collected preference pairs. Use RLHF only if simpler methods plateau and I have the budget and infra.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Quality is subjective and hard to specify as rules
- You have many human preference labels and ML infra
- Safety/helpfulness alignment is critical

❌ Avoid when:
- SFT, prompting or DPO already meets the bar
- Small team, small data, limited GPUs
- You cannot monitor for reward hacking

---

## 📊 Visual Diagram
```
 Base --SFT--> Policy (+ frozen Reference copy)
                 |
   prompt --> 2 answers --> human picks better --> preference pairs
                                                    |
                                          train Reward Model (RM)
                                                    |
   Policy generates --> RM score - beta*KL(Policy||Reference)
                 ^                         |
                 +------ PPO update -------+
```

---

## 💰 Cost Impact
RLHF is the most expensive alignment path: human labelling (people-hours), reward model training, and RL that samples many generations per update, often with 3-4 models in memory (policy, reference, reward, sometimes value). Token cost is a multiple of SFT because of generation during training (illustrative).

Optimise: use DPO or other offline preference methods first, LoRA for policy updates, smaller reward models, active learning to label only uncertain pairs, LLM-as-judge for pre-filtering (validate against humans), and limit generation length.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RLHF | RL from human feedback | Human feedback से RL |
| Reward model | Scores answers | Answers को score देने वाला model |
| Policy | Model being trained | जो model train हो रहा है |
| PPO | Common RL algorithm | आम RL algorithm |
| KL penalty | Stay near reference | Reference के पास रहने की सज़ा |
| Reward hacking | Exploit the proxy | Proxy का ग़लत फ़ायदा उठाना |
| Preference pair | Chosen vs rejected | पसंद बनाम नापसंद answer |

---

## ⚡ 3-Line Summary
English: RLHF = SFT, then a reward model learned from human comparisons, then RL (PPO) with a KL penalty. It optimises subjective qualities beyond imitation. It is costly and fragile, so try prompting, SFT and DPO first.
Hindi: RLHF = SFT, फिर human comparisons से reward model, फिर KL penalty के साथ RL (PPO)। यह imitation से आगे subjective quality सुधारता है। महँगा और fragile है, इसलिए पहले prompting, SFT और DPO आज़माओ।

---

## ➡️ Next Topic
**501. DPO (Direct Preference Optimization)** — a simpler alternative that learns from preference pairs without a reward model or RL loop.
