import React from 'react';
import {
  LayoutDashboard,
  Network,
  AlertTriangle,
  Cpu,
  FlaskConical,
  BarChart3,
  FileText,
  Activity,
} from 'lucide-react';

export type PageId =
  | 'overview'
  | 'map'
  | 'simulator'
  | 'recovery'
  | 'lab'
  | 'experiments'
  | 'reports';

interface SidebarProps {
  currentPage: PageId;
  onSelectPage: (page: PageId) => void;
  unservedDemand: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  onSelectPage,
  unservedDemand,
}) => {
  const navItems: { id: PageId; label: string; icon: React.ReactNode; badge?: string }[] = [
    { id: 'overview', label: 'Overview', icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: 'map', label: 'Infrastructure Map', icon: <Network className="w-4 h-4" /> },
    {
      id: 'simulator',
      label: 'Failure Simulator',
      icon: <AlertTriangle className="w-4 h-4" />,
      badge: unservedDemand > 0.1 ? `${unservedDemand.toFixed(0)} MW` : undefined,
    },
    { id: 'recovery', label: 'AI Recovery Pipeline', icon: <Cpu className="w-4 h-4" /> },
    { id: 'lab', label: 'Algorithm Laboratory', icon: <FlaskConical className="w-4 h-4" /> },
    { id: 'experiments', label: 'Experiments & Benchmark', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'reports', label: 'Technical Reports', icon: <FileText className="w-4 h-4" /> },
  ];

  return (
    <aside className="w-64 border-r border-surface-border bg-surface flex flex-col justify-between shrink-0 select-none">
      {/* Top Nav items */}
      <div className="p-3 space-y-1">
        <div className="px-3 py-2 text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">
          Simulation Platform
        </div>
        {navItems.map((item) => {
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectPage(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                  : 'text-zinc-400 hover:text-zinc-100 hover:bg-surface-subtle'
              }`}
            >
              <div className="flex items-center space-x-2.5">
                <span className={isActive ? 'text-blue-400' : 'text-zinc-500'}>{item.icon}</span>
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-red-500/15 text-red-400 border border-red-500/30">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Bottom: Core AI Algorithms status */}
      <div className="p-3 border-t border-surface-border space-y-2.5 bg-surface-subtle/40">
        <div className="flex items-center justify-between px-1 text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">
          <span>Active AI Engine</span>
          <Activity className="w-3 h-3 text-accent-green" />
        </div>
        <div className="space-y-1.5 font-mono text-[11px]">
          <div className="flex items-center justify-between px-2 py-1 rounded bg-surface border border-surface-border/60 text-zinc-300">
            <span className="text-zinc-400">1. Fuzzy Logic</span>
            <span className="text-accent-blue text-[10px]">Mamdani</span>
          </div>
          <div className="flex items-center justify-between px-2 py-1 rounded bg-surface border border-surface-border/60 text-zinc-300">
            <span className="text-zinc-400">2. A* Search</span>
            <span className="text-accent-green text-[10px]">Admissible</span>
          </div>
          <div className="flex items-center justify-between px-2 py-1 rounded bg-surface border border-surface-border/60 text-zinc-300">
            <span className="text-zinc-400">3. Genetic Algo</span>
            <span className="text-accent-purple text-[10px]">Multi-Obj</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
