output "organization_id" {
  description = "AWS Organization ID."
  value       = module.landing_zone.organization_id
}

output "organization_root_id" {
  description = "Organization root ID. Both service control policies are attached here."
  value       = module.landing_zone.organization_root_id
}

output "organizational_unit_ids" {
  description = "Map of organizational unit key to OU ID."
  value       = module.landing_zone.organizational_unit_ids
}

output "account_ids" {
  description = "Map of member account key to AWS account ID."
  value       = module.landing_zone.account_ids
}

output "account_emails" {
  description = "Map of member account key to the email address used to create it."
  value       = module.landing_zone.account_emails
}

output "scp_policy_ids" {
  description = "Map of service control policy key to Organizations policy ID."
  value = {
    deny_root      = aws_organizations_policy.deny_root.id
    deny_public_s3 = aws_organizations_policy.deny_public_s3.id
  }
}

output "guardduty_detector_id" {
  description = "GuardDuty detector ID in the management account and var.aws_region."
  value       = aws_guardduty_detector.management.id
}

output "securityhub_standards_arn" {
  description = "Security Hub standard subscribed in the management account."
  value       = aws_securityhub_standards_subscription.nist_800_53.standards_arn
}
