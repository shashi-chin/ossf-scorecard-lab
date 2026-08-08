#!/usr/bin/env python3
"""Build a private-friendly HTML Scorecard viewer from results.json.

Usage (CI or local):
  python make_report.py
  python make_report.py --input results.json --output scorecard-report.html
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_html(data: dict) -> str:
    payload = json.dumps(data)
    # Escape </script> so embedded JSON cannot break out of the script tag.
    payload = payload.replace("<", "\\u003c")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>OpenSSF Scorecard Report (private viewer)</title>
<style>
  :root {{
    --bg: #0f1419;
    --panel: #1a222c;
    --text: #e7ecf1;
    --muted: #9aa7b5;
    --line: #2a3542;
    --good: #3d9a6a;
    --mid: #c4a035;
    --bad: #c45c5c;
    --na: #6b7785;
    --accent: #5b9fd4;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: "Segoe UI", system-ui, sans-serif;
    background: radial-gradient(1200px 600px at 10% -10%, #1b2a3a 0%, var(--bg) 55%);
    color: var(--text);
    line-height: 1.45;
  }}
  main {{ max-width: 960px; margin: 0 auto; padding: 2rem 1.25rem 4rem; }}
  h1 {{ font-size: 1.6rem; margin: 0 0 .35rem; font-weight: 650; }}
  .sub {{ color: var(--muted); margin-bottom: 1.75rem; font-size: .95rem; }}
  .banner {{
    background: #243041; border: 1px solid var(--line); border-radius: 10px;
    padding: .75rem 1rem; margin-bottom: 1.25rem; color: var(--muted); font-size: .9rem;
  }}
  .hero {{
    display: grid;
    grid-template-columns: 140px 1fr;
    gap: 1.25rem;
    align-items: center;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
  }}
  .score-ring {{
    width: 120px; height: 120px; border-radius: 50%;
    display: grid; place-items: center;
    background: conic-gradient(var(--ring) calc(var(--pct) * 1%), var(--line) 0);
    position: relative;
  }}
  .score-ring::after {{
    content: "";
    position: absolute; inset: 10px; border-radius: 50%; background: var(--panel);
  }}
  .score-ring strong {{
    position: relative; z-index: 1; font-size: 1.8rem; font-variant-numeric: tabular-nums;
  }}
  .meta dt {{ color: var(--muted); font-size: .8rem; }}
  .meta dd {{ margin: 0 0 .55rem; font-size: .95rem; word-break: break-all; }}
  .filters {{ display: flex; flex-wrap: wrap; gap: .5rem; margin-bottom: 1rem; }}
  .filters button {{
    background: transparent; color: var(--muted); border: 1px solid var(--line);
    border-radius: 999px; padding: .35rem .8rem; cursor: pointer; font: inherit;
  }}
  .filters button.active, .filters button:hover {{ color: var(--text); border-color: var(--accent); }}
  .check {{
    background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
    padding: 1rem 1.1rem; margin-bottom: .75rem;
  }}
  .check header {{ display: flex; justify-content: space-between; gap: 1rem; align-items: baseline; }}
  .check h2 {{ font-size: 1.05rem; margin: 0; }}
  .badge {{
    font-variant-numeric: tabular-nums; font-weight: 650; min-width: 2.4rem; text-align: center;
    border-radius: 8px; padding: .2rem .45rem; color: #0f1419;
  }}
  .badge.good {{ background: var(--good); }}
  .badge.mid {{ background: var(--mid); }}
  .badge.bad {{ background: var(--bad); color: #fff; }}
  .badge.na {{ background: var(--na); color: #fff; }}
  .reason {{ color: var(--muted); margin: .45rem 0 .2rem; }}
  .short {{ font-size: .9rem; margin: .35rem 0; }}
  details {{ margin-top: .5rem; }}
  details summary {{ cursor: pointer; color: var(--accent); }}
  ul {{ margin: .4rem 0 0; padding-left: 1.1rem; color: var(--muted); font-size: .9rem; }}
  a {{ color: var(--accent); }}
</style>
</head>
<body>
<main>
  <h1>OpenSSF Scorecard</h1>
  <p class="sub">Private-friendly viewer generated in CI from <code>results.json</code></p>
  <div class="banner">
    This HTML is produced by the Scorecard workflow and uploaded as an Actions artifact.
    It works for private repos (no scorecard.dev required). Download the
    <code>scorecard-results</code> artifact and open <code>scorecard-report.html</code>.
  </div>
  <section class="hero" id="hero"></section>
  <div class="filters" id="filters">
    <button class="active" data-f="all">All</button>
    <button data-f="pass">Pass (8–10)</button>
    <button data-f="warn">Needs work (1–7)</button>
    <button data-f="fail">Fail (0)</button>
    <button data-f="na">N/A (−1)</button>
  </div>
  <div id="checks"></div>
</main>
<script>
const data = {payload};
function band(score) {{
  if (score === -1 || score == null) return "na";
  if (score >= 8) return "good";
  if (score >= 1) return "mid";
  return "bad";
}}
function label(score) {{
  return score === -1 || score == null ? "N/A" : String(score);
}}
const pct = Math.max(0, Math.min(100, (data.score / 10) * 100));
const colors = {{ good: "#3d9a6a", mid: "#c4a035", bad: "#c45c5c", na: "#6b7785" }};
const ring = colors[band(data.score)];
document.getElementById("hero").innerHTML = `
  <div class="score-ring" style="--pct:${{pct}};--ring:${{ring}}"><strong>${{data.score}}</strong></div>
  <dl class="meta">
    <dt>Repository</dt><dd>${{data.repo?.name || ""}}</dd>
    <dt>Commit</dt><dd>${{data.repo?.commit || ""}}</dd>
    <dt>Scanned</dt><dd>${{data.date || ""}}</dd>
    <dt>Scorecard</dt><dd>${{data.scorecard?.version || ""}}</dd>
  </dl>`;
const checks = [...(data.checks || [])].sort((a,b) => (b.score ?? -2) - (a.score ?? -2));
const root = document.getElementById("checks");
function escapeHtml(s) {{
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}}
function render(filter) {{
  root.innerHTML = "";
  for (const c of checks) {{
    const b = band(c.score);
    if (filter === "pass" && b !== "good") continue;
    if (filter === "warn" && b !== "mid") continue;
    if (filter === "fail" && b !== "bad") continue;
    if (filter === "na" && b !== "na") continue;
    const details = (c.details || []).map(d => `<li>${{escapeHtml(d)}}</li>`).join("");
    const el = document.createElement("article");
    el.className = "check";
    el.innerHTML = `
      <header>
        <h2>${{escapeHtml(c.name)}}</h2>
        <span class="badge ${{b}}">${{label(c.score)}}</span>
      </header>
      <p class="reason">${{escapeHtml(c.reason || "")}}</p>
      <p class="short">${{escapeHtml(c.documentation?.short || "")}}</p>
      ${{c.documentation?.url ? `<a href="${{escapeHtml(c.documentation.url)}}" target="_blank" rel="noopener">Check docs</a>` : ""}}
      ${{details ? `<details><summary>Details</summary><ul>${{details}}</ul></details>` : ""}}`;
    root.appendChild(el);
  }}
}}
render("all");
document.getElementById("filters").addEventListener("click", (e) => {{
  const btn = e.target.closest("button");
  if (!btn) return;
  document.querySelectorAll("#filters button").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  render(btn.dataset.f);
}});
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
