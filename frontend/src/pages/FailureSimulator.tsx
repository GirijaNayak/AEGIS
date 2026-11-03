import React, { useState } from 'react';
import {
  AlertTriangle,
  ZapOff,
  Flame,
  RotateCcw,
  Sliders,
  ChevronRight,
  ShieldAlert,
  ArrowRight,
} from 'lucide-react';
import { InfrastructureNetwork, EventLogEntry, SimulationMetrics } from '../types';
import { api } from '../services/api';

interface FailureSimulatorProps {
  network: InfrastructureNetwork | null;
  metrics: SimulationMetrics | null;
  events: EventLogEntry[];
  onRefreshState: () => void;
}

export const FailureSimulator: React.FC<FailureSimulatorProps> = ({
  network,
  metrics,
  events,
  onRefreshState,
}) => {
  const [selectedComponentId, setSelectedComponentId] = useState<string>('SUB3');
  const [failureType, setFailureType] = useState<string>('substation_failure');
  const [severity, setSeverity] = useState<number>(1.0);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Grouped components for dropdown
  const allComponents = [
    ...(network?.substations.map(s => ({ id: s.id, name: `${s.id} - ${s.name}`, type: 'substation', defaultType: 'substation_failure' })) || []),
    ...(network?.power_stations.map(p => ({ id: p.id, name: `${p.id} - ${p.name}`, type: 'power_station', defaultType: 'power_station_failure' })) || []),
    ...(network?.transmission_lines.map(l => ({ id: l.id, name: `Line ${l.id} (${l.source_id}->${l.destination_id})`, type: 'transmission_line', defaultType: 'transmission_line_failure' })) || []),
  ];

  const handleComponentChange = (id: string) => {
    setSelectedComponentId(id);
    const comp = allComponents.find(c => c.id === id);
    if (comp) {
      setFailureType(comp.defaultType);
    }
  };

  const handleTriggerFailure = async () => {
    setIsSubmitting(true);
    try {
      const comp = allComponents.find(c => c.id === selectedComponentId);
      const cType = comp?.type || 'substation';
      await api.triggerFailure(selectedComponentId, cType, failureType, severity);
      onRefreshState();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleLoadPreset = async (presetId: string) => {
    setIsSubmitting(true);
    try {
      await api.loadPreset(presetId);
      onRefreshState();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = async () => {
    setIsSubmitting(true);
    try {
      await api.resetSimulation();
      onRefreshState();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const latestEvent = events.length > 0 ? events[0] : null;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto overflow-y-auto h-full">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-surface-border">
        <div>
          <h1 className="text-lg font-bold text-zinc-100 flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-accent-red" />
            <span>Infrastructure Failure Injection & Cascade Simulator</span>
          </h1>
          <p className="text-xs text-zinc-400 mt-1">
            Simulate primary asset outages, capacity degradations, and thermal cascading overload propagation across the grid.
          </p>
        </div>
        <button
          onClick={handleReset}
          disabled={isSubmitting}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-surface-subtle hover:bg-surface-muted text-zinc-300 border border-surface-border transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Grid Scenario</span>
        </button>
      </div>

      {/* Preset Scenario Quick Selectors */}
      <div className="space-y-2">
        <div className="text-xs font-semibold text-zinc-400 uppercase tracking-wide">
          Standardized Academic Demo Scenarios
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          <button
            onClick={() => handleLoadPreset('scenario_a')}
            disabled={isSubmitting}
            className="p-3.5 rounded-xl bg-surface hover:bg-surface-subtle border border-surface-border text-left transition-all hover:border-blue-500/50 space-y-1.5"
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400">Preset A</span>
              <ChevronRight className="w-3.5 h-3.5 text-zinc-500" />
            </div>
            <div className="text-xs font-semibold text-zinc-100">Substation Failure (SUB3)</div>
            <div className="text-[11px] text-zinc-400">Transformer explosion isolates Metro Core and St. Jude Hospital.</div>
          </button>

          <button
            onClick={() => handleLoadPreset('scenario_b')}
            disabled={isSubmitting}
            className="p-3.5 rounded-xl bg-surface hover:bg-surface-subtle border border-surface-border text-left transition-all hover:border-amber-500/50 space-y-1.5"
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400">Preset B</span>
              <ChevronRight className="w-3.5 h-3.5 text-zinc-500" />
            </div>
            <div className="text-xs font-semibold text-zinc-100">Transmission Corridor Cut (TL1 & TL6)</div>
            <div className="text-[11px] text-zinc-400">Double line collapse cuts northern transmission trunk lines.</div>
          </button>

          <button
            onClick={() => handleLoadPreset('scenario_c')}
            disabled={isSubmitting}
            className="p-3.5 rounded-xl bg-surface hover:bg-surface-subtle border border-surface-border text-left transition-all hover:border-red-500/50 space-y-1.5"
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-red-500/20 text-red-400">Preset C</span>
              <ChevronRight className="w-3.5 h-3.5 text-zinc-500" />
            </div>
            <div className="text-xs font-semibold text-zinc-100">Power Station Loss (PS1 450MW)</div>
            <div className="text-[11px] text-zinc-400">Loss of 55% regional generation triggers catastrophic deficit.</div>
          </button>

          <button
            onClick={() => handleLoadPreset('scenario_d')}
            disabled={isSubmitting}
            className="p-3.5 rounded-xl bg-surface hover:bg-surface-subtle border border-surface-border text-left transition-all hover:border-purple-500/50 space-y-1.5"
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-400">Preset D</span>
              <ChevronRight className="w-3.5 h-3.5 text-zinc-500" />
            </div>
            <div className="text-xs font-semibold text-zinc-100">Hospital Emergency (SUB6 Trauma)</div>
            <div className="text-[11px] text-zinc-400">Westside Trauma Center loses primary grid connection.</div>
          </button>
        </div>
      </div>

      {/* Manual Failure Injection Form & Cascading Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Manual Controls */}
        <div className="p-5 rounded-xl bg-surface border border-surface-border space-y-4">
          <div className="flex items-center space-x-2 pb-3 border-b border-surface-border">
            <Sliders className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-semibold text-zinc-100">Custom Failure Injector</span>
          </div>

          <div className="space-y-3 text-xs">
            {/* Component Selector */}
            <div>
              <label className="text-zinc-400 block mb-1">Target Component</label>
              <select
                value={selectedComponentId}
                onChange={(e) => handleComponentChange(e.target.value)}
                className="w-full p-2.5 rounded-lg bg-surface-subtle border border-surface-border text-zinc-200 focus:outline-none focus:border-blue-500"
              >
                {allComponents.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Failure Type */}
            <div>
              <label className="text-zinc-400 block mb-1">Failure Mode</label>
              <select
                value={failureType}
                onChange={(e) => setFailureType(e.target.value)}
                className="w-full p-2.5 rounded-lg bg-surface-subtle border border-surface-border text-zinc-200 focus:outline-none focus:border-blue-500"
              >
                <option value="substation_failure">Complete Substation Failure (Outage)</option>
                <option value="transmission_line_failure">Transmission Line Trip / Cut</option>
                <option value="power_station_failure">Power Station Turbine Trip</option>
                <option value="capacity_reduction">Capacity Derating / Degradation</option>
              </select>
            </div>

            {/* Severity Slider */}
            <div>
              <div className="flex justify-between mb-1">
                <label className="text-zinc-400">Severity</label>
                <span className="font-mono text-zinc-200">{(severity * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0.1"
                max="1.0"
                step="0.05"
                value={severity}
                onChange={(e) => setSeverity(parseFloat(e.target.value))}
                className="w-full accent-blue-500"
              />
            </div>

            {/* Trigger Button */}
            <div className="pt-2">
              <button
                onClick={handleTriggerFailure}
                disabled={isSubmitting}
                className="w-full py-2.5 rounded-lg text-xs font-semibold bg-red-600 hover:bg-red-500 text-white flex items-center justify-center space-x-2 shadow-lg shadow-red-900/30 transition-colors disabled:opacity-50"
              >
                <ZapOff className="w-4 h-4" />
                <span>Inject Fault & Trigger Cascade</span>
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Cascading Timeline & Impact Analysis */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-surface border border-surface-border space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-surface-border">
            <div className="flex items-center space-x-2">
              <Flame className="w-4 h-4 text-accent-amber" />
              <span className="text-sm font-semibold text-zinc-100">Cascading Failure Propagation Sequence</span>
            </div>
            {latestEvent && (
              <span className="text-[11px] font-mono text-zinc-400">{latestEvent.timestamp}</span>
            )}
          </div>

          {!latestEvent || latestEvent.cascading_steps.length === 0 ? (
            <div className="py-12 text-center text-xs text-zinc-500 space-y-2">
              <ShieldAlert className="w-8 h-8 text-zinc-600 mx-auto" />
              <div>No cascading trip sequence recorded in current event.</div>
              <div className="text-[11px] text-zinc-600">
                Trigger a major outage (e.g. Preset B or C) to observe thermal overload cascade tripping.
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="text-xs text-zinc-400">
                Primary fault on <span className="text-zinc-200 font-semibold">{latestEvent.component_name}</span> triggered{' '}
                <span className="text-accent-red font-semibold">{latestEvent.cascading_steps.length} sequential secondary trips</span> due to electrical thermal overload limits.
              </div>

              {/* Timeline Steps */}
              <div className="space-y-2.5">
                {latestEvent.cascading_steps.map((step) => (
                  <div
                    key={step.step_number}
                    className="p-3 rounded-lg bg-surface-subtle border border-red-500/20 text-xs space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 font-semibold">
                        Cascade Step {step.step_number}
                      </span>
                      <span className="font-mono text-red-400 font-bold">{step.overload_percentage}% Overload</span>
                    </div>
                    <div className="font-semibold text-zinc-200 flex items-center space-x-2">
                      <span>{step.component_name}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-zinc-500" />
                      <span className="text-red-400 uppercase font-mono">{step.new_status}</span>
                    </div>
                    <div className="text-[11px] text-zinc-400 leading-snug">{step.event_reason}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Current Post-Failure Impact Summary */}
          {metrics && (
            <div className="pt-3 border-t border-surface-border grid grid-cols-3 gap-3 text-xs font-mono">
              <div className="p-2.5 rounded bg-surface-subtle border border-surface-border/50">
                <span className="text-zinc-500 block text-[10px]">Unserved Demand:</span>
                <span className="text-red-400 font-bold text-sm">{metrics.unserved_demand} MW</span>
              </div>
              <div className="p-2.5 rounded bg-surface-subtle border border-surface-border/50">
                <span className="text-zinc-500 block text-[10px]">Hospitals Offline:</span>
                <span className="text-red-400 font-bold text-sm">{metrics.critical_facilities_unserved} Facilities</span>
              </div>
              <div className="p-2.5 rounded bg-surface-subtle border border-surface-border/50">
                <span className="text-zinc-500 block text-[10px]">Overloaded Lines:</span>
                <span className="text-amber-400 font-bold text-sm">{metrics.overloaded_lines_count} Lines</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
