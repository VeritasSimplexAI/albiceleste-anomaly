"""Build per-team officiating stats from the fjelstul World Cup dataset (men's, 1990+).

Outputs:
  data/processed/team_tournament_stats.csv  - one row per team per tournament
  data/processed/team_era_stats.csv         - one row per team per era (pre: 1990-2018, apex: 2022)
  data/processed/argentina_vs_field_tests.csv - exact Poisson rate-ratio tests per era/metric

Definitions:
  yellows      = yellow cards shown (first + second yellows)
  dismissals   = sendings off (straight red or second yellow)
  pen_goals    = in-game penalty goals (NOTE: converted penalties only; missed
                 penalty awards are not recorded in this dataset - documented caveat)
  *_received   = shown to the team;  *_drawn = shown to the team's opponents
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys
import pandas as pd
import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8")

RAW = rf"{_ROOT}\data\worldcup-1930-2022"
OUT = rf"{_ROOT}\data\processed"
import os
os.makedirs(OUT, exist_ok=True)


def load(name):
    df = pd.read_csv(rf"{RAW}\{name}.csv", encoding="utf-8")
    df = df[df.tournament_name.str.contains("Men's")]
    df["year"] = df.tournament_id.str[-4:].astype(int)
    return df  # full history 1930-2022; cards only exist from 1970 (era-binned below)


ta = load("team_appearances")
bookings = load("bookings")
goals = load("goals")

# --- per match+team event counts ---
bk = bookings.groupby(["match_id", "team_name"]).agg(
    yellows=("yellow_card", "sum"),
    second_yellows=("second_yellow_card", "sum"),
    dismissals=("sending_off", "sum"),
).reset_index()
bk["yellows"] = bk.yellows + bk.second_yellows

pg = (goals[goals.penalty == 1]
      .groupby(["match_id", "team_name"]).size()
      .rename("pen_goals").reset_index())

m = ta.merge(bk[["match_id", "team_name", "yellows", "dismissals"]],
             on=["match_id", "team_name"], how="left")
m = m.merge(pg, on=["match_id", "team_name"], how="left")
# opponent's events in the same match = what this team "drew"
opp = m[["match_id", "team_name", "yellows", "dismissals", "pen_goals"]].rename(
    columns={"team_name": "opponent_name", "yellows": "opp_yellows",
             "dismissals": "opp_dismissals", "pen_goals": "opp_pen_goals"})
m = m.merge(opp, on=["match_id", "opponent_name"], how="left")
for c in ["yellows", "dismissals", "pen_goals", "opp_yellows", "opp_dismissals", "opp_pen_goals"]:
    m[c] = m[c].fillna(0).astype(int)

m.to_csv(rf"{OUT}\match_team_level.csv", index=False)

AGG = dict(
    matches=("match_id", "count"), wins=("win", "sum"), draws=("draw", "sum"),
    losses=("lose", "sum"), goals_for=("goals_for", "sum"), goals_against=("goals_against", "sum"),
    yellows_received=("yellows", "sum"), dismissals_received=("dismissals", "sum"),
    pen_goals_for=("pen_goals", "sum"), yellows_drawn=("opp_yellows", "sum"),
    dismissals_drawn=("opp_dismissals", "sum"), pen_goals_against=("opp_pen_goals", "sum"),
)

per_tourn = m.groupby(["year", "team_name"]).agg(**AGG).reset_index()
per_tourn.to_csv(rf"{OUT}\team_tournament_stats.csv", index=False)

m["era"] = np.select([m.year <= 1966, m.year <= 1986, m.year <= 2018],
                     ["1930-1966", "1970-1986", "1990-2018"], default="2022")
per_era = m.groupby(["era", "team_name"]).agg(**AGG).reset_index()
per_era.to_csv(rf"{OUT}\team_era_stats.csv", index=False)

# --- Argentina vs pooled field: exact Poisson rate-ratio tests ---
METRICS = ["yellows_received", "dismissals_received", "yellows_drawn",
           "dismissals_drawn", "pen_goals_for", "pen_goals_against"]
FAVORABLE_IF = {"yellows_received": "low", "dismissals_received": "low",
                "yellows_drawn": "high", "dismissals_drawn": "high",
                "pen_goals_for": "high", "pen_goals_against": "low"}


def pois_ci(c, n):
    lo = 0.5 * stats.chi2.ppf(0.025, 2 * c) / n if c > 0 else 0.0
    hi = 0.5 * stats.chi2.ppf(0.975, 2 * c + 2) / n
    return lo, hi


rows = []
for era, grp in per_era.groupby("era"):
    arg = grp[grp.team_name == "Argentina"]
    fld = grp[grp.team_name != "Argentina"]
    if arg.empty:
        continue
    m_a, m_f = int(arg.matches.iloc[0]), int(fld.matches.sum())
    for met in METRICS:
        if era == "1930-1966" and ("yellows" in met or "dismissals" in met):
            continue  # no booking records before 1970
        c_a, c_f = int(arg[met].iloc[0]), int(fld[met].sum())
        r_a, r_f = c_a / m_a, c_f / m_f
        lo, hi = pois_ci(c_a, m_a)
        # exact two-sample Poisson test via binomial conditioning on total events
        p = stats.binomtest(c_a, c_a + c_f, m_a / (m_a + m_f)).pvalue if c_a + c_f > 0 else 1.0
        rows.append(dict(era=era, metric=met, favorable_if=FAVORABLE_IF[met],
                         arg_count=c_a, arg_matches=m_a, arg_rate=round(r_a, 3),
                         arg_ci_low=round(lo, 3), arg_ci_high=round(hi, 3),
                         field_rate=round(r_f, 3),
                         rate_ratio=round(r_a / r_f, 3) if r_f else np.nan,
                         p_value=round(p, 4)))
tests = pd.DataFrame(rows)
tests.to_csv(rf"{OUT}\argentina_vs_field_tests.csv", index=False)

print("=== Argentina per tournament (1990-2022) ===")
at = per_tourn[per_tourn.team_name == "Argentina"]
print(at.to_string(index=False))
print("\n=== Argentina vs field, exact Poisson tests ===")
print(tests.to_string(index=False))
