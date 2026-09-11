# thevinotheca.com

This repository holds the published content of the public site at thevinotheca.com, served by Cloudflare Pages directly from the `main` branch. Everything committed here is published. Nothing enters this repository that is not intended for publication: no working documents, drafts, notes, planning material, credentials or configuration for other systems.

## Conventions

1. **The site carries no build step.** Cloudflare Pages is configured to build nothing. Pages are plain files. The three leaves that are Vite applications (Region Affinities, Region Resonances, Grape Resonances) are built in a session in this directory, with `base` set to the leaf's address, and their `dist` output is committed at that address. Their source trees remain in their own repositories.

2. **Existing leaf HTML is not rewritten.** The migration pass is limited to: adding a missing viewport meta tag, consolidating duplicated CSS, removing vestigial files, and rewriting links to the new addresses. Anything beyond that is a separate decision and is not taken inside a migration task.

3. **Git.** The agent stages files and writes commits. The operator pushes. No branch is created or switched; all work is on `main`. A commit takes its identity from this directory's git configuration; `--author` and `GIT_AUTHOR_*` are never passed, and a commit message carries no trailer — no Co-Authored-By, no session link. A commit message states what changed in plain terms.

4. **Commands are kept to the minimal form that works.** An elaborated command is a deviation to correct, not an improvement.

5. **Nothing is checked piecemeal.** A check over a set of files is run over the whole set at every depth; an incomplete check is widened and re-run whole rather than extended.

6. **A direction addressed by one file to another is reported.** Where a file states that another is to be amended, the direction is reported together with whether the amendment appears in the current version of the file addressed, and reported even where it does.

7. **This file imports nothing** and names no location outside this directory.
