# 75. CMD vs ENTRYPOINT — Difference
# हिंदी में: CMD और ENTRYPOINT में अंतर (तुलना और combination matrix)

---

## 🔵 Simple Definition (English)
`CMD` = default command or default arguments, replaced entirely by anything you type after the image name in `docker run`. `ENTRYPOINT` = the main executable that always runs; run arguments are appended to it, and only `--entrypoint` replaces it. This note is the side-by-side comparison for interviews.

## 🔵 सरल परिभाषा (Hindi)
`CMD` = default command या default arguments, जो `docker run` में image नाम के बाद लिखी किसी भी चीज़ से पूरी तरह बदल जाते हैं। `ENTRYPOINT` = मुख्य executable जो हमेशा चलता है; run arguments उसके पीछे जुड़ते हैं, और सिर्फ `--entrypoint` उसे बदलता है। यह note interview के लिए आमने-सामने की तुलना है।

---

## 🔴 Problem it Solves
Engineers constantly mix the two up, and the result is containers that ignore arguments, cannot be debugged (`docker run img sh` does nothing useful), or do not stop gracefully. Knowing the override rules lets you design images that are both safe by default and flexible for ops.

## 🔴 यह क्यों बना? (Hindi)
Engineers दोनों को अक्सर मिला देते हैं, जिससे containers arguments ignore करते हैं, debug नहीं हो पाते (`docker run img sh` काम का नहीं रहता), या gracefully बंद नहीं होते। Override rules जानने से ऐसी images बनती हैं जो default में सुरक्षित और ops के लिए flexible दोनों हों।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Final command = ENTRYPOINT array + CMD array (both in exec form)
Step 2 → docker run IMG args  -> CMD := args   (ENTRYPOINT unchanged)
Step 3 → docker run --entrypoint X IMG [args] -> ENTRYPOINT := X, image CMD discarded
Step 4 → Shell-form ENTRYPOINT ignores CMD and run args completely
Step 5 → Shell-form CMD only works when there is no ENTRYPOINT (becomes sh -c "cmd")
Step 6 → Check with: docker inspect --format '{{.Config.Entrypoint}} {{.Config.Cmd}}' IMG
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Final command = ENTRYPOINT array + CMD array (दोनों exec form में)
Step 2 → docker run IMG args  -> CMD := args   (ENTRYPOINT वही)
Step 3 → docker run --entrypoint X IMG [args] -> ENTRYPOINT := X, image का CMD हट जाता है
Step 4 → Shell-form ENTRYPOINT, CMD और run args को पूरी तरह ignore करता है
Step 5 → Shell-form CMD तभी चलता है जब ENTRYPOINT न हो (sh -c "cmd" बन जाता है)
Step 6 → जाँचने के लिए: docker inspect --format '{{.Config.Entrypoint}} {{.Config.Cmd}}' IMG
```

---

## 🟡 Real World Example
Two images in one company. The `web` image has only `CMD ["nginx","-g","daemon off;"]`: when an engineer runs `docker run web sh`, they get a shell to debug, which is exactly what they want. The `db-backup` image has `ENTRYPOINT ["/usr/local/bin/backup.sh"]` and `CMD ["--daily"]`: nightly cron runs it with defaults, while an admin runs `docker run db-backup --restore 2025-01-01`. The script is always the thing executed, so nobody accidentally runs the wrong binary.

## 🟡 Real Example Hindi mein
एक company की दो images। `web` image में सिर्फ `CMD ["nginx","-g","daemon off;"]` है: engineer `docker run web sh` चलाए तो debug के लिए shell मिल जाता है, जो वही चाहिए। `db-backup` image में `ENTRYPOINT ["/usr/local/bin/backup.sh"]` और `CMD ["--daily"]` है: रात का cron default से चलाता है, और admin `docker run db-backup --restore 2025-01-01` चलाता है। हर बार वही script चलती है, इसलिए गलत binary चलने का खतरा नहीं।

---

## 💻 Code / Config Example — Basic
```bash
# ---- Observe the override rules with a throwaway image ----
mkdir -p /tmp/cmdtest && cd /tmp/cmdtest           # temp folder for the demo
printf 'FROM alpine:3.20\nENTRYPOINT ["echo","hello"]\nCMD ["world"]\n' > Dockerfile   # create the demo Dockerfile
docker build -t cmdtest .                          # build the image
docker run --rm cmdtest                            # prints: hello world   (ENTRYPOINT + CMD)
docker run --rm cmdtest team                       # prints: hello team    (CMD replaced)
docker run --rm --entrypoint printf cmdtest '%s\n' bye   # prints: bye   (ENTRYPOINT replaced, CMD dropped)
docker inspect --format '{{.Config.Entrypoint}} {{.Config.Cmd}}' cmdtest   # shows [echo hello] [world]
```

## 💻 Code / Config Example — Advanced
Comparison matrix (what actually runs):

```
| Dockerfile                              | docker run img        | docker run img X Y        |
|-----------------------------------------|-----------------------|---------------------------|
| (none)                                  | base image default    | X Y                       |
| CMD ["a","b"]                           | a b                   | X Y                       |
| CMD a b            (shell form)         | /bin/sh -c "a b"      | X Y                       |
| ENTRYPOINT ["e"]                        | e                     | e X Y                     |
| ENTRYPOINT e       (shell form)         | /bin/sh -c "e"        | /bin/sh -c "e"  (X Y lost)|
| ENTRYPOINT ["e"] + CMD ["a"]            | e a                   | e X Y                     |
| ENTRYPOINT e (shell) + CMD ["a"]        | /bin/sh -c "e"        | /bin/sh -c "e"            |
| ENTRYPOINT ["e"] + CMD a (shell form)   | e /bin/sh -c a        | e X Y                     |
```
Production pattern combining both with a signal-safe wrapper:

```dockerfile
# Dockerfile -- Node.js API with tini as init, wrapper script, and overridable CMD
FROM node:20-alpine
# tini reaps zombies and forwards signals (apk package name: tini)
RUN apk add --no-cache tini
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
# Run as the built-in non-root "node" user of the official image
USER node
# tini is PID 1, the wrapper script is its child, "$@" exec replaces the script
ENTRYPOINT ["/sbin/tini", "--", "/app/docker-entrypoint.sh"]
# Default server command; "docker run img node scripts/migrate.js" replaces it
CMD ["node", "server.js"]
```
```sh
#!/bin/sh
# docker-entrypoint.sh -- fail fast on missing config, then hand over to the real process
set -e
# Refuse to start without a required secret passed at runtime
: "${JWT_SECRET:?JWT_SECRET must be set}"
# Replace this shell with the command (CMD or user override)
exec "$@"
```
Not built or run locally (no Docker). The matrix follows Docker's documented behaviour; verify with `docker inspect` on your version. Make `docker-entrypoint.sh` executable (`chmod +x`) before COPY.

---

## 🟠 My Stack Integration
Decide per service which one is the "contract" and which one is the "default".

```yaml
# docker-compose.yml -- override patterns in a Node + FastAPI + Nginx stack
services:                                       # services
  node-api:                                     # Node.js API
    image: ghcr.io/addyrj/node-api:1.2.0        # example image
    command: ["node", "dist/server.js"]         # overrides CMD only, entrypoint wrapper still runs
  migrate:                                      # one-off job using the same image
    image: ghcr.io/addyrj/node-api:1.2.0        # same image
    command: ["node", "scripts/migrate.js"]     # different CMD
    profiles: ["tools"]                         # run with: docker compose --profile tools run migrate
  fastapi:                                      # Python API
    image: ghcr.io/addyrj/fastapi:1.2.0         # example image
    entrypoint: []                              # clears ENTRYPOINT (and CMD) so command below is the full command
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0"]  # explicit full command
```
Rule of thumb for your VPS: web servers use CMD (easy `docker run img sh` debugging); CLI/job images use ENTRYPOINT.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting the whole command in ENTRYPOINT, so `docker run img sh` just passes `sh` as an argument to your app.
✅ Correct: Keep the main command in CMD, or know to use `--entrypoint sh`.

❌ Mistake 2: Mixing a shell-form ENTRYPOINT with CMD and expecting arguments to flow.
✅ Correct: Both in exec (JSON) form.

❌ Mistake 3: Expecting `docker run --entrypoint x img` to still apply the image CMD.
✅ Correct: Overriding entrypoint clears the image CMD; pass args explicitly.

❌ Mistake 4: Using Compose `entrypoint:` and being surprised the Dockerfile CMD stops applying.
✅ Correct: Also set `command:` when you override `entrypoint:`.

---

## 🧠 Tricky Interview Question
Image has `ENTRYPOINT ["python","app.py"]` only. You run `docker run img --debug`. What executes, and how do you get a shell for debugging?

Answer: `python app.py --debug` (run args append to ENTRYPOINT). For a shell: `docker run -it --entrypoint sh img`. If instead the image had `CMD ["python","app.py"]` only, `docker run -it img sh` would work directly, which is why web services usually prefer CMD.

---

## ⚫ Interview Questions + Answers

Q1: One-line difference?
A1: ENTRYPOINT = what to run (hard to override); CMD = default arguments/command (easy to override).

Q2: Which is overridden by `docker run img arg`?
A2: CMD. ENTRYPOINT stays and receives `arg`.

Q3: Which Kubernetes fields map to them?
A3: Pod `command` overrides ENTRYPOINT; Pod `args` overrides CMD.

Q4: Can you have multiple ENTRYPOINT lines?
A4: Only the last one is effective; same for CMD.

Q5: When prefer ENTRYPOINT + CMD together?
A5: When the binary is fixed and only parameters vary (CLI tools, backup jobs), or a wrapper script must always run before the app.

---

## 🔷 When to Use + When Not to Use
✅ Use ENTRYPOINT when:
- Image is a tool/CLI or needs mandatory init logic.
- You want a fixed contract for how the container starts.

✅ Use CMD when:
- Providing a default that ops often override (shell, alternate script).

❌ Avoid when:
- ENTRYPOINT used for services that need frequent debugging overrides.
- Shell form in production (signals not forwarded).

---

## 📊 Visual Diagram
```
                 +-----------------+------------------+
 Dockerfile:     |   ENTRYPOINT    |       CMD        |
                 |   (executable)  | (default args)   |
                 +-----------------+------------------+
 docker run img            ->  [ENTRYPOINT] [CMD]
 docker run img A B        ->  [ENTRYPOINT] [A B]        <- CMD replaced
 docker run --entrypoint Z img A  ->  [Z] [A]            <- both replaced
 Kubernetes:   command: -> ENTRYPOINT      args: -> CMD
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Override | Replace image default at run | Run पर default बदलना |
| Exec form | JSON array, direct exec | JSON array, सीधा चलना |
| Wrapper script | Entrypoint doing setup then exec | Setup करके exec करने वाली script |
| tini | Tiny init process | छोटा init process |
| Pod command/args | K8s names for ENTRYPOINT/CMD | K8s में नाम |
| Contract | Fixed behaviour of an image | Image का तय व्यवहार |

---

## ⚡ 3-Line Summary
English: CMD is replaceable defaults; ENTRYPOINT is the fixed executable and receives run arguments. Combine them as ENTRYPOINT [binary] + CMD [default args]. Always use exec form and `exec "$@"` in wrappers.
Hindi: CMD बदले जा सकने वाले defaults हैं; ENTRYPOINT fixed executable है जो run arguments लेता है। दोनों को ENTRYPOINT [binary] + CMD [default args] की तरह जोड़ो। हमेशा exec form और wrappers में `exec "$@"` रखो।

---

## ➡️ Next Topic
**76. COPY vs ADD** — Dockerfile में files image के अंदर कैसे पहुँचती हैं और ADD से क्यों बचना चाहिए।
