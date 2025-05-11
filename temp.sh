#!/bin/bash

mkdir -p app/api/routes
mkdir -p app/core
mkdir -p app/db/repositories
mkdir -p app/services
mkdir -p app/schemas
mkdir -p app/utils
mkdir -p alembic/versions
mkdir -p tests/test_api

touch app/api/__init__.py
touch app/api/dependencies.py
touch app/api/routes/__init__.py
touch app/api/routes/auth.py
touch app/api/routes/documents.py
touch app/api/routes/registry.py
touch app/api/routes/owners.py
touch app/api/routes/customers.py
touch app/api/routes/tasks.py
touch app/api/routes/reports.py

touch app/core/__init__.py
touch app/core/config.py
touch app/core/security.py

touch app/db/__init__.py
touch app/db/database.py
touch app/db/models.py
touch app/db/repositories/__init__.py
touch app/db/repositories/documents.py
touch app/db/repositories/owners.py
touch app/db/repositories/customers.py
touch app/db/repositories/tasks.py

touch app/services/__init__.py
touch app/services/extract_info.py
touch app/services/auto_mode.py
touch app/services/extract_zipcode.py
touch app/services/merge_data.py
touch app/services/pdf_processing.py

touch app/schemas/__init__.py
touch app/schemas/auth.py
touch app/schemas/documents.py
touch app/schemas/owners.py
touch app/schemas/customers.py
touch app/schemas/tasks.py

touch app/utils/__init__.py
touch app/utils/helpers.py

touch app/__init__.py
touch app/main.py

touch alembic/env.py
touch alembic/README
touch alembic/script.py.mako
touch alembic/alembic.ini

touch tests/__init__.py
touch tests/conftest.py
touch tests/test_api/__init__.py
touch tests/test_api/test_documents.py
touch tests/test_api/test_owners.py

touch .env
touch requirements.txt
touch README.md
