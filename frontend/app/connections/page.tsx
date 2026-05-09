import { AppShell } from "../_components/AppShell";
import { PageHeader } from "../_components/PageHeader";

const connections = [
  {
    id: "wallbit",
    name: "Wallbit",
    status: "Conectado",
    description: "API key validada · Sync hace 5 min",
  },
  {
    id: "wallet",
    name: "Wallet Ethereum",
    status: "Conectado",
    description: "0xA7c...dE9 · Último bloque hace 1 min",
  },
  {
    id: "bank",
    name: "Banco tradicional",
    status: "No conectado",
    description: "Conectá tu banco para consolidar saldos",
  },
];

export default function ConnectionsPage() {
  return (
    <AppShell>
      <div className="flex min-h-0 flex-1 flex-col">
        <PageHeader
          title="Conexiones"
          description="Gestioná las cuentas y wallets vinculadas."
        />
        <div className="flex-1 bg-zinc-50 px-4 py-6 dark:bg-zinc-950 sm:px-6 lg:px-10">
          <div className="grid gap-4 md:grid-cols-2">
            {connections.map((item) => (
              <div
                key={item.id}
                className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-base font-medium">{item.name}</div>
                    <div className="text-xs text-zinc-500">{item.description}</div>
                  </div>
                  <span
                    className={`rounded-full px-2 py-1 text-xs font-medium ${
                      item.status === "Conectado"
                        ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-200"
                        : "bg-zinc-200 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-200"
                    }`}
                  >
                    {item.status}
                  </span>
                </div>
                <button
                  type="button"
                  className="mt-4 w-full rounded-xl border border-zinc-200 px-3 py-2 text-xs font-medium text-zinc-600 transition hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                >
                  {item.status === "Conectado" ? "Ver detalles" : "Conectar"}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
