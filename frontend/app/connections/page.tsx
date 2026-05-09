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
        <div className="flex-1 overflow-y-auto overscroll-contain bg-[#050505] px-4 py-6 sm:px-6 lg:px-10">
          <div className="mx-auto max-w-5xl grid gap-4 md:grid-cols-2">
            {connections.map((item) => (
              <div
                key={item.id}
                className="rounded-3xl border border-[#1A1A1A] bg-[#080C0D] p-6 shadow-[0_0_24px_rgba(56,217,198,0.03)] transition-all duration-200 hover:border-[#38D9C6]/25 hover:shadow-[0_0_30px_rgba(56,217,198,0.06)]"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-base font-medium text-[#F4F8FB]">{item.name}</div>
                    <div className="mt-1 text-xs text-[#A8B3C2] font-mono">{item.description}</div>
                  </div>
                  <span
                    className={`rounded-full px-2 py-1 text-xs font-medium border ${
                      item.status === "Conectado"
                        ? "bg-[#3EE98A]/10 text-[#3EE98A] border-[#3EE98A]/20 shadow-[0_0_10px_rgba(62,233,138,0.05)]"
                        : "bg-[#050505] text-[#6B7788] border-[#1A1A1A]"
                    }`}
                  >
                    {item.status}
                  </span>
                </div>
                <button
                  type="button"
                  className="mt-6 w-full rounded-xl border border-[#38D9C6]/25 bg-[#050505] px-3 py-2 text-xs font-medium text-[#A8B3C2] transition-all duration-200 hover:bg-[#38D9C6]/10 hover:text-[#F4F8FB] hover:border-[#38D9C6]/50 active:scale-[0.98]"
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
