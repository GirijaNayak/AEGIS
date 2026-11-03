import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import {
  Zap,
  Building2,
  Flame,
  Home,
  GraduationCap,
  HeartPulse,
  Factory,
  Radio,
} from 'lucide-react';
import { OperationalStatus, RiskCategory } from '../../types';

// 1. Power Station Node
export const PowerStationNode = memo(({ data }: { data: any }) => {
  const isFailed = data.operational_status === 'failed';
  return (
    <div className={`px-3 py-2.5 rounded-lg border shadow-lg bg-surface transition-all min-w-[170px] ${
      isFailed ? 'border-accent-red/80 bg-red-950/20' : 'border-blue-500/40 hover:border-blue-500'
    }`}>
      <Handle type="source" position={Position.Bottom} className="!bg-blue-500 !w-2.5 !h-2.5" />
      <div className="flex items-center space-x-2 mb-1.5">
        <div className={`p-1.5 rounded ${isFailed ? 'bg-red-500/20 text-red-400' : 'bg-blue-500/20 text-blue-400'}`}>
          <Zap className="w-4 h-4" />
        </div>
        <div>
          <div className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider">Power Station</div>
          <div className="text-xs font-semibold text-zinc-100 truncate max-w-[120px]">{data.name}</div>
        </div>
      </div>
      <div className="space-y-1 font-mono text-[10px] pt-1 border-t border-surface-border">
        <div className="flex justify-between text-zinc-400">
          <span>Gen Dispatch:</span>
          <span className={isFailed ? 'text-red-400' : 'text-zinc-200'}>{data.current_generation} / {data.generation_capacity} MW</span>
        </div>
        <div className="flex justify-between text-zinc-400">
          <span>Status:</span>
          <span className={`uppercase font-medium ${isFailed ? 'text-red-400' : 'text-accent-green'}`}>{data.operational_status}</span>
        </div>
      </div>
    </div>
  );
});

// 2. Substation Node
export const SubstationNode = memo(({ data }: { data: any }) => {
  const isFailed = data.operational_status === 'failed';
  const isOverloaded = data.operational_status === 'overloaded';
  const risk = data.risk_category?.toLowerCase() as RiskCategory;

  const riskBadgeColor =
    risk === 'critical' ? 'text-red-400 bg-red-500/20 border-red-500/40' :
    risk === 'high' ? 'text-amber-400 bg-amber-500/20 border-amber-500/40' :
    risk === 'moderate' ? 'text-blue-400 bg-blue-500/20 border-blue-500/40' :
    'text-emerald-400 bg-emerald-500/20 border-emerald-500/40';

  const loadPercent = Math.min(100, Math.round((data.current_load / Math.max(1, data.max_capacity)) * 100));

  return (
    <div className={`px-3 py-2.5 rounded-lg border shadow-lg bg-surface transition-all min-w-[180px] ${
      isFailed ? 'border-accent-red bg-red-950/20 ring-1 ring-red-500/40' :
      isOverloaded ? 'border-accent-amber bg-amber-950/20 ring-1 ring-amber-500/40' :
      'border-surface-border hover:border-zinc-400'
    }`}>
      <Handle type="target" position={Position.Top} className="!bg-zinc-400 !w-2 !h-2" />
      <Handle type="source" position={Position.Bottom} className="!bg-zinc-400 !w-2 !h-2" />
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center space-x-1.5">
          <div className={`p-1.5 rounded ${isFailed ? 'bg-red-500/20 text-red-400' : 'bg-surface-muted text-zinc-300'}`}>
            <Radio className="w-3.5 h-3.5" />
          </div>
          <div className="text-xs font-semibold text-zinc-100">{data.id}</div>
        </div>
        <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded border ${riskBadgeColor}`}>
          Risk {data.risk_score?.toFixed(0) ?? 0}
        </span>
      </div>

      <div className="text-[10px] text-zinc-400 truncate mb-1">{data.name}</div>

      {/* Load Bar */}
      <div className="w-full bg-surface-muted h-1.5 rounded-full overflow-hidden mb-1.5">
        <div
          className={`h-full rounded-full ${
            loadPercent > 90 ? 'bg-accent-red' : loadPercent > 70 ? 'bg-accent-amber' : 'bg-accent-green'
          }`}
          style={{ width: `${loadPercent}%` }}
        />
      </div>

      <div className="flex justify-between font-mono text-[9px] text-zinc-400">
        <span>Load: {data.current_load} / {data.max_capacity} MW</span>
        <span>{data.temperature}°C</span>
      </div>
    </div>
  );
});

// 3. Backup Generator Node
export const BackupGeneratorNode = memo(({ data }: { data: any }) => {
  const isActive = data.is_active;
  return (
    <div className={`px-2.5 py-2 rounded-lg border shadow-md bg-surface transition-all min-w-[150px] ${
      isActive ? 'border-accent-purple bg-purple-950/20' : 'border-surface-border text-zinc-400'
    }`}>
      <Handle type="source" position={Position.Top} className="!bg-purple-500 !w-2 !h-2" />
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-1.5">
          <Flame className={`w-3.5 h-3.5 ${isActive ? 'text-accent-purple animate-pulse' : 'text-zinc-500'}`} />
          <span className="text-[11px] font-medium text-zinc-200">{data.id}</span>
        </div>
        <span className={`text-[9px] font-mono px-1 rounded ${isActive ? 'bg-purple-500/20 text-purple-300' : 'bg-surface-muted text-zinc-500'}`}>
          {isActive ? `${data.current_utilization} MW` : 'OFFLINE'}
        </span>
      </div>
      <div className="text-[9px] text-zinc-400 truncate mt-1">Cap: {data.capacity} MW</div>
    </div>
  );
});

// 4. Consumer Node
export const ConsumerNode = memo(({ data }: { data: any }) => {
  const isHospital = data.category === 'hospital' || data.priority === 1;
  const isFailed = data.supplied_power < 0.1;
  const isDegraded = data.supplied_power < data.demand && !isFailed;

  const renderIcon = () => {
    switch (data.category) {
      case 'hospital': return <HeartPulse className="w-3.5 h-3.5 text-red-400" />;
      case 'educational': return <GraduationCap className="w-3.5 h-3.5 text-blue-400" />;
      case 'industrial': return <Factory className="w-3.5 h-3.5 text-amber-400" />;
      default: return <Home className="w-3.5 h-3.5 text-emerald-400" />;
    }
  };

  return (
    <div className={`px-2.5 py-2 rounded-md border shadow-sm bg-surface transition-all min-w-[140px] ${
      isFailed ? 'border-accent-red bg-red-950/30' :
      isDegraded ? 'border-accent-amber bg-amber-950/20' :
      isHospital ? 'border-red-500/40 bg-surface' :
      'border-surface-border'
    }`}>
      <Handle type="target" position={Position.Top} className="!bg-zinc-500 !w-1.5 !h-1.5" />
      <div className="flex items-center space-x-1.5 mb-1">
        {renderIcon()}
        <span className="text-[11px] font-medium text-zinc-200 truncate max-w-[95px]">{data.name}</span>
      </div>
      <div className="flex justify-between font-mono text-[9px]">
        <span className="text-zinc-500">Dem: {data.demand}MW</span>
        <span className={isFailed ? 'text-red-400 font-bold' : isDegraded ? 'text-amber-400' : 'text-accent-green'}>
          {data.supplied_power}MW
        </span>
      </div>
    </div>
  );
});
