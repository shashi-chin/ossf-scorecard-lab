# OpenSSF Scorecard Lab (broken on purpose)

[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/shashi-chin/ossf-scorecard-lab/badge)](https://scorecard.dev/viewer/?uri=github.com/shashi-chin/ossf-scorecard-lab)

> **Lab status:** this repository is intentionally misconfigured so **each major Scorecard check fails (or is N/A for a clear reason)**.  
> Use it to study Scorecard, prepare for security / DevSecOps interviews, and practice reading remediation guidance.  
> **Do not copy anti-patterns into production.**

| | |
|---|---|
| Repo | https://github.com/shashi-chin/ossf-scorecard-lab |
| Live viewer | https://scorecard.dev/viewer/?uri=github.com/shashi-chin/ossf-scorecard-lab |
| Scanner workflow | [`.github/workflows/scorecards.yml`](.github/workflows/scorecards.yml) (kept *correct* so publishing still works) |
| Anti-pattern workflow | [`.github/workflows/demo-antipatterns.yml`](.github/workflows/demo-antipatterns.yml) (kept *wrong* on purpose) |

---

## Will Scorecard still matter in the age of AI?

**Yes — more, not less.** AI changes *how fast* code and dependencies appear; Scorecard measures whether the *repository operating system* can absorb that speed safely.

| AI-era pressure | What Scorecard still catches |
| --- | --- |
| Models suggest Actions YAML, Dockerfiles, and package pins at high volume | Dangerous workflows, unpinned actions, overly broad `GITHUB_TOKEN` permissions |
| AI-assisted PRs increase merge velocity | Missing branch protection, missing human review, missing CI on PRs |
| Copilots pull in libraries from memory / outdated training data | Known vulns (`Vulnerabilities`), missing Dependabot/Renovate |
| “Ship the demo” culture skips process docs | No `SECURITY.md`, no license, no signed releases, no packaging path |
| AI code review helps *content* of a diff | Scorecard judges *controls around* the diff (review required? SAST required? fuzzing?) |

**What Scorecard is *not*:** a replacement for SAST/DAST, secret scanning, AI code review, or threat modeling.  
**What it *is*:** a continuous, evidence-based score of supply-chain and repo hygiene — useful for OSS selection, vendor questionnaires, SSDF/SLSA conversations, and interview storytelling (“here’s how I’d raise Branch-Protection from 0→8”).

**Interview one-liner:**  
*“Scorecard doesn’t ask whether AI wrote good code; it asks whether the project can safely accept code — from humans or models — without silent supply-chain failure.”*

---

## How to use this lab (interviews / study)

1. Open the [viewer](https://scorecard.dev/viewer/?uri=github.com/shashi-chin/ossf-scorecard-lab) and expand a failing check.  
2. Jump to that check’s section below — each section has: risk, what it measures, **how this repo fails**, remediation, and an interview prompt.  
3. Mentally reverse the failure: what file would you add/change to earn points?  
4. Optional: download `scorecard-results` from Actions → open `results.json` for raw scores.

**Scoring reminder:** each check is `0–10`, or `-1` / `?` when **Not Applicable** (not enough signal yet — e.g. no PRs / no releases). Aggregate is a weighted blend, not a simple average.

---

## Intentional failure map (this project)

Live snapshot after the “failure classroom” setup (**aggregate 1.0** — confirm on the [viewer](https://scorecard.dev/viewer/?uri=github.com/shashi-chin/ossf-scorecard-lab)).  
“Fail a criterion” ≠ always score `0`: Scorecard uses **tiered / proportional** scoring (e.g. one binary → **9/10** with Warn; mixed CI history → **5/10**).

| Check | Lab score | Failed criterion / evidence in this repo |
| --- | --- | --- |
| Dangerous-Workflow | **0** | `demo-antipatterns.yml`: `pull_request_target` + PR checkout + untrusted `${{ ... }}` |
| Maintained | **0** | Repo &lt; 90 days — “review its contents carefully” |
| Code-Review | **0** | Merges without approvals (`Found 0/N approved changesets`) |
| Branch-Protection | **0** | No ruleset / protection on `main` |
| Binary-Artifacts | **9** | [`bin/demo-helper`](bin/demo-helper) — Warn: binaries present |
| Dependency-Update-Tool | **0** | No Dependabot / Renovate config |
| Token-Permissions | **0** | `permissions: write-all` in anti-pattern workflow |
| Vulnerabilities | **0** | **18** OSV findings from [`package.json`](package.json) / [`package-lock.json`](package-lock.json) + [`requirements.txt`](requirements.txt) |
| SAST | **0** | No CodeQL / Sonar on all commits |
| Fuzzing | **0** | No fuzzer integration |
| Pinned-Dependencies | **4** | Unpinned Actions (`@v4`) + unpinned [`Dockerfile`](Dockerfile) base image |
| Security-Policy | **0** | No `SECURITY.md` |
| CII-Best-Practices | **0** | No Best Practices badge |
| Contributors | **0** | Solo-author lab |
| License | **0** | No `LICENSE` |
| CI-Tests | **5** | 1/2 merged PRs had a check run (no real test suite; proportional score) |
| Packaging | **?** (−1) | No packaging publish workflow |
| Signed-Releases | **0** | [Unsigned release `v0.0.1-unsigned`](https://github.com/shashi-chin/ossf-scorecard-lab/releases/tag/v0.0.1-unsigned) |

The Scorecard Action workflow itself stays pinned + least-privilege so results can still publish to [scorecard.dev](https://scorecard.dev).

---

## Check-by-check study guide

### 1. Dangerous-Workflow — Risk: Critical

**What it measures**  
Whether GitHub Actions avoid patterns that let an attacker run code with the base repo’s privileges (classic “pwn request”).

**Why it matters (AI age)**  
Models happily emit `pull_request_target` + `actions/checkout` of the PR head because it “makes CI work on forks.” That’s exactly the dangerous combo.

**How this project fails**  
[`.github/workflows/demo-antipatterns.yml`](.github/workflows/demo-antipatterns.yml):

- Trigger: `pull_request_target` (secrets + write to base)
- Checkout: `ref: ${{ github.event.pull_request.head.sha }}` (untrusted code)
- Script injection: `run: echo "... ${{ github.event.pull_request.title }}"`

**Remediation (what you’d say in an interview)**  
Prefer `pull_request` for untrusted code; never checkout PR head in `pull_request_target` without strong isolation; pass untrusted data via `env:` not inline `${{ }}`; use `permissions:` least privilege.

**Interview prompt:** *Walk me through a pwn-request and how you’d rewrite the workflow.*

---

### 2. Maintained — Risk: High

**What it measures**  
Recent commit / issue activity (and special-case warnings for very new repos).

**Why it matters**  
Unmaintained projects accumulate unpatched vulns. AI can generate “complete” looking libraries that nobody maintains after the demo.

**How this project fails**  
Scorecard flags repositories created within the last 90 days: *“Please review its contents carefully.”* This lab is new by design.

**Remediation**  
Sustain commits/issue response over time; archive dead projects; for vendors, ask for release cadence SLAs — don’t trust a high Scorecard alone on a 2-week-old repo.

**Interview prompt:** *How would you evaluate a brand-new OSS dependency that Scorecard marks Maintained=0?*

---

### 3. Code-Review — Risk: High

**What it measures**  
Whether recent changes were approved via human review (PRs with approvals / equivalent).

**Why it matters**  
AI-generated PRs can look polished and still be wrong or malicious. Review is the human (or dual-control) brake.

**How this project fails**  
Direct pushes / unreviewed merges → “Found 0/N approved changesets.”

**Remediation**  
Require PR + ≥1 approving review (2 for higher assurance); CODEOWNERS for sensitive paths; ban force-push to default branch (pairs with Branch-Protection).

**Interview prompt:** *What’s the difference between Code-Review and Branch-Protection scores?*  
*(Review looks at historical evidence of approvals; Branch-Protection looks at enforced rules.)*

---

### 4. Branch-Protection — Risk: High

**What it measures**  
Rules on default/release branches: no force-push, no deletion, required reviews, status checks, etc. (tiered scoring).

**Why it matters**  
Without protection, anyone with push (or a stolen token) can rewrite `main`. AI bots with write access make this worse.

**How this project fails**  
`main` has no protection / ruleset → score **0**. Viewer detail: *“branch protection not enabled for branch 'main'”*.

**Remediation**  
GitHub **Rulesets** (readable with default `GITHUB_TOKEN`) or classic Branch Protection; require PR + review + CI; dismiss stale reviews; restrict admin bypass.

**Interview prompt:** *Design a ruleset for a 5-person team shipping weekly with AI-assisted PRs.*

---

### 5. Binary-Artifacts — Risk: High

**What it measures**  
Whether opaque executables are committed (hard to review; may drift from source).

**Why it matters**  
“Just commit the binary the model built” shortcuts reproducibility and hides malware.

**How this project fails**  
[`bin/demo-helper`](bin/demo-helper) — ELF-header blob checked into git on purpose.  
Scorecard Warn: `binary detected: bin/demo-helper`. With few binaries the numeric score may stay high (e.g. **9/10**) — the **failed criterion** is still “binaries present in source.”

**Remediation**  
Build in CI; release via attested artifacts; don’t store `.exe`/`.so`/`.dll`/`.class` in source without a strong exception policy.

**Interview prompt:** *When are binaries in-repo acceptable (if ever)?*

---

### 6. Dependency-Update-Tool — Risk: High

**What it measures**  
Presence of Dependabot, Renovate, or similar automation.

**Why it matters**  
AI pins packages that rot quickly. Automation is how you keep OSV findings from lingering.

**How this project fails**  
No `.github/dependabot.yml` / Renovate config (removed for the lab).

**Remediation**  
Add Dependabot for `github-actions` + language ecosystems; merge update PRs on a cadence; pair with `Vulnerabilities` + `Pinned-Dependencies`.

**Interview prompt:** *Dependabot vs Renovate — when pick which?*

---

### 7. Token-Permissions — Risk: High

**What it measures**  
Whether workflows use least-privilege `permissions` (top-level read, job-level writes only as needed).

**Why it matters**  
A compromised workflow with `write-all` can push malware to `main` or steal secrets. AI-generated YAML often omits `permissions:` (defaults can be broad depending on org settings).

**How this project fails**  
`demo-antipatterns.yml` sets `permissions: write-all`.  
Contrast: `scorecards.yml` uses `permissions: read-all` + narrow job writes — the *good* pattern.

**Remediation**  
Default `contents: read` / `read-all` at workflow top; grant `security-events: write` etc. only on jobs that need them.

**Interview prompt:** *Show a before/after YAML that drops Token-Permissions findings without breaking Code Scanning upload.*

---

### 8. Vulnerabilities — Risk: High

**What it measures**  
Open known vulns in the project or its dependencies via [OSV](https://osv.dev/).

**Why it matters**  
This is the closest Scorecard check to “are we shipping known bad CVEs?” — complementary to AI that may suggest outdated majors.

**How this project fails**  
- [`package.json`](package.json) → `lodash@4.17.15`  
- [`requirements.txt`](requirements.txt) → `django==1.11.29`, `PyYAML==5.1`  

These are classic OSV-listed pins. If the live score is still 10, treat that as a teaching moment: **scanner coverage depends on manifests/lockfiles and ecosystem support**, so always verify with `osv-scanner` / GitHub Dependabot alerts too.

**Remediation**  
Bump to fixed versions; run `osv-scanner` / Dependabot security updates; use `osv-scanner.toml` only with documented exceptions.

**Interview prompt:** *A Scorecard Vulnerabilities=0 but commercial SCA disagrees — how do you reconcile?*

---

### 9. SAST — Risk: Medium

**What it measures**  
Evidence of static application security testing (e.g. CodeQL, SonarCloud) on recent PRs / workflows.

**Why it matters**  
AI introduces classes of bugs (injection, path traversal) at scale; SAST is a cheap gate before review.

**How this project fails**  
No CodeQL workflow / SAST app → *“no SAST tool detected.”*

**Remediation**  
Add `github/codeql-action` workflow; require the check in a ruleset; don’t confuse Scorecard SAST with “we ran ESLint once.”

**Interview prompt:** *Where does SAST sit vs Scorecard vs secret scanning in a pipeline diagram?*

---

### 10. Fuzzing — Risk: Medium

**What it measures**  
OSS-Fuzz / ClusterFuzzLite / recognized in-repo fuzz harnesses.

**Why it matters**  
Parsers and AI-generated protocol code are fuzz-hungry. Most app repos score 0 — know *why* and when it matters (libraries, codecs, crypto).

**How this project fails**  
No fuzzer integration → score **0**.

**Remediation**  
For libraries: OSS-Fuzz or language fuzz tests (Go fuzzing, etc.). For typical apps: explain residual risk rather than cargo-culting a fake harness.

**Interview prompt:** *Would you fail a product team’s security review for Fuzzing=0? When yes/no?*

---

### 11. Pinned-Dependencies — Risk: Medium

**What it measures**  
Build/release dependencies pinned by immutable digest/SHA (Actions, Docker base images, etc.).

**Why it matters**  
`actions/checkout@v4` can move; a compromised tag republish = your CI runs attacker code. AI snippets almost always show floating tags.

**How this project fails**  
Anti-pattern workflow: `uses: actions/checkout@v4`.  
Good contrast in Scorecard workflow: full commit SHA pins.

**Remediation**  
Pin Actions to full SHA; pin Docker `image@sha256:...`; use Dependabot to update pins safely.

**Interview prompt:** *Tradeoff: pin-by-SHA vs renovate noise — how do you operate it?*

---

### 12. Security-Policy — Risk: Medium

**What it measures**  
Discoverable vulnerability reporting policy (`SECURITY.md` with contact + process signals).

**Why it matters**  
Without a private reporting path, researchers file public issues — or stay silent. AI-era products get more external attention.

**How this project fails**  
`SECURITY.md` removed for the lab → score **0**.

**Remediation**  
Add `SECURITY.md` with contact (email / private advisory), disclosure expectations, and timelines; enable GitHub private vulnerability reporting.

**Interview prompt:** *Draft a minimal SECURITY.md you’d accept in a Series-A startup.*

---

### 13. CII-Best-Practices — Risk: Low

**What it measures**  
Progress toward an [OpenSSF Best Practices](https://www.bestpractices.dev/) badge (passing/silver/gold).

**Why it matters**  
Broader than Scorecard (docs, crypto policy, unique contributors). Low weight alone, strong signal for mature OSS.

**How this project fails**  
No badge / bestpractices.dev enrollment → **0**.

**Remediation**  
Create a Best Practices self-assessment; treat it as a roadmap, not a vanity badge.

**Interview prompt:** *How do Scorecard and Best Practices badge overlap / diverge?*

---

### 14. Contributors — Risk: Low

**What it measures**  
Recent contributors from multiple companies/orgs (bus-factor / capture resistance).

**Why it matters**  
Single-maintainer projects (including AI-generated one-person repos) are fragile and easier to compromise socially.

**How this project fails**  
Solo lab authorship → **0**.

**Remediation**  
Encourage diverse reviewers; for critical deps require org diversity or internal forks with ownership.

**Interview prompt:** *How do you risk-rank a critical dep with Contributors=0 but score 9 elsewhere?*

---

### 15. License — Risk: Low

**What it measures**  
Presence of a recognizable license file (LEGAL clarity for use/review).

**Why it matters**  
No license ⇒ default “all rights reserved” ambiguity; blocks secure use and some corp scanners. AI copy-paste often omits licenses.

**How this project fails**  
No `LICENSE` in repo root → **0**.

**Remediation**  
Add an SPDX-identifiable license (`MIT`, `Apache-2.0`, etc.) at repo root.

**Interview prompt:** *Why does a security scorecard care about licensing at all?*

---

### 16. CI-Tests — Risk: Low

**What it measures**  
Whether recent PRs ran tests before merge.

**Why it matters**  
AI PRs need executable proof, not vibes. Without CI, review is theatre.

**How this project fails**  
There is no unit-test workflow. A lab PR once scored **10** because the anti-pattern `pull_request_target` workflow *ran* and counted as “CI.”  
The anti-pattern file still contains the dangerous YAML, but its `paths:` filter should prevent it from running on normal PRs so future unreviewed merges can show **0**.

**Remediation**  
Add a real `pull_request` test job; mark that check **required** in a ruleset (ties to Branch-Protection).

**Interview prompt:** *CI-Tests vs SAST vs Branch-Protection required checks — how do they layer?*

---

### 17. Packaging — Risk: Medium

**What it measures**  
Whether the project publishes an installable package (GitHub Actions publish workflows / language hubs).

**Why it matters**  
Packaged distribution is how users receive patches. Random git clones of AI demos don’t get updates.

**How this project fails**  
No packaging workflow → **`?` / N/A** (not detected). That’s still “doesn’t earn the control.”

**Remediation**  
Publish to npm/PyPI/GHCR/etc. from CI with provenance where possible (pairs with Signed-Releases / SLSA).

**Interview prompt:** *What’s the security difference between ‘git clone install’ and a signed package?*

---

### 18. Signed-Releases — Risk: High

**What it measures**  
Cryptographic signatures on release artifacts (sigstore/cosign, GPG, etc.).

**Why it matters**  
Unsigned GitHub Release zips are a trust-on-first-download problem — easy to swap in a supply-chain attack.

**How this project fails**  
If a Release exists without signatures → **0**. If no releases → **`?`**. Lab uses an **unsigned** release asset when present (see Releases page).

**Remediation**  
Sign with cosign/sigstore; attach `.sig` / provenance; verify in install docs.

**Interview prompt:** *Explain keyless cosign for a GitHub Release in three steps.*

---

## Good vs bad patterns in *this* repo

| Concern | Bad example (study) | Good example (keep) |
| --- | --- | --- |
| Workflow privilege | `demo-antipatterns.yml` → `write-all`, `pull_request_target` | `scorecards.yml` → `read-all` + job-scoped writes |
| Action pins | `actions/checkout@v4` | `actions/checkout@<full-sha>` |
| Dependencies | `lodash@4.17.15` in `package.json` | (would) Dependabot + current versions |
| Binaries | `bin/demo-helper` | build in CI, don’t commit |
| Policy / legal | missing `SECURITY.md` / `LICENSE` | restore both for production |

---

## How to raise the score (practice exercise)

Work these in order for interview drills:

1. Delete `demo-antipatterns.yml` and `bin/demo-helper`.  
2. Restore `LICENSE`, `SECURITY.md`, `.github/dependabot.yml`.  
3. Fix / remove vulnerable `package.json` dependency.  
4. Add CodeQL workflow (`SAST`).  
5. Add a branch ruleset: required PR + 1 review + required CI.  
6. Merge only via reviewed PRs (`Code-Review`).  
7. Publish a cosign-signed release (`Signed-Releases`) and a package workflow (`Packaging`).  
8. Re-run Scorecard; watch the [viewer](https://scorecard.dev/viewer/?uri=github.com/shashi-chin/ossf-scorecard-lab) move.

---

## Viewing results

**Private-repo style (implemented here):** each Scorecard run builds `scorecard-report.html` in CI and uploads it in the `scorecard-results` artifact. Download the zip → open the HTML. Details: [docs/VIEWING-RESULTS.md](docs/VIEWING-RESULTS.md).

| Surface | URL / path |
| --- | --- |
| **HTML viewer (private-friendly)** | Actions → run → Artifacts → `scorecard-results` → **`scorecard-report.html`** |
| Official public UI | https://scorecard.dev/viewer/?uri=github.com/shashi-chin/ossf-scorecard-lab |
| Raw JSON / SARIF | Same artifact: `results.json`, `results.sarif` |
| Code Scanning | Repo **Security** tab (public / GHAS) |
| Check criteria | https://github.com/ossf/scorecard/blob/main/docs/checks.md |

---

## Disclaimer

This repository contains **deliberate insecure CI patterns** and a **known-vulnerable dependency** for education. It is not a template for production systems.
