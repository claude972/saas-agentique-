"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { api, type Project } from "@/lib/api";

const STATUS: Record<string, string> = {
  prospect: "bg-slate-100 text-slate-600",
  etude: "bg-blue-100 text-blue-700",
  en_cours: "bg-emerald-100 text-emerald-700",
  suspendu: "bg-amber-100 text-amber-700",
  termine: "bg-violet-100 text-violet-700",
  archive: "bg-slate-100 text-slate-400",
};

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listProjects().then(setProjects).catch((e) => setError(String(e)));
  }, []);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    try {
      const project = await api.createProject({ name });
      setProjects((prev) => [project, ...prev]);
      setName("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur");
    }
  }

  return (
    <Shell active="projects">
      <div className="mx-auto max-w-5xl px-6 py-7">
        <div className="mb-6 flex items-end justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-ink">Projets</h1>
            <p className="text-sm text-slate-500">{projects.length} affaire(s) suivie(s)</p>
          </div>
          <form onSubmit={onCreate} className="flex gap-2">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Nouveau projet"
              className="rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-sm shadow-card outline-none focus:border-brand"
            />
            <button className="rounded-xl bg-brand px-4 py-2 text-sm font-medium text-white shadow-soft hover:bg-brand-dark">
              Créer
            </button>
          </form>
        </div>

        {error && (
          <p className="mb-4 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>
        )}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((p) => (
            <Link
              key={p.id}
              href={`/projects/${p.id}`}
              className="group rounded-2xl border border-slate-200 bg-white p-5 shadow-card transition hover:-translate-y-0.5 hover:border-brand hover:shadow-soft"
            >
              <div className="mb-3 flex items-start justify-between">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-light text-lg">
                  🏗️
                </span>
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS[p.status] ?? "bg-slate-100 text-slate-600"}`}
                >
                  {p.status.replace("_", " ")}
                </span>
              </div>
              <h3 className="font-semibold leading-snug text-ink group-hover:text-brand">
                {p.name}
              </h3>
              {p.description && (
                <p className="mt-1 line-clamp-2 text-sm text-slate-500">{p.description}</p>
              )}
            </Link>
          ))}
          {projects.length === 0 && (
            <p className="text-sm text-slate-400">Aucun projet pour le moment.</p>
          )}
        </div>
      </div>
    </Shell>
  );
}
