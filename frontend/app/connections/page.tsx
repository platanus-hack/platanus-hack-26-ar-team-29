import { Sidebar } from "../_components/Sidebar";
import { PageHeader } from "../_components/PageHeader";
import { ConnectionsClient } from "./ConnectionsClient";

export const dynamic = "force-dynamic";

export default async function ConnectionsPage() {
  const url = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
  let connections = [];
  try {
    const res = await fetch(`${url}/api/v1/connections`, { cache: 'no-store' });
    if (res.ok) {
      connections = await res.json();
    }
  } catch (error) {
    console.error("Failed to fetch connections:", error);
  }

  return (
    <Sidebar>
      <div className="flex min-h-0 flex-1 flex-col">
        <PageHeader
          title="Conexiones"
          description="Gestioná tus cuentas y wallets vinculadas"
        />
        <div className="flex-1 overflow-y-auto overscroll-contain bg-background px-4 py-6 sm:px-6 lg:px-10">
          <ConnectionsClient initialConnections={connections} url={url} />
        </div>
      </div>
    </Sidebar>
  );
}
