'use client';

import { useState } from 'react';
import type { InputRequest } from '../types';

export function InputQuestion({
  input,
  isBusy,
  onResolve,
}: {
  input: InputRequest;
  isBusy: boolean;
  onResolve: (inputId: string, selectedIds: string[]) => void;
}) {
  const [selected, setSelected] = useState<Set<string>>(new Set());

  if (input.resolved) {
    return (
      <div className="rounded-2xl rounded-bl-sm border border-line bg-card px-5 py-3 text-sm text-muted shadow-sm">
        <div className="text-xs uppercase tracking-wide text-accent">{input.title}</div>
        <div className="mt-1 text-foreground">{input.question}</div>
        <div className="mt-2 text-accent">
          {(input.selectedLabels?.length ? input.selectedLabels : ['(sin respuesta)']).join(', ')}
        </div>
      </div>
    );
  }

  function toggle(id: string) {
    if (input.multiSelect) {
      setSelected((prev) => {
        const next = new Set(prev);
        if (next.has(id)) next.delete(id);
        else next.add(id);
        return next;
      });
    } else {
      onResolve(input.inputId, [id]);
    }
  }

  function submitMulti() {
    onResolve(input.inputId, Array.from(selected));
  }

  return (
    <div className="rounded-2xl rounded-bl-sm border border-accent/30 bg-card px-5 py-4 text-sm text-foreground shadow-glow-xs">
      <div className="text-xs uppercase tracking-wide text-accent">{input.title}</div>
      <div className="mt-1 mb-3">{input.question}</div>
      <div className="flex flex-col gap-2">
        {input.options.map((opt) => {
          const isSelected = selected.has(opt.id);
          return (
            <button
              key={opt.id}
              type="button"
              disabled={isBusy}
              onClick={() => toggle(opt.id)}
              className={`rounded-xl border px-4 py-2.5 text-left text-sm transition disabled:opacity-50 ${
                isSelected
                  ? 'border-accent bg-accent/15 text-foreground'
                  : 'border-line bg-background text-foreground hover:border-accent/50 hover:bg-card'
              }`}
            >
              <div className="font-medium">{opt.label}</div>
              {opt.description && (
                <div className="mt-0.5 text-xs text-muted">{opt.description}</div>
              )}
            </button>
          );
        })}
      </div>
      {input.multiSelect && (
        <button
          type="button"
          disabled={isBusy || selected.size === 0}
          onClick={submitMulti}
          className="mt-3 w-full rounded-xl border border-accent bg-accent/15 px-4 py-2 text-sm font-medium text-foreground transition hover:bg-accent/25 disabled:opacity-50"
        >
          Confirmar
        </button>
      )}
    </div>
  );
}
