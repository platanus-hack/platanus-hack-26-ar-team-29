import type { ReactNode } from "react";
import type { Message } from "../types";
import { PlanConfirmation } from "./PlanConfirmation";

type MarkdownBlock =
  | { type: "paragraph"; text: string }
  | { type: "unordered_list"; items: string[] }
  | { type: "ordered_list"; items: string[] };

function renderInlineMarkdown(text: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  const boldPattern = /\*\*(.+?)\*\*/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = boldPattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      nodes.push(text.slice(lastIndex, match.index));
    }
    nodes.push(
      <strong key={`${match.index}-${match[1]}`} className="font-semibold text-[#F4F8FB]">
        {match[1]}
      </strong>,
    );
    lastIndex = boldPattern.lastIndex;
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
      flushParagraph();
      flushUnorderedList();
      flushOrderedList();
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
            <ul key={index} className="m-0 list-disc space-y-1.5 pl-5 marker:text-[#38D9C6]">
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
            <ol key={index} className="m-0 list-decimal space-y-1.5 pl-5 marker:text-[#38D9C6]">
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
}: {
  message: Message;
  onApprovePlan?: (planId: string) => void;
  onRejectPlan?: (planId: string) => void;
  busyPlanId?: string | null;
}) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  if (message.plan) {
    return (
      <div className="flex justify-start">
        <div className="flex w-full flex-col gap-3 sm:max-w-[88%] lg:max-w-[78%]">
          {message.content && (
            <div className="rounded-2xl rounded-bl-sm border border-[#1A1A1A] bg-[#080C0D] px-5 py-3 text-sm break-words text-[#F4F8FB] shadow-sm">
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
            <div key={tool.id} className="flex items-center gap-2 rounded-xl bg-[#080C0D] border border-[#1A1A1A] px-3 py-2 text-xs text-[#A8B3C2]">
              {tool.status === 'started' ? (
                <span className="flex h-4 w-4 items-center justify-center">
                  <span className="h-3 w-3 animate-spin rounded-full border-2 border-[#38D9C6] border-t-transparent" />
                </span>
              ) : tool.status === 'error' ? (
                <span className="flex h-4 w-4 items-center justify-center text-red-400">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-4 h-4">
                    <path fillRule="evenodd" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14Zm2.78-4.22a.75.75 0 0 1-1.06 0L8 9.06l-1.72 1.72a.75.75 0 1 1-1.06-1.06L6.94 8 5.22 6.28a.75.75 0 0 1 1.06-1.06L8 6.94l1.72-1.72a.75.75 0 1 1 1.06 1.06L9.06 8l1.72 1.72a.75.75 0 0 1 0 1.06Z" clipRule="evenodd" />
                  </svg>
                </span>
              ) : (
                <span className="flex h-4 w-4 items-center justify-center text-[#38D9C6]">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-4 h-4">
                    <path fillRule="evenodd" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14Zm3.844-8.791a.75.75 0 0 0-1.188-.918l-3.7 4.79-1.649-1.833a.75.75 0 1 0-1.114 1.004l2.25 2.5a.75.75 0 0 0 1.15-.043l4.25-5.5Z" clipRule="evenodd" />
                  </svg>
                </span>
              )}
              <span className="font-mono">{tool.name}</span>
            </div>
          ))}
        </div>
      )}
      
      {hasContent && (
        <div
          className={`max-w-[96%] rounded-2xl px-5 py-3.5 text-sm break-words shadow-sm sm:max-w-[86%] md:max-w-[74%] lg:max-w-[68%] xl:max-w-[62%] ${
            isUser
              ? "whitespace-pre-wrap bg-[#38D9C6]/10 text-[#F4F8FB] border border-[#38D9C6]/30 rounded-br-sm shadow-[0_0_15px_rgba(56,217,198,0.08)]"
              : isSystem
                ? "bg-[#F5B84B]/10 text-[#F5B84B] border border-[#F5B84B]/20 rounded-bl-sm"
                : "bg-[#080C0D] text-[#F4F8FB] border border-[#1A1A1A] rounded-bl-sm"
          }`}
        >
          {isUser ? message.content : <RichMessageContent content={message.content} />}
        </div>
      )}
    </div>
  );
}
