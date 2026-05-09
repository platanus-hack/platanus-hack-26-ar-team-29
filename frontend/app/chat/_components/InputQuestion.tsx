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
      <div className="rounded-2xl rounded-bl-sm border border-[#1A1A1A] bg-[#080C0D] px-5 py-3 text-sm text-[#A8B3C2] shadow-sm">
        <div className="text-xs uppercase tracking-wide text-[#38D9C6]">{input.title}</div>
        <div className="mt-1 text-[#F4F8FB]">{input.question}</div>
        <div className="mt-2 text-[#38D9C6]">
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
    <div className="rounded-2xl rounded-bl-sm border border-[#38D9C6]/30 bg-[#080C0D] px-5 py-4 text-sm text-[#F4F8FB] shadow-[0_0_15px_rgba(56,217,198,0.08)]">
      <div className="text-xs uppercase tracking-wide text-[#38D9C6]">{input.title}</div>
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
                  ? 'border-[#38D9C6] bg-[#38D9C6]/15 text-[#F4F8FB]'
                  : 'border-[#1A1A1A] bg-[#050505] text-[#F4F8FB] hover:border-[#38D9C6]/50 hover:bg-[#080C0D]'
              }`}
            >
              <div className="font-medium">{opt.label}</div>
              {opt.description && (
                <div className="mt-0.5 text-xs text-[#A8B3C2]">{opt.description}</div>
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
          className="mt-3 w-full rounded-xl border border-[#38D9C6] bg-[#38D9C6]/15 px-4 py-2 text-sm font-medium text-[#F4F8FB] transition hover:bg-[#38D9C6]/25 disabled:opacity-50"
        >
          Confirmar
        </button>
      )}
    </div>
  );
}
