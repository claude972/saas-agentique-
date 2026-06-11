"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  api,
  clearToken,
  getToken,
  type CurrentUser,
  type DashboardStats,
} from "@/lib/api";

const MODULES = [
  { name: "Projets", href: "/projects", desc: "Suivi des affaires et chantiers", icon: "🏗️" },
  { name: "Chat agents", href: "/chat", desc: "Supervisor + agents, mémoire persistante", icon: "💬" },
  { name: "CRM", href: "/crm", desc: "Clients, contacts, opportunités", icon: "🤝" },
  { name: "Devis", href: "/projects", desc: "Génération assistée par QuoteAgent", icon: "📄" },
  { name: "Appels d'offres", href: "/projects", desc: "Détection BOAMP + GO/NO-GO", icon: "📢" },
  { name: "Documents", href: "/projects", desc: "OCR, classement, recherche", icon: "📁" },
];

const EUR = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    Promise.all([api.me(), api.dashboardStats()])
      .then(([u, s]) => {
        setUser(u);
        setStats(s);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Erreur"));
  }, [router]);

  function logout() {
    clearToken();
    router.push("/login");
  }

  return (
    <main className="min-h-screen bg-slate-50">
      {/* Barre supérieure */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand font-bold text-white">
              BTP
            </div>
            <div>
              <h1 className="text-lg font-bold leading-tight text-slate-900">
                BTP Agent Platform
              </h1>
              {user && (
                <p className="text-xs text-slate-500">
                  {user.full_name ?? user.email} · {user.role}
                </p>
              )}
            </div>
          </div>
          <button
            onClick={logout}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100"
          >
            Déconnexion
          </button>
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-6 py-8">
        <h2 className="mb-5 text-2xl font-bold text-slate-900">Tableau de bord</h2>
        {error && (
          <p className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
        )}

        {/* KPIs */}
        <section className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <Kpi label="Projets actifs" value={stats?.projects_active ?? "—"} accent="from-blue-500 to-blue-600" icon="🏗️" />
          <Kpi
            label="Devis"
            value={stats?.quotes_count ?? "—"}
            sub={stats ? EUR.format(stats.quotes_total_ht) : ""}
            accent="from-emerald-500 to-emerald-600"
            icon="📄"
          />
          <Kpi
            label="AO détectés"
            value={stats?.tenders_total ?? "—"}
            sub={stats ? `${stats.tenders_go} GO` : ""}
            accent="from-amber-500 to-orange-600"
            icon="📢"
          />
          <Kpi label="Comptes-rendus" value={stats?.reports_count ?? "—"} accent="from-violet-500 to-violet-600" icon="📝" />
        </section>

        {/* Activité récente */}
        <section className="mt-6 grid gap-4 lg:grid-cols-2">
          <Card title="Devis récents" href="/projects">
            {stats && stats.recent_quotes.length > 0 ? (
              <ul className="divide-y divide-slate-100">
                {stats.recent_quotes.map((q) => (
                  <li key={q.id} className="flex items-center justify-between py-2.5">
                    <div>
                      <p className="font-medium text-slate-800">{q.reference}</p>
                      <p className="text-xs text-slate-500">{EUR.format(q.total_ht)} HT</p>
                    </div>
                    <StatusBadge status={q.status} />
                  </li>
                ))}
              </ul>
            ) : (
              <Empty />
            )}
          </Card>

          <Card title="Appels d'offres détectés" href="/projects">
            {stats && stats.recent_tenders.length > 0 ? (
              <ul className="divide-y divide-slate-100">
                {stats.recent_tenders.map((t) => (
                  <li key={t.id} className="flex items-center justify-between gap-3 py-2.5">
                    <div className="min-w-0">
                      <p className="truncate font-medium text-slate-800">{t.title}</p>
                      <p className="text-xs text-slate-500">{t.buyer ?? "—"}</p>
                    </div>
                    <DecisionBadge decision={t.decision} />
                  </li>
                ))}
              </ul>
            ) : (
              <Empty />
            )}
          </Card>
        </section>

        {/* Modules */}
        <h3 className="mb-3 mt-8 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Modules
        </h3>
        <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {MODULES.map((m) => (
            <Link
              key={m.name}
              href={m.href}
              className="group rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-brand hover:shadow-md"
            >
              <div className="mb-2 text-2xl">{m.icon}</div>
              <h4 className="font-semibold text-slate-800 group-hover:text-brand">{m.name}</h4>
              <p className="mt-1 text-sm text-slate-500">{m.desc}</p>
            </Link>
          ))}
        </section>
      </div>
    </main>
  );
}

function Kpi({
  label,
  value,
  sub,
  accent,
  icon,
}: {
  label: string;
  value: number | string;
  sub?: string;
  accent: string;
  icon: string;
}) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className={`h-1 bg-gradient-to-r ${accent}`} />
      <div className="p-4">
        <div className="flex items-center justify-between">
          <span className="text-3xl font-bold text-slate-900">{value}</span>
          <span className="text-xl opacity-80">{icon}</span>
        </div>
        <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</div>
        {sub && <div className="mt-0.5 text-xs text-slate-400">{sub}</div>}
      </div>
    </div>
  );
}

function Card({ title, href, children }: { title: string; href: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="font-semibold text-slate-800">{title}</h3>
        <Link href={href} className="text-xs text-brand hover:underline">
          Tout voir →
        </Link>
      </div>
      {children}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    brouillon: "bg-slate-100 text-slate-600",
    en_revision: "bg-amber-100 text-amber-700",
    envoye: "bg-blue-100 text-blue-700",
    accepte: "bg-emerald-100 text-emerald-700",
    refuse: "bg-red-100 text-red-700",
  };
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${map[status] ?? "bg-slate-100 text-slate-600"}`}>
      {status.replace("_", " ")}
    </span>
  );
}

function DecisionBadge({ decision }: { decision: string }) {
  const map: Record<string, [string, string]> = {
    go: ["🟢 GO", "bg-emerald-100 text-emerald-700"],
    no_go: ["🔴 NO-GO", "bg-red-100 text-red-700"],
    a_qualifier: ["⏳ À qualifier", "bg-slate-100 text-slate-600"],
  };
  const [text, cls] = map[decision] ?? [decision, "bg-slate-100 text-slate-600"];
  return <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${cls}`}>{text}</span>;
}

function Empty() {
  return <p className="py-6 text-center text-sm text-slate-400">Aucun élément récent.</p>;
}
