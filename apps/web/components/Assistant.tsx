"use client";

import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";

type Msg = { role: "user" | "assistant"; text: string; agents?: string[] };

const SUGGESTIONS = [
  "Analyse une photo et prépare un devis",
  "Détecte les AO gros œuvre",
  "Rédige un compte-rendu de réunion",
];

export function Assistant({ compact = false }: { compact?: boolean }) {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  async function send(text: string) {
    if (!text.trim() || busy) return;
    setMessages((m) => [...m, { role: "user", text }]);
    setInput("");
    setBusy(true);
    try {
      const res = await api.askSupervisor(text);
      setMessages((m) => [
        ...m,
        { role: "assistant", text: res.summary, agents: res.plan?.agents },
      ]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: "assistant", text: e instanceof Error ? e.message : "Erreur" },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex h-full flex-col">
      {/* En-tête */}
      <div className="flex items-center gap-2.5 border-b border-slate-100 px-4 py-3">
        <span className="relative flex h-2.5 w-2.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
          <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
        </span>
        <div>
          <p className="text-sm font-semibold text-ink">Assistant BTP</p>
          <p className="text-[11px] text-slate-400">Supervisor · 6 agents</p>
        </div>
      </div>

      {/* Fil */}
      <div className={"flex-1 space-y-3 overflow-y-auto px-4 py-4 " + (compact ? "min-h-[280px]" : "")}>
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-soft">
              ✦
            </div>
            <p className="text-sm font-medium text-slate-600">Comment puis-je vous aider ?</p>
            <p className="mt-1 max-w-xs text-xs text-slate-400">
              Décrivez votre besoin, le superviseur orchestre les agents.
            </p>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600 transition hover:border-brand hover:text-brand"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "flex justify-end" : "flex justify-start"}>
            <div className={m.role === "user" ? "max-w-[80%]" : "max-w-[85%]"}>
              <div
                className={
                  "whitespace-pre-wrap rounded-2xl px-3.5 py-2.5 text-sm " +
                  (m.role === "user"
                    ? "rounded-br-md bg-brand text-white"
                    : "rounded-bl-md border border-slate-200 bg-white text-slate-700")
                }
              >
                {m.text}
              </div>
              {m.agents && m.agents.length > 0 && (
                <div className="mt-1.5 flex flex-wrap gap-1">
                  {m.agents.map((a) => (
                    <span
                      key={a}
                      className="rounded-full bg-brand-light px-2 py-0.5 text-[10px] font-medium text-brand-dark"
                    >
                      {a}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {busy && (
          <div className="flex justify-start">
            <div className="flex items-center gap-1 rounded-2xl rounded-bl-md border border-slate-200 bg-white px-4 py-3">
              <Dot /> <Dot delay="150ms" /> <Dot delay="300ms" />
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Saisie */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="border-t border-slate-100 p-3"
      >
        <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-slate-50 px-3 py-1.5 focus-within:border-brand focus-within:bg-white">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Écrivez un message…"
            className="flex-1 bg-transparent py-1.5 text-sm outline-none placeholder:text-slate-400"
          />
          <button
            type="submit"
            disabled={busy || !input.trim()}
            className="flex h-8 w-8 items-center justify-center rounded-xl bg-brand text-white transition hover:bg-brand-dark disabled:opacity-40"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="h-4 w-4">
              <path d="M22 2 11 13M22 2l-7 20-4-9-9-4 20-7z" />
            </svg>
          </button>
        </div>
      </form>
    </div>
  );
}

function Dot({ delay = "0ms" }: { delay?: string }) {
  return (
    <span
      className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400"
      style={{ animationDelay: delay }}
    />
  );
}
