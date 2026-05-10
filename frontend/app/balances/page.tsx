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
                      <div className="text-xs text-muted font-mono truncate">
                        {item.account}
                      </div>
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
