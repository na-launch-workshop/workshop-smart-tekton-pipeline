# Available Review Agent Tools

The AI review agent has a set of built-in tools it can call when investigating your code. You can also extend it with optional tools that are pre-installed in the pipeline image.

---

## Built-in tools

These tools are always available — no changes needed.

| Tool | What it does |
|---|---|
| `run_linter` | Runs flake8 — catches syntax errors, style violations, unused imports |
| `check_secrets` | Runs detect-secrets — flags hardcoded passwords, API keys, tokens |
| `audit_dependencies` | Runs pip-audit — checks requirements files for known CVEs |
| `run_tests` | Runs pytest — executes your test suite and reports pass/fail |
| `read_file` | Reads any file in the repo for additional context |

---

## Optional tools

These tools are pre-installed in the pipeline image but need to be wired up in `tekton/tasks/claude-review.yaml`. See the linked guide for each one.

| Tool | What it does | Guide |
|---|---|---|
| `complexity_scorer` | Runs radon — measures cyclomatic complexity, flags complex functions | [Adding Radon](adding-radon-complexity-scoring.md) |
| `bandit_scanner` | Runs bandit — Python security linter, catches eval/exec/injection/weak crypto | [Adding Bandit](adding-bandit-security-scanner.md) |
| `type_checker` | Runs mypy — checks type annotations for correctness | [Adding mypy](adding-mypy-type-checker.md) |
| `dead_code_detector` | Runs vulture — finds unused functions, variables, and imports | [Adding Vulture](adding-vulture-dead-code-detector.md) |

---

## Adding an optional tool

Each optional tool requires two changes in `tekton/tasks/claude-review.yaml`:

1. Add the `@tool` function to the `# ── tools ──` section
2. Add the tool name to the `SYSTEM_PROMPT` tools list and the `tools = [...]` list

See the individual guides above for the exact code to add.
