#!/bin/bash
set -e

NAMESPACE=${1:-$(oc project -q)}
REPO=$(git remote get-url origin)
BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "Namespace : $NAMESPACE"
echo "Repo      : $REPO"
echo "Branch    : $BRANCH"
echo ""

oc apply -f tekton/tasks/ -f tekton/pipeline.yaml -n "$NAMESPACE"

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