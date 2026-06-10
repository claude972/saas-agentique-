import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-8 text-center">
      <h1 className="text-4xl font-bold text-brand">BTP Agent Platform</h1>
      <p className="max-w-xl text-slate-600">
        Plateforme agentique spécialisée BTP : analyse de photos de chantier,
        génération de devis, réponses aux appels d&apos;offres, comptes-rendus
        et CRM — orchestrés par une équipe d&apos;agents IA.
      </p>
      <div className="flex gap-4">
        <Link
          href="/login"
          className="rounded-lg bg-brand px-5 py-2.5 font-medium text-white hover:bg-brand-dark"
        >
          Connexion
        </Link>
        <Link
          href="/dashboard"
          className="rounded-lg border border-slate-300 px-5 py-2.5 font-medium hover:bg-slate-100"
        >
          Tableau de bord
        </Link>
      </div>
    </main>
  );
}
