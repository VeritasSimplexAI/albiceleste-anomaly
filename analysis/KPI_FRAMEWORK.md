# KPI framework — Argentina officiating analysis (1990–2026)

All KPIs are per-match rates with exact Poisson 95% CIs unless noted.
Eras: pre (1990–2018), 2022, 2026. "Post-apex" = 2022+2026 combined.

## Tier 1 — direct officiating outcomes
PRINCIPLE: bias lives in referee DECISIONS, not player execution. Penalties
AWARDED (regardless of outcome) are the primary metric; conversions are
descriptive only. Same logic everywhere: fouls called, cards shown, VAR
overturns — all measured as decisions in each direction.
1. Penalties awarded for / against, and net. Sources: 2014+ FBref
   PKatt/PKwon/PKcon; 1990–2010 compiled per-incident from match archives
   (RSSSF / FIFA technical reports / Wikipedia match reports); converted-only
   counts (goals.csv) used solely as a cross-check lower bound.
2. Yellow cards received / drawn; card differential per match.
3. Dismissals (straight red + second yellow) for / against.
4. Fouls committed / drawn (2014+ via FBref).
5. Cards-per-foul leniency ratio, both directions: fouls_committed / yellows_received
   (higher = more lenient treatment) vs the same for opponents.
6. VAR overturns benefiting / harming the team; net VAR swing (2018+,
   journalistic compilation — softer evidence class, flagged as such).

## Tier 2 — context adjustments
7. Stage-adjusted rates: group vs knockout (knockouts differ systematically).
8. Deep-run cohort: compare only against other semifinalists of the same tournament.
9. Empirical-Bayes (Gamma-Poisson) shrunk team rankings — protects against
   small-sample teams topping the charts by noise.

## Tier 3 — inference
10. Exact Poisson rate-ratio tests, Argentina vs pooled field, per era.
11. Difference-in-differences: (Argentina post − pre) − (field post − pre).
12. Poisson GLM at match level: outcome ~ is_argentina + is_argentina:post2022
    + knockout + tournament fixed effects, cluster-robust SEs by team.
    The interaction term IS the thesis test: "extra Argentina favorability after 2022".
13. Benjamini–Hochberg FDR scan across all teams x metrics: is Argentina uniquely
    extreme or one of several outliers?

## Known limitations (must be published with the site)
- THE UNCALLED-INCIDENT GHOST (selection bias): "fouls" data is itself the
  referee's output — challenges that SHOULD have been fouls/cards but weren't
  given never enter any dataset. A referee swallowing the whistle for one team
  makes that team's numbers look NORMAL. Fouls/cards must therefore be read as
  decision-consistency metrics, not ground truth about physical play. The only
  cure is independent video re-refereeing of match footage (manual, per-match) —
  flagged as future work; penalties awarded and VAR overturns are less exposed
  to this bias because the underlying incidents (shots, goals, contact in the
  box leading to review) are more independently observable.
- Post-2022 sample: 7 matches (2022) + 7 so far (2026). Wide CIs are honest CIs.
- Converted-vs-awarded penalty gap pre-2014.
- VAR incident data is compiled from journalism, not an official FIFA database.
- Fouls unavailable before 2014.
- Deep runs mechanically inflate counting stats; rates + stage adjustment mitigate.
