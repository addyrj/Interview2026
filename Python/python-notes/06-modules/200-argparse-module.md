---

# 200. argparse Module
# हिंदी में: argparse Module (command-line arguments पढ़ना)

---

## 🔵 Simple Definition (English)
`argparse` is the standard-library module for building command-line tools. You declare which arguments and flags your script accepts, and `argparse` reads `sys.argv`, converts types, validates input, and creates `--help` automatically.

## 🔵 सरल परिभाषा (Hindi)
`argparse` command-line tools बनाने का standard-library module है। आप बताते हैं कि script कौन से arguments और flags लेगी, और `argparse` `sys.argv` पढ़ता है, types बदलता है, input validate करता है और `--help` अपने आप बनाता है।

---

## 🔴 Problem it Solves
Reading `sys.argv` by hand means manual index checks, manual `int()` conversion, no help text, and confusing crashes. Every DevOps script (migrations, seeding, deploy) needs flags like `--env prod --dry-run`. `argparse` gives a standard, user-friendly interface with clear error messages.

## 🔴 यह क्यों बना? (Hindi)
`sys.argv` हाथ से पढ़ने पर index check, `int()` conversion, help text और समझने लायक errors सब खुद लिखने पड़ते हैं। हर DevOps script (migration, seeding, deploy) को `--env prod --dry-run` जैसे flags चाहिए। `argparse` एक standard और user-friendly interface और साफ error messages देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → parser = argparse.ArgumentParser(prog=..., description=...)
Step 2 → parser.add_argument("name", ...)  positional (required)
Step 3 → parser.add_argument("--count", type=int, default=1)  optional flag
Step 4 → args = parser.parse_args()  reads sys.argv[1:] (or a list you pass)
Step 5 → Types converted, choices checked; on error -> message + exit code 2
Step 6 → Use args.name, args.count (a Namespace object)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → ArgumentParser बनाएँ
Step 2 → positional argument जोड़ें (ज़रूरी होता है)
Step 3 → optional flag जोड़ें (--count, type=int, default=1)
Step 4 → parse_args() sys.argv[1:] पढ़ता है (या आपकी दी हुई list)
Step 5 → type conversion और choices check; गलती पर error + exit code 2
Step 6 → args.name, args.count (Namespace object) इस्तेमाल करें
```

---

## 🟡 Real World Example
Swiggy's backend team runs `python manage.py migrate --target 0042 --dry-run` before every release. A Razorpay settlement script takes `--date 2026-01-31 --env prod`. An AI team has `python embed.py docs/ --model small --batch-size 64` to build a vector index. Git-like tools use subcommands (`tool migrate`, `tool seed`).

## 🟡 Real Example Hindi mein
Swiggy की backend team हर release से पहले `python manage.py migrate --target 0042 --dry-run` चलाती है। Razorpay की settlement script `--date 2026-01-31 --env prod` लेती है। AI team `python embed.py docs/ --model small --batch-size 64` से vector index बनाती है। Git जैसे tools में subcommands होते हैं (`tool migrate`, `tool seed`)।

---

## 💻 Code Example — Basic
```python
# Basic argparse - every line commented
import argparse  # standard library, nothing to install

parser: argparse.ArgumentParser = argparse.ArgumentParser(  # create the parser
    prog="greet", description="Greet people"  # name shown in help
)
parser.add_argument("name")  # positional: required, no dashes
parser.add_argument("-c", "--count", type=int, default=1)  # optional int flag
parser.add_argument("-v", "--verbose", action="store_true")  # flag: True if present

# We pass a list so the example runs without a real terminal.
# In a real script call parser.parse_args() with no argument.
args: argparse.Namespace = parser.parse_args(["Aditya", "-c", "3", "-v"])  # parse
print(args)  # the Namespace object
# Output: Namespace(name='Aditya', count=3, verbose=True)

print(args.name, args.count, args.verbose)  # attribute access
# Output: Aditya 3 True

print(parser.parse_args(["Bob"]))  # defaults are used for missing flags
# Output: Namespace(name='Bob', count=1, verbose=False)

print(vars(args))  # convert Namespace to a dict
# Output: {'name': 'Aditya', 'count': 3, 'verbose': True}

try:  # bad input stops the program with exit code 2
    parser.parse_args(["Bob", "--count", "abc"])  # "abc" is not an int
except SystemExit as exc:  # argparse calls sys.exit(2) after printing the error
    print("exit code:", exc.code)  # shows 2
# stderr: greet: error: argument -c/--count: invalid int value: 'abc'
# Output: exit code: 2
```

## 💻 Code Example — Advanced
```python
# Production style: subcommands, choices, lists, testable main()
import argparse  # CLI parsing
from pathlib import Path  # type=Path converts text to a Path
from typing import Optional, Sequence  # type hints


def build_parser() -> argparse.ArgumentParser:
    """Create the parser (separate function = easy to test)."""
    parser = argparse.ArgumentParser(prog="dbtool")  # top-level parser
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")  # --version
    sub = parser.add_subparsers(dest="command", required=True)  # subcommands

    migrate = sub.add_parser("migrate", help="run migrations")  # dbtool migrate
    migrate.add_argument("--target", default="head")  # which revision
    migrate.add_argument("--dry-run", action="store_true")  # dest becomes dry_run

    seed = sub.add_parser("seed", help="seed data")  # dbtool seed
    seed.add_argument("file", type=Path)  # positional converted to Path
    seed.add_argument("--env", choices=["dev", "staging", "prod"], default="dev")  # limited values
    seed.add_argument("--tag", action="append", default=[])  # repeat: --tag a --tag b
    seed.add_argument("--rows", type=int, nargs="+", default=[10])  # one or more ints
    return parser  # hand back the parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entry point; returns an exit code (0 = success)."""
    ns: argparse.Namespace = build_parser().parse_args(argv)  # None -> sys.argv
    if ns.command == "migrate":  # which subcommand ran
        print(f"migrate to {ns.target} dry={ns.dry_run}")  # act on it
    else:
        print(f"seed {ns.file} env={ns.env} tags={ns.tag} rows={ns.rows}")  # seed branch
    return 0  # success


if __name__ == "__main__":  # run only as a script
    raise SystemExit(main())  # pass the exit code to the shell

# Calls made for verification (argv given as lists):
main(["migrate", "--dry-run"])
# Output: migrate to head dry=True
main(["seed", "data.json", "--env", "prod", "--tag", "a", "--tag", "b", "--rows", "5", "6"])
# Output: seed data.json env=prod tags=['a', 'b'] rows=[5, 6]
try:
    main(["seed", "x", "--env", "qa"])  # not in choices
except SystemExit as exc:
    print("exit", exc.code)
# stderr: dbtool seed: error: argument --env: invalid choice: 'qa' (choose from dev, staging, prod)
# Output: exit 2
```
`choices` message format shown above is from Python 3.13; older versions quote choices differently. Verified on Python 3.13.3.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python way
import argparse
p = argparse.ArgumentParser()
p.add_argument("--port", type=int, default=8000)
p.add_argument("--debug", action="store_true")
args = p.parse_args()
print(args.port, args.debug)
```
```javascript
// JavaScript way (Node 18.3+ built-in)
import { parseArgs } from "node:util";
const { values } = parseArgs({
  options: {
    port: { type: "string", default: "8000" },   // no auto int conversion
    debug: { type: "boolean", default: false },
  },
});
console.log(Number(values.port), values.debug);
// Popular libraries: commander, yargs, minimist
```

Key differences: Python's `argparse` is built in with automatic `--help`, type conversion and subcommands. In Node you use `util.parseArgs` (basic) or a library such as `commander`/`yargs`. Python's argument `--dry-run` becomes `args.dry_run` (dash to underscore).

---

## 🟠 FastAPI Connection
FastAPI apps are started with `uvicorn`, which has its own CLI. For your own entry point (custom launcher, migration command, data-import job) you use `argparse`. Keep `build_parser()` and `main(argv)` separate so tests can call them without a terminal.

```python
# Custom launcher for a FastAPI app (pip install fastapi uvicorn)
import argparse  # CLI parsing
from typing import Sequence  # type hints
from fastapi import FastAPI  # the app
import uvicorn  # ASGI server

app: FastAPI = FastAPI()  # the application


@app.get("/health")  # simple health check
def health() -> dict[str, str]:
    return {"status": "ok"}  # JSON reply


def cli(argv: Sequence[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="serve")  # launcher parser
    p.add_argument("--host", default="127.0.0.1")  # bind address
    p.add_argument("--port", type=int, default=8000)  # port as int
    p.add_argument("--reload", action="store_true")  # dev auto-reload
    return p.parse_args(argv)  # parse


if __name__ == "__main__":  # python serve.py --port 9000
    ns = cli(__import__("sys").argv[1:])  # read terminal args
    uvicorn.run(app, host=ns.host, port=ns.port)  # start server
# cli(["--port", "9000"]) printed: Namespace(host='127.0.0.1', port=9000, reload=False)
# (Server start itself was not run here.)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `type=bool` for flags
✅ Correct:

```python
import argparse
# Wrong - bool("False") is True because any non-empty string is truthy:
p = argparse.ArgumentParser(); p.add_argument("--flag", type=bool, default=False)
print(p.parse_args(["--flag", "False"]).flag)   # True  (surprise!)
# Right - use store_true (or BooleanOptionalAction for --flag / --no-flag):
p = argparse.ArgumentParser(); p.add_argument("--flag", action="store_true")
```

❌ Mistake 2: Using `args.dry-run`
✅ Correct:

```python
# Wrong - SyntaxError, a dash is minus in Python:
# args.dry-run
# Right - dashes become underscores:
# args.dry_run
```

❌ Mistake 3: Mutable default plus wrong `action` for repeated flags
✅ Correct:

```python
# Wrong - second --tag overwrites the first (action defaults to "store"):
p.add_argument("--tag")
# Right - collect values in a list:
p.add_argument("--tag", action="append", default=[])
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import argparse
p = argparse.ArgumentParser()
p.add_argument("--flag", type=bool, default=False)
p.add_argument("-n", type=int)
p.add_argument("--x", type=int, default="7")
print(p.parse_args(["--flag", "False"]).flag)
print(p.parse_args([]))
print(repr(p.parse_args([]).x))
print(p.parse_known_args(["-n", "5", "--extra"]))
```

**Answer**:
```
True
Namespace(flag=False, n=None, x=7)
7
(Namespace(flag=False, n=5, x=7), ['--extra'])
```
`bool("False")` is `True`. A missing optional with no default is `None`. A string default is passed through `type`, so `"7"` becomes the int `7`. `parse_known_args` returns unknown arguments instead of failing.

---

## ⚫ Interview Questions + Answers

Q1: Positional vs optional arguments?
A1: Positional names have no dashes and are required (unless `nargs="?"`). Optional ones start with `-` or `--` and are not required unless `required=True`.

Q2: What does `action="store_true"` do?
A2: The option takes no value. It is `False` by default and becomes `True` when the flag appears.

Q3: How do you make subcommands like `git commit`?
A3: `parser.add_subparsers(dest="command")` then `add_parser("name")` for each, with their own arguments.

Q4: What exit code does `argparse` use on error?
A4: It prints usage to stderr and calls `sys.exit(2)`. `--help` exits with 0.

Q5: argparse vs click vs typer?
A5: `argparse` is built in and enough for scripts. `click` and `typer` (built on type hints, by the FastAPI author) give nicer decorators and are good for larger CLIs, but need installation.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Writing scripts with flags (migrate, seed, backup, import)
- You want no extra dependency
- You want automatic `--help` and validation

❌ Avoid when:
- A big CLI with many nested commands (consider `typer`/`click`)
- Configuration is better in env vars or a config file (12-factor apps)
- Inside the web request path (arguments come from the terminal, not HTTP)

---

## 📊 Visual Diagram

```
$ python dbtool.py seed data.json --env prod --tag a
                    |      |          |        |
                 command  positional  option   option
                    v
 ArgumentParser -> subparser "seed" -> Namespace(
     command='seed', file=Path('data.json'), env='prod', tag=['a'], rows=[10])
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Positional | Argument decided by its order | क्रम से पहचाना जाने वाला argument |
| Optional / flag | Starts with - or -- | - या -- से शुरू होने वाला option |
| Namespace | Object that holds parsed values | parsed values वाला object |
| Subparser | A subcommand with own arguments | अलग arguments वाला subcommand |
| nargs | How many values an option takes | option कितनी values लेता है |
| Exit code | Number returned to the shell | shell को लौटाया गया number |

---

## ⚡ 3-Line Summary
English: `argparse` turns `sys.argv` into validated, typed values with free `--help`. Use `add_argument`, `store_true`, `choices`, `nargs`, and `add_subparsers`. Put parsing in `build_parser()` and `main(argv)` so it is testable.
Hindi: `argparse` `sys.argv` को validated और typed values में बदलता है, `--help` मुफ़्त मिलता है। `add_argument`, `store_true`, `choices`, `nargs` और `add_subparsers` इस्तेमाल करें। Parsing को `build_parser()` और `main(argv)` में रखें ताकि test हो सके।

---

## ➡️ Next Topic
**201. File Handling Complete** is already written; continue with **202. open() Function** — the doorway to reading and writing files.
