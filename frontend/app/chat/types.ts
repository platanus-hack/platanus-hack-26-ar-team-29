import type { TradePlan } from "../lib/backend/types";

export type ChatRole = "user" | "assistant" | "system";

export interface ToolCall {
  id: string;
  name: string;
  inputSummary?: string;
  resultSummary?: string;
  isError?: boolean;
  status: 'started' | 'ok' | 'error';
}

export interface Message {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: number;
  kind?: "text" | "plan_proposal" | "stream" | "error";
  planId?: string | null;
  plan?: TradePlan;
  tools?: ToolCall[];
}
