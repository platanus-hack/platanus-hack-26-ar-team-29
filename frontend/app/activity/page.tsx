import { AppShell } from "../_components/AppShell";
import { PageHeader } from "../_components/PageHeader";

const activity = [
  {
    id: "1",
    title: "Compra SPY",
    detail: "USD 500 · Wallbit",
    time: "Hace 3 min",
    status: "Completado",
  },
  {
    id: "2",
    title: "Swap USDC → ETH",
    detail: "USDC 400 · Wallet",
    time: "Hace 2 h",
    status: "Completado",
  },
  {
    id: "3",
    title: "Plan DCA mensual",
    detail: "USD 150 · Wallbit",
    time: "Ayer",
    status: "Pendiente",
  },
  {
    id: "4",
    title: "Ingreso transferencia",
    detail: "USD 1.200 · Wallbit",
    time: "Hace 2 días",
    status: "Completado",
  },
];

export default function ActivityPage() {
  return (
    <AppShell>
      <div className="flex min-h-0 flex-1 flex-col">
        <PageHeader title="Actividad" description="Movimientos recientes y estado de planes." />
        <div className="flex-1 overflow-y-auto overscroll-contain bg-[#050505] px-4 py-6 sm:px-6 lg:px-10">
          <div className="mx-auto max-w-5xl rounded-3xl border border-[#1A1A1A] bg-[#080C0D] shadow-[0_0_24px_rgba(56,217,198,0.03)]">
            {activity.map((item) => (
              <div
                key={item.id}
                className="flex flex-col gap-2 border-b border-[#1A1A1A] px-5 py-4 last:border-b-0 sm:flex-row sm:items-center sm:justify-between transition-all duration-200 hover:bg-[#38D9C6]/5"
              >
                <div>
                  <div className="text-base font-medium text-[#F4F8FB]">{item.title}</div>
                  <div className="mt-1 text-xs text-[#A8B3C2] font-mono">{item.detail}</div>
                </div>
                <div className="flex items-center gap-4 text-sm mt-2 sm:mt-0">
                  <span className="text-xs text-[#6B7788]">{item.time}</span>
                  <span
                    className={`rounded-full px-2 py-1 text-xs font-medium border ${
                      item.status === "Pendiente"
                        ? "bg-[#F5B84B]/10 text-[#F5B84B] border-[#F5B84B]/20"
                        : "bg-[#3EE98A]/10 text-[#3EE98A] border-[#3EE98A]/20 shadow-[0_0_10px_rgba(62,233,138,0.05)]"
                    }`}
                  >
                    {item.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
