"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Assistant } from "@/components/Assistant";
import { Shell } from "@/components/Shell";
import { api, type DashboardStats } from "@/lib/api";

const EUR = new Intl.NumberFormat("fr-FR", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0,
});

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    api.dashboardStats().then(setStats).catch(() => {});
  }, []);

  return (
    <Shell active="dashboard">
      <div className="mx-auto max-w-7xl px-6 py-7">
        <div className="mb-6">
          <h1 className="text-2xl font-bold tracking-tight text-ink">Tableau de bord</h1>
          <p className="text-sm text-slate-500">
            Vue d'ensemble de votre activité BTP.
          </p>
        </div>

        {/* KPIs */}
        <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Kpi label="Projets actifs" value={stats?.projects_active} icon="🏗️" tint="indigo" />
          <Kpi
            label="Devis"
            value={stats?.quotes_count}
            sub={stats ? `${EUR.format(stats.quotes_total_ht)} HT` : undefined}
            icon="📄"
            tint="emerald"
          />
          <Kpi
            label="AO détectés"
            value={stats?.tenders_total}
            sub={stats ? `${stats.tenders_go} qualifiés GO` : undefined}
            icon="📢"
            tint="amber"
          />
          <Kpi label="Comptes-rendus" value={stats?.reports_count} icon="📝" tint="violet" />
        </section>

        {/* Contenu : listes + fenêtre de discussion */}
        <section className="mt-6 grid gap-5 lg:grid-cols-3">
          <div className="space-y-5 lg:col-span-2">
            <Card title="Devis récents" href="/projects">
              {stats?.recent_quotes?.length ? (
                <ul className="divide-y divide-slate-100">
                  {stats.recent_quotes.map((q) => (
                    <li key={q.id} className="flex items-center justify-between py-2.5">
                      <div className="flex items-center gap-3">
                        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
                          📄
                        </span>
                        <div>
                          <p className="text-sm font-medium text-ink">{q.reference}</p>
                          <p className="text-xs text-slate-500">{EUR.format(q.total_ht)} HT</p>
                        </div>
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
              {stats?.recent_tenders?.length ? (
                <ul className="divide-y divide-slate-100">
                  {stats.recent_tenders.map((t) => (
                    <li key={t.id} className="flex items-center justify-between gap-3 py-2.5">
                      <div className="flex min-w-0 items-center gap-3">
                        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-amber-50 text-amber-600">
                          📢
                        </span>
                        <div className="min-w-0">
                          <p className="truncate text-sm font-medium text-ink">{t.title}</p>
                          <p className="truncate text-xs text-slate-500">{t.buyer ?? "—"}</p>
                        </div>
                      </div>
                      <DecisionBadge decision={t.decision} />
                    </li>
                  ))}
                </ul>
              ) : (
                <Empty />
              )}
            </Card>

            {/* Accès modules */}
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              <Tile href="/projects" icon="🏗️" label="Projets" />
              <Tile href="/chat" icon="💬" label="Assistant IA" />
              <Tile href="/crm" icon="🤝" label="CRM" />
              <Tile href="/projects" icon="🧱" label="Devis" />
              <Tile href="/projects" icon="📁" label="Documents" />
              <Tile href="/projects" icon="📸" label="Photos chantier" />
            </div>
          </div>

          {/* Fenêtre de discussion */}
          <div className="lg:col-span-1">
            <div className="sticky top-6 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-card">
              <Assistant compact />
            </div>
          </div>
        </section>
      </div>
    </Shell>
  );
}

const TINTS: Record<string, string> = {
  indigo: "from-indigo-500 to-violet-600",
  emerald: "from-emerald-500 to-teal-600",
  amber: "from-amber-500 to-orange-600",
  violet: "from-violet-500 to-fuchsia-600",
};

function Kpi({
  label,
  value,
  sub,
  icon,
  tint,
}: {
  label: string;
  value?: number;
  sub?: string;
  icon: string;
  tint: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card">
      <div className="flex items-start justify-between">
        <div
          className={`flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${TINTS[tint]} text-white shadow-soft`}
        >
          <span className="text-lg">{icon}</span>
        </div>
      </div>
      <div className="mt-3 text-3xl font-bold tracking-tight text-ink">
        {value ?? <span className="text-slate-300">—</span>}
      </div>
      <div className="text-xs font-medium text-slate-500">{label}</div>
      {sub && <div className="mt-0.5 text-[11px] text-slate-400">{sub}</div>}
    </div>
  );
}

function Card({ title, href, children }: { title: string; href: string; children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
      <div className="mb-1 flex items-center justify-between">
        <h3 className="font-semibold text-ink">{title}</h3>
        <Link href={href} className="text-xs font-medium text-brand hover:underline">
          Tout voir →
        </Link>
      </div>
      {children}
    </div>
  );
}

function Tile({ href, icon, label }: { href: string; icon: string; label: string }) {
  return (
    <Link
      href={href}
      className="flex items-center gap-2.5 rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm font-medium text-slate-700 shadow-card transition hover:-translate-y-0.5 hover:border-brand hover:text-brand"
    >
      <span className="text-lg">{icon}</span>
      {label}
    </Link>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    brouillon: "bg-slate-100 text-slate-600",
    en_revision: "bg-amber-100 text-amber-700",
    envoye: "bg-blue-100 text-blue-700",
    accepte: "bg-emerald-100 text-emerald-700",
    refuse: "bg-rose-100 text-rose-700",
  };
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${map[status] ?? "bg-slate-100 text-slate-600"}`}>
      {status.replace("_", " ")}
    </span>
  );
}

function DecisionBadge({ decision }: { decision: string }) {
  const map: Record<string, [string, string]> = {
    go: ["GO", "bg-emerald-100 text-emerald-700"],
    no_go: ["NO-GO", "bg-rose-100 text-rose-700"],
    a_qualifier: ["À qualifier", "bg-slate-100 text-slate-500"],
  };
  const [text, cls] = map[decision] ?? [decision, "bg-slate-100 text-slate-600"];
  return <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${cls}`}>{text}</span>;
}

function Empty() {
  return <p className="py-6 text-center text-sm text-slate-400">Aucun élément récent.</p>;
}
