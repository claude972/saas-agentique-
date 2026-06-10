# Roadmap MVP — 10 sprints

| Sprint | Périmètre | Livrables clés | État |
|-------:|-----------|----------------|------|
| 1 | **Auth · Rôles · Projets** | JWT, RBAC 5 rôles, CRUD projets, CLI admin | ✅ |
| 2 | **Documents · Stockage · OCR** | Upload S3, versioning, OCR (DocumentAgent) | 🏗️ |
| 3 | **Chat · Supervisor** | Conversation/projet, mémoire persistante, SupervisorAgent | 🏗️ |
| 4 | **PhotoAgent** | Analyse photo → ouvrages, quantités, anomalies | 🏗️ |
| 5 | **QuoteAgent** | Devis JSON → PDF → archivage | 🏗️ |
| 6 | **ReportAgent** | Comptes-rendus chantier/visite/réunion | 🏗️ |
| 7 | **AO Crawler** | Détection, téléchargement, qualification GO/NO-GO | 🏗️ |
| 8 | **ConsultationAgent** | Lecture CCTP/CCAP/BPU/DPGF/plans | 🏗️ |
| 9 | **TenderAgent** | Mémoire technique, planning, méthodologie | 🏗️ |
| 10 | **PWA** | Photo, notes vocales, mode mobile offline-first | 🏗️ |

Légende : ✅ implémenté · 🏗️ scaffold + interfaces (prêt à implémenter).

## Détail Sprint 1 (livré)

- `packages/database` : modèles `User`, `Project`, `Client`, `Contact`,
  `Opportunity`, `Document`, `Photo`, `Quote`, `Tender`, `Report`,
  `Conversation`, `ChatMessage`, `ActivityLog`.
- `packages/auth` : hash Argon2/bcrypt, JWT access tokens, RBAC complet.
- `services/api` : endpoints `/auth`, `/users`, `/projects`, `/health` +
  CLI `btp-api` (`init-db`, `create-admin`).
- Tests `pytest` couvrant auth, RBAC et CRUD projets.

## Convention de définition de « done » par sprint

1. Modèles ORM + migration.
2. Services métier dans le package dédié (`packages/<domaine>`).
3. Endpoints API + permissions RBAC.
4. Agent(s) associés câblés au `LLMRouter`.
5. UI minimale dans `apps/web`.
6. Tests automatisés.
