"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import {
  api,
  getToken,
  type ChatMessage,
  type Project,
} from "@/lib/api";

export default function ChatPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectId, setProjectId] = useState<string>("");
  const [conversationId, setConversationId] = useState<string>("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    api.listProjects().then((p) => {
      setProjects(p);
      if (p[0]) setProjectId(p[0].id);
    });
  }, [router]);

  // À chaque changement de projet, on (ré)ouvre une conversation.
  useEffect(() => {
    if (!projectId) return;
    api
      .createConversation(projectId, "Conversation web")
      .then((c) => {
        setConversationId(c.id);
        setMessages([]);
      })
      .catch((e) => setError(String(e)));
  }, [projectId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || !conversationId || busy) return;
    setBusy(true);
    setError(null);
    const content = input;
    setInput("");
    try {
      const res = await api.postMessage(conversationId, content);
      setMessages((prev) => [...prev, res.user_message, res.assistant_message]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto flex h-screen max-w-3xl flex-col p-4">
      <header className="mb-3 flex items-center justify-between">
        <h1 className="text-xl font-bold text-brand">Chat agents</h1>
        <select
          value={projectId}
          onChange={(e) => setProjectId(e.target.value)}
          className="rounded-md border border-slate-300 px-2 py-1 text-sm"
        >
          {projects.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </header>

      <div className="flex-1 space-y-3 overflow-y-auto rounded-xl border border-slate-200 bg-white p-4">
        {messages.length === 0 && (
          <p className="text-sm text-slate-400">
            Décrivez votre besoin (ex. « analyse cette photo et prépare un devis »).
            Le SupervisorAgent choisit les agents et fusionne les résultats.
          </p>
        )}
        {messages.map((m) => (
          <div
            key={m.id}
            className={m.role === "user" ? "text-right" : "text-left"}
          >
            <span
              className={
                "inline-block max-w-[85%] whitespace-pre-wrap rounded-2xl px-3 py-2 text-sm " +
                (m.role === "user"
                  ? "bg-brand text-white"
                  : "bg-slate-100 text-slate-800")
              }
            >
              {m.content}
            </span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {error && (
        <p className="mt-2 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}

      <form onSubmit={send} className="mt-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Votre message…"
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2"
        />
        <button
          disabled={busy}
          className="rounded-lg bg-brand px-4 py-2 font-medium text-white hover:bg-brand-dark disabled:opacity-60"
        >
          {busy ? "…" : "Envoyer"}
        </button>
      </form>
    </main>
  );
}
