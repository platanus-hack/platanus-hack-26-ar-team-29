"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export function SyncButton() {
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSync = async () => {
    setLoading(true);
    try {
      const url = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
      const res = await fetch(`${url}/api/v1/transactions/sync`, {
        method: "POST",
      });
      if (res.ok) {
        alert("Sincronización iniciada en segundo plano. Los cambios aparecerán en breve.");
        // Give it a bit of time then refresh
        setTimeout(() => {
          router.refresh();
          setLoading(false);
        }, 2000);
      } else {
        alert("Error al iniciar sincronización.");
        setLoading(false);
      }
    } catch (error) {
      console.error(error);
      alert("Error al conectar con el backend.");
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleSync}
      disabled={loading}
      className={`rounded-xl border border-accent/25 bg-background px-4 py-2 text-sm font-medium text-foreground transition-all duration-200 hover:bg-accent/10 hover:border-accent/50 active:scale-[0.98] ${
        loading ? "opacity-50 cursor-not-allowed" : ""
      }`}
    >
      {loading ? "Sincronizando..." : "Sincronizar Wallbit"}
    </button>
  );
}
