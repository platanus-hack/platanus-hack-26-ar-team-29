export function PageHeader({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  return (
    <header className="shrink-0 border-b border-zinc-200 bg-white/95 px-4 pb-3 pt-4 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/95 sm:px-6 sm:py-5 lg:px-10">
      <div className="flex flex-col gap-2">
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
    </header>
  );
}
