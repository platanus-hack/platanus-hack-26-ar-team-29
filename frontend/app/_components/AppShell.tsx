'use client';

import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

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
    const active = currentLabel(pathname);

    return (
        <main className='min-h-[100dvh] bg-background text-text-primary'>
            <div className='flex h-[100dvh]'>
                <aside className='hidden w-56 shrink-0 flex-col border-r border-[#1A1A1A] bg-[#050505] px-4 pb-6 pt-5 md:flex lg:w-64'>
                    <div className='flex items-center gap-3 px-1'>
                        <Image
                            src='/openfi.png'
                            width={35}
                            height={35}
                            alt='logo'
                            className='rounded-full shadow-[0_0_10px_rgba(56,217,198,0.2)]'
                        />
                        <span className='text-lg font-semibold tracking-tight text-[#F4F8FB]'>
                            Open<span className='text-[#38D9C6]'>Fi</span>
                        </span>
                    </div>
                    <nav className='mt-8 space-y-2 text-sm'>
                        {NAV_ITEMS.map((item) => {
                            const isActive = item.href === pathname;
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={
                                        isActive
                                            ? 'flex items-center gap-2 rounded-xl bg-[#38D9C6]/10 border border-[#38D9C6]/45 px-3 py-2.5 text-[#F4F8FB] font-medium shadow-[0_0_20px_rgba(56,217,198,0.14)] transition-all duration-200'
                                            : 'flex items-center gap-2 rounded-xl border border-transparent px-3 py-2.5 text-[#A8B3C2] font-medium transition-all duration-200 hover:bg-[#38D9C6]/10 hover:text-[#F4F8FB] hover:border-[#38D9C6]/25'
                                    }
                                >
                                    {item.label}
                                </Link>
                            );
                        })}
                    </nav>
                    <div className='mt-auto space-y-3 pt-6'>
                        <div className='rounded-2xl border border-[#38D9C6]/20 bg-[#080C0D] p-3 shadow-[0_0_24px_rgba(56,217,198,0.08)]'>
                            <div className='flex items-center gap-3'>
                                <div className='flex h-10 w-10 items-center justify-center rounded-full bg-[#050505] text-sm font-semibold text-[#F4F8FB] border border-[#38D9C6]/40'>
                                    AL
                                </div>
                                <div className='min-w-0'>
                                    <div className='truncate font-medium text-[#F4F8FB]'>
                                        Alen Davies
                                    </div>
                                    <div className='truncate text-xs text-[#38D9C6]'>
                                        Risk Optimizer
                                    </div>
                                </div>
                            </div>
                            <button
                                className='mt-3 h-9 w-full rounded-xl border border-[#38D9C6]/25 bg-[#050505] text-xs font-medium text-[#A8B3C2] transition-all duration-200 hover:border-[#38D9C6]/50 hover:bg-[#38D9C6]/10 hover:text-[#F4F8FB] active:scale-[0.98]'
                                type='button'
                            >
                                Gestionar cuenta
                            </button>
                        </div>
                    </div>
                </aside>

                <section className='flex min-h-0 flex-1 flex-col'>
                    <div className='border-b border-card bg-surface px-4 pb-2 pt-[max(0.75rem,env(safe-area-inset-top))] md:hidden'>
                        <div className='flex items-center justify-between'>
                            <div className='flex items-center gap-2 text-base font-semibold'>
                                <Image
                                    src='/openfi.png'
                                    alt='OpenFi Logo'
                                    width={24}
                                    height={24}
                                    className='rounded-md shadow-[0_0_10px_rgba(56,217,198,0.2)]'
                                />
                                <span className='text-text-primary'>
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
