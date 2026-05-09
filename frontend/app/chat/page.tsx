"use client";

import { useState } from "react";
import { ChatInput } from "./_components/ChatInput";
import { ChatThread } from "./_components/ChatThread";
import type { Message } from "./types";

const CANNED_REPLIES = [
  "Got it!",
  "Interesting — tell me more.",
  "Hmm, let me think about that.",
  "Thanks for sharing.",
  "Could you elaborate?",
  "Makes sense to me.",
  "Noted. What else?",
];

function makeId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function pickReply() {
  return CANNED_REPLIES[Math.floor(Math.random() * CANNED_REPLIES.length)];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>(() => [
    {
      id: makeId(),
      role: "bot",
      content: "Hi! I'm a mocked bot. Say something.",
      createdAt: Date.now(),
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);

  function handleSend(text: string) {
    const userMsg: Message = {
      id: makeId(),
      role: "user",
      content: text,
      createdAt: Date.now(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    setTimeout(() => {
      const botMsg: Message = {
        id: makeId(),
        role: "bot",
        content: pickReply(),
        createdAt: Date.now(),
      };
      setMessages((prev) => [...prev, botMsg]);
      setIsTyping(false);
    }, 800);
  }

  return (
    <div className="mx-auto flex h-[100dvh] w-full max-w-2xl flex-col border-zinc-200 bg-white sm:border-x dark:border-zinc-800 dark:bg-zinc-950">
      <header className="border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
        <h1 className="text-lg font-semibold">Chat</h1>
      </header>
      <ChatThread messages={messages} isTyping={isTyping} />
      <ChatInput onSend={handleSend} disabled={isTyping} />
    </div>
  );
}
