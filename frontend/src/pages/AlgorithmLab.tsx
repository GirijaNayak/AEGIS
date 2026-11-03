import React, { useState } from 'react';
import {
  FlaskConical,
  ShieldCheck,
  GitBranch,
  Sparkles,
  Play,
  RotateCw,
  Info,
  CheckCircle,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  AreaChart,
  Area,
} from 'recharts';
import { api } from '../services/api';
import { FuzzyEvaluationResult, AStarRouteResult, GARecoveryResult, InfrastructureNetwork } from '../types';

interface AlgorithmLabProps {
  network: InfrastructureNetwork | null;
}

export const AlgorithmLab: React.FC<AlgorithmLabProps> = ({ network }) => {
  const [activeTab, setActiveTab] = useState<'fuzzy' | 'astar' | 'ga'>('fuzzy');

  // --- Fuzzy Logic Lab State ---
  const [fuzzyLoad, setFuzzyLoad] = useState<number>(75);
  const [fuzzyHealth, setFuzzyHealth] = useState<number>(55);
  const [fuzzyTemp, setFuzzyTemp] = useState<number>(78);
  const [fuzzyResult, setFuzzyResult] = useState<FuzzyEvaluationResult | null>(null);
  const [isEvaluatingFuzzy, setIsEvaluatingFuzzy] = useState<boolean>(false);

  // --- A* Search Lab State ---
  const [aStarSource, setAStarSource] = useState<string>('PS1');
  const [aStarDest, setAStarDest] = useState<string>('SUB3');
  const [aStarCapacity, setAStarCapacity] = useState<number>(15);
  const [aStarAvoidLine, setAStarAvoidLine] = useState<string>('');
  const [aStarResult, setAStarResult] = useState<AStarRouteResult | null>(null);
  const [isSearchingAStar, setIsSearchingAStar] = useState<boolean>(false);

  // --- Genetic Algorithm Lab State ---
  const [gaPopSize, setGaPopSize] = useState<number>(30);
  const [gaGenerations, setGaGenerations] = useState<number>(25);
  const [gaMutationRate, setGaMutationRate] = useState<number>(0.15);
  const [gaResult, setGaResult] = useState<GARecoveryResult | null>(null);
  const [isOptimizingGA, setIsOptimizingGA] = useState<boolean>(false);

  // Initial trigger for Fuzzy
  const runFuzzy = async () => {
    setIsEvaluatingFuzzy(true);
    try {
      const res = await api.evaluateFuzzy(fuzzyLoad, fuzzyHealth, fuzzyTemp);
      setFuzzyResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsEvaluatingFuzzy(false);
    }
  };

  const runAStar = async () => {
    setIsSearchingAStar(true);
    try {
      const avoidLines = aStarAvoidLine ? [aStarAvoidLine] : [];
      const res = await api.findAStarRoute(aStarSource, aStarDest, aStarCapacity, [], avoidLines);
      setAStarResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSearchingAStar(false);
    }
  };

  const runGA = async () => {
    setIsOptimizingGA(true);
    try {
      const res = await api.runGAOptimization({
        population_size: gaPopSize,
        generations: gaGenerations,
        mutation_rate: gaMutationRate,
        random_seed: 42,
      });
      setGaResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsOptimizingGA(false);
    }
  };

  // Run initial fuzzy on mount
  React.useEffect(() => {
    runFuzzy();
    runAStar();
  }, []);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto overflow-y-auto h-full">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-surface-border">
        <div>
          <h1 className="text-lg font-bold text-zinc-100 flex items-center space-x-2">
            <FlaskConical className="w-5 h-5 text-accent-blue" />
            <span>AI Algorithm Laboratory & Theoretical Bench</span>
          </h1>
          <p className="text-xs text-zinc-400 mt-1">
            Independently calibrate, experiment with, and visually demonstrate each of the three core AI models.
          </p>
        </div>

        {/* Algorithm Tabs */}
        <div className="flex p-0.5 rounded-lg bg-surface-subtle border border-surface-border text-xs font-medium">
          <button
            onClick={() => setActiveTab('fuzzy')}
            className={`px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition-colors ${
              activeTab === 'fuzzy' ? 'bg-surface text-blue-400 shadow-sm' : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>1. Fuzzy Logic</span>
          </button>
          <button
            onClick={() => setActiveTab('astar')}
            className={`px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition-colors ${
              activeTab === 'astar' ? 'bg-surface text-emerald-400 shadow-sm' : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <GitBranch className="w-3.5 h-3.5" />
            <span>2. A* Search</span>
          </button>
          <button
            onClick={() => setActiveTab('ga')}
            className={`px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition-colors ${
              activeTab === 'ga' ? 'bg-surface text-purple-400 shadow-sm' : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>3. Genetic Algorithm</span>
          </button>
        </div>
      </div>

      {/* ======================================================== */}
      {/* TAB 1: FUZZY LOGIC LAB */}
      {/* ======================================================== */}
      {activeTab === 'fuzzy' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Controls */}
          <div className="p-5 rounded-xl bg-surface border border-surface-border space-y-4">
            <div className="flex items-center space-x-2 pb-3 border-b border-surface-border">
              <ShieldCheck className="w-4 h-4 text-blue-400" />
              <span className="text-sm font-semibold text-zinc-100">Fuzzy Input Sliders</span>
            </div>

            <div className="space-y-4 text-xs">
              {/* Load Slider */}
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-zinc-400">Operating Load:</span>
                  <span className="font-mono text-zinc-200">{fuzzyLoad}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={fuzzyLoad}
                  onChange={(e) => setFuzzyLoad(parseInt(e.target.value))}
                  className="w-full accent-blue-500"
                />
                <div className="flex justify-between text-[10px] text-zinc-500 font-mono mt-0.5">
                  <span>0% (Low)</span>
                  <span>50% (Medium)</span>
                  <span>100% (High)</span>
                </div>
              </div>

              {/* Health Slider */}
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-zinc-400">Component Health:</span>
                  <span className="font-mono text-zinc-200">{fuzzyHealth}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={fuzzyHealth}
                  onChange={(e) => setFuzzyHealth(parseInt(e.target.value))}
                  className="w-full accent-emerald-500"
                />
                <div className="flex justify-between text-[10px] text-zinc-500 font-mono mt-0.5">
                  <span>0% (Poor)</span>
                  <span>60% (Average)</span>
                  <span>100% (Good)</span>
                </div>
              </div>

              {/* Temperature Slider */}
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-zinc-400">Operating Temperature:</span>
                  <span className="font-mono text-zinc-200">{fuzzyTemp}°C</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="120"
                  value={fuzzyTemp}
                  onChange={(e) => setFuzzyTemp(parseInt(e.target.value))}
                  className="w-full accent-red-500"
                />
                <div className="flex justify-between text-[10px] text-zinc-500 font-mono mt-0.5">
                  <span>0°C (Normal)</span>
                  <span>70°C (Elevated)</span>
                  <span>120°C (Critical)</span>
                </div>
              </div>

              <button
                onClick={runFuzzy}
                disabled={isEvaluatingFuzzy}
                className="w-full py-2.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white flex items-center justify-center space-x-1.5 transition-colors disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Evaluate Mamdani Inference</span>
              </button>
            </div>
          </div>

          {/* Results & Defuzzification */}
          <div className="lg:col-span-2 p-5 rounded-xl bg-surface border border-surface-border space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-surface-border">
              <span className="text-sm font-semibold text-zinc-100">Inference & Centroid Defuzzification Outcome</span>
              {fuzzyResult && (
                <span className={`text-xs font-bold font-mono px-2.5 py-0.5 rounded border ${
                  fuzzyResult.risk_category === 'Critical' ? 'bg-red-500/20 text-red-400 border-red-500/40' :
                  fuzzyResult.risk_category === 'High' ? 'bg-amber-500/20 text-amber-400 border-amber-500/40' :
                  'bg-blue-500/20 text-blue-400 border-blue-500/40'
                }`}>
                  Score: {fuzzyResult.defuzzified_risk_score} / 100 ({fuzzyResult.risk_category} Risk)
                </span>
              )}
            </div>

            {fuzzyResult && (
              <div className="space-y-4 text-xs">
                {/* Membership degrees */}
                <div className="grid grid-cols-3 gap-3 font-mono">
                  <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border/50">
                    <span className="text-zinc-500 block text-[10px] mb-1">Load Memberships:</span>
                    <div>Low: <span className="text-zinc-200">{fuzzyResult.load_memberships.low}</span></div>
                    <div>Med: <span className="text-zinc-200">{fuzzyResult.load_memberships.medium}</span></div>
                    <div>High: <span className="text-zinc-200">{fuzzyResult.load_memberships.high}</span></div>
                  </div>

                  <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border/50">
                    <span className="text-zinc-500 block text-[10px] mb-1">Health Memberships:</span>
                    <div>Poor: <span className="text-zinc-200">{fuzzyResult.health_memberships.poor}</span></div>
                    <div>Avg: <span className="text-zinc-200">{fuzzyResult.health_memberships.average}</span></div>
                    <div>Good: <span className="text-zinc-200">{fuzzyResult.health_memberships.good}</span></div>
                  </div>

                  <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border/50">
                    <span className="text-zinc-500 block text-[10px] mb-1">Temp Memberships:</span>
                    <div>Norm: <span className="text-zinc-200">{fuzzyResult.temperature_memberships.normal}</span></div>
                    <div>Elev: <span className="text-zinc-200">{fuzzyResult.temperature_memberships.elevated}</span></div>
                    <div>Crit: <span className="text-zinc-200">{fuzzyResult.temperature_memberships.critical}</span></div>
                  </div>
                </div>

                {/* Activated Rules Table */}
                <div className="space-y-1.5">
                  <div className="text-xs font-semibold text-zinc-300">Activated Fuzzy Rules ({fuzzyResult.activated_rules.length} fired)</div>
                  <div className="max-h-44 overflow-y-auto space-y-1.5 font-mono text-[11px]">
                    {fuzzyResult.activated_rules.map((r) => (
                      <div key={r.rule_id} className="p-2 rounded bg-surface-subtle border border-surface-border flex items-center justify-between">
                        <span className="text-zinc-300">Rule #{r.rule_id}: {r.antecedent} → <strong className="text-accent-blue">{r.consequent}</strong></span>
                        <span className="text-zinc-400">Firing Strength: <strong className="text-white">{r.firing_strength}</strong></span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Defuzzification Explanation */}
                <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border text-zinc-400 text-[11px] leading-relaxed">
                  <strong className="text-zinc-200">Viva Explanation: </strong>
                  {fuzzyResult.explanation}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* TAB 2: A* SEARCH LAB */}
      {/* ======================================================== */}
      {activeTab === 'astar' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Controls */}
          <div className="p-5 rounded-xl bg-surface border border-surface-border space-y-4">
            <div className="flex items-center space-x-2 pb-3 border-b border-surface-border">
              <GitBranch className="w-4 h-4 text-emerald-400" />
              <span className="text-sm font-semibold text-zinc-100">Pathfinding Query</span>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-zinc-400 block mb-1">Source Node</label>
                <select
                  value={aStarSource}
                  onChange={(e) => setAStarSource(e.target.value)}
                  className="w-full p-2.5 rounded-lg bg-surface-subtle border border-surface-border text-zinc-200 font-mono"
                >
                  <option value="PS1">PS1 (Grand Hydroelectric)</option>
                  <option value="PS2">PS2 (East Thermal)</option>
                  <option value="BG1">BG1 (Metro Diesel)</option>
                  <option value="BG2">BG2 (Valley Gas)</option>
                  <option value="SUB1">SUB1 (North Gateway)</option>
                  <option value="SUB2">SUB2 (Central Dist)</option>
                </select>
              </div>

              <div>
                <label className="text-zinc-400 block mb-1">Destination Node</label>
                <select
                  value={aStarDest}
                  onChange={(e) => setAStarDest(e.target.value)}
                  className="w-full p-2.5 rounded-lg bg-surface-subtle border border-surface-border text-zinc-200 font-mono"
                >
                  <option value="SUB3">SUB3 (Metro Core)</option>
                  <option value="SUB4">SUB4 (South Valley)</option>
                  <option value="SUB5">SUB5 (Industrial Park)</option>
                  <option value="SUB6">SUB6 (West Hills)</option>
                  <option value="SUB2">SUB2 (Central Dist)</option>
                </select>
              </div>

              <div>
                <label className="text-zinc-400 block mb-1">Required Flow Capacity (MW)</label>
                <input
                  type="number"
                  min="5"
                  max="150"
                  value={aStarCapacity}
                  onChange={(e) => setAStarCapacity(parseInt(e.target.value) || 10)}
                  className="w-full p-2.5 rounded-lg bg-surface-subtle border border-surface-border text-zinc-200 font-mono"
                />
              </div>

              <div>
                <label className="text-zinc-400 block mb-1">Simulate Severed Line (Avoid Edge)</label>
                <select
                  value={aStarAvoidLine}
                  onChange={(e) => setAStarAvoidLine(e.target.value)}
                  className="w-full p-2.5 rounded-lg bg-surface-subtle border border-surface-border text-zinc-200 font-mono"
                >
                  <option value="">None (All operational)</option>
                  <option value="TL1">TL1 (PS1 → SUB1)</option>
                  <option value="TL6">TL6 (SUB1 → SUB3)</option>
                  <option value="TL7">TL7 (SUB2 → SUB3)</option>
                </select>
              </div>

              <button
                onClick={runAStar}
                disabled={isSearchingAStar}
                className="w-full py-2.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white flex items-center justify-center space-x-1.5 transition-colors"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Execute A* Search</span>
              </button>
            </div>
          </div>

          {/* A* Exploration Results */}
          <div className="lg:col-span-2 p-5 rounded-xl bg-surface border border-surface-border space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-surface-border">
              <span className="text-sm font-semibold text-zinc-100">A* Exploration & Path Reconstruction</span>
              {aStarResult && (
                <span className="text-xs font-mono text-emerald-400 font-semibold">
                  Cost: {aStarResult.total_cost} | Nodes Explored: {aStarResult.nodes_explored_count}
                </span>
              )}
            </div>

            {aStarResult && (
              <div className="space-y-4 text-xs">
                <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border flex items-center justify-between font-mono">
                  <div>
                    <span className="text-zinc-400 block text-[10px]">Optimal Reconstructed Path:</span>
                    <span className="text-emerald-400 font-bold text-sm">
                      {aStarResult.path_found ? aStarResult.path_nodes.join(' → ') : 'NO FEASIBLE PATH'}
                    </span>
                  </div>
                  <div>
                    <span className="text-zinc-400 block text-[10px]">Bottleneck Capacity:</span>
                    <span className="text-zinc-200 font-bold">{aStarResult.bottleneck_capacity_mw} MW</span>
                  </div>
                </div>

                {/* Step by step exploration table */}
                <div className="space-y-1.5">
                  <div className="text-xs font-semibold text-zinc-300">Closed Set Exploration Trace</div>
                  <div className="max-h-52 overflow-y-auto">
                    <table className="w-full text-left text-xs font-mono">
                      <thead>
                        <tr className="border-b border-surface-border text-zinc-500 text-[10px]">
                          <th className="pb-1.5">Step</th>
                          <th className="pb-1.5">Node ID</th>
                          <th className="pb-1.5">g(n)</th>
                          <th className="pb-1.5">h(n)</th>
                          <th className="pb-1.5">f(n) = g + h</th>
                          <th className="pb-1.5">Parent</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-surface-border/40 text-zinc-300">
                        {aStarResult.exploration_steps.map((st) => (
                          <tr key={st.step} className="hover:bg-surface-subtle/50">
                            <td className="py-1.5 text-zinc-500">{st.step}</td>
                            <td className="py-1.5 font-bold text-zinc-200">{st.node_id}</td>
                            <td className="py-1.5">{st.g_cost}</td>
                            <td className="py-1.5">{st.h_cost}</td>
                            <td className="py-1.5 text-emerald-400 font-bold">{st.f_cost}</td>
                            <td className="py-1.5 text-zinc-400">{st.parent_id || 'START'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border text-zinc-400 text-[11px] leading-relaxed">
                  <strong className="text-zinc-200">Viva Explanation: </strong>
                  {aStarResult.explanation}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* TAB 3: GENETIC ALGORITHM LAB */}
      {/* ======================================================== */}
      {activeTab === 'ga' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Controls */}
          <div className="p-5 rounded-xl bg-surface border border-surface-border space-y-4">
            <div className="flex items-center space-x-2 pb-3 border-b border-surface-border">
              <Sparkles className="w-4 h-4 text-purple-400" />
              <span className="text-sm font-semibold text-zinc-100">Evolutionary Hyperparameters</span>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-zinc-400">Population Size:</span>
                  <span className="font-mono text-zinc-200">{gaPopSize}</span>
                </div>
                <input
                  type="range"
                  min="10"
                  max="100"
                  step="5"
                  value={gaPopSize}
                  onChange={(e) => setGaPopSize(parseInt(e.target.value))}
                  className="w-full accent-purple-500"
                />
              </div>

              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-zinc-400">Generations:</span>
                  <span className="font-mono text-zinc-200">{gaGenerations}</span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="80"
                  step="5"
                  value={gaGenerations}
                  onChange={(e) => setGaGenerations(parseInt(e.target.value))}
                  className="w-full accent-purple-500"
                />
              </div>

              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-zinc-400">Mutation Rate:</span>
                  <span className="font-mono text-zinc-200">{gaMutationRate}</span>
                </div>
                <input
                  type="range"
                  min="0.01"
                  max="0.4"
                  step="0.01"
                  value={gaMutationRate}
                  onChange={(e) => setGaMutationRate(parseFloat(e.target.value))}
                  className="w-full accent-purple-500"
                />
              </div>

              <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border space-y-1 text-[11px]">
                <div className="text-zinc-400 font-semibold mb-1">Reproduction Operators:</div>
                <div className="text-zinc-400">• Tournament Selection (k=3)</div>
                <div className="text-zinc-400">• Uniform Crossover (rate=0.8)</div>
                <div className="text-zinc-400">• Gaussian & Bit-Flip Mutation</div>
                <div className="text-zinc-400">• Elitism Preservation (top 2)</div>
              </div>

              <button
                onClick={runGA}
                disabled={isOptimizingGA}
                className="w-full py-2.5 rounded-lg text-xs font-semibold bg-purple-600 hover:bg-purple-500 text-white flex items-center justify-center space-x-1.5 transition-colors disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Run Genetic Algorithm</span>
              </button>
            </div>
          </div>

          {/* GA Convergence Chart & History */}
          <div className="lg:col-span-2 p-5 rounded-xl bg-surface border border-surface-border space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-surface-border">
              <span className="text-sm font-semibold text-zinc-100">Generational Cost Optimization</span>
              {gaResult && (
                <span className="text-xs font-mono text-purple-400 font-semibold">
                  Best Cost: {gaResult.best_cost} | Runtime: {gaResult.execution_time_ms} ms
                </span>
              )}
            </div>

            {gaResult ? (
              <div className="space-y-4">
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={gaResult.generations_history}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#262b3d" />
                      <XAxis dataKey="generation" stroke="#71717a" fontSize={10} />
                      <YAxis stroke="#71717a" fontSize={10} />
                      <Tooltip contentStyle={{ backgroundColor: '#111318', borderColor: '#262b3d', fontSize: '11px', fontFamily: 'monospace' }} />
                      <Line type="monotone" dataKey="best_cost" stroke="#c084fc" strokeWidth={2} name="Best Cost (Minimization)" dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                <div className="p-3 rounded-lg bg-surface-subtle border border-surface-border text-zinc-400 text-[11px] leading-relaxed">
                  <strong className="text-zinc-200">Viva Explanation: </strong>
                  {gaResult.explanation}
                </div>
              </div>
            ) : (
              <div className="py-20 text-center text-xs text-zinc-500">
                Click "Run Genetic Algorithm" to execute stochastic optimization and plot real-time convergence.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
