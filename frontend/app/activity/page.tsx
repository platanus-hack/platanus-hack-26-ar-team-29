import { Sidebar } from "../_components/Sidebar";
import { PageHeader } from "../_components/PageHeader";
import { SyncButton } from "./SyncButton";

export const dynamic = "force-dynamic";

interface ActivityItem {
  id: string;
  type?: string;
  merchant?: string;
  classifier?: { category?: string; merchant?: string };
  title?: string;
  detail?: string;
  source_amount?: number;
  source_currency?: string;
  dest_amount?: number;
  dest_unit?: string;
  occurred_at?: string;
  status?: string;
  time?: string;
}

export default async function ActivityPage() {
  const url = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
  let activity = [];
  try {
    const res = await fetch(`${url}/api/v1/transactions`, { cache: 'no-store' });
    if (res.ok) {
      activity = await res.json();
    }
  } catch (error) {
    console.error("Failed to fetch transactions:", error);
  }

  // Format activity
  const formattedActivity = activity.map((item: ActivityItem) => {
    let title = item.type === "trade" ? `Trade ${item.merchant || "Asset"}` : item.type === "transfer_internal" ? "Transferencia" : "Transacción";
    if (item.classifier?.category) {
      title = `${item.classifier.merchant || item.merchant || "Movimiento"} (${item.classifier.category})`;
    }
    
    let detail = "";
    if (item.source_amount) {
      detail += `${item.source_currency} ${item.source_amount} `;
    }
    if (item.dest_amount) {
      if (detail) detail += "→ ";
      detail += `${item.dest_amount} ${item.dest_unit}`;
    }

    const date = new Date(item.occurred_at || "");
    const timeStr = isNaN(date.getTime()) ? item.occurred_at : date.toLocaleDateString('es-AR', {
      day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
    });
    
    let statusLabel = item.status;
    if (statusLabel === "completed") statusLabel = "Completado";
    else if (statusLabel === "pending") statusLabel = "Pendiente";
    else if (statusLabel === "failed") statusLabel = "Fallido";

    return {
      id: item.id,
      title: title,
      detail: detail,
      time: timeStr,
      status: statusLabel,
    };
  });

  return (
    <Sidebar>
      <div className="flex min-h-0 flex-1 flex-col">
        <div className="px-4 sm:px-6 lg:px-10">
          <PageHeader title="Actividad" description="Movimientos recientes y estado de planes">
            <SyncButton />
          </PageHeader>
        </div>
        <div className="flex-1 overflow-y-auto overscroll-contain bg-background px-4 py-6 sm:px-6 lg:px-10">
          <div className="mx-auto max-w-5xl rounded-3xl border border-line bg-card shadow-card">
            {formattedActivity.length === 0 && (
               <div className="p-8 text-center text-muted">No hay actividad reciente.</div>
            )}
            {formattedActivity.map((item: ActivityItem) => (
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
                        : item.status === "Fallido"
                        ? "bg-red-500/10 text-red-500 border-red-500/20"
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
    </Sidebar>
  );
}
