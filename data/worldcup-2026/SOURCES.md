# 2026 FIFA World Cup — Data Sources and Notes

Data compiled on **July 16, 2026**. Covers all **102 matches played so far** (of 104 scheduled).

## Tournament status as of July 16, 2026

- Group stage (72 matches), Round of 32 (16), Round of 16 (8), Quarterfinals (4) and Semifinals (2) are complete: **102 of 104 matches played**.
- Semifinal results: **France 0–2 Spain** (July 14, referee Iván Barton) and **England 1–2 Argentina** (July 15, referee Ismail Elfath).
- Remaining matches:
  - **Third-place match: France vs England** — July 18, 2026
  - **Final: Argentina vs Spain** — July 19, 2026, MetLife Stadium, East Rutherford, New Jersey
- Argentina (2022 champions) are attempting back-to-back titles; Spain seek their second World Cup.

## Sources used

### matches_2026.csv (all fields)

Match data (date, teams, scores, extra time, shootouts, referee name and country) was parsed
programmatically from the raw wikitext of the English Wikipedia articles below, retrieved via the
MediaWiki API (`https://en.wikipedia.org/w/api.php`) on July 16, 2026:

- https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_A (and Groups B, C, D, E, F, G, H, I, J, K, L — all 12 group articles fetched, 72 matches)
- https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_round_of_32 (16 matches; the knockout-stage article transcludes this page)
- https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_knockout_stage (Round of 16, Quarterfinals, Semifinals — 14 matches)
- https://en.wikipedia.org/wiki/2026_FIFA_World_Cup (tournament structure and status)

### team_stats_2026.csv

- `matches_played, wins, draws, losses, goals_for, goals_against`: computed arithmetically from the
  102 match results in `matches_2026.csv` (Wikipedia-sourced, above). Matches decided by penalty
  shootout are counted as **draws** for both teams (FIFA convention); matches decided in extra time
  count as wins/losses on the ET-inclusive score.
- `yellow_cards, red_cards, fouls_committed, fouls_drawn`: FBref "Squad Miscellaneous Stats" table
  (CrdY, CrdR, Fls, Fld columns), via the only available Wayback Machine snapshot:
  - https://web.archive.org/web/20260708125036/https://fbref.com/en/comps/1/2026/misc/2026-FIFA-World-Cup-Stats
  - (live page: https://fbref.com/en/comps/1/misc/World-Cup-Stats — returned HTTP 403 to every fetch method tried)
- `penalties_won, penalties_conceded`: **left blank** — see gaps below.

### Status confirmation and cross-checks

- ESPN public scoreboard API (independent cross-check of all 7 Argentina matches):
  `https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates=YYYYMMDD`
  for 20260616, 20260622, 20260627, 20260703, 20260707, 20260711, 20260715 — scores and
  extra-time flags agreed exactly with Wikipedia for all seven matches.
- Web search confirmation of semifinals/final: Yahoo Sports ("FIFA World Cup 2026 Semifinal: Spain
  Blanks France 2-0", https://sports.yahoo.com/articles/fifa-world-cup-2026-semifinal-235458083.html),
  FIFA match centre links, Al Jazeera (July 13-14, 2026 coverage of the semifinals).
- Narrative detail on Argentina's run comes from the Wikipedia match-report prose, which cites (among
  others): BBC Sport live pages, The Guardian match reports
  (e.g. https://www.theguardian.com/football/2026/jul/15/england-argentina-world-cup-semi-final-match-report),
  Sky Sports, and ESPN (e.g. https://www.espn.com.au/football/report/_/gameId/760513).

## Argentina's run (7 wins in 7 matches, 19 goals for / 7 against)

| Date | Stage | Result |
|---|---|---|
| Jun 16 | Group J | Argentina 3–0 Algeria |
| Jun 22 | Group J | Argentina 2–0 Austria |
| Jun 27 | Group J | Jordan 1–3 Argentina |
| Jul 3 | Round of 32 | Argentina 3–2 Cape Verde (a.e.t.) |
| Jul 7 | Round of 16 | Argentina 3–2 Egypt |
| Jul 11 | Quarterfinal | Argentina 3–1 Switzerland (a.e.t.) |
| Jul 15 | Semifinal | England 1–2 Argentina |

Notable items from the match reports:

- **Penalties won: 3, converted: 1.** Vs Austria (group stage, 8'), Messi fired the penalty wide after
  Stefan Posch fouled Lautaro Martínez. Vs Jordan (group stage), Lautaro Martínez converted a
  31st-minute penalty (per the Wikipedia match box goal annotation "La. Martínez 31' pen" and ESPN's
  match report, https://www.espn.com/soccer/report/_/gameId/760483). Vs Egypt (R16, 21'), Messi's
  penalty was saved by Mostafa Shobeir. No penalties conceded by Argentina were reported in any of
  their seven match reports, and ESPN's boxscores show 0 penalty attempts by all seven opponents.
- **Red cards: Argentina 0; opponents 1** — Breel Embolo (Switzerland) was sent off in the quarterfinal
  on a second yellow after VAR overturned a yellow card initially shown to Leandro Paredes under the
  "mistaken identity" protocol (the second such incident of the tournament). Note this red card is
  NOT in the team_stats discipline figures (it happened after the FBref snapshot date — see gaps).
- R32 vs debutants Cape Verde was a near-upset: 2–2 after 105 minutes, settled by a Diney Borges own
  goal (111') from a Messi corner.
- R16 vs Egypt: Argentina trailed 0–2, won 3–2 with Enzo Fernández's 93' header — the 3,000th goal in
  World Cup history.
- The quarterfinal ended Messi's record streak of scoring in nine consecutive World Cup matches
  (2022 R16 through 2026 R16; his 7th goal of this tournament came in the R32 per the match report).
- Semifinal controversy was mostly about England: Thomas Tuchel was widely criticized for a defensive
  switch after going 1–0 up (England had 12% possession from their goal until Lautaro Martínez's 90+2'
  winner, per ESPN). Post-match, some Argentine players displayed a "Las Malvinas son Argentinas"
  banner on the pitch (covered by The Guardian).

## Data gaps and caveats

1. **`penalties_won` / `penalties_conceded` are blank for all 48 teams.** FBref's PKwon/PKcon columns
   were empty for every squad in the only available snapshot, no archived FBref Squad Standard Stats
   (PKatt) or Goalkeeping page exists for July 2026, and the live FBref site is unreachable (HTTP 403).
   No other reliable per-team penalties table was found, so the columns were left blank rather than
   estimated.
2. **Discipline stats are frozen at July 8, 2026** (the single Wayback snapshot of the FBref page).
   They are complete through the Round of 16 (ended July 7) — i.e. final for the 40 teams eliminated
   by then — but for the 8 quarterfinalists (**France, Morocco, Spain, Belgium, Norway, England,
   Argentina, Switzerland**) the yellow_cards/red_cards/fouls figures EXCLUDE their quarterfinal and
   semifinal matches (6 matches total). Example: Embolo's QF red card is missing from Switzerland's
   red_cards value.
3. Within the snapshot's coverage no team had a second-yellow dismissal (FBref 2CrdY = 0 for all
   squads), so `red_cards` = straight red cards with no ambiguity.
4. A consistency check confirmed FBref's minutes-played (90s) matched the computed matches_played for
   all 40 teams whose tournaments ended by the snapshot date; South Africa's 2 red cards and Mexico's 1
   from the opening match also match the Wikipedia match report.
5. `home_team` is the first-listed team in Wikipedia's match box (nominal designation — hosts
   Mexico/USA/Canada aside, there is no true home side).
6. Match dates are the local dates given by Wikipedia's match templates.
7. Team names were normalized to Wikipedia conventions in both CSVs; FBref names mapped as:
   Türkiye→Turkey, Korea Republic→South Korea, IR Iran→Iran, Cabo Verde→Cape Verde,
   Congo DR→DR Congo, Côte d'Ivoire→Ivory Coast, Czechia→Czech Republic,
   Bosnia–Herz→Bosnia and Herzegovina. Both files use identical spellings for all 48 teams (verified).
8. Ivory Coast vs Ecuador (Group E): Michael Oliver was originally appointed but withdrew injured;
   the CSV lists the actual match referee, François Letexier (France).
9. The third-place match (Jul 18) and final (Jul 19) are excluded from both CSVs as unplayed at
   compile time.

## Patch file: qfsf_cards_2026.csv

To close gap #2 above, `qfsf_cards_2026.csv` (12 rows: one per team per match) provides per-match
yellow cards, red cards, and fouls committed for the 6 matches missing from the FBref snapshot —
the 4 quarterfinals (France 2–0 Morocco, Spain 2–1 Belgium, Norway 1–2 England, Argentina 3–1
Switzerland) and 2 semifinals (France 0–2 Spain, England 1–2 Argentina). Data was fetched from the
ESPN match-summary API (`https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/summary?event=760510`
… `760515`; per-row source_url in the file). Sanity check: ESPN shows 1 red card for Switzerland in
the Argentina quarterfinal, matching Embolo's sending-off in the Wikipedia match report. Caveats:
ESPN's foul counts come from a different data provider than FBref's, so summing the two sources may
not be perfectly consistent with how FBref would have counted; fouls drawn is not published
per-match by ESPN and is omitted from the patch file. Team names use the same canonical spellings
as the other CSVs (verified).

## Patch file: argentina_matches_cards_2026.csv

Per-match discipline for all seven Argentina matches (14 rows: Argentina and the opponent in each
match), fetched from the same ESPN match-summary API (event IDs 760433, 760456, 760483, 760500,
760509, 760513, 760515; per-row source_url in the file). Columns: yellow cards, red cards, fouls
committed, and `penalties_awarded` = in-game penalty kicks taken by that team in that match (ESPN's
`penaltyKickShots`; shootout kicks are not involved — none of Argentina's matches went to a
shootout). The three Argentina penalties (vs Austria, Jordan, Egypt) were each cross-verified
against the Wikipedia match reports; all opponents had zero. Caveats: a penalty awarded but
rescinded before being taken would not appear in this count; ESPN's companion `penaltyKickGoals`
field was found to be unreliable (it shows 0 for the Jordan match despite Lautaro Martínez's
converted 31' penalty, confirmed by Wikipedia's goal annotation and ESPN's own written match
report) and was therefore not used.
