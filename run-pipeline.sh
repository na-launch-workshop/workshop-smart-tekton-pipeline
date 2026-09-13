#!/bin/bash
set -e

NAMESPACE=$(oc project -q)
REPO=$(git remote get-url origin)
BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "Namespace : $NAMESPACE"
echo "Repo      : $REPO"
echo "Branch    : $BRANCH"
echo ""

oc apply -f tekton/tasks/ -f tekton/pipeline.yaml -n "$NAMESPACE"

# Build optional LangSmith env vars if set
LANGSMITH_ENV=""
if [ -n "${LANGCHAIN_API_KEY:-}" ]; then
  LANGSMITH_ENV="
        - name: LANGCHAIN_TRACING_V2
          value: \"true\"
        - name: LANGCHAIN_API_KEY
          value: \"$LANGCHAIN_API_KEY\""
fi

oc create -n "$NAMESPACE" -f - <<EOF
apiVersion: tekton.dev/v1
kind: PipelineRun
metadata:
  generateName: smart-pipeline-run-
  labels:
    app.kubernetes.io/part-of: smart-pipeline
spec:
  pipelineRef:
    name: smart-pipeline
  params:
    - name: git-url
      value: "$REPO"
    - name: git-revision
      value: "$BRANCH"
    - name: claude-model
      value: "claude-sonnet-5"
  taskRunTemplate:
    podTemplate:
      env:$LANGSMITH_ENV
  workspaces:
    - name: shared-workspace
      volumeClaimTemplate:
        spec:
          accessModes:
            - ReadWriteOnce
          resources:
            requests:
              storage: 1Gi
EOF

echo ""
echo "Pipeline triggered. Watch logs with:"
echo "  tkn pipelinerun logs --last -f"
