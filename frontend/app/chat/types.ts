export type ChatRole = "user" | "bot";

export interface Message {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: number;
}
