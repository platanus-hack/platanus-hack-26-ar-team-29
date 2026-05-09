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
        <div className="flex-1 overflow-y-auto overscroll-contain bg-background px-4 py-6 sm:px-6 lg:px-10">
          <div className="mx-auto max-w-5xl rounded-3xl border border-line bg-card shadow-card">
            {activity.map((item) => (
              <div
                key={item.id}
                className="flex flex-col gap-2 border-b border-line px-5 py-4 last:border-b-0 sm:flex-row sm:items-center sm:justify-between transition-all duration-200 hover:bg-accent/5"
              >
                <div>
                  <div className="text-base font-medium text-foreground">{item.title}</div>
                  <div className="mt-1 text-xs text-muted font-mono">{item.detail}</div>
                </div>
                <div className="flex items-center gap-4 text-sm mt-2 sm:mt-0">
                  <span className="text-xs text-subdued">{item.time}</span>
                  <span
                    className={`rounded-full px-2 py-1 text-xs font-medium border ${
                      item.status === "Pendiente"
                        ? "bg-warning/10 text-warning border-warning/20"
                        : "bg-success/10 text-success border-success/20 shadow-success-soft"
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
