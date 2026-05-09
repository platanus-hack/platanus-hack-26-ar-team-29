import Link from 'next/link';

interface TabProps {
    href: string;
    label: string;
    isActive: boolean;
}

export function Tab({ href, label, isActive }: TabProps) {
    return (
        <Link
            href={href}
            className={
                isActive
                    ? 'flex-1 flex items-center gap-2 rounded-xl bg-accent/10 border border-accent/45 px-3 py-2.5 text-foreground font-medium shadow-glow transition-all duration-200'
                    : 'flex-1 flex items-center gap-2 rounded-xl border border-transparent px-3 py-2.5 text-muted font-medium transition-all duration-200 hover:bg-accent/10 hover:text-foreground hover:border-accent/25'
            }
        >
            {label}
        </Link>
    );
}
