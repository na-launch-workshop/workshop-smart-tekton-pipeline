# 🚀 Module: Smart Tekton Pipeline

A CI pipeline with an AI-assisted code review gate. Before the build runs, an AI agent reviews your code using real tools — linter, secrets scanner, dependency auditor, and test runner — and decides whether to approve, warn, or block the build.

## How it works

1. **Clone** — pipeline fetches your code from GitLab
2. **AI Review** — agent investigates the code with tools and produces a verdict
3. **Build** — only runs if the agent approves or warns; blocked on serious issues

## Running the pipeline from DevSpaces

### 1. Fork the repo

In GitLab, open the workshop repo and click **Fork**. (be sure to move to your workspaace)

### 2. Unprotect the main branch

In your fork go to **Settings → Repository → Protected branches**, find `main` and click **Unprotect**. This allows you to push changes directly.

### 3. Open your fork in DevSpaces

From the DevSpaces dashboard, create a new workspace using your fork's GitLab URL.

### 4. Make some code changes

Edit files in `app/main.py` or elsewhere. The agent will review whatever is in your repo.

### 5. Push your changes

```bash
git add .
git commit -m "my changes"
git push origin main
```

### 6. Run the pipeline

```bash
bash run-pipeline.sh
```

### 7. Watch the logs

```bash
tkn pipelinerun logs --last -f
```

---

## Optional: trace agent runs with LangSmith

Sign up for a free account at [smith.langchain.com](https://smith.langchain.com), create a project, and get an API key. Then before running the pipeline:

```bash
export LANGCHAIN_API_KEY=ls-...
```

The script will automatically pass it into the pipeline. Open LangSmith to watch the agent's tool calls, reasoning, and token usage in real time.

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
