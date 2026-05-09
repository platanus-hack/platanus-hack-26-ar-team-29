import { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  description: string;
  children?: ReactNode;
}

export function PageHeader({ title, description, children }: PageHeaderProps) {
  return (
    <div className="flex-none pt-8 sm:pt-10 flex justify-between items-end">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">{title}</h1>
        <p className="mt-2 text-sm text-subdued">{description}</p>
      </div>
      {children && <div>{children}</div>}
    </div>
  );
}
