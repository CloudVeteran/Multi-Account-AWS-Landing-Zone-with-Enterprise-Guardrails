# Partial S3 backend. encrypt and use_lockfile are set here.
# bucket, region, and kms_key_id come from backend.hcl (see backend.hcl.example):
#   terraform init -backend-config=backend.hcl
# Validate without contacting AWS:
#   terraform init -backend=false && terraform validate
terraform {
  backend "s3" {
    key          = "landing-zone/terraform.tfstate"
    encrypt      = true
    use_lockfile = true
  }
}
