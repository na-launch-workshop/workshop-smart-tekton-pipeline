# Adding Radon Complexity Scoring to the Pipeline

This guide explains how to extend the AI review agent with a cyclomatic complexity tool using `radon`.

---

## What is cyclomatic complexity?

Cyclomatic complexity measures how many independent paths exist through a function. Every branch — `if`, `elif`, `for`, `while`, `try`, `except`, `and`, `or` — adds 1 to the score. The base score starts at 1.




## Why is important?
**Testability** — every branch is an independent path through the code that needs its own test case. A function with complexity 15 has up to 15 paths to cover. Most never get tested, which means bugs hide there.

**Bug density** — research shows that higher complexity correlates directly with more defects per line of code. A function scoring D is statistically much more likely to contain bugs than one scoring A, even if it looks clean on the surface.

**Change risk** — when you need to modify a complex function, you can't easily predict what else you'll break. Simple functions are safe to change. Complex ones make developers afraid to touch them, so technical debt compounds over time.

The practical effect: a grade A function takes 5 minutes to understand and test. A grade D function takes an afternoon — and you still might miss something.

---

## Scoring
### Radon grades functions on a scale of A to F:
| Grade | Score | Meaning |
|---|---|---|
| A | 1–5 | Simple, easy to test, low risk |
| B | 6–10 | Slightly complex, acceptable |
| C | 11–15 | Complex, consider refactoring |
| D | 16–50 | High risk, hard to maintain |
| F | 51+ | Untestable, rewrite strongly recommended |

---
## Example functions by grade

### Grade A — Score 2

Simple, low risk. Easy to read, test, and maintain. This is the target for most functions.

```python
def get_user(username):
    if not username:
        return None
    return db.find(username)
```

---

### Grade B — Score 7

Slightly complex but well structured. Acceptable — no action needed, but worth keeping an eye on as the function grows.

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

---

### Grade C — Score 13

Moderate risk. The function is doing too many things. Consider breaking it into smaller, focused functions. The agent will flag this as a warning.

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
                    if "email" in data:
                        if "@" not in data["email"]:
                            return "invalid_email"
                if user:
                    if user.is_active:
                        if user.role in ["admin", "editor"]:
                            try:
                                db.save(data)
                                return "saved"
                            except Exception:
                                return "error"
                        else:
                            return "forbidden"
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

---

### Grade D — Score 29

High risk. Hard to test, hard to maintain, and almost impossible to fully understand without running it. Refactoring is strongly recommended. The agent will flag this and suggest splitting it up.

```python
def handle_request(req, user, config, retry=False, strict=False):
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
                        elif config["transform"] == "xml":
                            result = to_xml(data)
                        else:
                            result = str(data)
                    else:
                        result = data
                    if strict:
                        if not validate_schema(result):
                            result = None
                else:
                    result = "not_found"
            else:
                result = "forbidden"
        elif req.method == "POST":
            if user and user.role == "admin":
                if strict:
                    if not validate_body(req.body):
                        return "invalid_body"
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
        elif req.method == "DELETE":
            if user and user.role == "superadmin":
                db.delete(req.resource)
                result = "deleted"
            else:
                result = "forbidden"
        else:
            result = "method_not_allowed"
    else:
        result = "no_request"
    return result
```

---

### Grade F — Score 51+

Untestable. This function is a liability — every bug fix risks introducing another. It should be rewritten, not refactored. No code review tool will save you here; the architecture is the problem.

```python
def process_everything(req, user, db, config, logger,
                       retry=False, strict=False, audit=False,
                       tenant=None, device_id=None):
    result = None
    if req:
        if user:
            if user.is_active:
                if not user.locked:
                    if tenant:
                        if tenant != user.tenant:
                            return "wrong_tenant"
                        if not tenant.is_active:
                            return "tenant_suspended"
                    if device_id:
                        if device_id not in user.trusted_devices:
                            if user.require_device_trust:
                                return "untrusted_device"
                    if user.role in ["admin", "superadmin", "editor"]:
                        if req.method == "GET":
                            data = db.fetch(req.resource)
                            if data:
                                if config.get("transform"):
                                    if config["transform"] == "json":
                                        result = json.dumps(data)
                                    elif config["transform"] == "csv":
                                        result = to_csv(data)
                                    elif config["transform"] == "xml":
                                        result = to_xml(data)
                                    else:
                                        result = str(data)
                                else:
                                    result = data
                                if strict:
                                    if not validate_schema(result):
                                        result = None
                            else:
                                result = "not_found"
                        elif req.method == "POST":
                            try:
                                if strict:
                                    if not validate_body(req.body):
                                        return "invalid_body"
                                db.insert(req.body)
                                result = "created"
                            except Exception as e:
                                if retry:
                                    try:
                                        db.insert(req.body)
                                        result = "created_on_retry"
                                    except Exception:
                                        result = "failed"
                                else:
                                    result = "error"
                        elif req.method == "PUT":
                            if strict:
                                if not validate_body(req.body):
                                    return "invalid_body"
                            if user.role in ["admin", "superadmin"]:
                                db.update(req.resource, req.body)
                                result = "updated"
                            else:
                                result = "forbidden"
                        elif req.method == "PATCH":
                            if req.body:
                                if strict:
                                    if not validate_body(req.body):
                                        return "invalid_body"
                                db.patch(req.resource, req.body)
                                result = "patched"
                            else:
                                result = "empty_patch"
                        elif req.method == "DELETE":
                            if user.role == "superadmin":
                                if strict:
                                    if not confirm_delete(req.resource):
                                        return "delete_not_confirmed"
                                db.delete(req.resource)
                                result = "deleted"
                            else:
                                result = "forbidden"
                        else:
                            result = "method_not_allowed"
                    else:
                        result = "forbidden"
                else:
                    result = "account_locked"
            else:
                result = "inactive_user"
        else:
            result = "no_user"
    else:
        result = "no_request"

    if audit and result:
        try:
            if logger:
                logger.info(f"{user.role} {req.method} {result}")
            else:
                print(f"audit: {result}")
        except Exception:
            pass

    return result
```

---

## Run radon from the CLI

You can run radon directly from your terminal without the pipeline:

```bash
# Install
pip install radon

# Show all functions with grades
radon cc app/ -s

# Only show functions graded C or above
radon cc app/ -s --min C

# Show a summary by file
radon cc app/ -s --average

# Get a full complexity report in JSON
radon cc app/ -s --json
```

This is useful for quickly checking your code before triggering the pipeline.

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

This is the image the pipeline will run in. You will see this image when the pipeline kicks off.

---

### Step 2 — Add the tool to `tekton/tasks/claude-review.yaml`

Add the following `@tool` function alongside the other tools in the `script:` section of `claude-review.yaml`:

```python
@tool
def complexity_scorer() -> str:
    """Run radon to measure cyclomatic complexity. Reports functions graded C or above."""
    r = subprocess.run(
        ["radon", "cc", WORKSPACE, "-s", "--min", "C"],
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

### Step 3 — Update the system prompt in `tekton/tasks/claude-review.yaml`

The agent only knows about tools that are listed in the system prompt. Find the `SYSTEM_PROMPT` variable in the `script:` section and add one line to the tools section:

```
- complexity_scorer: run radon to measure cyclomatic complexity of functions
```

So it looks like:

```python
You have tools to actively investigate the code before reaching a verdict:
- run_linter: flake8 syntax and style check
- check_secrets: detect-secrets scan for hardcoded credentials
- audit_dependencies: pip-audit CVE check on requirements files
- run_tests: execute pytest and return results
- read_file: read any file in the repo for additional context
- complexity_scorer: run radon to measure cyclomatic complexity of functions
```

Without this, the agent won't know to call `complexity_scorer` even though it's registered.

---

### Step 4 — Optionally add a rule to `rules/review-rules.json`

```json
{
  "id": "complexity",
  "name": "High Cyclomatic Complexity",
  "description": "Functions graded C or above by radon — hard to test and maintain",
  "severity": "warn",
  "enabled": true
}
```

Adding this rule tells the agent that complexity has a named, intentional policy in your project. Without it, the agent may still flag complex functions based on what radon returns, but it won't tie the finding to a specific rule ID or know the expected severity. With it, the agent references `complexity` in its findings JSON, the output is consistent across runs, and you can disable it entirely by setting `"enabled": false` — without changing any code. Set `"severity": "block"` if you want complex functions to stop the build entirely.

---

## When the agent uses it

The agent decides when to call `complexity_scorer` based on what it sees in the code. It will typically call it when it notices large functions, deeply nested logic, or multiple branching conditions in the diff. It does not call it on every run — only when relevant.

