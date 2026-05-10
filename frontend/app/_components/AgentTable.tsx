import React from 'react';
import { Table as TableIcon } from 'lucide-react';

export interface AgentTableProps {
  csvData: string;
  title?: string;
  description?: string;
}

export function AgentTable({ csvData, title, description }: AgentTableProps) {
  if (!csvData) return null;

  // Split the CSV data into lines, ignoring empty lines
  const lines = csvData
    .trim()
    .split('\n')
    .map(line => line.split(',').map(cell => cell.trim()))
    .filter(row => row.length > 0 && row.some(cell => cell !== ''));

  if (lines.length === 0) return null;

  const headers = lines[0];
  const rows = lines.slice(1);

  return (
    <div className="space-y-3 rounded-2xl border border-line bg-background p-4 sm:p-5 my-2 w-full">
      {(title || description) && (
        <div className="mb-4">
          {title && (
            <div className="flex items-center gap-2 mb-1 text-lg font-semibold text-foreground">
              <TableIcon className="w-5 h-5 text-accent" />
              <h3>{title}</h3>
            </div>
          )}
          {description && <p className="text-sm text-muted">{description}</p>}
        </div>
      )}
      
      <div className="w-full overflow-x-auto rounded-xl border border-line bg-card">
        <table className="w-full text-sm text-left border-collapse">
          <thead className="text-xs text-muted tracking-wide uppercase bg-background/50 border-b border-line">
            <tr>
              {headers.map((header, i) => (
                <th key={i} className="px-4 py-3 font-medium whitespace-nowrap">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {rows.length > 0 ? (
              rows.map((row, i) => (
                <tr key={i} className="hover:bg-accent/5 transition-colors duration-200">
                  {row.map((cell, j) => (
                    <td key={j} className="px-4 py-3 whitespace-nowrap text-foreground">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={headers.length} className="px-4 py-4 text-center text-muted italic">
                  No hay datos en la tabla.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
