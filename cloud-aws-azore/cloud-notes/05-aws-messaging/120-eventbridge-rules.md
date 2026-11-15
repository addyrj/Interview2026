# 120. EventBridge Rules
# AWS: EventBridge rules (event patterns + schedules)
# Azure: Event Grid event subscriptions with advanced filters
# हिंदी में: Rule तय करता है कौन सा event किस target को जाएगा, या कब चलना है (schedule)

---

## 🔵 Simple Definition
A rule on a bus either matches events by a JSON event pattern or fires on a schedule (cron/rate), then invokes up to several targets.
Rule = "अगर event ऐसा दिखे तो ये target चलाओ" या "हर रात 2 बजे चलाओ"।

---

## 🔴 Why it Exists
Central, declarative routing replaces polling code and cron servers.

---

## 🟢 How it Works
```
Event {source, detail-type, detail{...}}
   -> Rule pattern: {"source":["shop.orders"],"detail":{"amount":[{"numeric":[">",500]}]}}
   -> match? yes -> Target(s) (+ optional InputTransformer, DLQ, retry)
Schedule rule: cron(0 2 * * ? *) (UTC, 6 fields)  or  rate(5 minutes)
```

---

## 💻 Code / Config Example
```yaml
# CloudFormation: route big orders to SQS; nightly cron to Lambda
Resources:
  BigOrderRule:
    Type: AWS::Events::Rule
    Properties:
      EventBusName: shop
      EventPattern:
        source: [shop.orders]
        detail-type: [OrderCreated]
        detail:
          amount:
            - numeric: [">", 500]
      Targets:
        - Id: bigOrderQueue
          Arn: !GetAtt BigOrderQueue.Arn
  NightlyRule:
    Type: AWS::Events::Rule
    Properties:
      ScheduleExpression: cron(0 2 * * ? *)
      Targets:
        - Id: cleanup
          Arn: !GetAtt CleanupFn.Arn
```
```bash
aws events put-rule --name nightly --schedule-expression "cron(0 2 * * ? *)"
aws events put-targets --rule nightly --targets "Id"="1","Arn"="arn:aws:lambda:ap-south-1:123456789012:function:cleanup"
```
Target also needs permission: SQS queue policy / `lambda add-permission` for events.amazonaws.com.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Pattern routing | Rule event pattern | Subscription advanced filters |
| Schedules | Schedule rules / Scheduler | Timer-trigger Functions / Logic Apps |
| Payload reshaping | Input transformer | Not built-in |
| Pricing | Rules free; pay per event (approximate - check docs) | Per operation |

---

## ⚠️ Common Mistakes
❌ Mistake: Rule created but target lacks resource permission.
✅ Correct: Grant events.amazonaws.com invoke/send permission.

❌ Mistake: Cron in local time.
✅ Correct: Cron is UTC; use EventBridge Scheduler for time zones.

---

## ⚫ Interview Q&A
Q1: [Easy] Two rule types?
A1: Event pattern rules and schedule rules.
Q2: [Medium] Cron format?
A2: Six fields, one of day-of-month/day-of-week must be `?`.
Q3: [Hard] Debug a rule that never fires?
A3: Check bus name, pattern vs actual event JSON (test-event-pattern), rule enabled, target permissions, CloudWatch metrics (FailedInvocations).

---

## ✅ Quick Checklist
□ Pattern tested with sample event
□ Target permissions set
□ DLQ on target

---

## ⚡ 1-Line Summary
Rules map event patterns or schedules to targets | Rules pattern या schedule को targets से जोड़ते हैं।

## ➡️ Next: 121. EventBridge + Lambda
