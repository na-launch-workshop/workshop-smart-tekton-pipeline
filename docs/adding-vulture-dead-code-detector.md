# Adding Vulture Dead Code Detector to the Pipeline

This guide explains how to extend the AI review agent with dead code detection using `vulture`.

---

## What is Vulture?

Vulture scans Python code for unused functions, variables, imports, and classes — code that is defined but never called or referenced anywhere. Dead code is a maintenance hazard: it confuses readers, inflates the codebase, and can mask bugs if someone assumes unused code is tested.

### Example dead code Vulture catches

| Type | Example |
|---|---|
| Unused function | `def validate_user(data): return data` — defined but never called |
| Unused variable | `SECRET_KEY = "..."` — assigned but never read |
| Unused import | `import os` at the top of a file that never uses `os` |
| Unused class | A class defined but never instantiated |
| Unreachable code | Code after `return` in a function |

---

## Run Vulture from the CLI

```bash
# Install
pip install vulture

# Scan the app directory
vulture app/

# Set a minimum confidence threshold (0-100)
vulture app/ --min-confidence 80

# Whitelist specific names to ignore
vulture app/ --ignore-names "test_*,setUp,tearDown"
```

Vulture reports confidence as a percentage — lower confidence means it's less sure the code is truly dead (e.g. it might be called dynamically).

---

## How to add Vulture to the pipeline

Vulture is pre-installed in the pipeline image — no Dockerfile changes needed.

### Step 1 — Add the tool to `tekton/tasks/claude-review.yaml`

Add the following `@tool` function alongside the other tools in the `script:` section:

```python
@tool
def dead_code_detector() -> str:
    """Run vulture to find unused functions, variables, and imports."""
    r = subprocess.run(
        ["vulture", WORKSPACE, "--min-confidence", "80"],
        capture_output=True, text=True, timeout=30
    )
    output = r.stdout.strip()
    return output if output else "No dead code found."
```

Then add `dead_code_detector` to the tools list:

```python
tools = [complexity_scorer, bandit_scanner, type_checker, dead_code_detector, run_linter, check_secrets, audit_dependencies, run_tests, read_file]
```

---

### Step 2 — Update the system prompt in `tekton/tasks/claude-review.yaml`

Add `dead_code_detector` to the tools list in `SYSTEM_PROMPT`:

```
        - dead_code_detector: run vulture to find unused functions, variables, and imports
```

---

### Step 3 — Optionally add a rule to `rules/review-rules.json`

```json
{
  "id": "dead-code",
  "name": "Dead Code",
  "description": "Unused functions, variables, or imports detected by vulture — increases maintenance burden",
  "severity": "info",
  "enabled": true
}
```

Dead code is typically `info` severity — it's a cleanliness issue rather than a security or reliability risk. Move it to `warn` if you want to enforce a stricter no-dead-code policy.

---

## Why dead code matters

Dead code in a workshop setting is particularly educational — the broken `app/main.py` deliberately includes `validate_input`, `validate_user`, and `process_data` as no-op pass-through functions that do nothing and are never called. Vulture would catch all three immediately.

For participants, seeing vulture flag their own unused code makes the concept concrete and gives them something actionable to clean up.
