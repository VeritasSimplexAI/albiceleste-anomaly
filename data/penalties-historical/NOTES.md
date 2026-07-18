# In-game penalties awarded at the World Cups of 1990–2010 — sources & verification notes

Compiled 2026-07-16. Covers every in-game penalty kick AWARDED (scored, missed or saved)
at the 1990, 1994, 1998, 2002, 2006 and 2010 FIFA Men's World Cups.
**Penalty-shootout kicks are excluded.**

Companion file: `penalties_awarded_1990_2010.csv` (101 rows).

## Sources used (all fetched during compilation)

Primary (per-match detail, one file per tournament):
- RSSSF full match details: https://www.rsssf.org/tables/90full.html, .../94full.html,
  .../98full.html, .../2002full.html, .../2006full.html, .../2010full.html
  (penalty goals are flagged in goal lines; missed/saved penalties appear in match notes,
  except in the 1994 and 2006 files — see below).

Independent per-match cross-check:
- Linguasport final-stage files (site currently unreachable; fetched via Wayback Machine):
  - 1990: https://web.archive.org/web/20170629000323/http://www.linguasport.com/futbol/internacional/mundial/1990_ITALY_FS.htm
  - 1994: https://web.archive.org/web/20170629000341/http://www.linguasport.com/futbol/internacional/mundial/1994_USA_FS.htm
  - 1998: https://web.archive.org/web/20170607054522/http://www.linguasport.com/futbol/internacional/mundial/1998_FRANCE_FS.htm
  - 2002: https://web.archive.org/web/20170606060244/http://www.linguasport.com/futbol/internacional/mundial/2002_KJ_FS.htm
  - 2006: https://web.archive.org/web/20170707062417/http://www.linguasport.com/futbol/internacional/mundial/2006_GERMANY_FS.htm
  - 2010: https://web.archive.org/web/20140623132830/http://www.linguasport.com/futbol/internacional/mundial/2010_SA_FS.htm
  (penalty goals marked "[p.]"; missed/saved penalties listed in "[Incidents: ...]" notes).

Aggregate cross-checks:
- Kaggle "FIFA World Cup Penalties Awarded" (data collected from Linguasport; in-game only):
  https://www.kaggle.com/datasets/ogakulov/world-cup-penalties-awarded
- SportsHistori per-tournament penalty-goals table:
  https://www.sportshistori.com/2022/11/total-no-of-goals-penalty-scored-at-every-fifa-world-cups-since-1930.html
- FBref 2006 squad/player PK data (scored penalties only for these years):
  https://fbref.com/en/comps/1/2006/stats/2006-World-Cup-Stats
- Statbunker "Penalties awarded" (2010: https://www.statbunker.com/competitions/ForPenalty?comp_id=306) —
  usable for 2010 only; pre-2010 pages are badly incomplete (e.g. 1994 shows only 7 of 15, 2006 only 5 of 17).

Individual corroboration of the four 2006 misses (absent from RSSSF match pages):
- Gyan v Czech Republic (66'): Wikipedia "2006 FIFA World Cup Group E"; Linguasport incidents note.
- Srna v Japan (21'/22', saved by Kawaguchi): Taipei Times report
  https://www.taipeitimes.com/News/sport/archives/2006/06/20/2003314662; Linguasport.
- Bravo v Portugal (57', over the bar): NPR match report
  https://www.npr.org/2006/06/21/5501277/mexico-in-round-of-16-despite-loss-to-portugal; Linguasport.
- Larsson v Germany (53', over the bar): Wikipedia "2006 FIFA World Cup knockout stage"; Linguasport.

## Per-tournament totals (this dataset vs sources)

| Tournament | Awarded (this file) | Converted | RSSSF | Linguasport | Kaggle (Linguasport agg.) | SportsHistori (scored) |
|-----------:|:-------------------:|:---------:|:-----:|:-----------:|:-------------------------:|:----------------------:|
| 1990       | 18                  | 13        | 18 (13+5) | 18 (13+5) | 18 / 13 scored           | 13 ✓ |
| 1994       | 15                  | 15        | 15 (15+0) | 15 (15+0) | 15 / 15 scored           | 15 ✓ |
| 1998       | 18                  | 17        | 18 (17+1) | 18 (17+1) | 18 / 17 scored           | 17 ✓ |
| 2002       | 18                  | 13        | 18 (13+5) | 18 (13+5) | 18 / 13 scored           | 13 ✓ |
| 2006       | **17**              | 13        | match pages: 13 scored, 0 misses noted; stats block says "Penalties: 16" | 17 (13+4) | 17 / 13 scored | 13 ✓ |
| 2010       | **15**              | 9         | 15 (9+6)  | 15 (9+6)  | **14** / 9 scored        | 9 ✓ |
| **Total**  | **101**             | **80**    |       |             |                           |      |

2002's 18 is also consistent with the widely reported line that 2018's 29 penalties
surpassed "the previous record of 18 set in 2002".

## Coverage assessment

- **Complete for all six tournaments.** Every row was verified in at least two independently
  compiled per-match sources (RSSSF + Linguasport), except the four 2006 misses, which are
  absent from RSSSF's match pages but confirmed by Linguasport plus a third source each
  (Wikipedia / NPR / Taipei Times, listed above).
- Scored-penalty counts for all six tournaments independently match SportsHistori's table,
  and (for 2006) FBref's PK data row-by-row (same 13 takers/teams).

## Source disagreements (documented, not silently resolved)

1. **2006 total: 16 vs 17.** RSSSF's own statistics block says "Penalties: 16", but four
   individually documented misses exist (Gyan, Srna, Bravo, Larsson) on top of 13 scored.
   Linguasport (per match), Kaggle (17) and per-match press reports support 17.
   **Adopted: 17.** RSSSF's 16 appears to be an undercount (its match pages record no
   2006 misses at all, so the 16 was not derived from them consistently).
2. **2010 total: 14 vs 15.** Kaggle's aggregate says 14 (9+3+2), but its own source
   (Linguasport) documents six misses per match, as does RSSSF: Podolski, Tomasson, Villa,
   Gyan, and BOTH Cardozo and Xabi Alonso in the same Paraguay–Spain quarter-final.
   The aggregate appears to have counted that double-penalty match once. Statbunker also
   shows 14, but with a different omission (it lists both Spain–Paraguay penalties and
   drops Podolski's). **Adopted: 15** (RSSSF and Linguasport agree event-by-event).
3. **Minute discrepancies** between RSSSF and Linguasport for a handful of kicks
   (e.g. Vialli 1990: 20' vs 32'; Djorkaeff 1998: 23' vs 12'; Harte 2002: 62' vs 69';
   Srna 2006: 22' vs 21' in Taipei Times). Minutes are therefore not included in the CSV.
4. **RSSSF 1990 date typos:** the third-place match (Italy–England) is dated "07.06.90"
   in the RSSSF file; the correct date, 1990-07-07, is used (per Linguasport). The RSSSF
   1990 file also mislabels the Czechoslovakia–Austria date line "15.06.94" (game was
   15 June 1990).

## Retaken / rebound penalties (counted once each, by final outcome)

- Šuker (CRO v ROM, 1998): retaken, scored → converted = yes.
- Dindane (CIV v SCG, 2006): retaken, scored → yes.
- Gyan (GHA v CZE, 2006): scored the first attempt, referee ordered a retake, retake missed → **no**.
- Xabi Alonso (ESP v PAR, 2010): scored the first attempt, retake ordered for encroachment,
  retake saved by Villar → **no**.
- Tomasson (DEN v JPN, 2010): kick saved by Kawashima, Tomasson scored the rebound.
  The penalty itself counts as not converted (the rebound goal is not a penalty goal) → **no**.

## Argentina: awarded for / against (in-game only)

| Tournament | For (converted) | Against (converted) | Detail |
|-----------:|:---------------:|:-------------------:|:-------|
| 1990 | 0 (0) | 1 (1) | conceded: Brehme 85', Final v West Germany |
| 1994 | 2 (2) | 0 (0) | Batistuta v Greece; Batistuta v Romania |
| 1998 | 2 (2) | 1 (1) | Batistuta v Jamaica; Batistuta v England; conceded: Shearer (England) |
| 2002 | 1 (0) | 1 (1) | Ortega saved by Hedman v Sweden (Crespo scored the rebound — not a penalty goal); conceded: Beckham (England) |
| 2006 | 0 (0) | 0 (0) | (Germany QF decided on shootout — excluded) |
| 2010 | 0 (0) | 0 (0) | |

This is fully consistent with the project's independent anchors: Argentina converted
2 in 1994, 2 in 1998, 0 in 2002/2006/2010; conceded converted penalties in 1990 (1),
1998 (1), 2002 (1). No mismatches found.

## Naming conventions

- Historical team names as of the tournament: West Germany (1990), Soviet Union (1990),
  Czechoslovakia (1990), Yugoslavia (1990 and 1998), Serbia and Montenegro (2006), Serbia (2010).
- Takers are given as named in the sources: surnames only for 1990–1998 (RSSSF/Linguasport
  list surnames), full names for 2002–2010 where the RSSSF files provide them.

---

# 1930–1986: In-game penalties awarded — sources & verification notes

Compiled 2026-07-16 with the same method as the 1990–2010 section. Covers every in-game
penalty kick AWARDED (scored, missed or saved) at the 13 FIFA Men's World Cups from
1930 to 1986. **Penalty-shootout kicks are excluded** (1982 GER–FRA SF, 1986 FRA–BRA,
GER–MEX and BEL–ESP QFs all went to shootouts — none of those kicks are counted).

Companion file: `penalties_awarded_1930_1986.csv` (104 rows).

## Sources used (all fetched during compilation)

Primary (per-match detail, one file per tournament):
- RSSSF full match details: https://www.rsssf.org/tables/30full.html, .../34full.html,
  .../38full.html, .../50full.html, .../54full.html, .../58full.html, .../62full.html,
  .../66full.html, .../70full.html, .../74full.html, .../78full.html, .../82full.html,
  .../86full.html. Penalty goals are flagged "p" in the goal lines; missed/saved
  penalties appear in parenthetical match notes. Each file's own statistics block
  ("In total N goals (x p, ...)") was used as an internal consistency check on the
  converted counts — all 13 agree with this dataset.

Independent per-match cross-check (Linguasport final-stage files via Wayback Machine;
penalty goals marked "[p.]", misses in "[Incidents: ...]" notes):
- 1930: https://web.archive.org/web/20120626030433/http://www.linguasport.com/futbol/internacional/mundial/1930_URUGUAY_FS.htm
- 1934: https://web.archive.org/web/20140202180109/http://www.linguasport.com/futbol/internacional/mundial/1934_ITALY_FS.htm
- 1938: https://web.archive.org/web/20160304115136/http://www.linguasport.com/futbol/internacional/mundial/1938_FRANCE_FS.htm
- 1950: https://web.archive.org/web/20161007184737/http://www.linguasport.com/futbol/internacional/mundial/1950_BRAZIL_FS.htm
- 1954: https://web.archive.org/web/20170629050715/http://www.linguasport.com/futbol/internacional/mundial/1954_SWITZERLAND_FS.htm
- 1958: https://web.archive.org/web/20170628232729/http://www.linguasport.com/futbol/internacional/mundial/1958_SWEDEN_FS.htm
- 1962: https://web.archive.org/web/20170509015505/http://www.linguasport.com/futbol/internacional/mundial/1962_CHILE_FS.htm
- 1966: https://web.archive.org/web/20170629045304/http://www.linguasport.com/futbol/internacional/mundial/1966_ENGLAND_FS.htm
- 1970: https://web.archive.org/web/20170629050751/http://www.linguasport.com/futbol/internacional/mundial/1970_MEXICO_FS.htm
- 1974: https://web.archive.org/web/20170628235639/http://www.linguasport.com/futbol/internacional/mundial/1974_FRG_FS.htm
- 1978: https://web.archive.org/web/20170412101911/http://www.linguasport.com/futbol/internacional/mundial/1978_ARGENTINA_FS.htm
- 1982: https://web.archive.org/web/20170405011540/http://www.linguasport.com/futbol/internacional/mundial/1982_SPAIN_FS.htm
- 1986: https://web.archive.org/web/20160409222149/http://www.linguasport.com/futbol/internacional/mundial/1986_MEXICO_FS.htm

Aggregate cross-checks:
- The project's independent academic anchors (converted in-game penalties per tournament):
  1930:1, 1934:3, 1938:3, 1950:3, 1954:7, 1958:7, 1962:8, 1966:8, 1970:5, 1974:6,
  1978:12, 1982:8, 1986:12 — **all 13 match this dataset exactly; no mismatches.**
- SportsHistori per-tournament penalty-goals table (same page as used for 1990–2010):
  identical figures for all 13 tournaments.

Individual corroboration of disputed items (all fetched):
- 1930 Chile–France taker (Vidal): Wikipedia "1930 FIFA World Cup Group 1" and
  topendsports "World Cup Football Firsts" (first WC penalty save: Thépot from Carlos
  Vidal, 30'); soccernostalgia.blogspot.com "Compendium to the 1930 World Cup, part 2"
  gives "Saavedra (or Carlos Vidal)".
- 1930 Brazil–Bolivia miss (Sáinz): soccernostalgia "World Cup Stories, part 1 (1930)"
  ("According to some sources, Brazil goalkeeper Velloso saved a penalty kick ...
  Though some claim this is unconfirmed").
- 1950 Chile–USA taker (Maca): Wikipedia "1950 FIFA World Cup Group 2"
  (Wallace 47', Maca 48' pen.).
- 1954 Austria–Switzerland miss (Alfred Körner): Wikipedia
  "Austria v Switzerland (1954 FIFA World Cup)" (explicitly Alfred, not Robert).
- 1962 Brazil–England non-penalty (excluded row, see disagreements): Wikipedia
  "1962 FIFA World Cup knockout stage", historicalkits.co.uk 1962 knockout page,
  englandstats.com match 362, thehardtackle.com match retrospective.

## Per-tournament totals (this dataset)

| Tournament | Awarded | Converted | Missed/saved | RSSSF stats block ("x p") | Anchor | Linguasport |
|-----------:|:-------:|:---------:|:------------:|:-------------------------:|:------:|:-----------:|
| 1930 | 5  | 1  | 4 | 1 p ✓ | 1 ✓  | agrees + 1 extra miss (see below) |
| 1934 | 4  | 3  | 1 | 3 p ✓ | 3 ✓  | agrees event-for-event |
| 1938 | 5  | 3  | 2 | 3 p ✓ | 3 ✓  | agrees event-for-event |
| 1950 | 3  | 3  | 0 | 3 p ✓ | 3 ✓  | agrees event-for-event |
| 1954 | 8  | 7  | 1 | 7 p ✓ | 7 ✓  | agrees event-for-event |
| 1958 | 10 | 7  | 3 | 7 p ✓ | 7 ✓  | agrees event-for-event |
| 1962 | 8  | 8  | 0 | 8 p ✓ | 8 ✓  | agrees; RSSSF has 1 extra miss, rejected (see below) |
| 1966 | 8  | 8  | 0 | 8 p ✓ | 8 ✓  | agrees event-for-event |
| 1970 | 5  | 5  | 0 | 5 p ✓ | 5 ✓  | agrees event-for-event |
| 1974 | 8  | 6  | 2 | 6 p ✓ | 6 ✓  | agrees event-for-event |
| 1978 | 14 | 12 | 2 | 12 p ✓ | 12 ✓ | agrees event-for-event |
| 1982 | 10 | 8  | 2 | 8 p ✓ | 8 ✓  | agrees event-for-event |
| 1986 | 16 | 12 | 4 | 12 p ✓ | 12 ✓ | agrees event-for-event |
| **Total** | **104** | **83** | **21** | | | |

## Coverage assessment (graded honestly per tournament)

Converted penalties: **grade A for all 13 tournaments** — every scored penalty was
verified in both RSSSF and Linguasport, matches RSSSF's own per-tournament statistics
blocks, the academic anchors, and SportsHistori.

Missed/saved penalties (the fragile part for old tournaments):
- **1930 — C+.** Four misses recorded. Three are in both sources; the Bolivia miss
  (Sáinz v Brazil, saved by Velloso) is in Linguasport only, with soccernostalgia
  calling it "unconfirmed" — that row is included but should be treated as uncertain.
  The Chile–France taker is disputed (see below). Additional unrecorded misses from
  1930 cannot be ruled out.
- **1934, 1938 — B.** The single 1934 miss and both 1938 misses appear independently
  in both per-match sources. Records of this era are thin, so completeness of the
  missed-penalty record is plausible but not provable.
- **1950 — C.** Zero misses recorded by either source (or by Wikipedia's match pages).
  Genuine absence is plausible for a 22-match tournament, but a missed penalty escaping
  both compilers cannot be excluded.
- **1954, 1958 — B+.** Misses (1 and 3 respectively) agree event-for-event across both
  sources, including takers, opponents and save details.
- **1962, 1966, 1970 — B-.** No misses recorded in Linguasport for any of the three
  (RSSSF's lone 1962 miss claim was rejected — see disagreements). Zero missed penalties
  across three whole tournaments (89+89+95 goals) is possible but slightly suspicious;
  treat "0 missed" as a floor, not a certainty.
- **1974, 1978, 1982, 1986 — A-.** Detailed era: misses agree event-for-event in both
  sources (takers, saving keepers, minutes), and the well-known events (Tomaszewski's
  two 1974 saves, Cabrini's 1982 final miss, Zico's 1986 QF miss) are all present.

## Source disagreements (documented, not silently resolved)

1. **1962 Brazil–England QF, alleged Garrincha penalty saved by Springett (66').**
   RSSSF's match note says "(66 Springett saved a penalty by Garrincha)". No other
   source supports this: Linguasport describes the same moment as Springett saving a
   long-range Garrincha *shot* ("a top drawer save to deny his long-range effort"),
   and Wikipedia, historicalkits, englandstats.com (England match database) and a
   detailed match retrospective all record no penalty in the match. **Row EXCLUDED**
   — RSSSF-only claim contradicted by the second primary source. (The only web echo
   found was an AI-generated wiki, likely derived from RSSSF itself.)
2. **1930 Chile–France missed penalty taker.** RSSSF: Saavedra; Linguasport, Wikipedia
   and topendsports: Carlos Vidal (30', saved by Thépot — the first penalty, and first
   penalty save, in World Cup history); soccernostalgia lists both. **Adopted: Vidal.**
3. **1930 Brazil–Bolivia missed penalty (Sáinz, saved by Velloso, 0-0 at the time).**
   In Linguasport (incidents note + match summary) but absent from RSSSF;
   soccernostalgia reports it as claimed-but-unconfirmed. **Included, flagged uncertain.**
4. **1950 Chile–USA penalty taker.** RSSSF: "J.Sousa 49 p" (John Souza); Linguasport:
   "Maca [p.] 48'" — supported by Wikipedia/FIFA records (Wallace 47', Maca 48' pen).
   The two sources disagree on the whole USA goal sequence. **Adopted: Maca.**
5. **1954 Austria–Switzerland missed penalty (42').** RSSSF: A.Körner (Alfred);
   Linguasport: "Robert Körner". Wikipedia's dedicated match page explicitly states
   Alfred (not his brother Robert). **Adopted: A.Körner.**
6. **1934 Brazil taker naming.** RSSSF "Brito" and Linguasport "Waldemar" are the same
   player, Waldemar de Brito (penalty saved by Zamora; RSSSF 62', Linguasport 70').
7. **RSSSF date errors (all corrected from Linguasport, plus Wikipedia where noted):**
   - 1950 Yugoslavia–Mexico: RSSSF 29.06.50 → **1950-06-28** (Linguasport + Wikipedia).
   - 1950 Brazil–Sweden (final round): RSSSF 03.07.50 → **1950-07-09** (Linguasport;
     the final pool only began 9 July).
   - 1958 third-place France–West Germany: RSSSF 26.06.58 → **1958-06-28**.
   - 1962 Hungary–England: RSSSF "31.06.62" (non-existent date) → **1962-05-31**.
   - 1966 third-place Portugal–Soviet Union: RSSSF "28.07.70" → **1966-07-28**.
   - 1982 Yugoslavia–Honduras: RSSSF "24.06.98" → **1982-06-24**.
8. **Minute discrepancies** between RSSSF and Linguasport for many kicks (e.g. M.Rosas
   1930: 42' vs 37'; Waldemar de Brito 1934: 62' vs 70'; Patesko 1938: 78' vs 48';
   Andersson 1950: 57' vs 67'; Hewie 1958: 23' vs 28'; Krankl 1978: 42' vs 44').
   Minutes are therefore not included in the CSV, consistent with the 1990–2010 file.
9. **Name spellings.** RSSSF "Howie" (1958 Scotland) is John Hewie → "Hewie" used;
   RSSSF "Patesco" / Linguasport "Patesko" → "Patesko"; RSSSF "Vásquez-Ayala" /
   Linguasport "Vázquez Ayala" → "Vázquez Ayala"; RSSSF "Amoros" → "Amorós";
   RSSSF "Evtushenko"/"Yevtushenko" variants → "Yevtushenko".

## Retaken / rebound penalties (counted once each, by final outcome)

- M.Rosas (MEX v ARG, 1930, 2nd penalty): saved by Bossio, Rosas scored the rebound.
  The penalty itself counts as not converted (the rebound goal is not a penalty goal) → **no**.
- Liedholm (SWE v MEX, 1958): first kick ordered retaken, retake scored → **yes**.
- Juanito (ESP v JUG, 1982): López Ufarte took the first kick and missed; the referee
  ordered a retake (Pantelić moved early); Juanito converted the retake. One penalty
  awarded → **yes**, taker recorded as Juanito (the successful retaker).
- Peña (MEX v BEL, 1970): not a retake, but FIFA times the goal at 14' while the kick
  was actually taken at ~16' after Belgian protests (Linguasport note).

## Argentina: awarded for / against (in-game only), 1930–1986

| Tournament | For (converted) | Against (converted) | Detail |
|-----------:|:---------------:|:-------------------:|:-------|
| 1930 | 1 (0) | 2 (1) | Paternoster saved by Bonfiglio (v Mexico); conceded: M.Rosas scored 42' + M.Rosas saved by Bossio (both v Mexico, 19 July) |
| 1934 | 0 (0) | 0 (0) | (eliminated by Sweden in the only match; no penalties) |
| 1958 | 2 (2) | 0 (0) | Corbatta v Northern Ireland; Corbatta v Czechoslovakia |
| 1962 | 0 (0) | 1 (1) | conceded: Flowers (England) |
| 1966 | 0 (0) | 0 (0) | |
| 1974 | 0 (0) | 0 (0) | |
| 1978 | 1 (1) | 1 (0) | Passarella v France; conceded: Deyna saved by Fillol (v Poland, 2nd round) |
| 1982 | 1 (1) | 0 (0) | Passarella v El Salvador |
| 1986 | 0 (0) | 1 (1) | conceded: Altobelli (Italy, group stage) |

(Argentina did not enter/appear in 1938, 1950, 1954 and did not qualify in 1970.)
This matches the project's independent anchors exactly: Argentina converted 2 in 1958,
1 in 1978, 1 in 1982 and **0 in 1986** (the anchor's 1986 total of 12 contains no
Argentina penalty; Maradona never took an in-game World Cup penalty in 1986 —
the only penalty in an Argentina match that year was Altobelli's against them).

## Naming conventions (1930–1986 file)

- Team names follow the fjelstul dataset conventions and the historical names of the
  time: West Germany (1954–1986), Soviet Union, Czechoslovakia, Yugoslavia,
  United States, North Korea, South Korea, El Salvador, Northern Ireland.
- Stages: official numbered groups ("Group 1"–"Group 6") for 1930–1982 first rounds
  (RSSSF's files letter them A–D/E, which was mapped back to the official numbers);
  lettered groups ("Group A"–"Group F") for 1986; "Round of 16" for the 1934/1938
  knockout first round and the 1986 knockout round; "Second round Group A/B" for the
  1974/1978 second group phases; "Final round" for the 1950 deciding pool; otherwise
  "Quarter-final", "Semi-final", "Third place", "Final" as in the 1990–2010 file.
- Takers are given as named in the sources (surnames, with initials where the sources
  use them to disambiguate, e.g. M.Rosas, A.Körner, F.Walter, A.Tóth, H.Hernández,
  L.Sánchez, J.Olsen).
