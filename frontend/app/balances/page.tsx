'use client';

import { useEffect, useState } from "react";
import { Sidebar } from "../_components/Sidebar";
import { PageHeader } from "../_components/PageHeader";
import { ProviderLogo } from "../_components/ProviderLogo";
import { backendApi } from "../lib/backend/client";
import type { BalanceRow } from "../lib/backend/types";

function formatAmount(amount: number, currency: string) {
  // Crypto-like assets need more decimals; fiat sticks to 2.
  const isCrypto = currency !== "USD" && currency !== "ARS";
  return amount.toLocaleString("es-AR", {
    minimumFractionDigits: isCrypto ? 3 : 2,
    maximumFractionDigits: isCrypto ? 3 : 2,
  });
}

function CopyableAccount({ account, raw }: { account: string; raw: any }) {
  const [copied, setCopied] = useState(false);
  const address = raw?.address;

  if (!address) {
    return <div className="text-xs text-muted font-mono truncate">{account}</div>;
  }

  return (
    <div className="flex items-center gap-1.5">
      <div className="text-xs text-muted font-mono truncate">{account}</div>
      <button
        onClick={() => {
          navigator.clipboard.writeText(address);
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
        }}
        className="text-accent hover:text-accent/80 transition-colors"
        title="Copiar dirección"
      >
        {copied ? (
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-check"><polyline points="20 6 9 17 4 12"></polyline></svg>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-copy"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect><path d="M4 15v-1c0-1.1.9-2 2-2h1v9a2 2 0 0 0 2 2h10c1.1 0 2-.9 2-2V19"></path></svg>
        )}
      </button>
    </div>
  );
}

export default function BalancesPage() {
  const [balances, setBalances] = useState<BalanceRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    backendApi.getBalances().then((data) => {
      setBalances(data);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  return (
    <Sidebar>
      <div className="flex min-h-0 flex-1 flex-col">
        <PageHeader title="Balances" description="Saldos por proveedor y moneda." />
        <div className="flex-1 overflow-y-auto overscroll-contain bg-background px-4 py-6 sm:px-6 lg:px-10">
          {loading ? (
            <div className="text-center text-muted py-10">Cargando balances...</div>
          ) : (
            <div className="mx-auto max-w-5xl grid gap-4 sm:grid-cols-2">
              {balances.length === 0 ? (
                <div className="col-span-2 text-center text-muted py-10 border border-dashed border-line rounded-3xl">
                  No se encontraron balances.
                </div>
              ) : null}
              {balances.map((item, idx) => (
                <div
                  key={idx}
                  className="rounded-3xl border border-line bg-card p-6 shadow-card transition-all duration-200 hover:border-accent/25 hover:shadow-card-hover"
                >
                  <div className="flex items-center gap-3">
                    <ProviderLogo provider={item.provider} size="md" />
                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-medium text-foreground truncate">
                        {item.provider}
                      </div>
                      <CopyableAccount account={item.account} raw={item.raw} />
                    </div>
                  </div>
                  <div className="mt-4 text-2xl font-semibold tabular-nums text-foreground">
                    {item.currency === "USD" ? "$" : ""}
                    {formatAmount(item.amount, item.currency)}
                  </div>
                  <div className="text-xs text-subdued font-mono">{item.symbol}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Sidebar>
  );
}
