# Software Requirement Specification (SRS) — BTP Agent Platform

- **Nom de code** : BTP Agent Platform
- **Version** : 1.0
- **Type** : SaaS interne mono-entreprise
- **Architecture** : Multi-utilisateurs
- **Plateforme** : Web + PWA

## 1. Objectif

Créer une plateforme agentique spécialisée BTP capable de :

- analyser des photos de chantier ;
- générer des devis ;
- analyser des consultations ;
- préparer des réponses aux appels d'offres ;
- générer des comptes-rendus chantier ;
- centraliser la relation client ;
- gérer les documents projets.

## 2. Utilisateurs & rôles

| Rôle | Accès |
|------|-------|
| **Admin** | Accès total : utilisateurs, rôles, projets, documents, agents, paramètres |
| **Direction** | Tous les projets, AO, CRM, rapports |
| **Chargé d'affaires** | Devis, AO, CRM, documents |
| **Conducteur de travaux** | Chantier, photos, comptes-rendus |
| **Lecture seule** | Consultation uniquement |

Le détail des permissions par rôle est codifié dans `packages/auth`
(`btp.auth.rbac`) et présenté dans [`ARCHITECTURE.md`](ARCHITECTURE.md#rbac).

## 3. Modules fonctionnels

### 3.1 Dashboard
Statistiques, AO détectés, projets actifs, devis récents, activité des agents.

### 3.2 Projet
Chaque projet possède : `id`, `nom`, `client`, `description`, `statut`,
`documents`, `photos`, `chat`, `devis`, `AO`, `rapports`, `historique`.

### 3.3 CRM
Clients, contacts, opportunités, historique, documents, interactions.

### 3.4 Documents
Téléversement, classement automatique, OCR, recherche, versioning.

### 3.5 Chat
Conversation par projet, mémoire persistante, historique complet.

## 4. Architecture agentique

| Agent | Mission |
|-------|---------|
| **SupervisorAgent** | Comprendre la demande, choisir les agents, construire le workflow, fusionner les résultats |
| **PhotoAgent** | Entrées : jpg/png/pdf → description, ouvrages, quantités estimées, anomalies |
| **QuoteAgent** | Analyse, quantification, chiffrage, génération & révision de devis |
| **ConsultationAgent** | Lecture CCTP, CCAP, BPU, DPGF, plans |
| **TenderAgent** | Rédaction mémoire technique, planning, méthodologie, organisation chantier |
| **ReportAgent** | Compte-rendu chantier, visite, réunion, réserve |
| **DocumentAgent** | Classement, OCR, recherche documentaire, extraction de données |

## 5. Router multi-LLM

| Fournisseur | Usages privilégiés |
|-------------|--------------------|
| **Claude** | AO, mémoire technique, rédaction complexe |
| **GPT** | Vision, OCR, analyse photo |
| **Gemini** | Gros PDF, recherche documentaire |
| **Mistral** | Classification, extraction simple |

## 6. Workflows

### 6.1 Devis
`Photo → PhotoAgent → Description → Quantification → QuoteAgent → Devis JSON → PDF → Archivage`

### 6.2 Appel d'offres
`Crawler → Détection → Téléchargement → Analyse → Qualification → GO / NO GO → TenderAgent → Dossier final`

### 6.3 Chantier
`Photo / Audio / Texte → ReportAgent → Compte-rendu → Validation → Archivage`

## 7. PWA
Prise photo, upload document, notes vocales, consultation devis, consultation AO,
chat agents, mode mobile.

## 8. Infrastructure

- **Frontend** : Next.js, TypeScript, Tailwind, shadcn/ui, déploiement Vercel.
- **Backend** : FastAPI, Python, déploiement Railway.
- **Données** : PostgreSQL, Redis, S3.

## 9. Découpage MVP

Voir [`ROADMAP.md`](ROADMAP.md). Dix sprints : Auth/Rôles/Projets → Documents/OCR →
Chat/Supervisor → PhotoAgent → QuoteAgent → ReportAgent → AO Crawler →
ConsultationAgent → TenderAgent → PWA.
