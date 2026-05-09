import { AppShell } from "../_components/AppShell";
import { PageHeader } from "../_components/PageHeader";

const balances = [
  {
    provider: "Wallbit",
    account: "Cuenta USD",
    currency: "USD",
    available: "$2.450.000",
    updated: "hace 2 min",
  },
  {
    provider: "Wallbit",
    account: "Inversiones",
    currency: "USD",
    available: "$1.125.000",
    updated: "hace 2 min",
  },
  {
    provider: "Wallet",
    account: "USDC",
    currency: "USDC",
    available: "$890.000",
    updated: "hace 1 min",
  },
  {
    provider: "Wallet",
    account: "ETH",
    currency: "ETH",
    available: "1.9 ETH",
    updated: "hace 1 min",
  },
];

export default function BalancesPage() {
  return (
    <AppShell>
      <div className="flex min-h-0 flex-1 flex-col">
        <PageHeader title="Balances" description="Saldos por proveedor y moneda." />
        <div className="flex-1 bg-zinc-50 px-4 py-6 dark:bg-zinc-950 sm:px-6 lg:px-10">
          <div className="grid gap-4 sm:grid-cols-2">
            {balances.map((item) => (
              <div
                key={`${item.provider}-${item.account}`}
                className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
              >
                <div className="flex items-center justify-between text-xs text-zinc-500">
                  <span>
                    {item.provider} · {item.account}
                  </span>
                  <span>{item.updated}</span>
                </div>
                <div className="mt-2 text-lg font-semibold">{item.available}</div>
                <div className="text-xs text-zinc-500">{item.currency}</div>
                <button
                  type="button"
                  className="mt-4 w-full rounded-xl border border-zinc-200 px-3 py-2 text-xs font-medium text-zinc-600 transition hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                >
                  Pedir a OpenFi
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
