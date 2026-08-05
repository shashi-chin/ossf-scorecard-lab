# OpenSSF Scorecard Lab

Private sandbox to explore what [OpenSSF Scorecard](https://github.com/ossf/scorecard) and the [Scorecard GitHub Action](https://github.com/ossf/scorecard-action) actually measure and deliver.

**Repo:** https://github.com/shashi-chin/ossf-scorecard-lab (private)

---

## What Scorecard gives you

Scorecard is a **repository / supply-chain posture scanner**, not a SAST/DAST bug finder. It answers: *“How well is this project set up against common open-source and CI/CD risks?”*

| Output | Where to find it | Notes for private repos |
| ------ | ---------------- | ----------------------- |
| Per-check scores (0–10) + aggregate | Workflow logs + SARIF artifact | Always available |
| SARIF + JSON score table | **Actions → run → Artifacts → `scorecard-results`** | Kept 14 days; open `results.json` for the full 0–10 table |
| Code Scanning alerts + remediation text | **Security → Code scanning** | Needs **GitHub Advanced Security** on private repos |
| Public badge + api.scorecard.dev | N/A | Disabled here (`publish_results: false`) |

Each failed/low check in Code Scanning includes remediation guidance (“Show more” in the alert).

---

## Checks Scorecard runs (capabilities map)

| Check | Risk focus | What a good score means |
| ----- | ---------- | ----------------------- |
| **Binary-Artifacts** | High | No checked-in binaries / opaque build products |
| **Branch-Protection** | High | Default branch protected (reviews, no force-push, etc.) |
| **CI-Tests** | Medium | PRs run CI before merge |
| **CII-Best-Practices** | Low | OpenSSF Best Practices badge progress |
| **Code-Review** | High | Changes land via reviewed PRs |
| **Contributors** | Low | Diverse recent committers (bus-factor signal) |
| **Dangerous-Workflow** | Critical | Workflows avoid untrusted code execution patterns |
| **Dependency-Update-Tool** | High | Dependabot / Renovate (or similar) configured |
| **Fuzzing** | Medium | Fuzzing integrated (OSS-Fuzz, etc.) |
| **License** | Low | Detectable OSS license file |
| **Maintained** | High | Recent commits / issues activity |
| **Packaging** | Medium | Published via GitHub Packages / trusted release path |
| **Pinned-Dependencies** | Medium | Actions/deps pinned by hash (as in this workflow) |
| **SAST** | Medium | CodeQL / similar SAST enabled |
| **SBOM** | Medium | SBOM present in releases |
| **Security-Policy** | Medium | `SECURITY.md` (or equivalent) exists |
| **Signed-Releases** | High | Release artifacts cryptographically signed |
| **Token-Permissions** | High | Workflows use least-privilege `permissions:` |
| **Vulnerabilities** | High | Known vulns in deps (via OSV) are addressed |
| **Webhooks** | Critical | Webhooks not using insecure HTTP (org/repo webhooks) |

Full criteria: [Scorecard checks docs](https://github.com/ossf/scorecard/blob/main/docs/checks.md)

---

## How to run / view results

### 1. Trigger the Action

- Push to `main`, or
- **Actions → OpenSSF Scorecard → Run workflow**

### 2. Read the SARIF artifact (works without Advanced Security)

1. Open the completed workflow run  
2. Download **scorecard-results**  
3. Open `results.json` for the full per-check score table (easiest learning path)  
4. Open `results.sarif` if you want the Code Scanning-oriented view

### 3. Optional: Code Scanning dashboard

Requires GitHub Advanced Security on this private repo. Without it, the upload step is allowed to fail (`continue-on-error`) so the rest of the job still succeeds.

### 4. Optional: richer Branch-Protection scores

Create a **fine-grained PAT** (read-only) with access to this repo, store it as secret `SCORECARD_TOKEN`, then uncomment `repo_token` in `.github/workflows/scorecards.yml`.

Recommended PAT permissions (read): Contents, Issues, Metadata, Pull requests, and Administration (read) if you want admin-gated branch-protection fields.

---

## What’s already seeded in this lab

| File | Helps Scorecard check |
| ---- | --------------------- |
| `.github/workflows/scorecards.yml` | Token-Permissions, Pinned-Dependencies, Dangerous-Workflow (good patterns) |
| `.github/dependabot.yml` | Dependency-Update-Tool |
| `SECURITY.md` | Security-Policy |
| `LICENSE` | License |

Expect **low** scores on things this empty lab doesn’t have yet (SAST, fuzzing, packaging, signed releases, multi-contributor review culture, etc.). That’s intentional — use the results as a checklist of capabilities.

---

## Private vs public Action support

From the official Scorecard Action docs:

- **Public repos:** Action is free; can publish results + badge.
- **Private repos:** Action supported when **GitHub Advanced Security** is available; otherwise you can still use Scorecard via CLI / local runs, and this workflow still produces the SARIF artifact.

CLI alternative (any machine with Go or the Scorecard release binary):

```bash
# Example after installing scorecard
scorecard --repo=github.com/shashi-chin/ossf-scorecard-lab --show-details
```

(Private CLI runs need a token with repo access in `GITHUB_AUTH_TOKEN` / `GH_TOKEN`.)

---

## Suggested experiments

1. Run once → download SARIF → note which checks are `0` / `NotApplicable`.  
2. Enable a branch ruleset (require PR + 1 review) → re-run → watch **Branch-Protection** / **Code-Review**.  
3. Add CodeQL workflow → re-run → watch **SAST**.  
4. Add `SCORECARD_TOKEN` → compare Branch-Protection detail vs default `GITHUB_TOKEN`.  
5. Temporarily make the repo public → flip `publish_results: true` → try the public badge URL.

---

## References

- [ossf/scorecard](https://github.com/ossf/scorecard)  
- [ossf/scorecard-action](https://github.com/ossf/scorecard-action)  
- [Check documentation](https://github.com/ossf/scorecard/blob/main/docs/checks.md)  
- [scorecard.dev viewer](https://scorecard.dev/) (public repos with published results)
