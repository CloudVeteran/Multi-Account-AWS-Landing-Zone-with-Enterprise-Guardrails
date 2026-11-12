variable "aws_region" {
  description = "Region for the state bucket and the KMS key. Use this same value as region in backend.hcl."
  type        = string
  default     = "us-east-1"
}

variable "state_bucket_name" {
  description = "Globally unique name for the Terraform state bucket. No default, so the name is not hard-coded."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.state_bucket_name))
    error_message = "state_bucket_name must be 3-63 characters and use only lowercase letters, numbers, dots, and hyphens."
  }
}

variable "tags" {
  description = "Tags applied to the state bucket and the KMS key."
  type        = map(string)
  default = {
    Project     = "Landing-Zone"
    Environment = "Management"
    Owner       = "Marlon"
    Compliance  = "NIST-800-53"
    ManagedBy   = "Terraform"
  }
}
