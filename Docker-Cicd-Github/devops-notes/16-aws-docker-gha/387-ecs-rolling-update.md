# 387. ECS Rolling Update
# हिंदी में: ECS Rolling Update (धीरे-धीरे पुराने tasks बदलना)

---

## 🔵 Simple Definition (English)
A rolling update is ECS's default deployment: it starts tasks of the new task definition revision and stops old ones step by step, controlled by `minimumHealthyPercent` and `maximumPercent`, so the service keeps serving traffic during the release.

## 🔵 सरल परिभाषा (Hindi)
Rolling update ECS का default deployment है: यह नए task definition revision के tasks शुरू करता है और पुराने को step by step बंद करता है, `minimumHealthyPercent` और `maximumPercent` के नियंत्रण में, ताकि release के दौरान service traffic serve करती रहे।

---

## 🔴 Problem it Solves
- Stop-all-then-start-all causes downtime.
- Blue/green needs double infrastructure; for most APIs a gradual replacement is enough and cheaper.
- A bad release should stop spreading before it replaces every healthy task.

## 🔴 यह क्यों बना? (Hindi)
- सब बंद करके फिर सब शुरू करने से downtime होता है।
- Blue/green में दोगुना infrastructure लगता है; ज़्यादातर APIs के लिए धीरे-धीरे replace करना काफी और सस्ता है।
- खराब release सारे healthy tasks को replace करने से पहले रुक जाना चाहिए।

---

## 🟢 How it Works — Step by Step

```
Example: desired=4, minimumHealthy=100%, maximum=200%

Step 1 → Start: 4 old (rev 42)
Step 2 → ECS may run up to 8 tasks (200%), starts 4 new (rev 43)
Step 3 → New tasks pass ALB health check + grace period
Step 4 → ALB starts sending traffic to new tasks
Step 5 → Old tasks deregister (connection draining), receive SIGTERM, stop after stopTimeout
Step 6 → End: 4 new tasks; deployment COMPLETED
Failure → new tasks keep failing -> circuit breaker -> rollback to rev 42
```

## 🟢 कैसे काम करता है? (Hindi)
```
उदाहरण: desired=4, minimumHealthy=100%, maximum=200%

Step 1 → शुरुआत: 4 पुराने (rev 42)
Step 2 → ECS 8 tasks तक (200%) चला सकता है, 4 नए (rev 43) शुरू करता है
Step 3 → नए tasks ALB health check + grace period पास करते हैं
Step 4 → ALB नए tasks को traffic भेजना शुरू करता है
Step 5 → पुराने tasks deregister (connection draining), SIGTERM मिलता है, stopTimeout बाद बंद
Step 6 → अंत: 4 नए tasks; deployment COMPLETED
Failure → नए tasks बार-बार fail -> circuit breaker -> rev 42 पर rollback
```

---

## 🟡 Real World Example
During an IPL match, a ticketing API must never go down. The team releases a hotfix at the break: with minimum healthy 100% and maximum 200%, ECS brings up 8 new tasks next to 8 old ones, shifts traffic when they are healthy and retires the old ones. Customers see no errors. In another release, a missing env variable made new tasks crash at startup; the circuit breaker stopped the rollout after a few failed launches and returned to the old revision automatically.

## 🟡 Real Example Hindi mein
IPL match के दौरान ticketing API कभी बंद नहीं होनी चाहिए। Team break में hotfix release करती है: minimum healthy 100% और maximum 200% के साथ ECS 8 पुराने tasks के बगल में 8 नए चलाता है, healthy होने पर traffic शिफ्ट करता है और पुराने हटा देता है। Customers को कोई error नहीं दिखता। एक दूसरे release में env variable missing होने से नए tasks startup पर crash हुए; circuit breaker ने कुछ failed launches के बाद rollout रोककर अपने आप पुराने revision पर लौटा दिया।

---

## 💻 Code / Config Example — Basic

```bash
# rolling-basic.sh  - tune the rolling parameters on an existing service
set -euo pipefail                                              # stop on error
aws ecs update-service --cluster prod --service api \
  --task-definition api:43 \
  --deployment-configuration "minimumHealthyPercent=100,maximumPercent=200"   # no capacity loss, double during rollout
aws ecs wait services-stable --cluster prod --services api     # block until finished
aws ecs describe-services --cluster prod --services api \
  --query 'services[0].deployments[].{status:status,rollout:rolloutState,running:runningCount,desired:desiredCount,td:taskDefinition}'   # PRIMARY vs ACTIVE deployments
```

## 💻 Code / Config Example — Advanced
Service definition with circuit breaker, alarms rollback, graceful shutdown settings and ALB tuning (CloudFormation).

```yaml
# rolling-service.yml  - CloudFormation
AWSTemplateFormatVersion: "2010-09-09"             # template version
Parameters:
  TaskDefArn: {Type: String}                        # revision to run
  Subnets: {Type: "List<AWS::EC2::Subnet::Id>"}     # private subnets
  Sg: {Type: AWS::EC2::SecurityGroup::Id}           # task SG
  VpcId: {Type: AWS::EC2::VPC::Id}                  # VPC for the target group
Resources:
  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup  # ALB list of tasks
    Properties:
      VpcId: !Ref VpcId
      Port: 3000                                     # container port
      Protocol: HTTP
      TargetType: ip                                 # required for awsvpc/Fargate
      HealthCheckPath: /health                       # your app health route
      HealthCheckIntervalSeconds: 15                 # check often for fast rollouts
      HealthyThresholdCount: 2                       # 2 passes = healthy
      UnhealthyThresholdCount: 3                     # 3 fails = unhealthy
      TargetGroupAttributes:
        - {Key: deregistration_delay.timeout_seconds, Value: "30"}   # drain time for old tasks
  Service:
    Type: AWS::ECS::Service
    Properties:
      Cluster: prod
      ServiceName: api
      LaunchType: FARGATE
      TaskDefinition: !Ref TaskDefArn
      DesiredCount: 4
      DeploymentController: {Type: ECS}              # rolling update controller
      DeploymentConfiguration:
        MinimumHealthyPercent: 100                   # keep full capacity
        MaximumPercent: 200                          # allow surge
        DeploymentCircuitBreaker: {Enable: true, Rollback: true}   # auto rollback
        Alarms:
          Enable: true
          Rollback: true
          AlarmNames: [api-5xx-high]                 # CloudWatch alarm; rollback if it fires during deploy
      HealthCheckGracePeriodSeconds: 60              # allow boot time
      NetworkConfiguration:
        AwsvpcConfiguration: {Subnets: !Ref Subnets, SecurityGroups: [!Ref Sg], AssignPublicIp: DISABLED}
      LoadBalancers:
        - {ContainerName: api, ContainerPort: 3000, TargetGroupArn: !Ref TargetGroup}
```

---

## 🟠 My Stack Integration
Your Node.js and FastAPI apps must shut down gracefully, otherwise rolling updates drop requests. ECS sends SIGTERM, waits `stopTimeout` (max 120 s on Fargate), then SIGKILL.

```javascript
// server.js  - Node.js graceful shutdown for rolling updates
const http = require('http');                         // core http module
const server = http.createServer((req, res) => {      // minimal app
  if (req.url === '/health') {                        // health endpoint for ALB
    res.writeHead(200); return res.end('ok');         // 200 = healthy
  }
  res.writeHead(200); res.end('hello');               // normal response
});
server.listen(process.env.PORT || 3000);              // listen on all interfaces (default)

process.on('SIGTERM', () => {                         // ECS sends this to stop the task
  console.log('SIGTERM: draining');                   // log for debugging
  server.close(() => process.exit(0));                // stop accepting, finish in-flight, exit
  setTimeout(() => process.exit(1), 25000).unref();   // hard exit before stopTimeout (30 s)
});
```

For FastAPI use `uvicorn` (it handles SIGTERM gracefully; set `--timeout-graceful-shutdown` in recent versions, check your version). Use `CMD ["node", "server.js"]` (exec form) so Node is PID 1 and receives the signal; `npm start` swallows SIGTERM.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Dockerfile `CMD npm start` (shell form), so SIGTERM never reaches Node.
✅ Correct: `CMD ["node","server.js"]`, or use `init: true` / tini.

❌ Mistake 2: `minimumHealthyPercent: 0` in prod.
✅ Correct: 100 (or at least 50 with eyes open); 0 means downtime.

❌ Mistake 3: maximumPercent 100 with minimum 100. Then ECS can neither add nor remove, so the deploy stalls.
✅ Correct: Leave headroom (200) or reduce the minimum.

❌ Mistake 4: Health check depends on the database, so a DB blip kills every task at once.
✅ Correct: Keep the ALB health check shallow; separate deep readiness checks.

---

## 🧠 Tricky Interview Question
A deployment with 100/200 gets stuck at 4 old + 2 new tasks for 20 minutes with no errors. What could cause it?

Answer: Usually not enough resources for the surge: Fargate account vCPU quota reached, no free IPs in the subnets (awsvpc uses one IP per task), EC2 capacity short, or the new tasks are pending image pull/health failing slowly. Check service events, subnet free IPs and quotas.

---

## ⚫ Interview Questions + Answers

Q1: What do minimumHealthyPercent and maximumPercent mean?
A1: Minimum: lowest percentage of desiredCount that must be healthy/running during deploy. Maximum: upper bound of tasks (running+pending) as a percentage of desiredCount.

Q2: How does the circuit breaker decide to fail?
A2: If tasks repeatedly fail to reach steady state (threshold scales with desired count, minimum 3 and maximum 200 failures), the deployment is marked FAILED and rolled back if enabled.

Q3: Rolling vs blue/green?
A3: Rolling mixes versions in one fleet and is simple. Blue/green runs two fleets and shifts traffic atomically with fast rollback but costs more and is more complex.

Q4: Does rolling keep API compatibility problems away?
A4: No. During rollout, v1 and v2 run together, so DB migrations and APIs must be backward compatible.

Q5: What is the connection draining?
A5: ALB stops sending new requests to a deregistering task and waits `deregistration_delay` for in-flight requests to finish.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Stateless services with backward-compatible releases
- You want simple, cheap zero-downtime deploys

❌ Avoid when:
- You need instant, all-at-once cutover and quick rollback (blue/green)
- Breaking API or schema changes without compatibility steps

---

## 📊 Visual Diagram
```
 time ->
 old rev42: [A][B][C][D]  [A][B][C][D]  [ ][ ][C][D]  [ ][ ][ ][ ]
 new rev43:  .  .  .  .   [a][b][c][d]  [a][b][c][d]  [a][b][c][d]
            start        new healthy    old draining   done
 ALB:       -> old       -> both        -> mostly new  -> new
 fail path: new unhealthy x3 -> circuit breaker -> back to rev42
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Rolling update | Replace tasks gradually | धीरे-धीरे tasks बदलना |
| minimumHealthyPercent | Floor of healthy tasks | न्यूनतम healthy tasks का प्रतिशत |
| maximumPercent | Ceiling of total tasks | अधिकतम tasks का प्रतिशत |
| Circuit breaker | Auto-stop and rollback of failing deploy | खराब deploy का auto stop व rollback |
| Draining | Letting in-flight requests finish | चल रही requests पूरी होने देना |
| SIGTERM | Polite stop signal | शांति से रुकने का signal |

---

## ⚡ 3-Line Summary
English: Rolling update replaces tasks gradually within min/max percent limits.
Use 100/200 with a circuit breaker, correct health checks and graceful SIGTERM handling.
Versions overlap during the rollout, so releases must be backward compatible.

Hindi: Rolling update min/max percent की सीमा में tasks को धीरे-धीरे बदलता है।
Circuit breaker, सही health checks और graceful SIGTERM handling के साथ 100/200 रखो।
Rollout में versions एक साथ चलते हैं, इसलिए releases backward compatible होने चाहिए।

---

## ➡️ Next Topic
388. ECS Blue-Green Deploy: two parallel fleets with instant traffic switch and rollback.
