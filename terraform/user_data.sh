#!/bin/bash
set -e
exec > /var/log/user-data.log 2>&1

# ── System deps ───────────────────────────────────────────────────────────────
yum update -y
yum install -y python3 python3-pip

# ── App directory ─────────────────────────────────────────────────────────────
mkdir -p /app/data /app/src

# ── Pull files from S3 ────────────────────────────────────────────────────────
aws s3 cp s3://${s3_bucket}/app/app.py          /app/app.py
aws s3 cp s3://${s3_bucket}/app/requirements.txt /app/requirements.txt
aws s3 cp s3://${s3_bucket}/data/retail_data.csv /app/data/retail_data.csv

# ── Python venv + dependencies ────────────────────────────────────────────────
python3 -m venv /app/venv
/app/venv/bin/pip install --quiet --upgrade pip
/app/venv/bin/pip install --quiet -r /app/requirements.txt

# ── Env vars ──────────────────────────────────────────────────────────────────
cat > /app/.env <<EOF
S3_BUCKET=${s3_bucket}
AWS_REGION=${aws_region}
LOCAL_PATH=/app/data/retail_data.csv
EOF

# ── systemd service ───────────────────────────────────────────────────────────
cat > /etc/systemd/system/streamlit.service <<EOF
[Unit]
Description=Retail Dashboard — Streamlit
After=network.target

[Service]
User=root
WorkingDirectory=/app
EnvironmentFile=/app/.env
ExecStart=/app/venv/bin/streamlit run app.py \
    --server.port ${streamlit_port} \
    --server.headless true \
    --server.address 0.0.0.0
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable streamlit
systemctl start streamlit
