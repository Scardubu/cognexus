# Detailed guidance: Production Codebase Zip Audit Skill

> This reference preserves and reorganizes the supplied domain guidance. It is loaded on demand. Verify time-sensitive framework versions, security recommendations, legal requirements, prices, APIs, and platform behavior against authoritative current documentation before applying them. The core `SKILL.md` operating contract takes precedence if guidance conflicts.

# Production Codebase Zip Audit Skill

Structured workflow for extracting, deeply auditing, and producing surgical patches for
uploaded production codebase bundles.

---

## Phase 0 — Extract & Map

```bash
# Extract (exclude macOS metadata)
unzip -q /mnt/user-data/uploads/<file>.zip -x "__MACOSX/*" -d /home/claude/repo

# Map structure
find /home/claude/repo -type f | grep -v node_modules | grep -v .git | sort
```

Identify and read in this order:
1. `package.json` / `pnpm-lock.yaml` — stack versions, scripts
2. `tsconfig.json` — strict mode, path aliases
3. `app/layout.tsx` + `app/page.tsx` — entry points
4. `app/globals.css` — design token system, component classes
5. Key components (Hero, Nav, major sections)
6. `lib/` data files, motion variants, utilities
7. Config files: `next.config.*`, `tailwind.config.*`

---

## Phase 1 — Audit Dimensions

Run through every dimension systematically. Never skip.

### 1A — Build Correctness
- Missing imports / unresolved path aliases (`@/lib/motion`, `@/components/ui`)
- TypeScript errors that would block `tsc --noEmit`
- Duplicate exports, conflicting type definitions
- `package.json` vs `pnpm-lock.yaml` version mismatches

### 1B — Runtime Correctness
- Undefined functions/hooks called
- Duplicate `style` props on the same JSX element (last-write-wins — silent data loss)
- Missing `key` props in maps
- SSR hydration mismatches (browser-only APIs without guards)
- Incorrect CSS class references (class used in TSX but never defined in globals.css)

### 1C — Accessibility (WCAG 2.2 AA)
- Interactive `<span>` / `<div>` elements that should be `<button>` (touch targets)
- Missing `aria-label` on icon-only controls
- `outline: none` without `:focus-visible` replacement
- `:focus` firing on mouse clicks instead of `:focus-visible`
- Touch target size < 24×24px (WCAG 2.5.5)
- Missing skip-nav link

### 1D — Performance
- Heavy `motion` imports instead of `m.` with `LazyMotion + domAnimations`
- `useEffect` with missing or incorrect deps
- `@property` CSS variables declared but never animated
- GPU overdraw from radial gradients at full intensity on mobile
- Images without `width`/`height` or `priority` prop

### 1E — Responsive Layout
- Horizontal overflow at 320px viewport
- Text overflow / truncation at smallest breakpoint
- Touch targets not reachable on mobile
- Ultra-wide (1920px+) containers looking sparse

### 1F — Design System Integrity
- CSS custom properties referenced but never declared
- Token naming inconsistencies across files
- `!important` overrides suppressing correct cascade rules
- Duplicate rule definitions (same selector defined twice with different values)

---

## Phase 2 — Prioritize

| Priority | Tag | Action |
|----------|-----|--------|
| P0 | Build-blocking | Fix before anything else |
| P1 | Runtime bug / silent data loss | Fix in same patch |
| P2 | Accessibility violation | Fix in same patch |
| P3 | Performance / responsive | Fix or document |
| P4 | Polish / enhancement | Fix if time, else document |

---

## Phase 3 — Surgical Output

**Preference order:**
1. `str_replace` patches for files where < 30% changes
2. Append-only blocks to CSS (never rewrite the whole file)
3. Full file replacement only when > 50% of file changes

**For CSS patches**, always append as a clearly delimited block:
```css
/* ══ AUDIT PATCH v[version] ════════════════════════════════════ */
/* [description of what this fixes] */
```

**Always verify the merged output:**
```bash
# Check no referenced class is undefined
grep -oP '(?<=className=")[^"]+' components/*.tsx | tr ' ' '\n' | sort -u > /tmp/used_classes.txt
grep -oP '^\.[a-z][a-zA-Z-]+' app/globals.css | sort -u > /tmp/defined_classes.txt
comm -23 /tmp/used_classes.txt /tmp/defined_classes.txt  # should be empty or known globals
```

---

## Phase 4 — File Manifest

Always close with a structured manifest:

```
## File Manifest

| File | Change Type | Priority | Description |
|------|-------------|----------|-------------|
| components/HeroSection.tsx | Surgical patch | P0+P2 | Fix duplicate style prop, upgrade dots to <button> |
| app/globals.css | Append patch block | P1+P3 | Add missing classes, fix :focus vs :focus-visible |
| lib/motionVariants.ts | Full replace | P0 | Fix TypeScript Variant cast errors |
```

List unchanged files explicitly: "All other files are unchanged and correct."

---

## Stack-Specific Notes

### Next.js 15 / React 19
- Verify `'use client'` directives on all components using hooks or browser APIs
- Check for deprecated `next/font` patterns
- `Partial Prerendering` opt-in requires explicit `<Suspense>` boundaries

### Framer Motion
- `LazyMotion` + `domAnimations` + `m.` prefix is required for code-splitting
- `AnimatePresence` must wrap conditionally rendered children, not the parent
- `useScroll` / `useTransform` must be called at component top level

### Tailwind CSS v4
- JIT purge relies on static class strings — no dynamic class construction
- Custom design tokens go in `@theme` block, not `extend`

### TypeScript Strict Mode
- `as unknown as T` is acceptable for Framer Motion `Variant` cast issues
- Never use `any` — use `unknown` + narrowing or proper generic constraints
