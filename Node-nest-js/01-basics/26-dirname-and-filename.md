# 26. __dirname + __filename
# हिंदी में: __dirname + __filename — Current File/Folder का Path

---

## 🔵 Simple Definition (English)
`__dirname` and `__filename` are special CommonJS module-level variables that give you the **absolute path** of the current file's folder (`__dirname`) and the current file itself (`__filename`). They're automatically injected by Node into every CJS module — no `require()` needed.

## 🔵 सरल परिभाषा (Hindi)
`__dirname` और `__filename` special CommonJS module-level variables हैं जो current file के folder का **absolute path** (`__dirname`) और current file का खुद का path (`__filename`) देते हैं। Node हर CJS module में इन्हें automatically inject करता है — कोई `require()` ज़रूरी नहीं।

---

## 🔴 Problem it Solves
Scripts are often run from different working directories (`cd /home/user && node app/server.js` vs `cd /home/user/app && node server.js`) — relative paths like `fs.readFileSync('./config.json')` resolve relative to `process.cwd()` (where the command was launched FROM), not where the file itself lives. This breaks file access when a script is invoked from an unexpected directory, run via cron, or required as a dependency from another project. `__dirname`/`__filename` solve this by always giving the TRUE location of the file itself, regardless of where the process was launched from.

## 🔴 यह क्यों बना? (Hindi)
Scripts अक्सर अलग-अलग working directories से run होते हैं (`cd /home/user && node app/server.js` या `cd /home/user/app && node server.js`) — relative paths जैसे `fs.readFileSync('./config.json')` `process.cwd()` के relative resolve होते हैं (जहाँ से command launch हुआ), file खुद जहाँ है वहाँ नहीं। इससे file access टूट जाता है जब script किसी अलग directory से invoke हो, cron से run हो, या किसी दूसरे project से dependency की तरह require हो। `__dirname`/`__filename` इसे solve करते हैं — हमेशा file की TRUE location देते हैं, process कहीं से भी launch हुआ हो।

---

## 🟢 How it Works — Step by Step

Step 1 → When Node loads a CJS module, it wraps the file in a function with 5 parameters: `(exports, require, module, __filename, __dirname)`.
Step 2 → `__filename` = the absolute, resolved path of the CURRENT file (e.g., `/home/user/app/routes/users.js`).
Step 3 → `__dirname` = `path.dirname(__filename)` — just the folder part (e.g., `/home/user/app/routes`).
Step 4 → Use them to build reliable paths: `path.join(__dirname, 'views', 'index.html')` always resolves relative to the FILE, never the shell's current directory.
Step 5 → In ES Modules, these don't exist — you must derive them from `import.meta.url` using `fileURLToPath()` and `path.dirname()`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Node जब CJS module load करता है, file को 5 parameters वाले function में wrap करता है: `(exports, require, module, __filename, __dirname)`।
Step 2 → `__filename` = CURRENT file का absolute, resolved path (जैसे `/home/user/app/routes/users.js`)।
Step 3 → `__dirname` = `path.dirname(__filename)` — सिर्फ folder part (जैसे `/home/user/app/routes`)।
Step 4 → इनसे reliable paths बनाओ: `path.join(__dirname, 'views', 'index.html')` हमेशा FILE के relative resolve होता है, shell की current directory के नहीं।
Step 5 → ES Modules में ये exist नहीं करते — `import.meta.url` से `fileURLToPath()` और `path.dirname()` का use करके derive करना पड़ता है।

---

## 🟡 Real World Example
**Zomato's restaurant-menu PDF generator service:** The service needs to load HTML templates and font files that live alongside the script (`./templates/menu.html`, `./fonts/brand.ttf`). Since this service is sometimes triggered by a cron job (running from `/`), sometimes by PM2 (running from `/var/app`), and sometimes locally by a developer — any hardcoded or `process.cwd()`-relative path would break in at least one of these contexts. Using `path.join(__dirname, 'templates', 'menu.html')` guarantees the correct file is found no matter how or from where the process was started.

## 🟡 Real Example Hindi mein
**Zomato का restaurant-menu PDF generator service:** इस service को script के साथ रहने वाली HTML templates और font files load करनी होती हैं (`./templates/menu.html`, `./fonts/brand.ttf`)। क्योंकि यह service कभी cron job से trigger होती है (`/` से run), कभी PM2 से (`/var/app` से run), और कभी developer local से — कोई भी hardcoded या `process.cwd()`-relative path इनमें से किसी एक context में टूट जाएगी। `path.join(__dirname, 'templates', 'menu.html')` use करने से हमेशा correct file मिलती है, process कहीं से भी शुरू हुआ हो।

---

## 💻 Code Example — Basic

```javascript
// info.js — demonstrates __dirname and __filename
console.log('__filename:', __filename);
// e.g. /Users/dev/project/info.js — full path to THIS file

console.log('__dirname:', __dirname);
// e.g. /Users/dev/project — folder containing THIS file

// Compare with process.cwd() — the shell's current working directory
console.log('process.cwd():', process.cwd());
// If you run `node info.js` from /Users/dev, cwd would be /Users/dev
// even though the file itself lives in /Users/dev/project (if run via a different path)

const path = require('path');

// Build a reliable path to a sibling file, regardless of cwd
const configPath = path.join(__dirname, 'config.json');
console.log('Reliable config path:', configPath);
```

## 💻 Code Example — Advanced

```javascript
// fileLoader.js — production pattern: loading static assets reliably
const fs = require('fs');
const path = require('path');

function loadTemplate(templateName) {
  // Always resolve relative to THIS file's directory, not cwd
  const templatePath = path.join(__dirname, 'templates', `${templateName}.html`);

  try {
    return fs.readFileSync(templatePath, 'utf8'); // read synchronously (startup-time load is OK)
  } catch (err) {
    if (err.code === 'ENOENT') {
      throw new Error(`Template not found: ${templatePath}`); // clear error with full resolved path
    }
    throw err; // re-throw unexpected errors
  }
}

module.exports = { loadTemplate };

// -------------------------------------------------------

// esmEquivalent.mjs — same pattern in ES Modules (no native __dirname/__filename)
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

// Manually derive __filename and __dirname from import.meta.url
const __filename = fileURLToPath(import.meta.url); // converts file:// URL to OS path
const __dirname = path.dirname(__filename);

function loadTemplateESM(templateName) {
  const templatePath = path.join(__dirname, 'templates', `${templateName}.html`);
  return fs.readFileSync(templatePath, 'utf8');
}

console.log(loadTemplateESM('menu')); // works identically to the CJS version
```

---

## 🟠 Express.js Integration

```javascript
// app.js — Express serving static files and views reliably via __dirname
const express = require('express');
const path = require('path');

const app = express();

// Serve a "public" folder that lives next to THIS file, no matter where
// the Node process was launched from (important for PM2, Docker, systemd)
app.use(express.static(path.join(__dirname, 'public')));

// Set the views directory for a template engine (e.g., EJS)
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

app.get('/invoice/:id', (req, res) => {
  // Always build file paths off __dirname — never trust process.cwd()
  const logoPath = path.join(__dirname, 'assets', 'logo.png');
  res.render('invoice', { id: req.params.id, logoPath });
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using relative paths directly with `fs` instead of `__dirname`
```javascript
// Wrong — breaks if the process is launched from a different directory
fs.readFileSync('./config.json');
// Works fine when run as `node server.js` from the project root,
// but FAILS if run as `node /app/server.js` from "/" (e.g., via systemd/cron)

// Right — always anchor to __dirname
fs.readFileSync(path.join(__dirname, 'config.json'));
```

❌ Mistake 2: Expecting `__dirname` to exist in ES Modules
```javascript
// Wrong — throws ReferenceError in a .mjs file or "type":"module" package
console.log(__dirname); // ReferenceError: __dirname is not defined

// Right — derive it from import.meta.url
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
```

---

## 🧠 Tricky Interview Question

```javascript
// /app/moduleA.js
console.log(__dirname);

// /app/sub/moduleB.js
require('../moduleA.js');

// run: node /app/sub/moduleB.js
```
Answer: Prints **`/app`** — NOT `/app/sub`. `__dirname` always reflects the directory of the file it's WRITTEN in, not the file that required it, and not the directory the process was launched from. Even though `moduleB.js` (in `/app/sub`) is the one doing the requiring, `moduleA.js`'s own `__dirname` is always `/app` because that's where `moduleA.js` physically lives. This trips people up when they assume `__dirname` is somehow "inherited" from the caller — it's not; it's purely per-file, baked in at module-wrap time.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `__dirname` and `process.cwd()`?
A1: `__dirname` is the absolute path of the folder containing the CURRENT FILE — fixed, based on the file's physical location on disk. `process.cwd()` is the directory from which the Node PROCESS was launched (the shell's current working directory when you ran `node ...`) — it can be anywhere and has nothing to do with where any particular file lives. They often coincide for simple scripts run from their own folder, but diverge in production (PM2, Docker, cron, systemd) or when files require each other across folders.

Q2: Why doesn't `__dirname` exist in ES Modules?
A2: `__dirname`/`__filename`/`require`/`module`/`exports` are all part of Node's CommonJS module wrapper function — they're injected as function parameters when Node wraps a CJS file. ES Modules follow the official ECMAScript module spec, which defines no such globals (for portability with browsers, which also don't have filesystem concepts like these). ESM instead exposes `import.meta.url`, a browser-compatible way to get the current module's URL, which Node-specific code converts to a filesystem path via `fileURLToPath()`.

Q3: How would you reliably load a JSON config file that sits next to your script, regardless of how the script is invoked?
A3: `const config = JSON.parse(fs.readFileSync(path.join(__dirname, 'config.json'), 'utf8'));` — anchoring to `__dirname` guarantees correctness whether the script runs via `node ./server.js`, `node /abs/path/server.js`, a symlinked binary, PM2, Docker `WORKDIR`, or a cron job with a different `cwd`. Never rely on bare relative paths with `fs` functions for files meant to travel with the script.

Q4: Does `__dirname` change if the file is required from a different location?
A4: No. `__dirname` is baked in per-file at the time Node wraps and loads that module — it always reflects where the file itself lives on disk, regardless of which other file `require()`d it or from where. See the Tricky Question above for a concrete demonstration.

Q5: How do you get `__dirname`-equivalent behavior inside an ESM file?
A5: ```js
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
```
This is now such a common boilerplate that some projects centralize it in a shared utility module, or rely on newer Node versions exposing `import.meta.dirname` and `import.meta.filename` directly (added in Node 20.11+/21.2+) as a built-in shortcut, removing the need for manual conversion.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Loading any file that lives alongside your script (templates, static assets, config, certs, migrations).
- Building CLI tools or libraries that may be invoked from any working directory.
- Writing Express `express.static()` or template engine `views` paths.

❌ Avoid when:
- You actually WANT a path relative to where the user launched the command (then `process.cwd()` is correct, e.g., CLI tools reading a user's project files in their current folder).
- Working in ESM without first deriving the equivalent via `import.meta.url` (plain `__dirname` will throw).

---

## 📊 Visual Diagram
```
__dirname vs process.cwd():
──────────────────────────────────────────────────────────

  Disk layout:
    /app/
      server.js        ← contains: console.log(__dirname)
      sub/
        helper.js

  Terminal:
    $ cd /home/user
    $ node /app/server.js

  Result:
    __dirname       = "/app"          ← where server.js FILE lives
    process.cwd()   = "/home/user"    ← where the COMMAND was run from

  __filename = "/app/server.js"       ← full path to the file itself
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| __dirname | Folder of current file (CJS) | Current file का folder path |
| __filename | Full path of current file (CJS) | Current file का पूरा path |
| process.cwd() | Shell's launch directory | Process शुरू होने की directory |
| import.meta.url | Current module URL (ESM) | ESM में module का URL |
| fileURLToPath | Converts file:// URL to OS path | URL को OS path में बदलना |
| path.join | Joins path segments safely | Paths को सुरक्षित तरीके से जोड़ना |

---

## ⚡ 3-Line Summary
English: `__dirname` and `__filename` are CJS-only globals giving the absolute location of the current file, independent of where the process was launched (`process.cwd()`). They're essential for reliably loading files that live alongside a script, especially in production environments like PM2, Docker, or cron. ES Modules have no such globals natively — derive the equivalent from `import.meta.url` via `fileURLToPath()`.
Hindi: `__dirname` और `__filename` CJS-only globals हैं जो current file की absolute location देते हैं, process कहीं से भी launch हुआ हो (`process.cwd()` से independent)। Script के साथ रहने वाली files को reliably load करने के लिए ज़रूरी हैं, especially PM2, Docker, cron जैसे production environments में। ES Modules में ये natively नहीं होते — `import.meta.url` से `fileURLToPath()` का use करके equivalent derive करो।

---

## ➡️ Next Topic
**27. process Object — Complete Guide** — everything the global `process` object exposes: env, argv, exit codes, signals, and more.
