---

# 290. BDD with behave
# हिंदी में: behave के साथ BDD (सामान्य भाषा में behaviour लिखना)

---

## 🔵 Simple Definition (English)
Behaviour-Driven Development (BDD) describes what a feature should do in plain English using Given / When / Then steps. `behave` is the Python tool that reads those `.feature` files (written in Gherkin) and runs matching Python "step functions". Product people can read the scenarios, and developers make them executable.

## 🔵 सरल परिभाषा (Hindi)
Behaviour-Driven Development (BDD) में feature क्या करे, यह सामान्य अंग्रेज़ी में Given / When / Then steps से लिखा जाता है। `behave` वह Python tool है जो ऐसी `.feature` files (Gherkin भाषा में) पढ़ता है और उनसे मेल खाने वाले Python "step functions" चलाता है। Product के लोग scenarios पढ़ सकते हैं और developers उन्हें चलने लायक बनाते हैं।

---

## 🔴 Problem it Solves
Requirements written in documents get out of date, and developers, testers, and product managers understand them differently. Unit tests are written in code that business people cannot read. BDD makes the examples ("when I pay 900 from a balance of 500, the payment fails") the shared specification: readable by everyone, and executed as an automatic test, so the documentation can never drift from the code.

## 🔴 यह क्यों बना? (Hindi)
Documents में लिखी requirements पुरानी हो जाती हैं और developers, testers व product managers उन्हें अलग-अलग समझते हैं। Unit tests ऐसे code में होते हैं जिसे business के लोग पढ़ नहीं सकते। BDD उदाहरणों ("500 के balance से 900 चुकाने पर payment fail होता है") को साझा specification बना देता है: सबके लिए पढ़ने लायक और अपने आप चलने वाला test, इसलिए documentation code से कभी अलग नहीं होती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write features/wallet.feature in Gherkin: Feature, Scenario, Given / When / Then / And
Step 2 → Write step functions in features/steps/*.py with @given / @when / @then
         and a pattern string:  "a wallet with balance {balance:d}"
Step 3 → Run:  behave     (it finds the "features" folder, matches each step text to a function)
Step 4 → Data passes between steps through the "context" object (context.wallet = ...)
Step 5 → Optional: environment.py hooks (before_scenario, after_all), Background, Scenario Outline + Examples tables, tags (@smoke)
Step 6 → Report shows each scenario/step as passed, failed, or undefined (with a ready-to-copy snippet)

features/
  wallet.feature        <- plain English
  environment.py        <- hooks (optional)
  steps/wallet_steps.py <- Python glue
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → features/wallet.feature Gherkin में लिखो: Feature, Scenario, Given / When / Then / And
Step 2 → features/steps/*.py में @given / @when / @then से step functions लिखो
         और pattern string:  "a wallet with balance {balance:d}"
Step 3 → चलाओ:  behave     (यह "features" folder ढूंढकर हर step text को function से मिलाता है)
Step 4 → Steps के बीच data "context" object से जाता है (context.wallet = ...)
Step 5 → वैकल्पिक: environment.py hooks (before_scenario, after_all), Background, Scenario Outline + Examples tables, tags (@smoke)
Step 6 → Report हर scenario/step को passed, failed या undefined (copy करने लायक snippet के साथ) दिखाती है
```

---

## 🟡 Real World Example
A fintech team (UPI wallet) sits with the product manager and writes scenarios before coding: "Successful payment", "Insufficient funds", "Daily limit exceeded". The PM reviews the wording, the developers write the steps against the `Wallet` service, and the same scenarios run in CI on every commit. When a bank changes the daily limit, the PM edits one number in the `.feature` file and the build tells the team what to update. Many teams also run the scenarios against a staging API with `httpx`.

## 🟡 Real Example Hindi mein
Fintech team (UPI wallet) product manager के साथ बैठकर code से पहले scenarios लिखती है: "सफल payment", "Balance कम", "रोज़ की limit पार"। PM शब्दों की समीक्षा करता है, developers `Wallet` service के लिए steps लिखते हैं और वही scenarios हर commit पर CI में चलते हैं। बैंक रोज़ की limit बदले तो PM `.feature` file में एक संख्या बदलता है और build बताता है कि team को क्या update करना है। कई teams वही scenarios staging API पर `httpx` से भी चलाती हैं।

---

## 💻 Code Example — Basic
```gherkin
# features/wallet.feature  (Gherkin: plain English)
Feature: Wallet payments
  As a customer I want to pay from my wallet so that checkout is fast

  Background:                                    # runs before EVERY scenario
    Given a wallet with balance 500

  Scenario: Successful payment
    When I pay 200
    Then the balance is 300
    And the payment succeeds

  Scenario: Insufficient funds
    When I pay 900
    Then the payment fails with "insufficient funds"
    And the balance is 500
```

```python
# features/steps/wallet_steps.py  (verified with behave 1.3.3, Python 3.13)
from behave import given, when, then              # step decorators
from behave.runner import Context                 # type of the shared context object


class Wallet:                                     # system under test (normally imported from your app)
    def __init__(self, balance: int) -> None:
        self.balance: int = balance               # money in the wallet

    def pay(self, amount: int) -> None:
        if amount > self.balance:                 # not enough money
            raise ValueError("insufficient funds")
        self.balance -= amount                    # deduct


@given("a wallet with balance {balance:d}")       # {balance:d} parses an int from the text
def step_wallet(context: Context, balance: int) -> None:
    context.wallet = Wallet(balance)              # state is shared through context
    context.error = None                          # no error yet


@when("I pay {amount:d}")
def step_pay(context: Context, amount: int) -> None:
    try:
        context.wallet.pay(amount)                # act
    except ValueError as exc:                     # remember the error for a later Then step
        context.error = str(exc)


@then("the balance is {expected:d}")
def step_balance(context: Context, expected: int) -> None:
    assert context.wallet.balance == expected, context.wallet.balance   # plain assert with message


@then("the payment succeeds")
def step_ok(context: Context) -> None:
    assert context.error is None


@then('the payment fails with "{msg}"')
def step_fail(context: Context, msg: str) -> None:
    assert context.error == msg, context.error

# Run:  behave --no-color        (from the folder that contains features/)
# REAL output (trimmed):
#   Scenario: Successful payment      # features/wallet.feature:7
#     Given a wallet with balance 500 # features/steps/wallet_steps.py:15
#     When I pay 200                  # features/steps/wallet_steps.py:21
#     Then the balance is 300         # features/steps/wallet_steps.py:29
#     And the payment succeeds        # features/steps/wallet_steps.py:34
#   ...
#   1 feature passed, 0 failed, 0 skipped
#   4 scenarios passed, 0 failed, 0 skipped      (2 above + 2 from the outline below)
#   14 steps passed, 0 failed, 0 skipped
```

## 💻 Code Example — Advanced
```gherkin
# features/wallet.feature (continued) — Scenario Outline: one scenario, many data rows
  Scenario Outline: Many amounts
    When I pay <amount>
    Then the balance is <left>

    Examples:
      | amount | left |
      | 100    | 400  |
      | 500    | 0    |
```
Real output for the outline: it is expanded into two scenarios, `Many amounts -- @1.1` (pay 100, balance 400) and `@1.2` (pay 500, balance 0); both passed.

```python
# features/environment.py — hooks for set-up and clean-up
from behave.model import Scenario                 # type of the scenario object
from behave.runner import Context                 # shared context


def before_all(context: Context) -> None:
    context.base_url = "http://localhost:8000"    # config shared by all scenarios


def before_scenario(context: Context, scenario: Scenario) -> None:
    if "skip" in scenario.tags:                   # tags like @skip control execution
        scenario.skip("marked @skip")             # skip this scenario with a reason


def after_scenario(context: Context, scenario: Scenario) -> None:
    context.wallet = None                         # clean state between scenarios


# FastAPI version of a step: call the real app in-process with TestClient (no network)
from behave import given, when, then              # decorators
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # in-process client

api: FastAPI = FastAPI()                          # in a real project: from app.main import app
BALANCES: dict[str, int] = {}                     # fake storage


@api.post("/wallets/{wid}/pay")
def pay(wid: str, amount: int) -> dict[str, int]:
    from fastapi import HTTPException
    if amount > BALANCES.get(wid, 0):             # business rule
        raise HTTPException(status_code=400, detail="insufficient funds")
    BALANCES[wid] -= amount                       # deduct
    return {"balance": BALANCES[wid]}


@given("wallet {wid} has balance {balance:d} in the API")
def api_given(context: Context, wid: str, balance: int) -> None:
    BALANCES[wid] = balance                       # arrange
    context.client = TestClient(api)              # create the client once


@when("{wid} pays {amount:d} through the API")
def api_when(context: Context, wid: str, amount: int) -> None:
    context.response = context.client.post(f"/wallets/{wid}/pay", params={"amount": amount})   # act


@then("the API answers {status:d}")
def api_then(context: Context, status: int) -> None:
    assert context.response.status_code == status, context.response.text   # assert on HTTP status
```

Useful commands: `behave --tags=@smoke`, `behave --tags=~@slow` (exclude), `behave features/wallet.feature`, `behave -f json -o out.json` (JSON report), `behave --dry-run` (find undefined steps), `behave --junit` (CI report).

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python behave | JavaScript (Cucumber.js) |
|---------|---------------|--------------------------|
| Spec language | Gherkin `.feature` | Gherkin `.feature` (same) |
| Step definition | `@given("text {x:d}")` | `Given("text {int}", function (x) {...})` |
| Shared state | `context` object | `this` (World) |
| Hooks | `environment.py` | `Before` / `After` hooks |
| Table data | `context.table` | `dataTable` argument |
| Run | `behave` | `npx cucumber-js` |
| Alternative | `pytest-bdd` (works inside pytest) | `jest-cucumber` |

```python
# Python way (behave)
from behave import when

@when("I pay {amount:d}")                         # "{amount:d}" -> int
def step_pay(context, amount: int) -> None:
    context.wallet.pay(amount)
```
```javascript
// JavaScript way (Cucumber.js)
const { When } = require("@cucumber/cucumber");

When("I pay {int}", function (amount) {           // {int} -> number
  this.wallet.pay(amount);                        // "this" is the World (shared state)
});
```

Key difference: the `.feature` files are identical in both worlds (Gherkin is language independent). Only the step glue differs: `behave` uses parse-style patterns and the `context` object; Cucumber.js uses Cucumber expressions and `this`.

---

## 🟠 FastAPI Connection
BDD is a good fit for API acceptance tests: scenarios describe user-visible behaviour ("When I pay 900 through the API, the API answers 400"), and the steps call the app through `TestClient` (in-process, fast) or `httpx` against a staging server (true end-to-end). Keep scenarios at business level (no URLs or JSON in the feature file); put technical details in the step functions. If you prefer to stay inside pytest (fixtures, parametrize, coverage in one run), use the `pytest-bdd` plugin with the same Gherkin files.

```gherkin
# features/api.feature
Feature: Wallet API
  Scenario: Reject overdraft
    Given wallet w1 has balance 500 in the API
    When w1 pays 900 through the API
    Then the API answers 400
```
(The step functions for this scenario are in the Advanced example above.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Writing scenarios as technical scripts ("click button id=pay-btn, POST /api/v1/...")
✅ Correct: describe behaviour in business language; hide the technical detail in steps

```gherkin
# Wrong
When I send POST /wallets/1/pay with JSON {"amount": 900}
# Right
When I pay 900
```

❌ Mistake 2: Using BDD for every unit-level check
✅ Correct: keep BDD for important user-facing flows; use plain pytest for edge-case unit tests (BDD is slower and costs more to maintain)

❌ Mistake 3: Steps that depend on the order or the state of previous scenarios
✅ Correct: each scenario builds its own state (Background / `before_scenario`) and cleans up

❌ Mistake 4: Undefined steps because the step text and pattern do not match (extra space, wrong type like `{amount}` vs `{amount:d}`)
✅ Correct: run `behave --dry-run`; behave prints a ready-to-paste snippet for undefined steps

```python
# Wrong — "{amount}" captures the TEXT "200" as a str, so amount > balance compares str to int -> TypeError
@when("I pay {amount}")
def bad(context, amount): context.wallet.pay(amount)
# Right — ":d" converts to int
@when("I pay {amount:d}")
def good(context, amount: int): context.wallet.pay(amount)
```

---

## 🧠 Tricky Interview Question

```gherkin
Scenario: Pay twice
  Given a wallet with balance 500
  When I pay 200
  And I pay 200
  Then the balance is 100
```
Question: With the step functions from this note, what happens, and which decorator does `And I pay 200` use?
Answer: `And` takes the keyword of the previous step, so `And I pay 200` is matched as a `@when` step (behave looks the text up among `when` steps). The two payments run (500 -> 300 -> 100) and `the balance is 100` passes. Note that in behave the step function is matched by TEXT and step type, not by the exact keyword, and `@step("...")` registers a function usable for any keyword. A common surprise: if the `Then` text is defined only with `@given`, behave reports it as an undefined step.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between TDD and BDD?
A1: TDD is a developer practice driven by unit tests (red, green, refactor). BDD focuses on behaviour and shared language: scenarios in Given/When/Then written with business people, executed as acceptance tests. They complement each other: BDD scenarios on the outside, TDD unit tests inside.

Q2: What is Gherkin and what keywords does it have?
A2: A plain-text format for specifications: `Feature`, `Background`, `Scenario`, `Scenario Outline` with `Examples`, and steps `Given` (context), `When` (action), `Then` (outcome), `And` / `But`. Tags start with `@`.

Q3: How do steps share data in behave?
A3: Through the `context` object: attributes set in one step (`context.wallet`) are visible to later steps in the same scenario. Attributes added in a scenario are cleaned up after it; attributes set in `before_all` live for the whole run.

Q4: What is a Scenario Outline?
A4: A scenario template with `<placeholders>` and an `Examples` table. behave runs it once per row, like `parametrize` in pytest.

Q5: behave or pytest-bdd?
A5: `behave` is a standalone runner with its own conventions (features folder, environment.py, context). `pytest-bdd` runs Gherkin inside pytest, so you reuse fixtures, markers, parametrization, and plugins (coverage, xdist). Teams already on pytest often choose `pytest-bdd`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Product owners/QA should read and review the specifications
- Acceptance tests for core user journeys (checkout, login, payments)
- You want living documentation that is always executable

❌ Avoid when:
- A small team of developers with no business reader (the Gherkin layer is overhead)
- Fine-grained unit or edge-case testing (use pytest)
- Performance-sensitive or highly technical checks (parsers, algorithms)

---

## 📊 Visual Diagram
```
 wallet.feature (English)                steps/wallet_steps.py (Python)
 ┌──────────────────────────────┐        ┌──────────────────────────────────────┐
 │ Given a wallet with balance 500 ────►  @given("a wallet with balance {balance:d}")
 │ When I pay 200               ────────►  @when("I pay {amount:d}")
 │ Then the balance is 300      ────────►  @then("the balance is {expected:d}")
 └──────────────────────────────┘        └──────────────────────────────────────┘
                 \                                   /
                  └──── context (shared state) ─────┘
                                  |
                                  v
                     Wallet / FastAPI app under test
 result: scenario passed / failed / undefined (step missing)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BDD | Behaviour-driven development | Behaviour आधारित development |
| Gherkin | Plain-English spec syntax | सामान्य भाषा की spec syntax |
| Feature / Scenario | A capability / one example of it | क्षमता / उसका एक उदाहरण |
| Given / When / Then | Context / action / outcome | स्थिति / क्रिया / नतीजा |
| Step definition | Python function for a step | Step का Python function |
| context | Object that shares state between steps | Steps के बीच state साझा करने वाला object |

---

## ⚡ 3-Line Summary
English: BDD writes behaviour as Given/When/Then scenarios in `.feature` files, and `behave` runs them by matching each step to a Python function. State travels in `context`, and Scenario Outlines handle data tables. Use it for business-readable acceptance tests, not for every unit test.
Hindi: BDD behaviour को `.feature` files में Given/When/Then scenarios के रूप में लिखता है और `behave` हर step को Python function से मिलाकर उन्हें चलाता है। State `context` में चलती है और Scenario Outlines data tables संभालते हैं। इसे business के पढ़ने लायक acceptance tests के लिए इस्तेमाल करें, हर unit test के लिए नहीं।

---

## ➡️ Next Topic
**291. Property-Based Testing (Hypothesis)** — let the library generate hundreds of inputs and shrink failures to the smallest example.
