<!-- # 01. How Internet Works
# हिंदी में: इंटरनेट कैसे काम करता है — दुनिया भर के कंप्यूटरों का आपस में जुड़ा हुआ नेटवर्क

---

## 🔵 Simple Definition (English)
The Internet is a **network of networks**. Millions of computers (phones, laptops, servers) are connected through cables, Wi-Fi and routers, and they talk to each other using common rules called **protocols** (TCP/IP).
Data is never sent as one big piece — it is broken into small **packets**, sent separately, and joined back at the destination.

## 🔵 सरल परिभाषा (Hindi)
इंटरनेट बहुत सारे छोटे-छोटे नेटवर्क्स का एक बड़ा जाल है। हर डिवाइस एक तय नियम (प्रोटोकॉल — TCP/IP) से बात करता है।
डेटा छोटे-छोटे टुकड़ों (पैकेट्स) में जाता है और मंज़िल पर पहुँचकर फिर से जुड़ जाता है।

---

## 🔴 Problem it Solves
- Before the internet, computers were isolated. To share data you physically carried floppy disks or used a direct dedicated phone line between **two** machines.
- A dedicated line between every pair of computers is impossible (1 billion devices → ~10¹⁷ wires).
- If one dedicated line broke, the communication stopped completely.

The internet solved this with:
1. **Shared network** — everyone uses the same roads (routers + cables), not private wires.
2. **Packet switching** — data is split into packets; each packet can take a different route. If one road breaks, packets take another road.
3. **Common language (TCP/IP)** — any device from any company can talk to any other device.

## 🔴 यह क्यों बना? (Hindi)
पहले हर दो कंप्यूटर के बीच अलग तार चाहिए था — करोड़ों डिवाइस के लिए यह नामुमकिन था, और तार टूटे तो बात बंद।
इंटरनेट ने सबको एक साझा रास्ता (राउटर्स + केबल) दिया, डेटा को पैकेट्स में तोड़ा ताकि रास्ता बंद हो तो दूसरा रास्ता ले सके, और सबको एक भाषा (TCP/IP) दी।

---

## 🟢 How it Works — Step by Step

### The big picture

```
 Your Phone/Laptop
      │  (Wi-Fi / 4G / 5G)
      ▼
 ┌──────────────┐
 │ Home Router  │  ← gives you a private IP (192.168.x.x), does NAT
 └──────┬───────┘
        │ (fiber / cable)
        ▼
 ┌──────────────┐
 │  Local ISP   │  ← Jio / Airtel / ACT. Gives you a public IP
 └──────┬───────┘
        │
        ▼
 ┌──────────────┐        ┌──────────────┐
 │ Regional /   │◄──────►│ Internet     │  ← IXP: ISPs exchange traffic
 │ Tier-1 ISP   │        │ Exchange(IXP)│
 └──────┬───────┘        └──────────────┘
        │  (undersea fiber cables between countries)
        ▼
 ┌──────────────┐
 │ Data Center  │  ← AWS Mumbai (ap-south-1), Google, etc.
 │  (Server)    │
 └──────────────┘
```

### What happens when you open `https://www.swiggy.com`

```
Step 1 → You type swiggy.com in the browser
Step 2 → DNS lookup: "What is the IP of swiggy.com?"  → 13.x.x.x
Step 3 → TCP connection: 3-way handshake with that IP on port 443
Step 4 → TLS handshake: agree on encryption keys (HTTPS)
Step 5 → Browser sends HTTP request:  GET / HTTP/1.1
Step 6 → Request is split into PACKETS → routers forward each packet hop by hop
Step 7 → Server (Nginx → Node.js) builds a response (HTML/JSON)
Step 8 → Response packets travel back, maybe by different routes
Step 9 → Your device reassembles packets in order (TCP does this)
Step 10 → Browser renders the page
```

### Packet switching — the core idea

```
Message: "HELLO WORLD"  →  split into packets

 [1|HEL] ──► Router A ──► Router C ──────────────┐
 [2|LO ] ──► Router A ──► Router B ──► Router D ──┤──► Server joins: 1,2,3,4
 [3|WOR] ──► Router A ──► Router C ──────────────┤     "HELLO WORLD"
 [4|LD ] ──► Router A ──► Router B ──► Router D ──┘

Each packet has:  [ Source IP | Destination IP | Sequence No. | Data ]
If Router C dies → packets automatically go through B and D.
```

### TCP/IP layers (the "post office" model)

```
┌───────────────────────────┬──────────────────────────┬─────────────────────┐
│ Layer                     │ Job                      │ Examples            │
├───────────────────────────┼──────────────────────────┼─────────────────────┤
│ 4. Application            │ What the data means      │ HTTP, HTTPS, DNS,   │
│                           │                          │ WebSocket, SMTP     │
│ 3. Transport              │ Reliable delivery, ports │ TCP, UDP            │
│ 2. Internet (Network)     │ Addressing + routing     │ IP, ICMP            │
│ 1. Link (Network Access)  │ Physical sending         │ Ethernet, Wi-Fi, 4G │
└───────────────────────────┴──────────────────────────┴─────────────────────┘

Sending:   HTTP data → + TCP header (ports) → + IP header (IPs) → + Ethernet frame → wire
Receiving: unwrap in reverse order. (Called ENCAPSULATION)
```

> 💡 **Analogy:** Sending a parcel. Application = the letter you write. Transport (TCP) = courier that guarantees delivery & tracking number. IP = the address on the parcel. Link = the truck/bike that physically carries it.

## 🟢 कैसे काम करता है? (Hindi)
1. आप URL डालते हो → DNS से सर्वर का IP मिलता है।
2. TCP कनेक्शन बनता है, फिर TLS से एन्क्रिप्शन सेट होता है।
3. आपका रिक्वेस्ट पैकेट्स में टूटकर राउटर्स से होते हुए सर्वर तक जाता है।
4. सर्वर जवाब भेजता है, पैकेट्स वापस आते हैं और TCP उन्हें सही क्रम में जोड़ता है।
5. हर लेयर अपना "लिफ़ाफ़ा" (header) लगाती है — इसे Encapsulation कहते हैं।

> The **OSI model** has 7 layers (Physical, Data Link, Network, Transport, Session, Presentation, Application). In interviews, TCP/IP 4-layer is enough, but know that "Layer 4" = Transport and "Layer 7" = Application — load balancers are described this way (L4 vs L7 LB).

---

## 🟡 Real World Example

**Netflix in India**
- You press play in Mumbai. If the video came from a US server, every packet would cross undersea cables (~200+ ms latency) → buffering.
- So Netflix places **Open Connect** cache servers *inside* Jio/Airtel data centers in India. Your packets travel only Phone → ISP → Netflix box inside the ISP. Very short path → instant playback.
- This is why **"where your server is physically located" is a system design decision**, not just a deployment detail.

**Zomato during a cable cut**
- In 2024 several Red Sea undersea cables were damaged. Traffic between Asia and Europe was **re-routed automatically** via other cables — slower, but the internet kept working. That's packet switching + routing in action.

## 🟡 Real Example Hindi में
Netflix ने भारत में Jio/Airtel के डेटा सेंटर के अंदर ही अपने कैश सर्वर रख दिए — इसलिए वीडियो अमेरिका से नहीं, पास से आता है और बफ़रिंग नहीं होती।
2024 में Red Sea की केबल कटी, फिर भी इंटरनेट चलता रहा क्योंकि पैकेट्स ने अपने आप दूसरा रास्ता ले लिया।

---

## 🟠 My Stack Example

### See the path your packets take
```bash
# Every line = one router (hop) between you and the server
traceroute google.com          # mac / linux
tracert google.com             # windows

# Example output:
#  1  192.168.1.1   (your home router)        2 ms
#  2  10.50.0.1     (Jio internal)            8 ms
#  3  ...           (Jio backbone)           12 ms
#  9  142.250.x.x   (Google)                 18 ms
```

### See every phase of a request (DNS, TCP, TLS, server time)
```bash
curl -o /dev/null -s -w "\
DNS lookup:    %{time_namelookup}s\n\
TCP connect:   %{time_connect}s\n\
TLS handshake: %{time_appconnect}s\n\
Server wait:   %{time_starttransfer}s  (TTFB)\n\
Total:         %{time_total}s\n" https://api.yourapp.com/health
```
Use this when someone says "the API is slow" — it tells you **whether the problem is network (DNS/TCP/TLS) or your Node/FastAPI code (TTFB)**.

### Where your app sits in this picture
```
React Native app / Next.js browser
        │  HTTPS (packets over the internet)
        ▼
  AWS ap-south-1 (Mumbai)  ← choose region close to users (India users → Mumbai)
        │
   Nginx (port 443, TLS termination)
        │  (private network inside VPC — fast, no internet)
        ▼
   Node.js / FastAPI (port 3000 / 8000)
        │
   PostgreSQL (5432) + Redis (6379)
```

Key takeaway for your apps: **the public internet part is slow and unreliable; the inside-the-data-center part is fast.** So: reduce round trips from client (batch API calls), compress responses (gzip/brotli in Nginx), and put static files on a CDN.

```nginx
# nginx.conf — fewer bytes over the internet
gzip on;
gzip_types application/json text/css application/javascript;
```

---

## ⚫ Interview Questions + Answers

**Q1: What happens when you type a URL in the browser and press Enter?**
A1: (Most famous question.) 1) Browser checks its cache, then does a **DNS lookup** to get the IP. 2) Opens a **TCP connection** (3-way handshake) to that IP on port 443. 3) Does a **TLS handshake** to set up encryption. 4) Sends an **HTTP request**. 5) Request reaches load balancer/Nginx → app server → maybe DB/cache. 6) Server sends an **HTTP response**. 7) Browser parses HTML, downloads CSS/JS/images (more requests), builds DOM + CSSOM, and **renders** the page. Mention caching (browser, DNS, CDN) at every step for bonus points.

**Q2: What is packet switching and why is it better than circuit switching?**
A2: Circuit switching (old telephone) reserves a full dedicated path for the whole call — wasteful when idle and fails if the path breaks. Packet switching splits data into packets that share the network and can take different routes. Benefits: efficient sharing of bandwidth, and resilience — if a router fails, packets are re-routed.

**Q3: Explain the TCP/IP model layers.**
A3: Application (HTTP, DNS — meaning of data), Transport (TCP/UDP — ports, reliability), Internet (IP — addressing and routing between networks), Link (Ethernet/Wi-Fi — physical transfer). Each layer adds its own header (encapsulation). L4 = transport, L7 = application, which is why we say "L4 load balancer" vs "L7 load balancer".

**Q4: What is an ISP and an IXP?**
A4: An ISP (Internet Service Provider like Jio, Airtel) connects you to the internet. ISPs connect to each other at IXPs (Internet Exchange Points) so traffic between two Indian ISPs doesn't have to go abroad. Big companies (Netflix, Google) also "peer" at IXPs or put caches inside ISPs to reduce latency.

**Q5: Why does server location matter for system design?**
A5: Data can't travel faster than light in fiber (~200,000 km/s). Mumbai → US East and back is ~200+ ms just in travel time, before any processing. For users in India, host in Mumbai (ap-south-1), use a CDN for static content, and for global apps use multi-region deployment. Fewer round trips and closer servers = lower latency.

---

## 🔷 Trade-offs
✅ Advantages (of packet-switched internet design):
- Very resilient — no single path; routes around failures.
- Efficient — many users share the same cables.
- Open standards (TCP/IP) — any device can join.

❌ Disadvantages:
- No guaranteed speed — packets can be delayed, lost or arrive out of order (TCP must fix this).
- Latency depends on physical distance — can't be fully "optimized away".
- Shared network → security risks (sniffing, spoofing) → we need HTTPS/TLS.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Packet | Small chunk of data with source/destination address | डेटा का छोटा टुकड़ा |
| Router | Device that forwards packets to the next hop | रास्ता बताने वाला डिवाइस |
| ISP | Company providing internet (Jio, Airtel) | इंटरनेट देने वाली कंपनी |
| Protocol | Agreed rules for communication | बातचीत के नियम |
| TCP/IP | Core protocol suite of the internet | इंटरनेट की मूल भाषा |
| Hop | One router jump on the path | एक राउटर से दूसरे तक की छलांग |
| Latency | Time for data to travel | डेटा पहुँचने में लगने वाला समय |
| Encapsulation | Each layer wraps data with its header | डेटा को परतों में लपेटना |
| Data Center | Building full of servers (AWS, GCP) | सर्वरों का घर |

---

## ⚡ 3-Line Summary
**English:**
1. The internet is a network of networks; devices talk using TCP/IP.
2. Data is split into packets that travel via routers, possibly on different paths, and get reassembled.
3. Physical distance = latency, so put servers/CDN close to users and reduce round trips.

**Hindi:**
1. इंटरनेट नेटवर्क्स का जाल है, सब TCP/IP भाषा में बात करते हैं।
2. डेटा पैकेट्स में टूटकर राउटर्स से होकर जाता है और मंज़िल पर जुड़ता है।
3. दूरी = देरी, इसलिए सर्वर और CDN यूज़र के पास रखो।

---

## ➡️ Next Topic Suggestion
**02. DNS** — Step 2 of every request is "find the IP of swiggy.com". Next, learn how DNS does that in milliseconds for billions of requests, and how it's used for load balancing and failover. -->
