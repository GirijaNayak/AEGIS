import React, { useState, useEffect } from 'react';
import {
  FileText,
  Download,
  ShieldCheck,
  Cpu,
  Layers,
  Info,
  ExternalLink,
} from 'lucide-react';
import { api } from '../services/api';

export const Reports: React.FC = () => {
  const [reportData, setReportData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const data = await api.getReportJson();
        setReportData(data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchReport();
  }, []);

  const handleDownloadJSON = () => {
    if (!reportData) return;
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `aegis_simulation_report_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto overflow-y-auto h-full">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-surface-border">
        <div>
          <h1 className="text-lg font-bold text-zinc-100 flex items-center space-x-2">
            <FileText className="w-5 h-5 text-accent-blue" />
            <span>Technical Simulation Audit & Viva Evaluation Report</span>
          </h1>
          <p className="text-xs text-zinc-400 mt-1">
            Academic verification document summarizing grid operational state, AI algorithm decisions, and experimental outcomes.
          </p>
        </div>

        <button
          onClick={handleDownloadJSON}
          className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-surface-subtle hover:bg-surface-muted text-zinc-200 border border-surface-border transition-colors shadow-sm"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Export JSON Report</span>
        </button>
      </div>

      {isLoading ? (
        <div className="py-20 text-center text-xs text-zinc-500">
          Generating technical report...
        </div>
      ) : reportData ? (
        <div className="space-y-6 text-xs text-zinc-300">
          {/* Section 1: Executive Summary */}
          <div className="p-5 rounded-xl bg-surface border border-surface-border space-y-3">
            <div className="flex items-center space-x-2 text-sm font-semibold text-zinc-100 pb-2 border-b border-surface-border">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>1. Project Vision & Implementation Overview</span>
            </div>
            <p className="leading-relaxed text-zinc-400">
              <strong className="text-zinc-200">AEGIS</strong> is an academic college-level Artificial Intelligence simulator that models electrical transmission and distribution grids under severe asset failure conditions.
              The simulator implements three foundational, non-neural AI paradigms strictly from first principles:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1 font-mono text-[11px]">
              <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border/50">
                <span className="text-blue-400 font-bold block mb-1">Fuzzy Logic</span>
                <span className="text-zinc-400">Mamdani inference system evaluating 3 operational inputs (Load, Health, Temperature) to produce crisp 0–100 risk assessments via Centroid Defuzzification.</span>
              </div>
              <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border/50">
                <span className="text-emerald-400 font-bold block mb-1">A* Search</span>
                <span className="text-zinc-400">Admissible capacity-constrained shortest pathfinder routing power around failed substations and severed transmission lines.</span>
              </div>
              <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border/50">
                <span className="text-purple-400 font-bold block mb-1">Genetic Algorithm</span>
                <span className="text-zinc-400">Evolutionary multi-objective optimizer coordinating emergency generator dispatches, bypass line switches, and priority load shedding.</span>
              </div>
            </div>
          </div>

          {/* Section 2: Mathematical Formulation */}
          <div className="p-5 rounded-xl bg-surface border border-surface-border space-y-3">
            <div className="flex items-center space-x-2 text-sm font-semibold text-zinc-100 pb-2 border-b border-surface-border">
              <Cpu className="w-4 h-4 text-purple-400" />
              <span>2. Mathematical Models & Cost Formulation</span>
            </div>
            
            <div className="space-y-2 text-zinc-400 font-mono text-[11px]">
              <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border">
                <div className="text-zinc-200 font-semibold mb-1">GA Multi-Objective Cost Function (Minimization):</div>
                <div className="text-purple-400 font-bold">
                  Cost = w₁ · UnservedDemand + w₂ · RecoveryTime + w₃ · ResourceFuelCost + w₄ · OverloadPenalty + w₅ · CriticalHospitalPenalty
                </div>
                <div className="text-zinc-500 text-[10px] mt-1 font-sans">
                  Fitness Score = 10,000 / (1.0 + Cost). Hospitals (Critical Priority 1) receive a 50× penalty multiplier ensuring emergency services are prioritized above industrial or residential loads.
                </div>
              </div>

              <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border">
                <div className="text-zinc-200 font-semibold mb-1">A* Admissible Heuristic Formulation:</div>
                <div className="text-emerald-400 font-bold">
                  f(n) = g(n) + h(n), where h(n) = k_min · ||Position(n) - Position(goal)||₂
                </div>
                <div className="text-zinc-500 text-[10px] mt-1 font-sans">
                  Where k_min = min(TransferCost_e / Distance_e) across all physical grid edges, guaranteeing mathematical admissibility (h(n) ≤ h*(n)).
                </div>
              </div>

              <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border">
                <div className="text-zinc-200 font-semibold mb-1">Fuzzy Centroid Defuzzification:</div>
                <div className="text-blue-400 font-bold">
                  RiskScore = ( ∫ z · μ_aggregated(z) dz ) / ( ∫ μ_aggregated(z) dz ) ≈ Σ ( z_i · μ_i ) / Σ μ_i
                </div>
                <div className="text-zinc-500 text-[10px] mt-1 font-sans">
                  Evaluated across 101 discrete sample points from z = 0 to 100 with Mamdani MIN operator for rule antecedents and MAX for rule aggregation.
                </div>
              </div>
            </div>
          </div>

          {/* Section 3: Engineering Assumptions and Limitations */}
          <div className="p-5 rounded-xl bg-surface border border-surface-border space-y-3">
            <div className="flex items-center space-x-2 text-sm font-semibold text-zinc-100 pb-2 border-b border-surface-border">
              <Info className="w-4 h-4 text-amber-400" />
              <span>3. Engineering Assumptions & Academic Boundaries</span>
            </div>
            <ul className="space-y-1.5 list-disc list-inside text-zinc-400 text-xs">
              <li>
                <strong className="text-zinc-300">Simplified Network Flow Model: </strong>
                This system models active MW flow capacity constraints and thermal overload limits on a graph. It does not replace full certified AC power flow solvers (e.g. Newton-Raphson, reactive power MVAR, phase angles, or generator transient inertia).
              </li>
              <li>
                <strong className="text-zinc-300">Stochastic Heuristic Nature: </strong>
                The Genetic Algorithm converges to high-quality feasible recovery solutions but does not mathematically guarantee global optimality.
              </li>
              <li>
                <strong className="text-zinc-300">Safety & Validation: </strong>
                Every candidate solution is filtered through a physical constraint validator to ensure offline generators or severed lines are never dispatched.
              </li>
            </ul>
          </div>
        </div>
      ) : null}
    </div>
  );
};
