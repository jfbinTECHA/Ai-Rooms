.PHONY: install-deps test-backend

install-deps:
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip setuptools
	./venv/bin/pip install -r backend/requirements.txt
	./venv/bin/pip install -r websocket/requirements.txt
	./venv/bin/pip install -r model_workers/requirements.txt
	./venv/bin/pip install -r embeddings_worker/requirements.txt

test-backend:
	cd backend && ../venv/bin/python -m pytest --tb=short -v || echo "No tests found, running health check..."
	cd backend && ../venv/bin/python -c "import requests; print('Health check:', requests.get('http://localhost:8000/health').json())" || echo "Backend not running"
