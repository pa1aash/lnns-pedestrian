# Venue requirements: Springer LNNS (checked 2026-11-07)

Sources (all paraphrased):
- Series page, read via Internet Archive snapshot 2026-09-15: https://link.springer.com/series/15179 . It describes LNNS as a proceedings and edited-volume series on networks and systems (ISSN 2367-3389). It gives no separate typesetting rules and points to Springer's general submission and book-policy pages.
- Proceedings guidelines (Archive snapshot 2026-06-13): https://www.springer.com/gp/computer-science/lncs/conference-proceedings-guidelines . Springer lists the LaTeX2e template under the LNCS/CCIS/LNBIP family; no LNNS-specific template is listed. Use the same llncs class.
- Instructions for proceedings authors (PDF): https://resource-cms.springernature.com/springer-cms/rest/v1/content/19242230/data/v17

Findings, relative to a plain LNCS paper:
1. No LNNS-specific class or template was found; llncs v2.24 (runningheads) is the one to use. If the volume editors give another template, theirs wins.
2. Corresponding author: exactly one, marked in the header; email mandatory; signs the licence to publish for all authors. The template has no dedicated marker, so a label in the institute block is used (open point, see below).
3. ORCID via \orcidID; emails of all authors recommended in the header.
4. Alt text is required for non-text content (EU Accessibility Act, WCAG). Either the programme chairs ask for it or typesetters write it and the corresponding author checks it at proof.
5. End matter: acknowledgments and a disclosure-of-interests statement, set with the credits environment in the template.
6. Citations: numbered, square brackets; splncs04 style.
7. Authorship (names, order, corresponding author) cannot change after delivery.
8. Extended versions: the guidelines state for journal extensions that at least 30% new material, a citation of the original and an explicit statement of the increment are needed. Not stated for LNNS, but the "Main Differences from the Conference Version" section covers the same ground. Also: no footnotes in the abstract; permission is needed for third-party figures and text.
9. Springer AI-use policy is linked from the instructions; wording of any disclosure is for the authors (change C5).
10. Page budget: the instructions call 12-15 pages typical for a full paper; the 23-25 page target comes from the invitation and should be confirmed with the volume editors.

Open points: confirm corresponding-author marking convention with the editors; confirm page limit.
