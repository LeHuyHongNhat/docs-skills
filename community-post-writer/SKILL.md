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

**Voice.** If the user gives one or two of their past posts, read them first and match sentence length, word choice, punctuation and how they open and close; their sample overrides the style tables in `plain-language.md`. Without a sample, take the voice from the platform row above.

**If the user brings their own draft**, pick the mode before touching it: *rebuild* (the draft is thin or generic → run the whole process from the facts) · *restore* (a real voice with real content → keep their argument and words; fix accuracy, clarity and tells only) · *point edit* (one line or section → change that and the minimum around it; skip the rest of the process).

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
6. **When an agent produced the work** (it wrote the code, ran the experiments or searched the literature), read `references/agent-assisted-research.md` and do the evidence intake in its §1 before drafting: the frozen plan with its decision rule, the run log, the reproduced baseline, the data check, the checked citations. Compute the comparison straight from the log (`stats_check.py runs <log> --metric … --group … --treat … --control … --pair seed`) and report the verdict the pre-written rule gives — "inconclusive" included. A number with no run behind it is removed; an analysis with no pre-written rule is labelled exploratory; a missing item becomes a stated limit. State how many variants were tried (`fwer`, `winners-curse` show what selection alone produces).
7. **Say what is missing and what would settle it**: per-item results, more seeds, an out-of-sample period — with the sample size from `mde` / `power-prop` when you can compute it. If the user can supply the missing data (per-question results, run logs), ask for it; otherwise write the weaker claim.

The post then carries, in prose or as sections: how it was measured (design, n, baseline, metric), results with uncertainty, limits/threats, reproducibility (code, data, versions — or why not), and sources with dates. Readability rules still apply: explain a confidence interval in one clause the first time ("khoảng tin cậy 95%: vùng giá trị mà chênh lệch thật nhiều khả năng nằm trong").

### 3. Choose the angle (offer several when the user asks for ideas)

One body of research supports many posts. Pick the angle that fits the brief; when the user asks "what can I write from this" or wants a series, give a **content plan** of 3–6 angles (format in `references/research-to-content.md` §3): working title, audience, type, the one-sentence takeaway, key evidence rows, platform. Then write the one they choose — or the best fit, if they are not around to choose, saying which and why.

Every post has **one takeaway** you can say in one sentence. Write it down before outlining. If you cannot, the angle is too broad — split it.

### 4. Outline: hook → context → core → takeaway → discussion

1. **Title** — specific, honest, ≤ 70 characters in English / ≤ 90 in Vietnamese. Promise only what the post delivers. Produce 3 options in different styles (result-first, question, how-to); recommend one.
2. **Hook (first 2 lines)** — the problem, the surprising result, or the question; never a greeting or "in this post I will…". On Facebook/LinkedIn this is all that shows before "See more".
3. **Context** — who this is for, why it matters, what you did/read (1 short paragraph).
4. **Core** — 3–5 sections, each one idea: claim → evidence (number + source) → plain-language explanation → example. On long-form platforms each heading states the point of its section ("Semantic chunking took 26 minutes to index"), not its slot ("Results").
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

### 6. Check, one pass per question

One pass looks for one thing; a single "review everything" read misses most of them. Run the passes in this order, and after each fix re-check the passes before it.

| Pass | Question | Tool |
|---|---|---|
| 1. Fidelity | Does every number, name, date and quote match the ledger? Did any rewrite drop or merge a claim? | ledger; `stats_check.py claims` |
| 2. Rigor (research-grade) | Is each claim only as strong as its verdict and design? Limits, sources, dates present? | `post_check.py --rigor`; rubric R1–R12 and the reviewer pass in `research-rigor.md` §7 |
| 3. Newcomer | Can someone new to the topic follow every sentence? Terms defined at first use? | `post_check.py` (sentence length, acronyms) |
| 4. So what | Does each section tell the reader why it matters to them? Does each heading state its point? | read each section and ask "so what?" |
| 5. Specific | Is there a number or a concrete example wherever an adjective stands? | `post_check.py` (hype, unsourced figures, headline numbers) |
| 6. Voice | Does it read like one person wrote it for this community? | structural tells in `plain-language.md` §7; `post_check.py` TELL findings |
| 7. Platform | Will it render and fit? | `post_check.py --platform …` |

```bash
python <skill-dir>/scripts/post_check.py <post.md> --platform <platform> [--rigor] [--title "<title>"]
```
Fix every `high` finding. Fix each `medium` finding or keep it with a reason you can state. `TELL-*` findings are fixed by rewriting the passage around its point, not by swapping the flagged phrase.

### 6b. Reader test

Before delivering a post that will be published, run the reader test in `references/reader-test.md`: write 5–8 reader questions (including one the text should not be able to answer), have a reader with only the post answer them, and fix what they get wrong. If a subagent or Task tool is available, the reader is a fresh agent that sees only the post — for a mixed audience, one newcomer and one critical specialist. If not, do the cold read yourself and say in the hand-off that it was a self-test.

### 7. Deliver

- Save the post as `.md` (source). For text-only platforms also save the plain-text version ready to paste (`post_check.py --platform facebook --export post.txt` converts headings/bold/links to platform-safe text).
- If there are charts, export the images with `render_doc.py <post.md> --to charts --out-dir <dir>`.
- For a research-grade post, start from `assets/research-post-template.md` when outlining: its REQUIRED slots are the blocks a reviewer looks for.
- In the reply: the assumed brief (1 line), the 3 title options with your pick, how the reader test was run and what it changed, the file(s), and anything the user must fill in or verify (e.g. [TO CONFIRM] a number you could not source). For research-grade posts also list the claims that came out WEAK / INCONCLUSIVE / UNQUANTIFIED and what data would upgrade them. When an agent did substantial work, add (a) the whiteboard questions — three things the author should be able to explain without the agent before publishing — and (b) a one-line AI-use disclosure for the post, with a reminder to check the venue's policy for the exact year when the text is a submission. Do not paste a long post into chat if the file exists; short posts (≤ 300 words) can also be shown inline for copy-paste.
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

- `references/post-types.md` — 10 post types with structure, title patterns and pitfalls (explainer, tutorial, research summary, lessons learned, comparison/review, help request, announcement, discussion/opinion, roundup, internal update), the reader-question order and the worth-sharing test.
- `references/research-to-content.md` — evidence ledger, angle matrix, content plan & series format, citing sources, repurposing across platforms.
- `references/platform-formats.md` — what each platform renders, length limits, conventions and etiquette (VI + EN communities).
- `references/plain-language.md` — readability rules, term-definition patterns, analogy rules, hedging scale, banned hype/cliché lists (VI/EN), structural tells of machine-written prose, heading and ending rules.
- `scripts/post_check.py` — readability & platform checker (sentence/paragraph length, undefined acronyms, hype words, unsourced numbers, markdown support, length limits, title checks); `--rigor` adds research-grade checks; `--export` writes a platform-safe plain-text version.
- `references/research-rigor.md` + `scripts/stats_check.py` — claim ledger, design → allowed verbs, statistics minimum, threats to validity by domain (ML, data science, quant, systems), reporting other people's studies, rigor rubric R1–R12; the script computes CIs, paired tests, seed variance, Sharpe SE/deflation, Holm correction and overclaim flags.
- `references/agent-assisted-research.md` — for work an agent helped produce: evidence intake per stage, frozen plan and decision rule, run log, selection effects of fast iteration (multiple testing, low prior, winner's curse), what an interval covers, agent failure modes and how to detect them, paper cards and novelty verdicts, review, responsibility and disclosure.
- `assets/experiment-plan-template.md` — plan to freeze before the first run, with the decision rule and an append-only amendments log.
- `references/reader-test.md` — question-based test with a reader who has only the text; prompt for a fresh agent, cold-read fallback, how to read the results.
- `assets/research-post-template.md` — skeleton with REQUIRED slots for research-grade posts.
- `references/presentation-and-charts.md` + `scripts/charts.py` + `scripts/render_doc.py` — charts and comparison layouts; `--to charts` exports chart images for posts, `--to html` makes a shareable page.
