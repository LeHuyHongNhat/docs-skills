# Reader test — check the text with a reader who has none of your context

The writer cannot see their own gaps: everything missing from the page is still present in their head. A reader test puts the finished text in front of a reader who has only the page, asks the questions a real reader would ask, and compares the answers with what the writer meant.

Run it when the text goes to people who were not in the conversation: a post to publish, a spec for approval, a README for new developers. Skip it for point edits and for drafts the user will rework anyway.

## 1. Write the questions first (5–8)

Write them before re-reading the draft, from the reader's side:

| Kind | Example for a post | Example for a spec / README |
|---|---|---|
| The point | What is the one thing this post claims? | What does this feature do, in one sentence? |
| The number | How large is the effect, and how sure is the author? | What is the threshold in FR-007, and is the boundary included? |
| The scope | For whom / when does this not apply? | What is explicitly out of scope? |
| The action | What should I do differently after reading? | What do I run first? What do I need installed? |
| The term | What does <term used in the text> mean? | Who is the "operator" in section 3? |
| The gap | What did the author not test? | What happens when the payment fails? |
| The trap | A question whose honest answer is "the text does not say" | same |

Include at least one trap question. A reader who answers it confidently has been misled by the text — or is filling gaps with guesses, which real readers also do.

Write down the answer you expect for each question before the test.

## 2. Run the test

**If you can start a fresh agent (subagent / Task tool):** give it only the text and the questions — no conversation, no source material, no skill instructions. Use this prompt:

```text
You are a reader who has only the text below. Answer each question using only what the text says.
For each answer, quote the sentence(s) you relied on. If the text does not answer a question, reply
"The text does not say" — do not use outside knowledge and do not guess.
Then list: (a) any sentence you had to read twice, (b) any term used before it is explained,
(c) any two statements that seem to disagree.

<text>
…
</text>

Questions:
1. …
```

For a post with a mixed audience, run two readers: a newcomer ("you are new to this topic") and a critical specialist ("you review such work for a living; also list every claim that is stronger than its evidence").

**If you cannot start a fresh agent:** do a cold read yourself. Answer each question by quoting lines from the text only; where you cannot quote, the answer is "the text does not say", even if you know it. Tell the user this was a self-test (weaker: you share the writer's context) and offer the questions so they can try them in a fresh chat or with a colleague.

## 3. Compare and fix

| Reader's answer | Meaning | Fix |
|---|---|---|
| Matches the expected answer, quotes the right sentence | The text works here | — |
| Right answer, but pieced together from distant sentences | The point is buried | Move it up; state it once, plainly |
| Wrong answer with a quote | The sentence is ambiguous or misleading | Rewrite that sentence |
| "The text does not say" for a non-trap question | A gap | Add the fact — or, if you do not have it, say it is unknown |
| A confident answer to the trap question | The text implies something it should not | Find the sentence that implies it and bound it |
| Read-twice sentences, unexplained terms, disagreements | Clarity defects | Fix each |

Read the specialist's list of over-strong claims even when every question was answered correctly: comprehension questions show whether the text is understood, the critique shows whether it is right. In the first run on four sample posts, both readers answered all 27 questions correctly, and the specialist readers still found the defects that mattered (a title claiming equivalence from a non-difference, "measured" used for self-reported time, a causal "because" without a measurement).

Re-run only the questions that failed, once. If the same question fails again, the problem is the structure of that section, not its wording: rewrite the section around the answer.

## 4. Report

In the hand-off, state: how the test was run (fresh agent or self-test), how many questions, how many failed at first, and what was changed. Do not claim a reader test that was not run.
