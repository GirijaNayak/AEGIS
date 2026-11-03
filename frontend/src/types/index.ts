export type ComponentType =
  | 'power_station'
  | 'substation'
  | 'transmission_line'
  | 'consumer'
  | 'backup_generator';

export type OperationalStatus = 'operational' | 'degraded' | 'overloaded' | 'failed' | 'offline';

export type ConsumerCategory = 'hospital' | 'educational' | 'residential' | 'industrial' | 'commercial';

export type CriticalityLevel = 'critical' | 'high' | 'medium' | 'low';

export type RiskCategory = 'low' | 'moderate' | 'high' | 'critical';

export interface Position {
  x: number;
  y: number;
}

export interface PowerStation {
  id: string;
  name: string;
  generation_capacity: number;
  current_generation: number;
  operational_status: OperationalStatus;
  health_percentage: number;
  position: Position;
}

export interface Substation {
  id: string;
  name: string;
  max_capacity: number;
  current_load: number;
  health_percentage: number;
  temperature: number;
  operational_status: OperationalStatus;
  risk_score: number;
  risk_category: RiskCategory;
  position: Position;
}

export interface TransmissionLine {
  id: string;
  source_id: string;
  destination_id: string;
  max_capacity: number;
  current_flow: number;
  transfer_cost: number;
  operational_status: OperationalStatus;
  is_backup_feeder: boolean;
}

export interface Consumer {
  id: string;
  name: string;
  category: ConsumerCategory;
  demand: number;
  nominal_demand?: number;
  supplied_power: number;
  criticality: CriticalityLevel;
  priority: number;
  connected_substation_id: string;
  backup_substation_id?: string;
  operational_status: OperationalStatus;
  position: Position;
}

export interface BackupGenerator {
  id: string;
  name: string;
  capacity: number;
  current_utilization: number;
  location_substation_id: string;
  operational_status: OperationalStatus;
  is_active: boolean;
  fuel_cost_per_mw: number;
  position: Position;
}

export interface InfrastructureNetwork {
  power_stations: PowerStation[];
  substations: Substation[];
  transmission_lines: TransmissionLine[];
  consumers: Consumer[];
  backup_generators: BackupGenerator[];
  name?: string;
  description?: string;
}

export interface SimulationMetrics {
  total_demand: number;
  total_generation_capacity: number;
  current_generation: number;
  total_supplied_power: number;
  unserved_demand: number;
  restoration_percentage: number;
  critical_facilities_total: number;
  critical_facilities_supplied: number;
  critical_facilities_unserved: number;
  critical_unserved_demand: number;
  operational_components_count: number;
  failed_components_count: number;
  overloaded_lines_count: number;
  grid_reliability_index: number;
  system_health_average: number;
}

export interface CascadingEventStep {
  step_number: number;
  component_id: string;
  component_name: string;
  component_type: string;
  event_reason: string;
  flow_before: number;
  capacity: number;
  overload_percentage: number;
  new_status: string;
}

export interface EventLogEntry {
  id: string;
  timestamp: string;
  component_id: string;
  component_name: string;
  event_type: string;
  severity: number;
  directly_affected_components: string[];
  secondary_effects: string[];
  cascading_steps: CascadingEventStep[];
  description: string;
}

export interface ActivatedFuzzyRule {
  rule_id: number;
  antecedent: string;
  consequent: string;
  firing_strength: number;
}

export interface FuzzyEvaluationResult {
  component_id: string;
  component_name: string;
  inputs: {
    load_percentage: number;
    health_percentage: number;
    temperature: number;
  };
  load_memberships: { low: number; medium: number; high: number };
  health_memberships: { poor: number; average: number; good: number };
  temperature_memberships: { normal: number; elevated: number; critical: number };
  activated_rules: ActivatedFuzzyRule[];
  aggregated_risk_distribution: number[];
  defuzzified_risk_score: number;
  risk_category: string;
  explanation: string;
}

export interface ExploredNodeStep {
  step: number;
  node_id: string;
  node_name: string;
  g_cost: number;
  h_cost: number;
  f_cost: number;
  parent_id?: string;
}

export interface AStarRouteResult {
  source_id: string;
  destination_id: string;
  path_found: boolean;
  path_nodes: string[];
  path_node_names: string[];
  path_edges: string[];
  total_cost: number;
  total_distance_km: number;
  bottleneck_capacity_mw: number;
  nodes_explored_count: number;
  exploration_steps: ExploredNodeStep[];
  admissible_heuristic_used: string;
  explanation: string;
}

export interface GenerationMetric {
  generation: number;
  best_fitness: number;
  average_fitness: number;
  best_cost: number;
  unserved_demand_mw: number;
  critical_unserved_mw: number;
}

export interface BaselineComparison {
  strategy_name: string;
  cost: number;
  fitness: number;
  unserved_demand_mw: number;
  critical_unserved_mw: number;
  generators_used_mw: number;
  recovery_time_min: number;
}

export interface ChromosomeDecisions {
  generator_dispatch: Record<string, number>;
  line_switches: Record<string, boolean>;
  consumer_curtailment: Record<string, number>;
}

export interface GARecoveryResult {
  best_fitness: number;
  best_cost: number;
  best_chromosome: ChromosomeDecisions;
  generations_history: GenerationMetric[];
  execution_time_ms: number;
  is_valid: boolean;
  validation_notes: string[];
  baseline_comparison: BaselineComparison;
  explanation: string;
}

export interface RecoveryAnalysisResponse {
  failed_components: string[];
  isolated_substations: string[];
  affected_consumers: string[];
  unserved_demand_mw: number;
  critical_unserved_mw: number;
  fuzzy_risk_assessments: FuzzyEvaluationResult[];
  alternative_astar_routes: AStarRouteResult[];
  recommended_ga_plan?: GARecoveryResult;
  summary: string;
}

export interface RecoveryExecutionResponse {
  success: boolean;
  plan_applied: ChromosomeDecisions;
  before_metrics: Record<string, any>;
  after_metrics: Record<string, any>;
  improvements: {
    unserved_demand_recovered_mw: number;
    critical_demand_recovered_mw: number;
    reliability_index_gain: number;
    facilities_restored: number;
  };
  status_message: string;
}

export interface SimulationState {
  network: InfrastructureNetwork;
  metrics: SimulationMetrics;
  active_scenario: string;
  events_count: number;
}
