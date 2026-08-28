import { DollarSign, Percent, TrendingUp, Calendar, Clock } from 'lucide-react';

interface TelemetryCardsProps {
  occupancyPercentage: number;
  smoothedOccupiedCount: number;
  totalCapacity: number;
  hourlyCost: number;
  dailyCost: number;
  annualCost: number;
  hourlyRate: number;
  operatingHours: number;
}

export const TelemetryCards: React.FC<TelemetryCardsProps> = ({
  occupancyPercentage,
  smoothedOccupiedCount,
  totalCapacity,
  hourlyCost,
  dailyCost,
  annualCost,
  hourlyRate,
  operatingHours,
}) => {
  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(val || 0);
  };

  return (
    <div className="space-y-4">
      {/* Primary KPI Grid: Occupancy & Hourly Loss */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Card 1: Occupancy Rate */}
        <div className="p-5 rounded-2xl bg-zinc-900/80 border border-zinc-800 backdrop-blur-sm relative overflow-hidden group hover:border-zinc-700/80 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
              Curb Occupancy Rate
            </span>
            <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <Percent className="w-4 h-4" />
            </div>
          </div>

          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono tracking-tight text-white">
              {occupancyPercentage.toFixed(1)}%
            </span>
            <span className="text-xs text-zinc-400 font-mono">
              ({smoothedOccupiedCount}/{totalCapacity} spots)
            </span>
          </div>

          {/* Progress Bar */}
          <div className="mt-4 w-full h-2 rounded-full bg-zinc-800 overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500 bg-gradient-to-r from-emerald-500 to-teal-400"
              style={{ width: `${Math.min(100, Math.max(0, occupancyPercentage))}%` }}
            ></div>
          </div>
        </div>

        {/* Card 2: Hourly Revenue Loss */}
        <div className="p-5 rounded-2xl bg-zinc-900/80 border border-zinc-800 backdrop-blur-sm relative overflow-hidden group hover:border-zinc-700/80 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
              Hourly Revenue Loss
            </span>
            <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <Clock className="w-4 h-4" />
            </div>
          </div>

          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono tracking-tight text-amber-400">
              {formatCurrency(hourlyCost)}
            </span>
            <span className="text-xs text-zinc-500 font-mono">/ hr</span>
          </div>

          <p className="mt-4 text-xs text-zinc-400 font-mono flex items-center gap-1.5">
            <span>Based on Manhattan Zone M2 rate ({formatCurrency(hourlyRate)}/hr)</span>
          </p>
        </div>
      </div>

      {/* Aggregate Municipal Opportunity Cost Breakdown */}
      <div className="p-5 rounded-2xl bg-gradient-to-br from-zinc-900/90 to-zinc-950 border border-zinc-800 relative overflow-hidden">
        <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3 mb-4">
          <div className="flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-bold text-white tracking-wide">
              Unrealized Municipal Revenue (Opportunity Cost)
            </h3>
          </div>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700">
            Unmetered Curb Subsidy
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Daily Projected Loss */}
          <div className="p-4 rounded-xl bg-zinc-950/60 border border-zinc-800/60">
            <div className="flex items-center gap-2 text-xs text-zinc-400 mb-1.5">
              <TrendingUp className="w-3.5 h-3.5 text-zinc-500" />
              <span>Daily Loss ({operatingHours.toFixed(1)} enforcement hrs)</span>
            </div>
            <div className="text-2xl font-bold font-mono text-white">
              {formatCurrency(dailyCost)}
            </div>
            <p className="text-[11px] text-zinc-500 mt-1">
              8:00 AM – 8:30 PM standard metered period
            </p>
          </div>

          {/* Annual Projected Loss */}
          <div className="p-4 rounded-xl bg-zinc-950/60 border border-zinc-800/60">
            <div className="flex items-center gap-2 text-xs text-zinc-400 mb-1.5">
              <Calendar className="w-3.5 h-3.5 text-emerald-400" />
              <span>Annual Opportunity Cost (312 days)</span>
            </div>
            <div className="text-2xl font-bold font-mono text-emerald-400">
              {formatCurrency(annualCost)}
            </div>
            <p className="text-[11px] text-zinc-500 mt-1">
              6 metered enforcement days/wk (Sundays free in NYC)
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
