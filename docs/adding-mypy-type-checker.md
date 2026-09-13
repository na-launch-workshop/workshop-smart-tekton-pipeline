# Adding mypy Type Checking to the Pipeline

This guide explains how to extend the AI review agent with static type checking using `mypy`.

---

## What is mypy?

mypy is a static type checker for Python. It reads type annotations in your code and verifies they're consistent — catching type mismatches, missing return types, and functions called with the wrong argument types, all before the code runs.

Python is dynamically typed, so these errors normally only surface at runtime. mypy brings compile-time safety to Python.

### Example issues mypy catches

| Issue | Example |
|---|---|
| Wrong argument type | `get_user(123)` when username should be `str` |
| Missing return type | Function annotated `-> str` that sometimes returns `None` |
| Attribute doesn't exist | Calling `.upper()` on a value that could be `None` |
| Incompatible types | Assigning `int` to a variable typed as `str` |
| Unreachable code | Code after an unconditional `return` |

---

## Run mypy from the CLI

```bash
# Install
pip install mypy

# Check the app directory
mypy app/

# Strict mode — catches more issues
mypy app/ --strict

# Ignore missing stubs for third-party packages
mypy app/ --ignore-missing-imports

# Output as JSON
mypy app/ --output json
```

---

## How to add mypy to the pipeline

mypy is pre-installed in the pipeline image — no Dockerfile changes needed.

### Step 1 — Add the tool to `tekton/tasks/claude-review.yaml`

Add the following `@tool` function alongside the other tools in the `script:` section:

```python
@tool
def type_checker() -> str:
    """Run mypy to check type annotations for consistency and correctness."""
    r = subprocess.run(
        ["mypy", WORKSPACE, "--ignore-missing-imports", "--no-error-summary"],
        capture_output=True, text=True, timeout=60
    )
    output = (r.stdout + r.stderr).strip()
    if not output or "Success" in output:
        return "No type errors found."
    return output[:5000]
```

Then add `type_checker` to the tools list:

```python
tools = [complexity_scorer, bandit_scanner, type_checker, run_linter, check_secrets, audit_dependencies, run_tests, read_file]
```

---

### Step 2 — Update the system prompt in `tekton/tasks/claude-review.yaml`

Add `type_checker` to the tools list in `SYSTEM_PROMPT`:

```
        - type_checker: run mypy to check type annotations for correctness
```

---

### Step 3 — Optionally add a rule to `rules/review-rules.json`

```json
{
  "id": "type-errors",
  "name": "Type Annotation Errors",
  "description": "mypy found type mismatches or incorrect annotations that could cause runtime failures",
  "severity": "warn",
  "enabled": true
}
```

---

## Why type checking matters

Type annotations are documentation that the computer can verify. Without type checking, a function like:

```python
def get_user(username: str) -> dict:
    ...
```

Can be called with `get_user(None)` and fail at runtime in production. mypy catches this before the code ships.

For a workshop app, type errors are typically `warn` not `block` — they indicate code quality issues rather than security problems. As the codebase matures, you can move them to `block` to enforce stricter standards.
