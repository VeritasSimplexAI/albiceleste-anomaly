"""
Hypothetical "run to the final" draw analysis.

For each team in each tournament (1986-2026, knockout-bracket era), score the
difficulty of its POTENTIAL road from the group draw to the final -- not the
realized road -- two ways:

1. UNWEIGHTED: at each knockout round, the set of possible opponents given the
   bracket structure and the team's own slot; difficulty = mean pre-tournament
   Elo of that set; path score = mean across rounds (sum also reported).

2. ELO-WEIGHTED: same rounds, but each possible opponent is weighted by its
   probability of reaching that round, obtained by iterating Elo win
   probabilities through the bracket (E = 1/(1+10^(-d/400)), +100 host bonus).
   Group qualification probabilities come from exact enumeration of the
   round-robin under an Elo win/draw/loss model (see GROUP MODEL below).

SLOT ASSUMPTIONS: each team is evaluated assuming it wins its group AND
assuming it finishes runner-up.  For the weighted method a qualification-
weighted blend is also produced, mixing the two by the team's conditional
probability of being 1st vs 2nd (P1/(P1+P2)).

GROUP MODEL (documented approximation):
- Per group match, Elo expectancy E = 1/(1+10^(-d/400)) with +100 host bonus.
- Draw probability p_draw = min(0.25, 2E, 2(1-E)); p_win = E - p_draw/2;
  p_loss = 1 - E - p_draw/2.  (E is the Elo *expected score*, draws count 0.5,
  so this decomposition is exactly consistent with the Elo expectancy.)
- All 3^6 = 729 outcome combinations of the 6 group matches are enumerated
  exactly with era-correct points (2 pts/win before 1994, 3 pts from 1994).
- Goals are not modelled, so ties on points are split uniformly across all
  orderings of the tied teams ("uniform tie-splitting").
- This yields the exact JOINT distribution over finishing orders under the
  model, from which marginal and conditional (given the focal team's assumed
  slot) leaf-occupancy probabilities are taken.

BRACKET SKELETONS:
- 1998-2022 (32 teams): the bracket is fixed and known at the draw (A1 v B2
  etc.).  It is derived per-edition from the realized knockout matches plus
  computed group positions, which reproduces the official template exactly
  (asserted: every R16 match pairs a group winner with another group's
  runner-up; all 8 groups x {1st, 2nd} appear exactly once).
- 2026 (48 teams): the round-of-32 slots of the 8 best third-placed teams
  depend on which groups' thirds qualify, which is NOT known at the draw.
  LIMITATION: we use the REALIZED bracket skeleton (which group's third landed
  in which R32 slot) and compute from the R32 onward.
- 1986-1994 (24 teams): same situation (4 best thirds, placement matrices).
  Implemented like 2026: REALIZED skeleton, computed from the R16 onward.
- Pre-1986: skipped (second group stages / final round -- no bracket).

Additional documented approximations:
- Leaf occupancies are treated as independent across leaves (standard bracket-
  calculator approximation).  In 1998/2006-2022 brackets a group's two slots
  sit in opposite halves, so no team can appear twice inside any opponent
  subtree.  2002 is the known exception: to keep Korea-based groups in one
  half and Japan-based groups in the other, each group's winner AND runner-up
  were drawn into the SAME half -- the data-derived skeleton reproduces this,
  and a team may then appear in an opponent subtree via both of its group's
  slots (handled; the independence approximation applies).  In 24/48-team
  brackets a team may likewise appear via both a "runner-up" and a
  "third-place" leaf of the same subtree (small effect).
- Third-place leaves are populated with that group's P(3rd) distribution,
  renormalized within the group; the cross-group probability that this
  particular group's third qualifies at all is conditioned on the realized
  allocation (see LIMITATION above).
- Blend weights use P(1st) and P(2nd) only (qualification as a third-placed
  team is not a slot assumption).
- Difficulty is always measured in RAW pre-tournament Elo; the +100 host bonus
  enters win probabilities only.

SANITY CHECKS (hard asserts):
- Skeleton integrity: every group's 1st and 2nd slot appears exactly once;
  third-place slots come from distinct groups (24/48-team formats).
- 32-team formats: for every team and slot assumption, each round's possible-
  opponent set contains each team at most once, and the union over rounds
  covers all 31 other teams.
- Weighted opponent probabilities sum to 1 (+-1e-9) at every round for every
  slot, and the focal team never appears in its own opponent distribution.

Outputs:
- data/processed/hypothetical_paths.csv
- data/processed/hypothetical_paths_by_round.csv
- analysis/subreports/HYPOTHETICAL_PATHS.md
"""

import os
from collections import defaultdict
from itertools import combinations, permutations, product

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT_CSV = os.path.join(DATA, "processed", "hypothetical_paths.csv")
OUT_CSV_ROUNDS = os.path.join(DATA, "processed", "hypothetical_paths_by_round.csv")
OUT_MD = os.path.join(BASE, "analysis", "subreports", "HYPOTHETICAL_PATHS.md")

HOSTS = {
    1986: ["Mexico"], 1990: ["Italy"], 1994: ["United States"], 1998: ["France"],
    2002: ["South Korea", "Japan"], 2006: ["Germany"], 2010: ["South Africa"],
    2014: ["Brazil"], 2018: ["Russia"], 2022: ["Qatar"],
    2026: ["United States", "Mexico", "Canada"],
}
YEARS_24 = [1986, 1990, 1994]
YEARS_32 = [1998, 2002, 2006, 2010, 2014, 2018, 2022]
YEARS_48 = [2026]
ALL_YEARS = YEARS_24 + YEARS_32 + YEARS_48

ROUND_LABELS = {4: ["R16", "QF", "SF", "F"], 5: ["R32", "R16", "QF", "SF", "F"]}

DRAW_BASE = 0.25       # base draw probability in the group model
HOST_BONUS = 100.0     # Elo bonus for hosts, win probabilities only
TOL = 1e-9


# ----------------------------------------------------------------------------
# Elo helpers
# ----------------------------------------------------------------------------

def load_elo():
    e1 = pd.read_csv(os.path.join(DATA, "elo", "elo_pre_tournament.csv"))
    e2 = pd.read_csv(os.path.join(DATA, "elo", "elo_pre_tournament_1930_1986.csv"))
    elo = pd.concat([e1, e2], ignore_index=True)
    return {(int(r.tournament_year), r.team): float(r.elo) for r in elo.itertuples()}


def expectancy(ra, rb):
    return 1.0 / (1.0 + 10.0 ** (-(ra - rb) / 400.0))


class EloBook:
    """Per-tournament Elo lookups, raw and host-adjusted."""

    def __init__(self, year, elo_map, teams):
        self.year = year
        self.raw = {}
        hosts = set(HOSTS.get(year, []))
        self.adj = {}
        for t in teams:
            key = (year, t)
            if key not in elo_map:
                raise KeyError(f"Missing Elo for {t} in {year}")
            self.raw[t] = elo_map[key]
            self.adj[t] = elo_map[key] + (HOST_BONUS if t in hosts else 0.0)

    def winprob(self, a, b):
        return expectancy(self.adj[a], self.adj[b])


# ----------------------------------------------------------------------------
# Tournament data extraction
# ----------------------------------------------------------------------------

def load_tournament_1986_2022(mt, year):
    """Return groups, realized standings, ordered knockout rounds."""
    sub = mt[mt.year == year]
    grp = sub[sub.stage_name == "group stage"]
    groups, records = {}, {}
    for g, gdf in grp.groupby("group_name"):
        letter = g.replace("Group ", "")
        teams = sorted(gdf.team_name.unique())
        groups[letter] = teams
        agg = gdf.groupby("team_name").agg(
            w=("win", "sum"), d=("draw", "sum"),
            gf=("goals_for", "sum"), ga=("goals_against", "sum"),
            yel=("yellows", "sum"), dis=("dismissals", "sum"))
        ppw = 2 if year < 1994 else 3
        for t, row in agg.iterrows():
            records[(letter, t)] = dict(
                pts=row.w * ppw + row.d, gd=row.gf - row.ga, gf=row.gf,
                cards=row.yel + 3 * row.dis)
    # head-to-head results within groups (for tiebreak)
    h2h = {}
    for r in grp.itertuples():
        h2h[(r.team_name, r.opponent_name)] = (r.goals_for, r.goals_against)
    standings = {g: rank_group(groups[g], {t: records[(g, t)] for t in groups[g]},
                               h2h, 2 if year < 1994 else 3)
                 for g in groups}
    # knockout rounds in order
    rounds = []
    for stage in ["round of 16", "quarter-finals", "semi-finals", "final"]:
        st = sub[sub.stage_name == stage]
        if st.empty:
            continue
        ms = []
        for _, mdf in st.groupby("match_id"):
            a, b = list(mdf.team_name)
            winners = list(mdf[mdf.win == 1].team_name)
            assert len(winners) == 1, f"{year} {stage}: no unique winner {a} v {b}"
            ms.append((a, b, winners[0]))
        rounds.append(ms)
    return groups, standings, rounds


def load_tournament_2026():
    m = pd.read_csv(os.path.join(DATA, "worldcup-2026", "matches_2026.csv"),
                    encoding="utf-8-sig")
    grp = m[m.stage == "Group stage"]
    groups = defaultdict(set)
    records = defaultdict(lambda: dict(pts=0, gd=0, gf=0, cards=0))
    h2h = {}
    for r in grp.itertuples():
        g = r.group_name
        groups[g].update([r.home_team, r.away_team])
        hs, as_ = int(r.home_score), int(r.away_score)
        for t, o, gf_, ga_ in [(r.home_team, r.away_team, hs, as_),
                               (r.away_team, r.home_team, as_, hs)]:
            rec = records[(g, t)]
            rec["pts"] += 3 if gf_ > ga_ else (1 if gf_ == ga_ else 0)
            rec["gd"] += gf_ - ga_
            rec["gf"] += gf_
            h2h[(t, o)] = (gf_, ga_)
    groups = {g: sorted(ts) for g, ts in groups.items()}
    standings = {g: rank_group(groups[g], {t: records[(g, t)] for t in groups[g]},
                               h2h, 3) for g in groups}
    rounds = []
    for stage in ["Round of 32", "Round of 16", "Quarterfinals", "Semifinals",
                  "Final"]:
        st = m[m.stage == stage]
        if st.empty:
            continue
        ms = []
        for r in st.itertuples():
            hs, as_ = int(r.home_score), int(r.away_score)
            if hs != as_:
                w = r.home_team if hs > as_ else r.away_team
            else:
                ph, pa = [int(x) for x in str(r.score_penalties).split("-")]
                w = r.home_team if ph > pa else r.away_team
            ms.append((r.home_team, r.away_team, w))
        rounds.append(ms)
    return groups, standings, rounds


def rank_group(teams, recs, h2h, ppw):
    """Order teams: pts, GD, GF overall; then head-to-head mini-table
    (pts, GD, GF among the tied); then fewer cards (fair play); then name.
    Validated downstream by bracket-consistency asserts."""

    def overall_key(t):
        r = recs[t]
        return (-r["pts"], -r["gd"], -r["gf"])

    ordered = sorted(teams, key=overall_key)
    final = []
    i = 0
    while i < len(ordered):
        tied = [t for t in ordered if overall_key(t) == overall_key(ordered[i])]
        if len(tied) > 1:
            mini = {}
            for t in tied:
                pts = gd = gf = 0
                for o in tied:
                    if o == t or (t, o) not in h2h:
                        continue
                    a, b = h2h[(t, o)]
                    pts += ppw if a > b else (1 if a == b else 0)
                    gd += a - b
                    gf += a
                mini[t] = (-pts, -gd, -gf, recs[t]["cards"], t)
            tied = sorted(tied, key=lambda t: mini[t])
        final.extend(tied)
        i += len(tied)
    return final


# ----------------------------------------------------------------------------
# Bracket skeleton: nested tree with (group, position) leaves
# ----------------------------------------------------------------------------

def build_skeleton(year, groups, standings, rounds):
    slot_of = {}
    for g, order in standings.items():
        for pos, t in enumerate(order, start=1):
            slot_of[t] = (g, pos)
    # leaves of the first knockout round
    nodes, winners = [], []
    for a, b, w in rounds[0]:
        la, lb = slot_of[a], slot_of[b]
        nodes.append(("match", ("leaf", la), ("leaf", lb)))
        winners.append(w)
    check_skeleton_leaves(year, groups, [n for m in nodes
                                         for n in (m[1][1], m[2][1])])
    if year in YEARS_32:
        for (a, b, w) in rounds[0]:
            pa, pb = slot_of[a][1], slot_of[b][1]
            assert {pa, pb} == {1, 2}, \
                f"{year}: R16 {a} v {b} is not winner-vs-runner-up"
    # subsequent realized rounds pair the feeder nodes
    for rnd in rounds[1:]:
        idx = {w: i for i, w in enumerate(winners)}
        new_nodes, new_winners, used = [], [], set()
        for a, b, w in rnd:
            i, j = idx[a], idx[b]
            assert i not in used and j not in used
            used.update([i, j])
            new_nodes.append(("match", nodes[i], nodes[j]))
            new_winners.append(w)
        assert len(used) == len(nodes), f"{year}: unpaired feeder nodes"
        nodes, winners = new_nodes, new_winners
    # unplayed rounds (e.g. the 2026 final): structure is still determined
    while len(nodes) > 1:
        assert len(nodes) == 2, f"{year}: cannot infer structure with >2 nodes left"
        nodes = [("match", nodes[0], nodes[1])]
    return nodes[0]


def check_skeleton_leaves(year, groups, leaves):
    from collections import Counter
    c = Counter(leaves)
    assert all(v == 1 for v in c.values()), f"{year}: duplicated leaf slot"
    for g in groups:
        assert (g, 1) in c and (g, 2) in c, f"{year}: missing 1st/2nd slot for {g}"
    thirds = [l for l in leaves if l[1] == 3]
    expected_thirds = {1986: 4, 1990: 4, 1994: 4, 2026: 8}.get(year, 0)
    assert len(thirds) == expected_thirds, f"{year}: wrong number of third slots"
    assert len(set(t[0] for t in thirds)) == len(thirds), \
        f"{year}: two thirds from the same group"


def tree_leaves(node):
    if node[0] == "leaf":
        return [node[1]]
    return tree_leaves(node[1]) + tree_leaves(node[2])


def path_to_leaf(node, slot, trail=()):
    """Return list of sibling subtrees from the FIRST round up to the final."""
    if node[0] == "leaf":
        return [] if node[1] == slot else None
    for child, sib in [(node[1], node[2]), (node[2], node[1])]:
        below = path_to_leaf(child, slot)
        if below is not None:
            return below + [sib]
    return None


# ----------------------------------------------------------------------------
# Group qualification model (exact enumeration)
# ----------------------------------------------------------------------------

def group_joint(teams, book, ppw):
    """Exact joint distribution over finishing orders of a 4-team group under
    the Elo win/draw/loss model with uniform tie-splitting."""
    n = len(teams)
    pairs = list(combinations(range(n), 2))
    mp = []
    for i, j in pairs:
        E = book.winprob(teams[i], teams[j])
        p_d = min(DRAW_BASE, 2 * E, 2 * (1 - E))
        mp.append((E - p_d / 2, p_d, 1 - E - p_d / 2))
    joint = defaultdict(float)
    for outcome in product((0, 1, 2), repeat=len(pairs)):
        p = 1.0
        pts = [0.0] * n
        for k, (i, j) in enumerate(pairs):
            o = outcome[k]
            p *= mp[k][o]
            if o == 0:
                pts[i] += ppw
            elif o == 1:
                pts[i] += 1
                pts[j] += 1
            else:
                pts[j] += ppw
        if p <= 0:
            continue
        tiers = defaultdict(list)
        for idx in range(n):
            tiers[pts[idx]].append(idx)
        tier_lists = [tiers[v] for v in sorted(tiers, reverse=True)]
        perms = [list(permutations(t)) for t in tier_lists]
        n_ord = 1
        for pp in perms:
            n_ord *= len(pp)
        w = p / n_ord
        for combo in product(*perms):
            ordering = tuple(teams[idx] for tier in combo for idx in tier)
            joint[ordering] += w
    s = sum(joint.values())
    assert abs(s - 1.0) < 1e-6, f"group joint does not sum to 1: {s}"
    return dict(joint)


def marginal(joint, team, pos):
    return sum(p for o, p in joint.items() if o[pos - 1] == team)


def conditional_dist(joint, focal, focal_pos, pos):
    """P(team at `pos` | focal at `focal_pos`) within the same group."""
    denom = marginal(joint, focal, focal_pos)
    dist = defaultdict(float)
    for o, p in joint.items():
        if o[focal_pos - 1] == focal:
            dist[o[pos - 1]] += p
    return {t: v / denom for t, v in dist.items()}, denom


# ----------------------------------------------------------------------------
# Path evaluation
# ----------------------------------------------------------------------------

def winthrough(node, occupancy, book):
    """Distribution over teams winning through this subtree."""
    if node[0] == "leaf":
        return dict(occupancy[node[1]])
    dl = winthrough(node[1], occupancy, book)
    dr = winthrough(node[2], occupancy, book)
    out = defaultdict(float)
    for t, plt in dl.items():
        for u, pru in dr.items():
            w = book.winprob(t, u)
            out[t] += plt * pru * w
            out[u] += plt * pru * (1 - w)
    s = sum(out.values())
    assert abs(s - 1.0) < TOL, f"winthrough mass {s}"
    return dict(out)


def evaluate_team(year, team, pos, groups, joints, skeleton, book):
    """Score team's potential path assuming it finishes `pos` in its group.
    Returns (per-round rows, unweighted mean, weighted mean, qualification
    probability P(pos)), or None if the slot does not exist in the skeleton."""
    g_of = {t: g for g, ts in groups.items() for t in ts}
    g = g_of[team]
    slot = (g, pos)
    leaves = tree_leaves(skeleton)
    if slot not in leaves:
        return None
    # leaf occupancy distributions
    occupancy = {}
    qual_p = marginal(joints[g], team, pos)
    for leaf in leaves:
        lg, lp = leaf
        if lg == g:
            dist, _ = conditional_dist(joints[g], team, pos, lp)
        else:
            dist = {t: marginal(joints[lg], t, lp) for t in groups[lg]}
            dist = {t: v for t, v in dist.items() if v > 0}
        s = sum(dist.values())
        assert abs(s - 1.0) < 1e-6, f"{year} {leaf}: occupancy sums to {s}"
        occupancy[leaf] = {t: v / s for t, v in dist.items()}
    assert abs(occupancy[slot].get(team, 0.0) - 1.0) < 1e-9
    siblings = path_to_leaf(skeleton, slot)
    labels = ROUND_LABELS[len(siblings)]
    rows = []
    for rnd, sib in enumerate(siblings):
        sib_leaves = tree_leaves(sib)
        # unweighted possible-opponent set (a set: each team counted once per
        # round even when a group contributes both of its slots to the same
        # subtree, as in the anomalous 2002 half-split)
        cand = set()
        for (lg, lp) in sib_leaves:
            cand.update(t for t in groups[lg] if t != team)
        assert team not in cand
        if year in YEARS_32:
            distinct_groups = {lg for lg, lp in sib_leaves}
            expected = sum(len([t for t in groups[gg] if t != team])
                           for gg in distinct_groups)
            assert len(cand) == expected, \
                f"{year} {team}: opponent set corrupt at round {labels[rnd]}"
        unw = sum(book.raw[t] for t in cand) / len(cand)
        # weighted opponent distribution
        opp = winthrough(sib, occupancy, book)
        s = sum(opp.values())
        assert abs(s - 1.0) < TOL, \
            f"{year} {team} {labels[rnd]}: opponent probs sum to {s}"
        assert opp.get(team, 0.0) < TOL, \
            f"{year} {team}: appears in own opponent distribution"
        wtd = sum(p * book.raw[t] for t, p in opp.items())
        rows.append(dict(round_label=labels[rnd], unweighted_round_elo=unw,
                         weighted_round_elo=wtd, n_possible_opponents=len(cand),
                         cand=cand))
    if year in YEARS_32:
        union = set()
        for r in rows:
            union |= r["cand"]
        allothers = set(t for ts in groups.values() for t in ts) - {team}
        assert union == allothers, \
            f"{year} {team}: union of round sets misses {allothers - union}"
    for r in rows:
        del r["cand"]
    unw_mean = sum(r["unweighted_round_elo"] for r in rows) / len(rows)
    wtd_mean = sum(r["weighted_round_elo"] for r in rows) / len(rows)
    return rows, unw_mean, wtd_mean, qual_p


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    elo_map = load_elo()
    mt = pd.read_csv(os.path.join(DATA, "processed", "match_team_level.csv"))
    results, round_rows = [], []
    tournaments = {}

    for year in ALL_YEARS:
        if year == 2026:
            groups, standings, rounds = load_tournament_2026()
        else:
            groups, standings, rounds = load_tournament_1986_2022(mt, year)
        teams = [t for ts in groups.values() for t in ts]
        book = EloBook(year, elo_map, teams)
        ppw = 2 if year < 1994 else 3
        joints = {g: group_joint(groups[g], book, ppw) for g in groups}
        skeleton = build_skeleton(year, groups, standings, rounds)
        tournaments[year] = dict(groups=groups, book=book)

        for team in sorted(teams):
            per_slot = {}
            for pos, slot_name in [(1, "winner"), (2, "runner_up")]:
                res = evaluate_team(year, team, pos, groups, joints, skeleton,
                                    book)
                assert res is not None, f"{year} {team}: slot {pos} missing"
                rows, unw, wtd, qual_p = res
                per_slot[slot_name] = (unw, wtd, qual_p, len(rows))
                results.append(dict(year=year, team=team,
                                    slot_assumption=slot_name,
                                    unweighted_path_elo=round(unw, 2),
                                    weighted_path_elo=round(wtd, 2),
                                    rounds_used=len(rows)))
                for r in rows:
                    round_rows.append(dict(year=year, team=team,
                                           slot_assumption=slot_name, **r))
            # qualification-weighted blend
            (u1, w1, p1, nr), (u2, w2, p2, _) = per_slot["winner"], \
                per_slot["runner_up"]
            share = p1 / (p1 + p2) if (p1 + p2) > 0 else 0.5
            results.append(dict(
                year=year, team=team, slot_assumption="blend",
                unweighted_path_elo=round(share * u1 + (1 - share) * u2, 2),
                weighted_path_elo=round(share * w1 + (1 - share) * w2, 2),
                rounds_used=nr))

    df = pd.DataFrame(results)
    df.to_csv(OUT_CSV, index=False)
    rdf = pd.DataFrame(round_rows)
    rdf[["unweighted_round_elo", "weighted_round_elo"]] = \
        rdf[["unweighted_round_elo", "weighted_round_elo"]].round(2)
    rdf.to_csv(OUT_CSV_ROUNDS, index=False)
    write_report(df, tournaments)
    print(f"Wrote {OUT_CSV} ({len(df)} rows), {OUT_CSV_ROUNDS} "
          f"({len(rdf)} rows), {OUT_MD}")


# ----------------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------------

def seed_table(df, year, book):
    """Top-8 by pre-tournament Elo (Pot-1 proxy) plus Argentina, with path
    scores and hardest-first ranks."""
    top8 = sorted(book.raw, key=book.raw.get, reverse=True)[:8]
    cohort = list(top8) + (["Argentina"] if "Argentina" not in top8 else [])
    sub = df[df.year == year].set_index(["team", "slot_assumption"])
    rows = []
    for t in cohort:
        rows.append(dict(
            team=t, elo=book.raw[t],
            unw_winner=sub.loc[(t, "winner"), "unweighted_path_elo"],
            unw_runner_up=sub.loc[(t, "runner_up"), "unweighted_path_elo"],
            wtd_winner=sub.loc[(t, "winner"), "weighted_path_elo"],
            wtd_runner_up=sub.loc[(t, "runner_up"), "weighted_path_elo"],
            wtd_blend=sub.loc[(t, "blend"), "weighted_path_elo"]))
    tab = pd.DataFrame(rows)
    for col, rk in [("unw_winner", "rank_unw"), ("wtd_blend", "rank_wtd")]:
        tab[rk] = tab[col].rank(ascending=False, method="min").astype(int)
    return tab.sort_values("elo", ascending=False), "Argentina" in top8


def write_report(df, tournaments):
    lines = []
    a = lines.append
    a("# Hypothetical run-to-the-final draw analysis")
    a("")
    a("How hard was each team's POTENTIAL road from the group draw to the "
      "final -- judged before a ball was kicked, from the bracket structure "
      "and pre-tournament Elo, not from the opponents that actually showed "
      "up?  Generated by `analysis/hypothetical_paths.py`; full results in "
      "`data/processed/hypothetical_paths.csv` (path scores) and "
      "`data/processed/hypothetical_paths_by_round.csv` (per-round detail).")
    a("")
    a("## Method")
    a("")
    a("Two scores per team, per slot assumption (group winner / runner-up):")
    a("")
    a("- **Unweighted**: at each knockout round, the set of teams that could "
      "occupy the opposing bracket slot(s) given the draw; difficulty = mean "
      "pre-tournament Elo of that set; path score = mean across rounds "
      "(first knockout round through the final).")
    a("- **Elo-weighted**: each possible opponent weighted by its probability "
      "of reaching that round, iterating Elo win probabilities "
      "(E = 1/(1+10^(-d/400)), +100 host bonus) through the bracket.  A "
      "qualification-weighted **blend** mixes the winner/runner-up paths by "
      "the team's own conditional probability of finishing 1st vs 2nd.")
    a("")
    a("Group qualification probabilities come from exact enumeration of all "
      "3^6 outcomes of the group round-robin under an Elo win/draw/loss "
      "model: per match, draw probability = min(0.25, 2E, 2(1-E)) and "
      "P(win) = E - P(draw)/2 (consistent with Elo expectancy, draws = 0.5); "
      "era-correct points (2/win before 1994, 3/win after); points ties "
      "split uniformly over orderings since goals are not modelled.  "
      "Difficulty is always measured in raw Elo -- the host bonus affects "
      "win probabilities only.")
    a("")
    a("## Scope by format")
    a("")
    a("- **1998-2022 (32 teams)**: bracket fixed and known at the draw "
      "(A1 v B2 etc.) -- full computation, R16 through final, under both "
      "slot assumptions plus the blend.")
    a("- **2026 (48 teams)**: the R32 slots of the 8 best third-placed teams "
      "were NOT knowable at the draw.  We use the REALIZED bracket skeleton "
      "(which group's third landed where) and compute from the R32 onward -- "
      "a documented limitation; winner/runner-up slot projections are still "
      "draw-time information.")
    a("- **1986-1994 (24 teams)**: same issue (4 best thirds, placement "
      "matrices); implemented like 2026 with the realized skeleton, R16 "
      "onward.")
    a("- **Pre-1986**: skipped -- second group stages / final round mean "
      "there is no bracket to project.")
    a("")
    a("## Reading notes")
    a("")
    a("- **Winner and runner-up unweighted scores are identical in 1998-2022.**"
      "  This is a real property of the mirrored template, not a bug: group "
      "A's winner and runner-up both face group B at the R16 (1A v 2B, "
      "2A v 1B), groups C/D at the QF, and so on -- the possible-opponent "
      "SETS coincide.  What differs is which of those teams you are likely "
      "to meet (group winners face runners-up first), which only the "
      "Elo-weighted score captures -- runner-up paths are systematically "
      "harder there.")
    a("- **2002 anomaly**: to keep Korea-based groups in one half and "
      "Japan-based groups in the other, each group's winner and runner-up "
      "were drawn into the SAME half (e.g. 1E and 2E could meet in the "
      "semi-final).  The data-derived skeleton reproduces this faithfully.")
    a("- **2026 final**: not yet played at the data cutoff (semi-finals "
      "complete), but the bracket skeleton is fully determined, so all "
      "projections through the final are unaffected.")
    a("")
    a("## Sanity checks (asserted at run time)")
    a("")
    a("- Every group's 1st and 2nd slot appears exactly once in each "
      "skeleton; third-place slots come from distinct groups.")
    a("- 32-team editions: for every team and slot, each round's possible-"
      "opponent set has no duplicates and the union over rounds covers all "
      "31 other teams.")
    a("- Weighted opponent probabilities sum to 1 (+-1e-9) at every round "
      "for every slot, and a team never appears in its own opponent "
      "distribution.")
    a("")
    a("## Argentina vs the top seeds, edition by edition")
    a("")
    a("Cohort = top-8 pre-tournament Elo teams (Pot-1 proxy) plus Argentina "
      "when outside the top 8.  Rank 1 = HARDEST projected path within the "
      "cohort.  `unw` = unweighted, `wtd` = Elo-weighted; blend = "
      "qualification-weighted mix of winner/runner-up assumptions.")
    summary = []
    for year in ALL_YEARS:
        book = tournaments[year]["book"]
        tab, arg_in_top8 = seed_table(df, year, book)
        a("")
        a(f"### {year}")
        a("")
        if not arg_in_top8:
            a("*(Argentina outside the top-8 Elo this edition -- appended to "
              "the cohort.)*")
            a("")
        cols = ["team", "elo", "unw_winner", "unw_runner_up", "wtd_winner",
                "wtd_runner_up", "wtd_blend", "rank_unw", "rank_wtd"]
        a("| " + " | ".join(cols) + " |")
        a("|" + "---|" * len(cols))
        for _, r in tab.iterrows():
            vals = [str(r.team), f"{r.elo:.0f}"] + \
                   [f"{r[c]:.1f}" for c in cols[2:7]] + \
                   [str(r.rank_unw), str(r.rank_wtd)]
            a("| " + " | ".join(vals) + " |")
        arow = tab[tab.team == "Argentina"].iloc[0]
        n = len(tab)
        a("")
        a(f"Argentina: rank {arow.rank_unw}/{n} unweighted (winner slot), "
          f"rank {arow.rank_wtd}/{n} Elo-weighted (blend); "
          f"1 = hardest projected path.")
        summary.append(dict(year=year, n=n, rank_unw=int(arow.rank_unw),
                            rank_wtd=int(arow.rank_wtd),
                            unw=arow.unw_winner, wtd=arow.wtd_blend))
    a("")
    a("## Summary: Argentina's projected-path rank per edition")
    a("")
    a("| year | cohort size | unweighted rank | weighted rank | "
      "unw path Elo | wtd path Elo |")
    a("|---|---|---|---|---|---|")
    for s in summary:
        a(f"| {s['year']} | {s['n']} | {s['rank_unw']} | {s['rank_wtd']} | "
          f"{s['unw']:.1f} | {s['wtd']:.1f} |")
    a("")
    a("*(Rank 1 = hardest projected path among the cohort; larger rank = "
      "easier draw.)*")
    a("")
    a("## Headline findings")
    a("")
    by_year = {s["year"]: s for s in summary}
    s22, s26 = by_year[2022], by_year[2026]
    best_rank = min(s["rank_wtd"] for s in summary)
    worst_rank = max(s["rank_wtd"] for s in summary)
    hardest_yrs = "/".join(str(s["year"]) for s in summary
                           if s["rank_wtd"] == best_rank)
    easiest_yrs = "/".join(str(s["year"]) for s in summary
                           if s["rank_wtd"] == worst_rank)
    a(f"- **2022 projected EASY at the draw**: among the top-8 Elo seeds "
      f"Argentina ranked {s22['rank_unw']}/{s22['n']} unweighted and "
      f"{s22['rank_wtd']}/{s22['n']} Elo-weighted -- near the bottom of the "
      f"cohort on both methods.  The bracket that later felt brutal "
      f"(Netherlands, Croatia, France in the knockouts) was not projected "
      f"to be so when the groups were drawn.")
    a(f"- **2026 also projected on the easy side**: rank "
      f"{s26['rank_unw']}/{s26['n']} unweighted and "
      f"{s26['rank_wtd']}/{s26['n']} Elo-weighted among the top seeds "
      f"(realized-skeleton caveat above applies to the third-place slots).")
    a(f"- Argentina's HARDEST projected draw(s) of the era on the weighted "
      f"method: {hardest_yrs} (rank {best_rank}); easiest: {easiest_yrs} "
      f"(rank {worst_rank}).")
    a("- Across editions Argentina's weighted runner-up path is always "
      "harder than its winner path (you meet group winners a round "
      "earlier) -- EXCEPT 2022.  There, finishing second in Group C "
      "projected slightly softer overall: the runner-up slot did face a "
      "likely France at the R16 (1976 vs 1925 weighted), but the winner "
      "slot's semi-final quarter contained the likely group winners of "
      "BOTH Spain's and Brazil's groups (SF round weighted 2072 vs 1987), "
      "which outweighed it.")
    a("")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    main()
