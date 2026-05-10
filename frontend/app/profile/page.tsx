'use client';

import { useEffect, useState } from "react";
import { Sidebar } from "../_components/Sidebar";
import { PageHeader } from "../_components/PageHeader";
import { backendApi } from "../lib/backend/client";
import type { UserProfile } from "../lib/backend/types";
import { Activity, ShieldAlert, PieChart, RefreshCw } from "lucide-react";

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const fetchProfile = () => {
    setLoading(true);
    backendApi.getProfile()
      .then((data) => {
        if (Object.keys(data).length > 0) setProfile(data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const newProfile = await backendApi.generateProfile();
      setProfile(newProfile);
    } catch (e) {
      console.error(e);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <Sidebar>
      <div className="flex min-h-0 flex-1 flex-col">
        <PageHeader
          title="Perfil de Atajo"
          description="Análisis automático de tus tendencias financieras y de riesgo."
        />
        <div className="flex-1 overflow-y-auto overscroll-contain bg-background px-4 py-6 sm:px-6 lg:px-10">
          <div className="mx-auto max-w-4xl space-y-6">
            
            <div className="flex justify-end">
              <button
                onClick={handleGenerate}
                disabled={generating}
                className="flex items-center gap-2 rounded-xl bg-accent text-accent-foreground px-4 py-2 text-sm font-medium transition-all hover:bg-accent/90 disabled:opacity-50"
              >
                <RefreshCw size={16} className={generating ? "animate-spin" : ""} />
                {generating ? "Generando..." : profile ? "Regenerar Perfil" : "Generar Perfil"}
              </button>
            </div>

            {loading ? (
              <div className="text-center text-muted py-10">Cargando perfil...</div>
            ) : !profile ? (
              <div className="text-center text-muted py-20 border border-dashed border-line rounded-3xl">
                Aún no tienes un perfil generado. Presiona el botón de arriba para analizar tus datos.
              </div>
            ) : (
              <div className="grid gap-6 sm:grid-cols-2">
                {/* Riesgo */}
                <div className="rounded-3xl border border-line bg-card p-6 shadow-card">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-accent/10 text-accent rounded-lg"><ShieldAlert size={20} /></div>
                    <h3 className="font-semibold text-lg">Perfil de Riesgo</h3>
                  </div>
                  <div className="text-3xl font-bold capitalize mb-2">{profile.risk_profile?.level || "N/A"}</div>
                  <div className="text-sm text-muted mb-4">Score: {profile.risk_profile?.score_1_to_10 || 0}/10</div>
                  <p className="text-sm text-subdued leading-relaxed">{profile.risk_profile?.reasoning}</p>
                </div>

                {/* Métricas de Portfolio */}
                <div className="rounded-3xl border border-line bg-card p-6 shadow-card">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-accent/10 text-accent rounded-lg"><PieChart size={20} /></div>
                    <h3 className="font-semibold text-lg">Métricas de Portfolio</h3>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <div className="text-xs font-mono text-muted mb-1">Net Worth Estimado</div>
                      <div className="text-2xl font-semibold">${profile.portfolio_metrics?.estimated_net_worth_usd?.toLocaleString("es-AR") || "0"} USD</div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-xs font-mono text-muted mb-1">Fiat (Liquidez)</div>
                        <div className="text-lg font-medium">{profile.portfolio_metrics?.fiat_percentage?.toFixed(1) || "0"}%</div>
                      </div>
                      <div>
                        <div className="text-xs font-mono text-muted mb-1">Inversiones</div>
                        <div className="text-lg font-medium">{profile.portfolio_metrics?.investments_percentage?.toFixed(1) || "0"}%</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Comportamiento */}
                <div className="rounded-3xl border border-line bg-card p-6 shadow-card sm:col-span-2">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-accent/10 text-accent rounded-lg"><Activity size={20} /></div>
                    <h3 className="font-semibold text-lg">Análisis de Comportamiento</h3>
                  </div>
                  <div className="grid gap-6 sm:grid-cols-2">
                    <div>
                      <h4 className="text-sm font-medium mb-2">Gastos y Ahorro</h4>
                      <p className="text-sm text-subdued leading-relaxed">{profile.summaries?.spending_behavior}</p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium mb-2">Estilo de Inversión</h4>
                      <p className="text-sm text-subdued leading-relaxed">{profile.summaries?.investment_style}</p>
                    </div>
                  </div>
                  
                  {profile.last_recomputed_at && (
                    <div className="mt-6 pt-4 border-t border-line text-xs text-muted text-right">
                      Última actualización: {new Date(profile.last_recomputed_at).toLocaleString('es-AR')}
                    </div>
                  )}
                </div>

              </div>
            )}
          </div>
        </div>
      </div>
    </Sidebar>
  );
}
