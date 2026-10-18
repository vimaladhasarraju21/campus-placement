#!/usr/bin/env bash
# Runs on every deploy (Render). Idempotent: safe to run again and again.
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Create the placement-cell admin (from env vars) + the demo companies/students/applications.
# Set SEED_DEMO_DATA=false in Render if you ever want a clean, empty system.
if [ "${SEED_DEMO_DATA:-true}" = "true" ]; then
  python manage.py seed_demo_data
else
  python manage.py create_placement_admin --username "${ADMIN_USERNAME:-admin}" --password "${ADMIN_PASSWORD:-admin1234}"
fi
