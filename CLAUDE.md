# CLAUDE.md — Repère pour les sessions Claude Code

## Quoi
**BTP Agent Platform** : SaaS agentique BTP. Monorepo polyglotte Python (backend +
packages) + Next.js (frontend). Voir `docs/SRS.md`, `docs/ARCHITECTURE.md`,
`docs/ROADMAP.md`.

## Structure
- `packages/*` — bibliothèques Python sous le namespace PEP 420 `btp.*`
  (database, auth, agents, llm_router, vector_store, crm, ao, quotes, reports,
  documents). Importables tels quels (`from btp.auth import ...`).
- `services/api` — FastAPI, package `btp_api`. Cœur applicatif (Sprint 1 livré).
- `services/workers`, `services/crawler` — services Python (`btp_workers`, `btp_crawler`).
- `apps/web` — Next.js 14 (App Router) + Tailwind, package `@btp/web`.

## Conventions
- **Workspace Python géré par `uv`** (membres déclarés dans le `pyproject.toml`
  racine). `uv sync` installe tout en éditable.
- Modèles : SQLAlchemy 2.0 (`Mapped` / `mapped_column`). ⚠️ Tout type utilisé
  dans une annotation `Mapped[...]` doit être importé **au runtime** (pas
  seulement sous `TYPE_CHECKING`), sinon SQLAlchemy échoue à la résolution.
- Mots de passe : `pbkdf2_sha256` (passlib) — pur Python, robuste en CI.
- Enums métier : motif `(str, enum.Enum)` volontaire (UP042 ignoré dans ruff).
- RBAC : matrice unique dans `packages/auth/btp/auth/rbac.py`.
- Routage LLM : `packages/llm-router/btp/llm_router/router.py`. Sans clé d'API,
  `EchoProvider` (mock déterministe) est utilisé → tests hors-ligne.

## Commandes
```bash
uv sync                 # dépendances Python
uv run pytest           # tests (14 tests, doivent rester verts)
uv run ruff check .     # lint (doit rester clean)
uv run btp-api init-db
uv run btp-api create-admin --email a@b.c --password ********
uv run uvicorn btp_api.main:app --reload --port 8000
make help               # autres raccourcis
```

## État
Sprint 1 (Auth · Rôles · Projets) implémenté et testé. Sprints 2–10 :
interfaces + stubs prêts à compléter (cf. `docs/ROADMAP.md`).
