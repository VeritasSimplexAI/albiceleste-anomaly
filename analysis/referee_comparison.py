"""Argentina vs each official, with baselines:
  - argentina win% with the official (any-role scope AND referee-only scope)
  - other teams' average win% in that official's matches (Argentina matches excluded)
  - opponent-adjusted expected win% (leave-one-out Argentina record vs each opponent)
Output: processed/argentina_official_comparison.csv with a `scope` column
("crew" = any role, "referee" = main referee only).
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
ROLE_COLS = ["referee", "assistant1", "assistant2", "fourth_official", "var", "avar1", "avar2", "avar3"]

ALIAS = {"Ireland": "Republic of Ireland", "USA": "United States", "Korea Republic": "South Korea",
         "IR Iran": "Iran", "Türkiye": "Turkey", "Czechia": "Czech Republic", "China PR": "China",
         "Côte d'Ivoire": "Ivory Coast", "FR Yugoslavia": "Yugoslavia", "Curacao": "Curaçao"}
def norm(s): return ALIAS.get(str(s).strip(), str(s).strip())
def key(date, a, b): return f"{date}|" + "|".join(sorted([norm(a), norm(b)]))

# ---------- all team-match results 1990-2026 ----------
ml = pd.read_csv(rf"{P}\match_team_level.csv")
ml = ml[ml.year >= 1930]
res = ml[["match_date", "team_name", "opponent_name", "win", "draw", "lose"]].copy()
res.columns = ["date", "team", "opponent", "win", "draw", "lose"]

m26 = pd.read_csv(rf"{ROOT}\data\worldcup-2026\matches_2026.csv", encoding="utf-8-sig")
rows = []
for r in m26.itertuples():
    hs, as_ = r.home_score, r.away_score
    if r.penalty_shootout == "yes" and isinstance(r.score_penalties, str) and "-" in r.score_penalties:
        ph, pa = map(int, r.score_penalties.split("-"))
        hw, aw = int(ph > pa), int(pa > ph)
        rows += [dict(date=r.match_date, team=r.home_team, opponent=r.away_team, win=hw, draw=0, lose=aw),
                 dict(date=r.match_date, team=r.away_team, opponent=r.home_team, win=aw, draw=0, lose=hw)]
    else:
        rows += [dict(date=r.match_date, team=r.home_team, opponent=r.away_team,
                      win=int(hs > as_), draw=int(hs == as_), lose=int(hs < as_)),
                 dict(date=r.match_date, team=r.away_team, opponent=r.home_team,
                      win=int(as_ > hs), draw=int(hs == as_), lose=int(as_ < hs))]
res = pd.concat([res, pd.DataFrame(rows)], ignore_index=True)
res["date"] = pd.to_datetime(res.date).dt.date.astype(str)
res["team"] = res.team.map(norm); res["opponent"] = res.opponent.map(norm)
res["mkey"] = [key(d, a, b) for d, a, b in zip(res.date, res.team, res.opponent)]

# ---------- officials, long format ----------
mo = pd.concat([
    pd.read_csv(rf"{RT}\match_officials_1930_1986.csv", encoding="utf-8-sig"),
    pd.read_csv(rf"{RT}\match_officials_1990_2010.csv", encoding="utf-8-sig"),
    pd.read_csv(rf"{RT}\match_officials_2014_2026.csv", encoding="utf-8-sig"),
], ignore_index=True)
mo["date"] = pd.to_datetime(mo.match_date).dt.date.astype(str)
mo["mkey"] = [key(d, a, b) for d, a, b in zip(mo.date, mo.home_team, mo.away_team)]
unmatched = set(mo.mkey) - set(res.mkey)
print(f"officials matches joined: {len(set(mo.mkey) & set(res.mkey))}/{mo.mkey.nunique()}; unmatched: {len(unmatched)}")
for u in sorted(unmatched)[:12]: print("  UNMATCHED:", u)

off_long = []
for r in mo.itertuples():
    for role in ROLE_COLS:
        name = getattr(r, role)
        if pd.notna(name):
            off_long.append(dict(mkey=r.mkey, official=name, role=role, year=r.tournament_year))
ol = pd.DataFrame(off_long)

# per team-match rows with official attached
tm = res.merge(ol, on="mkey")  # two team rows per match per official-role

# ---------- Argentina leave-one-out expected win% vs each opponent ----------
ares = res[res.team == "Argentina"].copy()
opp_tot = ares.groupby("opponent").agg(n=("win", "size"), w=("win", "sum"))
BASE = ares.win.mean()
def expected_loo(row):
    t = opp_tot.loc[row.opponent]
    if t.n <= 1: return BASE
    return (t.w - row.win) / (t.n - 1)
ares["exp_win"] = ares.apply(expected_loo, axis=1)

# ---------- build comparison per scope ----------
def build(scope):
    sub = tm if scope == "crew" else tm[tm.role == "referee"]
    a = sub[sub.team == "Argentina"].drop_duplicates(["mkey", "official"])
    a = a.merge(ares[["mkey", "exp_win"]], on="mkey")
    others = sub[(sub.team != "Argentina") & (sub.opponent != "Argentina")].drop_duplicates(["mkey", "official", "team"])
    ostat = others.groupby("official").agg(others_matches=("win", "size"), others_win=("win", "mean"))
    g = (a.groupby("official")
         .agg(matches=("mkey", "nunique"), wins=("win", "sum"), draws=("draw", "sum"),
              losses=("lose", "sum"), exp_win=("exp_win", "mean"),
              roles=("role", lambda s: "/".join(sorted(set(s)))),
              years=("year", lambda s: "/".join(map(str, sorted(set(s))))))
         .reset_index().join(ostat, on="official"))
    g["win_pct"] = (100 * g.wins / g.matches).round(0)
    g["others_win_pct"] = (100 * g.others_win).round(0)
    g["expected_win_pct"] = (100 * g.exp_win).round(0)
    g["delta_vs_expected"] = (g.win_pct - g.expected_win_pct).round(0)
    g["scope"] = scope
    return g.drop(columns=["others_win", "exp_win"])

out = pd.concat([build("crew"), build("referee")], ignore_index=True)
out["others_matches"] = out.others_matches.fillna(0).astype(int)
out["others_win_pct"] = out.others_win_pct.fillna(-1).astype(int)  # -1 -> "n/a" client-side
out.to_csv(rf"{P}\argentina_official_comparison.csv", index=False)

print(f"\nArgentina baseline win%: {100*BASE:.0f}%")
ref = out[(out.scope == "referee") & (out.matches >= 2)].sort_values(["matches", "win_pct"], ascending=False)
print("\n=== Referee-only scope, >=2 Argentina matches ===")
print(ref[["official", "matches", "wins", "draws", "losses", "win_pct", "expected_win_pct",
           "delta_vs_expected", "others_matches", "others_win_pct", "years"]].to_string(index=False))
