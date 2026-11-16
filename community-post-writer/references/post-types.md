# Post types

Pick the type from the material and the goal. Each type lists: when to use it, the structure, title patterns, and the pitfalls readers punish.

Contents: 1 Explainer · 2 Tutorial / how-to · 3 Research summary · 4 Lessons learned · 5 Comparison / review · 6 Help request · 7 Announcement / release · 8 Discussion / opinion · 9 Roundup

## 1. Explainer ("what is X and why should I care")
**Use when** the audience does not know a concept the material relies on.
**Structure**: the problem X solves (concrete situation) → X in one sentence → how it works in 3–5 steps or one diagram → a worked example with real numbers or code → when *not* to use X → further reading.
**Titles**: "X explained with one real example" · "X là gì? Giải thích bằng một ví dụ thật" · "Why your RAG answers drift: chunking in 5 minutes".
**Pitfalls**: definition-first openings; analogies that are wrong in the details that matter; no "when not to use".

## 2. Tutorial / how-to
**Use when** the reader should be able to do something after reading.
**Structure**: what you will have at the end (screenshot/result) → prerequisites (versions!) → numbered steps, each: what + command/code + expected output → common errors and fixes → next steps.
**Titles**: "How to <result> with <tool> in <N> steps" · "Hướng dẫn <kết quả> bằng <công cụ> (từng bước)".
**Pitfalls**: untested commands; missing versions; steps that silently depend on the author's setup; screenshots instead of copyable text for code.
**Rule**: run or verify every command you can; mark the ones you could not verify.

## 3. Research summary (paper, report, benchmark)
**Use when** the material is someone else's research and the audience will not read the original.
**Structure**: one-sentence finding in plain words → the question the authors asked and why it matters → what they did (data, method, scale) → key results (numbers with units; a chart if comparing) → limits the authors state + limits you notice → what it means for practitioners → link to the original.
**Titles**: "<Finding> — what the <venue/year> paper actually shows" · "Tóm tắt paper <tên ngắn>: <phát hiện chính>".
**Pitfalls**: reporting the abstract's spin instead of the tables; dropping the conditions under which a result holds; implying causation; quoting > 1–2 short sentences verbatim (paraphrase and link instead).

## 4. Lessons learned / experience report
**Use when** the material is the user's own project, experiment, incident or career experience.
**Structure**: context in 2–3 lines (team size, stack, constraint) → what we tried → what happened (numbers where possible) → 3–5 lessons, each tied to an event → what we would do differently → question to the community.
**Titles**: "What we learned migrating <X> to <Y>" · "3 điều mình rút ra sau <N> tháng làm <X>".
**Pitfalls**: generic lessons ("communication is important") not tied to an event; hiding failures; sharing confidential numbers/names — ask the user what can be public.

## 5. Comparison / review
**Use when** readers must choose between options (tools, approaches, courses).
**Structure**: who should read this + the decision → criteria and why they matter (before results) → comparison table (options as columns, ✓ ✗ ◐ with reasons) and/or chart → per-option short verdict ("pick A if…") → what you did not test → disclosure (affiliation, sponsorship, the user's own product).
**Titles**: "A vs B for <use case>: <short verdict>" · "So sánh A, B, C cho <bài toán> — chọn cái nào khi nào".
**Pitfalls**: criteria chosen after seeing results; one "winner" for all cases; undisclosed affiliation; versions/dates missing (reviews age fast).

## 6. Help request / question
**Use when** the user is stuck and wants answers from the community.
**Structure**: one-line goal → what happens vs what you expected → minimal reproducible example (code, data sample, exact error text) → environment (versions, OS) → what you already tried → a specific question.
**Titles**: "<Tool>: <exact symptom> when <condition>" — e.g. "pandas merge drops rows when key has trailing spaces". Not "Help!!!" or "Lỗi gấp, ai giúp với".
**Pitfalls**: screenshots of code; no error text; "it doesn't work"; asking several unrelated questions at once.

## 7. Announcement / release
**Use when** sharing something the user built or an event.
**Structure**: what it is in one sentence + who it is for → the problem it solves → what is new (bullets, user-facing) → how to try it (link, install command) → limits/known issues → how to give feedback.
**Titles**: "<Name> <version>: <main benefit>" · "Ra mắt <tên>: <lợi ích chính> cho <đối tượng>".
**Pitfalls**: feature lists without the problem; superlatives; no way to try it; ignoring community self-promotion rules (check the platform section).

## 8. Discussion / opinion
**Use when** the user has a position and wants debate.
**Structure**: the claim stated plainly → the 2–3 strongest reasons, each with evidence or experience → the strongest counter-argument, stated fairly → where you might be wrong → an open question.
**Titles**: a clear position or question — "Unpopular opinion: you don't need a vector DB for < 10k documents" (only if the post actually argues that).
**Pitfalls**: straw-man counter-arguments; rage-bait titles; presenting opinion as fact.

## 9. Roundup / curated resources
**Use when** pointing readers to the best material on a topic.
**Structure**: who it is for and how items were chosen → grouped list (beginner → advanced, or by sub-topic), each item: link + 1–2 lines on why and what you get → a suggested path through the list.
**Titles**: "<N> resources to learn <X> (ordered from zero to production)".
**Pitfalls**: lists of links without judgment; dead or outdated links; too many items (≤ 10 per group).

## Series

When the material is too big for one post, plan a series: post 1 is the explainer or the most surprising result (to earn the audience), the middle posts are tutorials/deep dives, the last post is lessons/discussion. Each post must stand alone (re-state the context in 2 lines) and link to the others.
