import { useState } from "react";

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
      className="shrink-0 border-t border-zinc-200 bg-white/95 px-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-3 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/95 sm:px-6 sm:py-4 lg:px-8"
    >
      <div className="flex items-end gap-2 sm:gap-3">
        <label className="sr-only" htmlFor="chat-message">
          Mensaje
        </label>
        <input
          id="chat-message"
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Escribí un mensaje..."
          className="min-h-12 flex-1 rounded-2xl border border-zinc-300 bg-white px-4 py-3 text-base leading-6 shadow-sm outline-none transition placeholder:text-zinc-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 sm:min-h-11 sm:rounded-full sm:px-5 sm:text-base lg:min-h-12"
        />
        <button
          type="submit"
          disabled={disabled || false}
          suppressHydrationWarning
          className="min-h-12 shrink-0 rounded-2xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 sm:min-h-11 sm:rounded-full sm:px-6 sm:text-base lg:min-h-12"
        >
          <span className="hidden min-[360px]:inline">Enviar</span>
          <span className="min-[360px]:hidden" aria-hidden="true">
            ↑
          </span>
        </button>
      </div>
    </form>
  );
}
