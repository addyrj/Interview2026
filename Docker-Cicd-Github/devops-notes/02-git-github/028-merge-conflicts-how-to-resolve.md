---

# 28. Merge Conflicts — How to Resolve
# हिंदी में: Merge Conflicts — कैसे सुलझाएं

---

## 🔵 Simple Definition (English)
A **merge conflict** happens when Git cannot automatically combine changes because two branches edited the same lines (or one deleted a file the other edited). Git stops and marks the problem spots; a human decides the final content.

## 🔵 सरल परिभाषा (Hindi)
**Merge conflict** तब होता है जब Git दो branches के changes अपने-आप नहीं जोड़ पाता क्योंकि दोनों ने एक ही lines बदलीं (या एक ने file delete की और दूसरे ने edit)। Git रुक जाता है, problem जगहों पर markers लगाता है और final content इंसान तय करता है।

---

## 🔴 Problem it Solves
Git can merge different parts of a file automatically (3-way merge). But when meaning is ambiguous, guessing would silently lose someone's work. Conflict detection is a safety feature: it forces a human to choose, so no teammate's code is overwritten without notice.

## 🔴 यह क्यों बना? (Hindi)
अलग-अलग हिस्सों के changes Git अपने-आप merge कर लेता है (3-way merge)। लेकिन जहाँ मतलब साफ़ नहीं, वहाँ अंदाज़ा लगाने से किसी का काम चुपचाप खो सकता है। Conflict detection एक safety feature है: यह इंसान को चुनने पर मजबूर करता है ताकि बिना बताए किसी साथी का code overwrite न हो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → git merge feature (or git rebase main / git pull)
Step 2 → Git finds common ancestor, compares both sides
Step 3 → Same lines changed differently -> CONFLICT, merge pauses
Step 4 → git status lists "both modified" files; markers added in file:
            <<<<<<< HEAD        (your current branch)
            ...ours...
            =======
            ...theirs...
            >>>>>>> feature     (incoming branch)
Step 5 → Edit file: keep ours / theirs / combine; delete the markers
Step 6 → git add <file>   (marks as resolved)
Step 7 → git merge --continue  (or git rebase --continue) / git commit
Step 8 → Run tests! Then push.
Escape hatch → git merge --abort  /  git rebase --abort
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → merge/rebase/pull चलाओ
Step 2 → Git common ancestor ढूँढकर दोनों तरफ की तुलना करता है
Step 3 → एक ही lines अलग तरह बदली हों तो CONFLICT, merge रुक जाता है
Step 4 → git status में "both modified" दिखता है; file में markers होते हैं
         (<<<<<<< HEAD = आपकी branch, ======= = बीच, >>>>>>> = आने वाली branch)
Step 5 → file edit करो: ours / theirs / दोनों का मेल रखो; markers हटाओ
Step 6 → git add <file> से resolved mark करो
Step 7 → git merge --continue (या rebase --continue)
Step 8 → tests चलाओ, फिर push करो
बचाव → git merge --abort या git rebase --abort से पहले की हालत पर लौटो
```

---

## 🟡 Real World Example
Two developers on your Node.js API: Aman changes `package.json` (adds `express-rate-limit`) and Riya adds `zod`. Both edit the `dependencies` block, Git conflicts. Even worse: `package-lock.json` conflicts with 3000 lines. The right way: resolve `package.json` by keeping both lines, then **delete and regenerate** the lockfile: `git checkout --theirs package-lock.json && npm install` (or run `npm install` after resolving). Never hand-edit the lock file.
Another classic: two people edit `nginx.conf` on the same `location` block; the team resolves by keeping Riya's rate-limit and Aman's proxy header, then runs `nginx -t` before pushing.

## 🟡 Real Example Hindi mein
आपके Node.js API पर दो developers: Aman `package.json` में `express-rate-limit` जोड़ता है और Riya `zod`। दोनों ने `dependencies` block बदला, इसलिए conflict। उससे बुरा: `package-lock.json` में 3000 lines का conflict। सही तरीका: `package.json` में दोनों lines रखो, फिर lock file को **regenerate** करो: `npm install` चलाओ। Lock file हाथ से कभी edit मत करो।
एक और आम case: दो लोग `nginx.conf` के एक ही `location` block में बदलाव करते हैं; team Riya का rate-limit और Aman का proxy header दोनों रखती है और push से पहले `nginx -t` चलाती है।

---

## 💻 Code / Config Example — Basic

```bash
#!/usr/bin/env bash
# conflict-demo.sh - create a conflict on purpose and resolve it
set -uo pipefail                               # no -e: merge is expected to fail

rm -rf /tmp/conflict-demo && mkdir /tmp/conflict-demo && cd /tmp/conflict-demo  # sandbox
git init -q -b main                            # new repo, branch main
git config user.email "dev@example.com"        # local identity
git config user.name "Dev"                     # local name

echo 'PORT=3000' > .env.example                # base file
git add . && git commit -qm "base"             # base commit

git switch -q -c feature                       # branch 1
echo 'PORT=4000' > .env.example                # change same line
git commit -qam "feature: port 4000"           # commit on feature

git switch -q main                             # back to main
echo 'PORT=5000' > .env.example                # change SAME line differently
git commit -qam "main: port 5000"              # commit on main

git merge feature                              # CONFLICT happens here (exit code 1)
git status --short                             # shows: UU .env.example
cat .env.example                               # see the conflict markers

# resolve: decide final value is 4000
echo 'PORT=4000' > .env.example                # write final content, markers gone
grep -n '<<<<<<<\|>>>>>>>' .env.example || echo "no markers left"  # safety check
git add .env.example                           # mark resolved
git commit -qm "Merge feature, resolve port"   # finish the merge
git log --oneline --graph                      # verify result
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# resolve-helpers.sh - tools that make conflict handling faster and safer

# --- one-time config ---
git config --global rerere.enabled true          # reuse recorded resolutions (great for repeated rebases)
git config --global merge.conflictstyle zdiff3   # shows base version too (git >= 2.35; use diff3 on older)
git config --global merge.tool vimdiff           # or "code" etc; any installed mergetool
git config --global mergetool.keepBackup false   # no .orig files left behind

# --- during a conflict ---
git status                                       # list unmerged paths
git diff --name-only --diff-filter=U             # ONLY the conflicted files
git checkout --ours   -- path/file               # take our whole version (in rebase, "ours" = branch being rebased ONTO)
git checkout --theirs -- path/file               # take their whole version
git mergetool                                    # open visual tool one file at a time
git log --merge --oneline -p -- path/file        # commits from both sides touching this file

# --- strategy options for automated cases ---
git merge -X ours   feature                      # on conflicting hunks prefer ours (non-conflicting still merge)
git merge -X theirs feature                      # prefer theirs (use carefully!)

# --- block markers from ever being committed ---
git diff --check                                 # fails/warns if conflict markers or whitespace errors exist
git grep -nE '^(<<<<<<<|>>>>>>>) ' -- . ':!*.md' # find leftover markers in code files

# --- abort everything ---
git merge --abort                                # back to pre-merge state
git rebase --abort                               # back to pre-rebase state
```

---

## 🟠 My Stack Integration
In a Node.js/FastAPI/React repo most conflicts occur in: `package-lock.json`, `requirements.txt`, `docker-compose.yml`, `nginx.conf`, and `.github/workflows/*.yml`. Add a CI guard so leftover markers never reach your VPS/AWS deploy.

```yaml
# .github/workflows/conflict-markers.yml - fail PR if conflict markers are committed
name: No conflict markers                      # shows in PR checks
on:
  pull_request:                                # run on PRs
    branches: [main]                           # targeting main
jobs:
  markers:                                     # job id
    runs-on: ubuntu-latest                     # hosted runner
    steps:
      - uses: actions/checkout@v4              # example version; update as needed
      - name: Search for markers               # step label
        run: |                                 # multi-line shell
          if git grep -nE '^(<<<<<<<|=======|>>>>>>>)( |$)' -- ':!*.md' ':!*.rst'; then
            echo "Conflict markers found"      # explain the failure
            exit 1                             # fail the job
          fi
```
Security: a careless `-X theirs` or `--theirs` can silently drop a security fix or re-introduce a leaked secret. Always review the final diff (`git diff HEAD~1`) and keep branch protection requiring review.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Committing files that still contain `<<<<<<<` markers (app crashes, or worse, YAML breaks the deploy).
✅ Correct: Search for markers, run `git diff --check`, run tests and the build before `git commit`.

❌ Mistake 2: Blindly picking "accept mine" for everything to finish quickly.
✅ Correct: Read both sides; ask the author when unsure. Conflicts mean two intentions collided.

❌ Mistake 3: Hand-editing `package-lock.json` / `poetry.lock`.
✅ Correct: Resolve the manifest (`package.json`) and regenerate the lock with `npm install` / `poetry lock`.

❌ Mistake 4: Confusing ours/theirs during rebase (they are swapped).
✅ Correct: In rebase, "ours" is the branch you are rebasing onto (e.g. main), "theirs" is your own commit being replayed.

---

## 🧠 Tricky Interview Question
You resolved a conflict, tests pass, but after merge the production feature is missing a function that was there in both branches. How is that possible with no conflict markers?

Answer: This is a **semantic conflict**. Git merges text, not meaning. Branch A renamed `getUser()` to `fetchUser()` and branch B added a new call to `getUser()` in a different file. No overlapping lines, so no textual conflict, yet the code is broken. Prevention: run CI on the merge result (PR checks with `pull_request` event test the merge commit), enable "Require branches to be up to date", and use a merge queue.

---

## ⚫ Interview Questions + Answers

Q1: What are the three sections inside a conflict marker?
A1: `<<<<<<< HEAD` to `=======` is your current branch's version, `=======` to `>>>>>>> name` is the incoming branch's version. With diff3/zdiff3 style a `|||||||` base section is also shown.

Q2: How do you abort a conflicted merge?
A2: `git merge --abort` (or `git rebase --abort`, `git cherry-pick --abort`). It returns the working tree to its pre-operation state.

Q3: What is `git rerere`?
A3: "Reuse recorded resolution". Git remembers how you resolved a conflict and applies the same fix automatically when it sees the same conflict again, useful in repeated rebases.

Q4: Difference between `-X ours` and `-s ours`?
A4: `-X ours` is a merge option: only conflicting hunks prefer ours, other changes still merge. `-s ours` is a strategy: the result is exactly our tree, discarding everything from the other branch.

Q5: How to reduce conflicts in a team?
A5: Small short-lived branches, frequent rebase/merge from main, CODEOWNERS for ownership, formatters (Prettier/Black) so formatting does not collide, and avoid editing generated files by hand.

---

## 🔷 When to Use + When Not to Use
✅ Use (manual resolve) when:
- Both sides contain valuable changes in the same code
- Config files (nginx, compose, workflows) where order and combination matter

❌ Avoid (shortcut resolves like `-X theirs`) when:
- Security patches, migrations or lock files are involved
- You have not read what the other side changed

---

## 📊 Visual Diagram
```
        base (common ancestor)
        PORT=3000
         /            \
   main: PORT=5000   feature: PORT=4000
         \            /
          git merge feature
                |
     +----------------------------+
     | <<<<<<< HEAD               |
     | PORT=5000                  |
     | =======                    |
     | PORT=4000                  |
     | >>>>>>> feature            |
     +----------------------------+
                |  human edits, git add, git commit
                v
          PORT=4000 (resolved)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Conflict | Overlapping edits Git can't combine | टकराव वाले बदलाव |
| Conflict markers | `<<<<<<<`, `=======`, `>>>>>>>` lines | टकराव के निशान |
| 3-way merge | Compare two tips with common ancestor | तीन तरफ़ा तुलना |
| rerere | Remember and reuse resolutions | हल याद रखना |
| ours / theirs | The two sides (swapped in rebase) | हमारा / उनका पक्ष |
| Semantic conflict | Code merges cleanly but is logically broken | अर्थ का टकराव |

---

## ⚡ 3-Line Summary
English: Conflicts happen when two branches change the same lines; Git pauses and you choose the final text.
Remove markers, `git add`, then `--continue`; abort anytime if unsure.
Always run tests, because a clean merge can still be semantically broken.
Hindi: दो branches एक ही lines बदलें तो conflict होता है; Git रुकता है और आप final text चुनते हैं।
Markers हटाओ, `git add` करो, फिर `--continue`; शक हो तो कभी भी abort करो।
हमेशा tests चलाओ, क्योंकि clean merge भी logic में टूटा हो सकता है।

---

## ➡️ Next Topic
**29. Git Hooks**: automate checks (lint, tests, marker detection) on your machine before a commit or push even happens.

---
