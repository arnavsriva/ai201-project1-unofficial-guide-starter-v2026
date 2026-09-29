# The Unofficial Guide

Arnav Srivastava (arnavsriva) — corpus: `city_guides`

---

# Unit 1

## What This Does

This answers questions about a fictional English region of nine small towns,
using fourteen travel guides as its only source. Nine of those documents are
town guides — Brightwater, Kestrelford, Halden Bay and six others — each broken
into the same seven sections: getting there, getting around, eating, what to
see, where to stay, when to go, practical notes. The other five cut across all
nine towns and cover eating, walking, regional transport, seasons and
accessibility. It answers the kind of question you would ask before a trip:
where to stay in a particular town, what time the pubs stop serving, which
towns are hard to get around in a wheelchair. If the documents don't cover it,
a relevance gate refuses the question before it reaches the model rather than
letting it improvise.

## Chunking Strategy

**Chunk size:** 900 characters, as a ceiling that splits a section only if it
exceeds it. On this corpus it never fires — the longest section is 691
characters.
**Overlap:** 80 characters, and for the same reason it also never fires. Between
sections the overlap is zero, deliberately.

The numbers are guard rails rather than the strategy. The strategy is: **one
`##` section per chunk, with the document's `#` title prepended to every one.**

What made me pick it was reading the documents in Milestone 1 and noticing two
things at once. The first is that every document is already divided into
labelled sections of about 275 characters each, and those sections are real
boundaries — "Getting there" is a complete thought and "Where to stay" is a
different one. Cutting anywhere else is cutting across a division somebody else
already made for a reason. So a character count is the wrong instrument here;
the section is the unit.

The second thing is the one that actually decided it. **Nine of the fourteen
guides have identical section headings, and the town's name appears exactly
once, in the `#` line at the top of the file.** Under the starter's 800-character
windows, 34 of 51 chunks never named their own subject. I confirmed what that
costs before changing anything: asking "Where should I stay in Halden Bay?"
returned chunk 0 of `guide_halden_bay.md`, which holds Getting there, Getting
around and Eat and drink. The Where to stay text is in chunks 1 and 2, and
neither of them contains the word "Halden". The only chunk carrying the town's
name was the one that didn't have the answer, so it won every question about
that town regardless of what was being asked.

That is why the title goes on the front of every chunk. It is a change of about
four lines and it matters more than the section splitting does.

I set overlap to zero between sections on purpose. Overlap exists to stop a
fact being cut in half at a boundary, and on this corpus the boundaries are
places where the subject genuinely changes. Duplicating text across one would
produce two chunks that each half-answer two different questions. The 80
characters are reserved for the case where a single section is too long and has
to be split internally — which is a case this corpus does not contain, and I
left the code in anyway because a chunker whose only rule is "one section, one
chunk" is one badly-structured document away from emitting a 6,000-character
chunk.

**I changed my mind once.** I set the 200-character floor expecting it to do a
lot of work, because twelve sections in the corpus are under 200 characters —
mostly "Where to stay" in the smaller towns, which is sometimes two sentences.
It fires three times. Adding the title line lifted nine of those twelve over the
floor by itself, which I had not predicted. The merge rule is still there and is
still doing something real for `guide_thornby_wells.md` and
`guide_givens_mill.md`, but it turned out to be a detail rather than the fix.

The result: 51 chunks became 91, averaging 329 characters, shortest 206, longest
894. Chunks that fail to name their own subject went from 34 of 51 to 0 of 91.

## Sample Chunks

`python app.py chunks -n 5`

**Chunk 1** — source: `guide_accessibility.md#0` — produced by: `chunker.py::split_documents`

```
Getting around the region with limited mobility — Overview / Straightforward

An honest assessment rather than a promotional one. Some of these places are
difficult and it is better to know in advance.

**Thornby Wells** is the easiest town in the region. It is flat, compact, and
everything is within three minutes of everything else. Parking is free for two
hours anywhere in town and the station is central. The pump room and gardens
are level throughout.

**Marchwood** has a modern tram network with level boarding on all four lines,
running every 8 minutes on weekdays. The city museum and covered market are both
step-free. The distances between districts are the main consideration.

**Brightwater** is level along the river and through the centre. The mill museum
is step-free. The station is a 15-minute walk from campus on flat ground, or the
shuttle meets the four busiest arrivals.
```

This is one of the three merged chunks — a 123-character intro that could not
stand on its own, joined to the section after it. The `Overview / Straightforward`
in the title line is the merge showing itself.

**Chunk 2** — source: `guide_corry_vale.md#6` — produced by: `chunker.py::split_documents`

```
Corry Vale — When to go

May to September. Outside those months the pub in the third village closes, the farm shop reduces its hours, and several footpaths become genuinely boggy rather than merely wet. The road is not gritted above the second village and is impassable in snow.
```

**Chunk 3** — source: `guide_givens_mill.md#3` — produced by: `chunker.py::split_documents`

```
Givens Mill — Eat and drink

A tearoom attached to the mill, open 10 to 4 daily except Tuesdays, which sells bread made from the flour ground twenty metres away and is the reason most people come. One pub, food served lunchtimes and Thursday to Saturday evenings.
```

**Chunk 4** — source: `guide_kestrelford.md#6` — produced by: `chunker.py::split_documents`

```
Kestrelford — When to go

Late spring and early autumn. The Saturday market runs year-round but is much reduced from November to February. August is busy with walkers. The single-track approach road is genuinely difficult in snow and the town can be cut off for a day or two most winters.
```

Chunks 2 and 4 are the case the title line exists for. Both are "When to go",
both are about 270 characters, both say a season and then a warning about snow.
Without `Corry Vale —` and `Kestrelford —` on the front they are close to
indistinguishable, and a question about either town could retrieve the other.

**Chunk 5** — source: `guide_regional_transport.md#0` — produced by: `chunker.py::split_documents`

```
Getting around the region — The railway

The line runs along the river valley, connecting Brightwater to the regional
hub in 50 minutes. Eleven services a day on weekdays, six on Sundays. The line
north of Brightwater closed in 1963 and everything beyond it is bus or car.

Tickets are cheaper booked the day before than on the day, and considerably
cheaper than that booked a week ahead. There is no ticket office at
Brightwater station outside weekday mornings; the machine on the platform takes
cards only.
```

## Sample Answer

`python app.py ask "Where should I stay in Halden Bay?"`

**Question:** Where should I stay in Halden Bay?

**Answer:**

```
  (best distance 0.243, cutoff 0.59)

Halden Bay is almost entirely made up of holiday lets rather than hotels, and there is also one inn located on the harbour.

Source: `guide_halden_bay.md`

Sources retrieved: guide_halden_bay.md, guide_regional_transport.md, guide_seasons.md
```

This is the question that returned the wrong section of the right file before
Milestone 3. The best distance was 0.351 then, against a chunk that did not
contain the answer; it is 0.243 now, against the chunk that does.

**My relevance cutoff:** 0.59

I ran all ten questions through `app.py retrieve`, which shows distances without
spending a model call, and wrote down the best distance for each. The two groups
separate cleanly: in-corpus tops out at **0.5589** and out-of-corpus starts at
**0.6244**, so there is a gap 0.066 wide with nothing in it. 0.59 is
approximately the middle — 0.031 of room below, 0.034 above.

The starter's default of 0.6 also lands in that gap, so this is a small move
rather than a rescue. I made it anyway because 0.6 is off-centre: it leaves only
0.024 before Kyoto gets through, against 0.041 of slack on the other side, and
there is no reason to spend margin on the side that is already safer.

What the two groups look like is more interesting than the number. The in-corpus
distances are not a tight cluster — they run from 0.166 to 0.559, a spread of
nearly 0.4 — and the question at the top of that range is the one I flagged in
criteria.md as hard, the wheelchair question, which is answered in one section
of a document whose title never names a town. The out-of-corpus group has the
same structure in reverse. The two questions I kept from the starter's set sit at
0.810 and 0.861, miles away, because nothing about Mongolia or Rust resembles a
travel guide. The three I wrote myself are all between 0.624 and 0.721. Kyoto is
the closest thing to a false positive in the whole set, and it is close for an
obvious reason: "what is the best time of year to visit Kyoto?" and "when should
I visit Kestrelford?" are the same sentence with a different noun, and the
embedding model has no way to know which of those two places I have documents
about. Had I kept the starter's five, the gap would have measured about 0.25
wide and I would have concluded the cutoff barely mattered.

| Question | In corpus? | Best distance |
|---|---|---|
| What time do the pubs in Kestrelford stop serving food in the evening? | yes | 0.1655 |
| Where should I stay in Halden Bay? | yes | 0.2433 |
| Why is Brightwater at its busiest in late September? | yes | 0.2589 |
| Is there a full hospital in Kestrelford? | yes | 0.3865 |
| Which towns in the region are hardest to get around in a wheelchair? | yes | 0.5589 |
| What is the best time of year to visit Kyoto? | no | 0.6244 |
| Where can I hire a car at Edinburgh airport? | no | 0.6421 |
| How much does a rail pass cost in Switzerland? | no | 0.7215 |
| What is the capital of Mongolia? | no | 0.8104 |
| How do I write a for loop in Rust? | no | 0.8614 |

## How I Used AI

I used Claude heavily on this — it wrote most of the code in `chunker.py` and
drafted large parts of this file. Two moments where what came back needed
changing:

**1.** I asked for a chunker that splits on `##` headings, prepends the document
title, merges anything under 200 characters and splits anything over 900. What
came back did all four, but it applied the 900-character budget to the section
body and then prepended the title *afterwards* — so the title line was never
counted, and a section just under budget would produce a chunk just over it. It
was invisible on this corpus, because nothing here comes close to 900, which is
exactly why I would not have caught it by reading the output. I changed
`_split_oversized` to be handed `budget - len(title_line)` instead of `budget`.

**2.** I asked whether to keep the five `OUT_OF_SCOPE` questions the starter
ships with. The answer I got back was that they are all so far from a travel
corpus — Mongolia, Rust, ibuprofen, the 1994 World Cup — that refusing them
demonstrates the gate is connected and nothing more, and that questions shaped
like the ones the corpus *does* answer, about places it has never heard of,
would actually locate the boundary. I replaced three of the five with Kyoto,
Swiss rail passes and Edinburgh airport. That turned out to be the single
decision with the largest effect on Milestone 4: it narrowed the measured gap
from roughly 0.25 to 0.066, and 0.066 is the number the cutoff is actually
chosen against. I did keep two of the originals rather than replacing all five,
which was my change to the suggestion — having both ends visible in the table is
what shows that the narrowness is a property of my three questions and not of
the gate.

No stretch feature attempted in unit 1.

---

# Unit 2

## Run Log — Before

`python run_eval.py --label before` → `results/run_2026-09-29_0938_before.md`.
Corpus `city_guides`, top-k 5, cutoff 0.59, three runs per question with
caching off, 15 model calls. Chunks from `chunker.py::split_documents`,
retrieval by `store.py::search`, answers by `generate.py::answer_from_chunks`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 2. Every answer names a source | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 4. Every chunk names its document, none under 200 chars | 91 of 91 | 91 of 91 | 91 of 91 | 91 of 91 | MET |
| 5. Cited source contains the fact | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |

Criteria 3 and 4 are one deterministic pass each, so the same number sits in
all three columns.

**How the numbers were produced.** The starter's `run_eval.py` gives one
pass/fail per run and cannot say which criterion it was. So `scorer.py` has,
besides the `judge` the script looks for, a `breakdown` that runs the checks
behind criteria 1, 2 and 5 separately, and `run_eval.py::write_report` now
counts those per run into a "Per-criterion counts" table in the results file.
The checks are string comparisons against the `expects` phrase written in
`questions.py` in unit 1:

- `scorer.retrieval_hit` — criterion 1: some retrieved chunk contains the phrase.
- `scorer.names_source` — criterion 2: the answer contains a filename that
  actually exists in the corpus. "The guide says" does not count.
- `scorer.citations_hold` — criterion 5: *every* file the answer names contains
  the phrase. An answer that names nothing fails this too, rather than passing
  by having no citation to get wrong.
- `scorer.chunk_check` — criterion 4, counted once over all 91 chunks.

One normalisation, and it is the only judgement in the file: `8.30`, `8:30`
and `8 30` are treated as the same string, because question 2 expects "8:30"
and the model is entitled to write it either way.

### Real output, one per criterion

**Criterion 1** — retrieval by `store.py::search`, checked by
`scorer.py::retrieval_hit`. This is the closest of the five, the wheelchair
question, from `python app.py retrieve`:

```
Question: Which towns in the region are hardest to get around in a wheelchair?

#   distance   source                           preview
1   0.5589     guide_accessibility.md           Getting around the region with limited mobility — Di...
2   0.6184     guide_accessibility.md           Getting around the region with limited mobility — Ov...
3   0.6347     guide_corry_vale.md              Corry Vale — Getting around  Nothing within the vall...
4   0.6526     guide_walking.md                 Walking in the region — Seasonal notes  Add four min...
5   0.6534     guide_walking.md                 Walking in the region — Easy, on good surfaces  The ...

Gate: best distance 0.559 is under the 0.59 cutoff
```

The rank-1 chunk is `guide_accessibility.md#2`, the "Difficult" section, and
it contains "Halden Bay". It is also the only one of the five under the
cutoff — the other four are material the gate would have refused on their own.
That is worth remembering for the Diagnoses.

**Criterion 2** — answers by `generate.py::answer_from_chunks`, checked by
`scorer.py::names_source`. Question 1, run 1:

```
According to `guide_halden_bay.md`, Halden Bay consists almost entirely of holiday lets rather than hotels, and there is also one inn located on the harbour.
```

**Criterion 3** — `run_eval.py::check_out_of_scope` through `gate.py::check`:

```
| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.810 | refused |
| How do I write a for loop in Rust? | 0.861 | refused |
| What is the best time of year to visit Kyoto? | 0.624 | refused |
| How much does a rail pass cost in Switzerland? | 0.721 | refused |
| Where can I hire a car at Edinburgh airport? | 0.642 | refused |
```

**Criterion 4** — `scorer.py::chunk_check` over `chunker.py::split_documents`:

```
91 of 91 chunks name their document and are at least 200 characters.
```

**Criterion 5** — checked by `scorer.py::citations_hold`. Question 5, run 1,
the question written to break this criterion:

```
No, there is not a full hospital in Kestrelford; the nearest full hospital is in Brightwater.

(Source: `guide_kestrelford.md`)
```

The run log's scorer line for it reads *"every source the answer cites
contains the fact yes; cited guide_kestrelford.md"*, and that file does say
"The nearest full hospital is in Brightwater." Sources retrieved for the same
run: `guide_accessibility.md, guide_kestrelford.md` — and the rank-1 chunk,
at 0.3865, was the accessibility one, which says the nearest full hospital is
in **Marchwood**. The answer does not mention it. Hold that thought.

## Verdicts

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | MET | 15 of 15 runs by the scorer, and retrieval is deterministic so the three runs are one measurement repeated. I hand-checked that the `expects` phrase sits in the chunk that *is* the answer rather than incidentally elsewhere — for question 4, "term" is in `guide_seasons.md#2` ("as term starts"), which is the answering chunk, and also in the Brightwater overview ("term time"), which is not; both were retrieved, so the check would have passed either way. The close call is question 3 at 0.559, discussed below. |
| 2 | Every answer names a source | MET | 15 of 15. The scorer only accepts a filename that exists in the corpus, so this is not a check that can be passed by writing "the guide". Every answer named at least one file and nine of the fifteen named exactly one. No judgement was needed, which is what I said in unit 1 would happen. |
| 3 | Gate stops out-of-corpus questions | MET | 5 of 5 in one deterministic pass. The nearest to getting through was Kyoto at 0.624, with 0.034 to spare — the identical number from Milestone 4, because nothing touched the index between then and now. |
| 4 | Every chunk names its document, none under 200 chars | MET | 91 of 91, both halves counted over every chunk rather than a sample. |
| 5 | Cited source contains the fact | MET | 15 of 15 by the proxy. I read all fifteen answers by hand as well, because the proxy only says the cited file contains the `expects` phrase, not that it contains the sentence the answer attributes to it. It did, every time: nine answers cite one file, six cite two, and each citation is a file that says what it is credited with. The close one is question 3, run 2, which named only Halden Bay and Kestrelford where the section lists four towns — an incomplete answer, but every word of it is in `guide_accessibility.md`, and this criterion is about the citation, not completeness. |

## Diagnoses

Nothing was missed. All five criteria held in all three runs, so there is no
miss to diagnose, and I want to be careful not to invent one.

The honest version of "were the targets set low" is: two of them were, in ways
I can show with numbers rather than assert, and both come from the same
mistake — I measured one phrasing of one question per criterion, and the
phrasing was doing work I had not noticed.

**1. Criterion 5 could not see the failure it was written to catch.**
Question 5 retrieves two chunks 0.002 apart: `guide_accessibility.md#3`
(0.3865, "The nearest full hospital is in Marchwood") at rank 1 and
`guide_kestrelford.md#7` (0.3889, "The nearest full hospital is in
Brightwater") at rank 2. The corpus contradicts itself, and I knew that in unit
1 — it is in the criteria file. All three answers cited the Kestrelford guide,
said Brightwater, and never mentioned Marchwood. Every citation was accurate,
so criterion 5 passed 3 of 3 while the system did precisely the thing I wrote
in criteria.md that I cared about most: it picked one of two conflicting
sources and presented it as the answer, with nothing on the surface to say a
choice had been made.

**Stage: generation.** Both claims were in the prompt — retrieval did its job.
The mechanism, as far as I can see it from outside: the grounding instruction
says to be brief and to name the document, and says nothing about what to do
when documents disagree, so the model resolved the conflict by omission. Which
one it dropped was consistent, 3 of 3, and I think the title line explains it:
`Kestrelford — Practical notes` names the town in the question and
`Getting around the region with limited mobility — Practical` does not.

**What I would tighten it to:** *where two retrieved sources disagree about the
fact asked for, the answer says so and names both.* Re-scored against the
"before" transcript that is 0 of 3 — none of the three answers contains the
word "Marchwood". This is now written under the original in `criteria.md`,
marked as an addition rather than a revision, and implemented as
`scorer.disagreement_named`, which only applies to question 5 because it is
the only question where the corpus disagrees with itself. The original
criterion stays, and the run logs are scored against it.

**2. Criteria 1 and 3 were measured with a margin of one sentence.** Question
3 passed at 0.559 against a cutoff of 0.59. I rephrased it seven ways and put
each through `store.py::search` and `gate.py::check` — no model calls:

| Phrasing | Best distance | Rank-1 chunk | Gate |
|---|---|---|---|
| Which towns in the region are hardest to get around in a wheelchair? | 0.559 | `guide_accessibility.md#2` | passed |
| Which towns should I avoid if I use a wheelchair? | 0.596 | `guide_accessibility.md#2` | **refused** |
| Which towns are worst for wheelchair users? | 0.603 | `guide_accessibility.md#2` | **refused** |
| Where in the region is wheelchair access poor? | 0.619 | `guide_accessibility.md#2` | **refused** |
| Which places are difficult with limited mobility? | 0.556 | `guide_accessibility.md#2` | passed |
| Is Halden Bay wheelchair accessible? | 0.504 | `guide_accessibility.md#2` | passed |
| Which towns are step-free? | 0.530 | `guide_accessibility.md#0` | passed |

Three of the four phrasings built around the word "wheelchair" are refused,
and in every one of them the right chunk is at rank 1. Retrieval is correct
and the gate says no.

**Stage: embedding.** Not retrieval, which ranked the right chunk first every
time, and not the cutoff. The accessibility guide says "limited mobility" in
its title and "wheelchair" once in 2,178 characters, so a question built on
"wheelchair" embeds at about 0.60 from it — the same band as Kyoto (0.624) and
Edinburgh airport (0.642). No cutoff separates 0.596 from 0.624; the gap I
measured in Milestone 4 was between the five sentences I happened to write and
the five out-of-scope sentences I happened to write, not between in-corpus and
out-of-corpus. Nothing in the criteria measured that, because each criterion
saw one phrasing.

I tightened the first of these and not the second, because the first could be
measured on the questions I already had and it is the one I said mattered
most. The second is in What's Still Broken.

## The Improvement

**What I changed:** one line added to `GROUNDING_INSTRUCTION` in
`generate.py`:

```
- If two documents disagree about the answer, say so and name both. Do not pick one and drop the other.
```

Nothing else. No re-index, same chunks, same cutoff, same top-k. The "before"
and "after" runs differ by that sentence and by nothing else, which is the
only way the second run says anything about the first.

**Why I picked it:** diagnosis 1 puts the miss in the generation stage — both
claims were in the prompt and the model dropped one — so the fix belongs in
the one instruction that stage receives.

### Run Log — After

`python run_eval.py --label after` → `results/run_2026-09-29_0942_after.md`.
Same settings, 15 model calls.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 2. Every answer names a source | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 4. Every chunk names its document, none under 200 chars | 91 of 91 | 91 of 91 | 91 of 91 | 91 of 91 | MET |
| 5. Cited source contains the fact | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 5, tightened in unit 2: where sources disagree, the answer names both (question 5 only) | 1 of 1 | 0 of 1 | 0 of 1 | 0 of 1 | MISSED |

Question 5, run 1, after the change — `generate.py::answer_from_chunks`:

```
No, there is no full hospital in Kestrelford. According to `guide_accessibility.md`, Kestrelford has a minor injuries unit with limited hours or nothing at all, and `guide_kestrelford.md` states that the nearest full hospital is in Brightwater.
```

**Did it help?** No, on the number it was aimed at. Something adjacent moved,
and the way it moved is the finding.

| Question 5, three runs each | Before | After |
|---|---|---|
| Answers citing `guide_accessibility.md` | 0 of 3 | 3 of 3 |
| Answers that mention Marchwood | 0 of 3 | 0 of 3 |

The instruction got the model to bring in the second document, and it brought
in the sentence from that document that *agrees* — "Kestrelford has a minor
injuries unit with limited hours or nothing at all" — and left out the
sentence two lines above it that disagrees. I think I know why, and it is my
wording rather than the model's disobedience: the question is a yes/no, both
documents agree the answer is no, and the disagreement is about a secondary
fact — where the nearest full hospital is. "Disagree about the answer" was
satisfied to the letter. The scorer reads 0 of 3 before and 0 of 3 after, and
I read all six answers to make sure the scorer was not missing a paraphrase
of Marchwood. It was not.

Side effects, since a prompt change touches every question: no regression on
any of the five criteria, all 15 runs pass as before. Answers got longer —
question 3 run 3 became a four-bullet list, question 4 run 3 added a hedge
about which document "explicitly" gives the reason — and output tokens across
the 15 calls went from 715 to 893. That is the cost of a sentence that did not
buy what it was for.

One probe outside the run logs, which I am reporting because it changes what
I would do next: I reworded the instruction to *"check whether any two
documents state different facts about the same thing; if they do, say so and
name both files, even if the difference is not the main point of the
question"* and ran question 5 three times with it. It named Marchwood in 1 of
3. A stronger instruction moves this from never to sometimes, which is not a
fix, and I did not swap it in — one change per logged run is the rule that
makes the "after" log attributable to the "before" log.

## What's Still Broken

**The tightened criterion 5: 0 of 3.** Two things I would do, in order.

The cheap one is to change the question. "Where is the nearest full hospital
to Kestrelford?" makes the disagreement *the* answer rather than a footnote to
a yes/no; there is then no agreed "no" for the model to settle on and stop.
Retrieval for that phrasing already returns the same two chunks in the same
order (0.344 and 0.357), so it is a change to the question, not the pipeline.

The real one is to stop asking the model to notice contradictions in passing.
The probe above says an instruction gets followed somewhere between 0 and 1
time in 3; that is not a knob to keep turning. Instead, a second call before
the answer: *"Here are five excerpts. List any facts two of them state
differently."* Its output goes into the answer prompt as a "Conflicts" block
the model has to address. It costs one extra call per question and turns
something the model can skip into a step it cannot.

Why I stopped: the two logged runs plus the probe came to 33 model calls and
all of the time I had, and a second prompt change would need its own
before-and-after to mean anything — stacking it on this one would leave me
unable to say which sentence did what.

**The gate refuses paraphrases of in-corpus questions.** Three of the seven
wheelchair phrasings above, all with the right chunk at rank 1. The obvious
next step is hybrid search — `rank-bm25` ships in the starter for it — so I
measured what it would do before building it. BM25 over the 91 chunks, top
score and top chunk per question, against the dense distance:

| Question | Dense | BM25 top score | BM25 top chunk |
|---|---|---|---|
| Which towns should I avoid if I use a wheelchair? | 0.596 | 6.75 | `guide_seasons.md#1` |
| Which towns are worst for wheelchair users? | 0.603 | 4.37 | `guide_regional_transport.md#2` |
| Where in the region is wheelchair access poor? | 0.619 | 9.57 | `guide_marchwood.md#3` |
| What is the best time of year to visit Kyoto? | 0.624 | 11.27 | `guide_seasons.md#0` |
| Where can I hire a car at Edinburgh airport? | 0.642 | 7.32 | `guide_givens_mill.md#5` |

Keyword search does not rescue these. Its top chunk for all three paraphrases
is the wrong one — "towns", "region", "access" outscore the single occurrence
of "wheelchair" — and Kyoto scores higher on BM25 than any of them, because
"time", "year" and "visit" are all over the seasons guide. A keyword signal
folded into the gate would let Kyoto through before it let a wheelchair
question in. The fix that actually changes these distances is a different
embedding model, which is the stretch option, and it means a new Milestone 4:
new distances, new gap, new cutoff, and a 2 GB install. That is a
re-calibration rather than one change, and the run log as written cannot show
it, since all five of my phrasings already pass. I stopped there and wrote it
down instead.

## What I'd Do Differently

**Criterion 5** I would write in the tightened form from the start — *where
retrieved sources disagree, the answer says so and names both* — and I would
phrase question 5 so that the disagreement is the answer. I built the one
question in the set designed to break this criterion, then wrote a criterion
that the intended failure passes. The citation-accuracy version is still
worth having, but as the floor, not the criterion.

**Criteria 1 and 3** I would measure over paraphrases: *for each of the five
questions, at least two of three phrasings pass the gate and retrieve the
answering chunk.* One phrasing per question gave me a Milestone 4 gap of 0.066
that the wheelchair table shows does not exist for questions about that
document. It would also have caught that criterion 3's "4 of 5" was budgeting
for the wrong failure — I set it aside for one out-of-scope question getting
through, and none did; the failure that actually shows up is in-corpus
questions being refused, and the criterion as written cannot see that
direction at all.

**Criterion 2** I would drop. It was 15 of 15 twice, and I said in unit 1 that
it was plumbing rather than judgement; a criterion that cannot fail is a smoke
test. In its place: *no answer cites a document that was not retrieved for
it* — which is the hallucinated-citation case, and which, having now checked
all 30 answers against their retrieved sets, also held 30 of 30, but at least
it is a thing that could go wrong.

**Criterion 4** I would keep exactly as it is. It is the only one that was a
full count rather than a sample of five, it stayed at 91 of 91 through both
runs because nothing touched the chunker, and that is what a criterion about a
finished stage looks like: it did its job in unit 1 and now has nothing left
to say, which is different from having nothing to say.
