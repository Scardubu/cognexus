# Detailed guidance: Portfolio Conviction Engine Skill

> This reference preserves and reorganizes the supplied domain guidance. It is loaded on demand. Verify time-sensitive framework versions, security recommendations, legal requirements, prices, APIs, and platform behavior against authoritative current documentation before applying them. The core `SKILL.md` operating contract takes precedence if guidance conflicts.

# Portfolio Conviction Engine Skill

Systematic audit and surgical elevation of developer portfolio sites and their
governing specification documents.

---

## Core Philosophy

A portfolio for a Staff+ Lagos-forged engineer must:
1. **Convert two audiences simultaneously**: technical evaluators need systems thinking signals; non-technical decision-makers need trust, speed, and risk-reduction signals
2. **Reward scrutiny**: the deeper a visitor explores, the stronger their conviction should become
3. **Embody SCAR precision**: restraint over decoration, purposeful over impressive
4. **Never fabricate**: no invented metrics, clients, awards, or capabilities

---

## Phase 0 — Intake

Identify what has been provided:
- **Source code** (zip): run codebase-zip-audit skill first for correctness, then return here for conviction layer
- **Spec document** (Conviction Engine .md): audit and enhance the governing prompt
- **Screenshots + spec**: visual + strategic audit
- **Live site URL**: fetch and audit in-browser representation
- **Specific section**: targeted section-level audit

Read any uploaded files fully before writing a single word of output.

---

## Phase 1 — Trust & Conversion Audit

Score each section against these conversion dimensions:

| Dimension | Questions |
|-----------|----------|
| **Immediate authority** | Can a technical evaluator confirm Staff+ signal in < 5 seconds? |
| **Proof density** | Are claims backed by specific, verifiable evidence (repo names, metrics, system names)? |
| **Narrative momentum** | Does each section's closing sentence pull the visitor into the next? |
| **CTA clarity** | Is the primary action obvious? Is friction minimal? |
| **Mobile-first** | Does the full conviction arc work on a 375px viewport? |
| **Depth reward** | Does deeper scrolling/exploring reveal more conviction, not less? |

### Behavioral Frameworks (Apply Deliberately)

| Framework | Application |
|-----------|------------|
| **Fogg Behavior Model** | Increase motivation (proof density), reduce friction (fast CTA), timely prompts (sticky nav) |
| **Hook Model** | Trigger curiosity in Hero, reward exploration in Projects/Skills, investment via contact |
| **Cialdini** | Authority (Staff+ label, production metrics), Social proof (GitHub activity, OSS contributions), Unity (Lagos identity as shared context) |
| **Nielsen Norman** | Recognition over recall (skill tags, not just skill names), minimalist hierarchy, error prevention |

**Dark pattern prohibition**: No fake urgency, misleading availability, inflated metrics, invented testimonials.

---

## Phase 2 — Section-Level Audit

### Hero
- Does the H1 communicate role + differentiator in < 10 words?
- Is the Lagos identity framed as an asset, not an apology?
- Are the proof metrics (years, projects, skills) specific and verifiable?
- Is the primary CTA above the fold on mobile?
- Status indicators (live badge, GitHub activity) — real data or hardcoded?

### Projects
- Does each project card communicate: what it does, what stack was used, what problem it solved?
- Are "WHY" blocks present for each project (not just what, but why it was built)?
- Cross-link system: do related projects/packages reference each other?
- Filter system: accessible on mobile? Includes FINTECH/COMPLIANCE category?

### Skills
- Is the full-stack signal clear (not just backend, not just frontend)?
- Are skills grouped by domain, not alphabetically?
- Do 62+ skills feel comprehensive without feeling exhausting?

### Open Source
- Is OSS contribution provably real (links to merged PRs, actual repo names)?
- Metrics: contribution count, merged PRs, license type — verifiable?

### About
- Narrative arc: origin → constraint → discipline → precision?
- Lagos context embedded as advantage, not background noise?
- "The incision is precise" philosophy visible or implicit?

### Contact
- Is friction minimal? (Email copy-to-clipboard, no form required for initial contact)
- Response time signal present?
- CTA hover state reveals additional trust information?

---

## Phase 3 — Diagnosis Tags

Use these named tags in audit output for precision:

| Tag | Meaning |
|-----|---------|
| `DELIGHT_MISS` | Interactive opportunity missed (hover state, copy-to-clipboard, easter egg) |
| `TRUST_GAP` | Claim present but evidence absent |
| `NARRATIVE_BREAK` | Section ends without momentum into the next |
| `SILOED_PROOF` | Related projects/systems not cross-linked |
| `CONVERSION_LEAK` | User intent present but CTA path broken or unclear |
| `FABRICATION_RISK` | Metric or claim that cannot be verified from codebase |
| `MOBILE_FAIL` | Interaction or content not accessible on 375px viewport |
| `A11Y_VIOLATION` | WCAG 2.2 AA failure |

---

## Phase 4 — Spec Document (Conviction Engine) Upgrade

When the user uploads a Conviction Engine .md / implementation guide:

1. Read the full document — extract current version, protected sections, and invariants
2. Audit against: trust dimensions, conversion framework completeness, diagnosis taxonomy, section coverage, mobile-first directives
3. Identify gaps: missing categories, weak copy directives, absent behavioral framework applications
4. Apply surgical additions (never remove, never version-bump unless requested):
   - Add missing surface imperatives as table rows
   - Add missing diagnosis tags
   - Strengthen copy directives with specific examples
   - Add cross-link schema if absent
5. Produce the complete updated document

**Protected section rule**: Any section marked `PROTECTED`, `DO NOT MODIFY`, or equivalent must be preserved byte-for-byte.

---

## Phase 5 — Component Output

For code-level fixes:

- Prefer surgical `str_replace` over full rewrites
- CSS corrections: append as named patch block to globals.css
- Component fixes: produce complete updated TSX file
- Always accompany code output with a **Testing Recommendations** block:
  ```
  ## Testing Recommendations

  ### Viewport Grid
  320×568 / 375×667 / 390×844 / 768×1024 / 1280×800 / 1440×900 / 1920×1080

  ### Automated
  - Lighthouse: npx lighthouse [url] --form-factor=mobile
  - Playwright viewport sweep

  ### Manual
  - [ ] [specific interaction to verify]
  ```

---

## Constraints & Guardrails

- Never invent metrics, client names, project names, or testimonials not present in source
- Never remove content without documenting the removal and reason
- "Elevated" ≠ "more". Restraint is the aesthetic. Remove noise before adding signal.
- All motion must respect `prefers-reduced-motion`
- All interactive elements must have minimum 44×44px touch targets (WCAG 2.5.5)
