# 138. CloudWatch Alarms
# AWS: CloudWatch Alarms
# Azure: Azure Monitor Alerts (metric/log alert rules + Action Groups)
# हिंदी में: मेट्रिक सीमा पार होने पर सूचना या ऑटो-एक्शन

---

## 🔵 Simple Definition
An alarm watches a metric and changes state (OK, ALARM, INSUFFICIENT_DATA) based on a threshold, triggering actions like SNS or Auto Scaling.
हिंदी: अलार्म मेट्रिक देखता है और थ्रेशोल्ड पार होने पर SNS या ऑटो-स्केलिंग जैसा एक्शन चलाता है।

---

## 🔴 Why it Exists
Humans cannot watch dashboards 24/7; problems should page you or self-heal.

---

## 🟢 How it Works
```
Metric --(Period x EvaluationPeriods vs Threshold)--> Alarm state
   OK -> ALARM  => action: SNS (email/Slack/PagerDuty), Auto Scaling, EC2 recover
Composite alarms combine several alarms (AND/OR) to cut noise
```

---

## 💻 Code / Config Example
```hcl
# Terraform (aws provider ~> 5.x) - ALB 5xx alarm to SNS
resource "aws_sns_topic" "alerts" { name = "alerts" }

resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "api-5xx"
  namespace           = "AWS/ApplicationELB"
  metric_name         = "HTTPCode_Target_5XX_Count"
  dimensions          = { LoadBalancer = var.alb_arn_suffix }
  statistic           = "Sum"
  period              = 60
  evaluation_periods  = 5
  datapoints_to_alarm = 3
  threshold           = 10
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | CloudWatch Alarm | Monitor Alert rule |
| Notification | SNS topic | Action Group |
| Composite | Composite alarm | Multi-condition / smart groups |
| Pricing | Per alarm/month (approximate - check current docs) | Per rule (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Alarm flaps on a single spike.
✅ Correct: Use datapoints_to_alarm (M out of N).

❌ Mistake: Alarm stuck on INSUFFICIENT_DATA.
✅ Correct: Set treat_missing_data deliberately.

---

## ⚫ Interview Q&A
Q1: [Easy] What are the alarm states?
A1: OK, ALARM, INSUFFICIENT_DATA.

Q2: [Medium] How does an alarm trigger scaling?
A2: A target tracking or step scaling policy uses the alarm to change desired capacity.

Q3: [Hard] Reduce alert fatigue?
A3: Composite alarms, M-of-N evaluation, anomaly detection, alert on symptoms (5xx, latency) not causes.

---

## ✅ Quick Checklist
□ Actions to SNS (subscription confirmed)
□ M-of-N set
□ Missing data handled

---

## ⚡ 1-Line Summary
Alarms turn metrics into notifications and actions | अलार्म मेट्रिक्स को सूचना और एक्शन में बदलते हैं।

## ➡️ Next: CloudWatch Dashboards
