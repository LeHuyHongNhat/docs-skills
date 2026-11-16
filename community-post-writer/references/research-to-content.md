# Research → content

How to turn papers, notes, experiment logs, benchmark tables or project experience into posts without losing accuracy — and how to get several posts out of one body of research.

## 1. Evidence ledger

Build it before writing; the post may only use rows from it.

| # | Claim (your words) | Number / short quote | Source | Strength | Limits |
|---|---|---|---|---|---|
| E1 | Heading-based chunking answered more questions correctly than fixed 500-token chunks | 38/50 vs 31/50 | notes.md §2 | measured | 1 run, 50 internal questions, manual grading |
| E2 | Semantic chunking is slower | ~4× indexing time | notes.md §3 | measured | single machine |
| E3 | "Semantic chunking is best for everything" | — | notes.md §5 (author's guess) | opinion | not tested → do **not** use as a claim |

For research-grade posts the ledger becomes a **claim ledger** with design, n and a computed verdict — see `research-rigor.md` §1–§3. The strength scale below is the minimum for every post; the verdict from `stats_check.py` overrides it when numbers are compared.

Strength scale (use it to choose verbs):

| Strength | Means | Verbs/hedges to use |
|---|---|---|
| measured | the user or a cited study measured it | "measured", "in our test", "đo được" + conditions |
| reported | from a paper, official docs or a credible report | "the paper reports", "theo <nguồn>" |
| experience | the user's observation, not measured | "in my experience", "mình thấy" |
| opinion | belief, prediction, preference | "I think", "mình nghĩ", framed as opinion |

Rules:
- Numbers are copied exactly from the source with their unit; rounding is fine if consistent and does not change a comparison.
- Keep the conditions with the number (dataset, sample size, version, date). A number without conditions is not usable in a comparison.
- When two sources disagree, show both and say which you trust and why — or say it is unresolved.
- Quoting: at most one short quote per source; paraphrase everything else and link the original. Never paste paragraphs of someone else's article.
- People and companies: only public, relevant facts. Do not name colleagues, clients or internal systems unless the user confirms it is OK to publish.

## 2. Angle matrix — one body of research, many posts

For each angle, ask: who is the reader, what do they already know, what will they do after reading?

| Angle | Reader | Post type | Example takeaway (from one chunking experiment) |
|---|---|---|---|
| The surprising result | practitioners | lessons learned | "The fancy chunking did not win on our wiki" |
| The concept | beginners | explainer | "Chunking decides what your RAG can find — here is how it works" |
| The how-to | practitioners | tutorial | "Heading-based chunking in 30 lines of Python" |
| The comparison | decision-makers | comparison | "Fixed vs heading vs semantic chunking: pick by document type" |
| The method | researchers / careful readers | research summary | "How we graded 50 questions by hand, and why not LLM-as-judge" |
| The debate | community | discussion | "Do we over-engineer RAG before measuring?" |
| The resources | learners | roundup | "What to read before choosing a chunking strategy" |

Pick angles whose takeaway is supported by **measured/reported** rows. Angles that rest only on opinion rows become discussion posts, clearly framed as opinion.

## 3. Content plan format

When asked for ideas or a series, deliver a table, then a recommendation:

| # | Working title | Reader | Type | Takeaway (1 sentence) | Evidence | Platform | Effort |
|---|---|---|---|---|---|---|---|
| 1 | … | … | … | … | E1, E2 | Viblo | M |

Then: "Start with #N because …" and a suggested order/cadence for a series. Do not draft all posts unless asked.

## 4. Making it accessible without making it wrong

- **Translate, don't dilute**: replace jargon with an explanation, but keep the precise term once so readers can search for it ("cosine similarity — a score of how close two vectors point").
- **Numbers people can feel**: "38 of 50 questions" is clearer than "76% accuracy" for small samples; give both if useful. Relative changes always with absolute values ("from 31 to 38 correct answers, +7").
- **One example carried through**: introduce one running example early and reuse it in every section.
- **Uncertainty as information**: "we ran it once on 50 questions" helps readers judge; it is not weakness.
- **Visuals**: one chart per comparison claim (see `presentation-and-charts.md`); a table when readers need exact values; a diagram for a process. Charts get a `source:` line just like text.

## 5. Citing on community platforms

- Long-form (Viblo, dev.to, Medium, Discourse, Reddit): inline links on the claim, plus a "Sources / Tài liệu tham khảo" list at the end with title + link.
- Facebook / LinkedIn: links lower reach on some platforms; put the key source link at the end of the post or in the first comment — tell the user which you chose. Still name the source in the text ("theo paper của Google DeepMind 2025").
- The user's own unpublished data: say so ("số liệu từ thử nghiệm nội bộ của team mình").

## 6. Repurposing pack

From one long post:
- **Short social version** (Facebook/LinkedIn, 120–300 words): hook + 3 bullets of evidence + takeaway + question + link.
- **X thread** (5–8 posts ≤ 280 characters): 1 hook, 1 per key point, 1 limits, 1 link/question. Number them 1/7…
- **Series follow-ups**: the next 2–3 angles from the matrix.
Each version must keep the same numbers and the same caveats — shorter is not permission to drop limits that change the meaning.
