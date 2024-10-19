frontend-dbg:
    cd frontend/project-galaxy-front && npm run dev

frontend-build:
    cd frontend/project-galaxy-front && npm run build

backend-dbg:
    DEBUG= python app.py

fmt:
    isort --profile black -l 120 .
    black -l 120 .

test:
    pytest

create-tables:
    PYTHONPATH=$PWD python database/create_tables.py

delete-tables:
    PYTHONPATH=$PWD python database/delete_tables.py