.PHONY: setup data run docker-build docker-run docker-stop docker-logs tf-init tf-plan tf-apply tf-destroy

IMAGE  = retail-dashboard
PORT   = 8501

# ── Local dev (Python) ────────────────────────────────────────────────────────
setup:
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt

data:
	./venv/bin/python generate_data.py

run:
	./venv/bin/streamlit run app.py

# ── Docker ────────────────────────────────────────────────────────────────────
docker-build:
	docker build -t $(IMAGE):local .

docker-run: docker-build
	docker compose up -d
	@echo "Dashboard → http://localhost:$(PORT)"

docker-stop:
	docker compose down

docker-logs:
	docker compose logs -f

# ── Terraform ─────────────────────────────────────────────────────────────────
tf-init:
	cd terraform && terraform init

tf-plan:
	cd terraform && terraform plan

tf-apply:
	cd terraform && terraform apply -auto-approve

tf-destroy:
	cd terraform && terraform destroy -auto-approve
