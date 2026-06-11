"use client";

import { useEffect, useRef, useState } from "react";
import { Shell } from "@/components/Shell";
import { api, type ChatMessage, type Project } from "@/lib/api";

export default function ChatPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectId, setProjectId] = useState("");
  const [conversationId, setConversationId] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.listProjects().then((p) => {
      setProjects(p);
      if (p[0]) setProjectId(p[0].id);
    });
  }, []);

  useEffect(() => {
    if (!projectId) return;
    api.createConversation(projectId, "Conversation web").then((c) => {
      setConversationId(c.id);
      setMessages([]);
    });
  }, [projectId]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || !conversationId || busy) return;
    const content = input;
    setInput("");
    setBusy(true);
    try {
      const res = await api.postMessage(conversationId, content);
      setMessages((m) => [...m, res.user_message, res.assistant_message]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Shell active="chat">
      <div className="mx-auto flex h-screen max-w-4xl flex-col px-6 py-6">
        {/* En-tête */}
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-ink">Assistant IA</h1>
            <p className="text-sm text-slate-500">
              Le superviseur orchestre les agents · mémoire par projet
            </p>
          </div>
          <select
            value={projectId}
            onChange={(e) => setProjectId(e.target.value)}
            className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm shadow-card focus:border-brand focus:outline-none"
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>

        {/* Fil */}
        <div className="flex-1 space-y-4 overflow-y-auto rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
          {messages.length === 0 && (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 text-2xl text-white shadow-soft">
                ✦
              </div>
              <p className="font-medium text-slate-600">Démarrez la conversation</p>
              <p className="mt-1 max-w-sm text-sm text-slate-400">
                Ex. « Analyse cette photo de chantier et prépare un devis », « Rédige
                un compte-rendu de réunion », « Détecte les AO gros œuvre ».
              </p>
            </div>
          )}

          {messages.map((m) => (
            <div key={m.id} className={m.role === "user" ? "flex justify-end" : "flex justify-start gap-2.5"}>
              {m.role === "assistant" && (
                <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-sm text-white">
                  ✦
                </div>
              )}
              <div
                className={
                  "max-w-[78%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm " +
                  (m.role === "user"
                    ? "rounded-br-md bg-brand text-white"
                    : "rounded-bl-md border border-slate-200 bg-slate-50 text-slate-700")
                }
              >
                {m.content}
              </div>
            </div>
          ))}

          {busy && (
            <div className="flex justify-start gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-sm text-white">
                ✦
              </div>
              <div className="flex items-center gap-1 rounded-2xl rounded-bl-md border border-slate-200 bg-slate-50 px-4 py-3">
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400" />
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400" style={{ animationDelay: "150ms" }} />
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* Saisie */}
        <form onSubmit={send} className="mt-4">
          <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-3 py-2 shadow-card focus-within:border-brand">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Votre message…"
              className="flex-1 bg-transparent py-1.5 text-sm outline-none placeholder:text-slate-400"
            />
            <button
              disabled={busy || !input.trim()}
              className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand text-white transition hover:bg-brand-dark disabled:opacity-40"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="h-4 w-4">
                <path d="M22 2 11 13M22 2l-7 20-4-9-9-4 20-7z" />
              </svg>
            </button>
          </div>
        </form>
      </div>
    </Shell>
  );
}
