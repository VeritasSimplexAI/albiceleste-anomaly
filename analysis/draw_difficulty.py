"""Draw difficulty across time, Elo view (pots/FIFA-rank views join when
data/seedings/ lands).

Per tournament 1990-2026:
  A) Group difficulty = mean pre-tournament Elo of a team's 3 group opponents.
     Argentina's value, its rank among the presumptive top seeds' groups
     (top-N teams by Elo, N = number of groups), and its percentile among ALL teams.
  B) Knockout path = mean Elo of actual knockout opponents faced; Argentina vs
     the other semifinalists of the same tournament.
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
ROOT = rf"{_ROOT}"
P = rf"{ROOT}\data\processed"

elo = pd.concat([
    pd.read_csv(rf"{ROOT}\data\elo\elo_pre_tournament.csv", encoding="utf-8-sig"),
    pd.read_csv(rf"{ROOT}\data\elo\elo_pre_tournament_1930_1986.csv", encoding="utf-8-sig"),
], ignore_index=True)
E = elo.set_index(["tournament_year", "team"]).elo

ml = pd.read_csv(rf"{P}\match_team_level.csv")  # full history 1930-2022
m26 = pd.read_csv(rf"{ROOT}\data\worldcup-2026\matches_2026.csv", encoding="utf-8-sig")

# ---------- group membership (FIRST group stage only; 1934/38 were pure knockout) ----------
grp_rows = []
g22 = ml[ml.stage_name == "group stage"]
for r in g22.itertuples():
    grp_rows.append(dict(year=r.year, team=r.team_name, group=r.group_name))
for r in m26[m26.stage == "Group stage"].itertuples():
    grp_rows.append(dict(year=2026, team=r.home_team, group=r.group_name))
    grp_rows.append(dict(year=2026, team=r.away_team, group=r.group_name))
groups = pd.DataFrame(grp_rows).drop_duplicates()

# ---------- A) group difficulty ----------
rows = []
for (yr, grp), g in groups.groupby(["year", "group"]):
    teams = list(g.team)
    for t in teams:
        opps = [o for o in teams if o != t]
        elos = [E.get((yr, o), np.nan) for o in opps]
        rows.append(dict(year=yr, team=t, group=grp, n_opps=len(opps),
                         opp_elo_mean=np.nanmean(elos),
                         own_elo=E.get((yr, t), np.nan)))
gd = pd.DataFrame(rows)
missing = gd[gd.opp_elo_mean.isna() | gd.own_elo.isna()]
if len(missing):
    print("WARNING missing Elo:", missing[["year", "team"]].to_string())

out = []
for yr, g in gd.groupby("year"):
    n_groups = g.group.nunique()
    seeds = g.nlargest(n_groups, "own_elo")  # presumptive Pot-1 proxy until real pots land
    a = g[g.team == "Argentina"]
    if a.empty: continue
    a = a.iloc[0]
    seed_diffs = seeds.set_index("team").opp_elo_mean
    arg_in_seeds = "Argentina" in seed_diffs.index
    rank_among_seeds = int((seed_diffs > a.opp_elo_mean).sum()) + 1
    pctl_all = round(100 * (g.opp_elo_mean < a.opp_elo_mean).mean(), 1)
    out.append(dict(year=yr, arg_group=a.group, arg_opp_elo_mean=round(a.opp_elo_mean, 1),
                    tournament_mean=round(g.opp_elo_mean.mean(), 1),
                    diff_vs_mean=round(a.opp_elo_mean - g.opp_elo_mean.mean(), 1),
                    rank_among_seeds=f"{rank_among_seeds}/{n_groups}",
                    arg_is_top_elo_seed=arg_in_seeds,
                    pctl_vs_all_teams=pctl_all))
gdiff = pd.DataFrame(out)
gd.to_csv(rf"{P}\draw_group_difficulty_all_teams.csv", index=False)
gdiff.to_csv(rf"{P}\draw_argentina_group_difficulty.csv", index=False)
print("=== A) Argentina group difficulty (opponents' mean Elo; rank 1 = HARDEST group among top seeds) ===")
print(gdiff.to_string(index=False))

# ---------- B) knockout path ----------
ko_rows = []
ko22 = ml[(ml.knockout_stage == 1)]
for r in ko22.itertuples():
    ko_rows.append(dict(year=r.year, team=r.team_name, opp=r.opponent_name))
for r in m26[m26.stage != "Group stage"].itertuples():
    ko_rows.append(dict(year=2026, team=r.home_team, opp=r.away_team))
    ko_rows.append(dict(year=2026, team=r.away_team, opp=r.home_team))
ko = pd.DataFrame(ko_rows)
ko["opp_elo"] = [E.get((y, o), np.nan) for y, o in zip(ko.year, ko.opp)]
kagg = ko.groupby(["year", "team"]).agg(ko_matches=("opp", "size"),
                                        ko_opp_elo_mean=("opp_elo", "mean")).reset_index()
kagg.to_csv(rf"{P}\draw_ko_path_all_teams.csv", index=False)
print("\n=== B) Knockout-path difficulty: Argentina vs same-year semifinalists (mean opponent Elo, KO only) ===")
for yr in sorted(kagg[kagg.team == "Argentina"].year.unique()):
    g = kagg[kagg.year == yr]
    semi = g[g.ko_matches >= 3].sort_values("ko_opp_elo_mean", ascending=False)
    a = g[g.team == "Argentina"].iloc[0]
    tag = " <- Argentina"
    line = ", ".join(f"{r.team} {r.ko_opp_elo_mean:.0f}" + (tag if r.team == "Argentina" else "")
                     for r in semi.itertuples())
    if "Argentina" not in list(semi.team):
        line += f" | Argentina ({int(a.ko_matches)} KO) {a.ko_opp_elo_mean:.0f}{tag}"
    print(f"{yr}: {line}")
print("\n(2026 Argentina KO opponents: " + ", ".join(
    f"{r.opp} ({r.opp_elo:.0f})" for r in ko[(ko.year == 2026) & (ko.team == 'Argentina')].itertuples()) + ")")
