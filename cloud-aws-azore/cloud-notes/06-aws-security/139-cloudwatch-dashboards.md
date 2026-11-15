# 139. CloudWatch Dashboards
# AWS: CloudWatch Dashboards
# Azure: Azure Monitor Workbooks / Azure Dashboards
# हिंदी में: मेट्रिक्स और लॉग को एक स्क्रीन पर चार्ट के रूप में देखना

---

## 🔵 Simple Definition
Dashboards are customisable pages of widgets (graphs, numbers, logs) showing metrics and alarms across regions.
हिंदी: डैशबोर्ड विजेट्स वाला पेज है जो मेट्रिक्स, अलार्म और लॉग एक साथ दिखाता है।

---

## 🔴 Why it Exists
Teams need one shared view of health during releases and incidents.

---

## 🟢 How it Works
```
Dashboard (JSON body)
 widgets: metric graph | alarm status | log query | text
 Auto-refresh; cross-region and cross-account possible
 Defined as code via put-dashboard / CloudFormation / Terraform
```

---

## 💻 Code / Config Example
```json
{
  "widgets": [
    {
      "type": "metric", "x": 0, "y": 0, "width": 12, "height": 6,
      "properties": {
        "title": "ALB 5xx",
        "region": "ap-south-1",
        "stat": "Sum", "period": 60,
        "metrics": [["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", "app/api/abc123"]]
      }
    },
    {
      "type": "text", "x": 12, "y": 0, "width": 12, "height": 6,
      "properties": { "markdown": "## API service\nOn-call: see runbook" }
    }
  ]
}
```
```bash
# AWS CLI v2
aws cloudwatch put-dashboard --dashboard-name api-health --dashboard-body file://dash.json
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | CloudWatch Dashboards | Workbooks / Portal dashboards |
| As code | JSON body | ARM/Bicep |
| Third-party | Grafana (managed or self-host) | Managed Grafana |
| Pricing | Per dashboard/month beyond free tier (approximate - check current docs) | Mostly free (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Dashboards made by clicking only, lost on rebuild.
✅ Correct: Keep dashboard JSON in git and deploy with IaC.

❌ Mistake: Too many widgets with no focus.
✅ Correct: Show the golden signals: latency, traffic, errors, saturation.

---

## ⚫ Interview Q&A
Q1: [Easy] What is a dashboard widget?
A1: A single panel such as a graph, number or log query.

Q2: [Medium] Can a dashboard span regions?
A2: Yes, a widget specifies its own region; dashboards are global-view.

Q3: [Hard] CloudWatch dashboards or Grafana?
A3: CloudWatch is zero-setup for AWS metrics; Grafana suits multi-source (Prometheus, Loki, SQL) and richer visuals.

---

## ✅ Quick Checklist
□ Golden signals present
□ Dashboard in IaC
□ Alarm widgets included

---

## ⚡ 1-Line Summary
Dashboards = one-screen service health view | डैशबोर्ड सेवा की सेहत एक स्क्रीन पर दिखाता है।

## ➡️ Next: AWS Config
