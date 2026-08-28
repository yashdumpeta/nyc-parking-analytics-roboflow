import { Crosshair, Move, DollarSign, RotateCcw, Cpu } from 'lucide-react';

export interface AppConfig {
  confidence_threshold: number;
  model_id: string;
  trigger_anchor: string;
  zone_offset_x: number;
  zone_offset_y: number;
  zone_scale: number;
  hourly_rate: number;
  total_capacity: number;
  operating_hours_per_day: number;
}

interface ControlSidebarProps {
  config: AppConfig;
  onConfigChange: (newConfig: Partial<AppConfig>) => void;
  onResetZone: () => void;
}

export const ControlSidebar: React.FC<ControlSidebarProps> = ({
  config,
  onConfigChange,
  onResetZone,
}) => {
  return (
    <aside className="w-full lg:w-80 flex-shrink-0 space-y-5">
      {/* Section 1: AI Model & Sensitivity */}
      <div className="p-4 rounded-2xl bg-zinc-900/80 border border-zinc-800 backdrop-blur-sm space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-zinc-300">
          <Cpu className="w-4 h-4 text-emerald-400" />
          <span>AI Detection Tuning</span>
        </div>

        {/* Confidence Threshold */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs">
            <label className="text-zinc-400 font-medium">Confidence Threshold</label>
            <span className="font-mono text-emerald-400 font-bold">
              {(config.confidence_threshold * 100).toFixed(0)}%
            </span>
          </div>
          <input
            type="range"
            min="0.05"
            max="0.90"
            step="0.05"
            value={config.confidence_threshold}
            onChange={(e) => onConfigChange({ confidence_threshold: parseFloat(e.target.value) })}
            className="w-full accent-emerald-500 bg-zinc-800 rounded-lg cursor-pointer h-1.5"
          />
          <p className="text-[10px] text-zinc-500">
            Lower if parked cars are visible but not highlighted (e.g. 15%).
          </p>
        </div>

        {/* Model Selector */}
        <div className="space-y-1.5">
          <label className="text-xs text-zinc-400 font-medium">Inference Model</label>
          <select
            value={config.model_id}
            onChange={(e) => onConfigChange({ model_id: e.target.value })}
            className="w-full px-3 py-1.5 rounded-lg bg-zinc-950 border border-zinc-800 text-xs font-mono text-zinc-200 focus:outline-none focus:border-emerald-500 cursor-pointer"
          >
            <option value="yolov8m-640">yolov8m-640 (Balanced Default)</option>
            <option value="yolov8s-640">yolov8s-640 (Fast Lightweight)</option>
            <option value="yolov8n-640">yolov8n-640 (Ultra Fast Nano)</option>
            <option value="curbside-parking-mpa/1">curbside-parking-mpa/1 (Fine-Tuned)</option>
          </select>
        </div>

        {/* Trigger Anchor */}
        <div className="space-y-1.5">
          <label className="text-xs text-zinc-400 font-medium flex items-center justify-between">
            <span>Vehicle Anchor Point</span>
            <Crosshair className="w-3 h-3 text-zinc-500" />
          </label>
          <select
            value={config.trigger_anchor}
            onChange={(e) => onConfigChange({ trigger_anchor: e.target.value })}
            className="w-full px-3 py-1.5 rounded-lg bg-zinc-950 border border-zinc-800 text-xs font-mono text-zinc-200 focus:outline-none focus:border-emerald-500 cursor-pointer"
          >
            <option value="BOTTOM_CENTER">BOTTOM_CENTER (Tire Base - Default)</option>
            <option value="CENTER">CENTER (Vehicle Centroid)</option>
            <option value="BOTTOM_LEFT">BOTTOM_LEFT</option>
            <option value="BOTTOM_RIGHT">BOTTOM_RIGHT</option>
            <option value="TOP_CENTER">TOP_CENTER</option>
          </select>
        </div>
      </div>

      {/* Section 2: Polygon Zone Alignment */}
      <div className="p-4 rounded-2xl bg-zinc-900/80 border border-zinc-800 backdrop-blur-sm space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-zinc-300">
            <Move className="w-4 h-4 text-emerald-400" />
            <span>Zone Alignment</span>
          </div>
          <button
            onClick={onResetZone}
            className="text-[11px] font-mono text-zinc-400 hover:text-white flex items-center gap-1 transition-colors cursor-pointer"
            title="Reset polygon to default York Ave coordinates"
          >
            <RotateCcw className="w-3 h-3" />
            Reset
          </button>
        </div>

        {/* Shift X */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs">
            <label className="text-zinc-400 font-medium">Horizontal Shift (X)</label>
            <span className="font-mono text-zinc-300">{config.zone_offset_x}px</span>
          </div>
          <input
            type="range"
            min="-80"
            max="80"
            step="2"
            value={config.zone_offset_x}
            onChange={(e) => onConfigChange({ zone_offset_x: parseInt(e.target.value, 10) })}
            className="w-full accent-emerald-500 bg-zinc-800 rounded-lg cursor-pointer h-1.5"
          />
        </div>

        {/* Shift Y */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs">
            <label className="text-zinc-400 font-medium">Vertical Shift (Y)</label>
            <span className="font-mono text-zinc-300">{config.zone_offset_y}px</span>
          </div>
          <input
            type="range"
            min="-80"
            max="80"
            step="2"
            value={config.zone_offset_y}
            onChange={(e) => onConfigChange({ zone_offset_y: parseInt(e.target.value, 10) })}
            className="w-full accent-emerald-500 bg-zinc-800 rounded-lg cursor-pointer h-1.5"
          />
        </div>

        {/* Scale */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs">
            <label className="text-zinc-400 font-medium">Zone Scale / Padding</label>
            <span className="font-mono text-zinc-300">{config.zone_scale.toFixed(2)}x</span>
          </div>
          <input
            type="range"
            min="0.6"
            max="1.8"
            step="0.05"
            value={config.zone_scale}
            onChange={(e) => onConfigChange({ zone_scale: parseFloat(e.target.value) })}
            className="w-full accent-emerald-500 bg-zinc-800 rounded-lg cursor-pointer h-1.5"
          />
        </div>
      </div>

      {/* Section 3: Financial Rates */}
      <div className="p-4 rounded-2xl bg-zinc-900/80 border border-zinc-800 backdrop-blur-sm space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-zinc-300">
          <DollarSign className="w-4 h-4 text-emerald-400" />
          <span>Municipal Simulation</span>
        </div>

        {/* Hourly Rate */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs">
            <label className="text-zinc-400 font-medium">Hourly Meter Rate</label>
            <span className="font-mono text-emerald-400 font-bold">
              ${config.hourly_rate.toFixed(2)}/hr
            </span>
          </div>
          <input
            type="range"
            min="1.00"
            max="20.00"
            step="0.50"
            value={config.hourly_rate}
            onChange={(e) => onConfigChange({ hourly_rate: parseFloat(e.target.value) })}
            className="w-full accent-emerald-500 bg-zinc-800 rounded-lg cursor-pointer h-1.5"
          />
        </div>

        {/* Total Capacity */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs">
            <label className="text-zinc-400 font-medium">Curb Capacity</label>
            <span className="font-mono text-zinc-300 font-bold">{config.total_capacity} spots</span>
          </div>
          <input
            type="range"
            min="1"
            max="20"
            step="1"
            value={config.total_capacity}
            onChange={(e) => onConfigChange({ total_capacity: parseInt(e.target.value, 10) })}
            className="w-full accent-emerald-500 bg-zinc-800 rounded-lg cursor-pointer h-1.5"
          />
        </div>

        {/* Operating Hours */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs">
            <label className="text-zinc-400 font-medium">Enforcement Hours / Day</label>
            <span className="font-mono text-zinc-300 font-bold">
              {config.operating_hours_per_day.toFixed(1)} hrs
            </span>
          </div>
          <input
            type="range"
            min="1.0"
            max="24.0"
            step="0.5"
            value={config.operating_hours_per_day}
            onChange={(e) => onConfigChange({ operating_hours_per_day: parseFloat(e.target.value) })}
            className="w-full accent-emerald-500 bg-zinc-800 rounded-lg cursor-pointer h-1.5"
          />
        </div>
      </div>
    </aside>
  );
};
