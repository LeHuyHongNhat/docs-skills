# Platform formats

What each platform renders, how long posts should be, and the conventions readers expect. Platform limits change — when a limit matters (e.g. a post close to it), tell the user to check the current value. `post_check.py --platform <key>` uses the keys and limits below.

| Key | Platforms | Renders | Practical length | Hard limit used by the checker |
|---|---|---|---|---|
| `forum` (default) | Discourse, company/internal forums, GitHub Discussions | Markdown: headings, lists, tables, code, links, images | 600–1,800 words | — |
| `viblo` | Viblo | Markdown incl. code blocks, tables, math | 800–2,500 words | — |
| `devto` | dev.to, Hashnode | Markdown + front matter (title, tags) | 800–2,000 words | — |
| `medium` | Medium, Spiderum, other rich-text editors | Rich text; pasted Markdown is not reliably converted — headings/bold must be applied in the editor; no Markdown tables | 800–2,000 words | — |
| `reddit` | Reddit | Markdown (headings, lists, tables, code) | 300–900 words | 40,000 characters |
| `facebook` | Facebook groups/pages | Plain text: no Markdown, no tables; line breaks and emoji/• bullets only; links shown as preview | 120–300 words; the first 2–3 lines show before "See more" | 63,206 characters |
| `linkedin` | LinkedIn posts | Plain text, line breaks; no Markdown | 120–300 words; ~2 lines before "…see more" | 3,000 characters |
| `x` | X / Twitter threads | Plain text per post | 5–8 posts | 280 characters per post (split on lines with `---`) |

## Conventions by platform

**Markdown forums (forum, viblo, devto, reddit)**
- H2 for sections (`##`); never more than one H1 (the title is usually a separate field — do not repeat it as H1 in the body if the platform has a title field).
- Code in fenced blocks with a language; never screenshots of code.
- Tables: ≤ 5 columns; put long explanations below.
- Charts: platforms do not render ` ```chart ` blocks → export with `render_doc.py --to charts` and upload the PNG; write the takeaway as the image caption/alt text.
- dev.to: add front matter (`title`, `tags` ≤ 4, `description`) when the user wants a ready-to-publish file.
- Reddit: read the subreddit rules (self-promotion ratio, flair, "no low-effort questions"); put a TL;DR at the top or bottom for posts > 300 words; disclose if the user built the thing being discussed.
- Viblo / Vietnamese tech communities: technical depth is welcome; keep English technical terms; credit sources; tags matter for discovery.

**Rich-text editors (medium, Spiderum)**
- Deliver Markdown as the source, and tell the user that headings, bold and images must be applied in the editor (or use the platform's import feature if they have one).
- Spiderum readers expect essay-style prose with a personal voice; fewer bullet lists, more connected paragraphs.

**Plain-text social (facebook, linkedin, x)**
- No `#`, `**`, `[text](url)`, tables or code fences — they show up as raw symbols. Use line breaks, short paragraphs, `•` or `–` bullets, and CAPS sparingly (at most one word) instead of bold.
- The hook must be complete in the first 2 lines (≤ ~150 characters): result, problem, or question.
- 1–3 hashtags at the end at most (LinkedIn/X); none needed in Facebook groups.
- Links: the main link at the end, or in the first comment — say which in your reply.
- X threads: one idea per post, number them (1/6), the last post links to the long version.

## Community etiquette (checked in your review, not by the script)

- Disclose affiliation when recommending a product, course or tool the user is connected to.
- Don't post confidential data: client names, internal metrics, unreleased features, colleagues' names — ask the user before publishing anything that looks internal.
- Credit and link original work; do not repost someone's article as your own summary without a link.
- Some communities forbid sharing certain content (e.g. full solutions to graded challenges, proprietary strategies or competition submissions). If the material looks like that, tell the user to check the community rules and keep the post at the level of ideas and methods.
- Help requests: one question per post; follow up with the solution when found.
- Vietnamese groups: "mình/các bạn" peer tone is standard; avoid "AE", teen-code and excessive emoji in technical groups; add "(nguồn: …)" for figures.
