# Déploiement

## Backend (Railway)

L'API se déploie via le `Dockerfile` (`services/api/Dockerfile`), piloté par
`railway.json`. Provisionner les add-ons **PostgreSQL** et **Redis** sur Railway,
puis définir les variables d'environnement (cf. `.env.example`) :

| Variable | Obligatoire | Note |
|----------|:-----------:|------|
| `DATABASE_URL` | ✅ | fournie par l'add-on Postgres |
| `REDIS_URL` | ✅ | fournie par l'add-on Redis |
| `SECRET_KEY` | ✅ | `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `ANTHROPIC_API_KEY` | ⚠️ | active le pipeline LLM réel (sinon mock) |
| `CORS_ORIGINS` | ✅ | URL du frontend Vercel |
| `S3_*` | ⛔️ | optionnel ; sans config, stockage local |

La commande `release` (Procfile) applique les **migrations Alembic**
(`alembic upgrade head`) au déploiement. En développement, `btp-api init-db`
(`create_all`) reste un raccourci. Créer l'admin :

```bash
railway run uv run btp-api create-admin --email admin@votre-domaine.fr --password '********'
```

Health check : `GET /health`.

## Frontend (Vercel)

Importer le dossier `apps/web` (framework Next.js auto-détecté, cf.
`apps/web/vercel.json`). Définir la variable :

| Variable | Valeur |
|----------|--------|
| `API_URL` | URL publique de l'API Railway (ex. `https://btp-api.up.railway.app`) |

Les appels `/api/*` du frontend sont proxifiés vers `API_URL`
(`next.config.mjs`), évitant les problèmes de CORS côté navigateur.

## Local (rappel)

```bash
docker compose up -d db redis
cp .env.example .env            # renseigner ANTHROPIC_API_KEY pour le LLM réel
uv sync && uv run btp-api init-db
uv run btp-api create-admin --email admin@btp.local --password changeme123
uv run uvicorn btp_api.main:app --reload --port 8000   # API
cd apps/web && pnpm install && pnpm dev                 # Web
```
