"""Three inline analyses:
1. Robustness stress-tests of the core post-2022 penalty/card findings.
2. Decision-impact quantification (goals-equivalent) per post-2022 match.
   Conventions (stated on site): penalty awarded = 0.78 expected goals;
   goal disallowed = 1.00; opponent red card ~= 0.50.
3. Argentina aggregates by FIFA-president era.
Outputs -> data/processed/{robustness_tests,decision_impact,president_eras}.csv
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys
import pandas as pd
import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8")
ROOT = rf"{_ROOT}"
P = rf"{ROOT}\data\processed"

sq = pd.read_csv(rf"{P}\squad_discipline_clean.csv")
var = pd.read_csv(rf"{ROOT}\data\officiating-extra\var_incidents.csv", encoding="utf-8-sig")


def ptest(c_a, m_a, c_f, m_f):
    return stats.binomtest(int(c_a), int(c_a + c_f), m_a / (m_a + m_f)).pvalue if c_a + c_f else 1.0


# ---------- 1) robustness ----------
s = sq[sq.tournament_year.isin([2022, 2026])]
a = s[s.team == "Argentina"]
f = s[s.team != "Argentina"]
A_P, A_M = int(a.penalty_kicks_attempted.sum()), 14
F_P, F_M = int(f.penalty_kicks_attempted.sum()), int(f.matches_played.sum())
rows = []
def add(name, c_a, m_a, c_f, m_f, note):
    rows.append(dict(test=name, argentina=f"{c_a} in {m_a}", rate=round(c_a / m_a, 3),
                     field_rate=round(c_f / m_f, 3), ratio=round((c_a / m_a) / (c_f / m_f), 2),
                     p=round(ptest(c_a, m_a, c_f, m_f), 5), note=note))

add("Baseline: pens awarded, 2022+2026", A_P, A_M, F_P, F_M, "the headline result")
# VAR-awarded pens both sides (from incident compilation)
vp = var[(var.decision_type == "penalty_awarded") & (var.tournament_year.isin([2022, 2026]))]
a_var = int((vp.beneficiary_team == "Argentina").sum())
f_var = int((vp.beneficiary_team != "Argentina").sum())
add("Excluding VAR-awarded penalties", A_P - a_var, A_M, F_P - f_var, F_M,
    f"removes {a_var} ARG / {f_var} field VAR-review awards — on-field decisions only")
# excluding the 2022 final (ARG 1 for; France 2 for in that match)
add("Excluding the 2022 final", A_P - 1, A_M - 1, F_P - 2, F_M - 1,
    "drops the most scrutinized match entirely")
add("2022 alone", 5, 7, int(sq[(sq.tournament_year == 2022) & (sq.team != 'Argentina')].penalty_kicks_attempted.sum()), int(sq[(sq.tournament_year == 2022) & (sq.team != 'Argentina')].matches_played.sum()), "single-tournament")
add("2026 alone (through SF)", 3, 7, int(sq[(sq.tournament_year == 2026) & (sq.team != 'Argentina')].penalty_kicks_attempted.sum()), int(sq[(sq.tournament_year == 2026) & (sq.team != 'Argentina')].matches_played.sum()), "single-tournament")
# cards anomaly minus Lahoz (field = 2022 yellows to all non-ARG teams / their matches)
tt22 = pd.read_csv(rf"{P}\team_tournament_stats.csv").query("year==2022")
fy = int(tt22[tt22.team_name != "Argentina"].yellows_received.sum())
fm = int(tt22[tt22.team_name != "Argentina"].matches.sum())
add("2022 opponents' yellows minus the Lahoz QF", 26 - 8, 6, fy, fm,
    "removes the record-card Netherlands match entirely")
# symmetric check
add("Pens awarded AGAINST Argentina 2022+2026", 2, 14, F_P, F_M,
    "the mirror stat — below field rate")
rob = pd.DataFrame(rows)
rob.to_csv(rf"{P}\robustness_tests.csv", index=False)
print(rob.to_string(index=False))

# ---------- 2) decision impact ----------
va = var[(var.beneficiary_team == "Argentina") | (var.against_team == "Argentina")].copy()
va["md"] = pd.to_datetime(va.match_date)
mlv = pd.read_csv(rf"{P}\match_team_level.csv")
a22 = mlv[(mlv.team_name == "Argentina") & (mlv.year == 2022)]
c26 = pd.read_csv(rf"{ROOT}\data\worldcup-2026\argentina_matches_cards_2026.csv", encoding="utf-8-sig")
m26 = pd.read_csv(rf"{ROOT}\data\worldcup-2026\matches_2026.csv", encoding="utf-8-sig")

PEN, GOAL, RED = 0.78, 1.00, 0.50
imp = []
def var_counts(date, opp):
    g = va[(abs(va.md - pd.to_datetime(date)).dt.days <= 1) & ((va.home_team == opp) | (va.away_team == opp))]
    gd_for = int(((g.decision_type == "goal_disallowed") & (g.beneficiary_team == "Argentina")).sum())
    gd_ag = int(((g.decision_type == "goal_disallowed") & (g.against_team == "Argentina")).sum())
    return gd_for, gd_ag

for r in a22.itertuples():
    d = pd.to_datetime(r.match_date).date().isoformat()
    pens_for = int(r.pen_goals) + (1 if r.opponent_name == "Poland" else 0)  # + the missed VAR award
    gd_for, gd_ag = var_counts(d, r.opponent_name)
    swing = PEN * (pens_for - int(r.opp_pen_goals)) + GOAL * (gd_for - gd_ag) + RED * int(r.opp_dismissals)
    margin = int(r.goals_for) - int(r.goals_against)
    imp.append(dict(year=2022, date=d, opponent=r.opponent_name, score=f"{int(r.goals_for)}–{int(r.goals_against)}",
                    net_swing=round(swing, 2), margin=margin,
                    decisive="yes" if swing >= abs(margin) and margin >= 0 else ""))
for r in c26[c26.team == "Argentina"].itertuples():
    d = pd.to_datetime(r.match_date).date().isoformat()
    opp_row = c26[(c26.match_date == r.match_date) & (c26.team != "Argentina")].iloc[0]
    mrow = m26[(m26.match_date == r.match_date) & ((m26.home_team == "Argentina") | (m26.away_team == "Argentina"))].iloc[0]
    gf, ga = (mrow.home_score, mrow.away_score) if mrow.home_team == "Argentina" else (mrow.away_score, mrow.home_score)
    gd_for, gd_ag = var_counts(d, opp_row.team)
    swing = PEN * (int(r.penalties_awarded) - int(opp_row.penalties_awarded)) + GOAL * (gd_for - gd_ag) + RED * int(opp_row.red_cards)
    imp.append(dict(year=2026, date=d, opponent=opp_row.team, score=f"{gf}–{ga}",
                    net_swing=round(swing, 2), margin=int(gf - ga),
                    decisive="yes" if swing >= abs(gf - ga) and gf - ga >= 0 else ""))
impact = pd.DataFrame(imp).sort_values("date")
impact.to_csv(rf"{P}\decision_impact.csv", index=False)
print("\nDecision impact (goals-equivalent):")
print(impact.to_string(index=False))
print(f"Totals: 2022 {impact[impact.year==2022].net_swing.sum():+.2f} | 2026 {impact[impact.year==2026].net_swing.sum():+.2f} goals-equivalent")

# ---------- 3) FIFA-president eras ----------
ERAS = [("Rimet & successors", 1930, 1958), ("Rous", 1962, 1974),
        ("Havelange", 1978, 1998), ("Blatter", 2002, 2014), ("Infantino", 2018, 2026)]
tt = pd.read_csv(rf"{P}\team_tournament_stats.csv")
at = tt[tt.team_name == "Argentina"]
# per-tournament awarded for/against (verified: archival per-incident 1930-2010, FBref 2014+)
awarded = {1930: (1, 2), 1958: (2, 0), 1962: (0, 1), 1966: (0, 0), 1974: (0, 0), 1978: (1, 1), 1982: (1, 0), 1986: (0, 1),
           1990: (0, 1), 1994: (2, 0), 1998: (2, 1), 2002: (1, 1), 2006: (0, 0), 2010: (0, 0),
           2014: (0, None), 2018: (1, 2), 2022: (5, 2), 2026: (3, 0), 1934: (0, 0)}
RECORD_LBL = {1978: "champion", 1986: "champion", 2022: "champion", 1930: "final", 1990: "final", 2014: "final", 2026: "final*"}
prez = []
for name, y0, y1 in ERAS:
    g = at[(at.year >= y0) & (at.year <= y1)]
    m = int(g.matches.sum()) + (7 if name == "Infantino" else 0)
    w = int(g.wins.sum()) + (7 if name == "Infantino" else 0)
    dr = int(g.draws.sum()); lo = int(g.losses.sum())
    pf = sum(awarded.get(y, (0, 0))[0] for y in g.year) + (3 if name == "Infantino" else 0)
    pa = sum((awarded.get(y, (0, 0))[1] or 0) for y in g.year) + (0 if name == "Infantino" else 0)
    finals = ", ".join(f"{y} {RECORD_LBL[y]}" for y in sorted(set(list(g.year) + ([2026] if name == "Infantino" else []))) if y in RECORD_LBL) or "—"
    prez.append(dict(era=name, span=f"{y0}–{y1}", tournaments=len(g) + (1 if name == "Infantino" else 0),
                     matches=m, record=f"{w}–{dr}–{lo}", win_pct=round(100 * w / m, 0),
                     pens_for=pf, pens_against=pa,
                     pens_net_pm=round((pf - pa) / m, 3), honors=finals))
pz = pd.DataFrame(prez)
pz.to_csv(rf"{P}\president_eras.csv", index=False)
print("\nFIFA-president eras:")
print(pz.to_string(index=False))
