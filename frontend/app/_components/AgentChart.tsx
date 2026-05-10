"use client";

import React from 'react';
import { PieChart as PieChartIcon, BarChart3, TrendingUp } from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  LineChart, 
  Line, 
  PieChart,
  Pie,
  Cell,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip,
  Legend
} from 'recharts';

export interface ChartDataPoint {
  label: string;
  value: number;
}

export interface AgentChartProps {
  title?: string;
  description?: string;
  type?: 'bar' | 'line' | 'pie';
  data: ChartDataPoint[];
  valueLabel?: string;
  color?: string;
}

export function AgentChart({ 
  title, 
  description, 
  type = 'bar', 
  data = [], 
  valueLabel = 'Valor',
  color
}: AgentChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="p-4 border border-line rounded-xl bg-card flex items-center justify-center text-sm text-muted">
        No hay datos para mostrar.
      </div>
    );
  }

  // Use the native accent color from the theme
  const chartColor = color ? color : 'var(--color-accent)';

  // Theme variables for recharts
  const axisColor = 'var(--color-muted)';
  const gridColor = 'var(--color-line)';
  const tooltipBg = 'var(--color-card)';
  const tooltipBorder = 'var(--color-line)';
  const tooltipText = 'var(--color-foreground)';

  return (
    <div className="space-y-3 rounded-2xl border border-line bg-background p-4 sm:p-5 my-2 w-full">
      {(title || description) && (
        <div className="mb-4">
          {title && (
            <div className="flex items-center gap-2 mb-1 text-lg font-semibold text-foreground">
              {type === 'bar' ? <BarChart3 className="w-5 h-5 text-accent" /> : type === 'pie' ? <PieChartIcon className="w-5 h-5 text-accent" /> : <TrendingUp className="w-5 h-5 text-accent" />}
              <h3>{title}</h3>
            </div>
          )}
          {description && <p className="text-sm text-muted">{description}</p>}
        </div>
      )}

      <div className="w-full h-64 mt-2">
        <ResponsiveContainer width="100%" height="100%">
          {type === 'pie' ? (
            <PieChart margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
                nameKey="label"
              >
                {data.map((entry, index) => {
                  const colors = [
                    'var(--color-accent)', 
                    'var(--color-accent-secondary)', 
                    'var(--color-warning)', 
                    'var(--color-error)', 
                    'var(--color-success)', 
                    '#8b5cf6', 
                    '#ec4899'
                  ];
                  return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                })}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: tooltipBg, borderRadius: '8px', border: `1px solid ${tooltipBorder}`, boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                formatter={(value: any) => [value, valueLabel]}
                itemStyle={{ color: tooltipText, fontWeight: 600 }}
              />
              <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ color: axisColor }} />
            </PieChart>
          ) : type === 'line' ? (
            <LineChart data={data} margin={{ top: 5, right: 10, bottom: 5, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={gridColor} />
              <XAxis 
                dataKey="label" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 12, fill: axisColor }} 
                dy={10}
              />
              <YAxis 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 12, fill: axisColor }}
                tickFormatter={(val) => val >= 1000 ? `${(val/1000).toFixed(1)}k` : val}
              />
              <Tooltip 
                cursor={{ stroke: gridColor, strokeWidth: 2 }}
                contentStyle={{ backgroundColor: tooltipBg, borderRadius: '8px', border: `1px solid ${tooltipBorder}`, boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                formatter={(value: any) => [value, valueLabel]}
                labelStyle={{ color: tooltipText, fontWeight: 600, marginBottom: '4px' }}
                itemStyle={{ color: chartColor, fontWeight: 600 }}
              />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke={chartColor} 
                strokeWidth={3}
                dot={{ r: 4, fill: chartColor, strokeWidth: 0 }}
                activeDot={{ r: 6, stroke: tooltipBg, strokeWidth: 2 }}
              />
            </LineChart>
          ) : (
            <BarChart data={data} margin={{ top: 5, right: 10, bottom: 5, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={gridColor} />
              <XAxis 
                dataKey="label" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 12, fill: axisColor }} 
                dy={10}
              />
              <YAxis 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 12, fill: axisColor }}
                tickFormatter={(val) => val >= 1000 ? `${(val/1000).toFixed(1)}k` : val}
              />
              <Tooltip 
                cursor={{ fill: 'var(--color-surface)' }}
                contentStyle={{ backgroundColor: tooltipBg, borderRadius: '8px', border: `1px solid ${tooltipBorder}`, boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                formatter={(value: any) => [value, valueLabel]}
                labelStyle={{ color: tooltipText, fontWeight: 600, marginBottom: '4px' }}
                itemStyle={{ color: chartColor, fontWeight: 600 }}
              />
              <Bar 
                dataKey="value" 
                fill={chartColor} 
                radius={[4, 4, 0, 0]} 
                maxBarSize={40}
              />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
