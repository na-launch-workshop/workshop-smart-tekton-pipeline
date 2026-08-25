# Cluster Setup Guide

Steps to deploy the smart pipeline on a new cluster before the workshop.

## Prerequisites

- `oc` logged in as cluster admin
- `podman` installed locally
- Vault running and unsealed
- Vault Kubernetes auth enabled and configured against the cluster

---

## 1. Store the Anthropic API key in Vault

```bash
vault exec -n vault vault-0 -- vault kv put kv/secrets/common/anthropic api-key="sk-ant-..."
```

## 2. Create Vault policy and Kubernetes auth role

```bash
oc exec -n vault vault-0 -- vault policy write smart-pipeline-policy - <<'EOF'
path "kv/data/secrets/common/anthropic" {
  capabilities = ["read"]
}
EOF

oc exec -n vault vault-0 -- vault write auth/kubernetes/role/smart-pipeline-role \
  bound_service_account_names=pipeline \
  bound_service_account_namespaces="*" \
  policies=smart-pipeline-policy \
  ttl=1h
```

## 3. Enable the OpenShift internal registry default route

```bash
oc patch configs.imageregistry.operator.openshift.io cluster \
  --type merge -p '{"spec":{"defaultRoute":true}}'
```

## 4. Create the workspace-images namespace

```bash
oc new-project workspace-images
```

## 5. Build and push the review image

Replace `<registry-route>` with the external registry route:
```bash
oc get route default-route -n openshift-image-registry -o jsonpath='{.spec.host}'
```

Then:
```bash
podman login <registry-route> -u admin -p $(oc whoami -t) --tls-verify=false
podman build -t <registry-route>/workspace-images/smart-pipeline-review:latest images/
podman push <registry-route>/workspace-images/smart-pipeline-review:latest --tls-verify=false
```

## 6. Update cluster-specific values

In `tekton/tasks/claude-review.yaml`, update the `VAULT_ADDR` default to the new cluster's Vault route:
```bash
oc get route -n vault vault -o jsonpath='{.spec.host}'
```

Update the image reference to use the new registry route.

---

## Per-participant setup

Grant each participant's DevSpaces namespace access to their pipeline namespace:

```bash
oc create rolebinding devspaces-pipeline-access \
  --clusterrole=edit \
  --group=system:serviceaccounts:<username>-devspaces \
  -n <username>-devspaces
```

---

## Participant instructions

1. Fork the repo in GitLab
2. Open the fork in DevSpaces
3. From the terminal:
   ```bash
   bash run-pipeline.sh <your-namespace>
   ```
4. Watch the pipeline:
   ```bash
   tkn pipelinerun logs -n <your-namespace> --last -f
   ```
