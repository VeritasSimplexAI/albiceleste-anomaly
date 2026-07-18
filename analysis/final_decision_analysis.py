"""FINAL decision-metric analysis: penalties AWARDED, VAR overturns, and
foul/card leniency — Argentina vs field across three eras.

Decision metrics only (referee choices), execution excluded.
Era 1990-2018 penalties: 1990-2010 per-incident compilation + FBref PKatt/PKcon
2014-2018. Known gap: 2014 awarded-against per team unpublished by FBref;
Argentina's 2014 converted-against is 0, missed-against unverified (flagged).
VAR: directional incidents only (27 ambiguous 2026 rows excluded, flagged).
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys, os
import pandas as pd
import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8")
P = rf"{_ROOT}\data\processed"
OE = rf"{_ROOT}\data\officiating-extra"

sq = pd.read_csv(rf"{OE}\squad_discipline.csv", encoding="utf-8-sig")
var = pd.read_csv(rf"{OE}\var_incidents.csv", encoding="utf-8-sig")
hist = pd.read_csv(rf"{P}\pens_awarded_team_1990_2010.csv")


def ptest(c_a, m_a, c_f, m_f):
    if c_a + c_f == 0:
        return 1.0
    return stats.binomtest(int(c_a), int(c_a + c_f), m_a / (m_a + m_f)).pvalue


print("=" * 70)
print("1) PENALTIES AWARDED — Argentina vs field, per era")
print("=" * 70)
h = hist.groupby("team_name")[["matches", "pens_awarded_for", "pens_awarded_against"]].sum()
rows = []

# 1930-1986 era from the archival per-incident file (complete as of 2026-07-16)
old_fp = rf"{_ROOT}\data\penalties-historical\penalties_awarded_1930_1986.csv"
if os.path.exists(old_fp):
    old = pd.read_csv(old_fp, encoding="utf-8-sig")
    tt = pd.read_csv(rf"{P}\team_tournament_stats.csv")
    tt_old = tt[tt.year <= 1986]
    m_arg = int(tt_old[tt_old.team_name == "Argentina"].matches.sum())
    m_fld = int(tt_old[tt_old.team_name != "Argentina"].matches.sum())
else:
    old = None

def era_pen(era, a_for, a_against, m_a, f_for, f_against, m_f, note=""):
    for met, c_a, c_f, fav in [("awarded_for", a_for, f_for, "high"),
                               ("awarded_against", a_against, f_against, "low")]:
        p = ptest(c_a, m_a, c_f, m_f)
        rows.append(dict(era=era, metric=met, arg=c_a, arg_matches=m_a,
                         arg_rate=round(c_a / m_a, 3), field_rate=round(c_f / m_f, 3),
                         ratio=round((c_a / m_a) / (c_f / m_f), 2), p=round(p, 4), note=note))

if old is not None:
    era_pen("1930-1986",
            int((old.team_awarded == "Argentina").sum()), int((old.opponent == "Argentina").sum()), m_arg,
            int((old.team_awarded != "Argentina").sum()), int((old.opponent != "Argentina").sum()), m_fld,
            note="archival per-incident compilation; missed-penalty records pre-1974 graded B/C")

# 1990-2018
a9010 = h.loc["Argentina"]
f9010 = h.drop(index="Argentina").sum()
s1418 = sq[sq.tournament_year.isin([2014, 2018])]
a1418 = s1418[s1418.team == "Argentina"]
f1418 = s1418[s1418.team != "Argentina"]
era_pen("1990-2018",
        int(a9010.pens_awarded_for + a1418.penalty_kicks_attempted.sum()),
        int(a9010.pens_awarded_against + a1418.penalties_conceded.fillna(0).sum()),
        int(a9010.matches + a1418.matches_played.sum()),
        int(f9010.pens_awarded_for + f1418.penalty_kicks_attempted.sum()),
        int(f9010.pens_awarded_against + f1418.penalty_kicks_attempted.sum()),  # symmetry: every pen is against someone
        int(f9010.matches + f1418.matches_played.sum()),
        note="2014 ARG awarded-against uses 0 (converted-against=0; missed-against unverified)")

for yr in [2022, 2026]:
    s = sq[sq.tournament_year == yr]
    a, f = s[s.team == "Argentina"], s[s.team != "Argentina"]
    a_con = a.penalties_conceded.fillna(0).sum() if yr == 2022 else 0  # 2026: exact 0 from per-match file
    era_pen(str(yr), int(a.penalty_kicks_attempted.sum()), int(a_con), int(a.matches_played.sum()),
            int(f.penalty_kicks_attempted.sum()), int(f.penalty_kicks_attempted.sum()),
            int(f.matches_played.sum()),
            note="" if yr == 2022 else "ARG against=0 verified per-match; field from PKatt symmetry")

pens_tbl = pd.DataFrame(rows)
pens_tbl.to_csv(rf"{P}\pens_awarded_tests_all_eras.csv", index=False)
print(pens_tbl.to_string(index=False))

print()
print("=" * 70)
print("2) VAR OVERTURNS 2018-2026 (directional incidents only)")
print("=" * 70)
vd = var.dropna(subset=["beneficiary_team"]).copy()
print(f"Directional incidents: {len(vd)} of {len(var)} (excluded {len(var)-len(vd)} ambiguous 2026 rows)")
mp = sq.groupby(["tournament_year", "team"]).matches_played.sum()

var_rows = []
for yr in [2018, 2022, 2026]:
    vy = vd[vd.tournament_year == yr]
    fav = vy.beneficiary_team.value_counts()
    ag = vy.against_team.value_counts()
    my = mp.loc[yr]
    a_fav, a_ag, a_m = int(fav.get("Argentina", 0)), int(ag.get("Argentina", 0)), int(my.get("Argentina", 0))
    tot = len(vy)
    f_m = int(my.sum()) - a_m
    p_fav = ptest(a_fav, a_m, tot - a_fav, f_m)
    var_rows.append(dict(year=yr, arg_favorable=a_fav, arg_against=a_ag, arg_net=a_fav - a_ag,
                         arg_matches=a_m, arg_fav_rate=round(a_fav / a_m, 3) if a_m else 0,
                         field_fav_rate=round((tot - a_fav) / f_m, 3), p_favorable=round(p_fav, 4)))
var_tbl = pd.DataFrame(var_rows)
var_tbl.to_csv(rf"{P}\var_argentina_tests.csv", index=False)
print(var_tbl.to_string(index=False))

# pooled 2018-2026
A_fav = var_tbl.arg_favorable.sum(); A_m = var_tbl.arg_matches.sum()
T = len(vd); F_m = int(mp.loc[[2018, 2022, 2026]].sum()) - A_m
print(f"\nPooled: Argentina {A_fav} favorable / {var_tbl.arg_against.sum()} against in {A_m} matches "
      f"({A_fav/A_m:.2f}/match) vs field {(T-A_fav)/F_m:.2f}/match | p={ptest(A_fav, A_m, T-A_fav, F_m):.4f}")

# net-VAR leaderboard (all teams, pooled, >=7 matches in VAR-era tournaments only)
mp_var = mp.loc[[2018, 2022, 2026]].groupby("team").sum()
net = (vd.beneficiary_team.value_counts().rename("fav").to_frame()
       .join(vd.against_team.value_counts().rename("ag"), how="outer").fillna(0))
net["m"] = net.index.map(mp_var)
net = net.dropna(subset=["m"])
net["net_pm"] = (net.fav - net.ag) / net.m
lb = net[net.m >= 7].nlargest(8, "net_pm")
print("\nNet VAR benefit per match, teams with >=7 matches 2018-2026:")
print(lb.to_string(float_format=lambda x: f"{x:+.3f}"))
net.to_csv(rf"{P}\var_net_leaderboard.csv")

print()
print("=" * 70)
print("4) UNIQUENESS + POOLED POST-2022 PENALTY TEST")
print("=" * 70)
# pooled 2022+2026 awarded-for
s22, s26 = sq[sq.tournament_year == 2022], sq[sq.tournament_year == 2026]
a_c = int(s22[s22.team == "Argentina"].penalty_kicks_attempted.sum() +
          s26[s26.team == "Argentina"].penalty_kicks_attempted.sum())
f_c = int(s22[s22.team != "Argentina"].penalty_kicks_attempted.sum() +
          s26[s26.team != "Argentina"].penalty_kicks_attempted.sum())
f_m = int(s22[s22.team != "Argentina"].matches_played.sum() +
          s26[s26.team != "Argentina"].matches_played.sum())
print(f"Post-apex pooled (2022+2026): Argentina {a_c} awarded in 14 ({a_c/14:.2f}/match) "
      f"vs field {f_c}/{f_m} ({f_c/f_m:.2f}/match) | ratio {(a_c/14)/(f_c/f_m):.1f} "
      f"| p={ptest(a_c, 14, f_c, f_m):.5f}")
for yr in [2018, 2022, 2026]:
    s = sq[sq.tournament_year == yr]
    top = s.nlargest(4, "penalty_kicks_attempted")[["team", "matches_played", "penalty_kicks_attempted"]]
    print(f"{yr} most penalties awarded: " + ", ".join(
        f"{r.team} {int(r.penalty_kicks_attempted)} in {int(r.matches_played)}" for r in top.itertuples()))

print()
print("=" * 70)
print("3) LENIENCY — fouls committed per yellow card received (higher = more lenient)")
print("=" * 70)
for yr in [2018, 2022, 2026]:
    s = sq[(sq.tournament_year == yr) & sq.fouls_committed.notna() & (sq.yellow_cards > 0)].copy()
    s["fpy"] = s.fouls_committed / s.yellow_cards
    s["rank"] = s.fpy.rank(ascending=False, method="min").astype(int)
    a = s[s.team == "Argentina"]
    if a.empty: continue
    print(f"{yr}: Argentina {a.fpy.iloc[0]:.2f} fouls/yellow (rank {int(a['rank'].iloc[0])}/{len(s)} "
          f"most lenient) | field median {s.fpy.median():.2f}")
sq.to_csv(rf"{P}\squad_discipline_clean.csv", index=False)
