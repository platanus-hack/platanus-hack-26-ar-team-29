export function PageHeader({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  return (
    <header className="flex min-h-[74px] shrink-0 flex-col justify-center border-b border-[#1A1A1A] bg-[#050505] px-4 py-3 sm:px-6 lg:px-10">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight text-[#F4F8FB]">{title}</h1>
        {description && <p className="text-[#A8B3C2] text-sm">{description}</p>}
      </div>
    </header>
  );
}
