# CertGuardian Deployment

## Process

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
CERTGUARDIAN_DB=/var/lib/certguardian/certguardian.db \
  uvicorn app.api:app --host 127.0.0.1 --port 8001
```

Run `certguardian watch --database /var/lib/certguardian/certguardian.db --poll-seconds 60` under a supervisor for scheduled scans. Use one writer process per SQLite database.

## Container

```bash
docker compose up --build -d
curl --fail http://127.0.0.1:8001/health
```

The reference mapping is loopback-only. Add an authenticated TLS reverse proxy for remote administration and restrict egress to approved certificate endpoints.

## Recovery

Use SQLite online backup or stop writers before copying the database. Encrypt backups and test restoration. After restore, confirm inventory through `/endpoints`, run a non-critical endpoint, and confirm new history. Roll back with the preceding immutable image after backing up the database.
