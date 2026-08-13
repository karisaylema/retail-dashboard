#!/bin/bash
set -e
exec > /var/log/user-data.log 2>&1

# ── Docker ────────────────────────────────────────────────────────────────────
yum update -y
yum install -y docker
systemctl enable docker
systemctl start docker

# ── Pull app source from S3 ───────────────────────────────────────────────────
mkdir -p /app/src/data /app/src/components /app/data

aws s3 cp s3://${s3_bucket}/app/app.py              /app/app.py
aws s3 cp s3://${s3_bucket}/app/requirements.txt    /app/requirements.txt
aws s3 cp s3://${s3_bucket}/app/Dockerfile          /app/Dockerfile
aws s3 cp s3://${s3_bucket}/app/src/config.py       /app/src/config.py
aws s3 cp s3://${s3_bucket}/app/src/__init__.py      /app/src/__init__.py
aws s3 cp s3://${s3_bucket}/app/src/data/loader.py  /app/src/data/loader.py
aws s3 cp s3://${s3_bucket}/app/src/data/__init__.py /app/src/data/__init__.py
aws s3 cp s3://${s3_bucket}/app/src/components/charts.py   /app/src/components/charts.py
aws s3 cp s3://${s3_bucket}/app/src/components/echarts.py  /app/src/components/echarts.py
aws s3 cp s3://${s3_bucket}/app/src/components/kpi.py      /app/src/components/kpi.py
aws s3 cp s3://${s3_bucket}/app/src/components/sidebar.py  /app/src/components/sidebar.py
aws s3 cp s3://${s3_bucket}/app/src/components/__init__.py /app/src/components/__init__.py
aws s3 cp s3://${s3_bucket}/data/retail_data.csv    /app/data/retail_data.csv

# ── Build Docker image ────────────────────────────────────────────────────────
cd /app
docker build -t retail-dashboard:latest .

# ── systemd service (runs the container) ──────────────────────────────────────
cat > /etc/systemd/system/retail-dashboard.service <<EOF
[Unit]
Description=Retail Dashboard — Docker container
After=docker.service
Requires=docker.service

[Service]
Restart=always
RestartSec=5
ExecStartPre=-/usr/bin/docker rm -f retail-dashboard
ExecStart=/usr/bin/docker run --rm \
    --name retail-dashboard \
    -p ${streamlit_port}:8501 \
    -v /app/data:/app/data:ro \
    -e LOCAL_PATH=/app/data/retail_data.csv \
    -e AWS_REGION=${aws_region} \
    -e S3_BUCKET=${s3_bucket} \
    retail-dashboard:latest
ExecStop=/usr/bin/docker stop retail-dashboard

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable retail-dashboard
systemctl start retail-dashboard
