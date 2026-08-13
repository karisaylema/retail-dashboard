.PHONY: setup data run tf-init tf-plan tf-apply tf-destroy

# ── Local dev ─────────────────────────────────────────────────────────────────
setup:
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt

data:
	./venv/bin/python generate_data.py

run:
	./venv/bin/streamlit run app.py

# ── Terraform ─────────────────────────────────────────────────────────────────
tf-init:
	cd terraform && terraform init

tf-plan:
	cd terraform && terraform plan

tf-apply:
	cd terraform && terraform apply -auto-approve

tf-destroy:
	cd terraform && terraform destroy -auto-approve
