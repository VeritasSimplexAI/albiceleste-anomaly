"""Export all processed analysis outputs into one site-ready data.js
(window.WC_DATA = {...}) consumed by the static site. Rerun after any pipeline
refresh. Includes 1930-1986 awarded pens automatically once that CSV exists.
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys, os, json
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
ROOT = rf"{_ROOT}"
P = rf"{ROOT}\data\processed"
SITE = rf"{ROOT}\site"
os.makedirs(SITE, exist_ok=True)

def recs(df):
    return json.loads(df.to_json(orient="records"))

out = {}

# per-tournament team stats, full history (cards/pens-converted/results)
tourn = pd.read_csv(rf"{P}\team_tournament_stats.csv")
out["team_tournament"] = recs(tourn)

# Argentina vs field era tests (cards + converted pens + 2026 cards/fouls)
out["era_tests"] = recs(pd.read_csv(rf"{P}\argentina_vs_field_all_eras.csv"))

# decision metrics: penalties awarded
out["pens_awarded_tests"] = recs(pd.read_csv(rf"{P}\pens_awarded_tests_all_eras.csv"))

# per-incident awarded penalties (1990-2010 + 1930-1986 when present)
pen_files = ["penalties_awarded_1990_2010.csv", "penalties_awarded_1930_1986.csv"]
pens_all = []
for f in pen_files:
    fp = rf"{ROOT}\data\penalties-historical\{f}"
    if os.path.exists(fp):
        pens_all.append(pd.read_csv(fp, encoding="utf-8-sig"))
if pens_all:
    pa = pd.concat(pens_all, ignore_index=True)
    out["pens_incidents"] = recs(pa)
    # per-tournament awarded series: Argentina for/against + field per-team-match rate
    tm = tourn.groupby("year").matches.sum()  # team-matches per tournament
    per_t = []
    for yr, g in pa.groupby("tournament_year"):
        a_for = int((g.team_awarded == "Argentina").sum())
        a_ag = int((g.opponent == "Argentina").sum())
        am = tourn[(tourn.year == yr) & (tourn.team_name == "Argentina")].matches
        per_t.append(dict(year=int(yr), total_awarded=len(g),
                          field_rate_per_team_match=round(len(g) / tm.get(yr, np.nan), 4),
                          arg_matches=int(am.iloc[0]) if len(am) else 0,
                          arg_for=a_for, arg_against=a_ag))
    out["pens_awarded_by_tournament"] = per_t

# FBref squad discipline 2014-2026 (fouls, cards, PKatt)
out["squad_discipline"] = recs(pd.read_csv(rf"{P}\squad_discipline_clean.csv"))

# VAR
out["var_tests"] = recs(pd.read_csv(rf"{P}\var_argentina_tests.csv"))
out["var_leaderboard"] = recs(pd.read_csv(rf"{P}\var_net_leaderboard.csv")
                              .rename(columns={"Unnamed: 0": "team"}))
_vres = rf"{ROOT}\data\officiating-extra\var_incidents_resolved.csv"
var = pd.read_csv(_vres if os.path.exists(_vres) else rf"{ROOT}\data\officiating-extra\var_incidents.csv",
                  encoding="utf-8-sig")
var = var[var.decision_type != "no_overturn"]  # 26 checks confirmed the call; not overturns
out["var_incidents_argentina"] = recs(var[(var.beneficiary_team == "Argentina") |
                                          (var.against_team == "Argentina")])

# deep analysis outputs
for key, f in [("eb_rankings", "eb_rankings.csv"), ("fdr_outliers", "fdr_outliers.csv"),
               ("did", "did_results.csv"), ("cohort_2022", "cohort_2022.csv"),
               ("argentina_2026", "argentina_vs_field_2026.csv")]:
    out[key] = recs(pd.read_csv(rf"{P}\{f}"))

# referee-teams study (present once referee_analysis.py has run)
for key, f in [("crew_growth", "referee_crew_growth.csv"),
               ("referee_repeats", "referee_repeat_leaderboard.csv"),
               ("argentina_officials", "argentina_officials.csv"),
               ("argentina_official_records", "argentina_official_records.csv"),
               ("argentina_official_comparison", "argentina_official_comparison.csv")]:
    fp = rf"{P}\{f}"
    if os.path.exists(fp):
        out[key] = recs(pd.read_csv(fp, encoding="utf-8-sig"))
fp = rf"{P}\referee_confederation_mix.csv"
if os.path.exists(fp):
    out["referee_conf_mix"] = recs(pd.read_csv(fp, encoding="utf-8-sig")
                                   .rename(columns={"Unnamed: 0": "confederation", "ref_conf": "confederation"}))

# ===== "The record": Argentina at every World Cup + full match browser =====
mlv_full = pd.read_csv(rf"{P}\match_team_level.csv")
arg_all = mlv_full[mlv_full.team_name == "Argentina"].copy()
ts = pd.read_csv(rf"{ROOT}\data\worldcup-1930-2022\tournament_standings.csv")
ts = ts[ts.team_name == "Argentina"]
ts["year"] = ts.tournament_id.str[-4:].astype(int)
POS = ts.set_index("year").position

STAGE_ORD = {"group stage": 1, "final round": 1, "round of 16": 2, "quarter-finals": 3,
             "second group stage": 3, "semi-finals": 4, "third-place match": 4, "final": 5}
STAGE_LBL = {1: "Group stage", 2: "Round of 16", 3: "Quarter-finals", 4: "Semi-finals", 5: "Final"}
record = []
tstats = tourn[tourn.team_name == "Argentina"]
for yr, g in arg_all.groupby("year"):
    best = max(STAGE_ORD.get(s, 1) for s in g.stage_name)
    pos = POS.get(yr)
    if pos == 1: label, ordv = "CHAMPIONS", 6
    elif pos == 2: label, ordv = "Runners-up", 5
    else:
        label, ordv = STAGE_LBL[best], best
        if (g.stage_name == "second group stage").any() and best == 3: label = "2nd group stage"
    t = tstats[tstats.year == yr].iloc[0]
    record.append(dict(year=int(yr), label=label, ord=ordv, matches=int(t.matches),
                       wins=int(t.wins), draws=int(t.draws), losses=int(t.losses),
                       gf=int(t.goals_for), ga=int(t.goals_against)))
record.append(dict(year=2026, label="Final — Jul 19 (pending)", ord=5, matches=7,
                   wins=7, draws=0, losses=0, gf=19, ga=7))
out["argentina_record"] = record

matches_browser = [dict(year=int(r.year), date=str(r.match_date)[:10], stage=r.stage_name,
                        opponent=r.opponent_name, score=f"{int(r.goals_for)}–{int(r.goals_against)}",
                        result="W" if r.win else ("D" if r.draw else "L"),
                        et="yes" if r.extra_time else "",
                        pens=f"{int(r.penalties_for)}–{int(r.penalties_against)}" if r.penalty_shootout else "")
                   for r in arg_all.itertuples()]
m26a = pd.read_csv(rf"{ROOT}\data\worldcup-2026\matches_2026.csv", encoding="utf-8-sig")
m26a = m26a[(m26a.home_team == "Argentina") | (m26a.away_team == "Argentina")]
for r in m26a.itertuples():
    gf, ga = ((r.home_score, r.away_score) if r.home_team == "Argentina" else (r.away_score, r.home_score))
    matches_browser.append(dict(year=2026, date=r.match_date, stage=r.stage,
                                opponent=r.away_team if r.home_team == "Argentina" else r.home_team,
                                score=f"{gf}–{ga}", result="W" if gf > ga else ("D" if gf == ga else "L"),
                                et="yes" if r.extra_time == "yes" else "",
                                pens=r.score_penalties if isinstance(r.score_penalties, str) else ""))
out["argentina_all_matches"] = sorted(matches_browser, key=lambda x: x["date"])

# full directional VAR incident table (site browser)
out["var_incidents_all"] = recs(var.dropna(subset=["beneficiary_team"])[
    ["tournament_year", "match_date", "home_team", "away_team", "decision_type",
     "beneficiary_team", "against_team", "description"]])

# referee forensics (four independent tests; sources: analysis/subreports/*)
fp = rf"{P}\elo_residuals_by_referee.csv"
if os.path.exists(fp):
    rr = pd.read_csv(fp, encoding="utf-8-sig")
    out["forensics_ref_residuals"] = recs(
        rr[rr.n_argentina_matches >= 2][["referee", "referee_country", "n_argentina_matches",
                                         "arg_resid_sum", "p_perm_onesided_pos",
                                         "p_perm_twosided_centered", "years"]]
        .sort_values("n_argentina_matches", ascending=False))
    hp = pd.read_csv(rf"{P}\hierarchical_pairs.csv", encoding="utf-8-sig")
    out["forensics_pairs_argentina"] = recs(
        hp[hp.is_argentina == True][["referee", "n_matches", "yellows_total", "expected_nonpair",
                                     "oe_ratio_raw", "rate_ratio_shrunk", "abs_rank"]]
        .sort_values("abs_rank").head(8))
    # champion title runs vs Elo (source: analysis/subreports/ELO_FORENSICS.md §3b, verified run)
    out["forensics_champions"] = [
        dict(year=1990, champion="West Germany", resid=1.18), dict(year=1994, champion="Brazil", resid=1.63),
        dict(year=1998, champion="France", resid=0.98), dict(year=2002, champion="Brazil", resid=2.85),
        dict(year=2006, champion="Italy", resid=1.72), dict(year=2010, champion="Spain", resid=0.45),
        dict(year=2014, champion="Germany", resid=1.63), dict(year=2018, champion="France", resid=2.03),
        dict(year=2022, champion="Argentina", resid=-0.72), dict(year=2026, champion="Argentina (finalist)", resid=1.07),
    ]

# draw analysis (Exhibit H)
fp = rf"{P}\draw_argentina_three_metrics.csv"
if os.path.exists(fp):
    out["draw_group_summary"] = recs(pd.read_csv(fp, encoding="utf-8-sig"))
    out["draw_group_pctl"] = recs(pd.read_csv(rf"{P}\draw_argentina_group_difficulty.csv", encoding="utf-8-sig"))
    koE = pd.read_csv(rf"{P}\draw_ko_by_stage_enriched.csv", encoding="utf-8-sig")
    koE = koE[koE.stage != "third place"]
    STAGE_ORD = {"round of 32": 0, "round of 16": 1, "quarter-finals": 2, "semi-finals": 3, "final": 4}
    paths = []
    for yr in [2022, 2026]:
        g = koE[koE.year == yr]
        deep = g.groupby("team").size()
        for t in deep[deep >= 3].index:
            p = g[g.team == t].copy()
            p["o"] = p.stage.map(STAGE_ORD)
            p = p.sort_values("o")
            paths.append(dict(year=yr, team=t, n=len(p),
                              path_elo=round(p.opp_elo.mean(), 0),
                              path_fifa=round(p.opp_fifa.mean(), 1),
                              pot1_opps=int((p.opp_pot == 1).sum()),
                              route=" → ".join(f"{r.opp} ({r.opp_elo:.0f})" for r in p.itertuples())))
    out["draw_ko_paths"] = paths

# Copa América control (cross-competition penalty comparison)
fp = rf"{ROOT}\data\copa-america\copa_squad_discipline.csv"
if os.path.exists(fp):
    csq = pd.read_csv(fp, encoding="utf-8-sig")
    ctrl = []
    for yr, g in csq.groupby("edition_year"):
        a, f = g[g.team == "Argentina"], g[g.team != "Argentina"]
        if a.empty or a.penalty_kicks_attempted.isna().all(): continue
        ar, am = int(a.penalty_kicks_attempted.sum()), int(a.matches_played.sum())
        fr, fm = int(f.penalty_kicks_attempted.sum()), int(f.matches_played.sum())
        ctrl.append(dict(comp="Copa América", year=int(yr), arg=ar, matches=am,
                         ratio=round((ar / am) / (fr / fm), 2) if fr else None))
    ctrl.append(dict(comp="World Cup", year=2022, arg=5, matches=7, ratio=4.80))
    ctrl.append(dict(comp="World Cup", year=2026, arg=3, matches=7, ratio=4.69))
    out["copa_control"] = sorted(ctrl, key=lambda x: x["year"])
    crec = pd.read_csv(rf"{ROOT}\data\copa-america\copa_record.csv", encoding="utf-8-sig")
    out["copa_recent"] = recs(crec[crec.year >= 2011][["year", "host", "finish", "matches", "wins", "draws", "losses"]])

# whistle study (player-level tackles/fouls/cards)
for key, f in [("whistle_team", "whistle_team.csv"),
               ("whistle_players", "whistle_players.csv"),
               ("whistle_pairs", "whistle_pairs.csv")]:
    fp = rf"{P}\{f}"
    if os.path.exists(fp):
        out[key] = recs(pd.read_csv(fp, encoding="utf-8-sig"))

# CONMEBOL peers referee mix + crew by confederation
for key, f in [("conmebol_ref_mix", "conmebol_ref_mix.csv"), ("crew_by_conf", "crew_by_conf.csv")]:
    fp = rf"{P}\{f}"
    if os.path.exists(fp):
        out[key] = recs(pd.read_csv(fp, encoding="utf-8-sig"))

# confirmed (non-overturn) VAR reviews — coverage-biased lower bound, see NOTES
fp = rf"{ROOT}\data\officiating-extra\var_confirmed_reviews.csv"
if os.path.exists(fp):
    out["var_confirmed"] = recs(pd.read_csv(fp, encoding="utf-8-sig"))

# hypothetical run-to-final difficulty (projected at the draw)
fp = rf"{P}\hypothetical_paths.csv"
if os.path.exists(fp):
    hp2 = pd.read_csv(fp, encoding="utf-8-sig")
    out["hypo_paths"] = recs(hp2[hp2.slot_assumption == "blend"][
        ["year", "team", "unweighted_path_elo", "weighted_path_elo"]].round(0))
    # Argentina's projected-difficulty rank among top-8-Elo seeds (verified: subreports/HYPOTHETICAL_PATHS.md)
    out["hypo_arg_ranks"] = [
        dict(year=1986, unw="1/9", wt="2/9"), dict(year=1990, unw="3/9", wt="2/9"),
        dict(year=1994, unw="1/8", wt="1/8"), dict(year=1998, unw="2/9", wt="2/9"),
        dict(year=2002, unw="5/8", wt="6/8"), dict(year=2006, unw="7/8", wt="4/8"),
        dict(year=2010, unw="4/8", wt="2/8"), dict(year=2014, unw="6/8", wt="5/8"),
        dict(year=2018, unw="2/8", wt="1/8"), dict(year=2022, unw="7/8", wt="7/8"),
        dict(year=2026, unw="6/8", wt="6/8"),
    ]

# fouls-before-first-yellow ("the rope"), StatsBomb events 2018+2022
fp = rf"{ROOT}\data\player-defense\fouls_before_yellow_team.csv"
if os.path.exists(fp):
    out["whistle_rope"] = recs(pd.read_csv(fp, encoding="utf-8-sig"))

# contested calls video index
fp = rf"{ROOT}\data\contested-calls\contested_calls.csv"
if os.path.exists(fp):
    out["contested_calls"] = recs(pd.read_csv(fp, encoding="utf-8-sig"))

# robustness + impact + president eras
for key, f in [("robustness_tests", "robustness_tests.csv"),
               ("decision_impact", "decision_impact.csv"),
               ("president_eras", "president_eras.csv")]:
    fp = rf"{P}\{f}"
    if os.path.exists(fp):
        out[key] = recs(pd.read_csv(fp, encoding="utf-8-sig"))

# deep-run penalty cohort, 2022 + 2026 (teams with >=5 matches; PKatt = pens awarded)
sq = pd.read_csv(rf"{P}\squad_discipline_clean.csv")
coh = sq[(sq.tournament_year.isin([2022, 2026])) & (sq.matches_played >= 5)].copy()
coh["pens_pm"] = (coh.penalty_kicks_attempted / coh.matches_played).round(3)
out["cohort_post22"] = recs(coh[["tournament_year", "team", "matches_played",
                                 "penalty_kicks_attempted", "pens_pm"]])

# "the receipts": per-match decision ledger, Argentina 2022 + 2026
mlv = pd.read_csv(rf"{P}\match_team_level.csv")
a22 = mlv[(mlv.team_name == "Argentina") & (mlv.year == 2022)]
var = pd.read_csv(rf"{ROOT}\data\officiating-extra\var_incidents.csv", encoding="utf-8-sig")
va = var[(var.beneficiary_team == "Argentina") | (var.against_team == "Argentina")].copy()
va["md"] = pd.to_datetime(va.match_date)
def var_sum(date, opponent):
    d0 = pd.to_datetime(date)
    g = va[(abs(va.md - d0).dt.days <= 1) &
           ((va.home_team == opponent) | (va.away_team == opponent))]
    f = [r.decision_type for r in g.itertuples() if r.beneficiary_team == "Argentina"]
    a = [r.decision_type for r in g.itertuples() if r.against_team == "Argentina"]
    fmt = lambda L: ", ".join(x.replace("_", " ") for x in L) if L else ""
    return fmt(f), fmt(a)
receipts = []
for r in a22.itertuples():
    d = pd.to_datetime(r.match_date).date().isoformat()
    vf, vg = var_sum(d, r.opponent_name if hasattr(r, "opponent_name") else opp_row.team)
    receipts.append(dict(date=d, stage=r.stage_name, opponent=r.opponent_name,
                         score=f"{r.goals_for}–{r.goals_against}",
                         pens_for=int(r.pen_goals), pens_against=int(r.opp_pen_goals),
                         pens_note="scored only; +1 awarded & missed v Poland (VAR)" if r.opponent_name == "Poland" else "",
                         opp_reds=int(r.opp_dismissals), own_reds=int(r.dismissals),
                         var_for=vf, var_against=vg))
c26 = pd.read_csv(rf"{ROOT}\data\worldcup-2026\argentina_matches_cards_2026.csv", encoding="utf-8-sig")
m26x = pd.read_csv(rf"{ROOT}\data\worldcup-2026\matches_2026.csv", encoding="utf-8-sig")
for r in c26[c26.team == "Argentina"].itertuples():
    d = pd.to_datetime(r.match_date).date().isoformat()
    opp_row = c26[(c26.match_date == r.match_date) & (c26.team != "Argentina")].iloc[0]
    mrow = m26x[(m26x.match_date == r.match_date) &
                ((m26x.home_team == "Argentina") | (m26x.away_team == "Argentina"))].iloc[0]
    gf, ga = ((mrow.home_score, mrow.away_score) if mrow.home_team == "Argentina"
              else (mrow.away_score, mrow.home_score))
    vf, vg = var_sum(d, r.opponent_name if hasattr(r, "opponent_name") else opp_row.team)
    receipts.append(dict(date=d, stage=mrow.stage, opponent=opp_row.team,
                         score=f"{gf}–{ga}",
                         pens_for=int(r.penalties_awarded), pens_against=int(opp_row.penalties_awarded),
                         pens_note="awarded (Messi missed v Austria, saved v Egypt; Lautaro scored v Jordan)"
                                   if r.penalties_awarded else "",
                         opp_reds=int(opp_row.red_cards), own_reds=int(r.red_cards),
                         var_for=vf, var_against=vg))
out["argentina_receipts"] = sorted(receipts, key=lambda x: x["date"])

# 2026 matches + Argentina per-match cards
out["matches_2026"] = recs(pd.read_csv(rf"{ROOT}\data\worldcup-2026\matches_2026.csv", encoding="utf-8-sig"))
out["arg_2026_matches"] = recs(pd.read_csv(rf"{ROOT}\data\worldcup-2026\argentina_matches_cards_2026.csv", encoding="utf-8-sig"))

with open(rf"{SITE}\data.js", "w", encoding="utf-8") as fh:
    fh.write("window.WC_DATA = ")
    json.dump(out, fh, ensure_ascii=False)
    fh.write(";")
# cache-bust: stamp a fresh version on the script tags each export
import time as _t
_ih = open(rf"{SITE}\index.html", encoding="utf-8").read()
import re as _re
_ih = _re.sub(r'(data|app)\.js\?v=\d+', lambda m: m.group(0).split("?")[0] + "?v=" + str(int(_t.time())), _ih)
open(rf"{SITE}\index.html", "w", encoding="utf-8").write(_ih)
size = os.path.getsize(rf"{SITE}\data.js") / 1024
print(f"site/data.js written ({size:.0f} KB), keys: {sorted(out.keys())}")
print("pens_awarded_by_tournament years:", [r['year'] for r in out.get('pens_awarded_by_tournament', [])])
