import { useState } from "react";
import { Send } from "lucide-react";

export function ChatInput({
  onSend,
  disabled,
}: {
  onSend: (text: string) => void;
  disabled?: boolean;
}) {
  const [text, setText] = useState("");

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const trimmed = text.trim();
        if (!trimmed || disabled) return;
        onSend(trimmed);
        setText("");
      }}
      className="shrink-0 border-t border-[#1A1A1A] bg-[#050505] px-4 pb-[max(1rem,env(safe-area-inset-bottom))] pt-4 sm:px-8"
    >
      <div className="flex items-end gap-3 max-w-4xl mx-auto w-full">
        <label className="sr-only" htmlFor="chat-message">
          Mensaje
        </label>
        <input
          id="chat-message"
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Escribí un mensaje..."
          className="h-12 flex-1 rounded-full border border-[#2A3F57] bg-[#050505] px-5 text-sm text-[#F4F8FB] placeholder:text-[#6B7788] outline-none transition-all duration-200 focus:border-[#38D9C6] focus:ring-4 focus:ring-[#38D9C6]/10"
        />
        <button
          type="submit"
          disabled={disabled || false}
          suppressHydrationWarning
          className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-[#38D9C6] text-[#050505] shadow-[0_0_28px_rgba(56,217,198,0.45)] transition-all duration-200 hover:bg-[#54E3D3] hover:shadow-[0_0_36px_rgba(56,217,198,0.65)] active:scale-95 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <Send className="h-5 w-5 ml-[-2px]" />
        </button>
      </div>
    </form>
  );
}
