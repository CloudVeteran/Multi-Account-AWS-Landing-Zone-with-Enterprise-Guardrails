output "organization_id" {
  description = "Identifier of the AWS Organization."
  value       = aws_organizations_organization.this.id
}

output "organization_root_id" {
  description = "Identifier of the organization root."
  value       = aws_organizations_organization.this.roots[0].id
}

output "organizational_unit_ids" {
  description = "Map of organizational unit key to OU ID."
  value       = { for key, ou in aws_organizations_organizational_unit.this : key => ou.id }
}

output "account_ids" {
  description = "Map of member account key to AWS account ID."
  value       = { for key, account in aws_organizations_account.this : key => account.id }
}

output "account_emails" {
  description = "Map of member account key to the email address used to create it."
  value       = { for key, account in aws_organizations_account.this : key => account.email }
}
