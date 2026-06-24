# Detailed guidance: Surgical Merge & Audit Skill

> This reference preserves and reorganizes the supplied domain guidance. It is loaded on demand. Verify time-sensitive framework versions, security recommendations, legal requirements, prices, APIs, and platform behavior against authoritative current documentation before applying them. The core `SKILL.md` operating contract takes precedence if guidance conflicts.

# Surgical Merge & Audit Skill

A structured workflow for comparing multiple file versions and producing one definitive
production-ready output with a complete audit trail.

---

## Phase 0 — Intake

1. Identify all input artifacts. List each by version label (V1, V2, vΩ, filename, etc.).
2. Determine artifact type: single file, multi-file bundle/zip, structured config, prompt/doc.
3. If zips: extract all. Map the file tree of each. Run:
   ```bash
   find <dir> -type f | grep -v node_modules | grep -v .git | sort > /tmp/<version>_files.txt
   diff /tmp/v1_files.txt /tmp/v2_files.txt
   ```
4. State the merge goal aloud (one sentence) before touching anything.

---

## Phase 1 — Exhaustive Diff

For each file present in any version:

| Dimension | What to check |
|-----------|--------------|
| **Presence** | File exists in all versions? Missing from any? |
| **Structure** | Sections added/removed/reordered |
| **Logic** | Functions/routes/agents added, removed, changed |
| **Bugs** | Errors introduced or fixed across versions |
| **Regressions** | Features present in older version, missing in newer |
| **Conflicts** | Same identifier defined differently across versions |
| **Quality** | Version that handles edge cases, error paths, typing better |

Build an internal **Comparison Matrix** (not always shown to user unless requested):

```
File / Section | V1 | V2 | V3 | Winner | Notes
```

---

## Phase 2 — Gap Taxonomy

Classify every finding by severity before writing output:

| Tag | Meaning |
|-----|---------|
| **P0** | Blocking — system will not run / silent data corruption |
| **P1** | Ship-blocking — incorrect behavior, broken integration |
| **P2** | Regression — feature lost vs. prior version |
| **P3** | Quality — style, naming, minor inefficiency |
| **KEEP** | Correct in all versions — do not change |
| **CONFLICT** | Versions disagree — requires decision |

For CONFLICT items: state the tradeoff and make a recommendation with rationale.

---

## Phase 3 — Produce Definitive Output

Rules:
- **Best-of-all-versions**: take the superior implementation of each unit, regardless of which version it came from.
- **Never drop without explanation**: if a feature exists in V1 but not V2, consciously decide — restore it or document why it's excluded.
- **Append-only preference**: for config files and CSS, prefer appending corrections over rewriting. For logic files, prefer surgical str_replace over full rewrites when < 30% of the file changes.
- **Version header**: bump the version string (if any) and log the merge in the file's changelog section.
- Always validate: search for any symbol in the merged output that is *called* but never *defined*.

---

## Phase 4 — Audit Trail

Always emit a structured change log after producing output:

```
## Merge Audit — [date]

### Source versions
- V1: [label / filename]
- V2: [label / filename]

### P0 fixes applied
- [item]: [what was wrong] → [what was done]

### P1 fixes applied
- ...

### Regressions restored
- [feature]: present in [vX], absent in [vY] — restored because [reason]

### Conflicts resolved
- [item]: [V1 approach] vs [V2 approach] → chose [X] because [reason]

### Unchanged (verified correct across all versions)
- [list]
```

---

## Output Format

- **Single file**: produce complete file, present via `present_files`.
- **Multi-file bundle**: produce all changed files in `/mnt/user-data/outputs/`, present together.
- **Patch-only mode** (if user asks): produce only the diff/patch blocks with line references.
- Always state: "Files unchanged from any source version: [list]" so the user knows what they don't need to re-copy.

---

## Constraints & Guardrails

- Never silently drop a symbol, function, or config key that exists in any input version.
- Never invent functionality not present in any source version.
- If a version contains a dangerous pattern (e.g., top-level `emulate -L zsh` in a sourced file, duplicate alias+function, missing guard), flag it explicitly as a P0/P1 bug — do not silently propagate it to the merged output.
- For prompt/doc files: preserve all protected sections (marked `<!-- PROTECTED -->` or equivalent) byte-for-byte.
