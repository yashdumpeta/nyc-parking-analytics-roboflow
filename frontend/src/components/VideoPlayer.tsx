import React, { useState } from 'react';
import { Camera, AlertCircle } from 'lucide-react';

interface VideoPlayerProps {
  streamUrl: string;
  modelId: string;
  confidence: number;
  occupiedCount: number;
  totalCapacity: number;
  totalDetected: number;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({
  streamUrl,
  modelId,
  confidence,
  occupiedCount,
  totalCapacity,
  totalDetected,
}) => {
  const [hasError, setHasError] = useState(false);

  return (
    <div className="relative rounded-2xl overflow-hidden border border-zinc-800 bg-zinc-950 shadow-2xl">
      {/* 1. Video Header Bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-zinc-900/90 border-b border-zinc-800/80 text-xs text-zinc-300">
        <div className="flex items-center gap-2 font-mono">
          <Camera className="w-3.5 h-3.5 text-emerald-400" />
          <span className="font-semibold text-white">NYC DOT CCTV Feed</span>
          <span className="text-zinc-600">|</span>
          <span className="text-zinc-400">York Ave & 72nd St</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded bg-zinc-800 text-[11px] font-mono text-zinc-400 border border-zinc-700">
            {modelId} ({(confidence * 100).toFixed(0)}% conf)
          </span>
        </div>
      </div>

      {/* 2. Unified Status, Legend & Occupancy Row (Above Raw Feed) */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-2.5 bg-zinc-900/50 border-b border-zinc-800 text-xs font-mono">
        <div className="flex items-center gap-3">
          {/* AI Detection Active Pill */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/25 text-[11px] text-emerald-400 font-semibold">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            AI DETECTION ACTIVE
          </div>

          {/* Legend Items */}
          <div className="flex items-center gap-3 text-[11px] text-zinc-400">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
              In Curb Zone (Counted)
            </span>
            <span className="text-zinc-700">•</span>
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-amber-400"></span>
              Outside Zone (Travel Lane)
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3.5 text-xs">
          {/* Total Vehicles in View */}
          <div className="text-zinc-400 text-[11px]">
            Vehicles in View: <span className="font-bold text-white">{totalDetected}</span>
          </div>

          <span className="text-zinc-700">•</span>

          {/* Curb Occupancy */}
          <div className="px-2.5 py-1 rounded-md bg-zinc-900 border border-zinc-700/80 text-[11px] text-zinc-300">
            Curb Occupancy:{' '}
            <span className="font-bold text-emerald-400">{occupiedCount}</span> /{' '}
            {totalCapacity} spots
          </div>
        </div>
      </div>

      {/* 3. Dedicated Raw Feed Container */}
      <div className="relative aspect-[4/3] sm:aspect-[16/10] max-h-[500px] w-full bg-black flex items-center justify-center overflow-hidden">
        {hasError ? (
          <div className="flex flex-col items-center justify-center gap-3 text-zinc-500 p-6 text-center">
            <AlertCircle className="w-8 h-8 text-amber-500/80" />
            <p className="text-sm font-medium text-zinc-400">
              Connecting to live AI inference stream at <code className="text-xs text-emerald-400">127.0.0.1:8000</code>...
            </p>
            <p className="text-xs text-zinc-600">
              Ensure the FastAPI backend is running and streaming frames.
            </p>
          </div>
        ) : (
          <img
            src={streamUrl}
            alt="NYC DOT Live Camera Stream"
            className="w-full h-full object-contain"
            onError={() => setHasError(true)}
            onLoad={() => setHasError(false)}
          />
        )}
      </div>
    </div>
  );
};
