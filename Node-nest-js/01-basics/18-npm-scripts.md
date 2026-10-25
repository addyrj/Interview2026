# 18. npm scripts
# हिंदी में: npm scripts

---

## 🔵 Simple Definition (English)
**npm scripts** are named shell commands defined in the `"scripts"` field of `package.json`, run via `npm run <name>` (or shorthand for `start`/`test`). They let a team standardize how to build, test, lint, and start a project without everyone needing to remember raw CLI commands.

## 🔵 सरल परिभाषा (Hindi)
**npm scripts** `package.json` के `"scripts"` field में defined named shell commands हैं, जो `npm run <name>` (या `start`/`test` के shorthand) से चलते हैं। यह team को build, test, lint, और project start करने का तरीका standardize करने देता है, बिना हर किसी को raw CLI commands याद रखने की ज़रूरत के।

---

## 🔴 Problem it Solves
Without npm scripts, every developer would need to remember and correctly type long, tool-specific commands (`node_modules/.bin/jest --coverage --watchAll=false`, `node_modules/.bin/eslint src/ --fix`), and these would differ project to project. npm scripts give every project a CONSISTENT, discoverable interface (`npm run build`, `npm test`) regardless of which underlying tools are used.

## 🔴 यह क्यों बना? (Hindi)
npm scripts के बिना हर developer को लंबे, tool-specific commands याद रखने और सही टाइप करने पड़ते (`node_modules/.bin/jest --coverage --watchAll=false`, `node_modules/.bin/eslint src/ --fix`), और यह project दर project अलग होते। npm scripts हर project को एक CONSISTENT, discoverable interface देते हैं (`npm run build`, `npm test`), चाहे नीचे कोई भी tools इस्तेमाल हों।

---

## 🟢 How it Works — Step by Step

Step 1 → Define named commands under `"scripts"` in `package.json`: `{"scripts": {"start": "node server.js", "test": "jest", "build": "webpack --mode production"}}`.
Step 2 → Run with `npm run <script-name>` — e.g., `npm run build`. Two scripts (`start`, `test`) get a shorthand: `npm start` and `npm test` (no `run` needed) for historical/convention reasons.
Step 3 → npm scripts automatically add `node_modules/.bin` to the `PATH` for that command's execution — so you can write `"lint": "eslint src/"` directly, without needing `./node_modules/.bin/eslint`.
Step 4 → **Pre/post hooks**: npm automatically runs `pre<name>` before and `post<name>` after a script of the same base name — e.g., `"pretest": "npm run lint"` runs automatically before `npm run test`, without you calling it explicitly.
Step 5 → Scripts can chain with `&&` (run sequentially, stop on failure) or `&` (run in parallel, rarely used alone — tools like `concurrently` or `npm-run-all` are preferred for true parallel script execution).
Step 6 → Environment variables can be set inline: `"start:prod": "NODE_ENV=production node server.js"` (Unix-style; use `cross-env` package for Windows compatibility).
Step 7 → `npm run` (no script name) lists ALL available scripts in the current project — useful for discovering what a new/unfamiliar project supports.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `package.json` के `"scripts"` में named commands define करें: `{"scripts": {"start": "node server.js", "test": "jest", "build": "webpack --mode production"}}`।
Step 2 → `npm run <script-name>` से चलाएं — जैसे `npm run build`। दो scripts (`start`, `test`) को shorthand मिलता है: `npm start` और `npm test` (बिना `run`), historical/convention कारणों से।
Step 3 → npm scripts automatically उस command के execution के लिए `node_modules/.bin` को `PATH` में जोड़ते हैं — इसलिए `"lint": "eslint src/"` सीधे लिख सकते हैं, `./node_modules/.bin/eslint` की ज़रूरत नहीं।
Step 4 → **Pre/post hooks**: npm automatically same base name के `pre<name>` को पहले और `post<name>` को बाद में चलाता है — जैसे `"pretest": "npm run lint"` automatically `npm run test` से पहले चलता है, explicitly call किए बिना।
Step 5 → Scripts `&&` (sequentially चलते हैं, failure पर रुक जाते हैं) या `&` (parallel, अकेले कम इस्तेमाल होता है — true parallel के लिए `concurrently` या `npm-run-all` tools बेहतर हैं) से chain हो सकते हैं।
Step 6 → Environment variables inline set हो सकते हैं: `"start:prod": "NODE_ENV=production node server.js"` (Unix-style; Windows compatibility के लिए `cross-env` package use करें)।
Step 7 → `npm run` (बिना script name) current project के सारे available scripts list करता है — किसी नए/अनजान project को समझने में मदद करता है।

---

## 🟡 Real World Example
**A Razorpay-style monorepo service:** `package.json` scripts might include `"dev": "nodemon src/server.js"` (local dev with auto-restart), `"build": "tsc"` (compile TypeScript), `"start": "node dist/server.js"` (run compiled production code), `"test": "jest --coverage"`, `"lint": "eslint src/ --fix"`, and `"pretest": "npm run lint"` (ensures code is linted before every test run). A new engineer joining the team just runs `npm run` to discover the entire development workflow instantly, without reading separate docs.

## 🟡 Real Example Hindi mein
**Razorpay-style monorepo service:** `package.json` scripts में हो सकता है `"dev": "nodemon src/server.js"` (local dev auto-restart के साथ), `"build": "tsc"` (TypeScript compile), `"start": "node dist/server.js"` (compiled production code चलाना), `"test": "jest --coverage"`, `"lint": "eslint src/ --fix"`, और `"pretest": "npm run lint"` (हर test run से पहले lint confirm करता है)। Team में नया engineer सिर्फ `npm run` चलाकर पूरा development workflow instantly discover कर लेता है, अलग docs पढ़े बिना।

---

## 💻 Code Example — Basic
```javascript
// npm-scripts-demo-server.js
// A simple server referenced by npm scripts below (run with: npm start)

const http = require('http');

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ message: 'Started via npm script', env: process.env.NODE_ENV }));
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server running on :${PORT}`));

/*
Corresponding package.json:
{
  "scripts": {
    "start": "node npm-scripts-demo-server.js",
    "start:dev": "NODE_ENV=development node npm-scripts-demo-server.js",
    "start:prod": "NODE_ENV=production PORT=8080 node npm-scripts-demo-server.js"
  }
}

Run:
  npm start           -> starts with no NODE_ENV set
  npm run start:dev   -> starts with NODE_ENV=development
  npm run start:prod  -> starts with NODE_ENV=production, PORT=8080
*/
```

## 💻 Code Example — Advanced
```javascript
// custom-script-runner.js
// A Node.js script showing how npm scripts pass arguments and env vars through,
// and how to build a small custom task runner (what many "scripts" ultimately call)

const { execSync } = require('child_process');

function runStep(name, command) {
  console.log(`\n=== Running: ${name} ===`);
  try {
    execSync(command, { stdio: 'inherit' }); // inherit so output streams live
    console.log(`=== ${name} succeeded ===`);
  } catch (err) {
    console.error(`=== ${name} FAILED ===`);
    process.exit(err.status || 1); // propagate failure to npm (stops chained scripts)
  }
}

// Simulates a "build" script running multiple sequential sub-steps,
// similar to how "pretest"/"test"/"posttest" hooks chain automatically
runStep('Lint', 'echo "Linting code..." && echo "No lint errors found"');
runStep('Type-check', 'echo "Type checking..." && echo "Types OK"');
runStep('Compile', 'echo "Compiling..." && echo "Build output written to dist/"');

console.log('\nAll build steps completed successfully.');

/*
package.json:
{
  "scripts": {
    "build": "node custom-script-runner.js"
  }
}
Usage: npm run build
Passing extra args to an npm script: npm run build -- --verbose
(everything after "--" is forwarded as process.argv to the underlying command)
*/
```

---

## 🟠 Express.js Integration
```javascript
// Express project's package.json scripts tailored for a real dev workflow
// server.js
const express = require('express');
const app = express();

app.get('/', (req, res) => res.json({ status: 'running', env: process.env.NODE_ENV }));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Express server on :${PORT} (${process.env.NODE_ENV})`));

/*
package.json excerpt:
{
  "scripts": {
    "dev": "cross-env NODE_ENV=development nodemon server.js",
    "start": "cross-env NODE_ENV=production node server.js",
    "lint": "eslint . --ext .js",
    "pretest": "npm run lint",
    "test": "jest --coverage",
    "posttest": "echo Tests and coverage complete"
  }
}

Workflow:
  npm run dev    -> auto-restarting dev server with NODE_ENV=development
  npm test       -> automatically runs lint FIRST (pretest), then jest, then posttest
  npm start      -> production start command, matches what a Dockerfile/PM2 would call
*/
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Hardcoding OS-specific syntax (breaks cross-platform teams)
```json
// Wrong — Unix-only env var syntax, fails on Windows cmd.exe
{ "scripts": { "start": "NODE_ENV=production node server.js" } }

// Correct — use cross-env for cross-platform environment variables
{ "scripts": { "start": "cross-env NODE_ENV=production node server.js" } }
```

❌ Mistake 2: Forgetting that `pre`/`post` hooks run automatically and duplicating the call
```json
// Wrong — lint runs TWICE: once from pretest, once because test ALSO calls it
{
  "scripts": {
    "pretest": "npm run lint",
    "test": "npm run lint && jest"
  }
}

// Correct — let the pretest hook handle it, keep "test" focused on its own job
{
  "scripts": {
    "pretest": "npm run lint",
    "test": "jest"
  }
}
```

---

## 🧠 Tricky Interview Question

```json
{
  "scripts": {
    "clean": "rm -rf dist",
    "build": "npm run clean && tsc",
    "prebuild": "echo 'Preparing build...'"
  }
}
```
**Q: Running `npm run build` — what is the FULL execution order?**
Answer: `prebuild` runs FIRST automatically (npm's hook convention: `pre<script>` always runs before `<script>`), printing "Preparing build...". THEN `build` itself runs, which explicitly calls `npm run clean` (deleting `dist`) before running `tsc`. So the order is: `prebuild` → `clean` (via build's own command) → `tsc` (via build's own command). Note there's no `postbuild` defined here, so nothing runs after. This hook-chaining behavior is a common interview trap because it's implicit, not visible in the `build` script's command string itself.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `npm start` and `npm run start`?
A1: They're functionally identical — `start` (along with `test`, `stop`, `restart`) is one of a few script names npm allows running WITHOUT the `run` keyword as a historical convenience/convention; all other custom script names require `npm run <name>`.

Q2: How do pre/post hooks work in npm scripts?
A2: For any script named `foo`, npm automatically runs a script named `prefoo` (if defined) immediately before, and `postfoo` (if defined) immediately after — without you needing to call them explicitly in `foo`'s own command.

Q3: How do you pass command-line arguments through an npm script to the underlying tool?
A3: Use `--` to separate npm's own arguments from the ones meant for the script: `npm run test -- --watch` passes `--watch` to whatever `test` actually runs (e.g., `jest --watch`).

Q4: Why does `node_modules/.bin` not need to be referenced explicitly inside scripts?
A4: npm automatically prepends `node_modules/.bin` (and parent directories' `.bin` folders, for monorepos) to the `PATH` environment variable when executing a script, so locally-installed CLI tools (`eslint`, `jest`, `webpack`) can be called by name directly.

Q5: What's a practical way to run multiple npm scripts in parallel (e.g., a frontend and backend dev server together)?
A5: Use a package like `concurrently` or `npm-run-all`: `"dev": "concurrently \"npm run dev:client\" \"npm run dev:server\""` — plain `&` works on Unix shells but isn't cross-platform reliable, and doesn't aggregate output/exit codes as cleanly.

---

## 🔷 When to Use + When Not to Use
✅ Use npm scripts when:
- Standardizing any repeatable project task (build, test, lint, start, migrate) so the whole team and CI use the same commands

❌ Avoid when:
- A task genuinely needs complex cross-platform logic, branching, or orchestration — at that point a dedicated Node.js script (called FROM an npm script) or a proper task runner is clearer than a long one-line shell command

---

## 📊 Visual Diagram
```
NPM SCRIPT EXECUTION FLOW (for `npm run test`)
──────────────────────────────────────────────
  package.json:
  {
    "scripts": {
      "pretest": "npm run lint",   ┐
      "test": "jest",               ├─ npm's implicit hook chain
      "posttest": "echo Done"       ┘
    }
  }

  npm run test
       │
       ▼
  1. pretest  -> runs "npm run lint" automatically
       │
       ▼
  2. test     -> runs "jest"
       │
       ▼
  3. posttest -> runs "echo Done" automatically

  (If step 1 or 2 fails/exits non-zero, the chain STOPS — later steps don't run)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| npm run | Command to execute a named script | Named script चलाने का command |
| pre/post hooks | Auto-run scripts before/after a same-named script | Same-named script से पहले/बाद auto-run होने वाले scripts |
| .bin PATH injection | Local CLI tools usable by name in scripts | Scripts में local CLI tools को name से use करना |
| cross-env | Package for cross-platform env vars in scripts | Scripts में cross-platform env vars के लिए package |
| concurrently | Tool to run multiple scripts in parallel | कई scripts parallel चलाने का tool |

---

## ⚡ 3-Line Summary
English:
1. npm scripts, defined under `"scripts"` in package.json, give every project a consistent, discoverable command interface (`npm run <name>`) regardless of underlying tools.
2. `pre`/`post` hooks auto-chain around same-named scripts, and locally-installed CLI tools work without a full path thanks to automatic `.bin` PATH injection.
3. Use `cross-env` for cross-platform environment variables and `concurrently`/`npm-run-all` for true parallel script execution.

Hindi:
1. npm scripts, `package.json` के `"scripts"` में defined, हर project को एक consistent, discoverable command interface (`npm run <name>`) देते हैं, नीचे के tools चाहे कोई भी हों।
2. `pre`/`post` hooks same-named scripts के चारों तरफ auto-chain होते हैं, और locally-installed CLI tools बिना full path के काम करते हैं automatic `.bin` PATH injection से।
3. Cross-platform environment variables के लिए `cross-env` और true parallel script execution के लिए `concurrently`/`npm-run-all` use करें।

---

## ➡️ Next Topic
**19. npx — What + Why** — Learn the companion tool for running CLI packages without installing them globally or even at all.
