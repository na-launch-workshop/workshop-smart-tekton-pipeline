# Adding Bandit Security Scanner to the Pipeline

This guide explains how to extend the AI review agent with a Python-specific security scanner using `bandit`.

---

## What is Bandit?

Bandit is a security linter for Python. It scans your code for common security issues that general linters like flake8 miss — things like use of `eval`, weak cryptography, hardcoded passwords, SQL string formatting, and unsafe subprocess calls.

Bandit assigns each finding a severity (LOW, MEDIUM, HIGH) and a confidence level, so the agent can prioritise what matters.

### Example findings Bandit catches

| Issue | Severity |
|---|---|
| `eval()` or `exec()` with user input | HIGH |
| SQL query built with string formatting | MEDIUM |
| Hardcoded password or secret | MEDIUM |
| `subprocess.call(shell=True)` | HIGH |
| Use of MD5 or SHA1 for hashing | MEDIUM |
| Binding to `0.0.0.0` | LOW |
| Use of `pickle` for deserialization | MEDIUM |

---

## Run Bandit from the CLI

You can run Bandit directly from your terminal without the pipeline:

```bash
# Install
pip install bandit

# Scan the app directory
bandit -r app/

# Scan and show only MEDIUM and HIGH severity
bandit -r app/ -l

# Output as JSON for programmatic use
bandit -r app/ -f json

# Skip specific tests
bandit -r app/ --skip B101,B601
```

---

## How to add Bandit to the pipeline

Bandit is pre-installed in the pipeline image — no Dockerfile changes needed.

### Step 1 — Add the tool to `tekton/tasks/claude-review.yaml`

Add the following `@tool` function alongside the other tools in the `script:` section:

```python
@tool
def bandit_scanner() -> str:
    """Run bandit to scan for Python security issues. Reports MEDIUM and HIGH severity findings."""
    r = subprocess.run(
        ["bandit", "-r", WORKSPACE, "-f", "json", "-l"],
        capture_output=True, text=True, timeout=60
    )
    try:
        data = json.loads(r.stdout)
        results = data.get("results", [])
        if not results:
            return "No security issues found by bandit."
        findings = []
        for issue in results:
            findings.append(
                f"[{issue['issue_severity']}] {issue['test_id']}: {issue['issue_text']}\n"
                f"  at {issue['filename']}:{issue['line_number']}"
            )
        return "\n".join(findings)
    except Exception:
        return r.stdout.strip() or r.stderr.strip() or "Bandit scan completed with no output."
```

Then add `bandit_scanner` to the tools list:

```python
tools = [complexity_scorer, bandit_scanner, run_linter, check_secrets, audit_dependencies, run_tests, read_file]
```

---

### Step 2 — Update the system prompt in `tekton/tasks/claude-review.yaml`

Add `bandit_scanner` to the tools list in `SYSTEM_PROMPT`:

```
        - bandit_scanner: scan for Python security issues using bandit (MEDIUM and HIGH severity)
```

---

### Step 3 — Optionally add a rule to `rules/review-rules.json`

```json
{
  "id": "bandit-security",
  "name": "Bandit Security Finding",
  "description": "Python security issue detected by bandit — eval, subprocess injection, weak crypto, hardcoded secrets",
  "severity": "block",
  "enabled": true
}
```

Adding this rule ties bandit findings to an explicit policy. Set `"severity": "warn"` if you want findings to be noted but not block the build.

---

## Why Bandit matters

Bandit catches things that detect-secrets and flake8 miss. detect-secrets looks for credential patterns; Bandit looks for *insecure coding patterns* — how code is written, not just what values are in it.

A developer might write perfectly formatted, secret-free code that still uses `subprocess.call(shell=True, input=user_data)` — flake8 won't flag it, detect-secrets won't flag it, but Bandit will.
