'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { Sidebar } from './_components/Sidebar';
import { ChatInput } from './chat/_components/ChatInput';
import { ChatThread } from './chat/_components/ChatThread';
import type { Message } from './chat/types';
import { BackendApiError, backendApi } from './lib/backend/client';
import type {
    BackendWsFrame,
    ChatMessageDto,
    TradePlan,
} from './lib/backend/types';
import {
    openSessionWebSocket,
    type BackendWsSubscription,
} from './lib/backend/ws';
import { useChat } from './contexts/ChatContext';

function makeId() {
    return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function dtoToMessage(dto: ChatMessageDto, plan?: TradePlan): Message {
    return {
        id: dto.id,
        role: dto.role,
        content: dto.content,
        createdAt: Date.parse(dto.created_at) || Date.now(),
        kind: dto.kind === 'plan_proposal' ? 'plan_proposal' : 'text',
        planId: dto.plan_id,
        plan,
        attachments: dto.attachments,
    };
}

function errorText(err: unknown) {
    if (err instanceof BackendApiError) return err.message;
    if (err instanceof Error) return err.message;
    return 'Ocurrió un error inesperado.';
}

function sortMessages(messages: Message[]) {
    return [...messages].sort((a, b) => a.createdAt - b.createdAt);
}

export default function ChatPage() {
    const wsRef = useRef<BackendWsSubscription | null>(null);
    const planTurnIdsRef = useRef<Set<string>>(new Set());
    const { currentSessionId, updateSessionTitle } = useChat();
    const [messages, setMessages] = useState<Message[]>([]);
    const [isBooting, setIsBooting] = useState(true);
    const [isTyping, setIsTyping] = useState(false);
    const [busyPlanId, setBusyPlanId] = useState<string | null>(null);
    const [busyInputId, setBusyInputId] = useState<string | null>(null);
    const [busyCredentialId, setBusyCredentialId] = useState<string | null>(null);
    const [, setError] = useState<string | null>(null);

    const upsertMessage = useCallback((message: Message) => {
        setMessages((prev) => {
            const withoutSame = prev.filter((m) => m.id !== message.id);
            return sortMessages([...withoutSame, message]);
        });
    }, []);

    const updatePlan = useCallback(
        (planId: string, updater: (plan: TradePlan) => TradePlan) => {
            setMessages((prev) => {
                const next = prev.map((message) => {
                    if (message.plan?.id !== planId) return message;
                    const newPlan = updater(message.plan);
                    const wasPending = message.plan.state === 'pending_approval';
                    const isPending = newPlan.state === 'pending_approval';
                    // Pending plans pin to the bottom (Date.now() + 1e9).
                    // Once resolved, drop the pin so subsequent responses sort after.
                    // Re-pin if the plan flips back to pending (e.g., error rollback).
                    let createdAt = message.createdAt;
                    if (isPending && !wasPending) createdAt = Date.now() + 1e9;
                    else if (!isPending && wasPending) createdAt = Date.now();
                    return { ...message, plan: newPlan, createdAt };
                });
                return sortMessages(next);
            });
        },
        [],
    );

    const appendSystemMessage = useCallback(
        (content: string) => {
            upsertMessage({
                id: makeId(),
                role: 'system',
                content,
                createdAt: Date.now(),
                kind: 'error',
            });
        },
        [upsertMessage],
    );

    const isRedundantApprovalMessage = useCallback((content: string) => {
        const normalized = content.toLowerCase();
        return [
            'para que confirmes',
            'para que apruebes',
            'ventana de confirmación',
            'ventana de confirmacion',
            'orden está lista',
            'orden esta lista',
            'esperando tu aprobación',
            'esperando aprobación',
            'esperando tu aprobacion',
            'esperando aprobacion',
            'panel',
            'aprobar o rechazar',
            'aprobar/rechazar',
            'confirmación para que',
            'confirmacion para que',
            'botón',
            'botones',
            'revisar transacción',
            'revisar transaccion',
        ].some((phrase) => normalized.includes(phrase));
    }, []);

    const handleWsFrame = useCallback(
        (frame: BackendWsFrame) => {
            if (frame.type === 'subscribed') {
                return;
            }

            if (frame.type === 'chat_title_updated') {
                updateSessionTitle(frame.session_id, frame.title);
                return;
            }

            if (frame.type === 'ping') {
                wsRef.current?.sendPing();
                return;
            }

            if (frame.type === 'chat_token') {
                setIsTyping(true);
                setMessages((prev) => {
                    const streamId = `stream-${frame.turn_id}`;
                    const existing = prev.find((m) => m.id === streamId);
                    const nextMessage: Message = existing
                        ? {
                              ...existing,
                              content: existing.content + frame.delta,
                          }
                        : {
                              id: streamId,
                              role: 'assistant',
                              content: frame.delta,
                              createdAt: Date.now(),
                              kind: 'stream',
                          };
                    return sortMessages([
                        ...prev.filter((m) => m.id !== streamId),
                        nextMessage,
                    ]);
                });
                return;
            }

            if (frame.type === 'tool_call_started') {
                setIsTyping(true);
                setMessages((prev) => {
                    const isVisual = frame.tool_name === 'mcp__wallbit__show_table' || frame.tool_name === 'show_table';
                    const toolsId = isVisual ? `visual-${frame.turn_id}-${frame.tool_use_id}` : `tools-${frame.turn_id}`;
                    const existing = prev.find((m) => m.id === toolsId);
                    const newTool = {
                        id: frame.tool_use_id,
                        name: frame.tool_name,
                        label: frame.tool_label,
                        inputSummary: frame.input_summary,
                        status: 'started' as const,
                    };
                    const nextMessage: Message = existing
                        ? {
                              ...existing,
                              tools: [...(existing.tools || []), newTool],
                          }
                        : {
                              id: toolsId,
                              role: 'assistant',
                              content: '',
                              createdAt: Date.now(),
                              kind: 'text',
                              tools: [newTool],
                          };
                    return sortMessages([
                        ...prev.filter((m) => m.id !== toolsId),
                        nextMessage,
                    ]);
                });
                return;
            }

            if (frame.type === 'tool_call_finished') {
                setMessages((prev) => {
                    const existing = prev.find((m) => m.tools?.some(t => t.id === frame.tool_use_id));
                    if (!existing || !existing.tools) return prev;
                    const toolsId = existing.id;

                    const nextMessage: Message = {
                        ...existing,
                        tools: existing.tools.map(t =>
                            t.id === frame.tool_use_id
                                ? { ...t, status: frame.is_error ? 'error' : 'ok', resultSummary: frame.result_summary }
                                : t
                        ),
                    };
                    return sortMessages([
                        ...prev.filter((m) => m.id !== toolsId),
                        nextMessage,
                    ]);
                });
                return;
            }

            if (frame.type === 'chat_message') {
                if (
                    planTurnIdsRef.current.has(frame.turn_id) &&
                    isRedundantApprovalMessage(frame.message.content || '')
                ) {
                    return;
                }
                setMessages((prev) => {
                    const streamId = `stream-${frame.turn_id}`;
                    const withoutStream = prev.filter((m) => m.id !== streamId);
                    const finalMessage = dtoToMessage(frame.message);
                    return sortMessages([
                        ...withoutStream.filter((m) => m.id !== frame.message.id),
                        finalMessage,
                    ]);
                });
                return;
            }

            if (frame.type === 'plan_proposed') {
                planTurnIdsRef.current.add(frame.turn_id);
                // Plan cards are the actionable item — pin them after any
                // current or future end-of-turn agent message in this session.
                upsertMessage({
                    id: `plan-${frame.plan_id}`,
                    role: 'assistant',
                    content: '',
                    createdAt: Date.now() + 1e9,
                    kind: 'plan_proposal',
                    planId: frame.plan_id,
                    plan: frame.plan,
                });
                return;
            }

            if (frame.type === 'plan_update') {
                updatePlan(frame.plan_id, (plan) => ({
                    ...plan,
                    state: frame.step_id ? plan.state : frame.state,
                    steps: frame.step_id
                        ? plan.steps.map((step) =>
                              step.id === frame.step_id
                                  ? {
                                        ...step,
                                        state: frame.state,
                                        result_summary:
                                            frame.summary ||
                                            frame.error ||
                                            step.result_summary,
                                    }
                                  : step,
                          )
                        : plan.steps,
                }));
                return;
            }

            if (frame.type === 'input_requested') {
                setIsTyping(false);
                upsertMessage({
                    id: `input-${frame.input_id}`,
                    role: 'assistant',
                    content: '',
                    createdAt: Date.now(),
                    kind: 'input_request',
                    input: {
                        inputId: frame.input_id,
                        title: frame.title,
                        question: frame.question,
                        options: frame.options,
                        multiSelect: frame.multi_select,
                    },
                });
                return;
            }

            if (frame.type === 'input_resolved') {
                setMessages((prev) =>
                    prev.map((m) =>
                        m.input?.inputId === frame.input_id
                            ? {
                                  ...m,
                                  input: {
                                      ...m.input,
                                      resolved: true,
                                      selectedLabels: Array.isArray(frame.selected_options) ? frame.selected_options : [frame.selected_options],
                                  },
                              }
                            : m,
                    ),
                );
                return;
            }

            if (frame.type === 'credential_requested') {
                setIsTyping(false);
                upsertMessage({
                    id: `credential-${frame.request_id}`,
                    role: 'assistant',
                    content: '',
                    createdAt: Date.now(),
                    kind: 'credential_request',
                    credential: {
                        requestId: frame.request_id,
                        title: frame.title,
                        instructions: frame.instructions,
                        kind: frame.kind,
                        placeholder: frame.placeholder,
                    },
                });
                return;
            }

            if (frame.type === 'credential_resolved') {
                setMessages((prev) =>
                    prev.map((m) =>
                        m.credential?.requestId === frame.request_id
                            ? {
                                  ...m,
                                  credential: {
                                      ...m.credential,
                                      resolved: true,
                                      cancelled: frame.cancelled,
                                  },
                              }
                            : m,
                    ),
                );
                return;
            }

            if (frame.type === 'turn_complete') {
                setIsTyping(false);
                setMessages((prev) =>
                    prev.flatMap((m) => {
                        if (m.id.startsWith('stream-')) {
                            if (
                                m.id === `stream-${frame.turn_id}` &&
                                planTurnIdsRef.current.has(frame.turn_id) &&
                                isRedundantApprovalMessage(m.content)
                            ) {
                                return [];
                            }
                            return { ...m, id: `streamed-${m.id}`, kind: 'text' };
                        }
                        return m;
                    })
                );
                return;
            }

            if (frame.type === 'error') {
                setIsTyping(false);
                appendSystemMessage(
                    frame.message_es || frame.message_en || frame.code,
                );
            }
        },
        [appendSystemMessage, isRedundantApprovalMessage, updatePlan, upsertMessage, updateSessionTitle],
    );

    useEffect(() => {
        let cancelled = false;

        async function boot() {
            if (!currentSessionId) {
                setMessages([]);
                setIsBooting(false);
                return;
            }

            setIsBooting(true);
            setError(null);
            
            try {
                const rawMessages = await backendApi.listChatMessages(currentSessionId);
                const hydrated = await Promise.all(
                    rawMessages.map(async (message) => {
                        if (
                            message.kind === 'plan_proposal' &&
                            message.plan_id
                        ) {
                            try {
                                return dtoToMessage(
                                    message,
                                    await backendApi.getPlan(message.plan_id),
                                );
                            } catch {
                                return dtoToMessage(message);
                            }
                        }
                        return dtoToMessage(message);
                    }),
                );
                if (!cancelled) setMessages(sortMessages(hydrated));
            } catch (err) {
                if (!cancelled) setError(errorText(err));
            } finally {
                if (!cancelled) setIsBooting(false);
            }
        }

        boot();
        return () => {
            cancelled = true;
        };
    }, [currentSessionId]);

    useEffect(() => {
        if (!currentSessionId) return;

        wsRef.current?.close();
        wsRef.current = openSessionWebSocket({
            sessionId: currentSessionId,
            onFrame: handleWsFrame,
            onClose: () => undefined,
            onError: () =>
                setError('No pudimos conectar el WebSocket del chat.'),
        });

        return () => {
            wsRef.current?.close();
            wsRef.current = null;
        };
    }, [handleWsFrame, currentSessionId]);

    async function handleSend(text: string, files?: File[]) {
        if (!currentSessionId) return;

        const attachments = files?.map(f => ({
            name: f.name,
            type: f.type,
            url: URL.createObjectURL(f)
        }));

        const userMsg: Message = {
            id: makeId(),
            role: 'user',
            content: text,
            createdAt: Date.now(),
            attachments,
        };
        upsertMessage(userMsg);
        setIsTyping(true);
        setError(null);

        try {
            await backendApi.sendChatMessage(currentSessionId, text, attachments);
        } catch (err) {
            appendSystemMessage(errorText(err));
            setIsTyping(false);
        }
    }

    async function approvePlan(planId: string) {
        setBusyPlanId(planId);
        setError(null);
        updatePlan(planId, (plan) => ({ ...plan, state: 'approved' }));
        try {
            await backendApi.approvePlan(planId);
        } catch (err) {
            appendSystemMessage(errorText(err));
            try {
                const fresh = await backendApi.getPlan(planId);
                updatePlan(planId, () => fresh);
            } catch {
                updatePlan(planId, (plan) => ({
                    ...plan,
                    state: 'pending_approval',
                }));
            }
        } finally {
            setBusyPlanId(null);
        }
    }

    async function resolveInput(inputId: string, selectedIds: string[]) {
        if (!currentSessionId) return;
        setBusyInputId(inputId);
        setError(null);
        setIsTyping(true);
        try {
            await backendApi.resolveChatInput(currentSessionId, inputId, selectedIds);
        } catch (err) {
            appendSystemMessage(errorText(err));
            setIsTyping(false);
        } finally {
            setBusyInputId(null);
        }
    }

    async function resolveCredential(requestId: string, value: string | null) {
        if (!currentSessionId) return;
        setBusyCredentialId(requestId);
        setError(null);
        setIsTyping(true);
        try {
            await backendApi.resolveCredential(currentSessionId, requestId, value);
        } catch (err) {
            appendSystemMessage(errorText(err));
            setIsTyping(false);
        } finally {
            setBusyCredentialId(null);
        }
    }

    async function rejectPlan(planId: string) {
        setBusyPlanId(planId);
        setError(null);
        updatePlan(planId, (plan) => ({ ...plan, state: 'rejected' }));
        try {
            await backendApi.rejectPlan(planId, 'Rechazado desde frontend');
        } catch (err) {
            appendSystemMessage(errorText(err));
            try {
                const fresh = await backendApi.getPlan(planId);
                updatePlan(planId, () => fresh);
            } catch {
                updatePlan(planId, (plan) => ({
                    ...plan,
                    state: 'pending_approval',
                }));
            }
        } finally {
            setBusyPlanId(null);
        }
    }

    const visibleMessages = messages.filter(
        (message) =>
            message.kind === 'plan_proposal' ||
            message.role !== 'assistant' ||
            !isRedundantApprovalMessage(message.content),
    );

    return (
        <Sidebar>
            <div className='flex h-full w-full flex-col bg-background'>
                <header className='hidden md:flex min-h-[74px] items-center border-b border-line bg-background px-10 flex-shrink-0'>
                    <div className='flex flex-col gap-2 min-[380px]:flex-row min-[380px]:items-start min-[380px]:justify-between'>
                        <div className='min-w-0'>
                            <h1 className='text-2xl font-semibold tracking-tight text-foreground'>
                                Ata<span className='text-accent'>jo</span>{' '}
                                <span className='text-muted'>Agent</span>
                            </h1>
                        </div>
                    </div>
                </header>
                <ChatThread
                    messages={visibleMessages}
                    isTyping={isTyping || isBooting}
                    onApprovePlan={approvePlan}
                    onRejectPlan={rejectPlan}
                    busyPlanId={busyPlanId}
                    onResolveInput={resolveInput}
                    busyInputId={busyInputId}
                    onResolveCredential={resolveCredential}
                    busyCredentialId={busyCredentialId}
                />
                <ChatInput
                    onSend={handleSend}
                    disabled={isTyping || isBooting || !currentSessionId}
                />
            </div>
        </Sidebar>
    );
}
