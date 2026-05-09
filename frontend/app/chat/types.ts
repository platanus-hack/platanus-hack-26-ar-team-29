export type ChatRole = "user" | "bot";

export interface Message {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: number;
}

export interface SendMessageRequest {
  messages: Message[];
}

export interface SendMessageResponse {
  reply: Message;
}
