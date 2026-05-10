'use client';

import Image from 'next/image';
import { usePathname, useRouter } from 'next/navigation';
import { Plus, Trash2, ChevronDown, ChevronUp, Menu, X } from 'lucide-react';
import { useChat } from '../contexts/ChatContext';
import { useState, useEffect } from 'react';
import { Tab } from './Tab';
import { Button } from './Button';

const NAV_ITEMS = [
    { label: 'Chat', href: '/' },
    { label: 'Conexiones', href: '/connections' },
    { label: 'Balances', href: '/balances' },
    { label: 'Perfil', href: '/profile' },
    { label: 'Inversiones', href: '/investments' },
    { label: 'Actividad', href: '/activity' },
];

function currentLabel(pathname: string) {
    return NAV_ITEMS.find((item) => item.href === pathname)?.label ?? 'Atajo';
}

export function Sidebar({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const router = useRouter();
    const active = currentLabel(pathname);
    const { sessions, currentSessionId, setCurrentSessionId, createNewSession, deleteSession } = useChat();
    const [showAllChats, setShowAllChats] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    useEffect(() => {
        setIsMobileMenuOpen(false);
    }, [pathname]);

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
        setIsMobileMenuOpen(false);
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
        setIsMobileMenuOpen(false);
    };

    const sidebarContent = (
        <>
            <div className='flex items-center justify-between gap-3 px-1 md:justify-start'>
                <div className='flex items-center gap-3'>
                    <Image
                        src='/atajo.png'
                        width={35}
                        height={35}
                        alt='logo'
                        className='rounded-full shadow-logo'
                    />
                    <span className='text-lg font-semibold tracking-tight text-foreground'>
                        Ata<span className='text-accent'>jo</span>
                    </span>
                </div>
                <Button 
                    variant="ghost" 
                    size="icon-sm" 
                    className="md:hidden text-muted hover:text-foreground" 
                    onClick={() => setIsMobileMenuOpen(false)}
                >
                    <X size={20} />
                </Button>
            </div>
            <nav className='mt-8 space-y-2 text-sm flex-1 overflow-y-auto pr-2 custom-scrollbar'>
                {NAV_ITEMS.map((item) => {
                    const isActive = item.href === pathname && (item.label !== 'Chat' || isChatPage);
                    const isChat = item.label === 'Chat';
                    
                    return (
                        <div key={item.href} className="flex flex-col">
                            <div className="flex items-center group relative">
                                <Tab 
                                    href={item.href} 
                                    label={item.label} 
                                    isActive={isActive} 
                                />
                                
                                {isChat && (
                                    <Button 
                                        variant="ghost"
                                        size="icon-sm"
                                        onClick={handleCreateChat}
                                        className="absolute right-2"
                                        title="Nuevo chat"
                                    >
                                        <Plus size={16} />
                                    </Button>
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
                                            <Button
                                                variant="danger"
                                                size="icon-sm"
                                                onClick={(e) => handleDeleteChat(e, session.id)}
                                                className="opacity-0 group-hover:opacity-100 p-1 rounded"
                                                title="Eliminar chat"
                                            >
                                                <Trash2 size={12} />
                                            </Button>
                                        </div>
                                    ))}
                                    
                                    {sessions.length > 5 && (
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => setShowAllChats(!showAllChats)}
                                            className="gap-1 px-2 py-1.5 text-subdued hover:text-muted mt-1 !justify-start hover:bg-transparent"
                                        >
                                            {showAllChats ? (
                                                <><ChevronUp size={12} /> Mostrar menos</>
                                            ) : (
                                                <><ChevronDown size={12} /> Mostrar {sessions.length - 5} más</>
                                            )}
                                        </Button>
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
                                Asistente de inversión
                            </div>
                        </div>
                    </div>
                    <Button
                        variant="outline"
                        size="sm"
                        fullWidth
                        className="mt-3 text-xs"
                        type='button'
                    >
                        Gestionar cuenta
                    </Button>
                </div>
            </div>
        </>
    );

    return (
        <main className='min-h-[100dvh] bg-background text-foreground'>
            <div className='flex h-[100dvh] overflow-hidden'>
                {/* Desktop Sidebar */}
                <aside className='hidden w-56 shrink-0 flex-col border-r border-line bg-background px-4 pb-6 pt-5 md:flex lg:w-64 z-10'>
                    {sidebarContent}
                </aside>

                {/* Mobile Drawer Overlay */}
                {isMobileMenuOpen && (
                    <div 
                        className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm md:hidden"
                        onClick={() => setIsMobileMenuOpen(false)}
                    />
                )}
                
                {/* Mobile Sidebar */}
                <aside 
                    className={`fixed inset-y-0 left-0 z-50 w-64 flex-col border-r border-line bg-background px-4 pb-6 pt-5 transition-transform duration-300 ease-in-out md:hidden flex ${
                        isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
                    }`}
                >
                    {sidebarContent}
                </aside>

                <section className='flex min-h-0 flex-1 flex-col overflow-hidden'>
                    <div className='border-b border-line bg-surface px-4 pb-2 pt-[max(0.75rem,env(safe-area-inset-top))] md:hidden flex-shrink-0'>
                        <div className='flex items-center justify-between'>
                            <div className='flex items-center gap-2 text-base font-semibold'>
                                <Image
                                    src='/atajo.png'
                                    alt='Atajo Logo'
                                    width={24}
                                    height={24}
                                    className='rounded-md shadow-logo'
                                />
                                <span className='text-foreground'>
                                    {active}
                                </span>
                            </div>
                            <Button variant="ghost" size="icon-sm" onClick={() => setIsMobileMenuOpen(true)}>
                                <Menu size={20} className="text-foreground" />
                            </Button>
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
