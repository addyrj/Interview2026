# 36. EC2 User Data
# AWS: EC2 User Data (cloud-init)
# Azure: Custom Data / Custom Script Extension
# हिंदी में: सर्वर पहली बार चालू होते ही अपने-आप चलने वाली स्क्रिप्ट

---

## 🔵 Simple Definition
User data is a script or cloud-init config passed at launch; it runs once as root on first boot (by default) to configure the instance.
हिंदी: User data वह स्क्रिप्ट है जो इंस्टेंस के पहली बार बूट होने पर root से एक बार अपने-आप चलती है।

---

## 🔴 Why it Exists
Automate setup (install Docker, pull image, start app) so instances in an ASG configure themselves without manual SSH.

---

## 🟢 How it Works
```
RunInstances --user-data -> stored (max 16 KB, base64 in API)
First boot -> cloud-init reads from IMDS -> runs script as root
Logs: /var/log/cloud-init-output.log
Starts with #!/bin/bash  (or #cloud-config for YAML)
Runs only first boot unless configured otherwise.
```

---

## 💻 Code / Config Example
```bash
cat > userdata.sh <<'EOF'
#!/bin/bash
set -euxo pipefail
dnf install -y docker
systemctl enable --now docker
# Pull secrets at runtime, not baked into user data
DB_URL=$(aws ssm get-parameter --name /app/prod/DB_URL --with-decryption \
  --query Parameter.Value --output text)
docker run -d --restart=always -p 3000:3000 -e DATABASE_URL="$DB_URL" \
  123456789012.dkr.ecr.ap-south-1.amazonaws.com/api:latest
EOF
bash -n userdata.sh && echo syntax ok

aws ec2 run-instances --image-id ami-0123456789abcdef0 --instance-type t3.micro \
  --user-data file://userdata.sh --iam-instance-profile Name=api-profile
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Boot script | User data | Custom Data (cloud-init) |
| Post-boot script | SSM Run Command | Custom Script Extension |
| Size limit | 16 KB | Custom data limit approx 64 KB (check docs) |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Putting passwords in user data (readable via IMDS and console).
✅ Correct: Fetch secrets from SSM/Secrets Manager using the instance role.

❌ Mistake: Script fails silently.
✅ Correct: Use `set -euxo pipefail`, check `/var/log/cloud-init-output.log`.

---

## ⚫ Interview Q&A
Q1: [Easy] When does user data run?
A1: At first boot, as root, via cloud-init.

Q2: [Medium] Does it run on every reboot?
A2: Not by default; use the `#cloud-config` per-boot setting or systemd service.

Q3: [Hard] Why prefer baked AMI over heavy user data in ASGs?
A3: Faster scale-out, no dependency on external repos at boot, reproducible; user data only for small environment-specific bits.

---

## ✅ Quick Checklist
□ Script starts with shebang, `set -e`
□ No secrets inside
□ Logs checked on failure

---

## ⚡ 1-Line Summary
User data bootstraps an instance at first boot via cloud-init. | User data पहली बार बूट पर cloud-init से इंस्टेंस को अपने-आप कॉन्फ़िगर करता है।

## ➡️ Next: EC2 Auto Scaling
