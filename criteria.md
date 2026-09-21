# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:** Nine of my fourteen documents are town guides with the
*same seven section headings*, and the town's name appears only in the `#` line
at the top of the file. So a question that names a town has to be matched by a
chunk that may never mention that town. I watched this happen at the baseline:
"Where should I stay in Halden Bay?" returns chunk 0 of `guide_halden_bay.md`,
which holds Getting there, Getting around and Eat and drink — the Where to stay
text is in chunks 1 and 2, split across the boundary between them. Not 5 of 5,
because question 4 is answered in two different documents at once
(`guide_brightwater.md` says *when* the town is busiest, `guide_seasons.md` says
*why*), and one retrieval pulling both is the thing I am least confident about.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:** All fourteen documents are single files with stable
filenames, `store.py::search` carries `source` through on every `Result`, and
`generate.py` puts those filenames in the prompt. Nothing has to be inferred or
reconstructed, so this is plumbing rather than judgement. That is exactly why
the target is 5 of 5 and not 4: at 4 of 5 a genuine bug would look like normal
variation, whereas any miss against 5 of 5 tells me something is actually
broken. Note this criterion only asks that a source is *named* — whether it is
the *right* source is criterion 5, and they come apart on this corpus.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:** I rewrote three of the five `OUT_OF_SCOPE` questions so
this target means something. The starter's set — Mongolia, Rust, ibuprofen — is
so far from a travel corpus that refusing it proves only that the gate is
plugged in. Mine asks about Kyoto, Swiss rail passes and Edinburgh airport:
travel questions, phrased like the ones the corpus *does* answer, about places
it has never heard of. That is the case I expect to be close, because "when
should I visit Kyoto" and "when should I visit Kestrelford" are near-identical
sentences and the embedding model does not know which of those two places is in
my documents. 4 of 5 rather than 5 of 5 is me budgeting for exactly one of those
three near-misses getting through.

Distances measured in Milestone 4 are in the README table, and they are the
reason the cutoff is where it is.

---

## 4. Chunks carry enough context to be identified on their own

Every chunk contains the title of the document it came from, and no chunk is
shorter than 200 characters. Both counted across all chunks, not a sample.

**Why this target:** I measured the baseline chunker on this corpus before
writing the criterion. Of its 51 chunks, **34 never name their own subject** and
**8 are under 200 characters**, the shortest being a 24-character fragment left
over at the end of a file. On a corpus of nine guides with identical section
headings, a chunk that does not say which town it is about is close to useless:
the "Where to stay" text for Halden Bay and for Kestrelford are two paragraphs
that mean different things and read almost the same. The 200-character floor is
there because those tail fragments are pure noise — they carry a sentence and a
half of a section whose heading is in a different chunk — and they take up a
top-k slot that a real chunk could have used. I am counting every chunk rather
than sampling five because both numbers are cheap to compute and a sample of
five would have missed the 24-character one entirely.

---

## 5. The source named is the source the fact came from

For at least 4 of my 5 test questions, every source document the answer cites
actually contains the fact it is being credited with.

**Why this target:** The `## Practical notes` block at the end of the nine town
guides is **byte-identical in all nine files**. Ask "is there a full hospital in
Kestrelford?" and there are nine chunks with an equal claim to being the answer,
eight of which are the wrong town — and `guide_accessibility.md` contradicts all
nine anyway, saying the nearest full hospital is in Marchwood rather than
Brightwater. So an answer here can name a real file, quote it accurately, and
still be citing the wrong document, which criterion 2 would happily pass. I care
about this one more than any of the others: a system that cites confidently and
wrongly is worse than one that refuses, because there is nothing on the surface
of the answer to tell you which you got. 4 of 5 and not 5 of 5 because question
5 is the one designed to break this, and I would rather write down now that I
expect to miss it than discover it next unit and claim I meant to.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
