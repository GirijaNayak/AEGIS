import React, { useState, useEffect } from 'react';
import {
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Play,
  RotateCw,
  GitBranch,
  Layers,
  ArrowRight,
  TrendingDown,
  Sparkles,
  ShieldCheck,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import {
  RecoveryAnalysisResponse,
  RecoveryExecutionResponse,
  SimulationMetrics,
  InfrastructureNetwork,
} from '../types';
import { api } from '../services/api';

interface AIRecoveryProps {
  network: InfrastructureNetwork | null;
  metrics: SimulationMetrics | null;
  onRefreshState: () => void;
  onHighlightRoute: (edges: string[]) => void;
}

export const AIRecovery: React.FC<AIRecoveryProps> = ({
  network,
  metrics,
  onRefreshState,
  onHighlightRoute,
}) => {
  const [analysisData, setAnalysisData] = useState<RecoveryAnalysisResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [executionResult, setExecutionResult] = useState<RecoveryExecutionResponse | null>(null);
  const [activeStepTab, setActiveStepTab] = useState<'fuzzy' | 'astar' | 'ga'>('ga');

  const runAnalysis = async () => {
    setIsAnalyzing(true);
    setExecutionResult(null);
    try {
      const res = await api.analyzeRecovery();
      setAnalysisData(res);
      // If A* found routes, highlight first route
      if (res.alternative_astar_routes.length > 0) {
        onHighlightRoute(res.alternative_astar_routes[0].path_edges);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  useEffect(() => {
    // Automatically trigger analysis if not analyzed yet
    if (!analysisData && !isAnalyzing) {
      runAnalysis();
    }
  }, []);

  const handleExecute = async () => {
    if (!analysisData?.recommended_ga_plan) return;
    setIsExecuting(true);
    try {
      const res = await api.executeRecovery(analysisData.recommended_ga_plan.best_chromosome);
      setExecutionResult(res);
      onRefreshState();
    } catch (err) {
      console.error(err);
    } finally {
      setIsExecuting(false);
    }
  };

  const gaPlan = analysisData?.recommended_ga_plan;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto overflow-y-auto h-full">
      {/* Top Header */}
      <div className="flex items-center justify-between pb-4 border-b border-surface-border">
        <div>
          <h1 className="text-lg font-bold text-zinc-100 flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-accent-purple" />
            <span>AI Automated Infrastructure Recovery Pipeline</span>
          </h1>
          <p className="text-xs text-zinc-400 mt-1">
            Triages failure severity via <strong className="text-blue-400">Fuzzy Logic</strong>, computes bypass corridors via <strong className="text-emerald-400">A* Search</strong>, and optimizes multi-objective recovery decisions via a <strong className="text-purple-400">Genetic Algorithm</strong>.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={runAnalysis}
            disabled={isAnalyzing}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-surface-subtle hover:bg-surface-muted text-zinc-300 border border-surface-border transition-colors disabled:opacity-50"
          >
            <RotateCw className={`w-3.5 h-3.5 ${isAnalyzing ? 'animate-spin' : ''}`} />
            <span>Re-run AI Pipeline</span>
          </button>

          {gaPlan && !executionResult && (
            <button
              onClick={handleExecute}
              disabled={isExecuting || !gaPlan.is_valid}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-900/30 transition-all disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Apply Recommended Plan</span>
            </button>
          )}
        </div>
      </div>

      {/* Execution Improvement Banner (if executed) */}
      {executionResult && (
        <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/40 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-emerald-500/20 text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-semibold text-emerald-300">
                Recovery Plan Applied Successfully
              </div>
              <div className="text-xs text-emerald-400/80">
                Restored {executionResult.improvements.unserved_demand_recovered_mw} MW unserved demand (+{executionResult.improvements.reliability_index_gain}% Grid Reliability gain).
              </div>
            </div>
          </div>
          <span className="text-xs font-mono px-3 py-1 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-semibold">
            STATUS: ACTIVE IN SIMULATION
          </span>
        </div>
      )}

      {/* 5-Step Pipeline Breadcrumb */}
      <div className="grid grid-cols-5 gap-2 text-xs">
        <div className="p-3 rounded-lg bg-surface border border-blue-500/30">
          <div className="text-[10px] font-mono text-blue-400 font-semibold">STEP 1</div>
          <div className="font-semibold text-zinc-100">Failure Analysis</div>
          <div className="text-[10px] text-zinc-400 mt-1">
            {analysisData ? `${analysisData.failed_components.length} Failed Assets` : 'Detecting...'}
          </div>
        </div>

        <div className={`p-3 rounded-lg bg-surface border ${activeStepTab === 'fuzzy' ? 'border-blue-500' : 'border-surface-border'} cursor-pointer`}
          onClick={() => setActiveStepTab('fuzzy')}
        >
          <div className="text-[10px] font-mono text-blue-400 font-semibold">STEP 2 (AI)</div>
          <div className="font-semibold text-zinc-100">Fuzzy Risk Score</div>
          <div className="text-[10px] text-zinc-400 mt-1">Mamdani Inference</div>
        </div>

        <div className={`p-3 rounded-lg bg-surface border ${activeStepTab === 'astar' ? 'border-emerald-500' : 'border-surface-border'} cursor-pointer`}
          onClick={() => setActiveStepTab('astar')}
        >
          <div className="text-[10px] font-mono text-emerald-400 font-semibold">STEP 3 (AI)</div>
          <div className="font-semibold text-zinc-100">A* Pathfinding</div>
          <div className="text-[10px] text-zinc-400 mt-1">Admissible Routing</div>
        </div>

        <div className={`p-3 rounded-lg bg-surface border ${activeStepTab === 'ga' ? 'border-purple-500' : 'border-surface-border'} cursor-pointer`}
          onClick={() => setActiveStepTab('ga')}
        >
          <div className="text-[10px] font-mono text-purple-400 font-semibold">STEP 4 (AI)</div>
          <div className="font-semibold text-zinc-100">Genetic Optimizer</div>
          <div className="text-[10px] text-zinc-400 mt-1">Multi-Objective Cost</div>
        </div>

        <div className="p-3 rounded-lg bg-surface border border-surface-border">
          <div className="text-[10px] font-mono text-zinc-500 font-semibold">STEP 5</div>
          <div className="font-semibold text-zinc-100">Constraint Validation</div>
          <div className="text-[10px] text-emerald-400 mt-1 font-mono">
            {gaPlan?.is_valid ? 'Constraints Passed' : 'Checking'}
          </div>
        </div>
      </div>

      {/* Main Algorithm Detail Panels */}
      {isAnalyzing ? (
        <div className="py-20 text-center text-xs text-zinc-500 space-y-2">
          <Cpu className="w-8 h-8 text-blue-500 animate-spin mx-auto" />
          <div className="text-zinc-300 font-semibold">Executing AI Inference Engine...</div>
          <div className="text-zinc-500 font-mono text-[11px]">Fuzzy evaluation → A* Open/Closed set exploration → GA Multi-generation convergence</div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* TAB 1: FUZZY LOGIC INSPECTOR */}
          {activeStepTab === 'fuzzy' && analysisData && (
            <div className="p-5 rounded-xl bg-surface border border-surface-border space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-surface-border">
                <div className="flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4 text-blue-400" />
                  <span className="text-sm font-semibold text-zinc-100">Fuzzy Logic Infrastructure Risk Assessment (Mamdani Model)</span>
                </div>
                <span className="text-xs font-mono text-zinc-400">Centroid Defuzzification Method</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {analysisData.fuzzy_risk_assessments.map((f) => (
                  <div key={f.component_id} className="p-4 rounded-lg bg-surface-subtle border border-surface-border text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-zinc-200">{f.component_name}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        f.risk_category === 'Critical' ? 'bg-red-500/20 text-red-400 border border-red-500/40' :
                        f.risk_category === 'High' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40' :
                        'bg-blue-500/20 text-blue-400 border border-blue-500/40'
                      }`}>
                        {f.defuzzified_risk_score} ({f.risk_category})
                      </span>
                    </div>

                    <div className="font-mono text-[11px] text-zinc-400 space-y-0.5 pt-1 border-t border-surface-border/50">
                      <div>Load: {f.inputs.load_percentage}% (Low:{f.load_memberships.low}, Med:{f.load_memberships.medium}, High:{f.load_memberships.high})</div>
                      <div>Health: {f.inputs.health_percentage}% (Poor:{f.health_memberships.poor}, Avg:{f.health_memberships.average}, Good:{f.health_memberships.good})</div>
                      <div>Temp: {f.inputs.temperature}°C (Norm:{f.temperature_memberships.normal}, Elev:{f.temperature_memberships.elevated}, Crit:{f.temperature_memberships.critical})</div>
                    </div>

                    <div className="pt-2 text-[10px] text-zinc-400 leading-snug">
                      <strong className="text-zinc-300">Strongest Rules: </strong>
                      {f.activated_rules.slice(0, 2).map(r => `Rule #${r.rule_id} (${r.consequent})`).join(', ')}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 2: A* SEARCH INSPECTOR */}
          {activeStepTab === 'astar' && analysisData && (
            <div className="p-5 rounded-xl bg-surface border border-surface-border space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-surface-border">
                <div className="flex items-center space-x-2">
                  <GitBranch className="w-4 h-4 text-emerald-400" />
                  <span className="text-sm font-semibold text-zinc-100">A* Search Alternative Route Discovery</span>
                </div>
                <span className="text-xs font-mono text-zinc-400">Admissible Heuristic: f(n) = g(n) + h(n)</span>
              </div>

              {analysisData.alternative_astar_routes.length === 0 ? (
                <div className="py-12 text-center text-xs text-zinc-500">
                  No alternative transmission bypass routes needed or available.
                </div>
              ) : (
                <div className="space-y-4">
                  {analysisData.alternative_astar_routes.map((route, idx) => (
                    <div key={idx} className="p-4 rounded-lg bg-surface-subtle border border-surface-border space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2 text-xs font-semibold text-zinc-200">
                          <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-mono">Route #{idx + 1}</span>
                          <span>{route.source_id} <ArrowRight className="inline w-3 h-3 text-zinc-500 mx-1" /> {route.destination_id}</span>
                        </div>
                        <button
                          onClick={() => onHighlightRoute(route.path_edges)}
                          className="px-2.5 py-1 rounded text-[11px] font-mono bg-blue-600/20 text-blue-300 border border-blue-500/30 hover:bg-blue-600/30 transition-colors"
                        >
                          Highlight on Map
                        </button>
                      </div>

                      <div className="text-xs font-mono text-zinc-300">
                        Path: <span className="text-emerald-400 font-bold">{route.path_nodes.join(' → ')}</span>
                      </div>

                      <div className="grid grid-cols-4 gap-2 text-xs font-mono">
                        <div className="p-2 rounded bg-surface border border-surface-border/50">
                          <span className="text-zinc-500 text-[10px] block">Total Cost g(goal):</span>
                          <span className="text-zinc-200">{route.total_cost}</span>
                        </div>
                        <div className="p-2 rounded bg-surface border border-surface-border/50">
                          <span className="text-zinc-500 text-[10px] block">Bottleneck Capacity:</span>
                          <span className="text-emerald-400">{route.bottleneck_capacity_mw} MW</span>
                        </div>
                        <div className="p-2 rounded bg-surface border border-surface-border/50">
                          <span className="text-zinc-500 text-[10px] block">Nodes Explored:</span>
                          <span className="text-zinc-200">{route.nodes_explored_count}</span>
                        </div>
                        <div className="p-2 rounded bg-surface border border-surface-border/50">
                          <span className="text-zinc-500 text-[10px] block">Distance:</span>
                          <span className="text-zinc-200">{route.total_distance_km} km</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 3: GENETIC ALGORITHM OPTIMIZER */}
          {activeStepTab === 'ga' && gaPlan && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left 2 Cols: Convergence Chart & Chromosome Breakdown */}
              <div className="lg:col-span-2 p-5 rounded-xl bg-surface border border-surface-border space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-surface-border">
                  <div className="flex items-center space-x-2">
                    <Sparkles className="w-4 h-4 text-purple-400" />
                    <span className="text-sm font-semibold text-zinc-100">Genetic Algorithm Convergence (Generations vs Fitness)</span>
                  </div>
                  <span className="text-xs font-mono text-zinc-400">
                    Runtime: {gaPlan.execution_time_ms} ms
                  </span>
                </div>

                {/* Recharts Convergence Chart */}
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={gaPlan.generations_history} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#262b3d" />
                      <XAxis dataKey="generation" stroke="#71717a" fontSize={10} label={{ value: 'Generation', position: 'insideBottom', offset: -5, fill: '#71717a', fontSize: 10 }} />
                      <YAxis stroke="#71717a" fontSize={10} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#111318', borderColor: '#262b3d', borderRadius: '8px', fontSize: '11px', fontFamily: 'monospace' }}
                      />
                      <Line type="monotone" dataKey="best_cost" stroke="#a855f7" strokeWidth={2} name="Best Objective Cost (lower is better)" dot={false} />
                      <Line type="monotone" dataKey="unserved_demand_mw" stroke="#ef4444" strokeWidth={1.5} name="Unserved Demand (MW)" dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {/* Optimal Decision Variables (Chromosome) */}
                <div className="space-y-2 pt-2">
                  <div className="text-xs font-semibold text-zinc-300">Recommended Chromosome Actions</div>
                  
                  {/* Backup Generators */}
                  <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border space-y-1 text-xs font-mono">
                    <span className="text-purple-400 font-semibold block mb-1">Backup Generator Dispatch:</span>
                    <div className="grid grid-cols-2 gap-2 text-zinc-300">
                      {Object.entries(gaPlan.best_chromosome.generator_dispatch).map(([k, v]) => (
                        <div key={k} className="flex justify-between p-1.5 rounded bg-surface border border-surface-border/40">
                          <span>{k}:</span>
                          <span className={v > 0 ? 'text-accent-green font-bold' : 'text-zinc-500'}>
                            {v > 0 ? `${v} MW (ACTIVE)` : 'OFFLINE'}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Priority Curtailments */}
                  <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border space-y-1 text-xs font-mono">
                    <span className="text-blue-400 font-semibold block mb-1">Consumer Load Curtailment Decisions:</span>
                    <div className="grid grid-cols-3 gap-2 text-zinc-300">
                      {Object.entries(gaPlan.best_chromosome.consumer_curtailment).slice(0, 6).map(([k, v]) => (
                        <div key={k} className="flex justify-between p-1.5 rounded bg-surface border border-surface-border/40">
                          <span>{k}:</span>
                          <span className={v > 0 ? 'text-amber-400' : 'text-emerald-400'}>
                            {(v * 100).toFixed(0)}% shed
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Col: Benchmark vs Greedy Baseline & Viva Explanation */}
              <div className="p-5 rounded-xl bg-surface border border-surface-border space-y-4 flex flex-col justify-between">
                <div className="space-y-4">
                  <div className="flex items-center space-x-2 pb-3 border-b border-surface-border">
                    <TrendingDown className="w-4 h-4 text-accent-green" />
                    <span className="text-sm font-semibold text-zinc-100">Baseline Benchmark Comparison</span>
                  </div>

                  <div className="space-y-2 text-xs font-mono">
                    <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border">
                      <div className="text-zinc-500 text-[10px] uppercase">Greedy Heuristic Baseline</div>
                      <div className="text-base font-bold text-zinc-300 mt-1">{gaPlan.baseline_comparison.cost} Cost</div>
                      <div className="text-[11px] text-zinc-400">Unserved: {gaPlan.baseline_comparison.unserved_demand_mw} MW</div>
                      <div className="text-[11px] text-zinc-400">Recovery Time: {gaPlan.baseline_comparison.recovery_time_min} min</div>
                    </div>

                    <div className="p-3 rounded-lg bg-purple-950/20 border border-purple-500/40">
                      <div className="text-purple-400 text-[10px] uppercase font-bold">Genetic Algorithm Optimized</div>
                      <div className="text-base font-bold text-purple-300 mt-1">{gaPlan.best_cost} Cost</div>
                      <div className="text-[11px] text-emerald-400">Unserved: {gaPlan.generations_history.slice(-1)[0]?.unserved_demand_mw ?? 0} MW</div>
                      <div className="text-[11px] text-zinc-400">Fitness: {gaPlan.best_fitness}</div>
                    </div>
                  </div>

                  {/* Viva Technical Explanation */}
                  <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border text-xs space-y-1">
                    <div className="font-semibold text-zinc-200">Viva Presentation Summary:</div>
                    <div className="text-zinc-400 text-[11px] leading-relaxed">
                      {gaPlan.explanation}
                    </div>
                  </div>
                </div>

                {/* Apply Button */}
                {!executionResult && (
                  <button
                    onClick={handleExecute}
                    disabled={isExecuting || !gaPlan.is_valid}
                    className="w-full py-2.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white flex items-center justify-center space-x-2 shadow-lg shadow-emerald-900/30 transition-colors"
                  >
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>Apply Recovery Strategy to Grid</span>
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
