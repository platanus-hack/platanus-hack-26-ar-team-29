'use client';

import { useState } from 'react';
import type { InputRequest } from '../types';
import { Button } from '../../_components/Button';

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
            <Button
              key={opt.id}
              type="button"
              disabled={isBusy}
              onClick={() => toggle(opt.id)}
              variant={isSelected ? 'primary' : 'outline'}
              className="justify-start h-auto py-2.5 flex-col items-start gap-0.5"
              fullWidth
            >
              <div className="font-medium">{opt.label}</div>
              {opt.description && (
                <div className={`mt-0.5 text-xs ${isSelected ? 'text-background/80' : 'text-muted'}`}>{opt.description}</div>
              )}
            </Button>
          );
        })}
      </div>
      {input.multiSelect && (
        <div className="mt-3">
          <Button
            type="button"
            disabled={isBusy || selected.size === 0}
            onClick={submitMulti}
            variant="primary"
            fullWidth
          >
            Confirmar
          </Button>
        </div>
      )}
    </div>
  );
}
