import React from 'react';
import {
  Activity,
  Zap,
  AlertTriangle,
  HeartPulse,
  ShieldCheck,
  Flame,
  ArrowUpRight,
  TrendingDown,
  Layers,
} from 'lucide-react';
import { SimulationMetrics, InfrastructureNetwork, EventLogEntry } from '../types';

interface OverviewProps {
  metrics: SimulationMetrics | null;
  network: InfrastructureNetwork | null;
  events: EventLogEntry[];
  onNavigate: (page: any) => void;
}

export const Overview: React.FC<OverviewProps> = ({
  metrics,
  network,
  events,
  onNavigate,
}) => {
  if (!metrics || !network) {
    return (
      <div className="flex h-full items-center justify-center text-zinc-500">
        Loading infrastructure telemetry...
      </div>
    );
  }

  const isCriticalLoss = metrics.critical_facilities_unserved > 0;
  const loadPercentage = Math.round((metrics.total_supplied_power / Math.max(1, metrics.total_demand)) * 100);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto overflow-y-auto h-full">
      {/* Top Banner Alert if grid is failing */}
      {metrics.unserved_demand > 0.1 && (
        <div className="p-4 rounded-xl bg-red-950/30 border border-red-500/40 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-red-500/20 text-red-400">
              <AlertTriangle className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="text-sm font-semibold text-red-300">
                Infrastructure Disruption Detected: {metrics.unserved_demand.toFixed(1)} MW Unserved Demand
              </div>
              <div className="text-xs text-red-400/80">
                {metrics.critical_facilities_unserved} critical health/emergency facilities affected. AI recovery recommended.
              </div>
            </div>
          </div>
          <button
            onClick={() => onNavigate('recovery')}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-red-600 hover:bg-red-500 text-white flex items-center space-x-1.5 shadow-lg shadow-red-900/20 transition-colors"
          >
            <span>Launch AI Recovery</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* KPI Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Reliability */}
        <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-2">
          <div className="flex items-center justify-between text-zinc-400 text-xs">
            <span>Grid Reliability</span>
            <ShieldCheck className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-zinc-100">
            {metrics.grid_reliability_index.toFixed(1)}%
          </div>
          <div className="text-[11px] text-zinc-500">Composite availability index</div>
        </div>

        {/* Card 2: Total Demand vs Supplied */}
        <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-2">
          <div className="flex items-center justify-between text-zinc-400 text-xs">
            <span>Power Supplied</span>
            <Zap className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-zinc-100">
            {metrics.total_supplied_power.toFixed(1)}{' '}
            <span className="text-sm font-normal text-zinc-400">/ {metrics.total_demand.toFixed(1)} MW</span>
          </div>
          <div className="text-[11px] text-zinc-500">{loadPercentage}% of consumer demand met</div>
        </div>

        {/* Card 3: Critical Facilities */}
        <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-2">
          <div className="flex items-center justify-between text-zinc-400 text-xs">
            <span>Critical Facilities (Hospitals)</span>
            <HeartPulse className={`w-4 h-4 ${isCriticalLoss ? 'text-red-400 animate-pulse' : 'text-emerald-400'}`} />
          </div>
          <div className="text-2xl font-bold font-mono text-zinc-100">
            {metrics.critical_facilities_supplied}{' '}
            <span className="text-sm font-normal text-zinc-400">/ {metrics.critical_facilities_total} Active</span>
          </div>
          <div className={`text-[11px] ${isCriticalLoss ? 'text-red-400 font-medium' : 'text-zinc-500'}`}>
            {metrics.critical_unserved_demand > 0
              ? `${metrics.critical_unserved_demand.toFixed(1)} MW deficit`
              : '100% priority power ensured'}
          </div>
        </div>

        {/* Card 4: Component Health */}
        <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-2">
          <div className="flex items-center justify-between text-zinc-400 text-xs">
            <span>Equipment Status</span>
            <Activity className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-zinc-100">
            {metrics.operational_components_count}{' '}
            <span className="text-sm font-normal text-zinc-400">/ {metrics.failed_components_count} Failed</span>
          </div>
          <div className="text-[11px] text-zinc-500">
            {metrics.overloaded_lines_count > 0
              ? `${metrics.overloaded_lines_count} transmission line(s) overloaded`
              : 'All transmission lines within limits'}
          </div>
        </div>
      </div>

      {/* Grid Status Split Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Component Categories Breakdown */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-surface border border-surface-border space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-surface-border">
            <div className="flex items-center space-x-2">
              <Layers className="w-4 h-4 text-blue-400" />
              <span className="text-sm font-semibold text-zinc-100">Network Operational Inventory</span>
            </div>
            <button
              onClick={() => onNavigate('map')}
              className="text-xs text-blue-400 hover:text-blue-300 flex items-center space-x-1"
            >
              <span>View Map</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border/50">
              <div className="text-zinc-500 mb-1">Power Stations</div>
              <div className="font-mono text-base font-bold text-zinc-100">
                {network.power_stations.filter(p => p.operational_status === 'operational').length} / {network.power_stations.length}
              </div>
              <div className="text-[10px] text-zinc-400">{metrics.current_generation} MW Dispatched</div>
            </div>

            <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border/50">
              <div className="text-zinc-500 mb-1">Substations</div>
              <div className="font-mono text-base font-bold text-zinc-100">
                {network.substations.filter(s => s.operational_status === 'operational').length} / {network.substations.length}
              </div>
              <div className="text-[10px] text-zinc-400">Avg Temp: {metrics.system_health_average}°C</div>
            </div>

            <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border/50">
              <div className="text-zinc-500 mb-1">Transmission Lines</div>
              <div className="font-mono text-base font-bold text-zinc-100">
                {network.transmission_lines.filter(l => l.operational_status === 'operational').length} / {network.transmission_lines.length}
              </div>
              <div className="text-[10px] text-zinc-400">{metrics.overloaded_lines_count} Overloaded</div>
            </div>

            <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border/50">
              <div className="text-zinc-500 mb-1">Backup Generators</div>
              <div className="font-mono text-base font-bold text-zinc-100">
                {network.backup_generators.filter(g => g.is_active).length} / {network.backup_generators.length} Active
              </div>
              <div className="text-[10px] text-purple-400 font-mono">
                {network.backup_generators.reduce((sum, g) => sum + g.current_utilization, 0)} MW Dispatched
              </div>
            </div>
          </div>

          {/* Substations Table */}
          <div className="pt-2">
            <div className="text-xs font-semibold text-zinc-400 mb-2">Substation Telemetry & Fuzzy Risk</div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-surface-border text-zinc-500 text-[11px]">
                    <th className="pb-2">Substation</th>
                    <th className="pb-2">Load</th>
                    <th className="pb-2">Health</th>
                    <th className="pb-2">Temperature</th>
                    <th className="pb-2">Fuzzy Risk</th>
                    <th className="pb-2">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-border/40 text-zinc-300">
                  {network.substations.map((sub) => (
                    <tr key={sub.id} className="hover:bg-surface-subtle/50">
                      <td className="py-2 font-sans font-medium text-zinc-200">{sub.id} - {sub.name}</td>
                      <td className="py-2">{sub.current_load} / {sub.max_capacity} MW</td>
                      <td className="py-2">{sub.health_percentage}%</td>
                      <td className="py-2">{sub.temperature}°C</td>
                      <td className="py-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] ${
                          sub.risk_score > 70 ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                          sub.risk_score > 40 ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                          'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        }`}>
                          {sub.risk_score.toFixed(0)} ({sub.risk_category})
                        </span>
                      </td>
                      <td className="py-2 uppercase text-[11px] font-semibold">
                        <span className={sub.operational_status === 'failed' ? 'text-red-400' : 'text-emerald-400'}>
                          {sub.operational_status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right: Recent Events Feed */}
        <div className="p-5 rounded-xl bg-surface border border-surface-border space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between pb-3 border-b border-surface-border">
              <span className="text-sm font-semibold text-zinc-100">Chronological Event Feed</span>
              <span className="text-[11px] font-mono text-zinc-500">{events.length} Events</span>
            </div>

            {events.length === 0 ? (
              <div className="py-12 text-center text-xs text-zinc-500 space-y-1">
                <ShieldCheck className="w-8 h-8 text-zinc-600 mx-auto" />
                <div>System operating in equilibrium.</div>
                <div>No failures injected yet.</div>
              </div>
            ) : (
              <div className="space-y-3 overflow-y-auto max-h-[380px] pr-1">
                {events.map((e) => (
                  <div key={e.id} className="p-3 rounded-lg bg-surface-subtle border border-surface-border/60 text-xs space-y-1">
                    <div className="flex items-center justify-between font-mono text-[10px] text-zinc-400">
                      <span>{e.timestamp}</span>
                      <span className="text-red-400 uppercase font-semibold">{e.event_type.replace('_', ' ')}</span>
                    </div>
                    <div className="font-semibold text-zinc-200">{e.component_name}</div>
                    <div className="text-[11px] text-zinc-400 leading-snug">{e.description}</div>
                    {e.secondary_effects.length > 0 && (
                      <div className="text-[10px] text-amber-400/90 pt-1 font-mono">
                        Cascade: {e.secondary_effects[0]}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="pt-3 border-t border-surface-border flex items-center space-x-2">
            <button
              onClick={() => onNavigate('simulator')}
              className="w-1/2 py-2 rounded-lg text-xs font-medium bg-surface-subtle hover:bg-surface-muted text-zinc-200 border border-surface-border text-center transition-colors"
            >
              Inject Failure
            </button>
            <button
              onClick={() => onNavigate('recovery')}
              className="w-1/2 py-2 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white text-center transition-colors"
            >
              AI Recovery Pipeline
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
