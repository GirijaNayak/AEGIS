import React from 'react';
import { X, PlayCircle, ShieldCheck, ArrowRight, Zap, CheckCircle } from 'lucide-react';

interface DemoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectScenario: (scenarioId: string) => void;
  onNavigate: (page: any) => void;
}

export const DemoModal: React.FC<DemoModalProps> = ({
  isOpen,
  onClose,
  onSelectScenario,
  onNavigate,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-surface border border-surface-border rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-5 animate-in fade-in zoom-in-95 duration-150">
        {/* Modal Header */}
        <div className="flex items-center justify-between pb-3 border-b border-surface-border">
          <div className="flex items-center space-x-2">
            <PlayCircle className="w-5 h-5 text-blue-400" />
            <h2 className="text-base font-bold text-zinc-100">AEGIS Viva Presentation & Demo Walkthrough</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-surface-subtle text-zinc-400 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Viva Guide Body */}
        <div className="space-y-4 text-xs text-zinc-300">
          <p className="text-zinc-400 leading-relaxed">
            Welcome to the demonstration mode for AEGIS. Follow this suggested viva examination path to demonstrate each AI topic in action:
          </p>

          <div className="space-y-2.5 font-mono text-[11px]">
            {/* Step 1 */}
            <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border flex items-start space-x-3">
              <span className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                1
              </span>
              <div className="space-y-1">
                <div className="font-semibold text-zinc-200">Inject Fault: Scenario A (SUB3 Failure)</div>
                <div className="text-zinc-400 font-sans text-xs">
                  Trips Metro Core Substation, cutting power to St. Jude Hospital. Shows cascading detection and unserved demand.
                </div>
                <button
                  onClick={() => {
                    onSelectScenario('scenario_a');
                    onClose();
                  }}
                  className="mt-1 px-3 py-1 rounded bg-blue-600/20 text-blue-400 border border-blue-500/30 hover:bg-blue-600/30 transition-colors inline-flex items-center space-x-1"
                >
                  <span>Launch Scenario A</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>

            {/* Step 2 */}
            <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border flex items-start space-x-3">
              <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                2
              </span>
              <div className="space-y-1">
                <div className="font-semibold text-zinc-200">Observe Multi-Stage AI Recovery</div>
                <div className="text-zinc-400 font-sans text-xs">
                  Inspect Fuzzy Risk scores, trace A* search exploration set ($g + h$), and view Genetic Algorithm convergence across generations.
                </div>
                <button
                  onClick={() => {
                    onNavigate('recovery');
                    onClose();
                  }}
                  className="mt-1 px-3 py-1 rounded bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-600/30 transition-colors inline-flex items-center space-x-1"
                >
                  <span>Go to AI Recovery</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>

            {/* Step 3 */}
            <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border flex items-start space-x-3">
              <span className="w-5 h-5 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                3
              </span>
              <div className="space-y-1">
                <div className="font-semibold text-zinc-200">Independent Algorithm Laboratory</div>
                <div className="text-zinc-400 font-sans text-xs">
                  Directly manipulate Fuzzy membership curves, test A* heuristic admissibility, and tune GA mutation rates.
                </div>
                <button
                  onClick={() => {
                    onNavigate('lab');
                    onClose();
                  }}
                  className="mt-1 px-3 py-1 rounded bg-purple-600/20 text-purple-400 border border-purple-500/30 hover:bg-purple-600/30 transition-colors inline-flex items-center space-x-1"
                >
                  <span>Open Algorithm Lab</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-surface-subtle hover:bg-surface-muted text-zinc-300 border border-surface-border transition-colors"
          >
            Close Walkthrough
          </button>
        </div>
      </div>
    </div>
  );
};
