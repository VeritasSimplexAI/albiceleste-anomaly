# Officiating data — FIFA Men's World Cups 2014, 2018, 2022, 2026

Compiled 2026-07-16. The 2026 World Cup was **in progress** at compile time:
data covers the 102 matches played through the semifinals (last match included:
England 1-2 Argentina, 2026-07-15). The third-place match and final are NOT included.

Every number in these files was read from a fetched web page (listed below).
Nothing was estimated. Fields that could not be verified are left blank and
explained here.

---

## Files

### 1. squad_discipline.csv (144 rows: 32 + 32 + 32 + 48 teams)

One row per team per tournament. Sources: FBref "Squad Misc Stats" and
"Squad Standard Stats" tables for each World Cup.

FBref's live site blocks automated access (HTTP 403), so all pages were
retrieved via Wayback Machine snapshots (several were freshly created for this
task with Save Page Now on 2026-07-16, so they reflect FBref's current data).
The 2026 snapshots contain exactly 102 matches (sum of squad matches-played =
204 = 102 x 2), i.e. complete through the semifinals.

Column -> source table:
- matches_played, penalty_kicks_attempted (PKatt) -> Squad Standard Stats
- fouls_committed (Fls), fouls_drawn (Fld), yellow_cards (CrdY),
  red_cards (CrdR), penalties_won (PKwon), penalties_conceded (PKcon)
  -> Squad Misc Stats
- source_url column carries the misc-stats snapshot; the standard-stats
  snapshots (for matches_played and penalty_kicks_attempted) are listed below.

FBref snapshot URLs used:
- 2014 misc: https://web.archive.org/web/20260716204012/https://fbref.com/en/comps/1/2014/misc/2014-FIFA-World-Cup-Stats
- 2014 standard: https://web.archive.org/web/20260716204107/https://fbref.com/en/comps/1/2014/stats/2014-FIFA-World-Cup-Stats
- 2018 misc: https://web.archive.org/web/20260716203607/https://fbref.com/en/comps/1/2018/misc/2018-FIFA-World-Cup-Stats
- 2018 standard: https://web.archive.org/web/20250519020101/https://fbref.com/en/comps/1/2018/stats/2018-FIFA-World-Cup-Stats
- 2022 misc: https://web.archive.org/web/20260716203158/https://fbref.com/en/comps/1/2022/misc/2022-FIFA-World-Cup-Stats
- 2022 standard: https://web.archive.org/web/20260716203513/https://fbref.com/en/comps/1/2022/stats/2022-FIFA-World-Cup-Stats
- 2026 misc: https://web.archive.org/web/20260716203655/https://fbref.com/en/comps/1/2026/misc/2026-FIFA-World-Cup-Stats
- 2026 standard: https://web.archive.org/web/20260716203739/https://fbref.com/en/comps/1/2026/stats/2026-FIFA-World-Cup-Stats

Coverage quality:
- 2014: PARTIAL. FBref does not publish fouls, fouls-drawn, penalties-won or
  penalties-conceded for the 2014 tournament (those columns are blank on the
  source page for every squad). Cards, matches played and PK attempts are complete.
- 2018: COMPLETE (all requested columns populated for all 32 squads).
- 2022: COMPLETE (all requested columns populated for all 32 squads).
- 2026: PARTIAL (in progress, through 102 of 104 matches). Fouls, cards,
  matches and PK attempts populated for all 48 squads; FBref leaves PKwon and
  PKcon blank for 2026, so penalties_won / penalties_conceded are blank.

Definitions / caveats:
- penalty_kicks_attempted counts in-game penalty kicks only (no shoot-outs).
- FBref counts a second-yellow dismissal in both CrdY and a separate 2CrdY
  column; totals may differ slightly from FIFA official card counts
  (e.g. FBref sums for yellows: 2014 = 188, 2018 = 223, 2022 = 230).
- fouls_drawn (FBref "Fld") is FBref's count of fouls suffered; it does not
  exactly equal the sum of opponents' fouls committed in other providers' data.
- Team names were normalised (Türkiye -> Turkey, Korea Republic -> South Korea,
  Cabo Verde -> Cape Verde, Congo DR -> DR Congo, Côte d'Ivoire -> Ivory Coast,
  Bosnia–Herz -> Bosnia and Herzegovina, Czechia -> Czech Republic, IR Iran -> Iran).

### Argentina cross-check (second source: ESPN per-match box scores)

Argentina's rows were re-computed by summing ESPN's per-match team statistics
(site.api.espn.com match summaries) for every Argentina match in each tournament:

| Year | Metric | FBref | ESPN sum | Match? |
|------|--------|-------|----------|--------|
| 2014 | matches | 7 | 7 | yes |
| 2014 | fouls | (blank on FBref) | 64 | ESPN only |
| 2014 | yellow cards | 8 | 6 | **discrepancy** |
| 2014 | red cards | 0 | 0 | yes |
| 2014 | PK attempts | 0 | 0 | yes |
| 2018 | fouls | 56 | 55 | 1 apart |
| 2018 | yellow cards | 11 | 11 | yes |
| 2018 | red cards | 0 | 0 | yes |
| 2018 | PK attempts | 1 | 1 | yes |
| 2022 | fouls | 100 | 100 | yes |
| 2022 | yellow cards | 19 | 17 | **discrepancy** |
| 2022 | red cards | 0 | 0 | yes |
| 2022 | PK attempts | 5 | 5 | yes |
| 2026 | fouls | 88 | 88 | yes |
| 2026 | yellow cards | 9 | 9 | yes |
| 2026 | red cards | 0 | 0 | yes |
| 2026 | PK attempts | 3 | 3 | yes |

The two yellow-card discrepancies (2014: 8 vs 6; 2022: 19 vs 17) are most
likely due to providers counting differently cards shown to substitutes/bench
players or cards shown after full time / during shoot-outs (Argentina's 2022
QF vs Netherlands produced many such cards). Not resolved; both values noted.
The CSV keeps the FBref values, matching the rest of the file.

ESPN endpoints used for the cross-check (all Argentina match IDs, fetched
2026-07-16; pattern: https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/summary?event=ID):
- 2014: 383293, 383277, 383262, 383248, 383244, 383241, 383239
- 2018: 498197, 498180, 498163, 498154
- 2022: 633794, 633807, 633824, 633836, 633844, 633847, 633850
- 2026: 760433, 760456, 760483, 760500, 760509, 760513, 760515
- Match lists from: https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates=YYYYMMDD-YYYYMMDD

Also cross-checked (2026): sanity check of Sky Sports match page for the R16
(referenced by Wikipedia): https://www.skysports.com/football/argentina-vs-egypt/549861

---

### 2. var_incidents.csv (113 rows: 21 + 27 + 65)

One row per VAR intervention/overturn (plus formally-logged rejected on-field
reviews, recorded as decision_type = other). VAR did not exist at the 2014
World Cup, so it has no rows.

**2018 (21 rows) — coverage: COMPLETE (interventions/on-field reviews).**
Source: REFSIX, "Every VAR Review at the FIFA World Cup 2018"
(https://refsix.com/news/2018/7/18/every-var-on-field-review-at-the-fifa-world-cup-2018),
which itemises all 21 VAR reviews of the tournament (19 match sections; the
Iran-Portugal match had 3 reviews). Note: media counts differ slightly by
definition — ESPN's 2022 tracker describes 2018 as "17 overturns and 3
rejections"; REFSIX counts 21 reviews because it also includes factual
decisions (no on-field review) and the mistaken-identity card change.
One correction: REFSIX's Peru-Denmark paragraph reverses the teams; the
penalty was awarded to PERU (foul by Poulsen on Cueva, who missed). Verified
against Wikipedia (https://en.wikipedia.org/wiki/2018_FIFA_World_Cup_Group_C),
which is the source_url for that row.

**2022 (27 rows) — coverage: COMPLETE.**
Source: ESPN, "2022 World Cup VAR review: Every decision in Qatar analysed"
by Dale Johnson — fetched via a Wayback snapshot created for this task:
https://web.archive.org/web/20260716205424/https://www.espn.com/soccer/story/_/id/37634070/var-review-every-decision-world-cup-analysed
ESPN's own totals: 27 interventions = 25 overturns (incl. 1 penalty retake)
+ 2 rejected on-field reviews. The 27 CSV rows reproduce exactly that set
(the France-Poland penalty and its retake are 2 rows; the two rejected
reviews are decision_type = other). Match dates taken from ESPN's 2022
scoreboard API. The 2022 final (Argentina 3-3 France) had NO VAR overturn:
ESPN analysed the Di Maria penalty as an on-field decision that VAR checked
and did not overturn — hence no row for the final.

**2026 (65 rows) — coverage: PARTIAL-to-COMPLETE for goal/penalty/red-card
overturns; includes 26 ambiguous feed entries.**
Compiled from three fetched sources:
1. ESPN match commentary feeds for ALL 102 matches played (systematic sweep;
   structured "VAR Decision: ..." entries). 52 matches contained VAR entries.
2. ESPN's running 2026 tracker column ("World Cup VAR review", Andy Davies /
   Dale Johnson), archived:
   - https://web.archive.org/web/20260716210709/https://www.espn.co.uk/football/story/_/id/49027532/world-cup-2026-var-review-red-card-penalty-handball-goal-line-technology
   - https://web.archive.org/web/20260716210756/https://www.espn.com/soccer/story/_/id/49283462/world-cup-2026-var-review-quansahs-red-kanes-penalty-did-ref-get-right
3. Wikipedia's 2026 knockout-stage article (fetched 2026-07-16).

Breakdown of the 65 rows: 12 goals disallowed, 3 goals awarded, 8 penalties
awarded, 1 penalty rescinded (changed to free kick), 9 red cards via VAR,
1 mistaken-identity card change, 1 penalty retake, 4 "no penalty" review
outcomes, and 26 rows where ESPN's feed logs only
"VAR Decision: Other Decision Cancelled" with no detail. Those 26 are included
for completeness with blank beneficiary — treat them with caution; the feed
does not say what was cancelled.

2026 caveats:
- match_date for 2026 (and 2022) rows is the ESPN event date in UTC; matches
  played in evening US time zones can therefore differ by one day from the
  local date (e.g. the Argentina-Switzerland QF: local July 11, UTC July 12).
- The ESPN feed's category labels were interpreted with surrounding
  commentary and the tracker column (e.g. "Card upgraded X" is always
  followed by "X is shown the red card").
- No VAR entries were logged for 51 of the 102 matches, including
  Argentina-Cape Verde (R32) and England-Argentina (SF): no interventions there.

Argentina matches with VAR rows (10 total):
- 2018 Nigeria-Argentina: Rojo handball review, referee stuck with no penalty (favoured Argentina).
- 2022 Argentina-Saudi Arabia: VAR penalty to Argentina (Messi scored); Lautaro Martinez goal disallowed (offside).
- 2022 Poland-Argentina: VAR penalty to Argentina (Messi's kick saved); ESPN judged the intervention unnecessary.
- 2026 Argentina-Algeria: Algeria goal (Chaibi, 8') ruled out by VAR.
- 2026 Argentina-Austria: VAR penalty to Argentina (7'), Messi missed.
- 2026 Jordan-Argentina: VAR penalty to Argentina (29'), Lautaro Martinez scored.
- 2026 Argentina-Egypt (R16): Egypt goal (Zico, 58') disallowed for a foul in the build-up; plus one unexplained "Other Decision Cancelled" at 32'.
- 2026 Argentina-Switzerland (QF): Paredes yellow rescinded, Embolo booked for simulation instead — second yellow, sent off.

---

## Argentina VAR controversies (2026), with coverage links

**Egypt vs Argentina, round of 16, 2026-07-07 (Argentina won 3-2 after
trailing 2-0).** The most disputed VAR call of Argentina's tournament:
- With Egypt 1-0 up, Mostafa Zico's 58th-minute goal (which would have made it
  2-0) was disallowed after an on-field review for a foul by Marwan Attia on
  Lisandro Martinez (shirt hold plus stepping on his foot) at the start of the
  counter-attack. Egypt still made it 2-0 through Zico in the 67th, but
  Argentina scored 3 goals in the final 11+ minutes.
- ESPN's news report (Mark Ogden): "The VAR mission creep continues, this time
  to Egypt's detriment... contact was minimal and nowhere near enough to
  warrant such an intervention" — and Egypt were "rightly furious" that VAR
  did NOT intervene for an apparent Mac Allister shirt-pull on Hamdy Fathy in
  the box in the same phase as Argentina's stoppage-time winner, nor for a
  Julian Alvarez challenge on Mohamed Salah late on. Several Egypt players and
  coach Hossam Hassan were booked in the aftermath.
  https://web.archive.org/web/20260716210322/https://www.espn.com/soccer/story/_/id/49298199/argentina-lionel-messi-world-cup-round-16-egypt-var-mohamed-salah
- ESPN's refereeing analyst Andy Davies, by contrast, judged the disallowal
  "a correct intervention", while ESPN's embedded video segment quotes a VAR
  expert calling it "probably intervention too far" (both in the tracker
  column, first URL below). Both late Egypt appeals were checked and cleared.
  https://web.archive.org/web/20260716210709/https://www.espn.co.uk/football/story/_/id/49027532/world-cup-2026-var-review-red-card-penalty-handball-goal-line-technology
- Wikipedia's knockout-stage article records the disallowed goal and cites the
  Sky Sports report: https://www.skysports.com/football/argentina-vs-egypt/549861
- Also in this match (not VAR): Messi's 21st-minute penalty (won by
  Tagliafico, foul by Haissem Hassan — awarded on-field) was saved by
  Mostafa Shobeir.

**Argentina vs Switzerland, quarterfinal (local 2026-07-11 / UTC 07-12,
Argentina won).** Shortly after Ndoye's equaliser, Leandro Paredes was booked
for a challenge on Breel Embolo. VAR review showed Embolo fell before any
contact; under the new mistaken-identity protocol the card was rescinded and
transferred to Embolo for simulation — his second yellow, so Switzerland went
down to 10. ESPN's analyst supported the call ("Embolo has only himself to
blame") but noted debate about whether the new law's wording allows this use;
it was the second such reversal of the tournament after Tim Ream/Almiron in
USA-Paraguay (2026-06-13). Covered in the ESPN tracker column (URL above) and
Wikipedia's knockout-stage article.

**Also notable (Argentina, 2026, not an intervention):** in the group opener
vs Algeria, a 30th-minute studs-to-calf tackle by Messi on Aissa Mandi was
checked and cleared with no card; ESPN's analyst wrote "this was a red card
offense" in his verdict (tracker column, URL above).

---

## Gaps and caveats (summary)

1. 2014 fouls / fouls-drawn / penalties won-conceded: not published by FBref;
   blank in squad_discipline.csv. (Argentina's 2014 fouls from the ESPN
   cross-check: 64 committed — single-source, so not entered in the CSV.)
2. 2026 penalties won/conceded: not published by FBref yet; blank.
3. 2026 is incomplete: through 102 of 104 matches (semifinals). Final and
   third-place match missing (played after 2026-07-16).
4. Yellow-card counting differs between FBref, ESPN and FIFA (second yellows,
   bench cards, post-match cards). Two Argentina discrepancies documented above.
5. var_incidents.csv is a journalistic compilation, not an official FIFA
   database. 2018 relies on one comprehensive source (REFSIX) plus a Wikipedia
   correction; 2022 mirrors ESPN's authoritative tracker; 2026 combines a
   structured feed sweep with ESPN's tracker column — the 26 "Other Decision
   Cancelled" rows are unexplained in the source feed.
6. FIFA's official refereeing/VAR statistics PDF for 2018 exists
   (https://fifa-backend.pressfire.net/media/newsletter/FWC18-Refereeing-VAR-Report-Statistics-Finals-STATS.pdf,
   found via search, not parsed) — could be used to reconcile 2018 counts.
7. beneficiary_team is blank where a decision favoured neither team
   (mistaken-identity card corrections within one team, unexplained feed rows).
8. All Wayback URLs above were live snapshots verified during compilation on
   2026-07-16; the live fbref.com and espn.com pages block automated fetching.


---

## 2026 ambiguous resolution (added 2026-07-17)

The 26 unexplained "VAR Decision: Other Decision Cancelled" rows from the 2026
feed sweep (blank beneficiary_team) have been investigated one by one. Results
are in `var_incidents_resolved.csv`, which contains all 113 rows of
`var_incidents.csv` plus a new `resolution_source` column (URLs actually
fetched during resolution on 2026-07-17). The 87 other rows are unchanged.
(Note: the resolution brief referred to "27" ambiguous rows; the 27th
blank-beneficiary row is the 2018 France-Peru mistaken-identity correction,
which is intentionally non-directional and was left as-is.)

**Method.** For each of the 22 matches involved, the full ESPN summary feed
(play-by-play + embedded ESPN match report) was fetched from
`site.api.espn.com`. In this feed, every genuine overturn carries an explicit
label ("VAR Decision: No Goal ...", "Goal ...", "Penalty ...", "No Penalty
...", "Card upgraded ...", "Card Changed"), and goals/penalties/cards are
logged as their own entries. None of the 26 "Other Decision Cancelled" entries
coincides with any goal, penalty, or card change, and no ESPN match report
mentions a VAR incident at those minutes. ESPN's VAR tracker column (Wayback
snapshot of 2026-07-16, story id 49027532) covers six of the affected matches
and records no intervention at these minutes either. Targeted press checks
were made for the knockout rows and the most suggestive group rows.

**Outcome (26 rows):**

- **Resolved with review subject identified: 1.** Bosnia and Herzegovina vs
  Qatar (2026-06-24, 28'): the entry was the check on Alajbegovic's 29'
  opening goal, which VAR confirmed ("After a short suspension due to a VAR
  auto check, it has been established as a goal by all regular means" - Sunday
  Guardian live report). Classified `no_overturn`, beneficiary Bosnia and
  Herzegovina.
- **No-overturn feed artifacts, review subject unknown: 25.** All verified
  against the full feed + match report (+ tracker column where available) as
  producing no change to any on-field decision; reclassified from `other` to
  `no_overturn` so they can be excluded from overturn counts. Six of these
  have a plausible subject suggested by adjacent feed context, noted as
  unverified in the description (Belgium-Egypt 12' card check; Switzerland-
  Bosnia 56' offside; Uruguay-Cape Verde 90'+3'; Colombia-DR Congo 45'+5'
  handball; Morocco-Haiti 57' offside; Argentina-Egypt 32' after Messi's free
  kick hit the post).
- **Still unknown whether an overturn occurred: 0.**

**Impact on net-VAR pictures:** none. All 26 rows were previously
non-directional (`other`, blank beneficiary) and none turned out to be an
overturn, so no team's overturn/benefit counts change. Overturn tallies
should filter `decision_type != 'no_overturn'` (and continue to treat the
directional `other` rows - rejected reviews, retakes, card transfers - per
existing conventions). The one Argentina row among the 26 (vs Egypt, R16
2026-07-07, 32') resolved as a no-overturn artifact and does not affect
Argentina's totals.

**Side-finding:** the France vs Spain semifinal (2026-07-14) featured a
notable VAR check that CONFIRMED Spain's 20' penalty (Digne on Yamal; fan
petition and press coverage followed, and per press reports FIFA adjusted VAR
protocol before the semifinals). It is a confirmation, not an overturn, and is
not currently a row in the CSV; flagged here in case non-overturn checks are
ever added systematically.

---

## Confirmed (non-overturn) VAR reviews — var_confirmed_reviews.csv (added 2026-07-17)

New file: `var_confirmed_reviews.csv` (74 rows: 5 × 2018, 22 × 2022, 47 × 2026).
One row per formally recorded VAR review/check that CONFIRMED the on-field
decision (no overturn), with the team the standing decision favoured.
Columns: tournament_year, match_date, home_team, away_team, minute,
review_subject, standing_decision, favoured_team, source_url.

### KEY CAVEAT — read this before using the file

**Confirmed-review counts are a LOWER BOUND, and they are recorded
asymmetrically versus overturns.** Under FIFA's protocol every goal, penalty
incident and red-card situation is silently checked by the VAR; virtually none
of those background checks are individually published. FIFA's own 2018 figures
make the gap concrete: 455 incidents checked across 64 matches (~7.1 per game)
versus only ~20 formal reviews — i.e. more than 95% of VAR activity produced
no public record (FIFA 2018 refereeing stats PDF:
https://fifa-backend.pressfire.net/media/newsletter/FWC18-Refereeing-VAR-Report-Statistics-Finals-STATS.pdf
— graphics-only, not text-parseable; group-stage breakdown 335 checks /
17 reviews / 14 changed reported by ITV News:
https://www.itv.com/news/2018-06-29/var-checked-335-incidents-in-world-cup-group-stage-helping-referees-get-99-3-decisions-correct).
Overturns, by contrast, are essentially always recorded by every outlet.
A confirmation only enters the public record when (a) the referee went to the
monitor and rejected the review, (b) a data feed happened to log the check, or
(c) a journalist chose to analyse it. So the rows in this file are the
*recorded* confirmations, not *the* confirmations, and cross-team comparisons
on this file inherit each source's editorial choices.

### Method and coverage grade, per tournament

**2018 — 5 rows. Grade: COMPLETE for on-field reviews; NO coverage of silent
checks.** Source: REFSIX's itemised list of all 21 reviews (same source as
var_incidents.csv), taking the 5 whose outcome text says the referee stuck
with / did not overturn the on-field decision: Costa Rica–Serbia (no red,
Prijovic), Saudi Arabia–Egypt (penalty award stood), Iran–Portugal (no red,
Ronaldo), Nigeria–Argentina (no penalty, Rojo), Mexico–Sweden (no penalty,
Hernandez). REFSIX does not give incident minutes, so `minute` is blank for
all 2018 rows (not fabricated from memory). The two "no red card" rows ended
with a yellow being issued, i.e. the reviewed-for red was rejected but a
lesser sanction was added — they are conventionally counted as non-overturns
(ESPN's "17 overturns and 3 rejections" framing counts only the three
penalty-related rejections; our 5 use REFSIX's outcome wording).

**2022 — 22 rows. Grade: GOOD but EDITORIAL.** Source: ESPN's tracker
("Every decision in Qatar analysed", Dale Johnson; same Wayback snapshot as
var_incidents.csv). The tracker formally records, with match and verdict,
both rejected on-field reviews (Ghana–Uruguay, Denmark–Tunisia) and a set of
background checks it chose to analyse ("VAR decision: No penalty / Goal
stands / Penalty stands"), including six checks in the final alone and the
two goalkeeper-line checks after saved penalties (Mexico–Poland,
Poland–Saudi Arabia). ESPN covered every match but only wrote up incidents it
judged significant — this is journalist-selected coverage, not a check
registry. Note the Denmark–Tunisia "confirmation" is impure: the referee
rejected the advised handball penalty but restarted with a free kick to
Tunisia for an earlier Denmark foul.

**2026 — 47 rows. Grade: MIXED; two very different record types; through the
semifinals only (102 of 104 matches).**
1. *Feed-logged checks (26 rows)*: the 26 "VAR Decision: Other Decision
   Cancelled" entries from the systematic ESPN feed sweep (reclassified
   no_overturn in var_incidents_resolved.csv). These are machine-logged and
   systematic across all 102 matches, but the label carries no subject.
2. *Tracker/press-recorded checks (21 rows)*: incidents with identified
   subject and outcome from ESPN's 2026 VAR column (Andy Davies), its
   Mexico–England companion piece, the feed's explicit "No Penalty X"
   entries, and (France–Spain penalty) thevarverdict.com + the ESPN feed.
   Same editorial-selection caveat as 2022.

### Resolution of the 26 feed-logged 2026 rows (the task's core question)

Favoured team resolved for **6 of 26**; the remaining 20 keep
`favoured_team` blank.

- **Verified (1):** Bosnia and Herzegovina–Qatar 28' — check on
  Alajbegovic's 29' goal, confirmed (Sunday Guardian live report). Favoured
  Bosnia and Herzegovina.
- **Probable (5)** — assigned only where a same-or-adjacent-minute *on-field
  decision event* identifies the likely subject AND every plausible adjacent
  candidate favours the same team; each row says PROBABLE in review_subject:
  - Switzerland–Bosnia 56': Ndoye (SUI) offside flagged the same minute with
    a logged review stoppage → flag stood → favoured Bosnia and Herzegovina.
  - Morocco–Haiti 57': El Kaabi (MAR) offside flagged at 56' → flag stood →
    favoured Haiti.
  - Colombia–DR Congo 45+5': handball called against Wissa (COD) at 45+4'
    during a Colombia attack; whether the check was penalty-or-not or
    card-or-not, the standing outcome favoured DR Congo.
  - Uruguay–Cape Verde 90+3': both same-minute candidates (Uruguay fast-break
    attempt; Borges (CPV) yellow card) leave Cape Verde favoured.
  - New Zealand–Egypt 21': both adjacent candidates (Egypt corner sequence
    same minute; Singh (NZL) yellow at 20') leave New Zealand favoured.
- **Unresolved (20):** no press coverage found (targeted searches were run
  for Brazil–Morocco, Spain–Austria, US–Australia, Argentina–Egypt 32',
  France–Spain 83' and others; live blogs and match reports do not mention
  these checks), and feed adjacency was either absent or pointed in
  conflicting directions (e.g. Belgium–Egypt 12', where nearby fouls belong
  to both teams). Rows kept with favoured_team blank per instruction.
  These 20 include one Argentina match row (Argentina–Egypt R16, 32', right
  after Messi's free kick hit the post — suggestive but not determinable).

Correction found during re-verification: the earlier note (2026 ambiguous
resolution, above) said press reported a stoppage-time Uruguay "third goal"
disallowed vs Cape Verde. Re-reading the cited VAVEL live blog: the match
finished 2-2 and the only disallowed Uruguay goal it records is at 24'
(Maxi Araújo, offside, first half — an on-field call with no feed VAR entry).
The 90+3' feed entry therefore remains subject-unknown; the probable-Cape
Verde assignment rests on the same-minute feed candidates, not on the
"third goal" claim.

### Double-counting warning

11 rows of var_confirmed_reviews.csv also exist in
var_incidents_resolved.csv as decision_type = `other` (the formally logged
rejected reviews): all five 2018 rows, Denmark–Tunisia and Ghana–Uruguay
(2022), and France–Senegal 62', Ecuador–Germany 47', New Zealand–Belgium 21',
Norway–England 101' (2026). The 26 feed rows exist there as
decision_type = `no_overturn`. Any combined metric must use ONE of the two
files per incident class, not both.

### Argentina, for the site's purposes

Confirmed reviews favouring Argentina: **9** (2018 Rojo no-penalty; 2022
final ×4: Di Maria penalty stood, Otamendi no red, Thuram no penalty,
L. Martinez onside on Messi's 108' goal; 2026 ×4: Messi–Mandi no card vs
Algeria, goal-check cleared vs Austria 38', and both late Egypt appeals
checked and cleared in the R16). Confirmed reviews against Argentina
(favouring the opponent): 2 (2022 final: Mac Allister no-penalty 62',
Montiel penalty stood 114'). One Argentina-match row unresolved
(vs Egypt R16 32'). Argentina's high confirmed-in-favour count is partly a
coverage artifact: Argentina played the most-analysed matches (two finals
runs), and the 2022 final alone contributed 6 of ESPN's recorded checks.

### Verdict on a "decisions in favour" metric (overturns + confirmed)

Not defensible as a symmetric cross-team statistic with this coverage; usable
only with a strong asymmetry warning. Overturn counts are near-complete for
all three tournaments; confirmed-review counts are (a) a lower bound, (b)
journalist-selected for 2022 and half of 2026, (c) subject-blind for the 26
feed rows, and (d) biased toward teams whose matches attracted analysis
(finalists, England, big upsets). Silent checks that cleared a decision in a
small nation's group game are systematically missing; the same check in a
final is recorded. If the site shows "decisions in favour", it should either
restrict to overturns + formally rejected on-field reviews (the only class
recorded consistently across 2018/2022/2026), or carry the lower-bound /
selection-bias caveat verbatim next to the number.
