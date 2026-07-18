"""
Referee-ASSIGNMENT randomness test, World Cups 1990-2026.
=========================================================

Question: Szymon Marciniak refereed Argentina 4 times across 2018/2022/2026
(including the 2022 final and Argentina's 2026 opener) -- the only 4-match
referee-team pairing in 1990-2026. How improbable is that pairing under a
plausibly random assignment process? This tests FIFA's *assignment* process,
completely separate from anything that happens inside the matches.

Method
------
1. Reconstruct per tournament: the played-match list, the actual referee of
   each match, the appointed (serving) referee pool, and each referee's
   realized match count.
2. Verify which neutrality constraints FIFA actually respects:
     - country neutrality (referee's country is never one of the two teams)
     - confederation neutrality (referee's confederation vs the two teams)
   Constraints are then enforced in the null models only as strongly as the
   real data shows they are respected.
3. Null model A (primary): within each tournament, randomly re-assign the
   realized referee workloads to matches (each referee keeps his exact
   observed match count), subject to (a) strict country neutrality (observed
   to hold with zero violations) and (b) a *calibrated soft* confederation
   constraint: same-confederation candidates are re-weighted by an odds
   factor w (per tournament x stage class), calibrated so the simulated mean
   number of same-confederation assignments matches the observed number
   (confederation neutrality is NOT absolute in reality - FIFA avoids it
   only partially). Random sequential assignment with restarts on the rare
   dead ends caused by the exact-count + country constraints.
4. Null model B (sensitivity): each match's referee drawn uniformly from the
   tournament's serving referee pool (country-neutral members only),
   ignoring realized match counts.
5. Statistics per simulation, computed jointly across ALL tournaments:
     (i)   max referee-team pair count 1990-2026
     (ii)  max pair count among pairs spanning >= 3 distinct tournaments
     (iii) indicator: some referee has >= 4 Argentina matches
     (iv)  count of "same referee takes a team's final and that team's
           next-tournament opening match" coincidences (any finalist)
   Monte Carlo p-values are P(sim >= observed) with the standard +1
   correction, plus exact (Clopper-Pearson) 95% CIs on the raw proportion.

Outputs
-------
- data/processed/assignment_sim_results.csv  (summary stats + p-values)
- analysis/subreports/ASSIGNMENT_SIM.md      (full write-up)

Run:  python analysis/assignment_simulation.py
"""

import re
import time
import unicodedata
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
REF_DIR = ROOT / "data" / "referee-teams"
OUT_CSV = ROOT / "data" / "processed" / "assignment_sim_results.csv"
OUT_MD = ROOT / "analysis" / "subreports" / "ASSIGNMENT_SIM.md"

SEED = 42
N_SIMS_A = 20_000  # null model A (workload-preserving permutations)
N_SIMS_B = 20_000  # null model B (uniform pool draws)
MAX_RESTARTS = 500  # per tournament draw in model A

# Referees appointed but withdrawn/removed before officiating, 2014-2026
# batch (the 1990-2010 batch flags these directly in role_pool; the
# 2014-2026 batch documents them in NOTES_2014_2026.md instead).
WITHDRAWN_2014_2026 = {(2018, "Fahad Al-Mirdasi"), (2026, "Omar Artan")}

# Referee-name aliases: match-file spelling -> tournament-pool spelling
# (normalized form). Documented in the subreport.
REF_ALIASES = {
    "filippi cavani": "ernesto filippi",            # 1994, Uruguay
    "marco antonio rodriguez": "marco rodriguez",   # 2014, Mexico
}

# Confederations for teams absent from data/worldcup-1930-2022/teams.csv.
# "China PR"/"Curacao" are spelling variants; the rest are 2026 debutants
# (teams.csv only covers teams that appeared through 2022).
MANUAL_TEAM_CONF = {
    "China PR": "AFC",        # teams.csv row is named "China"
    "Jordan": "AFC",
    "Uzbekistan": "AFC",
    "Cape Verde": "CAF",
    "DR Congo": "CAF",        # teams.csv has only the historical "Zaire"
    "Curacao": "CONCACAF",
    "Curaçao": "CONCACAF",
    "Haiti": "CONCACAF",
}

# Team-identity merges for the pairing statistics (FIFA-recognised
# successor teams). Raw names are kept for the country-neutrality checks.
TEAM_MERGES = {"West Germany": "Germany"}


def norm_name(s: str) -> str:
    """Normalize an official's name: strip accents, lowercase, unify hyphens."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(s.lower().replace("-", " ").split())


# ----------------------------------------------------------------------
# 1. Load data
# ----------------------------------------------------------------------
def load_data():
    m1 = pd.read_csv(REF_DIR / "match_officials_1990_2010.csv", encoding="utf-8-sig")
    m2 = pd.read_csv(REF_DIR / "match_officials_2014_2026.csv", encoding="utf-8-sig")
    matches = pd.concat([m1, m2], ignore_index=True)

    # One 2026 row carries a wikitext footnote inside the referee field
    # ("François Letexier (France){{efn-ua|Michael Oliver ... pulled out}}")
    # and a blank referee_country. Strip everything from the first "(" on.
    bad = matches["referee"].str.contains(r"\(", na=False)
    matches.loc[bad, "referee"] = matches.loc[bad, "referee"].str.replace(
        r"\s*\(.*$", "", regex=True
    )

    matches["nref"] = matches["referee"].map(norm_name).replace(REF_ALIASES)
    matches["match_date"] = pd.to_datetime(matches["match_date"])
    matches["stage_class"] = np.where(
        matches["stage"].str.contains("Group", case=False), "group", "knockout"
    )
    matches = matches.sort_values(["tournament_year", "match_date"]).reset_index(drop=True)

    t1 = pd.read_csv(REF_DIR / "tournament_officials_1990_2010.csv", encoding="utf-8-sig")
    t2 = pd.read_csv(REF_DIR / "tournament_officials_2014_2026.csv", encoding="utf-8-sig")
    pools = pd.concat([t1, t2], ignore_index=True)

    # Serving referee pool: role_pool contains "referee" but is not an
    # assistant/support role ("assistant referee" also contains "referee"!),
    # minus officials flagged as withdrawn/removed (1990-2010 flags in
    # role_pool text; 2014-2026 withdrawals listed in the NOTES file).
    is_ref = pools["role_pool"].str.contains("referee", case=False) & ~pools[
        "role_pool"
    ].str.contains("assistant|support", case=False)
    refpool = pools[is_ref].copy()
    refpool = refpool[~refpool["role_pool"].str.contains("withdrew|removed", case=False)]
    refpool = refpool[
        ~refpool.apply(
            lambda r: (r.tournament_year, r.official_name) in WITHDRAWN_2014_2026, axis=1
        )
    ]
    refpool["nname"] = refpool["official_name"].map(norm_name)

    teams = pd.read_csv(ROOT / "data" / "worldcup-1930-2022" / "teams.csv")
    team_conf = dict(zip(teams["team_name"], teams["confederation_code"]))
    team_conf.update(MANUAL_TEAM_CONF)

    # Sanity: every match referee must be in that tournament's serving pool.
    for yr, grp in matches.groupby("tournament_year"):
        pool_names = set(refpool.loc[refpool.tournament_year == yr, "nname"])
        missing = set(grp["nref"]) - pool_names
        if missing:
            raise ValueError(f"{yr}: match referees missing from pool: {missing}")
    # Sanity: every team must have a confederation.
    for t in set(matches["home_team"]) | set(matches["away_team"]):
        if t not in team_conf:
            raise ValueError(f"team without confederation mapping: {t}")

    return matches, refpool, team_conf


# ----------------------------------------------------------------------
# 2. Neutrality verification against the real data
# ----------------------------------------------------------------------
def verify_neutrality(matches, refpool, team_conf):
    """Return (#country violations, observed confed-conflict counts, totals, examples)."""
    ref_info = {
        (r.tournament_year, r.nname): (r.country, r.confederation)
        for r in refpool.itertuples()
    }
    country_viol = []
    confed_rows = []
    for r in matches.itertuples():
        country, conf = ref_info[(r.tournament_year, r.nref)]
        if country in (r.home_team, r.away_team):
            country_viol.append(r)
        conflict = conf in (team_conf[r.home_team], team_conf[r.away_team])
        confed_rows.append(conflict)
    matches = matches.assign(confed_conflict=confed_rows)
    budget = (
        matches.groupby(["tournament_year", "stage_class"])["confed_conflict"]
        .sum()
        .astype(int)
    )
    totals = matches.groupby(["tournament_year", "stage_class"]).size()
    examples = matches[matches["confed_conflict"]].sort_values("match_date")
    return country_viol, budget, totals, examples


# ----------------------------------------------------------------------
# 3. Build per-tournament simulation structures
# ----------------------------------------------------------------------
class Tournament:
    __slots__ = (
        "year", "n_matches", "global_idx", "used_refs", "counts",
        "elig_country", "confed_conflict", "stratum", "obs_conflicts",
        "weights", "pool_elig_lists",
    )


def build_structures(matches, refpool, team_conf):
    # Global integer ids for referees (person = normalized name across
    # tournaments) and merged team identities.
    ref_ids = {n: i for i, n in enumerate(sorted(set(matches["nref"]) | set(refpool["nname"])))}
    merged_team = lambda t: TEAM_MERGES.get(t, t)
    team_ids = {t: i for i, t in enumerate(sorted({merged_team(t) for t in set(matches["home_team"]) | set(matches["away_team"])}))}

    years = sorted(matches["tournament_year"].unique())
    year_bit = {y: 1 << i for i, y in enumerate(years)}

    # Global per-match arrays (aligned with `matches` row order)
    g_team1 = np.array([team_ids[merged_team(t)] for t in matches["home_team"]])
    g_team2 = np.array([team_ids[merged_team(t)] for t in matches["away_team"]])
    g_yearbit = np.array([year_bit[y] for y in matches["tournament_year"]])
    g_actual_ref = np.array([ref_ids[n] for n in matches["nref"]])

    ref_info = {
        (r.tournament_year, r.nname): (r.country, r.confederation)
        for r in refpool.itertuples()
    }

    tournaments = []
    for yr in years:
        sub = matches[matches.tournament_year == yr]
        t = Tournament()
        t.year = yr
        t.n_matches = len(sub)
        t.global_idx = sub.index.to_numpy()

        counts = Counter(sub["nref"])
        used = sorted(counts)  # referees who actually took >=1 match
        t.used_refs = np.array([ref_ids[n] for n in used])
        t.counts = np.array([counts[n] for n in used])

        u_country = [ref_info[(yr, n)][0] for n in used]
        u_conf = [ref_info[(yr, n)][1] for n in used]

        # Eligibility matrices (n_matches x n_used_refs)
        home = sub["home_team"].to_numpy()
        away = sub["away_team"].to_numpy()
        hconf = np.array([team_conf[x] for x in home])
        aconf = np.array([team_conf[x] for x in away])
        t.elig_country = np.array(
            [[c != h and c != a for c in u_country] for h, a in zip(home, away)]
        )
        t.confed_conflict = np.array(
            [[c == hc or c == ac for c in u_conf] for hc, ac in zip(hconf, aconf)]
        )
        t.stratum = (sub["stage_class"] == "knockout").to_numpy().astype(int)

        # Model B: per-match eligible list over the FULL serving pool
        pool = refpool[refpool.tournament_year == yr]
        pool_names = pool["nname"].tolist()
        pool_country = pool["country"].tolist()
        pool_gids = np.array([ref_ids[n] for n in pool_names])
        t.pool_elig_lists = [
            pool_gids[[c != h and c != a for c in pool_country]]
            for h, a in zip(home, away)
        ]
        tournaments.append(t)

    globals_pack = dict(
        ref_ids=ref_ids, team_ids=team_ids, years=years, year_bit=year_bit,
        g_team1=g_team1, g_team2=g_team2, g_yearbit=g_yearbit,
        g_actual_ref=g_actual_ref, n_total=len(matches),
    )
    return tournaments, globals_pack


def attach_conflict_targets(tournaments, budget):
    """Observed same-confed assignment counts (group, knockout) per tournament."""
    for t in tournaments:
        bg = int(budget.get((t.year, "group"), 0))
        bk = int(budget.get((t.year, "knockout"), 0))
        t.obs_conflicts = (bg, bk)
        t.weights = [1.0, 1.0]  # starting odds factors, calibrated later


def succession_pairs(matches):
    """(final_row_idx, opener_row_idx) for every finalist with a next WC."""
    years = sorted(matches["tournament_year"].unique())
    merged = lambda t: TEAM_MERGES.get(t, t)
    pairs = []
    finals = matches[matches["stage"].str.strip().str.lower() == "final"]
    for f in finals.itertuples():
        yi = years.index(f.tournament_year)
        if yi + 1 >= len(years):
            continue
        ny = years[yi + 1]
        for team in (merged(f.home_team), merged(f.away_team)):
            nxt = matches[
                (matches.tournament_year == ny)
                & (
                    (matches.home_team.map(merged) == team)
                    | (matches.away_team.map(merged) == team)
                )
            ].sort_values("match_date")
            if len(nxt):
                pairs.append((f.Index, nxt.index[0], f.tournament_year, team))
    return pairs


# ----------------------------------------------------------------------
# 4. Statistics on one full (654-match) assignment
# ----------------------------------------------------------------------
def compute_stats(ref_vec, gp, succ, arg_id):
    """ref_vec: global referee id per match (aligned with matches rows)."""
    t1, t2, yb = gp["g_team1"], gp["g_team2"], gp["g_yearbit"]
    cnt = {}
    msk = {}
    for i in range(gp["n_total"]):
        r = ref_vec[i]
        for tm in (t1[i], t2[i]):
            k = (r, tm)
            cnt[k] = cnt.get(k, 0) + 1
            msk[k] = msk.get(k, 0) | yb[i]

    s1 = max(cnt.values())
    s2 = 0
    for k, c in cnt.items():
        if c > s2 and bin(msk[k]).count("1") >= 3:
            s2 = c
    arg_max = max((c for (r, tm), c in cnt.items() if tm == arg_id), default=0)
    s3 = 1 if arg_max >= 4 else 0
    s4 = sum(1 for fi, oi, _, _ in succ if ref_vec[fi] == ref_vec[oi])
    span3_exists = 1 if s2 >= 1 else 0
    return s1, s2, s3, s4, span3_exists, arg_max


# ----------------------------------------------------------------------
# 5. Null model samplers
# ----------------------------------------------------------------------
def sample_model_A(t, rng):
    """One workload-preserving permutation for one tournament.

    Sequential random assignment over a shuffled match order; each referee
    keeps his exact observed match count; strict country neutrality.
    Same-confederation candidates are chosen with relative odds
    t.weights[stage_class] vs 1 for confederation-neutral candidates
    (weights are calibrated so the mean simulated number of same-confed
    assignments matches the observed number). Restarts on the rare dead
    ends. Returns (local ref index per match, n_restarts, conflicts_by_stratum).
    """
    n = t.n_matches
    for attempt in range(MAX_RESTARTS):
        order = rng.permutation(n)
        counts = t.counts.copy()
        assign = np.empty(n, dtype=np.int64)
        nconf = [0, 0]
        ok = True
        for mi in order:
            mask = t.elig_country[mi] & (counts > 0)
            conf_row = t.confed_conflict[mi]
            cand_c = np.flatnonzero(mask & conf_row)
            cand_n = np.flatnonzero(mask & ~conf_row)
            st = t.stratum[mi]
            w_total = cand_n.size + t.weights[st] * cand_c.size
            if w_total <= 0:
                ok = False
                break
            # two-group weighted pick: neutral candidates weight 1,
            # conflicted candidates weight w
            if rng.random() * w_total < cand_n.size:
                r = cand_n[rng.integers(cand_n.size)]
            else:
                r = cand_c[rng.integers(cand_c.size)]
                nconf[st] += 1
            assign[mi] = r
            counts[r] -= 1
        if ok:
            return assign, attempt, nconf
    raise RuntimeError(f"model A: no valid permutation for {t.year} "
                       f"after {MAX_RESTARTS} restarts")


def calibrate_weights(tournaments, rng, n_pilot=300, n_iter=8):
    """Fit per-tournament, per-stage-class conflict odds factors so that the
    simulated mean same-confed assignment count matches the observed count."""
    log = []
    for t in tournaments:
        for it in range(n_iter):
            tot = np.zeros(2)
            for _ in range(n_pilot):
                _, _, nconf = sample_model_A(t, rng)
                tot += nconf
            mean = tot / n_pilot
            done = True
            for st in (0, 1):
                obs = t.obs_conflicts[st]
                ratio = (obs + 0.5) / (mean[st] + 0.5)
                if abs(np.log(ratio)) > 0.02:  # within ~2% is good enough
                    done = False
                t.weights[st] = float(np.clip(t.weights[st] * ratio, 1e-3, 1e3))
            if done:
                break
        log.append((t.year, t.weights[0], t.weights[1],
                    t.obs_conflicts[0], round(mean[0], 2),
                    t.obs_conflicts[1], round(mean[1], 2)))
    return pd.DataFrame(
        log, columns=["year", "w_group", "w_knockout",
                      "obs_group", "sim_group", "obs_knockout", "sim_knockout"]
    )


def run_model_A(tournaments, gp, succ, arg_id, n_sims, rng):
    stats = np.empty((n_sims, 6), dtype=np.int64)
    restarts = 0
    conflict_sums = {t.year: np.zeros(2) for t in tournaments}
    ref_vec = np.empty(gp["n_total"], dtype=np.int64)
    for s in range(n_sims):
        for t in tournaments:
            local, att, nconf = sample_model_A(t, rng)
            restarts += att
            conflict_sums[t.year] += nconf
            ref_vec[t.global_idx] = t.used_refs[local]
        stats[s] = compute_stats(ref_vec, gp, succ, arg_id)
    conflict_means = {y: v / n_sims for y, v in conflict_sums.items()}
    return stats, restarts, conflict_means


def run_model_B(tournaments, gp, succ, arg_id, n_sims, rng):
    stats = np.empty((n_sims, 6), dtype=np.int64)
    # Pre-draw uniform picks per match column for all sims at once.
    draws = np.empty((n_sims, gp["n_total"]), dtype=np.int64)
    for t in tournaments:
        for j, gi in enumerate(t.global_idx):
            elig = t.pool_elig_lists[j]
            draws[:, gi] = elig[rng.integers(elig.size, size=n_sims)]
    for s in range(n_sims):
        stats[s] = compute_stats(draws[s], gp, succ, arg_id)
    return stats


# ----------------------------------------------------------------------
# 6. p-values with CIs
# ----------------------------------------------------------------------
def mc_pvalue(sim_values, observed):
    n = len(sim_values)
    k = int(np.sum(sim_values >= observed))
    p = (k + 1) / (n + 1)  # add-one Monte Carlo correction
    ci = binomtest(k, n).proportion_ci(confidence_level=0.95, method="exact")
    return k, p, ci.low, ci.high


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    t_start = time.time()
    rng = np.random.default_rng(SEED)

    print("Loading data ...")
    matches, refpool, team_conf = load_data()
    n_matches = len(matches)
    print(f"  {n_matches} played matches, "
          f"{matches['tournament_year'].nunique()} tournaments")

    print("Verifying neutrality constraints against the real data ...")
    country_viol, budget, totals, confed_examples = verify_neutrality(
        matches, refpool, team_conf
    )
    print(f"  country-level violations: {len(country_viol)} / {n_matches}")
    print("  same-confederation assignments (observed 'violations' of "
          "confederation neutrality):")
    tbl = pd.DataFrame({"conflicts": budget, "matches": totals})
    print(tbl.to_string())

    tournaments, gp = build_structures(matches, refpool, team_conf)
    attach_conflict_targets(tournaments, budget)
    succ = succession_pairs(matches)
    arg_id = gp["team_ids"]["Argentina"]
    print(f"  finalist->next-opener succession slots: {len(succ)}")

    obs = compute_stats(gp["g_actual_ref"], gp, succ, arg_id)
    obs_s1, obs_s2, obs_s3, obs_s4, obs_span3, obs_argmax = obs
    print(f"\nObserved: max pair={obs_s1}, max pair(span>=3)={obs_s2}, "
          f"any ref >=4 ARG matches={obs_s3} (max ARG count={obs_argmax}), "
          f"final->opener coincidences={obs_s4}")

    print("\nCalibrating confederation-conflict odds factors (model A) ...")
    tC = time.time()
    calib = calibrate_weights(tournaments, rng)
    print(calib.to_string(index=False))
    print(f"  calibrated in {time.time() - tC:.0f}s")

    print(f"\nRunning null model A ({N_SIMS_A} sims) ...")
    tA = time.time()
    stats_A, restarts_A, conflict_means = run_model_A(
        tournaments, gp, succ, arg_id, N_SIMS_A, rng
    )
    dur_A = time.time() - tA
    print(f"  done in {dur_A:.0f}s ({restarts_A} restarts total)")
    # final achieved conflict means (for the report's calibration table)
    calib["sim_group"] = [round(conflict_means[y][0], 2) for y in calib["year"]]
    calib["sim_knockout"] = [round(conflict_means[y][1], 2) for y in calib["year"]]

    print(f"Running null model B ({N_SIMS_B} sims) ...")
    tB = time.time()
    stats_B = run_model_B(tournaments, gp, succ, arg_id, N_SIMS_B, rng)
    dur_B = time.time() - tB
    print(f"  done in {dur_B:.0f}s")

    # ------------------------------------------------------------------
    # Summarize
    # ------------------------------------------------------------------
    stat_defs = [
        ("i_max_pair", "Max referee-team pair count, all tournaments jointly", 0, obs_s1),
        ("ii_max_pair_span3", "Max pair count among pairs spanning >=3 tournaments", 1, obs_s2),
        ("iii_ref_4plus_argentina", "Some referee takes >=4 Argentina matches (indicator)", 2, obs_s3),
        ("iv_final_then_opener", "Same ref: a team's final + that team's next-WC opener (count)", 3, obs_s4),
        ("aux_any_pair_span3", "Any referee-team pair spans >=3 tournaments (indicator)", 4, obs_span3),
        ("aux_max_argentina_count", "Max Argentina-match count by one referee", 5, obs_argmax),
    ]
    rows = []
    for model_name, stats, n_sims in (("A", stats_A, N_SIMS_A), ("B", stats_B, N_SIMS_B)):
        for stat_id, desc, col, observed in stat_defs:
            v = stats[:, col]
            k, p, lo, hi = mc_pvalue(v, observed)
            rows.append({
                "statistic": stat_id,
                "model": model_name,
                "description": desc,
                "observed": observed,
                "null_mean": round(float(v.mean()), 4),
                "null_sd": round(float(v.std()), 4),
                "null_p95": float(np.percentile(v, 95)),
                "null_max": int(v.max()),
                "n_sims_geq_observed": k,
                "p_value_mc": round(p, 6),
                "p_ci95_low": round(lo, 6),
                "p_ci95_high": round(hi, 6),
                "n_sims": n_sims,
                "seed": SEED,
            })
    results = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\nWrote {OUT_CSV}")

    total_dur = time.time() - t_start
    write_report(results, matches, refpool, budget, totals, country_viol,
                 confed_examples, succ, obs, dur_A, dur_B, restarts_A,
                 total_dur, calib)
    print(f"Wrote {OUT_MD}")
    print(f"Total runtime: {total_dur:.0f}s")

    # Console summary of the headline numbers
    print("\n=== HEADLINE RESULTS ===")
    for stat_id in ("i_max_pair", "ii_max_pair_span3",
                    "iii_ref_4plus_argentina", "iv_final_then_opener"):
        for model in ("A", "B"):
            r = results[(results.statistic == stat_id) & (results.model == model)].iloc[0]
            print(f"{stat_id:26s} model {model}: observed={r.observed}, "
                  f"null mean={r.null_mean}, p={r.p_value_mc:.4f} "
                  f"[{r.p_ci95_low:.4f}, {r.p_ci95_high:.4f}]")


# ----------------------------------------------------------------------
# Report writer
# ----------------------------------------------------------------------
def write_report(results, matches, refpool, budget, totals, country_viol,
                 confed_examples, succ, obs, dur_A, dur_B, restarts_A,
                 total_dur, calib):
    obs_s1, obs_s2, obs_s3, obs_s4, obs_span3, obs_argmax = obs
    n_matches = len(matches)

    def res(stat_id, model):
        return results[(results.statistic == stat_id) & (results.model == model)].iloc[0]

    def fmt_row(stat_id, label):
        a, b = res(stat_id, "A"), res(stat_id, "B")
        return (f"| {label} | {a.observed} | {a.null_mean} | "
                f"{a.p_value_mc:.4f} [{a.p_ci95_low:.4f}, {a.p_ci95_high:.4f}] | "
                f"{b.null_mean} | {b.p_value_mc:.4f} [{b.p_ci95_low:.4f}, {b.p_ci95_high:.4f}] |")

    budget_tbl = "\n".join(
        f"| {yr} | {int(budget.get((yr, 'group'), 0))}/{int(totals.get((yr, 'group'), 0))} "
        f"| {int(budget.get((yr, 'knockout'), 0))}/{int(totals.get((yr, 'knockout'), 0))} |"
        for yr in sorted(matches["tournament_year"].unique())
    )

    calib_tbl = "\n".join(
        f"| {int(r.year)} | {r.w_group:.3f} | {int(r.obs_group)} | {r.sim_group} "
        f"| {r.w_knockout:.3f} | {int(r.obs_knockout)} | {r.sim_knockout} |"
        for r in calib.itertuples()
    )

    ex = confed_examples[confed_examples.tournament_year >= 2022].tail(6)
    ex_lines = "\n".join(
        f"- {r.tournament_year} {r.stage}: {r.referee} ({r.referee_country}) took "
        f"{r.home_team} v {r.away_team}"
        for r in ex.itertuples()
    )

    pool_sizes = refpool.groupby("tournament_year").size()
    pool_line = ", ".join(f"{y}: {n}" for y, n in pool_sizes.items())

    md = f"""# Referee-assignment randomness test (Marciniak-Argentina pairing)

*Generated by `analysis/assignment_simulation.py` (seed {SEED}); data cut-off
2026-07-16 (2026 tournament complete through the semi-finals; the third-place
match and the final, Spain v Argentina on 2026-07-19, are unplayed and excluded).*

## Question

Szymon Marciniak (Poland) refereed **Argentina 4 times** across the 2018, 2022
and 2026 World Cups - including the **2022 final** and **Argentina's 2026
opening match**. Across all {n_matches} played matches of the 1990-2026 World Cups
this is the **only referee-team pairing with 4 matches**, and the only pairing
of any size spanning 3 or more tournaments. How improbable is that if FIFA's
referee-assignment process were (plausibly constrained) random? This tests the
**assignment process only** - it says nothing about in-match behaviour.

## Data

- `data/referee-teams/match_officials_1990_2010.csv` + `match_officials_2014_2026.csv`:
  actual referee for all {n_matches} played matches (52+52+64x7+102).
- `data/referee-teams/tournament_officials_*.csv`: appointed officials per
  tournament. Serving referee pools (role_pool = referee, excluding
  assistant/support pools and officials withdrawn or removed before the
  tournament) - {pool_line}.
- Team confederations from `data/worldcup-1930-2022/teams.csv`, plus a manual
  map in the script for 2026 debutants (Jordan, Uzbekistan, Cape Verde,
  DR Congo, Curacao) and spelling variants (China PR).

Data-cleaning decisions (all in the script):

- Withdrawn officials excluded from pools: De Santis & Prendergast (2006,
  flagged in role_pool), Amarilla & Benouza (2010, flagged), Al-Mirdasi (2018)
  and Artan (2026) per `NOTES_2014_2026.md`. Al-Jassim (2018) kept - he was
  VAR-appointed but did referee on-field matches.
- Name aliases when joining match rows to pools: "Filippi Cavani" =
  Ernesto Filippi (1994), "Marco Antonio Rodriguez" = Marco Rodriguez (2014).
  One 2026 row carried a wikitext footnote inside the referee field
  (Ivory Coast v Ecuador; referee is Francois Letexier) - cleaned on load.
- Referees are matched across tournaments by accent-stripped name; Alireza
  Faghani correctly appears as Iran (2014-22) and Australia (2026).
- West Germany is merged with Germany for team-identity statistics (raw names
  are kept for neutrality checks).

## Neutrality: what FIFA actually respects (verification)

- **Country neutrality: {len(country_viol)} violations in {n_matches} matches.** No referee
  ever took a match involving his own country's team. -> Enforced strictly in
  both null models.
- **Confederation neutrality is NOT a real constraint.** Same-confederation
  assignments (referee shares a confederation with at least one team) are
  routine, especially UEFA referees on matches involving UEFA teams:

| Tournament | group: conflicts/matches | knockout: conflicts/matches |
|---|---|---|
{budget_tbl}

  Recent examples:
{ex_lines}

  Notably, Marciniak (UEFA) taking the 2022 final *was itself* a
  same-confederation assignment (France is UEFA). Because the constraint is
  real but soft (FIFA clearly avoids some same-confed pairings - e.g. only
  5/48 group matches in 2010 - yet allows many), model A enforces it **only as
  strongly as reality does**: same-confederation candidates are re-weighted
  by an odds factor per tournament and stage class, calibrated so the
  *simulated mean* number of same-confederation assignments matches the
  observed number. (A hard cap at the observed count was tried first and is
  infeasible to sample - e.g. 1998, with 15 UEFA teams and a UEFA-heavy
  referee pool, structurally dead-ends a sequential sampler.)

  Calibration result (observed vs simulated mean same-confed assignments;
  w = odds factor applied to conflicted candidates, w<1 means FIFA avoids
  the pairing relative to random, w>1 means the opposite):

| Tournament | w group | obs group | sim group | w knockout | obs knockout | sim knockout |
|---|---|---|---|---|---|---|
{calib_tbl}

## Null models

**Model A (primary - workload-preserving permutation).** Within each
tournament, each referee keeps *exactly* his observed number of matches, and
matches are re-dealt at random among the referees who actually officiated,
subject to strict country neutrality and the calibrated soft confederation
constraint above. Sampled by random sequential assignment over a shuffled
match order with restarts on dead ends ({restarts_A} restarts across
{int(res('i_max_pair','A').n_sims)} x 10 tournament draws; sequential sampling is not exactly uniform
over the constrained assignment set, an accepted approximation). This holds
fixed *how much* each referee worked (talent, trust, fitness, rotation
policy) and randomizes only *which* matches he got.

**Model B (sensitivity - uniform pool draws).** Each match's referee is drawn
uniformly from the tournament's serving referee pool (country-neutral members
only), ignoring realized match counts and the confederation weighting. This is the
"pure lottery" benchmark; it overstates randomness (in reality workloads are
very unequal), so it brackets model A from the loose side.

**Explicitly NOT modeled** (assumption, stated honestly): FIFA assigns finals
and big knockout matches to its most-trusted referees, and openers are also
showcase appointments. If a team keeps reaching finals (Argentina reached 3 of
the last 4) while a referee is the reigning "best in the world" (Marciniak
2022-2026), merit-based assignment mechanically raises the chance of repeat
pairings. Neither null model encodes this best-referee-to-biggest-match
coupling; model A only preserves total workloads. p-values below are therefore
for the hypothesis "assignment is random given workloads and neutrality", not
"FIFA did something wrong".

## Statistics (computed jointly across all 10 tournaments per simulation)

1. **(i) Max referee-team pair count** - observed **{obs_s1}** (Marciniak-Argentina).
2. **(ii) Max pair count among pairs spanning >=3 tournaments** - observed **{obs_s2}**
   (Marciniak-Argentina is the only such pair; statistic is 0 when no pair spans 3).
3. **(iii) Some referee takes >=4 Argentina matches** - observed **yes** ({obs_argmax}).
4. **(iv) Same referee gets a team's final and that team's next-WC opener** -
   observed **{obs_s4}** of {len(succ)} finalist slots (Marciniak: 2022 final -> ARG 2026 opener).

## Results

| Statistic | Observed | Model A null mean | Model A p [95% CI] | Model B null mean | Model B p [95% CI] |
|---|---|---|---|---|---|
{fmt_row('i_max_pair', '(i) max pair count')}
{fmt_row('ii_max_pair_span3', '(ii) max pair count, span>=3')}
{fmt_row('iii_ref_4plus_argentina', '(iii) any ref >=4 ARG matches')}
{fmt_row('iv_final_then_opener', '(iv) final -> next-opener, same ref')}
{fmt_row('aux_any_pair_span3', 'aux: any pair spans >=3 tournaments')}
{fmt_row('aux_max_argentina_count', 'aux: max ARG matches by one ref')}

p-values are Monte Carlo P(sim >= observed) with add-one correction;
brackets are exact Clopper-Pearson 95% CIs on the raw exceedance proportion.
Full numbers in `data/processed/assignment_sim_results.csv`.

## Interpretation (honest)

**Headline: the Marciniak-Argentina pattern is mildly unusual but nowhere
near a smoking gun.** Depending on the formulation, it is roughly a
1-in-{int(round(1/max(res('ii_max_pair_span3','A').p_value_mc, 1e-9)))} to
1-in-{int(round(1/max(res('iii_ref_4plus_argentina','A').p_value_mc, 1e-9)))} outcome under the
workload-preserving null - and the most honest formulation is not unusual at all.

- **(i)** p = {res('i_max_pair','A').p_value_mc:.2f} (A) / {res('i_max_pair','B').p_value_mc:.2f} (B).
  That *some* referee-team pair somewhere in 1990-2026 reaches 4 matches is
  close to expected (null mean of the max is {res('i_max_pair','A').null_mean:.1f}). This statistic scans
  every referee-team pair over 37 years, so it fully pays the
  multiple-comparisons penalty - and at that price, a 4 is unremarkable.
  Busy referees + deep-running teams produce 3-4-match pairs inside a single
  World Cup quite easily (Rizzoli-Argentina reached 3 in 2014 alone).
- **(ii)** p = {res('ii_max_pair_span3','A').p_value_mc:.3f} (A) / {res('ii_max_pair_span3','B').p_value_mc:.3f} (B).
  The genuinely uncommon part is the *cross-tournament* structure: a 4-match
  pair spread over >= 3 different World Cups. Note the aux row: some pair
  spanning 3 tournaments exists in {res('aux_any_pair_span3','A').null_mean:.0%} of model A simulations,
  so spanning per se is not rare - it is the combination of span and count.
- **(iii)** p = {res('iii_ref_4plus_argentina','A').p_value_mc:.3f} (A) / {res('iii_ref_4plus_argentina','B').p_value_mc:.3f} (B).
  The Argentina-specific version is the rarest formulation, but it is
  **post hoc** - Argentina was singled out *because* that is where the
  anomaly is. Its p-value is descriptive, not confirmatory; (i) and (ii) are
  the fair headline numbers.
- **(iv)** p = {res('iv_final_then_opener','A').p_value_mc:.3f} (A) / {res('iv_final_then_opener','B').p_value_mc:.3f} (B).
  "Same referee takes a team's final and that team's next-WC opener" - a
  striking story, but with 18 finalist slots over nine successions it is
  roughly a 1-in-{int(round(1/max(res('iv_final_then_opener','A').p_value_mc, 1e-9)))} event under model A.
- **These four statistics are not independent evidence** - all are driven by
  the same four Marciniak matches. The strongest defensible summary is the
  (ii)/(iii) level: an event of roughly the 1-in-10 order, i.e. p > 0.05 in
  the fair formulations and p < 0.05 only in the post-hoc Argentina-specific
  one under model B. This is *not* statistical evidence that FIFA's
  assignment process treated Argentina specially.
- **What would explain even the mild excess without any impropriety:** FIFA
  demonstrably gives marquee matches to its top-ranked referees, and openers
  and finals are marquee appointments. Argentina played an unusually high
  share of marquee matches (two finals and a champions' opener in the window)
  while Marciniak was the reigning top referee (2022-2026). Neither null
  model encodes this best-referee-to-biggest-match coupling - model A only
  preserves total workloads - so even the mild tail-ness observed here is
  compatible with benign merit-based assignment.
- Confederation neutrality is empirically soft (see verification table), and
  country neutrality is absolute (0/{len(matches)}). Any claim of the form "a European
  referee should not keep getting Argentina" has no basis in FIFA's actual
  constraint set - Marciniak taking the 2022 final was itself a
  same-confederation (UEFA-France) assignment.
- **Residual calibration gap**: in the group stages of 2010/2022/2026 FIFA
  avoided same-confed assignments almost maximally; even with the conflict
  odds at the floor, the sequential sampler is forced into ~2-3 more
  conflicts than observed (see calibration table). The effect on the
  statistics is second-order (it marginally diverts UEFA referees away from
  non-UEFA teams like Argentina, i.e. very slightly anti-conservative for
  statistic (iii)).
- 2026 is included only through the semi-finals (data cut-off 2026-07-16).
  Argentina are in the 2026 final; if Marciniak were appointed to it, the
  pairing would grow to 5 and this analysis should be re-run on the completed
  data - the conclusions could change materially.

## Reproducibility

- Script: `analysis/assignment_simulation.py`; seed = {SEED};
  model A sims = {int(res('i_max_pair','A').n_sims)}, model B sims = {int(res('i_max_pair','B').n_sims)}.
- Runtime: model A {dur_A:.0f}s, model B {dur_B:.0f}s, total {total_dur:.0f}s.
- Outputs: `data/processed/assignment_sim_results.csv`, this file.
"""
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(md, encoding="utf-8")


if __name__ == "__main__":
    main()
