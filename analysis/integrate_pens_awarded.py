"""Penalties AWARDED (decision metric) — integrate the 1990-2010 per-incident
compilation into per-team tables and run Argentina-vs-field tests for that span.
2014-2026 awarded data joins when the FBref squad_discipline file lands.
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys
import pandas as pd
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8")
P = rf"{_ROOT}\data\processed"
pens = pd.read_csv(rf"{_ROOT}\data\penalties-historical\penalties_awarded_1990_2010.csv",
                   encoding="utf-8-sig")
tourn = pd.read_csv(rf"{P}\team_tournament_stats.csv")
# align naming with the fjelstul dataset
for col in ["team_awarded", "opponent"]:
    pens[col] = pens[col].replace({"Ireland": "Republic of Ireland"})

# per team per tournament: awarded for / against
pf = pens.groupby(["tournament_year", "team_awarded"]).size().rename("pens_awarded_for")
pa = pens.groupby(["tournament_year", "opponent"]).size().rename("pens_awarded_against")
base = tourn[(tourn.year >= 1990) & (tourn.year <= 2010)][["year", "team_name", "matches"]]
base = (base.set_index(["year", "team_name"])
        .join(pf.rename_axis(["year", "team_name"]))
        .join(pa.rename_axis(["year", "team_name"]))
        .fillna(0).astype(int).reset_index())
base.to_csv(rf"{P}\pens_awarded_team_1990_2010.csv", index=False)

# consistency: every compiled penalty must map onto a known team-tournament
unmatched_for = pf.sum() - base.pens_awarded_for.sum()
unmatched_against = pa.sum() - base.pens_awarded_against.sum()
if unmatched_for or unmatched_against:
    print(f"WARNING: unmatched team names — for:{unmatched_for} against:{unmatched_against}")
    known = set(tourn.team_name)
    bad = set(pens.team_awarded) | set(pens.opponent)
    print("  names not in dataset:", sorted(n for n in bad if n not in known))

agg = base.groupby("team_name")[["matches", "pens_awarded_for", "pens_awarded_against"]].sum()
arg = agg.loc["Argentina"]
fld = agg.drop(index="Argentina").sum()

print("=== Penalties AWARDED, 1990-2010 (decision metric) ===")
for met, fav in [("pens_awarded_for", "high"), ("pens_awarded_against", "low")]:
    c_a, m_a, c_f, m_f = int(arg[met]), int(arg.matches), int(fld[met]), int(fld.matches)
    p = stats.binomtest(c_a, c_a + c_f, m_a / (m_a + m_f)).pvalue
    print(f"{met:22s} Argentina {c_a}/{m_a} = {c_a/m_a:.3f}/match | field {c_f/m_f:.3f}/match "
          f"| ratio {(c_a/m_a)/(c_f/m_f):.2f} | p={p:.3f} (favorable if {fav})")

top = agg[agg.matches >= 10].copy()
top["net_pm"] = (top.pens_awarded_for - top.pens_awarded_against) / top.matches
print("\nTop-8 net awarded-penalty advantage per match (teams >=10 matches):")
print(top.nlargest(8, "net_pm")[["matches", "pens_awarded_for", "pens_awarded_against", "net_pm"]]
      .to_string(float_format=lambda x: f"{x:+.3f}"))
