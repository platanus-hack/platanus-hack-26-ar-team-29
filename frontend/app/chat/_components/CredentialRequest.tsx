'use client';

import { useState } from 'react';
import type { CredentialRequest as ICredentialRequest } from '../types';
import { Button } from '../../_components/Button';

export function CredentialRequest({
  credential,
  isBusy,
  onResolve,
}: {
  credential: ICredentialRequest;
  isBusy: boolean;
  onResolve: (requestId: string, value: string | null) => void;
}) {
  const [value, setValue] = useState('');

  if (credential.resolved) {
    return (
      <div className="rounded-2xl rounded-bl-sm border border-line bg-card px-5 py-3 text-sm text-muted shadow-sm">
        <div className="text-xs uppercase tracking-wide text-accent">{credential.title}</div>
        <div className="mt-1 text-foreground">{credential.instructions}</div>
        <div className="mt-2 text-accent">
          {credential.cancelled ? '(cancelado)' : '••• (proveído)'}
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl rounded-bl-sm border border-accent/30 bg-card px-5 py-4 text-sm text-foreground shadow-glow-xs">
      <div className="text-xs uppercase tracking-wide text-accent">{credential.title}</div>
      <div className="mt-1 mb-3">{credential.instructions}</div>
      <div className="flex flex-col gap-2">
        <input
          type={credential.kind === 'seed_phrase' ? 'text' : 'password'}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={credential.placeholder || 'Escribí acá...'}
          className="w-full rounded-xl border border-line bg-background px-4 py-2.5 text-sm outline-none focus:border-accent"
          disabled={isBusy}
        />
        <div className="mt-2 flex gap-2">
          <Button
            type="button"
            disabled={isBusy}
            onClick={() => onResolve(credential.requestId, null)}
            variant="outline"
            className="flex-1"
          >
            Cancelar
          </Button>
          <Button
            type="button"
            disabled={isBusy || !value}
            onClick={() => onResolve(credential.requestId, value)}
            variant="primary"
            className="flex-1"
          >
            Confirmar
          </Button>
        </div>
      </div>
    </div>
  );
}
