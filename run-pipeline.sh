#!/bin/bash
set -e

CURRENT_NS=$(oc config view --minify -o jsonpath='{.contexts[0].context.namespace}' 2>/dev/null)
USERNAME=$(echo "$CURRENT_NS" | sed 's/-devspaces$\|-build$\|-dev$\|-prod$\|-showroom$//')
NAMESPACE=${1:-${USERNAME}-build}
REPO=$(git remote get-url origin)
BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "Namespace : $NAMESPACE"
echo "Repo      : $REPO"
echo "Branch    : $BRANCH"
echo ""

oc apply -f tekton/tasks/ -f tekton/pipeline.yaml -n "$NAMESPACE"

# If LANGCHAIN_API_KEY is set, create/update a secret and reference it
LANGSMITH_ENV=""
if [ -n "${LANGCHAIN_API_KEY:-}" ]; then
  oc create secret generic langsmith-api-key \
    --from-literal=api-key="$LANGCHAIN_API_KEY" \
    -n "$NAMESPACE" --dry-run=client -o yaml | oc apply -f - -n "$NAMESPACE" > /dev/null
  LANGSMITH_ENV="
        - name: LANGCHAIN_TRACING_V2
          value: \"true\"
        - name: LANGCHAIN_API_KEY
          valueFrom:
            secretKeyRef:
              name: langsmith-api-key
              key: api-key"
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
echo "  tkn pipelinerun logs -n $NAMESPACE --last -f"
