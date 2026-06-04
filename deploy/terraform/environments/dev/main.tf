# EKS + PromptLedger platform — dev environment scaffold.
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "cluster_name" {
  type    = string
  default = "promptledger-dev"
}

variable "region" {
  type    = string
  default = "us-east-1"
}

provider "aws" {
  region = var.region
}

# TODO: module "eks" { ... }
# TODO: module "rds" { engine = postgres }
# TODO: module "elasticache" { engine = redis }
# TODO: helm_release "promptledger_platform" { chart = "../../helm/promptledger-platform" }

output "next_steps" {
  value = "Implement EKS module and ArgoCD Application — see deploy/terraform/README.md"
}
