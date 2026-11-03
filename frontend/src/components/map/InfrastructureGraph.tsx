import React, { useMemo, useState } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {
  PowerStationNode,
  SubstationNode,
  BackupGeneratorNode,
  ConsumerNode,
} from './CustomNodes';
import { InfrastructureNetwork } from '../../types';
import { Layers, Activity, AlertCircle, X, ShieldAlert, Cpu } from 'lucide-react';

interface InfrastructureGraphProps {
  network: InfrastructureNetwork;
  highlightedPathEdges?: string[];
  viewMode?: 'normal' | 'failure' | 'heatmap' | 'route';
  onSelectComponent?: (comp: any) => void;
}

const nodeTypes = {
  powerStation: PowerStationNode,
  substation: SubstationNode,
  backupGenerator: BackupGeneratorNode,
  consumer: ConsumerNode,
};

export const InfrastructureGraph: React.FC<InfrastructureGraphProps> = ({
  network,
  highlightedPathEdges = [],
  viewMode = 'normal',
  onSelectComponent,
}) => {
  const [selectedElement, setSelectedElement] = useState<any>(null);

  // 1. Build Nodes
  const nodes: Node[] = useMemo(() => {
    const list: Node[] = [];

    // Power Stations
    network.power_stations.forEach((ps) => {
      list.push({
        id: ps.id,
        type: 'powerStation',
        position: { x: ps.position.x, y: ps.position.y },
        data: { ...ps },
      });
    });

    // Substations
    network.substations.forEach((sub) => {
      list.push({
        id: sub.id,
        type: 'substation',
        position: { x: sub.position.x, y: sub.position.y },
        data: { ...sub },
      });
    });

    // Backup Generators
    network.backup_generators.forEach((bg) => {
      list.push({
        id: bg.id,
        type: 'backupGenerator',
        position: { x: bg.position.x, y: bg.position.y },
        data: { ...bg },
      });
    });

    // Consumers
    network.consumers.forEach((cons) => {
      list.push({
        id: cons.id,
        type: 'consumer',
        position: { x: cons.position.x, y: cons.position.y },
        data: { ...cons },
      });
    });

    return list;
  }, [network]);

  // 2. Build Edges
  const edges: Edge[] = useMemo(() => {
    const list: Edge[] = [];

    // Transmission lines
    network.transmission_lines.forEach((line) => {
      const isRoute = highlightedPathEdges.includes(line.id);
      const isFailed = line.operational_status === 'failed';
      const isOverloaded = line.operational_status === 'overloaded';

      let strokeColor = '#3f3f46';
      let strokeWidth = 2;
      let animated = false;

      if (isRoute) {
        strokeColor = '#06b6d4'; // Cyan
        strokeWidth = 3.5;
        animated = true;
      } else if (isFailed) {
        strokeColor = '#ef4444'; // Red
        strokeWidth = 2;
      } else if (isOverloaded) {
        strokeColor = '#f59e0b'; // Amber
        strokeWidth = 3;
        animated = true;
      } else if (line.current_flow > 0) {
        strokeColor = '#3b82f6'; // Blue for active flow
      }

      list.push({
        id: line.id,
        source: line.source_id,
        target: line.destination_id,
        animated,
        style: {
          stroke: strokeColor,
          strokeWidth,
          strokeDasharray: isFailed ? '5,5' : undefined,
        },
        label: `${line.id}: ${line.current_flow}/${line.max_capacity}MW`,
        labelStyle: {
          fill: isFailed ? '#f87171' : isOverloaded ? '#fbbf24' : '#a1a1aa',
          fontSize: 9,
          fontFamily: 'monospace',
          fontWeight: 500,
        },
        labelBgStyle: {
          fill: '#090a0f',
          fillOpacity: 0.85,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: strokeColor,
          width: 12,
          height: 12,
        },
        data: line as unknown as Record<string, unknown>,
      });
    });

    // Consumer distribution links (from connected substation to consumer)
    network.consumers.forEach((cons) => {
      const isFailed = cons.supplied_power < 0.1;
      list.push({
        id: `link-${cons.connected_substation_id}-${cons.id}`,
        source: cons.connected_substation_id,
        target: cons.id,
        style: {
          stroke: isFailed ? '#ef4444' : '#27272a',
          strokeWidth: 1.2,
          strokeDasharray: '3,3',
        },
      });
    });

    return list;
  }, [network, highlightedPathEdges]);

  const handleNodeClick = (_: any, node: Node) => {
    setSelectedElement(node.data);
    onSelectComponent?.(node.data);
  };

  const handleEdgeClick = (_: any, edge: Edge) => {
    if (edge.data) {
      setSelectedElement(edge.data);
      onSelectComponent?.(edge.data);
    }
  };

  return (
    <div className="relative w-full h-full bg-[#090a0f] overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodeClick={handleNodeClick}
        onEdgeClick={handleEdgeClick}
        fitView
        fitViewOptions={{ padding: 0.15 }}
        minZoom={0.3}
        maxZoom={2.0}
      >
        <Background color="#1e2230" gap={20} size={1} />
        <Controls className="!bg-surface !border-surface-border !text-zinc-200" />
        <MiniMap
          nodeColor={(n) => {
            if (n.type === 'powerStation') return '#3b82f6';
            if (n.type === 'substation') return '#10b981';
            if (n.type === 'backupGenerator') return '#8b5cf6';
            return '#71717a';
          }}
          className="!bg-surface !border-surface-border"
        />
      </ReactFlow>

      {/* Floating Legend */}
      <div className="absolute top-4 left-4 p-3 rounded-lg bg-surface/90 backdrop-blur-md border border-surface-border shadow-xl text-xs space-y-2 select-none z-10">
        <div className="flex items-center space-x-2 text-[11px] font-semibold text-zinc-300 pb-1 border-b border-surface-border">
          <Layers className="w-3.5 h-3.5 text-blue-400" />
          <span>Grid Infrastructure Topology</span>
        </div>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-[10px] text-zinc-400">
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
            <span>Power Station</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
            <span>Substation</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500" />
            <span>Backup Generator</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-400" />
            <span>Critical Hospital</span>
          </div>
        </div>
      </div>

      {/* Side Inspector Drawer */}
      {selectedElement && (
        <div className="absolute top-4 right-4 w-80 max-h-[85vh] overflow-y-auto p-4 rounded-xl bg-surface/95 backdrop-blur-md border border-surface-border shadow-2xl z-20 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-surface-border">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-blue-400" />
              <span className="text-xs font-semibold text-zinc-100 uppercase tracking-wide">Component Inspector</span>
            </div>
            <button
              onClick={() => setSelectedElement(null)}
              className="p-1 rounded hover:bg-surface-muted text-zinc-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div>
            <div className="text-sm font-bold text-zinc-100">{selectedElement.name || selectedElement.id}</div>
            <div className="text-[10px] font-mono text-zinc-400">ID: {selectedElement.id}</div>
          </div>

          <div className="space-y-1.5 font-mono text-xs">
            {selectedElement.max_capacity !== undefined && (
              <div className="flex justify-between p-2 rounded bg-surface-subtle">
                <span className="text-zinc-400">Max Capacity:</span>
                <span className="text-zinc-200">{selectedElement.max_capacity} MW</span>
              </div>
            )}
            {selectedElement.current_load !== undefined && (
              <div className="flex justify-between p-2 rounded bg-surface-subtle">
                <span className="text-zinc-400">Current Load:</span>
                <span className="text-zinc-200">{selectedElement.current_load} MW</span>
              </div>
            )}
            {selectedElement.generation_capacity !== undefined && (
              <div className="flex justify-between p-2 rounded bg-surface-subtle">
                <span className="text-zinc-400">Gen Capacity:</span>
                <span className="text-zinc-200">{selectedElement.generation_capacity} MW</span>
              </div>
            )}
            {selectedElement.temperature !== undefined && (
              <div className="flex justify-between p-2 rounded bg-surface-subtle">
                <span className="text-zinc-400">Temperature:</span>
                <span className={selectedElement.temperature > 85 ? 'text-red-400' : 'text-zinc-200'}>
                  {selectedElement.temperature}°C
                </span>
              </div>
            )}
            {selectedElement.risk_score !== undefined && (
              <div className="flex justify-between p-2 rounded bg-surface-subtle">
                <span className="text-zinc-400">Fuzzy Risk Score:</span>
                <span className="text-accent-amber font-bold">{selectedElement.risk_score} / 100</span>
              </div>
            )}
            {selectedElement.demand !== undefined && (
              <div className="flex justify-between p-2 rounded bg-surface-subtle">
                <span className="text-zinc-400">Demand:</span>
                <span className="text-zinc-200">{selectedElement.demand} MW</span>
              </div>
            )}
            {selectedElement.supplied_power !== undefined && (
              <div className="flex justify-between p-2 rounded bg-surface-subtle">
                <span className="text-zinc-400">Supplied Power:</span>
                <span className={selectedElement.supplied_power < selectedElement.demand ? 'text-red-400' : 'text-accent-green'}>
                  {selectedElement.supplied_power} MW
                </span>
              </div>
            )}
            <div className="flex justify-between p-2 rounded bg-surface-subtle">
              <span className="text-zinc-400">Operational Status:</span>
              <span className={`uppercase font-semibold ${selectedElement.operational_status === 'failed' ? 'text-red-400' : 'text-accent-green'}`}>
                {selectedElement.operational_status}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
