"""
Psychological Recession Index (PRI) — v2 estimation
===================================================
Improvements over v1:
    * Richer macro RHS: + log(JTSJOL) captures vacancy-side tightness.
    * Two outcome series:
        (a) UMCSENT (sentiment-as-psychiatric-proxy, monthly→quarterly)
        (b) HPS_ANXDEP (Census/CDC anxiety+depression %, post-2020 + NHIS 2019 anchor)
    * Composite PRI = mean of standardized residuals across available outcomes.

Method:
    1. Fit baseline OLS on UMCSENT 2010Q1-2019Q4 (training window) with macro RHS.
    2. Project predicted sentiment through 2026.
    3. PRI_sent(t) = standardized residual from that model.
    4. For HPS, use the published 2019 NHIS pre-pandemic anchor (10.8%) as
       the baseline value and the HPS waves 2020-2025 as observations.
       Compute PRI_hps as deviation from baseline in σ units (where σ is
       NHIS pre-pandemic year-to-year SD, conservatively 1.5pp).
    5. Composite PRI = mean(PRI_sent, PRI_hps) when both available; else
       the available one. This is the multi-indicator construct definition
       from the paper's PRI specification.

Output:
    figures/pri_v2_paper.png    -- museum-quality figure for paper
    figures/pri_v2_paper.pdf    -- vector version
    output/pri_v2_quarterly.csv -- the underlying data
    output/pri_v2_fit.txt       -- OLS regression results
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import statsmodels.api as sm

ROOT = Path("/home/claude/pri")
DATA = ROOT / "data"
FIG  = ROOT / "figures"
OUT  = ROOT / "output"
for p in (FIG, OUT): p.mkdir(exist_ok=True)


def load_series(name: str) -> pd.Series:
    df = pd.read_csv(DATA / f"{name}.csv", comment="#",
                     parse_dates=["DATE"]).set_index("DATE")
    s = pd.to_numeric(df["VALUE"], errors="coerce").rename(name)
    s.index.name = "date"
    return s

# ------------------------------------------------------ load monthly inputs --
unrate = load_series("UNRATE")
payems = load_series("PAYEMS")
umcsent = load_series("UMCSENT")
jtsjol = load_series("JTSJOL")
hps    = load_series("HPS_ANXDEP")    # irregular cadence

print("Series loaded.")
for s in (unrate, payems, umcsent, jtsjol, hps):
    print(f"  {s.name:<10} {s.index.min().date()} → {s.index.max().date()}  n={s.notna().sum()}")

# ----------------------------------------------------- quarterly aggregate --
def Q(s): return s.resample("QS").mean()

q = pd.DataFrame({
    "unrate":   Q(unrate),
    "payems":   Q(payems),
    "umcsent":  Q(umcsent),
    "jtsjol":   Q(jtsjol),
})
q["dpayems_yoy"] = q["payems"].pct_change(4) * 100
q["log_jolts"]   = np.log(q["jtsjol"])
q["hps"]         = Q(hps)

panel = q.dropna(subset=["umcsent", "unrate", "dpayems_yoy", "log_jolts"])
print(f"\nQuarterly panel: {len(panel)} obs, "
      f"{panel.index.min().date()} → {panel.index.max().date()}")

# ----------------------------------------------------------- baseline fit --
TRAIN_END = pd.Timestamp("2019-10-01")
TEST_START = pd.Timestamp("2020-01-01")
train = panel.loc[:TRAIN_END]
test  = panel.loc[TEST_START:]
print(f"Training  2010Q1-2019Q4  n={len(train)}")
print(f"Test      2020Q1-{panel.index.max().strftime('%YQ%q').replace('Q1','Q1').replace('Q2','Q2').replace('Q3','Q3').replace('Q4','Q4')}  n={len(test)}")

# Sentiment model with richer macro RHS
X_train = sm.add_constant(train[["unrate", "dpayems_yoy", "log_jolts"]])
y_train = train["umcsent"]
m_sent = sm.OLS(y_train, X_train).fit()

print("\n" + "=" * 70)
print("V2 BASELINE OLS — UMCSENT ~ UNRATE + ΔPAYEMS_yoy + log(JTSJOL)")
print("=" * 70)
print(m_sent.summary().as_text())

res_train = y_train - m_sent.predict(X_train)
sigma_sent = float(res_train.std(ddof=1))
print(f"\nBaseline residual σ  = {sigma_sent:.3f} sentiment-index points")

# project full sample
X_full = sm.add_constant(panel[["unrate", "dpayems_yoy", "log_jolts"]])
pred_sent = m_sent.predict(X_full).rename("predicted_sentiment")
obs_sent  = panel["umcsent"].rename("observed_sentiment")
gap_sent  = (pred_sent - obs_sent).rename("sentiment_gap")
pri_sent  = (gap_sent / sigma_sent).rename("pri_sentiment")

# ---------------------------------------------- HPS deviation from baseline --
# NHIS 2019 pre-pandemic anchor = 10.8% (Vahratian 2021)
# Conservative σ for year-to-year NHIS variation in this prevalence: ~1.5 pp
NHIS_2019  = 10.8
SIGMA_HPS  = 1.5   # pre-pandemic year-to-year SD for K6-equivalent prevalence
hps_q      = panel["hps"].dropna()
pri_hps_q  = ((hps_q - NHIS_2019) / SIGMA_HPS).rename("pri_hps")

# ------------------------------- composite PRI = mean of available indicators
pri_components = pd.DataFrame({"sent": pri_sent, "hps": pri_hps_q})
pri_composite = pri_components.mean(axis=1, skipna=True).rename("pri_composite")

# only count composite where at least one indicator is present
mask = pri_components.notna().any(axis=1)
pri_composite = pri_composite.where(mask)

# assemble result
result = pd.concat([
    panel["unrate"].rename("unrate"),
    panel["dpayems_yoy"].rename("dpayems_yoy"),
    panel["jtsjol"].rename("jtsjol_thousands"),
    obs_sent, pred_sent, gap_sent, pri_sent,
    panel["hps"].rename("hps_obs"), pri_hps_q,
    pri_composite,
], axis=1)
result.to_csv(OUT / "pri_v2_quarterly.csv", float_format="%.3f")
print(f"\nWrote {OUT / 'pri_v2_quarterly.csv'}")

# ----------------------------------------------------- headline numbers --
LATEST = panel.index.max()
print(f"\nLatest quarter ({LATEST.date()}):")
print(f"  unemployment        = {result.loc[LATEST, 'unrate']:>6.2f}%")
print(f"  observed sentiment  = {result.loc[LATEST, 'observed_sentiment']:>6.1f}")
print(f"  predicted sentiment = {result.loc[LATEST, 'predicted_sentiment']:>6.1f}")
print(f"  PRI (sentiment)     = {result.loc[LATEST, 'pri_sentiment']:>6.2f}σ")
last_hps = result["pri_hps"].dropna()
if not last_hps.empty:
    print(f"  PRI (HPS, latest)   = {last_hps.iloc[-1]:>6.2f}σ")
print(f"  Composite PRI       = {result.loc[LATEST, 'pri_composite']:>6.2f}σ")

mean_pri_22on = pri_composite.loc["2022-01-01":].mean()
peak = pri_composite.idxmax()
print(f"\nMean composite PRI 2022Q1→ : {mean_pri_22on:.2f}σ")
print(f"Peak composite PRI         : {pri_composite.max():.2f}σ ({peak.date()})")

# save fit summary
with open(OUT / "pri_v2_fit.txt", "w") as f:
    f.write("PRI v2 — sentiment fit\n")
    f.write("OLS  UMCSENT ~ UNRATE + ΔPAYEMS_yoy + log(JTSJOL)\n")
    f.write("Training window: 2010Q1 - 2019Q4\n")
    f.write("=" * 70 + "\n")
    f.write(m_sent.summary().as_text() + "\n\n")
    f.write(f"Residual σ = {sigma_sent:.3f} sentiment-index points\n\n")
    f.write("HPS series anchored to NHIS 2019 (10.8%); σ_baseline = 1.5pp\n\n")
    f.write(f"Latest composite PRI ({LATEST.date()}) = "
            f"{result.loc[LATEST, 'pri_composite']:.2f}σ above baseline\n")

# =============================================================================
#                          MUSEUM-QUALITY FIGURE
# =============================================================================
plt.rcParams.update({
    "font.family"       : "DejaVu Serif",
    "mathtext.fontset"  : "dejavuserif",
    "font.size"         : 10.5,
    "axes.titlesize"    : 11,
    "axes.titleweight"  : "bold",
    "axes.labelsize"    : 10,
    "axes.spines.top"   : False,
    "axes.spines.right" : False,
    "axes.edgecolor"    : "#1a1a1a",
    "axes.labelcolor"   : "#1a1a1a",
    "xtick.color"       : "#1a1a1a",
    "ytick.color"       : "#1a1a1a",
    "xtick.labelsize"   : 9.5,
    "ytick.labelsize"   : 9.5,
    "legend.fontsize"   : 9.5,
    "legend.frameon"    : False,
    "savefig.dpi"       : 200,
})

INK   = "#0b1d3a"      # deep navy — observed series
EMBER = "#b35900"      # rust orange — model prediction
RUST  = "#8a2c20"      # crimson — sentiment shortfall / PRI elevated
SLATE = "#4a6b8a"      # muted blue — sentiment surplus / negative PRI
MOSS  = "#3a6b3a"      # forest — HPS series
CREAM = "#faf8f3"
GREY  = "#888888"
LIGHT = "#e8dfc8"

fig = plt.figure(figsize=(10.5, 11.5))
gs = fig.add_gridspec(4, 1, hspace=0.55, top=0.94, bottom=0.06, left=0.10, right=0.95)
axA = fig.add_subplot(gs[0])
axB = fig.add_subplot(gs[1])
axC = fig.add_subplot(gs[2])
axD = fig.add_subplot(gs[3])

def shade_post(ax):
    ax.axvspan(TEST_START, panel.index.max(), color=LIGHT, alpha=0.45, zorder=0)
    ax.axvline(TEST_START, color=GREY, lw=0.6, ls=":")

# Panel A — sentiment observed vs predicted -----------------------------------
shade_post(axA)
axA.plot(obs_sent.index, obs_sent, color=INK, lw=1.8,
         label="Observed (Michigan Survey)")
axA.plot(pred_sent.index, pred_sent, color=EMBER, lw=1.8, ls="--",
         label="Macro-predicted (2010-2019 baseline rule)")
axA.set_title("A. Consumer sentiment: observed vs. what the macro state predicts",
              loc="left")
axA.set_ylabel("UMCSENT (1966Q1=100)")
axA.legend(loc="lower left", ncol=2)
axA.grid(axis="y", alpha=0.25, color=LIGHT)
axA.text(TEST_START, axA.get_ylim()[1]*0.97,
         "  out-of-sample (2020Q1→)", fontsize=8.5, color=GREY, va="top", style="italic")

# Panel B — psychiatric proxy: HPS anxiety+depression vs NHIS 2019 anchor -----
shade_post(axB)
hps_pts = panel["hps"].dropna()
axB.scatter(hps_pts.index, hps_pts.values, s=42, color=MOSS, zorder=4,
            label="HPS (anxiety or depression %, biweekly→quarterly)")
axB.plot(hps_pts.index, hps_pts.values, color=MOSS, lw=1.1, alpha=0.55)
axB.axhline(NHIS_2019, color=EMBER, lw=1.5, ls="--",
            label=f"NHIS 2019 pre-pandemic anchor = {NHIS_2019}%")
axB.axhspan(NHIS_2019 - SIGMA_HPS, NHIS_2019 + SIGMA_HPS,
            color=EMBER, alpha=0.10, lw=0,
            label=f"±1σ pre-pandemic ({SIGMA_HPS} pp)")
axB.set_title("B. Direct psychiatric outcome: HPS adult anxiety+depression vs. pre-pandemic NHIS",
              loc="left")
axB.set_ylabel("Percent of adults")
axB.legend(loc="lower right", ncol=1, fontsize=8.5)
axB.grid(axis="y", alpha=0.25, color=LIGHT)
axB.set_ylim(0, 48)

# Panel C — sentiment gap (predicted - observed) -------------------------------
shade_post(axC)
axC.fill_between(gap_sent.index, 0, gap_sent.values,
                 where=(gap_sent.values >= 0),
                 color=RUST, alpha=0.55, lw=0, label="Sentiment shortfall")
axC.fill_between(gap_sent.index, 0, gap_sent.values,
                 where=(gap_sent.values < 0),
                 color=SLATE, alpha=0.55, lw=0, label="Sentiment surplus")
axC.axhline(0, color="#1a1a1a", lw=0.7)
axC.set_title("C. Sentiment gap (predicted − observed, index points)",
              loc="left")
axC.set_ylabel("Index points")
axC.legend(loc="upper left", ncol=2)
axC.grid(axis="y", alpha=0.25, color=LIGHT)

# Panel D — composite PRI -----------------------------------------------------
shade_post(axD)
# component lines (thin, semi-transparent)
axD.plot(pri_sent.index, pri_sent.values, color=INK, lw=0.9, alpha=0.45,
         label="PRI · sentiment component")
axD.scatter(pri_hps_q.dropna().index, pri_hps_q.dropna().values,
            s=18, color=MOSS, alpha=0.7, label="PRI · HPS component")
# composite (thick)
axD.plot(pri_composite.index, pri_composite.values,
         color=RUST, lw=2.4, label="PRI · composite (mean)")
axD.fill_between(pri_composite.index, 0, pri_composite.values,
                 where=(pri_composite.values > 0),
                 color=RUST, alpha=0.18, lw=0)

# σ markers
xmin, xmax = pri_composite.index.min(), pri_composite.index.max()
for level in [5, 10, 15]:
    axD.axhline(level, color=GREY, lw=0.5, ls=(0, (1, 3)))
xlabel = xmax + pd.Timedelta(days=80)
for level, label in [(5, "+5σ"), (10, "+10σ"), (15, "+15σ")]:
    axD.text(xlabel, level, label, fontsize=8.5, color=GREY, va="center", ha="left")

axD.axhline(0, color="#1a1a1a", lw=0.7)
axD.set_title("D. Composite Psychological Recession Index (σ above 2010-2019 baseline)",
              loc="left")
axD.set_ylabel("PRI (σ)")
axD.legend(loc="upper left", ncol=3)
axD.grid(axis="y", alpha=0.25, color=LIGHT)

# uniform x-axis formatting -----------------------------------------------
for ax in (axA, axB, axC, axD):
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_minor_locator(mdates.YearLocator(1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlim(panel.index.min() - pd.Timedelta(days=90),
                panel.index.max() + pd.Timedelta(days=300))

fig.suptitle("The Psychological Recession Index, v2  ·  United States, 2010–2026  ·  "
             "macro-divergent psychiatric exposure",
             fontweight="bold", y=0.985, fontsize=13)

source_note = (
    "Sources: BLS via FRED (UNRATE, PAYEMS, JTSJOL); Surveys of Consumers, "
    "University of Michigan via FRED (UMCSENT, ©); U.S. Census Bureau / CDC NCHS "
    "Household Pulse Survey (HPS, modified PHQ-2 + GAD-2); NHIS 2019 (Vahratian "
    "et al., MMWR 2021).  Model: OLS  UMCSENT ~ UNRATE + ΔPAYEMS_yoy + log(JTSJOL), "
    "trained 2010Q1–2019Q4; PRI = standardized residual.  Composite = mean of "
    "available standardized residuals."
)
fig.text(0.5, 0.005, source_note, ha="center", color="#555",
         fontsize=7.8, style="italic", wrap=True)

fig.savefig(FIG / "pri_v2_paper.png", dpi=220, bbox_inches="tight",
            facecolor="white")
fig.savefig(FIG / "pri_v2_paper.pdf", bbox_inches="tight", facecolor="white")
print(f"\nWrote {FIG / 'pri_v2_paper.png'}")
print(f"Wrote {FIG / 'pri_v2_paper.pdf'}")
plt.close()
