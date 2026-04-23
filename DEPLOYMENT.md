# Production Deployment Guide (CS Server)

This project should be deployed with Docker Compose in production.  
The stack in this repo is:

- `web`: Django + Gunicorn
- `db`: PostgreSQL
- `caddy`: HTTPS reverse proxy (automatic TLS certificates)

## 1) Server prerequisites

On the CS server, install:

- Docker Engine
- Docker Compose plugin (`docker compose`)
- A DNS record for your site domain (example: `cscita.bc.edu`) pointing to this server
- Open inbound ports `80` and `443`

## 2) One-time setup

From the repository root:

1. Create `.env` from `.env.example`
2. Fill in all required values
3. Start services with `docker compose -f docker-compose.prod.yml up -d --build`
4. Create admin user once

### Recommended `.env` template

Use this as a baseline:

```bash
ENV=prod
DEBUG=false
SECRET_KEY=replace-with-a-long-random-secret

SITE_DOMAIN=cscita.bc.edu
SITE_HOSTNAME=cscita.bc.edu
PUBLIC_SITE_URL=https://cscita.bc.edu
ALLOWED_HOSTS=cscita.bc.edu
CSRF_TRUSTED_ORIGINS=https://cscita.bc.edu

SECURE_SSL_REDIRECT=true
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true

DATABASE_NAME=bc_tasystem
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=replace-with-strong-db-password
DATABASE_HOST=db
DATABASE_PORT=5432

GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
DEFAULT_FROM_EMAIL=csci_ta_app@bc.edu

LETSENCRYPT_EMAIL=you@bc.edu
```

### How to complete `.env` (what each value should be)

- `ENV`: set to `prod` on the CS server.
- `DEBUG`: set to `false` in production.
- `SECRET_KEY`: generate a new long random value for production (do not reuse a dev key).
- `SITE_DOMAIN`: public DNS name pointing to this server (for example `cscita.bc.edu`).
- `SITE_HOSTNAME`: same hostname as `SITE_DOMAIN`, no scheme and no trailing slash.
- `PUBLIC_SITE_URL`: full HTTPS origin for user-facing links (for example `https://cscita.bc.edu`).
- `ALLOWED_HOSTS`: comma-separated hostnames Django should accept (usually just your domain).
- `CSRF_TRUSTED_ORIGINS`: comma-separated HTTPS origins (for example `https://cscita.bc.edu`).
- `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`: keep these `true` in production.

- `DATABASE_NAME`: Postgres database name to create/use.
- `DATABASE_USERNAME`: Postgres username.
- `DATABASE_PASSWORD`: strong password for that Postgres user (create a new production value).
- `DATABASE_HOST`: keep as `db` for Docker Compose deployment.
- `DATABASE_PORT`: keep as `5432`.

- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`: values from Google Cloud OAuth credentials for this app.
  - In Google Cloud Console, add authorized redirect URI:
    - `https://<your-domain>/oauth/google/callback`
  - If an old secret was shared publicly, rotate/regenerate and use the new secret.

- `EMAIL_HOST_USER`: SMTP login username (typically full sender email, e.g. `csci_ta_app@bc.edu`).
- `EMAIL_HOST_PASSWORD`: SMTP password/app-password for that sending account.
- `DEFAULT_FROM_EMAIL`: sender email address shown to users (often same as `EMAIL_HOST_USER`).
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`: values provided by your SMTP provider.

- `LETSENCRYPT_EMAIL`: contact email used by Caddy/Let's Encrypt for certificate notices.

Secrets handling recommendation:

- Do not commit `.env` to git.
- Share production secrets with professor/IT via a secure channel (not plain email).
- Rotate any secret that has already been sent in plaintext or committed previously.

## 3) Start, stop, logs

From repo root:

- Start/update: `docker compose -f docker-compose.prod.yml up -d --build`
- Stop: `docker compose -f docker-compose.prod.yml down`
- Logs: `docker compose -f docker-compose.prod.yml logs -f`
- Service logs only:
  - web: `docker compose -f docker-compose.prod.yml logs -f web`
  - db: `docker compose -f docker-compose.prod.yml logs -f db`
  - caddy: `docker compose -f docker-compose.prod.yml logs -f caddy`

## 4) First-run admin user

After containers are up:

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## 5) HTTPS behavior

- `caddy` handles HTTPS termination and certificate renewal automatically.
- Django trusts proxy HTTPS headers and enforces secure cookies when `ENV=prod`.
- Keep `PUBLIC_SITE_URL=https://<your-domain>` so outbound links and OAuth redirects use HTTPS.

## 6) Deploying updates

For each new release:

1. Pull latest code
2. Review `.env` changes (if any)
3. Run:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Migrations run automatically on startup.

## 7) Database backup and restore

### Backup

```bash
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U "$DATABASE_USERNAME" "$DATABASE_NAME" > backup.sql
```

### Restore

```bash
docker compose -f docker-compose.prod.yml exec -T db psql -U "$DATABASE_USERNAME" "$DATABASE_NAME" < backup.sql
```

## 8) Quick troubleshooting

- **HTTP works but HTTPS fails**
  - Verify DNS points to this server
  - Verify ports `80`/`443` are reachable
  - Check `caddy` logs

- **OAuth callback mismatch**
  - Confirm Google OAuth callback URL exactly matches:
    - `https://<domain>/oauth/google/callback`
  - Confirm `PUBLIC_SITE_URL` is set to the same domain and scheme

- **Static files missing**
  - Confirm `web` container started successfully (collectstatic runs on boot)
  - Confirm `caddy` service is running

- **Database connection errors**
  - Ensure `DATABASE_HOST=db`, not `localhost`
  - Ensure DB credentials in `.env` match Postgres service variables

