"""
Museum-quality interactive PRI dashboard
=========================================
Self-contained HTML using Jacob's signature aesthetic:
    void black #030303 background, ember gold #c9a227,
    Cormorant Garamond display, IBM Plex Mono data labels.

Output: output/pri_dashboard_v2.html
"""

from pathlib import Path
import json
import datetime
import pandas as pd
import math

ROOT = Path("/home/claude/pri")
OUT  = ROOT / "output"

df = pd.read_csv(OUT / "pri_v2_quarterly.csv", parse_dates=["date"])
df = df.sort_values("date").reset_index(drop=True)

# helper that converts NaN -> None for JSON (Plotly tolerates null gaps)
def to_jl(s):
    return [None if (isinstance(v, float) and math.isnan(v)) else v for v in s]

dates_iso = df["date"].dt.strftime("%Y-%m-%d").tolist()

obs       = to_jl(df["observed_sentiment"].round(2).tolist())
pred      = to_jl(df["predicted_sentiment"].round(2).tolist())
gap       = to_jl(df["sentiment_gap"].round(2).tolist())
pri_sent  = to_jl(df["pri_sentiment"].round(2).tolist())
hps_obs   = to_jl(df["hps_obs"].round(2).tolist())
pri_hps   = to_jl(df["pri_hps"].round(2).tolist())
pri_comp  = to_jl(df["pri_composite"].round(2).tolist())
unrate    = to_jl(df["unrate"].round(2).tolist())
dpayems   = to_jl(df["dpayems_yoy"].round(2).tolist())
jolts     = to_jl(df["jtsjol_thousands"].round(0).tolist())

# headline statistics
last        = df.iloc[-1]
latest_q    = f"{last['date'].year}Q{(last['date'].month - 1) // 3 + 1}"
latest_pri  = float(last["pri_composite"]) if not pd.isna(last["pri_composite"]) else None
latest_sent_pri  = float(last["pri_sentiment"])
latest_obs_sent  = float(last["observed_sentiment"])
latest_pred_sent = float(last["predicted_sentiment"])
latest_gap_val   = float(last["sentiment_gap"])
latest_un        = float(last["unrate"])
latest_jolts_thou = int(last["jtsjol_thousands"])

post22 = df[df["date"] >= "2022-01-01"]
mean_comp_22on = float(post22["pri_composite"].mean())
peak_idx = post22["pri_composite"].idxmax()
peak_q   = df.loc[peak_idx, "date"]
peak_q_str  = f"{peak_q.year}Q{(peak_q.month-1)//3+1}"
peak_pri = float(df.loc[peak_idx, "pri_composite"])

# latest HPS observation
last_hps_row = df[df["hps_obs"].notna()].iloc[-1]
last_hps_q   = f"{last_hps_row['date'].year}Q{(last_hps_row['date'].month-1)//3+1}"
last_hps_val = float(last_hps_row["hps_obs"])
last_hps_pri = float(last_hps_row["pri_hps"])

q_above_5  = int((df.loc[df["date"] >= "2020-01-01", "pri_composite"] > 5).sum())
q_post     = int((df["date"] >= "2020-01-01").sum())

with open(OUT / "pri_v2_fit.txt") as f:
    fit_text = f.read()

# ============================================================================
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>The Psychological Recession Index · v2 · United States, 2010–2026</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400;1,500&family=IBM+Plex+Mono:wght@300;400;500;600&display=swap" rel="stylesheet">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
<style>
  :root {
    --void:    #030303;
    --void2:   #0a0a0a;
    --void3:   #141414;
    --bone:    #f0e8d0;
    --bone2:   #c8bfa3;
    --ember:   #c9a227;
    --ember2:  #e3c151;
    --rust:    #b35900;
    --crimson: #8a2c20;
    --moss:    #6b8a4a;
    --slate:   #6a8aa8;
    --line:    #2a2620;
    --muted:   #7a7060;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--void); color: var(--bone); }
  body {
    font-family: "Cormorant Garamond", "Times New Roman", Georgia, serif;
    font-size: 17px;
    line-height: 1.6;
    font-weight: 400;
    min-height: 100vh;
  }
  .wrap { max-width: 1180px; margin: 0 auto; padding: 60px 36px 96px; }

  /* HERO ---------------------------------------------------------------- */
  header.hero {
    border-top: 1px solid var(--ember);
    border-bottom: 1px solid var(--line);
    padding: 56px 0 64px;
    margin-bottom: 56px;
    position: relative;
  }
  header.hero::before {
    content: "";
    display: block;
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--ember); opacity: 0.85;
    margin: 0 auto 18px;
    box-shadow: 0 0 18px var(--ember);
  }
  .eyebrow {
    font-family: "IBM Plex Mono", monospace;
    font-size: 10.5px;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    color: var(--ember);
    text-align: center;
    margin: 0 0 22px;
    font-weight: 500;
  }
  h1 {
    font-family: "Cormorant Garamond", serif;
    font-weight: 500;
    font-size: 56px;
    line-height: 1.05;
    letter-spacing: -0.012em;
    margin: 0 0 24px;
    text-align: center;
    color: var(--bone);
  }
  h1 .em {
    font-style: italic;
    color: var(--ember2);
    font-weight: 400;
  }
  .lede {
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
    font-size: 19px;
    line-height: 1.55;
    color: var(--bone2);
    font-weight: 400;
  }
  .lede em { color: var(--ember2); font-style: italic; }

  /* SECTION HEADERS ----------------------------------------------------- */
  h2 {
    font-family: "Cormorant Garamond", serif;
    font-weight: 500;
    font-size: 30px;
    letter-spacing: -0.005em;
    color: var(--bone);
    margin: 64px 0 8px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--line);
  }
  h2 .num {
    font-family: "IBM Plex Mono", monospace;
    font-size: 12px;
    color: var(--ember);
    letter-spacing: 0.2em;
    vertical-align: middle;
    margin-right: 14px;
    font-weight: 400;
  }
  .subhead {
    font-family: "IBM Plex Mono", monospace;
    font-size: 11px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 0 0 22px;
    font-weight: 400;
  }

  /* KPI grid ------------------------------------------------------------ */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: var(--line);
    border: 1px solid var(--line);
    margin-top: 18px;
  }
  .kpi {
    background: var(--void2);
    padding: 28px 24px 26px;
    text-align: left;
  }
  .kpi .l {
    font-family: "IBM Plex Mono", monospace;
    font-size: 10.5px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 0 0 14px;
    font-weight: 500;
  }
  .kpi .v {
    font-family: "Cormorant Garamond", serif;
    font-size: 44px;
    line-height: 1.0;
    font-weight: 500;
    color: var(--bone);
    margin: 0;
  }
  .kpi.crit .v { color: var(--ember2); }
  .kpi .u {
    font-family: "IBM Plex Mono", monospace;
    font-size: 12px;
    color: var(--muted);
    margin-left: 6px;
    letter-spacing: 0.05em;
    font-weight: 400;
  }
  .kpi .desc {
    font-family: "Cormorant Garamond", serif;
    font-style: italic;
    font-size: 14px;
    color: var(--bone2);
    margin: 10px 0 0;
    line-height: 1.45;
  }
  @media (max-width: 900px) {
    .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  }

  /* READING BLOCK ------------------------------------------------------- */
  .reading {
    background: var(--void2);
    border-left: 2px solid var(--ember);
    padding: 24px 28px;
    margin: 32px 0;
    font-size: 18px;
    line-height: 1.6;
    color: var(--bone);
  }
  .reading strong { color: var(--ember2); font-weight: 600; }
  .reading em { font-style: italic; color: var(--bone2); }
  .reading .num {
    font-family: "IBM Plex Mono", monospace;
    font-size: 16px;
    color: var(--ember2);
    font-weight: 500;
  }

  /* CHARTS -------------------------------------------------------------- */
  .chart-card {
    background: var(--void2);
    border: 1px solid var(--line);
    padding: 24px 18px 14px;
    margin: 14px 0 28px;
  }
  .chart-card .cap {
    font-family: "Cormorant Garamond", serif;
    font-style: italic;
    font-size: 15px;
    color: var(--bone2);
    margin: 6px 16px 16px;
    line-height: 1.5;
  }

  /* PRE / CODE ---------------------------------------------------------- */
  pre.fit {
    background: var(--void2);
    border: 1px solid var(--line);
    color: var(--bone2);
    padding: 20px 22px;
    font-family: "IBM Plex Mono", monospace;
    font-size: 12px;
    line-height: 1.55;
    overflow-x: auto;
    border-radius: 0;
    margin: 8px 0;
  }
  pre.fit .hl { color: var(--ember2); }

  /* TABLE --------------------------------------------------------------- */
  .data-table { overflow-x: auto; margin-top: 8px; }
  table {
    width: 100%;
    border-collapse: collapse;
    font-family: "IBM Plex Mono", monospace;
    font-size: 12.5px;
  }
  thead {
    background: var(--void3);
    border-bottom: 1px solid var(--ember);
  }
  th {
    padding: 12px 14px;
    text-align: right;
    font-weight: 500;
    color: var(--ember);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-size: 10px;
  }
  th:first-child { text-align: left; }
  td {
    padding: 9px 14px;
    border-bottom: 1px solid var(--line);
    color: var(--bone2);
    text-align: right;
  }
  td:first-child {
    text-align: left;
    color: var(--bone);
    font-weight: 500;
  }
  tbody tr:hover { background: var(--void3); }
  td.pos { color: var(--ember2); font-weight: 500; }
  td.neg { color: var(--slate); font-weight: 500; }
  td.crit { color: #d9605a; font-weight: 600; }

  /* FOOTER -------------------------------------------------------------- */
  footer {
    margin-top: 96px;
    padding-top: 32px;
    border-top: 1px solid var(--line);
    font-size: 14.5px;
    color: var(--bone2);
    line-height: 1.65;
  }
  footer p { margin: 10px 0; }
  footer .label {
    font-family: "IBM Plex Mono", monospace;
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ember);
    margin-right: 8px;
    font-weight: 500;
  }
  footer a { color: var(--ember2); text-decoration: none; border-bottom: 1px dotted var(--ember); }
  footer a:hover { color: var(--bone); }

  .sigil {
    display: block;
    margin: 72px auto 0;
    opacity: 0.7;
  }

  /* SCROLL REVEAL ------------------------------------------------------- */
  .reveal { opacity: 0; transform: translateY(18px); transition: opacity 0.9s ease, transform 0.9s ease; }
  .reveal.in { opacity: 1; transform: translateY(0); }
</style>
</head>
<body>
<div class="wrap">

<header class="hero reveal">
  <p class="eyebrow">A Public-Health Data Science Instrument · 2010–__LATEST_Q__</p>
  <h1>The Psychological <span class="em">Recession</span> Index</h1>
  <p class="lede">A population can be <em>sick at scale</em> and be invisible to the instruments that govern it. The Psychological Recession Index measures what the macroeconomic vocabulary cannot detect: the residual divergence between the labor market the government sees and the one the population reports living in.</p>
</header>

<!-- KPIs -->
<section class="reveal">
  <h2><span class="num">I.</span>Where the population stands today</h2>
  <p class="subhead">Composite construct estimate · __LATEST_Q__</p>

  <div class="kpi-grid">
    <div class="kpi crit">
      <p class="l">Composite PRI · __LATEST_Q__</p>
      <p class="v">+__PRI_LATEST__<span class="u">σ</span></p>
      <p class="desc">Standard deviations above the 2010–2019 baseline residual. The headline construct estimate.</p>
    </div>
    <div class="kpi">
      <p class="l">Mean PRI · 2022Q1→</p>
      <p class="v">+__PRI_MEAN__<span class="u">σ</span></p>
      <p class="desc">A sustained, multi-year departure from the baseline. The post-2021 plateau is the construct's signature.</p>
    </div>
    <div class="kpi">
      <p class="l">Peak · __PEAK_Q__</p>
      <p class="v">+__PRI_PEAK__<span class="u">σ</span></p>
      <p class="desc">The high-water mark to date in the empirical record.</p>
    </div>
    <div class="kpi">
      <p class="l">Quarters PRI &gt; +5σ</p>
      <p class="v">__Q_ABOVE__<span class="u">/__Q_POST__</span></p>
      <p class="desc">Post-2020 quarters where the composite exceeds the +5σ threshold.</p>
    </div>
  </div>

  <div class="reading">
    At <strong>__LATEST_Q__</strong>, the U.S. unemployment rate stands at <span class="num">__LATEST_UN__%</span> and job openings at <span class="num">__LATEST_JOLTS__ thousand</span>. The 2010–2019 macro→sentiment baseline predicts consumer sentiment near <span class="num">__LATEST_PRED__</span> at this macro state; the Michigan Survey observes <span class="num">__LATEST_OBS__</span>. The Household Pulse Survey reports <span class="num">__LAST_HPS__%</span> of adults with anxiety or depression symptoms — a level <em>roughly three times</em> the pre-pandemic NHIS 2019 anchor of 10.8%. The composite PRI registers <strong>+__PRI_LATEST__σ</strong> above the baseline residual — the empirical signature of what this paper names a <em>psychological recession</em>.
  </div>
</section>

<!-- Panel A: Sentiment -->
<section class="reveal">
  <h2><span class="num">II.</span>Consumer sentiment versus what the macro state predicts</h2>
  <p class="subhead">Michigan Survey, quarterly · 2010Q1–__LATEST_Q__</p>
  <div class="chart-card">
    <div id="chartA" style="height: 360px;"></div>
    <p class="cap">Through 2019 the relationship between macro labor indicators and consumer sentiment was statistically tight: a linear model in unemployment, payroll growth, and log job openings explained 91.5% of sentiment variance with a 3.1-point residual standard deviation. The dashed line projects that 2010–2019 rule through the post-2020 period. Observed sentiment has not returned to its predicted level.</p>
  </div>
</section>

<!-- Panel B: HPS -->
<section class="reveal">
  <h2><span class="num">III.</span>Direct psychiatric outcome: HPS anxiety + depression</h2>
  <p class="subhead">CDC / U.S. Census Household Pulse Survey, modified PHQ-2 + GAD-2 · 2019 NHIS anchor + 2020–__LATEST_Q__ HPS waves</p>
  <div class="chart-card">
    <div id="chartB" style="height: 360px;"></div>
    <p class="cap">The pre-pandemic National Health Interview Survey reported 10.8% of U.S. adults with anxiety or depression symptoms. The Census Bureau's Household Pulse Survey, fielding a clinically validated short-form instrument from April 2020 forward, has not registered values below approximately 30% in any subsequent wave. This is a direct psychiatric measurement — not a sentiment proxy — and it shows the same divergence the macro→sentiment model implies.</p>
  </div>
</section>

<!-- Panel C: Gap -->
<section class="reveal">
  <h2><span class="num">IV.</span>The sentiment gap, in index points</h2>
  <p class="subhead">Predicted minus observed UMCSENT · 2010Q1–__LATEST_Q__</p>
  <div class="chart-card">
    <div id="chartC" style="height: 320px;"></div>
    <p class="cap">During the 2020 pandemic shock the relationship inverted briefly — sentiment was <em>better</em> than the 14.8% unemployment spike would have predicted, almost certainly because the CARES Act and unemployment expansion buffered the psychological cost of the macro shock. From 2021 forward the gap inverts and persists, peaking at roughly 50 index points in mid-2022 and remaining 30+ points wide through late 2025.</p>
  </div>
</section>

<!-- Panel D: Composite -->
<section class="reveal">
  <h2><span class="num">V.</span>The composite Psychological Recession Index</h2>
  <p class="subhead">Standardized residual, σ above 2010–2019 baseline · two psychiatric proxies, composite</p>
  <div class="chart-card">
    <div id="chartD" style="height: 420px;"></div>
    <p class="cap">The composite PRI is the mean of two standardized residuals: (a) the sentiment-fundamentals gap divided by the 2010–2019 residual standard deviation, and (b) the HPS anxiety/depression deviation from the NHIS 2019 anchor divided by a conservative 1.5 percentage-point baseline σ. Both components register the same direction and similar magnitude. The construct is robust to the choice of psychiatric proxy.</p>
  </div>
</section>

<!-- OLS Fit -->
<section class="reveal">
  <h2><span class="num">VI.</span>The baseline regression</h2>
  <p class="subhead">UMCSENT ~ UNRATE + ΔPAYEMS_yoy + log(JTSJOL) · 2010Q1–2019Q4</p>
  <pre class="fit" id="fitText">__FIT_TEXT__</pre>
</section>

<!-- Table -->
<section class="reveal">
  <h2><span class="num">VII.</span>The quarterly panel</h2>
  <p class="subhead">All input series and PRI components, reverse-chronological</p>
  <div class="data-table">
    <table>
      <thead><tr>
        <th>Quarter</th><th>UNRATE %</th><th>ΔPAY yoy %</th><th>JOLTS K</th>
        <th>Sent obs</th><th>Sent pred</th><th>Gap pts</th>
        <th>HPS %</th><th>PRI sent σ</th><th>PRI HPS σ</th><th>PRI comp σ</th>
      </tr></thead>
      <tbody id="rows"></tbody>
    </table>
  </div>
</section>

<footer class="reveal">
  <p><span class="label">Data sources</span>Bureau of Labor Statistics via FRED (UNRATE, PAYEMS, JTSJOL); Surveys of Consumers, University of Michigan via FRED (UMCSENT, ©); U.S. Census Bureau / CDC NCHS Household Pulse Survey (HPS, modified PHQ-2 + GAD-2 indicators of anxiety or depression); 2019 National Health Interview Survey, as compiled in Vahratian et al., MMWR <em>70</em>(13), 2021. Series fetched __FETCH_DATE__.</p>

  <p><span class="label">Method</span>Monthly series resampled to quarterly (mean within quarter). OLS regression of UMCSENT on unemployment, year-over-year payroll growth, and log job openings, training window 2010Q1–2019Q4 (R² = 0.915, n = 36). Out-of-sample residuals standardized by the training-window residual standard deviation. HPS series standardized as deviation from the NHIS 2019 pre-pandemic anchor (10.8%), with a conservative 1.5 percentage-point baseline standard deviation reflecting pre-pandemic year-to-year variation in equivalent K6-based prevalence estimates. Composite PRI = mean of available standardized component series.</p>

  <p><span class="label">Caveats</span>The HPS series was not available pre-pandemic by construction; its baseline is the NHIS 2019 anchor rather than the same instrument fielded under different macro conditions. The sentiment series carries a documented inflation-memory component (Bernstein &amp; Posthumus 2025); inflation memory does not account for the HPS divergence, which is measured on a clinical screening instrument. Multicollinearity among macro RHS variables (condition number = 2,640) does not affect the fitted predictions used to compute PRI but should be addressed by ridge regularization in a v3 specification. The construct's external validity awaits cross-national replication.</p>

  <p><span class="label">Citation</span>Thomas, J. E., &amp; [Co-author]. The Psychological Recession: Conceptualizing and Operationalizing the Post-Pandemic United States Labor Market as a Distal Psychiatric Exposure. SSRN preprint, 2026.</p>

  <svg class="sigil" width="44" height="44" viewBox="0 0 44 44" xmlns="http://www.w3.org/2000/svg">
    <circle cx="22" cy="22" r="20" fill="none" stroke="#c9a227" stroke-width="0.8" opacity="0.6"/>
    <circle cx="22" cy="22" r="12" fill="none" stroke="#c9a227" stroke-width="0.8" opacity="0.5"/>
    <circle cx="22" cy="22" r="4" fill="#c9a227" opacity="0.9"/>
    <line x1="22" y1="2" x2="22" y2="42" stroke="#c9a227" stroke-width="0.4" opacity="0.4"/>
    <line x1="2" y1="22" x2="42" y2="22" stroke="#c9a227" stroke-width="0.4" opacity="0.4"/>
  </svg>
</footer>

</div>

<script>
const dates = __DATES__;
const obs = __OBS__;
const pred = __PRED__;
const gap = __GAP__;
const priSent = __PRI_SENT__;
const hpsObs = __HPS_OBS__;
const priHps = __PRI_HPS__;
const priComp = __PRI_COMP__;
const unrate = __UN__;
const dpayems = __DPAY__;
const jolts = __JOLTS__;

const TEST_START = "2020-01-01";

// palette
const VOID  = "#030303";
const VOID2 = "#0a0a0a";
const BONE  = "#f0e8d0";
const BONE2 = "#c8bfa3";
const EMBER = "#c9a227";
const EMBER2= "#e3c151";
const RUST  = "#b35900";
const CRIM  = "#8a2c20";
const MOSS  = "#6b8a4a";
const SLATE = "#6a8aa8";
const LINE  = "#2a2620";
const MUTED = "#7a7060";

const baseLayout = {
  paper_bgcolor: VOID2,
  plot_bgcolor: VOID2,
  font: { family: "IBM Plex Mono, monospace", size: 11, color: BONE2 },
  margin: { l: 56, r: 56, t: 14, b: 36 },
  hovermode: "x unified",
  hoverlabel: { bgcolor: VOID, bordercolor: EMBER, font: { family: "IBM Plex Mono, monospace", color: BONE, size: 12 } },
  showlegend: true,
  legend: { orientation: "h", x: 0, y: 1.10, font: { size: 11, color: BONE2 }, bgcolor: "rgba(0,0,0,0)" },
  shapes: [{
    type: "rect", xref: "x", yref: "paper",
    x0: TEST_START, x1: dates[dates.length - 1],
    y0: 0, y1: 1,
    fillcolor: EMBER, opacity: 0.06, line: { width: 0 }, layer: "below"
  }, {
    type: "line", xref: "x", yref: "paper",
    x0: TEST_START, x1: TEST_START, y0: 0, y1: 1,
    line: { color: EMBER, width: 0.8, dash: "dot" }
  }],
  annotations: [{
    xref: "x", yref: "paper",
    x: TEST_START, y: 1.04, text: "  out-of-sample 2020Q1→",
    showarrow: false, xanchor: "left",
    font: { size: 10, color: MUTED, family: "IBM Plex Mono, monospace" }
  }],
  xaxis: { gridcolor: LINE, zerolinecolor: LINE, color: BONE2, tickfont: { color: BONE2 } },
  yaxis: { gridcolor: LINE, zerolinecolor: LINE, color: BONE2, tickfont: { color: BONE2 } }
};
const cfg = { displayModeBar: false, responsive: true };

// Panel A — sentiment
Plotly.newPlot("chartA", [
  { x: dates, y: obs,  name: "Observed (Michigan)",          mode: "lines", line: { color: BONE,  width: 2.4 } },
  { x: dates, y: pred, name: "Macro-predicted (2010-19 rule)", mode: "lines", line: { color: EMBER, width: 2.4, dash: "dash" } }
], { ...baseLayout, yaxis: { ...baseLayout.yaxis, title: { text: "UMCSENT (1966Q1=100)", font: { color: BONE2 } } } }, cfg);

// Panel B — HPS
const hpsLayout = JSON.parse(JSON.stringify(baseLayout));
const hpsFiltered = dates.map((d, i) => hpsObs[i] !== null ? [d, hpsObs[i]] : null).filter(x => x);
hpsLayout.shapes = hpsLayout.shapes.concat([
  { type: "line", xref: "paper", yref: "y", x0: 0, x1: 1, y0: 10.8, y1: 10.8,
    line: { color: EMBER, width: 1.4, dash: "dash" } },
  { type: "rect", xref: "paper", yref: "y", x0: 0, x1: 1, y0: 10.8 - 1.5, y1: 10.8 + 1.5,
    fillcolor: EMBER, opacity: 0.10, line: { width: 0 }, layer: "below" }
]);
hpsLayout.annotations = hpsLayout.annotations.concat([{
  xref: "paper", yref: "y", x: 0.005, y: 10.8 + 1.8,
  text: "NHIS 2019 anchor (10.8 % ± 1σ)",
  showarrow: false, xanchor: "left", font: { color: EMBER, size: 10, family: "IBM Plex Mono, monospace" }
}]);
Plotly.newPlot("chartB", [
  { x: hpsFiltered.map(p => p[0]), y: hpsFiltered.map(p => p[1]),
    name: "HPS adults · anxiety or depression",
    mode: "lines+markers",
    line: { color: MOSS, width: 1.5 },
    marker: { size: 8, color: MOSS, line: { color: BONE, width: 0.5 } } }
], { ...hpsLayout, yaxis: { ...hpsLayout.yaxis, title: { text: "% of adults", font: { color: BONE2 } }, range: [0, 48] } }, cfg);

// Panel C — gap
const gapPos = gap.map(v => v !== null && v >= 0 ? v : null);
const gapNeg = gap.map(v => v !== null && v < 0 ? v : null);
Plotly.newPlot("chartC", [
  { x: dates, y: gapPos, name: "Sentiment shortfall", type: "bar",
    marker: { color: CRIM, opacity: 0.8 } },
  { x: dates, y: gapNeg, name: "Sentiment surplus",   type: "bar",
    marker: { color: SLATE, opacity: 0.8 } }
], { ...baseLayout, yaxis: { ...baseLayout.yaxis, title: { text: "Index points (predicted − observed)", font: { color: BONE2 } }, zeroline: true, zerolinecolor: BONE2, zerolinewidth: 0.6 }, bargap: 0.05 }, cfg);

// Panel D — composite + components
const compLayout = JSON.parse(JSON.stringify(baseLayout));
compLayout.shapes = compLayout.shapes.concat([
  { type: "line", xref: "paper", yref: "y", x0: 0, x1: 1, y0: 5,  y1: 5,  line: { color: MUTED, width: 0.4, dash: "dot" } },
  { type: "line", xref: "paper", yref: "y", x0: 0, x1: 1, y0: 10, y1: 10, line: { color: MUTED, width: 0.4, dash: "dot" } },
  { type: "line", xref: "paper", yref: "y", x0: 0, x1: 1, y0: 15, y1: 15, line: { color: MUTED, width: 0.4, dash: "dot" } },
  { type: "line", xref: "paper", yref: "y", x0: 0, x1: 1, y0: 0,  y1: 0,  line: { color: BONE2, width: 0.6 } }
]);
compLayout.annotations = compLayout.annotations.concat([
  { xref: "paper", yref: "y", x: 1.005, y: 5,  text: "+5σ",  showarrow: false, xanchor: "left", font: { color: MUTED, size: 10, family: "IBM Plex Mono, monospace" } },
  { xref: "paper", yref: "y", x: 1.005, y: 10, text: "+10σ", showarrow: false, xanchor: "left", font: { color: MUTED, size: 10, family: "IBM Plex Mono, monospace" } },
  { xref: "paper", yref: "y", x: 1.005, y: 15, text: "+15σ", showarrow: false, xanchor: "left", font: { color: MUTED, size: 10, family: "IBM Plex Mono, monospace" } }
]);
Plotly.newPlot("chartD", [
  { x: dates, y: priSent, name: "PRI · sentiment component",
    mode: "lines", line: { color: SLATE, width: 1.4 }, opacity: 0.7 },
  { x: dates, y: priHps,  name: "PRI · HPS component",
    mode: "markers", marker: { size: 8, color: MOSS, line: { color: BONE, width: 0.5 } } },
  { x: dates, y: priComp, name: "PRI · composite (mean)",
    mode: "lines", line: { color: EMBER, width: 3.0 },
    fill: "tozeroy", fillcolor: "rgba(201,162,39,0.12)" }
], { ...compLayout, yaxis: { ...compLayout.yaxis, title: { text: "PRI (σ above 2010-2019 baseline)", font: { color: BONE2 } } } }, cfg);

// table -----------------------------------------------------------------------
const tbody = document.getElementById("rows");
function fmt(v, dec=2) { return (v === null || v === undefined) ? "—" : v.toFixed(dec); }
function fmtInt(v) { return (v === null || v === undefined) ? "—" : Math.round(v).toLocaleString(); }

for (let i = dates.length - 1; i >= 0; i--) {
  const d = new Date(dates[i]);
  const q = Math.floor(d.getMonth() / 3) + 1;
  const ymd = `${d.getFullYear()}Q${q}`;
  const tr = document.createElement("tr");
  const gapCls = (gap[i] !== null && gap[i] > 0) ? "pos" : (gap[i] !== null && gap[i] < 0 ? "neg" : "");
  const priCls = (priComp[i] !== null && priComp[i] > 5) ? "crit"
               : (priComp[i] !== null && priComp[i] > 1) ? "pos"
               : (priComp[i] !== null && priComp[i] < -1) ? "neg" : "";
  tr.innerHTML =
    `<td>${ymd}</td>` +
    `<td>${fmt(unrate[i], 1)}</td>` +
    `<td>${fmt(dpayems[i], 2)}</td>` +
    `<td>${fmtInt(jolts[i])}</td>` +
    `<td>${fmt(obs[i], 1)}</td>` +
    `<td>${fmt(pred[i], 1)}</td>` +
    `<td class="${gapCls}">${fmt(gap[i], 1)}</td>` +
    `<td>${hpsObs[i] !== null ? hpsObs[i].toFixed(1) : "—"}</td>` +
    `<td>${fmt(priSent[i], 2)}</td>` +
    `<td>${priHps[i] !== null ? priHps[i].toFixed(2) : "—"}</td>` +
    `<td class="${priCls}">${fmt(priComp[i], 2)}</td>`;
  tbody.appendChild(tr);
}

// scroll reveal -------------------------------------------------------------
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add("in");
      io.unobserve(e.target);
    }
  });
}, { threshold: 0.08 });
document.querySelectorAll(".reveal").forEach(el => io.observe(el));
</script>
</body>
</html>
"""

HTML = (HTML
  .replace("__LATEST_Q__",       latest_q)
  .replace("__PRI_LATEST__",     f"{latest_pri:.1f}" if latest_pri is not None else "—")
  .replace("__PRI_MEAN__",       f"{mean_comp_22on:.1f}")
  .replace("__PEAK_Q__",         peak_q_str)
  .replace("__PRI_PEAK__",       f"{peak_pri:.1f}")
  .replace("__Q_ABOVE__",        str(q_above_5))
  .replace("__Q_POST__",         str(q_post))
  .replace("__LATEST_UN__",      f"{latest_un:.1f}")
  .replace("__LATEST_JOLTS__",   f"{latest_jolts_thou:,}")
  .replace("__LATEST_PRED__",    f"{latest_pred_sent:.1f}")
  .replace("__LATEST_OBS__",     f"{latest_obs_sent:.1f}")
  .replace("__LAST_HPS__",       f"{last_hps_val:.1f}")
  .replace("__FIT_TEXT__",       fit_text.replace("<", "&lt;").replace(">", "&gt;"))
  .replace("__FETCH_DATE__",     datetime.date.today().isoformat())
  .replace("__DATES__",          json.dumps(dates_iso))
  .replace("__OBS__",            json.dumps(obs))
  .replace("__PRED__",           json.dumps(pred))
  .replace("__GAP__",            json.dumps(gap))
  .replace("__PRI_SENT__",       json.dumps(pri_sent))
  .replace("__HPS_OBS__",        json.dumps(hps_obs))
  .replace("__PRI_HPS__",        json.dumps(pri_hps))
  .replace("__PRI_COMP__",       json.dumps(pri_comp))
  .replace("__UN__",             json.dumps(unrate))
  .replace("__DPAY__",           json.dumps(dpayems))
  .replace("__JOLTS__",          json.dumps(jolts))
)

(OUT / "pri_dashboard_v2.html").write_text(HTML)
print(f"Wrote {OUT / 'pri_dashboard_v2.html'}  ({len(HTML):,} bytes)")
