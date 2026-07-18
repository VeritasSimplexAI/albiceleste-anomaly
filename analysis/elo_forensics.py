"""Elo forensics for the Argentina World Cup project.

STEP 3 — Elo-adjusted overperformance per referee (1990-2026)
  * Expected score per match from pre-tournament Elo (data/elo/elo_pre_tournament.csv),
    with +100 Elo for host-nation teams (standard eloratings.net home-advantage convention;
    all other venues treated as neutral).
  * Actual score, primary convention: result at END OF PLAY (after extra time) —
    win=1, draw=0.5, loss=0; penalty shootouts count as 0.5 draws (Elo methodology).
    Secondary sensitivity: shootout winner credited with a full win (=1).
  * Per referee: Argentina's total (actual - expected) in his matches = "Elo residual".
  * Era aggregates (1990-2018 / 2022 / 2026) for Argentina and other elite teams,
    plus champion title-run residuals for context.
  * Inference: stratified permutation test. Within each tournament x stage stratum the
    referee assignment is permuted (respecting the same-country constraint: a referee is
    never assigned a match involving his own country), each referee's Argentina residual
    is rebuilt, and Monte Carlo p-values are computed. N_PERM iterations, fixed seed.

STEP 4 — hierarchical referee x team model of yellow cards (1990-2022)
  * Outcome: yellows received per team-match (data/processed/match_team_level.csv).
    2026 is excluded: per-match card data for non-Argentina 2026 matches does not exist.
  * Fixed effects: standardized team Elo, standardized opponent Elo, knockout flag,
    tournament year (categorical).
  * Random effects: referee intercept, team intercept, referee x team interaction.
    (The task specified referee + referee x team; a team random intercept is added so
    that a team's general card-proneness is not misattributed to its referee pairs.
    The 2-component spec model is also fitted and reported as a sensitivity.)
  * Implementation: statsmodels PoissonBayesMixedGLM fitted by variational Bayes
    (fit_vb). If the fit fails, a two-stage empirical-Bayes (gamma-Poisson) fallback
    is used and documented in the output.

Outputs:
  data/processed/elo_residuals_by_referee.csv
  data/processed/hierarchical_pairs.csv
  (console report used to build analysis/subreports/ELO_FORENSICS.md)

Run:  python analysis/elo_forensics.py
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
N_PERM = 10_000
SEED = 20260717

# Team-name aliases: officials-file spellings -> project (match-file) spellings.
# Same dict as analysis/referee_comparison.py (654/654 join verified there).
ALIAS = {"Ireland": "Republic of Ireland", "USA": "United States", "Korea Republic": "South Korea",
         "IR Iran": "Iran", "Türkiye": "Turkey", "Czechia": "Czech Republic", "China PR": "China",
         "Côte d'Ivoire": "Ivory Coast", "FR Yugoslavia": "Yugoslavia", "Curacao": "Curaçao"}

# Host nations by tournament (+100 Elo, standard convention). 2002 and 2026 co-hosts.
HOSTS = {1990: {"Italy"}, 1994: {"United States"}, 1998: {"France"},
         2002: {"South Korea", "Japan"}, 2006: {"Germany"}, 2010: {"South Africa"},
         2014: {"Brazil"}, 2018: {"Russia"}, 2022: {"Qatar"},
         2026: {"United States", "Canada", "Mexico"}}

ELITE = ["Argentina", "Brazil", "France", "Germany", "Spain", "England"]
# Champions in scope (2026 pending: Argentina are finalists, final 2026-07-19 not in data).
CHAMPIONS = [(1990, "West Germany"), (1994, "Brazil"), (1998, "France"), (2002, "Brazil"),
             (2006, "Italy"), (2010, "Spain"), (2014, "Germany"), (2018, "France"),
             (2022, "Argentina"), (2026, "Argentina (finalist, tournament ongoing)")]


def norm(s):
    return ALIAS.get(str(s).strip(), str(s).strip())


def mkey(date, a, b):
    return f"{date}|" + "|".join(sorted([norm(a), norm(b)]))


def canon(team):
    """Canonical national identity for era aggregation / same-country checks."""
    return "Germany" if team == "West Germany" else team


def stage_type(s):
    s = str(s).strip()
    if s.startswith("Group"):
        return "Group"
    if s.startswith("Third"):
        return "Third place"
    return s  # Round of 32 / Round of 16 / Quarter-finals / Semi-finals / Final


# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------

def load_elo():
    elo = pd.read_csv(ROOT / "data" / "elo" / "elo_pre_tournament.csv")
    return {(int(y), t): float(e) for y, t, e in zip(elo.tournament_year, elo.team, elo.elo)}


def load_matches():
    """One row per match 1990-2026: teams (project spellings), end-of-play scores,
    shootout info, referee, stage. actual_h = home-side Elo score, both conventions."""
    m = pd.read_csv(ROOT / "data" / "worldcup-1930-2022" / "matches.csv")
    m["year"] = m.tournament_id.str.slice(3).astype(int)
    m = m[m.year.isin([1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022])].copy()
    rows = []
    for r in m.itertuples():
        rows.append(dict(year=r.year, date=r.match_date, team_h=r.home_team_name,
                         team_a=r.away_team_name, score_h=r.home_team_score,
                         score_a=r.away_team_score, shootout=bool(r.penalty_shootout),
                         pen_h=r.home_team_score_penalties, pen_a=r.away_team_score_penalties))
    m26 = pd.read_csv(ROOT / "data" / "worldcup-2026" / "matches_2026.csv", encoding="utf-8-sig")
    for r in m26.itertuples():
        po = bool(r.penalty_shootout == "yes")
        ph = pa = 0
        if po:
            ph, pa = map(int, str(r.score_penalties).split("-"))
        rows.append(dict(year=2026, date=r.match_date, team_h=r.home_team, team_a=r.away_team,
                         score_h=r.home_score, score_a=r.away_score, shootout=po,
                         pen_h=ph, pen_a=pa))
    df = pd.DataFrame(rows)
    df["mkey"] = [mkey(d, a, b) for d, a, b in zip(df.date, df.team_h, df.team_a)]

    mo = pd.concat([
        pd.read_csv(ROOT / "data" / "referee-teams" / "match_officials_1990_2010.csv", encoding="utf-8-sig"),
        pd.read_csv(ROOT / "data" / "referee-teams" / "match_officials_2014_2026.csv", encoding="utf-8-sig"),
    ], ignore_index=True)
    mo["mkey"] = [mkey(d, a, b) for d, a, b in zip(mo.match_date, mo.home_team, mo.away_team)]
    mo["referee"] = mo.referee.str.strip()
    df = df.merge(mo[["mkey", "referee", "referee_country", "stage"]], on="mkey", how="left")
    assert df.referee.notna().all(), "referee join incomplete"
    assert len(df) == 654, f"expected 654 matches, got {len(df)}"
    df["stage_type"] = df.stage.map(stage_type)

    # Actual home-side scores.
    def actual(sh, sa, po, ph, pa):
        if po:  # level at end of play by construction
            return 0.5, (1.0 if ph > pa else 0.0)
        a = 1.0 if sh > sa else (0.5 if sh == sa else 0.0)
        return a, a
    df[["actual_h", "actual_h_sw"]] = [actual(*t) for t in
                                       zip(df.score_h, df.score_a, df.shootout, df.pen_h, df.pen_a)]

    # Expected home-side score from pre-tournament Elo (+100 for host nations).
    ELO = load_elo()
    eh = [ELO[(y, t)] + (100 if t in HOSTS[y] else 0) for y, t in zip(df.year, df.team_h)]
    ea = [ELO[(y, t)] + (100 if t in HOSTS[y] else 0) for y, t in zip(df.year, df.team_a)]
    df["elo_h_adj"], df["elo_a_adj"] = eh, ea
    df["expected_h"] = 1.0 / (1.0 + 10 ** (-(df.elo_h_adj - df.elo_a_adj) / 400.0))
    return df


def team_view(df):
    """Two rows per match: residual = actual - expected from each team's perspective."""
    h = pd.DataFrame(dict(year=df.year, date=df.date, team=df.team_h, opponent=df.team_a,
                          referee=df.referee, stage_type=df.stage_type,
                          resid=df.actual_h - df.expected_h,
                          resid_sw=df.actual_h_sw - df.expected_h,
                          actual=df.actual_h, expected=df.expected_h))
    a = pd.DataFrame(dict(year=df.year, date=df.date, team=df.team_a, opponent=df.team_h,
                          referee=df.referee, stage_type=df.stage_type,
                          resid=(1 - df.actual_h) - (1 - df.expected_h),
                          resid_sw=(1 - df.actual_h_sw) - (1 - df.expected_h),
                          actual=1 - df.actual_h, expected=1 - df.expected_h))
    return pd.concat([h, a], ignore_index=True)


# --------------------------------------------------------------------------
# STEP 3a — era / champion residuals
# --------------------------------------------------------------------------

def era_tables(tv):
    tv = tv.copy()
    tv["team_c"] = tv.team.map(canon)
    tv["era"] = np.where(tv.year <= 2018, "1990-2018", tv.year.astype(str))
    rows = []
    for team in ELITE:
        sub = tv[tv.team_c == team]
        for era in ["1990-2018", "2022", "2026"]:
            s = sub[sub.era == era]
            if len(s) == 0:
                rows.append(dict(team=team, era=era, n=0, resid_sum=np.nan,
                                 resid_mean=np.nan, resid_sum_sw=np.nan))
            else:
                rows.append(dict(team=team, era=era, n=len(s), resid_sum=s.resid.sum(),
                                 resid_mean=s.resid.mean(), resid_sum_sw=s.resid_sw.sum()))
    era = pd.DataFrame(rows)

    champ_rows = []
    for year, name in CHAMPIONS:
        tname = name.split(" (")[0]
        s = tv[(tv.year == year) & (tv.team == tname)]
        champ_rows.append(dict(year=year, champion=name, n=len(s), resid_sum=s.resid.sum(),
                               resid_mean=s.resid.mean(), resid_sum_sw=s.resid_sw.sum()))
    champs = pd.DataFrame(champ_rows)

    pt_rows = []
    for team in ELITE:
        sub = tv[tv.team_c == team]
        for year, s in sub.groupby("year"):
            pt_rows.append(dict(team=team, year=year, n=len(s), resid_sum=s.resid.sum(),
                                resid_mean=s.resid.mean()))
    per_tournament = pd.DataFrame(pt_rows)
    return era, champs, per_tournament


# --------------------------------------------------------------------------
# STEP 3b — per-referee residuals + stratified permutation test
# --------------------------------------------------------------------------

def referee_residuals(df):
    """Observed Argentina residual per referee + permutation p-values.

    Null model: within each tournament x stage-type stratum, referee assignments are
    exchangeable, subject to the same-country constraint (a referee never officiates
    his own country). 10,000 stratified permutations, fixed seed.
    """
    is_h = df.team_h == "Argentina"
    is_a = df.team_a == "Argentina"
    df = df.assign(is_arg=is_h | is_a,
                   arg_resid=np.where(is_h, df.actual_h - df.expected_h,
                                      np.where(is_a, (1 - df.actual_h) - (1 - df.expected_h), 0.0)),
                   arg_resid_sw=np.where(is_h, df.actual_h_sw - df.expected_h,
                                         np.where(is_a, (1 - df.actual_h_sw) - (1 - df.expected_h), 0.0)))

    refs, ref_idx = np.unique(df.referee, return_inverse=True)
    nref = len(refs)
    df["ref_code"] = ref_idx

    # Country codes for the same-country constraint ("West Germany" == "Germany").
    cn = lambda x: canon(norm(x)) if pd.notna(x) else "<none>"
    countries = pd.unique(np.concatenate([df.team_h.map(cn), df.team_a.map(cn),
                                          df.referee_country.map(cn)]))
    cmap = {c: i for i, c in enumerate(countries)}
    t1 = df.team_h.map(cn).map(cmap).to_numpy()
    t2 = df.team_a.map(cn).map(cmap).to_numpy()
    ref_cty = np.full(nref, -1, dtype=int)
    for code, cty in zip(df.ref_code, df.referee_country.map(cn)):
        ref_cty[code] = cmap.get(cty, -1)
    obs_conf = int(((ref_cty[df.ref_code] == t1) | (ref_cty[df.ref_code] == t2)).sum())

    # Observed statistics.
    obs = np.zeros(nref)
    np.add.at(obs, df.ref_code.to_numpy(), df.arg_resid.to_numpy())
    obs_sw = np.zeros(nref)
    np.add.at(obs_sw, df.ref_code.to_numpy(), df.arg_resid_sw.to_numpy())
    n_arg = np.zeros(nref, dtype=int)
    np.add.at(n_arg, df.ref_code.to_numpy(), df.is_arg.to_numpy().astype(int))

    # Strata containing at least one Argentina match (others contribute 0 always).
    strata = []
    for (_, _), g in df.groupby(["year", "stage_type"]):
        if not g.is_arg.any():
            continue
        strata.append(dict(codes=g.ref_code.to_numpy(), resid=g.arg_resid.to_numpy(),
                           arg_pos=np.nonzero(g.is_arg.to_numpy())[0],
                           t1=t1[g.index.to_numpy()], t2=t2[g.index.to_numpy()],
                           n=len(g)))

    rng = np.random.default_rng(SEED)
    Tmat = np.zeros((N_PERM, nref))
    unresolved = 0
    t0 = time.time()
    for it in range(N_PERM):
        T = Tmat[it]
        for st in strata:
            n = st["n"]
            perm = rng.permutation(n)
            codes = st["codes"][perm].copy()
            # Repair same-country conflicts by local swaps.
            for _rep in range(100):
                bad = np.nonzero((ref_cty[codes] == st["t1"]) | (ref_cty[codes] == st["t2"]))[0]
                if bad.size == 0:
                    break
                fixed_any = False
                for k in bad:
                    for _try in range(20):
                        m = int(rng.integers(n))
                        ck, cm = codes[k], codes[m]
                        ok_k = ref_cty[cm] != st["t1"][k] and ref_cty[cm] != st["t2"][k]
                        ok_m = ref_cty[ck] != st["t1"][m] and ref_cty[ck] != st["t2"][m]
                        if ok_k and ok_m:
                            codes[k], codes[m] = cm, ck
                            fixed_any = True
                            break
                if not fixed_any:
                    unresolved += 1
                    break
            ap = st["arg_pos"]
            np.add.at(T, codes[ap], st["resid"][ap])
    elapsed = time.time() - t0

    null_mean = Tmat.mean(axis=0)
    null_sd = Tmat.std(axis=0)
    # One-sided (directional, favoritism = positive residual): P(T_perm >= T_obs).
    p_pos = (1 + (Tmat >= obs - 1e-12).sum(axis=0)) / (N_PERM + 1)
    # Two-sided, centered on the null mean (the null is not centered at 0 because
    # single-match strata — every Final — are pinned to their actual referee).
    p_two = (1 + (np.abs(Tmat - null_mean) >= np.abs(obs - null_mean) - 1e-12).sum(axis=0)) \
        / (N_PERM + 1)

    # Match detail strings for referees with Argentina matches.
    arg_matches = df[df.is_arg].copy()
    arg_matches["opp"] = np.where(arg_matches.team_h == "Argentina",
                                  arg_matches.team_a, arg_matches.team_h)
    arg_is_home = arg_matches.team_h == "Argentina"
    arg_matches["arg_actual"] = np.where(arg_is_home, arg_matches.actual_h, 1 - arg_matches.actual_h)
    arg_matches["arg_expected"] = np.where(arg_is_home, arg_matches.expected_h, 1 - arg_matches.expected_h)
    detail, years = {}, {}
    for code, g in arg_matches.groupby("ref_code"):
        detail[code] = "; ".join(
            f"{r.year} {r.stage_type} vs {r.opp} (act {r.arg_actual:.1f}, exp {r.arg_expected:.2f}, "
            f"resid {r.arg_resid:+.2f}{', pens' if r.shootout else ''})" for r in g.itertuples())
        years[code] = "/".join(map(str, sorted(g.year.unique())))

    ref_country = df.drop_duplicates("ref_code").set_index("ref_code").referee_country
    out = pd.DataFrame(dict(
        referee=refs, referee_country=[ref_country.get(i, "") for i in range(nref)],
        n_argentina_matches=n_arg,
        arg_resid_sum=obs, arg_resid_mean=np.where(n_arg > 0, obs / np.maximum(n_arg, 1), np.nan),
        arg_resid_sum_shootout_as_win=obs_sw,
        perm_null_mean=null_mean, perm_null_sd=null_sd,
        p_perm_onesided_pos=p_pos, p_perm_twosided_centered=p_two,
        years=[years.get(i, "") for i in range(nref)],
        matches_detail=[detail.get(i, "") for i in range(nref)],
    ))
    out = out[out.n_argentina_matches >= 1].sort_values(
        ["n_argentina_matches", "arg_resid_sum"], ascending=[False, False]).reset_index(drop=True)
    meta = dict(n_perm=N_PERM, seed=SEED, elapsed_s=elapsed, strata=len(strata),
                unresolved_repairs=unresolved, observed_conflicts=obs_conf)
    return out, meta, arg_matches


# --------------------------------------------------------------------------
# STEP 4 — hierarchical referee x team model of yellow cards (1990-2022)
# --------------------------------------------------------------------------

def build_card_data():
    ml = pd.read_csv(P / "match_team_level.csv")
    ml = ml[ml.year.isin([1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022])].copy()
    ml["mkey"] = [mkey(d, a, b) for d, a, b in zip(ml.match_date, ml.team_name, ml.opponent_name)]
    mo = pd.concat([
        pd.read_csv(ROOT / "data" / "referee-teams" / "match_officials_1990_2010.csv", encoding="utf-8-sig"),
        pd.read_csv(ROOT / "data" / "referee-teams" / "match_officials_2014_2026.csv", encoding="utf-8-sig"),
    ], ignore_index=True)
    mo["mkey"] = [mkey(d, a, b) for d, a, b in zip(mo.match_date, mo.home_team, mo.away_team)]
    mo["referee"] = mo.referee.str.strip()
    ml = ml.merge(mo[["mkey", "referee"]], on="mkey", how="left")
    assert ml.referee.notna().all()

    ELO = load_elo()
    ml["elo_t"] = [ELO[(y, t)] for y, t in zip(ml.year, ml.team_name)]
    ml["elo_o"] = [ELO[(y, t)] for y, t in zip(ml.year, ml.opponent_name)]
    mu, sd = ml.elo_t.mean(), ml.elo_t.std()  # elo_t and elo_o share the same marginal
    ml["elo_t_std"] = (ml.elo_t - mu) / sd
    ml["elo_o_std"] = (ml.elo_o - mu) / sd
    ml["pair"] = ml.referee + " | " + ml.team_name
    return ml


def sparse_dummies(codes, ncols):
    from scipy import sparse
    n = len(codes)
    return sparse.csr_matrix((np.ones(n), (np.arange(n), codes)), shape=(n, ncols))


def fit_glmm(ml, include_team=True):
    """PoissonBayesMixedGLM fitted by variational Bayes (L-BFGS-B, deterministic
    starting values -> reproducible). Returns dict of results, including each row's
    model-expected yellows EXCLUDING the pair effect (for observed/expected diagnostics).
    """
    import warnings as _w
    from scipy import sparse
    from statsmodels.genmod.bayes_mixed_glm import PoissonBayesMixedGLM

    y = ml.yellows.to_numpy(float)
    years = sorted(ml.year.unique())
    X = [np.ones(len(ml)), ml.elo_t_std.to_numpy(), ml.elo_o_std.to_numpy(),
         ml.knockout_stage.to_numpy(float)]
    fep = ["Intercept", "elo_team_std", "elo_opp_std", "knockout"]
    for yr in years[1:]:
        X.append((ml.year == yr).to_numpy(float))
        fep.append(f"year_{yr}")
    exog = np.column_stack(X)

    ref_codes, refs = pd.factorize(ml.referee)
    team_codes, teams = pd.factorize(ml.team_name)
    pair_codes, pairs = pd.factorize(ml.pair)
    blocks = [sparse_dummies(ref_codes, len(refs))]
    ident_parts = [np.zeros(len(refs), int)]
    vcp_names = ["referee"]
    if include_team:
        blocks.append(sparse_dummies(team_codes, len(teams)))
        ident_parts.append(np.ones(len(teams), int))
        vcp_names.append("team")
    blocks.append(sparse_dummies(pair_codes, len(pairs)))
    ident_parts.append(np.full(len(pairs), len(vcp_names), int))
    vcp_names.append("pair")
    exog_vc = sparse.hstack(blocks).tocsr()
    ident = np.concatenate(ident_parts)

    model = PoissonBayesMixedGLM(y, exog, exog_vc, ident, vcp_p=2.0, fe_p=2.0,
                                 fep_names=fep, vcp_names=vcp_names)
    n_par = model.k_fep + model.k_vcp + model.k_vc
    np.random.seed(SEED)  # fit_vb draws random starting sds unless supplied
    with _w.catch_warnings(record=True) as wlist:
        _w.simplefilter("always")
        r = model.fit_vb(mean=np.zeros(n_par), sd=np.full(n_par, 0.5),
                         fit_method="L-BFGS-B",
                         minim_opts={"maxiter": 5000, "maxfun": 50000})
        conv_warnings = [str(x.message) for x in wlist if "converge" in str(x.message)]
    params = np.asarray(r.params)
    cov = r.cov_params()
    sds = np.sqrt(np.diag(cov)) if np.ndim(cov) == 2 else np.sqrt(np.asarray(cov))
    assert np.isfinite(params).all(), "non-finite VB parameters"
    if conv_warnings:
        raise RuntimeError(f"VB did not converge: {conv_warnings}")
    k_fe, k_vcp = model.k_fep, model.k_vcp
    fe_mean, fe_sd = params[:k_fe], sds[:k_fe]
    vcp_mean, vcp_sd = params[k_fe:k_fe + k_vcp], sds[k_fe:k_fe + k_vcp]
    vc_mean, vc_sd = params[k_fe + k_vcp:], sds[k_fe + k_vcp:]

    off = len(refs) + (len(teams) if include_team else 0)
    pair_mean = vc_mean[off:off + len(pairs)]
    pair_sd = vc_sd[off:off + len(pairs)]
    # Row-level expected yellows from everything EXCEPT the pair effect.
    eta = exog @ fe_mean + vc_mean[:len(refs)][ref_codes]
    if include_team:
        eta = eta + vc_mean[len(refs):off][team_codes]
    return dict(ok=True,
                method=f"PoissonBayesMixedGLM fit_vb (L-BFGS-B, {'3' if include_team else '2'} "
                       f"variance components)",
                fe=dict(zip(fep, zip(fe_mean.round(4), fe_sd.round(4)))),
                vcp=dict(zip(vcp_names, zip(np.exp(vcp_mean).round(4), vcp_mean.round(4),
                                            vcp_sd.round(4)))),
                pairs=list(pairs), pair_mean=pair_mean, pair_sd=pair_sd,
                row_mu_nonpair=np.exp(eta))


def fit_eb_fallback(ml):
    """Two-stage empirical Bayes (gamma-Poisson) — only used if the GLMM fails.
    Stage 1: Poisson GLM with the fixed effects -> per-row expected counts.
    Stage 2: pair multipliers lambda ~ Gamma(a,a); posterior mean (O+a)/(E+a),
    with a chosen by a moment estimate of the between-pair variance (if the
    moment estimate is <= 0, shrinkage is total and all pair effects are ~0)."""
    import statsmodels.api as sm
    years = sorted(ml.year.unique())
    X = [np.ones(len(ml)), ml.elo_t_std, ml.elo_o_std, ml.knockout_stage.astype(float)]
    for yr in years[1:]:
        X.append((ml.year == yr).astype(float))
    exog = np.column_stack(X)
    glm = sm.GLM(ml.yellows.to_numpy(float), exog, family=sm.families.Poisson()).fit()
    mu = np.asarray(glm.fittedvalues)
    g = pd.DataFrame(dict(pair=ml.pair, O=ml.yellows, E=mu)).groupby("pair").sum()
    lam = g.O / g.E
    # moment estimate of Var(lambda): E-weighted, subtracting Poisson noise 1/E
    v = float(np.average((lam - 1) ** 2 - 1 / g.E, weights=g.E ** 2))
    a = 1 / v if v > 1e-6 else 1e6
    post = (g.O + a) / (g.E + a)
    post_sd = np.sqrt((g.O + a)) / (g.E + a)  # gamma posterior sd of lambda
    return dict(ok=True,
                method=f"two-stage empirical Bayes (gamma-Poisson, a={a:.1f}, "
                       f"between-pair var estimate={max(v, 0):.5f})",
                pairs=list(g.index), pair_mean=np.log(post.to_numpy()),
                pair_sd=(post_sd / post).to_numpy(),  # delta-method log-scale sd
                fe=None, vcp=None, row_mu_nonpair=mu)


def hierarchical_report(ml, fit):
    stats = ml.assign(mu_np=fit["row_mu_nonpair"]).groupby("pair").agg(
        n_matches=("yellows", "size"), yellows_total=("yellows", "sum"),
        yellows_mean=("yellows", "mean"), expected_nonpair=("mu_np", "sum"))
    out = pd.DataFrame(dict(pair=fit["pairs"], pair_effect_mean=fit["pair_mean"],
                            pair_effect_sd=fit["pair_sd"]))
    out["referee"] = out.pair.str.split(" | ", regex=False).str[0]
    out["team"] = out.pair.str.split(" | ", regex=False).str[1]
    out = out.join(stats, on="pair")
    out["oe_ratio_raw"] = out.yellows_total / out.expected_nonpair
    out["rate_ratio_shrunk"] = np.exp(out.pair_effect_mean)
    out["z"] = out.pair_effect_mean / out.pair_effect_sd
    out["abs_rank"] = out.pair_effect_mean.abs().rank(ascending=False, method="min").astype(int)
    out["is_argentina"] = out.team == "Argentina"
    return out.sort_values("abs_rank").reset_index(drop=True)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    print("=" * 78)
    print("STEP 3 — Elo-adjusted residuals")
    print("=" * 78)
    df = load_matches()
    print(f"matches: {len(df)} (1990-2022: {(df.year<=2022).sum()}, 2026: {(df.year==2026).sum()})")
    tv = team_view(df)

    era, champs, per_t = era_tables(tv)
    print("\n--- Era residuals (actual - Elo-expected; shootout = 0.5 draw) ---")
    piv = era.pivot(index="team", columns="era", values=["n", "resid_sum", "resid_mean"])
    print(piv.round(3).to_string())
    print("\n--- Champion title-run residuals ---")
    print(champs.round(3).to_string(index=False))
    print("\n--- Per-tournament residuals, elite teams ---")
    print(per_t.pivot(index="team", columns="year", values="resid_sum").round(2).to_string())

    ref_out, meta, arg_matches = referee_residuals(df)
    print(f"\npermutation: {meta['n_perm']} iters, {meta['strata']} Argentina strata, "
          f"{meta['elapsed_s']:.1f}s, unresolved repairs {meta['unresolved_repairs']}, "
          f"observed same-country conflicts {meta['observed_conflicts']}")
    print("\n--- Referees with >=2 Argentina matches ---")
    cols = ["referee", "referee_country", "n_argentina_matches", "arg_resid_sum", "arg_resid_mean",
            "arg_resid_sum_shootout_as_win", "perm_null_mean", "perm_null_sd",
            "p_perm_onesided_pos", "p_perm_twosided_centered", "years"]
    print(ref_out[ref_out.n_argentina_matches >= 2][cols].round(4).to_string(index=False))
    print("\n--- Marciniak match detail ---")
    print(ref_out[ref_out.referee == "Szymon Marciniak"].matches_detail.iloc[0])
    ref_out.round(6).to_csv(P / "elo_residuals_by_referee.csv", index=False, encoding="utf-8")
    print(f"\nwrote {P / 'elo_residuals_by_referee.csv'} ({len(ref_out)} referees with >=1 ARG match)")

    print("\n" + "=" * 78)
    print("STEP 4 — hierarchical referee x team model (yellows, 1990-2022)")
    print("=" * 78)
    ml = build_card_data()
    print(f"team-match rows: {len(ml)}, referees: {ml.referee.nunique()}, "
          f"teams: {ml.team_name.nunique()}, pairs: {ml.pair.nunique()}")
    try:
        fit = fit_glmm(ml, include_team=True)
    except Exception as e:
        print(f"GLMM (3 VC) failed: {e!r} -> empirical-Bayes fallback")
        fit = fit_eb_fallback(ml)
    print(f"method: {fit['method']}")
    if fit["vcp"]:
        print("\nvariance components (posterior): sd, log-sd mean, log-sd sd")
        for k, v in fit["vcp"].items():
            print(f"  {k:8s} sd={v[0]:.4f} (variance={v[0]**2:.4f})  log-sd {v[1]}+/-{v[2]}")
        print("\nfixed effects (posterior mean +/- sd):")
        for k, v in fit["fe"].items():
            print(f"  {k:14s} {v[0]:+.4f} +/- {v[1]:.4f}")

    out = hierarchical_report(ml, fit)
    try:
        fit2 = fit_glmm(ml, include_team=False)
        print("\nsensitivity (spec 2-VC model: referee + pair only):")
        for k, v in fit2["vcp"].items():
            print(f"  {k:8s} sd={v[0]:.4f} (variance={v[0]**2:.4f})")
        out2 = hierarchical_report(ml, fit2)
        out = out.merge(out2[["pair", "pair_effect_mean", "abs_rank"]]
                        .rename(columns={"pair_effect_mean": "pair_effect_mean_2vc",
                                         "abs_rank": "abs_rank_2vc"}), on="pair", how="left")
    except Exception as e:
        print(f"2-VC sensitivity model failed: {e!r}")

    print("\n--- Top 10 most extreme shrunk referee-team pairs ---")
    show = ["pair", "n_matches", "yellows_total", "expected_nonpair", "oe_ratio_raw",
            "pair_effect_mean", "pair_effect_sd", "rate_ratio_shrunk", "z", "abs_rank"]
    print(out.head(10)[show].round(4).to_string(index=False))
    print("\n--- All Argentina pairs, ranked ---")
    print(out[out.is_argentina][show].round(4).to_string(index=False))
    out.round(6).to_csv(P / "hierarchical_pairs.csv", index=False, encoding="utf-8")
    print(f"\nwrote {P / 'hierarchical_pairs.csv'} ({len(out)} pairs)")


if __name__ == "__main__":
    main()
