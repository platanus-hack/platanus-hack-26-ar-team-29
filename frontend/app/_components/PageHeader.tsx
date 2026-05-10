import { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  description: string;
  children?: ReactNode;
}

export function PageHeader({ title, description, children }: PageHeaderProps) {
  return (
    <header className="hidden md:flex min-h-[74px] shrink-0 items-center justify-between border-b border-line bg-background px-4 py-3 sm:px-6 lg:px-10">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">{title}</h1>
        {description && <p className="text-muted text-sm">{description}</p>}
      </div>
      {children && <div className="ml-4">{children}</div>}
    </header>
  );
}
