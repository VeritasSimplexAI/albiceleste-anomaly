"""Argentina's record with each match official (any role), 1990-2026.
Win convention: shootout winners count as wins (matches the source dataset).
Also computes the card differential in those matches as officiating context.
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

mo = pd.concat([
    pd.read_csv(rf"{RT}\match_officials_1930_1986.csv", encoding="utf-8-sig"),
    pd.read_csv(rf"{RT}\match_officials_1990_2010.csv", encoding="utf-8-sig"),
    pd.read_csv(rf"{RT}\match_officials_2014_2026.csv", encoding="utf-8-sig"),
], ignore_index=True)
arg_mo = mo[(mo.home_team == "Argentina") | (mo.away_team == "Argentina")].copy()
arg_mo["opponent"] = np.where(arg_mo.home_team == "Argentina", arg_mo.away_team, arg_mo.home_team)

# --- Argentina results + cards per match, 1990-2022 (academic data) ---
ml = pd.read_csv(rf"{P}\match_team_level.csv")
am = ml[(ml.team_name == "Argentina")][
    ["match_date", "opponent_name", "win", "draw", "lose", "goals_for", "goals_against", "yellows", "opp_yellows"]]
am = am.rename(columns={"opponent_name": "opponent"})

# --- 2026: results from matches file, cards from the per-match compilation ---
m26 = pd.read_csv(rf"{ROOT}\data\worldcup-2026\matches_2026.csv", encoding="utf-8-sig")
a26 = m26[(m26.home_team == "Argentina") | (m26.away_team == "Argentina")].copy()
a26["opponent"] = np.where(a26.home_team == "Argentina", a26.away_team, a26.home_team)
a26["gf"] = np.where(a26.home_team == "Argentina", a26.home_score, a26.away_score)
a26["ga"] = np.where(a26.home_team == "Argentina", a26.away_score, a26.home_score)
c26 = pd.read_csv(rf"{ROOT}\data\worldcup-2026\argentina_matches_cards_2026.csv", encoding="utf-8-sig")
own = c26[c26.team == "Argentina"].set_index("match_date").yellow_cards
opp = c26[c26.team != "Argentina"].set_index("match_date").yellow_cards
rows26 = [dict(match_date=r.match_date, opponent=r.opponent,
               win=int(r.gf > r.ga), draw=int(r.gf == r.ga), lose=int(r.gf < r.ga),
               goals_for=r.gf, goals_against=r.ga,
               yellows=int(own.get(r.match_date, 0)), opp_yellows=int(opp.get(r.match_date, 0)))
          for r in a26.itertuples()]
res = pd.concat([am, pd.DataFrame(rows26)], ignore_index=True)

# --- join officials to results on match_date (unique per Argentina match) ---
res.match_date = pd.to_datetime(res.match_date).dt.date.astype(str)
arg_mo.match_date = pd.to_datetime(arg_mo.match_date).dt.date.astype(str)
merged = arg_mo.merge(res, on="match_date", how="left", suffixes=("", "_r"))
missing = merged[merged.win.isna()]
if len(missing):
    print("WARNING: unmatched officials rows:", missing[["match_date", "home_team", "away_team"]].to_string())

long = []
for r in merged.itertuples():
    for role in ROLE_COLS:
        name = getattr(r, role)
        if pd.notna(name):
            long.append(dict(official=name, role=role, year=r.tournament_year,
                             match_date=r.match_date, opponent=r.opponent,
                             win=r.win, draw=r.draw, lose=r.lose,
                             card_net=r.opp_yellows - r.yellows))
lg = pd.DataFrame(long)
rec = (lg.groupby("official")
       .agg(matches=("match_date", "nunique"), wins=("win", "sum"), draws=("draw", "sum"),
            losses=("lose", "sum"), card_net=("card_net", "sum"),
            roles=("role", lambda s: "/".join(sorted(set(s)))),
            years=("year", lambda s: "/".join(map(str, sorted(set(s))))),
            ref_matches=("role", lambda s: int((s == "referee").sum())))
       .reset_index())
rec["win_pct"] = (100 * rec.wins / rec.matches).round(0).astype(int)
rec["card_net_pm"] = (rec.card_net / rec.matches).round(2)
rec = rec.sort_values(["matches", "win_pct"], ascending=False)
rec.to_csv(rf"{P}\argentina_official_records.csv", index=False)

base = res[["win", "draw", "lose"]].sum()
print(f"Baseline: Argentina {int(base.win)}W {int(base.draw)}D {int(base.lose)}L in {len(res)} matches "
      f"1990-2026 ({100*base.win/len(res):.0f}% wins, shootout wins included)")
print(f"\nOfficials with >=3 Argentina matches: {len(rec[rec.matches>=3])}")
print(rec[rec.matches >= 3].head(16).to_string(index=False))
print("\nSpotlight:")
for name in ["Ismail Elfath", "Szymon Marciniak", "Tomasz Kwiatkowski"]:
    r = rec[rec.official == name]
    if len(r): print(r.to_string(index=False, header=(name == "Ismail Elfath")))
