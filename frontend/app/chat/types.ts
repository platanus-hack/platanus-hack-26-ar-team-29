export type ChatRole = "user" | "bot";

export interface Message {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: number;
  trade?: {
    data: Trade;
    status: TradeStatus;
  };
}

export interface SendMessageRequest {
  messages: Message[];
}

export interface SendMessageResponse {
  reply: Message;
}

export interface Trade {
  id: string;
  fromTicker: string;
  fromAmount: number;
  toTicker: string;
  toAmount: number;
  valueUSD: number;
}

export type TradeStatus = "pending" | "confirmed" | "rejected";
