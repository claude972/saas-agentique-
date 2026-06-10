# BTP Agent Platform

> Plateforme agentique SaaS spécialisée BTP (Bâtiment & Travaux Publics).
> Mono-entreprise, multi-utilisateurs, Web + PWA.

La plateforme orchestre une équipe d'agents IA spécialisés pour :

- analyser des **photos de chantier**
- générer des **devis**
- analyser des **consultations** (CCTP, CCAP, BPU, DPGF, plans)
- préparer des **réponses aux appels d'offres (AO)**
- générer des **comptes-rendus de chantier**
- centraliser la **relation client (CRM)**
- gérer les **documents projets**

## Architecture

Monorepo polyglotte :

```
apps/web              # Frontend Next.js + TypeScript + Tailwind + shadcn (PWA)
services/api          # API FastAPI (Python) — cœur applicatif
services/workers      # Workers asynchrones (tâches longues, agents)
services/crawler      # Crawler de détection d'appels d'offres
packages/             # Bibliothèques Python partagées (namespace `btp`)
  database            #   modèles SQLAlchemy + migrations
  auth                #   authentification JWT + RBAC
  agents              #   SupervisorAgent + agents spécialisés
  llm-router          #   routage multi-LLM (Claude / GPT / Gemini / Mistral)
  vector-store        #   recherche sémantique / RAG
  crm                 #   logique métier CRM
  ao                  #   logique métier appels d'offres
  quotes              #   logique métier devis
  reports             #   logique métier comptes-rendus
  documents           #   gestion documentaire (OCR, classement)
docs                  # SRS, architecture, roadmap
```

Données : **PostgreSQL** (relationnel) · **Redis** (cache / files) · **S3** (objets).

Voir [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) pour le détail et
[`docs/ROADMAP.md`](docs/ROADMAP.md) pour le découpage en 10 sprints.

## État d'avancement

| Sprint | Périmètre | État |
|-------:|-----------|------|
| 1 | Auth · Rôles · Projets | ✅ Implémenté (API + DB + RBAC) |
| 2 | Documents · Stockage · OCR | 🏗️ Scaffold + interfaces |
| 3 | Chat · Supervisor | 🏗️ Scaffold + interfaces |
| 4–9 | Agents (Photo, Quote, Report, AO, Consultation, Tender) | 🏗️ Interfaces + stubs |
| 10 | PWA | 🏗️ Scaffold frontend |

## Démarrage rapide

### Pré-requis
- Python 3.11+, [uv](https://docs.astral.sh/uv/)
- Node 20+, pnpm 9+
- Docker (pour Postgres / Redis en local)

### Backend (API)

```bash
# 1. Infra locale (Postgres + Redis)
docker compose up -d db redis

# 2. Dépendances Python (workspace uv)
uv sync

# 3. Variables d'environnement
cp .env.example .env

# 4. Initialiser la base + un compte admin
uv run btp-api init-db
uv run btp-api create-admin --email admin@btp.local --password changeme

# 5. Lancer l'API
uv run uvicorn btp_api.main:app --reload --port 8000
```

API disponible sur http://localhost:8000 — documentation interactive sur `/docs`.

### Frontend (web)

```bash
cd apps/web
pnpm install
pnpm dev
```

### Tests

```bash
uv run pytest
```

## Licence

Propriétaire — usage interne.
