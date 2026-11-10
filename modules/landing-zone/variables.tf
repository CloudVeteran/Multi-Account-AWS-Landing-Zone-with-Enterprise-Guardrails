variable "organization_name" {
  description = "Prefix used in member account names and email addresses."
  type        = string
}

variable "email_domain" {
  description = "Domain used to build member account email addresses."
  type        = string
}

variable "tags" {
  description = "Tags applied to organizational units and member accounts."
  type        = map(string)
}
