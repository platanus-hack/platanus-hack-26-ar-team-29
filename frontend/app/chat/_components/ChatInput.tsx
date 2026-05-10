import { useState, useRef } from "react";
import { Send, Paperclip, X, Image as ImageIcon, FileText } from "lucide-react";
import { Button } from "../../_components/Button";

export function ChatInput({
  onSend,
  disabled,
}: {
  onSend: (text: string, files?: File[]) => void;
  disabled?: boolean;
}) {
  const [text, setText] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFiles = Array.from(e.target.files);
      const validFiles = selectedFiles.filter(file => {
        if (file.type.startsWith('video/') || file.type.startsWith('audio/')) {
          alert(`El archivo "${file.name}" no está permitido. No se admiten videos ni audios.`);
          return false;
        }
        return true;
      });
      
      if (validFiles.length > 0) {
        setFiles((prev) => [...prev, ...validFiles]);
      }
    }
    // Reset input so the same file can be selected again if removed
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeFile = (indexToRemove: number) => {
    setFiles((prev) => prev.filter((_, index) => index !== indexToRemove));
  };

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const trimmed = text.trim();
        if (!trimmed && files.length === 0 || disabled) return;
        onSend(trimmed, files);
        setText("");
        setFiles([]);
      }}
      className="shrink-0 border-t border-line bg-background px-4 pb-[max(1rem,env(safe-area-inset-bottom))] pt-4 sm:px-8"
    >
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-3">
        {/* Attachments Preview Area */}
        {files.length > 0 && (
          <div className="flex flex-wrap gap-2 px-1">
            {files.map((file, index) => {
              const isImage = file.type.startsWith('image/');
              return (
                <div 
                  key={`file-${index}-${file.name}`} 
                  className="group relative flex items-center gap-2 rounded-xl border border-line bg-card py-1.5 pl-2.5 pr-2 shadow-sm"
                >
                  {isImage ? (
                    <ImageIcon size={14} className="text-accent shrink-0" />
                  ) : (
                    <FileText size={14} className="text-muted shrink-0" />
                  )}
                  <span className="max-w-[140px] truncate text-xs font-medium text-foreground">
                    {file.name || 'Archivo adjunto'}
                  </span>
                  <button
                    type="button"
                    onClick={() => removeFile(index)}
                    className="ml-1 flex shrink-0 items-center justify-center rounded-full p-1 text-muted transition-colors hover:bg-line hover:text-foreground"
                    title="Eliminar archivo"
                  >
                    <X size={12} />
                  </button>
                </div>
              );
            })}
          </div>
        )}

        <div className="flex items-end gap-2">
          <input
            type="file"
            multiple
            ref={fileInputRef}
            onChange={handleFileSelect}
            className="hidden"
          />
          
          <Button
            type="button"
            variant="ghost"
            size="icon"
            disabled={disabled || false}
            suppressHydrationWarning
            className="shrink-0 text-muted hover:text-foreground"
            onClick={() => fileInputRef.current?.click()}
            title="Adjuntar archivo"
          >
            <Paperclip className="h-5 w-5" />
          </Button>

          <div className="relative flex-1">
            <label className="sr-only" htmlFor="chat-message">
              Mensaje
            </label>
            <input
              id="chat-message"
              type="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Escribí un mensaje..."
              className="h-12 w-full rounded-full border border-input bg-background px-5 text-sm text-foreground placeholder:text-subdued outline-none transition-all duration-200 focus:border-accent focus:ring-4 focus:ring-accent/10"
            />
          </div>

          <Button
            type="submit"
            disabled={disabled || (!text.trim() && files.length === 0)}
            suppressHydrationWarning
            variant="primary"
            size="icon"
          >
            <Send className="h-5 w-5 ml-[-2px]" />
          </Button>
        </div>
      </div>
    </form>
  );
}
