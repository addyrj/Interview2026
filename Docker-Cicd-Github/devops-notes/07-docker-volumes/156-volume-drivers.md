---

# 156. Volume Drivers
# हिंदी में: Volume Drivers (Volume कहाँ और कैसे रखा जाए)

---

## 🔵 Simple Definition (English)
A **volume driver** is a plugin that decides where and how a volume's data is stored. The built-in `local` driver stores data on the host disk, and it can also mount NFS, CIFS or tmpfs through options. Third-party plugins (REX-Ray, Portworx, Azure File, rclone, NetApp Trident) connect volumes to cloud or network storage so containers on different hosts can reach the same data.

## 🔵 सरल परिभाषा (Hindi)
**Volume driver** एक plugin है जो तय करता है कि volume का data कहाँ और कैसे रखा जाएगा। Built-in `local` driver data host disk पर रखता है, और options से NFS, CIFS या tmpfs भी mount कर सकता है। Third-party plugins (REX-Ray, Portworx, Azure File, rclone, NetApp Trident) volumes को cloud या network storage से जोड़ते हैं ताकि अलग-अलग hosts के containers एक ही data तक पहुँच सकें।

---

## 🔴 Problem it Solves
Local volumes live on one machine. If the VPS dies, the data dies with it; if the container moves to another host, the data does not follow. Teams need shared uploads across several app servers, storage on a NAS, encrypted or replicated storage, or snapshots. Volume drivers let the same `-v name:/path` syntax work with remote or specialised storage without changing the container image.

## 🔴 यह क्यों बना? (Hindi)
Local volumes एक ही machine पर रहते हैं। VPS मरे तो data भी साथ मरता है; container दूसरे host पर जाए तो data साथ नहीं जाता। Teams को कई app servers में shared uploads, NAS पर storage, encrypted या replicated storage, या snapshots चाहिए। Volume drivers वही `-v name:/path` syntax remote या विशेष storage के साथ चलने देते हैं, container image बदले बिना।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose a driver: local (built in) or install a plugin: docker plugin install <name>
Step 2 → Create the volume with it:  docker volume create -d <driver> -o key=value myvol
Step 3 → Docker stores driver name and options in the volume metadata
Step 4 → On container start dockerd calls the driver: Create -> Mount (returns a host path)
Step 5 → Docker bind-mounts that path into the container
Step 6 → On stop the driver Unmount is called; data stays in the backend (NFS server, S3, EBS)
Step 7 → docker volume rm calls the driver Remove (may or may not delete backend data)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Driver चुनो: local (built-in) या plugin install करो: docker plugin install <name>
Step 2 → उससे volume बनाओ:  docker volume create -d <driver> -o key=value myvol
Step 3 → Docker driver का नाम और options volume metadata में रखता है
Step 4 → Container start पर dockerd driver को बुलाता है: Create -> Mount (host path लौटता है)
Step 5 → Docker उस path को container में bind-mount करता है
Step 6 → Stop पर driver का Unmount चलता है; data backend (NFS server, S3, EBS) में रहता है
Step 7 → docker volume rm driver का Remove बुलाता है (backend data हटे या नहीं, driver पर निर्भर)
```

---

## 🟡 Real World Example
A media-publishing site runs three API servers behind a load balancer. Users upload images that must be visible on every server. With local volumes, an image uploaded through server A returned 404 on server B. The team created an NFS volume (`type=nfs`) pointing to a small storage box in the same private network, mounted into all three API containers. Uploads became visible everywhere. Later, they moved images to S3 and kept NFS only for legacy files, because NFS was a single point of failure and slow for many small files.

## 🟡 Real Example Hindi mein
एक media-publishing site के तीन API servers load balancer के पीछे हैं। Users की upload की हुई images हर server पर दिखनी चाहिए। Local volumes के साथ server A से upload हुई image server B पर 404 देती थी। Team ने उसी private network के एक storage box की ओर NFS volume (`type=nfs`) बनाया और तीनों API containers में mount किया। Uploads हर जगह दिखने लगे। बाद में उन्होंने images S3 में रखीं और NFS सिर्फ़ पुरानी files के लिए रखा, क्योंकि NFS single point of failure था और छोटी files के लिए धीमा।

---

## 💻 Code / Config Example — Basic

```bash
# Default driver is "local": these two commands are equivalent
docker volume create appdata
docker volume create --driver local appdata2
# both store data under /var/lib/docker/volumes on this host

# Show the driver and options of a volume
docker volume inspect appdata --format '{{.Driver}} {{.Options}}'
# prints: local map[]

# local driver with NFS: mount a remote export as a volume
docker volume create \
  --driver local \
  --opt type=nfs \
  --opt o=addr=10.0.0.20,rw,nfsvers=4 \
  --opt device=:/exports/uploads \
  nfs-uploads
# type=nfs tells the kernel mount type; o= are mount options (addr is the server);
# device is the export path on the NFS server (leading colon for NFS syntax)
# requires NFS client utilities (nfs-common) installed on the Docker host

# Use it like any other volume
docker run --rm -v nfs-uploads:/data alpine:3.20 ls /data
# lists the files stored on the NFS server

# local driver with tmpfs: a volume that lives in RAM
docker volume create --driver local \
  --opt type=tmpfs --opt device=tmpfs --opt o=size=100m,uid=1000 ramvol
# type=tmpfs with device=tmpfs makes a named RAM volume; o sets size and owner

# local driver bind-style volume pointing at a specific host directory
docker volume create --driver local \
  --opt type=none --opt o=bind --opt device=/srv/data/pg pgbind
# lets you keep a NAMED volume while choosing the host location (e.g. a big mounted disk)
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml: volumes backed by NFS and by a custom disk path
services:
  api:
    image: ghcr.io/acme/node-api:1.8.3            # Node.js API (example tag)
    deploy:
      replicas: 2                                 # honoured in Swarm; use `docker compose up --scale` otherwise
    volumes:
      - uploads:/app/uploads                      # shared NFS-backed uploads
    restart: unless-stopped                       # restart after reboot or crash

  db:
    image: postgres:16-alpine                     # database image (example tag)
    volumes:
      - pgdata:/var/lib/postgresql/data           # data on a dedicated big disk
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pass   # secret file for the password
    secrets:
      - db_pass                                   # attach the secret

volumes:
  uploads:
    driver: local                                 # built-in driver doing an NFS mount
    driver_opts:
      type: nfs                                   # filesystem type
      o: "addr=10.0.0.20,rw,nfsvers=4,hard"       # server address and mount options (hard = retry forever)
      device: ":/exports/uploads"                 # remote export path
  pgdata:
    driver: local                                 # still local driver
    driver_opts:
      type: none                                  # no filesystem type: use bind semantics
      o: bind                                     # bind-mount an existing directory
      device: /mnt/data-disk/postgres             # path on the extra EBS/VPS disk (must exist)

secrets:
  db_pass:
    file: ./secrets/db_pass.txt                   # keep out of version control
```

```bash
# Third-party plugin workflow (example: rclone volume plugin to S3-compatible storage)
# NOTE: plugin names, settings and options are plugin specific: read its README first

docker plugin install rclone/docker-volume-rclone:amd64 --grant-all-permissions --alias rclone
# installs a managed plugin; --alias gives it the short name "rclone" used as the driver
# --grant-all-permissions skips the prompt: review requested permissions in real use

docker volume create -d rclone -o type=s3 -o s3-provider=AWS -o path=my-bucket/uploads s3vol
# creates a volume through the plugin; -o options are passed to the plugin untouched
# (option names above are illustrative; credentials usually come from plugin config or env)

docker plugin ls
# lists installed plugins and whether they are enabled
```

Compose YAML parsed and shell checked with `bash -n`; the NFS and plugin steps were not run (no Docker daemon, NFS server or S3 here). Plugin options are examples; verify against the plugin documentation.

---

## 🟠 My Stack Integration
Single VPS: the default `local` driver is enough, optionally with `type=none,o=bind,device=...` to place data on a bigger attached disk. Several VPS or EC2 instances sharing uploads: NFS (EFS on AWS) through the `local` driver options: EFS mount target + `nfsvers=4.1` and the security group allowing port 2049. ECS: define EFS volumes in the task definition rather than Docker plugins. For Postgres, avoid network filesystems: use RDS or a local fast disk with replication. Node.js and FastAPI only see a normal folder, so no code changes are needed.

```bash
# AWS EFS as a Docker volume on an EC2 host (mount target DNS from the EFS console)
docker volume create --driver local \
  --opt type=nfs \
  --opt o=addr=fs-0123456789abcdef0.efs.ap-south-1.amazonaws.com,nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 \
  --opt device=:/ \
  efs-uploads
# addr is the example EFS DNS name; options follow AWS recommended NFS client settings
# the EC2 security group must allow NFS (TCP 2049) to the EFS mount target
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting a database on NFS or a FUSE/S3 plugin volume.
✅ Correct: Databases need low-latency block storage with proper `fsync` and locking. Use local SSD/EBS, or a managed database.

❌ Mistake 2: Creating an NFS volume but forgetting the NFS client (`nfs-common`) on the Docker host, or the firewall rule.
✅ Correct: Install the client, allow port 2049, and test with a manual `mount -t nfs`.

❌ Mistake 3: Trusting a plugin blindly with `--grant-all-permissions`.
✅ Correct: Plugins run with high privileges. Use maintained plugins, review permissions, and pin versions.

❌ Mistake 4: Assuming `docker volume rm` always deletes backend data, or never does.
✅ Correct: It depends on the driver. Read the plugin docs and keep independent backups.

---

## 🧠 Tricky Interview Question
You defined an NFS-backed volume in Compose with `type: nfs`. After correcting a typo in `device:` and running `docker compose up -d` again, the container still tries the old path. Why?

Answer: Volume driver options are stored when the volume is created; Docker does not update an existing volume if the Compose file changes (Compose even warns that the volume exists with different options in newer versions). The old definition persists. You must stop the containers, remove the volume (`docker volume rm`, safe here because the data lives on the NFS server, not in Docker) and let Compose recreate it. This differs from images and services, which Compose does recreate on config change.

---

## ⚫ Interview Questions + Answers

Q1: What is the default volume driver?
A1: `local`, which stores data on the Docker host in `/var/lib/docker/volumes`.

Q2: How can the `local` driver use network storage?
A2: Through `--opt type=nfs` (or `cifs`), `o=` mount options and `device=` pointing to the remote path; the host kernel does the actual mount.

Q3: Volume driver vs storage driver?
A3: Storage driver (overlay2) manages image and container layers. Volume driver manages the lifecycle and location of volumes. They are unrelated.

Q4: How do you manage Docker plugins?
A4: `docker plugin install | ls | enable | disable | rm | inspect`.

Q5: What are the main risks of remote volume drivers?
A5: Latency, network partitions causing hangs (`hard` mounts block), single point of failure, security (credentials, NFS exports open to the network), and file locking differences.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several hosts need the same files (uploads, media, shared assets)
- Data must live on a specific bigger disk or NAS
- You need snapshots or encryption provided by a storage plugin

❌ Avoid when:
- Single host with a normal disk (use plain local volumes)
- Latency-sensitive databases
- You cannot maintain the storage backend or plugin lifecycle

---

## 📊 Visual Diagram
```
   container ──► -v uploads:/app/uploads
                       │
                       ▼
                 dockerd + VOLUME DRIVER
        ┌──────────────┼───────────────────────────┐
        ▼              ▼                           ▼
   local (disk)   local + NFS/CIFS opts       3rd-party plugin
   /var/lib/...   kernel mounts remote        (rclone, Portworx,
                  share on the host            Trident, REX-Ray)
        │              │                           │
   host SSD/EBS   NFS server / AWS EFS        S3 / SAN / cloud disks
   single host    shared by many hosts        driver defines semantics
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Volume driver | Plugin controlling volume storage | Volume storage नियंत्रित करने वाला plugin |
| local driver | Built-in host-disk driver | Built-in host-disk driver |
| NFS | Network File System | Network File System |
| EFS | AWS managed NFS | AWS का managed NFS |
| driver_opts | Options passed to the driver | Driver को दिए जाने वाले options |
| Managed plugin | Plugin installed via docker plugin | docker plugin से install किया plugin |

---

## ⚡ 3-Line Summary
English: Volume drivers choose where volume data lives: the default `local` driver for the host disk (or NFS via options), plugins for cloud and network storage. Use shared drivers for uploads across hosts, not for databases. Options are fixed at creation, so recreate the volume to change them.
Hindi: Volume drivers तय करते हैं कि volume का data कहाँ रहे: host disk के लिए default `local` driver (या options से NFS), cloud और network storage के लिए plugins। Hosts के बीच uploads के लिए shared drivers लो, databases के लिए नहीं। Options बनाते समय तय हो जाते हैं, इसलिए बदलने को volume दोबारा बनाओ।

---

## ➡️ Next Topic
**157. docker volume Commands**: the full CLI toolkit (`create`, `ls`, `inspect`, `rm`, `prune`) for managing everything you have learned in this section.

---
