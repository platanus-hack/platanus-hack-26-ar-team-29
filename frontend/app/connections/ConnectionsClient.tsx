"use client";

import { useState, useCallback } from "react";
import { ProviderLogo } from "../_components/ProviderLogo";

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
  const [isDisconnecting, setIsDisconnecting] = useState(false); // New state for disconnecting
  const [mnemonicData, setMnemonicData] = useState<{ mnemonic: string, address: string } | null>(null);

  const [copiedListId, setCopiedListId] = useState<string | null>(null);
  const [copiedModalAddress, setCopiedModalAddress] = useState(false);
  const [copiedModalMnemonic, setCopiedModalMnemonic] = useState(false);

  const copyToClipboard = <T,>(text: string, setter: (val: T) => void, val: T, clearVal: T) => {
    navigator.clipboard.writeText(text);
    setter(val);
    setTimeout(() => setter(clearVal), 2000);
  };

  const wallbitConnection = connections.find(c => c.connection_type === "wallbit");
  const ethereumConnections = connections.filter(c => c.connection_type === "ethereum_custodial");

  const handleDisconnectCryptoWallet = useCallback(async (connectionId: string) => {
    setIsDisconnecting(true); // Set disconnecting state
    const isConfirmed = window.confirm(
      "¿Estás seguro de que quieres desconectar esta wallet? Se eliminará tu clave privada/frase semilla de la base de datos y no podrás recuperarla."
    );

    if (isConfirmed) {
      try {
        const res = await fetch(`${url}/api/v1/connections/${connectionId}`, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (res.ok) {
          // Refresh connections
          const refreshRes = await fetch(`${url}/api/v1/connections`, { cache: 'no-store' });
          if (refreshRes.ok) {
            setConnections(await refreshRes.json());
          } else {
            alert("Error al refrescar la lista de conexiones después de desconectar.");
          }
        } else {
          const errorData = await res.json();
          alert(`Error al desconectar: ${errorData.error?.message_es || "Fallo al desconectar la wallet"}`);
        }
      } catch (error) {
        console.error(error);
        alert("Error de conexión al intentar desconectar.");
      } finally {
        setIsDisconnecting(false); // Reset disconnecting state
      }
    } else {
      setIsDisconnecting(false); // Reset disconnecting state if cancelled
    }
  }, [url, setConnections]); // Dependency array includes url and setConnections

  const displayList = [
    {
      id: "wallbit",
      connectionId: wallbitConnection?.id,
      name: "Wallbit",
      status: wallbitConnection ? "Conectado" : "No conectado",
      description: wallbitConnection ? "API key validada" : "Conectá tu cuenta de Wallbit",
    },
    // If no ethereum connections exist, show a single placeholder to connect one.
    // Otherwise, map all existing ethereum connections.
    ...(ethereumConnections.length > 0 
      ? ethereumConnections.map((ethConn) => ({
          id: "ethereum_custodial",
          connectionId: ethConn.id,
          name: "Wallet Ethereum",
          status: "Conectado",
          address: ethConn.address,
          description: ethConn.address ? `${ethConn.address.slice(0, 6)}...${ethConn.address.slice(-4)} (${(ethConn.network || "sepolia").charAt(0).toUpperCase() + (ethConn.network || "sepolia").slice(1)})` : "Wallet conectada",
        }))
      : [{
          id: "ethereum_custodial",
          connectionId: undefined,
          name: "Wallet Ethereum",
          status: "No conectado",
          address: undefined,
          description: "Creá una wallet custodial",
        }]
    ),
    {
      id: "bank",
      connectionId: undefined,
      name: "Tu fintech de confianza",
      status: "Próximamente",
      description: "Sumá tu billetera virtual para consolidar todos tus saldos en un solo lugar",
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
        {displayList.map((item, index) => (
          <div
            key={item.connectionId || item.id + index}
            className="rounded-3xl border border-line bg-card p-6 shadow-card transition-all duration-200 hover:border-accent/25 hover:shadow-card-hover"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3 min-w-0">
                <ProviderLogo provider={item.id} size="md" />
                  <div className="min-w-0">
                    <div className="text-base font-medium text-foreground">{item.name}</div>
                    <div className="mt-1 text-xs text-muted font-mono break-words flex items-center gap-1.5">
                      {item.id === "ethereum_custodial" && item.address ? (
                        <>
                          {item.description}
                          <button
                            onClick={() => copyToClipboard(item.address!, setCopiedListId, item.connectionId || item.id, null)}
                            className="text-accent hover:text-accent/80 transition-colors"
                            aria-label="Copiar dirección"
                          >
                            {copiedListId === (item.connectionId || item.id) ? (
                              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-check"><polyline points="20 6 9 17 4 12"></polyline></svg>
                            ) : (
                              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-copy"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect><path d="M4 15v-1c0-1.1.9-2 2-2h1v9a2 2 0 0 0 2 2h10c1.1 0 2-.9 2-2V19"></path></svg>
                            )}
                          </button>
                        </>
                      ) : (
                        item.description
                      )}
                    </div>
                  </div>
                </div>
                <span
                  className={`shrink-0 rounded-full px-2 py-1 text-xs font-medium border ${
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


            {/* Buttons section */}
            <div className="mt-6 flex gap-3">
              {/* Connect/Connected Button */}
              <button
                type="button"
                disabled={
                  item.status !== "No conectado" || // Disable if not "No conectado"
                  isCreating ||
                  isDisconnecting
                }
                onClick={() => {
                  if (item.id === "ethereum_custodial") {
                    handleCreateEthereum();
                  } else if (item.id === "wallbit") {
                    alert("Para conectar Wallbit, se necesita el API key (no implementado en esta vista aún).");
                  }
                }}
                className={`flex-1 rounded-xl border px-3 py-2 text-xs font-medium transition-all duration-200 active:scale-[0.98] ${
                  item.status !== "No conectado" || isCreating || isDisconnecting
                    ? "bg-background border-line text-muted opacity-50 cursor-not-allowed"
                    : "border-accent/25 bg-background text-muted hover:bg-accent/10 hover:text-foreground hover:border-accent/50"
                }`}
              >
                {isCreating && item.id === "ethereum_custodial" ? "Creando..." : item.status === "Conectado" ? "Conectado" : "Conectar"}
              </button>

              {/* Disconnect Button */}
              {item.status === "Conectado" && (
                <button
                  type="button"
                  disabled={isDisconnecting || isCreating || item.id === "wallbit"} // Disable if disconnecting or creating
                  onClick={() => {
                    if (item.id === "ethereum_custodial" && item.connectionId) {
                      handleDisconnectCryptoWallet(item.connectionId);
                    }
                  }}
                  className={`flex-1 rounded-xl border px-3 py-2 text-xs font-medium transition-all duration-200 active:scale-[0.98] ${
                    isDisconnecting || isCreating || item.id === "wallbit"
                      ? "bg-background border-line text-muted opacity-50 cursor-not-allowed"
                      : "border-destructive/25 bg-background text-destructive hover:bg-destructive/10 hover:border-destructive/50"
                  }`}
                >
                  Desconectar
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {mnemonicData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4">
          <div className="bg-card border border-line rounded-3xl shadow-2xl max-w-md w-full p-8 space-y-6">
            <h3 className="text-xl font-bold text-foreground">¡Wallet Creada!</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-muted mb-1">Tu dirección es</p>
                <div className="flex items-center gap-2">
                  <code className="bg-accent/10 px-2 py-1 rounded text-accent flex-1 break-all">{mnemonicData.address}</code>
                  <button
                    onClick={() => copyToClipboard(mnemonicData.address, setCopiedModalAddress, true, false)}
                    className="shrink-0 p-1.5 bg-accent/10 text-accent rounded hover:bg-accent/20 transition-colors"
                    title="Copiar dirección"
                  >
                    {copiedModalAddress ? (
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect><path d="M4 15v-1c0-1.1.9-2 2-2h1v9a2 2 0 0 0 2 2h10c1.1 0 2-.9 2-2V19"></path></svg>
                    )}
                  </button>
                </div>
              </div>
              <div className="bg-warning/10 border border-warning/20 rounded-xl p-4">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <p className="text-sm font-medium text-warning">Importante: Guardá tu frase semilla</p>
                    <p className="text-xs text-warning/80 mt-1">
                      Esta es la única vez que verás esta frase. Si la perdés, no podrás recuperar el acceso.
                    </p>
                  </div>
                  <button
                    onClick={() => copyToClipboard(mnemonicData.mnemonic, setCopiedModalMnemonic, true, false)}
                    className="shrink-0 p-1.5 bg-warning/20 text-warning rounded hover:bg-warning/30 transition-colors"
                    title="Copiar frase semilla"
                  >
                    {copiedModalMnemonic ? (
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect><path d="M4 15v-1c0-1.1.9-2 2-2h1v9a2 2 0 0 0 2 2h10c1.1 0 2-.9 2-2V19"></path></svg>
                    )}
                  </button>
                </div>
                <div className="grid grid-cols-3 gap-2 mt-3">
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
