# README Improvements Plan

**Goal:** Apply six targeted improvements to README.md, INTEGRATIONS.md, and the SVG diagram. All changes are documentation-only — no src/ code touched.

**Gates must stay green after every sub-task:**
- `python3 scripts/check_savings_claims.py`
- `python3 scripts/check_status_consistency.py`
- `python3 scripts/check_value_homes.py`
- `uv run python3 scripts/generate_api_docs.py --check`

---

## Sub-task 1 — Remove the retracted-metrics callout from README.md §9

**Intent:**
The ⚠️ Retracted blockquote at README.md:249-251 was necessary when the fabricated
"68.96%" figures were still live on documentation surfaces. The claims gate
(`check_savings_claims.py`) now covers 233 surfaces tree-wide; the fabrication is
fully retracted across every live surface. Keeping a prominent retraction notice in
the primary README sends a negative signal to first-time readers who never saw the
original false claim. Remove the three-line blockquote; the §9 section stands on its
own (positive, manifest-backed) without it.

**Expected Outcomes:**
- README.md:249-251 deleted (three lines starting with `> ⚠️ **Retracted:**`).
- §9 "Token savings" ends cleanly after the null-test bullet.
- `check_savings_claims.py` still passes (removal of a retraction record is safe —
  the 68.96% figure no longer appears on this surface at all, which is correct).
- All 4 gate scripts pass.

**Todo List:**
1. Delete README.md lines 249-251 (the three-line `> ⚠️ **Retracted:**` block).
2. Run `python3 scripts/check_savings_claims.py` — must pass.
3. Run remaining gate scripts — must all pass.

**Relevant Context:**
- README.md:236-252 — full §9 Token savings section
- The 68.96% figure is NOT in §9 as a claim — only as a retraction record. Removing
  the retraction record leaves zero occurrences of "68.96" in README.md, which is the
  correct final state.
- `evaluation/VALIDATION_DISCLAIMER.md` still exists for anyone who needs the history.

**Status:** [ ] pending

---

## Sub-task 2 — Update the ⚠️ two-systems banner to reflect partial integration

**Intent:**
README.md:17-26 states "They share a repository but are **not integrated**." This was
accurate before the P1/P2 integration work. Three opt-in integration points now exist
in shipped code: (1) KB query engine uses TOS embedding scorer, (2) KB Manager mode
calls `bob-optimize` subprocess for context compression, (3) `src/embeddings/`
PersistentEmbeddingIndex bridges KB search with TOS cache infrastructure. The banner
must be updated so new readers get an accurate picture.

The ⚠️ icon and the warn tone should be softened to ℹ️ — this is now a navigation
note, not a danger warning.

**Expected Outcomes:**
- README.md:17 changes from `## ⚠️ This repository contains two separate systems` to
  `## ℹ️ This repository contains two independently-operable systems`.
- README.md:24 changes from "not integrated" to a description of the three opt-in
  integration points and a link to INTEGRATIONS.md.
- The Status column for KB Manager changes from "Stable v1.0" to "Stable v1.0".
  (No change needed — already accurate.)
- All 4 gate scripts pass.

**Todo List:**
1. Read README.md:17-26 for exact current text.
2. Replace heading icon ⚠️ → ℹ️ and update heading text.
3. Replace "They share a repository but are **not integrated**." paragraph with a
   two-sentence description covering the three opt-in integration points and linking
   to INTEGRATIONS.md.
4. Run all 4 gate scripts — must pass.

**Relevant Context:**
- README.md:17-26 — current banner
- INTEGRATIONS.md — the three integration points are §3 (KB Query Engine), §4
  (Context Compression), and now §5 (Persistent Embedding Index)
- Existing integration work: src/embeddings/ (P2), src/tools/kb_query.py (P1-1),
  config/custom_modes.yaml:204-220 (P1-3)

**Status:** [ ] pending

---

## Sub-task 3 — Add "Best for / Key trade-off" columns to the §6 activation paths table

**Intent:**
README.md:28-34 has a paths table (E, A, B, C, D) that lists Activation, Install step,
Skill lazy-load, and save_memory — but no guidance on *when to choose* each path.
A new user reading sequentially cannot answer "which path is right for me?" without
reading all five sections beneath the table.

Add two columns — "Best for" and "Key trade-off" — so the table is self-contained.
This replaces five separate H3 sections' worth of decision overhead with one scannable row.

The five-path H3 sections (Path E, A, B, C, D) below the table remain unchanged —
they are the reference detail.

**Expected Outcomes:**
- README.md:30-34 (the paths table) gains two new columns: `Best for` and `Key trade-off`.
- The per-path H3 sections beneath the table are NOT changed.
- Table remains accurate for both Bob Shell CLI and Bob IDE.
- All 4 gate scripts pass.

**Column values (grounded in code and mode config):**

| Path | Best for | Key trade-off |
|------|----------|--------------|
| E — Bob IDE mode picker | IDE users; zero install | No `save_memory`; file persistence only |
| A — Wrapper script alias | Daily CLI users; one word to start | Requires `install.sh` once + `~/.zshrc` alias |
| B — Direct flag | Occasional CLI use; no alias setup | Must `cd` first; no auto-validation |
| C — Mode switch mid-session | Already in a session; want to pivot | KB maintenance discipline activates only after switch |
| D — Prompt injection | Any mode; no install at all | No template enforcement; re-paste every session |

**Todo List:**
1. Read README.md:28-34 for exact table Markdown.
2. Insert `Best for` and `Key trade-off` columns into the table header and each row.
3. Run all 4 gate scripts — must pass.

**Relevant Context:**
- README.md:28-34 — the supported-targets table
- README.md:138-201 — the five path H3 sections (unchanged)
- config/custom_modes.yaml:222-228 — knowledge-manager groups (read, edit, command,
  browser) confirm what is and is not available per mode

**Status:** [ ] pending

---

## Sub-task 4 — Add repo-analyzer callout to §5 "Get started"

**Intent:**
README.md:98-136 mentions `run-full-analysis.sh` in a bash block without explaining
what it produces or why you run it before starting a KB session. A new user who skips
it gets an empty KB and then asks Bob to "suggest 5 documents" with nothing to ground
the suggestions. The value proposition of `repo-analyzer` — 7 scripts that summarise
the repo into 7 dated research files so Bob never reads raw source — is the strongest
differentiation of this tool but is currently invisible at the point where the user
would need it.

Add a short callout box immediately after the `run-full-analysis.sh` step explaining
what it produces and how that populates the KB.

**Expected Outcomes:**
- README.md: after the `validate-kb.sh` step, a callout block explains:
  (a) what the 7 scripts produce (7 dated Markdown files in docs/knowledge-base/research/ and guides/)
  (b) why this matters (Bob reads 200-line digested reports, not raw source)
  (c) that re-running it later refreshes the dated snapshots without overwriting prior KB work
- The existing prose "The scripts have already filed…" at line 133-134 is updated to
  specifically name what was filed (research/ snapshots).
- All 4 gate scripts pass.

**Todo List:**
1. Read README.md:98-136 for exact section content.
2. Add a blockquote callout after the validate-kb.sh step naming what run-full-analysis.sh
   produces and why it matters before starting a KB session.
3. Update line 133-134 to specifically mention the research/ snapshots.
4. Run all 4 gate scripts — must pass.

**Relevant Context:**
- README.md:98-136 — §5 Get started
- config/custom_modes.yaml:103-113 — exact output locations from repo-analyzer
  (research/repo-scan-YYYY-MM-DD.md, concepts/dependency-analysis.md, etc.)
- docs/knowledge-base/guides/complete-repository-analysis.md — existing detailed guide
  to reference from the callout

**Status:** [ ] pending

---

## Sub-task 5 — Add "Mode switching and the KB" note to §6

**Intent:**
README.md:138-201 explains how to start a KB session but says nothing about what
happens when you switch away to another mode mid-session (e.g. to agent, plan, ask).
This is a real user workflow: code in agent mode, then document findings in
knowledge-manager mode. Without guidance, users either stay stuck in one mode or
lose knowledge that was generated in another mode.

The accurate answer (grounded in how Bob modes work): KB files persist on disk
regardless of mode; the maintenance discipline (templates, INDEX.md, cross-refs) is
mode-specific and only active in knowledge-manager mode. `save_memory` (Bob Shell CLI)
persists across the switch; Bob IDE file persistence is always available.

Add a short section at the end of §6 covering this.

**Expected Outcomes:**
- README.md: after the "Standard resume prompt" block, a new `### Mode switching and the KB`
  subsection explains:
  (a) KB files always exist on disk — switching mode does not delete or hide them
  (b) The 7-step maintenance discipline (templates, cross-refs, INDEX.md) only fires in knowledge-manager mode
  (c) Recommended pattern: use agent/plan/ask for code work, switch back to knowledge-manager to file findings
  (d) `save_memory` facts (Bob Shell CLI) survive the mode switch
- The section is ≤ 120 words (concise — not a tutorial).
- All 4 gate scripts pass.

**Todo List:**
1. Read README.md:191-201 for the end of §6.
2. Insert the new `### Mode switching and the KB` subsection immediately after the
   `> **Full reference:** …` line at the end of §6 (currently line 201).
3. Run all 4 gate scripts — must pass.

**Relevant Context:**
- README.md:138-201 — §6 full content
- config/custom_modes.yaml:180-228 — knowledge-manager mode customInstructions
  (the 7-step workflow is mode-specific — it lives only in these instructions)
- Bob mode switching behaviour: modes are stateless instruction sets; switching
  replaces the active instructions; no persistent agent process exists

**Status:** [ ] pending

---

## Sub-task 6 — Fix SVG diagram (4 issues) and update INTEGRATIONS.md §5

**Intent:**
Two independent fixes bundled as one commit since both are small:

**A — SVG (`docs/assets/kb-compounding-loop.svg`)**

Four confirmed issues (see prior analysis):
1. `repo-analyzer`/scripts are invisible — the arrow "read once" goes repo → Bob directly,
   hiding the fact that 7 Bash scripts do the summarisation step.
2. `research` category chip is missing (diagram shows concepts · guides · references but not research).
3. `save_memory` shown without platform caveat (only Bob Shell CLI; Bob IDE uses file persistence).
4. Return loop arrow points back into the same Bob box (implies same session) — should label
   it as "next session" to reinforce the cross-session value.

Fix all four by editing the SVG directly:
- Add a `Scripts` node between `Your repository` and `Bob Shell` on the top row.
- Add the `research` chip (4th pill) inside the KB box.
- Add `(Bob Shell CLI)` subscript to the `save_memory` line; add `(Bob IDE: file persistence)` below it.
- Relabel the return loop as "next session retrieves" and point it to a new "New session" label.

**B — INTEGRATIONS.md §5**

INTEGRATIONS.md:102-109 still says "P2 — Persistent Embedding Index (**Planned**)" and
"A `src/embeddings/PersistentEmbeddingIndex` **will** bridge…". The package shipped in the
last session. Update to reflect shipped status.

**Expected Outcomes:**
- SVG renders with a Scripts step, 4 category chips, platform-conditional save_memory note,
  and a "next session" label on the return arrow.
- INTEGRATIONS.md §5 heading changes from "(Planned)" to "(Shipped — P2 complete)".
- INTEGRATIONS.md §5 body updates "will bridge" → "bridges", adds a link to
  `src/embeddings/`, mentions ADR-015.
- All 4 gate scripts pass.

**Todo List:**
1. Read docs/assets/kb-compounding-loop.svg in full (78 lines).
2. Edit the SVG:
   a. Move `Your repository` node left (x=40 → x=20) and `Bob Shell` node right slightly.
   b. Add an intermediate `Scripts` rect node between them on the top row.
   c. Change the "read once" arrow to go repo → scripts; add a second arrow scripts → Bob.
   d. Add a 4th chip (`research`) inside the KB rect.
   e. Replace `+ save_memory facts` (line 71) with two lines: `+ save_memory (Bob Shell CLI)` and
      `+ file persistence (Bob IDE)`.
   f. Add a small `New session` text label at the head of the return loop arrow.
3. Read INTEGRATIONS.md:102-109.
4. Update §5 heading, body verb tense, and add ADR-015 link.
5. Run all 4 gate scripts — must pass.

**Relevant Context:**
- docs/assets/kb-compounding-loop.svg — full 78-line SVG
- INTEGRATIONS.md:102-109 — §5 to update
- src/embeddings/__init__.py — confirms package exists and is exported
- docs/adr/015-persistent-embedding-index.md — ADR to link from INTEGRATIONS.md

**Status:** [ ] pending

---

## Execution Order

Sub-tasks are fully independent. Recommended order (trivial → moderate):

```
1  →  Remove retracted callout          (3-line delete, zero risk)
2  →  Update two-systems banner         (paragraph rewrite, low risk)
3  →  Add Best for/Trade-off columns    (table edit, low risk)
4  →  Add repo-analyzer callout         (new content, low risk)
5  →  Add mode-switching note           (new content, low risk)
6  →  Fix SVG + INTEGRATIONS.md §5      (SVG edit + one section rewrite, moderate)
```

Each sub-task is one commit. Run all 4 gates after every commit.
