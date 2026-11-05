# 121. SBOM — Software Bill of Materials
# हिंदी में: SBOM — Software की सामग्री सूची

---

## 🔵 Simple Definition (English)
An SBOM is a machine readable list of every package, library and version inside your software or Docker image, like the ingredients label on food. Common formats are SPDX and CycloneDX.

## 🔵 सरल परिभाषा (Hindi)
SBOM आपके software या Docker image के अंदर मौजूद हर package, library और version की machine-readable सूची है, बिल्कुल खाने के packet पर लिखी ingredients की तरह। आम formats SPDX और CycloneDX हैं।

---

## 🔴 Problem it Solves
- When a big vulnerability appears (Log4Shell, xz), the first question is "are we using it, and where?". Without a list nobody can answer for hours.
- Customers and regulators (US executive order, EU CRA, enterprise buyers) now ask for SBOMs.
- License compliance: you must know if a GPL library is hidden in your image.
- Rescanning a stored SBOM is faster than re-pulling every image.

## 🔴 यह क्यों बना? (Hindi)
- बड़ी vulnerability (Log4Shell, xz) आने पर पहला सवाल होता है "क्या हम इसे use करते हैं, और कहाँ?"। सूची के बिना घंटों जवाब नहीं मिलता।
- Customers और regulators (US executive order, EU CRA, enterprise buyers) अब SBOM माँगते हैं।
- License compliance: जानना ज़रूरी है कि image में कोई GPL library छुपी तो नहीं।
- सहेजे हुए SBOM को दोबारा scan करना हर image फिर से pull करने से तेज़ है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → A tool (Syft, Trivy, docker buildx, docker sbom/Scout) reads the image layers
Step 2 → It detects OS packages (dpkg, apk, rpm) and language packages (package-lock.json, requirements.txt, go.mod)
Step 3 → It writes a document: name, version, license, hash (and PURL id) for every component
Step 4 → Output format: SPDX JSON or CycloneDX JSON
Step 5 → You store it as a build artifact, or attach it to the image as an attestation in the registry
Step 6 → Later a scanner (Grype, Trivy) reads the SBOM and finds new CVEs without touching the image
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → कोई tool (Syft, Trivy, docker buildx, docker sbom/Scout) image की layers पढ़ता है
Step 2 → OS packages (dpkg, apk, rpm) और language packages (package-lock.json, requirements.txt, go.mod) पहचानता है
Step 3 → हर component का नाम, version, license, hash (और PURL id) एक document में लिखता है
Step 4 → Output format: SPDX JSON या CycloneDX JSON
Step 5 → इसे build artifact की तरह सहेजें, या registry में image से attestation के रूप में जोड़ें
Step 6 → बाद में कोई scanner (Grype, Trivy) SBOM पढ़कर image को छुए बिना नए CVE ढूँढता है
```

---

## 🟡 Real World Example
When a critical OpenSSL bug is announced, a company with 120 services needs to know which ones are affected. Because CI stores an SBOM for every release, the security team runs one command over the SBOM folder and gets the answer in 5 minutes: 9 services. The patched ones are redeployed the same day. A company without SBOMs spends days opening images one by one.

## 🟡 Real Example Hindi mein
जब OpenSSL में critical bug घोषित होता है, 120 services वाली company को जानना होता है कि कौन सी प्रभावित हैं। CI हर release का SBOM सहेजता है, इसलिए security team SBOM folder पर एक command चलाकर 5 मिनट में जवाब पाती है: 9 services। Patch वाली उसी दिन redeploy हो जाती हैं। SBOM के बिना company दिनों तक एक-एक image खोलती रहती है।

---

## 💻 Code / Config Example — Basic
```bash
# --- Option A: Syft (open source, by Anchore) ---
brew install syft                                        # install syft on macOS

syft myorg/api:1.0.0                                     # print a table of packages in the image
syft myorg/api:1.0.0 -o spdx-json=sbom.spdx.json         # write SPDX JSON file
syft myorg/api:1.0.0 -o cyclonedx-json=sbom.cdx.json     # write CycloneDX JSON file

# --- Option B: Trivy can also create an SBOM ---
trivy image --format cyclonedx --output sbom.cdx.json myorg/api:1.0.0

# --- Option C: build with SBOM attached (needs BuildKit / buildx) ---
docker buildx build --sbom=true --provenance=true -t myorg/api:1.0.0 --push .   # SBOM stored as attestation in the registry

# --- Scan an existing SBOM later (no image needed) ---
trivy sbom sbom.cdx.json                                 # vulnerabilities from the SBOM
grype sbom:./sbom.spdx.json                              # same with Grype

# --- Quick look with jq: list package names and versions (CycloneDX) ---
jq -r '.components[] | "\(.name) \(.version)"' sbom.cdx.json | head
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/sbom.yml  (example versions: verify before use)
name: build-sbom-attest                        # workflow name
on:
  push:
    tags: ['v*']                               # run on release tags like v1.2.0
permissions:
  contents: read                               # read the repo
  packages: write                              # push to GHCR
  id-token: write                              # needed for keyless signing/attestation
  attestations: write                          # needed by actions/attest-build-provenance
jobs:
  sbom:
    runs-on: ubuntu-latest                     # hosted runner
    steps:
      - uses: actions/checkout@v4              # get source
      - uses: docker/setup-buildx-action@v3    # buildx for attestations
      - uses: docker/login-action@v3           # log in to GHCR
        with:
          registry: ghcr.io                    # registry host
          username: ${{ github.actor }}        # the user who triggered the run
          password: ${{ secrets.GITHUB_TOKEN }}# built-in token with packages:write
      - name: Build and push with SBOM + provenance
        id: build                              # id so we can read the digest
        uses: docker/build-push-action@v6
        with:
          context: ./api                       # build context
          push: true                           # push to the registry
          tags: ghcr.io/${{ github.repository }}/api:${{ github.ref_name }}   # release tag
          sbom: true                           # create SBOM attestation
          provenance: mode=max                 # create detailed provenance
      - name: Generate standalone SBOM file
        uses: anchore/sbom-action@v0           # runs Syft
        with:
          image: ghcr.io/${{ github.repository }}/api:${{ github.ref_name }}   # image to inspect
          format: cyclonedx-json               # output format
          output-file: sbom.cdx.json           # file name
      - name: Keep SBOM with the release
        uses: actions/upload-artifact@v4       # save for later audits
        with:
          name: sbom-${{ github.ref_name }}    # artifact name
          path: sbom.cdx.json                  # file to keep
          retention-days: 365                  # keep one year (check your policy)
```

---

## 🟠 My Stack Integration
- **Node.js:** SBOM includes every transitive npm package from `package-lock.json`. Always commit the lock file and use `npm ci`, otherwise versions in SBOM differ from what you built.
- **FastAPI:** pin dependencies (`requirements.txt` with hashes, or `uv`/`poetry` lock) so the SBOM is accurate.
- **React:** build-time node_modules are not in the final Nginx image; the SBOM of the runtime image lists only Nginx and OS packages. Generate a second SBOM from the repo (`syft dir:.`) if you want the build dependencies.
- **VPS / AWS:** store SBOM next to the image in ECR/GHCR (attestation) or in S3 by release tag.

```bash
# Quick answer on the VPS: "is openssl 3.0.x running in any of my containers?"
for c in $(docker ps --format '{{.Image}}' | sort -u); do   # unique images that are running now
  echo "== $c"                                              # print image name
  syft "$c" -q -o json | jq -r '.artifacts[] | select(.name=="openssl") | .version'   # openssl version, if present
done
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Generating an SBOM from source only and assuming it matches the image.
✅ Correct: Generate it from the final built image; OS packages and base image layers appear only there.

❌ Mistake 2: Creating SBOMs and never storing or using them.
✅ Correct: Keep them per release (artifact/attestation) and rescan them regularly.

❌ Mistake 3: Treating the SBOM as a vulnerability report.
✅ Correct: It is an inventory. A scanner combines it with CVE data to find vulnerabilities.

❌ Mistake 4: Publishing an SBOM that exposes internal package names or paths publicly by accident.
✅ Correct: Review before sharing outside the company; share via customer portal under NDA if needed.

---

## 🧠 Tricky Interview Question
Your SBOM lists `lodash 4.17.20`, but a scanner says the running container has `4.17.21`. Which is right?

Answer: Check how both were produced. The SBOM may have been generated from an older commit, from source instead of the final image, or before an `npm install` changed the lock file. The truth is what the running image digest contains, so regenerate the SBOM from that digest (`syft myorg/api@sha256:...`). This is why SBOMs must be tied to the image digest, not just to a tag.

---

## ⚫ Interview Questions + Answers

Q1: What is an SBOM and why do we need it?
A1: A complete inventory of components in software. It speeds up vulnerability response, license checks and compliance.

Q2: SPDX vs CycloneDX?
A2: Both are standard formats. SPDX (Linux Foundation) started with licensing; CycloneDX (OWASP) started with security use cases. Most tools support both.

Q3: How do you create an SBOM for a Docker image?
A3: `syft image -o cyclonedx-json`, `trivy image --format cyclonedx`, or `docker buildx build --sbom=true`.

Q4: What is the difference between SBOM and provenance?
A4: SBOM says WHAT is inside. Provenance says HOW, WHERE and FROM WHAT SOURCE it was built.

Q5: Where would you store SBOMs?
A5: As registry attestations tied to the image digest, plus as CI artifacts or in object storage (S3) organised by release.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Customers, auditors or regulators require it.
- You run many services and need fast "are we affected?" answers.
- You want license compliance checks.

❌ Avoid when:
- It is created but nobody owns the process of reading it. An unused SBOM adds nothing.
- Used as the only security control.

---

## 📊 Visual Diagram
```
   Source + lock files          Base image (node:20-alpine)
          \                           /
           v                         v
            +-----------------------+
            |   Built Docker image  |  digest sha256:abc...
            +-----------------------+
                       |  Syft / Trivy / buildx
                       v
            +-----------------------+
            |  SBOM (SPDX/CycloneDX)|  express 4.19.2, openssl 3.0.15, ...
            +-----------------------+
              |          |          |
              v          v          v
          CVE scan   License     Stored as attestation
          (Grype)    check       in GHCR/ECR + S3 archive
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SBOM | List of all components in software | software की पूरी सामग्री सूची |
| SPDX | SBOM standard (Linux Foundation) | SBOM का एक standard format |
| CycloneDX | SBOM standard (OWASP) | SBOM का दूसरा standard format |
| PURL | Package URL, unique package id | package की unique पहचान |
| Attestation | Signed claim attached to an image | image से जुड़ा प्रमाणित दावा |
| Transitive dependency | Dependency of a dependency | निर्भरता की निर्भरता |

---

## ⚡ 3-Line Summary
English: An SBOM is the ingredient list of your image in SPDX or CycloneDX format.
English: Generate it from the final image with Syft, Trivy or buildx and store it per release.
English: It lets you answer "are we affected?" quickly and supports compliance.
Hindi: SBOM आपकी image की ingredient सूची है, SPDX या CycloneDX format में।
Hindi: इसे final image से Syft, Trivy या buildx से बनाएँ और हर release के साथ सहेजें।
Hindi: इससे "क्या हम प्रभावित हैं?" का जवाब जल्दी मिलता है और compliance में मदद होती है।

---

## ➡️ Next Topic
**122. Image Signing** — an SBOM says what is inside; signing proves WHO built the image and that nobody changed it.
