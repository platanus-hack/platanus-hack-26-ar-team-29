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
        <div className="flex-1 bg-zinc-50 px-4 py-6 dark:bg-zinc-950 sm:px-6 lg:px-10">
          <div className="rounded-2xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
            {activity.map((item) => (
              <div
                key={item.id}
                className="flex flex-col gap-2 border-b border-zinc-100 px-4 py-4 last:border-b-0 dark:border-zinc-800 sm:flex-row sm:items-center sm:justify-between"
              >
                <div>
                  <div className="text-base font-medium">{item.title}</div>
                  <div className="text-xs text-zinc-500">{item.detail}</div>
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-xs text-zinc-500">{item.time}</span>
                  <span
                    className={`rounded-full px-2 py-1 text-xs font-medium ${
                      item.status === "Pendiente"
                        ? "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-200"
                        : "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-200"
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
