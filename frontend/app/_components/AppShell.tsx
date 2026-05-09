"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { label: "Chat", href: "/" },
  { label: "Inversiones", href: "/investments" },
  { label: "Balances", href: "/balances" },
  { label: "Actividad", href: "/activity" },
  { label: "Conexiones", href: "/connections" },
];

function currentLabel(pathname: string) {
  return NAV_ITEMS.find((item) => item.href === pathname)?.label ?? "OpenFi";
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const active = currentLabel(pathname);

  return (
    <main className="min-h-[100dvh] bg-white text-zinc-950 dark:bg-black dark:text-zinc-50">
      <div className="flex h-[100dvh]">
        <aside className="hidden w-56 shrink-0 flex-col border-r border-zinc-200 bg-zinc-50 px-4 pb-6 pt-5 dark:border-zinc-800 dark:bg-zinc-950 md:flex lg:w-64">
          <div className="flex items-center gap-2 text-lg font-semibold">
            <span className="inline-flex h-9 w-9 items-center justify-center rounded-2xl bg-zinc-900 text-sm font-semibold text-white dark:bg-white dark:text-zinc-900">
              P
            </span>
            OpenFi
          </div>
          <nav className="mt-6 space-y-1 text-sm">
            {NAV_ITEMS.map((item) => {
              const isActive = item.href === pathname;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={
                    isActive
                      ? "flex items-center gap-2 rounded-xl bg-zinc-900 px-3 py-2 text-white dark:bg-white dark:text-zinc-900"
                      : "flex items-center gap-2 rounded-xl px-3 py-2 text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-900"
                  }
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="mt-auto space-y-3 pt-6">
            <div className="rounded-2xl border border-zinc-200 bg-white p-3 text-sm shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-zinc-200 text-xs font-semibold text-zinc-700 dark:bg-zinc-800 dark:text-zinc-200">
                  AL
                </div>
                <div className="min-w-0">
                  <div className="truncate font-medium">Alen Davies</div>
                  <div className="truncate text-xs text-zinc-500">Cuenta personal</div>
                </div>
              </div>
              <button
                className="mt-3 w-full rounded-xl border border-zinc-200 px-3 py-2 text-xs font-medium text-zinc-600 transition hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                type="button"
              >
                Gestionar cuenta
              </button>
            </div>
          </div>
        </aside>

        <section className="flex min-h-0 flex-1 flex-col">
          <div className="border-b border-zinc-200 px-4 pb-2 pt-[max(0.75rem,env(safe-area-inset-top))] dark:border-zinc-800 md:hidden">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-base font-semibold">
                <span className="inline-flex h-8 w-8 items-center justify-center rounded-xl bg-zinc-900 text-xs font-semibold text-white dark:bg-white dark:text-zinc-900">
                  P
                </span>
                {active}
              </div>
            </div>
          </div>
          <div className="flex min-h-0 flex-1 flex-col">{children}</div>
        </section>
      </div>
    </main>
  );
}
