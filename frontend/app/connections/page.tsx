import { Sidebar } from "../_components/Sidebar";
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
    <Sidebar>
      <div className="flex min-h-0 flex-1 flex-col">
        <PageHeader
          title="Conexiones"
          description="Gestioná las cuentas y wallets vinculadas."
        />
        <div className="flex-1 overflow-y-auto overscroll-contain bg-background px-4 py-6 sm:px-6 lg:px-10">
          <div className="mx-auto max-w-5xl grid gap-4 md:grid-cols-2">
            {connections.map((item) => (
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
                        : "bg-background text-subdued border-line"
                    }`}
                  >
                    {item.status}
                  </span>
                </div>
                <button
                  type="button"
                  className="mt-6 w-full rounded-xl border border-accent/25 bg-background px-3 py-2 text-xs font-medium text-muted transition-all duration-200 hover:bg-accent/10 hover:text-foreground hover:border-accent/50 active:scale-[0.98]"
                >
                  {item.status === "Conectado" ? "Ver detalles" : "Conectar"}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Sidebar>
  );
}
