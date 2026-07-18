"""Who referees the CONMEBOL nations? Referee-confederation mix per South
American team (all-time and 1990+), vs the field baseline — tests whether
Argentina's UEFA tilt is unusual among its own confederation's peers.
Also: appointed officials per tournament split by confederation (crew growth).
Outputs -> processed/conmebol_ref_mix.csv, processed/crew_by_conf.csv
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
ROOT = rf"{_ROOT}"
P = rf"{ROOT}\data\processed"
RT = rf"{ROOT}\data\referee-teams"

mo = pd.concat([pd.read_csv(rf"{RT}\match_officials_{s}.csv", encoding="utf-8-sig")
                for s in ["1930_1986", "1990_2010", "2014_2026"]], ignore_index=True)
to = pd.concat([pd.read_csv(rf"{RT}\tournament_officials_{s}.csv", encoding="utf-8-sig")
                for s in ["1930_1986", "1990_2010", "2014_2026"]], ignore_index=True)

conf = to.dropna(subset=["confederation"]).drop_duplicates("official_name").set_index("official_name").confederation
mo["ref_conf"] = mo.referee.map(conf)

CONMEBOL = ["Argentina", "Brazil", "Uruguay", "Chile", "Colombia", "Paraguay", "Peru", "Ecuador"]
CONFS = ["UEFA", "CONMEBOL", "CONCACAF", "AFC", "CAF", "OFC"]

rows = []
for era, lo in [("all-time", 1930), ("since 1990", 1990)]:
    sub = mo[mo.tournament_year >= lo]
    base = sub.ref_conf.value_counts(normalize=True)
    for t in CONMEBOL:
        g = sub[(sub.home_team == t) | (sub.away_team == t)]
        if len(g) < 8: continue
        shares = g.ref_conf.value_counts(normalize=True)
        rows.append(dict(era=era, team=t, matches=len(g),
                         **{c.lower(): round(float(shares.get(c, 0)) * 100, 1) for c in CONFS}))
    rows.append(dict(era=era, team="— field (all matches)", matches=len(sub),
                     **{c.lower(): round(float(base.get(c, 0)) * 100, 1) for c in CONFS}))
mix = pd.DataFrame(rows)
mix.to_csv(rf"{P}\conmebol_ref_mix.csv", index=False)
print("=== Referee confederation shares (%) for CONMEBOL teams ===")
print(mix.to_string(index=False))

# crew growth stacked by confederation of APPOINTED officials
cg = (to.dropna(subset=["confederation"])
      .groupby(["tournament_year", "confederation"]).size().rename("n").reset_index())
cg.to_csv(rf"{P}\crew_by_conf.csv", index=False)
print("\ncrew_by_conf.csv written:", len(cg), "rows")
uefa_share = cg[cg.confederation == "UEFA"].set_index("tournament_year").n / cg.groupby("tournament_year").n.sum()
print("UEFA share of appointed officials, first/last:",
      round(float(uefa_share.iloc[0]) * 100), "% (1930) ->", round(float(uefa_share.iloc[-1]) * 100), "% (2026)")
