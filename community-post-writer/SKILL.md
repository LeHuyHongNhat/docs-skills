---
name: community-post-writer
description: 'Write accessible posts for community forums and groups (Viblo, Spiderum, dev.to, Medium, Reddit, Discourse/company forums, Facebook groups, LinkedIn, X threads) and turn research — papers, experiment results, notes, benchmarks, project experience — into content: explainers, tutorials, research-grade summaries (uncertainty, limits, sources checked), lessons learned, comparisons, help requests, announcements, content plans and series. Use when the user says "write a forum post", "turn this research/paper into a post", "share this on Reddit/LinkedIn", "content ideas from this", or in Vietnamese "viết bài đăng forum", "viết post chia sẻ", "đăng lên group", "viết bài Viblo", "biến research này thành bài viết", "lên ý tưởng nội dung". Writes in the user''s language (English or Vietnamese). Do NOT use for formal product/technical documentation (product-spec-writer, codebase-doc-writer), reviewing specs (doc-clarity-review), or submissions with a fixed official template.'
---

# Community Post Writer

Goal: a post that a stranger in the community **understands on first read, trusts, and wants to reply to** — written from real material, with every claim traceable, in the format the platform actually renders.

Community readers differ from document readers: they skim, they did not ask for your post, they range from beginners to experts, and they will call out exaggeration in the comments. So the post must earn attention in its first two lines, explain without talking down, and be more careful with claims than marketing copy.

## Process

### 1. Pin down the brief (infer first, ask only if it changes the post)

| Decide | Default when the user says nothing |
|---|---|
| Platform | Generic Markdown forum (Discourse/Viblo-like). Platform rules: `references/platform-formats.md` |
| Audience level | Mixed: practitioners new to *this* topic. Define every term on first use |
| Goal | Share knowledge + start a discussion |
| Post type | Pick from `references/post-types.md` by the material (research → summary/explainer; own project → lessons learned; options → comparison; stuck → help request) |
| Language & voice | The user's language. Vietnamese forums: "mình – các bạn" (friendly, peer); LinkedIn/company forums: "tôi" or neutral |
| Length | Long-form forum/blog 800–1,800 words; Facebook/LinkedIn 120–300 words; Reddit 300–900 words |
| Rigor tier | **Research-grade** whenever the post compares things with numbers, claims a cause, summarises a study, or shows a benchmark/backtest (step 2b applies). **Share** tier (opinion, how-to, question, announcement) skips 2b |

State in one line at the top of your reply which platform, audience and post type you assumed. Ask only when two readings lead to very different posts (e.g. a beginner tutorial vs an expert critique).

### 2. Research → evidence ledger (before any prose)

Read every source the user gave. If the user asks you to research and you have search tools, search; otherwise work only from what was given. Build a ledger (scratch file is fine), one row per claim you might use:

| # | Claim (your words) | Number/quote | Source (link, file, section) | Strength |
|---|---|---|---|---|

- **Strength**: measured (experiment/data) · reported (paper, docs, official post) · experience (the user's own observation) · opinion.
- Record **limits** next to the claim: sample size, number of runs, dataset, date, conditions.
- Note **tempting overclaims** in the material ("so X is always better") — the post must not repeat them.
- Never add numbers, benchmarks, quotes, dates or names that are not in the ledger. A gap stays a gap: write around it, say it is unknown, or ask the user.

Details and the angle matrix: `references/research-to-content.md`.

### 2b. Rigor pass — required for research-grade posts

A plain, honest post can still be wrong in the way a reviewer cares about: "38/50 beats 31/50" sounds careful and is not supported (the 95% CI of that difference runs from −4 to +31 points). Read `references/research-rigor.md` and, before choosing any wording:

1. **Turn the ledger into a claim ledger**: for each claim add its type (descriptive / comparative / causal / predictive), the design behind it (randomised experiment, observational, single benchmark, case study, backtest, one run) and the unit and n.
2. **Run the numbers** — `python <skill-dir>/scripts/stats_check.py claims claims.yaml --strict` (or the single commands: `prop`, `diff-prop`, `mcnemar`, `paired`, `seeds`, `sharpe`, `reported`, `mde`). Each claim gets a verdict: SUPPORTED, WEAK, INCONCLUSIVE, DESCRIPTIVE or UNQUANTIFIED, plus a wording hint. The verdict, not the size of the gap, decides the verb. A claim whose source gives no n or variance is UNQUANTIFIED and is written as "the source states".
3. **Let the design choose the verb** (rigor §2): only a randomised/controlled design earns causal words; a benchmark earns "on this dataset"; a backtest earns "in simulation, gross/net of costs"; one company's migration earns "in this case".
4. **Walk the threat list for the domain** (rigor §4: ML eval · data science · quant · systems benchmarks) and write down which threats apply and whether each was addressed, partly addressed or not checked. For quant content state the economic hypothesis and cover look-ahead bias, survivorship, number of trials/overfitting, out-of-sample evidence and costs — or say plainly that they are unknown.
5. **For someone else's study** (rigor §5): take numbers from the primary source's tables with their intervals; keep the authors' own "this does not show" list; check for follow-ups, corrections and newer versions and state the date of the evidence; when a sign convention or unit is undefined in the source, quote it verbatim and build nothing on one reading.
6. **Say what is missing and what would settle it**: per-item results, more seeds, an out-of-sample period — with the sample size from `mde` / `power-prop` when you can compute it. If the user can supply the missing data (per-question results, run logs), ask for it; otherwise write the weaker claim.

The post then carries, in prose or as sections: how it was measured (design, n, baseline, metric), results with uncertainty, limits/threats, reproducibility (code, data, versions — or why not), and sources with dates. Readability rules still apply: explain a confidence interval in one clause the first time ("khoảng tin cậy 95%: vùng giá trị mà chênh lệch thật nhiều khả năng nằm trong").

### 3. Choose the angle (offer several when the user asks for ideas)

One body of research supports many posts. Pick the angle that fits the brief; when the user asks "what can I write from this" or wants a series, give a **content plan** of 3–6 angles (format in `references/research-to-content.md` §3): working title, audience, type, the one-sentence takeaway, key evidence rows, platform. Then write the one they choose — or the best fit, if they are not around to choose, saying which and why.

Every post has **one takeaway** you can say in one sentence. Write it down before outlining. If you cannot, the angle is too broad — split it.

### 4. Outline: hook → context → core → takeaway → discussion

1. **Title** — specific, honest, ≤ 70 characters in English / ≤ 90 in Vietnamese. Promise only what the post delivers. Produce 3 options in different styles (result-first, question, how-to); recommend one.
2. **Hook (first 2 lines)** — the problem, the surprising result, or the question; never a greeting or "in this post I will…". On Facebook/LinkedIn this is all that shows before "See more".
3. **Context** — who this is for, why it matters, what you did/read (1 short paragraph).
4. **Core** — 3–5 sections, each one idea: claim → evidence (number + source) → plain-language explanation → example. Use headings on long-form platforms.
5. **Limits** — what this does not show (sample, conditions, what you did not test). Short, honest; it is what makes experts trust the rest.
6. **Takeaway + discussion** — the one-sentence takeaway, then one concrete question to the community ("Bạn đang chunk theo cách nào, và đo bằng gì?"), not "Thoughts?".

### 5. Draft in plain, accurate language

Follow `references/plain-language.md`. The essentials:
- Short paragraphs (≤ 4 sentences); sentences ≤ 25 words on average; one idea per sentence.
- Define each term and acronym on first use in a clause; then keep the same word (no synonyms for technical terms).
- Explain with a concrete example or an everyday analogy before (or right after) the abstract statement. Mark analogies as analogies; do not stretch them.
- Every number has a unit, a comparison base and a source; percent vs percentage points kept straight.
- Hedge exactly as much as the evidence: measured → state it; one run / small sample → "in my test of 50 questions"; opinion → "I think".
- No hype, no clichés, no fake urgency: banned-word lists are in `plain-language.md` and checked by the script.
- Vietnamese: keep standard English technical terms (embedding, chunking, latency, API) and explain them in Vietnamese on first use; do not invent Vietnamese translations nobody uses.

**Visuals.** If the post compares numbers or shows a trend, add a chart (` ```chart ` block; rules in `references/presentation-and-charts.md`) or a compact table. Most platforms cannot render chart blocks: export them as images (`render_doc.py --to charts`) and reference the PNG where the image goes. Text-only platforms (Facebook, LinkedIn, X) get the image as an attachment, mentioned in your reply.

### 6. Check

```bash
python <skill-dir>/scripts/post_check.py <post.md> --platform <platform> [--title "<title>"]
```
Add `--rigor` for research-grade posts: it flags a missing sample size, comparative claims with no uncertainty anywhere, "significant" without a test, causal wording with no controlled design, absolute words ("proves", "luôn luôn"), missing limitations/sources/dates, and backtest or eval caveats. Then score the draft against rubric R1–R12 in `references/research-rigor.md` §7; anything scoring 0 is fixed or declared in the reply.

Fix every `high` finding (markdown the platform cannot render, over the length limit, banned clickbait/hype in the title). For `medium` findings (long sentences, undefined acronyms, numbers with no source nearby, filler opening), fix or keep with a reason. Then re-read as a newcomer: is any sentence understandable only if you already know the topic? Then as an expert: is any claim stronger than the ledger allows?

### 7. Deliver

- Save the post as `.md` (source). For text-only platforms also save the plain-text version ready to paste (`post_check.py --platform facebook --export post.txt` converts headings/bold/links to platform-safe text).
- If there are charts, export the images with `render_doc.py <post.md> --to charts --out-dir <dir>`.
- In the reply: the assumed brief (1 line), the 3 title options with your pick, the file(s), and anything the user must fill in or verify (e.g. [TO CONFIRM] a number you could not source). For research-grade posts also list the claims that came out WEAK / INCONCLUSIVE / UNQUANTIFIED and what data would upgrade them. Do not paste a long post into chat if the file exists; short posts (≤ 300 words) can also be shown inline for copy-paste.
- When asked, add a repurposing pack: a short version for Facebook/LinkedIn, an X thread, and the next 2–3 posts of a series (from the content plan).

## Short example (Vietnamese, Facebook group, from an experiment note)

❌ "🚀 Semantic chunking là GAME-CHANGER cho RAG!!! Tăng độ chính xác cực kỳ ấn tượng, ai làm RAG cũng phải biết!"

✅
```
Mình thử 3 cách cắt tài liệu (chunking) cho chatbot hỏi đáp nội bộ, và cách "đắt" nhất không thắng.

Chunking là bước chia tài liệu dài thành các đoạn nhỏ trước khi đưa vào tìm kiếm. Mình đo trên 50 câu hỏi thật của team, chấm đúng/sai bằng tay:
• Cắt cố định 500 token: 31/50 câu đúng
• Cắt theo heading: 38/50
• Semantic chunking: 37/50 (chạy chậm hơn ~4 lần)

Với tài liệu có heading rõ ràng như wiki nội bộ, cắt theo heading đủ tốt và rẻ hơn. Mình mới chạy 1 lần, 50 câu, nên chưa dám nói cho mọi loại tài liệu.

Mọi người đang chunk theo cách nào, và đo kết quả bằng gì?
```

## Resources

- `references/post-types.md` — 9 post types with structure, title patterns and pitfalls (explainer, tutorial, research summary, lessons learned, comparison/review, help request, announcement, discussion/opinion, roundup).
- `references/research-to-content.md` — evidence ledger, angle matrix, content plan & series format, citing sources, repurposing across platforms.
- `references/platform-formats.md` — what each platform renders, length limits, conventions and etiquette (VI + EN communities).
- `references/plain-language.md` — readability rules, term-definition patterns, analogy rules, hedging scale, banned hype/cliché lists (VI/EN).
- `scripts/post_check.py` — readability & platform checker (sentence/paragraph length, undefined acronyms, hype words, unsourced numbers, markdown support, length limits, title checks); `--rigor` adds research-grade checks; `--export` writes a platform-safe plain-text version.
- `references/research-rigor.md` + `scripts/stats_check.py` — claim ledger, design → allowed verbs, statistics minimum, threats to validity by domain (ML, data science, quant, systems), reporting other people's studies, rigor rubric R1–R12; the script computes CIs, paired tests, seed variance, Sharpe SE/deflation, Holm correction and overclaim flags.
- `references/presentation-and-charts.md` + `scripts/charts.py` + `scripts/render_doc.py` — charts and comparison layouts; `--to charts` exports chart images for posts, `--to html` makes a shareable page.
