"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur de connexion");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen">
      {/* Panneau marketing */}
      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-ink p-12 text-white lg:flex">
        <div
          className="absolute inset-0 opacity-30"
          style={{
            background:
              "radial-gradient(600px circle at 20% 20%, #6366f1, transparent 45%), radial-gradient(500px circle at 80% 70%, #8b5cf6, transparent 45%)",
          }}
        />
        <div className="relative flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10 text-lg font-bold backdrop-blur">
            B
          </div>
          <span className="text-lg font-semibold">BTP Agent Platform</span>
        </div>
        <div className="relative">
          <h2 className="text-3xl font-bold leading-snug">
            Votre équipe d'agents IA pour le BTP.
          </h2>
          <p className="mt-4 max-w-md text-slate-300">
            Analyse de photos de chantier, génération de devis, veille et réponse
            aux appels d'offres, comptes-rendus et CRM — orchestrés par un
            superviseur intelligent.
          </p>
          <div className="mt-8 flex flex-wrap gap-2">
            {["PhotoAgent", "QuoteAgent", "TenderAgent", "ReportAgent", "+ BOAMP", "Telegram"].map(
              (t) => (
                <span
                  key={t}
                  className="rounded-full border border-white/15 bg-white/5 px-3 py-1 text-xs text-slate-200"
                >
                  {t}
                </span>
              )
            )}
          </div>
        </div>
        <div className="relative text-xs text-slate-400">© 2026 BTP Agent Platform</div>
      </div>

      {/* Formulaire */}
      <div className="flex w-full items-center justify-center bg-slate-50 p-6 lg:w-1/2">
        <form onSubmit={onSubmit} className="w-full max-w-sm">
          <h1 className="text-2xl font-bold tracking-tight text-ink">Connexion</h1>
          <p className="mt-1 text-sm text-slate-500">Accédez à votre espace.</p>

          {error && (
            <p className="mt-5 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>
          )}

          <label className="mt-6 block text-sm font-medium text-slate-700">
            Email
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="vous@entreprise.fr"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/20"
            />
          </label>

          <label className="mt-4 block text-sm font-medium text-slate-700">
            Mot de passe
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/20"
            />
          </label>

          <button
            type="submit"
            disabled={loading}
            className="mt-6 w-full rounded-xl bg-brand px-4 py-2.5 font-medium text-white shadow-soft transition hover:bg-brand-dark disabled:opacity-60"
          >
            {loading ? "Connexion…" : "Se connecter"}
          </button>

          <p className="mt-4 text-center text-xs text-slate-400">
            Démo : admin@btp.fr · demo1234
          </p>
        </form>
      </div>
    </main>
  );
}
