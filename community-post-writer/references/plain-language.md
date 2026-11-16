# Plain language for community posts

Accessible ≠ simplistic. The goal is that a reader new to the topic follows every sentence, and an expert finds nothing wrong.

## 1. Sentence and paragraph rules

| Rule | Target | Checked by `post_check.py` |
|---|---|---|
| Average sentence length | ≤ 20 words (EN) / ≤ 28 syllables (VI) | yes |
| Longest sentences | none > 35 words (EN) / > 45 syllables (VI) | yes (medium) |
| Paragraph length | ≤ 4 sentences, ≤ 80 words (EN) / ≤ 110 syllables (VI) | yes |
| Headings in long posts | one per 250–400 words on Markdown platforms | yes (posts > 600 words without H2) |
| Hook | first paragraph ≤ 60 words, no greeting/filler | yes |
| Discussion ending | the last paragraph asks one specific question (when the goal includes discussion) | info |

Active voice, concrete subject: "We measured…", "The script deletes…" — not "It was observed that…" / "Được ghi nhận rằng…".

## 2. Terms and acronyms

- First use: term + plain explanation in the same sentence. Pattern: "**term** — what it is / does, in everyday words". "Embedding — biểu diễn một đoạn văn thành một dãy số để máy so sánh được độ giống nhau."
- Acronyms: spell out at first use: "Retrieval-Augmented Generation (RAG)". The checker flags acronyms with no expansion nearby (common ones like API, AI, URL, PDF are allowed).
- One concept = one word for the whole post. Do not alternate "chunk / đoạn / mảnh / segment".
- Vietnamese: keep the standard English term and explain it; avoid literal translations nobody searches for ("nhúng" for embedding is acceptable only if you also give "embedding").

## 3. Examples and analogies

- Concrete before abstract: show the example, then name the principle.
- One running example through the post beats five unrelated ones.
- Analogies: say it is an analogy, keep it short, and state where it breaks if that matters ("like a library index — except the index is built from meaning, not titles").
- Code/data examples must be real or clearly marked as illustrative.

## 4. Numbers

- Unit + comparison base + source: "p95 latency fell from 480 ms to 270 ms (−44%) after enabling the cache (Grafana, weeks 5–7)".
- Percent vs percentage points; absolute alongside relative.
- Small samples as counts: "38/50", not "76%" alone.
- Same rounding everywhere; numbers in text, tables and charts must match.
- Vietnamese number format: `92,5%`, `1.200 người dùng`; English: `92.5%`, `1,200 users`.

## 5. Hedging scale (match the evidence, no more, no less)

| Evidence | EN | VI |
|---|---|---|
| Measured, adequate sample | "X reduced Y by 20%" | "X giảm Y 20%" |
| Measured, small/one run | "In our test (50 questions, one run), X…" | "Trong thử nghiệm của mình (50 câu, chạy 1 lần), X…" |
| Reported by others | "The paper reports…" | "Theo paper…, …" |
| Experience | "In my experience…" | "Theo kinh nghiệm của mình…" |
| Opinion / prediction | "I think…, because…" | "Mình nghĩ…, vì…" |

Never: "proves", "always", "everyone should", "chắc chắn", "luôn luôn", "ai cũng nên" — unless literally true.

## 6. Banned: hype, clichés, filler (checked by the script)

**Hype / clickbait (EN)**: game-changer, revolutionary, mind-blowing, insane, ultimate guide, secret, hack (as "trick"), you won't believe, must-read, 10x, skyrocket, unlock the power, supercharge, crushing it.

**Hype / clickbait (VI)**: cực kỳ, vô cùng, siêu (as intensifier), đỉnh cao, bá đạo, thần thánh, bí kíp, bí mật, đột phá, không thể bỏ qua, chắc chắn 100%, sốc, gây bão, cực phẩm, xịn sò.

**AI-sounding clichés (EN)**: delve, in today's fast-paced world, in the ever-evolving landscape, it's important to note that, let's dive in, a testament to, navigate the complexities, embark on a journey, in conclusion.

**AI-sounding clichés (VI)**: trong thời đại công nghệ 4.0, trong thế giới ngày nay, hãy cùng khám phá, không chỉ… mà còn… (overused), đóng vai trò vô cùng quan trọng, có thể nói rằng, nhìn chung thì, tóm lại là.

**Filler openings**: "Hello everyone, today I want to share…", "In this post I will…", "Xin chào mọi người, hôm nay mình xin chia sẻ…", "Chào các bạn, chắc hẳn ai cũng từng…". Start with the hook instead.

Replace with the specific fact: not "a game-changer for RAG" but "answered 7 more of 50 questions correctly".

## 7. Structural tells of machine-written prose

Word lists age with every model release. The shapes below persist, because they are what "writing for nobody in particular" looks like. `post_check.py` reports the first five on one sighting and the rest only when two or more kinds occur together — a careful writer makes any single one on purpose.

| Tell | Looks like | Do instead |
|---|---|---|
| Contrast for weight | "Chunking is not just a step, but the foundation…" · "không chỉ là… mà còn là…" · "It's not X. It's Y." | State Y. Keep a contrast only when the reader really believed X |
| Staged run-up | "Here's the thing", "Let's dive in" · "Sự thật là", "Hãy cùng đi sâu" | Start with the point |
| One-line closer | "That's it." "Let that sink in." · "Chỉ vậy thôi." · a last sentence that names what the example showed | Cut it, or end on a fact |
| Chat residue | "I hope this helps", "Great question" · "Hy vọng bài viết hữu ích", "Chúc các bạn thành công" | Delete |
| Inflated significance | "plays a crucial role", "a pivotal moment" · "đóng vai trò then chốt", "bước ngoặt" | Say what happened and how much |
| Dashes as the default connector | several " — " per paragraph | Period, comma, colon or parentheses |
| Bold label on every list item | "- **Speed.** It is fast." repeated | Prose, or a table when items share fields |
| Clipped fragments in a row | "No errors. No warnings. All green." | One full sentence |
| Forced triads | three adjectives or three examples by reflex | The one or two that are true |
| Decorated or echoed headings | emoji, Title Case, a heading restated by the next sentence | A heading that states the point, then the content |
| Voice only at both ends | personal opening, impersonal middle, call-to-action ending | Keep the writer's reactions where the work was hard |

**When not to act**: inside a quotation, a title, a proper name, or a passage that discusses the phrase; when the user's own writing sample does it (their voice wins over this table).

**After any rewrite, re-check the facts.** Compare the rewritten text with the ledger: every number, name, date, quote and "X happened before Y" must survive unchanged. Smoothing prose is where numbers get dropped or claims get merged.

## 8. Headings, paragraphs, endings

- **A heading states the point of its section.** "Kết quả" names a slot; "Cắt theo heading ngang semantic chunking trên 50 câu" tells the skimmer the result. Exception: conventional end sections (Sources, Limits).
- **Break the paragraph where the direction turns** ("but", "tuy nhiên"): the turn starts a new paragraph.
- **Numbers over adjectives**: "p99 from 340 ms to 45 ms", not "significantly faster".
- **End on something usable**: the question to the community, a link to code or data, the next experiment. Not a recap, not a slogan.
- **A number promised in the title or opening must reappear in the body** with its source.

## 9. Titles

- Specific: names the topic and the result or promise.
- Honest: the post delivers exactly that.
- ≤ 70 characters (EN), ≤ 90 (VI); no ALL-CAPS words, no "!!!", no "?!".
- Patterns: result-first ("Heading-based chunking beat semantic chunking on our wiki"), question ("Do you need semantic chunking for internal docs?"), how-to ("How to measure RAG chunking with 50 real questions").
