"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { Btn, GhostBtn, Panel } from "@/components/Panel";
import {
  api,
  getToken,
  openAuthed,
  type DocumentItem,
  type PhotoItem,
  type Project,
  type QuoteItem,
  type ReportItem,
  type TenderItem,
} from "@/lib/api";

export default function ProjectHub() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const pid = params.id;

  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [photos, setPhotos] = useState<PhotoItem[]>([]);
  const [quotes, setQuotes] = useState<QuoteItem[]>([]);
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [tenders, setTenders] = useState<TenderItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const [p, d, ph, q, r, t] = await Promise.all([
      api.getProject(pid),
      api.listDocuments(pid),
      api.listPhotos(pid),
      api.listQuotes(pid),
      api.listReports(pid),
      api.listTenders(pid),
    ]);
    setProject(p);
    setDocuments(d);
    setPhotos(ph);
    setQuotes(q);
    setReports(r);
    setTenders(t);
  }, [pid]);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    refresh().catch((e) => setError(String(e)));
  }, [router, refresh]);

  function guard<T>(p: Promise<T>) {
    p.then(() => refresh()).catch((e) =>
      setError(e instanceof Error ? e.message : "Erreur")
    );
  }

  return (
    <main className="mx-auto max-w-4xl p-6">
      <header className="mb-6">
        <Link href="/projects" className="text-sm text-slate-500 hover:underline">
          ← Projets
        </Link>
        <h1 className="mt-1 text-2xl font-bold text-brand">
          {project?.name ?? "Projet"}
        </h1>
        <Link href="/chat" className="text-sm text-brand hover:underline">
          Ouvrir le chat agents →
        </Link>
      </header>

      {error && (
        <p className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <Panel title="Documents">
          <FileInput
            label="Téléverser"
            onFile={(f) => guard(api.uploadDocument(pid, f))}
          />
          <List
            items={documents}
            render={(d) => (
              <Row
                key={d.id}
                label={d.filename}
                tag={d.kind}
                action={<GhostBtn onClick={() => guard(api.analyzeDocument(d.id))}>OCR</GhostBtn>}
              />
            )}
          />
        </Panel>

        <Panel title="Photos chantier">
          <FileInput label="Ajouter une photo" onFile={(f) => guard(api.uploadPhoto(pid, f, ""))} />
          <List
            items={photos}
            render={(p) => (
              <Row
                key={p.id}
                label={p.caption || "photo"}
                tag={p.analysis ? "analysée" : "—"}
                action={<GhostBtn onClick={() => guard(api.analyzePhoto(p.id))}>Analyser</GhostBtn>}
              />
            )}
          />
        </Panel>

        <Panel title="Devis">
          <TextAction
            placeholder="Description des ouvrages…"
            button="Générer"
            onSubmit={(v) => guard(api.generateQuote(pid, v))}
          />
          <List
            items={quotes}
            render={(q) => (
              <Row
                key={q.id}
                label={`${q.reference} — ${q.total_ht.toFixed(2)} € HT`}
                tag={q.status}
                action={
                  <>
                    <GhostBtn onClick={() => guard(api.buildQuotePdf(q.id))}>PDF</GhostBtn>
                    <GhostBtn onClick={() => openAuthed(`/quotes/${q.id}/pdf`)}>Voir</GhostBtn>
                  </>
                }
              />
            )}
          />
        </Panel>

        <Panel title="Comptes-rendus">
          <TextAction
            placeholder="Titre du compte-rendu…"
            button="Générer"
            onSubmit={(v) => guard(api.generateReport(pid, v, "chantier"))}
          />
          <List
            items={reports}
            render={(r) => (
              <Row
                key={r.id}
                label={r.title}
                tag={r.validated ? "validé" : r.kind}
                action={
                  !r.validated && (
                    <GhostBtn onClick={() => guard(api.validateReport(r.id))}>Valider</GhostBtn>
                  )
                }
              />
            )}
          />
        </Panel>

        <Panel title="Appels d'offres">
          <TextAction
            placeholder="Intitulé de l'AO…"
            button="Enregistrer"
            onSubmit={(v) => guard(api.createTender(pid, v, ""))}
          />
          <List
            items={tenders}
            render={(t) => (
              <Row
                key={t.id}
                label={t.title}
                tag={t.decision}
                action={
                  <>
                    <GhostBtn onClick={() => guard(api.qualifyTender(t.id, 0.75))}>GO?</GhostBtn>
                    <GhostBtn onClick={() => guard(api.respondTender(t.id))}>Mémoire</GhostBtn>
                  </>
                }
              />
            )}
          />
        </Panel>
      </div>
    </main>
  );
}

function List<T>({ items, render }: { items: T[]; render: (item: T) => React.ReactNode }) {
  if (items.length === 0)
    return <p className="mt-2 text-xs text-slate-400">Aucun élément.</p>;
  return <ul className="mt-3 space-y-1.5">{items.map(render)}</ul>;
}

function Row({
  label,
  tag,
  action,
}: {
  label: string;
  tag?: string;
  action?: React.ReactNode;
}) {
  return (
    <li className="flex items-center justify-between gap-2 rounded-md bg-slate-50 px-3 py-1.5 text-sm">
      <span className="truncate">{label}</span>
      <span className="flex items-center gap-1.5">
        {tag && (
          <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs text-slate-600">
            {tag}
          </span>
        )}
        {action}
      </span>
    </li>
  );
}

function FileInput({ label, onFile }: { label: string; onFile: (f: File) => void }) {
  return (
    <label className="inline-flex cursor-pointer items-center gap-2 text-sm text-brand hover:underline">
      {label}
      <input
        type="file"
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) onFile(f);
          e.target.value = "";
        }}
      />
    </label>
  );
}

function TextAction({
  placeholder,
  button,
  onSubmit,
}: {
  placeholder: string;
  button: string;
  onSubmit: (value: string) => void;
}) {
  const [value, setValue] = useState("");
  return (
    <div className="flex gap-2">
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        className="flex-1 rounded-md border border-slate-300 px-2 py-1 text-sm"
      />
      <Btn
        onClick={() => {
          if (value.trim()) {
            onSubmit(value);
            setValue("");
          }
        }}
      >
        {button}
      </Btn>
    </div>
  );
}
