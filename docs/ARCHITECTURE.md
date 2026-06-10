# Architecture — BTP Agent Platform

## Vue d'ensemble

```
                         ┌────────────────────────┐
                         │   apps/web (Next.js)    │  Web + PWA
                         │  Tailwind · shadcn/ui   │
                         └───────────┬────────────┘
                                     │ HTTPS / JSON
                         ┌───────────▼────────────┐
                         │   services/api          │  FastAPI
                         │   Auth · RBAC · REST     │
                         └───┬───────────┬─────────┘
              enqueue tasks  │           │  domain calls
                   ┌─────────▼──┐   ┌────▼──────────────────────────┐
                   │ services/  │   │ packages/* (namespace `btp`)  │
                   │ workers    │   │ auth · database · agents ·    │
                   │ (Redis/RQ) │   │ llm-router · crm · ao ·       │
                   └─────┬──────┘   │ quotes · reports · documents ·│
                         │          │ vector-store                  │
        ┌────────────────▼───┐      └───────────────┬───────────────┘
        │ services/crawler   │                      │
        │ (détection AO)     │      ┌───────────────▼───────────────┐
        └────────────────────┘      │  PostgreSQL · Redis · S3      │
                                     │  + LLM providers (Claude…)   │
                                     └───────────────────────────────┘
```

## Packages Python (namespace PEP 420 `btp`)

Tous les paquets partagent le namespace `btp`. Ils sont installés en mode
éditable via le workspace `uv` déclaré à la racine (`pyproject.toml`).

| Paquet | Import | Responsabilité |
|--------|--------|----------------|
| `packages/database` | `btp.database` | `Base`, modèles ORM, session, helpers de migration |
| `packages/auth` | `btp.auth` | Hash mot de passe, JWT, RBAC (rôles → permissions) |
| `packages/llm-router` | `btp.llm_router` | Abstraction provider + sélection du modèle par tâche |
| `packages/agents` | `btp.agents` | `BaseAgent`, `SupervisorAgent`, agents spécialisés |
| `packages/vector-store` | `btp.vector_store` | Indexation & recherche sémantique (RAG) |
| `packages/crm` | `btp.crm` | Services métier CRM |
| `packages/ao` | `btp.ao` | Services métier appels d'offres |
| `packages/quotes` | `btp.quotes` | Services métier devis |
| `packages/reports` | `btp.reports` | Services métier comptes-rendus |
| `packages/documents` | `btp.documents` | OCR, classement, extraction |

Les *services* (`services/api`, `services/workers`, `services/crawler`)
consomment ces paquets ; ils ne contiennent que la couche de transport
(HTTP, files de tâches, scheduling) et l'assemblage.

## RBAC

Le contrôle d'accès est centralisé dans `btp.auth.rbac`. Chaque rôle est associé
à un ensemble de permissions atomiques `(ressource, action)`. Les dépendances
FastAPI (`require_permission(...)`) vérifient la permission de l'utilisateur
courant avant d'exécuter une route.

| Permission | Admin | Direction | Chargé d'affaires | Conducteur | Lecture seule |
|------------|:-----:|:---------:|:-----------------:|:----------:|:-------------:|
| `users:*` | ✅ | | | | |
| `roles:*` | ✅ | | | | |
| `settings:*` | ✅ | | | | |
| `agents:*` | ✅ | | | | |
| `projects:read` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `projects:write` | ✅ | ✅ | ✅ | ✅ | |
| `documents:read` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `documents:write` | ✅ | ✅ | ✅ | ✅ | |
| `crm:read` / `crm:write` | ✅ | ✅ | ✅ | | (read) |
| `ao:read` / `ao:write` | ✅ | ✅ | ✅ | | (read) |
| `quotes:read` / `quotes:write` | ✅ | ✅ | ✅ | | (read) |
| `reports:read` / `reports:write` | ✅ | ✅ | | ✅ | (read) |
| `chantier:*` | ✅ | ✅ | | ✅ | (read) |

> La matrice exacte fait foi dans le code (`btp/auth/rbac.py`) ; ce tableau en
> est le résumé documentaire.

## Router multi-LLM

`btp.llm_router.LLMRouter` expose `route(task: TaskType) -> Provider`. La table
de routage par défaut (surchargée par configuration) :

| `TaskType` | Provider par défaut |
|------------|---------------------|
| `TENDER`, `TECHNICAL_MEMO`, `COMPLEX_WRITING` | `claude` |
| `VISION`, `OCR_PHOTO`, `PHOTO_ANALYSIS` | `gpt` |
| `LARGE_PDF`, `DOC_SEARCH` | `gemini` |
| `CLASSIFICATION`, `SIMPLE_EXTRACTION` | `mistral` |

Chaque provider implémente l'interface `LLMProvider` (`complete`, `vision`,
`embed`). Tant qu'aucune clé n'est configurée, un provider `echo`/mock est
utilisé pour permettre les tests et le développement hors-ligne.

## Architecture agentique

```
            ┌──────────────────────────┐
  demande → │     SupervisorAgent      │
            │  plan → orchestration    │
            └───┬───────┬───────┬──────┘
                │       │       │
        ┌───────▼─┐ ┌───▼────┐ ┌▼─────────┐  …PhotoAgent, QuoteAgent,
        │ Agent A │ │ Agent B│ │ Agent C  │   ConsultationAgent, TenderAgent,
        └───────┬─┘ └───┬────┘ └┬─────────┘   ReportAgent, DocumentAgent
                │       │       │
            ┌───▼───────▼───────▼──┐
            │   fusion résultats   │ → réponse
            └──────────────────────┘
```

`BaseAgent` définit le contrat (`name`, `description`, `async run(context)`).
`SupervisorAgent` planifie (sélection d'agents + workflow), exécute (séquentiel
ou parallèle) et fusionne. Chaque agent s'appuie sur le `LLMRouter` pour
choisir le bon modèle selon la nature de la tâche.

## Données

- **PostgreSQL** : entités métier (users, projects, clients, documents, quotes…).
- **Redis** : cache, file de tâches workers, mémoire de session de chat court terme.
- **S3** : fichiers (photos, PDF, devis générés).

Les modèles sont décrits dans `btp.database.models`. Migrations gérées via
Alembic (config dans `packages/database`).
