import { useEffect, useRef } from 'react';
import type { Message } from '../types';
import { ChatMessage } from './ChatMessage';

export function ChatThread({
    messages,
    isTyping,
    onApprovePlan,
    onRejectPlan,
    busyPlanId,
    onResolveInput,
    busyInputId,
}: {
    messages: Message[];
    isTyping: boolean;
    onApprovePlan?: (planId: string) => void;
    onRejectPlan?: (planId: string) => void;
    busyPlanId?: string | null;
    onResolveInput?: (inputId: string, selectedIds: string[]) => void;
    busyInputId?: string | null;
}) {
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const el = ref.current;
        if (!el) return;
        el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
    }, [messages, isTyping]);

    return (
        <div
            ref={ref}
            className='min-h-0 flex-1 overflow-y-auto overscroll-contain'
        >
            <div className='space-y-5 px-4 py-5 sm:px-6 sm:py-7 lg:px-12 max-w-4xl mx-auto'>
                {messages.length === 0 && !isTyping && (
                    <div className='mx-auto flex min-h-full flex-col items-center justify-center px-4 py-10 text-center'>
                        <div className='rounded-3xl border border-accent/15 bg-card px-10 py-7 text-center shadow-panel-glow max-w-[420px]'>
                            <h2 className='mb-3 text-xl font-semibold text-foreground'>
                                Terminal lista
                            </h2>
                            <p className='max-w-[340px] mx-auto text-sm leading-6 text-muted'>
                                Tu billetera está conectada. Pedime un análisis
                                de riesgo, mover liquidez a una bóveda o buscar
                                yield pasivo.
                            </p>
                        </div>
                    </div>
                )}
                {messages.map((m) => (
                    <ChatMessage
                        key={m.id}
                        message={m}
                        onApprovePlan={onApprovePlan}
                        onRejectPlan={onRejectPlan}
                        busyPlanId={busyPlanId}
                        onResolveInput={onResolveInput}
                        busyInputId={busyInputId}
                    />
                ))}
                {isTyping && (
                    <div className='flex justify-start'>
                        <div className='rounded-2xl rounded-bl-sm bg-surface px-4 py-3 text-sm text-accent shadow-sm border border-line'>
                            <span className='inline-flex gap-1'>
                                <span className='h-1.5 w-1.5 animate-bounce rounded-full bg-current' />
                                <span className='h-1.5 w-1.5 animate-bounce rounded-full bg-current [animation-delay:150ms]' />
                                <span className='h-1.5 w-1.5 animate-bounce rounded-full bg-current [animation-delay:300ms]' />
                            </span>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
