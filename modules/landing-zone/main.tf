locals {
  organizational_units = {
    security = {
      name = "Security"
    }
    workloads = {
      name = "Workloads"
    }
    infrastructure = {
      name = "Infrastructure"
    }
  }

  # name is the suffix for the AWS account name and the email local-part.
  accounts = {
    security = {
      name   = "security"
      ou_key = "security"
    }
    logging = {
      name   = "logging"
      ou_key = "security"
    }
    audit = {
      name   = "audit"
      ou_key = "security"
    }
    prod = {
      name   = "prod"
      ou_key = "workloads"
    }
    nonprod = {
      name   = "nonprod"
      ou_key = "workloads"
    }
    shared = {
      name   = "shared-services"
      ou_key = "infrastructure"
    }
  }
}

resource "aws_organizations_organization" "this" {
  feature_set                   = "ALL"
  enabled_policy_types          = ["SERVICE_CONTROL_POLICY"]
  aws_service_access_principals = []
}

resource "aws_organizations_organizational_unit" "this" {
  for_each = local.organizational_units

  name      = each.value.name
  parent_id = aws_organizations_organization.this.roots[0].id
  tags      = var.tags
}

resource "aws_organizations_account" "this" {
  for_each = local.accounts

  name                       = "${var.organization_name}-${each.value.name}"
  email                      = "${var.organization_name}-${each.value.name}@${var.email_domain}"
  parent_id                  = aws_organizations_organizational_unit.this[each.value.ou_key].id
  role_name                  = "OrganizationAccountAccessRole"
  iam_user_access_to_billing = "DENY"
  close_on_deletion          = false
  tags                       = var.tags
}
