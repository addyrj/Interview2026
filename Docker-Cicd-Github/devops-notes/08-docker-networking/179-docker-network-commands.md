# 179. Docker Network Commands
# हिंदी में: Docker Network Commands

---

## 🔵 Simple Definition (English)
The `docker network` command family lets you create, list, inspect, connect, disconnect and remove Docker networks: `create`, `ls`, `inspect`, `connect`, `disconnect`, `rm`, `prune`. These are the daily tools for building and debugging container connectivity.

## 🔵 सरल परिभाषा (Hindi)
`docker network` command family से तुम Docker networks बना, देख, inspect, connect, disconnect और हटा सकते हो: `create`, `ls`, `inspect`, `connect`, `disconnect`, `rm`, `prune`। Container connectivity बनाने और debug करने के रोज़ के औज़ार यही हैं।

---

## 🔴 Problem it Solves
Without knowing the commands, engineers guess when "API cannot reach DB" happens. The commands answer precisely: Which network is the container on? What IP? What subnet? Is DNS working? Who else is attached? They turn network mysteries into a 2-minute diagnosis.

## 🔴 यह क्यों बना? (Hindi)
Commands न आते हों तो "API DB तक नहीं पहुँच रहा" पर लोग अंदाज़े लगाते हैं। ये commands सटीक जवाब देते हैं: container किस network पर है? कौन सी IP? कौन सा subnet? DNS चल रहा है? और कौन जुड़ा है? इनसे network की पहेली 2 मिनट की जाँच बन जाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → docker network ls                    : see all networks (id, name, driver, scope)
Step 2 → docker network create NAME           : make a new network (bridge by default)
Step 3 → docker run --network NAME ...        : start a container directly on it
Step 4 → docker network connect NAME CTR      : attach a running container (live, no restart)
Step 5 → docker network inspect NAME          : see subnet, gateway, containers + IPs
Step 6 → docker network disconnect NAME CTR   : detach a container
Step 7 → docker network rm / prune            : delete (only if no container is attached)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → docker network ls                    : सारे networks देखो (id, name, driver, scope)
Step 2 → docker network create NAME           : नया network (default bridge)
Step 3 → docker run --network NAME ...        : container सीधे उस पर चलाओ
Step 4 → docker network connect NAME CTR      : चालू container जोड़ो (बिना restart)
Step 5 → docker network inspect NAME          : subnet, gateway, containers + IPs देखो
Step 6 → docker network disconnect NAME CTR   : container अलग करो
Step 7 → docker network rm / prune            : delete (जब कोई container जुड़ा न हो)
```

---

## 🟡 Real World Example
At 2 AM the checkout API cannot reach Redis after a deploy. The on-call engineer runs `docker network inspect shop_backend`, sees Redis is attached but the API container is not (a typo in the compose network name created a new network). He runs `docker network connect shop_backend shop-api-1` as a hotfix, service recovers in seconds, and the permanent fix goes into the Compose file next morning.

## 🟡 Real Example Hindi mein
रात 2 बजे deploy के बाद checkout API Redis तक नहीं पहुँच रहा। On-call engineer `docker network inspect shop_backend` चलाता है, देखता है Redis जुड़ा है पर API container नहीं (Compose में network नाम की typo से नया network बन गया)। वह hotfix के तौर पर `docker network connect shop_backend shop-api-1` चलाता है, service सेकंडों में ठीक हो जाती है और permanent fix अगली सुबह Compose file में जाता है।

---

## 💻 Code / Config Example — Basic
```bash
docker network ls                                  # list networks: bridge, host, none + yours
docker network ls --filter driver=bridge           # only bridge networks
docker network create appnet                       # create a user-defined bridge
docker network create --internal secure_net        # create a network with no external access
docker run -d --name db --network appnet \
  -e POSTGRES_PASSWORD=secret postgres:16-alpine   # container started on appnet
docker network connect appnet existing_container   # attach an already running container
docker network disconnect appnet existing_container # detach it again
docker network inspect appnet                      # full JSON: subnet, gateway, containers
docker network rm appnet                           # remove (fails if containers attached)
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# net-debug.sh - quick diagnosis when container A cannot reach container B
set -euo pipefail                                   # stop on first error

A="${1:?usage: net-debug.sh <from-container> <to-container> <port>}"   # source container
B="${2:?}"                                          # destination container name
PORT="${3:?}"                                       # destination port

echo "== networks of $A =="                         # which networks is A on?
docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{$v.IPAddress}}{{"\n"}}{{end}}' "$A"

echo "== networks of $B =="                         # which networks is B on?
docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{$v.IPAddress}}{{"\n"}}{{end}}' "$B"

echo "== DNS from $A =="                            # does Docker DNS resolve B?
docker exec "$A" getent hosts "$B" || echo "DNS FAIL (different network or wrong name)"

echo "== TCP test from $A =="                       # can A open the port?
docker exec "$A" sh -c "nc -zv -w3 $B $PORT" || echo "TCP FAIL (service down, firewall or wrong port)"

echo "== containers per network =="                 # who is attached where
for n in $(docker network ls --format '{{.Name}}'); do
  echo "-- $n"; docker network inspect -f '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{"\n"}}{{end}}' "$n"
done
```

```bash
# cleanup and capture helpers
docker network prune -f                              # remove ALL unused networks (safe, no data)
docker network prune --filter "until=24h" -f         # only unused ones older than 24h
docker run --rm --net container:api nicolaka/netshoot \
  ss -tulpn                                          # debug using api's network namespace (netshoot image)
```

---

## 🟠 My Stack Integration
- **Node.js API cannot reach Mongo:** run `docker network inspect <project>_default`, confirm both are listed, then `docker compose exec api getent hosts mongo`.
- **Nginx 502 Bad Gateway:** usually nginx and the upstream are on different networks, or the upstream container restarted with a new IP while nginx cached the old one. Fix with a resolver directive or `docker compose restart nginx`.
- **Compose project names:** networks are prefixed with the project name (`myapp_default`); use `docker network ls | grep myapp`.
- **VPS:** `ss -tulpn` on the host shows what is listening publicly; compare to what you intended.
- **CI:** create a throwaway network for integration tests and remove it in an `if: always()` step.

```yaml
# GitHub Actions snippet: isolated network for integration tests
- name: Create test network          # label in the UI
  run: docker network create ci-net  # throwaway bridge
- name: Run tests
  run: docker run --rm --network ci-net myorg/api-tests:latest   # example image
- name: Cleanup
  if: always()                       # even on failure
  run: docker network rm ci-net || true   # ignore if already gone
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `docker network rm` fails with "active endpoints" and the user keeps retrying.
✅ Correct: Run `docker network inspect` to see attached containers, disconnect or stop them first.

❌ Mistake 2: Forgetting that `connect` changes are not persisted in Compose; next `up` loses them.
✅ Correct: Treat `connect` as a hotfix and update the Compose file.

❌ Mistake 3: Running `docker network prune` and being surprised that it only removes unused networks (not default ones).
✅ Correct: That is correct and safe; default `bridge/host/none` are never removed.

❌ Mistake 4: Testing connectivity from the host instead of from inside the container.
✅ Correct: Use `docker exec <ctr> ...`; the host network view is different.

---

## 🧠 Tricky Interview Question
**Q:** `docker network inspect` shows both containers on the same network, and `getent hosts db` resolves, yet `nc -zv db 5432` times out. What do you check next?

**Answer:** DNS and network membership are fine, so the problem is at the service level: Postgres may still be starting or crashed (check `docker logs`), it may listen only on `127.0.0.1` inside its container (check `listen_addresses`), the port may differ, or a host firewall rule in `DOCKER-USER` blocks it. Network membership does not guarantee that the process accepts connections; healthchecks and `depends_on: condition: service_healthy` solve the startup race.

---

## ⚫ Interview Questions + Answers

Q1: How do you list the containers on a network?
A1: `docker network inspect <net>`; look at the `Containers` section.

Q2: Can you connect a running container to a network?
A2: Yes, `docker network connect <net> <container>`; no restart is needed.

Q3: What does `docker network prune` do?
A3: Deletes all networks with no containers attached (asks for confirmation unless `-f`).

Q4: How do you give a container a network alias?
A4: `docker network connect --alias backend <net> <ctr>` or `--network-alias` at `docker run`.

Q5: How to find a container's IP?
A5: `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <ctr>`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Debugging connectivity or DNS issues
- Hotfixing network membership in an incident
- Scripting test environments

❌ Avoid when:
- Managing permanent topology by hand; keep it in Compose files (infrastructure as code)

---

## 📊 Visual Diagram
```
  docker network create appnet ---> [ appnet ]
                                        ^   ^
        docker run --network appnet ----+   |
        docker network connect appnet ctr --+
                                        |
        docker network inspect appnet --+--> subnet, gateway, {ctr: IP}
        docker network disconnect ------> detach
        docker network rm / prune ------> delete (only if empty)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| inspect | Show detailed JSON | विस्तार से जानकारी |
| connect | Attach container to network | network से जोड़ना |
| disconnect | Detach container | अलग करना |
| prune | Delete unused networks | बेकार networks हटाना |
| alias | Extra DNS name | अतिरिक्त DNS नाम |
| netshoot | Debug toolbox image | debugging औज़ार वाली image |

---

## ⚡ 3-Line Summary
English: `docker network` has create, ls, inspect, connect, disconnect, rm and prune.
`inspect` plus `docker exec ... getent/nc` solves most connectivity problems.
Hotfix with `connect`, but keep the final topology in Compose.
Hindi: `docker network` में create, ls, inspect, connect, disconnect, rm और prune हैं।
`inspect` और `docker exec ... getent/nc` से ज़्यादातर connectivity problems हल होती हैं।
Hotfix `connect` से करो, पर final topology Compose में रखो।

---

## ➡️ Next Topic
**180. Service Discovery in Docker** - how containers find each other by name, and what happens when IPs change.
