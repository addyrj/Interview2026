# 65. RDS PARAMETER GROUPS
# AWS: RDS DB Parameter Groups (and Option Groups)
# Azure: Server parameters (Flexible Server)
# हिंदी में: RDS पैरामीटर ग्रुप यानी डेटाबेस कॉन्फ़िग

---

## 🔵 Simple Definition (2 lines)
A parameter group is the named set of engine settings (like postgresql.conf / my.cnf) you attach to RDS instances, since you cannot edit files on the server.
हिंदी: पैरामीटर ग्रुप इंजन सेटिंग्स का नामित सेट है, क्योंकि RDS में आप कॉन्फ़िग फ़ाइल सीधे नहीं बदल सकते।

---

## 🔴 Why it Exists (2 lines)
No SSH means no config file editing; settings like max_connections, slow query log or timezone must be changed another way.
Groups make config versionable and reusable across instances.

---

## 🟢 How it Works
```
Default group (read-only) -> create CUSTOM group -> change params -> attach to instance
Dynamic parameter : applies immediately
Static parameter  : status "pending-reboot" until you reboot
Family must match engine version (e.g. postgres16)
```

---

## 💻 Code / Config Example
```bash
# Custom Postgres parameter group (AWS CLI v2)
aws rds create-db-parameter-group \
  --db-parameter-group-name app-pg16 \
  --db-parameter-group-family postgres16 \
  --description "App tuned params"

aws rds modify-db-parameter-group \
  --db-parameter-group-name app-pg16 \
  --parameters "ParameterName=log_min_duration_statement,ParameterValue=500,ApplyMethod=immediate"

aws rds modify-db-instance \
  --db-instance-identifier app-pg \
  --db-parameter-group-name app-pg16 --apply-immediately
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Config unit | Parameter group (reusable) | Server parameters (per server) |
| Static changes | Need reboot | Some need restart |
| Reuse across DBs | Yes | No, set per server (use IaC) |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Trying to edit the default parameter group.
✅ Correct: Create a custom group and attach it.

❌ Mistake: Changing a static parameter and expecting it live.
✅ Correct: Check status; reboot in a maintenance window.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is a parameter group?
A1: A reusable collection of DB engine settings applied to RDS instances.

Q2: [Medium] Dynamic vs static parameters?
A2: Dynamic apply without reboot; static need a reboot to take effect.

Q3: [Hard] Upgrading Postgres 15 to 16, what happens to parameters?
A3: Parameter group family is version-specific, so create a new group for the new family, port settings, attach it during the upgrade.

---

## ✅ Quick Checklist
□ Custom group, not default
□ Slow query logging enabled
□ Group defined in IaC (Terraform/CloudFormation)

---

## ⚡ 1-Line Summary
Parameter groups are how you tune RDS since you have no config file. | RDS में कॉन्फ़िग फ़ाइल नहीं होती, इसलिए ट्यूनिंग पैरामीटर ग्रुप से होती है।

## ➡️ Next: RDS Security Groups

---
