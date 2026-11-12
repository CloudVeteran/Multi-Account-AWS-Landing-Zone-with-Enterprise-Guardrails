output "state_bucket_name" {
  description = "Value for bucket in backend.hcl."
  value       = aws_s3_bucket.state.id
}

output "state_bucket_region" {
  description = "Value for region in backend.hcl."
  value       = var.aws_region
}

output "state_kms_key_arn" {
  description = "Value for kms_key_id in backend.hcl. Terraform uses this key for SSE-KMS on the state and lock objects."
  value       = aws_kms_key.state.arn
}
