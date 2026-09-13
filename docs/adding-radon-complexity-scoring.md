# Adding Radon Complexity Scoring to the Pipeline

This guide explains how to extend the AI review agent with a cyclomatic complexity tool using `radon`.

---

## What is cyclomatic complexity?

Cyclomatic complexity measures how many independent paths exist through a function. Every branch — `if`, `elif`, `for`, `while`, `try`, `except`, `and`, `or` — adds 1 to the score. The base score starts at 1.

Radon grades functions on a scale of A to F:

| Grade | Score | Meaning |
|---|---|---|
| A | 1–5 | Simple, easy to test, low risk |
| B | 6–10 | Slightly complex, acceptable |
| C | 11–15 | Complex, consider refactoring |
| D | 16–20 | High risk, hard to maintain |
| F | 21+ | Untestable, rewrite strongly recommended |

---

## Example functions by grade

### Grade A — Score 2

```python
def get_user(username):
    if not username:
        return None
    return db.find(username)
```

Simple — one branch, easy to reason about and test.

---

### Grade B — Score 7

```python
def process_payment(amount, currency, method):
    if amount <= 0:
        raise ValueError("Invalid amount")
    if currency not in ["USD", "EUR", "GBP"]:
        raise ValueError("Unsupported currency")
    if method == "card":
        return charge_card(amount, currency)
    elif method == "bank":
        return bank_transfer(amount, currency)
    elif method == "wallet":
        return wallet_pay(amount, currency)
    else:
        raise ValueError("Unknown payment method")
```

Multiple branches but each is clear. Getting complex but manageable.

---

### Grade C — Score 12

```python
def validate_and_save(data, user, strict=False):
    if data:
        if isinstance(data, dict):
            if "name" in data:
                if strict:
                    if len(data["name"]) < 3:
                        return "too_short"
                    elif len(data["name"]) > 100:
                        return "too_long"
                if user:
                    if user.is_active:
                        try:
                            db.save(data)
                            return "saved"
                        except Exception:
                            return "error"
                    else:
                        return "inactive_user"
                else:
                    return "no_user"
            else:
                return "missing_name"
        else:
            return "invalid_format"
    else:
        return "no_data"
```

Deeply nested. Hard to follow, hard to test every path.

---

### Grade D — Score 17

```python
def handle_request(req, user, config, retry=False):
    result = None
    if req:
        if req.method == "GET":
            if user and user.role in ["admin", "viewer"]:
                data = db.fetch(req.resource)
                if data:
                    if config.get("transform"):
                        if config["transform"] == "json":
                            result = json.dumps(data)
                        elif config["transform"] == "csv":
                            result = to_csv(data)
                        else:
                            result = str(data)
                    else:
                        result = data
                else:
                    result = None
            else:
                result = "forbidden"
        elif req.method == "POST":
            if user and user.role == "admin":
                try:
                    db.insert(req.body)
                    result = "created"
                except Exception as e:
                    if retry:
                        db.insert(req.body)
                    else:
                        result = "error"
            else:
                result = "forbidden"
        else:
            result = "method_not_allowed"
    else:
        result = "no_request"
    return result
```

---

### Grade F — Score 23+

A grade F function is typically one that tries to do everything — authentication, validation, database access, transformation, logging, and error handling all in one place, with deeply nested conditions and multiple loops.

```python
def process_everything(req, user, db, config, logger, retry=False, strict=False):
    # ... 60+ lines of deeply nested branches, loops within loops,
    # multiple try/except blocks, and conditional returns scattered throughout
    pass
```

If radon gives a function an F, it should be split into multiple smaller functions immediately.

---

## How to add radon to the pipeline

### Step 1 — Add radon to `images/Dockerfile`

```dockerfile
RUN pip install --no-cache-dir \
    langchain==0.3.25 \
    langchain-anthropic==0.3.15 \
    langgraph==1.0.1 \
    langgraph-prebuilt==1.0.1 \
    flake8==7.3.0 \
    detect-secrets==1.5.0 \
    pip-audit==2.9.0 \
    pytest==8.3.5 \
    radon==6.0.1
```

Rebuild and push the image after this change.

---

### Step 2 — Add the tool to `tekton/tasks/claude-review.yaml`

Add the following `@tool` function alongside the other tools in the script:

```python
@tool
def complexity_scorer() -> str:
    """Run radon to measure cyclomatic complexity. Reports functions graded C or above."""
    r = subprocess.run(
        ["radon", "cc", ws, "-s", "--min", "C"],
        capture_output=True, text=True, timeout=30
    )
    output = r.stdout.strip()
    return output if output else "All functions are within acceptable complexity (grade A or B)."
```

Then add `complexity_scorer` to the tools list:

```python
tools = [run_linter, check_secrets, audit_dependencies, run_tests, read_file, complexity_scorer]
```

---

### Step 3 — Optionally add a rule to `rules/review-rules.json`

```json
{
  "id": "complexity",
  "name": "High Cyclomatic Complexity",
  "description": "Functions graded C or above by radon — hard to test and maintain",
  "severity": "warn",
  "enabled": true
}
```

---

## When the agent uses it

The agent decides when to call `complexity_scorer` based on what it sees in the code. It will typically call it when it notices large functions, deeply nested logic, or multiple branching conditions in the diff. It does not call it on every run — only when relevant.
