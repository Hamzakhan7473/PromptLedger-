# Terraform (EKS + platform infra)

Planned modules:

- `modules/eks` — EKS cluster (Terraform AWS provider)
- `modules/platform` — Helm release `promptledger-platform` via ArgoCD
- `modules/data` — RDS Postgres, ElastiCache Redis, S3 bucket, Qdrant on EC2 or managed

```bash
# Scaffold (when AWS credentials configured)
cd deploy/terraform/environments/dev
terraform init
terraform plan
```

Wire GitHub Actions → ECR → ArgoCD Application for `deploy/helm/promptledger-platform`.
