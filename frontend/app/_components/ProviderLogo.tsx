import Image from 'next/image';

type ProviderKey =
    | 'wallbit'
    | 'ethereum'
    | 'ethereum_custodial'
    | 'aave'
    | 'usdc'
    | 'bank'
    | string;

const SIZE_CLASSES: Record<NonNullable<ProviderLogoProps['size']>, string> = {
    sm: 'h-7 w-7 text-xs',
    md: 'h-9 w-9 text-sm',
    lg: 'h-11 w-11 text-base',
};

interface ProviderLogoProps {
    provider: ProviderKey;
    size?: 'sm' | 'md' | 'lg';
    className?: string;
}

function normalize(provider: string): string {
    return provider.toLowerCase().replace(/[\s_-]+/g, '');
}

export function ProviderLogo({ provider, size = 'md', className = '' }: ProviderLogoProps) {
    const key = normalize(provider);
    const dim = SIZE_CLASSES[size];
    const base =
        `inline-flex shrink-0 items-center justify-center rounded-full border border-line bg-card font-semibold ${dim} ${className}`.trim();

    if (key === 'ethereum' || key === 'ethereumcustodial' || key === 'eth') {
        return (
            <span className={base} title='Ethereum'>
                <svg
                    viewBox='0 0 256 417'
                    aria-hidden='true'
                    className='h-[55%] w-[55%] text-foreground'
                >
                    <path
                        fill='currentColor'
                        d='M127.961 0l-2.795 9.5v275.668l2.795 2.79 127.962-75.638z'
                        opacity='0.85'
                    />
                    <path
                        fill='currentColor'
                        d='M127.962 0L0 212.32l127.962 75.639V154.158z'
                        opacity='0.55'
                    />
                    <path
                        fill='currentColor'
                        d='M127.961 312.187l-1.575 1.92v98.199l1.575 4.6L256 236.587z'
                        opacity='0.85'
                    />
                    <path
                        fill='currentColor'
                        d='M127.962 416.905v-104.72L0 236.585z'
                        opacity='0.55'
                    />
                    <path
                        fill='currentColor'
                        d='M127.961 287.958l127.96-75.637-127.96-58.162z'
                        opacity='0.95'
                    />
                    <path
                        fill='currentColor'
                        d='M0 212.32l127.96 75.638V154.159z'
                        opacity='0.7'
                    />
                </svg>
            </span>
        );
    }

    if (key === 'wallbit') {
        return (
            <span
                className={`${base} bg-white overflow-hidden`}
                title='Wallbit'
            >
                <img
                    src='/wallbit-logo.png'
                    alt='Wallbit'
                    className='h-full w-full object-cover'
                />
            </span>
        );
    }

    if (key === 'aave') {
        return (
            <span
                className={`${base} bg-accent/15 border-accent/30 text-accent`}
                title='Aave'
            >
                <svg
                    viewBox='0 0 24 24'
                    aria-hidden='true'
                    className='h-[55%] w-[55%]'
                    fill='none'
                    stroke='currentColor'
                    strokeWidth='2.4'
                    strokeLinecap='round'
                    strokeLinejoin='round'
                >
                    <path d='M4 20 12 4l8 16' />
                    <path d='M8 14h8' />
                </svg>
            </span>
        );
    }

    if (key === 'usdc') {
        return (
            <span className={`${base} text-foreground`} title='USDC'>
                <span className='font-mono'>$</span>
            </span>
        );
    }

    if (key === 'bank') {
        return (
            <span className={`${base} text-muted`} title='Fintech'>
                <svg
                    viewBox='0 0 24 24'
                    aria-hidden='true'
                    className='h-[50%] w-[50%]'
                    fill='none'
                    stroke='currentColor'
                    strokeWidth='2'
                    strokeLinecap='round'
                    strokeLinejoin='round'
                >
                    <path d='M21 12V7H5a2 2 0 0 1 0-4h14v4' />
                    <path d='M3 5v14a2 2 0 0 0 2 2h16v-5' />
                    <path d='M18 12a2 2 0 0 0 0 4h4v-4Z' />
                </svg>
            </span>
        );
    }

    // Fallback: first letter of provider name in a neutral badge.
    const letter = (provider || '?').trim().charAt(0).toUpperCase() || '?';
    return (
        <span className={`${base} text-muted`} title={provider}>
            {letter}
        </span>
    );
}
