export interface ApiErrorEnvelope {
  error: {
    code: string;
    message_es: string;
    message_en?: string | null;
    params?: Record<string, unknown>;
    details?: unknown;
    trace_id?: string;
  };
}

export interface ChatSession {
  id: string;
  title?: string | null;
  created_at?: string;
  updated_at?: string;
  last_message_preview?: string | null;
}

export type BackendMessageRole = "user" | "assistant" | "system";
export type BackendMessageKind = "text" | "plan_proposal" | string;

export interface ChatMessageDto {
  id: string;
  role: BackendMessageRole;
  content: string;
  kind?: BackendMessageKind;
  plan_id?: string | null;
  created_at: string;
  attachments?: {
    name: string;
    type: string;
    url?: string;
  }[];
}

export interface SendMessageResponse {
  message_id: string;
  accepted: true;
  turn_id: string;
}

export type PlanState =
  | "draft"
  | "pending_approval"
  | "approved"
  | "executing"
  | "completed"
  | "partially_failed"
  | "rejected"
  | "expired"
  | string;

export type PlanStepState = "pending" | "executing" | "ok" | "failed" | string;

export interface TradePlanStep {
  id: string;
  ordinal: number;
  tool_name: string;
  args: Record<string, unknown>;
  human_description_es?: string | null;
  human_description_en?: string | null;
  category?: string | null;
  estimated_usd?: number | null;
  state: PlanStepState;
  result_summary?: string | null;
}

export interface TradePlan {
  id: string;
  state: PlanState;
  total_estimated_usd?: number | null;
  estimated_unit_price_usd?: number | null;
  expires_at?: string;
  created_at?: string;
  steps: TradePlanStep[];
}

export interface PlanActionResponse {
  ok: true;
  plan_state: PlanState;
  plan_id: string;
}

export interface ProviderConnection {
  id: string;
  connection_type: string;
  label?: string | null;
  status: string;
  capabilities: string[];
  created_at: string;
}

export interface BalanceRow {
  provider?: string;
  connection_type?: string;
  account_type?: string;
  currency?: string;
  symbol?: string;
  asset_type?: string;
  amount?: number;
  quantity?: number;
  value_usd?: number | null;
  [key: string]: unknown;
}

export interface TransactionRow {
  id?: string;
  provider?: string;
  connection_type?: string;
  type?: string;
  status?: string;
  amount?: number;
  currency?: string;
  symbol?: string;
  created_at?: string;
  [key: string]: unknown;
}

export type BackendWsFrame =
  | { type: "subscribed"; session_id: string }
  | { type: "chat_token"; session_id: string; turn_id: string; delta: string }
  | { type: "tool_call_started"; session_id: string; turn_id: string; tool_use_id: string; tool_name: string; input_summary: string }
  | { type: "tool_call_finished"; session_id: string; turn_id: string; tool_use_id: string; is_error: boolean; result_summary: string }
  | { type: "chat_message"; session_id: string; turn_id: string; message: ChatMessageDto }
  | { type: "plan_proposed"; session_id: string; plan_id: string; plan: TradePlan }
  | {
      type: "plan_update";
      session_id: string;
      plan_id: string;
      step_id?: string | null;
      state: PlanState | PlanStepState;
      reason?: string | null;
      error?: string | null;
      summary?: string | null;
      ts: string;
    }
  | { type: "turn_complete"; session_id: string; turn_id: string }
  | {
      type: "input_requested";
      session_id: string;
      turn_id: string;
      input_id: string;
      title: string;
      question: string;
      options: { id: string; label: string; description?: string }[];
      multi_select: boolean;
    }
  | {
      type: "input_resolved";
      session_id: string;
      turn_id: string;
      input_id: string;
      selected_options: string[];
    }
  | { type: "error"; code: string; message_es: string; message_en?: string | null }
  | { type: "chat_title_updated"; session_id: string; title: string }
  | { type: "ping" }
  | { type: "pong" };
