"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { Btn, GhostBtn, Panel } from "@/components/Panel";
import {
  api,
  getToken,
  type ClientItem,
  type ContactItem,
  type InteractionItem,
  type OpportunityItem,
} from "@/lib/api";

export default function CrmPage() {
  const router = useRouter();
  const [clients, setClients] = useState<ClientItem[]>([]);
  const [selected, setSelected] = useState<ClientItem | null>(null);
  const [contacts, setContacts] = useState<ContactItem[]>([]);
  const [opportunities, setOpportunities] = useState<OpportunityItem[]>([]);
  const [interactions, setInteractions] = useState<InteractionItem[]>([]);
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    api.listClients().then(setClients).catch((e) => setError(String(e)));
  }, [router]);

  const loadClient = useCallback(async (c: ClientItem) => {
    setSelected(c);
    const [co, op, it] = await Promise.all([
      api.listContacts(c.id),
      api.listOpportunities(c.id),
      api.listInteractions(c.id),
    ]);
    setContacts(co);
    setOpportunities(op);
    setInteractions(it);
  }, []);

  async function createClient(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    try {
      const c = await api.createClient(name, "");
      setClients((p) => [...p, c]);
      setName("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur");
    }
  }

  function reload() {
    if (selected) loadClient(selected);
  }

  return (
    <main className="mx-auto max-w-5xl p-6">
      <Link href="/dashboard" className="text-sm text-slate-500 hover:underline">
        ← Tableau de bord
      </Link>
      <h1 className="mb-6 mt-1 text-2xl font-bold text-brand">CRM</h1>
      {error && (
        <p className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
      )}

      <div className="grid gap-4 md:grid-cols-[260px_1fr]">
        <Panel title="Clients">
          <form onSubmit={createClient} className="mb-3 flex gap-2">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Nouveau client"
              className="flex-1 rounded-md border border-slate-300 px-2 py-1 text-sm"
            />
            <Btn>+</Btn>
          </form>
          <ul className="space-y-1">
            {clients.map((c) => (
              <li key={c.id}>
                <button
                  onClick={() => loadClient(c)}
                  className={
                    "w-full rounded-md px-3 py-1.5 text-left text-sm hover:bg-slate-100 " +
                    (selected?.id === c.id ? "bg-slate-100 font-medium" : "")
                  }
                >
                  {c.name}
                </button>
              </li>
            ))}
            {clients.length === 0 && (
              <li className="text-xs text-slate-400">Aucun client.</li>
            )}
          </ul>
        </Panel>

        <div className="space-y-4">
          {!selected && (
            <p className="text-sm text-slate-400">
              Sélectionnez un client pour voir contacts, opportunités et interactions.
            </p>
          )}
          {selected && (
            <>
              <Panel title={`Contacts — ${selected.name}`}>
                <Adder
                  placeholder="Nom du contact"
                  onAdd={(v) => api.addContact(selected.id, v).then(reload)}
                />
                <Lines items={contacts.map((c) => c.full_name + (c.role ? ` (${c.role})` : ""))} />
              </Panel>
              <Panel title="Opportunités">
                <Adder
                  placeholder="Intitulé de l'opportunité"
                  onAdd={(v) => api.addOpportunity(selected.id, v, null).then(reload)}
                />
                <Lines
                  items={opportunities.map(
                    (o) => `${o.title} — ${o.stage}${o.amount ? ` — ${o.amount} €` : ""}`
                  )}
                />
              </Panel>
              <Panel title="Interactions">
                <Adder
                  placeholder="Résumé de l'échange"
                  onAdd={(v) => api.addInteraction(selected.id, v).then(reload)}
                />
                <Lines items={interactions.map((i) => `[${i.channel}] ${i.summary}`)} />
              </Panel>
            </>
          )}
        </div>
      </div>
    </main>
  );
}

function Adder({
  placeholder,
  onAdd,
}: {
  placeholder: string;
  onAdd: (value: string) => Promise<unknown>;
}) {
  const [v, setV] = useState("");
  return (
    <div className="mb-3 flex gap-2">
      <input
        value={v}
        onChange={(e) => setV(e.target.value)}
        placeholder={placeholder}
        className="flex-1 rounded-md border border-slate-300 px-2 py-1 text-sm"
      />
      <GhostBtn
        onClick={() => {
          if (v.trim()) {
            onAdd(v);
            setV("");
          }
        }}
      >
        Ajouter
      </GhostBtn>
    </div>
  );
}

function Lines({ items }: { items: string[] }) {
  if (items.length === 0) return <p className="text-xs text-slate-400">Aucun élément.</p>;
  return (
    <ul className="space-y-1 text-sm">
      {items.map((t, i) => (
        <li key={i} className="rounded-md bg-slate-50 px-3 py-1.5">
          {t}
        </li>
      ))}
    </ul>
  );
}
