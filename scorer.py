"""
The scorer. Decides whether an answer was right — built in unit 2.

`run_eval.py` finds this file on its own. It calls `judge` once per run and
puts pass/fail in the Run columns; if `breakdown` exists it records the
per-criterion checks too, so the run log carries the evidence for criteria
1, 2 and 5 separately instead of one bool that mixes them together.

What "right" means here is deliberately mechanical, and the README says where
that came apart from what a person would say:

  criterion 1  retrieval_hit    some retrieved chunk contains `expects`
  criterion 2  names_source     the answer names a real file from the corpus
  criterion 5  citations_hold   every file the answer names contains `expects`
  (the run)    correct          the answer itself contains `expects`

`expects` is the word or phrase written in questions.py in unit 1, before any
results existed. The scorer never sees the question text; it only compares
strings. That is a limitation and it is the point — a scorer that has to be
argued with about what "8:30" means is a scorer that can be run twice and get
the same answer.

Criterion 4 is not per-run. `chunk_check` counts it once over every chunk.
"""

import re
from functools import lru_cache

import gate


# ─── Normalisation ───────────────────────────────────────────────────────────


def _norm(text: str) -> str:
    """Lower-case, collapse whitespace, and treat 8.30 / 8:30 / 8 30 alike.

    The only judgement call in this file. Question 2 expects "8:30" and the
    model is entitled to write "8.30pm"; refusing that on punctuation would be
    the scorer failing, not the system.
    """
    text = text.lower()
    text = re.sub(r"(\d)[.\s](\d\d)\b", r"\1:\2", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _contains(haystack: str, needle: str) -> bool:
    return _norm(needle) in _norm(haystack)


# ─── The corpus, for criteria 2 and 5 ────────────────────────────────────────


@lru_cache(maxsize=1)
def _documents() -> dict[str, str]:
    """Filename -> full cleaned text, loaded once. Disk only, no model."""
    from ingest import load_documents

    return {d.source: d.text for d in load_documents()}


def cited(answer: str) -> list[str]:
    """Every real corpus filename the answer mentions, in order, once each."""
    names = _documents()
    found = []
    for match in re.finditer(r"[\w-]+\.(?:md|txt)", answer):
        name = match.group(0)
        if name in names and name not in found:
            found.append(name)
    return found


# ─── The four checks ─────────────────────────────────────────────────────────


def retrieval_hit(expects: str, results) -> bool:
    """Criterion 1: did any retrieved chunk contain the expected phrase?"""
    return any(_contains(r.text, expects) for r in results)


def names_source(answer: str) -> bool:
    """Criterion 2: does the answer name at least one real source file?"""
    return bool(cited(answer))


def citations_hold(expects: str, answer: str) -> bool:
    """Criterion 5: does every file the answer names actually contain the fact?

    An answer that names nothing has no citation to be wrong, and also none to
    be right — that is criterion 2's failure, so it comes back False here too
    rather than passing by default.
    """
    files = cited(answer)
    if not files:
        return False
    docs = _documents()
    return all(_contains(docs[name], expects) for name in files)


def disagreement_named(question: str, answer: str) -> bool | None:
    """Criterion 5, tightened in unit 2: where the sources disagree, say so.

    Only applies to questions that carry a `disagreement` list in
    questions.py — the terms an answer has to name to have surfaced both
    sides. Returns None for every other question, so the run log counts it
    out of the questions it applies to rather than out of five.

    Added after the "before" run, where all three answers to the hospital
    question quoted guide_kestrelford.md and never mentioned that the rank-1
    chunk from guide_accessibility.md says something different.
    """
    import questions as qs

    terms = None
    for item in qs.QUESTIONS:
        if item.get("question") == question:
            terms = item.get("disagreement")
            break
    if not terms:
        return None
    if answer.strip() == gate.REFUSAL:
        return False
    return all(_contains(answer, term) for term in terms)


def correct(expects: str, answer: str) -> bool:
    """The answer itself contains the expected phrase and is not a refusal."""
    if answer.strip() == gate.REFUSAL:
        return False
    return _contains(answer, expects)


# ─── What run_eval.py calls ──────────────────────────────────────────────────


def breakdown(question: str, expects: str, answer: str, results) -> dict:
    """Every check separately, so the run log can count them per criterion."""
    return {
        "retrieval_hit": retrieval_hit(expects, results),
        "names_source": names_source(answer),
        "correct": correct(expects, answer),
        "citations_hold": citations_hold(expects, answer),
        "disagreement_named": disagreement_named(question, answer),
        "cited": cited(answer),
    }


def judge(question: str, expects: str, answer: str, results) -> bool:
    """One verdict for one run. Everything has to hold at once.

    A run passes when the answer contains the expected phrase, names a source,
    and every source it names contains that phrase. Retrieval is included
    because an answer that is right without the fact being in a retrieved
    chunk came from the model's memory, which is the thing this whole system
    exists to prevent.

    `disagreement_named` is deliberately NOT in here. It is the unit 2
    tightening of criterion 5, and the pass/fail column has to mean the same
    thing in the "before" and "after" logs. It is reported on its own row.
    """
    b = breakdown(question, expects, answer, results)
    return b["retrieval_hit"] and b["correct"] and b["names_source"] and b["citations_hold"]


# ─── Criterion 4, counted once ───────────────────────────────────────────────


def chunk_check(min_chars: int | None = None) -> dict:
    """Every chunk names its document and none is under the floor.

    Deterministic, so it runs once. Returns the counts and the offenders.
    """
    import config
    from chunker import split_documents, TITLE_RE
    from ingest import load_documents

    floor = min_chars if min_chars is not None else getattr(config, "MIN_CHUNK_SIZE", 200)
    documents = load_documents()
    titles = {}
    for doc in documents:
        match = TITLE_RE.search(doc.text)
        titles[doc.source] = match.group(1) if match else doc.source.rsplit(".", 1)[0]

    chunks = split_documents(documents)
    missing_title = [c.label for c in chunks if titles[c.source] not in c.text]
    too_short = [(c.label, len(c.text)) for c in chunks if len(c.text) < floor]

    return {
        "total": len(chunks),
        "floor": floor,
        "missing_title": missing_title,
        "too_short": too_short,
        "passing": len(chunks) - len({*missing_title, *(label for label, _ in too_short)}),
    }


if __name__ == "__main__":
    result = chunk_check()
    print(
        f"{result['passing']} of {result['total']} chunks name their document "
        f"and are at least {result['floor']} characters."
    )
    if result["missing_title"]:
        print("  missing title:", ", ".join(result["missing_title"]))
    if result["too_short"]:
        print("  too short:", ", ".join(f"{l} ({n})" for l, n in result["too_short"]))
