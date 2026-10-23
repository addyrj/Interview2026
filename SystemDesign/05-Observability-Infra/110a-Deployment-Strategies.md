# 110a. Deployment Strategies
# हिंदी में: Deployment Strategies — नया code बिना downtime के production में कैसे पहुँचाएँ: Blue-Green, Canary, Rolling, Feature Flags, Strangler Fig — हर strategy कब इस्तेमाल करें, क्या खतरा है, कैसे rollback करें

---

## 🔵 Simple Definition (English)
A **deployment strategy** is the method you choose to release a new version of your application into production. The goal is to ship changes **safely, with minimal downtime, and with fast rollback** if something goes wrong.

## 🔵 सरल परिभाषा (Hindi)
Deployment strategy यह तय करती है कि नए code को production में कैसे पहुँचाएँ — बिना downtime के, अगर कुछ गलत हो तो जल्दी rollback के साथ।
जैसे एक दुकान में नया सामान रखते समय पुराना सामान एकदम नहीं हटाते, पहले थोड़ा-थोड़ा बदलते हैं।

---

## 🔴 Problem it Solves
Without a proper strategy:
- Deploy new version → users see errors → site down
- No way to test in production with real traffic
- Rollback takes hours (re-deploy old version manually)
- One bad deploy can affect all users at once

## 🔴 यह क्यों बना? (Hindi)
बिना strategy के एक ही बार में सब users को नया version मिल जाता है — अगर bug हो तो सबका system टूट जाता है। इसलिए strategies बनी जो धीरे-धीरे, safely deploy करती हैं।

---

## 🟢 How it Works — The 5 Strategies

---

### 1. Recreate Deployment (Simplest — avoid in production)

```
Old v1 → Kill all → Deploy v2
```

- Stop all old instances, start all new ones
- **Downtime:** YES (gap between kill and start)
- **Use only:** dev/staging, or non-critical batch jobs

---

### 2. Rolling Deployment ⭐⭐⭐⭐⭐

```
        v1  v1  v1  v1
              ↓
        v2  v1  v1  v1   ← replace one at a time
              ↓
        v2  v2  v1  v1
              ↓
        v2  v2  v2  v2   ← done
```

Replace old instances one by one (or in batches).

**Advantages:**
- Zero downtime
- Gradual rollout
- Simple to implement (AWS ECS, Kubernetes default)

**Disadvantages:**
- During rollout, v1 and v2 run simultaneously → both versions must be backward-compatible
- Rollback requires another rolling update (slow)
- Hard to control "how many users see v2"

**When to use:**
- Most standard web service updates
- API is backward-compatible

**AWS/Stack example:**
```
ECS Service
  → new task definition
  → minimum healthy percent: 100%
  → maximum percent: 200%
  → ECS replaces tasks one by one
```

---

### 3. Blue-Green Deployment ⭐⭐⭐⭐⭐

```
         Blue (v1 — LIVE)      Green (v2 — IDLE)
              │                      │
              ▼                      ▼
     ┌──────────────┐       ┌──────────────┐
     │  ECS v1      │       │  ECS v2      │
     └──────────────┘       └──────────────┘
              ↑
           ALB → Blue

After testing Green is ready:

     ┌──────────────┐       ┌──────────────┐
     │  ECS v1      │       │  ECS v2      │
     └──────────────┘       └──────────────┘
                                    ↑
                             ALB → Green (instant switch)
```

Two identical environments. Switch traffic instantly.

**Advantages:**
- Zero downtime (ALB switch = milliseconds)
- Instant rollback (switch ALB back to Blue)
- Can fully test Green before switching

**Disadvantages:**
- Double infrastructure cost during transition
- DB schema changes are tricky (both versions share DB)
- Stateful services (DB, cache) need careful handling

**When to use:**
- Major releases, risky changes
- When instant rollback is critical (payments, auth)

**Rollback:**
```
Problem detected on Green
   ↓
ALB → switch back to Blue
   ↓
< 1 minute rollback
```

---

### 4. Canary Deployment ⭐⭐⭐⭐⭐

```
           ALL users (100%)
                │
           Load Balancer
          /              \
        95%              5%
         ↓                ↓
       v1 (old)       v2 (canary)
```

Route a small percentage (1–5–10%) to the new version. Monitor. Gradually increase.

**Advantages:**
- Real production traffic tests the new version
- Bug affects only a small percentage of users
- Data-driven rollout decisions
- Easy rollback (route 0% to canary)

**Disadvantages:**
- Requires traffic-splitting infrastructure (ALB weighted rules, Nginx, Istio)
- Need good monitoring to detect canary issues
- Both versions run simultaneously (backward compatibility needed)

**Rollout sequence:**
```
1%  → monitor 30 min → metrics OK?
5%  → monitor 30 min → metrics OK?
20% → monitor 1 hour → metrics OK?
50% → monitor 1 hour → metrics OK?
100% → fully deployed
```

**My Stack Example (ECS + ALB):**
```
ALB Weighted Target Group:
  v1-target-group: weight 95
  v2-target-group: weight 5
```

**When to use:**
- Feature rollouts to real users
- When you want to A/B test with production traffic
- High-traffic services where a bug is very costly

---

### 5. Feature Flags (Feature Toggles) ⭐⭐⭐⭐⭐

```
Code is deployed (same version for all)
          ↓
Feature flag in config:
  new_checkout: enabled for user.group === "beta"
          ↓
Beta users see new checkout
Regular users see old checkout
```

The feature is in the code but controlled by a flag (config/DB/service).

**Advantages:**
- Deploy code without activating the feature
- Enable for specific users, groups, regions
- Instant rollback (flip flag off) — no re-deploy
- A/B testing, gradual rollout, kill switch

**Disadvantages:**
- Old flags must be cleaned up (tech debt)
- Complex logic if many flags interact
- Testing all flag combinations is hard

**Tools:**
```
LaunchDarkly
AWS AppConfig
Flagsmith (open source)
Simple: Redis key / DB row
```

**Node.js example:**
```js
const flags = await redis.hgetall('feature_flags');
if (flags.new_checkout === 'true' && user.isBeta) {
  return newCheckoutFlow();
}
return oldCheckoutFlow();
```

---

### 6. Strangler Fig Pattern ⭐⭐⭐⭐⭐ (Migration strategy)

Named after the strangler fig tree that grows around an existing tree and eventually replaces it.

```
         Before:
         ┌────────────────────┐
         │   Monolith v1      │
         │  (all features)    │
         └────────────────────┘

         During migration:
         ┌─────────────┐
         │  Monolith   │ ← handles old features
         └─────────────┘
         ┌─────────────┐
         │ New Service │ ← handles migrated feature
         └─────────────┘
         (Router/proxy sends traffic to correct one)

         After:
         ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
         │ User Svc    │  │ Order Svc   │  │ Payment Svc │
         └─────────────┘  └─────────────┘  └─────────────┘
         (Monolith fully replaced)
```

Used when migrating a large monolith to microservices — incrementally, not all at once.

**Process:**
1. New features → always built as new services
2. Old features → migrated one by one to new services
3. A reverse proxy routes to the right service
4. Monolith shrinks until it can be deleted

**Advantages:**
- Low risk (monolith always runs as fallback)
- Gradual — no big-bang rewrite
- Team learns microservices incrementally

**Disadvantages:**
- Running two systems increases complexity
- Routing logic must be maintained
- Takes months or years for large monoliths

**When to use:**
- Legacy monolith that needs modernization
- Team too small to rewrite everything at once
- Amazon, Netflix both used this pattern

---

## 🟢 कैसे काम करता है? (Hindi)
1. **Recreate:** सब पुराना बंद, सब नया शुरू — downtime होती है; सिर्फ़ dev/staging के लिए।
2. **Rolling:** एक-एक server पर नया version डालो — zero downtime, लेकिन rollback धीमा।
3. **Blue-Green:** दो environment, ALB switch से instant swap — rollback भी instant, लेकिन double cost।
4. **Canary:** 5% traffic को नया version दो, monitor करो, ठीक हो तो बढ़ाओ — production में real testing।
5. **Feature Flags:** code तो deploy हो गया, feature config से on/off करो — instant rollback, A/B testing।
6. **Strangler Fig:** monolith को धीरे-धीरे microservices में बदलो — proxy पुराने और नए के बीच route करता है।

---

## 🟡 Real World Example
- **Netflix:** Canary deployments with automatic rollback if error rate crosses threshold
- **Amazon:** Feature flags for every major change — "flag off" = instant rollback
- **Uber:** Strangler Fig to break their monolith (dispatch, payments extracted as services)
- **GitHub:** Blue-Green to deploy with zero downtime for millions of developers

## 🟡 Real Example Hindi में
Netflix अपना हर नया feature पहले 1% users को देता है, error rate देखता है — ठीक हो तो बढ़ाता है; Uber ने Strangler Fig से अपने monolith को धीरे-धीरे microservices में बदला; GitHub Blue-Green से deploy करता है ताकि developers को कोई downtime न हो।

---

## 🟠 My Stack Example (Node.js + ECS + ALB)

### Canary with ALB weighted target groups:
```
# AWS CLI — split 5% to v2
aws elbv2 modify-rule \
  --rule-arn $RULE_ARN \
  --actions '[
    {"Type":"forward","ForwardConfig":{"TargetGroups":[
      {"TargetGroupArn":"$TG_V1","Weight":95},
      {"TargetGroupArn":"$TG_V2","Weight":5}
    ]}}
  ]'
```

### Feature Flag in FastAPI:
```python
from redis import Redis

redis = Redis.from_url(os.getenv("REDIS_URL"))

def is_feature_enabled(feature: str, user_id: str) -> bool:
    flag = redis.hget("feature_flags", feature)
    if flag == b"all":
        return True
    if flag == b"off":
        return False
    # Check user-specific list
    return redis.sismember(f"flag:{feature}:users", user_id)
```

### GitHub Actions — Blue-Green deploy:
```yaml
- name: Deploy Green
  run: |
    aws ecs update-service \
      --cluster cashify-prod \
      --service cashify-green \
      --task-definition $NEW_TASK_DEF

- name: Wait for Green healthy
  run: aws ecs wait services-stable ...

- name: Switch ALB to Green
  run: aws elbv2 modify-listener ... # point to green TG

- name: Mark Blue as standby
  run: # scale blue to 0 (keep for rollback)
```

---

## ⚫ Interview Questions + Answers

**Q1: What deployment strategy would you choose for a payment service update?**
A1: Blue-Green — instant rollback is critical for payments. I'd deploy to Green, run smoke tests, then switch ALB. If any issue, switch back to Blue in under a minute. I'd also run both versions for 30 minutes before killing Blue.

**Q2: What is the difference between Canary and Blue-Green?**
A2: Blue-Green switches 100% of traffic at once (with instant rollback). Canary gradually routes a small percentage to the new version. Canary is better for feature validation with real users; Blue-Green is better for fast, safe full releases with instant rollback capability.

**Q3: When would you use Feature Flags over Canary?**
A3: Feature flags are better when you want to control rollout by user segment (beta users, specific region, paying customers) or when you need to test a feature without routing by percentage. Canary is better for infrastructure/backend changes where you test the code itself, not just a feature.

**Q4: What is the Strangler Fig pattern?**
A4: A migration strategy to decompose a monolith incrementally. New features go directly to new services; old features migrate one by one. A proxy routes traffic to the correct system. The monolith "shrinks" over time until it can be deleted — no big-bang rewrite needed.

**Q5: How do you handle database schema changes in Blue-Green deployments?**
A5: The DB is typically shared between Blue and Green. Schema changes must be backward-compatible — add columns with defaults, never drop columns until both versions are gone. Use expand-and-contract pattern: first expand (add new column), deploy both versions, then contract (remove old column after old version is gone).

---

## 🔷 Trade-offs

| Strategy | Downtime | Rollback speed | Cost | Complexity |
|---|---|---|---|---|
| Recreate | YES | Fast | Low | Low |
| Rolling | No | Slow | Low | Medium |
| Blue-Green | No | Instant | Double | Medium |
| Canary | No | Fast | Low extra | High |
| Feature Flag | No | Instant | Low | Medium |
| Strangler Fig | No | N/A (migration) | High (2 systems) | Very high |

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Blue-Green | Two identical envs, instant switch | दो environment, तुरंत बदलाव |
| Canary | Small % gets new version first | कुछ % users को पहले नया version |
| Feature Flag | Code deployed, feature toggled via config | code में feature, config से on/off |
| Strangler Fig | Incremental monolith → microservices | धीरे-धीरे monolith को बदलना |
| Rolling | Replace instances one by one | एक-एक server पर नया version |
| Rollback | Revert to previous version | पुराने version पर वापस जाना |

---

## ⚡ 3-Line Summary
**English:**
1. Rolling = gradual instance replacement, zero downtime, slow rollback. Blue-Green = two full environments, instant switch, double cost.
2. Canary = 1–5% real traffic to new version, monitor, then gradually expand — best for validating changes safely.
3. Feature Flags = deploy code but control activation per user/region; Strangler Fig = migrate a monolith to microservices incrementally without a big-bang rewrite.

**Hindi:**
1. Rolling = एक-एक server, zero downtime, rollback धीमा। Blue-Green = दो environment, instant switch, double cost।
2. Canary = 1–5% real traffic को नया version — monitor करो, ठीक हो तो बढ़ाओ।
3. Feature Flags = code deploy हो, feature user/region के हिसाब से on/off; Strangler Fig = monolith को धीरे-धीरे microservices में बदलो।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [ByteByteGo — CI/CD and Deployment Strategies](https://www.youtube.com/results?search_query=blue+green+canary+deployment+strategy+bytebytego) | Blue-green vs canary visuals, rollback mechanics |
| 📺 YouTube | [Tech World with Nana — Kubernetes Deployments](https://www.youtube.com/results?search_query=kubernetes+rolling+canary+deployment+strategy) | Rolling updates, canary in Kubernetes with Argo Rollouts |
| 📝 Article | [Martin Fowler — Blue Green Deployment](https://martinfowler.com/bliki/BlueGreenDeployment.html) | Original blue-green pattern definition |
| 📝 Article | [Martin Fowler — Canary Release](https://martinfowler.com/bliki/CanaryRelease.html) | Why canary, traffic splitting, feature flags combo |
| 🐙 GitHub | [argoproj/argo-rollouts](https://github.com/argoproj/argo-rollouts) | Kubernetes progressive delivery — canary + blue-green with real YAML |

---

## ➡️ Next Topic Suggestion
**105-Disaster-Recovery-RPO-RTO** — once deployed, what happens if the production system fails?
