# Top 50 IoT Interview Q&A — Quick Revision
# 5+ YOE — Protocols + Cloud IoT + Edge + Security + System Design

---

## 🔴 Protocols & MQTT (Q1-Q15)

**Q1. What is MQTT and why is it preferred for IoT over HTTP?**
A: MQTT is a lightweight pub/sub protocol over TCP. After the initial connection, each message adds only ~2 bytes overhead vs ~700 bytes of HTTP headers. It supports QoS delivery guarantees, retained messages, Last Will, and persistent sessions — all designed for constrained devices on unreliable networks. HTTP is request/response — device must initiate every exchange. MQTT is bidirectional — cloud can push to device anytime.

**Q2. Explain MQTT QoS levels with real scenarios.**
A: QoS 0 (at most once) = fire and forget. Use for frequent metrics (CPU usage every 1s — if one drops, next arrives soon). QoS 1 (at least once) = broker sends PUBACK; publisher retries if no ACK — message may duplicate. Use for events (door opened — must receive, dup is ok). QoS 2 (exactly once) = 4-way handshake, no duplicates. Use for billing meter readings. In practice: QoS 1 + application-level deduplication gives QoS-2 semantics at QoS-1 speed.

**Q3. What is MQTT Last Will and Testament (LWT)?**
A: LWT is a message the broker publishes on behalf of the device if it disconnects ungracefully (without sending DISCONNECT). Configured at connection time: `will: { topic: 'devices/001/status', payload: '{"online":false}', qos: 1, retain: true }`. The broker only sends it if the connection drops without a clean DISCONNECT. Use case: device goes offline (power cut, network failure) → broker publishes `{online: false}` to a status topic → dashboard shows device offline.

**Q4. What is a retained message in MQTT?**
A: A retained message is stored by the broker and immediately delivered to any new subscriber — they get the last known value without waiting for the device to publish again. Set with `retain: true` on publish. Use case: device status `{online: true}` — dashboard subscribes after device connected → gets status immediately (without retained, would see nothing until next publish). Important: only one retained message per topic — new retained publish replaces it. Clear with empty payload: `publish(topic, '', {retain: true})`.

**Q5. MQTT topic wildcard: + vs # — explain with examples.**
A: `+` = single level wildcard. `devices/+/temperature` matches `devices/001/temperature` and `devices/999/temperature` but NOT `devices/001/sensor/temperature`. `#` = multi-level wildcard (must be at end). `devices/#` matches `devices/001`, `devices/001/temperature`, `devices/001/sensor/deep/reading`. Rule: `#` used for broad subscriptions (all topics under a prefix), `+` for structured topics where you know the depth. Brokers may restrict `#` subscriptions for performance.

**Q6. What is the difference between MQTT 3.1.1 and MQTT 5.0?**
A: MQTT 5.0 adds: (1) **Message expiry interval** — auto-expire stale messages broker is holding. (2) **User properties** — custom key-value headers in each packet. (3) **Request/response pattern** — `responseTopic` and `correlationData` properties. (4) **Topic aliases** — replace long topic strings with a short integer to save bandwidth. (5) **Shared subscriptions** — load balance consumers on one topic (multiple workers share messages). (6) **Reason codes** — specific disconnect/error reasons vs just error flag. Most AWS/Azure IoT supports both; MQTT 5.0 for new systems.

**Q7. What is a persistent session in MQTT?**
A: Set `clean: false` + stable `clientId`. Broker stores: active subscriptions, undelivered QoS 1/2 messages, and in-flight messages. When device reconnects with same clientId + clean:false, broker immediately delivers all queued messages. Use for devices that go offline frequently (battery-powered, cellular). Tradeoff: broker must store state per device — memory overhead. For millions of devices: set message expiry (MQTT 5.0) to avoid unbounded queue growth.

**Q8. How do you design MQTT topics for a large IoT system?**
A: Best practices: (1) Hierarchical: `{company}/{site}/{deviceType}/{deviceId}/{dataType}` e.g., `acme/plant-1/sensor/s-001/temperature`. (2) No leading slash. (3) No spaces or special chars. (4) Keep depth ≤ 6 levels. (5) Put variable parts (deviceId) after fixed parts (company, site) — enables wildcard at specific levels. (6) Separate telemetry, commands, status: `.../telemetry`, `.../commands`, `.../status`. (7) ACL can restrict per topic pattern — design with security in mind.

**Q9. How does MQTT over WebSocket differ from regular MQTT?**
A: Regular MQTT runs over TCP (port 1883/8883 for TLS). MQTT over WebSocket encapsulates MQTT inside the WebSocket protocol, which runs over HTTP upgrade (port 80/443). Why: browsers can't open raw TCP connections but can do WebSocket. Use case: real-time IoT dashboard in browser subscribes to MQTT topics directly. AWS IoT supports MQTT over WebSocket with Signature V4 auth. Device firmware uses raw TCP; browser dashboard uses WebSocket.

**Q10. What is Modbus and when is it used in IoT?**
A: Modbus is a legacy serial communication protocol from 1979, still dominant in industrial equipment (PLCs, VFDs, energy meters). Modbus RTU = binary encoding over RS-485 serial. Modbus TCP = same protocol over TCP/IP. Still used because: millions of legacy industrial devices speak Modbus and won't be replaced. IoT gateways read Modbus from industrial sensors and translate to MQTT for cloud. Key registers: Coils (0/1), Discrete Inputs (read-only 0/1), Input Registers (read-only 16-bit), Holding Registers (read-write 16-bit).

**Q11. LoRa vs LoRaWAN — what is the difference?**
A: **LoRa** = physical layer modulation technology (Chirp Spread Spectrum) — long range, low power radio. **LoRaWAN** = network protocol stack on top of LoRa — defines network architecture (end devices, gateways, network server). LoRa = the radio hardware. LoRaWAN = the complete network system. Range: 2-5km urban, 15km+ rural. Data rate: 250bps – 50kbps. Use: sensors that need very long range + battery-powered + send small data infrequently (farm moisture sensors, parking sensors, water meters).

**Q12. What is CoAP and when to use it over MQTT?**
A: CoAP (Constrained Application Protocol) is a RESTful protocol designed for constrained devices — uses UDP (not TCP), has GET/POST/PUT/DELETE like HTTP. Use when: device has no TCP stack (microcontrollers with limited memory), REST-style interactions needed, and network has high packet loss (UDP with retries). vs MQTT: CoAP is request/response (like HTTP), MQTT is pub/sub. For devices that are too constrained even for TCP: CoAP. For systems needing bidirectional messaging and broker fanout: MQTT.

**Q13. What is AMQP and how does it compare to MQTT for IoT?**
A: AMQP (Advanced Message Queuing Protocol) is a full-featured messaging protocol with exchanges, queues, routing keys, and binding patterns. More powerful but heavier than MQTT. MQTT: ~2 byte overhead, simple pub/sub. AMQP: ~60 byte overhead, rich routing, headers, transactions. Use AMQP: enterprise message bus, backend service-to-service, when you need complex routing (exchange types: direct, fanout, topic, headers). Use MQTT: device-to-cloud, constrained devices. Common pattern: devices → MQTT broker → bridge → RabbitMQ (AMQP) → backend services.

**Q14. What is shared subscription in MQTT?**
A: Shared subscriptions (MQTT 5.0 / some brokers support in 3.x) allow multiple subscribers to share a single subscription — messages are load-balanced across them (round-robin or random). Topic format: `$share/{groupName}/{topic}`. Example: 3 worker services subscribe to `$share/workers/devices/+/telemetry` → each message goes to exactly ONE worker (not all three). Use case: scaling out consumers — run 3 Node.js workers on an event queue without every worker processing every message.

**Q15. What is DDS (Data Distribution Service) and when is it used?**
A: DDS is a publish/subscribe middleware for real-time, mission-critical systems (aerospace, defense, robotics, autonomous vehicles). Unlike MQTT (centralized broker), DDS is brokerless — peer-to-peer discovery via multicast. Features: ultra-low latency (microseconds), QoS policies (deadline, liveliness, durability), typed data (IDL schema). Used in: ROS 2 (Robot Operating System), autonomous vehicles (Waymo), military systems. Too complex for typical IoT but important for IIoT and robotics.

---

## 🟠 Cloud IoT (Q16-Q25)

**Q16. Explain AWS IoT Core architecture.**
A: AWS IoT Core has: (1) **Message Broker** — managed MQTT/WebSocket/HTTP broker. (2) **Device Shadow** — per-device JSON state document (desired/reported). (3) **Rules Engine** — SQL-like rules to filter/transform/route messages to 20+ AWS services (DynamoDB, Lambda, S3, Kinesis, SNS). (4) **Registry** — device database with Things, certificates, policies. (5) **Fleet Indexing** — query across all device shadows/attributes. (6) **IoT Jobs** — manage OTA updates and remote operations. Scales to billions of devices.

**Q17. What is AWS IoT Rules Engine and how does it work?**
A: Rules Engine applies SQL statements to MQTT messages and routes to AWS services. Example: `SELECT *, clientid() as deviceId FROM 'devices/+/temperature' WHERE value > 80` → Lambda function (alert) + DynamoDB (store). Supports functions: `clientid()`, `topic()`, `timestamp()`, `aws_lambda()`. No need to write forwarding code — declarative rules in console or CloudFormation. Can filter, transform, and fan-out to multiple actions from one rule. DLQ (error action) handles failed routing.

**Q18. How does AWS IoT Device Provisioning work at scale?**
A: Two approaches: (1) **Fleet Provisioning with Claim Certificates** — devices ship with a shared "claim" certificate (different from their final cert). On first boot: device connects with claim cert → calls `CreateKeysAndCertificate` API → gets unique cert + private key generated on cloud → registers as a Thing → disables claim cert. (2) **Just-In-Time Registration (JITR)** — device brings its own cert (from factory CA). First connection: AWS IoT sees unknown cert → triggers Lambda via JITR → Lambda verifies, creates Thing + policy. Scales to millions without pre-provisioning.

**Q19. What is Azure IoT Hub vs Azure IoT Central?**
A: **IoT Hub** — PaaS service, full control, you build everything (routing, processing, UI). For developers/enterprises who need custom solutions. **IoT Central** — SaaS platform, opinionated, pre-built dashboards, device templates, built-in rules/actions. For quick PoC or when you want managed IoT without building everything. Think: IoT Hub = AWS IoT Core (PaaS). IoT Central = managed IoT application platform. For 5+ YOE interview: mention you've used IoT Hub for production and know when to choose each.

**Q20. What is Azure IoT Device Provisioning Service (DPS)?**
A: DPS automates zero-touch provisioning — devices self-register and are automatically assigned to the right IoT Hub. Enrollment types: (1) Individual enrollment (specific device, certificate or SAS). (2) Group enrollment (all devices from same CA). On first boot: device contacts DPS endpoint → DPS verifies certificate/SAS → assigns device to IoT Hub → returns IoT Hub hostname. Device then connects directly to IoT Hub. Supports multi-hub routing (e.g., route devices to closest regional hub). Equivalent to AWS IoT Fleet Provisioning.

**Q21. How does AWS IoT Jobs work for OTA updates?**
A: Jobs are cloud-managed operations sent to device fleets. Create a job with a Job Document (JSON with firmware URL, version, instructions) → target specific things or groups → AWS pushes to devices via MQTT. Device subscribes to `$aws/things/{name}/jobs/notify` → receives job notification → downloads firmware (from S3 pre-signed URL) → installs → reports status (queued → in_progress → succeeded/failed). Built-in: retry policies, timeout, rollout rate (e.g., 10% of fleet per hour to detect bad firmware).

**Q22. When would you use AWS Greengrass for edge computing?**
A: Use Greengrass when: (1) Processing must happen locally (latency-critical, <10ms). (2) Devices operate with intermittent cloud connectivity. (3) Need to run ML inference on edge (TensorFlow Lite). (4) Local MQTT broker for device-to-device communication without cloud round trip. (5) Protocol translation (Modbus devices → local Greengrass → MQTT to cloud). Greengrass v2 uses component model — deploy containerized or packaged Lambda components. Sync with cloud when connected; continues operating offline.

**Q23. How do you handle 1 million IoT devices on AWS IoT Core?**
A: AWS IoT Core scales automatically to 1B+ devices. Design concerns: (1) **Connection throttling** — default 500 new connections/sec per account (request limit increase). (2) **Publish throttling** — 2000 publishes/sec/connection default. (3) **Rules Engine throughput** — scale Lambda concurrency for spiky ingestion. (4) **Cost optimization** — minimize message frequency, use payloads efficiently, aggregate at edge. (5) **Topic naming** — avoid fan-out subscriptions that match millions of devices. (6) Use Fleet Indexing for querying device state instead of reading individual shadows.

**Q24. What is the difference between device-to-cloud and cloud-to-device messages in Azure IoT?**
A: **D2C (Device-to-Cloud)**: device sends telemetry and events to IoT Hub. Uses MQTT publish. IoT Hub stores in built-in Event Hub endpoint (24h retention). **C2D (Cloud-to-Device)**: cloud sends commands to specific device. IoT Hub queues them. Device acknowledges receipt. Max 64KB per message, 48h TTL. For configuration/state: use Device Twin (desired properties). For one-time commands: use Direct Methods (synchronous, timeout-based). For long-running jobs: use IoT Hub Jobs.

**Q25. How do you implement time-series data pipeline for IoT?**
A: Typical pipeline: Device → MQTT → IoT Core → Rules Engine → (1) Kinesis Data Streams → Kinesis Firehose → S3 (raw archive) + Lambda → InfluxDB/TimescaleDB (hot storage for dashboards). Schema: `{deviceId, metric, value, unit, timestamp}` with timestamp as primary sort key. Retention policies: raw data 7 days (hot), hourly aggregates 90 days (warm), daily aggregates 2 years (cold). Downsampling with InfluxDB tasks or TimescaleDB continuous aggregates. Grafana on top for visualization.

---

## 🟡 Edge Computing (Q26-Q30)

**Q26. What is edge computing in IoT and when is it essential?**
A: Edge computing moves processing from cloud to local devices/gateways. Essential when: (1) Latency requirements < cloud RTT (10-100ms for robot arms, autonomous vehicles — cloud adds 50-200ms). (2) Bandwidth cost too high (factory camera streams at 100Mbps — sending to cloud would cost millions). (3) Intermittent connectivity (shipping container in ocean — must work offline). (4) Data privacy (medical device — patient data can't leave hospital). (5) Local safety logic (industrial press — stop if sensor anomaly, don't wait for cloud roundtrip).

**Q27. How does store-and-forward work for offline IoT?**
A: Device/gateway stores messages locally when cloud is unreachable, forwards when connection restores. Implementation: (1) Local database (SQLite, LevelDB) on device. (2) Write sensor data to local DB always. (3) Background sync thread: reads unsent records, sends to cloud, marks as sent. (4) Handle order: send oldest first (FIFO) to maintain time ordering. (5) Set TTL: drop records older than N days to prevent unbounded storage. AWS Greengrass has built-in spooler component for this.

**Q28. What is protocol translation at the edge?**
A: Many industrial devices use legacy protocols (Modbus, OPC-UA, BACnet) that can't connect directly to cloud IoT platforms. Edge gateway translates: Modbus RTU (serial) → read registers → convert to JSON → publish to MQTT → cloud. Implementation: gateway runs Node.js with `modbus-serial` library, reads every 10s, publishes to AWS IoT Core via MQTT. Also normalizes data (temperature in Celsius → Fahrenheit if needed, units, scaling factors). This is one of the most common real-world IoT patterns.

**Q29. Explain edge ML inference with TensorFlow Lite.**
A: Train model in cloud (TensorFlow) → convert to TensorFlow Lite (.tflite) → deploy to edge device (Raspberry Pi, NVIDIA Jetson). Edge runs inference locally: camera frame → TFLite model → classification (anomaly/normal) → trigger alert or log. No cloud roundtrip for inference — works offline, sub-100ms latency. AWS Greengrass supports deploying ML components to edge. Azure IoT Edge has ML module support. Use case: quality control camera on production line — detects defects in real-time without cloud.

**Q30. How do you handle edge-to-cloud synchronization conflicts?**
A: When device operates offline and cloud state changes: (1) **Last-write-wins** — compare timestamps, latest wins (simplest). (2) **Device always wins for reported state** — device knows its actual state, cloud can't override reported. (3) **Cloud always wins for desired state** — device should always converge to cloud's desired config. (4) **Version vectors** — for complex state (device shadow version number). In AWS IoT Shadow: device reports current state, cloud sets desired — the separation of reported/desired eliminates most conflicts. For custom systems: use optimistic concurrency (version field, reject out-of-order updates).

---

## 🟢 Security (Q31-Q38)

**Q31. What is the OWASP IoT Top 10?**
A: (1) Weak/hardcoded passwords. (2) Insecure network services. (3) Insecure ecosystem interfaces (web/API). (4) Lack of secure update mechanism. (5) Use of insecure or outdated components. (6) Insufficient privacy protection. (7) Insecure data transfer and storage. (8) Lack of device management. (9) Insecure default settings. (10) Lack of physical hardening. Most critical in practice: hardcoded credentials (Mirai botnet exploited default admin:admin), insecure OTA (no signature verification), and no network segmentation.

**Q32. How do you secure an IoT device from scratch?**
A: Layered approach: (1) **Hardware**: secure element for key storage, no debug ports in production, tamper detection. (2) **Firmware**: signed firmware (verify before flash), minimal attack surface (disable unused services), RTOS with memory protection. (3) **Communication**: TLS/mTLS for all comms, certificate-based device identity, no self-signed certs in production. (4) **Cloud**: least-privilege IAM policies per device, restrict to own topic namespace. (5) **Network**: VLAN segregation for IoT, no direct internet access from devices (only to broker). (6) **Lifecycle**: OTA for security patches, certificate rotation, decommission procedure.

**Q33. What is secure boot?**
A: Secure boot verifies each stage of firmware loading using cryptographic signatures. Chain: Hardware Root of Trust (burned-in public key) → verifies Bootloader → verifies Firmware → verifies Application. Each component verifies the next using a trusted key. If verification fails → device refuses to boot (bricked is safer than compromised). Prevents: malicious firmware replacement (even with physical device access), runtime code injection. Implementation: microcontrollers with TrustZone (ARM), ATECC608 secure element, STM32 with option bytes.

**Q34. How does firmware OTA signing work?**
A: (1) Developer builds firmware binary. (2) CI/CD pipeline signs with private key: `openssl dgst -sha256 -sign firmware-signing.key firmware.bin > firmware.bin.sig`. (3) Signed firmware + signature uploaded to S3. (4) IoT Jobs sends job document with firmware URL + signature. (5) Device downloads firmware binary + signature. (6) Device verifies: `openssl dgst -sha256 -verify firmware-signing-pub.key -signature firmware.bin.sig firmware.bin`. (7) If valid: write to inactive partition → reboot. If invalid: discard, report failure. Never flash unverified firmware.

**Q35. How do you handle certificate rotation for a large device fleet?**
A: (1) **New certs with overlap period**: issue new cert 30 days before old expires. Attach both to device's Thing. Device uses new cert but broker accepts both during overlap. (2) **Via OTA/Job**: IoT Job pushes new cert + script → device writes to secure storage → updates connection config → reconnects with new cert → success → remove old cert. (3) **AWS IoT automation**: use EventBridge rule triggered on cert expiry → Lambda → create new cert → attach to Thing → push via IoT Job. Zero-downtime rotation is possible because AWS IoT allows multiple certs per Thing.

**Q36. What is network segmentation for IoT?**
A: IoT devices should be on a separate VLAN/network segment from corporate IT. Why: IoT devices often have weak security (Shodan searchable, default creds, no patching). If compromised, attacker on same network as corporate systems = lateral movement. Segmentation: IoT VLAN → firewall rules → only allow outbound to IoT broker/cloud. Block IoT-to-IT communication entirely. Block IoT-to-IoT unless explicitly needed. This limits blast radius if a device is compromised. AWS: IoT devices in private subnet, Greengrass gateway in DMZ subnet, rules for outbound-only communication.

**Q37. What is the Mirai botnet and what can we learn from it?**
A: Mirai (2016) was a botnet of ~600,000 IoT devices (cameras, routers) that launched the largest DDoS attack in history (1.1 Tbps). Attack vector: Mirai scanned the internet for devices with default credentials (admin:admin, root:root — 60 hardcoded combos). Devices compromised → used for DDoS. Lessons: (1) Change default credentials — force on first boot. (2) Network segmentation — IoT devices shouldn't be directly internet-accessible. (3) Auto-updates for security patches. (4) Rate limiting on login attempts. (5) Monitor outbound traffic from IoT devices for anomalies.

**Q38. What is mutual TLS (mTLS) in IoT?**
A: Normal TLS: only client verifies server's certificate. mTLS: BOTH sides verify each other's certificate. Broker presents cert → device verifies (server auth). Device presents cert → broker verifies (client auth). Both are authenticated. In IoT: device uses X.509 cert as its identity — no username/password needed. Policy attached to device cert controls what topics it can publish/subscribe. Enables: (1) No shared secrets. (2) Per-device identity and access control. (3) Cert revocation for decommissioning. AWS IoT Core, Azure IoT Hub, Mosquitto all support mTLS.

---

## 🔵 System Design (Q39-Q45)

**Q39. Design a system to monitor 100,000 industrial sensors in real-time.**
A: Architecture: Sensors → Edge Gateway (Modbus/RS-485) → MQTT over TLS → AWS IoT Core → Rules Engine → Kinesis Data Streams → (1) Lambda → InfluxDB (hot storage, last 7 days, real-time dashboards) + (2) Kinesis Firehose → S3 (cold storage, compressed Parquet). Alert path: Rule → IoT Events → SNS → PagerDuty. Dashboard: Grafana on InfluxDB. Scale considerations: 100K sensors × 1 msg/10s = 10K msg/sec. InfluxDB handles millions of writes/sec. Kinesis: 1 shard per 1K msg/sec = 10 shards.

**Q40. How would you scale MQTT broker to 1 million concurrent devices?**
A: (1) **Managed broker**: AWS IoT Core or Azure IoT Hub — they handle scaling, no broker management. (2) **Self-hosted cluster**: EMQX or HiveMQ cluster — distributed nodes with shared state (connection, session, routing). (3) Load balancer in front (NLB for TCP/TLS). (4) Sticky sessions not needed for MQTT if using clustered broker (session state shared). (5) 1M devices × 1 msg/5min = 3,333 msg/sec — very manageable for EMQX (handles 100M+ devices). (6) Horizontal scale: add EMQX nodes, NLB distributes new connections. Existing connections stay on current nodes.

**Q41. Design an OTA update system for 500,000 devices.**
A: (1) Firmware stored in S3 with versioning. (2) IoT Job created targeting device group. (3) **Staged rollout**: 1% first (500 devices) → monitor for 24h → 10% → 50% → 100%. (4) **Success criteria**: 95% of devices in cohort must succeed before expanding. (5) **Rollback**: if > 5% failures → pause/rollback. A/B partition on device — write to inactive, verify, then switch active. (6) **Bandwidth management**: schedule downloads off-peak, limit parallel downloads (100 simultaneous per broker). (7) **Monitoring**: CloudWatch metrics on job progress, Lambda alert on failure spike.

**Q42. How do you handle devices that go offline for months (e.g., seasonal equipment)?**
A: (1) **Shadow/twin persistence** — last known state preserved indefinitely. (2) **Pending jobs** — IoT Jobs queue commands for when device reconnects (job status: QUEUED). (3) **Expired message cleanup** — MQTT 5.0 message expiry: set TTL on commands so stale commands aren't executed months later. (4) **Re-provisioning** — cert may expire; either use long-validity certs (5+ years) for seasonal devices, or implement fleet provisioning that re-issues cert on reconnect if expired. (5) **Data gap handling** — time-series queries must handle gaps; Grafana can interpolate or show null.

**Q43. Design a real-time IoT dashboard for 10,000 devices.**
A: (1) Devices → MQTT broker → Rules Engine → InfluxDB (live data). (2) Dashboard backend: Node.js WebSocket server subscribes to MQTT `devices/#` with wildcard → streams updates to browser via WebSocket. (3) **Scalability**: WebSocket server can't subscribe to all 10K device topics if using 1 server. Use Redis pub/sub: MQTT → Lambda → Redis PUBLISH → WebSocket servers subscribe to Redis. Browser connects to any WS server → gets updates via Redis. (4) **Aggregated view**: pre-compute stats (active count, avg temperature) every 30s via scheduled Lambda → cache in Redis → serve from cache.

**Q44. How do you design for 99.99% availability in IoT?**
A: 99.99% = ~52 min downtime/year. Multi-layer HA: (1) **Device**: persistent MQTT session, auto-reconnect with backoff. If broker unreachable: buffer locally (store-and-forward). (2) **Broker**: managed service (AWS IoT Core) with SLA, or multi-AZ EMQX cluster. (3) **Ingestion**: Kinesis/Kafka with multi-AZ. (4) **Processing**: Lambda (99.95% SLA) + SQS DLQ for retries. (5) **Storage**: multi-AZ InfluxDB or managed TimescaleDB. (6) **Multi-region**: active-active for global IoT (Route 53 latency routing). Test: chaos engineering — kill AZs, test reconnect behavior.

**Q45. What's the biggest IoT architectural mistake you've seen or would avoid?**
A: Common mistakes: (1) **HTTP polling instead of MQTT push** — kills at scale (1000 devices × 1 req/sec = 1000 req/sec, vs MQTT push). (2) **No message deduplication** — using QoS 1 without idempotent handlers causes duplicate database writes. (3) **Storing credentials in firmware** — gets extracted, leaks, all devices compromised. (4) **Not planning for offline** — device reboots and loses 2 hours of data because there's no local buffer. (5) **Wrong granularity** — sending raw sensor readings to cloud every second when aggregated per minute would suffice (60x cost + bandwidth savings). (6) **No device shadow/twin** — app polls device directly; device offline = app broken.

---

## ⚫ Coding + Troubleshooting (Q46-Q50)

**Q46. Write a Node.js MQTT client that handles reconnection gracefully.**
A: Key points: (1) Set `reconnectPeriod: 0` (disable built-in). (2) Implement exponential backoff on `'close'` event. (3) Add jitter (±30%) to prevent thundering herd. (4) Buffer QoS 1 messages while offline. (5) Flush buffer after reconnect. (6) Never reconnect on `'error'` — many errors (auth, permission) won't be fixed by reconnect. Cap backoff at 60s. Reset attempt counter on successful connect. See Q064 for full implementation.

**Q47. How do you debug a device that keeps disconnecting from MQTT broker?**
A: Systematic debug: (1) Check broker logs — what reason code? 0x80 = unspecified, 0x8E = session takeover (another device using same clientId!). (2) Check keepalive — broker timeout is 1.5× keepalive. If device takes >90s for any operation → disconnect. (3) Check network — packet loss? MTU issues? (4) Check device memory — Node.js heap growing → GC pause > keepalive → disconnect. (5) Check TLS cert — expired? Wrong CA? (6) Enable mqtt.js debug: `DEBUG=mqtt* node app.js`. (7) Capture packets: Wireshark on broker or tcpdump on device.

**Q48. A device is sending data but it's not reaching the database. Debug.**
A: Trace the pipeline: (1) **MQTT received?** Check broker logs / MQTT spy (MQTT Explorer). (2) **Rules Engine triggered?** Check IoT Core CloudWatch metrics: `TopicMatch`, `RuleMessageThrottled`. (3) **Rules Engine error?** Check error action (should have error action configured → DLQ). (4) **Action executed?** Lambda/Kinesis → CloudWatch logs for Lambda invocations. (5) **Database write?** DB logs, connectivity from Lambda (VPC?). (6) **Common gotcha**: IoT Rules Engine SQL topic filter is case-sensitive! `devices/001/Temperature` ≠ `devices/001/temperature`.

**Q49. How do you parse binary Modbus data in Node.js?**
A: Use Node.js `Buffer` API. Modbus uses big-endian 16-bit registers. Example: read 2 registers (4 bytes) = one 32-bit float. `const buf = Buffer.from([0x42, 0xF6, 0x00, 0x00])` → `buf.readFloatBE(0)` = 123.0. For int16: `buf.readInt16BE(0)`. For uint32: `buf.readUInt32BE(0)`. Scale factors common in Modbus: value / 10 for one decimal. Bitfield registers: `(reg >> 3) & 0x01` to extract bit 3. Library: `modbus-serial` npm package handles framing; you still need to parse register values.

**Q50. How do you simulate 1,000 IoT devices for load testing?**
A: Use Node.js with async: spawn 1000 MQTT clients in parallel with artificial delays. Key: don't connect all 1000 simultaneously — stagger by 100ms to avoid connection spike. Each simulated device: unique clientId (device-{i}), publishes random sensor data every 10s, subscribes to its command topic. Monitor: broker CPU/memory, message throughput, connection count. Tools: MQTT Bench (CLI), custom Node.js simulator, or AWS IoT Device Simulator (managed service). Track: connection success rate, publish latency (P99), message loss rate. See Q219 for implementation.
