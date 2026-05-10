import { TrendingDown, TrendingUp, Activity } from "lucide-react";
import Image from "next/image";

export interface TickerProps {
  symbol: string;
  name: string;
  price: number | string;
  change24h?: number;
  exchange?: string;
  imageUrl?: string;
  currency?: string;
  volume?: string;
  onClick?: () => void;
  className?: string;
}

export function Ticker({
  symbol,
  name,
  price,
  change24h,
  exchange,
  imageUrl,
  currency = "$",
  volume,
  onClick,
  className = "",
}: TickerProps) {
  const isPositive = change24h !== undefined && change24h > 0;
  const isNegative = change24h !== undefined && change24h < 0;

  const formatPrice = (val: number | string) => {
    if (typeof val === "number") {
      return new Intl.NumberFormat("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 6, // Para soportar criptos con muchos decimales
      }).format(val);
    }
    return val;
  };

  return (
    <div
      onClick={onClick}
      className={`flex items-center justify-between rounded-2xl border border-line bg-card p-4 shadow-sm transition-all duration-200 ${
        onClick ? "cursor-pointer hover:border-accent/40 hover:shadow-md hover:bg-surface/50" : ""
      } ${className}`}
    >
      {/* Izquierda: Icono e Información */}
      <div className="flex items-center gap-3 min-w-0">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-full bg-surface border border-line">
          {imageUrl ? (
            <Image 
              src={imageUrl} 
              alt={symbol} 
              width={40} 
              height={40} 
              className="h-full w-full object-cover" 
            />
          ) : (
            <span className="text-sm font-bold text-muted uppercase">
              {symbol.slice(0, 2)}
            </span>
          )}
        </div>
        <div className="flex flex-col min-w-0 pr-2">
          <div className="flex items-center gap-2">
            <span className="truncate font-semibold text-foreground">{symbol}</span>
            {exchange && (
              <span className="rounded bg-background px-1.5 py-0.5 text-[10px] font-medium tracking-wide text-subdued border border-line/50">
                {exchange}
              </span>
            )}
          </div>
          <span className="truncate text-xs text-muted max-w-[160px]">{name}</span>
        </div>
      </div>

      {/* Derecha: Precio y Tendencias */}
      <div className="flex flex-col items-end shrink-0">
        <div className="font-mono font-medium text-foreground">
          {currency}{formatPrice(price)}
        </div>
        {change24h !== undefined && (
          <div
            className={`mt-0.5 flex items-center gap-1 text-xs font-medium ${
              isPositive 
                ? "text-green-500" 
                : isNegative 
                  ? "text-red-500" 
                  : "text-muted"
            }`}
          >
            {isPositive ? (
              <TrendingUp size={14} strokeWidth={2.5} />
            ) : isNegative ? (
              <TrendingDown size={14} strokeWidth={2.5} />
            ) : (
              <Activity size={14} strokeWidth={2.5} />
            )}
            <span>
              {isPositive ? "+" : ""}
              {change24h.toFixed(2)}%
            </span>
          </div>
        )}
        {volume && change24h === undefined && (
          <div className="mt-0.5 text-xs text-muted font-mono">Vol: {volume}</div>
        )}
      </div>
    </div>
  );
}
