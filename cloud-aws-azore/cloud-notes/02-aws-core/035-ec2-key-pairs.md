# 35. EC2 Key Pairs
# AWS: EC2 Key Pairs
# Azure: SSH public key on VM (or Azure AD login / Bastion)
# हिंदी में: सर्वर में लॉगिन की SSH चाबी का जोड़ा

---

## 🔵 Simple Definition
A key pair is a public/private SSH key; AWS puts the public key on the instance and you keep the private key to log in.
हिंदी: Key pair में public और private key होती हैं; public key सर्वर पर रहती है और private key आपके पास।

---

## 🔴 Why it Exists
Passwords are guessable; key-based SSH is far stronger and works without sharing secrets.

---

## 🟢 How it Works
```
create-key-pair -> AWS stores PUBLIC key, returns PRIVATE .pem once
Launch with --key-name -> public key in ~/.ssh/authorized_keys of default user
ssh -i key.pem ec2-user@<ip>   (Amazon Linux: ec2-user, Ubuntu: ubuntu)
Private key must be chmod 400. Lost private key = cannot recover.
```

---

## 💻 Code / Config Example
```bash
# Create (ed25519 supported on Linux AMIs) and save safely
aws ec2 create-key-pair --key-name api-key --key-type ed25519 \
  --query KeyMaterial --output text > api-key.pem
chmod 400 api-key.pem

# Or import your own public key
aws ec2 import-key-pair --key-name my-laptop \
  --public-key-material fileb://~/.ssh/id_ed25519.pub

ssh -i api-key.pem ec2-user@203.0.113.25

# Better: no SSH port, no keys
aws ssm start-session --target i-0123456789abcdef0
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Key storage | Public key stored in EC2 key pairs | Public key stored on VM / SSH key resource |
| Keyless access | SSM Session Manager, EC2 Instance Connect | Azure Bastion, Entra ID SSH login |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Permission error "UNPROTECTED PRIVATE KEY FILE".
✅ Correct: `chmod 400 key.pem`.

❌ Mistake: Sharing one .pem across the team and committing it.
✅ Correct: Use SSM/Instance Connect with IAM, or per-user keys; add `*.pem` to `.gitignore`.

---

## ⚫ Interview Q&A
Q1: [Easy] What if you lose the private key?
A1: AWS cannot recover it. Attach a new key via user data, or mount the root volume on another instance, or use SSM.

Q2: [Medium] Can you change a key pair after launch?
A2: Not directly; edit `authorized_keys` through SSM or user data, or relaunch.

Q3: [Hard] How do you remove SSH keys at scale?
A3: Install SSM agent with an instance profile, close port 22, audit via CloudTrail/session logs, optionally enforce via SG policy and Config rules.

---

## ✅ Quick Checklist
□ .pem chmod 400, not in Git
□ Port 22 restricted or closed
□ SSM preferred

---

## ⚡ 1-Line Summary
Key pair = public key on the server, private key with you; prefer SSM. | Key pair में public key सर्वर पर और private key आपके पास होती है; SSM बेहतर विकल्प है।

## ➡️ Next: EC2 User Data
