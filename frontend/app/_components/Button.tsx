import { ButtonHTMLAttributes, forwardRef } from 'react';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'outline' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg' | 'icon' | 'icon-sm';
    fullWidth?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    (
        {
            className = '',
            variant = 'primary',
            size = 'md',
            fullWidth = false,
            children,
            ...props
        },
        ref,
    ) => {
        const baseStyles =
            'inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer';

        const variants = {
            primary:
                'bg-accent text-background shadow-send hover:bg-accent-hover hover:shadow-send-hover active:scale-95',
            outline:
                'border border-accent/25 bg-background text-muted hover:border-accent/50 hover:bg-accent/10 hover:text-foreground active:scale-[0.98]',
            ghost: 'text-muted hover:bg-accent/20 hover:text-accent active:scale-[0.98]',
            danger: 'text-muted hover:bg-red-500/10 hover:text-red-400 active:scale-[0.98]',
        };

        const sizes = {
            sm: 'h-9 px-3 text-xs',
            md: 'h-10 px-4 text-sm',
            lg: 'h-12 px-6 text-base',
            'icon-sm': 'p-1.5',
            icon: 'h-12 w-12 shrink-0',
        };

        // Determine default border radius based on size if not overridden
        let borderRadius = 'rounded-xl';
        if (size === 'icon') borderRadius = 'rounded-full';
        if (size === 'icon-sm') borderRadius = 'rounded-md';

        const classes = [
            baseStyles,
            variants[variant],
            sizes[size],
            borderRadius,
            fullWidth ? 'w-full' : '',
            className,
        ]
            .filter(Boolean)
            .join(' ');

        return (
            <button ref={ref} className={classes} {...props}>
                {children}
            </button>
        );
    },
);

Button.displayName = 'Button';
