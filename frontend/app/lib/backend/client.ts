import type {
  ApiErrorEnvelope,
  BalanceRow,
  ChatMessageDto,
  ChatSession,
  PlanActionResponse,
  ProviderConnection,
  SendMessageResponse,
  TradePlan,
  TransactionRow,
} from "./types";

const DEFAULT_API_BASE_URL = "http://localhost:8000";

export class BackendApiError extends Error {
  code: string;
  status: number;
  traceId?: string;
  details?: unknown;

  constructor({
    code,
    message,
    status,
    traceId,
    details,
  }: {
    code: string;
    message: string;
    status: number;
    traceId?: string;
    details?: unknown;
  }) {
    super(message);
    this.name = "BackendApiError";
    this.code = code;
    this.status = status;
    this.traceId = traceId;
    this.details = details;
  }
}

export function getApiBaseUrl() {
  return (process.env.NEXT_PUBLIC_API_BASE_URL || DEFAULT_API_BASE_URL).replace(/\/$/, "");
}

export function getWsBaseUrl() {
  const explicit = process.env.NEXT_PUBLIC_WS_BASE_URL;
  if (explicit) return explicit.replace(/\/$/, "");

  const apiBase = getApiBaseUrl();
  if (apiBase.startsWith("https://")) return apiBase.replace(/^https:\/\//, "wss://");
  if (apiBase.startsWith("http://")) return apiBase.replace(/^http:\/\//, "ws://");
  return apiBase;
}

async function parseError(res: Response): Promise<BackendApiError> {
  let body: Partial<ApiErrorEnvelope> | null = null;
  try {
    body = (await res.json()) as ApiErrorEnvelope;
  } catch {
    body = null;
  }

  const err = body?.error;
  return new BackendApiError({
    code: err?.code || `HTTP_${res.status}`,
    message: err?.message_es || err?.message_en || `Backend request failed (${res.status})`,
    status: res.status,
    traceId: err?.trace_id,
    details: err?.details,
  });
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set("Accept", "application/json");
  headers.set("Accept-Language", "es-AR");
  if (init?.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");

  const res = await fetch(`${getApiBaseUrl()}/api/v1${path}`, {
    ...init,
    headers,
  });

  if (!res.ok) throw await parseError(res);
  return (await res.json()) as T;
}

export const backendApi = {
  health() {
    return requestJson<{ status: "ok" }>("/health");
  },

  listChatSessions() {
    return requestJson<ChatSession[]>("/chat/sessions");
  },

  createChatSession(body: { title?: string | null } = {}) {
    return requestJson<ChatSession>("/chat/sessions", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  deleteChatSession(sessionId: string) {
    return requestJson<void>(`/chat/sessions/${sessionId}`, {
      method: "DELETE",
    });
  },

  listChatMessages(sessionId: string) {
    return requestJson<ChatMessageDto[]>(`/chat/sessions/${sessionId}/messages`);
  },

  sendChatMessage(sessionId: string, content: string) {
    return requestJson<SendMessageResponse>(`/chat/sessions/${sessionId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    });
  },

  getPlan(planId: string) {
    return requestJson<TradePlan>(`/plans/${planId}`);
  },

  approvePlan(planId: string) {
    return requestJson<PlanActionResponse>(`/plans/${planId}/approve`, {
      method: "POST",
      body: JSON.stringify({ approved: true }),
    });
  },

  rejectPlan(planId: string, reason?: string) {
    return requestJson<PlanActionResponse>(`/plans/${planId}/reject`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    });
  },

  resolveChatInput(sessionId: string, inputId: string, selectedOptions: string[]) {
    return requestJson<{ ok: true; input_id: string }>(
      `/chat/sessions/${sessionId}/inputs/${inputId}/resolve`,
      {
        method: "POST",
        body: JSON.stringify({ selected_options: selectedOptions }),
      },
    );
  },

  connectWallbit(body: { label?: string | null; api_key: string }) {
    return requestJson<ProviderConnection>("/connections/wallbit", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  listConnections() {
    return requestJson<ProviderConnection[]>("/connections");
  },

  getBalances() {
    return requestJson<BalanceRow[]>("/balances");
  },

  getTransactions(limit = 50) {
    return requestJson<TransactionRow[]>(`/transactions?limit=${encodeURIComponent(limit)}`);
  },
};
