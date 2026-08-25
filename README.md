# Smart Tekton Pipeline

A CI pipeline with an AI-assisted code review gate. Before the build runs, an AI agent reviews your code using real tools — linter, secrets scanner, dependency auditor, and test runner — and decides whether to approve, warn, or block the build.

## How it works

1. **Clone** — pipeline fetches your code from GitLab
2. **AI Review** — agent investigates the code with tools and produces a verdict
3. **Build** — only runs if the agent approves or warns; blocked on serious issues

## Running the pipeline from DevSpaces

### 1. Fork the repo

In GitLab, open the workshop repo and click **Fork**.

### 2. Open your fork in DevSpaces

From the DevSpaces dashboard, create a new workspace using your fork's GitLab URL.

### 3. Make some code changes

Edit files in `app/main.py` or elsewhere. The agent will review whatever is in your repo.

### 4. Push your changes

```bash
git add .
git commit -m "my changes"
git push origin main
```

### 5. Run the pipeline

```bash
bash run-pipeline.sh <your-namespace>
```

Replace `<your-namespace>` with the namespace your facilitator assigned to you (e.g. `user1-devspaces`).

### 6. Watch the logs

```bash
tkn pipelinerun logs -n <your-namespace> --last -f
```

---

## Review rules

The agent enforces rules defined in `rules/review-rules.json`. Each rule has a severity:

| Severity | Effect |
|---|---|
| `block` | Pipeline stops — must be fixed before build |
| `warn` | Build proceeds but findings are reported |
| `info` | Informational only |

You can edit `rules/review-rules.json` to add, remove, or adjust rules and thresholds.

## Project structure

```
app/                  # Sample Python application
  main.py
  tests/
images/               # Dockerfile for the AI review container image
rules/                # Configurable review rules
tekton/
  pipeline.yaml       # Pipeline definition
  pipelinerun.yaml    # Example pipeline run
  tasks/              # Tekton task definitions
run-pipeline.sh       # Helper script to trigger a pipeline run
```
