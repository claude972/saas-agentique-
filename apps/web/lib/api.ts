// Client API minimal pour le backend FastAPI.
// Les appels passent par /api/* (proxy configuré dans next.config.mjs).

const TOKEN_KEY = "btp_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  window.localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`/api${path}`, { ...init, headers });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail ?? `Erreur ${res.status}`);
  }
  return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
}

/** Ouvre dans un nouvel onglet un fichier servi par l'API (auth via header). */
export async function openAuthed(path: string): Promise<void> {
  const token = getToken();
  const res = await fetch(`/api${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) throw new Error(`Erreur ${res.status}`);
  const url = URL.createObjectURL(await res.blob());
  window.open(url, "_blank");
}

export async function login(email: string, password: string): Promise<string> {
  // L'endpoint /auth/login attend un form-urlencoded (OAuth2 password flow).
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch(`/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw new Error("Email ou mot de passe incorrect");
  const data = (await res.json()) as { access_token: string };
  setToken(data.access_token);
  return data.access_token;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  status: string;
  client_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface CurrentUser {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
}

export interface Conversation {
  id: string;
  project_id: string | null;
  title: string | null;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  role: string;
  content: string;
  created_at: string;
}

export interface ChatPostResponse {
  user_message: ChatMessage;
  assistant_message: ChatMessage;
  plan: { agents: string[]; parallel: boolean };
}

export interface DocumentItem {
  id: string;
  filename: string;
  mime_type: string | null;
  kind: string;
}

export interface PhotoItem {
  id: string;
  caption: string | null;
  analysis: string | null;
}

export interface QuoteItem {
  id: string;
  reference: string;
  status: string;
  total_ht: number;
  pdf_s3_key: string | null;
}

export interface ReportItem {
  id: string;
  kind: string;
  title: string;
  validated: boolean;
}

export interface TenderItem {
  id: string;
  title: string;
  buyer: string | null;
  decision: string;
  qualification: string | null;
}

function upload<T>(path: string, file: File, fields: Record<string, string> = {}): Promise<T> {
  const form = new FormData();
  form.append("file", file);
  for (const [k, v] of Object.entries(fields)) form.append(k, v);
  return request<T>(path, { method: "POST", body: form });
}

export const api = {
  me: () => request<CurrentUser>("/auth/me"),
  listProjects: () => request<Project[]>("/projects"),
  createProject: (payload: { name: string; description?: string }) =>
    request<Project>("/projects", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // Chat (mémoire persistante par projet)
  listConversations: (projectId: string) =>
    request<Conversation[]>(`/projects/${projectId}/conversations`),
  createConversation: (projectId: string, title?: string) =>
    request<Conversation>(`/projects/${projectId}/conversations`, {
      method: "POST",
      body: JSON.stringify({ title }),
    }),
  listMessages: (conversationId: string) =>
    request<ChatMessage[]>(`/conversations/${conversationId}/messages`),
  postMessage: (conversationId: string, content: string) =>
    request<ChatPostResponse>(`/conversations/${conversationId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),

  getProject: (id: string) => request<Project>(`/projects/${id}`),

  // Documents
  listDocuments: (pid: string) => request<DocumentItem[]>(`/projects/${pid}/documents`),
  uploadDocument: (pid: string, file: File) =>
    upload<DocumentItem>(`/projects/${pid}/documents`, file),
  analyzeDocument: (id: string) =>
    request<DocumentItem>(`/documents/${id}/analyze`, { method: "POST" }),

  // Photos
  listPhotos: (pid: string) => request<PhotoItem[]>(`/projects/${pid}/photos`),
  uploadPhoto: (pid: string, file: File, caption: string) =>
    upload<PhotoItem>(`/projects/${pid}/photos`, file, caption ? { caption } : {}),
  analyzePhoto: (id: string) =>
    request<PhotoItem>(`/photos/${id}/analyze`, { method: "POST" }),

  // Devis
  listQuotes: (pid: string) => request<QuoteItem[]>(`/projects/${pid}/quotes`),
  generateQuote: (pid: string, description: string) =>
    request<QuoteItem>(`/projects/${pid}/quotes/generate`, {
      method: "POST",
      body: JSON.stringify({ description }),
    }),
  buildQuotePdf: (id: string) =>
    request<QuoteItem>(`/quotes/${id}/pdf`, { method: "POST" }),

  // Comptes-rendus
  listReports: (pid: string) => request<ReportItem[]>(`/projects/${pid}/reports`),
  generateReport: (pid: string, title: string, kind: string) =>
    request<ReportItem>(`/projects/${pid}/reports/generate`, {
      method: "POST",
      body: JSON.stringify({ title, kind }),
    }),
  validateReport: (id: string) =>
    request<ReportItem>(`/reports/${id}/validate`, { method: "POST" }),

  // Appels d'offres
  listTenders: (pid: string) => request<TenderItem[]>(`/projects/${pid}/tenders`),
  createTender: (pid: string, title: string, buyer: string) =>
    request<TenderItem>(`/projects/${pid}/tenders`, {
      method: "POST",
      body: JSON.stringify({ title, buyer: buyer || null }),
    }),
  qualifyTender: (id: string, score: number) =>
    request<TenderItem>(`/tenders/${id}/qualify`, {
      method: "POST",
      body: JSON.stringify({ score }),
    }),
  respondTender: (id: string) =>
    request<{ document_id: string; memoire_technique: string }>(
      `/tenders/${id}/respond`,
      { method: "POST" }
    ),
};
