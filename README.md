# The Unofficial Guide

arnavsriva — corpus: `city_guides`

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

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. Every chunk names its document, none under 200 chars | 91 of 91 |  |  |  |  |
| 5. Cited source contains the fact | 4 of 5 |  |  |  |  |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. Every chunk names its document, none under 200 chars | 91 of 91 |  |  |  |  |
| 5. Cited source contains the fact | 4 of 5 |  |  |  |  |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
