"""Within-referee bias analysis: does the SAME referee treat Argentina differently
than he treats other teams?

Design: each referee serves as his own control, so personal style (card-happy vs
lenient) cancels out. Two components:

1. Pooled within-referee Poisson GLM on team-match rows 1990-2022:
       yellows ~ C(referee) + is_arg + is_arg_opponent + knockout + C(year)
   Referee fixed effects make is_arg / is_arg_opponent within-referee estimates.
   Cluster-robust SEs by match (two team rows per match). Same model for
   converted penalties (pen_goals) - much lower power, reported honestly.

2. Per-referee descriptive table (>=2 Argentina matches AND >=4 total matches):
   cards / converted pens to Argentina and to Argentina's opponents vs the same
   referee's rate per team-match in his OTHER matches. Exact conditional Poisson
   tests (binomial), Benjamini-Hochberg FDR across referees per test family.
   Nothing is flagged as "biased" - effect sizes + p/q values only.

Scope: 1990-2022 (552 matches, per-match cards+pens available for all matches).
2026 is a descriptive appendix only (per-match cards exist only for Argentina's
own 2026 matches, so no within-referee control group is possible).

Outputs:
  data/processed/within_referee_results.csv  (per-referee table)
  stdout: join rate, pooled model IRRs, per-referee table, 2026 appendix
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import binomtest
from statsmodels.stats.multitest import multipletests

sys.stdout.reconfigure(encoding="utf-8")
ROOT = rf"{_ROOT}"
P = rf"{ROOT}\data\processed"
RT = rf"{ROOT}\data\referee-teams"

# same alias approach as analysis/referee_comparison.py (654/654 join there)
ALIAS = {"Ireland": "Republic of Ireland", "USA": "United States", "Korea Republic": "South Korea",
         "IR Iran": "Iran", "Türkiye": "Turkey", "Czechia": "Czech Republic", "China PR": "China",
         "Côte d'Ivoire": "Ivory Coast", "FR Yugoslavia": "Yugoslavia", "Curacao": "Curaçao"}
def norm(s): return ALIAS.get(str(s).strip(), str(s).strip())
def key(date, a, b): return f"{date}|" + "|".join(sorted([norm(a), norm(b)]))

# ---------------------------------------------------------------- build data
ml = pd.read_csv(rf"{P}\match_team_level.csv")
ml = ml[ml.year >= 1990].copy()          # cards/pens per match verified from 1990 on
ml["date"] = pd.to_datetime(ml.match_date).dt.date.astype(str)
ml["mkey"] = [key(d, a, b) for d, a, b in zip(ml.date, ml.team_name, ml.opponent_name)]

mo = pd.concat([
    pd.read_csv(rf"{RT}\match_officials_1990_2010.csv", encoding="utf-8-sig"),
    pd.read_csv(rf"{RT}\match_officials_2014_2026.csv", encoding="utf-8-sig"),
], ignore_index=True)
mo["date"] = pd.to_datetime(mo.match_date).dt.date.astype(str)
mo["mkey"] = [key(d, a, b) for d, a, b in zip(mo.date, mo.home_team, mo.away_team)]
mo22 = mo[mo.tournament_year <= 2022]

joined = set(mo22.mkey) & set(ml.mkey)
print(f"JOIN 1990-2022: {len(joined)}/{mo22.mkey.nunique()} officials matches matched "
      f"({len(joined)/mo22.mkey.nunique():.1%}); team-level matches: {ml.mkey.nunique()}")

df = ml.merge(mo22[["mkey", "referee"]].drop_duplicates("mkey"), on="mkey")
df["is_arg"] = (df.team_name == "Argentina").astype(int)
df["is_arg_opponent"] = (df.opponent_name == "Argentina").astype(int)
df["knockout"] = df.knockout_stage.astype(int)
df["cluster"] = pd.factorize(df.mkey)[0]
print(f"team-match rows: {len(df)}; referees: {df.referee.nunique()}; "
      f"ARG team-rows: {df.is_arg.sum()}")

# ------------------------------------------------- pooled within-referee GLM
def fit_pooled(data, outcome, label):
    f = f"{outcome} ~ C(referee) + is_arg + is_arg_opponent + knockout + C(year)"
    model = smf.glm(f, data=data, family=sm.families.Poisson())
    rank = np.linalg.matrix_rank(model.exog)
    res = model.fit(cov_type="cluster", cov_kwds={"groups": data.cluster.values})
    print(f"\n=== Pooled within-referee Poisson GLM: {label} ===")
    print(f"n rows={len(data)}, clusters(matches)={data.cluster.nunique()}, "
          f"params={model.exog.shape[1]}, design rank={rank}"
          + ("  [RANK DEFICIENT]" if rank < model.exog.shape[1] else ""))
    ci = res.conf_int()
    for term in ["is_arg", "is_arg_opponent", "knockout"]:
        b, lo, hi, p = res.params[term], ci.loc[term, 0], ci.loc[term, 1], res.pvalues[term]
        print(f"  {term:16s} IRR={np.exp(b):5.3f}  95% CI [{np.exp(lo):.3f}, {np.exp(hi):.3f}]"
              f"  p={p:.3f}")
    # the directly bias-relevant contrast: are ARG's opponents carded more than ARG,
    # by the same referee, relative to his own baseline?
    ct = res.t_test("is_arg_opponent - is_arg = 0")
    lo, hi = ct.conf_int()[0]
    print(f"  contrast opp-arg IRR={np.exp(ct.effect[0]):5.3f}  95% CI "
          f"[{np.exp(lo):.3f}, {np.exp(hi):.3f}]  p={float(ct.pvalue):.3f}")
    return res

fit_pooled(df, "yellows", "yellow cards received (per team-match)")

# pens: referees whose matches contain zero converted pens contribute no
# information to a fixed-effects Poisson (their FE -> -inf); drop those groups
# as in standard conditional/FE Poisson practice.
pen_ok = df.groupby("referee").pen_goals.transform("sum") > 0
dfp = df[pen_ok].copy()
dropped = df.referee.nunique() - dfp.referee.nunique()
print(f"\n[pens model: dropped {dropped} referees with zero converted pens in all "
      f"their matches ({len(df) - len(dfp)} rows) - uninformative for FE Poisson]")
fit_pooled(dfp, "pen_goals", "converted penalties scored (per team-match)")

# --------------------------------------------------------- per-referee table
def exact_rate_p(c1, e1, c2, e2):
    """Exact conditional test of Poisson rate c1/e1 vs c2/e2:
    given c1+c2, c1 ~ Binomial(c1+c2, e1/(e1+e2))."""
    if c1 + c2 == 0:
        return 1.0
    return binomtest(int(c1), int(c1 + c2), e1 / (e1 + e2)).pvalue

rows = []
for ref, sub in df.groupby("referee"):
    arg = sub[sub.is_arg == 1]                      # Argentina's own rows
    other = sub[(sub.is_arg == 0) & (sub.is_arg_opponent == 0)]
    n_arg, n_other = len(arg), other.mkey.nunique()
    if n_arg < 2 or (n_arg + n_other) < 4:
        continue
    e_other = 2 * n_other                            # team-match exposures
    c_arg, c_opp = arg.yellows.sum(), arg.opp_yellows.sum()
    c_oth = other.yellows.sum()
    p_arg, p_opp = arg.pen_goals.sum(), arg.opp_pen_goals.sum()
    p_oth = other.pen_goals.sum()
    r_oth_cards = c_oth / e_other
    r_oth_pens = p_oth / e_other
    rows.append(dict(
        referee=ref,
        years="/".join(map(str, sorted(sub.year.unique()))),
        n_arg_matches=n_arg, n_other_matches=n_other,
        cards_to_arg=c_arg, cards_to_arg_per_match=round(c_arg / n_arg, 2),
        cards_to_opp=c_opp, cards_to_opp_per_match=round(c_opp / n_arg, 2),
        other_cards_per_team_match=round(r_oth_cards, 2),
        card_diff_arg_matches=round((arg.opp_yellows - arg.yellows).mean(), 2),
        irr_cards_arg=round(c_arg / n_arg / r_oth_cards, 2) if r_oth_cards else np.nan,
        p_cards_arg=exact_rate_p(c_arg, n_arg, c_oth, e_other),
        irr_cards_opp=round(c_opp / n_arg / r_oth_cards, 2) if r_oth_cards else np.nan,
        p_cards_opp=exact_rate_p(c_opp, n_arg, c_oth, e_other),
        pens_by_arg=p_arg, pens_by_opp=p_opp,
        other_pens_per_team_match=round(r_oth_pens, 3),
        p_pens_arg=exact_rate_p(p_arg, n_arg, p_oth, e_other),
        p_pens_opp=exact_rate_p(p_opp, n_arg, p_oth, e_other),
    ))

tab = pd.DataFrame(rows).sort_values(["n_arg_matches", "p_cards_opp"],
                                     ascending=[False, True]).reset_index(drop=True)

# Benjamini-Hochberg across referees, separately per test family
for fam in ["p_cards_arg", "p_cards_opp", "p_pens_arg", "p_pens_opp"]:
    tab["q" + fam[1:]] = multipletests(tab[fam], method="fdr_bh")[1]
qcols = [c for c in tab.columns if c.startswith("q_")]
tab["fdr_survives_05"] = tab.apply(
    lambda r: ";".join(c[2:] for c in qcols if r[c] < 0.05), axis=1)

for c in tab.columns:
    if c.startswith(("p_", "q_")):
        tab[c] = tab[c].round(4)
tab.to_csv(rf"{P}\within_referee_results.csv", index=False)
print(f"\nwrote {P}\\within_referee_results.csv ({len(tab)} referees with "
      f">=2 ARG matches and >=4 total)")

print("\n=== Per-referee within-referee comparison (cards) ===")
print(tab[["referee", "years", "n_arg_matches", "n_other_matches",
           "cards_to_arg_per_match", "cards_to_opp_per_match",
           "other_cards_per_team_match", "card_diff_arg_matches",
           "irr_cards_arg", "p_cards_arg", "q_cards_arg",
           "irr_cards_opp", "p_cards_opp", "q_cards_opp"]].to_string(index=False))
print("\n=== Per-referee within-referee comparison (converted pens) ===")
print(tab[["referee", "n_arg_matches", "pens_by_arg", "pens_by_opp",
           "other_pens_per_team_match", "p_pens_arg", "p_pens_opp",
           "q_pens_arg", "q_pens_opp"]].to_string(index=False))
surv = tab[tab.fdr_survives_05 != ""]
print("\nFDR (BH, q<0.05) survivors:",
      "none" if surv.empty else surv[["referee", "fdr_survives_05"]].to_string(index=False))

# ------------------------------------------------- 2026 descriptive appendix
print("\n=== APPENDIX: Argentina 2026 (descriptive only - no control group; "
      "per-match cards for other 2026 matches unavailable) ===")
c26 = pd.read_csv(rf"{ROOT}\data\worldcup-2026\argentina_matches_cards_2026.csv",
                  encoding="utf-8-sig")
c26["date"] = pd.to_datetime(c26.match_date).dt.date.astype(str)
arg26 = c26[c26.team == "Argentina"].copy()
opp26 = c26[c26.opponent == "Argentina"].set_index("date")
mo26 = mo[mo.tournament_year == 2026]
ref26 = {r.date: r.referee for r in mo26.itertuples()
         if "Argentina" in (norm(r.home_team), norm(r.away_team))}
prior = df.groupby("referee").agg(prior_matches=("mkey", "nunique"),
                                  prior_cards_rate=("yellows", "mean"))
for r in arg26.itertuples():
    o = opp26.loc[r.date]
    ref = ref26.get(r.date, "?")
    extra = ""
    if ref in prior.index:
        extra = (f"  [1990-2022: {prior.loc[ref].prior_matches:.0f} matches, "
                 f"{prior.loc[ref].prior_cards_rate:.2f} cards/team-match]")
    print(f"  {r.date} vs {r.opponent:<12s} ref={ref:<22s} "
          f"cards ARG {r.yellow_cards}Y/{r.red_cards}R vs opp {o.yellow_cards}Y/{o.red_cards}R, "
          f"fouls {r.fouls_committed}-{o.fouls_committed}, "
          f"pens awarded {r.penalties_awarded}-{o.penalties_awarded}{extra}")
