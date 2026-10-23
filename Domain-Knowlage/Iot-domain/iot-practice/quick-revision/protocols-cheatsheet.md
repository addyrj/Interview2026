# IoT Protocols Cheatsheet — Quick Revision
# 5+ YOE IoT Interview — Protocol Decision Guide

---

## 📊 Protocol Comparison Table

```
Protocol  | Transport | Direction      | QoS | Overhead | Range    | Best For
──────────┼───────────┼────────────────┼─────┼──────────┼──────────┼────────────────────────
MQTT      | TCP       | Bidirectional  | 0,1,2| ~2B     | Internet | IoT telemetry (default)
CoAP      | UDP       | Req/Response   | 0,1 | ~4B      | Internet | Ultra-constrained MCU
HTTP/REST | TCP       | Req/Response   | None| ~700B    | Internet | APIs, one-time commands
WebSocket | TCP       | Bidirectional  | None| ~6B      | Internet | Browser dashboards
AMQP      | TCP       | Bidirectional  | Yes | ~60B     | LAN/Int  | Enterprise messaging
Modbus    | Serial/TCP| Req/Response   | None| ~8B      | <1200m   | Legacy industrial PLCs
OPC-UA    | TCP       | Bidirectional  | Yes | Heavy    | LAN      | Industrial automation
Zigbee    | 802.15.4  | Mesh           | Yes | ~10B     | <100m    | Smart home mesh
Z-Wave    | 908MHz    | Mesh           | Yes | ~5B      | <30m     | Smart home (low EMI)
Thread    | 802.15.4  | Mesh (IPv6)    | Yes | ~10B     | <100m    | Next-gen smart home
BLE       | 2.4GHz    | Point-to-point | No  | ~10B     | <50m     | Wearables, beacons
LoRa      | Sub-GHz   | Point-to-point | App | ~10B     | 15km     | Long-range low-data
LoRaWAN   | LoRa      | Star           | 0,1,2| ~13B   | 15km     | Smart city, agriculture
NB-IoT    | LTE-M1   | Bidirectional  | Yes | ~25B     | Carrier  | Smart meters, cellular
LTE-M     | LTE-M2   | Bidirectional  | Yes | Variable | Carrier  | Mobile IoT, asset track
WiFi      | 802.11    | Bidirectional  | App | ~30B     | <100m    | High-data local IoT
```

---

## 🎯 Protocol Decision Tree

```
Is device battery-powered?
  YES → How much data per transmission?
    Small (<100 bytes/day) AND long range needed:
      → LoRaWAN (smart city) or NB-IoT (cellular coverage)
    Small-medium AND short range:
      → Zigbee / Thread / BLE
    Medium AND needs reliable delivery:
      → MQTT over WiFi / LTE-M

  NO → Is device industrial/legacy?
    YES → Does it use RS-485/serial?
        → Modbus RTU → translate at gateway to MQTT
      Uses OPC-UA?
        → OPC-UA for data modeling, MQTT for cloud transport
    NO → Connect to internet?
      Direct internet → MQTT (cloud IoT)
      Browser dashboard → WebSocket
      One-time command/API → HTTP REST
      Ultra-constrained (no TCP) → CoAP
```

---

## 🔴 MQTT In-Depth

```
Ports:
  1883  → plain TCP (dev only!)
  8883  → TLS (production)
  80/443 → WebSocket / WSS

Architecture:
  Device ←MQTT→ Broker ←MQTT→ Backend/Cloud
  (Publisher)   (Hub)         (Subscriber)

Topic hierarchy example:
  factory/line-1/robot-001/temperature
  factory/line-1/robot-001/speed
  factory/line-1/+/alarm            → all robots alarm on line-1
  factory/#                          → everything in factory

Broker options:
  Mosquitto    → single node, open source, simple
  HiveMQ       → enterprise, cloud, clustering
  EMQX         → open source, 100M+ connections, clustering
  AWS IoT Core → fully managed, unlimited scale
  Azure IoT Hub → fully managed, Azure integration

Message format (no mandated format — use JSON):
{
  "deviceId": "robot-001",
  "metric": "temperature",
  "value": 73.2,
  "unit": "C",
  "ts": 1640000000000   ← Unix epoch milliseconds
}
```

---

## 🟠 Modbus Reference

```
Modbus function codes (most common):
  0x01 → Read Coils (1-bit read)
  0x02 → Read Discrete Inputs (1-bit read-only)
  0x03 → Read Holding Registers (16-bit read/write)
  0x04 → Read Input Registers (16-bit read-only)
  0x05 → Write Single Coil
  0x06 → Write Single Register
  0x10 → Write Multiple Registers (0x10 = decimal 16)

Register layout example (energy meter):
  Register 40001 (0x0000) → Voltage L1 (× 0.1 = Volts)
  Register 40003 (0x0002) → Current L1 (× 0.01 = Amps)
  Register 40005 (0x0004) → Active Power (int32, 2 registers)

Node.js reading Modbus:
  const ModbusRTU = require('modbus-serial');
  const client = new ModbusRTU();
  await client.connectRTUBuffered('/dev/ttyUSB0', { baudRate: 9600 });
  client.setID(1);  // slave address
  const data = await client.readHoldingRegisters(0, 10);  // read 10 regs from address 0
  const voltage = data.data[0] * 0.1;  // scale factor

Modbus TCP vs RTU:
  RTU → RS-485 serial, CRC checksum, up to 247 devices on one bus
  TCP → over Ethernet/WiFi, same protocol, port 502, no CRC (TCP handles it)
```

---

## 🟡 LoRaWAN Quick Reference

```
Classes:
  Class A → Lowest power. Device transmits, then opens 2 brief RX windows.
            No other downlink possible. Best: battery sensors.
  Class B → Scheduled downlinks via beacon. Moderate power.
  Class C → Always listening. High power. Use: mains-powered devices.

Data rates (EU868):
  SF12 → slowest, longest range, 250bps
  SF7  → fastest, shortest range, 5.5kbps
  Adaptive Data Rate (ADR): network adjusts SF automatically

Frequency plans:
  EU868: 868MHz  US915: 915MHz  AS923: 923MHz  IN865: 865MHz

Architecture:
  End Device → (LoRa radio) → Gateway → (internet) → Network Server (TTN/ChirpStack)
               many gateways can receive same packet (diversity)

Payload limit:
  SF7: max 242 bytes  SF12: max 51 bytes
  → Compress! No verbose JSON → use binary encoding

Real usage: water meters, soil moisture, parking sensors, asset tracking
```

---

## 🟢 OPC-UA Quick Reference

```
What: Machine-readable standard for industrial equipment
      Self-describing data (information model)
      Rich address space (objects, variables, methods, events)

When to use:
  - Industrial automation (PLCs, SCADA, HMI)
  - Need semantic data model (not just values)
  - IEC 62541 compliance required
  - Brownfield integration (PLC → OPC-UA server → MQTT bridge → cloud)

Architecture:
  PLC → OPC-UA Server → OPC-UA Client/Gateway → MQTT → Cloud IoT

Security modes:
  None / Sign / Sign+Encrypt + user auth (anonymous, username, certificate)

Companion specifications (Sparkplug B):
  MQTT + Sparkplug B = OPC-UA style data model over MQTT
  Used in: oil & gas, manufacturing, industrial IoT

vs Modbus:
  Modbus: register-based, no data semantics, simple, fast
  OPC-UA: object model, semantic, complex, slower — but self-describing
```

---

## 🔵 Wireless Protocol Comparison (Short Range)

```
Protocol | Freq     | Range  | Power  | Throughput | Mesh | Use Case
─────────┼──────────┼────────┼────────┼────────────┼──────┼────────────────
WiFi     | 2.4/5GHz | 100m   | High   | 100+ Mbps  | No   | Cameras, gateways
BLE 5.x  | 2.4GHz   | 50m    | Low    | 2 Mbps     | Mesh | Wearables, beacons
Zigbee   | 2.4GHz   | 10-100m| Low    | 250 kbps   | Yes  | Smart home sensors
Z-Wave   | 908MHz   | 30m    | Low    | 100 kbps   | Yes  | Smart home (EU/US)
Thread   | 2.4GHz   | 10-100m| Low    | 250 kbps   | Yes  | Modern smart home
Matter   | WiFi/BLE/Thread | - | -    | -          | -    | Apple/Google/Amazon unified

Matter (2022):
  - Unified smart home standard (Apple, Google, Amazon, Samsung)
  - Works over WiFi, Thread, Ethernet
  - Local communication first (no cloud required)
  - Google Home, Apple Home, Amazon Alexa all support it
```

---

## ⚡ Protocol Quick Picks (Interview Answers)

```
"Smart home thermostat" → Zigbee/Thread (low power, mesh) or WiFi (if always-on)
"Industrial robot arm" → OPC-UA (semantic model) + MQTT bridge to cloud
"Remote water meter" → LoRaWAN Class A (battery, rare readings, long range)
"Real-time dashboard" → WebSocket (browser) + MQTT (devices)
"Mobile asset tracking" → LTE-M or NB-IoT (cellular, wide coverage)
"Legacy PLC integration" → Modbus TCP → edge gateway → MQTT → cloud
"100K sensor telemetry" → MQTT to AWS IoT Core → Kinesis → InfluxDB
"Door lock control" → MQTT with QoS 1 (must receive command) + ZigBee local
"Wearable fitness band" → BLE to phone → phone sends to cloud via HTTPS
"Autonomous vehicle" → DDS (real-time, brokerless, low latency)
```
