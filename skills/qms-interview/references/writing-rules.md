# Writing rules for drafted QMS content

Distilled from the vault's `AGENTS.md`. These are hard rules; when a rule
here conflicts with anything else, follow `AGENTS.md`.

1. Never fabricate regulatory content. Name clauses ("per ISO 13485:2016
   clause 7.3"); never quote or paraphrase the standard's text - it is
   copyright and is not stored in this vault. Leave `[verify: ...]` for
   anything a human must check against the official text.
2. Never edit a document with `status: approved`. Approved documents change
   only through a revision bump the user explicitly requests.
3. Never write into `05-records/software-validation/`,
   `05-records/distribution/`, `_archive/`, or `.git/`.
4. Never run `git push`, `git tag`, `git merge`, or state-changing `make`
   targets on your own initiative. Show the command, explain it, wait.
5. No "shall". Write procedures as statements of fact ("The Quality Manager
   reviews...") or use "must". "Shall" belongs to the standard, not to the
   organisation's own documents.
6. Dates: frontmatter `YYYY-MM-DD`; body text `DD/MM/YYYY`. Never mix or
   reformat existing dates.
7. No emojis anywhere.
8. UK English, consistently (organisation, sterilisation, authorise).
9. Frontmatter: all 18 fields present; `revision` quoted as a string;
   `clauses` and `related` as inline arrays. Do not reorder or reformat the
   block.
10. Draft section by section with the user reviewing, never a whole
    document unseen. Keep the document's existing structure and heading
    numbering; fill the `[bracketed]` prompts rather than restructuring.
11. Write for the company being interviewed: their devices, their process
    names, their role titles. Generic filler ("the organisation ensures
    quality at all times") is worse than an honest placeholder.
12. Tone: plain, factual, auditable. Short sentences. Present tense. Name
    the role that does each thing.
