'use client';

import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Plus, Trash2, ChevronDown, ChevronUp } from 'lucide-react';
import { useChat } from '../contexts/ChatContext';
import { useState } from 'react';

const NAV_ITEMS = [
    { label: 'Chat', href: '/' },
    { label: 'Inversiones', href: '/investments' },
    { label: 'Balances', href: '/balances' },
    { label: 'Actividad', href: '/activity' },
    { label: 'Conexiones', href: '/connections' },
];

function currentLabel(pathname: string) {
    return NAV_ITEMS.find((item) => item.href === pathname)?.label ?? 'OpenFi';
}

export function AppShell({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const router = useRouter();
    const active = currentLabel(pathname);
    const { sessions, currentSessionId, setCurrentSessionId, createNewSession, deleteSession } = useChat();
    const [showAllChats, setShowAllChats] = useState(false);

    const isChatPage = pathname === '/';
    
    // Sort sessions to make the current one appear in the list properly
    // and show only up to 5 by default
    const displaySessions = showAllChats ? sessions : sessions.slice(0, 5);

    const handleCreateChat = async (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();
        await createNewSession();
        if (!isChatPage) {
            router.push('/');
        }
    };

    const handleDeleteChat = async (e: React.MouseEvent, id: string) => {
        e.preventDefault();
        e.stopPropagation();
        await deleteSession(id);
    };

    const handleSelectChat = (e: React.MouseEvent, id: string) => {
        e.preventDefault();
        setCurrentSessionId(id);
        if (!isChatPage) {
            router.push('/');
        }
    };

    return (
        <main className='min-h-[100dvh] bg-background text-foreground'>
            <div className='flex h-[100dvh]'>
                <aside className='hidden w-56 shrink-0 flex-col border-r border-line bg-background px-4 pb-6 pt-5 md:flex lg:w-64'>
                    <div className='flex items-center gap-3 px-1'>
                        <Image
                            src='/openfi.png'
                            width={35}
                            height={35}
                            alt='logo'
                            className='rounded-full shadow-logo'
                        />
                        <span className='text-lg font-semibold tracking-tight text-foreground'>
                            Open<span className='text-accent'>Fi</span>
                        </span>
                    </div>
                    <nav className='mt-8 space-y-2 text-sm flex-1 overflow-y-auto pr-2 custom-scrollbar'>
                        {NAV_ITEMS.map((item) => {
                            const isActive = item.href === pathname && (item.label !== 'Chat' || isChatPage);
                            const isChat = item.label === 'Chat';
                            
                            return (
                                <div key={item.href} className="flex flex-col">
                                    <div className="flex items-center group relative">
                                        <Link
                                            href={item.href}
                                            className={
                                                isActive
                                                    ? 'flex-1 flex items-center gap-2 rounded-xl bg-accent/10 border border-accent/45 px-3 py-2.5 text-foreground font-medium shadow-glow transition-all duration-200'
                                                    : 'flex-1 flex items-center gap-2 rounded-xl border border-transparent px-3 py-2.5 text-muted font-medium transition-all duration-200 hover:bg-accent/10 hover:text-foreground hover:border-accent/25'
                                            }
                                        >
                                            {item.label}
                                        </Link>
                                        
                                        {isChat && (
                                            <button 
                                                onClick={handleCreateChat}
                                                className="absolute right-2 p-1.5 text-muted hover:text-accent hover:bg-accent/20 rounded-md transition-colors"
                                                title="Nuevo chat"
                                            >
                                                <Plus size={16} />
                                            </button>
                                        )}
                                    </div>
                                    
                                    {isChat && sessions.length > 0 && (
                                        <div className="mt-1 ml-4 flex flex-col gap-1 border-l border-line pl-2 py-1">
                                            {displaySessions.map((session) => (
                                                <div 
                                                    key={session.id}
                                                    onClick={(e) => handleSelectChat(e, session.id)}
                                                    className={`group flex items-center justify-between px-2 py-1.5 rounded-lg cursor-pointer transition-colors text-xs
                                                        ${currentSessionId === session.id && isChatPage
                                                            ? 'bg-line text-foreground font-medium' 
                                                            : 'text-muted hover:bg-line/50 hover:text-foreground'
                                                        }`}
                                                >
                                                    <span className="truncate pr-2">
                                                        {session.title || 'Nuevo chat'}
                                                    </span>
                                                    <button
                                                        onClick={(e) => handleDeleteChat(e, session.id)}
                                                        className="opacity-0 group-hover:opacity-100 p-1 text-muted hover:text-red-400 transition-all rounded"
                                                        title="Eliminar chat"
                                                    >
                                                        <Trash2 size={12} />
                                                    </button>
                                                </div>
                                            ))}
                                            
                                            {sessions.length > 5 && (
                                                <button
                                                    onClick={() => setShowAllChats(!showAllChats)}
                                                    className="flex items-center gap-1 px-2 py-1.5 text-xs text-subdued hover:text-muted transition-colors mt-1"
                                                >
                                                    {showAllChats ? (
                                                        <><ChevronUp size={12} /> Mostrar menos</>
                                                    ) : (
                                                        <><ChevronDown size={12} /> Mostrar {sessions.length - 5} más</>
                                                    )}
                                                </button>
                                            )}
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </nav>
                    <div className='mt-auto space-y-3 pt-6 shrink-0'>
                        <div className='rounded-2xl border border-accent/20 bg-card p-3 shadow-panel-glow-sm'>
                            <div className='flex items-center gap-3'>
                                <div className='flex h-10 w-10 items-center justify-center rounded-full bg-background text-sm font-semibold text-foreground border border-accent/40'>
                                    AL
                                </div>
                                <div className='min-w-0'>
                                    <div className='truncate font-medium text-foreground'>
                                        Alen Davies
                                    </div>
                                    <div className='truncate text-xs text-accent'>
                                        Risk Optimizer
                                    </div>
                                </div>
                            </div>
                            <button
                                className='mt-3 h-9 w-full rounded-xl border border-accent/25 bg-background text-xs font-medium text-muted transition-all duration-200 hover:border-accent/50 hover:bg-accent/10 hover:text-foreground active:scale-[0.98]'
                                type='button'
                            >
                                Gestionar cuenta
                            </button>
                        </div>
                    </div>
                </aside>

                <section className='flex min-h-0 flex-1 flex-col'>
                    <div className='border-b border-line bg-surface px-4 pb-2 pt-[max(0.75rem,env(safe-area-inset-top))] md:hidden'>
                        <div className='flex items-center justify-between'>
                            <div className='flex items-center gap-2 text-base font-semibold'>
                                <Image
                                    src='/openfi.png'
                                    alt='OpenFi Logo'
                                    width={24}
                                    height={24}
                                    className='rounded-md shadow-logo'
                                />
                                <span className='text-foreground'>
                                    {active}
                                </span>
                            </div>
                        </div>
                    </div>
                    <div className='flex min-h-0 flex-1 flex-col'>
                        {children}
                    </div>
                </section>
            </div>
        </main>
    );
}
