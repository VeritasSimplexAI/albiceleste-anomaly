"""Integrate the compiled 2026 files into the era analysis (cards + fouls).

Exposure alignment: team_stats_2026.csv discipline numbers are frozen at FBref's
July 8 snapshot (= through the round of 16). qfsf_cards_2026.csv patches the
4 QFs + 2 SFs. Argentina's 7 matches come exactly from argentina_matches_cards_2026.csv.
Field rate convention matches build_stats.py: field = all team-match rows except
Argentina's own rows (opponents' rows in Argentina matches stay in the field).
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys
import pandas as pd
import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8")
D26 = rf"{_ROOT}\data\worldcup-2026"
P = rf"{_ROOT}\data\processed"

matches = pd.read_csv(rf"{D26}\matches_2026.csv", encoding="utf-8-sig")
squad = pd.read_csv(rf"{D26}\team_stats_2026.csv", encoding="utf-8-sig")
qfsf = pd.read_csv(rf"{D26}\qfsf_cards_2026.csv", encoding="utf-8-sig")
arg = pd.read_csv(rf"{D26}\argentina_matches_cards_2026.csv", encoding="utf-8-sig")

# snapshot exposure = matches in group/R32/R16 per team
pre_qf = matches[matches.stage.isin(["Group stage", "Round of 32", "Round of 16"])]
exp = pd.concat([pre_qf.home_team, pre_qf.away_team]).value_counts().rename("snap_matches")
team = squad.set_index("team").join(exp)
team["snap_matches"] = team.snap_matches.fillna(0).astype(int)

qf_add = qfsf.groupby("team").agg(qf_matches=("team", "count"), qf_yellows=("yellow_cards", "sum"),
                                  qf_reds=("red_cards", "sum"), qf_fouls=("fouls_committed", "sum"))
team = team.join(qf_add).fillna({"qf_matches": 0, "qf_yellows": 0, "qf_reds": 0, "qf_fouls": 0})
team["yellows_full"] = team.yellow_cards + team.qf_yellows
team["reds_full"] = team.red_cards + team.qf_reds
team["fouls_full"] = team.fouls_committed + team.qf_fouls
team["exposure"] = team.snap_matches + team.qf_matches

# sanity: Argentina per-match file vs patched totals
a_own = arg[arg.team == "Argentina"]
a_opp = arg[arg.team != "Argentina"]
assert len(a_own) == 7 and len(a_opp) == 7, "expected 7+7 Argentina match rows"
patched = team.loc["Argentina"]
if int(a_own.yellow_cards.sum()) != int(patched.yellows_full):
    print(f"WARNING: Argentina yellows mismatch: per-match {a_own.yellow_cards.sum()} vs patched {patched.yellows_full}")

fld = team.drop(index="Argentina")
f_y, f_r, f_f, f_m = fld.yellows_full.sum(), fld.reds_full.sum(), fld.fouls_full.sum(), fld.exposure.sum()

rows = []
def add(metric, c_a, m_a, c_f, m_f, favorable_if):
    p = stats.binomtest(int(c_a), int(c_a + c_f), m_a / (m_a + m_f)).pvalue if c_a + c_f > 0 else 1.0
    rows.append(dict(era="2026", metric=metric, favorable_if=favorable_if,
                     arg_count=int(c_a), arg_matches=int(m_a), arg_rate=round(c_a / m_a, 3),
                     field_rate=round(c_f / m_f, 3),
                     rate_ratio=round((c_a / m_a) / (c_f / m_f), 3) if c_f else np.nan,
                     p_value=round(p, 4)))

add("yellows_received", a_own.yellow_cards.sum(), 7, f_y, f_m, "low")
add("yellows_drawn", a_opp.yellow_cards.sum(), 7, f_y, f_m, "high")
add("dismissals_received", a_own.red_cards.sum(), 7, f_r, f_m, "low")
add("dismissals_drawn", a_opp.red_cards.sum(), 7, f_r, f_m, "high")
add("fouls_committed", a_own.fouls_committed.sum(), 7, f_f, f_m, "n/a")
add("fouls_drawn", a_opp.fouls_committed.sum(), 7, f_f, f_m, "n/a")

t26 = pd.DataFrame(rows)
t26.to_csv(rf"{P}\argentina_vs_field_2026.csv", index=False)
print("=== Argentina vs field, 2026 (cards/fouls; field = 47 other teams, exposure-aligned) ===")
print(t26.to_string(index=False))

# cards-per-foul leniency (2026): fouls per yellow, higher = more lenient refereeing
a_fpy = a_own.fouls_committed.sum() / max(a_own.yellow_cards.sum(), 1)
o_fpy = a_opp.fouls_committed.sum() / max(a_opp.yellow_cards.sum(), 1)
f_fpy = f_f / f_y
print(f"\nLeniency (fouls per yellow card): Argentina {a_fpy:.2f} | Argentina's opponents {o_fpy:.2f} | field {f_fpy:.2f}")

# penalties (awarded) in Argentina matches, from per-match file
print(f"\nPenalties awarded: Argentina {int(a_own.penalties_awarded.sum())} in 7 "
      f"(converted 1 - Lautaro vs Jordan); opponents {int(a_opp.penalties_awarded.sum())}")

# three-era Argentina summary table for the site
hist = pd.read_csv(rf"{P}\argentina_vs_field_tests.csv")
combined = pd.concat([hist, t26], ignore_index=True)
combined.to_csv(rf"{P}\argentina_vs_field_all_eras.csv", index=False)
print(f"\nSaved combined era tests -> argentina_vs_field_all_eras.csv ({len(combined)} rows)")
