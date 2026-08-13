output "dashboard_url" {
  description = "Public URL of the Streamlit dashboard"
  value       = "http://${aws_instance.app.public_ip}:${var.streamlit_port}"
}

output "public_ip" {
  description = "EC2 public IP address"
  value       = aws_instance.app.public_ip
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ${var.project_name}.pem ec2-user@${aws_instance.app.public_ip}"
}

output "s3_bucket" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.data.id
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.app.id
}
