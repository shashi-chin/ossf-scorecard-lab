#!/usr/bin/env python3
"""Build a private-friendly HTML Scorecard viewer from results.json.

Richer UI inspired by https://scorecard.dev/viewer (aggregate, risk badges,
sort/filter, expandable details). Works offline from a single JSON file.

Usage (CI or local):
  python make_report.py
  python make_report.py --input results.json --output scorecard-report.html
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

# Mirrors OpenSSF Scorecard docs risk levels (checks.md).
RISK_BY_CHECK = {
    "Binary-Artifacts": "High",
    "Branch-Protection": "High",
    "CI-Tests": "Low",
    "CII-Best-Practices": "Low",
    "Code-Review": "High",
    "Contributors": "Low",
    "Dangerous-Workflow": "Critical",
    "Dependency-Update-Tool": "High",
    "Fuzzing": "Medium",
    "License": "Low",
    "Maintained": "High",
    "Packaging": "Medium",
    "Pinned-Dependencies": "Medium",
    "SAST": "Medium",
    "SBOM": "Medium",
    "Security-Policy": "Medium",
    "Signed-Releases": "High",
    "Token-Permissions": "High",
    "Vulnerabilities": "High",
    "Webhooks": "Critical",
}


def build_html(data: dict) -> str:
    enriched = {
        **data,
        "riskByCheck": RISK_BY_CHECK,
    }
    payload = json.dumps(enriched).replace("<", "\\u003c")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>OpenSSF Scorecard report</title>
<style>
  :root {{
    --bg: #f6f7f9;
    --surface: #ffffff;
    --text: #1b1f24;
    --muted: #5c6770;
    --line: #d8dee4;
    --accent: #0b6bcb;
    --good: #1a7f37;
    --good-bg: #dafbe1;
    --mid: #9a6700;
    --mid-bg: #fff8c5;
    --bad: #cf222e;
    --bad-bg: #ffebe9;
    --na: #6e7781;
    --na-bg: #eaeef2;
    --crit: #82071e;
    --crit-bg: #ffe2e0;
    --high: #bc4c00;
    --high-bg: #fff1e5;
    --med: #bf8700;
    --med-bg: #fff8c5;
    --low: #6e7781;
    --low-bg: #eaeef2;
    --shadow: 0 1px 2px rgba(27,31,36,.06), 0 1px 3px rgba(27,31,36,.04);
    --radius: 12px;
    --font: "Segoe UI", ui-sans-serif, system-ui, -apple-system, sans-serif;
    --mono: ui-monospace, "Cascadia Code", Consolas, monospace;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: var(--font);
    background:
      radial-gradient(900px 420px at 0% 0%, #e7f1fb 0%, transparent 55%),
      radial-gradient(700px 380px at 100% 0%, #eef6ee 0%, transparent 50%),
      var(--bg);
    color: var(--text);
    line-height: 1.5;
  }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  main {{ max-width: 980px; margin: 0 auto; padding: 2rem 1.25rem 4rem; }}
  .top {{
    display: flex; flex-wrap: wrap; gap: 1rem; justify-content: space-between;
    align-items: flex-start; margin-bottom: 1.25rem;
  }}
  h1 {{ font-size: 1.55rem; margin: 0 0 .35rem; letter-spacing: -.02em; }}
  .eyebrow {{ color: var(--muted); font-size: .85rem; margin: 0 0 .25rem; }}
  .banner {{
    background: #ddf4ff; border: 1px solid #b6e3ff; color: #0a3069;
    border-radius: 10px; padding: .7rem .95rem; font-size: .9rem; margin-bottom: 1.25rem;
  }}
  .hero {{
    display: grid; grid-template-columns: 160px 1fr; gap: 1.25rem;
    background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius);
    box-shadow: var(--shadow); padding: 1.25rem 1.4rem; margin-bottom: 1rem;
  }}
  @media (max-width: 640px) {{
    .hero {{ grid-template-columns: 1fr; justify-items: center; text-align: center; }}
    .meta {{ text-align: left; width: 100%; }}
  }}
  .score-ring {{
    width: 140px; height: 140px; border-radius: 50%;
    display: grid; place-items: center;
    background: conic-gradient(var(--ring) calc(var(--pct) * 1%), #eaeef2 0);
    position: relative;
  }}
  .score-ring::after {{
    content: ""; position: absolute; inset: 12px; border-radius: 50%; background: var(--surface);
  }}
  .score-ring .inner {{
    position: relative; z-index: 1; text-align: center;
  }}
  .score-ring strong {{
    display: block; font-size: 2.2rem; font-variant-numeric: tabular-nums; line-height: 1.1;
  }}
  .score-ring span {{ color: var(--muted); font-size: .85rem; }}
  .meta {{ display: grid; gap: .55rem; }}
  .meta-row {{
    display: grid; grid-template-columns: 140px 1fr; gap: .5rem; font-size: .92rem;
  }}
  .meta-row dt {{ color: var(--muted); margin: 0; }}
  .meta-row dd {{ margin: 0; word-break: break-all; font-family: var(--mono); font-size: .84rem; }}
  .stats {{
    display: grid; grid-template-columns: repeat(4, 1fr); gap: .6rem; margin-bottom: 1rem;
  }}
  @media (max-width: 640px) {{ .stats {{ grid-template-columns: repeat(2, 1fr); }} }}
  .stat {{
    background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
    padding: .7rem .8rem; box-shadow: var(--shadow);
  }}
  .stat b {{ display: block; font-size: 1.25rem; font-variant-numeric: tabular-nums; }}
  .stat span {{ color: var(--muted); font-size: .8rem; }}
  .toolbar {{
    display: flex; flex-wrap: wrap; gap: .6rem; align-items: center;
    margin-bottom: 1rem; background: var(--surface); border: 1px solid var(--line);
    border-radius: var(--radius); padding: .75rem .9rem; box-shadow: var(--shadow);
  }}
  .toolbar label {{ color: var(--muted); font-size: .82rem; margin-right: .15rem; }}
  .toolbar input[type="search"], .toolbar select {{
    border: 1px solid var(--line); border-radius: 8px; padding: .4rem .55rem;
    font: inherit; background: #fff; color: var(--text);
  }}
  .toolbar input[type="search"] {{ min-width: 180px; flex: 1; }}
  .chips {{ display: flex; flex-wrap: wrap; gap: .4rem; width: 100%; }}
  .chips button {{
    border: 1px solid var(--line); background: #fff; color: var(--muted);
    border-radius: 999px; padding: .28rem .7rem; font: inherit; cursor: pointer;
  }}
  .chips button.active, .chips button:hover {{
    color: var(--text); border-color: var(--accent); background: #ddf4ff;
  }}
  .check {{
    background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius);
    box-shadow: var(--shadow); margin-bottom: .7rem; overflow: hidden;
  }}
  .check > summary {{
    list-style: none; cursor: pointer; display: grid;
    grid-template-columns: 56px 1fr auto; gap: .85rem; align-items: start;
    padding: .95rem 1.05rem;
  }}
  .check > summary::-webkit-details-marker {{ display: none; }}
  .check[open] {{ border-color: #afb8c1; }}
  .score-box {{
    width: 56px; min-height: 56px; border-radius: 10px; display: grid; place-items: center;
    font-weight: 700; font-variant-numeric: tabular-nums; font-size: 1.15rem;
  }}
  .score-box small {{ display: block; font-size: .68rem; font-weight: 600; opacity: .85; }}
  .score-box.good {{ background: var(--good-bg); color: var(--good); }}
  .score-box.mid {{ background: var(--mid-bg); color: var(--mid); }}
  .score-box.bad {{ background: var(--bad-bg); color: var(--bad); }}
  .score-box.na {{ background: var(--na-bg); color: var(--na); }}
  .check-title {{
    display: flex; flex-wrap: wrap; gap: .45rem .6rem; align-items: center; margin-bottom: .25rem;
  }}
  .check-title h2 {{ margin: 0; font-size: 1.05rem; }}
  .icon {{
    width: 1.15rem; height: 1.15rem; border-radius: 50%; display: inline-grid; place-items: center;
    font-size: .7rem; font-weight: 700; color: #fff;
  }}
  .icon.good {{ background: var(--good); }}
  .icon.bad {{ background: var(--bad); }}
  .icon.mid {{ background: var(--mid); }}
  .icon.na {{ background: var(--na); }}
  .risk {{
    font-size: .68rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase;
    border-radius: 999px; padding: .18rem .5rem;
  }}
  .risk.critical {{ background: var(--crit-bg); color: var(--crit); }}
  .risk.high {{ background: var(--high-bg); color: var(--high); }}
  .risk.medium {{ background: var(--med-bg); color: var(--med); }}
  .risk.low {{ background: var(--low-bg); color: var(--low); }}
  .reason {{ color: var(--muted); margin: .15rem 0; font-size: .92rem; }}
  .short {{ margin: .2rem 0 0; font-size: .9rem; }}
  .chev {{ color: var(--muted); font-size: 1.1rem; padding-top: .15rem; }}
  .body {{
    border-top: 1px solid var(--line); padding: .9rem 1.05rem 1.05rem; background: #fafbfc;
  }}
  .body h3 {{ margin: 0 0 .45rem; font-size: .85rem; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }}
  .body ul {{ margin: 0; padding-left: 1.1rem; }}
  .body li {{ margin: .25rem 0; font-size: .9rem; word-break: break-word; }}
  .body li.warn {{ color: #9a6700; }}
  .body li.info {{ color: #0550ae; }}
  .actions {{ margin-top: .75rem; display: flex; flex-wrap: wrap; gap: .75rem; }}
  .empty {{ color: var(--muted); padding: 1.5rem; text-align: center; }}
  footer {{ margin-top: 1.5rem; color: var(--muted); font-size: .82rem; }}
</style>
</head>
<body>
<main>
  <div class="top">
    <div>
      <p class="eyebrow">OpenSSF Scorecard report</p>
      <h1 id="repo-title">Scorecard</h1>
    </div>
  </div>
  <div class="banner">
    Private-friendly viewer generated in CI from <code>results.json</code>
    (scorecard.dev-style layout). Download the <code>scorecard-results</code>
    artifact and open this file — no public publish required.
  </div>
  <section class="hero" id="hero"></section>
  <div class="stats" id="stats"></div>
  <div class="toolbar">
    <input type="search" id="search" placeholder="Filter checks…" />
    <label for="sort">Sort</label>
    <select id="sort">
      <option value="risk-desc">Risk level (high → low)</option>
      <option value="score-asc">Score (low → high)</option>
      <option value="score-desc">Score (high → low)</option>
      <option value="name-asc">Check name (A–Z)</option>
      <option value="name-desc">Check name (Z–A)</option>
    </select>
    <div class="chips" id="chips">
      <button type="button" class="active" data-f="all">All</button>
      <button type="button" data-f="pass">Pass (8–10)</button>
      <button type="button" data-f="warn">Needs work (1–7)</button>
      <button type="button" data-f="fail">Fail (0)</button>
      <button type="button" data-f="na">N/A</button>
      <button type="button" data-f="critical">Critical risk</button>
      <button type="button" data-f="high">High risk</button>
    </div>
  </div>
  <div id="checks"></div>
  <p class="empty" id="empty" hidden>No checks match this filter.</p>
  <footer>
    Offline viewer inspired by
    <a href="https://scorecard.dev/viewer" target="_blank" rel="noopener">scorecard.dev</a>.
    Not an official OpenSSF product.
  </footer>
</main>
<script>
const data = {payload};
const riskRank = {{ Critical: 4, High: 3, Medium: 2, Low: 1, Unknown: 0 }};
function band(score) {{
  if (score === -1 || score == null) return "na";
  if (score >= 8) return "good";
  if (score >= 1) return "mid";
  return "bad";
}}
function label(score) {{
  return (score === -1 || score == null) ? "?" : String(score);
}}
function displayScore(score) {{
  return (score === -1 || score == null) ? "?" : String(score);
}}
function riskFor(name) {{
  return (data.riskByCheck && data.riskByCheck[name]) || "Unknown";
}}
function escapeHtml(s) {{
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}}
function linkify(text) {{
  const escaped = escapeHtml(text);
  return escaped.replace(
    /(https:\\/\\/[^\\s<]+)/g,
    '<a href="$1" target="_blank" rel="noopener">$1<\\/a>'
  );
}}
function iconFor(b) {{
  if (b === "good") return "✓";
  if (b === "na") return "?";
  if (b === "mid") return "!";
  return "✕";
}}
function ringColor(b) {{
  if (b === "good") return "#1a7f37";
  if (b === "mid") return "#9a6700";
  if (b === "na") return "#6e7781";
  return "#cf222e";
}}

const repoName = data.repo?.name || "repository";
document.getElementById("repo-title").textContent = repoName.replace(/^github\\.com\\//, "");
const agg = data.score;
const aggBand = band(agg);
const pct = (agg == null || agg < 0) ? 0 : Math.max(0, Math.min(100, (agg / 10) * 100));
document.getElementById("hero").innerHTML = `
  <div class="score-ring" style="--pct:${{pct}};--ring:${{ringColor(aggBand)}}">
    <div class="inner"><strong>${{displayScore(agg)}}</strong><span>/ 10</span></div>
  </div>
  <dl class="meta">
    <div class="meta-row"><dt>Repository</dt><dd>${{escapeHtml(repoName)}}</dd></div>
    <div class="meta-row"><dt>Commit</dt><dd>${{escapeHtml(data.repo?.commit || "")}}</dd></div>
    <div class="meta-row"><dt>Generated at</dt><dd>${{escapeHtml(data.date || "")}}</dd></div>
    <div class="meta-row"><dt>Scorecard</dt><dd>${{escapeHtml(data.scorecard?.version || "")}}</dd></div>
  </dl>`;

const checks = (data.checks || []).map(c => ({{
  ...c,
  risk: riskFor(c.name),
  band: band(c.score),
}}));

function counts() {{
  let pass=0, warn=0, fail=0, na=0;
  for (const c of checks) {{
    if (c.band === "good") pass++;
    else if (c.band === "mid") warn++;
    else if (c.band === "na") na++;
    else fail++;
  }}
  document.getElementById("stats").innerHTML = `
    <div class="stat"><b>${{pass}}</b><span>Passing (8–10)</span></div>
    <div class="stat"><b>${{warn}}</b><span>Needs work (1–7)</span></div>
    <div class="stat"><b>${{fail}}</b><span>Failing (0)</span></div>
    <div class="stat"><b>${{na}}</b><span>Not applicable</span></div>`;
}}
counts();

let filter = "all";
const root = document.getElementById("checks");
const empty = document.getElementById("empty");

function sortedChecks() {{
  const mode = document.getElementById("sort").value;
  const q = document.getElementById("search").value.trim().toLowerCase();
  let list = checks.filter(c => {{
    if (filter === "pass" && c.band !== "good") return false;
    if (filter === "warn" && c.band !== "mid") return false;
    if (filter === "fail" && c.band !== "bad") return false;
    if (filter === "na" && c.band !== "na") return false;
    if (filter === "critical" && c.risk !== "Critical") return false;
    if (filter === "high" && c.risk !== "High") return false;
    if (!q) return true;
    const hay = [c.name, c.reason, c.documentation?.short, c.risk, ...(c.details || [])]
      .join(" ").toLowerCase();
    return hay.includes(q);
  }});
  list = [...list].sort((a, b) => {{
    if (mode === "name-asc") return a.name.localeCompare(b.name);
    if (mode === "name-desc") return b.name.localeCompare(a.name);
    if (mode === "score-desc") return (b.score ?? -2) - (a.score ?? -2);
    if (mode === "score-asc") return (a.score ?? -2) - (b.score ?? -2);
    // risk-desc default
    const rd = (riskRank[b.risk] || 0) - (riskRank[a.risk] || 0);
    if (rd) return rd;
    return (a.score ?? -2) - (b.score ?? -2);
  }});
  return list;
}}

function render() {{
  const list = sortedChecks();
  root.innerHTML = "";
  empty.hidden = list.length > 0;
  for (const c of list) {{
    const b = c.band;
    const details = (c.details || []).map(d => {{
      const cls = /^Warn:/i.test(d) ? "warn" : (/^Info:/i.test(d) ? "info" : "");
      return `<li class="${{cls}}">${{linkify(d)}}</li>`;
    }}).join("");
    const el = document.createElement("details");
    el.className = "check";
    el.innerHTML = `
      <summary>
        <div class="score-box ${{b}}">${{displayScore(c.score)}}<small>/10</small></div>
        <div>
          <div class="check-title">
            <span class="icon ${{b}}" aria-hidden="true">${{iconFor(b)}}</span>
            <h2>${{escapeHtml(c.name)}}</h2>
            <span class="risk ${{c.risk.toLowerCase()}}">${{escapeHtml(c.risk)}}</span>
          </div>
          <p class="reason">${{escapeHtml(c.reason || "")}}</p>
          <p class="short">${{escapeHtml(c.documentation?.short || "")}}</p>
        </div>
        <div class="chev" aria-hidden="true">▾</div>
      </summary>
      <div class="body">
        ${{details ? `<h3>Details</h3><ul>${{details}}</ul>` : `<p class="reason">No additional details for this check.</p>`}}
        <div class="actions">
          ${{c.documentation?.url ? `<a href="${{escapeHtml(c.documentation.url)}}" target="_blank" rel="noopener">Check documentation</a>` : ""}}
        </div>
      </div>`;
    root.appendChild(el);
  }}
}}

document.getElementById("chips").addEventListener("click", (e) => {{
  const btn = e.target.closest("button");
  if (!btn) return;
  document.querySelectorAll("#chips button").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  filter = btn.dataset.f;
  render();
}});
document.getElementById("sort").addEventListener("change", render);
document.getElementById("search").addEventListener("input", render);
render();
</script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate private Scorecard HTML viewer")
    parser.add_argument("--input", "-i", default="results.json", help="Path to Scorecard JSON")
    parser.add_argument("--output", "-o", default="scorecard-report.html", help="HTML output path")
    args = parser.parse_args()

    src = Path(args.input)
    out = Path(args.output)
    if not src.is_file():
        raise SystemExit(f"Missing Scorecard JSON: {src.resolve()}")

    data = json.loads(src.read_text(encoding="utf-8"))
    out.write_text(build_html(data), encoding="utf-8")
    score = data.get("score")
    checks = len(data.get("checks") or [])
    print(f"Wrote {out.resolve()} (aggregate={score}, checks={checks})")


if __name__ == "__main__":
    main()
