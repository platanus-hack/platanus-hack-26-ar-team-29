"use client";

import { useState, useCallback } from "react";

export interface Connection {
  id: string;
  connection_type: string;
  label?: string;
  status: string;
  capabilities: string[];
  created_at: string;
  address?: string;
  network?: string;
  chain_id?: number;
  primary_asset_hint?: string;
}

export function ConnectionsClient({ initialConnections, url }: { initialConnections: Connection[], url: string }) {
  const [connections, setConnections] = useState(initialConnections);
  const [isCreating, setIsCreating] = useState(false);
  const [mnemonicData, setMnemonicData] = useState<{ mnemonic: string, address: string } | null>(null);

  const ethereumConnection = connections.find(c => c.connection_type === "ethereum_custodial");
  const wallbitConnection = connections.find(c => c.connection_type === "wallbit");

  const displayList = [
    {
      id: "wallbit",
      name: "Wallbit",
      status: wallbitConnection ? "Conectado" : "No conectado",
      description: wallbitConnection ? "API key validada" : "Conectá tu cuenta de Wallbit",
    },
    {
      id: "ethereum_custodial",
      name: "Wallet Ethereum",
      status: ethereumConnection ? "Conectado" : "No conectado",
      description: ethereumConnection?.address ? `${ethereumConnection.address.slice(0, 6)}...${ethereumConnection.address.slice(-4)} (${ethereumConnection.network || "sepolia"})` : "Creá una wallet custodial",
    },
    {
      id: "bank",
      name: "Banco tradicional",
      status: "Próximamente",
      description: "Conectá tu banco para consolidar saldos",
    },
  ];

  const handleCreateEthereum = useCallback(async () => {
    setIsCreating(true);
    try {
      const res = await fetch(`${url}/api/v1/connections/ethereum-custodial/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          network: "sepolia",
          label: "Wallet Ethereum",
          primary_asset_hint: "ETH"
        }),
      });
      if (res.ok) {
        const json = await res.json();
        setMnemonicData({
          mnemonic: json.data.mnemonic,
          address: json.data.address
        });
        
        // Refresh connections
        const refreshRes = await fetch(`${url}/api/v1/connections`, { cache: 'no-store' });
        if (refreshRes.ok) {
          setConnections(await refreshRes.json());
        }
      } else {
        const errorData = await res.json();
        alert(`Error: ${errorData.error?.message_es || "Fallo al crear la wallet"}`);
      }
    } catch (error) {
      console.error(error);
      alert("Error de conexión");
    } finally {
      setIsCreating(false);
    }
  }, [url]);

  return (
    <>
      <div className="mx-auto max-w-5xl grid gap-4 md:grid-cols-2">
        {displayList.map((item) => (
          <div
            key={item.id}
            className="rounded-3xl border border-line bg-card p-6 shadow-card transition-all duration-200 hover:border-accent/25 hover:shadow-card-hover"
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="text-base font-medium text-foreground">{item.name}</div>
                <div className="mt-1 text-xs text-muted font-mono">{item.description}</div>
              </div>
              <span
                className={`rounded-full px-2 py-1 text-xs font-medium border ${
                  item.status === "Conectado"
                    ? "bg-success/10 text-success border-success/20 shadow-success-soft"
                    : item.status === "Próximamente"
                    ? "bg-accent/10 text-accent border-accent/20"
                    : "bg-background text-subdued border-line"
                }`}
              >
                {item.status}
              </span>
            </div>
            <button
              type="button"
              disabled={item.status === "Conectado" || item.status === "Próximamente" || isCreating}
              onClick={() => {
                if (item.id === "ethereum_custodial") {
                  handleCreateEthereum();
                } else if (item.id === "wallbit") {
                  alert("Para conectar Wallbit, se necesita el API key (no implementado en esta vista aún).");
                }
              }}
              className={`mt-6 w-full rounded-xl border px-3 py-2 text-xs font-medium transition-all duration-200 active:scale-[0.98] ${
                item.status === "Conectado" || item.status === "Próximamente" 
                  ? "bg-background border-line text-muted opacity-50 cursor-not-allowed" 
                  : "border-accent/25 bg-background text-muted hover:bg-accent/10 hover:text-foreground hover:border-accent/50"
              }`}
            >
              {isCreating && item.id === "ethereum_custodial" ? "Creando..." : item.status === "Conectado" ? "Conectado" : "Conectar"}
            </button>
          </div>
        ))}
      </div>

      {mnemonicData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4">
          <div className="bg-card border border-line rounded-3xl shadow-2xl max-w-md w-full p-8 space-y-6">
            <h3 className="text-xl font-bold text-foreground">¡Wallet Creada!</h3>
            <div className="space-y-4">
              <p className="text-sm text-muted">
                Tu dirección es <code className="bg-accent/10 px-1 py-0.5 rounded text-accent">{mnemonicData.address}</code>
              </p>
              <div className="bg-warning/10 border border-warning/20 rounded-xl p-4">
                <p className="text-sm font-medium text-warning mb-2">Importante: Guardá tu frase semilla</p>
                <p className="text-xs text-warning/80 mb-3">
                  Esta es la única vez que verás esta frase. Si la perdés, no podrás recuperar el acceso.
                </p>
                <div className="grid grid-cols-3 gap-2">
                  {mnemonicData.mnemonic.split(" ").map((word: string, i: number) => (
                    <div key={i} className="bg-background border border-warning/20 rounded-md py-1 px-2 flex items-center gap-1.5">
                      <span className="text-[10px] text-warning/50 select-none">{i + 1}</span>
                      <span className="text-xs font-mono font-medium text-warning-foreground">{word}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <button
              onClick={() => setMnemonicData(null)}
              className="w-full rounded-xl bg-foreground text-background py-3 text-sm font-medium hover:bg-foreground/90 transition-colors"
            >
              Ya guardé mi frase
            </button>
          </div>
        </div>
      )}
    </>
  );
}
