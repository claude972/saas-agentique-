# CLAUDE.md — Construction de site / app qualité (frontend `apps/web`)

## Stack imposé (ne pas dévier)
- **Framework** : Next.js + TypeScript
- **Styling** : Tailwind CSS
- **Composants** : shadcn/ui + registries Aceternity UI + Magic UI
- **Animation** : Motion (ex-Framer Motion)
- **Smooth scroll** : Lenis
- **Carrousels / slides** : Embla (composant shadcn "carousel")

## Workflow obligatoire à chaque tâche

Pour CHAQUE page ou section à construire, suis cet ordre :

1. **Context7 d'abord** — récupère la doc à jour de Next.js / Tailwind / Motion
   AVANT d'écrire du code. Ne te fie pas à ta mémoire sur les versions.

2. **shadcn MCP ensuite** — pour tout composant UI (hero, carrousel, cards,
   nav, footer...), cherche d'abord dans les registries (shadcn, Aceternity,
   Magic UI) et installe le composant existant.
   N'écris JAMAIS un composant à la main si un équivalent existe dans un registry.

3. **Code & adaptation** — adapte le composant installé à la direction du projet
   (couleurs, polices, espacement). Garde le code propre et typé.

4. **Playwright après chaque section** — teste le rendu réel, vérifie le
   responsive et que les animations se déclenchent. Corrige avant de continuer.

5. **GitHub MCP** — commit à chaque section validée. Messages clairs.

## Carrousels / slides — règle spécifique
- Tout slider/carrousel = Embla via le composant shadcn "carousel".
- Ne code pas un slider maison.
- Pour des transitions de slides premium : combine Embla + Motion.

## Direction "qualité / luxe" — principes non négociables
- **Palette restreinte** : 2-3 couleurs max.
- **2 polices max** : une serif de caractère (titres) + une sans-serif neutre (corps).
- **Beaucoup d'espace blanc**. La retenue prime sur la richesse visuelle.
- **Animations subtiles** : apparitions au scroll, transitions douces. Jamais clinquant.
- **Assets** : zéro stock photo générique. Si visuel médiocre, signale-le, ne livre pas.

## Ce qu'il ne faut PAS faire
- Pas de composant écrit à la main si un registry en a un.
- Pas de code basé sur des versions devinées (toujours Context7).
- Pas de section livrée sans passage Playwright.
- Pas de localStorage/sessionStorage dans les artifacts.

---

## Note d'intégration (spécifique à ce repo)

L'app `apps/web` est le frontend d'un **SaaS** (auth JWT, dashboard, CRUD), pas
un artifact isolé. Deux points d'attention vis-à-vis du guide ci-dessus :

- **Auth & stockage** : l'authentification stocke aujourd'hui le JWT en
  `localStorage`. La règle « pas de localStorage » vise les artifacts ; pour un
  SaaS réel, l'alternative propre est un **cookie httpOnly** posé par l'API.
  À arbitrer avant de toucher au flux d'auth.
- **MCP requis** : le workflow impose **Context7** et **shadcn MCP**. Ils sont
  déclarés dans `.mcp.json` à la racine — à connecter/approuver dans la session
  avant de démarrer une tâche UI.
