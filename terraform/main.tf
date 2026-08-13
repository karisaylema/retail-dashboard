terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ── Data sources ──────────────────────────────────────────────────────────────
data "aws_caller_identity" "current" {}

data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-2023*-x86_64"]
  }
  filter {
    name   = "state"
    values = ["available"]
  }
}

# ── S3 bucket ─────────────────────────────────────────────────────────────────
resource "aws_s3_bucket" "data" {
  bucket        = "${var.project_name}-${data.aws_caller_identity.current.account_id}"
  force_destroy = true

  tags = {
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "dataset" {
  bucket = aws_s3_bucket.data.id
  key    = "data/retail_data.csv"
  source = "${path.module}/../data/retail_data.csv"
  etag   = filemd5("${path.module}/../data/retail_data.csv")
}

locals {
  app_files = {
    "app/app.py"                        = "${path.module}/../app.py"
    "app/requirements.txt"              = "${path.module}/../requirements.txt"
    "app/Dockerfile"                    = "${path.module}/../Dockerfile"
    "app/src/__init__.py"               = "${path.module}/../src/__init__.py"
    "app/src/config.py"                 = "${path.module}/../src/config.py"
    "app/src/data/__init__.py"          = "${path.module}/../src/data/__init__.py"
    "app/src/data/loader.py"            = "${path.module}/../src/data/loader.py"
    "app/src/components/__init__.py"    = "${path.module}/../src/components/__init__.py"
    "app/src/components/charts.py"      = "${path.module}/../src/components/charts.py"
    "app/src/components/echarts.py"     = "${path.module}/../src/components/echarts.py"
    "app/src/components/kpi.py"         = "${path.module}/../src/components/kpi.py"
    "app/src/components/sidebar.py"     = "${path.module}/../src/components/sidebar.py"
  }
}

resource "aws_s3_object" "app_files" {
  for_each = local.app_files
  bucket   = aws_s3_bucket.data.id
  key      = each.key
  source   = each.value
  etag     = filemd5(each.value)
}

# ── IAM role for EC2 → S3 ─────────────────────────────────────────────────────
resource "aws_iam_role" "ec2_role" {
  name = "${var.project_name}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = { Project = var.project_name }
}

resource "aws_iam_role_policy" "s3_read" {
  name = "${var.project_name}-s3-read"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:ListBucket"]
      Resource = [
        aws_s3_bucket.data.arn,
        "${aws_s3_bucket.data.arn}/*"
      ]
    }]
  })
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.project_name}-profile"
  role = aws_iam_role.ec2_role.name
}

# ── Key pair (auto-generated) ─────────────────────────────────────────────────
resource "tls_private_key" "ssh_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "deployer" {
  key_name   = "${var.project_name}-key"
  public_key = tls_private_key.ssh_key.public_key_openssh
}

resource "local_sensitive_file" "private_key" {
  content         = tls_private_key.ssh_key.private_key_pem
  filename        = "${path.module}/../${var.project_name}.pem"
  file_permission = "0400"
}

# ── Security group ────────────────────────────────────────────────────────────
resource "aws_security_group" "app" {
  name        = "${var.project_name}-sg"
  description = "SSH + Streamlit access"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  ingress {
    description = "Streamlit"
    from_port   = var.streamlit_port
    to_port     = var.streamlit_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Project = var.project_name }
}

# ── EC2 instance ──────────────────────────────────────────────────────────────
resource "aws_instance" "app" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.deployer.key_name
  vpc_security_group_ids = [aws_security_group.app.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name

  user_data = templatefile("${path.module}/user_data.sh", {
    s3_bucket      = aws_s3_bucket.data.id
    streamlit_port = var.streamlit_port
    aws_region     = var.aws_region
  })

  tags = {
    Name      = var.project_name
    Project   = var.project_name
    ManagedBy = "terraform"
  }
}
