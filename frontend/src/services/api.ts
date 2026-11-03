/**
 * REST API client for AEGIS Backend.
 */

import {
  SimulationState,
  SimulationMetrics,
  InfrastructureNetwork,
  EventLogEntry,
  FuzzyEvaluationResult,
  AStarRouteResult,
  GARecoveryResult,
  RecoveryAnalysisResponse,
  ChromosomeDecisions,
} from '../types';

const BASE_URL = '/api';

export const api = {
  // 1. Simulation & Infrastructure
  async getSimulationState(): Promise<SimulationState> {
    const res = await fetch(`${BASE_URL}/simulation/state`);
    if (!res.ok) throw new Error('Failed to fetch simulation state');
    return res.json();
  },

  async resetSimulation(): Promise<{ status: string; state: SimulationState }> {
    const res = await fetch(`${BASE_URL}/simulation/reset`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reset simulation');
    return res.json();
  },

  async loadPreset(scenarioId: string): Promise<SimulationState> {
    const res = await fetch(`${BASE_URL}/simulation/preset/${scenarioId}`, { method: 'POST' });
    if (!res.ok) throw new Error(`Failed to load preset ${scenarioId}`);
    return res.json();
  },

  async getMetrics(): Promise<SimulationMetrics> {
    const res = await fetch(`${BASE_URL}/simulation/metrics`);
    if (!res.ok) throw new Error('Failed to fetch metrics');
    return res.json();
  },

  async getInfrastructure(): Promise<InfrastructureNetwork> {
    const res = await fetch(`${BASE_URL}/infrastructure`);
    if (!res.ok) throw new Error('Failed to fetch infrastructure');
    return res.json();
  },

  // 2. Failures
  async triggerFailure(componentId: string, componentType: string, failureType: string, severity: number = 1.0) {
    const res = await fetch(`${BASE_URL}/failures/trigger`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        component_id: componentId,
        component_type: componentType,
        failure_type: failureType,
        severity,
      }),
    });
    if (!res.ok) throw new Error('Failed to trigger failure');
    return res.json();
  },

  async getFailureHistory(): Promise<EventLogEntry[]> {
    const res = await fetch(`${BASE_URL}/failures/history`);
    if (!res.ok) throw new Error('Failed to fetch event history');
    return res.json();
  },

  // 3. AI Direct Evaluation & Lab
  async evaluateFuzzy(load: number, health: number, temp: number): Promise<FuzzyEvaluationResult> {
    const res = await fetch(`${BASE_URL}/ai/fuzzy/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        load_percentage: load,
        health_percentage: health,
        temperature: temp,
      }),
    });
    if (!res.ok) throw new Error('Failed to evaluate fuzzy risk');
    return res.json();
  },

  async getFuzzyRules() {
    const res = await fetch(`${BASE_URL}/ai/fuzzy/rules`);
    if (!res.ok) throw new Error('Failed to fetch fuzzy rules');
    return res.json();
  },

  async findAStarRoute(sourceId: string, destinationId: string, capacity: number = 10.0, avoidNodes: string[] = [], avoidEdges: string[] = []): Promise<AStarRouteResult> {
    const res = await fetch(`${BASE_URL}/ai/astar/find-route`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_id: sourceId,
        destination_id: destinationId,
        required_capacity: capacity,
        avoid_node_ids: avoidNodes,
        avoid_edge_ids: avoidEdges,
      }),
    });
    if (!res.ok) throw new Error('Failed to find A* route');
    return res.json();
  },

  async runGAOptimization(config?: any): Promise<GARecoveryResult> {
    const res = await fetch(`${BASE_URL}/ai/genetic/optimize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config || {}),
    });
    if (!res.ok) throw new Error('Failed to run GA optimization');
    return res.json();
  },

  // 4. Recovery Pipeline
  async analyzeRecovery(): Promise<RecoveryAnalysisResponse> {
    const res = await fetch(`${BASE_URL}/recovery/analyze`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to analyze recovery pipeline');
    return res.json();
  },

  async executeRecovery(plan: ChromosomeDecisions) {
    const res = await fetch(`${BASE_URL}/recovery/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recovery_plan: plan }),
    });
    if (!res.ok) throw new Error('Failed to execute recovery');
    return res.json();
  },

  // 5. Experiments & Reports
  async runExperiment(scenarioId: string, config?: any) {
    const res = await fetch(`${BASE_URL}/experiments/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario_id: scenarioId, ga_config: config }),
    });
    if (!res.ok) throw new Error('Failed to run experiment');
    return res.json();
  },

  async listExperiments() {
    const res = await fetch(`${BASE_URL}/experiments`);
    if (!res.ok) throw new Error('Failed to fetch experiments');
    return res.json();
  },

  async getReportJson() {
    const res = await fetch(`${BASE_URL}/reports/current/json`);
    if (!res.ok) throw new Error('Failed to fetch JSON report');
    return res.json();
  },
};
