# How to view Scorecard results (private-repo style)

This lab builds an HTML report **inside the workflow** and uploads it as an Actions artifact. That is the practical viewer when the repo is private (no [scorecard.dev](https://scorecard.dev)).

## Steps

1. Open **Actions** → **OpenSSF Scorecard**  
   https://github.com/shashi-chin/ossf-scorecard-lab/actions/workflows/scorecards.yml
2. Open the latest **green** run.
3. Scroll to **Artifacts**.
4. Download **`scorecard-results`** (zip).
5. Unzip and open **`scorecard-report.html`** in your browser.

You will also find:
- `results.json` — raw scores (good for scripts)
- `results.sarif` — Code Scanning format / VS Code SARIF Viewer

## CLI alternative

```powershell
gh run list --workflow=scorecards.yml --limit 1
gh run download <RUN_ID> -n scorecard-results -D .\scorecard-out
start .\scorecard-out\scorecard-report.html
```

## Private vs public

| | Private repo | This lab (public) |
|--|--------------|-------------------|
| HTML artifact viewer | Primary UX | Also available |
| scorecard.dev | Not available | Available |
| Code Scanning UI | Needs GitHub Advanced Security | Available on public |

For a real private repo, set `publish_results: false` in `scorecards.yml`.
