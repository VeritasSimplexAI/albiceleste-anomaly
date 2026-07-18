"""Stage-by-stage knockout opponents (Elo) — Argentina vs rival deep-run teams.
Output: processed/draw_ko_by_stage.csv + console pivot per tournament.
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

STAGE_ORDER = ["round of 32", "round of 16", "quarter-finals", "semi-finals", "third place", "final"]
NORM = {"Round of 32": "round of 32", "Round of 16": "round of 16", "Quarterfinals": "quarter-finals",
        "Semifinals": "semi-finals", "quarter-final": "quarter-finals", "semi-final": "semi-finals",
        "third place match": "third place", "third-place match": "third place"}

ml = pd.read_csv(rf"{P}\match_team_level.csv")
ml = ml[ml.knockout_stage == 1]
rows = [dict(year=r.year, team=r.team_name, stage=NORM.get(r.stage_name, r.stage_name.lower()),
             opp=r.opponent_name) for r in ml.itertuples()]
m26 = pd.read_csv(rf"{ROOT}\data\worldcup-2026\matches_2026.csv", encoding="utf-8-sig")
for r in m26[m26.stage != "Group stage"].itertuples():
    st = NORM.get(r.stage, r.stage.lower())
    rows.append(dict(year=2026, team=r.home_team, stage=st, opp=r.away_team))
    rows.append(dict(year=2026, team=r.away_team, stage=st, opp=r.home_team))
ko = pd.DataFrame(rows)
ko["opp_elo"] = [E.get((y, o), np.nan) for y, o in zip(ko.year, ko.opp)]
ko.to_csv(rf"{P}\draw_ko_by_stage.csv", index=False)

for yr in [2022, 2026]:
    g = ko[ko.year == yr]
    deep = g.groupby("team").size()
    deep = deep[deep >= 3].index  # semifinalists
    print(f"\n=== {yr}: stage-by-stage opponents (Elo), deep-run teams ===")
    for t in deep:
        path = g[g.team == t].copy()
        path["o"] = pd.Categorical(path.stage, STAGE_ORDER, ordered=True)
        path = path.sort_values("o")
        line = " -> ".join(f"{r.stage.split()[0][:5].upper()}: {r.opp} ({r.opp_elo:.0f})"
                           for r in path.itertuples() if r.stage != "third place")
        mean = path[path.stage != "third place"].opp_elo.mean()
        print(f"{t:12s} (path mean {mean:.0f}): {line}")

print("\n=== Argentina KO opponents by stage, all tournaments ===")
ag = ko[ko.team == "Argentina"].copy()
ag["o"] = pd.Categorical(ag.stage, STAGE_ORDER, ordered=True)
for yr, g in ag.groupby("year"):
    line = " -> ".join(f"{r.stage}: {r.opp} ({r.opp_elo:.0f})" for r in g.sort_values("o").itertuples())
    print(f"{yr}: {line}")
