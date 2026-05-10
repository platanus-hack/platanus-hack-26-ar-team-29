import { FileText, Image as ImageIcon, Copy, Check } from "lucide-react";
import { useState } from "react";
import type { ReactNode } from "react";
import type { Message } from "../types";
import { InputQuestion } from "./InputQuestion";
import { PlanConfirmation } from "./PlanConfirmation";

function CopyableCode({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <span className="inline-flex items-center gap-1.5 rounded-md bg-background px-2 py-0.5 border border-line text-accent font-mono text-[11px] shadow-sm">
      <span className="truncate max-w-[200px] sm:max-w-xs">{text}</span>
      <button onClick={handleCopy} className="text-muted hover:text-foreground transition-colors ml-1 p-0.5 rounded-sm hover:bg-surface active:scale-95" title="Copiar">
        {copied ? <Check size={12} className="text-success" /> : <Copy size={12} />}
      </button>
    </span>
  );
}

type MarkdownBlock =
  | { type: "paragraph"; text: string }
  | { type: "unordered_list"; items: string[] }
  | { type: "ordered_list"; items: string[] };

function renderInlineMarkdown(text: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  const tokenPattern = /(\*\*.+?\*\*|```.+?```|`.+?`)/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = tokenPattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      nodes.push(text.slice(lastIndex, match.index));
    }
    const token = match[1];
    if (token.startsWith('**') && token.endsWith('**')) {
      nodes.push(<strong key={`${match.index}-bold`} className="font-semibold text-foreground">{token.slice(2, -2)}</strong>);
    } else if (token.startsWith('```') && token.endsWith('```')) {
      const code = token.slice(3, -3).trim();
      nodes.push(<CopyableCode key={`${match.index}-code3`} text={code} />);
    } else if (token.startsWith('`') && token.endsWith('`')) {
      const code = token.slice(1, -1);
      nodes.push(<CopyableCode key={`${match.index}-code1`} text={code} />);
    }
    lastIndex = tokenPattern.lastIndex;
  }

  if (lastIndex < text.length) {
    nodes.push(text.slice(lastIndex));
  }

  return nodes.length ? nodes : [text];
}

function parseMarkdownBlocks(content: string): MarkdownBlock[] {
  const blocks: MarkdownBlock[] = [];
  let paragraph: string[] = [];
  let unorderedItems: string[] = [];
  let orderedItems: string[] = [];

  function flushParagraph() {
    if (!paragraph.length) return;
    blocks.push({ type: "paragraph", text: paragraph.join(" ") });
    paragraph = [];
  }

  function flushUnorderedList() {
    if (!unorderedItems.length) return;
    blocks.push({ type: "unordered_list", items: unorderedItems });
    unorderedItems = [];
  }

  function flushOrderedList() {
    if (!orderedItems.length) return;
    blocks.push({ type: "ordered_list", items: orderedItems });
    orderedItems = [];
  }

  for (const rawLine of content.trim().split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line) {
      // Blank line ends a paragraph but not a list — LLMs frequently emit
      // blank lines between list items (and reset numbering to "1." each
      // time), so we keep adjacent list items in a single block so the
      // browser auto-numbers them sequentially.
      flushParagraph();
      continue;
    }

    const unorderedMatch = line.match(/^[-*]\s+(.+)$/);
    if (unorderedMatch) {
      flushParagraph();
      flushOrderedList();
      unorderedItems.push(unorderedMatch[1]);
      continue;
    }

    const orderedMatch = line.match(/^\d+[.)]\s+(.+)$/);
    if (orderedMatch) {
      flushParagraph();
      flushUnorderedList();
      orderedItems.push(orderedMatch[1]);
      continue;
    }

    flushUnorderedList();
    flushOrderedList();
    paragraph.push(line);
  }

  flushParagraph();
  flushUnorderedList();
  flushOrderedList();

  return blocks;
}

function RichMessageContent({ content }: { content: string }) {
  const blocks = parseMarkdownBlocks(content);

  return (
    <div className="space-y-3 leading-6">
      {blocks.map((block, index) => {
        if (block.type === "unordered_list") {
          return (
            <ul key={index} className="m-0 list-disc space-y-1.5 pl-5 marker:text-accent">
              {block.items.map((item, itemIndex) => (
                <li key={itemIndex} className="pl-1">
                  {renderInlineMarkdown(item)}
                </li>
              ))}
            </ul>
          );
        }

        if (block.type === "ordered_list") {
          return (
            <ol key={index} className="m-0 list-decimal space-y-1.5 pl-5 marker:text-accent">
              {block.items.map((item, itemIndex) => (
                <li key={itemIndex} className="pl-1">
                  {renderInlineMarkdown(item)}
                </li>
              ))}
            </ol>
          );
        }

        return (
          <p key={index} className="m-0">
            {renderInlineMarkdown(block.text)}
          </p>
        );
      })}
    </div>
  );
}

export function ChatMessage({
  message,
  onApprovePlan,
  onRejectPlan,
  busyPlanId,
  onResolveInput,
  busyInputId,
}: {
  message: Message;
  onApprovePlan?: (planId: string) => void;
  onRejectPlan?: (planId: string) => void;
  busyPlanId?: string | null;
  onResolveInput?: (inputId: string, selectedIds: string[]) => void;
  busyInputId?: string | null;
}) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  if (message.input && onResolveInput) {
    return (
      <div className="flex justify-start">
        <div className="flex w-full flex-col gap-3 sm:max-w-[88%] lg:max-w-[78%]">
          <InputQuestion
            input={message.input}
            isBusy={busyInputId === message.input.inputId}
            onResolve={onResolveInput}
          />
        </div>
      </div>
    );
  }

  if (message.plan) {
    return (
      <div className="flex justify-start">
        <div className="flex w-full flex-col gap-3 sm:max-w-[88%] lg:max-w-[78%]">
          {message.content && (
            <div className="rounded-2xl rounded-bl-sm border border-line bg-card px-5 py-3 text-sm break-words text-foreground shadow-sm">
              <RichMessageContent content={message.content} />
            </div>
          )}
          <PlanConfirmation
            plan={message.plan}
            isBusy={busyPlanId === message.plan.id}
            onApprove={() => onApprovePlan?.(message.plan!.id)}
            onReject={() => onRejectPlan?.(message.plan!.id)}
          />
        </div>
      </div>
    );
  }

  const hasTools = message.tools && message.tools.length > 0;
  const hasContent = message.content && message.content.length > 0;

  return (
    <div className={`flex flex-col gap-2 ${isUser ? "items-end" : "items-start"}`}>
      {hasTools && !isUser && (
        <div className="flex flex-col gap-1.5 w-full sm:max-w-[86%] md:max-w-[74%] lg:max-w-[68%] xl:max-w-[62%]">
          {message.tools!.map(tool => (
            <div key={tool.id} className="flex items-center gap-2 rounded-xl bg-card border border-line px-3 py-2 text-xs text-muted">
              {tool.status === 'started' ? (
                <span className="flex h-4 w-4 items-center justify-center">
                  <span className="h-3 w-3 animate-spin rounded-full border-2 border-accent border-t-transparent" />
                </span>
              ) : tool.status === 'error' ? (
                <span className="flex h-4 w-4 items-center justify-center text-red-400">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-4 h-4">
                    <path fillRule="evenodd" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14Zm2.78-4.22a.75.75 0 0 1-1.06 0L8 9.06l-1.72 1.72a.75.75 0 1 1-1.06-1.06L6.94 8 5.22 6.28a.75.75 0 0 1 1.06-1.06L8 6.94l1.72-1.72a.75.75 0 1 1 1.06 1.06L9.06 8l1.72 1.72a.75.75 0 0 1 0 1.06Z" clipRule="evenodd" />
                  </svg>
                </span>
              ) : (
                <span className="flex h-4 w-4 items-center justify-center text-accent">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-4 h-4">
                    <path fillRule="evenodd" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14Zm3.844-8.791a.75.75 0 0 0-1.188-.918l-3.7 4.79-1.649-1.833a.75.75 0 1 0-1.114 1.004l2.25 2.5a.75.75 0 0 0 1.15-.043l4.25-5.5Z" clipRule="evenodd" />
                  </svg>
                </span>
              )}
              <span className="font-mono">{tool.label || tool.name}</span>
            </div>
          ))}
        </div>
      )}
      
      {message.attachments && message.attachments.length > 0 && (
        <div className={`flex flex-wrap gap-2 max-w-[96%] sm:max-w-[86%] md:max-w-[74%] lg:max-w-[68%] xl:max-w-[62%] ${isUser ? "justify-end" : "justify-start"}`}>
          {message.attachments.map((file, index) => {
            const isImage = file.type.startsWith('image/');
            return (
              <div 
                key={`${file.name}-${index}`} 
                className={`flex items-center gap-2 rounded-xl border py-1.5 px-3 shadow-sm ${
                  isUser 
                    ? "bg-accent/5 border-accent/20" 
                    : "bg-card border-line"
                }`}
              >
                {isImage && file.url ? (
                  <div className="relative h-12 w-12 shrink-0 overflow-hidden rounded-md border border-line">
                    <img src={file.url} alt={file.name} className="h-full w-full object-cover" />
                  </div>
                ) : (
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-surface text-muted">
                    <FileText size={18} />
                  </div>
                )}
                <div className="flex flex-col min-w-0 pr-1">
                  <span className="max-w-[140px] truncate text-xs font-medium text-foreground">
                    {file.name}
                  </span>
                  <span className="text-[10px] text-muted uppercase">
                    {isImage ? "IMAGEN" : "ARCHIVO"}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {hasContent && (
        <div
          className={`max-w-[96%] rounded-2xl px-5 py-3.5 text-sm break-words shadow-sm sm:max-w-[86%] md:max-w-[74%] lg:max-w-[68%] xl:max-w-[62%] ${
            isUser
              ? "whitespace-pre-wrap bg-accent/10 text-foreground border border-accent/30 rounded-br-sm shadow-glow-xs"
              : isSystem
                ? "bg-warning/10 text-warning border border-warning/20 rounded-bl-sm"
                : "bg-card text-foreground border border-line rounded-bl-sm"
          }`}
        >
          {isUser ? message.content : <RichMessageContent content={message.content} />}
        </div>
      )}
    </div>
  );
}
