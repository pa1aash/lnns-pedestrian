# Prose audit prompt (paste above any manuscript)

You are auditing the prose of an academic paper. Read the whole manuscript, main text and appendix, and return an exhaustive list of writing and framing defects with a specific fix for each one.

Ignore any submission checklist, reviewer form, or declaration section. Do not evaluate the science, the method, or whether the results are correct. Judge only the writing.

---

## Output rules

Read these first; they govern everything below.

**Be exhaustive, not illustrative.** For every category, list every instance you find. Never write "e.g.", "and similar", "several other cases", or "throughout". If a construction appears eleven times, list eleven entries. A category with many instances is the most useful output you can produce, because a single example lets the author fix one line and believe the problem is solved.

**Anchor every entry.** Give the line number or section, the exact text quoted, and the replacement text. Not a description of the fix — the replacement, written out. If the fix is deletion, say delete and say why the sentence is not load-bearing.

**Group by defect type**, using the categories below, in that order. Within a category use a table when entries are short and a list when each needs a sentence of reasoning.

**Do not rewrite the paper.** No clean version, no full rewritten sections. The author fixes their own manuscript; you locate the defects.

**Do not soften.** If a paragraph is the worst-written in the paper, say so and say which one it competes with. If a device is a tic, name it a tic and count it. Rank severity where it helps triage.

**Separate taste from error.** Mark any entry that is a stylistic preference rather than a defect, and say what the competing convention is.

**Preserve the author's voice.** Fixes should sound like the author's own registers with the defect removed, not like generic academic filler. Never replace a specific claim with a vaguer one to make a sentence smoother.

---

## Categories to audit

### 1. Rhetorical negation

Find every "not X, but Y" and every variant: "not merely X", "X rather than Y" used rhetorically, "not A, not B, but C", bookended negation, and cascades of consecutive rule-outs.

The fix is always the same shape. State Y. If X genuinely needs ruling out, rule it out in its own sentence with a reason and a number.

Flag separately any place where three or more consecutive sentences rule out alternatives before the claim itself appears. Also flag mirrored pairs — the same distinction stated in both directions in different parts of the paper ("a property of the estimator, not the matrix" in one place, "a property of the matrix, not the estimator" in another).

Keep genuine technical contrasts where the contrast carries information ("conservatively rather than exactly" for a type-I error claim). Say which ones you are keeping and why.

### 2. Sentences that announce their own significance

"It is worth noting", "it is important to", "it is worth pausing", "crucially", "notably", "significantly", "the key point is", "what matters here is". Delete the announcement and keep the claim.

### 3. Sentences that announce what a section will do

Roadmap sentences, forward pointers, and openings that summarize the paragraphs beneath them. "This section builds X, then Y." "Section 4 shows what happens when the assumption is dropped." "Table 1 collects the findings."

Just build X. Delete the announcement.

Flag any paragraph whose entire content is restated in the paragraphs following it — a common failure at the opening of a results section, where an abstract-shaped summary precedes the actual results. Say which sentences in it are unique and should survive.

### 4. Trailing appositive qualifications

Clauses tacked onto the end of a sentence, set off by a comma, that qualify, hedge, confess, or editorialize: ", work this paper has not done", ", the question this paper asks instead", ", a stated design limitation", ", as the only simplification".

Promote to its own sentence, move to the limitations section, or delete. Say which.

Flag dangling modifiers in this pattern, where the trailing clause grammatically attaches to the wrong noun.

### 5. Softening adverbs on binary claims

arguably, somewhat, fairly, rather, quite, perhaps, seemingly, essentially, virtually, largely, generally, typically, usually, roughly, comfortably, clearly, actually, exactly, almost, nearly, real/really, relatively, effectively, particularly.

The claim is either true or it is not. Delete, or replace with the number that justifies the hedge.

Flag internally contradictory pairs, such as "almost exactly" or "essentially always".

Flag any adverb doing argumentative work with no definition behind it — "a realistic neighborhood", "a natural construction", "a reasonable choice" — and ask what defines it.

### 6. Sentences beginning with "What"

"What this shows is X" becomes "This shows X". "What the test delivers is the global null" becomes "The test delivers the global null". Rephrase every one.

Apply the same treatment to other cleft and expletive constructions used for emphasis: "It is X that...", "There is X which...", "The thing that matters is...".

### 7. Headers and bold paragraph leads

Section headings, subsection headings, and bold run-in leads should name their content, not narrate or editorialize.

Flag:
- Headings that read as essay titles or arguments ("Where exact conditional attribution becomes unaffordable, and why")
- Headings that list three topics joined by commas and "and"
- Suffixes like ", in full", ", revisited", ", in detail"
- Paired rhetorical devices across headings ("Where X is true" / "Where it is not") — these read as clever and defeat scanning
- Headings stating two results at once
- Headings that a reader scanning the contents page cannot use to find anything

Give a replacement heading for each.

### 8. Figure and table captions

Cap at three sentences. A caption states what is plotted and how to read it.

Flag every caption that:
- Exceeds three sentences or roughly sixty words
- Repeats a claim already made in the body text, verbatim or in substance
- Argues, interprets, or justifies a design decision
- Contains a specification (design grid, threshold definition, plotting convention) that belongs in the method section
- Contains a measurement or result that appears nowhere else in the paper — this is the dangerous case; say so explicitly and say where it should move

For each caption give the sentences to cut and where their content already lives, or where it should move.

### 9. Run-on and over-nested sentences

Flag every sentence with four or more comma-joined clauses, nested parentheticals, or a parenthetical inside a clause inside a parenthetical.

Name the worst sentence in the paper explicitly. Show the split.

Also flag comma splices presented as lists of results, where three or four independent findings are joined by commas into one sentence.

### 10. Aphoristic paragraph endings

Short gnomic closing sentences aiming for quotability: "the contribution is the finding", "that is one point, not a distribution", "and nothing further".

Individually fine. Count them. Above two or three per paper they establish a voice that reads as overclaiming. Say which single one earns its place and convert the rest to ordinary sentences.

### 11. Process-record and internal-code leakage

Language that belongs to the project's construction rather than the paper:

- Internal tracking labels (C1, C2, L1, B1, phase names, run IDs) used as headings without explanation
- Source-code constants, variable names, or file paths in running prose
- Narrated belief revision: "contradicting our earlier claim", "originally we thought", "as first declared"
- Unspecifiable references: "this study's budget", "our internal threshold", "the earlier session"
- Pre-registration assertions phrased as narrative rather than fact ("fixed before any measurement existed")
- Confessional asides about process that the reader cannot verify or use

Say what each should become, or that it should be deleted.

### 12. Terminology and notation drift

Build a table of every concept called by more than one name. For each, list all the names used, where each appears, and recommend one.

Check specifically:
- The same object or verdict under two vocabularies (e.g. a structural term and a numerical term used interchangeably)
- The same quantity under different symbols or labels in text, figures, tables, and appendix
- Overloaded symbols — one letter meaning two things in different sections
- Terms used once with a threshold and never defined or mentioned again
- Bare definite nouns introduced without a name and then reused ("the composition", "the gate", "the box")
- Quantities described approximately in one place and exactly in another ("roughly ten" then "d = 10")

### 13. Numbers and internal consistency

- Same quantity reported at different precisions in different places
- Inconsistent significant figures across the paper
- Precision that overstates what the measurement supports, especially Monte Carlo p-values reported to four significant figures
- Repeated identical values presented as independent measurements when they are a resolution floor or a clipped bound — flag and say it should be stated as such
- Claims in one section contradicted by another section, especially generalization claims contradicted by the limitations
- Comparatives with no grammatical parallel ("sharper than failing inside...") — sharper than what?
- Subjects that do not match their verbs semantically ("the collapse survives" where the finding survives and the collapse recurs)

### 14. Structural and framing problems

- Results buried in a background or related-work section where a reviewer will not find them
- Ordering that forces forward references and later repair sentences ("as shown below", followed by a paragraph correcting the earlier framing) — give the reordering that removes both
- The same content stated three times across abstract, introduction, and a section opening, in the same order and near-identical words — say what the introduction should contain instead
- Missing conclusion, or a paper whose final words are limitations
- A paper that diagnoses a problem but never states the recommendation a reader should act on
- Framing that advertises something unusual while declining to explain it
- Novelty or contribution claims that overreach what the results section supports

### 15. Spelling and convention consistency

Mixed British and American spelling. Mixed date, number, or citation formats. Inconsistent capitalization of defined terms. Serial comma inconsistency. Report the mix, pick one, list the instances to change.

### 16. Anything else

After working the categories above, add a final section for defects that fit none of them. Include awkward phrasings, unclear antecedents, buried subjects, sentences whose meaning you had to reread to recover, jargon used before definition, metaphors that do not survive scrutiny, and anything that made you stop while reading. This section is not optional — if you found nothing, say what you checked for.

---

## Closing instruction

Order the whole audit so the highest-leverage fixes come first, and end with a short triage note: the five changes that most improve how a skeptical reviewer reads this paper, and roughly how long each takes.
