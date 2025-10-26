import json
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# --- Load JSON ---
json_path = Path("results/latest.json")
with open(json_path) as f:
    data = json.load(f)

tests = data.get("tests", [])
df = pd.DataFrame([
    {
        "name": t["nodeid"],
        "outcome": t["outcome"],
        "duration": round(t.get("duration", 0), 2),
        "path": t["nodeid"].split("::")[0],
    }
    for t in tests
])

# --- Infer categories ---
def detect_category(path):
    p = path.lower()
    if "frontend" in p or "home_page" in p or "checkout" in p:
        if "smoke" in p:
            if "firefox" in p:
                return "Frontend Smoke (Firefox)"
            return "Frontend Smoke (Chrome)"
        else:
            if "firefox" in p:
                return "Frontend Regression (Firefox)"
            return "Frontend Regression (Chrome)"
    elif "backend" in p:
        if "smoke" in p:
            return "Backend Smoke"
        return "Backend Regression"
    else:
        return "Other"

df["category"] = df["path"].apply(detect_category)

# --- Summary ---
total = len(df)
passed = len(df[df["outcome"] == "passed"])
failed = len(df[df["outcome"] == "failed"])
xfailed = len(df[df["outcome"] == "xfailed"])

categories = df["category"].unique()

# --- Styling ---
css = """
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Rajdhani:wght@400;500;600&display=swap');

:root {
  --bg: #020305;
  --panel: #0B0D10;
  --accent: #00E8FF;
  --accent2: #00FFA6;
  --danger: #FF3B6A;
  --warn: #FFC14D;
  --text: #E8E8E8;
}

body {
  background: radial-gradient(circle at 15% 20%, #0C0E12 0%, #050607 100%);
  color: var(--text);
  font-family: 'Rajdhani', sans-serif;
  margin: 0;
  padding: 0;
}

/* --- Header --- */
.header {
  text-align: center;
  padding: 45px 0 25px;
}

h1 {
  font-family: 'Orbitron', sans-serif;
  font-size: 38px;
  font-weight: 800;
  letter-spacing: 4px;
  margin: 0;
  background: linear-gradient(90deg, var(--accent2), var(--accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 20px rgba(0,255,255,0.25);
}

/* --- Summary Cards --- */
.cards {
  display: flex;
  justify-content: center;
  gap: 18px;
  margin: 25px auto 40px;
  max-width: 1100px;
}

.card {
  background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  box-shadow: 0 0 18px rgba(0,255,255,0.05);
  text-align: center;
  padding: 18px 24px;
  min-width: 150px;
  transition: all 0.3s ease;
}
.card:hover {
  border-color: var(--accent);
  box-shadow: 0 0 25px rgba(0,255,255,0.2);
}

.card h2 {
  font-family: 'Orbitron', sans-serif;
  font-size: 26px;
  margin: 0;
  color: var(--accent2);
}

.card p {
  color: #9a9a9a;
  font-size: 13px;
  margin: 6px 0 0;
}

/* --- Charts --- */
.grid {
  max-width: 1150px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.chart-wrap {
  background: linear-gradient(145deg, rgba(255,255,255,0.02), rgba(255,255,255,0.005));
  border: 1px solid rgba(0,255,255,0.15);
  border-radius: 16px;
  box-shadow: inset 0 0 10px rgba(255,255,255,0.05), 0 0 18px rgba(0,255,255,0.08);
  padding: 12px 14px;
  transition: all 0.3s ease;
}
.chart-wrap:hover {
  box-shadow: inset 0 0 14px rgba(0,255,255,0.12), 0 0 28px rgba(0,255,255,0.25);
  border-color: rgba(0,255,255,0.4);
}

.chart-div {
  width: 100%;
  height: 180px;
}

/* --- Failed Table --- */
.failed-section {
  max-width: 1100px;
  margin: 35px auto 60px;
}

.failed-table {
  width: 100%;
  border-collapse: collapse;
  color: var(--text);
  font-size: 13px;
}

.failed-table th, .failed-table td {
  border-bottom: 1px solid rgba(255,255,255,0.06);
  padding: 8px 10px;
}

.failed-table th {
  text-align: left;
  color: #999;
  font-weight: 600;
  text-transform: uppercase;
}

.failed-table tr:hover {
  background: rgba(0,255,255,0.04);
}
"""

# --- Build HTML ---
html_parts = [
    f"<html><head><title>Automation Dashboard</title><script src='https://cdn.plot.ly/plotly-latest.min.js'></script><style>{css}</style></head><body>",
    "<div class='header'><h1>QA AUTOMATION DASHBOARD</h1></div>",
    f"<div class='cards'>"
    f"<div class='card'><h2>{total}</h2><p>Total</p></div>"
    f"<div class='card'><h2 style='color:#00FFA6'>{passed}</h2><p>Passed</p></div>"
    f"<div class='card'><h2 style='color:#FF3B6A'>{failed}</h2><p>Failed</p></div>"
    f"<div class='card'><h2 style='color:#FFC14D'>{xfailed}</h2><p>XFailed</p></div></div>",
    "<div class='grid'>"
]

# --- Charts ---
for cat in categories:
    cat_df = df[df["category"] == cat]
    if cat_df.empty:
        continue
    counts = cat_df["outcome"].value_counts()
    chart_id = f"chart-{cat.replace(' ', '-').replace('(', '').replace(')', '')}"

    fig = go.Figure()
    fig.add_trace(go.Bar(x=["Passed"], y=[counts.get("passed", 0)], marker_color="#00FFA6"))
    fig.add_trace(go.Bar(x=["Failed"], y=[counts.get("failed", 0)], marker_color="#FF3B6A"))
    fig.add_trace(go.Bar(x=["XFailed"], y=[counts.get("xfailed", 0)], marker_color="#FFC14D"))
    fig.update_layout(
        title=cat,
        showlegend=False,
        margin=dict(t=35, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#E6E6E6", size=12, family="Rajdhani"),
    )
    html_parts.append(f"<div class='chart-wrap'><div id='{chart_id}' class='chart-div'></div></div>")
    html_parts.append(f"<script>Plotly.newPlot('{chart_id}', {fig.to_json()}.data, {fig.to_json()}.layout);</script>")

html_parts.append("</div>")  # grid end

# --- Failed tests table ---
failed_tests = df[df["outcome"] == "failed"].copy()
if not failed_tests.empty:
    failed_tests["duration(s)"] = failed_tests["duration"]
    failed_table_html = failed_tests[["name", "category", "duration(s)"]].to_html(index=False, classes="failed-table")
    html_parts.append(f"<div class='failed-section'><h2>Failed Tests ({len(failed_tests)})</h2>{failed_table_html}</div>")

html_parts.append("</body></html>")

# --- Save HTML ---
Path("dashboard.html").write_text("".join(html_parts), encoding="utf-8")
print("✅ Futuristic dashboard generated: dashboard.html")
