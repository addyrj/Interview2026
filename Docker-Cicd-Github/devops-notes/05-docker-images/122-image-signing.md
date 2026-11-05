# 122. Image Signing
# हिंदी में: Image Signing (image पर डिजिटल हस्ताक्षर)

---

## 🔵 Simple Definition (English)
Image signing attaches a cryptographic signature to an image digest, proving that a specific person or pipeline built it and that it was not changed afterwards. Cosign (Sigstore project) is the most common tool today.

## 🔵 सरल परिभाषा (Hindi)
Image signing, image के digest पर एक cryptographic signature लगाता है, जो साबित करता है कि इसे किस व्यक्ति या pipeline ने बनाया और बाद में इसमें बदलाव नहीं हुआ। आजकल सबसे आम tool Cosign (Sigstore project) है।

---

## 🔴 Problem it Solves
- A registry account can be hacked, or someone can push a malicious `myorg/api:1.0.0` over yours (tag overwrite).
- `docker pull` by default only checks the content hash that the registry itself reports; it cannot know who published it.
- Supply chain attacks (SolarWinds style) insert code between build and deploy.
- You need proof "this image came from MY GitHub Actions workflow on the main branch".

## 🔴 यह क्यों बना? (Hindi)
- Registry account hack हो सकता है, या कोई आपके `myorg/api:1.0.0` पर दुर्भावनापूर्ण image push कर सकता है (tag overwrite)।
- `docker pull` default में सिर्फ वही content hash जाँचता है जो registry खुद बताती है; उसे यह पता नहीं कि publish किसने किया।
- Supply chain attacks (SolarWinds जैसे) build और deploy के बीच code घुसा देते हैं।
- आपको सबूत चाहिए "यह image मेरे GitHub Actions workflow से, main branch से आई है"।

---

## 🟢 How it Works — Step by Step

```
Step 1 → CI builds and pushes image; registry returns the DIGEST (sha256:...)
Step 2 → cosign sign <image>@<digest> creates a signature over that digest
Step 3 → Two key models:
         a) Key pair: you hold cosign.key (private) in a secret store, share cosign.pub
         b) Keyless: GitHub OIDC token -> Fulcio issues a short-lived certificate -> entry in Rekor transparency log
Step 4 → The signature is stored in the SAME registry as an extra artifact (tag sha256-<digest>.sig)
Step 5 → Before deploy: cosign verify checks signature, and (keyless) the identity + issuer
Step 6 → Verification fails -> the deploy (or Kubernetes admission policy) is rejected
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → CI image build और push करता है; registry DIGEST (sha256:...) लौटाती है
Step 2 → cosign sign <image>@<digest> उस digest पर signature बनाता है
Step 3 → दो key models:
         a) Key pair: private cosign.key secret store में, public cosign.pub सबके साथ
         b) Keyless: GitHub OIDC token -> Fulcio छोटी अवधि का certificate देता है -> Rekor transparency log में entry
Step 4 → Signature उसी registry में अतिरिक्त artifact (tag sha256-<digest>.sig) के रूप में रहता है
Step 5 → Deploy से पहले: cosign verify signature जाँचता है, और (keyless में) identity + issuer भी
Step 6 → Verification fail -> deploy (या Kubernetes admission policy) reject
```

---

## 🟡 Real World Example
A company deploys to AWS from GitHub Actions. The pipeline signs every image keylessly. The deploy server runs `cosign verify` with `--certificate-identity` set to the workflow path on `main`. An attacker who stole a Docker Hub token and pushed a backdoored `api:1.4.0` cannot produce a valid signature for that identity, so the server refuses to run it.

## 🟡 Real Example Hindi mein
एक company GitHub Actions से AWS पर deploy करती है। Pipeline हर image पर keyless signature लगाती है। Deploy server `cosign verify` को `main` पर चलने वाले workflow path की `--certificate-identity` के साथ चलाता है। Docker Hub token चुराकर backdoor वाली `api:1.4.0` push करने वाला attacker उस identity की valid signature नहीं बना सकता, इसलिए server उसे चलाने से मना कर देता है।

---

## 💻 Code / Config Example — Basic
```bash
# Install cosign (macOS)
brew install cosign

# Generate a key pair: creates cosign.key (private, password protected) and cosign.pub
cosign generate-key-pair

# Always sign by DIGEST, not by tag (tags can move)
DIGEST=$(docker buildx imagetools inspect myorg/api:1.0.0 --format '{{json .Manifest.Digest}}' | tr -d '"')   # get sha256 digest
cosign sign --key cosign.key myorg/api@"$DIGEST"        # sign; asks for key password

# Verify with the public key
cosign verify --key cosign.pub myorg/api@"$DIGEST"      # prints JSON if valid, error if not

# Sign with an SBOM attached as a signed attestation
cosign attest --key cosign.key --type cyclonedx --predicate sbom.cdx.json myorg/api@"$DIGEST"
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/release-sign.yml  (example versions: verify before use)
name: release-and-sign                         # workflow name
on:
  push:
    branches: [main]                           # sign only images built from main
permissions:
  contents: read                               # read repo
  packages: write                              # push to GHCR
  id-token: write                              # REQUIRED for keyless signing (OIDC token)
jobs:
  release:
    runs-on: ubuntu-latest                     # hosted runner
    steps:
      - uses: actions/checkout@v4              # get source
      - uses: sigstore/cosign-installer@v3     # installs the cosign CLI
      - uses: docker/setup-buildx-action@v3    # buildx
      - uses: docker/login-action@v3           # login to GHCR
        with:
          registry: ghcr.io                    # registry host
          username: ${{ github.actor }}        # triggering user
          password: ${{ secrets.GITHUB_TOKEN }}# built-in token
      - name: Build and push
        id: build                              # lets us read steps.build.outputs.digest
        uses: docker/build-push-action@v6
        with:
          context: ./api                       # Dockerfile folder
          push: true                           # push image
          tags: ghcr.io/${{ github.repository }}/api:${{ github.sha }}   # tag with commit SHA
      - name: Sign image (keyless)
        env:
          IMAGE: ghcr.io/${{ github.repository }}/api       # repo path without tag
          DIGEST: ${{ steps.build.outputs.digest }}         # exact digest just pushed
        run: cosign sign --yes "${IMAGE}@${DIGEST}"         # --yes = no interactive prompt; uses OIDC identity
```

```bash
# On the deploy side: verify the identity of the signer BEFORE running (keyless)
cosign verify \
  --certificate-identity-regexp '^https://github.com/myorg/api/\.github/workflows/release-sign\.yml@refs/heads/main$' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  ghcr.io/myorg/api@sha256:REPLACE_WITH_DIGEST            # fails (non-zero) if signer is not that workflow
```

---

## 🟠 My Stack Integration
- **Node.js / FastAPI / React images:** sign each image in the same workflow that pushes it; use the digest output from `build-push-action`.
- **GHCR / ECR:** cosign works with both; signatures appear as extra tags (`sha256-....sig`). ECR lifecycle rules must NOT delete them.
- **VPS:** add a verify step in the deploy script before `docker compose up -d`. Compose itself does not verify signatures.
- **Kubernetes:** use an admission controller (Kyverno, Sigstore policy-controller) to enforce signatures cluster wide.

```bash
# deploy.sh on the VPS (fragment)
set -euo pipefail                                          # stop on any error
IMAGE="ghcr.io/myorg/api@${DIGEST}"                        # deploy by digest, never by moving tag
cosign verify \
  --certificate-identity-regexp '^https://github.com/myorg/api/' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  "$IMAGE" >/dev/null                                      # abort deploy if signature is invalid
docker pull "$IMAGE"                                       # pull the verified image
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Signing `myorg/api:latest` (a tag).
✅ Correct: Sign the digest; a tag can later point to an unsigned image.

❌ Mistake 2: Committing `cosign.key` to git or leaving it without a strong password.
✅ Correct: Prefer keyless signing; otherwise keep the key in GitHub Secrets/KMS.

❌ Mistake 3: Verifying with only `--certificate-oidc-issuer` and a wildcard identity.
✅ Correct: Pin the exact repository/workflow/branch in `--certificate-identity`, otherwise any GitHub user could pass.

❌ Mistake 4: Signing but never verifying.
✅ Correct: A signature has value only when a deploy gate checks it.

---

## 🧠 Tricky Interview Question
An attacker overwrites tag `api:1.0.0` in your registry with a malicious image. Your pipeline had signed `api:1.0.0`. Does verification catch it?

Answer: If you verify by TAG, cosign resolves the tag to the new digest, finds no signature for that digest, and fails: good. But if you deployed by tag without verifying, nothing stops it. Best practice is to record the digest at build time, sign that digest, and deploy by `@sha256:` so the thing you verified is exactly the thing you run.

---

## ⚫ Interview Questions + Answers

Q1: Why sign images?
A1: To prove origin and integrity, protecting against tag overwrites, compromised registries and supply chain attacks.

Q2: What is keyless signing?
A2: Cosign gets a short-lived certificate for the CI identity (via OIDC) from Fulcio and records the event in the Rekor log, so no long-lived private key exists.

Q3: Where is the signature stored?
A3: In the same OCI registry as an extra artifact linked to the image digest.

Q4: Cosign vs Docker Content Trust?
A4: DCT (Notary v1) is the older Docker-specific system; Cosign (Sigstore) is the modern OCI-native standard with keyless support.

Q5: How do you enforce signatures on Kubernetes?
A5: Use admission policies (Kyverno verifyImages, Sigstore policy-controller, Ratify) that reject unsigned pods.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You release images to production or to customers.
- Multiple people/systems can push to the registry.
- Compliance requires provenance (SLSA).

❌ Avoid when:
- Local throwaway images.
- You will never verify; then spend the effort on scanning and least-privilege tokens first.

---

## 📊 Visual Diagram
```
 GitHub Actions (main branch)
        |  build + push
        v
  +--------------------+       OIDC token        +---------+
  | Registry: image    | <--- cosign sign ---->  | Fulcio  | short-lived cert
  | sha256:abc...      |                         +---------+
  | + abc.sig          |  ---- log entry ---->   +---------+
  +--------------------+                         | Rekor   | public log
        |                                        +---------+
        | docker pull @sha256:abc
        v
  +--------------------+   cosign verify (identity + issuer)
  | VPS / Kubernetes   | -------------------------> OK  -> run
  +--------------------+                            FAIL -> reject
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Digest | Content hash of an image (sha256) | image का content hash |
| Cosign | Tool to sign/verify OCI images | image sign करने का tool |
| Sigstore | Open source signing project | signing का open source project |
| Fulcio | CA issuing short-lived certs | छोटी अवधि के certificate देने वाली CA |
| Rekor | Public transparency log | सार्वजनिक पारदर्शिता log |
| OIDC | Identity token from GitHub | GitHub से मिलने वाला identity token |

---

## ⚡ 3-Line Summary
English: Signing proves who built an image and that it is unchanged.
English: Use Cosign keyless in GitHub Actions and sign the digest, not the tag.
English: Verify identity before deploy, or signing gives no protection.
Hindi: Signing साबित करता है कि image किसने बनाई और वह बदली नहीं गई।
Hindi: GitHub Actions में Cosign keyless use करें और tag नहीं, digest पर sign करें।
Hindi: Deploy से पहले identity verify करें, वरना signing से कोई सुरक्षा नहीं मिलती।

---

## ➡️ Next Topic
**123. Docker Content Trust** — Docker's older built-in signing system (Notary v1), still asked in interviews.
