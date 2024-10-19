.PHONY: frontend-dbg
frontend-dbg:
	cd frontend/project-galaxy-front && npm run dev

.PHONY: frontend-build
frontend-build:
	cd frontend/project-galaxy-front && npm run build

.PHONY: backend-dbg
backend-dbg:
	DEBUG= python app.py

.PHONY: fmt
fmt:
	isort --profile black -l 120 .
	black -l 120 .

.PHONY: test
test:
	pytest

.PHONY: create-tables
create-tables:
	PYTHONPATH=$(PWD) python database/create_tables.py

.PHONY: delete-tables
delete-tables:
	PYTHONPATH=$(PWD) python database/delete_tables.py