"use client";

import { type ReactNode } from "react";

/** Carte de module avec titre et contenu (utilisée par le hub projet). */
export function Panel({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="mb-3 font-semibold text-slate-800">{title}</h2>
      {children}
    </section>
  );
}

export function Btn({
  children,
  onClick,
  disabled,
}: {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="rounded-md bg-brand px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-dark disabled:opacity-50"
    >
      {children}
    </button>
  );
}

export function GhostBtn({
  children,
  onClick,
}: {
  children: ReactNode;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="rounded-md border border-slate-300 px-2.5 py-1 text-xs hover:bg-slate-100"
    >
      {children}
    </button>
  );
}
