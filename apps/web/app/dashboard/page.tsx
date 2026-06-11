"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, clearToken, getToken, type CurrentUser, type Project } from "@/lib/api";

const MODULES = [
  { name: "Projets", href: "/projects", desc: "Suivi des affaires et chantiers" },
  { name: "Chat agents", href: "/chat", desc: "Supervisor + agents, mémoire persistante" },
  { name: "Devis", href: "#", desc: "Génération assistée par QuoteAgent" },
  { name: "Appels d'offres", href: "#", desc: "Détection et qualification GO/NO-GO" },
  { name: "Comptes-rendus", href: "#", desc: "Chantier, visite, réunion, réserve" },
  { name: "CRM", href: "/crm", desc: "Clients, contacts, opportunités" },
  { name: "Documents", href: "#", desc: "OCR, classement, recherche" },
];

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    Promise.all([api.me(), api.listProjects()])
      .then(([u, p]) => {
        setUser(u);
        setProjects(p);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Erreur"));
  }, [router]);

  function logout() {
    clearToken();
    router.push("/login");
  }

  return (
    <main className="mx-auto max-w-5xl p-6">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-brand">Tableau de bord</h1>
          {user && (
            <p className="text-sm text-slate-500">
              {user.email} — rôle : {user.role}
            </p>
          )}
        </div>
        <button
          onClick={logout}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100"
        >
          Déconnexion
        </button>
      </header>

      {error && (
        <p className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}

      <section className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Stat label="Projets actifs" value={projects.length} />
        <Stat label="Devis récents" value={0} />
        <Stat label="AO détectés" value={0} />
        <Stat label="Agents" value={6} />
      </section>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {MODULES.map((m) => (
          <a
            key={m.name}
            href={m.href}
            className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-brand"
          >
            <h2 className="font-semibold text-slate-800">{m.name}</h2>
            <p className="mt-1 text-sm text-slate-500">{m.desc}</p>
          </a>
        ))}
      </section>
    </main>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 text-center shadow-sm">
      <div className="text-3xl font-bold text-brand">{value}</div>
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
    </div>
  );
}
