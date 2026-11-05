# 171. Macvlan Network
# हिंदी में: Macvlan Network (container को अपना LAN IP और MAC)

---

## 🔵 Simple Definition (English)
A **macvlan network** gives each container its **own MAC address and an IP from your physical LAN**. The container looks like a separate machine plugged into the same switch as the host. There is no NAT and no port mapping; you reach it directly on its own IP.

## 🔵 सरल परिभाषा (Hindi)
**Macvlan network** हर container को **अपना MAC address और आपके physical LAN का IP** देता है। Container ऐसा दिखता है जैसे वह host के साथ उसी switch में लगा कोई अलग machine हो। यहाँ NAT या port mapping नहीं होता; आप सीधे उसके अपने IP पर पहुँचते हैं।

---

## 🔴 Problem it Solves
Bridge networking hides containers behind the host IP with NAT and `-p` mappings. That breaks legacy software that expects to bind a real IP (DHCP servers, SNMP/monitoring agents, SIP/VoIP, network appliances, licensed software tied to a MAC) and adds NAT overhead. Macvlan lets such workloads sit directly on the LAN with their own address and with near bare-metal network performance.

## 🔴 यह क्यों बना? (Hindi)
Bridge networking में containers host IP के पीछे NAT और `-p` mapping से छिपे रहते हैं। इससे वे legacy software टूटते हैं जिन्हें असली IP चाहिए (DHCP server, SNMP/monitoring agents, SIP/VoIP, network appliances, MAC से बँधे license)। NAT का overhead भी आता है। Macvlan ऐसे workloads को सीधे LAN पर अपने address के साथ रखता है और performance लगभग bare-metal मिलती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick the host's physical NIC (parent), e.g. eth0, and the LAN subnet/gateway
Step 2 → docker network create -d macvlan --subnet --gateway -o parent=eth0 lan-net
Step 3 → Container starts, kernel creates a virtual sub-interface of eth0 with a NEW MAC
Step 4 → Container gets a static/chosen IP inside the LAN subnet (outside your DHCP range!)
Step 5 → Other LAN machines reach the container directly: ARP -> container MAC
Step 6 → Host itself CANNOT reach its own macvlan containers (kernel isolation) unless you add a macvlan shim interface
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Host की physical NIC (parent) चुनो, जैसे eth0, और LAN का subnet/gateway
Step 2 → docker network create -d macvlan --subnet --gateway -o parent=eth0 lan-net
Step 3 → Container चलते ही kernel eth0 का virtual sub-interface बनाता है, नए MAC के साथ
Step 4 → Container को LAN subnet का IP मिलता है (अपनी DHCP range के बाहर से चुनो!)
Step 5 → LAN की दूसरी machines सीधे पहुँचती हैं: ARP -> container का MAC
Step 6 → Host खुद अपने macvlan containers तक नहीं पहुँच पाता, जब तक macvlan shim interface न बनाओ
```

---

## 🟡 Real World Example
A company runs a **UniFi / Pi-hole / SNMP exporter** on an office server. The Pi-hole container needs IP `192.168.1.53` so every device uses it as DNS, and it must bind port 53 without clashing with the host's own resolver. Macvlan gives it that IP. On AWS this is different: ENIs do not allow extra MACs, so macvlan generally does **not** work on EC2 (and many VPS providers block it); it is mainly for on-prem or bare-metal servers.

## 🟡 Real Example Hindi mein
किसी company के office server पर **Pi-hole / SNMP exporter** चलता है। Pi-hole container को IP `192.168.1.53` चाहिए ताकि हर device उसे DNS बनाए, और port 53 host के resolver से टकराए नहीं। Macvlan यह IP देता है। AWS पर स्थिति अलग है: ENI अतिरिक्त MAC नहीं मानते, इसलिए EC2 पर macvlan आम तौर पर **काम नहीं करता** (कई VPS providers भी block करते हैं); यह मुख्यतः on-prem या bare-metal के लिए है।

---

## 💻 Code / Config Example — Basic
```bash
# Find parent interface and LAN details first
ip route | grep default            # shows gateway and interface (e.g. eth0)

# Create macvlan network on the LAN 192.168.1.0/24
docker network create -d macvlan \
  --subnet=192.168.1.0/24 \
  --gateway=192.168.1.1 \
  --ip-range=192.168.1.192/27 \
  -o parent=eth0 \
  lan-net
# --subnet     : your real LAN subnet
# --gateway    : your real router
# --ip-range   : addresses Docker may assign (reserve it outside the DHCP pool!)
# -o parent    : physical NIC to attach to

# Run a container with a fixed LAN IP
docker run -d --name whoami \
  --network lan-net \
  --ip 192.168.1.200 \
  traefik/whoami:v1.10             # example image, prints request info

# From ANOTHER machine on the LAN (not the host):
# curl http://192.168.1.200
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - macvlan + host access shim + bridge for internal talk
services:
  pihole:
    image: pihole/pihole:2024.07.0        # example tag, update to current
    container_name: pihole                # fixed name for logs / scripts
    environment:
      TZ: Asia/Kolkata                    # timezone
      WEBPASSWORD_FILE: /run/secrets/pihole_pw   # keep password out of env (compose secret)
    secrets:
      - pihole_pw                         # mount secret file
    networks:
      lan:                                # LAN-facing macvlan network
        ipv4_address: 192.168.1.53        # fixed IP, outside DHCP pool
      internal:                           # private bridge for sidecar containers
        {}
    restart: unless-stopped               # survive host reboot

  exporter:
    image: ekofr/pihole-exporter:v1.0.0   # example monitoring sidecar
    environment:
      PIHOLE_HOSTNAME: pihole             # reach pihole via bridge DNS, no LAN needed
    networks:
      - internal                          # not exposed to the LAN
    restart: unless-stopped

networks:
  lan:
    driver: macvlan                       # macvlan driver
    driver_opts:
      parent: eth0                        # host NIC (use eth0.20 for VLAN 20 - 802.1q sub-interface)
    ipam:
      config:
        - subnet: 192.168.1.0/24          # real LAN subnet
          gateway: 192.168.1.1            # real router
          ip_range: 192.168.1.192/27      # Docker auto-assign range
  internal:
    driver: bridge                        # ordinary bridge
    internal: true                        # no outside access

secrets:
  pihole_pw:
    file: ./pihole_pw.txt                 # chmod 600, never commit
```
```bash
# Let the HOST reach macvlan containers: create a shim interface on the same parent
sudo ip link add macvlan-shim link eth0 type macvlan mode bridge   # virtual NIC on eth0
sudo ip addr add 192.168.1.250/32 dev macvlan-shim                 # unused host-side IP
sudo ip link set macvlan-shim up                                   # bring it up
sudo ip route add 192.168.1.192/27 dev macvlan-shim                # route container range via shim
# Not persistent: add to netplan / systemd-networkd for reboot survival
```

---

## 🟠 My Stack Integration
For a typical Node.js/FastAPI + React + Nginx stack on one VPS or EC2 you should **not** use macvlan; use a custom bridge with Nginx publishing 80/443. Macvlan fits on an **on-prem** box where, say, a FastAPI inference service must be reachable on a dedicated LAN IP, or a monitoring agent must sit on the office network.

```yaml
# Only if the host is on-prem: give FastAPI its own LAN IP, Nginx stays on bridge
services:
  fastapi:
    image: myrepo/fastapi:1.0.0           # example image
    networks:
      lan:
        ipv4_address: 192.168.1.210       # clients call http://192.168.1.210:8000
networks:
  lan:
    external: true                        # created once with docker network create -d macvlan ...
```
Security: macvlan bypasses the host's iptables NAT rules and Docker's published-port firewalling, so the container is exposed to the whole LAN. Put firewalling on the router/switch, use VLANs, and enable promiscuous mode only where the hypervisor requires it. Not run locally (no Docker daemon here); syntax checked only.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Picking a container IP inside the router's DHCP pool.
✅ Correct: Reserve a range (`--ip-range`) that DHCP never hands out.

❌ Mistake 2: Expecting the host to curl its own macvlan container.
✅ Correct: Use a second device, or add a macvlan shim interface on the host.

❌ Mistake 3: Using macvlan on EC2, VirtualBox or a cloud VPS and wondering why traffic dies.
✅ Correct: Clouds/hypervisors filter unknown MACs; use bridge/ipvlan or enable promiscuous mode where allowed.

❌ Mistake 4: Using `-p 8080:80` with macvlan.
✅ Correct: Ports are not mapped; connect directly to the container IP and its real port.

---

## 🧠 Tricky Interview Question
Your container on macvlan can ping the router and other LAN PCs, but `ping` from the Docker host to the container fails. Is the container broken?

Answer: No. The Linux kernel does not allow a parent interface to talk to its own macvlan sub-interfaces, by design (traffic is isolated at L2). Fix by creating a macvlan shim interface on the host in bridge mode with a route to the container range, or run the test from another machine. Alternatively use **ipvlan L3** or a bridge if host-to-container access is required.

---

## ⚫ Interview Questions + Answers

Q1: What is macvlan?
A1: A Docker network driver that assigns each container a unique MAC and an IP on the physical network, making it a first-class LAN citizen without NAT.

Q2: Macvlan vs ipvlan?
A2: Macvlan gives each container a distinct MAC. Ipvlan shares the parent's MAC and differentiates by IP, which helps when switches or clouds limit MAC counts. Ipvlan also has an L3 mode.

Q3: Why can't the host reach macvlan containers?
A3: Kernel isolation between the parent NIC and its macvlan children. Use a shim interface.

Q4: How do you use VLANs with macvlan?
A4: Set `parent=eth0.20` (802.1q sub-interface); containers then sit on VLAN 20.

Q5: Drawbacks?
A5: Needs promiscuous mode/MAC allowance, can exhaust switch MAC tables, no port publishing, no built-in isolation from LAN, and usually unsupported on public clouds.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Legacy or network appliances need a real LAN IP
- You need DNS/DHCP/SNMP/VoIP style services on standard ports
- You want to skip NAT for lower latency on-prem

❌ Avoid when:
- Running on AWS/most VPS (MAC filtering)
- You need host-to-container traffic without extra setup
- You want Docker's built-in port filtering/isolation (use bridge)

---

## 📊 Visual Diagram
```
        LAN 192.168.1.0/24  (router 192.168.1.1)
 ---------+----------------+------------------+---------
          |                |                  |
     [Laptop]        [Docker host]     [Pi-hole container]
   192.168.1.20      192.168.1.10       192.168.1.53
                      eth0 (parent)     MAC: 02:42:c0:a8:01:35
                         |                   ^
                         +--- macvlan -------+
   Host --X--> container (blocked)   Laptop ----> container (OK)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Macvlan | Driver giving containers their own MAC | हर container को अपना MAC देने वाला driver |
| Parent | Physical NIC used as base | आधार physical NIC |
| Promiscuous mode | NIC accepts frames for other MACs | NIC दूसरे MACs के frames भी लेता है |
| ipvlan | Like macvlan but shared MAC | Macvlan जैसा पर MAC साझा |
| 802.1q | VLAN tagging standard | VLAN tag करने का standard |
| Shim | Host-side macvlan interface for access | Host से access के लिए extra interface |

---

## ⚡ 3-Line Summary
English: Macvlan puts containers directly on your physical LAN with own MAC and IP.
English: No NAT or port mapping, but host cannot reach them without a shim.
English: Great on-prem for legacy/network services; usually unsupported on cloud VPS.

Hindi: Macvlan containers को सीधे आपके physical LAN पर अपने MAC और IP के साथ रखता है।
Hindi: NAT/port mapping नहीं होता, पर host बिना shim के उन तक नहीं पहुँचता।
Hindi: On-prem legacy/network services के लिए बढ़िया; cloud VPS पर आम तौर पर unsupported।

---

## ➡️ Next Topic
**172. Custom Bridge Network** - the everyday, most used network for Compose stacks and name-based discovery on a single host.
