import type { TradePlan } from "../lib/backend/types";

export type ChatRole = "user" | "assistant" | "system";

export interface Message {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: number;
  kind?: "text" | "plan_proposal" | "stream" | "error";
  planId?: string | null;
  plan?: TradePlan;
}
