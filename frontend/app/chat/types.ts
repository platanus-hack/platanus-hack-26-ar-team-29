import type { TradePlan } from "../lib/backend/types";

export type ChatRole = "user" | "assistant" | "system";

export interface ToolCall {
  id: string;
  name: string;
  label?: string;
  inputSummary?: string;
  resultSummary?: string;
  isError?: boolean;
  status: 'started' | 'ok' | 'error';
}

export interface InputOption {
  id: string;
  label: string;
  description?: string;
}

export interface InputRequest {
  inputId: string;
  title: string;
  question: string;
  options: InputOption[];
  multiSelect: boolean;
  resolved?: boolean;
  selectedLabels?: string[];
}

export interface CredentialRequest {
  requestId: string;
  title: string;
  instructions: string;
  kind: string;
  placeholder?: string | null;
  resolved?: boolean;
  cancelled?: boolean;
}

export interface Attachment {
  name: string;
  type: string;
  url?: string;
}

export interface Message {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: number;
  kind?: "text" | "plan_proposal" | "stream" | "error" | "input_request" | "credential_request";
  planId?: string | null;
  plan?: TradePlan;
  tools?: ToolCall[];
  input?: InputRequest;
  credential?: CredentialRequest;
  attachments?: Attachment[];
}
