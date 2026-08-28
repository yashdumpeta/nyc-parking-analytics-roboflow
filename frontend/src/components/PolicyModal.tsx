import { X, Landmark, FileText, AlertTriangle } from 'lucide-react';

interface PolicyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PolicyModal: React.FC<PolicyModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl rounded-2xl bg-zinc-950 border border-zinc-800 p-6 shadow-2xl space-y-5 text-zinc-300">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <Landmark className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">
                Manhattan Zone M2 Curb Policy & Fiscal Context
              </h2>
              <p className="text-xs text-zinc-400">
                NYC Department of Transportation Parking Telemetry
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-900 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Policy Content */}
        <div className="space-y-4 text-xs leading-relaxed">
          <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-400">
            About
          </h4>
          <div className="p-3.5 rounded-xl bg-zinc-900/90 border border-zinc-800 space-y-1.5">

            <div className="flex items-center gap-1.5 text-white font-semibold text-xs">
              <FileText className="w-4 h-4 text-emerald-400" />
              <span>The York Avenue Policy Disparity</span>
            </div>
            <p className="text-zinc-400">
              On the <strong className="text-zinc-200">West Curb of York Avenue (between 72nd and 73rd St, Manhattan)</strong>, parking is currently free and unrestricted outside of scheduled street sweeping. Adjacent commercial avenues and cross streets charge <strong className="text-zinc-200">Zone M2 metered rates ($5.00/hour)</strong>.
            </p>
          </div>

          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-400">
              Opportunity Cost Formulation
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 font-mono text-[11px]">
              <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800/80">
                <span className="text-zinc-500">Meter Rate:</span>
                <p className="text-emerald-400 font-bold mt-0.5">$5.00 / vehicle / hour</p>
              </div>
              <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800/80">
                <span className="text-zinc-500">Enforcement Period:</span>
                <p className="text-white font-bold mt-0.5">8:00 AM – 8:30 PM (12.5 hrs/day)</p>
              </div>
              <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800/80">
                <span className="text-zinc-500">Annual Enforcement:</span>
                <p className="text-white font-bold mt-0.5">312 days/year (Sundays free)</p>
              </div>
              <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800/80">
                <span className="text-zinc-500">Block Capacity:</span>
                <p className="text-white font-bold mt-0.5">7 designated parallel spaces</p>
              </div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-xs text-amber-200">Municipal Impact</p>
              <p className="text-[11px] text-amber-300/80 mt-0.5">
                At full occupancy, leaving this single block unmetered represents an unrealized municipal subsidy exceeding <strong>$75,000 to $85,000 annually</strong> in uncollected parking revenue.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end pt-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-xs font-medium text-white transition-colors cursor-pointer"
          >
            Close Policy Guide
          </button>
        </div>
      </div>
    </div>
  );
};
