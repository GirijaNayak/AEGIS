import React from 'react';
import { RefreshCw, PlayCircle, ShieldCheck, AlertOctagon } from 'lucide-react';
import { SimulationMetrics } from '../../types';

interface NavbarProps {
  activeScenario: string;
  metrics: SimulationMetrics | null;
  onReset: () => void;
  onOpenDemo: () => void;
  isResetting: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeScenario,
  metrics,
  onReset,
  onOpenDemo,
  isResetting,
}) => {
  const isFailed = metrics && metrics.unserved_demand > 0.1;
  const reliability = metrics?.grid_reliability_index ?? 100;

  return (
    <header className="h-14 border-b border-surface-border bg-surface px-5 flex items-center justify-between z-20">
      {/* Left: Brand and Active Scenario */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <div className="h-6 w-6 rounded bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center font-bold text-xs text-white tracking-wider shadow-sm">
            AE
          </div>
          <span className="font-semibold text-sm tracking-tight text-zinc-100">AEGIS</span>
          <span className="text-[11px] font-mono px-1.5 py-0.5 rounded bg-surface-muted text-zinc-400 border border-surface-border">
            v1.0
          </span>
        </div>

        <div className="h-4 w-[1px] bg-surface-border" />

        <div className="flex items-center space-x-2 text-xs">
          <span className="text-zinc-500">Scenario:</span>
          <span className="font-mono text-zinc-200 truncate max-w-md bg-surface-subtle px-2 py-0.5 rounded border border-surface-border/50">
            {activeScenario}
          </span>
        </div>
      </div>

      {/* Right: Grid State & Actions */}
      <div className="flex items-center space-x-3">
        {/* Reliability Pill */}
        <div className="flex items-center space-x-2 px-2.5 py-1 rounded bg-surface-subtle border border-surface-border text-xs">
          {isFailed ? (
            <AlertOctagon className="w-3.5 h-3.5 text-accent-red animate-pulse" />
          ) : (
            <ShieldCheck className="w-3.5 h-3.5 text-accent-green" />
          )}
          <span className="text-zinc-400">Reliability:</span>
          <span className={`font-mono font-medium ${reliability < 70 ? 'text-accent-red' : reliability < 90 ? 'text-accent-amber' : 'text-accent-green'}`}>
            {reliability.toFixed(1)}%
          </span>
        </div>

        {/* Viva Demo Button */}
        <button
          onClick={onOpenDemo}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium bg-blue-600/10 text-blue-400 border border-blue-500/30 hover:bg-blue-600/20 transition-colors"
        >
          <PlayCircle className="w-3.5 h-3.5" />
          <span>Demo Walkthrough</span>
        </button>

        {/* Reset Environment */}
        <button
          onClick={onReset}
          disabled={isResetting}
          title="Reset infrastructure to baseline"
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium bg-surface-subtle text-zinc-300 border border-surface-border hover:bg-surface-muted hover:text-white transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isResetting ? 'animate-spin' : ''}`} />
          <span>Reset Grid</span>
        </button>
      </div>
    </header>
  );
};
