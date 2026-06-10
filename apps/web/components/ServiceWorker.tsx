"use client";

import { useEffect } from "react";

/** Enregistre le service worker PWA côté client (no-op si non supporté). */
export function ServiceWorker() {
  useEffect(() => {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js").catch(() => {
        /* enregistrement best-effort */
      });
    }
  }, []);
  return null;
}
