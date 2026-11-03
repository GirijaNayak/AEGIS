import React, { useState } from 'react';
import { InfrastructureGraph } from '../components/map/InfrastructureGraph';
import { InfrastructureNetwork, SimulationMetrics } from '../types';
import { Eye, ShieldAlert, Cpu, Network } from 'lucide-react';

interface InfrastructurePageProps {
  network: InfrastructureNetwork | null;
  metrics: SimulationMetrics | null;
  highlightedRouteEdges?: string[];
}

export const Infrastructure: React.FC<InfrastructurePageProps> = ({
  network,
  metrics,
  highlightedRouteEdges = [],
}) => {
  const [viewMode, setViewMode] = useState<'normal' | 'failure' | 'heatmap' | 'route'>('normal');

  if (!network) {
    return (
      <div className="flex h-full items-center justify-center text-zinc-500">
        Loading network map topology...
      </div>
    );
  }

  return (
    <div className="relative w-full h-full flex flex-col">
      {/* Top Filter & View Mode Controls Bar */}
      <div className="h-12 border-b border-surface-border bg-surface px-6 flex items-center justify-between z-10">
        <div className="flex items-center space-x-2">
          <Network className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-semibold text-zinc-200">Interactive Infrastructure Map</span>
          <span className="text-[11px] font-mono text-zinc-500">
            ({network.substations.length} Substations, {network.transmission_lines.length} Lines)
          </span>
        </div>

        {/* View Mode Switcher */}
        <div className="flex items-center p-0.5 rounded-lg bg-surface-subtle border border-surface-border text-xs font-medium">
          <button
            onClick={() => setViewMode('normal')}
            className={`px-3 py-1 rounded-md transition-colors ${
              viewMode === 'normal' ? 'bg-surface text-white shadow-sm' : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Topology View
          </button>
          <button
            onClick={() => setViewMode('failure')}
            className={`px-3 py-1 rounded-md transition-colors ${
              viewMode === 'failure' ? 'bg-surface text-accent-red shadow-sm' : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Failure Impact
          </button>
          <button
            onClick={() => setViewMode('heatmap')}
            className={`px-3 py-1 rounded-md transition-colors ${
              viewMode === 'heatmap' ? 'bg-surface text-accent-amber shadow-sm' : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Risk Heatmap
          </button>
          <button
            onClick={() => setViewMode('route')}
            className={`px-3 py-1 rounded-md transition-colors ${
              viewMode === 'route' ? 'bg-surface text-accent-cyan shadow-sm' : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            A* Alternative Route
          </button>
        </div>
      </div>

      {/* Main Interactive React Flow Map Canvas */}
      <div className="flex-1 w-full h-[calc(100%-3rem)]">
        <InfrastructureGraph
          network={network}
          highlightedPathEdges={highlightedRouteEdges}
          viewMode={viewMode}
        />
      </div>
    </div>
  );
};
