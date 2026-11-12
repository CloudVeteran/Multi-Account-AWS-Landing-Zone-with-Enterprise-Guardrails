provider "aws" {
  region = var.aws_region
}

module "landing_zone" {
  source = "./modules/landing-zone"

  organization_name = var.organization_name
  email_domain      = var.email_domain
  tags              = var.tags
}

# Attached at the organization root, so member accounts inherit both policies.
# Service control policies do not apply to the management account.
resource "aws_organizations_policy" "deny_root" {
  name        = "DenyRootAccess"
  description = "Deny all actions by the account root user (aws:PrincipalArn like arn:aws:iam::*:root)."
  type        = "SERVICE_CONTROL_POLICY"
  content     = file("${path.module}/policies/deny-root.json")
  tags        = var.tags

  depends_on = [module.landing_zone]
}

resource "aws_organizations_policy" "deny_public_s3" {
  name        = "DenyPublicS3Buckets"
  description = "Deny s3:PutBucketAcl and s3:PutBucketPolicy when aws:SecureTransport is false."
  type        = "SERVICE_CONTROL_POLICY"
  content     = file("${path.module}/policies/deny-public-s3.json")
  tags        = var.tags

  depends_on = [module.landing_zone]
}

resource "aws_organizations_policy_attachment" "deny_root" {
  policy_id = aws_organizations_policy.deny_root.id
  target_id = module.landing_zone.organization_root_id
}

resource "aws_organizations_policy_attachment" "deny_public_s3" {
  policy_id = aws_organizations_policy.deny_public_s3.id
  target_id = module.landing_zone.organization_root_id
}

# Detective controls for the management account in var.aws_region only.
# No delegated administrator and no member-account enablement.
resource "aws_guardduty_detector" "management" {
  enable                       = true
  finding_publishing_frequency = "FIFTEEN_MINUTES"
  tags                         = var.tags
}

resource "aws_securityhub_account" "management" {
  enable_default_standards = false
}

resource "aws_securityhub_standards_subscription" "nist_800_53" {
  standards_arn = "arn:aws:securityhub:${var.aws_region}::standards/nist-800-53/v/5.0.0"

  depends_on = [aws_securityhub_account.management]
}
