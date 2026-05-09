"use client";

import { useState } from "react";
import { sendChatMessage } from "./api";
import { ChatInput } from "./_components/ChatInput";
import { ChatThread } from "./_components/ChatThread";
import type { Message, TradeStatus } from "./types";

function makeId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>(() => [
    {
      id: "seed",
      role: "bot",
      content: "Hi! I'm a mocked bot. Say something.",
      createdAt: 0,
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);

  async function handleSend(text: string) {
    const userMsg: Message = {
      id: makeId(),
      role: "user",
      content: text,
      createdAt: Date.now(),
    };
    const next = [...messages, userMsg];
    setMessages(next);
    setIsTyping(true);

    try {
      const { reply } = await sendChatMessage({ messages: next });
      setMessages((prev) => [...prev, reply]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          id: makeId(),
          role: "bot",
          content: "Sorry, something went wrong.",
          createdAt: Date.now(),
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  }

  function setTradeStatus(messageId: string, status: TradeStatus) {
    setMessages((prev) =>
      prev.map((m) =>
        m.id === messageId && m.trade
          ? { ...m, trade: { ...m.trade, status } }
          : m,
      ),
    );
  }

  return (
    <div className="mx-auto flex h-[100dvh] w-full max-w-2xl flex-col border-zinc-200 bg-white sm:border-x dark:border-zinc-800 dark:bg-zinc-950">
      <header className="border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
        <h1 className="text-lg font-semibold">Chat</h1>
      </header>
      <ChatThread
        messages={messages}
        isTyping={isTyping}
        onConfirmTrade={(id) => setTradeStatus(id, "confirmed")}
        onRejectTrade={(id) => setTradeStatus(id, "rejected")}
      />
      <ChatInput onSend={handleSend} disabled={isTyping} />
    </div>
  );
}
