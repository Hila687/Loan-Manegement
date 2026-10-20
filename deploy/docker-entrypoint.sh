#!/bin/sh
# Container entry point.
#   web        - prepare the database, then run the site (default)
#   reminders  - send payment reminders once a day at REMINDERS_HOUR
#   backup     - one backup now;  backup-loop - a backup every night
#   anything else is passed to manage.py (e.g. "createsuperuser")
set -e

wait_for_db() {
  python - <<'PY'
import sys, time
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_project.settings")
django.setup()
from django.db import connection
for attempt in range(60):
    try:
        connection.ensure_connection()
        sys.exit(0)
    except Exception as exc:
        print(f"waiting for database... ({exc.__class__.__name__})", flush=True)
        time.sleep(2)
sys.exit("database not reachable")
PY
}

seconds_until() {
  # seconds until the next HH:00 local time
  python -c "
import datetime as d, sys
h=int(sys.argv[1]); now=d.datetime.now()
nxt=now.replace(hour=h, minute=0, second=0, microsecond=0)
if nxt<=now: nxt+=d.timedelta(days=1)
print(int((nxt-now).total_seconds()))" "$1"
}

case "$1" in
  web)
    wait_for_db
    python manage.py migrate --noinput
    python manage.py createcachetable
    exec gunicorn backend_project.wsgi:application \
      --bind "0.0.0.0:${PORT:-8000}" \
      --workers "${WEB_CONCURRENCY:-3}" \
      --timeout "${GUNICORN_TIMEOUT:-60}" \
      --forwarded-allow-ips "*" \
      --access-logfile - \
      --error-logfile -
    ;;
  reminders)
    wait_for_db
    while true; do
      sleep "$(seconds_until "${REMINDERS_HOUR:-9}")"
      python manage.py send_payment_reminders || echo "reminders run failed"
    done
    ;;
  backup)
    exec backup.sh
    ;;
  backup-loop)
    wait_for_db
    while true; do
      sleep "$(seconds_until "${BACKUP_HOUR:-2}")"
      backup.sh || echo "backup failed"
    done
    ;;
  *)
    exec python manage.py "$@"
    ;;
esac
