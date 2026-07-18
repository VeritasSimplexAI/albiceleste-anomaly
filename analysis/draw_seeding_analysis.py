"""Draw difficulty, full three-metric view: opponents' Elo, official draw pots,
and pre-tournament FIFA ranks — Argentina vs the other Pot-1 seeds, 1990-2026.
Plus realized knockout-path difficulty by stage with seeding context.

Rank conventions (1 = HARDEST draw among Pot-1 teams):
  elo:  highest opponents' mean Elo
  pot:  lowest opponents' pot sum (low pots = strong opponents)
  fifa: lowest opponents' mean FIFA rank (low rank number = strong)
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
ROOT = rf"{_ROOT}"
P = rf"{ROOT}\data\processed"

pots = pd.read_csv(rf"{ROOT}\data\seedings\draw_pots.csv", encoding="utf-8-sig")
fifa = pd.read_csv(rf"{ROOT}\data\seedings\fifa_rankings_pre.csv", encoding="utf-8-sig")
POT = pots.set_index(["tournament_year", "team"]).pot
SEEDED = pots[pots.seeded == "yes"].groupby("tournament_year").team.apply(set)
FIFA = fifa.set_index(["tournament_year", "team"]).fifa_rank
gd = pd.read_csv(rf"{P}\draw_group_difficulty_all_teams.csv")  # year, team, group, opp_elo_mean, own_elo

# opponents' pot sum + fifa mean per team (via group membership)
rows = []
for (yr, grp), g in gd.groupby(["year", "group"]):
    teams = list(g.team)
    for t in teams:
        opps = [o for o in teams if o != t]
        rows.append(dict(year=yr, team=t,
                         opp_pot_sum=sum(POT.get((yr, o), np.nan) for o in opps),
                         opp_fifa_mean=np.mean([FIFA.get((yr, o), np.nan) for o in opps])))
extra = pd.DataFrame(rows)
gd = gd.merge(extra, on=["year", "team"])
gd.to_csv(rf"{P}\draw_group_difficulty_all_metrics.csv", index=False)

print("=== Argentina group draw vs other Pot-1 seeds (rank 1 = HARDEST) ===")
summary = []
for yr, g in gd.groupby("year"):
    seeds = g[g.team.isin(SEEDED.get(yr, set()))]
    if "Argentina" not in list(seeds.team):
        continue
    a = seeds[seeds.team == "Argentina"].iloc[0]
    n = len(seeds)
    r_elo = int((seeds.opp_elo_mean > a.opp_elo_mean).sum()) + 1
    r_pot = int((seeds.opp_pot_sum < a.opp_pot_sum).sum()) + 1
    r_fifa = (int((seeds.opp_fifa_mean < a.opp_fifa_mean).sum()) + 1) if not np.isnan(a.opp_fifa_mean) else None
    summary.append(dict(year=yr, group=a.group,
                        opp_elo_mean=round(a.opp_elo_mean, 0), elo_rank=f"{r_elo}/{n}",
                        opp_pot_sum=int(a.opp_pot_sum) if not np.isnan(a.opp_pot_sum) else None,
                        pot_rank=f"{r_pot}/{n}",
                        opp_fifa_mean=round(a.opp_fifa_mean, 1) if not np.isnan(a.opp_fifa_mean) else None,
                        fifa_rank_rank=f"{r_fifa}/{n}" if r_fifa else "n/a"))
sm = pd.DataFrame(summary)
sm.to_csv(rf"{P}\draw_argentina_three_metrics.csv", index=False)
print(sm.to_string(index=False))

# ---------- realized KO path with seeding context ----------
ko = pd.read_csv(rf"{P}\draw_ko_by_stage.csv")
ko["opp_pot"] = [POT.get((y, o), np.nan) for y, o in zip(ko.year, ko.opp)]
ko["opp_fifa"] = [FIFA.get((y, o), np.nan) for y, o in zip(ko.year, ko.opp)]
ko.to_csv(rf"{P}\draw_ko_by_stage_enriched.csv", index=False)

for yr in [2022, 2026]:
    g = ko[(ko.year == yr) & (ko.stage != "third place")]
    deep = g.groupby("team").size()
    deep = deep[deep >= 3].index
    print(f"\n=== {yr} knockout paths of deep-run teams (opponent pot in brackets) ===")
    agg = []
    for t in deep:
        p = g[g.team == t]
        agg.append(dict(team=t, path_elo=round(p.opp_elo.mean(), 0),
                        path_pot_mean=round(p.opp_pot.mean(), 2),
                        path_fifa_mean=round(p.opp_fifa.mean(), 1),
                        pot1_opponents=int((p.opp_pot == 1).sum()),
                        n=len(p)))
    ag = pd.DataFrame(agg).sort_values("path_elo")
    print(ag.to_string(index=False))
    a = g[g.team == "Argentina"].sort_values("opp_elo")
    print("Argentina route: " + " -> ".join(
        f"{r.opp} (pot {int(r.opp_pot) if not np.isnan(r.opp_pot) else '?'}, FIFA {int(r.opp_fifa) if not np.isnan(r.opp_fifa) else '—'}, Elo {r.opp_elo:.0f})"
        for r in g[g.team == 'Argentina'].itertuples()))
