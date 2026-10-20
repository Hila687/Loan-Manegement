#!/usr/bin/env bash
# Native (non-Docker) build, e.g. a Render "Python" service.
# The recommended path is the Dockerfile at the repository root, which also
# builds the Vue app; see DEPLOY.md.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createcachetable
