# 04. TCP vs UDP
# हिंदी में: TCP — भरोसेमंद डिलीवरी (रजिस्टर्ड डाक); UDP — तेज़ पर बिना गारंटी (पोस्टकार्ड)

---

## 🔵 Simple Definition (English)
**TCP** (Transmission Control Protocol) and **UDP** (User Datagram Protocol) are the two main transport-layer protocols.
- **TCP** = connection-based, **reliable**, ordered delivery. Lost packets are re-sent. Used by HTTP/1.1, HTTP/2, databases, SSH.
- **UDP** = connectionless, **fast**, no guarantee of delivery or order. Used by video calls, live streaming, gaming, DNS, and HTTP/3 (QUIC).

## 🔵 सरल परिभाषा (Hindi)
TCP पहले कनेक्शन बनाता है, हर पैकेट पहुँचने की पुष्टि लेता है, खोया तो दोबारा भेजता है — धीमा पर भरोसेमंद।
UDP बिना कनेक्शन के सीधे पैकेट फेंक देता है — तेज़ है, पर कुछ पैकेट खो सकते हैं।

---

## 🔴 Problem it Solves
IP (Topic 1, 3) only moves packets from machine A to machine B, on a **best-effort** basis. Packets can be:
- **lost** (router overloaded),
- **duplicated**,
- **out of order** (took different routes),
- **corrupted**.

Applications need different things:
- A bank transfer / web page / DB query needs **every byte, in order** → TCP adds reliability on top of IP.
- A video call needs **low delay** more than perfection. A frame that arrives 1 second late is useless → UDP just sends, no waiting for re-sends.

## 🔴 यह क्यों बना? (Hindi)
IP सिर्फ़ "कोशिश" करता है पैकेट पहुँचाने की — पैकेट खो सकते हैं, उल्टे क्रम में आ सकते हैं।
बैंकिंग, वेबसाइट, डेटाबेस को हर बाइट सही क्रम में चाहिए → TCP। वीडियो कॉल को देरी नहीं चाहिए, थोड़ा डेटा खो जाए तो चलेगा → UDP।

---

## 🟢 How it Works — Step by Step

### TCP 3-Way Handshake (connection setup)

```
   Client                                   Server (port 443)
     │                                          │
     │ ─────── SYN (seq=100) ────────────────►  │  "I want to connect"
     │                                          │
     │ ◄────── SYN-ACK (seq=300, ack=101) ────  │  "OK, I'm ready too"
     │                                          │
     │ ─────── ACK (ack=301) ────────────────►  │  "Great, let's go"
     │                                          │
     │ ═══════ DATA flows both ways ═════════   │
     │                                          │
Cost: 1 full round trip (RTT) BEFORE any data is sent.
Mumbai ↔ Mumbai: ~5 ms.   Mumbai ↔ US: ~200 ms.  → This is why connection reuse matters.
```

### TCP reliability features

```
1. Sequence numbers  → receiver puts packets back in order
2. ACKs              → receiver confirms "I got up to byte X"
3. Retransmission    → no ACK within timeout → sender re-sends
4. Checksum          → detects corrupted data
5. Flow control      → receiver says "my buffer is full, slow down" (window size)
6. Congestion control→ sender slows down when network is overloaded (slow start, CUBIC, BBR)

Example of a lost packet:
  Sender: [1] [2] [3] [4]
  Network loses [3]
  Receiver: got 1,2,4 → keeps sending "ACK 3" (I still need 3)
  Sender: re-sends [3] → receiver now has 1,2,3,4 → delivers to app IN ORDER
```

### Head-of-Line (HOL) Blocking — TCP's weakness

```
Packets: [1][2][3][4][5]   → [2] is lost
Receiver has 3,4,5 but CANNOT give them to the app until 2 is re-sent.
Everything waits for one lost packet.  ← That's why video calls don't use TCP,
                                          and why HTTP/3 moved to QUIC (UDP).
```

### TCP connection close (4-way)

```
Client ── FIN ──► Server
Client ◄── ACK ── Server
Client ◄── FIN ── Server
Client ── ACK ──► Server   → client socket stays in TIME_WAIT for ~60s
(Too many short connections → thousands of TIME_WAIT sockets → use keep-alive)
```

### UDP — just send

```
   Client                         Server
     │ ──── datagram 1 ────────►    │
     │ ──── datagram 2 ────X        │   (lost — nobody re-sends)
     │ ──── datagram 3 ────────►    │
No handshake, no ACK, no order, no retransmit.
Header: only 8 bytes (TCP: 20–60 bytes).
If the app needs reliability, the APP builds it (like QUIC does).
```

### Side by side

```
┌────────────────────┬─────────────────────────┬─────────────────────────┐
│ Feature            │ TCP                     │ UDP                     │
├────────────────────┼─────────────────────────┼─────────────────────────┤
│ Connection         │ Yes (handshake)         │ No                      │
│ Reliable delivery  │ Yes (ACK + retransmit)  │ No                      │
│ Ordering           │ Yes                     │ No                      │
│ Speed / latency    │ Slower (overhead)       │ Faster                  │
│ Header size        │ 20–60 bytes             │ 8 bytes                 │
│ Flow/congestion    │ Yes                     │ No (app must handle)    │
│ Data model         │ Byte stream             │ Individual messages     │
│ Broadcast/multicast│ No                      │ Yes                     │
│ Used by            │ HTTP/1.1, HTTP/2, SSH,  │ DNS, WebRTC video/voice,│
│                    │ Postgres, MySQL, Redis, │ online gaming, QUIC/    │
│                    │ SMTP, WebSocket, Kafka  │ HTTP/3, VoIP, IoT CoAP  │
└────────────────────┴─────────────────────────┴─────────────────────────┘
```

### QUIC / HTTP/3 = best of both

```
QUIC runs on UDP but adds reliability itself, PER STREAM:
  - stream A loses a packet → only stream A waits; streams B, C continue (no HOL blocking)
  - handshake + TLS combined → 1 RTT (0-RTT for repeat visits)
  - connection survives network change (Wi-Fi → 4G) via connection ID, not IP:port
Used by: Google, YouTube, Facebook, Cloudflare. Great for mobile users.
```

## 🟢 कैसे काम करता है? (Hindi)
1. TCP: पहले 3-way handshake (SYN → SYN-ACK → ACK) से कनेक्शन बनता है।
2. हर पैकेट पर नंबर होता है; रिसीवर ACK भेजता है; ACK नहीं आया तो पैकेट दोबारा भेजा जाता है।
3. एक पैकेट खो जाए तो बाक़ी पैकेट भी रुक जाते हैं (Head-of-Line blocking)।
4. UDP: कोई handshake नहीं, कोई ACK नहीं — बस भेज दो। खोया तो खोया।
5. QUIC (HTTP/3) UDP के ऊपर अपनी reliability बनाता है — तेज़ भी, भरोसेमंद भी।

---

## 🟡 Real World Example

**WhatsApp / Google Meet video call — UDP (WebRTC)**
- If one video frame is lost, the call just shows the next frame. Re-sending an old frame would cause lag and echo. So WebRTC uses UDP (SRTP). Chat messages, however, go over TCP-like reliable connections, because a lost message is not acceptable.

**PUBG / BGMI — UDP**
- Your position is sent 20–60 times per second. If one update is lost, the next one replaces it. Waiting for a retransmit would make the game "laggy".

**Paytm / bank payment API — TCP (HTTPS)**
- Every byte of the payment request must arrive exactly. Losing a byte is unacceptable.

**YouTube on mobile — QUIC (UDP)**
- Google moved YouTube and Search to QUIC. Users on flaky Indian mobile networks get fewer stalls, because one lost packet doesn't block everything and the connection survives Wi-Fi → 4G switches.

## 🟡 Real Example Hindi में
WhatsApp वीडियो कॉल UDP पर चलती है — एक फ़्रेम खो जाए तो अगला दिख जाता है, पुराना दोबारा भेजने से कॉल अटक जाती।
Paytm का पेमेंट TCP (HTTPS) पर जाता है — वहाँ एक भी बाइट खोना मंज़ूर नहीं। YouTube मोबाइल पर QUIC (UDP) इस्तेमाल करता है ताकि नेटवर्क बदलने पर भी वीडियो न रुके।

---

## 🟠 My Stack Example

Almost everything in your stack is **TCP**:
```
Browser/RN app ──TCP 443──► Nginx ──TCP 3000──► Node.js ──TCP 5432──► PostgreSQL
                                                       └──TCP 6379──► Redis
                                                       └──TCP 27017─► MongoDB
```
So the main optimization is: **avoid paying the TCP (and TLS) handshake again and again.**

### 1. Keep-alive between Nginx and your app
```nginx
upstream api_backend {
  server api:3000;
  keepalive 64;                  # keep 64 idle TCP connections open to Node
}
server {
  listen 443 ssl;
  http2 on;                      # many requests over ONE TCP connection
  location / {
    proxy_pass http://api_backend;
    proxy_http_version 1.1;      # required for upstream keep-alive
    proxy_set_header Connection "";
  }
}
```

### 2. Connection pooling to the DB (TCP + auth handshake is expensive)
```js
// Node.js — pg Pool reuses TCP connections instead of opening one per query
import pg from 'pg';
const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL, max: 20 });
const { rows } = await pool.query('SELECT * FROM orders WHERE id = $1', [id]);
```
```python
# FastAPI + SQLAlchemy — same idea
engine = create_async_engine(DATABASE_URL, pool_size=20, max_overflow=10)
```

### 3. Enable HTTP/3 (QUIC over UDP) in Nginx (1.25+)
```nginx
server {
  listen 443 quic reuseport;     # UDP 443
  listen 443 ssl;                # TCP 443 fallback
  http2 on;
  add_header Alt-Svc 'h3=":443"; ma=86400';   # tell browsers HTTP/3 is available
}
# AWS: open UDP 443 in the Security Group too!
```
(Easiest way in practice: put Cloudflare or CloudFront in front — both give HTTP/3 with a checkbox.)

### 4. A tiny UDP example in Node (e.g. IoT sensor metrics, StatsD)
```js
import dgram from 'node:dgram';
const sock = dgram.createSocket('udp4');
// Fire-and-forget metric: if lost, no big deal
sock.send('api.requests:1|c', 8125, 'statsd.internal');
```

### 5. React Native — real-time features
- Chat, notifications, REST → TCP (HTTPS / WebSocket).
- Voice/video calls → `react-native-webrtc` (UDP under the hood), with a TURN server fallback (TCP 443) for strict corporate networks that block UDP.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between TCP and UDP? When would you pick each?**
A1: TCP is connection-oriented and reliable: it guarantees delivery and order, and has flow and congestion control, at the cost of extra latency and overhead. UDP is connectionless with no guarantees, but it's fast and lightweight. Pick TCP when correctness matters (APIs, payments, DB, file transfer). Pick UDP when low latency matters and a little loss is OK (voice/video, gaming, live streaming, DNS, metrics), or when you build your own reliability (QUIC).

**Q2: Explain the TCP three-way handshake. Why three steps and not two?**
A2: SYN → SYN-ACK → ACK. Each side must announce its initial sequence number and confirm the other's. With two steps, the server would never know whether the client received its sequence number. Old duplicate SYNs could also create ghost connections. Three steps is the minimum for both sides to agree.

**Q3: What is head-of-line blocking? How does HTTP/3 fix it?**
A3: In TCP, data is a single ordered stream, so if one packet is lost, all later packets wait in the buffer until it's retransmitted, even if they belong to unrelated HTTP requests multiplexed over HTTP/2. HTTP/3 uses QUIC over UDP, where each stream has independent ordering. A loss on one stream doesn't block the others. QUIC also merges the transport and TLS handshakes (1-RTT, 0-RTT on resume) and supports connection migration.

**Q4: Why does DNS use UDP?**
A4: Queries and answers are small and a single request/response is enough. A TCP handshake would triple the latency for no benefit. If the answer is too large or truncated, the client retries over TCP. Zone transfers also use TCP.

**Q5: Your API latency is high only for the first request from mobile clients. Why, and how do you fix it?**
A5: The first request pays for DNS lookup + TCP handshake (1 RTT) + TLS handshake (1–2 RTT) before any data. On a 100 ms mobile network that's 300+ ms of overhead. Fixes: keep-alive and connection reuse (one shared HTTP client instance in the app), HTTP/2 multiplexing, TLS 1.3 (1-RTT) and session resumption, HTTP/3 (QUIC), a CDN edge close to users to terminate TCP/TLS nearby, and `preconnect` hints on web.

---

## 🔷 Trade-offs
✅ TCP Advantages:
- Guaranteed, ordered, error-checked delivery — the app doesn't worry.
- Built-in congestion control protects the network.

❌ TCP Disadvantages:
- Handshake latency; head-of-line blocking; more overhead per packet.
- Connection state on the server (memory, TIME_WAIT sockets).

✅ UDP Advantages:
- Minimal latency and overhead, no connection state; supports broadcast/multicast.

❌ UDP Disadvantages:
- No reliability/order — app must handle loss; often blocked by corporate firewalls; no congestion control (can flood networks).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TCP | Reliable, ordered, connection-based protocol | भरोसेमंद कनेक्शन वाला प्रोटोकॉल |
| UDP | Fast, connectionless, no-guarantee protocol | तेज़, बिना गारंटी वाला प्रोटोकॉल |
| Handshake | Setup messages before data | बात शुरू करने से पहले हाथ मिलाना |
| ACK | Acknowledgement of received data | "मिल गया" की पुष्टि |
| Retransmission | Re-sending lost packets | खोया पैकेट दोबारा भेजना |
| RTT | Round Trip Time | जाने और वापस आने का समय |
| HOL Blocking | One lost packet blocks all after it | एक पैकेट के कारण सब रुक जाना |
| QUIC | Google's reliable protocol over UDP (HTTP/3) | UDP पर बना नया तेज़ प्रोटोकॉल |
| Keep-alive | Reusing a TCP connection | कनेक्शन को बार-बार इस्तेमाल करना |

---

## ⚡ 3-Line Summary
**English:**
1. TCP = reliable + ordered (handshake, ACKs, retransmits); UDP = fast, fire-and-forget.
2. TCP for APIs/DB/payments; UDP for video calls, gaming, DNS, and HTTP/3 (QUIC).
3. In production, reuse TCP connections (keep-alive, pooling, HTTP/2) to avoid handshake cost.

**Hindi:**
1. TCP = भरोसेमंद और क्रम में; UDP = तेज़ पर बिना गारंटी।
2. API, DB, पेमेंट के लिए TCP; वीडियो कॉल, गेम, DNS के लिए UDP।
3. बार-बार handshake से बचने के लिए कनेक्शन reuse करो (keep-alive, pooling)।

---

## ➡️ Next Topic Suggestion
**05. HTTP vs HTTPS** — TCP gives you a reliable pipe. Next: HTTP, the language your browser and APIs speak over that pipe (methods, status codes, headers, HTTP/1.1 vs 2 vs 3), and why HTTPS is mandatory.
