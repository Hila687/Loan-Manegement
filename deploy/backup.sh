#!/bin/sh
# Nightly backup: the database (pg_dump) and the uploaded signed forms.
# Keeps the last BACKUP_KEEP_DAYS days (default 30) in $BACKUP_DIR.
set -e
umask 077  # backups hold personal data: owner-only files

STAMP="$(date +%Y-%m-%d_%H%M)"
DIR="${BACKUP_DIR:-/data/backups}"
mkdir -p "$DIR"

URL="${DATABASE_URL:-postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT:-5432}/${DB_NAME}}"

pg_dump --no-owner --format=custom "$URL" > "$DIR/db_$STAMP.dump"
tar -czf "$DIR/media_$STAMP.tar.gz" -C "${MEDIA_ROOT:-/data/media}" .

find "$DIR" -type f -mtime +"${BACKUP_KEEP_DAYS:-30}" -delete

echo "backup done: $DIR/db_$STAMP.dump, $DIR/media_$STAMP.tar.gz"
