"""Deep statistical analysis: EB shrinkage rankings, FDR outlier scan,
difference-in-differences, Poisson GLM with stage/tournament controls,
and a 2022 deep-run cohort comparison. 1990-2022 for now; rerun after the
2026 files land to extend eras.

Run build_stats.py first (produces data/processed/*).
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys, os
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

sys.stdout.reconfigure(encoding="utf-8")
P = rf"{_ROOT}\data\processed"

era = pd.read_csv(rf"{P}\team_era_stats.csv")
tourn = pd.read_csv(rf"{P}\team_tournament_stats.csv")
ml = pd.read_csv(rf"{P}\match_team_level.csv")

METRICS = ["yellows_received", "dismissals_received", "yellows_drawn",
           "dismissals_drawn", "pen_goals_for", "pen_goals_against"]
GOOD_HIGH = {"yellows_drawn", "dismissals_drawn", "pen_goals_for"}  # favorable when high

# ---------- A) Empirical-Bayes (Gamma-Poisson) shrunk rankings ----------
def eb_shrink(df, metric):
    c, n = df[metric].to_numpy(float), df["matches"].to_numpy(float)
    mu = c.sum() / n.sum()
    rate = c / n
    w = n / n.sum()
    between = max((w * (rate - mu) ** 2).sum() - mu * (w / n).sum(), 1e-9)
    k = mu / between  # prior strength in "matches"
    return (c + mu * k) / (n + k)

eb_rows = []
for e, g in era.groupby("era"):
    g = g.copy()
    for met in METRICS:
        g[f"eb_{met}"] = eb_shrink(g, met)
    g["eb_card_net"] = g.eb_yellows_drawn - g.eb_yellows_received
    g["eb_pen_net"] = g.eb_pen_goals_for - g.eb_pen_goals_against
    for col in ["eb_card_net", "eb_pen_net"]:
        g[f"{col}_rank"] = g[col].rank(ascending=False, method="min").astype(int)
    eb_rows.append(g)
eb = pd.concat(eb_rows)
eb.to_csv(rf"{P}\eb_rankings.csv", index=False)

print("=== A) EB-shrunk favorability ranks (1 = most favored) ===")
for e, g in eb.groupby("era"):
    a = g[g.team_name == "Argentina"]
    if a.empty: continue
    nteams = len(g)
    print(f"{e}: card_net rank {int(a.eb_card_net_rank.iloc[0])}/{nteams} "
          f"(net {a.eb_card_net.iloc[0]:+.2f}/match), "
          f"pen_net rank {int(a.eb_pen_net_rank.iloc[0])}/{nteams} "
          f"(net {a.eb_pen_net.iloc[0]:+.3f}/match)")
    top = g.nsmallest(5, "eb_card_net_rank")[["team_name", "eb_card_net", "matches"]]
    print("  top-5 card_net:", ", ".join(f"{r.team_name} ({r.eb_card_net:+.2f}, {int(r.matches)}m)" for r in top.itertuples()))
    topp = g.nsmallest(5, "eb_pen_net_rank")[["team_name", "eb_pen_net", "matches"]]
    print("  top-5 pen_net: ", ", ".join(f"{r.team_name} ({r.eb_pen_net:+.3f}, {int(r.matches)}m)" for r in topp.itertuples()))

# ---------- B) FDR outlier scan: every team vs rest, per era & metric ----------
fdr_rows = []
for e, g in era.groupby("era"):
    Mtot = g.matches.sum()
    for met in METRICS:
        Ctot = g[met].sum()
        if Ctot == 0: continue
        for r in g.itertuples():
            c, n = getattr(r, met), r.matches
            if n < 3: continue
            p = stats.binomtest(int(c), int(Ctot), n / Mtot).pvalue
            direction = "high" if c / n > Ctot / Mtot else "low"
            favorable = (direction == "high") == (met in GOOD_HIGH)
            fdr_rows.append(dict(era=e, metric=met, team=r.team_name, matches=n,
                                 count=c, rate=c / n, field_rate=Ctot / Mtot,
                                 direction=direction, favorable=favorable, p=p))
fdr = pd.DataFrame(fdr_rows)
def bh(pvals, q=0.10):
    s = np.sort(pvals); k = np.arange(1, len(s) + 1)
    ok = s <= q * k / len(s)
    return s[ok].max() if ok.any() else 0.0
fdr["signif_fdr10"] = False
for e in fdr.era.unique():
    mask = fdr.era == e
    thr = bh(fdr.loc[mask, "p"].to_numpy())
    fdr.loc[mask, "signif_fdr10"] = fdr.loc[mask, "p"] <= thr
fdr.to_csv(rf"{P}\fdr_outliers.csv", index=False)
sig = fdr[fdr.signif_fdr10].sort_values(["era", "p"])
print("\n=== B) FDR(10%) significant outliers (all teams, all metrics) ===")
print(sig[["era", "metric", "team", "matches", "count", "rate", "field_rate",
           "direction", "favorable", "p"]].to_string(index=False,
      float_format=lambda x: f"{x:.4f}"))

# ---------- C) Difference-in-differences (needs both eras) ----------
pre = era[era.era == "1990-2018"].set_index("team_name")
post = era[era.era == "2022"].set_index("team_name")
common = [t for t in post.index if t in pre.index and pre.loc[t, "matches"] >= 8 and post.loc[t, "matches"] >= 3]
did_rows = []
for t in common:
    d = {}
    for name, hi, lo in [("card_net", "yellows_drawn", "yellows_received"),
                         ("pen_net", "pen_goals_for", "pen_goals_against")]:
        pre_rate = (pre.loc[t, hi] - pre.loc[t, lo]) / pre.loc[t, "matches"]
        post_rate = (post.loc[t, hi] - post.loc[t, lo]) / post.loc[t, "matches"]
        d[f"{name}_pre"], d[f"{name}_post"], d[f"{name}_change"] = pre_rate, post_rate, post_rate - pre_rate
    did_rows.append(dict(team=t, pre_matches=pre.loc[t, "matches"], post_matches=post.loc[t, "matches"], **d))
did = pd.DataFrame(did_rows).sort_values("card_net_change", ascending=False)
did.to_csv(rf"{P}\did_results.csv", index=False)
print("\n=== C) Difference-in-differences, 1990-2018 -> 2022 (teams w/ >=8 pre, >=3 post matches) ===")
print(did.to_string(index=False, float_format=lambda x: f"{x:+.3f}" if isinstance(x, float) else str(x)))

# ---------- D) Poisson GLM at match level ----------
ml["is_arg"] = (ml.team_name == "Argentina").astype(int)
ml["post2022"] = (ml.year >= 2022).astype(int)
ml["knockout"] = ml.knockout_stage.astype(int)
print("\n=== D) Poisson GLM (match level, cluster-robust SE by team) ===")
for outcome in ["opp_yellows", "yellows", "pen_goals", "opp_pen_goals"]:
    f = f"{outcome} ~ is_arg + is_arg:post2022 + knockout + C(year)"
    mod = smf.glm(f, data=ml, family=sm.families.Poisson()).fit(
        cov_type="cluster", cov_kwds={"groups": ml.team_name})
    for term in ["is_arg", "is_arg:post2022"]:
        b, se, p = mod.params[term], mod.bse[term], mod.pvalues[term]
        print(f"{outcome:15s} {term:18s} IRR={np.exp(b):5.2f}  95%CI=({np.exp(b-1.96*se):.2f},{np.exp(b+1.96*se):.2f})  p={p:.4f}")

# ---------- E) 2022 deep-run cohort ----------
deep = tourn[(tourn.year == 2022) & (tourn.matches >= 5)].copy()
deep["card_net_pm"] = (deep.yellows_drawn - deep.yellows_received) / deep.matches
deep["pen_net_pm"] = (deep.pen_goals_for - deep.pen_goals_against) / deep.matches
deep["pens_for_pm"] = deep.pen_goals_for / deep.matches
print("\n=== E) 2022 deep-run cohort (>=5 matches) ===")
print(deep[["team_name", "matches", "card_net_pm", "pen_net_pm", "pens_for_pm"]]
      .sort_values("card_net_pm", ascending=False)
      .to_string(index=False, float_format=lambda x: f"{x:+.3f}"))
deep.to_csv(rf"{P}\cohort_2022.csv", index=False)
