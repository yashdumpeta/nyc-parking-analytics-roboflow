import React from 'react';
import { RefreshCw, Info, Building2 } from 'lucide-react';

interface HeaderProps {
  isConnected: boolean;
  isRefreshing: boolean;
  onRefresh: () => void;
  onOpenPolicy: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  isConnected,
  isRefreshing,
  onRefresh,
  onOpenPolicy,
}) => {
  return (
    <header className="border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-40 px-6 py-4">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        {/* Title & Location */}
        <div className="flex items-center gap-3.5">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-emerald-500/20 to-emerald-700/10 border border-emerald-500/30 text-emerald-400 shadow-inner">
            <Building2 className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                NYC Curb Telemetry & Revenue Engine
              </h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-zinc-800 border border-zinc-700 text-zinc-300 font-mono">
                v1.0
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5 flex items-center gap-1.5">
              <span>West Curb, York Avenue (72nd & 73rd St, Manhattan)</span>
              <span className="text-zinc-600">•</span>
              <span className="text-emerald-400 font-medium">Zone M2 Telemetry</span>
            </p>
          </div>
        </div>

        {/* Status Indicators & Actions */}
        <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-end">
          {/* Live Status Pill */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-900/90 border border-zinc-800 text-xs font-mono">
            <span className="relative flex h-2 w-2">
              {isConnected && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              )}
              <span
                className={`relative inline-flex rounded-full h-2 w-2 ${
                  isConnected ? 'bg-emerald-500' : 'bg-rose-500'
                }`}
              ></span>
            </span>
            <span className={isConnected ? 'text-zinc-200' : 'text-zinc-400'}>
              {isConnected ? 'NYCDOT LIVE' : 'CONNECTING...'}
            </span>
          </div>

          {/* Policy Context Button */}
          <button
            onClick={onOpenPolicy}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 text-xs text-zinc-300 transition-colors cursor-pointer"
            title="View Municipal Policy Context"
          >
            <Info className="w-3.5 h-3.5 text-zinc-400" />
            <span className="hidden sm:inline">Policy Context</span>
          </button>

          {/* Force Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 active:scale-95 disabled:opacity-50 text-xs font-medium text-white shadow-lg shadow-emerald-950/50 transition-all cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>Force Snapshot</span>
          </button>
        </div>
      </div>
    </header>
  );
};
