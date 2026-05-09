import { useState } from "react";
import { Send } from "lucide-react";
import { Button } from "../../_components/Button";

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
      className="shrink-0 border-t border-line bg-background px-4 pb-[max(1rem,env(safe-area-inset-bottom))] pt-4 sm:px-8"
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
          className="h-12 flex-1 rounded-full border border-input bg-background px-5 text-sm text-foreground placeholder:text-subdued outline-none transition-all duration-200 focus:border-accent focus:ring-4 focus:ring-accent/10"
        />
        <Button
          type="submit"
          disabled={disabled || false}
          suppressHydrationWarning
          variant="primary"
          size="icon"
        >
          <Send className="h-5 w-5 ml-[-2px]" />
        </Button>
      </div>
    </form>
  );
}
