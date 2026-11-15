# VPC / VNet Cheatsheet: AWS VPC and Azure VNet
# हिंदी में: नेटवर्क की बुनियाद, यानी VPC, सबनेट, रूटिंग, NAT, फ़ायरवॉल, peering और private endpoints

> Source: notes 023-030, 145, 205-207, 213, 216-217, 289, 306. Prices "approximate — check current docs".

---

## 1. Layout at a glance

```
Region ap-south-1
 VPC 10.0.0.0/16  (spans all AZs)
  ├── Public subnet  10.0.1.0/24 (AZ-a) -> route 0.0.0.0/0 -> IGW
  ├── Private subnet 10.0.11.0/24 (AZ-a) -> route 0.0.0.0/0 -> NAT
  └── Security Groups / NACLs filter traffic
Default VPC per region: 172.31.0.0/16

Azure: Subscription -> Resource Group -> VNet 10.0.0.0/16 (regional)
   |-- subnet web 10.0.1.0/24 [NSG]
   |-- subnet app 10.0.2.0/24 [NSG]
   |-- subnet db  10.0.3.0/24 [NSG]
```
- हिंदी: VPC/VNet क्लाउड में आपका अपना प्राइवेट नेटवर्क है; दोनों regional हैं।

---

## 2. AWS vs Azure side by side

| Feature | AWS | Azure |
|---------|-----|-------|
| Network | VPC (regional) | VNet (regional) |
| Subnet scope | One AZ | Whole region (spans zones) |
| Default network | Default VPC | None by default |
| Public vs private | Route to IGW decides | Public IP + NSG/route decide; default outbound access being phased out (use NAT Gateway, check docs) |
| Reserved IPs | 5 per subnet | 5 per subnet |
| Instance firewall | Security Group (stateful, allow-only) | NSG (stateful, allow+deny, priority) |
| Subnet firewall | NACL (stateless, ordered, allow+deny) | NSG on subnet |
| Outbound only | NAT Gateway (zonal) / egress-only IGW (IPv6) | NAT Gateway (attached to subnet) |
| Route control | Route tables per subnet | UDR route table per subnet |
| Peering | VPC Peering (routes manual); Transit Gateway | VNet Peering (routes automatic; global peering cross-region); Virtual WAN |
| Private PaaS access | Interface endpoint (PrivateLink); Gateway endpoint for S3/DynamoDB (free) | Private Endpoint; Service Endpoint (free) |
| Flow logs | VPC Flow Logs | NSG / VNet Flow Logs (NSG flow log retirement announced, check docs) |
| Admin access | SSM Session Manager | Azure Bastion |
| Cost | VPC free; NAT, endpoints, transfer paid | VNet free; NAT GW, peering transfer paid |

---

## 3. CIDR sizing examples

Formula: total addresses = 2^(32 - prefix). Both clouds reserve 5 per subnet, so usable = total - 5 (derived from the notes' "5 reserved IPs").
AWS IPv4 VPC CIDR must be between /16 (largest) and /28 (smallest).

| CIDR | Total | Usable (minus 5) | Typical use in notes |
|------|-------|------------------|----------------------|
| /16 | 65,536 | 65,531 | whole VPC/VNet, e.g. 10.0.0.0/16 |
| /20 | 4,096 | 4,091 | derived example, bigger subnet |
| /24 | 256 | 251 | one subnet, e.g. 10.0.1.0/24 |
| /28 | 16 | 11 | smallest allowed |

- Carving /24s from a /16: 10.0.1.0/24 public AZ-a, 10.0.2.0/24 public AZ-b, 10.0.11.0/24 private AZ-a, 10.0.12.0/24 private AZ-b.
- Terraform helper: `cidrsubnet("10.20.0.0/16", 8, n)` gives the n-th /24 (public 0,1; private 10,11; isolated 20,21).
- Peered/connected networks must NOT overlap (VPC-A 10.0.0.0/16 with VPC-B 10.1.0.0/16 works).
- Azure reserved subnet names: GatewaySubnet, AzureFirewallSubnet, AzureBastionSubnet.
- हिंदी: हर सबनेट में 5 IP आरक्षित रहते हैं, इसलिए /24 में 251 उपयोगी IP मिलते हैं।

```bash
# VPC and subnets (notes 023-024)
VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
  --query 'Vpc.VpcId' --output text)
aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-hostnames
PUB=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 \
  --availability-zone ap-south-1a --query Subnet.SubnetId --output text)
PRIV=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.11.0/24 \
  --availability-zone ap-south-1a --query Subnet.SubnetId --output text)
aws ec2 modify-subnet-attribute --subnet-id $PUB --map-public-ip-on-launch
```

```bash
# Azure VNet and subnets (note 205)
az network vnet create -g rg-demo -n vnet-prod -l centralindia \
  --address-prefixes 10.0.0.0/16 \
  --subnet-name web --subnet-prefixes 10.0.1.0/24
az network vnet subnet create -g rg-demo --vnet-name vnet-prod \
  -n app --address-prefixes 10.0.2.0/24
```

---

## 4. Internet Gateway, route tables, NAT

- **IGW** — one per VPC, free (data transfer out billed). Public subnet = `0.0.0.0/0 -> igw`. | हिंदी: IGW दोनों तरफ का इंटरनेट देता है।
- **Route tables** — `local` route (VPC CIDR) cannot be removed; longest-prefix match wins; each subnet has one RT (else main RT).
- **NAT Gateway** — sits in a PUBLIC subnet with an Elastic IP; private RT points `0.0.0.0/0 -> nat`; one per AZ for HA. | हिंदी: NAT private सबनेट को सिर्फ़ बाहर जाने देता है।
- **NAT bill high?** — find top talkers with Flow Logs, add S3/DynamoDB gateway endpoints (free) and interface endpoints (ECR, Secrets Manager), keep traffic same-AZ.
- Azure: system routes + UDR; "Virtual appliance" next hop forces traffic through a firewall.

```
Public RT:   10.0.0.0/16 -> local ; 0.0.0.0/0 -> igw-xxx
Private RT:  10.0.0.0/16 -> local ; 0.0.0.0/0 -> nat-xxx ; 10.1.0.0/16 -> pcx-xxx
```

```bash
# IGW + public route; NAT GW + private route (notes 025-026)
IGW=$(aws ec2 create-internet-gateway --query InternetGateway.InternetGatewayId --output text)
aws ec2 attach-internet-gateway --internet-gateway-id $IGW --vpc-id $VPC_ID
aws ec2 create-route --route-table-id $RTB_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW

EIP=$(aws ec2 allocate-address --domain vpc --query AllocationId --output text)
NAT=$(aws ec2 create-nat-gateway --subnet-id $PUB_SUBNET --allocation-id $EIP \
  --query NatGateway.NatGatewayId --output text)
aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT
aws ec2 create-route --route-table-id $PRIV_RTB \
  --destination-cidr-block 0.0.0.0/0 --nat-gateway-id $NAT
```

---

## 5. Security Groups, NACLs, NSGs

```
Internet -> [ALB SG: 443 from 0.0.0.0/0]
              -> [App SG: 3000 from ALB SG]
                   -> [DB SG: 5432 from App SG]
Default SG: all inbound denied, outbound allowed. Rules evaluated together.
NACL: lowest rule number first, first match wins, stateless, "*" = deny.
      Custom NACL denies all until rules are added; return traffic needs ephemeral 1024-65535.
NSG: priority 100..4096 (lowest first), defaults at 65000+: allow VNet-to-VNet,
     allow LB probes, deny other inbound, allow all outbound. Stateful.
```
- Multiple SGs on one instance: rules are a union. Subnet NSG and NIC NSG both apply; both must allow.
- NSG (free L3/L4) vs Azure Firewall (central L3-L7, FQDN filtering, threat intel).
- Missing ephemeral ports on a NACL: site works for some clients but connections hang.
- Group by role: AWS references SG ids; Azure uses Application Security Groups.
- हिंदी: SG स्टेटफुल और सिर्फ़ allow; NACL स्टेटलेस और allow+deny।

```bash
# SG chain (note 027)
aws ec2 authorize-security-group-ingress --group-id $ALB_SG \
  --protocol tcp --port 443 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $APP_SG \
  --protocol tcp --port 3000 --source-group $ALB_SG
aws ec2 authorize-security-group-ingress --group-id $APP_SG \
  --protocol tcp --port 22 --cidr 203.0.113.10/32
```

```bash
# NACL: block a bad IP, allow HTTPS in, ephemeral out (note 028)
aws ec2 create-network-acl-entry --network-acl-id $NACL --ingress --rule-number 90 \
  --protocol -1 --rule-action deny --cidr-block 198.51.100.7/32
aws ec2 create-network-acl-entry --network-acl-id $NACL --ingress --rule-number 100 \
  --protocol tcp --port-range From=443,To=443 --rule-action allow --cidr-block 0.0.0.0/0
aws ec2 create-network-acl-entry --network-acl-id $NACL --egress --rule-number 100 \
  --protocol tcp --port-range From=1024,To=65535 --rule-action allow --cidr-block 0.0.0.0/0
```

```bash
# Azure NSG (note 207)
az network nsg create -g rg-demo -n nsg-web
az network nsg rule create -g rg-demo --nsg-name nsg-web -n allow-https \
  --priority 100 --direction Inbound --access Allow --protocol Tcp \
  --source-address-prefixes Internet --destination-port-ranges 443
az network vnet subnet update -g rg-demo --vnet-name vnet-prod -n web \
  --network-security-group nsg-web
```

---

## 6. Peering and hub-and-spoke

- Both clouds: peering is private, 1:1, **non-transitive**, CIDRs must not overlap.
- AWS: request, accept, then add routes on BOTH sides. Azure: create peering in BOTH directions (routes automatic).
- Full mesh of n VPCs = n(n-1)/2 peerings (10 VPCs = 45): use Transit Gateway (AWS) or Virtual WAN / hub VNet (Azure).
- Azure hub-and-spoke: hub holds Firewall/VPN/DNS; spokes peer to hub with UDRs through the firewall; "allow gateway transit" on hub, "use remote gateways" on spokes.
- TGW costs hourly + per-GB attachment (approximate — check current docs).
- हिंदी: Peering transitive नहीं है, इसलिए कई नेटवर्क हों तो hub चाहिए।

```bash
PCX=$(aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-aaaa1111 --peer-vpc-id vpc-bbbb2222 \
  --query VpcPeeringConnection.VpcPeeringConnectionId --output text)
aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id $PCX
aws ec2 create-route --route-table-id rtb-aaaa1111 \
  --destination-cidr-block 10.1.0.0/16 --vpc-peering-connection-id $PCX
aws ec2 create-route --route-table-id rtb-bbbb2222 \
  --destination-cidr-block 10.0.0.0/16 --vpc-peering-connection-id $PCX
```

```bash
# Azure: both directions (note 213)
az network vnet peering create -g rg-a -n a-to-b --vnet-name vnet-a \
  --remote-vnet "$VNET_B_ID" --allow-vnet-access
az network vnet peering create -g rg-b -n b-to-a --vnet-name vnet-b \
  --remote-vnet "$VNET_A_ID" --allow-vnet-access
```

---

## 7. Private access to PaaS: endpoints

- **AWS gateway endpoint** (S3, DynamoDB) — free, route-table entry, add endpoint policy to limit buckets. **Interface endpoint** (PrivateLink) — per endpoint-hour + GB (approximate — check current docs).
- **Azure Service Endpoint** — free, subnet-to-PaaS over backbone, service keeps its public IP, not reachable from on-prem via endpoint.
- **Azure Private Endpoint** — private IP in your VNet via `privatelink.*` private DNS zone; allows disabling public access and on-prem reach (forward the zone to Azure DNS Private Resolver or a forwarder).
- हिंदी: Private Endpoint को अपना private IP मिलता है, Service Endpoint को नहीं।

```bash
# Service endpoint, deny by default, allow subnet (note 217)
az network vnet subnet update -g rg-demo --vnet-name vnet-prod -n app \
  --service-endpoints Microsoft.Storage
az storage account update -n mystorage123 -g rg-demo --default-action Deny
az storage account network-rule add -g rg-demo --account-name mystorage123 \
  --vnet-name vnet-prod --subnet app
```

---

## 8. Secure VPC blueprint (note 306)

```
Public subnets   : ALB, NAT          (0.0.0.0/0 -> IGW)
Private subnets  : app               (0.0.0.0/0 -> NAT; S3/ECR via endpoints)
Isolated subnets : DB                (no internet route)
SG = stateful SG-to-SG ; NACL = stateless backstop (deny known bad)
Flow Logs -> CloudWatch Logs / S3 ; admin via SSM Session Manager (no SSH port)
```
- No 0.0.0.0/0 ingress except ALB 443; never SSH to the world; do not use the default VPC/SG for production (empty the default SG).
- Compromised instance: Flow Logs/GuardDuty alert, swap to an isolation SG, snapshot for forensics, rotate the role's credentials.
- Flow Logs show metadata only; SG allows but app unreachable: REJECT points to NACL/SG, ACCEPT with no reply points to app or return path. Amazon DNS, metadata and DHCP traffic is not logged.

```bash
aws ec2 create-flow-logs \
  --resource-type VPC --resource-ids vpc-0abc1234 \
  --traffic-type ALL \
  --log-destination-type s3 \
  --log-destination arn:aws:s3:::my-flow-logs-bucket/vpc/
```

---

## 9. Debug: public instance cannot reach the internet
- Route table of that subnet has `0.0.0.0/0 -> IGW`, IGW attached, SG outbound and NACL (ephemeral both ways) allow, OS firewall open.
- हिंदी: पहले रूट, फिर IGW, फिर SG/NACL, आख़िर में OS फ़ायरवॉल देखें।
