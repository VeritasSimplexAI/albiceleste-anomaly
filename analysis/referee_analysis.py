"""Referee-teams study, 1990-2026: crew expansion, repeat officials
(with all-teams baseline), and confederation mix for Argentina matches.
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
RT = rf"{_ROOT}\data\referee-teams"
P = rf"{_ROOT}\data\processed"

mo = pd.concat([
    pd.read_csv(rf"{RT}\match_officials_1930_1986.csv", encoding="utf-8-sig"),
    pd.read_csv(rf"{RT}\match_officials_1990_2010.csv", encoding="utf-8-sig"),
    pd.read_csv(rf"{RT}\match_officials_2014_2026.csv", encoding="utf-8-sig"),
], ignore_index=True)
to = pd.concat([
    pd.read_csv(rf"{RT}\tournament_officials_1930_1986.csv", encoding="utf-8-sig"),
    pd.read_csv(rf"{RT}\tournament_officials_1990_2010.csv", encoding="utf-8-sig"),
    pd.read_csv(rf"{RT}\tournament_officials_2014_2026.csv", encoding="utf-8-sig"),
], ignore_index=True)

# ---------- 1) crew expansion ----------
growth = to.groupby("tournament_year").size().rename("appointed_officials").reset_index()
ROLE_COLS = ["referee", "assistant1", "assistant2", "fourth_official", "var", "avar1", "avar2", "avar3"]
crew = mo.groupby("tournament_year")[ROLE_COLS].apply(lambda g: g.notna().sum(axis=1).mean()).round(2)
growth["avg_match_crew"] = growth.tournament_year.map(crew)
growth.to_csv(rf"{P}\referee_crew_growth.csv", index=False)
print("=== Crew expansion ===")
print(growth.to_string(index=False))

# ---------- 2) repeat referees: all-teams baseline ----------
long = []
for _, r in mo.iterrows():
    for side in ["home_team", "away_team"]:
        long.append(dict(team=r[side], year=r.tournament_year, referee=r.referee, var=r.get("var")))
tm = pd.DataFrame(long)
rep = (tm.groupby(["team", "referee"])
       .agg(n=("year", "size"), years=("year", lambda s: sorted(set(s))))
       .reset_index().sort_values("n", ascending=False))
rep["n_tournaments"] = rep.years.apply(len)
top = rep[rep.n >= 3].copy()
top["years"] = top.years.apply(lambda y: "/".join(map(str, y)))
top.to_csv(rf"{P}\referee_repeat_leaderboard.csv", index=False)
print("\n=== Referee-team pairs with >=3 matches, 1990-2026 (all teams) ===")
print(top.head(14).to_string(index=False))

# VAR repeats (2018+)
vrep = (tm.dropna(subset=["var"]).groupby(["team", "var"])
        .agg(n=("year", "size"), years=("year", lambda s: sorted(set(s)))).reset_index()
        .sort_values("n", ascending=False))
print("\n=== VAR-official-team pairs with >=3 matches, 2018-2026 ===")
v3 = vrep[vrep.n >= 3].copy(); v3["years"] = v3.years.apply(lambda y: "/".join(map(str, y)))
print(v3.to_string(index=False) if len(v3) else "(none)")

# ---------- 3) Argentina officials, any role ----------
arg = mo[(mo.home_team == "Argentina") | (mo.away_team == "Argentina")].copy()
rows = []
for _, r in arg.iterrows():
    for role in ROLE_COLS:
        if pd.notna(r.get(role)):
            rows.append(dict(official=r[role], role=role, year=r.tournament_year, date=r.match_date))
ao = pd.DataFrame(rows)
aosum = (ao.groupby("official")
         .agg(matches=("date", "nunique"), roles=("role", lambda s: "/".join(sorted(set(s)))),
              years=("year", lambda s: "/".join(map(str, sorted(set(s))))))
         .reset_index().sort_values("matches", ascending=False))
aosum.to_csv(rf"{P}\argentina_officials.csv", index=False)
print("\n=== Officials most often in Argentina matches (any role, 1990-2026) ===")
print(aosum.head(12).to_string(index=False))

# ---------- 4) referee confederation mix for Argentina vs all ----------
conf = to.dropna(subset=["confederation"]).drop_duplicates("official_name").set_index("official_name").confederation
mo["ref_conf"] = mo.referee.map(conf)
arg["ref_conf"] = arg.referee.map(conf)
mix = pd.DataFrame({
    "argentina": arg.ref_conf.value_counts(normalize=True).round(3),
    "all_matches": mo.ref_conf.value_counts(normalize=True).round(3),
}).fillna(0)
mix.to_csv(rf"{P}\referee_confederation_mix.csv")
print("\n=== Referee confederation mix (share of matches) ===")
print(mix.to_string())
print(f"\nunmapped referee-confederation rows: {int(mo.ref_conf.isna().sum())} of {len(mo)}")
