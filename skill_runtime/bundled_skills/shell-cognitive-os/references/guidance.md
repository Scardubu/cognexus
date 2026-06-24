# Detailed guidance: Shell Cognitive OS Surgical Fix Skill

> This reference preserves and reorganizes the supplied domain guidance. It is loaded on demand. Verify time-sensitive framework versions, security recommendations, legal requirements, prices, APIs, and platform behavior against authoritative current documentation before applying them. The core `SKILL.md` operating contract takes precedence if guidance conflicts.

# Shell Cognitive OS Surgical Fix Skill

Deep static analysis and production-grade correction of zsh/bash shell configurations.

---

## Phase 0 — Read & Classify

1. Read the full file(s). Never truncate the audit.
2. Identify:
   - Shell: `zsh` / `bash` / `fish`
   - OS target: WSL2 (GNU tools) / macOS (BSD) / Linux bare metal
   - RAM constraint: extract from comments or ask
   - Plugin manager: Oh My Zsh, Zinit, Prezto, none
   - Key tools referenced: starship, zoxide, fzf, nvm, bun, ollama, etc.
3. Check if multiple files need merging (e.g., `.zshrc` + `.ai-helpers.zsh`)

---

## Phase 1 — Static Audit

Run every check. Never skip a category.

### 1A — Critical Bugs (P0)

| Pattern | Why it's a bug |
|---------|---------------|
| `emulate -L zsh` at file top level (not inside function) | `-L` flag does NOT scope back after sourcing — permanently mutates parent shell options |
| `setopt no_unset` / `pipe_fail` at file top level | Same — unscoped option changes leak to all sourced files |
| Function AND alias with same name | Function shadows alias silently — one is dead code |
| `compinit` called after `source "$ZSH/oh-my-zsh.sh"` | OMZ already calls compinit internally — double-init wastes 80–150ms minimum |
| Plugin listed AND function manually defined (e.g., `extract`) | Double definition — behavior is undefined, order-dependent |
| `eval "$(tool init zsh)"` without `command -v tool >/dev/null` guard | Hard crash if tool not installed |
| `autoload -Uz compinit && compinit` before OMZ source | OMZ will re-init, negating the cache |

### 1B — Missing Definitions (P1)

- Functions called but never defined anywhere in the file
- Variables referenced (`$SCAR_LOG_DIR`, `$TAXBRIDGE_ROOT`, etc.) but never exported
- Aliases referencing commands that may not be installed without guards
- Completion functions (`_function_name`) loaded with `compdef` but never defined

### 1C — Namespace Collisions (P1)

- Global variables set without `local` inside functions
- `free_mem=$(...)` type bare global assignments that pollute namespace
- Functions with generic names that may conflict with system tools (`extract`, `update`, `open`)

### 1D — Performance (P2)

- `nvm` eagerly loaded at startup (adds 200–800ms) — should use lazy-load pattern
- `conda init` block eagerly evaluating instead of lazy
- Multiple `eval "$(X init zsh)"` calls at startup
- `compinit` without `-C` flag (skips security check on cached dumpfile — safe in trusted environments)
- `zsh-syntax-highlighting` loaded before completions (causes slowdown)

### 1E — Portability (P2)

- `grep -P` (PCRE) used on macOS where BSD grep has no `-P` — must use `grep -E` or `ggrep`
- `free -h` used on macOS (not available — use `vm_stat` instead)
- `date --iso-8601` used on macOS (use `date -u +%Y-%m-%dT%H:%M:%SZ`)
- `readlink -f` used on macOS (use `greadlink -f` or `$(cd "$(dirname "$1")"; pwd)/$(basename "$1")`)

### 1F — Correctness & Completeness (P1)

- Functions listed in `scar_help` / `README` block but never defined in the file
- Stubs: functions that are a comment block only (`# TODO: implement`)
- Auto-run at file bottom that double-fires because `.zshrc` already calls it
- Duplicate alias definitions (same alias defined on 2+ lines)
- Version header not updated to match actual changes

---

## Phase 2 — Correction Protocol

**For each P0/P1 bug:**
1. State what the bug is and why it's dangerous
2. Show the fix inline with a comment explaining the change
3. Never silently remove functionality — if a function is stubbed, implement it or mark it `# NOT YET IMPLEMENTED — see Phase 2`

**Lazy-load pattern for heavy tools:**
```zsh
# Lazy nvm — loads only on first invocation
_load_nvm() {
  unfunction _load_nvm node npm npx nvm 2>/dev/null
  export NVM_DIR="$HOME/.nvm"
  [[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh"
}
if [[ -s "$HOME/.nvm/nvm.sh" ]] && ! typeset -f nvm >/dev/null; then
  node() { _load_nvm && node "$@"; }
  npm()  { _load_nvm && npm  "$@"; }
  npx()  { _load_nvm && npx  "$@"; }
  nvm()  { _load_nvm && nvm  "$@"; }
fi
```

**Safe option scoping:**
```zsh
# WRONG (top-level — leaks):
emulate -L zsh
setopt pipe_fail

# CORRECT (inside function — scoped):
my_function() {
  emulate -L zsh
  setopt pipe_fail
  ...
}
```

---

## Phase 3 — SCAR OS Standards

Upgraded shell configs must meet:

- **Version header**: `# SCAR Cognitive Shell OS · v[YEAR].[MONTH].[REV] · ELITE`
- **Changelog block**: last 3–5 entries with date and description
- **Section structure**: numbered `§` sections with clear labels
- **Welcome banner**: opt-in via `SCAR_WELCOME=1` env var, not auto-run
- **`scar_help()` function**: full command reference in a 78-char box
- **Vertical awareness**: `TAXBRIDGE_ROOT`, `SABISCORE_ROOT`, `HASHABLANCA_ROOT` exported
- **RAM-aware**: model loading and daemon starts respect the RAM constraint
- **WSL2 compatibility**: `free -m` over `vm_stat`, GNU tools assumed unless macOS detected

---

## Phase 4 — Output

- Produce **complete corrected file(s)** — never partial
- Multi-file output: each file complete and independently functional
- Close with **Correction Summary**:
  ```
  ## Correction Summary

  ### P0 fixes (X)
  - [bug]: [what was wrong] → [what was done]

  ### P1 fixes (X)
  - ...

  ### Missing implementations added (X)
  - [function]: [what it does]

  ### Unchanged (verified correct)
  - [list]
  ```
- Present via `present_files` for download
