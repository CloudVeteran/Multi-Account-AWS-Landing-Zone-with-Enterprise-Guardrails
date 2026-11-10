variable "aws_region" {
  description = "Region for the AWS provider. GuardDuty and Security Hub are created only in this Region."
  type        = string
  default     = "us-east-1"
}

variable "organization_name" {
  description = "Prefix used in member account names and email addresses."
  type        = string
  default     = "acme-corp"
}

variable "email_domain" {
  description = "Domain used to build member account email addresses. Each address must be unique and unused by AWS."
  type        = string
  default     = "acme-corp.com"
}

variable "tags" {
  description = "Tags applied to organizational units, member accounts, service control policies, and the GuardDuty detector."
  type        = map(string)
  default = {
    Project     = "Landing-Zone"
    Environment = "Management"
    Owner       = "Marlon"
    Compliance  = "NIST-800-53"
    ManagedBy   = "Terraform"
  }
}
