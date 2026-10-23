---

# Q243. How Does Certificate-Based Device Auth Work?
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Explain how X.509 certificate-based authentication works for IoT devices. Walk through the full flow from device manufacturing to connecting to AWS IoT Core. How is it different from username/password auth?

---

## 💡 Quick Concept (2 lines only)
X.509 certs use asymmetric cryptography — device holds a private key, broker trusts a CA-signed certificate. During TLS handshake, device proves it owns the private key without ever sending it — unlike passwords which travel over the wire.
हिंदी: Certificate-based auth में device private key रखता है, जो कभी network पर नहीं जाती। TLS handshake में device prove करता है कि उसके पास वो key है।

---

## ✅ Answer / Solution

```
// ============================================
// STEP 1: Manufacturing — Certificate Generation
// ============================================

// Option A: Generate on device (most secure — private key never leaves device)
// Done during factory provisioning:

//  1. Device generates key pair on secure element:
//     Private key  → stored in hardware secure element (never extractable)
//     Public key   → sent to CA for signing

//  2. Certificate Signing Request (CSR):
openssl req -new -newkey rsa:2048 -nodes \
  -keyout device-001.key \
  -out device-001.csr \
  -subj "/CN=device-001/O=MyCompany/C=IN"

//  3. CA signs it → issues device certificate:
openssl x509 -req -in device-001.csr \
  -CA root-ca.crt -CAkey root-ca.key \
  -CAcreateserial -out device-001.crt \
  -days 3650 -sha256

// Certificate contains:
//  - Device ID (CN = device-001)
//  - Public key
//  - CA's signature
//  - Validity period (not before, not after)
//  - Serial number

// ============================================
// STEP 2: Provisioning — Install on Device
// ============================================

// Device receives (during factory or first boot):
//  ✓ device-001.crt  → device certificate (public)
//  ✓ root-ca.crt     → CA certificate (to verify broker)
//  ✗ device-001.key  → private key stays on device/secure element

// Store in device filesystem:
//  /certs/device.crt
//  /certs/root-ca.crt
//  /secure/device.key  ← protected, hardware-backed if possible

// ============================================
// STEP 3: TLS Mutual Authentication Handshake
// ============================================

/*
Device (Client)                    Broker (Server)
     │                                    │
     │──── ClientHello ──────────────────►│  "I support TLS 1.3, here's my random"
     │                                    │
     │◄─── ServerHello ───────────────────│  "OK, here's MY certificate"
     │◄─── ServerCertificate ─────────────│  broker's cert (device verifies with root-ca.crt)
     │◄─── CertificateRequest ────────────│  "Send ME your certificate too" (mutual TLS!)
     │                                    │
     │──── ClientCertificate ────────────►│  device.crt (broker verifies with root-ca.crt)
     │──── CertificateVerify ────────────►│  device signs data with private key
     │                                    │  (broker verifies with device's public key from cert)
     │◄─── Finished ──────────────────────│  "Auth complete, session keys established"
     │──── Finished ──────────────────────►│
     │                                    │
     │══════ Encrypted MQTT over TLS ════►│
     │   CONNECT { clientId: "device-001" }│
     │◄═══════════════════════════════════│
     │   CONNACK (rc: 0 = accepted)        │
*/

// ============================================
// STEP 4: Node.js — Connect with Certificate
// ============================================

const mqtt = require('mqtt');
const fs = require('fs');
const path = require('path');

const client = mqtt.connect('mqtts://a1234567890.iot.us-east-1.amazonaws.com:8883', {
  clientId: 'device-001',

  // ← These prove device identity
  key:  fs.readFileSync(path.join('/certs', 'device.key')),     // private key
  cert: fs.readFileSync(path.join('/certs', 'device.crt')),     // device certificate
  ca:   fs.readFileSync(path.join('/certs', 'root-ca.crt')),    // CA to verify broker

  // Protocol settings
  protocol: 'mqtts',
  rejectUnauthorized: true,  // ← ALWAYS true in production! Verifies broker cert

  // Connection settings
  keepalive: 60,
  reconnectPeriod: 5000,
  connectTimeout: 10000,
});

client.on('connect', () => {
  console.log('Connected with certificate auth — device authenticated ✅');
  // At this point:
  // ✓ Device verified broker's certificate (server auth)
  // ✓ Broker verified device's certificate (client auth = mTLS)
  // ✓ Session is encrypted end-to-end
});

client.on('error', (err) => {
  // Common errors:
  // ECONNREFUSED       → broker refused (cert invalid / not registered)
  // CERT_NOT_YET_VALID → clock wrong! Device needs NTP
  // CERT_EXPIRED       → rotate certificate
  // UNABLE_TO_VERIFY   → wrong CA certificate
  console.error('Connection error:', err.message);
});

// ============================================
// STEP 5: AWS IoT Core — Register + Authorize
// ============================================

// AWS IoT Certificate lifecycle:
// 1. Register cert in AWS IoT
aws iot register-certificate \
  --certificate-pem file://device-001.crt \
  --ca-certificate-pem file://root-ca.crt

// 2. Attach IoT Policy (defines what the device CAN do):
const devicePolicy = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "iot:Connect",
      "Resource": "arn:aws:iot:us-east-1:123456:client/device-001"
      // Only THIS specific device can connect with this cert!
    },
    {
      "Effect": "Allow",
      "Action": "iot:Publish",
      "Resource": "arn:aws:iot:us-east-1:123456:topic/devices/device-001/*"
      // Can only publish to ITS OWN topics
    },
    {
      "Effect": "Allow",
      "Action": "iot:Subscribe",
      "Resource": "arn:aws:iot:us-east-1:123456:topicfilter/devices/device-001/commands"
    }
  ]
};

// 3. Attach policy to certificate:
aws iot attach-policy \
  --policy-name device-001-policy \
  --target arn:aws:iot:us-east-1:123456:cert/abc123...

// 4. Attach certificate to Thing:
aws iot attach-thing-principal \
  --thing-name device-001 \
  --principal arn:aws:iot:us-east-1:123456:cert/abc123...

// ============================================
// COMPARISON: Certificate vs Password auth
// ============================================

/*
Feature               | Certificate (X.509) | Username/Password
──────────────────────┼─────────────────────┼──────────────────
Secret travels wire?  | NO (private key)     | YES (password)
Brute-forceable?      | No (2048-bit RSA)    | Yes
Phishable?            | No                   | Yes
Rotation complexity   | Medium (new cert)    | Easy (new pass)
Per-device identity   | Yes (unique cert)    | Depends
Revocation            | CRL / OCSP           | Delete from DB
Hardware binding      | Secure element       | Not possible
Used in production    | AWS IoT, Azure IoT   | Mosquitto, HiveMQ
*/
```

---

## 🔍 Why This Works (3 lines max)
The private key NEVER leaves the device — during TLS handshake, the device signs a challenge with its private key; the broker verifies the signature using the public key in the device certificate. Even if someone intercepts the network traffic, they only see the certificate (public info) and the signed challenge — they can't reconstruct the private key. This is why certificate-based auth is the gold standard for production IoT.
हिंदी: Private key कभी device से बाहर नहीं जाती। Device handshake में उससे data sign करता है, broker public key से verify करता है। Intercept करने से कुछ नहीं मिलता।

---

## ⚡ Alternative / Comparison

```
Certificate vs Token vs PSK:

X.509 Certificate (best):
  → Per-device identity, hardware bindable, industry standard
  → AWS IoT Core, Azure IoT Hub default method

JWT Token (good for dev):
  → Device generates JWT with device key → sends to auth server → gets short-lived token
  → Easier to rotate, but needs extra auth server

Pre-Shared Key (PSK):
  → Single secret shared between device and broker
  → Simpler setup, but if leaked = all devices compromised
  → Use only for development / prototype

Fleet provisioning (for mass production):
  → All devices ship with a CLAIM certificate (not final cert)
  → On first boot: device connects with claim cert, proves it's new
  → AWS IoT DPS issues a unique device certificate
  → Claim cert is invalidated for that device
  → Scalable for millions of devices
```

---

## ⚠️ Common Mistake

```
❌ Wrong: rejectUnauthorized: false in production
  const client = mqtt.connect('mqtts://broker', {
    rejectUnauthorized: false  // ← NEVER do this in production!
    // This disables broker certificate verification
    // Device connects to ANY server claiming to be the broker
    // Man-in-the-middle attack is trivially possible
  });

✅ Correct: Always verify broker cert
  const client = mqtt.connect('mqtts://broker', {
    ca: fs.readFileSync('/certs/root-ca.crt'),  // broker CA
    rejectUnauthorized: true,                   // verify broker cert!
  });

❌ Wrong: Storing private key in environment variable or config
  process.env.DEVICE_PRIVATE_KEY = '-----BEGIN RSA PRIVATE KEY...'
  // Readable by any process on the device, leaked in logs

✅ Correct: Store in file with restricted permissions (or hardware secure element)
  chmod 400 /certs/device.key  // only root can read
  // Best: use hardware TPM/secure element — private key never extractable
```

---

## 🎯 Interview Tip (1 line)
Say: "In production, I use mTLS — both device and broker present certificates; device identity is bound to the certificate's Common Name, and the IoT policy restricts it to only publish/subscribe to its own topic namespace — so even if a device is compromised, blast radius is contained."

---

## 🔗 Related Questions
→ Q122 (PSK vs certificate) | Q126 (TLS pinning) | Q133 (IoT PKI) | Q074 (MQTT over TLS code)
