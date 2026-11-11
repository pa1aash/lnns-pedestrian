# Fix log: Sects. 7-10 and back matter (07, 08, 085, 09, 10; registry p_end.yaml)

Applied: prose 13-2, 7-6, 9-5, 9-6, 4-11 (moved to Limitations), 15-3 and 15-8 (Sect. 7), 13-8 in part, 3-1, 14-5, 16-14 (08:7),
4-12 (08 part), 5-6 (interval stated by macros), 5-9, 4-3 (08 part), 12-6, 12-7, 12-15 (08), 12-17 (085), 10-8, 15-2, 14-2 (ratio once in
Sect. 7, once in Conclusions; per-variant ratio values dropped from Sect. 7), 14-6, 1-6, 1-7 (with the brief's qualifier), 10-9;
numbers.md 07:21 (mean over the 15 censored runs), 07:23 (literal 100 replaced by \PendModelFlowMax), 07:19/23/25 two-figure items;
P_RESOLUTION disputes 7 (8.1 no longer claims each surrogate is separated), 12 (Limitations: arch searches below 5 m/s at dt = 0.01 s),
13 (scoped to the five CroMa runs), 14 (qualifier "uncalibrated default parameters" in Sect. 7 and Conclusions), 15 ("tracked"
participants; `\;` removed), 23 / F-13 (hoogendoorn2005, seyfried2009: measured bottleneck flow grows with width, verified against
the Crossref abstracts: stepwise in Hoogendoorn and Daamen, linear in Seyfried et al.).

## Declined
- prose 1-4, 10-7, 16-5 (07:25 "passes ... realistic"): the brief fixes the headline wording; kept verbatim.
- prose 16-5 (09:2 "passes"): kept for agreement with the Sect. 7 headline the brief prescribes.
- numbers.md 07:25 gap maxima "at most" 20.4/15.6/237.2 -> 21/16/240: make_numbers.py has no ceiling format; the one-decimal values are valid upper bounds.
- prose 13-8 "446 -> 450", "416/432 -> 420/430": no rounding-to-2-sf format for values >= 100; the lower bounds use one decimal (415.9, 431.8) so they stay below the true bound, as the task asked.
- numbers.md 07:19 EtenHumanGapMax 2.04 -> 2.0: it is compared with 2 s ("1 gap exceeds 2 s"); 2.0 would contradict that (prose 13-8 keeps it too).
- numbers.md RevBtwoWfifty (09:2): three figures resolve the interval and match Sects. 1 and 5; the exception belongs in Sect. 4.4 (another writer).
- C11 per-run CroMa table: left out under the page limit, as instructed.
- prose 11-1 (back matter `\pending` DOI, acknowledgements, disclosure): author-only content; the DOI is not minted.
- prose 11-2 (back-matter half: add hashes, tag, file path): conditional on the Sect. 6 writer moving them out of 06:26; not done to avoid duplication.
- prose 15-1 (`\ackname`): main.tex is not mine.
- compliance B1 ("attempt rate" -> "attempt frequency" at 08:7): advisory; the term stays as in Sects. 2, 5, 6 for one name per concept.
- compliance B5 (CroMa run IDs): published dataset names, needed for attribution; kept.
- P_RESOLUTION dispute 15, second half (archive registers 161/160/132/132/129): would add numbers and words; "tracked" scopes the claim.
