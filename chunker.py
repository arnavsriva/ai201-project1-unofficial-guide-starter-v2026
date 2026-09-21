"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.M)
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)


def _parse_sections(doc: Document) -> tuple[str, list[tuple[str, str]]]:
    """
    Pull a document apart into its title and its `##` sections.

    Returns the title and a list of (heading, body) pairs, in document order.
    Anything sitting between the `#` title and the first `##` — every guide in
    this corpus opens with a paragraph of scene-setting — comes back as a
    section headed "Overview", because it is real content and dropping it would
    lose the population, the history and the one-line summary of each town.
    """
    title_match = TITLE_RE.search(doc.text)
    title = title_match.group(1) if title_match else doc.source.rsplit(".", 1)[0]

    body = doc.text[title_match.end():] if title_match else doc.text

    # re.split with a capturing group interleaves [before, head, body, head, ...]
    parts = SECTION_RE.split(body)

    sections: list[tuple[str, str]] = []
    intro = parts[0].strip()
    if intro:
        sections.append(("Overview", intro))
    for heading, text in zip(parts[1::2], parts[2::2]):
        text = text.strip()
        if text:
            sections.append((heading, text))

    # A document with no `##` headings at all still has to produce something.
    if not sections:
        whole = doc.text.strip()
        if whole:
            sections.append(("Overview", whole))

    return title, sections


def _render(title: str, headings: list[str], body: str) -> str:
    """
    Stick the document's title on the front of the chunk.

    This is the whole point of the strategy, so it gets its own function. Nine
    of my fourteen documents are town guides with identical section headings,
    and the town's name appears exactly once, in the `#` line at the top. Cut
    on sections without doing this and eight of every nine chunks are an
    anonymous paragraph about somewhere.
    """
    return f"{title} — {' / '.join(headings)}\n\n{body}"


def _split_oversized(body: str, budget: int, overlap: int) -> list[str]:
    """
    Last resort for a section longer than the budget: split it at paragraphs.

    On `city_guides` this never runs — the longest section in the corpus is 691
    characters against a 900 budget. It is here because a chunker whose only
    rule is "one section, one chunk" is one badly-structured document away from
    emitting a 6,000-character chunk, and I would rather that failure be a
    split I chose than a chunk nobody notices.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    pieces: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if current and len(candidate) > budget:
            pieces.append(current)
            tail = current[-overlap:] if overlap else ""
            current = f"{tail}\n\n{paragraph}" if tail else paragraph
        else:
            current = candidate

    if current:
        pieces.append(current)
    return pieces or [body]


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents on their `##` section headings, titling every chunk.

    Three rules, in this order:

    1. **One section, one chunk.** These are sectioned travel guides. The
       section is already the unit the author wrote in — "Getting there" is a
       complete thought and "Where to stay" is a different one — so cutting
       anywhere else is cutting across meaning that someone else put there.

    2. **Every chunk gets the document's title.** Nine of the fourteen guides
       share the same seven headings, and the town name lives only in the `#`
       line. Without this, "Where to stay" for Halden Bay and for Kestrelford
       are near-identical paragraphs that the embedding model has no way to
       tell apart. This is the change that matters most.

    3. **Merge below 200 characters, split above 900.** Twelve sections in this
       corpus are under 200 characters, mostly "Where to stay" in the smaller
       towns. Left alone they are thin chunks that win a top-k slot and then
       answer nothing, so each one is merged into the section after it, keeping
       both headings in the title line. Nothing in this corpus exceeds 900, but
       see `_split_oversized`.

    Returns chunks in document order, `produced_by` set to this function.
    """
    budget = config.CHUNK_SIZE
    overlap = config.CHUNK_OVERLAP
    floor = getattr(config, "MIN_CHUNK_SIZE", 0)

    chunks: list[Chunk] = []

    for doc in documents:
        title, sections = _parse_sections(doc)

        # Rule 3, first half: roll short sections forward into the next one.
        # `pending` holds the headings and bodies waiting to be joined up.
        merged: list[tuple[list[str], str]] = []
        pending_headings: list[str] = []
        pending_body = ""

        for heading, body in sections:
            pending_headings.append(heading)
            pending_body = f"{pending_body}\n\n{body}" if pending_body else body

            if len(_render(title, pending_headings, pending_body)) >= floor:
                merged.append((pending_headings, pending_body))
                pending_headings, pending_body = [], ""

        # A tail too short to stand alone joins the previous chunk rather than
        # being dropped — the last section of a document is still content.
        if pending_headings:
            if merged:
                headings, body = merged[-1]
                merged[-1] = (headings + pending_headings, f"{body}\n\n{pending_body}")
            else:
                merged.append((pending_headings, pending_body))

        # Rule 3, second half, then render.
        index = 0
        for headings, body in merged:
            # The budget is on the finished chunk, so the title line it is
            # about to be given comes out of it first.
            room = budget - len(_render(title, headings, ""))
            for piece in _split_oversized(body, max(room, 1), overlap):
                chunks.append(
                    Chunk(
                        text=_render(title, headings, piece),
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::split_documents",
                    )
                )
                index += 1

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
