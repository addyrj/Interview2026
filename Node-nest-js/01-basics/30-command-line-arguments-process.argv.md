# 30. Command Line Arguments (process.argv)
# हिंदी में: Command Line Arguments — process.argv

---

## 🔵 Simple Definition (English)
`process.argv` is an **array of strings** containing the command-line arguments passed when a Node.js script was launched from the terminal. The first two elements are always the Node executable path and the script path; everything after that is user-supplied arguments.

## 🔵 सरल परिभाषा (Hindi)
`process.argv` एक **strings का array** है जिसमें वो command-line arguments होते हैं जो Node.js script को terminal से launch करते समय दिए गए थे। पहले दो elements हमेशा Node executable का path और script का path होते हैं; उसके बाद जो भी है वो user-supplied arguments हैं।

---

## 🔴 Problem it Solves
CLI tools (build scripts, migration runners, data-import utilities, custom deployment scripts) need to accept input at runtime — which file to process, which environment to target, what flags to toggle (`--verbose`, `--dry-run`) — without hardcoding or prompting interactively every time. `process.argv` gives direct access to whatever the user typed after `node script.js`, enabling flexible, scriptable, automatable command-line tools.

## 🔴 यह क्यों बना? (Hindi)
CLI tools (build scripts, migration runners, data-import utilities, custom deployment scripts) को runtime पर input accept करना होता है — कौन सी file process करनी है, किस environment को target करना है, कौन से flags toggle करने हैं (`--verbose`, `--dry-run`) — बिना hardcode किए या हर बार interactively prompt किए। `process.argv` user ने `node script.js` के बाद जो भी type किया उसे direct access देता है, flexible, scriptable, automatable command-line tools बनाने में मदद करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Run `node script.js arg1 arg2 --flag=value`.
Step 2 → `process.argv` = `['/usr/local/bin/node', '/path/to/script.js', 'arg1', 'arg2', '--flag=value']`.
Step 3 → Index 0 is always the Node binary path; index 1 is always the script's absolute path — these are rarely useful for parsing user input.
Step 4 → `process.argv.slice(2)` gives just the user-supplied arguments: `['arg1', 'arg2', '--flag=value']`.
Step 5 → For simple positional args, access by index after slicing. For flags (`--name=value` or `--verbose`), you need to manually parse the strings (split on `=`, check for `--` prefix) OR use a library like `yargs`/`commander`/`minimist` for robust parsing (handles quoting, short flags `-v`, aliases, help text generation).
Step 6 → `process.argv0` additionally gives the raw value of `argv[0]` as originally passed by the OS (rarely different from `process.argv[0]`, but exists for edge cases).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Run करो `node script.js arg1 arg2 --flag=value`।
Step 2 → `process.argv` = `['/usr/local/bin/node', '/path/to/script.js', 'arg1', 'arg2', '--flag=value']`।
Step 3 → Index 0 हमेशा Node binary का path है; index 1 हमेशा script का absolute path है — ये parsing के लिए शायद ही useful होते हैं।
Step 4 → `process.argv.slice(2)` सिर्फ user-supplied arguments देता है: `['arg1', 'arg2', '--flag=value']`।
Step 5 → Simple positional args के लिए, slice करने के बाद index से access करो। Flags (`--name=value` या `--verbose`) के लिए, strings को manually parse करना पड़ता है (`=` पर split करो, `--` prefix check करो) या `yargs`/`commander`/`minimist` जैसी library use करो (quoting, short flags `-v`, aliases, help text generation handle करती है)।
Step 6 → `process.argv0` additionally `argv[0]` का raw value देता है जो OS ने originally pass किया था (शायद ही `process.argv[0]` से अलग हो, पर edge cases के लिए exist करता है)।

---

## 🟡 Real World Example
**Flipkart's internal data-migration CLI:** Engineers run `node migrate.js --table=orders --from=2023-01-01 --dry-run` to preview a database migration before actually executing it. The script parses `process.argv` to extract `table`, `from`, and the `dry-run` boolean flag, then conditionally either logs what WOULD change (`--dry-run` present) or actually runs the migration against production — a single script handling many different migration scenarios purely through CLI arguments, no code changes needed per migration.

## 🟡 Real Example Hindi mein
**Flipkart का internal data-migration CLI:** Engineers `node migrate.js --table=orders --from=2023-01-01 --dry-run` run करते हैं database migration को actually execute करने से पहले preview करने के लिए। Script `process.argv` parse करके `table`, `from`, और `dry-run` boolean flag निकालता है, फिर conditionally या तो log करता है क्या बदलता (`--dry-run` present) या actually production पर migration run करता है — एक ही script कई अलग migration scenarios handle करता है सिर्फ CLI arguments से, हर migration के लिए code changes नहीं चाहिए।

---

## 💻 Code Example — Basic

```javascript
// argvBasics.js — exploring process.argv
console.log('Full argv:', process.argv);
// run: node argvBasics.js hello world
// → [ '/usr/bin/node', '/path/to/argvBasics.js', 'hello', 'world' ]

// Skip the first two (node path, script path) to get real user arguments
const userArgs = process.argv.slice(2);
console.log('User arguments:', userArgs); // [ 'hello', 'world' ]

// Access positionally
const firstArg = userArgs[0];
const secondArg = userArgs[1];
console.log(`First: ${firstArg}, Second: ${secondArg}`);

// run: node argvBasics.js hello world
// Output: First: hello, Second: world
```

## 💻 Code Example — Advanced

```javascript
// cliTool.js — manual flag parsing (no external library), production pattern
function parseArgs(argv) {
  const args = argv.slice(2); // strip node path + script path
  const parsed = { _: [] }; // "_" holds positional (non-flag) arguments, like minimist does

  for (const arg of args) {
    if (arg.startsWith('--')) {
      // Long flag: --key=value OR --flag (boolean true)
      const [key, value] = arg.slice(2).split('='); // remove "--", split on "="
      parsed[key] = value !== undefined ? value : true; // if no "=value", treat as boolean true
    } else if (arg.startsWith('-')) {
      // Short flag: -v (treated as boolean true)
      parsed[arg.slice(1)] = true;
    } else {
      parsed._.push(arg); // positional argument
    }
  }
  return parsed;
}

const args = parseArgs(process.argv);
console.log(args);

// run: node cliTool.js migrate --table=orders --dry-run -v
// → { _: ['migrate'], table: 'orders', 'dry-run': true, v: true }

// Use the parsed values to drive behavior:
if (args._[0] === 'migrate') {
  console.log(`Migrating table: ${args.table}`);
  if (args['dry-run']) {
    console.log('[DRY RUN] No changes will be made.');
  } else {
    console.log('Running actual migration...');
  }
}

// -------------------------------------------------------

// Using a real library (recommended for production CLIs): yargs
// npm install yargs
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

const argv = yargs(hideBin(process.argv))
  .option('table', { type: 'string', demandOption: true, describe: 'Table to migrate' })
  .option('dry-run', { type: 'boolean', default: false, describe: 'Preview without executing' })
  .help() // auto-generates --help output
  .argv;

console.log(`Table: ${argv.table}, Dry run: ${argv.dryRun}`);
// run: node cliTool.js --table=orders --dry-run
```

---

## 🟠 Express.js Integration

```javascript
// server.js — using process.argv to control server startup behavior
// This is less common for Express apps (which usually use process.env instead),
// but useful for CLI-launched scripts like seeders, one-off migration runners, etc.

const express = require('express');

function parseArgs(argv) {
  const args = argv.slice(2);
  const parsed = {};
  for (const arg of args) {
    if (arg.startsWith('--')) {
      const [key, value] = arg.slice(2).split('=');
      parsed[key] = value !== undefined ? value : true;
    }
  }
  return parsed;
}

const args = parseArgs(process.argv);
const port = Number(args.port) || 3000; // allow: node server.js --port=4000
const seedData = args.seed === true;    // allow: node server.js --seed

const app = express();
app.get('/', (req, res) => res.send('Server is running'));

if (seedData) {
  console.log('Seeding database before starting server...');
  // runSeeder();
}

app.listen(port, () => console.log(`Server running on port ${port} (via CLI arg)`));

// run: node server.js --port=5000 --seed
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting to `slice(2)` and accidentally reading the Node/script path as "the first argument"
```javascript
// Wrong — index 0 is the Node binary, not user input!
const command = process.argv[0]; // '/usr/local/bin/node' — NOT what was intended

// Right — slice off the first two system-provided entries first
const command = process.argv.slice(2)[0]; // the actual first user-typed argument
```

❌ Mistake 2: Manually parsing flags without handling edge cases (quoted values, missing `=`, combined short flags)
```javascript
// Wrong — naive split breaks on values containing "=" themselves (e.g., --query=a=b)
const [key, value] = arg.slice(2).split('='); // "query=a=b" → value becomes just "a", loses "=b"

// Right — split only on the FIRST "=" using indexOf, or better, use a tested library
const eqIndex = arg.indexOf('=');
const key = arg.slice(2, eqIndex);
const value = arg.slice(eqIndex + 1); // "a=b" — preserves the full value
// OR simply: npm install yargs / commander / minimist for robust, battle-tested parsing
```

---

## 🧠 Tricky Interview Question

```javascript
// run: node app.js --name="John Doe" active

// app.js:
console.log(process.argv.length);
console.log(process.argv[2]);
console.log(process.argv[3]);
```
Answer: Prints **`4`**, **`--name=John Doe`**, **`active`**. The shell strips the quotes around `"John Doe"` before Node ever sees the argument — by the time `process.argv` is populated, the value is the single string `--name=John Doe` (with the space preserved INSIDE the string, no quotes). This confuses people who expect to see literal quote characters in `process.argv` — quoting is a SHELL-level concept for grouping words with spaces into one argument; Node only ever sees the final, already-split array of strings, never the raw quote characters themselves.

---

## ⚫ Interview Questions + Answers

Q1: What are the first two elements of `process.argv` always guaranteed to be?
A1: `process.argv[0]` is the absolute path to the Node.js executable that's running the script (e.g., `/usr/local/bin/node`). `process.argv[1]` is the absolute path to the script file being executed. Both are present regardless of how many (or how few) arguments the user supplies — which is why parsing logic almost always starts with `process.argv.slice(2)` to isolate just the user-provided arguments.

Q2: How would you support both `--flag=value` and `--flag value` (space-separated) syntax?
A2: `--flag=value` is easy to parse by splitting on `=`. `--flag value` (space-separated) requires look-ahead logic: when you encounter a flag with NO `=`, check if the NEXT array element doesn't itself start with `-`/`--`, and if so, treat it as that flag's value and skip it in the next iteration. This gets complex fast — which is exactly why most production CLIs reach for `yargs`, `commander`, or `minimist` rather than hand-rolling a parser, since these libraries already handle both syntaxes, short-flag combining (`-abc` = `-a -b -c`), and more.

Q3: Can you change what's in `process.argv` at runtime?
A3: Technically yes — `process.argv` is a regular mutable array, so you could push/splice/reassign elements. This is occasionally done in testing (mocking CLI input) or edge-case tooling, but it's unusual in normal application code since it doesn't reflect how the process was ACTUALLY launched and could confuse any other code reading it later expecting real launch arguments.

Q4: What's the difference between `process.argv` and `process.env` for passing configuration?
A4: `process.argv` carries ONE-TIME, per-invocation arguments explicitly typed on the command line when launching — good for CLI tools, scripts, one-off commands (`node migrate.js --table=orders`). `process.env` carries environment-level configuration set BEFORE the process starts, often persistent across many invocations/sessions (DB URLs, API keys, feature flags) — better suited for long-running servers where config shouldn't be retyped every launch. Many apps use BOTH: env vars for persistent config, argv for one-off overrides/commands.

Q5: Why do CLI tools often prefer a library like `yargs` over manually parsing `process.argv`?
A5: Manual parsing (as shown in the Advanced example) handles the simple cases but misses many real-world edge cases: short flag combining (`-abc`), flag aliases (`-v`/`--verbose`), type coercion with validation, auto-generated `--help`/usage text, required-flag enforcement with clear error messages, and nested sub-commands (`git commit -m "..."` style). Libraries like `yargs`, `commander`, and `minimist` have solved and tested all these edge cases, saving significant time and avoiding subtle parsing bugs in production CLI tools.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building CLI tools, migration scripts, build/deploy scripts, data-import utilities.
- Needing one-off, per-invocation overrides (`--dry-run`, `--verbose`, `--table=orders`).
- Writing quick automation/ops scripts that need flexible, scriptable input.

❌ Avoid when:
- Configuring long-running servers' persistent settings — prefer `process.env` for that (config shouldn't need retyping on every restart).
- Parsing complex flag grammars by hand — reach for `yargs`/`commander` instead of a custom parser past trivial cases.

---

## 📊 Visual Diagram
```
process.argv STRUCTURE:
──────────────────────────────────────────────────────────
  $ node /app/migrate.js --table=orders --dry-run seed

  process.argv:
    [0] "/usr/local/bin/node"   ← Node executable path (always present)
    [1] "/app/migrate.js"       ← script path (always present)
    [2] "--table=orders"        ← user arg #1
    [3] "--dry-run"             ← user arg #2
    [4] "seed"                  ← user arg #3 (positional)

  process.argv.slice(2):
    ["--table=orders", "--dry-run", "seed"]   ← only what the user typed

  After parsing (e.g. via yargs/minimist):
    { table: "orders", "dry-run": true, _: ["seed"] }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| process.argv | Array of CLI launch arguments | CLI launch arguments का array |
| slice(2) | Strips node path + script path | Node path और script path हटाना |
| Positional argument | Argument without a flag prefix | बिना flag prefix वाला argument |
| Flag/option | --key=value style input | --key=value जैसा input |
| yargs/commander/minimist | CLI argument parsing libraries | CLI arguments parse करने वाली libraries |

---

## ⚡ 3-Line Summary
English: `process.argv` is an array where index 0/1 are always the Node path and script path, and everything after (`slice(2)`) is user-supplied CLI input. Simple positional args can be read by index; flags (`--key=value`) need manual parsing or, better, a library like `yargs`/`commander` for production robustness. It's ideal for CLI tools and one-off scripts, while `process.env` suits persistent server configuration.
Hindi: `process.argv` एक array है जिसमें index 0/1 हमेशा Node path और script path होते हैं, और बाकी सब (`slice(2)`) user-supplied CLI input है। Simple positional args index से पढ़े जा सकते हैं; flags (`--key=value`) के लिए manual parsing या बेहतर, production robustness के लिए `yargs`/`commander` जैसी library चाहिए। यह CLI tools और one-off scripts के लिए ideal है, जबकि persistent server configuration के लिए `process.env` suited है।

---

## ➡️ Next Topic
**31. fs Module — File System** — reading, writing, and managing files using Node's built-in `fs` module.
